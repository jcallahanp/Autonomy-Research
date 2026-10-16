#!/bin/bash
set -euo pipefail
# Install the engineer's user-level tools, pinned, as the engineer user (setup.md step 8).
# Usage: bootstrap.sh [--dry-run]
#   Rows come from <root>/templates/bootstrap-packages.txt (name<TAB>method<TAB>pin):
#     npm             npm install -g --prefix "$HOME/.local" <name>@<pin>
#     github-release  download the URL in templates/release-pins.txt (name<TAB>url<TAB>sha256),
#                     check its sha256, install the binary to $HOME/.local/bin
#     pipx            pipx install --force <name>==<pin>
#   Then the Channels Telegram plugin at user scope (the one exception, repo-composition.md).
#   --dry-run prints each command instead of running it. Every row is checked before anything runs.
# Exit: 0 done, 1 refused or failed (root, Path B credentials, bad pin, checksum), 2 usage.
root=$(cd "$(dirname "$(readlink -f "$0")")/.." && pwd)
export PATH="$root/bin:$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin"

# Channels plugin name from https://code.claude.com/docs/en/channels (read 2026-10-16).
PLUGIN="telegram@claude-plugins-official"
MARKETPLACE="anthropics/claude-plugins-official"
PACKAGES="$root/templates/bootstrap-packages.txt"
RELEASES="$root/templates/release-pins.txt"

dry=0
case "${1:-}" in
  "") ;;
  --dry-run) dry=1 ;;
  *) echo "usage: bootstrap.sh [--dry-run]" >&2; exit 2 ;;
esac
[ $# -le 1 ] || { echo "usage: bootstrap.sh [--dry-run]" >&2; exit 2; }

die() { echo "bootstrap: $*" >&2; exit 1; }

# John's decision 1: Claude Max via /login only; no API key, no setup-token.
for v in ANTHROPIC_API_KEY CLAUDE_CODE_OAUTH_TOKEN; do
  [ -z "${!v:-}" ] || die "$v is set; Path A (Max /login) only: unset it and run again"
done
[ "$(id -u)" != 0 ] || die "run as engineer, not root"
[ -n "${HOME:-}" ] && [ -d "$HOME" ] || die "HOME is not a directory"

run() {
  if [ "$dry" -eq 1 ]; then printf '+'; printf ' %q' "$@"; printf '\n'; else "$@"; fi
}

# Pass 1: check every row; refuse unpinned or unknown rows before installing anything.
rows=()
n=0
while IFS= read -r line || [ -n "$line" ]; do
  n=$((n+1))
  case "$line" in ''|'#'*) continue ;; esac
  IFS=$'\t' read -r name method pin _ <<<"$line"
  where="bootstrap-packages.txt:$n ($name)"
  [[ "$name" =~ ^[@a-z0-9][a-z0-9._/@-]*$ ]] || die "$where: bad package name"
  case "${pin:-}" in
    ''|latest|TO-PIN) die "$where: pin '${pin:-}' is not a version; pin it (docs/versions.md)" ;;
  esac
  [[ "$pin" =~ ^[0-9A-Za-z][0-9A-Za-z.+-]*$ ]] || die "$where: bad pin '$pin'"
  case "$method" in
    npm|pipx) ;;
    github-release)
      rel=$(awk -F'\t' -v n="$name" '$1 == n { print $2 "\t" $3; exit }' "$RELEASES" 2>/dev/null || true)
      url=${rel%%$'\t'*}; sha=${rel#*$'\t'}
      [ -n "$rel" ] || die "$where: no row in templates/release-pins.txt"
      [[ "$sha" =~ ^[0-9a-f]{64}$ ]] || die "$where: release-pins.txt checksum '$sha' is not a sha256"
      [[ "$url" == https://github.com/*"$pin"* ]] || die "$where: release URL is not a github.com URL for $pin"
      ;;
    *) die "$where: unknown method '$method'" ;;
  esac
  rows+=("$name"$'\t'"$method"$'\t'"$pin")
done < "$PACKAGES"

install_release() {  # install_release NAME PIN
  local name=$1 rel url sha tmp bin
  rel=$(awk -F'\t' -v n="$name" '$1 == n { print $2 "\t" $3; exit }' "$RELEASES")
  url=${rel%%$'\t'*}; sha=${rel#*$'\t'}
  if [ "$dry" -eq 1 ]; then
    tmp=/tmp/tmp.XXXXXXXXXX
    run curl -fsSL --proto '=https' --max-redirs 3 -o "$tmp/asset" "$url"
    echo "+ sha256 check $sha $tmp/asset"
    run install -m 0755 "$tmp/$name" "$HOME/.local/bin/$name"
    return
  fi
  tmp=$(mktemp -d)
  curl -fsSL --proto '=https' --max-redirs 3 -o "$tmp/asset" "$url" || { rm -rf "$tmp"; die "$name: download failed"; }
  if ! printf '%s  %s\n' "$sha" "$tmp/asset" | sha256sum -c --quiet - >/dev/null 2>&1; then
    rm -rf "$tmp"; die "$name: sha256 mismatch for $url; not installed"
  fi
  case "$url" in
    *.tar.gz|*.tgz)
      mkdir "$tmp/x"; tar -xzf "$tmp/asset" -C "$tmp/x"
      bin=$(find "$tmp/x" -maxdepth 2 -type f -name "$name" | head -1) ;;
    *) bin="$tmp/asset" ;;
  esac
  [ -n "$bin" ] || { rm -rf "$tmp"; die "$name: binary not found in $url"; }
  install -m 0755 "$bin" "$HOME/.local/bin/$name"
  rm -rf "$tmp"
}

# Pass 2: install.
[ "$dry" -eq 1 ] || mkdir -p "$HOME/.local/bin"
for row in "${rows[@]}"; do
  IFS=$'\t' read -r name method pin <<<"$row"
  case "$method" in
    npm) run npm install -g --prefix "$HOME/.local" "$name@$pin" ;;
    pipx) run pipx install --force "$name==$pin" ;;
    github-release) install_release "$name" "$pin" ;;
  esac
done

if [ "$dry" -eq 1 ]; then
  run claude plugin install "$PLUGIN" --scope user
elif ! claude plugin install "$PLUGIN" --scope user; then
  claude plugin marketplace add "$MARKETPLACE"
  claude plugin install "$PLUGIN" --scope user
fi
if [ "$dry" -eq 1 ]; then echo "bootstrap: dry run, nothing installed"; else echo "bootstrap: done"; fi
