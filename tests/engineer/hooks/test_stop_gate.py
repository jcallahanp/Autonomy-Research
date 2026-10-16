"""stop_gate.py: the task's check and the DEPENDENTS rule hold the session open (Stop, TaskCompleted)."""
import json
import unittest
from pathlib import Path

from hookfix import HookCase, git

TASK = {"ENGINEER_TASK_ID": "t1", "ENGINEER_PROJECT": "demo"}


class StopGateTest(HookCase):
    def setUp(self):
        super().setUp()
        self.set_check("true")
        self.write(self.proj / "docs/DEPENDENTS.md",
                   "# Dependents\n\n| Source glob | Dependent doc |\n| --- | --- |\n| `src/**` | `docs/api.md` |\n")
        self.write(self.proj / "docs/api.md", "api\n")
        self.commit(self.proj, "plan")
        git(self.proj, "checkout", "-q", "-b", "task/t1", env=self.env)

    def set_check(self, check):
        task = {"id": "t1", "title": "T", "type": "feat", "status": "running", "depends_on": [],
                "requirement_ids": [], "files": [], "check": check, "passes": False, "attempts": 0}
        self.write(self.proj / "docs/plan/tasks.json", json.dumps({"version": 1, "tasks": [task]}))

    def stop(self, env=TASK, name="Stop"):
        ev = {"session_id": "sess-1", "transcript_path": "x", "cwd": str(self.proj),
              "hook_event_name": name, "stop_hook_active": False}
        if name == "TaskCompleted":
            ev.update(task_id="1", task_subject="t1")
        return self.run_hook("stop_gate.py", ev, env=env)

    def counter(self):
        return self.home / ".cache" / "engineer" / "stop-sess-1"

    def test_no_task_id_allows(self):
        self.set_check("exit 1")
        self.assertAllowed(self.stop(env={}))

    def test_failing_check_blocks_with_tail(self):
        self.set_check("for i in $(seq 1 50); do echo line$i; done; exit 1")
        r = self.stop()
        self.assertDenied(r, "line50")
        self.assertNotIn("line20\n", r.stderr)
        self.assertEqual(self.counter().read_text().strip(), "1")

    def test_check_runs_in_project_dir(self):
        self.set_check("test -f docs/api.md")
        self.assertAllowed(self.stop())

    def test_passing_check_and_clean_tree_allows(self):
        self.assertAllowed(self.stop())

    def test_dependents_doc_missing_blocks(self):
        self.write(self.proj / "src/a.py", "A = 2\n")
        self.commit(self.proj, "change src")
        r = self.stop()
        self.assertDenied(r, "src/a.py")
        self.assertIn("docs/api.md", r.stderr)

    def test_dependents_working_tree_counts(self):
        self.write(self.proj / "src/new.py", "B = 1\n")
        self.assertDenied(self.stop(), "docs/api.md")
        self.write(self.proj / "docs/api.md", "api v2\n")
        self.assertAllowed(self.stop())

    def test_dependents_both_changed_allows(self):
        self.write(self.proj / "src/a.py", "A = 2\n")
        self.write(self.proj / "docs/api.md", "api v2\n")
        self.commit(self.proj, "change both")
        self.assertAllowed(self.stop())

    def test_task_completed_event_gated(self):
        self.set_check("exit 3")
        self.assertDenied(self.stop(name="TaskCompleted"))

    def test_unknown_task_blocks(self):
        self.assertDenied(self.stop(env={"ENGINEER_TASK_ID": "nope"}), "nope")

    def test_eighth_block_gives_up_and_spools(self):
        self.set_check("exit 1")
        self.counter().parent.mkdir(parents=True)
        self.counter().write_text("7\n")
        r = self.stop()
        self.assertAllowed(r)
        lines = (Path(self.conf["SPOOL_DIR"]) / "sess-1.jsonl").read_text().splitlines()
        self.assertEqual(len(lines), 1)
        rec = json.loads(lines[0])
        self.assertEqual(rec["detail"]["kind"], "gate_gave_up")
        self.assertEqual(rec["task_id"], "t1")
        self.assertEqual(rec["project"], "demo")


if __name__ == "__main__":
    unittest.main()
