# Task 6 rules: docs for strangers, repo files and the CI workflow.
# Sourced by tests/check.sh (provides fail, fm). Offline: reads files only.

docs="docs/installation.md docs/connectors.md docs/plugin-vs-template.md docs/cloud-sessions.md"
repo_files="README.md CHANGELOG.md CONTRIBUTING.md SECURITY.md"
wf=.github/workflows/validate.yml

for f in $docs $repo_files $wf; do
  [ -f "$f" ] || fail docs "missing $f"
done

# Each guide stays short.
for f in $docs; do
  [ -f "$f" ] || continue
  n=$(wc -l < "$f"); [ "$n" -le 120 ] || fail docs "$f has $n lines (limit 120)"
done

# Minimum version is stated where a stranger will look.
for f in docs/installation.md README.md; do
  [ -f "$f" ] && { grep -q '2\.1\.292' "$f" || fail docs "$f does not state minimum version 2.1.292"; }
done

# Installation covers both paths, verify, troubleshoot, uninstall, with the real names.
if [ -f docs/installation.md ]; then
  for k in "research-agent-marketplace" "jcallahanp/Autonomy-Research" "/research-agent:setup" \
           "set up the research agent" "## Troubleshooting" "## Uninstall" "claude plugin uninstall"; do
    grep -qF -- "$k" docs/installation.md || fail docs "docs/installation.md does not mention '$k'"
  done
  grep -q 'Verify path A' docs/installation.md && grep -q 'Verify path B' docs/installation.md \
    || fail docs "docs/installation.md lacks a verify step for each path"
fi

# Connectors: the four connectors, the exact UI path, the Owner step, and the free-tier note.
if [ -f docs/connectors.md ]; then
  for k in "Parallel Search" "Exa" "Context7" "Mermaid Chart" "Customize > Connectors" \
           "Organization settings > Connectors" "Connect" "free tier"; do
    grep -qF -- "$k" docs/connectors.md || fail docs "docs/connectors.md does not mention '$k'"
  done
fi

# Cloud sessions: the points a stranger needs.
if [ -f docs/cloud-sessions.md ]; then
  for k in "claude.ai/code" "scripts/cloud-setup.sh" "CLAUDE_CODE_REMOTE" "Superpowers" "claude mcp add" "no user logins"; do
    grep -qiF -- "$k" docs/cloud-sessions.md || fail docs "docs/cloud-sessions.md does not mention '$k'"
  done
fi

# README is for strangers: no sign-off wording, links to the proposal, diagram index and docs.
if [ -f README.md ]; then
  grep -qi 'awaiting sign-off' README.md && fail docs "README.md still says awaiting sign-off"
  for k in docs/proposal/ docs/diagrams/index.md docs/installation.md docs/connectors.md \
           docs/plugin-vs-template.md docs/cloud-sessions.md "MIT"; do
    grep -qF -- "$k" README.md || fail docs "README.md does not mention '$k'"
  done
  for s in $(ls plugin/skills 2>/dev/null); do
    grep -qF -- "\`$s\`" README.md || fail docs "README.md skill table lacks $s"
  done
fi

# Relative links in the docs and README resolve.
for f in $docs $repo_files; do
  [ -f "$f" ] || continue
  d=$(dirname "$f")
  for l in $(grep -oE '\]\(([^)#:]+)(#[^)]*)?\)' "$f" | sed -E 's/^\]\(([^)#]*).*/\1/'); do
    [ -e "$d/$l" ] || fail docs "$f links to missing $l"
  done
done

# Changelog matches the plugin version and date.
if [ -f CHANGELOG.md ] && [ -f plugin/.claude-plugin/plugin.json ]; then
  v=$(jq -r .version plugin/.claude-plugin/plugin.json)
  grep -qE "^## $v - 2026-10-16" CHANGELOG.md || fail docs "CHANGELOG.md has no '## $v - 2026-10-16' entry"
fi

# SECURITY names the rules and no invented email.
if [ -f SECURITY.md ]; then
  grep -qi 'private vulnerability reporting' SECURITY.md || fail docs "SECURITY.md lacks private vulnerability reporting"
  grep -qE '[A-Za-z0-9._-]+@[A-Za-z0-9.-]+\.[a-z]{2,}' SECURITY.md && fail docs "SECURITY.md contains an email address"
  grep -q 'env -i' SECURITY.md || fail docs "SECURITY.md does not mention env -i"
fi

# No secrets in the new files.
for f in $docs $repo_files $wf; do
  [ -f "$f" ] || continue
  grep -Eq '(sk-[A-Za-z0-9]{16,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|fc-[A-Za-z0-9]{20,}|Bearer [A-Za-z0-9._-]{20,})' "$f" \
    && fail docs "$f looks like it contains a secret"
done

# Workflow: triggers, checks, pins, no secrets.
if [ -f "$wf" ]; then
  grep -qE '^  push:' "$wf" || fail docs "$wf does not trigger on push"
  grep -qE '^  pull_request:' "$wf" || fail docs "$wf does not trigger on pull_request"
  grep -q 'bash tests/check.sh' "$wf" || fail docs "$wf does not run tests/check.sh"
  grep -q 'bash tests/check-mermaid.sh' "$wf" || fail docs "$wf does not run tests/check-mermaid.sh"
  grep -q 'claude plugin validate plugin --strict' "$wf" || fail docs "$wf does not run claude plugin validate"
  grep -q '@anthropic-ai/claude-code@[0-9]\+\.[0-9]\+\.[0-9]\+' "$wf" || fail docs "$wf does not pin Claude Code to an exact version"
  grep -v '^[[:space:]]*#' "$wf" | grep -qE 'secrets\.' && fail docs "$wf uses secrets"
  for u in $(grep -oE 'uses: *[^ ]+' "$wf" | sed 's/uses: *//'); do
    echo "$u" | grep -qE '@v[0-9]+\.[0-9]+\.[0-9]+$' || fail docs "$wf action $u is not pinned to an exact version"
  done
  grep -qE 'node-version: *"?[0-9]+\.[0-9]+\.[0-9]+"?' "$wf" || fail docs "$wf does not pin Node to an exact version"
fi

# Registry: Firecrawl is recorded as installed.
grep -E '^\| Firecrawl' research/tool-registry.md | grep -q 'plugin/.mcp.json' \
  || fail docs "research/tool-registry.md Firecrawl row does not say it is bundled in plugin/.mcp.json"
