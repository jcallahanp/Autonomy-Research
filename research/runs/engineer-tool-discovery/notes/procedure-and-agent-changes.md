# Decision procedure, discovery envelope and research-agent changes

Brief: Define how the engineer chooses between a connector or MCP server, a direct API call, a script or library, and the browser; a bounded envelope for a discovery pass inside a build; and how the research agent's skills map onto engineer phases and what must change.
Run: research/runs/engineer-tool-discovery/PLAN.md

Note on quotes: pages were opened with WebFetch (a small model returns excerpts) and Exa highlights were used only to choose pages; every quote below came from the WebFetch result for that URL. Parallel web_fetch returned "Too Many Requests" on 2026-10-16.

## Decision procedure: connector or MCP, API, script or library, browser

### Takeaway
Decide per capability, not once: (1) if a free vendor CLI, SDK or documented REST API covers the needed reads and writes, write a small script or library call and keep it as a file; (2) use an MCP server or connector when the service has no usable CLI or SDK, needs OAuth consent or per-user scopes, or the call is interactive and exploratory; (3) use the browser only for the specific operations the API lacks. Token cost of MCP schemas is now mostly a configuration issue in Claude Code (tool search defers definitions), so it is a weak criterion; auth, write coverage, determinism and secrets exposure are the strong ones. Confidence: medium (vendor docs plus practitioner and one preprint; no controlled study for our case).

### Cited findings
- MCP connects, skills teach: connectors give access to a service, skills carry the procedure. Anthropic recommends both together — https://claude.com/blog/skills-explained, opened 2026-10-16, WebFetch — Quote: "MCP connects Claude to data; Skills teach Claude what to do with that data."
- Anthropic's own engineering view: loading every tool definition and passing every intermediate result through the model is costly, and code execution cuts it, at an operations price — https://www.anthropic.com/engineering/code-execution-with-mcp, opened 2026-10-16, WebFetch — Quote: "reduces the token usage from 150,000 tokens to 2,000 tokens."
- Same post, the cost side of the code route — https://www.anthropic.com/engineering/code-execution-with-mcp, opened 2026-10-16, WebFetch — Quote: "These infrastructure requirements add operational overhead and security considerations that direct tool calls avoid."
- Same post, secrets: code execution lets data be tokenised so the agent does not handle it — https://www.anthropic.com/engineering/code-execution-with-mcp, opened 2026-10-16, WebFetch — Quote: "This prevents the agent from accidentally logging or processing sensitive data."
- Cloudflare Code Mode: models write code against MCP-derived APIs better than they call tools — https://blog.cloudflare.com/code-mode/, opened 2026-10-16, WebFetch — Quote: "LLMs are better at writing code to call MCP, than at calling MCP directly."
- Code Mode secrets model: bindings hold authorisation, the sandbox cannot leak keys — https://blog.cloudflare.com/code-mode/, opened 2026-10-16, WebFetch — Quote: "This means that the AI cannot possibly write code that leaks any keys."
- Claude Code defers MCP tool definitions by default, so the "schemas bloat context" criterion is largely configured away on current models — https://code.claude.com/docs/en/mcp, opened 2026-10-16, WebFetch — Quote: "Only tool names and server instructions load at session start, so adding more MCP servers has minimal impact on your context window."
- Tool search is off on a non-first-party base URL and on pre-Sonnet-4 models (relevant if the engineer runs behind a proxy) — https://code.claude.com/docs/en/mcp, opened 2026-10-16, WebFetch — Quote: "Claude Code disables it when `ANTHROPIC_BASE_URL` points to a non-first-party host, since most proxies don't forward `tool_reference` blocks."
- Claude Code prompts for MCP writes per call and can mark a tool as always needing a human — https://code.claude.com/docs/en/mcp, opened 2026-10-16, WebFetch — Quote: "Claude Code shows that tool's permission prompt on every call, even in `acceptEdits`, `auto`, and `bypassPermissions` permission modes"
- Third-party MCP servers carry prompt-injection risk; verify trust before connecting — https://code.claude.com/docs/en/mcp, opened 2026-10-16, WebFetch — Quote: "Servers that fetch external content can expose you to prompt injection risk."
- Output cap: MCP results over 10,000 tokens warn, default max 25,000 — https://code.claude.com/docs/en/mcp, opened 2026-10-16, WebFetch — Quote: "the default maximum is 25,000 tokens"
- Tool design: wrapping every endpoint is a weak tool; consolidate and return high-signal output — https://www.anthropic.com/engineering/writing-tools-for-agents, opened 2026-10-16, WebFetch — Quote: "tool implementations should take care to return only high signal information back to agents."
- Controlled-ish measurement 2026: the scaffolding, not the protocol, dominated cost; CLI-only scaffoldings were cheaper and finished every run; MCP failures cost more — https://arxiv.org/abs/2608.08654, opened 2026-10-16, WebFetch — Quote: "12.9 per cent of the money spent on MCP runs bought no completed work against 2.2 per cent on CLI runs"
- Same paper, caution on the headline ratios — https://arxiv.org/abs/2608.08654, opened 2026-10-16, WebFetch — Quote: "thirteen strictly paired MCP-to-CLI ratios span 0.43x to 29x, with outliers on both sides."
- Per-task API-versus-browser table already settled in the repo: Attio objects/attributes/lists by REST, views and Workflows need the browser; Clay tables cannot be created programmatically — /home/user/Autonomy-Research/research/findings/engineer-browser.md:Q11 table (line 522 onward), read 2026-10-16, Read — Quote: "you **cannot** create tables programmatically"
- Tool registry carries the browser stack verdicts (Playwright CLI primary, MCP alternate, Stagehand only as optional replay) — /home/user/Autonomy-Research/research/tool-registry.md:204-210, read 2026-10-16, Read — Quote: "**Use**: primary driver for the engineer; spike on real Attio/Clay tasks"

### Contradictions
- Practitioner posts say MCP costs 4x to 35x more tokens than CLI (secondary reports, not opened as primary: Exa highlights only, see Gaps) — versus the preprint above, which reports paired ratios of 0.43x to 29x and says scaffolding dominates. The Claude Code docs (tool search default) also remove the upfront cost the posts measure. Settle by measuring in the actual engineer session with `/context` before and after adding a server.
- A 2026 course page says the token argument against MCP "is out of date" while Fern/Numlytics-type posts still lead with it. Search excerpts only; treat as unresolved.

### Inferences
- Decision procedure (mine), ordered, stop at the first yes, each step with a gate:
  1. Dead-end and registry lookup (grep `dead-ends.md`, `tool-registry.md`): a known verdict ends the search.
  2. Does an official vendor CLI/SDK/REST cover every operation the task needs, including writes? Then script/library. Gates: free tier works, auth is a key or token John can create once, retries and pagination are in the library, output can be asserted in a test.
  3. Is there an official or well-maintained MCP server/connector, and does it add something a script cannot: OAuth consent John already did, per-call human approval on writes, a hosted maintained schema, or exploration before the API is known? Then MCP, with tool search on, read-only first, writes behind approval. Prefer vendor-hosted official servers; treat community servers as untrusted code.
  4. Is the operation a repeatable pipeline step? Convert it to a script/library call or a recorded Playwright test even if discovered through MCP (determinism, testability, no schema tokens, key never in context).
  5. Does the API lack the operation (views, Workflow canvas, Clay table creation, OAuth consent clicks)? Then the browser, narrowly: Playwright CLI, record once then replay, with the PreToolUse guard from the registry.
- Criteria weights for John's stated order (outcome, effort, cost): auth model and write coverage decide feasibility; maintenance and vendor support decide durability; determinism/testability decides whether the engineer can verify its own work; secrets exposure decides which route may hold which credential; token cost comes last because tool search and code execution reduce it.
- Code-execution/Code Mode is an optimisation for many-tool, multi-step MCP use, not a starting point; Claude Code's Bash tool already is a code executor, so "write a script that calls the API" is the cheap local version of the same idea (my inference from the Anthropic and Cloudflare posts).

### Gaps
- Fern (https://buildwithfern.com/post/sdk-vs-cli-vs-mcp-choosing-interface), Numlytics (https://numlytics.com/blog/mcp-vs-cli-vs-api-decision-framework/) and Seongok Ryu (https://seongokryu.github.io/posts/agent-tool-interface-landscape/): seen only in Exa highlights; WebFetch on Fern returned a truncated placeholder. Their numbers (35x, 4-32x, 44,026 vs 1,365 tokens) are not cited.
- No test of the real token cost of Attio/Clay/n8n MCP servers in Claude Code with tool search on; spike item.
- MCP spec text (auth, 2026-07-28 revision) was not read.

## Discovery envelope and stop rules

### Takeaway
Recommend a discovery pass of one capability = one lead decision, at most 3 researcher workers (one per candidate cluster: connector/MCP, library/script, browser/other), at most 3 candidate URLs per cluster, about 15 tool calls per worker, 10 minutes wall-clock and 40 lead turns, no gap round; stop at the first candidate that passes the gate with evidence. The research skill's current tiers (1 / 2-4 / 5 / cap 8 workers) are for research runs, too big for mid-build. Evidence supports a small cap: returns plateau after about three searches and useful evidence appears early. Confidence: medium (numbers are my design, the plateau evidence is from QA benchmarks, not tool discovery).

### Cited findings
- Anthropic's effort scaling: simple 1 agent 3-10 calls; comparisons 2-4 subagents with 10-15 calls each — https://www.anthropic.com/engineering/multi-agent-research-system, opened 2026-10-16, WebFetch — Quote: "direct comparisons might need 2-4 subagents with 10-15 calls each"
- Same post: simple fact-finding — https://www.anthropic.com/engineering/multi-agent-research-system, opened 2026-10-16, WebFetch — Quote: "Simple fact-finding requires just 1 agent with 3-10 tool calls"
- Same post: cost of multi-agent — https://www.anthropic.com/engineering/multi-agent-research-system, opened 2026-10-16, WebFetch — Quote: "multi-agent systems use about 15× more tokens than chats"
- Same post: start broad then narrow — https://www.anthropic.com/engineering/multi-agent-research-system, opened 2026-10-16, WebFetch — Quote: "start with short, broad queries, evaluate what's available, then progressively narrow focus."
- Search depth plateau in a controlled budgeted-search study (QA benchmarks, six LLMs) — https://arxiv.org/html/2603.08877v1, opened 2026-10-16, WebFetch — Quote: "Increasing search steps yields consistent gains up to roughly three searches, after which returns plateau."
- Search effort weakly tracks answer quality; stop on evidence sufficiency — https://arxiv.org/abs/2608.01913, opened 2026-10-16, WebFetch — Quote: "Across settings, we find that search effort and answer quality are only weakly aligned."
- Same paper, stop criteria — https://arxiv.org/abs/2608.01913, opened 2026-10-16, WebFetch — Quote: "stopping criteria based on whether sufficient supporting evidence has been retrieved."
- Research skill effort table and caps (what the build-time envelope must be smaller than) — /home/user/Autonomy-Research/plugin/skills/research/SKILL.md:36-42, read 2026-10-16, Read — Quote: "| Hard cap | 8 | - | Never more than 8 workers in a run, gap round included. |"
- Research skill: single gap round, worker cuts to three URLs — /home/user/Autonomy-Research/plugin/skills/research/SKILL.md:221-225, read 2026-10-16, Read — Quote: "When a search returns more than three candidate URLs, the worker shall select at most three before any fetch."
- Tool-scan: at most 8 workers, one per cluster, six steps per candidate — /home/user/Autonomy-Research/plugin/skills/tool-scan/SKILL.md:13-15, read 2026-10-16, Read — Quote: "one per candidate cluster, at most 8"
- Spike worker caps (turns and calls) — Autonomy-Research/feasibility finding citing plugin/agents/spike-worker.md:6,79, read via /home/user/Autonomy-Research/research/findings/engineer-feasibility.md:262, 2026-10-16, Read — Quote: "caps are "maxTurns: 40" and "Stop at about 15 tool calls.""
- Claude Code caps for unattended runs exist (`--max-turns`, `--max-budget-usd`) — /home/user/Autonomy-Research/research/tool-registry.md:181, read 2026-10-16, Read — Quote: "Per-run turn and estimated-spend caps; `error_max_turns` / `error_max_budget_usd` result subtypes; default none"

### Contradictions
- Anthropic's post ties quality to spending more tokens ("token usage by itself explains 80% of the variance", same URL as above) while the 2026 search-agent studies say effort and quality are weakly aligned and returns plateau. Reconcile: Anthropic measured on open-ended breadth research (BrowseComp-like); the build-time question is narrow (does a tool exist that does X), so the plateau applies. Not tested on tool discovery.

### Inferences
- Proposed envelope (my design, to be spiked on 3 real capabilities):
  - Tier D0 (default, lookup): 0 workers. Lead greps `dead-ends.md`, registry, and checks the vendor's own docs page plus the official MCP registry: at most 2 content calls. Covers "does Attio have an API for views".
  - Tier D1 (one capability, no known candidate): 1 worker, at most 15 tool calls, at most 3 candidate URLs, return one recommendation and a `ROW:`.
  - Tier D2 (real choice, e.g. MCP vs script vs browser for a core integration): 2-3 workers, one per path, same caps; exceeding 3 requires John.
  - Time box: 10 minutes per pass, 25 minutes absolute including vetting; turn box 40 for the lead's discovery; if the box ends with no passing candidate, write a `dead-ends.md` entry with `inconclusive`, carry on with the browser or a manual step, and flag to John. No gap round in build mode.
  - Stop rules, "good enough": stop when one candidate (a) does every operation the task card lists, (b) has an official source or a repo with recent commits and a licence, (c) shows auth John can complete, (d) has one cited example of the needed write. Also stop when two consecutive searches add no new candidate (evidence: plateau after about three).
  - Depth escalation only on a named blocker (auth wall, missing write); never to "find a better one".
- Compared with the research agent: its tiers are sized for knowledge questions (5 workers for a landscape, 8 cap). For a build the same shapes map to D0 (one fact), D1 (one focused question) and D2 (comparison), so the change is to cap at D2 and add a time box, not a new tier set.

### Gaps
- No vendor guidance exists for discovery-inside-a-build specifically; the numbers above are untested design values.
- Deep-research evaluations (DeepResearch Bench etc.) were not read for effort scaling beyond the two arXiv studies.

## Skill-to-phase mapping and required changes

### Takeaway
Map: interview serves intake (and an "I don't know" branch that calls research); system-map and research serve as-is mapping; tool-scan plus repo-triage serve feasibility and build-time discovery; spike serves feasibility and build-time trials; research (focused tiers) serves audit and re-checks. None fits as shipped: all assume user-triggered runs, no time box, outputs in `research/`, and (spike) no credentials. Skill files must not be edited here; the change list below is for the build run. Confidence: high on today's contents (files read), medium on the changes.

### Cited findings
- Interview needs no workers and fetches nothing — /home/user/Autonomy-Research/plugin/skills/interview/SKILL.md:8-11, read 2026-10-16, Read — Quote: "The interview is conversation with the user; it needs no workers and fetches no pages."
- Interview: reconnaissance is opt-in only — /home/user/Autonomy-Research/plugin/skills/interview/SKILL.md:47-48, read 2026-10-16, Read — Quote: "Offer repo or web reconnaissance as an option; do not start it unasked."
- Interview output path is research/requirements, not the engineer's repo — /home/user/Autonomy-Research/plugin/skills/interview/SKILL.md:12-14, read 2026-10-16, Read — Quote: "tell the user the output path `research/requirements/<slug>.md`."
- Tool-scan never installs or runs — /home/user/Autonomy-Research/plugin/skills/tool-scan/SKILL.md:21-23, read 2026-10-16, Read — Quote: "The scan shall never install, build or run a candidate or any script from it."
- Tool-scan logs only to the registry; the lead writes rows after all workers return — /home/user/Autonomy-Research/plugin/skills/tool-scan/SKILL.md:16-19, read 2026-10-16, Read — Quote: "the lead shall write the registry rows, one at a time, from those `ROW:` lines."
- Spike tests only named paths — /home/user/Autonomy-Research/plugin/skills/spike/SKILL.md:14-15, read 2026-10-16, Read — Quote: "The skill shall test only paths the user named, and shall not add a path of its own."
- Spike gives no credentials — /home/user/Autonomy-Research/plugin/skills/spike/SKILL.md:27-29, read 2026-10-16, Read — Quote: "The skill shall give a worker no credentials beyond read-only search keys."
- Spike confirms with the user and writes to research/spikes — /home/user/Autonomy-Research/plugin/skills/spike/SKILL.md:52-53,64, read 2026-10-16, Read — Quote: "Confirm the question, the named paths (one to three) and the probe with the user in one message."
- Research lead never reads sources itself — /home/user/Autonomy-Research/plugin/skills/research/SKILL.md:26-27, read 2026-10-16, Read — Quote: "never fetch, search or read a source yourself;"
- Earlier-run spike gaps (13 numbered gaps) — /home/user/Autonomy-Research/research/findings/engineer-feasibility.md:245-270, read 2026-10-16, Read — Quote: "Path cap and source: make the cap configurable and use a pre-authorised path list written at intake."
- Earlier-run interview gaps (7 inferences) — /home/user/Autonomy-Research/research/findings/engineer-intake.md:65-72, read 2026-10-16, Read — Quote: "an explicit "I don't know" path that triggers exploration instead of recording a gap"
- Dead-end lookup requirement — /home/user/Autonomy-Research/research/findings/engineer-feasibility.md:598, read 2026-10-16, Read — Quote: "When a candidate path matches a `dead-ends.md` entry, the engineer shall state the prior result and shall not dispatch a trial unless the entry's `retry-when` condition holds."

### Contradictions
- Spike-worker forbids retries ("do not retry with changed flags"), the Claude Code best-practices page and the context protocol allow two attempts; earlier run reconciled by mode (feasibility spike: no retry; build trial: two attempts). Source: /home/user/Autonomy-Research/research/findings/engineer-feasibility.md:Q9 Contradictions.

### Inferences
- Mapping table (mine):

| Engineer phase | Skill(s) | Mode |
| --- | --- | --- |
| Intake | interview, then research D0/D1 for options John cannot name | interactive; recon only when John says "I don't know" |
| As-is mapping | system-map (read-only), research D1 for each unfamiliar system's API surface | no installs |
| Feasibility | tool-scan + repo-triage (D2), then spike (trial mode) for the 1-3 surviving paths | writes dead-ends.md, integration cards |
| Build | tool-scan D0/D1 on demand; spike trial for a blocker; research one-fact for docs | box and gates, no user confirmation per call |
| Audit | research D1 (re-verify vendor claims, licences, versions), repo-triage on what was installed | reads only |

- Changes needed, collected (earlier gaps marked E-spike n / E-int n; new ones marked NEW):
  - Spike: E-spike 1-13 as listed in engineer-feasibility Q9 (configurable path cap and pre-authorised list; credential manifest; network boundary; real isolation; wall-clock, USD and progress rule; bounded retries in trial mode; relaxed installs in a container; JSON result record; supervisor teardown; unattended authorisation record; output location; `claude -p` auth; resource limits), plus dead-end lookup, riskiest-first ordering and `inconclusive` at box end.
  - Interview: E-int 1-7 (landscape-first explore branch; option-based questions; "I don't know" triggers exploration; plan-approval checkpoint; verification pass on candidates offered; budget; unknown-unknowns probe), plus spec-kit-style gap closing and a file-based approval record.
  - NEW, research skill: a build-mode switch with tiers D0-D2, a 10-minute box, no gap round, worker cap 3; lead may do D0 inline (it already allows two content calls); outputs go to the engineer repo, not `research/findings/`; skip synthesizer and verifier for D0/D1 and run a cheap verify (open the primary URL, quote) instead.
  - NEW, tool-scan: a mode that stops at the first passing candidate rather than judging all; add a "capability card" input (operations needed, auth John can do, writes required); add the decision-procedure result (script/MCP/browser) to the row; read dead-ends.md first; at most 3 candidates per cluster already exists.
  - NEW, all skills: output paths configurable via a project file (`docs/` in the engineer repo); a registry `Verified` date plus `re-check after` field; dispatch brief shows Today and the box.
  - NEW, engineer-side: PreToolUse/SessionStart reminder to grep dead-ends and registry before choosing a tool (spike item in engineer-feasibility).

### Gaps
- Agent files (researcher.md, spike-worker.md) were not re-read in this run; their facts come from the feasibility finding.
- repo-triage and system-map skill files not read in detail; the mapping assumes their descriptions.

## Flow from discovery result to card, registry row and plan entry

### Takeaway
A worker's single return should carry three typed blocks that the lead copies without re-research: a `ROW:` line (registry), a capability/integration card patch (operations covered, auth, scopes, rate limit, write coverage, evidence URL and quote, version, `re-check after`), and a plan entry (chosen route from the decision procedure, setup steps for John, test that proves it, fallback). Negative results go to `dead-ends.md` with `retry-when`. Confidence: medium (design from existing formats; untested).

### Cited findings
- Registry row format workers return — /home/user/Autonomy-Research/plugin/skills/tool-scan/SKILL.md:44-46, read 2026-10-16, Read — Quote: "`ROW: | <Tool> | <Link> | <What it does, incl. install surface> | <Where it runs> | <Verified YYYY-MM-DD> | <Verdict> |`"
- Dead-ends record proposal — /home/user/Autonomy-Research/research/findings/engineer-feasibility.md:109, read 2026-10-16, Read — Quote: "path, date, version or commit tested, probe, result, evidence location (command and output), `retry-when` condition"
- Integration cards come from a 12-point checklist and feed the setup list — /home/user/Autonomy-Research/research/findings/engineer-feasibility.md:301, read 2026-10-16, Read — Quote: "One ordered page from the integration cards, long waits first"
- Note schema already forces claim + URL + quote, so a card can copy a finding verbatim — /home/user/Autonomy-Research/plugin/skills/research/note-schema.md:14-16, read 2026-10-16, Read — Quote: "The claim says no more than the quote does."

### Contradictions
- None found.

### Inferences
- Flow (mine): worker note -> three blocks -> lead writes: (1) registry row, one at a time; (2) card fields appended to `docs/integrations/<service>.md` (the 12 checklist points; unknown fields stay `unknown`, not guessed); (3) plan entry as a task with acceptance test and John-step list; (4) if no pass, `dead-ends.md`. The lead never opens the note, same as today. The cheap re-check rule: reuse a registry row if `Verified` is under 90 days old and the version matches; otherwise run D0 on the single changed fact (my number, unvalidated).
- Idempotency: key rows by tool name plus link so a repeat discovery updates the row rather than adding one.

### Gaps
- The card template file does not exist in the repo yet (only the checklist in engineer-feasibility Q7); its final field list needs the feasibility facet.
- Where the engineer's `docs/integrations/` lives is a plan decision, not researched.

## Recommendation, alternatives, rejected, spikes (facet close)
- Recommendation: adopt the five-step decision procedure, the D0-D2 envelope (max 3 workers, 15 calls each, 10-minute box, stop at first passing candidate), and the skill change list; keep skill files unedited until the build run.
- Alternatives: always-MCP (simple, but writes and determinism weaker); always-script (cheapest, but fails where OAuth or no API); full research-skill tiers at build time (more thorough, stalls the build); Cloudflare-style Code Mode gateway (large tool surface only, extra infrastructure).
- Rejected: pick a transport once for the whole engineer (evidence says per-integration); use 4-35x token multipliers as a decision driver (unreproducible, config-dependent); unbounded gap rounds at build time.
- Spike first: (1) measure `/context` cost of the Attio, Clay and n8n MCP servers with tool search on and off; (2) run D1 on three real capabilities to calibrate 15 calls / 10 minutes; (3) check the hook that greps dead-ends and registry; (4) one writing round-trip through MCP with approval in an unattended session (the docs say prompts must reach a person).

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Cloudflare Code Mode | https://blog.cloudflare.com/code-mode/ | Converts MCP tools to a TypeScript API; agent gets one code-execution tool in a sandbox with keys held by bindings | Cloudflare Workers sandbox (pattern) | 2026-10-16 | Reference design only; the idea is to prefer scripts over many tool calls; do not adopt a gateway for one user |
| Anthropic code execution with MCP | https://www.anthropic.com/engineering/code-execution-with-mcp | Agent writes code against MCP servers presented as files; 150k to 2k tokens quoted | Claude Code with a code runtime | 2026-10-16 | Reference design; Bash already provides the runtime |
| Claude Code MCP tool search | https://code.claude.com/docs/en/mcp | Defers MCP tool definitions; `ENABLE_TOOL_SEARCH` auto/auto:N/false; description limits | Claude Code | 2026-10-16 | Use (default on); check it is off behind non-first-party proxies |
| Anthropic multi-agent research system post | https://www.anthropic.com/engineering/multi-agent-research-system | Effort-scaling rules, 15x tokens | blog | 2026-10-16 | Evidence for envelope tiers |
| Budget-Constrained Agentic Search (BCAS) | https://arxiv.org/html/2603.08877v1 | Measures accuracy vs search depth; plateau near three searches | paper | 2026-10-16 | Evidence only |
| Diagnosing long-horizon search agents | https://arxiv.org/abs/2608.01913 | Effort and quality weakly aligned; stop on evidence sufficiency | paper | 2026-10-16 | Evidence only |
| Scaffolding vs interface MCP/CLI study | https://arxiv.org/abs/2608.08654 | Paired MCP-vs-CLI cost study; scaffolding dominates | paper | 2026-10-16 | Evidence; preprint, treat with care |
| Skills explained (Anthropic) | https://claude.com/blog/skills-explained | Skills vs MCP vs subagents guidance | blog | 2026-10-16 | Evidence for connector-plus-skill pairing |
