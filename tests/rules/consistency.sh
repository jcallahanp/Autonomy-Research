# Self-improvement round 1, change 6: contradictions the plugin's own research run found in it.
# Sourced by tests/check.sh (provides fail, fm). Offline: reads files only.

# routing.md agrees with researcher.md: no Parallel full content, no fallback no agent can run.
grep -qiE 'full.content' plugin/skills/research/routing.md \
  && fail consistency "routing.md still offers Parallel full content (researcher.md forbids it)"

# Registry rows: one owner per context. Spike rows: the synthesizer in Spike mode. Triage and
# tool-scan rows: the lead, from ROW lines. Inside a spike the lead writes no row.
s=plugin/skills/spike/SKILL.md
sf=$(tr '\n' ' ' < "$s" | tr -s ' ')
echo "$sf" | grep -qiF 'lead writes no registry row' || fail consistency "spike SKILL.md does not say the lead writes no registry row in a spike"
echo "$sf" | grep -qiF 'only writer of spike rows' || fail consistency "spike SKILL.md does not name the synthesizer as the only writer of spike rows"
grep -qiE 'inside a .?spike' plugin/skills/repo-triage/SKILL.md || fail consistency "repo-triage does not say who writes the row when it runs inside a spike"
grep -qiE 'triage .?ROW:.? line' plugin/agents/synthesizer.md || fail consistency "synthesizer Spike mode does not take the triage ROW: line from PLAN.md"

# Findings files have "Open questions", not "Gaps" (findings-format.md section 6).
grep -qE 'list (it|them) under Gaps' plugin/agents/synthesizer.md plugin/skills/research/SKILL.md \
  && fail consistency "synthesizer/research still send excluded claims to 'Gaps' (findings-format says Open questions)"
tr '\n' ' ' < plugin/skills/research/SKILL.md | tr -s ' ' | grep -qE 'Contradictions and Gaps|the open Gaps' \
  && fail consistency "research SKILL.md reply step still says 'Gaps' for the findings file's Open questions"
grep -qF 'stay gaps' plugin/agents/synthesizer.md \
  && fail consistency "synthesizer.md rule 2 still says note gaps 'stay gaps' instead of naming Open questions"
