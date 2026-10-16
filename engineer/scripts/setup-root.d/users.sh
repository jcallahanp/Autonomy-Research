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

# The secret store's age key: engineer.conf AGE_KEY_FILE and AGE_RECIPIENT_FILE (test_install checks they agree).
AGE_DIR=/home/secretbroker/.config/sops/age

# install_age_key: make the key with age-keygen if there is none (never replaced, never printed) and write
# its public recipient beside it. age-keygen comes from apt-packages.txt (`age`).
install_age_key() {
  local d pub key="$P$AGE_DIR/keys.txt" rec="$P$AGE_DIR/recipient.txt"
  for d in .config .config/sops .config/sops/age; do
    [ ! -L "$P/home/secretbroker/$d" ] || die "$P/home/secretbroker/$d is a symlink"
    make_dir "$P/home/secretbroker/$d" 0700 secretbroker:secretbroker
  done
  [ ! -L "$key" ] && [ ! -L "$rec" ] || die "age key or recipient path is a symlink"
  if [ -e "$key" ]; then
    echo "setup-root: age key exists; not replaced"
  else
    # age-keygen writes the private key only to the file (0600) and the public key to stderr.
    (umask 077 && run age-keygen -o "$key")
  fi
  run chown secretbroker:secretbroker "$key"
  if [ "$DRY_RUN" = 1 ] && [ ! -e "$key" ]; then
    echo "RUN: age-keygen -y $key > $rec"
  else
    chmod 0600 "$key"
    pub=$(age-keygen -y "$key") && [[ $pub =~ ^age1[a-z0-9]+$ ]] || die "cannot read the recipient of $key"
    printf '%s\n' "$pub" | write_file "$rec" 0644
    run chown secretbroker:secretbroker "$rec"
  fi
}
