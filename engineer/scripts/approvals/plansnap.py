"""The plan John approves: the signed files at the exact commit of the plan PR, never the working tree.

A plan ask line is `Approve plan v<N> for <project>? PR https://github.com/<owner>/<repo>/pull/<n>`. The
supervisor asks the broker for that PR's head commit (`pr-head`), fetches it into the broker's mirror
(`sync-mirror P --pr n`), reads each signed file at that commit from the mirror (`git cat-file`, regular
blobs of at most 1 MiB, no symlinks), and commits those exact bytes to engineer-records under
approvals/<p>/v<N>/ with a SNAPSHOT.json (pr, sha, hashes). The ask carries the hashes and the sha;
approve-plan checks the stored bytes against them, so the approval is exactly what John could see.
"""
import hashlib
import json
import os
import re
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

from eng import approval
from supervisor import records

LINE = re.compile(r"^Approve plan v([1-9][0-9]{0,5}) for ")
PR_URL = re.compile(r"https://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)/pull/([1-9][0-9]{0,8})(?![0-9/])")
MAX_BYTES = 1 << 20


class SnapError(Exception):
    """The plan cannot be bound to a commit John can see; the message says why."""


def parse(text: str, repo: str) -> tuple:
    """(version, PR number, PR url) from a plan ask line; SnapError when the PR is not this repo's."""
    m = LINE.match(text)
    if not m:
        raise SnapError("not a plan approval line")
    pr = PR_URL.search(text)
    if not pr or pr.group(1).lower() != repo.lower():
        raise SnapError(f"the line names no PR of {repo}")
    return int(m.group(1)), int(pr.group(2)), pr.group(0)


def _json(res) -> dict:
    rc, out = getattr(res, "returncode", 1), getattr(res, "stdout", "") or ""
    for line in reversed(out.splitlines() if rc == 0 else []):
        try:
            doc = json.loads(line)
        except ValueError:
            continue
        if isinstance(doc, dict):
            return doc
    return {}


def _git(mirror: Path, *args) -> bytes:
    """git on the broker's bare mirror (trusted for this call only), binary stdout."""
    with tempfile.TemporaryDirectory(prefix="plansnap.") as tmp:
        cfg = Path(tmp) / "config"
        subprocess.run(["git", "config", "--file", str(cfg), "safe.directory", str(mirror)], check=True,
                       capture_output=True)
        env = {**os.environ, "GIT_CONFIG_GLOBAL": str(cfg), "GIT_CONFIG_NOSYSTEM": "1", "GIT_TERMINAL_PROMPT": "0"}
        p = subprocess.run(["git", "-c", "core.hooksPath=/dev/null", "--git-dir", str(mirror), *args],
                           capture_output=True, env=env)
    if p.returncode:
        raise SnapError(f"git {args[0]} failed in the mirror")
    return p.stdout


def read_signed(mirror: Path, sha: str) -> dict:
    """{path: bytes} of each signed file at sha in the mirror."""
    out = {}
    for rel in approval.SIGNED:
        entry = _git(mirror, "ls-tree", "-z", "-l", sha, "--", rel).split(b"\0")[0].decode(errors="replace")
        meta = entry.split("\t", 1)[0].split()
        if len(meta) != 4 or meta[1] != "blob" or meta[0] not in ("100644", "100755"):
            raise SnapError(f"{rel} is missing at {sha[:7]} or is not a regular file")
        if not meta[3].isdigit() or int(meta[3]) > MAX_BYTES:
            raise SnapError(f"{rel} is larger than 1 MiB")
        out[rel] = _git(mirror, "cat-file", "blob", meta[2])
    return out


def snapshot(conf: dict, project: str, version: int, pr: int, run) -> dict:
    """Bind plan v<version> to PR pr's head commit; return the ask detail fields. SnapError on any doubt."""
    head = _json(run(["pr-head", project, str(pr)]))
    sha = head.get("head_sha")
    if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise SnapError(f"pr-head gave no head commit for PR {pr}")
    synced = (_json(run(["sync-mirror", project, "--pr", str(pr)])).get("pr") or {}).get("sha")
    if synced != sha:
        raise SnapError(f"PR {pr} moved while it was read ({sha[:7]} then {str(synced)[:7]}); asking again later")
    mirror = Path(conf.get("MIRROR_DIR") or Path(conf["STATE_DIR"]) / "mirrors") / f"{project}.git"
    if mirror.is_symlink() or mirror.parent.is_symlink() or not mirror.is_dir():
        raise SnapError("the broker mirror is missing or a symlink")
    data = read_signed(mirror, sha)
    hashes = {rel: hashlib.sha256(b).hexdigest() for rel, b in data.items()}
    base = f"approvals/{project}/v{version}"
    files = {f"{base}/{rel}": b for rel, b in data.items()}
    files[f"{base}/SNAPSHOT.json"] = json.dumps({"project": project, "version": version, "pr": pr, "sha": sha,
                                                 "files": hashes}, indent=2, sort_keys=True) + "\n"
    res = records.write_files(conf["RECORDS_DIR"], project, files, f"records: plan v{version} at {sha[:12]}",
                              run, email=conf.get("BOT_EMAIL", "engineer-bot@users.noreply.github.com"),
                              mirror_dir=conf.get("MIRROR_DIR"))
    if res["error"] or not res["sha"]:
        raise SnapError(f"the plan snapshot could not be stored: {res['error']}")
    return {"version": version, "pr": pr, "sha": sha, "files": hashes, "snapshot": base,
            "records_sha": res["sha"], "pushed": bool(res["pushed"])}


def commit_url(url: str, sha: str) -> str:
    """The PR's page for this one commit: what John approves, even after the PR moves on."""
    return f"{url}/commits/{sha}"


def text_for(repo: str, url: str, d: dict) -> str:
    """The ask line John sees: version, short sha, the commit's link in the PR (not the PR page, which shows
    its latest head), where the stored files are, short hashes. approve-plan refuses if the head moved."""
    where = f"https://github.com/{repo}/tree/{d['records_sha']}/{d['snapshot']}"
    if not d["pushed"]:
        where += " (records push pending)"
    short = ", ".join(f"{Path(rel).name} {h[:8]}" for rel, h in sorted(d["files"].items()))
    return (f"Approve plan v{d['version']} @ {d['sha'][:7]}? PR {commit_url(url, d['sha'])}; signed files {where} "
            f"({short})")


def approved_version(conf: dict, project: str) -> int:
    """scope_version of the live approval STATE_DIR/approvals/<p>.json; 0 when there is none."""
    try:
        v = json.loads((Path(conf["STATE_DIR"]) / "approvals" / f"{project}.json").read_text())["scope_version"]
    except (OSError, ValueError, KeyError, TypeError):
        return 0
    return v if isinstance(v, int) and not isinstance(v, bool) else 0


def _paced(c, version: int, minutes: int = 30) -> bool:
    """True when a snapshot of this version failed less than minutes ago (no GitHub call every pass)."""
    try:
        last = datetime.fromisoformat((c.dir / f"plan-v{version}.failed").read_text().strip())
    except (OSError, ValueError):
        return False
    return (c.now - last).total_seconds() < minutes * 60


def raise_ask(c, task_id, text: str, seen: set):
    """Raise the plan ask for a PROGRESS.md plan line once per version (asks.py); notes when it cannot."""
    from supervisor import asks, commands
    try:
        version, pr, url = parse(text, c.row["repo"])
    except SnapError as e:
        return asks.note(c, task_id, "plan-line:" + hashlib.sha256(text.encode()).hexdigest()[:16],
                         f"Plan line not asked ({e}): {text}")
    live = approved_version(c.conf, c.name)
    if f"plan:v{version}" in seen or _paced(c, version):
        return None
    if version <= live:
        return asks.note(c, task_id, f"plan-old:v{version}",
                         f"Plan v{version} not asked: the approved plan is v{live}; raise the version.")
    try:
        d = snapshot(c.conf, c.name, version, pr, lambda a: commands.agent_run(c.conf, *a))
    except SnapError as e:
        c.dir.mkdir(parents=True, exist_ok=True)
        (c.dir / f"plan-v{version}.failed").write_text(c.now.isoformat() + "\n")
        return asks.note(c, task_id, f"plan-err:v{version}", f"Plan v{version} not asked yet (retried every "
                         f"30 min): {e}")
    item = asks.ask(c, task_id, "plan", text_for(c.row["repo"], url, d), ref=url, reversible=False,
                    source="progress", key=f"plan:v{version}", **d)
    from approvals import telegram
    telegram.send_items(c, [item], "plan")
    return item
