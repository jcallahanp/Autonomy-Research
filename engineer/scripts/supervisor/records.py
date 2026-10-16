"""The supervisor-owned records clone per project (RECORDS_DIR/<p>, branch engineer-records).

The supervisor writes audit/AUDIT-<id>.md, docs/runs/<date>-MORNING.md and decisions/approvals.jsonl
here, commits as the bot and pushes through the broker (`AGENT_RUN push-branch <clone> engineer-records`).
engineer never writes this clone, so git may run in it; repo hooks and fsmonitor are still switched off.

The clone is made from the broker's bare mirror MIRROR_DIR/<p>.git (sync-mirror keeps engineer-records
there once it exists on GitHub), so a new clone carries on the published history; a fresh engineer-records
is started only when the mirror has no such branch (or no mirror has been synced yet).
"""
import os
import subprocess
import tempfile
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


def _mirror_git(mirror: Path, *args, cwd=None) -> subprocess.CompletedProcess:
    """git trusting the broker-owned mirror for one call; `-c` does not reach the upload-pack it starts."""
    with tempfile.TemporaryDirectory(prefix="records-git.") as tmp:
        cfg = Path(tmp) / "config"
        for key, value in (("safe.directory", str(mirror)), ("core.hooksPath", "/dev/null")):
            subprocess.run(["git", "config", "--file", str(cfg), key, value], check=True, capture_output=True)
        env = {**os.environ, "GIT_CONFIG_GLOBAL": str(cfg), "GIT_CONFIG_NOSYSTEM": "1", "GIT_TERMINAL_PROMPT": "0"}
        return subprocess.run(["git", *SAFE, "-c", "protocol.file.allow=always", *args], cwd=cwd,
                              capture_output=True, text=True, check=True, env=env)


def _mirror_has_branch(mirror: Path) -> bool:
    out = _mirror_git(mirror, "ls-remote", "--heads", f"file://{mirror}", f"refs/heads/{BRANCH}").stdout
    return any(line.split("\t")[-1] == f"refs/heads/{BRANCH}" for line in out.splitlines())


def ensure(records_dir, project: str, mirror_dir=None) -> Path:
    """Return the clone, cloning engineer-records from the mirror (default <records_dir>/../mirrors).

    Without the branch in the mirror (or without a mirror) it starts an empty repo on engineer-records.
    Raises ValueError for a symlinked mirror and CalledProcessError when git fails on an existing mirror.
    """
    clone = Path(records_dir) / project
    if not (clone / ".git").exists():
        mdir = Path(mirror_dir) if mirror_dir is not None else Path(records_dir).parent / "mirrors"
        mirror = mdir / f"{project}.git"
        if mdir.is_symlink() or mirror.is_symlink():
            raise ValueError(f"records mirror path is a symlink: {mirror}")
        if mirror.is_dir() and _mirror_has_branch(mirror):
            clone.parent.mkdir(parents=True, exist_ok=True)
            _mirror_git(mirror, "clone", "-q", "--template=", "--no-tags", "--single-branch", "--branch", BRANCH,
                        f"file://{mirror}", str(clone))
            _git(clone, "config", "core.hooksPath", "/dev/null")
        else:
            clone.mkdir(parents=True, exist_ok=True)
            _git(clone, "init", "-q", "-b", BRANCH)
    head = _git(clone, "symbolic-ref", "--short", "HEAD", check=False).stdout.strip()
    if head != BRANCH:
        if _git(clone, "checkout", "-q", BRANCH, check=False).returncode:
            _git(clone, "checkout", "-q", "-b", BRANCH)
    return clone


def write_and_push(records_dir, project: str, relpath: str, content: str, message: str, run,
                   email: str = "engineer-bot@users.noreply.github.com", mirror_dir=None) -> bool:
    """Write relpath in the records clone, commit as the bot, push via run(["push-branch", clone, BRANCH]).

    run is a callable taking the AGENT_RUN argument list. Returns True when a commit was made.
    """
    rel = _relpath(relpath)
    clone = ensure(records_dir, project, mirror_dir)
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
