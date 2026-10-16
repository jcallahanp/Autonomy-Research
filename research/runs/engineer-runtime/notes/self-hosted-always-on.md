# Self-hosted always-on Claude Code (VPS, VM, own machine)

Brief: How do people run Claude Code unattended on a machine they control (VPS, VM, home computer), and what does it take to do it reliably and within Anthropic's terms?
Run: research/runs/engineer-runtime/PLAN.md

## Official unattended modes
### Takeaway
Anthropic documents `claude -p` (the Agent SDK via CLI), permission modes (`acceptEdits`, `dontAsk`, `auto`, `bypassPermissions`), `--permission-prompts none`, `--max-budget-usd`, SIGTERM handling and a session-resume flow. Its stated condition for fully unattended skip-permissions is a container, VM or sandbox, run as non-root. Confidence: high (all from code.claude.com, opened 2026-10-16).

### Cited findings
- `claude -p` is the non-interactive entry point and is the Agent SDK as a CLI — https://code.claude.com/docs/en/headless, opened 2026-10-16, WebFetch — Quote: "To run Claude Code in non-interactive mode, pass `-p` with your prompt and the CLI options you need"
- `--bare` is recommended for scripts but never reads OAuth or keychain, so it needs an API key — https://code.claude.com/docs/en/headless, opened 2026-10-16, WebFetch — Quote: "In bare mode, Claude Code never reads OAuth credentials or the system keychain."
- Without `--bare`, a `-p` session runs project hooks and MCP servers with no trust prompt (matters if the VM clones untrusted repos) — same page — Quote: "A `-p` session shows no workspace trust dialog and no per-server approval prompt."
- Unattended-specific flag: deny anything that would prompt — same page — Quote: "Pass `--permission-prompts none` when nobody is available to answer permission prompts, for example in a scheduled job."
- Exit codes and cost visibility for scripts — same page — Quote: "the response payload includes `total_cost_usd` and a per-model cost breakdown"; also "Both figures are client-side estimates and can differ from your actual bill."
- A `-p` run stays open for background work but kills idle waits after 10 minutes by default — same page — Quote: "stops whatever is still running after 10 minutes of continuous idle waiting by default and drops its partial result."
- Fully unattended recipe and its required isolation — https://code.claude.com/docs/en/permission-modes (saved fetch, table row), opened 2026-10-16, WebFetch — Quote: "Run fully unattended inside a container | `claude -p "<prompt>" --dangerously-skip-permissions` | Required: a container, VM, or the sandbox runtime"
- bypassPermissions warning — same page — Quote: "Only use this mode in isolated environments like containers, VMs, or dev containers without internet access, where Claude Code cannot damage your host system."
- Deny rules still hold under bypass — same page — Quote: "Deny rules block in every mode, including `bypassPermissions`."
- Auto mode (classifier) is the middle option and is now the default start mode in interactive sessions (v2.1.283+) — https://code.claude.com/docs/en/security, opened 2026-10-16, WebFetch — Quote: "A separate classifier model reviews actions instead of you and blocks the ones it judges unsafe."
- Anthropic's security page advises VMs for external web work and the dev container / sandbox runtime for whole-process isolation — same page — Quote: "Use virtual machines (VMs) to run scripts and make tool calls, especially when interacting with external web services"
- Remote Control: runs on your machine, phone/web steer it, needs subscription auth, server mode gives up after about 10 minutes of network refusal — https://code.claude.com/docs/en/remote-control, opened 2026-10-16, WebFetch — Quote: "API keys are not supported." and "Server mode: Claude Code gives up after roughly 10 minutes and the `claude remote-control` process exits."

### Contradictions
- None found.

### Inferences
- (mine) For John, a non-root Linux user on a dedicated VM with `claude -p` in a loop plus deny rules and `--max-budget-usd`/`--max-turns` is the documented path; `auto` mode with a sandbox is a lower-risk alternative to `bypassPermissions`. Rests on headless and permission-modes pages.
- (mine) "Without internet access" in the bypass warning conflicts with browser work with logins; the real mitigation is a disposable VM plus scoped credentials, not network isolation. Rests on the warning quote and the brief.

### Gaps
- Exact hook-based Stop/loop patterns for overnight runs (Ralph-style) not covered here; another facet.
- Sandbox runtime page (https://code.claude.com/docs/en/sandbox-environments) not opened.

## Authentication on a server (Max plan vs API key)
### Takeaway
Max can be used on a server you own: Anthropic documents `claude setup-token` to mint a one-year OAuth token for `CLAUDE_CODE_OAUTH_TOKEN` "for CI pipelines, scripts". Anthropic's line is that developers building products for others must use API keys, and third-party harnesses (OpenClaw) were cut off from subscription limits on 2026-04-04. Your own use of unmodified Claude Code on your own box is not barred by anything I found, but "ordinary, individual usage" is the stated assumption and the rules have changed repeatedly in 2026. Confidence: medium (policy text is clear; enforcement and future limits are not).

### Cited findings
- Long-lived token for headless use, from a Max plan — https://code.claude.com/docs/en/authentication, opened 2026-10-16, WebFetch — Quote: "generate a one-year OAuth token with `claude setup-token`"
- That token's limits — same page — Quote: "It can only make model requests, so it can't establish Remote Control sessions or fetch claude.ai connectors."
- `--bare` ignores the token — same page — Quote: "Bare mode does not read `CLAUDE_CODE_OAUTH_TOKEN`."
- An API key in the environment silently overrides the subscription (cost trap) — https://code.claude.com/docs/en/authentication — Quote: "In non-interactive mode (`-p`), the key is always used when present."
- Subscription login on a headless box is an accepted case — same page — Quote: "This happens when the browser can't reach Claude Code's local callback server, which is common in WSL2, SSH sessions, and containers."
- Credentials live in a plain file on Linux — same page — Quote: "On Linux, credentials are stored in `~/.claude/.credentials.json` with file mode `0600`."
- Terms: who may use OAuth, and the developer rule — https://code.claude.com/docs/en/legal-and-compliance, opened 2026-10-16, WebFetch — Quote: "Advertised usage limits for Pro and Max plans assume ordinary, individual usage of Claude Code and the Agent SDK."
- Same page, restriction on third parties — Quote: "Anthropic does not permit third-party developers to offer Claude.ai login into their own applications, or to route requests through Free, Pro, or Max plan credentials on behalf of their users."
- Same page, own use of the unmodified binary is allowed — Quote: "Nor does it prevent an end user from signing in to the unmodified Claude Code binary with their own Claude subscription"
- Same page, enforcement — Quote: "Anthropic reserves the right to take measures to enforce these restrictions and may do so without prior notice."
- Third-party harness ban: OpenClaw et al. moved off subscription limits on 2026-04-04 — https://www.theregister.com/software/2026/04/06/anthropic-closes-door-on-subscription-use-of-openclaw/5222854, opened 2026-10-16 (search excerpt only; page not fetched, see Gaps).
- Usage limits are shared and windowed — https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan, opened 2026-10-16, WebFetch — Quote: "Both Pro and Max plans have a five-hour session limit and a weekly limit."
- Same article: Claude chat and Claude Code share one allowance — Quote: "all activity in both tools counts against the same limits"
- Agent SDK / `claude -p` billing status, latest update — https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan, opened 2026-10-16, WebFetch — Quote: "We've paused the previously-announced changes to Claude Agent SDK usage." (June 15, 2026 update) and "Claude Max and Team plans now include monthly API credits, which cover the Claude Agent SDK" (Oct 7, 2026 update).

### Contradictions
- Search excerpt of the same support URL says "Starting June 15, 2026, Claude Agent SDK and claude -p usage no longer counts toward your Claude plan's usage limits" (a pre-June-15 version); the opened current page says the change is "paused" and "Subscription limits still apply". The opened current page (Oct 2026) is the later one. Also wmedia.es (https://wmedia.es/en/tips/claude-code-agent-sdk-credit, search excerpt) says it was cancelled the same day. Treat `claude -p` billing as unstable; re-check before building.

### Inferences
- (mine) For overnight `claude -p` on Max, usage draws on the same 5-hour and weekly windows as John's daytime work, so a long overnight run can exhaust the week; plan a budget and a stop on limit. Rests on the help-center quotes.
- (mine) Anthropic's text permits John (single user, own unmodified Claude Code, own machine) to use his subscription; the risk is policy drift (April harness ban, June credit episode, Oct 7 API-credit change), not current prohibition. Do not put John's token into any third-party harness (OpenClaw etc.).
- (mine) Fallback if limits bite: API key with `--max-budget-usd`, at API rates, only for the overflow.

### Gaps
- The Consumer Terms of Service and AUP text themselves were not opened; I relied on the Claude Code legal page that summarises them.
- Numeric Max 5x/20x weekly caps: not in the opened article.
- The Register and Verge articles on the OpenClaw ban were seen only as search excerpts, not opened; not used as cited findings.

## VPS setups reported 2025-2026
### Takeaway
The converging pattern is: small Ubuntu VPS (about 5-20 EUR/month), non-root user, Tailscale-only firewall, Claude Code inside tmux (or a systemd service), subscription login via browser-URL or `setup-token`. A home Mac mini variant adds launchd, `pmset` no-sleep and ntfy hooks. Failure modes reported: OOM kills of tmux, silent 401s, sleeping hosts. Confidence: medium (blogs and small repos; most with 0 stars, no independent validation).

### Cited findings
- VPS sizing and cost for a Max/Pro-login setup — https://www.virtua.cloud/learn/en/tutorials/run-claude-code-vps (2026-03-19), opened 2026-10-16, WebFetch — Quote: "Claude Code runs on your existing Claude subscription with no additional fee." (guide estimates roughly 10-20 EUR/month for 4 vCPU/8 GB; 4 GB handles a medium codebase)
- Same guide, subscription login on headless server — Quote: "generate an OAuth token on a machine with a browser, then transfer it to the VPS."
- tmux guide: failure modes — https://www.ssdnodes.com/learn/claude-code-on-a-vps-with-tmux (2026-07-14), opened 2026-10-16, WebFetch — Quote: "The OOM killer may also pick the tmux server rather than the build, taking your session with it."
- Same guide: non-root advice — Quote: "That one decision removes most of the ways a stray shell command can wreck the host."
- Hetzner repo: Ubuntu 24.04 CX22, Tailscale-only firewall, tmux — https://github.com/thereisno-tomorrow/claude-vps (search excerpt; repo not cloned; see Gaps). Not cited.
- Browser Use "bux": a $5 Ubuntu VPS, Claude logged in, real Chromium with persistent cookies — https://github.com/browser-use/bux, opened 2026-10-16, WebFetch — Quote: "Ubuntu 22.04+ with ≥2GB RAM. A $5/mo VPS is fine."
- Same repo, handling logins/2FA — Quote: "A real Chromium session via browser-harness — cookies persist, logins stick"
- Spare Mac guide: keep awake with pmset, Remote Control, Claude in Chrome, Screen Sharing — https://www.developersdigest.tech/blog/spare-mac-claude-code-control-guide (search excerpt only; not opened). Not cited.

### Contradictions
- None found.

### Inferences
- (mine) A $5 box is enough for the CLI but a headed/headless Chromium plus builds argues for 4 GB+ RAM and swap; ssdnodes says size for the toolchain not the CLI.
- (mine) John is not deep on Docker; every guide above works without Docker (VM/VPS plus non-root user is the isolation unit).

### Gaps
- No opened source for Fly.io, Lightsail or DigitalOcean specifics, or for Xvfb/VNC on Claude Code VPSes. bux page does not mention Xvfb or VNC.
- No opened source with measured overnight cost on a VPS.
- Hetzner and nurkert/claude-systemd repos seen only in search excerpts; not cloned.

## Logins, secrets, remote access
### Takeaway
Browser logins persist through a persistent Playwright profile (`--user-data-dir`) or `--storage-state`; Claude in Chrome needs a real `/login` session and is off with `setup-token`/API-key auth. Remote reach is Tailscale plus SSH, per the guides. A secrets vault with agent-safe fill exists (1Password for Claude) but is Mac/desktop-bound. Confidence: medium.

### Cited findings
- Playwright MCP persistence options — https://github.com/microsoft/playwright-mcp, opened 2026-10-16 (search excerpt only; not fetched). Not cited; see Gaps.
- Claude in Chrome cannot use token auth, so it does not fit a headless VPS logged in via `setup-token` — https://code.claude.com/docs/en/chrome.md (search excerpt only). Not cited; see Gaps.
- 1Password for Claude: the model never sees secrets; Mac only — https://1password.com/blog/1password-for-claude, opened 2026-10-16, WebFetch — Quote: "Claude never sees the vault item, password, or one-time code."
- Same page, availability — Quote: "1Password for Claude is available now for Mac, across business, family, and individual plans."
- Claude Code credential file is plaintext at mode 0600 on Linux — https://code.claude.com/docs/en/authentication — Quote: "On Linux, credentials are stored in `~/.claude/.credentials.json` with file mode `0600`."
- Security page: prompts from a `-p` run load project hooks/MCP with no trust dialog — https://code.claude.com/docs/en/headless — Quote: "A `-p` session shows no workspace trust dialog and no per-server approval prompt."
- bux hands the human a live view on login walls — https://github.com/browser-use/bux — Quote: "no credential-stuffing, no brittle workarounds"

### Contradictions
- None found.

### Inferences
- (mine) Safest login model for John: log in once by hand into a dedicated persistent browser profile on the VM (using a throwaway or limited-scope account where possible) and never put passwords in the model context; use human hand-off for 2FA. Rests on the bux quote and the 1Password quote (what good looks like).
- (mine) The Mac-only 1Password route would favour a home Mac mini over a Linux VPS if John wants vault-mediated fills.

### Gaps
- Cloudflare Access: no source opened.
- Bitwarden/`op` CLI on a headless Linux box: no source opened.
- Tailscale docs not opened; Tailscale claims come only from search excerpts of third-party guides (not cited).
- Playwright MCP docs and Chrome integration docs seen only in search excerpts.

## Documented pitfalls
### Takeaway
Documented: silent OAuth 401s on unattended runs (several Anthropic GitHub issues), a session-bound 401 that "latches" until process restart, shared Max limits being drained, long-context cost growth, and prompt injection with browsers. Mitigations: watchdog restart, budget flags, non-root VM, deny rules. Confidence: medium (issues are user reports, not Anthropic confirmation).

### Cited findings
- Static Max token can 401 permanently on one instance until restart — https://dev.to/drickon/the-token-is-valid-but-your-headless-claude-code-agent-just-401d-forever-48ip (2026-06-28), opened 2026-10-16, WebFetch — Quote: "once it 401s the instance hard-latches and never self-recovers until you restart the process."
- Same report: workaround is a watchdog — Quote: "A restart is the only thing that clears the latch."
- Silent expiry in cron/LaunchAgent, issue filed 2026-03-25 — https://github.com/anthropics/claude-code/issues/38813 (search excerpt; page not fetched). Not cited; Anthropic docs confirm the symptom: unattended sessions stall on expiry — https://code.claude.com/docs/en/authentication — Quote: "A background session in agent view or a Remote Control session that outlives the login stops making progress once the credential expires"
- Long sessions get expensive — https://code.claude.com/docs/en/costs, opened 2026-10-16, WebFetch — Quote: "a one-line question in a session that has been open all day still draws usage for the whole conversation."
- Compaction cost — same page — Quote: "`/compact` reads the conversation it summarizes, so compacting a large context is itself a large request."
- Idle cost: scheduled tasks and goals keep spending — same page — Quote: "a scheduled task fires on its interval even while the session is idle, sending your full context each time"
- Cache lifetime shifts when on credits — same page — Quote: "The lifetime is an hour on a subscription and drops to five minutes once you're drawing on usage credits"
- Hitting a limit mid-run — help article — https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan — Quote: "is small and capped" (wrap-up allowance) ; and the costs page says Claude Code (v2.1.234+) can "wait and continue the interrupted task automatically after the reset".
- Prompt injection and web content — https://code.claude.com/docs/en/security — Quote: "no system is completely immune to all attacks."
- Skip-permissions on a credentialed server — https://www.ssdnodes.com/learn/claude-code-on-a-vps-with-tmux — Quote: "removes the last thing standing between a misread instruction and a `git push --force`."
- SIGTERM leaves the turn unfinished — https://code.claude.com/docs/en/headless — Quote: "Claude Code leaves the turn that was in progress unfinished and records no result for it."
- Agent teams cost — https://code.claude.com/docs/en/costs — Quote: "Agent teams use approximately 7x more tokens than standard sessions when teammates run in plan mode"

### Contradictions
- None found.

### Inferences
- (mine) An overnight design needs: a watchdog that restarts on 401/stall; per-run `--max-budget-usd` and `--max-turns`; fresh sessions per task (not one all-night context); notification on stall (ntfy/Telegram as in the Mac and bux repos); a non-root user with deny rules for `~/.ssh`, vault files and push to protected branches.
- (mine) The machine is an attack surface: a logged-in browser plus `bypassPermissions` means a prompt-injected web page can act as John. Use a dedicated profile with minimal accounts, and `auto` mode or an allowlist instead of bypass where possible.

### Gaps
- No opened source quantifying runaway-cost incidents on a Max plan (an unopened search excerpt mentioned "$1,800+ in 2 days via claude -p"; unverified, not cited).
- Issue #41506 (token-use jump on Max, 2026-03-31) seen as excerpt only.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| claude -p / Agent SDK CLI | https://code.claude.com/docs/en/headless | Official non-interactive Claude Code | VPS/VM/own machine | 2026-10-16 | Use: core of unattended runs; add `--bare` only with API key |
| claude setup-token | https://code.claude.com/docs/en/authentication | One-year OAuth token from a Max plan for headless auth | any server | 2026-10-16 | Use, with watchdog; breaks Remote Control and Chrome ext |
| Remote Control | https://code.claude.com/docs/en/remote-control | Steer a local session from phone/web; subscription login only | the machine | 2026-10-16 | Use for monitoring; gives up after about 10 min offline |
| browser-use/bux | https://github.com/browser-use/bux | Claude Code on a $5 Ubuntu VPS with persistent real Chromium, Telegram, hand-off on login walls (setup prompt tells agents to run installer) | VPS | 2026-10-16 | Candidate/reference only; not installed, not cloned; page contains instructions addressed to agents ("Paste into Claude Code ... and it will set up your VPS for you"); not followed. Spike before trust |
| thereisno-tomorrow/claude-vps | https://github.com/thereisno-tomorrow/claude-vps | Hetzner + Tailscale + tmux bootstrap scripts | Hetzner VPS | 2026-10-16 | Reference only (search excerpt, 0 stars); not verified |
| amineorion/claude-mini-setup | https://github.com/amineorion/claude-mini-setup | Spare Mac, tmux, Tailscale, ntfy hooks | Mac mini | 2026-10-16 | Reference only (search excerpt) |
| nurkert/claude-systemd | https://github.com/nurkert/claude-systemd | systemd service for Claude Code with Remote Control | Linux | 2026-10-16 | Reference only (search excerpt, 0 stars) |
| 1Password for Claude | https://1password.com/blog/1password-for-claude | Vault fill without exposing secrets to the model | Mac desktop | 2026-10-16 | Paid; Mac-only; defer |
| OpenClaw (subscription use) | https://www.theregister.com/software/2026/04/06/anthropic-closes-door-on-subscription-use-of-openclaw/5222854 | Third-party harness | n/a | 2026-10-16 | Reject on subscription: Anthropic excluded third-party harnesses from subscription limits (not opened; excerpt) |
