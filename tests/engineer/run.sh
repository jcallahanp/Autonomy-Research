#!/bin/bash
# Runs the engineer tests: tests/engineer/<area>/test_*.sh, then each test_*.py with unittest.
# Usage: bash tests/engineer/run.sh [area ...]   (no area = every subdirectory)
# Prints "FAIL engineer/<area>: <file>" per failing file (its output indented below); exits 1 on any.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
cd "$here/../.."
export PYTHONDONTWRITEBYTECODE=1

areas=("$@")
if [ ${#areas[@]} -eq 0 ]; then
  for d in "$here"/*/; do
    a=$(basename "$d")
    case "$a" in _*|.*) continue ;; esac
    areas+=("$a")
  done
fi

fails=0; ran=0
out=$(mktemp)
trap 'rm -f "$out"' EXIT

report() {  # report AREA FILE STATUS
  if [ "$3" -ne 0 ]; then
    echo "FAIL engineer/$1: $2"
    sed 's/^/    /' "$out"
    fails=$((fails+1))
  fi
}

for a in "${areas[@]}"; do
  d="$here/$a"
  if [ ! -d "$d" ]; then echo "FAIL engineer/$a: no such area"; fails=$((fails+1)); continue; fi
  n=0
  for t in "$d"/test_*.sh; do
    [ -f "$t" ] || continue
    n=$((n+1)); rc=0
    bash "$t" >"$out" 2>&1 || rc=$?
    report "$a" "$(basename "$t")" "$rc"
  done
  for t in "$d"/test_*.py; do
    [ -f "$t" ] || continue
    n=$((n+1)); rc=0
    python3 -m unittest discover -s "$d" -t "$d" -p "$(basename "$t")" >"$out" 2>&1 || rc=$?
    report "$a" "$(basename "$t")" "$rc"
  done
  [ "$n" -gt 0 ] || { echo "FAIL engineer/$a: no test files"; fails=$((fails+1)); }
  ran=$((ran+n))
done

if [ "$fails" -eq 0 ]; then echo "run.sh: $ran test files pass"; else echo "run.sh: $fails failure(s) in $ran test files"; exit 1; fi
