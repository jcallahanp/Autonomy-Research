import http.server
import os
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "engineer" / "scripts"))
sys.path.insert(0, str(REPO / "tests" / "engineer"))

from eng import brokerlib, conf  # noqa: E402
import testlib  # noqa: E402

SOPS = '[ -n "${SOPS_AGE_KEY_FILE:-}" ] || exit 9\nprintf "TEST-TOKEN-1"'


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        code = {"/ok": 200, "/redirect": 302}.get(self.path, 404)
        self.send_response(code)
        if code == 302:
            self.send_header("Location", "http://127.0.0.1:1/elsewhere")
        self.end_headers()
        self.wfile.write(b"ok" if code == 200 else b"no")

    def do_POST(self):
        body = self.rfile.read(int(self.headers["Content-Length"]))
        self.send_response(201)
        self.end_headers()
        self.wfile.write(body + self.headers.get("X-Test", "").encode())

    def log_message(self, *args):
        pass


class BrokerlibTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = testlib.make_root(self._tmp.name)
        self.conf = conf.load(self.root)
        testlib.stub(self.root, "sops", SOPS)
        self.env = mock.patch.dict(os.environ, {"PATH": f"{self.root}/bin:/usr/bin:/bin"})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self._tmp.cleanup()

    def test_secret(self):
        self.assertEqual(brokerlib.secret(self.conf, "GH_BOT_PAT"), "TEST-TOKEN-1")
        log = testlib.argv_log(self.root)
        self.assertEqual(len(log), 1)
        self.assertIn('["GH_BOT_PAT"]', log[0])
        self.assertIn(self.conf["SECRETS_FILE"], log[0])

    def test_secret_bad_name(self):
        for name in ("bad-name", "GH PAT", "", "A\"]", "lower"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                brokerlib.secret(self.conf, name)
        self.assertEqual(testlib.argv_log(self.root), [])

    def test_secret_sops_failure_raises(self):
        testlib.stub(self.root, "sops", "echo boom >&2; exit 3")
        with self.assertRaises(RuntimeError):
            brokerlib.secret(self.conf, "GH_BOT_PAT")

    def test_caller(self):
        with mock.patch.dict(os.environ, {"SUDO_USER": "engineer"}):
            self.assertEqual(brokerlib.caller(self.conf), "engineer")
            other = dict(self.conf, BROKER_USER="nobody-else")
            with mock.patch("getpass.getuser", return_value="me"):
                self.assertEqual(brokerlib.caller(other), "me")

    def test_log(self):
        brokerlib.log(self.conf, "push-branch", 0)
        brokerlib.log(self.conf, "bad\njob", 3)
        lines = (Path(self.conf["BROKER_STATE_DIR"]) / "agent-run.log").read_text().splitlines()
        self.assertEqual(len(lines), 2)
        ts, who, job, code = lines[0].split(" ")
        self.assertRegex(ts, r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
        self.assertEqual((job, code), ("push-branch", "0"))
        self.assertNotIn("bad", lines[1])

    def test_http(self):
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{server.server_address[1]}"
        try:
            self.assertEqual(brokerlib.http("GET", base + "/ok", {}, None), (200, b"ok"))
            self.assertEqual(brokerlib.http("GET", base + "/missing", {}, None), (404, b"no"))
            self.assertEqual(brokerlib.http("GET", base + "/redirect", {}, None)[0], 302)
            self.assertEqual(brokerlib.http("POST", base + "/", {"X-Test": "!"}, b"hi"), (201, b"hi!"))
        finally:
            server.shutdown()
            server.server_close()

    def test_http_refuses_plain_http_off_loopback(self):
        with self.assertRaises(ValueError):
            brokerlib.http("GET", "http://example.com/", {}, None)


if __name__ == "__main__":
    unittest.main()
