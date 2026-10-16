#!/bin/bash
# doctor.sh (Task 4): read-only host checks; OK/FAIL lines; exit 1 on any FAIL.
set -euo pipefail
. "$(dirname "$0")/../lib.sh"

root=$(mk_root "$T")
export HOME="$T/home"; mkdir -p "$HOME"
unset ANTHROPIC_API_KEY CLAUDE_CODE_OAUTH_TOKEN
D="$root/scripts/doctor.sh"
. "$root/etc/engineer.conf"
mkdir -p "$(dirname "$MANAGED_SETTINGS")"; echo '{"permissions": {}}' > "$MANAGED_SETTINGS"
rm -f "$KILL_SWITCH"

printf 'NAME="Ubuntu"\nVERSION_ID="24.04"\nID=ubuntu\n' > "$T/os-release"
printf 'NAME="Ubuntu"\nVERSION_ID="22.04"\nID=ubuntu\n' > "$T/os-old"
printf 'MemTotal:        8140000 kB\nMemFree:  100 kB\n' > "$T/meminfo"
printf 'MemTotal:        4000000 kB\n' > "$T/meminfo-small"
export DOCTOR_OS_RELEASE="$T/os-release" DOCTOR_MEMINFO="$T/meminfo" DOCTOR_NPROC=4 DOCTOR_DISK_GB=160
stub "$root" claude 'echo "2.1.301 (Claude Code)"'
stub "$root" google-chrome-stable 'echo "Google Chrome 141.0.7390.54"'

run() { rc=0; out=$(bash "$D" "$@" 2>&1) || rc=$?; }

# Good host: 9 OK lines (os cpu ram disk no_api_key claude chrome kill_switch managed_settings).
run --skip units
[ "$rc" -eq 0 ] || fail "good host exit $rc: $out"
n=$(echo "$out" | grep -c '^OK ' || true)
[ "$n" -eq 9 ] || fail "good host: $n OK lines: $out"
for c in os cpu ram disk no_api_key claude chrome kill_switch managed_settings; do
  echo "$out" | grep -qx "OK $c" || fail "missing OK $c"
done
echo "$out" | grep -q '^FAIL' && fail "good host has FAIL: $out"

expect_fail() {  # expect_fail CHECK [doctor args...]
  local check=$1; shift
  run "$@"
  [ "$rc" -eq 1 ] || fail "$check: exit $rc"
  echo "$out" | grep -q "^FAIL $check: " || fail "no FAIL $check: $out"
}

ANTHROPIC_API_KEY=TEST-TOKEN-fake expect_fail no_api_key --skip units
echo "$out" | grep -q TEST-TOKEN-fake && fail "key value printed"
CLAUDE_CODE_OAUTH_TOKEN=TEST-TOKEN-fake expect_fail no_api_key --skip units
echo "$out" | grep -q TEST-TOKEN-fake && fail "token value printed"
DOCTOR_NPROC=2 expect_fail cpu --skip units
DOCTOR_OS_RELEASE="$T/os-old" expect_fail os --skip units
DOCTOR_MEMINFO="$T/meminfo-small" expect_fail ram --skip units
DOCTOR_DISK_GB=50 expect_fail disk --skip units

stub "$root" claude 'echo "2.1.200 (Claude Code)"'
expect_fail claude --skip units
stub "$root" claude 'echo "2.10.0 (Claude Code)"'
run --skip units; echo "$out" | grep -qx 'OK claude' || fail "2.10.0 should pass the 2.1.301 pin: $out"
stub "$root" claude 'exit 127'
expect_fail claude --skip units
stub "$root" claude 'echo "2.1.301 (Claude Code)"'

stub "$root" google-chrome-stable 'exit 1'
expect_fail chrome --skip units
stub "$root" google-chrome-stable 'echo "Google Chrome 141.0.7390.54"'

touch "$KILL_SWITCH"; expect_fail kill_switch --skip units; rm -f "$KILL_SWITCH"
mv "$MANAGED_SETTINGS" "$T/ms"; expect_fail managed_settings --skip units; mv "$T/ms" "$MANAGED_SETTINGS"

# Units: all active passes; one inactive fails; engineer-supervisor only once LOCKED exists.
stub "$root" systemctl 'exit 0'
run
[ "$rc" -eq 0 ] || fail "units active: exit $rc: $out"
for u in chrome-xvfb novnc engineer-egress-proxy; do
  echo "$out" | grep -qx "OK unit_$u" || fail "missing OK unit_$u: $out"
done
echo "$out" | grep -q 'engineer-supervisor' && fail "supervisor checked before LOCKED"
touch "$root/LOCKED"
run; echo "$out" | grep -qx 'OK unit_engineer-supervisor' || fail "supervisor not checked when LOCKED: $out"
stub "$root" systemctl 'case "$*" in *novnc*) exit 3 ;; esac; exit 0'
expect_fail unit_novnc
grep -q '^systemctl is-active --quiet novnc.service$' "$T/argv.log" || fail "systemctl argv: $(cat "$T/argv.log")"

rc=0; bash "$D" --skip nope >/dev/null 2>&1 || rc=$?
[ "$rc" -eq 2 ] || fail "--skip nope: exit $rc"
