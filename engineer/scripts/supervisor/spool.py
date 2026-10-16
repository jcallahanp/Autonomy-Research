"""Move hook-tap lines (plugin/hooks/event_tap.py, stop_gate.py) from SPOOL_DIR into events.jsonl.

A tap line is {ts, session_id, hook_event_name, project, task_id, detail} (hookctx.tap_record).
StopFailure becomes a `limit` event, Notification a `denial`, Stop or TaskCompleted with
detail.kind == "gate_gave_up" (stop_gate.py) a `gate`; any other line is dropped and counted. Every
event carries detail.source = "hook". A file holding another project's lines is left alone.
"""
import json
import re
from pathlib import Path

from supervisor import events

KINDS = {"StopFailure": "limit", "Notification": "denial", "Stop": "gate", "TaskCompleted": "gate"}
_TS = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$")


def _event(line: dict) -> dict | None:
    hook = line.get("hook_event_name")
    if not isinstance(hook, str) or not hook or not isinstance(line.get("project"), str):
        return None
    detail = line.get("detail") if isinstance(line.get("detail"), dict) else {}
    detail = {**detail, "source": "hook", "hook_event_name": hook}
    kind = KINDS.get(hook)
    if kind is None or (kind == "gate" and detail.get("kind") != "gate_gave_up"):
        return None
    if kind == "denial":
        detail.setdefault("kind", detail.get("notification_type") or detail.get("tool_name") or hook)
    ts = line.get("ts")
    event = {"project": line["project"], "event": kind, "detail": detail,
             "task_id": line.get("task_id") if isinstance(line.get("task_id"), str) else None,
             "session_id": line.get("session_id") if isinstance(line.get("session_id"), str) else None}
    if isinstance(ts, str) and _TS.match(ts):
        event["ts"] = ts
    return event


def _parse(path: Path) -> tuple:
    good, bad = [], 0
    for raw in path.read_text(errors="replace").splitlines():
        if not raw.strip():
            continue
        try:
            line = json.loads(raw)
        except ValueError:
            bad += 1
            continue
        ev = _event(line) if isinstance(line, dict) else None
        if ev is None:
            bad += 1
        else:
            good.append(ev)
    return good, bad


def ingest(spool_dir, events_path, project: str, counts: dict | None = None) -> int:
    """Append this project's tap lines as events, delete each ingested file; return the count appended.

    Invalid lines are dropped and counted in counts["dropped"].
    """
    counts = counts if counts is not None else {}
    counts.setdefault("dropped", 0)
    spool_dir = Path(spool_dir)
    if not spool_dir.is_dir():
        return 0
    added = 0
    for path in sorted(spool_dir.glob("*.jsonl")):
        if not path.is_file() or path.is_symlink():
            continue
        good, bad = _parse(path)
        if any(e["project"] != project for e in good):
            continue
        for ev in good:
            try:
                events.append(events_path, ev)
                added += 1
            except ValueError:
                bad += 1
        counts["dropped"] += bad
        path.unlink()
    return added
