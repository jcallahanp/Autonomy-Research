"""PreToolUse guards and the shell parsing they share.

Each guard module has `check(event: dict, ctx) -> str | None` (a deny reason). pre_tool_use.py runs
ORDER and stops at the first reason. Shell parsing is a heuristic (SP13): it errs towards seeing
more commands, never fewer; the audit script and CODEOWNERS are the real stops.
"""
import os
import re
import shlex

ORDER = ("kill", "protected", "git", "plan_hash", "vendor", "browser", "deploy")

PUNCT = ";&|<>()\n"
SHELLS = {"bash", "sh", "dash", "zsh", "ksh", "ash", "mksh", "fish"}
KEYWORDS = {"{", "}", "!", "if", "then", "else", "elif", "fi", "do", "done", "while", "until",
            "time", "coproc"}
WRAPPERS = {"env", "command", "exec", "nohup", "nice", "timeout", "sudo", "doas", "xargs",
            "stdbuf", "builtin", "setsid", "ionice", "chronic", "unbuffer", "time", "flock"}
ARG_OPTS = {
    "env": {"-u", "-C", "-S", "--unset", "--chdir", "--split-string"},
    "nice": {"-n", "--adjustment"},
    "timeout": {"-s", "-k", "--signal", "--kill-after"},
    "sudo": {"-u", "-g", "-C", "-D", "-h", "-p", "-r", "-t", "-U", "-T", "--user", "--group"},
    "doas": {"-u", "-C"},
    "xargs": {"-I", "-n", "-L", "-P", "-d", "-E", "-s", "-a", "--arg-file", "--delimiter",
              "--max-args", "--max-procs", "--replace"},
    "exec": {"-a"}, "ionice": {"-c", "-n", "-p"}, "stdbuf": {"-i", "-o", "-e"},
}
_ASSIGN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*\+?=")
_HEREDOC = re.compile(r"(?<!<)<<-?\s*(['\"]?)([A-Za-z0-9_.-]+)\1")
_SHELL_WORD = re.compile(r"(^|[\s;&|(/])(" + "|".join(sorted(SHELLS)) + r"|python3?|eval)(\s|$)")
MAX_DEPTH = 6


def command(event: dict):
    """The Bash command string, or None for any other tool."""
    if event.get("tool_name") != "Bash":
        return None
    return str((event.get("tool_input") or {}).get("command") or "")


def is_op(tok: str) -> bool:
    return bool(tok) and all(c in PUNCT for c in tok)


def is_redirect(tok: str) -> bool:
    """`>`, `>>`, `2>&1`-style operators; `>(` and `<(` (process substitution) separate commands."""
    return is_op(tok) and (">" in tok or "<" in tok) and "(" not in tok and ")" not in tok


def strip_heredocs(cmd: str):
    """(command without heredoc bodies, bodies fed to a shell or interpreter)."""
    out, nested, pending = [], [], []
    for line in cmd.split("\n"):
        if pending:
            delim, to_shell, body = pending[0]
            if line.strip() == delim:
                pending.pop(0)
                if to_shell:
                    nested.append("\n".join(body))
            else:
                body.append(line)
            continue
        out.append(line)
        for m in _HEREDOC.finditer(line):
            pending.append((m.group(2), bool(_SHELL_WORD.search(line[:m.start()])), []))
    for _, to_shell, body in pending:  # unterminated: keep it visible
        nested.append("\n".join(body))
    return "\n".join(out), nested


def substitutions(cmd: str) -> list:
    """Bodies of $(...) and `...`, quoting ignored (seeing too many is the safe side)."""
    found = re.findall(r"`([^`]*)`", cmd)
    i = cmd.find("$(")
    while i != -1:
        depth, j = 0, i + 1
        while j < len(cmd):
            depth += {"(": 1, ")": -1}.get(cmd[j], 0)
            if depth == 0:
                break
            j += 1
        found.append(cmd[i + 2:j])
        i = cmd.find("$(", i + 2)
    return found


def tokenize(cmd: str) -> list:
    cmd = cmd.replace("$'", "'").replace('$"', '"')  # ANSI-C and locale quoting read as plain quotes
    try:
        lex = shlex.shlex(cmd, posix=True, punctuation_chars=PUNCT)
        lex.whitespace = " \t\r"
        lex.whitespace_split = True
        return list(lex)
    except ValueError:  # unbalanced quotes: split crudely, keep every word
        return [t.strip("'\"") for t in re.findall(r"[^\s;&|()<>]+|[;&|()<>\n]+", cmd)]


def segments(cmd: str, depth: int = 0) -> list:
    """Token lists of every simple command in cmd, nested ones (bash -c, eval, $(...)) included."""
    if depth > MAX_DEPTH:
        return [["<too deeply nested>"]]
    text, nested = strip_heredocs(cmd)
    segs, cur = [], []
    for tok in tokenize(text):
        if is_op(tok) and not is_redirect(tok):
            if cur:
                segs.append(cur)
            cur = []
        else:
            cur.append(tok)
    if cur:
        segs.append(cur)
    out = []
    for seg in segs:
        out.append(seg)
        for inner in _inner(seg):
            out += segments(inner, depth + 1)
    for inner in nested + substitutions(text):
        out += segments(inner, depth + 1)
    return out


def _inner(seg: list) -> list:
    """Command strings a segment hands to a shell: `sh -c STR`, `bash -lc STR`, `eval ARGS`."""
    found = []
    for i, tok in enumerate(seg):
        if os.path.basename(tok) in SHELLS:
            for j in range(i + 1, len(seg) - 1):
                if re.fullmatch(r"-[A-Za-z]*c[A-Za-z]*", seg[j]):
                    found.append(seg[j + 1])
                    break
    argv = effective(seg)
    if argv and argv[0] == "eval":
        found.append(" ".join(argv[1:]))
    return found


def words(seg: list) -> list:
    """The segment without redirection operators and their targets."""
    out, skip = [], False
    for tok in seg:
        if skip:
            skip = False
        elif is_redirect(tok):
            skip = True
        else:
            out.append(tok)
    return out


def redirect_targets(seg: list) -> list:
    """Files the segment writes by `>`, `>>`, `>|`, `&>` (input redirections excluded)."""
    return [seg[i + 1] for i, tok in enumerate(seg[:-1])
            if is_redirect(tok) and ">" in tok and not tok.endswith("&")]


def effective(seg: list) -> list:
    """argv of the command that really runs: keywords, VAR=value and wrappers removed."""
    w, i = words(seg), 0
    while i < len(w):
        tok, base = w[i], os.path.basename(w[i])
        if tok in KEYWORDS or _ASSIGN.match(tok):
            i += 1
        elif base in WRAPPERS:
            i += 1
            while i < len(w) and w[i].startswith("-") and w[i] != "-":
                i += 2 if w[i] in ARG_OPTS.get(base, ()) else 1
            if base in ("timeout", "flock") and i < len(w):
                i += 1  # the duration or the lock file
        else:
            return w[i:]
    return []
