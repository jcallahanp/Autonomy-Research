# Tool discovery (Area 3) - digest
Source: research/findings/engineer-tool-discovery.md; verification: 19 of 20 verified, 1 unverified (E25 "about 4%" figure; page says 3.1%-8.6%)

## Decision
Confidence medium (Q9). One bounded, keyless discovery pass inside a build, reusing the research agent's skills:
- Step 0, lookup: grep `dead-ends.md` and `tool-registry.md`. A known verdict ends the pass (E120, E126).
- Discovery ladder for a named SaaS:
  1. The vendor's own docs.
  2. The official MCP Registry. It is keyless (E1, E2), but it verifies namespace, not code (E4), and "consumers should assume minimal-to-no moderation" (E5).
  3. Claude plugin marketplaces and the Connectors Directory, where "Verification isn't a security audit" (E10-E13).
  4. The Docker MCP Catalog, if Docker is present (E14, E15).
  5. Smithery's keyless API, last (E16).
  For libraries, web search names the candidates and exact-name npm and PyPI lookups plus deps.dev confirm them (E30, E32, E34).
- Keyless vet card on at most 3 candidates, each call under 1 s:
  - OSV `querybatch` (E44, E45).
  - deps.dev licence and project (E46-E48).
  - The Scorecard API, where 404 means unavailable, not pass (E41).
  - npm attestations or Socket `sfw` (E50, E54).
  - A read-only clone grep.
  MCP servers add launch-command and scope review plus a hash of the tool definitions (E58-E64).
- Route, stopping at the first yes (worker inference, Q3):
  1. A script or library when an official CLI, SDK or REST API covers the writes.
  2. MCP only when it adds OAuth consent, per-call approval or exploration (E88). Token cost matters little, because Claude Code defers MCP tool definitions (E86).
  3. The browser last and narrow (E94).
- Envelope (the worker's untested design): tiers D0-D2, at most 3 workers with about 15 calls each, at most 3 URLs per cluster, a 10-minute box, stop at the first passing candidate. It rests on returns plateauing after about three searches (E101) and effort being weakly aligned with quality (E102).
- Hand-back is three typed blocks: a `ROW:`, an integration-card patch and a plan entry. Negatives go to `dead-ends.md` with `retry-when` (E74, E121, E122).
- Registries and stars are leads, never trust signals: 155 expired-domain hijacks (E8), a backdoored package (E22), a cloned malicious server (E23).

## Alternatives and rejected
- Docker MCP Catalog first when Docker is the host runtime - kept as alternative (E14, E15)
- Always MCP - kept as alternative - simple, weaker on writes and determinism (Q9)
- Always scripts - kept as alternative - fails where OAuth is needed or no API exists (Q9)
- Full research-skill tiers at build time - kept as alternative - stalls the build (E104)
- Cloudflare-style Code Mode gateway - kept as reference - pays off only for a large tool surface (E84)
- GitHub search with a token on John's machine - kept as alternative (E27)
- mcp.so - rejected - no JSON API (E19)
- Glama and PulseMCP APIs - rejected - need a key (E17, E18)
- GitHub topic and code search in the cloud - rejected - 403 (E28)
- PyPI search - rejected - disabled (E31)
- libraries.io - rejected - needs a key (E33)
- Star counts as a pass signal - rejected - can be fabricated (E23)
- npm text search for choosing - rejected - noise and typosquats (E30, E37)
- Scorecard HTML viewer for agents - rejected - the API is better (E41, E69)
- Standalone Snyk Advisor - rejected - gone, migrated (E53)
- agent-scan inside triage - rejected - can execute commands; throwaway-VM spike only (E67)
- One transport for the whole engineer - rejected - choose per integration (E92, E93)
- Token multipliers as a decision driver - rejected - unreproducible (E86, E93)
- Unbounded gap rounds at build time - rejected - conflicts with the plateau evidence (E101, E103)

## Stack
| Tool | What it does here | Where it runs | Cost | Evidence |
| --- | --- | --- | --- | --- |
| Official MCP Registry API | First MCP lead source (`version=latest`, vendor-namespace filter, timeout); 14-23 s latency seen | curl | Free, keyless | E1-E3 |
| Claude plugin marketplaces / Connectors Directory | Second source; `marketplace.json` is greppable | Claude Code | Free | E10-E13 |
| Docker MCP Catalog | Signed local servers, if Docker is present | Docker | Free | E14, E15 |
| Smithery registry API | Last-rung lead source | curl | Free, keyless (terms not opened) | E16 |
| npm search / PyPI JSON | Confirm names (never choose with npm search) | curl | Free | E30, E32 |
| deps.dev API v3 | Licence, advisories, deprecation, footprint | curl | Free, keyless | E34, E46-E48 |
| OSV.dev `querybatch` | Advisory check by version | curl | Free; "no limits" stated | E44, E45 |
| OpenSSF Scorecard REST API | Repo hygiene checks; 404 = unavailable | curl | Free, keyless | E41, E42 |
| npm attestations | Provenance, a positive signal only | curl | Free | E49, E50 |
| Socket `sfw` (to spike) | Install-time malicious-package block | CLI | Free plan $0: 1,000 scans/month, 500 API req/hour | E54, E55 |
| OWASP MCP cheat sheet + MCP spec security practices | MCP vetting checklist | Docs | Free | E58-E64 |
| Claude Code MCP tool search | Defers tool definitions; off behind a non-first-party `ANTHROPIC_BASE_URL` | Claude Code | Free | E86, E87 |
No paid option is recommended (Q9).

## Setup steps
| Step | Automated or John | How it is verified |
| --- | --- | --- |
| 1. Create `dead-ends.md` and the registry Meta cell or sidecar `research/tool-registry.meta.csv` (Q6) | Automated | Schema keeps the six-column `ROW:` contract (E74, E75) |
| 2. Vet-card script, HTTP requests only, never touching candidate code (Q5) | Automated | Each call answers under 1 s (E45, E50); spike 12 end to end |
| 3. Check MCP tool search is on, including behind any proxy (E87) | Automated | `/context` cost measured (spike 6) |
| 4. SessionStart or PreToolUse reminder to grep `dead-ends.md` and the registry (Implications 7) | Automated | Spike 8: does it change behaviour |
| 5. Staleness script: `recheck_by` past, version behind, archived flip, 404 (Q6) | Automated | Lists stale rows |
| 6. **GitHub token on John's machine, only if the engineer runs locally** | John (optional) | Spike 5 |
| 7. **PulseMCP or Glama keys, only if John provides them** | John (optional) | Not needed by default |

## Repo composition
- Files:
  - `dead-ends.md`: path, date, version, probe, result, evidence, `retry-when` (E121).
  - `tool-registry.md` plus Meta fields: `version_checked`, `source_depth`, `verdict_code`, `risk`, `recheck_by` (90 days for MCP servers and agent tools, 180 for libraries), `trigger`, `superseded_by`, and for MCP servers `tooldef_sha256`, `scopes` and `local|remote` (Q6).
  - A short approved list (tool, version, install command, hash), kept apart from the research log (Q6).
  - Integration cards. Where `docs/integrations/` lives is a plan decision (Open questions).
- Scripts: vet card, staleness check.
- Hooks: the dead-end lookup reminder (step 4).
- Skill changes (recommendations only; nothing in `plugin/` changed):
  - research gets a build-mode switch (D0-D2, a worker cap of 3, a 10-minute box, no gap round, outputs to the engineer repo).
  - tool-scan gets a stop-at-first-pass mode, a capability-card input, the route result recorded in the row and wider MCP discovery.
  - repo-triage gets its 11 vetting gaps fixed (OSV, the Scorecard API, licence, footprint, manifest scripts, typosquat, MCP static checks, version recorded, a path without DeepWiki, aligned verdicts).
  - spike and interview get an `inconclusive` verdict (Implications 1-6).
- Skill per phase: interview for intake, system-map for as-is, tool-scan + repo-triage + spike for feasibility, tool-scan D0/D1 for build, research D1 and repo-triage for audit (Q8).
- Superpowers, Beads, Ralph: not discussed in this findings file.

## Spikes
| Spike | Probe (what to run) | Pass criterion |
| --- | --- | --- |
| 1 | Official registry call 10 times from the real runtime | Latency and timeouts recorded; timeout (60 s proposed) and caching settled |
| 2 | Vendor-namespace registry entries for Attio, Clay, n8n, Supabase | Present or absent known |
| 3 | Fetch `claude.com/plugins` and `marketplace.json` by script from the cloud runtime | Fetch succeeds |
| 4 | Smithery keyless search at volume; meaning of `verified` | No key needed at volume; meaning known |
| 5 | GitHub search with a token on John's machine | Works locally |
| 6 | `/context` cost of Attio, Clay, n8n MCP with tool search on and off | Cost measured |
| 7 | D1 on three real capabilities | 15 calls and 10 minutes calibrated |
| 8 | Hook that greps `dead-ends.md` and the registry | Changes behaviour |
| 9 | One MCP write round-trip with approval in an unattended session (E88) | Write completes with approval |
| 10 | agent-scan on one candidate MCP server in a throwaway VM | What it catches is measured |
| 11 | Hash `tools/list` on a sandboxed server, re-fetch and diff | Rug-pull detected |
| 12 | One end-to-end ladder pass on a real SaaS need | Pass ends with typed blocks |
| 13 | Re-check a vendor-namespace domain at install time (E8) | MCPJacking defence works |

## Requirements served
- R19: this area is the bounded discovery pass, with every candidate logged as a `ROW:` with a verdict and reason (Decision).
- R7: at most 3 candidates per pass, negatives in `dead-ends.md` with `retry-when` so they are not retried (E121), and a lookup first (E120).
- R18 / Q3: at the end of the time box with no passing candidate, write an `inconclusive` dead-end, flag John and continue with the browser or a manual step (Q4).
- R11: card patches feed the one setup list (E122).
- R13: the route procedure sends only API-less operations to the browser (Q3, E94).
- Q1: the criteria order puts outcome (auth, write coverage, maintenance, determinism) before token cost (Q3).
- Q6: everything is free and keyless; Socket Free is $0 within quotas (E55).

## GTM scenario
- Scan as-is: gap. This area only supports it with research D1 per unfamiliar API surface (Q8).
- Fix Attio tables and views: the route procedure picks REST for the data model and the browser for views, per the settled table (E94).
- Clay workflows: the route procedure picks the Clay plugin or CLI for Workflows and the browser for tables (E94). Spike 2 checks registry entries.
- Clean data: gap.
- Finish tooling: per-capability route choice and vetting for any missing tool. Spike 6 measures the Attio, Clay and n8n MCP context cost.

## Tensions
- Untested worker designs the decision rests on: the ladder order, the envelope numbers (3 workers, 15 calls, 10 minutes) and the registry schema. The CLI-tool ordering has no cited source (Open questions).
- Smithery: this run says it is a usable fallback (E16), but tool-registry.md:160 and tool-routing.md:154 still say "Skip" (E124). Those rows were not rewritten.
- The research skill's cap of 8 workers (E104) conflicts with the build envelope of 3. The plugin changes are recommendations only.
- MCP writes prompt per call (E88), and Area 6 notes that Attio MCP writes ask for confirmation. Both sit against R15 and R16, so spike 9 decides whether MCP writes work unattended.
- GitHub search returns 403 in the cloud sandbox (E28), so discovery is weaker if the engineer runs in cloud sessions. This depends on the runtime choice.
- Tool search is off behind a non-first-party `ANTHROPIC_BASE_URL` (E87). That matters if other models attach through a proxy (Constraints).
- Contradictions reconciled by scope, not settled:
  - Token usage explaining 80% of variance (E100) vs the plateau (E101, E102).
  - MCP 4x-35x token claims (excluded, highlights only) vs 0.43x-29x (E92, E93).
  - Spike-worker no-retry vs two attempts in a build trial (Q8).
- "Parallel Search returned Too Many Requests on every call" was excluded. It bears on the routing default in tool-routing.md (E38).
- Scorecard's skip of Maintained for young repos rests on an unquoted claim (excluded claim 13).

## Open for John
- Whether a D2 pass may go beyond 3 workers (the envelope says that needs John).
- Whether to provide a GitHub token (local runs), or PulseMCP or Glama keys.
- How inconclusive dead-ends should reach him (via the approval batch).
