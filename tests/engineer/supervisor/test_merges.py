"""merges.pass_open_prs: an in_review task is done only once the broker mirror's default branch has its merge."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tests" / "engineer"))
sys.path.insert(0, str(REPO / "engineer" / "scripts"))

import testlib  # noqa: E402
from eng import conf as engconf  # noqa: E402
from approvals import items  # noqa: E402
from supervisor import dag, events, merges  # noqa: E402

NOW = datetime(2026, 10, 16, 7, 0, tzinfo=timezone.utc)
GIT_ENV = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@example.invalid", "GIT_CONFIG_NOSYSTEM": "1"}
AGENT_RUN = r'''d=__D__
case "$1" in
  automerge) cat "$d/automerge.json"; exit "$(cat "$d/automerge.rc" 2>/dev/null || echo 0)" ;;
esac'''


def git(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True, text=True,
                          env=GIT_ENV).stdout.strip()


def task(tid, deps=()):
    return {"id": tid, "title": tid, "type": "feat", "status": "todo", "depends_on": list(deps),
            "requirement_ids": [], "files": [], "check": "true", "passes": False, "attempts": 0}


class MergesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """GitHub's default branch (a bare mirror) and a work repo whose task/t1 holds the audited commit;
        built once, copied per test."""
        cls._td = tempfile.TemporaryDirectory()
        src = Path(cls._td.name)
        work = src / "work"
        git(src, "init", "-q", "-b", "main", str(work))
        (work / "a.txt").write_text("a\n")
        git(work, "add", "-A")
        git(work, "commit", "-qm", "base")
        git(work, "checkout", "-qb", "task/t1")
        (work / "b.txt").write_text("b\n")
        git(work, "add", "-A")
        git(work, "commit", "-qm", "feat: t1")
        cls.sha = git(work, "rev-parse", "HEAD")
        git(work, "checkout", "-q", "main")
        git(src, "clone", "-q", "--bare", str(work), str(src / "mirror.git"))
        cls.src = src

    @classmethod
    def tearDownClass(cls):
        cls._td.cleanup()

    def setUp(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        self.tmp = Path(td.name)
        self.root = testlib.make_root(self.tmp)
        self.conf = engconf.load(self.root)
        (Path(self.conf["ETC_DIR"]) / "projects.txt").write_text(
            "demo o/demo main self_merge=on scratch=yes owner_login=john-test\n")
        testlib.stub(self.root, "agent-run", AGENT_RUN.replace("__D__", repr(str(self.tmp))))
        self.automerge({"tier": 2, "auto_merge": False, "reasons": ["auth/**"]}, rc=3)
        self.work = self.tmp / "work"
        shutil.copytree(self.src / "work", self.work, symlinks=True)
        self.mirror = Path(self.conf["MIRROR_DIR"]) / "demo.git"
        shutil.copytree(self.src / "mirror.git", self.mirror, symlinks=True)
        self.events = Path(self.conf["STATE_DIR"]) / "demo" / "events.jsonl"
        for kind, detail in (("audit", {"verdict": "PASS", "status": "in_review", "audited_sha": self.sha}),
                             ("pr_open", {"number": 7, "url": "https://github.com/o/demo/pull/7"})):
            events.append(self.events, {"project": "demo", "event": kind, "task_id": "t1", "head_sha": self.sha,
                                        "detail": detail})

    def automerge(self, doc, rc=0):
        (self.tmp / "automerge.json").write_text(json.dumps(doc))
        (self.tmp / "automerge.rc").write_text(str(rc))

    def mirror_main(self, ref):
        """GitHub's main moves to ref (a commit in the work repo); the broker mirror fetches it."""
        git(self.work, "push", "-q", str(self.mirror), f"{ref}:refs/heads/main")

    def state(self):
        return events.state(events.read(self.events))

    def calls(self, job):
        return [a for a in testlib.argv_log(self.root) if a.startswith(f"agent-run {job}")]

    def test_merged_when_mirror_default_contains_audited_sha(self):
        self.mirror_main(self.sha)  # merge commit / fast-forward: the audited sha itself is on main
        out = merges.pass_open_prs(self.conf, "demo", NOW)
        self.assertEqual([(e["event"], e["detail"]["merged"]) for e in out], [("merge", True)])
        self.assertEqual((self.state()["done"], self.state()["in_review"]), ({"t1"}, set()))
        self.assertTrue(self.calls("sync-mirror demo"))
        self.assertFalse(self.calls("automerge"))
        self.assertEqual(merges.pass_open_prs(self.conf, "demo", NOW), [])

    def test_squash_merge_counts_once_mirror_has_the_merge_commit(self):
        git(self.work, "checkout", "-q", "main")
        (self.work / "b.txt").write_text("b\n")
        git(self.work, "add", "-A")
        git(self.work, "commit", "-qm", "feat: t1 (#7)")
        squash = git(self.work, "rev-parse", "HEAD")
        self.automerge({"merged": True, "head": self.sha, "merge_commit": squash})
        self.assertEqual(merges.pass_open_prs(self.conf, "demo", NOW), [])  # GitHub says merged; mirror lacks it
        self.assertEqual(self.state()["done"], set())
        self.mirror_main(squash)
        out = merges.pass_open_prs(self.conf, "demo", NOW)
        self.assertEqual(out[0]["detail"]["merge_commit"], squash)
        self.assertEqual(self.state()["done"], {"t1"})

    def test_merged_at_unaudited_head_needs_john_once(self):
        self.mirror_main("main")
        self.automerge({"merged": True, "head": "f" * 40, "merge_commit": git(self.work, "rev-parse", "main"),
                        "merged_by": "someone-else"})
        out = merges.pass_open_prs(self.conf, "demo", NOW)
        self.assertEqual([(e["event"], e["detail"]["status"]) for e in out], [("audit", "needs_john")])
        self.assertIn("unaudited", out[0]["detail"]["reason"])
        self.assertEqual((self.state()["needs_john"], self.state()["done"]), ({"t1"}, set()))
        n = len(self.calls("automerge"))
        self.assertEqual(merges.pass_open_prs(self.conf, "demo", NOW), [])  # raised once, not every pass
        self.assertEqual(len(self.calls("automerge")), n)

    def test_merge_john_made_himself_counts_done_with_a_note(self):
        main = git(self.work, "rev-parse", "main")
        self.mirror_main("main")
        self.automerge({"merged": True, "head": "f" * 40, "merge_commit": main, "merged_by": "john-test"})
        out = merges.pass_open_prs(self.conf, "demo", NOW)
        self.assertEqual([(e["event"], e["detail"].get("merged")) for e in out], [("merge", True)])
        self.assertIn("john-test", out[0]["detail"]["note"])
        self.assertIn("not the audited", out[0]["detail"]["note"])
        self.assertEqual(self.state()["done"], {"t1"})

    def test_head_moved_needs_john_once(self):
        self.automerge({"tier": None, "auto_merge": False,
                        "reasons": ["head moved: GitHub has ffffffffffff, the audit passed 0123456789ab"]}, rc=65)
        out = merges.pass_open_prs(self.conf, "demo", NOW)
        self.assertEqual([(e["event"], e["detail"]["status"]) for e in out], [("audit", "needs_john")])
        self.assertIn("head moved", out[0]["detail"]["reason"])
        self.assertEqual(merges.pass_open_prs(self.conf, "demo", NOW), [])
        self.assertEqual(len(self.calls("automerge")), 1)

    def test_merge_closes_the_open_merge_ask(self):
        for n, kind in ((3, "merge"), (4, "other")):
            events.append(self.events, {"project": "demo", "event": "approval_ask", "task_id": "t1", "detail": {
                "item": n, "tier": "T1", "kind": kind, "text": f"ask {n}", "default": "n", "reversible": True,
                "ref": "https://github.com/o/demo/pull/7"}})
        self.mirror_main(self.sha)
        out = merges.pass_open_prs(self.conf, "demo", NOW)
        ans = [e for e in out if e["event"] == "approval_answer"]
        self.assertEqual([(e["detail"]["item"], e["detail"]["answer"], e["detail"]["by"]) for e in ans],
                         [(3, "merged", "system")])
        records = Path(self.conf["RECORDS_DIR"]) / "demo" / "decisions" / "approvals.jsonl"
        recs = items.answers(self.events, records)
        self.assertEqual([(r["item"], r["answer"], r["source"]) for r in recs], [("3", "yes", "pr")])
        self.assertEqual(sorted(items.open_items(items.read_jsonl(self.events), recs, "2026-10-16T08:00:00Z")), [4])

    def test_tier2_approval_runs_automerge_with_audited_sha(self):
        self.assertEqual(merges.pass_open_prs(self.conf, "demo", NOW), [])  # no approving review yet
        self.assertIn(f"agent-run automerge demo 7 {self.sha}", self.calls("automerge"))
        self.automerge({"tier": 2, "auto_merge": True})  # John approved commit sha on GitHub
        out = merges.pass_open_prs(self.conf, "demo", NOW)
        self.assertEqual([(e["event"], e["detail"].get("auto_merge")) for e in out], [("merge", True)])
        self.assertEqual(out[0]["head_sha"], self.sha)
        self.assertEqual(self.state()["in_review"], {"t1"})  # auto-merge on is not merged
        self.automerge({"tier": None, "auto_merge": True, "already": True})
        self.assertEqual(merges.pass_open_prs(self.conf, "demo", NOW), [])

    def test_closed_pr_needs_john(self):
        self.automerge({"closed": True, "auto_merge": False, "reasons": ["the PR is closed without merging"]}, rc=3)
        out = merges.pass_open_prs(self.conf, "demo", NOW)
        self.assertEqual(out[0]["detail"]["status"], "needs_john")
        self.assertEqual(self.state()["needs_john"], {"t1"})

    def test_no_open_pr_no_calls(self):
        self.events.unlink()
        self.assertEqual(merges.pass_open_prs(self.conf, "demo", NOW), [])
        self.assertEqual(testlib.argv_log(self.root), [])

    def test_dependents_ready_only_after_merged(self):
        tasks = [task("t1"), task("t2", ["t1"])]
        st = self.state()
        self.assertEqual(dag.ready(tasks, st["done"], st["in_review"], st["running"]), [])
        self.mirror_main(self.sha)
        merges.pass_open_prs(self.conf, "demo", NOW)
        st = self.state()
        self.assertEqual(dag.ready(tasks, st["done"], st["in_review"], st["running"]), ["t2"])


if __name__ == "__main__":
    unittest.main()
