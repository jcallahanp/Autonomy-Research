"""What John approved: the plan ask he answered, with the sha256 of each signed file as he saw it.

approve-plan (run by the supervisor) reads the ask from STATE_DIR/<p>/events.jsonl and John's answer
from RECORDS_DIR/<p>/decisions/approvals.jsonl, and refuses unless every signed file it copied still has
the hash the ask carried (security: John approves exactly what he saw).
"""
from pathlib import Path

from approvals import items
from eng import approval


def ask(events_path, item: int) -> dict:
    """The detail of the last `plan` approval_ask with this item number; ValueError if there is none."""
    found = None
    for ev in items.read_jsonl(events_path):
        d = ev.get("detail")
        if ev.get("event") == "approval_ask" and isinstance(d, dict) and d.get("item") == item:
            found = d
    if found is None or found.get("kind") != "plan":
        raise ValueError(f"item {item} is not a plan approval ask")
    return found


def answered_yes(records_path, item: int) -> bool:
    """True when approvals.jsonl holds John's `yes` for this item."""
    return any(items.item_num(r.get("item")) == item and r.get("answer") == "yes" and r.get("kind") == "plan"
               for r in items.read_jsonl(records_path))


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
