"""event_tap.py: StopFailure and Notification events land in the spool; it never fails."""
import json
import shutil
import unittest
from pathlib import Path

from hookfix import HookCase


class EventTapTest(HookCase):
    def tap(self, ev, raw=None):
        return self.run_hook("event_tap.py", ev, raw=raw,
                             env={"ENGINEER_TASK_ID": "t1", "ENGINEER_PROJECT": "demo"})

    def spool(self):
        return Path(self.conf["SPOOL_DIR"]) / "sess-1.jsonl"

    def test_notification_appends_one_line(self):
        ev = {"session_id": "sess-1", "cwd": str(self.proj), "hook_event_name": "Notification",
              "message": "Claude needs your permission", "notification_type": "permission_prompt"}
        self.assertAllowed(self.tap(ev))
        lines = self.spool().read_text().splitlines()
        self.assertEqual(len(lines), 1)
        rec = json.loads(lines[0])
        self.assertEqual(set(rec), {"ts", "session_id", "hook_event_name", "project", "task_id", "detail"})
        self.assertEqual(rec["hook_event_name"], "Notification")
        self.assertEqual(rec["project"], "demo")
        self.assertEqual(rec["task_id"], "t1")
        self.assertEqual(rec["detail"]["notification_type"], "permission_prompt")
        self.assertRegex(rec["ts"], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(\.\d+)?Z$")

    def test_stop_failure_appends(self):
        ev = {"session_id": "sess-1", "cwd": str(self.proj), "hook_event_name": "StopFailure",
              "error": "rate_limit", "error_details": "429"}
        self.assertAllowed(self.tap(ev))
        self.assertAllowed(self.tap(ev))
        recs = [json.loads(x) for x in self.spool().read_text().splitlines()]
        self.assertEqual([r["detail"]["error"] for r in recs], ["rate_limit", "rate_limit"])

    def test_session_id_cannot_escape_spool(self):
        ev = {"session_id": "../../evil", "cwd": str(self.proj), "hook_event_name": "Notification"}
        self.assertAllowed(self.tap(ev))
        self.assertFalse((Path(self.conf["SPOOL_DIR"]).parent.parent / "evil.jsonl").exists())
        self.assertEqual(len(list(Path(self.conf["SPOOL_DIR"]).iterdir())), 1)

    def test_unwritable_spool_still_exits_zero(self):
        spool = Path(self.conf["SPOOL_DIR"])
        shutil.rmtree(spool)
        spool.write_text("not a directory")
        ev = {"session_id": "sess-1", "cwd": str(self.proj), "hook_event_name": "Notification"}
        self.assertAllowed(self.tap(ev))

    def test_bad_input_still_exits_zero(self):
        self.assertAllowed(self.tap(None, raw="garbage"))


if __name__ == "__main__":
    unittest.main()
