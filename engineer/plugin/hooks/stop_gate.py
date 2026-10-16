#!/usr/bin/env python3
"""Stop and TaskCompleted: hold the session open until the task's check and DEPENDENTS rule pass.

Exit 0 when ENGINEER_TASK_ID is unset. Otherwise run the task's `check` from docs/plan/tasks.json
with `bash -c` in the project (timeout: run-defaults profile `check`); then every changed file
matching a `| <glob> | <doc> |` row of docs/DEPENDENTS.md needs its doc changed too. A failure
exits 2 with the reason on stderr (contract: https://code.claude.com/docs/en/hooks; Stop: Claude
continues; TaskCompleted: the task stays open). At the 8th block of a session the gate gives up:
exit 0 and a `gate_gave_up` spool line, so the audit fails the task instead of looping forever.
"""
import json
import os
import pwd
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

MAX_BLOCKS = 8
TAIL_LINES = 30
FORBIDDEN_USERS = ("supervisor", "secretbroker", "egress")


def check_timeout(root: Path) -> int:
    import yaml
    data = yaml.safe_load((root / "templates" / "run-defaults.yaml").read_text())
    return int(data["profiles"]["check"]["timeout_minutes"]) * 60


def run_check(ctx, task_id: str):
    tasks = json.loads((ctx.project_dir / "docs/plan/tasks.json").read_text()).get("tasks", [])
    task = next((t for t in tasks if t.get("id") == task_id), None)
    if task is None or not task.get("check"):
        return f"task {task_id} has no check in docs/plan/tasks.json"
    secs = check_timeout(ctx.root)
    try:
        r = subprocess.run(["bash", "-c", task["check"]], cwd=ctx.project_dir, text=True,
                           stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, timeout=secs, errors="replace")
    except subprocess.TimeoutExpired:
        return f"check for {task_id} timed out after {secs // 60} min: {task['check']}"
    if r.returncode != 0:
        tail = "\n".join(r.stdout.splitlines()[-TAIL_LINES:])
        return f"check for {task_id} failed (exit {r.returncode}): {task['check']}\n{tail}"
    return None


def _git(ctx, *args) -> list:
    r = subprocess.run(["git", "-C", str(ctx.project_dir), *args], capture_output=True, text=True)
    return [x for x in r.stdout.splitlines() if x.strip()] if r.returncode == 0 else []


def default_branch(ctx) -> str:
    try:
        for line in (Path(ctx.conf["ETC_DIR"]) / "projects.txt").read_text().splitlines():
            f = line.split()
            if len(f) >= 3 and f[0] == ctx.project:
                return f[2]
    except OSError:
        pass
    return "main"


def changed_files(ctx) -> set:
    base = default_branch(ctx)
    changed = set()
    for ref in (f"origin/{base}", base):
        mb = _git(ctx, "merge-base", ref, "HEAD")
        if mb:
            changed.update(_git(ctx, "diff", "--name-only", f"{mb[0]}...HEAD"))
            break
    changed.update(_git(ctx, "diff", "--name-only", "HEAD"))
    changed.update(_git(ctx, "ls-files", "--others", "--exclude-standard"))
    return changed


def dependents_rows(project_dir: Path) -> list:
    path = project_dir / "docs" / "DEPENDENTS.md"
    rows = []
    if not path.is_file():
        return rows
    for line in path.read_text().splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip().strip("`").strip() for c in s.strip("|").split("|")]
        if len(cells) < 2 or not cells[0] or not cells[1] or set(cells[0]) <= set("-: "):
            continue
        if cells[0].lower() == "source glob":
            continue
        rows.append((cells[0], cells[1]))
    return rows


def check_dependents(ctx):
    from eng import paths
    rows = dependents_rows(ctx.project_dir)
    if not rows:
        return None
    changed = changed_files(ctx)
    for glob, doc in rows:
        for f in sorted(changed):
            if f != doc and paths.match(f, glob) and doc not in changed:
                return f"{f} changed (matches {glob}) but {doc} did not; update it (docs/DEPENDENTS.md)"
    return None


def bump(session_id) -> int:
    import hookctx
    path = Path.home() / ".cache" / "engineer" / f"stop-{hookctx.safe_id(session_id)}"
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        n = int(path.read_text().strip() or 0) + 1
    except (OSError, ValueError):
        n = 1
    path.write_text(f"{n}\n")
    return n


def gate(event: dict, task_id: str):
    import hookctx
    ctx = hookctx.load(event)
    user = pwd.getpwuid(os.geteuid()).pw_name
    if user in FORBIDDEN_USERS or (os.geteuid() == 0 and (ctx.root / "LOCKED").exists()):
        return ctx, f"stop gate refuses to run checks as {user}; checks run as engineer"
    if ctx.project_dir is None:
        return ctx, f"no project: {ctx.cwd} is not inside a git checkout"
    return ctx, run_check(ctx, task_id) or check_dependents(ctx)


def main() -> int:
    task_id = os.environ.get("ENGINEER_TASK_ID")
    if not task_id:
        return 0
    ctx, event = None, {}
    try:
        import hookctx
        event = hookctx.read_event()
        ctx, reason = gate(event, task_id)
    except Exception as e:  # noqa: BLE001 - an unexpected error still blocks (and counts)
        reason = f"stop gate error: {type(e).__name__}"
    if not reason:
        return 0
    n = bump(event.get("session_id"))
    if n >= MAX_BLOCKS:
        detail = {"kind": "gate_gave_up", "blocks": n, "reason": reason[:500]}
        try:
            hookctx.spool(ctx.conf if ctx else hookctx.engconf.load(hookctx.ROOT), event.get("session_id"),
                          hookctx.tap_record(event, ctx, detail))
        except Exception as e:  # noqa: BLE001
            print(f"stop gate: spool write failed ({type(e).__name__})", file=sys.stderr)
        return 0
    print(f"{reason}\n(stop gate block {n} of {MAX_BLOCKS - 1})", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
