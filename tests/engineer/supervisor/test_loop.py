import json
import signal
import time
import unittest
from pathlib import Path

from loopfix import DAY, OTHER, SHA, SID, Rig, result, task


class LoopTest(unittest.TestCase):
    def setUp(self):
        self.rig = Rig()
        self.addCleanup(self.rig.close)

    def run_ok(self, *a):
        p = self.rig.run(*a)
        self.assertEqual(p.returncode, 0, p.stderr)
        return p

    def outcome(self, tid="t1"):
        return [e["detail"] for e in self.rig.events() if e["event"] == "audit" and e["task_id"] == tid]

    def test_happy_path_opens_pr_and_automerges(self):
        self.run_ok()
        argv = self.rig.argv()
        rec = str(Path(self.rig.conf["RECORDS_DIR"]) / "demo")
        for want in ("run-task demo t1 implementer", "run-task demo t1 check", "audit.sh demo t1",
                     "run-task demo t1 auditor", f"agent-run push-branch {rec} engineer-records",
                     "agent-run open-pr demo task/t1 feat: task t1", "agent-run automerge demo 7", "agent-run hc-ping"):
            self.assertTrue(any(line.startswith(want) for line in argv), (want, argv))
        self.assertEqual(self.outcome()[-1]["status"], "done")
        kinds = [e["event"] for e in self.rig.events()]
        for k in ("night_start", "task_start", "task_end", "check", "audit", "pr_open", "merge"):
            self.assertIn(k, kinds)
        check = json.loads((Path(self.rig.conf["STATE_DIR"]) / "checks" / "demo" / "t1.json").read_text())
        self.assertEqual(check["output_tail"], "TESTS_RUN=3")
        self.assertIn("audit/AUDIT-t1.md", self.rig.records("log", "--name-only", "--format=%an <%ae>"))
        self.assertIn("engineer-bot <engineer-bot@users.noreply.github.com>", self.rig.records("log", "--format=%an <%ae>"))
        self.assertIn("PASS", (self.rig.rt / "pr-body.txt").read_text())

    def test_night_done_writes_morning_and_digest(self):
        self.run_ok()
        self.run_ok()
        self.assertEqual(self.rig.status()["state"], "done")
        self.assertIn("- t1", (self.rig.state_dir / "MORNING.md").read_text())
        self.assertIn("docs/runs/2026-10-15-MORNING.md", self.rig.records("log", "--name-only", "--format="))
        self.assertIn("Merge PR 7?", (self.rig.rt / "sent.txt").read_text())
        self.assertEqual([e["event"] for e in self.rig.events()][-1], "night_end")
        n = len(self.rig.argv())
        self.run_ok()
        self.assertFalse([a for a in self.rig.argv()[n:] if a.startswith("run-task")])

    def test_auditor_sha_mismatch_is_fail(self):
        self.rig.verdict("PASS", OTHER)
        self.run_ok()
        out = self.outcome()[-1]
        self.assertEqual((out["verdict"], out["status"]), ("FAIL", "retry"))
        self.assertIn("head_sha", out["reason"])
        self.assertFalse([a for a in self.rig.argv() if "open-pr" in a])

    def test_auditor_invalid_verdict_is_fail(self):
        self.rig.reply("auditor", result(output_tail="looks good to me"))
        self.run_ok()
        self.assertEqual(self.outcome()[-1]["verdict"], "FAIL")

    def test_audit_exit_other_than_0_or_1_is_fail(self):
        import testlib
        body = f"echo '{json.dumps({'verdict': 'PASS', 'head_sha': SHA, 'lines': []})}'; exit 2"
        testlib.stub(self.rig.root, "scripts/checks/audit.sh", body)
        self.run_ok()
        out = self.outcome()[-1]
        self.assertEqual(out["verdict"], "FAIL")
        self.assertIn("exit 2", out["reason"])
        self.assertFalse([a for a in self.rig.argv() if "auditor" in a or "open-pr" in a])

    def test_two_failures_block_task(self):
        self.rig.reply("implementer", result(exit_code=1, is_error=True, subtype="error_max_turns"), n=1, rc=1)
        self.rig.reply("audit", {"verdict": "FAIL", "head_sha": SHA, "lines": ["2 tests fail"]})
        self.run_ok()
        self.assertEqual(self.outcome()[-1]["status"], "retry")
        self.run_ok()
        self.assertEqual(self.outcome()[-1]["status"], "blocked")
        self.assertIn("2 tests fail", self.outcome()[-1]["reason"])
        self.run_ok()
        self.assertEqual(self.rig.status()["state"], "blocked")
        self.assertIn("2 tests fail", (self.rig.state_dir / "MORNING.md").read_text())

    def test_same_fail_twice_needs_john(self):
        self.rig.reply("audit", {"verdict": "FAIL", "head_sha": SHA, "lines": ["2 tests fail"]})
        self.run_ok()
        self.run_ok()
        self.assertEqual(self.outcome()[-1]["status"], "needs_john")

    def test_tier2_adds_merge_ask(self):
        self.rig.reply("automerge", {"tier": 2, "auto_merge": False, "reasons": ["package.json"]}, rc=3)
        self.run_ok()
        asks = [e["detail"] for e in self.rig.events() if e["event"] == "approval_ask"]
        self.assertEqual(len(asks), 1)
        self.assertEqual((asks[0]["tier"], asks[0]["kind"], asks[0]["item"]), ("T1", "merge", 1))
        self.assertEqual(asks[0]["ref"], "https://github.com/o/demo/pull/7")
        self.assertEqual(self.outcome()[-1]["status"], "done")

    def test_kill_switch_stops(self):
        Path(self.rig.conf["KILL_SWITCH"]).touch()
        self.run_ok()
        st = self.rig.status()
        self.assertEqual((st["state"], st["reason"]), ("stopped_by_bound", "kill switch"))
        self.assertFalse([a for a in self.rig.argv() if a.startswith("run-task")])

    def test_weekly_limit_stops_night(self):
        self.rig.reply("implementer", result(exit_code=1, is_error=True,
                                             output_tail="Weekly limit reached ∙ resets Oct 20, 9am"), rc=1)
        self.run_ok()
        st = self.rig.status()
        self.assertEqual(st["state"], "stopped_by_bound")
        self.assertIn("weekly", st["reason"])
        self.assertTrue((self.rig.state_dir / "MORNING.md").exists())

    def test_session_limit_waits_then_resumes(self):
        self.rig.reply("implementer", result(exit_code=1, is_error=True,
                                             output_tail="Claude AI usage limit reached|1792141200"), n=1, rc=1)
        self.run_ok()
        st = self.rig.status()
        self.assertEqual((st["state"], st["reset_at"]), ("waiting_for_reset", "2026-10-16T09:00:00Z"))
        self.run_ok("2026-10-16T08:00:00Z")
        self.assertEqual(len([a for a in self.rig.argv() if a.startswith("run-task demo t1 implementer")]), 1)
        self.run_ok("2026-10-16T09:05:00Z")
        self.assertIn(f"run-task demo t1 implementer --resume {SID}", self.rig.argv())
        self.assertEqual(self.outcome()[-1]["status"], "done")
        self.assertIn("resume", [e["event"] for e in self.rig.events()])

    def test_dag_cycle_blocks_night(self):
        self.rig.tasks([task("a", ["b"]), task("b", ["a"])])
        self.run_ok()
        st = self.rig.status()
        self.assertEqual(st["state"], "blocked")
        self.assertIn("cycle", st["reason"])
        self.assertFalse([a for a in self.rig.argv() if a.startswith("run-task")])

    def test_unknown_dependency_blocks_night(self):
        self.rig.tasks([task("a", ["zz"])])
        self.run_ok()
        self.assertEqual(self.rig.status()["state"], "blocked")
        self.assertIn("zz", self.rig.status()["reason"])

    def test_sigterm_writes_status(self):
        (self.rig.rt / "sleep").write_text("20")
        p = self.rig.popen()
        deadline = time.time() + 20
        while not [a for a in self.rig.argv() if a.startswith("run-task")] and time.time() < deadline:
            time.sleep(0.05)
        p.send_signal(signal.SIGTERM)
        p.communicate(timeout=20)
        st = self.rig.status()
        self.assertEqual((st["state"], st["reason"]), ("stopped_by_bound", "stopped by systemd"))

    def test_crash_writes_crashed(self):
        self.rig.state_dir.mkdir(parents=True, exist_ok=True)
        (self.rig.state_dir / "events.jsonl").mkdir()
        p = self.rig.run()
        self.assertNotEqual(p.returncode, 0)
        st = self.rig.status()
        self.assertEqual((st["state"], st["reason"]), ("crashed", "IsADirectoryError"))

    def test_outside_window_polls_and_sends_digest(self):
        (self.rig.rt / "poll").write_text('{"update_id": 1, "from_id": 111111, "date": 1, "text": "1 y", "edited": false}\n')
        (self.rig.rt / "apply-replies.py.out").write_text('{"item": 1, "kind": "plan", "answer": "yes", "ref": null}')
        self.run_ok(DAY)
        argv = self.rig.argv()
        self.assertFalse([a for a in argv if a.startswith("run-task")])
        self.assertTrue([a for a in argv if a.startswith("agent-run tg-poll")])
        self.assertIn("1 y", (self.rig.rt / "apply-replies.py.stdin").read_text())
        self.assertTrue([a for a in argv if a.startswith("approve-plan demo --record-id item-1 --item 1 --by john --source telegram")])
        self.assertIn("approval_answer", [e["event"] for e in self.rig.events()])
        self.assertIn("Merge PR 7?", (self.rig.rt / "sent.txt").read_text())
        n = len((self.rig.rt / "sent.txt").read_text())
        self.run_ok(DAY)
        self.assertEqual(len((self.rig.rt / "sent.txt").read_text()), n)


if __name__ == "__main__":
    unittest.main()
