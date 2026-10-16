# Diagrams non-technical readers understand and the three-page template

Brief: Design the at-most-three-page, dark-theme project brief a non-technical owner (John) can read on a phone and explain back, before and after each project.
Run: research/runs/engineer-briefing/PLAN.md

Note on sources: Pages marked "WebFetch" were opened with WebFetch (the tool returns a model-summarised page, quotes inside it are verbatim). Pages marked "Exa" were read as page text returned by Exa search/fetch. Dates opened: 2026-10-16.

## Which diagram types do non-technical readers understand

### Takeaway
Use ONE C4 system-context-style diagram (people, the system, outside services) with a legend, a title and a verb on every arrow; add a short numbered flow list beside it. Evidence says plain text first then a diagram beats a diagram alone for untrained readers, and swimlanes/BPMN/sequence diagrams are not reliably read by untrained people. Confidence: medium (the evidence is mostly student experiments, 2011-2014, and Simon Brown's practitioner guidance).

### Cited findings
- C4 system context is meant for everyone — https://c4model.com/diagrams/system-context, opened 2026-10-16, WebFetch — Quote: "Everybody, both technical and non-technical people, inside and outside the software development team."
- Detail is deliberately low at context level — same URL — Quote: "Detail isn’t important here as this is your zoomed out view showing a big picture of the system landscape."
- Different levels for different audiences; context + container suffice for most — https://c4model.com/diagrams, opened 2026-10-16, WebFetch — Quote: "the system context and container diagrams are sufficient for most software development teams."
- Notation rules: title, legend, labelled lines, readable acronyms — https://c4model.com/diagrams/notation, opened 2026-10-16, WebFetch — Quote: "Every diagram should have a key/legend explaining the notation being used."
- Same page: line labels — Quote: "Every line should be labelled, the label being consistent with the direction and intent of the relationship."
- Same page: acronyms — Quote: "Acronyms and abbreviations (business/domain or technology) should be understandable by all audiences."
- Brown's list of failure modes of boxes-and-arrows (unexplained colour, mixed abstraction, missing context) — https://leanpub.com/read/visualising-software-architecture/failure-to-communicate, opened 2026-10-16, Exa — Quote: "Notation (e.g. colour coding, shapes, line styles, etc) is not explained or is inconsistent."
- Same page: stand-alone test (give it to someone, no narrative) — Quote: "give it to somebody else and ask them to interpret it without providing a narrative."
- Brown on the context diagram for non-technical people, and a legend like a map key — https://www.infoq.com/articles/agile-software-architecture-sketches-NoUML/, 2013, opened 2026-10-16, Exa — Quote: "It's the sort of diagram that you could show to non-technical people."
- Same page: "Including a simple key/legend on each diagram to explain the notation will help too."
- Brown: keep a technical and a non-technical variant of the same diagram, plus a large-font version — https://dev.to/simonbrown/visio-draw-io-lucidchart-gliffy-etc-not-recommended-for-software-architecture-diagrams-4bmm (2020), opened 2026-10-16, Exa — Quote: "A version without technical information, for non-technical people."
- Google design docs: system-context diagram is useful; docs must be short — https://www.industrialempathy.com/posts/design-docs-at-google/, opened 2026-10-16, WebFetch — Quote: "a system-context-diagram can be very useful"
- Business-process study (BPMN vs written use cases, 196 participants): untrained readers did not gain from the graphic alone; text first then diagram worked best — https://doi.org/10.1016/j.jss.2011.09.023 (2011), opened 2026-10-16, Exa — Quote: "BPMN on its own is not a sufficient way to present process designs, despite its success among those with training in process models."
- Same paper: ordering — Quote: "presenting a business process twice, in the sequence of a written use case set followed by its equivalent set of BPMN diagrams, was the most effective way to build up comprehension"
- Swimlanes (142 and 131 student responses): non-swimlane more effective, swimlane faster; handshake steps and visual cues help — https://jitm.ubalt.edu/XXV-4/article3.pdf, opened 2026-10-16, Exa — Quote: "non-swimlane diagrams are more effective overall in conveying information to stakeholders, but that swimlane diagrams are more efficient"
- UML sequence diagrams help only high-ability/experienced readers (112 participants, five experiments) — https://doi.org/10.1109/tse.2012.27 (2013), opened 2026-10-16, Exa — Quote: "sequence diagrams improve the comprehension of the modeled functional requirements in the case of high ability and more experienced participants."
- Diagrams beat prose for procedure-style content in a government study (flowchart/swimlane/timeline, readers were civil servants) — https://doi.org/10.1177/1050651917746459 (2017), opened 2026-10-16, Exa — Quote: "the diagrammatic format, compared to prose, significantly enhances comprehension accuracy and answering speed"
- Size: component diagrams are best understood at middle numbers of elements, worse when too many or too few — https://eprints.cs.univie.ac.at/4059/1/Empirical_Evaluation_of_the_Understandability_of_Architectural_Component_Diagrams.pdf (Javed/Stevanetic/Zdun, 2014), opened 2026-10-16, Exa search text (WebFetch could not extract the PDF) — Quote: "middle values of the number of components, links, elements, and symbols in the diagram significantly increase the architectural understandability compared to high or low values."
- Same paper: thresholds are only rough — Quote: "we consider the thresholds we found as rough indicators."
- Companion study: one box per relevant function beats too few or too many — https://doi.org/10.1109/qsic.2014.20 (2014), opened 2026-10-16, Exa — Quote: "each component in the architecture corresponds to one system's relevant functionality"

### Contradictions
- Swimlanes: "more effective" claim by proponents is unsupported — jitm.ubalt.edu paper says swimlane "more efficient" but less effective than non-swimlane; Passera 2017 finds diagrams (incl. swimlanes) beat prose for civil servants. Different readers and tasks; not settled for John.

### Inferences
- (Mine) For John the best diagram is a C4 context picture whose arrows read as plain sentences ("sends the nightly email via SendGrid"), with the same story as a numbered list beneath: this matches Brown's "stand alone" test and Ottensooser's text-then-diagram result.
- (Mine) Keep to roughly 6-9 boxes (inference from "middle values" finding; no study gives an exact number for phone screens). Split into two diagrams rather than exceed it.
- (Mine) Skip sequence diagrams and swimlanes in the brief; keep them in the engineer's own architecture file.

### Gaps
- No study found on diagram comprehension on a phone-sized screen, and no exact box-count threshold (the Univie PDF could not be text-extracted, so numeric thresholds unverified).
- arc42 Architecture Communication Canvas page https://canvas.arc42.org/architecture-communication-canvas/ returned 404; the index page https://canvas.arc42.org/ opened but listed no canvas sections. arc42 canvas content therefore not cited.
- DFD-specific comprehension research and "architecture haiku" not searched (budget).

## What belongs on each of three pages (and explain-back)

### Takeaway
The proposal holds up: page 1 how it works (one diagram plus numbered flow), page 2 stack, keys, what John sees, page 3 what John must do, risks/open questions, costs. Add at the top of page 1 a two-line plain "what and why", and put "not doing" on page 3 (Shape Up no-gos). Sources support short, forced-length, stand-alone narratives with explicit risks and exclusions; none prescribes this exact split. Confidence: medium.

### Cited findings
- Amazon narratives: six-page cap, readable with no prior knowledge — https://aws.amazon.com/blogs/startups/startup-advice-how-to-write-a-narrative/ (2019), opened 2026-10-16, WebFetch — Quote: "It is limited to a maximum of six pages (but can have a reasonable number of appendices)"
- Same page: readable by anyone — Quote: "anybody within your organization can read and understand it" (without "any prior knowledge of the proposal").
- Amazon PR/FAQ lengths and length as forcing function — https://www.aboutamazon.com/news/workplace/an-insider-look-at-amazons-culture-and-processes (2021), opened 2026-10-16, WebFetch — Quote: "The press release (PR) portion is a few paragraphs, always less than one page."
- Same page — Quote: "restricting the length of the document is, to use a term that came up when describing the narratives, a forcing function"
- Shape Up pitch ingredients (problem, appetite, solution, rabbit holes, no-gos) — https://basecamp.com/shapeup/1.5-chapter-06, opened 2026-10-16, WebFetch — Quote: "There are five ingredients that we always want to include in a pitch:"
- Shape Up on making the idea visible but not over-detailed — same URL — Quote: "Therefore we need some techniques to help people see the idea while still not going too far into irrelevant details."
- Shape Up: no-gos defined (Exa text of same chapter) — https://basecamp.com/shapeup/1.5-chapter-06, Exa — Quote: "Anything specifically excluded from the concept: functionality or use cases we intentionally aren’t covering to fit the appetite or make the problem tractable"
- Google design docs: sections and "short enough" — https://www.industrialempathy.com/posts/design-docs-at-google/, opened 2026-10-16, WebFetch — Quote: "1-3 page 'mini design doc'" (acceptable for smaller changes; 10-20 pages for larger projects).
- Google: goals and non-goals — same URL — Quote: "non-goals aren't negated goals"
- Teach-back, explain-back method: ask in own words; test of the explainer — https://www.health.tas.gov.au/professionals/health-literacy/health-literacy-workplace-toolkit/spoken-communication/checking-understanding, opened 2026-10-16, Exa fetch — Quote: "This isn't a test of the consumer's knowledge; it's a test of how well you've communicated."
- Same page: avoid yes/no — Quote: "Teach-back works better than asking 'yes' and 'no' questions like \"Do you understand?\""
- Same page: chunk and re-explain — Quote: "'Chunk' your information into small sections."
- Teach-back toolkit: use own words, not "repeat back" — https://teachbacktraining.org/about-teach-back/10-elements-of-using-teach-back-effectively-detailed-version/, seen as Exa search text only, 2026-10-16 — Quote: "Do not ask the person to “repeat back.”"
- Brown: diagrams should stand alone — see question 1.

### Contradictions
- Length: Amazon allows six pages, Google "1-3 page mini design doc" for small changes, PR under one page. None is for a phone; John's three-page cap is stricter than all three. Not a conflict, a design choice.

### Inferences
- (Mine) Page 1: "In one sentence" + context diagram + 5-8 numbered flow steps. Page 2: stack table (part, what it does, who pays), where each key lives (name and location only, never value), what John sees (screens, emails, messages, in the words he will see them). Page 3: "What I need from you" (checklist with dates), "Not doing", risks/open questions (each with what the engineer will do if it happens), monthly cost and one-off cost.
- (Mine) Explain-back built in: end each page with 2-3 "In your own words" prompts John answers to the engineer in chat; the engineer flags gaps and rewrites the unclear passage (wording follows the Tasmanian toolkit: test of the document, not of John). No source tests teach-back for software briefs; this is an adaptation from health literacy.
- (Mine) Shape Up "appetite" maps to a one-line time and cost budget on page 3; "rabbit holes" map to risks.

### Gaps
- Amazon "narratives convey ~10x" claim was only seen in a search excerpt (a16z podcast) and is not cited.
- arc42 canvas and ADR/RFC templates (Rust RFC, Python PEP) not opened; comparison with them rests only on Google and Shape Up.
- No evidence found on whether non-technical owners actually retain more from 3 pages than 1 or 6; page counts are a design choice.

## Before versus after brief

### Takeaway
Same three-page skeleton; the after-brief swaps "plan" for "what exists", adds a plan-versus-actual table (scope, cost, time), and shifts page 3 to "what to watch" and handover. Project-closeout templates confirm the standard content: baseline versus actual with explanation of variance, outstanding issues, lessons learned. Confidence: medium (templates are generic project-management, not software-agent specific).

### Cited findings
- Closeout templates compare initial with actual and explain variance for goals, schedule and cost — https://www.smartsheet.com/sites/default/files/2023-08/IC-Project-Closeout-11813_PDF.pdf, opened 2026-10-16, Exa — Quote: "INITIAL GOALS AND DELIVERABLES ACTUAL GOALS AND DELIVERABLES EXPLANATION OF VARIANCE"
- Government closeout template: compare baseline to actual, brief enough for an unfamiliar reader — https://portal.ct.gov/-/media/Departments-and-Agencies/DSS/CT-METS/Library/General/CTDSSProjectCloseoutReportv11.pdf, opened 2026-10-16, Exa — Quote: "Compare baselines to actual and describe discrepancies."
- Same: audience — Quote: "Be brief, but provide enough detail so that any person not familiar with the project will have the necessary information"
- Prior run: John approves the owner-facing brief, not the architecture; approval bound to a hash — /home/user/Autonomy-Research/research/runs/engineer-planning/notes/plan-set.md:106 — Quote: "What John signs: (a) goals and non-goals, (b) scope list in plain words, (c) acceptance criteria as observable outcomes"

### Contradictions
- None found.

### Inferences
- (Mine) After-brief pages: 1 = "what was built" (the as-built diagram, drawn from the code, with changed boxes marked using the legend, not colour alone); 2 = "what differs from the plan" table (planned, actual, why, cost impact) and what John will now see; 3 = "what to watch": renewals and expiring keys, monthly cost actual vs estimate, known limits, who to ask, how to switch off. Use the same diagram ids as the before-brief so John can compare.
- (Mine) The before-brief should be the file John approves (plan-set.md approval hash); the after-brief is generated from it, so a diff of the two is mechanical.
- (Mine) An after-brief must be built from observed facts (tests run, URLs live) and mark anything unverified, otherwise it repeats the plan.

### Gaps
- No software-specific "as-built brief for a non-technical owner" source found; adaptation of PM closeout templates only.

## Dark theme and readability

### Takeaway
Dark theme is a preference with mixed evidence: some studies find light-on-dark harder to read at small sizes in dim rooms, others find it more comfortable. Therefore ship dark as default with contrast well above AA (aim 7:1+ for body, never pure #FFF on #000), body at least 17 pt equivalent on phone, a colour-blind-safe palette with shape/label redundancy, and a print/light export. Confidence: medium.

### Cited findings
- WCAG 1.4.3 thresholds — https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html, opened 2026-10-16, WebFetch — Quote: "has a contrast ratio of at least 4.5:1"
- Same: large text — Quote: "Large-scale text and images of large-scale text have a contrast ratio of at least 3:1;"
- WCAG 1.4.11: graphics and UI need 3:1 — https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html, opened 2026-10-16, WebFetch — Quote: "The visual presentation of the following have a contrast ratio of at least 3:1 against adjacent color(s):"
- Same: diagram parts — Quote: "Parts of graphics required to understand the content"
- Apple HIG iOS default 17 pt, minimum 11 pt — https://apple-docs.everest.mt/docs/design/human-interface-guidelines/typography/ (mirror of Apple's page; developer.apple.com page returned no text in search), seen in Exa search text 2026-10-16 — Quote: "iOS, iPadOS | 17 pt | 11 pt"
- Apple: allow 200% enlargement — https://apple-docs.everest.mt/docs/design/human-interface-guidelines/accessibility/, Exa search text — Quote: "give people the option to enlarge text by at least 200 percent"
- Dark-on-light advantage in dim light, larger at small sizes — https://www.sciencedirect.com/science/article/abs/pii/S0003687016302459 (Dobres et al., 2017), opened 2026-10-16, Exa fetch — Quote: "Under dark illumination, white-on-black text suffers a legibility disadvantage."
- Same: size interaction — Quote: "This disadvantage is more pronounced as text size decreases."
- Opposite finding for word-spelling task: negative polarity preferred/comfortable — https://doi.org/10.1167/13.9.1157 (Tai et al., VSS 2013 abstract), Exa search text 2026-10-16 — Quote: "subjects preferred display that is less stimulating to the eyes (i.e., negative polarity and black text on gray)."
- Okabe-Ito colour-blind palette hex codes — https://siegal.bio.nyu.edu/color-palette/, opened 2026-10-16, Exa fetch — Quote: "Masataka Okabe (Jikei Medical School) and Kei Ito (University of Tokyo) have devised a very nice palette that is color-blind friendly."
- Same page lists #E69F00, #56B4E9, #009E73, #F0E442, #0072B2, #D55E00, #CC79A7 (table rows).
- Notation: colour alone is ambiguous — Brown (leanpub, above) — Quote: "Can you work out what the colour coding means?"

### Contradictions
- Dobres 2017 (white-on-black harder to read under dark ambient light, worse for small text) — https://www.sciencedirect.com/science/article/abs/pii/S0003687016302459; disagrees with Tai 2013 (negative polarity preferred and more comfortable for word task) — https://doi.org/10.1167/13.9.1157. Setting (glance reading vs 3-minute tasks) differs; settle by a quick test on John's phone in his usual lighting.

### Inferences
- (Mine) Palette for dark background (~#121212 to #1A1D23, not pure black): body text #E6E6E6 or similar (contrast above 7:1, to verify with a contrast calculator in a spike); the Okabe-Ito hues (skipping black) for box categories, each also coded by shape or text label ("Your data", "Paid service") so colour is never the only cue. Verify every border and arrow reaches 3:1 against the background (WCAG 1.4.11).
- (Mine) Phone: render diagrams as vertical (top-to-bottom) SVG/PNG at 390 px width so text is at least 14-16 px after scaling; if a diagram has to be pinch-zoomed, it is too big. This follows the 17 pt default and the box-count finding; no source tests phone diagram legibility.
- (Mine) Provide a light-theme PDF export (print) from the same source; Mermaid or HTML with CSS variables suits this (registry: Mermaid Chart MCP). Print/PDF specifics were not researched.
- (Mine) Test: John explains page back on his phone; that is the real acceptance test, per teach-back.

### Gaps
- Print and PDF export guidance (page size, dark-to-light switch) not researched; no source opened.
- Contrast ratios for the chosen colours were not computed in this session.
- Material Design 3 dark-theme guidance page returned no usable text; dark-surface colour values unsourced.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| C4 model notation rules | https://c4model.com/diagrams/notation | Title, legend, labelled lines rules | notation, no install | 2026-10-16 | Use context level for John's page 1 with legend and verb labels; container level in the engineer's file |
| Okabe-Ito palette | https://siegal.bio.nyu.edu/color-palette/ | 8 colour-blind-safe colours | palette, no install | 2026-10-16 | Use for box categories on dark, with shape/label redundancy |
| WCAG 2.2 SC 1.4.3 / 1.4.11 | https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html | 4.5:1 text, 3:1 graphics | standard | 2026-10-16 | Use as floor; aim higher for body text |
| Teach-back method | https://www.health.tas.gov.au/professionals/health-literacy/health-literacy-workplace-toolkit/spoken-communication/checking-understanding | Explain-back check of understanding | method | 2026-10-16 | Use as the brief's acceptance test (prompts at page ends) |
| Shape Up pitch | https://basecamp.com/shapeup/1.5-chapter-06 | Five-ingredient pitch | template | 2026-10-16 | Borrow no-gos, appetite, rabbit holes |
| Amazon six-pager / PR-FAQ | https://www.aboutamazon.com/news/workplace/an-insider-look-at-amazons-culture-and-processes | Length-capped narrative | template | 2026-10-16 | Borrow forced length and FAQ-of-risks idea; skip six pages |
| arc42 canvas | https://canvas.arc42.org/ | Architecture canvases | template | 2026-10-16 (index only; sub-page 404) | Not evaluated beyond index; skip |
