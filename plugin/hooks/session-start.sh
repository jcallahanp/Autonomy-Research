#!/bin/bash
# SessionStart hook (startup, resume, clear, compact): inject the research-agent skill index,
# the first 60 lines of the active run's PLAN.md (the newest research/runs/*/PLAN.md whose
# ## Outputs section still says pending or running), and the newest 30 lines of
# research/findings/INDEX.md, as additionalContext. Needs no jq. Always exits 0.
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"
plugin_root="${CLAUDE_PLUGIN_ROOT:-$(dirname "$here")}"
project="${CLAUDE_PROJECT_DIR:-$(dirname "$plugin_root")}"

# Skill index: the body of using-research-agent/SKILL.md (frontmatter stripped).
ctx=$(awk 'c >= 2; /^---$/ { c++ }' "$plugin_root/skills/using-research-agent/SKILL.md" 2>/dev/null)
[ -n "$ctx" ] || ctx="research-agent skills: using-research-agent (index), research, tool-scan, repo-triage, setup, interview, system-map, spike, self-test, self-improve."
ctx="research-agent is loaded. Skill index (using-research-agent):
$ctx"

# Active run: newest PLAN.md (by modification time) with pending or running under ## Outputs.
active=""
while IFS= read -r p; do
  [ -f "$p" ] || continue
  if awk '/^## / { o = ($0 ~ /^## Outputs/); next } o && /pending|running/ { f = 1; exit } END { exit !f }' "$p" 2>/dev/null; then
    active=$p; break
  fi
done < <(ls -t "$project"/research/runs/*/PLAN.md 2>/dev/null)
if [ -n "$active" ]; then
  rel=${active#"$project"/}
  ctx="$ctx

Active research run ($rel, first 60 lines). Re-read it before acting; trust it over memory:
$(head -n 60 "$active" 2>/dev/null)"
fi

index=$(tail -n 30 "$project/research/findings/INDEX.md" 2>/dev/null)
[ -z "$index" ] || ctx="$ctx

Findings so far (research/findings/INDEX.md, newest 30 lines):
$index"

if command -v jq >/dev/null 2>&1; then
  jq -n --arg c "$ctx" '{hookSpecificOutput: {hookEventName: "SessionStart", additionalContext: $c}}'
else
  printf '%s\n' "$ctx"  # plain stdout also reaches the session context
fi
exit 0
