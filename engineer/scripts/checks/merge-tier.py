"""Classify a PR as merge Tier 1 (self-merge) or Tier 2 (John's own review) (engineer-protocol §Q5).

Usage: merge-tier.py [--tier2 FILE] [--protected FILE] < {"title": str, "files": [{"path", "additions", "deletions"}]}
Prints {"tier": 1|2, "reasons": [...]}; exit 0, or 2 on bad input.
Tier 1 only when: the Conventional Commit type is docs, test, chore, style, fix, feat or refactor; no `!` and
no BREAKING; at most 20 files; at most 1000 changed lines; no path in tier2-paths.txt or protected [always].
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from eng import paths  # noqa: E402

TIER1_TYPES = ("docs", "test", "chore", "style", "fix", "feat", "refactor")
TITLE = re.compile(r"^([a-z]+)(\([^)]*\))?(!)?: \S")
MAX_FILES = 20
MAX_LINES = 1000


def load_patterns(path: Path) -> list:
    return [s for s in (ln.strip() for ln in path.read_text().splitlines()) if s and not s.startswith("#")]


def classify(pr: dict, tier2: list, always: list) -> dict:
    reasons = []
    title = pr.get("title") or ""
    m = TITLE.match(title)
    if not m:
        reasons.append("title is not a Conventional Commit title")
    elif m.group(1) not in TIER1_TYPES:
        reasons.append(f"type '{m.group(1)}' is not a Tier 1 type")
    if (m and m.group(3)) or "BREAKING" in title:
        reasons.append("breaking change")
    files = pr.get("files") or []
    if len(files) > MAX_FILES:
        reasons.append(f"{len(files)} files (Tier 1 allows {MAX_FILES})")
    lines = sum(int(f.get("additions") or 0) + int(f.get("deletions") or 0) for f in files)
    if lines > MAX_LINES:
        reasons.append(f"{lines} changed lines (Tier 1 allows {MAX_LINES})")
    for f in files:
        path = paths.normalise(str(f.get("path") or ""))
        if path is None:
            reasons.append(f"path outside the project: {f.get('path')!r}")
            continue
        hit = next((p for p in always if paths.match(path, p)), None)
        if hit:
            reasons.append(f"{path} is protected ({hit})")
            continue
        hit = next((p for p in tier2 if paths.match(path, p)), None)
        if hit:
            reasons.append(f"{path} is a Tier 2 path ({hit})")
    return {"tier": 2 if reasons else 1, "reasons": reasons}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Classify a PR's merge tier.")
    ap.add_argument("--tier2", default=str(ROOT / "templates" / "tier2-paths.txt"))
    ap.add_argument("--protected", default=str(ROOT / "templates" / "protected-paths.txt"))
    args = ap.parse_args(argv)
    try:
        pr = json.loads(sys.stdin.read())
        if not isinstance(pr, dict) or not isinstance(pr.get("files", []), list):
            raise ValueError("expected an object with a files list")
        out = classify(pr, load_patterns(Path(args.tier2)), paths.load(Path(args.protected))["always"])
    except (ValueError, TypeError, AttributeError, OSError) as exc:
        print(f"merge-tier: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
