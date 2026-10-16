"""A task's check, as run-task (profile `check`) and the stop gate run it.

The command comes only from the tasks.json John approved: the copy stored in the records clone at
RECORDS_DIR/<p>/approvals/<p>/v<scope_version>/docs/plan/tasks.json (approvals/plansnap.py) when it is there, else docs/plan/tasks.json in the commit itself; either way its
sha256 must equal the hash in the live approval STATE_DIR/approvals/<p>.json, or nothing runs.
It runs in a clean detached checkout of that commit (no untracked or uncommitted files), inside bwrap with
no network and writes only to the checkout and a tmp dir. Without bwrap the caller logs WARNING and runs
it unsandboxed (development containers); the droplet installs bwrap.
"""
import contextlib
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from runtask.worktree import SAFE, git

REL = "docs/plan/tasks.json"
WARNING = "run-task: warning: bwrap not found; the check runs without the sandbox (network and writes open)"


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def commit(repo, ref: str) -> str:
    """The commit ref names in repo; ValueError when there is none."""
    try:
        return git("rev-parse", "--verify", "-q", f"{ref}^{{commit}}", cwd=repo)
    except subprocess.CalledProcessError:
        raise ValueError(f"no commit {ref}") from None


def approval(conf: dict, project: str) -> dict:
    path = Path(conf["STATE_DIR"]) / "approvals" / f"{project}.json"
    try:
        doc = json.loads(path.read_text())
    except (OSError, ValueError):
        raise ValueError(f"no readable plan approval for {project}; the plan must be approved first") from None
    want = (doc.get("files") or {}).get(REL) if isinstance(doc, dict) else None
    if not isinstance(want, str) or len(want) != 64:
        raise ValueError(f"the plan approval for {project} has no hash for {REL}; approve the plan again")
    return doc


def approved_bytes(conf: dict, project: str, repo, sha: str) -> bytes:
    """tasks.json exactly as approved: the stored copy, else the blob at sha; ValueError on any mismatch."""
    doc = approval(conf, project)
    want, version = doc["files"][REL], doc.get("scope_version")
    try:
        data = (Path(conf["RECORDS_DIR"]) / project / "approvals" / project / f"v{version}" / REL).read_bytes()
    except OSError:
        data = None
    if data is not None and _sha256(data) == want:
        return data
    p = subprocess.run(["git", *SAFE, "cat-file", "blob", f"{sha}:{REL}"], cwd=repo, capture_output=True)
    if p.returncode != 0:
        raise ValueError(f"{REL} is missing at {sha[:12]}")
    if _sha256(p.stdout) != want:
        raise ValueError(f"{REL} at {sha[:12]} is not the approved copy (sha256 differs from plan approval "
                         f"v{version}); a task never edits it")
    return p.stdout


def task(data: bytes, task_id: str) -> dict:
    """The task with this id from approved tasks.json bytes; ValueError when absent or without a check."""
    try:
        doc = json.loads(data)
    except ValueError:
        raise ValueError(f"approved {REL} is not JSON") from None
    for t in doc.get("tasks", []) if isinstance(doc, dict) else []:
        if isinstance(t, dict) and t.get("id") == task_id:
            if not isinstance(t.get("check"), str) or not t["check"].strip():
                raise ValueError(f"task {task_id} has no check in the approved {REL}")
            return t
    raise ValueError(f"task {task_id} is not in the approved {REL}")


@contextlib.contextmanager
def checkout(repo, sha: str):
    """Yield (checkout, tmp): a detached worktree of sha with no untracked files, and a scratch dir."""
    base = Path(tempfile.mkdtemp(prefix="run-task-check."))
    co, scratch = base / "co", base / "tmp"
    scratch.mkdir()
    try:
        git("worktree", "add", "-q", "--detach", str(co), sha, cwd=repo)
        yield co, scratch
    finally:
        subprocess.run(["git", *SAFE, "worktree", "remove", "--force", str(co)], cwd=repo, capture_output=True)
        subprocess.run(["git", *SAFE, "worktree", "prune"], cwd=repo, capture_output=True)
        shutil.rmtree(base, ignore_errors=True)


def bwrap(root) -> str | None:
    """bwrap from the root-owned bin dirs only (never a PATH dir the engineer can write)."""
    for d in (Path(root) / "bin", Path("/usr/bin"), Path("/bin")):
        if os.access(d / "bwrap", os.X_OK):
            return str(d / "bwrap")
    return None


def sandbox(argv: list, co, scratch, home: str, bw: str | None) -> list:
    """argv inside bwrap: everything read-only, no network, writable only co and scratch; argv when no bwrap."""
    if not bw:
        return list(argv)
    hide = ["--tmpfs", home] if home and home != "/" else []
    return [bw, "--die-with-parent", "--new-session", "--unshare-all", "--ro-bind", "/", "/", "--dev", "/dev",
            "--proc", "/proc", "--tmpfs", "/tmp", *hide, "--bind", str(co), str(co),
            "--bind", str(scratch), str(scratch), "--chdir", str(co), "--setenv", "HOME", str(scratch),
            "--setenv", "TMPDIR", str(scratch), "--", *argv]
