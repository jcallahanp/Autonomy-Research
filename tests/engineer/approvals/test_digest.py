"""digest.render / render_t2: the morning T1 digest and the separate T2 hard-gate message."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "engineer" / "scripts"))
from approvals import digest  # noqa: E402


def t1(n, text=None, ts=None):
    return {"item": n, "tier": "T1", "kind": "merge", "text": text or f"Merge PR {n}",
            "default": "no", "asked_at": ts or f"2026-10-16T0{n}:00:00Z"}


class Digest(unittest.TestCase):
    def test_six_items_five_lines_and_more(self):
        msgs = digest.render({n: t1(n) for n in range(6, 0, -1)}, max_open=5)
        lines = "\n".join(msgs).splitlines()
        self.assertEqual(len(lines), 6)
        self.assertEqual(lines[0], '1. Merge PR 1 (default: no). Reply "1 y" or "1 n".')
        self.assertEqual(lines[4][:3], "5. ")
        self.assertEqual(lines[5], "+1 more in the next digest")

    def test_oldest_first(self):
        items = {1: t1(1, ts="2026-10-16T09:00:00Z"), 2: t1(2, ts="2026-10-16T01:00:00Z")}
        msgs = digest.render(items)
        self.assertTrue(msgs[0].startswith("2. "))

    def test_long_text_splits_into_messages(self):
        msgs = digest.render({1: t1(1, text="x" * 5000)})
        self.assertEqual(len(msgs), 2)
        self.assertTrue(all(len(m) <= 4096 for m in msgs))

    def test_t2_not_in_t1_digest(self):
        items = {1: t1(1), 2: {"item": 2, "tier": "T2", "text": "Pay", "phrase": "PAY $5"}}
        self.assertNotIn("Pay", "\n".join(digest.render(items)))

    def test_newlines_in_text_stay_one_line(self):
        msgs = digest.render({1: t1(1, text="a\nb")})
        self.assertEqual(msgs, ['1. a b (default: no). Reply "1 y" or "1 n".'])

    def test_lines_carry_the_project(self):
        msgs = digest.render({3: {**t1(3), "project": "gtm"}})
        self.assertEqual(msgs, ['3. gtm: Merge PR 3 (default: no). Reply "3 y" or "3 n".'])
        item = {"item": 4, "tier": "T2", "text": "Buy the domain", "phrase": "SPEND $12", "project": "gtm"}
        self.assertTrue(digest.render_t2(item).startswith("HARD GATE 4: gtm: Buy the domain\n"))

    def test_reminder(self):
        self.assertEqual(digest.render_reminder({**t1(3), "project": "gtm"}),
                         'Reminder: 3. gtm: Merge PR 3 (default: no). Reply "3 y" or "3 n".')
        item = {"item": 4, "tier": "T2", "text": "Pay", "phrase": "PAY $5", "project": "gtm"}
        self.assertEqual(digest.render_reminder(item), "Reminder: " + digest.render_t2(item))

    def test_render_t2(self):
        item = {"item": 4, "tier": "T2", "text": "Buy the domain", "phrase": "SPEND $12"}
        self.assertEqual(digest.render_t2(item),
                         "HARD GATE 4: Buy the domain\nTo approve, reply exactly: CONFIRM 4 SPEND $12\n"
                         "No reply means no.")

    def test_empty(self):
        self.assertEqual(digest.render({}), [])

    def test_cli_prints_json_list_with_t2_separate(self):
        with tempfile.TemporaryDirectory() as tmp:
            ev, rec = Path(tmp) / "events.jsonl", Path(tmp) / "approvals.jsonl"
            asks = [(1, "T1", {}), (2, "T2", {"phrase": "DELETE ROWS"})]
            ev.write_text("".join(json.dumps(
                {"ts": "2026-10-16T01:00:00Z", "project": "demo", "event": "approval_ask",
                 "detail": {"item": n, "tier": tier, "kind": "other", "text": f"ask {n}", "default": "no",
                            "reversible": True, "ref": None, **extra}}) + "\n" for n, tier, extra in asks))
            out = subprocess.run([sys.executable, str(REPO / "engineer/scripts/approvals/digest.py"),
                                  "--events", str(ev), "--records", str(rec), "--now", "2026-10-16T07:30:00Z"],
                                 capture_output=True, text=True, check=True)
            msgs = json.loads(out.stdout)
            self.assertEqual(msgs[0], "HARD GATE 2: demo: ask 2\nTo approve, reply exactly: CONFIRM 2 DELETE ROWS\n"
                                      "No reply means no.")
            self.assertEqual(msgs[1], '1. demo: ask 1 (default: no). Reply "1 y" or "1 n".')

    def test_cli_json_object_lists_shown_items(self):
        with tempfile.TemporaryDirectory() as tmp:
            ev, rec = Path(tmp) / "events.jsonl", Path(tmp) / "approvals.jsonl"
            ev.write_text("".join(json.dumps(
                {"ts": f"2026-10-16T0{n}:00:00Z", "project": "demo", "event": "approval_ask",
                 "detail": {"item": n, "tier": "T1", "kind": "other", "text": f"ask {n}", "default": "no",
                            "reversible": True, "ref": None}}) + "\n" for n in range(1, 8)))
            out = subprocess.run([sys.executable, str(REPO / "engineer/scripts/approvals/digest.py"),
                                  "--events", str(ev), "--records", str(rec), "--now", "2026-10-16T09:30:00Z",
                                  "--max-open", "5", "--json-object"], capture_output=True, text=True, check=True)
            doc = json.loads(out.stdout)
            self.assertEqual(doc["shown"], [1, 2, 3, 4, 5])
            self.assertIn("+2 more in the next digest", doc["messages"][-1])


    def test_cli_pending_answers_count(self):
        """A reply kept in STATE_DIR/<p>/approvals.pending.jsonl (no records clone) closes its item too."""
        with tempfile.TemporaryDirectory() as tmp:
            ev, rec = Path(tmp) / "events.jsonl", Path(tmp) / "records" / "approvals.jsonl"
            ev.write_text("".join(json.dumps(
                {"ts": f"2026-10-16T0{n}:00:00Z", "project": "demo", "event": "approval_ask",
                 "detail": {"item": n, "tier": "T1", "kind": "other", "text": f"ask {n}", "default": "no",
                            "reversible": True, "ref": None}}) + "\n" for n in (1, 2)))
            (Path(tmp) / "approvals.pending.jsonl").write_text(json.dumps({"item": "1", "answer": "yes"}) + "\n")
            clone = Path(tmp) / "clone.jsonl"  # the records clone's file, read only while replies go to pending
            clone.write_text(json.dumps({"item": "2", "answer": "no"}) + "\n")
            cmd = [sys.executable, str(REPO / "engineer/scripts/approvals/digest.py"), "--events", str(ev),
                   "--records", str(rec), "--now", "2026-10-16T09:30:00Z", "--json-object"]
            out = subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.assertEqual(json.loads(out.stdout)["shown"], [2])
            out = subprocess.run(cmd + ["--read-records", str(clone)], capture_output=True, text=True, check=True)
            self.assertEqual(json.loads(out.stdout)["shown"], [])


if __name__ == "__main__":
    unittest.main()
