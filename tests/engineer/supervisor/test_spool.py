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

    def test_spool_maps_event_tap_lines(self):
        """Lines written by the real plugin/hooks/event_tap.py and hookctx.tap_record map to events."""
        import os
        import subprocess
        sys.path.insert(0, str(REPO / "tests" / "engineer"))
        import testlib
        root = testlib.make_root(self.spool.parent / "t")
        conf_spool = Path(next(l.split("=", 1)[1].strip('"') for l in (root / "etc/engineer.conf").read_text().splitlines()
                               if l.startswith("SPOOL_DIR=")))
        conf_spool.mkdir(parents=True, exist_ok=True)
        env = dict(os.environ, ENGINEER_PROJECT="demo", ENGINEER_TASK_ID="t1")
        for ev in ({"hook_event_name": "Notification", "notification_type": "permission_prompt", "message": "m"},
                   {"hook_event_name": "StopFailure", "error": "rate_limit"}):
            ev.update(session_id="sess-9", cwd=str(self.spool.parent))
            subprocess.run([sys.executable, str(root / "plugin/hooks/event_tap.py")], input=json.dumps(ev),
                           env=env, text=True, check=True, capture_output=True)
        code = ("import json, sys; sys.path.insert(0, sys.argv[1]); import hookctx\n"
                "for h in ('Stop', 'TaskCompleted'):\n"
                "    print(json.dumps(hookctx.tap_record({'session_id': 'sess-9', 'hook_event_name': h}, None,"
                " {'kind': 'gate_gave_up', 'blocks': 3, 'reason': 'check fails'})))")
        out = subprocess.run([sys.executable, "-c", code, str(root / "plugin/hooks")], env=env, text=True,
                             check=True, capture_output=True).stdout
        with open(conf_spool / "sess-9.jsonl", "a") as f:
            f.write(out)
        self.assertEqual(spool.ingest(conf_spool, self.events, "demo"), 4)
        got = events.read(self.events)
        self.assertEqual([e["event"] for e in got], ["denial", "limit", "gate", "gate"])
        self.assertEqual(got[0]["detail"]["kind"], "permission_prompt")
        self.assertTrue(all(e["task_id"] == "t1" and e["session_id"] == "sess-9" and e["project"] == "demo"
                            and e["detail"]["source"] == "hook" for e in got))
        self.assertEqual([e["detail"]["hook_event_name"] for e in got[2:]], ["Stop", "TaskCompleted"])
        self.assertEqual(got[3]["detail"]["kind"], "gate_gave_up")

    def test_unknown_hook_event_dropped(self):
        (self.spool / "s4.jsonl").write_text(tap("SessionStart") + "\n" + tap("Stop", kind="other") + "\n")
        counts = {}
        self.assertEqual(spool.ingest(self.spool, self.events, "demo", counts), 0)
        self.assertEqual(counts["dropped"], 2)


if __name__ == "__main__":
    unittest.main()
