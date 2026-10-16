"""The supervisor-owned records clone per project (RECORDS_DIR/<p>, branch engineer-records).

The supervisor writes audit/AUDIT-<id>.md, docs/runs/<date>-MORNING.md and decisions/approvals.jsonl
here, commits as the bot and pushes through the broker (`AGENT_RUN push-branch <clone> engineer-records`).
engineer never writes this clone, so git may run in it; repo hooks and fsmonitor are still switched off.
"""
import os
import subprocess
from pathlib import Path, PurePosixPath

BRANCH = "engineer-records"
BOT_NAME = "engineer-bot"
SAFE = ["-c", "core.hooksPath=/dev/null", "-c", "core.fsmonitor=", "-c", "commit.gpgsign=false"]


def _git(clone: Path, *args, check=True) -> subprocess.CompletedProcess:
    env = {**os.environ, "GIT_CONFIG_NOSYSTEM": "1", "GIT_TERMINAL_PROMPT": "0"}
    return subprocess.run(["git", *SAFE, "-C", str(clone), *args], capture_output=True, text=True,
                          check=check, env=env)


def _relpath(relpath: str) -> PurePosixPath:
    rel = PurePosixPath(relpath)
    if rel.is_absolute() or ".." in rel.parts or not rel.parts or rel.parts[0] == ".git":
        raise ValueError(f"records path not allowed: {relpath!r}")
    return rel


def ensure(records_dir, project: str) -> Path:
    """Return the clone, creating an empty repo on engineer-records if setup has not cloned one yet."""
    clone = Path(records_dir) / project
    if not (clone / ".git").exists():
        clone.mkdir(parents=True, exist_ok=True)
        _git(clone, "init", "-q", "-b", BRANCH)
    head = _git(clone, "symbolic-ref", "--short", "HEAD", check=False).stdout.strip()
    if head != BRANCH:
        if _git(clone, "checkout", "-q", BRANCH, check=False).returncode:
            _git(clone, "checkout", "-q", "-b", BRANCH)
    return clone


def write_and_push(records_dir, project: str, relpath: str, content: str, message: str, run,
                   email: str = "engineer-bot@users.noreply.github.com") -> bool:
    """Write relpath in the records clone, commit as the bot, push via run(["push-branch", clone, BRANCH]).

    run is a callable taking the AGENT_RUN argument list. Returns True when a commit was made.
    """
    rel = _relpath(relpath)
    clone = ensure(records_dir, project)
    target = clone.joinpath(*rel.parts)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)
    _git(clone, "add", "--", str(rel))
    if _git(clone, "diff", "--cached", "--quiet", check=False).returncode == 0:
        return False
    _git(clone, "-c", f"user.name={BOT_NAME}", "-c", f"user.email={email}",
         "commit", "-q", "--no-verify", "-m", message)
    run(["push-branch", str(clone), BRANCH])
    return True
