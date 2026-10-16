"""events.jsonl: the supervisor's append-only log per project, the source of every night's state.

A crash can leave a torn last line; read() skips it and append() starts a fresh line after it.
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from eng import schema

ROOT = Path(__file__).resolve().parents[2]
_SCHEMA = schema.load(ROOT, "event")
OUTCOMES = {"done": "done", "in_review": "in_review", "blocked": "blocked", "needs_john": "needs_john"}
FAILED = ("retry", "blocked", "needs_john")


def now_iso(now: datetime | None = None) -> str:
    return (now or datetime.now(timezone.utc)).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def append(path, event: dict) -> dict:
    """Add ts if missing, validate, append one line with flush and fsync; return the event."""
    event = {"ts": now_iso(), **event}
    if event["ts"] is None:
        event["ts"] = now_iso()
    errors = schema.validate(event, _SCHEMA)
    if errors:
        raise ValueError("invalid event: " + "; ".join(errors))
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(event, sort_keys=True) + "\n"
    with open(path, "a+b") as f:
        f.seek(0, os.SEEK_END)
        if f.tell():
            f.seek(-1, os.SEEK_END)
            if f.read(1) != b"\n":
                line = "\n" + line
        f.write(line.encode())
        f.flush()
        os.fsync(f.fileno())
    return event


def read(path, counts: dict | None = None) -> list:
    """Every valid event in order; a torn, non-JSON or schema-invalid line is skipped and counted."""
    counts = counts if counts is not None else {}
    counts.setdefault("skipped", 0)
    path = Path(path)
    if not path.exists():
        return []
    out = []
    for raw in path.read_bytes().split(b"\n"):
        if not raw.strip():
            continue
        try:
            event = json.loads(raw)
        except ValueError:
            counts["skipped"] += 1
            continue
        if schema.validate(event, _SCHEMA):
            counts["skipped"] += 1
            continue
        out.append(event)
    return out


def state(events: list) -> dict:
    """Fold events into task sets.

    running: task_start or resume without a later task_end or crash. attempts: failed attempts
    (an outcome `audit` event whose detail.status is retry, blocked or needs_john, or a crash). waiting: tasks
    with a reset_wait not yet followed by a resume. John's `yes` to a task's relogin ask unblocks it.
    in_review: the audited sha is pushed and its PR open; only a `merge` event with detail.merged (the
    broker mirror's default branch has it, merges.py) makes the task done, so dependents wait for the merge.
    """
    st = {"done": set(), "in_review": set(), "blocked": set(), "needs_john": set(), "running": set(),
          "attempts": {}, "waiting": {}}
    for e in events:
        tid, kind, detail = e.get("task_id"), e["event"], e.get("detail") or {}
        if not tid:
            continue
        if kind in ("task_start", "resume"):
            st["running"].add(tid)
            st["waiting"].pop(tid, None)
        elif kind in ("task_end", "crash"):
            st["running"].discard(tid)
        if kind == "crash":
            st["attempts"][tid] = st["attempts"].get(tid, 0) + 1
        elif kind == "reset_wait":
            st["waiting"][tid] = {"session_id": e.get("session_id"), "reset_at": detail.get("reset_at")}
        elif kind == "approval_answer" and detail.get("kind") == "relogin" and detail.get("answer") == "yes":
            st["blocked"].discard(tid)
        elif kind == "merge" and detail.get("merged") is True:
            for key in OUTCOMES.values():
                st[key].discard(tid)
            st["done"].add(tid)
        elif kind == "audit" and detail.get("status"):
            status = detail["status"]
            if status in FAILED:
                st["attempts"][tid] = st["attempts"].get(tid, 0) + 1
            if status in OUTCOMES:
                for key in OUTCOMES.values():
                    st[key].discard(tid)
                st[OUTCOMES[status]].add(tid)
    return st


def reconcile(path, project: str | None = None) -> list:
    """After a restart: append crash then reconcile for each task left running; return their ids."""
    evs = read(path)
    running = sorted(state(evs)["running"], key=lambda t: _last_index(evs, t))
    for tid in running:
        p = project or next(e["project"] for e in evs if e.get("task_id") == tid)
        append(path, {"project": p, "event": "crash", "task_id": tid,
                      "detail": {"reason": "no task_end before the supervisor restarted"}})
        append(path, {"project": p, "event": "reconcile", "task_id": tid,
                      "detail": {"counted_attempt": True}})
    return running


def _last_index(evs, tid) -> int:
    return max(i for i, e in enumerate(evs) if e.get("task_id") == tid)


def current_night(evs: list) -> tuple:
    """(index of the last night_start or None, True when no night_end follows it)."""
    idx = next((i for i in range(len(evs) - 1, -1, -1) if evs[i]["event"] == "night_start"), None)
    if idx is None:
        return None, False
    return idx, not any(e["event"] == "night_end" for e in evs[idx:])
