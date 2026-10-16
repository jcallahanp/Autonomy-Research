"""secret-scan.py: finds secret-shaped text in files or added diff lines, never prints the match."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from gitfix import Repo

REPO = Path(__file__).resolve().parents[3]
SCAN = REPO / "engineer" / "scripts" / "checks" / "secret-scan.py"
# Built at runtime so no file holds a secret-shaped string; visibly fake.
FAKE_GH = "gh" + "p_" + "TESTTOKEN" + "0" * 27
FAKE_SK = "s" + "k-" + "TESTTOKEN" + "1" * 20
FAKE_BEARER = "Bear" + "er " + "TEST.TOKEN-" + "2" * 20


def scan(*args):
    return subprocess.run([sys.executable, str(SCAN), *args], capture_output=True, text=True)


class FileModeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_positive(self):
        f = self.dir / "a.env"
        f.write_text(f"OK=1\nGH={FAKE_GH}\nX={FAKE_SK}\nH: {FAKE_BEARER}\n")
        r = scan(str(f))
        self.assertEqual(r.returncode, 1)
        self.assertIn(f"{f}:2 github_token", r.stdout)
        self.assertIn(f"{f}:3 sk_key", r.stdout)
        self.assertIn(f"{f}:4 bearer", r.stdout)
        for value in (FAKE_GH, FAKE_SK, FAKE_BEARER, "TESTTOKEN"):
            self.assertNotIn(value, r.stdout + r.stderr)

    def test_negative(self):
        f = self.dir / "a.py"
        f.write_text("token = os.environ['GH_BOT_PAT']\nheader = 'Bearer ' + token\n")
        r = scan(str(f))
        self.assertEqual((r.returncode, r.stdout), (0, ""), r.stderr)

    def test_engineer_tree_is_clean(self):
        r = scan(*[str(p) for p in (REPO / "engineer" / "scripts" / "checks").glob("*.py")])
        self.assertEqual(r.returncode, 0, r.stdout)


class DiffModeTest(unittest.TestCase):
    def test_only_added_lines(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Repo(Path(tmp) / "p")
            base = repo.commit({"old.txt": f"{FAKE_GH}\n", "a.txt": "one\n"})
            head = repo.commit({"a.txt": f"one\ntwo\nkey={FAKE_SK}\n"})
            r = scan("--diff", repo.gitdir, base, head)
            self.assertEqual(r.returncode, 1)
            self.assertEqual(r.stdout.strip(), "a.txt:3 sk_key [REDACTED]")
            clean = repo.commit({"b.txt": "nothing here\n"})
            r = scan("--diff", repo.gitdir, head, clean)
            self.assertEqual((r.returncode, r.stdout), (0, ""), r.stderr)


if __name__ == "__main__":
    unittest.main()
