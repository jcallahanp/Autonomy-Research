"""Other vendors' AI CLIs: deny a Bash command whose any segment runs one (templates/vendor-cli-deny.txt)."""
import os

from guards import command, effective, segments


def _names(ctx) -> set:
    path = ctx.root / "templates" / "vendor-cli-deny.txt"
    out = set()
    for raw in path.read_text().splitlines():
        line = raw.split("#", 1)[0].strip()
        if line:
            out.add(line.split()[0])
    return out


def check(event: dict, ctx):
    cmd = command(event)
    if not cmd:
        return None
    names = _names(ctx)
    for seg in segments(cmd):
        argv = effective(seg)
        if argv and os.path.basename(argv[0]) in names:
            return f"vendor CLI {os.path.basename(argv[0])!r} is not allowed (templates/vendor-cli-deny.txt)"
    return None
