"""The supervisor's side of the Telegram channel: what John is sent and what his replies do.

- send / send_items: tg-send through the broker; a `notify` event lists the items a message showed, and is
  written only after every tg-send succeeded (a numbered reply must name an item John was sent).
- send_digest: the digest (open T2 prompts, then T1 lines); the `digest` event and last-digest are written
  only after the send succeeded, so a failed send is retried at the next pass.
- reminders: one reminder per open item at t1.reminder_hours.
- apply_all: one apply-replies.py run over every project (item numbers are global), so a reply never answers
  another project's item; timeouts run on every pass, even with no message. A plan yes runs approve-plan (a
  refusal becomes a T1 line sent at once); a merge yes tells John to approve the PR on GitHub, where the
  supervisor's merge pass picks it up.
"""
import subprocess
import sys
from pathlib import Path

from approvals import items, render
from supervisor import commands, events, nightwin, records


def send(c, texts: list) -> bool:
    """tg-send each text; False at the first failure."""
    return all(commands.agent_run(c.conf, "tg-send", stdin=t).returncode == 0 for t in texts if t)


def records_path(c) -> Path:
    """approvals.jsonl in the records clone; STATE_DIR/<p>/approvals.pending.jsonl while there is no clone
    (its lines move into the clone's file once there is one)."""
    pending = c.dir / "approvals.pending.jsonl"
    target = Path(c.conf["RECORDS_DIR"]) / c.name / "decisions" / "approvals.jsonl"
    try:
        records.ensure(c.conf["RECORDS_DIR"], c.name, c.conf.get("MIRROR_DIR"),
                       lambda a: commands.agent_run(c.conf, *a))
    except (records.RecordsError, ValueError, subprocess.CalledProcessError, OSError):
        return pending
    if pending.is_file():
        old = target.read_text() if target.is_file() else ""
        add = [line for line in pending.read_text().splitlines() if line.strip() and line not in old.splitlines()]
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "a") as f:
            f.write(("\n" if old and not old.endswith("\n") else "") + "".join(line + "\n" for line in add))
        pending.unlink()
    return target


def open_items(c) -> dict:
    return items.open_items(items.read_jsonl(c.events), items.read_jsonl(records_path(c)), events.now_iso(c.now))


def send_items(c, nums: list, why: str) -> bool:
    """Send these open items now (a T2 prompt or a T1 line each); record a `notify` event on success."""
    open_ = open_items(c)
    shown = [n for n in nums if n in open_]
    texts = [render.render_t2(open_[n]) if open_[n]["tier"] == "T2" else render.line(open_[n]) for n in shown]
    if not texts or not send(c, texts):
        return False
    c.ev("notify", detail={"items": shown, "why": why})
    return True


def _approvals(c, script, *argv, stdin=None):
    return commands.run([sys.executable, c.root / "scripts" / "approvals" / script, *argv,
                         "--now", events.now_iso(c.now)], stdin)


def send_digest(c, header=None) -> bool:
    """Send the digest (with an optional header line); record it only when every message went out."""
    doc = commands.json_line(_approvals(c, "digest.py", "--events", c.events, "--records", records_path(c),
                                        "--json-object").stdout, (dict, list))
    msgs, shown = (doc.get("messages"), doc.get("shown")) if isinstance(doc, dict) else (doc, None)
    msgs = [m for m in msgs or [] if isinstance(m, str)]
    if not send(c, ([header] if header else []) + msgs):
        return False
    if isinstance(shown, list):
        c.ev("digest", detail={"items": [n for n in shown if isinstance(n, int)]})
    c.dir.mkdir(parents=True, exist_ok=True)
    (c.dir / "last-digest").write_text(nightwin.local_date(c.now, c.tz) + "\n")
    return True


def reminders(c) -> list:
    """Remind John once of each item open at least t1.reminder_hours; return the items reminded."""
    hours = float((c.defaults.get("t1") or {}).get("reminder_hours", 12))
    done = {n for e in items.read_jsonl(c.events) if e.get("event") == "notify"
            and (e.get("detail") or {}).get("why") == "reminder" for n in e["detail"].get("items") or []}
    open_ = open_items(c)
    due = [n for n in items.reminders(open_, events.now_iso(c.now), hours) if n not in done]
    if due and send(c, [render.render_reminder(open_[n]) for n in due]):
        c.ev("notify", detail={"items": due, "why": "reminder"})
        return due
    return []


def _act(c, d: dict) -> None:
    item = items.item_num(d.get("item"))
    if d.get("answer") != "yes" or not item:
        return
    if d.get("kind") == "plan":
        p = commands.run([c.root / "bin" / "approve-plan", c.name, "--record-id", f"item-{item}", "--item", item,
                          "--by", "john", "--source", "telegram"])
        if p.returncode == 0:
            send(c, [f"{c.name}: plan approval for item {item} is live."])
            return
        why = ((p.stderr or "").strip().splitlines() or [f"exit {p.returncode}"])[-1][:200]
        from supervisor import asks
        asks.note(c, None, f"plan-refused:{item}:{p.returncode}", f"Plan approval {item} not applied: {why}",
                  at_once=True)
    elif d.get("kind") == "merge":
        send(c, [f"{c.name}: to merge {d.get('ref') or 'the PR'} (item {item}), approve it on GitHub at its "
                 "audited commit; the supervisor merges it on its next pass."])


def apply_all(ctxs: list, polled: str) -> None:
    """Apply polled replies and timeouts for every project at once; act on the decisions; push records."""
    if not ctxs:
        return
    argv = []
    for c in ctxs:
        argv += ["--events", c.events, "--records", records_path(c)]
    out = _approvals(ctxs[0], "apply-replies.py", *argv, stdin=polled or "").stdout
    by = {c.name: c for c in ctxs}
    for d in (commands.json_line(line) for line in out.splitlines()):
        c = by.get((d or {}).get("project")) or (ctxs[0] if d and len(ctxs) == 1 else None)
        if c is None:
            continue
        if "notice" in d:
            if send(c, [str(d["notice"])]) and items.item_num(d.get("item")):
                c.ev("notify", detail={"items": [d["item"]], "why": "not_understood"})
            continue
        asked = {(e.get("detail") or {}).get("item"): e.get("task_id")
                 for e in events.read(c.events) if e["event"] == "approval_ask"}
        c.ev("approval_answer", d.get("task_id") or asked.get(d.get("item")), detail=d)
        _act(c, d)
    for c in ctxs:
        path = records_path(c)
        if path.is_file() and path.parent.parent == Path(c.conf["RECORDS_DIR"]) / c.name:
            c.push("decisions/approvals.jsonl", path.read_text(), "records: approvals")

