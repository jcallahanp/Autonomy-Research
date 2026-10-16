import json
import sys
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[3]
ROOT = REPO / "engineer"
TEMPLATES = ROOT / "templates"
NPM = ("@anthropic-ai/claude-code", "@playwright/mcp", "@playwright/cli", "@mermaid-js/mermaid-cli")
OTHER = ("gitleaks", "osv-scanner", "semgrep")


class TemplatesTest(unittest.TestCase):
    def test_run_defaults(self):
        d = yaml.safe_load((TEMPLATES / "run-defaults.yaml").read_text())
        self.assertEqual(d["night"], {"start": "22:00", "end": "07:00", "tz": "America/New_York", "digest_at": "07:30"})
        self.assertEqual(d["task"]["attempts"], 2)
        self.assertEqual(d["breaker"], {"no_diff_sessions": 3, "same_failure_repeats": 5})
        self.assertEqual(d["denials_per_kind_per_night"], 5)
        self.assertEqual(d["t1"], {"timeout_hours": 24, "reminder_hours": 12, "max_open": 5})
        self.assertEqual(d["profiles"]["implementer"]["max_turns"], 60)
        self.assertEqual(d["profiles"]["implementer"]["max_budget_usd"], 5)
        self.assertEqual(d["profiles"]["auditor"]["json_schema"], "audit-verdict")
        self.assertEqual(d["profiles"]["planner"]["model"], "opus")
        self.assertEqual(d["profiles"]["check"], {"timeout_minutes": 20})
        for name, p in d["profiles"].items():
            if name != "check":
                self.assertEqual(p["agent"], name)

    def test_bootstrap_packages(self):
        rows = {}
        for line in (TEMPLATES / "bootstrap-packages.txt").read_text().splitlines():
            if not line.strip() or line.startswith("#"):
                continue
            name, method, pin = line.split("\t")
            self.assertRegex(pin, r"^v?\d+\.\d+\.\d+$", name)
            rows[name] = (method, pin)
        for name in NPM:
            self.assertEqual(rows[name][0], "npm", name)
        for name in OTHER:
            self.assertIn(name, rows)
        self.assertTrue(any(n.endswith("mermaid-lint") or n.startswith("@mermaid-lint/") for n in rows))
        self.assertEqual(rows["@anthropic-ai/claude-code"][1], "2.1.301")
        versions = (ROOT / "docs" / "versions.md").read_text()
        for name, (_, pin) in rows.items():
            self.assertIn(pin, versions, f"{name} {pin} not in versions.md")

    def test_plugin_manifest(self):
        m = json.loads((ROOT / "plugin" / ".claude-plugin" / "plugin.json").read_text())
        self.assertEqual((m["name"], m["version"], m["license"]), ("engineer", "0.1.0", "MIT"))
        self.assertEqual(m["author"]["name"], "jcallahanp")


if __name__ == "__main__":
    unittest.main()
