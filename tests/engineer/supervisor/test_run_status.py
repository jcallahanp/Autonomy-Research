import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "engineer" / "scripts"))

from supervisor import run_status  # noqa: E402


class RunStatusTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name) / "demo"
        self.path = self.dir / "RUN_STATUS.json"

    def test_write_valid(self):
        run_status.write(self.path, "done", reason=None, counts={"done": 2}, project="demo")
        data = json.loads(self.path.read_text())
        self.assertEqual(data["state"], "done")
        self.assertEqual(data["counts"], {"done": 2})
        self.assertIn("updated", data)

    def test_write_invalid_raises(self):
        with self.assertRaises(ValueError):
            run_status.write(self.path, "running")
        with self.assertRaises(ValueError):
            run_status.write(self.path, "done", colour="red")
        self.assertFalse(self.path.exists())

    def test_run_status_atomic(self):
        run_status.write(self.path, "waiting_for_reset", reset_at="2026-10-16T08:00:00Z")
        before = self.path.read_text()
        with mock.patch.object(os, "replace", side_effect=OSError("disk gone")):
            with self.assertRaises(OSError):
                run_status.write(self.path, "crashed", reason="KeyError")
        self.assertEqual(self.path.read_text(), before)
        self.assertEqual(json.loads(before)["state"], "waiting_for_reset")
        self.assertEqual(sorted(p.name for p in self.dir.iterdir()), ["RUN_STATUS.json"])


if __name__ == "__main__":
    unittest.main()
