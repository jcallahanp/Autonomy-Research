"""MORNING.md: the night in one page, rendered from events.jsonl and RUN_STATUS.json, and the end of a night."""
import sys
from collections import Counter

from approvals import telegram
from supervisor import events as _events
from supervisor import nightwin, run_status


def _outcomes(events: list) -> dict:
    """Last outcome per task: {task_id: detail of its last `audit` event with a status, or of its `merge`
    event with detail.merged (its `note`, e.g. a merge John made himself, is shown under Done)}."""
    last = {}
    for e in events:
        detail = e.get("detail") or {}
        if e.get("task_id") and ((e["event"] == "audit" and detail.get("status"))
                                 or (e["event"] == "merge" and detail.get("merged") is True)):
            last[e["task_id"]] = {"note": detail.get("note")} if e["event"] == "merge" else detail
    return last


def _pr_line(e: dict) -> str | None:
    """One Pull requests line for a pr_open or merge event; None for any other event."""
    d, tid = e.get("detail") or {}, e.get("task_id")
    if e["event"] == "pr_open":
        return f"- {tid}: {d.get('url', d.get('number'))}"
    if e["event"] != "merge":
        return None
    if d.get("merged") is True:
        commit = str(d.get("merge_commit") or e.get("head_sha") or "")[:12]
        return f"- {tid}: merged" + (f" at {commit}" if commit else "") + (f" ({d['note']})" if d.get("note") else "")
    return f"- {tid}: auto-merge on" + (f" (tier {d['tier']})" if d.get("tier") is not None else "")


def open_t1(events: list) -> int:
    asked = {}
    answered = set()
    for e in events:
        d = e.get("detail") or {}
        if e["event"] == "approval_ask" and "item" in d:
            asked[d["item"]] = d
        elif e["event"] == "approval_answer" and "item" in d:
            answered.add(d["item"])
    return sum(1 for n, d in asked.items() if d.get("tier") in ("T1", 1) and n not in answered)


def _section(title: str, lines: list) -> list:
    return [f"## {title}", *(lines or ["- none"]), ""]


def render(events: list, run_status: dict) -> str:
    """Markdown: state line, done, blocked with notes, needs-John, PRs, denials, cost total, open T1 count."""
    project = next((e["project"] for e in events), (run_status or {}).get("project") or "project")
    night = next((e["detail"].get("night") for e in events
                  if e["event"] == "night_start" and e.get("detail")), None)
    state = (run_status or {}).get("state", "unknown")
    reason = (run_status or {}).get("reason")
    out = [f"# Morning report: {project}" + (f", night of {night}" if night else ""), "",
           f"State: **{state}**" + (f" - {reason}" if reason else ""), ""]
    outcomes, st = _outcomes(events), _events.state(events)  # a task is done only once its PR merged
    order = list(outcomes)

    def tasks(key, field=None):
        notes = {t: outcomes[t].get(field) if field else None for t in order}
        return [f"- {t}: {notes[t]}" if notes[t] else f"- {t}" for t in order if t in st[key]]

    out += _section("Done", tasks("done", "note"))
    out += _section("In review (PR open, waiting for the merge)", tasks("in_review"))
    out += _section("Blocked", tasks("blocked", "reason"))
    out += _section("Needs John", tasks("needs_john", "reason"))
    out += _section("Pull requests", [x for x in map(_pr_line, events) if x])
    denials = Counter((e.get("detail") or {}).get("kind", "unknown") for e in events if e["event"] == "denial")
    out += _section("Denials", [f"- {k}: {n}" for k, n in sorted(denials.items())])
    cost = sum(e.get("cost_usd") or 0 for e in events if e["event"] == "task_end")
    cost += sum((e.get("detail") or {}).get("auditor_cost_usd") or 0 for e in events if e["event"] == "audit")
    sessions = sum(1 for e in events if e["event"] == "task_end")
    out += [f"Cost: ${cost:.2f} over {sessions} session(s).", f"Open T1 items: {open_t1(events)}", ""]
    return "\n".join(out)


def audit_md(task: dict, script: dict, auditor: dict) -> str:
    """audit/AUDIT-<id>.md for the records branch and the PR body."""
    return "\n".join([f"# AUDIT {task['id']}: {auditor['verdict']}", "", f"Task: {task['title']}",
                      f"HEAD: {script['head_sha']}", "", "## audit.sh", *[f"- {x}" for x in script["lines"]], "",
                      "## Auditor", *[f"- {x}" for x in auditor["lines"]], ""])


def finish_night(c, state, reason):
    """Terminal state: RUN_STATUS.json, MORNING.md (local and on engineer-records), night_end, digest.
    A records failure never stops night_end or the digest (records keeps it for the retry and the ask)."""
    evs = _events.read(c.events)
    idx, _ = _events.current_night(evs)
    night = evs[idx or 0:]
    st = _events.state(night)
    key = ((night[0].get("detail") or {}).get("night") if night and idx is not None
           else nightwin.local_date(c.now, c.tz))
    counts = {k: len(st[k]) for k in ("done", "blocked", "needs_john")}
    counts["sessions"] = sum(1 for e in night if e["event"] == "task_end")
    last = next((e["task_id"] for e in reversed(night) if e.get("task_id")), None)
    status = run_status.write(c.status, state, reason=reason, last_task=last, counts=counts, project=c.name,
                              started=night[0]["ts"] if night else None, ended=_events.now_iso(c.now),
                              updated=_events.now_iso(c.now))
    md = render(night, status)
    (c.dir / "MORNING.md").write_text(md)
    try:
        c.push(f"docs/runs/{key}-MORNING.md", md, f"records: morning report {key}")
    except Exception as e:  # noqa: BLE001 - the night must still end and John must still hear of it
        print(f"supervisor: records push of MORNING.md failed: {type(e).__name__}: {e}", file=sys.stderr)
    c.ev("night_end", detail={"state": state, "reason": reason})
    telegram.send_digest(c, f"{c.name}: night of {key} ended {state}" + (f" ({reason})" if reason else ""))
