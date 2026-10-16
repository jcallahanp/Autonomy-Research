#!/usr/bin/env python3
"""PreToolUse: run the guards in order; the first deny reason goes to stderr and exits 2.

Any error (bad input, a missing list, a guard raising) also exits 2: the hook fails closed.
Contract: https://code.claude.com/docs/en/hooks (PreToolUse; exit 2 blocks the call and feeds
stderr to Claude as the reason).
"""
import importlib
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))


def main() -> int:
    try:
        import hookctx
        import guards
        event = hookctx.read_event()
        ctx = hookctx.load(event)
        for name in guards.ORDER:
            reason = importlib.import_module(f"guards.{name}").check(event, ctx)
            if reason:
                print(f"engineer guard ({name}): {reason}", file=sys.stderr)
                return 2
    except Exception as e:  # noqa: BLE001 - fail closed on anything
        print(f"engineer guard error: {type(e).__name__}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
