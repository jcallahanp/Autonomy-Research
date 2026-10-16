"""loop.py: tasks come only from the approved tasks.json (status ignored), and a night with an auto-merging PR
stays open until the window ends or a bound stops it."""
import json
import unittest
from pathlib import Path

from loopfix import DAY, NIGHT, SHA, Rig, task


class LoopPlanTest(unittest.TestCase):
    def setUp(self):
        self.rig = Rig()
        self.addCleanup(self.rig.close)

    def run_ok(self, *a):
        p = self.rig.run(*a)
        self.assertEqual(p.returncode, 0, p.stderr)
        return p

    def runs(self):
        return [a for a in self.rig.argv() if a.startswith("run-task")]

    def test_working_tree_tasks_json_not_approved_runs_nothing(self):
        self.rig.tasks([task("t1")])
        self.rig.tasks([task("t1"), task("t9")], approve=False)  # the engineer edited the clone's copy
        self.run_ok()
        self.assertEqual(self.runs(), [])
        self.assertEqual(self.rig.status()["state"], "blocked")
        self.assertIn("approved", self.rig.status()["reason"])

    def test_stored_approved_copy_wins_over_the_working_tree(self):
        approved = self.rig.tasks([{**task("t1"), "title": "approved title"}])
        self.run_ok(DAY)  # makes the records clone, where approve-plan stores the approved copy
        stored = Path(self.rig.conf["RECORDS_DIR"]) / "demo" / "approvals" / "demo" / "v1" / "docs" / "plan"
        stored.mkdir(parents=True)
        (stored / "tasks.json").write_bytes(approved)
        self.rig.tasks([{**task("t1"), "title": "sneaky title"}, task("t9")], approve=False)
        self.run_ok()
        self.assertFalse([a for a in self.runs() if " t9 " in a])
        self.assertTrue([a for a in self.rig.argv() if a.startswith("agent-run open-pr demo task/t1 feat: approved title")],
                        self.rig.argv())

    def test_status_in_tasks_json_is_ignored(self):
        self.rig.tasks([{**task("t1"), "status": "done"}, {**task("t2"), "status": "blocked"}])
        self.run_ok()
        self.assertTrue([a for a in self.runs() if a.startswith("run-task demo t1 implementer")], self.runs())

    def test_night_stays_open_while_a_pr_auto_merges(self):
        self.rig.tasks([task("t1"), task("t2", ["t1"])])
        self.run_ok()  # t1 passes; tier 1 auto-merge on; t2 waits for the merge
        self.run_ok()
        kinds = [e["event"] for e in self.rig.events()]
        self.assertNotIn("night_end", kinds)
        self.assertEqual(kinds.count("night_start"), 1)
        self.assertFalse([a for a in self.runs() if " t2 " in a])
        self.run_ok("2026-10-16T11:00:00Z")  # 07:00 in New York: the window has ended
        self.assertEqual([e["event"] for e in self.rig.events()].count("night_end"), 1)

    def test_night_ends_when_the_review_needs_john(self):
        self.rig.reply("automerge", {"tier": 2, "auto_merge": False, "reasons": ["auth/**"]}, rc=3)
        self.run_ok()
        self.run_ok()
        self.assertEqual(self.rig.status()["state"], "done")
        self.assertIn("waiting for merge", self.rig.status()["reason"])

    def test_merge_event_then_dependents_run_in_the_same_night(self):
        self.rig.tasks([task("t1"), task("t2", ["t1"])])
        self.run_ok()
        ev = Path(self.rig.conf["STATE_DIR"]) / "demo" / "events.jsonl"
        with open(ev, "a") as f:
            f.write(json.dumps({"ts": "2026-10-16T07:05:00Z", "project": "demo", "event": "merge", "task_id": "t1",
                                "head_sha": SHA, "detail": {"merged": True, "number": 7}}) + "\n")
        self.run_ok(NIGHT)
        self.assertTrue([a for a in self.runs() if a.startswith("run-task demo t2 implementer")], self.runs())


if __name__ == "__main__":
    unittest.main()
