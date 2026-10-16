"""loop.py asks: browser challenges, PROGRESS.md asks, plan asks with hashes, digest records, no-diff, verdicts."""
import hashlib
import json
import sys
import unittest
from pathlib import Path

from loopfix import DAY, REPO, SHA, Rig, result

sys.path.insert(0, str(REPO / "engineer" / "scripts"))
from approvals import digest, items  # noqa: E402

BLOCKED = ("Stopped at the login page.\nBLOCKED: browser challenge kind=cloudflare host=app.example.com "
           "url=https://app.example.com/login\nT1: Re-login or clear the challenge on app.example.com in noVNC "
           "(https://novnc.example.invalid), then reply \"N y\" to retry.")
SIGNED = ("brief.md", "requirements.md", "integrations.yaml", "profile.yaml")


class LoopAsks(unittest.TestCase):
    def setUp(self):
        self.rig = Rig()
        self.addCleanup(self.rig.close)
        self.clone = Path(self.rig.conf["PROJECTS_DIR"]) / "demo"

    def run_ok(self, *a):
        p = self.rig.run(*a)
        self.assertEqual(p.returncode, 0, p.stderr)

    def asks(self):
        return [e for e in self.rig.events() if e["event"] == "approval_ask"]

    def outcome(self):
        return [e["detail"] for e in self.rig.events() if e["event"] == "audit"][-1]

    def progress(self, *lines, where=None):
        d = where or (Path(self.rig.conf["PROJECTS_DIR"]) / "demo.wt" / "t1")
        d.mkdir(parents=True, exist_ok=True)
        (d / "PROGRESS.md").write_text("# Progress\n\n## 2026-10-16 t1\n- did things\n\n## Asks for John\n"
                                       + "".join(f"- {x}\n" for x in lines) + "\n## Later\n- not an ask\n")

    def test_browser_challenge_raises_relogin_ask(self):
        tail = "\n".join(["progress", json.dumps({"type": "result", "is_error": False, "result": BLOCKED})])
        self.rig.reply("implementer", result(output_tail=tail))
        self.run_ok()
        ch = [e for e in self.rig.events() if e["event"] == "challenge"]
        self.assertEqual(ch[0]["detail"], {"kind": "cloudflare", "host": "app.example.com",
                                           "url": "https://app.example.com/login"})
        a = self.asks()[-1]
        self.assertEqual((a["task_id"], a["detail"]["kind"], a["detail"]["tier"], a["detail"]["default"],
                          a["detail"]["reversible"]), ("t1", "relogin", "T1", "n", True))
        self.assertIn("app.example.com", a["detail"]["text"])
        self.assertEqual(self.outcome()["status"], "blocked")
        self.assertFalse([x for x in self.rig.argv() if " check" in x or "audit.sh" in x])

    def test_relogin_yes_unblocks_task(self):
        tail = json.dumps({"type": "result", "result": BLOCKED})
        self.rig.reply("implementer", result(output_tail=tail), n=1)
        self.run_ok()
        item = self.asks()[-1]["detail"]["item"]
        (self.rig.rt / "apply-replies.py.out").write_text(json.dumps(
            {"item": item, "kind": "relogin", "answer": "yes", "ref": "https://app.example.com/login"}))
        (self.rig.rt / "poll").write_text('{"update_id": 1, "from_id": 111111, "date": 2, "text": "1 y", "edited": false}\n')
        self.run_ok()
        self.assertEqual(self.outcome()["status"], "done")

    def test_progress_asks_reach_digest(self):
        self.progress("Rotate the n8n API key for demo? y rotates it tonight.", "Rotate the n8n API key for demo? y rotates it tonight.",
                      "Unblock t2: add the Attio workspace id to .env")
        self.rig.reply("audit", {"verdict": "FAIL", "head_sha": SHA, "lines": ["2 tests fail"]})
        self.run_ok()
        self.run_ok()
        got = [a["detail"] for a in self.asks()]
        self.assertEqual([d["text"] for d in got], ["Rotate the n8n API key for demo? y rotates it tonight.",
                                                    "Unblock t2: add the Attio workspace id to .env"])
        self.assertTrue(all((d["tier"], d["kind"], d["default"]) == ("T1", "other", "n") for d in got))
        open_ = items.open_items(self.rig.events(), [], DAY)
        text = "\n".join(digest.render(open_))
        self.assertIn('1. Rotate the n8n API key for demo? y rotates it tonight. (default: n). Reply "1 y"', text)
        self.assertIn("2. Unblock t2", text)

    def test_plan_ask_carries_signed_hashes(self):
        plan = self.clone / "docs" / "plan"
        for f in SIGNED:
            (plan / f).write_text(f"synthetic {f}\n")
        self.progress("Approve plan v1 for demo? PR https://github.com/o/demo/pull/3", where=self.clone)
        self.run_ok()
        d = self.asks()[-1]["detail"]
        self.assertEqual((d["kind"], d["tier"], d["reversible"]), ("plan", "T1", False))
        self.assertEqual(d["files"], {f"docs/plan/{f}": hashlib.sha256(f"synthetic {f}\n".encode()).hexdigest()
                                      for f in SIGNED})
        (self.rig.rt / "apply-replies.py.out").write_text(json.dumps(
            {"item": d["item"], "kind": "plan", "answer": "yes", "ref": None}))
        (self.rig.rt / "poll").write_text('{"update_id": 1, "from_id": 111111, "date": 2, "text": "1 y", "edited": false}\n')
        self.run_ok(DAY)
        want = f"approve-plan demo --record-id item-{d['item']} --item {d['item']} --by john --source telegram"
        self.assertIn(want, self.rig.argv())

    def test_clone_asks_raised_outside_the_night(self):
        self.progress("Approve plan v1 for demo? PR https://github.com/o/demo/pull/3", where=self.clone)
        self.run_ok(DAY)
        self.run_ok(DAY)
        got = [a for a in self.asks() if a["detail"]["kind"] == "plan"]
        self.assertEqual(len(got), 1)
        self.assertEqual(got[0]["detail"]["ref"], "https://github.com/o/demo/pull/3")
        self.assertFalse([a for a in self.rig.argv() if a.startswith("run-task")])

    def test_first_attempt_without_commits_is_no_diff(self):
        self.rig.reply("implementer", result(base_sha=SHA))
        self.rig.reply("audit", {"verdict": "FAIL", "head_sha": SHA, "lines": ["nothing changed"]})
        self.run_ok()
        self.assertIs(self.outcome()["diff"], False)

    def test_commit_since_base_is_a_diff(self):
        self.rig.reply("implementer", result(base_sha="ab" * 20))
        self.rig.reply("audit", {"verdict": "FAIL", "head_sha": SHA, "lines": ["2 tests fail"]})
        self.run_ok()
        self.assertIs(self.outcome()["diff"], True)

    def test_auditor_verdict_from_structured_output(self):
        self.rig.reply("auditor", result(output_tail="not json at all",
                                         structured_output={"verdict": "PASS", "head_sha": SHA, "lines": ["ok"]}))
        self.run_ok()
        self.assertEqual(self.outcome()["status"], "done")
        self.assertTrue([a for a in self.rig.argv() if a.startswith("agent-run open-pr")])

    def test_sync_mirror_before_each_task(self):
        self.run_ok()
        argv = self.rig.argv()
        sync = [i for i, a in enumerate(argv) if a == "agent-run sync-mirror demo"]
        impl = [i for i, a in enumerate(argv) if a.startswith("run-task demo t1 implementer")]
        self.assertTrue(sync and impl and sync[0] < impl[0], argv)

    def test_digest_records_shown_items(self):
        (self.rig.rt / "digest.py.out").write_text(json.dumps({"messages": ["1. a", "+1 more"], "shown": [1]}))
        self.run_ok(DAY)
        dig = [e for e in self.rig.events() if e["event"] == "digest"]
        self.assertEqual(dig[-1]["detail"]["items"], [1])
        self.assertIn("1. a", (self.rig.rt / "sent.txt").read_text())
        self.assertTrue([a for a in self.rig.argv() if a.startswith("digest.py") and "--json-object" in a])


if __name__ == "__main__":
    unittest.main()
