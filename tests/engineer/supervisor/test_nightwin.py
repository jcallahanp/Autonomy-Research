import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "engineer" / "scripts"))

from supervisor import nightwin  # noqa: E402

TZ = "America/New_York"


def utc(*a):
    return datetime(*a, tzinfo=timezone.utc)


class NightWindowTest(unittest.TestCase):
    def test_window_crosses_midnight(self):
        self.assertTrue(nightwin.in_window(utc(2026, 10, 16, 7, 0), "22:00", "07:00", TZ))   # 03:00 EDT
        self.assertFalse(nightwin.in_window(utc(2026, 10, 16, 16, 0), "22:00", "07:00", TZ))  # 12:00 EDT
        self.assertTrue(nightwin.in_window(utc(2026, 10, 17, 2, 30), "22:00", "07:00", TZ))   # 22:30 EDT
        self.assertFalse(nightwin.in_window(utc(2026, 10, 16, 11, 0), "22:00", "07:00", TZ))  # 07:00 EDT, end
        # DST dates: 2026-03-08 (clocks go forward) and 2026-11-01 (clocks go back)
        self.assertTrue(nightwin.in_window(utc(2026, 3, 8, 7, 0), "22:00", "07:00", TZ))    # 03:00 EDT
        self.assertFalse(nightwin.in_window(utc(2026, 3, 8, 16, 0), "22:00", "07:00", TZ))  # 12:00 EDT
        self.assertTrue(nightwin.in_window(utc(2026, 11, 1, 8, 0), "22:00", "07:00", TZ))   # 03:00 EST
        self.assertFalse(nightwin.in_window(utc(2026, 11, 1, 17, 0), "22:00", "07:00", TZ))  # 12:00 EST
        self.assertTrue(nightwin.in_window(utc(2026, 11, 1, 11, 30), "22:00", "07:00", TZ))  # 06:30 EST

    def test_window_same_day(self):
        self.assertTrue(nightwin.in_window(utc(2026, 10, 16, 14, 0), "09:00", "17:00", TZ))
        self.assertFalse(nightwin.in_window(utc(2026, 10, 16, 22, 0), "09:00", "17:00", TZ))

    def test_night_key_is_start_date(self):
        self.assertEqual(nightwin.night_key(utc(2026, 10, 16, 7, 0), "22:00", TZ), "2026-10-15")
        self.assertEqual(nightwin.night_key(utc(2026, 10, 17, 2, 30), "22:00", TZ), "2026-10-16")

    def test_digest_due(self):
        at = utc(2026, 10, 16, 11, 45)  # 07:45 EDT
        self.assertTrue(nightwin.digest_due(at, None, "07:30", TZ))
        self.assertTrue(nightwin.digest_due(at, "2026-10-15", "07:30", TZ))
        self.assertFalse(nightwin.digest_due(at, "2026-10-16", "07:30", TZ))
        self.assertFalse(nightwin.digest_due(utc(2026, 10, 16, 11, 0), None, "07:30", TZ))  # 07:00 EDT


if __name__ == "__main__":
    unittest.main()
