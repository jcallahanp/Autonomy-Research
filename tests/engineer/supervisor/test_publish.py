"""A PASS publishes exactly the audited sha: push-branch --expect, then open-pr, then automerge pinned to it.

End to end through the real agent-run and broker jobs against a local bare "GitHub" (GITHUB_URL=file://...),
with a loopback `gh` stub that answers `pr view` from that bare repo. RUN_TASK and AUDIT_CMD are stubs.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tests" / "engineer"))
sys.path.insert(0, str(REPO / "engineer" / "scripts"))

import testlib  # noqa: E402
import yaml  # noqa: E402
from eng import conf as engconf  # noqa: E402
from supervisor import events, steps  # noqa: E402

NOW = datetime(2026, 10, 16, 7, 0, tzinfo=timezone.utc)
RUN_TASK = 'cat "__D__/rt/$3.json"'
AUDIT = 'cat "__D__/rt/audit.json"'
GH = r'''[ "${GH_TOKEN:-}" = TEST-TOKEN-PAT ] || exit 9
case "$1 $2" in
  'pr create') cat > /dev/null; echo https://github.com/owner/demo/pull/7 ;;
  'pr view') h=$(git --git-dir="__REMOTE__" rev-parse refs/heads/task/t1)
    printf '{"title": "feat: task t1", "headRefOid": "%s", "reviews": [], "state": "OPEN", "mergeCommit": null,
      "autoMergeRequest": null, "files": [{"path": "src/a.py", "additions": 1, "deletions": 0}]}\n' "$h" ;;
  'pr merge') echo merged ;;
  *) exit 5 ;;
esac'''


class PublishTest(unittest.TestCase):
    def setUp(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        self.tmp = Path(td.name).resolve()
        self.root = testlib.make_root(self.tmp)
        conf_file = self.root / "etc" / "engineer.conf"
        conf_file.write_text(conf_file.read_text().replace('GITHUB_URL="https://github.com"',
                                                           f'GITHUB_URL="file://{self.tmp}/remotes"'))
        self.conf = engconf.load(self.root)
        for name in ("sops", "gh"):
            body = (REPO / "tests/engineer/broker/sops-stub.sh").read_text() if name == "sops" else GH
            testlib.stub(self.root, name, body.replace("__REMOTE__", str(self.tmp / "remotes/owner/demo.git")))
        for key, text in (("SECRETS_FILE", '{"GH_BOT_PAT": "TEST-TOKEN-PAT"}\n'),
                          ("AGE_RECIPIENT_FILE", "age1testrecipientnotarealkey\n"), ("AGE_KEY_FILE", "")):
            Path(self.conf[key]).parent.mkdir(parents=True, exist_ok=True)
            Path(self.conf[key]).write_text(text)
        (Path(self.conf["ETC_DIR"]) / "projects.txt").write_text(
            "demo owner/demo main self_merge=on scratch=yes owner_login=john-test\n")
        gitcfg = self.tmp / "gitconfig"
        for k, v in (("user.name", "Test Bot"), ("user.email", "test@example.invalid"), ("safe.directory", "*"),
                     ("init.defaultBranch", "main"), ("commit.gpgsign", "false")):
            subprocess.run(["git", "config", "--file", str(gitcfg), k, v], check=True)
        env = {"GIT_CONFIG_GLOBAL": str(gitcfg), "GIT_CONFIG_NOSYSTEM": "1", "SUDO_USER": "supervisor"}
        patcher = mock.patch.dict(os.environ, env)
        patcher.start()
        self.addCleanup(patcher.stop)
        # GitHub: main only. The engineer clone: task/t1 one commit ahead.
        self.remote = self.tmp / "remotes/owner/demo.git"
        self.git(self.tmp, "init", "-q", "--bare", str(self.remote))
        self.clone = Path(self.conf["PROJECTS_DIR"]) / "demo"
        self.git(self.tmp, "init", "-q", str(self.clone))
        (self.clone / "README.md").write_text("demo\n")
        self.git(self.clone, "add", "-A")
        self.git(self.clone, "commit", "-qm", "chore: init")
        self.git(self.clone, "push", "-q", str(self.remote), "main")
        self.git(self.clone, "checkout", "-qb", "task/t1")
        (self.clone / "src").mkdir()
        (self.clone / "src/a.py").write_text("A = 1\n")
        self.git(self.clone, "add", "-A")
        self.git(self.clone, "commit", "-qm", "feat: task t1")
        self.sha = self.git(self.clone, "rev-parse", "HEAD")
        rt = self.tmp / "rt"
        rt.mkdir()
        for name, doc in (("implementer", {"exit_code": 0, "is_error": False, "head_sha": self.sha}),
                          ("check", {"exit_code": 0, "is_error": False, "head_sha": self.sha}),
                          ("auditor", {"exit_code": 0, "is_error": False, "structured_output":
                                       {"verdict": "PASS", "head_sha": self.sha, "lines": ["auditor PASS"]}}),
                          ("audit", {"verdict": "PASS", "head_sha": self.sha, "lines": ["audit PASS"]})):
            (rt / f"{name}.json").write_text(json.dumps(doc) + "\n")
        testlib.stub(self.root, "run-task", RUN_TASK.replace("__D__", str(self.tmp)))
        testlib.stub(self.root, "scripts/checks/audit.sh", AUDIT.replace("__D__", str(self.tmp)))
        defaults = yaml.safe_load((self.root / "templates" / "run-defaults.yaml").read_text())
        self.ctx = steps.Ctx(self.root, self.conf, defaults, {"name": "demo", "repo": "owner/demo", "branch": "main"},
                             NOW)
        self.ctx.push = mock.Mock(return_value=True)  # the records clone is records.py's (tested there)

    def git(self, cwd, *args):
        return subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True,
                              text=True).stdout.strip()

    def remote_sha(self, ref):
        p = subprocess.run(["git", "--git-dir", str(self.remote), "rev-parse", "-q", "--verify", ref],
                           capture_output=True, text=True)
        return p.stdout.strip() or None

    def task(self):
        return {"id": "t1", "title": "task t1", "type": "feat", "status": "todo", "depends_on": [],
                "requirement_ids": [], "files": [], "check": "true", "passes": False, "attempts": 0}

    def evs(self, kind):
        return [e for e in events.read(self.ctx.events) if e["event"] == kind]

    def test_pass_pushes_audited_sha_then_opens_pr(self):
        res = steps.attempt(self.ctx, self.task())
        self.assertEqual(res, {"status": "in_review"})
        self.assertEqual(self.remote_sha("refs/heads/task/t1"), self.sha)
        argv = testlib.argv_log(self.root)
        order = [next(i for i, a in enumerate(argv) if a.startswith(want)) for want in (
            "run-task demo t1 check --sha " + self.sha, "audit.sh demo t1", "run-task demo t1 auditor",
            "gh pr create --repo owner/demo --head task/t1",
            f"gh pr merge 7 --auto --squash --repo owner/demo --match-head-commit {self.sha}")]
        self.assertEqual(order, sorted(order), argv)
        jobs = [line.split()[2:4] for line in (Path(self.conf["BROKER_STATE_DIR"]) / "agent-run.log").read_text()
                .splitlines()]
        self.assertEqual([j for j, _ in jobs if j != "sync-mirror"], ["push-branch", "open-pr", "automerge"], jobs)
        self.assertEqual({rc for _, rc in jobs}, {"0"}, jobs)
        audit = self.evs("audit")[-1]
        self.assertEqual((audit["head_sha"], audit["detail"]["audited_sha"], audit["detail"]["status"]),
                         (self.sha, self.sha, "in_review"))
        self.assertEqual(self.evs("pr_open")[-1]["head_sha"], self.sha)
        self.assertTrue(self.evs("merge")[-1]["detail"]["auto_merge"])
        self.assertEqual(events.state(events.read(self.ctx.events))["in_review"], {"t1"})

    def test_head_moved_after_audit_is_not_pushed(self):
        (self.clone / "src/b.py").write_text("B = 2\n")  # the engineer commits after the audit passed
        self.git(self.clone, "add", "-A")
        self.git(self.clone, "commit", "-qm", "feat: sneak")
        res = steps.attempt(self.ctx, self.task())
        self.assertEqual(res, {"status": "needs_john"})
        self.assertIsNone(self.remote_sha("refs/heads/task/t1"))
        self.assertFalse([a for a in testlib.argv_log(self.root) if a.startswith(("agent-run open-pr", "gh pr"))])
        self.assertIn("push", self.evs("audit")[-1]["detail"]["reason"])


if __name__ == "__main__":
    unittest.main()
