"""Usage-limit texts here are SYNTHETIC placeholders, not captured output. Spike SP07 (setup day) captures
the real headless usage-limit text; replace these fixtures and the patterns in limits.py with it."""
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "engineer" / "scripts"))

from supervisor import limits  # noqa: E402

NOW = datetime(2026, 10, 16, 5, 0, tzinfo=timezone.utc)  # 01:00 in New York (EDT)
SYNTHETIC = {
    "epoch": "Claude AI usage limit reached|1792141200",
    "clock": "5-hour limit reached ∙ resets 3am",
    "clock_tz": "You've hit your limit · resets 11:30pm (America/New_York)",
    "weekly": "Weekly limit reached ∙ resets Oct 20, 9am",
    "none": "Ran 12 tests in 0.4s\nOK",
}


class LimitsTest(unittest.TestCase):
    def test_limits_session_and_weekly(self):
        got = limits.classify(SYNTHETIC["epoch"], now=NOW)
        self.assertEqual(got, {"kind": "session", "reset_at": "2026-10-16T09:00:00Z"})
        got = limits.classify(SYNTHETIC["clock"], now=NOW)
        self.assertEqual(got, {"kind": "session", "reset_at": "2026-10-16T07:00:00Z"})
        self.assertEqual(limits.classify(SYNTHETIC["weekly"], now=NOW)["kind"], "weekly")
        self.assertEqual(limits.classify(SYNTHETIC["none"], now=NOW), {"kind": None, "reset_at": None})

    def test_clock_reset_rolls_to_next_day(self):
        got = limits.classify(SYNTHETIC["clock_tz"], now=NOW)
        self.assertEqual(got, {"kind": "session", "reset_at": "2026-10-17T03:30:00Z"})

    def test_session_limit_without_reset_time(self):
        got = limits.classify("usage limit reached", now=NOW)
        self.assertEqual(got, {"kind": "session", "reset_at": None})

    def test_empty_and_none_text(self):
        self.assertEqual(limits.classify("", now=NOW)["kind"], None)
        self.assertEqual(limits.classify(None, now=NOW)["kind"], None)


if __name__ == "__main__":
    unittest.main()
