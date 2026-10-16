#!/bin/bash
set -euo pipefail
# Shared helpers for the bash broker jobs. Source it after setting `root`; it is not a job.
# Exit codes: 64 usage, 65 bad input (refused), 77 caller not allowed.
# shellcheck disable=SC1091
. "$root/etc/engineer.conf"
# Broker git reads no global config and never prompts; repo config is only ever the broker's own mirror's.
export GIT_CONFIG_GLOBAL=/dev/null GIT_TERMINAL_PROMPT=0 GH_PROMPT_DISABLED=1 GH_NO_UPDATE_NOTIFIER=1

NAME_RE='^[a-z0-9][a-z0-9-]{0,39}$'
ID_RE='^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$'

die() { echo "$(basename "$0"): $2" >&2; exit "$1"; }

need_caller() { [ -n "${AGENT_RUN_CALLER:-}" ] || die 77 "run through agent-run"; }

# secret NAME: print one decrypted value (eng.brokerlib.secret); only NAME is on a command line.
secret() {
  python3 -I -c '
import sys
sys.path.insert(0, sys.argv[1] + "/scripts")
from eng import brokerlib, conf
sys.stdout.write(brokerlib.secret(conf.load(sys.argv[1]), sys.argv[2]))
' "$root" "$1" </dev/null
}

# project_row NAME: set P_REPO P_DEFAULT P_SELF_MERGE P_SCRATCH P_OWNER from ETC_DIR/projects.txt, or exit 65.
project_row() {
  local name=$1 n repo def rest kv
  [[ "$name" =~ $NAME_RE ]] || die 65 "bad project name"
  P_REPO=; P_DEFAULT=; P_SELF_MERGE=off; P_SCRATCH=no; P_OWNER=
  while read -r n repo def rest; do
    [ "$n" = "$name" ] || continue
    P_REPO=$repo; P_DEFAULT=$def
    for kv in $rest; do
      case "$kv" in
        self_merge=*) P_SELF_MERGE=${kv#*=} ;;
        scratch=*) P_SCRATCH=${kv#*=} ;;
        owner_login=*) P_OWNER=${kv#*=} ;;
      esac
    done
    break
  done < <(grep -v '^[[:space:]]*#' "$ETC_DIR/projects.txt" 2>/dev/null || true)
  [ -n "$P_REPO" ] || die 65 "project not in projects.txt: $name"
  [[ "$P_REPO" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]] || die 65 "bad owner/repo for $name"
  [[ "$P_DEFAULT" =~ ^[A-Za-z0-9][A-Za-z0-9._/-]*$ ]] || die 65 "bad default branch for $name"
  [[ "$P_OWNER" =~ ^[A-Za-z0-9-]*$ ]] || die 65 "bad owner_login for $name"
}

# branch_ok BRANCH: exit 65 unless BRANCH is a plain branch name other than the default, main or master.
branch_ok() {
  local b=$1
  [[ "$b" =~ ^[A-Za-z0-9][A-Za-z0-9._/-]{0,199}$ ]] || die 65 "bad branch name"
  case "$b" in
    *..*|*//*|*/|*.lock|*.|*/.*|HEAD) die 65 "bad branch name" ;;
    main|master|"$P_DEFAULT") die 65 "refusing the default branch" ;;
  esac
  git check-ref-format "refs/heads/$b" || die 65 "bad branch name"
}

# git_with_pat ARGS...: run one git command with the bot PAT as an http.extraheader in its environment only.
# The PAT stays in local variables; printf is a builtin, so it is never on a command line.
git_with_pat() {
  local pat auth
  pat=$(secret GH_BOT_PAT)
  [ -n "$pat" ] || die 1 "GH_BOT_PAT is empty"
  auth=$(printf 'x-access-token:%s' "$pat" | base64 -w0)
  GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0="http.$GITHUB_URL/.extraheader" GIT_CONFIG_VALUE_0="AUTHORIZATION: basic $auth" \
    git "$@"
}
