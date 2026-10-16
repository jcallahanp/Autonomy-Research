"""The night window (crosses midnight, local time zone) and when the morning digest is due."""
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo


def _hm(text: str) -> time:
    h, m = text.split(":")
    return time(int(h), int(m))


def in_window(now_utc: datetime, start: str, end: str, tz: str) -> bool:
    """True when now, in tz, is in [start, end); a start after end means the window crosses midnight."""
    t = now_utc.astimezone(ZoneInfo(tz)).time().replace(tzinfo=None)
    s, e = _hm(start), _hm(end)
    if s <= e:
        return s <= t < e
    return t >= s or t < e


def night_key(now_utc: datetime, start: str, tz: str) -> str:
    """Local date on which the current (or most recent) night window started."""
    local = now_utc.astimezone(ZoneInfo(tz))
    day = local.date() if local.time().replace(tzinfo=None) >= _hm(start) else local.date() - timedelta(days=1)
    return day.isoformat()


def local_date(now_utc: datetime, tz: str) -> str:
    return now_utc.astimezone(ZoneInfo(tz)).date().isoformat()


def digest_due(now_utc: datetime, last_digest_date: str | None, digest_at: str, tz: str) -> bool:
    """True once local time passes digest_at and no digest was sent on this local date."""
    local = now_utc.astimezone(ZoneInfo(tz))
    return local.time().replace(tzinfo=None) >= _hm(digest_at) and local.date().isoformat() != last_digest_date
