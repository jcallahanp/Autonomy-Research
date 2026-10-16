#!/usr/bin/env python3
"""Telegram digest text: one numbered line per open T1 item, and a separate message per T2 hard gate.

CLI (run by the supervisor): digest.py --events E --records R --now ISO [--max-open N]
prints a JSON list of message strings: each open T2 item first, then the T1 digest.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))
from approvals import items as _items  # noqa: E402

LIMIT = 4096


def one_line(text) -> str:
    """Collapse whitespace and control characters so an item is exactly one line."""
    text = "".join(c if c.isprintable() else " " for c in str(text))
    return " ".join(text.split())


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


def render(open_items: dict, max_open: int = 5) -> list:
    """T1 digest messages: oldest first, at most max_open lines plus "+K more in MORNING.md"."""
    t1 = [it for it in _oldest_first(open_items) if it.get("tier") == "T1"]
    lines = []
    for it in t1[:max_open]:
        n = it["item"]
        lines.append(f'{n}. {one_line(it.get("text", ""))} (default: {one_line(it.get("default", "no"))}). '
                     f'Reply "{n} y" or "{n} n".')
    if len(t1) > max_open:
        lines.append(f"+{len(t1) - max_open} more in MORNING.md")
    return chunk(lines)


def render_t2(item: dict) -> str:
    """The separate hard-gate message; no reply means no."""
    n = item["item"]
    return (f"HARD GATE {n}: {one_line(item.get('text', ''))}\n"
            f"To approve, reply exactly: CONFIRM {n} {one_line(item['phrase'])}\n"
            "No reply means no.")


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
    a = ap.parse_args(argv)
    open_ = _items.open_items(_items.read_jsonl(a.events), _items.read_jsonl(a.records), a.now)
    msgs = [render_t2(it) for it in _oldest_first(open_) if it.get("tier") == "T2"]
    msgs += render(open_, a.max_open if a.max_open is not None else _max_open_default())
    print(json.dumps(msgs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
