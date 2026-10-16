# Integration edge cases and the human setup list

Brief: Build the integration edge-case checklist an autonomous engineer runs before committing to a path, apply it to John's services, and turn a chosen path into an ordered human setup list.
Run: research/runs/engineer-feasibility/PLAN.md

Recommendation (one): the engineer runs a fixed 12-point edge-case checklist per integration BEFORE choosing a path, records the answers in a per-service "integration card", then derives one setup list sorted by dependency and grouped by service. A human does only account creation, billing, consent clicks, 2FA and pasting secrets; the browser agent (Claude in Chrome, local) prepares forms and stops at those points.
Alternatives: (a) per-service interactive setup as each gate appears (rejected by requirement R11, no piecemeal asks); (b) a pure script like `setup.sh` with prompts (good for the final verification step only); (c) fully browser-agent-driven setup (rejected: login/CAPTCHA pause by design, ToS bans bot account creation on some platforms).
Rejected: asking the model to solve CAPTCHA/2FA; storing secrets in the chat; Supabase `anon`/`service_role` keys for new work (deprecation by end 2026).
Spike before building: (1) Google OAuth app publishing status (Testing = 7-day refresh tokens) with John's real scopes; (2) Outreach dev credentials vs production approval; (3) Clay API surface on John's plan; (4) n8n API plan check; (5) WHOOP/Withings refresh-token rotation store.

## Q1 Generic integration edge-case checklist

### Takeaway
A defensible checklist has 12 points: auth type and token lifetime, refresh-token rotation, scopes/admin role needed, rate limit and 429 handling, pagination, webhook signature, webhook retries/ordering/duplicates, idempotency, sandbox vs production, API version/deprecation, plan gating, data residency/ToS. Stripe's webhook and idempotency docs and Google's OAuth and AIP-194 docs supply the concrete rules. Confidence: medium-high (Stripe and Google are primary; Twilio, Shopify, Microsoft guidelines, Zapier and Postman were not opened).

### Cited findings
- Webhooks: verify signature on the raw body, return 2xx fast — https://docs.stripe.com/webhooks, opened 2026-10-16, WebFetch — Quote: "Quickly returns a successful status code (`2xx`) before any complex logic that might cause a timeout."
- Raw-body trap — https://docs.stripe.com/webhooks, opened 2026-10-16, WebFetch — Quote: "Any manipulation to the raw body of the request causes the verification to fail."
- Ordering not guaranteed — https://docs.stripe.com/webhooks, opened 2026-10-16, WebFetch — Quote: "Stripe doesn’t guarantee the delivery of events in the order that they’re generated."
- Duplicates: dedupe on event ID — https://docs.stripe.com/webhooks, opened 2026-10-16, WebFetch — Quote: "Webhook endpoints might occasionally receive the same event more than once."
- Replay protection via signed timestamp, default tolerance 5 minutes — https://docs.stripe.com/webhooks, opened 2026-10-16, WebFetch — Quote: "Our libraries have a default tolerance of 5 minutes between the timestamp and the current time."
- Retry horizon differs live vs sandbox — https://docs.stripe.com/webhooks, opened 2026-10-16, WebFetch — Quote: "Stripe attempts to deliver events to your destination for up to three days with an exponential back off in live mode."
- Sandbox retries are shorter — same page — Quote: "We retry event deliveries created in a sandbox three times over the course of a few hours."
- Webhook payload version pinned to account API version at event time — same page — Quote: "The API version in your account settings when the event occurs dictates the API version, and therefore the structure of an"
- Secret rotation overlap up to 24 h — same page — Quote: "You can choose to immediately expire the current secret or delay its expiration for up to 24 hours"
- Idempotency keys: saved result incl. errors, 24 h pruning, all POSTs — https://docs.stripe.com/api/idempotent_requests, opened 2026-10-16, WebFetch — Quote: "you can remove keys from the system automatically after they’re at least 24 hours old."
- Idempotency key reuse with different params errors — same page — Quote: "The idempotency layer compares incoming parameters to those of the original request and errors if they’re not the same"
- Google refresh-token traps: Testing status 7 days; unused 6 months; 100 per client — https://developers.google.com/identity/protocols/oauth2, opened 2026-10-16, WebFetch — Quote: "is issued a refresh token expiring in 7 days"; "The refresh token has not been used for six months."; "100 refresh tokens per Google Account per OAuth 2.0 client ID"
- Google consent screen: Testing is capped at 100 test users; unverified apps capped — https://support.google.com/cloud/answer/15549945, opened 2026-10-16, WebFetch — Quote: "are limited to up to 100 test users listed in the OAuth consent screen."
- Retry only transient errors, never blindly retry state-changing calls — https://google.aip.dev/194, opened 2026-10-16, WebFetch — Quote: "Clients should not automatically retry requests in which repeated runs would cause unintended state changes."
- AIP-194 marks UNAVAILABLE as the retryable code — same page — Quote: "This code generally results from network hiccups, and is generally transient."

### Contradictions
- None found.

### Inferences
- The checklist (mine, built from the above plus the per-service facts in Q2): 1 auth type; 2 token lifetime and rotation (store the NEW refresh token atomically); 3 scopes and who may grant them; 4 rate limit, window, 429 and Retry-After; 5 pagination and offset caps; 6 webhook signature and timestamp; 7 webhook retries, ordering, duplicates, and a reconciliation poll because delivery is not guaranteed; 8 idempotency for every write; 9 sandbox/test mode vs production; 10 API version pinning and deprecations; 11 plan or role gating (feature exists but not on John's plan); 12 data residency, ToS, automated-account rules.
- Rule for the engineer: any "no" on 2, 3 or 11 becomes a human setup step; any "no" on 7 means design a polling reconciler.

### Gaps
- Twilio, Shopify, Zapier, Postman and Microsoft REST API guidelines were not opened; no cited claim comes from them. No 2025-26 practitioner "integration checklist" page was opened.
- Data residency per service not researched (no service doc opened on it).
- Parallel `web_fetch` returned "Too Many Requests" at the start; fell back to WebFetch and Exa.

## Q2 Per-service facts

### Takeaway
All eleven have usable APIs, but the traps differ: WHOOP and Withings rotate refresh tokens (lose the new one and you lose access); Google tokens die in 7 days while the app is in Testing; Slack and Supabase/Vercel gate by plan or role; n8n API is unavailable on the free trial; Clay's public API is alpha/Enterprise for tables; Outreach production credentials need a review; Withings and Vercel offer no true sandbox. Confidence: medium (Cloudflare TTL, Vercel REST limit values, Clay auth/rate limits, Outreach webhooks signature, Withings webhook signing were not confirmed).

### Cited findings
**Attio**
- Rate limit 100 read/s, 25 write/s, 429 with Retry-After — https://docs.attio.com/rest-api/guides/rate-limiting, opened 2026-10-16, WebFetch — Quote: "Rate limit responses always have the HTTP status code 429."
- Webhook header and retries — https://docs.attio.com/rest-api/guides/webhooks, opened 2026-10-16, WebFetch — Quote: "retry delivery of the message up to 10 times with an exponential back-off."
- Webhook signature header `Attio-Signature`, 5 s timeout — same page — Quote: "a 5 second timeout on requests to your target URL"
- API key for one workspace vs OAuth for many; admin grants workspace-level tokens — https://docs.attio.com/rest-api/guides/authentication, opened 2026-10-16, WebFetch — Quote: "Only workspace admins can grant a workspace-level token."
**Clay**
- Webhook source cap 50,000 submissions, optional header token — https://university.clay.com/docs/webhook-integration-guide, opened 2026-10-16, WebFetch — Quote: "Webhook sources are limited to 50,000 submissions, and this limit persists even after deleting rows."
- Developer platform: tables Enterprise only — https://developers.clay.com/, opened 2026-10-16, WebFetch — Quote: "Tables are Enterprise only."
**n8n**
- API not on free trial; self-hosted all editions — https://docs.n8n.io/connect/n8n-api, opened 2026-10-16, WebFetch — Quote: "It isn't available on the free trial."
- API key created in Settings, header `X-N8N-API-KEY`, scopes Enterprise only — https://docs.n8n.io/connect/n8n-api/authentication.md, opened 2026-10-16, WebFetch — Quote: "Non-Enterprise API keys have full access to all the account's resources and capabilities."
**Outreach**
- Rate limit 10,000 requests/hour per user, 429 — https://developers.outreach.io/api/getting-started, opened 2026-10-16, WebFetch — Quote: "The Outreach API is generally rate-limited on a per-user basis, with a limit of 10,000 requests per hour."
- Dev credentials immediate, production after review; access token `expires_in` 7200 — https://developers.outreach.io/api/oauth/, opened 2026-10-16, WebFetch (page text paraphrased by tool; no verbatim quote returned) — Quote: "you need to create an Outreach app"
**WHOOP**
- `offline` scope required for refresh token; refresh rotates both tokens — https://developer.whoop.com/docs/developing/oauth, opened 2026-10-16, WebFetch — Quote: "Existing access tokens are invalidated once your app uses the refresh token to generate a new access token."
- Rate limit 100/min, 10,000/day, 429 — https://developer.whoop.com/docs/developing/rate-limiting, opened 2026-10-16, WebFetch — Quote: "100 requests per minute."
- Webhooks: `X-WHOOP-Signature` + timestamp, 5 retries over ~1 hour, may be missed — https://developer.whoop.com/docs/developing/webhooks, opened 2026-10-16, WebFetch — Quote: "WHOOP will retry webhook delivery for failed webhook requests **five times over the course of about one hour**." and "It is possible that a webhook may be missed."
**Withings**
- Access token 3 h, refresh token 1 year, rotation, old token valid 8 h; code 30 s; poll no more than every 10 min; demo mode only — https://developer.withings.com/llms.md, opened 2026-10-16, WebFetch — Quote: "Do not poll more than once every 10 minutes per user"; "Add `&mode=demo` to test without a real device."
- Public API needs no contract — same page — Quote: "No contract required"
- Page states nothing about webhook retries or signing — same page (negative; tool summary: "says nothing about retries or signature verification for webhooks").
**Slack**
- Tier rate limits, Retry-After; 2025 limits on conversations.history/replies for new non-Marketplace commercial apps — https://docs.slack.dev/apis/web-api/rate-limits, opened 2026-10-16, WebFetch — Quote: "Existing installations of apps that are not Marketplace-approved are not subject to the new posted limits."
- Signing secret, 5-minute window — https://docs.slack.dev/authentication/verifying-requests-from-slack, opened 2026-10-16, WebFetch — Quote: "we verify that the timestamp does not differ from local time by more than five minutes."
- Token rotation optional but irreversible; 12 h expiry — https://docs.slack.dev/authentication/tokens, opened 2026-10-16, WebFetch — Quote: "Token rotation may not be turned off once it's turned on."
- `apps.manifest.create` needs an app configuration token — https://docs.slack.dev/reference/methods/apps.manifest.create, opened 2026-10-16, WebFetch — Quote: "An app configuration access token."
**Cloudflare**
- Global limit 1,200 requests/5 min per user, then 5-minute block — https://developers.cloudflare.com/fundamentals/api/reference/limits/, opened 2026-10-16, WebFetch — Quote: "The global rate limit for the Cloudflare API is 1,200 requests per five minute period per user."
- Token secret shown once; scoped by permission and resource; verify endpoint — https://developers.cloudflare.com/fundamentals/api/get-started/create-token/, opened 2026-10-16, WebFetch — Quote: "The token secret is only shown once."
- First account sign-up is email+password with email verification; account-owned tokens cannot create accounts — https://developers.cloudflare.com/fundamentals/account/create-account/, opened 2026-10-16, WebFetch — Quote: "Account-owned API tokens cannot create accounts."
**Vercel**
- Account webhooks only on Pro and Enterprise; secret shown once; `x-vercel-signature` — https://vercel.com/docs/webhooks, opened 2026-10-16, WebFetch — Quote: "Account Webhooks are available on Enterprise and Pro plans"
- Rate limits are per named limit with window and scope (e.g. 60 domain deletes/min) — https://vercel.com/docs/limits, opened 2026-10-16, WebFetch (persisted output, grep) — Quote: "Once a rate limit is hit, it will be reset after the **Duration** has expired."
**Supabase**
- Management API 120 calls/min per user/project/endpoint; PATs have custom expiry; OAuth tokens short-lived — https://supabase.com/docs/reference/api/introduction, opened 2026-10-16, WebFetch — Quote: "PATs are tokens with a custom expiry that you manually generate to access the Management API."
- Legacy anon/service_role deprecated by end of 2026 — https://supabase.com/docs/guides/api/api-keys, opened 2026-10-16, WebFetch — Quote: "Supabase is deprecating the `anon` and `service_role` keys by the end of 2026."
- Secret key bypasses RLS — same page — Quote: "It bypasses Row Level Security, so it must never leave your control."
- Database webhooks: async via pg_net; page says nothing on retries or signing — https://supabase.com/docs/guides/database/webhooks, opened 2026-10-16, WebFetch — Quote: "This extension is asynchronous, and therefore will not block your database changes for long-running network requests."
**Google OAuth** — see Q1 (7-day Testing refresh token, 100 test users, 6-month idle expiry).

### Contradictions
- None found. (An earlier finding in engineer-existing-systems.md line 422 notes an Attio scope-quote mismatch; not re-tested here.)

### Inferences
- Integration card, one row per service (mine): auth / lifetime / limit / webhook signing / test mode / gotcha. WHOOP, Withings and Slack-with-rotation need a token store written on every refresh; the engineer should write that as a requirement, not leave it to the code.
- Google OAuth: John should move the consent screen to "In production" (his own app, single user, unverified warning acceptable) or the refresh token dies weekly. This rests on the 7-day rule above; the sensitive-scope verification need depends on the scopes, which I did not test.
- Withings and WHOOP are single-user health feeds; plan a poll-based reconciler (Withings: >=10 min per user; WHOOP: webhooks may be missed).

### Gaps
- Not confirmed from an opened page: Clay API auth method and rate limit; Outreach webhook signing and refresh-token rotation; Attio token expiry; Cloudflare token TTL values; Vercel REST access-token expiry; Withings webhook retry/signing; Slack Events API retry rules; n8n API key expiry options and rate limit; sandbox existence for Attio, Clay, Outreach, Slack (Slack developer sandbox not opened).
- Vercel `/docs/rest-api` page was opened but yielded only an endpoint list.

## Q3 Turning a design into an ordered human setup list; agent vs human steps

### Takeaway
Order by dependency: (1) human identity/billing accounts, (2) org/workspace roles and plan tier, (3) app registration (agent can prefill; some via API such as Slack manifests), (4) consent/OAuth clicks as the account owner, (5) secrets to the vault, (6) automated verification call. Browser agents may do the form-filling and navigation but must stop at CAPTCHA, login, 2FA, passkey and payment; Claude in Chrome does this by design. Confidence: medium (evidence for the pause-points is primary for Claude in Chrome, secondary/practitioner for the rest; no Terraform or infra-README bootstrap page was opened).

### Cited findings
- Claude in Chrome pauses on login and CAPTCHA — https://code.claude.com/docs/en/chrome, opened 2026-10-16, WebFetch — Quote: "When Claude encounters a login page or CAPTCHA, it pauses and asks you to handle it manually."
- Claude in Chrome refuses credential-named files for upload — same page — Quote: "Claude refuses a file whose name or folder is one that credentials are kept under, such as `.env`, a `.pem` or `.key` file"
- Chrome integration is off under API key / setup-token auth — same page — Quote: "Claude Code keeps Chrome integration off, even when you pass `--chrome`"
- Practitioner handoff record (secondary source, 2026-10-01): four parts — https://launchrepo.dev/guides/ai-agent-captcha-2fa-handoffs/, opened 2026-10-16, WebFetch — Quote: "records a handoff with four parts: what it saw, the one action you take, where you take it, and the signal that lets it continue."
- Same source: some platforms ban bot-created accounts — Quote: "Accounts registered by "bots" or other automated methods are not permitted." (it is a table row quoting a platform term, not a named platform).
- Cloudflare: first account is human email+password, verify email; additional Free accounts need an existing Super Administrator — https://developers.cloudflare.com/fundamentals/account/create-account/, opened 2026-10-16, WebFetch — Quote: "You must have the Super Administrator role on an existing account."
- Supabase-on-Vercel marketplace install is a single click that creates the project and syncs env vars, owner role given to the installing user — https://supabase.com/docs/guides/integrations/vercel-marketplace, opened 2026-10-16, WebFetch — Quote: "Both create a Supabase project and sync the following environment variables to your connected Vercel projects:"
- Attio: workspace-level tokens need an admin, so the human must hold the admin role — https://docs.attio.com/rest-api/guides/authentication, opened 2026-10-16, WebFetch — Quote: "Only workspace admins can grant a workspace-level token."
- n8n API key: create in UI Settings, copy once — https://docs.n8n.io/connect/n8n-api/authentication.md, opened 2026-10-16, WebFetch — Quote: "Copy **My API Key** and use this key to authenticate your calls."
- Requirement R11/R12 context: local file /home/user/Autonomy-Research/research/requirements/autonomous-engineer.md:105-110 (read via grep) — Quote: "R11 When the plan is approved, the engineer shall produce one ordered setup list (accounts,"

### Contradictions
- None found.

### Inferences
- Human-only steps (mine, from the pause-points above): first account creation per vendor (email verification, possible identity checks), billing/plan upgrade (n8n API needs paid cloud or self-host; Vercel webhooks need Pro; Clay Tables need Enterprise), OAuth consent as the data owner (WHOOP, Withings, Google, Slack install, Outreach), 2FA enrolment, copy-once secrets (Cloudflare, Vercel webhook secret, n8n key).
- Agent-doable with John's session open (local Claude in Chrome): navigate to the right settings page, prefill app names/redirect URIs/scopes, create Slack apps from a manifest, run verification calls after secrets exist, rotate/verify tokens.
- Cloud sessions cannot use the browser; Chrome integration needs local `/login` (Chrome page). So the setup session is local.
- Secrets: John pastes into the vault/env himself; the agent never reads them (aligns with Claude in Chrome's refusal of credential files).
- Example dependency order for John: Google Cloud project -> consent screen to production -> OAuth client -> consent click -> store token; Cloudflare account -> API token (scoped) -> verify endpoint; Vercel team (Pro if webhooks) -> token; Supabase via Vercel marketplace or own org -> PAT; Slack workspace admin -> app via manifest -> install -> bot token + signing secret; Attio admin -> API key; n8n (self-host) -> API key; WHOOP/Withings developer apps -> redirect URI -> consent; Outreach dev app -> production review wait (start first, it blocks longest); Clay -> check plan.

### Gaps
- No Terraform provider prerequisite page, infrastructure bootstrap README or "one-time setup script" example was opened; the Cloudflare Terraform tutorial and a Cloudflare provider page appeared only as search excerpts.
- Identity checks: no opened page establishes that any of John's eleven services requires ID verification at signup; Cloudflare, n8n, Attio, Supabase signup requirements not confirmed beyond Cloudflare email+password.
- No legal source opened on ToS bans of agent-created accounts for specific services.
- Time per step is unmeasured (see Q4).

## Q4 Presenting the list for one sitting

### Takeaway
Present one page grouped by service in dependency order, each item as: what you do, where (URL), how long, what you hand back (secret name, never value), and a one-command verification the agent runs afterwards; put long-wait items (Outreach production review, Google verification) first as "start now, finish later". Confidence: low-medium (design inference from the handoff pattern and the requirements; no source on time estimates).

### Cited findings
- Handoff record that maps to one checklist row: "what it saw, the one action you take, where you take it, and the signal that lets it continue" — https://launchrepo.dev/guides/ai-agent-captcha-2fa-handoffs/, opened 2026-10-16, WebFetch — Quote: "records a handoff with four parts: what it saw, the one action you take, where you take it, and the signal that lets it continue."
- Cloudflare gives a built-in verification call — https://developers.cloudflare.com/fundamentals/api/get-started/create-token/, opened 2026-10-16, WebFetch — Quote: "The token secret is only shown once."  (and the page names the `/user/tokens/verify` endpoint as the check)
- Requirement G4/R12 context: /home/user/Autonomy-Research/research/requirements/autonomous-engineer.md:29 (read via grep) — Quote: "G4 Minimal manual setup."

### Contradictions
- None found.

### Inferences
- Row format (mine): `[ ] 4. Slack -- create app from manifest (agent prepares) -- you click Install as workspace admin -- 3 min -- paste bot token + signing secret into vault names SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET -- verify: auth.test returns ok`.
- Group order: Start-now waits (Outreach, Google consent-screen verification if needed) -> one local session with Claude in Chrome open and signed in -> services by dependency -> final "agent verifies all" step with a pass/fail table and the first failing row named.
- Time estimates must be labelled estimates until John's first run; capture actual minutes in the spike and feed them back.
- Expected cost of the sitting: 11 services x about 3-10 minutes each, so likely 45-90 minutes (my estimate, not sourced).

### Gaps
- No source found on time estimates for these setups; none on checklist UX research.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Claude in Chrome (re-check for setup session) | https://code.claude.com/docs/en/chrome | Pauses on login/CAPTCHA, asks the user | local | 2026-10-16 | Use for the setup session only (local, `/login` auth); human does consent/2FA |
| Stripe webhook + idempotency docs (reference) | https://docs.stripe.com/webhooks | Reference rules for checklist points 6-8 | docs | 2026-10-16 | Use as the reference pattern |
| Google AIP-194 (retry guidance) | https://google.aip.dev/194 | Which errors to retry | docs | 2026-10-16 | Reference; thin on backoff |
| Slack apps.manifest.create | https://docs.slack.dev/reference/methods/apps.manifest.create | Create a Slack app from a manifest with a config token | hosted | 2026-10-16 | Use; install still needs admin click |
| Cloudflare Terraform provider | https://developers.cloudflare.com/api/terraform/ | IaC for Cloudflare, token auth | local | not opened (search excerpt only) | Candidate for DNS/config; spike |
