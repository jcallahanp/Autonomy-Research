#!/bin/bash
set -euo pipefail
# setup-root.sh --install: the four Unix users (sourced).
#   engineer      login shell; runs Claude Code, the browser display and chat sessions
#   supervisor    system, no login; runs the night loop
#   secretbroker  system, no login; owns the SOPS+age secrets and runs broker jobs
#   egress        system, no login; runs the egress proxy

NOLOGIN=/usr/sbin/nologin

add_user() {  # add_user NAME USERADD-ARGS...
  local name=$1; shift
  if getent passwd "$name" >/dev/null; then
    echo "setup-root: user $name exists"
  else
    run useradd "$@" "$name"
  fi
}

install_users() {
  add_user engineer --create-home --shell /bin/bash
  add_user supervisor --system --create-home --home-dir /home/supervisor --shell "$NOLOGIN"
  add_user secretbroker --system --create-home --home-dir /home/secretbroker --shell "$NOLOGIN"
  add_user egress --system --create-home --home-dir /var/lib/egress --shell "$NOLOGIN"
  # Homes the rest of the install writes into (useradd makes them on the droplet).
  make_dir "$P/home/engineer" 0750
  make_dir "$P/home/secretbroker" 0700
}
