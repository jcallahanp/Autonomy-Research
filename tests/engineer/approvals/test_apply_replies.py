"""apply-replies.py: tg-poll lines in, approval-record lines and applied decisions out."""
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "engineer" / "scripts"))
from eng import schema  # noqa: E402

CLI = REPO / "engineer" / "scripts" / "approvals" / "apply-replies.py"
NOW = "2026-10-16T12:00:00Z"
ASKED = "2026-10-16T07:00:00Z"
AFTER = int(datetime(2026, 10, 16, 8, tzinfo=timezone.utc).timestamp())
BEFORE = int(datetime(2026, 10, 16, 6, tzinfo=timezone.utc).timestamp())


def ask(n, tier="T1", ts=ASKED, **extra):
    detail = {"item": n, "tier": tier, "kind": "merge", "text": f"Merge PR {n}", "default": "no",
              "reversible": True, "ref": f"https://example.invalid/pr/{n}"}
    if tier == "T2":
        detail.update(kind="other", phrase="SPEND $12")
    detail.update(extra)
    return {"ts": ts, "project": "demo", "event": "approval_ask", "detail": detail}


def digest_ev(shown, ts="2026-10-16T07:30:00Z"):
    return {"ts": ts, "project": "demo", "event": "digest", "detail": {"items": shown}}


def msg(text, date=AFTER, edited=False, uid=1):
    return {"update_id": uid, "from_id": 111111, "date": date, "text": text, "edited": edited}


class ApplyReplies(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name) / "demo"
        self.dir.mkdir()
        self.events, self.records = self.dir / "events.jsonl", self.dir / "records" / "approvals.jsonl"

    def tearDown(self):
        self.tmp.cleanup()

    def run_cli(self, events, lines, now=NOW):
        self.events.write_text("".join(json.dumps(e) + "\n" for e in events))
        stdin = "".join((ln if isinstance(ln, str) else json.dumps(ln)) + "\n" for ln in lines)
        p = subprocess.run([sys.executable, str(CLI), "--events", str(self.events), "--records", str(self.records),
                            "--now", now], input=stdin, capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        out = [json.loads(x) for x in p.stdout.splitlines()]
        recs = [json.loads(x) for x in self.records.read_text().splitlines()] if self.records.exists() else []
        evs = [json.loads(x) for x in self.events.read_text().splitlines()]
        return out, recs, evs

    def test_records_validate_and_decisions_print(self):
        out, recs, _ = self.run_cli([ask(1), ask(2)], [msg("1 y 2 n")])
        self.assertEqual(out, [{"item": 1, "kind": "merge", "answer": "yes", "ref": "https://example.invalid/pr/1"},
                               {"item": 2, "kind": "merge", "answer": "no", "ref": "https://example.invalid/pr/2"}])
        sch = schema.load(REPO / "engineer", "approval-record")
        self.assertEqual(len(recs), 2)
        for r in recs:
            self.assertEqual(schema.validate(r, sch), [], r)
        self.assertEqual((recs[0]["source"], recs[0]["from_id"], recs[0]["raw"]), ("telegram", 111111, "1 y 2 n"))

    def test_reply_edited_message_ignored(self):
        out, recs, evs = self.run_cli([ask(1)], [msg("1 y", edited=True)])
        self.assertEqual((out, recs, len(evs)), ([], [], 1))

    def test_reply_unparseable_adds_one_t1_line(self):
        out, recs, evs = self.run_cli([ask(1)], [msg("1 yes please")])
        self.assertEqual((out, recs), ([], []))
        self.assertEqual(len(evs), 2)
        d = evs[1]["detail"]
        self.assertEqual((evs[1]["event"], d["tier"], d["item"]), ("approval_ask", "T1", 2))
        self.assertIn("not understood", d["text"])
        ev_schema = schema.load(REPO / "engineer", "event")
        self.assertEqual(schema.validate(evs[1], ev_schema), [])

    def test_reply_unknown_item_approves_nothing(self):
        out, recs, _ = self.run_cli([ask(1)], [msg("1 y 9 y")])
        self.assertEqual((out, recs), ([], []))

    def test_reply_t2_needs_confirm(self):
        out, recs, _ = self.run_cli([ask(4, tier="T2")], [msg("4 y"), msg("all y")])
        self.assertEqual((out, recs), ([], []))
        out, recs, _ = self.run_cli([ask(4, tier="T2")], [msg("CONFIRM 4 SPEND $12")])
        self.assertEqual([(o["item"], o["answer"]) for o in out], [(4, "yes")])
        self.assertEqual(recs[0]["tier"], "T2")

    def test_reply_sent_before_ask_does_not_cover_it(self):
        out, recs, _ = self.run_cli([ask(1), ask(2, ts="2026-10-16T09:00:00Z"), digest_ev([1, 2])], [msg("all y")])
        self.assertEqual([o["item"] for o in out], [1])

    def test_reply_all_y_skips_hidden_items(self):
        evs = [ask(n) for n in range(1, 7)] + [digest_ev([1, 2, 3, 4, 5])]
        out, recs, _ = self.run_cli(evs, [msg("all y")])
        self.assertEqual([o["item"] for o in out], [1, 2, 3, 4, 5])
        self.assertEqual(sorted(r["item"] for r in recs), ["1", "2", "3", "4", "5"])
        out, recs, _ = self.run_cli(evs, [msg("6 y", uid=2)])
        self.assertEqual([o["item"] for o in out], [6])

    def test_reply_all_y_uses_digest_the_reply_answers(self):
        evs = [ask(1), ask(2), digest_ev([1], ts="2026-10-16T07:30:00Z"),
               digest_ev([1, 2], ts="2026-10-16T09:00:00Z")]
        out, _, _ = self.run_cli(evs, [msg("all y")])
        self.assertEqual([o["item"] for o in out], [1])

    def test_reply_all_y_without_digest_approves_nothing(self):
        out, recs, evs = self.run_cli([ask(1)], [msg("all y")])
        self.assertEqual((out, recs), ([], []))
        self.assertIn("not understood", evs[-1]["detail"]["text"])

    def test_reply_same_item_twice_in_batch(self):
        out, recs, _ = self.run_cli([ask(1)], [msg("1 n", uid=1), msg("1 y", uid=2)])
        self.assertEqual([(o["item"], o["answer"]) for o in out], [(1, "no")])
        self.assertEqual(len(recs), 1)

    def test_bad_stdin_line_is_skipped(self):
        out, recs, _ = self.run_cli([ask(1)], ["not json", "[1]", msg("1 y")])
        self.assertEqual([o["item"] for o in out], [1])

    def test_timeout_applies_default(self):
        out, recs, _ = self.run_cli([ask(1, ts="2026-10-15T07:00:00Z")], [])
        self.assertEqual(out, [{"item": 1, "kind": "merge", "answer": "default", "default": "no",
                                "ref": "https://example.invalid/pr/1"}])
        self.assertEqual(recs[0]["source"], "timeout")

    def test_torn_events_line_skipped(self):
        self.events.write_text(json.dumps(ask(1)) + "\n" + '{"ts": "2026')
        p = subprocess.run([sys.executable, str(CLI), "--events", str(self.events), "--records", str(self.records),
                            "--now", NOW], input=json.dumps(msg("1 y")) + "\n", capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(json.loads(p.stdout)["item"], 1)


if __name__ == "__main__":
    unittest.main()
