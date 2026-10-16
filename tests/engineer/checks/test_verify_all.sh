#!/bin/bash
# verify-all.sh: one broker call per row, stops at the first failure, writes the table.
set -euo pipefail
. "$(dirname "$0")/../lib.sh"

root=$(mk_root "$T")
# AGENT_RUN in the test conf is <root>/bin/agent-run. Rows 1-2 pass, row 3 (hc-ping) fails.
stub "$root" agent-run 'cat > /dev/null; case "$1" in hc-ping) echo "ping failed" >&2; exit 1 ;; esac; echo "{}"'
tsv="$root/templates/verify-all.tsv"
first3=$(grep -v '^#' "$tsv" | grep -v '^$' | head -3 | cut -f2 | cut -d' ' -f1 | paste -sd' ' -)
[ "$first3" = "api-call tg-send hc-ping" ] || fail "tsv: first three jobs are '$first3'"

rc=0; (cd "$T" && "$root/scripts/checks/verify-all.sh" --out "$T/verify.md") >"$T/out" 2>&1 || rc=$?
[ "$rc" -eq 1 ] || fail "exit $rc, want 1: $(cat "$T/out")"
[ -f "$T/verify.md" ] || fail "no output table"
grep -q '^| Name | Broker job | Check | Result |$' "$T/verify.md" || fail "no header row"
results=$(grep '^| [A-Za-z]' "$T/verify.md" | grep -v '^| Name ' | awk -F' [|] ' '{print $4}' | sed 's/ |$//' | paste -sd, -)
case "$results" in
  pass,pass,FAIL,not\ run,not\ run*) ;;
  *) fail "results: $results" ;;
esac
case "$results" in *manual*) fail "manual row reported after a failure: $results" ;; esac
grep -q '^agent-run api-call github GET /user$' "$T/argv.log" || fail "argv: $(cat "$T/argv.log")"
grep -q '^agent-run tg-send$' "$T/argv.log" || fail "tg-send argv: $(cat "$T/argv.log")"
[ "$(grep -c '^agent-run' "$T/argv.log")" -eq 3 ] || fail "calls after the failure: $(cat "$T/argv.log")"

# tg-send gets its text on stdin
stub "$root" agent-run 'if [ "$1" = tg-send ]; then cat > '"$T"'/tg-stdin; fi; exit 0'
rc=0; (cd "$T" && "$root/scripts/checks/verify-all.sh") >"$T/out" 2>&1 || rc=$?
[ "$rc" -eq 0 ] || fail "all pass: exit $rc: $(cat "$T/out")"
[ -f "$T/docs/setup-verify.md" ] || fail "default --out not written"
grep -qx 'setup test' "$T/tg-stdin" || fail "tg-send stdin: $(cat "$T/tg-stdin" 2>/dev/null)"
[ "$(grep -c '| manual |$' "$T/docs/setup-verify.md")" -eq 3 ] || fail "manual rows: $(cat "$T/docs/setup-verify.md")"

rc=0; "$root/scripts/checks/verify-all.sh" --bogus >/dev/null 2>&1 || rc=$?
[ "$rc" -eq 2 ] || fail "bad flag: exit $rc"
