#!/usr/bin/env python3
"""Check a host against an egress list (eng.hosts patterns).

Usage: allowlist.py check FILE HOST
Exit 0 allowed, 1 denied, 2 usage error or a list that does not load.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from eng import hosts  # noqa: E402


def main(argv: list) -> int:
    if len(argv) != 3 or argv[0] != "check":
        print("usage: allowlist.py check FILE HOST", file=sys.stderr)
        return 2
    try:
        patterns = hosts.load(Path(argv[1]))
    except (OSError, ValueError) as e:
        print(f"allowlist: {e}", file=sys.stderr)
        return 2
    return 0 if hosts.allowed(argv[2], patterns) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
