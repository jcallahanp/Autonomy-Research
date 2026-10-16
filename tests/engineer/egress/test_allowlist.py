"""allowlist.py check and the mitmproxy add-on's logic, without mitmproxy installed (Task 4)."""
import importlib.util
import py_compile
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
EGRESS = REPO / "engineer" / "scripts" / "egress"
sys.path.insert(0, str(REPO / "engineer" / "scripts"))
from eng import hosts  # noqa: E402

PATTERNS = ["api.anthropic.com", "*.claude.ai", "github.com"]
HOSTS = ["api.anthropic.com", "API.Anthropic.com.", "x.claude.ai", "a.b.claude.ai", "claude.ai",
         "github.com", "api.github.com", "evil.com", "github.com.evil.com", "", "10.0.0.1",
         "anthropic.com", "xclaude.ai"]


def fake_mitmproxy():
    """Install a minimal fake `mitmproxy` package; return its ctx.options namespace."""
    pkg = types.ModuleType("mitmproxy")
    http = types.ModuleType("mitmproxy.http")
    exc = types.ModuleType("mitmproxy.exceptions")

    class Response:
        @staticmethod
        def make(status_code=200, content=b"", headers=None):
            return types.SimpleNamespace(status_code=status_code, content=content, headers=headers)

    class OptionsError(Exception):
        pass

    http.Response, exc.OptionsError = Response, OptionsError
    options = types.SimpleNamespace()
    pkg.http, pkg.exceptions, pkg.ctx = http, exc, types.SimpleNamespace(options=options)
    sys.modules.update({"mitmproxy": pkg, "mitmproxy.http": http, "mitmproxy.exceptions": exc})
    return options


def load_addon():
    spec = importlib.util.spec_from_file_location("mitm_addon_under_test", EGRESS / "mitm_addon.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def flow(host, port=443, method="CONNECT"):
    return types.SimpleNamespace(request=types.SimpleNamespace(host=host, port=port, method=method),
                                 response=None)


class Loader:
    def __init__(self):
        self.options = {}

    def add_option(self, name, typespec, default, help):
        self.options[name] = default


class CheckCli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.list = Path(self.tmp.name) / "egress.txt"
        self.list.write_text("# test list\napi.anthropic.com\n*.claude.ai  # note\n")

    def tearDown(self):
        self.tmp.cleanup()

    def check(self, *args):
        return subprocess.run([sys.executable, str(EGRESS / "allowlist.py"), *args],
                              capture_output=True, text=True).returncode

    def test_allowed_and_denied(self):
        self.assertEqual(self.check("check", str(self.list), "api.anthropic.com"), 0)
        self.assertEqual(self.check("check", str(self.list), "x.claude.ai"), 0)
        self.assertEqual(self.check("check", str(self.list), "claude.ai"), 1)
        self.assertEqual(self.check("check", str(self.list), "evil.com"), 1)

    def test_usage_and_bad_list_exit_2(self):
        self.assertEqual(self.check("check", str(self.list)), 2)
        self.assertEqual(self.check("nope", str(self.list), "x"), 2)
        self.assertEqual(self.check("check", str(self.list) + ".missing", "x"), 2)
        self.list.write_text("*\n")
        self.assertEqual(self.check("check", str(self.list), "evil.com"), 2)


class Addon(unittest.TestCase):
    def setUp(self):
        self.saved = {k: v for k, v in sys.modules.items() if k.startswith("mitmproxy")}
        self.options = fake_mitmproxy()
        self.tmp = tempfile.TemporaryDirectory()
        tmp = Path(self.tmp.name)
        self.list, self.log = tmp / "egress.txt", tmp / "log" / "egress-denied.log"
        self.list.write_text("\n".join(PATTERNS) + "\n")
        self.log.parent.mkdir()
        self.mod = load_addon()
        self.addon = self.mod.addons[0]
        loader = Loader()
        self.addon.load(loader)
        self.assertIn("engineer_allowlist", loader.options)
        self.options.engineer_allowlist = str(self.list)
        self.options.engineer_denied_log = str(self.log)
        self.addon.configure({"engineer_allowlist", "engineer_denied_log"})

    def tearDown(self):
        for k in [k for k in sys.modules if k.startswith("mitmproxy")]:
            del sys.modules[k]
        sys.modules.update(self.saved)
        self.tmp.cleanup()

    def test_compiles_without_mitmproxy(self):
        with tempfile.TemporaryDirectory() as d:
            py_compile.compile(str(EGRESS / "mitm_addon.py"), cfile=str(Path(d) / "a.pyc"),
                               doraise=True)

    def test_decide_matches_eng_hosts(self):
        for h in HOSTS:
            with self.subTest(host=h):
                self.assertEqual(self.mod.decide(h, PATTERNS), hosts.allowed(h, PATTERNS))

    def test_connect_denied_gets_403_and_log_line(self):
        f = flow("evil.com")
        self.addon.http_connect(f)
        self.assertEqual(f.response.status_code, 403)
        line = self.log.read_text().splitlines()[-1]
        ts, host = line.split(" ")
        self.assertRegex(ts, r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")
        self.assertEqual(host, "evil.com")

    def test_connect_allowed_passes(self):
        f = flow("x.claude.ai")
        self.addon.http_connect(f)
        self.assertIsNone(f.response)
        self.assertFalse(self.log.exists())

    def test_plain_request_checked_too(self):
        f = flow("github.com.evil.com", 80, "GET")
        self.addon.request(f)
        self.assertEqual(f.response.status_code, 403)
        g = flow("github.com", 80, "GET")
        self.addon.request(g)
        self.assertIsNone(g.response)

    def test_connect_only_to_443(self):
        for port in (22, 80, 8443, 25):
            with self.subTest(port=port):
                f = flow("github.com", port)
                self.addon.http_connect(f)
                self.assertEqual(f.response.status_code, 403)
        self.assertEqual(self.log.read_text().splitlines()[-1].split(" ")[1], "github.com:25")

    def test_plain_http_only_to_80(self):
        for port in (443, 8080, 22):
            with self.subTest(port=port):
                f = flow("github.com", port, "GET")
                self.addon.request(f)
                self.assertEqual(f.response.status_code, 403)

    def test_decide_port_rule(self):
        self.assertTrue(self.mod.decide("github.com", PATTERNS, 443, connect=True))
        self.assertFalse(self.mod.decide("github.com", PATTERNS, 80, connect=True))
        self.assertTrue(self.mod.decide("github.com", PATTERNS, 80, connect=False))
        self.assertFalse(self.mod.decide("github.com", PATTERNS, 443, connect=False))
        self.assertFalse(self.mod.decide("evil.com", PATTERNS, 443, connect=True))

    def test_log_line_cannot_be_forged(self):
        self.addon.http_connect(flow("evil.com\n2026-01-01T00:00:00Z ok.com"))
        lines = self.log.read_text().splitlines()
        self.assertEqual(len(lines), 1)
        self.assertEqual(len(lines[0].split(" ")), 2)

    def test_unwritable_log_still_denies(self):
        self.options.engineer_denied_log = str(Path(self.tmp.name) / "no" / "such" / "dir.log")
        self.addon.configure({"engineer_denied_log"})
        f = flow("evil.com")
        self.addon.http_connect(f)
        self.assertEqual(f.response.status_code, 403)

    def test_bad_list_refuses_to_start(self):
        self.list.write_text("*\n")
        with self.assertRaises(sys.modules["mitmproxy.exceptions"].OptionsError):
            self.addon.configure({"engineer_allowlist"})

    def test_no_list_denies_everything(self):
        self.options.engineer_allowlist = ""
        self.addon.configure({"engineer_allowlist"})
        f = flow("api.anthropic.com")
        self.addon.http_connect(f)
        self.assertEqual(f.response.status_code, 403)


if __name__ == "__main__":
    unittest.main()
