import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "engineer" / "scripts"))

from eng import hosts  # noqa: E402


class HostsTest(unittest.TestCase):
    def test_wildcard_matches_deeper_subdomains(self):
        self.assertTrue(hosts.allowed("app.attio.com", ["*.attio.com"]))
        self.assertTrue(hosts.allowed("a.b.attio.com", ["*.attio.com"]))

    def test_wildcard_not_bare_suffix(self):
        self.assertFalse(hosts.allowed("attio.com", ["*.attio.com"]))

    def test_no_lookalike(self):
        self.assertFalse(hosts.allowed("evilattio.com", ["*.attio.com"]))
        self.assertFalse(hosts.allowed("attio.com.evil.net", ["attio.com"]))

    def test_case_and_trailing_dot(self):
        self.assertTrue(hosts.allowed("API.Telegram.org.", ["api.telegram.org"]))
        self.assertTrue(hosts.allowed("api.telegram.org", ["API.Telegram.org."]))

    def test_empty(self):
        self.assertFalse(hosts.allowed("", ["*.attio.com"]))
        self.assertFalse(hosts.allowed("x.com", []))

    def test_load(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "allow.txt"
            f.write_text("# comment\n\nAPI.github.com.\n*.attio.com   # note\n")
            self.assertEqual(hosts.load(f), ["api.github.com", "*.attio.com"])
            for bad in ("*", "*.com", "a.*.com", "*foo.com", "http://x.com", "x.com/path", "a,b.com"):
                f.write_text(bad + "\n")
                with self.subTest(bad=bad), self.assertRaises(ValueError):
                    hosts.load(f)


if __name__ == "__main__":
    unittest.main()
