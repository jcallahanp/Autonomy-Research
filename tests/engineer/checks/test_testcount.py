"""testcount.parse: one sample per runner format; unrelated text gives None. Plus the --result CLI."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
CHECKS = REPO / "engineer" / "scripts" / "checks"
sys.path.insert(0, str(CHECKS))
import testcount  # noqa: E402

SHA = "a" * 40


class ParseTest(unittest.TestCase):
    def test_explicit(self):
        self.assertEqual(testcount.parse("build ok\nTESTS_RUN=7\n"), 7)

    def test_explicit_wins_over_runner(self):
        self.assertEqual(testcount.parse("3 passed in 0.1s\nTESTS_RUN=9"), 9)

    def test_pytest(self):
        self.assertEqual(testcount.parse("===== 12 passed, 1 skipped in 0.42s ====="), 12)

    def test_unittest(self):
        self.assertEqual(testcount.parse("....\n----\nRan 4 tests in 0.003s\n\nOK"), 4)

    def test_jest(self):
        self.assertEqual(testcount.parse("Tests:       1 skipped, 6 passed, 7 total"), 6)

    def test_vitest(self):
        self.assertEqual(testcount.parse("  Test Files  2 passed (2)\n      Tests  8 passed (8)"), 8)

    def test_node(self):
        self.assertEqual(testcount.parse("# tests 5\n# suites 1\n# pass 5\n# fail 0"), 5)

    def test_tap(self):
        self.assertEqual(testcount.parse("1..3\nok 1 a\nok 2 b\nok 3 c"), 3)

    def test_zero(self):
        self.assertEqual(testcount.parse("TESTS_RUN=0"), 0)

    def test_unrelated(self):
        self.assertIsNone(testcount.parse("compiled 3 files, all good"))
        self.assertIsNone(testcount.parse(""))
        self.assertIsNone(testcount.parse(None))


class ResultCliTest(unittest.TestCase):
    def run_cli(self, result: dict, head: str = SHA):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "r.json"
            p.write_text(json.dumps(result))
            return subprocess.run([sys.executable, str(CHECKS / "testcount.py"), "--result", str(p), "--head", head],
                                  capture_output=True, text=True)

    def test_good_result(self):
        r = self.run_cli({"exit_code": 0, "is_error": False, "head_sha": SHA, "output_tail": "TESTS_RUN=3"})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("3 tests", r.stdout)

    def test_stale_sha(self):
        r = self.run_cli({"exit_code": 0, "is_error": False, "head_sha": "b" * 40, "output_tail": "TESTS_RUN=3"})
        self.assertEqual(r.returncode, 1)
        self.assertIn("head_sha", r.stdout)

    def test_nonzero_exit(self):
        r = self.run_cli({"exit_code": 2, "is_error": True, "head_sha": SHA, "output_tail": "TESTS_RUN=3"})
        self.assertEqual(r.returncode, 1)

    def test_no_tests(self):
        r = self.run_cli({"exit_code": 0, "is_error": False, "head_sha": SHA, "output_tail": "TESTS_RUN=0"})
        self.assertEqual(r.returncode, 1)

    def test_missing_file(self):
        r = subprocess.run([sys.executable, str(CHECKS / "testcount.py"), "--result", "/nonexistent/x.json",
                            "--head", SHA], capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        self.assertIn("no check result", r.stdout)


if __name__ == "__main__":
    unittest.main()
