"""tg-send and tg-poll broker jobs against a loopback stand-in for Telegram (never api.telegram.org)."""
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tests" / "engineer"))
import testlib  # noqa: E402

TOKEN = "TEST-TOKEN-TG"
SOPS = """case "$3" in
  '["TG_SUPERVISOR_TOKEN"]') echo TEST-TOKEN-TG ;;
  '["TG_JOHN_CHAT_ID"]') echo 111111 ;;
  '["TG_JOHN_USER_ID"]') echo 111111 ;;
  *) exit 1 ;;
esac"""


class FakeTelegram(BaseHTTPRequestHandler):
    def _reply(self):
        n = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(n) if n else b""
        self.server.calls.append((self.command, self.path, body))
        status, payload = self.server.respond(self.path)
        data = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    do_GET = do_POST = _reply

    def log_message(self, *args):
        pass


class TgJobs(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = testlib.make_root(self.tmp.name)
        testlib.stub(self.root, "sops", SOPS)
        self.srv = ThreadingHTTPServer(("127.0.0.1", 0), FakeTelegram)
        self.srv.calls, self.srv.respond = [], lambda path: (200, {"ok": True, "result": {"message_id": 1}})
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        conf = self.root / "etc" / "engineer.conf"
        text = conf.read_text().replace('TELEGRAM_API="https://api.telegram.org"',
                                        f'TELEGRAM_API="http://127.0.0.1:{self.srv.server_port}"')
        self.assertIn("127.0.0.1", text)
        conf.write_text(text)
        self.state = Path(self.tmp.name) / "home" / "secretbroker" / "state"

    def tearDown(self):
        self.srv.shutdown()
        self.srv.server_close()
        self.tmp.cleanup()

    def job(self, name, stdin="", via_agent_run=False):
        env = {"PATH": f"{self.root}/bin:/usr/bin:/bin", "HOME": self.tmp.name, "LANG": "C.UTF-8"}
        argv = [str(self.root / "scripts" / "broker" / "jobs" / name)]
        if via_agent_run:
            env["SUDO_USER"] = "supervisor"
            argv = [str(self.root / "bin" / "agent-run"), name]
        return subprocess.run(argv, input=stdin, capture_output=True, text=True, env=env, timeout=30)

    def assertNoToken(self, p):
        self.assertNotIn(TOKEN, p.stdout)
        self.assertNotIn(TOKEN, p.stderr)
        for path in [Path(self.tmp.name) / "argv.log", *self.state.rglob("*")]:
            if path.is_file():
                self.assertNotIn(TOKEN, path.read_text(errors="replace"), path)

    def test_tg_send_splits_long_text(self):
        p = self.job("tg-send", "x" * 5000 + "\n")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(json.loads(p.stdout), {"sent": 2})
        posts = [c for c in self.srv.calls if c[0] == "POST"]
        self.assertEqual(len(posts), 2)
        self.assertEqual(posts[0][1], f"/bot{TOKEN}/sendMessage")
        bodies = [json.loads(c[2]) for c in posts]
        self.assertTrue(all(len(b["text"]) <= 4096 and b["chat_id"] == 111111 for b in bodies))
        self.assertEqual(sum(len(b["text"]) for b in bodies), 5000)

    def test_tg_send_splits_on_line_boundaries(self):
        text = "\n".join(f"{i}. " + "y" * 96 for i in range(60))
        p = self.job("tg-send", text)
        self.assertEqual(json.loads(p.stdout), {"sent": 2})
        first = json.loads(self.srv.calls[0][2])["text"]
        self.assertTrue(first.endswith("y"))
        self.assertEqual(json.loads(self.srv.calls[1][2])["text"].split(".")[0], str(len(first.splitlines())))

    def test_tg_send_token_not_logged(self):
        p = self.job("tg-send", "hello\n")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertNoToken(p)
        self.srv.respond = lambda path: (401, {"ok": False, "description": f"Unauthorized {path}"})
        p = self.job("tg-send", "hello\n")
        self.assertNotEqual(p.returncode, 0)
        self.assertNoToken(p)

    @unittest.skipUnless(os.access(REPO / "engineer" / "bin" / "agent-run", os.X_OK)
                         and (REPO / "engineer" / "etc" / "broker-jobs.txt").exists(), "Task 5 not built yet")
    def test_tg_send_token_not_logged_via_agent_run(self):
        p = self.job("tg-send", "hello\n", via_agent_run=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertTrue((self.state / "agent-run.log").exists())
        self.assertNoToken(p)

    def test_tg_send_empty_sends_nothing(self):
        p = self.job("tg-send", "\n\n")
        self.assertEqual((p.returncode, json.loads(p.stdout), self.srv.calls), (0, {"sent": 0}, []))

    def updates(self, *ups):
        self.srv.respond = lambda path: (200, {"ok": True, "result": list(ups)})

    def test_tg_poll_drops_other_senders(self):
        def m(uid, sender, text, key="message"):
            return {"update_id": uid, key: {"message_id": uid, "date": 1760000000 + uid, "text": text,
                                            "from": {"id": sender, "is_bot": False}, "chat": {"id": sender}}}
        self.updates(m(10, 111111, "1 y"), m(11, 222222, "all y"))
        p = self.job("tg-poll")
        self.assertEqual(p.returncode, 0, p.stderr)
        lines = [json.loads(x) for x in p.stdout.splitlines()]
        self.assertEqual(lines, [{"update_id": 10, "from_id": 111111, "date": 1760000010, "text": "1 y",
                                  "edited": False}])
        self.assertIn("dropped 1", p.stderr)
        self.assertEqual(self.srv.calls[0][1], f"/bot{TOKEN}/getUpdates?offset=0&timeout=0")
        self.assertEqual((self.state / "tg-offset").read_text().strip(), "11")
        self.assertNoToken(p)
        self.updates(m(12, 111111, "2 n", key="edited_message"), m(13, 222222, "1 y", key="edited_message"),
                     {"update_id": 14, "callback_query": {"from": {"id": 111111}}})
        p = self.job("tg-poll")
        self.assertEqual(self.srv.calls[1][1], f"/bot{TOKEN}/getUpdates?offset=12&timeout=0")
        lines = [json.loads(x) for x in p.stdout.splitlines()]
        self.assertEqual([(x["update_id"], x["edited"]) for x in lines], [(12, True)])
        self.assertIn("dropped 2", p.stderr)
        self.assertEqual((self.state / "tg-offset").read_text().strip(), "14")

    def test_tg_poll_error_keeps_offset(self):
        (self.state).mkdir(parents=True, exist_ok=True)
        (self.state / "tg-offset").write_text("5\n")
        self.srv.respond = lambda path: (500, {"ok": False, "description": path})
        p = self.job("tg-poll")
        self.assertNotEqual(p.returncode, 0)
        self.assertEqual((self.state / "tg-offset").read_text().strip(), "5")
        self.assertNoToken(p)


if __name__ == "__main__":
    unittest.main()
