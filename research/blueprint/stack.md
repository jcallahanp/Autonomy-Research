# Stack

Purpose: every tool the engineer uses, where it runs and what it costs, then where every key and secret lives and who can read it.

Costs are as seen in the findings on 2026-10-16 unless a row says otherwise. "Plan" means John's Claude Max usage pool; the Max price was not opened (engineer-runtime §open q 12). Citations as in decisions.md.

## Tools
| Tool | What it does | Where it runs | Cost | Area | Evidence |
| --- | --- | --- | --- | --- | --- |
| Claude Code CLI, interactive (`/login` Max) | Intake, approval, publishing pages, daytime Channels | VM | Plan | runtime | S1, S16 |
| Claude Code `claude -p` per task | Unattended bounded runs, `--max-turns`, `--max-budget-usd`, `--permission-mode auto --permission-prompts none` | VM | Plan: Path A, Max `/login`, no API key in v1 (updated 2026-10-16, John's decision) | context, human-loop | §Q4; E126, E129 |
| Supervisor (own build) | DAG `ready`, worktrees, bounds, breaker, events, digest, reply parser, reset and resume | VM, systemd | Free | context, protocol, human-loop | §Q7.4; E108, E124 |
| DigitalOcean droplet, Ubuntu 24.04 LTS (updated 2026-10-16, John's decision) | Host and isolation boundary | DigitalOcean Basic, US East, 4 vCPU / 8 GiB | $48/month; snapshots $0.06/GB-month; weekly backups +20% (off by default) | runtime, host | engineer-host E64 |
| Managed settings `/etc/claude-code/managed-settings.json` | Deny rules, `disableBypassPermissionsMode`; beats CLI flags | VM | Free | human-loop | E148-E151 |
| Bash sandbox (bubblewrap) + AppArmor profile | Inner shell isolation, `allowUnsandboxedCommands: false` | VM | Free | human-loop, feasibility | E166-E171; C10 |
| Rootless Podman (as `supervisor`) + host proxy (mitmproxy by default; Envoy or Squid alternatives) | Trial containers `--network none`; allowlist and credential injection | VM | Free | feasibility | C23, C24, C38 |
| SOPS + age, `secretbroker` user, `agent-run` | Encrypted secrets; allowlisted jobs; engineer never reads values | VM | Free (licences not opened) | human-loop | E58-E60 |
| Telegram Bot API (supervisor bot) | Digest, hard-gate prompts, long-poll replies, `from.id` allowlist | SaaS + VM | Free | human-loop, protocol | E16, E118, E103 |
| Channels (Telegram plugin) | Daytime live tool prompts; research preview | VM + phone | Free | human-loop | E111-E114 |
| Remote Control | Phone view of sessions; subscription login only | VM + John's phone | In plan | runtime | C43-C53 |
| Remote Control server mode (`engineer-remote-control` unit) (updated 2026-10-16, John's decision) | John's phone cockpit: live view, new sessions, push notifications; restarted because it exits after about 10 minutes offline | VM + John's phone | In plan | host | engineer-host E103, E104, E106 |
| Max monthly API credits (later option, not v1) (updated 2026-10-16, John's decision) | Would fund a later Slack bridge on an API key | SaaS | Included: Max 5x $100, Max 20x $200 per month; API-key use only | host | engineer-host E122 |
| Twilio SMS (alternative dead-man route) | SMS to John if the chosen route cannot send SMS | SaaS | $0.0083/segment; long code $1.15/month is inference | human-loop | E121 |
| ntfy (alternative) | Push alerts by `curl`; the topic is the password | SaaS | Free | protocol, deploy | E102, E133 |
| healthchecks.io Hobbyist (chosen dead-man route) | The supervisor pings a check at every loop and at least every 15 minutes (untested default); `ExecStopPost` sends a fail ping; when pings stop, healthchecks.io notifies John's phone by SMS if Hobbyist offers it, else by its Telegram or email integration (untested, SP72) | SaaS | Free: 20 jobs | deploy | E131 |
| UptimeRobot Free | Uptime checks of deployed apps and VM web services | SaaS | Free: 50 monitors | deploy | E129 |
| Superpowers, https://github.com/obra/superpowers at commit `bb92a77` (pin recorded in /home/user/attio-project/CLAUDE.md; version label 7.0.0 unverified) | Brainstorm gate, writing-plans, fresh subagent per task, verification, worktrees | Plugin | Free (MIT) | planning, context, protocol | E25, E82; E19, E40 |
| Hooks (SessionStart, PreToolUse, PostToolUse, Stop/TaskCompleted) | Re-inject state, guards, lint, done gate | VM | Free | context, protocol | §Q7.1-7.3; E11, E15 |
| `auditor` agent + `audit.sh` | Script layer then narrow claim judge | VM | Tokens, about 2-4x per gated task (inference from E151) | protocol | E137-E151 |
| backcheck, https://github.com/VectorInstitute/backcheck (spike first) | Claim vs transcript check, no LLM | VM | Free (Apache-2.0) | protocol | E152, E153 |
| `gh`, `claude --worktree`, GitHub branch protection, CODEOWNERS | PR per task, server-side merge stop | VM + GitHub | Private-repo protection under GitHub Pro, which John bought (updated 2026-10-16, John's decision); Pro price not opened | protocol | E50-E59 |
| GitHub bot account + fine-grained PAT | Repo-scoped agent credential | GitHub | Free | protocol, human-loop | E80, E81; E13, E40 |
| Playwright CLI skill (`@playwright/cli`) | Alternate browser driver | VM | Free, Apache-2.0 | browser | T4, T41 |
| Playwright MCP, `--browser chrome` (updated 2026-10-16, stage-1 plan) | Primary browser driver; drives branded Chrome, `browser_drag` | VM, stdio | Free, Apache-2.0 | browser, host | T1, S1; engineer-host E12 |
| Playwright Test Agents, trace viewer | Generate and heal `.spec.ts` flows | VM | Free | browser | T39, T40; R1, R2 |
| Branded Google Chrome via Playwright `channel chrome`, headed, non-default `--user-data-dir`; Xvfb, x11vnc, noVNC behind Cloudflare Access (updated 2026-10-16, John's decision) | Persistent logged-in profile; John's one-time hand sign-in | VM, private network | Free; noVNC MPL 2.0 | browser, host | S1, S2, S38; engineer-host E12, E13 |
| Claude in Chrome | Attended setup sitting only; off under API key | John's machine | Not stated | feasibility, browser | D44-D46; T17 |
| Mermaid flowchart, mermaid-lint, mermaid-cli | Diagram source, parse gate, dark SVG | VM, CI | Free (mermaid-lint MIT) | briefing | E49, E58, E59 |
| Claude artifacts | Published brief for John's phone | Interactive `/login` session | Plan | briefing | E51-E53 |
| n8nmermaid, docker-compose-to-mermaid, dependency-cruiser, pydeps | Generated diagrams and import graphs | VM | Free | briefing, existing-systems | E67-E69; M10-M12 |
| Explore subagents | Per-module mapping, reads above about 128K-256K | VM | Tokens | existing-systems, models | M26; E33 |
| Official MCP Registry, plugin marketplaces, Smithery | Discovery lead sources | curl | Free, keyless | tool-discovery | E1-E16 |
| OSV.dev, deps.dev, Scorecard API, npm attestations | Vet card | curl | Free, keyless | tool-discovery | E41-E50 |
| Socket free | Install-time malware check, npm PRs | GitHub app, CLI | $0: 1,000 scans/month | tool-discovery, security | E54, E55; E49 |
| Semgrep CE, Bandit or Ruff `S`, OSV-Scanner, pip-audit, `npm audit` | SAST and dependency scans | VM, CI | Free | security | E25-E39 |
| gitleaks `--redact` | Secret scan, pre-commit and CI | VM, CI | Free (MIT) | security, existing-systems | E44; B16 |
| ZAP baseline, Checkov, Lynis, Dependabot alerts | DAST on own staging, IaC, VM audit, alerts | CI, VM, GitHub | Free | security | E35, E54, E57, E61 |
| `/security-review`, Claude Security plugin | LLM review per PR and per milestone | Interactive session | Plan usage; no price | security | E70, E71, E149 |
| lychee, Schemathesis, Atlas (where they apply) | Drift gates | CI | lychee, Atlas not stated; Schemathesis MIT | planning | E49-E54 |
| wrangler, Cloudflare Workers, D1, R2 | Default web deploy, cron, receivers | SaaS + VM CLI | Free: 100k requests/day; D1 5M reads/day, 5 GB; R2 10 GB-month | deploy | E1-E5 |
| Cloudflare Tunnel + Access | Private sign-in to VM services; noVNC at `novnc.<domain>` with a one-email policy, SSH tunnel as fallback (updated 2026-10-16, John's decision) | SaaS + VM | Free-seat count and Tunnel price unverified | deploy, host | E30, E31; engineer-host E80 |
| Tailscale (fallback only) (updated 2026-10-16, John's decision) | Exit node at home for the browser's traffic, only if the setup-day sign-in test (SP85) fails | VM + home device | Free: Personal plan, 3 users, 100 devices | host | engineer-host E81 |
| Mac mini M6 at home (fallback only) (updated 2026-10-16, John's decision) | The same setup on a residential IP, only if SP85 fails and the Tailscale route does not fix it | John's home | $899 one-off | host | engineer-host E74, E75 |
| Google Cloud Run, Workload Identity | Container APIs from source, short-lived tokens | GCP | Free tier per billing account; quote unverified | deploy | E26, E27, E109 |
| Neon Free / Supabase Free | Postgres | SaaS | Neon 100 CU-hours/project/month; Supabase 2 projects, 500 MB | deploy | E21, E23 |
| Docker Compose (deploy target host, not the engineer VM; or `podman compose` there, builder decides and records), systemd timers | Always-on processes, scheduler | Deploy VM | Free | deploy | E29, E59 |
| n8n (John's existing instance) | John's visual flows; nightly export to git | Open until John answers (open-questions 16): his n8n Cloud, or self-hosted Community on a VM if he moves it | Community free with internal-business licence; Cloud Starter 20 EUR/month annual | deploy | E45, E47, E48, E51 |
| Gradle, Capacitor, adb | Android builds and installs | VM | Free | deploy | E69, E72, E79 |
| Attio REST + MCP, Clay CLI/plugin, n8n API, Outreach REST, Slack manifest API | GTM reads and writes | SaaS | John's plans; Clay tables Enterprise only | existing-systems, browser | S1-S60; A1-A43 |
| `openai/codex-plugin-cc` (off) | Cross-family Tier 2 review after a spike | VM | OpenAI key; GPT-6.1 Sol $2/$10 per 1M | models | E67, E68 |
| Gemini 4 Argon (not in v1) | Video, PDF, long-output jobs after a spike | SaaS | $2/$10 per 1M through 2026-11-30, then $4/$20 | models | E2-E4 |

## VM size
Fixed by John (updated 2026-10-16, John's decision): DigitalOcean Basic, US East, 4 vCPU, 8 GiB RAM, 160 GiB disk, Ubuntu 24.04 LTS, $48/month (engineer-host E64). Headed Chrome, trial containers and parallel `claude -p` workers are why it is larger than "A $5/mo VPS is fine" (engineer-runtime S29). SP88 measures memory with real Attio, Clay and n8n tabs; the droplet resizes in place if it is short (engineer-host E84). `doctor.sh` fails below it.

## Install list
Pins: the builder picks the current stable release on build day and records it in `engineer/docs/versions.md` (updated 2026-10-16, stage-1 plan) (untested default, confirmed by SP22), except where a row states a pin from the findings or this repo. "root" means `setup-root.sh --install`, run by John (setup.md step 6); "bootstrap" means `bootstrap.sh`, run unprivileged by the builder (step 8).
| Tool | Installed by | Runs where | Pin or source |
| --- | --- | --- | --- |
| Users `engineer`, `secretbroker`, `supervisor`, `egress` (runs the proxy) (updated 2026-10-16, stage-1 plan); AppArmor profile; managed settings; sudoers; nftables egress rules; systemd units | root | VM | n/a |
| Rootless Podman with subuid/subgid for `supervisor` (no Docker Engine, no `docker` group) | root | VM | Ubuntu archive |
| sops, age; age key and SOPS file skeleton for `secretbroker` | root | VM | Release binaries, checksum-verified |
| Node.js | root | VM | 22 LTS or later from the NodeSource apt repo (mermaid-lint needs Node 22+, engineer-briefing E59) |
| Google Chrome, Xvfb, a window manager, x11vnc, noVNC + websockify, Playwright system deps | root | VM | Distribution and Google apt repos (install steps are worker inference, engineer-browser setup 1) |
| `gh`, `gcloud`, `cloudflared`, Lynis | root | VM | GitHub, Google, Cloudflare apt repos; Ubuntu archive (updated 2026-10-16, John's decision) |
| mitmproxy (the host proxy) | root | VM | Recorded pin; Envoy or Squid are the alternatives (engineer-feasibility C23) |
| `/opt/engineer/` (bin wrappers, hooks, broker jobs, supervisor, the plugin with the vendored Superpowers subset) | root, copied from `/srv/autonomy-research/engineer/` (updated 2026-10-16, stage-1 plan) | VM | The merged SHA |
| pyotp (later stage, when a project needs TOTP) (updated 2026-10-16, John's decision) | root, in a venv owned by `secretbroker` | VM | Recorded pin |
| Claude Code CLI | bootstrap | VM, `engineer` | At least 2.1.234, the version the auto-continue docs name (engineer-protocol E117); exact pin recorded |
| Playwright, `@playwright/mcp`, `@playwright/cli` (branded Chrome comes from the Google apt repo) (updated 2026-10-16, stage-1 plan) | bootstrap (user npm prefix and browser cache) | VM | Recorded pin (engineer-browser T4, T1) |
| mermaid-lint, mermaid-cli | bootstrap | VM, CI | mermaid-cli 11.12.0, as in `tests/check-mermaid.sh` |
| wrangler, Clay CLI (run by broker jobs) | root, into `/opt/engineer/node_modules` | VM | Recorded pin; Clay CLI package name not in the findings, builder takes it from Clay's docs (SP65) |
| dependency-cruiser, docker-compose-to-mermaid | bootstrap (npm) | VM | Recorded pin |
| Semgrep CE, Bandit or Ruff, OSV-Scanner, pip-audit, gitleaks, Checkov, n8nmermaid, pydeps | bootstrap (user venv or release binaries) | VM, CI | Version plus checksum (engineer-security E41, E42) |
| backcheck (after SP20) | bootstrap, via its `install.sh` | VM | https://github.com/VectorInstitute/backcheck, Apache-2.0 (engineer-protocol notes `audit-gap.md`:92) |
| Channels Telegram plugin (the one user-scope exception, repo-composition.md) | bootstrap (`claude plugin install` from the Anthropic-maintained marketplace; the preview accepts only allowlisted plugins, engineer-runtime H37) | VM | Recorded pin |
| Android SDK, Gradle, adb | `bootstrap.sh --with-android` | VM | Recorded pin |
| n8n | Not installed by default; only if John moves n8n to the VM | VM | Open (open-questions 16) |

## Egress
Mechanism (builder default, untested; SP09, SP13, SP26): root-owned nftables rules match the `engineer` and `supervisor` user IDs and allow outbound traffic only to the local mitmproxy, which enforces a domain allowlist; `HTTPS_PROXY` points Claude Code at it, and the Bash sandbox network settings sit inside that. Root's own traffic (apt) is not restricted. Trial containers get a per-trial list through the same proxy (engineer-feasibility C23, C24).
- Install-mode list (`templates/egress-install.txt`, from `--install` until `--lock`): everything in the runtime list, the login and consent hosts for the sitting (Google sign-in and consent, GitHub, Cloudflare dashboard, Outreach, WHOOP and Withings developer and consent pages, Slack), plus registry.npmjs.org, github.com and its release and content hosts, the Playwright browser download host, pypi.org and its file host. Hosts are logged so `--lock` can drop what only installs needed. Outreach, WHOOP, Withings and Slack hosts join only with the project that needs them (setup.md, Per-project rows) (updated 2026-10-16, John's decision).
- Runtime list (`templates/egress-allowlist.txt`, from `--lock`): Anthropic API and claude.ai hosts; github.com and its API host; api.telegram.org; the healthchecks.io and UptimeRobot API hosts; the API hosts of Attio, Clay, n8n, Outreach, Slack, Google, WHOOP, Withings, Cloudflare, Vercel, Supabase and Neon actually in use; osv.dev, deps.dev, the Scorecard API and the official MCP Registry; and, for Chrome, the web-app and login hosts of Attio, Clay, n8n, Outreach and Google sign-in that browser-only work and re-logins need (engineer-browser §Q11). The builder writes the exact host names from the logged requests of the sitting.
- Adding a host: a denied request becomes a T1 digest line; John runs `sudo setup-root.sh --allow <host>`.

## Where secrets live and who can read them
Rule: the model never receives a value through chat or a file it can read (engineer-human-loop §Q3, E81, E82).
| Secret | Lives in | Who can read it | Evidence |
| --- | --- | --- | --- |
| age private key | `secretbroker` home, 0600 | `secretbroker` only | engineer-human-loop E58-E60 |
| SaaS keys: Attio, n8n (with expiry), Outreach, Google, Slack, WHOOP and Withings OAuth refresh tokens (written by `oauth-capture`, a later stage; per project) (updated 2026-10-16, stage-1 plan) | SOPS files | `secretbroker`; used by `agent-run` jobs; rotated refresh tokens written back on every refresh | engineer-human-loop E21-E25; engineer-feasibility spike 19 |
| Parent tokens: Cloudflare (Account API Tokens Edit), Vercel, Supabase PAT, Slack config token (12 h) | SOPS files | `secretbroker`; children minted per job | engineer-human-loop E1-E11, E28-E34 |
| GitHub bot fine-grained PAT (Contents, Pull requests, Metadata) | SOPS files | `secretbroker`; pushes and PRs go through an `agent-run` job (blueprint inference) | engineer-protocol E80, E81 |
| Telegram supervisor bot token | SOPS files | `secretbroker` only: the supervisor never holds it, it calls the `tg-send` and `tg-poll` broker jobs (builder default; repo-composition.md Enforcement) | engineer-human-loop E15, E118 |
| healthchecks.io ping URL, UptimeRobot API key | SOPS files | `secretbroker`; the supervisor pings through the `hc-ping` broker job | engineer-deploy E129, E131 |
| Clay CLI, `gh`, `gcloud` session stores | `secretbroker`'s home, created when John runs the sign-in as `secretbroker` | `secretbroker` only | setup.md step 27 (builder default) |
| Deploy key for Autonomy-Research (read-only) (updated 2026-10-16, stage-1 plan) | `/root/.ssh/autonomy-research` | root, used by John for `git pull` before `--install` | setup.md step 5 (builder default) |
| Telegram Channels bot token | The Channels plugin's config under `engineer`, because the daytime session uses it | `engineer` user, so the model can read it; this bot carries no approvals (ruling 3) | engineer-runtime C54, C57 (blueprint inference on location) |
| Trial test credentials | Host proxy config | Proxy only; injected on the wire, never inside the trial container | engineer-feasibility C17, C23, C24 |
| Cloud deploy credentials | None stored: GitHub OIDC and Workload Identity mint short-lived tokens | GitHub Actions job | engineer-deploy E109-E114 |
| Deploy secrets for apps | Vault, piped to `wrangler secret put` and similar setters | Setter process; never `echo VALUE |` | engineer-deploy E102-E108 |
| TOTP seeds | Local seed with pyotp behind a broker wrapper; no 1Password (updated 2026-10-16, John's decision) | Wrapper returns the code only | engineer-browser S13, S15 (Exa highlights) |
| Browser profile cookies | `--user-data-dir` under the engineer user, chmod 700, gitignored, Read denied | Engineer OS user; the deny rule is not a boundary (engineer-human-loop E142-E145) | engineer-browser §Implications 2 |
| Max `/login` credentials (`claude auth login`, never `setup-token`) (updated 2026-10-16, John's decision) | Claude Code's own store for the engineer user | Engineer user; location not covered by the findings (unverified) | engineer-runtime S16 |
| OpenAI or Gemini keys (optional) | SOPS; wrapper process only, never a job-wide variable | Wrapper | engineer-models S8 |
| ntfy topic, Twilio credentials (optional) | SOPS | Supervisor | engineer-deploy E133; engineer-human-loop E121 |
| Production, billing and backup values | Outside the engineer's reach | John only | engineer-human-loop setup step 6 |
| Bootstrap values | 0600 env file, deleted after bootstrap | root during bootstrap | engineer-runtime P29, P31 (ruling 6) |
| Names of all of the above | `.env.example`, `integrations.yaml`, credential inventory | Everyone; names only | engineer-existing-systems J17, J28 |
