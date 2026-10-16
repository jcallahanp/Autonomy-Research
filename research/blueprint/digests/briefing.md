# Visual briefing (Area 8) - digest
Source: research/findings/engineer-briefing.md; verification: 19 of 20 verified, 1 unverified (check-mermaid.sh line citation, E114; rule true, line number corrected; not load-bearing)

## Decision
- John's brief is one Markdown source of at most three pages, made into a dark-theme claude.ai page; a before-brief and an after-brief share one skeleton and the same diagram ids (Summary; Q2, confidence medium).
- Page 1: two-line what and why, one plain Mermaid flowchart at C4 system-context level with a legend and a verb on every arrow, then a numbered text flow (E1, E4, E5); untrained readers did best with text followed by the diagram (E14, E15, Exa).
- Page 2: stack, where each key lives (names only), what John will see. Page 3: what John must do, not doing, risks, costs. Explain-back prompts close each page (worker inference built on E25, E26, E28, E29, E31-E33).
- Toolchain, all free: Mermaid source committed as text, gated by pinned mermaid-lint (E59); dark SVG rendered by pinned mermaid-cli `-t dark` (E58, E55); SVG inlined in a published artifact page, which says "Prefer SVG" (E52). Colours Okabe-Ito with shape or label redundancy (E47, E9); borders 3:1 or better, text 4.5:1 (E43, E41).
- An API-key, gateway-token or `claude -p` session cannot publish artifacts (E53), so an unattended engineer commits the brief and an interactive `/login` session (John's or Remote Control) publishes it (Implications, cross-area).
- Agent counterpart is text, not an image (E77, E79, E81; mostly Exa search text): a small YAML model with only facts the code does not show, read by path, kept out of CLAUDE.md (E98-E101, E104), Mermaid views generated from it with a parity check per commit (Q6, worker inference).
- Extend the system-map skill with the ten gaps in Q7; it today emits theme-less `.mmd` only (E108, E115).
- Overall confidence medium; nothing tested on John's phone or on 2026 models (Summary).

## Alternatives and rejected
- D2 - alternative - polished architecture SVG, MPL-2.0, `validate`, dark flag; extra render step, not GitHub-rendered (E60, E61, E49).
- Client-side Mermaid from jsDelivr `/npm/` in the artifact - alternative - less safe than inline SVG (E51; worker inference).
- Structurizr DSL + free MCP export to Mermaid - alternative if C4 model rules matter; needs Java (E63, E96, E97).
- Hand-kept Mermaid as source - alternative - simplest, no parity check possible (worker inference, Q8).
- Image plus text - alternative for UI review only (E80).
- Generators dependency-cruiser, n8nmermaid, docker-compose-to-mermaid or own scripts - kept (E67-E69).
- PlantUML as default - rejected - GPL-3.0 among licences, Java, not GitHub-rendered (E64, E49).
- Kroki - rejected - adds a service; Mermaid needs companion containers (E65).
- Excalidraw - rejected for agent-written docs - JSON scene, not text-diffable (worker verdict; only licence opened, E66).
- Eraser - rejected - paid SaaS, no page opened (open q 10).
- Mermaid C4 syntax - rejected - experimental (E40).
- Sequence diagrams and swimlanes on John's pages - rejected - help only experienced readers; swimlanes less effective (E17, E16).
- Image-only diagrams as agent spec - rejected (E81, E79).
- Overview in CLAUDE.md or AGENTS.md - rejected - no gain, over 20 % cost (E100, E101; Exa search text), excluded by best practices (E99).
- LLM-generated diagrams unchecked - rejected - below human quality, over-inclusion (E88, E89).
- Gating merges on rendered SVG bytes - rejected until spike 7 - byte-instability rests on an unopened excerpt (open q 7).
- ELK layout in committed Mermaid - rejected - GitHub has not adopted it (E76).

## Stack
| Tool | What it does here | Where it runs | Cost | Evidence |
|---|---|---|---|---|
| Mermaid flowchart | Diagram source for brief and generated views; limits 50,000 chars / 500 edges | GitHub, artifact page | free | E49, E72 |
| mermaid-lint | Parser-based validation, exit codes, Node 22+ | hook, CI | free (MIT) | E59 |
| mermaid-cli (mmdc) | Renders dark SVG; v12.0.0 depends on Puppeteer (headless Chromium) | local, CI | free | E58 |
| Claude Code artifacts | Published claude.ai page for John's phone, inline SVG | interactive `/login` session | included in plan (not stated as priced) | E51-E54 |
| Okabe-Ito palette, WCAG 1.4.3/1.4.11 | Colour-blind-safe categories; 4.5:1 text, 3:1 graphics floors | design rules | free | E47, E41, E43 |
| n8nmermaid | n8n workflow JSON to Mermaid | local Python (uv) | free (MIT) | E68 |
| docker-compose-to-mermaid | Compose to Mermaid, offline | local Node, CI | free (MIT) | E69 |
| dependency-cruiser | TS module graph, Mermaid reporter | npx | free | E67 |
| `git status --porcelain` CI check | Fails PR on stale generated diagrams | CI | free | E70 |

## Setup steps
| Step | Automated or John | How it is verified |
|---|---|---|
| 1. Pin mermaid-lint and mermaid-cli; provide headless Chromium in the cloud environment | Automated | Spike 2 renders a dark SVG |
| 2. Lint hook (PostToolUse or Stop) on changed `.mmd` files | Automated | Bad `.mmd` fails the hook (E71) |
| 3. Fixed dark theme config (`-t dark` or `base` + `themeVariables`) with contrast check | Automated | Computed contrast meets 4.5:1 / 3:1 (not yet computed, open q 14) |
| 4. CI drift check; generated diagrams carry a generator header | Automated | `git status --porcelain` clean after regeneration (E70) |
| 5. Add `docs/plan/brief.md` before and after templates with fixed page headings | Automated | Template present; page count at most three |
| 6. Add system model file plus parity check | Automated | Mermaid node id missing from model fails the check |
| 7. Add `tests/check-mermaid.sh` to `tests/check.sh` | Automated | Runs by default (Q7 gap 10) |
| 8. Publish the brief as a claude.ai page | **John** (interactive `/login` session) or a Remote Control session | Spike 9: page opens on the phone |
| 9. Explain-back: read each page and answer "in your own words" prompts | **John** | Passages rewritten until explained (spike 3) |
| 10. View diagrams on the phone in usual lighting, dark vs light, node counts | **John** | Spikes 1, 2, 6 |

## Repo composition
- Templates: `docs/plan/brief.md` (before) and after-brief reusing diagram ids; replaces the earlier 1-2 page `brief.md` size and stays the file John signs (E37, E38).
- Model file: small `architecture.yaml` (or `.json`) referenced by path from the plan, never imported in CLAUDE.md; links service nodes to `integrations.yaml` ids (E39; synthesizer inference).
- Skill (researcher plugin): extend `system-map` with as-is input contract, to-be view via `classDef`, model file with parity check, agent counterpart output, content validation, dark theme and contrast check, SVG output kept in a stable place, sequence rules, open-questions path parameter, default checker run (Q7, E108-E116).
- Hooks: mermaid-lint in PostToolUse or Stop (E71). Scripts: generator wrappers (n8nmermaid, docker-compose-to-mermaid or own transforms), contrast check, parity check.
- Files: committed `.mmd` source plus SVG; generator header per generated diagram.
- Superpowers/Beads/Ralph: not discussed in this findings file.

## Spikes
| Spike | Probe (what to run) | Pass criterion |
|---|---|---|
| 1 | Mermaid fences in claude.ai project files and a published page, on John's phone, vs inline SVG | Records which renders; no source found |
| 2 | Dark diagram through pinned mermaid-cli in the cloud environment; contrast computed; viewed on phone vs light | Renders headless; contrast floors met; John's polarity preference recorded |
| 3 | John reads one real three-page brief on his phone and explains each page | Time and count of rewritten passages recorded |
| 4 | Same change from the model file vs the rendered image on one of John's systems | Scored against a fixed checklist |
| 5 | Parity check on a model of one real system across three changes | Model stays updated; check catches drift |
| 6 | 6-9, 10-15 and about 25-line diagrams on the phone | Legible without pinch-zoom; node-count target chosen |
| 7 | mermaid-cli SVG output in two environments | Byte-stable or not; decides gating on SVG |
| 8 | n8nmermaid and docker-compose-to-mermaid on John's n8n workflows and compose files | Usable Mermaid after lint and trim |
| 9 | Unattended run commits brief; interactive or Remote Control session publishes | `/login` requirement confirmed; hand-off works |
| 10 | GitHub's current Mermaid version via its docs snippet | Version recorded |
| 11 | Structurizr MCP export to Mermaid without local Java (only if wanted) | Export works or not |

## Requirements served
- R22: three-page, mostly-diagram, dark-theme brief before and after each project covering how it works, stack and key locations, what John must do, plus a machine-oriented YAML model for the agent (Q2, Q6, Q8).
- R5: plain context-level flowcharts with legend and numbered text for a non-technical reader (E1, E4, E14).
- R6: as-is input contract for system-map; after-brief diagram drawn from the code (Q7 gap 1; Q2).
- R8: model file referenced by the plan; before-brief is the signed file (E37).
- R9: model updated in the same commit as any system change; CI drift check (Implications; E70).
- R11: page 3 "What I need from you" checklist and page 2 key locations by name (Q2).
- Q2: model file read by path so a fresh session can resume (Q6).
- Q5: John's brief capped at three pages; agent file sized small and kept out of CLAUDE.md (E100, E106).
- Q4: after-brief built from observed facts, unverified items marked (Q2, worker inference).

## GTM scenario
- Scan as-is: system-map takes the as-is map as a named input (Q7 gap 1); n8nmermaid draws John's n8n workflows (E68, spike 8).
- Fix Attio tables and views: to-be/change view marks new, changed and removed boxes (Q7 gap 2); no Attio generator - gap.
- Set up Clay workflows: gap (no generator; diagram written from the model).
- Clean data: gap.
- Finish tooling: before-brief for approval and after-brief "what differs from the plan" and "what to watch" (Q2).

## Tensions
- Publishing: unattended API-key or `-p` sessions cannot publish (E53), so R22's phone-readable page needs an interactive `/login` or Remote Control step, against R15 hands-off running. Requirements also list "Max subscription unattended on a server" as unverified; whichever auth the runtime area picks decides whether publishing is possible.
- The earlier planning findings sized `brief.md` at 1-2 pages (E38, worker inference); this area replaces it with three pages per John's cap (Q2).
- Dark polarity: Dobres 2017 finds white-on-black harder to read in dim light, worse at small sizes (E45, E46); John asked for dark; the opposing Tai 2013 source is excluded (open q 4). Unresolved, spike 2. Suggested dark colour values are uncomputed worker inference (Q3).
- GitHub dark Mermaid breaks when dark is implied by system setting (E57), so committed Mermaid may need a neutral theme while the artifact is dark (worker inference, untested).
- Node count: system-map caps diagrams at about 25 lines (E109); workers disagree on 6-9, 10-15 or about 25 for a phone (open q 21; spike 6).
- Plain Mermaid vs Structurizr model consistency (E92, vendor claim) unresolved; repo forbids C4 syntax (Q6).
- Text over image rests mostly on Exa search text and 2024-2025 models (E77-E89, open q 18-19); GraphTMI dissents for large graphs (E86).
- Keeping overviews out of CLAUDE.md rests on E100-E101 (Exa search text) and left open in engineer-existing-systems.md:415 (E107); OpenReview abstract says context files "tend to reduce" success (open q 9, not opened).
- Mermaid ELK default (v12, E75) vs `dagre` default (excerpt only) unresolved (Q5); advice unaffected.
- Mermaid rendering in claude.ai project files or the phone app is unknown (open q 17; spike 1); 50,000/500 limits on GitHub rest on a third-party doc (E73).
- mermaid-cli needs headless Chromium (E58); offline rendering in the engineer environment untested (open q 20).

## Open for John
- Dark vs light after the phone test (spike 2), given E45-E46.
- Who publishes the brief: John's own `/login` session, or a Remote Control session he approves (spike 9).
- Whether C4 model rules matter enough to adopt Structurizr (spike 11).
- Accepting the three-page brief as the signed file, with signed parts on pages 1 and 3 (Q2).
