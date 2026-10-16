"""Shared fixture for the hook tests: a make_root copy, a temp git project and a hook runner.

Each test pipes the JSON Claude Code sends on stdin into a hook script of the copy and checks the
exit code and output (contract: https://code.claude.com/docs/en/hooks). Claude Code is never run.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import testlib  # noqa: E402
from eng import conf as engconf  # noqa: E402

GIT_ENV = {"GIT_AUTHOR_NAME": "Test", "GIT_AUTHOR_EMAIL": "test@example.invalid",
           "GIT_COMMITTER_NAME": "Test", "GIT_COMMITTER_EMAIL": "test@example.invalid",
           "GIT_CONFIG_NOSYSTEM": "1"}


def git(cwd, *args, env=None):
    return subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True,
                          text=True, env=env).stdout


class HookCase(unittest.TestCase):
    """One make_root copy per test class; per test, fresh state dirs, HOME and project.

    self.tmp, self.root, self.conf, self.home, self.env, self.proj (git repo on main, one commit).
    A test that changes a file inside self.root must restore it (addCleanup).
    """
    STATE_KEYS = ("STATE_DIR", "PROJECTS_DIR", "ETC_DIR", "BROKER_STATE_DIR")

    @classmethod
    def setUpClass(cls):
        cls._td = tempfile.TemporaryDirectory()
        cls.tmp = Path(cls._td.name).resolve()
        cls.root = testlib.make_root(cls.tmp)
        cls.conf = engconf.load(cls.root)
        cls.home = cls.tmp / "userhome"
        cls.env = {k: v for k, v in os.environ.items() if not k.startswith(("ENGINEER_", "GIT_"))}
        cls.env.update(GIT_ENV, HOME=str(cls.home), PYTHONDONTWRITEBYTECODE="1")
        cls.template = cls.make_project(cls.tmp / "template" / "demo")

    @classmethod
    def tearDownClass(cls):
        cls._td.cleanup()

    def setUp(self):
        for key in self.STATE_KEYS:
            shutil.rmtree(self.conf[key], ignore_errors=True)
        shutil.rmtree(self.home, ignore_errors=True)
        for key in self.STATE_KEYS + ("SPOOL_DIR", "RECORDS_DIR"):
            Path(self.conf[key]).mkdir(parents=True, exist_ok=True)
        self.home.mkdir()
        self.proj = Path(self.conf["PROJECTS_DIR"]) / "demo"
        shutil.copytree(self.template, self.proj, symlinks=True)

    @classmethod
    def make_project(cls, path: Path) -> Path:
        path.mkdir(parents=True)
        git(path, "init", "-q", "-b", "main", env=cls.env)
        cls.write(path / "README.md", "demo\n")
        cls.write(path / "tests/unit/test_old.py", "def test_x():\n    pass\n")
        cls.write(path / "tests/acceptance/a.py", "# acceptance\n")
        cls.write(path / "src/a.py", "A = 1\n")
        cls.commit(path, "init")
        return path

    @classmethod
    def commit(cls, path, msg):
        git(path, "add", "-A", env=cls.env)
        git(path, "commit", "-q", "-m", msg, env=cls.env)

    @staticmethod
    def write(path: Path, text: str) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def run_hook(self, script, event, env=None, raw=None, cwd=None):
        full_env = dict(self.env, **(env or {}))
        data = raw if raw is not None else json.dumps(event)
        return subprocess.run(["python3", "-I", str(self.root / "plugin" / "hooks" / script)],
                              input=data, capture_output=True, text=True, env=full_env,
                              cwd=str(cwd or self.proj), timeout=60)

    def event(self, tool_name, tool_input, cwd=None, name="PreToolUse"):
        return {"session_id": "sess-1", "transcript_path": str(self.tmp / "t.jsonl"),
                "cwd": str(cwd or self.proj), "permission_mode": "auto", "hook_event_name": name,
                "tool_name": tool_name, "tool_input": tool_input, "tool_use_id": "toolu_1"}

    def pre(self, tool_name, tool_input, cwd=None, env=None):
        return self.run_hook("pre_tool_use.py", self.event(tool_name, tool_input, cwd), env=env)

    def bash(self, command, cwd=None, env=None):
        return self.pre("Bash", {"command": command, "description": "test"}, cwd=cwd, env=env)

    def many(self, fn, items):
        """[(item, result)] of fn(item) for each item, run in parallel (each is its own hook process)."""
        with ThreadPoolExecutor(max_workers=os.cpu_count() or 2) as pool:
            return list(zip(items, pool.map(fn, items)))

    def assertDenied(self, r, contains=None, msg=None):
        self.assertEqual(r.returncode, 2, msg or f"expected deny; stdout={r.stdout!r} stderr={r.stderr!r}")
        if contains:
            self.assertIn(contains, r.stderr, msg)

    def assertAllowed(self, r, msg=None):
        self.assertEqual(r.returncode, 0, msg or f"expected allow; stderr={r.stderr!r}")
