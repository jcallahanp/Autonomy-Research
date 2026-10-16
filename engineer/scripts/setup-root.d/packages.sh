#!/bin/bash
# setup-root.sh --install: pin checks, third-party apt repos, apt packages, release binaries (sourced).
set -euo pipefail

NAME_RE='^[a-z0-9][a-z0-9-]*$'
FPR_RE='^[0-9A-F]{40}(,[0-9A-F]{40})*$'
SHA_RE='^[0-9a-f]{64}$'

# check_pins: refuse any apt-repos.txt or release-pins.txt row that is TO-PIN or malformed (both modes).
check_pins() {
  local name url fpr deb sha bad=0
  while IFS=$'\t' read -r name url fpr deb; do
    if ! [[ $name =~ $NAME_RE && $url == https://* && $fpr =~ $FPR_RE ]] \
       || [[ $deb != "deb ["*"signed-by=/etc/apt/keyrings/$name.gpg"*"] https://"* ]]; then
      echo "setup-root: apt-repos.txt row '$name' is not pinned (fingerprint '$fpr') or malformed" >&2; bad=1
    fi
  done < <(rows "$SRC/templates/apt-repos.txt")
  while IFS=$'\t' read -r name url sha scope; do
    if ! [[ $name =~ $NAME_RE && $url == https://* && $sha =~ $SHA_RE && $scope =~ ^(root|user)$ ]]; then
      echo "setup-root: release-pins.txt row '$name' is not pinned (sha256 '$sha') or malformed" >&2; bad=1
    fi
  done < <(rows "$SRC/templates/release-pins.txt")
  [ "$bad" = 0 ] || die "fill the pins above, then run again"
}

# fetch_key NAME URL FPRS: download a repo key, require its primary keys to equal FPRS, install it binary.
fetch_key() {
  local dest="$P/etc/apt/keyrings/$1.gpg"
  if [ "$DRY_RUN" = 1 ]; then
    echo "RUN: curl -fsSL --proto =https $2 (primary keys must be $3) | gpg --dearmor > $dest"
    return
  fi
  local tmp got want
  tmp=$(mktemp -d); mkdir -m 700 "$tmp/gnupg"
  curl -fsSL --proto '=https' "$2" -o "$tmp/key"
  got=$(GNUPGHOME="$tmp/gnupg" gpg --show-keys --with-colons "$tmp/key" \
        | awk -F: '$1=="pub"{p=1;next} $1=="fpr"&&p{print $10;p=0}' | sort | paste -sd, -)
  want=$(tr ',' '\n' <<<"$3" | sort | paste -sd, -)
  [ "$got" = "$want" ] || { rm -rf "$tmp"; die "key for $1 has primary keys '$got', expected '$want'"; }
  if grep -q 'BEGIN PGP PUBLIC KEY BLOCK' "$tmp/key"; then
    GNUPGHOME="$tmp/gnupg" gpg --dearmor < "$tmp/key" > "$tmp/key.gpg"
  else
    cp "$tmp/key" "$tmp/key.gpg"
  fi
  install_file "$tmp/key.gpg" "$dest" 0644
  rm -rf "$tmp"
}

install_repos() {
  local name url fpr deb
  make_dir "$P/etc/apt/keyrings" 0755
  while IFS=$'\t' read -r name url fpr deb; do
    fetch_key "$name" "$url" "$fpr"
    printf '# Written by setup-root.sh from engineer/templates/apt-repos.txt\n%s\n' "$deb" \
      | write_file "$P/etc/apt/sources.list.d/engineer-$name.list" 0644
  done < <(rows "$SRC/templates/apt-repos.txt")
}

install_packages() {
  local pkgs
  pkgs=$(rows "$SRC/templates/apt-packages.txt" | tr -s ' \t\n' ' ')
  run apt-get update
  # shellcheck disable=SC2086  # one word per package
  run env DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends $pkgs
}

# unpack_one NAME FILE URL: print the path of the binary NAME in FILE (unpacked if URL is an archive).
unpack_one() {
  local dir found
  case "$3" in
    *.zip|*.tar.gz|*.tgz)
      dir=$(dirname "$2")/x; mkdir "$dir"
      case "$3" in *.zip) unzip -q "$2" -d "$dir" ;; *) tar -xzf "$2" -C "$dir" ;; esac
      found=$(find "$dir" -type f -name "$1")
      [ -n "$found" ] && [ "$(wc -l <<<"$found")" = 1 ] || die "$3 does not hold exactly one file called $1"
      echo "$found" ;;
    *) echo "$2" ;;
  esac
}

# install_releases: each scope-root release-pins.txt row to /usr/local/bin/<name> after a sha256 check.
install_releases() {
  local name url sha scope dest tmp
  while IFS=$'\t' read -r name url sha scope; do
    [ "$scope" = root ] || continue
    dest="$P/usr/local/bin/$name"
    if [ "$DRY_RUN" = 1 ]; then
      echo "RUN: curl -fsSL --proto =https $url (sha256 must be $sha) > $dest"
      continue
    fi
    tmp=$(mktemp -d)
    curl -fsSL --proto '=https' "$url" -o "$tmp/asset"
    echo "$sha  $tmp/asset" | sha256sum -c --quiet - || { rm -rf "$tmp"; die "sha256 mismatch for $name"; }
    install_file "$(unpack_one "$name" "$tmp/asset" "$url")" "$dest" 0755
    rm -rf "$tmp"
  done < <(rows "$SRC/templates/release-pins.txt")
}
