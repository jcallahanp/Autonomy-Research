"""loop.py asks: browser challenges, PROGRESS.md asks, plan asks with hashes, digest records, no-diff, verdicts."""
import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

from loopfix import AGENT_RUN, DAY, REPO, SHA, Rig, result

sys.path.insert(0, str(REPO / "engineer" / "scripts"))
import testlib  # noqa: E402
from approvals import digest, items  # noqa: E402
from eng import approval  # noqa: E402

PLAN = "Approve plan v1 for demo? PR https://github.com/o/demo/pull/3"

BLOCKED = ("Stopped at the login page.\nBLOCKED: browser challenge kind=cloudflare host=app.example.com "
           "url=https://app.example.com/login\nT1: Re-login or clear the challenge on app.example.com in noVNC "
           "(https://novnc.example.invalid), then reply \"N y\" to retry.")


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

    def agent_run(self, extra: str):
        """The rig's AGENT_RUN stub with extra `case` lines tried first."""
        testlib.stub(self.rig.root, "agent-run", extra + "\n" + AGENT_RUN.replace("__D__", repr(str(self.rig.tmp))))

    def no_approval(self):
        """No live plan approval yet (the rig approves its tasks.json by default)."""
        (Path(self.rig.conf["STATE_DIR"]) / "approvals" / "demo.json").unlink()

    def plan_pr(self):
        """GitHub's plan PR 3 in the broker mirror, with signed files that differ from the working tree."""
        self.no_approval()
        mirror = Path(self.rig.conf["MIRROR_DIR"]) / "demo.git"
        seed = self.rig.tmp / "plan-seed"
        git = lambda *a: subprocess.run(["git", *a], cwd=seed, check=True, capture_output=True, text=True).stdout  # noqa: E731
        subprocess.run(["git", "init", "-q", "--bare", str(mirror)], check=True)
        subprocess.run(["git", "init", "-q", str(seed)], check=True)
        for rel in approval.SIGNED:
            (seed / rel).parent.mkdir(parents=True, exist_ok=True)
            (seed / rel).write_text(f"pr {rel}\n")
            if not rel.endswith("tasks.json"):
                (self.clone / rel).parent.mkdir(parents=True, exist_ok=True)
                (self.clone / rel).write_text(f"working tree {rel}\n")
        git("add", "-A")
        git("-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-qm", "docs: plan v1")
        sha = git("rev-parse", "HEAD").strip()
        git("push", "-q", str(mirror), f"{sha}:refs/pull/3/head")
        self.agent_run(f"""case "$1" in
  pr-head) echo '{{"number": 3, "head_sha": "{sha}", "state": "OPEN"}}'; exit 0 ;;
  sync-mirror) [ "${{3:-}}" = --pr ] && {{ echo '{{"pr": {{"number": 3, "sha": "{sha}"}}}}'; exit 0; }} ;;
esac""")
        return sha

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
        self.assertEqual(self.outcome()["status"], "in_review")  # a PASS waits for its merge

    def test_progress_asks_reach_digest(self):
        self.progress("Rotate the n8n API key for demo? y rotates it tonight.", "Rotate the n8n API key for demo? y rotates it tonight.",
                      "Unblock t2: add the Attio workspace id to .env")
        self.rig.reply("audit", {"verdict": "FAIL", "head_sha": SHA, "lines": ["2 tests fail"]})
        self.run_ok()
        self.run_ok()
        got = [a["detail"] for a in self.asks() if a["detail"]["kind"] != "deadend"]
        self.assertEqual([d["text"] for d in got], ["Rotate the n8n API key for demo? y rotates it tonight.",
                                                    "Unblock t2: add the Attio workspace id to .env"])
        self.assertTrue(all((d["tier"], d["kind"], d["default"]) == ("T1", "other", "n") for d in got))
        open_ = items.open_items(self.rig.events(), [], DAY)
        text = "\n".join(digest.render(open_))
        self.assertIn('1. demo: Rotate the n8n API key for demo? y rotates it tonight. (default: n). Reply "1 y"', text)
        self.assertIn("2. demo: Unblock t2", text)

    def test_plan_ask_binds_pr_head_not_working_tree(self):
        sha = self.plan_pr()
        self.progress(PLAN, where=self.clone)
        self.run_ok(DAY)
        d = self.asks()[-1]["detail"]
        self.assertEqual((d["kind"], d["tier"], d["reversible"], d["version"], d["sha"], d["pr"]),
                         ("plan", "T1", False, 1, sha, 3))
        self.assertEqual(d["files"], {rel: hashlib.sha256(f"pr {rel}\n".encode()).hexdigest()
                                      for rel in approval.SIGNED})
        rec = Path(self.rig.conf["RECORDS_DIR"]) / "demo" / "approvals" / "demo" / "v1"
        self.assertEqual((rec / approval.SIGNED[0]).read_text(), f"pr {approval.SIGNED[0]}\n")
        sent = (self.rig.rt / "sent.txt").read_text()
        self.assertIn(f"{d['item']}. demo: Approve plan v1 @ {sha[:7]}? PR https://github.com/o/demo/pull/3", sent)
        self.assertEqual([e["detail"]["items"] for e in self.rig.events() if e["event"] == "notify"], [[d["item"]]])
        (self.rig.rt / "apply-replies.py.out").write_text(json.dumps(
            {"item": d["item"], "kind": "plan", "answer": "yes", "ref": None, "project": "demo"}))
        self.run_ok(DAY)
        want = f"approve-plan demo --record-id item-{d['item']} --item {d['item']} --by john --source telegram"
        self.assertIn(want, self.rig.argv())
        self.assertEqual(len([a for a in self.asks() if a["detail"]["kind"] == "plan"]), 1)

    def test_plan_version_not_newer_than_approved_is_not_asked(self):
        self.plan_pr()
        appr = Path(self.rig.conf["STATE_DIR"]) / "approvals" / "demo.json"
        appr.parent.mkdir(parents=True, exist_ok=True)
        appr.write_text(json.dumps({"scope_version": 1}))
        self.progress(PLAN, where=self.clone)
        self.run_ok(DAY)
        self.run_ok(DAY)
        got = [a["detail"] for a in self.asks()]
        self.assertEqual([(d["kind"], "approved plan is v1" in d["text"]) for d in got], [("other", True)])

    def test_plan_refusal_becomes_t1_line_sent_at_once(self):
        testlib.stub(self.rig.root, "approve-plan",
                     "echo 'approve-plan: refused: profile.yaml hard_gates is empty' >&2; exit 65")
        (self.rig.rt / "apply-replies.py.out").write_text(json.dumps(
            {"item": 4, "kind": "plan", "answer": "yes", "ref": None, "project": "demo"}))
        self.run_ok(DAY)
        d = self.asks()[-1]["detail"]
        self.assertEqual((d["kind"], d["tier"]), ("other", "T1"))
        self.assertIn("hard_gates is empty", d["text"])
        self.assertIn("hard_gates is empty", (self.rig.rt / "sent.txt").read_text())

    def test_hard_gate_line_is_t2_sent_at_once(self):
        self.progress("HARD GATE: money Buy the Pro plan for demo, $12 a month CONFIRM: SPEND $12",
                      "HARD GATE: delete Drop table leads_old (40 rows)", where=self.clone)
        self.run_ok(DAY)
        got = [a["detail"] for a in self.asks()]
        self.assertEqual([(d["tier"], d["gate"], d["phrase"]) for d in got],
                         [("T2", "money", "SPEND $12"), ("T2", "delete_data", f"DELETE {got[1]['item']}")])
        sent = (self.rig.rt / "sent.txt").read_text()
        self.assertIn(f"HARD GATE {got[0]['item']}: demo: Buy the Pro plan for demo, $12 a month\n"
                      f"To approve, reply exactly: CONFIRM {got[0]['item']} SPEND $12", sent)

    def test_malformed_hard_gate_is_irreversible_t1(self):
        self.progress("HARD GATE: data Wipe the staging bucket", where=self.clone)
        self.run_ok(DAY)
        d = self.asks()[-1]["detail"]
        self.assertEqual((d["tier"], d["reversible"]), ("T1", False))

    def test_clone_asks_raised_outside_the_night(self):
        self.plan_pr()
        self.progress(PLAN, where=self.clone)
        self.run_ok(DAY)
        self.run_ok(DAY)
        got = [a for a in self.asks() if a["detail"]["kind"] == "plan"]
        self.assertEqual(len(got), 1)
        self.assertEqual(got[0]["detail"]["ref"], "https://github.com/o/demo/pull/3")
        self.assertFalse([a for a in self.rig.argv() if a.startswith("run-task")])

    def test_plan_without_pr_head_is_a_note_not_an_ask(self):
        self.no_approval()
        self.progress(PLAN, where=self.clone)
        self.run_ok(DAY)
        self.run_ok(DAY)
        got = [a["detail"] for a in self.asks()]
        self.assertEqual([d["kind"] for d in got], ["other"])
        self.assertIn("Plan v1 not asked yet", got[0]["text"])

    def test_plan_tag_push_pending_over_12_hours_is_a_t1_line(self):
        self.agent_run('case "$1 $*" in "push-branch "*--tag*) exit 1 ;; esac')
        self.rig.state_dir.mkdir(parents=True, exist_ok=True)
        (self.rig.state_dir / "plan-tags.pending").write_text("plan-approved-1\n")
        for now in ("2026-10-15T22:00:00Z", "2026-10-16T08:00:00Z"):  # first seen, then 10 h later
            self.run_ok(now)
        self.assertFalse([a for a in self.asks() if "plan-approved-1" in a["detail"]["text"]])
        self.run_ok(DAY)  # 13 h 45 min after the first pass that saw it
        self.run_ok(DAY)
        got = [a["detail"] for a in self.asks() if "plan-approved-1" in a["detail"]["text"]]
        self.assertEqual([(d["tier"], d["kind"]) for d in got], [("T1", "other")])

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
        self.assertEqual(self.outcome()["status"], "in_review")  # a PASS waits for its merge
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
