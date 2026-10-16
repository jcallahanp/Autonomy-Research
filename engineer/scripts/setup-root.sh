#!/bin/bash
set -euo pipefail
# Root setup for the engineer droplet. Run once as root on setup day (see engineer/docs).
# Usage: setup-root.sh MODE [--dry-run] [--prefix DIR] [--src DIR] [--research-plugin DIR]
#   MODE: --install | --lock | --unlock | --allow HOST
#   --dry-run  print each privileged command as "RUN: <cmd>" instead of running it; file writes still
#              happen, under --prefix, which must then be a directory other than /
#   --prefix   prepended to every path written (default /); real runs need EUID 0 and --prefix /
#   --src      the engineer/ tree to install (default: the tree this script lives in)
#   --research-plugin  the research-agent plugin to take skills and agents from (default <src>/../plugin)
# Exit codes: 0 done, 1 refused or failed, 2 usage or bad host.
umask 022
here=$(cd "$(dirname "$(readlink -f "$0")")" && pwd)

usage() { sed -n '4,11p' "$0" | sed 's/^# \{0,1\}//' >&2; exit 2; }

MODE="" HOST="" DRY_RUN=0 PREFIX=/ SRC="" RESEARCH_PLUGIN=""
while [ $# -gt 0 ]; do
  case "$1" in
    --install|--lock|--unlock) [ -z "$MODE" ] || usage; MODE=${1#--} ;;
    --allow) [ -z "$MODE" ] && [ $# -ge 2 ] || usage; MODE=allow; HOST=$2; shift ;;
    --dry-run) DRY_RUN=1 ;;
    --prefix) [ $# -ge 2 ] || usage; PREFIX=$2; shift ;;
    --src) [ $# -ge 2 ] || usage; SRC=$2; shift ;;
    --research-plugin) [ $# -ge 2 ] || usage; RESEARCH_PLUGIN=$2; shift ;;
    *) usage ;;
  esac
  shift
done
[ -n "$MODE" ] || usage

. "$here/setup-root.d/common.sh"
. "$here/setup-root.d/allow.sh"

# Validate the host before anything else, so a bad one never reaches a file.
if [ "$MODE" = allow ]; then valid_host "$HOST" || die "not an allowed host pattern: $HOST" 2; fi

if [ "$DRY_RUN" = 1 ]; then
  [ "$PREFIX" != / ] || die "--dry-run needs --prefix DIR (a directory other than /)"
else
  [ "$EUID" -eq 0 ] || die "must run as root (or use --dry-run --prefix DIR)"
  [ "$PREFIX" = / ] || die "a real run must use --prefix /"
fi
mkdir -p "$PREFIX"
P=$(cd "$PREFIX" && pwd); [ "$P" != / ] || P=""
SRC=$(cd "${SRC:-$here/..}" && pwd)
RESEARCH_PLUGIN=${RESEARCH_PLUGIN:-$SRC/../plugin}
OPT=$P/opt/engineer
ETC=$P/etc/engineer

for f in users packages tree managed units egress lock; do . "$here/setup-root.d/$f.sh"; done

case "$MODE" in
  install) do_install ;;
  lock) do_lock ;;
  unlock) do_unlock ;;
  allow) do_allow "$HOST" ;;
esac
echo "setup-root: $MODE done$([ "$DRY_RUN" = 1 ] && echo ' (dry run)' || true)"
