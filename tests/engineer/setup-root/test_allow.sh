#!/bin/bash
# setup-root.sh --allow HOST in dry run: strict host pattern, appended once, proxy restarted.
set -euo pipefail
. "$(dirname "$0")/../lib.sh"
. "$(dirname "$0")/fixtures.sh"

sr --install >/dev/null 2>&1 || fail "install failed"
EG="$P/etc/engineer/egress.txt"
AD="$P/etc/engineer/egress-added.txt"

out=$(sr --allow api.attio.com 2>&1) || fail "allow exit $?: $out"
echo "$out" | grep -qx 'RUN: systemctl restart engineer-egress-proxy.service' || fail "proxy not restarted"
sr --allow api.attio.com >/dev/null 2>&1 || fail "second allow failed"
[ "$(grep -cx 'api.attio.com' "$EG")" = 1 ] || fail "egress.txt does not hold the host once"
[ "$(grep -cx 'api.attio.com' "$AD")" = 1 ] || fail "egress-added.txt does not hold the host once"
sr --allow '*.clay.com' >/dev/null 2>&1 || fail "wildcard subdomain refused"
grep -qx '\*\.clay\.com' "$AD" || fail "wildcard not recorded"

for bad in 'evil.com;rm' '*' 'localhost' 'EVIL.COM' 'a.b.c/x' '-x.com' '*.com' 'evil.com
x.org' ''; do
  rc=0; sr --allow "$bad" >/dev/null 2>&1 || rc=$?
  [ "$rc" = 2 ] || fail "--allow '$bad': exit $rc"
done
rc=0; "${SR[@]}" --allow --dry-run --prefix "$P" >/dev/null 2>&1 || rc=$?
[ "$rc" = 2 ] || fail "--allow without host: exit $rc"
[ "$(grep -c . "$AD")" = 2 ] || fail "a refused host was recorded"
