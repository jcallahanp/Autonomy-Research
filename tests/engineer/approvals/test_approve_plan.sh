#!/bin/bash
# approve-plan: checks the plan files the supervisor stored from the plan PR's head commit against the hashes
# in the ask John answered, sets scope_version to the plan version, commits and tags the records clone, and
# pushes through AGENT_RUN push-branch (stubbed). The engineer's working tree never counts.
set -euo pipefail
. "$(dirname "$0")/../lib.sh"

root=$(mk_root "$T")
stub "$root" agent-run 'exit 0'
state="$T/var/lib/engineer"
proj="$T/home/engineer/projects/demo"
rec="$T/var/lib/engineer/records/demo"
mkdir -p "$proj/docs/plan" "$T/etc/engineer"
printf 'demo owner/demo main self_merge=on scratch=no owner_login=octo\n' > "$T/etc/engineer/projects.txt"
git init -q -b engineer-records "$rec"
gc() { git -C "$rec" -c user.name=t -c user.email=t@example.invalid "$@"; }
gc commit -q --allow-empty -m init
mapfile -t SIGNED < <(python3 -c 'import sys; sys.path.insert(0, sys.argv[1]); from eng import approval
print("\n".join(approval.SIGNED))' "$root/scripts")

ap() { "$root/bin/approve-plan" "$@"; }
# store V [GATES]: the supervisor's snapshot of plan vV (approvals/demo/vV/...), committed on engineer-records.
store() {
  local d="$rec/approvals/demo/v$1" f
  for f in "${SIGNED[@]}"; do mkdir -p "$(dirname "$d/$f")"; echo "plan v$1 $f" > "$d/$f"; done
  printf 'self_merge: true\nhard_gates: %s\n' "${2:-[money, delete_data]}" > "$d/docs/plan/profile.yaml"
  git -C "$rec" add approvals && gc commit -qm "records: plan v$1"
}
# plan_ask N V [no-files]: the plan ask for vV with the hashes of the stored files as John saw them.
plan_ask() {
  python3 - "$state/demo/events.jsonl" "$rec" "$1" "$2" "${3:-}" "${SIGNED[@]}" <<'PY'
import hashlib, json, os, sys
ev, rec, n, v, mode, *signed = sys.argv[1:]
base = f"approvals/demo/v{v}"
files = {} if mode == "no-files" else {
    f: hashlib.sha256(open(f"{rec}/{base}/{f}", "rb").read()).hexdigest() for f in signed}
os.makedirs(os.path.dirname(ev), exist_ok=True)
open(ev, "a").write(json.dumps({"ts": "2026-10-16T07:00:00Z", "project": "demo", "event": "approval_ask",
    "task_id": None, "detail": {"item": int(n), "tier": "T1", "kind": "plan", "text": f"Approve plan v{v} @ 1234567?",
    "default": "n", "reversible": False, "ref": None, "version": int(v), "pr": 3, "sha": "1234567" * 5 + "89abc",
    "snapshot": base, "files": files}}) + "\n")
PY
}
# said_yes N: John's yes for item N in the records clone's approvals.jsonl.
said_yes() {
  mkdir -p "$rec/decisions"
  printf '{"ts": "2026-10-16T08:00:00Z", "item": "%s", "tier": "T1", "kind": "plan", "ask": "a", "answer": "yes", "source": "telegram"}\n' "$1" \
    >> "$rec/decisions/approvals.jsonl"
  git -C "$rec" add decisions && gc commit -qm records
}
refused() {  # refused DESC ARGS...: approve-plan must exit 65
  local desc=$1 rc=0; shift
  ap "$@" 2>"$T/err" >/dev/null || rc=$?
  [ "$rc" -eq 65 ] || fail "$desc: rc=$rc ($(cat "$T/err"))"
}

# --- test_working_tree_differs_from_pr_head_no_effect: the working tree holds other bytes; the stored ones count.
for f in "${SIGNED[@]}"; do mkdir -p "$(dirname "$proj/$f")"; echo "engineer's unpushed edit" > "$proj/$f"; done
store 1; plan_ask 1 1; said_yes 1
ap demo --record-id tg-10 --item 1 --by John --source telegram >/dev/null 2>"$T/err" || fail "v1 failed: $(cat "$T/err")"
j="$state/approvals/demo.json"
python3 - "$j" "$root" "$rec/approvals/demo/v1" <<'PY' || fail "approval file wrong (v1)"
import json, sys
sys.path.insert(0, sys.argv[2] + "/scripts")
from eng import approval, schema
a = json.load(open(sys.argv[1]))
assert schema.validate(a, schema.load(sys.argv[2], "approval")) == [], a
assert a["files"] == approval.hashes(sys.argv[3]) and len(a["files"]) == len(approval.SIGNED), a
assert a["scope_version"] == 1 and a["gates"] == ["money", "delete_data"], a
assert a["source"] == "telegram" and a["record_id"] == "tg-10", a
PY
cmp -s "$j" "$rec/docs/plan/approval.json" || fail "records copy differs from the state file"
git -C "$rec" rev-parse -q --verify refs/tags/plan-approved-1 >/dev/null || fail "no tag plan-approved-1"
[ "$(git -C "$rec" log -1 --format=%an)" = engineer-bot ] || fail "commit not by engineer-bot"
[ -z "$(git -C "$rec" status --porcelain)" ] || fail "records clone left dirty"
grep -qx "agent-run push-branch $rec engineer-records --tag plan-approved-1" "$T/argv.log" \
  || fail "push-branch not called with --tag plan-approved-1: $(cat "$T/argv.log")"

# --- v3 approved from a PR review: scope_version is the plan version, not previous + 1.
store 3; plan_ask 2 3
ap demo --record-id pr-3 --item 2 --by John --source pr >/dev/null || fail "v3 run failed"
python3 -c 'import json,sys; a=json.load(open(sys.argv[1])); assert a["scope_version"]==3 and a["source"]=="pr", a' "$j" \
  || fail "scope_version not 3"
grep -q -- "--tag plan-approved-3" "$T/argv.log" || fail "v3 push not tagged plan-approved-3"

# Refusals: nothing written, exit 65.
before=$(cat "$j")
plan_ask 3 3; refused "test_same_version_twice_refused" demo --record-id x --item 3 --by John --source pr
grep -q 'not newer' "$T/err" || fail "same version: $(cat "$T/err")"
store 2; plan_ask 4 2; refused "test_older_version_refused" demo --record-id x --item 4 --by John --source pr
# test_approve_plan_refuses_changed_file: a stored file changed after John was asked.
store 4; plan_ask 5 4; said_yes 5
echo "edit after the ask" >> "$rec/approvals/demo/v4/docs/plan/requirements.md"
gc commit -qam "records: tamper"
refused "test_approve_plan_refuses_changed_file" demo --record-id tg-11 --item 5 --by John --source telegram
grep -q 'requirements.md' "$T/err" || fail "refusal does not name the changed file: $(cat "$T/err")"
store 5; plan_ask 6 5 no-files; said_yes 6
refused "ask without hashes" demo --record-id tg-12 --item 6 --by John --source telegram
store 6; plan_ask 7 6; refused "no yes record" demo --record-id tg-13 --item 7 --by John --source telegram
refused "unknown item" demo --record-id tg-14 --item 99 --by John --source pr
rc=0; ap demo --record-id tg-15 --by John --source pr 2>/dev/null || rc=$?; [ "$rc" -ne 0 ] || fail "missing --item accepted"
store 7 '[]'; plan_ask 8 7; refused "test_empty_hard_gates_refused" demo --record-id x --item 8 --by John --source pr
grep -q 'hard_gates is empty' "$T/err" || fail "empty gates: $(cat "$T/err")"
store 8; plan_ask 9 8
refused "bad name" Bad_Name --record-id x --item 9 --by John --source pr
refused "unlisted project" other --record-id x --item 9 --by John --source pr
refused "bad source" demo --record-id x --item 9 --by John --source email
refused "bad record id" demo --record-id 'x;y' --item 9 --by John --source pr
echo "uncommitted" >> "$rec/approvals/demo/v8/docs/plan/brief.md"
refused "uncommitted snapshot" demo --record-id x --item 9 --by John --source pr
git -C "$rec" checkout -q -- approvals
mv "$rec/approvals/demo/v8/docs/plan/requirements.md" "$T/req.md"
ln -s "$T/req.md" "$rec/approvals/demo/v8/docs/plan/requirements.md"
gc commit -qam "records: symlink"
refused "symlinked stored file" demo --record-id x --item 9 --by John --source pr
git -C "$rec" rm -q approvals/demo/v8/docs/plan/requirements.md && gc commit -qm "records: missing"
refused "missing stored file" demo --record-id x --item 9 --by John --source pr
[ "$before" = "$(cat "$j")" ] || fail "a refused run changed the approval"

# A failed push is reported.
store 9; plan_ask 10 9
stub "$root" agent-run 'exit 9'
rc=0; ap demo --record-id x --item 10 --by John --source pr >/dev/null 2>&1 || rc=$?; [ "$rc" -eq 1 ] || fail "push failure rc=$rc"
exit 0
