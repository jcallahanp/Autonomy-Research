# Engineer runtime: where an always-on autonomous Claude Code engineer runs, and how it is packaged

**Summary.** The evidence points to a mix with a John-controlled machine at the core. Claude Code cloud
sessions and Routines run unattended on the Max plan with no VM charge
(https://code.claude.com/docs/en/claude-code-on-the-web, https://code.claude.com/docs/en/routines), but a
routine has "no permission-mode picker" (https://code.claude.com/docs/en/routines), the VM carries no login
state and "SSO requires browser-based login that can't run in a cloud session"
(https://code.claude.com/docs/en/cloud-environments), and Claude in Chrome runs only "in a visible Chrome
window" on the user's own machine (https://code.claude.com/docs/en/chrome). The two requirements cloud cannot
meet, browser work with John's logins and approvals relayed over a chat channel, are met only by a session on
a machine John controls: Channels push Telegram/Discord/iMessage events into "your already-running local
session" and can relay permission prompts (https://code.claude.com/docs/en/channels), Remote Control pushes
decisions to the phone and keeps prompts open until answered (https://code.claude.com/docs/en/remote-control),
and a real Chromium profile keeps cookies (https://github.com/browser-use/bux). Anthropic documents
`claude -p` for unattended runs (https://code.claude.com/docs/en/headless), requires "a container, VM, or the
sandbox runtime" for skip-permissions (https://code.claude.com/docs/en/permission-modes), and its legal page
allows "an end user ... signing in to the unmodified Claude Code binary with their own Claude subscription"
while assuming "ordinary, individual usage" (https://code.claude.com/docs/en/legal-and-compliance). Max
usage is one shared pool with "a five-hour session limit and a weekly limit"
(https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan), so overnight
work is bounded by John's own quota, not by any VM timer. For packaging, Anthropic's own table says a VM needs
no Docker while a dev container does (https://code.claude.com/docs/en/sandbox-environments); a cloud session
"doesn't install the plugins a repository turns on" (https://code.claude.com/docs/en/cloud-environments), so
Superpowers must be installed by a bootstrap script, as `scripts/cloud-setup.sh:8-18` already does; Beads is
"a CLI tool you install once" (https://github.com/steveyegge/beads README.md:30-43,131 (commit d274841)) and
the official Ralph plugin is "a **Stop hook**" (https://github.com/anthropics/claude-code
plugins/ralph-wiggum/README.md:13,38 (commit 03b5892)), so neither is a plugin to bundle by default. OpenClaw can
run Claude Code as its runtime through a `claude-cli` backend (https://github.com/openclaw/openclaw
docs/gateway/cli-backends.md:9 (commit ca009ba)), but its sandboxing "is off by default"
(docs/gateway/sandboxing.md:9), it has "over 255 GitHub Security Advisories"
(https://www.ibm.com/think/x-force/what-openclaw-reveals-about-agentic-ai-security-risks), and Claude Code
already ships chat push, remote steering and scheduling, so no harness should be the host. Recommendation:
one plain Ubuntu VM (VPS or home box) with a non-root user, the unmodified Claude Code binary signed in with
John's Max subscription, a pinned `bootstrap.sh`, Channels plus Remote Control for approvals and a dedicated
persistent browser profile, with cloud Routines as the companion for GitHub-only overnight jobs. All claims
rest on pages or clones opened 2026-10-16; inferences are marked.

## Questions and answers

### Q1. Can Claude Code cloud sessions and Routines be the unattended overnight runtime, and what can they not do?

**Confidence: medium-high** for what the docs state; **medium** on run length (no cap is documented).

- *What they are.* Cloud sessions run on Anthropic VMs for Pro/Max/Team users and "there's no separate charge
  for the cloud VM" (https://code.claude.com/docs/en/claude-code-on-the-web). Each session gets "4 vCPUs *
  16 GB of RAM * 30 GB of disk" (https://code.claude.com/docs/en/cloud-environments) with a network level of
  None, Trusted (default), Full or Custom (https://code.claude.com/docs/en/cloud-environments); blocked hosts
  fail with 403 and `x-deny-reason: host_not_allowed` (https://code.claude.com/docs/en/routines). Docker,
  PostgreSQL 16 and Redis 7.0 are preinstalled (https://code.claude.com/docs/en/cloud-environments).
- *Unattended triggers.* Routines "are available on Pro, Max, Team, and Enterprise plans", are "in research
  preview", "run autonomously as full Claude Code cloud sessions: there is no permission-mode picker", can use
  connector writes "without asking for permission", have a minimum schedule interval of one hour, caps of
  "100 per hour" per account and "30 per hour" per routine for Run now/API fires, an API `/fire` endpoint under
  the `experimental-cc-routine-2026-04-01` beta header whose payload "arrives wrapped in a
  `<routine-fire-payload>` block that labels it as untrusted data", and push work to `claude/` branches
  (all https://code.claude.com/docs/en/routines). "A green status in the run list ... does not mean the task
  in your prompt succeeded", and "After 72 hours without a connection, the routine turns off"
  (https://code.claude.com/docs/en/routines). Routines cannot be created from inside a cloud session
  (https://code.claude.com/docs/en/routines). Follow-ups can be queued with `claude -p "your message" --cloud
  <session-id>` (https://code.claude.com/docs/en/claude-code-on-the-web). GitHub Actions is the alternative:
  "If you authenticate with an OAuth token, runs use your Claude subscription instead of API billing", with
  the caveat that GitHub runs schedules only from the default branch and disables them in public repos after
  60 idle days (https://code.claude.com/docs/en/github-actions).
- *Duration and continuity.* "after a few minutes without activity, a session's VM pauses with its files
  saved" (https://code.claude.com/docs/en/cloud-environments); a reclaimed VM does not restore "background
  work that was still running ... such as subagents and shell commands", and a session "counts as inactive
  while it waits for you to approve an MCP connector tool call" and "can expire during that wait"
  (https://code.claude.com/docs/en/claude-code-on-the-web). Foreground commands wait 2 minutes by default,
  up to 10 (https://code.claude.com/docs/en/cloud-environments), tunable via `BASH_DEFAULT_TIMEOUT_MS` and
  `BASH_MAX_TIMEOUT_MS` (same page). Worker inference (not in the source): a further 30 minutes in the
  background after that. The setup script is cached only if it finishes in "roughly five minutes"
  (https://code.claude.com/docs/en/cloud-environments). *Worker inference:* an "always-on" engineer on cloud is
  a chain of discrete runs (hourly cron, API fire, GitHub events) with no persistent daemon; continuity must
  live in the repo because each run is a fresh clone and VM; no hard maximum for an active session is
  documented, so the real ceilings are the Max usage windows (see Q2) and the VM size.
- *What loads.* A single-repo session loads the repo's `.mcp.json`, hooks, skills, agents and rules "Part of the
  clone" (https://code.claude.com/docs/en/cloud-environments), but "A cloud session doesn't install the plugins
  a repository turns on under `enabledPlugins`" and user-level skills, CLAUDE.md and MCP servers "Live on your
  machine, not in the repo" (same page). Clone and PR creation "require GitHub"
  (https://code.claude.com/docs/en/claude-code-on-the-web); `--cloud` "requires an Anthropic account" and is
  unavailable on Bedrock/Vertex (same page). Self-hosted environments for own compute exist only "on Team and
  Enterprise plans" (https://code.claude.com/docs/en/claude-code-on-the-web,
  https://code.claude.com/docs/en/self-hosted-environments).
- *What they cannot do.* No browser beyond chromedriver is listed among preinstalled tools
  (https://code.claude.com/docs/en/cloud-environments), "SSO requires browser-based login that can't run in a
  cloud session" (same page), and environment variables are readable by anyone using the environment, so
  keys belong in network secrets where "the key itself stays outside the VM" (same page). *Worker inference:*
  a headless Playwright/Chromium installed by the setup script under Full network could in principle run,
  but nothing in the docs says it is supported; credentials would have to be env vars.

### Q2. Can John run Claude Code unattended on a machine he controls on his Max plan within Anthropic's terms, and what does it take?

**Confidence: high** on the documented modes; **medium** on terms and billing (policy text is clear but has
changed during 2026).

- *Official unattended modes.* `claude -p` is the non-interactive entry point
  (https://code.claude.com/docs/en/headless). `--permission-prompts none` is for "a scheduled job" where
  "nobody is available to answer" (same page). The fully unattended recipe is `claude -p "<prompt>"
  --dangerously-skip-permissions` with "Required: a container, VM, or the sandbox runtime"
  (https://code.claude.com/docs/en/permission-modes); the same page warns to use bypass only "in isolated
  environments like containers, VMs, or dev containers without internet access" and that "Deny rules block in
  every mode, including `bypassPermissions`". Auto mode uses "A separate classifier model" instead of the
  user (https://code.claude.com/docs/en/security); worker inference (not in the source): it is the default
  start mode from v2.1.283. Anthropic advises VMs "especially when interacting with external web services"
  (https://code.claude.com/docs/en/security). A `-p` session "shows no workspace trust dialog and no
  per-server approval prompt" (https://code.claude.com/docs/en/headless), stops idle waits after 10 minutes by
  default (same page), reports `total_cost_usd` as a client-side estimate (same page), and on SIGTERM "leaves
  the turn that was in progress unfinished" (same page). `--bare` "never reads OAuth credentials or the
  system keychain" (https://code.claude.com/docs/en/headless) and "does not read `CLAUDE_CODE_OAUTH_TOKEN`"
  (https://code.claude.com/docs/en/authentication), so it needs an API key.
- *Authentication on a server.* A Max plan can mint "a one-year OAuth token with `claude setup-token`"
  (https://code.claude.com/docs/en/authentication); that token "can only make model requests, so it can't
  establish Remote Control sessions or fetch claude.ai connectors" (same page), and with it or an API key
  "Claude Code keeps Chrome integration off" (https://code.claude.com/docs/en/chrome). "In non-interactive
  mode (`-p`), the key is always used when present" (https://code.claude.com/docs/en/authentication), so a
  stray API key silently bills at API rates. Headless login is an accepted case: the browser callback
  failure "is common in WSL2, SSH sessions, and containers" (same page). On Linux credentials sit in
  `~/.claude/.credentials.json` at mode 0600 (same page), and "A background session ... that outlives the
  login stops making progress once the credential expires" (same page). A field report says a static Max token
  can 401 and "hard-latches and never self-recovers until you restart the process"
  (https://dev.to/drickon/the-token-is-valid-but-your-headless-claude-code-agent-just-401d-forever-48ip).
- *Terms.* "Advertised usage limits for Pro and Max plans assume ordinary, individual usage of Claude Code and
  the Agent SDK"; "Anthropic does not permit third-party developers to offer Claude.ai login into their own
  applications, or to route requests through Free, Pro, or Max plan credentials on behalf of their users";
  "Nor does it prevent an end user from signing in to the unmodified Claude Code binary with their own Claude
  subscription"; "Anthropic reserves the right to take measures to enforce these restrictions and may do so
  without prior notice" (all https://code.claude.com/docs/en/legal-and-compliance). The Agent SDK page adds
  "Unless previously approved, Anthropic does not allow third party developers to offer claude.ai login or
  rate limits for their products, including agents built on the Claude Agent SDK"
  (https://code.claude.com/docs/en/agent-sdk/overview). *Worker inference:* John as a single user running the
  unmodified binary on his own machine fits the permitted case; the risk is policy drift, not current
  prohibition.
- *Usage limits and cost.* "Both Pro and Max plans have a five-hour session limit and a weekly limit" and "These
  limits are shared across Claude and Claude Code"
  (https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan; also quoted as
  "all activity in both tools counts against the same limits" at
  https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan). "Running
  multiple tasks in parallel consumes more rate limits proportionately"
  (https://code.claude.com/docs/en/claude-code-on-the-web). At the limit, "additional runs are rejected until
  your usage window resets" unless usage credits allow "metered overage", and "None of these hourly limits
  has overage" (https://code.claude.com/docs/en/routines). The wrap-up allowance "is small and capped"
  (https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan) and Claude
  Code can "wait and continue the interrupted task automatically after the reset"
  (https://code.claude.com/docs/en/costs; worker inference (not in the source): from v2.1.234). Long sessions
  cost more: "a one-line question in a session that has been open all day still draws usage for the whole
  conversation", "`/compact` ... is itself a large request", "a scheduled task fires on its interval even while
  the session is idle, sending your full context each time", cache lifetime "is an hour on a subscription and
  drops to five minutes once you're drawing on usage credits", and agent teams "use approximately 7x more
  tokens" (all https://code.claude.com/docs/en/costs). GitHub Actions can use `CLAUDE_CODE_OAUTH_TOKEN`
  "available on Pro, Max, Team, and Enterprise plans" (https://code.claude.com/docs/en/github-actions).
- *Reported VPS setups.* "Claude Code runs on your existing Claude subscription with no additional fee"
  (https://www.virtua.cloud/learn/en/tutorials/run-claude-code-vps); worker inference (not in the source):
  the guide estimates roughly 10-20 EUR/month for 4 vCPU/8 GB and says 4 GB handles a medium codebase. Login
  on a headless server: "generate an OAuth token on a machine with a browser, then transfer it to the VPS"
  (same page). Failure modes: "The OOM killer may also pick the tmux server rather than the build, taking your
  session with it", a non-root user "removes most of the ways a stray shell command can wreck the host", and
  skip-permissions "removes the last thing standing between a misread instruction and a `git push --force`"
  (https://www.ssdnodes.com/learn/claude-code-on-a-vps-with-tmux). Browser Use's bux runs Claude Code on
  "Ubuntu 22.04+ with ≥2GB RAM. A $5/mo VPS is fine." (https://github.com/browser-use/bux). *Worker inference:*
  a $5 box suffices for the CLI, but a Chromium plus builds argues for 4 GB+ RAM and swap; every guide works
  without Docker, the VM plus non-root user being the isolation unit.

**Contradictions.** (1) *How `claude -p` is billed on Max.* A search excerpt of
https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan (not an opened
source) said that from June 15, 2026 `claude -p` usage no longer counts toward plan limits; the opened current
page says "We've paused the previously-announced changes to Claude Agent SDK usage." (June 15, 2026 update) and
"Claude Max and Team plans now include monthly API credits, which cover the Claude Agent SDK" (Oct 7, 2026
update). OpenClaw's own doc agrees with the pause: "Subscription-plan Claude Agent SDK, `claude -p`, and
third-party app usage still draw from the signed-in subscription's usage limits"
(https://github.com/openclaw/openclaw docs/providers/anthropic.md:281-288 (commit ca009ba)). The opened pages
win; how the Oct 7 "monthly API credits" interact with the shared 5-hour/weekly windows for `claude -p` is
unresolved and is a spike item. (2) *Third-party harness use of a subscription.* The self-hosted worker relied
on a Register search excerpt (not opened) for an April 2026 cut-off of OpenClaw from subscription limits, and a
snippet from openclawlaunch.com (not opened) claimed a May 2026 reversal; neither is a source here. The opened
Anthropic legal page forbids third parties routing through plan credentials and permits the end user's own
unmodified binary (https://code.claude.com/docs/en/legal-and-compliance). Whether a harness that merely
spawns the unmodified `claude` binary (OpenClaw's `claude-cli` backend) counts as the permitted case is
unresolved: the harness worker infers it is "the policy-safest harness path", the self-hosted worker infers
"Do not put John's token into any third-party harness". Both are inferences; carried to Open questions.

### Q3. Where do John's browser logins and secrets live for browser work?

**Confidence: medium-high** for the Anthropic-documented routes; **medium** for third-party patterns.

- *Claude in Chrome* "shares your browser's login state, so it can access any site you're already signed into",
  but "Browser actions run in a visible Chrome window in real time. When Claude encounters a login page or
  CAPTCHA, it pauses and asks you to handle it manually"; its "service worker can go idle during extended
  sessions, which breaks the connection"; it is off under API-key or setup-token auth; and "a repository you
  check out must not be able to connect Claude to your browser" (all https://code.claude.com/docs/en/chrome).
  So it needs a subscription `/login` session on a headed machine and is not documented for unattended use.
- *Remote Control keeps execution local.* "Claude keeps running locally the entire time, so your code execution
  and filesystem access stay on your machine"; server mode can "Turn Chrome integration on or off in the
  sessions the server creates"; it is "available on Pro, Max, Team, and Enterprise plans. API keys are not
  supported."; "Your local Claude Code session makes outbound HTTPS requests only and never opens inbound
  ports"; and "Server mode: Claude Code gives up after roughly 10 minutes" of outage (all
  https://code.claude.com/docs/en/remote-control). Worker inference (not in the source): up to 32 concurrent
  sessions. The cloud docs themselves point heavy or local-resource work to "Remote Control to run Claude Code
  on your own hardware" (https://code.claude.com/docs/en/cloud-environments).
- *Persistent real browser on a VPS.* bux gives Claude Code "A real Chromium session via browser-harness —
  cookies persist, logins stick" with "no credential-stuffing, no brittle workarounds" and a human hand-off on
  login walls (https://github.com/browser-use/bux). The bux page contains instructions addressed to agents
  ("Paste into Claude Code ... and it will set up your VPS for you", as the note reports); they were not
  followed and the tool was not installed.
- *Secrets.* "Claude never sees the vault item, password, or one-time code" with 1Password for Claude, which
  "is available now for Mac" (https://1password.com/blog/1password-for-claude). For containers, "Avoid
  mounting host secrets such as `~/.ssh` or cloud credential files into the container; prefer
  repository-scoped or short-lived tokens", "pass credentials into the container as environment variables
  through `containerEnv`, a Codespaces secret, or your cloud's workload identity", "Codespaces exposes secrets
  as environment variables inside the container automatically", and a malicious project can exfiltrate
  "anything accessible inside the container, including the Claude Code credentials stored in" `~/.claude`
  (all https://code.claude.com/docs/en/devcontainer); persisting login needs more than a volume at `~/.claude`
  (same page). The devcontainer spec leaves unset `${localEnv:}` variables blank
  (https://containers.dev/implementors/json_reference/; the note flags this fetch as tool-summarised, medium
  reliability). In the cloud, network secrets keep the key outside the VM
  (https://code.claude.com/docs/en/cloud-environments; /home/user/Autonomy-Research/research/findings/packaging.md:164-168,299-303).
  "MCP servers, command hooks, and plugin monitors are separate processes that run unconstrained on the host"
  even under the Bash sandbox (https://code.claude.com/docs/en/sandbox-environments). OpenClaw's own guidance
  for any always-on agent host is to "Run it on a dedicated machine/VM/container, use a dedicated OS user +
  dedicated browser/profile/accounts, and do not sign that runtime into personal Apple/Google accounts"
  (https://github.com/openclaw/openclaw docs/gateway/security/secrets-and-storage.md:17 (commit ca009ba)).
- *Worker inferences (all marked as such in the notes):* log in once by hand into a dedicated persistent browser
  profile on the VM, prefer limited-scope accounts, never put passwords in model context, hand off 2FA to John;
  a logged-in browser plus bypass permissions means a prompt-injected page can act as John, so use `auto` mode
  or an allowlist where possible and deny rules for `~/.ssh`, vault files and protected branches; the repo
  holds secret *names* only (`.env.example`), values live in the host's store; the Mac-only 1Password route
  would favour a home Mac over a Linux VPS if vault-mediated fills are wanted; whether Playwright profile
  persistence (`--user-data-dir`, `--storage-state`) works was seen only in a snippet and is not cited.

### Q4. How does the engineer reach John with batched approvals over a light channel?

**Confidence: medium-high.** Cloud routines never ask; approvals there are outputs reviewed afterwards.
Live approval relays exist only for sessions on John's machine.

- *Cloud.* Routines have no permission prompts (https://code.claude.com/docs/en/routines) and can post "a
  summary to Slack so the team starts the day with a groomed queue" via a connector (same page); work lands on
  `claude/` branches (same page). In an interactive cloud session, "If Claude asks a question and the session
  sits idle, you can still answer when you come back, up to environment expiry"
  (https://code.claude.com/docs/en/claude-code-on-the-web). The auto-fix PR flow asks before acting on
  ambiguous or architecturally significant review comments (same page). *Worker inference:* the fitting pattern
  is an overnight routine that produces PRs/issues plus a Slack digest, which John approves in the morning by
  merging, labelling or commenting, with a GitHub-event routine or `claude -p ... --cloud <id>` follow-up
  reacting; this is a batched-approval design built from parts, not a documented feature. No SMS or email
  approval mechanism was found.
- *John's machine: Remote Control.* "Claude decides when to push. It typically sends one when a long-running
  task finishes or when it needs a decision from you to continue."; users can "enable **Push when Claude
  decides** ... **Push when actions required** for permission prompts and questions, or both"; and "Claude Code
  keeps permission prompts and `AskUserQuestion` questions open until you answer them" (all
  https://code.claude.com/docs/en/remote-control).
- *John's machine: Channels.* "Telegram, Discord, and iMessage are included in the research preview"; "Events
  only arrive while the session is open, so for an always-on setup you run Claude in a background process or
  persistent terminal"; "Channel servers that declare the permission relay capability can forward these
  prompts to you so you can approve or deny remotely"; Channels push events "into your already-running local
  session"; "Anyone who can reply through the channel can approve or deny tool use in your session, so only
  allowlist senders you trust with that authority"; "the actions no mode auto-approves still apply"; during
  the preview `--channels` accepts only Anthropic-allowlisted plugins; Channels are not available on
  Bedrock/Vertex/Foundry; and "`--dangerously-skip-permissions` bypasses most prompts, but only use it in
  environments you trust" (all https://code.claude.com/docs/en/channels). Scheduling that "survives
  independently of any session" is Routines, a Desktop scheduled task, or GitHub Actions
  (https://code.claude.com/docs/en/scheduled-tasks); `/loop` tasks "automatically expire 7 days after
  creation" (same page); Desktop scheduled tasks run on "Your machine" (same page).
- *Worker inference:* Slack/Telegram-style live approvals need a local always-on Claude Code process, not a
  cloud routine; the overnight design needs a watchdog that restarts on 401/stall, per-run `--max-budget-usd`
  and `--max-turns`, fresh sessions per task, and a stall notification.

### Q5. How should the engineer be packaged for a non-Docker user, and how does it bundle its pieces?

**Confidence: medium** (docs and clones read; no route was run). Builds on
/home/user/Autonomy-Research/research/findings/packaging.md (plugin anatomy, load matrix, secrets).

- *Routes compared.* Anthropic's table: "Virtual machine | Full operating system | No | High" (Docker required:
  No; setup effort High); cloud sessions need "None; requires a Claude subscription, and a connected GitHub
  account unless you launch with `claude --cloud`"; "Always run `--dangerously-skip-permissions` sessions
  inside a container, a VM, or the sandbox runtime"; the container is "a convention rather than an
  enforcement boundary, because Claude Code does not require a container"; and "Don't take a clean start as
  proof your settings loaded" (all https://code.claude.com/docs/en/sandbox-environments). A dev container
  "runs as a Docker container, either on your machine or on a cloud host such as GitHub Codespaces"; its
  feature tag "pins the feature's install script, not the Claude Code release"; exact pinning needs `npm
  install -g @anthropic-ai/claude-code@X.Y.Z` in a Dockerfile; the reference container "is provided as a
  working example rather than a maintained base image" and its firewall "and these capabilities are not
  required for Claude Code itself"; MCP servers belong "at project scope in a `.mcp.json` file at the
  repository root" (all https://code.claude.com/docs/en/devcontainer). Ansible is idempotent: "When the system
  is in the state your playbook describes, Ansible does not change anything"
  (https://docs.ansible.com/ansible/latest/getting_started/introduction.html). Beads ships both a devcontainer
  and a Nix flake (https://github.com/steveyegge/beads .devcontainer/README.md:1 and flake.nix (commit
  d274841)). Self-hosted environments "are in public beta on Team and Enterprise plans and are off by
  default", use an environment key "Shown once at environment creation", and offer "a CI smoke test that
  verifies a runner image" (https://code.claude.com/docs/en/self-hosted-environments). *Worker inference:*
  for one non-Docker user the lowest-effort reproducible path is a plain Ubuntu VM or his own machine plus a
  committed `scripts/bootstrap.sh` that pins the Claude Code version, with the devcontainer as an optional
  second route for Codespaces; Nix and Packer are over-spec for one user; Ansible is a second tool to learn,
  fine later.
- *Composing the pieces.* Skills are namespaced but "hooks have no prefix, so a hook that is in both your
  settings file and `hooks/hooks.json` runs twice each time its event fires"
  (/home/user/Autonomy-Research/research/findings/packaging.md:122-125); "Manifest `version` pins users to the
  cached copy until the string changes" (packaging.md:71-75). Superpowers installs with `/plugin install
  superpowers@superpowers-marketplace` (https://github.com/obra/superpowers README.md:52-81 (commit bb92a77))
  and its manifest says `"version": "7.0.0",` (https://github.com/obra/superpowers .claude-plugin/plugin.json
  (commit bb92a77)). This repo's bootstrap already runs `claude plugin install superpowers@superpowers-marketplace
  >/dev/null 2>&1` only when `CLAUDE_CODE_REMOTE` is true, unpinned
  (/home/user/Autonomy-Research/scripts/cloud-setup.sh:8-18). The official Ralph plugin "implements Ralph using a
  **Stop hook** that intercepts Claude's exit attempts" with `--max-iterations` and `--completion-promise`
  (https://github.com/anthropics/claude-code plugins/ralph-wiggum/README.md:13,38 (commit 03b5892)). "Beads is a
  CLI tool you install once and use everywhere. You don't need to clone this repository into your project."
  (https://github.com/steveyegge/beads README.md:30-43,131 (commit d274841)); "The install scripts verify release
  checksums before install." (README.md:99-121 and README.md:110,121); its installer URL now points at
  `gastownhall/beads` while the repo stays `steveyegge/beads` (README.md:31). Plugin MCP tools are named
  `mcp__plugin_research-agent_<server>__<tool>` (/home/user/Autonomy-Research/plugin/skills/setup/SKILL.md:13-17).
  *Worker inferences:* compose as one repo = engineer plugin + `bootstrap.sh` that installs pinned third-party
  plugins (Superpowers) and CLIs (`bd`), recording commits in a `docs/versions.md`; do not vendor Superpowers'
  files; the collision risk is hooks (Superpowers SessionStart, Beads hooks, Ralph Stop, this repo's
  SessionStart), so spike an all-four install and count firings; Ralph/Beads stay Phase 2 behind a
  `bootstrap.sh --with-beads` flag; `bd init` mutates the work repo, so run it only there.
- *Connectors versus `.mcp.json`.* Connectors are "automatically available in Claude Code" when "your active
  authentication method is a claude.ai subscription login" (packaging.md:169-175); cloud "loads
  project-scoped servers without asking" (packaging.md:151-155); on a Remote Control machine "your
  filesystem, MCP servers, tools, and project configuration all stay available" but "API keys are not
  supported." (https://code.claude.com/docs/en/remote-control); a setup-token "can't ... fetch claude.ai
  connectors" (https://code.claude.com/docs/en/authentication). The repo's split is stated in its CLAUDE.md:
  "Exa, Context7, Parallel Search and Mermaid Chart come from claude.ai connectors, not this repo."
  (/home/user/Autonomy-Research/CLAUDE.md). *Worker inference:* three targets, three strategies: cloud =
  `.mcp.json` plus connectors; local with claude.ai login = both; VPS with API key or setup-token = `.mcp.json`
  only, so the research path must work on keyless `.mcp.json` servers alone and browser tooling (Playwright
  MCP) must be in `.mcp.json` with Node and browser binaries installed by the bootstrap.
- *Health checks.* The repo's setup skill probes tools by name and says "Do not edit settings, install
  anything, or add keys." and "a tool absent from your list is not yet proof it is missing."
  (/home/user/Autonomy-Research/plugin/skills/setup/SKILL.md:8-9,51-55 and :13-15); ECC ships "`node
  scripts/ecc.js doctor` / `repair`" (packaging.md:243,246, DeepWiki-derived); `claude plugin validate
  --strict` "Checks manifest, frontmatter, `.mcp.json`"
  (/home/user/Autonomy-Research/research/tool-registry.md:40-41). *Worker inference:* two layers, a
  deterministic `scripts/doctor.sh` (pinned Claude version, node, bd, git, env var names set, `claude plugin
  list`, `claude mcp list`) and `/research-agent:setup`, plus a smoke task graded with `file_exists`; in
  unattended mode run the probe at SessionStart, write a status file and fail closed if the sandbox check
  fails.

### Q6. What do OpenClaw and comparable always-on harnesses add as hosts, and should any be used?

**Confidence: high** on what OpenClaw is and how it hosts Claude Code (read in source); **medium** on
comparison and incident counts (READMEs and secondary pages; nothing was run).

- *OpenClaw.* "OpenClaw is an open-source AI assistant that runs on your own computer and meets you in the
  channels you already use: Discord, iMessage, Slack, Teams, Telegram, WhatsApp, and 20+ more"
  (https://github.com/openclaw/openclaw README.md:~20 (commit ca009ba)); installed as a daemon via `openclaw
  onboard --install-daemon` (README.md "Quick start"); MIT, "Copyright (c) 2026 OpenClaw Foundation"
  (LICENSE:1-3, package.json:3); worker inference (not in the source): package version 2026.10.4 with HEAD
  dated 2026-10-16. "Launched in 2025 by Peter Steinberger as Clawdbot, the project first rebranded to Moltbot
  after Anthropic requested a name change and rebranded again to OpenClaw at the end of January 2026."
  (https://www.infosecurity-magazine.com/news/malicious-crypto-trading-skills/). Its threat model: "OpenClaw is
  local-first agent infrastructure for trusted operators; it is not designed as a shared multi-tenant
  boundary" (SECURITY.md:5), and it excludes "Prompt injection without a policy, auth, approval, sandbox, or
  tool-boundary bypass." (SECURITY.md:52-53). "OpenClaw has already published over 255 GitHub Security
  Advisories." and "Attackers uploaded over 1,100 malicious skills to ClawHub"
  (https://www.ibm.com/think/x-force/what-openclaw-reveals-about-agentic-ai-security-risks); an earlier count
  was "386 malicious skills published on ClawHub" (Infosecurity page above). A competitor says "OpenClaw has
  nearly half a million lines of code, 53 config files, and 70+ dependencies" (NanoClaw README.md:36 (commit
  2105169), a competitor's claim).
- *How it hosts Claude Code.* "OpenClaw can run agent turns through a local AI CLI, such as Claude Code or
  Gemini CLI, instead of calling the provider API itself" (docs/gateway/cli-backends.md:9); "A backend with
  `bundleMcp: true` receives Gateway tools through a loopback MCP bridge." (:11); "The gateway service must have
  the CLI on its `PATH`." (~30). Alternatively "ACP Claude is a **harness session** with ACP controls, session
  resume, background-task tracking, and optional conversation/thread binding." (docs/tools/acp-agents.md:69-78)
  through a stack of "OpenClaw ACP session control plane. Official @openclaw/acpx runtime plugin. Claude ACP
  adapter. Claude-side runtime/session machinery." (:71-76); the reverse direction is `openclaw mcp serve`
  (:25). Sandboxing "is off by default and controlled by `agents.defaults.sandbox`"
  (docs/gateway/sandboxing.md:9), "is not a perfect security boundary" (:12), with modes "`off`, `non-main`,
  `all`" (docs/gateway/sandboxing/modes-scope-and-backend.md:15-17); "container images default to an exposed
  bind" (docs/gateway/security/index.md:7); the hardened baseline sets `exec: { security: "deny", ask: "always"
  }` (docs/gateway/security/hardened-baseline.md:~20). *Worker inference:* the permission model becomes
  two-layered (OpenClaw tool policy plus Claude Code's own), so approvals can be double-gated or silently
  bypassed depending on config (not tested); whether Claude Code's prompts surface through OpenClaw chat is
  undetermined.
- *Comparables.* NanoClaw: "Agents run in their own Linux containers with filesystem isolation, not merely
  behind permission checks." and "agents never hold raw API keys. Outbound requests route through a credential
  gateway that injects credentials at request time" (NanoClaw README.md:36-38, 77, 97 (commit 2105169)), MIT
  (LICENSE:1-3). Hermes Agent (Nous Research, MIT, LICENSE:1-3): "Seven terminal backends — local, Docker, SSH,
  Singularity, Modal, Daytona, and Vercel Sandbox.", "Built-in cron scheduler with delivery to any platform.",
  "A closed learning loop" (Hermes README.md:25-29, 27 (commit 9c002cb)). *Worker inference:* ranking from
  feature lists only: breadth OpenClaw > Hermes > NanoClaw; isolation NanoClaw > Hermes (Docker backend) >
  OpenClaw (sandbox off by default); Claude Code fit NanoClaw > OpenClaw > Hermes. The note's statement that
  NanoClaw embeds Claude Code via the Claude Agent SDK has no quoted line behind it and is carried as an open
  question.
- *What Claude Code already covers.* Channels push events "from a chat app like Telegram or Discord, or your
  own server" (https://code.claude.com/docs/en/channels, "How channels compare"); Remote Control is
  outbound-only (https://code.claude.com/docs/en/remote-control); durable scheduling is Routines, Desktop tasks
  or GitHub Actions (https://code.claude.com/docs/en/scheduled-tasks); and the Agent SDK is "A library that runs
  the Claude Code binary, with Claude Code's capabilities, such as built-in tools, permissions, sessions, and
  hooks." (https://code.claude.com/docs/en/agent-sdk/overview). *Worker inference:* a harness adds a 20+
  channel surface, a persistent daemon, cross-session memory, multi-model fallback and (NanoClaw) per-agent
  containers, but no engineering capability; it adds attack surface and a second permission model, and a daily
  release cadence to patch. Recommendation from the note: do not make OpenClaw the host; if a Slack/WhatsApp
  control channel is needed, spike NanoClaw first and OpenClaw second, inside the VM, with `openclaw security
  audit`, sandbox `all` and no ClawHub skills.

**Contradictions.** (1) Malicious ClawHub skill counts differ by date and source: "386" (Infosecurity, Feb 2026)
versus "over 1,100" (IBM, Oct 2026), and a 341 figure in a headline URL cited by IBM; the same campaign at
different dates, so no single number is final. (2) A third-party blog (remoteopenclaw.com, not opened) is
reported to say Claude Code has no messaging integrations; the opened Anthropic page lists Channels for
Telegram, Discord and iMessage (https://code.claude.com/docs/en/channels). The docs win; the blog is not a
source here. (3) Subscription use through a harness: see Q2 contradiction (2).

### Q7. Recommendation, alternatives, rejected candidates, spike list

**Confidence: medium.** The facts above are mostly high-confidence; the recommendation is a synthesis of four
workers' facet recommendations, which agree on the split and differ only in emphasis (the cloud-sessions
worker put Routines first for repo work; the self-hosted, packaging and harness workers put a John-controlled
VM first). Because the brief requires browser work with John's logins and chat-relayed approvals, which the
evidence places only on a machine John controls (Q3, Q4), the VM is the core and cloud is the companion.

**One recommendation.** Run the engineer as the unmodified Claude Code binary on one plain Ubuntu VM John
controls (a small VPS or a home box), under a dedicated non-root user, signed in with his Max subscription by
`/login` (not `setup-token`, which disables Remote Control, connectors and Chrome:
https://code.claude.com/docs/en/authentication, https://code.claude.com/docs/en/chrome), kept running in a
background process with a watchdog, with Channels (Telegram allowlist) plus Remote Control push for approvals
(https://code.claude.com/docs/en/channels, https://code.claude.com/docs/en/remote-control), a dedicated
persistent Chromium profile for logins (pattern: https://github.com/browser-use/bux), deny rules and
`auto`/allowlist mode rather than blanket bypass (https://code.claude.com/docs/en/permission-modes). Package
it as the single template-plus-plugin repo from packaging.md with a pinned `scripts/bootstrap.sh` (Claude
Code version, Superpowers by marketplace, optional `bd`, Node and Playwright browsers), `.env.example` with
names only, `scripts/doctor.sh` and the `/setup` skill as verifier; no Docker is required for this route
(https://code.claude.com/docs/en/sandbox-environments). Use cloud Routines as the companion for GitHub-only
overnight jobs that need neither logins nor prompts, with outputs on `claude/` branches and a Slack digest for
morning review (https://code.claude.com/docs/en/routines).

**Alternatives.** (a) Cloud Routines alone, if browser logins are dropped from scope: zero setup, no VM charge,
GitHub-bound (https://code.claude.com/docs/en/claude-code-on-the-web). (b) GitHub Actions with
`CLAUDE_CODE_OAUTH_TOKEN` for cron/CI-bound jobs (https://code.claude.com/docs/en/github-actions). (c) A spare
Mac with Remote Control server mode or Desktop scheduled tasks, which also unlocks 1Password for Claude
(Mac-only: https://1password.com/blog/1password-for-claude). (d) A Codespaces devcontainer as route two, where
Docker is hidden (https://code.claude.com/docs/en/devcontainer). (e) An Agent SDK daemon for a custom always-on
service (https://code.claude.com/docs/en/agent-sdk/overview). (f) NanoClaw, only if a Slack/WhatsApp control
channel is needed (container per agent: NanoClaw README.md:36-38).

**Rejected.** OpenClaw as host: sandbox off by default, "over 255 GitHub Security Advisories", ClawHub malware,
a second permission model, and Claude Code already has Channels/Remote Control/Routines (Q6). Hermes Agent: not
Claude Code-centric (Hermes README.md:25-29). `/loop` for overnight work: 7-day expiry and needs an open session
(https://code.claude.com/docs/en/scheduled-tasks). Cloud sessions for logged-in browsing: no documented browser,
no login state, SSO unsupported (https://code.claude.com/docs/en/cloud-environments). Claude in Chrome
unattended: visible window, pauses on login/CAPTCHA, service worker idles (https://code.claude.com/docs/en/chrome).
Self-hosted environments: Team/Enterprise only (https://code.claude.com/docs/en/self-hosted-environments).
`setup-token` or API-key auth as the VM's primary auth: loses Remote Control, connectors and Chrome
(https://code.claude.com/docs/en/authentication); keep an API key only as an overflow fallback with
`--max-budget-usd` (worker inference). `--bare`: ignores OAuth (https://code.claude.com/docs/en/headless). Nix,
Packer, Ansible for v1: more to learn than one user gains (worker inference; Nix and Packer were not researched
from opened pages). Ralph and Beads as default installs: Phase 2 behind a flag (worker inference, consistent
with the registry).

**Spike list (must be tried for real before building).**
1. Overnight VM run: Claude Code with `--channels plugin:telegram` (allowlist) plus Remote Control in a
   throwaway VM; measure unattended stability, restart on 401/stall, and whether permission prompts stall or
   relay. (harness and self-hosted notes)
2. Longest Routine run actually allowed and its usage cost against the Max 5-hour/weekly windows; confirm how
   the Oct 7, 2026 "monthly API credits" interact with `claude -p` on Max. (cloud and self-hosted notes)
3. Headless Chromium/Playwright install in the cloud setup script under Full network, and Playwright browser
   download inside the VM bootstrap. (cloud and packaging notes)
4. Routine writes a Slack/email digest via connector and a morning approval round-trips through a GitHub-event
   routine or `claude -p ... --cloud <id>`. (cloud note)
5. All-four-plugin hook collision count: Superpowers, Beads (`bd setup claude`), Ralph Stop hook, this repo's
   SessionStart. (packaging note)
6. Connector visibility on the VM under `/login` versus `setup-token` auth. (packaging note)
7. Claude in Chrome on an unattended headed machine with a logged-in profile. (cloud note)
8. Codespaces `~/.claude` persistence with the `CLAUDE_CONFIG_DIR` mount; pinning a third-party marketplace to
   a tag. (packaging note)
9. Agent SDK daemon triggered by webhook/cron with hooks as guardrails, compared with Routines. (harness note)
10. Only if a Slack/WhatsApp channel is required: NanoClaw in a VM with an API key through its credential
    gateway; then OpenClaw `claude-cli` backend with `openclaw security audit`, sandbox `all`, no ClawHub
    skills, testing whether Claude Code prompts reach chat. (harness note)
11. Re-read Anthropic's current support article on harness and Agent SDK billing before committing a
    subscription to any of the above. (harness note)

## Evidence

All opened 2026-10-16. Repo citations are kept as the notes wrote them. "Tool not stated in note" marks
pages the harness note lists as opened without naming the tool; where another note opened the same page with
a stated tool, that tool is given.

Cloud sessions note:
- C1 https://code.claude.com/docs/en/claude-code-on-the-web — WebFetch — Cloud sessions are on Pro/Max/Team plans, run on Anthropic VMs, keep running after laptop closes, and have no separate VM charge. Quote: "It counts toward your plan's usage limits alongside the rest of your Claude and Claude Code usage, and there's no separate charge for the cloud VM."
- C2 https://code.claude.com/docs/en/cloud-environments — WebFetch — Four network levels (None, Trusted, Full, Custom); default environment is Trusted. Quote: "**Trusted** | Allowlisted domains only: package registries, GitHub, cloud SDKs | **Full** | Any domain | **Custom** | Your own allowlist"
- C3 https://code.claude.com/docs/en/routines — WebFetch — Blocked hosts fail with 403; connectors bypass the allowlist (routed via Anthropic servers). Quote: "Requests on that path to hosts outside the allowlist fail with `403` and `x-deny-reason: host_not_allowed`."
- C4 https://code.claude.com/docs/en/cloud-environments — WebFetch — VM size. Quote: "4 vCPUs * 16 GB of RAM * 30 GB of disk"
- C5 https://code.claude.com/docs/en/cloud-environments — WebFetch — Idle behaviour: pause after a few minutes, later reclaimed; reclaimed VM restores conversation but not background work. Quote: "after a few minutes without activity, a session's VM pauses with its files saved. Your next message restores the same VM"
- C6 https://code.claude.com/docs/en/claude-code-on-the-web — WebFetch — Reclaimed VM loses background processes and self-paced loop wakeups. Quote: "Not restored: background work that was still running when the VM was reclaimed, such as subagents and shell commands"
- C7 https://code.claude.com/docs/en/claude-code-on-the-web — WebFetch — Waiting on an MCP connector approval counts as inactive and can expire. Quote: "A session counts as inactive while it waits for you to approve an MCP connector tool call or to sign in to an MCP server, and it can expire during that wait."
- C8 https://code.claude.com/docs/en/cloud-environments — WebFetch — Command time limits: 2 min default / 10 min max foreground, then moved to background up to 30 more minutes. Quote: "Claude waits 2 minutes for a foreground command by default and can ask for up to 10 minutes."
- C9 https://code.claude.com/docs/en/cloud-environments — WebFetch — Env var timeouts are tunable. Quote: "add BASH_DEFAULT_TIMEOUT_MS and BASH_MAX_TIMEOUT_MS to its environment variables"
- C10 https://code.claude.com/docs/en/cloud-environments — WebFetch — Setup script cached only if under ~5 minutes. Quote: "keep the script's total runtime under roughly five minutes so the environment cache can build."
- C11 https://code.claude.com/docs/en/cloud-environments — WebFetch — Env vars readable by anyone using the environment; use network secrets for keys. Secrets stay outside the VM, proxy attaches them to listed hosts; cannot be edited, only deleted and re-added. Quote: "Anthropic's agent proxy adds the key to requests for the hosts you list, after each request leaves the session's VM, so the key itself stays outside the VM."
- C12 https://code.claude.com/docs/en/cloud-environments — WebFetch — Repo-loaded files: .mcp.json, hooks, skills, agents, rules load in a single-repo session. Quote: "Your repo's `.mcp.json` MCP servers | Yes, in a session with one repository | Part of the clone, found from the session's working directory."
- C13 https://code.claude.com/docs/en/cloud-environments — WebFetch — Plugins declared in repo settings are NOT installed. Quote: "A cloud session doesn't install the plugins a repository turns on under `enabledPlugins`, including ones from the marketplaces it lists under `extraKnownMarketplaces`"
- C14 https://code.claude.com/docs/en/cloud-environments — WebFetch — User-level skills/CLAUDE.md/user MCP servers do not carry over. Quote: "Live on your machine, not in the repo. Commit them to the repo's `.claude/` directory instead."
- C15 https://code.claude.com/docs/en/cloud-environments — WebFetch — Pre-installed: Docker, Postgres 16, Redis 7, chromedriver (Node row); no browser listed beyond chromedriver. Quote: "Docker | docker, dockerd, docker compose | Databases | PostgreSQL 16, Redis 7.0"
- C16 https://code.claude.com/docs/en/claude-code-on-the-web — WebFetch — GitHub-only for clone/PR; non-GitHub repos can be bundled but cannot push back. Quote: "repository cloning and pull request creation require GitHub."
- C17 https://code.claude.com/docs/en/cloud-environments — WebFetch — Interactive auth (SSO) unsupported. Quote: "SSO requires browser-based login that can't run in a cloud session"
- C18 https://code.claude.com/docs/en/claude-code-on-the-web — WebFetch — Self-hosted environment option (Team/Enterprise only) exists for own compute. Quote: "Self-hosted environments | Start a cloud session and pick your organization's environment | Your organization's infrastructure | Deploy runners, on Team and Enterprise plans"
- C19 https://code.claude.com/docs/en/routines — WebFetch — Routines have three trigger types, run on Anthropic cloud, available on Max. Quote: "Routines are available on Pro, Max, Team, and Enterprise plans."
- C20 https://code.claude.com/docs/en/routines — WebFetch — Research preview, behaviour may change. Quote: "Routines are in research preview. Behavior, limits, and the API surface may change."
- C21 https://code.claude.com/docs/en/routines — WebFetch — Runs are fully autonomous, no approval. Quote: "Routines run autonomously as full Claude Code cloud sessions: there is no permission-mode picker"
- C22 https://code.claude.com/docs/en/routines — WebFetch — Connector writes happen without asking. Quote: "Claude can use every tool from an included connector, including writes, without asking for permission during a run."
- C23 https://code.claude.com/docs/en/routines — WebFetch — Minimum schedule interval 1 hour, starts can be minutes late. Quote: "The minimum interval is one hour; expressions that run more frequently are rejected."
- C24 https://code.claude.com/docs/en/routines — WebFetch — Rate caps. Quote: "Scheduled runs, including one-off runs | 100 per hour | Your account"
- C25 https://code.claude.com/docs/en/routines — WebFetch — API trigger: POST /fire with bearer token and optional text, beta header. Quote: "The `/fire` endpoint ships under the `experimental-cc-routine-2026-04-01` beta header."
- C26 https://code.claude.com/docs/en/routines — WebFetch — Fire text is wrapped as untrusted; prompt must opt in. Quote: "It arrives wrapped in a `<routine-fire-payload>` block that labels it as untrusted data"
- C27 https://code.claude.com/docs/en/routines — WebFetch — Status green does not mean task succeeded. Quote: "A green status in the run list means the session started and exited without an infrastructure error. It does not mean the task in your prompt succeeded."
- C28 https://code.claude.com/docs/en/routines — WebFetch — Routines skip runs if GitHub connection lapses; off after 72 h. Quote: "After 72 hours without a connection, the routine turns off"
- C29 https://code.claude.com/docs/en/routines — WebFetch — Branch pushes go to `claude/` prefixed branches; use branch protection to restrict. Quote: "Claude pushes its work to a branch prefixed with `claude/` unless your prompt directs it to push to another branch."
- C30 https://code.claude.com/docs/en/scheduled-tasks — WebFetch — Comparison of scheduling options (cloud vs desktop vs /loop). Quote: "Requires machine on | No | Yes | Yes"
- C31 https://code.claude.com/docs/en/scheduled-tasks — WebFetch (also cited by the harness note) — /loop recurring tasks expire after 7 days and only fire while a session is open. Quote: "Recurring tasks automatically expire 7 days after creation."
- C32 https://code.claude.com/docs/en/routines — WebFetch — Routines cannot be created from inside a cloud session (/schedule unavailable there). Quote: "You are inside a cloud session, where submitting `/schedule` answers that the command isn't available in that environment."
- C33 https://code.claude.com/docs/en/claude-code-on-the-web — WebFetch — Follow-ups can be queued into a running cloud session from any CLI/CI. Quote: "claude -p "your message" --cloud <session-id>"
- C34 https://code.claude.com/docs/en/claude-code-on-the-web — WebFetch — Auto-fix PR: session subscribes to CI failures and review comments, asks when ambiguous. Quote: "Ambiguous requests: if a reviewer's comment could be interpreted multiple ways or involves something architecturally significant, Claude asks you before acting"
- C35 https://code.claude.com/docs/en/github-actions — WebFetch — GitHub Actions: schedule cron works in automation mode; runs on GitHub runners; OAuth token uses subscription. Quote: "If you authenticate with an OAuth token, runs use your Claude subscription instead of API billing."
- C36 https://code.claude.com/docs/en/github-actions — WebFetch — GitHub Actions schedule caveat. Quote: "GitHub runs scheduled workflows only from the default branch and, in public repositories, disables the schedule after 60 days without repository activity."
- C37 https://code.claude.com/docs/en/github-actions — WebFetch — Actions cost controls: max-turns and workflow timeouts. Quote: "Set `--max-turns` in `claude_args` to limit iterations"
- C38 https://code.claude.com/docs/en/chrome — WebFetch — Claude in Chrome reuses the logged-in browser. Quote: "Claude opens new tabs for browser tasks and shares your browser's login state, so it can access any site you're already signed into."
- C39 https://code.claude.com/docs/en/chrome — WebFetch — It is visible, and pauses on login/CAPTCHA. Quote: "Browser actions run in a visible Chrome window in real time. When Claude encounters a login page or CAPTCHA, it pauses and asks you to handle it manually."
- C40 https://code.claude.com/docs/en/chrome — WebFetch — Needs claude.ai login; API key or setup-token disables it. Quote: "If you authenticate with an API key or a long-lived token from `claude setup-token`, Claude Code keeps Chrome integration off"
- C41 https://code.claude.com/docs/en/chrome — WebFetch — Not in WSL; service worker can go idle on long sessions. Quote: "The Chrome extension's service worker can go idle during extended sessions, which breaks the connection."
- C42 https://code.claude.com/docs/en/chrome — WebFetch — A repo cannot enable Chrome itself. Quote: "a repository you check out must not be able to connect Claude to your browser."
- C43 https://code.claude.com/docs/en/remote-control — WebFetch — Remote Control: execution stays on the user's machine, all local tools/MCP available. Quote: "When you start a Remote Control session on your machine, Claude keeps running locally the entire time, so your code execution and filesystem access stay on your machine."
- C44 https://code.claude.com/docs/en/remote-control — WebFetch — Remote Control server mode can turn on Chrome for spawned sessions. Quote: "Turn Chrome integration on or off in the sessions the server creates, so Claude can use Chrome on your machine while you work from another device."
- C45 https://code.claude.com/docs/en/remote-control — WebFetch (also cited by the self-hosted note) — Remote Control server mode: up to 32 concurrent sessions, worktree spawn; gives up after ~10 min outage. Quote: "Server mode: Claude Code gives up after roughly 10 minutes and the `claude remote-control` process exits."
- C46 https://code.claude.com/docs/en/remote-control — WebFetch (also cited by the self-hosted and packaging notes) — Remote Control is Pro/Max/Team/Enterprise, no API keys. Quote: "available on Pro, Max, Team, and Enterprise plans. API keys are not supported."
- C47 https://code.claude.com/docs/en/cloud-environments — WebFetch — Cloud docs point heavy workloads to Remote Control on own hardware. Quote: "use Remote Control to run Claude Code on your own hardware, or run cloud sessions in a self-hosted environment"
- C48 https://code.claude.com/docs/en/scheduled-tasks — WebFetch — Desktop scheduled tasks run locally with local files (machine on, no open session). Quote: "Desktop | Runs on | Your machine"
- C49 https://code.claude.com/docs/en/routines — WebFetch — Routines can post summaries to Slack (connector). Quote: "posts a summary to Slack so the team starts the day with a groomed queue."
- C50 https://code.claude.com/docs/en/claude-code-on-the-web — WebFetch — Cloud session: a question left unanswered keeps the session until environment expiry; answer later continues it. Quote: "If Claude asks a question and the session sits idle, you can still answer when you come back, up to environment expiry"
- C51 https://code.claude.com/docs/en/remote-control — WebFetch — Remote Control push notifications for decisions. Quote: "Claude decides when to push. It typically sends one when a long-running task finishes or when it needs a decision from you to continue."
- C52 https://code.claude.com/docs/en/remote-control — WebFetch — Permission prompt pushes toggle. Quote: "enable **Push when Claude decides** for proactive notifications, **Push when actions required** for permission prompts and questions, or both."
- C53 https://code.claude.com/docs/en/remote-control — WebFetch — Prompts held open until answered. Quote: "Claude Code keeps permission prompts and `AskUserQuestion` questions open until you answer them."
- C54 https://code.claude.com/docs/en/channels — WebFetch — Channels: Telegram, Discord, iMessage plugins; research preview; session must be open. Quote: "Events only arrive while the session is open, so for an always-on setup you run Claude in a background process or persistent terminal."
- C55 https://code.claude.com/docs/en/channels — WebFetch — Channels can relay permission prompts to the user. Quote: "Channel servers that declare the permission relay capability can forward these prompts to you so you can approve or deny remotely."
- C56 https://code.claude.com/docs/en/channels — WebFetch — Channels apply to a running local session, not spawned cloud sessions. Quote: "Channels fill the gap in that list by pushing events from non-Claude sources into your already-running local session."
- C57 https://code.claude.com/docs/en/channels — WebFetch (also cited by the harness note) — Channel allowlist: anyone who can reply can approve tools. Quote: "Anyone who can reply through the channel can approve or deny tool use in your session, so only allowlist senders you trust with that authority."
- C58 https://code.claude.com/docs/en/channels — WebFetch (also cited by the harness note) — Unattended local alternative: skip-permissions flag with caveat. Quote: "--dangerously-skip-permissions bypasses most prompts, but only use it in environments you trust."
- C59 https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan — WebFetch — Max/Pro have 5-hour and weekly limits shared across Claude and Claude Code. Quote: "Both Pro and Max plans have a five-hour session limit and a weekly limit."
- C60 https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan — WebFetch — Shared across surfaces. Quote: "These limits are shared across Claude and Claude Code"
- C61 https://code.claude.com/docs/en/claude-code-on-the-web — WebFetch — Cloud usage counts against plan; parallel tasks multiply consumption. Quote: "Running multiple tasks in parallel consumes more rate limits proportionately."
- C62 https://code.claude.com/docs/en/routines — WebFetch — Routine behaviour at limit. Quote: "Without usage credits, additional runs are rejected until your usage window resets."
- C63 https://code.claude.com/docs/en/routines — WebFetch — Overage possible on metered credits. Quote: "organizations with usage credits turned on can keep running routines on metered overage."
- C64 https://code.claude.com/docs/en/routines — WebFetch — Hourly caps have no overage. Quote: "None of these hourly limits has overage."
- C65 https://code.claude.com/docs/en/routines — WebFetch — Routine run caps per routine. Quote: "Run now, API fires, and setting a one-off routine to run again | 30 per hour | Each routine"
- C66 https://code.claude.com/docs/en/claude-code-on-the-web — WebFetch — Cloud sessions unavailable on API-key auth or Bedrock/Vertex. Quote: "`--cloud` requires an Anthropic account. It's not available when Claude Code is configured for Amazon Bedrock, Google Cloud's Agent Platform, or another third-party provider."
- C67 https://code.claude.com/docs/en/claude-code-on-the-web — WebFetch — ZDR/HIPAA/CMEK orgs cannot use cloud sessions (not relevant to a personal Max account). Quote: "Organizations with Zero Data Retention enabled, or with the HIPAA configuration applied, can't use `/web-setup` or other cloud session features."
- C68 https://code.claude.com/docs/en/github-actions — WebFetch — GitHub Actions can run on the Max subscription via OAuth token. Quote: "`CLAUDE_CODE_OAUTH_TOKEN`: an OAuth token that authenticates with your Claude subscription, available on Pro, Max, Team, and Enterprise plans."

Self-hosted always-on note:
- S1 https://code.claude.com/docs/en/headless — WebFetch — `claude -p` is the non-interactive entry point and is the Agent SDK as a CLI. Quote: "To run Claude Code in non-interactive mode, pass `-p` with your prompt and the CLI options you need"
- S2 https://code.claude.com/docs/en/headless — WebFetch — `--bare` is recommended for scripts but never reads OAuth or keychain, so it needs an API key. Quote: "In bare mode, Claude Code never reads OAuth credentials or the system keychain."
- S3 https://code.claude.com/docs/en/headless — WebFetch — Without `--bare`, a `-p` session runs project hooks and MCP servers with no trust prompt (matters if the VM clones untrusted repos). Quote: "A `-p` session shows no workspace trust dialog and no per-server approval prompt."
- S4 https://code.claude.com/docs/en/headless — WebFetch — Unattended-specific flag: deny anything that would prompt. Quote: "Pass `--permission-prompts none` when nobody is available to answer permission prompts, for example in a scheduled job."
- S5 https://code.claude.com/docs/en/headless — WebFetch — Exit codes and cost visibility for scripts. Quote: "the response payload includes `total_cost_usd` and a per-model cost breakdown"; also "Both figures are client-side estimates and can differ from your actual bill."
- S6 https://code.claude.com/docs/en/headless — WebFetch — A `-p` run stays open for background work but kills idle waits after 10 minutes by default. Quote: "stops whatever is still running after 10 minutes of continuous idle waiting by default and drops its partial result."
- S7 https://code.claude.com/docs/en/permission-modes (saved fetch, table row) — WebFetch — Fully unattended recipe and its required isolation. Quote: "Run fully unattended inside a container | `claude -p "<prompt>" --dangerously-skip-permissions` | Required: a container, VM, or the sandbox runtime"
- S8 https://code.claude.com/docs/en/permission-modes — WebFetch — bypassPermissions warning. Quote: "Only use this mode in isolated environments like containers, VMs, or dev containers without internet access, where Claude Code cannot damage your host system."
- S9 https://code.claude.com/docs/en/permission-modes — WebFetch — Deny rules still hold under bypass. Quote: "Deny rules block in every mode, including `bypassPermissions`."
- S10 https://code.claude.com/docs/en/security — WebFetch — Auto mode (classifier) is the middle option and is now the default start mode in interactive sessions (v2.1.283+). Quote: "A separate classifier model reviews actions instead of you and blocks the ones it judges unsafe."
- S11 https://code.claude.com/docs/en/security — WebFetch — Anthropic's security page advises VMs for external web work and the dev container / sandbox runtime for whole-process isolation. Quote: "Use virtual machines (VMs) to run scripts and make tool calls, especially when interacting with external web services"
- S12 https://code.claude.com/docs/en/authentication — WebFetch — Long-lived token for headless use, from a Max plan. Quote: "generate a one-year OAuth token with `claude setup-token`"
- S13 https://code.claude.com/docs/en/authentication — WebFetch — That token's limits. Quote: "It can only make model requests, so it can't establish Remote Control sessions or fetch claude.ai connectors."
- S14 https://code.claude.com/docs/en/authentication — WebFetch — `--bare` ignores the token. Quote: "Bare mode does not read `CLAUDE_CODE_OAUTH_TOKEN`."
- S15 https://code.claude.com/docs/en/authentication — WebFetch — An API key in the environment silently overrides the subscription (cost trap). Quote: "In non-interactive mode (`-p`), the key is always used when present."
- S16 https://code.claude.com/docs/en/authentication — WebFetch — Subscription login on a headless box is an accepted case. Quote: "This happens when the browser can't reach Claude Code's local callback server, which is common in WSL2, SSH sessions, and containers."
- S17 https://code.claude.com/docs/en/authentication — WebFetch — Credentials live in a plain file on Linux. Quote: "On Linux, credentials are stored in `~/.claude/.credentials.json` with file mode `0600`."
- S18 https://code.claude.com/docs/en/legal-and-compliance — WebFetch — Terms: who may use OAuth, and the developer rule. Quote: "Advertised usage limits for Pro and Max plans assume ordinary, individual usage of Claude Code and the Agent SDK."
- S19 https://code.claude.com/docs/en/legal-and-compliance — WebFetch (also cited by the harness note) — Restriction on third parties. Quote: "Anthropic does not permit third-party developers to offer Claude.ai login into their own applications, or to route requests through Free, Pro, or Max plan credentials on behalf of their users."
- S20 https://code.claude.com/docs/en/legal-and-compliance — WebFetch — Own use of the unmodified binary is allowed. Quote: "Nor does it prevent an end user from signing in to the unmodified Claude Code binary with their own Claude subscription"
- S21 https://code.claude.com/docs/en/legal-and-compliance — WebFetch — Enforcement. Quote: "Anthropic reserves the right to take measures to enforce these restrictions and may do so without prior notice."
- S22 https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan — WebFetch — Usage limits are shared and windowed. Quote: "Both Pro and Max plans have a five-hour session limit and a weekly limit."
- S23 https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan — WebFetch — Claude chat and Claude Code share one allowance. Quote: "all activity in both tools counts against the same limits"
- S24 https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan — WebFetch — Agent SDK / `claude -p` billing status, latest update. Quote: "We've paused the previously-announced changes to Claude Agent SDK usage." (June 15, 2026 update) and "Claude Max and Team plans now include monthly API credits, which cover the Claude Agent SDK" (Oct 7, 2026 update).
- S25 https://www.virtua.cloud/learn/en/tutorials/run-claude-code-vps (2026-03-19) — WebFetch — VPS sizing and cost for a Max/Pro-login setup. Quote: "Claude Code runs on your existing Claude subscription with no additional fee." (guide estimates roughly 10-20 EUR/month for 4 vCPU/8 GB; 4 GB handles a medium codebase)
- S26 https://www.virtua.cloud/learn/en/tutorials/run-claude-code-vps — WebFetch — Subscription login on headless server. Quote: "generate an OAuth token on a machine with a browser, then transfer it to the VPS."
- S27 https://www.ssdnodes.com/learn/claude-code-on-a-vps-with-tmux (2026-07-14) — WebFetch — tmux guide: failure modes. Quote: "The OOM killer may also pick the tmux server rather than the build, taking your session with it."
- S28 https://www.ssdnodes.com/learn/claude-code-on-a-vps-with-tmux — WebFetch — Non-root advice. Quote: "That one decision removes most of the ways a stray shell command can wreck the host."
- S29 https://github.com/browser-use/bux — WebFetch — Browser Use "bux": a $5 Ubuntu VPS, Claude logged in, real Chromium with persistent cookies. Quote: "Ubuntu 22.04+ with ≥2GB RAM. A $5/mo VPS is fine."
- S30 https://github.com/browser-use/bux — WebFetch — Handling logins/2FA. Quote: "A real Chromium session via browser-harness — cookies persist, logins stick"
- S31 https://1password.com/blog/1password-for-claude — WebFetch — 1Password for Claude: the model never sees secrets; Mac only. Quote: "Claude never sees the vault item, password, or one-time code."
- S32 https://1password.com/blog/1password-for-claude — WebFetch — Availability. Quote: "1Password for Claude is available now for Mac, across business, family, and individual plans."
- S33 https://github.com/browser-use/bux — WebFetch — bux hands the human a live view on login walls. Quote: "no credential-stuffing, no brittle workarounds"
- S34 https://dev.to/drickon/the-token-is-valid-but-your-headless-claude-code-agent-just-401d-forever-48ip (2026-06-28) — WebFetch — Static Max token can 401 permanently on one instance until restart. Quote: "once it 401s the instance hard-latches and never self-recovers until you restart the process."
- S35 https://dev.to/drickon/the-token-is-valid-but-your-headless-claude-code-agent-just-401d-forever-48ip — WebFetch — Workaround is a watchdog. Quote: "A restart is the only thing that clears the latch."
- S36 https://code.claude.com/docs/en/authentication — WebFetch — Anthropic docs confirm the symptom: unattended sessions stall on expiry. Quote: "A background session in agent view or a Remote Control session that outlives the login stops making progress once the credential expires"
- S37 https://code.claude.com/docs/en/costs — WebFetch — Long sessions get expensive. Quote: "a one-line question in a session that has been open all day still draws usage for the whole conversation."
- S38 https://code.claude.com/docs/en/costs — WebFetch — Compaction cost. Quote: "`/compact` reads the conversation it summarizes, so compacting a large context is itself a large request."
- S39 https://code.claude.com/docs/en/costs — WebFetch — Idle cost: scheduled tasks and goals keep spending. Quote: "a scheduled task fires on its interval even while the session is idle, sending your full context each time"
- S40 https://code.claude.com/docs/en/costs — WebFetch — Cache lifetime shifts when on credits. Quote: "The lifetime is an hour on a subscription and drops to five minutes once you're drawing on usage credits"
- S41 https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan and https://code.claude.com/docs/en/costs — WebFetch — Hitting a limit mid-run. Quote: "is small and capped" (wrap-up allowance) ; and the costs page says Claude Code (v2.1.234+) can "wait and continue the interrupted task automatically after the reset".
- S42 https://code.claude.com/docs/en/security — WebFetch — Prompt injection and web content. Quote: "no system is completely immune to all attacks."
- S43 https://www.ssdnodes.com/learn/claude-code-on-a-vps-with-tmux — WebFetch — Skip-permissions on a credentialed server. Quote: "removes the last thing standing between a misread instruction and a `git push --force`."
- S44 https://code.claude.com/docs/en/headless — WebFetch — SIGTERM leaves the turn unfinished. Quote: "Claude Code leaves the turn that was in progress unfinished and records no result for it."
- S45 https://code.claude.com/docs/en/costs — WebFetch — Agent teams cost. Quote: "Agent teams use approximately 7x more tokens than standard sessions when teammates run in plan mode"

Packaging and composition note:
- P1 https://code.claude.com/docs/en/sandbox-environments — WebFetch — Anthropic's own comparison table lists Docker required: no for sandbox runtime, VM and cloud sessions; yes for dev container and custom container; VM setup effort "High", cloud sessions "None". Quote: "Virtual machine | Full operating system | No | High"
- P2 https://code.claude.com/docs/en/sandbox-environments — WebFetch — Cloud sessions need no setup but need a Claude subscription and GitHub (or `--cloud` upload). Quote: "None; requires a Claude subscription, and a connected GitHub account unless you launch with `claude --cloud`"
- P3 https://code.claude.com/docs/en/sandbox-environments — WebFetch — Unattended runs must sit inside a container, VM or sandbox runtime. Quote: "Always run `--dangerously-skip-permissions` sessions inside a container, a VM, or the sandbox runtime"
- P4 https://code.claude.com/docs/en/devcontainer — WebFetch — Devcontainer minimum is a 4-line devcontainer.json using the Claude Code Feature; the feature version tag pins the install script, not Claude Code. Quote: "The version tag at the end, such as `:1.0`, pins the feature's install script, not the Claude Code release."
- P5 https://code.claude.com/docs/en/devcontainer — WebFetch — Exact Claude Code pinning needs a Dockerfile npm install plus autoupdate off. Quote: "To pin a specific Claude Code version for reproducible builds, install it from your Dockerfile with `npm install -g @anthropic-ai/claude-code@X.Y.Z`"
- P6 https://code.claude.com/docs/en/devcontainer — WebFetch — Devcontainer needs an editor plus Docker (or Codespaces) on the user side. Quote: "A dev container runs as a Docker container, either on your machine or on a cloud host such as GitHub Codespaces."
- P7 https://code.claude.com/docs/en/devcontainer — WebFetch — Anthropic calls its reference container an example, not a maintained base. Quote: "It is provided as a working example rather than a maintained base image"
- P8 https://code.claude.com/docs/en/devcontainer — WebFetch — The reference container needs NET_ADMIN for its firewall, and the firewall is optional. Quote: "The firewall script and these capabilities are not required for Claude Code itself"
- P9 https://code.claude.com/docs/en/sandbox-environments — WebFetch — The devcontainer is a convention, not enforcement. Quote: "This is a convention rather than an enforcement boundary, because Claude Code does not require a container."
- P10 https://code.claude.com/docs/en/self-hosted-environments — WebFetch — Self-hosted cloud-session environments exist but are Team/Enterprise public beta and mean you "build and maintain the runner image". Quote: "Self-hosted environments are in public beta on Team and Enterprise plans and are off by default."
- P11 https://docs.ansible.com/ansible/latest/getting_started/introduction.html — Parallel web_fetch — Ansible is agentless, SSH-based, idempotent. Quote: "When the system is in the state your playbook describes, Ansible does not change anything, even if the playbook runs multiple times."
- P12 https://github.com/steveyegge/beads .devcontainer/README.md:1 and flake.nix (commit d274841) — git clone — Beads ships a devcontainer and a Nix flake in its own repo, showing both routes are used by agent tooling. Quote: "This devcontainer configuration provides a fully-configured development environment for beads with:"
- P13 /home/user/Autonomy-Research/research/findings/packaging.md:122-125 — local file read — Existing local finding: skills namespaced, hooks run twice if in both settings and plugin; cloud never installs plugins. Quote: "hooks have no prefix, so a hook that is in both your settings file and `hooks/hooks.json` runs twice each time its event fires."
- P14 /home/user/Autonomy-Research/research/findings/packaging.md:71-75 — local file read — Existing local finding: manifest `version` pins; omitting it tracks commits; auto-update off by default for third-party marketplaces. Quote: "Manifest `version` pins users to the cached copy until the string changes"
- P15 https://github.com/obra/superpowers README.md:52-81 (commit bb92a77) — git clone — Superpowers install paths are per-harness and it appears in two marketplaces. Quote: "/plugin install superpowers@superpowers-marketplace"
- P16 https://github.com/obra/superpowers .claude-plugin/plugin.json (commit bb92a77) — git clone — Superpowers manifest is a plain plugin with a version. Quote: "\"version\": \"7.0.0\","
- P17 /home/user/Autonomy-Research/scripts/cloud-setup.sh:8-18 — local file read — Repo's current cloud bootstrap installs Superpowers only when `CLAUDE_CODE_REMOTE` is true, unpinned. Quote: "claude plugin install superpowers@superpowers-marketplace >/dev/null 2>&1"
- P18 https://github.com/anthropics/claude-code plugins/ralph-wiggum/README.md:13,38 (commit 03b5892) — git clone — Ralph official plugin is a Stop hook that re-feeds the prompt, with `--max-iterations` and `--completion-promise`. Quote: "This plugin implements Ralph using a **Stop hook** that intercepts Claude's exit attempts:"
- P19 https://github.com/steveyegge/beads README.md:30-43,131 (commit d274841) — git clone — Beads is a CLI installed once system-wide, not a plugin; `bd setup claude` writes hooks and settings; embedded Dolt by default. Quote: "Beads is a CLI tool you install once and use everywhere. You don't need to clone this repository into your project."
- P20 https://github.com/steveyegge/beads README.md:99-121 (commit d274841) — git clone — Beads install notes: npm path suits cloud, and install scripts check checksums. Quote: "The install scripts verify release checksums before install."
- P21 https://github.com/steveyegge/beads README.md:31 (commit d274841) — git clone — Beads README now points its installer at the `gastownhall` org, while the repo URL stays `steveyegge/beads`. Quote: "curl -fsSL https://raw.githubusercontent.com/gastownhall/beads/main/scripts/install.sh | bash"
- P22 /home/user/Autonomy-Research/plugin/skills/setup/SKILL.md:13-17 — local file read — Plugin MCP servers are named with a plugin prefix, which the repo's setup skill already probes for both forms. Quote: "Installed as a plugin, the bundled servers' tools are named `mcp__plugin_research-agent_<server>__<tool>`"
- P23 /home/user/Autonomy-Research/research/findings/packaging.md:169-175 — local file read — Connectors need a claude.ai login; cloud connector traffic goes via Anthropic servers; repo `.mcp.json` servers run in the VM. Quote: "are automatically available in Claude Code\" when \"your active authentication method is a claude.ai subscription login"
- P24 /home/user/Autonomy-Research/research/findings/packaging.md:151-155 — local file read — Cloud sessions load `.mcp.json` without a prompt; local asks per-server approval. Quote: "it loads project-scoped servers without asking"
- P25 https://code.claude.com/docs/en/remote-control — WebFetch — Remote Control on a machine you control keeps MCP servers and tools available. Quote: "your filesystem, [MCP servers](/docs/en/mcp), tools, and project configuration all stay available"
- P26 https://code.claude.com/docs/en/devcontainer — WebFetch — Devcontainer doc: put MCP servers in project `.mcp.json`, install stdio binaries in the image, allowlist remote domains. Quote: "define them at project scope in a `.mcp.json` file at the repository root so they are checked in alongside your dev container configuration."
- P27 https://code.claude.com/docs/en/sandbox-environments — WebFetch — Bash sandbox does not cover MCP servers or hooks; they run on the host. Quote: "MCP servers, command hooks, and plugin monitors are separate processes that run unconstrained on the host."
- P28 /home/user/Autonomy-Research/CLAUDE.md (attached context, tools section) — local file read — Repo CLAUDE.md states the split. Quote: "Exa, Context7, Parallel Search and Mermaid Chart come from claude.ai connectors, not this repo."
- P29 https://code.claude.com/docs/en/devcontainer — WebFetch — Codespaces secrets arrive as environment variables, and long-lived tokens come from `claude setup-token`. Quote: "Codespaces exposes secrets as environment variables inside the container automatically."
- P30 https://code.claude.com/docs/en/devcontainer — WebFetch — Do not mount host secrets into the container. Quote: "Avoid mounting host secrets such as `~/.ssh` or cloud credential files into the container; prefer repository-scoped or short-lived tokens."
- P31 https://code.claude.com/docs/en/devcontainer — WebFetch — Cloud providers: pass credentials as env vars, not mounted files. Quote: "pass credentials into the container as environment variables through `containerEnv`, a Codespaces secret, or your cloud's workload identity"
- P32 https://containers.dev/implementors/json_reference/ — WebFetch (summarised by fetch model; not verbatim page) — Devcontainer spec has `${localEnv:VAR}` and warns unset variables are blank; it has no dedicated secrets property. Quote: "Unset variables are left blank."
- P33 https://code.claude.com/docs/en/devcontainer — WebFetch — A bypass-permissions session can exfiltrate anything in the container including `~/.claude` credentials. Quote: "dev containers do not prevent a malicious project from exfiltrating anything accessible inside the container, including the Claude Code credentials stored in"
- P34 https://code.claude.com/docs/en/devcontainer — WebFetch — Persisting login across rebuilds needs a volume at `~/.claude` plus `CLAUDE_CONFIG_DIR`. Quote: "so mounting a volume at `~/.claude` alone doesn't keep you signed in."
- P35 /home/user/Autonomy-Research/research/findings/packaging.md:164-168,299-303 — local file read — Cloud network secrets, `userConfig` sensitive, GitHub Actions secrets. Quote: "so \"the key itself stays outside the VM\""
- P36 https://code.claude.com/docs/en/self-hosted-environments — WebFetch — Self-hosted environments use an environment key shown once. Quote: "Shown once at environment creation, labeled **environment key** in the admin UI."
- P37 /home/user/Autonomy-Research/plugin/skills/setup/SKILL.md:8-9,51-55 — local file read — The repo's setup skill probes seven tools by name, reports missing ones with fallbacks, and installs nothing. Quote: "Do not edit settings, install anything, or add keys."
- P38 /home/user/Autonomy-Research/plugin/skills/setup/SKILL.md:13-15 — local file read — Deferred tools mean absence from a list is not proof; use ToolSearch. Quote: "a tool absent from your list is not yet proof it is missing."
- P39 /home/user/Autonomy-Research/research/findings/packaging.md:243,246 (DeepWiki-derived for ECC, flagged medium there) — local file read — Other plugins: ECC ships `doctor`/`repair`; research-superpowers uses a session-start notice as the install signal. Quote: "`node scripts/ecc.js doctor` / `repair`"
- P40 /home/user/Autonomy-Research/research/tool-registry.md:40-41 — local file read — `claude plugin validate --strict` and `claude plugin eval` give CI-time checks. Quote: "Checks manifest, frontmatter, `.mcp.json`"
- P41 https://code.claude.com/docs/en/self-hosted-environments — WebFetch — Self-hosted runner has a CI smoke test and a health endpoint for verifying a runner image. Quote: "a CI smoke test that verifies a runner image before you promote it"
- P42 https://github.com/steveyegge/beads README.md:110,121 (commit d274841) — git clone — Beads' installer verifies release checksums and `bd version` / `bd hooks install` are documented upgrade checks. Quote: "The install scripts verify release checksums before install."
- P43 https://code.claude.com/docs/en/sandbox-environments — WebFetch — Runtime-sandbox gotcha: a clean start is not proof config loaded. Quote: "Don't take a clean start as proof your settings loaded."

Always-on agent harnesses note (OR = https://github.com/openclaw/openclaw, commit ca009ba036a80172885b60feb7dcc4f0920744e3; NanoClaw = qwibitai/nanoclaw clone, commit 2105169d8f7f017cd1ba3222cbf9708273fa1a3b; Hermes = NousResearch/hermes-agent, commit 9c002cb941de1e1708294d0cd58e060b6a417b5e; all read 2026-10-16 via git clone + grep):
- H1 OR README.md:~20 (commit ca009ba) — git clone + grep — It is an open-source assistant on your own computer reached via many chat channels; Gateway runs it; models/harnesses are swappable plugins. Quote: "OpenClaw is an open-source AI assistant that runs on your own computer and meets you in the channels you already use: Discord, iMessage, Slack, Teams, Telegram, WhatsApp, and 20+ more"
- H2 OR README.md "Quick start" (commit ca009ba) — git clone — Install is a daemon via onboarding wizard (curl|bash installer, npm global, Docker, Nix). Quote: "openclaw onboard --install-daemon"
- H3 OR LICENSE:1-3, package.json:3 (commit ca009ba) — git clone — Licence MIT, held by "OpenClaw Foundation"; package version 2026.10.4; HEAD commit dated 2026-10-16 (calendar-versioned, daily releases). Quote: "Copyright (c) 2026 OpenClaw Foundation"
- H4 https://www.infosecurity-magazine.com/news/malicious-crypto-trading-skills/ — Parallel fetch — Name history and launch: Clawdbot -> Moltbot (Anthropic name request) -> OpenClaw end Jan 2026. Quote: "Launched in 2025 by Peter Steinberger as Clawdbot, the project first rebranded to Moltbot after Anthropic requested a name change and rebranded again to OpenClaw at the end of January 2026."
- H5 OR SECURITY.md:5 (commit ca009ba) — git clone — Threat model: single trusted operator per gateway, not multi-tenant. Quote: "OpenClaw is local-first agent infrastructure for trusted operators; it is not designed as a shared multi-tenant boundary between adversarial users on one gateway."
- H6 OR SECURITY.md:52-53 — git clone — SECURITY.md treats prompt injection alone and local shell as non-vulnerabilities. Quote: "Prompt injection without a policy, auth, approval, sandbox, or tool-boundary bypass."
- H7 https://www.ibm.com/think/x-force/what-openclaw-reveals-about-agentic-ai-security-risks — tool not stated in note — Advisory volume (IBM X-Force, dated 2026-10-13). Quote: "OpenClaw has already published over 255 GitHub Security Advisories."
- H8 https://www.ibm.com/think/x-force/what-openclaw-reveals-about-agentic-ai-security-risks — tool not stated in note — ClawHub supply-chain campaign "ClawHavoc". Quote: "Attackers uploaded over 1,100 malicious skills to ClawHub, many masquerading as productivity, crypto or coding tools."
- H9 https://www.infosecurity-magazine.com/news/malicious-crypto-trading-skills/ — Parallel fetch — Early count of malicious skills (Feb 2026). Quote: "McCarty found 386 malicious skills published on ClawHub, a skill repository for OpenClaw assistants."
- H10 NanoClaw README.md:36-38 (commit 2105169) — git clone — NanoClaw design motive and isolation vs OpenClaw. Quote: "Agents run in their own Linux containers with filesystem isolation, not merely behind permission checks."
- H11 NanoClaw README.md:77, 97 — git clone — NanoClaw bash safety and credential gateway. Quote: "agents never hold raw API keys. Outbound requests route through a credential gateway that injects credentials at request time"
- H12 NanoClaw LICENSE:1-3 — git clone — NanoClaw licence MIT, 2026. Quote: "MIT License"
- H13 Hermes README.md:25-29 (commit 9c002cb) — git clone — Hermes Agent: gateway on Telegram/Discord/Slack/WhatsApp/Signal, cron, seven terminal backends. Quote: "Seven terminal backends — local, Docker, SSH, Singularity, Modal, Daytona, and Vercel Sandbox."
- H14 Hermes README.md:27 — git clone — Hermes scheduler. Quote: "Built-in cron scheduler with delivery to any platform."
- H15 Hermes LICENSE:1-3 — git clone — Hermes licence MIT (2025 Nous Research), HEAD dated 2026-10-16. Quote: "Copyright (c) 2025 Nous Research"
- H16 https://code.claude.com/docs/en/channels — Parallel fetch — Claude Code itself now has first-party messaging: Channels (Telegram, Discord, iMessage; research preview). Quote: "Telegram, Discord, and iMessage are included in the research preview."
- H17 OR docs/gateway/cli-backends.md:9 (commit ca009ba) — git clone — CLI backend runs Claude Code as the runtime. Quote: "OpenClaw can run agent turns through a local AI CLI, such as Claude Code or Gemini CLI, instead of calling the provider API itself"
- H18 OR docs/gateway/cli-backends.md:11 — git clone — Tool access via MCP bridge. Quote: "A backend with `bundleMcp: true` receives Gateway tools through a loopback MCP bridge."
- H19 OR docs/gateway/cli-backends.md ~30 — git clone — Setup requires Claude Code installed on the gateway host. Quote: "The gateway service must have the CLI on its `PATH`."
- H20 OR docs/tools/acp-agents.md:69-78 — git clone — ACP path for Claude Code. Quote: "ACP Claude is a **harness session** with ACP controls, session resume, background-task tracking, and optional conversation/thread binding."
- H21 OR docs/tools/acp-agents.md:71-76 — git clone — ACP stack depth. Quote: "OpenClaw ACP session control plane. Official @openclaw/acpx runtime plugin. Claude ACP adapter. Claude-side runtime/session machinery."
- H22 OR docs/tools/acp-agents.md:25 — git clone — Reverse direction. Quote: "To let Codex or Claude Code connect as an external MCP client directly to existing OpenClaw channel conversations, use openclaw mcp serve instead of ACP."
- H23 https://code.claude.com/docs/en/remote-control — tool not stated in note (WebFetch in the cloud-sessions note) — Remote Control: local session, outbound-only, transcript stored at Anthropic. Quote: "Your local Claude Code session makes outbound HTTPS requests only and never opens inbound ports on your machine."
- H24 https://code.claude.com/docs/en/remote-control — tool not stated in note (WebFetch in the cloud-sessions note) — Remote Control not usable with setup-token or custom base URL. Quote: "These tokens can only make model requests, so they can't establish Remote Control sessions."
- H25 https://code.claude.com/docs/en/agent-sdk/overview — tool not stated in note — Agent SDK embeds Claude Code (tools, hooks, subagents, MCP, permissions, sessions) in your own process. Quote: "A library that runs the Claude Code binary, with Claude Code's capabilities, such as built-in tools, permissions, sessions, and hooks."
- H26 https://code.claude.com/docs/en/agent-sdk/overview — tool not stated in note — Agent SDK doc note. Quote: "Unless previously approved, Anthropic does not allow third party developers to offer claude.ai login or rate limits for their products, including agents built on the Claude Agent SDK."
- H27 OR docs/providers/anthropic.md:281-288 (commit ca009ba) — git clone — OpenClaw's own current statement on subscription use (Oct 2026). Quote: "Anthropic's June 15, 2026 support update paused the previously announced separate Agent SDK credit plan."
- H28 OR docs/providers/anthropic.md:281-288 (commit ca009ba) — git clone — Same section. Quote: "Subscription-plan Claude Agent SDK, `claude -p`, and third-party app usage still draw from the signed-in subscription's usage limits."
- H29 OR docs/gateway/sandboxing.md:9 (commit ca009ba) — git clone — Sandboxing off by default; gateway stays on host. Quote: "Sandboxing is off by default and controlled by `agents.defaults.sandbox`"
- H30 OR docs/gateway/sandboxing.md:12 — git clone — Self-assessment. Quote: "This is not a perfect security boundary, but it materially limits filesystem and process access when the model does something dumb."
- H31 OR docs/gateway/sandboxing/modes-scope-and-backend.md:15-17 — git clone — Backends and default. Quote: "`off`, `non-main`, `all`"
- H32 OR docs/gateway/security/secrets-and-storage.md:17 — git clone — Dedicated machine/VM/user advice. Quote: "Run it on a dedicated machine/VM/container, use a dedicated OS user + dedicated browser/profile/accounts, and do not sign that runtime into personal Apple/Google accounts"
- H33 OR docs/gateway/security/index.md:7 — git clone — Defaults: loopback bind, pairing for unknown DMs; container images default exposed. Quote: "container images default to an exposed bind"
- H34 OR docs/gateway/security/hardened-baseline.md:~20 — git clone — Hardened baseline denies exec/fs/runtime tools. Quote: "exec: { security: \"deny\", ask: \"always\" }"
- H35 https://code.claude.com/docs/en/channels — Parallel fetch — Claude Code permission modes still apply: some actions never auto-approve. Quote: "the actions no mode auto-approves still apply."
- H36 https://code.claude.com/docs/en/channels "How channels compare" (remote-control page table) — Parallel fetch — Claude Code first-party surfaces compared. Quote: "Push events from a chat app like Telegram or Discord, or your own server"
- H37 https://code.claude.com/docs/en/channels — Parallel fetch — Channels are research preview with allowlisted plugins only. Quote: "During the preview, `--channels` only accepts plugins from an Anthropic-maintained allowlist"
- H38 https://code.claude.com/docs/en/channels — Parallel fetch — Channels need Anthropic auth, not Bedrock/Vertex/Foundry. Quote: "are not available on Amazon Bedrock, Google Cloud's Agent Platform, or Microsoft Foundry."
- H39 https://code.claude.com/docs/en/scheduled-tasks — tool not stated in note (WebFetch in the cloud-sessions note) — Scheduled durable options. Quote: "For scheduling that survives independently of any session, use Routines to create a routine on the cloud, set up a Desktop scheduled task, or use GitHub Actions."
- H40 Hermes README.md:27 — git clone — Hermes adds learning loop/memory and cron. Quote: "A closed learning loop"
- H41 NanoClaw README.md:36 (comparison claim by a competitor) — git clone — OpenClaw scale, risk: nearly half a million lines. Quote: "OpenClaw has nearly half a million lines of code, 53 config files, and 70+ dependencies."

## Implications for the autonomous engineer and the researcher plugin

Design consequences, each tied to the evidence above; items marked *inference* come from the workers' marked
inferences.

1. **Two surfaces, one repo.** The template-plus-plugin repo from packaging.md stays the unit of distribution.
   Cloud sessions load only what is committed in `.claude/` and `.mcp.json` (C12, C13, C14), so the engineer's
   skills, agents, rules and hooks live in the repo; Superpowers is installed by the bootstrap, not by
   `enabledPlugins` (C13, P17). *Inference:* pin the Superpowers manifest version in the bootstrap (P16, P14)
   and record commits in `docs/versions.md`.
2. **Bootstrap, not Dockerfile, for John's route.** A VM needs no Docker (P1); exact Claude Code pinning is a
   fixed `npm install -g @anthropic-ai/claude-code@X.Y.Z` (P5). *Inference:* `scripts/bootstrap.sh` pins
   Claude Code, Node, Playwright browsers, Superpowers, optional `bd` (`--with-beads`); `.devcontainer/` is an
   optional second route for Codespaces (P6, P29).
3. **Auth on the VM is `/login`, not `setup-token`.** A setup-token loses Remote Control and connectors (S13,
   H24) and turns Chrome integration off (C40); an API key in the environment silently takes over `-p` runs
   (S15). *Inference:* the doctor script must check that no `ANTHROPIC_API_KEY` is set unless overflow is
   intended, and a watchdog restarts the process on 401 or stall (S34, S35, S36).
4. **Permissions on the VM.** Skip-permissions only inside the VM boundary as a non-root user (S7, S8, P3,
   S28); deny rules still apply under bypass (S9) and should cover `~/.ssh`, credential files and protected
   branches (*inference*; S17, P33, S43). Prefer `auto` mode or an allowlist for browser work (*inference*;
   S10, S42).
5. **Approvals are two-tier.** Live approvals via Channels (Telegram allowlist, permission relay: C54, C55,
   C57) and Remote Control push (C51, C52, C53) on the VM; batched approvals from Routines as `claude/`
   branches and a Slack digest (C29, C49), reviewed in the morning (*inference*). Document that anyone on the
   channel allowlist can approve tool use (C57).
6. **Browser logins live in a dedicated profile on the VM.** A real Chromium profile with persistent cookies
   (S30) in a dedicated OS user with no personal Apple/Google accounts (H32); Claude in Chrome is a
   headed-machine fallback only (C39, C41). Playwright MCP stays in `.mcp.json` with binaries installed by the
   bootstrap (*inference*; P26).
7. **Secrets.** Repo holds names only (`.env.example`); values in a 0600 env file on the VM, Codespaces secrets
   in a container, network secrets in the cloud (P29, P31, P35, C11). Never mount host secrets into a container
   (P30).
8. **Health checks.** `scripts/doctor.sh` (deterministic) plus `/setup` (tool-name probes, installs nothing:
   P37, P38), with `claude plugin validate --strict` in CI (P40); "Don't take a clean start as proof your
   settings loaded" (P43). *Inference:* in unattended mode, run the probe at SessionStart and fail closed.
9. **Cost guardrails.** Fresh session per task rather than one all-night context (S37, S38, S39); cap
   parallelism (C61); `--max-turns` and `--max-budget-usd` per run (C37, S5); expect routine runs to be rejected
   at the limit without usage credits (C62, C64).
10. **No harness as host.** OpenClaw and Hermes are rejected as hosts (Q6); the engineer's chat and remote
    surfaces are Claude Code's own (C54, C43, H39). Keep a slot in the design for an Agent SDK daemon (H25)
    and, only if Slack/WhatsApp is required, a NanoClaw spike (H10, H11).
11. **For this research plugin.** The run confirms that `scripts/cloud-setup.sh` should pin Superpowers (P17,
    P16) and that the `/setup` skill's tool-name probe is the right shape for a VM too (P22, P37). Add the
    spike list to `research/open-questions.md` ownership and write the EARS requirements for the runtime in
    `research/requirements/autonomous-engineer.md`.

## Tools evaluated

| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Claude Code cloud sessions | https://code.claude.com/docs/en/claude-code-on-the-web | Anthropic-hosted VM sessions, no VM charge, plan usage | cloud | 2026-10-16 | Use as the unattended repo worker; no browser logins |
| Routines | https://code.claude.com/docs/en/routines | Schedule (>=1 h), API `/fire`, GitHub triggers; no approval prompts; research preview | cloud | 2026-10-16 | Use for overnight GitHub-only runs; spike duration |
| Cloud environments (setup script, network secrets) | https://code.claude.com/docs/en/cloud-environments | Network levels, env vars, secrets via proxy, cached setup | cloud | 2026-10-16 | Use; Full network for installs, secrets for keys |
| Remote Control | https://code.claude.com/docs/en/remote-control | Drive local sessions from phone/web; push notifications; server mode; outbound-only; subscription login only | John's machine/VM | 2026-10-16 | Use for browser logins, monitoring and live approvals; gives up after about 10 min offline; API keys and setup-token unsupported |
| Claude in Chrome | https://code.claude.com/docs/en/chrome | Uses logged-in Chrome; visible window; local only; off under API-key/setup-token auth | John's machine | 2026-10-16 | Fallback; not unattended-safe per docs |
| Channels (Telegram/Discord/iMessage) | https://code.claude.com/docs/en/channels | Push events and permission relay into a running local session; sender allowlist; research preview | John's machine/VM | 2026-10-16 | Use for live approvals; needs always-on local process |
| /loop and scheduled tasks | https://code.claude.com/docs/en/scheduled-tasks | In-session cron, 7-day expiry; Desktop tasks run on your machine | local session | 2026-10-16 | Skip /loop for overnight; Desktop tasks are an alternative on a spare machine |
| Claude Code GitHub Actions | https://code.claude.com/docs/en/github-actions | Action with cron, uses subscription via OAuth token | GitHub runners | 2026-10-16 | Alternative to routines for CI-bound jobs |
| claude -p / Agent SDK CLI | https://code.claude.com/docs/en/headless | Official non-interactive Claude Code | VPS/VM/own machine | 2026-10-16 | Use: core of unattended runs; add `--bare` only with API key |
| claude setup-token | https://code.claude.com/docs/en/authentication | One-year OAuth token from a Max plan for headless auth | any server | 2026-10-16 | Avoid as the VM's primary auth (breaks Remote Control, connectors, Chrome); fine for CI |
| Claude Agent SDK | https://code.claude.com/docs/en/agent-sdk/overview | Embed Claude Code loop, hooks, MCP in own daemon | local/VM | 2026-10-16 | Use for a custom always-on service if needed; third-party login rules apply |
| browser-use/bux | https://github.com/browser-use/bux | Claude Code on a $5 Ubuntu VPS with persistent real Chromium, Telegram, hand-off on login walls (setup prompt tells agents to run installer) | VPS | 2026-10-16 | Reference pattern only; not installed, not cloned; page contains instructions addressed to agents, not followed. Spike before trust |
| thereisno-tomorrow/claude-vps | https://github.com/thereisno-tomorrow/claude-vps | Hetzner + Tailscale + tmux bootstrap scripts | Hetzner VPS | not opened (search excerpt only) | Reference only; not verified |
| amineorion/claude-mini-setup | https://github.com/amineorion/claude-mini-setup | Spare Mac, tmux, Tailscale, ntfy hooks | Mac mini | not opened (search excerpt only) | Reference only; not verified |
| nurkert/claude-systemd | https://github.com/nurkert/claude-systemd | systemd service for Claude Code with Remote Control | Linux | not opened (search excerpt only) | Reference only; not verified |
| 1Password for Claude | https://1password.com/blog/1password-for-claude | Vault fill without exposing secrets to the model | Mac desktop | 2026-10-16 | Paid; Mac-only; defer; favours a spare Mac if wanted |
| Dev Container + Claude Code Feature | https://github.com/anthropics/devcontainer-features/tree/main/src/claude-code | 4-line devcontainer.json installs Claude Code; needs Docker or Codespaces (facts from https://code.claude.com/docs/en/devcontainer) | local Docker / Codespaces | 2026-10-16 | Second route; hides Docker only inside Codespaces |
| Anthropic reference devcontainer | https://github.com/anthropics/claude-code/tree/main/.devcontainer | Dockerfile + iptables firewall + volumes, example only (facts from https://code.claude.com/docs/en/devcontainer) | Docker | 2026-10-16 | Copy as a starting point; not a maintained base |
| Self-hosted environments | https://code.claude.com/docs/en/self-hosted-environments | Run cloud sessions on own runners | own infra, Team/Enterprise beta | 2026-10-16 | Skip for one Max user |
| sandbox-runtime | https://github.com/anthropics/sandbox-runtime | Wraps whole Claude process in bubblewrap/Seatbelt, no Docker (facts from https://code.claude.com/docs/en/sandbox-environments) | Linux/macOS | 2026-10-16 | Option for isolation without Docker; beta |
| Beads (bd) | https://github.com/steveyegge/beads | CLI + Dolt tracker; `bd setup claude`; checksum-verified installer now under gastownhall org | CLI install | 2026-10-16 | Phase 2; install by bootstrap flag only |
| Ralph Loop plugin | https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum | Stop-hook loop, `--max-iterations`, `--completion-promise` | plugin | 2026-10-16 | Phase 2 with iteration cap |
| Superpowers | https://github.com/obra/superpowers | Methodology skills plugin, manifest version 7.0.0 at commit bb92a77 | plugin via bootstrap | 2026-10-16 | In use; pin the version in the bootstrap |
| Nix flake / Home Manager | https://devopsboys.com/blog/nix-reproducible-devops-environments-guide-2026 | Declarative env | any | not opened (search excerpt only) | Reject for v1 (worker inference; not researched from an opened page) |
| Ansible | https://docs.ansible.com/ansible/latest/getting_started/introduction.html | Idempotent agentless playbooks | SSH to VM | 2026-10-16 | Later, if multiple hosts |
| cloud-init | https://docs.cloud-init.io/en/latest | First-boot VPS config | VPS | not opened (search excerpt only) | Optional wrapper that calls bootstrap.sh; unverified |
| Packer | (no page opened) | Machine images | - | not opened | Reject; not researched beyond name |
| OpenClaw | https://github.com/openclaw/openclaw | MIT Node gateway daemon, 20+ chat channels, drives Claude Code via claude-cli backend or ACP; install via curl script/npm/Docker; sandbox off by default; 255+ advisories | local/VM/VPS | 2026-10-16 | Reject as host; fallback only if channel breadth is needed, in a dedicated VM, sandbox `all`, no ClawHub skills |
| NanoClaw | https://github.com/nanocoai/nanoclaw | Small TS assistant, Docker container per agent, credential gateway; install via nanoclaw.sh | local/VM, Docker | 2026-10-16 (clone of qwibitai/nanoclaw) | Spike first if a Slack/WhatsApp daemon is needed; Agent SDK claim unverified |
| Hermes Agent | https://github.com/NousResearch/hermes-agent | MIT Python agent with memory, cron, gateway, 7 execution backends; model-agnostic | local/VPS/serverless | 2026-10-16 | Skip as Claude Code host; not Claude-centric |

## Open questions

Claims excluded for lack of an opened source (search excerpts only), kept here rather than in findings:
1. The Register (2026-04-06) report that Anthropic cut OpenClaw and other third-party harnesses off from
   subscription limits on 2026-04-04 (https://www.theregister.com/software/2026/04/06/anthropic-closes-door-on-subscription-use-of-openclaw/5222854): not opened.
2. openclawlaunch.com claim of a May 2026 reversal with Agent SDK credits: not opened.
3. wmedia.es claim that the June 15 Agent SDK change was cancelled the same day: not opened.
4. thereisno-tomorrow/claude-vps (Hetzner, Tailscale-only firewall, tmux): repo not cloned.
5. amineorion/claude-mini-setup (spare Mac, pmset, ntfy): not opened.
6. nurkert/claude-systemd (systemd unit with Remote Control): not opened.
7. developersdigest spare-Mac guide: not opened.
8. Tailscale plus SSH as the remote-access pattern: seen only in third-party excerpts; the opened guides'
   quotes do not mention it.
9. Playwright MCP profile persistence (`--user-data-dir`, `--storage-state`): https://github.com/microsoft/playwright-mcp not fetched.
10. GitHub issue #38813 (silent OAuth expiry in cron/LaunchAgent) and #41506 (token-use jump on Max): not fetched.
11. "$1,800+ in 2 days via claude -p" runaway-cost anecdote: unverified excerpt.
12. Max 5x/20x prices ($100/$200) at support.claude.com/en/articles/11049741: not opened; the opened Pro/Max
    article lists no prices.
13. Per-tier Max token quotas (third-party blog, 2026-10-08): snippet only.
14. A separate "Fable" weekly limit on Max: snippet only.
15. Nix guide (devopsboys) and cloud-init run-once behaviour: snippets only.
16. Ralph origin claims (bash loop, fresh context; ghuntley.com/ralph "isn't it" remark about the plugin): not opened.
17. OpenClaw authentication.md line calling an API key "the most predictable option" and Claude CLI reuse
    "sanctioned": grep output seen but no quote carried; not cited.
18. NanoClaw "runs Claude Code natively via the Claude Agent SDK" (nanoclaw.dev): no quoted line in the clone
    supports it; the tools row carries it as unverified.
19. PointGuard report of 1,000+ exposed OpenClaw instances (Jan 2026): snippet only.
20. CVE-2026-25253 (one-click RCE), ClawJacked, CVE-2026-32302: snippets only.
21. Palo Alto (persistent-memory delayed injection) and Bitdefender (do not run on a company device): snippets.
22. remoteopenclaw.com claim that Claude Code has no messaging integrations: not opened; contradicted by the
    opened Channels page.
23. Worker-inferred values not in any quote: 30 extra background minutes for cloud commands; 32 concurrent
    Remote Control server-mode sessions; auto mode as default from v2.1.283; "wait and continue" from
    v2.1.234; virtua.cloud's 10-20 EUR/month for 4 vCPU/8 GB; OpenClaw package version 2026.10.4.
24. Pages the harness note lists as opened without naming the tool (IBM X-Force, Agent SDK overview): the
    verifier should confirm the quotes.

Unsettled by the evidence:
25. Maximum wall-clock length of an active cloud session or Routine run, and a Routine's per-run token budget:
    not stated on any opened page. Spike.
26. Whether headless Chromium/Playwright installs and runs in the cloud VM under Full network: undocumented.
27. How the Oct 7, 2026 "monthly API credits" for Max interact with `claude -p` and the shared 5-hour/weekly
    windows (see Q2 contradiction 1).
28. Whether a harness that spawns the unmodified `claude` binary (OpenClaw `claude-cli` backend) is within
    the "end user ... unmodified Claude Code binary" allowance (see Q2 contradiction 2); the consumer Terms
    and AUP texts themselves were not opened.
29. Whether Claude Code's own permission prompts surface through OpenClaw chat in the `claude-cli` backend.
30. Whether Claude in Chrome tolerates an unattended, logged-in headed Chrome (visible window, idle service
    worker).
31. Whether Desktop scheduled tasks can drive Chrome: desktop-scheduled-tasks page not opened.
32. Connector visibility under `CLAUDE_CODE_OAUTH_TOKEN` auth; per-conversation connector toggle in cloud
    sessions (packaging.md open question 6).
33. Notification hook behaviour in cloud sessions; Slack integration page (https://code.claude.com/docs/en/slack)
    not opened; no official SMS or email approval mechanism found.
34. Hook collision count when Superpowers, Beads, Ralph and this repo's SessionStart hook are all installed.
35. Marketplace-level pinning of a third-party plugin to a tag or SHA; how Superpowers updates interact with a
    pinned manifest.
36. Codespaces `~/.claude` persistence with the `CLAUDE_CONFIG_DIR` mount.
37. Cloudflare Access, Bitwarden/`op` CLI on headless Linux, Ansible Vault, SOPS, agenix/sops-nix: no source
    opened.
38. Measured overnight cost of a VPS run on Max; Fly.io, Lightsail, DigitalOcean, Xvfb/VNC specifics: no
    source opened.
39. NanoClaw and Hermes star counts, advisory history and maintenance depth: not searched; other harnesses
    (NemoClaw, AutoGPT-style) seen only as names.
40. GitHub-trigger hourly caps for Routines: docs point to "Add a GitHub trigger" without numbers.
