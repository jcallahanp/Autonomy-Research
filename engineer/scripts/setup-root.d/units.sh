#!/bin/bash
# setup-root.sh: systemd units (sourced).
set -euo pipefail

UNITS="engineer-supervisor chrome-xvfb novnc engineer-remote-control engineer-channels engineer-egress-proxy"
START_AT_INSTALL="chrome-xvfb novnc engineer-egress-proxy"

# install_units: write every unit; start the browser display, noVNC and the proxy. The supervisor
# waits for --lock; Remote Control and channels are enabled by hand after phone pairing.
install_units() {
  local u
  for u in $UNITS; do
    install_file "$OPT/templates/systemd/$u.service" "$P/etc/systemd/system/$u.service" 0644
  done
  run systemctl daemon-reload
  for u in $START_AT_INSTALL; do
    run systemctl enable --now "$u.service"
  done
}

restart_proxy() { run systemctl restart engineer-egress-proxy.service; }
