# Engineer briefing: a three-page dark-theme brief for John and a machine-oriented counterpart for the agent

John's brief should be one Markdown source of at most three pages, made into a dark-theme claude.ai page. The engineer writes a before-brief and an after-brief with the same skeleton.

**Page 1** gives a two-line "what and why", then one plain Mermaid flowchart drawn at C4 system-context level, with a numbered list of the same flow underneath.
- C4 says the context diagram is for "Everybody, both technical and non-technical people" (https://c4model.com/diagrams/system-context).
- Every diagram needs a key/legend and every line a label (https://c4model.com/diagrams/notation).
- Untrained readers did best with a written version followed by the diagram (https://doi.org/10.1016/j.jss.2011.09.023).

**Page 2** covers the stack, where each key lives (names only) and what John will see. **Page 3** covers what John must do, what is not being done, risks and costs. Explain-back prompts close each page.
- These page contents are worker inference built on several sources: Amazon's length cap as a "forcing function" (https://www.aboutamazon.com/news/workplace/an-insider-look-at-amazons-culture-and-processes), Shape Up's no-gos (https://basecamp.com/shapeup/1.5-chapter-06), Google's "1-3 page 'mini design doc'" (https://www.industrialempathy.com/posts/design-docs-at-google/) and the teach-back method (https://www.health.tas.gov.au/professionals/health-literacy/health-literacy-workplace-toolkit/spoken-communication/checking-understanding).

**Toolchain.** Mermaid source is committed as text and gated by mermaid-lint (https://github.com/jasonworden/mermaid-lint). mermaid-cli renders it to SVG with `-t dark` (https://github.com/mermaid-js/mermaid-cli). The SVG is inlined in a published artifact page, because the artifacts page says "Prefer SVG, or HTML and CSS, for diagrams" and allows scripts only from listed CDNs (https://code.claude.com/docs/en/artifacts).
- **Cross-area point for the blueprint:** "Sessions using an API key, gateway token, or cloud-provider credential cannot publish" (https://code.claude.com/docs/en/artifacts). An unattended API-key or `claude -p` engineer must therefore commit the brief files, and an interactive `/login` session (or John) must publish them.

**Agent counterpart.** The agent gets text, not a picture.
- Flowcharts given as Mermaid beat the same flowcharts given as images for most models (https://arxiv.org/html/2502.11829).
- Visual-only input is worse than text-only on average (https://arxiv.org/html/2402.02130v3).
- One dissenting study favours images for large graphs (https://aclanthology.org/2024.findings-naacl.34/).
- The workers recommend a small YAML or JSON model holding only facts that cannot be found by reading the code. The agent reads it by path. Mermaid views are generated from it, and it is kept out of CLAUDE.md. This follows two sources: context files that give a repository overview did not raise success and added over 20% cost (https://arxiv.org/html/2602.11988), and Claude Code's guidance is to keep CLAUDE.md to things that apply broadly (https://code.claude.com/docs/en/best-practices).

**system-map skill.** It produces only `.mmd` files with no theme (/home/user/Autonomy-Research/plugin/skills/system-map/SKILL.md:3). It needs an as-is input contract, a to-be view, a text model with a parity check, a dark theme and a rendered view.

Overall confidence: medium. Nothing has been tested on John's phone or on the 2026 models.

## Questions and answers

### Q1. Which diagram types do non-technical readers understand?

**Confidence: medium.** Most of the evidence is 2011-2017 student and practitioner studies plus Simon Brown's guidance. No study covers phone screens.

**Use a C4 system-context-style picture.** It shows people, the system and the outside services.
- C4 states its audience as "Everybody, both technical and non-technical people, inside and outside the software development team." (https://c4model.com/diagrams/system-context). Detail is deliberately low (same URL).
- "the system context and container diagrams are sufficient for most software development teams." (https://c4model.com/diagrams).
- Brown calls it "the sort of diagram that you could show to non-technical people." (https://www.infoq.com/articles/agile-software-architecture-sketches-NoUML/).
- Google's design-doc guidance says "a system-context-diagram can be very useful" (https://www.industrialempathy.com/posts/design-docs-at-google/).

**Notation rules.**
- Every diagram has a key/legend, every line a label, and acronyms all audiences understand (https://c4model.com/diagrams/notation).
- A diagram must stand alone: "give it to somebody else and ask them to interpret it without providing a narrative." (https://leanpub.com/read/visualising-software-architecture/failure-to-communicate).
- Brown recommends keeping "A version without technical information, for non-technical people." (https://dev.to/simonbrown/visio-draw-io-lucidchart-gliffy-etc-not-recommended-for-software-architecture-diagrams-4bmm).

**Text first, then the diagram.**
- For untrained readers, "BPMN on its own is not a sufficient way to present process designs". A written use case followed by the diagram "was the most effective way to build up comprehension" (https://doi.org/10.1016/j.jss.2011.09.023).

**Skip sequence diagrams and swimlanes on John's pages.**
- Sequence diagrams helped only "high ability and more experienced participants" (https://doi.org/10.1109/tse.2012.27).
- Non-swimlane diagrams were "more effective overall" and swimlanes "more efficient" (https://jitm.ubalt.edu/XXV-4/article3.pdf).
- Worker inference: keep these diagram types in the engineer's own architecture file.

**Size.**
- Understandability peaked at "middle values of the number of components, links, elements, and symbols". The authors call their thresholds "rough indicators" (https://eprints.cs.univie.ac.at/4059/1/Empirical_Evaluation_of_the_Understandability_of_Architectural_Component_Diagrams.pdf; the quote is from Exa search text because the PDF could not be extracted).
- A companion study favours one component per "relevant functionality" (https://doi.org/10.1109/qsic.2014.20).
- Worker inference (not in the source): about 6-9 boxes per diagram for John, split into two diagrams rather than exceed that.

**Contradictions.** The two swimlane studies point different ways:
- Swimlane diagrams were less effective than non-swimlane ones (https://jitm.ubalt.edu/XXV-4/article3.pdf).
- Diagrams, swimlanes included, beat prose for civil servants: "the diagrammatic format, compared to prose, significantly enhances comprehension accuracy and answering speed" (https://doi.org/10.1177/1050651917746459).

The readers and tasks differ. Both results support a diagram plus text over prose alone, but neither settles swimlanes for John. **Unresolved**, and listed under Open questions.

The node-count targets also disagree, and all of them are inferences:
- about 6-9 boxes (template note);
- about 10-15 nodes, "well under 30" (toolchain note);
- under about 25 lines (/home/user/Autonomy-Research/plugin/skills/system-map/SKILL.md:15-16).

No opened source gives a number for phone screens. Spike it.

### Q2. What goes on each of the three pages, how is explain-back built in, and how does the after-brief differ?

**Confidence: medium.** The sources support short, length-capped narratives that stand alone and state their exclusions. None prescribes this exact split.

**Length and audience.**
- Amazon caps narratives "to a maximum of six pages" so that "anybody within your organization can read and understand it" (https://aws.amazon.com/blogs/startups/startup-advice-how-to-write-a-narrative/).
- Amazon's PR section is "always less than one page", and length is "a forcing function" (https://www.aboutamazon.com/news/workplace/an-insider-look-at-amazons-culture-and-processes).
- Google allows a "1-3 page 'mini design doc'" for smaller changes and says "non-goals aren't negated goals" (https://www.industrialempathy.com/posts/design-docs-at-google/).
- Shape Up names five pitch ingredients, including no-gos: "Anything specifically excluded from the concept" (https://basecamp.com/shapeup/1.5-chapter-06).

**Page layout (template-note worker inference).**

| Page | Before-brief | After-brief |
|---|---|---|
| 1 | "In one sentence" what and why; one context diagram (legend, verb on every arrow); 5-8 numbered flow steps | "What was built": the as-built diagram drawn from the code, changed boxes marked through the legend, not colour alone; same diagram ids as the before-brief |
| 2 | Stack table (part, what it does, who pays); where each key lives (name and location only, never the value); what John will see, in the words he will see | "What differs from the plan": planned, actual, why, cost impact; what John now sees |
| 3 | "What I need from you" checklist with dates; "Not doing"; risks and open questions, each with what the engineer will do if it happens; monthly and one-off cost; the Shape Up appetite as a one-line time and cost budget | "What to watch": renewals and expiring keys, actual against estimated monthly cost, known limits, who to ask, how to switch it off |

**The after-brief.**
- It follows closeout templates: "INITIAL GOALS AND DELIVERABLES ACTUAL GOALS AND DELIVERABLES EXPLANATION OF VARIANCE" (https://www.smartsheet.com/sites/default/files/2023-08/IC-Project-Closeout-11813_PDF.pdf).
- "Compare baselines to actual and describe discrepancies." The template is to be "brief, but provide enough detail so that any person not familiar with the project will have the necessary information" (https://portal.ct.gov/-/media/Departments-and-Agencies/DSS/CT-METS/Library/General/CTDSSProjectCloseoutReportv11.pdf).
- Worker inference: an after-brief must be built from observed facts (tests run, URLs live) and mark anything unverified.

**Explain-back (worker inference, adapted from health literacy).**
- End each page with 2-3 "In your own words" prompts that John answers in chat. The engineer rewrites any passage he gets wrong.
- The method's framing is "This isn't a test of the consumer's knowledge; it's a test of how well you've communicated." It also says teach-back "works better than asking 'yes' and 'no' questions" and advises to "'Chunk' your information into small sections." (https://www.health.tas.gov.au/professionals/health-literacy/health-literacy-workplace-toolkit/spoken-communication/checking-understanding).
- No source tests teach-back on software briefs.

**What John signs.** The earlier plan-set note has John sign "(a) goals and non-goals, (b) scope list in plain words, (c) acceptance criteria as observable outcomes" (/home/user/Autonomy-Research/research/runs/engineer-planning/notes/plan-set.md:106). Worker inference: the before-brief should be the file John approves under that approval hash, and the after-brief is generated from it so the two can be diffed.

**Contradictions.** The earlier planning findings size the owner-facing `brief.md` at "Prose, 1-2 pages" (/home/user/Autonomy-Research/research/findings/engineer-planning.md:44). That size was worker inference in that run. John's requirement is at most three pages.
- The evidence favours John's cap. The three-page template replaces the 1-2 page size, and `brief.md` keeps its role as the signed file.
- Synthesizer inference: the two are compatible if the signed parts (goals, scope, acceptance, costs, gates) sit on pages 1 and 3.

The length sources differ (six pages, under one page, 1-3 pages, all cited above), but none is written for a phone. The three-page cap is a design choice, not a conflict.

### Q3. Dark theme and readability on a phone

**Confidence: medium on the contrast floors, low on dark-versus-light polarity and on phone font sizes.**

**Contrast floors.**
- Text needs "a contrast ratio of at least 4.5:1", or 3:1 for large-scale text (https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html).
- Graphics need "at least 3:1 against adjacent color(s)", including "Parts of graphics required to understand the content" (https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html). This covers diagram borders and arrows.

**Polarity.** "Under dark illumination, white-on-black text suffers a legibility disadvantage", and "This disadvantage is more pronounced as text size decreases." (https://www.sciencedirect.com/science/article/abs/pii/S0003687016302459, Dobres et al. 2017).

**Colour.**
- The Okabe-Ito palette is colour-blind friendly (https://siegal.bio.nyu.edu/color-palette/). The note lists its hues #E69F00, #56B4E9, #009E73, #F0E442, #0072B2, #D55E00 and #CC79A7.
- Colour must not be the only cue: "Can you work out what the colour coding means?" (https://leanpub.com/read/visualising-software-architecture/failure-to-communicate).

**Worker inference (not in the source):**
- a background around #121212 to #1A1D23, not pure black;
- body text about #E6E6E6, aiming for 7:1 or more;
- diagrams rendered top-to-bottom at 390 px width so text is at least 14-16 px;
- a light-theme print or PDF export from the same source.

None of these values or contrast ratios was computed or tested.

**Contradictions.** The template note sets Dobres 2017 (white-on-black harder to read in dim light) against Tai et al. 2013, which found negative polarity preferred (https://doi.org/10.1167/13.9.1157). The Tai claim was seen only in Exa search text, so it is excluded as evidence and the disagreement cannot be weighed here.
- Evidence on hand: only Dobres. That favours dark as John's stated preference but with a large body size and high contrast, and a quick check on his phone in his usual lighting.
- **Unresolved.** Listed under Open questions.

The note's "17 pt body" figure comes from a search-text mirror of Apple's HIG and is excluded (see Open questions).

### Q4. Toolchain: rendering where John reads, dark theme and validation

**Confidence: medium.** The GitHub, artifact, Mermaid and D2 facts come from opened sources. Whether Mermaid renders in project files or in the Claude app on a phone was not found.

**Mermaid is the default format.**
- GitHub renders Mermaid. Its docs say "You can create diagrams in Markdown using four different syntaxes: mermaid, geoJSON, topoJSON, and ASCII STL." That quote came from an Exa excerpt of the page; the WebFetch of the page returned "Diagram rendering is available in GitHub Issues, GitHub Discussions, pull requests, wikis, and Markdown files." (https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams).
- GitHub picks its own Mermaid version: "check the Mermaid version currently in use" (same URL).

**Published claude.ai pages (artifacts).**
- Scripts may come only from "cdnjs, unpkg, the Tailwind and jQuery CDNs, and selected paths on jsDelivr such as `/npm/`".
- The page says to "Prefer SVG, or HTML and CSS, for diagrams over embedded raster images".
- "Markdown files render as styled document pages with syntax-highlighted code". The page does not say that Mermaid fences render.
- All three: https://code.claude.com/docs/en/artifacts.
- Worker inference: pre-rendered SVG inlined in the page is safer than client-side Mermaid, and dark theme then becomes a build parameter.

**Publishing needs a login (cross-area point).** "Sessions using an API key, gateway token, or cloud-provider credential cannot publish." (https://code.claude.com/docs/en/artifacts).
- Worker inference: an unattended `claude -p` engineer commits SVG and Markdown to the repo, and an interactive or Remote Control session (or John) publishes the page.

**Dark theme.**
- Mermaid has a dark theme that "goes well with dark-colored elements or dark-mode", but "the only theme that can be customized is the base theme." (https://mermaid.js.org/config/theming.html).
- mermaid-cli renders with "mmdc -i input.mmd -o output.png -t dark -b transparent". It depends on `"puppeteer": "^25.0.0"`, a headless browser (https://github.com/mermaid-js/mermaid-cli (clone, commit f416ac5) package.json:47).
- On GitHub, a user reported on 2026-04-29 (no GitHub reply) that dark Mermaid "is still broken when dark mode is implied by system setting." (https://github.com/orgs/community/discussions/194348).
- Worker inference: a neutral or mid-tone theme for committed Mermaid shown on GitHub. This was not tested.

**Validation.** mermaid-lint uses the real parser and "only requires Node.js ≥22 and runs via `npx`". It exits "`0` = all valid · `1` = validation failures (or warnings with `--strict`) · `2` = usage/IO error" (https://github.com/jasonworden/mermaid-lint).

**Second tool: D2.**
- "D2 supports SVG, PNG, GIF, PDF, and PPTX exports." "Open sourced under the Mozilla Public License 2.0." (https://github.com/terrastruct/d2 (clone, commit 6a7b483 dated 2026-10-11)).
- It has a dark-theme flag used "when the viewer's browser is in dark mode", SVG only, and a `validate` subcommand (d2cli/main.go:101 and :213, commit 6a7b483).
- It bundles "A native Go port of the ELK directed graph layout engine" (https://github.com/terrastruct/d2).

**Other candidates.**
- Structurizr is a "\"models as code\" tool designed for the [C4 model](https://c4model.com)", with exporters for mermaid, plantuml, dot and ilograph (https://github.com/structurizr/structurizr (clone, commit da99caf) README:3).
- PlantUML is "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007" (https://github.com/plantuml/plantuml (clone, commit 09c9256) LICENSE:1-2).
- Kroki is "MIT License" (https://github.com/yuzutech/kroki (clone, commit 96acbf8) LICENSE:1). Mermaid needs "companion containers" (https://docs.kroki.io/kroki/setup/install/).
- Excalidraw is "MIT License" (https://github.com/excalidraw/excalidraw (clone, commit 4c37956) LICENSE:1).

**Contradictions.** None found in this run. The toolchain note points to an earlier disagreement on whether GitHub renders Mermaid C4 (research/findings/engineer-feasibility.md:22). That is not re-settled here; using a plain flowchart avoids the question.

### Q5. Generating diagrams from code and configuration, keeping them current, and render limits

**Confidence: medium on generators and the CI pattern. High on the Mermaid limits as Mermaid defaults; it is less certain that GitHub applies the same limits.**

**Generators.** Treat their Mermaid output as a draft: validate it, check its size, then trim it by hand (worker inference).
- dependency-cruiser has a Mermaid reporter, but "the graph cannot be (made as) feature rich as those produced by the `dot` or `d2` reporters." (https://github.com/sverweij/dependency-cruiser (clone, commit c580daf, 2026-10-13) doc/cli.md:233-240).
- n8nmermaid "Converts n8n workflow JSON files into Mermaid flowchart syntax (V2)". It is MIT and its last commit was 2026-06-11 (https://github.com/jwa91/n8nmermaid (clone, commit 8aaf7dc) README.md:5).
- docker-compose-to-mermaid is "**Fully offline** — no external APIs, no paid services required". It is MIT and its last commit was 2026-03-14 (https://github.com/TamirTapiro/docker-compose-to-mermaid (clone, commit 311e116) README.md:14).

Worker inferences:
- n8n to Mermaid is a deterministic transform, so a short script is an alternative to adding a dependency.
- OpenAPI sequence diagrams stay LLM-written, then linted.
- Python import graphs go through Graphviz dot.

The OpenAPI (Hidi) and Terraform generators were seen only in search excerpts and are excluded (Open questions).

**Keeping diagrams current.**
- A real workflow fails the PR when generated diagrams are stale: `if [[ -n "$(git status --porcelain -- docs/diagrams)" ]]; then` (https://github.com/stackitcloud/stackit-landing-zone/blob/2dfc21ec702698d2806ee48cd0e001c4f561e98e/.github/workflows/generate-architecture-diagrams.yml).
- The earlier feasibility findings propose to "Put a parse gate (mermaid-lint) in a Stop or PostToolUse hook." (/home/user/Autonomy-Research/research/findings/engineer-feasibility.md:20).

Worker inferences:
- Gate on the Mermaid source text and regenerate SVGs on main. The reason given, that mermaid-cli output is not byte-stable, rests on an unopened excerpt, so it is a hypothesis to spike.
- Each generated diagram carries a header naming its generator command and input file.

**Limits.**
- Mermaid's defaults are "default: 50000" (maxTextSize) and "default: 500" (maxEdges) (https://github.com/mermaid-js/mermaid/blob/master/packages/mermaid/src/schemas/config.schema.yaml).
- A third-party doc says "GitHub, GitLab, and the Mermaid live editor all stop at 50,000 characters of diagram source". It calls splitting "The structural answer, and the only one that helps both limits at once." (https://docs.rcsc.dev/laravel-cartographer/v1/renderer-limits).
- "ELK is bundled and default from v12.0.0." (https://mermaid.ai/open-source/config/layouts.html). The GitHub ELK request is still waiting: "We're still waiting @github !! It's been two years" (https://github.com/orgs/community/discussions/138426).
- Worker inference: do not rely on ELK in committed Mermaid. Keep diagrams small enough that Dagre lays them out well.

**Contradictions.** The layouts page says ELK is the default from v12 (https://mermaid.ai/open-source/config/layouts.html). The toolchain note reports an older theming source saying the global default is `dagre`, but that source was seen only as an excerpt and is excluded. The note suggests version drift (v11 against v12). **Unresolved**, and listed under Open questions. It does not change the advice, because GitHub renders its own pinned version.

### Q6. What should the agent-facing counterpart be? Text versus image, and how much context

**Confidence: medium.** The evidence comes from 2024-2025 papers on older models. Several quotes come from Exa search text, which the worker rated one level weaker. No agentic-coding test exists.

**Text versus image.**
- In Code-Vision, "when using mermaid as input, most models exhibit performance improvements" (https://arxiv.org/html/2502.11829).
- Strong proprietary models still read images well: "On Hard problems, GPT-4o can achieve 79.3% pass@1, but the best open-source model only achieves 15%." (same URL).
- In GITA, "using the visual modality alone is worse than using the textual modality alone on average", and "combining textual and visual information together performs better than using one modality alone." (https://arxiv.org/html/2402.02130v3).
- "providing only graph visualisations, without accompanying textual descriptions, is insufficient for LLMs to fully comprehend graph structures." (https://arxiv.org/html/2409.08864).
- Reading images back is hard. Models "struggled with the more complex task of accurately generating Mermaid code from flowcharts." (https://doi.org/10.48550/arxiv.2407.05183). VLMs "struggled to execute visual and spatial reasoning tasks" (https://aclanthology.org/2024.findings-acl.78.pdf).

**The text encoding matters.**
- One task moved from 19.8% to 53.8% accuracy between two encodings of the same graph (https://proceedings.iclr.cc/paper_files/paper/2024/file/bf72f65f30eedf5d48da6980ee02b589-Paper-Conference.pdf).
- After instruction tuning, "JSON format for graph representation consistently outperforms natural language and code formats" (small tuned models; https://doi.org/10.48550/arxiv.2408.05457).

**Generated diagrams need checking.**
- Across seven LLMs, results vary by model: "some LLMs demonstrating strong syntax adherence, while others struggle with diagram structure and semantic accuracy." (https://doi.org/10.1016/j.procs.2025.09.191).
- LLM UML "consistently underperform compared to human-created diagrams" (https://doi.org/10.3390/info16070565).
- "Claude produces diagrams with 31.67 nodes on average" against 21.42 for Gemini (https://aclanthology.org/2025.emnlp-main.640.pdf).

**One model, many views.**
- Structurizr's case: "a collection of consistent views onto a single model". It can "export Structurizr views to “diagrams as code” formats such as PlantUML and Mermaid" (https://docs.structurizr.com/ai).
- The DSL is the source and the JSON is "not designed to be edited by hand" (https://docs.structurizr.com/workspaces/file-types).
- "AI agents have limited abilities to interact with UI-driven tools, but they can generate text" (https://docs.structurizr.com/as-code). The same page describes an agent that "periodically compares code or infrastructure against the Structurizr model and raises an alert when they diverge."
- "A free and open source Structurizr MCP server is available on GitHub." (https://docs.structurizr.com/ai/mcp).
- The DSL has "a slightly higher learning curve than a UI." (https://docs.structurizr.com/as-code).

**Where the counterpart lives.**
- "CLAUDE.md is loaded every session, so only include things that apply broadly. For domain knowledge or workflows that are only relevant sometimes, use skills instead." The guidance includes "Architectural decisions specific to your project" and excludes "File-by-file descriptions of the codebase" (https://code.claude.com/docs/en/best-practices).
- On benchmarks, "providing context files does not generally improve task success rates, while increasing inference cost by over 20% on average", and "context files are not effective at providing a repository overview." (https://arxiv.org/html/2602.11988).
- That study covers four agents, SWE-bench and 138 Python instances (https://arxiv.org/abs/2602.11988). It recommends that files "only include instructions required for coding agents that are not already present in the README" (same URL).

**Recommended counterpart (agent-counterpart worker inference).**
- A small `architecture.yaml` (or `.json`) per system holds named nodes, labelled edges, owner, store, credential name and confirmed or unconfirmed status. Mermaid views for John are rendered from it.
- The engineer updates it in the same commit as any system change. A check enforces that every Mermaid node id exists in the model.
- It holds only what grep cannot find (external systems, owners, credential names, confirmed links). The agent loads it by path from the plan, not through CLAUDE.md.
- Synthesizer inference: the earlier planning findings already define `integrations.yaml`, with purpose, auth type, env var name, price, owner action and fallback per service (/home/user/Autonomy-Research/research/findings/engineer-planning.md:47). The architecture model should reference those service entries by id rather than repeat them, so there is one source per fact.

**Contradictions.**
- *Image against text.* GraphTMI found "the image modality ... is superior to text in balancing token limits" for large graphs (https://aclanthology.org/2024.findings-naacl.34/). That disagrees with GITA (https://arxiv.org/html/2402.02130v3) and Code-Vision (https://arxiv.org/html/2502.11829). The evidence favours text for this use: John's brief diagrams are small, so GraphTMI's token-budget advantage does not apply. That reasoning is worker inference, and the models tested are GPT-4V era. Spike 4 tests it.
- *Model consistency.* Structurizr says "diagrams as code tools tools don’t understand the C4 model and don’t respect its rules." (https://docs.structurizr.com/ai). The repo's system-map skill uses plain Mermaid flowcharts and forbids C4 syntax (/home/user/Autonomy-Research/plugin/skills/system-map/SKILL.md:13-14). Structurizr is a vendor with a stake, and for one user Java tooling may cost more than it gives. **Unresolved**; spike before choosing Structurizr.
- *Practice against measurement on overviews.* The paper measures no gain from overviews (https://arxiv.org/html/2602.11988), while agent vendors' prompts recommend them. The note reports the vendor side without a quote, so it is in Open questions. The earlier finding left this open (/home/user/Autonomy-Research/research/findings/engineer-existing-systems.md:415). The evidence favours the measurement for repo-internal overviews. Whether it transfers to maps of external SaaS is untested (worker inference).

### Q7. What does the system-map skill need?

**Confidence: high on what it does today** (files read in full). The list of gaps is worker inference.

**What it does today.**
- It "Produces C4 context and container levels as flowcharts, and sequenceDiagram for flows, one concern per small .mmd file in docs/diagrams/" (/home/user/Autonomy-Research/plugin/skills/system-map/SKILL.md:3).
- Each diagram is kept "under about 25 lines." (:15-16).
- Unconfirmed parts are omitted and listed in `research/open-questions.md` (:23-25).
- It runs `tests/check-mermaid.sh` when that file exists (:21-22).
- It reads only "the sources the user points at" (:28-31).
- The `.mmd` file is the deliverable (:48-51).
- The checker verifies the index link, the first-line type and the render, not content: "does not render with mermaid-cli." (/home/user/Autonomy-Research/tests/check-mermaid.sh:8-11). It rejects anything but flowchart or sequenceDiagram (:46).
- A grep for "theme" and "dark" in tests/, docs/diagrams/ and plugin/skills/ returned "(no output)".

**Gaps (agent-counterpart worker inference).**
1. No as-is input contract. It should take the as-is map and the plan as named inputs and draw only cited facts.
2. No to-be or change view. It needs `classDef` new, changed and removed classes plus a legend, or a diff of two model states.
3. No single text model. It needs a model file with `.mmd` generated from it, and a check that every id exists in the model.
4. No agent counterpart output. It needs the model, a "must not touch / must preserve" list and the facts the code does not show, written to a path the plan references.
5. Validation only renders. It needs node and edge parity with the model, a label on every edge, an evidence reference on every external system, and the 25-line cap enforced by script.
6. No dark theme. It needs an init directive or an `mmdc -c` config, a background colour, a fixed `classDef` palette and a contrast check.
7. No human view. It needs SVG or PNG output kept in a stable place; the checker's render goes to a temp dir that is deleted.
8. Sequence rules cover only the semicolon. Numbering, John as an actor at approval points, and manual steps are not covered.
9. The open-questions path is hard-coded to the research repo. It needs a parameter for engineer workspaces.
10. The checker does not run by default: tests/check.sh does not call it (/home/user/Autonomy-Research/tests/check-mermaid.sh:2-3).

### Q8. Recommendation, alternatives, rejected candidates and what to spike

**Confidence: medium.**

**Recommendation.** Claude Code stays the engine. All of the following are free; there is no paid option and no service to host.

*Brief.*
- The format is a three-page `brief.md`, laid out per Q2: before and after versions with the same skeleton, explain-back prompts, and the signed parts on pages 1 and 3.
- Each diagram is a plain Mermaid flowchart at C4 context level for John: legend, a verb on every arrow, a numbered text flow beside it, Okabe-Ito colours plus shape or label redundancy, and borders at 3:1 or better against the background.

*Pipeline.*
- The engineer writes Mermaid source and checks it with mermaid-lint, in a hook or CI.
- It renders dark SVG with a pinned mermaid-cli (`-t dark`, or `base` with `themeVariables`).
- It commits source and SVG. CI regenerates any generated diagrams and fails if `git status --porcelain` shows a change.
- An interactive `/login` session publishes the brief as a claude.ai page with the SVG inlined, following the artifacts page's own "Prefer SVG" advice. An unattended API-key or `-p` run cannot publish (https://code.claude.com/docs/en/artifacts).

*Agent counterpart and skill.*
- The counterpart is a small YAML model of the system with only the facts the code does not show, read by path and kept out of CLAUDE.md. Mermaid views are generated from it and a parity check runs on every commit.
- Extend the system-map skill with the ten items in Q7.

**Alternatives.**
- **D2** for a polished architecture SVG (MPL-2.0, `validate`, dark-theme flag; https://github.com/terrastruct/d2). It adds a render step, and GitHub's text view would be lost (worker inference).
- **Client-side Mermaid** loaded from jsDelivr `/npm/` in the artifact page (https://code.claude.com/docs/en/artifacts) instead of pre-rendered SVG. Worker inference: less safe than inline SVG.
- **Structurizr DSL** plus its free MCP export to Mermaid (https://docs.structurizr.com/ai/mcp), if C4 model rules matter more than simplicity. It needs Java tooling (https://github.com/structurizr/structurizr).
- **Hand-kept Mermaid as the source**, with the agent reading the `.mmd` directly. It is the simplest, but a parity check is not possible (worker inference).
- **Image plus text together** for UI review tasks only (https://arxiv.org/html/2402.02130v3).
- **Generators:** dependency-cruiser, n8nmermaid and docker-compose-to-mermaid, or the engineer's own small transform scripts.

**Rejected, with reasons.**

| Candidate | Reason |
|---|---|
| PlantUML as default | GPL-3.0 among its licences, Java (https://github.com/plantuml/plantuml LICENSE:1-2); not among GitHub's four rendered syntaxes (https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams, quote from an Exa excerpt) |
| Kroki | Adds a service; Mermaid needs companion containers (https://docs.kroki.io/kroki/setup/install/) |
| Excalidraw for agent-written docs | JSON scene, not text-diffable (worker verdict; only the licence was opened, https://github.com/excalidraw/excalidraw) |
| Eraser | Paid SaaS, rejected on the free-first rule; no page opened (Open questions) |
| Mermaid C4 syntax | Experimental; already rejected (/home/user/Autonomy-Research/research/findings/engineer-planning.md:255) |
| Sequence diagrams and swimlanes on John's pages | Help only experienced readers (https://doi.org/10.1109/tse.2012.27); swimlanes less effective (https://jitm.ubalt.edu/XXV-4/article3.pdf) |
| Image-only diagrams as the agent's spec | Image alone is insufficient (https://arxiv.org/html/2409.08864, https://arxiv.org/html/2402.02130v3) |
| Overview in CLAUDE.md or AGENTS.md | No gain and over 20% cost (https://arxiv.org/html/2602.11988); best practices exclude file-by-file descriptions (https://code.claude.com/docs/en/best-practices) |
| LLM-generated diagrams accepted unchecked | Below human quality (https://doi.org/10.3390/info16070565); over-inclusion (https://aclanthology.org/2025.emnlp-main.640.pdf) |
| Gating merges on rendered SVG bytes | Worker inference from an unopened excerpt about byte instability; gate on source text until spike 7 settles it |
| ELK layout in committed Mermaid | GitHub has not adopted it (https://github.com/orgs/community/discussions/138426) |

**Spikes, before building.**
1. Do Mermaid fences in claude.ai project files, and in a published page, render in the Claude app on John's phone? Compare with inline SVG. No source was found.
2. Render a dark-theme diagram through a pinned mermaid-cli in the cloud environment (headless Chromium). Compute contrast for the chosen colours. View it on John's phone in his usual lighting, against a light version.
3. Explain-back: John reads one real three-page brief on his phone and explains each page. Time it and count the passages that had to be rewritten.
4. Text against image: give the engineer the same change twice, once from the model file and once from the rendered image, on one of John's systems. Score against a fixed checklist.
5. Model parity: run the parity check on a model of one real system, and see whether the engineer keeps the model updated across three changes.
6. Node count on the phone: compare 6-9, 10-15 and about 25-line diagrams for legibility without pinch-zoom.
7. Is mermaid-cli SVG output byte-stable across two environments?
8. Run n8nmermaid and docker-compose-to-mermaid on John's real n8n workflows and compose files.
9. Publishing hand-off: an unattended run commits the brief, and an interactive or Remote Control session publishes it. Confirm that the `/login` requirement holds and that the hand-off works.
10. Read GitHub's current Mermaid version with the snippet its docs provide.
11. Only if the Structurizr alternative is wanted: Structurizr MCP export to Mermaid without a local Java install.

## Evidence

All sources were opened on 2026-10-16. "Exa search text" means the note lists the page as opened but the quote came from page text that Exa returned in search; the worker rated these one level weaker than a fetch.

**Diagrams for non-technical readers**
- E1. https://c4model.com/diagrams/system-context — 2026-10-16 — WebFetch — C4 system context is meant for everyone. Quote: "Everybody, both technical and non-technical people, inside and outside the software development team."
- E2. https://c4model.com/diagrams/system-context — 2026-10-16 — WebFetch — Detail is deliberately low at context level. Quote: "Detail isn’t important here as this is your zoomed out view showing a big picture of the system landscape."
- E3. https://c4model.com/diagrams — 2026-10-16 — WebFetch — Different levels for different audiences; context + container suffice for most. Quote: "the system context and container diagrams are sufficient for most software development teams."
- E4. https://c4model.com/diagrams/notation — 2026-10-16 — WebFetch — Notation rules: title, legend, labelled lines, readable acronyms. Quote: "Every diagram should have a key/legend explaining the notation being used."
- E5. https://c4model.com/diagrams/notation — 2026-10-16 — WebFetch — Line labels. Quote: "Every line should be labelled, the label being consistent with the direction and intent of the relationship."
- E6. https://c4model.com/diagrams/notation — 2026-10-16 — WebFetch — Acronyms. Quote: "Acronyms and abbreviations (business/domain or technology) should be understandable by all audiences."
- E7. https://leanpub.com/read/visualising-software-architecture/failure-to-communicate — 2026-10-16 — Exa — Brown's list of failure modes of boxes-and-arrows (unexplained colour, mixed abstraction, missing context). Quote: "Notation (e.g. colour coding, shapes, line styles, etc) is not explained or is inconsistent."
- E8. https://leanpub.com/read/visualising-software-architecture/failure-to-communicate — 2026-10-16 — Exa — Stand-alone test (give it to someone, no narrative). Quote: "give it to somebody else and ask them to interpret it without providing a narrative."
- E9. https://leanpub.com/read/visualising-software-architecture/failure-to-communicate — 2026-10-16 — Exa — Notation: colour alone is ambiguous. Quote: "Can you work out what the colour coding means?"
- E10. https://www.infoq.com/articles/agile-software-architecture-sketches-NoUML/ (2013) — 2026-10-16 — Exa — Brown on the context diagram for non-technical people, and a legend like a map key. Quote: "It's the sort of diagram that you could show to non-technical people."
- E11. https://www.infoq.com/articles/agile-software-architecture-sketches-NoUML/ — 2026-10-16 — Exa — Same page. Quote: "Including a simple key/legend on each diagram to explain the notation will help too."
- E12. https://dev.to/simonbrown/visio-draw-io-lucidchart-gliffy-etc-not-recommended-for-software-architecture-diagrams-4bmm (2020) — 2026-10-16 — Exa — Brown: keep a technical and a non-technical variant of the same diagram, plus a large-font version. Quote: "A version without technical information, for non-technical people."
- E13. https://www.industrialempathy.com/posts/design-docs-at-google/ — 2026-10-16 — WebFetch — Google design docs: system-context diagram is useful; docs must be short. Quote: "a system-context-diagram can be very useful"
- E14. https://doi.org/10.1016/j.jss.2011.09.023 (2011) — 2026-10-16 — Exa — Business-process study (BPMN vs written use cases, 196 participants): untrained readers did not gain from the graphic alone; text first then diagram worked best. Quote: "BPMN on its own is not a sufficient way to present process designs, despite its success among those with training in process models."
- E15. https://doi.org/10.1016/j.jss.2011.09.023 — 2026-10-16 — Exa — Same paper: ordering. Quote: "presenting a business process twice, in the sequence of a written use case set followed by its equivalent set of BPMN diagrams, was the most effective way to build up comprehension"
- E16. https://jitm.ubalt.edu/XXV-4/article3.pdf — 2026-10-16 — Exa — Swimlanes (142 and 131 student responses): non-swimlane more effective, swimlane faster; handshake steps and visual cues help. Quote: "non-swimlane diagrams are more effective overall in conveying information to stakeholders, but that swimlane diagrams are more efficient"
- E17. https://doi.org/10.1109/tse.2012.27 (2013) — 2026-10-16 — Exa — UML sequence diagrams help only high-ability/experienced readers (112 participants, five experiments). Quote: "sequence diagrams improve the comprehension of the modeled functional requirements in the case of high ability and more experienced participants."
- E18. https://doi.org/10.1177/1050651917746459 (2017) — 2026-10-16 — Exa — Diagrams beat prose for procedure-style content in a government study (flowchart/swimlane/timeline, readers were civil servants). Quote: "the diagrammatic format, compared to prose, significantly enhances comprehension accuracy and answering speed"
- E19. https://eprints.cs.univie.ac.at/4059/1/Empirical_Evaluation_of_the_Understandability_of_Architectural_Component_Diagrams.pdf (Javed/Stevanetic/Zdun, 2014) — 2026-10-16 — Exa search text (WebFetch could not extract the PDF) — Size: component diagrams are best understood at middle numbers of elements, worse when too many or too few. Quote: "middle values of the number of components, links, elements, and symbols in the diagram significantly increase the architectural understandability compared to high or low values."
- E20. Same URL as E19 — 2026-10-16 — Exa search text — Same paper: thresholds are only rough. Quote: "we consider the thresholds we found as rough indicators."
- E21. https://doi.org/10.1109/qsic.2014.20 (2014) — 2026-10-16 — Exa — Companion study: one box per relevant function beats too few or too many. Quote: "each component in the architecture corresponds to one system's relevant functionality"

**Three pages, explain-back, before and after**
- E22. https://aws.amazon.com/blogs/startups/startup-advice-how-to-write-a-narrative/ (2019) — 2026-10-16 — WebFetch — Amazon narratives: six-page cap, readable with no prior knowledge. Quote: "It is limited to a maximum of six pages (but can have a reasonable number of appendices)"
- E23. Same URL as E22 — 2026-10-16 — WebFetch — Readable by anyone. Quote: "anybody within your organization can read and understand it" (without "any prior knowledge of the proposal").
- E24. https://www.aboutamazon.com/news/workplace/an-insider-look-at-amazons-culture-and-processes (2021) — 2026-10-16 — WebFetch — Amazon PR/FAQ lengths and length as forcing function. Quote: "The press release (PR) portion is a few paragraphs, always less than one page."
- E25. Same URL as E24 — 2026-10-16 — WebFetch — Same page. Quote: "restricting the length of the document is, to use a term that came up when describing the narratives, a forcing function"
- E26. https://basecamp.com/shapeup/1.5-chapter-06 — 2026-10-16 — WebFetch — Shape Up pitch ingredients (problem, appetite, solution, rabbit holes, no-gos). Quote: "There are five ingredients that we always want to include in a pitch:"
- E27. https://basecamp.com/shapeup/1.5-chapter-06 — 2026-10-16 — WebFetch — Shape Up on making the idea visible but not over-detailed. Quote: "Therefore we need some techniques to help people see the idea while still not going too far into irrelevant details."
- E28. https://basecamp.com/shapeup/1.5-chapter-06 — 2026-10-16 — Exa — Shape Up: no-gos defined (Exa text of same chapter). Quote: "Anything specifically excluded from the concept: functionality or use cases we intentionally aren’t covering to fit the appetite or make the problem tractable"
- E29. https://www.industrialempathy.com/posts/design-docs-at-google/ — 2026-10-16 — WebFetch — Google design docs: sections and "short enough". Quote: "1-3 page 'mini design doc'" (acceptable for smaller changes; 10-20 pages for larger projects).
- E30. https://www.industrialempathy.com/posts/design-docs-at-google/ — 2026-10-16 — WebFetch — Google: goals and non-goals. Quote: "non-goals aren't negated goals"
- E31. https://www.health.tas.gov.au/professionals/health-literacy/health-literacy-workplace-toolkit/spoken-communication/checking-understanding — 2026-10-16 — Exa fetch — Teach-back, explain-back method: ask in own words; test of the explainer. Quote: "This isn't a test of the consumer's knowledge; it's a test of how well you've communicated."
- E32. Same URL as E31 — 2026-10-16 — Exa fetch — Avoid yes/no. Quote: "Teach-back works better than asking 'yes' and 'no' questions like \"Do you understand?\""
- E33. Same URL as E31 — 2026-10-16 — Exa fetch — Chunk and re-explain. Quote: "'Chunk' your information into small sections."
- E34. https://www.smartsheet.com/sites/default/files/2023-08/IC-Project-Closeout-11813_PDF.pdf — 2026-10-16 — Exa — Closeout templates compare initial with actual and explain variance for goals, schedule and cost. Quote: "INITIAL GOALS AND DELIVERABLES ACTUAL GOALS AND DELIVERABLES EXPLANATION OF VARIANCE"
- E35. https://portal.ct.gov/-/media/Departments-and-Agencies/DSS/CT-METS/Library/General/CTDSSProjectCloseoutReportv11.pdf — 2026-10-16 — Exa — Government closeout template: compare baseline to actual, brief enough for an unfamiliar reader. Quote: "Compare baselines to actual and describe discrepancies."
- E36. Same URL as E35 — 2026-10-16 — Exa — Audience. Quote: "Be brief, but provide enough detail so that any person not familiar with the project will have the necessary information"
- E37. /home/user/Autonomy-Research/research/runs/engineer-planning/notes/plan-set.md:106 — 2026-10-16 — Read — Prior run: John approves the owner-facing brief, not the architecture; approval bound to a hash. Quote: "What John signs: (a) goals and non-goals, (b) scope list in plain words, (c) acceptance criteria as observable outcomes"
- E38. /home/user/Autonomy-Research/research/findings/engineer-planning.md:44 — 2026-10-16 — Read (earlier findings named by the lead) — The earlier recommended plan set sizes `brief.md` at 1-2 pages as worker inference. Quote: "| 1 | `brief.md` | Prose, 1-2 pages; the owner-facing file | Goal, non-goals, users, success measures, costs and risks |"
- E39. /home/user/Autonomy-Research/research/findings/engineer-planning.md:47 — 2026-10-16 — Read (earlier findings named by the lead) — The earlier plan set holds per-service integration facts in YAML. Quote: "| 4 | `integrations.yaml` | YAML; a script can check it against `.env.example` | Per service: purpose, auth type, env var name only, free or paid and price, owner action, fallback |"
- E40. /home/user/Autonomy-Research/research/findings/engineer-planning.md:255 — 2026-10-16 — Read (earlier findings named by the lead) — Mermaid C4 syntax rejected as default. Quote: "| Mermaid C4 syntax as default | Experimental (/home/user/Autonomy-Research/research/findings/engineer-feasibility.md:319) |"

**Dark theme and readability**
- E41. https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html — 2026-10-16 — WebFetch — WCAG 1.4.3 thresholds. Quote: "has a contrast ratio of at least 4.5:1"
- E42. Same URL as E41 — 2026-10-16 — WebFetch — Large text. Quote: "Large-scale text and images of large-scale text have a contrast ratio of at least 3:1;"
- E43. https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html — 2026-10-16 — WebFetch — WCAG 1.4.11: graphics and UI need 3:1. Quote: "The visual presentation of the following have a contrast ratio of at least 3:1 against adjacent color(s):"
- E44. Same URL as E43 — 2026-10-16 — WebFetch — Diagram parts. Quote: "Parts of graphics required to understand the content"
- E45. https://www.sciencedirect.com/science/article/abs/pii/S0003687016302459 (Dobres et al., 2017) — 2026-10-16 — Exa fetch — Dark-on-light advantage in dim light, larger at small sizes. Quote: "Under dark illumination, white-on-black text suffers a legibility disadvantage."
- E46. Same URL as E45 — 2026-10-16 — Exa fetch — Size interaction. Quote: "This disadvantage is more pronounced as text size decreases."
- E47. https://siegal.bio.nyu.edu/color-palette/ — 2026-10-16 — Exa fetch — Okabe-Ito colour-blind palette hex codes. Quote: "Masataka Okabe (Jikei Medical School) and Kei Ito (University of Tokyo) have devised a very nice palette that is color-blind friendly."
- E48. Same URL as E47 — 2026-10-16 — Exa fetch — Same page lists #E69F00, #56B4E9, #009E73, #F0E442, #0072B2, #D55E00, #CC79A7 (table rows).

**Toolchain: rendering, dark theme, validation**
- E49. https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams — 2026-10-16 — WebFetch — GitHub renders only four fence types, so Mermaid yes; D2, PlantUML, Graphviz, Structurizr need a committed image. Quote: "You can create diagrams in Markdown using four different syntaxes: mermaid, geoJSON, topoJSON, and ASCII STL." (the four-syntax sentence was seen in an Exa excerpt of this page; the WebFetch of it returned "Diagram rendering is available in GitHub Issues, GitHub Discussions, pull requests, wikis, and Markdown files.")
- E50. Same URL as E49 — 2026-10-16 — WebFetch — GitHub Mermaid version is whatever GitHub runs; it tells you to check it. Quote: "To ensure GitHub supports your Mermaid syntax, check the Mermaid version currently in use."
- E51. https://code.claude.com/docs/en/artifacts — 2026-10-16 — WebFetch — Claude Code artifacts (published claude.ai pages) allow scripts from five CDNs only, so Mermaid can load from jsDelivr `/npm/`, cdnjs or unpkg; every image must be a data URI. Quote: "scripts from five public CDN hosts: cdnjs, unpkg, the Tailwind and jQuery CDNs, and selected paths on jsDelivr such as `/npm/`."
- E52. Same URL as E51 — 2026-10-16 — WebFetch — The same page recommends SVG for diagrams. Quote: "Prefer SVG, or HTML and CSS, for diagrams over embedded raster images"
- E53. Same URL as E51 — 2026-10-16 — WebFetch — Artifact publishing needs a claude.ai login session and is off by default in `-p` runs, so an unattended engineer on API key or `claude -p` cannot publish a page. Quote: "Sessions using an API key, gateway token, or cloud-provider credential cannot publish."
- E54. Same URL as E51 — 2026-10-16 — WebFetch — Markdown artifact files render as styled documents; the page does not say Mermaid fences render in them. Quote: "Markdown files render as styled document pages with syntax-highlighted code."
- E55. https://mermaid.js.org/config/theming.html — 2026-10-16 — WebFetch — Mermaid built-in themes include dark; custom `themeVariables` work only on `base`. Quote: "the only theme that can be customized is the base theme."
- E56. Same URL as E55 — 2026-10-16 — WebFetch — Dark theme pairs with `darkMode`. Quote: "This theme goes well with dark-colored elements or dark-mode."
- E57. https://github.com/orgs/community/discussions/194348 — 2026-10-16 — WebFetch — GitHub dark mode: a Mermaid diagram renders right when GitHub's theme is explicitly dark but breaks when dark is implied by the system setting (user report 2026-04-29, no GitHub reply). Quote: "it is still broken when dark mode is implied by system setting."
- E58. https://github.com/mermaid-js/mermaid-cli (clone, commit f416ac5) package.json:47 — read 2026-10-16 — clone — mermaid-cli renders SVG/PNG/PDF, takes `-t dark -b transparent`; v12.0.0 depends on Puppeteer (a headless browser). Quote: `"puppeteer": "^25.0.0"`; README usage — Quote: "mmdc -i input.mmd -o output.png -t dark -b transparent"
- E59. https://github.com/jasonworden/mermaid-lint — 2026-10-16 — WebFetch — mermaid-lint validates with the real parser, MIT, Node 22+, exit codes for CI. Quote: "mermaid-lint only requires Node.js ≥22 and runs via `npx`."; "`0` = all valid · `1` = validation failures (or warnings with `--strict`) · `2` = usage/IO error"
- E60. https://github.com/terrastruct/d2 (clone, commit 6a7b483 dated 2026-10-11) — 2026-10-16 — clone — D2 licence MPL-2.0, exports SVG/PNG/GIF/PDF/PPTX, runs server-side. Quote: "D2 supports SVG, PNG, GIF, PDF, and PPTX exports."; "Open sourced under the Mozilla Public License 2.0."
- E61. https://github.com/terrastruct/d2 d2cli/main.go:101 and :213 (commit 6a7b483) — 2026-10-16 — clone — D2 dark theme and validate: `--dark-theme` is used when the viewer's browser is dark, and only for SVG; `fmt` and `validate` subcommands exist. Quote: "the theme to use when the viewer's browser is in dark mode."; `case "validate":`
- E62. https://github.com/terrastruct/d2 — 2026-10-16 — WebFetch — D2 bundles Dagre and ELK, and opt-in TALA. Quote: "A native Go port of the ELK directed graph layout engine"
- E63. https://github.com/structurizr/structurizr (clone, commit da99caf) README:3 — 2026-10-16 — clone — Structurizr is Apache-2.0 "models as code" for C4; its export module has mermaid, plantuml, dot and ilograph exporters. Quote: "Structurizr is a \"models as code\" tool designed for the [C4 model](https://c4model.com)"; directory `structurizr-export/.../export/` lists `dot`, `ilograph`, `mermaid`, `plantuml`
- E64. https://github.com/plantuml/plantuml (clone, commit 09c9256) LICENSE:1-2 — 2026-10-16 — clone — PlantUML is GPL-3.0 (also offers other licences). Quote: "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"
- E65. https://github.com/yuzutech/kroki (clone, commit 96acbf8) LICENSE:1; https://docs.kroki.io/kroki/setup/install/ — 2026-10-16 — clone; page opened — Kroki is MIT; the main image bundles D2, GraphViz, PlantUML (incl. C4), Structurizr; Mermaid and Excalidraw need companion containers; hosted free service exists. Quote: "MIT License"; "then you will also need to start their companion containers"
- E66. https://github.com/excalidraw/excalidraw (clone, commit 4c37956) LICENSE:1 — 2026-10-16 — clone — Excalidraw is MIT. Quote: "MIT License"

**Generation, currency and limits**
- E67. https://github.com/sverweij/dependency-cruiser (clone, commit c580daf, 2026-10-13) doc/cli.md:233-240 — read 2026-10-16 — clone — dependency-cruiser has a mermaid reporter, but it is less rich than dot/d2. Quote: "the graph cannot be (made as) feature rich as those produced by the `dot` or `d2` reporters."
- E68. https://github.com/jwa91/n8nmermaid (clone, commit 8aaf7dc) README.md:5 — 2026-10-16 — clone — n8nmermaid converts n8n workflow JSON to Mermaid flowchart text; MIT; last commit 2026-06-11. Quote: "Converts n8n workflow JSON files into Mermaid flowchart syntax (V2) or generates detailed analysis reports (V2)."
- E69. https://github.com/TamirTapiro/docker-compose-to-mermaid (clone, commit 311e116) README.md:14 — 2026-10-16 — clone — docker-compose-to-mermaid: CLI, GitHub Action, offline; MIT; last commit 2026-03-14. Quote: "**Fully offline** — no external APIs, no paid services required"
- E70. https://github.com/stackitcloud/stackit-landing-zone/blob/2dfc21ec702698d2806ee48cd0e001c4f561e98e/.github/workflows/generate-architecture-diagrams.yml — 2026-10-16 — WebFetch — A real workflow fails PRs when generated diagrams are stale using `git status --porcelain`. Quote: `if [[ -n "$(git status --porcelain -- docs/diagrams)" ]]; then`
- E71. /home/user/Autonomy-Research/research/findings/engineer-feasibility.md:20 — 2026-10-16 — Read — The earlier feasibility note proposes a Stop or PostToolUse hook parse gate and a source-pointer/last-verified date per diagram, flagged as untested. Quote: "Put a parse gate (mermaid-lint) in a Stop or PostToolUse hook."
- E72. https://github.com/mermaid-js/mermaid/blob/master/packages/mermaid/src/schemas/config.schema.yaml — 2026-10-16 — WebFetch — Defaults in the Mermaid config schema. Quote: "default: 50000" (maxTextSize); "default: 500" (maxEdges)
- E73. https://docs.rcsc.dev/laravel-cartographer/v1/renderer-limits — 2026-10-16 — WebFetch — Hosted renderers share the limits. Quote: "GitHub, GitLab, and the Mermaid live editor all stop at 50,000 characters of diagram source"
- E74. Same URL as E73 — 2026-10-16 — WebFetch — Splitting is the structural fix. Quote: "The structural answer, and the only one that helps both limits at once."
- E75. https://mermaid.ai/open-source/config/layouts.html — 2026-10-16 — WebFetch — ELK is bundled and the default from Mermaid v12.0.0. Quote: "ELK is bundled and default from v12.0.0."
- E76. https://github.com/orgs/community/discussions/138426 — 2026-10-16 — WebFetch — GitHub's ELK request is still open and unanswered as of 2026-09-23. Quote: "We're still waiting @github !! It's been two years"

**Agent counterpart: text versus image**
- E77. https://arxiv.org/html/2502.11829 — 2026-10-16 — Exa web_fetch_exa (search text for the Table 4 passage) — Code-Vision (Feb 2025) fed the same flowcharts as image and as Mermaid; most models did better on Mermaid, open-source ones much better. Quote: "when using mermaid as input, most models exhibit performance improvements. This suggests that the mermaid, being a more structured and textual representation, may be easier for MLLMs to interpret"
- E78. https://arxiv.org/html/2502.11829 — 2026-10-16 — Exa web_fetch_exa — In the same benchmark GPT-4o reached 79.3% pass@1 on Hard problems from flowchart images, so strong proprietary models read flowcharts well; the gap is mainly open models. Quote: "On Hard problems, GPT-4o can achieve 79.3% pass@1, but the best open-source model only achieves 15%."
- E79. https://arxiv.org/html/2402.02130v3 — 2026-10-16 — Exa search text — GITA/GITQA (graph reasoning): visual-only is worse than text-only on average; text plus image is best. Quote: "using the visual modality alone is worse than using the textual modality alone on average."
- E80. https://arxiv.org/html/2402.02130v3 — 2026-10-16 — Exa search text — Same paper: combining modalities wins. Quote: "combining textual and visual information together performs better than using one modality alone."
- E81. https://arxiv.org/html/2409.08864 — 2026-10-16 — Exa search text — Case study with GPT-4o: images alone are not enough, and help most on global properties (cycle detection). Quote: "providing only graph visualisations, without accompanying textual descriptions, is insufficient for LLMs to fully comprehend graph structures."
- E82. https://proceedings.iclr.cc/paper_files/paper/2024/file/bf72f65f30eedf5d48da6980ee02b589-Paper-Conference.pdf — 2026-10-16 — Exa search text — Text encoding matters a lot: the same graph in different text forms moves accuracy from 19.8% to 53.8% on one task. Quote: "for finding connected nodes to a node in a graph, adjacency achieves 19.8% accuracy and incident achieves 53.8% accuracy."
- E83. https://doi.org/10.48550/arxiv.2408.05457 — 2026-10-16 — Exa search text — JSON beat natural-language and DOT graph representations after instruction tuning (small Llama/Mistral/Gemma models, tuned). Quote: "JSON format for graph representation consistently outperforms natural language and code formats across various LLMs and graph types."
- E84. https://doi.org/10.48550/arxiv.2407.05183 — 2026-10-16 — Exa search text — Reading a flowchart image back into Mermaid is hard even for frontier VLMs of 2024. Quote: "struggled with the more complex task of accurately generating Mermaid code from flowcharts."
- E85. https://aclanthology.org/2024.findings-acl.78.pdf — 2026-10-16 — Exa search text — FlowVQA: VLMs struggle on image flowcharts built from Mermaid scripts. Quote: "both closed and open-source Vision Language Models (VLMs), equipped with a range of prompting strategies and fine-tuning techniques, struggled to execute visual and spatial reasoning tasks"
- E86. https://aclanthology.org/2024.findings-naacl.34/ — 2026-10-16 — Exa search text — Dissenting result: GraphTMI (NAACL 2024 Findings) found image better than text for large graphs. Quote: "the image modality, especially with vision-language models like GPT-4V, is superior to text in balancing token limits and preserving essential information"
- E87. https://doi.org/10.1016/j.procs.2025.09.191 — 2026-10-16 — Exa search text — LLMs generating diagrams from text: seven LLMs, Mermaid versus structured YAML, results vary widely by model. Quote: "some LLMs demonstrating strong syntax adherence, while others struggle with diagram structure and semantic accuracy."
- E88. https://doi.org/10.3390/info16070565 — 2026-10-16 — Exa search text — LLM-generated UML via PlantUML scored 61.1% to 67.7% completeness/correctness and always below human diagrams (GPT-4-turbo, one domain, student raters). Quote: "they consistently underperform compared to human-created diagrams."
- E89. https://aclanthology.org/2025.emnlp-main.640.pdf — 2026-10-16 — Exa search text — Claude 3.7 Sonnet generated diagrams with many extra nodes (31.67 on average versus 21.42 Gemini), so generated diagrams over-include. Quote: "Claude produces diagrams with 31.67 nodes on average, much more than 21.42 nodes of Gemini and 10.68 nodes of Llama."

**Agent counterpart: one model, many views, and context**
- E90. https://docs.structurizr.com/ai — 2026-10-16 — Exa search text — Structurizr separates model from views and recommends text for AI. Quote: "you can create a collection of consistent views onto a single model, where element names/descriptions, relationship descriptions, styling, etc all remain the same across the diagrams."
- E91. https://docs.structurizr.com/ai — 2026-10-16 — Exa search text — It exports to Mermaid and PlantUML, so the human picture is a rendering of the same source. Quote: "export Structurizr views to “diagrams as code” formats such as PlantUML and Mermaid for integration into your existing toolchain."
- E92. https://docs.structurizr.com/ai — 2026-10-16 — Exa search text — Structurizr's own claim that diagrams-as-code tools lack model consistency (vendor view; Mermaid alone is a view, not a model). Quote: "diagrams as code tools tools don’t understand the C4 model and don’t respect its rules."
- E93. https://docs.structurizr.com/workspaces/file-types — 2026-10-16 — Exa search text — Source and compiled forms: DSL is the source, JSON is generated. Quote: "The “compiled” version of your workspace source, additionally including diagram layout information from the diagram editor. This is an open JSON data format and is not designed to be edited by hand."
- E94. https://docs.structurizr.com/as-code — 2026-10-16 — Exa web_fetch_exa — Who maintains it: the team, in git next to the code, with agents proposing updates. Quote: "AI agents have limited abilities to interact with UI-driven tools, but they can generate text, making “as code” tools a better option"
- E95. https://docs.structurizr.com/as-code — 2026-10-16 — Exa search text — Agent roles Structurizr lists: diagram generation from a codebase, update via pull requests, drift detection. Quote: "an AI agent periodically compares code or infrastructure against the Structurizr model and raises an alert when they diverge."
- E96. https://docs.structurizr.com/ai/mcp — 2026-10-16 — Exa search text — Structurizr MCP server is free, open source, can validate DSL and export to Mermaid/PlantUML; a hosted instance exists at mcp.structurizr.com. Quote: "A free and open source Structurizr MCP server is available on GitHub. It runs standalone and supports stateless HTTP transport."
- E97. https://docs.structurizr.com/as-code — 2026-10-16 — Exa web_fetch_exa — Structurizr DSL carries a learning cost and needs Java tooling to run (cost note from the vendor). Quote: "The Structurizr DSL does have a slightly higher learning curve than a UI."
- E98. https://code.claude.com/docs/en/best-practices — 2026-10-16 — WebFetch — Claude Code's own guidance puts architectural decisions in CLAUDE.md but not file-by-file descriptions, and pushes sometimes-relevant knowledge into skills loaded on demand. Quote: "CLAUDE.md is loaded every session, so only include things that apply broadly. For domain knowledge or workflows that are only relevant sometimes, use skills instead."
- E99. https://code.claude.com/docs/en/best-practices — 2026-10-16 — WebFetch — The include/exclude table. Quote: "Architectural decisions specific to your project" (include) and "File-by-file descriptions of the codebase" (exclude)
- E100. https://arxiv.org/html/2602.11988 — 2026-10-16 — Exa search text — Cost and success: context files did not raise success and raised cost. Quote: "providing context files does not generally improve task success rates, while increasing inference cost by over 20% on average."
- E101. https://arxiv.org/html/2602.11988 — 2026-10-16 — Exa search text — Overviews specifically. Quote: "We conclude that context files are not effective at providing a repository overview."
- E102. https://arxiv.org/html/2602.11988 — 2026-10-16 — Exa search text — Measure used: steps before the agent touches a file in the real patch did not fall. Quote: "the context files do not meaningfully reduce this metric"
- E103. https://arxiv.org/abs/2602.11988 — 2026-10-16 — Exa search text — Scope: four coding agents, SWE-bench plus a new benchmark of 138 instances in 12 Python repositories. Quote: "comprising Python software engineering tasks, created specifically from real GitHub issues. The benchmark contains 138 unique instances"
- E104. https://arxiv.org/abs/2602.11988 — 2026-10-16 — Exa search text — What did work: instructions are followed, and the paper recommends minimal, non-discoverable requirements. Quote: "Human-written context files should only include instructions required for coding agents that are not already present in the README"
- E105. https://arxiv.org/html/2602.11988 — 2026-10-16 — Exa search text — Developer-written files gave a small non-significant gain, LLM-generated a marginal loss. Quote: "LLM-generated context files have a marginal negative effect on task success rates, while developer-written ones provide a marginal performance gain, neither statistically significant."
- E106. https://code.claude.com/docs/en/best-practices — 2026-10-16 — WebFetch — Claude Code's guidance matches: exclude what the agent can read from code, and prune. Quote: "Bloated CLAUDE.md files cause Claude to ignore your actual instructions!"
- E107. /home/user/Autonomy-Research/research/findings/engineer-existing-systems.md:415 — 2026-10-16 — Read — Earlier-wave note that context-file overview guidance versus this paper remained unresolved. Quote: "context-file overview guidance versus 2602.11988"

**The system-map skill**
- E108. /home/user/Autonomy-Research/plugin/skills/system-map/SKILL.md:3 — 2026-10-16 — Read — What it produces. Quote: "Produces C4 context and container levels as flowcharts, and sequenceDiagram for flows, one concern per small .mmd file in docs/diagrams/"
- E109. /home/user/Autonomy-Research/plugin/skills/system-map/SKILL.md:15-16 — 2026-10-16 — Read — Size limit and split rule. Quote: "keep each under about 25 lines."
- E110. /home/user/Autonomy-Research/plugin/skills/system-map/SKILL.md:23-25 — 2026-10-16 — Read — Evidence rule: omit unconfirmed. Quote: "If a part or link is not confirmed, it shall omit it and list the question in `research/open-questions.md`."
- E111. /home/user/Autonomy-Research/plugin/skills/system-map/SKILL.md:21-22 — 2026-10-16 — Read — Validation if present. Quote: "When `tests/check-mermaid.sh` exists, the skill shall run it on the directory and fix any failure before reporting."
- E112. /home/user/Autonomy-Research/plugin/skills/system-map/SKILL.md:28-31 — 2026-10-16 — Read — Inputs are only the user's pointers. Quote: "Read the sources the user points at; use `researcher` workers for anything external so fetched pages stay out of the lead."
- E113. /home/user/Autonomy-Research/tests/check-mermaid.sh:8-11 — 2026-10-16 — Read — The checker verifies link-in-index, first-line type, and render, not content. Quote: "does not render with mermaid-cli."
- E114. /home/user/Autonomy-Research/tests/check-mermaid.sh:46 — 2026-10-16 — Read — The checker rejects anything but flowchart/graph/sequenceDiagram. Quote: "*) fail "$n starts with '$first'; only flowchart or sequenceDiagram are allowed" ;;"
- E115. grep for "theme" and "dark" in /home/user/Autonomy-Research/tests/, docs/diagrams/ and plugin/skills/ — checked 2026-10-16 — Bash grep — No theme config exists in skill, tests or docs/diagrams. Quote: "(no output)"
- E116. /home/user/Autonomy-Research/plugin/skills/system-map/SKILL.md:48-51 — 2026-10-16 — Read — Shareable render link is optional and lead-only. Quote: "The `.mmd` file in the repo is the deliverable, and tests/check-mermaid.sh is the check."

## Implications for the autonomous engineer (and the researcher plugin)

**Brief template (engineer)**
- Add `docs/plan/brief.md` as a three-page template with the page headings from Q2. Add an after-brief template that reuses the same diagram ids (E22-E36). The before-brief replaces the earlier 1-2 page `brief.md` size (E38) and stays the file John signs (E37).
- End each page with explain-back prompts (E31-E33). The engineer rewrites any passage John cannot explain. Synthesizer inference: John's explanation can be recorded next to the approval, so the signature follows understanding.
- EARS requirements:
  - *When the engineer starts or finishes a project, it shall write a brief of at most three pages with the fixed page headings.*
  - *When a brief contains a diagram, the engineer shall use a plain Mermaid flowchart with a title, a legend and a label on every arrow, followed by a numbered text flow.*

**Toolchain (engineer)**
- Pin mermaid-lint and mermaid-cli. Run the lint in a PostToolUse or Stop hook on changed `.mmd` files (E59, E71). Render dark SVG with a fixed theme config (E55, E58).
- Commit source and SVG together. Generated diagrams carry a header naming their generator, and CI fails on drift with `git status --porcelain` (E70).
- **Cross-area (blueprint):** an unattended API-key or `claude -p` run cannot publish artifact pages (E53). The engineer's last step is to commit the brief and post a notice. Publishing happens from an interactive `/login` session (John's own, or Remote Control). The notification path must point John to the published page or the repo file accordingly.
  - *When the engineer runs with an API key or in `-p` mode, it shall commit the brief files and shall not attempt to publish an artifact page.*

**Agent counterpart (engineer)**
- Add a small system model file that the plan references by path, never imported in CLAUDE.md (E98-E101, E104). It holds only facts the code does not show.
- Synthesizer inference: link the model's service nodes to `integrations.yaml` entries by id (E39) rather than duplicating them.
- EARS requirements:
  - *When a change alters a system part or link, the engineer shall update the model file in the same commit.*
  - *When a Mermaid view names a node id that the model lacks, the check shall fail.*

**system-map skill (researcher plugin)**
- Implement the ten gaps in Q7 (E108-E116). The first ones to do are a model file with parity check, a dark theme config with a contrast check, an SVG output step, and a parameter for the open-questions path.
- Add `tests/check-mermaid.sh` to `tests/check.sh` so validation runs by default.
- Keep the plain-flowchart rule. Revisit only if the Structurizr spike shows a clear gain (E92, E97).

## Tools evaluated

| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Mermaid (language and Mermaid.js) | https://mermaid.js.org/config/theming.html | Text diagrams; themes incl. dark; renders on GitHub; limits 50,000 chars / 500 edges | GitHub, browser, artifact page via CDN | 2026-10-16 | **Default**; keep diagrams small |
| mermaid-cli (mmdc) | https://github.com/mermaid-js/mermaid-cli | Mermaid to SVG/PNG/PDF with `-t dark`; v12.0.0 depends on Puppeteer | local, CI (needs headless Chromium) | 2026-10-16 (clone, commit f416ac5) | Use for committed SVGs; spike Chromium in the cloud environment |
| mermaid-lint | https://github.com/jasonworden/mermaid-lint | Parser-based validation, MIT, Node 22+, exit codes | local, CI, hook | 2026-10-16 | Use (as existing row) |
| Mermaid ELK layout | https://mermaid.ai/open-source/config/layouts.html | Default layout from v12; GitHub does not support yet | Mermaid >= 12 | 2026-10-16 | Use only in rendered SVGs, not committed Mermaid |
| Claude Code artifacts (page constraints) | https://code.claude.com/docs/en/artifacts | Published claude.ai pages; scripts only from listed CDNs; SVG preferred for diagrams; API-key sessions cannot publish | CLI/Desktop session with /login | 2026-10-16 | Use for John's phone reading via an interactive session; unattended engineer commits files instead |
| D2 | https://github.com/terrastruct/d2 | Go binary; MPL-2.0; SVG/PNG/PDF; dark-theme flag; `fmt`, `validate`; Dagre/ELK/TALA | local, CI | 2026-10-16 (clone, commit 6a7b483) | Alternative for polished architecture SVG; not rendered by GitHub |
| Structurizr (DSL and tooling) | https://github.com/structurizr/structurizr | Apache-2.0 C4 models as code; exporters to Mermaid, PlantUML, dot | local (Java/Docker) | 2026-10-16 (clone, commit da99caf) | Fallback for multi-view C4 models only |
| Structurizr DSL (as code) | https://docs.structurizr.com/as-code | Text C4 model with generated views, JSON compiled form, export to Mermaid/PlantUML | local (Java tooling) | 2026-10-16 | Fallback: use if model rules matter; spike runtime cost |
| Structurizr MCP server | https://docs.structurizr.com/ai/mcp | Free OSS MCP: DSL parse/validate to JSON workspace, Mermaid and PlantUML export; hosted instance at mcp.structurizr.com | standalone or hosted | 2026-10-16 | Fallback; hosted instance would send DSL to a third party, use standalone; not run |
| PlantUML | https://github.com/plantuml/plantuml | UML text diagrams; GPL-3.0 among licences | local (Java) | 2026-10-16 (clone, commit 09c9256) | Reject as default: not GitHub-rendered, Java, GPL |
| Graphviz | (no page opened) | dot layouts; used by dependency-cruiser and pydeps | local | not opened | Use only as a generator back end; not researched further |
| Kroki | https://github.com/yuzutech/kroki | MIT gateway rendering many text formats; Mermaid/Excalidraw need companion containers | self-hosted Docker or hosted free service | 2026-10-16 (clone, commit 96acbf8) | Skip: adds a service; only useful for non-Mermaid formats |
| Excalidraw | https://github.com/excalidraw/excalidraw | MIT hand-drawn whiteboard | browser | 2026-10-16 (licence only) | Reject for agent-written docs: JSON scene, not text-diffable; not deeply evaluated |
| Eraser | (no page opened) | Paid diagram SaaS | hosted | not opened | Reject on free-first; not evaluated |
| dependency-cruiser (Mermaid reporter) | https://github.com/sverweij/dependency-cruiser | JS/TS dependency graph; Mermaid reporter less rich than dot/d2 | npx, local | 2026-10-16 (clone, commit c580daf) | Use for TS module graph (existing row); trim Mermaid output by hand |
| n8nmermaid | https://github.com/jwa91/n8nmermaid | n8n JSON to Mermaid, MIT | local Python (uv) | 2026-10-16 (clone, commit 8aaf7dc) | Use or copy the logic; spike on John's workflows |
| docker-compose-to-mermaid | https://github.com/TamirTapiro/docker-compose-to-mermaid | Compose to Mermaid, MIT, offline, CI action | local Node | 2026-10-16 (clone, commit 311e116) | Fallback; spike |
| Microsoft Hidi | https://www.nuget.org/packages/Microsoft.OpenApi.Hidi/2.4.1 | OpenAPI `show` emits Mermaid | .NET tool | not opened (search excerpt only) | Candidate; unverified |
| Terraform diagram tools (tfmermaid-action, infra-diagram-cli) | https://github.com/asannou/tfmermaid-action | Terraform graph/IaC to Mermaid | CI / local | not opened (search excerpt only) | Candidate; unverified |
| C4 model notation rules | https://c4model.com/diagrams/notation | Title, legend, labelled lines rules | notation, no install | 2026-10-16 | Use context level for John's page 1 with legend and verb labels; container level in the engineer's file |
| Okabe-Ito palette | https://siegal.bio.nyu.edu/color-palette/ | 8 colour-blind-safe colours | palette, no install | 2026-10-16 | Use for box categories on dark, with shape/label redundancy |
| WCAG 2.2 SC 1.4.3 / 1.4.11 | https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html | 4.5:1 text, 3:1 graphics | standard | 2026-10-16 | Use as floor; aim higher for body text |
| Teach-back method | https://www.health.tas.gov.au/professionals/health-literacy/health-literacy-workplace-toolkit/spoken-communication/checking-understanding | Explain-back check of understanding | method | 2026-10-16 | Use as the brief's acceptance test (prompts at page ends) |
| Shape Up pitch | https://basecamp.com/shapeup/1.5-chapter-06 | Five-ingredient pitch | template | 2026-10-16 | Borrow no-gos, appetite, rabbit holes |
| Amazon six-pager / PR-FAQ | https://www.aboutamazon.com/news/workplace/an-insider-look-at-amazons-culture-and-processes | Length-capped narrative | template | 2026-10-16 | Borrow forced length and FAQ-of-risks idea; skip six pages |
| arc42 canvas | https://canvas.arc42.org/ | Architecture canvases | template | 2026-10-16 (index only; sub-page 404) | Not evaluated beyond index; skip |
| Code-Vision benchmark | https://arxiv.org/html/2502.11829 | Flowchart-to-code benchmark with image versus Mermaid input | dataset | 2026-10-16 | Evidence; possible harness for the text-versus-image spike |
| FlowVQA / FlowLearn / GITQA | https://aclanthology.org/2024.findings-acl.78.pdf | Flowchart and graph VQA benchmarks | datasets | 2026-10-16 | Evidence only |
| FlowSight dataset | https://github.com/herbit2004/FlowSight-Dataset | Mermaid source, PNG, description and QA per architecture diagram | local Python, OpenRouter key | 2026-10-16 (search text only) | Skip; not opened beyond search text |
| DiagramEval | https://aclanthology.org/2025.emnlp-main.640.pdf | Graph-based node/path metric for LLM diagrams | research code | 2026-10-16 | Idea: node/path F1 as a parity check against the model |

## Open questions

**Excluded claims.** Each of these rests on no opened source (search excerpt or search text only, or a page that was never opened), or carries no quote.
1. Teach-back toolkit: "Do not ask the person to “repeat back.”" (https://teachbacktraining.org/about-teach-back/10-elements-of-using-teach-back-effectively-detailed-version/). Seen as Exa search text only.
2. Apple HIG iOS default body 17 pt, minimum 11 pt (https://apple-docs.everest.mt/docs/design/human-interface-guidelines/typography/). Mirror page, Exa search text only; developer.apple.com returned no text. The template note's "17 pt" phone body size is therefore unsourced.
3. Apple: allow text to enlarge by at least 200 percent (https://apple-docs.everest.mt/docs/design/human-interface-guidelines/accessibility/). Exa search text only.
4. Tai et al. 2013: negative polarity was preferred and more comfortable (https://doi.org/10.1167/13.9.1157). Exa search text, not listed as opened. This was the opposing side of the dark-theme contradiction in Q3, so dark against light for John remains open; the phone test is in spike 2.
5. Microsoft Hidi can generate a Mermaid diagram from an OpenAPI document (https://www.nuget.org/packages/Microsoft.OpenApi.Hidi/2.4.1). Exa excerpt only. Its output quality and the repo's licence and maintenance were not verified.
6. Terraform-to-Mermaid tools (tfmermaid-action, Terraform Mermaid Visualizer, infra-diagram-cli). Seen in Exa excerpts only; quality, licence and maintenance not verified. Rover, inframap and Graphviz-based Terraform graphs were not researched.
7. mermaid-cli SVG output is not byte-stable across environments (https://github.com/optivem/gh-optivem/blob/main/.github/workflows/regenerate-diagram.yml). Exa excerpt only; spike 7.
8. Mermaid's global default layout is `dagre`, with `elk` a separately registered package (packages/mermaid/src/docs/config/theming.md excerpt). Excerpt only. This is the opposing side of the ELK-default contradiction in Q5, probably v11 against v12 drift; unresolved.
9. The OpenReview abstract of 2602.11988 says context files "tend to reduce task success rates" (https://openreview.net/forum?id=0DyJeJ3iia), against the arXiv abstract's "does not generally improve" (https://arxiv.org/abs/2602.11988). The OpenReview page is not listed as opened. Both versions agree on the cost increase.
10. Eraser is a paid SaaS. No page opened; it was rejected on the free-first rule alone. Graphviz's licence and dot CLI details were not opened either.
11. Unquoted claim: per the 2602.11988 paper, the Codex and Qwen Code generation prompts instruct an overview section. The note gives no quote for this, so the practice-against-measurement dispute is recorded without it.

**Gaps from the notes**
12. No study on diagram comprehension on a phone-sized screen, and no exact box-count threshold. The Univie PDF could not be text-extracted, so its numeric thresholds are unverified.
13. The arc42 Architecture Communication Canvas page (https://canvas.arc42.org/architecture-communication-canvas/) returned 404. The index page listed no canvas sections, so arc42 is not cited.
14. Not searched or not opened: DFD comprehension research, "architecture haiku", ADR/RFC templates (Rust RFC, Python PEP), and print or PDF export guidance (page size, dark-to-light switch). The Material Design 3 dark-theme page returned no usable text, so dark-surface colour values are unsourced. Contrast ratios for the proposed colours were not computed.
15. The claim that Amazon narratives convey about 10x was seen only in a search excerpt (a16z podcast) and is not cited.
16. No evidence on whether non-technical owners retain more from 3 pages than from 1 or 6. No software-specific "as-built brief for a non-technical owner" source; the after-brief adapts project-management closeout templates.
17. Not tested or found:
    - whether Mermaid fences render in claude.ai project files or in the Claude app on a phone (spike 1);
    - GitHub's current Mermaid version (spike 10);
    - whether GitHub applies exactly the 50,000-character and 500-edge limits (only a third-party doc says so).
18. No paper compares a coding agent's implementation fidelity when given Mermaid versus a rendered image of the same design. No 2026 benchmark covers frontier models on architecture diagrams. The models in 2602.11988 are not the current Sonnet 5.5.
19. Many agent-counterpart quotes come from Exa search text, which the worker rated one level weaker (marked in Evidence). No independent, non-vendor account was found of a team using Structurizr or Mermaid as an agent's source of truth. No evidence on C4 JSON or OpenAPI as a source of truth beyond Structurizr's vendor claims. No study of context files for non-code (SaaS, no-code) systems.
20. Not tested: whether the Structurizr MCP validates and exports without a local Java install, and whether mermaid-cli renders offline in the engineer environment.
21. Contradictions left open:
    - swimlanes for John (Q1);
    - dark against light polarity (Q3, with item 4);
    - Structurizr model consistency against plain Mermaid (Q6);
    - node-count target for a phone, where the workers' inferences of 6-9, 10-15 and about 25 lines disagree (Q1, spike 6).
