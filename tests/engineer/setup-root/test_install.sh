#!/bin/bash
# setup-root.sh --install in dry run: tree, plugin, managed settings, users, units, idempotence, guards.
set -euo pipefail
. "$(dirname "$0")/../lib.sh"
. "$(dirname "$0")/fixtures.sh"

out=$(sr --install 2>&1) || fail "install --dry-run exit $?: $out"
E="$P/opt/engineer"
[ "$(jq -c . "$E/plugin/hooks/hooks.json" 2>/dev/null)" = '{"hooks":{}}' ] || fail "hooks.json is not {\"hooks\":{}}"
for s in interview research tool-scan repo-triage spike system-map setup; do
  [ -f "$E/plugin/skills/$s/SKILL.md" ] || fail "research skill $s not copied"
done
for a in researcher synthesizer verifier spike-worker; do
  [ -f "$E/plugin/agents/$a.md" ] || fail "agent $a not copied"
done
[ ! -e "$E/plugin/skills/self-test" ] || fail "self-test skill should not be copied"
[ -s "$E/SOURCE_SHA" ] || fail "SOURCE_SHA missing"
[ -f "$E/scripts/setup-root.sh" ] || fail "src not copied"
M="$P/etc/claude-code/managed-settings.json"
jq -e 'has("hooks") | not' "$M" >/dev/null 2>&1 || fail "managed settings missing or has hooks"
jq -e '.permissions.disableBypassPermissionsMode == "disable"' "$M" >/dev/null 2>&1 || fail "managed settings content"
for u in engineer supervisor secretbroker egress; do
  echo "$out" | grep -Eq "^RUN: useradd .*[ ]$u\$" || getent passwd "$u" >/dev/null || fail "no useradd for $u"
done
echo "$out" | grep -Eq '^RUN: useradd .*--shell /bin/bash engineer$' || fail "engineer has no login shell"
for u in chrome-xvfb novnc engineer-egress-proxy; do
  grep -qx "RUN: systemctl enable --now $u.service" <<<"$out" || fail "$u not enabled"
done
grep -q 'enable.*engineer-supervisor' <<<"$out" && fail "engineer-supervisor enabled at install"
for u in engineer-supervisor engineer-remote-control engineer-channels chrome-xvfb; do
  [ -f "$P/etc/systemd/system/$u.service" ] || fail "unit $u not installed"
done
[ "$(stat -c %a "$P/etc/sudoers.d/engineer" 2>/dev/null)" = 440 ] || fail "sudoers not 0440"
[ "$(stat -c %a "$P/var/lib/engineer/spool" 2>/dev/null)" = 1770 ] || fail "spool not 1770"
for d in records approvals checks audit-clones; do [ -d "$P/var/lib/engineer/$d" ] || fail "no $d"; done
[ "$(stat -c %a "$P/home/engineer/.engineer/chrome-profile" 2>/dev/null)" = 700 ] || fail "chrome profile not 0700"
# Mirrors: the broker's sync-mirror job writes them; run-task as engineer reads them.
[ "$(stat -c %a "$P/var/lib/engineer/mirrors" 2>/dev/null)" = 2750 ] || fail "mirrors not 2750"
grep -qx "RUN: chown -h secretbroker:engineer $P/var/lib/engineer/mirrors" <<<"$out" || fail "mirrors not secretbroker:engineer"
# supervisor reads the mirrors too (records.ensure clones engineer-records from them), never writes.
# Set by the owner, never following a symlink (-P).
SB="RUN: runuser -u secretbroker -- setfacl"
grep -qx "$SB -m u:supervisor:rX $P/var/lib/engineer/mirrors" <<<"$out" || fail "no supervisor ACL on mirrors"
grep -qx "$SB -R -P -d -m u:supervisor:rX $P/var/lib/engineer/mirrors" <<<"$out" || fail "no default supervisor ACL on mirrors"
echo "$out" | grep '^RUN: .*setfacl -R ' | grep -qv -- '-R -P' && fail "a recursive setfacl may follow symlinks"
grep -qx 'MIRROR_DIR=/var/lib/engineer/mirrors' "$REPO/engineer/etc/engineer.conf" || fail "engineer.conf has no MIRROR_DIR"
# The secret store's age key: made with age-keygen (a privileged step), never printed; dirs 0700.
K=/home/secretbroker/.config/sops/age
grep -qx "AGE_KEY_FILE=$K/keys.txt" "$REPO/engineer/etc/engineer.conf" || fail "AGE_KEY_FILE differs from setup-root's"
grep -qx "AGE_RECIPIENT_FILE=$K/recipient.txt" "$REPO/engineer/etc/engineer.conf" || fail "AGE_RECIPIENT_FILE differs"
grep -qx "RUN: runuser -u secretbroker -- age-keygen -o $P$K/keys.txt" <<<"$out" || fail "no age-keygen as secretbroker"
grep -qx "RUN: age-keygen -y $P$K/keys.txt > $P$K/recipient.txt" <<<"$out" || fail "no recipient written in dry run"
grep -qx "RUN: chown -h secretbroker:secretbroker $P$K/keys.txt" <<<"$out" || fail "age key not owned by secretbroker"
for d in .config .config/sops .config/sops/age; do
  [ "$(stat -c %a "$P/home/secretbroker/$d" 2>/dev/null)" = 700 ] || fail "$d not 0700"
done
[ ! -e "$P$K/keys.txt" ] || fail "dry run wrote an age key"
grep -qx "MIRROR_DIR=\"$T/src/var/lib/engineer/mirrors\"" "$SRC/etc/engineer.conf" || fail "mk_root does not rewrite MIRROR_DIR"
[ -d "$P/var/log/engineer" ] || fail "no /var/log/engineer"
cmp -s "$P/etc/engineer/egress.txt" "$SRC/templates/egress-install.txt" || fail "egress.txt is not the install list"
[ -f "$P/etc/apparmor.d/bwrap" ] || fail "apparmor profile not written"
EN="RUN: runuser -u engineer -- setfacl"
grep -qx "$EN -R -P -m u:supervisor:rX $P/home/engineer/projects" <<<"$out" || fail "no supervisor ACL"
grep -qx "$EN -R -P -d -m u:supervisor:rX $P/home/engineer/projects" <<<"$out" || fail "no default supervisor ACL"
grep -qx "$EN -m u:supervisor:x $P/home/engineer" <<<"$out" || fail "no supervisor x on engineer home"
echo "$out" | grep -Eq '^RUN: .*render-nft.py --uid engineer=.* --uid supervisor=.* --lo engineer=3128,5900 --lo supervisor=3128 ' || fail "nft render not printed with loopback ports"
grep -q '^RUN: apparmor_parser -r ' <<<"$out" || fail "apparmor_parser not printed"
grep -q '^RUN: .*apt-get install .*google-chrome-stable' <<<"$out" || fail "apt-get install not printed"
grep -q '^RUN: curl .*sops-test.* > .*/usr/local/bin/sops$' <<<"$out" || fail "root release not installed"
grep -q 'tool.tar.gz' <<<"$out" && fail "user-scope release installed by setup-root"
[ "$(stat -c %U:%a "$P/var/log/engineer" 2>/dev/null)" = "$(id -un):1775" ] || fail "/var/log/engineer not 1775"
grep -qx "RUN: chown -h root:egress $P/var/log/engineer" <<<"$out" || fail "/var/log/engineer not group egress"
# Engineer's dirs are made by engineer; root never chowns or chmods inside engineer's home.
grep -qx "RUN: runuser -u engineer -- mkdir -p $P/home/engineer/.engineer/chrome-profile" <<<"$out" || fail "chrome profile owner"
grep -qx "RUN: runuser -u engineer -- chmod 0700 $P/home/engineer/.engineer/chrome-profile" <<<"$out" || fail "chrome profile mode"
grep -q "^RUN: chown .*$P/home/engineer/" <<<"$out" && fail "root chowns inside engineer's home"

# Idempotent: a second run leaves the same tree.
before=$(tree_sum "$P")
sr --install >/dev/null 2>&1 || fail "second install failed"
[ "$before" = "$(tree_sum "$P")" ] || fail "second install changed the tree"

# A TO-PIN row stops the install, naming the row.
cp "$SRC/templates/release-pins.txt" "$T/pins.bak"
printf 'sops\thttps://example.invalid/sops\tTO-PIN\troot\n' > "$SRC/templates/release-pins.txt"
rc=0; o=$(sr --install 2>&1) || rc=$?
[ "$rc" = 1 ] || fail "TO-PIN release pin: exit $rc"
grep -q 'sops' <<<"$o" || fail "TO-PIN error does not name the row: $o"
cp "$T/pins.bak" "$SRC/templates/release-pins.txt"
sed -i "s/$FPR/TO-PIN/" "$SRC/templates/apt-repos.txt"
rc=0; o=$(sr --install 2>&1) || rc=$?
[ "$rc" = 1 ] && grep -q testrepo <<<"$o" || fail "TO-PIN apt key: exit $rc: $o"

# Not root and not dry run: refuse before doing anything.
if [ "$(id -u)" = 0 ]; then
  chmod 755 "$T"
  as_user=(setpriv --reuid=65534 --regid=65534 --clear-groups)
else
  as_user=()
fi
rc=0; o=$("${as_user[@]}" bash "$SRC/scripts/setup-root.sh" --install 2>&1) || rc=$?
[ "$rc" = 1 ] && grep -q 'must run as root' <<<"$o" || fail "non-root install: exit $rc: $o"

# Dry run must not write to the real filesystem.
rc=0; o=$("${as_user[@]}" bash "$SRC/scripts/setup-root.sh" --install --dry-run --src "$SRC" 2>&1) || rc=$?
[ "$rc" = 1 ] && grep -q -- <<<"$o" '--prefix' || fail "dry run with prefix /: exit $rc: $o"
rc=0; "${SR[@]}" --bogus >/dev/null 2>&1 || rc=$?
[ "$rc" = 2 ] || fail "unknown option: exit $rc"
