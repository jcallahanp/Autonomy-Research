#!/bin/bash
# browser-login: plain (non-automated) Chrome on the engineer profile for John's hand sign-in.
set -euo pipefail
. "$(dirname "$0")/../lib.sh"

setup() {  # setup DIR UID: root with stub id and chrome; prints the root
  local R; R=$(mk_root "$1")
  stub "$R" id "echo $2"
  stub "$R" google-chrome-stable "echo \"DISPLAY=\$DISPLAY\" > '$1/env'"
  echo "$R"
}
run() {  # run ROOT ARGS...: prints the exit code
  local R=$1; shift; local rc=0
  bash "$R/bin/browser-login" "$@" >/dev/null 2>&1 || rc=$?
  echo "$rc"
}
chrome_called() { grep -q '^google-chrome-stable ' "$1/argv.log" 2>/dev/null; }

# Happy path
R=$(setup "$T/a" 1000)
profile="$T/a/home/engineer/.engineer/chrome-profile"
rc=$(run "$R" https://accounts.google.com/)
[ "$rc" -eq 0 ] || fail "happy path exit $rc"
line=$(grep '^google-chrome-stable ' "$T/a/argv.log" || true)
for want in "--user-data-dir=$profile" "--no-first-run" "--proxy-server=http://127.0.0.1:3128" \
            "https://accounts.google.com/"; do
  case "$line" in *"$want"*) ;; *) fail "chrome argv lacks '$want': $line" ;; esac
done
case "$line" in *--headless*|*--remote-debugging*|*--enable-automation*) fail "automation flag: $line" ;; esac
[ "$(stat -c %a "$profile" 2>/dev/null)" = 700 ] || fail "profile mode is not 700"
grep -qx 'DISPLAY=:99' "$T/a/env" 2>/dev/null || fail "DISPLAY not :99"

# Refuses as root
R=$(setup "$T/b" 0)
rc=$(run "$R" https://accounts.google.com/)
[ "$rc" -ne 0 ] || fail "ran as root"
! chrome_called "$T/b" || fail "chrome started as root"

# A live SingletonLock refuses with 75; a dead one does not
R=$(setup "$T/c" 1000)
p="$T/c/home/engineer/.engineer/chrome-profile"; mkdir -p "$p"
ln -s "host-$$" "$p/SingletonLock"
rc=$(run "$R" https://app.attio.com/)
[ "$rc" -eq 75 ] || fail "live lock: exit $rc, want 75"
! chrome_called "$T/c" || fail "chrome started over a live lock"
rm "$p/SingletonLock"; ln -s "host-99999999" "$p/SingletonLock"
rc=$(run "$R" https://app.attio.com/)
[ "$rc" -eq 0 ] || fail "dead lock: exit $rc, want 0"

# A URL that is really a switch, or not http(s), is refused
for bad in --remote-debugging-port=9222 "javascript:alert(1)" "file:///etc/passwd" "" "https://a b"; do
  d=$(mktemp -d "$T/u.XXXX"); R=$(setup "$d" 1000)
  rc=$(run "$R" "$bad")
  [ "$rc" -eq 64 ] || fail "url '$bad': exit $rc, want 64"
  ! chrome_called "$d" || fail "url '$bad': chrome started"
done

# The default Chrome profile is refused
d=$(mktemp -d "$T/d.XXXX"); R=$(setup "$d" 1000)
sed -i 's|^CHROME_PROFILE=.*|CHROME_PROFILE="/home/engineer/.config/google-chrome"|' "$R/etc/engineer.conf"
rc=$(run "$R" https://accounts.google.com/)
[ "$rc" -eq 2 ] || fail "default profile: exit $rc, want 2"
