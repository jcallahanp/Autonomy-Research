# Self-improvement round 1, changes 1-3: the verifier can open what researchers cite, a verbatim
# quote travels with every claim from note to findings, and repo path:line citations are legal.
# Sourced by tests/check.sh (provides fail, fm). Offline: reads files only.

v=plugin/agents/verifier.md
r=plugin/agents/researcher.md
sy=plugin/agents/synthesizer.md
ns=plugin/skills/research/note-schema.md
ff=plugin/skills/research/findings-format.md
tools_of() { fm "$1" tools | tr ',' '\n' | sed 's/^[ \t]*//; s/[ \t]*$//'; }

# Change 1: the verifier has Firecrawl (both the plugin and the template server names), reads
# repo citations, caps its sample at 20 by risk, and counts an uncertain judgment as unverified.
if [ -f "$v" ]; then
  for t in mcp__plugin_research-agent_firecrawl__firecrawl_scrape mcp__firecrawl__firecrawl_scrape Read; do
    tools_of "$v" | grep -qx "$t" || fail citations "verifier tools lack $t"
  done
  grep -qF 'path:line' "$v" || fail citations "verifier.md does not say how to check repo path:line citations"
  grep -qiF 'never more than 20' "$v" || fail citations "verifier.md does not cap the sample at 20"
  grep -qiE 'include every (claim|number)' "$v" && fail citations "verifier.md still requires every summary claim and number (can exceed 20)"
  grep -qiE 'numbers.{0,80}quotes.{0,80}single.source' "$v" || fail citations "verifier.md does not pick the sample by risk (numbers, quotes, single-source first)"
  grep -qi 'uncertain' "$v" || fail citations "verifier.md does not count an uncertain judgment as unverified"
  grep -qi 'uncertain' "$ff" || fail citations "findings-format.md section 7 lacks the 'uncertain' reason"
  # Review I1: the verifier only appends and edits; Write could truncate INDEX.md or the findings.
  tools_of "$v" | grep -qx Write && fail citations "verifier has Write (it should only Edit; the lead creates INDEX.md)"
  tr '\n' ' ' < plugin/skills/research/SKILL.md | tr -s ' ' | grep -qF 'If it does not exist, create it holding `# Findings index`' \
    || fail citations "research SKILL.md does not have the lead create INDEX.md before the verifier edits it"
else fail citations "missing $v"; fi

# Change 2: Quote field in the note, carried by the synthesizer into the findings Evidence.
grep -qE '^- <claim> — .*Quote: "' "$ns" || fail citations "note-schema.md Cited findings template line lacks Quote: \"...\""
grep -qF '30 words' "$ns" || fail citations "note-schema.md does not cap a quote at 30 words"
grep -qF 'Quote:' "$r" || fail citations "researcher.md does not ask for a Quote: on every cited finding"
grep -qF 'Quote:' "$sy" || fail citations "synthesizer.md does not carry the Quote: field"
grep -qiF 'not backed by a cited line' "$sy" || fail citations "synthesizer.md lacks the no-unbacked-information rule"
grep -qF 'Quote:' "$ff" || fail citations "findings-format.md Evidence bullet lacks Quote:"

# Change 3: repo path:line citations are opened sources; the synthesizer keeps them.
for f in "$ns" "$r" "$sy"; do
  grep -qF 'path:line' "$f" || fail citations "$f does not accept repo path:line citations"
done
grep -qF 'with no URL' "$sy" && fail citations "synthesizer.md still drops every claim with no URL (repo citations included)"

# Round 1 re-measure fix: summary and answer lines cite inline, and an unquoted qualifier is
# labelled as a worker inference instead of borrowing the claim's URL (contradiction case dip).
grep -q 'inline, not only an Evidence number' "$sy" || fail citations "$sy: summary and answers must cite URLs inline"
grep -q 'Worker inference (not' "$sy" || fail citations "$sy: unquoted qualifiers must be labelled as worker inference"
grep -q 'inline, the URL or `path:line`' "$ff" || fail citations "$ff: answers must cite inline"
