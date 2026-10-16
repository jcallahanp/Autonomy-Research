# Autonomous engineer blueprint

Purpose: the one-page entry to the build blueprint for John's autonomous Claude Code engineer; start here.

Built 2026-10-16 from the 14 area digests in `digests/` and the findings files in `research/findings/engineer-*.md`.
Citations read "(engineer-<area> E12)" or "(engineer-<area> §section)": the evidence ID or section in
`research/findings/engineer-<area>.md`. This folder is synthesis; nothing here was run or installed.

## What the engineer is
A packaged Claude Code setup that takes a project from a spoken brief to deployed, audited software
with John at design and approval level only. Claude Code is the only engine and the only writer
(engineer-models E57, E58). It runs on one Ubuntu VM John controls (engineer-runtime §Q7, S16, S28).

## Architecture in one paragraph
John talks to an interactive Claude Code session for intake, plan approval and anything that needs
a claude.ai login (publishing pages, Remote Control). After he approves a hash-bound plan
(engineer-planning E29, E30), a supervisor process under systemd (engineer-protocol E124) works the
`tasks.json` DAG: one fresh, bounded `claude -p` per task in its own worktree and branch
(engineer-context §Q7.4; engineer-protocol E37, E38), behind a root-owned managed-settings file, the
Bash sandbox and fail-closed hooks (engineer-human-loop E148, E168, E152). A Stop/TaskCompleted gate
and a script-first auditor decide "done" from evidence, never from the model's claim (engineer-protocol
E11, E15, E138). Secrets sit in SOPS+age files readable only by a `secretbroker` user that runs
allowlisted jobs (engineer-human-loop E58-E60). Browser-only work (Attio views, Clay tables, OAuth
consent) runs in Playwright on a persistent headed branded Chrome profile (engineer-browser T4, S1;
engineer-host E12) on a DigitalOcean droplet. The supervisor's own Telegram bot sends one numbered daily
digest plus immediate hard-gate prompts (engineer-human-loop E118); Remote Control in server mode is
John's phone cockpit (engineer-host E103) (updated 2026-10-16, John's decision). Every night ends in a known state written to `RUN_STATUS.json` and
`MORNING.md` (engineer-context §Q7.5; engineer-protocol E103).

## Files in this folder
| File | What it holds |
| --- | --- |
| [decisions.md](decisions.md) | Per area: decision, alternatives, rejected with reason; the lead's 12 rulings applied |
| [stack.md](stack.md) | Every tool with where it runs and cost; where every secret lives and who can read it |
| [setup.md](setup.md) | Numbered setup order, John's one sitting as one block, the spike that must pass first |
| [repo-composition.md](repo-composition.md) | Plugin and template layout, state files, hooks, MCP, what comes from Superpowers, Beads, Ralph |
| [flow.md](flow.md) | One project end to end, with EARS requirements |
| [gtm-scenario.md](gtm-scenario.md) | John's GTM acceptance scenario traced step by step, GAPs flagged |
| [spikes.md](spikes.md) | Every spike, de-duplicated, ordered by what it blocks |
| [requirements-trace.md](requirements-trace.md) | R1-R23 and Q1-Q8 mapped to decisions |
| [open-questions.md](open-questions.md) | What stays open, with the default taken meanwhile |
| `digests/` | The 14 area digests this blueprint was built from |

Diagrams: `docs/diagrams/engineer-context.mmd`, `engineer-runtime.mmd`, `engineer-project-flow.mmd`,
`engineer-approvals.mmd`, `engineer-supervisor-loop.mmd`, `engineer-browser-route.mmd` (linked from
`docs/diagrams/index.md`). John's decisions are recorded as ADRs 0001-0006 in `engineer/docs/adr/`
(updated 2026-10-16, John's decision).

## Decisions John made
(updated 2026-10-16, John's decision)

| # | Decision | ADR | Where it lands |
| --- | --- | --- | --- |
| 1 | Auth Path A: Claude Max via `/login` for every run, unattended runs included; no API key in v1 | 0001 | Ruling 1; wrappers refuse `ANTHROPIC_API_KEY` and `CLAUDE_CODE_OAUTH_TOKEN` |
| 2 | GitHub Pro bought; R16 self-merge on from day one; no shadow or trial weeks | 0002 | Ruling 2; `self_merge: true`; SP18 gates `--lock`; SP19 dropped |
| 3 | No 1Password: SOPS+age behind `secretbroker` | 0003 | Ruling 6; `op` rows removed |
| 4 | DigitalOcean US-East droplet, Ubuntu 24.04, 4 vCPU / 8 GB; branded Chrome via Playwright `channel chrome`, persistent non-default profile, Xvfb, noVNC behind Cloudflare Access; John signs in by hand once; APIs first; stop and notify on any bot challenge; no stealth, proxy rotation or CAPTCHA solvers; Tailscale exit node at home or a home Mac mini only if the setup-day sign-in test fails | 0004 | Areas 6 and 14; stack.md; F41 |
| 5 | Chat control: Remote Control (server mode) plus a Telegram channel and bot; no NanoClaw or OpenClaw in v1; a Slack bridge on an API key is a later option | 0005 | Ruling 3 |
| 6 | First project: the GTM framework over Attio, Clay, n8n; the focus is the framework for automating such projects | 0006 | setup.md per-project rows |

The rows John used to owe: 1 (auth) is answered by decision 1, 2 (secrets) by decision 3, 3 (R16) by decision 2,
and 5 (host) by decision 4, a dedicated droplet separate from the health VM. One row stays open:

| # | Decision | Default until he answers |
| --- | --- | --- |
| 4 | Hard gates beyond his three, and per-project privacy (ruling 9) | Exactly money, deleting data, app-store submission; production promotes are digest items with default "hold"; health data Claude-only |

## Glossary
| Term | Meaning |
| --- | --- |
| Path A / Path B | Auth for the supervisor's `claude -p` runs: John's Max `/login`, or a Console API key (ruling 1). Path A is chosen (updated 2026-10-16, John's decision) |
| `setup-token` | `claude setup-token`, which mints a one-year OAuth token from a Max plan for servers; it loses Remote Control and connectors like an API key (engineer-runtime §Authentication, S13) |
| `--bare` | A `claude -p` mode that ignores OAuth login, hooks and MCP from the directory (engineer-feasibility C20, C21) |
| Builder session | The interactive Claude Code session under John's `/login` that builds the engineer (setup.md) |
| Supervisor | The engineer's own outer process under systemd that runs one `claude -p` per task |
| Broker, `agent-run` | The `secretbroker` user and its allowlisted job runner; the only way the engineer uses a secret |
| T0, T1, T2 | Approval tiers: automatic; a numbered line in the daily digest; a hard-gate prompt sent at once |
| Tier 1 / Tier 2 paths | Protocol's merge classes: Tier 1 self-merges (R16 is on); Tier 2 always needs John's own approving review (engineer-protocol §Q5) (updated 2026-10-16, John's decision) |
| `NEEDS-JOHN` | An auditor verdict that turns into a T1 line |
| D0, D1, D2 | Discovery depth: D0 lookup with at most 2 content calls; D1 one capability, one worker, at most 15 calls and 3 URLs; D2 a real choice, 2-3 workers (engineer-tool-discovery §Tiers) |
| Capability card | Input to a discovery pass: operations needed, auth John can complete, writes required (engineer-tool-discovery §Implications) |
| `ROW:` | The six-column tool-registry row a discovery pass returns (Tool, Link, What it does, Where it runs, Verified, Verdict) (engineer-tool-discovery E74, E75) |
| Dead-end | A recorded negative result in `dead-ends.md` with the version tested and `retry-when` |
| `inconclusive` | The verdict when a trial or discovery box ends without a pass |
| Trial | A feasibility test of one path in a sandboxed container (engineer-feasibility) |
| Ledger | Superpowers' git-ignored progress file that survives compaction (engineer-context §Superpowers) |
| pass^3 | All 3 repeated trials of a task pass; used to decide if a cheaper model tier holds (engineer-context §Measuring tier choices) |
| As-is pack | The map of an existing system: context diagram, system-of-record table, credential names, gaps, risks |
| `profile.yaml` | Per-project gates, data classes, promote and self-merge settings, and adopted repo rules |
| EARS | "When X, the engineer shall Y" requirement form |
| ADR / MADR | Architecture decision record; MADR is its Markdown template, kept in `docs/adr/` |
| `waiting_for_reset`, `stopped_by_bound` | Run states: paused for a usage-limit reset; ended by a turn, budget, time or weekly-limit bound |
| Channels, Remote Control, Routines | Claude Code features: chat relay of a live session (research preview); phone view of a session; scheduled cloud runs |
| Server mode (Remote Control) | Remote Control run as a long-lived server process on the headless droplet, so John can open sessions from his phone; kept alive by a restart unit because it exits after about 10 minutes offline (engineer-host E103, E104) (updated 2026-10-16, John's decision) |
| SPxx | A spike in spikes.md |
