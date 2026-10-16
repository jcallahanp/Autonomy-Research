#!/bin/bash
set -euo pipefail
# Read-only health check of the engineer host. Run as engineer (unprivileged).
# Usage: doctor.sh [--skip units]
# Prints "OK <check>" or "FAIL <check>: <detail>" per check; exits 1 on any FAIL, 2 on usage.
# Checks: no_api_key (Path A: Max /login only; Remote Control refuses setup-token, engineer-host
# E105), os (Ubuntu 24.04), cpu (>= 4), ram (>= 7.5 GiB), disk (>= 75 GB on /), claude (version
# >= the bootstrap pin), chrome (google-chrome-stable), kill_switch (absent), managed_settings
# (present, valid JSON), and unless --skip units: unit_chrome-xvfb, unit_novnc,
# unit_engineer-egress-proxy, plus unit_engineer-supervisor once <root>/LOCKED exists.
# Test overrides (harmless: doctor only reads): DOCTOR_OS_RELEASE, DOCTOR_MEMINFO, DOCTOR_NPROC,
# DOCTOR_DISK_GB.
root=$(cd "$(dirname "$(readlink -f "$0")")/.." && pwd)
export PATH="$root/bin:$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin"

skip_units=0
while [ $# -gt 0 ]; do
  case "$1 ${2:-}" in
    "--skip units") skip_units=1; shift 2 ;;
    *) echo "usage: doctor.sh [--skip units]" >&2; exit 2 ;;
  esac
done

# shellcheck source=/dev/null
. "$root/etc/engineer.conf"

fails=0
ok() { echo "OK $1"; }
bad() { echo "FAIL $1: $2"; fails=$((fails+1)); }

# no_api_key: John's decision 1. Name the variable, never print its value.
set_vars=()
for v in ANTHROPIC_API_KEY CLAUDE_CODE_OAUTH_TOKEN; do
  [ -z "${!v:-}" ] || set_vars+=("$v")
done
if [ ${#set_vars[@]} -eq 0 ]; then ok no_api_key
else bad no_api_key "${set_vars[*]} set; Path A (Max /login) only, unset it"; fi

# os
osr=${DOCTOR_OS_RELEASE:-/etc/os-release}
os_id=$(sed -n 's/^ID=//p' "$osr" 2>/dev/null | tr -d '"' | head -1 || true)
os_ver=$(sed -n 's/^VERSION_ID=//p' "$osr" 2>/dev/null | tr -d '"' | head -1 || true)
if [ "$os_id" = ubuntu ] && [ "$os_ver" = 24.04 ]; then ok os
else bad os "want Ubuntu 24.04, found ${os_id:-?} ${os_ver:-?}"; fi

# cpu
cpus=${DOCTOR_NPROC:-$(nproc 2>/dev/null || echo 0)}
if [[ "$cpus" =~ ^[0-9]+$ ]] && [ "$cpus" -ge 4 ]; then ok cpu
else bad cpu "want at least 4 CPUs, found $cpus"; fi

# ram: MemTotal in KiB; 7.5 GiB = 7864320 KiB
mem_kib=$(awk '$1 == "MemTotal:" { print $2; exit }' "${DOCTOR_MEMINFO:-/proc/meminfo}" 2>/dev/null || true)
if [[ "${mem_kib:-}" =~ ^[0-9]+$ ]] && [ "$mem_kib" -ge 7864320 ]; then ok ram
else bad ram "want at least 7.5 GiB, found ${mem_kib:-?} KiB"; fi

# disk: size of / in GB (10^9 bytes)
if [ -n "${DOCTOR_DISK_GB:-}" ]; then disk_gb=$DOCTOR_DISK_GB
else disk_gb=$(df -P -B1 / 2>/dev/null | awk 'NR == 2 { printf "%d", $2 / 1000000000 }' || true); fi
if [[ "${disk_gb:-}" =~ ^[0-9]+$ ]] && [ "$disk_gb" -ge 75 ]; then ok disk
else bad disk "want at least 75 GB on /, found ${disk_gb:-?} GB"; fi

# claude: version at least the pin in bootstrap-packages.txt
pin=$(awk -F'\t' '$1 == "@anthropic-ai/claude-code" { print $3; exit }' "$root/templates/bootstrap-packages.txt")
have=$(timeout 30 claude --version 2>/dev/null | grep -Eo '[0-9]+\.[0-9]+\.[0-9]+' | head -1 || true)
if [ -z "$have" ]; then bad claude "claude --version gave no version (want >= $pin)"
elif [ "$(printf '%s\n%s\n' "$pin" "$have" | sort -V | head -1)" = "$pin" ]; then ok claude
else bad claude "version $have is below the pin $pin"; fi

# chrome
if chrome=$(timeout 30 google-chrome-stable --version 2>/dev/null) && [ -n "$chrome" ]; then ok chrome
else bad chrome "google-chrome-stable --version failed"; fi

# kill_switch
if [ ! -e "$KILL_SWITCH" ]; then ok kill_switch
else bad kill_switch "$KILL_SWITCH exists; the engineer is stopped"; fi

# managed_settings
if [ -f "$MANAGED_SETTINGS" ] && python3 -c 'import json, sys; json.load(open(sys.argv[1]))' "$MANAGED_SETTINGS" 2>/dev/null
then ok managed_settings
else bad managed_settings "$MANAGED_SETTINGS missing or not JSON"; fi

# units
if [ "$skip_units" -eq 0 ]; then
  units=(chrome-xvfb novnc engineer-egress-proxy)
  [ ! -e "$root/LOCKED" ] || units+=(engineer-supervisor)
  for u in "${units[@]}"; do
    if systemctl is-active --quiet "$u.service"; then ok "unit_$u"
    else bad "unit_$u" "$u.service is not active"; fi
  done
fi

[ "$fails" -eq 0 ]
