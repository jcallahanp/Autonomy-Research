"""stop_gate.py: the task's check and the DEPENDENTS rule hold the session open (Stop, TaskCompleted).

The check comes from the approved tasks.json at HEAD (its sha256 must match the live plan approval) and runs
in a clean checkout of HEAD, inside bwrap when bwrap exists.
"""
import hashlib
import json
import unittest
from pathlib import Path

from hookfix import HookCase, git, testlib

TASK = {"ENGINEER_TASK_ID": "t1", "ENGINEER_PROJECT": "demo"}


class StopGateTest(HookCase):
    def setUp(self):
        super().setUp()
        self.write(self.proj / "docs/DEPENDENTS.md",
                   "# Dependents\n\n| Source glob | Dependent doc |\n| --- | --- |\n| `src/**` | `docs/api.md` |\n")
        self.write(self.proj / "docs/api.md", "api\n")
        self.set_check("true", msg="plan")
        git(self.proj, "checkout", "-q", "-b", "task/t1", env=self.env)

    def set_check(self, check, approve=True, msg="set check"):
        """Commit tasks.json with this check for t1 and (unless approve=False) approve exactly those bytes."""
        task = {"id": "t1", "title": "T", "type": "feat", "status": "running", "depends_on": [],
                "requirement_ids": [], "files": [], "check": check, "passes": False, "attempts": 0}
        path = self.write(self.proj / "docs/plan/tasks.json", json.dumps({"version": 1, "tasks": [task]}))
        self.commit(self.proj, msg)
        if approve:
            self.approve(hashlib.sha256(path.read_bytes()).hexdigest())

    def approve(self, digest):
        self.write(Path(self.conf["STATE_DIR"]) / "approvals" / "demo.json",
                   json.dumps({"scope_version": 1, "files": {"docs/plan/tasks.json": digest}}))

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

    def test_check_runs_in_clean_checkout_of_head(self):
        self.set_check("test ! -e scratch.txt && test ! -e src/wip.py")
        self.write(self.proj / "scratch.txt", "untracked\n")
        self.write(self.proj / "docs/api.md", "api v2\n")
        self.assertAllowed(self.stop())

    def test_working_tree_tasks_json_is_ignored(self):
        self.set_check("exit 1")
        task = json.loads((self.proj / "docs/plan/tasks.json").read_text())
        task["tasks"][0]["check"] = "true"
        self.write(self.proj / "docs/plan/tasks.json", json.dumps(task))
        self.assertDenied(self.stop(), "exit 1")

    def test_unapproved_tasks_json_blocks(self):
        self.set_check("echo unapproved", approve=False)
        self.assertDenied(self.stop(), "approved")

    def test_no_approval_blocks(self):
        (Path(self.conf["STATE_DIR"]) / "approvals" / "demo.json").unlink()
        self.assertDenied(self.stop(), "approval")

    def test_check_uses_worktree_deps_and_git(self):
        self.set_check("test -f node_modules/dep/index.js && git rev-parse HEAD")
        self.write(self.proj / "node_modules/dep/index.js", "module.exports = 1\n")  # untracked
        self.assertAllowed(self.stop())
        self.assertTrue((self.proj / "node_modules/dep/index.js").exists())

    def test_check_runs_in_bwrap_when_present(self):
        path = testlib.stub(self.root, "bwrap", 'while [ "$1" != -- ]; do shift; done; shift; exec "$@"')
        self.addCleanup(path.unlink)
        (self.home / ".ssh").mkdir(exist_ok=True)
        self.set_check("echo inside")
        self.write(self.proj / "node_modules/dep/index.js", "module.exports = 1\n")
        self.assertAllowed(self.stop())
        line = [x for x in testlib.argv_log(self.root) if x.startswith("bwrap ")][-1]
        gitdir = (self.proj / ".git").resolve()
        for want in ("--unshare-all --share-net", "--ro-bind / /", "--tmpfs /tmp", "-- bash -c echo inside",
                     f"--tmpfs {self.home}/.ssh ", f"--ro-bind {gitdir} {gitdir} ",
                     f"--ro-bind {self.proj.resolve()}/node_modules "):
            self.assertIn(want, line)
        self.assertNotIn(f"--tmpfs {self.home} ", line)

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
