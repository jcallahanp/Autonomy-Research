#!/bin/bash
set -euo pipefail
# Fetch a task branch and the project's default branch into the supervisor-owned bare clone
# STATE_DIR/audit-clones/<p>.git. Usage: clone.sh PROJECT TASK_ID  (prints the clone's path)
# The task branch comes from the engineer-writable project repo; the base comes only from the broker's mirror
# MIRROR_DIR/<p>.git (GitHub's default branch, kept by sync-mirror), never from the engineer clone's own default
# branch, so a commit the engineer made on its local main is part of the audited diff.
# Only `git fetch file://...` touches either repo, which runs upload-pack there and nothing else. Hooks and
# fsmonitor are off, system config is skipped, and trust for the two source repos is a one-shot global config
# (git drops `-c` settings for the upload-pack it starts on a local repo).
root=$(cd "$(dirname "$(readlink -f "$0")")/../.." && pwd)
. "$root/etc/engineer.conf"
export PATH="$root/bin:/usr/local/bin:/usr/bin:/bin" GIT_CONFIG_NOSYSTEM=1 GIT_TERMINAL_PROMPT=0
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES GIT_CONFIG \
  GIT_CONFIG_PARAMETERS GIT_CONFIG_COUNT GIT_EXEC_PATH GIT_TEMPLATE_DIR GIT_SSH GIT_SSH_COMMAND GIT_ASKPASS

die() { echo "clone: $2" >&2; exit "$1"; }
[ $# -eq 2 ] || die 2 "usage: clone.sh PROJECT TASK_ID"
p=$1 id=$2
[[ $p =~ ^[a-z0-9][a-z0-9-]{0,39}$ ]] || die 2 "bad project name"
[[ $id =~ ^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$ ]] || die 2 "bad task id"
[ -f "$ETC_DIR/projects.txt" ] || die 2 "no $ETC_DIR/projects.txt"
default=$(awk -v p="$p" '$1 == p { print $3; exit }' "$ETC_DIR/projects.txt")
[ -n "$default" ] || die 2 "project $p is not in projects.txt"
[[ $default =~ ^[A-Za-z0-9][A-Za-z0-9._/-]{0,99}$ && $default != *..* ]] || die 2 "bad default branch for $p"

src="$PROJECTS_DIR/$p"
mirror="${MIRROR_DIR:-$STATE_DIR/mirrors}/$p.git"
[ -d "$mirror" ] && [ ! -L "$mirror" ] || die 3 "no broker mirror $mirror (sync-mirror has not run)"
clone="$STATE_DIR/audit-clones/$p.git"
mkdir -p "$STATE_DIR/audit-clones"
cfg=$(mktemp "$STATE_DIR/audit-clones/.fetch-config.XXXXXX")
trap 'rm -f "$cfg"' EXIT
for d in "$src" "$src/.git" "$mirror"; do git config --file "$cfg" --add safe.directory "$d"; done
git config --file "$cfg" core.hooksPath /dev/null
G() { GIT_CONFIG_GLOBAL=$cfg git -c core.hooksPath=/dev/null -c core.fsmonitor= -c protocol.file.allow=always "$@"; }
[ -d "$clone" ] || G init -q --bare --template= "$clone" >&2
fetch() { G --git-dir="$clone" fetch -q --no-tags --no-recurse-submodules --no-write-fetch-head "$@" >&2; }
fetch "file://$mirror" "+refs/heads/$default:refs/audit/base" || die 3 "fetch of $default from the mirror failed"
fetch "file://$src" "+refs/heads/task/$id:refs/audit/head" || die 3 "fetch of task/$id from $src failed"
echo "$clone"
