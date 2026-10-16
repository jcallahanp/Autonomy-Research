"""Production deploys: deny a Bash command matching any regex of templates/deploy-deny.txt.

Promotes go through the morning digest (ruling 9), never through the engineer's shell.
"""
import re

from guards import command, segments


def _patterns(ctx) -> list:
    path = ctx.root / "templates" / "deploy-deny.txt"
    lines = (raw.strip() for raw in path.read_text().splitlines())
    return [re.compile(line) for line in lines if line and not line.startswith("#")]


def check(event: dict, ctx):
    cmd = command(event)
    if not cmd:
        return None
    texts = [cmd] + [" ".join(seg) for seg in segments(cmd)]
    for pattern in _patterns(ctx):
        if any(pattern.search(t) for t in texts):
            return f"production deploy is not allowed (deploy-deny.txt: {pattern.pattern}); promote via the digest"
    return None
