# Runtime (Area 14) - digest
Source: research/findings/engineer-runtime.md; verification: 20 of 20, verified (none unverified; checked 2026-10-16)

## Decision
- One plain Ubuntu VM John controls (small VPS or home box), dedicated non-root user, unmodified Claude Code binary signed in with John's Max plan by `/login` (S16, S20, S28; findings Q7). Cloud cannot do the two things that force a VM: browser work with John's logins (C17 SSO unsupported in cloud; C38-C41 Claude in Chrome is local and visible) and chat-relayed approvals (C54-C56 Channels need a running local session).
- Not `setup-token` or an API key as primary auth: they lose Remote Control, connectors and Chrome (S13, H24, C40); an API key in the environment silently overrides the subscription in `-p` (S15). API key only as an overflow fallback with `--max-budget-usd` (worker inference, Q7).
- Process kept alive in the background with a watchdog that restarts on 401 or stall (S34, S35, S36); fresh session per task, `--max-turns` and `--max-budget-usd` per run (S37-S39, C37, S5).
- Approvals: Channels with a Telegram allowlist plus Remote Control push (C51-C55, C57). Amended by Area 5 (see Tensions).
- Logins live in a dedicated persistent Chromium profile on the VM (pattern S29, S30, S33); Claude in Chrome is a headed-machine fallback only (C39, C41).
- Permissions: skip-permissions only inside the VM boundary as non-root (S7, S8, P3); deny rules still hold under bypass (S9); prefer `auto` or an allowlist (S10, S42).
- Packaging: the single template-plus-plugin repo with a pinned `scripts/bootstrap.sh`, no Docker needed for a VM (P1, P5); Superpowers installed by the bootstrap because cloud does not install repo-declared plugins (C13, P17).
- Companion: cloud Routines for GitHub-only overnight jobs that need no logins or prompts, output on `claude/` branches plus a Slack digest (C19, C21, C29, C49).
- Overnight work is bounded by Max's shared 5-hour and weekly limits, not by a VM timer (C59, C60, S22, S23).

## Alternatives and rejected
- Cloud Routines alone - alternative if browser logins leave scope; zero setup, GitHub-bound (C1, C19, C16).
- GitHub Actions with `CLAUDE_CODE_OAUTH_TOKEN` - alternative for cron/CI-bound jobs (C35, C68).
- Spare Mac with Remote Control server mode or Desktop scheduled tasks - alternative; unlocks 1Password for Claude, Mac-only (C44, C48, S31, S32).
- Codespaces devcontainer - alternative second route where Docker is hidden (P4, P6, P29).
- Agent SDK daemon - alternative for a custom always-on service (H25).
- NanoClaw - alternative only if Slack/WhatsApp control is needed (H10, H11); its Agent SDK claim unverified (open question 18).
- OpenClaw as host - rejected: sandbox off by default (H29), 255+ advisories (H7), ClawHub malware (H8), second permission model; Claude Code already has Channels/RC/Routines (H16, H36).
- Hermes Agent - rejected: not Claude Code-centric (H13).
- `/loop` for overnight - rejected: 7-day expiry, needs an open session (C31).
- Cloud sessions for logged-in browsing - rejected: no login state, SSO unsupported (C17, C15).
- Claude in Chrome unattended - rejected: visible window, pauses on login/CAPTCHA, worker idles (C39, C41).
- Self-hosted environments - rejected: Team/Enterprise only (C18, P10).
- `setup-token`/API key as primary auth - rejected (S13, H24, C40). `--bare` - rejected: ignores OAuth (S2, S14).
- Nix, Packer, Ansible for v1 - rejected: worker inference, Nix/Packer not researched from opened pages; Ansible "later, if multiple hosts" (P11).
- Ralph and Beads as default installs - Phase 2 behind a flag (P18, P19; worker inference).

## Stack
| Tool | What it does here | Where it runs | Cost | Evidence |
| --- | --- | --- | --- | --- |
| Claude Code CLI (`claude -p`, interactive) | The engine; unattended runs | VM | Max plan usage pool; Max price not opened (open q 12) | S1, S16, C59 |
| Ubuntu VM / VPS | Host and isolation boundary | VPS or home box | bux: "A $5/mo VPS is fine" (S29); 10-20 EUR/month for 4 vCPU/8 GB is worker inference, unverified (open q 23) | S29, S25 |
| Channels (Telegram plugin) | Push events and relay permission prompts; research preview | VM | free | C54, C55, C57, H37 |
| Remote Control | Phone view, push on decisions, server mode | VM | in plan; subscription login only | C43, C45, C46, C51-C53 |
| Persistent Chromium profile + Playwright MCP | Browser work with John's logins | VM | free | S29, S30, P26 |
| Routines | Overnight GitHub-only jobs; schedule >= 1 h | Anthropic cloud | plan usage, no VM charge | C19, C21, C23, C1 |
| `scripts/bootstrap.sh` | Pins Claude Code, Node, Playwright browsers, Superpowers, optional `bd` | VM | free | P5, P17, P20 |
| `scripts/doctor.sh` + `/setup` skill | Deterministic health check + tool-name probe | VM | free | P37, P38, P43 |

## Setup steps
| Step | Automated or John | How it is verified |
| --- | --- | --- |
| 1 Choose and rent the VPS or prepare a home box (Ubuntu) | **John** | doctor.sh reports OS and RAM |
| 2 Create the dedicated non-root user | Automated (bootstrap, run once as root) | doctor.sh checks user is not root (S28, P3) |
| 3 Run pinned `bootstrap.sh` (Claude Code version, Node, Playwright browsers, Superpowers, optional `--with-beads`) | Automated | `claude --version` matches pin; `/setup` probes tools (P5, P37) |
| 4 `/login` with the Max account (on a headless box: OAuth from a machine with a browser) | **John** | doctor.sh: no `ANTHROPIC_API_KEY` set unless overflow intended (S15, S26) |
| 5 Create the Telegram bot and pair the sender allowlist for Channels | **John** (BotFather, pairing) | test event reaches the session; relay prompt answered (C54, C57) |
| 6 Turn on Remote Control push settings on the phone | **John** | test push received (C52) |
| 7 Log in to each site in the dedicated browser profile | **John** | session cookie persists across restart (S30) |
| 8 Start the background process with watchdog | Automated | watchdog restarts on simulated stall (S35; spike 1) |
| 9 Create Routines for GitHub-only jobs (not creatable from inside a cloud session) | John or local CLI | Routine run lands on a `claude/` branch (C32, C29) |
| 10 SessionStart probe, fail closed in unattended mode | Automated | probe result logged (P43; inference) |

## Repo composition
- Scripts: `scripts/bootstrap.sh` (pinned), `scripts/doctor.sh`, existing `scripts/cloud-setup.sh` to pin Superpowers (P17, P16); optional `.devcontainer/` as route two (P4, P34).
- Files: `.env.example` (names only; values in a 0600 env file on the VM) (P29, P31, P35); `docs/versions.md` recording pinned commits (inference).
- Skills: `/setup` as verifier (P37); MCP: Playwright stays in `.mcp.json`, binaries installed by bootstrap (P26).
- Hooks: SessionStart probe failing closed (inference); `claude plugin validate --strict` in CI (P40).
- Superpowers: kept, installed by bootstrap pinned to manifest version (P15, P16). Beads: dropped from default, `--with-beads` flag, Phase 2 (P19, P42). Ralph: dropped from default, Phase 2 with iteration cap (P18).
- Process watchdog (mechanism unnamed in the findings; systemd unit references not opened, open q 6).

## Spikes
| Spike | Probe (what to run) | Pass criterion |
| --- | --- | --- |
| 1 Overnight VM run | Claude Code with `--channels plugin:telegram` (allowlist) plus Remote Control in a throwaway VM | Runs unattended overnight; restarts on 401/stall; permission prompts relay rather than stall |
| 2 Routine length and cost | Longest Routine run; usage against Max 5-hour/weekly windows; Oct 7, 2026 "monthly API credits" vs `claude -p` | Max run length and quota draw measured |
| 3 Browser install | Headless Chromium/Playwright in cloud setup script (Full network) and in VM bootstrap | Browsers install and launch in both |
| 4 Routine digest round-trip | Routine posts Slack/email digest; morning approval via GitHub-event routine or `claude -p ... --cloud <id>` | Approval triggers the follow-up run |
| 5 Hook collisions | Install Superpowers, Beads (`bd setup claude`), Ralph Stop hook, repo SessionStart | Collision count recorded; none fatal |
| 6 Connector visibility | Compare `/login` and `setup-token` on the VM | Connectors visible under `/login` |
| 7 Chrome unattended | Claude in Chrome on a headed machine with logged-in profile, unattended | Survives idle without pausing |
| 8 Codespaces persistence | `~/.claude` with `CLAUDE_CONFIG_DIR` mount; pin a third-party marketplace to a tag | Login survives rebuild; pin holds |
| 9 Agent SDK daemon | Webhook/cron-triggered daemon with hooks as guardrails vs Routines | Comparison recorded |
| 10 NanoClaw/OpenClaw (only if Slack/WhatsApp needed) | NanoClaw with API key via credential gateway; OpenClaw `claude-cli`, sandbox `all`, `openclaw security audit`, no ClawHub | Claude Code prompts reach chat safely |
| 11 Billing re-read | Re-read Anthropic's support article on harness and Agent SDK billing | Current terms recorded before committing a subscription |

## Requirements served
- R13: dedicated persistent browser profile on the VM gives browser control with John's logins (S29, S30); cloud cannot (C17).
- R14: Channels permission relay and Remote Control push reach John's phone (C55, C51-C53); Routines batch via Slack digest (C49).
- R15: background process with watchdog on the VM plus Routines overnight (S35, C19, C21).
- R16: Routines push to `claude/` branches with branch protection (C29); self-merge itself not designed here (gap).
- R18: `--max-turns`, `--max-budget-usd`, watchdog on stall, routine runs rejected at limit (C37, S5, S35, C62).
- R23: pinned `bootstrap.sh`, `doctor.sh`, `/setup`, `.env.example` (P5, P37, P29).
- Q2: fresh session per task with state in repo files (S37, S38; inference).
- Q3: watchdog plus stall notification (S34-S36; inference); "status green does not mean task succeeded" for Routines (C27).
- Q7: non-root user in a VM with deny rules as the disclosed boundary (S7, S9, S43, P33).

## GTM scenario
- Scan as-is: VM session with John's logged-in browser profile can open Attio, Clay, n8n, Outreach UIs (S29, S30); repo scan can run as a Routine (C16, C19).
- Fix Attio tables and views: browser work from the VM profile (S30); cloud cannot log in (C17).
- Clay workflows, data cleaning, finishing tooling: host only; mechanism is gap in this area.
- Approvals for the GTM run go over Channels/RC (C55, C51).

## Tensions
- Max `/login` as primary auth (Q7) versus Anthropic's legal page: products "including those using the Agent SDK, should use API key authentication" (human-loop E42). Unresolved; human-loop carries it as a decision for John. Runtime Q2 contradiction 2 (harness use of a subscription) also unresolved.
- Approvals: runtime puts live approvals on Channels plus RC; human-loop Q7 amends: do not rely on the relay overnight (prompts stay open until answered, E109; session pauses at a prompt), digest is owned by a supervisor bot, relay carries no product decisions (E112). Human-loop says its notes win.
- Runtime keeps an always-open interactive session for Channels; human-loop runs `claude -p` per task, where Channels disable interactive tools (human-loop E115). Two process shapes to reconcile.
- Two digest channels: Routines digest on Slack (C49) versus supervisor Telegram digest (human-loop); requirement says one batched list over one channel.
- Secrets: runtime "0600 env file on the VM" (P29, P31) versus human-loop SOPS+age behind a broker user versus deploy 1Password `op` vault pipe.
- Billing of `claude -p` on Max: Oct 7, 2026 "monthly API credits" vs shared windows unresolved (Q2 contradiction 1, open q 27; spike 2).
- Max-length of a Routine or cloud session unknown (open q 25); VPS price and Max prices rest on unopened pages or worker inference (open q 12, 23).
- Hook collision count across Superpowers, Beads, Ralph, SessionStart unknown (open q 34).

## Open for John
- VPS versus home box (and whether a spare Mac is wanted for 1Password for Claude).
- Max `/login` versus a Console API key for the supervisor's runs (with human-loop).
- Whether browser logins stay in scope (if not, Routines alone suffice).
- Whether a Slack/WhatsApp control channel is required (triggers spike 10).
