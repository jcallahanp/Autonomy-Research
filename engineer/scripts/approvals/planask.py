"""What John approved: the plan ask he answered and the signed files stored for it (approvals/plansnap.py).

approve-plan (run by the supervisor) reads the ask from STATE_DIR/<p>/events.jsonl, John's answer from
RECORDS_DIR/<p>/decisions/approvals.jsonl (or STATE_DIR/<p>/approvals.pending.jsonl) and the files from RECORDS_DIR/<p>/approvals/<p>/v<N>/ (the bytes of
the plan PR's head commit, committed when the ask was raised), and refuses unless every stored file has the
hash the ask carried (security: John approves exactly what he saw, never the engineer's working tree).
"""
import os
import stat
from pathlib import Path

from approvals import items
from eng import approval

TAG_PENDING = "plan-tags.pending"  # STATE_DIR/<p>/: plan-approved tags whose push failed (telegram retries)
GATES = ("money", "delete_data", "store_submission")
MAX_BYTES = 1 << 20


class Refused(Exception):
    pass


def ask(events_path, item: int) -> dict:
    """The detail of the last `plan` approval_ask with this item number; Refused if there is none."""
    found = None
    for ev in items.read_jsonl(events_path):
        d = ev.get("detail")
        if ev.get("event") == "approval_ask" and isinstance(d, dict) and d.get("item") == item:
            found = d
    if found is None or found.get("kind") != "plan":
        raise Refused(f"item {item} is not a plan approval ask")
    v = found.get("version")
    if not isinstance(v, int) or isinstance(v, bool) or v < 1 or not isinstance(found.get("snapshot"), str):
        raise Refused(f"item {item} carries no plan version and stored snapshot")
    return found


def answered_yes(events_path, records_path, item: int) -> bool:
    """True when approvals.jsonl, or the pending file kept while there was no records clone, holds John's `yes`."""
    return any(items.item_num(r.get("item")) == item and r.get("answer") == "yes" and r.get("kind") == "plan"
               for r in items.answers(events_path, records_path))


def copy_signed(src: Path, dest: Path) -> None:
    """Copy each signed file of src as a regular file (no symlink anywhere on its path) into dest."""
    if src.is_symlink() or not src.is_dir():
        raise Refused(f"{src} is not a directory")
    for rel in approval.SIGNED:
        parts = Path(rel).parts
        for i in range(1, len(parts)):
            if src.joinpath(*parts[:i]).is_symlink():
                raise Refused(f"{'/'.join(parts[:i])} is a symlink")
        try:
            fd = os.open(src / rel, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        except OSError as e:
            raise Refused(f"{rel}: cannot open ({e.strerror})")
        with os.fdopen(fd, "rb") as f:
            if not stat.S_ISREG(os.fstat(f.fileno()).st_mode):
                raise Refused(f"{rel} is not a regular file")
            data = f.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise Refused(f"{rel} is larger than 1 MiB")
        (dest / rel).parent.mkdir(parents=True, exist_ok=True)
        (dest / rel).write_bytes(data)


def mismatches(expected, copy_dir: Path) -> list:
    """One line per signed file whose hash is missing from the ask or differs from the copy; [] when equal."""
    if not isinstance(expected, dict):
        return ["the plan ask carries no file hashes"]
    got = approval.hashes(Path(copy_dir))
    out = []
    for rel in approval.SIGNED:
        want = expected.get(rel)
        if not isinstance(want, str) or len(want) != 64:
            out.append(f"{rel}: no hash in the plan ask")
        elif got.get(rel) != want:
            out.append(f"{rel}: changed since John was asked")
    out += [f"{rel}: not a signed file" for rel in expected if rel not in approval.SIGNED]
    return out


def gates(profile: Path) -> list:
    """profile.yaml hard_gates (all three when the key is absent); Refused when empty or unknown."""
    import yaml
    try:
        data = yaml.safe_load(profile.read_text())
    except yaml.YAMLError:
        raise Refused("profile.yaml is not valid YAML")
    found = data.get("hard_gates", list(GATES)) if isinstance(data, dict) else None
    if not isinstance(found, list) or any(g not in GATES for g in found):
        raise Refused(f"profile.yaml hard_gates must be a list from {', '.join(GATES)}")
    if not found:
        raise Refused("profile.yaml hard_gates is empty; money, deletes and store submissions need a hard gate")
    return found


def previous_version(path: Path) -> int:
    """scope_version of the live approval (0 when none); RuntimeError when it is unreadable."""
    import json
    if not path.exists():
        return 0
    try:
        v = json.loads(path.read_text())["scope_version"]
    except (ValueError, KeyError, TypeError):
        raise RuntimeError(f"{path} is unreadable; fix it by hand before approving again")
    if not isinstance(v, int) or isinstance(v, bool) or v < 0:
        raise RuntimeError(f"{path} has a bad scope_version")
    return v
