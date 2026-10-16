#!/bin/bash
# push-branch: fetch into a broker-owned mirror, push from there with the PAT only in the environment.
set -euo pipefail
. "$(dirname "$0")/../lib.sh"
. "$REPO/tests/engineer/broker/helpers.sh"

# A git wrapper that logs argv (ps-style capture) and records the header env only for `push`.
stub "$R" git "if [ \"\${2:-}\" = push ]; then printf '%s' \"\${GIT_CONFIG_VALUE_0:-}\" > '$T/hdr.seen'
elif [ -n \"\${GIT_CONFIG_VALUE_0:-}\" ]; then echo \"\$*\" >> '$T/hdr.leak'; fi
exec /usr/bin/git \"\$@\""

remote="$T/remotes/owner/demo.git"
git init -q --bare "$remote"
src="$PROJECTS_DIR/demo"
new_clone "$src"
git -C "$src" worktree add -q -b task/t2 "$PROJECTS_DIR/demo.wt/t2" main
echo t2 > "$PROJECTS_DIR/demo.wt/t2/t2.txt"
git -C "$PROJECTS_DIR/demo.wt/t2" add t2.txt && git -C "$PROJECTS_DIR/demo.wt/t2" commit -qm "feat: t2"
# On the droplet the clone belongs to engineer, not to the broker: give it to another user here too.
git config --file "$GIT_CONFIG_GLOBAL" safe.directory '*'
chown -R nobody "$src" "$PROJECTS_DIR/demo.wt"
rsha() { git --git-dir="$remote" rev-parse -q --verify "$1" 2>/dev/null || echo none; }

# --- test_push_branch_ignores_repo_config: arm the source clone, prove the trap works, then push.
mkdir -p "$T/evil-hooks"
printf '#!/bin/sh\ntouch %s/pwned\n' "$T" > "$T/evil-hooks/pre-push"
cp "$T/evil-hooks/pre-push" "$src/.git/hooks/pre-push"
cp "$T/evil-hooks/pre-push" "$T/evil-hooks/post-checkout"
chmod 755 "$T/evil-hooks/pre-push" "$T/evil-hooks/post-checkout" "$src/.git/hooks/pre-push"
git -C "$src" config core.fsmonitor "touch $T/pwned"
git -C "$src" config core.hooksPath "$T/evil-hooks"
git -C "$src" config uploadpack.packObjectsHook "touch $T/pwned;"
git -C "$src" config core.sshCommand "touch $T/pwned;"
git -C "$src" status >/dev/null 2>&1 || true
[ -e "$T/pwned" ] || fail "positive control: core.fsmonitor did not fire for git status"
rm -f "$T/pwned"

expect 0 "push task/t1 from the main clone" as engineer push-branch "$src" task/t1
[ "$(rsha refs/heads/task/t1)" = "$(git -C "$src" rev-parse task/t1)" ] || fail "remote task/t1 not pushed"
jq -e --arg s "$(git -C "$src" rev-parse task/t1)" '.branch == "task/t1" and .sha == $s' "$T/out" >/dev/null \
  || fail "push-branch output: $(cat "$T/out")"
[ -e "$T/pwned" ] && fail "test_push_branch_ignores_repo_config: engineer-controlled config ran"
[ -d "$BROKER_STATE_DIR/mirrors/demo.git" ] || fail "no broker mirror"
[ -z "$(ls -A "$BROKER_STATE_DIR/mirrors/demo.git/hooks" 2>/dev/null)" ] || fail "mirror has hook files"

expect 0 "push task/t2 from a worktree" as supervisor push-branch "$PROJECTS_DIR/demo.wt/t2" task/t2
[ "$(rsha refs/heads/task/t2)" = "$(git -C "$PROJECTS_DIR/demo.wt/t2" rev-parse HEAD)" ] || fail "remote task/t2"
[ -e "$T/pwned" ] && fail "worktree push ran engineer-controlled config"

# A rewritten branch is not force-pushed.
git -C "$src" -c core.fsmonitor=false -c core.hooksPath=/dev/null branch -qf task/t1 main
expect 1 "non-fast-forward push" as engineer push-branch "$src" task/t1
[ "$(rsha refs/heads/task/t1)" != "$(git -C "$src" -c core.fsmonitor=false rev-parse main)" ] || fail "force-pushed"

# --- test_push_branch_token_not_in_argv
[ "$(base64 -d < <(sed 's/^AUTHORIZATION: basic //' "$T/hdr.seen"))" = "x-access-token:TEST-TOKEN-PAT" ] \
  || fail "push did not carry the bot PAT header: $(cat "$T/hdr.seen" 2>/dev/null)"
[ -e "$T/hdr.leak" ] && fail "header env reached a non-push git call: $(cat "$T/hdr.leak")"
b64=$(printf 'x-access-token:TEST-TOKEN-PAT' | base64 -w0)
for f in "$T/argv.log" "$T/out" "$T/err" "$BROKER_STATE_DIR/agent-run.log"; do
  grep -qe TEST-TOKEN-PAT -e "$b64" "$f" && fail "test_push_branch_token_not_in_argv: token in $f"
done
grep -q '^git .*push' "$T/argv.log" || fail "git stub did not see the push"

# --- Refusals.
expect 65 "main" as engineer push-branch "$src" main
expect 65 "master" as engineer push-branch "$src" master
expect 65 "leading dash" as engineer push-branch "$src" -x
expect 65 "dot-dot" as engineer push-branch "$src" 'a..b'
expect 65 "bad ref" as engineer push-branch "$src" 'a b'
expect 77 "engineer pushes engineer-records" as engineer push-branch "$src" engineer-records
expect 65 "--tag v1" as supervisor push-branch "$src" task/t1 --tag v1
expect 77 "engineer pushes a tag" as engineer push-branch "$src" task/t1 --tag plan-approved-1
expect 65 "outside PROJECTS_DIR" as engineer push-branch "$T/remotes" task/t1
expect 65 "dot-dot path" as engineer push-branch "$PROJECTS_DIR/demo/../demo" task/t1
expect 65 "relative path" as engineer push-branch demo task/t1
mkdir -p "$PROJECTS_DIR/stranger" && expect 65 "project not in projects.txt" as engineer push-branch "$PROJECTS_DIR/stranger" task/t1
new_clone "$T/outside"
ln -s "$T/outside" "$PROJECTS_DIR/quiet"
expect 65 "symlinked project dir" as engineer push-branch "$PROJECTS_DIR/quiet" task/t1
mkdir -p "$PROJECTS_DIR/demo.wt/forged"
echo "gitdir: $T/outside/.git" > "$PROJECTS_DIR/demo.wt/forged/.git"
expect 65 "worktree .git pointing outside the project" as engineer push-branch "$PROJECTS_DIR/demo.wt/forged" task/t1
expect 64 "missing args" as engineer push-branch "$src"

# --- Records clone: supervisor only, branch engineer-records plus a plan-approved tag.
rec="$RECORDS_DIR/demo"
git clone -q "$src" "$rec" 2>/dev/null
git -C "$rec" checkout -qb engineer-records
echo verdict > "$rec/AUDIT.md" && git -C "$rec" add AUDIT.md && git -C "$rec" commit -qm "docs: audit"
git -C "$rec" tag plan-approved-1
expect 77 "engineer pushes from the records clone" as engineer push-branch "$rec" engineer-records
expect 0 "supervisor pushes records with a tag" as supervisor push-branch "$rec" engineer-records --tag plan-approved-1
[ "$(rsha refs/heads/engineer-records)" = "$(git -C "$rec" rev-parse HEAD)" ] || fail "records branch not pushed"
[ "$(rsha refs/tags/plan-approved-1)" = "$(git -C "$rec" rev-parse plan-approved-1)" ] || fail "tag not pushed"
exit 0
