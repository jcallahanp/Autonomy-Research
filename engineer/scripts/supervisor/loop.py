#!/usr/bin/env python3
"""The supervisor loop (runs as `supervisor` under systemd): one task at a time from each project's DAG.

Per iteration and project: ingest the hook spool, reconcile, ping hc-ping, apply Telegram replies, then
inside the night window run the first ready task; outside it, end an open night and send the digest when due.
Usage: loop.py [--projects FILE] [--project NAME] [--once] [--now ISO]
"""
import argparse
import signal
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import yaml  # noqa: E402

from eng import conf as engconf  # noqa: E402
from supervisor import breaker, dag, events, morning, nightwin, run_status, spool, steps  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SLEEP_SECONDS = 60


class Stopped(Exception):
    """SIGTERM from systemd."""


def _term(signum, frame):
    raise Stopped()


def _when(text: str) -> datetime:
    return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(timezone.utc)


def read_projects(path, only=None) -> list:
    """ETC_DIR/projects.txt rows: name owner/repo default_branch key=value..."""
    rows = []
    for line in Path(path).read_text().splitlines():
        parts = line.split()
        if not parts or parts[0].startswith("#") or len(parts) < 3:
            continue
        row = {"name": parts[0], "repo": parts[1], "branch": parts[2]}
        row.update(p.split("=", 1) for p in parts[3:] if "=" in p)
        if only in (None, row["name"]):
            rows.append(row)
    if only and not rows:
        raise SystemExit(f"project {only!r} is not in {path}")
    return rows


def send_digest(c, header=None):
    for text in ([header] if header else []) + steps.digest(c):
        steps.agent_run(c.conf, "tg-send", stdin=text)
    (c.dir / "last-digest").write_text(nightwin.local_date(c.now, c.tz) + "\n")


def end_night(c, state, reason):
    """Terminal state: RUN_STATUS.json, MORNING.md (local and on engineer-records), night_end, digest."""
    evs = events.read(c.events)
    idx, _ = events.current_night(evs)
    night = evs[idx or 0:]
    st = events.state(night)
    key = ((night[0].get("detail") or {}).get("night") if night and idx is not None
           else nightwin.local_date(c.now, c.tz))
    counts = {k: len(st[k]) for k in ("done", "blocked", "needs_john")}
    counts["sessions"] = sum(1 for e in night if e["event"] == "task_end")
    last = next((e["task_id"] for e in reversed(night) if e.get("task_id")), None)
    status = run_status.write(c.status, state, reason=reason, last_task=last, counts=counts, project=c.name,
                              started=night[0]["ts"] if night else None, ended=events.now_iso(c.now),
                              updated=events.now_iso(c.now))
    md = morning.render(night, status)
    (c.dir / "MORNING.md").write_text(md)
    c.push(f"docs/runs/{key}-MORNING.md", md, f"records: morning report {key}")
    c.ev("night_end", detail={"state": state, "reason": reason})
    send_digest(c, f"{c.name}: night of {key} ended {state}" + (f" ({reason})" if reason else ""))


def apply_replies(c, polled: str):
    if not polled.strip():
        return
    c.records_file.parent.mkdir(parents=True, exist_ok=True)
    for d in steps.poll_replies(c, polled):
        c.ev("approval_answer", detail=d)
        if d.get("kind") == "plan" and d.get("answer") == "y":
            steps.approve_plan(c, str(d.get("ref") or f"item-{d.get('item')}"))
    if c.records_file.exists():
        c.push("decisions/approvals.jsonl", c.records_file.read_text(), "records: approvals")


def _after(c, res: dict):
    if "night" in res:
        end_night(c, res["night"], res["reason"])
    elif "wait" in res:
        run_status.write(c.status, "waiting_for_reset", reason="session usage limit", reset_at=res["wait"],
                         project=c.name, updated=events.now_iso(c.now))


def iterate(c, polled: str):
    spool.ingest(c.conf["SPOOL_DIR"], c.events, c.name)
    events.reconcile(c.events, c.name)
    steps.agent_run(c.conf, "hc-ping")
    apply_replies(c, polled)
    win = c.defaults["night"]
    idx, open_night = events.current_night(events.read(c.events))
    if Path(c.conf["KILL_SWITCH"]).exists():
        if open_night:
            return end_night(c, "stopped_by_bound", "kill switch")
        return run_status.write(c.status, "stopped_by_bound", reason="kill switch", project=c.name,
                                updated=events.now_iso(c.now))
    if not nightwin.in_window(c.now, win["start"], win["end"], c.tz):
        if open_night:
            return end_night(c, "stopped_by_bound", "night window ended")
        last = c.dir / "last-digest"
        if nightwin.digest_due(c.now, last.read_text().strip() if last.exists() else None, win["digest_at"], c.tz):
            send_digest(c)
        return None
    key = nightwin.night_key(c.now, win["start"], c.tz)
    evs = events.read(c.events)
    if idx is None or (evs[idx].get("detail") or {}).get("night") != key:
        if open_night:
            end_night(c, "stopped_by_bound", "night window ended")
        c.ev("night_start", detail={"night": key})
    elif not open_night:
        return None
    try:
        tasks = dag.load(Path(c.conf["PROJECTS_DIR"]) / c.name / "docs" / "plan" / "tasks.json")
        cycle = dag.find_cycle(tasks)
        if cycle:
            raise ValueError("tasks.json has a dependency cycle: " + " -> ".join(cycle))
    except ValueError as e:
        return end_night(c, "blocked", str(e)[:500])
    evs = events.read(c.events)
    reason = breaker.night_bound(c.defaults, evs[events.current_night(evs)[0]:])
    if reason:
        return end_night(c, "stopped_by_bound", reason)
    st, by_id = events.state(evs), {t["id"]: t for t in tasks}
    for tid, wait in st["waiting"].items():
        if tid in by_id:
            if c.now < _when(wait["reset_at"]):
                return _after(c, {"wait": wait["reset_at"]})
            return _after(c, steps.attempt(c, by_id[tid], resume=wait["session_id"]))
    done = st["done"] | {t["id"] for t in tasks if t["status"] == "done"}
    stuck = st["blocked"] | st["needs_john"] | {t["id"] for t in tasks if t["status"] in ("blocked", "needs_john")}
    ready = dag.ready(tasks, done, stuck, st["running"])
    if ready:
        return _after(c, steps.attempt(c, by_id[ready[0]]))
    if all(t["id"] in done for t in tasks):
        return end_night(c, "done", "all tasks done")
    return end_night(c, "blocked", "no task ready; stuck: " + (", ".join(sorted(stuck)) or "none"))


def _final(rows, conf, defaults, current, state, reason):
    targets = [current] if current else [steps.Ctx(ROOT, conf, defaults, r, datetime.now(timezone.utc)) for r in rows]
    for c in targets:
        run_status.write(c.status, state, reason=reason, project=c.name, updated=events.now_iso())


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--projects")
    ap.add_argument("--project")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--now")
    a = ap.parse_args(argv)
    conf = engconf.load(ROOT)
    defaults = yaml.safe_load((ROOT / "templates" / "run-defaults.yaml").read_text())
    rows = read_projects(a.projects or Path(conf["ETC_DIR"]) / "projects.txt", a.project)
    signal.signal(signal.SIGTERM, _term)
    current = None
    try:
        while True:
            now = _when(a.now) if a.now else datetime.now(timezone.utc)
            polled = steps.agent_run(conf, "tg-poll").stdout
            for row in rows:
                current = steps.Ctx(ROOT, conf, defaults, row, now)
                iterate(current, polled)
            current = None
            if a.once:
                return 0
            time.sleep(SLEEP_SECONDS)
    except Stopped:
        _final(rows, conf, defaults, current, "stopped_by_bound", "stopped by systemd")
        return 0
    except Exception as e:  # noqa: BLE001 - every crash must leave a whole RUN_STATUS.json
        traceback.print_exc()
        _final(rows, conf, defaults, current, "crashed", type(e).__name__)
        steps.agent_run(conf, "hc-ping", "fail")
        return 1


if __name__ == "__main__":
    sys.exit(main())
