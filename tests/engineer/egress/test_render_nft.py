"""render-nft.py: nftables ruleset that limits the listed uids to loopback (Task 4)."""
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SCRIPT = REPO / "engineer" / "scripts" / "egress" / "render-nft.py"


def render(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


class RenderNft(unittest.TestCase):
    def test_rules_in_order(self):
        r = render("--uid", "engineer=1001", "--uid", "supervisor=1002")
        self.assertEqual(r.returncode, 0, r.stderr)
        out = r.stdout
        parts = ["table inet engineer_egress",
                 'meta skuid { 1001, 1002 } oif "lo" accept',
                 'meta skuid { 1001, 1002 } log prefix "engineer-egress-drop " drop']
        pos = [out.find(p) for p in parts]
        self.assertTrue(all(p >= 0 for p in pos), out)
        self.assertEqual(pos, sorted(pos), out)

    def test_other_uids_untouched(self):
        out = render("--uid", "engineer=1001", "--uid", "supervisor=1002").stdout
        self.assertIn("policy accept;", out)
        rules = [l.strip() for l in out.splitlines()
                 if l.strip() and not l.strip().startswith(("#", "table", "delete", "chain", "type", "}"))]
        self.assertEqual(len(rules), 2, out)
        for rule in rules:
            self.assertTrue(rule.startswith("meta skuid { 1001, 1002 } "), rule)

    def test_replaces_table_atomically(self):
        out = render("--uid", "engineer=1001").stdout
        self.assertLess(out.find("delete table inet engineer_egress"),
                        out.find("table inet engineer_egress {"))
        self.assertIn("meta skuid { 1001 } oif", out)

    def test_custom_table(self):
        out = render("--uid", "engineer=1001", "--table", "eng_test").stdout
        self.assertIn("table inet eng_test {", out)
        self.assertNotIn("engineer_egress", out)

    def test_duplicate_uid_listed_once(self):
        out = render("--uid", "engineer=1001", "--uid", "engineer=1001").stdout
        self.assertIn("meta skuid { 1001 } oif", out)

    def test_bad_input_exits_2(self):
        for args in (["--uid", "engineer=abc"], ["--uid", "engineer"], ["--uid", "root=0"],
                     ["--uid", "Bad;name=1001"], [], ["--uid", "engineer=1001", "--table", "x;y"],
                     ["--uid", "engineer=-5"]):
            with self.subTest(args=args):
                self.assertEqual(render(*args).returncode, 2)


if __name__ == "__main__":
    unittest.main()
