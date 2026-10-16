#!/bin/bash
set -euo pipefail
# mirror.sh NAME SRC_DIR REFSPEC...: fetch refs from an engineer- or supervisor-owned repo into the broker's
# bare mirror BROKER_STATE_DIR/mirrors/NAME.git; prints the mirror path. Run as BROKER_USER by push-branch.
# The only git command that touches SRC_DIR is `git fetch file://SRC_DIR`, which runs upload-pack there:
# upload-pack runs no hooks and no fsmonitor and ignores uploadpack.packObjectsHook from repo config.
# Trust for SRC_DIR (another user's repo) goes in a one-shot global config (`safe.directory = SRC_DIR/.git`),
# because git clears `-c` settings (GIT_CONFIG_PARAMETERS) for the local upload-pack it starts.
root=$(cd "$(dirname "$(readlink -f "$0")")/../.." && pwd)
# shellcheck disable=SC1091
. "$root/scripts/broker/common.sh"

[ $# -ge 3 ] || die 64 "usage: mirror.sh NAME SRC_DIR REFSPEC..."
name=$1 src=$2
shift 2
[[ "$name" =~ $NAME_RE ]] || die 65 "bad mirror name"
case "$src" in /*) ;; *) die 65 "SRC_DIR must be absolute" ;; esac

umask 077
m="$BROKER_STATE_DIR/mirrors/$name.git"
if [ ! -d "$m" ]; then
  mkdir -p "$BROKER_STATE_DIR/mirrors"
  git init -q --bare --template= "$m"
  git --git-dir="$m" config core.hooksPath /dev/null
fi

cfg=$(mktemp "$BROKER_STATE_DIR/fetch-config.XXXXXX")
trap 'rm -f "$cfg"' EXIT
git config --file "$cfg" safe.directory "$src/.git"
git config --file "$cfg" core.hooksPath /dev/null
GIT_CONFIG_GLOBAL=$cfg git --git-dir="$m" -c protocol.file.allow=always \
  fetch --quiet --no-tags --no-recurse-submodules --no-write-fetch-head "file://$src" "$@" >&2
echo "$m"
