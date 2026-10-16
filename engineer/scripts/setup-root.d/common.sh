#!/bin/bash
# Shared helpers for setup-root.sh (sourced). Needs DRY_RUN; P (prefix, "" for /) is set after sourcing.
set -euo pipefail

die() { echo "setup-root: $1" >&2; exit "${2:-1}"; }

# run CMD...: a privileged command. Dry run prints "RUN: CMD"; otherwise runs it.
run() {
  if [ "$DRY_RUN" = 1 ]; then echo "RUN: $*"; else "$@"; fi
}

# install_file SRC DEST MODE: copy SRC to DEST (a prefixed path) atomically with MODE.
install_file() {
  mkdir -p "$(dirname "$2")"
  local tmp="$2.setup-root.tmp"
  cp "$1" "$tmp" && chmod "$3" "$tmp" && mv -f "$tmp" "$2"
}

# write_file DEST MODE: stdin to DEST atomically with MODE.
write_file() {
  mkdir -p "$(dirname "$1")"
  local tmp="$1.setup-root.tmp"
  cat > "$tmp" && chmod "$2" "$tmp" && mv -f "$tmp" "$1"
}

FSAFE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/fsafe.py"

# fsafe OP PATH ARG: fsafe.py under the prefix; never follows a symlink a non-root user planted.
fsafe() { python3 -I "$FSAFE" "${P:-/}" "$@" || exit "$?"; }

# own OWNER PATH: chown PATH without following a symlink anywhere on it (privileged: dry run prints it).
own() {
  if [ "$DRY_RUN" = 1 ]; then echo "RUN: chown -h $1 $2"; else fsafe chown "$2" "$1"; fi
}

# make_dir DIR MODE [OWNER]: create DIR (prefixed) with MODE, refusing a symlink on its path.
# Engineer's own dirs are made and chmodded as engineer (runuser), so root never acts inside a tree
# the model can write; any other owner is set by a no-follow chown after the mode.
make_dir() {
  local dir=$1 mode=$2 owner=${3:-}
  if [ "${owner%%:*}" = engineer ]; then
    fsafe check "$dir" -
    if [ "$DRY_RUN" = 1 ]; then fsafe mkdir "$dir" "$mode"; fi
    run runuser -u engineer -- mkdir -p "$dir"
    run runuser -u engineer -- chmod "$mode" "$dir"
    return
  fi
  fsafe mkdir "$dir" "$mode"
  [ -z "$owner" ] || own "$owner" "$dir"
}

# rows FILE: the non-comment, non-blank lines of FILE.
rows() { grep -v '^[[:space:]]*#' "$1" | grep -v '^[[:space:]]*$' || true; }

# settings_hooks FILE off | FILE on HOOKS_JSON: remove or set the "hooks" key of a managed settings file.
settings_hooks() {
  python3 - "$@" <<'PY'
import json, os, sys
path, mode = sys.argv[1], sys.argv[2]
with open(path) as f:
    settings = json.load(f)
settings.pop("hooks", None)
if mode == "on":
    with open(sys.argv[3]) as f:
        hooks = json.load(f)
    if set(hooks) == {"hooks"}:
        hooks = hooks["hooks"]
    if not isinstance(hooks, dict) or not hooks:
        sys.exit("setup-root: managed hooks file has no hooks")
    settings["hooks"] = hooks
tmp = path + ".setup-root.tmp"
with open(tmp, "w") as f:
    json.dump(settings, f, indent=2)
    f.write("\n")
os.chmod(tmp, 0o644)
os.replace(tmp, path)
PY
}

# uid_of USER: the uid, or "<USER-uid>" in a dry run when the user does not exist yet.
uid_of() {
  if getent passwd "$1" >/dev/null; then id -u "$1"
  elif [ "$DRY_RUN" = 1 ]; then echo "<$1-uid>"
  else die "user $1 does not exist"
  fi
}
