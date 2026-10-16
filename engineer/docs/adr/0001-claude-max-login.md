# ADR 0001: Claude Max via /login for every run

Status: accepted 2026-10-16

## Context
- The supervisor runs one bounded `claude -p` per task overnight; it needs an auth path (blueprint decisions.md, ruling 1).
- Path A is John's Max `/login`; Path B is a Console API key. A key in the environment silently overrides the subscription in `-p` (engineer-runtime S15).
- Remote Control does not accept `setup-token` or `CLAUDE_CODE_OAUTH_TOKEN` (engineer-host E105); `/login` keeps Remote Control, connectors and Chrome (engineer-runtime S13).
- Recorded risk (engineer-host §Q6 Contradictions): the legal page says "Developers building products or services that interact with Claude's capabilities, including those using the Agent SDK, should use API key authentication" (engineer-host E113; engineer-human-loop E42). The Help Center, updated 2026-10-07, says "You can still use the Claude Agent SDK, claude -p, and third-party apps with your subscription limits" (engineer-host E120). The legal page allows an end user signing in to the unmodified binary with their own subscription (engineer-host E115).

## Decision
- John chose Path A for every run, interactive and unattended. There is no API key in v1.
- The operator logs in with `claude auth login` (`/login`), never `setup-token` (blueprint flow.md F42).
- Every wrapper and `doctor.sh` refuse to start if `ANTHROPIC_API_KEY` or `CLAUDE_CODE_OAUTH_TOKEN` is set.

## Consequences
- The supervisor and `run-task` are built in stage 1; Path B rows are gone from setup.md and the "Verifies all" table.
- Runs share Max's 5-hour and weekly limits; the supervisor waits for resets (ruling 5).
- SP01 re-reads the billing article and the legal page on setup day and adds the quotes here; SP02 confirms what `/login` keeps.
- A Slack bridge on an API key, funded by Max's monthly API credits (engineer-host E122), stays a later option.
