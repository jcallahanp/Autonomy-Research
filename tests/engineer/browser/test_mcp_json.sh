#!/bin/bash
# engineer/plugin/.mcp.json: valid, keyless, playwright through the wrapper.
set -euo pipefail
. "$(dirname "$0")/../lib.sh"

f=engineer/plugin/.mcp.json
jq -e . "$f" >/dev/null 2>&1 || fail "$f is not valid JSON"
! grep -qE 'KEY|TOKEN|SECRET' "$f" || fail "$f mentions a key, token or secret"
[ "$(jq -r '.mcpServers.playwright.command' "$f")" = bash ] || fail "playwright command is not bash"
arg=$(jq -r '.mcpServers.playwright.args[0]' "$f")
[ "$arg" = '${CLAUDE_PLUGIN_ROOT}/scripts/playwright-mcp.sh' ] || fail "playwright arg: $arg"
[ -f "engineer/plugin/${arg#\$\{CLAUDE_PLUGIN_ROOT\}/}" ] || fail "playwright script missing: $arg"
[ "$(jq '.mcpServers.playwright.args | length' "$f")" -eq 1 ] || fail "playwright takes extra args"
for s in deepwiki firecrawl; do
  [ "$(jq -c ".mcpServers.$s" "$f")" = "$(jq -c ".mcpServers.$s" plugin/.mcp.json)" ] \
    || fail "$s differs from plugin/.mcp.json"
done
[ "$(jq -r '.mcpServers | keys | join(" ")' "$f")" = "deepwiki firecrawl playwright" ] || fail "unexpected servers"
