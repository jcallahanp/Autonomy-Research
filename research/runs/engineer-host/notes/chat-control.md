# Controlling the engineer from WhatsApp, Slack or Telegram

Brief: Tell John whether NanoClaw is the best way to talk to and control the engineer (Claude Code) from WhatsApp or Slack, or what is better, given the Claude Max plan.
Run: research/runs/engineer-host/PLAN.md

## 1. NanoClaw: what it is, channels, auth, isolation, health

### Takeaway
NanoClaw (MIT, ~31k stars, calendar release 2026.10.0 on 2026-10-09) is a chat-to-Agent-SDK assistant in Docker containers, with WhatsApp (Baileys or Cloud API), Slack, Telegram and more as add-on skills. It is a separate assistant that runs its own agents, not a remote for John's existing engineer session; the isolation that protects the host also cuts the agent off from the VM's headed Chrome and logged-in browser unless he mounts them in. It has had two CVEs (one in the approval handler). Confidence: high on facts, medium on fit.

### Cited findings
- Channels: WhatsApp, Telegram, Discord, Slack, Teams, iMessage and others, installed on demand by `/add-<channel>` skills — https://github.com/nanocoai/nanoclaw README.md:91 (clone, commit 2105169, read 2026-10-16) — Quote: "WhatsApp, Telegram, Discord, Slack, Microsoft Teams, iMessage, Matrix, Google Chat, Webex, Linear, GitHub, WeChat, and email via Resend."
- Engine is the Agent SDK, not the `claude` TUI — README.md:87 (same commit) — Quote: "NanoClaw natively uses Claude Code via Anthropic's official Claude Agent SDK"
- Agent SDK is a dependency of the in-container runner — container/agent-runner/package.json:12 — Quote: "@anthropic-ai/claude-agent-sdk": "^0.3.296","
- Auth options include a Claude subscription OAuth token or an API key — docs/SPEC.md:391 and :397 — Quote: "Option 1: Claude Subscription (OAuth token)" ... "Option 2: Pay-per-use API Key"
- Setup captures the token from `claude setup-token` — setup/lib/captured-token.ts:49 — Quote: "Extract the Claude OAuth token from a PTY capture of `claude setup-token`,"
- Isolation: Docker container per session, mounts only; credential gateway injects keys — README.md:97 — Quote: "agents never hold raw API keys. Outbound requests route through a credential gateway that injects credentials at request time"
- Container boundary is the primary defence — docs/SECURITY.md:24-28 — Quote: "Container Isolation (Primary Boundary)"
- WhatsApp adapter uses Baileys (unofficial WhatsApp Web emulation); a separate `add-whatsapp-cloud` skill exists — docs/api-details.md:221 and `.claude/skills/` listing — Quote: "The WhatsApp/Baileys adapter is the canonical example"
- Repo health: 30,951 stars, 1,048 open issues, MIT, created 2026-01-31 — https://github.com/nanocoai/nanoclaw, opened 2026-10-16, Exa fetch — Quote: "Open issues: 1048"
- Release 2026.10.0 of 2026-10-09 carries a BREAKING gateway upgrade for a credential-injection bypass — CHANGELOG.md (commit 2105169) — Quote: "upgrade the OneCLI gateway to exactly 1.42.0, which closes a credential-injection bypass."
- Approval-handler CVE: NanoClaw before 2.1.17 lets a responder without role approve privileged actions — https://nvd.nist.gov/vuln/detail/CVE-2026-56402 as shown in a Parallel search excerpt only; direct WebFetch of the NVD page returned no content, so it is a Gap, not cited.
- Third-party NanoClaw site says it needs an API key (stale/other site, not the repo) — not opened, Gap.

### Contradictions
- Repo docs offer a subscription OAuth token (docs/SPEC.md:391) while Anthropic's page says Agent SDK developers "should use API key authentication" (see section 4). Not a factual conflict, a policy tension; section 4 sets both out.

### Inferences
- The repo's own mention of subscription auth means NanoClaw will technically run on a Max `setup-token`, but that is the exact pattern the legal page restricts (section 4). Rests on SPEC.md:391 and the legal page.
- NanoClaw runs its own agent in a container; it does not attach to John's host Claude Code session, so the engineer's Playwright/Chrome/noVNC setup would have to be rebuilt inside or mounted into the container. Rests on README.md:87, docs/SECURITY.md mounts table.

### Gaps
- Commit cadence and issue triage are not measurable from a depth-1 clone; GitHub API returned "access not enabled" in this session.
- NVD CVE-2026-56402 and CVE-2026-7875 and GHSA-mhq9-hcw8-22mj seen in search excerpts only (not opened); severity unknown.
- Not verified whether Max OAuth via the OneCLI gateway still works on v2 (only the setup log wording "subscription / oauth / api", docs/setup-flow.md:182); no run allowed.

## 2. Anthropic-native options

### Takeaway
Channels (Telegram, Discord, iMessage; no Slack, no WhatsApp) and Remote Control both run against a session on John's own host and both work on Max with claude.ai login; Remote Control is the best phone view and approval path. Claude in Slack only starts cloud sessions on GitHub repos, so it cannot reach the VPS browser session. Confidence: high.

### Cited findings
- Channels support: "Telegram, Discord, and iMessage are included in the research preview." — https://code.claude.com/docs/en/channels, opened 2026-10-16, WebFetch — Quote: "Telegram, Discord, and iMessage are included in the research preview."
- Channels need an open session; always-on means a background process — same page — Quote: "Events only arrive while the session is open, so for an always-on setup you run Claude in a background process or persistent terminal."
- Channels auth: claude.ai or Console key; Pro/Max without an org skip admin checks — same page — Quote: "Pro and Max users without an organization skip these checks entirely"
- Permission relay forwards approval prompts to chat; any allowlisted sender can approve — same page — Quote: "Anyone who can reply through the channel can approve or deny tool use in your session"
- Channels are a research preview; flags may change; custom channels can be built — same page — Quote: "Channels are a research preview feature."
- Remote Control needs subscription login, not an API key — https://code.claude.com/docs/en/remote-control, opened 2026-10-16, WebFetch (saved output line 28) — Quote: "available on Pro, Max, Team, and Enterprise plans. API keys are not supported."
- Remote Control server mode on a headless host, QR code for phone — same page, line 53 — Quote: "The process stays running in your terminal in server mode, waiting for remote connections."
- Remote Control gives up after about 10 min offline in server mode — same page, line 345 — Quote: "Claude Code gives up after roughly 10 minutes and the `claude remote-control` process exits."
- `setup-token`/`CLAUDE_CODE_OAUTH_TOKEN` cannot establish Remote Control — same page, line 407 — Quote: "These tokens can only make model requests, so they can't establish Remote Control sessions."
- Remote Control sends push notifications to the phone — same page, line 306 — Quote: "When Remote Control is active, Claude can send push notifications to your phone."
- Claude in Slack starts cloud sessions, channels only (no DMs), needs Pro/Max and GitHub — https://code.claude.com/docs/en/slack, opened 2026-10-16, WebFetch — Quote: "creates a Claude Code cloud session, allowing you to delegate development work without leaving your team conversations."
- Same page: "Claude Code in Slack only works in channels (public or private). It does not work in direct messages (DMs)." and "GitHub only: repositories must be on GitHub." — Quote: "It does not work in direct messages (DMs)."
- Claude Tag is the Team/Enterprise successor; legacy bot retired for connected workspaces on 2026-10-05 — same page — Quote: "Claude Tag isn't available on individual plans"
- Routines: not re-opened this run; registry row (Routines, 2026-10-16) says cloud, no approval prompts. See Gaps.

### Contradictions
- None found.

### Inferences
- Channels are the native way to get Telegram into the VPS session, with approval relay; there is no native WhatsApp or Slack channel for a local session. Rests on the channels page list.
- A custom channel (channels reference) could bridge Slack to the VPS session without a second agent; effort is John's/the engineer's own build, untested. Rests on "To build your own channel" in the channels page.
- Because Remote Control rejects setup-token auth, the VPS user must do an interactive `claude auth login`; Channels accepts the same login. Rests on remote-control line 407.

### Gaps
- Routines and Claude Tag pages not opened here.
- Whether Channels and Remote Control can run in the same VPS session was not verified.
- Channels reference (permission relay detail, Slack custom channel feasibility) not opened.

## 3. Other bridges and WhatsApp ban risk

### Takeaway
Every WhatsApp route for a personal assistant is either unofficial (Baileys, ban risk, small and accepted by the bridge authors) or the official Business Platform, whose terms bar AI providers whose AI is the primary offering; for John a dedicated number on the Cloud API for a private single-user bot is a grey zone. Telegram is the lowest-friction, ban-free chat. Confidence: medium.

### Cited findings
- Hermes Agent's Baileys bridge states the risk — https://hermes-agent.nousresearch.com/docs/user-guide/messaging/whatsapp, opened 2026-10-16, WebFetch — Quote: "Using a third-party bridge carries a small risk of account restrictions."
- Hermes advice: dedicated number, no bulk, no unsolicited outbound — same page — Quote: "Use a dedicated phone number for the bot (not your personal number)"
- Meta's AI Provider clause (effective 2026-01-15) — https://techcrunch.com/2025/10/18/whatssapp-changes-its-terms-to-bar-general-purpose-chatbots-from-its-platform/ appeared in Parallel search excerpt, not opened; the WhatsApp terms page itself (https://www.whatsapp.com/legal/business-solution-terms) was seen in search excerpts only. Both moved to Gaps.
- OpenClaw and Hermes: registry rows verified 2026-10-16 (research/tool-registry.md lines 161, 76) — Quote: "MIT Node gateway daemon, 20+ chat channels, drives Claude Code via claude-cli backend or ACP; install via curl script/npm/Docker; sandbox off by default; 255+ advisories"

### Contradictions
- None found.

### Inferences
- Baileys-based paths (NanoClaw `/add-whatsapp`, Hermes, OpenClaw) share the same ban exposure; a dedicated spare number limits damage. Rests on the Hermes page.

### Gaps
- Primary WhatsApp Business Solution Terms text not opened; the AI Provider scope (primary vs incidental, single-user private bot) is unsettled.
- No community "claude-code-slack bot" project was opened and vetted; a zeroclaw issue (task runner with Slack progress and SSH/tmux handoff) was in a search excerpt only.

## 4. Anthropic terms

### Takeaway
The legal page tells developers building products "including those using the Agent SDK" to use API keys and bars routing through Pro/Max credentials on behalf of users, but it expressly allows a user to sign in to the unmodified Claude Code binary with their own subscription. Driving the real `claude` binary yourself (Channels, Remote Control, `claude -p`) is the safe side; NanoClaw/OpenClaw-style Agent SDK harnesses on a Max token are the contested side. Help Center says (Oct 7 2026) SDK and third-party use still draws from subscription limits, and Max now carries API credits ($100/$200) usable with an API key. Confidence: medium (pages disagree in tone).

### Cited findings
- API-key rule for SDK developers — https://code.claude.com/docs/en/legal-and-compliance, opened 2026-10-16, WebFetch — Quote: "Developers building products or services that interact with Claude's capabilities, including those using the Agent SDK, should use API key authentication"
- Same page, no third-party routing — Quote: "Anthropic does not permit third-party developers to offer Claude.ai login into their own applications, or to route requests through Free, Pro, or Max plan credentials on behalf of their users."
- Same page, own use of unmodified binary allowed — Quote: "Nor does it prevent an end user from signing in to the unmodified Claude Code binary with their own Claude subscription"
- Same page, enforcement without notice — Quote: "Anthropic reserves the right to take measures to enforce these restrictions and may do so without prior notice."
- Same page, usage limits assumption — Quote: "Advertised usage limits for Pro and Max plans assume ordinary, individual usage of Claude Code and the Agent SDK."
- Consumer Terms automation clause — https://www.anthropic.com/legal/consumer-terms, opened 2026-10-16, WebFetch — Quote: "Except when you are accessing our Services via an Anthropic API Key or where we otherwise explicitly permit it"
- Consumer Terms credential sharing — same page — Quote: "You may not share your Account login information, Anthropic API key, or Account credentials with anyone else."
- Help Center (updated 2026-10-07): SDK, `claude -p` and third-party apps still use subscription limits — https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan, opened 2026-10-16, WebFetch — Quote: "You can still use the Claude Agent SDK, claude -p, and third-party apps with your subscription limits."
- Max now includes monthly API credits for the Agent SDK — same page — Quote: "Claude Max and Team plans now include monthly API credits"
- Credits: Max 5x $100, Max 20x $200; apply only with an API key; not to interactive Claude Code — https://support.claude.com/en/articles/17154008-monthly-api-credits-for-max-and-team-plans, opened 2026-10-16, WebFetch — Quote: "API credits cover `claude -p` and the Claude Agent SDK when you run them yourself with an API key."

### Contradictions
- Legal page: SDK developers "should use API key authentication" and Anthropic does not permit routing via Pro/Max credentials for users — https://code.claude.com/docs/en/legal-and-compliance; Help Center (2026-10-07): "You can still use the Claude Agent SDK ... with your subscription limits" — https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan. The legal clause targets third parties serving other users; a single owner using his own plan is not addressed directly for a bridge. Settling needs written confirmation from Anthropic (contact sales line on the legal page) before relying on it.
- Press/search excerpts report an April 2026 ban on OpenClaw with subscriptions, then reversal, then a June credit-pool pause (not opened as primary; pcmag, oflight). The Help Center page opened here shows only the June pause and Oct 7 update. Policy has reversed repeatedly in 2026.

### Inferences
- John as sole user with his own token sits in the "end user" carve-out only when the binary is the unmodified Claude Code binary; NanoClaw runs the Agent SDK, which the page lists on the API-key side. Lower risk: Channels or Remote Control (real `claude`), or NanoClaw/SDK with an API key funded by Max credits ($100 or $200 a month). Rests on the legal page and credits page.
- Max credits do not cover interactive Claude Code, so an overnight `claude -p` on login still uses plan limits; only SDK on API key uses credits.

### Gaps
- Exact consumer-terms sentence beyond the quoted fragment (bot/script wording) was truncated by the fetcher.
- No Anthropic statement found on a personal-use chat bridge specifically.

## 5. What John can do from his phone, per option

### Takeaway
Remote Control is the full phone cockpit (live view, approvals, files/photos, push); Channels via Telegram adds chat-style tasks with approvals relayed; NanoClaw gives WhatsApp/Slack chat with its own approval cards and scheduled reports but for its own agent. Slack native is for GitHub cloud tasks only. Confidence: medium.

### Cited findings
- Remote Control: use local environment remotely, subagent and workflow progress in sync, send files from phone — https://code.claude.com/docs/en/remote-control, opened 2026-10-16 — Quote: "the conversation and the progress of subagents and dynamic workflows stay in sync across all connected devices"
- Channels: approvals from phone — https://code.claude.com/docs/en/channels — Quote: "Channel servers that declare the permission relay capability can forward these prompts to you so you can approve or deny remotely."
- Channels: chat answers from phone, work on own machine — same page — Quote: "ask Claude something from your phone via Telegram, Discord, or iMessage, and the answer comes back in the same chat while the work runs on your machine"
- Claude in Slack: progress posts, summary, buttons — https://code.claude.com/docs/en/slack — Quote: "Claude posts status updates to your Slack thread as work progresses"
- NanoClaw: scheduled tasks with optional script gates — README.md (commit 2105169) — Quote: "recurring jobs executed by the agent, with optional script gates that avoid waking it when there is no work"
- NanoClaw approvals via chat cards: file `src/gateway-approval-presentation.ts` exists (listing); behaviour not read, see Gaps.

### Contradictions
- None found.

### Inferences
- Morning report: the engineer can push it via a Channels reply (Telegram) or a NanoClaw scheduled task; Remote Control gives push notifications, not a report. Slack native cannot, for a non-GitHub task. Rests on the findings above.
- Recommended shape (mine): Remote Control server mode plus Telegram channel on the VPS session for John; skip NanoClaw unless he insists on WhatsApp/Slack as the primary UI, then run it separate with an API key, Slack not WhatsApp-Baileys.

### Gaps
- Not tested: whether Telegram channel plus Remote Control can attach to one session; Slack custom channel; NanoClaw approval card flow on a phone.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| NanoClaw (update) | https://github.com/nanocoai/nanoclaw | Container-per-agent assistant on Agent SDK; WhatsApp (Baileys/Cloud API), Slack, Telegram skills; release 2026.10.0; MIT; CVE-2026-56402 reported | VM, Docker | 2026-10-16 | Not the best remote for the engineer; separate agent, Agent SDK on Max token is policy-contested; use only if WhatsApp/Slack UI is a must, with API key |
| Claude Code Channels (update) | https://code.claude.com/docs/en/channels | Telegram, Discord, iMessage into running local session; permission relay | VM/host | 2026-10-16 | Use Telegram for chat control and approvals; no Slack/WhatsApp |
| Remote Control (update) | https://code.claude.com/docs/en/remote-control | Phone/web view of local session; server mode; push; subscription login only | VM/host | 2026-10-16 | Use as the main phone cockpit; 10-min offline limit; not with setup-token |
| Claude Code in Slack / Claude Tag | https://code.claude.com/docs/en/slack | @Claude starts cloud session on GitHub repo; channels only | Anthropic cloud | 2026-10-16 | Skip for the VPS engineer; fine for GitHub-only tasks |
| Hermes Agent WhatsApp (Baileys) page | https://hermes-agent.nousresearch.com/docs/user-guide/messaging/whatsapp | Baileys bridge with stated ban risk | VPS | 2026-10-16 | Evidence for ban risk; skip as host |
| Monthly API credits for Max | https://support.claude.com/en/articles/17154008-monthly-api-credits-for-max-and-team-plans | $100/$200 a month API credit for SDK/API with Console key | Anthropic billing | 2026-10-16 | Use if running any Agent SDK bridge |
