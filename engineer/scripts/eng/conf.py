"""Parse <root>/etc/engineer.conf the way bash sources it, refusing anything bash would expand."""
import re
from pathlib import Path

_KEY = r"[A-Z_][A-Z0-9_]*"
# Quoted: no ", $, backtick or backslash inside. Plain: no whitespace or shell metacharacter.
_LINE = re.compile(rf'^({_KEY})=(?:"([^"$`\\]*)"|([^\s"\'$`\\#;&|<>(){{}}~*?\[\]!]*))$')


def parse(text: str) -> dict:
    """Return {KEY: VALUE}; raise ValueError naming the first line that is not KEY=VALUE."""
    values = {}
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = _LINE.match(line)
        if not m:
            raise ValueError(f"engineer.conf line {n}: not KEY=VALUE: {line[:60]!r}")
        values[m.group(1)] = m.group(2) if m.group(2) is not None else m.group(3)
    return values


def load(root: Path) -> dict:
    """Read <root>/etc/engineer.conf."""
    return parse((Path(root) / "etc" / "engineer.conf").read_text())
