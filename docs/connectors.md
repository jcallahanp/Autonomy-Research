# Connectors

Four research tools are claude.ai connectors. They belong to your claude.ai account, not to
this repo, so neither install path can add them for you. Connect each one by hand.

| Connector | What research uses it for | Fallback when missing |
| --- | --- | --- |
| Parallel Search | Web search and page fetch | Exa, then WebSearch and WebFetch |
| Exa | Web search and page fetch | Parallel Search, then WebSearch and WebFetch |
| Context7 | Current library documentation | WebFetch the official docs page |
| Mermaid Chart | Validate and render Mermaid diagrams | Validate with local `mmdc`; give a live-editor link for humans |

If both Parallel Search and Exa are missing, research runs on WebSearch (titles and URLs only,
US-only) and WebFetch, and says so in every output.

## Connect a connector on claude.ai

1. Sign in to claude.ai with the account you use for Claude Code. Connectors reach Claude Code
   only when you sign in with a claude.ai subscription login, not an API key.
2. Go to **Customize > Connectors**.
3. Click the **+** button next to Connectors.
4. Find the connector by name: Parallel Search, Exa, Context7 or Mermaid Chart.
5. Click **Connect** and follow the sign-in prompts.
6. Start a new Claude Code session so the tools load. Run `/research-agent:setup` (or say "set
   up the research agent") to confirm.

Source: [Use connectors to extend Claude's capabilities](https://support.claude.com/en/articles/11176164-use-connectors-to-extend-claude-s-capabilities).

### Team and Enterprise plans

An Owner must add the connector first, under **Organization settings > Connectors**. Then each
member connects it with steps 2 to 6 above. Source:
[Get started with custom connectors](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp).

### Cloud sessions

Connector traffic goes through Anthropic's servers, not the session's network. If a cloud
session says a connector needs authorizing again, reconnect it at
[claude.ai/customize/connectors](https://claude.ai/customize/connectors). Re-auth does not
happen inside the session. Source: `research/findings/packaging.md`, Q3, which cites the
[Claude Code environments docs](https://code.claude.com/docs/en/cloud-environments).

## Bundled servers need no connector and no key

DeepWiki, Firecrawl (keyless) and Playwright come from `.mcp.json`. They need no API key and no
claude.ai connection. Firecrawl's keyless tier is rate limited, per its
[keyless docs](https://docs.firecrawl.dev/mcp-server/keyless). Locally, accept the one-time
approval prompt for each server; run `/mcp` to see their status.

## Costs

Only free tiers are assumed. Nothing here needs a paid key, and no secret belongs in
`.mcp.json`. If you add a paid key later, see [cloud-sessions.md](cloud-sessions.md) for where
secrets go.
