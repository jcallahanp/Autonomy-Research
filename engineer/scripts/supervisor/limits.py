"""Classify a run's output as a session or weekly usage limit and parse the reset time.

PROVISIONAL: these patterns are guesses at the headless usage-limit text. Spike SP07 (setup day)
captures the real text, exit code and result.subtype; replace the patterns and the synthetic test
fixtures with it.
"""
import re
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

_WEEKLY = re.compile(r"weekly limit|weekly usage limit|opus limit reached", re.I)
_SESSION = re.compile(r"usage limit reached|session limit|5-hour limit|hit your limit", re.I)
_EPOCH = re.compile(r"limit reached\|(\d{10})\b", re.I)
_CLOCK = re.compile(r"resets\s+(?:at\s+)?(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b(?:\s*\(([A-Za-z_]+/[A-Za-z_/]+)\))?",
                    re.I)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _clock_reset(m, now: datetime, tz: str) -> str:
    hour = int(m.group(1)) % 12 + (12 if m.group(3).lower() == "pm" else 0)
    zone = ZoneInfo(m.group(4) or tz)
    local = now.astimezone(zone)
    at = local.replace(hour=hour, minute=int(m.group(2) or 0), second=0, microsecond=0)
    if at <= local:
        at = (at.replace(tzinfo=None) + timedelta(days=1)).replace(tzinfo=zone)
    return _iso(at)


def classify(text: str | None, now: datetime | None = None, tz: str = "America/New_York") -> dict:
    """{"kind": "session"|"weekly"|None, "reset_at": ISO-8601 UTC | None}."""
    text = text or ""
    now = now or datetime.now(timezone.utc)
    if _WEEKLY.search(text):
        kind = "weekly"
    elif _SESSION.search(text):
        kind = "session"
    else:
        return {"kind": None, "reset_at": None}
    reset_at = None
    if kind == "session":
        m = _EPOCH.search(text)
        if m:
            reset_at = _iso(datetime.fromtimestamp(int(m.group(1)), timezone.utc))
        else:
            m = _CLOCK.search(text)
            if m:
                try:
                    reset_at = _clock_reset(m, now, tz)
                except (KeyError, ValueError):
                    reset_at = None
    return {"kind": kind, "reset_at": reset_at}
