"""Browser: Playwright may open only http(s) URLs whose host is in templates/browser-allowlist.txt.

Applies to `mcp__*playwright*__browser_navigate` and any other Playwright browser tool given a
`url` (browser_tabs new). A missing allowlist denies every navigation (SP64 confirms tool names).
"""
import re
from urllib.parse import urlsplit

from eng import hosts

TOOL = re.compile(r"^mcp__.*playwright.*__browser_[a-z_]+$")
NAVIGATE = re.compile(r"__browser_navigate$")
BAD_CHARS = re.compile(r"[\\\s\x00-\x1f\x7f]")


def _reason(url: str, ctx):
    if not url or BAD_CHARS.search(url):
        return "browser: URL is empty or has a backslash, space or control character"
    if not re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", url):
        url = "https://" + url
    parts = urlsplit(url)
    if parts.scheme.lower() not in ("http", "https"):
        return f"browser: scheme {parts.scheme!r} is not allowed (http and https only)"
    allow = ctx.root / "templates" / "browser-allowlist.txt"
    if not allow.is_file():
        return "browser: templates/browser-allowlist.txt is missing, so every navigation is denied"
    host = parts.hostname or ""
    if not hosts.allowed(host, hosts.load(allow)):
        return f"browser: host {host!r} is not in browser-allowlist.txt"
    return None


def check(event: dict, ctx):
    name = str(event.get("tool_name") or "")
    if not TOOL.match(name):
        return None
    ti = event.get("tool_input") or {}
    if "url" in ti or NAVIGATE.search(name):
        return _reason(str(ti.get("url") or ""), ctx)
    return None
