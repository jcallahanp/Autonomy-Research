"""The asks the supervisor raises (approval_ask events; numbers global across projects).

- merge: a Tier 2 PR (steps._verify). A yes tells John to approve it on GitHub (approvals/telegram.py).
- relogin: a browser challenge the run reported as `BLOCKED: browser challenge kind=K host=H url=U`.
- deadend: a task that ended `blocked` or `needs_john` (not by a challenge); John's yes resets it to ready.
- plan: a line `Approve plan v<N> for <project>? PR <url>` under `## Asks for John` in PROGRESS.md, bound to the
  PR's head commit (approvals/plansnap.py); never raised twice for one version, never for N <= the approved
  version. Irreversible, so neither a timeout nor `all y` answers it. Sent to John at once.
- T2 hard gate: a line `HARD GATE: <money|delete|appstore|promote> <text> [CONFIRM: <PHRASE>]`; sent at
  once, approved only by `CONFIRM <item> <PHRASE>` (default phrase MONEY|DELETE|STORE|PROMOTE <item>),
  never by a default or a timeout.
- other: any other ask line, and notes the supervisor owes John (a refused plan, a failed records push).
PROGRESS.md is read as a plain file from the task worktree and the clone (never git, never via a symlink).
"""
import hashlib
import json
import os
import re
import stat
from pathlib import Path

from approvals import items, plansnap, telegram
from supervisor import commands, events, records

CHALLENGE = re.compile(r"(?m)^[ \t]*BLOCKED: browser challenge kind=([a-z][a-z0-9_]{0,40}) "
                       r"host=([A-Za-z0-9.-]{1,253}) url=(https?://\S{1,500})[ \t]*$")
GATE = re.compile(r"^HARD GATE: (money|delete|appstore|promote) (.+?)(?: CONFIRM: ([A-Za-z0-9][A-Za-z0-9 $._/-]{1,39}))?$")
GATES = {"money": "money", "delete": "delete_data", "appstore": "store_submission", "promote": "promote"}
SECTION = "## Asks for John"
MAX_TEXT, MAX_NEW, MAX_BYTES = 300, 5, 1 << 20
STOPPED_EXIT = 75  # run-task's exit when the kill switch stopped the run


def stopped(result: dict) -> bool:
    """True when run-task ended because STOP exists: the night stops; it is not a failed attempt."""
    return isinstance(result, dict) and result.get("exit_code") == STOPPED_EXIT


def ask(c, task_id, kind, text, ref=None, reversible=True, tier="T1", **extra) -> int:
    """Append an approval_ask (default n) with the next global item number; return the number."""
    item = items.next_global(c.conf["STATE_DIR"])
    detail = {"item": item, "tier": tier, "kind": kind, "text": text, "default": "n", "reversible": reversible,
              "ref": ref, **extra}
    if tier == "T2" and not detail.get("phrase"):
        detail["phrase"] = f"{str(extra.get('gate', 'gate')).split('_')[0].upper()} {item}"
    c.ev("approval_ask", task_id, detail=detail)
    return item


def note(c, task_id, key, text, at_once=False) -> int | None:
    """A T1 `other` line raised once per key; sent at once when asked."""
    if key in _keys(c):
        return None
    item = ask(c, task_id, "other", text[:MAX_TEXT], key=key)
    if at_once:
        telegram.send_items(c, [item], "note")
    return item


def challenge(tail) -> dict | None:
    """{kind, host, url} from a BLOCKED line in the run's output (raw, or inside claude's JSON result)."""
    texts = [tail or ""]
    for line in (tail or "").splitlines():
        try:
            doc = json.loads(line)
        except ValueError:
            continue
        if isinstance(doc, dict) and isinstance(doc.get("result"), str):
            texts.append(doc["result"])
    for text in texts:
        m = CHALLENGE.search(text)
        if m:
            return {"kind": m.group(1), "host": m.group(2), "url": m.group(3)}
    return None


def relogin(c, task_id, ch: dict) -> int:
    text = (f"Re-login or clear the {ch['kind']} challenge on {ch['host']} in noVNC (task {task_id}); "
            "y retries the task.")
    return ask(c, task_id, "relogin", text, ref=ch["url"])


def _open_plain(path: Path, limit: int) -> bytes | None:
    """A regular file's bytes (at most limit), opened without following a symlink; None otherwise."""
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except OSError:
        return None
    with os.fdopen(fd, "rb") as f:
        if not stat.S_ISREG(os.fstat(f.fileno()).st_mode):
            return None
        data = f.read(limit + 1)
    return data if len(data) <= limit else None


def one_line(text: str) -> str:
    """Whitespace and control characters collapsed, as digest.one_line renders an item."""
    return " ".join("".join(ch if ch.isprintable() else " " for ch in text).split())


def ask_lines(text: str) -> list:
    """One-line texts under every `## Asks for John` heading (bullets stripped)."""
    out, inside = [], False
    for line in text.splitlines():
        if line.startswith("#"):
            inside = line.strip() == SECTION
            continue
        t = one_line(re.sub(r"^\s*[-*]\s+", "", line)) if inside else ""
        if t:
            out.append(t[:MAX_TEXT])
    return out


def _keys(c) -> set:
    return {(e.get("detail") or {}).get("key") for e in events.read(c.events) if e["event"] == "approval_ask"}


def _hash(*parts) -> str:
    return hashlib.sha256(json.dumps(list(parts), sort_keys=True).encode()).hexdigest()[:16]


def from_progress(c, task_id=None) -> list:
    """Raise each new PROGRESS.md ask line (at most MAX_NEW per call) from the task worktree, when a task
    is named, and the clone; return the new item numbers."""
    base = Path(os.path.realpath(c.conf["PROJECTS_DIR"]))
    seen, new = _keys(c), []
    for d in ([base / f"{c.name}.wt" / task_id] if task_id else []) + [base / c.name]:
        if os.path.realpath(d) != str(d):
            continue
        data = _open_plain(d / "PROGRESS.md", MAX_BYTES)
        for text in ask_lines(data.decode("utf-8", "replace") if data else ""):
            key = _hash(text, None)
            if len(new) >= MAX_NEW or key in seen:
                continue
            seen.add(key)
            gate = GATE.match(text)
            if plansnap.LINE.match(text):
                n = plansnap.raise_ask(c, task_id, text, seen)
                seen |= _keys(c)
            elif gate:
                n = ask(c, task_id, "other", gate.group(2), tier="T2", source="progress", key=key,
                        gate=GATES[gate.group(1)], phrase=gate.group(3))
                telegram.send_items(c, [n], "hard_gate")
            else:  # a malformed HARD GATE line is never reversible: no timeout, no `all y`
                n = ask(c, task_id, "other", text, source="progress", key=key,
                        reversible=not text.upper().startswith("HARD GATE"))
            new += [n] if n else []
    return new


def deadends(c) -> list:
    """A T1 deadend ask for each task whose last outcome is blocked or needs_john (not a browser challenge)."""
    evs, keys, new = events.read(c.events), _keys(c), []
    last = {e["task_id"]: e for e in evs if e["event"] == "audit" and e.get("task_id")
            and (e.get("detail") or {}).get("status")}
    for tid, e in last.items():
        d, key = e["detail"], f"deadend:{tid}:{e['ts']}"
        if d["status"] in ("blocked", "needs_john") and key not in keys and not str(
                d.get("reason", "")).startswith("browser challenge"):
            why = one_line(str(d.get("reason") or "no reason recorded"))[:160]
            new.append(ask(c, tid, "deadend", f"Unblock {tid} ({d['status']}): {why}. y sets it ready again.",
                           key=key))
    return new


def unblocked(evs: list) -> set:
    """Tasks John answered yes on a deadend ask after their last outcome: ready again."""
    out = set()
    for e in evs:
        d = e.get("detail") or {}
        if e["event"] == "audit" and e.get("task_id") and d.get("status"):
            out.discard(e["task_id"])
        elif e["event"] == "approval_answer" and d.get("kind") == "deadend" and d.get("answer") == "yes":
            out.add(e.get("task_id"))
    return out


def records_health(c) -> None:
    """Retry a failed engineer-records push; tell John once per distinct failure."""
    run = lambda a: commands.agent_run(c.conf, *a)  # noqa: E731
    if records.retry_push(c.conf["RECORDS_DIR"], c.name, run):
        return
    why = records.failure(c.conf["RECORDS_DIR"], c.name) or "unknown"
    note(c, None, "records:" + _hash(why), f"engineer-records for {c.name} is not pushed ({why[:120]}); "
         "the supervisor retries each pass. Check the broker and GitHub.")
