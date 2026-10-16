#!/bin/bash
# pr-head PROJECT PR: the supervisor reads a PR's head commit (the plan PR John is asked to approve).
set -euo pipefail
. "$(dirname "$0")/../lib.sh"
. "$REPO/tests/engineer/broker/helpers.sh"

HEAD=1111111111111111111111111111111111111111
stub "$R" gh "[ \"\${GH_TOKEN:-}\" = TEST-TOKEN-PAT ] || exit 9
case \"\$1 \$2\" in
  'pr view') cat '$T/view.json' ;;
  *) exit 5 ;;
esac"
view() {  # view HEAD STATE
  jq -n --arg h "$1" --arg s "$2" '{number: 3, state: $s, headRefOid: $h, headRefName: "plan/v1",
    baseRefName: "main", url: "https://github.com/owner/demo/pull/3"}' > "$T/view.json"
}
run() { SUDO_USER=supervisor "$R/bin/agent-run" pr-head "$@"; }

# --- test_pr_head_prints_head_sha
view "$HEAD" OPEN
expect 0 "pr-head" run demo 3
jq -e --arg h "$HEAD" '.number == 3 and .head_sha == $h and .state == "OPEN" and .base == "main"
  and .head == "plan/v1" and .url == "https://github.com/owner/demo/pull/3"' "$T/out" >/dev/null \
  || fail "pr-head output: $(cat "$T/out")"
grep -q '^gh pr view 3 --repo owner/demo --json number,state,headRefOid,headRefName,baseRefName,url' "$T/argv.log" \
  || fail "gh call: $(cat "$T/argv.log")"
grep -q TEST-TOKEN-PAT "$T/argv.log" "$T/out" "$T/err" && fail "token leaked"

# --- test_pr_head_refusals
view "not-a-sha" OPEN
expect 1 "bad head from gh" run demo 3
expect 77 "engineer may not read pr-head" as engineer pr-head demo 3
expect 65 "PR not a number" run demo 3x
expect 65 "unlisted project" run stranger 3
expect 64 "usage" run demo
exit 0
