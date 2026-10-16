# Elicitation methods for non-experts

Brief: Which requirements-elicitation methods designed for non-expert users produce testable requirements and transfer to an LLM-run intake, and which question styles and stopping rules get the most information per question?
Run: research/runs/engineer-intake/PLAN.md

All sources opened 2026-10-16 with Parallel web_fetch (excerpt mode). Today is 2026-10-16.

## Which methods work with non-experts, what do they produce, is there LLM adaptation?

### Takeaway
EARS (Kiro) and Volere fit criteria are the two methods with direct evidence of producing testable output and of being used in LLM spec flows; JTBD timeline and story-map backbone are interview structures, not output formats. Five whys and goal modelling: no source opened (Gaps). Academic LLM interviewers exist (LLMREI, OntoAgent, ELISA) but are tested on simulated stakeholders, not on non-experts dictating by voice. Confidence: medium.

### Cited findings
- EARS is a small set of clause patterns (trigger, precondition, system, response) written in plain English — https://alistairmavin.com/EARS, opened 2026-10-16, Parallel web_fetch — Quote: "When <trigger>, the <system name> shall <system response>"
- EARS ruleset constraints — https://alistairmavin.com/EARS, opened 2026-10-16, Parallel web_fetch — Quote: "a requirement must have: Zero or many preconditions; Zero or one trigger; One system name; One or many system responses."
- Kiro (an LLM coding agent product) generates requirements.md as user stories plus EARS behaviours, and claims EARS is testable and readable by non-technical stakeholders (vendor claim, page dated 2026-09-25) — https://kiro.dev/docs/specs/feature-specs/requirements-first/, opened 2026-10-16, Parallel web_fetch — Quote: "Unambiguous and testable; Easy to translate into test cases; Traceable through implementation; Clear for both technical and non-technical stakeholders"
- Volere makes a requirement testable by a fit criterion; no fit criterion means the requirement is unclear — https://www.reqview.com/blog/2019-02-27-news-volere-requirements-specification-template (secondary, 2019 blog on the Volere template), opened 2026-10-16, Parallel web_fetch — Quote: "If a fit criterion cannot be found for a requirement, then the requirement is either ambiguous or poorly understood. All requirements can be measured, and all should carry a fit criterion."
- Volere types include constraints (budget, time, skills) — same URL — Quote: "Constraints impose restrictions on the chosen solution. These restrictions might apply to the whole project, for example: budget, time, skills."
- JTBD switch interview: users misreport when things began, so the interviewer probes backward along a timeline (2026-06-04 page) — https://jobstobedone.org/the-timeline/, opened 2026-10-16, Parallel web_fetch — Quote: "Keep probing backward, asking “what was going on before that?”, until you reach the true beginning."
- JTBD timeline doubles as a gap tracker during the interview — same URL — Quote: "The timeline gives you a structure to organize the story even as it comes out in pieces, so you always know where the gaps are."
- Story mapping frames breadth first — https://www.jpattonassociates.com/wp-content/uploads/2015/03/story_mapping.pdf, opened 2026-10-16, Parallel web_fetch — Quote: "Focus on getting the whole story. Think “mile- wide, inch deep”"
- LLM adaptation exists: LLMREI (arXiv 2507.02564, July 2025) used GPT-4o prompts in 33 simulated interviews with students as stakeholders; error rate similar to human students — https://arxiv.org/html/2507.02564v1, opened 2026-10-16, Parallel web_fetch — Quote: "LLMREI makes a similar number of errors compared to human interviewers, is capable of extracting a large portion of requirements"
- LLMREI fine-tuning on interview transcripts failed; prompting beat it — same URL — Quote: "the non-fine-tuned models clearly outperformed the fine-tuned ones."
- Free-form LLM interviewing is weak at implicit requirements (ReqElicitGym, Feb 2026, 101 website scenarios, 7 LLMs) — https://arxiv.org/abs/2602.18306v1, opened 2026-10-16, Parallel web_fetch — Quote: "they elicit less than half of the users' implicit requirements, and their effective elicitation questions often emerge in later turns of the dialogue."
- Structured slot ontology beat free-form chat (OntoAgent, May 2026; GPT-5.1; web-app domain only) — https://arxiv.org/html/2605.05828, opened 2026-10-16, Parallel web_fetch — Quote: "OntoAgent achieves an IRE of 0.69, outperforming all baselines. The strongest baseline ( i.e., Mistake-guided Prompting) reaches 0.52."
- ReqElicitGym style requirements are the hardest category — https://arxiv.org/abs/2602.18306v1 — Quote: "consistently struggle with style-related requirements."

### Contradictions
- None found. (Vendor claim that EARS is clear to non-technical people is not independently tested in anything I opened.)

### Inferences
- (Mine) A non-expert cannot write EARS, but an LLM can draft EARS or Given/When/Then lines from the story John tells and read them back in plain words; John's role is confirm/correct. Rests on Kiro flow and Volere fit-criterion rule.
- (Mine) Use JTBD "last time" timeline as the question style and a story-map backbone ("mile wide, inch deep") as the first-pass coverage structure, then EARS plus a fit criterion as the output layer.
- (Mine) Since free-form LLM chat finds under half of implicit requirements and finds them late, the intake should carry a fixed slot list (like spec-kit's taxonomy below) rather than rely on the model's improvisation.

### Gaps
- Five whys, goal modelling (KAOS/i*) as non-expert methods: no source opened; not claimed.
- No study found of any of these with non-experts using an LLM interviewer by voice; all LLM studies use simulated or student stakeholders.
- Mavin's IEEE 2009 EARS paper (https://ieeexplore.ieee.org/document/5328509) not opened; only the author's own page used.

## Question styles: open vs closed, playback-and-correct, "last time"

### Takeaway
Primary evidence (NN/g, 2022 and 2024) says start open and specific-past ("tell me about the last time"), use closed questions only for detail and clarification, avoid "because" leading probes and compound questions. For playback there is evidence from voice-dialogue and LLM-interview work on read-back and one-question-at-a-time, but no study of requirements playback with non-experts. Confidence: medium.

### Cited findings
- Open questions find unanticipated things — https://www.nngroup.com/articles/open-ended-questions/ (page dated 2024-02-05), opened 2026-10-16, Parallel web_fetch — Quote: "The greatest benefit of open-ended questions is that they allow you to find more than you anticipate."
- Closed questions as clarifiers, not drivers — same URL — Quote: "Use closed questions to gather additional small details, gain clarification, or when you want to analyze responses quantitatively."
- Closed questions can lead — same URL — Quote: "Leading closed questions often start with the words “did,” “was,” or “is.” Open-ended questions often begin with “how” or “what.”"
- Funnel: broad open first, then specific closed — same URL — Quote: "researchers use the funnel technique, where the session or followup questions begin with broad, open-ended questions before introducing specific, closed questions."
- Prefer specific examples over typical behaviour; a grand-tour opener is fine — https://www.nngroup.com/articles/interview-questions-mistakes/ (2022-03-03), opened 2026-10-16, Parallel web_fetch — Quote: "It’s much better to ask about specific examples than to ask them to describe what they think is typical."
- Hypotheticals are unreliable — same URL — Quote: "people are bad at predicting their future behavior or choices — but they’ll likely have a good answer for you!"
- Do not offer interpretations with "because" — same URL — Quote: "avoid asking questions that use the word ‘because.’"
- One question at a time — same URL — Quote: "keep questions short and concise, and don’t ask people to tell you what they did and why; that’s what followup and probing questions are for!"
- LLM interviewer failure mode matches that rule — https://arxiv.org/html/2507.02564v1, opened 2026-10-16, Parallel web_fetch — Quote: "the bot often asked multiple questions simultaneously, overwhelming stakeholders."
- Mom Test rules (secondary summary dated 2026-06-24, not the book) — https://hellopm.co/book-summary-the-mom-test-by-rob-fitzpatrick appeared in search only; NOT opened, so not cited. Search-only: see Gaps.
- spec-kit clarify uses multiple-choice with a recommended option or a 5-word answer, plus "yes/recommended" acceptance — https://github.com/github/spec-kit/blob/main/templates/commands/clarify.md, opened 2026-10-16, Parallel web_fetch — Quote: "Each question must be answerable with EITHER: A short multiple‑choice selection (2–5 distinct, mutually exclusive options), OR A one-word / short‑phrase answer"
- Same file asks the model to explain stakes in plain language — Quote: "add one plain-language \"Why it matters\" sentence (the stake for acceptance or shipping) before the recommendation/options."

### Contradictions
- NN/g says closed questions are sparing and can lead — https://www.nngroup.com/articles/open-ended-questions/; spec-kit clarify is almost entirely closed (multiple choice, <=5 words) — https://github.com/github/spec-kit/blob/main/templates/commands/clarify.md. They address different phases (discovery vs gap-closing), not a true conflict. A spike should test whether a recommended-option choice biases John toward accepting the model's default (NN/g's leading-question warning applies).

### Inferences
- (Mine) Two-phase intake: open "tell me about the last time you wanted this / got stuck" phase driven by John's voice rant, then a closed gap-closing phase with recommended defaults, each question one item, each with a one-line "why it matters".
- (Mine) Playback should be of the drafted behaviours in John's words (not leading "because" restatements), with the correction path being free speech.

### Gaps
- Mom Test primary text, Bano et al. mistake taxonomy, and any quantitative information-per-question comparison of open vs closed questions: not opened or not found.
- No source found on playback-and-correct specifically in requirements elicitation.

## Stopping rules

### Takeaway
Three usable rules appear in sources: slot/coverage exhaustion plus a turn cap (OntoAgent: "no eligible slots remain ... or a predefined maximum number of turns"), a hard question cap with user-stop (spec-kit: 5 questions), and saturation by diminishing new items per respondent (PLOS ONE, which warns that strict saturation is not a good guide). Confidence: medium-high for the rules, low for which is best for a single-user intake.

### Cited findings
- Coverage-plus-cap stop — https://arxiv.org/html/2605.05828, opened 2026-10-16, Parallel web_fetch — Quote: "until no eligible slots remain in $\mathcal{T}$ or a predefined maximum number of turns is reached."
- Their experiments cap at 20 turns and key requirements arrive early — same URL — Quote: "often eliciting key implicit requirements within the first 3–5 turns, while free-form baselines typically exhibit prolonged stagnation in the initial dialogue phase."
- Pruning low-yield branches improved efficiency without hurting coverage — same URL — Quote: "the pruning does not harm coverage. Instead, it improves IRE"
- spec-kit stop rules — https://github.com/github/spec-kit/blob/main/templates/commands/clarify.md, opened 2026-10-16, Parallel web_fetch — Quote: "Stop asking further questions when: All critical ambiguities resolved early (remaining queued items become unnecessary), OR User signals completion (\"done\", \"good\", \"no more\"), OR You reach 5 asked questions."
- spec-kit defers leftovers explicitly — same URL — Quote: "If quota reached with unresolved high-impact categories remaining, explicitly flag them under Deferred with rationale."
- spec-kit coverage taxonomy statuses — same URL — Quote: "mark status: Clear / Partial / Missing."
- Saturation as stopping rule is shaky — https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0198606 (2018, across respondents, not turns), opened 2026-10-16, Parallel web_fetch — Quote: "The strict notion of complete saturation as the point where few or no new ideas are observed is not a useful concept to guide sample size decisions"
- Salience is the alternative — same URL — Quote: "Even small samples (n = 10) produced 95% of the most salient ideas with exhaustive listing"
- Saturation defined as new-items-per-unit threshold — same URL — Quote: "Saturation was defined as the point where less than one new item would be expected for each additional person interviewed."
- JTBD timeline: gaps visible while interviewing, so "no unfilled timeline gaps" is a coverage criterion — https://jobstobedone.org/the-timeline/ — Quote: "so you always know where the gaps are."

### Contradictions
- None found. Note the PLOS saturation work is about number of respondents, not questions per interview; transfer to per-question stopping is my extrapolation.

### Inferences
- (Mine) Recommended stop for John: stop when (a) every heading in the fixed coverage list is Clear or explicitly Deferred, or (b) John says done, or (c) a cap of roughly 5 gap-closing questions after the open rant (spec-kit) and 20 turns overall (OntoAgent); plus a diminishing-yield check: two consecutive answers add no new requirement or entity. (b)/(c) cited; the yield check is mine.

### Gaps
- No empirical study of information gained per question for any LLM interviewer beyond TKQR/IRE on website scenarios.
- Whether 5 questions is enough for John's larger projects: untested; needs a spike.

## What a finished intake artifact contains and which formats work downstream

### Takeaway
Evidence supports: user stories with EARS acceptance criteria (Kiro), a coverage/clarifications log inside the spec (spec-kit), and Volere-style type, rationale and fit criterion per requirement. I found no source on anti-goals or decision-log formats improving model performance; those are design choices, not evidenced. Confidence: medium-low.

### Cited findings
- Kiro requirements.md contents — https://kiro.dev/docs/specs/feature-specs/requirements-first/, opened 2026-10-16, Parallel web_fetch — Quote: "User stories with clear acceptance criteria; System behaviors in EARS format (WHEN...THE SYSTEM SHALL...); Functional requirements; Edge cases and error handling"
- Kiro example shows error-path EARS lines — same URL — Quote: "WHEN a user submits an email that already exists THE SYSTEM SHALL display \"Email already registered\" error"
- Kiro prompt (third-party extraction of an older prompt, not opened; unused) — search-only, see Gaps.
- spec-kit clarify writes answers back into the spec as a log and keeps them testable — https://github.com/github/spec-kit/blob/main/templates/commands/clarify.md, opened 2026-10-16, Parallel web_fetch — Quote: "Keep each inserted clarification minimal and testable (avoid narrative drift)."
- spec-kit ends with a coverage report — same URL — Quote: "Coverage summary table listing each taxonomy category with Status: Resolved (was Partial/Missing and addressed), Deferred"
- spec-kit taxonomy includes constraints and failure handling — same URL — Quote: "Edge Cases & Failure Handling: Constraints & Tradeoffs: Terminology & Consistency: Completion Signals:"
- Volere atomic requirement shell and separate definitions doc — https://www.reqview.com/blog/2019-02-27-news-volere-requirements-specification-template, opened 2026-10-16 — Quote: "Project Scope (SCOPE), Project Requirements (REQS), Project Issues (ISSUES) and Naming Conventions and Definitions (DEFS)"
- Kiro troubleshooting for vague specs — https://kiro.dev/docs/specs/feature-specs/requirements-first/ — Quote: "Include specific user scenarios and edge cases; Define clear success criteria"
- LLMREI had the bot produce an end-of-interview summary, which a prompt line improved — https://arxiv.org/html/2507.02564v1 — Quote: "the long prompt showed consistently better results in generating a final summary after completion of the interview."

### Contradictions
- None found.

### Inferences
- (Mine) Proposed artifact, assembled from the above: goal and user story; EARS requirements each with a fit criterion; acceptance scenarios; constraints (Volere constraint type); deferred/unknown list (spec-kit Deferred); glossary of confirmed entity names (Volere DEFS); decision log of John's answers with "recommended accepted" vs "own answer". Anti-goals as an explicit "shall not" section are my addition: EARS has no keyword for them beyond unwanted-behaviour patterns (not opened in detail).
- (Mine) Glossary and decision log double as the dictation-error fix (below).

### Gaps
- No evidence found that anti-goals, decision logs or acceptance scenarios improve a coding model's output; needs a spike (build the same feature from artifact variants and score).
- EARS "unwanted behaviour" pattern (If ... then ...) not verified from the opened page excerpt.

## Voice-dictated input: confirming entities without nagging

### Takeaway
Confirm sparingly and by risk: Google's conversation design guidance says explicit confirmation only when misunderstanding is costly (names, addresses); a 2026 benchmark shows voice agents capture lexical entities badly and that a prescribed read-back plus spelling step lifts accuracy 14-31 points at a time cost, while confirming every attribute frustrates callers. Batch the confirmations into one end-of-rant glossary playback. Confidence: medium (benchmark is simulated callers, English).

### Cited findings
- Use explicit confirmation sparingly — https://developers.google.com/assistant/conversation-design/confirmations, opened 2026-10-16, Parallel web_fetch — Quote: "Use sparingly, only when the cost of misunderstanding the user is high, for example, names, addresses, texts to be shared on the user’s behalf."
- Confirming everything is itself a cost — https://arxiv.org/html/2609.13602v1 (tau-Elicitation, 2026-09-15), opened 2026-10-16, Parallel web_fetch — Quote: "misunderstood named entities impede spoken dialogue, while confirming every attribute can itself frustrate callers"
- Scaffold of read-back/spelling/correction helps substantially — same URL — Quote: "A scaffold that prescribes spelling, read-back, correction, and confirmation raises robust $\mathrm{Pass}^{3}$ by 14–31 points, at a cost of 21–28 seconds per call."
- Coined names and similar are hardest — same URL — Quote: "Pooled $\mathrm{Pass}^{3}$ ranges from 1.7% for medications and 3.3% for coined names to 46.7% for phone numbers and 60.0% for dates"
- Models verify too little at the right moments and repair badly — same URL — Quote: "Agents often double down on an error or hallucinate a replacement rather than complete the repair."
- Text agent had no trouble, so the problem is the spoken channel — same URL — Quote: "A matched text run passes all 200 tasks, implicating spoken capture and repair rather than task understanding."
- Confidence-based mix of explicit and implicit confirmation is standard in spoken dialogue (older, CMU) — https://www.cs.cmu.edu/~dbohus/docs/bu.pdf, appeared in search only, NOT opened: not cited.
- Entity-error correction by retrieval of known entity lists then LLM correction reduces WER 33-39% on rare music entities (Sept 2024 arXiv 2409.06062) — appeared in search only, NOT opened: not cited.

### Contradictions
- None found. (Tension, not contradiction: Google says confirm rarely; tau-Elicitation says confirmation helps accuracy but costs time and annoyance. Resolve by risk-tiering.)

### Inferences
- (Mine) Note that John's input is dictation to text (his own STT), not a live voice agent; tau-Elicitation's voice-channel errors arise partly at the agent's own speech recognition, so the transfer is partial. The hazard that transfers is coined product names (OpenClaw, Stagehand, Gemini Argon 4 type words) being mis-transcribed.
- (Mine) Practical rule set: (1) keep a glossary seeded from tools/names John has already used and from the repo; fuzzy-match each unknown noun against it silently; (2) auto-accept high-confidence matches and log them; (3) batch low-confidence or coined names into ONE playback list at the end ("I heard these names: ... correct any"), with the model's best guess and the alternative; (4) never ask about generic words; (5) for names with irreversible cost (repo names, domains, paid services) require explicit confirmation.

### Gaps
- No source opened on handling very long dictated rants (segmenting, extracting requirements, deduplicating); nothing on STT custom vocabulary for Claude Code setups.
- Bohus/Rudnicky confirmation paper and the retrieval-correction paper seen in search but not opened.

## Recommendation, alternatives, rejected, spike (facet-level)

Recommendation: A two-phase intake in Claude Code. Phase 1: John rants by voice; the model asks "tell me about the last time" style open questions, one at a time, walking a JTBD-style timeline with a fixed coverage list (story-map backbone). Phase 2: gap-closing questions drawn from a spec-kit-style taxonomy (Clear/Partial/Missing), at most about 5, multiple choice with a recommended default and a "why it matters" line. Output: EARS requirements with fit criteria, acceptance scenarios, constraints, deferred list, glossary and decision log. One batched entity playback at the end. All of this is prompt and file structure, free, nothing to install.

Alternatives: adopt spec-kit clarify or Kiro-style flow directly (both free-form markdown; Kiro is a separate IDE, not adopted); OntoAgent-style ontology of slots induced from past scenarios (best measured gains, but web-app domain and needs scenario data).

Rejected: fine-tuning an interviewer (LLMREI abandoned it); pure free-form LLM chat (under half of implicit requirements, found late); asking John to write EARS himself; confirming every entity.

Spike before building: (1) run the same 3 past briefs of John's through the two-phase flow vs a free-form interview and count implicit requirements found and questions asked; (2) test whether recommended-default choices bias John's answers; (3) test glossary-based entity repair on a real dictated transcript with his tool names; (4) build the same small feature from artifact variants with and without anti-goals/decision log and score.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| spec-kit (clarify command template) | https://github.com/github/spec-kit/blob/main/templates/commands/clarify.md | Prompt template: coverage scan, max 5 questions, multiple choice, writes answers into spec | markdown command in a coding agent | 2026-10-16 | Reference design for gap-closing phase; read template only, not installed |
| Kiro specs (requirements-first) | https://kiro.dev/docs/specs/feature-specs/requirements-first/ | Generates user stories + EARS requirements.md | Kiro IDE (separate product) | 2026-10-16 | Borrow the output format; do not adopt the IDE (Claude Code is the engine) |
| EARS | https://alistairmavin.com/EARS | Five-pattern requirement syntax | notation, no install | 2026-10-16 | Use as output layer, model drafts and John confirms |
| Volere fit criterion / snow card | https://www.reqview.com/blog/2019-02-27-news-volere-requirements-specification-template | Per-requirement shell with fit criterion | template | 2026-10-16 | Use fit criterion and glossary ideas only |
| ReqElicitGym | https://arxiv.org/abs/2602.18306v1 | Benchmark with oracle user for LLM interviewers | local Python (not run) | 2026-10-16 | Possible later test harness; website domain only |
| OntoAgent | https://arxiv.org/html/2605.05828 | Ontology-guided interview agent, IRE 0.69 | research prototype (not run) | 2026-10-16 | Reference design; idea of slot pruning worth copying |
| LLMREI | https://arxiv.org/html/2507.02564v1 | GPT-4o interviewer chatbot prompts | research prototype (not run) | 2026-10-16 | Reference for prompt rules (one question at a time, final summary) |
| tau-Elicitation | https://arxiv.org/html/2609.13602v1 | Voice entity capture benchmark | research (not run) | 2026-10-16 | Evidence only |
