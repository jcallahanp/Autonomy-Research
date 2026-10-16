"""items: open asks, T1 timeouts (never T2) and reminders."""
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "engineer" / "scripts"))
from approvals import items  # noqa: E402

NOW = "2026-10-20T12:00:00Z"


def ask(n, tier="T1", hours_ago=1, reversible=True, **extra):
    from datetime import datetime, timedelta, timezone
    ts = (datetime(2026, 10, 20, 12, tzinfo=timezone.utc) - timedelta(hours=hours_ago)).strftime("%Y-%m-%dT%H:%M:%SZ")
    detail = {"item": n, "tier": tier, "kind": "merge", "text": f"ask {n}", "default": "yes",
              "reversible": reversible, "ref": f"pr-{n}"}
    if tier == "T2":
        detail["phrase"] = "SPEND $12"
    detail.update(extra)
    return {"ts": ts, "project": "demo", "event": "approval_ask", "detail": detail}


class Items(unittest.TestCase):
    def test_item_number_round_trip(self):
        for n in (1, 7, 123456789):
            self.assertEqual(items.item_key(n), str(n))
            self.assertEqual(items.item_num(items.item_key(n)), n)
            self.assertEqual(items.item_num(n), n)
        rec = items.record({"item": 4, "tier": "T1", "kind": "merge", "text": "t"}, NOW, "yes", "telegram")
        self.assertEqual((rec["item"], items.item_num(rec["item"])), ("4", 4))
        for bad in (0, -1, True, "", "04x", "\uff11", "1.0", None, 1.5):
            self.assertIsNone(items.item_num(bad), bad)
        with self.assertRaises(ValueError):
            items.item_key("4")

    def test_open_items_skip_answered(self):
        events = [ask(1), ask(2), {"ts": NOW, "project": "demo", "event": "task_start"}]
        records = [{"item": "1", "answer": "yes"}]
        self.assertEqual(sorted(items.open_items(events, records, NOW)), [2])

    def test_open_items_skip_malformed(self):
        events = [ask(1, tier="T2", phrase=""), ask(True), ask("3"), ask(4, tier="T3")]
        self.assertEqual(items.open_items(events, [], NOW), {})

    def test_reversible_t1_times_out_to_default(self):
        open_ = items.open_items([ask(1, hours_ago=25)], [], NOW)
        recs = items.apply_timeouts(open_, NOW)
        self.assertEqual(len(recs), 1)
        self.assertEqual((recs[0]["item"], recs[0]["answer"], recs[0]["source"]), ("1", "default", "timeout"))

    def test_non_reversible_t1_stays_open(self):
        open_ = items.open_items([ask(1, hours_ago=25, reversible=False)], [], NOW)
        self.assertEqual(items.apply_timeouts(open_, NOW), [])

    def test_t2_never_times_out(self):
        open_ = items.open_items([ask(4, tier="T2", hours_ago=100)], [], NOW)
        self.assertEqual(items.apply_timeouts(open_, NOW), [])

    def test_young_t1_stays_open(self):
        open_ = items.open_items([ask(1, hours_ago=23)], [], NOW)
        self.assertEqual(items.apply_timeouts(open_, NOW), [])

    def test_reminder_at_12h(self):
        open_ = items.open_items([ask(1, hours_ago=12), ask(2, hours_ago=11)], [], NOW)
        self.assertEqual(items.reminders(open_, NOW), [1])

    def test_next_item(self):
        self.assertEqual(items.next_item([ask(3), ask(7)]), 8)
        self.assertEqual(items.next_item([]), 1)


if __name__ == "__main__":
    unittest.main()
