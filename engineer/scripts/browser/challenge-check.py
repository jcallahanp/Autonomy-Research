#!/usr/bin/env python3
"""Detect a login page, CAPTCHA or bot challenge in a browser page (F41: stop and notify, never bypass).

stdin: one JSON object {"url", "title", "text"} built from a Playwright MCP snapshot. When "text" is
absent, "html" (page source) may be given instead; its visible text and <title> are used.
Patterns: templates/challenge-patterns.txt, one `kind<TAB>field<TAB>regex` per line, field url|title|text,
matched case-insensitively, first match wins.
stdout: {"challenge": bool, "kind": str|null, "host": str|null}
Exit: 0 clean, 3 challenge, 2 bad input or bad pattern file.
Usage: challenge-check.py [--patterns FILE] < snapshot.json
"""
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PATTERNS = ROOT / "templates" / "challenge-patterns.txt"
FIELDS = ("url", "title", "text")


class _Text(HTMLParser):
    """Visible text and the <title> of an HTML page; script and style bodies are skipped."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.title, self._skip, self._in_title = [], "", 0, False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "template"):
            self._skip += 1
        elif tag == "title":
            self._in_title = True

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "template") and self._skip:
            self._skip -= 1
        elif tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        elif not self._skip:
            self.parts.append(data)


def load_patterns(path: Path) -> list:
    """[(kind, field, compiled regex)] in file order; raise ValueError naming a bad line."""
    rows = []
    for n, raw in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        parts = raw.split("\t")
        if len(parts) != 3 or not parts[0] or parts[1] not in FIELDS or not parts[2]:
            raise ValueError(f"{path}:{n}: want kind<TAB>url|title|text<TAB>regex")
        try:
            rows.append((parts[0], parts[1], re.compile(parts[2], re.IGNORECASE)))
        except re.error as e:
            raise ValueError(f"{path}:{n}: bad regex: {e}") from None
    if not rows:
        raise ValueError(f"{path}: no patterns")
    return rows


def snapshot_fields(snap: dict) -> dict:
    """Normalise the input to {url, title, text}; raise ValueError on a wrong shape."""
    if not isinstance(snap, dict):
        raise ValueError("input is not a JSON object")
    for key in ("url", "title", "text", "html"):
        if key in snap and not isinstance(snap[key], str):
            raise ValueError(f"{key} is not a string")
    fields = {"url": snap.get("url", ""), "title": snap.get("title", ""), "text": snap.get("text", "")}
    if "text" not in snap and "html" in snap:
        p = _Text()
        p.feed(snap["html"])
        p.close()
        fields["text"] = " ".join(" ".join(p.parts).split())
        fields["title"] = fields["title"] or " ".join(p.title.split())
    return fields


def host_of(url: str):
    try:
        return urlsplit(url).hostname or None
    except ValueError:
        return None


def check(fields: dict, patterns: list) -> dict:
    for kind, field, rx in patterns:
        if rx.search(fields[field]):
            return {"challenge": True, "kind": kind, "host": host_of(fields["url"])}
    return {"challenge": False, "kind": None, "host": host_of(fields["url"])}


def main(argv: list) -> int:
    path = DEFAULT_PATTERNS
    if argv[:1] == ["--patterns"] and len(argv) == 2:
        path = Path(argv[1])
    elif argv:
        print(__doc__.strip().splitlines()[-1], file=sys.stderr)
        return 2
    try:
        patterns = load_patterns(path)
        fields = snapshot_fields(json.loads(sys.stdin.read()))
    except (OSError, ValueError) as e:  # json.JSONDecodeError is a ValueError
        print(f"challenge-check: {e}", file=sys.stderr)
        return 2
    result = check(fields, patterns)
    print(json.dumps(result))
    return 3 if result["challenge"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
