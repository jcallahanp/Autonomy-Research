"""How many tests a check run reports (F25), and whether a stored check result is good evidence.

parse(text) -> int | None, trying in order: explicit TESTS_RUN=<n>; jest `Tests: ... <n> passed`;
vitest `Tests  <n> passed`; pytest `<n> passed`; unittest `Ran <n> tests`; node test runner `# pass <n>`;
bats/TAP `1..<n>`. The last match of the first format found wins.
CLI: testcount.py --result FILE --head SHA  prints one line per problem with the check result; exit 1 on any.
"""
import argparse
import json
import re
import sys
from pathlib import Path

PATTERNS = [
    re.compile(r"^\s*TESTS_RUN=(\d+)\s*$", re.M),
    re.compile(r"^\s*Tests:\s.*?(\d+) passed", re.M),
    re.compile(r"^\s*Tests\s+(\d+) passed", re.M),
    re.compile(r"\b(\d+) passed\b"),
    re.compile(r"^Ran (\d+) tests? in ", re.M),
    re.compile(r"^[#ℹ] pass (\d+)\s*$", re.M),
    re.compile(r"^1\.\.(\d+)\b", re.M),
]


def parse(text):
    """The number of tests run, or None when no known runner summary is present."""
    if not text:
        return None
    for pattern in PATTERNS:
        found = pattern.findall(text)
        if found:
            return int(found[-1])
    return None


def problems(result: dict, head: str) -> list:
    """Reasons a run-result is not evidence that head passed with at least one test."""
    out = []
    if result.get("head_sha") != head:
        out.append(f"head_sha {str(result.get('head_sha'))[:12]} is not the branch head {head[:12]}")
    if result.get("exit_code") != 0:
        out.append(f"exit_code {result.get('exit_code')}")
    n = parse(result.get("output_tail"))
    if not n:
        out.append("no tests ran" if n == 0 else "output shows no test count")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--result", required=True)
    ap.add_argument("--head", required=True)
    args = ap.parse_args(argv)
    try:
        result = json.loads(Path(args.result).read_text())
        if not isinstance(result, dict):
            raise ValueError("not an object")
    except (OSError, ValueError) as exc:
        print(f"no check result ({type(exc).__name__})")
        return 1
    found = problems(result, args.head)
    for line in found:
        print(line)
    if found:
        return 1
    print(f"passed at {args.head[:12]}: {parse(result.get('output_tail'))} tests")
    return 0


if __name__ == "__main__":
    sys.exit(main())
