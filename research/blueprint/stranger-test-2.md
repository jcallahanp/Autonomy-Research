# Stranger test 2

Date: 2026-10-16. Reader: a builder with no prior knowledge of the project.
Read: every file in `research/blueprint/` except `digests/`, `hand-check.md`, `verification.md`
and `stranger-test.md`, plus `docs/diagrams/engineer-{approvals,context,project-flow,runtime}.mmd`.
No other file was opened and no web lookup was made. References are `file:line`.

## 1. Exact tools

### On the VM (Ubuntu 24.04; default size 4 vCPU, 8 GB RAM, 80 GB disk, stack.md:60)
| Tool | Version or plan | Runs where / as | Installed by |
| --- | --- | --- | --- |
| Claude Code CLI (interactive `/login` Max; `claude -p` per task) | at least 2.1.234, exact pin in `docs/versions.md` | VM, `engineer` user | bootstrap.sh (stack.md:69) |
| Users `engineer`, `secretbroker`, `supervisor`; AppArmor bubblewrap profile; managed settings; sudoers; egress allowlist | n/a | VM, root-owned | setup-root.sh (stack.md:66) |
| Bash sandbox (bubblewrap) | `allowUnsandboxedCommands: false` | VM | setup-root.sh / step 7 |
| Docker Engine + Compose plugin, or rootless Podman | distro or vendor apt | VM | setup-root.sh (stack.md:67) |
| Host proxy: Envoy, mitmproxy or Squid | not chosen | VM, for trial containers | not in install list (stack.md:16) |
| sops, age | release binaries, checksum-verified | VM, `secretbroker` | setup-root.sh (stack.md:68) |
| Node.js | 22 LTS or later | VM | bootstrap.sh (stack.md:70) |
| Playwright, browsers, `@playwright/cli`, Playwright MCP, Test Agents | recorded pin | VM | bootstrap.sh (stack.md:71) |
| Google Chrome, Xvfb, a window manager, x11vnc, noVNC + websockify | distro packages | VM; noVNC on 127.0.0.1:6080 | bootstrap.sh (stack.md:72) |
| Superpowers | commit `bb92a77` (label 7.0.0 unverified), vendored minus TDD and finishing skills | VM, plugin / `templates/superpowers/` | bootstrap.sh (stack.md:73) |
| mermaid-lint, mermaid-cli | mermaid-cli 11.12.0 | VM, CI | bootstrap.sh (stack.md:74) |
| `gh` | GitHub apt repo | VM | bootstrap.sh |
| wrangler | recorded pin (npm) | VM | bootstrap.sh |
| `gcloud` | Google apt repo | VM | bootstrap.sh |
| `cloudflared` | Cloudflare apt repo | VM | bootstrap.sh |
| Clay CLI | package name open (SP65) | VM | bootstrap.sh |
| pyotp (only without 1Password) | recorded pin, venv owned by `secretbroker` | VM | bootstrap.sh |
| 1Password `op` (only if John has it) | 1Password apt repo | VM | bootstrap.sh |
| Semgrep CE, Bandit or Ruff `S`, OSV-Scanner, pip-audit, gitleaks `--redact`, Checkov, Lynis, `npm audit` | version plus checksum | VM, CI | bootstrap.sh (stack.md:82) |
| n8nmermaid, docker-compose-to-mermaid, dependency-cruiser, pydeps | recorded pin | VM | bootstrap.sh |
| Channels Telegram plugin | recorded pin, Anthropic marketplace | VM, `engineer`, daytime tmux session | bootstrap.sh (stack.md:84) |
| backcheck | after a spike; no version | VM | not in install list (stack.md:28) |
| lychee, Schemathesis, Atlas | where they apply | CI | not in install list (stack.md:47) |
| Supervisor, broker (`agent-run`, `seed`), trial runner, audit.sh, checks | own build | VM, `supervisor` / `secretbroker` | template repo |
| Docker Compose, systemd timers and units (supervisor, chrome-xvfb, novnc) | n/a | VM | step 9, 12 |
| Android SDK, Gradle, adb, Capacitor | recorded pin, optional | VM | `bootstrap.sh --with-android` |
| n8n | only if John moves it to the VM | VM | open (open-questions 16) |

### MCP servers
| Server | Where configured | Runs where |
| --- | --- | --- |
| Playwright, DeepWiki, Firecrawl | `plugin/.mcp.json`, pinned with `tools/list` hash | VM (stdio / HTTP) |
| Attio MCP (reads only) | user scope on VM | hosted by Attio |
| n8n instance MCP | user scope | John's n8n 2.13+ instance |
| Outreach MCP | user scope, once app exists | not stated |
| Vercel MCP (read-only, if Vercel used) | user scope | OAuth remote |
| claude.ai connectors: Exa, Parallel Search, Context7, Mermaid Chart | claude.ai account | interactive `/login` sessions only |

### Services and accounts
| Service | Plan or cost | Where |
| --- | --- | --- |
| Claude Max (John's) | price not opened | Anthropic |
| Anthropic Console API key | Path B only, per token | Anthropic |
| VPS or home box | "$5/mo VPS is fine"; 4 vCPU/8 GB price unverified | John's choice |
| Telegram Bot API: supervisor bot + Channels bot | free | SaaS + VM |
| Remote Control, Claude artifacts | in plan | John's phone; interactive session |
| GitHub: machine account (hand-registered), fine-grained PAT; Pro optional for R16 | free; Pro price unverified | GitHub |
| Socket free, Dependabot | $0, 1,000 scans/month | GitHub app |
| Cloudflare: Workers, D1, R2, Tunnel, Access, domain | Free tiers; Access seat count and Tunnel price unverified | SaaS |
| Google Cloud: OAuth client, Cloud Run, Workload Identity | free tier, quote unverified | GCP |
| Neon Free or Supabase Free | free | SaaS |
| Vercel (optional) | not stated | SaaS |
| UptimeRobot Free / healthchecks.io Hobbyist | free | SaaS |
| Twilio SMS (optional) or ntfy | $0.0083/segment; ntfy free | SaaS |
| Attio, Clay, n8n (Cloud or self-hosted), Outreach, Slack | John's plans; Clay tables Enterprise only | SaaS |
| WHOOP, Withings developer apps | Withings+ need open | SaaS |
| OSV.dev, deps.dev, Scorecard API, official MCP Registry | keyless | curl |
| OpenAI key (`codex-plugin-cc`), Gemini 4 Argon | off in v1 | SaaS |
| Claude in Chrome | attended setup only | John's computer |

## 2. Setup steps in order (setup.md). J = John by hand
Phase A, builder in a claude.ai/code cloud session, no VM:
1. Write the template repo per repo-composition.md and stack.md; CI green (`claude plugin validate --strict`, `tests/check.sh`, `tests/check-mermaid.sh`).
2. SP01: re-read Agent SDK billing and legal pages; write the Path A/B page.

Phase B, John:
3. **J** Rent or prepare the Ubuntu 24.04 machine, add SSH key.
4. **J** `git clone` the template; `sudo bash scripts/setup-root.sh`. Check: `sudo -l` as `engineer` lists only `agent-run`.
5. **J** As `engineer`: `tmux new -s builder`, `claude`, `/login` (Max); start the builder session.

Phase C, builder on the VM:
6. `scripts/bootstrap.sh` (SP22, SP23).
7. Sandbox, managed settings, hooks in `/opt/engineer/hooks/` (SP06, SP09, SP10, SP13).
8. Broker: SOPS files, age key, `agent-run` allowlist, `seed <NAME>` (SP11, SP12).
9. Supervisor and systemd unit, run defaults, `autoContinueAtUsageLimit` (SP04, SP05, SP07, SP08).
10. Trial runner with host proxy (SP03, SP26, SP27, SP28).
11. Approval-hash hook, reply parser (SP17, SP15).
12. Browser profile, noVNC on localhost, browser hooks (SP64).
13. Privacy settings, `dead-ends.md`, registry fields, vet card, Channels plugin (SP53, SP54).
14. SP02, then **J** chooses Path A or B and says whether he has 1Password; ADR committed.

Phase D, John's one sitting (each credential: John creates it, runs `sudo -u secretbroker seed <NAME>`, builder checks at once):
15. **J** Outreach API app, production credentials, employer approval.
16. **J** Google app and OAuth client, consent screen to production.
17. **J** WHOOP and Withings developer apps.
18. **J** Two Telegram bots, `/start`, seed tokens, pair Channels allowlist.
19. **J** Remote Control push on phone.
20. **J** Cloudflare account, domain, parent token.
21. **J** GitHub machine account, fine-grained PAT.
22. **J** Path B only: Console API key.
23. **J** Vercel / Supabase tokens if used.
24. **J** Attio key, n8n key with expiry, Clay CLI sign-in.
25. **J** GCP roles for Workload Identity; builder binds the OIDC subject.
26. **J** Slack config token; builder creates the app from a manifest.
27. **J** All consent clicks: Slack, Google, Outreach, WHOOP, Withings.
28. **J** Browser logins through `ssh -L 6080:127.0.0.1:6080` and noVNC.
29. **J** TOTP seeds.
30. **J** Data-privacy toggle; confirm hard gates and default `profile.yaml`.

Phase E, builder:
31. Branch protection, required checks, CODEOWNERS; bot push to main and force push refused (SP18).
32. "Verifies all" table through broker jobs.
33. `cloudflared` tunnel and Access app; uptime monitors and healthchecks.
34. n8n nightly export to git (SP66).
35. Daytime Channels session in tmux.
36. Enable unattended runs (after step 14 and spikes section A).

Later, each needing John:
37. **J** R16 self-merge route plus two weeks of shadow mode.
38. **J** OpenAI key for the cross-family reviewer.
39. Android toolchain via `bootstrap.sh --with-android`.

## 3. How the repo is composed (repo-composition.md)
- **Template repo:** `plugin/` (skills, agents, hooks source, scripts, `.mcp.json`, `evals/`);
  `scripts/` (`setup-root.sh`, `bootstrap.sh`, `doctor.sh`, `cloud-setup.sh`, and folders `supervisor/`, `trial/`,
  `broker/`, `snapshot/`, `checks/`); `templates/` (managed settings, egress allowlist, systemd units,
  vendored Superpowers, project skeleton); `tests/` (check scripts, unit tests, seeded-flaw fixtures);
  `.github/workflows/ci.yml`; `.claude/` (builder only); `docs/versions.md`.
- **Skills:** changed: interview, research, tool-scan, repo-triage, spike, system-map, setup. New: as-is, plan,
  browser, deploy, security-review, digest.
- **Agents:** existing: researcher, synthesizer, verifier, spike-worker. New: planner, implementer,
  plan-reviewer, auditor, mapper, merger, triage-reader; Haiku roles only after SP32.
- **Hooks:** SessionStart (`startup|resume|compact`), PreToolUse (protected-path deny, approval hash, deploy
  allowlist, browser classifier, kill switch, dead-end reminder), PostToolUse (lint, mermaid-lint), Stop /
  TaskCompleted (evidence gate), StopFailure and Notification (event taps). Source in `plugin/hooks/`,
  installed root-owned in `/opt/engineer/hooks/`.
- **Scripts:** supervisor loop and its parts, trial runner, broker jobs, snapshot exporters, checks.
- **State files:** VM state dir: `events.jsonl`, `RUN_STATUS.json`, `MORNING.md`, per-night counter,
  `trials/<id>/result.json`, kill switch `/var/lib/engineer/STOP`. Project repo: `docs/plan/` (`tasks.json`,
  `approval.json`, `profile.yaml`, `integrations.yaml`, `architecture.yaml`, ...), `decisions/approvals.jsonl`,
  `PROGRESS.md`, `dead-ends.md`, `audit/`, `security/`, `docs/adr/`, `docs/runs/`. Root: `/etc/claude-code/managed-settings.json`.
- **Project skeleton:** repo-composition.md:123-142.

## 4. Questions before I could build

### (a) Already marked open for John, or a labelled default a spike or the builder settles (fine)
- Path A or B for `claude -p` (README.md:49; decisions.md:11; open-questions.md:10).
- 1Password or SOPS+age (open-questions.md:11); R16 route (open-questions.md:12); VPS vs home box and shared health VM (open-questions.md:16).
- One or two Telegram bots (open-questions.md:22; SP16).
- n8n hosting and API availability (open-questions.md:29; stack.md:53, 85).
- Clay CLI package name and vendor MCP URLs and auth (stack.md:79; repo-composition.md:112; open-questions.md:52).
- Whether managed settings accept hook entries; fallback root-owned plugin copy (repo-composition.md:99; open-questions.md:51; SP10).
- Third `supervisor` OS user (open-questions.md:40).
- Every version pin: builder picks current stable and records it (stack.md:63; SP22).
- VM size, egress host list, run defaults, schemas, kill-switch path, all numeric budgets (stack.md:60, 89; flow.md:8-20; repo-composition.md:94, 114-120; open-questions.md:48).
- Stop-hook exit 2 vs JSON (open-questions.md:49); `/login` credential location and readability (open-questions.md:39); Path B key exposure (open-questions.md:38).
- Host proxy product (Envoy, mitmproxy or Squid, stack.md:16) and Docker vs rootless Podman (stack.md:67): options left to the builder, tested by SP26.
- State-dir path (repo-composition.md:81): location by inference, path left to the builder under the "builder decides" schema rule (repo-composition.md:115).
- GTM GAP steps 3, 5, 16, 23, 26 (gtm-scenario.md:12, 14, 37, 48, 55) and the open time budget (open-questions.md:50).

### (b) Real gaps
1. **Root work assigned to an unprivileged builder.** From step 6 the builder runs as `engineer`, and step 4 checks
   that `engineer` may sudo only `agent-run` (setup.md:7, 19). Yet bootstrap.sh adds apt repos and distro packages
   (stack.md:72-81), step 7 writes root-owned `/opt/engineer/hooks/` and managed settings, and its own check says
   `engineer` cannot write there (setup.md:26). Step 8 creates `secretbroker` files (setup.md:27), and steps 9 and 12
   install systemd units (setup.md:28, 31). No step says who runs these as root, for example John re-running
   setup-root.sh, or how.
2. **The builder is bound by the guards it is building.** Managed settings apply to every session.
   The PreToolUse hook denies writes to tests, CI, hooks and `.claude/`, and refuses code edits without a matching
   approval hash (repo-composition.md:73, 98-99). From step 7 the builder must still edit the template's
   tests, CI and hooks (setup.md:7, 26-32). No exemption or builder mode is defined. Repo-composition.md:37 says
   `.claude/` is "used only by the builder session", but that does not exempt it from managed settings.
3. **Git plumbing for the template repo is missing.** Phase A needs a GitHub repo that a claude.ai/code session can
   open, and step 4 clones it on the VM (setup.md:8, 12, 19). No step creates or hosts it, sets its visibility
   or gives the VM read access before step 21. Also, `engineer` has no push credential
   (repo-composition.md:102), so nothing says how the builder's Phase C-E commits reach the template repo:
   `docs/versions.md` pins, the step 14 ADR and script fixes.
4. **The supervisor user's privileges are unspecified.** The supervisor runs as `supervisor` and starts `claude -p` as
   `engineer`, which under Path A uses `engineer`'s `/login` (engineer-runtime.mmd:4-5, 17; repo-composition.md:100).
   It reads its Telegram token "through the broker" (stack.md:99). Only `engineer`'s `agent-run` sudoers line is
   specified (setup.md:19), so the cross-user launch and the supervisor's path to the broker are undefined.
5. **The egress allowlist would block bootstrap.** setup-root.sh applies the allowlist at step 4 (setup.md:19).
   The default list (stack.md:89) lacks hosts bootstrap needs at step 6: the Ubuntu archive, the Docker, Google,
   Cloudflare and 1Password apt repos, Node and the Playwright browser download. No mechanism enforces the list
   (firewall, proxy or sandbox network setting). "Adds a host only after a logged denial" needs root, which
   ties back to gap 1.
6. **Step 31 needs admin rights nobody has.** The builder sets branch protection, required checks and CODEOWNERS
   (setup.md:59). The only GitHub credential is the bot PAT with Contents, Pull requests and Metadata, and the
   account is "write not admin" (setup.md:45; stack.md:98). Branch protection needs repo admin, so either John
   does it or an admin token is needed. Neither is stated.
7. **Alerting accounts and the dead-man route are never set up.** Step 33 has the builder create UptimeRobot and
   healthchecks.io monitors (setup.md:61; stack.md:24), and step 9 has an `ExecStopPost` ping (setup.md:28). Phase D
   has no sign-up row for these services, and browser-driven account creation is rejected (decisions.md:54).
   The approvals diagram and ruling 3 make SMS the dead-man alert (engineer-approvals.mmd:24; decisions.md:13),
   but Twilio and ntfy are optional (stack.md:22-23) and no setup step configures either. So the target of the
   "supervisor died" ping is undefined.
8. **No source for Superpowers.** Only commit `bb92a77` and a path in another local repo
   (`/home/user/attio-project/.claude/skills/`) are given (stack.md:25, 73; repo-composition.md:28, 162). The
   Phase A cloud builder cannot read that path, and the blueprint never names the upstream repository. backcheck
   (stack.md:28) likewise has no link.
9. **Files and terms are referenced but not defined.**
   - `templates/run-defaults.yaml` (flow.md:8) and `templates/schemas/` (repo-composition.md:115) are not in the
     template tree (repo-composition.md:26-28).
   - setup.md:12 puts hooks under `templates/`, while repo-composition.md:14 puts them in `plugin/hooks/`.
   - The "Verifies all" table of step 32 (setup.md:60) appears in no blueprint file.

## 5. Verdict
**FAIL: 9 real gaps (section 4(b)).** The tools, the phase order and the repo layout are clear enough to start
Phase A. Phases C-E cannot run as written, because the blueprint never says who holds root, how the builder
bypasses its own guards, or how its work reaches GitHub.
