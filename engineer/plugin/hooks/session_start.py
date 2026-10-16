#!/usr/bin/env python3
"""SessionStart (startup|resume|compact): give Claude the plan state; always exit 0.

Prints {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "..."}}
(contract: https://code.claude.com/docs/en/hooks, SessionStart) with up to 20 open tasks, the
last `## ` section of PROGRESS.md, the plan approval status and the kill switch status.
"""
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

MAX_TASKS = 20
MAX_PROGRESS_LINES = 40
SUPERPOWERS = ("superpowers:<name> means the local skill <name>; "
               "the plan skill's task contract wins over Superpowers task sizing")


def open_tasks(project_dir: Path) -> list:
    data = json.loads((project_dir / "docs/plan/tasks.json").read_text())
    rows = [t for t in data.get("tasks", []) if t.get("status") != "done"]
    out = [f"- {t.get('id')} [{t.get('status')}] {t.get('title')}" for t in rows[:MAX_TASKS]]
    if len(rows) > MAX_TASKS:
        out.append(f"- ... and {len(rows) - MAX_TASKS} more in docs/plan/tasks.json")
    return out or ["- none"]


def last_progress(project_dir: Path) -> list:
    lines = (project_dir / "PROGRESS.md").read_text().splitlines()
    starts = [i for i, line in enumerate(lines) if line.startswith("## ")]
    if not starts:
        return []
    return lines[starts[-1]:][:MAX_PROGRESS_LINES]


def approval_status(ctx) -> str:
    from eng import approval
    from guards.plan_hash import load_approval
    try:
        record = load_approval(ctx)
    except (OSError, ValueError):
        return "unreadable"
    if record is None:
        return "none"
    errors = approval.check(ctx.project_dir, record)
    return "approved" if not errors else "changed: " + errors[0].split(":", 1)[0]


def build(event: dict) -> list:
    import hookctx
    ctx = hookctx.load(event)
    kill = Path(ctx.conf["KILL_SWITCH"]).exists()
    out = [f"Engineer session context (project: {ctx.project or 'none'}).",
           f"Kill switch: {'on: every tool call is denied' if kill else 'off'}"]
    if ctx.project_dir is None:
        return out
    out.append(f"Plan approval: {approval_status(ctx)}")
    for title, part in (("Open tasks (docs/plan/tasks.json):", open_tasks),
                        ("Last PROGRESS.md section:", last_progress)):
        try:
            body = part(ctx.project_dir)
        except (OSError, ValueError, AttributeError):
            continue
        if body:
            out += [title, *body]
    return out


def main() -> int:
    try:
        lines = build(json.loads(sys.stdin.read() or "{}"))
    except Exception as e:  # noqa: BLE001 - context is best effort; never block a session
        lines = [f"Engineer session context unavailable ({type(e).__name__})."]
    lines.append(SUPERPOWERS)
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart",
                                             "additionalContext": "\n".join(lines)}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
