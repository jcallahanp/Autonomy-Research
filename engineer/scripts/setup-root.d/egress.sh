#!/bin/bash
set -euo pipefail
# setup-root.sh: the egress allowlist files and the per-uid nft rules (sourced).
#   /etc/engineer/egress.txt        active allowlist, read by the proxy
#   /etc/engineer/egress-added.txt  hosts added with --allow, kept across --lock/--unlock

EGRESS="$ETC/egress.txt"
EGRESS_ADDED="$ETC/egress-added.txt"
NFT_FILE="$ETC/egress.nft"
NFT_TABLE="inet engineer_egress"

# egress_install_list: the install-time list (wider: package registries, sign-in pages).
egress_install_list() {
  install_file "$OPT/templates/egress-install.txt" "$EGRESS" 0644
}

# egress_runtime_list: the runtime allowlist plus every host added with --allow, each once.
egress_runtime_list() {
  {
    echo "# Written by setup-root.sh --lock: templates/egress-allowlist.txt plus egress-added.txt"
    { cat "$OPT/templates/egress-allowlist.txt"; [ ! -f "$EGRESS_ADDED" ] || cat "$EGRESS_ADDED"; } \
      | sed 's/#.*//' | awk 'NF && !seen[$1]++ {print $1}'
  } | write_file "$EGRESS" 0644
}

# X11VNC_PORT: where novnc-session's x11vnc listens; websockify (engineer) connects to it on loopback.
X11VNC_PORT=5900

# conf_port KEY: a numeric port from the installed engineer.conf.
conf_port() {
  local v
  v=$(sed -n "s/^$1=\"\{0,1\}\([0-9]\{1,5\}\)\"\{0,1\}\$/\1/p" "$OPT/etc/engineer.conf" | tail -1)
  [ -n "$v" ] || die "no numeric $1 in $OPT/etc/engineer.conf"
  echo "$v"
}

# install_nft: render the rules for engineer and supervisor, load them atomically, load them at boot.
# On loopback, engineer may open only the proxy and x11vnc ports, supervisor only the proxy (R1-8).
install_nft() {
  local render="$OPT/scripts/egress/render-nft.py" e s px args
  e=$(uid_of engineer); s=$(uid_of supervisor); px=$(conf_port PROXY_PORT)
  args="--uid engineer=$e --uid supervisor=$s --lo engineer=$px,$X11VNC_PORT --lo supervisor=$px"
  if [ "$DRY_RUN" = 1 ]; then
    echo "RUN: python3 $render $args > $NFT_FILE"
  else
    # The rendered file starts "table X; delete table X", so a reload replaces the table atomically.
    # shellcheck disable=SC2086  # args holds plain words checked above
    python3 "$render" $args > "$NFT_FILE.setup-root.tmp"
    grep -qx "delete table $NFT_TABLE" "$NFT_FILE.setup-root.tmp" || die "render-nft.py output does not replace $NFT_TABLE"
    chmod 0644 "$NFT_FILE.setup-root.tmp"; mv -f "$NFT_FILE.setup-root.tmp" "$NFT_FILE"
  fi
  run nft -f "$NFT_FILE"
  local conf="$P/etc/nftables.conf" inc="include \"/etc/engineer/egress.nft\""
  if ! grep -qxF "$inc" "$conf" 2>/dev/null; then
    { [ ! -f "$conf" ] || cat "$conf"; echo "$inc"; } | write_file "$conf" 0644
  fi
  run systemctl enable nftables.service
}
