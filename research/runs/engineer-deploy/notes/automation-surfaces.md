# Automation surfaces for GTM and health flows

Brief: Decide where an autonomous Claude Code engineer should run scheduled and event-driven automations (GTM enrichment/sync, health reminders/device syncs) and how it deploys them unattended.
Run: research/runs/engineer-deploy/PLAN.md

## n8n self-hosted vs Cloud
### Takeaway
Self-host n8n (Docker, Postgres, one VM) if John wants visual flows; Cloud Starter (20 EUR/mo billed annually, 2.5K executions) is workable but small. The public API and instance MCP exist on Cloud paid plans and all self-hosted editions, not the free trial; git source control is Business/Enterprise only, so on Community the engineer must version workflows by exporting JSON to git itself. Confidence: medium (no first-hand test; Cloud monthly price and Cloud-MCP plan gating not confirmed).

### Cited findings
- API availability: Cloud Starter, Pro, Enterprise and all self-hosted; not the free trial — https://docs.n8n.io/connect/n8n-api, opened 2026-10-16, WebFetch — Quote: "It isn't available on the free trial."
- Self-hosted API can be switched off by env var, default on — https://docs.n8n.io/hosting/configuration/environment-variables/deployment/, opened 2026-10-16, WebFetch — Quote: "Whether to disable the public API (true) or not (false)."
- Licence permits internal business use; ".ee." files need Enterprise licence — https://github.com/n8n-io/n8n/blob/master/LICENSE.md, opened 2026-10-16, WebFetch — Quote: "You may use or modify the software only for your own internal business purposes or for non-commercial or personal use."
- Cloud pricing/limits (annual billing): Starter 20 EUR, 2.5K executions, 5 min max duration; Pro 50 EUR, 10K, 40 min — https://n8n.io/pricing/, opened 2026-10-16, WebFetch — Quote: "Starter | 20€/mo | 2.5K" (tool-rendered table row; page summary, not raw text)
- Git source control is Business/Enterprise only; Community lacks it — https://docs.n8n.io/source-control-environments/, opened 2026-10-16, WebFetch — Quote: "Available on Business and Enterprise plans."
- Community lacks environments and Git — https://docs.n8n.io/hosting/community-edition-features/, opened 2026-10-16, WebFetch — Quote: "These features are available on self-hosted Business and Enterprise plans."
- Instance-level MCP can create/edit workflows (n8n 2.13.0+), only workflows flagged "Available in MCP"; enabled by owner/admin; OAuth or API key — https://docs.n8n.io/advanced-ai/mcp/accessing-n8n-mcp-server/, opened 2026-10-16, WebFetch — Quote: "Create and edit workflows and data tables."
- Self-hosted failure modes: SQLite default, OOM on large payloads, unbounded execution history, unrestored backups/encryption key — https://www.stackledge.com/blog/self-hosting-n8n-in-production-what-breaks, published 2026-08-05, from Exa search highlights (page not separately opened) — Quote: "Postgres from day one, never SQLite" (treat as secondary).
- Queue mode main-process leak, open issue — https://github.com/n8n-io/n8n/issues/37342, Exa highlights — Quote: "Main process leaks off-heap memory until OOMKill in queue mode (~40 MiB/s), workers unaffected" (single-reporter, 178 workflows; irrelevant at one-VM regular mode scale).
- v2 queue-mode stalls report — https://community.n8n.io/t/after-upgrading-n8n-self-hosted-to-v2-x-queue-mode-reliability-much-worse/247235 , Exa highlights — Quote: "execution error rates from like (1-2% on v1.x) to like (5-20% on v2.x)" (user report).

### Contradictions
- None found.

### Inferences
- Without Business licence, git version control = a scheduled export (n8n CLI export / API GET workflows) committed by the engineer; credentials must be recreated by id references, never exported decrypted (registry: n8n CLI export). Rests on source-control and Community-features findings.
- Single-instance regular mode with Postgres avoids the queue-mode issues above; John's flows are low volume.

### Gaps
- Whether Cloud MCP/API creation of credentials works with secrets write-only — not tested; spike on a throwaway self-hosted container, not John's account.
- Cloud monthly (non-annual) price and whether Cloud Starter has MCP build tools — pricing page shows annual only.
- Sustainable Use License page on docs.n8n.io returned "Page Not Found" (used GitHub LICENSE.md instead). Reselling/hosting-for-others limits only seen via the "internal business purposes" clause.

## Code-first alternatives
### Takeaway
For unattended agent deployment, plain code on the VM (systemd timers) plus Cloudflare Workers (free cron + HTTPS) cover almost everything free; GitHub Actions schedules suit repo-bound jobs but drift and auto-disable. Trigger.dev, Inngest and Windmill add durable retries and a dashboard but are only needed if flows are long or multi-step. Confidence: medium.

### Cited findings
- GitHub Actions: 5-minute minimum, delays under load, auto-disable after 60 days without repo activity (public repos), default branch only — https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows, opened 2026-10-16, WebFetch — Quote: "In a public repository, scheduled workflows are automatically disabled when no repository activity has occurred in 60 days."
- Same page on drift — Quote: "The `schedule` event can be delayed during periods of high loads of GitHub Actions workflow runs."
- Cloudflare Workers Free: 100k requests/day, 10 ms CPU, 5 cron triggers, 50 subrequests — https://developers.cloudflare.com/workers/platform/limits/, opened 2026-10-16, WebFetch — Quote: "Accounts on the Workers Free plan have a daily request limit of 100,000 requests, resetting at midnight UTC." (tool paraphrased the other numbers; 10 ms CPU, 5 triggers as reported by the fetch tool.)
- Cloudflare cron: UTC, config in wrangler `triggers.crons`, local test route — https://developers.cloudflare.com/workers/configuration/cron-triggers/, opened 2026-10-16, WebFetch — Quote: "This exposes a `/cdn-cgi/local/scheduled` route, which can be used to test using an HTTP request."
- Cloudflare cron changes can lag — Quote: "may take several minutes (up to 15 minutes) to propagate to the Cloudflare global network."
- Supabase cron (pg_cron) calls Edge Functions; 10-min job guidance — https://supabase.com/docs/guides/cron, opened 2026-10-16, WebFetch — Quote: "Each Job should run no more than 10 minutes."
- Supabase edge function limits: free 150 s wall clock, 2 s CPU — https://supabase.com/docs/guides/functions/limits, opened 2026-10-16, WebFetch — Quote: "If an Edge Function doesn't send a response before the timeout, 504 Gateway Timeout will be returned."
- systemd timers catch up missed runs with Persistent= — https://man7.org/linux/man-pages/man5/systemd.timer.5.html, opened 2026-10-16, WebFetch — Quote: "the service unit is triggered immediately if it would have been triggered at least once during the time when the timer was inactive."
- Trigger.dev free: $5 monthly credit, 20 concurrent runs, 10 schedules, 1-day logs; Apache 2.0 self-hostable — https://trigger.dev/pricing, opened 2026-10-16, WebFetch — Quote: "you'll need to upgrade to keep running tasks" (as rendered by the fetch tool)
- Inngest free: 50k executions/mo, 5 concurrent, 24 h trace history — https://www.inngest.com/pricing, opened 2026-10-16, WebFetch — Quote: "50k /mo included"
- Windmill community self-hosted: unlimited executions, 3 workspaces, git sync up to 2 users; "Commercial licence" No; licence not named on page — https://www.windmill.dev/pricing, opened 2026-10-16, WebFetch — Quote: "Unlimited"

### Contradictions
- None found. (Tool-paraphrased quotes above should be spot-checked before they drive a purchase.)

### Inferences
- Agent deployability ranking (my judgement): systemd timer + script in git (agent writes unit file, tests with `systemd-run`/manual start) > Cloudflare Worker (wrangler deploy, local `/cdn-cgi/local/scheduled` test) > GitHub Actions (workflow file in PR, test via workflow_dispatch) > Supabase (SQL migration + edge function) > Trigger.dev/Inngest/Windmill (extra service and SDK). Rests on the cited testing hooks and limits.
- Cloudflare's 10 ms CPU on Free is enough for I/O-bound API sync but not for heavy parsing; long enrichment batches belong on the VM or GitHub Actions.
- Temporal: not researched; for one user it is over-built (my judgement, uncited).

### Gaps
- Temporal, Trigger.dev and Inngest retry semantics/observability not opened beyond pricing pages.
- Windmill licence text (AGPL claimed in memory) not verified.
- GitHub Actions free-minute figures: docs URL returned 404.
- Trigger.dev/Inngest cron drift not tested.

## Webhook receivers
### Takeaway
Receivers must answer fast (Attio 5 s, WHOOP about 1 s) over HTTPS on a real domain; Withings also needs ports 80/443 and HEAD support. Cheapest stable endpoint: a Cloudflare Worker that verifies the signature, enqueues/forwards and returns 2xx, or a Cloudflare Tunnel from the VM (outbound-only, no public IP). Confidence: medium-high.

### Cited findings
- Attio: HTTPS only, HMAC-SHA256 `Attio-Signature`, 5 s timeout, 10 retries over about 3 days — https://docs.attio.com/rest-api/guides/webhooks, opened 2026-10-16, WebFetch — Quote: "Attio will retry delivery of the message up to 10 times with an exponential back-off."
- Attio timeout — Quote: "Attio also enforces a 5 second timeout on requests to your target URL."
- WHOOP: HTTPS endpoint, signature headers, retries five times over about an hour, respond within a second — https://developer.whoop.com/docs/developing/webhooks, opened 2026-10-16, WebFetch — Quote: "WHOOP will retry webhook delivery for failed webhook requests five times over the course of about one hour."
- WHOOP events: workout/sleep/recovery updated|deleted — same URL — Quote: "Enum: "workout.updated" "workout.deleted" "sleep.updated" "sleep.deleted" "recovery.updated" "recovery.deleted""
- Withings: 10 attempts over about 5 h, missed notifications not redelivered (backfill with lastupdate) — https://developer.withings.com/developer-guide/v3/data-api/notifications/notification-overview/, opened 2026-10-16, WebFetch — Quote: "Missed notifications are not redelivered. Once your endpoint is back up, backfill via the Data API using lastupdate."
- Withings URL rules (HTTPS, no IPs, ports 80/443, HEAD) — https://developer.withings.com/developer-guide/v3/data-api/notifications/notification-subscribe/ , Exa search highlights only (page not separately opened) — Quote: "HTTPS only — plain HTTP URLs are not accepted"
- Cloudflare Tunnel is outbound-only and needs no public IP — https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/, opened 2026-10-16, WebFetch — Quote: "creates outbound-only connections to Cloudflare's global network"
- n8n Cloud/self-hosted webhooks work with n8n's `WEBHOOK_URL` behind a reverse proxy (queue-mode docs) — https://docs.n8n.io/deploy/host-n8n/configure-n8n/scaling/enable-queue-mode, Exa highlights — Quote: "The main n8n instance handles timers and webhook calls, generating (but not running) a workflow execution."

### Contradictions
- Withings page: retry when response not "HTTP < 400" vs "return HTTP 2xx within a few seconds" — same overview URL; spike with a test subscription.

### Inferences
- A Worker receiver that stores the raw event (KV/D1/Queue) or forwards to the VM then returns 2xx stays within WHOOP's 1 s limit and survives VM downtime; WHOOP and Attio retry, Withings does not redeliver after 5 h so a daily backfill poll is required. Slack not researched (Slack requires 3 s ack; uncited).
- n8n Webhook node is an acceptable receiver only when n8n is already behind HTTPS; it adds n8n downtime to the retry budget.

### Gaps
- Slack Events API ack rules not opened.
- Cloudflare Tunnel pricing: page does not state it; not confirmed free.
- Cloudflare Queues/D1/KV free limits not opened.

## Choosing rule
### Takeaway
Keep a flow in n8n when it is mostly glue between built-in nodes, John wants to see/edit it, and failure is cheap. Move to code when it needs tests, git review, signature-verified webhooks with strict latency, or loops over many records. The agent should not build in n8n when it cannot version/test the result (no Business git, no API on Cloud trial), or when the flow is long-running/high-volume. Confidence: medium (judgement built on findings above).

### Cited findings
See sections above (API availability, no Community git, MCP flagging requirement, webhook timeouts).

### Contradictions
- None found.

### Inferences
- Rule: (1) Existing John-visible n8n flow, low volume, built-in nodes -> leave in n8n; agent edits via instance MCP/API only after an exported JSON copy is committed to git. (2) New flow with Attio/Clay/WHOOP/Withings custom auth, retries, backfill, tests -> code (TypeScript/Python) in a repo; schedule on systemd timer (VM) or Cloudflare cron; receiver on a Worker. (3) Never in n8n: webhook handlers with <=1-5 s deadlines unless n8n is always up; health data pipelines needing auditable diffs; anything on the n8n free trial (no API). (4) Add Trigger.dev/Inngest only if a job needs durable multi-step retries beyond a script's resume logic.
- Recommendation: code-first on the VM (systemd timers + git) and a Cloudflare Worker for webhooks; keep n8n self-hosted (Docker + Postgres) for John's existing visual flows with nightly JSON export to git.

### Gaps
- Spike before building: (a) create/update workflow and credential through n8n API/MCP on a throwaway self-hosted container; (b) Worker receiving a real WHOOP and Withings test event with HMAC check; (c) systemd Persistent= catch-up after VM reboot; (d) GitHub Actions schedule drift measurement; (e) Withings response-code contract.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| n8n self-hosted (Community) | https://github.com/n8n-io/n8n | Visual workflow engine, Docker; Sustainable Use Licence (internal business use); API on; no git/environments | VM/VPS | 2026-10-16 | Keep for John's visual flows; Postgres, pruning, export-to-git |
| n8n Cloud | https://n8n.io/pricing/ | Hosted n8n; Starter 20 EUR/mo annual, 2.5K executions; API not on trial | cloud | 2026-10-16 | Fallback; small quota, paid |
| n8n instance MCP | https://docs.n8n.io/advanced-ai/mcp/accessing-n8n-mcp-server/ | Build/edit workflows from an MCP client, flagged workflows only | n8n 2.13+ | 2026-10-16 | Use after spike |
| Cloudflare Workers cron + webhooks | https://developers.cloudflare.com/workers/platform/limits/ | Free 100k req/day, 5 crons, 10 ms CPU | cloud | 2026-10-16 | Use for webhook receivers and light cron |
| Cloudflare Tunnel | https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/ | Outbound-only tunnel exposing VM service | VM | 2026-10-16 | Option for VM-hosted receivers; price unverified |
| GitHub Actions schedule | https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows | Cron >=5 min, delays, 60-day auto-disable on public repos | GitHub | 2026-10-16 | Fallback for repo-bound jobs |
| Supabase pg_cron + edge functions | https://supabase.com/docs/guides/cron | SQL cron, HTTP to edge functions, 150 s free wall clock | cloud | 2026-10-16 | Use only if data already in Supabase |
| systemd timers | https://man7.org/linux/man-pages/man5/systemd.timer.5.html | Persistent= catch-up | VM | 2026-10-16 | Use: default scheduler on the VM |
| Trigger.dev | https://trigger.dev/pricing | Durable tasks, Apache 2.0, $5 free credit, 10 schedules | cloud/self-host | 2026-10-16 | Fallback if durable retries needed |
| Inngest | https://www.inngest.com/pricing | Durable functions, 50k exec/mo free | cloud | 2026-10-16 | Fallback |
| Windmill | https://www.windmill.dev/pricing | Scripts+flows, free self-host, unlimited execs | self-host | 2026-10-16 | Fallback; licence unverified |
| Temporal | (not opened) | Durable workflow engine | - | not opened | Reject for one user; not researched |
