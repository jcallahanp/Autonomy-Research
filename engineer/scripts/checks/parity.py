"""Check that docs/plan/architecture.yaml and docs/plan/architecture.mmd name the same nodes.

Usage: parity.py --repo DIR
YAML ids: nodes[].id. Mermaid ids: lines matching ^\\s*([A-Za-z0-9_]+)[\\[\\(\\{] (node definitions).
Prints `missing in mmd: ID` and `missing in yaml: ID`; exit 1 on any mismatch, 2 when a file cannot be read.
"""
import argparse
import re
import sys
from pathlib import Path

import yaml

MMD_NODE = re.compile(r"^\s*([A-Za-z0-9_]+)[\[\(\{]")


def yaml_ids(path: Path) -> set:
    data = yaml.safe_load(path.read_text()) or {}
    return {str(n["id"]) for n in data.get("nodes") or [] if isinstance(n, dict) and "id" in n}


def mmd_ids(path: Path) -> set:
    return {m.group(1) for m in map(MMD_NODE.match, path.read_text().splitlines()) if m}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="architecture.yaml vs architecture.mmd node ids")
    ap.add_argument("--repo", required=True)
    args = ap.parse_args(argv)
    plan = Path(args.repo) / "docs" / "plan"
    try:
        y = yaml_ids(plan / "architecture.yaml")
        m = mmd_ids(plan / "architecture.mmd")
    except (OSError, yaml.YAMLError, AttributeError, TypeError) as exc:
        print(f"parity: cannot read the architecture files ({type(exc).__name__})", file=sys.stderr)
        return 2
    lines = [f"missing in mmd: {i}" for i in sorted(y - m)] + [f"missing in yaml: {i}" for i in sorted(m - y)]
    for line in lines:
        print(line)
    return 1 if lines else 0


if __name__ == "__main__":
    sys.exit(main())
