#!/usr/bin/env python3
"""Apply John's Telegram replies and T1 timeouts to the open approval items of every project.

Usage: apply-replies.py --events E --records R [--events E2 --records R2 ...] [--read-records F ...] --now ISO
       [--timeout-hours H]
One --events/--records pair per project (STATE_DIR/<p>/events.jsonl, RECORDS_DIR/<p>/decisions/approvals.jsonl).
Item numbers are global across projects, so each reply is parsed once against every project's open items
and each decision is recorded in its own project's records file: a reply never answers another project's
item. A number open in two projects (legacy state) is refused.
stdin: tg-poll JSON lines {update_id, from_id, date, text, edited} (tg-poll keeps only John's messages).
Prints each applied decision as a JSON line {item, kind, answer, ref, project, task_id} (a timeout adds
"default"), and {notice, project, item} for a reply that was not understood (the supervisor sends it at once).
An edited message is ignored. A message that does not parse approves nothing and adds one T1 "not
understood" ask to the first project. An item asked after a message was sent is not open to that message;
`N y|n` needs N in a digest or notice John was sent before the message; `all y|n` covers only the reversible
T1 items the last digest of each project sent before the message listed (a `digest` event's detail.items).
A record in STATE_DIR/<p>/approvals.pending.jsonl (kept while there is no records clone) counts as answered,
and so does one in a --read-records file (a records clone's file while new records go to the pending file;
item numbers are global, so these are read for every project).
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
    def __init__(self, pairs: list, now: str, read=()):
        self.now, self.pairs = now, [(Path(e), Path(r)) for e, r in pairs]
        self.events, self.open, dup = [], {}, set()
        extra = [r for path in read for r in items.read_jsonl(path)]
        for i, (ev_path, rec_path) in enumerate(self.pairs):
            evs = items.read_jsonl(ev_path)
            self.events += evs
            for n, it in items.open_items(evs, items.answers(ev_path, rec_path) + extra, now).items():
                if n in self.open:
                    dup.add(n)
                self.open[n] = {**it, "pair": i}
        for n in sorted(dup):
            print(f"apply-replies: item {n} is open in two projects; refused", file=sys.stderr)
            self.open.pop(n)
        self.rec_schema = schema.load(ROOT, "approval-record")
        self.ev_schema = schema.load(ROOT, "event")
        ev0 = self.pairs[0][0]
        names = [e["project"] for e in items.read_jsonl(ev0) if isinstance(e.get("project"), str) and e["project"]]
        self.project = names[-1] if names else ev0.parent.name

    def _visible(self, date) -> dict:
        if not isinstance(date, int) or isinstance(date, bool):
            return {}
        return {n: it for n, it in self.open.items() if items.parse_ts(it["asked_at"]).timestamp() <= date}

    def _record(self, item: dict, answer: str, source: str, **extra) -> dict | None:
        rec = items.record(item, self.now, answer, source, **extra)
        errs = schema.validate(rec, self.rec_schema)
        if errs:
            print(f"apply-replies: record for item {item['item']} invalid: {errs[0]}", file=sys.stderr)
            return None
        append_line(self.pairs[item["pair"]][1], rec)
        self.open.pop(item["item"], None)
        return {"item": item["item"], "kind": item["kind"], "answer": answer, "ref": item.get("ref"),
                "project": item.get("project"), "task_id": item.get("task_id")}

    def not_understood(self, text, errors: list) -> list:
        snippet = digest.one_line(text or "")[:60]
        n = max(items.next_global(self.pairs[0][0].parent.parent), items.next_item(self.events))
        why = f'Reply not understood ({digest.one_line(errors[0])[:120]}): "{snippet}". Nothing was approved; send it again.'
        ev = {"ts": items.iso(items.parse_ts(self.now)), "project": self.project, "event": "approval_ask",
              "detail": {"item": n, "tier": "T1", "kind": "other", "text": why, "default": "no",
                         "reversible": True, "ref": None}}
        errs = schema.validate(ev, self.ev_schema)
        if errs:
            print(f"apply-replies: not-understood event invalid: {errs[0]}", file=sys.stderr)
            return []
        append_line(self.pairs[0][0], ev)
        self.events.append(ev)
        return [{"notice": f"{n}. {self.project}: {why}", "project": self.project, "item": n}]

    def reply(self, msg: dict) -> list:
        text, date = msg.get("text"), msg.get("date")
        last, listed = items.seen(self.events, date)
        result = replies.parse(text, self._visible(date), shown=last, listed=listed)
        if result["errors"]:
            return self.not_understood(text, result["errors"])
        from_id = msg.get("from_id") if isinstance(msg.get("from_id"), (int, str)) else None
        out = [self._record(self.open[d["item"]], d["answer"], "telegram", from_id=from_id, raw=text[:1000])
               for d in result["decisions"]]
        return [d for d in out if d]

    def timeouts(self, timeout_h: float) -> list:
        applied = []
        for rec in items.apply_timeouts(self.open, self.now, timeout_h):
            item = self.open[items.item_num(rec["item"])]
            d = self._record(item, "default", "timeout")
            if d:
                applied.append({**d, "default": item.get("default")})
        return applied


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Apply Telegram replies and T1 timeouts.")
    ap.add_argument("--events", required=True, action="append")
    ap.add_argument("--records", required=True, action="append")
    ap.add_argument("--read-records", action="append", default=[])
    ap.add_argument("--now", required=True)
    ap.add_argument("--timeout-hours", type=float, default=None)
    a = ap.parse_args(argv)
    if len(a.events) != len(a.records):
        ap.error("give one --records per --events")
    app = Applier(list(zip(a.events, a.records)), a.now, a.read_records)
    out = []
    for msg in _messages(sys.stdin):
        out += app.reply(msg)
    out += app.timeouts(a.timeout_hours if a.timeout_hours is not None else _timeout_default())
    for d in out:
        print(json.dumps(d))
    return 0


if __name__ == "__main__":
    sys.exit(main())
