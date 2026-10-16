"""The two egress lists (Task 4): load, runtime is a subset of install, no `*`, no duplicates."""
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "engineer" / "scripts"))
from eng import hosts  # noqa: E402

TEMPLATES = REPO / "engineer" / "templates"
INSTALL = TEMPLATES / "egress-install.txt"
RUNTIME = TEMPLATES / "egress-allowlist.txt"

RUNTIME_HOSTS = {
    "api.anthropic.com", "claude.ai", "*.claude.ai", "github.com", "api.github.com",
    "api.telegram.org", "hc-ping.com", "api.uptimerobot.com", "api.attio.com", "app.attio.com",
    "*.attio.com", "app.clay.com", "*.clay.com", "accounts.google.com", "api.osv.dev",
    "api.deps.dev", "api.securityscorecards.dev", "registry.modelcontextprotocol.io",
    "semgrep.dev",  # the audit's semgrep fetches its registry rules (osv-scanner uses api.osv.dev)
}
INSTALL_EXTRA = {
    "registry.npmjs.org", "github.com", "objects.githubusercontent.com", "codeload.github.com",
    "pypi.org", "files.pythonhosted.org", "accounts.google.com", "dash.cloudflare.com",
    # GitHub release downloads redirect here (checked 2026-10-16 with curl -I on the gitleaks
    # and osv-scanner release URLs), so bootstrap.sh needs it.
    "release-assets.githubusercontent.com",
}


class Lists(unittest.TestCase):
    def test_both_load(self):
        self.assertTrue(hosts.load(INSTALL))
        self.assertTrue(hosts.load(RUNTIME))

    def test_runtime_list_is_the_plan_list(self):
        self.assertEqual(set(hosts.load(RUNTIME)), RUNTIME_HOSTS)

    def test_install_is_runtime_plus_install_hosts(self):
        self.assertEqual(set(hosts.load(INSTALL)), RUNTIME_HOSTS | INSTALL_EXTRA)

    def test_every_runtime_host_in_install(self):
        install = set(hosts.load(INSTALL))
        for h in hosts.load(RUNTIME):
            self.assertIn(h, install)

    def test_no_star_and_no_duplicates(self):
        for path in (INSTALL, RUNTIME):
            with self.subTest(path=path.name):
                lines = [l.split("#", 1)[0].strip() for l in path.read_text().splitlines()]
                lines = [l for l in lines if l]
                self.assertNotIn("*", lines)
                self.assertEqual(len(lines), len(set(lines)))

    def test_groups_sorted_in_domain_order(self):
        # A group is a run of host lines with no blank or comment line between them; within it
        # hosts sort by reversed labels (github.com, then api.github.com), so families stay together.
        for path in (INSTALL, RUNTIME):
            groups, cur = [], []
            for line in path.read_text().splitlines() + [""]:
                h = line.split("#", 1)[0].strip()
                if h and not line.lstrip().startswith("#"):
                    cur.append(h)
                elif cur:
                    groups, cur = groups + [cur], []
            for g in groups:
                with self.subTest(path=path.name, group=g[0]):
                    self.assertEqual(g, sorted(g, key=lambda h: h.lower().split(".")[::-1]))

    def test_header_says_provisional(self):
        for path in (INSTALL, RUNTIME):
            head = path.read_text().split("\n\n", 1)[0].lower()
            self.assertIn("provisional", head)
            self.assertIn("n8n", head)


if __name__ == "__main__":
    unittest.main()
