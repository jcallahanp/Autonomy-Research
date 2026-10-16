#!/bin/bash
# Deterministic audit of a task branch, run by the supervisor (F24, F25). Usage: audit.sh PROJECT TASK_ID
set -euo pipefail
# Fetches into the supervisor-owned bare clone (clone.sh) and reads only from there: nothing from the
# engineer-writable project repo's config, hooks or attributes runs. Prints one audit-verdict JSON object
# {"verdict": "PASS"|"FAIL", "head_sha", "lines"} (at most 15 lines); exit 0 PASS, 1 FAIL, 2 or 3 when the
# branch could not be audited (bad arguments, unknown project, fetch failed).
root=$(cd "$(dirname "$(readlink -f "$0")")/../.." && pwd)
. "$root/etc/engineer.conf"
export PATH="$root/bin:/usr/local/bin:/usr/bin:/bin" GIT_CONFIG_NOSYSTEM=1 GIT_TERMINAL_PROMPT=0 PYTHONDONTWRITEBYTECODE=1
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_CONFIG GIT_CONFIG_PARAMETERS GIT_CONFIG_COUNT GIT_EXEC_PATH
checks="$root/scripts/checks"

[ $# -eq 2 ] || { echo "usage: audit.sh PROJECT TASK_ID" >&2; exit 2; }
p=$1 id=$2
clone=$("$checks/clone.sh" "$p" "$id") || exit $?
G() { git -c core.hooksPath=/dev/null -c core.fsmonitor= --git-dir="$clone" "$@"; }
head=$(G rev-parse --verify -q 'refs/audit/head^{commit}') || { echo "audit: no task/$id" >&2; exit 3; }
base=$(G merge-base "$head" refs/audit/base) || { echo "audit: no merge base" >&2; exit 3; }

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
lines=() failed=0

# step NAME CMD...: run a check, prefix its output lines with NAME (unless already prefixed), note failure.
step() {
  local name=$1 rc=0 out line
  shift
  out=$("$@" 2>"$tmp/err") || rc=$?
  while IFS= read -r line; do
    [ -n "$line" ] || continue
    case "$line" in "$name:"*) lines+=("$line") ;; *) lines+=("$name: $line") ;; esac
  done <<< "$out"
  if [ "$rc" -ne 0 ]; then
    failed=1
    [ -n "$out" ] || lines+=("$name: error (exit $rc) $(head -c 200 "$tmp/err" | tr '\n' ' ')")
  fi
  return 0
}

guard_lines() {  # test-diff-guard JSON findings as text lines; keeps its exit status
  local rc=0 out
  out=$(python3 "$checks/test-diff-guard.py" --repo "$clone" --base "$base" --head "$head") || rc=$?
  [ "$rc" -le 1 ] || return "$rc"
  jq -r '.[] | "\(.kind) \(.path) (\(.detail))"' <<< "$out"
  return "$rc"
}

protected_lines() {  # changed paths matching a protected [always] pattern
  python3 - "$checks" "$clone" "$base" "$head" <<'PY'
import sys
sys.path.insert(0, sys.argv[1])
import checklib
rules, hits = checklib.rules(), 0
for status, path in checklib.changes(*sys.argv[2:5]):
    pattern = next((p for p in rules["always"] if checklib.paths.match(path, p)), None)
    if pattern:
        hits += 1
        print(f"{path} changed (status {status}; [always] {pattern})")
sys.exit(1 if hits else 0)
PY
}

at_head() {  # at_head PATH: copy PATH at head into $tmp/tree; fails when absent
  G cat-file -e "$head:$1" 2>/dev/null || return 1
  mkdir -p "$(dirname "$tmp/tree/$1")"
  G cat-file blob "$head:$1" > "$tmp/tree/$1"
}

step check python3 "$checks/testcount.py" --result "$STATE_DIR/checks/$p/$id.json" --head "$head"
step protected protected_lines
step test-diff-guard guard_lines
step secret-scan python3 "$checks/secret-scan.py" --diff "$clone" "$base" "$head"
step scanners python3 "$checks/scanners.py" --repo "$clone" --base "$base" --head "$head"

changed=$(G diff --name-only --no-renames --no-ext-diff --no-textconv "$base" "$head" --)
if grep -qxE 'docs/plan/integrations\.yaml|\.env\.example' <<< "$changed" && at_head docs/plan/integrations.yaml; then
  at_head .env.example || true
  step integrations-env python3 "$checks/integrations-env.py" --repo "$tmp/tree"
fi
if grep -qxE 'docs/plan/architecture\.(yaml|mmd)' <<< "$changed"; then
  at_head docs/plan/architecture.yaml || true
  at_head docs/plan/architecture.mmd || true
  step parity python3 "$checks/parity.py" --repo "$tmp/tree"
fi
n=$(grep -c . <<< "$changed" || true)
[ "$failed" -eq 1 ] || lines+=("diff: $n files from ${base:0:12} to ${head:0:12}, no findings")

verdict=PASS
[ "$failed" -eq 0 ] || verdict=FAIL
python3 - "$verdict" "$head" "${lines[@]}" <<'PY'
import json, sys
verdict, head, lines = sys.argv[1], sys.argv[2], [l[:300] for l in sys.argv[3:]]
if len(lines) > 15:
    lines = lines[:14] + [f"... {len(lines) - 14} more lines"]
print(json.dumps({"verdict": verdict, "head_sha": head, "lines": lines}))
PY
[ "$verdict" = PASS ]
