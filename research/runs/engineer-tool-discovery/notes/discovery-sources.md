# Where to discover tools at run time, and how reliable each source is

Brief: Rank the sources an autonomous Claude Code engineer queries, in order, when it needs a tool or integration it does not know, mid-build.
Run: research/runs/engineer-tool-discovery/PLAN.md

Environment note: all live calls below ran 2026-10-16 from the Claude Code cloud sandbox behind the agent proxy. Parallel Search returned "Too Many Requests" on every call in this run, so Exa and curl did the searching (Parallel not usable here, consistent with the registry).

## MCP discovery sources

### Takeaway
Order for MCP servers: (1) official MCP Registry API (keyless, namespace-verified, but unmoderated for quality or safety and slow, 14-23 s per call), (2) Anthropic plugin marketplaces and the Claude Connectors Directory (curated for Claude, but "verified" is not a security audit), (3) Docker MCP catalog (signed, built by Docker, needs Docker), (4) Smithery registry API (keyless, flags `verified`), (5) awesome lists / web search. Glama and PulseMCP APIs need a key; mcp.so has no API. Every listing is a lead, not a trust signal: malicious and hijackable servers were found in registries in 2025-2026. Confidence: high on access and policy facts (live-tested), medium on coverage and freshness (sampled only).

### Cited findings
- Official registry is keyless and live: `GET /v0.1/servers?search=stripe` returned results with `status`, `updatedAt`, `repository.url`, `remotes` — curl https://registry.modelcontextprotocol.io/v0.1/servers?search=stripe, run 2026-10-16, curl — Quote: "com.stripe/mcp" (server name returned, with `"url":"https://mcp.stripe.com"` and repo `https://github.com/stripe/agent-toolkit`).
- Registry search is name-substring only, can filter `version=latest`, `updated_since`, `include_deleted` — https://registry.modelcontextprotocol.io/openapi.yaml, opened 2026-10-16, curl — Quote: "Search servers by name (substring match)"; "Filter by version ('latest' for latest version, or an exact version like '1.2.3')"
- Without `version=latest`, one server returns many version rows (kesslerio/attio-mcp-server appeared 8 times in 10 results for `search=attio`), and calls took 14.2 s (attio) and 22.8 s (hubspot); two earlier calls timed out at 20 s — live curl, 2026-10-16 — Quote: "io.github.kesslerio/attio-mcp-server | https://github.com/kesslerio/attio-mcp-server | 1.6.0 | active 2026-05-05" (my script output).
- Registry verifies namespace ownership but not code safety — https://modelcontextprotocol.io/registry/about, opened 2026-10-16, Exa — Quote: "The MCP Registry focuses on namespace authentication and metadata hosting, while relying on the broader ecosystem for security scanning of actual server code."
- Registry moderation is minimal — https://modelcontextprotocol.io/registry/moderation-policy, opened 2026-10-16, Exa — Quote: "consumers should assume minimal-to-no moderation."
- Registry deliberately has no quality ranking or curation — https://github.com/modelcontextprotocol/registry/blob/main/complete.md, opened 2026-10-16, Exa — Quote: "Quality rankings: No built-in server quality assessments or rankings"
- Registry authors expect clients to use subregistries instead — complete.md same URL — Quote: "We highly recommend using a subregistry rather than fetching data from the official registry directly."
- Namespace check is not ownership forever: 155 official-registry entries relied on expired domains and were hijackable (Air Security, dated 2026-08-27) — https://www.air.security/blog-posts/mcpjacking, opened 2026-10-16, Exa — Quote: "We discovered 155 hijackable MCPs in the official worldwide marketplace used by millions of agents. Each relied on an expired domain"
- GitHub MCP Registry: 44 servers at launch, curated/partner-nominated, enterprise allow-list; web UI at github.com/mcp — https://github.blog/ai-and-ml/generative-ai/how-to-find-install-and-manage-mcp-servers-with-the-github-mcp-registry/, opened 2026-10-16, Exa (dated 2025-10-24) — Quote: "Currently, the GitHub MCP Registry has 44 MCP servers"; github.com/mcp returns 403 from this sandbox (session bound to repos), so not programmatically usable here.
- Claude Code official marketplace is auto-added; most entries come from partners — https://code.claude.com/docs/en/plugins/anthropic-marketplaces, opened 2026-10-16, Exa — Quote: "Most of what it lists comes from partners and other authors rather than from Anthropic"
- Community marketplace has automated screening, third-party marketplaces have none — https://code.claude.com/docs/en/discover-plugins and the anthropic-marketplaces page — Quotes: "have passed Anthropic's automated validation and safety screening" ; "Anthropic doesn't review third-party marketplaces"
- Catalog is a git file, so it is greppable: `.claude-plugin/marketplace.json` in anthropics/claude-plugins-official — anthropic-marketplaces page — Quote: "That file is the catalog itself."
- Claude Connectors Directory serves Claude Code too; verification is not a security audit; default listing is Community after automated scan — https://claude.com/docs/connectors/directory and https://claude.com/docs/connectors/building/submission, opened 2026-10-16, Exa — Quotes: "Verification isn't a security audit." ; "lists it as a Community connector with no action from you."
- Docker MCP Catalog: curated, Docker-built and signed local servers, SBOM, browsable at hub.docker.com/mcp or `docker mcp catalog server ls` — https://docs.docker.com/ai/mcp-catalog-and-toolkit/toolkit, opened 2026-10-16, Exa — Quote: "All MCP server images under `mcp/` in the MCP Catalog are built by Docker and digitally signed to verify their source and integrity."
- Docker Dynamic MCP lets an agent search the catalog and add servers mid-conversation — same toolkit page — Quote: "enables AI agents to discover, add, and compose MCP servers on-demand during conversations"
- Smithery registry API is keyless for search and returns a `verified` flag and `useCount`: `registry.smithery.ai/servers?q=attio` returned `attio` verified true, useCount 277, plus unverified zero-use entries created 2026-08 to 2026-10 — live curl, 2026-10-16 — Quote: "verified":true,"useCount":48 (response for q=stripe).
- PulseMCP API needs a key — curl https://api.pulsemcp.com/v0.1/servers, 2026-10-16 — Quote: "Invalid or missing API key"
- Glama API needs a key and attribution licence — curl https://glama.ai/api/mcp/v1/servers, 2026-10-16 — Quote: "This endpoint requires an API key."
- mcp.so: `/api/servers?q=` returned the HTML app shell, no JSON API found — curl https://mcp.so/api/servers?q=stripe, 2026-10-16 — Quote: "<!DOCTYPE html>" (first bytes of response).
- Registry-scale quality problems: a DSN 2026 study of 67,057 servers (mid-2025 data) found dead links and re-registrable GitHub accounts — https://arxiv.org/html/2510.16558v2, opened 2026-10-16, Exa — Quote: "we find 212 cases (15.37%) where the associated GitHub accounts are re-registrable, creating opportunities for attackers to hijack the corresponding servers."
- Abandonment/churn: July 2026 measurement — https://arxiv.org/html/2608.00150, opened 2026-10-16, Exa — Quote: "41.6% of confirmed servers disappear within three days between consecutive measurement runs"
- Malicious server in registries, 2025: postmark-mcp backdoor from v1.0.16 — https://postmarkapp.com/blog/information-regarding-malicious-postmark-mcp-package, opened 2026-10-16, Exa (published 2025-09-25) — Quote: "added a backdoor in version 1.0.16 that secretly BCC'd emails to an external server."
- Malicious server in registries, 2026: SmartLoader trojanized Oura MCP submitted to MCP Market (2026-02-05) — https://www.straiker.ai/blog/smartloader-clones-oura-ring-mcp-to-deploy-supply-chain-attack, opened 2026-10-16, Exa — Quote: "Traditional trust signals (GitHub stars, forks, contributor counts) can now be systematically fabricated"
- Sandworm_Mode (2026-02-24): 19 typosquatted npm packages injected a rogue MCP server into Claude Code config — https://www.helpnetsecurity.com/2026/02/24/npm-worm-sandworm-mode-supply-cain-attack/, opened 2026-10-16, Exa — Quote: "injecting a rogue Model Context Protocol (MCP) server into their configuration."
- Vulnerability rate: about 4% of 19,000 MCP repos estimated exploitable (2026-05-27) — https://www.trendaisecurity.com/en/resources-insights/deep-research/hunt-them-all-an-ai-powered-vulnerability-sweep-of-19-000-mcp-servers, opened 2026-10-16, Exa — Quote: "we estimate that the number of exploitable vulnerabilities across the 19,000 repositories lies between 600 and 1,650"
- awesome-mcp-servers (punkpeye) exists as a large list, homepage glama.ai/mcp/servers — http://github.com/punkpeye/awesome-mcp-servers, opened 2026-10-16, Exa — Quote: "A collection of MCP servers."

### Contradictions
- Official registry docs say namespaces tie servers to verified owners ("Namespace authentication ... providing trust and accountability", modelcontextprotocol.io/registry/about); Air Security (2026-08-27) says 155 listed entries were hijackable via expired domains. Both can be true: ownership is checked at publish time only. A re-check of the domain at install time would settle it.
- GitHub blog says the registry has 44 servers (2025-10-24); the page github.com/mcp could not be opened to get the current count. Treat the 44 as launch size only.

### Inferences
- The official registry is the best first MCP lead because it is keyless, structured and carries verifiable `repository.url` and namespace, but it is a name index, not a search engine: query it with the vendor's name AND prefer entries whose reverse-DNS namespace matches the vendor's own domain (e.g. `com.stripe/mcp`). Rests on the registry about page, openapi.yaml, and the attio/hubspot samples where community forks outnumber the vendor entry.
- Smithery, Glama, PulseMCP and mcp.so add no vetting beyond what the official registry gives (the registry docs say subregistries "may" add scans; I saw no scan data in the Smithery response), so for an autonomous run they are second-tier leads. Rests on the live Smithery response fields and the 401s.
- Because of the SmartLoader and MCPJacking reports, star counts and "listed in a registry" cannot be a pass criterion. Vetting is another facet; this facet only ranks where to look.
- The Claude directory and plugin marketplaces are the only sources where Anthropic applies any screening, so rank them above unreviewed aggregators for a Claude Code engineer, though below the vendor's own documentation.

### Gaps
- Claude Connectors Directory: no programmatic listing API found; browsing is via claude.ai or claude.com/plugins. Not tested whether claude.com/plugins is fetchable by script.
- Smithery registry API terms, rate limits and whether it needs a key at volume: not found.
- Current server counts per registry (official, Smithery, Glama, PulseMCP): not measured.
- GitHub MCP Registry (github.com/mcp) returned 403 in this sandbox; programmatic access not established.
- PulseMCP and Glama key signup cost and terms: not opened.

## General package and repo discovery

### Takeaway
Use npm registry search (keyless) and PyPI JSON API by exact name, deps.dev for health, advisories and Scorecard of a known package, and web search for "which library does X" (PyPI has no search API, npm text search is noisy). GitHub search is rate-limited (10/min unauthenticated, 30 authenticated, code search 9-10 and needs auth) and returned 403 in this cloud sandbox, so do not plan around it there. libraries.io needs a key. Context7 for API syntax only. Confidence: high on access, medium on relevance quality.

### Cited findings
- GitHub search limits — https://docs.github.com/en/rest/search/search?apiVersion=2022-1128, opened 2026-10-16, Exa — Quote: "The Search code endpoint requires you to authenticate and limits you to 9 requests per minute. For unauthenticated requests, the rate limit allows you to make up to 10 requests per minute."
- GitHub search from this sandbox is blocked — curl https://api.github.com/search/repositories?q=..., 2026-10-16 — Quote: "sessions are bound to their configured repositories. Use repository-scoped endpoints"
- npm search API is keyless and returns monthly/weekly downloads and dates, but is keyword-noisy: `text=mcp stripe` ranked "adscapi" (an ad-conversion SDK) first; `text=attio mcp` returned attio-mcp 1.7.0 (2026-08-25, 652 weekly) alongside attio-mcp-server 0.0.2 (2025-02-02) — curl https://registry.npmjs.org/-/v1/search, 2026-10-16 — Quote: `"downloads":{"monthly":3583,"weekly":222}` (first result for the stripe query).
- PyPI has no search API: XML-RPC search is disabled — https://warehouse.pypa.io/api-reference/xml-rpc/, opened 2026-10-16, Exa — Quote: "Permanently disabled due to excessive traffic driven by unidentified traffic, presumably automated."
- PyPI JSON and Simple index work by exact name, keyless (`/pypi/requests/json` returned metadata) — https://docs.pypi.org/api/, opened 2026-10-16, Exa; curl 2026-10-16 — Quote: "Query PyPI's Index API or JSON API to determine where to download files from."
- libraries.io search needs a key — curl https://libraries.io/api/search?q=stripe, 2026-10-16 — Quote: "An API key is required."
- deps.dev API v3 is keyless, by exact package, returns licences, advisories, Scorecard and a deprecation flag; it has no free-text package search (only GetPackage/GetVersion/Query by name or hash) — https://docs.deps.dev/api/v3/, opened 2026-10-16, Exa; curl api.deps.dev express returned `isDeprecated` per version — Quote: "GetVersion returns information about a specific package version, including its licenses and any security advisories known to affect it."
- deps.dev data sources include npm, PyPI, Maven, Go, Cargo, OSV and OpenSSF Scorecard — same docs page — Quote: "OpenSSF Scorecard"
- Docker Hub search works keyless (`/v2/search/repositories?query=` returned 980 hits for `mcp/stripe`, mostly unrelated) — curl, 2026-10-16 — Quote: `"count":980` .
- Awesome lists exist (punkpeye/awesome-mcp-servers) but are community PR lists — http://github.com/punkpeye/awesome-mcp-servers, opened 2026-10-16, Exa — Quote: "A collection of MCP servers."
- Typosquatting is active on npm: 19 packages posing as developer and AI-coding utilities (Feb 2026) — https://www.securityweek.com/new-sandworm_mode-supply-chain-attack-hits-npm/, opened 2026-10-16, Exa — Quote: "Dubbed Sandworm_Mode, the attack was deployed through 19 packages published under two aliases, which relied on typosquatting"

### Contradictions
- GitHub docs give the code-search limit as 9 per minute in one passage and 10 per minute in another on the same page (docs.github.com/en/rest/search/search). Minor; plan for 9.
- `api.github.com/rate_limit` from the sandbox showed `core` 15000 and `search` 30, i.e. an authenticated-style quota, while search endpoints returned 403. The quota number does not mean search is allowed; the 403 message is the operative fact.

### Inferences
- For a named library, resolve the exact package name through the vendor's docs or web search first, then confirm with npm search / PyPI JSON / deps.dev; do not let npm text search choose the package (rank noise, typosquats). Rests on the adscapi result, Sandworm_Mode and deps.dev capabilities.
- deps.dev is the best keyless health check (deprecated flag, advisories, Scorecard, licence) once the name is known; it cannot discover.
- On John's own machine, `gh search repos` and code search work with a token and are good for topic discovery (limit 30/min); in the cloud sandbox use Exa/Parallel and Sourcegraph (already in registry) instead.

### Gaps
- Sourcegraph stream API and Context7/DeepWiki coverage were not re-tested in this run; I rely on the registry rows and tool-routing.md.
- npm search API documented limits/ranking weights: not opened.
- Staleness of awesome lists: no measurement.
- GitHub topic search relevance (e.g. topic:mcp-server): not testable here (403).

## Web search versus structured sources

### Takeaway
Web search (Parallel first, Exa second, per tool-routing.md) is better when the need is described in words ("a CLI to export X", "which library handles Y", "official MCP for vendor Z") or when the structured index lacks coverage; structured sources (official registry, npm, PyPI JSON, deps.dev) are better when the name is known or when machine-checkable fields (namespace, repository URL, version, status, advisories) are needed. Practical rule: search to find the name and the vendor's own page, structured API to confirm and extract fields. Parallel was rate-limited throughout this run, so the fallback to Exa is a real operating condition. Confidence: medium-high.

### Cited findings
- Local routing recommendation: Parallel first, Exa second opinion, official registry for MCP — /home/user/Autonomy-Research/research/findings/tool-routing.md:1-13 and :199-215 (read 2026-10-16) — Quote: "Parallel Search is the default for discovery and page reading"
- Same file, MCP row of the decision table — tool-routing.md (Implications, decision table, read 2026-10-16) — Quote: "curl registry `/v0.1/servers?search=` | Parallel web_search with `site:github.com mcp` phrasing"
- Same file, hand-off contract — tool-routing.md — Quote: "Every discovery result must be reduced to <= 3 URLs before any fetch"
- Exa returned the primary docs pages (modelcontextprotocol.io registry about, moderation policy, GitHub rate-limit docs, deps.dev docs) in single calls this run, so it handled "find the official doc page" reliably — this run's Exa searches, 2026-10-16 — Quote: "TL;DR: The MCP Registry is quite permissive!" (moderation-policy page excerpt).
- Parallel Search failed with rate limit three times in a batch — this run, 2026-10-16 — Quote: "Error POSTing to endpoint: Too Many Requests"

### Contradictions
- None found.

### Inferences
- Web search can surface the vendor's official MCP/API page even when the registry only lists community forks (attio, hubspot samples show forks crowd the registry's substring results). Rests on the registry samples and tool-routing.md.
- Security reports say marketplace and stars signals can be faked (SmartLoader), so search result popularity is equally weak; both search and registries produce leads, and the vendor's own domain is the anchor.

### Gaps
- No head-to-head test of Parallel vs Exa vs registry on the same SaaS-integration query in this run (Parallel unavailable). tool-routing.md has the one prior test on a memory-tool query only.

## Ordered source list per need type

### Takeaway
Four ordered lists below (my recommendation, built from the findings above). Common rule: the vendor's own documentation page is step 1 for any named SaaS; registries are leads, each lead must pass the vetting facet before use. Confidence: medium (ordering is reasoned, partly untested on a real task).

### Cited findings
- See the three sections above; this section adds no new sources.

### Contradictions
- None found.

### Inferences
Recommendation (one): the engineer runs a short "discovery ladder" per need type, stops at the first step that returns a candidate with a verifiable vendor or maintainer, and hands at most 3 candidates to the vetting step.

1. Integration with a named SaaS (e.g. Attio, Clay, n8n, Supabase):
   1. Web search (Parallel, else Exa) for the vendor's own "API" and "MCP" docs pages. Anchor on the vendor domain.
   2. Official MCP Registry `?search=<vendor>&version=latest`, accept only namespaces matching the vendor domain (`com.vendor/*`, or `io.github.<vendor-org>/*`); check the domain is still owned.
   3. Claude plugins: grep `marketplace.json` of claude-plugins-official, or the `/plugin` Discover tab; Connectors Directory (Verified over Community).
   4. Vendor REST API plus OpenAPI spec and an official SDK (npm/PyPI via deps.dev) as the fallback; often better than an MCP wrapper.
   5. Smithery `verified:true`, then community MCPs from the registry. Last.
2. Library for a task:
   1. Web search by task description (Exa for semantic phrasing) to get 3 candidate names.
   2. npm search / PyPI JSON by exact name; deps.dev for deprecation, advisories, Scorecard, licence, last release.
   3. Context7 for API syntax of the chosen one; DeepWiki or clone for internals.
   4. Awesome lists only for orientation. GitHub search only on John's machine with a token.
3. MCP server (capability, not vendor-specific):
   1. Official registry search (several keywords, `version=latest`), 2. Claude plugin marketplaces and Connectors Directory, 3. Docker MCP catalog if Docker exists (signed, Docker-built `mcp/` images), 4. Smithery API, 5. awesome list or web search with `site:github.com mcp`. Skip Glama, PulseMCP (key) and mcp.so (no API) unless John supplies keys.
   Before 4-5 ask whether a plain CLI or API call would do; fewer MCP servers means less prompt-injection surface (Sandworm_Mode, MCPJacking).
4. CLI tool:
   1. Web search naming the task plus "CLI", 2. the distro or Homebrew/winget package page and the project's GitHub releases, 3. npm/PyPI name checks and deps.dev for pip/npm-distributed CLIs, 4. Docker Hub search for an image, 5. Sourcegraph stream API to see how real projects call it.

Alternatives: replace step order 2-3 for MCP lists if Docker is the host runtime (Docker catalog first). Rejected as primary sources: mcp.so (no API; highest dead-link rate, 6.75% invalid links in the 2025 study), Glama and PulseMCP (key required), GitHub topic search in cloud (403), PyPI search (disabled), libraries.io (key), star counts as a signal (fabricable).

What must be spiked before building:
- Run the official registry call from the engineer's real runtime 10 times and record latency and timeouts (14-23 s and two 20 s timeouts seen here); decide a 60 s timeout and caching.
- Test whether the registry result for a real vendor (Attio, Clay, n8n, Supabase) has a vendor-namespace entry at all.
- Check that `claude.com/plugins` and `marketplace.json` are scriptable from the cloud runtime.
- Confirm Smithery's keyless search is stable at volume and what `verified` means (Smithery docs not opened).
- Test GitHub search from John's machine with a token if the engineer runs locally.

### Gaps
- No end-to-end test of the ladder on a real SaaS need in this run.
- Ordering for CLI tools rests on general practice and no cited source; treat it as a hypothesis.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Official MCP Registry API (re-test) | https://registry.modelcontextprotocol.io/openapi.yaml | Keyless `/v0.1/servers` with `search`, `version=latest`, `updated_since`; 14-23 s latency seen; namespace-verified, unmoderated for safety | curl | 2026-10-16 | **Use** as first MCP lead source with `version=latest`, vendor-namespace filter and 60 s timeout; hijack risk (155 expired-domain entries, Air Security 2026-08-27) |
| Smithery registry API | https://registry.smithery.ai/servers | Keyless search with `verified`, `useCount`, `remote`; many unverified zero-use entries | curl | 2026-10-16 | Fallback lead source; docs/terms not opened |
| PulseMCP API | https://api.pulsemcp.com/v0.1/servers | MCP directory API; 401 without X-API-Key | curl | 2026-10-16 | Skip unless John provides a key |
| Glama API | https://glama.ai/api/mcp/v1/servers | MCP directory API; 401 without key; attribution licence | curl | 2026-10-16 | Skip unless John provides a key |
| mcp.so | https://mcp.so | MCP directory website; no JSON API found | web | 2026-10-16 | Skip; highest invalid-link rate in 2025 study |
| GitHub MCP Registry | https://github.com/mcp | Curated list (44 at launch) with enterprise allow-list; 403 from sandbox | web | 2026-10-16 (blog opened; page 403) | Fallback by hand on John's machine |
| Claude plugin marketplaces (official, community) | https://code.claude.com/docs/en/plugins/anthropic-marketplaces | Git-hosted `marketplace.json` catalogs; community has automated screening | Claude Code | 2026-10-16 | **Use** as second MCP/plugin source; greppable |
| Claude Connectors Directory | https://claude.com/docs/connectors/directory | Verified and Community remote MCP connectors across Claude products | claude.ai / Claude Code | 2026-10-16 | Use for named SaaS; no listing API found |
| Docker MCP Catalog / Toolkit | https://docs.docker.com/ai/mcp-catalog-and-toolkit/catalog/ | Docker-signed MCP images, Dynamic MCP search, `docker mcp catalog server ls` | Docker | 2026-10-16 | Use if Docker is present; needs Docker Desktop for the toolkit |
| awesome-mcp-servers (punkpeye) | http://github.com/punkpeye/awesome-mcp-servers | Community-curated MCP list | web | 2026-10-16 | Orientation only |
| npm registry search API | https://registry.npmjs.org/-/v1/search | Keyless package search with downloads and dates; keyword-noisy | curl | 2026-10-16 | Use to confirm names, not to choose |
| PyPI JSON / Simple API | https://docs.pypi.org/api/ | Exact-name metadata; search disabled | curl | 2026-10-16 | Use by exact name only |
| deps.dev API v3 | https://docs.deps.dev/api/v3/ | Keyless package health, advisories, Scorecard, deprecation; no free-text search | curl | 2026-10-16 | **Use** as the health lookup after a name is known |
| libraries.io API | https://libraries.io/api/search | Package search; 401 without key | curl | 2026-10-16 | Skip (key) |
| GitHub REST search | https://docs.github.com/en/rest/search/search | Repo/code/topic search; 10/min unauth, 30/min auth, code 9-10; 403 in cloud sandbox | curl / gh | 2026-10-16 | Use only on John's machine with a token |
| Docker Hub search API | https://hub.docker.com/v2/search/repositories | Keyless image search; noisy | curl | 2026-10-16 | Fallback for CLI-as-image |
