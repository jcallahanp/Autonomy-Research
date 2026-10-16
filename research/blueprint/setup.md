# Setup

Purpose: the order in which the engineer itself gets set up, who does each step, how it is verified and which spike (spikes.md) must pass first.

This is the engineer's own setup. Each project later gets its own ordered setup list from the feasibility hand-off (engineer-feasibility D52; flow.md stage 4). Values never pass through chat (engineer-human-loop §Q3).

**Who builds.** "Builder" rows are done by the *builder session*: an interactive Claude Code session under John's Max `/login` (allowed under both auth paths, decisions.md ruling 1). In phase A it is a claude.ai/code cloud session on the template repo, which needs no VM (engineer-runtime C19); in phases C and E it runs on the VM as the unprivileged `engineer` user inside `tmux`, which John can watch through Remote Control (engineer-runtime C43-C53). It records every pin it chooses in `docs/versions.md`.

**Root vs builder (builder default).** All root work is in one idempotent script, `scripts/setup-root.sh`, that John runs with `sudo`; the builder never holds root. Modes: `--install` (users, apt repos and packages, `/opt/engineer/` copied from the reviewed checkout, managed settings without hook registrations, sudoers, systemd units installed, with `chrome-xvfb` and `novnc` enabled at once and `engineer-supervisor` left disabled, AppArmor profile, rootless Podman, a dummy `CANARY` secret, egress in install mode), `--lock` (registers the hooks in managed settings, enables `engineer-supervisor`, switches egress to the runtime list), `--unlock` (maintenance) and `--allow <host>`. **The guards are installed last**: until `--lock` at step 34 the builder works in its own checkout `~engineer/engineer-template` with deny rules and sandbox active but no hooks registered, and tests hooks from a scratch project's `.claude/settings.json`. After `--lock` the builder edits no template file on the VM; template changes go through a PR and a re-run of `--install` and `--lock`.

## Phase A: template repo and code (no VM, no secrets)
| # | Step | Who | Verified by | Spike first |
| --- | --- | --- | --- | --- |
| 1 | **Seed the template repo:** create a private GitHub repo `engineer-template` under his own account and push a full copy of the Autonomy-Research repo into it (`git clone` it, `git remote set-url origin <new repo>`, `git push --all`); open a claude.ai/code session on the new repo (name and method are builder defaults; repo-composition.md, Template repo) | John | `plugin/`, `tests/`, `research/findings/` present in the new repo | none |
| 2 | Change the copied repo into the template tree in repo-composition.md, scripts first (`setup-root.sh`, `bootstrap.sh`, `doctor.sh`), then supervisor, broker, trial, snapshot, checks, plugin changes, `templates/`, `tests/`, CI; open a PR that John merges | Builder (cloud), from repo-composition.md and stack.md | CI green: `claude plugin validate --strict` (engineer-runtime P40), `tests/check.sh`, `tests/check-mermaid.sh` | none |
| 3 | SP01: re-read the Agent SDK billing article and legal page; write the Path A/B page | Builder (cloud) | Quote recorded | none |

## Phase B: John's bring-up (short; the precondition for every on-VM spike)
| # | Step | Who | Verified by | Spike first |
| --- | --- | --- | --- | --- |
| 4 | Rent or prepare an Ubuntu 24.04 machine of at least the size in stack.md; put his SSH key on it (engineer-runtime setup 1) | John | `doctor.sh` checks OS, CPU, RAM, disk | none |
| 5 | As root: `ssh-keygen -t ed25519 -f /root/.ssh/engineer-template`; add the public key to the repo as a **read-only deploy key**; `git clone` to `/srv/engineer-template` | John | Clone succeeds; push with that key is refused | none |
| 6 | `sudo bash /srv/engineer-template/scripts/setup-root.sh --install`; it also makes the builder's checkout `~engineer/engineer-template` from `/srv` (engineer-human-loop setup 1; engineer-feasibility setup 2-3) | John runs | `sudo -l` per user matches repo-composition.md (Enforcement) | none |
| 7 | As `engineer`: `tmux new -s builder`, `claude`, `/login` with Max (on a headless box, OAuth from a machine with a browser, engineer-runtime setup 4); start the builder session | John | `doctor.sh`: no `ANTHROPIC_API_KEY` in this environment (engineer-runtime S15) | none |

## Phase C: builder on the VM, unprivileged, before the guards
Commits stay local in `~engineer/engineer-template` until the bot credential exists (step 21).
| # | Step | Who | Verified by | Spike first |
| --- | --- | --- | --- | --- |
| 8 | `scripts/bootstrap.sh`: the install-list rows marked "bootstrap" (user-level, no root) | Builder | `claude --version` matches `docs/versions.md`; `/setup` probe | SP22, SP23 run here |
| 9 | Hooks tested from a scratch project's `.claude/settings.json`; sandbox and managed deny rules already live | Builder | Hooks fire and block in the scratch project | SP06, SP09, SP13 (partial; rerun after lock) |
| 10 | Broker jobs called through `sudo -u secretbroker agent-run`, with a dummy canary seeded | Builder | Canary used; `engineer` reads no value | SP11, SP12 |
| 11 | Supervisor loop run as `engineer` on a toy repo, defaults from `templates/run-defaults.yaml`; `autoContinueAtUsageLimit` on (ruling 5) | Builder | Simulated stall, kill and limit each end in a known state | SP04, SP05, SP07, SP08 |
| 12 | Trial runner: container, host proxy, `result.json`, teardown, startup sweep (engineer-feasibility setup 4) | Builder | A tool ignoring `HTTP_PROXY` fails closed | SP03, SP26, SP27, SP28 |
| 13 | Approval-hash hook; reply parser offline; browser profile dir chmod 700 with Read denied; check the `chrome-xvfb` and `novnc` units started at step 6 (noVNC on `127.0.0.1:6080`); privacy settings; `dead-ends.md`, registry Meta fields, vet card, staleness script; Channels plugin installed at user scope (the one exception, repo-composition.md) | Builder | Edit blocked on mismatch; junk never approves; port closed from outside; vet calls under 1 s | SP15, SP17, SP53, SP54, SP64 |
| 14 | SP02 (what each auth path loses); John answers Path A or B and whether he has 1Password; ADR in `docs/adr/` | Builder runs SP02; John decides | ADR committed | SP01, SP02 |

## Phase D: John's one setup sitting (one contiguous block; long waits first)
The worker's unsourced estimate is about 45-90 minutes across 11 services (engineer-feasibility setup 12); SP75 times each row. Every credential row is: John creates it, runs `sudo -u secretbroker /opt/engineer/bin/seed <NAME>` in his own SSH terminal, and the builder runs that row's "Verifies all" check at once.

**OAuth route (builder default, untested; SP84).** Every OAuth app registers the loopback redirect `http://127.0.0.1:8765/callback/<service>`, plus `https://oauth.<his domain>/callback/<service>` for a vendor that refuses loopback. For each consent John runs `sudo -u secretbroker /opt/engineer/bin/oauth-capture <service>` with his own sudo password (the model cannot: it is not an `agent-run` job): it starts a listener on that port as `secretbroker`, prints the authorize URL, and John opens it in the Chrome on the VM through noVNC over the SSH tunnel of step 30, so the redirect lands on the VM; the job exchanges the code with the client secret and writes the refresh token straight into SOPS. The tunnel hostname is routed to the same listener at step 24, before any consent. Creating accounts is human-only, since browser-driven account creation is rejected (engineer-feasibility D44, D48).
| # | Step | Who | Verified by | Spike first |
| --- | --- | --- | --- | --- |
| 15 | **Long wait 1.** Outreach: API app with the redirect URIs above, request production credentials, ask the employer to approve app creation and UI automation (engineer-browser A41, A42; engineer-feasibility D25) | John | Development credentials make one read call | SP67 answered live |
| 16 | **Long wait 2.** Google: app and OAuth client with the redirect URIs; consent screen to "In production" (engineer-human-loop E18; engineer-feasibility D12) | John | No 7-day Testing refresh token | SP70 |
| 17 | **Long wait 3.** WHOOP and Withings developer apps with the redirect URIs; is Withings+ required (engineer-human-loop E23-E25; E37 unverified) | John | App IDs exist | SP73 |
| 18 | Alerting: sign up for healthchecks.io Hobbyist (dead-man) and UptimeRobot Free (uptime) (engineer-deploy E129, E131); seed the check ping URL and API keys; set his phone as the notification target | John | Test alert reaches his phone | SP72 |
| 19 | GitHub: register the machine account by hand (bots banned, engineer-human-loop E40); fine-grained PAT for Contents, Pull requests, Metadata (engineer-protocol E80, E81); add the bot with **write** access to `engineer-template` and each project repo | John | Broker job opens a PR on a scratch repo | none |
| 20 | Branch protection from **his own admin account** on `engineer-template` and each project repo, from the builder's checklist: required checks, CODEOWNERS with "Require review from Code Owners", "Do not allow bypassing", no force pushes, auto-merge allowed only if R16 is on (engineer-protocol setup 3); an `engineer-records` branch that only the bot may push to (repo-composition.md, Records) | John | Builder checks bot push to main and force push are refused | SP18 |
| 21 | Builder pushes its Phase C commits as a branch through `agent-run push-branch`; John merges the PR; then `git -C /srv/engineer-template pull` and `sudo .../setup-root.sh --install` | Builder, then John | `/opt/engineer` matches the merged SHA | none |
| 22 | Telegram: two bots with @BotFather, one for the supervisor, one for Channels (default, open-questions 13); `/start` to each from his phone; seed both tokens; pair the Channels sender allowlist (engineer-runtime setup 5) | John | Test digest arrives; Channels relay prompt answered | SP16 |
| 23 | Remote Control push on his phone (engineer-runtime C52) | John | Test push received | none |
| 24 | Cloudflare: account, and a domain on Cloudflare if he has none (buying one is a T2 money prompt); parent token with Account API Tokens Edit (engineer-human-loop E1, E28); then the builder creates the `cloudflared` tunnel and routes `oauth.<domain>` to the `oauth-capture` port | John, then builder | Broker mints a child token with a TTL; tunnel route answers | SP71 |
| 25 | Path B only: Console API key (engineer-human-loop E26, E27) | John | One bounded `claude -p` bills the key | SP01, SP02 |
| 26 | Vercel token if used; scoped Supabase PAT if used (engineer-human-loop E4, E7) | John | Child token minted | none |
| 27 | Attio key (a workspace token needs an admin, E22); n8n key with an expiry (E21, E33); Clay CLI first sign-in as `secretbroker` (`sudo -u secretbroker` the Clay login command; its browser step opened in the noVNC Chrome; engineer-browser A22) | John | One read call per tool | SP65, SP66 |
| 28 | GCP: grant the project roles for Workload Identity (engineer-deploy setup 3) | John | Builder binds the OIDC subject | SP72 |
| 29 | Slack config token (lasts 12 h, so late); builder creates the app from a manifest with the redirect URIs (engineer-human-loop E10, E11, E30) | John, then builder | App exists | SP68 |
| 30 | Browser logins: `ssh -L 6080:127.0.0.1:6080 <vm>` from his computer, open `http://localhost:6080`; Google by hand first, then Attio, Clay, n8n, Outreach (engineer-browser setup 3-4, S11; SSH tunnel is the default of the two routes the findings name) | John | Per-site logged-in check | SP63 (lifetimes recorded, not gating) |
| 31 | Every consent click in one run, each through `oauth-capture`: Slack install, Google, Outreach, WHOOP, Withings (engineer-human-loop setup 5) | John | Refresh token in SOPS; broker job calls each API | SP84 |
| 32 | TOTP seeds into 1Password or the `seed` command for the pyotp store (engineer-browser setup 5) | John | Wrapper returns only the code | SP63 |
| 33 | Data-privacy toggle, 30 days vs 5 years (engineer-human-loop E85); confirm the hard gates and default `profile.yaml` (ruling 9) | John | Toggle recorded; profile committed | none |
| 34 | **Last John row:** `sudo .../setup-root.sh --lock` | John | Managed settings list the hooks; units enabled; runtime egress list active | none |

## Phase E: builder under the guards (edits no guarded file)
| # | Step | Who | Verified by | Spike first |
| --- | --- | --- | --- | --- |
| 35 | Rerun the guard spikes under the locked settings on scratch repos | Builder | All pass; on failure John runs `--unlock`, the fix goes through a PR, then `--install` and `--lock` | SP06, SP10, SP13 |
| 36 | "Verifies all" table (below), first failing row named (engineer-human-loop setup 8) | Builder | All pass, or failing rows go to the digest | none |
| 37 | Access app with a one-email policy for VM web services on the step-24 tunnel; UptimeRobot monitors (engineer-deploy setup 2, 8) | Builder via broker jobs | John logs in from his phone | SP71 |
| 38 | n8n nightly workflow JSON export to git before any edit, by CLI if self-hosted or by API otherwise (engineer-deploy §Implications 8) | Builder | Export commit exists | SP66 |
| 39 | Daytime Channels session: `claude --channels plugin:telegram` in `tmux` as `engineer` (engineer-runtime spike 1) | Builder | Relay prompt reaches the Channels bot | SP08 |
| 40 | Enable unattended runs | Builder, after step 14 | First night ends in a known state with a digest | spikes.md section A |

## "Verifies all" table
Written by `scripts/checks/verify-all.sh` to `docs/setup-verify.md` as `Name | Broker job | Check | Result`, one row per seeded name, stopping the report at the first failure (engineer-human-loop setup 8; engineer-feasibility setup 12). Rows and checks (builder default; each check is one read call through `agent-run`):
| Name | Check |
| --- | --- |
| `GH_BOT_PAT` | Open and close a PR on a scratch repo; push to main refused |
| `TG_SUPERVISOR_TOKEN`, `TG_CHANNELS_TOKEN` | `getMe` succeeds; test digest delivered |
| `HC_PING_URL`, `UPTIMEROBOT_API_KEY` | Ping accepted; monitor list returned |
| `CF_PARENT_TOKEN` | Mint and revoke a child token with a TTL |
| `VERCEL_TOKEN`, `SUPABASE_PAT` (if used) | Mint or list call succeeds |
| `ATTIO_API_KEY`, `N8N_API_KEY`, Clay CLI session (in `secretbroker`'s home) | One read call each |
| `OUTREACH_*`, `GOOGLE_OAUTH_*`, `WHOOP_*`, `WITHINGS_*`, `SLACK_*` | One read call each with the stored refresh token; new refresh token written back |
| `ANTHROPIC_API_KEY` (Path B) | One bounded `claude -p` |
| Browser sessions | Logged-in check per site |
| TOTP | Wrapper returns a 6-digit code, no seed in output |

## Later switch-ons (each needs John)
| # | Step | Who | Verified by | Spike first |
| --- | --- | --- | --- | --- |
| 41 | R16 self-merge: John picks GitHub Pro, a public repo or local-only enforcement; two weeks of shadow mode (ruling 2) | John | Tier agreement reviewed | SP18, SP19 |
| 42 | Cross-family reviewer for Tier 2: paid OpenAI key, wrapper only (engineer-models setup 4-6) | John | Only the wrapper sees the key | SP34, SP59 |
| 43 | Android SDK and Gradle via `bootstrap.sh --with-android` (engineer-deploy setup 9) | Builder | `./gradlew assembleRelease` passes | SP74 |
