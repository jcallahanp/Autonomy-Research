"""Move hook-tap lines (plugin/hooks/event_tap.py, stop_gate.py) from SPOOL_DIR into events.jsonl.

A tap line is {ts, session_id, hook_event_name, project, task_id, detail} (hookctx.tap_record).
StopFailure becomes a `limit` event, Notification a `denial`, Stop or TaskCompleted with
detail.kind == "gate_gave_up" (stop_gate.py) a `gate`; any other line is dropped and counted. Every
event carries detail.source = "hook". A file holding another project's lines is left alone.

A hook may append while a pass runs, so a file is renamed to a private `<name>.ingesting.<pid>` before
it is read and that name is unlinked after; the hook's next append makes a fresh `<name>`. Leftover
`.ingesting.<pid>` files (from a crashed or interrupted pass, unless the pid is another live process) are
ingested on the next pass.
"""
import json
import os
import re
import stat
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


def _read(path: Path) -> str | None:
    """The text of a regular file, never following a symlink; None if it is not one."""
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except OSError:
        return None
    with os.fdopen(fd, "rb") as f:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            return None
        return f.read().decode(errors="replace")


def _parse(text: str) -> tuple:
    good, bad = [], 0
    for raw in text.splitlines():
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


def _pid_alive(pid: int) -> bool:
    """True when another live process (a concurrent pass) owns the pid; this process's own is fair game."""
    if pid <= 0 or pid == os.getpid():
        return False
    try:
        os.kill(pid, 0)
    except PermissionError:
        return True
    except (ProcessLookupError, OverflowError):
        return False
    return True


def _claims(spool_dir: Path, project: str) -> list:
    """Private files to ingest: leftovers from dead passes, then each fresh file renamed away."""
    out = []
    for path in sorted(spool_dir.glob("*.jsonl.ingesting.*")):
        pid = path.name.rsplit(".", 1)[1]
        if pid.isdigit() and not _pid_alive(int(pid)):
            out.append(path)
    for path in sorted(spool_dir.glob("*.jsonl")):
        text = _read(path)
        if text is None or any(e["project"] != project for e in _parse(text)[0]):
            continue
        private = path.with_name(f"{path.name}.ingesting.{os.getpid()}")
        try:
            os.rename(path, private)
        except OSError:
            continue
        out.append(private)
    return out


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
    for path in _claims(spool_dir, project):
        text = _read(path)
        if text is None:
            continue
        good, bad = _parse(text)
        if any(e["project"] != project for e in good):
            continue  # a hook raced in another project's line: that project's pass takes it as a leftover
        for ev in good:
            try:
                events.append(events_path, ev)
                added += 1
            except ValueError:
                bad += 1
        counts["dropped"] += bad
        path.unlink()
    return added
