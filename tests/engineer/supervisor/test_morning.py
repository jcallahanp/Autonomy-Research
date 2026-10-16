import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "engineer" / "scripts"))

from supervisor import morning  # noqa: E402


def ev(event, task_id=None, **kw):
    return {"ts": "2026-10-16T03:00:00Z", "project": "demo", "event": event, "task_id": task_id, **kw}


EVENTS = [
    ev("night_start", detail={"night": "2026-10-15"}),
    ev("task_start", "a"), ev("task_end", "a", exit_code=0, cost_usd=1.25),
    ev("audit", "a", detail={"verdict": "PASS", "status": "done"}),
    ev("pr_open", "a", detail={"number": 7, "url": "https://github.com/o/r/pull/7"}),
    ev("task_start", "b"), ev("task_end", "b", exit_code=1, cost_usd=0.5),
    ev("audit", "b", detail={"verdict": "FAIL", "status": "blocked", "reason": "check failed: 2 tests"}),
    ev("task_start", "c"), ev("task_end", "c", exit_code=0, cost_usd=None),
    ev("audit", "c", detail={"verdict": "NEEDS-JOHN", "status": "needs_john", "reason": "touches auth"}),
    ev("denial", "b", detail={"kind": "Bash", "source": "hook"}),
    ev("denial", "b", detail={"kind": "Bash", "source": "run"}),
    ev("approval_ask", "a", detail={"item": 1, "tier": 1, "kind": "merge", "text": "Merge PR 7?"}),
    ev("approval_ask", None, detail={"item": 2, "tier": 1, "kind": "promote", "text": "Promote?"}),
    ev("approval_ask", None, detail={"item": 3, "tier": 2, "kind": "money", "text": "Spend?"}),
    ev("approval_answer", None, detail={"item": 2, "answer": "y"}),
]


class MorningTest(unittest.TestCase):
    def setUp(self):
        self.md = morning.render(EVENTS, {"state": "blocked", "reason": "no task ready"})

    def test_state_line(self):
        self.assertIn("blocked", self.md.splitlines()[2])
        self.assertIn("no task ready", self.md)

    def test_morning_lists_blocked_note(self):
        section = self.md.split("## Blocked")[1].split("##")[0]
        self.assertIn("b", section)
        self.assertIn("check failed: 2 tests", section)

    def test_done_needs_john_prs(self):
        self.assertIn("- a", self.md.split("## Done")[1].split("##")[0])
        self.assertIn("touches auth", self.md.split("## Needs John")[1].split("##")[0])
        self.assertIn("https://github.com/o/r/pull/7", self.md)

    def test_denials_cost_open_t1(self):
        self.assertIn("Bash: 2", self.md)
        self.assertIn("$1.75", self.md)
        self.assertIn("Open T1 items: 1", self.md)

    def test_in_review_section(self):
        md = morning.render([ev("audit", "d", detail={"verdict": "PASS", "status": "in_review"})], {"state": "done"})
        self.assertIn("- d", md.split("## In review")[1].split("##")[0])

    def test_empty_night(self):
        md = morning.render([], {"state": "done"})
        self.assertIn("done", md)
        self.assertIn("none", md)


if __name__ == "__main__":
    unittest.main()
