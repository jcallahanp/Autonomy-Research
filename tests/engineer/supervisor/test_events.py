import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "engineer" / "scripts"))

from supervisor import events  # noqa: E402

SHA = "0123456789abcdef0123456789abcdef01234567"


class EventsTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / "demo" / "events.jsonl"

    def add(self, event, task_id=None, **kw):
        return events.append(self.path, {"project": "demo", "event": event, "task_id": task_id, **kw})

    def test_append_adds_ts_and_writes_one_line(self):
        e = self.add("night_start", detail={"night": "2026-10-16"})
        self.assertRegex(e["ts"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
        lines = self.path.read_text().splitlines()
        self.assertEqual(len(lines), 1)
        self.assertEqual(json.loads(lines[0])["event"], "night_start")

    def test_append_keeps_given_ts(self):
        e = self.add("heartbeat", ts="2026-10-16T03:00:00Z")
        self.assertEqual(e["ts"], "2026-10-16T03:00:00Z")

    def test_append_fsyncs(self):
        with mock.patch.object(os, "fsync", wraps=os.fsync) as f:
            self.add("heartbeat")
        self.assertTrue(f.called)

    def test_append_invalid_raises_and_writes_nothing(self):
        with self.assertRaises(ValueError):
            self.add("not_an_event")
        with self.assertRaises(ValueError):
            self.add("task_end", "t1", head_sha="nothex")
        self.assertFalse(self.path.exists() and self.path.read_text())

    def test_events_skip_torn_line(self):
        self.add("task_start", "t1")
        self.add("task_end", "t1", exit_code=0)
        with open(self.path, "a") as f:
            f.write('{"ts": "2026')
        counts = {}
        got = events.read(self.path, counts)
        self.assertEqual(len(got), 2)
        self.assertEqual(counts.get("skipped"), 1)

    def test_append_after_torn_line_starts_a_new_line(self):
        self.add("task_start", "t1")
        with open(self.path, "a") as f:
            f.write('{"ts": "2026')
        self.add("task_end", "t1", exit_code=0)
        got = events.read(self.path)
        self.assertEqual([e["event"] for e in got], ["task_start", "task_end"])

    def test_read_skips_schema_invalid_line(self):
        self.add("task_start", "t1")
        with open(self.path, "a") as f:
            f.write(json.dumps({"ts": "x", "project": "demo", "event": "bogus"}) + "\n[1, 2]\n")
        counts = {}
        self.assertEqual(len(events.read(self.path, counts)), 1)
        self.assertEqual(counts["skipped"], 2)

    def test_read_missing_file_is_empty(self):
        self.assertEqual(events.read(self.path), [])

    def test_state(self):
        self.add("task_start", "a")
        self.add("task_end", "a", exit_code=0)
        self.add("audit", "a", detail={"verdict": "PASS", "status": "done"})
        self.add("task_start", "b")
        self.add("task_end", "b", exit_code=1)
        self.add("audit", "b", detail={"verdict": "FAIL", "status": "retry"})
        self.add("task_start", "b")
        self.add("task_end", "b", exit_code=1)
        self.add("audit", "b", detail={"verdict": "FAIL", "status": "blocked"})
        self.add("task_start", "c")
        self.add("task_end", "c", exit_code=0)
        self.add("audit", "c", detail={"verdict": "NEEDS-JOHN", "status": "needs_john"})
        self.add("task_start", "d")
        st = events.state(events.read(self.path))
        self.assertEqual(st["done"], {"a"})
        self.assertEqual(st["blocked"], {"b"})
        self.assertEqual(st["needs_john"], {"c"})
        self.assertEqual(st["running"], {"d"})
        self.assertEqual(st["attempts"]["b"], 2)
        self.assertEqual(st["attempts"].get("a", 0), 0)

    def test_state_in_review_until_merged(self):
        """A PASS with an open PR is in_review (not done, not a failed attempt); `merge` with merged makes it done."""
        self.add("task_start", "a")
        self.add("task_end", "a", exit_code=0)
        self.add("audit", "a", head_sha=SHA, detail={"verdict": "PASS", "status": "in_review", "audited_sha": SHA})
        self.add("pr_open", "a", head_sha=SHA, detail={"number": 7, "url": "https://example.invalid/pull/7"})
        self.add("merge", "a", head_sha=SHA, detail={"tier": 1, "auto_merge": True, "number": 7})
        st = events.state(events.read(self.path))
        self.assertEqual(st["in_review"], {"a"})
        self.assertEqual(st["done"], set())
        self.assertEqual(st["attempts"].get("a", 0), 0)
        self.add("merge", "a", head_sha=SHA, detail={"merged": True, "number": 7, "merge_commit": SHA})
        st = events.state(events.read(self.path))
        self.assertEqual((st["in_review"], st["done"]), (set(), {"a"}))

    def test_deadend_yes_resets_attempts(self):
        for status in ("retry", "blocked"):
            self.add("task_end", "a", exit_code=1)
            self.add("audit", "a", detail={"verdict": "FAIL", "status": status})
        self.add("approval_answer", "a", detail={"item": 3, "kind": "deadend", "answer": "no"})
        self.assertEqual(events.state(events.read(self.path))["attempts"]["a"], 2)
        self.add("approval_answer", "a", detail={"item": 3, "kind": "deadend", "answer": "yes"})
        self.add("approval_answer", "b", detail={"item": 4, "kind": "deadend", "answer": "yes"})
        st = events.state(events.read(self.path))
        self.assertEqual((st["attempts"].get("a", 0), st["attempts"].get("b", 0)), (0, 0))
        self.add("audit", "a", detail={"verdict": "FAIL", "status": "retry"})
        self.assertEqual(events.state(events.read(self.path))["attempts"]["a"], 1)

    def test_state_waiting_and_resume(self):
        self.add("task_start", "a")
        self.add("task_end", "a", exit_code=1, session_id="s1")
        self.add("reset_wait", "a", session_id="s1", detail={"reset_at": "2026-10-16T08:00:00Z"})
        st = events.state(events.read(self.path))
        self.assertEqual(st["waiting"], {"a": {"session_id": "s1", "reset_at": "2026-10-16T08:00:00Z"}})
        self.assertEqual(st["running"], set())
        self.add("resume", "a", session_id="s1")
        st = events.state(events.read(self.path))
        self.assertEqual(st["waiting"], {})
        self.assertEqual(st["running"], {"a"})

    def test_reconcile_marks_running_as_crash(self):
        self.add("task_start", "a")
        self.add("task_end", "a", exit_code=0)
        self.add("task_start", "b")
        self.assertEqual(events.reconcile(self.path), ["b"])
        got = events.read(self.path)
        self.assertEqual([e["event"] for e in got[-2:]], ["crash", "reconcile"])
        self.assertEqual(got[-2]["task_id"], "b")
        st = events.state(got)
        self.assertEqual(st["running"], set())
        self.assertEqual(st["attempts"]["b"], 1)
        self.assertEqual(events.reconcile(self.path), [])


if __name__ == "__main__":
    unittest.main()
