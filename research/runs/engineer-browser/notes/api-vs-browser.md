# API versus browser per task for Attio, Clay, n8n, Outreach and health portals

Brief: Pin down from official documentation which configuration tasks in John's GTM and health systems can be done through an API or MCP server and which need a browser.
Run: research/runs/engineer-browser/PLAN.md

Scope note: stopped early on the coordinator's instruction. Patient portals, FHIR aggregators, the Attio App SDK org block, and Withings plan pricing were not researched; they are under Gaps. All dates below are 2026-10-16.

## Attio: REST v2, official MCP, views, workflows, scopes, limits, App SDK

### Takeaway
The open question is settled: Attio views are GET-only (one list route for objects, one for lists, no create, update or delete), and no REST or MCP route creates or edits Workflows. Objects, attributes (including select options, statuses and bidirectional relationship attributes on objects and lists), lists and list attributes are writable by REST; the MCP covers lists and records but has no attribute-creation, view or workflow tool. Views (table and Kanban) and Workflow building therefore need a browser; Attio Workflows can be triggered over HTTP once a human has built them. Confidence: high for the spec reading, medium for the MCP (docs page, not a live tools/list).

### Cited findings
- REST views are read-only for objects: the only views route on objects is GET, scope object_configuration:read. I enumerated all 53 paths of the downloaded spec; the only paths containing "views" are GET /v2/objects/{object}/views and GET /v2/lists/{list}/views. — https://api.attio.com/openapi/api (downloaded with curl, parsed with python -I), opened 2026-10-16, curl — Quote: "Lists saved views for an object. Results are ordered by view ID (`id.view_id` ascending)."
- Same for list views, scope list_configuration:read. — https://api.attio.com/openapi/api, opened 2026-10-16, curl — Quote: "Lists saved views for a list. Results are ordered by view ID (`id.view_id` ascending)."
- No workflows path exists in the spec: the tag list has no Workflows tag (tags include Objects, Object views, List views, Attributes, Lists, Entries, Webhooks, SQL, Sequences). — https://api.attio.com/openapi/api, opened 2026-10-16, curl — Quote: "Required scopes: `webhook:read-write`." (webhook create; the spec has webhooks but no workflow routes)
- Create object is POST, update PATCH, delete DELETE; scope object_configuration:read-write. — https://api.attio.com/openapi/api, opened 2026-10-16, curl — Quote: "Creates a new custom object in your workspace."
- Attribute create works on objects, lists and activities, with bidirectional relationships. — https://api.attio.com/openapi/api, opened 2026-10-16, curl — Quote: "For record-reference attributes, you can optionally create a bidirectional relationship by providing a `relationship` object."
- Select options can be added by REST on objects, lists and activities (statuses have their own POST/PATCH routes). — https://api.attio.com/openapi/api, opened 2026-10-16, curl — Quote: "Adds a select option to a select attribute on an object, a list or an activity."
- Lists are created by POST /v2/lists, PATCH updates; no DELETE list route exists in the spec path listing. — https://api.attio.com/openapi/api, opened 2026-10-16, curl — Quote: "Creates a new list."
- Scopes are per area, for example object_configuration, list_configuration, activity_configuration, webhook, record_permission; webhooks are workspace-level tokens only. — https://api.attio.com/openapi/api, opened 2026-10-16, curl — Quote: "Required scopes: `webhook:read-write`. Supported token levels: `workspace`."
- Auth: API key or OAuth; only admins grant workspace-level OAuth tokens. — https://docs.attio.com/rest-api/guides/authentication.md, opened 2026-10-16, curl — Quote: "Only workspace admins can grant a workspace-level token."
- Rate limits. — https://docs.attio.com/rest-api/guides/rate-limiting.md, opened 2026-10-16, curl — Quote: "Our rate limit across the whole API is **100 requests per second** for read requests, **25 requests per second** for write requests."
- Official MCP is OAuth, hosted at https://mcp.attio.com/mcp; writes ask confirmation. — https://docs.attio.com/mcp/overview.md, opened 2026-10-16, curl — Quote: "Authenticates as your Attio user with OAuth, and read operations are auto-approved while write operations request confirmation"
- MCP tool list on that page (from the table): list-objects, list-attribute-definitions, list-lists, create-list, update-list, list-list-attribute-definitions, add-record-to-list, update-list-entry-by-id, create/update/upsert-record, merge-records, notes, tasks, comments, activities records, run-basic-report, query-particle-sql. No view, workflow, create-attribute or create-object tool appears. create-list is documented in the changelog. — https://docs.attio.com/changelog/mcp.md, opened 2026-10-16, curl — Quote: "`create-list` allows you to create a new list to group and track records of a single object type."
- Workflows can be triggered by an HTTP request once built in the UI. — https://attio.com/help/reference/automations/workflows/workflows-block-library, opened 2026-10-16, curl — Quote: "Webhook received starts a workflow when an external application sends a request to a provided URL."
- App SDK can add blocks to Workflows, not create workflows. — https://docs.attio.com/sdk/overview.md, opened 2026-10-16, curl — Quote: "Add custom triggers and steps to the Attio Workflows builder: subscribe to external events or call external APIs as part of a workflow run."
- App SDK setup needs a developer account in the Developer console (a browser step). — https://docs.attio.com/sdk/guides/creating-an-app.md, opened 2026-10-16, curl — Quote: "Head over to our [Developer console](https://build.attio.com) and sign in with your Attio account."

### Contradictions
- None found. (Earlier note said views return "id, title and created_at"; consistent with GET-only. The open question about webhook:read is answered: the list webhooks route needs `webhook:read`.)

### Inferences
- Inferred from the 53-path listing: the Attio view contents (filters, sorts, grouping, Kanban column setting) cannot be read or written by REST at all, only view id/title. So view configuration is a browser task, and any verification of it is also a browser task (or an export).
- Inferred: the engineer can build the whole data model (objects, attributes, select options, relationships, lists, list attributes) by REST with a scoped API key, so the browser job in Attio shrinks to views and workflow construction.
- Inferred: Workflow runs can be started from outside by a human-built "Webhook received" workflow, which gives an API path to execute but not to author automations.

### Gaps
- "App SDK is blocked at John's org": no public source; cannot be settled without his org. The docs only show a Developer console sign-in; whether an org admin must approve app installs was not read.
- Live MCP tools/list was not called (no account access); the list is from the docs page.
- Attio's agent-facing "Ask Attio"/AI automation features were not checked.

## Clay: API, MCP, webhooks, CLI

### Takeaway
Clay has an official CLI/plugin (works with Claude Code), a Public API with API keys, and an MCP connector. They can search, run functions, read signals and audiences, and build, edit and run Workflows (Alpha). They cannot create tables or columns or list tables; classic table building, custom functions, and custom signals are UI-only. Confidence: high (official docs plus plugin repo).

### Cited findings
- Workflows (Alpha) are buildable by agent via plugin/CLI. — https://developers.clay.com/routines/workflows-alpha.md, opened 2026-10-16, curl — Quote: "With the Clay plugin, agents can read and edit Workflows, validate the graph, run test actions, start runs, inspect failed steps, pause or resume runs, and restore snapshots."
- Custom functions are built in the UI, run by API/CLI/MCP. — https://developers.clay.com/routines/custom-functions.md, opened 2026-10-16, curl — Quote: "Build and manage the function in the Clay UI."
- Exposing a function to API or MCP is a toggle in the UI. — https://developers.clay.com/routines/custom-functions.md, opened 2026-10-16, curl — Quote: "Enable the integrations you need, such as **API** or **MCP**."
- Tables: Enterprise only, read only, no list endpoint. — https://developers.clay.com/tables.md, opened 2026-10-16, curl — Quote: "The current public API does not include a list-tables endpoint."
- Tables cannot be created programmatically. — https://github.com/clay-run/agent-plugins clay/skills/clay/SKILL.md:96 (commit b9952b6), read 2026-10-16, git clone + grep — Quote: "Query **existing** Clay tables only — you **cannot** create tables programmatically"
- Plugin also covers campaigns (email sequences), audiences, searches. — same file, line 91 — Quote: "Create, improve, compare, and analyze outbound email sequences"
- API key creation can be done by CLI, but CLI sign-in needs a browser once. — https://developers.clay.com/quickstart.md, opened 2026-10-16, curl — Quote: "Sign-in opens a browser to authorize the CLI."
- Keys by CLI. — https://developers.clay.com/quickstart.md — Quote: "Run `clay api-keys create --name \"<key name>\"` with the `clay` CLI."
- Clay webhooks here are run-finished notifications (outbound), created by CLI. — https://developers.clay.com/public-api/webhooks.md, opened 2026-10-16, curl — Quote: "Webhooks let Clay notify your service when a routine run finishes, so you can react without polling."
- Signals: most created by CLI, custom and web-intent UI only. — https://developers.clay.com/signals.md, opened 2026-10-16, curl — Quote: "Custom and Web intent signal triggers are configured in the Clay web app."
- Rate limit is per workspace; no number is given. — https://developers.clay.com/public-api/rate-limits.md, opened 2026-10-16, curl — Quote: "The Clay Public API enforces a per-workspace request rate limit."
- The plugin requires a shell host (Claude Code works). — https://developers.clay.com/quickstart.md — Quote: "It requires a coding-agent host with a shell — Claude Code, Codex, or Cursor"

### Contradictions
- None found.

### Inferences
- Inferred: the existing Clay tables John built (sources, enrichment columns) can be read only on Enterprise and only by known table id; to move logic to code the engineer should rebuild it as a Workflow (Alpha) or have John build custom functions in the UI. Whether the Alpha stays stable is unknown.
- Inferred: creating classic table columns and sources stays a browser (or human) task.

### Gaps
- Whether John's plan is Enterprise (tables) - unknown.
- The Clay MCP connector's tool list at the developers site was not opened; only the in-session connector description (find and enrich people/companies, run functions) was seen.
- Table-webhook sources (inbound webhooks into a classic table) were not researched.
- Clay Workflows (Alpha) rate and credit limits not read.

## n8n: API-reachable versus UI-only

### Takeaway
n8n's 2026 public API reaches much more than before: workflows, credentials (create; secrets never read back), tags, variables, projects, folders, executions, users, community packages, SSO/LDAP settings, source control. Owner setup and SSO can also be set by environment variables when self-hosted. Remaining UI steps are OAuth consent clicks, owner setup on Cloud, and the API key itself. Confidence: medium (handlers read from the master branch clone; release availability and Cloud behaviour unverified).

### Cited findings
- API availability. — https://docs.n8n.io/connect/n8n-api.md, opened 2026-10-16, curl — Quote: "It isn't available on the free trial."
- Self-hosted all editions, Cloud Starter and above. — same page — Quote: "**Self-hosted:** All editions"
- Community package install is an API route with its own scope. — https://github.com/n8n-io/n8n packages/cli/src/public-api/v1/handlers/community-packages/spec/paths/installPackage.generated.yml:5 (commit 21221ad), read 2026-10-16, sparse git clone — Quote: "description: Install a community package by npm name and optional version."
- Credential create route. — .../handlers/credentials/spec/paths/createCredential.generated.yml:5 (commit 21221ad) — Quote: "description: Creates a credential that can be used by nodes of the specified type."
- Handler directories exist for variables, tags, projects, workflows, users, source-control, settings (SAML, OIDC, LDAP). — https://github.com/n8n-io/n8n packages/cli/src/public-api/v1/handlers/ (commit 21221ad), read 2026-10-16 — Quote: "createVariable.generated.yml" and "updateSamlConfiguration.generated.yml" (file names from the directory listing).
- Owner setup via env on self-hosted. — https://docs.n8n.io/deploy/host-n8n/configure-n8n/manage-settings-using-environment-variables.md, opened 2026-10-16, curl — Quote: "Instance owner management through environment variables is available from n8n 2.17.0."
- Same page lists SSO and community packages as env-managed. — Quote: "Community packages: `N8N_COMMUNITY_PACKAGES_MANAGED_BY_ENV`"
- UI install of verified community nodes needs owner/admin. — https://docs.n8n.io/integrations/community-nodes/installation-and-management/install-verified-community-nodes.md, opened 2026-10-16, curl — Quote: "The n8n instance owner and admin accounts can install and manage verified community nodes."
- OAuth credentials need a human consent click. — https://docs.n8n.io/integrations/builtin/credentials/google/oauth-single-service.md, opened 2026-10-16, curl — Quote: "In n8n, select **Sign in with Google** to complete your Google authentication."
- The n8n MCP server (connected in this session) and CLI wrap the API. — https://docs.n8n.io/connect/n8n-api.md — Quote: "It wraps the public API and is a good fit for:"

### Contradictions
- None found.

### Inferences
- Inferred: on self-hosted n8n, almost everything including owner and SSO is scriptable, so the browser is needed only for OAuth consent clicks and for creating the first API key.
- Inferred: on Cloud, owner setup is UI-only (no env route) and whether the community-package route works on Cloud is unproven.

### Gaps
- Whether the master-branch routes (community packages, settings) exist in the released version John runs.
- Cloud behaviour of the community-package API route; API-key creation in UI (assumed UI; the page opened does not say).
- n8n API key scopes list and variables availability on non-Enterprise plans.

## Outreach: sequences, templates, mailboxes

### Takeaway
The Outreach REST API has create and update routes for sequences, templates, sequence templates and mailboxes, and an official MCP server (32 tools) includes sequence_create and sequence_add_prospects but no template or mailbox tool. Both act as the authorising user, so company-admin RBAC limits apply. Creating the OAuth app and authorising are human steps. Confidence: medium.

### Cited findings
- Mailbox create and update exist. — https://developers.outreach.io/api/reference/mailbox.md, opened 2026-10-16, curl — Quote: "## Update a Mailbox"
- Mailbox attribute shows per-user edit permission. — https://developers.outreach.io/api/reference/mailbox/paths/~1mailboxes~1%7Bid%7D/patch.md — Quote: "A boolean value to indicate if the user has the permission to edit mailbox fields."
- Sequence and template create routes (search excerpt pages opened as .md): sequence.md lists POST /sequences; template.md lists POST /templates. — https://developers.outreach.io/api/reference/sequence.md, opened 2026-10-16, curl — Quote: "## Create a New Sequence"
- OAuth acts as the user; app creation and scopes are set in the portal. — https://developers.outreach.io/api/oauth, opened 2026-10-16, curl — Quote: "To begin using the REST API you need to create an Outreach app."
- Dev credentials are immediate; production needs publish and review. — same page — Quote: "Development credentials are provisioned immediately"
- MCP: 32 tools, OAuth with dynamic client registration, RBAC inherited. — https://developers.outreach.io/mcp-server/authentication, opened 2026-10-16, curl — Quote: "Permissions inherit from the user."
- MCP write tools include sequence creation. — https://developers.outreach.io/mcp-server/tool-catalog, opened 2026-10-16, curl — Quote: "sequence_create destructiveHint: false Create a new sequence"

### Contradictions
- None found.

### Inferences
- Inferred: admin-only settings (mailbox limits, org-wide templates) will fail or be hidden for a non-admin token; the mailbox `editable` flag is the signal. Not tested.

### Gaps
- Sequence step routes, OAuth scope names per resource, and rate limits were not read (sequence-step.md returned no route lines).
- Whether John's company admin must approve an Outreach app, and John's role, are unknown.

## Health: WHOOP, Withings, patient portals

### Takeaway
WHOOP and Withings both need a one-time human developer-app registration in a browser and a one-time human OAuth consent per account; after that, token refresh and data pulls are fully API-driven. Note Withings changed its free plan on 12 Oct 2026 (membership requirement for newer accounts). Patient portals, FHIR aggregators and Function Health were not researched. Confidence: high for WHOOP/Withings, none for portals.

### Cited findings
- WHOOP app creation is a dashboard step with WHOOP login. — https://developer.whoop.com/docs/developing/getting-started, opened 2026-10-16, curl — Quote: "To create your first App, head to the App creation flow in the Developer Dashboard."
- WHOOP app limit. — same page — Quote: "You can create up to 5 Apps."
- WHOOP refresh needs the offline scope. — https://developer.whoop.com/docs/developing/oauth, opened 2026-10-16, curl — Quote: "You must request the offline scope to receive a refresh token."
- WHOOP rate limits. — https://developer.whoop.com/docs/developing/rate-limiting, opened 2026-10-16, curl — Quote: "100 requests per minute."
- WHOOP sandbox tier suffices for one user. — https://developer.whoop.com/docs/developing/app-approval, opened 2026-10-16, curl — Quote: "Every new app starts on the Sandbox tier, which allows up to 10 WHOOP members to connect."
- Withings app registration in Partner Hub. — https://developer.withings.com/developer-guide/v3/get-access/sign-up-for-a-developer-account, opened 2026-10-16, curl — Quote: "Register in the Partner Hub to get your client credentials."
- Withings plan change. — same page — Quote: "Withings accounts created after that date will need a membership to share health data with a free-plan app, including apps that are already live."
- Withings OAuth consent is a human step; code must be exchanged fast. — https://developer.withings.com/developer-guide/v3/integration-guide/public-health-data-api/get-access/oauth-web-flow, opened 2026-10-16, curl — Quote: "You have 30 seconds to exchange the authorization code for an access token and a refresh token."
- Withings data pull after consent includes history. — same page — Quote: "you will have access not only to new data but also to all historical health data collected by the devices"

### Contradictions
- None found.

### Inferences
- Inferred: the engineer can automate everything after John does registration and consent once, if the refresh token is stored as a secret and refreshed on schedule.

### Gaps
- Patient portals for blood work (typically no API), 1upHealth, Health Gorilla, Apple Health records, Function Health exports: not researched, no source opened.
- Withings Start-for-Free plan details/price page returned no readable content (JS page); the exact plan terms are unknown.
- WHOOP webhook details and Withings notification setup not read.

## Per-task table

| Task | API or MCP path | Browser needed | Human step needed | Source |
| --- | --- | --- | --- | --- |
| Attio: create/update objects | REST POST/PATCH /v2/objects, scope object_configuration:read-write | no | create API key once | api.attio.com/openapi/api |
| Attio: attributes incl. select options, statuses, relationships | REST POST attributes/options on objects and lists | no | none | same |
| Attio: lists, list attributes | REST POST/PATCH /v2/lists; MCP create-list, update-list | no | none | same; docs.attio.com/changelog/mcp.md |
| Attio: views (table, Kanban), filters, sorts, grouping | read-only REST (GET views, id/title); no write | yes | maybe | same |
| Attio: Workflows build/edit | none; run via Webhook-received trigger | yes | none | attio.com help block library |
| Attio: App SDK app | Developer console + CLI | yes (console) | admin approval unknown | docs.attio.com/sdk |
| Clay: search, run functions, Workflows (Alpha) | clay CLI/plugin, Public API, MCP | first sign-in only | authorise CLI once | developers.clay.com |
| Clay: create tables, columns, enrichment columns, sources | none | yes | none | clay-run/agent-plugins SKILL.md:96 |
| Clay: read table rows | POST /tables/query (Enterprise) | no | table ids from URL | developers.clay.com/tables.md |
| Clay: custom function build; custom/web-intent signals | UI only | yes | none | custom-functions.md, signals.md |
| n8n: workflows, credentials, tags, variables, projects, executions | public API / CLI / MCP | no | create API key | docs.n8n.io/connect/n8n-api.md; repo handlers |
| n8n: owner setup | env vars (self-hosted, 2.17.0+) | Cloud: yes | none | manage-settings page |
| n8n: community node install | API route (self-hosted; Cloud unverified) or UI | Cloud: probably | owner/admin | repo; install doc |
| n8n: OAuth credential connect | none | yes | consent click | Google OAuth doc |
| Outreach: sequences, templates, mailboxes | REST POST/PATCH; MCP sequence_create | no | create app, authorise once; admin rights | developers.outreach.io |
| WHOOP: developer app | none | yes | register, consent per account | developer.whoop.com |
| WHOOP: data pull | REST with refresh token | no | none after consent | same |
| Withings: developer app | none | yes | register, consent; membership rule | developer.withings.com |
| Blood-work patient portals | not researched | unknown | unknown | gap |

## Recommendation

One recommendation: use APIs and MCP for everything in the table marked "no" and restrict the browser to Attio views and Workflows, Clay table and column building, OAuth consent clicks, and one-time developer-app registration. Alternatives: for Clay, rebuild logic as Workflows (Alpha) via the CLI to avoid the browser; for Attio views, record them by hand in a runbook. Rejected: unofficial Clay session-cookie API (claycast, unofficial, fragile). Spike before building: (1) call Attio list views on a sandbox to confirm id/title only; (2) confirm the n8n community-package route and owner setup on John's n8n edition; (3) confirm the Outreach app can be created and what its token can edit; (4) test whether the Attio App SDK is truly blocked; (5) research patient portals separately.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Attio REST API + OpenAPI (re-checked) | https://api.attio.com/openapi/api | 53 paths; views GET-only; no workflow routes; attribute, option, list writes | hosted, API key or OAuth | 2026-10-16 | Use for data model; views and workflows need a browser |
| Attio MCP (re-checked) | https://docs.attio.com/mcp/overview.md | OAuth hosted; create-list, records, no attribute/view/workflow tool | hosted | 2026-10-16 | Use for records and lists |
| Clay agent plugin + CLI | https://github.com/clay-run/agent-plugins | Skills and clay CLI: searches, routines, Workflows (Alpha), campaigns, signals; no table creation | Claude Code with shell | 2026-10-16 | Use for Workflows and reads; cloned read only, not run |
| Outreach MCP server | https://developers.outreach.io/mcp-server | 32 tools, OAuth DCR, RBAC inherited, sequence_create | hosted | 2026-10-16 | Use for sequence work; no template or mailbox tools |
| WHOOP developer API | https://developer.whoop.com/docs/developing/getting-started | OAuth2 app, offline scope refresh, 100 req/min | hosted | 2026-10-16 | Use after one-time human registration |
| Withings Public API | https://developer.withings.com/developer-guide/v3/withings-solutions/app-to-app-solution | OAuth2 web flow, webhooks; Withings+ rule from 2026-10-12 | hosted | 2026-10-16 | Use; check plan terms first |
| n8n public API (master handlers) | https://github.com/n8n-io/n8n | Community packages, credentials, tags, variables, projects, SSO settings routes | self-hosted or cloud | 2026-10-16 (commit 21221ad) | Use; confirm release availability |
