# Claude Code cloud sessions as the runtime

Brief: What can Claude Code cloud sessions do as the runtime for an always-on autonomous engineer, and what can they not do?
Run: research/runs/engineer-runtime/PLAN.md

All pages below are official docs at code.claude.com or support.claude.com, opened 2026-10-16 with WebFetch (full page returned). Docs are current-version pages (they cite Claude Code v2.1.29x); individual features are marked research preview where the docs say so.

## Docs: network, duration, setup, secrets, repo loading, plugins
### Takeaway
Cloud sessions are a fresh Ubuntu VM per session (4 vCPU, 16 GB, 30 GB) with a configurable network level, setup script (cached), env vars, and proxy-attached network secrets. A single-repo session loads CLAUDE.md, .claude/{settings,rules,skills,agents,commands} and .mcp.json from the clone, but does NOT install plugins declared in the repo. Idle sessions pause after minutes and the VM is later reclaimed; there is no documented hard wall-clock cap on an active session, only per-command limits. Confidence: high for what is stated; medium on total run length (not stated).

### Cited findings
- Cloud sessions are on Pro/Max/Team plans, run on Anthropic VMs, keep running after laptop closes, and have no separate VM charge — https://code.claude.com/docs/en/claude-code-on-the-web, opened 2026-10-16, WebFetch — Quote: "It counts toward your plan's usage limits alongside the rest of your Claude and Claude Code usage, and there's no separate charge for the cloud VM."
- Four network levels (None, Trusted, Full, Custom); default environment is Trusted — https://code.claude.com/docs/en/cloud-environments, opened 2026-10-16, WebFetch — Quote: "**Trusted** | Allowlisted domains only: package registries, GitHub, cloud SDKs | **Full** | Any domain | **Custom** | Your own allowlist"
- Blocked hosts fail with 403; connectors bypass the allowlist (routed via Anthropic servers) — https://code.claude.com/docs/en/routines, opened 2026-10-16, WebFetch — Quote: "Requests on that path to hosts outside the allowlist fail with `403` and `x-deny-reason: host_not_allowed`."
- VM size — https://code.claude.com/docs/en/cloud-environments, opened 2026-10-16, WebFetch — Quote: "4 vCPUs * 16 GB of RAM * 30 GB of disk"
- Idle behaviour: pause after a few minutes, later reclaimed; reclaimed VM restores conversation but not background work — https://code.claude.com/docs/en/cloud-environments, opened 2026-10-16, WebFetch — Quote: "after a few minutes without activity, a session's VM pauses with its files saved. Your next message restores the same VM"
- Reclaimed VM loses background processes and self-paced loop wakeups — https://code.claude.com/docs/en/claude-code-on-the-web, opened 2026-10-16, WebFetch — Quote: "Not restored: background work that was still running when the VM was reclaimed, such as subagents and shell commands"
- Waiting on an MCP connector approval counts as inactive and can expire — https://code.claude.com/docs/en/claude-code-on-the-web, opened 2026-10-16, WebFetch — Quote: "A session counts as inactive while it waits for you to approve an MCP connector tool call or to sign in to an MCP server, and it can expire during that wait."
- Command time limits: 2 min default / 10 min max foreground, then moved to background up to 30 more minutes — https://code.claude.com/docs/en/cloud-environments, opened 2026-10-16, WebFetch — Quote: "Claude waits 2 minutes for a foreground command by default and can ask for up to 10 minutes."
- Env var timeouts are tunable — https://code.claude.com/docs/en/cloud-environments, opened 2026-10-16, WebFetch — Quote: "add BASH_DEFAULT_TIMEOUT_MS and BASH_MAX_TIMEOUT_MS to its environment variables"
- Setup script cached only if under ~5 minutes — https://code.claude.com/docs/en/cloud-environments, opened 2026-10-16, WebFetch — Quote: "keep the script's total runtime under roughly five minutes so the environment cache can build."
- Env vars readable by anyone using the environment; use network secrets for keys. Secrets stay outside the VM, proxy attaches them to listed hosts; cannot be edited, only deleted and re-added — https://code.claude.com/docs/en/cloud-environments, opened 2026-10-16, WebFetch — Quote: "Anthropic's agent proxy adds the key to requests for the hosts you list, after each request leaves the session's VM, so the key itself stays outside the VM."
- Repo-loaded files: .mcp.json, hooks, skills, agents, rules load in a single-repo session — https://code.claude.com/docs/en/cloud-environments, opened 2026-10-16, WebFetch — Quote: "Your repo's `.mcp.json` MCP servers | Yes, in a session with one repository | Part of the clone, found from the session's working directory."
- Plugins declared in repo settings are NOT installed — https://code.claude.com/docs/en/cloud-environments, opened 2026-10-16, WebFetch — Quote: "A cloud session doesn't install the plugins a repository turns on under `enabledPlugins`, including ones from the marketplaces it lists under `extraKnownMarketplaces`"
- User-level skills/CLAUDE.md/user MCP servers do not carry over — https://code.claude.com/docs/en/cloud-environments, opened 2026-10-16, WebFetch — Quote: "Live on your machine, not in the repo. Commit them to the repo's `.claude/` directory instead."
- Pre-installed: Docker, Postgres 16, Redis 7, chromedriver (Node row); no browser listed beyond chromedriver — https://code.claude.com/docs/en/cloud-environments, opened 2026-10-16, WebFetch — Quote: "Docker | docker, dockerd, docker compose | Databases | PostgreSQL 16, Redis 7.0"
- GitHub-only for clone/PR; non-GitHub repos can be bundled but cannot push back — https://code.claude.com/docs/en/claude-code-on-the-web, opened 2026-10-16, WebFetch — Quote: "repository cloning and pull request creation require GitHub."
- Interactive auth (SSO) unsupported — https://code.claude.com/docs/en/cloud-environments, opened 2026-10-16, WebFetch — Quote: "SSO requires browser-based login that can't run in a cloud session"
- Self-hosted environment option (Team/Enterprise only) exists for own compute — https://code.claude.com/docs/en/claude-code-on-the-web, opened 2026-10-16, WebFetch — Quote: "Self-hosted environments | Start a cloud session and pick your organization's environment | Your organization's infrastructure | Deploy runners, on Team and Enterprise plans"

### Contradictions
- None found.

### Inferences
- (mine) The repo-plugin gap means Superpowers-style plugins must be installed by the setup script or replaced by committed `.claude/skills`; the registry already uses `scripts/cloud-setup.sh` for this.
- (mine) No hard max duration for an active session is documented; real ceilings are the Max 5-hour/weekly usage windows and the 4 vCPU/16 GB/30 GB box. Needs a spike.
- (mine) Full network is available, so a headless Playwright/Chromium installed via setup script could in principle run, but nothing in the docs says it is supported; chromedriver being preinstalled is only a hint.

### Gaps
- Maximum wall-clock length of an active cloud session or routine run — not stated on the pages read; spike with a long overnight routine.
- Whether headless Chromium/Playwright installs and runs in the VM — not documented; spike.

## Unattended schedule/trigger runs
### Takeaway
Yes: routines (research preview) run as full cloud sessions on a schedule (min 1 hour), by API POST, or on GitHub PR/release events, with no permission prompts and no machine needed. Results land as a session transcript plus `claude/` branches/PRs and any connector writes (e.g. Slack). GitHub Actions is the alternative, billed on Actions minutes plus subscription (via OAuth token) or API. Confidence: high.

### Cited findings
- Routines have three trigger types, run on Anthropic cloud, available on Max — https://code.claude.com/docs/en/routines, opened 2026-10-16, WebFetch — Quote: "Routines are available on Pro, Max, Team, and Enterprise plans."
- Research preview, behaviour may change — https://code.claude.com/docs/en/routines, opened 2026-10-16, WebFetch — Quote: "Routines are in research preview. Behavior, limits, and the API surface may change."
- Runs are fully autonomous, no approval — https://code.claude.com/docs/en/routines, opened 2026-10-16, WebFetch — Quote: "Routines run autonomously as full Claude Code cloud sessions: there is no permission-mode picker"
- Connector writes happen without asking — https://code.claude.com/docs/en/routines, opened 2026-10-16, WebFetch — Quote: "Claude can use every tool from an included connector, including writes, without asking for permission during a run."
- Minimum schedule interval 1 hour, starts can be minutes late — https://code.claude.com/docs/en/routines, opened 2026-10-16, WebFetch — Quote: "The minimum interval is one hour; expressions that run more frequently are rejected."
- Rate caps — https://code.claude.com/docs/en/routines, opened 2026-10-16, WebFetch — Quote: "Scheduled runs, including one-off runs | 100 per hour | Your account"
- API trigger: POST /fire with bearer token and optional text, beta header — https://code.claude.com/docs/en/routines, opened 2026-10-16, WebFetch — Quote: "The `/fire` endpoint ships under the `experimental-cc-routine-2026-04-01` beta header."
- Fire text is wrapped as untrusted; prompt must opt in — https://code.claude.com/docs/en/routines, opened 2026-10-16, WebFetch — Quote: "It arrives wrapped in a `<routine-fire-payload>` block that labels it as untrusted data"
- Status green does not mean task succeeded — https://code.claude.com/docs/en/routines, opened 2026-10-16, WebFetch — Quote: "A green status in the run list means the session started and exited without an infrastructure error. It does not mean the task in your prompt succeeded."
- Routines skip runs if GitHub connection lapses; off after 72 h — https://code.claude.com/docs/en/routines, opened 2026-10-16, WebFetch — Quote: "After 72 hours without a connection, the routine turns off"
- Branch pushes go to `claude/` prefixed branches; use branch protection to restrict — https://code.claude.com/docs/en/routines, opened 2026-10-16, WebFetch — Quote: "Claude pushes its work to a branch prefixed with `claude/` unless your prompt directs it to push to another branch."
- Comparison of scheduling options (cloud vs desktop vs /loop) — https://code.claude.com/docs/en/scheduled-tasks, opened 2026-10-16, WebFetch — Quote: "Requires machine on | No | Yes | Yes"
- /loop recurring tasks expire after 7 days and only fire while a session is open — https://code.claude.com/docs/en/scheduled-tasks, opened 2026-10-16, WebFetch — Quote: "Recurring tasks automatically expire 7 days after creation."
- Routines cannot be created from inside a cloud session (/schedule unavailable there) — https://code.claude.com/docs/en/routines, opened 2026-10-16, WebFetch — Quote: "You are inside a cloud session, where submitting `/schedule` answers that the command isn't available in that environment."
- Follow-ups can be queued into a running cloud session from any CLI/CI — https://code.claude.com/docs/en/claude-code-on-the-web, opened 2026-10-16, WebFetch — Quote: "claude -p "your message" --cloud <session-id>"
- Auto-fix PR: session subscribes to CI failures and review comments, asks when ambiguous — https://code.claude.com/docs/en/claude-code-on-the-web, opened 2026-10-16, WebFetch — Quote: "Ambiguous requests: if a reviewer's comment could be interpreted multiple ways or involves something architecturally significant, Claude asks you before acting"
- GitHub Actions: schedule cron works in automation mode; runs on GitHub runners; OAuth token uses subscription — https://code.claude.com/docs/en/github-actions, opened 2026-10-16, WebFetch — Quote: "If you authenticate with an OAuth token, runs use your Claude subscription instead of API billing."
- GitHub Actions schedule caveat — https://code.claude.com/docs/en/github-actions, opened 2026-10-16, WebFetch — Quote: "GitHub runs scheduled workflows only from the default branch and, in public repositories, disables the schedule after 60 days without repository activity."
- Actions cost controls: max-turns and workflow timeouts — https://code.claude.com/docs/en/github-actions, opened 2026-10-16, WebFetch — Quote: "Set `--max-turns` in `claude_args` to limit iterations"

### Contradictions
- None found.

### Inferences
- (mine) An "always-on" engineer on cloud is really a chain of discrete runs: hourly-minimum cron plus API `/fire` from an external trigger (n8n/webhook) plus GitHub events. There is no persistent daemon.
- (mine) Continuity between runs must live in the repo (state files, issues), because each run is a fresh clone and VM.
- (mine) Since API-trigger/Run-now runs are launched by someone holding the token, a leaked token is an attack path; the docs mitigate via untrusted-payload wrapping.

### Gaps
- Per-run maximum duration and token budget for routines — not stated; spike.
- GitHub trigger hourly caps — docs say "See Add a GitHub trigger" but give no numbers.

## Browser and logins
### Takeaway
Three routes, none turnkey for unattended logged-in browsing. (1) Claude in Chrome shares the user's real logged-in browser but runs in a visible Chrome on the user's machine, pauses for login/CAPTCHA, and is local-only (no cloud). (2) Remote Control runs the session on the user's machine (so local Chrome and logins remain reachable, and `--chrome` is supported in server mode) but the machine must stay on. (3) Cloud VM headless browser has no documented support and no user logins. Confidence: medium-high.

### Cited findings
- Claude in Chrome reuses the logged-in browser — https://code.claude.com/docs/en/chrome, opened 2026-10-16, WebFetch — Quote: "Claude opens new tabs for browser tasks and shares your browser's login state, so it can access any site you're already signed into."
- It is visible, and pauses on login/CAPTCHA — https://code.claude.com/docs/en/chrome, opened 2026-10-16, WebFetch — Quote: "Browser actions run in a visible Chrome window in real time. When Claude encounters a login page or CAPTCHA, it pauses and asks you to handle it manually."
- Needs claude.ai login; API key or setup-token disables it — https://code.claude.com/docs/en/chrome, opened 2026-10-16, WebFetch — Quote: "If you authenticate with an API key or a long-lived token from `claude setup-token`, Claude Code keeps Chrome integration off"
- Not in WSL; service worker can go idle on long sessions — https://code.claude.com/docs/en/chrome, opened 2026-10-16, WebFetch — Quote: "The Chrome extension's service worker can go idle during extended sessions, which breaks the connection."
- A repo cannot enable Chrome itself — https://code.claude.com/docs/en/chrome, opened 2026-10-16, WebFetch — Quote: "a repository you check out must not be able to connect Claude to your browser."
- Remote Control: execution stays on the user's machine, all local tools/MCP available — https://code.claude.com/docs/en/remote-control, opened 2026-10-16, WebFetch — Quote: "When you start a Remote Control session on your machine, Claude keeps running locally the entire time, so your code execution and filesystem access stay on your machine."
- Remote Control server mode can turn on Chrome for spawned sessions — https://code.claude.com/docs/en/remote-control, opened 2026-10-16, WebFetch — Quote: "Turn Chrome integration on or off in the sessions the server creates, so Claude can use Chrome on your machine while you work from another device."
- Remote Control server mode: up to 32 concurrent sessions, worktree spawn; gives up after ~10 min outage — https://code.claude.com/docs/en/remote-control, opened 2026-10-16, WebFetch — Quote: "Server mode: Claude Code gives up after roughly 10 minutes and the `claude remote-control` process exits."
- Remote Control is Pro/Max/Team/Enterprise, no API keys — https://code.claude.com/docs/en/remote-control, opened 2026-10-16, WebFetch — Quote: "available on Pro, Max, Team, and Enterprise plans. API keys are not supported."
- Cloud docs point heavy workloads to Remote Control on own hardware — https://code.claude.com/docs/en/cloud-environments, opened 2026-10-16, WebFetch — Quote: "use Remote Control to run Claude Code on your own hardware, or run cloud sessions in a self-hosted environment"
- Desktop scheduled tasks run locally with local files (machine on, no open session) — https://code.claude.com/docs/en/scheduled-tasks, opened 2026-10-16, WebFetch — Quote: "Desktop | Runs on | Your machine"

### Contradictions
- None found.

### Inferences
- (mine) For "browser with John's logins, overnight", cloud is the wrong place; a John-controlled always-on machine running Claude Code (Remote Control server mode or Desktop scheduled tasks) with a logged-in Chrome profile is the documented route, and the cloud VM suits repo/CI/API work. Needs a spike on whether Claude in Chrome tolerates an unattended, logged-in headed Chrome (the docs describe "visible Chrome" and idle service worker).
- (mine) A cloud-side Playwright without logins is plausible with Full network but is undocumented; credentials would need to be injected as env vars (readable by anyone using the environment, single user here).

### Gaps
- No official statement on headless/unattended Claude in Chrome — not found on the pages read.
- Whether Desktop scheduled tasks can drive Chrome — I did not open the desktop-scheduled-tasks page.

## Reaching the user for approvals
### Takeaway
Cloud routines never ask; they have no permission prompts, so "batched approvals" must be designed as outputs (PRs, issues, Slack posts via connectors) that John approves afterwards. Official interactive approval paths exist only for sessions on John's machine: Remote Control mobile push (permission prompts and questions) and Channels (Telegram/Discord/iMessage, research preview, with optional permission relay). No official SMS or email approval channel found. Confidence: medium-high.

### Cited findings
- Routines can post summaries to Slack (connector) — https://code.claude.com/docs/en/routines, opened 2026-10-16, WebFetch — Quote: "posts a summary to Slack so the team starts the day with a groomed queue."
- Cloud session: a question left unanswered keeps the session until environment expiry; answer later continues it — https://code.claude.com/docs/en/claude-code-on-the-web, opened 2026-10-16, WebFetch — Quote: "If Claude asks a question and the session sits idle, you can still answer when you come back, up to environment expiry"
- Remote Control push notifications for decisions — https://code.claude.com/docs/en/remote-control, opened 2026-10-16, WebFetch — Quote: "Claude decides when to push. It typically sends one when a long-running task finishes or when it needs a decision from you to continue."
- Permission prompt pushes toggle — https://code.claude.com/docs/en/remote-control, opened 2026-10-16, WebFetch — Quote: "enable **Push when Claude decides** for proactive notifications, **Push when actions required** for permission prompts and questions, or both."
- Prompts held open until answered — https://code.claude.com/docs/en/remote-control, opened 2026-10-16, WebFetch — Quote: "Claude Code keeps permission prompts and `AskUserQuestion` questions open until you answer them."
- Channels: Telegram, Discord, iMessage plugins; research preview; session must be open — https://code.claude.com/docs/en/channels, opened 2026-10-16, WebFetch — Quote: "Events only arrive while the session is open, so for an always-on setup you run Claude in a background process or persistent terminal."
- Channels can relay permission prompts to the user — https://code.claude.com/docs/en/channels, opened 2026-10-16, WebFetch — Quote: "Channel servers that declare the permission relay capability can forward these prompts to you so you can approve or deny remotely."
- Channels apply to a running local session, not spawned cloud sessions — https://code.claude.com/docs/en/channels, opened 2026-10-16, WebFetch — Quote: "Channels fill the gap in that list by pushing events from non-Claude sources into your already-running local session."
- Channel allowlist: anyone who can reply can approve tools — https://code.claude.com/docs/en/channels, opened 2026-10-16, WebFetch — Quote: "Anyone who can reply through the channel can approve or deny tool use in your session, so only allowlist senders you trust with that authority."
- Unattended local alternative: skip-permissions flag with caveat — https://code.claude.com/docs/en/channels, opened 2026-10-16, WebFetch — Quote: "--dangerously-skip-permissions bypasses most prompts, but only use it in environments you trust."
- GitHub PR as an approval surface: auto-fix asks before acting on ambiguous review comments (see above), and pushes land on `claude/` branches gated by branch protection (routines page).

### Contradictions
- None found.

### Inferences
- (mine) Pattern that fits the docs: overnight routine produces PRs/issues and a Slack digest through a connector; John approves in the morning (merge, label, comment), with a GitHub-event routine or `claude -p ... --cloud <id>` follow-up reacting to approvals. This is a batched-approval design built from parts, not a documented feature.
- (mine) Slack/Telegram-style live approvals need a local always-on Claude Code process, not a cloud routine.
- (mine) Via the Gmail/Notion/Slack connectors a routine could email or message John, but I did not verify any connector for SMS or email send in the docs.

### Gaps
- No official SMS or email approval mechanism found.
- Slack integration page (https://code.claude.com/docs/en/slack) not opened.
- Notification hook behaviour in cloud sessions not checked.

## Cost and plan constraints
### Takeaway
Cloud sessions and routines draw on the same Max subscription usage as everything else (5-hour session limit plus weekly limit, shared across Claude and Claude Code); there is no per-VM charge. Usage credits can extend past limits at API rates; otherwise routine runs are rejected until reset. Routines add hourly run caps. Confidence: medium-high; Max prices and exact quotas not verified from an opened page.

### Cited findings
- Max/Pro have 5-hour and weekly limits shared across Claude and Claude Code — https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan, opened 2026-10-16, WebFetch — Quote: "Both Pro and Max plans have a five-hour session limit and a weekly limit."
- Shared across surfaces — same page — Quote: "These limits are shared across Claude and Claude Code"
- Cloud usage counts against plan; parallel tasks multiply consumption — https://code.claude.com/docs/en/claude-code-on-the-web, opened 2026-10-16, WebFetch — Quote: "Running multiple tasks in parallel consumes more rate limits proportionately."
- Routine behaviour at limit — https://code.claude.com/docs/en/routines, opened 2026-10-16, WebFetch — Quote: "Without usage credits, additional runs are rejected until your usage window resets."
- Overage possible on metered credits — https://code.claude.com/docs/en/routines, opened 2026-10-16, WebFetch — Quote: "organizations with usage credits turned on can keep running routines on metered overage."
- Hourly caps have no overage — https://code.claude.com/docs/en/routines, opened 2026-10-16, WebFetch — Quote: "None of these hourly limits has overage."
- Routine run caps per routine — https://code.claude.com/docs/en/routines, opened 2026-10-16, WebFetch — Quote: "Run now, API fires, and setting a one-off routine to run again | 30 per hour | Each routine"
- Cloud sessions unavailable on API-key auth or Bedrock/Vertex — https://code.claude.com/docs/en/claude-code-on-the-web, opened 2026-10-16, WebFetch — Quote: "`--cloud` requires an Anthropic account. It's not available when Claude Code is configured for Amazon Bedrock, Google Cloud's Agent Platform, or another third-party provider."
- ZDR/HIPAA/CMEK orgs cannot use cloud sessions (not relevant to a personal Max account) — https://code.claude.com/docs/en/claude-code-on-the-web, opened 2026-10-16, WebFetch — Quote: "Organizations with Zero Data Retention enabled, or with the HIPAA configuration applied, can't use `/web-setup` or other cloud session features."
- GitHub Actions can run on the Max subscription via OAuth token — https://code.claude.com/docs/en/github-actions, opened 2026-10-16, WebFetch — Quote: "`CLAUDE_CODE_OAUTH_TOKEN`: an OAuth token that authenticates with your Claude subscription, available on Pro, Max, Team, and Enterprise plans."

### Contradictions
- None found.

### Inferences
- (mine) A multi-hour overnight loop on Max will be bounded by the 5-hour window and the weekly cap, not by any cloud-VM timer; usage credits (pay-as-you-go) are the only documented way past that, which is a paid option and must be justified with price.
- (mine) Parallel overnight sessions burn the weekly limit proportionally faster; cap parallelism.

### Gaps
- Max 5x/20x prices ($100/$200) appeared only in a search snippet (support.claude.com/en/articles/11049741-what-is-the-max-plan), not an opened page; the opened Pro/Max article did not list prices. Not cited.
- Actual token quotas per Max tier are not published (the sources I saw say only multiples of Pro per-session allowance); a third-party blog (2026-10-08) said so too but was a snippet only.
- Search snippets mention a separate "Fable" weekly limit on Max; not verified on an opened page.

## Recommendation, alternatives, rejected, spikes
(Facet-level, as the plan requires.)
- Recommendation: use cloud routines (schedule + API fire + GitHub events) on the Max plan as the unattended repo/CI/PR worker, with all state in the repo, outputs as `claude/` branches/PRs plus a Slack (connector) digest for batched morning approval. Use a John-controlled always-on machine only for what cloud cannot do (logged-in browser, interactive approvals).
- Alternatives: (a) GitHub Actions with `CLAUDE_CODE_OAUTH_TOKEN` for cron/CI-bound jobs; (b) Remote Control server mode / Desktop scheduled tasks on John's own machine for browser logins and push-notification approvals; (c) Channels (Telegram/Discord) for live approvals on the local process; (d) self-hosted environments are Team/Enterprise only, so not available to a Max user.
- Rejected: `/loop` for overnight work (7-day expiry, needs open session); cloud sessions for logged-in browsing (no logins, SSO unsupported, no documented browser); Claude in Chrome unattended (visible window, pauses on login/CAPTCHA).
- Spike before building: (1) longest routine run actually allowed and its usage cost against Max windows; (2) headless Chromium/Playwright install in the setup script under Full network; (3) routine writes a Slack/email digest via connector and a morning approval round-trips through a GitHub event or `--cloud <id>` follow-up; (4) plugin install (Superpowers) via setup script since repo `enabledPlugins` is ignored; (5) Claude in Chrome on an unattended headed machine.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Claude Code cloud sessions | https://code.claude.com/docs/en/claude-code-on-the-web | Anthropic-hosted VM sessions, no VM charge, plan usage | cloud | 2026-10-16 | Use as the unattended repo worker; no browser logins |
| Routines | https://code.claude.com/docs/en/routines | Schedule (>=1 h), API `/fire`, GitHub triggers; no approval prompts; research preview | cloud | 2026-10-16 | Use for overnight runs; spike duration |
| Cloud environments (setup script, network secrets) | https://code.claude.com/docs/en/cloud-environments | Network levels, env vars, secrets via proxy, cached setup | cloud | 2026-10-16 | Use; Full network for installs, secrets for keys |
| Remote Control | https://code.claude.com/docs/en/remote-control | Drive local sessions from phone/web; push notifications; server mode | John's machine | 2026-10-16 | Use for browser logins and live approvals |
| Claude in Chrome | https://code.claude.com/docs/en/chrome | Uses logged-in Chrome; visible window; local only | John's machine | 2026-10-16 | Fallback; not unattended-safe per docs |
| Channels (Telegram/Discord/iMessage) | https://code.claude.com/docs/en/channels | Push events and permission relay into a running local session; research preview | John's machine | 2026-10-16 | Candidate for live approvals; needs always-on local process |
| /loop and scheduled tasks | https://code.claude.com/docs/en/scheduled-tasks | In-session cron, 7-day expiry | local session | 2026-10-16 | Skip for overnight |
| Claude Code GitHub Actions | https://code.claude.com/docs/en/github-actions | Action with cron, uses subscription via OAuth token | GitHub runners | 2026-10-16 | Fallback/alternative to routines |
