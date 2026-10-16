"""new-project: copies the project skeleton, fills {{NAME}} and {{OWNER}}, never overwrites."""
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "engineer" / "scripts"))
from eng import schema  # noqa: E402

ROOT = REPO / "engineer"
TOOL = ROOT / "bin" / "new-project"
SKELETON = ROOT / "templates" / "project"


def run(*args):
    return subprocess.run([sys.executable, str(TOOL), *map(str, args)],
                          capture_output=True, text=True, timeout=30)


class NewProjectTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.out = self.tmp / "demo"

    def tearDown(self):
        self._tmp.cleanup()

    def make(self, *extra):
        r = run(self.out, "--name", "demo", "--owner", "octo-test", *extra)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r

    def test_empty_dir_gets_valid_plan_files(self):
        self.out.mkdir()
        self.make()
        plan = self.out / "docs" / "plan"
        tasks = json.loads((plan / "tasks.json").read_text())
        self.assertEqual(tasks, {"version": 1, "tasks": []})
        self.assertEqual(schema.validate(tasks, schema.load(ROOT, "tasks")), [])
        profile = yaml.safe_load((plan / "profile.yaml").read_text())
        self.assertEqual(schema.validate(profile, schema.load(ROOT, "profile")), [])
        self.assertIs(profile["self_merge"], True)
        self.assertEqual(profile["hard_gates"], ["money", "delete_data", "store_submission"])
        self.assertEqual(profile["promote"], "hold")
        self.assertIs(profile["unattended"], True)
        integ = yaml.safe_load((plan / "integrations.yaml").read_text())
        self.assertEqual(schema.validate(integ, schema.load(ROOT, "integrations")), [])
        arch = yaml.safe_load((plan / "architecture.yaml").read_text())
        self.assertEqual((arch["nodes"], arch["edges"]), ([], []))
        self.assertTrue((plan / "architecture.mmd").read_text().lstrip().startswith("flowchart LR"))

    def test_missing_dir_is_created(self):
        self.make()
        self.assertTrue((self.out / "CLAUDE.md").is_file())

    def test_every_skeleton_file_copied_and_filled(self):
        self.make()
        for src in SKELETON.rglob("*"):
            if src.is_file():
                dst = self.out / src.relative_to(SKELETON)
                self.assertTrue(dst.is_file(), dst)
                self.assertNotIn("{{", dst.read_text(), dst)
        for rel in ("docs/plan/contracts/.gitkeep", "docs/plan/changes/.gitkeep", "docs/map/.gitkeep",
                    "tests/acceptance/.gitkeep", "security/.gitkeep", "flows/.gitkeep", ".env.example",
                    "docs/adr/0000-template.md", "docs/setup.md", "dead-ends.md", "PROGRESS.md",
                    "docs/plan/brief.md", "docs/plan/requirements.md"):
            self.assertTrue((self.out / rel).is_file(), rel)
        self.assertIn("demo", (self.out / "CLAUDE.md").read_text())

    def test_codeowners_lines_end_with_owner(self):
        self.make()
        lines = [ln for ln in (self.out / ".github" / "CODEOWNERS").read_text().splitlines()
                 if ln.strip() and not ln.startswith("#")]
        self.assertGreater(len(lines), 10)
        for ln in lines:
            self.assertTrue(ln.endswith(" @octo-test"), ln)
        globs = {ln.rsplit(" ", 1)[0].strip() for ln in lines}
        for g in (".github/**", "docs/plan/**", "CLAUDE.md", "tests/acceptance/**", ".github/CODEOWNERS"):
            self.assertIn(g, globs)
        tier2 = ROOT / "templates" / "tier2-paths.txt"
        if tier2.exists():  # Task 9's list: every Tier 2 glob is a literal CODEOWNERS line
            for ln in tier2.read_text().splitlines():
                if ln.strip() and not ln.startswith("#"):
                    self.assertIn(ln.strip(), globs)

    def test_claude_md_rules(self):
        self.make()
        text = (self.out / "CLAUDE.md").read_text()
        self.assertLess(len(text.splitlines()), 200)
        self.assertIn("# Compact instructions", text)
        for line in ("superpowers:<name> means the local skill <name>",
                     "test-driven-development and finishing-a-development-branch are not installed",
                     "every task ends in a PR",
                     "the plan skill's task contract wins over Superpowers task sizing",
                     "no generated overview here; read docs/map/ by path"):
            self.assertIn(line, text)

    def test_dependents_and_dead_ends_headers(self):
        self.make()
        self.assertIn("| Source glob | Dependent doc |", (self.out / "docs" / "DEPENDENTS.md").read_text())
        dead = (self.out / "dead-ends.md").read_text()
        for col in ("Tool or path", "Version tested", "What failed", "Retry when"):
            self.assertIn(col, dead)

    def test_workflow_pins_exact(self):
        self.make()
        wf = (self.out / ".github" / "workflows" / "checks.yml").read_text()
        doc = yaml.safe_load(wf)
        self.assertEqual(len(doc["jobs"]), 1)
        self.assertIn("bash scripts/check.sh", wf)
        uses = re.findall(r"uses:\s*(\S+)", wf)
        self.assertTrue(uses)
        for u in uses:
            self.assertRegex(u, r"@([0-9a-f]{40}|v\d+\.\d+\.\d+)$", u)

    def test_non_empty_dir_refused_without_adopt(self):
        self.out.mkdir()
        (self.out / "README.md").write_text("mine\n")
        r = run(self.out, "--name", "demo", "--owner", "octo-test")
        self.assertEqual(r.returncode, 1)
        self.assertEqual(sorted(p.name for p in self.out.iterdir()), ["README.md"])

    def test_adopt_keeps_existing_and_reports(self):
        self.out.mkdir()
        (self.out / "CLAUDE.md").write_text("house rules\n")
        (self.out / "docs" / "plan").mkdir(parents=True)
        (self.out / "docs" / "plan" / "tasks.json").write_text('{"version": 1, "tasks": []}\n')
        r = self.make("--adopt")
        self.assertEqual((self.out / "CLAUDE.md").read_text(), "house rules\n")
        self.assertIn("CLAUDE.md", r.stdout)
        self.assertIn("docs/plan/tasks.json", r.stdout)
        self.assertTrue((self.out / "PROGRESS.md").is_file())

    def test_adopt_never_writes_through_symlink(self):
        self.out.mkdir()
        outside = self.tmp / "outside"
        outside.mkdir()
        (self.out / "docs").symlink_to(outside)
        r = run(self.out, "--name", "demo", "--owner", "octo-test", "--adopt")
        self.assertEqual(r.returncode, 1)
        self.assertEqual(list(outside.iterdir()), [])

    def test_bad_name_or_owner_refused(self):
        for name, owner in (("de mo", "octo-test"), ("{{X}}", "octo-test"), ("demo", "bad owner"),
                            ("demo", "-octo")):
            r = run(self.out, "--name", name, "--owner", owner)
            self.assertEqual(r.returncode, 2, (name, owner))
        self.assertFalse(self.out.exists())


if __name__ == "__main__":
    unittest.main()
