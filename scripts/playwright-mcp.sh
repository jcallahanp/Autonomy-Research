#!/bin/bash
# Starts the Playwright MCP server. In cloud sessions it points at the
# pre-installed Chromium, because @playwright/mcp@latest expects a newer
# browser build than the cloud image ships.
args=(-y @playwright/mcp@latest --headless --browser chromium)
if [ "$CLAUDE_CODE_REMOTE" = "true" ] && [ -x /opt/pw-browsers/chromium ]; then
  args+=(--executable-path /opt/pw-browsers/chromium)
fi
exec npx "${args[@]}"
