import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "engineer" / "scripts"))

from eng import approval, schema  # noqa: E402


class ApprovalTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        for rel in approval.SIGNED:
            (self.repo / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.repo / rel).write_text(f"synthetic {rel}\n")
        self.a = approval.make(self.repo, "john", "telegram", "rec-1", 1, ["money"], "2026-10-16")

    def tearDown(self):
        self._tmp.cleanup()

    def test_make_has_four_hashes_and_validates(self):
        self.assertEqual(len(self.a["files"]), 4)
        self.assertTrue(all(len(v) == 64 for v in self.a["files"].values()))
        self.assertEqual(schema.validate(self.a, schema.load(REPO / "engineer", "approval")), [])

    def test_check_clean(self):
        self.assertEqual(approval.check(self.repo, self.a), [])

    def test_check_edited_file(self):
        (self.repo / "docs/plan/brief.md").write_text("changed\n")
        errs = approval.check(self.repo, self.a)
        self.assertEqual(len(errs), 1)
        self.assertIn("docs/plan/brief.md", errs[0])

    def test_check_missing_file(self):
        (self.repo / "docs/plan/profile.yaml").unlink()
        errs = approval.check(self.repo, self.a)
        self.assertEqual(len(errs), 1)
        self.assertIn("docs/plan/profile.yaml", errs[0])

    def test_check_none(self):
        self.assertEqual(approval.check(self.repo, None), ["no approval"])

    def test_check_hash_missing_from_approval(self):
        del self.a["files"]["docs/plan/integrations.yaml"]
        errs = approval.check(self.repo, self.a)
        self.assertEqual(len(errs), 1)
        self.assertIn("integrations.yaml", errs[0])

    def test_check_malformed(self):
        self.assertTrue(approval.check(self.repo, {"files": "nope"}))

    def test_make_missing_file_raises(self):
        (self.repo / "docs/plan/brief.md").unlink()
        with self.assertRaises(FileNotFoundError):
            approval.make(self.repo, "john", "pr", "rec-2", 2, [], "2026-10-16")


if __name__ == "__main__":
    unittest.main()
