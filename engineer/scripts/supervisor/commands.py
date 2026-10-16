"""The commands the supervisor runs (all named in engineer.conf), and their replies.

The approvals CLIs (digest.py, apply-replies.py, approve-plan) are run by approvals/telegram.py.
"""
import json
import shlex
import subprocess
from pathlib import Path

from eng import schema

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


def run_task(conf, project, task_id, profile, resume=None, sha=None) -> dict:
    """RUN_TASK P ID PROFILE [--resume S] [--sha SHA]; its run-result line, or {exit_code, is_error: true} if none."""
    extra = (["--resume", resume] if resume else []) + (["--sha", sha] if sha else [])
    p = _cmd(conf, "RUN_TASK", project, task_id, profile, *extra)
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


def push_branch(conf, repo_dir, branch, sha) -> subprocess.CompletedProcess:
    """push-branch REPO_DIR BRANCH --expect SHA: push exactly the audited commit (refused if the head moved)."""
    return agent_run(conf, "push-branch", repo_dir, branch, "--expect", sha)


def automerge(conf, project, number, sha) -> dict:
    """automerge P PR SHA: merges only GitHub's head == SHA (the audited commit); its JSON reply or {}."""
    return json_line(agent_run(conf, "automerge", project, number, sha).stdout) or {}
