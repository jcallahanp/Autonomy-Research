"""Run the pinned scanners on a diff and report only what the diff adds.

Usage: scanners.py --repo GITDIR --base SHA --head SHA
- gitleaks (always): `gitleaks git --redact` over the commits base..head; one line per leak.
- osv-scanner (when a dependency manifest or lockfile changed): `scan source` on those files at base and at
  head; vulnerability ids present at head but not at base.
- semgrep (when files were added or changed): `scan` on those files at base and at head; a (rule, path) pair
  counted more often at head than at base.
Files are written from git blobs into temp dirs (no checkout, no attributes). Prints `<tool>: ...` lines;
exit 1 on any finding, scanner error or missing scanner, 2 on bad input.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

import checklib

MANIFESTS = {"package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "pyproject.toml", "poetry.lock",
             "uv.lock", "Pipfile.lock", "go.mod", "go.sum", "Cargo.toml", "Cargo.lock", "Gemfile.lock",
             "composer.lock"}
SEMGREP_CONFIG = "p/owasp-top-ten"
TOOLS = ("gitleaks", "osv-scanner", "semgrep")


def is_manifest(path: str) -> bool:
    name = path.rsplit("/", 1)[-1]
    return name in MANIFESTS or (name.startswith("requirements") and name.endswith(".txt"))


def run(argv, cwd=None):
    env = dict(os.environ, SEMGREP_ENABLE_VERSION_CHECK="0", SEMGREP_SEND_METRICS="off")
    return subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True, timeout=900)


def gitleaks(gitdir, base, head, tmp) -> list:
    report = Path(tmp) / "gitleaks.json"
    r = run(["gitleaks", "git", "--redact", "--no-banner", "--exit-code", "0", "--report-format", "json",
             "--report-path", str(report), f"--log-opts={base}..{head}", str(gitdir)])
    if r.returncode != 0 or not report.exists():
        return [f"gitleaks: error (exit {r.returncode})"]
    return [f"gitleaks: {f.get('File')}:{f.get('StartLine')} {f.get('RuleID')}"
            for f in json.loads(report.read_text() or "[]")]


def osv_ids(tree: Path, files: list):
    """{(id, package)} at one tree, or None on a scanner error."""
    if not files:
        return set()
    r = run(["osv-scanner", "scan", "source", "--format", "json", str(tree)])
    if r.returncode == 128:
        return set()
    if r.returncode not in (0, 1):
        return None
    out = set()
    for res in json.loads(r.stdout or "{}").get("results") or []:
        for pkg in res.get("packages") or []:
            name = (pkg.get("package") or {}).get("name", "?")
            out.update((v.get("id"), name) for v in pkg.get("vulnerabilities") or [])
    return out


def semgrep_hits(tree: Path, files: list):
    """Counter of (rule, path) at one tree, or None on a scanner error."""
    if not files:
        return Counter()
    # "./" keeps an engineer-chosen file name such as "-x.py" from reading as an option.
    r = run(["semgrep", "scan", "--config", SEMGREP_CONFIG, "--json", "--metrics=off", "--quiet",
             *[f"./{f}" for f in files]], cwd=tree)
    if r.returncode not in (0, 1):
        return None
    hits = json.loads(r.stdout or "{}").get("results") or []
    return Counter((h.get("check_id"), str(h.get("path")).removeprefix("./")) for h in hits)


def scan(gitdir, base, head) -> list:
    missing = [t for t in TOOLS if shutil.which(t) is None]
    if missing:
        return [f"{t}: not installed" for t in missing]
    changed = checklib.changes(gitdir, base, head)
    deps = any(is_manifest(p) for _, p in changed)
    code = {p for s, p in changed if s != "D"}
    with tempfile.TemporaryDirectory() as tmp:
        lines = gitleaks(gitdir, base, head, tmp)
        trees = {}
        for name, sha in (("base", base), ("head", head)):
            d = Path(tmp) / name
            d.mkdir()
            got = checklib.extract(gitdir, sha, lambda p: (deps and is_manifest(p)) or p in code, d)
            trees[name] = (d, [p for p in got if is_manifest(p)], [p for p in got if p in code])
        if deps:
            before, after = osv_ids(*trees["base"][:2]), osv_ids(*trees["head"][:2])
            if before is None or after is None:
                lines.append("osv-scanner: error")
            else:
                lines += [f"osv-scanner: new {i} ({pkg})" for i, pkg in sorted(after - before)]
        if code:
            before = semgrep_hits(trees["base"][0], trees["base"][2])
            after = semgrep_hits(trees["head"][0], trees["head"][2])
            if before is None or after is None:
                lines.append("semgrep: error")
            else:
                lines += [f"semgrep: {p} {rule}" for (rule, p), n in sorted(after.items()) if n > before[(rule, p)]]
    return lines


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Run gitleaks, osv-scanner and semgrep on a diff.")
    ap.add_argument("--repo", required=True)
    ap.add_argument("--base", required=True)
    ap.add_argument("--head", required=True)
    args = ap.parse_args(argv)
    try:
        lines = scan(Path(args.repo).resolve(), checklib.check_sha(args.base), checklib.check_sha(args.head))
    except (ValueError, subprocess.CalledProcessError) as exc:
        print(f"scanners: {exc}", file=sys.stderr)
        return 2
    except subprocess.TimeoutExpired as exc:
        lines = [f"{Path(exc.cmd[0]).name}: timed out"]
    for line in lines:
        print(line)
    return 1 if lines else 0


if __name__ == "__main__":
    sys.exit(main())
