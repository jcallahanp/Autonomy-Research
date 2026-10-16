#!/bin/bash
# setup-root.sh --allow HOST: add one host to the active egress list and to egress-added.txt (sourced).
set -euo pipefail

# valid_host HOST: lowercase host or *.suffix, at least two labels, letters-only TLD, no edge hyphens.
valid_host() {
  local label='[a-z0-9]([a-z0-9-]*[a-z0-9])?'
  [[ $1 =~ ^(\*\.)?($label\.)+[a-z]{2,}$ ]] && [ "${#1}" -le 253 ]
}

do_allow() {
  local host=$1
  valid_host "$host" || die "not an allowed host pattern: $host" 2
  [ -f "$OPT/SOURCE_SHA" ] || die "not installed; run --install first"
  mkdir -p "$ETC"
  [ -f "$EGRESS_ADDED" ] || : > "$EGRESS_ADDED"
  local f
  for f in "$EGRESS_ADDED" "$EGRESS"; do
    if ! grep -qxF "$host" "$f" 2>/dev/null; then
      { [ ! -f "$f" ] || cat "$f"; echo "$host"; } | write_file "$f" 0644
    fi
  done
  restart_proxy
}
