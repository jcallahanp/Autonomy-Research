# Integration mapping artifacts and comparing paths on evidence

Brief: Find which integration-mapping artifacts an autonomous Claude Code engineer can generate and keep current before building, and how it should represent and score candidate paths (one combination of tool choices) so they compare on evidence.
Run: research/runs/engineer-feasibility/PLAN.md

Connectors note: Parallel Search returned "Too Many Requests" on both searches; Exa search/fetch and WebFetch were used instead.

## Which mapping artifacts can an LLM generate as text and keep current?

### Takeaway
Text-first artifacts (Mermaid flowchart/sequence, Structurizr DSL, OpenAPI/AsyncAPI files, markdown tables) are generable by the model, and a parse/render check in CI or a hook is what keeps them valid; LLM-only generation is about 70% valid and about 95% only with validation plus a syntax reference. Keeping them current is a process problem (regenerate from code or config where possible, check on change), not a tool problem. Confidence: medium (the 70/95 figures come from one student project with local models).

### Cited findings
- C4 itself says two levels are enough for most teams — https://c4model.com/diagrams, opened 2026-10-16, WebFetch — Quote: "only those that add value - the system context and container diagrams are sufficient for most software development teams."
- Structurizr DSL is a text model of C4 and exports to PlantUML and Mermaid (D2 export not confirmed on the page) — https://docs.structurizr.com/dsl, opened 2026-10-16, WebFetch — Quote: "The Structurizr DSL provides a way to define a software architecture model."
- Mermaid's own C4 type is experimental — https://mermaid.js.org/syntax/c4.html, opened 2026-10-16, WebFetch — Quote: "This is an experimental diagram for now. The syntax and properties can change in future releases."
- LLM Mermaid reliability measured once: about 70% valid at first, 95% with a render check, repair loop and a long syntax reference; repair loop fixes only 80-85% of broken diagrams — https://llm-enabled-development-41d6d8.pages.cms.hu-berlin.de/en/archiv/experiments/diagram/diagram-long/, opened 2026-10-16, WebFetch — Quote: "This pipeline increased the success rate from an initial 70% to 95% after the final iteration."
- Same project: repair by the LLM is the weak point — same URL, opened 2026-10-16, WebFetch — Quote: "the repair of invalid code is only successful in about 80-85% of cases."
- A free MIT Mermaid linter exists that uses the official parser, runs via npx, and returns exit code 1 on failure, so it works as a CI gate or hook (Node 22+) — https://github.com/jasonworden/mermaid-lint, opened 2026-10-16, WebFetch — Quote: "Uses the official `mermaid.parse()` API — catches real syntax errors, not just missing diagram-type keywords."
- A real agent-driven repo found that nothing checked its docs' diagrams, so it added a render gate in CI — https://github.com/juliusz-cwiakalski/agentic-delivery-os/pull/123, opened 2026-10-16, WebFetch — Quote: "Agents cannot \"see\" a broken diagram; a human only notices by rendering."
- OpenAPI is the machine-readable contract format for REST — https://learn.openapis.org/, opened 2026-10-16, WebFetch — Quote: "A format readable by both machines and humans"
- AsyncAPI is the equivalent for event-driven APIs (webhooks, queues) — https://www.asyncapi.com/docs/tutorials/getting-started, opened 2026-10-16, WebFetch — Quote: "Much like OpenAPI (aka Swagger) does for REST APIs"
- Event storming is a human workshop format, not an agent output — https://www.eventstorming.com/, opened 2026-10-16, WebFetch — Quote: "EventStorming is a flexible workshop format for collaborative exploration of complex business domains."
- The Claude Code plan is not kept by default, so any mapping artifact must be saved as a file — https://kaden-projects.com/blog/vibe-coding-to-spec-first-agentic-ides-engineering-process/, opened 2026-10-16, WebFetch — Quote: "The plan itself is a review gate, not a committed document, unless you explicitly save it."

### Contradictions
- Mermaid C4 should be avoided because it does not render on GitHub — https://github.com/juliusz-cwiakalski/agentic-delivery-os/pull/123 (PR text: "AVOID Mermaid C4 (renders in tooling, not on GitHub)"); disagrees with a later comment in the same PR where the author says GitHub now renders C4 and removed the restriction (commits 98e4f73, 87ef6bb, as reported by the fetch tool). Mermaid itself still labels C4 experimental (above). A spike should render a C4 block on John's actual viewer; default to plain flowchart/sequence.

### Inferences
- The engineer should author the integration map in plain Mermaid `flowchart` plus `sequenceDiagram` (labelled with C4 level in a title/comment), not Mermaid C4 or Structurizr, for a small project; Structurizr DSL is a fallback only when one model must yield several views (rests on experimental C4 label, 70/95% figures, single-project evidence).
- Generate from facts, not memory: config snapshots (see engineer-existing-systems.md recommendation step 2) and OpenAPI files feed the diagram, and a parse gate (mermaid-lint or mmdc) plus a Stop/PostToolUse hook rejects invalid blocks; this follows from the 70%-to-95% finding and the PR 123 incident.
- Event storming cannot be run by the agent alone; its useful output (events, actors, systems) can be replaced by an interview-derived event list in the intake spec.
- "Kept current" means: each diagram has a source-of-truth pointer (file path or API snapshot) and a last-verified date in the file; a check flags the diagram when the pointed file changes. No opened source shows this done for integration maps, so it is untested.

### Gaps
- No opened source measured how often agents keep diagrams-as-code current across design changes; only validity (syntax) was measured. Needs a spike.
- Structurizr D2 export unconfirmed (page did not mention D2). PlantUML and D2 LLM reliability not researched.
- Whether GitHub (or John's viewer) renders Mermaid C4 today: not settled.

## Minimum mapping set for a small project

### Takeaway
Three artifacts carry most of the value: (1) a context-plus-container flowchart showing every system, who owns it and what crosses each boundary; (2) an integration matrix (table: edge, direction, protocol, auth, data moved, contract source, evidence/status, failure mode); (3) one sequence diagram per critical flow, only for the flow being built. OpenAPI/AsyncAPI files are inputs referenced from the matrix, not separate deliverables. Confidence: medium (synthesised; the one opened source on the diagram level is C4's own).

### Cited findings
- C4 context and container are sufficient for most teams — https://c4model.com/diagrams, opened 2026-10-16, WebFetch — Quote: "only those that add value - the system context and container diagrams are sufficient for most software development teams."
- The earlier existing-systems recommendation already prescribes "C4 context-plus-container Mermaid, system-of-record table, credential inventory" with each row marked observed, inferred or asserted, and John reviewing the context diagram and system-of-record table — /home/user/Autonomy-Research/research/findings/engineer-existing-systems.md:83, read 2026-10-16, Read/grep — Quote: "John reviews the context diagram and the system-of-record table, and the pack feeds the intake explore branch"
- The earlier intake recommendation already shows John a comparison table of at most 5 options, not a diagram, and offers a diagram after he picks (worker inference there) — /home/user/Autonomy-Research/research/findings/engineer-intake.md:51, read 2026-10-16, grep — Quote: "offer a diagram only after he picks (judgement, no source)."
- AWS lists "Interfaces (APIs and published contracts)" and "Dependencies" as ADR-worthy decision areas, so the matrix rows map onto ADR triggers — https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html, opened 2026-10-16, WebFetch — Quote: "Interfaces (APIs and published contracts)"

### Contradictions
- None found.

### Inferences
- Integration matrix is the highest-value artifact because it is a table (reliable for an LLM to write, diff-able in git, checkable by script for empty cells) and it holds the evidence column that the path comparison needs. This is my judgement; no opened source ranks artifacts by value.
- Dependency graphs from code (pydeps, dependency-cruiser; already in registry) feed container-level edges for existing code; for SaaS-to-SaaS glue (Attio, Clay, n8n) the edges come from config exports, so the matrix, not a code graph, is the main artifact for John's GTM case.
- For the health app (code in a repo) the dependency graph adds more; for GTM (repo holds nothing per existing-systems) the config snapshot plus matrix dominates.
- John reviews diagram and matrix at the "map" gate; he never needs to read OpenAPI/AsyncAPI.

### Gaps
- No small-project case study was found that tests which two or three artifacts reduce rework. The set above is not validated.

## Representing and scoring a path (rubric, weights)

### Takeaway
Represent a path as one row-set in a matrix: hard gates first (pass/fail with evidence), then a few criteria rated on a coarse High/Medium/Low (or +/0/- against a datum) scale, each cell carrying an evidence level and a source; no weighted sum to decimals. Weights, if any, are set by John before scoring, frozen, and tested by sensitivity; near-ties are declared ties and decided on reversibility. Confidence: medium-high on the method, medium on the criterion list (it is a synthesis).

### Cited findings
- Pugh matrix is non-numeric, compares each option to a datum with +, S, - — https://www.ifm.eng.cam.ac.uk/research/dmg/tools-and-techniques/controlled-convergence/, opened 2026-10-16, WebFetch — Quote: "non-numeric and iterative tool for concept selection"
- Weighted scoring is defensible only if weights are frozen before scoring — https://www.digitaladvisory.com/resources/frameworks/weighted-scoring-model, opened 2026-10-16, WebFetch — Quote: "The model produces a defensible decision only when the criteria and weights are locked before anyone scores"
- Near-ties are not verdicts — same URL, opened 2026-10-16, WebFetch — Quote: "A 6.75 versus 7.00 result is a tie that deserves a conversation, not a verdict."
- Mandatory requirements belong in a gate, not in the weights — same URL, opened 2026-10-16, WebFetch — Quote: "it belongs in a pass/fail gate before scoring, not blended into a percentage."
- SEI says stakeholders cannot rate finer than three levels — SEI CMU/SEI-2000-TR-004 https://www.sei.cmu.edu/documents/629/2000_005_001_13706.pdf (pdftotext of the fetched file, line 1151), read 2026-10-16, WebFetch + pdftotext — Quote: "stakeholders cannot reliably and repeatably make finer distinctions than High, Medium, and Low."
- Weightings add upkeep and error risk; prefer splitting criteria to the same level of abstraction — https://jacquiread.com/posts/2024-09-11-decision-making-adrs-weightings-are-a-workaround/, opened 2026-10-16, WebFetch — Quote: "These need to be reassessed when criteria are added and removed"
- A rune-kit rubric scores reversibility 1-5 on cost to change one's mind and demands a named rejected alternative — https://github.com/rune-kit/rune/blob/master/skills/journal/references/adr-criteria.md, opened 2026-10-16, WebFetch — Quote: "Score 1–5: how expensive is it to change your mind later?"

### Contradictions
- Weighted numeric scoring is the standard decision-matrix recipe (https://www.digitaladvisory.com/resources/frameworks/weighted-scoring-model, with weights frozen) versus an engineering-manager post calling summed weighted scores an anti-pattern to be "avoided entirely" (https://engmanage.substack.com/p/decision-matrix, 2025-09-03, seen in Exa results, not separately opened). Reconciled in Inferences: use gates plus coarse ratings, no sum.

### Inferences
- Proposed rubric for a path (my synthesis; criteria drawn from the brief, structure from the sources above):
  - Gates (pass/fail, evidence required): works with the accounts and permissions John actually has; no secret leaves its allowed boundary; privacy-risk data (health) not sent to an unapproved processor; free tier or priced within John's stated limit.
  - Rated H/M/L, each cell with an evidence tag: feasibility evidence (spiked = ran it; documented = vendor docs opened; asserted = unverified), John's effort (his clock time, setup + upkeep), cost (monthly, with price quoted), maintenance (who fixes it when it breaks, update cadence), reversibility (use the 1-5 scale mapped to H/M/L), lock-in (export format, can leave in a day), privacy risk (what data crosses which boundary).
  - Order of judgement follows the ruling: outcome quality (feasibility evidence, gates) first, then John's effort, then cost; maintenance, reversibility, lock-in, privacy break ties and trigger flags.
- Weights without false precision: ask John once to rank the 3 to 4 criteria he cares about (rank order, not percentages), freeze it in the decision file before scoring, then do a sensitivity check (does the winner change if the top two criteria swap?). Report "tie" when it does. Rests on SEI High/Med/Low finding, tie quote, weights-frozen quote.
- Evidence level should be a separate column from the rating, so an unspiked "High" cannot look like a spiked "High". Rests on the "asserted/inferred/observed" marking already used in existing-systems and on the cited weighted-scoring warnings; no opened source defines evidence grades for tool choices.
- Use a Pugh datum = the cheapest or current path (often "do nothing" or John's named tool), which makes the effort and cost comparison relative and cheap to LLM-generate.
- Mini-ATAM scenarios are useful in miniature: write 3 to 5 concrete scenarios ("Clay row arrives, Attio record exists within 5 min, no duplicate") and check each path against them. Full ATAM is too heavy for one user.

### Gaps
- Two pages seen only in Exa excerpts were not opened separately (dmccreary ATAM chapters, engmanage substack); their claims are listed with that caveat and are not load-bearing.
- https://sustainablecatalyst.com/decision-matrices-and-their-limits/ (2026-06-05): WebFetch returned a truncated page ("Content truncated due to length"); no quote taken.
- No source found that validates the proposed criteria list for tool-integration choices specifically.
- Whether an LLM scores consistently across runs (rating noise) is untested; needs a spike (score the same 3 paths 5 times, compare).

## How agent tools and practitioners do this today

### Takeaway
All the agent tools share one loop: explore, produce a plan, human approves, then build. They differ in how durable the artifact is. Claude Code plan mode is not persisted by default, Kiro persists requirements/design/tasks, and practitioners fill the gap for "why we chose X" with lightweight ADRs that the agent checks before design changes. None of the opened sources shows a tool that compares integration paths on gathered evidence; that part is custom. Confidence: medium.

### Cited findings
- Claude Code plan mode plan is a review gate, not committed — https://kaden-projects.com/blog/vibe-coding-to-spec-first-agentic-ides-engineering-process/ (2026-06-16), opened 2026-10-16, WebFetch — Quote: "The plan itself is a review gate, not a committed document, unless you explicitly save it."
- Kiro design.md already holds alternatives considered and maps to ADRs — same URL, opened 2026-10-16, WebFetch — Quote: "Design decisions captured in `design.md` map cleanly onto Architecture Decision Records."
- Agents do not know past decisions and may reverse them unless ADRs are scanned; a CLAUDE.md rule can force the check — https://zenn.dev/kosk_t/articles/adr-lightweight-decision-records-for-ai?locale=en (2026-04-20), opened 2026-10-16, WebFetch — Quote: "Agents like Claude Code don’t know past team decisions."
- Google Cloud advises ADRs be kept with code and written when options compete — https://docs.cloud.google.com/architecture/architecture-decision-records, opened 2026-10-16, WebFetch — Quote: "Store your ADRs close to your application code, ideally in the same version control system."
- AWS Prescriptive Guidance treats accepted ADRs as immutable — https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html, opened 2026-10-16, WebFetch — Quote: "When the team accepts an ADR, it becomes immutable."
- A recorded ADR criteria gate: only log a decision if hard to reverse, surprising and a real trade-off; conventions go in CLAUDE.md — https://github.com/rune-kit/rune/blob/master/skills/journal/references/adr-criteria.md, opened 2026-10-16, WebFetch — Quote: "Conventions are choices everyone makes the same way."

### Contradictions
- None found among opened sources. (Kiro and Cursor behaviour descriptions come from third-party blogs dated 2026-06, not the vendors' own pages; the Kiro plan-mode doc https://kiro.dev/docs/specs/plan/ appeared only in a search excerpt.)

### Inferences
- Claude Code is the engine, so plan mode is the approval surface and the engineer must write the matrix and ADR to files; the plan alone is lost. Rests on the Kaden quote and registry row for plan mode (issues #50176, #30090).
- A one-line CLAUDE.md rule ("before choosing a tool or integration, read docs/adr/ and the decision file") is a cheap fit for the engineer, based on the Zenn finding.
- Third-party agent frameworks (Kiro, Spec Kit, OpenSpec, BMAD) are already in the registry; none adds evidence-based path comparison, so adopt none for this.

### Gaps
- Devin, Factory and Cursor treatment of alternatives: not researched beyond registry rows; no opened source in this facet.
- Bruniaux "Plan-Validate-Execute" guide (cc.bruniaux.com) described ADR auto-resolution from search excerpt only; not opened, not cited.
- No 2025-2026 write-up found that scores competing integration stacks; likely absent or not indexed.

## From comparison to an auditable recorded decision

### Takeaway
Record each decision as a short MADR-style ADR in git: context, decision drivers, considered options with pros/cons and evidence links, decision outcome, a "confirmation" line stating how it will be verified, status (proposed, then accepted by John), and supersede-not-edit. The matrix is attached or linked. John's approval is a file edit (status change plus date), not only a chat reply. Confidence: high on ADR mechanics, medium on the approval-record design.

### Cited findings
- MADR template sections: decision drivers, considered options, pros and cons, confirmation — https://adr.github.io/madr/, opened 2026-10-16, WebFetch — Quote: "a streamlined template for recording architectural significant decisions in a structured manner."
- MADR has a confirmation field — same URL, opened 2026-10-16, WebFetch — Quote: "Describe how the implementation of/compliance with the ADR can/will be confirmed."
- ADR is short and keeps status — https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions, opened 2026-10-16, WebFetch — Quote: "The whole document should be one or two pages long."
- Reversal keeps history — same URL, opened 2026-10-16, WebFetch — Quote: "If a decision is reversed, we will keep the old one around, but mark it as superseded."
- AWS lifecycle Proposed, Accepted, Rejected, Superseded with timestamp and stakeholders — https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html, opened 2026-10-16, WebFetch — Quote: "If the team approves the ADR, the owner adds a timestamp, version, and list of stakeholders."
- Google's outline includes key options and reasons for the accepted choice — https://docs.cloud.google.com/architecture/architecture-decision-records, opened 2026-10-16, WebFetch — Quote: "When there are two or more engineering options and you want to document your thoughts and reasons behind the selection."
- The earlier intake recommendation already prescribes an "accepted over objection" ADR and a file-based approval record — /home/user/Autonomy-Research/research/findings/engineer-intake.md:77, read 2026-10-16, grep — Quote: "approval recorded in a file, not via ExitPlanMode alone"

### Contradictions
- None found.

### Inferences
- Proposed ADR for a path decision (my design): MADR sections plus (a) the gate table with evidence, (b) the rated matrix with evidence tags, (c) the frozen criteria order and date set by John, (d) the sensitivity note and "tie" flag, (e) "what would change this decision" triggers, (f) the spike result links, (g) status line `proposed -> accepted by John <date>` or `accepted over objection`. Keep to about two pages; the matrix lives in a linked file.
- Auditability for a non-engineer: a one-paragraph plain-language summary at top ("We chose X because Y; the cost is Z; you can undo it by W"). John reads that and the status line only.
- Re-open rule: each ADR names the evidence that, if it changes (price change, API limit, failed spike), makes the engineer propose a superseding ADR; a hook or session-start check lists ADRs whose triggers are flagged.
- Only record a path decision as an ADR if it passes the rune-style gate (hard to reverse, real alternative); small choices go in a conventions list.

### Gaps
- No opened source tests whether non-engineers actually audit ADRs; John's "approve without parsing" habit (existing-systems finding, docs/agent_rules.md:15-16) suggests the summary line matters more than the template. Spike: show John 3 ADRs, ask him to state what was decided and why.

## Recommendation, alternatives, rejected, spike list

**Recommendation (my synthesis).** For each integration choice, the engineer writes three small files in the repo: `docs/map/integration-map.md` (plain Mermaid flowchart at context+container level plus per-flow sequence diagrams, parse-checked), `docs/map/integration-matrix.md` (one row per edge with contract source and evidence tag), and `docs/adr/NNNN-<choice>.md` (MADR with the path matrix: gates, H/M/L ratings with evidence tags, John's frozen criterion order, sensitivity note, confirmation line, status). Paths are compared by gates first, then a Pugh-style rating against a datum (the cheapest or current path), then a tie rule that falls to reversibility. John approves by editing status; Claude Code plan mode is the live gate, the file is the record. All free: Markdown, Mermaid, mermaid-lint (MIT) in a hook.

**Alternatives.** Structurizr DSL when several C4 views must come from one model (self-hosted, free); weighted numeric scoring with frozen weights and sensitivity analysis if John wants a single number; mini-ATAM scenarios (3 to 5) for the one or two highest-risk choices; Kiro-style design.md per feature when the work is larger.

**Rejected.** Full ATAM (multi-day, 8-20 people per the cited table); event storming as an agent output (human workshop); Mermaid C4 as default (experimental, render question); summing unfrozen weights to two decimals (false precision); adopting Kiro, BMAD or Spec Kit just for this (already rejected or reference-only in the registry).

**Spike before building.** (1) Generate the integration map and matrix for John's GTM system from config snapshots and check validity rate and correctness vs a hand-made one. (2) Run mermaid-lint as a hook on 20 generated diagrams and count failures and repair rounds. (3) Score 3 candidate paths 5 times each; measure rating stability. (4) Show John 3 ADRs; test whether he can state the decision and its undo path. (5) Change one design input and see whether the stale-diagram check flags the map. (6) Render a Mermaid C4 block where John views docs.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| MADR | https://adr.github.io/madr/ | Markdown ADR template with decision drivers, considered options, pros/cons, confirmation | notation, no install | 2026-10-16 | Use as the decision record template |
| mermaid-lint | https://github.com/jasonworden/mermaid-lint | MIT; validates Mermaid blocks in Markdown with official parser; npx, Node 22+; exit 0/1/2 | local, CI, hook (not installed) | 2026-10-16 | Use as the diagram gate; spike on a dozen generated diagrams |
| Mermaid C4 diagram type | https://mermaid.js.org/syntax/c4.html | C4 inside Mermaid; labelled experimental | Mermaid renderers | 2026-10-16 | Skip as default; use plain flowchart |
| Structurizr DSL | https://docs.structurizr.com/dsl | Text C4 model; exports PlantUML/Mermaid | local tooling | 2026-10-16 | Fallback only when multiple views from one model |
| OpenAPI / AsyncAPI | https://learn.openapis.org/ ; https://www.asyncapi.com/docs/tutorials/getting-started | Machine-readable REST / event API contracts | files | 2026-10-16 | Use as inputs referenced by the matrix, not as deliverables |
| EventStorming | https://www.eventstorming.com/ | Human workshop for domain events | workshop | 2026-10-16 | Skip for the agent |
| Pugh matrix (controlled convergence) | https://www.ifm.eng.cam.ac.uk/research/dmg/tools-and-techniques/controlled-convergence/ | Non-numeric comparison against a datum | notation | 2026-10-16 | Use for path comparison |
| ATAM / mini-ATAM | https://www.sei.cmu.edu/documents/629/2000_005_001_13706.pdf | Utility tree and scenarios; risks, sensitivity and tradeoff points | method | 2026-10-16 | Borrow scenarios and H/M/L only |
| Weighted scoring model | https://www.digitaladvisory.com/resources/frameworks/weighted-scoring-model | Weighted sum with frozen weights | spreadsheet | 2026-10-16 | Alternative; only with frozen weights, gates, tie rule |
| rune-kit ADR criteria | https://github.com/rune-kit/rune/blob/master/skills/journal/references/adr-criteria.md | Gate for when to write an ADR; 1-5 reversibility scale | skill reference (not installed) | 2026-10-16 | Reference: copy the gate and counter-test |
| mermaid-mcp-server (andrewginns) | https://github.com/andrewginns/mermaid-mcp-server/ | MCP validating Mermaid via mermaid-cli | local, needs Node and Python (not installed; page seen in search excerpt only) | not opened (search excerpt only) | Skip; mermaid-lint is simpler; unverified |
