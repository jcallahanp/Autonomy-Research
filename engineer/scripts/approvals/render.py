"""One-line texts for John: a T1 line, a T2 hard-gate prompt, a reminder (digest.py and approvals/telegram.py).

Every line names its project, so with item numbers global across projects John sees whose item it is.
"""


def one_line(text) -> str:
    """Collapse whitespace and control characters so an item is exactly one line."""
    text = "".join(c if c.isprintable() else " " for c in str(text))
    return " ".join(text.split())


def _what(it: dict) -> str:
    """`<project>: <text>`: every line that names an item names its project."""
    project = f"{one_line(it['project'])}: " if it.get("project") else ""
    return project + one_line(it.get("text", ""))


def _head(it: dict) -> str:
    return f"{it['item']}. {_what(it)}"


def line(it: dict) -> str:
    """One T1 digest line."""
    n = it["item"]
    return f'{_head(it)} (default: {one_line(it.get("default", "no"))}). Reply "{n} y" or "{n} n".'


def render_t2(item: dict) -> str:
    """The separate hard-gate message; no reply means no."""
    n = item["item"]
    return (f"HARD GATE {n}: {_what(item)}\n"
            f"To approve, reply exactly: CONFIRM {n} {one_line(item['phrase'])}\n"
            "No reply means no.")


def render_reminder(item: dict) -> str:
    """A reminder for one open item (T1 line or T2 prompt)."""
    return "Reminder: " + (render_t2(item) if item.get("tier") == "T2" else line(item))
