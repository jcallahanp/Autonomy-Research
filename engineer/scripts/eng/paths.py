"""Protected-path rules (templates/protected-paths.txt).

Sections: [always] paths may never be written; [existing] paths may not be changed once they exist.
Patterns are anchored at the project root: `**` spans directories, `*` and `?` do not.
"""
import posixpath
import re
from functools import lru_cache
from pathlib import Path

SECTIONS = ("always", "existing")
OUTSIDE = "outside project"


def load(path: Path) -> dict:
    """Return {"always": [...], "existing": [...]}; raise ValueError on a line outside a known section."""
    rules = {s: [] for s in SECTIONS}
    section = None
    for n, raw in enumerate(Path(path).read_text().splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1]
            if section not in rules:
                raise ValueError(f"{path}:{n}: unknown section {line}")
        elif section is None:
            raise ValueError(f"{path}:{n}: pattern before any section")
        else:
            rules[section].append(line)
    return rules


@lru_cache(maxsize=512)
def _regex(pattern: str) -> re.Pattern:
    out, i = [], 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif pattern.startswith("**", i):
            out.append(".*")
            i += 2
        elif pattern[i] == "*":
            out.append("[^/]*")
            i += 1
        elif pattern[i] == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(pattern[i]))
            i += 1
    return re.compile("".join(out))


def match(rel: str, pattern: str) -> bool:
    """True when the project-relative path rel matches pattern."""
    return _regex(pattern).fullmatch(rel) is not None


def normalise(rel: str):
    """The clean project-relative path, or None when rel is absolute or escapes the project."""
    if not rel or rel.startswith("/") or "\0" in rel:
        return None
    clean = posixpath.normpath(rel)
    if clean == ".." or clean.startswith("../"):
        return None
    return clean


def protected(rel: str, rules: dict, exists: bool):
    """The first matching pattern, "outside project", or None when rel may be written."""
    clean = normalise(rel)
    if clean is None:
        return OUTSIDE
    for pattern in rules.get("always", []):
        if match(clean, pattern):
            return pattern
    if exists:
        for pattern in rules.get("existing", []):
            if match(clean, pattern):
                return pattern
    return None
