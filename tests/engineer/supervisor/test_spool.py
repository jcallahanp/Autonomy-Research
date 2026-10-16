import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "engineer" / "scripts"))

from supervisor import events, spool  # noqa: E402


def tap(hook, project="demo", **detail):
    return json.dumps({"ts": "2026-10-16T03:00:00Z", "session_id": "s1", "hook_event_name": hook,
                       "project": project, "task_id": "t1", "detail": detail})


class SpoolTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.spool = Path(tmp.name) / "spool"
        self.spool.mkdir()
        self.events = Path(tmp.name) / "demo" / "events.jsonl"

    def test_ingest_maps_kinds(self):
        (self.spool / "s1.jsonl").write_text("\n".join([
            tap("StopFailure", error="rate_limit"), tap("Notification", notification_type="permission_prompt"),
            tap("Stop", kind="gate_gave_up")]) + "\n")
        self.assertEqual(spool.ingest(self.spool, self.events, "demo"), 3)
        got = events.read(self.events)
        self.assertEqual([e["event"] for e in got], ["limit", "denial", "gate"])
        self.assertTrue(all(e["detail"]["source"] == "hook" for e in got))
        self.assertEqual(got[1]["detail"]["kind"], "permission_prompt")
        self.assertEqual(got[0]["session_id"], "s1")
        self.assertEqual(list(self.spool.iterdir()), [])

    def test_spool_ingest_drops_invalid(self):
        (self.spool / "s2.jsonl").write_text("\n".join([
            "not json", "[1]", json.dumps({"hook_event_name": "Stop"}), tap("Notification"),
            '{"ts": "2026']))
        counts = {}
        self.assertEqual(spool.ingest(self.spool, self.events, "demo", counts), 1)
        self.assertEqual(counts["dropped"], 4)
        self.assertEqual(len(events.read(self.events)), 1)
        self.assertFalse((self.spool / "s2.jsonl").exists())

    def test_other_project_file_left_alone(self):
        (self.spool / "s3.jsonl").write_text(tap("Notification", project="other") + "\n")
        self.assertEqual(spool.ingest(self.spool, self.events, "demo"), 0)
        self.assertTrue((self.spool / "s3.jsonl").exists())
        self.assertFalse(self.events.exists())

    def test_missing_spool_dir(self):
        self.assertEqual(spool.ingest(self.spool / "nope", self.events, "demo"), 0)


if __name__ == "__main__":
    unittest.main()
