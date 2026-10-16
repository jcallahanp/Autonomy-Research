"""parity.py: node ids in docs/plan/architecture.yaml vs docs/plan/architecture.mmd."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TOOL = REPO / "engineer" / "scripts" / "checks" / "parity.py"
YAML = "nodes:\n  - id: attio\n    label: Attio\n  - id: n8n\n  - id: clay\n"
MMD = "flowchart LR\n  attio[Attio]\n  n8n(n8n)\n  clay{Clay}\n  attio --> n8n\n"


def run(d):
    return subprocess.run([sys.executable, str(TOOL), "--repo", str(d)], capture_output=True, text=True)


class ParityTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.plan = Path(self.tmp.name) / "docs" / "plan"
        self.plan.mkdir(parents=True)
        (self.plan / "architecture.yaml").write_text(YAML)

    def tearDown(self):
        self.tmp.cleanup()

    def test_match(self):
        (self.plan / "architecture.mmd").write_text(MMD)
        r = run(self.tmp.name)
        self.assertEqual((r.returncode, r.stdout), (0, ""), r.stderr)

    def test_mismatch(self):
        (self.plan / "architecture.mmd").write_text(MMD.replace("clay{Clay}", "slack[Slack]"))
        r = run(self.tmp.name)
        self.assertEqual(r.returncode, 1)
        self.assertIn("missing in mmd: clay", r.stdout)
        self.assertIn("missing in yaml: slack", r.stdout)


if __name__ == "__main__":
    unittest.main()
