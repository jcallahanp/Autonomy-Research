#!/usr/bin/env python3
"""Apply John's Telegram replies and T1 timeouts to the open approval items.

Usage: apply-replies.py --events E --records R --now ISO [--timeout-hours H]
stdin: tg-poll JSON lines {update_id, from_id, date, text, edited} (tg-poll keeps only John's messages).
Appends approval-record lines to R, prints each applied decision as a JSON line {item, kind, answer, ref}
(a timeout adds "default"). An edited message is ignored. A message that does not parse approves
nothing and adds one T1 "not understood" ask to E. An item asked after a message was sent is not open
to that message, so a stale "all y" never covers it.
"""
import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))
from approvals import digest, items, replies  # noqa: E402
from eng import schema  # noqa: E402


def append_line(path: Path, obj: dict) -> None:
    """Append one JSON line, starting a fresh line after a torn one; flush and fsync."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "ab+") as f:
        f.seek(0, os.SEEK_END)
        lead = b""
        if f.tell() > 0:
            f.seek(-1, os.SEEK_END)
            lead = b"" if f.read(1) == b"\n" else b"\n"
        f.write(lead + json.dumps(obj, ensure_ascii=False).encode() + b"\n")
        f.flush()
        os.fsync(f.fileno())


def _timeout_default() -> float:
    try:
        import yaml
        return float(yaml.safe_load((ROOT / "templates" / "run-defaults.yaml").read_text())["t1"]["timeout_hours"])
    except Exception:
        return 24.0


def _messages(stream):
    """Well-formed, unedited tg-poll lines."""
    for n, line in enumerate(stream, 1):
        try:
            msg = json.loads(line)
        except ValueError:
            print(f"apply-replies: stdin line {n} is not JSON; skipped", file=sys.stderr)
            continue
        if not isinstance(msg, dict):
            print(f"apply-replies: stdin line {n} is not an object; skipped", file=sys.stderr)
            continue
        if msg.get("edited") is not False:
            print(f"apply-replies: update {msg.get('update_id')!r} is an edit; ignored", file=sys.stderr)
            continue
        yield msg


class Applier:
    def __init__(self, events_path: Path, records_path: Path, now: str):
        self.events_path, self.records_path, self.now = events_path, records_path, now
        self.events = items.read_jsonl(events_path)
        self.open = items.open_items(self.events, items.read_jsonl(records_path), now)
        self.rec_schema = schema.load(ROOT, "approval-record")
        self.ev_schema = schema.load(ROOT, "event")
        projects = [e["project"] for e in self.events if isinstance(e.get("project"), str) and e["project"]]
        self.project = projects[-1] if projects else events_path.parent.name

    def _visible(self, date) -> dict:
        if not isinstance(date, int) or isinstance(date, bool):
            return {}
        return {n: it for n, it in self.open.items() if items.parse_ts(it["asked_at"]).timestamp() <= date}

    def _record(self, item: dict, answer: str, source: str, **extra) -> bool:
        rec = items.record(item, self.now, answer, source, **extra)
        errs = schema.validate(rec, self.rec_schema)
        if errs:
            print(f"apply-replies: record for item {item['item']} invalid: {errs[0]}", file=sys.stderr)
            return False
        append_line(self.records_path, rec)
        self.open.pop(item["item"], None)
        return True

    def not_understood(self, text, errors: list) -> None:
        snippet = digest.one_line(text or "")[:60]
        ev = {"ts": items.iso(items.parse_ts(self.now)), "project": self.project, "event": "approval_ask",
              "detail": {"item": items.next_item(self.events), "tier": "T1", "kind": "other",
                         "text": f'Reply not understood ({digest.one_line(errors[0])[:120]}): "{snippet}". '
                                 "Nothing was approved; send it again.",
                         "default": "no", "reversible": True, "ref": None}}
        errs = schema.validate(ev, self.ev_schema)
        if errs:
            print(f"apply-replies: not-understood event invalid: {errs[0]}", file=sys.stderr)
            return
        append_line(self.events_path, ev)
        self.events.append(ev)

    def reply(self, msg: dict) -> list:
        text = msg.get("text")
        result = replies.parse(text, self._visible(msg.get("date")))
        if result["errors"]:
            self.not_understood(text, result["errors"])
            return []
        from_id = msg.get("from_id") if isinstance(msg.get("from_id"), (int, str)) else None
        raw = text[:1000]
        applied = []
        for d in result["decisions"]:
            item = self.open[d["item"]]
            if self._record(item, d["answer"], "telegram", from_id=from_id, raw=raw):
                applied.append({"item": item["item"], "kind": item["kind"], "answer": d["answer"],
                                "ref": item.get("ref")})
        return applied

    def timeouts(self, timeout_h: float) -> list:
        applied = []
        for rec in items.apply_timeouts(self.open, self.now, timeout_h):
            item = self.open[int(rec["item"])]
            if self._record(item, "default", "timeout"):
                applied.append({"item": item["item"], "kind": item["kind"], "answer": "default",
                                "default": item.get("default"), "ref": item.get("ref")})
        return applied


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Apply Telegram replies and T1 timeouts.")
    ap.add_argument("--events", required=True)
    ap.add_argument("--records", required=True)
    ap.add_argument("--now", required=True)
    ap.add_argument("--timeout-hours", type=float, default=None)
    a = ap.parse_args(argv)
    app = Applier(Path(a.events), Path(a.records), a.now)
    out = []
    for msg in _messages(sys.stdin):
        out += app.reply(msg)
    out += app.timeouts(a.timeout_hours if a.timeout_hours is not None else _timeout_default())
    for d in out:
        print(json.dumps(d))
    return 0


if __name__ == "__main__":
    sys.exit(main())
