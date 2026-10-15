# Autonomy Research

Research for a fully autonomous Claude Code engineer. Phase 1 is "the project before the project":
build the research and mapping toolkit, then use it to research the engineer itself.

## How to research here
- Every claim about a tool cites a page you actually opened. Search snippets are not sources.
- Log every tool you evaluate in `research/tool-registry.md` (name, link, what it does, verified date, verdict).
- Add anything you can't answer to `research/open-questions.md` instead of guessing.
- Diagrams are small Mermaid files, one concern each (C4 levels: context, containers, components),
  linked from an index. Never one giant design document.
- Write requirements in EARS form ("When X, the system shall Y").

## Tools available
- MCP servers in `.mcp.json`: DeepWiki (ask about any public GitHub repo), Mermaid (validate and render
  diagrams), Playwright (headless browser).
- Exa and Context7 come from claude.ai connectors, not this repo.
- Superpowers is installed in cloud sessions by `scripts/cloud-setup.sh`.
