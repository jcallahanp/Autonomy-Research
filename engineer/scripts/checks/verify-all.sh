#!/bin/bash
# Setup-day check that every secret of this sitting works, through the broker only.
set -euo pipefail
# Usage: verify-all.sh [--out FILE]   (run as supervisor, so agent-run accepts every job; default
# --out docs/setup-verify.md in the current directory). Rows come from <root>/templates/verify-all.tsv:
# name<TAB>job args<TAB>check text[<TAB>stdin]. Each row runs `AGENT_RUN <job args>`; `manual` rows are
# left for John. Stops at the first failure and marks the rest `not run`; exit 1 then.
# Writes `Name | Broker job | Check | Result`. Job output is discarded: no response body reaches the table.
root=$(cd "$(dirname "$(readlink -f "$0")")/../.." && pwd)
. "$root/etc/engineer.conf"
export PATH="$root/bin:/usr/local/bin:/usr/bin:/bin"

out=docs/setup-verify.md
while [ $# -gt 0 ]; do
  case "$1" in
    --out) [ $# -ge 2 ] || { echo "verify-all: --out needs a file" >&2; exit 2; }; out=$2; shift 2 ;;
    *) echo "usage: verify-all.sh [--out FILE]" >&2; exit 2 ;;
  esac
done
tsv="$root/templates/verify-all.tsv"
read -ra runner <<< "$AGENT_RUN"
cell() { local s=${1//|/\\|}; printf '%s' "$s"; }

rows=() stopped=0 failed=0
while IFS=$'\t' read -r name job check input; do
  case "$name" in ''|'#'*) continue ;; esac
  if [ "$stopped" -eq 1 ]; then
    result="not run"
  elif [ "$job" = manual ]; then
    result=manual
  else
    read -ra args <<< "$job"
    if [[ ! ${args[0]:-} =~ ^[a-z][a-z0-9-]*$ ]]; then
      result=FAIL
    else
      rc=0
      if [ -n "${input:-}" ]; then
        printf '%s\n' "$input" | "${runner[@]}" "${args[@]}" >/dev/null || rc=$?
      else
        "${runner[@]}" "${args[@]}" </dev/null >/dev/null || rc=$?
      fi
      result=pass
      [ "$rc" -eq 0 ] || result=FAIL
    fi
    if [ "$result" = FAIL ]; then stopped=1 failed=1; fi
  fi
  echo "verify-all: $name: $result"
  rows+=("| $(cell "$name") | $(cell "$job") | $(cell "$check") | $result |")
done < "$tsv"

mkdir -p "$(dirname "$out")"
{
  echo "# Setup verification"
  echo
  echo "Run $(date -u +%Y-%m-%dT%H:%M:%SZ) by scripts/checks/verify-all.sh. Values are never shown."
  echo
  echo "| Name | Broker job | Check | Result |"
  echo "| --- | --- | --- | --- |"
  printf '%s\n' "${rows[@]}"
} > "$out"
echo "verify-all: wrote $out"
[ "$failed" -eq 0 ]
