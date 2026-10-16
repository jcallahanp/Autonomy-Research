#!/bin/bash
# R1-1: setup-root never chmods, chowns or writes through a symlink a non-root user planted (real mode,
# temp prefix). Owner changes are recorded instead of run, since the test users do not exist here.
set -euo pipefail
. "$(dirname "$0")/../lib.sh"

DRY_RUN=0
. "$REPO/engineer/scripts/setup-root.d/common.sh"
. "$REPO/engineer/scripts/setup-root.d/tree.sh"
P="$T/fs"
mkdir -p "$P/var/lib/engineer" "$P/home/engineer/projects" "$T/victim"
chmod 0700 "$T/victim"
mkdir -p "$P/var/log/engineer"
# On the droplet these dirs belong to supervisor, engineer and egress; as root, hand them to nobody so
# the symlinks planted below are untrusted (a root-owned link in a root-owned dir would be followed).
[ "$(id -u)" != 0 ] || chown 65534:65534 "$P/var/lib/engineer" "$P/home/engineer" "$P/var/log/engineer"
plog="$T/priv.log"
# Record privileged steps instead of running them (no engineer/secretbroker users in the test box).
run() { echo "RUN $*" >> "$plog"; }
own() { echo "OWN $*" >> "$plog"; }
expect_refusal() {  # expect_refusal WHAT CMD...: exit 1, victim untouched, nothing privileged done
  local what=$1 rc=0; shift
  : > "$plog"
  ( "$@" ) >/dev/null 2>&1 || rc=$?
  [ "$rc" = 1 ] || fail "$what: exit $rc, want 1"
  [ "$(stat -c %a "$T/victim")" = 700 ] || fail "$what: victim mode changed to $(stat -c %a "$T/victim")"
  [ ! -s "$plog" ] || fail "$what: privileged step ran: $(cat "$plog")"
}

# The reviewer's repro: supervisor (owner of /var/lib/engineer) plants mirrors -> victim before a re-run.
ln -s "$T/victim" "$P/var/lib/engineer/mirrors"
expect_refusal "symlinked mirrors" make_dir "$P/var/lib/engineer/mirrors" 2750 secretbroker:engineer
rm "$P/var/lib/engineer/mirrors"

# A symlink higher up the path is refused too, with no owner given.
ln -s "$T/victim" "$P/var/lib/engineer/records"
expect_refusal "symlinked parent" make_dir "$P/var/lib/engineer/records/sub" 0755
rm "$P/var/lib/engineer/records"

# Engineer's own tree: refused before any runuser step.
ln -s "$T/victim" "$P/home/engineer/.engineer"
expect_refusal "symlinked .engineer" make_dir "$P/home/engineer/.engineer/chrome-profile" 0700 engineer:engineer
rm "$P/home/engineer/.engineer"

# A plain directory works: mode set, owner change recorded as a no-follow chown.
: > "$plog"
make_dir "$P/var/lib/engineer/mirrors" 2750 secretbroker:engineer || fail "real dir refused"
[ "$(stat -c %a "$P/var/lib/engineer/mirrors")" = 2750 ] || fail "mirrors mode"
grep -qx "OWN secretbroker:engineer $P/var/lib/engineer/mirrors" "$plog" || fail "no owner step: $(cat "$plog")"

# Engineer-owned dirs are made and chmodded as engineer, never by root.
: > "$plog"
make_dir "$P/home/engineer/.engineer/chrome-profile" 0700 engineer:engineer || fail "engineer dir"
grep -qx "RUN runuser -u engineer -- mkdir -p $P/home/engineer/.engineer/chrome-profile" "$plog" \
  || fail "engineer dir not made as engineer: $(cat "$plog")"
grep -qx "RUN runuser -u engineer -- chmod 0700 $P/home/engineer/.engineer/chrome-profile" "$plog" \
  || fail "engineer dir not chmodded as engineer: $(cat "$plog")"
grep -q '^OWN' "$plog" && fail "root chowned an engineer dir"

# fsafe.py itself: chmod and chown refuse a symlink as the last component; write replaces one.
ln -s "$T/victim" "$P/var/lib/engineer/link"
rc=0; python3 -I "$FSAFE" "$P" chmod "$P/var/lib/engineer/link" 0777 2>/dev/null || rc=$?
[ "$rc" = 1 ] && [ "$(stat -c %a "$T/victim")" = 700 ] || fail "fsafe chmod followed a symlink (rc $rc)"
rc=0; python3 -I "$FSAFE" "$P" chown "$P/var/lib/engineer/link" root:root 2>/dev/null || rc=$?
[ "$rc" = 1 ] || fail "fsafe chown followed a symlink (rc $rc)"
echo data > "$T/victim/file"; ln -s "$T/victim/file" "$P/var/lib/engineer/out.txt"
echo new | python3 -I "$FSAFE" "$P" write "$P/var/lib/engineer/out.txt" 0644 || fail "fsafe write failed"
[ "$(cat "$T/victim/file")" = data ] || fail "fsafe write went through the symlink"
[ ! -L "$P/var/lib/engineer/out.txt" ] && [ "$(cat "$P/var/lib/engineer/out.txt")" = new ] || fail "write result"
rc=0; python3 -I "$FSAFE" "$P" mkdir "$T/outside" 0755 2>/dev/null || rc=$?
[ "$rc" = 2 ] || fail "path outside the root: exit $rc"

# The egress log in the egress-writable log dir: a planted symlink is refused, never chowned.
ln -s "$T/victim/file" "$P/var/log/engineer/egress-denied.log"
expect_refusal "symlinked egress log" egress_log
rm "$P/var/log/engineer/egress-denied.log"
: > "$plog"; egress_log || fail "egress_log on a clean dir"
[ "$(stat -c %a "$P/var/log/engineer/egress-denied.log")" = 640 ] || fail "egress log mode"
grep -qx "OWN egress:egress $P/var/log/engineer/egress-denied.log" "$plog" || fail "egress log owner"
exit 0
