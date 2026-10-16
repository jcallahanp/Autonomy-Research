#!/bin/bash
# setup-root.sh --install: managed settings, sudoers, AppArmor profile (sourced).
set -euo pipefail

MANAGED="$P/etc/claude-code/managed-settings.json"

# install_managed: managed settings from the template, without a hooks key (--lock adds it).
install_managed() {
  install_file "$OPT/templates/managed-settings.json" "$MANAGED" 0644
  settings_hooks "$MANAGED" off
}

# install_sudoers: checked with visudo before it goes live; sudo skips file names with a dot.
install_sudoers() {
  local dest="$P/etc/sudoers.d/engineer" tmp="$P/etc/sudoers.d/engineer.setup-root.tmp"
  mkdir -p "$(dirname "$dest")"
  cp "$OPT/templates/sudoers/engineer" "$tmp"
  chmod 0440 "$tmp"
  run visudo -cf "$tmp"
  mv -f "$tmp" "$dest"
}

install_apparmor() {
  install_file "$OPT/templates/apparmor/bwrap" "$P/etc/apparmor.d/bwrap" 0644
  run apparmor_parser -r "$P/etc/apparmor.d/bwrap"
}
