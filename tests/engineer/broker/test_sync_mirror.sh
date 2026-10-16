#!/bin/bash
# sync-mirror PROJECT: the broker fetches the default branch from GitHub into an engineer-readable bare mirror.
set -euo pipefail
. "$(dirname "$0")/../lib.sh"
. "$REPO/tests/engineer/broker/helpers.sh"

# A git wrapper that records which calls carry the PAT header in their environment.
stub "$R" git "if [ -n \"\${GIT_CONFIG_VALUE_0:-}\" ]; then echo \"\$*\" >> '$T/hdr.calls'; printf '%s' \"\$GIT_CONFIG_VALUE_0\" > '$T/hdr.seen'; fi
exec /usr/bin/git \"\$@\""

remote="$T/remotes/owner/demo.git"
git init -q --bare "$remote"
new_clone "$T/seed"
git -C "$T/seed" push -q "$remote" main task/t1
m="$STATE_DIR/mirrors/demo.git"

# --- test_sync_mirror_fetches_default_branch
expect 0 "sync-mirror demo" as supervisor sync-mirror demo
[ "$(git --git-dir="$m" rev-parse main)" = "$(git --git-dir="$remote" rev-parse main)" ] || fail "mirror main differs"
jq -e --arg s "$(git --git-dir="$remote" rev-parse main)" '.project == "demo" and .branch == "main" and .sha == $s' "$T/out" \
  >/dev/null || fail "sync-mirror output: $(cat "$T/out")"
git --git-dir="$m" rev-parse -q --verify refs/heads/task/t1 >/dev/null && fail "mirror holds a non-default branch"
[ -z "$(find "$m" -perm -o=r -print -quit)" ] || fail "mirror is world-readable"
[ -z "$(find "$m" -type f ! -perm -g=r -print -quit)" ] || fail "mirror file not group-readable"
[ -z "$(ls -A "$m/hooks" 2>/dev/null)" ] || fail "mirror has hook files"

# --- test_sync_mirror_updates: a new commit on GitHub reaches the mirror on the next sync.
echo two > "$T/seed/two.txt" && git -C "$T/seed" add two.txt && git -C "$T/seed" commit -qm "feat: two"
git -C "$T/seed" push -q "$remote" main
expect 0 "second sync" as supervisor sync-mirror demo
[ "$(git --git-dir="$m" rev-parse main)" = "$(git -C "$T/seed" rev-parse main)" ] || fail "mirror not updated"

# --- test_sync_mirror_records_branch: engineer-records is mirrored once it exists on GitHub, never before.
jq -e '.records == null' "$T/out" >/dev/null || fail "records sha without the branch: $(cat "$T/out")"
git --git-dir="$m" rev-parse -q --verify refs/heads/engineer-records >/dev/null && fail "records branch before it exists"
git -C "$T/seed" checkout -q -b engineer-records
echo rec > "$T/seed/rec.txt" && git -C "$T/seed" add rec.txt && git -C "$T/seed" commit -qm "docs: records"
git -C "$T/seed" push -q "$remote" engineer-records
git -C "$T/seed" checkout -q main
expect 0 "sync with records" as supervisor sync-mirror demo
rsha=$(git --git-dir="$remote" rev-parse engineer-records)
[ "$(git --git-dir="$m" rev-parse engineer-records 2>/dev/null)" = "$rsha" ] || fail "records branch not mirrored"
jq -e --arg s "$rsha" '.records == $s and .branch == "main"' "$T/out" >/dev/null || fail "records sha: $(cat "$T/out")"
[ -z "$(find "$m" -type f ! -perm -g=r -print -quit)" ] || fail "records objects not group-readable"
git --git-dir="$remote" branch -q -D engineer-records
expect 0 "sync after records deleted" as supervisor sync-mirror demo
git --git-dir="$m" rev-parse -q --verify refs/heads/engineer-records >/dev/null && fail "deleted records branch kept"
git --git-dir="$remote" branch -q engineer-records "$rsha"

# --- test_sync_mirror_token_not_in_argv
[ "$(base64 -d < <(sed 's/^AUTHORIZATION: basic //' "$T/hdr.seen"))" = "x-access-token:TEST-TOKEN-PAT" ] \
  || fail "fetch did not carry the bot PAT header"
grep -v -e ' fetch ' -e ' ls-remote ' "$T/hdr.calls" && fail "header env reached a git call other than fetch or ls-remote"
b64=$(printf 'x-access-token:TEST-TOKEN-PAT' | base64 -w0)
for f in "$T/argv.log" "$T/out" "$T/err" "$BROKER_STATE_DIR/agent-run.log"; do
  grep -qe TEST-TOKEN-PAT -e "$b64" "$f" && fail "test_sync_mirror_token_not_in_argv: token in $f"
done

# --- test_sync_mirror_pr_head: --pr N also fetches GitHub's refs/pull/N/head (the plan PR John approves).
git -C "$T/seed" checkout -q -b plan/v1
echo plan > "$T/seed/plan.txt" && git -C "$T/seed" add plan.txt && git -C "$T/seed" commit -qm "docs: plan v1"
psha=$(git -C "$T/seed" rev-parse HEAD)
git -C "$T/seed" checkout -q main
git -C "$T/seed" push -q "$remote" "$psha:refs/pull/3/head"
jq -e '.pr == null' "$T/out" >/dev/null || fail "pr without --pr: $(cat "$T/out")"
expect 0 "sync with --pr" as supervisor sync-mirror demo --pr 3
[ "$(git --git-dir="$m" rev-parse refs/pull/3/head 2>/dev/null)" = "$psha" ] || fail "PR head not in the mirror"
jq -e --arg s "$psha" '.pr == {number: 3, sha: $s} and .branch == "main"' "$T/out" >/dev/null \
  || fail "--pr output: $(cat "$T/out")"
expect 1 "unknown PR" as supervisor sync-mirror demo --pr 4
expect 65 "PR not a number" as supervisor sync-mirror demo --pr 3x
expect 64 "--pr without number" as supervisor sync-mirror demo --pr

# --- test_sync_mirror_refusals
expect 77 "engineer may not sync" as engineer sync-mirror demo
expect 65 "bad project name" as supervisor sync-mirror Bad_Name
expect 65 "project not listed" as supervisor sync-mirror stranger
expect 64 "no project" as supervisor sync-mirror
expect 64 "extra args" as supervisor sync-mirror demo main
exit 0
