"""Plan approval: the five files John signs, their sha256 hashes, and the check the hooks run.

tasks.json is signed too: each task's `check` command runs on the droplet, so only the approved bytes may
supply it (runtask/check.py), and a task never edits it (task status lives in the supervisor's events).

The live approval is $STATE_DIR/approvals/<project>.json, written by the supervisor only.
"""
import hashlib
from pathlib import Path

SIGNED = ("docs/plan/brief.md", "docs/plan/requirements.md",
          "docs/plan/integrations.yaml", "docs/plan/profile.yaml", "docs/plan/tasks.json")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hashes(repo: Path) -> dict:
    """{path: sha256} for each signed file that exists in repo."""
    repo = Path(repo)
    return {rel: _sha256(repo / rel) for rel in SIGNED if (repo / rel).is_file()}


def make(repo, approved_by, source, record_id, scope_version, gates, date) -> dict:
    """Build an approval record; raise FileNotFoundError if a signed file is missing."""
    files = hashes(repo)
    missing = [rel for rel in SIGNED if rel not in files]
    if missing:
        raise FileNotFoundError(f"signed file missing: {', '.join(missing)}")
    return {"approved_by": approved_by, "date": date, "files": files,
            "scope_version": scope_version, "gates": list(gates),
            "source": source, "record_id": record_id}


def check(repo: Path, approval) -> list:
    """One line per signed file that is missing or differs from the approval; [] when all match."""
    if approval is None:
        return ["no approval"]
    files = approval.get("files") if isinstance(approval, dict) else None
    if not isinstance(files, dict):
        return ["approval has no files map"]
    repo = Path(repo)
    errors = []
    for rel in SIGNED:
        path = repo / rel
        if rel not in files:
            errors.append(f"{rel}: not in the approval")
        elif not path.is_file():
            errors.append(f"{rel}: missing")
        elif _sha256(path) != files[rel]:
            errors.append(f"{rel}: changed since approval")
    errors += [f"{rel}: not a signed file" for rel in files if rel not in SIGNED]
    return errors
