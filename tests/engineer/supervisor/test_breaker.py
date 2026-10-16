import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "engineer" / "scripts"))

from supervisor import breaker  # noqa: E402


def s(diff, sig=None):
    return {"diff": diff, "failure_sig": sig}


class BreakerTest(unittest.TestCase):
    def test_task_blocked(self):
        self.assertFalse(breaker.task_blocked(0))
        self.assertFalse(breaker.task_blocked(1))
        self.assertTrue(breaker.task_blocked(2))
        self.assertTrue(breaker.task_blocked(3, max_attempts=3))

    def test_breaker_three_no_diff(self):
        self.assertIsNone(breaker.night_stop([s(False), s(False), s(True), s(False)]))
        reason = breaker.night_stop([s(True), s(False), s(False), s(False)])
        self.assertIn("no diff", reason)

    def test_breaker_same_failure_five(self):
        mixed = [s(True, "x"), s(True, "y")] * 4
        self.assertIsNone(breaker.night_stop(mixed))
        reason = breaker.night_stop([s(True, "sig1")] * 4 + [s(True, "sig2"), s(True, "sig1")])
        self.assertIn("same failure", reason)

    def test_none_signature_never_counts(self):
        self.assertIsNone(breaker.night_stop([s(True, None)] * 9))

    def test_custom_limits(self):
        self.assertIsNotNone(breaker.night_stop([s(False)], no_diff=1))
        self.assertIsNotNone(breaker.night_stop([s(True, "a")] * 2, same_failure=2))

    def test_task_status(self):
        self.assertEqual(breaker.task_status("PASS", None, [], 1), "done")
        self.assertEqual(breaker.task_status("NEEDS-JOHN", "a", [], 1), "needs_john")
        self.assertEqual(breaker.task_status("FAIL", "a", [], 1), "retry")
        self.assertEqual(breaker.task_status("FAIL", "a", ["a"], 2), "needs_john")
        self.assertEqual(breaker.task_status("FAIL", "b", ["a"], 2), "blocked")

    def test_denial_limit_per_kind(self):
        def denial(kind):
            return {"event": "denial", "detail": {"kind": kind}}
        night = [denial("Bash")] * 4 + [denial("Write")] * 4
        self.assertIsNone(breaker.night_bound({"denials_per_kind_per_night": 5}, night))
        reason = breaker.night_bound({"denials_per_kind_per_night": 5}, night + [denial("Bash")])
        self.assertIn("5 Bash denials", reason)

    def test_night_bound_uses_outcome_events(self):
        out = {"event": "audit", "detail": {"status": "retry", "diff": False, "sig": "x"}}
        self.assertIn("no diff", breaker.night_bound({}, [out] * 3))


if __name__ == "__main__":
    unittest.main()
