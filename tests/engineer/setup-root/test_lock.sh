#!/bin/bash
# setup-root.sh --lock and --unlock in dry run: managed hooks, LOCKED, egress list, supervisor unit.
set -euo pipefail
. "$(dirname "$0")/../lib.sh"
. "$(dirname "$0")/fixtures.sh"

sr --install >/dev/null 2>&1 || fail "install failed"
M="$P/etc/claude-code/managed-settings.json"
E="$P/opt/engineer"
EG="$P/etc/engineer/egress.txt"
hosts() { grep -v '^[[:space:]]*#' "$1" | awk 'NF {print $1}' | sort -u; }

out=$(sr --lock 2>&1) || fail "lock exit $?: $out"
[ "$(jq -cS .hooks "$M")" = "$(jq -cS .hooks "$SRC/templates/managed-hooks.json")" ] || fail "hooks key not the fixture"
jq -e '.permissions.disableBypassPermissionsMode == "disable"' "$M" >/dev/null || fail "lock lost other settings"
[ "$(cat "$E/LOCKED" 2>/dev/null)" = "$(cat "$E/SOURCE_SHA")" ] || fail "LOCKED does not hold the source SHA"
[ "$(hosts "$EG")" = "$(hosts "$SRC/templates/egress-allowlist.txt")" ] || fail "egress.txt is not the runtime list"
echo "$out" | grep -qx 'RUN: systemctl enable --now engineer-supervisor.service' || fail "supervisor not started"
echo "$out" | grep -qx 'RUN: systemctl restart engineer-egress-proxy.service' || fail "proxy not restarted"
before=$(tree_sum "$P")
sr --lock >/dev/null 2>&1 || fail "second lock failed"
[ "$before" = "$(tree_sum "$P")" ] || fail "second lock changed the tree"

# Install refuses while locked.
rc=0; sr --install >/dev/null 2>&1 || rc=$?
[ "$rc" = 1 ] || fail "install while locked: exit $rc"

# Hosts added with --allow survive into the locked list.
sr --unlock >/dev/null 2>&1 || fail "unlock failed"
sr --allow api.attio.com >/dev/null 2>&1 || fail "allow failed"
sr --lock >/dev/null 2>&1 || fail "relock failed"
grep -qx 'api.attio.com' "$EG" || fail "added host missing from the locked list"

out=$(sr --unlock 2>&1) || fail "unlock exit $?: $out"
jq -e 'has("hooks") | not' "$M" >/dev/null || fail "unlock left hooks"
[ ! -e "$E/LOCKED" ] || fail "unlock left LOCKED"
cmp -s "$EG" "$SRC/templates/egress-install.txt" || fail "unlock did not restore the install list"
echo "$out" | grep -qx 'RUN: systemctl disable --now engineer-supervisor.service' || fail "supervisor not stopped"
before=$(tree_sum "$P")
sr --unlock >/dev/null 2>&1 || fail "second unlock failed"
[ "$before" = "$(tree_sum "$P")" ] || fail "second unlock changed the tree"

# Lock refuses without an install or without the managed hooks template.
rm -rf "$P"
rc=0; sr --lock >/dev/null 2>&1 || rc=$?
[ "$rc" = 1 ] || fail "lock before install: exit $rc"
sr --install >/dev/null 2>&1
rm "$E/templates/managed-hooks.json"
rc=0; sr --lock >/dev/null 2>&1 || rc=$?
[ "$rc" = 1 ] || fail "lock without managed-hooks.json: exit $rc"
jq -e 'has("hooks") | not' "$M" >/dev/null || fail "failed lock wrote hooks"
