# Stranger test

Purpose: check whether someone with no prior context could start building the autonomous engineer tomorrow from this blueprint alone.

Date: 2026-10-16. Read: `README.md`, `decisions.md`, `stack.md`, `setup.md`, `repo-composition.md`, `flow.md`, `gtm-scenario.md`, `spikes.md`, `requirements-trace.md` and `open-questions.md` in this folder, plus `docs/diagrams/engineer-{context,runtime,project-flow,approvals}.mmd`. Nothing else was read, and nothing was run or looked up. Line references are `file:line`.

## 1. The exact tools

### On John's VM (Ubuntu 24.04, a VPS or a home box, size not fixed)
| Tool | Version or plan given | Runs where |
| --- | --- | --- |
| Claude Code CLI, interactive, `/login` with Max | Version "pinned", value not given; Max tier and price not given | VM, `engineer` user |
| Claude Code `claude -p` per task (`--max-turns`, `--max-budget-usd`, `--permission-mode auto --permission-prompts none`) | Path A Max or Path B Console key, still undecided | VM, started by the supervisor |
| Supervisor (built for this project: DAG, bounds, breaker, events, digest, reply parser, reset parser, reconcile) | none | VM, systemd unit (`Restart=on-failure`); OS user still open (open-questions:101) |
| Managed settings `/etc/claude-code/managed-settings.json` | none | VM, owned by root |
| Bash sandbox (bubblewrap) plus an AppArmor profile | none | VM |
| Docker or rootless Podman; host proxy (Envoy, mitmproxy or Squid, not chosen) | none | VM |
| SOPS + age; `secretbroker` user; `agent-run` job runner | none | VM |
| 1Password `op` (only if John already has it) | price not opened | VM |
| Node, Playwright, `@playwright/cli` skill, Playwright MCP, Playwright Test Agents | Node and Playwright "pinned", values not given | VM |
| Headed Chrome (`--user-data-dir`), Xvfb, a window manager, x11vnc on localhost, noVNC | none | VM; noVNC on a "private network" |
| Superpowers | 7.0.0, commit `bb92a77` | Plugin, installed by bootstrap |
| research-agent plugin (skills, agents, hooks), changed as in repo-composition.md | none | VM, template repo |
| mermaid-lint, mermaid-cli | pinned, no value | VM, CI |
| Semgrep CE, Bandit or Ruff `S`, OSV-Scanner, pip-audit, `npm audit`, gitleaks `--redact`, Checkov, Lynis | pinned by checksum, no values | VM, CI |
| ZAP baseline | none | CI, against own staging |
| `gh`, git worktrees (`claude --worktree`) | none | VM |
| backcheck | spike first (SP20) | VM |
| n8nmermaid, docker-compose-to-mermaid, dependency-cruiser, pydeps | none | VM |
| wrangler, `gcloud` (implied by `gcloud run deploy`), Docker Compose, systemd timers | none | VM |
| Gradle, Capacitor, adb (optional) | none | VM |
| pyotp TOTP wrapper (if no 1Password) | none | VM |
| Clay CLI or plugin | Clay plan unknown; tables need Enterprise | VM |
| n8n self-hosted Community | free; whether John self-hosts is open | VM per stack.md, but open per open-questions:86 |
| MCP in `.mcp.json`: Playwright, DeepWiki, Firecrawl, each pinned by a `tools/list` hash | none | VM, stdio |
| Attio MCP (reads), n8n instance MCP (2.13+), Outreach MCP, Vercel MCP (read-only) | n8n 2.13+ | Not stated |
| `openai/codex-plugin-cc` (off) | GPT-6.1 Sol, $2/$10 per 1M | VM, only after SP34 |

### SaaS and accounts to sign up for or configure
| Service | Plan or price given | Used for |
| --- | --- | --- |
| Anthropic Claude Max (Path A) or Console API key (Path B) | Max price not opened; per-token prices not verified | The engine |
| Telegram Bot API (@BotFather), supervisor bot; possibly a second bot for Channels | Free | Digest, T2 prompts, replies |
| Channels (Telegram plugin), research preview | Free | Daytime live prompts (VM and phone) |
| Remote Control on John's phone | In the plan | Phone view of sessions |
| GitHub: hand-made machine account, fine-grained PAT, branch protection, CODEOWNERS; GitHub Pro maybe | Pro price unverified | Repos, PRs |
| Cloudflare Workers, D1, R2, Tunnel, Access | Free tiers; Tunnel price and seat count unverified | Web deploy, private access |
| Google Cloud Run + Workload Identity | Free tier, quote unverified | Container APIs |
| Neon Free or Supabase Free | 100 CU-hours, or 2 projects / 500 MB | Postgres |
| UptimeRobot Free or healthchecks.io Hobbyist | Free | Uptime and cron alerts |
| Twilio SMS (optional) or ntfy (alternative) | $0.0083 per segment; ntfy free | Dead-man alert |
| Socket free | 1,000 scans per month | Install-time malware check |
| OSV.dev, deps.dev, Scorecard API, official MCP Registry, Smithery | Free, keyless | Tool vetting |
| Attio, Clay, n8n, Outreach, Slack, Google OAuth app, WHOOP, Withings developer apps | John's plans | GTM and health integrations |
| Gemini 4 Argon (not in v1) | $2/$10 per 1M until 2026-11-30, then $4/$20 | Later only |

## 2. Setup steps in order
(J) means John does it by hand; (A) means automated; (J+A) means John starts it and the engineer finishes.

1. (J) Choose Path A or B and say whether he has 1Password, recorded as an ADR. Waits on SP01 (and SP02, per open-questions:67).
2. (J) Rent an Ubuntu 24.04 VPS or prepare a home box, and give the engineer SSH access.
3. (J runs a script) `setup-root.sh` as root: `engineer` and `secretbroker` users, managed settings, AppArmor profile, `agent-run` sudoers line, egress allowlist, Docker or Podman. Try it on a throwaway VM first (SP09, SP10).
4. (J) `/login` with Max in the interactive session.
5. (A) `scripts/bootstrap.sh`: pinned Claude Code, Node, Playwright, Xvfb, x11vnc, noVNC, Chrome unit, Superpowers, mermaid tools, scanners.
6. (A) Plugin and template changes; CI runs `claude plugin validate --strict`.
7. (A) Hooks: SessionStart, PreToolUse, PostToolUse, Stop/TaskCompleted.
8. (A) Supervisor and its systemd unit.
9. (A) Trial runner: container, proxy, `result.json`, teardown.
10. (A) Broker: SOPS, age key, job allowlist, seeding command.
11. (A) Reply parser and Telegram sender.
12. (A) Approval-hash hook and `approval.json` schema.
13. (A) Browser profile lock-down and browser PreToolUse hooks.
14. (A) Privacy settings.
15. (A) `dead-ends.md`, registry fields, vet-card and staleness scripts.
16. (J) Outreach API app and employer approval (long wait).
17. (J) Google app and OAuth client, moved to "In production" (long wait).
18. (J) WHOOP and Withings developer apps (long wait).
19. (J) Telegram bot through @BotFather, then `/start` from his phone.
20. (J) Remote Control push settings on his phone.
21. (J) GitHub machine account and fine-grained PAT.
22. (J) Path B only: Console API key.
23. (J) Parent credentials: Cloudflare, Vercel, Supabase.
24. (J) SaaS keys: Attio, n8n, Clay CLI sign-in.
25. (J) GCP roles for Workload Identity.
26. (J+A) Slack config token; the engineer creates the app from a manifest.
27. (J) Every consent click in one run.
28. (J) Browser logins through noVNC.
29. (J) TOTP seeds.
30. (J) Seed every value into SOPS from his own terminal.
31. (J) Data-privacy toggle on his account.
32. (J) Confirm the hard gates and the default project profile.
33. (A) "Verifies all" table.
34. (A) Access apps, uptime monitors, healthchecks.
35. (A) Branch protection, required checks, CODEOWNERS.
36. (A) Nightly n8n export.
37. (A, after step 1) Turn on unattended runs.
38. (J) Later: the R16 self-merge route and two weeks of shadow mode.
39. (J) Later: an OpenAI key for the cross-family reviewer.
40. (A) Later: the Android SDK and Gradle.

## 3. Repo composition

From memory: a template repo holding `plugin/` (skills, agents, hooks, `.mcp.json`), `scripts/` (setup-root, bootstrap, doctor, cloud-setup, then supervisor, trial, broker, snapshot and checks subfolders), `templates/` (managed settings, systemd units, project skeleton) and a pins file. The skills are seven existing ones (interview, research, tool-scan, repo-triage, spike, system-map, setup, all changed) and six new ones (as-is, plan, browser, deploy, security-review, digest). The agents are four existing ones (researcher, synthesizer, verifier, spike-worker) and seven new ones (mapper, merger, planner, implementer, plan-reviewer, auditor, triage-reader), with Haiku roles only after SP32. The hooks are SessionStart (startup, resume, compact), PreToolUse guards plus a kill switch, PostToolUse lint, the Stop/TaskCompleted gate, and StopFailure and Notification taps. VM state lives in a per-project state dir outside the worktrees: `events.jsonl`, `RUN_STATUS.json`, `MORNING.md`, the per-night counter and `trials/<id>/result.json`. Project-repo state is `docs/plan/` (`tasks.json`, `approval.json`, `profile.yaml`, `integrations.yaml`, `architecture.yaml`), `decisions/approvals.jsonl`, `audit/`, `PROGRESS.md` and `dead-ends.md`. Root-owned files are the managed settings and the kill switch.

Checked against repo-composition.md:8-29 and 59-105. It matches. I had missed `docs/versions.md` as the pin file, `scripts/snapshot/` naming five tools (attio, clay, n8n, outreach, slack), and the project skeleton's `docs/map/`, `docs/DEPENDENTS.md`, `flows/<app>/<task>.spec.ts`, `security/`, `tests/acceptance/` and the optional `model-routing.json` and `reviews/`.

## 4. Questions before building

### (a) Already marked open for John (fine)
- Path A or B, and the Agent SDK terms question (README:49; open-questions:67).
- 1Password or not (README:50; open-questions:68).
- The R16 route (README:51; open-questions:69), lockfile self-merge (open-questions:75), and whether John can approve the bot's PR (open-questions:101).
- Gates beyond the three, auto-promote, Moderate changes, the threat model and health retention (open-questions:70-76).
- Health data to non-Anthropic endpoints (open-questions:72) and the OpenAI or Argon spend (open-questions:77).
- VPS or home box, and whether to share the health VM (README:53; open-questions:73).
- Dark or light (open-questions:78) and one Telegram bot or two (open-questions:79).
- GTM facts: where the configuration lives, his Clay plan, n8n hosting, his Outreach employer, Attio keys, the merge route, whether the health VM exists (open-questions:84-90). The GTM GAP steps are flagged in gtm-scenario.md:12, 14, 37, 48 and 55.
- Time budget for the build (open-questions:107).
- Design points with a default and a settling spike: the Path B key exposure, where the `/login` store lives, the supervisor's OS user, re-login frequency, backlog import, Routines, Smithery, the Semgrep licence, all numeric budgets, and Stop-hook exit 2 (open-questions:95-106).

### (b) Real gaps
1. **Bring-up order cannot run as written.** Phase 0 is "before any spike" (setup.md:7), yet row 1 needs SP01 (setup.md:10), and open-questions:67 also waits on SP02, which needs the VM and `/login` from steps 2 and 4 (spikes.md:11). Row 3 needs SP09 and SP10 on a throwaway VM (setup.md:12). Steps 2-4 run `setup-root.sh` and `doctor.sh` (setup.md:11-13), but nothing in this folder has been built yet (repo-composition.md:5), and no step writes those scripts or clones the template onto the VM. Phase 1 says "Automated" (setup.md:15-28) without naming who builds it: which session, under which login.
2. **Phase 2 checks run before their inputs exist.** Several checks need values that are seeded only at step 30 (setup.md:48): the test digest in step 19 (setup.md:37; the token lives in SOPS per stack.md:67), the PR and refused push in step 21 (setup.md:39), the child-token mint in step 23 (setup.md:41), the read calls in step 24 (setup.md:42) and the broker jobs in step 27 (setup.md:45). Step 21's "bot push to main refused" also needs the branch protection that only arrives at step 35 (setup.md:57).
3. **There is no defined way for John to reach noVNC.** Step 28 uses noVNC "on the private network" (setup.md:46; repo-composition.md:112), but no step creates that network. Cloudflare Tunnel and Access come only at step 34 (setup.md:56). `cloudflared` is never installed, and no step gives John a Cloudflare account or domain for Access (stack.md:49).
4. **The install list and pins are incomplete.** Neither bootstrap (setup.md:18) nor setup-root (setup.md:12) installs `gh`, sops, age, wrangler, `gcloud`, `cloudflared`, Docker Compose, Clay CLI, pyotp or n8n, all of which stack.md:17, 29, 48-55 and 71 rely on. No version is given for Claude Code, Node, Playwright or mermaid-cli (the pin file `docs/versions.md`, repo-composition.md:28, does not exist yet). The egress allowlist hosts are never listed (setup.md:12).
5. **Some tools are named with no install step or location.** The Channels Telegram plugin (stack.md:20) is never installed, and its second bot (the default per open-questions:79) is never created; step 19 creates only the supervisor bot (setup.md:37). The Attio, n8n instance, Outreach and Vercel MCP servers (repo-composition.md:110) have no config file, transport or install step.
6. **The template tree omits files that setup uses.** Step 6 runs `tests/check.sh`, `tests/check-mermaid.sh` and a CI job (setup.md:19), but the tree at repo-composition.md:8-29 has no `tests/`, no CI workflow and no `.claude/` wiring. The kill-switch file has no path (repo-composition.md:84).
7. **The enforcement layer has no stated owner.** decisions.md:87 calls for "external checks the engineer cannot rewrite", but the hooks live in `plugin/hooks/` in the engineer's own template (repo-composition.md:14). Root ownership or managed-only hooks are never stated, and stack.md:72 notes that deny rules are not a boundary. Superpowers is installed pinned (setup.md:18), yet its TDD iron law, local merge and finishing menu are "dropped" (repo-composition.md:117) with no mechanism given to switch them off.
8. **Numbers, schemas and pass thresholds are missing.** F29's "N denials" (flow.md:52) has no value. F22's `--max-turns`, `--max-budget-usd` and wall-clock values (flow.md:45) are not in the numeric-budget list either (open-questions:105). There are no schemas for `tasks.json` beyond `status` and `passes`, `events.jsonl`, `RUN_STATUS.json`, `profile.yaml` or `integrations.yaml` (repo-composition.md:71-80). There is no minimum VM size (stack.md:13), so "doctor.sh reports OS and RAM" (setup.md:11) has nothing to pass against. "Low `cleanupPeriodDays`" has no value (setup.md:27).
9. **Some files contradict each other, and some terms are undefined.** stack.md:53 puts n8n self-hosted on the VM, while open-questions:86 and gtm-scenario.md:43 say the hosting is unknown. engineer-project-flow.mmd numbers its steps 5-7 differently from flow.md's stages 5-7. It also omits stages 0, 6, 7 and 11, and says audit "passes merged work" (line 22) although merging is off by default (decisions.md:12). These terms are never defined: "D0-D2" (repo-composition.md:35), "capability-card" (repo-composition.md:36), "ledger" (repo-composition.md:117), "`ROW:`" (requirements-trace.md:135), "pass^3" (spikes.md:46) and "`setup-token`" (spikes.md:11).

## 5. Verdict
**FAIL: 9 gaps** in section 4(b).
