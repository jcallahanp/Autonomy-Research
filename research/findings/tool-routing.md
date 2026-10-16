# Tool routing

A project-development research agent has five jobs: discover (find tools and repos), read
(pull a page or file), understand (reason about how a repo or system works), verify (check a
claim against a primary page), and map (draw the architecture). On 2026-10-16 every tool in
this session was opened against its official docs and then run once on a real research task,
and overlapping tools were run on the same query. The short answer: **Parallel Search is the
default for discovery and page reading** (free, keyless, compact, objective-focused excerpts,
batches up to 20 URLs); **Exa web_search is the second discovery opinion** (better at
describing-the-ideal-page semantic queries, but ~2x the output and a metered account);
**DeepWiki ask_wiki_question is the default for understanding a public repo** (free, no auth,
~4k chars, grounded answers), with `git clone --depth 1` + grep as the verification step;
**Context7 is for API syntax of a known library only**; **WebFetch is the citation tool** (it
reads up to 100k chars of the real page and answers a prompt, so the claim can be tied to the
URL); **Playwright is a last resort** (slow, blocked by Cloudflare/Vercel bot checks on two of
three test sites, and its snapshots are 45-95 KB). `read_wiki_contents`, Mermaid render, and
Playwright snapshots are too large for the lead agent's context and belong in a subagent.
Three cheap additions are worth making now: Firecrawl keyless MCP (fallback fetcher), the
official MCP registry API (keyless tool discovery), and Sourcegraph's keyless stream API
(cross-repo code search). gh CLI, Jina Reader and grep.app failed in this cloud environment.

## Questions and answers

### Q1. Which tool should run first for "find tools / unknown GitHub repos"?

**Answer: Parallel `web_search`, with Exa `web_search_exa` as a second opinion. Built-in
WebSearch is a weak third.** Confidence: high (same query on all three, results compared).

Test query: "GitHub repos that give Claude Code agents persistent task memory".

| Tool | Results | Hit the canonical repo (steveyegge/beads)? | Output size | Notes |
| --- | --- | --- | --- | --- |
| Parallel web_search (3 queries, 1 call) | 10 URLs with excerpts | Yes, ranked #1, plus pkg.go.dev mirror, backloghq/backlog, memory-mcp | ~12,000 chars JSON | Excerpts carried install commands and CLI names; enough to cite without fetching |
| Exa web_search_exa (numResults 8) | 8 GitHub READMEs with highlights | No (returned agent-memory, handoff-mcp, claude-mem, agendum, choda-deck, cas, continuum, agentmemory) | ~22,000 chars | Richer long-tail discovery; highlights include noise (flag-emoji language lists). Needs the `objective` field |
| WebSearch (standard) | 9 URLs + model-written summary | Only as "a mention on a third-party listing site" | ~3,000 chars | Returned PyPI, pkg.go.dev, blogs; docs say it is US-only and returns titles+URLs without fetching pages |
| Exa agent_run (effort minimal) | 5-row table with citations | No; returned five low-visibility repos (cc-memory, memem, mnemo, memory_map, claude-code-memory), confidence "medium" | ~3,000 chars, 3 searches, **$0.012 charged** | Took noticeably longer than a search; usage-based, requires OAuth/API key per Exa docs |

Routing rule: run Parallel first; if the top 10 lack a GitHub repo or the task is "list many
candidates", add one Exa call. Do not use agent_run for a one-shot list; it spent money and
found worse repos than a single search.

### Q2. Which tool should read a page once a URL is known?

**Answer: Parallel `web_fetch` (excerpt mode) for research reading; WebFetch for the
citation step; Exa `web_fetch_exa` when repo metadata (stars, contributors) is wanted;
Playwright only when the first three fail and the site is not bot-protected.** Confidence: high.

Test: read https://github.com/steveyegge/beads and extract storage model, install command,
agent integrations.

| Tool | What came back | Size | Correctness |
| --- | --- | --- | --- |
| Parallel web_fetch (objective set) | Excerpts spanning README sections: Quick Start, Essential Commands, Installation, **Storage Modes**, HTTP backend, Git-free usage | ~7,000 chars | Complete; objective-steered excerpts reached sections 4k chars past the top |
| Exa web_fetch_exa (maxCharacters 4000) | Repo metadata header (27,789 stars, 1,880 forks, license, languages, top contributors) then README from the top, cut at "Essential" | ~4,500 chars | Truncated before Storage Modes; metadata is a bonus no other tool gives |
| WebFetch (prompt) | A small model's answer with quoted phrases; page reported as ~30k chars | ~1,500 chars | Correct and quotable; on two other pages (github-mcp-server README 131,536 chars; code.claude.com/docs/en/mcp 122,928 chars) it stopped at 100,000 chars and offered `offset` |
| Playwright browser_navigate | Inline result ~300 chars; accessibility snapshot written to `.playwright-mcp/page-*.yml` | **95,370 bytes** on disk (45,295 for a docs page) | Content present but as a YAML tree of every nav link; would need `browser_find` or a subagent to extract anything |
| git clone --depth 1 + Read | Whole repo | 3.7 s, 77 MB, 4,885 files; README 18,563 bytes | Exact text, greppable (`grep -rl embeddeddolt docs/` found 5 docs); best for verification |

Blocked-site test (mcpservers.org, grep.app): WebFetch got 403 and 429; Playwright got a
Cloudflare "Just a moment..." 403 and a "Vercel Security Checkpoint" 429; Parallel and Exa
fetch both returned mcpservers.org content (their own fetcher/cache) but only the static
landing text of grep.app (JS app). So: when WebFetch is blocked, try Parallel/Exa fetch before
Playwright; Playwright does not beat bot checks from this cloud IP.

### Q3. Which tool should be used to understand a repo?

**Answer: DeepWiki `ask_wiki_question` first, `read_wiki_structure` to see coverage, then
`git clone --depth 1` + grep to verify any claim you will cite. Never call
`read_wiki_contents` from the lead agent.** Confidence: high.

- `ask_wiki_question` on steveyegge/beads returned ~4,000 chars: Dolt embedded vs server
  mode, `.beads/embeddeddolt/`, `refs/dolt/data` sync, git hooks as shims, 12 CLI commands,
  and the source pages it drew from. Clone + grep confirmed `embeddeddolt` appears in
  docs/core-concepts/index.md, docs/reference/configuration.md, git-integration.md, faq.md.
- `read_wiki_structure` returned ~2,500 chars: 13 top-level sections, 50+ pages.
- `read_wiki_contents` on obra/superpowers returned **905,414 chars** (176 `# ` headings);
  the harness refused to inline it and saved it to a file. Treat it as a subagent-only tool.
- DeepWiki docs (Devin) say it is "free, remote, no-authentication-required" and covers
  "public repositories" only; no rate limit is documented.
- GitHub MCP in this session: `get_file_contents` on the user's own repo worked;
  `gh search repos` and any search endpoint returned
  `HTTP 403: This GitHub API path is not available: sessions are bound to their configured
  repositories`, and `gh auth status` reported the GH_TOKEN invalid. GitHub code/repo search
  is therefore unavailable in Claude Code cloud sessions regardless of client.
- Sourcegraph `/.api/search/stream` worked keyless (HTTP 200, 6,436 chars of SSE for a
  `"bd prime" lang:markdown count:5` query, 1 content match in 3 repos); a `type:repo` query
  returned zero repository matches, so it is a code-search tool, not a repo-discovery tool.

### Q4. Context7 or fetch the docs directly?

**Answer: Context7 for "what is the exact syntax/option of library X", direct fetch (WebFetch
or Parallel fetch) for "what does the doc page say about topic Y", because Context7 returns
snippets from several pages and cannot be cited as one URL.** Confidence: medium (one
question, three tools).

Question: how to configure http and stdio MCP servers in `.mcp.json` for Claude Code.

- Context7 `resolve-library-id` ("Claude Code") returned five candidates (~2,000 chars):
  `/websites/code_claude` (6,015 snippets, benchmark 85.42, High reputation) was the right
  one; `/anthropics/claude-code` scored 67.16. `query-docs` (~3,500 chars) returned five
  JSON snippets, each with a source URL, but drawn from agent-sdk/mcp, managed-mcp and
  channels-reference pages, not the main `docs/en/mcp` page.
- Parallel web_search (2 queries) put `code.claude.com/docs/en/mcp` at #1 and #2 with the
  exact `.mcp.json` block and the warning that a `url` without `type` is a config error.
- WebFetch of `code.claude.com/docs/en/mcp` returned the quoted JSON and page length
  (122,928 chars, 100k read).
- Context7 free tier (context7.com/plans): "1,000 API calls" per month, then 20/day; Pro
  $10/seat for 2,000. Claude Code plugin needs "No API key" (context7.com/docs/clients/
  claude-code). The connector in this session is keyless.

### Q5. Which tools are safe for the lead agent and which must run in a subagent?

**Answer:** measured output sizes, 2026-10-16. Confidence: high for the numbers, medium for
the thresholds (a 25k-char rule of thumb, roughly 6k tokens).

| Tool | Typical output | Lead or subagent |
| --- | --- | --- |
| Parallel web_search | ~12k chars (10 results, 3 queries); docs cap excerpts at "roughly 25,000 characters" per call | Lead |
| Parallel web_fetch (excerpt) | ~7k chars per URL; `full_content: true` warned as "tens of thousands of tokens" | Lead; never `full_content` in lead |
| Exa web_search_exa | ~22k chars for 8 results | Lead with numResults <= 5, else subagent |
| Exa web_fetch_exa | bounded by maxCharacters (default 3,000) + ~500 metadata | Lead |
| Exa agent_run | ~3k chars but metered ($0.012 minimal, $0.025 low, up to $1 xhigh; auto defaults $5 cap) | Subagent, and only with a budget line |
| WebSearch | ~3k chars | Lead |
| WebFetch | ~1-2k chars (model summary) | Lead; the citation tool |
| DeepWiki ask_wiki_question / read_wiki_structure | ~4k / ~2.5k chars | Lead |
| DeepWiki read_wiki_contents | 905k chars (superpowers) | Subagent only, or never |
| Context7 resolve + query | ~2k + ~3.5k chars | Lead (max 3 calls per question per its own instructions) |
| Playwright navigate/snapshot | ~300 chars inline, 45-95 KB snapshot file | Subagent; read the file with grep, not Read |
| Mermaid validate_and_render | 60,162 chars (58,243 is `rawSVG`) | Subagent, or `jq .valid` on the saved file; prefer a local `mmdc` validator |
| GitHub MCP get_file_contents | file size | Lead (own repo only in cloud sessions) |
| Bash: clone + grep | whatever you grep | Lead when targeted; subagent for whole-repo reading |

### Q6. Which candidate additions are worth adding (free tier only)?

**Answer:** add 3, later 5, skip 8. Confidence: high for existence/pricing (pages opened),
medium for value (only Sourcegraph, registry and Firecrawl's keyless endpoint were exercised).

| Candidate | Verdict | Reason (from the page opened) |
| --- | --- | --- |
| Firecrawl keyless MCP | **Add** | `https://mcp.firecrawl.dev/v2/mcp` with no credential exposes `firecrawl_search`, `firecrawl_scrape`, `firecrawl_parse`, "rate limited"; a third fetcher for sites that block WebFetch. Free account adds 1,000 credits/month, no card |
| Official MCP registry API | **Add** (curl, no MCP needed) | `GET https://registry.modelcontextprotocol.io/v0.1/servers?search=<q>&limit=N` returned HTTP 200 keyless (8,158 chars for 5 results). API frozen at v0.1, "preview". Results are Smithery-mirror heavy; filter on `repository.url` |
| Sourcegraph stream API | **Add** (curl) | Keyless on sourcegraph.com ("we can run queries without authentication"); SSE events; use for cross-repo code search since GitHub search is blocked here. Not for repo discovery (type:repo returned 0) |
| Tavily | Later | Free "Researcher" tier 1,000 credits/month, no card; hosted MCP `https://mcp.tavily.com/mcp/?tavilyApiKey=...` with search+extract. Overlaps Parallel/Exa; add only if both hit rate limits. Sign-up: tavily.com -> dashboard -> copy key |
| Octocode MCP | Later | 8 GitHub tools (`ghSearchCode`, `ghSearchRepos`, `ghGetFileContent`...), MIT, `npx octocode-mcp@latest`; needs a GitHub token (gh/`GH_TOKEN`), and the cloud session's token is invalid and search endpoints are proxied-off, so it cannot work here today |
| Jina Reader | Later | "free for basic usage", 20 RPM keyless, 500 RPM with free key (10M free tokens). Live test from this container: HTTP 401 "blocked from performing anonymous queries due to bad IP reputation". Needs a key: jina.ai -> API key dashboard -> `Authorization: Bearer` |
| arXiv MCP (blazickjp) | Later | 19 tools, `uvx arxiv-mcp-server` (PyPI 0.8.2; do not npx), 3.2k stars, listed on registry; only relevant when the research turns to papers |
| Semantic Scholar API | Later | Keyless pool "1000 requests per second shared among all unauthenticated users"; free key by email, 1 RPS to start. No MCP needed; curl when needed |
| Sequential Thinking MCP | Skip | One `sequential_thinking` tool that logs numbered thoughts; adds a tool call per step with no new information. Registry already marks it low value |
| grep.app | Skip | Search UI and `/api/search` both answered 429 "Vercel Security Checkpoint" from this container, via curl and headless Chromium. No documented API |
| gh CLI | Skip (here) | Installed, but `gh auth status` says the token is invalid and search endpoints return 403 in cloud sessions; fine on a local machine |
| Perplexity Sonar | Skip | Pricing page (112k chars read in full) lists only per-token and per-request fees ($1-$15/M tokens, $5-$14 per 1k requests); no free tier found |
| Brave Search MCP | Skip | $5 free credit/month but "a credit card is required to subscribe to a free plan"; MCP server needs `BRAVE_API_KEY`; no hosted endpoint |
| Glama directory API | Skip | `GET /api/mcp/v1/servers` returned 401 "requires an API key" plus an attribution license; web page lists 99,471 servers |
| Smithery | Skip | "27,000+ MCPs", now part of Arcade.dev; remotes need a Smithery bearer key (seen in registry entries); no search API documented |
| mcpservers.org | Skip as a tool | Curated list, 403 to WebFetch and Playwright; readable via Parallel/Exa fetch when needed. Use the registry API instead |

## Evidence

Every URL below was opened on 2026-10-16 with the tool named.

- https://exa.ai/pricing — WebFetch — free tier "$10 in credits when you sign up, with no payment method required", resets monthly; search $4-7/1k; contents $1/1k pages; Agent $0.012 (minimal) to $1.00 (xhigh) per request, auto capped at $5.
- https://exa.ai/docs/reference/exa-mcp — WebFetch (after 308 redirect from docs.exa.ai) — hosted at `https://mcp.exa.ai/mcp`; "No API key is required to get started"; keyless is "Free rate-limited usage"; `agent_run requires OAuth or an API key`; 429 means free rate limits.
- Exa web_search_exa, web_fetch_exa, agent_run — run live (see Q1, Q2); agent_run result reported `costDollars.total: 0.012`, `searches: 3`.
- https://docs.parallel.ai/search/search-mcp — WebFetch — endpoints `search.parallel.ai/mcp` (anonymous) and `/mcp-oauth`; "free to use" with no key for "exploration and light use"; `web_fetch` up to 20 URLs, `objective` <= 200 chars, excerpts capped at "roughly 25,000 characters"; `full_content` "can be tens of thousands of tokens"; errors 400/401/402.
- Parallel web_search and web_fetch — run live (Q1, Q2, Q4).
- https://context7.com/plans — WebFetch — Free "1,000 API calls" per month then 20/day; Pro $10/seat, 2,000 calls, $5 per extra 1,000.
- https://context7.com/docs/clients/claude-code — WebFetch — plugin at `https://mcp.context7.com/mcp`; "No API key is required"; `npx ctx7 setup --claude` for keyed mode.
- https://context7.com/pricing — WebFetch — not the pricing page (an empty "Pricing Libraries" listing); the real page is /plans.
- Context7 resolve-library-id and query-docs — run live (Q4).
- https://docs.devin.ai/work-with-devin/deepwiki-mcp — WebFetch — `https://mcp.deepwiki.com/mcp`, "free, remote, no-authentication-required", public repos only, SSE endpoint deprecated; wrong field name (`serverUrl` vs `url`) causes silent ignore.
- DeepWiki read_wiki_structure, ask_wiki_question (steveyegge/beads), read_wiki_contents (obra/superpowers) — run live; the last was 905,414 chars.
- https://github.com/microsoft/playwright-mcp — WebFetch — "Uses Playwright's accessibility tree, not pixel-based input"; action timeout 5000 ms, navigation 60000 ms; "Playwright MCP is **not** a security boundary"; `browser_run_code_unsafe` "is RCE-equivalent"; "CLI workflows are more token-efficient".
- Playwright browser_navigate — run live on github.com/steveyegge/beads (snapshot 95,370 bytes), mcpservers.org (403 Cloudflare), grep.app/search (429 Vercel checkpoint).
- https://mermaid.ai/docs/ai/mcp-server — WebFetch — hosted `https://mcp.mermaid.ai/mcp`; nine tools; "every tool call requires authentication"; "a Basic Mermaid account works, no paid plan required"; returns "Rendered PNG Image & SVG image".
- Mermaid validate_and_render_mermaid_diagram — run live; 60,162-char result (`valid: true`, `rawSVG` 58,243 chars) saved to file by the harness.
- https://github.com/github/github-mcp-server — WebFetch (first 100k of 131,536 chars) — remote `https://api.githubcopilot.com/mcp/`; OAuth or PAT; default toolsets context, repos, issues, pull_requests, users; `--read-only` skips write tools.
- GitHub MCP get_file_contents on jcallahanp/Autonomy-Research — run live, succeeded. `gh search repos` — run live, HTTP 403 "sessions are bound to their configured repositories".
- https://code.claude.com/docs/en/tools-reference (via Context7 /websites/code_claude) — WebSearch "returns result titles and URLs. It doesn't fetch the result pages"; "may issue up to eight backend searches per call"; WebFetch has preapproved documentation domains and a `WebFetch(domain:...)` rule form.
- https://code.claude.com/docs/en/mcp — WebFetch — `.mcp.json` http example quoted; 122,928 chars; also Parallel web_search ranked it #1.
- https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking — WebFetch — tool `sequential_thinking` with `thought`, `nextThoughtNeeded`, `thoughtNumber`, `totalThoughts`; `npx -y @modelcontextprotocol/server-sequential-thinking`.
- https://www.firecrawl.dev/pricing — WebFetch — Free "1,000 per month" credits, "No cost, no card"; 10/min scrape/search; 1 credit = 1 page.
- https://docs.firecrawl.dev/mcp-server and /mcp-server/keyless — WebFetch — keyless endpoint `https://mcp.firecrawl.dev/v2/mcp`; "Keyless MCP is rate limited and exposes Search, Scrape, and Parse".
- https://www.tavily.com/pricing — WebFetch — Researcher 1,000 credits/month, no card; PAYG $0.008/credit; key required.
- https://docs.tavily.com/documentation/mcp — WebFetch — `https://mcp.tavily.com/mcp/?tavilyApiKey=<key>`; tools tavily-search, tavily-extract.
- https://jina.ai/reader/ — WebFetch — "Reader is free for basic usage"; 20 RPM keyless, 500 RPM free key; "Every new API key comes with 10M free tokens"; s.jina.ai search not available keyless. Live curl to r.jina.ai: HTTP 401 bad IP reputation.
- https://docs.perplexity.ai/getting-started/pricing — WebFetch (both halves, 112,157 chars) — Sonar $1/$1 per M tokens + $5-12 per 1k requests; no free tier mentioned.
- https://brave.com/search/api/ — WebFetch — Search $5/1k, "$5 in free credits each month", card "required to subscribe to a free plan". https://github.com/brave/brave-search-mcp-server — WebFetch — `BRAVE_API_KEY` required, `npx -y @brave/brave-search-mcp-server`.
- https://github.com/modelcontextprotocol/registry — WebFetch — "API freeze (v0.1)", "launched in preview"; https://registry.modelcontextprotocol.io/docs returned only a title to WebFetch. Live curl: `/v0/servers?search=github&limit=5` and `/v0.1/servers?search=arxiv&limit=3` both HTTP 200 keyless.
- https://github.com/bgauryy/octocode-mcp — WebFetch — "Evidence-first code research"; 8 default tools; token via `npx octocode auth login`, gh, or `GH_TOKEN`; Node 20.12+.
- https://cli.github.com/manual/gh_search_repos — WebFetch — `--limit` default 30; JSON fields incl. stargazersCount, pushedAt, license.
- https://sourcegraph.com/docs/api/stream_api — WebFetch — "On Sourcegraph.com we can run queries without authentication"; SSE events matches/progress/filters/alert/done. Live curl: HTTP 200.
- https://grep.app/ — WebFetch 429; Parallel and Exa fetch returned only "search for code, files, and paths across a million GitHub repositories". Live curl `/api/search`: 429 Vercel checkpoint.
- https://www.semanticscholar.org/product/api — WebFetch — "1000 requests per second shared among all unauthenticated users"; new key "1 RPS on all endpoints".
- https://github.com/blazickjp/arxiv-mcp-server — WebFetch — 19 tools, `uvx arxiv-mcp-server`, PyPI 0.8.2, 3.2k stars, optional `SEMANTIC_SCHOLAR_API_KEY`.
- https://smithery.ai/ — WebFetch — "Browse 27,000+ MCPs", "now part of Arcade.dev". https://glama.ai/mcp/servers — WebFetch — "99,471 servers"; live curl to its API: 401 key required.
- https://mcpservers.org/ — WebFetch 403; Playwright 403 "Just a moment..."; Parallel and Exa fetch returned the directory text (categories, featured Context7/DeepWiki/Exa/Firecrawl/GitHub entries).
- Local: `git clone --depth 1 https://github.com/steveyegge/beads` — Bash — 3.7 s, 77 MB, 4,885 files.

## Implications for the researcher plugin

1. **Decision table** (task -> primary -> fallback -> hand-off):

| Research task | Primary | Fallback | Hand to next step |
| --- | --- | --- | --- |
| Discover tools / repos for a need | Parallel web_search (2-3 queries, one call) | Exa web_search_exa (numResults 5, with `objective`) | Top 3 GitHub URLs -> Q "understand a repo"; non-GitHub URLs -> "read a page" |
| Discover MCP servers specifically | curl registry `/v0.1/servers?search=` | Parallel web_search with `site:github.com mcp` phrasing | `repository.url` list -> DeepWiki or clone |
| Read a known page for facts | Parallel web_fetch (excerpt, objective) | Exa web_fetch_exa -> Firecrawl keyless scrape -> Playwright (subagent) | Quoted lines + URL -> "verify/cite" |
| Verify and cite a claim | WebFetch with a pointed prompt (quote exact wording) | Parallel web_fetch with `full_content` in a subagent | One bullet in the Evidence section: URL, date, tool, claim |
| Understand how a public repo works | DeepWiki ask_wiki_question (after read_wiki_structure) | git clone --depth 1 + grep/Read specific files | Named files/functions -> clone to confirm before citing; diagram candidates -> Mermaid |
| Find where code does X across GitHub | Sourcegraph stream API (curl, `count:10`) | Exa web_search_exa with code phrasing | repo/file list -> get_file_contents (own repo) or raw.githubusercontent.com fetch |
| Library/API syntax | Context7 resolve -> query-docs (<= 3 calls) | WebFetch the official docs page | Snippet source URL -> cite that URL, not Context7 |
| Test an edge case in a tool | Bash (curl / clone / run) | Playwright (subagent) for browser-only behaviour | Observed output + command -> findings |
| Map an architecture | Write Mermaid locally; validate with `mmdc` or the Mermaid MCP in a subagent | Mermaid MCP `liveEditUrl` for a human to view | Small .mmd files, one concern each, linked from an index |
| Multi-step list-building with a budget | Exa agent_run (effort low, `budget.maxCostDollars` set) | Lead runs 3-4 Parallel searches itself | Rows with citations -> verify top rows with WebFetch |

2. **When NOT to use a tool.** Playwright: never as a first reader, never from the lead,
   never against Cloudflare/Vercel-protected sites (it fails identically to curl). agent_run:
   never for a single lookup (metered; worse recall than one search in the test). WebSearch:
   not for GitHub discovery (missed the canonical repo; US-only). read_wiki_contents: never
   inline. Mermaid MCP: not for every diagram edit (60k chars per render). GitHub MCP search
   tools: not in cloud sessions (403). Context7: not for "what does the doc say"; it answers
   "how do I write this call".

3. **Hand-off contract.** Every discovery result must be reduced to <= 3 URLs before any
   fetch; every fetch must end in one Evidence bullet (URL, date, tool, claim) or be dropped;
   every DeepWiki answer must have at least one claim confirmed by clone+grep before the
   repo is written up.

4. **Keys to collect, all free, no card:** Exa (already connected), Parallel (none needed),
   Context7 (none needed), Firecrawl keyless (none), Tavily (sign up, copy key), Jina (sign
   up; required from cloud IPs). Add `research/open-questions.md` entries for any paid key.

5. **Session-start checks** the plugin should run: `gh auth status` (expect invalid in
   cloud), `curl registry /v0.1/servers?limit=1`, `curl search.parallel.ai` health via one
   tiny search, and that `.playwright-mcp/` stays gitignored (it is today; 4 snapshot files
   totalling ~140 KB landed there during this test).

6. **EARS requirements derived:**
   - When a search returns more than three candidate URLs, the router shall select at most
     three before any fetch.
   - When a page read is needed and the site returned 403/429 to WebFetch, the router shall
     try Parallel fetch, then Exa fetch, then Firecrawl keyless before Playwright.
   - When a tool's output is expected to exceed 25,000 characters, the router shall run that
     call in a subagent and return a summary of at most 2,000 characters.
   - When a claim about a repository comes from DeepWiki, the agent shall confirm it against
     the cloned source before citing it.
   - When agent_run is invoked, the agent shall set `budget.maxCostDollars` and record the
     returned `costDollars.total` in the findings.

## Tools evaluated

| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Parallel Search MCP (web_search, web_fetch) | https://docs.parallel.ai/search/search-mcp | Keyless web search with answer-ready excerpts; fetch up to 20 URLs with objective-focused excerpts | claude.ai connector | 2026-10-16 | **Primary** for discovery and reading |
| Exa MCP (web_search_exa, web_fetch_exa) | https://exa.ai/docs/reference/exa-mcp | Semantic search with highlights; fetch with repo metadata | claude.ai connector | 2026-10-16 | Second opinion for discovery; fetch when stars/contributors wanted |
| Exa agent_run | https://exa.ai/pricing | Multi-step metered research agent | claude.ai connector | 2026-10-16 | Subagent only, with budget; $0.012 spent in test |
| WebSearch (built-in) | https://code.claude.com/docs/en/tools-reference | Titles + URLs from Anthropic backend, US-only | Claude Code | 2026-10-16 | Fallback only |
| WebFetch (built-in) | https://code.claude.com/docs/en/tools-reference | Fetch up to 100k chars and answer a prompt | Claude Code | 2026-10-16 | **Primary** for verify/cite |
| DeepWiki MCP | https://docs.devin.ai/work-with-devin/deepwiki-mcp | Q&A and wiki over public GitHub repos, no auth | `.mcp.json` (http) | 2026-10-16 | **Primary** for understanding repos; read_wiki_contents subagent-only |
| Context7 MCP | https://context7.com/plans | Versioned library docs snippets; 1,000 calls/month free | claude.ai connector | 2026-10-16 | Keep, for API syntax only |
| Playwright MCP | https://github.com/microsoft/playwright-mcp | Headless Chromium via accessibility snapshots | `.mcp.json` (stdio) | 2026-10-16 | Last resort, subagent only; blocked by bot checks |
| Mermaid Chart MCP | https://mermaid.ai/docs/ai/mcp-server | Validate and render Mermaid (free account, auth required) | claude.ai connector | 2026-10-16 | Keep for validation via subagent; 60k-char output |
| GitHub MCP | https://github.com/github/github-mcp-server | Repo/file/PR tools; search blocked in cloud sessions | claude.ai connector | 2026-10-16 | Own-repo reads only |
| gh CLI | https://cli.github.com/manual/gh_search_repos | GitHub search/API from shell | preinstalled; token invalid here | 2026-10-16 | Skip in cloud; fine locally |
| git clone + grep | (local) | Exact source for verification | Bash | 2026-10-16 | **Primary** verification for repos |
| Official MCP registry API | https://github.com/modelcontextprotocol/registry | Keyless `/v0.1/servers?search=` listing, preview/frozen API | curl | 2026-10-16 | **Add** |
| Sourcegraph stream API | https://sourcegraph.com/docs/api/stream_api | Keyless cross-repo code search on sourcegraph.com | curl | 2026-10-16 | **Add** for code search |
| Firecrawl keyless MCP | https://docs.firecrawl.dev/mcp-server/keyless | Search/scrape/parse with no key, rate limited | not installed (`https://mcp.firecrawl.dev/v2/mcp`) | 2026-10-16 | **Add** as fallback fetcher |
| Tavily MCP | https://docs.tavily.com/documentation/mcp | Search + extract, 1,000 free credits/month with key | not installed | 2026-10-16 | Later |
| Octocode MCP | https://github.com/bgauryy/octocode-mcp | GitHub code/repo research tools, needs GitHub token | not installed | 2026-10-16 | Later (blocked by cloud token) |
| Jina Reader | https://jina.ai/reader/ | URL -> markdown; 20 RPM keyless, 500 with free key | curl (401 from this IP) | 2026-10-16 | Later, needs free key |
| arXiv MCP server | https://github.com/blazickjp/arxiv-mcp-server | 19 paper tools via uvx | not installed | 2026-10-16 | Later |
| Semantic Scholar API | https://www.semanticscholar.org/product/api | Scholarly graph, keyless shared pool | curl | 2026-10-16 | Later |
| Sequential Thinking MCP | https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking | Numbered thought log tool | not installed | 2026-10-16 | Skip |
| grep.app | https://grep.app/ | Code search over ~1M repos; blocked 429 | curl / Playwright | 2026-10-16 | Skip |
| Perplexity Sonar | https://docs.perplexity.ai/getting-started/pricing | Paid search-grounded LLM, no free tier | not installed | 2026-10-16 | Skip |
| Brave Search MCP | https://brave.com/search/api/ | Search API, card required for free credits | not installed | 2026-10-16 | Skip |
| Glama MCP directory | https://glama.ai/mcp/servers | 99,471 servers; API needs key + attribution | curl (401) | 2026-10-16 | Skip |
| Smithery | https://smithery.ai/ | 27,000+ MCPs, Arcade.dev; bearer key for remotes | not installed | 2026-10-16 | Skip |
| mcpservers.org | https://mcpservers.org/ | Curated MCP list; 403 to direct fetchers | via Parallel/Exa fetch | 2026-10-16 | Skip as a tool; read occasionally |

## Open questions

- Parallel's free-tier numeric rate limits are undocumented ("higher rate limits" with a key);
  no 429 was hit in ~6 calls. How many calls per hour does a research session need?
- Exa keyless rate limits are undocumented; the connector here appears signed in (agent_run
  worked), so its $10/month free credit is the real ceiling. Who owns that account?
- Does DeepWiki rate-limit `ask_wiki_question`, and how stale are its wikis for fast-moving
  repos (beads moved from steveyegge to gastownhall; DeepWiki still answered under the old name)?
- Firecrawl keyless daily limit is on a rate-limits page not opened here.
- Whether the Mermaid MCP can return only `valid`/`liveEditUrl` without `rawSVG` (no
  parameter seen); otherwise a local `@mermaid-js/mermaid-cli` validator is the cheaper path.
- Whether the GitHub MCP connector's search tools work outside cloud sessions (the 403 came
  from the session proxy, not GitHub).
- Playwright snapshot files accumulate in `.playwright-mcp/` (gitignored); who cleans them up
  between research runs?

## Verification
Checked 2026-10-16 by the verifier. Sample: 20 cited claims.
Verified: 15. Unverified: 5.
- Unverified: Context7 free plan "then 20/day" — https://context7.com/plans — the page grants 20 bonus calls a day only while a free user is blocked after 1,000 calls, not a standing allowance.
- Unverified: GitHub MCP page length "131,536 chars" — https://github.com/github/github-mcp-server — WebFetch reports 131,535 characters; off by one, possibly a counting difference.
- Unverified: Jina "500 RPM with a free key" — https://jina.ai/reader/ — the rate-limit table says 500 RPM, but the FAQ gives 100 RPM for the free tier; uncertain.
- Unverified: Semantic Scholar "new key ... 1 RPS on all endpoints" — https://www.semanticscholar.org/product/api — the page says "introductory rate limit for an API key is 1 RPS on all endpoints" and does not say "new".
- Unverified: Glama "99,471 servers" — https://glama.ai/mcp/servers — the page states 99,591 servers (updated 2026-10-16 04:48).
