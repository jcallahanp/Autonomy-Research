#!/bin/bash
# Structural checks for the research-agent plugin and template.
# Prints "FAIL <rule>: <detail>" for each problem; exits 1 if any.
cd "$(dirname "$0")/.." || exit 1
fails=0
fail() { echo "FAIL $1: $2"; fails=$((fails+1)); }
fm() { awk -v k="$2" 'NR==1&&$0!="---"{exit} NR>1&&$0=="---"{exit} NR>1&&index($0,k":")==1{sub(/^[^:]*:[ ]*/,"");print;exit}' "$1"; }

# Manifests
[ -f .claude-plugin/marketplace.json ] || fail manifest "missing .claude-plugin/marketplace.json"
[ -f plugin/.claude-plugin/plugin.json ] || fail manifest "missing plugin/.claude-plugin/plugin.json"
if [ -f .claude-plugin/marketplace.json ] && [ -f plugin/.claude-plugin/plugin.json ]; then
  m=$(jq -r '.plugins[0].name' .claude-plugin/marketplace.json)
  p=$(jq -r '.name' plugin/.claude-plugin/plugin.json)
  [ "$m" = "$p" ] || fail manifest "marketplace entry '$m' != plugin name '$p'"
  [ "$p" = "research-agent" ] || fail manifest "plugin name is '$p', want research-agent"
  mv=$(jq -r '.plugins[0].version // empty' .claude-plugin/marketplace.json)
  pv=$(jq -r '.version' plugin/.claude-plugin/plugin.json)
  [ -z "$mv" ] || [ "$mv" = "$pv" ] || fail manifest "version mismatch $mv vs $pv"
fi

# CLAUDE.md
if [ -f CLAUDE.md ]; then
  n=$(wc -l < CLAUDE.md); [ "$n" -lt 60 ] || fail claude-md "CLAUDE.md has $n lines (limit 59)"
  grep -q '^@' CLAUDE.md && fail claude-md "CLAUDE.md uses @imports"
  grep -q '^# Compact instructions' CLAUDE.md || fail claude-md "no '# Compact instructions' section"
else fail claude-md "missing CLAUDE.md"; fi

# Skills
for s in plugin/skills/*/SKILL.md; do
  [ -f "$s" ] || break  # none yet: Task 2 adds the rule that requires specific skills
  n=$(wc -l < "$s"); [ "$n" -lt 500 ] || fail skills "$s has $n lines"
  [ -n "$(fm "$s" name)" ] || fail skills "$s missing name"
  d=$(fm "$s" description); [ -n "$d" ] || fail skills "$s missing description"
  [ "${#d}" -lt 1536 ] || fail skills "$s description ${#d} chars"
  [ "$(fm "$s" name)" = "$(basename "$(dirname "$s")")" ] || fail skills "$s name != directory"
done

# Agents
for a in plugin/agents/*.md; do
  [ -f "$a" ] || break  # none yet: Task 2 adds the rule that requires specific agents
  for k in name description model; do [ -n "$(fm "$a" $k)" ] || fail agents "$a missing $k"; done
  grep -Eq '^(hooks|mcpServers|permissionMode):' "$a" && fail agents "$a sets a field plugin agents ignore"
done

# Template side
grep -q enabledPlugins .claude/settings.json 2>/dev/null && fail template "enabledPlugins set in .claude/settings.json"
for l in skills agents; do
  [ -L .claude/$l ] || fail template ".claude/$l is not a symlink"
  [ -d .claude/$l/ ] || fail template ".claude/$l does not resolve"
done
jq -e '.mcpServers' plugin/.mcp.json >/dev/null 2>&1 || fail mcp "plugin/.mcp.json missing or invalid"
grep -Eq '(KEY|TOKEN|SECRET)' plugin/.mcp.json .mcp.json 2>/dev/null && fail mcp ".mcp.json references a secret"

# Extra rules added by later tasks
for f in tests/rules/*.sh; do [ -f "$f" ] && . "$f"; done

[ "$fails" -eq 0 ] && echo "check.sh: all rules pass" || { echo "check.sh: $fails failure(s)"; exit 1; }
