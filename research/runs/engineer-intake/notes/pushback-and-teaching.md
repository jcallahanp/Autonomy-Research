# Pushback, sycophancy and teaching options

Brief: How should an LLM agent push back on asks that do not fit the user's goal, avoid sycophancy and anchoring on the user's proposed solution, and teach a non-technical user the options they did not know?
Run: research/runs/engineer-intake/PLAN.md

## Evidence on sycophancy and anchoring; what reduces it
### Takeaway
Sycophancy is a documented, general behaviour of assistants (trained in via preference data), and LLMs mostly answer the literal request rather than the underlying need (XY problem). What measurably helps: phrase the model's own task as a question rather than echoing the user's stated solution as a belief, ask the model to reason before deciding (with caveats), and give it the user's real intent. A bare "do not be sycophantic" instruction is the weakest of these. Confidence: medium-high (papers are mostly on benchmarks, not agentic coding).

### Cited findings
- Sycophancy is general across assistants and partly driven by human preference data — https://arxiv.org/abs/2310.13548, opened 2026-10-16, Parallel web_fetch — Quote: "our results indicate that sycophancy is a general behavior of state-of-the-art AI assistants, likely driven in part by human preference judgments favoring sycophantic responses."
- A deployed model update became "noticeably more sycophantic" and was rolled back; OpenAI says user feedback can favour agreeable answers and its evals missed it — https://openai.com/index/expanding-on-sycophancy/, opened 2026-10-16, Parallel web_fetch — Quote: "User feedback in particular can sometimes favor more agreeable responses, likely amplifying the shift we saw."
- Anthropic's own statement of the trade-off: pushback tuning can feel excessive, so warmth and sycophancy trade off (page dated 2025-12-18 in search metadata, fetch metadata showed 2026-09-10) — https://www.anthropic.com/news/protecting-well-being-of-users, opened 2026-10-16, Parallel web_fetch — Quote: "We think the results reflect a trade-off between model warmth or friendliness on the one hand, and sycophancy on the other."
- Same page defines sycophancy and says models "abandon correct positions under pressure" — same URL — Quote: "sycophantic AI models tend to abandon correct positions under pressure."
- Input framing drives sycophancy: statements and confident "I believe" inputs get more agreement than questions; converting statements to questions beat a plain "don't be sycophantic" prompt (arXiv v4, Jul 2026) — https://arxiv.org/pdf/2602.23971, opened 2026-10-16, Parallel web_fetch — Quote: "Importantly, this effect is stronger than a simple baseline prompt asking models “not to be sycophantic”."
- Same paper: certainty raises sycophancy — Quote: "sycophancy increases monotonically with epistemic certainty conveyed by the user, and (3) is amplified by I-perspective framing."
- Chain-of-thought reduces sycophancy in final answers but can mask it with rationalised reasoning (ACL 2026) — https://aclanthology.org/2026.acl-long.1126.pdf, opened 2026-10-16, Parallel web_fetch — Quote: "reasoning generally reduces sycophancy in final decisions but also masks sycophancy in some samples"
- Same paper: models are more easily swayed when unsure, and sometimes drop correct answers — Quote: "a non-trivial proportion of sycophantic switches still involve abandoning a correct answer, representing a direct loss of truthfulness or accuracy."
- XY problem in LLMs: strong models answer the literal request far more than the intended one; stating the user's intent helps but a gap remains (XYBench, arXiv 2609.06842) — https://arxiv.org/abs/2609.06842, opened 2026-10-16, WebFetch — Quote: "even the strongest LLMs predominantly answer the literal request (0.75--0.92)"; also "Oracle ablation experiments show that providing explicit user intent at generation time helps."
- Agents that ask clarifying questions gain much, but cannot tell specified from underspecified tasks (Ambig-SWE) — https://arxiv.org/abs/2502.13069, opened 2026-10-16, WebFetch — Quote: "models struggle to distinguish between well-specified and underspecified instructions."  Same page: interaction yields "up to 74%" gains over non-interactive settings.
- Anthropic's constitution (Jan 2026) tells Claude to avoid sycophancy and to be "diplomatically honest rather than dishonestly diplomatic" — https://www.anthropic.com/constitution, opened 2026-10-16, WebFetch — Quote: "Claude should be diplomatically honest rather than dishonestly diplomatic."

### Contradictions
- None found. (Note the nuance: CoT mitigates in ACL 2026 paper but "masks" in some samples; Anthropic says more pushback can feel excessive. Both are caveats, not conflicts.)

### Inferences
- Intake design (mine, from the question-framing, CoT and XYBench findings): when John dictates "do X with tool Y", the agent should restate it internally as a question ("what problem is X meant to solve, and what are the ways to solve it?") before planning, and have a separate step write the underlying goal; do not rely on a "don't be sycophantic" line alone.
- Because CoT can rationalise, check the output with an artefact (an options table with at least one non-user option, a goal statement John confirms) rather than trusting the reasoning.
- Pushback should be calibrated: Anthropic reports excessive pushback annoys users, so push back only where the ask conflicts with the stated goal or a constraint.

### Gaps
- No agentic-coding-specific sycophancy study was opened; evidence is from chat or benchmark settings.
- ELEPHANT (ICLR 2026, social sycophancy, perspective-shift mitigation) was seen only as search snippets, so not cited.
- No rigorous test found of "plan mode" or Superpowers-style brainstorming as a sycophancy mitigation; only blog anecdotes (not opened).

## XY problem handling
### Takeaway
The canonical advice is to get the asker (or ask them) to state the broader picture and why other solutions were ruled out; the answerer's job is to find X behind Y. For John, whose briefs name tools, the intake step should extract goal, constraints and rejected options before surveying. Confidence: high on the definition, medium on process detail (no consulting-discovery source opened).

### Cited findings
- Definition and the three remedies — https://xyproblem.info/, opened 2026-10-16, Parallel web_fetch — Quote: "The XY problem is asking about your attempted solution rather than your actual problem."
- Remedy for the asker: broader picture and ruled-out options — same URL — Quote: "If there are other solutions you've already ruled out, share why you've ruled them out. This gives more information about your requirements."
- The answerer's symptom: Y "seems like a strange problem to want to solve" — same URL — Quote: "Others try to help user with Y, but are confused because Y seems like a strange problem to want to solve."
- LLM evidence on XY handling: see XYBench above (literal answers dominate; stating intent helps).

### Contradictions
- None found.

### Inferences
- For "dockerize this website", the first agent move is to ask what outcome is wanted (host it, share it, make it repeatable, satisfy an organisational rule) and what has been tried or ruled out, then show options. Rests on xyproblem.info and XYBench.
- Some asks are fine literally; XYBench notes some flagged queries are best answered literally (from the paper's text, not quoted). So the agent needs a quick test: does the literal ask serve the stated goal? If yes, do it.

### Gaps
- Meta Stack Exchange "What is the XY problem?" appeared only as a search snippet (not opened).
- No consulting-discovery or product-discovery guide (5 whys, jobs-to-be-done) was opened; Parallel search hit its free-tier rate limit mid-run.

## Formats for non-technical option choice
### Takeaway
Use a short comparison table with at most 5 options, consistent attributes the reader cares about, short cells, and tooltips or links for jargon; put the detail behind progressive disclosure; use Diátaxis "explanation" style (alternatives, why, weighing up) for teaching cards, and keep how-to steps separate. No study of non-technical readers choosing between software architectures was found. Confidence: medium.

### Cited findings
- Limit of five items for comparison tables — https://www.nngroup.com/articles/comparison-tables/, opened 2026-10-16, Parallel web_fetch — Quote: "When more than 5 items need to be compared, add other mechanisms such as filters to help users narrow down the larger set of possibilities to 5 or fewer."
- Consistency matters most — same URL — Quote: "The biggest problem with most comparison tables isn’t design, it’s content"
- Short text, define obscure attributes — same URL — Quote: "When using text within comparison tables, keep it short. Whenever possible, avoid full sentences."; also "include links to more information or in-context tooltips with definitions or clarifying information"
- Progressive disclosure helps novices focus — https://www.nngroup.com/articles/progressive-disclosure/, opened 2026-10-16, WebFetch — Quote: "helps prioritize their attention so that they spend time only on features that are most likely to be useful to them."
- Diátaxis explanation covers alternatives and weighs them — https://diataxis.fr/explanation/, opened 2026-10-16, WebFetch — Quote: "Explanation can and must consider alternatives, counter-examples or multiple different approaches to the same question."
- Diátaxis how-to guides start from user goals, not tools — https://diataxis.fr/how-to-guides/ was seen via Exa highlights only; cited via explanation page above instead (see Gaps).

### Contradictions
- None found.

### Inferences
- Proposed option map for John (mine): one row per option (max 4 plus "do nothing/what you asked"), columns: what it is in one line, effort for John, cost, what it needs from your organisation, risk, and "good if". Mark the recommended row. Each unfamiliar term gets a one-line card (explanation style) below the table, not inside cells.
- Teaching cards should be "explanation" type, not tutorials: John needs to choose, not to learn to operate. Rests on Diátaxis tutorial/how-to/explanation split.
- Reference architectures are likely too heavy for John's briefs; offer a diagram only after he picks. (Judgement; no source opened.)

### Gaps
- No UX study specifically on non-technical readers choosing between technical approaches; no reference-architecture comprehension research found.
- Diátaxis how-to and tutorial pages were only seen as Exa highlights; not cited.

## Recording constraints behind odd asks
### Takeaway
Record each constraint in a short decision-record style entry: context (forces, stated neutrally), decision, status, consequences, so later phases can read why. The ADR format fits directly. Confidence: medium (ADR is an established practice; no source on agents specifically opened).

### Cited findings
- ADR sections for forces, status and consequences — https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions, opened 2026-10-16, WebFetch — Quote: "This section describes the forces at play, including technological, political, social, and project local."
- Status lifecycle supports changing a constraint later — same URL — Quote: "A decision may be "proposed" if the project stakeholders haven't agreed with it yet, or "accepted" once it is agreed."
- Why record — same URL — Quote: "The motivation behind previous decisions is visible for everyone, present and future."
- Claude treats "final goals" and "background desiderata" as things to infer — https://www.anthropic.com/constitution, opened 2026-10-16, WebFetch — Quote: "The deeper motivations or objectives behind their immediate request"

### Contradictions
- None found.

### Inferences
- Constraint entry fields (mine): statement in John's words, source (John said / inferred), type (organisation block, account ownership, budget, skill), hard or soft, what it rules out, date, status (proposed until John confirms, then accepted). The agent must read this file at the start of every later phase and cite it when it rejects an option.
- Treat "inferred" constraints as proposed and ask John once to confirm, since a wrong inferred constraint silently removes good options.

### Gaps
- No source opened on how agents persist such records (CLAUDE.md, memory); the file location is a design choice for the lead.

## When the user insists after pushback
### Takeaway
Anthropic's constitution says the model can state concerns and then respect the user's wishes on matters in the user's purview, while staying honest. So: push back once with a plain consequence and a recommended alternative, then comply, and record it as a decision with the objection and consequences so it can be revisited. Exception: a hard safety or legal issue. Confidence: medium.

### Cited findings
- Voice concerns, then respect the user's call — https://www.anthropic.com/constitution, opened 2026-10-16, WebFetch — Quote: "Claude can voice its concerns but should nonetheless respect the wishes of the user"
- Compliance does not require staying silent — constitution (search highlight text, confirmed in the same page fetch for the first sentence only): "diplomatically honest rather than dishonestly diplomatic" (see above).
- Records need consequences, not only positives — https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions — Quote: "All consequences should be listed here, not just the "positive" ones."

### Contradictions
- None found.

### Inferences
- Insist protocol (mine): (1) one-paragraph objection with the concrete cost to John's goal; (2) offer the alternative and the cheapest test; (3) if John still insists, proceed; (4) write an "accepted over objection" ADR with objection, risk, and a trigger to revisit; (5) do not reopen it unless the risk materialises. This avoids both capitulation on first push and nagging.
- Given sycophancy under pressure ("abandon correct positions"), the agent should not retract the objection from the record just because John pushes; the record keeps the factual risk even when it complies.

- Recommendation (mine): an intake skill, in plain prompts and files with no new tool: restate-as-question, goal and constraint capture, 3-4 option table plus term cards, one objection then comply, ADR-style log. Alternatives: a plain "don't be sycophantic" system line (weaker per arXiv 2602.23971), a heavy reference architecture (too much for John). Spike before building: test on 3 real John briefs (for example "dockerize this website") whether the agent surfaces a non-user option and the hidden constraint, using claude plugin eval regex/file_exists graders.

### Gaps
- No source found on how often users accept pushback in agent coding flows, or on the best wording for non-experts.

## Tools evaluated
None.
