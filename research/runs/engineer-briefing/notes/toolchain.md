# Diagram toolchain: rendering, dark theme, validation and generation

Brief: Choose the diagram toolchain an autonomous Claude Code engineer uses for John's briefs and repo docs, given that John reads on a phone in the Claude app and on GitHub.
Run: research/runs/engineer-briefing/PLAN.md

Recommendation (one): Mermaid source (flowchart, sequenceDiagram, erDiagram) committed as text, gated by mermaid-lint, with a pre-rendered dark-friendly SVG made by mermaid-cli (or Mermaid loaded from jsDelivr /npm/ in a published artifact page) for the phone. Generators emit Mermaid; CI re-generates and diffs. Alternatives and rejections are in the Takeaways and the table. Spike list at the end of Question 4.

## Candidates: licence, native rendering, dark theme, headless render, validation

### Takeaway
Mermaid is the only candidate that renders natively on GitHub, and it is also the easiest to load in a published Claude page; D2 is the best second tool (single Go binary, real dark-theme flag, `d2 fmt`/`d2 validate`), but GitHub does not render it. Structurizr, PlantUML and Graphviz are generators or fallbacks, not defaults. Confidence: medium-high (GitHub, artifact, Mermaid, D2 facts from opened sources; phone rendering of Mermaid in project files not found).

### Cited findings
- GitHub renders only four fence types, so Mermaid yes; D2, PlantUML, Graphviz, Structurizr need a committed image — https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams, opened 2026-10-16, WebFetch — Quote: "You can create diagrams in Markdown using four different syntaxes: mermaid, geoJSON, topoJSON, and ASCII STL." (the four-syntax sentence was seen in an Exa excerpt of this page; the WebFetch of it returned "Diagram rendering is available in GitHub Issues, GitHub Discussions, pull requests, wikis, and Markdown files.")
- GitHub Mermaid version is whatever GitHub runs; it tells you to check it — same URL, opened 2026-10-16, WebFetch — Quote: "To ensure GitHub supports your Mermaid syntax, check the Mermaid version currently in use."
- Claude Code artifacts (published claude.ai pages) allow scripts from five CDNs only, so Mermaid can load from jsDelivr `/npm/`, cdnjs or unpkg; every image must be a data URI — https://code.claude.com/docs/en/artifacts, opened 2026-10-16, WebFetch — Quote: "scripts from five public CDN hosts: cdnjs, unpkg, the Tailwind and jQuery CDNs, and selected paths on jsDelivr such as `/npm/`."
- The same page recommends SVG for diagrams — same URL — Quote: "Prefer SVG, or HTML and CSS, for diagrams over embedded raster images"
- Artifact publishing needs a claude.ai login session and is off by default in `-p` runs, so an unattended engineer on API key or `claude -p` cannot publish a page — same URL — Quote: "Sessions using an API key, gateway token, or cloud-provider credential cannot publish."
- Markdown artifact files render as styled documents; the page does not say Mermaid fences render in them — same URL — Quote: "Markdown files render as styled document pages with syntax-highlighted code."
- Mermaid built-in themes include dark; custom `themeVariables` work only on `base` — https://mermaid.js.org/config/theming.html, opened 2026-10-16, WebFetch — Quote: "the only theme that can be customized is the base theme."
- Dark theme pairs with `darkMode` — same URL — Quote: "This theme goes well with dark-colored elements or dark-mode."
- GitHub dark mode: a Mermaid diagram renders right when GitHub's theme is explicitly dark but breaks when dark is implied by the system setting (user report 2026-04-29, no GitHub reply) — https://github.com/orgs/community/discussions/194348, opened 2026-10-16, WebFetch — Quote: "it is still broken when dark mode is implied by system setting."
- mermaid-cli renders SVG/PNG/PDF, takes `-t dark -b transparent`; v12.0.0 depends on Puppeteer (a headless browser) — https://github.com/mermaid-js/mermaid-cli (clone, commit f416ac5) package.json:47, read 2026-10-16 — Quote: `"puppeteer": "^25.0.0"`; README usage — Quote: "mmdc -i input.mmd -o output.png -t dark -b transparent"
- mermaid-lint validates with the real parser, MIT, Node 22+, exit codes for CI — https://github.com/jasonworden/mermaid-lint, opened 2026-10-16, WebFetch — Quote: "mermaid-lint only requires Node.js ≥22 and runs via `npx`."; "`0` = all valid · `1` = validation failures (or warnings with `--strict`) · `2` = usage/IO error"
- D2 licence MPL-2.0, exports SVG/PNG/GIF/PDF/PPTX, runs server-side — https://github.com/terrastruct/d2 (clone, commit 6a7b483 dated 2026-10-11), opened 2026-10-16 — Quote: "D2 supports SVG, PNG, GIF, PDF, and PPTX exports."; "Open sourced under the Mozilla Public License 2.0."
- D2 dark theme and validate: `--dark-theme` is used when the viewer's browser is dark, and only for SVG; `fmt` and `validate` subcommands exist — d2cli/main.go:101 and :213 (commit 6a7b483) — Quote: "the theme to use when the viewer's browser is in dark mode."; `case "validate":`
- D2 bundles Dagre and ELK, and opt-in TALA — https://github.com/terrastruct/d2, opened 2026-10-16, WebFetch — Quote: "A native Go port of the ELK directed graph layout engine"
- Structurizr is Apache-2.0 "models as code" for C4; its export module has mermaid, plantuml, dot and ilograph exporters — https://github.com/structurizr/structurizr (clone, commit da99caf), README:3 — Quote: "Structurizr is a \"models as code\" tool designed for the [C4 model](https://c4model.com)"; directory `structurizr-export/.../export/` lists `dot`, `ilograph`, `mermaid`, `plantuml`
- PlantUML is GPL-3.0 (also offers other licences) — https://github.com/plantuml/plantuml (clone, commit 09c9256) LICENSE:1-2 — Quote: "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"
- Kroki is MIT; the main image bundles D2, GraphViz, PlantUML (incl. C4), Structurizr; Mermaid and Excalidraw need companion containers; hosted free service exists — https://github.com/yuzutech/kroki (clone, commit 96acbf8) LICENSE:1 — Quote: "MIT License"; https://docs.kroki.io/kroki/setup/install/ opened 2026-10-16 — Quote: "then you will also need to start their companion containers"
- Excalidraw is MIT — https://github.com/excalidraw/excalidraw (clone, commit 4c37956) LICENSE:1 — Quote: "MIT License"

### Contradictions
- GitHub docs page states four syntaxes only (no D2/PlantUML), consistent with all sources; no disagreement. The earlier feasibility note records a disagreement on GitHub rendering Mermaid C4 (research/findings/engineer-feasibility.md:22); not re-settled here, plain flowchart avoids it.

### Inferences
- Mermaid is the default because it is the only text format that shows inline on GitHub and, via one CDN script tag, in a published Claude page (rests on the GitHub docs and artifacts page quotes).
- For the phone, pre-rendered SVG inlined in the page is safer than client-side Mermaid: the CSP blocks images but inline SVG is plain HTML, and the artifacts page itself recommends SVG. Dark theme is then a build parameter (`-t dark` or a `themeVariables` init) not a viewer behaviour.
- Dark/light on GitHub cannot be controlled per viewer; a neutral look (Mermaid `neutral` theme or `base` with mid-tone colours) works on both backgrounds. This is my reasoning from the dark-mode report, not a tested result.
- Artifact publishing needs a `/login` session, so an unattended `claude -p` engineer should commit SVG/Markdown to the repo and let an interactive or Remote Control session (or John) publish the page.
- D2 earns a place only if a diagram must be pretty (architecture with icons) and be committed as SVG; that adds a render step and loses GitHub's text view.

### Gaps
- Whether Mermaid fences render in claude.ai project files and the Claude app on a phone: no source found. Spike on John's phone.
- GitHub's current Mermaid version and whether it is v12: not read (the page offers a version-check snippet; not run).
- Eraser and excalidraw-from-text tools: not opened; Eraser is a paid SaaS, treated as rejected on the free-first rule without evidence beyond that rule.
- Graphviz licence and dot-from-CLI details: not opened (Graphviz appears only as a Kroki bundle member and dependency-cruiser dot output).
- Mermaid Chart connector: already in registry (validate/render, 60k chars output per render); not re-tested.

## Generation from code and configuration

### Takeaway
Mermaid output exists for most inputs, but quality is mixed and most tools are small, single-maintainer projects: dependency-cruiser (mature, mermaid reporter), n8nmermaid, docker-compose-to-mermaid and the Microsoft Hidi OpenAPI `show` command are usable; Terraform has several tools and none is a clear standard. The engineer should treat generated Mermaid as a draft that is validated, size-checked and then trimmed by hand. Confidence: medium.

### Cited findings
- dependency-cruiser has a mermaid reporter, but it is less rich than dot/d2 — https://github.com/sverweij/dependency-cruiser (clone, commit c580daf, 2026-10-13) doc/cli.md:233-240, read 2026-10-16 — Quote: "the graph cannot be (made as) feature rich as those produced by the `dot` or `d2` reporters."
- n8nmermaid converts n8n workflow JSON to Mermaid flowchart text; MIT; last commit 2026-06-11 — https://github.com/jwa91/n8nmermaid (clone, commit 8aaf7dc) README.md:5 — Quote: "Converts n8n workflow JSON files into Mermaid flowchart syntax (V2) or generates detailed analysis reports (V2)."
- docker-compose-to-mermaid: CLI, GitHub Action, offline; MIT; last commit 2026-03-14 — https://github.com/TamirTapiro/docker-compose-to-mermaid (clone, commit 311e116) README.md:14 — Quote: "**Fully offline** — no external APIs, no paid services required"
- Microsoft Hidi can generate a Mermaid diagram of an API from an OpenAPI document — https://www.nuget.org/packages/Microsoft.OpenApi.Hidi/2.4.1 (seen via Exa excerpt only, not separately opened) — see Gaps; not relied on.
- Terraform: tfmermaid-action, a VS Code extension and infra-diagram-cli exist — seen in Exa excerpts only; not opened. See Gaps.

### Contradictions
- None found.

### Inferences
- Because n8n JSON carries node connections explicitly, n8n to Mermaid is a deterministic transform; a 100-line script by the engineer is a credible alternative to a third-party dependency (rests on the n8nmermaid README description).
- OpenAPI to sequence diagrams: no tool opened produces true sequence flows; Hidi `show` outputs an API structure diagram, so sequence diagrams stay LLM-written from the spec, then linted.
- pydeps outputs Graphviz dot (registry row); Python import graphs to Mermaid have no opened tool, so convert dot to Mermaid with a small script or render the dot to SVG with Graphviz.
- For Structurizr, the exporters (mermaid, plantuml, dot) exist in source, so a Structurizr DSL model can be exported to Mermaid (README listing). Worth it only for a multi-view C4 model; the Structurizr CLI is Java and was not run.

### Gaps
- Terraform-to-diagram tools (tfmermaid-action, Terraform Mermaid Visualizer, infra-diagram-cli): surfaced in search only; quality, licence and maintenance not verified.
- Hidi `show`: output quality and the OpenAPI.NET repo licence/maintenance not verified.
- pydeps Mermaid output: no source found.
- Rover, inframap, Graphviz-based Terraform graph: not researched.

## Keeping diagrams current

### Takeaway
Use the commit-the-generated-file pattern: a generator script writes `.mmd`/`.md` into the repo, CI re-runs it and fails the PR if `git status --porcelain` shows a change; do not gate merges on mermaid-cli SVG bytes because they differ across environments. Confidence: medium-high.

### Cited findings
- A real workflow fails PRs when generated diagrams are stale using `git status --porcelain` — https://github.com/stackitcloud/stackit-landing-zone/blob/2dfc21ec702698d2806ee48cd0e001c4f561e98e/.github/workflows/generate-architecture-diagrams.yml, opened 2026-10-16, WebFetch — Quote: `if [[ -n "$(git status --porcelain -- docs/diagrams)" ]]; then`
- Another repo regenerates SVGs only on push to main because mermaid-cli output is not byte-stable — https://github.com/optivem/gh-optivem/blob/main/.github/workflows/regenerate-diagram.yml (Exa excerpt; not separately opened) — see Gaps; not relied on.
- mermaid-lint offers exit codes 0/1/2 suited to a hook or CI step (see Question 1).
- The earlier feasibility note proposes a Stop or PostToolUse hook parse gate and a source-pointer/last-verified date per diagram, flagged as untested — /home/user/Autonomy-Research/research/findings/engineer-feasibility.md:20 — Quote: "Put a parse gate (mermaid-lint) in a Stop or PostToolUse hook."

### Contradictions
- None found.

### Inferences
- Gate on the Mermaid source text (deterministic) and treat rendered SVG as a build artifact regenerated on main; this follows from the stackit workflow and the byte-stability complaint (the latter only from an unopened excerpt, so treat as a hypothesis to spike).
- Each generated diagram should carry a header comment naming its generator command and input file, so the engineer can re-run it, and the done-gate can list stale ones.

### Gaps
- Byte stability of mermaid-cli output across machines: only an unopened excerpt; spike by rendering twice on two environments.

## Rendering limits

### Takeaway
Mermaid hard-stops at 50,000 characters of source and 500 edges by default; GitHub and GitLab enforce the same, and then show "Maximum text size in diagram exceeded". Split by concern long before that (target well under 30 nodes for phone readability, my number). ELK is the default layout in Mermaid 12 but GitHub has not adopted it as of Sep 2026. Confidence: high on limits, low on the node-count target.

### Cited findings
- Defaults in the Mermaid config schema — https://github.com/mermaid-js/mermaid/blob/master/packages/mermaid/src/schemas/config.schema.yaml, opened 2026-10-16, WebFetch — Quote: "default: 50000" (maxTextSize); "default: 500" (maxEdges)
- Hosted renderers share the limits — https://docs.rcsc.dev/laravel-cartographer/v1/renderer-limits, opened 2026-10-16, WebFetch — Quote: "GitHub, GitLab, and the Mermaid live editor all stop at 50,000 characters of diagram source"
- Splitting is the structural fix — same URL — Quote: "The structural answer, and the only one that helps both limits at once."
- ELK is bundled and the default from Mermaid v12.0.0 — https://mermaid.ai/open-source/config/layouts.html, opened 2026-10-16, WebFetch — Quote: "ELK is bundled and default from v12.0.0."
- GitHub's ELK request is still open and unanswered as of 2026-09-23 — https://github.com/orgs/community/discussions/138426, opened 2026-10-16, WebFetch — Quote: "We're still waiting @github !! It's been two years"
- D2 also ships Dagre and ELK, so layout choice is available outside Mermaid — see Question 1.

### Contradictions
- Mermaid docs say ELK is the default layout (layouts page above); an older theming source (packages/mermaid/src/docs/config/theming.md excerpt) says the global default is `dagre` and `elk` is a separately registered package. Likely version drift (v11 vs v12); not settled. GitHub renders its own pinned version, so do not rely on ELK in committed Mermaid.

### Inferences
- Because GitHub's layout engine is outside our control, a diagram that only reads well under ELK will look different on GitHub than in our rendered SVG. Keep committed diagrams small enough that Dagre layout is fine, or commit the SVG next to the source and embed the SVG.
- For a phone, width matters more than the 500-edge limit: prefer `flowchart TD` with at most about 10 to 15 nodes per diagram and one concern each (matches CLAUDE.md "Diagrams are small Mermaid files, one concern each").

### Gaps
- Real render-time and legibility thresholds on a phone: no source; spike.
- Whether `maxTextSize` / `maxEdges` on GitHub are exactly these: only a third-party doc states it.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Mermaid (language and Mermaid.js) | https://mermaid.js.org/config/theming.html | Text diagrams; themes incl. dark; renders on GitHub; limits 50,000 chars / 500 edges | GitHub, browser, artifact page via CDN | 2026-10-16 | **Default**; keep diagrams small |
| mermaid-cli (mmdc) | https://github.com/mermaid-js/mermaid-cli | Mermaid to SVG/PNG/PDF with `-t dark`; v12.0.0 depends on Puppeteer | local, CI (needs headless Chromium) | 2026-10-16 (clone, commit f416ac5) | Use for committed SVGs; spike Chromium in the cloud environment |
| mermaid-lint | https://github.com/jasonworden/mermaid-lint | Parser-based validation, MIT, Node 22+, exit codes | local, CI, hook | 2026-10-16 | Use (as existing row) |
| D2 | https://github.com/terrastruct/d2 | Go binary; MPL-2.0; SVG/PNG/PDF; dark-theme flag; `fmt`, `validate`; Dagre/ELK/TALA | local, CI | 2026-10-16 (clone, commit 6a7b483) | Alternative for polished architecture SVG; not rendered by GitHub |
| Structurizr (DSL and tooling) | https://github.com/structurizr/structurizr | Apache-2.0 C4 models as code; exporters to Mermaid, PlantUML, dot | local (Java/Docker) | 2026-10-16 (clone, commit da99caf) | Fallback for multi-view C4 models only |
| PlantUML | https://github.com/plantuml/plantuml | UML text diagrams; GPL-3.0 among licences | local (Java) | 2026-10-16 (clone, commit 09c9256) | Reject as default: not GitHub-rendered, Java, GPL |
| Graphviz | (no page opened) | dot layouts; used by dependency-cruiser and pydeps | local | not opened | Use only as a generator back end; not researched further |
| Kroki | https://github.com/yuzutech/kroki | MIT gateway rendering many text formats; Mermaid/Excalidraw need companion containers | self-hosted Docker or hosted free service | 2026-10-16 (clone, commit 96acbf8) | Skip: adds a service; only useful for non-Mermaid formats |
| Excalidraw | https://github.com/excalidraw/excalidraw | MIT hand-drawn whiteboard | browser | 2026-10-16 (licence only) | Reject for agent-written docs: JSON scene, not text-diffable; not deeply evaluated |
| Eraser | (no page opened) | Paid diagram SaaS | hosted | not opened | Reject on free-first; not evaluated |
| n8nmermaid | https://github.com/jwa91/n8nmermaid | n8n JSON to Mermaid, MIT | local Python (uv) | 2026-10-16 (clone, commit 8aaf7dc) | Use or copy the logic; spike on John's workflows |
| docker-compose-to-mermaid | https://github.com/TamirTapiro/docker-compose-to-mermaid | Compose to Mermaid, MIT, offline, CI action | local Node | 2026-10-16 (clone, commit 311e116) | Fallback; spike |
| Microsoft Hidi | https://www.nuget.org/packages/Microsoft.OpenApi.Hidi/2.4.1 | OpenAPI `show` emits Mermaid | .NET tool | not opened (search excerpt only) | Candidate; unverified |
| Terraform diagram tools (tfmermaid-action, infra-diagram-cli) | https://github.com/asannou/tfmermaid-action | Terraform graph/IaC to Mermaid | CI / local | not opened (search excerpt only) | Candidate; unverified |
| Mermaid ELK layout | https://mermaid.ai/open-source/config/layouts.html | Default layout from v12; GitHub does not support yet | Mermaid >= 12 | 2026-10-16 | Use only in rendered SVGs, not committed Mermaid |
