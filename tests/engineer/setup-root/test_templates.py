"""Static checks on Task 3's templates: sudoers, managed settings, AppArmor, units, package lists."""
import json
import re
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[3]
TPL = REPO / "engineer" / "templates"

SUDO_RULES = [
    "Defaults:engineer,supervisor env_reset",
    "engineer ALL=(secretbroker) NOPASSWD: /opt/engineer/bin/agent-run",
    "supervisor ALL=(engineer) NOPASSWD: /opt/engineer/bin/run-task",
    "supervisor ALL=(secretbroker) NOPASSWD: /opt/engineer/bin/agent-run",
]
UNITS = {
    "engineer-supervisor": "supervisor",
    "chrome-xvfb": "engineer",
    "novnc": "engineer",
    "engineer-remote-control": "engineer",
    "engineer-channels": "engineer",
    "engineer-egress-proxy": "egress",
}


def lines(path):
    return [l.strip() for l in path.read_text().splitlines() if l.strip() and not l.strip().startswith("#")]


def unit(name):
    sections, cur = {}, None
    for l in lines(TPL / "systemd" / f"{name}.service"):
        if l.startswith("["):
            cur = sections.setdefault(l, {})
        else:
            k, _, v = l.partition("=")
            cur.setdefault(k, []).append(v)
    return sections


class SudoersTest(unittest.TestCase):
    def test_exact_rules(self):
        self.assertEqual(sorted(lines(TPL / "sudoers" / "engineer")), sorted(SUDO_RULES))

    def test_no_other_nopasswd(self):
        text = (TPL / "sudoers" / "engineer").read_text()
        self.assertEqual(text.count("NOPASSWD"), 3)


class ManagedSettingsTest(unittest.TestCase):
    def setUp(self):
        self.s = json.loads((TPL / "managed-settings.json").read_text())

    def test_keys(self):
        s = self.s
        self.assertEqual(s["permissions"]["disableBypassPermissionsMode"], "disable")
        self.assertIs(s["sandbox"]["allowUnsandboxedCommands"], False)
        self.assertIs(s["sandbox"]["enabled"], True)
        self.assertEqual(s["cleanupPeriodDays"], 7)
        self.assertIs(s["autoContinueAtUsageLimit"], True)
        self.assertEqual(s["env"]["HTTPS_PROXY"], "http://127.0.0.1:3128")
        self.assertEqual(s["env"]["NO_PROXY"], "127.0.0.1,localhost")
        self.assertNotIn("hooks", s)

    def test_deny(self):
        deny = self.s["permissions"]["deny"]
        for rule in ["Read(//home/engineer/.engineer/chrome-profile/**)", "Read(//home/secretbroker/**)",
                     "Read(//var/lib/engineer/**)", "Read(**/.env)", "Bash(git push:*)", "Bash(git -C * push:*)"]:
            self.assertIn(rule, deny)


class AppArmorTest(unittest.TestCase):
    def test_profile(self):
        text = (TPL / "apparmor" / "bwrap").read_text()
        for part in ["abi <abi/4.0>,", "include <tunables/global>", "profile bwrap /usr/bin/bwrap flags=(unconfined)",
                     "userns,", "include if exists <local/bwrap>"]:
            self.assertIn(part, text)


class UnitsTest(unittest.TestCase):
    def test_units(self):
        for name, user in UNITS.items():
            with self.subTest(unit=name):
                u = unit(name)
                for sec in ("[Unit]", "[Service]", "[Install]"):
                    self.assertIn(sec, u)
                svc = u["[Service]"]
                self.assertEqual(svc["User"], [user])
                for cmd in svc["ExecStart"]:
                    self.assertRegex(cmd.split()[0], r"^/(opt/engineer|usr/bin)/")

    def test_supervisor(self):
        svc = unit("engineer-supervisor")["[Service]"]
        self.assertIn("/opt/engineer/scripts/supervisor/loop.py --projects /etc/engineer/projects.txt", svc["ExecStart"][0])
        self.assertEqual(svc["Restart"], ["on-failure"])
        self.assertIn("hc-ping fail", svc["ExecStopPost"][0])
        self.assertIn("TZ=America/New_York", svc["Environment"])
        self.assertNotIn("NoNewPrivileges", svc)

    def test_others(self):
        self.assertEqual(unit("engineer-remote-control")["[Service]"]["Restart"], ["always"])
        self.assertEqual(unit("engineer-channels")["[Service]"]["Type"], ["forking"])
        self.assertIn("chrome-xvfb.service", unit("novnc")["[Unit]"]["After"][0])
        proxy = unit("engineer-egress-proxy")["[Service]"]["ExecStart"][0]
        self.assertIn("--listen-host 127.0.0.1 --listen-port 3128", proxy)
        self.assertIn("engineer_allowlist=/etc/engineer/egress.txt", proxy)


class ListsTest(unittest.TestCase):
    def test_apt_packages(self):
        pkgs = " ".join(lines(TPL / "apt-packages.txt")).split()
        for p in ["git", "jq", "pipx", "unzip", "python3-yaml", "age", "nftables", "bubblewrap", "acl", "mitmproxy",
                  "google-chrome-stable", "nodejs", "gh", "cloudflared", "novnc", "xvfb"]:
            self.assertIn(p, pkgs)

    def test_apt_repos(self):
        rows = [l.split("\t") for l in (TPL / "apt-repos.txt").read_text().splitlines()
                if l.strip() and not l.startswith("#")]
        self.assertEqual(sorted(r[0] for r in rows), ["cloudflare", "github-cli", "google-chrome", "nodesource"])
        for name, url, fpr, deb in rows:
            self.assertTrue(url.startswith("https://"), url)
            self.assertRegex(fpr, r"^(TO-PIN|[0-9A-F]{40}(,[0-9A-F]{40})*)$")
            self.assertIn(f"signed-by=/etc/apt/keyrings/{name}.gpg", deb)
            self.assertRegex(deb, r"^deb \[[^]]*\] https://")

    def test_release_pins(self):
        rows = [l.split("\t") for l in lines(TPL / "release-pins.txt")]
        scopes = {r[0]: r[3] for r in rows}
        self.assertEqual(scopes.get("sops"), "root")
        self.assertEqual(scopes.get("bun"), "root")
        self.assertEqual(scopes.get("gitleaks"), "user")
        self.assertEqual(scopes.get("osv-scanner"), "user")
        for name, url, sha, scope in rows:
            self.assertTrue(url.startswith("https://"), url)
            self.assertRegex(sha, r"^(TO-PIN|[0-9a-f]{64})$")


if __name__ == "__main__":
    unittest.main()
