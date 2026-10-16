# Deploy operations: domains, secrets, environments, rollback, monitoring, human-only steps

Brief: Define how an autonomous Claude Code engineer handles the operational side of deploys unattended (domains, DNS, TLS, secrets, preview vs production, rollback, logs, uptime, alerts) and which steps stay with John.
Run: research/runs/engineer-deploy/PLAN.md

Recommendation (one line): the engineer holds only narrow, per-job tokens (zone-scoped Cloudflare DNS Edit, per-platform deploy tokens, GitHub OIDC), sets secrets by piping from a vault CLI into the platform CLI, deploys preview then promotes production through a human-approved GitHub Environment, rolls back with the platform command, watches with free uptime checks that publish to ntfy/Telegram, and never buys, verifies identity, consents or pays without John. Alternatives and rejected options are in each Takeaway. Spikes before building are listed at the end of the Gaps in each section and collected in the last section.

## Domains, DNS, TLS and narrowest tokens
### Takeaway
Cloudflare lets a token be limited to one zone with DNS Edit, so DNS work uses a per-zone token and nothing else. Domain purchase is technically automatable on both Cloudflare (beta API) and Vercel (CLI), but Vercel's own flow is built as a two-step human approval, which is the model to copy: the engineer asks for the price, John approves the exact amount, the engineer then charges. TLS is automatic on Cloudflare. Confidence: medium-high (Vercel and Cloudflare pages opened; TLS on Vercel, Fly, Pages not opened).

### Cited findings
- DNS token can be limited to a single zone; Edit is full CRUDL, so give Edit only when records are written — https://developers.cloudflare.com/fundamentals/api/get-started/create-token/, opened 2026-10-16, WebFetch — Quote: "Select which resources the token is authorized to access."
- A leaked Cloudflare token acts with its full authorization, so scope and TTL/IP filters matter — same page — Quote: "Anyone with this token can perform the authorized actions against the resources that the token has access to."
- Cloudflare Registrar API can register domains (beta) but not renew, transfer or update contacts — https://developers.cloudflare.com/registrar/registrar-api/, opened 2026-10-16, WebFetch — Quote: "Renewals are not yet available through the API."
- Registrar API needs a write token and a stored payment method and default contact set up in the dashboard; premium domains are excluded — https://developers.cloudflare.com/api/resources/registrar/subresources/registrations/methods/create/ (Exa search highlight only, page not opened; see Gaps) and registrar-api page — Quote: "An API token with Registrar write permissions." (paraphrased by the fetch tool from the registrar-api page; exact wording of that page not re-verified)
- Vercel CLI supports price check without charging and a charge only with an approved amount — https://vercel.com/docs/cli/domains, opened 2026-10-16, WebFetch — Quote: "Only after a human approves: charges $20.00 now"
- Vercel: the approved amount must equal the current price and registrations are non-refundable — same page — Quote: "The amount must match the current price; it isn't a spending limit."
- Vercel: an unknown purchase outcome must be inspected before retry (double-charge risk) — same page — Quote: "Retrying immediately can charge you twice."
- Vercel buy needs registrant first name, last name, phone from a person; billing details never supply them — same page — Quote: "never the registrant's first name, last name, or phone"
- Cloudflare TLS is issued and renewed automatically — https://developers.cloudflare.com/ssl/edge-certificates/universal-ssl/, opened 2026-10-16, WebFetch — Quote: "Cloudflare handles issuance, renewal, and deployment automatically."
- The Vercel docs page carries an "AI agents" navigation note ("For AI agents: Follow these links to understand how this page connects...") — it is a link map, not a command; not followed.

### Contradictions
- None found. (Cloudflare Registrar overview page said nothing on API registration; the API page says beta registration exists. Not a conflict: different pages.)

### Inferences
- Narrowest token per job (mine, from the Cloudflare scoping page): DNS records = one zone, DNS Edit, with IP filter and TTL; verification-only = DNS Read; domain purchase = a separate Registrar-write token that the engineer does not hold by default (John mints it for one purchase or buys himself); Workers/Pages deploy = a separate account token limited to those scopes (permission names not verified, see Gaps).
- Spend gate design: two-step. Step 1 non-charging quote (Vercel `domains buy --json` without `--amount`, or Cloudflare `domain-check`); step 2 send the price, term and auto-renew choice over the approval channel; only on John's reply run the charge. Because renewals are not API-supported at Cloudflare, John must renew or enable auto-renew himself in the dashboard.
- Preferred route: buy through Cloudflare (at cost) and keep DNS there, so TLS and DNS tokens live in one place; fall back to the Vercel CLI if the platform is Vercel. Registrant legal details are John's to give.

### Gaps
- Per-platform TLS for Vercel, Fly and Cloudflare Pages/Workers custom domains: not opened this session.
- Exact Cloudflare permission names for Workers deploy token: not opened.
- The `create` registration page was seen only as a search highlight (Exa); the fetch tool was not run on it.
- Spike: scoped token creation by API (token-creating tokens) vs John minting tokens by hand.

## Secrets per platform without values in model context
### Takeaway
Every platform CLI studied accepts the secret on stdin or from a file, so the engineer can run `vault-cli read ... | platform-cli secret set NAME` and the model sees only the command and "success". CI-to-cloud uses GitHub OIDC with no stored keys. Vaults: 1Password CLI (`op run`) and Infisical free tier exist; Doppler not verified. Confidence: medium-high.

### Cited findings
- Wrangler `secret put` accepts piped input — https://developers.cloudflare.com/workers/wrangler/commands/workers/, opened 2026-10-16, WebFetch — Quote: "The `put` command can also receive piped input."
- Wrangler `secret bulk` reads stdin if no file is given, up to 100 secrets — same page — Quote: "If omitted, Wrangler expects to receive input from stdin rather than a file."
- Vercel `env add` takes a value from a file or stdin; piping with echo leaks to shell history — https://vercel.com/docs/cli/env, opened 2026-10-16, WebFetch — Quote: "Warning: this will save the value in bash history, so this is not recommended for secrets."
- Vercel `env add` defaults to Secret type for production and preview, and a value may come via stdin — same page — Quote: "unless you pass a type flag, `--yes`, `--value`, or a value through stdin"
- Vercel can run a command with env without writing a file — same page — Quote: "runs any command with environment variables from your linked Vercel project, without writing them to a file."
- Fly `secrets import` reads stdin — https://docs.fly.io/flyctl/secrets-import, opened 2026-10-16, WebFetch — Quote: "Values are read from stdin as NAME=VALUE pairs"
- Fly `--stage` sets secrets without a deploy on machine apps — same page — Quote: "sets the secrets without triggering a deployment on machine apps."
- GitHub OIDC replaces stored cloud credentials with short-lived tokens — https://docs.github.com/en/actions/concepts/security/openid-connect, opened 2026-10-16, WebFetch — Quote: "request a short-lived access token directly from the cloud provider."
- OIDC needs `id-token: write` and the cloud trust policy must pin the subject — https://docs.github.com/en/actions/reference/security/oidc, opened 2026-10-16, WebFetch — Quote: "Without `id-token: write`, the OIDC JWT ID token cannot be requested."
- Subject can be pinned to repo and environment — same page — Quote: "repo:ORG-NAME/REPO-NAME:environment:ENVIRONMENT-NAME"
- 1Password `op run` injects secrets into one process; same-user processes may read them — https://www.1password.dev/cli/secrets-environment-variables/, opened 2026-10-16, WebFetch — Quote: "You should assume that processes on your computer can access the environment of other processes run by the same user."
- Infisical free: 5 identities, unlimited projects, 3 environments per project — https://infisical.com/pricing, opened 2026-10-16, WebFetch — Quote: "unlimited projects" (identities 5 and environments 3 stated in the same fetch result, not separately quoted)
- John's health-management repo already uses OIDC + Workload Identity Federation with no stored keys, only `deploy.yml` on `main` — /home/user/health-management/docs/design/ops.md:40-43 — Quote: "reaches the VM through IAP using GitHub OIDC and Workload Identity Federation"

### Contradictions
- None found.

### Inferences
- Pattern (mine): `op read "op://vault/item/field" | wrangler secret put NAME`; `op read ... | vercel env add NAME production --sensitive`; `printf 'NAME=%s\n' "$(op read ...)" | fly secrets import --stage`. The value passes through the shell pipe, not through a tool result. Rule: never `echo value |` (history), never `cat .env`, and add `permissions.deny` on `.env*` (registry row exists). Caveat: with `op run` the value sits in the child process environment.
- `op` needs a service-account token on the machine; that token is the one long-lived secret, so scope its vault to deploy secrets only (registry row "1Password CLI service accounts" exists). If John has no 1Password, Infisical free (self-hostable) is the free vault; Doppler was not verified, so not recommended.
- Secrets that the model must never see (production DB password, payment keys): John seeds them once in the vault; the engineer only references them. Secrets the engineer generates (random app keys) it can create with `openssl rand` piped straight into the setter.
- Fly `secrets import` without `--stage` may redeploy; use `--stage` then one controlled `fly deploy`.

### Gaps
- Doppler free tier: not opened.
- GitHub Actions encrypted secrets via `gh secret set` stdin: not opened (known behaviour not cited).
- Whether Claude Code logs the piped command's stdout when a vault CLI errors and prints the value: spike.

## Environments, migrations and rollback
### Takeaway
Preview per branch is a platform default; production promote should be a separate human-gated step (GitHub Environment reviewers or a chat approval). Each platform has a one-command rollback, but Cloudflare and Vercel only roll code, not data, so migrations must be additive (expand-contract) with a backup first; John's health app already encodes exactly this rule. Confidence: high for the rollback commands, medium for gates.

### Cited findings
- Vercel rollback command and Hobby limit — https://vercel.com/docs/cli/rollback, opened 2026-10-16, WebFetch — Quote: "On the hobby plan, you can only roll back to the previous production deployment."
- Vercel undo rollback by promote — same page — Quote: "To undo a rollback, promote a deployment using `vercel promote`"
- Wrangler rollback creates a new deployment on all routes — https://developers.cloudflare.com/workers/configuration/versions-and-deployments/rollbacks/, opened 2026-10-16, WebFetch — Quote: "Rolling back to a previous version of your Worker will immediately create a new deployment"
- Wrangler rollback does not touch data or bindings — same page — Quote: "Resources connected to your Worker will not be changed during a rollback."
- Wrangler rollback is limited to 100 versions — same page — Quote: "You can only roll back to the 100 most recently published versions."
- `wrangler deployments list --json` and `status --json` give machine output — https://developers.cloudflare.com/workers/wrangler/commands/workers/, opened 2026-10-16, WebFetch — Quote: "Display output as JSON"
- Fly: `fly releases` lists releases; `fly deploy --image` deploys a given image, `--strategy` has canary, rolling, bluegreen, immediate — https://docs.fly.io/flyctl/deploy, opened 2026-10-16, WebFetch — Quote: "Options are canary, rolling, bluegreen, or immediate. The default strategy is rolling."
- Fly releases page lists releases with success/fail — https://docs.fly.io/flyctl/releases/, opened 2026-10-16, WebFetch — Quote: "all the releases of the application onto the Fly platform"
- GitHub environment reviewers gate secrets — https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/review-deployments, opened 2026-10-16, WebFetch — Quote: "You can approve or reject jobs awaiting review."
- Expand/migrate/contract — https://martinfowler.com/bliki/ParallelChange.html, opened 2026-10-16, WebFetch — Quote: "In the expand phase you augment the interface to support both the old and the new versions."
- Google SRE: pause and roll back a bad canary, small deployments — https://sre.google/workbook/canarying-releases/, opened 2026-10-16, WebFetch — Quote: "we should pause and roll back the deployment, or perhaps contact a human to help troubleshoot the issue."
- John's own deploy: CI gate, migrate, up, probe /healthz, auto-roll back; migrations add-only so the previous image runs on the new schema — /home/user/health-management/docs/design/ops.md:44-48 — Quote: "Migrations only add, and new columns are nullable or defaulted (ADR 0010), so the previous image runs on the newer schema."
- Nightly dump plus monthly restore check; /healthz reports backups — /home/user/health-management/docs/design/ops.md:55-61 — Quote: "Nightly `pg_dump` at 03:30 US Eastern"

### Contradictions
- None found. (Fly page did not document a rollback command; absence, not conflict.)

### Inferences
- Rollback table (mine): Vercel `vercel rollback [url]` then `vercel promote` to undo; Cloudflare `wrangler rollback [version-id]` (blocked if bindings changed); Fly `fly deploy --image <previous>` after `fly releases --image` shows the prior reference; self-hosted compose: restart previous image (John's deploy.sh pattern).
- Environments: preview URL for every branch; production only after the engineer posts preview URL + smoke result and John approves; implement as a GitHub Environment `production` with required reviewer (availability on private free repos not verified) or, if that is unavailable, an approval message on the chat channel plus a `DEPLOY_ENABLED` variable like John's.
- Migrations: backup (dump + row counts) before every migrate; migrate step is expand-only; contract steps are a separate later change John approves; feature flags only as an env var/`features.yaml` baked into the image (health app: rollback restores switches too, ops.md:117) before any flag service.
- Rollback never fixes data: any destructive migration is a human-only decision.

### Gaps
- Fly rollback command not on any page opened; derived from `--image`.
- Vercel promote / Pages rollback semantics for Cloudflare Pages not opened.
- Environment-reviewer availability on John's plan: not stated on the page.
- Spike: run a throwaway app through preview, promote, rollback on the chosen platform, plus migrate-then-rollback with a dump restore.

## Monitoring, logs, alerts and the approval channel
### Takeaway
Free, adequate stack: platform CLI logs (`wrangler tail`, vercel/fly logs), UptimeRobot free (50 monitors, 5 min) for HTTP, healthchecks.io free (20 checks) for cron, Sentry free for errors (email only), and ntfy or Telegram bot for push. The engineer's approval channel (Telegram via Channels, wave 1) is a send-only Bot API call, so alerts can share it. Confidence: medium (UptimeRobot channel detail unclear; ntfy auth not read).

### Cited findings
- `wrangler tail` streams logs with JSON format and status filter — https://developers.cloudflare.com/workers/wrangler/commands/workers/, opened 2026-10-16, WebFetch — Quote: "Filter by invocation status: `ok`, `error`, or `canceled`"
- UptimeRobot Free: 50 monitors, 5 min — https://uptimerobot.com/pricing/, opened 2026-10-16, WebFetch — Quote: "50 monitors"
- UptimeRobot free is positioned for hobby use; SMS/voice credits not included — same page — Quote: "Good for hobby and non-profit projects."
- healthchecks.io Hobbyist is free for 20 jobs — https://healthchecks.io/pricing/, opened 2026-10-16, WebFetch — Quote: "Monitor 20 jobs"
- Sentry free: 5k errors, one user, email alerts only — https://sentry.io/pricing/, opened 2026-10-16, WebFetch — Quote: "5k errors"
- ntfy publishes with plain HTTP and topic name is the password — https://docs.ntfy.sh/publish/, opened 2026-10-16, WebFetch — Quote: "the topic is essentially a password"
- Pushover: $4.99 one-time per platform, 10,000 free messages per month — https://pushover.net/pricing, opened 2026-10-16, WebFetch — Quote: "$4.99 USD one-time purchase"
- Twilio US SMS $0.0083 per segment, $1.15 per month long code, plus 10DLC onboarding fees — https://www.twilio.com/en-us/sms/pricing/us, opened 2026-10-16, WebFetch — Quote: "$0.0083 per segment"
- Telegram Bot API is HTTPS with the token in the URL — https://core.telegram.org/bots/api, opened 2026-10-16, WebFetch — Quote: "All queries to the Telegram Bot API must be served over HTTPS."
- Approval channel from wave 1: Channels forward permission prompts, session must be open — /home/user/Autonomy-Research/research/findings/engineer-runtime.md:529-531 — Quote: "Events only arrive while the session is open, so for an always-on setup you run Claude in a background process or persistent terminal."
- Channel allowlist caution — /home/user/Autonomy-Research/research/findings/engineer-runtime.md:532 — Quote: "Anyone who can reply through the channel can approve or deny tool use in your session, so only allowlist senders you trust with that authority."
- John's health app: two 5-minute uptime checks through Cloudflare Access service token, email on failure — /home/user/health-management/docs/design/ops.md:62 — Quote: "Two uptime checks every 5 minutes"

### Contradictions
- None found.

### Inferences
- Alert split (mine): approvals and "deploy done/rolled back" go through the Channels/Telegram session; outages must not depend on the Claude session being alive, so uptime tools alert John directly (email plus ntfy or Telegram webhook) and also write a status the engineer reads on next run. Pushover is the one paid option worth $4.99 only if ntfy phone push proves unreliable. Twilio SMS rejected for default: per-message cost plus 10DLC registration, which is a human identity step.
- Health endpoint design from John's repo (/healthz includes backups status, "ok" body match) is the model for every new app.
- Post-deploy auto-check: after promote, the engineer curls /healthz and one key page for N minutes, compares error counts, rolls back itself on failure (Google canary guidance) and then messages John; rolling back is allowed without approval, rolling forward is not.

### Gaps
- UptimeRobot free tier integrations (Telegram/webhook) not confirmed; page said only "Only 5 integrations".
- Cloudflare health checks / Notifications pricing: not opened.
- Sentry alerts to Slack/Telegram on free: page indicated integrated alerts not available; confirm via docs.
- ntfy authentication, self-hosting: past character 100000 of the page; not read.
- Better Stack free tier: not opened.
- Does a stopped Claude session still deliver Telegram messages: out of facet.

## Human-only steps
### Takeaway
Keep with John: money (any charge, renewal, billing profile), registrant/legal identity, KYC and Apple Developer enrollment (legal-name verification, 2FA Apple Account, $99/yr, D-U-N-S for orgs), OAuth consent, and creating the root credentials/2FA. A browser agent can do clicks after John's go in a session he is logged into, but cannot legally attest identity for him. Confidence: medium (Apple page and Vercel CLI opened; Stripe, Google Play, OAuth consent rules not opened).

### Cited findings
- Apple enrollment requires 2FA Apple Account, legal-name verification and a paid membership — https://developer.apple.com/programs/enroll/, opened 2026-10-16, WebFetch — Quote: "The Apple Developer Program is 99 USD per membership year."
- Apple organization needs legal authority and D-U-N-S — same page — Quote: "you'll be the Account Holder and must have the legal authority to bind your organization to legal agreements."
- Apple name must match legal identity — same page — Quote: "will cause a delay in the approval of your enrollment."
- Domain registrant details (name, phone) and charge approval stay with a person — https://vercel.com/docs/cli/domains, opened 2026-10-16, WebFetch — Quote: "Ask a person to approve the price, paying team, and, for a purchase, automatic renewal."
- Cloudflare dashboard settings are the only way to manage the registrar address book and agreement — Cloudflare create-registration page (Exa highlight, not opened) — see Gaps.
- Slack app install still needs an admin click (existing registry row, edge-cases-and-setup-list.md) — /home/user/Autonomy-Research/research/tool-registry.md:279 — Quote: "workspace install still needs an admin click"

### Contradictions
- None found.

### Inferences
- List for John (mine): (1) buy/renew a domain, set auto-renew; (2) create billing profile and payment method on any platform; (3) store and seed root secrets and the vault service-account token; (4) OAuth consent screens (Google, WHOOP, Withings) and Slack workspace install; (5) Apple/Google Play developer enrollment and App Store submissions that attest identity; (6) 2FA enrolment and recovery codes; (7) any CAPTCHA/KYC/identity check; (8) accepting legal agreements and registrar terms; (9) deleting production data or contract migrations.
- Browser agent after John's go (registry: Playwright persistent profile on the VM, John logs in once): fill non-attesting forms, create API tokens in dashboards, click through consent flows already authorised by John in a session he is present for, read dashboards. Not CAPTCHA/bot-check evasion (registry rejects). Treat "technically possible" as separate from "should": the Terms of the store may require the account holder personally, which was not verified.
- The spend gate and these steps share one mechanism: a typed request on the approval channel showing amount, payee and what it unlocks, with the engineer's action blocked until a matching reply.

### Gaps
- Stripe/payment-provider KYC, Google Play enrollment, OAuth consent automation rules, registrar terms on agent purchases: not researched.
- Legal question (can an agent act as the account holder): no source; John's own legal advice if relevant.

## Deploy safety checklist
### Takeaway
A short, mechanical gate the engineer runs before promote; each item has a check it can run and a stop rule. Confidence: medium (assembled from cited platform behaviours and John's own deploy.sh pattern).

### Cited findings
- John's deploy.sh refuses unless CI for the exact commit is green — /home/user/health-management/docs/design/ops.md:44-45 — Quote: "**refuses** unless `ci_gate.py verify` finds the newest CI run for that exact commit succeeded with every job green"
- Canary evaluation: compare to control, use absolute SLOs, one canary at a time — https://sre.google/workbook/canarying-releases/, opened 2026-10-16, WebFetch — Quote: "It is important to also use absolute measures, such as defined SLOs, to ensure the system is operating correctly."
- Releases small and automated — same page — Quote: "Deployments should be performed by computers, not humans."

### Contradictions
- None found.

### Inferences
- Checklist (mine). 1 CI green for exact SHA; no secrets in diff (gitleaks row exists). 2 Preview URL passes smoke (`/healthz`, key page, console/network errors). 3 Migration is add-only; backup taken and restorable (dump with row counts). 4 Previous release identified and rollback command dry-read (version id, image ref). 5 Secrets present in target environment (names only, `vercel env ls` / `wrangler secret list` / `fly secrets list`); production values separate from preview. 6 OIDC subject pinned, token scopes narrowest, no new long-lived key. 7 DNS/TLS valid (`vercel domains verify`, curl -I). 8 Uptime check and error tracking exist for the new URL before launch. 9 Spend: no new paid resource without John's reply. 10 Approval message to John with diff summary, preview URL, rollback command; wait. 11 After promote: watch window with auto-rollback on failed health, then notify.
- Not-in-scope cases requiring John: destructive migration, new paid plan, new domain, new OAuth scope.

### Gaps
- The checklist is untested; spike on a throwaway app.

## Spikes before building
1. Pipe a vault secret into wrangler/vercel/fly setters and prove the value never appears in transcript, logs, or hook output.
2. Cloudflare scoped token created for one zone: create/read DNS, prove other zones are refused.
3. Vercel `domains buy --json` quote step on a real name without `--amount`; confirm zero charge; then Cloudflare `domain-check`.
4. Full preview, promote, rollback, migrate-with-backup cycle on a throwaway app on the chosen platform.
5. Alert path: UptimeRobot or healthchecks.io to ntfy/Telegram webhook; confirm free-tier support.

## Alternatives and rejected
- Alternatives: Pushover ($4.99 one-time) for push; Infisical free/self-hosted for vault; Cloudflare Registrar vs Vercel Domains for purchases.
- Rejected as default: Twilio SMS (per-message cost, 10DLC onboarding fees); `echo VALUE | setter` (shell history, per Vercel's own warning); giving the engineer a Registrar-write token permanently; storing long-lived cloud keys in GitHub secrets (OIDC instead); Sentry free as sole alerting (email only).

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Cloudflare API tokens (zone-scoped) | https://developers.cloudflare.com/fundamentals/api/get-started/create-token/ | Per-zone DNS Edit/Read tokens, IP filter, TTL | hosted | 2026-10-16 | Use: narrowest DNS token |
| Cloudflare Registrar API (beta) | https://developers.cloudflare.com/registrar/registrar-api/ | Search, check, register; no renew/transfer/contacts | hosted | 2026-10-16 | Use only behind a spend gate; token not kept by engineer |
| Vercel CLI domains buy/rollback/env | https://vercel.com/docs/cli/domains | Non-interactive price quote, human-approved charge, rollback, env stdin | CLI | 2026-10-16 | Use: copy the two-step approval |
| Wrangler secret/rollback/tail | https://developers.cloudflare.com/workers/wrangler/commands/workers/ | Piped secrets, rollback, tail, deployments --json | CLI | 2026-10-16 | Use |
| Fly secrets import / deploy --image | https://docs.fly.io/flyctl/secrets-import | Stdin secrets with --stage; deploy a given image | CLI | 2026-10-16 | Use; rollback derived |
| GitHub OIDC | https://docs.github.com/en/actions/reference/security/oidc | Short-lived cloud tokens with subject pinning | GitHub Actions | 2026-10-16 | Use |
| GitHub environment reviewers | https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/review-deployments | Human approval before a job gets environment secrets | GitHub | 2026-10-16 | Use if available on plan |
| Infisical (free) | https://infisical.com/pricing | Secrets manager; 5 identities, 3 envs | hosted / self-host | 2026-10-16 | Fallback vault if no 1Password |
| UptimeRobot free | https://uptimerobot.com/pricing/ | 50 monitors, 5 min | hosted | 2026-10-16 | Use; integrations unverified |
| healthchecks.io free | https://healthchecks.io/pricing/ | 20 cron checks | hosted | 2026-10-16 | Use for cron |
| Sentry Developer (free) | https://sentry.io/pricing/ | 5k errors, 1 user, email alerts | hosted | 2026-10-16 | Use for errors only; not for paging |
| ntfy | https://docs.ntfy.sh/publish/ | HTTP push by topic | hosted / self-host | 2026-10-16 | Use for alerts; auth unread |
| Pushover | https://pushover.net/pricing | $4.99 one-time, 10k msgs/month | hosted | 2026-10-16 | Fallback push |
| Twilio SMS | https://www.twilio.com/en-us/sms/pricing/us | $0.0083/segment, $1.15/month number, 10DLC fees | hosted | 2026-10-16 | Reject by default |
| Telegram Bot API | https://core.telegram.org/bots/api | HTTPS send with bot token | hosted | 2026-10-16 | Use: shares approval channel |
| Google SRE canarying | https://sre.google/workbook/canarying-releases/ | Canary and rollback principles | docs | 2026-10-16 | Reference |
