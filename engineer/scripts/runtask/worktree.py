"""run-task's git work, run as `engineer` inside its own clone (never by a privileged user).

Before a new task branch is made, the default branch is fetched over file:// from the broker-owned bare
mirror (`sync-mirror` keeps it at GitHub's head), so the task starts from an up-to-date base without the
engineer holding any GitHub credential. Repo hooks and fsmonitor are off for every git call here.
"""
import os
import subprocess
import tempfile
from pathlib import Path

SAFE = ["-c", "core.hooksPath=/dev/null", "-c", "core.fsmonitor=false"]


def git(*args, cwd=None, env=None) -> str:
    return subprocess.run(["git", *SAFE, *args], cwd=cwd, env=env, check=True, capture_output=True,
                          text=True).stdout.strip()


def mirror_path(conf: dict, project: str) -> Path:
    """MIRROR_DIR/<p>.git (default STATE_DIR/mirrors), written by the broker's sync-mirror job."""
    return Path(conf.get("MIRROR_DIR") or Path(conf["STATE_DIR"]) / "mirrors") / f"{project}.git"


def mirror_ref(default: str) -> str:
    return f"refs/remotes/mirror/{default}"


def fetch_mirror(clone: Path, mirror: Path, default: str) -> str | None:
    """Fetch the mirror's default branch into refs/remotes/mirror/<default>; None when there is no mirror.

    The mirror belongs to the broker, so it is trusted for this one fetch through a one-shot global config
    (git drops `-c` settings for the upload-pack it starts on a local repo).
    """
    if not mirror.is_dir():
        return None
    with tempfile.TemporaryDirectory(prefix="run-task-git.") as tmp:
        cfg = Path(tmp) / "config"
        env = {**os.environ, "GIT_CONFIG_GLOBAL": str(cfg), "GIT_CONFIG_NOSYSTEM": "1", "GIT_TERMINAL_PROMPT": "0"}
        git("config", "--file", str(cfg), "safe.directory", str(mirror), env=env)
        git("-c", "protocol.file.allow=always", "fetch", "--quiet", "--no-tags", "--no-recurse-submodules",
            "--no-write-fetch-head", f"file://{mirror}", f"+refs/heads/{default}:{mirror_ref(default)}",
            cwd=clone, env=env)
    return mirror_ref(default)


def _has_ref(cwd: Path, ref: str) -> bool:
    return subprocess.run(["git", *SAFE, "rev-parse", "-q", "--verify", ref], cwd=cwd,
                          capture_output=True).returncode == 0


def base_ref(clone: Path, default: str) -> str:
    """refs/remotes/mirror/<default> when the clone has it, else the clone's own default branch."""
    return mirror_ref(default) if _has_ref(clone, mirror_ref(default)) else default


def ensure_worktree(clone: Path, wt: Path, branch: str, default: str, mirror: Path) -> str:
    """Create or reuse the worktree wt on branch; return the ref the branch is based on.

    A reused branch gets a fresh refs/remotes/mirror/<default> too (best effort), so a retry can merge or
    rebase onto GitHub's head when the audit says the branch does not contain it.
    Raises ValueError when wt exists but is not a worktree on branch, CalledProcessError when git fails.
    """
    if wt.exists():
        if wt.is_symlink() or git("rev-parse", "--abbrev-ref", "HEAD", cwd=wt) != branch:
            raise ValueError(f"{wt} exists but is not a worktree on {branch}")
    elif _has_ref(clone, f"refs/heads/{branch}"):
        wt.parent.mkdir(parents=True, exist_ok=True)
        git("worktree", "add", "-q", str(wt), branch, cwd=clone)
    else:
        wt.parent.mkdir(parents=True, exist_ok=True)
        base = fetch_mirror(clone, mirror, default) or default
        git("worktree", "add", "-q", "-b", branch, str(wt), base, cwd=clone)
        return base
    try:
        fetch_mirror(clone, mirror, default)
    except subprocess.CalledProcessError:
        pass
    return base_ref(clone, default)


def shas(wt: Path, base_ref: str) -> dict:
    """{"head_sha", "base_sha"}: HEAD of the worktree and the commit its branch started from."""
    out = {"head_sha": None, "base_sha": None}
    try:
        out["head_sha"] = git("rev-parse", "HEAD", cwd=wt)
        out["base_sha"] = git("merge-base", "HEAD", base_ref, cwd=wt)
    except subprocess.CalledProcessError:
        pass
    return out
