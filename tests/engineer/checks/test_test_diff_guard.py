"""test-diff-guard.py: deleted tests, skip markers, fewer asserts, acceptance and test-config changes."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from gitfix import Repo

REPO = Path(__file__).resolve().parents[3]
GUARD = REPO / "engineer" / "scripts" / "checks" / "test-diff-guard.py"
FIVE = "def test_a():\n" + "".join(f"    assert {i} == {i}\n" for i in range(5))
THREE = "def test_a():\n" + "".join(f"    assert {i} == {i}\n" for i in range(3))


class GuardTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Repo(Path(self.tmp.name) / "p")
        self.base = self.repo.commit({"src/a.py": "x = 1\n", "tests/test_a.py": FIVE, "conftest.py": "# c\n",
                                      "tests/acceptance/test_acc.py": FIVE})

    def tearDown(self):
        self.tmp.cleanup()

    def guard(self, head):
        r = subprocess.run([sys.executable, str(GUARD), "--repo", self.repo.gitdir, "--base", self.base,
                            "--head", head], capture_output=True, text=True)
        return r.returncode, json.loads(r.stdout or "null"), r.stderr

    def kinds(self, findings):
        return sorted(f["kind"] for f in findings)

    def test_clean(self):
        rc, out, err = self.guard(self.repo.commit({"src/a.py": "x = 2\n"}))
        self.assertEqual((rc, out), (0, []), err)

    def test_deleted_test(self):
        rc, out, _ = self.guard(self.repo.commit(delete=["tests/test_a.py"]))
        self.assertEqual(rc, 1)
        self.assertEqual(self.kinds(out), ["deleted_test"])
        self.assertEqual(out[0]["path"], "tests/test_a.py")

    def test_fewer_asserts(self):
        rc, out, _ = self.guard(self.repo.commit({"tests/test_a.py": THREE}))
        self.assertEqual(rc, 1)
        self.assertEqual(self.kinds(out), ["fewer_asserts"])
        self.assertIn("5 -> 3", out[0]["detail"])

    def test_conftest(self):
        rc, out, _ = self.guard(self.repo.commit({"conftest.py": "# changed\n"}))
        self.assertEqual(rc, 1)
        self.assertEqual(self.kinds(out), ["test_config"])

    def test_skip_marker(self):
        rc, out, _ = self.guard(self.repo.commit({"tests/test_b.py": "import pytest\n@pytest.mark.skip\ndef test_b():\n    assert 1\n"}))
        self.assertEqual(rc, 1)
        self.assertEqual(self.kinds(out), ["skip_marker"])
        self.assertEqual(out[0]["path"], "tests/test_b.py")

    def test_js_skip(self):
        rc, out, _ = self.guard(self.repo.commit({"web/a.test.js": "it.skip('x', () => { expect(1).toBe(1) })\n"}))
        self.assertEqual(self.kinds(out), ["skip_marker"])

    def test_acceptance(self):
        rc, out, _ = self.guard(self.repo.commit({"tests/acceptance/test_acc.py": FIVE + "    assert True\n"}))
        self.assertEqual(rc, 1)
        self.assertIn("acceptance_changed", self.kinds(out))

    def test_bad_sha(self):
        r = subprocess.run([sys.executable, str(GUARD), "--repo", self.repo.gitdir, "--base", "--output=x",
                            "--head", self.base], capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
