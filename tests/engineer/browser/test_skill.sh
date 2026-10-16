#!/bin/bash
# The browser skill: frontmatter, the ladder, the challenge rule, no evasion, read after write.
set -euo pipefail
. "$(dirname "$0")/../lib.sh"

f=engineer/plugin/skills/browser/SKILL.md
[ -f "$f" ] || { fail "$f missing"; exit 1; }
[ "$(head -1 "$f")" = "---" ] || fail "no frontmatter"
fm=$(awk 'NR==1{next} /^---$/{exit} {print}' "$f")
grep -qx 'name: browser' <<<"$fm" || fail "frontmatter name is not browser"
desc=$(grep '^description: ' <<<"$fm" | sed 's/^description: //')
[ -n "$desc" ] || fail "no description"
[ "${#desc}" -lt 1536 ] || fail "description ${#desc} chars"
[ "$(wc -l < "$f")" -le 300 ] || fail "over 300 lines"
for want in challenge-check.py noVNC stealth "CAPTCHA" "flows/<app>/<task>.spec.ts" precondition postcondition \
            browser-login "T1" blocked; do
  grep -qF -- "$want" "$f" || fail "skill does not mention '$want'"
done
grep -qiE 'write.{0,80}(separate|then).{0,40}read|read.{0,40}(confirm|after).{0,40}write' "$f" \
  || fail "skill lacks the read-after-write rule"
grep -qiE 'API.{0,40}(MCP)' "$f" || fail "skill lacks the API or MCP first rung"
