# Diagrams for the agent: text versus image, and the system-map skill

Brief: Decide what the agent-facing counterpart of John's brief should be, with evidence on text versus image diagrams for LLMs, and what the system-map skill needs.
Run: research/runs/engineer-briefing/PLAN.md

Tooling note: Parallel Search returned "Too Many Requests" on both searches; Exa search and fetch were used. DeepWiki, Firecrawl, Playwright not connected. Exa search highlights were used only where the same page was also opened with a fetch tool (Code-Vision, Structurizr as-code, Claude best-practices); other quotes below come from Exa search results that returned page text (marked "Exa search text") and should be treated as one level weaker.

## Evidence on LLMs reading diagrams: text vs image

### Takeaway
No benchmark tests "does a coding agent implement more faithfully from Mermaid or from a rendered image". The nearest evidence points one way: for structure (nodes, edges, flow), text input equals or beats image input, and image plus text together beats either alone for global properties. So the agent's source of truth should be text; the picture is for John. Confidence: medium (2024-2025 papers on older models; no agentic-coding test).

### Cited findings
- Code-Vision (Feb 2025) fed the same flowcharts as image and as Mermaid; most models did better on Mermaid, open-source ones much better — https://arxiv.org/html/2502.11829, opened 2026-10-16, Exa web_fetch_exa (search text for the Table 4 passage) — Quote: "when using mermaid as input, most models exhibit performance improvements. This suggests that the mermaid, being a more structured and textual representation, may be easier for MLLMs to interpret"
- In the same benchmark GPT-4o reached 79.3% pass@1 on Hard problems from flowchart images, so strong proprietary models read flowcharts well; the gap is mainly open models — https://arxiv.org/html/2502.11829, opened 2026-10-16, Exa web_fetch_exa — Quote: "On Hard problems, GPT-4o can achieve 79.3% pass@1, but the best open-source model only achieves 15%."
- GITA/GITQA (graph reasoning): visual-only is worse than text-only on average; text plus image is best — https://arxiv.org/html/2402.02130v3, opened 2026-10-16, Exa search text — Quote: "using the visual modality alone is worse than using the textual modality alone on average."
- Same paper: combining modalities wins — https://arxiv.org/html/2402.02130v3, opened 2026-10-16, Exa search text — Quote: "combining textual and visual information together performs better than using one modality alone."
- Case study with GPT-4o: images alone are not enough, and help most on global properties (cycle detection) — https://arxiv.org/html/2409.08864, opened 2026-10-16, Exa search text — Quote: "providing only graph visualisations, without accompanying textual descriptions, is insufficient for LLMs to fully comprehend graph structures."
- Text encoding matters a lot: the same graph in different text forms moves accuracy from 19.8% to 53.8% on one task — https://proceedings.iclr.cc/paper_files/paper/2024/file/bf72f65f30eedf5d48da6980ee02b589-Paper-Conference.pdf, opened 2026-10-16, Exa search text — Quote: "for finding connected nodes to a node in a graph, adjacency achieves 19.8% accuracy and incident achieves 53.8% accuracy."
- JSON beat natural-language and DOT graph representations after instruction tuning (small Llama/Mistral/Gemma models, tuned) — https://doi.org/10.48550/arxiv.2408.05457, opened 2026-10-16, Exa search text — Quote: "JSON format for graph representation consistently outperforms natural language and code formats across various LLMs and graph types."
- Reading a flowchart image back into Mermaid is hard even for frontier VLMs of 2024 — https://doi.org/10.48550/arxiv.2407.05183, opened 2026-10-16, Exa search text — Quote: "struggled with the more complex task of accurately generating Mermaid code from flowcharts."
- FlowVQA: VLMs struggle on image flowcharts built from Mermaid scripts — https://aclanthology.org/2024.findings-acl.78.pdf, opened 2026-10-16, Exa search text — Quote: "both closed and open-source Vision Language Models (VLMs), equipped with a range of prompting strategies and fine-tuning techniques, struggled to execute visual and spatial reasoning tasks"
- Dissenting result (see Contradictions): GraphTMI (NAACL 2024 Findings) found image better than text for large graphs — https://aclanthology.org/2024.findings-naacl.34/, opened 2026-10-16, Exa search text — Quote: "the image modality, especially with vision-language models like GPT-4V, is superior to text in balancing token limits and preserving essential information"
- LLMs generating diagrams from text: seven LLMs, Mermaid versus structured YAML, results vary widely by model — https://doi.org/10.1016/j.procs.2025.09.191, opened 2026-10-16, Exa search text — Quote: "some LLMs demonstrating strong syntax adherence, while others struggle with diagram structure and semantic accuracy."
- LLM-generated UML via PlantUML scored 61.1% to 67.7% completeness/correctness and always below human diagrams (GPT-4-turbo, one domain, student raters) — https://doi.org/10.3390/info16070565, opened 2026-10-16, Exa search text — Quote: "they consistently underperform compared to human-created diagrams."
- Claude 3.7 Sonnet generated diagrams with many extra nodes (31.67 on average versus 21.42 Gemini), so generated diagrams over-include — https://aclanthology.org/2025.emnlp-main.640.pdf, opened 2026-10-16, Exa search text — Quote: "Claude produces diagrams with 31.67 nodes on average, much more than 21.42 nodes of Gemini and 10.68 nodes of Llama."

### Contradictions
- GraphTMI: image beats text on token budget for big graphs (https://aclanthology.org/2024.findings-naacl.34/) disagrees with GITA: visual-only is worse than text-only on average (https://arxiv.org/html/2402.02130v3) and Code-Vision: Mermaid beats flowchart image (https://arxiv.org/html/2502.11829). Tasks differ (graph statistics on large graphs versus path/flow reasoning on small diagrams) and models are GPT-4V era; a spike on John's own architecture facts would settle it.

### Inferences
- The brief's diagram is small (about 25 lines, C4 context and container). At that size text is cheap in tokens, so the token argument for images does not apply. Source of truth for the agent: text. (rests on Code-Vision, GITA, 2409.08864)
- A rendered image is a supplement worth giving the agent only for visual review tasks (a UI), not for architecture facts. (rests on 2409.08864: image-only is insufficient)
- Nothing here measures 2026 frontier models or agentic implementation fidelity; the claim "a coding agent implements more faithfully from text" is an inference, not a measured result.

### Gaps
- No paper found comparing implementation fidelity of a coding agent given Mermaid versus a rendered image of the same design. Searches did not surface one.
- No 2026 benchmark found for frontier models on text-versus-image architecture diagrams.
- No evidence found on C4 JSON or OpenAPI as agent source of truth beyond the Structurizr vendor claim below.

## The split: text for the agent, picture for the human

### Takeaway
Practice supports one text model with views generated from it. Structurizr is the worked example: a DSL workspace in git beside the code, rendered to a viewer or exported to Mermaid and PlantUML, with an MCP server for AI. For John (one user, small systems) the single source can be a small hand-kept file the engineer maintains, with Mermaid views rendered from it; Structurizr is a heavier option. Confidence: medium (vendor sources, no independent comparison).

### Cited findings
- Structurizr separates model from views and recommends text for AI — https://docs.structurizr.com/ai, opened 2026-10-16, Exa search text — Quote: "you can create a collection of consistent views onto a single model, where element names/descriptions, relationship descriptions, styling, etc all remain the same across the diagrams."
- It exports to Mermaid and PlantUML, so the human picture is a rendering of the same source — https://docs.structurizr.com/ai, opened 2026-10-16, Exa search text — Quote: "export Structurizr views to “diagrams as code” formats such as PlantUML and Mermaid for integration into your existing toolchain."
- Structurizr's own claim that diagrams-as-code tools lack model consistency (vendor view; Mermaid alone is a view, not a model) — https://docs.structurizr.com/ai, opened 2026-10-16, Exa search text — Quote: "diagrams as code tools tools don’t understand the C4 model and don’t respect its rules."
- Source and compiled forms: DSL is the source, JSON is generated — https://docs.structurizr.com/workspaces/file-types, opened 2026-10-16, Exa search text — Quote: "The “compiled” version of your workspace source, additionally including diagram layout information from the diagram editor. This is an open JSON data format and is not designed to be edited by hand."
- Who maintains it: the team, in git next to the code, with agents proposing updates — https://docs.structurizr.com/as-code, opened 2026-10-16, Exa web_fetch_exa — Quote: "AI agents have limited abilities to interact with UI-driven tools, but they can generate text, making “as code” tools a better option"
- Agent roles Structurizr lists: diagram generation from a codebase, update via pull requests, drift detection — https://docs.structurizr.com/as-code, opened 2026-10-16, Exa search text — Quote: "an AI agent periodically compares code or infrastructure against the Structurizr model and raises an alert when they diverge."
- Structurizr MCP server is free, open source, can validate DSL and export to Mermaid/PlantUML; a hosted instance exists at mcp.structurizr.com — https://docs.structurizr.com/ai/mcp, opened 2026-10-16, Exa search text — Quote: "A free and open source Structurizr MCP server is available on GitHub. It runs standalone and supports stateless HTTP transport."
- Structurizr DSL carries a learning cost and needs Java tooling to run (cost note from the vendor) — https://docs.structurizr.com/as-code, opened 2026-10-16, Exa web_fetch_exa — Quote: "The Structurizr DSL does have a slightly higher learning curve than a UI."
- Claude Code's own guidance puts architectural decisions in CLAUDE.md but not file-by-file descriptions, and pushes sometimes-relevant knowledge into skills loaded on demand — https://code.claude.com/docs/en/best-practices, opened 2026-10-16, WebFetch — Quote: "CLAUDE.md is loaded every session, so only include things that apply broadly. For domain knowledge or workflows that are only relevant sometimes, use skills instead."
- Same page, the include/exclude table — https://code.claude.com/docs/en/best-practices, opened 2026-10-16, WebFetch — Quote: "Architectural decisions specific to your project" (include) and "File-by-file descriptions of the codebase" (exclude)

### Contradictions
- Structurizr says plain diagrams-as-code are a poor fit (https://docs.structurizr.com/ai); the repo's rule and skill use plain Mermaid flowcharts and forbid C4 syntax (plugin/skills/system-map/SKILL.md:13-14). Structurizr is a vendor with a stake; for one user with small diagrams the cost of Java tooling may outweigh model consistency. A spike would settle it.

### Inferences
- Recommended split (mine): a small `architecture.yaml` (or `.json`) per system holds named nodes, edges with labels, and the facts the agent needs (owner, store, credential name, status confirmed/unconfirmed). The skill renders Mermaid `.mmd` views from it for John. The engineer is the maintainer and any change to the system must update the file in the same commit, enforced by a check that every Mermaid node id exists in the file. This copies the Structurizr idea (one model, many views) without Java. Rests on Structurizr docs and on the repo's existing .mmd checker.
- The agent should read the text model by path on demand, not from CLAUDE.md (see next section).
- Fallback if John wants model rules enforced: Structurizr DSL plus its MCP export to Mermaid; spike before adopting.

### Gaps
- No independent (non-vendor) account of a team using Structurizr or Mermaid as the agent's source of truth found in this session.
- No Anthropic-specific page on architecture diagrams for agents found beyond the best-practices page.
- Whether the Structurizr MCP validates and exports without a Java install was not tested.

## How much architecture context helps or hurts

### Takeaway
The wave 1 finding is real but narrow: on Python issue-fixing benchmarks, repository overviews in AGENTS.md-style files did not help the agent find the right files and the files raised cost by over 20%. It does not test a map of external systems, credentials and integrations, which an agent cannot find by grepping code. So: keep overviews out of the always-loaded file, keep the map as an on-demand file with only non-discoverable facts. Confidence: medium-high on the finding, low on the transfer.

### Cited findings
- Cost and success: context files did not raise success and raised cost — https://arxiv.org/html/2602.11988, opened 2026-10-16, Exa search text — Quote: "providing context files does not generally improve task success rates, while increasing inference cost by over 20% on average."
- Overviews specifically — https://arxiv.org/html/2602.11988, opened 2026-10-16, Exa search text — Quote: "We conclude that context files are not effective at providing a repository overview."
- Measure used: steps before the agent touches a file in the real patch did not fall — https://arxiv.org/html/2602.11988, opened 2026-10-16, Exa search text — Quote: "the context files do not meaningfully reduce this metric"
- Scope: four coding agents, SWE-bench plus a new benchmark of 138 instances in 12 Python repositories — https://arxiv.org/abs/2602.11988, opened 2026-10-16, Exa search text — Quote: "comprising Python software engineering tasks, created specifically from real GitHub issues. The benchmark contains 138 unique instances"
- What did work: instructions are followed, and the paper recommends minimal, non-discoverable requirements — https://arxiv.org/abs/2602.11988, opened 2026-10-16, Exa search text — Quote: "Human-written context files should only include instructions required for coding agents that are not already present in the README"
- Developer-written files gave a small non-significant gain, LLM-generated a marginal loss — https://arxiv.org/html/2602.11988, opened 2026-10-16, Exa search text — Quote: "LLM-generated context files have a marginal negative effect on task success rates, while developer-written ones provide a marginal performance gain, neither statistically significant."
- Claude Code's guidance matches: exclude what the agent can read from code, and prune — https://code.claude.com/docs/en/best-practices, opened 2026-10-16, WebFetch — Quote: "Bloated CLAUDE.md files cause Claude to ignore your actual instructions!"
- Earlier-wave note that context-file overview guidance versus this paper remained unresolved — /home/user/Autonomy-Research/research/findings/engineer-existing-systems.md:415 — Quote: "context-file overview guidance versus 2602.11988"

### Contradictions
- Agent vendors recommend an overview section (the paper says Codex and Qwen Code generation prompts instruct it) — https://arxiv.org/html/2602.11988; the paper's data say it does not help. The Claude Code prompt only advocates a high-level overview per the same paper; Anthropic's best-practices page excludes file-by-file descriptions. No dispute between sources on the facts; it is a dispute between practice and measurement.
- 2602.11988 versions differ: the OpenReview abstract says context files "tend to reduce task success rates" (https://openreview.net/forum?id=0DyJeJ3iia) while the arXiv abstract says "does not generally improve" (https://arxiv.org/abs/2602.11988). Both agree on cost; earlier wave quote M29 uses the "reduce" wording.

### Inferences
- The paper tests repo-internal overviews on Python benchmarks with discoverable structure. John's engineer faces systems with external SaaS, credentials, and undocumented manual steps; that is non-discoverable, which the paper itself says context files are for. Transfer is plausible but untested (mine).
- Design rule (mine): the agent-facing map holds only what grep cannot find: external systems, who owns what, where credentials live (names only), which links are confirmed. No directory listings. Load by path from the plan, not from CLAUDE.md.

### Gaps
- No study found of context files for non-code (SaaS, no-code) systems.
- Models in the paper (Sonnet-4.5, GPT-5.x, Qwen3) are not the current Sonnet 5.5; effect on current models unknown.

## The system-map skill: today and gaps

### Takeaway
Today the skill draws small Mermaid C4-style flowcharts and sequence diagrams from what it was told or read, saves them to docs/diagrams with an index row, and runs a render check if present. It cannot yet produce the brief's as-is and to-be diagrams, an agent-readable counterpart, a drift check, or a dark theme. Confidence: high (file read in full).

### Cited findings
- What it produces — /home/user/Autonomy-Research/plugin/skills/system-map/SKILL.md:3 — Quote: "Produces C4 context and container levels as flowcharts, and sequenceDiagram for flows, one concern per small .mmd file in docs/diagrams/"
- Size limit and split rule — /home/user/Autonomy-Research/plugin/skills/system-map/SKILL.md:15-16 — Quote: "keep each under about 25 lines."
- Evidence rule: omit unconfirmed — /home/user/Autonomy-Research/plugin/skills/system-map/SKILL.md:23-25 — Quote: "If a part or link is not confirmed, it shall omit it and list the question in `research/open-questions.md`."
- Validation if present — /home/user/Autonomy-Research/plugin/skills/system-map/SKILL.md:21-22 — Quote: "When `tests/check-mermaid.sh` exists, the skill shall run it on the directory and fix any failure before reporting."
- Inputs are only the user's pointers — /home/user/Autonomy-Research/plugin/skills/system-map/SKILL.md:28-31 — Quote: "Read the sources the user points at; use `researcher` workers for anything external so fetched pages stay out of the lead."
- The checker verifies link-in-index, first-line type, and render, not content — /home/user/Autonomy-Research/tests/check-mermaid.sh:8-11 — Quote: "does not render with mermaid-cli."
- The checker rejects anything but flowchart/graph/sequenceDiagram — /home/user/Autonomy-Research/tests/check-mermaid.sh:46 — Quote: "*) fail "$n starts with '$first'; only flowchart or sequenceDiagram are allowed" ;;"
- No theme config exists in skill, tests or docs/diagrams (grep for "theme" and "dark" in tests/, docs/diagrams/ and plugin/skills/ returned nothing) — checked 2026-10-16, Bash grep — Quote: "(no output)"
- Shareable render link is optional and lead-only — /home/user/Autonomy-Research/plugin/skills/system-map/SKILL.md:48-51 — Quote: "The `.mmd` file in the repo is the deliverable, and tests/check-mermaid.sh is the check."

### Contradictions
- None found.

### Inferences (concrete gaps; no edit made)
1. No as-is input contract. The skill says "read the sources the user points at"; it should take the as-is map (earlier wave: C4 context plus container with `path:line` facts and confidence tags) and the plan as named inputs and draw only facts carrying a citation.
2. No to-be or change view. The brief needs "what exists now" versus "what will change". Needed: a convention for marking added/changed/removed nodes (for example `classDef` new/changed/removed plus a legend) in a second file set, or a diff of two model states.
3. No single text model. It writes only `.mmd`. For the split above it needs a source file (nodes, edges, status, owner, evidence refs) with .mmd generated from it, and a check that every id in every .mmd exists in the model.
4. No agent counterpart output. Needed: the model file plus a short "what the agent must not touch / must preserve" list and the non-discoverable facts, written to a path the plan references, kept out of CLAUDE.md.
5. Validation is render-only. Add: node/edge parity with the model, every edge has a label, every external system has an evidence ref, and the 25-line cap enforced by script (currently prose only).
6. No dark theme. Needed: an init directive or a config file passed to mmdc (`-c`) and a background colour, a fixed palette with `classDef` for system/external/store/new/changed, and a contrast check; the checker renders with default theme so a dark-mode problem would not be caught. Mermaid dark-theme syntax was not researched in this facet.
7. No human-view rendering. John reads pictures, but the skill outputs `.mmd` only. Need a step producing SVG/PNG (the checker already renders to a temp dir that is deleted) and a stable place to open it, plus the one-page brief layout (other facet).
8. Sequence diagram rules cover only the semicolon; no rule for numbering steps, naming the actor who is John (approval points), or marking manual steps, which the brief probably needs.
9. Unconfirmed items go to `research/open-questions.md`, which is the research repo's file; in an engineer workspace the target path is wrong and needs a parameter.
10. Checker not run by default: tests/check.sh does not run it (tests/check-mermaid.sh:2-3), so "validated" depends on someone running it by hand.

### Gaps
- Dark theme specifics (Mermaid theme variables, contrast for flowchart subgraphs) not researched.
- Whether mermaid-cli renders offline in the engineer environment was not tested (checker uses npx at a pinned version).

## Recommendation, alternatives, rejected, spikes

### Takeaway
Recommend: one small text model per system (YAML or JSON in git, written by the engineer, confirmed by John), Mermaid views generated from it for John, the same model read by path by the agent; extend system-map to take the as-is map and plan as inputs and add model-parity checks and a dark theme. Do not put the overview in CLAUDE.md.

Alternatives: (a) Structurizr DSL workspace plus its free MCP export to Mermaid, if model rules and consistency matter more than simplicity; (b) hand-kept Mermaid as source with the agent reading the .mmd directly (simplest, no parity check possible); (c) image plus text together for UI work only.

Rejected: image-only diagrams as the agent's spec (GITA, 2409.08864: image alone insufficient); directory overview in AGENTS.md/CLAUDE.md (2602.11988); LLM-generated diagrams accepted unchecked (65% completeness in the UML study, over-inclusion in DiagramEval).

Must spike before building: (1) give the engineer the same change twice, once from model file and once from the rendered image, on one of John's real systems, and score against a fixed checklist; (2) run the parity check on a model of one real system and see whether the engineer keeps the model updated across three changes; (3) render a dark-theme diagram through the pinned mmdc and view it; (4) Structurizr MCP export to Mermaid without Java, if option (a) is wanted.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Structurizr DSL | https://docs.structurizr.com/as-code | Text C4 model with generated views, JSON compiled form, export to Mermaid/PlantUML | local (Java tooling) | 2026-10-16 | Fallback: use if model rules matter; spike runtime cost |
| Structurizr MCP server | https://docs.structurizr.com/ai/mcp | Free OSS MCP: DSL parse/validate to JSON workspace, Mermaid and PlantUML export; hosted instance at mcp.structurizr.com | standalone or hosted | 2026-10-16 | Fallback; hosted instance would send DSL to a third party, use standalone; not run |
| Code-Vision benchmark | https://arxiv.org/html/2502.11829 | Flowchart-to-code benchmark with image versus Mermaid input | dataset | 2026-10-16 | Evidence; possible harness for the text-versus-image spike |
| FlowVQA / FlowLearn / GITQA | https://aclanthology.org/2024.findings-acl.78.pdf | Flowchart and graph VQA benchmarks | datasets | 2026-10-16 | Evidence only |
| FlowSight dataset | https://github.com/herbit2004/FlowSight-Dataset | Mermaid source, PNG, description and QA per architecture diagram | local Python, OpenRouter key | 2026-10-16 (search text only) | Skip; not opened beyond search text |
| DiagramEval | https://aclanthology.org/2025.emnlp-main.640.pdf | Graph-based node/path metric for LLM diagrams | research code | 2026-10-16 | Idea: node/path F1 as a parity check against the model |
