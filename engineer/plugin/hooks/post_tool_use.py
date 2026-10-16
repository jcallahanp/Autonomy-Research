#!/usr/bin/env python3
"""PostToolUse (Edit|Write|MultiEdit): a `.mmd` file must be a flowchart, graph or sequenceDiagram.

C4 diagrams are drawn as flowcharts (system-map rule). Exit 2 shows stderr to Claude; the write
already happened, so Claude fixes the file. Contract: https://code.claude.com/docs/en/hooks.
"""
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

ALLOWED = re.compile(r"^(flowchart|graph|sequenceDiagram)\b")
C4 = re.compile(r"C4")


def first_line(text: str) -> str:
    """The first line that is not blank, a `%%` comment or YAML front matter."""
    lines = text.splitlines()
    i = 0
    if lines and lines[0].strip() == "---":
        i = next((j + 1 for j in range(1, len(lines)) if lines[j].strip() == "---"), len(lines))
    for line in lines[i:]:
        s = line.strip()
        if s and not s.startswith("%%"):
            return s
    return ""


def reason(path: Path, fallback: str):
    try:
        text = path.read_text()
    except OSError:
        text = fallback
    line = first_line(text)
    if C4.search(line):
        return f"{path.name}: C4 diagram types are not allowed; draw C4 levels as a flowchart"
    if not ALLOWED.match(line):
        return f"{path.name}: the first line must start with flowchart, graph or sequenceDiagram"
    return None


def main() -> int:
    try:
        import hookctx
        event = hookctx.read_event()
        path = hookctx.tool_path(event)
        if not path or not path.endswith(".mmd"):
            return 0
        ti = event.get("tool_input") or {}
        msg = reason(hookctx.resolve(path, Path(event.get("cwd") or ".")), str(ti.get("content") or ""))
    except Exception as e:  # noqa: BLE001
        print(f"post_tool_use: {type(e).__name__}", file=sys.stderr)
        return 0
    if msg:
        print(msg, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
