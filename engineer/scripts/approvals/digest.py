#!/usr/bin/env python3
"""Telegram digest text: one numbered line per open T1 item, and a separate message per T2 hard gate.

CLI (run by the supervisor): digest.py --events E --records R --now ISO [--max-open N] [--json-object]
prints a JSON list of message strings: each open T2 item first, then the T1 digest. With --json-object it
prints {"messages": [...], "shown": [item, ...]}: the T1 items the digest lists, which `all y` may cover.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))
from approvals import items as _items  # noqa: E402
from approvals.render import line, one_line, render_reminder, render_t2  # noqa: E402,F401

LIMIT = 4096


def chunk(lines: list, limit: int = LIMIT) -> list:
    """Join lines into messages of at most limit characters, splitting only between lines
    unless a single line is longer than limit."""
    msgs, cur = [], ""
    for line in lines:
        while len(line) > limit:
            if cur:
                msgs.append(cur)
                cur = ""
            msgs.append(line[:limit])
            line = line[limit:]
        if cur and len(cur) + 1 + len(line) > limit:
            msgs.append(cur)
            cur = ""
        cur = f"{cur}\n{line}" if cur else line
    if cur:
        msgs.append(cur)
    return msgs


def _oldest_first(open_items: dict) -> list:
    return sorted(open_items.values(), key=lambda it: (str(it.get("asked_at", "")), it["item"]))


def shown(open_items: dict, max_open: int = 5) -> list:
    """The T1 items render() lists, oldest first (the rest are "+K more")."""
    return [it for it in _oldest_first(open_items) if it.get("tier") == "T1"][:max_open]


def render(open_items: dict, max_open: int = 5) -> list:
    """T1 digest messages: oldest first, at most max_open lines plus "+K more in the next digest"."""
    t1 = [it for it in _oldest_first(open_items) if it.get("tier") == "T1"]
    lines = [line(it) for it in shown(open_items, max_open)]
    if len(t1) > max_open:
        lines.append(f"+{len(t1) - max_open} more in the next digest")
    return chunk(lines)


def _max_open_default() -> int:
    try:
        import yaml
        conf = yaml.safe_load((ROOT / "templates" / "run-defaults.yaml").read_text())
        return int(conf["t1"]["max_open"])
    except Exception:
        return 5


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--events", required=True)
    ap.add_argument("--records", required=True)
    ap.add_argument("--now", required=True)
    ap.add_argument("--max-open", type=int, default=None)
    ap.add_argument("--json-object", action="store_true")
    a = ap.parse_args(argv)
    open_ = _items.open_items(_items.read_jsonl(a.events), _items.read_jsonl(a.records), a.now)
    max_open = a.max_open if a.max_open is not None else _max_open_default()
    msgs = [render_t2(it) for it in _oldest_first(open_) if it.get("tier") == "T2"]
    msgs += render(open_, max_open)
    if a.json_object:
        print(json.dumps({"messages": msgs, "shown": [it["item"] for it in shown(open_, max_open)]}))
    else:
        print(json.dumps(msgs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
