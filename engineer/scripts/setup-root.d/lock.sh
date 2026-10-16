#!/bin/bash
# setup-root.sh --install, --lock, --unlock (sourced after the other setup-root.d files).
set -euo pipefail

do_install() {
  [ ! -e "$OPT/LOCKED" ] || die "the engineer is locked; run --unlock first"
  check_pins
  install_users
  install_repos
  install_packages
  install_releases
  install_tree
  install_dirs
  install_managed
  install_sudoers
  install_units
  egress_install_list
  install_nft
  install_apparmor
}

# do_lock: managed hooks on, LOCKED written, runtime egress list, proxy restarted, supervisor on.
do_lock() {
  [ -f "$OPT/SOURCE_SHA" ] && [ -f "$MANAGED" ] || die "not installed; run --install first"
  local hooks="$OPT/templates/managed-hooks.json"
  [ -f "$hooks" ] || die "no $hooks; the managed hooks are what lock turns on"
  settings_hooks "$MANAGED" on "$hooks"
  write_file "$OPT/LOCKED" 0644 < "$OPT/SOURCE_SHA"
  egress_runtime_list
  restart_proxy
  run systemctl enable --now engineer-supervisor.service
}

# do_unlock: supervisor off first, then hooks off, LOCKED removed, install egress list back.
do_unlock() {
  [ -f "$OPT/SOURCE_SHA" ] && [ -f "$MANAGED" ] || die "not installed; run --install first"
  run systemctl disable --now engineer-supervisor.service
  settings_hooks "$MANAGED" off
  rm -f "$OPT/LOCKED"
  egress_install_list
  restart_proxy
}
