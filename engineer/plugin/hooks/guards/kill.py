"""Kill switch: while KILL_SWITCH exists, deny every tool call."""
from pathlib import Path


def check(event: dict, ctx):
    if Path(ctx.conf["KILL_SWITCH"]).exists():
        return "kill switch is on: every tool call is denied until John removes it"
    return None
