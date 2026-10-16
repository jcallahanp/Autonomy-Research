#!/bin/bash
# Runs the engineer tests: tests/engineer/<area>/test_*.sh, then each test_*.py with unittest.
# Usage: bash tests/engineer/run.sh [area ...]   (no area = every subdirectory)
# Files run in parallel (ENG_JOBS, default nproc); results print afterwards in area and file order.
# Prints "FAIL engineer/<area>: <file>" per failing file (its output indented below); exits 1 on any.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
cd "$here/../.."
export PYTHONDONTWRITEBYTECODE=1
jobs=${ENG_JOBS:-$(nproc 2>/dev/null || echo 4)}

areas=("$@")
if [ ${#areas[@]} -eq 0 ]; then
  for d in "$here"/*/; do
    a=$(basename "$d")
    case "$a" in _*|.*) continue ;; esac
    areas+=("$a")
  done
fi

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

fails=0; ran=0; files=()
for a in "${areas[@]}"; do
  d="$here/$a"
  if [ ! -d "$d" ]; then echo "FAIL engineer/$a: no such area"; fails=$((fails+1)); continue; fi
  n=0
  for t in "$d"/test_*.sh "$d"/test_*.py; do
    [ -f "$t" ] || continue
    n=$((n+1)); files+=("$a/$(basename "$t")")
  done
  [ "$n" -gt 0 ] || { echo "FAIL engineer/$a: no test files"; fails=$((fails+1)); }
  ran=$((ran+n))
done

run_one() {  # run_one AREA/FILE: output to $work/N.out, exit code to $work/N.rc
  local rel=$1 key=${1//\//__} d=$here/${1%%/*} f=${1##*/} rc=0
  case "$f" in
    *.sh) bash "$d/$f" >"$work/$key.out" 2>&1 || rc=$? ;;
    *.py) python3 -m unittest discover -s "$d" -t "$d" -p "$f" >"$work/$key.out" 2>&1 || rc=$? ;;
  esac
  echo "$rc" >"$work/$key.rc"
}

running=0
for rel in "${files[@]}"; do
  if [ "$running" -ge "$jobs" ]; then wait -n || true; running=$((running-1)); fi
  run_one "$rel" &
  running=$((running+1))
done
wait

for rel in "${files[@]}"; do
  key=${rel//\//__}
  rc=$(cat "$work/$key.rc" 2>/dev/null || echo 1)
  if [ "$rc" -ne 0 ]; then
    echo "FAIL engineer/${rel%%/*}: ${rel##*/}"
    sed 's/^/    /' "$work/$key.out" 2>/dev/null || true
    fails=$((fails+1))
  fi
done

if [ "$fails" -eq 0 ]; then echo "run.sh: $ran test files pass"; else echo "run.sh: $fails failure(s) in $ran test files"; exit 1; fi
