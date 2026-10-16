"""records.ensure: clone engineer-records from the broker's mirror when it has the branch, else start one."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "engineer" / "scripts"))

from supervisor import records  # noqa: E402


def git(*args, cwd=None):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


class RecordsTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)
        self.records_dir = self.tmp / "var/lib/engineer/records"
        self.mirrors = self.tmp / "var/lib/engineer/mirrors"
        self.records_dir.mkdir(parents=True)
        self.mirror = self.mirrors / "demo.git"
        git("init", "-q", "--bare", str(self.mirror))
        seed = self.tmp / "seed"
        git("init", "-q", "-b", "main", str(seed))
        for k, v in (("user.name", "t"), ("user.email", "t@example.invalid")):
            git("config", k, v, cwd=seed)
        (seed / "README.md").write_text("demo\n")
        git("add", "README.md", cwd=seed)
        git("commit", "-qm", "init", cwd=seed)
        git("push", "-q", str(self.mirror), "main", cwd=seed)
        self.seed = seed

    def add_records_branch(self):
        git("checkout", "-q", "-b", records.BRANCH, cwd=self.seed)
        (self.seed / "audit").mkdir()
        (self.seed / "audit" / "AUDIT-t0.md").write_text("earlier night\n")
        git("add", "audit", cwd=self.seed)
        git("commit", "-qm", "docs: earlier audit", cwd=self.seed)
        git("push", "-q", str(self.mirror), records.BRANCH, cwd=self.seed)
        return git("rev-parse", "HEAD", cwd=self.seed)

    def test_ensure_clones_records_branch_from_mirror(self):
        sha = self.add_records_branch()
        clone = records.ensure(self.records_dir, "demo", mirror_dir=self.mirrors)
        self.assertEqual(git("rev-parse", "HEAD", cwd=clone), sha)
        self.assertEqual(git("symbolic-ref", "--short", "HEAD", cwd=clone), records.BRANCH)
        self.assertTrue((clone / "audit" / "AUDIT-t0.md").exists())
        hooks = clone / ".git" / "hooks"
        self.assertFalse(hooks.is_dir() and any(hooks.iterdir()), "clone has hook files")
        self.assertEqual(git("config", "--get", "core.hooksPath", cwd=clone), "/dev/null")

    def test_write_after_clone_extends_history(self):
        sha = self.add_records_branch()
        pushed = []
        self.assertTrue(records.write_and_push(self.records_dir, "demo", "audit/AUDIT-t1.md", "x\n", "docs: t1",
                                               pushed.append, mirror_dir=self.mirrors))
        clone = self.records_dir / "demo"
        self.assertEqual(git("rev-parse", "HEAD~1", cwd=clone), sha)
        self.assertEqual(pushed, [["push-branch", str(clone), records.BRANCH]])

    def test_default_mirror_dir_is_beside_records_dir(self):
        sha = self.add_records_branch()
        clone = records.ensure(self.records_dir, "demo")
        self.assertEqual(git("rev-parse", "HEAD", cwd=clone), sha)

    def test_ensure_inits_when_mirror_has_no_records_branch(self):
        clone = records.ensure(self.records_dir, "demo", mirror_dir=self.mirrors)
        self.assertEqual(git("symbolic-ref", "--short", "HEAD", cwd=clone), records.BRANCH)
        self.assertEqual(subprocess.run(["git", "-C", str(clone), "rev-parse", "-q", "--verify", "HEAD"],
                                        capture_output=True).returncode, 1)

    def test_ensure_inits_when_no_mirror(self):
        clone = records.ensure(self.records_dir, "demo", mirror_dir=self.tmp / "nope")
        self.assertEqual(git("symbolic-ref", "--short", "HEAD", cwd=clone), records.BRANCH)

    def test_existing_clone_kept(self):
        clone = records.ensure(self.records_dir, "demo", mirror_dir=self.mirrors)
        (clone / "keep.txt").write_text("k\n")
        self.add_records_branch()
        self.assertEqual(records.ensure(self.records_dir, "demo", mirror_dir=self.mirrors), clone)
        self.assertTrue((clone / "keep.txt").exists())

    def test_mirror_symlink_refused(self):
        self.add_records_branch()
        link = self.tmp / "links"
        link.mkdir()
        (link / "demo.git").symlink_to(self.mirror)
        with self.assertRaises(ValueError):
            records.ensure(self.records_dir, "demo", mirror_dir=link)


if __name__ == "__main__":
    unittest.main()
