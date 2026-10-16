"""T1 asks the supervisor raises, and the answers it acts on.

- merge: a Tier 2 PR (steps._verify).
- relogin: a browser challenge the run reported as `BLOCKED: browser challenge kind=K host=H url=U`
  (browser skill); the task is blocked until John answers y.
- other / plan: each new line under `## Asks for John` in PROGRESS.md (digest skill), read as a plain file
  from the task worktree and the clone (never git, never through a symlink). A line starting
  `Approve plan v<N> for` becomes the plan item and carries the sha256 of each signed file as it is now;
  approve-plan refuses if any differs when John answers (he approves exactly what he saw).
"""
import hashlib
import json
import os
import re
import stat
from pathlib import Path

from approvals import items
from eng import approval
from supervisor import commands, events

CHALLENGE = re.compile(r"(?m)^[ \t]*BLOCKED: browser challenge kind=([a-z][a-z0-9_]{0,40}) "
                       r"host=([A-Za-z0-9.-]{1,253}) url=(https?://\S{1,500})[ \t]*$")
PLAN = re.compile(r"^Approve plan v[0-9]+ for ")
URL = re.compile(r"https://\S{1,500}")
SECTION = "## Asks for John"
MAX_TEXT, MAX_NEW, MAX_BYTES = 300, 5, 1 << 20


def ask(c, task_id, kind, text, ref=None, reversible=True, **extra) -> int:
    """Append a T1 approval_ask (default n) with the next item number; return the number."""
    item = items.next_item(events.read(c.events))
    c.ev("approval_ask", task_id, detail={"item": item, "tier": "T1", "kind": kind, "text": text, "default": "n",
                                          "reversible": reversible, "ref": ref, **extra})
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
    text = (f"Re-login or clear the {ch['kind']} challenge on {ch['host']} in noVNC ({c.name} task {task_id}); "
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


def signed_hashes(clone: Path) -> dict:
    """{path: sha256} for each signed file that is a regular file (no symlink) of at most 1 MiB."""
    out = {}
    for rel in approval.SIGNED:
        data = _open_plain(clone / rel, MAX_BYTES)
        if data is not None:
            out[rel] = hashlib.sha256(data).hexdigest()
    return out


def from_progress(c, task_id=None) -> list:
    """Raise each new PROGRESS.md ask line (at most MAX_NEW per call) from the task worktree, when a task
    is named, and the clone; return the new item numbers."""
    base = Path(os.path.realpath(c.conf["PROJECTS_DIR"]))
    seen = {(e.get("detail") or {}).get("key") for e in events.read(c.events) if e["event"] == "approval_ask"}
    new = []
    for d in ([base / f"{c.name}.wt" / task_id] if task_id else []) + [base / c.name]:
        if os.path.realpath(d) != str(d):
            continue
        data = _open_plain(d / "PROGRESS.md", MAX_BYTES)
        for text in ask_lines(data.decode("utf-8", "replace") if data else ""):
            plan = bool(PLAN.match(text))
            files = signed_hashes(base / c.name) if plan else None
            key = hashlib.sha256(json.dumps([text, files], sort_keys=True).encode()).hexdigest()[:16]
            if key in seen or len(new) >= MAX_NEW:
                continue
            seen.add(key)
            if plan:
                m = URL.search(text)
                new.append(ask(c, task_id, "plan", text, ref=m.group(0) if m else None, reversible=False,
                               source="progress", key=key, files=files))
            else:
                new.append(ask(c, task_id, "other", text, source="progress", key=key))
    return new


def apply_replies(c, polled: str) -> None:
    """Apply John's polled replies; a plan yes runs approve-plan; push approvals.jsonl to engineer-records."""
    if not polled.strip():
        return
    c.records_file.parent.mkdir(parents=True, exist_ok=True)
    asked = {(e.get("detail") or {}).get("item"): e.get("task_id")
             for e in events.read(c.events) if e["event"] == "approval_ask"}
    for d in commands.poll_replies(c, polled):
        c.ev("approval_answer", asked.get(d.get("item")), detail=d)
        if d.get("kind") == "plan" and d.get("answer") == "yes" and items.item_num(d.get("item")):
            commands.approve_plan(c, items.item_num(d["item"]))
    if c.records_file.exists():
        c.push("decisions/approvals.jsonl", c.records_file.read_text(), "records: approvals")
