"""Git guard: push and history/config rewrites in every spelling (Review Focus 5)."""
import unittest

from hookfix import HookCase

DENIED = (
    "git push", "git push origin main", "git -C . push origin x", "/usr/bin/git push",
    "git --git-dir=.git push", "git --git-dir .git push", "git -c user.name=x push",
    "env git push", "env -i PATH=/usr/bin git push", "command git push", "exec git push",
    "sudo -u engineer git push", "timeout 30 git push", "nohup git push &", "xargs git push",
    "bash -c \"git push\"", "sh -c 'cd x && git push'", "bash -lc 'git push'", "zsh -c 'git push'",
    "eval 'git push'", "echo $(git push)", "echo \"$(git push)\"", "echo `git push`", "(git push)",
    "{ git push; }", "true; git push", "false || git push", "true && git push", "ls | git push",
    "ls\ngit push", "GIT_DIR=.git git push", "git -C ../other push", "/usr/lib/git-core/git-push",
    "git-push origin", "git send-pack x", "git filter-branch --all", "git filter-repo --force",
    "git update-ref refs/heads/main HEAD", "git reflog expire --all", "git remote add x y",
    "git remote set-url origin x", "git config core.hooksPath /tmp", "git config core.fsmonitor x",
    "git config --local core.sshCommand x", "git config credential.helper store",
    "git config http.extraHeader x", "git config --global Core.HooksPath /tmp",
    "git config set core.hooksPath /tmp", "git config alias.p push", "git config include.path x",
    "git config -e", "git -c core.hooksPath=/tmp commit -m x", "git -c alias.x=push x",
    "git --config-env=core.hooksPath=V commit", "GIT_CONFIG_PARAMETERS=x git commit -m y",
    "GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.hooksPath GIT_CONFIG_VALUE_0=/t git commit",
    "export GIT_CONFIG_PARAMETERS=x", "GIT_SSH_COMMAND=x git fetch",
    "git branch -D old", "git branch --delete --force old", "git branch -df old",
    "git tag -d v1", "git tag --delete v1", "ls | tee >(git push)", "diff <(git push) x",
    "$'git' push", "\"git\" push", "g\\it push", "git\tpush", "git -C. push",
)

ALLOWED = (
    "git status", "git commit -m x", "git diff", "git diff --stat HEAD~1", "git log --grep push",
    "git commit -m \"docs: explain git push policy\"", "git checkout -b fix-git-push",
    "git checkout git-push", "git add -A && git commit -m 'wip'", "git branch -d merged",
    "git branch feature", "git tag v1", "git config user.name x", "git config --get core.hooksPath",
    "git fetch origin", "git -C sub status", "git stash", "grep -rn 'git push' docs/",
    "git commit -m \"$(cat <<'EOF'\nfeat: don't push\nEOF\n)\"",
)


class GitGuardTest(HookCase):
    def test_git_push_variants(self):
        for cmd, r in self.many(self.bash, DENIED):
            with self.subTest(cmd=cmd):
                self.assertDenied(r, "git")

    def test_git_allowed(self):
        for cmd, r in self.many(self.bash, ALLOWED):
            with self.subTest(cmd=cmd):
                self.assertAllowed(r)

    def test_git_reason_names_subcommand(self):
        self.assertDenied(self.bash("git -C . push origin x"), "push")


if __name__ == "__main__":
    unittest.main()
