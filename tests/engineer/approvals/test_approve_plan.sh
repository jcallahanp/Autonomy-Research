#!/bin/bash
# approve-plan: checks the four signed files against the hashes in the plan ask John answered, bumps
# scope_version, commits and tags the records clone, and pushes through AGENT_RUN push-branch (stubbed).
set -euo pipefail
. "$(dirname "$0")/../lib.sh"

root=$(mk_root "$T")
stub "$root" agent-run 'exit 0'
state="$T/var/lib/engineer"
proj="$T/home/engineer/projects/demo"
rec="$T/var/lib/engineer/records/demo"
mkdir -p "$proj/docs/plan" "$T/etc/engineer"
printf 'demo owner/demo main self_merge=on scratch=no owner_login=octo\n' > "$T/etc/engineer/projects.txt"
for f in brief.md requirements.md integrations.yaml; do echo "synthetic $f" > "$proj/docs/plan/$f"; done
printf 'self_merge: true\nhard_gates: [money, delete_data]\n' > "$proj/docs/plan/profile.yaml"
git init -q -b engineer-records "$rec"
git -C "$rec" -c user.name=t -c user.email=t@example.invalid commit -q --allow-empty -m init

ap() { "$root/bin/approve-plan" "$@"; }
# plan_ask N [no-files]: the supervisor's plan ask with the sha256 of each signed file as John saw it.
plan_ask() {
  python3 - "$state/demo/events.jsonl" "$proj" "$1" "${2:-}" <<'PY'
import hashlib, json, os, sys
ev, proj, n, mode = sys.argv[1:]
files = {} if mode == "no-files" else {
    f"docs/plan/{f}": hashlib.sha256(open(f"{proj}/docs/plan/{f}", "rb").read()).hexdigest()
    for f in ("brief.md", "requirements.md", "integrations.yaml", "profile.yaml")}
os.makedirs(os.path.dirname(ev), exist_ok=True)
open(ev, "a").write(json.dumps({"ts": "2026-10-16T07:00:00Z", "project": "demo", "event": "approval_ask",
    "task_id": None, "detail": {"item": int(n), "tier": "T1", "kind": "plan", "text": "Approve plan v1 for demo?",
    "default": "n", "reversible": False, "ref": None, "files": files}}) + "\n")
PY
}
# said_yes N: John's yes for item N in the records clone's approvals.jsonl.
said_yes() {
  mkdir -p "$rec/decisions"
  printf '{"ts": "2026-10-16T08:00:00Z", "item": "%s", "tier": "T1", "kind": "plan", "ask": "a", "answer": "yes", "source": "telegram"}\n' "$1" \
    >> "$rec/decisions/approvals.jsonl"
  git -C "$rec" add decisions && git -C "$rec" -c user.name=t -c user.email=t@example.invalid commit -qm records
}

plan_ask 1; said_yes 1
ap demo --record-id tg-10 --item 1 --by John --source telegram >/dev/null || fail "first approve-plan run failed"
j="$state/approvals/demo.json"
[ -f "$j" ] || fail "no approval file"
python3 - "$j" "$root" <<'PY' || fail "approval file wrong (run 1)"
import json, sys
sys.path.insert(0, sys.argv[2] + "/scripts")
from eng import schema
a = json.load(open(sys.argv[1]))
assert schema.validate(a, schema.load(sys.argv[2], "approval")) == [], a
assert len(a["files"]) == 4 and a["scope_version"] == 1, a
assert a["gates"] == ["money", "delete_data"] and a["source"] == "telegram" and a["record_id"] == "tg-10", a
PY
cmp -s "$j" "$rec/docs/plan/approval.json" || fail "records copy differs from the state file"
git -C "$rec" rev-parse -q --verify refs/tags/plan-approved-1 >/dev/null || fail "no tag plan-approved-1"
[ "$(git -C "$rec" log -1 --format=%an)" = engineer-bot ] || fail "commit not by engineer-bot"
[ -z "$(git -C "$rec" status --porcelain)" ] || fail "records clone left dirty"
grep -qx "agent-run push-branch $rec engineer-records --tag plan-approved-1" "$T/argv.log" \
  || fail "push-branch not called with --tag plan-approved-1: $(cat "$T/argv.log")"

echo "changed" >> "$proj/docs/plan/brief.md"
plan_ask 2
ap demo --record-id pr-3 --item 2 --by John --source pr >/dev/null || fail "second run failed"
python3 -c 'import json,sys; a=json.load(open(sys.argv[1])); assert a["scope_version"]==2 and a["source"]=="pr", a' "$j" \
  || fail "scope_version not bumped to 2"
grep -q -- "--tag plan-approved-2" "$T/argv.log" || fail "second push not tagged plan-approved-2"

# Refusals: nothing written, exit 65.
before=$(cat "$j")
# test_approve_plan_refuses_changed_file: John approved item 3 as he saw it; a signed file changed since.
plan_ask 3; said_yes 3
echo "engineer edit after the ask" >> "$proj/docs/plan/requirements.md"
rc=0; ap demo --record-id tg-11 --item 3 --by John --source telegram 2>"$T/err" || rc=$?
[ "$rc" -eq 65 ] || fail "test_approve_plan_refuses_changed_file: rc=$rc"
grep -q 'requirements.md' "$T/err" || fail "refusal does not name the changed file: $(cat "$T/err")"
plan_ask 4 no-files; said_yes 4
rc=0; ap demo --record-id tg-12 --item 4 --by John --source telegram 2>/dev/null || rc=$?; [ "$rc" -eq 65 ] || fail "ask without hashes rc=$rc"
plan_ask 5
rc=0; ap demo --record-id tg-13 --item 5 --by John --source telegram 2>/dev/null || rc=$?; [ "$rc" -eq 65 ] || fail "no yes record rc=$rc"
rc=0; ap demo --record-id tg-14 --item 99 --by John --source pr 2>/dev/null || rc=$?; [ "$rc" -eq 65 ] || fail "unknown item rc=$rc"
rc=0; ap demo --record-id tg-15 --by John --source pr 2>/dev/null || rc=$?; [ "$rc" -ne 0 ] || fail "missing --item accepted"
plan_ask 6
rc=0; ap Bad_Name --record-id x --item 6 --by John --source pr 2>/dev/null || rc=$?; [ "$rc" -eq 65 ] || fail "bad name rc=$rc"
rc=0; ap other --record-id x --item 6 --by John --source pr 2>/dev/null || rc=$?; [ "$rc" -eq 65 ] || fail "unlisted project rc=$rc"
rc=0; ap demo --record-id x --item 6 --by John --source email 2>/dev/null || rc=$?; [ "$rc" -eq 65 ] || fail "bad source rc=$rc"
rc=0; ap demo --record-id 'x;y' --item 6 --by John --source pr 2>/dev/null || rc=$?; [ "$rc" -eq 65 ] || fail "bad record id rc=$rc"
mv "$proj/docs/plan/requirements.md" "$T/req.md"
ln -s "$T/req.md" "$proj/docs/plan/requirements.md"
rc=0; ap demo --record-id x --item 6 --by John --source pr 2>/dev/null || rc=$?; [ "$rc" -eq 65 ] || fail "symlinked signed file rc=$rc"
rm "$proj/docs/plan/requirements.md"
rc=0; ap demo --record-id x --item 6 --by John --source pr 2>/dev/null || rc=$?; [ "$rc" -eq 65 ] || fail "missing signed file rc=$rc"
[ "$before" = "$(cat "$j")" ] || fail "a refused run changed the approval"

# A failed push is reported.
mv "$T/req.md" "$proj/docs/plan/requirements.md"
plan_ask 7
stub "$root" agent-run 'exit 9'
rc=0; ap demo --record-id x --item 7 --by John --source pr >/dev/null 2>&1 || rc=$?; [ "$rc" -ne 0 ] || fail "push failure not reported"
exit 0
