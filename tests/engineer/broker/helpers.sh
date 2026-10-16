# Sourced by tests/engineer/broker/test_*.sh and run-task/test_*.sh after ../lib.sh.
# Sets R (temp root), loads its engineer.conf, writes fake secrets, a projects.txt, a sops stub,
# a git identity for fixture commits, and `as USER JOB ARGS...` (agent-run with SUDO_USER=USER).
R=$(mk_root "$T")
sed -i "s|^GITHUB_URL=.*|GITHUB_URL=\"file://$T/remotes\"|" "$R/etc/engineer.conf"
# shellcheck disable=SC1091
. "$R/etc/engineer.conf"
stub "$R" sops "$(cat "$REPO/tests/engineer/broker/sops-stub.sh")"
mkdir -p "$(dirname "$SECRETS_FILE")" "$(dirname "$AGE_RECIPIENT_FILE")" "$T/remotes/owner"
printf '{"GH_BOT_PAT": "TEST-TOKEN-PAT", "ATTIO_API_KEY": "TEST-TOKEN-ATTIO"}\n' > "$SECRETS_FILE"
printf 'age1testrecipientnotarealkey\n' > "$AGE_RECIPIENT_FILE"
touch "$AGE_KEY_FILE"
cat > "$ETC_DIR/projects.txt" <<'EOF'
# name owner/repo default_branch self_merge scratch owner_login
demo owner/demo main self_merge=on scratch=no owner_login=example-owner
quiet owner/quiet main self_merge=off scratch=yes owner_login=example-owner
EOF
export GIT_CONFIG_GLOBAL="$T/gitconfig" GIT_CONFIG_NOSYSTEM=1
git config --file "$GIT_CONFIG_GLOBAL" user.name "Test Bot"
git config --file "$GIT_CONFIG_GLOBAL" user.email "test@example.invalid"
git config --file "$GIT_CONFIG_GLOBAL" commit.gpgsign false
git config --file "$GIT_CONFIG_GLOBAL" init.defaultBranch main

as() { local who=$1; shift; SUDO_USER=$who "$R/bin/agent-run" "$@"; }

# expect CODE DESC CMD...: run CMD, fail unless it exits CODE.
expect() {
  local want=$1 desc=$2 rc=0; shift 2
  "$@" >"$T/out" 2>"$T/err" || rc=$?
  [ "$rc" -eq "$want" ] || fail "$desc: exit $rc, want $want ($(head -c 300 "$T/err"))"
}

# new_clone DIR: a git repo with one commit on main and a branch task/t1 with one more.
new_clone() {
  git init -q "$1"
  echo hello > "$1/README.md"
  git -C "$1" add README.md && git -C "$1" commit -qm "chore: init"
  git -C "$1" checkout -qb task/t1
  echo t1 > "$1/t1.txt"
  git -C "$1" add t1.txt && git -C "$1" commit -qm "feat: t1"
  git -C "$1" checkout -q main
}
