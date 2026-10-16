# Tool registry

| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Exa | https://mcpservers.org/remote-mcp-servers/exa | Semantic search built for agents | claude.ai connector | 2026-10-15 | Starter kit |
| DeepWiki | https://mcp.deepwiki.com/ | Q&A over any public GitHub repo | `.mcp.json` | 2026-10-15 | Starter kit |
| Context7 | https://context7.com/docs/clients/claude-code | Current library and SDK docs | claude.ai connector | 2026-10-15 | Starter kit |
| Mermaid Chart | https://mermaid.ai/docs/ai/mcp-server | Validates and renders Mermaid | claude.ai connector (repo copy needed sign-in) | 2026-10-15 | Starter kit |
| Playwright MCP | https://playwright.dev/docs/getting-started-mcp | Browser automation | `.mcp.json` | 2026-10-15 | Starter kit |
| Superpowers | https://github.com/obra/superpowers | Engineering methodology skills | plugin, via `scripts/cloud-setup.sh` | 2026-10-15 | In use |
| Sequential Thinking | https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking | Structured thought log | not installed | 2026-10-15 | Low value with current models |
| Ralph Loop | https://claude.com/plugins/ralph-loop | Stop hook re-feeds one prompt until `<promise>` text or iteration cap | not installed | 2026-10-16 | Phase 2; only with script-checked completion + max-iterations |
| Beads | https://github.com/steveyegge/beads | Dolt-backed dependency-graph issue tracker for agents (hook, plugin, MCP) | not installed | 2026-10-16 | Phase 2; git files suffice for one researcher |
| Trail of Bits skills | https://github.com/trailofbits/skills | ~40 security plugins; two relevant (supply-chain-risk-auditor, gh-cli) | not installed | 2026-10-16 | Install only the two named plugins |
| Semgrep plugin | https://claude.com/plugins/semgrep | Post-edit SAST/SCA/secrets scan via Semgrep MCP | not installed | 2026-10-16 | Not useful for a researcher (no code output) |
| OpenClaw | https://openclaw.ai/security | Always-on personal agent platform | not installed | 2026-10-15 | Phase 2, security risk noted |
| supply-chain-risk-auditor (Trail of Bits) | https://github.com/trailofbits/skills/blob/main/plugins/supply-chain-risk-auditor/README.md | OSV advisories, yanked releases, archived upstreams, npm install scripts, Scorecard checks for npm/PyPI/Go deps | plugin + `uv run` scripts | 2026-10-16 | Adopt for "safe to install" checks (see findings/methodology.md) |
| gh-cli (Trail of Bits) | https://github.com/trailofbits/skills/blob/main/plugins/gh-cli/README.md | PreToolUse hooks redirect GitHub fetches to authenticated `gh` | plugin hooks + PATH shim | 2026-10-16 | Evaluate; would deny web_fetch_exa on github.com |
| OpenSSF Scorecard | https://github.com/ossf/scorecard | Per-repo security heuristics scored 0-10, viewer + REST API | hosted, read-only | 2026-10-16 | Adopt as lookup in repo triage |
| claude plugin eval | https://code.claude.com/docs/en/plugin-evals | Runs plugin eval cases with regex/tool_used/llm graders vs no-plugin baseline | Claude Code CLI v2.1.269+ | 2026-10-16 | Adopt for `/self-test` |
