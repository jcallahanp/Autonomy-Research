#!/bin/bash
# remote-control-session / channels-session: refuse API credentials (Path A), cd PROJECTS_DIR, exec claude.
set -euo pipefail
. "$(dirname "$0")/../lib.sh"

root=$(mk_root "$T")
stub "$root" claude 'pwd > "$(dirname "$0")/../../cwd"'
projects="$T/home/engineer/projects"
clean_env=(env -u ANTHROPIC_API_KEY -u CLAUDE_CODE_OAUTH_TOKEN -u ANTHROPIC_AUTH_TOKEN)

"${clean_env[@]}" "$root/bin/remote-control-session" || fail "remote-control-session failed"
grep -qx 'claude remote-control' "$T/argv.log" || fail "argv: $(cat "$T/argv.log")"
[ "$(cat "$T/cwd")" = "$projects" ] || fail "cwd $(cat "$T/cwd") is not PROJECTS_DIR"

"${clean_env[@]}" "$root/bin/channels-session" || fail "channels-session failed"
grep -qx 'claude --channels plugin:telegram' "$T/argv.log" || fail "argv: $(cat "$T/argv.log")"

for s in remote-control-session channels-session; do
  for v in ANTHROPIC_API_KEY CLAUDE_CODE_OAUTH_TOKEN ANTHROPIC_AUTH_TOKEN; do
    : > "$T/argv.log"
    rc=0; err=$("${clean_env[@]}" "$v=TEST-TOKEN-fake" "$root/bin/$s" 2>&1) || rc=$?
    [ "$rc" -eq 78 ] || fail "$s with $v set: rc=$rc"
    echo "$err" | grep -q "$v" || fail "$s did not name $v: $err"
    echo "$err" | grep -q TEST-TOKEN-fake && fail "$s printed the $v value"
    [ ! -s "$T/argv.log" ] || fail "$s ran claude with $v set"
  done
  rc=0; "${clean_env[@]}" ANTHROPIC_API_KEY= "$root/bin/$s" 2>/dev/null || rc=$?
  [ "$rc" -eq 78 ] || fail "$s with ANTHROPIC_API_KEY set but empty: rc=$rc"
done

# R3-5: with no claude in <root>/bin or on PATH, both find the one bootstrap.sh put in ~/.local/bin.
rm -f "$root/bin/claude"
mkdir -p "$T/h/.local/bin"
printf '#!/bin/bash\necho "local $*" >> "%s/local.log"\n' "$T" > "$T/h/.local/bin/claude"
chmod +x "$T/h/.local/bin/claude"
for s in remote-control-session channels-session; do
  rc=0; "${clean_env[@]}" HOME="$T/h" PATH=/usr/bin:/bin "$root/bin/$s" 2>/dev/null || rc=$?
  [ "$rc" = 0 ] || fail "$s did not find ~/.local/bin/claude: rc=$rc"
done
grep -qx 'local remote-control' "$T/local.log" 2>/dev/null || fail "remote-control-session: $(cat "$T/local.log" 2>&1)"
grep -qx 'local --channels plugin:telegram' "$T/local.log" 2>/dev/null || fail "channels-session: ~/.local/bin claude not run"
rm -f "$T/h/.local/bin/claude"
if [ ! -e /usr/bin/claude ] && [ ! -e /bin/claude ]; then
  rc=0; "${clean_env[@]}" HOME="$T/h" PATH=/usr/bin:/bin "$root/bin/remote-control-session" 2>/dev/null || rc=$?
  [ "$rc" = 69 ] || fail "no claude anywhere: rc=$rc, want 69"
fi
exit 0
