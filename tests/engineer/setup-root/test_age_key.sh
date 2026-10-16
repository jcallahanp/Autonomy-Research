#!/bin/bash
# install_age_key for real (not dry run) in a temp prefix: key 0600, recipient from it, never printed, never replaced.
set -euo pipefail
. "$(dirname "$0")/../lib.sh"
command -v age-keygen >/dev/null || { echo "SKIP age-keygen not installed"; exit 0; }

DRY_RUN=0
. "$REPO/engineer/scripts/setup-root.d/common.sh"
. "$REPO/engineer/scripts/setup-root.d/users.sh"
P="$T/fs"
# chown and runuser need the real users: record the owner change, run runuser's command as this user.
own() { echo "CHOWN chown -h $*" >> "$T/chown.log"; }
run() {
  if [ "$1" = runuser ]; then echo "AS $3: ${*:5}" >> "$T/runuser.log"; shift 4; fi
  "$@"
}
K="$P/home/secretbroker/.config/sops/age"
mkdir -p "$P/home/secretbroker"

out=$(install_age_key 2>&1) || fail "install_age_key failed: $out"
[ "$(stat -c %a "$K/keys.txt" 2>/dev/null)" = 600 ] || fail "key not 0600"
for d in .config .config/sops .config/sops/age; do
  [ "$(stat -c %a "$P/home/secretbroker/$d")" = 700 ] || fail "$d not 0700"
done
grep -q '^AGE-SECRET-KEY-' "$K/keys.txt" || fail "no private key written"
[ "$(cat "$K/recipient.txt")" = "$(age-keygen -y "$K/keys.txt")" ] || fail "recipient does not match the key"
grep -Eqx 'age1[a-z0-9]+' "$K/recipient.txt" || fail "recipient is not one age1 line"
echo "$out" | grep -q 'AGE-SECRET-KEY' && fail "private key printed"
grep -qx "CHOWN chown -h secretbroker:secretbroker $K/keys.txt" "$T/chown.log" || fail "key not chowned"
grep -qx "CHOWN chown -h secretbroker:secretbroker $K/recipient.txt" "$T/chown.log" || fail "recipient not chowned"
grep -qx "AS secretbroker: age-keygen -o $K/keys.txt" "$T/runuser.log" || fail "age-keygen not run as secretbroker"

# Idempotent: an existing key is never replaced; a lost recipient is rebuilt from it.
before=$(sha256sum < "$K/keys.txt")
rm "$K/recipient.txt"
out=$(install_age_key 2>&1) || fail "second run failed: $out"
[ "$before" = "$(sha256sum < "$K/keys.txt")" ] || fail "existing key replaced"
[ "$(cat "$K/recipient.txt")" = "$(age-keygen -y "$K/keys.txt")" ] || fail "recipient not rebuilt"
echo "$out" | grep -q 'AGE-SECRET-KEY' && fail "private key printed on rerun"

# A symlink at the key path is refused, not followed.
rm "$K/keys.txt"; ln -s "$T/elsewhere" "$K/keys.txt"
rc=0; (install_age_key) >/dev/null 2>&1 || rc=$?
[ "$rc" = 1 ] || fail "symlinked key path: exit $rc"
[ ! -e "$T/elsewhere" ] || fail "key written through a symlink"
exit 0
