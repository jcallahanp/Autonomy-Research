#!/bin/bash
# Vendored Superpowers subset: manifest checks and covers every vendored file plus the licence; licence is MIT.
set -euo pipefail
. "$(dirname "$0")/../lib.sh"

p=engineer/plugin
vendored=(brainstorming writing-plans subagent-driven-development executing-plans
          verification-before-completion using-git-worktrees using-superpowers)

[ -f "$p/superpowers.sha256" ] || { fail "$p/superpowers.sha256 missing"; exit 1; }
(cd "$p" && sha256sum --quiet -c superpowers.sha256) || fail "sha256sum -c superpowers.sha256"

listed=$(awk '{sub(/^\*/, "", $2); print $2}' "$p/superpowers.sha256" | sort)
actual=$(cd "$p" && { for d in "${vendored[@]}"; do find "skills/$d" -type f; done; echo LICENSE-superpowers; } | sort)
[ "$listed" = "$actual" ] || fail "manifest does not list exactly the vendored files"
! grep -q '^[^ ]*  /' "$p/superpowers.sha256" || fail "manifest has absolute paths"

grep -q 'MIT' "$p/LICENSE-superpowers" 2>/dev/null || fail "LICENSE-superpowers does not say MIT"
grep -q 'Jesse Vincent' "$p/LICENSE-superpowers" 2>/dev/null || fail "LICENSE-superpowers lost the copyright line"

# Unchanged from the pinned source when that clone is on this machine.
src=/home/user/attio-project/.claude/skills
if [ -d "$src" ]; then
  for d in "${vendored[@]}"; do
    diff -r "$src/$d" "$p/skills/$d" >/dev/null || fail "skills/$d differs from $src/$d"
  done
  cmp -s "$src/LICENSE-superpowers" "$p/LICENSE-superpowers" || fail "LICENSE-superpowers differs from source"
fi
