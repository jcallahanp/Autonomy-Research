# Changelog

All notable changes to this project are listed here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## 0.1.0 - 2026-10-16

First release.

### Added
- Plugin `research-agent` in `plugin/`, with marketplace `research-agent-marketplace`
  (`.claude-plugin/marketplace.json`). Minimum Claude Code version 2.1.292.
- Nine skills: `research`, `setup`, `tool-scan`, `repo-triage`, `using-research-agent`,
  `interview`, `system-map`, `spike`, `self-test`.
- Four agents: `researcher`, `synthesizer`, `verifier`, `spike-worker`.
- SessionStart hook that injects the skill index and the top of `research/findings/INDEX.md`:
  `plugin/hooks/hooks.json` for installed users, `.claude/settings.json` for cloud sessions
  (guarded by `CLAUDE_CODE_REMOTE`).
- Bundled keyless MCP servers in `.mcp.json`: DeepWiki, Firecrawl and Playwright.
- Template wiring: `.claude/settings.json` and `.claude/skills` and `.claude/agents` symlinks
  to `plugin/skills` and `plugin/agents`; `scripts/cloud-setup.sh` installs Superpowers in
  cloud sessions.
- Eval suite in `plugin/evals` and the `self-test` skill that runs it with `claude plugin eval`.
- Research workspace: `research/findings`, `research/tool-registry.md`,
  `research/open-questions.md`, and small Mermaid diagrams in `docs/diagrams`.
- Checks: `tests/check.sh` and `tests/check-mermaid.sh`, run in CI by
  `.github/workflows/validate.yml`.
- Docs: `docs/installation.md`, `docs/connectors.md`, `docs/plugin-vs-template.md`,
  `docs/cloud-sessions.md`, plus `CONTRIBUTING.md` and `SECURITY.md`.
