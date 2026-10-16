"""approvals/telegram.py: pending answers count, a plan yes whose records push failed, the tag push retry."""
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tests" / "engineer"))
sys.path.insert(0, str(REPO / "engineer" / "scripts"))
import testlib  # noqa: E402
import yaml  # noqa: E402
from approvals import planask, telegram  # noqa: E402
from eng import conf as engconf  # noqa: E402
from supervisor import steps  # noqa: E402

AGENT_RUN = r'''d=__D__
case "$1" in
  tg-send) cat >> "$d/sent.txt"; printf '\n---\n' >> "$d/sent.txt" ;;
  push-branch) exit "$(cat "$d/push.rc" 2>/dev/null || echo 0)" ;;
  sync-mirror) exit 1 ;;
esac'''


def ask(n):
    return {"ts": "2026-10-16T07:00:00Z", "project": "demo", "event": "approval_ask", "task_id": None,
            "detail": {"item": n, "tier": "T1", "kind": "other", "text": f"ask {n}", "default": "n",
                       "reversible": True, "ref": None}}


class Telegram(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)
        self.root = testlib.make_root(self.tmp)
        conf = engconf.load(self.root)
        defaults = yaml.safe_load((self.root / "templates" / "run-defaults.yaml").read_text())
        testlib.stub(self.root, "agent-run", AGENT_RUN.replace("__D__", repr(str(self.tmp))))
        now = datetime(2026, 10, 16, 12, tzinfo=timezone.utc)
        self.c = steps.Ctx(self.root, conf, defaults, {"name": "demo", "repo": "o/demo"}, now)
        self.c.dir.mkdir(parents=True, exist_ok=True)
        self.rec = Path(conf["RECORDS_DIR"]) / "demo"

    def sent(self):
        p = self.tmp / "sent.txt"
        return p.read_text() if p.exists() else ""

    def test_open_items_read_clone_and_pending_answers(self):
        """The clone exists but cannot be checked now (mirror dir is a symlink): both answer files still count."""
        (self.rec / "decisions").mkdir(parents=True)
        (self.rec / "decisions" / "approvals.jsonl").write_text(json.dumps({"item": "1", "answer": "yes"}) + "\n")
        (self.c.dir / "approvals.pending.jsonl").write_text(json.dumps({"item": "2", "answer": "no"}) + "\n")
        os.symlink(self.tmp, self.tmp / "mirrors-link")
        self.c.conf["MIRROR_DIR"] = str(self.tmp / "mirrors-link")
        self.c.events.write_text("".join(json.dumps(ask(n)) + "\n" for n in (1, 2, 3)))
        self.assertEqual(sorted(telegram.open_items(self.c)), [3])

    def test_plan_yes_push_pending_is_reported_applied(self):
        testlib.stub(self.root, "approve-plan", 'echo "approve-plan: push pending" >&2; exit 75')
        telegram._act(self.c, {"item": 4, "kind": "plan", "answer": "yes"})
        self.assertIn("demo: plan approval for item 4 is live; the records push is pending", self.sent())
        self.assertNotIn("not applied", self.sent())
        self.assertFalse([e for e in telegram.items.read_jsonl(self.c.events) if e.get("event") == "approval_ask"])

    def test_pending_tag_pushed_again_until_it_goes(self):
        marker = self.c.dir / planask.TAG_PENDING
        marker.write_text("plan-approved-2\nnot-a-tag; rm -rf /\n")
        (self.tmp / "push.rc").write_text("1")
        telegram.retry_tags(self.c)
        self.assertEqual(marker.read_text().split(), ["plan-approved-2"])
        (self.tmp / "push.rc").write_text("0")
        telegram.retry_tags(self.c)
        self.assertFalse(marker.exists())
        pushes = [a for a in testlib.argv_log(self.root) if a.startswith("agent-run push-branch")]
        self.assertEqual(pushes, [f"agent-run push-branch {self.rec} engineer-records --tag plan-approved-2"] * 2)


if __name__ == "__main__":
    unittest.main()
