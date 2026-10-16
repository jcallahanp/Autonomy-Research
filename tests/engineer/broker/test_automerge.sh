#!/bin/bash
# automerge PROJECT PR: tier 1 auto-merges; tier 2 only on John's APPROVED review of the head commit.
set -euo pipefail
. "$(dirname "$0")/../lib.sh"
. "$REPO/tests/engineer/broker/helpers.sh"

HEAD=1111111111111111111111111111111111111111
OLD=2222222222222222222222222222222222222222
mkdir -p "$R/scripts/checks"
cat > "$R/scripts/checks/merge-tier.py" <<EOF
import json, sys
open("$T/tier-in.json", "w").write(sys.stdin.read())
sys.stdout.write(open("$T/tier.json").read())
EOF
stub "$R" gh "[ \"\${GH_TOKEN:-}\" = TEST-TOKEN-PAT ] || exit 9
case \"\$1 \$2\" in
  'pr view') cat '$T/view.json' ;;
  'pr merge') echo merged ;;
  *) exit 5 ;;
esac"

view() {  # view REVIEWS_JSON
  jq -n --arg h "$HEAD" --argjson r "$1" '{title: "feat: t1", headRefOid: $h, reviews: $r,
    files: [{path: "src/a.py", additions: 3, deletions: 1, extra: true}]}' > "$T/view.json"
}
merges() { grep -c '^gh pr merge' "$T/argv.log" || true; }
run() { SUDO_USER=supervisor "$R/bin/agent-run" automerge "$@"; }

# Tier 1.
view '[]'
echo '{"tier": 1, "reasons": []}' > "$T/tier.json"
expect 0 "tier 1" run demo 7
jq -e '.tier == 1 and .auto_merge == true' "$T/out" >/dev/null || fail "tier 1 output: $(cat "$T/out")"
grep -q "^gh pr merge 7 --auto --squash --repo owner/demo --match-head-commit $HEAD" "$T/argv.log" \
  || fail "merge call: $(grep '^gh pr merge' "$T/argv.log")"
grep -q '^gh pr view 7 --repo owner/demo --json title,files,reviews,headRefOid' "$T/argv.log" || fail "view call"
jq -e '.title == "feat: t1" and .files == [{"path": "src/a.py", "additions": 3, "deletions": 1}]' "$T/tier-in.json" \
  >/dev/null || fail "merge-tier input: $(cat "$T/tier-in.json")"

# Tier 2 without a review: no merge, exit 3, reasons passed on.
echo '{"tier": 2, "reasons": ["path auth/** is tier 2"]}' > "$T/tier.json"
n=$(merges)
expect 3 "tier 2 without review" run demo 7
jq -e '.tier == 2 and .auto_merge == false and .reasons == ["path auth/** is tier 2"]' "$T/out" >/dev/null \
  || fail "tier 2 output: $(cat "$T/out")"
[ "$(merges)" -eq "$n" ] || fail "merged a tier 2 PR without review"

rev() { jq -n --arg l "$1" --arg s "$2" --arg c "$3" '{author: {login: $l}, state: $s, commit: {oid: $c}}'; }
view "[$(rev someone-else APPROVED "$HEAD")]"
expect 3 "tier 2 approved by someone else" run demo 7
view "[$(rev example-owner APPROVED "$OLD")]"
expect 3 "tier 2 approved on an older commit" run demo 7
view "[$(rev example-owner APPROVED "$HEAD"), $(rev example-owner CHANGES_REQUESTED "$HEAD")]"
expect 3 "tier 2 approval then changes requested" run demo 7
[ "$(merges)" -eq "$n" ] || fail "merged a tier 2 PR without a valid review"

view "[$(rev example-owner COMMENTED "$HEAD"), $(rev example-owner APPROVED "$HEAD")]"
expect 0 "tier 2 approved by the owner on head" run demo 7
jq -e '.tier == 2 and .auto_merge == true' "$T/out" >/dev/null || fail "tier 2 approved output: $(cat "$T/out")"
[ "$(merges)" -eq $((n + 1)) ] || fail "tier 2 approved PR not merged"

# self_merge=off, bad PR numbers, wrong caller.
n=$(merges)
echo '{"tier": 1, "reasons": []}' > "$T/tier.json"
expect 3 "self_merge=off" run quiet 7
jq -e '.auto_merge == false' "$T/out" >/dev/null || fail "self_merge=off output: $(cat "$T/out")"
expect 65 "PR not a number" run demo 7x
expect 65 "unknown project" run nope 7
expect 77 "engineer calls automerge" as engineer automerge demo 7
[ "$(merges)" -eq "$n" ] || fail "merged on a refused request"

# A failed or unreadable merge-tier answer counts as Tier 2 and never merges, even with an approval.
view "[$(rev example-owner APPROVED "$HEAD")]"
for bad in garbage notier tier3 exit2; do
  case $bad in
    garbage) echo 'not json' > "$T/tier.json" ;;
    exit2) echo '{"tier": 1, "reasons": []}' > "$T/tier.json"
      printf 'import sys\nprint("{\\"tier\\": 1}")\nsys.exit(2)\n' > "$R/scripts/checks/merge-tier.py" ;;
    notier) echo '{"reasons": []}' > "$T/tier.json" ;;
    tier3) echo '{"tier": 3, "reasons": []}' > "$T/tier.json" ;;
  esac
  expect 3 "merge-tier $bad" run demo 7
  jq -e '.tier == 2 and .auto_merge == false and (.reasons | length > 0)' "$T/out" >/dev/null \
    || fail "merge-tier $bad output: $(cat "$T/out")"
done
[ "$(merges)" -eq "$n" ] || fail "merged on a bad tier answer"
grep -q TEST-TOKEN-PAT "$T/argv.log" && fail "token in argv"
exit 0
