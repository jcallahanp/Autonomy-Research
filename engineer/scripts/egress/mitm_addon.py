"""mitmproxy add-on: allow only hosts on the engineer egress list.

Loaded by engineer-egress-proxy.service:
  mitmdump --listen-host 127.0.0.1 --listen-port 3128 --ignore-hosts '.*' \
    -s /opt/engineer/scripts/egress/mitm_addon.py --set engineer_allowlist=/etc/engineer/egress.txt
With --ignore-hosts '.*' TLS is never intercepted; the add-on judges the CONNECT host and port
(port 443 only) and any plain-HTTP request (port 80 only). A denied request gets 403 and a line
`<ISO-8601 UTC> <host>` (`<host>:<port>` when only the port is wrong) in engineer_denied_log. A list that does not load stops the proxy
(fail closed); no list at all denies everything. mitmproxy is imported only inside functions,
so this file compiles and its logic is testable without mitmproxy installed.
"""
import re
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from eng import hosts  # noqa: E402

DENIED_LOG = "/var/log/engineer/egress-denied.log"
CONNECT_PORT, PLAIN_PORT = 443, 80
_UNSAFE = re.compile(r"[^A-Za-z0-9._:\[\]-]")


def decide(host: str, patterns: list, port: int = None, connect: bool = True) -> bool:
    """True when host may be reached (same rule as eng.hosts.allowed) on port: a CONNECT tunnel
    only to 443, a plain-HTTP request only to 80. port None judges the host alone."""
    if not hosts.allowed(host, patterns):
        return False
    return port is None or port == (CONNECT_PORT if connect else PLAIN_PORT)


def deny_line(host: str, now: float = None) -> str:
    """One log line; the host is reduced to safe characters so it cannot forge a line."""
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now))
    safe = _UNSAFE.sub("?", host or "")[:253] or "-"
    return f"{ts} {safe}\n"


class Allowlist:
    def __init__(self):
        self.patterns = []
        self.log_path = DENIED_LOG

    def load(self, loader):
        loader.add_option("engineer_allowlist", str, "",
                          "Egress list file (eng.hosts patterns); empty denies everything.")
        loader.add_option("engineer_denied_log", str, DENIED_LOG,
                          "File that receives one line per denied host.")

    def configure(self, updated):
        from mitmproxy import ctx, exceptions
        if "engineer_denied_log" in updated:
            self.log_path = ctx.options.engineer_denied_log
        if "engineer_allowlist" in updated:
            path = ctx.options.engineer_allowlist
            self.patterns = []
            if path:
                try:
                    self.patterns = hosts.load(Path(path))
                except (OSError, ValueError) as e:
                    raise exceptions.OptionsError(f"engineer_allowlist: {e}") from None

    def _judge(self, flow, connect):
        host, port = flow.request.host, flow.request.port
        if decide(host, self.patterns, port, connect):
            return
        if hosts.allowed(host, self.patterns):
            host = f"{host}:{port}"
        from mitmproxy import http
        flow.response = http.Response.make(
            403, b"engineer egress: host not on the allowlist\n", {"Content-Type": "text/plain"})
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(deny_line(host))
        except OSError:
            pass  # the deny stands even when the log cannot be written

    def http_connect(self, flow):
        self._judge(flow, True)

    def request(self, flow):
        if flow.response is None:
            self._judge(flow, getattr(flow.request, "method", "") == "CONNECT")


addons = [Allowlist()]
