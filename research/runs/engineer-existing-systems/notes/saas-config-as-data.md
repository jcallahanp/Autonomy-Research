# Reading SaaS configuration as data (Attio, Clay, n8n, Outreach, Slack)

Brief: For each SaaS tool in John's GTM stack, what configuration can an agent read through an API, MCP server or CLI (objects, attributes, lists, views, workflows, sequences, credentials in use, run histories), and what is only visible in the UI?
Run: research/runs/engineer-existing-systems/PLAN.md

Recommendation (one for the facet): build a read-only "config snapshot" step in the engineer that, per tool, uses the cheapest official read path and writes JSON to the repo: Attio REST (objects, attributes, lists, list views as id/title only, webhooks) via an API key; Clay CLI/plugin for Workflows plus the Enterprise-only tables query; n8n `export:workflow` plus public API for credential metadata and executions; Outreach REST for sequences, steps, templates, mailboxes via OAuth; Slack `apps.manifest.export` with a config token; Claude Code `claude mcp list/get` and files on disk. Alternatives: UI screenshots through a browser tool (last resort, no Playwright run here); unofficial Clay internal API (rejected: session cookie, undocumented). Rejected: third-party Attio/Clay MCP wrappers as a primary path (unofficial; not opened as sources for behaviour). Spike before building: (1) which Clay plan John is on and whether `clay workflows` can dump a Workflow definition; (2) whether John's Outreach profile can create an API app; (3) n8n self-hosted vs cloud and whether the CLI is reachable; (4) which Attio features exist only in the UI (automation/Workflows, views' filters and columns).

## Attio: what REST and MCP expose for reading, and what is UI-only

### Takeaway
REST reads objects, attributes (with select options and statuses), lists, entries, webhooks, a token-identify call and read-only SQL. Views are listable only as id, title and created_at. There is no workflow/automation read endpoint and no API-key list. The official MCP reads objects, attributes, lists and entries but has no view or workflow tool. Tables and views cannot be created through REST or MCP: confirmed by absence in the OpenAPI paths and MCP tool table (confidence: high for absence in the sources read; the vendor never states it in words).

### Cited findings
- REST lists saved views per object, scope object_configuration:read — https://docs.attio.com/rest-api/endpoint-reference/objects/list-views-for-object, opened 2026-10-16, Parallel web_fetch — Quote: "Lists saved views for an object. Results are ordered by view ID (`id.view_id` ascending)."
- Views are described as table or board layouts (so Kanban boards are a view type), yet the object-view schema has only id, title and created_at (I parsed https://api.attio.com/openapi/api with python: `['id', 'title', 'created_at']`; WebFetch of the page said the same) — https://api.attio.com/openapi/api, opened 2026-10-16, curl — Quote: "Object views are saved table or board layouts for an object."
- A list-views endpoint also exists for lists — https://docs.attio.com/llms.txt, opened 2026-10-16, curl — Quote: "Lists saved views for a list. Results are ordered by view ID (`id.view_id` ascending)."
- OpenAPI paths for views contain only GET (no POST under any `view` path); attributes support list/create/get/update, select options and statuses — https://api.attio.com/openapi/api, opened 2026-10-16, curl+python — Quote: "GET /v2/lists/{list}/views - List views for list" (my parsed path listing; no POST view path appeared).
- Attribute listing covers objects and lists — https://docs.attio.com/rest-api/endpoint-reference/attributes/list-attributes, seen in Parallel search result, opened via search excerpt only (see Gaps) — not used as a cited source.
- Webhooks can be listed — https://docs.attio.com/rest-api/endpoint-reference/webhooks/list-webhooks, search excerpt only; corroborated by the opened OpenAPI path `GET /v2/webhooks - List webhooks` — https://api.attio.com/openapi/api, opened 2026-10-16, curl — Quote: "GET /v2/webhooks - List webhooks"
- Token introspection exists — https://docs.attio.com/llms.txt, opened 2026-10-16, curl — Quote: "Identify the current access token, the workspace it is linked to, and any permissions it has."
- No workflow read endpoint: the only "workflow" pages in the docs index are App SDK blocks — https://docs.attio.com/llms.txt, opened 2026-10-16, curl — Quote: "Build custom triggers and steps that show up inside Attio Workflows"
- Read-only SQL over all objects and lists — https://docs.attio.com/sql/overview.md via llms.txt, opened 2026-10-16, curl — Quote: "Query your workspace data with read-only SQL"
- MCP read tools for schema — https://docs.attio.com/mcp/overview, opened 2026-10-16, Parallel web_fetch — Quote: "`list-attribute-definitions` | List all attributes available on an object type, including their types and valid options"
- MCP list tools — same page — Quote: "`list-lists` | List all lists in the workspace, with optional filtering by name or slug"
- MCP list-entry reading — same page — Quote: "`list-list-attribute-definitions` | List the available entry attributes for a given list, including their types and options"
- MCP can create a list and update list name/slug/permissions but the tool table has no view tool — same page — Quote: "`create-list` | Create a new list to group and track records of a single object type"
- MCP approvals and identity: reads auto-approved, acts as the OAuth user — same page — Quote: "Read operations** : Auto-approved for seamless searching and viewing"
- MCP SQL tool is plan-gated — same page — Quote: "`query-particle-sql` is not available on every billing plan."
- Scopes available (webhook:read, object_configuration:read, list_configuration:read) — https://docs.attio.com/rest-api/endpoint-reference/objects/list-views-for-object, opened 2026-10-16, Parallel web_fetch — Quote: "webhook:read: View, and optionally manage, webhooks."
- Attio docs changelog notes recent REST additions (beta attribute-value history writes, merge) — https://docs.attio.com/changelog/rest-api, search excerpt only; not relied on.

### Contradictions
- None found. Note: docs tag views as "table or board layouts" but the schema returns no layout type; a Kanban view is therefore listable by title but its grouping and filters are not readable (inference below).

### Inferences
- Views' filters, columns, sort and Kanban grouping are UI-only; an agent can only inventory view names. Rests on the object-view schema (id, title, created_at).
- Attio automations (Workflows) have no read API; their definitions are UI-only, or readable only if John exports screenshots. Rests on absence in the OpenAPI path list and llms.txt.
- API keys cannot be enumerated by API; only the calling token can be identified through the meta endpoint. Rests on the absence of a token-list path in the OpenAPI.
- John's report that tables/views cannot be created via API or MCP is consistent with the sources (no POST view path; no view tool in the MCP table). Lists can be created by MCP; creating side belongs to Area 6.
- App SDK is blocked at his organisation, so workflow blocks are out of reach; REST with a personal API key on his own account is the unblocked path.

### Gaps
- Exact fields returned by `GET /v2/objects` and `/v2/lists` were not opened individually (relied on index and OpenAPI path listing).
- Whether Attio "Workflows" run history is available anywhere programmatically: no source found.
- Whether personal API keys (rather than OAuth app tokens) are issued on John's plan: https://docs.attio.com/rest-api/guides/authentication not opened.
- Third-party Attio MCP servers (kesslerio, itsbrex) appeared in search; not opened as primary sources, not evaluated.

## Clay: tables, enrichment columns, workflows

### Takeaway
Clay's official developer platform (2026) offers Searches, Routines (managed functions, custom functions, Workflows in Alpha), Audiences, Signals and an Enterprise-only table query. Workflows can be read, run and inspected via the Clay CLI/plugin; there is no official list-tables, schema-of-columns or table-export endpoint. Enrichment column configuration is effectively UI-only unless the table is turned into a Workflow or the unofficial internal API is used. Confidence: medium (Alpha surface, plan unknown).

### Cited findings
- Official platform primitives — http://developers.clay.com/ (via https://developers.clay.com/index.md), opened 2026-10-16, Parallel search excerpt + curl of sibling .md — Quote: "Tables (Enterprise) | Query existing Clay table data from known tables"
- Table query is Enterprise only and has no list endpoint — https://developers.clay.com/tables.md, opened 2026-10-16, curl — Quote: "The current public API does not include a list-tables endpoint."
- Table query returns records with field metadata — https://developers.clay.com/llms.txt, opened 2026-10-16, curl — Quote: "Runs a structured query against Clay table data and returns records with field metadata."
- Plan gate — https://developers.clay.com/tables.md — Quote: "Tables are available on Enterprise plans."
- Workflows are Alpha and agents can read them — https://developers.clay.com/routines/workflows-alpha.md, opened 2026-10-16, curl — Quote: "With the Clay plugin, agents can read and edit Workflows, validate the graph, run test actions, start runs, inspect failed steps, pause or resume runs, and restore snapshots."
- Workflows are Alpha — same page — Quote: "**Workflows are in Alpha.** They are earlier than Clay-managed functions and custom functions."
- CLI can convert a table into a Workflow and inspect runs — https://developers.clay.com/recipes/build-workflow-alpha.md, opened 2026-10-16, curl — Quote: "Turn this Clay table into a Workflow I can run in batches. Keep the same enrichment steps"
- CLI read commands — same page — Quote: "clay workflows runs steps wf_abc123 wfr_abc123 --status failed"
- CLI lists workflows and snapshots — same page — Quote: "clay workflows snapshots list wf_abc123"
- Workflow run history query API (beta) — https://developers.clay.com/llms.txt — Quote: "Execute a Clay workflow-run query."
- Webhook in: every table has an endpoint; HTTP actions push out — https://www.clay.com/university/guide/using-clay-as-an-api, Parallel search excerpt (page fetch by WebFetch returned 404; treat as search excerpt, not primary) — see Gaps.
- Unofficial: a reverse-engineered internal API can read a table (`get_table`) and export (`POST /v3/tables/{TABLE_ID}/export`) using a browser session cookie — https://github.com/TenSpy-ai/claycast references/clay-api-reference.md:2-4 and :16, read 2026-10-16, curl — Quote: "Reverse-engineered internal API for programmatically building and updating Clay tables."
- Same source, auth — :16 — Quote: "**Auth:** Session cookie from Chrome DevTools → `app.clay.com` → Application → Cookies → `claysession`."
- Same source notes cookie expiry — :21 — Quote: "Cookie expires every few weeks — refresh manually."

### Contradictions
- None found. (Clay University says Enterprise API gives "basic people and company data"; the newer developer docs add table queries. Different dates; the newer one governs.)

### Inferences
- Enrichment column definitions (provider, inputs, conditional run formulas) are not exposed by an official read endpoint; best official route is "turn table into a Workflow" then read the Workflow via CLI. Rests on the tables page (data and field metadata only) and the Workflows recipe.
- The unofficial API can return full table schema, but is session-cookie based, undocumented and may breach terms; treat as a spike-only fallback.
- Because John's Clay account is his own, an API key and the CLI are likely accessible; Enterprise gating of tables may block data reads on his plan.

### Gaps
- Exact `clay workflows` subcommand that dumps a Workflow definition as JSON: the recipe lists `list`, `runs get`, `runs steps`, `snapshots list`; a `get`/export command is not documented there.
- John's Clay plan not known; not verified whether the table query works on non-Enterprise.
- clay.com/university guide URL returned 404 to WebFetch; search excerpt only.
- Clay's official MCP in this session (tools for people/company enrichment and `list_subroutines`) was not tested, only noted from session instructions.

## n8n: REST API and CLI

### Takeaway
n8n's public API covers workflows, executions (with status filter and optional data), credentials (list without secrets, admin/owner only), audit, tags, source control, variables, data tables and projects. The CLI exports workflows as JSON (including historical versions) and credentials (encrypted by default, plain with `--decrypted`). Execution errors are readable through `status=error` plus `includeData`. Confidence: high for API shape, medium for cloud-versus-self-hosted CLI differences.

### Cited findings
- Public API resource groups — https://docs.n8n.io/connect/n8n-api/api-reference, opened 2026-10-16, Exa search highlight — Quote: "Workflow, Execution, Credential, User, Audit, Tags, Source Control, Variables, Data Table, Projects, and more."
- Base URLs for cloud and self-hosted — same page — Quote: "n8n Cloud: `https://.app.n8n.cloud/api/v1`"
- Credential list excludes secrets, admin/owner only — https://github.com/n8n-io/n8n-docs/blob/main/docs/api/v1/openapi.yml, opened 2026-10-16, Exa fetch — Quote: "Retrieve all credentials from your instance. Only available for the instance owner and admin. Credential data (secrets) is not included."
- Credential type schema readable — same file — Quote: "summary: Show credential data schema"
- Executions list with filters — same file (search highlight, opened) — Quote: "Retrieve all executions from your instance."
- Execution status filter values include error and crashed — same file — Quote: "enum: - canceled - crashed - error - new - running - success - unknown - waiting"
- Security audit — same file — Quote: "Generate a security audit for your n8n instance."
- Retry can use saved or latest workflow — same file — Quote: "Whether to load the currently saved workflow to execute instead of the one saved at the time of the execution."
- API playground is self-hosted only — https://docs.n8n.io/connect/n8n-api, Exa highlight — Quote: "Use an API playground: try out the API in a built-in playground (self-hosted n8n only)."
- CLI workflow export flags — https://docs.n8n.io/deploy/host-n8n/configure-n8n/use-the-command-line, Exa highlight, opened 2026-10-16 — Quote: "Exports the published/active version of the workflow instead of the current draft."
- CLI backup shorthand — same page — Quote: "Sets --all --pretty --separate for backups. You can optionally set --output."
- CLI credentials plain text — same page — Quote: "Exports the credentials in a plain text format. (Credentials only.)"
- Warning — same page — Quote: "All sensitive information is visible in the files."

### Contradictions
- A third-party mirror (https://www.mintlify.com/n8n-io/n8n/api/overview, search excerpt) lists `GET /api/v1/credentials/:id` and per-resource scopes such as `credential:read`; the official openapi.yml portion I opened shows list, create, update, delete and schema paths but no GET-by-id. The mirror is unofficial and is not cited. Settle by reading the full official spec.

### Inferences
- A safe inventory: `GET /credentials` (names, types, ids; no secrets) joined against workflow JSON nodes' `credentials` references shows which credentials each workflow uses. Rests on the credential list description and workflow export; the join itself is my design.
- `n8n export:credentials --decrypted` must never be an agent default; the encrypted export still carries a key dependency. Rests on the warning quote.
- The CLI runs against the server's database, so it exists only where John controls the host (self-hosted); on cloud the REST API is the route. This is a prediction: no page I read says the CLI is unavailable on cloud.

### Gaps
- Whether the CLI or `n8n execute` is available on n8n Cloud: no source opened.
- Full workflow endpoint list (only partial official spec read, truncated at 8,000 chars).
- Whether public API access is plan-limited on Cloud trial: not verified.
- The n8n MCP server connected in this session (instance-level) was noted from session instructions only, not opened.

## Outreach: sequences, templates, mailboxes, permissions

### Takeaway
Outreach REST (JSON:API) exposes sequences, sequenceSteps, templates, mailboxes, mailings and more, via OAuth 2.0 with a developer app; a limited server-to-server token covers a subset, including read of sequences and templates. On a company account the blockers are app creation/installation by an org admin and profile-based permissions, not missing endpoints. Confidence: medium; no permissions/profiles endpoint was found.

### Cited findings
- Auth model — https://developers.outreach.io/api/oauth, opened 2026-10-16, Exa highlight — Quote: "Outreach currently enables access to the REST API via API calls authenticated via OAuth 2.0 protocol."
- Calls run as the authorizing user — same page — Quote: "Outreach will execute all the calls on behalf of the user who performed authorization."
- Dev credentials limited to 10 people of the owning org — same page — Quote: "Development credentials are usable with no limitation for up to 10 people from the organization that owns the app."
- Where to create the app (needs Settings -> Integrations) — https://support.outreach.io/support/solutions/articles/159000425919-how-to-access-outreach-apis, Exa highlight — Quote: "Settings -> Integrations -> Installed Apps -> Click on the app you desire to connect to Outreach API -> Set-up -> API access."
- Sequences, sequence steps and templates resources — https://developers.outreach.io/api/common-patterns, opened 2026-10-16, Exa highlight — Quote: "Sequences are at the heart of Outreach's system of engagement."
- Step types — same page — Quote: "Accepted values for the step type attribute include `"auto_email"`, `"call"`, `"manual_email"` and `"task"`."
- Templates carry subject/body and link to sequence templates — same page — Quote: "Templates are larger resources that encapsulate a mailing's subject and body"
- Mailbox resource exists — https://developers.outreach.io/api/reference/mailbox, Exa highlight — Quote: "/mailboxes"
- Sequence steps list endpoint — https://developers.outreach.io/api/reference/sequence-step/paths/~1sequencesteps/get.md — Quote: "Endpoint: GET /sequenceSteps"
- S2S token scopes (read-only subset: auditLogs, templates, snippets, users, mailings) — https://developers.outreach.io/api/s2s-access, opened 2026-10-16, curl + Exa — Quote: "templates - read"
- S2S includes audit logs read — same page — Quote: "auditLogs - read"
- S2S needs org-admin install, write limits — same page (curl, text stripped) — Quote: "In general, read operation on available endpoints works well."
- S2S token is per app install by org admin — same page — Quote: "installs your application to their org"
- Admin profile controls org configuration — https://support.outreach.io/support/solutions/articles/159000426212-what-permissions-do-outreach-admins-have-access-to-, Exa highlight — Quote: "It gives them the ability to control certain aspects of how the Outreach account is configured for the entire organization."
- Legacy SDK doc said provisioning was admin-locked in beta — https://github.com/getoutreach/outreach-platform-sdk/blob/master/documentation/authorization/oauth.md, Exa highlight — Quote: "This is currently locked-down for the duration of the BETA period"; likely outdated, do not rely on it.
- OAuth-only apps need no org install — https://developers.outreach.io/client-extensions/app-homepage, Exa highlight — Quote: "These apps do not require installation and can be accessed by the users provided that they grant your app permission through the OAuth flow."

### Contradictions
- App creation: the legacy SDK page says provisioning is admin-only (beta, old); the current support article describes self-serve credential generation. Settle by checking whether John's profile shows Settings -> Integrations -> Create new app.

### Inferences
- Because calls execute as the authorizing user, an agent run under John's token sees only what his profile permits; sequences owned by others may be hidden. Rests on the "on behalf of the user" quote.
- A company-owned account likely requires an admin to approve a custom app or give John the Integrations permission; whether John has it is unknown.
- Company policy may forbid putting company Outreach tokens in an agent environment: a John decision, not a technical limit.
- Read-only S2S scopes (templates, users, auditLogs) fit an inventory use case, but sequences scope in S2S includes write, so scope minimisation needs care.

### Gaps
- No endpoint found for profiles/permissions or role definitions; permissions may be UI-only.
- Rate limits not read.
- Sequence rulesets endpoint and mailbox attributes (what is returned about connection state) not opened.
- Outreach reference page link extraction returned nothing (client-rendered); resource list taken from search highlights only.

## Slack apps and Claude Code / Claude artifacts

### Takeaway
A Slack app's manifest (scopes, event subscriptions, slash commands, interactivity, even Workflow Builder-style `workflows`) is readable with `apps.manifest.export` using an app configuration token and `app_configurations:read`, per app id. Claude Code configuration is readable on disk and with `claude mcp list/get`, `claude doctor`, `/context`, `/mcp`; published Claude Code artifacts can be read by URL in-session, or in bulk through the Compliance API. Confidence: high for Slack and Claude Code, medium for Compliance API availability to John.

### Cited findings
- Export a manifest — https://docs.slack.dev/reference/methods/apps.manifest.export, opened 2026-10-16, Exa highlight — Quote: "Export an app manifest from an existing app."
- Token and scope — same page — Quote: "app_configurations:read"
- Manifest contains scopes and event subscriptions — same page, sample response — Quote: "event_subscriptions": {        "bot_events": [          "workflow_step_execute"        ]      }
- Config tokens are per user and workspace, not per app — https://docs.slack.dev/app-manifests/configuring-apps-with-app-manifests/, Exa highlight — Quote: "Each config token is unique to a user and a workspace, but not an app."
- Manifest methods — same page — Quote: "`apps.manifest.export` exports the manifest of your existing apps."
- Manifest reference fields include scopes, event_subscriptions, workflows — https://docs.slack.dev/reference/app-manifest, Exa highlight — Quote: "settings.event_subscriptions"
- Scope definition — https://docs.slack.dev/reference/scopes/app_configurations.read.md — Quote: "Read app configuration info via App Manifest APIs."
- Claude Code reads MCP config via CLI — https://code.claude.com/docs/en/mcp-quickstart, Exa highlight — Quote: "Run `claude mcp get claude-code-docs` to see which scope holds a server's definition."
- Config files and scopes — same page — Quote: "`project` | `.mcp.json` in your project root | Everyone who clones the project"
- Read-only diagnostics — https://code.claude.com/docs/en/debug-your-config — Quote: "It prints read-only installation and settings diagnostics without starting a session."
- In-session inspectors — same page — Quote: "`/hooks` | Active hook configurations"
- Settings files — https://code.claude.com/docs/en/settings-reference — Quote: "`Project` is `.claude/settings.json`, `Local` is `.claude/settings.local.json`"
- JSON session list — https://code.claude.com/docs/en/cli-reference — Quote: "`--json` to print active sessions as a JSON array for scripting"
- Claude can read an artifact by URL and saves source locally — https://code.claude.com/docs/en/artifacts, opened 2026-10-16, Exa highlight — Quote: "Claude Code also saves the page's full source to a local file, which Claude can open when it needs the exact content"
- Gallery lists own artifacts — same page — Quote: "The header also links to your gallery at claude.ai/code/artifacts, which lists every artifact you have created."
- Compliance API list and read — same page — Quote: "The Compliance API provides endpoints to list an organization's artifacts, retrieve a specific version's content, and delete an artifact"
- Compliance API shape and key — https://platform.claude.com/docs/en/api/compliance/code/artifacts, Exa highlight — Quote: "GET `/v1/compliance/apps/code/artifacts`"
- Legacy chat artifacts: code is viewable/downloadable in UI — https://support.claude.com/en/articles/17153992-what-are-artifacts-and-how-do-i-use-them — Quote: "Legacy artifacts: Use the controls at the top of the artifact panel to view the code, copy the content, or download it."
- Artifacts reading is summarised, not raw, and flags embedded instructions — artifacts doc — Quote: "the summary reports instructions written into the page instead of relaying them."

### Contradictions
- Two Compliance API path families appear: `/v1/compliance/code/artifacts` (Claude Code doc) versus `/v1/compliance/apps/code/artifacts` (platform reference). Likely a doc inconsistency or version change; settle by calling the list route in a spike with a compliance key.

### Inferences
- No Slack method to enumerate all apps was found; the agent needs app ids from John or the Slack app admin UI, then exports each manifest. Rests on the export method requiring `app_id`.
- Claude Code project "definition" is the set of files: `.claude/`, `.mcp.json`, `CLAUDE.md`, settings; the agent should read the files directly and use `claude mcp get` for resolved scope. Rests on the quotes above.
- The Compliance API is an organisation admin feature and probably unavailable to a personal John account; unverified.

### Gaps
- Slack app listing method, and reading Slack Workflow Builder workflows created in the UI (outside manifests): no source opened.
- Whether `apps.manifest.export` works for apps John did not create: not verified.
- Whether a Compliance API key is obtainable on John's plan: no source opened.
- Claude artifact (non-Code, chat) retrieval for an individual account by API: no source found.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Attio REST API + OpenAPI | https://docs.attio.com/rest-api/overview | Reads objects, attributes, lists, entries, view titles, webhooks, read-only SQL | hosted, API key or OAuth | 2026-10-16 | Use for Attio inventory; views and workflows incomplete |
| Attio MCP (official) | https://docs.attio.com/mcp/overview | OAuth-hosted MCP, 40+ tools, reads auto-approved | hosted remote MCP | 2026-10-16 | Use for interactive reads; no view or workflow tool |
| Clay developer platform + CLI | https://developers.clay.com/ | Searches, Routines, Workflows (Alpha), Enterprise table query | hosted API, CLI/plugin | 2026-10-16 | Use for Workflows reads; tables Enterprise only |
| claycast internal Clay API reference | https://github.com/TenSpy-ai/claycast | Reverse-engineered session-cookie API, table get/export | local Python (not run) | 2026-10-16 | Skip except as a spike; unofficial |
| n8n public API | https://docs.n8n.io/connect/n8n-api | Workflows, executions, credential metadata, audit | self-hosted or cloud | 2026-10-16 | Use |
| n8n CLI export | https://docs.n8n.io/deploy/host-n8n/configure-n8n/use-the-command-line | Workflow/credential export to JSON | self-hosted server | 2026-10-16 | Use workflow export; never `--decrypted` by default |
| Outreach REST API | https://developers.outreach.io/api/reference | Sequences, steps, templates, mailboxes via OAuth or S2S | hosted | 2026-10-16 | Use if app creation is permitted; needs company approval |
| Slack app manifest API | https://docs.slack.dev/reference/methods/apps.manifest.export | Exports scopes, events, features per app | hosted, config token | 2026-10-16 | Use |
| Claude Code CLI inspectors | https://code.claude.com/docs/en/debug-your-config | `claude mcp list/get`, `claude doctor`, /context, /mcp | local | 2026-10-16 | Use |
| Claude Compliance API artifacts | https://platform.claude.com/docs/en/api/compliance/code/artifacts | List and download artifact versions org-wide | hosted, compliance key | 2026-10-16 | Fallback; likely org-admin only |
