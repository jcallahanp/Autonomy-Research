"""Host allowlists (egress, install, browser).

A pattern is an exact host or `*.suffix`, which matches any deeper subdomain of suffix but not
suffix itself. Matching is case-insensitive and ignores a trailing dot. One pattern per line;
`#` starts a comment; anything after the first field on a line is a note.
"""
import re
from pathlib import Path

_LABEL = r"[a-z0-9_](?:[a-z0-9_-]{0,61}[a-z0-9_])?"
_HOST = re.compile(rf"^{_LABEL}(?:\.{_LABEL})*$")


def _norm(host: str) -> str:
    return host.strip().lower().rstrip(".")


def check_pattern(pattern: str) -> str:
    """The normalised pattern; raise ValueError for `*`, a one-label suffix or a malformed host."""
    p = _norm(pattern)
    if p.startswith("*."):
        suffix = p[2:]
        if "." not in suffix:
            raise ValueError(f"pattern too broad: {pattern!r}")
    else:
        suffix = p
    if not _HOST.match(suffix):
        raise ValueError(f"not a host pattern: {pattern!r}")
    return p


def load(path: Path) -> list:
    patterns = []
    for n, raw in enumerate(Path(path).read_text().splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        try:
            patterns.append(check_pattern(line.split()[0]))
        except ValueError as e:
            raise ValueError(f"{path}:{n}: {e}") from None
    return patterns


def allowed(host: str, patterns: list) -> bool:
    h = _norm(host or "")
    if not h:
        return False
    for raw in patterns:
        p = _norm(raw)
        if p.startswith("*."):
            if h.endswith(p[1:]) and h != p[2:]:
                return True
        elif h == p:
            return True
    return False
