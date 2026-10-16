"""Open task PRs: a task is done only when its audited commit is merged into the default branch.

A PASS pushes task/<id> at the audited sha (push-branch --expect), opens the PR and leaves the task
`in_review` (steps.py). loop.py calls pass_open_prs(conf, project, now) each iteration. For every in_review
task it syncs the broker mirror once, then:
- the mirror's default branch contains the audited sha (merge commit or fast-forward) -> `merge` {merged};
- else it asks `automerge PROJECT PR SHA` (pinned to the audited sha): a squash merge counts once GitHub
  reports the PR merged at that head and the mirror's default branch contains the merge commit; a Tier 2 PR
  that John has approved on GitHub at that sha gets auto-merge now (`merge` {auto_merge}); a PR closed
  without merging makes the task needs_john.
Only a `merge` event with detail.merged makes a task done (events.state), so dependents wait for the merge.
"""
import subprocess
from pathlib import Path

from supervisor import commands, events

SAFE = ["-c", "core.hooksPath=/dev/null", "-c", "core.fsmonitor="]


def _default(conf: dict, project: str) -> str | None:
    path = Path(conf["ETC_DIR"]) / "projects.txt"
    for line in path.read_text().splitlines() if path.exists() else []:
        parts = line.split()
        if len(parts) >= 3 and parts[0] == project:
            return parts[2]
    return None


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


def pass_open_prs(conf: dict, project, now=None) -> list:
    """Check every in_review task's PR once; return the events appended (see the module docstring)."""
    project = project["name"] if isinstance(project, dict) else project
    path = Path(conf["STATE_DIR"]) / project / "events.jsonl"
    evs = events.read(path)
    open_ = sorted(events.state(evs)["in_review"])
    if not open_:
        return []
    commands.agent_run(conf, "sync-mirror", project)  # best effort: a stale mirror only delays `merged`
    mirror, default, out = mirror_path(conf, project), _default(conf, project), []

    def ev(event, tid, sha, **detail):
        out.append(events.append(path, {"ts": events.now_iso(now), "project": project, "event": event,
                                        "task_id": tid, "head_sha": sha, "detail": detail}))

    for tid in open_:
        sha, number, url = _pr(evs, tid)
        if not sha:
            continue
        if contains(mirror, default, sha):
            ev("merge", tid, sha, merged=True, number=number, url=url, merge_commit=sha)
            continue
        m = commands.automerge(conf, project, number, sha)
        if m.get("merged"):
            if m.get("head") == sha and contains(mirror, default, m.get("merge_commit")):
                ev("merge", tid, sha, merged=True, number=number, url=url, merge_commit=m["merge_commit"])
        elif m.get("closed"):
            ev("audit", tid, sha, verdict="NEEDS-JOHN", status="needs_john", audited_sha=sha,
               reason=f"PR {url or number} was closed without merging", lines=["PR closed without merging"])
        elif m.get("auto_merge") and not _auto_on(evs, tid, sha):
            ev("merge", tid, sha, tier=m.get("tier"), auto_merge=True, number=number, url=url)
    return out
