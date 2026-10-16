"""Git: deny push, history and ref rewrites, remote changes and dangerous config, in any spelling.

Every `git` word in every segment counts (called by path, through env/command/exec/sudo/xargs,
inside `bash -c`, `eval` or `$(...)`), as do `git-<sub>` and git config passed by environment.
Pushes go through the broker's push-branch job, never through the engineer's shell.
"""
import os
import re

from guards import command, effective, segments, words

DENY_SUBS = {"push", "send-pack", "http-push", "filter-branch", "filter-repo", "update-ref",
             "reflog", "remote"}
ARG_OPTS = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--config-env",
            "--super-prefix", "--attr-source"}
DANGER_KEY = re.compile(r"^(core\.(hookspath|fsmonitor|sshcommand)|credential(\..*)?|http\..*"
                        r"|alias\..*|include\.path|includeif\..*)$")
READ_FLAGS = {"--get", "--get-all", "--get-regexp", "--get-urlmatch", "--list", "-l", "get", "list"}
ENV_VAR = re.compile(r"^(GIT_CONFIG\w*|GIT_SSH\w*)(=|$)")


def _danger(key: str) -> bool:
    return bool(DANGER_KEY.match(key.split("=", 1)[0].strip().lower()))


def _flags(args: list):
    letters, longs = set(), set()
    for a in args:
        if a.startswith("--"):
            longs.add(a.split("=", 1)[0])
        elif a.startswith("-") and len(a) > 1:
            letters.update(a[1:])
    return letters, longs


def _sub_reason(sub: str, rest: list):
    if sub in DENY_SUBS:
        return f"git {sub} is not allowed; pushes and ref changes go through the broker"
    letters, longs = _flags(rest)
    if sub == "config":
        if {"-e", "--edit", "edit"} & set(rest):
            return "git config --edit is not allowed"
        if any(_danger(a) for a in rest if not a.startswith("-")) and not READ_FLAGS & set(rest):
            return "git config may not set hooks, fsmonitor, ssh, credential, http, alias or include keys"
    if sub == "branch":
        delete = "d" in letters or "--delete" in longs
        if "D" in letters or (delete and ("f" in letters or "--force" in longs)):
            return "git branch -D (force delete) is not allowed"
    if sub == "tag" and ("d" in letters or "--delete" in longs):
        return "git tag -d is not allowed"
    return None


def parse(args: list):
    """Deny reason for the arguments that follow a `git` word, or None."""
    i = 0
    while i < len(args):
        a = args[i]
        if a in ("-c", "--config-env") and i + 1 < len(args):
            if _danger(args[i + 1]):
                return f"git {a} {args[i + 1].split('=', 1)[0]} is not allowed"
            i += 2
        elif a.startswith("--config-env="):
            if _danger(a.split("=", 1)[1]):
                return "git --config-env with a dangerous key is not allowed"
            i += 1
        elif a in ARG_OPTS:
            i += 2
        elif a.startswith("-"):
            i += 1
        else:
            return _sub_reason(a, args[i + 1:])
    return None


def check(event: dict, ctx):
    cmd = command(event)
    if not cmd:
        return None
    for seg in segments(cmd):
        w = words(seg)
        for tok in w:
            if ENV_VAR.match(tok) or (tok == "export" and any(ENV_VAR.match(x) for x in w)):
                return f"git config or ssh by environment ({tok.split('=', 1)[0]}) is not allowed"
        for i, tok in enumerate(w):
            if tok == "git" or tok.endswith("/git"):
                reason = parse(w[i + 1:])
                if reason:
                    return reason
            elif "/git-core/git-" in tok:
                reason = _sub_reason(tok.rsplit("/git-", 1)[1], w[i + 1:])
                if reason:
                    return reason
        argv = effective(seg)
        if argv and os.path.basename(argv[0]).startswith("git-"):
            reason = _sub_reason(os.path.basename(argv[0])[4:], argv[1:])
            if reason:
                return reason
    return None
