"""session_start.py: context JSON with open tasks, progress, approval and kill-switch status."""
import json
import unittest
from pathlib import Path

from hookfix import HookCase
from eng import approval


def task(tid, status):
    return {"id": tid, "title": f"title {tid}", "type": "feat", "status": status, "depends_on": [],
            "requirement_ids": [], "files": [], "check": "true", "passes": False, "attempts": 0}


class SessionStartTest(HookCase):
    def start(self):
        ev = {"session_id": "sess-1", "cwd": str(self.proj), "hook_event_name": "SessionStart",
              "source": "startup"}
        r = self.run_hook("session_start.py", ev)
        self.assertAllowed(r)
        out = json.loads(r.stdout)
        self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "SessionStart")
        return out["hookSpecificOutput"]["additionalContext"]

    def approve(self):
        for rel in approval.SIGNED:
            self.write(self.proj / rel, f"{rel}\n")
        rec = approval.make(self.proj, "john", "telegram", "r1", 1, [], "2026-10-16")
        self.write(Path(self.conf["STATE_DIR"]) / "approvals" / "demo.json", json.dumps(rec))

    def test_context_has_tasks_approval_and_superpowers_line(self):
        tasks = [task("t1", "ready"), task("t2", "done")] + [task(f"x{i}", "todo") for i in range(30)]
        self.write(self.proj / "docs/plan/tasks.json", json.dumps({"version": 1, "tasks": tasks}))
        self.write(self.proj / "PROGRESS.md", "# Progress\n\n## Day 1\nold news\n\n## Day 2\nlatest news\n")
        self.approve()
        ctx = self.start()
        self.assertIn("t1", ctx)
        self.assertNotIn("title t2", ctx)
        self.assertIn("x18", ctx)
        self.assertNotIn("x19", ctx)
        self.assertIn("approved", ctx)
        self.assertIn("superpowers:", ctx)
        self.assertIn("latest news", ctx)
        self.assertNotIn("old news", ctx)
        self.assertIn("Kill switch: off", ctx)

    def test_changed_approval_and_kill_switch(self):
        self.approve()
        self.write(self.proj / "docs/plan/brief.md", "changed\n")
        Path(self.conf["KILL_SWITCH"]).write_text("x")
        ctx = self.start()
        self.assertIn("changed: docs/plan/brief.md", ctx)
        self.assertIn("Kill switch: on", ctx)

    def test_bare_project_still_valid(self):
        ctx = self.start()
        self.assertIn("Plan approval: none", ctx)
        self.assertIn("superpowers:", ctx)

    def test_bad_input_still_exits_zero(self):
        r = self.run_hook("session_start.py", None, raw="nope")
        self.assertAllowed(r)
        self.assertIn("superpowers:", json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"])


if __name__ == "__main__":
    unittest.main()
