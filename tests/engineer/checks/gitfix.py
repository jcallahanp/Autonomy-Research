"""Test helper: a throwaway git repo with commits (synthetic content only)."""
import os
import subprocess
from pathlib import Path

ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.invalid", GIT_COMMITTER_NAME="t",
           GIT_COMMITTER_EMAIL="t@example.invalid", GIT_CONFIG_NOSYSTEM="1")


class Repo:
    def __init__(self, path):
        self.path = Path(path)
        self.path.mkdir(parents=True, exist_ok=True)
        self.git("init", "-q", "-b", "main")

    def git(self, *args) -> str:
        return subprocess.run(["git", "-C", str(self.path), *args], env=ENV, check=True,
                              capture_output=True, text=True).stdout.strip()

    def write(self, rel, text):
        p = self.path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)

    def commit(self, files: dict = None, delete=(), msg="c") -> str:
        for rel, text in (files or {}).items():
            self.write(rel, text)
        for rel in delete:
            self.git("rm", "-q", rel)
        self.git("add", "-A")
        self.git("commit", "-q", "--allow-empty", "-m", msg)
        return self.git("rev-parse", "HEAD")

    @property
    def gitdir(self) -> str:
        return str(self.path / ".git")
