"""A task's check, as run-task (profile `check`) and the stop gate run it.

The command comes only from the tasks.json John approved: the copy stored in the records clone at
RECORDS_DIR/<p>/approvals/<p>/v<scope_version>/docs/plan/tasks.json (approvals/plansnap.py) when it is there,
else the given bytes (docs/plan/tasks.json in the commit itself); either way its sha256 must equal the hash in
the live approval STATE_DIR/approvals/<p>.json, or nothing runs.
It runs in a clean detached checkout of that commit (no untracked or uncommitted files) inside bwrap: the root
read-only, writable only the checkout and a scratch dir, the clone's .git read-only (git works), the engineer
worktree's untracked dependency dirs (DEP_DIRS, real dirs only) bound read-only, the network shared but sent
through the egress proxy (nft confines the engineer uid), and the credential stores (HIDE_DIRS, HIDE_FILES,
CHROME_PROFILE) hidden. Without bwrap the caller logs WARNING and runs it unsandboxed (development
containers; dependency dirs are symlinked instead); the droplet installs bwrap.
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
DEP_DIRS = ("node_modules", ".venv", "venv", "vendor", ".bundle")
HIDE_DIRS = (".claude", ".config/gh", ".ssh", ".engineer", ".gnupg", ".aws", ".docker", ".config/gcloud",
             ".local/share/keyrings")
HIDE_FILES = (".claude.json", ".git-credentials", ".netrc", ".npmrc", ".pypirc")
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


def approved_copy(conf: dict, project: str, fallback: bytes | None, where: str = "the working tree") -> bytes:
    """tasks.json exactly as approved: the stored copy, else fallback; ValueError when neither matches."""
    doc = approval(conf, project)
    want, version = doc["files"][REL], doc.get("scope_version")
    try:
        data = (Path(conf["RECORDS_DIR"]) / project / "approvals" / project / f"v{version}" / REL).read_bytes()
    except OSError:
        data = None
    if data is not None and _sha256(data) == want:
        return data
    if fallback is None:
        raise ValueError(f"{REL} is missing at {where}")
    if _sha256(fallback) != want:
        raise ValueError(f"{REL} at {where} is not the approved copy (sha256 differs from plan approval "
                         f"v{version}); a task never edits it")
    return fallback


def approved_bytes(conf: dict, project: str, repo, sha: str) -> bytes:
    """tasks.json exactly as approved: the stored copy, else the blob at sha; ValueError on any mismatch."""
    p = subprocess.run(["git", *SAFE, "cat-file", "blob", f"{sha}:{REL}"], cwd=repo, capture_output=True)
    return approved_copy(conf, project, p.stdout if p.returncode == 0 else None, sha[:12])


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


def spec(conf: dict, repo, wt, co, home: str) -> dict:
    """What the sandbox shows: {"gitdir", "deps": [(src, dst)], "hide_dirs", "hide_files"} (existing paths only).

    deps: each DEP_DIRS entry that is a real directory directly in the engineer worktree wt (never a symlink,
    which could point at a credential store) and absent from the commit, bound at co/<name>.
    """
    p = subprocess.run(["git", *SAFE, "rev-parse", "--path-format=absolute", "--git-common-dir"], cwd=repo,
                       capture_output=True, text=True)
    out = {"gitdir": p.stdout.strip() if p.returncode == 0 else None, "deps": [], "hide_dirs": [], "hide_files": []}
    base = Path(wt).resolve() if wt and Path(wt).is_dir() and not Path(wt).is_symlink() else None
    for name in DEP_DIRS if base else ():
        src = base / name
        if not src.is_symlink() and src.is_dir() and src.resolve().parent == base \
                and not os.path.lexists(Path(co) / name):
            out["deps"].append((str(src), str(Path(co) / name)))
    homes = [Path(home) / d for d in HIDE_DIRS] if home and home != "/" else []
    for d in homes + ([Path(conf["CHROME_PROFILE"])] if conf.get("CHROME_PROFILE") else []):
        if d.is_dir() and str(d) not in out["hide_dirs"]:
            out["hide_dirs"].append(str(d))
    out["hide_files"] = [str(Path(home) / f) for f in HIDE_FILES if homes and (Path(home) / f).is_file()]
    return out


def place(sp: dict, bw: str | None) -> None:
    """Make each dependency mount point in the checkout: an empty dir for bwrap, else a symlink to the source."""
    for src, dst in sp["deps"]:
        if bw:
            Path(dst).mkdir()
        else:
            os.symlink(src, dst)


def env(conf: dict, scratch) -> dict:
    """The check's extra environment: scratch TMPDIR and caches, and the egress proxy (PROXY_PORT)."""
    out = {"TMPDIR": str(scratch), "npm_config_cache": f"{scratch}/npm-cache", "PIP_CACHE_DIR": f"{scratch}/pip",
           "UV_CACHE_DIR": f"{scratch}/uv"}
    if str(conf.get("PROXY_PORT") or "").isdigit():
        url = f"http://127.0.0.1:{conf['PROXY_PORT']}"
        for k in ("HTTPS_PROXY", "HTTP_PROXY", "https_proxy", "http_proxy"):
            out[k] = url
        out["NO_PROXY"] = out["no_proxy"] = "127.0.0.1,localhost"
    return out


def sandbox(argv: list, co, scratch, bw: str | None, sp: dict | None = None) -> list:
    """argv inside bwrap (see the module docstring); argv itself when there is no bwrap."""
    if not bw:
        return list(argv)
    sp = sp or {"gitdir": None, "deps": [], "hide_dirs": [], "hide_files": []}
    out = [bw, "--die-with-parent", "--new-session", "--unshare-all", "--share-net", "--ro-bind", "/", "/",
           "--dev", "/dev", "--proc", "/proc", "--tmpfs", "/tmp"]
    for d in sp["hide_dirs"]:
        out += ["--tmpfs", d]
    for f in sp["hide_files"]:
        out += ["--ro-bind", "/dev/null", f]
    if sp["gitdir"]:
        out += ["--ro-bind", sp["gitdir"], sp["gitdir"]]
    out += ["--bind", str(co), str(co), "--bind", str(scratch), str(scratch)]
    for src, dst in sp["deps"]:
        out += ["--ro-bind", src, dst]
    return out + ["--chdir", str(co), "--", *argv]
