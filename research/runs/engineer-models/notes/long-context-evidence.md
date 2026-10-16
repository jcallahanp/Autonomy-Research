# Large-context and second-opinion models: where they help, long-context reliability

Brief: Decide, from evidence, which engineering jobs a very large context window or a second model actually improves, and how reliable models are near 1M tokens.
Run: research/runs/engineer-models/PLAN.md

Dates: all pages opened 2026-10-16. Connectors: Parallel Search rate-limited (429) on first call, so Exa search/fetch and WebFetch were used.

## Long-context benchmarks at 128k/512k/1M

### Takeaway
Retrieval of identical lookalike items degrades sharply by 1M for most families; only Claude Opus 4.6 held about 76% on MRCR v2 8-needle at 1M (vendor-run, partly beyond the public API window), GPT-5.4 about 37% at 512K-1M, Gemini 3 Pro about 25%. Reasoning-style tasks (GraphWalks BFS, LongBench v2, code) are weaker than retrieval and the ranking differs by task. Stay well under 1M for anything that must be right. Confidence: medium (vendor and aggregator numbers, different harnesses, none for Opus 5.5 / GPT-6 / Gemini 4).

### Cited findings
- Chroma Context Rot (18 LLMs incl. GPT-4.1, Claude 4, Gemini 2.5, Qwen3): performance is not uniform across input length even on simple tasks; distractors hurt — https://www.trychroma.com/research/context-rot, opened 2026-10-16, WebFetch — Quote: "Through our experiments, we demonstrate that LLMs do not maintain consistent performance across input lengths."
- Chroma: a single distractor already lowers accuracy — https://www.trychroma.com/research/context-rot, opened 2026-10-16, WebFetch — Quote: "Even a single distractor reduces performance relative to the baseline"
- Chroma: Claude abstains, GPT hallucinates confidently (fetch-model paraphrase of the report, 2025 models) — https://www.trychroma.com/research/context-rot, opened 2026-10-16, WebFetch — Quote: "Claude models consistently exhibit the lowest hallucination rates."
- MRCR v2 8-needle: Opus 4.6 93.0% at 256K, 76.0% at 1M, max effort, Anthropic harness (2026-02-17 system card via Klu) — https://klu.ai/benchmarks/mrcr-v2, opened 2026-10-16, WebFetch — Quote: "93.0% at 256K; 76.0% at 1M"
- Same page: Gemini 3 Pro 24.5% at 1M on the contextarena.ai harness (not like-for-like with Anthropic's) — https://klu.ai/benchmarks/mrcr-v2, opened 2026-10-16, WebFetch — Quote: "45.4% at 256K; 24.5% at 1M"
- Aggregator (2026-03-15): GPT-5.4 falls to 36.6% at 512K-1M (OpenAI figure), Opus 4.6 the only model above 70% at 1M — https://yage.ai/share/long-context-benchmark-en-20260315.html, opened 2026-10-16, WebFetch — Quote: "512K-1M falls further to 36.6%."
- Same page — Quote: "If you need reliable 256K-1M context usage, Claude Opus 4.6 is currently the only model maintaining 70%+ performance."
- ATLAS (26 models, 8K-1M, 8 capability dimensions incl. MRCR-8, GraphWalks, LongCodeBench): ranking flips by length — https://ar5iv.labs.arxiv.org/html/2605.28079, opened 2026-10-16, WebFetch — Quote: "Gemini-3.1-Pro-Preview leads at 128K, Claude-Opus-4.6 leads at 1M, and GPT-5.5 remains third in both scopes."
- ATLAS: mean loss 128K to 1M is 24.3% — same URL/tool — Quote: "The mean relative decay across all 26 models is 24.3%, but the spread is large."
- ATLAS: degradation is task-specific; retrieval falls while in-context learning holds — same URL/tool — Quote: "Gemini-3.1-Pro-Preview retains high ICL performance (98.32), but its Retrieval score falls 41.5% from 84.96 to 49.67."
- LongBench v2 (503 MCQ, 8k-2M words, majority under 128k; human experts 53.7%): best direct-answer model 50.1%, reasoning o1-preview 57.7%; leaderboard has Gemini-2.5-Pro 63.3 (last updated 2025-05-06) — https://longbench2.github.io/, opened via Exa search page text only (see Gaps) — not cited as a finding.
- Anthropic Fellows (via prior note engineer-context.md:222): Opus 4.6 recall 99.7% at 100K vs 69% at 800K for an inserted attack — /home/user/Autonomy-Research/research/findings/engineer-context.md:222, read 2026-10-16, Read — Quote: "Opus 4.6 (with thinking)'s recall drops from 99.7% when such an attack is inserted in a 100K transcript to 69% when the same attack is inserted in an 800K transcript."
- Agent SWE results under long input: successful agent runs stay short — https://arxiv.org/html/2602.16069, opened 2026-10-16, WebFetch — Quote: "successful agentic trajectories typically remain under 20k-30k tokens"

### Contradictions
- Opus 4.6 76% at 1M (Anthropic internal harness, includes problems beyond the public 1M API limit) vs Gemini/GPT numbers from contextarena.ai / vendor reports — different harnesses; Klu itself says "Don't rank across harnesses" (https://klu.ai/benchmarks/mrcr-v2). ATLAS (independent 26-model suite) nonetheless also puts Opus 4.6 first at 1M, which supports direction. An independent same-harness rerun on current models would settle it.
- yage.ai lists Gemini 3 Pro 24.5% in one place and 26.3% in a timeline table (https://yage.ai/share/long-context-benchmark-en-20260315.html); the page is internally inconsistent.

### Inferences
- Retrieval-of-lookalikes (MRCR) is the best case for 1M; real reasoning (GraphWalks BFS: Opus 4.6 38.7% at 1M per Klu, quoted from the system card) is worse. Treat 1M as "readable", not "reliable for multi-step reasoning". Rests on Klu + ATLAS findings.
- Use ~128K-256K as the working ceiling for correctness-critical work; use more only for lookup-style questions where a miss is cheap. Rests on MRCR 93% at 256K vs 76% at 1M and the Fellows 800K drop.

### Gaps
- No source found with MRCR/ATLAS scores for Opus 5.5, Sonnet 5.5, GPT-6 or Gemini 4 (Klu states no primary document gives them). Claude Code's own 1M behaviour not measured.
- NoLiMa, RULER, HELMET, Fiction.LiveBench, LongCodeBench per-model 512K/1M scores not obtained: fiction.live page returned only navigation; ATLAS text read did not include LongCodeBench scores (WebFetch note: last 9,673 chars unread). Older RULER/NoLiMa results are in engineer-context.md:209-210 (prior run).
- longbench2.github.io and arXiv 2505.08120 (LCLM vs agent scaffolds on SWE-bench) were seen only as Exa search text (PDF fetch returned binary); figures not cited.

## Whole-repo in context vs retrieval/subagents

### Takeaway
No evidence found that dumping a whole repo into context beats agentic search for coding agents; the strongest controlled evidence says the opposite: successful runs are short, long single-shot inputs fail, and compressed relevant context matches whole files at about 1/4 of the tokens. Big windows help mainly as an "if it fits, read it" convenience for comprehension and for a localisation pass, not for edits. Confidence: medium (small models and older harnesses in some studies; none test Claude Code with 1M).

### Cited findings
- 64k single-shot with perfect retrieval recall still fails for the small models tested — https://arxiv.org/html/2602.16069, opened 2026-10-16, WebFetch — Quote: "Qwen3-Coder-30B-A3B achieves only a 7% resolve rate at 64k context, while GPT-5-nano solves none of the tasks."
- Same paper: agentic success comes from short steps — Quote: "successful agentic trajectories typically remain under 20k-30k tokens" (same URL/tool).
- Oracle-localised SWE-bench Verified, single-shot: compressed context equals whole files at about a third of tokens — https://arxiv.org/html/2607.09691, opened 2026-10-16, WebFetch — Quote: "On cost-normalized terms the gap is clear: 19,300 context tokens per resolve vs. 93,700"
- Scope limits of that study — same URL/tool — Quote: "All arms are oracle ceilings, not deployable policies"; "Single language (Python), single model family."
- Coding agents with file-system tools handle long documents as well as full-context GPT-5; retrieval tools did not consistently help — https://arxiv.org/html/2603.20432, opened 2026-10-16, WebFetch — Quote: "equipping coding agents with retrieval tools does not consistently improve performance and can even degrade it."
- On LongBench-v2 the agent just reads (agent 61.50 vs GPT-5 full context 61.00) — same URL/tool — Quote: "the agent's performance is nearly identical to the baseline performance of the LLM provided with the full context."
- Same paper abstract — Quote: "these agents outperform published state-of-the-art by 17.3% on average."
- Prior repo evidence: lead should hold little; degradation shape for 200K-1M unknown — /home/user/Autonomy-Research/research/findings/engineer-context.md:236, read 2026-10-16, Read — Quote: "the degradation shape for current models in the 200K-1M range is unknown"

### Contradictions
- arXiv 2505.08120 (search text only, not cited) reports a long-context model with whole repo outperforming Agentless scaffolds in matched comparisons on SWE-bench Verified, while 2602.16069 finds long single-shot patching collapses. Different models (Gemini 1.5/2.5 Pro vs small open models) and years; not settled. A same-model test on a real repo would settle it.

### Inferences
- For Claude Code the architecture "Explore subagent returns file:line, main session reads only those files" is supported over "load everything"; the only role for a huge window is one-shot comprehension ("how does this subsystem fit together") where a miss is visible and cheap. Rests on 2602.16069, 2607.09691, 2603.20432.
- Subagents win on rot, not necessarily accuracy: nothing opened measures Claude Code subagent exploration vs 1M whole-repo directly (Gap).

### Gaps
- No Claude-Code-specific or Opus/Sonnet 5.x whole-repo vs subagent experiment found. SWE-Explore / ContextBench / LongCodeBench (registry/others) not re-opened here.
- Log triage: security-incident RAG paper (https://arxiv.org/html/2603.18196v3) — Quote: "Context window constraints limit no-RAG approaches to 0.6–4.3% of available logs (22–158 out of 3,694)." Caveat: small windows (Claude Sonnet 4 era); says RAG pre-filtering essential, but does not test 1M. Traversal's RCA benchmark (https://www.traversal.com/blog/..., Exa search text only) says more reasoning did not raise accuracy; not cited. No direct 1M-window log-triage study found.

## Second-opinion and cross-model review

### Takeaway
Evidence is mixed and leans against "different family" as the cause of gains: a preregistered replay (Oct 2026) finds a fresh same-model session matches or beats a second family, while Greptile (vendor, Jul 2026) and a JHU LiveCodeBench study find cross-model effects that are asymmetric and depend on which model is stronger. What does repeatedly help: a second independent look, placed after a whole feature is done, with evidence (tests) attached, and acting on findings. A weak/lightweight cross-model reviewer does not help. Confidence: medium.

### Cited findings
- Preregistered replay, 183 reviews, Claude Opus 5.5 vs Codex (GPT-6.1 Sol): cross-family fails at 3 of 4 checkpoints — https://stephens.page/blog/fresh-eyes-beat-a-second-family/paper/fresh-eyes-beat-a-second-family.pdf, opened 2026-10-16, Exa fetch — Quote: "We conclude that the gain usually attributed to model diversity is mostly the gain of an independent second look, which a fresh same-model session provides"
- Same paper: second look after feature-level review found real bugs in more than half of 30 features from either family, largely disjoint findings — same URL/tool — Quote: "a second look found real missed bugs in more than half of 30 features from either family (Codex 16, fresh Claude 19, bar 6), with largely disjoint find ings."
- Same paper: finding is not acting — Quote: "the authoring agent declined both" (2 of 6 escaped bugs had been raised by in-session reviews). Single-system, single-author, unreviewed.
- Greptile (vendor, P0/P1 recall on ~500 PRs per author model, ground truth from sentiment/upvote/git archaeology): cross-model higher — https://www.greptile.com/blog/model-inversion, opened 2026-07-21 post, 2026-10-16, Exa fetch — Quote: "The data shows that both models find more bugs in code written by the other model than in code they wrote themselves."
- Same page figures: Opus 4.7 on Claude-authored PRs 53.7% vs 60.0% on Codex-authored; GPT 5.5 62.0% cross vs 50.5% same (page figure labels 60.0%/62.0%/53.7%/50.5%; same-model/cross-model legend).
- JHU/CSU LiveCodeBench (116 tasks, no test execution): asymmetric — https://arxiv.org/html/2607.21656v1, opened 2026-10-16, Exa fetch — Quote: "Claude Opus 4.7 review raises Codex GPT-5.5 drafts from 71.6% to 89.7%"; "Codex GPT-5.5 reviewing Claude Opus 4.7 drafts drops the pass rate from 91.4% to 82.8%"
- Same paper: authors note that design cannot separate direction from the baseline gap (reviewer stronger than drafter helps) — Quote (from search/fetch text, same URL): "this design cannot fully separate the effect of review direction from the effect of that baseline gap"
- Planted-errors study (30 artifacts, 150 errors, 900 sessions): lightweight cross-model reviewer no better; code favours same-model fresh review, documents favour cross-model — https://arxiv.org/html/2610.01471v1, opened 2026-10-16, WebFetch — Quote: "A lightweight cross-model reviewer scores no higher than same-model review."
- Same paper — Quote: "one CCR plus one XMR review covers more ground-truth errors than two CCR reviews (56.7% vs. 42.7%)"; "For code artifacts, CCR outperforms all XMR conditions" (CCR = fresh-context same-model review).
- Multi-family panel on a live team's corpus (294 confirmed issues, 15 model versions): single model ~half of defects; second reviewer is the big step — https://doi.org/10.5281/zenodo.20519584, opened 2026-10-16, Exa fetch — Quote: "coverage of an artifact's confirmed defects rises from about 47% with one reviewer to about 72% with a second (the largest single step)"
- Same page — Quote: "different providers are a sensible default this corpus cannot prove beats re-runs"
- Aider architect/editor (2025-01): R1 architect + Sonnet editor 64.0% at 14X less cost than o1; o1+Sonnet no better than o1 alone — https://aider.chat/2025/01/24/r1-sonnet.html, opened 2026-10-16, WebFetch — Quote: "o1 paired with Sonnet didn’t produce better results than just using o1 alone."

### Contradictions
- Greptile (cross-model +9 points) and the Zenodo panel favour a second family; Stephens replay (https://stephens.page/...pdf) and 2610.01471 find fresh same-model review equal or better on code. Differences: Greptile uses vendor-built ground truth and different tasks; Stephens catches specific escaped timing bugs in one pipeline. A third-family test with same-model fresh control on a shared corpus would settle it.
- JHU study (Claude reviewing Codex good; Codex reviewing Claude harmful) vs Greptile (both directions help): reviewer-without-execution vs full agent reviewers; ordering by baseline strength explains the JHU asymmetry per its authors.

### Inferences
- Default for John: fresh-context same-model (Claude) reviewer subagent with test output attached, placed after the whole feature/PR, with a rule that every finding becomes a test or a recorded decline. Add a cross-family reviewer only if cost is trivial, and only a top-tier model (never a lightweight one). Rests on Stephens, 2610.01471, JHU.
- A cross-family reviewer is more promising when the author model is the weaker of the pair, and for documents/plans/consistency than for code. Rests on JHU and 2610.01471 document result.
- Wave 1's "lightweight cross-model reviewer no better" is confirmed; the stronger finding is that the "fresh session" control, not family, explains most of the gain.

### Gaps
- No study of Gemini as reviewer for Claude Code output; no Opus 5.5 vs GPT-6 data beyond Stephens (single pipeline). LLM-as-judge self-preference (Zheng, Panickssery) cited only as secondary text inside Stephens' intro, not opened.
- Aider architect/editor for 2026 models: not found; 2024-09 post (aider.chat/2024/09/26/architect.html) seen in search text only.
- Zenodo and Stephens papers are self-published, not peer reviewed; Greptile is a vendor of review products.

## Net verdict per job

### Takeaway
Whole repo: no (use Explore subagents + targeted reads; big window only for one-shot comprehension). Logs: no for raw 1M dumps; pre-filter then read. Long documents (API docs, contracts): yes within about 128K-256K, beyond that chunk or let the agent grep. Review: fresh same-model subagent first, optional top-tier cross-family second look after the feature. Vision/UI screenshots: usable as a triage aid, not a gate. Confidence: medium (verdicts are inferences from cited findings).

### Cited findings
- Screenshot UI review: best VLMs catch about 40% of human-tagged defects and rarely abstain — https://blog.scrymore.com/blog/introducing-scry-design-diff-eval/, opened 2026-10-16, WebFetch — Quote: "The best models catch roughly two fifths of known issues."
- Same page — Quote: "Abstention is basically absent."; "nowhere near a drop-in replacement for a human reviewer".
- Vendor-run benchmark of 311 mobile UI pairs, Claude Fable 5 40.4% recall, Gemini 3.5 Flash 37.5%, Codex GPT-5.5 37.3% (page table; Fable run via Claude Code subagents) — same URL/tool.
- Log analysis: raw logs overflow even 158-log windows; RAG/pre-filter essential — https://arxiv.org/html/2603.18196v3, opened 2026-10-16, WebFetch — Quote: "Context window constraints limit no-RAG approaches to 0.6–4.3% of available logs (22–158 out of 3,694)."
- Long documents: agent reading equals full-context on LongBench-v2 (see Q2) — https://arxiv.org/html/2603.20432.

### Contradictions
- None found beyond those above. Vision: Repeato (Aug 2026, Exa search text only) shows Claude Sonnet 5 / Opus 5 poor at box grounding (21% / 46% hits) vs GPT-5.6 Luna 100% — not opened; would matter for click-by-coordinate, not for defect review (see Gaps).

### Inferences
| Job | Verdict | Basis |
| --- | --- | --- |
| Whole repo in context | Not worth it; Explore subagents/targeted reads | 2602.16069, 2607.09691, 2603.20432 |
| Log triage | Pre-filter (grep/aggregate) then read; 1M dump only for exploratory one-offs | 2603.18196, MRCR drop to 1M |
| Long docs/contracts/API docs | Large window helpful up to ~256K; verify extracted claims against source | MRCR 93% at 256K; Chroma distractors |
| Review | Fresh same-model reviewer with tests; optional top-tier second family after feature | Stephens, 2610.01471, JHU |
| UI screenshots | Triage aid; deterministic Playwright assertions as the gate | Scry (40% recall, no abstention) |
- Recommendation: keep Claude Code as the sole engine at default window; spend effort on retrieval discipline and fresh-context reviewers, not on a 1M-token or second-vendor tier.
- Alternatives: (a) add a second-family reviewer (Codex/Gemini CLI) after features, only top tier; (b) use 1M window ad hoc for subsystem comprehension; (c) Aider-style architect/editor split: skip, gain faded by 2025.
- Rejected: routing whole repos into 1M context; lightweight cross-model reviewer; ensemble "council" as default (no cost-justified evidence found beyond coverage of 2 reviewers).
- Spike before building: (1) 20 real John tasks: Explore-subagent vs 1M whole-repo for a "how does X work" question, score correctness and token cost; (2) seeded-bug review: fresh Claude vs Claude+Codex/Gemini on 20-30 own PRs, with fresh same-model control; (3) 3 recorded UI regressions: screenshot-review recall vs Playwright assertion.

### Gaps
- No direct "council/ensemble" evidence opened beyond Zenodo panel and 2610.01471. No contract-specific long-document benchmark opened. Repeato vision benchmark, CUJBench (https://arxiv.org/html/2604.23455, browser-only agents beat full-toolset, seen in search text only) not cited.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Chroma Context Rot report | https://www.trychroma.com/research/context-rot | 18-model long-input degradation study (2025) | web | 2026-10-16 | Evidence; models are 2025 vintage |
| OpenAI MRCR v2 (via Klu summary) | https://klu.ai/benchmarks/mrcr-v2 | 8-needle long-context retrieval tracker, up to 1M | dataset/web | 2026-10-16 | Evidence; do not rank across harnesses |
| ATLAS long-context benchmark | https://ar5iv.labs.arxiv.org/html/2605.28079 | 26 models, 8K-1M, 8 capability dimensions | paper, not run | 2026-10-16 | Evidence; best independent length-sliced view |
| Greptile Model Inversion | https://www.greptile.com/blog/model-inversion | Routes PR review to other vendor's model | vendor SaaS (not used) | 2026-10-16 | Reference only; vendor-measured |
| Scry Design Diff Eval / Leaderboard | https://blog.scrymore.com/blog/introducing-scry-design-diff-eval/ | 311-pair screenshot-vs-design defect benchmark | web | 2026-10-16 | Evidence; vendor-run |
| Aider architect/editor mode | https://aider.chat/2025/01/24/r1-sonnet.html | Reasoner proposes, second model edits | Aider CLI (not installed) | 2026-10-16 | Reference only; gain faded for stronger models |
