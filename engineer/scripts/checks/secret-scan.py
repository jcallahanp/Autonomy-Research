"""Scan files, or the lines a diff adds, for secret-shaped text. Never prints the match.

Usage: secret-scan.py FILE...  |  secret-scan.py --diff GITDIR BASE HEAD
Prints `path:line kind [REDACTED]` per hit; exit 1 on any hit, 2 on bad input.
Patterns follow tests/engineer/eng/test_static.sh plus sk- keys and bearer tokens. Each is written so it does
not match its own source (character classes split the literal prefixes). gitleaks --redact (scanners.py)
runs beside it on the droplet with the same output shape.
"""
import re
import subprocess
import sys
from pathlib import Path

import checklib

PATTERNS = [
    ("anthropic_key", re.compile(r"s[k]-ant-")),
    ("github_token", re.compile(r"gh[p]_[A-Za-z0-9]{20,}")),
    ("github_pat", re.compile(r"githu[b]_pat_")),
    ("slack_token", re.compile(r"xo[x][baprs]-")),
    ("aws_key", re.compile(r"AKI[A][0-9A-Z]{16}")),
    ("telegram_token", re.compile(r"[0-9]{8,10}:[A-Za-z0-9_-]{35}")),
    ("private_key", re.compile(r"BEGI[N] [A-Z ]*PRIVATE KEY")),
    ("sk_key", re.compile(r"s[k]-[A-Za-z0-9]{20,}")),
    ("bearer", re.compile(r"Beare[r] [A-Za-z0-9._-]{20,}")),
]


def kinds(text: str) -> list:
    """Names of the patterns found in one line."""
    return [name for name, rx in PATTERNS if rx.search(text)]


def scan_lines(items):
    """items: (path, line number, text). Yield output lines."""
    for path, n, text in items:
        for kind in kinds(text):
            yield f"{path}:{n} {kind} [REDACTED]"


def file_lines(names):
    for name in names:
        p = Path(name)
        if not p.is_file():
            continue
        data = p.read_bytes()
        if b"\0" in data[:8192]:
            continue
        for n, text in enumerate(data.decode("utf-8", "replace").splitlines(), 1):
            yield name, n, text


def main(argv) -> int:
    try:
        if argv[:1] == ["--diff"]:
            if len(argv) != 4:
                raise ValueError("usage: --diff GITDIR BASE HEAD")
            base, head = checklib.check_sha(argv[2]), checklib.check_sha(argv[3])
            lines = list(scan_lines(checklib.added_lines(argv[1], base, head)))
        else:
            if not argv or any(a.startswith("-") for a in argv):
                raise ValueError("usage: secret-scan.py FILE... | --diff GITDIR BASE HEAD")
            lines = list(scan_lines(file_lines(argv)))
    except (ValueError, subprocess.CalledProcessError) as exc:
        print(f"secret-scan: {exc}", file=sys.stderr)
        return 2
    for line in lines:
        print(line)
    return 1 if lines else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
