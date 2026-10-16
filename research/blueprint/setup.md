# Setup

Purpose: the order in which the engineer itself gets set up, who does each step, how it is verified and which spike (spikes.md) must pass first.

This is the engineer's own setup. Each project later gets its own ordered setup list from the feasibility hand-off (engineer-feasibility D52; flow.md stage 4). Every John step carries a plain-language line on the setup page; values never pass through chat (engineer-human-loop §Q3).

## Phase 0: bring-up (John, short, before any spike)
| # | Step | Who | Verified by | Spike first |
| --- | --- | --- | --- | --- |
| 1 | Read the Path A/B page (decisions.md ruling 1) and say A or B; say whether he has 1Password | John (decision) | Answer recorded as an ADR in `docs/adr/` | SP01 |
| 2 | Rent a small Ubuntu 24.04 VPS or prepare a home box; give the engineer SSH access (engineer-runtime setup 1) | John | `doctor.sh` reports OS and RAM | none |
| 3 | Run one command as root: `setup-root.sh` creates `engineer` and `secretbroker` users, root-owned managed settings, AppArmor bubblewrap profile, `agent-run` sudoers line, egress allowlist, Docker or rootless Podman (engineer-human-loop setup 1; engineer-feasibility setup 2-3) | Automated script, run by John | `sudo -l`, sandbox up, managed file honoured | SP09, SP10 (run on a throwaway VM first) |
| 4 | `/login` with the Max account in the interactive session; on a headless box, OAuth from a machine with a browser (engineer-runtime setup 4) | John | `doctor.sh`: no `ANTHROPIC_API_KEY` in the interactive environment (engineer-runtime S15) | none |

## Phase 1: automated build and core spikes (no John)
| # | Step | Who | Verified by | Spike first |
| --- | --- | --- | --- | --- |
| 5 | Pinned `scripts/bootstrap.sh`: Claude Code version, Node, Playwright and browsers, Xvfb, window manager, x11vnc on localhost, noVNC, Chrome systemd unit, Superpowers pinned, mermaid-lint and mermaid-cli pinned, security scanners pinned by checksum (engineer-runtime P5, P17; engineer-browser setup 1; engineer-briefing setup 1; engineer-security setup 2) | Automated | `claude --version` matches pin; `/setup` probes tools; Chrome and display survive restart | SP22, SP23 |
| 6 | Plugin and template changes from repo-composition.md; `claude plugin validate --strict` in CI (engineer-runtime P40) | Automated | CI green; `tests/check.sh` and `tests/check-mermaid.sh` pass | none |
| 7 | Hooks: SessionStart (startup, resume, compact), PreToolUse guards and kill switch, PostToolUse lint, Stop/TaskCompleted gate (engineer-context setup 2, 4; engineer-protocol setup 4-5) | Automated | Hooks fire and block | SP06, SP13 |
| 8 | Supervisor with caps, breaker, `events.jsonl`, `RUN_STATUS.json` trap, reset parser, `--resume`, reconcile; systemd unit with `Restart=on-failure`, `ExecStartPre` reconcile, `ExecStopPost` ping; `autoContinueAtUsageLimit` on per ruling 5 (engineer-context setup 5; engineer-protocol setup 8) | Automated | Simulated stall, kill and limit each end in a known state | SP04, SP05, SP07, SP08 |
| 9 | Trial runner: per-trial container, host proxy with allowlist and injection, `result.json`, teardown, startup sweep (engineer-feasibility setup 4) | Automated | Tool that ignores `HTTP_PROXY` fails closed | SP03, SP26, SP27, SP28 |
| 10 | Broker: SOPS files, age key for `secretbroker`, `agent-run` job allowlist, seeding command that reads from John's terminal only | Automated | `engineer` reads no value | SP11, SP12 |
| 11 | Reply parser and Telegram sender (bot token added in step 19) | Automated | Junk never approves | SP15 |
| 12 | Approval-hash hook and `docs/plan/approval.json` schema | Automated | Edit blocked on mismatch | SP17 |
| 13 | Profile directory chmod 700, gitignored, Read denied; PreToolUse hooks on browser write tools with domain allowlist (engineer-browser setup 2, 9) | Automated | Hook fires on click and type | SP64 |
| 14 | Privacy settings: `DISABLE_FEEDBACK_COMMAND=1`, low `cleanupPeriodDays` (engineer-human-loop E84, E91) | Automated | Settings file check | none |
| 15 | `dead-ends.md`, registry Meta fields, vet-card and staleness scripts (engineer-tool-discovery setup 1-5) | Automated | Each vet call answers under 1 s | SP53, SP54 |

## Phase 2: John's one setup sitting (one contiguous block; long waits first)
The worker's unsourced estimate is about 45-90 minutes across 11 services (engineer-feasibility setup 12); spike SP75 times each row. The agent prefills every form it can and shows a "verifies all" table at the end.
| # | Step | Who | Verified by | Spike first |
| --- | --- | --- | --- | --- |
| 16 | **Long wait 1.** Outreach: create the API app, request production credentials, ask the employer for approval of app creation and UI automation (engineer-browser A41, A42; engineer-feasibility D25) | John | Development credentials work now; production on approval | SP67 is answered live here |
| 17 | **Long wait 2.** Google: create the app and OAuth client; move the consent screen to "In production" (engineer-human-loop E18; engineer-feasibility D12) | John | No 7-day Testing refresh token | SP70 |
| 18 | **Long wait 3.** WHOOP and Withings developer apps; check whether Withings+ is required (engineer-human-loop E23-E25; E37 unverified) | John | App IDs exist | SP73 (Withings+ part) |
| 19 | Telegram: create the supervisor bot with @BotFather; send `/start` from his phone so his `from.id` is allowlisted (engineer-human-loop E15, E16) | John | Test digest arrives; reply parsed | SP16 |
| 20 | Remote Control push settings on his phone (engineer-runtime C52) | John | Test push received | none |
| 21 | GitHub: register the machine account by hand (bots banned, engineer-human-loop E40) with write, not admin; fine-grained PAT for Contents, Pull requests, Metadata (engineer-protocol E80, E81) | John | Bot push to main refused; PR opens | SP18 |
| 22 | Path B only: Console API key (engineer-human-loop E26, E27) | John | Supervisor test run bills the key | SP01, SP02 |
| 23 | Parent credentials: Cloudflare token with Account API Tokens Edit; Vercel token if used; scoped Supabase PAT (engineer-human-loop E1, E4, E7) | John | Broker mints and uses a child | SP71 |
| 24 | SaaS keys: Attio key (a workspace admin for a workspace token, E22); n8n key with an expiry (E21, E33); Clay CLI first sign-in (engineer-browser A22) | John | One read call per tool | SP65, SP66 |
| 25 | GCP: grant the project roles for Workload Identity (engineer-deploy setup 3) | John | `gcloud run deploy --source .` from CI | SP72 |
| 26 | Slack config token (lasts 12 h, so late in the sitting); the agent creates the app from a manifest (engineer-human-loop E10, E11, E30) | John, then automated | App exists | SP68 |
| 27 | Every consent click in one run: Slack install, Google, Outreach, WHOOP, Withings (engineer-human-loop setup 5) | John | Broker job calls each API | none |
| 28 | Browser logins through noVNC on the private network: Google by hand first, then Attio, Clay, n8n, Outreach (engineer-browser setup 3-4; S11) | John | Per-site logged-in check | SP63 (lifetimes recorded, not gating) |
| 29 | TOTP seeds into 1Password or the local pyotp store (engineer-browser setup 5) | John | Wrapper returns only the code | SP63 (TOTP part) |
| 30 | Seed every value into SOPS with the broker command in his own terminal; production, billing and backup values stay out (engineer-human-loop setup 6) | John | Engineer sees names only; canary grep clean | SP11, SP12 |
| 31 | Data-privacy toggle on his account, 30 days vs 5 years (engineer-human-loop E85) | John | Toggle state recorded | none |
| 32 | Confirm the hard-gate list (money, deleting data, store submission) and the default project profile (ruling 9) | John | `profile.yaml` defaults committed | none |

## Phase 3: automated verification and switch-on
| # | Step | Who | Verified by | Spike first |
| --- | --- | --- | --- | --- |
| 33 | "Verifies all" table through broker jobs: pass or fail per credential, first failing row named (engineer-human-loop setup 8; engineer-feasibility setup 12) | Automated | All rows pass, or failing rows go to the digest | none |
| 34 | Access apps with a one-email policy by API; uptime monitors and healthchecks to the Telegram bot (engineer-deploy setup 2, 8) | Automated | John logs in from his phone; test alert arrives | SP71, SP72 |
| 35 | Branch protection, required checks, CODEOWNERS with "Do not allow bypassing" on each repo, as far as his plan allows (engineer-protocol setup 3) | Automated | Bot push to main refused | SP18 |
| 36 | Nightly n8n workflow export to git, before any n8n edit (engineer-deploy §Implications 8) | Automated | Export commit exists | SP66 |
| 37 | Enable unattended runs | Automated after John's step 1 answer | First night ends in a known state with a digest | all of section A in spikes.md |

## Later switch-ons (each needs John)
| # | Step | Who | Verified by | Spike first |
| --- | --- | --- | --- | --- |
| 38 | R16 self-merge: John picks GitHub Pro, a public repo or local-only enforcement; two weeks of shadow mode (ruling 2) | John | Tier agreement reviewed by John | SP18, SP19 |
| 39 | Cross-family reviewer for Tier 2: paid OpenAI key, wrapper only (engineer-models setup 4-6) | John | Only the wrapper sees the key | SP34, SP59 |
| 40 | Optional Android SDK and Gradle in bootstrap (engineer-deploy setup 9) | Automated | `./gradlew assembleRelease` passes | SP74 |
