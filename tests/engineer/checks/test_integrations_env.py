"""integrations-env.py: env var names in docs/plan/integrations.yaml vs .env.example."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TOOL = REPO / "engineer" / "scripts" / "checks" / "integrations-env.py"
YAML = """version: 1
services:
  - id: attio
    env_vars: [ATTIO_API_KEY]
  - id: n8n
    env_vars: [N8N_API_KEY, N8N_BASE_URL]
"""


def run(d):
    return subprocess.run([sys.executable, str(TOOL), "--repo", str(d)], capture_output=True, text=True)


class IntegrationsEnvTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        (self.d / "docs" / "plan").mkdir(parents=True)
        (self.d / "docs" / "plan" / "integrations.yaml").write_text(YAML)

    def tearDown(self):
        self.tmp.cleanup()

    def test_match(self):
        (self.d / ".env.example").write_text("# names only\nATTIO_API_KEY=\nexport N8N_API_KEY=\nN8N_BASE_URL=https://example.invalid\n")
        r = run(self.d)
        self.assertEqual((r.returncode, r.stdout), (0, ""), r.stderr)

    def test_mismatch(self):
        (self.d / ".env.example").write_text("ATTIO_API_KEY=\nN8N_API_KEY=\nCLAY_KEY=\n")
        r = run(self.d)
        self.assertEqual(r.returncode, 1)
        self.assertEqual(sorted(r.stdout.split("\n")[:-1]), ["extra: CLAY_KEY", "missing: N8N_BASE_URL"])


if __name__ == "__main__":
    unittest.main()
