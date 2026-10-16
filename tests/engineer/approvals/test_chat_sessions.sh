#!/bin/bash
# remote-control-session / channels-session: refuse API credentials (Path A), cd PROJECTS_DIR, exec claude.
set -euo pipefail
. "$(dirname "$0")/../lib.sh"

root=$(mk_root "$T")
stub "$root" claude 'pwd > "$(dirname "$0")/../../cwd"'
projects="$T/home/engineer/projects"
clean_env=(env -u ANTHROPIC_API_KEY -u CLAUDE_CODE_OAUTH_TOKEN)

"${clean_env[@]}" "$root/bin/remote-control-session" || fail "remote-control-session failed"
grep -qx 'claude remote-control' "$T/argv.log" || fail "argv: $(cat "$T/argv.log")"
[ "$(cat "$T/cwd")" = "$projects" ] || fail "cwd $(cat "$T/cwd") is not PROJECTS_DIR"

"${clean_env[@]}" "$root/bin/channels-session" || fail "channels-session failed"
grep -qx 'claude --channels plugin:telegram' "$T/argv.log" || fail "argv: $(cat "$T/argv.log")"

for s in remote-control-session channels-session; do
  for v in ANTHROPIC_API_KEY CLAUDE_CODE_OAUTH_TOKEN; do
    : > "$T/argv.log"
    rc=0; "${clean_env[@]}" "$v=x" "$root/bin/$s" 2>/dev/null || rc=$?
    [ "$rc" -eq 78 ] || fail "$s with $v set: rc=$rc"
    [ ! -s "$T/argv.log" ] || fail "$s ran claude with $v set"
  done
  rc=0; "${clean_env[@]}" ANTHROPIC_API_KEY= "$root/bin/$s" 2>/dev/null || rc=$?
  [ "$rc" -eq 78 ] || fail "$s with ANTHROPIC_API_KEY set but empty: rc=$rc"
done
exit 0
