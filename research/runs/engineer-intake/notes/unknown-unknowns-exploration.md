# Exploring unknown unknowns with AI, and the current interview skill

Brief: How can AI tools help a person who does not know what they do not know learn the landscape, explore paths quickly and narrow the search space until they can give precise instructions, and what does this repo's interview skill do today against that?
Run: research/runs/engineer-intake/PLAN.md

## Q1 Approaches for guided exploration and evidence of effectiveness

### Takeaway
Patterns with support: plan-first with user review (Gemini collaborative planning), externalised multilevel maps of topics (Sensecape), visible goal/subgoal trails (TrailLM), and LLM clarifying questions. Evidence is thin: Sensecape is a small within-subject study, TrailLM has no controlled study yet, and off-the-shelf LLMs rarely ask clarifying questions unprompted, so the agent must be told to. Confidence: medium.

### Cited findings
- Gemini Deep Research can return a plan for the user to review and refine before any research runs (a "plan, then approve" loop) — https://ai.google.dev/gemini-api/docs/deep-research, opened 2026-10-16, Parallel web_fetch — Quote: "letting you review and refine the research plan before execution. When enabled, the agent returns a proposed research plan instead of executing immediately."
- Sensecape (UIST 2023) found a map-like, multilevel abstraction interface led users to explore more topics and structure knowledge; this is a user study, pre-2025 — https://dl.acm.org/doi/10.1145/3586183.3606756, opened 2026-10-16, Parallel web_fetch — Quote: "Sensecape empowers users to explore more topics and structure their knowledge hierarchically, thanks to the externalization of levels of abstraction."
- TrailLM (Aug 2026 prototype) argues LLM answers let users skip sensemaking, and proposes visible goal/subgoal tracking; it reports no controlled results yet — https://arxiv.org/html/2607.11810v1, opened 2026-10-16, Parallel web_fetch — Quote: "The next step will be to run a controlled user study."
- Same paper: novices struggle to turn vague goals into good prompts — https://arxiv.org/html/2607.11810v1, opened 2026-10-16, Parallel web_fetch — Quote: "users often struggle to translate their goals into the detailed prompts needed to use these systems effectively"
- LLMs recognise ambiguity but seldom ask (May 2026) — https://www.alphaxiv.org/abs/2605.25284, opened 2026-10-16, Parallel web_fetch — Quote: "models often identify ambiguity when explicitly asked to judge it, yet in the QA setting they overwhelmingly default to direct answers."
- Same paper: giving the model retrieved context makes it ask less (relevant to "research then ask") — https://www.alphaxiv.org/abs/2605.25284, opened 2026-10-16, Parallel web_fetch — Quote: "Retrieved context further widens this gap by improving answerability while making models even less likely to ask clarifying questions."

### Contradictions
- None found.

### Inferences
- (Mine) A "map first, then ask" loop (agent shows a short option map, user reacts, agent narrows) fits the evidence better than open-ended questions alone, because reacting to options is easier than generating requirements. Rests on the TrailLM, Gemini planning and Su/Cardie findings; no study I opened tests this exact loop with novices.
- (Mine) The skill must explicitly require the agent to ask, since defaults are to answer.

### Gaps
- No opened source gives an effect size for "options map then narrow" versus plain interviewing with novices; comparison matrices and decision trees as aids found no evidence in this session.

## Q2 Deep-research and discovery tools: help and mislead

### Takeaway
They surface candidates the user could not name, but deep-research agents fabricate or break citation URLs at measurable rates, and LLMs invent package names. Every candidate needs an existence and recency check before it reaches John. Confidence: high on the risks, medium on how each product helps.

### Cited findings
- Claude's research feature runs chained searches and decides what to look into next, paid plans only, web/desktop — https://support.claude.com/en/articles/11088861-use-research-on-claude, opened 2026-10-16 (search result page text via Parallel search; page not separately fetched, so treated as excerpt) — Quote: "It runs multiple searches that build on each other and decides what to look into next based on what it finds."
- Citation URLs: deep research agents hallucinate more than search-augmented LLMs — https://arxiv.org/abs/2604.03173v1, opened 2026-10-16, Parallel web_fetch — Quote: "We find that 3--13\% of citation URLs are hallucinated -- they have no record in the Wayback Machine and likely never existed -- while 5--18\% are non-resolving overall."
- Same paper: a post-hoc URL checker cut failures — https://arxiv.org/abs/2604.03173v1, opened 2026-10-16, Parallel web_fetch — Quote: "models equipped with urlhealth reduce non-resolving citation URLs by $6\textrm{--}79\times$ to under 1\%"
- LLMs name nonexistent packages (2025) — https://www.usenix.org/conference/usenixsecurity25/presentation/spracklen, opened 2026-10-16, Parallel search excerpt (page text returned by search) — Quote: "the average percentage of hallucinated packages is at least 5.2% for commercial models and 21.7% for open-source models"
- Frontier models in late 2025 to early 2026 still do so (4.62% to 6.10%) — https://www.alphaxiv.org/abs/2605.17062, opened 2026-10-16, Parallel search excerpt — Quote: "overall hallucination rates between 4.62% (Claude Haiku 4.5) and 6.10% (GPT-5.4-mini)"
- Staleness: LLMs miss library changes (SANER 2026) — https://www.computer.org/csdl/proceedings-article/saner/2026/858200a749/2hNeHlFresE, opened 2026-10-16, Parallel search excerpt — Quote: "libraries can be obsolete because of deprecated, vulnerable, and the emergence of better alternatives"
- Official MCP registry search is only a name substring match, advanced search is delegated — https://raw.githubusercontent.com/modelcontextprotocol/registry/main/docs/reference/api/official-registry-api.md:41-42, read 2026-10-16, curl — Quote: "Case-insensitive substring search on server names (e.g., `filesystem`)" and "This is intentionally simple. For more advanced searching and filtering, use a subregistry."
- Registry handles spam only by after-the-fact reports — https://raw.githubusercontent.com/modelcontextprotocol/registry/main/docs/modelcontextprotocol-io/faq.mdx:52-54, read 2026-10-16, curl — Quote: "What if I need to report a spam or malicious server?"
- Live registry query for "browser" (curl, 2026-10-16) returned a pay-per-call x402 server and a Smithery-hosted server needing a bearer token, i.e. results are unvetted listings — registry.modelcontextprotocol.io/v0.1/servers?search=browser, curl — Quote: "pay-per-call x402 tools, no API keys"
- Exa and Parallel docs not opened this session beyond the tool-registry rows (see Gaps).

### Contradictions
- Package-hallucination rate: 5.2% to 21.7% (USENIX 2025) vs 4.62% to 6.10% on 2026 models (alphaxiv 2605.17062). Not a conflict; the spread narrowed on newer models.

### Inferences
- (Mine) Candidate lists from search must pass a verify step: URL resolves, repo exists, last commit date, star count (the Exa fetch gives this). The repo's rules already forbid uncited claims (CLAUDE.md research rules), which covers this for the research skill but not for what an interview offers John.
- (Mine) For a novice, the larger risk is not a fake link but a real yet stale or irrelevant tool recommended with confidence.

### Gaps
- Anthropic help page and Perplexity/Exa/Parallel product docs were not fetched and quoted individually; the Claude quote comes from the search result text.
- No opened source measuring staleness of deep-research product results specifically.

## Q3 Exploratory search literature and steering a novice

### Takeaway
Marchionini frames exploratory search as learning and investigation, not lookup, with vague and evolving needs; recent work warns LLM direct answers short-circuit that learning. Agent implication: help the user shift from "not knowing what to ask" to reacting to concrete options, while keeping goals visible. Confidence: medium (Marchionini read only via abstract).

### Cited findings
- Marchionini 2006 positions exploratory search as beyond fact retrieval — https://dl.acm.org/doi/10.1145/1121949.1121979, opened 2026-10-16, Parallel search excerpt (abstract) — Quote: "Research tools critical for exploratory search success involve the creation of new interfaces that move the process beyond predictable fact retrieval."
- Exploratory search is cognitively demanding with evolving needs, and users must notice gaps — https://arxiv.org/html/2607.11810v1, opened 2026-10-16, Parallel web_fetch — Quote: "users must reflect on their metacognitive processes to recognize what they know, identify knowledge gaps, and deliberately regulate their search."
- Direct answers to underdeveloped prompts can skip sensemaking — https://arxiv.org/html/2607.11810v1, opened 2026-10-16, Parallel web_fetch — Quote: "users receive a direct answer to an initial, often underdeveloped prompt, which may encourage them to bypass the critical process of iterative sensemaking."
- Goal clarification via expected information gain is an active 2026 line — https://arxiv.org/html/2606.03135, opened 2026-10-16, Parallel search excerpt — Quote: "we optimize for Expected Information Gain (EIG) to quantify goal uncertainty reduction."

### Contradictions
- None found.

### Inferences
- (Mine) Questions that most reduce the remaining option set should come first (information-gain idea), e.g. "must it run unattended?" before "which framework?".
- (Mine) Expert questioning (not read as primary source here) is out of scope of the evidence; do not cite it.

### Gaps
- Marchionini full text (ACM PDF) not read; only the abstract. No primary source on "known unknowns" taxonomy was opened.

## Q4 What the interview and research skills do today, and what is missing

### Takeaway
The interview skill is a pure conversation: one open question per turn, playback, five whys, anti-goals, EARS output and audit. It explicitly does no exploration and starts no reconnaissance unasked, so it cannot help someone who does not know what exists. The research skill can survey a landscape but only on a brief the user already has. Confidence: high.

### Cited findings
- Interview needs no workers and fetches no pages — /home/user/Autonomy-Research/plugin/skills/interview/SKILL.md:9-10 — Quote: "The interview is conversation with the user; it needs no workers and fetches no pages."
- Exactly one open question per turn — SKILL.md:17-18 — Quote: "the skill shall ask exactly one open question per turn, and shall not stack a"
- Five whys on goals — SKILL.md:21-23 — Quote: "probe it with five-whys questions ("why does that"
- Fixed question order of eight topics with no option menus — SKILL.md:33-44 — Quote: "Ask in this order, skipping what the user already answered. One question per turn."
- Prior art is asked of the user, not found for them — SKILL.md:42 — Quote: "6. Prior art: what exists, what was tried, what failed."
- Reconnaissance is opt-in only — SKILL.md:47-48 — Quote: "Offer repo or web reconnaissance as an option; do not start it unasked."
- Thin answers become gaps, never guesses — SKILL.md:26-28 — Quote: "It shall not invent an answer."
- Requirement lines must not name designs the user did not require — SKILL.md:65-66 — Quote: "A requirement states behaviour or a limit, not a design."
- No time or question budget exists in the interview skill (absence: no match for turn limit in the file; see Gaps).
- Research skill scales effort by brief shape, with landscape enumeration at 5 workers — /home/user/Autonomy-Research/plugin/skills/research/SKILL.md:36 — Quote: "| Landscape or enumeration | 5 | "Which MCP servers exist for browser automation?" | One worker per cluster. |"
- Research is triggered by a user-supplied brief and never reads sources in the lead — research/SKILL.md:26-27 — Quote: "In every run except a one-fact question, never fetch, search or read a source yourself;"
- Research hard-caps workers and gap rounds (a bound exists on research, not on intake) — research/SKILL.md:42 and 144-145 — Quote: "There is never a second gap round."

### Contradictions
- None found.

### Inferences
- (Mine) Missing against the approaches: (1) a landscape-first step that runs the research skill before or during intake and presents a short option map; (2) closed or option-based questions ("pick A/B/C/none/don't know") alongside the open ones, since one open question per turn is hard when the user does not know the vocabulary; (3) an explicit "I don't know" path that triggers exploration instead of recording a gap (today it only records a gap, lines 26-28); (4) a plan-approval checkpoint like Gemini collaborative planning; (5) a verification pass on any candidate offered; (6) a budget; (7) an unknown-unknowns probe asking what a domain expert would ask (pre-mortem/checklist of dimensions) rather than only what John already worries about (question 8).
- (Mine) The five-whys probe on goals suits a user with goals but may frustrate one who lacks the vocabulary; it should follow, not precede, the map.

### Gaps
- Whether agents in this repo already chain interview into research (no file read outside the two skills).

## Q5 Bounding "learn what you don't know" in time

### Takeaway
No source I opened gives a validated time budget for intake. Existing mechanisms that bound loops: Gemini's plan-approval step, this repo's worker and gap-round caps, and the claim that clarification should target high-information questions. Recommended design is mine: a fixed budget of rounds, stated up front. Confidence: low on numbers, medium on structure.

### Cited findings
- Research bounded by caps in the repo (8 workers, one gap round) — research/SKILL.md:42 — Quote: "| Hard cap | 8 | - | Never more than 8 workers in a run, gap round included. |"
- Gemini research runs async and takes minutes, so exploration can run while the user does other things — https://ai.google.dev/gemini-api/docs/deep-research, opened 2026-10-16, Parallel search excerpt — Quote: "Research tasks involve iterative searching and reading and can take several minutes to complete."
- Plan is approved before execution, giving a user checkpoint — see Q1 Gemini quote.

### Contradictions
- None found.

### Inferences
- (Mine) Proposed bound: one landscape pass of at most the existing 5-worker landscape row, in the background, while the interview continues; present one page of at most about 5 options per dimension; at most about 3 option-narrowing rounds, then stop and record leftovers as gaps. Numbers are untested and must be spiked.
- (Mine) Treat "don't know" as a branch that queues a facet for research, not a stop.

### Gaps
- No empirical source on intake length versus requirement quality; budget values need a spike with John.

## Recommendation, alternatives, rejected, spike
- Recommendation (mine): extend the interview skill with an "explore" branch: on "I don't know", dispatch the existing research skill for a landscape map in the background, present a short verified option map (3 to 5 options per dimension, each with a one-line trade-off and a verified link), let John pick or say "none/unsure", then resume EARS capture. Add a user-approved plan checkpoint and a fixed round budget. Free: uses Claude Code, the research skill and Parallel/Exa already connected; no new tool.
- Alternatives: (a) Gemini Deep Research collaborative planning via API, which has the plan-review loop built in but is a paid/preview separate engine, not needed since Claude Code is the engine; (b) Claude's research feature in claude.ai (paid plan, web/desktop, cannot be driven from the engineer); (c) a static checklist of dimensions for common builds, cheap and offline but goes stale.
- Rejected: pure open interviewing only (does not solve unknown unknowns); trusting deep-research output without URL verification (3 to 13% hallucinated URLs); adopting a UI like Sensecape or TrailLM (research prototypes, not installable products, TrailLM unevaluated).
- Spike before building: (1) run the explore branch on one real John topic and count how many verified candidates he had not known; (2) check the verify step (URL resolves, repo exists, recent commit) catches planted fake names; (3) time-box test with 3 versus 5 rounds and measure whether John can state requirements afterward.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Gemini Deep Research (Interactions API) | https://ai.google.dev/gemini-api/docs/deep-research | Research agent with optional collaborative plan review, MCP tool support; preview | Google API, paid | 2026-10-16 | Reference design for plan-approval loop only; skip as engine |
| Claude research feature | https://support.claude.com/en/articles/11088861-use-research-on-claude | Multi-search research in claude.ai, paid plans | claude.ai web/desktop | 2026-10-16 | Skip for the engineer; cannot be driven from Claude Code |
| Official MCP registry API | https://github.com/modelcontextprotocol/registry | Keyless name-substring search of MCP servers; unvetted listings | curl | 2026-10-16 | Use as one candidate source, always followed by verification |
| urlhealth | https://arxiv.org/abs/2604.03173v1 | Open-source URL liveness and stale-vs-hallucinated checker, 83 lines of Python | pip / agent skill | 2026-10-16 | Reference: copy the idea as a verify step; not installed |
| TrailLM / Sensecape | https://arxiv.org/html/2607.11810v1 | Research prototypes for exploratory search with LLMs | academic | 2026-10-16 | Skip; design ideas only |
