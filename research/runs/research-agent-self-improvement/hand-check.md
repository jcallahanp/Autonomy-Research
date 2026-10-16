# Hand check: research-agent-self-improvement.md (20 citations)

Independent citation audit, 2026-10-16. Input: `research/findings/research-agent-self-improvement.md`
(287 lines at audit time). Any `## Verification` section in that file was ignored. Every source below
was opened in this session. Web pages went through Parallel `web_fetch`, with WebFetch for exact
quotes and `curl` for one raw README. Repo files were read with `sed`/`grep`. The skill-creator
citations were read from the session's own clone at `/tmp/tmp.lGRKOZligk/skills` (HEAD dbd4588,
2026-10-09, the commit the findings name).

## 1. Claim-citation pairs

I counted 109 claim-citation pairs. `[N]` marks a claim with a number, a percentage or a direct quote.

**Q1 (internal audit)**
1 [N] 0.97 vs 0.8, delta 0.76 vs 0.3, 7/8 at 1.0, one run per case per arm (self-test:7-8) ·
2 [N] no-beacon grader fixed, "has not been re-run" (:23-29) ·
3 [N] stated limits, "measures the workflow…" (:31-38) ·
4 [N] baseline 1.0 on one-fact-inline and passes some graders (aggregate-result.json) ·
5 reply-says-gap regex (reply-says-gap.md:5-7) ·
6 cites-url `https?://\S+` (cites-url.md:3-5) ·
7 with-only `scored: false` (content-calls.md:5-9) ·
8 no spike/tool-scan/gap/compaction case (self-test/SKILL.md:127-138) ·
9 single-facet prompts (prompt.md:10 ×2) ·
10 fallback chain (researcher.md:64-65) ·
11 verifier has no Bash/Firecrawl/Playwright (verifier.md:6) ·
12 [N] "page did not open" (verifier.md:23-24) ·
13 [N] "up to 20" plus mandatory classes (verifier.md:17-18) ·
14 verifier on haiku (verifier.md:4) ·
15 [N] "Cite the file path in the clone…" (researcher.md:67-68) ·
16 [N] "with no URL" excluded (synthesizer.md:24-26) ·
17 URL on every Cited line (note-schema.md:10-11) ·
18 lead writes registry rows (tool-scan:18-20, repo-triage:24-26) ·
19 synthesizer writes rows in normal mode (synthesizer.md:65-66) ·
20 [N] "nobody else writes those rows" (spike:67-68) ·
21 repo-triage lead writes row (repo-triage:46-47) ·
22 [N] 3 candidates × 5+ steps (tool-scan:34-47) ·
23 [N] "about 10 to 15 tool calls" (researcher.md:47-48) ·
24 [N] 25,000-character rule "in a subagent" (research/SKILL.md:208-209) ·
25 disallowedTools Agent (researcher.md:9) ·
26 routing "in a subagent" (routing.md:12,16-17) ·
27 [N] "No plugin agent has this tool" (system-map:50-51) ·
28 connector probe unspecified (research/SKILL.md:77-80,120) ·
29 [N] `head -n 30` (session-start.sh:14) ·
30 [N] INDEX up to 200 lines, 9-line header (INDEX.md:1-9) ·
31 [N] 8-worker cap includes gap round (research/SKILL.md:17,38) ·
32 spike triage not counted (spike:55) ·
33 [N] five INDEX lines unverified (INDEX.md:11-15) ·
34 [N] 533 and 543 lines (wc -l) ·
35 routing evidence is unverified file (routing.md:5) ·
36 [N] routing.md:13 full-content fallback ·
37 [N] researcher.md:46 never `full_content` ·
38 "Gaps" wording (synthesizer.md:79-80, research/SKILL.md:210-211) ·
39 no Gaps section (findings-format.md:18)

**Q2 (citation faithfulness)**
40 [N] DeepTRACE 303 queries, 9 systems, 12.5–97.5%, "40-80%" (2509.04499) ·
41 [N] judge r=0.62 (2509.04499) ·
42 [N] CbNV 130 queries, 14 models, 23.2/31.1/41.3/45.8/75.6% (2605.06635v1) ·
43 [N] dead links 0–6%, "mask factual failures" (2605.06635v1) ·
44 [N] GPT-5.4 21.4→83.3, Opus 4.6 20.0→42.1 (2605.06635v1) ·
45 [N] orchestrator 84.7/52.6/100%, mostly citation-related (2608.24306v1) ·
46 [N] stage error rates 46–71% vs 0.9–6.4% (2608.24306v1) ·
47 [N] AI-Q 50 examples, recall 64.5→69.7, precision 87.6→94.1, RACE 52.6→52.4 (2608.24306v1) ·
48 [N] citation-only instruction 69.6/91.0 (2608.24306v1) ·
49 [N] judge 76%, kappa 0.62, 20 examples (2608.24306v1) ·
50 [N] L-MARS F1 0.131→0.254, 34→13%, 36–54% (2509.00761v4) ·
51 quote-first and retract guidance (reduce-hallucinations) ·
52 [N] Citations API "valid pointers…" (citations) ·
53 [N] kappa 0.458/0.219/0.683 (2509.00761v4) ·
54 [N] 15 of 20 URLs disputed (2509.00761v4) ·
55 ensemble or hybrid checks (2605.06635v1) ·
56 [N] Gemini DR 50.3 vs 40.3 (2509.04499)

**Q3 (context rot)**
57 [N] NoLiMa 11/13 under 50% at 32K; Claude 3.5 Sonnet 87.5→29.8, 4K vs 200K (2502.05167v3) ·
58 [N] 13.9–85%, recite +4% (EMNLP 1264) ·
59 [N] up to 94 pp mid-context (2605.23170) ·
60 [N] Sonnet 4.5 context anxiety, Opus 4.5 removed it (harness-design) ·
61 [N] context-aware models may wrap up early (prompting best practices) ·
62 fresh window over compaction (prompting best practices) ·
63 [N] Context Rationale Erosion / Communication Failure (2607.28802v1) ·
64 hooks.json SessionStart only, matcher (hooks.json) ·
65 [N] sonnet/medium, maxTurns 40, no memory (agents/*.md) ·
66 [N] subagent auto-compact, maxTurns resume via SendMessage, 200 lines/25KB (sub-agents) ·
67 [N] 3 of 4 within 6 pp, 16–56 pp (2605.23170) ·
68 [N] "isn't loaded into subagents" (context-management.md) ·
108 CLAUDE.md has Compact instructions (CLAUDE.md) ·
109 sub-agents page silent on SessionStart in subagents (sub-agents)

**Q4 (change mechanisms)**
69 MIPROv2 Bayesian search (dspy MIPROv2) ·
70 [N] GEPA Pareto, minibatch 3, "if improved" (GEPA overview) ·
71 [N] GEPA +6% vs GRPO, 35×, >10% vs MIPROv2 (2507.19457) ·
72 [N] GEPA blog 200/50/60 (gepa blog) ·
73 [N] TextGrad "textual gradients" (textgrad) ·
74 [N] promptfoo "using observed failures…", "can overfit…" (promptfoo) ·
75 GEPA asserts reflection LM; TextGrad needs a key (GEPA, textgrad) ·
76 [N] "uses the session's Claude Code auth…" (improve_description.py) ·
77 content loop and benchmark.json (SKILL.md) ·
78 baseline without_skill or previous iteration (SKILL.md:313) ·
79 [N] stop rule (SKILL.md:316-322) ·
80 [N] 60/40, 3 runs, 5 iterations, "rather than train score…" (run_loop.py:79-234) ·
81 [N] PREVIOUS ATTEMPTS, no query lists, 1024 cap (improve_description.py:103-170) ·
82 [N] "fiddly overfitty", lean, "a yellow flag" (SKILL.md:298-306) ·
83 [N] blind A/B "optional…" (comparator.md, SKILL.md:325-330) ·
84 [N] agentskills.io loop, stddev quote (agentskills.io)

**Q5 (evaluation)**
85 [N] 0.702→0.781, CI, 3-seed 0.107 (2610.12601) ·
86 [N] gap "small-sample selection…", scalar negative, "Credible evaluation…" (2610.12601) ·
87 [N] DGM "was optimized without ever accessing" (2505.22954v3) ·
88 [N] DGM "objective hacking" (2505.22954v3) ·
89 [N] graders "resistant to bypasses or hacks" (demystifying evals) ·
90 [N] SWE-bench 2.2–6.0 pts, SD>1.5, 2–3 pts noise (2602.07150) ·
91 [N] plugin eval 3 runs and guidance quotes (plugin-evals) ·
92 [N] v0.1 one run per case (self-test:7-8) ·
93 [N] "20-50 simple tasks…" (demystifying) ·
94 [N] pass^3 ≈ 42% at 75% (demystifying) ·
95 [N] "Eval saturation…" (demystifying) ·
96 [N] "closely calibrated…" (demystifying) ·
97 [N] groundedness "verify that claims…" (demystifying) ·
98 [N] regression "nearly 100%" (demystifying) ·
99 [N] DRB RACE/FACT, judge switch 11 May 2026, keys, 100 reports (deep_research_bench) ·
100 [N] DRB II 132 tasks, ~9,430 rubrics, 1/0/-1, GPT-5.5, public jsonl (DRB-II) ·
101 [N] BrowseComp 1,266 short answers (2504.12516) ·
102 [N] self-test "never edits the plugin…" (self-test/SKILL.md:1-15) ·
103 [N] DGM staged 10 then 50 tasks (2505.22954v3) ·
104 [N] DGM fixed 80 iterations (2505.22954v3) ·
105 [N] agentskills.io stop quote (agentskills.io) ·
106 DRB license Apache-2.0 sidebar vs MIT badge (deep_research_bench) ·
107 [N] 19 commits in one day (git log)

Restatements in the summary, the Implications table and the Evidence list were folded into the pair
they repeat.

## 2. Picks

- **Number, percentage or quote (12), spread across sections:** 1, 23, 30 (Q1); 42, 45, 47 (Q2);
  57, 61, 66 (Q3); 80 (Q4); 85, 90 (Q5). I chose them because they carry the headline numbers (the
  0.97 score, the unsupported-citation rates, the merge-stage error share, the precision gain, NoLiMa,
  the held-out gain, eval noise) and the repo facts the ranking rests on.
- **Random (8)** from the other 97 indices:
  `python3 -c "import random; random.seed(20261016); picked={1,23,30,42,45,47,57,61,66,80,85,90}; rest=[i for i in range(1,110) if i not in picked]; print(sorted(random.sample(rest,8)))"`
  printed `[19, 60, 75, 81, 82, 97, 100, 106]`.

## 3. Results

| # | Claim (short) | Citation | Verdict | Quote from source (≤30 words) | Note |
| --- | --- | --- | --- | --- | --- |
| 1 | Self-test 0.97 vs 0.8, delta 0.76 vs 0.3, 7 of 8 at 1.0, one run per case per arm | docs/self-test/2026-10-16-v0.1.md:7-8 | PARTIAL | "Suite score 0.97 against a bar of 0.8; mean delta over the baseline 0.76 against a bar of 0.3. 7 of 8 cases passed every grader." | The numbers match. "One run per case per arm" is at line 4, not 7-8, so the line range is wrong for that part. |
| 19 | The synthesizer writes registry rows in normal mode | plugin/agents/synthesizer.md:65-66 | SUPPORTED | "Then add each new or changed row from `## Tools evaluated` to `research/tool-registry.md`, in the section that fits." | Exact lines. |
| 23 | The researcher stops at "about 10 to 15 tool calls" | plugin/agents/researcher.md:47-48 | SUPPORTED | "Stop at about 10 to 15 tool calls, or when the key questions are answered, or when new calls find nothing new." | Line 47. |
| 30 | INDEX.md allows up to 200 lines with a 9-line header | research/findings/INDEX.md:1-9 | SUPPORTED | "Keep it under 200 lines." | Lines 1-9 are the header and line 11 is the first entry. |
| 42 | CbNV: 130 queries, 14 models; unsupported 23.2% Opus 4.5, 31.1% Haiku 4.5, 41.3% Sonnet 4.6, 45.8% Opus 4.6, 75.6% OSS-120B | https://arxiv.org/html/2605.06635v1 | SUPPORTED | "Fact Check scores range from 24% (OSS-120B) to 77% (Claude Opus 4.5)"; table: Opus 4.5 76.8%, Haiku 4.5 68.9%, Sonnet 4.6 58.7%, Opus 4.6 54.2%, OSS-120B 24.4%. | Each rate is 100 minus the Fact Check column, and the arithmetic is exact. The paper reports accuracy, not "unsupported" rates. 130 queries is confirmed. |
| 45 | Orchestrator caused 84.7% / 52.6% / 100% of final-report errors in AI-Q / MS-Agent / TrajectoryKit, "mostly citation-related" | https://arxiv.org/html/2608.24306v1 | PARTIAL | "For AI-Q, 84.7% of final-report errors were attributed to the orchestrator, for MS-Agent 52.6%, and for TrajectoryKit 100%." | The numbers match. The page also says "TrajectoryKit is the exception: only 4% of its orchestrator errors are citation-related" and that 95% are hallucinations. The findings apply "mostly citation-related" to all three, which is stronger than the source. |
| 47 | AI-Q, 50 examples: raw snippets raise recall 64.5→69.7 and precision 87.6→94.1; RACE 52.6→52.4 | https://arxiv.org/html/2608.24306v1 | SUPPORTED | "AI-Q 52.6 ±0.4 64.5 ±3.9 87.6 ±3.0 + replace w/ snippets 52.4 ±0.7 69.7 ±4.1 94.1 ±2.0" | 50 examples confirmed ("We evaluate on 50 examples from DeepResearch Bench"). |
| 57 | NoLiMa: 11 of 13 models under 50% at 32K; Claude 3.5 Sonnet 87.5→29.8, effective 4K vs claimed 200K | https://arxiv.org/html/2502.05167v3 | SUPPORTED | "at 32K tokens, 11 out of 13 models achieve only half of their short-context performance." Table row: "Claude 3.5 Sonnet \| 200K \| 4K \| 87.5 (74.4) … 29.8" | |
| 60 | Sonnet 4.5 context anxiety; "compaction alone wasn't sufficient"; Opus 4.5 "largely removed that behavior"; 24 Mar 2026 | https://www.anthropic.com/engineering/harness-design-long-running-apps | SUPPORTED | "we found Claude Sonnet 4.5 exhibited context anxiety strongly enough that compaction alone wasn't sufficient to enable strong long task performance" | "Opus 4.5 largely removed that behavior on its own" and "Published Mar 24, 2026" are also on the page. |
| 61 | Sonnet 5, Sonnet 4.6 and Haiku 4.5 track their remaining window and "may sometimes naturally try to wrap up work…" unless told about compaction | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices | SUPPORTED | "Otherwise, Claude may sometimes naturally try to wrap up work as it approaches the context limit." | The page also lists Sonnet 4.5 (deprecated). Leaving it out is harmless. |
| 66 | Subagents auto-compact; a subagent stopped at maxTurns returns partial output, resumable via SendMessage; `memory:` loads the first 200 lines or 25KB | https://code.claude.com/docs/en/sub-agents | SUPPORTED | "The subagent's system prompt also includes the first 200 lines or 25KB of `MEMORY.md` in the memory directory, whichever comes first" | Also on the page: "Subagents support automatic compaction" and "Claude uses the `SendMessage` tool … to resume it". |
| 75 | GEPA asserts that a reflection LM or a custom proposer is given; TextGrad needs an OpenAI or Anthropic key | https://dspy.ai/api/optimizers/GEPA/overview/index.md; https://github.com/zou-group/textgrad | SUPPORTED | "assert reflection_lm is not None or instruction_proposer is not None" / "you need an OpenAI/Anthropic key to run the LLMs" | |
| 80 | Description optimiser: 60/40 split, 3 runs per query, `--max-iterations 5`, `best_description` by test score "rather than train score to avoid overfitting" | scripts/run_loop.py:79-234 (skill-creator clone) | PARTIAL | SKILL.md:394: "returns JSON with `best_description` — selected by test score rather than train score to avoid overfitting." | The facts are true but the location is wrong. The quote, 60/40 and "3 times" are in SKILL.md:394. The defaults (`--holdout 0.4`, `--runs-per-query 3`, `--max-iterations 5`) are at run_loop.py:251-254, outside 79-234. Lines 79-234 hold only the loop and the best-by-TEST selection (line 216). |
| 81 | Proposer sees "PREVIOUS ATTEMPTS (do NOT repeat these…)", may not grow a list of failing queries, 1024-character cap | scripts/improve_description.py:103-170 | SUPPORTED | "PREVIOUS ATTEMPTS (do NOT repeat these — try something structurally different)" … "There is a hard limit of 1024 characters" | The no-query-list rule is at about line 126. |
| 82 | Edit guidance: avoid "fiddly overfitty changes", keep lean, ALWAYS/NEVER is "a yellow flag" | skill-creator SKILL.md:298-306 | SUPPORTED | "If you find yourself writing ALWAYS or NEVER in all caps, or using super rigid structures, that's a yellow flag" | Lines 298, 300 and 302. |
| 85 | Held-out citation reward 0.702→0.781 (+0.079, CI [0.051, 0.107]), three-seed mean +0.107; 8 Oct 2026 | https://arxiv.org/abs/2610.12601 | SUPPORTED | "Held-out citation reward rises by 0.079, from 0.702 to 0.781, with a bootstrap 95% confidence interval of [0.051, 0.107], and the gain replicates across three seeds (mean 0.107)." | "Submitted on 8 Oct 2026" confirmed. |
| 90 | SWE-Bench-Verified single-run pass@1 varies 2.2–6.0 points, SD above 1.5 at temperature 0; 2–3 point gains may be noise | https://arxiv.org/abs/2602.07150 | SUPPORTED | "single-run pass@1 estimates vary by 2.2 to 6.0 percentage points depending on which run is selected, with standard deviations exceeding 1.5 percentage points even at temperature 0" | |
| 97 | Research-agent evals combine groundedness checks that "verify that claims are supported by retrieved sources" with coverage checks | https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents | SUPPORTED | "Groundedness checks verify that claims are supported by retrieved sources, coverage checks define key facts a good answer must include" | |
| 100 | DRB II: 132 tasks, about 9,430 binary rubrics scored 1/0/-1, GPT-5.5 judge, public `tasks_and_rubrics.jsonl` | https://github.com/imlrz/DeepResearch-Bench-II | SUPPORTED | "we retain **132 expert-authored reports**" … "GPT-5.5 is prompted to output, for each rubric item: `score ∈ {1, 0, -1}`" | "9,430 expert-written rubrics" is in News, and the jsonl is in the top-level files. |
| 106 | DeepResearch Bench repo shows Apache-2.0 in its sidebar and MIT in its README badge | https://github.com/Ayanami0730/deep_research_bench | SUPPORTED | Sidebar: "License: Apache-2.0 license"; README line 4: `img.shields.io/badge/Code_License-MIT-blue` | The LICENSE file itself is Apache 2.0. |

## 4. Totals

| Verdict | Count |
| --- | --- |
| SUPPORTED | 17 |
| PARTIAL | 3 (#1, #45, #80) |
| UNSUPPORTED | 0 |
| UNREACHABLE | 0 |

Every sampled number matched its source. None of the three PARTIALs was a wrong number: two were
wrong locations and one was an overstated qualifier.

## 5. Failure patterns and the stage that introduced them

1. **The synthesizer narrowed a citation and dropped the part that holds the quote (#80).**
   Stage: synthesizer. The note (prompt-optimization-loops.md:68) cites "SKILL.md lines 386-394 and
   scripts/run_loop.py lines 79-234". The findings keep only run_loop.py:79-234, where neither the
   quoted phrase nor the 60/40, 3-run and 5-iteration defaults appear. The Evidence list still names
   SKILL.md:386-394, but the inline citation does not.
2. **A claim made stronger than its source by dropping a qualifier during the merge (#45).** Stage:
   synthesizer. The note (citation-faithfulness.md:84) states the numbers and keeps the exception
   ("in AI-Q hallucinations were about 31% … TrajectoryKit about 95%"). The findings compress this to
   "mostly citation-related" across all three systems, which the paper explicitly contradicts for
   TrajectoryKit.
3. **Wrong line number for part of a merged claim (#1).** Stage: researcher. The note
   (internal-audit.md:14) already carries ":7-8" for "one run per case per arm", which is on line 4.
   The synthesizer copied it faithfully.

Minor patterns that did not change a verdict:
- **Derived numbers shown as if quoted (#42).** Stage: researcher. The note gives "unsupported"
  rates that are complements of the paper's Fact Check accuracy. The arithmetic is exact, but a
  verifier string-matching numbers against the page would not find 23.2% and so on.
- **A source's internal conflict not flagged (#44, outside the sample).** Stage: researcher. In
  2605.06635v1, Table 3's caption labels the 78.6%→16.7% series "Claude Opus 4.6", while the text gives
  GPT-5.4 as "79% to 17%" and Opus 4.6 as "80% to 58%". The note and the findings follow the text
  (GPT-5.4 21.4%→83.3%) without recording the conflict.
