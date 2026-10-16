#!/usr/bin/env python3
"""StopFailure and Notification: append one line to SPOOL_DIR/<session_id>.jsonl; always exit 0.

Line: {ts, session_id, hook_event_name, project, task_id, detail}; the supervisor's spool.ingest
moves it into events.jsonl. Contract: https://code.claude.com/docs/en/hooks (StopFailure adds
`error`, `error_details`; Notification adds `message`, `title`, `notification_type`; both
ignore the exit code).
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

FIELDS = ("error", "error_details", "notification_type", "title", "message")
MAX_TEXT = 500


def main() -> int:
    try:
        import hookctx
        event = hookctx.read_event()
        ctx = hookctx.load(event)
        detail = {k: str(event[k])[:MAX_TEXT] for k in FIELDS if event.get(k) is not None}
        hookctx.spool(ctx.conf, event.get("session_id"), hookctx.tap_record(event, ctx, detail))
    except Exception as e:  # noqa: BLE001 - a tap must never break the session
        print(f"event_tap: {type(e).__name__}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
