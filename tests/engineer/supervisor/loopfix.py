"""Test rig for loop.py: a make_root temp root with stub RUN_TASK, AUDIT_CMD, AGENT_RUN and Task 7 CLIs."""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tests" / "engineer"))
sys.path.insert(0, str(REPO / "engineer" / "scripts"))

import testlib  # noqa: E402
from eng import conf as engconf  # noqa: E402
from supervisor import events  # noqa: E402

SHA = "0123456789abcdef0123456789abcdef01234567"
OTHER = "fedcba9876543210fedcba9876543210fedcba98"
SID = "11111111-2222-3333-4444-555555555555"
NIGHT = "2026-10-16T07:00:00Z"   # 03:00 in New York
DAY = "2026-10-16T11:45:00Z"     # 07:45 in New York, after the 07:30 digest time

RUN_TASK = r'''d=__D__/rt; n=$(cat "$d/$3.n" 2>/dev/null || echo 0); n=$((n+1)); echo "$n" > "$d/$3.n"
f="$d/$3.$n"; [ -f "$f" ] || f="$d/$3"
[ -f "$d/sleep" ] && sleep "$(cat "$d/sleep")"
cat "$f" 2>/dev/null; exit "$(cat "$f.rc" 2>/dev/null || echo 0)"'''
AUDIT = r'''d=__D__/rt; n=$(cat "$d/audit.n" 2>/dev/null || echo 0); n=$((n+1)); echo "$n" > "$d/audit.n"
f="$d/audit.$n"; [ -f "$f" ] || f="$d/audit"
cat "$f"; grep -q '"PASS"' "$f"'''
AGENT_RUN = r'''d=__D__/rt
case "$1" in
  open-pr) cat > "$d/pr-body.txt"; echo '{"number": 7, "url": "https://github.com/o/demo/pull/7"}' ;;
  automerge) cat "$d/automerge"; exit "$(cat "$d/automerge.rc" 2>/dev/null || echo 0)" ;;
  tg-poll) cat "$d/poll" 2>/dev/null || true ;;
  tg-send) cat >> "$d/sent.txt"; printf '\n---\n' >> "$d/sent.txt"; echo '{"sent": 1}' ;;
esac'''
PY_STUB = '''import sys
open(__LOG__, "a").write(__NAME__ + " " + " ".join(sys.argv[1:]) + "\\n")
data = sys.stdin.read() if __NAME__ == "apply-replies.py" else ""
open(__D__ + "/rt/" + __NAME__ + ".stdin", "a").write(data)
print(open(__D__ + "/rt/" + __NAME__ + ".out").read() if __import__("os").path.exists(__D__ + "/rt/" + __NAME__ + ".out") else __DEFAULT__)
'''


def task(tid, deps=()):
    return {"id": tid, "title": f"task {tid}", "type": "feat", "status": "todo", "depends_on": list(deps),
            "requirement_ids": [], "files": [], "check": "true", "passes": False, "attempts": 0}


def result(**kw):
    base = {"exit_code": 0, "is_error": False, "session_id": SID, "cost_usd": 1.0, "head_sha": SHA}
    base.update(kw)
    return base


class Rig:
    def __init__(self, tasks=None):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.root = testlib.make_root(self.tmp)
        self.conf = engconf.load(self.root)
        self.rt = self.tmp / "rt"
        self.rt.mkdir()
        etc = Path(self.conf["ETC_DIR"])
        (etc / "projects.txt").write_text(
            "# name repo branch flags\ndemo o/demo main self_merge=on scratch=yes owner_login=john-test\n")
        self.tasks(tasks if tasks is not None else [task("t1")])
        d = repr(str(self.tmp))
        testlib.stub(self.root, "run-task", RUN_TASK.replace("__D__", d))
        testlib.stub(self.root, "agent-run", AGENT_RUN.replace("__D__", d))
        testlib.stub(self.root, "approve-plan")
        testlib.stub(self.root, "scripts/checks/audit.sh", AUDIT.replace("__D__", d))
        for name, default in (("digest.py", '["1. Merge PR 7? (default: n)"]'), ("apply-replies.py", "")):
            p = self.root / "scripts" / "approvals" / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(PY_STUB.replace("__LOG__", repr(str(self.tmp / "argv.log"))).replace("__D__", d)
                         .replace("__NAME__", repr(name)).replace("__DEFAULT__", repr(default)))
        self.reply("implementer", result())
        self.reply("check", result(output_tail="TESTS_RUN=3", session_id=None, cost_usd=None))
        self.verdict("PASS", SHA)
        self.reply("audit", {"verdict": "PASS", "head_sha": SHA, "lines": ["checks pass"]})
        self.reply("automerge", {"tier": 1, "auto_merge": True})

    def close(self):
        self._tmp.cleanup()

    def tasks(self, tasks, approve=True):
        """The clone's docs/plan/tasks.json; approve=True also makes those bytes the live plan approval's."""
        plan = Path(self.conf["PROJECTS_DIR"]) / "demo" / "docs" / "plan"
        plan.mkdir(parents=True, exist_ok=True)
        data = json.dumps({"version": 1, "tasks": tasks}).encode()
        (plan / "tasks.json").write_bytes(data)
        if approve:
            path = Path(self.conf["STATE_DIR"]) / "approvals" / "demo.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({"scope_version": 1, "files": {
                "docs/plan/tasks.json": hashlib.sha256(data).hexdigest()}}))
        return data

    def reply(self, name, obj, n=None, rc=0):
        f = self.rt / (f"{name}.{n}" if n else name)
        f.write_text(obj if isinstance(obj, str) else json.dumps(obj))
        Path(str(f) + ".rc").write_text(str(rc))

    def verdict(self, verdict, sha, n=None):
        out = json.dumps({"type": "result", "structured_output": {"verdict": verdict, "head_sha": sha,
                                                                  "lines": ["auditor says " + verdict]}})
        self.reply("auditor", result(output_tail=out), n=n)

    def run(self, now=NIGHT, *extra):
        cmd = [sys.executable, str(self.root / "scripts" / "supervisor" / "loop.py"),
               "--once", "--project", "demo", "--now", now, *extra]
        env = dict(os.environ, GIT_CONFIG_NOSYSTEM="1")
        return subprocess.run(cmd, capture_output=True, text=True, timeout=60, env=env)

    def popen(self, now=NIGHT):
        cmd = [sys.executable, str(self.root / "scripts" / "supervisor" / "loop.py"),
               "--once", "--project", "demo", "--now", now]
        return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    @property
    def state_dir(self):
        return Path(self.conf["STATE_DIR"]) / "demo"

    def events(self):
        return events.read(self.state_dir / "events.jsonl")

    def status(self):
        return json.loads((self.state_dir / "RUN_STATUS.json").read_text())

    def argv(self):
        return testlib.argv_log(self.root)

    def records(self, *args):
        clone = Path(self.conf["RECORDS_DIR"]) / "demo"
        return subprocess.run(["git", "-C", str(clone), *args], capture_output=True, text=True).stdout
