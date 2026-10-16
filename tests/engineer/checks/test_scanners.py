"""scanners.py: gitleaks, osv-scanner and semgrep through stubs; only new findings fail."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from gitfix import Repo

REPO = Path(__file__).resolve().parents[3]
TOOL = REPO / "engineer" / "scripts" / "checks" / "scanners.py"

GITLEAKS = r'''import json, os, sys
open(os.environ["STUB_LOG"], "a").write("gitleaks " + " ".join(sys.argv[1:]) + "\n")
path = sys.argv[sys.argv.index("--report-path") + 1]
open(path, "w").write(os.environ.get("GL_REPORT", "[]"))
'''
OSV = r'''import json, os, sys
open(os.environ["STUB_LOG"], "a").write("osv-scanner " + " ".join(sys.argv[1:]) + "\n")
d = sys.argv[-1]
lock = os.path.join(d, "package-lock.json")
if os.path.exists(lock) and "vulnerable" in open(lock).read():
    pkg = {"package": {"name": "left-pad"}, "vulnerabilities": [{"id": "GHSA-test-0001"}]}
    print(json.dumps({"results": [{"source": {"path": lock}, "packages": [pkg]}]}))
    sys.exit(1)
print(json.dumps({"results": []}))
'''
SEMGREP = r'''import json, os, sys
open(os.environ["STUB_LOG"], "a").write("semgrep " + " ".join(sys.argv[1:]) + "\n")
res = []
for f in sys.argv[1:]:
    if os.path.isfile(f) and "eval(" in open(f).read():
        res.append({"check_id": "test.eval", "path": f, "start": {"line": 1}, "extra": {"lines": "requires login"}})
print(json.dumps({"results": res, "errors": []}))
'''


class ScannersTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        t = Path(self.tmp.name)
        self.bin = t / "bin"
        self.bin.mkdir()
        for name, body in (("gitleaks", GITLEAKS), ("osv-scanner", OSV), ("semgrep", SEMGREP)):
            p = self.bin / name
            p.write_text(f"#!{sys.executable}\n{body}")
            p.chmod(0o755)
        self.log = t / "stub.log"
        self.repo = Repo(t / "p")
        self.base = self.repo.commit({"src/a.py": "x = 1\n", "package-lock.json": "{}\n"})
        self.env = dict(os.environ, PATH=f"{self.bin}:/usr/bin:/bin", STUB_LOG=str(self.log))

    def tearDown(self):
        self.tmp.cleanup()

    def run_tool(self, head):
        return subprocess.run([sys.executable, str(TOOL), "--repo", self.repo.gitdir, "--base", self.base,
                               "--head", head], capture_output=True, text=True, env=self.env)

    def calls(self):
        return self.log.read_text() if self.log.exists() else ""

    def test_clean(self):
        r = self.run_tool(self.repo.commit({"src/a.py": "x = 2\n", "package-lock.json": '{"a": 1}\n'}))
        self.assertEqual((r.returncode, r.stdout), (0, ""), r.stderr)
        log = self.calls()
        self.assertIn("--redact", log)
        self.assertIn(f"--log-opts={self.base}..", log)
        self.assertIn("osv-scanner", log)
        self.assertIn("semgrep", log)

    def test_gitleaks_finding(self):
        head = self.repo.commit({"src/a.py": "x = 3\n"})
        self.env["GL_REPORT"] = json.dumps([{"File": "src/a.py", "StartLine": 1, "RuleID": "generic-api-key",
                                             "Secret": "REDACTED", "Match": "REDACTED"}])
        r = self.run_tool(head)
        self.assertEqual(r.returncode, 1)
        self.assertIn("gitleaks: src/a.py:1 generic-api-key", r.stdout)
        self.assertNotIn("REDACTED", r.stdout)

    def test_osv_new_vuln(self):
        r = self.run_tool(self.repo.commit({"package-lock.json": '{"vulnerable": true}\n'}))
        self.assertEqual(r.returncode, 1)
        self.assertIn("osv-scanner: new GHSA-test-0001 (left-pad)", r.stdout)

    def test_osv_old_vuln_and_no_manifest(self):
        self.base = self.repo.commit({"package-lock.json": '{"vulnerable": true}\n'})
        r = self.run_tool(self.repo.commit({"package-lock.json": '{"vulnerable": 2}\n'}))
        self.assertEqual((r.returncode, r.stdout), (0, ""), r.stderr)
        self.log.unlink()
        self.base = self.repo.git("rev-parse", "HEAD")
        r = self.run_tool(self.repo.commit({"src/a.py": "y = 1\n"}))
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertNotIn("osv-scanner", self.calls())

    def test_semgrep_new_only(self):
        r = self.run_tool(self.repo.commit({"src/a.py": "eval(input())\n"}))
        self.assertEqual(r.returncode, 1)
        self.assertIn("semgrep: src/a.py test.eval", r.stdout)
        self.base = self.repo.git("rev-parse", "HEAD")
        r = self.run_tool(self.repo.commit({"src/a.py": "eval(input())\nz = 1\n"}))
        self.assertEqual((r.returncode, r.stdout), (0, ""), r.stderr)

    def test_missing_tool(self):
        (self.bin / "gitleaks").unlink()
        r = self.run_tool(self.repo.commit({"src/a.py": "x = 4\n"}))
        self.assertEqual(r.returncode, 1)
        self.assertIn("gitleaks: not installed", r.stdout)


if __name__ == "__main__":
    unittest.main()
