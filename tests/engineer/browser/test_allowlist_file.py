"""templates/browser-allowlist.txt loads with eng.hosts and allows only the expected apps."""
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "engineer" / "scripts"))
from eng import hosts  # noqa: E402

ALLOWLIST = REPO / "engineer" / "templates" / "browser-allowlist.txt"


class AllowlistFile(unittest.TestCase):
    def setUp(self):
        self.patterns = hosts.load(ALLOWLIST)

    def test_expected_hosts_allowed(self):
        for h in ("accounts.google.com", "app.attio.com", "api.attio.com", "app.clay.com", "x.clay.com"):
            self.assertTrue(hosts.allowed(h, self.patterns), h)

    def test_other_hosts_denied(self):
        for h in ("example.com", "attio.com.evil.example", "google.com", "mail.google.com", "clay.com.example"):
            self.assertFalse(hosts.allowed(h, self.patterns), h)

    def test_exact_entries(self):
        self.assertEqual(sorted(self.patterns),
                         sorted(["accounts.google.com", "app.attio.com", "*.attio.com", "app.clay.com", "*.clay.com"]))

    def test_n8n_comment(self):
        text = ALLOWLIST.read_text()
        self.assertIn("n8n", text)
        self.assertIn("setup day", text)


if __name__ == "__main__":
    unittest.main()
