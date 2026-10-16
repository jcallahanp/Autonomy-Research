# Autonomy Research

Research for a fully autonomous Claude Code engineer. This repo is a template for the
research-agent plugin and also the workspace where that agent does its research.

## Repo map
- `plugin/` is the plugin (skills, agents, hooks, scripts, `.mcp.json`). A plugin-root
  CLAUDE.md is never loaded, which is why the plugin lives here and not at the repo root.
- `.claude/` is the template wiring: settings and symlinks to `plugin/skills` and `plugin/agents`.
- `research/` is the workspace: findings, runs, `tool-registry.md`, `open-questions.md`.
- `docs/` holds the proposal, the diagrams (`docs/diagrams/index.md`) and the guides.
- `scripts/` holds template-side scripts such as `cloud-setup.sh`.

## Research rules
- Use the research-agent skills for research. For multi-source research the lead delegates reading to workers and never holds fetched pages; a one-fact lookup may be answered inline with at most two content calls.
- Every claim about a tool cites a page you actually opened. Search snippets are not sources.
- Log every tool you evaluate in `research/tool-registry.md`: name, link, what it does,
  verified date, verdict.
- Add anything you cannot answer to `research/open-questions.md` instead of guessing.
- Diagrams are small Mermaid files, one concern each, linked from `docs/diagrams/index.md`.
  Never one giant design document.
- Write requirements in EARS form ("When X, the system shall Y").

## What the lead may hold in context
- The plan (`PLAN.md`), `research/findings/INDEX.md`, one status line per facet, and the
  last worker summaries.
- Never a fetched page, a raw search result or a full findings file. Read those from disk
  in a subagent and take back a short summary.

## Tools
- MCP servers in `.mcp.json`: DeepWiki, Playwright and Firecrawl (keyless).
- Exa, Context7, Parallel Search and Mermaid Chart come from claude.ai connectors, not this repo.
- Superpowers is installed in cloud sessions by `scripts/cloud-setup.sh`.

# Compact instructions
When compacting, keep:
- The facet list with each facet's status.
- Paths of the plan, the notes and the findings files.
- Names of running subagents.
- Rulings and decisions already made, with the reason.

Drop:
- Fetched page contents.
- Raw search results and tool output.
