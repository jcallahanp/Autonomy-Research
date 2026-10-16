"""Supervisor steps: one task attempt (implementer session, checks, audit, PR) and its outcome.

The commands themselves are in commands.py, the asks in asks.py; loop.py reaches both through here.
"""
import hashlib
import json
import re
from datetime import timedelta
from pathlib import Path

from supervisor import asks, breaker, events, limits, morning, records
from supervisor.commands import (agent_run, approve_plan, audit, auditor_verdict, automerge, digest,  # noqa: F401
                                 open_pr, poll_replies, run_task)


class Ctx:
    """One project in one iteration: conf, run defaults, its projects.txt row and the clock."""

    def __init__(self, root, conf, defaults, row, now):
        self.root, self.conf, self.defaults, self.row, self.now = Path(root), conf, defaults, row, now
        self.name = row["name"]
        self.tz = defaults.get("night", {}).get("tz") or conf.get("TZ_NAME", "America/New_York")
        self.dir = Path(conf["STATE_DIR"]) / self.name
        self.events = self.dir / "events.jsonl"
        self.status = self.dir / "RUN_STATUS.json"
        self.records_file = Path(conf["RECORDS_DIR"]) / self.name / "decisions" / "approvals.jsonl"

    def ev(self, event, task_id=None, **fields):
        return events.append(self.events, {"ts": events.now_iso(self.now), "project": self.name,
                                           "event": event, "task_id": task_id, **fields})

    def push(self, relpath, content, message):
        return records.write_and_push(self.conf["RECORDS_DIR"], self.name, relpath, content, message,
                                      lambda args: agent_run(self.conf, *args), email=self.conf["BOT_EMAIL"])


def attempt(c, task, resume=None) -> dict:
    """One implementer session and its checks. Returns {"status"}, {"wait": reset_at} or {"night", "reason"}."""
    tid = task["id"]
    resume = resume if resume and re.fullmatch(r"[0-9a-f-]{36}", resume) else None  # run-task's own rule
    detail = {}
    if not resume:  # best effort: without a fresh mirror run-task branches from the clone's default branch
        detail["mirror_synced"] = agent_run(c.conf, "sync-mirror", c.name).returncode == 0
    c.ev("resume" if resume else "task_start", tid, session_id=resume, detail=detail)
    r = run_task(c.conf, c.name, tid, "implementer", resume=resume)
    c.ev("task_end", tid, exit_code=r["exit_code"], cost_usd=r.get("cost_usd"), session_id=r.get("session_id"),
         head_sha=r.get("head_sha"), detail={"subtype": r.get("subtype"), "is_error": r["is_error"]})
    for d in r.get("permission_denials") or []:
        c.ev("denial", tid, detail={"kind": str(d.get("tool_name", "unknown") if isinstance(d, dict) else d)[:60],
                                    "source": "run"})
    asks.from_progress(c, tid)
    ch = asks.challenge(r.get("output_tail"))
    if ch:
        c.ev("challenge", tid, detail=ch)
        asks.relogin(c, tid, ch)
        why = f"browser challenge kind={ch['kind']} host={ch['host']}; John re-logs in on noVNC"
        return outcome(c, task, r, "BLOCKED", [why], status="blocked")
    if not (r["is_error"] or r["exit_code"]):
        return _verify(c, task, r)
    lim = limits.classify(r.get("output_tail"), now=c.now, tz=c.tz)
    if lim["kind"]:
        c.ev("limit", tid, session_id=r.get("session_id"), detail=lim)
    if lim["kind"] == "weekly":
        return {"night": "stopped_by_bound", "reason": "weekly usage limit"}
    if lim["kind"] == "session":
        reset = lim["reset_at"] or events.now_iso(c.now + timedelta(hours=1))
        c.ev("reset_wait", tid, session_id=r.get("session_id"), detail={"reset_at": reset})
        return {"wait": reset}
    sub = f" ({r['subtype']})" if r.get("subtype") else ""
    return outcome(c, task, r, "FAIL", [f"implementer exit {r['exit_code']}{sub}"])


def _verify(c, task, r) -> dict:
    tid = task["id"]
    chk = run_task(c.conf, c.name, tid, "check")
    path = Path(c.conf["STATE_DIR"]) / "checks" / c.name / f"{tid}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(chk, sort_keys=True) + "\n")
    c.ev("check", tid, exit_code=chk["exit_code"], head_sha=chk.get("head_sha"))
    a = audit(c.conf, c.name, tid)
    if a["verdict"] != "PASS":
        return outcome(c, task, r, a["verdict"], a["lines"])
    ar = run_task(c.conf, c.name, tid, "auditor")
    v, cost = auditor_verdict(ar), ar.get("cost_usd")
    if v is None:
        return outcome(c, task, r, "FAIL", ["auditor verdict missing or not valid against the schema"], cost)
    if v["head_sha"] != a["head_sha"]:
        why = f"auditor head_sha {v['head_sha'][:12]} differs from audit.sh head_sha {a['head_sha'][:12]}"
        return outcome(c, task, r, "FAIL", [why], cost)
    if v["verdict"] != "PASS":
        return outcome(c, task, r, v["verdict"], v["lines"], cost)
    md = morning.audit_md(task, a, v)
    c.push(f"audit/AUDIT-{tid}.md", md, f"audit: {tid} PASS at {a['head_sha'][:12]}")
    pr = open_pr(c.conf, c.name, f"task/{tid}", f"{task['type']}: {task['title']}"[:72], md)
    if not pr:
        return outcome(c, task, r, "NEEDS-JOHN", ["open-pr failed; the audited branch is waiting"], cost)
    c.ev("pr_open", tid, head_sha=a["head_sha"], detail=pr)
    m = automerge(c.conf, c.name, pr["number"])
    if m.get("tier") == 1 and m.get("auto_merge"):
        c.ev("merge", tid, detail={"tier": 1, "auto_merge": True, "number": pr["number"], "url": pr.get("url")})
    else:
        why = ", ".join(m.get("reasons") or []) or "auto-merge not enabled"
        asks.ask(c, tid, "merge", f"Merge PR {pr.get('url') or pr['number']}? ({why})", ref=pr.get("url"))
    return outcome(c, task, r, "PASS", v["lines"], cost)


def outcome(c, task, r, verdict, lines, auditor_cost=None, status=None) -> dict:
    """Append the attempt's `audit` outcome event (status done|retry|blocked|needs_john); return it.

    diff: the run left a commit since its base (run-result base_sha) that no earlier attempt had.
    """
    tid, evs = task["id"], events.read(c.events)
    mine = [e for e in evs if e.get("task_id") == tid]
    sig = None if verdict == "PASS" else hashlib.sha256("\n".join(lines).encode()).hexdigest()[:16]
    fails = [(e.get("detail") or {}).get("sig") for e in mine if e["event"] == "audit"]
    fails = [s for s in fails if s]
    heads = [e.get("head_sha") for e in mine if e["event"] == "task_end"][:-1]
    attempts = events.state(evs)["attempts"].get(tid, 0) + 1
    status = status or breaker.task_status(verdict, sig, fails, attempts, c.defaults.get("task", {}).get("attempts", 2))
    head = r.get("head_sha")
    detail = {"verdict": verdict, "status": status, "reason": "; ".join(lines)[:300], "lines": list(lines)[:15],
              "sig": sig, "diff": bool(head) and head != r.get("base_sha") and head not in heads,
              "auditor_cost_usd": auditor_cost}
    c.ev("audit", tid, head_sha=r.get("head_sha"), detail=detail)
    return {"status": status}
