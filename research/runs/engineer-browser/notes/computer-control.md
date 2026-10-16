# Full-machine and desktop control

Brief: Decide whether an autonomous Claude Code engineer needs full-machine control beyond a browser, and if so which option (computer use, OpenClaw direction, sandboxed desktops).
Run: research/runs/engineer-browser/PLAN.md

## Q1 Anthropic computer use (API tool, Claude Code, Desktop, benchmarks, cost)

### Takeaway
Computer use exists in three forms: the API toolset (`computer_toolset_20260801`, GA), a built-in `computer-use` MCP server in the Claude Code CLI (macOS only, Pro/Max, interactive only, not `-p`), and the Desktop app (macOS and Windows, app must be running). None of the Claude Code routes runs on a headless Linux VM or in a cloud session, so an unattended engineer cannot use the built-in feature as shipped. Anthropic itself ranks it last resort after MCP, Bash and Chrome. Benchmarks: Anthropic models self-report 81-85% on OSWorld-Verified; aggregators disagree on details. Confidence: high on docs, medium on scores (all self-reported, aggregator-sourced).

### Cited findings
- CLI computer use is macOS-only, research preview, Pro/Max only, interactive only — https://code.claude.com/docs/en/computer-use, opened 2026-10-16, WebFetch — Quote: "Computer use is a research preview on macOS that requires a Pro or Max plan. It is not available on Team or Enterprise plans. It requires an interactive session"
- Explicitly not available on Linux or with `-p` — same URL — Quote: "Computer use in the CLI is not available on Linux or Windows."
- Anthropic's own routing puts it last — same URL — Quote: "Computer use is the broadest and slowest, so Claude tries the most precise tool first"
- It runs on the real desktop, not a sandbox; one session at a time — same URL — Quote: "Unlike the sandboxed Bash tool, computer use runs on your actual desktop with access to the apps you approve."
- Guardrails: per-app approval, terminal excluded from screenshots, Esc abort, lock file — same URL — Quote: "Per-app approval: Claude can only control apps you've approved in the current session."
- Desktop app: macOS and Windows, app must be running; browsers are view-only, terminals/IDEs click-only — https://code.claude.com/docs/en/desktop, opened 2026-10-16, WebFetch — Quote: "Computer use is a research preview on macOS and Windows that requires a Pro or Max plan." and "View only | See the app in screenshots | Browsers, trading platforms"
- Desktop: Dispatch sessions can use it with 30-minute approvals; whether scheduled tasks can use it was not stated in the part read — same URL — Quote: "Dispatch-spawned Code sessions can use it too. App approvals in those sessions expire after 30 minutes and re-prompt"
- API tool: current version GA on Claude API, with the list of supporting models including claude-sonnet-5-5 and claude-haiku-5-5 — https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool, opened 2026-10-16, WebFetch — Quote: "Computer use is available on the Claude API and Google Cloud as the `computer_toolset_20260801` toolset."
- Cost driver: screenshot tokens — same URL — Quote: "Long agent loops accumulate screenshots quickly (roughly 1,000–1,800 input tokens each)."
- Anthropic's own security advice for the API tool: VM, no sensitive data, domain allowlist, human confirmation — same URL — Quote: "Using a dedicated virtual machine or container with minimal privileges to prevent direct system attacks or accidents."
- Same page admits injection risk persists — same URL — Quote: "In some circumstances, Claude will follow commands found in content even when they conflict with your instructions."
- OSWorld-Verified leaderboard (aggregator, all self-reported): top rows Qwen3.8-Max 86.1%, Claude Mythos 5 / Fable 5 85.0%, Opus 4.8 83.4%, Claude Sonnet 5 81.2%; best open weights MiMo-V2.6-Pro-RL 82.0% — https://leaderboard.steel.dev/leaderboards/osworld/, opened 2026-10-16, WebFetch — Quote: "Claude Sonnet 5 | 81.2% | 2026-06-30 | Yes, in the Claude Sonnet 5 system card" (fetch-tool table rendering, row text paraphrased by the fetch model; treat as medium confidence)
- Price per token is the only per-action cost; no per-action fee seen. Sonnet 5.5 listed at $2/$10 per million — https://www.vellum.ai/llm-leaderboard (seen only in Exa search result, not opened; see Gaps).

### Contradictions
- Sonnet 5.5 / Opus 5.5 OSWorld-Verified: benchgap lists Claude Sonnet 5.5 85.6% and Opus 5.5 85.2% as "estimated ± 6.5 pp, low confidence" (https://benchgap.net/b/osworld-verified/current, search result only), while the Steel page I opened lists no 5.5 entries and puts Sonnet 5 at 81.2%. Settle with the Sonnet 5.5 system card; not opened.
- Steel notes Anthropic changed its harness ("revised harness", zoom fix) so older and newer scores are "not directly comparable" (Steel search excerpt); do not compare 2025 scores (Sonnet 4.5 61.4%) with 2026 scores as trends.

### Inferences
- Inference: for a headless Linux VM engineer, built-in Claude Code computer use is unavailable; the only Anthropic route there is the API toolset driven from our own loop inside a VM, or a third-party MCP desktop driver (Q3).
- Inference: at roughly 1-1.8k tokens per screenshot and one screenshot per action, a 30-step GUI task costs about 30-55k input tokens plus growth from history, a few cents to tens of cents at Sonnet-class prices. Not measured; spike.
- Inference: 80%+ OSWorld means roughly one failure in five on generic desktop tasks, so every desktop step must be verified by a check outside the model.

### Gaps
- Per-action latency in seconds: no source found with numbers; Anthropic only says "slowest".
- Sonnet 5.5 / Opus 5.5 official OSWorld numbers: system card not opened.
- Computer use inside scheduled tasks: Desktop page chunk read did not say; the unread final 52k characters may.

## Q2 OpenClaw as a controller

### Takeaway
OpenClaw has a real `computer` tool (Peekaboo or CUA drivers; macOS, Windows, Linux, plus a managed Linux X11 desktop) and a managed Chrome/Brave profile plus a Chrome extension for signed-in tabs. But its MCP server for Claude Code exposes only channel conversations, not the computer or browser tools, so Claude Code cannot borrow OpenClaw's hands; the supported direction is the reverse (OpenClaw hosts Claude Code), which the runtime run already rejected. Over Claude Code plus a browser MCP it buys only: desktop control on Linux headless, chat-channel reach, and its CUA driver, all of which Cua Driver offers directly. Confidence: high (read source at commit 58d7e878).

### Cited findings
- The computer tool controls the Gateway desktop or a paired node's desktop with Peekaboo (default on macOS) or CUA — https://github.com/openclaw/openclaw docs/nodes/computer-use.md:11 (commit 58d7e878), read 2026-10-16, git clone — Quote: "Computer use lets an agent see and control the Gateway's own desktop or a paired node's desktop through one built-in `computer` tool."
- Windows/Linux support is experimental — docs/nodes/computer-use.md:21 — Quote: "Windows and Linux can use the optional, experimental `cua-computer` plugin, which calls the packaged CUA Driver SDK directly."
- Headless Linux has a managed desktop — docs/nodes/computer-use.md:44 — Quote: "On a headless Linux Gateway, enable the managed desktop."
- Needs a vision model and tool policy; Full profile does not grant computer permissions — docs/nodes/computer-use.md:30 — Quote: "Full tool selection does not grant computer-control permissions."
- Browser: separate agent-only Chromium profile, or attach to your real signed-in Chrome — docs/tools/browser.md:12-14 — Quote: "The built-in `user` profile attaches to your real signed-in Chrome session instead, via Chrome DevTools MCP."
- Chrome extension automates signed-in tabs — docs/tools/chrome-extension.md:9 — Quote: "The OpenClaw Chrome extension lets the browser tool automate eligible tabs in your signed-in Chrome profile."
- Connection to Claude Code: `openclaw mcp serve` exposes only channel conversations — docs/cli/mcp.md:25 — Quote: "Let an external MCP client read/send OpenClaw channel conversations | `openclaw mcp serve` | OpenClaw is the MCP server and exposes Gateway-backed conversations over stdio."
- The other direction (OpenClaw hosts Claude Code) is ACP / claude-cli — docs/tools/acp-agents.md:25 — Quote: "To let Codex or Claude Code connect as an external MCP client directly to existing OpenClaw channel conversations, use `openclaw mcp serve` instead of ACP."
- Maintenance: calendar-versioned, version 2026.10.4 — package.json:3 (commit 58d7e878) — Quote: "\"version\": \"2026.10.4\","
- Security posture and 255+ advisories, sandbox off by default: already established in research/findings/engineer-runtime.md (Q6, lines 340-390; IBM X-Force 2026-10-13 quote "OpenClaw has already published over 255 GitHub Security Advisories.").

### Contradictions
- None found.

### Inferences
- Inference: using OpenClaw only to get a `computer` tool means installing a half-million-line gateway (engineer-runtime.md H41) to reach CUA, which is available standalone. Reject as controller.
- Inference: the name "OpenClaw" as John's pointer means "maximum capability, cutting edge, agent that acts on the machine and in chat". The direct equivalents are Claude Code plus Cua Driver MCP (machine), Channels (chat), Claude in Chrome / Playwright (browser).

### Gaps
- Whether OpenClaw's `computer` tool can be exposed to an external MCP client through some plugin: not found in docs read; only grep of cli/mcp.md done.
- Security advisories specific to the computer tool: not searched individually.

## Q3 Other desktop agents and sandboxed desktops

### Takeaway
Best fit as a plug-in for Claude Code: Cua (Driver MIT, MCP, macOS/Windows/Linux, installer can add the MCP to Claude Code) for driving a machine or VM, and E2B Desktop (Apache-2.0 SDK, paid cloud sandboxes) or a self-hosted Docker XFCE desktop as the sandbox. Bytebot is archived; UI-TARS Desktop is a separate agent app with its own model, not a Claude Code tool; Agent S is a research framework (Apache-2.0) that works with Anthropic models; ChatGPT agent is a closed OpenAI product that cannot be driven from Claude Code. Confidence: medium (repo pages opened; no code run, no OSWorld numbers for these from primary reports).

### Cited findings
- Cua Driver: operates native apps and browsers on macOS, Windows, Linux via CLI, MCP or SDK — https://github.com/trycua/cua, opened 2026-10-16, WebFetch — Quote: "Give your agent tools to inspect and operate native desktop apps and browsers on macOS, Windows, and Linux."
- Licence split: MIT for everything but Spaces/Driver Bench; Spaces is FSL — same URL — Quote: "Everything outside Cua Spaces and Cua Driver Bench is MIT-licensed."
- Installer can register the MCP for Claude Code — same URL — Quote: "the cua MCP server into your AI coding agents (Claude Code, Codex, Cursor, and others)"
- Cua repo warns against its own older npm package — same URL — Quote: "Do not run it: it has known security issues."
- Cua sandboxes run local (gVisor, runc, QEMU, Lume) or cloud; Spaces are VMs on your Mac, machines you own or your own cloud account — https://cua.ai/ and https://cua.ai/docs/cua-sdk/concepts/how-sandboxes-work (content seen via Exa search result only; see Gaps).
- E2B Desktop: open-source Linux/Xfce virtual desktop for LLM computer use, Apache-2.0, 1.5k stars — https://github.com/e2b-dev/desktop, opened 2026-10-16, WebFetch — Quote: "E2B Desktop Sandbox is an open source secure virtual desktop ready for Computer Use."
- E2B Desktop pricing: not on the page — same URL; the page "doesn't mention E2B pricing" (fetch summary).
- Bytebot: archived — https://github.com/bytebot-ai/bytebot, opened 2026-10-16, WebFetch — Quote: "This repository was archived by the owner on Mar 7, 2026. It is now read-only."
- UI-TARS Desktop / Agent TARS: Apache-2.0 native GUI agent driven by UI-TARS and Seed models; newest news item 2025-11-05 — https://github.com/bytedance/UI-TARS-desktop, opened 2026-10-16, WebFetch — Quote: "This project is licensed under the Apache License 2.0."
- Agent S3: open-source framework, Apache-2.0, 72.6% OSWorld with best-of-N (Dec 2025 self-report); hosted successor Sai — https://github.com/simular-ai/Agent-S (Exa search result only, not opened; see Gaps).
- OpenAI: Operator folded into ChatGPT agent, which is itself retired — https://help.openai.com/en/articles/11752874-agent (Exa search result only) — Quote: "ChatGPT agent is no longer available. Use ChatGPT Work for longer, multi-step tasks"

### Contradictions
- Agent S3 score: Simular blog (2025-10-02) says 69.9% with bBoN while the GitHub README says 72.6% (Dec 2025 update); different dates, same system, not a true conflict. Both from search results only.

### Inferences
- Inference: for Claude Code the useful split is "driver" (Cua Driver MCP, Linux/Windows/macOS) versus "container" (E2B Desktop, a self-built Docker XFCE + noVNC image, or Cua Linux sandbox). Browser Use desktop, ChatGPT agent, UI-TARS, Agent S are alternative agents, which would duplicate the engine and so are rejected under "Claude Code is the engine".
- Inference: licence and cost: Cua Driver, E2B Desktop SDK and Agent S are free to self-host; E2B cloud sandboxes and Cua relay above free allowance are paid (prices not retrieved).

### Gaps
- Browser Use desktop product: not researched (no source opened).
- E2B pricing, Cua Pro/Teams pricing: not retrieved.
- Cua Driver Linux headless behaviour (needs a display, accessibility tree availability): not verified; spike.
- Primary OSWorld numbers for UI-TARS: not found on repo page.

## Q4 When does a task need the desktop? John's tasks

### Takeaway
A browser (Playwright / Chrome) suffices for Attio, Clay, n8n, Outreach UIs and probably the blood-work portal; API/MCP is better than any UI for Attio, Clay, n8n and Outreach (registry rows). Desktop control is only justified for: native apps and OS dialogs (file pickers outside the browser, OS permission prompts), phone-companion pairing (Withings, WHOOP), and Android emulators; and for Android builds the CLI (Gradle, adb) covers building and install, and the emulator UI needs GUI. Confidence: medium (reasoned from cited docs; no task tried).

### Cited findings
- Anthropic's own order of preference: MCP, Bash, Chrome, then computer use — https://code.claude.com/docs/en/computer-use, opened 2026-10-16, WebFetch — Quote: "Screen control is reserved for things nothing else can reach: native apps, simulators such as the iOS Simulator, and tools without an API."
- Documented use cases are native-app and simulator tests, not SaaS UIs — same URL — Quote: "Drive GUI-only tools: interact with design tools, hardware control panels, the iOS Simulator, or proprietary apps that have no CLI or API."
- Existing API/MCP routes for John's SaaS tools: research/tool-registry.md rows "Attio REST API + OpenAPI", "Attio MCP (official)", "Clay developer platform + CLI", "n8n public API", "Outreach REST API" (all verified 2026-10-16 in earlier runs).
- Browsers are view-only in Desktop computer use, so the desktop tool cannot type in a browser; browser work must go through a browser tool — https://code.claude.com/docs/en/desktop, WebFetch — Quote: "View only | See the app in screenshots | Browsers, trading platforms"

### Contradictions
- None found.

### Inferences
Task buckets (inference from the above):
- API or MCP first, no UI: Attio, Clay (Workflows), n8n (public API), Outreach (needs approval for app).
- Browser needed: Clay tables (Enterprise-only via API), Outreach UI when no API access, n8n editor views, any SaaS config not in API (Attio views/workflows); the blood-work portal (login, MFA, download of PDFs; browser download folder is a file-system matter, handled by Playwright download events).
- Desktop needed: Withings and WHOOP pairing (Bluetooth pairing via a phone app; no browser route; likely requires a physical phone, which neither Cua nor an emulator provides for BLE), Android emulator UI interaction, OS permission prompts, native file dialogs when a site opens an OS picker that a browser tool cannot reach (Playwright can set files directly).
- Android builds: Bash (Gradle, adb) covers build and install; emulator on a Linux VM needs KVM; GUI checks via screenshot (`adb exec-out screencap`) need no desktop control. Only flows needing tap-through use `adb input` or a mobile MCP.
So the engineer does not need general desktop control for the core job; add it as a spiked, optional capability for pairing and emulator tests.

### Gaps
- Whether Withings/WHOOP pairing can be done on an emulator (BLE) or needs a real phone: not researched.
- Blood-work portal's actual login/MFA behaviour: unknown to me.

## Q5 Safety: incidents and guardrails

### Takeaway
Full-machine agents have real incident history: file deletion by Claude Code sub-agents (Sept/Oct 2026), a Codex data-loss report, a Chrome-extension hijack, and a published exploit chain of a computer-use agent through ambient web content to RCE. Guardrails: VM isolation with minimal privileges, domain allowlist, no real credentials, human confirmation, per-app approval, deterministic gating. Confidence: medium-high (reports are first-person and uncorroborated, flagged).

### Cited findings
- Claude Code sub-agent `rm -rf` on a Windows home folder; deletion continued about 45 minutes after stop; issue open with no maintainer reply — https://github.com/anthropics/claude-code/issues/99198, opened 2026-10-16, WebFetch — Quote: "no protection that prevents such a command from reaching the home directory, and no reliable way to stop it once started."
- Separate first-person report (issue #97660, 27 Sept 2026) of an auto-mode sub-agent deleting the C: drive top-down, about 125 GB — https://nope.net/incidents/2026-claude-code-sub-agent-auto-mode-recursive-delete-wiped-windows-drive-root-about-125-gb-first-person (Exa search result only, not opened) — uncorroborated.
- Computer use agents: visual prompt injection and an end-to-end exploit of OpenAI Operator to RCE — https://arxiv.org/html/2507.05445 (Microsoft affiliation, 2025-07-07; Exa search result only, not opened) — Quote: "Existing sandboxes and DOM-level constraints offer little protection against behavioral hijacking through perception-level inputs."
- LayerX flaw in Claude's Chrome extension (IANS write-up, 2026-05-14), Exa search result only, not opened.
- Anthropic's recommended guardrails: see Q1 (VM, no sensitive data, allowlist, human confirmation).

### Contradictions
- None found.

### Inferences
- Inference: the engineer runs in a throwaway VM or container with no personal files, no saved logins beyond scoped ones, a domain allowlist, and the destructive-command guard from the Claude Code issue (protected-path hook) in place; any real desktop with John's accounts is out.
- Inference: do not use the Claude Code Desktop computer use on John's own laptop for unattended work: approvals expire, it needs the app open, and it can reach the real desktop.

### Gaps
- Several sources above were only seen as search results (nope.net, arXiv, IANS, benchgap, vellum, Agent S, ChatGPT agent help page); treat those findings as pointers until opened.
- OpenClaw exposed-instance counts: PointGuard snippet only (engineer-runtime.md gap).

## Recommendation
Recommended: no general desktop control in v1. Engineer = Claude Code + API/MCP first + a browser tool (other facet). Add desktop control only as an optional, spiked add-on in a disposable Linux VM or container: Cua Driver MCP (MIT, supports Claude Code, Linux/Windows/macOS), driven by Claude Code, with a protected-path hook and no personal data.
Alternatives: (1) Anthropic API computer toolset from own loop inside an E2B Desktop or self-built Docker XFCE container (E2B SDK Apache-2.0, cloud paid); (2) Claude Code Desktop computer use on a dedicated spare Mac or Windows PC (Pro/Max, interactive, app open); (3) Cua Spaces VMs on a spare Mac (source-available FSL).
Rejected: OpenClaw as controller (cannot expose its computer tool to Claude Code, half-million-line gateway, 255+ advisories); Bytebot (archived 2026-03-07); ChatGPT agent/Operator (closed, retired, not drivable); UI-TARS Desktop and Agent S as separate agents (duplicate the engine; not Claude Code plug-ins); Browser Use desktop (not researched).
Spike before building: (a) Cua Driver MCP on a headless Linux VM with Claude Code, one task: open a native app, click, read result; time and tokens per step; (b) whether Withings/WHOOP pairing is feasible without a real phone; (c) Android emulator with KVM and adb screencap versus GUI driving; (d) protected-path hook blocks `rm -rf` against home in all modes.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Claude Code computer use (CLI `computer-use` MCP) | https://code.claude.com/docs/en/computer-use | Built-in screen control of approved apps; macOS only; Pro/Max; interactive only | John's Mac | 2026-10-16 | Not for unattended engineer; use only for native-app tests on a Mac |
| Claude Desktop computer use | https://code.claude.com/docs/en/desktop | Same engine in Desktop; macOS and Windows; session approvals | John's Mac/Windows | 2026-10-16 | Alternative on a spare machine; not unattended-safe |
| Anthropic computer toolset (API) | https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool | `computer_toolset_20260801`, GA; build own loop in a VM | API | 2026-10-16 | Fallback if the Cua route fails; pay per token |
| OpenClaw computer/browser tools | https://github.com/openclaw/openclaw | Peekaboo/CUA computer tool, managed Chrome; MCP server only exposes channels | local/VM | 2026-10-16 | Reject as controller |
| Cua (Driver, Lume, SDK, Spaces) | https://github.com/trycua/cua | Driver MIT, MCP for Claude Code; Spaces FSL; 29.9k stars | Mac/Win/Linux, VMs | 2026-10-16 | Spike first as optional desktop add-on |
| E2B Desktop | https://github.com/e2b-dev/desktop | Apache-2.0 Linux Xfce sandbox SDK for LLM computer use | E2B cloud (paid) or template | 2026-10-16 | Alternative sandbox; price unverified |
| Bytebot | https://github.com/bytebot-ai/bytebot | Self-hosted Docker desktop agent with MCP | Docker | 2026-10-16 | Reject: archived 2026-03-07 |
| UI-TARS Desktop / Agent TARS | https://github.com/bytedance/UI-TARS-desktop | Apache-2.0 GUI agent app, own models | local | 2026-10-16 | Reject: separate agent, last news 2025-11-05 |
| Agent S (Simular) | https://github.com/simular-ai/Agent-S | Apache-2.0 research GUI agent framework; 72.6% OSWorld (self-report) | local | 2026-10-16 (search result only) | Reference only |
| OpenAI ChatGPT agent / Operator | https://help.openai.com/en/articles/11752874-agent | Closed hosted agent; retired per help page | OpenAI | 2026-10-16 (search result only) | Reject: not drivable, retired |
