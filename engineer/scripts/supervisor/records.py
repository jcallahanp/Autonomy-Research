"""The supervisor-owned records clone per project (RECORDS_DIR/<p>, branch engineer-records).

The supervisor writes audit/AUDIT-<id>.md, docs/runs/<date>-MORNING.md, decisions/approvals.jsonl and the
plan snapshots approvals/<p>/v<N>/ here, commits as the bot and pushes through the broker
(`AGENT_RUN push-branch <clone> engineer-records`). engineer never writes this clone, so git may run in it;
repo hooks and fsmonitor are still switched off.

A missing clone is made only after `sync-mirror` (when a runner is given) has refreshed the broker's bare
mirror MIRROR_DIR/<p>.git: it is cloned from there when the mirror has engineer-records, and a fresh
engineer-records is started only when sync-mirror ran and GitHub has no such branch. Either way it is built
in a temp dir and renamed into place, so a crash never leaves a half clone; a broken clone found later is
moved aside (kept for its commits). A failed sync or push never raises out of write_and_push: it is kept
in RECORDS_DIR/.<p>.failed (failure()), retried by retry_push(), and the loop tells John.
"""
import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path, PurePosixPath

BRANCH = "engineer-records"
BOT_NAME = "engineer-bot"
SAFE = ["-c", "core.hooksPath=/dev/null", "-c", "core.fsmonitor=", "-c", "commit.gpgsign=false"]


class RecordsError(RuntimeError):
    """The records clone cannot be made or used safely."""


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


def _rc(res) -> tuple:
    """(exit code, stdout, stderr) of a runner's result; a runner returning None counts as success."""
    return getattr(res, "returncode", 0), getattr(res, "stdout", "") or "", getattr(res, "stderr", "") or ""


def _sync(run, project: str) -> dict:
    """Run sync-mirror; its JSON reply ({} when it printed none). RecordsError when it failed."""
    rc, out, err = _rc(run(["sync-mirror", project]))
    if rc:
        raise RecordsError(f"sync-mirror exited {rc} ({err.strip()[:120]}); no records clone made")
    for line in reversed(out.splitlines()):
        try:
            doc = json.loads(line)
        except ValueError:
            continue
        if isinstance(doc, dict):
            return doc
    return {}


def _healthy(clone: Path) -> bool:
    p = _git(clone, "rev-parse", "--is-inside-work-tree", check=False)
    return p.returncode == 0 and p.stdout.strip() == "true" and Path(_git(
        clone, "rev-parse", "--show-toplevel").stdout.strip()).resolve() == clone.resolve()


def _make(clone: Path, project: str, mirror: Path, run) -> None:
    synced = _sync(run, project) if run is not None else {}
    has = mirror.is_dir() and _mirror_has_branch(mirror)
    if synced.get("records") and not has:
        raise RecordsError("GitHub has engineer-records but the mirror does not; not starting a new one")
    for old in clone.parent.glob(f".{project}.new.*"):
        shutil.rmtree(old, ignore_errors=True)
    tmp = Path(tempfile.mkdtemp(prefix=f".{project}.new.", dir=clone.parent))
    try:
        if has:
            _mirror_git(mirror, "clone", "-q", "--template=", "--no-tags", "--single-branch", "--branch", BRANCH,
                        f"file://{mirror}", str(tmp))
            _git(tmp, "config", "core.hooksPath", "/dev/null")
        else:
            _git(tmp, "init", "-q", "--template=", "-b", BRANCH)
        os.rename(tmp, clone)
    except (subprocess.CalledProcessError, OSError) as e:
        shutil.rmtree(tmp, ignore_errors=True)
        raise RecordsError(f"making the records clone failed ({type(e).__name__})") from e


def ensure(records_dir, project: str, mirror_dir=None, run=None) -> Path:
    """Return the clone on engineer-records, making it when missing (see the module doc).

    run: the AGENT_RUN runner; when given, sync-mirror runs before a clone is made.
    Raises ValueError for a symlinked mirror or clone and RecordsError when the clone cannot be made.
    """
    records_dir = Path(records_dir)
    clone = records_dir / project
    mdir = Path(mirror_dir) if mirror_dir is not None else records_dir.parent / "mirrors"
    mirror = mdir / f"{project}.git"
    if mdir.is_symlink() or mirror.is_symlink() or clone.is_symlink():
        raise ValueError(f"records path is a symlink: {mirror} or {clone}")
    if clone.exists() and not ((clone / ".git").is_dir() and _healthy(clone)):
        os.rename(clone, records_dir / f"{project}.broken-{int(time.time())}")
    if not clone.exists():
        records_dir.mkdir(parents=True, exist_ok=True)
        _make(clone, project, mirror, run)
    head = _git(clone, "symbolic-ref", "--short", "HEAD", check=False).stdout.strip()
    if head != BRANCH and _git(clone, "checkout", "-q", BRANCH, check=False).returncode:
        if _git(clone, "checkout", "-q", "-b", BRANCH, check=False).returncode:
            raise RecordsError(f"{clone} cannot switch to {BRANCH}")
    return clone


def _marker(records_dir, project: str) -> Path:
    return Path(records_dir) / f".{project}.failed"


def failure(records_dir, project: str) -> str | None:
    """The last sync or push failure not yet cleared by a good push, or None."""
    m = _marker(records_dir, project)
    return m.read_text().strip() or "failed" if m.is_file() else None


def _push(records_dir, project: str, clone: Path, run) -> bool:
    rc, _, err = _rc(run(["push-branch", str(clone), BRANCH]))
    if rc:
        _marker(records_dir, project).write_text(f"push-branch exited {rc}: {err.strip()[:200]}\n")
        return False
    _marker(records_dir, project).unlink(missing_ok=True)
    return True


def retry_push(records_dir, project: str, run) -> bool:
    """Push again after a recorded failure; True when nothing is pending any more."""
    if failure(records_dir, project) is None:
        return True
    try:
        return _push(records_dir, project, ensure(records_dir, project, run=run), run)
    except (RecordsError, ValueError, subprocess.CalledProcessError, OSError) as e:
        _marker(records_dir, project).write_text(f"records clone: {e}\n")
        return False


def write_files(records_dir, project: str, files: dict, message: str, run,
                email: str = "engineer-bot@users.noreply.github.com", mirror_dir=None) -> dict:
    """Write {relpath: str|bytes}, commit as the bot, push. {committed, pushed, sha, error}; never raises
    for a sync, git or push failure (it is recorded for failure())."""
    rels = {_relpath(k): v for k, v in files.items()}
    out = {"committed": False, "pushed": None, "sha": None, "error": None}
    try:
        clone = ensure(records_dir, project, mirror_dir, run)
        for rel, content in rels.items():
            target = clone.joinpath(*rel.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content if isinstance(content, bytes) else content.encode())
        _git(clone, "add", "--", *[str(r) for r in rels])
        if _git(clone, "diff", "--cached", "--quiet", check=False).returncode:
            _git(clone, "-c", f"user.name={BOT_NAME}", "-c", f"user.email={email}",
                 "commit", "-q", "--no-verify", "-m", message)
            out["committed"] = True
        out["sha"] = _git(clone, "rev-parse", "HEAD").stdout.strip()
    except (RecordsError, ValueError, subprocess.CalledProcessError, OSError) as e:
        out["error"] = f"records clone: {e}"
        _marker(records_dir, project).write_text(out["error"] + "\n")
        return out
    if out["committed"] or failure(records_dir, project):
        out["pushed"] = _push(records_dir, project, clone, run)
    return out


def write_and_push(records_dir, project: str, relpath: str, content: str, message: str, run,
                   email: str = "engineer-bot@users.noreply.github.com", mirror_dir=None) -> bool:
    """Write relpath, commit as the bot, push via run(["push-branch", clone, BRANCH]); True when a commit
    was made. run is a callable taking the AGENT_RUN argument list."""
    _relpath(relpath)
    return write_files(records_dir, project, {relpath: content}, message, run, email, mirror_dir)["committed"]
