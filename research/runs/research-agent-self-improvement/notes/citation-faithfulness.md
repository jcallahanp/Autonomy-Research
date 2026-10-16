# Citation faithfulness techniques and failure rates

Brief: Find which techniques measurably raise citation faithfulness in LLM research agents, and how often citations fail without them, so the researcher, synthesizer and verifier can be tightened.
Run: research/runs/research-agent-self-improvement/PLAN.md

## How often do deep-research systems and answer engines cite pages that do not support the claim?

### Takeaway
Often. Measured unsupported-claim rates run from about 12% (best system) to 97% (worst) in DeepTRACE (Sep 2025), and 23% to 76% of citations were factually unsupported across 14 models in "Cited but Not Verified" (May 2026). Dead links are rare (0 to 6% for frontier models), so link checks give false comfort. Confidence: medium (LLM-judge based, judge agreement with humans only moderate).

### Cited findings
- DeepTRACE (arXiv 2509.04499v1, submitted 2 Sep 2025; 303 queries x 9 systems): unsupported statements / citation accuracy were Perplexity GSE 47.0%/39.8%, Perplexity DR 97.5%/58.0%, You.com GSE 30.8%/68.3%, YouChat DR 74.6%/72.3%, GPT-5 DR 12.5%/79.1%, Gemini DR 53.6%/50.3%, Copilot Bing 23.1%/65.8%, Copilot Think Deeper 90.2%/62.1%. The abstract states citation accuracy of "40-80% across systems". — https://arxiv.org/html/2509.04499 and https://arxiv.org/abs/2509.04499, opened 2026-10-16, WebFetch
- DeepTRACE's factual-support judge correlated only 0.62 (Pearson) with manual labels on 100 tasks, which the authors call moderate. — https://arxiv.org/html/2509.04499, opened 2026-10-16, WebFetch
- "Cited but Not Verified" (arXiv 2605.06635, May 2026; 130 queries, 14 models), derived from its Table 1: factually unsupported citations were Claude Opus 4.5 23.2%, Haiku 4.5 31.1%, Sonnet 4.6 41.3%, GPT-5.2 41.2%, Opus 4.6 45.8%, GPT-5.4 52.3%, Gemini 3.1 Pro 51.5%, OSS-120B 75.6%. Dead links 0 to 6% and irrelevant 4 to 19% for frontier models. "Fact Check" scores 0 for contradicted, absent or uncertain claims, so the figure includes uncertain cases. — https://arxiv.org/html/2605.06635v1, opened 2026-10-16, WebFetch
- Same paper: more search does not help. GPT-5.4 unsupported claims rose from 21.4% to 83.3% going from 2 to 150 tool calls; Opus 4.6 from 20.0% to 42.1%. It says surface metrics (link validity, relevance) "mask factual failures". — https://arxiv.org/html/2605.06635v1, opened 2026-10-16, WebFetch
- L-MARS legal QA audit (arXiv 2509.00761v4; n=100 questions, about 600 claims per condition): even with a multi-turn judge loop, unsupported claims were 36 to 54% and no-citation 13 to 37%; strict citation F1 only 0.13 (naive RAG) to 0.25. — https://arxiv.org/html/2509.00761v4, opened 2026-10-16, WebFetch

### Contradictions
- DeepTRACE reports Gemini DR citation accuracy as 50.3% in Table 1 but 40.3% in the Section 4 text. — https://arxiv.org/html/2509.04499, opened 2026-10-16. Check the PDF to settle (not readable in this session).

### Inferences
- (mine) Rates vary 4x by model and setup, so the plugin should assume a baseline of roughly 20 to 50% unsupported citations from an unverified worker and design the verifier for that, not for rare errors. Rests on the DeepTRACE and Cited-but-Not-Verified tables.
- (mine) A verifier that only checks URLs resolve (dead-link check) catches under 6% of failures. Change: plugin/agents/verifier.md must fetch the page and compare claim to passage, not just check status.

### Gaps
- Per-system DeepTRACE figures came from an HTML render summarized by WebFetch; PDF (https://arxiv.org/pdf/2509.04499) was unreadable (compressed stream), so numbers are not cross-checked against the PDF.
- DeepResearch Bench FACT method numbers were not opened; search surfaced only citation to it. No FACT citation-accuracy figures are cited here.

## Which techniques improve faithfulness, and by how much?

### Takeaway
Best measured: pass raw single-document snippets rather than synthesized notes to the writer (citation precision 87.6 to 94.1, recall 64.5 to 69.7), and add an explicit "no claim without citation" instruction (recall 69.6, precision 91.0). Anthropic's Citations API guarantees valid pointers and `cited_text` is free of output tokens but is not shown to ensure entailment. Quote-first and retract-if-no-quote are vendor-recommended without published effect sizes. Judges are only moderately reliable. Confidence: medium for the first, low for the others.

### Cited findings
- Replacing synthesized researcher notes with raw single-document snippets for the orchestrator (AI-Q, 50 DeepResearch Bench examples) raised citation recall 64.5 to 69.7 and precision 87.6 to 94.1 with RACE quality unchanged (52.6 to 52.4). Adding "do NOT use information which is not backed by citations" gave recall 69.6, precision 91.0. Judge agreement with arbitrated humans was 76% (kappa 0.62); agent-level results rest on 20 examples. — https://arxiv.org/html/2608.24306v1, opened 2026-10-16, WebFetch (first 100k of 156k chars read)
- Anthropic Citations API: citations are parsed into structured blocks so they "are guaranteed to contain valid pointers to the provided documents"; `cited_text` does not count toward output or subsequent input tokens; in Anthropic's own evaluations it is "significantly more likely to cite the most relevant quotes" than prompt-only citing (no number given). Citations cannot be combined with structured outputs (400 error). — https://platform.claude.com/docs/en/build-with-claude/citations, opened 2026-10-16, WebFetch (saved output grepped)
- Anthropic hallucination guide: for long documents (>20k tokens) extract word-for-word quotes first; after drafting, find a supporting quote for each claim and retract the claim if none is found; best-of-N comparison and "I don't know" permission also listed. It states techniques "don't eliminate them entirely". No effect sizes given. — https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations, opened 2026-10-16, WebFetch
- L-MARS: a multi-turn judge loop with cross-provider verifier lifted strict citation F1 from 0.131 to 0.254 (95% bootstrap CI excludes zero) and cut no-citation from 34% to 13%. A source-identity fix ("Faith-Search") gave no significant gain (delta +0.033, CI overlaps zero). — https://arxiv.org/html/2509.00761v4, opened 2026-10-16, WebFetch
- Attribution-checker reliability: in L-MARS, human vs Gemini verifier kappa was 0.458 (strict binary, n=65) and 0.219 (3-class), below the paper's 0.55 gate; two LLM families agreed at kappa 0.683 (n=57). DeepTRACE's judge r=0.62. — https://arxiv.org/html/2509.00761v4 and https://arxiv.org/html/2509.04499, opened 2026-10-16, WebFetch
- Cited-but-Not-Verified recommends ensemble LLM judges or hybrid rule-based plus LLM checks to reduce single-judge bias. — https://arxiv.org/html/2605.06635v1, opened 2026-10-16, WebFetch

### Contradictions
- None found.

### Inferences
- (mine) Exact-quote requirement: plugin/agents/researcher.md should require each finding to carry a verbatim supporting sentence copied from the fetched page before the claim is written (quote-first), because it makes the later check mechanical (string match, then entailment). Rests on Anthropic guide plus the snippet result. Effect size unmeasured; treat as low-confidence but cheap.
- (mine) plugin/skills/research/note-schema.md: add a `Quote:` field to each Cited findings line (one sentence, verbatim) and keep the "no URL, no claim" rule. Rests on the snippet-vs-synthesis result (precision +6.5 points).
- (mine) plugin/agents/synthesizer.md: add the citation-only instruction ("do not use information not backed by a cited line") and forbid new numbers not in a note. Rests on AI-Q instruction result (precision 87.6 to 91.0).
- (mine) Citations API fits only if the pipeline passes fetched pages as document blocks via the API; Claude Code subagents do not, so the plugin cannot rely on it. Not verified whether Claude Code exposes it; treat as out of scope for plugin/agents/*.md and note as a future option.
- (mine) Do not use a single LLM verdict as ground truth: plugin/agents/verifier.md should use a different model or fresh context from the writer and treat "uncertain" as fail. Rests on kappa 0.46 and r=0.62 results.

### Gaps
- No source found giving a measured effect size for quote-first extraction alone, or for claim-decomposition + re-verification alone in research agents. "Faithful by Construction" (arXiv 2606.23989) claims quote-anchored claim structure but its PDF was unreadable (compressed), so nothing is cited from it.
- No measured effect size for Anthropic Citations API vs prompting beyond the vendor's qualitative statement.

## What should a verifier sample, and how?

### Takeaway
No paper tested sampling schemes for a verifier directly. The evidence supports checking every high-risk claim (numbers, quoted text, single-source claims, deep-search-derived claims) and a random sample of the rest, with a fresh fetch of the page and an entailment check against a verbatim quote; on mismatch, retract or downgrade the claim and widen the sample for that worker. Confidence: low (mostly inference).

### Cited findings
- Judge samples in the literature are small: human audit n=65 (5 claims per condition x label cell, stratified), cross-model check n=57 stratified, Bar Exam audit n=100 questions. Stratified, not simple random, sampling was used. — https://arxiv.org/html/2509.00761v4, opened 2026-10-16, WebFetch
- Failures concentrate by stage: researchers and multi-document searchers made mistakes in 46 to 71% of sampled sentences; single-document snippet searchers only 0.9 to 6.4%; TrajectoryKit's orchestrator attached fabricated precise statistics to sources lacking them. — https://arxiv.org/html/2608.24306v1, opened 2026-10-16, WebFetch
- Verification must fetch the source live; in L-MARS, Gemini and a human disagreed on reachability for 15 of 20 and 10 of 15 URLs because of fetch environment and link drift. — https://arxiv.org/html/2509.00761v4, opened 2026-10-16, WebFetch
- Anthropic's guide: unfound supporting quote means retract the claim. — https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations, opened 2026-10-16, WebFetch

### Contradictions
- None found.

### Inferences
- (mine) plugin/agents/verifier.md: risk-weighted rule. Check 100% of claims containing numbers, dates, names, direct quotes, or resting on one source; plus a random 20% (minimum 5) of remaining claim-URL pairs per note. The thresholds are my choice, not from a source; with per-claim error 20 to 50% (above) a random 5 pairs would find at least one failure with probability 67 to 97%, which is why 5 is the floor.
- (mine) On any mismatch: label it (unreachable, irrelevant, partial, unsupported), strike or downgrade the claim in findings, and re-verify all claims from that same note (error clusters by worker/stage). Edit verifier.md and plugin/skills/research/findings-format.md (add a Verification section listing sampled pairs, results, retractions).
- (mine) Verifier should re-fetch the URL itself (not trust the worker's quote), then judge entailment of the claim by the quote plus page, with unreachable counted as fail (strict-ALCE convention).

### Gaps
- No paper on optimal sampling rate for claim-URL pairs in agent pipelines found.

## What failure modes are specific to multi-stage pipelines (worker note, synthesizer, verifier)?

### Takeaway
The synthesizer/orchestrator is the main source of final-report citation errors (53 to 100% of errors across three systems), and synthesized intermediate notes are less faithful than raw snippets. Also, a verifier that shares the writer's model or sees the writer's output inherits its errors. Confidence: medium.

### Cited findings
- Origin of final-report errors: AI-Q orchestrator 84.7% (researcher 14.8%); MS-Agent orchestrator 52.6% (reporter 47.4%); TrajectoryKit orchestrator 100%. Orchestrator errors are mostly citation-related; in AI-Q hallucinations were about 31% of final-report errors, TrajectoryKit about 95%. Error types: hallucination, uncited input reliance, uncited output, insufficient citations, and snippet missing context. — https://arxiv.org/html/2608.24306v1, opened 2026-10-16, WebFetch
- Global citation recall of final reports: AI-Q 58.7%, MS-Agent 28.5%, TrajectoryKit 7.1%. — https://arxiv.org/html/2608.24306v1, opened 2026-10-16, WebFetch
- MARCH (ACL 2026, 9 Jun 2026) states LLM-judge verifiers suffer "confirmation bias, where the verifier inadvertently reproduces the errors of the original generation"; its Checker answers questions from retrieved documents without seeing the original response. (From search excerpt of https://aclanthology.org/2026.acl-long.1828.pdf; page not opened, so this is not a cited finding; see Gaps.)

### Contradictions
- A multi-agent cascade study (arXiv 2606.07937) excerpt reports hallucination attenuating across a 3-agent chain (0.422 to 0.272), against the above where later stages introduce errors. Only the search excerpt was seen, page not opened; not cited. Settling it would need opening that paper.

### Inferences
- (mine) Claim drift at merge: plugin/agents/synthesizer.md should copy claims from notes verbatim or near-verbatim, carry the URL and quote with each claim, and mark any sentence that merges two notes' claims as "synthesis" needing both citations. Rests on orchestrator-error origin data.
- (mine) Citation laundering (a note cites a secondary page that cites the primary; the synthesizer cites the note as if primary): plugin/skills/research/note-schema.md should require a `Source type: primary|aggregator` tag per finding (already partly in the researcher rules) and the verifier should check that the cited URL itself states the claim, not a page linking to it.
- (mine) Pass the verifier the claim, URL and quote only, not the synthesizer's surrounding prose, and run it in fresh context to limit confirmation bias (MARCH idea, unverified). Edit plugin/agents/verifier.md.
- (mine) Do not add more retrieval to fix citation problems: depth increased unsupported rates in the ablation. Cap researcher tool calls in plugin/agents/researcher.md (existing 10 to 15 limit is consistent with this).

### Gaps
- MARCH page https://aclanthology.org/2026.acl-long.1828.pdf and hallucination cascade paper https://arxiv.org/pdf/2606.07937 were seen only as search excerpts, not opened; nothing from them is relied on.
- No source found that measures "citation laundering" by name.

## Tools evaluated
None.
