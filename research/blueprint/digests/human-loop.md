# Human in the loop (Area 5) - digest
Source: research/findings/engineer-human-loop.md; verification: 18 of 20 verified, 2 unverified (checked 2026-10-16)

## Decision
- One setup sitting from one ordered page; John makes only the first "parent" credential per service and each OAuth consent click (findings Q11.1; E187). Parent tokens mint narrower children only on Cloudflare (E1, E28), Vercel (E4, E5, E34) and Supabase PAT-driven APIs (E7, E32); Slack apps via manifest API from a hand-made 12 h config token (E10, E11, E30).
- Human-only: GitHub machine account registered by John (bots banned, E40) plus fine-grained PAT (no create API, E13); Telegram bot via @BotFather (E15); Google app + OAuth client (E18); n8n key with expiry (E21, E33); Attio key, workspace token needs an admin (E22); Outreach, WHOOP, Withings apps (E23-E25); Anthropic keys only from the Console (E26, E27).
- Secrets: SOPS+age readable only by a separate `secretbroker` Unix user plus an allowlisted job runner (E58-E60; tool docs not opened, comparison article only). Reason: leaks pass every model-facing control (E69 memory rule ignored, E70 `pass show`, E71 "file changed" notice bypassed a hook, E72 31 secrets) and transcripts are plaintext JSONL holding every tool result (E81, E82).
- Approvals in three tiers (worker inference, Q6): T0 automatic (reversible, in-repo, tests pass); T1 numbered digest with defaults and `all y`, expires to default after 24 h only if reversible; T2 hard gates (money, delete, store, external mail, secrets) as separate messages with typed confirmation, never default on timeout. Grounds: ~93% of prompts approved (E100), sandbox boundary cut prompts 84% (E101), Renovate/Dependabot patterns (E105-E108).
- Channel: the supervisor's own plain Telegram bot carries the digest (E118); Channels relay carries live tool prompts by day only (E111-E114); Remote Control is the phone view (E116); SMS a fallback dead-man alert only (E121). Prompts stay open until answered, so overnight runs must not depend on the relay (E109).
- Audit: every ask and answer appended to committed `decisions/approvals.jsonl`; deterministic code parses replies; unknown format never counts as approval (Q6, inference; format from E110).
- Permissions: supervisor runs `claude -p` per task with `--permission-mode auto --permission-prompts none`, `--max-turns`, `--max-budget-usd` (E126, E129, E131); Bash sandbox on with `allowUnsandboxedCommands: false` (E168); deny rules and `disableBypassPermissionsMode` in root-owned `/etc/claude-code/managed-settings.json` (E148, E150, E151); fail-closed PreToolUse guard and kill-switch file (E152, E163, E158); egress allowlist and server-side branch protection; stop the night after N denials of one kind. Bash deny rules are "not a security boundary" (E142-E145).
- Nothing was spiked; confidence medium (Q11).

## Alternatives and rejected
- Playwright on dashboards with GitHub PAT pre-fill URLs; GitHub App manifest flow - kept as alternatives for keys (E13, E12).
- 1Password service account with agent-only vault - alternative if John has 1Password (E49-E51, E97); price not opened.
- Infisical Agent Vault or Claude cloud network secrets - alternative for HTTPS APIs (E79, E80, E68); preview.
- systemd-creds - alternative for long-running services (E60).
- n8n send-and-wait - alternative only if n8n already runs; claims unverified (open q 14-16). Slack app - alternative. Twilio SMS - dead-man alert only (E121, E122).
- `dontAsk` with exact allowlist; `bypassPermissions` in a container with firewall; Docker Sandboxes (needs KVM); sandbox-runtime (beta); cloud sessions/Routines for GitHub-only jobs - alternatives (E124, E139, E175).
- Bot-created accounts - rejected: GitHub bans them (E40).
- Scraping dashboards to mint keys - rejected (worker judgement).
- OpenBao/Vault - rejected: seals on restart, Shamir split protects nothing for one person (E58).
- Self-hosted Infisical - rejected: rotation and audit log on Pro $20/identity/month (E54).
- Doppler - rejected: 3-day logs on Free (E57). Bitwarden SM as primary - rejected: no advantage (E52, E53).
- `pass` - rejected (E70). Plain `.env`/direnv - rejected (E69, E71). CLAUDE.md or memory rules as enforcement - rejected (E69).
- HumanLayer - rejected: deprecated (E120). LangGraph interrupts - rejected: second runtime, node replay (E119).
- OpenClaw as channel host - rejected (per engineer-runtime.md). SMS as primary channel - rejected: weaker identity, 10DLC registration (E121, E122).
- `bypassPermissions` on the host under John's account - rejected (E133, E134). Bash sandbox alone - rejected (E165). Prose boundaries or deny rules alone - rejected (E137, E144). Ralph loop as shipped - rejected (per registry).

## Stack
| Tool | What it does here | Where it runs | Cost | Evidence |
| --- | --- | --- | --- | --- |
| SOPS + age behind `secretbroker` user | Encrypted secrets; engineer never reads values | VM | free (licences not opened) | E58-E60 |
| Supervisor Telegram bot | Digest out, long-poll replies in, allowlist on `from.id` | VM | free | E16, E118 |
| Channels permission relay (Telegram plugin) | Live daytime tool prompts | VM | free; research preview | E111-E114 |
| Remote Control | Phone view, push for prompts | VM | in Max plan | E116, E117 |
| `claude -p` auto + `--permission-prompts none` | Unattended per-task runs; denials in `permission_denials` | VM | Max usage pool | E126, E129 |
| Managed settings file | Deny rules, `disableBypassPermissionsMode`; beats CLI flags | VM `/etc/claude-code/` | free | E148, E150, E151 |
| Claude Code Bash sandbox (bubblewrap) | Shell isolation; needs AppArmor profile on Ubuntu 24.04 | VM | free | E166-E171 |
| PreToolUse guard + kill-switch hook | Fail-closed command guard | VM | free | E152, E155, E158, E163 |
| Cloudflare / Vercel / Supabase / Slack token APIs | Engineer mints child tokens from John's parent tokens | hosted | free | E1, E4, E7, E11 |
| Twilio SMS (optional) | Dead-man alert | hosted | $0.0083/segment; long code $1.15/month is worker inference (Q7) | E121 |

## Setup steps
| Step | Automated or John | How it is verified |
| --- | --- | --- |
| 1 Run `setup-root.sh`: `engineer` and `secretbroker` users, managed settings, AppArmor profile, sudoers line for `agent-run`, egress allowlist | Automated, run as root by **John** | spikes 8, 19, 21 (`sudo -l`, sandbox up, managed file honoured) |
| 2 Choose what counts as a hard gate | **John** | gate list committed |
| 3 Parent credentials: Cloudflare token with Account API Tokens Edit (broker-held), Vercel token, scoped Supabase PAT, Slack config token | **John** | broker job mints/uses a child; pass/fail per credential |
| 4 Human-only registrations: GitHub machine account + PAT + branch protection; Telegram bot(s); Google app + OAuth client; Outreach, WHOOP, Withings apps (check Withings+); Attio and n8n keys with expiry; Console API key only if John so decides | **John** | broker verification table |
| 5 Every consent click in the same sitting: Slack install, Google, Outreach, WHOOP, Withings; then browser logins by hand (E188) | **John** | broker job calls each API |
| 6 Seed secret values into SOPS files; production, billing, backup values out of the engineer's reach | **John** | engineer sees names only; spike 10 canary grep |
| 7 Privacy: data-privacy toggle (30 days vs 5 years), `DISABLE_FEEDBACK_COMMAND=1`, low `cleanupPeriodDays` | **John** (toggle) / automated (settings) | settings file check (E84, E85, E91) |
| 8 Verification table through broker jobs | Automated | reports pass or fail per credential only |

## Repo composition
- Script: `setup-root.sh` (root VM steps); ordered setup page extended with "parent credential" and "consent click" columns (Implications).
- Files: `/etc/claude-code/managed-settings.json` template; SOPS-encrypted secrets files; `decisions/approvals.jsonl` (committed audit trail); kill-switch file.
- Supervisor component: Telegram digest sender, deterministic reply parser (`1 y 2 n`, `all y`, `CONFIRM 4 SPEND $12`), denial counter that stops the night after N denials and adds them to the morning digest.
- Hooks: fail-closed PreToolUse guard and kill switch (copied idea from cwc, not installed, E163, E164); PostToolUse `updatedToolOutput` as defence in depth pending spike 7 (E66).
- Broker: `agent-run` allowlisted job runner via sudoers; the model never interprets an approval and never receives a value through chat.
- Ralph: dropped as shipped; the cwc pattern of an outer script with capped sessions is kept (E179, E180). Superpowers/Beads: not addressed in this area.

## Spikes
| Spike | Probe (what to run) | Pass criterion |
| --- | --- | --- |
| 1 | Mint a Cloudflare child token with narrow permissions and a TTL | Child token works and expires |
| 2 | Create a Slack app from a manifest, then install it | App installed with one John click |
| 3 | `gcloud iam service-accounts keys create` in a throwaway project | Key created (or org policy block recorded) |
| 4 | Create a Telegram managed bot | Token fetched via `getManagedBotToken` |
| 5 | Check Withings+ requirement on John's account | Requirement known |
| 6 | Look for n8n and Clay key-create endpoints | Endpoint found or absence recorded |
| 7 | `updatedToolOutput` vs transcript JSONL and the "file changed" notice | Replacement is what gets written; fires on the notice |
| 8 | `engineer` tries `sudo -l`, `ps`, `/proc/*/environ` | No secret value readable |
| 9 | Deny rules vs `cat`, `python -c`, `grep -r` and equivalents | Bypasses listed |
| 10 | Full run, then grep `~/.claude/projects/` for a canary secret | Canary absent |
| 11 | Infisical Agent Vault preview | Viable or not |
| 12 | Channels relay under headless tmux with the Telegram plugin | Prompt relays and is answered |
| 13 | One bot shared by plugin and supervisor | Works, or two bots needed |
| 14 | Build and test the `1 y 2 n` parser | Unknown formats never approve |
| 15 | Measure John's reply latency | Timeouts set from data |
| 16 | Cost of a stalled prompt overnight | Cost recorded |
| 17 | auto + `--permission-prompts none` on a task that triggers blocks | Exit code, `permission_denials`, behaviour past 20 blocks recorded |
| 18 | Rewording bypasses (`git -C . push`) vs deny rules, hook, server rule | Server rule holds |
| 19 | Sandbox with `allowUnsandboxedCommands: false` on Ubuntu 24.04 | Sandbox active; `failIfUnavailable` confirmed |
| 20 | Hook timeout behaviour | Blocks with `onFailure: "block"` |
| 21 | Non-root user reading the managed-settings file | Honoured without MDM |
| 22 | Classifier cost per action | Tokens and latency recorded |
| 23 | Max-login vs API-key decision; re-read Agent SDK billing article | Decision recorded |

## Requirements served
- R11: one ordered setup page, one sitting, verified by broker jobs (E187; Q11.1).
- R12: parent-token minting on Cloudflare, Vercel, Supabase, Slack; UI-only steps listed with reason (E1, E4, E7, E10-E13, E40).
- R13: browser logins done by hand in the sitting; login expiry becomes a digest re-login item (E188).
- R14: T1 digest and T2 hard gates park only the gated task, others continue (Q6; E105-E108).
- R15: `claude -p` per task with `--permission-prompts none` so nothing waits on a human (E129, E126).
- R16: T0 tier makes reversible, test-passing repo work automatic; server-side branch protection bounds it (Q6, Q11.3).
- R18: stop after N denials of one kind; kill switch; `--max-turns`, `--max-budget-usd` (E163; Q11.3).
- R10: privacy toggle, feedback off, short transcript cleanup (E84, E85, E91).
- Q3: denials and parked T2 items reach the morning digest (Implications).
- Q7: auto mode inside an isolated non-root VM with managed deny rules, disclosed limits (E124, E133, E144).

## GTM scenario
- Scan as-is / fix Attio tables and views: John makes the Attio key in the Developer console; a workspace-level token needs an admin (E22). Attio terms limit automated decisions about people to supporting human decisions (E47), relevant to data cleaning.
- Clay workflows: gap; Clay key creation and terms not established (Q1 table; spike 6).
- n8n: key made by John in the UI with an expiry (E21, E33).
- Outreach: app plus OAuth consent; development credentials immediate, tokens last 7200 s (E23, E35).
- Finishing tooling: approvals via T1 digest and T2 gates; mechanism as above.

## Tensions
- Max `/login` (engineer-runtime Q7) versus the legal-page rule that products using the Agent SDK "should use API key authentication" (E42, verified). Unresolved; switching to an API key loses Remote Control, connectors and Chrome (E186).
- Overrides engineer-runtime on approvals: no overnight reliance on the Channels relay, digest owned by the supervisor (Q7 contradiction). Area 13 still routes spend gates and deploy approvals over "the Channels/Telegram approval channel" citing the runtime file (deploy E137, E138).
- Secrets store three ways: SOPS+age here, 1Password vault wrapper in engineer-browser.md, 1Password `op` pipe in engineer-deploy Q9, 0600 env file in engineer-runtime; depends on whether John has 1Password (Q3, open questions).
- SOPS+age, systemd-creds facts come from one third-party comparison article; tool docs not opened (Q3).
- Unverified: E69 (the four brokerage keys were revoked; the issue never confirms it) - used only as a leak example. E37 (Withings+ required from 2026-10-12) did not open; note the verifier tried `developers.withings.com` while the findings cite `developer.withings.com`.
- Fatigue remedy contradiction (severity tailoring vs volume cut not raising acceptance) rests on excluded sources; settle by measuring John's approve rate per tier.
- R14 says "send the batch as one concise list"; T2 hard gates are sent as separate immediate messages (Q6). Deliberate, but differs from the requirement text.
- Constraint says "SMS or similar"; SMS is demoted to dead-man alert only (E121, E122).
- Timeouts (24 h default, 12 h reminder, cap of 5 open T1 items) are worker inference, not measured (spike 15).

## Open for John
- Max login versus a Console API key for the supervisor's runs (E42).
- Secrets store: SOPS+age, or 1Password if he already has it (price not opened).
- Which actions count as hard gates beyond money, delete, store submission.
- Data-privacy toggle (30 days vs 5 years) on his account (E85).
- Whether he is willing to keep two Telegram bots if one cannot be shared (spike 13).
