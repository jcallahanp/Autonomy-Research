"""engineer/docs/versions.md records every pin the templates use: releases, apt keys, actions."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3] / "engineer"
TEMPLATES = ROOT / "templates"
VERSIONS = ROOT / "docs" / "versions.md"


def rows(path):
    for line in path.read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            yield line.split("\t")


class VersionsTest(unittest.TestCase):
    def setUp(self):
        self.text = VERSIONS.read_text()

    def test_under_250_lines(self):
        self.assertLessEqual(len(self.text.splitlines()), 250)

    def test_release_pins_recorded(self):
        for name, url, sha, _scope in rows(TEMPLATES / "release-pins.txt"):
            with self.subTest(name=name):
                version = re.search(r"v?(\d+\.\d+\.\d+)", url).group(1)
                line = next((l for l in self.text.splitlines() if l.startswith(f"| {name} ")), "")
                self.assertIn(version, line, f"{name} row missing or without {version}")
                self.assertIn("TO-PIN" if sha == "TO-PIN" else sha, line)

    def test_unverified_checksums_said_so(self):
        for name in ("gitleaks", "osv-scanner"):
            line = next(l for l in self.text.splitlines() if l.startswith(f"| {name} "))
            self.assertIn("copied from vendor checksum files, not re-verified by download", line)

    def test_apt_fingerprints_recorded(self):
        for name, _key, fprs, _deb in rows(TEMPLATES / "apt-repos.txt"):
            for fpr in fprs.split(","):
                with self.subTest(repo=name, fpr=fpr):
                    self.assertIn(fpr, self.text)
        for name in ("nodesource", "cloudflare"):
            line = next(l for l in self.text.splitlines() if l.startswith(f"| {name} apt key"))
            self.assertIn("trust-on-first-use", line)

    def test_actions_pinned_by_sha(self):
        wf = (TEMPLATES / "project" / ".github" / "workflows" / "checks.yml").read_text()
        for action, sha, tag in re.findall(r"uses: ([\w./-]+)@([0-9a-f]{40}) # (v[\d.]+)", wf):
            with self.subTest(action=action):
                self.assertRegex(self.text, rf"{re.escape(action)}.*{re.escape(tag)}.*{sha}")

    def test_managed_settings_note(self):
        self.assertIn("code.claude.com/docs/en/settings", self.text)
        self.assertIn("/usr/bin/git push", self.text)
        self.assertIn("sh -c", self.text)


if __name__ == "__main__":
    unittest.main()
