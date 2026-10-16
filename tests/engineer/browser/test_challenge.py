"""challenge-check.py on synthetic snapshots and fixture HTML."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SCRIPT = REPO / "engineer" / "scripts" / "browser" / "challenge-check.py"
FIX = Path(__file__).resolve().parent / "fixtures"


def check(snapshot, *args):
    data = snapshot if isinstance(snapshot, str) else json.dumps(snapshot)
    p = subprocess.run([sys.executable, str(SCRIPT), *args], input=data,
                       capture_output=True, text=True, timeout=20)
    out = json.loads(p.stdout) if p.stdout.strip().startswith("{") else None
    return p.returncode, out


def html(name, url):
    return {"url": url, "html": (FIX / name).read_text()}


class Challenge(unittest.TestCase):
    def assertChallenge(self, snap, kind):
        rc, out = check(snap)
        self.assertEqual(rc, 3, out)
        self.assertEqual(out["challenge"], True)
        self.assertEqual(out["kind"], kind)
        return out

    def test_google_blocked_text(self):
        snap = {"url": "https://accounts.google.com/v3/signin/rejected", "title": "Sign in - Google Accounts",
                "text": "Couldn't sign you in\nThis browser or app may not be secure."}
        out = self.assertChallenge(snap, "google_blocked")
        self.assertEqual(out["host"], "accounts.google.com")

    def test_google_blocked_html_curly_apostrophe(self):
        self.assertChallenge(html("google_blocked.html", "https://accounts.google.com/v3/signin/rejected"),
                             "google_blocked")

    def test_google_sorry(self):
        self.assertChallenge({"url": "https://www.google.com/sorry/index?continue=x", "title": "", "text": ""},
                             "google_sorry")

    def test_cloudflare_title(self):
        self.assertChallenge({"url": "https://app.example-vendor.test/", "title": "Just a moment...", "text": ""},
                             "cloudflare")

    def test_cloudflare_html(self):
        self.assertChallenge(html("cloudflare.html", "https://app.example-vendor.test/"), "cloudflare")

    def test_cloudflare_text_only(self):
        self.assertChallenge({"url": "https://x.test/", "title": "x", "text": "Verify you are human"}, "cloudflare")

    def test_captcha_html(self):
        self.assertChallenge(html("hcaptcha.html", "https://app.example-vendor.test/check"), "captcha")

    def test_login_required(self):
        out = self.assertChallenge({"url": "https://app.attio.com/login", "title": "Attio", "text": "Continue"},
                                   "login_required")
        self.assertEqual(out["host"], "app.attio.com")
        self.assertChallenge({"url": "https://app.clay.com/sign-in?next=/x", "title": "", "text": ""},
                             "login_required")

    def test_attio_records_page_is_clean(self):
        rc, out = check(html("attio_records.html", "https://app.attio.com/example-test/objects/companies"))
        self.assertEqual(rc, 0, out)
        self.assertEqual(out, {"challenge": False, "kind": None, "host": "app.attio.com"})

    def test_login_word_in_path_segment_is_clean(self):
        rc, out = check({"url": "https://app.attio.com/x/loginsettings-docs", "title": "t", "text": "t"})
        self.assertEqual(rc, 0, out)

    def test_bad_input_exit_2(self):
        self.assertEqual(check("not json")[0], 2)
        self.assertEqual(check("[1, 2]")[0], 2)
        self.assertEqual(check({"url": 5})[0], 2)

    def test_bad_pattern_file_exit_2(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d) / "patterns.txt"
            tmp.write_text("cloudflare\tbody\tx\n")
            self.assertEqual(check({"url": "https://a.test/"}, "--patterns", str(tmp))[0], 2)
            tmp.write_text("cloudflare\ttitle\t(unclosed\n")
            self.assertEqual(check({"url": "https://a.test/"}, "--patterns", str(tmp))[0], 2)
            self.assertEqual(check({"url": "https://a.test/"}, "--patterns", str(Path(d) / "none"))[0], 2)

    def test_pattern_file_has_the_plan_rows(self):
        rows = [l.split("\t") for l in
                (REPO / "engineer" / "templates" / "challenge-patterns.txt").read_text().splitlines()
                if l and not l.startswith("#")]
        kinds = [r[0] for r in rows]
        for k in ("google_blocked", "google_sorry", "cloudflare", "captcha", "login_required"):
            self.assertIn(k, kinds)
        self.assertEqual(kinds[-1], "login_required")  # most generic last
        self.assertTrue(all(len(r) == 3 for r in rows))


if __name__ == "__main__":
    unittest.main()
