"""Supervisor steps: the commands it runs (all from engineer.conf, Task 7 CLIs) and one task attempt."""
import hashlib
import json
import re
import shlex
import subprocess
import sys
from datetime import timedelta
from pathlib import Path

from eng import schema
from supervisor import breaker, events, limits, morning, records

ROOT = Path(__file__).resolve().parents[2]
TAIL = 4000

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

def _run(argv, stdin=None) -> subprocess.CompletedProcess:
    try:
        return subprocess.run([str(a) for a in argv], input=stdin, capture_output=True, text=True)
    except OSError as e:
        return subprocess.CompletedProcess(argv, 127, "", f"{type(e).__name__}: {e}")

def _cmd(conf, key, *args, stdin=None):
    return _run(shlex.split(conf[key]) + list(args), stdin)

def agent_run(conf, *args, stdin=None):
    return _cmd(conf, "AGENT_RUN", *args, stdin=stdin)

def _json_line(text, kind=dict):
    for line in reversed((text or "").splitlines()):
        try:
            value = json.loads(line)
        except ValueError:
            continue
        if isinstance(value, kind):
            return value
    return None

def _valid(value, name) -> bool:
    return isinstance(value, dict) and not schema.validate(value, schema.load(ROOT, name))

def run_task(conf, project, task_id, profile, resume=None) -> dict:
    """RUN_TASK P ID PROFILE [--resume S]; its run-result line, or {exit_code, is_error: true} if none."""
    p = _cmd(conf, "RUN_TASK", project, task_id, profile, *(["--resume", resume] if resume else []))
    result = _json_line(p.stdout)
    if not _valid(result, "run-result"):
        return {"exit_code": p.returncode, "is_error": True, "output_tail": (p.stdout + p.stderr)[-TAIL:]}
    return result

def audit(conf, project, task_id) -> dict:
    """AUDIT_CMD P ID; its verdict JSON, or a FAIL when it gave none (or PASS with a non-zero exit)."""
    p = _cmd(conf, "AUDIT_CMD", project, task_id)  # exit 0 PASS, 1 FAIL; any other exit: could not audit
    v = _json_line(p.stdout) if p.returncode in (0, 1) else None
    if not _valid(v, "audit-verdict") or (v["verdict"] == "PASS" and p.returncode != 0):
        return {"verdict": "FAIL", "head_sha": None, "lines": [f"audit.sh could not audit or gave no valid verdict (exit {p.returncode})"]}
    return v

def auditor_verdict(result) -> dict | None:
    """The auditor's verdict from its run-result output_tail (claude JSON output), if schema-valid."""
    tail = result.get("output_tail") or ""
    doc = _json_line(tail) or {}
    found = [doc.get("structured_output"), doc]
    if isinstance(doc.get("result"), str):
        found.append(_json_line(doc["result"]))
    return next((v for v in found if _valid(v, "audit-verdict")), None)

def open_pr(conf, project, branch, title, body) -> dict | None:
    pr = _json_line(agent_run(conf, "open-pr", project, branch, title, stdin=body).stdout)
    return pr if pr and isinstance(pr.get("number"), int) else None

def automerge(conf, project, number) -> dict:
    return _json_line(agent_run(conf, "automerge", project, number).stdout) or {}

def _approvals(c, script, *extra, stdin=None):
    argv = [sys.executable, c.root / "scripts" / "approvals" / script, "--events", c.events,
            "--records", c.records_file, "--now", events.now_iso(c.now), *extra]
    return _run(argv, stdin)

def digest(c) -> list:
    msgs = _json_line(_approvals(c, "digest.py").stdout, list) or []
    return [m for m in msgs if isinstance(m, str)]

def poll_replies(c, polled: str) -> list:
    """Feed tg-poll lines to apply-replies.py; return its decisions {item, kind, answer, ref}."""
    out = _approvals(c, "apply-replies.py", stdin=polled).stdout
    return [d for d in (_json_line(line) for line in out.splitlines()) if d]

def approve_plan(c, record_id):
    return _run([c.root / "bin" / "approve-plan", c.name, "--record-id", record_id, "--by", "john",
                 "--source", "telegram"])

def ask(c, task_id, kind, text, ref=None):
    """Add a T1 approval_ask with the next item number."""
    items = [(e.get("detail") or {}).get("item", 0) for e in events.read(c.events) if e["event"] == "approval_ask"]
    item = max([i for i in items if isinstance(i, int)], default=0) + 1
    c.ev("approval_ask", task_id, detail={"item": item, "tier": 1, "kind": kind, "text": text, "default": "n",
                                          "reversible": True, "ref": ref})

def attempt(c, task, resume=None) -> dict:
    """One implementer session and its checks. Returns {"status"}, {"wait": reset_at} or {"night", "reason"}."""
    tid = task["id"]
    resume = resume if resume and re.fullmatch(r"[0-9a-f-]{36}", resume) else None  # run-task's own rule
    c.ev("resume" if resume else "task_start", tid, session_id=resume)
    r = run_task(c.conf, c.name, tid, "implementer", resume=resume)
    c.ev("task_end", tid, exit_code=r["exit_code"], cost_usd=r.get("cost_usd"), session_id=r.get("session_id"),
         head_sha=r.get("head_sha"), detail={"subtype": r.get("subtype"), "is_error": r["is_error"]})
    for d in r.get("permission_denials") or []:
        c.ev("denial", tid, detail={"kind": str(d.get("tool_name", "unknown") if isinstance(d, dict) else d)[:60],
                                    "source": "run"})
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
        ask(c, tid, "merge", f"Merge PR {pr.get('url') or pr['number']}? ({why})", ref=pr.get("url"))
    return outcome(c, task, r, "PASS", v["lines"], cost)

def outcome(c, task, r, verdict, lines, auditor_cost=None) -> dict:
    """Append the attempt's `audit` outcome event (status done|retry|blocked|needs_john); return it."""
    tid, evs = task["id"], events.read(c.events)
    mine = [e for e in evs if e.get("task_id") == tid]
    sig = None if verdict == "PASS" else hashlib.sha256("\n".join(lines).encode()).hexdigest()[:16]
    fails = [(e.get("detail") or {}).get("sig") for e in mine if e["event"] == "audit"]
    fails = [s for s in fails if s]
    heads = [e.get("head_sha") for e in mine if e["event"] == "task_end"][:-1]
    attempts = events.state(evs)["attempts"].get(tid, 0) + 1
    status = breaker.task_status(verdict, sig, fails, attempts, c.defaults.get("task", {}).get("attempts", 2))
    detail = {"verdict": verdict, "status": status, "reason": "; ".join(lines)[:300], "lines": list(lines)[:15],
              "sig": sig, "diff": bool(r.get("head_sha")) and r.get("head_sha") not in heads,
              "auditor_cost_usd": auditor_cost}
    c.ev("audit", tid, head_sha=r.get("head_sha"), detail=detail)
    return {"status": status}
