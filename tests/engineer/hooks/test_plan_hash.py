"""Plan-hash guard: unattended writes need John's approval of the four signed plan files."""
import json
import unittest
from pathlib import Path

from hookfix import HookCase, git
from eng import approval

UNATTENDED = {"ENGINEER_UNATTENDED": "1"}


class PlanHashTest(HookCase):
    def setUp(self):
        super().setUp()
        for rel in approval.SIGNED:
            self.write(self.proj / rel, f"{rel}\n")
        self.commit(self.proj, "plan")
        self.approve(self.proj, "demo")

    def approve(self, proj, name):
        rec = approval.make(proj, "john", "telegram", "r1", 1, [], "2026-10-16")
        path = Path(self.conf["STATE_DIR"]) / "approvals" / f"{name}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(rec))

    def edit(self, rel, cwd=None, env=UNATTENDED):
        base = cwd or self.proj
        return self.pre("Edit", {"file_path": str(base / rel), "old_string": "a", "new_string": "b"},
                        cwd=base, env=env)

    def test_approval_matches_allows(self):
        self.assertAllowed(self.edit("src/a.py"))

    def test_brief_changed_denies(self):
        self.write(self.proj / "docs/plan/brief.md", "changed\n")
        self.assertDenied(self.edit("src/a.py"), "docs/plan/brief.md")
        self.assertDenied(self.bash("echo x > src/b.py", env=UNATTENDED), "docs/plan/brief.md")

    def test_plan_files_may_change(self):
        self.write(self.proj / "docs/plan/brief.md", "changed\n")
        self.assertAllowed(self.edit("docs/plan/brief.md"))
        self.assertAllowed(self.edit("docs/plan/tasks.json"))

    def test_not_unattended_allows(self):
        self.write(self.proj / "docs/plan/brief.md", "changed\n")
        self.assertAllowed(self.edit("src/a.py", env={}))
        self.assertAllowed(self.edit("src/a.py", env={"ENGINEER_UNATTENDED": "0"}))

    def test_no_approval_denies(self):
        (Path(self.conf["STATE_DIR"]) / "approvals" / "demo.json").unlink()
        self.assertDenied(self.edit("src/a.py"), "no approval")

    def test_bash_without_write_allowed(self):
        self.write(self.proj / "docs/plan/brief.md", "changed\n")
        self.assertAllowed(self.bash("pytest -q", env=UNATTENDED))

    def test_worktree_uses_main_project_approval(self):
        wt = self.proj.parent / "demo.wt" / "t1"
        git(self.proj, "worktree", "add", "-q", "-b", "task/t1", str(wt), env=self.env)
        self.assertAllowed(self.edit("src/a.py", cwd=wt))
        self.write(wt / "docs/plan/requirements.md", "changed\n")
        self.assertDenied(self.edit("src/a.py", cwd=wt), "docs/plan/requirements.md")


if __name__ == "__main__":
    unittest.main()
