# Changelog

All notable changes to this project are listed here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## Unreleased

Self-improvement round 1 (plan: `docs/self-improvement/2026-10-16-round-1-plan.md`).

### Added
- Skill `self-improve`: the capped loop (frozen exam, tail cases reported separately, research
  on the plugin itself, 20-citation hand check, paired re-measure, keep rule, 2 rounds per
  approval, pull request as sign-off).
- Development eval cases tagged `tail`: `verify-tail` (Verification section, INDEX line,
  PLAN.md Outputs) and `quote-carry` (verbatim quote reaches the findings; a planted claim is
  not cited). Not part of the frozen exam.
- Frozen-exam guard: `tests/frozen-exam.sha256`, checked by `tests/check.sh`.

### Changed
- Verifier: opens Firecrawl and repo `path:line` citations, samples at most 20 claims by risk,
  counts an uncertain judgment as unverified, and can create a missing INDEX.md.
- Notes carry a verbatim `Quote:` (at most 30 words) on every cited finding; the synthesizer
  copies claim, source and quote together and adds nothing not backed by a cited line.
- Repo `path:line` citations are legal sources in notes and findings.
- SessionStart hook: also injects the first 60 lines of the active run's PLAN.md, and the
  newest 30 INDEX.md lines instead of the first 30.
- Researchers write the note skeleton first and are told they may be compacted; dispatches
  copy the PLAN.md Rulings line verbatim; the lead marks PLAN.md Outputs done after
  verification.
- One-fact path: with no search or fetch tool, the lead says so and spawns no worker.
- Consistency: routing.md's verify fallback no longer uses Parallel full content; spike
  registry rows have one writer (the synthesizer); findings files say "Open questions"
  everywhere.

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
