"""Protected paths (templates/protected-paths.txt, eng.paths) for file tools and Bash write forms.

File tools: the target, with symlinks resolved, must be inside the project and not protected.
Bash: a write form (`>`, `>>`, tee, sed -i, mv, cp, rm, truncate, chmod, ln, ...) may not target a
protected path, `.git/`, or another project. Heuristic only (SP13); audit and CODEOWNERS are the
real stops.
"""
import os
from pathlib import Path

from eng import paths
from guards import command, effective, redirect_targets, segments
from hookctx import rel_to, resolve, tool_path

WRITE_CMDS = {"tee", "mv", "cp", "rm", "truncate", "chmod", "chown", "chgrp", "ln", "install",
              "rsync", "shred", "unlink", "rmdir", "patch"}
DESTRUCTIVE = {"rm", "mv", "chmod", "chown", "chgrp", "shred", "rmdir", "rsync"}
IN_PLACE = {"sed", "perl", "ruby"}
DEST_ONLY = {"cp", "ln", "install"}  # these write only the destination (last word or -t DIR)


def _rules(ctx) -> dict:
    return paths.load(ctx.root / "templates" / "protected-paths.txt")


def _in_place(args: list) -> bool:
    for a in args:
        if a.startswith("--in-place") or (a.startswith("-") and not a.startswith("--") and "i" in a):
            return True
    return False


def _dest(args: list) -> list:
    for i, a in enumerate(args):
        if a.startswith("--target-directory="):
            return [a.split("=", 1)[1]]
        if (a == "--target-directory" or (a.startswith("-") and not a.startswith("--")
                                           and a.endswith("t"))) and i + 1 < len(args):
            return [args[i + 1]]
    return [a for a in args if not a.startswith("-")][-1:]


def _targets(argv: list) -> list:
    """Paths a write command changes (non-option words; the destination for cp/ln/install)."""
    name = os.path.basename(argv[0])
    if name == "dd":
        return [a[3:] for a in argv[1:] if a.startswith("of=")]
    if name in DEST_ONLY:
        return _dest(argv[1:])
    if name in WRITE_CMDS or (name in IN_PLACE and _in_place(argv[1:])):
        return [a for a in argv[1:] if not a.startswith("-")]
    return []


def bash_targets(cmd: str, cwd: Path) -> list:
    """[(resolved path, destructive)] for every file a Bash command looks like it writes."""
    out, base = [], cwd
    for seg in segments(cmd):
        argv = effective(seg)
        if argv and argv[0] == "cd":
            dest = argv[1] if len(argv) > 1 and argv[1] != "-" else os.path.expanduser("~")
            base = resolve(dest, base)
            continue
        out += [(resolve(t, base), False) for t in redirect_targets(seg) if t]
        if argv:
            destructive = os.path.basename(argv[0]) in DESTRUCTIVE
            out += [(resolve(t, base), destructive) for t in _targets(argv) if t]
    return out


def _rel_reason(rel: str, real: Path, rules: dict, destructive: bool):
    if rel == ".git" or rel.startswith(".git/"):
        return f"{rel}: git internals may not be written"
    hit = paths.protected(rel, rules, real.exists())
    if hit:
        return f"protected path: {rel} matches {hit} (templates/protected-paths.txt)"
    if real.is_dir():
        probe = paths.protected(f"{rel}/x" if rel != "." else "x", rules, False)
        if probe:
            return f"protected path: {rel}/ holds {probe} (templates/protected-paths.txt)"
        if destructive:
            prefix = "" if rel == "." else rel + "/"
            for pattern in rules.get("always", []):
                if pattern.startswith(prefix):
                    return f"protected path: {rel} contains {pattern} (templates/protected-paths.txt)"
    return None


def _file_tool(path: str, ctx, rules):
    if not path:
        return "file tool call without a file path"
    real = resolve(path, ctx.cwd)
    rel = rel_to(real, ctx.project_dir)
    lexical = rel_to(Path(os.path.normpath(os.path.join(ctx.cwd, path))), ctx.project_dir)
    if rel is None:
        return f"outside project: {path} is not inside {ctx.project_dir}"
    return _rel_reason(rel, real, rules, False) or (
        _rel_reason(lexical, real, rules, False) if lexical not in (None, rel) else None)


def check(event: dict, ctx):
    path = tool_path(event)
    cmd = command(event)
    if path is None and not cmd:
        return None
    if path is not None and ctx.project_dir is None:
        return f"no project: {ctx.cwd} is not inside a git checkout"
    rules = _rules(ctx)
    if path is not None:
        return _file_tool(path, ctx, rules)
    projects = Path(os.path.realpath(ctx.conf["PROJECTS_DIR"]))
    for real, destructive in bash_targets(cmd, ctx.cwd):
        rel = rel_to(real, ctx.project_dir) if ctx.project_dir else None
        if rel is None:
            if real == projects or projects in real.parents:
                return f"write into another project: {real}"
            continue
        reason = _rel_reason(rel, real, rules, destructive)
        if reason:
            return reason
    return None
