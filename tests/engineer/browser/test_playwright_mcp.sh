#!/bin/bash
# playwright-mcp.sh: headed branded Chrome, persistent non-default profile, egress proxy, pinned package.
set -euo pipefail
. "$(dirname "$0")/../lib.sh"

pin=$(awk -F'\t' '$1=="@playwright/mcp"{print $3}' engineer/templates/bootstrap-packages.txt)
[ -n "$pin" ] || fail "no @playwright/mcp pin in bootstrap-packages.txt"

R=$(mk_root "$T/a")
stub "$R" npx "echo \"DISPLAY=\$DISPLAY\" > '$T/a/env'"
rc=0; bash "$R/plugin/scripts/playwright-mcp.sh" >/dev/null 2>&1 || rc=$?
[ "$rc" -eq 0 ] || fail "plain launch exit $rc"
line=$(grep '^npx ' "$T/a/argv.log" || true)
for want in "--no-install" "@playwright/mcp@$pin" "--browser chrome" \
            "--user-data-dir $T/a/home/engineer/.engineer/chrome-profile" \
            "--proxy-server http://127.0.0.1:3128"; do
  case "$line" in *"$want"*) ;; *) fail "npx argv lacks '$want': $line" ;; esac
done
case "$line" in *--headless*|*--isolated*) fail "npx argv has headless/isolated: $line" ;; esac
grep -qx 'DISPLAY=:99' "$T/a/env" 2>/dev/null || fail "DISPLAY not :99 from engineer.conf"

refuses() {  # refuses DIR ARGS...: exit 2 and npx never called
  local d=$1; shift
  rc=0; bash "$d/opt/plugin/scripts/playwright-mcp.sh" "$@" >/dev/null 2>&1 || rc=$?
  [ "$rc" -eq 2 ] || fail "args '$*' (dir $d): exit $rc, want 2"
  ! grep -q '^npx ' "$d/argv.log" 2>/dev/null || fail "args '$*': npx was called"
}
for bad in --headless --headless=true --isolated --user-data-dir=/tmp/x --browser=chromium \
           --executable-path=/x --cdp-endpoint=http://127.0.0.1:9222 --extension --config=/x.json; do
  d=$(mktemp -d "$T/r.XXXX"); R2=$(mk_root "$d"); stub "$R2" npx
  refuses "$d" "$bad"
done

set_profile() {  # set_profile DIR VALUE
  local R3; R3=$(mk_root "$1"); stub "$R3" npx
  sed -i "s|^CHROME_PROFILE=.*|CHROME_PROFILE=\"$2\"|" "$R3/etc/engineer.conf"
}
set_profile "$T/p1" "/home/engineer/.config/google-chrome"; refuses "$T/p1"
set_profile "$T/p2" "/home/engineer/.config/google-chrome/"; refuses "$T/p2"
set_profile "$T/p3" ""; refuses "$T/p3"

# No stealth plugin or CAPTCHA solver in the code of the browser route (comments may say they are banned).
for f in engineer/plugin/scripts/playwright-mcp.sh engineer/bin/browser-login engineer/bin/xvfb-session \
         engineer/bin/novnc-session engineer/plugin/.mcp.json; do
  [ -f "$f" ] || { fail "$f missing"; continue; }
  ! grep -vE '^\s*#' "$f" | grep -qiE 'stealth|playwright-extra|captcha|capsolver' || fail "evasion code in $f"
done
user_agent_set=$(grep -vE '^\s*#' engineer/plugin/scripts/playwright-mcp.sh engineer/bin/browser-login \
  | grep -E -- '--user-agent[= ]' | grep -v '\*--user-agent\*' || true)
[ -z "$user_agent_set" ] || fail "a user agent is set: $user_agent_set"
