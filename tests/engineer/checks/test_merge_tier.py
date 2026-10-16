"""merge-tier.py: tier 1 only for small, typed, non-breaking PRs outside tier-2 and protected paths."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TIER = REPO / "engineer" / "scripts" / "checks" / "merge-tier.py"


def tier(title, files):
    body = {"title": title, "files": [{"path": p, "additions": a, "deletions": d} for p, a, d in files]}
    r = subprocess.run([sys.executable, str(TIER)], input=json.dumps(body), capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


class TierTest(unittest.TestCase):
    def test_small_fix_is_tier1(self):
        self.assertEqual(tier("fix: x", [("src/a.py", 6, 4)]), {"tier": 1, "reasons": []})

    def test_breaking_bang(self):
        out = tier("feat!: x", [("src/a.py", 6, 4)])
        self.assertEqual(out["tier"], 2)
        self.assertEqual(len(out["reasons"]), 1)

    def test_breaking_footer_word(self):
        self.assertEqual(tier("feat: x BREAKING CHANGE", [("src/a.py", 1, 0)])["tier"], 2)

    def test_lockfile(self):
        self.assertEqual(tier("chore: bump", [("package-lock.json", 10, 10)])["tier"], 2)

    def test_too_many_files(self):
        self.assertEqual(tier("fix: x", [(f"src/f{i}.py", 1, 0) for i in range(21)])["tier"], 2)
        self.assertEqual(tier("fix: x", [(f"src/f{i}.py", 1, 0) for i in range(20)])["tier"], 1)

    def test_too_many_lines(self):
        self.assertEqual(tier("fix: x", [("src/a.py", 1000, 1)])["tier"], 2)
        self.assertEqual(tier("fix: x", [("src/a.py", 1000, 0)])["tier"], 1)

    def test_ci_type(self):
        self.assertEqual(tier("ci: x", [("src/a.py", 1, 0)])["tier"], 2)

    def test_untyped_title(self):
        self.assertEqual(tier("update stuff", [("src/a.py", 1, 0)])["tier"], 2)

    def test_github_workflow(self):
        out = tier("fix: x", [(".github/workflows/a.yml", 1, 0)])
        self.assertEqual(out["tier"], 2)
        self.assertTrue(any(".github/workflows/a.yml" in r for r in out["reasons"]))

    def test_nested_migration_and_protected(self):
        self.assertEqual(tier("fix: x", [("app/db/migrations/0001.sql", 1, 0)])["tier"], 2)
        self.assertEqual(tier("fix: x", [("pkg/conftest.py", 1, 0)])["tier"], 2)

    def test_reasons_one_each(self):
        out = tier("ci!: x", [(f"src/f{i}.py", 60, 0) for i in range(21)] + [("Dockerfile", 1, 0)])
        self.assertEqual(out["tier"], 2)
        self.assertEqual(len(out["reasons"]), 5, out["reasons"])

    def test_bad_input(self):
        r = subprocess.run([sys.executable, str(TIER)], input="not json", capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
