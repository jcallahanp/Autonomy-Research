# Setup

Purpose: the order in which the engineer itself gets set up, who does each step, how it is verified and which spike (spikes.md) must pass first.

This is the engineer's own setup. Each project later gets its own ordered setup list from the feasibility hand-off (engineer-feasibility D52; flow.md stage 4). Values never pass through chat (engineer-human-loop §Q3).

**Who builds.** Every "Builder" row is done by the *builder session*: an interactive Claude Code session under John's Max `/login` (allowed under both auth paths, decisions.md ruling 1). In phase A it runs as a claude.ai/code cloud session on the template repo, which needs no logins or VM (engineer-runtime C19); from phase C on it runs on the VM as the `engineer` user inside `tmux`, which John can watch or leave through Remote Control (engineer-runtime C43-C53). The builder writes each piece from the file named in the row and records every pin it chooses in `docs/versions.md`.

## Phase A: builder writes the template (no VM, no secrets)
| # | Step | Who | Verified by | Spike first |
| --- | --- | --- | --- | --- |
| 1 | Create the template repo with the tree in repo-composition.md: `scripts/` (setup-root, bootstrap, doctor, supervisor, broker, trial, snapshot, checks), `templates/` (managed settings, hooks, systemd units, egress allowlist), plugin changes, `tests/`, `.github/workflows/ci.yml`, `.claude/` wiring | Builder, from repo-composition.md and stack.md (install list) | CI green: `claude plugin validate --strict` (engineer-runtime P40), `tests/check.sh`, `tests/check-mermaid.sh` | none |
| 2 | SP01: re-read the Agent SDK billing article and legal page; write the Path A/B page for John | Builder | Quote recorded | none |

## Phase B: John's bring-up (short; the precondition for every on-VM spike)
| # | Step | Who | Verified by | Spike first |
| --- | --- | --- | --- | --- |
| 3 | Rent or prepare an Ubuntu 24.04 machine at least the size in stack.md (VM size); put his SSH key on it (engineer-runtime setup 1) | John | `doctor.sh` checks OS, CPU, RAM, disk against stack.md | none |
| 4 | `git clone` the template, then `sudo bash scripts/setup-root.sh`: users `engineer`, `secretbroker`, `supervisor`; root-owned `/etc/claude-code/managed-settings.json` and `/opt/engineer/` (hooks, plugin copy); AppArmor bubblewrap profile; `agent-run` sudoers line; egress allowlist; Docker or rootless Podman (engineer-human-loop setup 1; engineer-feasibility setup 2-3) | John runs; script written in step 1 | `sudo -l` as `engineer` lists only `agent-run` | none (SP09, SP10 run next; on failure the VM is rebuilt and the script fixed) |
| 5 | As `engineer`: `tmux new -s builder`, `claude`, `/login` with Max; on a headless box, OAuth from a machine with a browser (engineer-runtime setup 4); then start the builder session there | John | `doctor.sh`: no `ANTHROPIC_API_KEY` in the interactive environment (engineer-runtime S15) | none |

## Phase C: builder on the VM: install and core spikes (no John)
| # | Step | Who | Verified by | Spike first |
| --- | --- | --- | --- | --- |
| 6 | `scripts/bootstrap.sh`: everything in stack.md's install list marked "bootstrap" | Builder | `claude --version` matches `docs/versions.md`; `/setup` probe; Chrome and Xvfb survive a restart | SP22, SP23 run here |
| 7 | Sandbox and managed settings live; hooks copied to root-owned `/opt/engineer/hooks/` and registered as repo-composition.md (Enforcement) says | Builder | Hooks fire and block; `engineer` cannot write `/opt/engineer` | SP06, SP09, SP10, SP13 |
| 8 | Broker: SOPS files, age key for `secretbroker`, `agent-run` job allowlist, `seed <NAME>` command that reads from the caller's terminal only | Builder | Dummy canary seeded and used; `engineer` reads no value | SP11, SP12 |
| 9 | Supervisor and systemd unit (`Restart=on-failure`, `ExecStartPre` reconcile, `ExecStopPost` ping), with the defaults in flow.md (Run defaults); `autoContinueAtUsageLimit` on (ruling 5) | Builder | Simulated stall, kill and limit on a toy repo each end in a known state | SP04, SP05, SP07, SP08 |
| 10 | Trial runner: container, host proxy, `result.json`, teardown, startup sweep (engineer-feasibility setup 4) | Builder | A tool ignoring `HTTP_PROXY` fails closed | SP03, SP26, SP27, SP28 |
| 11 | Approval-hash hook; reply parser tested offline | Builder | Edit blocked on mismatch; junk never approves | SP17, SP15 |
| 12 | Browser: profile dir chmod 700, Read denied, noVNC bound to `127.0.0.1:6080` only; browser PreToolUse hooks | Builder | Port not reachable from outside; hook fires on click | SP64 |
| 13 | Privacy settings (`DISABLE_FEEDBACK_COMMAND=1`, `cleanupPeriodDays` per flow.md); `dead-ends.md`, registry Meta fields, vet card, staleness script; Channels Telegram plugin installed (stack.md install list) | Builder | Settings file check; vet calls under 1 s | SP53, SP54 |
| 14 | SP02 (what each auth path loses), then John answers Path A or B and whether he has 1Password; recorded as an ADR in `docs/adr/` | Builder runs SP02; John decides | ADR committed | SP01, SP02 |

## Phase D: John's one setup sitting (one contiguous block; long waits first)
The worker's unsourced estimate is about 45-90 minutes across 11 services (engineer-feasibility setup 12); SP75 times each row. Every credential row is: John creates it, John runs `sudo -u secretbroker seed <NAME>` in his own SSH terminal, then the builder runs that row's check at once.
| # | Step | Who | Verified by (right after seeding) | Spike first |
| --- | --- | --- | --- | --- |
| 15 | **Long wait 1.** Outreach: create the API app, request production credentials, ask the employer to approve app creation and UI automation (engineer-browser A41, A42; engineer-feasibility D25) | John | Development credentials make one read call | SP67 answered live |
| 16 | **Long wait 2.** Google: app and OAuth client; consent screen to "In production" (engineer-human-loop E18; engineer-feasibility D12) | John | No 7-day Testing refresh token | SP70 |
| 17 | **Long wait 3.** WHOOP and Withings developer apps; is Withings+ required (engineer-human-loop E23-E25; E37 unverified) | John | App IDs exist | SP73 |
| 18 | Telegram: two bots with @BotFather, one for the supervisor, one for Channels (default, open-questions 13); send `/start` to each from his phone; seed both tokens; pair the Channels sender allowlist (engineer-runtime setup 5) | John | Test digest arrives; Channels relay prompt answered | SP16 |
| 19 | Remote Control push on his phone (engineer-runtime C52) | John | Test push received | none |
| 20 | Cloudflare: account, and a domain on Cloudflare if he has none (buying one is a T2 money prompt); parent token with Account API Tokens Edit (engineer-human-loop E1, E28) | John | Broker mints a child token with a TTL | SP71 |
| 21 | GitHub: register the machine account by hand (bots banned, engineer-human-loop E40), write not admin; fine-grained PAT for Contents, Pull requests, Metadata (engineer-protocol E80, E81) | John | Broker job opens a PR on a scratch repo (push refusal is checked in step 31) | none |
| 22 | Path B only: Console API key (engineer-human-loop E26, E27) | John | One bounded `claude -p` bills the key | SP01, SP02 |
| 23 | Vercel token if Vercel is used; scoped Supabase PAT if Supabase is used (engineer-human-loop E4, E7) | John | Child token minted | none |
| 24 | Attio key (a workspace token needs an admin, E22); n8n key with an expiry (E21, E33); Clay CLI first sign-in (engineer-browser A22) | John | One read call per tool | SP65, SP66 |
| 25 | GCP: grant the project roles for Workload Identity (engineer-deploy setup 3) | John | Builder binds the OIDC subject | SP72 |
| 26 | Slack config token (lasts 12 h, so late); builder creates the app from a manifest (engineer-human-loop E10, E11, E30) | John, then builder | App exists | SP68 |
| 27 | Every consent click in one run: Slack install, Google, Outreach, WHOOP, Withings (engineer-human-loop setup 5) | John | Broker job calls each API | none |
| 28 | Browser logins: on his computer `ssh -L 6080:127.0.0.1:6080 <vm>`, open `http://localhost:6080`; Google by hand first, then Attio, Clay, n8n, Outreach (engineer-browser setup 3-4, S11; the SSH tunnel is the default of the two routes the findings name) | John | Per-site logged-in check | SP63 (lifetimes recorded, not gating) |
| 29 | TOTP seeds into 1Password or `seed` for the pyotp store (engineer-browser setup 5) | John | Wrapper returns only the code | SP63 |
| 30 | Data-privacy toggle, 30 days vs 5 years (engineer-human-loop E85); confirm the hard gates and default `profile.yaml` (ruling 9) | John | Toggle recorded; profile defaults committed | none |

## Phase E: builder verification and switch-on
| # | Step | Who | Verified by | Spike first |
| --- | --- | --- | --- | --- |
| 31 | Branch protection, required checks, CODEOWNERS with "Do not allow bypassing" as far as his plan allows (engineer-protocol setup 3); then bot push to main and force push | Builder | Both pushes refused | SP18 |
| 32 | "Verifies all" table through broker jobs, first failing row named (engineer-human-loop setup 8) | Builder | All pass, or failing rows go to the digest | none |
| 33 | `cloudflared` tunnel and Access app with a one-email policy for VM web services; uptime monitors and healthchecks to the supervisor bot (engineer-deploy setup 2, 8) | Builder | John logs in from his phone; test alert arrives | SP71, SP72 |
| 34 | n8n: nightly workflow JSON export to git before any edit, by CLI if self-hosted or by API otherwise (engineer-deploy §Implications 8) | Builder | Export commit exists | SP66 |
| 35 | Daytime Channels session: `claude --channels plugin:telegram` in `tmux` as `engineer` (engineer-runtime spike 1) | Builder | Relay prompt reaches the Channels bot | SP08 |
| 36 | Enable unattended runs | Builder, after step 14 | First night ends in a known state with a digest | spikes.md section A |

## Later switch-ons (each needs John)
| # | Step | Who | Verified by | Spike first |
| --- | --- | --- | --- | --- |
| 37 | R16 self-merge: John picks GitHub Pro, a public repo or local-only enforcement; two weeks of shadow mode (ruling 2) | John | Tier agreement reviewed | SP18, SP19 |
| 38 | Cross-family reviewer for Tier 2: paid OpenAI key, wrapper only (engineer-models setup 4-6) | John | Only the wrapper sees the key | SP34, SP59 |
| 39 | Android SDK and Gradle via `bootstrap.sh --with-android` (engineer-deploy setup 9) | Builder | `./gradlew assembleRelease` passes | SP74 |
