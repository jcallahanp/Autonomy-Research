# Stack

Purpose: every tool the engineer uses, where it runs and what it costs, then where every key and secret lives and who can read it.

Costs are as seen in the findings on 2026-10-16 unless a row says otherwise. "Plan" means John's Claude Max usage pool; the Max price was not opened (engineer-runtime §open q 12). Citations as in decisions.md.

## Tools
| Tool | What it does | Where it runs | Cost | Area | Evidence |
| --- | --- | --- | --- | --- | --- |
| Claude Code CLI, interactive (`/login` Max) | Intake, approval, publishing pages, daytime Channels | VM | Plan | runtime | S1, S16 |
| Claude Code `claude -p` per task | Unattended bounded runs, `--max-turns`, `--max-budget-usd`, `--permission-mode auto --permission-prompts none` | VM | Path A plan; Path B per-token, prices not verified | context, human-loop | §Q4; E126, E129 |
| Supervisor (own build) | DAG `ready`, worktrees, bounds, breaker, events, digest, reply parser, reset and resume | VM, systemd | Free | context, protocol, human-loop | §Q7.4; E108, E124 |
| Ubuntu 24.04 VM | Host and isolation boundary | VPS or home box | "A $5/mo VPS is fine" (S29); 10-20 EUR/month for 4 vCPU/8 GB is unverified | runtime | S29 |
| Managed settings `/etc/claude-code/managed-settings.json` | Deny rules, `disableBypassPermissionsMode`; beats CLI flags | VM | Free | human-loop | E148-E151 |
| Bash sandbox (bubblewrap) + AppArmor profile | Inner shell isolation, `allowUnsandboxedCommands: false` | VM | Free | human-loop, feasibility | E166-E171; C10 |
| Docker or rootless Podman + host proxy (Envoy, mitmproxy or Squid) | Trial containers `--network none`; allowlist and credential injection | VM | Free | feasibility | C23, C24, C38 |
| SOPS + age, `secretbroker` user, `agent-run` | Encrypted secrets; allowlisted jobs; engineer never reads values | VM | Free (licences not opened) | human-loop | E58-E60 |
| 1Password `op` (only if John has it) | Replaces SOPS as secret source; TOTP | VM | Price not opened | deploy, browser | E112; S13 |
| Telegram Bot API (supervisor bot) | Digest, hard-gate prompts, long-poll replies, `from.id` allowlist | SaaS + VM | Free | human-loop, protocol | E16, E118, E103 |
| Channels (Telegram plugin) | Daytime live tool prompts; research preview | VM + phone | Free | human-loop | E111-E114 |
| Remote Control | Phone view of sessions; subscription login only | VM + John's phone | In plan | runtime | C43-C53 |
| Twilio SMS (optional) | Dead-man alert only | SaaS | $0.0083/segment; long code $1.15/month is inference | human-loop | E121 |
| ntfy (alternative) | Push alerts by `curl`; the topic is the password | SaaS | Free | protocol, deploy | E102, E133 |
| UptimeRobot Free / healthchecks.io Hobbyist | Uptime and cron checks paging John | SaaS | Free: 50 monitors / 20 jobs | deploy | E129, E131 |
| Superpowers 7.0.0 (commit bb92a77) | Brainstorm gate, writing-plans, fresh subagent per task, verification, worktrees | Plugin | Free (MIT) | planning, context, protocol | E25, E82; E19, E40 |
| Hooks (SessionStart, PreToolUse, PostToolUse, Stop/TaskCompleted) | Re-inject state, guards, lint, done gate | VM | Free | context, protocol | §Q7.1-7.3; E11, E15 |
| `auditor` agent + `audit.sh` | Script layer then narrow claim judge | VM | Tokens, about 2-4x per gated task (inference from E151) | protocol | E137-E151 |
| backcheck (spike first) | Claim vs transcript check, no LLM | VM | Free (Apache-2.0) | protocol | E152, E153 |
| `gh`, `claude --worktree`, GitHub branch protection, CODEOWNERS | PR per task, server-side merge stop | VM + GitHub | Private-repo protection under Pro; Pro price unverified | protocol | E50-E59 |
| GitHub bot account + fine-grained PAT | Repo-scoped agent credential | GitHub | Free | protocol, human-loop | E80, E81; E13, E40 |
| Playwright CLI skill (`@playwright/cli`) | Primary browser driver | VM | Free, Apache-2.0 | browser | T4, T41 |
| Playwright MCP | Alternate driver, `browser_drag` | VM, stdio | Free, Apache-2.0 | browser | T1, S1 |
| Playwright Test Agents, trace viewer | Generate and heal `.spec.ts` flows | VM | Free | browser | T39, T40; R1, R2 |
| Headed Chrome `--user-data-dir`, Xvfb, x11vnc, noVNC | Persistent logged-in profile; John's one-time logins | VM, private network | Free; noVNC MPL 2.0 | browser | S1, S2, S38 |
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
| Cloudflare Tunnel + Access | Private sign-in to VM services | SaaS + VM | Free-seat count and Tunnel price unverified | deploy | E30, E31 |
| Google Cloud Run, Workload Identity | Container APIs from source, short-lived tokens | GCP | Free tier per billing account; quote unverified | deploy | E26, E27, E109 |
| Neon Free / Supabase Free | Postgres | SaaS | Neon 100 CU-hours/project/month; Supabase 2 projects, 500 MB | deploy | E21, E23 |
| Docker Compose, systemd timers | Always-on processes, scheduler | VM | Free | deploy | E29, E59 |
| n8n self-hosted (Community) | John's visual flows; nightly export to git | VM | Free; internal-business licence | deploy | E47, E51 |
| Gradle, Capacitor, adb | Android builds and installs | VM | Free | deploy | E69, E72, E79 |
| Attio REST + MCP, Clay CLI/plugin, n8n API, Outreach REST, Slack manifest API | GTM reads and writes | SaaS | John's plans; Clay tables Enterprise only | existing-systems, browser | S1-S60; A1-A43 |
| `openai/codex-plugin-cc` (off) | Cross-family Tier 2 review after a spike | VM | OpenAI key; GPT-6.1 Sol $2/$10 per 1M | models | E67, E68 |
| Gemini 4 Argon (not in v1) | Video, PDF, long-output jobs after a spike | SaaS | $2/$10 per 1M through 2026-11-30, then $4/$20 | models | E2-E4 |

## Where secrets live and who can read them
Rule: the model never receives a value through chat or a file it can read (engineer-human-loop §Q3, E81, E82).
| Secret | Lives in | Who can read it | Evidence |
| --- | --- | --- | --- |
| age private key | `secretbroker` home, 0600 | `secretbroker` only | engineer-human-loop E58-E60 |
| SaaS keys: Attio, n8n (with expiry), Clay CLI session, Outreach OAuth tokens, WHOOP and Withings refresh tokens | SOPS files | `secretbroker`; used by `agent-run` jobs; rotated refresh tokens written back on every refresh | engineer-human-loop E21-E25; engineer-feasibility spike 19 |
| Parent tokens: Cloudflare (Account API Tokens Edit), Vercel, Supabase PAT, Slack config token (12 h) | SOPS files | `secretbroker`; children minted per job | engineer-human-loop E1-E11, E28-E34 |
| GitHub bot fine-grained PAT (Contents, Pull requests, Metadata) | SOPS files | `secretbroker`; pushes and PRs go through an `agent-run` job (blueprint inference) | engineer-protocol E80, E81 |
| Telegram supervisor bot token | SOPS files | Supervisor through the broker (blueprint inference) | engineer-human-loop E15, E118 |
| Trial test credentials | Host proxy config | Proxy only; injected on the wire, never inside the trial container | engineer-feasibility C17, C23, C24 |
| Cloud deploy credentials | None stored: GitHub OIDC and Workload Identity mint short-lived tokens | GitHub Actions job | engineer-deploy E109-E114 |
| Deploy secrets for apps | Vault, piped to `wrangler secret put` and similar setters | Setter process; never `echo VALUE |` | engineer-deploy E102-E108 |
| TOTP seeds | 1Password, or local seed with pyotp behind a wrapper | Wrapper returns the code only | engineer-browser S13, S15 (Exa highlights) |
| Browser profile cookies | `--user-data-dir` under the engineer user, chmod 700, gitignored, Read denied | Engineer OS user; the deny rule is not a boundary (engineer-human-loop E142-E145) | engineer-browser §Implications 2 |
| Max `/login` credentials | Claude Code's own store for the engineer user | Engineer user; location not covered by the findings (unverified) | engineer-runtime S16 |
| Anthropic API key (Path B only) | SOPS; exported only into the supervisor's `claude -p` environment | Any process in that environment, so the model's shell may see it (open question) | engineer-runtime S15; engineer-human-loop E26 |
| OpenAI or Gemini keys (optional) | SOPS; wrapper process only, never a job-wide variable | Wrapper | engineer-models S8 |
| ntfy topic, Twilio credentials (optional) | SOPS | Supervisor | engineer-deploy E133; engineer-human-loop E121 |
| Production, billing and backup values | Outside the engineer's reach | John only | engineer-human-loop setup step 6 |
| Bootstrap values | 0600 env file, deleted after bootstrap | root during bootstrap | engineer-runtime P29, P31 (ruling 6) |
| Names of all of the above | `.env.example`, `integrations.yaml`, credential inventory | Everyone; names only | engineer-existing-systems J17, J28 |
