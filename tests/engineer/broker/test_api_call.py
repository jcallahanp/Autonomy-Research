"""api-call SERVICE METHOD PATH: allowlisted service, method and path; the secret never reaches output."""
import http.server
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "engineer" / "scripts"))
sys.path.insert(0, str(REPO / "tests" / "engineer"))

from eng import conf  # noqa: E402
import testlib  # noqa: E402

SOPS = (REPO / "tests" / "engineer" / "broker" / "sops-stub.sh").read_text()
SEEN = []


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        SEEN.append((self.path, self.headers))  # case-insensitive lookup
        code = 404 if self.path.endswith("/missing") else 200
        body = {"path": self.path, "auth": self.headers.get("Authorization"),
                "n8n": self.headers.get("X-N8N-API-KEY")}
        self.send_response(code)
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def log_message(self, *args):
        pass


class ApiCallTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name).resolve()
        self.root = testlib.make_root(self.tmp)
        self.conf = conf.load(self.root)
        testlib.stub(self.root, "sops", SOPS)
        secrets = Path(self.conf["SECRETS_FILE"])
        secrets.parent.mkdir(parents=True, exist_ok=True)
        secrets.write_text(json.dumps({"ATTIO_API_KEY": "TEST-TOKEN-ATTIO", "N8N_API_KEY": "TEST-TOKEN-N8N",
                                       "N8N_BASE_URL": self.base}))
        shipped = json.loads((self.root / "etc" / "broker-services.json").read_text())
        self.assertEqual(shipped["attio"]["base"], "https://api.attio.com/v2")
        shipped["attio"]["base"] = self.base + "/v2"
        (self.root / "etc" / "broker-services.json").write_text(json.dumps(shipped))
        SEEN.clear()

    def tearDown(self):
        self._tmp.cleanup()

    def call(self, *args, stdin=b"", caller="engineer"):
        env = {"PATH": "/usr/bin:/bin", "SUDO_USER": caller}
        return subprocess.run([str(self.root / "bin" / "agent-run"), "api-call", *args], input=stdin,
                              capture_output=True, env=env, timeout=30)

    def test_get_sends_bearer_and_prints_body(self):
        p = self.call("attio", "GET", "/self?limit=1")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(SEEN[0][0], "/v2/self?limit=1")
        self.assertEqual(SEEN[0][1]["Authorization"], "Bearer TEST-TOKEN-ATTIO")
        self.assertIn(b"HTTP 200", p.stderr)
        self.assertEqual(json.loads(p.stdout)["path"], "/v2/self?limit=1")

    def test_api_call_output_has_no_secret(self):
        p = self.call("attio", "GET", "/self")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn(b"[REDACTED]", p.stdout)
        for blob in (p.stdout, p.stderr, (Path(self.conf["BROKER_STATE_DIR"]) / "agent-run.log").read_bytes(),
                     "\n".join(testlib.argv_log(self.root)).encode()):
            self.assertNotIn(b"TEST-TOKEN-ATTIO", blob)

    def test_n8n_base_from_secret(self):
        p = self.call("n8n", "GET", "/workflows", caller="supervisor")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(SEEN[0][0], "/api/v1/workflows")
        self.assertEqual(SEEN[0][1]["X-N8N-API-KEY"], "TEST-TOKEN-N8N")
        self.assertNotIn(b"TEST-TOKEN-N8N", p.stdout + p.stderr)
        self.assertNotIn(self.base.encode(), p.stdout + p.stderr)

    def test_http_error_status(self):
        p = self.call("attio", "GET", "/missing")
        self.assertEqual(p.returncode, 1)
        self.assertIn(b"HTTP 404", p.stderr)

    def test_refusals(self):
        cases = [("attio", "POST", "/self"), ("attio", "get", "/self"), ("attio", "GET", "/../x"),
                 ("attio", "GET", "http://evil"), ("attio", "GET", "self"), ("attio", "GET", "//evil.com/x"),
                 ("attio", "GET", "/a/%2e%2e/b"), ("attio", "GET", "/a\\b"), ("attio", "GET", "/a b"),
                 ("attio", "GET", "/x#frag"), ("nope", "GET", "/self")]
        for args in cases:
            with self.subTest(args=args):
                self.assertEqual(self.call(*args, stdin=b"{}").returncode, 65)
        self.assertEqual(SEEN, [])
        self.assertEqual(self.call("attio", "GET").returncode, 64)

    def test_supervisor_and_unknown_caller(self):
        self.assertEqual(self.call("attio", "GET", "/self", caller="supervisor").returncode, 0)
        self.assertEqual(self.call("attio", "GET", "/self", caller="stranger").returncode, 77)


if __name__ == "__main__":
    unittest.main()
