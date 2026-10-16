#!/bin/bash
# SessionStart hook: inject the research-agent skill index and the first 30 lines of
# research/findings/INDEX.md (if present) as additionalContext. Always exits 0.
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"
plugin_root="${CLAUDE_PLUGIN_ROOT:-$(dirname "$here")}"
project="${CLAUDE_PROJECT_DIR:-$(dirname "$plugin_root")}"

# Skill index: the body of using-research-agent/SKILL.md (frontmatter stripped).
ctx=$(awk 'c >= 2; /^---$/ { c++ }' "$plugin_root/skills/using-research-agent/SKILL.md" 2>/dev/null)
[ -n "$ctx" ] || ctx="research-agent skills: using-research-agent (index), research, tool-scan, repo-triage, setup, interview, system-map, spike, self-test."
ctx="research-agent is loaded. Skill index (using-research-agent):
$ctx"

index=$(head -n 30 "$project/research/findings/INDEX.md" 2>/dev/null)
[ -z "$index" ] || ctx="$ctx

Findings so far (research/findings/INDEX.md, first 30 lines):
$index"

if command -v jq >/dev/null 2>&1; then
  jq -n --arg c "$ctx" '{hookSpecificOutput: {hookEventName: "SessionStart", additionalContext: $c}}'
else
  printf '%s\n' "$ctx"  # plain stdout also reaches the session context
fi
exit 0
