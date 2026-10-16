"""Open task PRs: a task is done only when its audited commit is merged into the default branch.

A PASS pushes task/<id> at the audited sha (push-branch --expect), opens the PR and leaves the task
`in_review` (steps.py). loop.py calls pass_open_prs(conf, project, now) each iteration. For every in_review
task it syncs the broker mirror once, then:
- the mirror's default branch contains the audited sha (merge commit or fast-forward) -> `merge` {merged};
- else it asks `automerge PROJECT PR SHA` (pinned to the audited sha): a squash merge counts once GitHub
  reports the PR merged at that head and the mirror's default branch contains the merge commit; a Tier 2 PR
  that John has approved on GitHub at that sha gets auto-merge now (`merge` {auto_merge}); a PR closed
  without merging makes the task needs_john.
- a PR merged at another head, or whose head moved away from the audited sha, makes the task needs_john once
  (asks.deadends turns that into one T1 line); a merge made by the project's owner_login counts as done, with
  a `note` in the merge event for MORNING.md (automerge's `merged_by`).
When a task is merged, its open `merge` asks are closed: an approval_answer {answer: merged, by: system} event
and an approval record (answer yes, source pr) in STATE_DIR/<p>/approvals.pending.jsonl, which
telegram.records_path moves into the records clone.
Only a `merge` event with detail.merged makes a task done (events.state), so dependents wait for the merge.
"""
import json
import subprocess
from pathlib import Path

from approvals import items
from eng import schema
from supervisor import commands, events

ROOT = Path(__file__).resolve().parents[2]
SAFE = ["-c", "core.hooksPath=/dev/null", "-c", "core.fsmonitor="]


def _row(conf: dict, project: str) -> dict:
    """projects.txt row: {"default", "owner_login", ...}; {} when the project is not listed."""
    path = Path(conf["ETC_DIR"]) / "projects.txt"
    for line in path.read_text().splitlines() if path.exists() else []:
        parts = line.split()
        if len(parts) >= 3 and parts[0] == project:
            return {"default": parts[2], **dict(p.split("=", 1) for p in parts[3:] if "=" in p)}
    return {}


def mirror_path(conf: dict, project: str) -> Path:
    return Path(conf.get("MIRROR_DIR") or Path(conf["STATE_DIR"]) / "mirrors") / f"{project}.git"


def contains(mirror: Path, default: str | None, sha: str | None) -> bool:
    """True when the mirror's refs/heads/<default> has commit sha (the broker owns the mirror; we only read)."""
    if not default or not sha or not mirror.is_dir():
        return False
    argv = ["git", *SAFE, "-c", f"safe.directory={mirror}", f"--git-dir={mirror}", "merge-base", "--is-ancestor",
            sha, f"refs/heads/{default}"]
    return subprocess.run(argv, capture_output=True, env={"GIT_CONFIG_NOSYSTEM": "1", "PATH": "/usr/bin:/bin"}
                          ).returncode == 0


def _pr(evs: list, tid: str) -> tuple:
    """(audited sha, PR number, url) from the task's last pr_open event, or (None, None, None)."""
    for e in reversed(evs):
        if e.get("task_id") == tid and e["event"] == "pr_open":
            d = e.get("detail") or {}
            if isinstance(d.get("number"), int) and e.get("head_sha"):
                return e["head_sha"], d["number"], d.get("url")
            break
    return None, None, None


def _auto_on(evs: list, tid: str, sha: str) -> bool:
    return any(e.get("task_id") == tid and e["event"] == "merge" and e.get("head_sha") == sha
               and (e.get("detail") or {}).get("auto_merge") for e in evs)


def auto_merging(evs: list, tids) -> bool:
    """True when GitHub auto-merge is on for the audited sha of any of these tasks' open PRs."""
    return any(_auto_on(evs, tid, _pr(evs, tid)[0]) for tid in tids if _pr(evs, tid)[0])


def close_asks(conf: dict, project: str, tid: str, now=None, why="merged on GitHub") -> list:
    """Answer the task's open merge asks for the system (the PR is merged); return the events appended."""
    path = Path(conf["STATE_DIR"]) / project / "events.jsonl"
    pending, evs = path.parent / items.PENDING, events.read(path)
    records = items.answers(path, Path(conf["RECORDS_DIR"]) / project / "decisions" / "approvals.jsonl")
    out, rec_schema = [], schema.load(ROOT, "approval-record")
    for n, it in sorted(items.open_items(evs, records, events.now_iso(now)).items()):
        if it.get("kind") != "merge" or it.get("task_id") != tid:
            continue
        rec = items.record(it, events.now_iso(now), "yes", "pr", raw=why)
        if schema.validate(rec, rec_schema):
            continue
        with open(pending, "a") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        out.append(events.append(path, {"ts": events.now_iso(now), "project": project, "event": "approval_answer",
                                        "task_id": tid, "detail": {"item": n, "kind": "merge", "answer": "merged",
                                                                   "by": "system", "source": "pr", "raw": why}}))
    return out


def pass_open_prs(conf: dict, project, now=None) -> list:
    """Check every in_review task's PR once; return the events appended (see the module docstring)."""
    project = project["name"] if isinstance(project, dict) else project
    path = Path(conf["STATE_DIR"]) / project / "events.jsonl"
    evs = events.read(path)
    open_ = sorted(events.state(evs)["in_review"])
    if not open_:
        return []
    commands.agent_run(conf, "sync-mirror", project)  # best effort: a stale mirror only delays `merged`
    row = _row(conf, project)
    mirror, default, owner, out = mirror_path(conf, project), row.get("default"), row.get("owner_login"), []

    def ev(event, tid, sha, **detail):
        out.append(events.append(path, {"ts": events.now_iso(now), "project": project, "event": event,
                                        "task_id": tid, "head_sha": sha, "detail": detail}))

    def merged(tid, sha, **detail):
        ev("merge", tid, sha, merged=True, **detail)
        out.extend(close_asks(conf, project, tid, now))

    def needs_john(tid, sha, reason, line):
        ev("audit", tid, sha, verdict="NEEDS-JOHN", status="needs_john", audited_sha=sha, reason=reason[:300],
           lines=[line])

    for tid in open_:
        sha, number, url = _pr(evs, tid)
        if not sha:
            continue
        pr = f"PR {url or number}"
        if contains(mirror, default, sha):
            merged(tid, sha, number=number, url=url, merge_commit=sha)
            continue
        m = commands.automerge(conf, project, number, sha)
        head = m.get("head") if isinstance(m.get("head"), str) else None
        moved = [str(r) for r in m.get("reasons") or [] if str(r).startswith("head moved")]
        if m.get("merged") and (head == sha or (owner and m.get("merged_by") == owner)):
            if contains(mirror, default, m.get("merge_commit")):
                note = {} if head == sha else {"note": f"John ({owner}) merged {pr} himself at {str(head)[:12]}, "
                                                       f"not the audited {sha[:12]}", "merged_head": head}
                merged(tid, sha, number=number, url=url, merge_commit=m["merge_commit"], **note)
        elif m.get("merged"):
            needs_john(tid, sha, f"{pr} was merged at an unaudited head {str(head)[:12]} (audited {sha[:12]}, "
                       f"merged by {m.get('merged_by') or 'unknown'}); check the merge", "merged at an unaudited head")
        elif m.get("closed"):
            needs_john(tid, sha, f"{pr} was closed without merging", "PR closed without merging")
        elif moved:
            needs_john(tid, sha, f"{pr}: {moved[0]}; nothing merges until John decides", "head moved")
        elif m.get("auto_merge") and not _auto_on(evs, tid, sha):
            ev("merge", tid, sha, tier=m.get("tier"), auto_merge=True, number=number, url=url)
    return out
