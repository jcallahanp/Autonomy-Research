"""Compare the env var names in docs/plan/integrations.yaml with the names in .env.example.

Usage: integrations-env.py --repo DIR
Prints `missing: NAME` (in integrations.yaml, not in .env.example) and `extra: NAME` (the reverse);
exit 1 on any, 2 when integrations.yaml cannot be read. Names only: values are never read or printed.
"""
import argparse
import re
import sys
from pathlib import Path

import yaml

ENV_LINE = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=")


def declared(path: Path) -> set:
    data = yaml.safe_load(path.read_text()) or {}
    names = set()
    for svc in data.get("services") or []:
        for name in (svc or {}).get("env_vars") or []:
            names.add(str(name))
    return names


def example(path: Path) -> set:
    if not path.is_file():
        return set()
    names = set()
    for line in path.read_text().splitlines():
        m = ENV_LINE.match(line)
        if m and not line.lstrip().startswith("#"):
            names.add(m.group(1))
    return names


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="integrations.yaml env_vars vs .env.example")
    ap.add_argument("--repo", required=True)
    args = ap.parse_args(argv)
    repo = Path(args.repo)
    try:
        want = declared(repo / "docs" / "plan" / "integrations.yaml")
    except (OSError, yaml.YAMLError, AttributeError, TypeError) as exc:
        print(f"integrations-env: cannot read integrations.yaml ({type(exc).__name__})", file=sys.stderr)
        return 2
    have = example(repo / ".env.example")
    lines = [f"missing: {n}" for n in sorted(want - have)] + [f"extra: {n}" for n in sorted(have - want)]
    for line in lines:
        print(line)
    return 1 if lines else 0


if __name__ == "__main__":
    sys.exit(main())
