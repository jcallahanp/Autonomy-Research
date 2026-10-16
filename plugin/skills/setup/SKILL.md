---
name: setup
description: Check that the research-agent tools are connected and print the exact steps for any that are missing. Use when the user says "set up the research agent", "check my research tools", or runs /research-agent:setup, or when a research run reports missing connectors (no Parallel Search or Exa tools, no Context7). Probes seven tools by name - Parallel Search, Exa, Context7, Mermaid Chart (claude.ai connectors) and DeepWiki, Playwright, Firecrawl (bundled) - and prints only what is missing, with the fallback research will use.
---

# Setup

Probe the seven tools by name, then print steps only for the ones that are missing. Print
nothing for tools that are present beyond one line "All seven tools present."

## 1. Probe

Tools may be deferred, so a tool absent from your list is not yet proof it is missing. Call
ToolSearch once per row with the query below and treat zero matches as missing. Installed as a
plugin, the bundled servers' tools are named `mcp__plugin_research-agent_<server>__<tool>`
instead of `mcp__<server>__<tool>`; each query names both forms, and either form matching
counts as present. Connector tools never carry the plugin prefix.

| Tool | Kind | ToolSearch query | Fallback research uses when missing |
| --- | --- | --- | --- |
| Parallel Search | claude.ai connector | `mcp__Parallel_Search__web_search` | Exa, then WebSearch and WebFetch |
| Exa | claude.ai connector | `mcp__Exa__web_search_exa` | Parallel Search, then WebSearch and WebFetch |
| Context7 | claude.ai connector | `mcp__Context7__resolve-library-id` | WebFetch the official docs page |
| Mermaid Chart | claude.ai connector | `mcp__Mermaid_Chart__validate_and_render_mermaid_diagram` | Validate with local `mmdc`; give a live-editor link for humans |
| DeepWiki | bundled `.mcp.json` | `select:mcp__deepwiki__ask_wiki_question,mcp__plugin_research-agent_deepwiki__ask_wiki_question` | `git clone --depth 1` and grep |
| Playwright | bundled `.mcp.json` | `select:mcp__playwright__browser_navigate,mcp__plugin_research-agent_playwright__browser_navigate` | Firecrawl, then WebFetch; pages needing a browser go to Gaps |
| Firecrawl | bundled `.mcp.json` | `select:mcp__firecrawl__firecrawl_scrape,mcp__plugin_research-agent_firecrawl__firecrawl_scrape` | Parallel or Exa fetch, then WebFetch |

If both Parallel Search and Exa are missing, say research will run on WebSearch (titles and
URLs only, US-only) and WebFetch, and will say so in every output.

## 2. Print the steps

For each missing connector (Parallel Search, Exa, Context7, Mermaid Chart), print:

1. Name the connector and the fallback from the table.
2. The manual steps, exactly:
   - On claude.ai: Customize > Connectors, the + button, find the connector by name, Connect.
   - Team or Enterprise plans: an Owner must add it first under Organization settings > Connectors,
     then each member connects it as above.
   - Connectors are per account, not per repo. Start a new session afterwards so the tools load.

For a missing bundled tool (DeepWiki, Playwright, Firecrawl):
- Template (cloud or local clone): the servers come from `.mcp.json`. Locally, accept the
  one-time per-server approval prompt; run `/mcp` to see status.
- Installed plugin: they come from the plugin's `.mcp.json`; run `/mcp` and, if absent,
  `claude plugin list` to confirm research-agent is enabled.
- Playwright needs Node and a browser download on first use; if it fails, treat it as the last
  resort tool and continue without it.

## 3. Finish

End with one line per missing tool: `<tool>: missing, fallback <fallback>`. Do not edit
settings, install anything, or add keys. All seven tools here are keyless; no secrets are
needed.
