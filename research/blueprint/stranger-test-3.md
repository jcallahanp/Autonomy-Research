# Stranger test 3

Date: 2026-10-16. Tester: a fresh session with no prior knowledge of the project.

Read only: `README.md`, `decisions.md`, `flow.md`, `gtm-scenario.md`, `open-questions.md`, `repo-composition.md`,
`requirements-trace.md`, `setup.md`, `spikes.md`, `stack.md` in this folder, and the four
`docs/diagrams/engineer-*.mmd` files. Not read: `digests/`, `hand-check.md`, `verification.md`, earlier stranger tests,
or the findings files the blueprint cites. Question: could I start building the engineer tomorrow from these files alone?

## 1. Exact tools

Pins: unless a row gives one, the builder picks the current stable release on build day and records it in
`docs/versions.md` (stack.md:64).

### On the VM (Ubuntu 24.04, at least 4 vCPU, 8 GB RAM, 80 GB disk; VPS or home box, John's choice)
| Tool | Version or plan | Installed by | Runs as / where |
| --- | --- | --- | --- |
| Claude Code CLI (interactive `/login` and `claude -p`) | at least 2.1.234; Max plan (Path A) or Console API key (Path B, John's choice) | `bootstrap.sh` | `engineer` user |
| Channels Telegram plugin | recorded pin, Anthropic marketplace | bootstrap | `engineer`, daytime tmux session |
| Remote Control | in Max plan | built into Claude Code | `engineer` sessions + John's phone |
| Supervisor (own code) | template SHA | `setup-root.sh` copy to `/opt/engineer/` | `supervisor` user, systemd `engineer-supervisor.service` |
| `run-task`, `agent-run` wrappers | template SHA | setup-root | root-owned in `/opt/engineer/bin/` |
| Managed settings `/etc/claude-code/managed-settings.json` | n/a | setup-root | root-owned |
| Bash sandbox (bubblewrap) + AppArmor profile | n/a | setup-root | VM |
| nftables egress rules + mitmproxy host proxy (Envoy or Squid alternatives) | recorded pin | setup-root | VM, matches `engineer` and `supervisor` UIDs |
| Docker Engine + Compose, or rootless Podman | distro or Docker apt | setup-root | VM (trial containers `--network none`) |
| sops, age | release binaries, checksum-verified | setup-root | `secretbroker` user |
| pyotp (only without 1Password) | recorded pin, venv | setup-root | `secretbroker` |
| 1Password `op` (only if John has it) | price not opened | setup-root | VM |
| Node.js | 22 LTS or later, NodeSource | setup-root | VM |
| Google Chrome, Xvfb, window manager, x11vnc, noVNC + websockify | distro and Google apt | setup-root | VM; systemd units `chrome-xvfb`, `novnc`; noVNC on 127.0.0.1:6080 |
| `gh`, `gcloud`, `cloudflared`, Lynis | vendor apt repos | setup-root | VM |
| Playwright, its browsers, `@playwright/cli`, Playwright MCP, Playwright Test Agents | recorded pin | bootstrap (user npm prefix) | `engineer` |
| mermaid-lint, mermaid-cli | mermaid-cli 11.12.0 | bootstrap | VM and CI |
| wrangler, dependency-cruiser, docker-compose-to-mermaid | recorded pin | bootstrap (npm) | VM |
| Semgrep CE, Bandit or Ruff `S`, OSV-Scanner, pip-audit, `npm audit`, gitleaks, Checkov, n8nmermaid, pydeps | version + checksum | bootstrap | VM and CI |
| backcheck | after SP20, via its `install.sh` | bootstrap | VM |
| Clay CLI | package name not given (SP65) | bootstrap | VM |
| Android SDK, Gradle, adb, Capacitor | recorded pin | `bootstrap.sh --with-android` (later) | VM |
| Superpowers | commit `bb92a77`, vendored minus TDD and finishing skills | template | plugin |
| MCP: Playwright, DeepWiki, Firecrawl | pinned + `tools/list` hash | `plugin/.mcp.json` | VM, stdio/HTTP |
| MCP: Attio, n8n instance (2.13+), Outreach, Vercel (if used) | URLs and auth not given (open q 35) | `claude mcp add --scope user` | `engineer` user scope |
| n8n | not installed unless John moves it (open q 16) | n/a | his Cloud or self-hosted |

### SaaS accounts and services
| Service | Plan or cost | Who signs up |
| --- | --- | --- |
| Anthropic Claude Max (Path A) or Console API key (Path B) | Max price not opened; per-token prices not verified | John |
| GitHub: John's account, private `engineer-template`, a hand-made bot account with fine-grained PAT | Free; Pro only if he picks it for R16 (price unverified) | John |
| Telegram: two bots via @BotFather (supervisor, Channels) | free | John |
| healthchecks.io | Hobbyist, free, 20 jobs | John |
| UptimeRobot | Free, 50 monitors | John |
| Cloudflare (Workers, D1, R2, Tunnel, Access; domain if none) | Free tier; domain purchase is a T2 money prompt | John |
| Google Cloud (Cloud Run, Workload Identity) and Google OAuth app | free tier, quote unverified | John |
| Neon Free or Supabase Free; Vercel Hobby if used | free | John |
| Attio, Clay, n8n, Outreach, Slack | John's existing plans; Clay tables Enterprise-only | John (existing) |
| WHOOP, Withings developer apps | Withings+ need unknown (SP73) | John |
| Socket free (1,000 scans/month), Dependabot | free | builder via GitHub |
| Keyless lookups: official MCP Registry, plugin marketplaces, Smithery, OSV.dev, deps.dev, Scorecard API | free | none |
| Optional later: Twilio SMS ($0.0083/segment), ntfy, OpenAI key for `codex-plugin-cc`, Gemini 4 Argon, CodeRabbit | off in v1 | John |
| claude.ai connectors (Exa, Parallel Search, Context7, Mermaid Chart) | in plan; interactive `/login` sessions only | already connected |

### Elsewhere
- claude.ai/code cloud session: phase A builder (no VM).
- GitHub Actions CI: `claude plugin validate --strict`, `tests/check.sh`, `tests/check-mermaid.sh`, gitleaks, scanners, Actions pinned by SHA.
- John's machine: SSH, SSH tunnel to noVNC, Claude in Chrome for attended one-offs. John's phone: Telegram, Remote Control, healthchecks.io alerts.

## 2. Setup steps in order
[J] = John by hand; [B] = builder session; [J+B] = both.

Phase A (no VM)
1. [J] Create private GitHub repo `engineer-template`; open a claude.ai/code session on it.
2. [B] Write the template (scripts first, then supervisor, broker, trial, snapshot, checks, plugin changes, templates, tests, CI); PR; [J] merges when CI is green.
3. [B] SP01: re-read Agent SDK billing and legal page; write the Path A/B page.

Phase B (bring-up)
4. [J] Rent or prepare the Ubuntu 24.04 VM; add his SSH key.
5. [J] As root, make a read-only deploy key, add it to the repo, clone to `/srv/engineer-template`.
6. [J] `sudo setup-root.sh --install` (users, packages, `/opt/engineer/`, managed settings without hooks, sudoers, units installed not enabled, AppArmor, containers, install-mode egress, builder checkout).
7. [J] As `engineer`: `tmux new -s builder`, `claude`, `/login` with Max; start the builder session.

Phase C (builder on VM, before guards)
8. [B] `bootstrap.sh` (user-level installs); SP22, SP23.
9. [B] Test hooks from a scratch project's `.claude/settings.json`; SP06, SP09, SP13.
10. [B] Broker jobs with a dummy canary; SP11, SP12.
11. [B] Supervisor loop on a toy repo; SP04, SP05, SP07, SP08.
12. [B] Trial runner (container, proxy, `result.json`, teardown, sweep); SP03, SP26-SP28.
13. [B] Approval-hash hook, reply parser, browser profile perms, noVNC, privacy settings, dead-ends and vet card, Channels plugin; SP15, SP17, SP53, SP54, SP64.
14. [B] runs SP02; [J] decides Path A or B and 1Password; ADR committed.

Phase D (John's one sitting, long waits first)
15. [J] Outreach API app and employer approval.
16. [J] Google app, OAuth client, consent screen to production.
17. [J] WHOOP and Withings developer apps.
18. [J] healthchecks.io and UptimeRobot sign-up; seed ping URL and keys; phone as target.
19. [J] GitHub bot account by hand, fine-grained PAT, bot write access to repos.
20. [J] Branch protection from his admin account (SP18).
21. [B] push Phase C commits through `agent-run push-branch`; [J] merges, pulls into `/srv`, re-runs `--install`.
22. [J] Two Telegram bots, `/start`, seed tokens, Channels allowlist.
23. [J] Remote Control push on phone.
24. [J] Cloudflare account (domain if none), parent token.
25. [J] Path B only: Console API key.
26. [J] Vercel token, Supabase PAT if used.
27. [J] Attio key, n8n key with expiry, Clay CLI first sign-in.
28. [J] GCP roles for Workload Identity; [B] binds OIDC subject.
29. [J] Slack config token; [B] creates the app from a manifest.
30. [J] All consent clicks: Slack install, Google, Outreach, WHOOP, Withings.
31. [J] Browser logins through the SSH tunnel to noVNC: Google first, then Attio, Clay, n8n, Outreach.
32. [J] TOTP seeds into 1Password or `seed`.
33. [J] Data-privacy toggle; confirm hard gates and default `profile.yaml`.
34. [J] `sudo setup-root.sh --lock` (last John row).

Phase E (builder under guards)
35. [B] Rerun guard spikes under lock (SP06, SP10, SP13); on failure [J] `--unlock`, PR, `--install`, `--lock`.
36. [B] `verify-all.sh` "Verifies all" table.
37. [B] `cloudflared` tunnel and Access app via broker; UptimeRobot monitors; [J] logs in from phone.
38. [B] n8n nightly JSON export to git.
39. [B] Daytime Channels session in tmux.
40. [B] Enable unattended runs (after step 14 and spikes section A).

Later, each needs John: 41 R16 self-merge route plus two weeks shadow mode [J]; 42 cross-family reviewer key [J]; 43 Android toolchain [B].

## 3. How the repo is composed
Template repo `engineer-template` (private, John's account):
- `plugin/skills/`: changed `interview`, `research`, `tool-scan`, `repo-triage`, `spike`, `system-map`, `setup`; new `as-is`, `plan`, `browser`, `deploy`, `security-review`, `digest`.
- `plugin/agents/`: existing `researcher`, `synthesizer`, `verifier`, `spike-worker`; new `mapper`, `merger`, `planner`, `implementer`, `plan-reviewer`, `auditor`, `triage-reader` (tiers: planner Opus/Fable class; implementer, reviewer, auditor Sonnet class; Haiku roles only after SP32).
- `plugin/hooks/`: `hooks.json` + scripts, source only; installed root-owned in `/opt/engineer/hooks/`. Events: SessionStart `startup|resume|compact` (state re-inject), PreToolUse (protected-path deny, destructive git, approval-hash check, deploy allowlist, vendor CLIs, browser domain allowlist, kill switch, dead-end reminder), PostToolUse (lint, typecheck, mermaid-lint, redaction pending SP14), Stop/TaskCompleted (evidence command, DEPENDENTS check, security gate, exit 2), StopFailure/Notification (event taps).
- `plugin/scripts/playwright-mcp.sh`, `plugin/.mcp.json` (playwright, deepwiki, firecrawl), `plugin/evals/`.
- `scripts/`: `setup-root.sh` (`--install`, `--lock`, `--unlock`, `--allow`), `bootstrap.sh`, `doctor.sh`, `cloud-setup.sh`; `supervisor/` (loop, DAG ready, bounds and breaker, events, morning, Telegram send/poll, reply parser, reset parser, reconcile); `trial/` (launch, proxy config, teardown, sweep); `broker/` (job allowlist; jobs `seed`, `push-branch`, `open-pr`, `mint-child`, `api-call`, `tg-send`, `tg-poll`, `hc-ping`); `snapshot/` (attio, clay, n8n, outreach, slack); `checks/` (`verify-all.sh`, `audit.sh`, test-diff guard, pre-merge refusal, parity, contrast, vet-card, staleness, integrations-vs-.env.example, n8n export).
- `templates/`: `managed-settings.json`, `egress-install.txt`, `egress-allowlist.txt`, `run-defaults.yaml`, `schemas/` (tasks, events, run-status, profile, integrations), systemd units (`engineer-supervisor`, `chrome-xvfb`, `novnc`), `superpowers/` (bb92a77 minus two skills), project skeleton.
- `tests/` (`check.sh`, `check-mermaid.sh`, `test-fm.sh`, `rules/`, `supervisor/`, `broker/`, `parser/`, `fixtures/seeded-flaw/`), `.github/workflows/ci.yml`, `.claude/` (builder only), `docs/versions.md`.

VM layout: `/srv/engineer-template` (root clone), `~engineer/engineer-template` (builder checkout), `/opt/engineer/` (root-owned runtime copy), `/etc/claude-code/managed-settings.json`, `/var/lib/engineer/` (supervisor state dir, kill switch `STOP`). Users: `engineer` (sessions, every `claude -p`, `/login`), `supervisor` (service; sudo to `run-task` as engineer and `agent-run` as secretbroker), `secretbroker` (SOPS+age, jobs).

State files: VM state dir per project: `events.jsonl`, `RUN_STATUS.json`, `MORNING.md`, per-night counter, `trials/<id>/result.json`. Project repo: `decisions/approvals.jsonl`, `docs/plan/approval.json` + tag `plan-approved-N`, `docs/plan/tasks.json`, `PROGRESS.md`, `dead-ends.md`, `docs/plan/architecture.yaml`, `audit/AUDIT-<id>.md`, `audit/waivers.md`, `docs/runs/`.

Project skeleton: `CLAUDE.md` (<200 lines), `.env.example`, `docs/plan/` (brief, brief-after, requirements, architecture.yaml/.mmd, integrations.yaml, contracts/, tasks.json, approval.json, plan.approved.vN, changes/, profile.yaml), `docs/adr/`, `docs/map/`, `docs/DEPENDENTS.md`, `docs/setup.md`, `docs/runs/`, `tests/acceptance/`, `flows/<app>/<task>.spec.ts`, `security/`, `audit/`, `decisions/approvals.jsonl`, `dead-ends.md`, `PROGRESS.md`.

## 4. Questions before building

### (a) Already marked open for John, or a labelled default a spike or the builder settles (fine)
- Path A or B for `claude -p` (README.md:49; open-questions.md:10; SP01, SP02).
- 1Password or SOPS+age (open-questions.md:11).
- R16 route; whether branch protection exists on his private-repo plan at step 20 is spike-first (open-questions.md:12; setup.md:47; SP18).
- Extra hard gates, promote automation, health-data processors, Moderate changes, lockfile self-merge, threat model, cross-family key, dark or light (open-questions.md:13-21).
- One or two Telegram bots (open-questions.md:22; setup.md:49; SP16).
- VM host and whether it is shared with the health VM (open-questions.md:16).
- GTM facts: where GTM config lives, Clay plan, n8n hosting and API, Outreach employer policy, Attio keys and merge route, health VM state (open-questions.md:27-33; gtm-scenario.md GAP steps 3, 5, 16, 23, 26).
- Supervisor OS user is a labelled builder default (open-questions.md:40).
- Whether managed settings accept hook entries, with a named fallback (open-questions.md:51; repo-composition.md:102; SP10).
- Vendor MCP URLs and auth, Clay CLI package name (open-questions.md:52; stack.md:82; repo-composition.md:124).
- Run defaults, schemas, VM size, egress mechanism, kill-switch path, template repo name, budgets (flow.md:8-20; repo-composition.md:97, 126-132; stack.md:61, 88; open-questions.md:48).
- Stop hook exit 2 vs JSON (open-questions.md:49; SP06); trial auth and `--bare` (SP03); dead-man SMS vs Telegram/email (decisions.md:35; SP72).
- Backlog import for adopted repos (open-questions.md:42).

### (b) Real gaps that would stop or mislead a builder
1. **Auditor launch path and write rights contradict.** The auditor agent "writes only `audit/AUDIT-<id>.md`" (repo-composition.md:67, 94), but the PreToolUse hook denies writes to `audit/` for every session (repo-composition.md:76; flow.md:61 F23), and the only launch path, `run-task`, takes a task id and execs the implementer's `claude -p` (repo-composition.md:112). Nothing says which user, wrapper and flags start the auditor, plan-reviewer or mapper sessions, or how the hook tells an auditor from an implementer. F25 (flow.md:63) cannot be built as written.
2. **How unattended runs load the plugin and Superpowers is unstated, and the files disagree on how Superpowers arrives.** `.claude/` is "used only by the builder session, never by unattended runs" (repo-composition.md:39-40), and the plugin copy at `/opt/engineer/plugin/` is installed only as the fallback if managed hooks fail (repo-composition.md:102). No file says how a project's `claude -p` gets the `plan`, `digest` and `security-review` skills, the `implementer` and `auditor` agents, or Superpowers. Superpowers is "installed by bootstrap" (decisions.md:103; repo-composition.md:165), "vendored as plain files" in the template (repo-composition.md:30-31, 174), and a "plugin copy" under `/opt/engineer/` (stack.md:74). Bootstrap installs are writable by `engineer`, which matters for the guard design.
3. **OAuth consent has no token-capture mechanism or redirect route.** Steps 15-17 and 30 (setup.md:42-44, 57) need authorization-code flows whose refresh tokens end up in SOPS (stack.md:98). The broker job list (repo-composition.md:110) has no OAuth callback or exchange job, no redirect URI is named for the Google, Outreach, WHOOP, Withings or Slack apps, and the only public ingress (the Cloudflare tunnel) is set up after the sitting, at step 37 (setup.md:68). John cannot type a refresh token into `seed`.
4. **Broker-run CLIs live where the model can edit them, and the Clay session's location contradicts.** Broker jobs deploy and call APIs with secrets (engineer-runtime.mmd:23; stack.md:107 pipes secrets to `wrangler secret put`), but wrangler and the Clay CLI are installed by `bootstrap.sh` into the `engineer` user's npm prefix (stack.md:79, 82). If `secretbroker` runs those binaries, `engineer` can replace them and read every secret, which defeats ruling 6. The Clay CLI session is listed as living in SOPS, readable only by `secretbroker` (stack.md:98), yet step 27 does "Clay CLI first sign-in" with the CLI installed for `engineer` (setup.md:54), so the CLI's own session store sits with `engineer`. Nothing says which user runs which CLI.
5. **Step 31 browser logins lack two preconditions.** Chrome runs as the `engineer` UID, whose traffic nftables forces through the mitmproxy allowlist (stack.md:88). Both lists name only API hosts: "the API hosts of Attio, Clay, ... Google" (stack.md:89-90). Neither covers the web-app and login hosts that browser-only work needs (Attio and Clay app UIs, Google sign-in, OAuth consent pages). Also, the `chrome-xvfb` and `novnc` units are "installed but not enabled" until `--lock` at step 34 (setup.md:9), yet noVNC must be up at step 13 (setup.md:35) and step 31 (setup.md:58). No file says who starts them before the lock.
6. **The template repo starts empty, but the build assumes "existing" parts and the findings.** Step 1 creates a new private repo (setup.md:14). Step 2 writes the tree in a cloud session on that repo (setup.md:15). That tree marks skills, agents, `.mcp.json`, `tests/check.sh`, `check-mermaid.sh`, `rules/` and `plugin/evals/` as "existing, changed" (repo-composition.md:11-17, 33, 36), and every decision cites `research/findings/engineer-*.md` (README.md:5-7). No step copies or forks the research repo into `engineer-template`, or gives the builder session access to it and its findings, so a stranger cannot tell where the "existing" files come from.
7. **The supervisor's container and worktree rights are missing from the enforcement table.** The supervisor "launches and tears down" trial containers and writes `result.json` (engineer-runtime.mmd:20; flow.md:49 F17), and it creates the per-task worktrees the `engineer` user writes in (flow.md:60 F22). The users and sudoers table gives `supervisor` only `run-task` and `agent-run` (repo-composition.md:106-110). No file says who owns the Docker socket or rootless Podman, or who owns the worktrees and project clones on the VM. Docker group membership is root-equivalent, so the builder needs a stated rule.
8. **The "8-file plan set" is never listed, and the signed files do not map to the skeleton.** The `plan` skill builds an "8-file plan set" (repo-composition.md:55). John signs "brief, acceptance, integrations and costs, gates" (decisions.md:68; flow.md:52), and `approval.json` hashes each signed file. The skeleton (repo-composition.md:138-141) has no acceptance file or costs file, and lists more than eight entries. So the approval-hash hook (F19-F20, flow.md:54-55; SP17) has no defined file list to hash.

Noted but not counted (a builder can decide and record): `seed` is both a standalone command John runs (setup.md:39) and an `agent-run` job that `engineer` may call (repo-composition.md:110), which would let the model overwrite secrets. When a "night" starts and when the daily digest goes out are not stated. Where project repos are cloned on the VM is not stated.

## 5. Verdict
**FAIL: 8 gaps in 4(b).**
