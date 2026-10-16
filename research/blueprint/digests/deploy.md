# Deployment (Area 13) - digest
Source: research/findings/engineer-deploy.md; verification: 18 of 20 verified, 2 unverified (checked 2026-10-16)

## Decision
- Deploy by platform CLI with one narrow token per job, never by OAuth MCP: wrangler reads a token from env for CI and automation (E6); Vercel MCP is OAuth remote (E38, E40); MCP stays read-only (inference from E38-E44).
- Web default: Cloudflare Workers with static assets, D1 and R2; Free has 100,000 requests/day (E1, E5, E2, E3).
- Container APIs: Cloud Run from source in John's GCP project, no Dockerfile or local Docker needed (E27, E36); free tier per billing account (E26; the "First 180,000 vCPU-seconds free per month" quote is UNVERIFIED, page truncated at verification).
- Postgres: Neon Free (100 CU-hours/project/month, E23) or Supabase Free (2 projects, 500 MB, E21).
- Always-on processes (bots, Socket Mode, n8n) stay on the existing VM with Docker Compose behind Cloudflare Tunnel plus an API-created Access app, John's health-app pattern (E29, E35, E31, E68).
- Automations code-first: systemd timers with `Persistent=` catch-up (E59) and Worker cron/webhook receivers (E55, E54); self-hosted n8n kept for John's visual flows, under nightly JSON export to git because Git source control is Business/Enterprise only (E49, E50) and the API is not on the free trial (E45).
- Android: PWA first; Capacitor wrapper built by Gradle on the VM only for native APIs such as Health Connect (E69, E72, E74); install by `adb`, exempt from verification (E79); no Play account until wide distribution ($25 fee, 12 testers for 14 days: E75, E77); iOS deferred at 99 USD/year (E88).
- Ops: secrets piped vault-to-setter (E102-E108); preview first, production after John's approval (E123); auto-rollback allowed (E117, E118); uptime alerts go to John directly (E129, E131); every charge goes through a two-step spend gate copied from Vercel's domain flow (E97-E100).

## Alternatives and rejected
- Vercel Hobby - alternative for personal Next.js; personal non-commercial only, 30-day lockout over limits (E9, E10, E12).
- Netlify Free - alternative; hard 300-credit cap (E13). Deno Deploy Free - alternative; personal use (E24).
- Railway - alternative for paid container + Postgres; Hobby $5/month (E17).
- GitHub Actions schedules - alternative for repo-bound jobs; drift, 60-day auto-disable on public repos (E52).
- Trigger.dev, Inngest, Windmill - alternatives if durable retries are needed (E60-E62).
- n8n Cloud Starter - alternative; 20 EUR/month annual, 2.5K executions (E48).
- Expo EAS (15 free builds/month) and local Linux builds; Bubblewrap TWA; fastlane supply or EAS Submit; Firebase App Distribution - alternatives for mobile (E70, E71, E73, E84, E82, E81).
- Pushover - alternative push, $4.99 one-time (E134). Infisical free - alternative vault if no 1Password (E113). Vercel Domains - alternative purchase route (E97).
- Fly.io - rejected for free-first: card after trial (E15).
- Render Free - rejected: Postgres expires in 30 days (E19).
- Cloudflare Containers - rejected: paid only (E7, E37).
- Tailscale Funnel as login - rejected: public exposure (E32).
- Vercel Password Protection - rejected: Pro $20/project/month (E33).
- Remote OAuth MCP as unattended deploy path - rejected (E38).
- Twilio SMS by default - rejected: $0.0083/segment plus 10DLC (E135).
- `echo VALUE | setter` - rejected: shell history (E104).
- Permanent Registrar-write token held by the engineer - rejected (E95, E96).
- Long-lived cloud keys in GitHub secrets - rejected for OIDC (E109).
- Sentry as sole alerting - rejected: email only (E132).
- Native Kotlin/Flutter as Android default - rejected (worker judgement: rewrite cost). EAS paid plans - not needed. iOS now - rejected (E88).
- n8n for strict-latency webhooks or on the free trial - rejected (E45). Temporal - rejected (not researched; over-built).

## Stack
| Tool | What it does here | Where it runs | Cost | Evidence |
| --- | --- | --- | --- | --- |
| Cloudflare Workers + wrangler (static assets, cron, receivers) | Default web, edge, cron, webhook receiver; piped secrets; rollback; tail | hosted / CLI on VM | Free: 100k requests/day, 5 cron triggers | E1, E5, E54, E102, E117, E128 |
| Cloudflare D1 / R2 | Data and object storage | hosted | Free: 5M reads/day, 5 GB; R2 10 GB-month | E2, E3 |
| Cloudflare Access + Tunnel | Private sign-in, outbound-only tunnel to VM | hosted + VM | free-seat count and Tunnel price unverified | E30, E31, E68 |
| Cloudflare API tokens (zone-scoped) | Narrowest DNS token | hosted | free | E93, E94 |
| Google Cloud Run | Container APIs from source | GCP | free tier per billing account (E26; quote unverified) | E26, E27, E28 |
| Neon Free / Supabase Free | Postgres | hosted | Neon 100 CU-hours/project/month; Supabase 2 projects, 500 MB | E23, E21, E22 |
| Docker Compose on existing VM | Always-on processes, self-hosted n8n | VM | VM already paid | E29 |
| systemd timers | Default VM scheduler | VM | free | E59 |
| n8n self-hosted (Community) | John's visual flows; instance MCP for edits | VM | free; internal-business licence | E47, E51 |
| Gradle wrapper + Capacitor + adb | Android builds and phone install | VM | free | E69, E72, E79 |
| GitHub OIDC / Workload Identity | Short-lived cloud tokens | GitHub Actions | free | E109-E111, E114 |
| GitHub environment reviewers | Production approval gate | GitHub | availability on John's plan unverified | E123 |
| 1Password `op` (vault CLI) | Source of piped secrets | VM | price not opened | E112 |
| UptimeRobot Free / healthchecks.io Hobbyist | Uptime and cron checks paging John | hosted | 50 monitors / 20 jobs, free | E129, E131 |
| ntfy | Push alerts | hosted | free; topic is the password | E133 |
| Sentry Developer | Error tracking, not paging | hosted | free, 5k errors | E132 |

## Setup steps
| Step | Automated or John | How it is verified |
| --- | --- | --- |
| 1 Cloudflare token (least privilege, or token-creating parent per Area 5) | **John** | `wrangler deploy` headless succeeds (spike 1) |
| 2 Access app + one-email policy per private app, by API | Automated | John logs in from his phone (spike 2) |
| 3 GCP service account via Workload Identity; OIDC subject pinned | Automated after **John** grants project roles | `gcloud run deploy --source .` from CI (spike 3) |
| 4 Seed root secrets and the vault service-account token | **John** | value never in transcript (spike 10) |
| 5 Billing profile and payment method on any platform | **John** | n/a |
| 6 OAuth consent screens (Google, WHOOP, Withings), Slack workspace install | **John** | receiver gets a test event (spike 6) |
| 7 GitHub Environment `production` with required reviewer, or chat approval plus `DEPLOY_ENABLED` | Automated config, **John** approves each promote | promote blocked without approval |
| 8 Uptime monitors and healthchecks pointing to ntfy/Telegram | Automated (account signup may be **John**) | alert reaches John (spike 14) |
| 9 Android SDK + Gradle in bootstrap (optional flag) | Automated | `./gradlew assembleRelease` passes (spike 8) |
| 10 Domain purchase, auto-renew; Cloudflare renewals not in API | **John** approves price; renewals by **John** in dashboard | quote without charge (spike 12) |
| 11 Play/Apple enrollment, 2FA, CAPTCHA/KYC, legal agreements, contract migrations | **John** (human-only list, Q12) | n/a |

## Repo composition
- Skill: `deploy` with the Q1 platform matrix as its decision table; picks by workload, not by tool name (Implications 1).
- Hooks: PreToolUse allowlist of deploy commands per project; blocks `--amount`, registrar and billing commands without a matching approval (Implications 2).
- Deny rules and a doctor check forbidding `echo VALUE |`, `cat .env`, reads of `.env*` (Implications 7).
- Pre-promote checklist (11 items: CI green on exact SHA, preview smoke, add-only migration with backup, rollback command, secrets by name, OIDC pinned, DNS/TLS, monitoring, no new paid resource, approval message, watch window with auto-rollback) and a rollback table (Q10, Q12).
- Scheduled job: nightly n8n workflow JSON export committed to git; engineer edits n8n only after the export exists (Implications 8).
- Bootstrap: optional Android SDK + Gradle step (Implications 9).
- Copied from John's health app: CI-green gate, add-only migrations, nightly `pg_dump`, `/healthz` with backup status, two uptime checks (E126, E127, E139, E145).
- Superpowers, Beads, Ralph: not addressed in this area.

## Spikes
| Spike | Probe (what to run) | Pass criterion |
| --- | --- | --- |
| 1 | Least-privilege Cloudflare token, `wrangler deploy` headless; Free build limits; Pages vs Workers static assets | Deploy succeeds; preference settled |
| 2 | Create Access app and policy by API; log in from John's phone | Login works; token route (parent vs hand-minted) settled |
| 3 | `gcloud run deploy --source .` from a service account via Workload Identity, incl. org-policy `allUsers` | Deploys; public-access behaviour known |
| 4 | Supabase Free idle pause against a keep-alive | Pause behaviour measured |
| 5 | n8n API and instance MCP create/update a workflow and credential on a throwaway self-hosted container | Both work, not on John's account |
| 6 | Worker receives real WHOOP and Withings test events with HMAC checks | Events verified; Withings response contract settled |
| 7 | systemd `Persistent=` after reboot; GitHub Actions schedule drift | Missed run fires; drift measured |
| 8 | `./gradlew assembleRelease` on VM; Health Connect from Capacitor plugin; wireless `adb` and PWA install | Builds and installs on John's phone |
| 9 | First `eas submit` vs fastlane first-upload rule on a throwaway app | Contradiction settled |
| 10 | Pipe a vault secret into wrangler, vercel, fly setters | Value absent from transcript, logs, hook output |
| 11 | Zone-scoped Cloudflare DNS token | Reads/writes own zone; other zones refused |
| 12 | Vercel `domains buy --json` without `--amount`, then Cloudflare `domain-check` | Quote returned; no charge |
| 13 | Preview, promote, rollback, migrate-with-backup on a throwaway app | Full cycle passes |
| 14 | UptimeRobot or healthchecks.io to ntfy or Telegram webhook on free tiers | Alert delivered |

## Requirements served
- R21: web deploys by CLI with scoped tokens, no human step beyond gates; Android after web via PWA/Capacitor/adb; no iOS (E6, E79, E88).
- R14: one typed-request gate for money, data and store, blocked until an allowlisted reply (E97-E100, E138).
- R12: least-privilege tokens minted by API where possible; human-only steps listed with reasons (E93, E31; Q12).
- R11: human-only list feeds the single setup page (Q12).
- R18 / Q3: watch window with auto-rollback then notify; alerts independent of the Claude session (E117, E125, E129).
- Q6: paid options carry prices (Pushover $4.99, Railway $5/month, n8n Cloud 20 EUR/month, Vercel password $20/project/month) (E134, E17, E48, E33).
- Q4: deploy reports carry preview URL, smoke result and rollback command (Q12 checklist).
- R23: optional Android step in the bootstrap (Implications 9).

## GTM scenario
- Finish tooling: n8n flows stay in n8n under nightly git export; edits through instance MCP (n8n 2.13+, workflows flagged "Available in MCP") or API, which is not on the free trial (E51, E45).
- New flows with Attio or Clay custom auth, retries or backfill: code in a repo on systemd timer or Cloudflare cron with a Worker receiver (Q5 rule, worker inference); Attio webhooks are HMAC-signed, 5 s timeout, 10 retries over about 3 days (E63, E64).
- Scan as-is, fix Attio tables and views, Clay workflows, clean data: gap in this area.

## Tensions
- Production promote needs John's approval (Q10, Q13) versus R21 "no human step beyond the gates" (gates are money, delete, store) and R16 self-merge. The requirements list R16 limits for production deploys as an open gap.
- Approval channel taken from engineer-runtime ("Channels/Telegram session", E137, E138); engineer-human-loop says do not rely on the relay overnight and puts gates on a supervisor bot. Spend gates and promotes need to move to the supervisor digest/T2 path.
- Secrets source: 1Password `op` service account here (Q9) versus SOPS+age broker in engineer-human-loop versus 0600 env file in engineer-runtime. Infisical free is this area's fallback; human-loop rejects self-hosted Infisical.
- Cloud Run free-tier quote ("First 180,000 vCPU-seconds free per month") is UNVERIFIED and appears in the summary; E26 rests on an Exa fetch.
- WHOOP "expects a response within a second" UNVERIFIED; page only recommends a 2XX within a second (E65 corrected).
- Unresolved: first Play upload (Expo E92 vs fastlane E84, spike 9); Withings response contract (spike 6); Pages vs Workers static assets (spike 1).
- Cloudflare Access free-seat count and Tunnel price unverified (open q 2-3); Supabase Free idle pause unverified (open q 1).
- Self-hosted n8n on the VM assumes John's n8n can move or already is self-hosted; n8n Cloud vs self-hosted for John is not established.
- GitHub environment reviewers' availability on John's plan unverified.

## Open for John
- Whether production promotes stay gated on his approval or become automatic after the pre-promote checklist (R16/R21 limit).
- Vault: 1Password (does he have it?) or the human-loop SOPS+age store.
- Domain purchases and renewals: buy himself or mint a one-purchase Registrar token.
- When a Play developer account (US$25) is worth opening; iOS stays deferred.
- Whether destructive or contract migrations are ever delegated (default: never).
