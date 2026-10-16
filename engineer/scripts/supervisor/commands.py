"""The commands the supervisor runs (all named in engineer.conf, plus the Task 7 CLIs), and their replies."""
import json
import shlex
import subprocess
import sys
from pathlib import Path

from eng import schema
from supervisor import events

ROOT = Path(__file__).resolve().parents[2]
TAIL = 4000


def run(argv, stdin=None) -> subprocess.CompletedProcess:
    try:
        return subprocess.run([str(a) for a in argv], input=stdin, capture_output=True, text=True)
    except OSError as e:
        return subprocess.CompletedProcess(argv, 127, "", f"{type(e).__name__}: {e}")


def _cmd(conf, key, *args, stdin=None):
    return run(shlex.split(conf[key]) + list(args), stdin)


def agent_run(conf, *args, stdin=None):
    return _cmd(conf, "AGENT_RUN", *args, stdin=stdin)


def json_line(text, kind=dict):
    """The last line of text that parses as JSON of this kind, or None."""
    for line in reversed((text or "").splitlines()):
        try:
            value = json.loads(line)
        except ValueError:
            continue
        if isinstance(value, kind):
            return value
    return None


def valid(value, name) -> bool:
    return isinstance(value, dict) and not schema.validate(value, schema.load(ROOT, name))


def run_task(conf, project, task_id, profile, resume=None) -> dict:
    """RUN_TASK P ID PROFILE [--resume S]; its run-result line, or {exit_code, is_error: true} if none."""
    p = _cmd(conf, "RUN_TASK", project, task_id, profile, *(["--resume", resume] if resume else []))
    result = json_line(p.stdout)
    if not valid(result, "run-result"):
        return {"exit_code": p.returncode, "is_error": True, "output_tail": (p.stdout + p.stderr)[-TAIL:]}
    return result


def audit(conf, project, task_id) -> dict:
    """AUDIT_CMD P ID; its verdict JSON, or a FAIL when it gave none (or PASS with a non-zero exit)."""
    p = _cmd(conf, "AUDIT_CMD", project, task_id)  # exit 0 PASS, 1 FAIL; any other exit: could not audit
    v = json_line(p.stdout) if p.returncode in (0, 1) else None
    if not valid(v, "audit-verdict") or (v["verdict"] == "PASS" and p.returncode != 0):
        return {"verdict": "FAIL", "head_sha": None,
                "lines": [f"audit.sh could not audit or gave no valid verdict (exit {p.returncode})"]}
    return v


def auditor_verdict(result) -> dict | None:
    """The auditor's schema-valid verdict: run-result structured_output first, else from output_tail."""
    if valid(result.get("structured_output"), "audit-verdict"):
        return result["structured_output"]
    doc = json_line(result.get("output_tail") or "") or {}
    found = [doc.get("structured_output"), doc]
    if isinstance(doc.get("result"), str):
        found.append(json_line(doc["result"]))
    return next((v for v in found if valid(v, "audit-verdict")), None)


def open_pr(conf, project, branch, title, body) -> dict | None:
    pr = json_line(agent_run(conf, "open-pr", project, branch, title, stdin=body).stdout)
    return pr if pr and isinstance(pr.get("number"), int) else None


def automerge(conf, project, number) -> dict:
    return json_line(agent_run(conf, "automerge", project, number).stdout) or {}


def _approvals(c, script, *extra, stdin=None):
    argv = [sys.executable, c.root / "scripts" / "approvals" / script, "--events", c.events,
            "--records", c.records_file, "--now", events.now_iso(c.now), *extra]
    return run(argv, stdin)


def digest(c) -> tuple:
    """(messages, shown T1 item numbers or None) from digest.py --json-object."""
    doc = json_line(_approvals(c, "digest.py", "--json-object").stdout, (dict, list))
    if isinstance(doc, dict):
        msgs, shown = doc.get("messages"), doc.get("shown")
        shown = [n for n in shown if isinstance(n, int)] if isinstance(shown, list) else None
    else:
        msgs, shown = doc, None
    return [m for m in msgs or [] if isinstance(m, str)], shown


def poll_replies(c, polled: str) -> list:
    """Feed tg-poll lines to apply-replies.py; return its decisions {item, kind, answer, ref}."""
    out = _approvals(c, "apply-replies.py", stdin=polled).stdout
    return [d for d in (json_line(line) for line in out.splitlines()) if d]


def approve_plan(c, item: int):
    return run([c.root / "bin" / "approve-plan", c.name, "--record-id", f"item-{item}", "--item", item,
                "--by", "john", "--source", "telegram"])
