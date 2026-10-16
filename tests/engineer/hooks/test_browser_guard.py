"""Browser guard: Playwright navigation only to allowlisted hosts over http(s)."""
import unittest

from hookfix import HookCase

NAV = "mcp__plugin_engineer_playwright__browser_navigate"
TABS = "mcp__plugin_engineer_playwright__browser_tabs"


class BrowserGuardTest(HookCase):
    def setUp(self):
        super().setUp()
        self.allow = self.root / "templates" / "browser-allowlist.txt"
        self.write(self.allow, "# fixture\napp.attio.com\n*.clay.com\n")

    def nav(self, url, tool=NAV):
        return self.pre(tool, {"url": url})

    def test_allowlisted_host_allowed(self):
        self.assertAllowed(self.nav("https://app.attio.com/x"))
        self.assertAllowed(self.nav("https://api.clay.com/y?q=1"))
        self.assertAllowed(self.nav("https://APP.attio.com./x"))

    def test_other_host_denied(self):
        urls = ("https://evil.example", "https://clay.com/", "https://app.attio.com.evil.example/",
                    "https://app.attio.com@evil.example/", "https://evil.example\\@app.attio.com/",
                    "https://evil.example/https://app.attio.com", "app.attio.com.evil.example")
        for url, r in self.many(self.nav, urls):
            with self.subTest(url=url):
                self.assertDenied(r, "browser")

    def test_bad_schemes_denied(self):
        urls = ("file:///etc/passwd", "chrome://settings", "data:text/html,hi",
                "javascript:alert(1)", "view-source:https://app.attio.com/", "ftp://app.attio.com/")
        for url, r in self.many(self.nav, urls):
            with self.subTest(url=url):
                self.assertDenied(r, "browser")

    def test_missing_allowlist_denies_everything(self):
        self.allow.unlink()
        self.assertDenied(self.nav("https://app.attio.com/x"), "browser")

    def test_tabs_with_url_checked(self):
        self.assertDenied(self.pre(TABS, {"action": "new", "url": "https://evil.example"}), "browser")
        self.assertAllowed(self.pre(TABS, {"action": "new", "url": "https://app.attio.com/"}))
        self.assertAllowed(self.pre(TABS, {"action": "list"}))

    def test_navigate_without_url_denied(self):
        self.assertDenied(self.pre(NAV, {}), "browser")

    def test_other_tools_untouched(self):
        self.assertAllowed(self.pre("mcp__plugin_engineer_playwright__browser_snapshot", {}))
        self.assertAllowed(self.pre("mcp__other__fetch", {"url": "https://evil.example"}))


if __name__ == "__main__":
    unittest.main()
