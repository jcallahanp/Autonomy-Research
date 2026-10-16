"""Open approval items: approval_ask events without an answer record; T1 timeouts and reminders.

An ask's detail: item (int), tier T1|T2, kind, text, default, reversible, phrase (T2 only), ref.
A T2 item never times out and never takes a default (F38).
"""
import json
from datetime import datetime, timezone
from pathlib import Path

TIERS = ("T1", "T2")
KINDS = ("merge", "plan", "promote", "relogin", "deadend", "denial", "other")


def parse_ts(value) -> datetime:
    """ISO-8601 (Z allowed) to an aware UTC datetime; raise ValueError on anything else."""
    if not isinstance(value, str):
        raise ValueError("timestamp must be a string")
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("timestamp has no timezone")
    return dt.astimezone(timezone.utc)


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_jsonl(path) -> list:
    """Every whole JSON object line of path; torn or invalid lines are skipped."""
    path = Path(path)
    if not path.exists():
        return []
    out = []
    for line in path.read_text(errors="replace").splitlines():
        try:
            obj = json.loads(line)
        except ValueError:
            continue
        if isinstance(obj, dict):
            out.append(obj)
    return out


def _valid(d: dict) -> bool:
    n = d.get("item")
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        return False
    if d.get("tier") not in TIERS or not isinstance(d.get("text"), str):
        return False
    if d["tier"] == "T2":
        phrase = d.get("phrase")
        return isinstance(phrase, str) and bool(phrase.split())
    return True


def open_items(events: list, records: list, now) -> dict:
    """{item: detail + asked_at + age_h} for each well-formed approval_ask without a record."""
    now_dt = parse_ts(now)
    answered = {str(r.get("item")) for r in records if isinstance(r, dict)}
    out = {}
    for ev in events:
        d = ev.get("detail") if ev.get("event") == "approval_ask" else None
        if not isinstance(d, dict) or not _valid(d) or str(d["item"]) in answered:
            continue
        try:
            asked = parse_ts(ev.get("ts"))
        except ValueError:
            continue
        item = dict(d)
        item.setdefault("kind", "other")
        if item["kind"] not in KINDS:
            item["kind"] = "other"
        item["asked_at"] = iso(asked)
        item["age_h"] = (now_dt - asked).total_seconds() / 3600
        out[d["item"]] = item
    return out


def next_item(events: list) -> int:
    """The next free item number: one more than any number ever asked."""
    nums = [ev["detail"]["item"] for ev in events
            if ev.get("event") == "approval_ask" and isinstance(ev.get("detail"), dict)
            and isinstance(ev["detail"].get("item"), int) and not isinstance(ev["detail"]["item"], bool)]
    return max(nums, default=0) + 1


def record(item: dict, now, answer: str, source: str, from_id=None, raw=None) -> dict:
    """An approval-record line for this item."""
    return {"ts": iso(parse_ts(now)), "item": str(item["item"]), "tier": item["tier"], "kind": item["kind"],
            "ask": item["text"], "answer": answer, "from_id": from_id, "raw": raw, "source": source}


def _age_h(item: dict, now) -> float:
    return (parse_ts(now) - parse_ts(item["asked_at"])).total_seconds() / 3600


def apply_timeouts(open_: dict, now, timeout_h: float = 24) -> list:
    """Records for reversible T1 items open at least timeout_h hours; never a T2 or irreversible item."""
    return [record(it, now, "default", "timeout") for _, it in sorted(open_.items())
            if it.get("tier") == "T1" and it.get("reversible") is True and _age_h(it, now) >= timeout_h]


def reminders(open_: dict, now, reminder_h: float = 12) -> list:
    """Item numbers open at least reminder_h hours."""
    return [n for n, it in sorted(open_.items()) if _age_h(it, now) >= reminder_h]
