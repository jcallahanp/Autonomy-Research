#!/usr/bin/env python3
"""The supervisor loop (runs as `supervisor` under systemd): one task at a time from each project's DAG.

Per iteration: poll Telegram once and apply replies and timeouts for every project at once (item numbers
are global). Then per project: ingest the hook spool, reconcile, ping hc-ping, retry a failed records push,
raise PROGRESS.md asks, run the merge pass, send reminders; inside the night window run the first ready task of
the approved tasks.json (a PR on auto-merge keeps the night open); outside it, end an open night and send the
digest when due. The kill switch stops tasks, never messages.
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
from approvals import telegram  # noqa: E402
from runtask import check as plan  # noqa: E402  (the approved tasks.json, as run-task's check reads it)
from supervisor import asks, breaker, dag, events, merges, morning, nightwin, run_status, spool, steps  # noqa: E402

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


def approved_tasks(c) -> list:
    """Tasks of the approved tasks.json (stored copy, else the clone's file if its sha256 matches); no status."""
    try:
        wt = (Path(c.conf["PROJECTS_DIR"]) / c.name / plan.REL).read_bytes()
    except OSError:
        wt = None
    data = plan.approved_copy(c.conf, c.name, wt, "the clone")
    path = c.dir / "tasks.approved.json"  # c.dir exists: night_start is already in events.jsonl
    path.write_bytes(data)
    return dag.load(path)


def end_night(c, state, reason):
    """Terminal state (morning.finish_night): RUN_STATUS.json, MORNING.md, night_end, digest."""
    morning.finish_night(c, state, reason)


def _after(c, res: dict):
    asks.deadends(c)  # a blocked or needs_john outcome becomes a T1 line before the digest
    if "night" in res:
        end_night(c, res["night"], res["reason"])
    elif "wait" in res:
        run_status.write(c.status, "waiting_for_reset", reason="session usage limit", reset_at=res["wait"],
                         project=c.name, updated=events.now_iso(c.now))


def housekeeping(c):
    """Every pass, STOP or not: spool, reconcile, heartbeat, records retry, asks, merge pass, reminders."""
    spool.ingest(c.conf["SPOOL_DIR"], c.events, c.name)
    events.reconcile(c.events, c.name)
    steps.agent_run(c.conf, "hc-ping")
    asks.records_health(c)
    asks.from_progress(c)  # the clone's asks (a plan approval comes before any task runs)
    merges.pass_open_prs(c.conf, c.name, c.now)
    asks.deadends(c)
    telegram.reminders(c)


def _stop(c, open_night, reason):
    if open_night:
        return end_night(c, "stopped_by_bound", reason)
    return run_status.write(c.status, "stopped_by_bound", reason=reason, project=c.name,
                            updated=events.now_iso(c.now))


def iterate(c):
    housekeeping(c)
    win = c.defaults["night"]
    idx, open_night = events.current_night(events.read(c.events))
    stop = Path(c.conf["KILL_SWITCH"]).exists()
    if not nightwin.in_window(c.now, win["start"], win["end"], c.tz):
        if open_night or stop:
            _stop(c, open_night, "kill switch" if stop else "night window ended")
        last = c.dir / "last-digest"
        if nightwin.digest_due(c.now, last.read_text().strip() if last.exists() else None, win["digest_at"], c.tz):
            telegram.send_digest(c)
        return None
    if stop:
        return _stop(c, open_night, "kill switch")
    key = nightwin.night_key(c.now, win["start"], c.tz)
    evs = events.read(c.events)
    if idx is None or (evs[idx].get("detail") or {}).get("night") != key:
        if open_night:
            end_night(c, "stopped_by_bound", "night window ended")
        c.ev("night_start", detail={"night": key})
    elif not open_night:
        return None
    try:
        tasks = approved_tasks(c)
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
    again = asks.unblocked(evs)
    for tid, wait in st["waiting"].items():
        if tid in by_id:
            if c.now < _when(wait["reset_at"]):
                return _after(c, {"wait": wait["reset_at"]})
            return _after(c, steps.attempt(c, by_id[tid], resume=wait["session_id"]))
    done, stuck = st["done"], (st["blocked"] | st["needs_john"]) - again  # events only, never tasks.json status
    review = st.get("in_review", set()) - done
    ready = dag.ready(tasks, done, stuck | review, st["running"])
    if ready:
        return _after(c, steps.attempt(c, by_id[ready[0]]))
    if all(t["id"] in done for t in tasks):
        return end_night(c, "done", "all tasks done")
    if merges.auto_merging(evs, review):
        return None  # a PR merges by itself: stay open (the merge pass runs each pass) until the window or a bound
    if review and not stuck:
        return end_night(c, "done", "waiting for merge: " + ", ".join(sorted(review)))
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
            poll = steps.agent_run(conf, "tg-poll")
            telegram.apply_all([steps.Ctx(ROOT, conf, defaults, r, now) for r in rows],
                               poll.stdout if poll.returncode == 0 else "")
            for row in rows:
                current = steps.Ctx(ROOT, conf, defaults, row, now)
                iterate(current)
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
