"""render-nft.py: nftables ruleset that limits the listed uids to named loopback ports (Task 4, R1-8)."""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SCRIPT = REPO / "engineer" / "scripts" / "egress" / "render-nft.py"
BOTH = ["--uid", "engineer=1001", "--uid", "supervisor=1002",
        "--lo", "engineer=3128,5900", "--lo", "supervisor=3128"]


def render(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


def rules(out):
    return [l.strip() for l in out.splitlines()
            if l.strip() and not l.strip().startswith(("#", "table", "delete", "chain", "type", "}"))]


class RenderNft(unittest.TestCase):
    def test_rules_in_order(self):
        r = render(*BOTH)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(rules(r.stdout), [
            'meta skuid { 1001, 1002 } meta l4proto { tcp, udp } th dport 53 log prefix "engineer-egress-dns " drop',
            'meta skuid { 1001, 1002 } oif "lo" ct state established,related accept',
            'meta skuid 1001 oif "lo" tcp dport { 3128, 5900 } accept',
            'meta skuid 1002 oif "lo" tcp dport { 3128 } accept',
            'meta skuid { 1001, 1002 } log prefix "engineer-egress-drop " drop',
        ])

    def test_no_blanket_loopback_accept(self):
        # R1-8: DNS through 127.0.0.53 (or any other loopback service) is not a way round the proxy.
        out = render(*BOTH).stdout
        for rule in rules(out):
            if rule.endswith("accept"):
                self.assertTrue("dport {" in rule or "established" in rule, rule)
        self.assertNotIn('oif "lo" accept', out)

    def test_other_uids_untouched(self):
        out = render(*BOTH).stdout
        self.assertIn("policy accept;", out)
        for rule in rules(out):
            self.assertRegex(rule, r"^meta skuid (\{ [0-9, ]+ \}|100[12]) ")

    def test_uid_without_ports_gets_no_new_loopback(self):
        out = render("--uid", "engineer=1001").stdout
        self.assertNotIn("tcp dport", out)
        self.assertIn('meta skuid { 1001 } log prefix "engineer-egress-drop " drop', out)

    def test_replaces_table_atomically(self):
        out = render(*BOTH).stdout
        self.assertLess(out.find("delete table inet engineer_egress"),
                        out.find("table inet engineer_egress {"))

    def test_custom_table(self):
        out = render("--uid", "engineer=1001", "--table", "eng_test").stdout
        self.assertIn("table inet eng_test {", out)
        self.assertNotIn("engineer_egress", out)

    def test_duplicate_uid_listed_once(self):
        out = render("--uid", "engineer=1001", "--uid", "engineer=1001", "--lo", "engineer=3128").stdout
        self.assertIn("meta skuid { 1001 } oif", out)
        self.assertEqual(out.count("tcp dport"), 1)

    def test_bad_input_exits_2(self):
        for args in (["--uid", "engineer=abc"], ["--uid", "engineer"], ["--uid", "root=0"],
                     ["--uid", "Bad;name=1001"], [], ["--uid", "engineer=1001", "--table", "x;y"],
                     ["--uid", "engineer=-5"], ["--uid", "engineer=1001", "--lo", "engineer=53"],
                     ["--uid", "engineer=1001", "--lo", "engineer=0"],
                     ["--uid", "engineer=1001", "--lo", "engineer=70000"],
                     ["--uid", "engineer=1001", "--lo", "engineer=1,x"],
                     ["--uid", "engineer=1001", "--lo", "nobody=3128"]):
            with self.subTest(args=args):
                self.assertEqual(render(*args).returncode, 2)

    def test_nft_accepts_it(self):
        nft = shutil.which("nft")
        if nft is None:
            self.skipTest("nft not installed")
        with tempfile.NamedTemporaryFile("w", suffix=".nft") as f:
            f.write(render(*BOTH).stdout.replace("delete table inet engineer_egress\n", ""))
            f.flush()
            r = subprocess.run([nft, "-c", "-f", f.name], capture_output=True, text=True)
        if r.returncode != 0 and ("Operation not permitted" in r.stderr or "netlink" in r.stderr.lower()):
            self.skipTest("nft -c needs CAP_NET_ADMIN here: " + r.stderr.strip())
        self.assertEqual(r.returncode, 0, r.stderr)


if __name__ == "__main__":
    unittest.main()
