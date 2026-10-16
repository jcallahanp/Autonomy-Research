#!/bin/bash
set -euo pipefail
# Task 1: the blueprint, diagrams and ADRs carry John's six decisions (2026-10-16).
# Runs standalone (bash tests/engineer/blueprint/test_blueprint.sh) or under tests/engineer/run.sh.
cd "$(dirname "$(readlink -f "$0")")/../../.."
fails=0
fail() { echo "FAIL blueprint: $*"; fails=$((fails+1)); }

bp=research/blueprint
m="updated 2026-10-16, John's decision"
p="updated 2026-10-16, stage-1 plan"
for f in README decisions setup stack repo-composition flow spikes open-questions requirements-trace; do
  grep -qF "$m" "$bp/$f.md" || fail "$f.md lacks marker"; done
for f in setup repo-composition; do grep -qF "$p" "$bp/$f.md" || fail "$f.md lacks stage-1 plan marker"; done
grep -q '^## Decisions John made' $bp/README.md || fail "README still lists decisions John owes"
! grep -q '^| Shadow mode' $bp/README.md || fail "Shadow mode still in glossary"
grep -q 'Server mode' $bp/README.md || fail "Server mode not in glossary"
! grep -q 'Path B only' $bp/setup.md || fail "Path B row still in setup.md"
! grep -q '^| `ANTHROPIC_API_KEY`' $bp/setup.md || fail "API-key verify row still in setup.md"
grep -q 'novnc\.<domain>' $bp/setup.md || fail "Cloudflare Access row missing from setup.md"
grep -q 'engineer-remote-control' $bp/setup.md || fail "Remote Control unit row missing from setup.md"
grep -q 'DigitalOcean' $bp/stack.md && grep -q '\$48' $bp/stack.md || fail "host row"
! grep -qi '1Password `op`' $bp/stack.md || fail "1Password install row"
! grep -q '| `op`' $bp/stack.md || fail "1Password op row"
grep -q 'Mac mini' $bp/stack.md && grep -q 'Tailscale' $bp/stack.md || fail "fallback rows in stack.md"
grep -q 'self_merge.*true' $bp/repo-composition.md || fail "self_merge default true"
grep -q 'approvals/<project>.json' $bp/repo-composition.md || fail "live approval path"
grep -q '`egress`' $bp/repo-composition.md || fail "egress user"
grep -q 'F41' $bp/flow.md && grep -q 'F42' $bp/flow.md || fail "F41/F42"
for s in SP85 SP86 SP87 SP88 SP89; do grep -q "| $s " $bp/spikes.md || fail "$s missing"; done
! grep -q '^| 1 | .*Path A, Max `/login`, or Path B' $bp/README.md || fail "auth still owed"
! grep -q 'or API key' docs/diagrams/engineer-context.mmd || fail "context diagram"
grep -q 'Cloudflare Access' docs/diagrams/engineer-runtime.mmd || fail "runtime diagram"
grep -q 'Remote Control' docs/diagrams/engineer-runtime.mmd || fail "runtime diagram lacks Remote Control"
grep -qi 'self-merge' docs/diagrams/engineer-approvals.mmd || fail "approvals diagram"
for d in engineer-supervisor-loop engineer-browser-route; do
  [ -f "docs/diagrams/$d.mmd" ] || fail "$d.mmd missing"
  grep -qF "($d.mmd)" docs/diagrams/index.md || fail "$d not indexed"; done
for n in 1 2 3 4 5 6; do
  a=$(ls engineer/docs/adr/000$n-*.md 2>/dev/null | head -1) || true
  if [ -z "$a" ]; then fail "ADR $n"; continue; fi
  for h in '## Context' '## Decision' '## Consequences'; do grep -qF "$h" "$a" || fail "$a lacks $h"; done
  grep -q 'Status: accepted 2026-10-16' "$a" || fail "$a lacks status"
  [ "$(wc -l < "$a")" -lt 40 ] || fail "$a is 40 lines or more"
done
MERMAID_SKIP_RENDER=1 bash tests/check-mermaid.sh >/dev/null || fail "mermaid static checks"

[ "$fails" -eq 0 ] || { echo "test_blueprint.sh: $fails failure(s)"; exit 1; }
echo "test_blueprint.sh: ok"
