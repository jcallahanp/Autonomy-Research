# Approval batches, fatigue and human-in-the-loop mechanisms

Brief: Design the batched approval request John receives and pick the mechanism that carries it, with evidence on what reduces approval fatigue.
Run: research/runs/engineer-human-loop/PLAN.md

## Q1 Evidence on fatigue and what reduces it

### Takeaway
Approval fatigue is measured and large: Anthropic's own telemetry shows about 93% of permission prompts approved, and warning-habituation research shows attention drops after the second exposure. What works is fewer prompts (boundaries, tiers, auto-handled low risk) plus varying the prompt form; reducing alert counts alone did not raise acceptance in clinical alert studies. Confidence: high on the problem, medium on which remedy is best for a single user.

### Cited findings
- Anthropic telemetry: users approved roughly 93% of prompts; more approvals means less attention per approval (2026-05-25 post) — https://www.anthropic.com/engineering/how-we-contain-claude, opened 2026-10-16, WebFetch — Quote: "Our telemetry showed users approved roughly 93% of permission prompts."
- Sandboxing, a boundary instead of per-action prompts, cut prompts 84% — same URL, opened 2026-10-16, WebFetch — Quote: "an 84% reduction in permission prompts"
- Experienced users auto-approve about twice as often as new users (they supervise only when it goes off track) — same URL — Quote: "experienced users auto-approve roughly twice as often as new users"
- Auto mode (classifier on Sonnet 4.6) exists to reduce fatigue: Anthropic defines approval fatigue and publishes 0.4% false positive and 17% miss on real overeager actions for the full pipeline; low-risk actions skip the classifier — https://www.anthropic.com/engineering/claude-code-auto-mode, opened 2026-10-16, WebFetch — Quote: "approval fatigue, where people stop paying close attention to what they're approving"
- Auto mode miss rate stated as a footnote caveat: one layer inside a sandbox, not a substitute — https://www.anthropic.com/engineering/how-we-contain-claude — Quote: "~17% of overeager actions get through"
- Security-warning habituation: attention falls sharply after the second exposure; partial recovery overnight; a polymorphic (changing-appearance) warning resists habituation, and field adherence stayed higher over 3 weeks — https://dl.acm.org/doi/10.25300/MISQ/2018/14124 (abstract) and https://doi.org/10.1145/3025453.3025896, both opened 2026-10-16 via Exa search result pages (abstract text only, not full paper) — Quote: "polymorphic warnings can substantially improve adherence."
- Habituation is neural, not carelessness — https://doi.org/10.1145/3025453.3025896 — Quote: "the root cause of habituation is an obligatory neurobiological response, rather than willful carelessness on the part of users."
- Clinical alerts: pooled override of drug-interaction alerts about 80% (55-96% per study); mitigation strategies were severity tiering and context — https://doi.org/10.2196/preprints.88578 (preprint, 2025-11-28) — Quote: "The overall drug-drug interaction alert override rate was 79.8%"
- Cutting alert volume to only important ones did not by itself fix acceptance; adding an authentication step raised workload — https://journals.sagepub.com/doi/10.1177/14604582241263242, 2024 — Quote: "the number of alerts decreased significantly, although the acceptance of these alerts did not increase significantly"
- Measurement advice: define fatigue as a sustained fall in appropriate response from a baseline — https://academic.oup.com/jamia/article/33/8/1523/8684938 (2026) — Quote: "use a significant, sustained decrease in appropriate alert response rates from an established baseline as a measure of alert fatigue."

(The last five came from search-result pages that I read as text through Exa; they are abstracts, not full-paper reads.)

### Contradictions
- Alert-volume reduction is the standard remedy — https://doi.org/10.2196/preprints.88578 (tailoring by severity); but the meta-analysis found acceptance stayed low after volume dropped — https://journals.sagepub.com/doi/10.1177/14604582241263242. Settled only by measuring John's own approve rate per tier after the first weeks.

### Inferences
- (Mine) A 93% approve rate means a yes-by-default batch is nearly always right; the design goal is to make the 7% visible (distinct form, hard gates), not to ask more often. Rests on the 93% and habituation findings.
- (Mine) Keep prompt count low and vary the form of the rare high-stakes ask (different header, a typed confirmation word instead of "1 yes") to counter habituation. Rests on the polymorphic-warning result; not tested for chat messages.
- (Mine) Track John's approve rate and response time per tier in the audit file; a sustained rise to ~100% or fall in response time is the fatigue signal, per the JAMIA measurement advice.

### Gaps
- No study on batched approvals for AI agents specifically; no data on John's behaviour.
- Auto mode and sandbox settings belong to the permission-modes facet.

## Q2 Batch design

### Takeaway
Ask immediately only for hard gates (spend, delete, publish/submit, anything irreversible or external); queue everything else as one numbered digest with a recommended default per line, expiring to a safe state (do not proceed with risky defaults; proceed with reversible ones). Renovate and Dependabot show the proven pattern: auto-handle low risk, put medium risk behind a visible approval list, group updates. Confidence: medium (pattern evidence is from dependency tools, design is inferred).

### Cited findings
- Renovate dashboard: approval for major updates via a checkbox list; the docs prefer it to disabling updates because pending work stays visible — https://docs.renovatebot.com/key-concepts/dashboard/, opened 2026-10-16, WebFetch — Quote: "you can fully see what's pending on the dashboard, instead of updates being totally invisible."
- Renovate: security fixes bypass the approval queue — same URL — Quote: "But vulnerability remediation PRs will still get created immediately without requiring approval."
- Dependabot grouping and cap: related updates combine into one PR, and a default cap of five open PRs stops pile-up — https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file, opened 2026-10-16, WebFetch — Quote: "All updates for dependencies that match a rule are combined in a single pull request."
- Dependabot cap — same URL — Quote: "no further pull requests are raised until some of those open requests are merged or closed."
- Claude Code's remote prompts have no timeout: permission prompts stay open until answered; other forwarded dialogs expire after five minutes to a no-action default — https://code.claude.com/docs/en/remote-control, opened 2026-10-16, WebFetch (saved page, grep) — Quote: "Claude Code keeps permission prompts and `AskUserQuestion` questions open until you answer them."
- Existing protocol design already has the shape: numbered lines with recommended default and reply token, pushed in one Telegram message at most 4096 characters — /home/user/Autonomy-Research/research/runs/engineer-protocol/notes/observability.md:87 — Quote: "Approvals needed: one numbered line per decision request, each with a recommended default and the reply token (`1 yes`)"
- n8n's approval node can auto-resume after a limit — https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-langchain.chat (via Exa search result text) — Quote: "Limit Wait Time: Whether the workflow automatically resumes execution after a specified time limit."

### Contradictions
- None found.

### Inferences
- (Mine) Proposed format (plain text, fits 4096 chars), sent at the morning report and at most one more digest per day:
  `DECISIONS (3)  reply "1 y 2 n 3 y" or "all y"` then lines `1. [reversible] Use Supabase RLS template A (default: yes) - why in one clause - file link`. Each line: id, tier tag, one-sentence ask, default, consequence of waiting, link to detail. Hard gates are never in "all y": they need their own message and a typed word (`CONFIRM 4 SPEND $12`).
- (Mine) Tiers: T0 auto (in repo, reversible, tests pass; log only); T1 batched digest with default, expires to the default after 24h only if the default is reversible and the task is parked otherwise; T2 hard gate (money, delete data, store submission, send external mail, secrets): immediate message, no timeout-default, task parked, other tasks continue. Rests on Renovate (security vs approval queue) and Anthropic's 93% data.
- (Mine) On timeout, pause that item and move to other work; never proceed on a risky default. Escalate by one reminder after 12h and again in the next morning report, never repeated pings (habituation).
- (Mine) Audit trail: the supervisor appends each ask and answer to `decisions/approvals.jsonl` (id, tier, text hash, default, reply, sender id, Telegram message id, timestamps) and commits it; Dependabot-style cap on open T1 items (for example 5) forces the engineer to resolve or merge asks.
- (Mine) Free-text replies are parsed by deterministic code, not by the model; unknown formats get a "didn't understand, resend" reply and never count as approval.

### Gaps
- Change-advisory-board practice (ITIL) not opened. HumanLayer's format could not be read (repo deprecated).
- Timeout lengths are judgement; spike with John's real response times.

## Q3 Mechanisms compared

### Takeaway
For one user on a machine he controls: Claude Code's own permission relay over Channels (Telegram) is the lowest-effort carrier for live tool-use prompts and has a built-in sender allowlist; the batched digest is better carried by the supervisor's own plain Telegram bot (one HTTPS call out, long-poll in, allowlist on from.id). LangGraph, n8n and Slack add a second runtime for no gain. HumanLayer's repo is deprecated. SMS costs little but is the weakest on identity and reply parsing. Confidence: medium-high.

### Cited findings
- Channels permission relay: both terminal and phone stay live, first answer wins; request ID is five letters; reply must match `yes <id>`; wrong ID dropped silently — https://code.claude.com/docs/en/channels-reference, opened 2026-10-16, WebFetch — Quote: "Both stay live: you can answer in the terminal or on your phone, and Claude Code applies whichever answer arrives first and closes the other."
- Relay covers tool-use only, not trust or MCP consent dialogs — same URL — Quote: "Project trust and MCP server consent dialogs don't relay; those only appear in the local terminal."
- Sender allowlist and spoofing: allowlist gates relay too; pairing bootstraps it — https://code.claude.com/docs/en/channels, opened 2026-10-16, WebFetch — Quote: "Anyone who can reply through the channel can approve or deny tool use in your session, so only allowlist senders you trust with that authority."
- Channels need a running local session and are research preview; Telegram plugin polls, no URL to expose — same URL — Quote: "Events only arrive while the session is open, so for an always-on setup you run Claude in a background process or persistent terminal."
- Channels in `-p` mode disable interactive tools — same URL — Quote: "tools that need terminal input, such as multiple-choice questions and plan mode approval, are disabled so the session never stalls waiting for input."
- Remote Control push for permission prompts is a setting; server mode gives up after roughly 10 minutes offline — https://code.claude.com/docs/en/remote-control, opened 2026-10-16, WebFetch (saved page) — Quote: "Claude Code gives up after roughly 10 minutes and the `claude remote-control` process exits."
- Remote Control push setting — same URL — Quote: "enable **Push when actions required** for permission prompts and questions"
- Telegram Bot API: long polling and webhook secret token exist; sender is the `from` field — https://core.telegram.org/bots/api, opened 2026-10-16, WebFetch (first 100k of 582k chars) — Quote: "A secret token to be sent in a header “X-Telegram-Bot-Api-Secret-Token” in every webhook request"
- LangGraph interrupts need a checkpointer, resume on the same thread id, and re-run the node from its start on resume — https://docs.langchain.com/oss/python/langgraph/interrupts, opened 2026-10-16, WebFetch — Quote: "The node restarts from the beginning of the node where the interrupt was called when resumed"
- HumanLayer repo is deprecated — https://github.com/humanlayer/humanlayer, opened 2026-10-16, WebFetch — Quote: "the code here is pretty much all deprecated."
- n8n human review: approval request via Slack, Telegram or chat for a chosen tool, approve/deny — https://docs.n8n.io/build/integrate-ai/ai-examples/human-in-the-loop-for-tools (Exa search text) — Quote: "The workflow pauses and sends an approval request through your configured channel (such as Slack, Telegram, or the n8n Chat interface)."
- n8n Telegram in-chat approval buttons are gated by a feature flag and need a public HTTPS instance — https://github.com/n8n-io/n8n/issues/34009 (Exa search text) — Quote: "Gated behind the `ENHANCED_HITL_TELEGRAM` PostHog flag (added in ENT-159), off by default."
- Twilio US SMS: $0.0083 per segment plus carrier fees, long code $1.15/month, A2P 10DLC registration required — https://www.twilio.com/en-us/sms/pricing/us, opened 2026-10-16, WebFetch — Quote: "$0.0083 per 160-character segment across long codes, toll-free numbers, and short codes."
- Twilio registration — same URL — Quote: "US A2P 10DLC are subject to registration"

### Contradictions
- None found.

### Inferences
- (Mine) Cost: Telegram free; SMS at a few digests a day is cents per month, but the registration step is real work for a personal number and the amount of the onboarding fee was not on the page.
- (Mine) Spoofing: Telegram replies carry a user id that Telegram assigns, checked against an allowlist; SMS sender numbers are weaker evidence (spoofing risk from general knowledge, not sourced here) and Twilio webhooks need signature checks and a public URL. Telegram long polling needs no public URL.
- (Mine) OpenClaw, Slack interactive messages: not re-researched; OpenClaw already rejected as host in the registry; Slack needs an app plus public endpoint or Socket Mode, no benefit over Telegram for one user.
- (Mine) Two paths, one bot decision: Channels' Telegram plugin owns the bot token's polling, so a second poller on the same bot would conflict (Telegram allows one getUpdates consumer; not verified here). Use two separate bots, or let the supervisor send digests via sendMessage only and read replies as Channel events. Spike.

### Gaps
- Slack interactive messages, OpenClaw messaging surfaces, Twilio onboarding fee: not opened.
- HumanLayer's new product (humanlayer.com) not opened.

## Q4 Telegram plus Remote Control: confirm or challenge; SMS

### Takeaway
Confirmed with two amendments. Telegram (Channels) for live prompts and the digest, Remote Control only as the phone view and fallback, because its server mode dies after about 10 minutes offline and permission prompts stay open indefinitely (a stalled session, not a safe default). SMS is a cheap fallback for a single "stuck" alert, not the approval path: weaker sender identity, no buttons, registration overhead. Confidence: medium.

### Cited findings
- See Q3 for the Channels, Remote Control, Twilio and Telegram quotes. Additional: both unattended sessions stall at a prompt until answered — https://code.claude.com/docs/en/channels, opened 2026-10-16, WebFetch — Quote: "If Claude hits a permission prompt while you're away from the terminal, the session pauses until you respond."

### Contradictions
- None found.

### Inferences
- (Mine) Amendment 1: do not rely on live relay for the overnight run. A stalled prompt blocks the whole session; with the 93% approve rate and a boundary (sandbox, allow rules, deny rules) the overnight run should hit few prompts, park T2 items in the digest, and keep working. Relay is for daytime.
- (Mine) Amendment 2: the digest is supervisor-owned (file plus Telegram message), because Channels relay covers only tool-use prompts, not product decisions like "pick design A".
- (Mine) SMS as John's first idea: keep as optional dead-man alert via Twilio only if Telegram is unreachable; defer.

### Gaps
- Whether the supervisor and the Telegram channel plugin can share one bot; whether relay works under a background tmux session on the VM: spike.

## Recommendation, alternatives, rejections, spikes
- Recommendation: tiered batching with the supervisor-owned digest in Telegram (numbered lines, defaults, `all y`, typed confirm for hard gates, allowlist on sender id, JSONL audit in repo); Claude Code Channels (Telegram) permission relay for live tool prompts; Remote Control as the phone window.
- Alternatives: n8n Telegram send-and-wait (only if n8n is already run), Slack app, Twilio SMS fallback.
- Rejected: HumanLayer (repo deprecated), LangGraph interrupts (second runtime, checkpointer, replay caveats), OpenClaw as a channel host (registry), SMS as primary.
- Spike: (1) relay under a headless tmux session with the Telegram plugin; (2) one bot shared between plugin and supervisor; (3) parser for `1 y 2 n`; (4) John's reply latency to set timeouts; (5) what a stalled prompt costs overnight.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Channels permission relay (Telegram plugin) | https://code.claude.com/docs/en/channels-reference | Forwards tool-use prompts to chat, `yes <id>` verdict, first answer wins, sender allowlist | John's machine/VM | 2026-10-16 | Use for live prompts; not for overnight reliance |
| Supervisor Telegram digest (plain bot) | https://core.telegram.org/bots/api | sendMessage out, getUpdates long poll in, allowlist on from.id | supervisor | 2026-10-16 | Use for batched digest |
| LangGraph interrupt/Command(resume) | https://docs.langchain.com/oss/python/langgraph/interrupts | Pause graph state, resume with value; needs checkpointer | Python | 2026-10-16 | Skip; second runtime |
| HumanLayer | https://github.com/humanlayer/humanlayer | Human approval SDK; repo says code is deprecated | - | 2026-10-16 | Reject |
| n8n human review / Send and Wait | https://docs.n8n.io/build/integrate-ai/ai-examples/human-in-the-loop-for-tools | Approval via Slack/Telegram nodes, Limit Wait Time | n8n | 2026-10-16 (search text) | Alternative if n8n already runs |
| Twilio SMS | https://www.twilio.com/en-us/sms/pricing/us | SMS at $0.0083/segment, 10DLC registration | hosted, paid | 2026-10-16 | Fallback alert only |
| Renovate Dependency Dashboard | https://docs.renovatebot.com/key-concepts/dashboard/ | Checkbox approval queue | hosted/self | 2026-10-16 | Pattern reference |
| Dependabot grouped updates | https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file | Group PRs, cap open PRs | GitHub | 2026-10-16 | Pattern reference |
