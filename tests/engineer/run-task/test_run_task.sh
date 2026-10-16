#!/bin/bash
# run-task PROJECT TASK_ID PROFILE [--resume SID] [--dry-run]: fixed claude argv, worktree, refusals.
set -euo pipefail
. "$(dirname "$0")/../lib.sh"
. "$REPO/tests/engineer/broker/helpers.sh"

RT="$R/bin/run-task"
SID=0123abcd-0000-4000-8000-0123456789ab
stub "$R" claude "printf '%s' \"\$2\" > '$T/prompt'
{ echo \"PWD=\$PWD\"; env | grep -E '^(ENGINEER_|HOME=|PATH=|ANTHROPIC|LEAK)' | sort; } > '$T/claude-env'
echo 'progress line'
echo '{\"type\":\"result\",\"subtype\":\"success\",\"is_error\":false,\"num_turns\":3,\"session_id\":\"$SID\",\"total_cost_usd\":0.42,\"permission_denials\":[{\"tool_name\":\"Bash\"}],\"structured_output\":{\"verdict\":\"PASS\"}}'"

src="$PROJECTS_DIR/demo"
new_clone "$src"
mkdir -p "$src/docs/plan"
jq -n '{version: 1, tasks: [
  {id: "t1", title: "T one", type: "feat", status: "ready", depends_on: [], requirement_ids: [], files: [],
   check: "test -f README.md && test ! -e untracked.txt && test ! -e .venv && test -f node_modules/dep/index.js && echo \"at $(git rev-parse HEAD)\" && echo checked-ok",
   passes: false, attempts: 0},
  {id: "t2", title: "T two", type: "fix", status: "ready", depends_on: [], requirement_ids: [], files: [],
   check: "echo failing-check; exit 3", passes: false, attempts: 0}]}' > "$src/docs/plan/tasks.json"
git -C "$src" add docs && git -C "$src" commit -qm "docs: plan"
git -C "$src" rebase -q main task/t1 && git -C "$src" branch -q task/t2 main && git -C "$src" checkout -q main
wt="$PROJECTS_DIR/demo.wt/t1"
# approve [HASH]: the live plan approval, with the sha256 of the committed tasks.json unless HASH is given.
approve() {
  local h=${1:-$(git -C "$src" show main:docs/plan/tasks.json | sha256sum | cut -d' ' -f1)}
  mkdir -p "$STATE_DIR/approvals"
  jq -n --arg h "$h" '{approved_by: "john", date: "2026-10-16", scope_version: 1, gates: [], source: "telegram",
    record_id: "item-1", files: {"docs/plan/tasks.json": $h}}' > "$STATE_DIR/approvals/demo.json"
}
approve
touch "$R/LOCKED"

# --dry-run, implementer.
expect 0 "dry-run implementer" "$RT" demo t1 implementer --dry-run
d="$T/dry.json"; cp "$T/out" "$d"
a=$(jq -r '.argv | join(" ")' "$d")
for want in "-p " "--permission-mode auto --permission-prompts none" "--max-turns 60" "--max-budget-usd 5" \
  "--plugin-dir $R/plugin" "--agent implementer" "--model sonnet" "--output-format json" \
  "timeout --kill-after=30s 45m claude"; do
  case "$a" in *"$want"*) ;; *) fail "dry-run argv lacks '$want': $a" ;; esac
done
case "$a" in *--json-schema*|*--resume*) fail "implementer argv has --json-schema or --resume" ;; esac
jq -e --arg wt "$wt" '.env.ENGINEER_UNATTENDED == "1" and .env.ENGINEER_TASK_ID == "t1"
  and .env.ENGINEER_PROJECT == "demo" and .cwd == $wt' "$d" >/dev/null || fail "dry-run env/cwd: $(jq -c '{cwd, env}' "$d")"
jq -e '.env | has("ANTHROPIC_API_KEY") | not' "$d" >/dev/null || fail "env has ANTHROPIC_API_KEY"
after() { jq -r --arg f "$1" '.argv as $a | $a[($a | index($f)) + 1]' "$2"; }
prompt=$(after -p "$d")
case "$prompt" in *"{{"*) fail "prompt has an unreplaced placeholder" ;; esac
case "$prompt" in *t1*demo*|*demo*t1*) ;; *) fail "prompt lacks task id and project: $prompt" ;; esac
[ -e "$wt" ] && fail "dry-run created the worktree"
# The implementer never edits docs/plan/ (tasks.json is signed; status lives in the supervisor's events).
for f in "$prompt" "$(cat "$R/plugin/agents/implementer.md")"; do
  case "$f" in *"Never edit anything under \`docs/plan/\`"*) ;; *) fail "implementer text lacks the docs/plan rule" ;; esac
  case "$f" in *"to \`done\`"*|*"status\` to"*) fail "implementer text still sets a tasks.json status" ;; esac
done

# Auditor gets --json-schema with the audit-verdict schema as JSON text; --resume is implementer-only.
expect 0 "dry-run auditor" "$RT" demo t1 auditor --dry-run
after --json-schema "$T/out" | jq -e '.properties.verdict' >/dev/null || fail "auditor --json-schema"
[ "$(after --max-turns "$T/out")" = 30 ] || fail "auditor max turns"
expect 0 "resume implementer" "$RT" demo t1 implementer --resume "$SID" --dry-run
[ "$(after --resume "$T/out")" = "$SID" ] || fail "--resume not in argv"
expect 65 "resume for auditor" "$RT" demo t1 auditor --resume "$SID" --dry-run
expect 65 "bad session id" "$RT" demo t1 implementer --resume 'x; rm -rf /' --dry-run

# Refusals.
expect 64 "no args" "$RT"
expect 65 "project Bad_Name" "$RT" Bad_Name t1 implementer --dry-run
expect 65 "project not in projects.txt" "$RT" nope t1 implementer --dry-run
expect 65 "unknown task" "$RT" demo t9 implementer --dry-run
expect 65 "bad task id" "$RT" demo '../t1' implementer --dry-run
expect 65 "unknown profile" "$RT" demo t1 hacker --dry-run
expect 78 "ANTHROPIC_API_KEY set" env ANTHROPIC_API_KEY=x "$RT" demo t1 implementer --dry-run
expect 78 "CLAUDE_CODE_OAUTH_TOKEN set" env CLAUDE_CODE_OAUTH_TOKEN=x "$RT" demo t1 implementer --dry-run
expect 78 "ANTHROPIC_AUTH_TOKEN set" env ANTHROPIC_AUTH_TOKEN=x "$RT" demo t1 implementer --dry-run
touch "$KILL_SWITCH"
expect 75 "kill switch" "$RT" demo t1 implementer --dry-run
rm -f "$KILL_SWITCH"
rm -f "$R/LOCKED"
expect 75 "not locked, scratch=no" "$RT" demo t1 implementer --dry-run
expect 0 "not locked, check profile" "$RT" demo t1 check --dry-run
touch "$R/LOCKED"

# A real implementer run with the stub claude: worktree on task/t1, run-result line.
expect 0 "implementer run" env LEAK_VAR=1 "$RT" demo t1 implementer
[ "$(git -C "$wt" rev-parse --abbrev-ref HEAD 2>/dev/null)" = task/t1 ] || fail "worktree not on task/t1"
grep -qxF "PWD=$wt" "$T/claude-env" || fail "claude cwd: $(head -n1 "$T/claude-env")"
grep -qxF "ENGINEER_UNATTENDED=1" "$T/claude-env" || fail "claude env lacks ENGINEER_UNATTENDED"
grep -q '^LEAK' "$T/claude-env" && fail "caller env reached claude"
case "$(cat "$T/prompt")" in *t1*) ;; *) fail "prompt not passed to claude" ;; esac
validate() {
  python3 - "$1" "$REPO" <<'EOF'
import json, sys
sys.path.insert(0, sys.argv[2] + "/engineer/scripts")
from eng import schema
lines = open(sys.argv[1]).read().splitlines()
assert len(lines) == 1, f"want one line, got {len(lines)}"
doc = json.loads(lines[0])
errs = schema.validate(doc, schema.load(sys.argv[2] + "/engineer", "run-result"))
assert not errs, errs
print(json.dumps(doc))
EOF
}
res=$(validate "$T/out") || fail "run-result invalid: $(cat "$T/out")"
echo "$res" | jq -e --arg s "$SID" --arg h "$(git -C "$wt" rev-parse HEAD)" '.profile == "implementer" and .exit_code == 0
  and .session_id == $s and .cost_usd == 0.42 and .num_turns == 3 and .is_error == false and .timed_out == false
  and .head_sha == $h and (.output_tail | contains("progress line")) and (.permission_denials | length == 1)' >/dev/null \
  || fail "run-result fields: $res"
# base_sha is the branch point (task/t1 already has a commit in the fixture); structured_output is passed on.
echo "$res" | jq -e --arg b "$(git -C "$src" merge-base main task/t1)" '.base_sha == $b and .head_sha != $b
  and .structured_output == {"verdict": "PASS"}' >/dev/null || fail "base_sha/structured_output: $res"
expect 0 "second run reuses the worktree" "$RT" demo t1 implementer

# check profile: the check comes from the approved tasks.json at the task's commit and runs in a clean
# detached checkout of that commit (untracked files in the worktree are not there).
# --- test_check_uses_worktree_deps: untracked dependency dirs of the engineer's worktree (node_modules, .venv,
# vendor ...) are there read-only; a symlinked one is not; git works in the checkout.
touch "$wt/untracked.txt"
mkdir -p "$wt/node_modules/dep" "$T/outside" && echo 'module.exports = 1' > "$wt/node_modules/dep/index.js"
ln -s "$T/outside" "$wt/.venv"
t1=$(git -C "$src" rev-parse task/t1)
expect 0 "check t1" "$RT" demo t1 check
res=$(validate "$T/out") || fail "check run-result invalid: $(cat "$T/out")"
echo "$res" | jq -e --arg h "$t1" '.profile == "check" and .exit_code == 0 and .is_error == false
  and .head_sha == $h and (.output_tail | contains("checked-ok")) and (.output_tail | contains("at " + $h))' \
  >/dev/null || fail "test_check_uses_worktree_deps: $res"
[ -e "$wt/node_modules/dep/index.js" ] || fail "the check removed the worktree's node_modules"
# --- test_check_without_bwrap_warns: this container has no bwrap, so the run says it is unsandboxed.
echo "$res" | jq -e '.output_tail | contains("bwrap not found")' >/dev/null || fail "no bwrap warning: $res"
[ "$(git -C "$src" worktree list | grep -c run-task-check)" -eq 0 ] || fail "check checkout left behind"
expect 0 "check t1 at an explicit sha" "$RT" demo t1 check --sha "$t1"
expect 65 "--sha not a sha" "$RT" demo t1 check --sha main
expect 65 "--sha for the implementer" "$RT" demo t1 implementer --sha "$t1" --dry-run
# A working-tree edit of tasks.json changes nothing: t2's approved check still fails.
jq '.tasks[1].check = "echo hacked"' "$src/docs/plan/tasks.json" > "$T/tasks.json" && cp "$T/tasks.json" "$src/docs/plan/tasks.json"
expect 0 "check t2 (failing check still prints a result)" "$RT" demo t2 check
echo "$(cat "$T/out")" | jq -e '.exit_code == 3 and .is_error == true and (.output_tail | contains("failing-check"))' >/dev/null \
  || fail "failing check result: $(cat "$T/out")"
[ -e "$PROJECTS_DIR/demo.wt/t2" ] && fail "the check profile created a worktree"
git -C "$src" checkout -q docs/plan/tasks.json
# --- test_check_refuses_unapproved_tasks_json: a commit whose tasks.json is not the approved copy.
git -C "$wt" -c core.hooksPath=/dev/null checkout -q -- . 2>/dev/null || true
jq '.tasks[0].check = "echo sneaky"' "$wt/docs/plan/tasks.json" > "$T/tasks.json" && cp "$T/tasks.json" "$wt/docs/plan/tasks.json"
git -C "$wt" commit -qam "chore: edit plan"
expect 65 "tasks.json differs from the approval" "$RT" demo t1 check
grep -q "approved" "$T/err" || fail "mismatch message: $(cat "$T/err")"
# --- test_check_reads_stored_approved_copy: the bytes approve-plan stored (records approvals/<p>/v<N>/) win.
stored="$RECORDS_DIR/demo/approvals/demo/v1/docs/plan"
mkdir -p "$stored" && echo '{"tampered": true}' > "$stored/tasks.json"
expect 65 "stored copy with other bytes is ignored" "$RT" demo t1 check
git -C "$src" show main:docs/plan/tasks.json > "$stored/tasks.json"
expect 0 "check from the stored approved copy" "$RT" demo t1 check
jq -e '(.output_tail | contains("checked-ok")) and (.output_tail | contains("sneaky") | not)' "$T/out" >/dev/null \
  || fail "test_check_reads_stored_approved_copy: $(cat "$T/out")"
rm -rf "$RECORDS_DIR/demo/approvals"
git -C "$wt" reset -q --hard HEAD~1
approve 0000000000000000000000000000000000000000000000000000000000000000
expect 65 "approval hash differs" "$RT" demo t1 check
rm -f "$STATE_DIR/approvals/demo.json"
expect 65 "no approval" "$RT" demo t1 check
approve
# --- test_check_runs_in_bwrap: with bwrap present the check runs inside it: root read-only, writable only the
# checkout and its tmp dir, the clone's .git read-only, the worktree's dependency dirs read-only, network
# through the egress proxy (nft confines the engineer uid), credential stores hidden, not the whole HOME.
# The stub bwrap logs its argv, links each empty --ro-bind target to its source, then runs the command.
stub "$R" bwrap 'while [ "$1" != -- ]; do
  if [ "$1" = --ro-bind ] && [ -d "$3" ] && [ -z "$(ls -A "$3")" ]; then rmdir "$3" && ln -s "$2" "$3"; fi; shift
done; shift; exec "$@"'
mkdir -p "$CHROME_PROFILE"
home=$(getent passwd "$(id -u)" | cut -d: -f6)
expect 0 "check t1 in bwrap" "$RT" demo t1 check
line=$(grep '^bwrap ' "$T/argv.log" | tail -n 1 || true)
for want in "--unshare-all --share-net" "--die-with-parent" "--ro-bind / /" "--tmpfs /tmp" "--chdir /" \
  "--ro-bind $src/.git $src/.git" "--tmpfs $CHROME_PROFILE" "-- bash -c test -f README.md"; do
  case "$line" in *"$want"*) ;; *) fail "bwrap argv lacks '$want': $line" ;; esac
done
co=$(sed -E 's/.*--chdir ([^ ]+) .*/\1/' <<< "$line")
case "$line" in *"--bind $co $co"*) ;; *) fail "bwrap does not bind the checkout read-write: $line" ;; esac
case "$line" in *"--ro-bind $wt/node_modules $co/node_modules"*) ;; *) fail "node_modules not bound read-only: $line" ;; esac
case "$line" in *"$co/.venv"*|*"$T/outside"*) fail "a symlinked dependency dir is bound: $line" ;; esac
case "$line" in *"--tmpfs $home "*) fail "bwrap hides the whole HOME: $line" ;; esac
for d in .claude .ssh .config/gh .engineer; do
  [ -d "$home/$d" ] || continue
  case "$line" in *"--tmpfs $home/$d "*) ;; *) fail "bwrap does not hide ~/$d: $line" ;; esac
done
jq -e '(.output_tail | contains("bwrap not found") | not) and .exit_code == 0 and (.output_tail | contains("checked-ok"))' \
  "$T/out" >/dev/null || fail "bwrap run: $(cat "$T/out")"
expect 0 "check t1 in bwrap, proxy env" "$RT" demo t1 check --dry-run
jq -e --arg p "http://127.0.0.1:$PROXY_PORT" '.env.HTTPS_PROXY == $p and .env.https_proxy == $p and .env.HTTP_PROXY == $p
  and (.env.NO_PROXY | contains("127.0.0.1"))' "$T/out" >/dev/null || fail "check env lacks the proxy: $(jq -c .env "$T/out")"
expect 0 "dry-run check shows bwrap" "$RT" demo t1 check --dry-run
jq -e '.argv | index("bwrap") != null' "$T/out" >/dev/null 2>&1 || jq -e '[.argv[] | test("bwrap$")] | any' "$T/out" >/dev/null \
  || fail "dry-run check argv: $(cat "$T/out")"
rm -f "$R/bin/bwrap"

# A scratch project runs without LOCKED.
rm -f "$R/LOCKED"
new_clone "$PROJECTS_DIR/quiet"
mkdir -p "$PROJECTS_DIR/quiet/docs/plan" && cp "$src/docs/plan/tasks.json" "$PROJECTS_DIR/quiet/docs/plan/"
expect 0 "scratch=yes without LOCKED" "$RT" quiet t1 implementer --dry-run
touch "$R/LOCKED"

# --- test_run_task_fetches_from_mirror: a new task branches from the broker mirror's default branch
# (newer than the engineer's clone), fetched over file:// with repo hooks off; the mirror belongs to another user.
m="$STATE_DIR/mirrors/demo.git"
git clone -q --bare "$src" "$m"
git clone -q "$m" "$T/upstream" && echo newer > "$T/upstream/newer.txt"
git -C "$T/upstream" add newer.txt && git -C "$T/upstream" commit -qm "feat: newer" && git -C "$T/upstream" push -q origin main
up=$(git --git-dir="$m" rev-parse main)
[ "$up" != "$(git -C "$src" rev-parse main)" ] || fail "fixture: mirror is not ahead of the clone"
chown -R nobody "$m"
jq '.tasks += [.tasks[0] | .id = "t3"]' "$src/docs/plan/tasks.json" > "$T/tasks.json" && cp "$T/tasks.json" "$src/docs/plan/tasks.json"
for h in reference-transaction post-checkout; do printf '#!/bin/sh\ntouch %s/hooked\n' "$T" > "$src/.git/hooks/$h"; chmod 755 "$src/.git/hooks/$h"; done
expect 0 "implementer run from the mirror" "$RT" demo t3 implementer
res=$(validate "$T/out") || fail "mirror run-result invalid: $(cat "$T/out")"
[ "$(git -C "$PROJECTS_DIR/demo.wt/t3" rev-parse HEAD)" = "$up" ] || fail "test_run_task_fetches_from_mirror: t3 not branched from the mirror"
# test_first_attempt_without_commits_is_no_diff (run-task side): a new branch with no commit has head == base.
echo "$res" | jq -e --arg u "$up" '.base_sha == $u and .head_sha == $u' >/dev/null || fail "base_sha is not the mirror head: $res"
[ -e "$T/hooked" ] && fail "a repo hook ran during the mirror fetch or worktree add"
[ "$(git -C "$src" rev-parse main)" != "$up" ] || fail "run-task moved the clone's main"
rm -rf "$m" && mkdir -p "$m" && echo garbage > "$m/HEAD"
jq '.tasks += [.tasks[0] | .id = "t4"]' "$src/docs/plan/tasks.json" > "$T/tasks.json" && cp "$T/tasks.json" "$src/docs/plan/tasks.json"
expect 65 "broken mirror" "$RT" demo t4 implementer
exit 0
