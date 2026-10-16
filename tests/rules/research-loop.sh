# Task 2 rules: the core research loop (research skill, three agents, note schema, INDEX).
# Sourced by tests/check.sh, which provides fail and fm.

# The three agents exist, with the models the global constraints fix.
for a in researcher synthesizer verifier; do
  [ -f "plugin/agents/$a.md" ] || fail research-loop "missing plugin/agents/$a.md"
done
want_model() { # agent model
  [ -f "plugin/agents/$1.md" ] || return
  m=$(fm "plugin/agents/$1.md" model)
  [ "$m" = "$2" ] || fail research-loop "$1 model is '$m', want $2"
}
want_model researcher sonnet
want_model synthesizer inherit
want_model verifier haiku
for a in researcher synthesizer verifier; do
  [ -f "plugin/agents/$a.md" ] || continue
  [ -z "$(fm "plugin/agents/$a.md" memory)" ] || fail research-loop "$a sets memory (auto memory is off in cloud)"
  # Deferred tools (WebFetch, MCP) need ToolSearch to load; an allowlist without it strands them.
  t=$(fm "plugin/agents/$a.md" tools)
  [ -z "$t" ] || echo "$t" | tr ',' '\n' | sed 's/^[ \t]*//; s/[ \t]*$//' | grep -qx ToolSearch \
    || fail research-loop "$a tools list lacks ToolSearch"
done

# The researcher never gets the Agent tool, and carries the return contract and safety rules.
r=plugin/agents/researcher.md
if [ -f "$r" ]; then
  [ "$(fm "$r" maxTurns)" = "40" ] || fail research-loop "researcher maxTurns is '$(fm "$r" maxTurns)', want 40"
  t=$(fm "$r" tools)
  if [ -n "$t" ]; then
    echo "$t" | tr ',' '\n' | sed 's/^[ \t]*//; s/[ \t]*$//' | grep -Eq '^(Agent|Task)(\(.*)?$' \
      && fail research-loop "researcher tools list includes the Agent tool"
  else
    echo "$(fm "$r" disallowedTools)" | tr ',' '\n' | sed 's/^[ \t]*//; s/[ \t]*$//' | grep -qx 'Agent' \
      || fail research-loop "researcher has no tools list and does not disallow Agent"
  fi
  for s in 'PATH:' 'TAKEAWAYS:' 'GAPS:' 'CONFIDENCE: high|medium|low'; do
    grep -qF "$s" "$r" || fail research-loop "researcher return contract missing '$s'"
  done
  grep -qi 'as data' "$r" || fail research-loop "researcher lacks the treat-fetched-content-as-data rule"
  grep -q '403' "$r" || fail research-loop "researcher lacks the unopenable-source rule (403/429 to Gaps)"
fi

# The research skill: effort table, ledger files, contradictions, note schema link.
s=plugin/skills/research/SKILL.md
if [ -f "$s" ]; then
  grep -Eq '^\| *Brief shape *\| *Workers *\|' "$s" || fail research-loop "research SKILL.md has no effort table (| Brief shape | Workers |)"
  for k in PLAN.md INDEX.md Contradictions note-schema.md 'notes/<facet-slug>.md'; do
    grep -qF "$k" "$s" || fail research-loop "research SKILL.md does not mention $k"
  done
  grep -qF 'notes/<facet>.md' "$s" && fail research-loop "research SKILL.md uses notes/<facet>.md, want notes/<facet-slug>.md"
  grep -qiE 'one tool call' "$s" && fail research-loop "research SKILL.md still says 'one tool call' (one-fact rule is at most two content calls)"
else
  fail research-loop "missing $s"
fi
n=plugin/skills/research/note-schema.md
if [ -f "$n" ]; then
  for h in '## <Key question>' '### Takeaway' '### Cited findings' '### Contradictions' '### Inferences' '### Gaps' '## Tools evaluated'; do
    grep -qx "$h" "$n" || fail research-loop "note-schema.md missing heading line '$h'"
  done
else
  fail research-loop "missing $n"
fi

# Findings index and format.
i=research/findings/INDEX.md
if [ -f "$i" ]; then
  for f in research/findings/*.md; do
    b=$(basename "$f"); case "$b" in _FORMAT.md|INDEX.md) continue;; esac
    grep -qF "]($b)" "$i" || fail research-loop "INDEX.md does not list $b"
  done
  bad=$(grep '^- \[' "$i" | grep -Ev '^- \[[^]]+\]\([a-z0-9-]+\.md\) — .+ \([0-9]{4}-[0-9]{2}-[0-9]{2}, (complete|needs-review|unverified)\)$')
  [ -z "$bad" ] || fail research-loop "INDEX.md line not in '- [title](slug.md) — answer (date, complete|needs-review|unverified)' form: $bad"
  for st in complete needs-review unverified; do
    grep -qF "\`$st\`" "$i" || fail research-loop "INDEX.md does not define status '$st'"
    grep -qF "\`$st\`" plugin/agents/verifier.md || fail research-loop "verifier.md does not define status '$st'"
  done
  for f in research/findings/*.md; do
    b=$(basename "$f"); case "$b" in _FORMAT.md|INDEX.md) continue;; esac
    grep -q '^## Verification' "$f" && continue
    grep -F "]($b)" "$i" | grep -qF ', unverified)' || fail research-loop "INDEX.md marks $b verified but it has no Verification section"
  done
  l=$(wc -l < "$i"); [ "$l" -lt 200 ] || fail research-loop "INDEX.md has $l lines (limit 199)"
else
  fail research-loop "missing $i"
fi
grep -q '^7\. `## Verification`' plugin/skills/research/findings-format.md 2>/dev/null \
  || fail research-loop "findings-format.md lacks section 7 '## Verification'"
