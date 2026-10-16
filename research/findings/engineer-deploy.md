# Engineer deploy: how an autonomous Claude Code engineer deploys web apps, automations and Android apps unattended, free tiers first

**Summary.** The notes support a split by workload, driven by platform CLIs with narrow tokens rather than by
OAuth MCP servers. Static and edge web projects go to Cloudflare Workers, whose Free plan has "a daily request
limit of 100,000 requests" (https://developers.cloudflare.com/workers/platform/limits/) and whose `wrangler`
reads an API token from the environment "for situations like CI/CD, and other automation"
(https://developers.cloudflare.com/workers/wrangler/system-environment-variables/). Container APIs go to Cloud
Run with `gcloud run deploy SERVICE --source .`, which "uses a Dockerfile if present, although it's not
required" (https://docs.cloud.google.com/run/docs/deploying-source-code), on a free tier that starts with
"First 180,000 vCPU-seconds free per month" (https://cloud.google.com/run/pricing). Always-on processes stay on
a VM: Fly.io requires that "you'll need to add a credit card to keep using billable resources"
(https://docs.fly.io/about/pricing), Railway's free plan is "$1 of free credit per month"
(https://docs.railway.com/pricing/plans) and "Free Render Postgres databases expire 30 days after creation"
(https://render.com/docs/free). John's health app already runs this way, on one GCP VM with Docker Compose and
`cloudflared` (/home/user/health-management/docs/architecture.md:8-10) where "Cloudflare Access lets only
John's Google account through" (/home/user/health-management/docs/architecture.md:9-10). Vendor MCP servers
such as Vercel's are "a remote MCP with OAuth" (https://vercel.com/docs/agent-resources/vercel-mcp), so the
worker inference is that CLI plus a scoped token is the unattended path. Automations go code-first: systemd
timers that catch up missed runs (https://man7.org/linux/man-pages/man5/systemd.timer.5.html) and Cloudflare
Worker cron and webhook receivers (https://developers.cloudflare.com/workers/configuration/cron-triggers/),
with self-hosted n8n kept for John's visual flows, because n8n Git source control is "Available on Business and
Enterprise plans" (https://docs.n8n.io/source-control-environments/) and its API "isn't available on the free
trial" (https://docs.n8n.io/connect/n8n-api). Android goes PWA first, with a Gradle-built wrapper only when an
app needs native APIs such as Health Connect, which is added as a Gradle SDK dependency
(https://developer.android.com/health-and-fitness/health-connect/get-started), and installs to John's phone by
ADB, which needs no verification (https://developer.android.com/developer-verification/guides/faq). The Play
Store waits behind a US$25 fee (https://support.google.com/googleplay/android-developer/answer/6112435) and a
closed test of "a minimum of 12 testers" for "at least 14 days"
(https://support.google.com/googleplay/android-developer/answer/14151465). iOS stays deferred at "99 USD per
membership year" (https://developer.apple.com/programs/whats-included/). For operations, secrets are piped
from a vault CLI into setters that accept stdin
(https://developers.cloudflare.com/workers/wrangler/commands/workers/), preview comes first and production is
gated by a human approval
(https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/review-deployments),
rollback is one command but "Resources connected to your Worker will not be changed during a rollback"
(https://developers.cloudflare.com/workers/configuration/versions-and-deployments/rollbacks/), free uptime
checks alert John (https://uptimerobot.com/pricing/, https://healthchecks.io/pricing/), and money is spent
through a two-step gate copied from Vercel's domain flow, "Only after a human approves"
(https://vercel.com/docs/cli/domains). Confidence is medium: most figures come from WebFetch extracts, nothing
was spiked, and 26 claims backed only by search highlights or by no source were excluded (see Open questions).

## Questions and answers

### Q1. Deploy matrix: which platform for which project type, and how the engineer deploys unattended

**Confidence: medium.** The matrix is the web-hosting worker's proposal (a worker inference); each cell's cited
fact carries its URL. Where a command or variable name is not in a quoted line it is marked.

| Project type | Platform, free tier first | Unattended deploy and token | Cited facts |
| --- | --- | --- | --- |
| Static site or SPA | Cloudflare Workers static assets, or Cloudflare Pages | Worker inference (not in the source): `wrangler deploy` with `CLOUDFLARE_API_TOKEN` | Wrangler takes an account API token for "CI/CD, and other automation" (https://developers.cloudflare.com/workers/wrangler/system-environment-variables/); SPA fallback returns "`index.html` for requests which don't match a static asset" (https://developers.cloudflare.com/workers/static-assets/); Pages allows "up to 20,000 files on the Free plan" (https://developers.cloudflare.com/pages/platform/limits/) |
| Edge API with a small database | Workers plus D1 and R2 | as above | D1 "5 million / day" (https://developers.cloudflare.com/d1/platform/pricing/); R2 "10 GB-month / month" (https://developers.cloudflare.com/r2/pricing/) |
| Next.js or SSR needing Vercel features, personal only | Vercel Hobby | Vercel CLI with `VERCEL_ORG_ID` and `VERCEL_PROJECT_ID` "to skip project linking" (https://vercel.com/docs/cli/global-options); Worker inference (not in the source): the token variable `VERCEL_TOKEN` and the `--non-interactive` flag are in the note's claim but not its quote | "non-commercial, personal use only" (https://vercel.com/docs/plans/hobby) |
| Postgres app with auth and storage | Supabase Free, or Neon Free plus own auth | `supabase link`, `supabase db push` with "`SUPABASE_ACCESS_TOKEN` ... a scoped personal access token" (https://supabase.com/docs/guides/deployment/managing-environments); Neon deploy flow not opened | "You are granted two free projects." (https://supabase.com/docs/guides/platform/billing-on-supabase); Neon "100 CU-hours/project/month" (https://neon.com/docs/introduction/plans) |
| Container API that can scale to zero | Google Cloud Run in John's GCP project | `gcloud run deploy SERVICE --source .` (https://docs.cloud.google.com/run/docs/deploying-source-code); Worker inference (not in the source): a service account through GitHub OIDC and Workload Identity Federation, the pattern John's repo already uses (/home/user/health-management/docs/design/ops.md:40-43) | "First 180,000 vCPU-seconds free per month" (https://cloud.google.com/run/pricing) |
| Always-on bot, queue worker, Slack Socket Mode, n8n | The existing VM with Docker Compose behind Cloudflare Tunnel | John's `deploy.sh` pattern: CI gate, migrate, probe `/healthz`, auto-rollback (/home/user/health-management/docs/design/ops.md:44-48) | Tunnel "creates outbound-only connections" (https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/); no free always-on PaaS found (Fly https://docs.fly.io/about/pricing, Railway https://docs.railway.com/pricing/plans, Render https://render.com/docs/free) |
| Paid container plus Postgres, if the VM is not wanted | Railway Hobby | Railway project token, which is "scoped to a specific environment and can only perform deployment-related actions" (https://docs.railway.com/cli/deploying) | Worker inference (not in the source): Hobby is $5/month |
| Scheduled jobs, webhook receivers | systemd timers on the VM; Worker cron and Worker receivers | see Q5 and Q6 | |
| Android app | PWA; Capacitor or Gradle wrapper when native APIs are needed | see Q7 | |

**How Claude Code users deploy today.** Vercel MCP "is a remote MCP with OAuth"
(https://vercel.com/docs/agent-resources/vercel-mcp) that "can now deploy code directly to a new or existing
project" (https://vercel.com/changelog/vercel-mcp-can-now-deploy-code), and Vercel itself says "Always enable
human confirmation in your workflows" (https://vercel.com/docs/agent-resources/vercel-mcp). Supabase MCP has
feature groups, of which "All groups except Storage are enabled by default"
(https://supabase.com/docs/guides/getting-started/mcp); the worker's claim adds a `read_only=true` flag,
`project_ref` scoping and a `deploy_edge_function` tool, and Supabase warns "you should always review the
output before proceeding" (same URL). Cloudflare's MCP servers each need "an API token that has the scopes
(permissions) required for that particular MCP server" (https://github.com/cloudflare/mcp-server-cloudflare).
Netlify offers an MCP server "which you can connect to through a connector, plugin, or your agent"
(https://docs.netlify.com/build/build-with-ai/netlify-mcp-server/). Worker inference: an unattended engineer
cannot complete a browser OAuth flow, so it deploys with the CLI and a token in the environment, a PreToolUse
hook limits which deploy commands run, and MCP servers are used read-only for logs and status. Claims about the
Vercel, Cloudflare, Netlify and Supabase Claude Marketplace plugins rested on search highlights only and are
excluded (Open questions).

**Contradictions.** Cloudflare Pages has its own Free limits page
(https://developers.cloudflare.com/pages/platform/limits/) while Workers can serve static assets in one deploy
(https://developers.cloudflare.com/workers/static-assets/); the web-hosting note found that neither page ranks
the two. Unresolved, and listed as a spike.

### Q2. Free-tier limits and traps

**Confidence: medium.** Quoted values carry URLs; other values the workers' fetch extracts reported are marked.

- **Cloudflare Workers:** the 100,000-request daily cap resets "at midnight UTC"
  (https://developers.cloudflare.com/workers/platform/limits/). Worker inference (not in the source): 10 ms CPU,
  100 Workers per account, 5 cron triggers and 50 subrequests, as reported by the fetch tool. Cron changes "may
  take several minutes (up to 15 minutes) to propagate"
  (https://developers.cloudflare.com/workers/configuration/cron-triggers/). Free build limits were not found.
- **Cloudflare Containers:** not free; the Workers Paid allowance is "25 GiB-hours/month included"
  (https://developers.cloudflare.com/containers/pricing/). Worker inference (not in the source): Workers Paid is
  $5/month, with 375 vCPU-minutes and 200 GB-hours of disk.
- **Vercel Hobby:** "Function Invocations | First 1,000,000" and personal, non-commercial use only; going over
  means "you will have to wait until 30 days have passed before you can use the feature again"
  (https://vercel.com/docs/plans/hobby). Worker inference (not in the source): 100 GB transfer, 1M CDN
  requests, 100 deployments a day, 300 s function maximum.
- **Netlify Free:** "300 credits/month with a hard limit and no auto recharge option"
  (https://docs.netlify.com/manage/accounts-and-billing/billing/billing-for-credit-based-plans/credit-based-pricing-plans/).
  Worker inference (not in the source): 1 GB of bandwidth costs 20 credits and a production deploy 15 credits,
  so a busy deploy day eats the month.
- **Fly.io:** no general free tier; a card is needed to keep using billable resources
  (https://docs.fly.io/about/pricing). Worker inference (not in the source): the trial is 2 hours or 7 days and
  the smallest machine is about $2.19 per 30 days.
- **Railway:** "$1 of free credit per month" (https://docs.railway.com/pricing/plans). Worker inference (not in
  the source): 1 replica, 0.5 GB RAM, post-paid card required.
- **Render Free:** free Postgres expires after 30 days (https://render.com/docs/free); the note's claim also
  records "Do not use them for production applications" from the same page. Worker inference (not in the
  source): web services sleep after 15 minutes, 750 instance hours.
- **Supabase Free:** two free projects (https://supabase.com/docs/guides/platform/billing-on-supabase). Worker
  inference (not in the source): 500 MB database, 50,000 MAU, 1 GB storage, 5 GB egress, 500,000 edge function
  invocations. Edge Functions return "504 Gateway Timeout" when they overrun
  (https://supabase.com/docs/guides/functions/limits); the worker reports a 150 s wall clock and 2 s CPU on Free.
  The weekly pause of idle Free projects rested on a search highlight only and is excluded (Open questions).
- **Neon Free:** "100 CU-hours/project/month (enough to run a 0.25 CU compute in a project for 400
  hours/month)" (https://neon.com/docs/introduction/plans). Worker inference (not in the source): compute
  suspends after 5 minutes idle, 1 GB per project.
- **Deno Deploy Free:** "For personal use and smaller projects" (https://deno.com/deploy/pricing); "maximum
  memory allocation of 512MB" (https://docs.deno.com/deploy/pricing_and_limits/). Commercial terms not on the
  page.
- **Cloud Run:** free tier per billing account per month (https://cloud.google.com/run/pricing, quote covers
  the 180,000 vCPU-seconds). Worker inference (not in the source): a billing account means a card on file, which
  John already has for the health-app VM.
- **GitHub Actions schedule:** "In a public repository, scheduled workflows are automatically disabled when no
  repository activity has occurred in 60 days", and the schedule "can be delayed during periods of high loads"
  (https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows).
- **n8n Cloud:** API not on the free trial (https://docs.n8n.io/connect/n8n-api); Starter "20€/mo | 2.5K"
  executions on annual billing (https://n8n.io/pricing/, a tool-rendered table row).
- **Expo EAS Free:** "wait times of 90+ minutes with the low-priority queue" at peak (https://expo.dev/pricing).
- **UptimeRobot Free:** "Good for hobby and non-profit projects." (https://uptimerobot.com/pricing/).

### Q3. When containers are the right answer

**Confidence: low to medium.** The note's decision rule rested mostly on vendor and blog pages read only as
search highlights; those claims are excluded, so the rule below is a worker inference supported by the opened
platform pages.

Worker inference (the web-hosting note's rule): (1) output is files with no server code: static, no Docker;
(2) a stateless handler under the platform time cap: a Worker or Vercel/Netlify function, no Docker; (3) needs
Postgres and an API and can scale to zero: Cloud Run from source, with Neon or Supabase; (4) needs a process
that never exits (Slack Socket Mode bot, queue worker, in-process cron): an always-on container on the existing
VM or a paid PaaS. The opened pages behind it: Cloud Run builds from source and "A Dockerfile is not required"
(https://docs.cloud.google.com/run/docs/deploying-source-code, extract wording), so the engineer needs no local
Docker; Cloudflare Containers run "code written in any programming language" as part of a Worker
(https://developers.cloudflare.com/containers/) but only on the paid allowance
(https://developers.cloudflare.com/containers/pricing/); no free platform keeps a process running (Fly
https://docs.fly.io/about/pricing, Railway https://docs.railway.com/pricing/plans, Render
https://render.com/docs/free). The health app is case 4 (one VM, Docker Compose, `cloudflared`:
/home/user/health-management/docs/architecture.md:8-10). Worker inference: moving it to Cloud Run would break
Slack Socket Mode unless min-instances is set, which costs money; Cloud Run min-instance pricing was not opened.

### Q4. Private sign-in from anywhere for a single-user app

**Confidence: medium.** Cloudflare Access in front of the app is the fit and already John's pattern: "Cloudflare
Access lets only John's Google account through" (/home/user/health-management/docs/architecture.md:9-10).
"All Access applications are deny by default"
(https://developers.cloudflare.com/cloudflare-one/access-controls/applications/http-apps/self-hosted-public-app/),
and an Access application can be created by API with a token holding "Access: Apps and Policies Write"
(https://developers.cloudflare.com/api/resources/zero_trust/subresources/access/subresources/applications/methods/create/).
The policy and service-token endpoints were not opened, and the free-seat count of the Zero Trust plan rested
on search highlights only and is excluded (Open questions). Worker inference: put each private app behind a
Tunnel plus an Access app with a one-email allow policy created by API, on a hostname under a
Cloudflare-managed domain (the note names `jpclifeops.com`).

Alternatives: Vercel Authentication and "All Deployments" protection "do not require a paid add-on"
(https://vercel.com/docs/deployment-protection); worker inference: it admits only Vercel accounts, so it suits
Vercel previews, not a borrowed device. Worker inference (not in the source): Vercel Password Protection is
$20/project/month on Pro. Cloud Run can require IAM instead of public access ("Run `gcloud run services update
SERVICE_NAME --invoker-iam-check`", https://docs.cloud.google.com/run/docs/authenticating/public, an extract
paraphrase the worker marked as indicative). Rejected: Tailscale Funnel, which exposes a service to anyone and
whose "Traffic sent over a Funnel is subject to non-configurable bandwidth limits"
(https://tailscale.com/kb/1223/funnel). Worker inference: Supabase auth is an in-app login to build and
maintain, worth it only when the app has its own users or row-level security must know the user.

### Q5. Automation surfaces and the n8n-versus-code rule

**Confidence: medium.** The rule is the automation worker's judgement built on cited limits.

n8n facts: the public API is on Cloud paid plans and all self-hosted editions and "isn't available on the free
trial" (https://docs.n8n.io/connect/n8n-api); self-hosted can disable it by an env var
(https://docs.n8n.io/hosting/configuration/environment-variables/deployment/); the licence allows use "only for
your own internal business purposes or for non-commercial or personal use"
(https://github.com/n8n-io/n8n/blob/master/LICENSE.md); Git source control is Business/Enterprise only
(https://docs.n8n.io/source-control-environments/) and Community lacks environments and Git
(https://docs.n8n.io/hosting/community-edition-features/); the instance-level MCP can "Create and edit workflows
and data tables" (https://docs.n8n.io/advanced-ai/mcp/accessing-n8n-mcp-server/), and the worker's claim limits
that to n8n 2.13.0+ and to workflows flagged "Available in MCP". Cloud Starter is 20 EUR/month billed annually
for 2.5K executions (https://n8n.io/pricing/, tool-rendered row). Self-hosted failure-mode and queue-mode
reports rested on search highlights only and are excluded.

Code-first facts: systemd `Persistent=` triggers a missed run "immediately if it would have been triggered at
least once during the time when the timer was inactive"
(https://man7.org/linux/man-pages/man5/systemd.timer.5.html); Workers cron can be tested locally through "a
`/cdn-cgi/local/scheduled` route" (https://developers.cloudflare.com/workers/configuration/cron-triggers/);
Supabase cron guidance is "Each Job should run no more than 10 minutes" (https://supabase.com/docs/guides/cron);
GitHub Actions schedules drift and auto-disable (Q2). Durable-task services: Trigger.dev free has a $5 monthly
credit, 20 concurrent runs and 10 schedules per the worker's claim, quote "you'll need to upgrade to keep
running tasks" (https://trigger.dev/pricing); Inngest "50k /mo included" (https://www.inngest.com/pricing);
Windmill community self-host "Unlimited" executions, licence not named on the page
(https://www.windmill.dev/pricing).

Worker inference, the rule: (1) an existing John-visible n8n flow, low volume, built-in nodes: leave it in
n8n; the engineer edits through the instance MCP or API only after an exported JSON copy is committed to git.
(2) A new flow with Attio, Clay, WHOOP or Withings custom auth, retries, backfill or tests: code in a repo,
scheduled by a systemd timer or Cloudflare cron, with a Worker as the webhook receiver. (3) Never in n8n:
webhook handlers with 1 to 5 s deadlines unless n8n is always up, health-data pipelines needing auditable
diffs, anything on the n8n free trial. (4) Add Trigger.dev or Inngest only if a job needs durable multi-step
retries. Worker inference: without a Business licence, versioning means a scheduled export committed by the
engineer, with credentials never exported decrypted; single-instance regular mode with Postgres suits John's
low volume. Temporal was not researched (worker judgement: over-built for one user).

### Q6. Webhook receivers

**Confidence: medium-high.** Attio "enforces a 5 second timeout" and retries "up to 10 times with an
exponential back-off" (https://docs.attio.com/rest-api/guides/webhooks). WHOOP retries "five times over the
course of about one hour" (https://developer.whoop.com/docs/developing/webhooks) for workout, sleep and recovery
update and delete events (same URL); the worker's claim adds that WHOOP expects a response within a second.
Withings makes 10 attempts over about 5 h and "Missed notifications are not redelivered. Once your endpoint is
back up, backfill via the Data API using lastupdate."
(https://developer.withings.com/developer-guide/v3/data-api/notifications/notification-overview/). Cloudflare
Tunnel "creates outbound-only connections" and needs no public IP
(https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/); its price was not
on the page. Withings URL rules (ports, HEAD) rested on search highlights only and are excluded.

Worker inference: a Worker that verifies the signature, stores the raw event (KV, D1 or a Queue) or forwards it
to the VM and returns 2xx stays within WHOOP's limit and survives VM downtime; WHOOP and Attio retry, Withings
does not redeliver, so a daily backfill poll is required. An n8n Webhook node is acceptable only when n8n is
already behind HTTPS, and it adds n8n downtime to the retry budget.

**Contradictions.** The Withings overview page both says Withings retries when the response is not "HTTP <
400" and asks receivers to "return HTTP 2xx within a few seconds"
(https://developer.withings.com/developer-guide/v3/data-api/notifications/notification-overview/, as reported in
the automation note). Unresolved; spiked with a test subscription (Open questions).

### Q7. The Android path and the iOS deferral

**Confidence: medium (high on Play fee and testing rule).**

Build: Android apps sign from the command line, "You do not need Android Studio to sign your app"
(https://developer.android.com/build/building-cmdline); Expo local builds support "macOS and Linux"
(https://docs.expo.dev/build-reference/local-builds/); Capacitor lets you "either run your app on the
command-line or with Android Studio" (https://capacitorjs.com/docs/android); a Trusted Web Activity wraps a PWA
where "the app and the site it opens are expected to come from the same developer", built with the Bubblewrap
CLI on a page last updated 2020-02-04
(https://developer.chrome.com/docs/android/trusted-web-activity/overview). Health Connect is added as a Gradle
SDK dependency and the page shows no web API
(https://developer.android.com/health-and-fitness/health-connect/get-started). Worker inference: Health
Connect, widgets and reliable background sync need a wrapper (widgets treated as native-only from general
knowledge, unverified); PWA notifications and mic on Android Chrome are general knowledge, no page opened.
Ranking (worker inference): PWA, then Capacitor around the same web code, then Expo only if a UI rewrite is
wanted, then native Kotlin only for Health Connect-centred apps; Flutter, React Native CLI and Kotlin were not
researched from opened pages.

Distribution: "you are free to install apps without verification with ADB", and a limited distribution account
shares apps "with up to 20 specific devices for testing and personal use at no cost and without ID verification"
(https://developer.android.com/developer-verification/guides/faq). Developer-verification protections begin
September 30, 2026 for "participating stores in select regions on certified Android devices"
(https://developer.android.com/developer-verification); the regions and the 2027 global date are in the
worker's claim but not its quote. Firebase App Distribution can be integrated "into continuous integration (CI)
jobs" (https://firebase.google.com/docs/app-distribution); its price was not on the page. The Play Store needs
a US$25 one-time fee and ID (https://support.google.com/googleplay/android-developer/answer/6112435), personal
accounts created after 13 Nov 2023 "must meet specific testing requirements" (same URL), and the closed test is
"a minimum of 12 testers who have been opted in continuously for at least 14 days"
(https://support.google.com/googleplay/android-developer/answer/14151465). Worker inference: the 12 testers are
a human-recruited step, so the Play Store is skipped until an app is worth it.

Automation after setup: "EAS requires a Google Service Account key to submit on your behalf"
(https://docs.expo.dev/submit/android/), and "To distribute beyond internal testing, finish the setup tasks in
Play Console and promote the release" (https://docs.expo.dev/submit/introduction/). fastlane supply pushes
binaries and listing text but "you'll need to set up your app manually first by uploading at least one build"
(https://docs.fastlane.tools/actions/upload_to_play_store/). "The service account credentials need to be
securely managed" (https://developers.google.com/android-publisher/getting_started). With Play App Signing, "If
you lose your upload key or suspect that it was compromised, you are not locked out of your app", and the upload
key is the one "You use this key to sign your app bundle before uploading"
(https://support.google.com/googleplay/android-developer/answer/9842756). Worker inference: the upload keystore
and service-account JSON live in the secret store, never the repo; the engineer may stage to the internal track,
and John approves any promotion (his app-store gate).

iOS: the Apple Developer Program "is 99 USD per membership year" (https://developer.apple.com/programs/whats-included/);
an iOS web app "that has been added to the Home Screen can request permission to receive push notifications"
(https://webkit.org/blog/13878/web-push-for-web-apps-on-ios-and-ipados/); Codemagic gives "first 500 / month -
$0, then $0.095 / minute" of macOS build time (https://codemagic.io/pricing/) and EAS Free includes "15 Android
and 15 iOS builds" (https://expo.dev/pricing). The deferral holds. Worker inference: the unlock path is John
paying $99, accepting Apple terms and creating an App Store Connect API key, then EAS or Codemagic builds and
TestFlight; TestFlight and App Store Connect API automation were not read. iOS 26 Home Screen behaviour, the EU
web-app reversal and App Store wrapper rejection rested on search highlights and are excluded.

**Contradictions.** Expo says "the default `eas submit` command works out of the box"
(https://docs.expo.dev/submit/android/), while fastlane says one build must first be uploaded manually
(https://docs.fastlane.tools/actions/upload_to_play_store/). The evidence does not settle it; the mobile worker
advises planning for a one-time manual `.aab` upload by John and spiking the question on a throwaway app.

### Q8. Domains and spend gates

**Confidence: medium-high.** A Cloudflare token can be limited per resource, "Select which resources the token
is authorized to access", and "Anyone with this token can perform the authorized actions"
(https://developers.cloudflare.com/fundamentals/api/get-started/create-token/); the worker's claim says it can
be limited to one zone with DNS Edit. The Cloudflare Registrar API can register (beta) but "Renewals are not yet
available through the API" (https://developers.cloudflare.com/registrar/registrar-api/) and needs "An API token
with Registrar write permissions" (same page, fetch-tool paraphrase). Vercel's CLI quotes a price without
charging and charges "Only after a human approves", "The amount must match the current price; it isn't a
spending limit", "Retrying immediately can charge you twice", registrant name and phone come from a person
("never the registrant's first name, last name, or phone"), and the agent must "Ask a person to approve the
price, paying team, and, for a purchase, automatic renewal" (https://vercel.com/docs/cli/domains). Cloudflare
"handles issuance, renewal, and deployment automatically" for TLS
(https://developers.cloudflare.com/ssl/edge-certificates/universal-ssl/).

Worker inference, the spend gate: step 1 a non-charging quote (Vercel `domains buy --json` without `--amount`,
or Cloudflare `domain-check`); step 2 the price, term and auto-renew choice go over the approval channel; only on
John's reply does the engineer charge. The engineer never holds a Registrar-write token by default; John mints
one for one purchase or buys himself. Because Cloudflare renewals are not in the API, John renews or enables
auto-renew in the dashboard. Prefer buying through Cloudflare and keeping DNS there; registrant details are
John's to give. The same typed-request mechanism covers any new paid plan.

### Q9. Secrets without values in model context

**Confidence: medium-high.** Wrangler's "`put` command can also receive piped input" and `secret bulk` reads
stdin "rather than a file" (https://developers.cloudflare.com/workers/wrangler/commands/workers/). Vercel `env
add` takes a value through stdin, warns that echo "will save the value in bash history, so this is not
recommended for secrets", and `vercel env run` "runs any command with environment variables from your linked
Vercel project, without writing them to a file" (https://vercel.com/docs/cli/env). Fly "Values are read from
stdin as NAME=VALUE pairs" and `--stage` "sets the secrets without triggering a deployment on machine apps"
(https://docs.fly.io/flyctl/secrets-import). GitHub OIDC lets a workflow "request a short-lived access token
directly from the cloud provider" (https://docs.github.com/en/actions/concepts/security/openid-connect), needs
`id-token: write` and pins the subject to "repo:ORG-NAME/REPO-NAME:environment:ENVIRONMENT-NAME"
(https://docs.github.com/en/actions/reference/security/oidc); John's repo already reaches its VM "using GitHub
OIDC and Workload Identity Federation" (/home/user/health-management/docs/design/ops.md:40-43). With 1Password
`op run`, "processes on your computer can access the environment of other processes run by the same user"
(https://www.1password.dev/cli/secrets-environment-variables/). Infisical's free plan offers "unlimited
projects" (https://infisical.com/pricing); the 5 identities and 3 environments are in the fetch result but not
the quote.

Worker inference, the pattern: `op read "op://vault/item/field" | wrangler secret put NAME`; `op read ... |
vercel env add NAME production --sensitive`; `printf 'NAME=%s\n' "$(op read ...)" | fly secrets import
--stage`. The value passes through a shell pipe, not a tool result. Never `echo value |`, never `cat .env`, deny
reads of `.env*`. The `op` service-account token is the one long-lived secret, so its vault holds deploy secrets
only; Infisical free is the fallback vault; Doppler was not verified. John seeds production database and payment
secrets once; the engineer generates random app keys with `openssl rand` piped straight into the setter.

### Q10. Preview, production, migrations and rollback

**Confidence: high for the rollback commands, medium for the gates.** Vercel: "On the hobby plan, you can only
roll back to the previous production deployment", and "To undo a rollback, promote a deployment using `vercel
promote`" (https://vercel.com/docs/cli/rollback). Cloudflare: rolling back "will immediately create a new
deployment", "Resources connected to your Worker will not be changed during a rollback", and "You can only roll
back to the 100 most recently published versions"
(https://developers.cloudflare.com/workers/configuration/versions-and-deployments/rollbacks/); deployments and
status can "Display output as JSON" (https://developers.cloudflare.com/workers/wrangler/commands/workers/). Fly:
deploy strategies "canary, rolling, bluegreen, or immediate" (https://docs.fly.io/flyctl/deploy) and a releases
list (https://docs.fly.io/flyctl/releases/); no Fly rollback command was on the pages opened. GitHub
environment reviewers "approve or reject jobs awaiting review"
(https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/review-deployments).
Expand-contract: "In the expand phase you augment the interface to support both the old and the new versions"
(https://martinfowler.com/bliki/ParallelChange.html). Google SRE: on a bad canary "pause and roll back the
deployment, or perhaps contact a human" (https://sre.google/workbook/canarying-releases/). John's own deploy
already keeps migrations add-only "so the previous image runs on the newer schema"
(/home/user/health-management/docs/design/ops.md:44-48) and takes a "Nightly `pg_dump` at 03:30 US Eastern"
(/home/user/health-management/docs/design/ops.md:55-61).

Worker inference: preview URL for every branch; production only after the engineer posts the preview URL and
smoke result and John approves, through a GitHub Environment `production` with a required reviewer (availability
on John's plan not verified) or a chat approval plus a `DEPLOY_ENABLED` variable. Rollback table: `vercel
rollback` then `vercel promote` to undo; `wrangler rollback [version-id]`; Fly `fly deploy --image <previous>`
(derived, not documented); self-hosted compose restarts the previous image. Back up (dump plus row counts) before
every migration; migrations expand-only; contract steps and any destructive migration are John's decision,
because rollback never fixes data. Rolling back is allowed without approval; rolling forward is not.

### Q11. Monitoring, logs and alerts

**Confidence: medium.** `wrangler tail` can "Filter by invocation status: `ok`, `error`, or `canceled`"
(https://developers.cloudflare.com/workers/wrangler/commands/workers/). UptimeRobot Free has "50 monitors"
(https://uptimerobot.com/pricing/), healthchecks.io Hobbyist can "Monitor 20 jobs"
(https://healthchecks.io/pricing/), Sentry's free plan has "5k errors" with email alerts only per the worker's
claim (https://sentry.io/pricing/). ntfy publishes over plain HTTP and "the topic is essentially a password"
(https://docs.ntfy.sh/publish/). Pushover is a "$4.99 USD one-time purchase" (https://pushover.net/pricing).
Twilio US SMS is "$0.0083 per segment" plus number and 10DLC fees (https://www.twilio.com/en-us/sms/pricing/us).
Telegram "All queries to the Telegram Bot API must be served over HTTPS" (https://core.telegram.org/bots/api).
The engineer's approval channel only receives events "while the session is open"
(/home/user/Autonomy-Research/research/findings/engineer-runtime.md:529-531), and "Anyone who can reply through
the channel can approve or deny tool use" (/home/user/Autonomy-Research/research/findings/engineer-runtime.md:532).
John's health app runs "Two uptime checks every 5 minutes" (/home/user/health-management/docs/design/ops.md:62).

Worker inference: approvals and "deploy done or rolled back" messages go through the Channels/Telegram session;
outage alerts must not depend on that session, so uptime tools alert John directly (email plus ntfy or a
Telegram webhook) and write a status the engineer reads next run. After a promote the engineer probes
`/healthz` and one key page for a watch window, rolls back on failure and then tells John. Pushover is the paid
fallback only if ntfy push proves unreliable; Twilio is rejected by default. UptimeRobot free integrations,
ntfy auth and Better Stack were not read.

### Q12. Human-only steps and the pre-promote checklist

**Confidence: medium.** Apple enrollment needs a paid membership, "99 USD per membership year", an organisation
Account Holder "must have the legal authority to bind your organization to legal agreements", and a name
mismatch "will cause a delay in the approval of your enrollment" (https://developer.apple.com/programs/enroll/).
Domain purchase needs a person to approve price, paying team and auto-renew (https://vercel.com/docs/cli/domains).
A Slack app's "workspace install still needs an admin click"
(/home/user/Autonomy-Research/research/tool-registry.md:279, as cited in the note). Play needs the $25 fee, ID
and a verified Android device (https://support.google.com/googleplay/android-developer/answer/6112435).

Worker inference, John's list: (1) buy or renew a domain, set auto-renew; (2) billing profile and payment method
on any platform; (3) seed root secrets and the vault service-account token; (4) OAuth consent screens (Google,
WHOOP, Withings) and Slack workspace install; (5) Apple and Google Play enrollment and store submissions that
attest identity; (6) 2FA enrolment and recovery codes; (7) any CAPTCHA, KYC or identity check; (8) accepting
legal agreements and registrar terms; (9) deleting production data or running contract migrations; plus Play
tester recruitment and any first manual `.aab` upload (mobile note). A browser agent may, after John's go and in
a profile he logged into, fill non-attesting forms and create dashboard tokens; it never evades a CAPTCHA, and
whether a store's terms need the account holder in person was not verified.

Pre-promote checklist (worker inference, built on John's `deploy.sh`, which "**refuses** unless `ci_gate.py
verify` finds the newest CI run for that exact commit succeeded" (/home/user/health-management/docs/design/ops.md:44-45),
and on SRE guidance to use "absolute measures, such as defined SLOs" and that "Deployments should be performed by
computers, not humans" (https://sre.google/workbook/canarying-releases/)): 1 CI green for the exact SHA, no
secrets in the diff; 2 preview passes smoke; 3 migration add-only, backup taken; 4 previous release and rollback
command identified; 5 secrets present by name only in the target environment; 6 OIDC subject pinned, narrowest
tokens; 7 DNS and TLS valid; 8 uptime check and error tracking exist; 9 no new paid resource without John's
reply; 10 approval message with diff summary, preview URL and rollback command; 11 watch window with
auto-rollback, then notify. Out of scope without John: destructive migration, new paid plan, new domain, new
OAuth scope.

### Q13. Recommendation, alternatives, rejected candidates and spike list

**Confidence: medium.** The four notes agree; the recommendation joins their facet recommendations and sits on
the engineer-runtime recommendation (one Ubuntu VM John controls, approvals over Channels plus Remote Control).

**One recommendation.** Deploy by platform CLI with one narrow token per job, never by OAuth MCP. Web projects
default to Cloudflare Workers with static assets, D1 and R2 (https://developers.cloudflare.com/workers/platform/limits/);
container APIs go to Cloud Run from source in John's GCP project (https://docs.cloud.google.com/run/docs/deploying-source-code);
Postgres to Neon Free or Supabase Free (https://neon.com/docs/introduction/plans,
https://supabase.com/docs/guides/platform/billing-on-supabase); always-on processes (bots, Socket Mode, n8n)
stay on the existing VM with Docker Compose behind Cloudflare Tunnel and an API-created Access app
(/home/user/health-management/docs/architecture.md:8-10). Automations are code-first on systemd timers plus
Cloudflare Worker cron and webhook receivers, with self-hosted n8n (Postgres, nightly JSON export to git) kept for
John's visual flows. Android apps are PWAs first, wrapped with Capacitor and built by Gradle on the Linux VM only
when native APIs are needed, installed by `adb` (https://developer.android.com/developer-verification/guides/faq);
no Play account until an app needs wide distribution; iOS deferred. Secrets go vault-to-setter by pipe; preview
first, production after John's approval, auto-rollback allowed; uptime alerts go to John directly; every charge
goes through the two-step spend gate.

**Alternatives.** Vercel Hobby for personal Next.js (https://vercel.com/docs/plans/hobby); Netlify Free with
its hard credit cap
(https://docs.netlify.com/manage/accounts-and-billing/billing/billing-for-credit-based-plans/credit-based-pricing-plans/);
Deno Deploy Free (https://deno.com/deploy/pricing); Railway (https://docs.railway.com/pricing/plans; Worker
inference (not in the source): Hobby $5/month) for a simple paid container plus Postgres; GitHub Actions
schedules for repo-bound jobs
(https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows); Trigger.dev,
Inngest or Windmill if durable retries are needed (https://trigger.dev/pricing, https://www.inngest.com/pricing,
https://www.windmill.dev/pricing); n8n Cloud Starter (20 EUR/month annual, https://n8n.io/pricing/); Expo EAS
with 15 free builds a month (https://expo.dev/pricing) and local Linux builds
(https://docs.expo.dev/build-reference/local-builds/), Bubblewrap TWA for listing a PWA
(https://developer.chrome.com/docs/android/trusted-web-activity/overview), fastlane supply or EAS Submit for Play
uploads (https://docs.fastlane.tools/actions/upload_to_play_store/, https://docs.expo.dev/submit/android/),
Firebase App Distribution for testers (https://firebase.google.com/docs/app-distribution); Pushover, a "$4.99 USD
one-time purchase" (https://pushover.net/pricing), for push; Infisical free as the vault if John has no
1Password (https://infisical.com/pricing); Vercel Domains as the purchase route if a project lives on Vercel
(https://vercel.com/docs/cli/domains).

**Rejected.** Fly.io for free-first (card after trial, https://docs.fly.io/about/pricing); Render Free (Postgres
expires in 30 days, https://render.com/docs/free); Cloudflare Containers (paid only,
https://developers.cloudflare.com/containers/pricing/); Tailscale Funnel as a login (public exposure,
https://tailscale.com/kb/1223/funnel); Vercel Password Protection (worker inference: $20/project/month);
remote OAuth MCP servers as the unattended deploy path (https://vercel.com/docs/agent-resources/vercel-mcp);
Twilio SMS by default (per-segment cost plus 10DLC, https://www.twilio.com/en-us/sms/pricing/us); `echo VALUE |
setter` (https://vercel.com/docs/cli/env); a permanent Registrar-write token in the engineer's hands; long-lived
cloud keys in GitHub secrets instead of OIDC (https://docs.github.com/en/actions/concepts/security/openid-connect);
Sentry as sole alerting (email only, https://sentry.io/pricing/); native Kotlin or Flutter as the Android default
(worker judgement: rewrite cost); EAS paid plans (not needed); iOS now (https://developer.apple.com/programs/whats-included/);
n8n for strict-latency webhooks or on the free trial (https://docs.n8n.io/connect/n8n-api); Temporal (not
researched; worker judgement: over-built for one user).

**Spike list (try for real before building).**
1. Least-privilege Cloudflare token, `wrangler deploy` from a headless session; confirm Free build limits and
   whether Pages or Workers static assets is preferred. (web-hosting)
2. Create an Access app and policy by API with that token; log in from John's phone. Settle whether token-creating
   tokens or John minting tokens by hand is the route. (web-hosting, operations)
3. `gcloud run deploy --source .` from a service account via Workload Identity, including org-policy `allUsers`
   behaviour. (web-hosting)
4. Supabase Free idle pause against a keep-alive. (web-hosting)
5. n8n API and instance MCP create/update of a workflow and a credential on a throwaway self-hosted container,
   not John's account. (automation)
6. A Worker receiving real WHOOP and Withings test events with HMAC checks; settle the Withings response-code
   contract. (automation)
7. systemd `Persistent=` catch-up after a VM reboot; GitHub Actions schedule drift. (automation)
8. `./gradlew assembleRelease` on the engineer VM with the Android SDK; Health Connect from a Capacitor plugin;
   wireless `adb` install and PWA install on John's phone. (mobile)
9. First `eas submit` against the fastlane first-upload rule on a throwaway app. (mobile)
10. Pipe a vault secret into wrangler, vercel and fly setters and prove the value never appears in the
    transcript, logs or hook output. (operations)
11. Zone-scoped Cloudflare DNS token: create and read records, prove other zones are refused. (operations)
12. Vercel `domains buy --json` quote without `--amount` (must not charge), then Cloudflare `domain-check`.
    (operations)
13. Full preview, promote, rollback and migrate-with-backup cycle on a throwaway app. (operations)
14. Alert path from UptimeRobot or healthchecks.io to ntfy or a Telegram webhook on the free tiers. (operations)

## Evidence

All web sources opened 2026-10-16 unless stated. WebFetch returns a model-written extract, so quotes are the
strings that extract put in quotation marks (worker method notes). Local files: the notes give path and lines
but no tool name. Source note in brackets.

**Web hosting (notes/web-hosting.md)**
- **E1** https://developers.cloudflare.com/workers/platform/limits/ — 2026-10-16, WebFetch — Cloudflare Workers Free: 100,000 requests/day, 10 ms CPU, 100 Workers per account. Quote: "Accounts on the Workers Free plan have a daily request limit of 100,000 requests, resetting at midnight UTC."
- **E2** https://developers.cloudflare.com/d1/platform/pricing/ — 2026-10-16, WebFetch — Cloudflare D1 Free: 5M rows read/day, 100k written/day, 5 GB. Quote: "5 million / day"
- **E3** https://developers.cloudflare.com/r2/pricing/ — 2026-10-16, WebFetch — Cloudflare R2 Free: 10 GB-month, free egress. Quote: "10 GB-month / month"
- **E4** https://developers.cloudflare.com/pages/platform/limits/ — 2026-10-16, WebFetch — Cloudflare Pages Free: 500 builds/month, 20,000 files, 25 MiB per file. Quote: "Cloudflare Pages sites can contain up to 20,000 files on the Free plan."
- **E5** https://developers.cloudflare.com/workers/static-assets/ — 2026-10-16, WebFetch — Workers can host static assets with the code in one deploy (SPA fallback via `not_found_handling`). Quote: "Sets your application to return a `200 OK` response with `index.html` for requests which don't match a static asset."
- **E6** https://developers.cloudflare.com/workers/wrangler/system-environment-variables/ — 2026-10-16, WebFetch — Wrangler reads a scoped token from env, for CI and automation. Quote: "The API token for your Cloudflare account, can be used for authentication for situations like CI/CD, and other automation."
- **E7** https://developers.cloudflare.com/containers/pricing/ — 2026-10-16, WebFetch — Cloudflare Containers: no Free allowance, Workers Paid ($5/month) with 25 GiB-hours memory, 375 vCPU-minutes, 200 GB-hours disk. Quote: "25 GiB-hours/month included"
- **E8** https://developers.cloudflare.com/containers/ — 2026-10-16, WebFetch — Cloudflare Containers run any language as part of a Worker, defined in config with `"image": "./Dockerfile"`. Quote: "Run code written in any programming language, built for any runtime, as part of apps built on Workers."
- **E9** https://vercel.com/docs/plans/hobby — 2026-10-16, WebFetch — Vercel Hobby: 1M function invocations, 100 GB fast data transfer, 1M CDN requests, 100 deployments/day, 300 s function max. Quote: "Function Invocations | First 1,000,000"
- **E10** https://vercel.com/docs/plans/hobby — 2026-10-16, WebFetch — Vercel Hobby is personal, non-commercial only. Quote: "the Hobby plan restricts users to non-commercial, personal use only."
- **E11** https://vercel.com/docs/cli/global-options — 2026-10-16, WebFetch — Vercel CLI authenticates with `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID`, and has `--non-interactive`. Quote: "set `VERCEL_ORG_ID` and `VERCEL_PROJECT_ID` as environment variables to skip project linking."
- **E12** https://vercel.com/docs/plans/hobby — 2026-10-16, WebFetch — Vercel exceeding Hobby limits means waiting 30 days. Quote: "you will have to wait until 30 days have passed before you can use the feature again."
- **E13** https://docs.netlify.com/manage/accounts-and-billing/billing/billing-for-credit-based-plans/credit-based-pricing-plans/ — 2026-10-16, WebFetch — Netlify Free is credit based with a hard limit (300 credits; 1 GB bandwidth = 20 credits; production deploy = 15 credits). Quote: "$0/month, forever, for 300 credits/month with a hard limit and no auto recharge option."
- **E14** https://docs.netlify.com/api-and-cli-guides/cli-guides/get-started-with-cli/ — 2026-10-16, WebFetch — Netlify CLI deploys non-interactively with two env vars. Quote: "Project ID** is exactly the value `NETLIFY_SITE_ID` expects."
- **E15** https://docs.fly.io/about/pricing — 2026-10-16, WebFetch — Fly.io has no general free tier; trial is 2 h or 7 days, then a card is required; smallest machine about $2.19 per 30 days. Quote: "you'll need to add a credit card to keep using billable resources."
- **E16** https://docs.fly.io/flyctl/tokens-create-deploy — 2026-10-16, WebFetch — Fly deploy token is scoped to one app. Quote: "Create an API token limited to managing a single app and its resources."
- **E17** https://docs.railway.com/pricing/plans — 2026-10-16, WebFetch — Railway: Free plan $1 credit/month with 1 replica and 0.5 GB RAM; Hobby $5/month; post-paid card required. Quote: "For running small apps with $1 of free credit per month"
- **E18** https://docs.railway.com/cli/deploying — 2026-10-16, WebFetch — Railway CI deploy uses a project token scoped to one environment. Quote: "Project tokens are scoped to a specific environment and can only perform deployment-related actions."
- **E19** https://render.com/docs/free — 2026-10-16, WebFetch — Render Free web service sleeps after 15 minutes, 750 instance hours, free Postgres expires after 30 days, "Do not use them for production applications". Quote: "Free Render Postgres databases expire 30 days after creation."
- **E20** https://render.com/docs/api — 2026-10-16, WebFetch — Render API needs an API key (create/deploy endpoint names not on the page I opened). Quote: "All Render API requests require authentication via API key."
- **E21** https://supabase.com/docs/guides/platform/billing-on-supabase — 2026-10-16, WebFetch — Supabase Free: 2 active projects, 500 MB DB, 50,000 MAU, 1 GB storage, 5 GB egress, 500,000 edge function invocations. Quote: "You are granted two free projects."
- **E22** https://supabase.com/docs/guides/deployment/managing-environments — 2026-10-16, WebFetch — Supabase CLI non-interactive: scoped personal access token, `supabase link`, `supabase db push`. Quote: "`SUPABASE_ACCESS_TOKEN` is a scoped personal access token limited to the projects this workflow deploys to."
- **E23** https://neon.com/docs/introduction/plans — 2026-10-16, WebFetch — Neon Free: 100 projects, 1 GB per project (20 GB total), 100 CU-hours/project/month, compute suspends after 5 min idle. Quote: "100 CU-hours/project/month (enough to run a 0.25 CU compute in a project for 400 hours/month)."
- **E24** https://deno.com/deploy/pricing — 2026-10-16, WebFetch — Deno Deploy Free: 1M requests, 20 GiB egress, 10 h active CPU; described as for personal use; commercial terms not on page. Quote: "For personal use and smaller projects"
- **E25** https://docs.deno.com/deploy/pricing_and_limits/ — 2026-10-16, WebFetch — Deno Deploy docs: memory cap 512 MB, 1 GB deploy size. Quote: "Applications have a maximum memory allocation of 512MB"
- **E26** https://cloud.google.com/run/pricing — 2026-10-16, Exa fetch — Cloud Run free tier is aggregated per billing account per month (request-based: 2M requests, 180,000 vCPU-s, 360,000 GiB-s; instance-based: 240,000 vCPU-s, 450,000 GiB-s) and egress 1 GiB North America. Quote: "First 180,000 vCPU-seconds free per month"
- **E27** https://docs.cloud.google.com/run/docs/deploying-source-code — 2026-10-16, WebFetch — `gcloud run deploy SERVICE --source .` needs no Dockerfile (buildpacks) and no local Docker. Quote: "uses a Dockerfile if present, although it's not required."
- **E28** https://docs.cloud.google.com/run/docs/authenticating/public — 2026-10-16, WebFetch — Cloud Run IAM: public access is a `roles/run.invoker` binding for `allUsers`; org policy can block it. Quote: "Enabling the Cloud Run Invoker IAM check in the Google Cloud console removes any existing"
- **E29** /home/user/health-management/docs/architecture.md:8-10 — local file, tool not named in the note — Health app today: one GCP VM, Docker Compose, Cloudflare Tunnel, Access limited to John's Google account. Quote: "One small Google Cloud VM runs four containers with Docker Compose: `cloudflared`, `api` (FastAPI), `worker` (Python)"
- **E30** https://developers.cloudflare.com/cloudflare-one/access-controls/applications/http-apps/self-hosted-public-app/ — 2026-10-16, WebFetch — Access apps are deny-by-default; dashboard flow is Zero Trust > Access controls > Applications. Quote: "All Access applications are deny by default"
- **E31** https://developers.cloudflare.com/api/resources/zero_trust/subresources/access/subresources/applications/methods/create/ — 2026-10-16, WebFetch — Access applications can be created by API: `POST /{accounts_or_zones}/{account_or_zone_id}/access/apps` with token permission `Access: Apps and Policies Write`. Quote: "Access: Apps and Policies Write"
- **E32** https://tailscale.com/kb/1223/funnel — 2026-10-16, WebFetch — Tailscale Funnel is available on all plans, needs MagicDNS, HTTPS, a `funnel` node attribute, exposes to anyone, with non-configurable bandwidth limits. Quote: "Traffic sent over a Funnel is subject to non-configurable bandwidth limits."
- **E33** https://vercel.com/docs/deployment-protection — 2026-10-16, WebFetch — Vercel Deployment Protection: Vercel Authentication and "All Deployments" scope work on every plan; Password Protection is Pro $20/project/month; Passport (own IdP) Enterprise only. Quote: "Vercel Authentication for All Deployments and Deployment Protection Exceptions do not require a paid add-on."
- **E34** https://docs.cloud.google.com/run/docs/authenticating/public — 2026-10-16, WebFetch — Cloud Run can require IAM auth instead of being public; IAP for Cloud Run is a separate guide I did not open. Quote: "Run `gcloud run services update SERVICE_NAME --invoker-iam-check`" (extract paraphrase of the page; treat as indicative)
- **E35** /home/user/health-management/docs/architecture.md:9-10 — local file, tool not named in the note — Existing pattern: Tunnel in, Access lets only John's Google account through. Quote: "and Cloudflare Access lets only John's Google account through."
- **E36** https://docs.cloud.google.com/run/docs/deploying-source-code — 2026-10-16, WebFetch — Cloud Run builds from source with no Dockerfile and no local Docker. Quote: "A Dockerfile is not required." (extract wording; the page line quoted in the matrix section is the safer verbatim)
- **E37** https://developers.cloudflare.com/containers/pricing/ — 2026-10-16, WebFetch — Cloudflare Containers cost the Workers Paid plan (no Free allowance). Quote: "25 GiB-hours/month included"
- **E38** https://vercel.com/docs/agent-resources/vercel-mcp — 2026-10-16, WebFetch — Vercel MCP is a remote MCP with OAuth at mcp.vercel.com, for managing projects and deployments. Quote: "It's a remote MCP with OAuth that gives AI tools secure access to your Vercel projects"
- **E39** https://vercel.com/changelog/vercel-mcp-can-now-deploy-code — 2026-10-16, WebFetch — Vercel MCP can deploy code via a `deploy_to_vercel` tool. Quote: "can now deploy code directly to a new or existing project."
- **E40** https://vercel.com/docs/agent-resources/vercel-mcp — 2026-10-16, WebFetch — Vercel advises human confirmation and warns of prompt injection through MCP. Quote: "Always enable human confirmation in your workflows to maintain control and prevent unauthorized changes"
- **E41** https://supabase.com/docs/guides/getting-started/mcp — 2026-10-16, WebFetch — Supabase MCP has `read_only=true`, `project_ref` scoping, feature groups, and a `deploy_edge_function` tool. Quote: "All groups except Storage are enabled by default"
- **E42** https://supabase.com/docs/guides/getting-started/mcp — 2026-10-16, WebFetch — Supabase recommends read-only for unattended routines (extract wording). Quote: "This is not foolproof though, so you should always review the output before proceeding with further actions."
- **E43** https://github.com/cloudflare/mcp-server-cloudflare — 2026-10-16, WebFetch — Cloudflare lists many MCP servers; the "Cloudflare API MCP Server" is recommended, several older ones deprecated. Quote: "an API token that has the scopes (permissions) required for that particular MCP server."
- **E44** https://docs.netlify.com/build/build-with-ai/netlify-mcp-server/ — 2026-10-16, WebFetch — Netlify: remote MCP, a Netlify connector on Claude Marketplace, and a skills plugin; deploy guidance lives in skills. Quote: "Netlify offers an [MCP server](https://github.com/netlify/netlify-mcp), which you can connect to through a connector, plugin, or your agent."

**Automation surfaces (notes/automation-surfaces.md)**
- **E45** https://docs.n8n.io/connect/n8n-api — 2026-10-16, WebFetch — API availability: Cloud Starter, Pro, Enterprise and all self-hosted; not the free trial. Quote: "It isn't available on the free trial."
- **E46** https://docs.n8n.io/hosting/configuration/environment-variables/deployment/ — 2026-10-16, WebFetch — Self-hosted API can be switched off by env var, default on. Quote: "Whether to disable the public API (true) or not (false)."
- **E47** https://github.com/n8n-io/n8n/blob/master/LICENSE.md — 2026-10-16, WebFetch — Licence permits internal business use; ".ee." files need Enterprise licence. Quote: "You may use or modify the software only for your own internal business purposes or for non-commercial or personal use."
- **E48** https://n8n.io/pricing/ — 2026-10-16, WebFetch — Cloud pricing/limits (annual billing): Starter 20 EUR, 2.5K executions, 5 min max duration; Pro 50 EUR, 10K, 40 min. Quote: "Starter | 20€/mo | 2.5K" (tool-rendered table row; page summary, not raw text)
- **E49** https://docs.n8n.io/source-control-environments/ — 2026-10-16, WebFetch — Git source control is Business/Enterprise only; Community lacks it. Quote: "Available on Business and Enterprise plans."
- **E50** https://docs.n8n.io/hosting/community-edition-features/ — 2026-10-16, WebFetch — Community lacks environments and Git. Quote: "These features are available on self-hosted Business and Enterprise plans."
- **E51** https://docs.n8n.io/advanced-ai/mcp/accessing-n8n-mcp-server/ — 2026-10-16, WebFetch — Instance-level MCP can create/edit workflows (n8n 2.13.0+), only workflows flagged "Available in MCP"; enabled by owner/admin; OAuth or API key. Quote: "Create and edit workflows and data tables."
- **E52** https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows — 2026-10-16, WebFetch — GitHub Actions: 5-minute minimum, delays under load, auto-disable after 60 days without repo activity (public repos), default branch only. Quote: "In a public repository, scheduled workflows are automatically disabled when no repository activity has occurred in 60 days."
- **E53** https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows — 2026-10-16, WebFetch — Same page on drift. Quote: "The `schedule` event can be delayed during periods of high loads of GitHub Actions workflow runs."
- **E54** https://developers.cloudflare.com/workers/platform/limits/ — 2026-10-16, WebFetch — Cloudflare Workers Free: 100k requests/day, 10 ms CPU, 5 cron triggers, 50 subrequests. Quote: "Accounts on the Workers Free plan have a daily request limit of 100,000 requests, resetting at midnight UTC." (tool paraphrased the other numbers; 10 ms CPU, 5 triggers as reported by the fetch tool.)
- **E55** https://developers.cloudflare.com/workers/configuration/cron-triggers/ — 2026-10-16, WebFetch — Cloudflare cron: UTC, config in wrangler `triggers.crons`, local test route. Quote: "This exposes a `/cdn-cgi/local/scheduled` route, which can be used to test using an HTTP request."
- **E56** https://developers.cloudflare.com/workers/configuration/cron-triggers/ — 2026-10-16, WebFetch — Cloudflare cron changes can lag. Quote: "may take several minutes (up to 15 minutes) to propagate to the Cloudflare global network."
- **E57** https://supabase.com/docs/guides/cron — 2026-10-16, WebFetch — Supabase cron (pg_cron) calls Edge Functions; 10-min job guidance. Quote: "Each Job should run no more than 10 minutes."
- **E58** https://supabase.com/docs/guides/functions/limits — 2026-10-16, WebFetch — Supabase edge function limits: free 150 s wall clock, 2 s CPU. Quote: "If an Edge Function doesn't send a response before the timeout, 504 Gateway Timeout will be returned."
- **E59** https://man7.org/linux/man-pages/man5/systemd.timer.5.html — 2026-10-16, WebFetch — systemd timers catch up missed runs with Persistent=. Quote: "the service unit is triggered immediately if it would have been triggered at least once during the time when the timer was inactive."
- **E60** https://trigger.dev/pricing — 2026-10-16, WebFetch — Trigger.dev free: $5 monthly credit, 20 concurrent runs, 10 schedules, 1-day logs; Apache 2.0 self-hostable. Quote: "you'll need to upgrade to keep running tasks" (as rendered by the fetch tool)
- **E61** https://www.inngest.com/pricing — 2026-10-16, WebFetch — Inngest free: 50k executions/mo, 5 concurrent, 24 h trace history. Quote: "50k /mo included"
- **E62** https://www.windmill.dev/pricing — 2026-10-16, WebFetch — Windmill community self-hosted: unlimited executions, 3 workspaces, git sync up to 2 users; "Commercial licence" No; licence not named on page. Quote: "Unlimited"
- **E63** https://docs.attio.com/rest-api/guides/webhooks — 2026-10-16, WebFetch — Attio: HTTPS only, HMAC-SHA256 `Attio-Signature`, 5 s timeout, 10 retries over about 3 days. Quote: "Attio will retry delivery of the message up to 10 times with an exponential back-off."
- **E64** https://docs.attio.com/rest-api/guides/webhooks — 2026-10-16, WebFetch — Attio timeout. Quote: "Attio also enforces a 5 second timeout on requests to your target URL."
- **E65** https://developer.whoop.com/docs/developing/webhooks — 2026-10-16, WebFetch — WHOOP: HTTPS endpoint, signature headers, retries five times over about an hour, respond within a second. Quote: "WHOOP will retry webhook delivery for failed webhook requests five times over the course of about one hour."
- **E66** https://developer.whoop.com/docs/developing/webhooks — 2026-10-16, WebFetch — WHOOP events: workout/sleep/recovery updated|deleted. Quote: "Enum: "workout.updated" "workout.deleted" "sleep.updated" "sleep.deleted" "recovery.updated" "recovery.deleted""
- **E67** https://developer.withings.com/developer-guide/v3/data-api/notifications/notification-overview/ — 2026-10-16, WebFetch — Withings: 10 attempts over about 5 h, missed notifications not redelivered (backfill with lastupdate). Quote: "Missed notifications are not redelivered. Once your endpoint is back up, backfill via the Data API using lastupdate."
- **E68** https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/ — 2026-10-16, WebFetch — Cloudflare Tunnel is outbound-only and needs no public IP. Quote: "creates outbound-only connections to Cloudflare's global network"

**Android and iOS (notes/mobile.md)**
- **E69** https://developer.android.com/build/building-cmdline — 2026-10-16, WebFetch — Android apps build and sign headless with the Gradle wrapper, no Android Studio. Quote: "You do not need Android Studio to sign your app. You can sign your app from the command line, using `apksigner` for APKs or `jarsigner` for app bundles"
- **E70** https://docs.expo.dev/build-reference/local-builds/ — 2026-10-16, WebFetch — Expo local builds run on Linux; you supply the Android SDK/NDK. Quote: "macOS and Linux are supported."
- **E71** https://expo.dev/pricing — 2026-10-16, WebFetch — EAS cloud free plan is 15 Android + 15 iOS builds, low-priority queue; paid from $19/month. Quote: "At peak times, you may experience wait times of 90+ minutes with the low-priority queue depending on demand."
- **E72** https://capacitorjs.com/docs/android — 2026-10-16, WebFetch — Capacitor Android is Android-Studio-centred; docs also allow command line. Quote: "either run your app on the command-line or with Android Studio."
- **E73** https://developer.chrome.com/docs/android/trusted-web-activity/overview — 2026-10-16, WebFetch — TWA wraps a PWA; same-developer check via Digital Asset Links; Bubblewrap is a Node CLI to build TWA projects (page last updated 2020-02-04). Quote: "the app and the site it opens are expected to come from the same developer."
- **E74** https://developer.android.com/health-and-fitness/health-connect/get-started — 2026-10-16, WebFetch — Health Connect is a native Android SDK (Gradle dependency, manifest permissions); the page shows no web API. Quote: "Add the Health Connect SDK dependency in your module-level `build.gradle` file"
- **E75** https://support.google.com/googleplay/android-developer/answer/6112435 — 2026-10-16, WebFetch — One-time $25 fee and ID requirements. Quote: "There is a US$25 one-time registration fee that you can pay with the following credit or debit cards:"
- **E76** https://support.google.com/googleplay/android-developer/answer/6112435 — 2026-10-16, WebFetch — Personal accounts after 13 Nov 2023 have testing requirements; new personal accounts must verify an Android device via the Play Console mobile app. Quote: "must meet specific testing requirements before they can make their app available on Google Play."
- **E77** https://support.google.com/googleplay/android-developer/answer/14151465 — 2026-10-16, WebFetch — Closed test: 12 testers, 14 days. Quote: "a minimum of 12 testers who have been opted in continuously for at least 14 days."
- **E78** https://developer.android.com/developer-verification — 2026-10-16, WebFetch — Developer verification dates: protections begin 30 Sep 2026 in Brazil, Indonesia, Singapore, Thailand, global in 2027; limited distribution account for hobbyists (20 devices). Quote: "Effective September 30, 2026: Protections begin for users installing apps from participating stores in select regions on certified Android devices."
- **E79** https://developer.android.com/developer-verification/guides/faq — 2026-10-16, WebFetch — ADB installs exempt; limited distribution account free, up to 20 devices; $25 for Full Distribution. Quote: "As a developer, you are free to install apps without verification with ADB."
- **E80** https://developer.android.com/developer-verification/guides/faq — 2026-10-16, WebFetch — Same FAQ. Quote: "This lets you share apps with up to 20 specific devices for testing and personal use at no cost and without ID verification."
- **E81** https://firebase.google.com/docs/app-distribution — 2026-10-16, WebFetch — Firebase App Distribution: CLI, Gradle, fastlane upload; CI integration; pricing not on page. Quote: "Automate distribution by integrating the CLI into continuous integration (CI) jobs."
- **E82** https://docs.expo.dev/submit/android/ — 2026-10-16, WebFetch — EAS Submit first release goes to internal testing; service account key required; listing is not managed. Quote: "EAS requires a Google Service Account key to submit on your behalf."
- **E83** https://docs.expo.dev/submit/introduction/ — 2026-10-16, WebFetch — EAS Submit does not do listing, and moving past internal needs Console work. Quote: "To distribute beyond internal testing, finish the setup tasks in Play Console and promote the release."
- **E84** https://docs.fastlane.tools/actions/upload_to_play_store/ — 2026-10-16, WebFetch — fastlane supply requires a manual first upload; can push listing text, screenshots, changelogs, binaries and promote tracks. Quote: "you'll need to set up your app manually first by uploading at least one build"
- **E85** https://developers.google.com/android-publisher/getting_started — 2026-10-16, WebFetch — Service account is created in Cloud Console and invited in Play Console Users & permissions; must be kept secure. Quote: "The service account credentials need to be securely managed"
- **E86** https://support.google.com/googleplay/android-developer/answer/9842756 — 2026-10-16, WebFetch — Play App Signing: Google holds app signing key; upload key loss is recoverable by reset request. Quote: "If you lose your upload key or suspect that it was compromised, you are not locked out of your app."
- **E87** https://support.google.com/googleplay/android-developer/answer/9842756 — 2026-10-16, WebFetch — Upload key is an RSA 2048+ keystore you hold. Quote: "You use this key to sign your app bundle before uploading it to the Play Console."
- **E88** https://developer.apple.com/programs/whats-included/ — 2026-10-16, WebFetch — Apple Developer Program price. Quote: "The Apple Developer Program is 99 USD per membership year, or in local currency where available."
- **E89** https://webkit.org/blog/13878/web-push-for-web-apps-on-ios-and-ipados/ — 2026-10-16, WebFetch — iOS web push needs iOS 16.4 and an installed Home Screen web app, triggered by user action. Quote: "A web app that has been added to the Home Screen can request permission to receive push notifications"
- **E90** https://codemagic.io/pricing/ — 2026-10-16, WebFetch — Codemagic free tier 500 macOS M2 minutes/month, then $0.095/min. Quote: "first 500 / month - $0, then $0.095 / minute"
- **E91** https://expo.dev/pricing — 2026-10-16, WebFetch — EAS Free plan includes iOS builds (15/month). Quote: "15 Android and 15 iOS builds"
- **E92** https://docs.expo.dev/submit/android/ — 2026-10-16, WebFetch — Expo says the first `eas submit` works out of the box (from the note's Contradictions). Quote: "the default `eas submit` command works out of the box"

**Operations (notes/operations.md)**
- **E93** https://developers.cloudflare.com/fundamentals/api/get-started/create-token/ — 2026-10-16, WebFetch — DNS token can be limited to a single zone; Edit is full CRUDL, so give Edit only when records are written. Quote: "Select which resources the token is authorized to access."
- **E94** https://developers.cloudflare.com/fundamentals/api/get-started/create-token/ — 2026-10-16, WebFetch — A leaked Cloudflare token acts with its full authorization, so scope and TTL/IP filters matter. Quote: "Anyone with this token can perform the authorized actions against the resources that the token has access to."
- **E95** https://developers.cloudflare.com/registrar/registrar-api/ — 2026-10-16, WebFetch — Cloudflare Registrar API can register domains (beta) but not renew, transfer or update contacts. Quote: "Renewals are not yet available through the API."
- **E96** https://developers.cloudflare.com/registrar/registrar-api/ (opened) and https://developers.cloudflare.com/api/resources/registrar/subresources/registrations/methods/create/ (Exa search highlight only, not opened) — 2026-10-16, WebFetch — Registrar API needs a write token and a stored payment method and default contact set up in the dashboard; premium domains are excluded. Quote: "An API token with Registrar write permissions." (paraphrased by the fetch tool from the registrar-api page; exact wording of that page not re-verified). Synthesizer note: only the write-token part is used in the answers; the payment-method, default-contact and premium parts appear to rest on the unopened page and are listed under Open questions.
- **E97** https://vercel.com/docs/cli/domains — 2026-10-16, WebFetch — Vercel CLI supports price check without charging and a charge only with an approved amount. Quote: "Only after a human approves: charges $20.00 now"
- **E98** https://vercel.com/docs/cli/domains — 2026-10-16, WebFetch — Vercel: the approved amount must equal the current price and registrations are non-refundable. Quote: "The amount must match the current price; it isn't a spending limit."
- **E99** https://vercel.com/docs/cli/domains — 2026-10-16, WebFetch — Vercel: an unknown purchase outcome must be inspected before retry (double-charge risk). Quote: "Retrying immediately can charge you twice."
- **E100** https://vercel.com/docs/cli/domains — 2026-10-16, WebFetch — Vercel buy needs registrant first name, last name, phone from a person; billing details never supply them. Quote: "never the registrant's first name, last name, or phone"
- **E101** https://developers.cloudflare.com/ssl/edge-certificates/universal-ssl/ — 2026-10-16, WebFetch — Cloudflare TLS is issued and renewed automatically. Quote: "Cloudflare handles issuance, renewal, and deployment automatically."
- **E102** https://developers.cloudflare.com/workers/wrangler/commands/workers/ — 2026-10-16, WebFetch — Wrangler `secret put` accepts piped input. Quote: "The `put` command can also receive piped input."
- **E103** https://developers.cloudflare.com/workers/wrangler/commands/workers/ — 2026-10-16, WebFetch — Wrangler `secret bulk` reads stdin if no file is given, up to 100 secrets. Quote: "If omitted, Wrangler expects to receive input from stdin rather than a file."
- **E104** https://vercel.com/docs/cli/env — 2026-10-16, WebFetch — Vercel `env add` takes a value from a file or stdin; piping with echo leaks to shell history. Quote: "Warning: this will save the value in bash history, so this is not recommended for secrets."
- **E105** https://vercel.com/docs/cli/env — 2026-10-16, WebFetch — Vercel `env add` defaults to Secret type for production and preview, and a value may come via stdin. Quote: "unless you pass a type flag, `--yes`, `--value`, or a value through stdin"
- **E106** https://vercel.com/docs/cli/env — 2026-10-16, WebFetch — Vercel can run a command with env without writing a file. Quote: "runs any command with environment variables from your linked Vercel project, without writing them to a file."
- **E107** https://docs.fly.io/flyctl/secrets-import — 2026-10-16, WebFetch — Fly `secrets import` reads stdin. Quote: "Values are read from stdin as NAME=VALUE pairs"
- **E108** https://docs.fly.io/flyctl/secrets-import — 2026-10-16, WebFetch — Fly `--stage` sets secrets without a deploy on machine apps. Quote: "sets the secrets without triggering a deployment on machine apps."
- **E109** https://docs.github.com/en/actions/concepts/security/openid-connect — 2026-10-16, WebFetch — GitHub OIDC replaces stored cloud credentials with short-lived tokens. Quote: "request a short-lived access token directly from the cloud provider."
- **E110** https://docs.github.com/en/actions/reference/security/oidc — 2026-10-16, WebFetch — OIDC needs `id-token: write` and the cloud trust policy must pin the subject. Quote: "Without `id-token: write`, the OIDC JWT ID token cannot be requested."
- **E111** https://docs.github.com/en/actions/reference/security/oidc — 2026-10-16, WebFetch — Subject can be pinned to repo and environment. Quote: "repo:ORG-NAME/REPO-NAME:environment:ENVIRONMENT-NAME"
- **E112** https://www.1password.dev/cli/secrets-environment-variables/ — 2026-10-16, WebFetch — 1Password `op run` injects secrets into one process; same-user processes may read them. Quote: "You should assume that processes on your computer can access the environment of other processes run by the same user."
- **E113** https://infisical.com/pricing — 2026-10-16, WebFetch — Infisical free: 5 identities, unlimited projects, 3 environments per project. Quote: "unlimited projects" (identities 5 and environments 3 stated in the same fetch result, not separately quoted)
- **E114** /home/user/health-management/docs/design/ops.md:40-43 — local file, tool not named in the note — John's health-management repo already uses OIDC + Workload Identity Federation with no stored keys, only `deploy.yml` on `main`. Quote: "reaches the VM through IAP using GitHub OIDC and Workload Identity Federation"
- **E115** https://vercel.com/docs/cli/rollback — 2026-10-16, WebFetch — Vercel rollback command and Hobby limit. Quote: "On the hobby plan, you can only roll back to the previous production deployment."
- **E116** https://vercel.com/docs/cli/rollback — 2026-10-16, WebFetch — Vercel undo rollback by promote. Quote: "To undo a rollback, promote a deployment using `vercel promote`"
- **E117** https://developers.cloudflare.com/workers/configuration/versions-and-deployments/rollbacks/ — 2026-10-16, WebFetch — Wrangler rollback creates a new deployment on all routes. Quote: "Rolling back to a previous version of your Worker will immediately create a new deployment"
- **E118** https://developers.cloudflare.com/workers/configuration/versions-and-deployments/rollbacks/ — 2026-10-16, WebFetch — Wrangler rollback does not touch data or bindings. Quote: "Resources connected to your Worker will not be changed during a rollback."
- **E119** https://developers.cloudflare.com/workers/configuration/versions-and-deployments/rollbacks/ — 2026-10-16, WebFetch — Wrangler rollback is limited to 100 versions. Quote: "You can only roll back to the 100 most recently published versions."
- **E120** https://developers.cloudflare.com/workers/wrangler/commands/workers/ — 2026-10-16, WebFetch — `wrangler deployments list --json` and `status --json` give machine output. Quote: "Display output as JSON"
- **E121** https://docs.fly.io/flyctl/deploy — 2026-10-16, WebFetch — Fly: `fly releases` lists releases; `fly deploy --image` deploys a given image, `--strategy` has canary, rolling, bluegreen, immediate. Quote: "Options are canary, rolling, bluegreen, or immediate. The default strategy is rolling."
- **E122** https://docs.fly.io/flyctl/releases/ — 2026-10-16, WebFetch — Fly releases page lists releases with success/fail. Quote: "all the releases of the application onto the Fly platform"
- **E123** https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/review-deployments — 2026-10-16, WebFetch — GitHub environment reviewers gate secrets. Quote: "You can approve or reject jobs awaiting review."
- **E124** https://martinfowler.com/bliki/ParallelChange.html — 2026-10-16, WebFetch — Expand/migrate/contract. Quote: "In the expand phase you augment the interface to support both the old and the new versions."
- **E125** https://sre.google/workbook/canarying-releases/ — 2026-10-16, WebFetch — Google SRE: pause and roll back a bad canary, small deployments. Quote: "we should pause and roll back the deployment, or perhaps contact a human to help troubleshoot the issue."
- **E126** /home/user/health-management/docs/design/ops.md:44-48 — local file, tool not named in the note — John's own deploy: CI gate, migrate, up, probe /healthz, auto-roll back; migrations add-only so the previous image runs on the new schema. Quote: "Migrations only add, and new columns are nullable or defaulted (ADR 0010), so the previous image runs on the newer schema."
- **E127** /home/user/health-management/docs/design/ops.md:55-61 — local file, tool not named in the note — Nightly dump plus monthly restore check; /healthz reports backups. Quote: "Nightly `pg_dump` at 03:30 US Eastern"
- **E128** https://developers.cloudflare.com/workers/wrangler/commands/workers/ — 2026-10-16, WebFetch — `wrangler tail` streams logs with JSON format and status filter. Quote: "Filter by invocation status: `ok`, `error`, or `canceled`"
- **E129** https://uptimerobot.com/pricing/ — 2026-10-16, WebFetch — UptimeRobot Free: 50 monitors, 5 min. Quote: "50 monitors"
- **E130** https://uptimerobot.com/pricing/ — 2026-10-16, WebFetch — UptimeRobot free is positioned for hobby use; SMS/voice credits not included. Quote: "Good for hobby and non-profit projects."
- **E131** https://healthchecks.io/pricing/ — 2026-10-16, WebFetch — healthchecks.io Hobbyist is free for 20 jobs. Quote: "Monitor 20 jobs"
- **E132** https://sentry.io/pricing/ — 2026-10-16, WebFetch — Sentry free: 5k errors, one user, email alerts only. Quote: "5k errors"
- **E133** https://docs.ntfy.sh/publish/ — 2026-10-16, WebFetch — ntfy publishes with plain HTTP and topic name is the password. Quote: "the topic is essentially a password"
- **E134** https://pushover.net/pricing — 2026-10-16, WebFetch — Pushover: $4.99 one-time per platform, 10,000 free messages per month. Quote: "$4.99 USD one-time purchase"
- **E135** https://www.twilio.com/en-us/sms/pricing/us — 2026-10-16, WebFetch — Twilio US SMS $0.0083 per segment, $1.15 per month long code, plus 10DLC onboarding fees. Quote: "$0.0083 per segment"
- **E136** https://core.telegram.org/bots/api — 2026-10-16, WebFetch — Telegram Bot API is HTTPS with the token in the URL. Quote: "All queries to the Telegram Bot API must be served over HTTPS."
- **E137** /home/user/Autonomy-Research/research/findings/engineer-runtime.md:529-531 — local file, tool not named in the note — Approval channel from wave 1: Channels forward permission prompts, session must be open. Quote: "Events only arrive while the session is open, so for an always-on setup you run Claude in a background process or persistent terminal."
- **E138** /home/user/Autonomy-Research/research/findings/engineer-runtime.md:532 — local file, tool not named in the note — Channel allowlist caution. Quote: "Anyone who can reply through the channel can approve or deny tool use in your session, so only allowlist senders you trust with that authority."
- **E139** /home/user/health-management/docs/design/ops.md:62 — local file, tool not named in the note — John's health app: two 5-minute uptime checks through Cloudflare Access service token, email on failure. Quote: "Two uptime checks every 5 minutes"
- **E140** https://developer.apple.com/programs/enroll/ — 2026-10-16, WebFetch — Apple enrollment requires 2FA Apple Account, legal-name verification and a paid membership. Quote: "The Apple Developer Program is 99 USD per membership year."
- **E141** https://developer.apple.com/programs/enroll/ — 2026-10-16, WebFetch — Apple organization needs legal authority and D-U-N-S. Quote: "you'll be the Account Holder and must have the legal authority to bind your organization to legal agreements."
- **E142** https://developer.apple.com/programs/enroll/ — 2026-10-16, WebFetch — Apple name must match legal identity. Quote: "will cause a delay in the approval of your enrollment."
- **E143** https://vercel.com/docs/cli/domains — 2026-10-16, WebFetch — Domain registrant details (name, phone) and charge approval stay with a person. Quote: "Ask a person to approve the price, paying team, and, for a purchase, automatic renewal."
- **E144** /home/user/Autonomy-Research/research/tool-registry.md:279 — local file, tool not named in the note — Slack app install still needs an admin click (existing registry row, edge-cases-and-setup-list.md). Quote: "workspace install still needs an admin click"
- **E145** /home/user/health-management/docs/design/ops.md:44-45 — local file, tool not named in the note — John's deploy.sh refuses unless CI for the exact commit is green. Quote: "**refuses** unless `ci_gate.py verify` finds the newest CI run for that exact commit succeeded with every job green"
- **E146** https://sre.google/workbook/canarying-releases/ — 2026-10-16, WebFetch — Canary evaluation: compare to control, use absolute SLOs, one canary at a time. Quote: "It is important to also use absolute measures, such as defined SLOs, to ensure the system is operating correctly."
- **E147** https://sre.google/workbook/canarying-releases/ — 2026-10-16, WebFetch — Releases small and automated. Quote: "Deployments should be performed by computers, not humans."

Data note (rule: page instructions are data): pages from vercel.com contain lines addressed to agents ("For AI
agents: Follow these links to understand how this page connects to the rest of the Vercel ecosystem", and
front-matter `install_vercel_plugin: npx plugins add vercel/vercel-plugin`); the workers did not follow them and
neither does this file.

## Implications for the autonomous engineer

Each item rests on the Evidence above; items marked *inference* come from the workers' marked inferences.

1. **A `deploy` skill with the Q1 matrix as its decision table** (*inference*). The engineer picks a platform by
   workload, not by tool name, and defaults to Cloudflare Workers (E1, E5, E6), Cloud Run from source (E26, E27)
   and the existing VM for always-on processes (E29).
2. **CLI plus token, MCP read-only** (*inference* from E38 to E44). Deploy tokens live in the vault and reach the
   CLI by environment; a PreToolUse hook allowlists the deploy commands per project and blocks any `--amount`,
   registrar or billing command without a matching approval.
3. **One gate mechanism for money, data and store** (*inference* from E97 to E100, E143, E126). A typed request
   on the Channels/Telegram approval channel names amount, payee and what it unlocks; the action stays blocked
   until a matching reply from an allowlisted sender (E138). The engineer never holds a Registrar-write token
   (E95, E96), stages Android releases no further than the internal track (E82, E83), and never runs contract or
   destructive migrations (E124, E126).
4. **Promote is gated; rollback is not** (*inference* from E115 to E125). Preview per branch, John approves
   production, the engineer rolls back on failed health checks without asking and reports afterwards.
5. **Alerts do not depend on the Claude session** (*inference* from E137, E129, E131, E133). Uptime and cron
   checks page John directly; the engineer reads their status on its next run.
6. **Copy John's health-app ops patterns** (E114, E126, E127, E139, E145): OIDC and Workload Identity
   Federation, CI-green gate on the exact SHA, add-only migrations, nightly `pg_dump`, `/healthz` with backup
   status, two uptime checks.
7. **Secrets by pipe only** (*inference* from E102 to E108, E104). A doctor check and deny rules forbid `echo
   VALUE |`, `cat .env` and reads of `.env*`; spike 10 must prove the value never reaches a transcript.
8. **n8n stays, but under git** (*inference* from E45 to E51). A nightly export job commits workflow JSON, and the
   engineer edits n8n only after that export exists.
9. **Mobile defaults** (*inference* from E69 to E80): the bootstrap gains an optional Android SDK plus Gradle step
   for Capacitor apps; Play and Apple enrollment are on John's human-only list.
10. **Registry upkeep.** New and changed rows are in `research/tool-registry.md` under Engineer deployment; the
    rows for Cloudflare Access and Supabase Free no longer state the free-seat count and weekly pause, which
    rested on search highlights only.

## Tools evaluated

| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Cloudflare Workers + wrangler (static assets, cron, webhook receivers) | https://developers.cloudflare.com/workers/platform/limits/ | 100k requests/day free; static assets with SPA fallback; token from env for CI; cron with local test route | hosted | 2026-10-16 | Use: default for static, edge, light cron and webhook receivers; spike headless token deploy |
| Cloudflare D1 / R2 | https://developers.cloudflare.com/d1/platform/pricing/ | D1 "5 million / day" reads; R2 "10 GB-month / month" | hosted | 2026-10-16 | Use with Workers |
| Cloudflare Pages | https://developers.cloudflare.com/pages/platform/limits/ | Static hosting, 20,000 files on Free | hosted | 2026-10-16 | Fallback to Workers static assets; spike which is preferred |
| Cloudflare Containers | https://developers.cloudflare.com/containers/pricing/ | Containers inside Workers; paid allowance only | hosted | 2026-10-16 | Skip: paid |
| Cloudflare Access (Zero Trust) | https://developers.cloudflare.com/api/resources/zero_trust/subresources/access/subresources/applications/methods/create/ | Deny-by-default identity gate; app create by API with `Access: Apps and Policies Write`; free-seat count unverified (search highlight only) | hosted | 2026-10-16 | Use for private apps; spike API app + policy and confirm free plan |
| Cloudflare Tunnel | https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/ | Outbound-only tunnel to a VM service; price not on page | VM | 2026-10-16 | Use for VM-hosted apps and receivers; price unverified |
| Cloudflare MCP servers | https://github.com/cloudflare/mcp-server-cloudflare | Official remote MCPs, each needing a scoped API token; read/write split unverified | hosted remote MCP | 2026-10-16 | Fallback for reads; use wrangler for deploys |
| Cloudflare API tokens (zone-scoped) | https://developers.cloudflare.com/fundamentals/api/get-started/create-token/ | Per-resource token scoping; leaked token acts with full authorization | hosted | 2026-10-16 | Use: narrowest DNS token |
| Cloudflare Registrar API (beta) | https://developers.cloudflare.com/registrar/registrar-api/ | Register by API; no renewals by API | hosted | 2026-10-16 | Use only behind the spend gate; engineer does not hold the token |
| Wrangler secret / rollback / tail | https://developers.cloudflare.com/workers/wrangler/commands/workers/ | Piped secrets, rollback, tail, JSON output | CLI | 2026-10-16 | Use |
| Vercel Hobby + CLI | https://vercel.com/docs/plans/hobby | Hosting; CLI env auth; personal non-commercial only; 30-day lockout over limits | hosted | 2026-10-16 | Alternative for personal Next.js |
| Vercel MCP | https://vercel.com/docs/agent-resources/vercel-mcp | OAuth remote MCP; can deploy | hosted | 2026-10-16 | Skip for unattended deploys (OAuth); read use only |
| Vercel Deployment Protection | https://vercel.com/docs/deployment-protection | Vercel Authentication free on all plans; password protection paid | hosted | 2026-10-16 | Fallback gate for Vercel previews |
| Vercel CLI domains / rollback / env | https://vercel.com/docs/cli/domains | Price quote then human-approved charge; rollback and promote; env via stdin | CLI | 2026-10-16 | Use; copy the two-step approval |
| Netlify Free + CLI | https://docs.netlify.com/manage/accounts-and-billing/billing/billing-for-credit-based-plans/credit-based-pricing-plans/ | 300 credits/month hard cap; `NETLIFY_SITE_ID` | hosted | 2026-10-16 | Alternative; watch credit cap |
| Netlify MCP / skills plugin | https://docs.netlify.com/build/build-with-ai/netlify-mcp-server/ | Remote MCP via connector, plugin or agent | hosted / plugin | 2026-10-16 | Reference; auth method unverified |
| Fly.io (incl. secrets import, deploy --image) | https://docs.fly.io/about/pricing | Container PaaS; card after trial; per-app deploy token; stdin secrets with `--stage` | hosted | 2026-10-16 | Reject for free-first; commands apply only if a paid Fly app is chosen |
| Railway | https://docs.railway.com/pricing/plans | $1 free credit; environment-scoped project tokens | hosted | 2026-10-16 | Paid alternative for container + Postgres |
| Render Free | https://render.com/docs/free | Free Postgres expires 30 days | hosted | 2026-10-16 | Reject |
| Supabase Free + CLI + MCP | https://supabase.com/docs/guides/getting-started/mcp | Postgres, auth, storage, edge functions; 2 free projects; scoped access token; MCP feature groups; idle pause unverified (search highlight only) | hosted | 2026-10-16 | Use for Postgres-with-auth apps; spike pause |
| Supabase pg_cron + edge functions | https://supabase.com/docs/guides/cron | SQL cron calling edge functions; 10-minute job guidance | hosted | 2026-10-16 | Only if data is already in Supabase |
| Neon Free | https://neon.com/docs/introduction/plans | Serverless Postgres, 100 CU-hours/project/month | hosted | 2026-10-16 | Use as Postgres for Cloud Run or Workers; API flow unverified |
| Deno Deploy Free | https://deno.com/deploy/pricing | Personal-use hosting, 512 MB memory | hosted | 2026-10-16 | Alternative; deploy flow unverified |
| Google Cloud Run | https://cloud.google.com/run/pricing | Container service, free tier per billing account; `--source` deploy without Dockerfile | GCP | 2026-10-16 | Use for container APIs in John's GCP project |
| Tailscale Funnel | https://tailscale.com/kb/1223/funnel | Public exposure of a local service, bandwidth capped | hosted + client | 2026-10-16 | Reject as private login |
| Claude Marketplace deploy plugins (Vercel, Cloudflare, Netlify, Supabase) | https://claude.com/marketplace/plugins | Vendor plugins and connectors | plugin | not opened (search highlights only) | Reference only; unverified; prefer CLI + scoped token |
| n8n self-hosted (Community) | https://github.com/n8n-io/n8n | Visual workflow engine; internal-business licence; API on by default; no git or environments | VM | 2026-10-16 | Keep for John's visual flows; Postgres, nightly export to git |
| n8n Cloud | https://n8n.io/pricing/ | Hosted n8n; Starter 20 EUR/month annual, 2.5K executions; no API on trial | cloud | 2026-10-16 | Fallback; small quota, paid |
| n8n instance MCP | https://docs.n8n.io/advanced-ai/mcp/accessing-n8n-mcp-server/ | Create and edit flagged workflows from an MCP client | n8n 2.13+ | 2026-10-16 | Use after spike |
| GitHub Actions schedule | https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows | Cron with load delays; 60-day auto-disable on public repos | GitHub | 2026-10-16 | Fallback for repo-bound jobs |
| systemd timers | https://man7.org/linux/man-pages/man5/systemd.timer.5.html | `Persistent=` catch-up of missed runs | VM | 2026-10-16 | Use: default VM scheduler |
| Trigger.dev | https://trigger.dev/pricing | Durable tasks; free credit | cloud / self-host | 2026-10-16 | Fallback if durable retries needed |
| Inngest | https://www.inngest.com/pricing | Durable functions, 50k executions/month free | cloud | 2026-10-16 | Fallback |
| Windmill | https://www.windmill.dev/pricing | Scripts and flows, free self-host, unlimited executions | self-host | 2026-10-16 | Fallback; licence unverified |
| Temporal | (not opened) | Durable workflow engine | - | not opened | Reject for one user; not researched |
| Gradle wrapper (Android CLI build) | https://developer.android.com/build/building-cmdline | Headless build and sign, no Android Studio | Linux VM | 2026-10-16 | Use; spike SDK setup |
| Bubblewrap / Trusted Web Activity | https://developer.chrome.com/docs/android/trusted-web-activity/overview | Wraps a PWA as an Android app (page dated 2020) | Linux VM | 2026-10-16 | Fallback for Play-listing a PWA |
| Capacitor | https://capacitorjs.com/docs/android | Web app in an Android shell; CLI or Android Studio | Linux VM | 2026-10-16 | Use when native plugins needed; spike headless |
| Expo EAS Build / local build | https://docs.expo.dev/build-reference/local-builds/ | Cloud 15 free builds/month; `--local` on Linux | Expo cloud or VM | 2026-10-16 | Fallback if React Native chosen |
| EAS Submit | https://docs.expo.dev/submit/android/ | Uploads to internal track via service account; no listing | Expo cloud / CLI | 2026-10-16 | Use if Expo; first-upload claim conflicts with fastlane |
| fastlane supply | https://docs.fastlane.tools/actions/upload_to_play_store/ | Uploads binaries and listing, promotes tracks; first build manual | Linux VM | 2026-10-16 | Use for non-Expo |
| Firebase App Distribution | https://firebase.google.com/docs/app-distribution | Tester distribution via CLI in CI; price not seen | Google cloud | 2026-10-16 | Fallback to `adb install` |
| Codemagic | https://codemagic.io/pricing/ | Cloud macOS builds, 500 free minutes/month | cloud | 2026-10-16 | Use for iOS later |
| Health Connect SDK | https://developer.android.com/health-and-fitness/health-connect/get-started | Native Android health API, Gradle dependency | Android | 2026-10-16 | Needs a wrapper or native app, not a PWA |
| GitHub OIDC | https://docs.github.com/en/actions/reference/security/oidc | Short-lived cloud tokens with subject pinning | GitHub Actions | 2026-10-16 | Use |
| GitHub environment reviewers | https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/review-deployments | Human approval of jobs awaiting review | GitHub | 2026-10-16 | Use if available on plan |
| Infisical (free) | https://infisical.com/pricing | Secrets manager, unlimited projects | hosted / self-host | 2026-10-16 | Fallback vault if no 1Password |
| UptimeRobot free | https://uptimerobot.com/pricing/ | 50 monitors; hobby positioning | hosted | 2026-10-16 | Use; integrations unverified |
| healthchecks.io Hobbyist | https://healthchecks.io/pricing/ | 20 cron checks | hosted | 2026-10-16 | Use for cron |
| Sentry Developer (free) | https://sentry.io/pricing/ | 5k errors, email alerts | hosted | 2026-10-16 | Use for errors, not paging |
| ntfy | https://docs.ntfy.sh/publish/ | HTTP push by topic; topic acts as password | hosted / self-host | 2026-10-16 | Use for alerts; auth unread |
| Pushover | https://pushover.net/pricing | $4.99 one-time push | hosted | 2026-10-16 | Fallback push |
| Twilio SMS | https://www.twilio.com/en-us/sms/pricing/us | $0.0083/segment plus number and 10DLC fees | hosted | 2026-10-16 | Reject by default |
| Telegram Bot API | https://core.telegram.org/bots/api | HTTPS send with bot token | hosted | 2026-10-16 | Use: shares the approval channel |
| Google SRE canarying | https://sre.google/workbook/canarying-releases/ | Canary, rollback and SLO principles | docs | 2026-10-16 | Reference |
| Apple Developer enrollment | https://developer.apple.com/programs/enroll/ | $99/yr, legal-name verification, legal authority for orgs | web | 2026-10-16 | Human-only step |

## Open questions

**Claims excluded (26), backed only by a search highlight or by no source:**
1. Supabase Free projects pause after a week of low activity, restorable for 90 days (https://supabase.com/docs/guides/platform/free-project-pausing and https://supabase.com/pricing, Exa highlights only). Spike 4.
2. Cloudflare Zero Trust Free covers up to 50 users (https://www.cloudflare.com/plans/, Exa highlight).
3. Cloudflare launched the free plan as up to 50 seats (https://blog.cloudflare.com/teams-plans/, Exa highlight, 2020 post). With 2 and 3 excluded, the free-seat count and price of Access are unverified; the Zero Trust pricing docs URL returned 404.
4. Supabase Free includes 50,000 MAU of auth (https://supabase.com/pricing, Exa highlight).
5. Static for assets, serverless for bursts, containers for continuity (https://displaying.cloud/static-vs-serverless-vs-container-hosting-what-should-you-deploy-where, Exa highlight).
6. Serverless functions cannot hold WebSockets or long-polling (https://blog.railway.com/p/serverless-functions-vs-containers-cicd-database-connections-cron-jobs-and-long-running-tasks, Exa highlight, vendor).
7. The workload, not the Dockerfile, decides the platform (https://vercel.com/i/which-platform-should-host-your-docker-app, Exa highlight, vendor).
8. A permanent bot connection needs an always-running process; Netlify does not run containers (https://flaviocopes.com/where-to-host/, Exa highlight).
9. Postgres on the same VPS means "You also become the ops team" (https://flaviocopes.com/where-to-host/, Exa highlight).
10. Vercel Claude Marketplace plugin offers `/deploy`, `/vercel-logs`, `/vercel-setup` (https://claude.com/marketplace/plugins/vercel, Exa highlight).
11. Cloudflare Claude Marketplace plugin is skills only (https://claude.com/marketplace/plugins/cloudflare, Exa highlight).
12. Netlify connector can create, deploy and manage sites (https://claude.com/marketplace/connectors/netlify, Exa highlight).
13. Supabase Claude plugin covers database ops, auth, storage (https://claude.com/marketplace/plugins, Exa highlight).
14. Anthropic's official marketplace is mostly partner plugins, community plugins unreviewed (https://code.claude.com/docs/en/plugins/anthropic-marketplaces, Exa highlight).
15. Self-hosted n8n failure modes: SQLite default, OOM, unbounded history, unrestored backups (https://www.stackledge.com/blog/self-hosting-n8n-in-production-what-breaks, Exa highlights).
16. n8n queue-mode main-process memory leak (https://github.com/n8n-io/n8n/issues/37342, Exa highlights).
17. n8n v2 queue-mode error rates rose (https://community.n8n.io/t/after-upgrading-n8n-self-hosted-to-v2-x-queue-mode-reliability-much-worse/247235, Exa highlights).
18. Withings URL rules: HTTPS only, no IPs, ports 80/443, HEAD support (https://developer.withings.com/developer-guide/v3/data-api/notifications/notification-subscribe/, Exa highlights).
19. n8n main instance handles timers and webhook calls in queue mode (https://docs.n8n.io/deploy/host-n8n/configure-n8n/scaling/enable-queue-mode, Exa highlights).
20. PWA capability gaps, Background Sync on Android but not iOS (https://toimi.pro/blog/pwa-vs-native-app/, Exa highlights).
21. iOS 26 opens every Home Screen site as a web app (https://progressivewebapps.com/blog/the-state-of-progressive-web-apps-in-2026/, Exa highlights).
22. Apple reversed removing Home Screen web apps in the EU (https://openpwa.net/reference/platforms/ios-by-version/, Exa highlights; Apple's EU page was not opened).
23. App Store rejects thin website wrappers (https://toimi.pro/blog/pwa-vs-native-app/, Exa highlights).
24. Cloudflare dashboard is the only way to manage the registrar address book and agreement (create-registration page, Exa highlight, not opened).
25. A third-party guide lists Fly.io among hosts for workers (flaviocopes.com, search highlight; framing only, Fly's own page sets the cost).
26. Slack Events API requires a 3 s acknowledgement (uncited; Slack docs not opened).

Also from the search-highlight-only page behind E96: the Registrar API's need for a stored payment method and
default contact set up in the dashboard, and the exclusion of premium domains.

**Unresolved contradictions.**
- First Play upload: Expo says `eas submit` works out of the box (https://docs.expo.dev/submit/android/); fastlane
  says one build must be uploaded manually first (https://docs.fastlane.tools/actions/upload_to_play_store/).
  Spike 9.
- Withings response contract: retry when the response is not "HTTP < 400" against "return HTTP 2xx within a few
  seconds", same overview page. Spike 6.
- Cloudflare Pages against Workers static assets: neither opened page ranks them. Spike 1.

**Gaps (pages that did not open or were not read).**
- Web hosting: Cloudflare Workers Free build limits not on the page opened; commercial-use terms only found for
  Vercel Hobby; Cloud Run Jobs and request-based egress not read (Exa fetch truncated at 6,000 characters);
  Render deploy endpoints and deploy hooks, Railway token creation UI, Fly `FLY_API_TOKEN` not stated; Neon
  `neonctl`/`NEON_API_KEY` flow not opened; Cloud Run min-instances and long-lived outbound connections not
  opened; no independent build or cold-start benchmark.
- Sign-in: Access policy and service-token API calls not opened; Tailscale Personal pricing not opened; Cloudflare
  Zero Trust pricing docs returned 404; IAP for Cloud Run not opened.
- MCP and plugins: Cloudflare MCP per-server tools and write split read via extract only; Vercel plugin `/deploy`
  with a token unverified; Netlify MCP auth method not stated; no repo cloned this run.
- Automation: Cloud MCP/API credential creation with write-only secrets untested; n8n Cloud monthly price and
  whether Starter has MCP build tools unknown; Sustainable Use License page on docs.n8n.io returned "Page Not
  Found"; Temporal, Trigger.dev and Inngest retry semantics not opened; Windmill licence unverified; GitHub
  Actions free-minute docs URL returned 404; Slack Events API ack rules, Cloudflare Tunnel pricing, Cloudflare
  Queues/D1/KV free limits not opened.
- Mobile: no page opened for Flutter, React Native CLI, Capacitor headless Gradle build, a Capacitor Health
  Connect plugin, widgets, Bubblewrap's current README; Android SDK install on a headless VM unverified; whether
  the 2026 advanced-flow waiting period affects non-ADB APK installs; Firebase App Distribution price; whether
  the limited distribution account (launching "in August" 2026 per the page) is live; Android Publisher API
  `edits.bundles.upload` reference returned 404; Apple web push docs returned a title stub; TestFlight, EAS iOS
  credentials, GitHub macOS runner pricing and Apple's EU page not opened; John's country unknown for the
  verification regions.
- Operations: per-platform TLS for Vercel, Fly and Cloudflare custom domains; Cloudflare Workers deploy-token
  permission names; Doppler and Better Stack free tiers; `gh secret set` stdin; whether a vault CLI error could
  print a value into the transcript; Fly rollback command (derived from `--image` only); Cloudflare Pages
  rollback and Vercel promote semantics; GitHub environment-reviewer availability on John's plan; UptimeRobot
  free integrations; Cloudflare health checks and Notifications pricing; Sentry free integrations; ntfy auth and
  self-hosting; whether a stopped Claude session still delivers Telegram messages; Stripe KYC, Google Play
  enrollment details, OAuth consent automation rules, registrar terms on agent purchases; whether an agent may act
  as an account holder (legal question).
- Citation drift: E144 cites `research/tool-registry.md:279` as written in the note; the Slack
  `apps.manifest.create` row no longer sits at line 279 of that file (it was at line 290 when this file was
written; the registry is edited concurrently), so the verifier should locate it by text.
