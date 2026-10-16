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
echo '{\"type\":\"result\",\"subtype\":\"success\",\"is_error\":false,\"num_turns\":3,\"session_id\":\"$SID\",\"total_cost_usd\":0.42,\"permission_denials\":[{\"tool_name\":\"Bash\"}]}'"

src="$PROJECTS_DIR/demo"
new_clone "$src"
mkdir -p "$src/docs/plan"
jq -n '{version: 1, tasks: [
  {id: "t1", title: "T one", type: "feat", status: "ready", depends_on: [], requirement_ids: [], files: [],
   check: "test -f README.md && echo checked-ok", passes: false, attempts: 0},
  {id: "t2", title: "T two", type: "fix", status: "ready", depends_on: [], requirement_ids: [], files: [],
   check: "echo failing-check; exit 3", passes: false, attempts: 0}]}' > "$src/docs/plan/tasks.json"
git -C "$src" add docs && git -C "$src" commit -qm "docs: plan"
wt="$PROJECTS_DIR/demo.wt/t1"
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
expect 0 "second run reuses the worktree" "$RT" demo t1 implementer

# check profile: runs the task check in the worktree.
expect 0 "check t1" "$RT" demo t1 check
res=$(validate "$T/out") || fail "check run-result invalid: $(cat "$T/out")"
echo "$res" | jq -e '.profile == "check" and .exit_code == 0 and .is_error == false and (.output_tail | contains("checked-ok"))' \
  >/dev/null || fail "check result: $res"
expect 0 "check t2 (failing check still prints a result)" "$RT" demo t2 check
echo "$(cat "$T/out")" | jq -e '.exit_code == 3 and .is_error == true and (.output_tail | contains("failing-check"))' >/dev/null \
  || fail "failing check result: $(cat "$T/out")"
[ "$(git -C "$PROJECTS_DIR/demo.wt/t2" rev-parse --abbrev-ref HEAD)" = task/t2 ] || fail "t2 worktree branch"

# A scratch project runs without LOCKED.
rm -f "$R/LOCKED"
new_clone "$PROJECTS_DIR/quiet"
mkdir -p "$PROJECTS_DIR/quiet/docs/plan" && cp "$src/docs/plan/tasks.json" "$PROJECTS_DIR/quiet/docs/plan/"
expect 0 "scratch=yes without LOCKED" "$RT" quiet t1 implementer --dry-run
exit 0
