# Mapping a codebase for an agent

Brief: Which tools and methods give an LLM agent a reliable map of an existing codebase before it changes anything, their limits, and how subagents do the mapping so the lead never holds the files.
Run: research/runs/engineer-existing-systems/PLAN.md

Recommendation (one): map with Claude Code's own read-only subagents (one per module, ripgrep/Glob/Read), seeded by deterministic dependency-graph output (pydeps, dependency-cruiser/madge, optionally SCIP indexes) produced by a script, each subagent writing a fixed-schema note to disk and returning a short reference. Do not auto-generate a CLAUDE.md overview. Alternatives and rejects are in "Tools evaluated" and in the last section. Spikes needed are listed at the end.

## Q1 Which tools produce codebase maps, what do they output, and what are the limits?

### Takeaway
No single tool gives a trustworthy whole-system map. Aider's repo map (tree-sitter definitions ranked by a file-dependency graph) is a token-budgeted signature index (default 1k tokens). SCIP indexers, madge, dependency-cruiser and pydeps give exact symbol or import graphs for Python and TypeScript. CodeQL gives a queryable AST/data-flow database without a build for Python and JS/TS. Semgrep matches syntax patterns. DeepWiki gives a generated wiki with a 30-page cap. Confidence: medium (docs opened; no hands-on accuracy tests, nothing run).

### Cited findings
- Aider repo map lists files with key symbols and signatures, ranks them with a graph algorithm over file dependencies, and fits a token budget — https://aider.chat/docs/repomap.html, opened 2026-10-16, Parallel fetch — Quote: "The token budget is influenced by the `--map-tokens` switch, which defaults to 1k tokens."
- Aider map can grow when no files are in chat, and shows only the most-referenced identifiers, so it is not complete — https://aider.chat/docs/repomap.html, opened 2026-10-16, Parallel fetch — Quote: "It only includes the most important identifiers, the ones which are most often referenced by other portions of the code."
- Aider replaced ctags with tree-sitter because the map is richer, covers many languages by pip package, and needs no external install — https://aider.chat/2023/10/22/repomap.html (2023, older), opened 2026-10-16, Parallel fetch — Quote: "The map is richer, showing full function call signatures and other details straight from the source files."
- Sourcegraph precise navigation uses SCIP indexes generated per language; scip-python and scip-typescript are generally available — https://docs.sourcegraph.com/code_intelligence/explanations/precise_code_intelligence, opened 2026-10-16, Parallel search excerpt, page body — Quote: "Precise Code Navigation requires language-specific indexes to be generated and uploaded to your Sourcegraph instance."
- Without an index Sourcegraph falls back to heuristics with no semantic information — https://sourcegraph.com/docs/code-navigation, opened 2026-10-16, Parallel search excerpt, page body — Quote: "It uses a mix of text search and syntax-level heuristics (no language-level semantic information)"
- scip-typescript needs the project installed and a tsconfig.json for TS (npm install, then index) — https://github.com/kernoio/scip-typescript (a fork listing; upstream is sourcegraph's), opened 2026-10-16, Parallel search excerpt — Quote: "Navigate to the project root, containing tsconfig.json ."
- CodeQL can create Python and JS/TS databases without building — https://docs.github.com/en/code-security/reference/code-scanning/codeql/codeql-cli-manual/database-create, opened 2026-10-16, Parallel fetch — Quote: "`none`: The database will be created without building the source root. Available for C#, Java, JavaScript/TypeScript, Python, and Ruby."
- CodeQL database holds AST, data-flow graph and control-flow graph for one language at one point in time — https://codeql.github.com/docs/codeql-overview/about-codeql/, opened 2026-10-16, Parallel search excerpt, page body — Quote: "CodeQL databases contain queryable data extracted from a codebase, for a single language at a particular point in time."
- Semgrep matches syntax patterns with ellipsis and metavariables (for example finding every call to a function, or `requests.get(..., verify=False, ...)`) — https://semgrep.dev/docs/writing-rules/pattern-syntax, opened 2026-10-16, Exa fetch — Quote: "The `...` ellipsis operator abstracts away a sequence of zero or more items such as arguments, statements, parameters, fields, characters."
- madge (JS/TS) outputs module dependency graphs in DOT and finds circular dependencies; resolves TS aliases through tsConfig — https://github.com/pahen/madge, opened 2026-10-16, Parallel search excerpt, page body — Quote: "Madge is a developer tool for generating a visual graph of your module dependencies, finding circular dependencies, and giving you other useful info."
- dependency-cruiser (MIT) validates dependencies against rules and emits dot/text/html — https://github.com/sverweij/dependency-cruiser, opened 2026-10-16, Parallel search excerpt, page body — Quote: "Validate and visualise dependencies. With your rules. JavaScript. TypeScript. CoffeeScript. ES6, CommonJS, AMD."
- pydeps (Python) lists a package's external dependencies as JSON and draws import graphs, flagging cycles; needs Graphviz for images — https://pythonhosted.org/pydeps/index.html, opened 2026-10-16, Parallel search excerpt, page body — Quote: "pydeps -- externals mypackage which will print a json formatted list of module names to the screen"
- DeepWiki wiki generation defaults to free low effort, and large repos can hit built-in limits; configurable page cap 30 — https://docs.devin.ai/work-with-devin/deepwiki, opened 2026-10-16, Parallel fetch — Quote: "especially important for large repositories that may hit built-in limits."
- DeepWiki limits: "Maximum 30 pages (80 for enterprise)" — same URL, same fetch — Quote: "Maximum 30 pages (80 for enterprise)"
- Public DeepWiki and its MCP are the basic tier — same URL — Quote: "Public DeepWiki and the DeepWiki MCP provide basic documentation and Q&A capabilities."
- Anthropic says Claude Code deliberately skips pre-built indexes: grep/glob retrieve just in time — https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents (dated 2026-01-06 by the fetch), opened 2026-10-16, Parallel fetch — Quote: "primitives like glob and grep allow it to navigate its environment and retrieve files just-in-time, effectively bypassing the issues of stale indexing and complex syntax trees."
- Benchmark evidence on accuracy: agentic exploration beats BM25/TF-IDF/dense retrieval, but line-level recall is low — https://arxiv.org/pdf/2606.07297 (SWE-Explore, June 2026), opened 2026-10-16, Parallel fetch — Quote: "current agents are strong at finding relevant files but remain recall-limited at the line level"
- SWE-Explore: classical retrievers close to random — same URL — Quote: "Sparse retrievers (BM25, TF–IDF) and the lightweight dense retriever remain close to Random on most metrics"
- SWE-Explore benchmark is 64.5% Python and 3.2% TypeScript, so TS evidence is thin — same URL, Table 7 — Quote: "Python 547 64.5 Go 84 9.9 JavaScript 51 6.0"
- SWE-QA-Pro (ACL Findings, July 2026): agents beat direct answering on long-tail repos — https://aclanthology.org/2026.findings-acl.837, opened 2026-10-16, Parallel search excerpt, page body — Quote: "agentic workflows significantly outperform direct answering (e.g., a ~13-point gap for Claude Sonnet 4.5)"

### Contradictions
- Anthropic describes grep/glob exploration as bypassing indexes — https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents; Aider (and Sourcegraph) build pre-computed indexes/maps to help the agent — https://aider.chat/docs/repomap.html. Not a hard conflict (Anthropic's text also names a hybrid), but no source compares them head-to-head on one repo; a spike would settle it.

### Inferences
- (mine) A precomputed map is best used as a seed that tells subagents where to look, and the facts it holds (import edges, symbol locations) should come from deterministic tools, not from an LLM reading files. Rests on the Aider, SCIP, madge/pydeps findings and the DocAgent use of an AST dependency DAG (see Q3).
- (mine) CodeQL and Semgrep answer targeted questions (who calls X, where are secrets/HTTP calls) well; they are not map generators. Rests on the CodeQL and Semgrep pages.

### Gaps
- Tree-sitter official docs and universal-ctags limits (accuracy, dynamic languages) not opened beyond one ctags man-page excerpt (no usable limit); ctags is only cited indirectly via Aider's reason for dropping it.
- No documented hard repo-size limit found for Sourcegraph SCIP indexing, CodeQL database size, or DeepWiki indexing beyond the 30-page cap; DeepWiki MCP not connected, so DeepWiki not tested.
- Parallel fetch of the CodeQL docs host docs.codeql.github.com failed (connect_error); codeql.github.com pages were used instead.
- No accuracy figures for pydeps/madge/dependency-cruiser on dynamic imports (Python importlib, TS path aliases); known blind spot, no source opened.

## Q2 What do Anthropic, Aider and others document about exploring a repo, and the context cost?

### Takeaway
Anthropic: context is the constraint; explore just in time with grep/glob/Read, scope investigations, and push research into subagents that return summaries. A 2026 study found auto-generated context files (including codebase overviews) slightly reduce success and raise cost over 20%, so the map should live in files read on demand, not in CLAUDE.md. Confidence: high for the practice, low for a numeric cost of mapping a mid-size repo (no source gives one).

### Cited findings
- Core constraint — https://code.claude.com/docs/en/best-practices (dated 2026-10-06 by fetch), opened 2026-10-16, Parallel fetch — Quote: "The infinite exploration. You ask Claude to “investigate” something without scoping it. Claude reads hundreds of files, filling the context."
- Delegate research — same page — Quote: "Delegate research with `"use subagents to investigate X"` . They explore in a separate context, keeping your main conversation clean for implementation."
- Just-in-time loading and progressive disclosure — https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents, opened 2026-10-16, Parallel fetch — Quote: "Rather than pre-processing all relevant data up front, agents built with the “just in time” approach maintain lightweight identifiers (file paths, stored queries, web links, etc.)"
- Smallest high-signal set — same page — Quote: "good context engineering means finding the smallest possible set of high-signal tokens that maximize the likelihood of some desired outcome."
- Subagent return size — same page — Quote: "Each subagent might explore extensively, using tens of thousands of tokens or more, but returns only a condensed, distilled summary of its work (often 1,000-2,000 tokens)."
- Built-in Explore agent is read-only, thoroughness settable, and can run on Haiku via an override — https://code.claude.com/docs/en/sub-agents, opened 2026-10-16, Parallel fetch — Quote: "A fast, read-only agent optimized for searching and analyzing codebases."
- Explore model override — same page — Quote: "define one with `model: haiku` to run exploration on a lower-cost model."
- Aider: map is sent with each request, and the LLM asks for files it needs — https://aider.chat/docs/repomap.html, opened 2026-10-16 — Quote: "If it needs to see more code, the LLM can use the map to figure out which files it needs to look at."
- Auto-generated context files hurt slightly and cost more — https://arxiv.org/pdf/2602.11988.pdf (Feb 2026, ETH Zurich), opened 2026-10-16, Parallel fetch — Quote: "context files tend to reduce task success rates compared to providing no repository context, while also increasing inference cost by over 20%."
- Overviews in particular do not help — same paper — Quote: "context files, even developer-provided ones, are not effective at providing a repository overview."
- They help only where documentation is missing — same paper — Quote: "LLM-generated context files not only consistently improve performance by 2.7% on average, but also outperform developer-written documentation."
- Cost of exploration is large: direct main-agent runs averaged hundreds of thousands of tokens per task — https://arxiv.org/html/2606.14066v1 (FastContext, Aug 2026), opened 2026-10-16, Parallel fetch — Quote: "| Direct main | 457k / task | $282.47 |"

### Contradictions
- Claude Code's own /init-style guidance advocates context files with overview; the Feb 2026 paper reports they do not help as overviews — https://arxiv.org/pdf/2602.11988.pdf (the paper notes the Claude Code prompt "advocates for a high-level overview only and warns against listing components that are easily discoverable"). Partial: the paper's effect sizes are small (-3% / +4%) and cover SWE-bench-style bug tasks, not a pre-change audit.

### Inferences
- (mine) A mid-size repo map cost is not published. FastContext's 457k tokens per task (GPT-5.4, SWE-bench Multilingual, whole solve not just exploration) and Anthropic's 1,000-2,000 token subagent returns suggest budgeting mapping in hundreds of thousands of subagent tokens and 1-2k tokens per module back to the lead. Treat as an estimate to measure in a spike.
- (mine) Keep the map out of CLAUDE.md and load it by path on demand; this fits both Anthropic's just-in-time stance and the 2602.11988 result.

### Gaps
- No published token cost for mapping a mid-size repo end to end; no Anthropic number for Explore agent tokens.
- Whether the 2602.11988 result transfers to a pre-change audit (rather than issue fixing) is untested.

## Q3 How are subagent splits done and merged without the lead reading files; accuracy versus one long context?

### Takeaway
The documented pattern is orchestrator-worker: subagents with their own windows, each with objective, output format, tool guidance and boundaries, writing artifacts to disk and returning light references. Evidence for accuracy gain in coding is modest: an exploration subagent gave up to +5.5 points and up to 60% fewer main-agent tokens; Anthropic itself warns coding is less parallelisable than research and multi-agent costs about 15x chat tokens. Confidence: medium.

### Cited findings
- Multi-agent outperformed single-agent on research evals (not coding) — https://www.anthropic.com/engineering/multi-agent-research-system, opened 2026-10-16, Parallel fetch — Quote: "a multi-agent system with Claude Opus 4 as the lead agent and Claude Sonnet 4 subagents outperformed single-agent Claude Opus 4 by 90.2% on our internal research eval."
- Cost — same page — Quote: "agents typically use about 4× more tokens than chat interactions, and multi-agent systems use about 15× more tokens than chats."
- Coding caveat — same page — Quote: "most coding tasks involve fewer truly parallelizable tasks than research, and LLM agents are not yet great at coordinating and delegating to other agents in real time."
- Delegation brief contents — same page — Quote: "Each subagent needs an objective, an output format, guidance on the tools and sources to use, and clear task boundaries."
- Write to filesystem, pass references — same page (appendix) — Quote: "Subagents call tools to store their work in external systems, then pass lightweight references back to the coordinator."
- Effort scaling rule — same page — Quote: "Simple fact-finding requires just 1 agent with 3-10 tool calls, direct comparisons might need 2-4 subagents with 10-15 calls each"
- Claude Code warns returns add up — https://code.claude.com/docs/en/sub-agents, opened 2026-10-16 — Quote: "Running many subagents that each return detailed results can consume significant context, and each subagent spends tokens of its own while it runs."
- Subagents start empty — same page — Quote: "Each subagent starts with a fresh, isolated context window. It doesn't see your conversation history, the skills you've already invoked, or the files Claude has already read."
- Exploration subagent accuracy and cost, with read/glob/grep only — https://arxiv.org/html/2606.14066v1, opened 2026-10-16, Parallel fetch — Quote: "our exploration subagents improve resolution accuracy up to 5.5% while reducing main model token consumption up to 60%."
- Cost audit: explorer overhead small — same page — Quote: "the explorer accounting for only 2.1% of that total and the system still saving $69.03 overall on this run."
- Explorer tools — same page — Quote: "The subagent deliberately exposes only three language-agnostic tools: Read for line-numbered file contents, Glob for path discovery, and Grep"
- Dependency-ordered documentation: DocAgent builds an AST dependency DAG, processes in topological order with Reader/Searcher/Writer/Verifier agents, and ablation confirms the order matters — https://aclanthology.org/2025.acl-demo.44.pdf (ACL 2025 demo), opened 2026-10-16, Exa fetch — Quote: "Our ablation study confirms the vital role of the topological processing order."
- General coding agents (Claude Code among them) converge on similar exploration behaviour — https://arxiv.org/pdf/2606.07297, opened 2026-10-16 — Quote: "high file hit, high early ranking, compact context, and low line recall."
- Aggregation across many sources is a known weakness — https://arxiv.org/pdf/2601.03731 (RepoReason, Jan 2026), opened only as search excerpt (page body not fetched) — see Gaps.

### Contradictions
- Anthropic: multi-agent beat single agent by 90.2% (research task) — https://www.anthropic.com/engineering/multi-agent-research-system; same page says coding has fewer parallelisable tasks. FastContext shows a small coding gain (+0.0 to +5.5 points, varying by model) — https://arxiv.org/html/2606.14066v1. The gains do not carry over in size from research to code; no source measures per-module subagent mapping versus one long context directly.

### Inferences
- (mine) For a read-only map, parallel per-module subagents are appropriate (breadth-first, independent, exceeds one window), and the lead should only receive file paths plus a 5-10 line status. This matches Anthropic's "pass lightweight references" and CLAUDE.md's lead rule.
- (mine) Order matters: run the script-produced dependency graph first, split modules along it (leaf modules first, as DocAgent does), then have an integration subagent read only the module notes and write the system-level map. A verifier subagent should spot-check claims against files (DocAgent has a Verifier role).
- (mine) Reported accuracy of an LLM-written map cannot be inferred from these sources; it needs a spike (see below).

### Gaps
- No published head-to-head: per-module subagent mapping versus single-long-context mapping of the same repo.
- RepoReason (arxiv 2601.03731) seen as search excerpt only; its "aggregation deficit" claim is not cited.

## Q4 How does an agent find why something breaks; what observability is cheap to attach?

### Takeaway
Claude Code best practices say to hand the agent evidence it can run: logs through `claude -p` pipes, test output via subagent, reproduction commands. For attaching observability, OpenTelemetry covers both sides: Claude Code can export its own traces, and an app can use OTel instrumentation. I found no 2025-2026 source that tests agents diagnosing production breakage from run histories, so this answer is thin. Confidence: low-medium.

### Cited findings
- Delegate log and test output handling — https://code.claude.com/docs/en/sub-agents, opened 2026-10-16 — Quote: "Running tests, fetching documentation, or processing log files can consume significant context."
- Pattern for failures — same page — Quote: "Use a subagent to run the test suite and report only the failing tests with their error messages"
- Pipe logs into a one-off non-interactive call — https://code.claude.com/docs/en/best-practices, opened 2026-10-16 — Quote: "claude -p "Analyze this log file" --output-format stream-json --verbose"
- Claude Code exports its own telemetry (OpenTelemetry), including subagent spans nested under the parent — https://code.claude.com/docs/en/monitoring-usage, opened 2026-10-16, Parallel search excerpt, page body — Quote: "When the Agent tool, or legacy Task tool, spawns a subagent, the subagent's API and tool spans nest under the parent's claude_code.tool span."
- Instrumented apps run via Bash do not inherit that exporter — same page — Quote: "An OpenTelemetry-instrumented application that you run through the Bash tool doesn't inherit Claude Code's exporter endpoint or headers"
- Repo settings cannot enable telemetry — same page — Quote: "Claude Code ignores the OpenTelemetry exporter variables in a repository's .claude/settings.json and .claude/settings.local.json"
- Debug log for Claude Code itself — same page — Quote: "start Claude Code with claude --debug-file <path> and check the log it writes to that path."
- Agent SDK exports the same data — https://code.claude.com/docs/en/agent-sdk/observability, opened 2026-10-16, Parallel search excerpt, page body — Quote: "Tracing is in beta. Span names and attributes may change between releases."
- Verification is the lever — https://code.claude.com/docs/en/best-practices — Quote: "If you can’t verify it, don’t ship it."

### Contradictions
- None found.

### Inferences
- (mine) Cheap attach order for John's own systems: (1) read existing logs and run histories (n8n/Vercel/Supabase/CI) via a subagent that returns error-pattern counts; (2) reproduce locally with a failing test or script; (3) only then add OTel auto-instrumentation to the app and a self-hosted collector. The Claude Code OTel documents describe observing the agent, not the app; the app needs its own OTel SDK. Step (3) is not backed by an opened source; "zero-code Python auto-instrumentation" appeared only in a search query I did not open.
- (mine) Recording known breakages into the map as "symptom, evidence path, first-seen, reproduction command" fits the evidence-first guidance.

### Gaps
- No opened source on OpenTelemetry Python/Node auto-instrumentation, Sentry self-hosting, or on agents diagnosing failures from run histories. Left open.
- No evidence found for error-pattern clustering by agents with measured accuracy.

## Q5 What should the code part of an as-is map contain?

### Takeaway
No source defines this list; the checklist below is my synthesis from the tools' outputs and the DocAgent/SWE-Explore/context-file findings. Confidence: low as sourced fact, medium as design.

### Cited findings
- Maps should cite file paths and line ranges because line-level evidence is what exploration misses — https://arxiv.org/pdf/2606.07297, opened 2026-10-16 — Quote: "missing core evidence hurts more than moderate redundant context."
- FastContext's explorers return file paths with line ranges — https://arxiv.org/html/2606.14066v1, opened 2026-10-16 — Quote: "receives one concise response containing file paths, line ranges, and short relevance notes."
- Context files should hold minimal, non-discoverable facts — https://arxiv.org/pdf/2602.11988.pdf, opened 2026-10-16 — Quote: "human-written context files should describe only minimal requirements."
- Dependency edges from import graphs: pydeps lists external dependencies — see Q1 pydeps quote (same URL).

### Contradictions
- None found.

### Inferences
- (mine) Per-module note schema, every fact with `path:line`: purpose in one line; public entry points (CLI, routes, handlers, cron/workflow triggers); imports in and out (from the script graph); data stores touched (tables, files, queues) with read or write; external calls (HTTP hosts, SDKs); credential names referenced (env var or secret names only, never values); tests (location, command, last result, coverage gaps); build and run commands; known breakages (symptom, evidence path, reproduction); confidence tag per fact (script-derived, read-verified, inferred); open questions.
- (mine) System-level file: module list with one-line purposes, dependency graph artefact path (DOT/JSON), entry-point table, data-store table, external-call table, credential-name table, test inventory, breakages. Credential and external-call tables can be built by Semgrep or ripgrep patterns, giving a checkable second source.
- (mine) Mark "inferred" claims and have a verifier subagent re-open a sample of cited lines before later phases rely on the map.

### Gaps
- No published standard schema for an as-is code map was found; this is design, not evidence.

## Recommendation, alternatives, rejects, spikes

- Recommendation: Claude Code orchestrator-worker mapping. Step 1, a script (no LLM) runs pydeps (Python) and dependency-cruiser or madge (TS) plus ripgrep passes for env-var, HTTP-call and DB-client patterns, writing JSON and DOT to a map directory. Step 2, one read-only subagent per module (Haiku or Sonnet Explore override) writes the per-module note and returns a path and a status line. Step 3, an integration subagent merges notes; a verifier subagent spot-checks cited lines. The lead reads only the status lines. All free, self-hosted.
- Alternatives: add scip-python/scip-typescript indexes for exact symbol references (free, needs a working install of the project); CodeQL (free for open source / research use, build-free for Python and JS/TS) for call and data-flow questions; Semgrep pattern scans for credentials and external calls; Aider's repo map as a separate quick-glance artefact (needs Aider, not Claude Code).
- Rejected: DeepWiki for John's private code (public repos only in the free tier I read; MCP not connected); auto-generated CLAUDE.md overview (2602.11988 results); a vector/embedding index (SWE-Explore: dense retrieval near random); agent teams (registry: about 7x tokens).
- Spike before building: (1) run the pipeline on one real mid-size John repo and record tokens per module, wall time and the lead's context growth; (2) measure map accuracy by having a verifier re-check a random 30 cited facts, plus compare against a single long-context Opus/Sonnet pass on the same repo; (3) test pydeps and dependency-cruiser on dynamic imports and TS path aliases in a real repo; (4) check whether CodeQL licence terms allow use on John's private repos before depending on it (I did not open the licence).

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Claude Code Explore/Plan subagents | https://code.claude.com/docs/en/sub-agents | Read-only exploration in separate context; model overridable to Haiku | Claude Code | 2026-10-16 | Use: the mapping workers |
| Aider repo map | https://aider.chat/docs/repomap.html | Tree-sitter definitions ranked by file-dependency graph, 1k-token default budget | Aider CLI (not installed) | 2026-10-16 | Reference design; do not adopt Aider as engine |
| SCIP / scip-python / scip-typescript | https://docs.sourcegraph.com/code_intelligence/explanations/precise_code_intelligence | Exact symbol index per language | CLI, CI | 2026-10-16 | Fallback: add if reference lookups prove unreliable |
| Sourcegraph (hosted) | https://sourcegraph.com/docs/code-navigation | Search-based and precise navigation | hosted / self-hosted | 2026-10-16 | Skip for private repos; existing registry row covers public search |
| CodeQL | https://codeql.github.com/docs/codeql-overview/about-codeql/ | AST, data-flow and control-flow database; build-free for Python and JS/TS | CLI, local | 2026-10-16 | Fallback for targeted queries; licence unchecked |
| Semgrep (pattern syntax) | https://semgrep.dev/docs/writing-rules/pattern-syntax | Structural pattern matching with ellipsis and metavariables | CLI, local | 2026-10-16 | Use for credential and external-call inventory; spike |
| pydeps | https://pythonhosted.org/pydeps/index.html | Python import graph, external dependency JSON | pip, local | 2026-10-16 | Use for Python module graph (spike on dynamic imports) |
| dependency-cruiser | https://github.com/sverweij/dependency-cruiser | JS/TS dependency graph and rule checks, MIT | npx, local | 2026-10-16 | Use for TS module graph |
| madge | https://github.com/pahen/madge | JS/TS module graph, circular dependency finder | npm, local | 2026-10-16 | Alternative to dependency-cruiser |
| DeepWiki (docs) | https://docs.devin.ai/work-with-devin/deepwiki | Generated wiki, 30-page cap, public basic tier | hosted | 2026-10-16 | Skip for private code; public repos only |
| universal-ctags | https://docs.ctags.io/en/latest/man/ctags.1.html | Symbol tag index | local | 2026-10-16 | Skip; Aider dropped it for tree-sitter |
| FastContext | https://arxiv.org/html/2606.14066v1 | Trained small explorer subagent (research) | research, not run | 2026-10-16 | Reference only: design of read/glob/grep explorer returning file:line |
| DocAgent | https://aclanthology.org/2025.acl-demo.44.pdf | Dependency-ordered multi-agent docstring generation | research code (not run) | 2026-10-16 | Reference: topological order, verifier role |
| SWE-Explore | https://arxiv.org/pdf/2606.07297 | Benchmark of repo exploration | dataset, not run | 2026-10-16 | Evidence source; possible test harness |
| Claude Code OpenTelemetry | https://code.claude.com/docs/en/monitoring-usage | Export traces/metrics of agent runs | Claude Code | 2026-10-16 | Use to measure mapping token cost |
