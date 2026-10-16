"""plansnap: a plan ask binds to the plan PR's head commit read from the broker mirror, never the working tree."""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "engineer" / "scripts"))
from approvals import plansnap  # noqa: E402
from eng import approval  # noqa: E402

LINE = "Approve plan v2 for demo? PR https://github.com/o/demo/pull/3"


def git(*args, cwd=None):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


class PlanSnap(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)
        lib = self.tmp / "var/lib/engineer"
        self.conf = {"STATE_DIR": str(lib), "RECORDS_DIR": str(lib / "records"), "MIRROR_DIR": str(lib / "mirrors"),
                     "BOT_EMAIL": "engineer-bot@users.noreply.github.com"}
        self.mirror = lib / "mirrors" / "demo.git"
        git("init", "-q", "--bare", str(self.mirror))
        self.seed = self.tmp / "seed"
        git("init", "-q", "-b", "plan/v2", str(self.seed))
        for k, v in (("user.name", "t"), ("user.email", "t@example.invalid")):
            git("config", k, v, cwd=self.seed)
        self.sha = self.commit({rel: f"pr {rel}\n" for rel in approval.SIGNED})
        self.calls, self.moved = [], False

    def commit(self, files, link=None):
        for rel, body in files.items():
            (self.seed / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.seed / rel).write_text(body)
        if link:
            (self.seed / link).unlink()
            (self.seed / link).symlink_to("/etc/hostname")
        git("add", "-A", cwd=self.seed)
        git("commit", "-qm", "docs: plan", cwd=self.seed)
        sha = git("rev-parse", "HEAD", cwd=self.seed)
        git("push", "-q", "-f", str(self.mirror), f"{sha}:refs/pull/3/head", cwd=self.seed)
        return sha

    def broker(self, args):
        self.calls.append(list(args))
        out = ""
        if args[0] == "pr-head":
            out = json.dumps({"number": 3, "head_sha": self.sha, "state": "OPEN"})
        elif args[:3] == ["sync-mirror", "demo", "--pr"]:
            out = json.dumps({"pr": {"number": 3, "sha": "f" * 40 if self.moved else self.sha}})
        return subprocess.CompletedProcess(args, 0, out, "")

    def test_parse(self):
        self.assertEqual(plansnap.parse(LINE, "o/demo"), (2, 3, "https://github.com/o/demo/pull/3"))
        for bad in ("Approve plan v2 for demo? PR https://github.com/evil/demo/pull/3",
                    "Approve plan v2 for demo? no link", "Approve plan v0 for demo? PR https://github.com/o/demo/pull/3",
                    "Approve plan v2 for demo? PR https://github.com/o/demo/pull/3/files"):
            with self.assertRaises(plansnap.SnapError, msg=bad):
                plansnap.parse(bad, "o/demo")

    def test_working_tree_differs_from_pr_head_no_effect(self):
        work = self.tmp / "home/engineer/projects/demo"
        for rel in approval.SIGNED:
            (work / rel).parent.mkdir(parents=True, exist_ok=True)
            (work / rel).write_text("engineer's unpushed edit\n")
        d = plansnap.snapshot(self.conf, "demo", 2, 3, self.broker)
        want = {rel: hashlib.sha256(f"pr {rel}\n".encode()).hexdigest() for rel in approval.SIGNED}
        self.assertEqual((d["files"], d["sha"], d["version"], d["snapshot"]), (want, self.sha, 2, "approvals/demo/v2"))
        rec = Path(self.conf["RECORDS_DIR"]) / "demo"
        for rel in approval.SIGNED:
            self.assertEqual((rec / "approvals/demo/v2" / rel).read_text(), f"pr {rel}\n")
        snap = json.loads((rec / "approvals/demo/v2/SNAPSHOT.json").read_text())
        self.assertEqual((snap["sha"], snap["files"]), (self.sha, want))
        self.assertEqual(git("rev-parse", "HEAD", cwd=rec), d["records_sha"])
        self.assertIn(["push-branch", str(rec), "engineer-records"], self.calls)
        text = plansnap.text_for("o/demo", "https://github.com/o/demo/pull/3", d)
        self.assertTrue(text.startswith(f"Approve plan v2 @ {self.sha[:7]}? PR https://github.com/o/demo/pull/3; "
                                        f"signed files https://github.com/o/demo/tree/{d['records_sha']}/approvals/demo/v2"))
        self.assertIn(f"brief.md {want['docs/plan/brief.md'][:8]}", text)

    def test_pr_moved_while_reading_refused(self):
        self.moved = True
        with self.assertRaises(plansnap.SnapError):
            plansnap.snapshot(self.conf, "demo", 2, 3, self.broker)
        self.assertFalse((Path(self.conf["RECORDS_DIR"]) / "demo").exists())

    def test_symlink_in_pr_refused(self):
        self.sha = self.commit({}, link=approval.SIGNED[0])
        with self.assertRaises(plansnap.SnapError):
            plansnap.snapshot(self.conf, "demo", 2, 3, self.broker)

    def test_missing_signed_file_refused(self):
        git("rm", "-q", approval.SIGNED[1], cwd=self.seed)
        self.sha = self.commit({})
        with self.assertRaises(plansnap.SnapError):
            plansnap.snapshot(self.conf, "demo", 2, 3, self.broker)


if __name__ == "__main__":
    unittest.main()
