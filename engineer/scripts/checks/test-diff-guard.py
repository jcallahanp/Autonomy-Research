"""Find changes that weaken the tests between two commits of a repo the checker owns.

Usage: test-diff-guard.py --repo GITDIR --base SHA --head SHA
Prints a JSON list of {kind, path, detail}; exit 1 when it is not empty, 2 on bad input.
Kinds: deleted_test ([existing] test patterns), skip_marker (added line), fewer_asserts (test file),
acceptance_changed (tests/acceptance/), test_config (the test config files of the [always] list).
"""
import argparse
import json
import re
import subprocess
import sys

import checklib
from checklib import paths

SKIP = re.compile(r"@pytest\.mark\.skip|pytest\.skip\(|@unittest\.skip|\bit\.skip\(|\bdescribe\.skip\("
                  r"|\btest\.skip\(|\bxit\(|\bxdescribe\(|\bt\.Skip\(")
ASSERT = re.compile(r"\bassert|\bexpect\(")
# The test config entries of templates/protected-paths.txt [always].
TEST_CONFIG = ("**/conftest.py", "pytest.ini", "tox.ini", "jest.config.*", "vitest.config.*", ".mocharc*")
ACCEPTANCE = "tests/acceptance/**"


def is_test(path: str, rules: dict) -> bool:
    return any(paths.match(path, p) for p in rules["existing"])


def asserts(text) -> int:
    return sum(1 for line in (text or "").splitlines() if ASSERT.search(line))


def findings(gitdir, base, head, rules) -> list:
    out = []
    for status, path in checklib.changes(gitdir, base, head):
        if paths.match(path, ACCEPTANCE):
            out.append({"kind": "acceptance_changed", "path": path, "detail": f"status {status}"})
        if any(paths.match(path, p) for p in TEST_CONFIG):
            out.append({"kind": "test_config", "path": path, "detail": f"status {status}"})
        if not is_test(path, rules):
            continue
        if status == "D":
            out.append({"kind": "deleted_test", "path": path, "detail": "test file deleted"})
        elif status == "M":
            before = asserts(checklib.blob(gitdir, base, path))
            after = asserts(checklib.blob(gitdir, head, path))
            if after < before:
                out.append({"kind": "fewer_asserts", "path": path, "detail": f"assert/expect lines {before} -> {after}"})
    for path, n, text in checklib.added_lines(gitdir, base, head):
        m = SKIP.search(text)
        if m:
            out.append({"kind": "skip_marker", "path": path, "detail": f"line {n}: {m.group(0)}"})
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Find test-weakening changes.")
    ap.add_argument("--repo", required=True)
    ap.add_argument("--base", required=True)
    ap.add_argument("--head", required=True)
    args = ap.parse_args(argv)
    try:
        base, head = checklib.check_sha(args.base), checklib.check_sha(args.head)
        found = findings(args.repo, base, head, checklib.rules())
    except (ValueError, subprocess.CalledProcessError) as exc:
        print(f"test-diff-guard: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(found, indent=1))
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
