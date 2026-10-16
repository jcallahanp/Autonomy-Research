"""records.ensure: clone engineer-records from the broker's mirror when it has the branch, else start one."""
import json
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
        self.assertEqual(pushed, [["sync-mirror", "demo"], ["push-branch", str(clone), records.BRANCH]])

    def run_stub(self, sync_rc=0, sync_out="", push_rc=0, on_sync=None):
        calls = []

        def run(args):
            calls.append(list(args))
            if args[0] == "sync-mirror":
                if on_sync:
                    on_sync()
                return subprocess.CompletedProcess(args, sync_rc, sync_out, "sync failed" if sync_rc else "")
            return subprocess.CompletedProcess(args, push_rc, "", "push refused" if push_rc else "")
        run.calls = calls
        return run

    def test_fork_repro_syncs_mirror_before_first_clone(self):
        """No mirror copy of engineer-records yet, but GitHub has it: sync first, then clone, never init."""
        state = {}

        def github_has_records():
            state["sha"] = self.add_records_branch()
        run = self.run_stub(on_sync=github_has_records)
        clone = records.ensure(self.records_dir, "demo", mirror_dir=self.mirrors, run=run)
        self.assertEqual(run.calls[0], ["sync-mirror", "demo"])
        self.assertEqual(git("rev-parse", "HEAD", cwd=clone), state["sha"])

    def test_no_init_when_sync_reports_records_the_mirror_lacks(self):
        run = self.run_stub(sync_out=json.dumps({"project": "demo", "records": "ab" * 20}))
        with self.assertRaises(records.RecordsError):
            records.ensure(self.records_dir, "demo", mirror_dir=self.mirrors, run=run)
        self.assertFalse((self.records_dir / "demo").exists())

    def test_no_init_when_sync_fails(self):
        with self.assertRaises(records.RecordsError):
            records.ensure(self.records_dir, "demo", mirror_dir=self.mirrors, run=self.run_stub(sync_rc=1))
        self.assertFalse((self.records_dir / "demo").exists())

    def test_failed_clone_leaves_no_clone(self):
        self.add_records_branch()
        real = records._mirror_git

        def broken(mirror, *args, **kw):
            if "clone" in args:
                raise subprocess.CalledProcessError(128, ["git", "clone"])
            return real(mirror, *args, **kw)
        records._mirror_git = broken
        self.addCleanup(setattr, records, "_mirror_git", real)
        with self.assertRaises(records.RecordsError):
            records.ensure(self.records_dir, "demo", mirror_dir=self.mirrors)
        self.assertEqual([p.name for p in self.records_dir.iterdir()], [])

    def test_crash_loop_repro_broken_clone_moved_aside(self):
        """A crash mid-clone left records/demo/.git empty: every pass used to raise; now it is set aside."""
        sha = self.add_records_branch()
        (self.records_dir / "demo" / ".git").mkdir(parents=True)
        clone = records.ensure(self.records_dir, "demo", mirror_dir=self.mirrors)
        self.assertEqual(git("rev-parse", "HEAD", cwd=clone), sha)
        self.assertTrue([p for p in self.records_dir.iterdir() if p.name.startswith("demo.broken-")])
        self.assertEqual(records.ensure(self.records_dir, "demo", mirror_dir=self.mirrors), clone)

    def test_push_failure_recorded_not_raised_then_retried(self):
        self.add_records_branch()
        run = self.run_stub(push_rc=1)
        self.assertTrue(records.write_and_push(self.records_dir, "demo", "a.md", "x\n", "docs: a", run,
                                               mirror_dir=self.mirrors))
        self.assertIn("push-branch exited 1", records.failure(self.records_dir, "demo"))
        self.assertFalse(records.retry_push(self.records_dir, "demo", self.run_stub(push_rc=1)))
        self.assertTrue(records.retry_push(self.records_dir, "demo", self.run_stub()))
        self.assertIsNone(records.failure(self.records_dir, "demo"))

    def test_sync_failure_recorded_not_raised(self):
        self.assertFalse(records.write_and_push(self.records_dir, "demo", "a.md", "x\n", "docs: a",
                                                self.run_stub(sync_rc=1), mirror_dir=self.mirrors))
        self.assertIn("sync-mirror", records.failure(self.records_dir, "demo"))

    def test_write_files_returns_commit(self):
        out = records.write_files(self.records_dir, "demo", {"approvals/demo/v1/docs/plan/brief.md": b"b\n"},
                                  "records: plan v1", self.run_stub(), mirror_dir=self.mirrors)
        clone = self.records_dir / "demo"
        self.assertEqual((out["committed"], out["pushed"], out["sha"]),
                         (True, True, git("rev-parse", "HEAD", cwd=clone)))
        self.assertEqual((clone / "approvals/demo/v1/docs/plan/brief.md").read_bytes(), b"b\n")

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
