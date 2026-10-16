"""loop.py and Telegram: digests and T2 prompts go out (STOP or not) and are recorded only when sent; replies
apply across projects with global item numbers; timeouts and reminders run every pass; records failures."""
import json
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

from loopfix import AGENT_RUN, DAY, NIGHT, REPO, SHA, Rig, result

sys.path.insert(0, str(REPO / "engineer" / "scripts"))
import testlib  # noqa: E402
from supervisor import asks  # noqa: E402


class LoopTelegram(unittest.TestCase):
    def setUp(self):
        self.rig = Rig()
        self.addCleanup(self.rig.close)
        self.clone = Path(self.rig.conf["PROJECTS_DIR"]) / "demo"

    def run_ok(self, *a):
        p = self.rig.run(*a)
        self.assertEqual(p.returncode, 0, p.stderr)

    def agent_run(self, extra: str):
        testlib.stub(self.rig.root, "agent-run", extra + "\n" + AGENT_RUN.replace("__D__", repr(str(self.rig.tmp))))

    def sent(self):
        p = self.rig.rt / "sent.txt"
        return p.read_text() if p.exists() else ""

    def asks(self):
        return [e["detail"] for e in self.rig.events() if e["event"] == "approval_ask"]

    def progress(self, *lines):
        (self.clone / "PROGRESS.md").write_text("## Asks for John\n" + "".join(f"- {x}\n" for x in lines))

    def test_digest_recorded_only_after_send(self):
        self.agent_run('[ "$1" = tg-send ] && exit 1')
        self.run_ok(DAY)
        self.assertFalse([e for e in self.rig.events() if e["event"] == "digest"])
        self.assertFalse((self.rig.state_dir / "last-digest").exists())
        self.agent_run("")
        self.run_ok(DAY)
        self.assertTrue([e for e in self.rig.events() if e["event"] == "digest"] or
                        (self.rig.state_dir / "last-digest").exists())
        self.assertIn("Merge PR 7?", self.sent())

    def test_stop_still_sends_digest_and_hard_gates(self):
        Path(self.rig.conf["KILL_SWITCH"]).touch()
        self.run_ok(DAY)
        self.assertIn("Merge PR 7?", self.sent())
        self.progress("HARD GATE: money Renew the domain for demo, $12 CONFIRM: SPEND $12")
        self.run_ok(NIGHT)
        self.assertIn("CONFIRM", self.sent())
        self.assertEqual(self.rig.status()["reason"], "kill switch")
        self.assertFalse([a for a in self.rig.argv() if a.startswith("run-task")])

    def test_stopped_run_is_not_a_failure(self):
        self.assertTrue(asks.stopped({"exit_code": 75, "is_error": True}))
        self.assertFalse(asks.stopped({"exit_code": 1, "is_error": True}))

    def test_apply_replies_runs_without_a_message(self):
        self.run_ok(DAY)
        self.assertTrue([a for a in self.rig.argv() if a.startswith("apply-replies.py")])

    def test_reminder_sent_once(self):
        ev = {"ts": "2026-10-15T20:00:00Z", "project": "demo", "event": "approval_ask", "task_id": None,
              "detail": {"item": 1, "tier": "T1", "kind": "other", "text": "Rotate the key", "default": "n",
                         "reversible": True, "ref": None}}
        self.rig.state_dir.mkdir(parents=True, exist_ok=True)
        (self.rig.state_dir / "events.jsonl").write_text(json.dumps(ev) + "\n")
        self.run_ok(DAY)
        self.run_ok(DAY)
        self.assertEqual(self.sent().count('Reminder: 1. demo: Rotate the key (default: n). Reply "1 y"'), 1)

    def test_records_push_failure_raises_t1_and_night_still_ends(self):
        self.agent_run('[ "$1" = push-branch ] && { echo "remote rejected" >&2; exit 1; }')
        self.run_ok()
        self.run_ok()
        evs = [e["event"] for e in self.rig.events()]
        self.assertIn("night_end", evs)
        self.assertTrue([d for d in self.asks() if "engineer-records for demo is not pushed" in d["text"]])
        self.assertIn("night of 2026-10-15 ended", self.sent())

    def test_reply_kept_while_records_clone_cannot_be_made(self):
        for name in ("digest.py", "apply-replies.py"):
            shutil.copy(REPO / "engineer" / "scripts" / "approvals" / name, self.rig.root / "scripts" / "approvals" / name)
        evs = [{"ts": "2026-10-16T11:00:00Z", "project": "demo", "event": "approval_ask", "task_id": None,
                "detail": {"item": 1, "tier": "T1", "kind": "other", "text": "Rotate", "default": "n",
                           "reversible": True, "ref": None}},
               {"ts": "2026-10-16T11:10:00Z", "project": "demo", "event": "digest", "detail": {"items": [1]}}]
        self.rig.state_dir.mkdir(parents=True, exist_ok=True)
        (self.rig.state_dir / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in evs))
        (self.rig.rt / "poll").write_text(json.dumps({"update_id": 1, "from_id": 111111, "date": 1792151000,
                                                      "text": "1 y", "edited": False}) + "\n")
        self.agent_run('[ "$1" = sync-mirror ] && exit 1')
        self.run_ok(DAY)
        pending = self.rig.state_dir / "approvals.pending.jsonl"
        self.assertEqual([json.loads(x)["item"] for x in pending.read_text().splitlines()], ["1"])
        self.assertFalse((Path(self.rig.conf["RECORDS_DIR"]) / "demo").exists())
        (self.rig.rt / "poll").unlink()
        self.agent_run("")
        self.run_ok(DAY)
        self.assertFalse(pending.exists())
        self.assertIn('"item": "1"', self.rig.records("show", "HEAD:decisions/approvals.jsonl"))

    def test_deadend_ask_then_yes_sets_task_ready(self):
        self.rig.reply("implementer", result(exit_code=1, is_error=True), rc=1)
        self.rig.reply("audit", {"verdict": "FAIL", "head_sha": SHA, "lines": ["2 tests fail"]})
        self.run_ok()
        self.run_ok()
        dead = [d for d in self.asks() if d["kind"] == "deadend"]
        self.assertEqual(len(dead), 1)
        self.assertIn("Unblock t1", dead[0]["text"])
        (self.rig.rt / "apply-replies.py.out").write_text(json.dumps(
            {"item": dead[0]["item"], "kind": "deadend", "answer": "yes", "ref": None, "project": "demo"}))
        n = len([a for a in self.rig.argv() if a.startswith("run-task demo t1 implementer")])
        self.run_ok("2026-10-16T08:00:00Z")  # 04:00 in New York: same night
        self.assertEqual(len([a for a in self.rig.argv() if a.startswith("run-task demo t1 implementer")]), n + 1)

    def test_merge_yes_tells_john_to_approve_on_github(self):
        (self.rig.rt / "apply-replies.py.out").write_text(json.dumps(
            {"item": 3, "kind": "merge", "answer": "yes", "ref": "https://github.com/o/demo/pull/7",
             "project": "demo"}))
        self.run_ok(DAY)
        self.assertIn("demo: to merge https://github.com/o/demo/pull/7 (item 3), approve it on GitHub", self.sent())

    def two_projects(self):
        """Real digest.py and apply-replies.py; projects demo and gtm, outside the night."""
        for name in ("digest.py", "apply-replies.py"):
            shutil.copy(REPO / "engineer" / "scripts" / "approvals" / name, self.rig.root / "scripts" / "approvals" / name)
        etc = Path(self.rig.conf["ETC_DIR"]) / "projects.txt"
        etc.write_text(etc.read_text() + "gtm o/gtm main self_merge=on scratch=no owner_login=john-test\n")
        for name, text in (("demo", "Rotate the demo key"), ("gtm", "Rotate the gtm key")):
            d = Path(self.rig.conf["PROJECTS_DIR"]) / name
            d.mkdir(parents=True, exist_ok=True)
            (d / "PROGRESS.md").write_text(f"## Asks for John\n- {text}\n")

    def loop(self, now):
        p = subprocess.run([sys.executable, str(self.rig.root / "scripts" / "supervisor" / "loop.py"), "--once",
                            "--now", now], capture_output=True, text=True, timeout=60,
                           env=dict(os.environ, GIT_CONFIG_NOSYSTEM="1"))
        self.assertEqual(p.returncode, 0, p.stderr)

    def project_events(self, name):
        p = Path(self.rig.conf["STATE_DIR"]) / name / "events.jsonl"
        return [json.loads(x) for x in p.read_text().splitlines()]

    def test_reply_one_project_only(self):
        self.two_projects()
        self.loop(DAY)
        nums = {n: [e["detail"]["item"] for e in self.project_events(n) if e["event"] == "approval_ask"]
                for n in ("demo", "gtm")}
        self.assertEqual(sorted(nums["demo"] + nums["gtm"]), [1, 2])
        self.assertIn(f'{nums["gtm"][0]}. gtm: Rotate the gtm key', self.sent())
        (self.rig.rt / "poll").write_text(json.dumps({"update_id": 9, "from_id": 111111, "date": 1792152000,
                                                      "text": f'{nums["gtm"][0]} y', "edited": False}) + "\n")
        self.loop("2026-10-16T12:05:00Z")
        answers = {n: [e for e in self.project_events(n) if e["event"] == "approval_answer"] for n in ("demo", "gtm")}
        self.assertEqual([a["detail"]["item"] for a in answers["gtm"]], nums["gtm"])
        self.assertEqual(answers["demo"], [])
        self.assertFalse([e for n in ("demo", "gtm") for e in self.project_events(n)
                          if "not understood" in (e.get("detail") or {}).get("text", "")])


if __name__ == "__main__":
    unittest.main()
