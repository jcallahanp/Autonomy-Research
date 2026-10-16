"""Plan hash: an unattended session may write outside docs/plan/ only while John's approval holds.

The approval is STATE_DIR/approvals/<project>.json (written by the supervisor only);
eng.approval.check compares it with the four signed plan files in the project checkout.
"""
import json
from pathlib import Path

from eng import approval
from guards import command
from guards.protected import bash_targets
from hookctx import rel_to, resolve, tool_path

PLAN_DIR = "docs/plan/"


def _writes_outside_plan(event: dict, ctx) -> bool:
    path = tool_path(event)
    if path is not None:
        targets = [resolve(path, ctx.cwd)] if path else []
    else:
        cmd = command(event)
        targets = [real for real, _ in bash_targets(cmd, ctx.cwd)] if cmd else []
    for real in targets:
        rel = rel_to(real, ctx.project_dir)
        if rel is None or not rel.startswith(PLAN_DIR):
            return True
    return False


def load_approval(ctx):
    """The live approval record, or None when there is none."""
    path = Path(ctx.conf["STATE_DIR"]) / "approvals" / f"{ctx.project}.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text())


def check(event: dict, ctx):
    if not ctx.unattended or ctx.project_dir is None or not _writes_outside_plan(event, ctx):
        return None
    errors = approval.check(ctx.project_dir, load_approval(ctx))
    if errors:
        return f"plan approval does not hold: {errors[0]}"
    return None
