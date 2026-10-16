# Task 3 rules: tool skills (setup, tool-scan, repo-triage, using-research-agent), routing.md,
# the SessionStart hook script and its wiring. Sourced by tests/check.sh (provides fail, fm).

for k in setup tool-scan repo-triage using-research-agent; do
  [ -f "plugin/skills/$k/SKILL.md" ] || fail tool-skills "missing plugin/skills/$k/SKILL.md"
done

# Setup names all seven tools, the manual path, and the fallbacks.
s=plugin/skills/setup/SKILL.md
if [ -f "$s" ]; then
  for t in 'Parallel Search' Exa Context7 'Mermaid Chart' DeepWiki Playwright Firecrawl 'Customize > Connectors' \
           'Organization settings > Connectors' ToolSearch WebFetch WebSearch; do
    grep -qF "$t" "$s" || fail tool-skills "setup SKILL.md does not mention '$t'"
  done
fi

# repo-triage never executes the candidate.
s=plugin/skills/repo-triage/SKILL.md
if [ -f "$s" ]; then
  grep -qF 'git clone --depth 1' "$s" || fail tool-skills "repo-triage lacks 'git clone --depth 1'"
  grep -qiE 'never (install|run|execute)' "$s" || fail tool-skills "repo-triage lacks the never-execute rule"
  grep -qi 'as data' "$s" || fail tool-skills "repo-triage lacks the treat-repo-content-as-data rule"
fi
s=plugin/skills/tool-scan/SKILL.md
if [ -f "$s" ]; then
  grep -qF 'routing.md' "$s" || fail tool-skills "tool-scan does not point to routing.md"
  grep -qF 'tool-registry.md' "$s" || fail tool-skills "tool-scan does not log to tool-registry.md"
fi

# Routing table: nine rows copied from the proposal, linked from the research skill.
r=plugin/skills/research/routing.md
if [ -f "$r" ]; then
  rows=$(grep -c '^| ' "$r"); [ "$rows" -ge 11 ] || fail tool-skills "routing.md has $rows table lines, want >= 11"
  for t in 'Parallel web_search' 'DeepWiki ask_wiki_question' 'Context7' 'mmdc'; do
    grep -qF "$t" "$r" || fail tool-skills "routing.md lacks '$t'"
  done
else fail tool-skills "missing $r"; fi
grep -qF 'routing.md' plugin/skills/research/SKILL.md || fail tool-skills "research SKILL.md does not point to routing.md"

# Session-start hook script: valid JSON in the fixed shape, with and without INDEX.md.
h=plugin/hooks/session-start.sh
if [ -f "$h" ]; then
  tmp=$(mktemp -d)
  mkdir -p "$tmp/research/findings"
  printf '%s\n' '# Index' '- [Quote "x"](a.md) — says "hi" \ back (2026-10-16, complete)' > "$tmp/research/findings/INDEX.md"
  for i in $(seq 1 40); do echo "- line $i" >> "$tmp/research/findings/INDEX.md"; done
  out=$(CLAUDE_PROJECT_DIR="$tmp" CLAUDE_PLUGIN_ROOT="$PWD/plugin" bash "$h"); rc=$?
  [ "$rc" -eq 0 ] || fail tool-skills "session-start.sh exited $rc"
  echo "$out" | jq -e '.hookSpecificOutput.hookEventName == "SessionStart"' >/dev/null 2>&1 \
    || fail tool-skills "session-start.sh output is not valid JSON with hookEventName SessionStart"
  ctx=$(echo "$out" | jq -r '.hookSpecificOutput.additionalContext // empty' 2>/dev/null)
  case "$ctx" in *using-research-agent*) ;; *) fail tool-skills "session-start additionalContext lacks 'using-research-agent'";; esac
  case "$ctx" in *'Quote "x"'*) ;; *) fail tool-skills "session-start did not carry INDEX.md lines (quotes)";; esac
  case "$ctx" in *'- line 28'*) ;; *) fail tool-skills "session-start dropped INDEX.md line 30";; esac
  case "$ctx" in *'- line 29'*) fail tool-skills "session-start carried more than 30 INDEX.md lines";; esac
  rm -rf "$tmp/research"
  out=$(CLAUDE_PROJECT_DIR="$tmp" CLAUDE_PLUGIN_ROOT="$PWD/plugin" bash "$h"); rc=$?
  [ "$rc" -eq 0 ] || fail tool-skills "session-start.sh exited $rc without INDEX.md"
  echo "$out" | jq -e '.hookSpecificOutput.additionalContext | contains("using-research-agent")' >/dev/null 2>&1 \
    || fail tool-skills "session-start.sh without INDEX.md is not valid JSON containing using-research-agent"
  out=$(cd / && env -u CLAUDE_PROJECT_DIR -u CLAUDE_PLUGIN_ROOT bash "$OLDPWD/$h" 2>/dev/null); rc=$?
  [ "$rc" -eq 0 ] && echo "$out" | jq -e '.hookSpecificOutput.additionalContext | contains("using-research-agent")' >/dev/null 2>&1 \
    || fail tool-skills "session-start.sh fails when no CLAUDE_* env vars are set (script-path fallback)"
  rm -rf "$tmp"
else fail tool-skills "missing $h"; fi

# Wiring: plugin hooks.json and the cloud settings hook, one place per surface.
if [ -f plugin/hooks/hooks.json ]; then
  jq -e '[.hooks.SessionStart[].hooks[].command] | any(contains("${CLAUDE_PLUGIN_ROOT}/hooks/session-start.sh"))' \
    plugin/hooks/hooks.json >/dev/null 2>&1 || fail tool-skills "plugin/hooks/hooks.json does not run \${CLAUDE_PLUGIN_ROOT}/hooks/session-start.sh"
else fail tool-skills "missing plugin/hooks/hooks.json"; fi
jq -e '[.hooks.SessionStart[].hooks[].command] | any(contains("plugin/hooks/session-start.sh")) and any(contains("scripts/cloud-setup.sh"))' \
  .claude/settings.json >/dev/null 2>&1 || fail tool-skills ".claude/settings.json SessionStart does not run both cloud-setup.sh and plugin/hooks/session-start.sh"

# CLAUDE.md one-fact rule matches the research skill.
grep -q 'one-fact lookup.*at most two content calls' CLAUDE.md || fail tool-skills "CLAUDE.md one-fact rule does not say 'at most two content calls'"
