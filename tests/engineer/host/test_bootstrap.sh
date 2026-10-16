#!/bin/bash
# bootstrap.sh (Task 4): pinned user-level installs as engineer, never as root, never "latest".
set -euo pipefail
. "$(dirname "$0")/../lib.sh"

root=$(mk_root "$T")
export HOME="$T/home"; mkdir -p "$HOME"
unset ANTHROPIC_API_KEY CLAUDE_CODE_OAUTH_TOKEN
stub "$root" id 'echo 1000'
B="$root/scripts/bootstrap.sh"

# Release fixture: one tarball, one bare binary, checksums in templates/release-pins.txt.
A="$T/assets"; mkdir -p "$A/pkg"
printf 'fake gitleaks\n' > "$A/pkg/gitleaks"
tar -C "$A/pkg" -czf "$A/gitleaks_8.30.1_linux_x64.tar.gz" gitleaks
printf 'fake osv\n' > "$A/osv-scanner_linux_amd64"
sum() { sha256sum "$1" | cut -d' ' -f1; }
pins="$root/templates/release-pins.txt"
write_pins() {
  printf '# fixture\nsops\thttps://example.invalid/sops\t%s\n' "$(printf 'a%.0s' $(seq 64))" > "$pins"
  printf 'gitleaks\thttps://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_linux_x64.tar.gz\t%s\n' "$1" >> "$pins"
  printf 'osv-scanner\thttps://github.com/google/osv-scanner/releases/download/v2.7.0/osv-scanner_linux_amd64\t%s\n' "$2" >> "$pins"
}
write_pins "$(sum "$A/gitleaks_8.30.1_linux_x64.tar.gz")" "$(sum "$A/osv-scanner_linux_amd64")"

# Dry run prints one pinned npm install per npm row and runs nothing.
out=$(bash "$B" --dry-run 2>&1) || fail "dry run exit $?: $out"
while IFS=$'\t' read -r name method pin; do
  case "$name" in ''|'#'*) continue ;; esac
  [ "$method" = npm ] || continue
  echo "$out" | grep -qF "npm install -g --prefix $HOME/.local $name@$pin" || fail "dry run lacks $name@$pin"
done < "$root/templates/bootstrap-packages.txt"
echo "$out" | grep -q 'pipx install --force semgrep==1.181.0' || fail "dry run lacks pipx row"
echo "$out" | grep -q 'telegram@claude-plugins-official' || fail "dry run lacks Channels plugin"
echo "$out" | grep -q 'gitleaks_8.30.1_linux_x64.tar.gz' || fail "dry run lacks gitleaks download"
grep -qv '^id ' "$T/argv.log" 2>/dev/null && fail "dry run ran a command: $(grep -v '^id ' "$T/argv.log")"
[ ! -e "$HOME/.local/bin/gitleaks" ] || fail "dry run installed gitleaks"

# Real run with stubbed npm, pipx, claude and curl (curl copies the fixture asset).
for c in npm pipx claude; do stub "$root" "$c"; done
stub "$root" curl 'u=""; o=""; while [ $# -gt 0 ]; do case "$1" in -o) o=$2; shift ;; https://*) u=$1 ;; esac; shift; done; cp "'"$A"'/$(basename "$u")" "$o"'
rm -f "$T/argv.log"
out=$(bash "$B" 2>&1) || fail "real run exit $?: $out"
grep -qx "npm install -g --prefix $HOME/.local @anthropic-ai/claude-code@2.1.301" "$T/argv.log" || fail "npm not called with pin"
grep -qx 'claude plugin install telegram@claude-plugins-official --scope user' "$T/argv.log" || fail "plugin not installed"
[ "$(cat "$HOME/.local/bin/gitleaks" 2>/dev/null)" = "fake gitleaks" ] || fail "gitleaks not installed from tarball"
[ "$(cat "$HOME/.local/bin/osv-scanner" 2>/dev/null)" = "fake osv" ] || fail "osv-scanner not installed"
[ -x "$HOME/.local/bin/osv-scanner" ] || fail "osv-scanner not executable"

# A checksum mismatch stops before installing that binary.
rm -f "$HOME/.local/bin/osv-scanner"
write_pins "$(sum "$A/gitleaks_8.30.1_linux_x64.tar.gz")" "$(printf 'b%.0s' $(seq 64))"
rc=0; out=$(bash "$B" 2>&1) || rc=$?
[ "$rc" -eq 1 ] || fail "checksum mismatch exit $rc"
echo "$out" | grep -q 'osv-scanner' || fail "mismatch does not name osv-scanner: $out"
[ ! -e "$HOME/.local/bin/osv-scanner" ] || fail "mismatched binary installed"

# A release row with no checksum (or TO-PIN) fails before anything runs, also in dry run.
write_pins "$(sum "$A/gitleaks_8.30.1_linux_x64.tar.gz")" TO-PIN
rc=0; out=$(bash "$B" --dry-run 2>&1) || rc=$?
[ "$rc" -eq 1 ] && echo "$out" | grep -q 'osv-scanner' || fail "TO-PIN checksum: exit $rc: $out"
write_pins "$(sum "$A/gitleaks_8.30.1_linux_x64.tar.gz")" "$(sum "$A/osv-scanner_linux_amd64")"

# Pins "latest", empty and TO-PIN are refused, naming the row.
cp "$root/templates/bootstrap-packages.txt" "$T/packages.orig"
for bad in latest TO-PIN ''; do
  cp "$T/packages.orig" "$root/templates/bootstrap-packages.txt"
  printf 'left-pad\tnpm\t%s\n' "$bad" >> "$root/templates/bootstrap-packages.txt"
  rc=0; out=$(bash "$B" --dry-run 2>&1) || rc=$?
  [ "$rc" -eq 1 ] || fail "pin '$bad': exit $rc"
  echo "$out" | grep -q 'left-pad' || fail "pin '$bad': row not named: $out"
done
cp "$T/packages.orig" "$root/templates/bootstrap-packages.txt"
printf 'thing\tcurl-pipe-sh\t1.0.0\n' >> "$root/templates/bootstrap-packages.txt"
rc=0; bash "$B" --dry-run >/dev/null 2>&1 || rc=$?
[ "$rc" -eq 1 ] || fail "unknown method: exit $rc"
cp "$T/packages.orig" "$root/templates/bootstrap-packages.txt"

# Root is refused.
stub "$root" id 'echo 0'
rc=0; out=$(bash "$B" --dry-run 2>&1) || rc=$?
[ "$rc" -eq 1 ] && echo "$out" | grep -q 'run as engineer' || fail "root: exit $rc: $out"
stub "$root" id 'echo 1000'

# Path A only: an API key or OAuth token in the environment is refused.
for v in ANTHROPIC_API_KEY CLAUDE_CODE_OAUTH_TOKEN; do
  rc=0; out=$(env "$v=TEST-TOKEN-fake" bash "$B" --dry-run 2>&1) || rc=$?
  [ "$rc" -eq 1 ] && echo "$out" | grep -q "$v" || fail "$v set: exit $rc: $out"
  echo "$out" | grep -q 'TEST-TOKEN-fake' && fail "$v value printed"
done

# Unknown argument.
rc=0; bash "$B" --bogus >/dev/null 2>&1 || rc=$?
[ "$rc" -eq 2 ] || fail "unknown argument: exit $rc"
