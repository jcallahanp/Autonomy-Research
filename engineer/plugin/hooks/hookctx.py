"""Shared context for the engineer hooks.

Hook contract (checked 2026-10-16 against https://code.claude.com/docs/en/hooks): Claude Code
sends one JSON object on stdin with the common fields `session_id`, `transcript_path`, `cwd`,
`permission_mode` and `hook_event_name`; PreToolUse/PostToolUse add `tool_name`, `tool_input`
(Bash: `command`; Write: `file_path`, `content`; Edit: `file_path`, `old_string`, `new_string`)
and `tool_use_id`; Stop adds `stop_hook_active`; TaskCompleted adds `task_id`, `task_subject`;
StopFailure adds `error`; Notification adds `message`, `notification_type`. Exit 2 blocks the
tool call (PreToolUse), keeps Claude going (Stop) or keeps a task open (TaskCompleted), and
stderr is fed to Claude as the reason. Commands run with `python3 -I`, so this file puts the
engineer libraries on sys.path itself.

The root is found from this file's path, not from CLAUDE_PLUGIN_ROOT: the locked droplet runs
these hooks from managed settings, where that variable is not set.
"""
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for _p in (ROOT / "scripts", Path(__file__).resolve().parent):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from eng import conf as engconf  # noqa: E402

FILE_TOOLS = ("Edit", "Write", "MultiEdit", "NotebookEdit")


class Ctx:
    """root, conf, cwd, project_dir (git top level or None), project (main clone name), unattended."""

    def __init__(self, root, conf, cwd, project_dir, project, unattended):
        self.root, self.conf, self.cwd = root, conf, cwd
        self.project_dir, self.project, self.unattended = project_dir, project, unattended


def read_event() -> dict:
    """The hook input; raise ValueError when stdin is not one JSON object."""
    event = json.loads(sys.stdin.read())
    if not isinstance(event, dict):
        raise ValueError("hook input is not a JSON object")
    return event


def git_top(start: Path) -> Path | None:
    """The nearest directory at or above start holding `.git` (a dir, or a file in a worktree)."""
    for d in (start, *start.parents):
        if os.path.lexists(d / ".git"):
            return d
    return None


def project_name(project_dir: Path | None) -> str | None:
    """`<p>` for the main clone `<p>` and for a task worktree `<p>.wt/<id>`."""
    if project_dir is None:
        return None
    parent = project_dir.parent.name
    if parent.endswith(".wt") and len(parent) > 3:
        return parent[:-3]
    return project_dir.name


def load(event: dict, root: Path = ROOT) -> Ctx:
    cwd = Path(os.path.realpath(event.get("cwd") or os.getcwd()))
    top = git_top(cwd)
    return Ctx(root=root, conf=engconf.load(root), cwd=cwd, project_dir=top,
               project=project_name(top), unattended=os.environ.get("ENGINEER_UNATTENDED") == "1")


def tool_path(event: dict) -> str | None:
    """The file a file-writing tool targets, or None for any other tool."""
    if event.get("tool_name") not in FILE_TOOLS:
        return None
    ti = event.get("tool_input") or {}
    path = ti.get("file_path") or ti.get("notebook_path")
    return str(path) if path else ""


def resolve(path: str, base: Path) -> Path:
    """Absolute path with every symlink resolved (also through not-yet-existing tails)."""
    p = Path(os.path.expanduser(path))
    return Path(os.path.realpath(p if p.is_absolute() else base / p))


def rel_to(real: Path, project_dir: Path) -> str | None:
    """The project-relative path of an already resolved path, or None when it is outside."""
    top = Path(os.path.realpath(project_dir))
    try:
        rel = real.relative_to(top)
    except ValueError:
        return None
    return rel.as_posix()


def safe_id(value) -> str:
    """A file-name-safe form of a session id."""
    text = re.sub(r"[^A-Za-z0-9_-]", "_", str(value or "unknown"))[:80]
    return text.strip("_") or "unknown"


def now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def spool(conf: dict, session_id, record: dict) -> None:
    """Append one JSON line to SPOOL_DIR/<session_id>.jsonl in a single write."""
    path = Path(conf["SPOOL_DIR"]) / f"{safe_id(session_id)}.jsonl"
    line = (json.dumps(record, sort_keys=True) + "\n").encode()
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o640)
    try:
        os.write(fd, line)
    finally:
        os.close(fd)


def tap_record(event: dict, ctx: "Ctx | None", detail: dict) -> dict:
    project = (ctx.project if ctx else None) or os.environ.get("ENGINEER_PROJECT")
    return {"ts": now_iso(), "session_id": event.get("session_id"),
            "hook_event_name": event.get("hook_event_name"), "project": project,
            "task_id": os.environ.get("ENGINEER_TASK_ID"), "detail": detail}
