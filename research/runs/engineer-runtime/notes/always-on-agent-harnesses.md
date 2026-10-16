# Always-on agent harnesses as hosts (OpenClaw and its direction)

Brief: Survey OpenClaw and comparable always-on personal-agent harnesses as hosts for Claude Code (hosting/runtime angle only), and recommend what they add over Claude Code's own features.
Run: research/runs/engineer-runtime/PLAN.md

Clones read 2026-10-16 (read-only, mktemp): openclaw/openclaw commit ca009ba036a80172885b60feb7dcc4f0920744e3; NousResearch/hermes-agent 9c002cb941de1e1708294d0cd58e060b6a417b5e; NanoClaw (qwibitai/nanoclaw, README links nanocoai/nanoclaw) 2105169d8f7f017cd1ba3222cbf9708273fa1a3b. OR = https://github.com/openclaw/openclaw.

## What is OpenClaw and how does it run?

### Takeaway
OpenClaw (earlier Clawdbot, then Moltbot, renamed after an Anthropic trademark request; launched 2025 by Peter Steinberger) is an MIT-licensed, Node.js, self-hosted always-on gateway daemon that connects 20+ chat channels (Slack, Telegram, WhatsApp, iMessage, Discord, Teams, Signal...) to a model/harness of your choice, including Claude Code via a `claude-cli` backend. It is very actively maintained (commit on the day of reading, version 2026.10.4) but has a heavy security record (255+ advisories, ClawHub malware). Confidence: high on what it is and licence; medium on incident counts (secondary sources).

### Cited findings
- It is an open-source assistant on your own computer reached via many chat channels; Gateway runs it; models/harnesses are swappable plugins — OR README.md:~20 (commit ca009ba), read 2026-10-16, git clone + grep — Quote: "OpenClaw is an open-source AI assistant that runs on your own computer and meets you in the channels you already use: Discord, iMessage, Slack, Teams, Telegram, WhatsApp, and 20+ more"
- Install is a daemon via onboarding wizard (curl|bash installer, npm global, Docker, Nix) — OR README.md "Quick start" (commit ca009ba), read 2026-10-16 — Quote: "openclaw onboard --install-daemon"
- Licence MIT, held by "OpenClaw Foundation"; package version 2026.10.4; HEAD commit dated 2026-10-16 (calendar-versioned, daily releases) — OR LICENSE:1-3, package.json:3 (commit ca009ba) — Quote: "Copyright (c) 2026 OpenClaw Foundation"
- Name history and launch: Clawdbot -> Moltbot (Anthropic name request) -> OpenClaw end Jan 2026 — https://www.infosecurity-magazine.com/news/malicious-crypto-trading-skills/, opened 2026-10-16, Parallel fetch — Quote: "Launched in 2025 by Peter Steinberger as Clawdbot, the project first rebranded to Moltbot after Anthropic requested a name change and rebranded again to OpenClaw at the end of January 2026."
- Threat model: single trusted operator per gateway, not multi-tenant — OR SECURITY.md:5 (commit ca009ba) — Quote: "OpenClaw is local-first agent infrastructure for trusted operators; it is not designed as a shared multi-tenant boundary between adversarial users on one gateway."
- SECURITY.md treats prompt injection alone and local shell as non-vulnerabilities — OR SECURITY.md:52-53 — Quote: "Prompt injection without a policy, auth, approval, sandbox, or tool-boundary bypass."
- Advisory volume (IBM X-Force, dated 2026-10-13) — https://www.ibm.com/think/x-force/what-openclaw-reveals-about-agentic-ai-security-risks, opened 2026-10-16 — Quote: "OpenClaw has already published over 255 GitHub Security Advisories."
- ClawHub supply-chain campaign "ClawHavoc" — same IBM page — Quote: "Attackers uploaded over 1,100 malicious skills to ClawHub, many masquerading as productivity, crypto or coding tools."
- Early count of malicious skills (Feb 2026) — Infosecurity page above — Quote: "McCarty found 386 malicious skills published on ClawHub, a skill repository for OpenClaw assistants."

### Contradictions
- Malicious-skill counts differ by date and source: 386 (McCarty, 2026-02) vs "over 1,100" (IBM, 2026-10) vs 341 in a Hacker News headline URL cited by IBM. Same campaign, growing counts over time; not a true disagreement but do not quote one number as final.

### Inferences
- OpenClaw is the most capable and most attacked option; its own SECURITY.md says tool power given to a trusted operator is intentional, so safety rests on the host boundary you build, not on OpenClaw (SECURITY.md:5, 53).

### Gaps
- CVE-2026-25253 (one-click RCE), ClawJacked, CVE-2026-32302 details came only from search snippets (cve.org, openclawlaunch.com, NVD); not opened, so not cited. GitHub advisories page not opened.
- Exact star count and contributors not retrieved.

## Comparable harnesses

### Takeaway
Two credible comparables: NanoClaw (small TypeScript codebase, each agent in a Docker container, runs Claude Code natively via the Claude Agent SDK) and Hermes Agent by Nous Research (MIT, Python, self-improving memory and cron, seven execution backends, model-agnostic, not Claude Code-centric). NanoClaw has the safest isolation model and is Claude-native; OpenClaw has the widest breadth. Confidence: medium (README claims, not tested).

### Cited findings
- NanoClaw design motive and isolation vs OpenClaw — NanoClaw README.md:36-38 (commit 2105169), read 2026-10-16 — Quote: "Agents run in their own Linux containers with filesystem isolation, not merely behind permission checks."
- NanoClaw bash safety and credential gateway — NanoClaw README.md:77, 97 — Quote: "agents never hold raw API keys. Outbound requests route through a credential gateway that injects credentials at request time"
- NanoClaw licence MIT, 2026 — NanoClaw LICENSE:1-3 — Quote: "MIT License"
- Hermes Agent: gateway on Telegram/Discord/Slack/WhatsApp/Signal, cron, seven terminal backends — Hermes README.md:25-29 (commit 9c002cb), read 2026-10-16 — Quote: "Seven terminal backends — local, Docker, SSH, Singularity, Modal, Daytona, and Vercel Sandbox."
- Hermes scheduler — Hermes README.md:27 — Quote: "Built-in cron scheduler with delivery to any platform."
- Hermes licence MIT (2025 Nous Research), HEAD dated 2026-10-16 — Hermes LICENSE:1-3 — Quote: "Copyright (c) 2025 Nous Research"
- Claude Code itself now has first-party messaging: Channels (Telegram, Discord, iMessage; research preview) — https://code.claude.com/docs/en/channels, opened 2026-10-16, Parallel fetch — Quote: "Telegram, Discord, and iMessage are included in the research preview."

### Contradictions
- Third-party blog (remoteopenclaw.com, not opened) lists Claude Code as having "No messaging channel integrations"; Anthropic's own docs (above) show Channels. The blog is stale or wrong. Not cited beyond this.

### Inferences
- Comparison is README-level only; I did not test any of the three, so capability ranking is a judgement from feature lists (breadth: OpenClaw > Hermes > NanoClaw; isolation: NanoClaw > Hermes(Docker backend) > OpenClaw(sandbox off by default); Claude Code fit: NanoClaw > OpenClaw > Hermes).
- NanoClaw maintenance looks active (commit 2026-10-16) but the project is young, single-maintainer-led (inference from LICENSE holder "Gavriel"); bus factor unverified.

### Gaps
- Star counts, security advisory history, and incident reports for NanoClaw and Hermes not searched.
- Other harnesses (e.g. NemoClaw, AutoGPT-style) seen only as names in blog listings; not evaluated.

## Hosting or wrapping Claude Code

### Takeaway
OpenClaw documents two ways: (1) `claude-cli` CLI backend, where the gateway runs Claude Code (`claude -p`-style) as the model runtime and exposes gateway tools via a loopback MCP bridge; (2) ACP, where Claude Code runs as a chat-bound harness session with resume and background-task tracking. Claude Code can also connect inward as an MCP client with `openclaw mcp serve`. NanoClaw instead embeds Claude Code via the Agent SDK inside a container. Confidence: high (read in source docs).

### Cited findings
- CLI backend runs Claude Code as the runtime — OR docs/gateway/cli-backends.md:9 (commit ca009ba), read 2026-10-16 — Quote: "OpenClaw can run agent turns through a local AI CLI, such as Claude Code or Gemini CLI, instead of calling the provider API itself"
- Tool access via MCP bridge — same file:11 — Quote: "A backend with `bundleMcp: true` receives Gateway tools through a loopback MCP bridge."
- Setup requires Claude Code installed on the gateway host — same file ~30 — Quote: "The gateway service must have the CLI on its `PATH`."
- ACP path for Claude Code — OR docs/tools/acp-agents.md:69-78 — Quote: "ACP Claude is a **harness session** with ACP controls, session resume, background-task tracking, and optional conversation/thread binding."
- ACP stack depth — same file:71-76 — Quote: "OpenClaw ACP session control plane. Official @openclaw/acpx runtime plugin. Claude ACP adapter. Claude-side runtime/session machinery."
- Reverse direction — same file:25 — Quote: "To let Codex or Claude Code connect as an external MCP client directly to existing OpenClaw channel conversations, use openclaw mcp serve instead of ACP."
- Claude Code native alternative for chat: allowlisted sender; permission relay means any allowlisted sender can approve tools — https://code.claude.com/docs/en/channels — Quote: "Anyone who can reply through the channel can approve or deny tool use in your session, so only allowlist senders you trust with that authority."
- Channels need the session kept running; unattended use needs bypass mode — same page — Quote: "For unattended use, `--dangerously-skip-permissions` bypasses most prompts, but only use it in environments you trust."
- Remote Control: local session, outbound-only, transcript stored at Anthropic — https://code.claude.com/docs/en/remote-control, opened 2026-10-16 — Quote: "Your local Claude Code session makes outbound HTTPS requests only and never opens inbound ports on your machine."
- Remote Control not usable with setup-token or custom base URL — same page — Quote: "These tokens can only make model requests, so they can't establish Remote Control sessions."
- Agent SDK embeds Claude Code (tools, hooks, subagents, MCP, permissions, sessions) in your own process — https://code.claude.com/docs/en/agent-sdk/overview, opened 2026-10-16 — Quote: "A library that runs the Claude Code binary, with Claude Code's capabilities, such as built-in tools, permissions, sessions, and hooks."
- Scheduling: cloud Routines, Desktop tasks, session-scoped /loop with 7-day expiry — https://code.claude.com/docs/en/scheduled-tasks, opened 2026-10-16 — Quote: "Recurring tasks automatically expire 7 days after creation."
- Billing/auth rule that matters for any harness: Anthropic's legal page — https://code.claude.com/docs/en/legal-and-compliance, opened 2026-10-16 — Quote: "Anthropic does not permit third-party developers to offer Claude.ai login into their own applications, or to route requests through Free, Pro, or Max plan credentials on behalf of their users."
- Agent SDK doc note — agent-sdk/overview page — Quote: "Unless previously approved, Anthropic does not allow third party developers to offer claude.ai login or rate limits for their products, including agents built on the Claude Agent SDK."
- OpenClaw's own current statement on subscription use (Oct 2026) — OR docs/providers/anthropic.md:281-288 — Quote: "Anthropic's June 15, 2026 support update paused the previously announced separate Agent SDK credit plan."
- Same section — Quote: "Subscription-plan Claude Agent SDK, `claude -p`, and third-party app usage still draw from the signed-in subscription's usage limits."

### Contradictions
- Subscription use via third-party harnesses: openclawlaunch.com (not opened, snippet) says Anthropic reversed an April 2026 ban in May 2026 with Agent SDK credits; OR docs/providers/anthropic.md:283 (opened) says the separate credit plan was paused 2026-06-15 and usage still draws from subscription limits; Anthropic's legal page (opened) forbids routing through plan credentials on behalf of users. A personal single-user run is arguably "ordinary individual usage", but the policy is in flux. Settle by checking Anthropic's current support article before committing; safest is an API key (the OpenClaw auth doc also calls an API key "the most predictable option").

### Inferences
- For a single user, OpenClaw's `claude-cli` backend keeps the real `claude` binary making the requests, which is the policy-safest harness path; hosts that call the API with a subscription token directly are the risky ones. This rests on the OpenClaw authentication doc line quoted in Gaps and the Anthropic legal page.
- Process model: gateway (Node daemon, always on) spawns Claude Code per turn/session; permission model is two-layered, OpenClaw tool policy plus Claude Code's own permissions, so approvals can be double-gated or silently bypassed depending on config (not tested).

### Gaps
- Whether Claude Code's own permission prompts surface cleanly through OpenClaw chat in the claude-cli backend: not found in docs I read.
- OpenClaw authentication.md quote about Claude CLI reuse being "sanctioned" (lines 48): grep output seen, not carried as a quote here to stay within word limits; claim rests on anthropic.md only.

## Sandboxing and public incidents

### Takeaway
OpenClaw sandboxing (Docker/Podman/SSH/OpenShell/Crabbox for tool execution) is OFF by default and self-described as imperfect; its docs advise a dedicated OS user, machine, VM or container and no personal accounts on the runtime. Public incidents: exposed instances (1,000+ found by scanners in Jan 2026), malicious ClawHub skills stealing keys, prompt-injection and web-hijack bugs. NanoClaw's container-per-agent is the stronger default. For John: run the whole stack in a dedicated VM with its own accounts and an API key with a spend cap. Confidence: medium-high.

### Cited findings
- Sandboxing off by default; gateway stays on host — OR docs/gateway/sandboxing.md:9 (commit ca009ba) — Quote: "Sandboxing is off by default and controlled by `agents.defaults.sandbox`"
- Self-assessment — same file:12 — Quote: "This is not a perfect security boundary, but it materially limits filesystem and process access when the model does something dumb."
- Backends and default — OR docs/gateway/sandboxing/modes-scope-and-backend.md:15-17 — Quote: "`off`, `non-main`, `all`"
- Dedicated machine/VM/user advice — OR docs/gateway/security/secrets-and-storage.md:17 — Quote: "Run it on a dedicated machine/VM/container, use a dedicated OS user + dedicated browser/profile/accounts, and do not sign that runtime into personal Apple/Google accounts"
- Defaults: loopback bind, pairing for unknown DMs; container images default exposed — OR docs/gateway/security/index.md:7 — Quote: "container images default to an exposed bind"
- Hardened baseline denies exec/fs/runtime tools — OR docs/gateway/security/hardened-baseline.md:~20 — Quote: "exec: { security: \"deny\", ask: \"always\" }"
- Claude Code permission modes still apply: some actions never auto-approve — channels page — Quote: "the actions no mode auto-approves still apply."

### Contradictions
- None found among opened sources.

### Inferences
- Because OpenClaw's own policy declares local shell and malicious-plugin-after-install out of scope (SECURITY.md:53, 55), John should treat ClawHub skills as untrusted code and install none without reading them.
- Sandbox-in-harness protects little if the host holds John's main accounts; the VM boundary matters more than OpenClaw's Docker sandbox.

### Gaps
- PointGuard, Palo Alto, Bitdefender, openclawlaunch.com pages seen only as search excerpts (dated 2026-10-09, 2026-01-29, 2026-02-05, 2026-08-12); not opened, so not cited.
- Not opened, search snippets only (uncited): nanoclaw.dev (Claude Agent SDK native, many channels); PointGuard (1,000+ exposed instances Jan 23-26 2026); Palo Alto (persistent-memory delayed injection); IBM-cited "lethal trifecta" wording from search excerpt; Bitdefender (do not run on company device).
- No public report found/checked of a Claude-Code-hosted-by-OpenClaw destructive incident; none searched specifically.

## What a harness adds over Claude Code native features; recommendation

### Takeaway
Claude Code alone now covers: remote steering (Remote Control, claude.ai/mobile), chat push (Channels for Telegram/Discord/iMessage, research preview), scheduling (Routines cloud, Desktop tasks, /loop), hooks, subagents, and a programmable Agent SDK. A harness adds: 20+ channel surface (Slack, WhatsApp, Signal, SMS-like), a persistent always-on daemon, cross-session memory and personal-assistant tooling, multi-model fallback, device nodes, and per-agent container sandboxes (NanoClaw). It does not add engineering capability. Recommendation: do NOT make OpenClaw the host. Primary: Claude Code in a dedicated VM, using Channels + Remote Control + Routines/Desktop tasks + Agent SDK for any custom daemon; if a messaging daemon beyond Telegram/Discord/iMessage is needed (Slack, WhatsApp), spike NanoClaw first (Claude Agent SDK, container per agent), OpenClaw second. Confidence: medium (based on docs and READMEs, no testing).

### Cited findings
- Claude Code first-party surfaces compared — https://code.claude.com/docs/en/channels "How channels compare" — Quote: "Push events from a chat app like Telegram or Discord, or your own server"  (remote-control page table, opened 2026-10-16)
- Channels are research preview with allowlisted plugins only — channels page — Quote: "During the preview, `--channels` only accepts plugins from an Anthropic-maintained allowlist"
- Channels need Anthropic auth, not Bedrock/Vertex/Foundry — channels page — Quote: "are not available on Amazon Bedrock, Google Cloud's Agent Platform, or Microsoft Foundry."
- Scheduled durable options — scheduled-tasks page — Quote: "For scheduling that survives independently of any session, use Routines to create a routine on the cloud, set up a Desktop scheduled task, or use GitHub Actions."
- Hermes adds learning loop/memory and cron — Hermes README.md:27 — Quote: "A closed learning loop"
- OpenClaw scale, risk: nearly half a million lines — NanoClaw README.md:36 (comparison claim by a competitor) — Quote: "OpenClaw has nearly half a million lines of code, 53 config files, and 70+ dependencies."

### Contradictions
- None beyond those already listed. The NanoClaw size figure is a competitor's claim; not independently counted.

### Inferences
- Outcome quality first: harness layers add attack surface and a second permission model without improving code quality; Claude Code's native stack already gives phone/chat control and scheduling. Effort second: Channels and Remote Control are minutes of setup; OpenClaw plus claude-cli adds a daemon to patch (daily releases, 255+ advisories). Cost: all free software; the real cost lever is auth (API key vs subscription limits).
- Where a harness is justified: need Slack/WhatsApp/Signal as a control channel, proactive messaging, or many always-on agents. Then NanoClaw (container isolation, Agent SDK) matches Claude Code better than OpenClaw; OpenClaw is the max-breadth option if John accepts the risks in the VM.
- Risks to state to John: indirect prompt injection from any inbound message; persistent memory poisoning; marketplace skills malware; exposed control UI; double permission model; Anthropic billing/policy churn for harness use; Remote Control stores transcripts at Anthropic; Channels permission relay lets any allowlisted sender approve tools.

### Spike list before building
1. Claude Code in a throwaway VM: `--channels plugin:telegram` with allowlist plus Remote Control; measure unattended stability, restart behaviour, and whether permission prompts stall.
2. Agent SDK daemon (small TS/Python service) triggered by webhook/cron with hooks as guardrails; compare with Routines.
3. NanoClaw in a VM with Slack or WhatsApp: check Claude Code works with API key through its credential gateway.
4. OpenClaw `claude-cli` backend in the same VM, `openclaw security audit`, sandbox mode `all`, no ClawHub skills; test whether Claude Code permission prompts reach chat.
5. Confirm current Anthropic billing rules for harness use (support article) before using a subscription.

### Gaps
- No hands-on test of any harness (rule: never install or run).
- Pricing: all candidates free/MIT; model cost not compared.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| OpenClaw | https://github.com/openclaw/openclaw | MIT Node gateway daemon, 20+ chat channels, drives Claude Code via claude-cli backend or ACP; install via curl script/npm/Docker | local/VM/VPS | 2026-10-16 | Fallback / only if breadth needed; 255+ advisories, sandbox off by default, run in dedicated VM only |
| NanoClaw | https://github.com/nanocoai/nanoclaw | Small TS assistant, Docker container per agent, Claude Agent SDK, credential gateway; install via nanoclaw.sh | local/VM, Docker | 2026-10-16 | Spike first if a messaging daemon is needed |
| Hermes Agent | https://github.com/NousResearch/hermes-agent | MIT Python agent with memory, cron, gateway, 7 execution backends; model-agnostic | local/VPS/serverless | 2026-10-16 | Skip as Claude Code host; not Claude-centric |
| Claude Code Channels | https://code.claude.com/docs/en/channels | First-party Telegram/Discord/iMessage push into a running session, sender allowlist | local CLI | 2026-10-16 | Use (research preview) |
| Claude Code Remote Control | https://code.claude.com/docs/en/remote-control | Drive local session from claude.ai/mobile, outbound-only | local CLI | 2026-10-16 | Use; needs full-scope login, api.anthropic.com |
| Claude Agent SDK | https://code.claude.com/docs/en/agent-sdk/overview | Embed Claude Code loop, hooks, MCP in own daemon | local/VM | 2026-10-16 | Use for custom always-on service; API key auth |
