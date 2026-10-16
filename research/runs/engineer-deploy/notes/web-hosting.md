# Web hosting free tiers, token-driven deploys and when to use containers

Brief: Build the web deploy matrix for an autonomous Claude Code engineer: which platform for which project type, deployed unattended from a CLI or API token, free tier first.
Run: research/runs/engineer-deploy/PLAN.md

Method note: pages opened with WebFetch (which returns a model-written extract, so quotes below are the strings that extract put in quotation marks), Exa fetch/search highlights for pages named in the line. Parallel Search returned "Too Many Requests" on the first call and was not used again. All opened 2026-10-16. Pages from vercel.com contain lines addressed to agents ("For AI agents: Follow these links to understand how this page connects to the rest of the Vercel ecosystem", and front-matter `install_vercel_plugin: npx plugins add vercel/vercel-plugin`); page contains instructions addressed to agents; not followed.

## Platform matrix: what each deploys, token command, free limits, human steps

### Takeaway
Free-and-unattended winners: Cloudflare (static + Workers + D1 + R2, token-scoped `wrangler`, no card needed for Free), Vercel Hobby (personal only, `VERCEL_TOKEN`), Netlify Free (hard credit cap, `NETLIFY_AUTH_TOKEN`), Supabase Free (Postgres+auth, pauses after a week idle), Neon Free (Postgres, scale-to-zero), Cloud Run (card-on-file GCP billing, large free tier). Fly.io and Railway have no real free tier now, Render Free sleeps and its free Postgres expires in 30 days; Deno Deploy Free is fine for personal. Medium-high confidence; some numbers come from WebFetch extracts and should be re-read from the cited page before a build depends on them.

### Cited findings
- Cloudflare Workers Free: 100,000 requests/day, 10 ms CPU, 100 Workers per account — https://developers.cloudflare.com/workers/platform/limits/, opened 2026-10-16, WebFetch — Quote: "Accounts on the Workers Free plan have a daily request limit of 100,000 requests, resetting at midnight UTC."
- Cloudflare D1 Free: 5M rows read/day, 100k written/day, 5 GB — https://developers.cloudflare.com/d1/platform/pricing/, opened 2026-10-16, WebFetch — Quote: "5 million / day"
- Cloudflare R2 Free: 10 GB-month, free egress — https://developers.cloudflare.com/r2/pricing/, opened 2026-10-16, WebFetch — Quote: "10 GB-month / month"
- Cloudflare Pages Free: 500 builds/month, 20,000 files, 25 MiB per file — https://developers.cloudflare.com/pages/platform/limits/, opened 2026-10-16, WebFetch — Quote: "Cloudflare Pages sites can contain up to 20,000 files on the Free plan."
- Workers can host static assets with the code in one deploy (SPA fallback via `not_found_handling`) — https://developers.cloudflare.com/workers/static-assets/, opened 2026-10-16, WebFetch — Quote: "Sets your application to return a `200 OK` response with `index.html` for requests which don't match a static asset."
- Wrangler reads a scoped token from env, for CI and automation — https://developers.cloudflare.com/workers/wrangler/system-environment-variables/, opened 2026-10-16, WebFetch — Quote: "The API token for your Cloudflare account, can be used for authentication for situations like CI/CD, and other automation."
- Cloudflare Containers: no Free allowance, Workers Paid ($5/month) with 25 GiB-hours memory, 375 vCPU-minutes, 200 GB-hours disk — https://developers.cloudflare.com/containers/pricing/, opened 2026-10-16, WebFetch — Quote: "25 GiB-hours/month included"
- Cloudflare Containers run any language as part of a Worker, defined in config with `"image": "./Dockerfile"` — https://developers.cloudflare.com/containers/, opened 2026-10-16, WebFetch — Quote: "Run code written in any programming language, built for any runtime, as part of apps built on Workers."
- Vercel Hobby: 1M function invocations, 100 GB fast data transfer, 1M CDN requests, 100 deployments/day, 300 s function max — https://vercel.com/docs/plans/hobby, opened 2026-10-16, WebFetch — Quote: "Function Invocations | First 1,000,000"
- Vercel Hobby is personal, non-commercial only — https://vercel.com/docs/plans/hobby, opened 2026-10-16, WebFetch — Quote: "the Hobby plan restricts users to non-commercial, personal use only."
- Vercel CLI authenticates with `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID`, and has `--non-interactive` — https://vercel.com/docs/cli/global-options, opened 2026-10-16, WebFetch — Quote: "set `VERCEL_ORG_ID` and `VERCEL_PROJECT_ID` as environment variables to skip project linking."
- Vercel exceeding Hobby limits means waiting 30 days — https://vercel.com/docs/plans/hobby, opened 2026-10-16, WebFetch — Quote: "you will have to wait until 30 days have passed before you can use the feature again."
- Netlify Free is credit based with a hard limit (300 credits; 1 GB bandwidth = 20 credits; production deploy = 15 credits) — https://docs.netlify.com/manage/accounts-and-billing/billing/billing-for-credit-based-plans/credit-based-pricing-plans/, opened 2026-10-16, WebFetch — Quote: "$0/month, forever, for 300 credits/month with a hard limit and no auto recharge option."
- Netlify CLI deploys non-interactively with two env vars — https://docs.netlify.com/api-and-cli-guides/cli-guides/get-started-with-cli/, opened 2026-10-16, WebFetch — Quote: "Project ID** is exactly the value `NETLIFY_SITE_ID` expects."
- Fly.io has no general free tier; trial is 2 h or 7 days, then a card is required; smallest machine about $2.19 per 30 days — https://docs.fly.io/about/pricing, opened 2026-10-16, WebFetch — Quote: "you'll need to add a credit card to keep using billable resources."
- Fly deploy token is scoped to one app — https://docs.fly.io/flyctl/tokens-create-deploy, opened 2026-10-16, WebFetch — Quote: "Create an API token limited to managing a single app and its resources."
- Railway: Free plan $1 credit/month with 1 replica and 0.5 GB RAM; Hobby $5/month; post-paid card required — https://docs.railway.com/pricing/plans, opened 2026-10-16, WebFetch — Quote: "For running small apps with $1 of free credit per month"
- Railway CI deploy uses a project token scoped to one environment — https://docs.railway.com/cli/deploying, opened 2026-10-16, WebFetch — Quote: "Project tokens are scoped to a specific environment and can only perform deployment-related actions."
- Render Free web service sleeps after 15 minutes, 750 instance hours, free Postgres expires after 30 days, "Do not use them for production applications" — https://render.com/docs/free, opened 2026-10-16, WebFetch — Quote: "Free Render Postgres databases expire 30 days after creation."
- Render API needs an API key (create/deploy endpoint names not on the page I opened) — https://render.com/docs/api, opened 2026-10-16, WebFetch — Quote: "All Render API requests require authentication via API key."
- Supabase Free: 2 active projects, 500 MB DB, 50,000 MAU, 1 GB storage, 5 GB egress, 500,000 edge function invocations — https://supabase.com/docs/guides/platform/billing-on-supabase, opened 2026-10-16, WebFetch — Quote: "You are granted two free projects."
- Supabase Free projects pause after a week of low activity; paused projects restorable for 90 days — https://supabase.com/docs/guides/platform/free-project-pausing (Exa search highlight, page not fetched separately) and https://supabase.com/pricing — Quote: "Supabase pauses Free Plan projects that show low activity over a 7-day period to save server resources."
- Supabase CLI non-interactive: scoped personal access token, `supabase link`, `supabase db push` — https://supabase.com/docs/guides/deployment/managing-environments, opened 2026-10-16, WebFetch — Quote: "`SUPABASE_ACCESS_TOKEN` is a scoped personal access token limited to the projects this workflow deploys to."
- Neon Free: 100 projects, 1 GB per project (20 GB total), 100 CU-hours/project/month, compute suspends after 5 min idle — https://neon.com/docs/introduction/plans, opened 2026-10-16, WebFetch — Quote: "100 CU-hours/project/month (enough to run a 0.25 CU compute in a project for 400 hours/month)."
- Deno Deploy Free: 1M requests, 20 GiB egress, 10 h active CPU; described as for personal use; commercial terms not on page — https://deno.com/deploy/pricing, opened 2026-10-16, WebFetch — Quote: "For personal use and smaller projects"
- Deno Deploy docs: memory cap 512 MB, 1 GB deploy size — https://docs.deno.com/deploy/pricing_and_limits/, opened 2026-10-16, WebFetch — Quote: "Applications have a maximum memory allocation of 512MB"
- Cloud Run free tier is aggregated per billing account per month (request-based: 2M requests, 180,000 vCPU-s, 360,000 GiB-s; instance-based: 240,000 vCPU-s, 450,000 GiB-s) and egress 1 GiB North America — https://cloud.google.com/run/pricing, opened 2026-10-16, Exa fetch — Quote: "First 180,000 vCPU-seconds free per month"
- `gcloud run deploy SERVICE --source .` needs no Dockerfile (buildpacks) and no local Docker — https://docs.cloud.google.com/run/docs/deploying-source-code, opened 2026-10-16, WebFetch — Quote: "uses a Dockerfile if present, although it's not required."
- Cloud Run IAM: public access is a `roles/run.invoker` binding for `allUsers`; org policy can block it — https://docs.cloud.google.com/run/docs/authenticating/public, opened 2026-10-16, WebFetch — Quote: "Enabling the Cloud Run Invoker IAM check in the Google Cloud console removes any existing"
- Health app today: one GCP VM, Docker Compose, Cloudflare Tunnel, Access limited to John's Google account — /home/user/health-management/docs/architecture.md:8-10 — Quote: "One small Google Cloud VM runs four containers with Docker Compose: `cloudflared`, `api` (FastAPI), `worker` (Python)"

### Contradictions
- Cloudflare Pages is not recommended over Workers on the limits page I opened, yet the Workers static-assets page presents Workers as able to host static assets in one deploy; neither page ranks them. Not resolved; see Gaps.
- Fly.io: a third-party guide (flaviocopes.com, 2026-09-14, search highlight) lists Fly.io among hosts for workers, while Fly's own page shows no free tier. Not a conflict of fact, only of framing; cost rests on Fly's page.

### Inferences
- Human steps that no token removes (my inference from the cited pages, not a quoted claim): account creation and email verification on each platform; a card on file for GCP billing (Cloud Run free tier is applied to a billing account), Fly after trial, and Railway ("post-paid card"); creating the first scoped token in a dashboard; Cloudflare Zero Trust team creation (the health app's SETUP.md already lists this as a manual step).
- Because John's health app already runs on GCP with Cloudflare Tunnel + Access, new small projects should default to Cloudflare for static/edge and to the existing GCP project (Cloud Run, `--source`) for containers; this reuses accounts and cards he already has.
- Deploy matrix (proposal):
  - Static site, SPA: Cloudflare Workers static assets (or Pages), `wrangler deploy` with scoped token. Alt: Netlify, Vercel (Vercel only if personal).
  - Serverless API + small DB, edge: Workers + D1/KV/R2.
  - Next.js or similar SSR with Vercel features, personal use: Vercel Hobby, `VERCEL_TOKEN`.
  - Postgres-backed app with auth and storage: Supabase Free (accept weekly pause; keep-alive ping or accept restore) or Neon Free plus own auth.
  - Container API or containerised health-app style service: Cloud Run `--source` (scale to zero) with Neon or Cloud SQL; or keep the existing VM.
  - Always-on bot: not free on any platform I checked (Fly, Railway have no real free tier; Render Free sleeps); use the existing GCP VM or a $5 VPS or Railway Hobby.

### Gaps
- Cloudflare Workers Free build minutes, Workers Builds limits: page I opened says nothing ("The page does not mention build limits"); not found.
- Commercial-use clauses: found only Vercel Hobby (explicit); Netlify, Render, Deno, Cloudflare pages do not state it on the pages opened; terms of service not opened.
- Supabase free-project pausing page fetched only as an Exa search highlight, not opened directly.
- Cloud Run free tier "Cloud Run Jobs" and exact request-based egress not read; Exa fetch truncated at 6,000 characters.
- Render deploy endpoints and deploy hooks, Railway token creation UI, Fly `FLY_API_TOKEN` env var: pages did not state them.
- Neon API/CLI token (`neonctl`, `NEON_API_KEY`) deploy flow not opened.

## Sign in from anywhere for a private single-user app

### Takeaway
Cloudflare Access on the free Zero Trust plan (50 users) is the best fit and is already John's pattern for the health app; it can be configured by API with an `Access: Apps and Policies Write` token. Tailscale Funnel is public exposure, not a login, and does not fit a private app by itself. Vercel's free protection is Vercel Authentication only (Vercel accounts); Supabase auth is an in-app login you build. Medium confidence.

### Cited findings
- Cloudflare Zero Trust Free covers up to 50 users — https://www.cloudflare.com/plans/ (Exa search highlight) — Quote: "User Limit 50 users No limit No limit"
- Cloudflare launched the free plan as "up to 50 seats of Access and Gateway" — https://blog.cloudflare.com/teams-plans/ (Exa highlight, 2020 post, so date-sensitive) — Quote: "protects up to 50 users at no cost"
- Access apps are deny-by-default; dashboard flow is Zero Trust > Access controls > Applications — https://developers.cloudflare.com/cloudflare-one/access-controls/applications/http-apps/self-hosted-public-app/, opened 2026-10-16, WebFetch — Quote: "All Access applications are deny by default"
- Access applications can be created by API: `POST /{accounts_or_zones}/{account_or_zone_id}/access/apps` with token permission `Access: Apps and Policies Write` — https://developers.cloudflare.com/api/resources/zero_trust/subresources/access/subresources/applications/methods/create/, opened 2026-10-16, WebFetch — Quote: "Access: Apps and Policies Write"
- Tailscale Funnel is available on all plans, needs MagicDNS, HTTPS, a `funnel` node attribute, exposes to anyone, with non-configurable bandwidth limits — https://tailscale.com/kb/1223/funnel, opened 2026-10-16, WebFetch — Quote: "Traffic sent over a Funnel is subject to non-configurable bandwidth limits."
- Vercel Deployment Protection: Vercel Authentication and "All Deployments" scope work on every plan; Password Protection is Pro $20/project/month; Passport (own IdP) Enterprise only — https://vercel.com/docs/deployment-protection, opened 2026-10-16, WebFetch — Quote: "Vercel Authentication for All Deployments and Deployment Protection Exceptions do not require a paid add-on."
- Supabase Free includes 50,000 MAU of auth — https://supabase.com/pricing (Exa highlight) — Quote: "50,000 monthly active users"
- Cloud Run can require IAM auth instead of being public; IAP for Cloud Run is a separate guide I did not open — https://docs.cloud.google.com/run/docs/authenticating/public, opened 2026-10-16, WebFetch — Quote: "Run `gcloud run services update SERVICE_NAME --invoker-iam-check`" (extract paraphrase of the page; treat as indicative)
- Existing pattern: Tunnel in, Access lets only John's Google account through — /home/user/health-management/docs/architecture.md:9-10 — Quote: "and Cloudflare Access lets only John's Google account through."

### Contradictions
- The 50-user figure comes from a 2020 blog post and a pricing page highlight, not from a current developer docs page (the pricing docs URL returned 404). Settle by reading the live Zero Trust plans page.

### Inferences
- For anything John uses from his phone or any laptop: put the app behind a Cloudflare Tunnel (no inbound port) plus an Access app with a one-email allow policy, created through the API; this needs one hostname on a Cloudflare-managed domain (he has `jpclifeops.com`).
- Vercel Authentication only admits Vercel accounts, so it works for John alone but is a poor fit if the app has to be opened on a borrowed device; use it as a cheap fallback for Vercel-hosted previews.
- Supabase auth is for apps with their own users or when the database policy (RLS) should know the user; for a single user it adds code to maintain compared with Access in front.
- Tailscale Funnel: skip for private apps (public by design); Tailscale serve (tailnet-only) is a different feature I did not research.

### Gaps
- Access policy and service-token API calls (`/access/policies`, service tokens for machine callers) not opened; only the create-application endpoint.
- Tailscale pricing for the Personal plan not opened.
- Cloudflare Zero Trust current free-plan docs page not fetched (404 on /cloudflare-one/pricing/).

## When Docker is the right answer

### Takeaway
Decision rule (my synthesis of vendor and practitioner pages): static files go static; short stateless request/response code goes to functions; use a container when you need a long-lived process, persistent connections, custom binaries, or a framework that expects a full runtime; and prefer a source-deploy (`gcloud run deploy --source .`, buildpacks) so the engineer does not need local Docker. Medium confidence; the sources are largely vendor or blog opinion.

### Cited findings
- Containers fit long-lived processes, WebSockets, background workers; static for files; serverless for short stateless compute — https://displaying.cloud/static-vs-serverless-vs-container-hosting-what-should-you-deploy-where (Exa highlight, 2026-06-11) — Quote: "use static hosting for assets, serverless for bursts of stateless compute, and containers for services that need continuity and control."
- Serverless limits: execution caps, cold starts, no persistent connections — https://blog.railway.com/p/serverless-functions-vs-containers-cicd-database-connections-cron-jobs-and-long-running-tasks (Exa highlight, 2025-12-16; vendor of containers, so biased) — Quote: "WebSockets, server-sent events, and long-polling don't work because connections terminate when the function ends."
- Workload decides, not the Dockerfile; always-on workers and bots need a long-lived-process platform — https://vercel.com/i/which-platform-should-host-your-docker-app (Exa highlight; Vercel is the vendor, and it says its containers do not fit workers) — Quote: "The right platform for a Docker app depends on the workload inside the container, not the container itself."
- A permanent bot connection needs an always-running process; Netlify does not run containers — https://flaviocopes.com/where-to-host/ (Exa highlight, 2026-09-14) — Quote: "A Discord bot that maintains a permanent gateway connection needs an always-running process."
- Same page: Postgres on the same VPS avoids a database fee but you own backups — https://flaviocopes.com/where-to-host/ — Quote: "You also become the ops team."
- Cloud Run builds from source with no Dockerfile and no local Docker — https://docs.cloud.google.com/run/docs/deploying-source-code, opened 2026-10-16, WebFetch — Quote: "A Dockerfile is not required." (extract wording; the page line quoted in the matrix section is the safer verbatim)
- Cloudflare Containers cost the Workers Paid plan (no Free allowance) — https://developers.cloudflare.com/containers/pricing/, opened 2026-10-16, WebFetch — Quote: "25 GiB-hours/month included"

### Contradictions
- None found on the rule itself; vendor pages (Railway, Vercel) each recommend their own model, so treat their bias as known.

### Inferences
- Rule for the engineer: (1) Output is files with no server code: static, no Docker. (2) Stateless handler under the platform time cap with spiky traffic: Worker or Vercel/Netlify function, no Docker. (3) Needs Postgres and an API, can scale to zero: container on Cloud Run via `--source` (Docker not needed locally), Neon or Supabase for data. (4) Needs a process that never exits (Slack Socket Mode bot, queue worker, cron-in-process): always-on container on the existing VM or a paid PaaS; none of the free tiers keep one running (cited above: Render sleeps, Fly/Railway not free).
- The health app is case 4 plus Postgres plus private ingress, which matches its present VM design; moving it to Cloud Run would break Slack Socket Mode (needs a persistent process) unless min-instances is set, which then costs money. (Inference; Cloud Run min-instance pricing not opened.)

### Gaps
- Cloud Run behaviour for long-lived outbound connections (min instances, CPU always allocated) not opened.
- No independent benchmark of build or cold-start behaviour; only opinion pages.

## How Claude Code users deploy today (MCP servers, CLIs, plugins)

### Takeaway
Most vendors ship an official remote MCP plus a Claude marketplace plugin, but for unattended deploys the CLI with a scoped token is the dependable path: remote MCP servers use OAuth in a browser, which an autonomous engineer cannot complete. Vercel MCP can deploy; Supabase MCP can be put in read-only mode; Cloudflare's MCP servers are listed but their read/write split is not stated on the page I opened. Medium confidence.

### Cited findings
- Vercel MCP is a remote MCP with OAuth at mcp.vercel.com, for managing projects and deployments — https://vercel.com/docs/agent-resources/vercel-mcp, opened 2026-10-16, WebFetch — Quote: "It's a remote MCP with OAuth that gives AI tools secure access to your Vercel projects"
- Vercel MCP can deploy code via a `deploy_to_vercel` tool — https://vercel.com/changelog/vercel-mcp-can-now-deploy-code, opened 2026-10-16, WebFetch — Quote: "can now deploy code directly to a new or existing project."
- Vercel advises human confirmation and warns of prompt injection through MCP — https://vercel.com/docs/agent-resources/vercel-mcp, opened 2026-10-16, WebFetch — Quote: "Always enable human confirmation in your workflows to maintain control and prevent unauthorized changes"
- Vercel plugin on Claude Marketplace: `/deploy`, `/vercel-logs`, `/vercel-setup`; handles CLI auth — https://claude.com/marketplace/plugins/vercel (Exa highlight) — Quote: "Run `/deploy` to push your application to production"
- Supabase MCP has `read_only=true`, `project_ref` scoping, feature groups, and a `deploy_edge_function` tool — https://supabase.com/docs/guides/getting-started/mcp, opened 2026-10-16, WebFetch — Quote: "All groups except Storage are enabled by default"
- Supabase recommends read-only for unattended routines (extract wording) — same page — Quote: "This is not foolproof though, so you should always review the output before proceeding with further actions."
- Cloudflare lists many MCP servers; the "Cloudflare API MCP Server" is recommended, several older ones deprecated — https://github.com/cloudflare/mcp-server-cloudflare, opened 2026-10-16, WebFetch — Quote: "an API token that has the scopes (permissions) required for that particular MCP server."
- Cloudflare plugin on Claude Marketplace is skills only (Workers, Wrangler, etc.) — https://claude.com/marketplace/plugins/cloudflare (Exa highlight) — Quote: "Skills for the Cloudflare developer platform: Workers, Durable Objects, Agents SDK, MCP servers, Wrangler CLI, and web performance."
- Netlify: remote MCP, a Netlify connector on Claude Marketplace, and a skills plugin; deploy guidance lives in skills — https://docs.netlify.com/build/build-with-ai/netlify-mcp-server/, opened 2026-10-16, WebFetch — Quote: "Netlify offers an [MCP server](https://github.com/netlify/netlify-mcp), which you can connect to through a connector, plugin, or your agent."
- Netlify connector claims create/deploy/manage/secure sites — https://claude.com/marketplace/connectors/netlify (Exa highlight) — Quote: "Create, deploy, and manage websites on Netlify."
- Supabase Claude plugin: database ops, auth, storage — https://claude.com/marketplace/plugins (Exa highlight) — Quote: "Supabase MCP: Database ops, auth, storage, real-time."
- Anthropic's official marketplace holds mostly partner plugins, and community plugins are not reviewed by Anthropic — https://code.claude.com/docs/en/plugins/anthropic-marketplaces (Exa highlight) — Quote: "Most of what it lists comes from partners and other authors rather than from Anthropic"

### Contradictions
- None found. Note: Cloudflare MCP read vs write is unstated on the opened page; the plugin descriptions are marketing copy.

### Inferences
- For the engineer in a cloud or headless session, OAuth MCP connectors cannot be completed unattended; use CLI plus token in env (Cloudflare `CLOUDFLARE_API_TOKEN`, `VERCEL_TOKEN`, `NETLIFY_AUTH_TOKEN`, `SUPABASE_ACCESS_TOKEN`, `RAILWAY_TOKEN`, Fly deploy token) with a PreToolUse hook limiting which deploy commands run. Use the MCP servers read-only for logs and status; for Supabase use `?read_only=true&project_ref=`.
- Token handling should follow the repo's existing rule: the cloud "network secrets" feature keeps keys out of the VM (tool-registry, Cloud network secrets row).

### Gaps
- Cloudflare MCP per-server tools and which are write: README read via extract only; `cloudflare/mcp` repo not opened or cloned.
- Plugin contents (whether Vercel plugin `/deploy` works with a token non-interactively) not verified; only marketplace copy read. Not installed, per rules.
- Netlify MCP auth method (PAT or OAuth) not stated on the page I opened.
- Not cloned any repo this run (no source-level verification).

## Recommendation, alternatives, rejects, spikes

- Recommendation: Cloudflare (Workers static assets + D1/R2, scoped token via `wrangler`) as the default for web projects; Cloud Run `--source` in John's existing GCP project for container APIs; Neon or Supabase Free for Postgres; Cloudflare Tunnel + Access (API-created, one-email policy) for private sign-in. Always-on bots stay on the existing VM.
- Alternatives: Vercel Hobby (personal Next.js), Netlify Free (credit capped), Deno Deploy Free, Railway Hobby ($5) for a simple container plus Postgres.
- Rejected: Fly.io (no free tier), Render Free (sleeps, Postgres expires in 30 days, "do not use for production"), Tailscale Funnel as login (public exposure), Cloudflare Containers (paid, $5 minimum), Vercel Password Protection ($20 per project), remote OAuth MCP servers as the unattended deploy path.
- Spike before building: (1) create a least-privilege Cloudflare token and run `wrangler deploy` from a headless cloud session; (2) create an Access app and policy via API with that token and confirm login from a phone; (3) `gcloud run deploy --source .` from a service account via Workload Identity, including org-policy `allUsers` behaviour; (4) Supabase 7-day pause vs a keep-alive; (5) confirm Cloudflare Free build limits and whether Pages or Workers static assets is the preferred path.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Cloudflare Workers + wrangler | https://developers.cloudflare.com/workers/platform/limits/ | Workers, static assets; 100k req/day free; `CLOUDFLARE_API_TOKEN` env auth | hosted | 2026-10-16 | Use: default for static and edge |
| Cloudflare D1 / R2 | https://developers.cloudflare.com/d1/platform/pricing/ | SQLite 5 GB, 5M reads/day free; R2 10 GB free, free egress | hosted | 2026-10-16 | Use with Workers |
| Cloudflare Pages | https://developers.cloudflare.com/pages/platform/limits/ | Static hosting, 500 builds/month free | hosted | 2026-10-16 | Fallback to Workers static assets; spike which is preferred |
| Cloudflare Containers | https://developers.cloudflare.com/containers/pricing/ | Containers inside Workers; Workers Paid only | hosted | 2026-10-16 | Skip: paid |
| Cloudflare Access (Zero Trust Free) | https://developers.cloudflare.com/api/resources/zero_trust/subresources/access/subresources/applications/methods/create/ | Identity gate; 50 users free; API-creatable | hosted | 2026-10-16 | Use for private apps; spike API flow |
| Cloudflare MCP servers | https://github.com/cloudflare/mcp-server-cloudflare | Official remote MCPs; read/write split unverified | hosted remote MCP | 2026-10-16 | Fallback for reads; use wrangler for deploys |
| Vercel Hobby + CLI | https://vercel.com/docs/plans/hobby | Hosting, `VERCEL_TOKEN`; personal non-commercial only | hosted | 2026-10-16 | Alternative for Next.js personal projects |
| Vercel MCP | https://vercel.com/docs/agent-resources/vercel-mcp | OAuth remote MCP; can deploy via `deploy_to_vercel` | hosted | 2026-10-16 | Skip for unattended (OAuth); read use only |
| Vercel Deployment Protection | https://vercel.com/docs/deployment-protection | Vercel Authentication free on all plans; password $20/project | hosted | 2026-10-16 | Fallback gate for Vercel previews |
| Netlify Free + CLI | https://docs.netlify.com/manage/accounts-and-billing/billing/billing-for-credit-based-plans/credit-based-pricing-plans/ | 300 credits/month hard cap; `NETLIFY_AUTH_TOKEN` | hosted | 2026-10-16 | Alternative; watch credit cap |
| Netlify MCP / skills plugin | https://docs.netlify.com/build/build-with-ai/netlify-mcp-server/ | Remote MCP, connector and skills plugin | hosted / plugin | 2026-10-16 | Reference; auth method unverified |
| Fly.io | https://docs.fly.io/about/pricing | Container PaaS, no free tier after 2 h/7 d trial | hosted | 2026-10-16 | Reject for free-first; paid option for bots |
| Railway | https://docs.railway.com/pricing/plans | Container PaaS; $1 free credit, Hobby $5; project tokens | hosted | 2026-10-16 | Alternative paid ($5) for container plus Postgres |
| Render | https://render.com/docs/free | Free web service sleeps; free Postgres expires 30 d | hosted | 2026-10-16 | Reject: not for production |
| Supabase Free + CLI + MCP | https://supabase.com/docs/guides/getting-started/mcp | Postgres, auth, storage, edge functions; pauses after 1 week; MCP read-only flag | hosted | 2026-10-16 | Use for Postgres-with-auth apps; spike pause |
| Neon Free | https://neon.com/docs/introduction/plans | Serverless Postgres, 100 CU-h, suspend at 5 min idle | hosted | 2026-10-16 | Use as Postgres for Cloud Run or Workers; API flow unverified |
| Deno Deploy Free | https://deno.com/deploy/pricing | 1M req, 20 GiB egress, 10 h CPU | hosted | 2026-10-16 | Alternative; deployctl flow unverified |
| Google Cloud Run | https://cloud.google.com/run/pricing | Container service with monthly free tier; `gcloud run deploy --source` | GCP | 2026-10-16 | Use for container APIs in John's GCP project |
| Tailscale Funnel | https://tailscale.com/kb/1223/funnel | Public internet exposure of a local service | hosted + client | 2026-10-16 | Reject for private login |
| Claude Marketplace plugins (Vercel, Cloudflare, Netlify, Supabase) | https://claude.com/marketplace/plugins | Vendor plugins and connectors for Claude Code | plugin | 2026-10-16 (marketing copy only, not installed) | Reference; prefer CLI plus token |
