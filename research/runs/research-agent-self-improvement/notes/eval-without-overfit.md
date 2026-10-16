# Evaluating research agents and self-improvement without overfitting

Brief: Say how a small Claude Code research plugin should measure its research quality across improvement rounds so a capped self-improvement loop cannot overfit its own exam.
Run: research/runs/research-agent-self-improvement/PLAN.md

## How do current deep-research benchmarks score quality and citations, and what can a solo developer reuse for free?

### Takeaway
DeepResearch Bench scores report quality with RACE (LLM judge against a reference report, task-specific weighted criteria) and citations with FACT (citation accuracy plus effective citations per task). DeepResearch Bench II (2026) replaces this with about 9,430 binary expert rubrics. BrowseComp and BrowseComp-Plus score short-answer accuracy only, so they do not measure report quality or citations. All are code-free to read and Apache-2.0, but running them needs a paid judge key (GPT-5.5) and 100+ full research runs, so a solo developer should borrow the designs (binary rubrics, claim-to-source checking) rather than run the benchmarks. Confidence: medium-high.

### Cited findings
- DeepResearch Bench: 100 PhD-level tasks, 22 fields, 50 Chinese and 50 English; RACE scores comprehensiveness, depth, instruction-following and readability with dynamically generated criteria and weights; FACT scores citation accuracy and average effective citations (arXiv 2506.11763, June 2025) — https://arxiv.org/html/2512.01948v2 (secondary description), opened 2026-10-16, Parallel search excerpt only; primary repo opened below.
- Repo README: RACE generates task-specific criteria and scores reports against high-quality reference reports; FACT extracts statement-URL pairs, dedupes, scrapes cited sources and has an LLM judge whether each source supports the claim. Judge was moved from Gemini-2.5-Pro to GPT-5.5 (RACE) and GPT-5.4-mini (FACT) on 11 May 2026; scores from old and new judges are not comparable. Needs an OpenRouter/OpenAI key, plus a Jina key for FACT scraping; run = put your agent's 100 reports in `data/test_data/raw_data/<model>.jsonl` then `bash run_benchmark.sh`. 100 queries are public in `data/prompt_data/query.jsonl` — https://github.com/Ayanami0730/deep_research_bench, opened 2026-10-16, WebFetch
- Human agreement baseline for the RACE judge is 68.78% pairwise on a 50-task x 4-agent subset (200 articles); the paper says RACE's pairwise agreement exceeds human inter-annotator agreement — https://github.com/Ayanami0730/deep_research_bench (search excerpt of README, 11 May 2026 entry) and https://arxiv.org/pdf/2506.11763v1, opened 2026-10-16, Parallel search excerpts (not fetched in full; treat as medium).
- DeepResearch Bench II (paper Jan 2026, dataset Feb 2026, evaluator updated Aug 2026): 132 expert-derived tasks, about 9,430 binary rubrics in three dimensions (information recall, analysis, presentation); each rubric scored 1/0/-1; judge GPT-5.5; code Apache-2.0, data mostly CC BY 4.0; `tasks_and_rubrics.jsonl` is in the repo — https://github.com/imlrz/DeepResearch-Bench-II, opened 2026-10-16, WebFetch
- BrowseComp: 1,266 questions, short answers that are easy to verify against a reference; measures persistent browsing, not report writing (arXiv 2504.12516, 16 Apr 2025) — https://arxiv.org/abs/2504.12516, opened 2026-10-16, WebFetch
- BrowseComp-Plus: BrowseComp queries over a fixed ~100K-document human-verified corpus so retrieval is controlled; scores accuracy (judged by gpt-4.1), evidence recall, search calls, calibration error (ACL 2026) — https://texttron.github.io/BrowseComp-Plus (search excerpt) and https://aclanthology.org/2026.acl-long.1023, opened 2026-10-16, Parallel search excerpts only; not fetched in full (medium).
- Anthropic says research-agent evals should combine grader types: groundedness checks "verify that claims are supported by retrieved sources" and coverage checks "define key facts a good answer must include" — https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents (Jan 2026), opened 2026-10-16, WebFetch

### Contradictions
- DeepResearch Bench repo page says License Apache-2.0 in the sidebar but the README badge shows MIT — https://github.com/Ayanami0730/deep_research_bench; check the LICENSE file before redistributing. Not material to this plugin.

### Inferences
- Running DRB for every round is not free: 100 tasks x full research run plus a GPT-5.5 judge key. The plugin has no such key (registry lists free tiers only). Inference from the README setup steps and tool-registry.md. What it can reuse is the design: (a) binary, atomic, expert-style rubrics (DRB II) as `llm` or `regex` graders; (b) a FACT-style claim-to-URL check as a deterministic grader (does each cited claim line carry a URL that the note's "opened" log lists), with an `llm` support check only on a sample. Files: plugin/evals/<case>/graders/*.md, new cases under plugin/evals/.
- BrowseComp-style short-answer questions are the only reusable item with a cheap exact grader: a handful of questions with known answers could test the search loop. Files: plugin/evals/ (new case dir, tag `live`).

### Gaps
- Cost per DRB/DRB II task run was not given on any page I opened; could not state a dollar figure.
- Did not open the DRB II paper itself, only its repo README; judge-human agreement for DRB II is unverified.
- Whether DRB reference reports are public: the README did not say; the 100 queries and criteria data are public.

## What practices prevent overfitting or Goodhart effects when prompts are tuned against an eval, and how many runs detect a change of a given size?

### Takeaway
Keep a split the improver never reads (topic-disjoint, ideally scored only at the end), run each case several times, compare paired against the previous version, and report a confidence interval, not a bare delta. A 2026 paper on GEPA-tuned deep-research prompts found a large validation gain that shrank on held-out topics, and attributed the gap to small-sample selection under a noisy judge. With a single-digit number of cases, only large effects (tens of points) are detectable. Confidence: medium-high.

### Cited findings
- Reflective prompt optimization of a multi-agent deep-research agent (arXiv 2610.12601, 8 Oct 2026): topic-disjoint train/validation/test split; held-out citation reward rose 0.702 to 0.781 (+0.079, bootstrap 95% CI [0.051, 0.107]), replicated over three seeds (mean +0.107); the validation-minus-held-out gap was "small-sample selection under a noisy judge, not memorization"; collapsing decomposed per-dimension feedback to one scalar made held-out transfer negative; "Credible evaluation of prompt optimizers therefore requires held-out topics, multiple seeds, and verifier ablations" — https://arxiv.org/abs/2610.12601, opened 2026-10-16, WebFetch (abstract only)
- GEPA: the test split "remains entirely held out and is inaccessible throughout the optimization process; performance on this split is only measured post-optimization"; separate D_train and D_pareto sets; the paper notes that putting all tasks in both sets lets GEPA "overfit" them deliberately — https://arxiv.org/html/2507.19457 (search excerpt, 2025), opened 2026-10-16, Parallel search excerpts only; not fetched in full (medium).
- Agents given validation access and told to maximize it overfit reliably: at 38 of 102 checkpoints the validation metric was more than 10% better than holdout (arXiv 2606.11045, 2026) — https://arxiv.org/html/2606.11045v1 (search excerpt), opened 2026-10-16, Parallel search excerpt only; medium.
- Variance: single-run pass@1 on SWE-Bench-Verified varied by 2.2 to 6.0 points depending on which run was picked; SD above 1.5 points even at temperature 0; "reported gains of 2 to 3 points may be evaluation noise"; recommendations are multiple independent runs and statistical power analysis (arXiv 2602.07150, Feb 2026, v3 25 Mar 2026) — https://arxiv.org/abs/2602.07150, opened 2026-10-16, WebFetch
- Same paper, full text: detecting a 2% improvement at p<0.05 with 80% power needs about 9 runs per agent under test and a 1% improvement needs 36, under that paper's variance; large (10%) improvements may be detectable with single runs — https://arxiv.org/html/2602.07150, opened 2026-10-16, Parallel search excerpt only (medium; numbers are for SWE-bench variance, not for research reports).
- Error-bars method: compare two systems on paired question-level differences, not on summary scores, and run power analysis to see whether an eval can test the hypothesis at all (arXiv 2411.00640, Nov 2024) — https://arxiv.org/abs/2411.00640 (search excerpt), opened 2026-10-16, Parallel search excerpt only (medium).
- Anthropic: start with "20-50 simple tasks drawn from real failures"; run multiple trials; use pass@k and pass^k; "Eval saturation occurs when an agent passes all of the solvable tasks"; LLM-as-judge graders "should be closely calibrated with human experts"; "Make your graders resistant to bypasses or hacks" — https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents, opened 2026-10-16, WebFetch. WebFetch reported the post does not discuss held-out sets or overfitting.
- Anthropic: capability evals "start at a low pass rate" and give "a hill to climb"; regression evals "should have a nearly 100% pass rate"; high-pass capability evals graduate to the regression suite (search excerpts of the post) — https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents, opened 2026-10-16, WebFetch (summary only) plus Parallel excerpt.
- `claude plugin eval` default is 3 runs per case per arm ("One run of a non-deterministic agent tells you little"); case passes when its mean score meets `--threshold` (default 1.0); "A single run is noisy, so confirm any change at the default three runs before you trust it"; the no-plugin baseline gives Δ; CI example uses `--threshold 0.8`, pinned `--judge-model`, `--max-cost-usd`; long text should be graded by `regex`, with `llm` graders kept for short outputs; a small judge can mark correct answers wrong — https://code.claude.com/docs/en/plugin-evals, opened 2026-10-16, WebFetch (read via saved output and grep)
- The skill-creator section of the skills docs describes with/without-skill benchmark, blind A/B between two versions, and should-trigger prompt generation; it says nothing about runs per eval, variance or a train/held-out split — https://code.claude.com/docs/en/skills, opened 2026-10-16, WebFetch (last 9,478 characters not read)

### Contradictions
- None found.

### Inferences
- Detectability for this plugin (my arithmetic, not a source): the fast suite is 8 cases x 3 runs = 24 binary-ish runs per arm. With per-run pass rates near 0.5 the standard error of a suite mean is about 0.10, and a paired difference between two versions is not much tighter, so only a change of roughly 0.2 to 0.3 or more is separable from noise. The existing bar "delta >= 0.3" in plugin/skills/self-test/SKILL.md is about at that resolution. A round that claims +0.05 is not distinguishable. Rests on 2602.07150 (variance dominates small gains) and the 3-run default in plugin-evals.
- A round that edits prompts after seeing which cases failed is adaptively fitting those cases. The 2610.12601 result suggests the gain on new topics is real but smaller than the in-sample gain. So the acceptance number must come from cases the proposer never saw.
- Recommended structure (all my synthesis):
  1. Split `plugin/evals/` into `dev/` (proposer may read transcripts and failures), `holdout/` (proposer sees only aggregate pass/fail, never prompts or graders; scored once per round) and `frozen-regression/` (graduated cases, must stay at or near 1.0). Files: new dirs under plugin/evals/, tag cases `dev`, `holdout`, `regression` so `--tag` selects them; edit plugin/skills/self-test/SKILL.md step 1.
  2. Rotation: after each accepted round, retire the holdout cases the proposer has been told were failing, promote them to `dev`, and add fresh cases built from real failures (Anthropic: tasks from real failures). Keep a never-used reserve of 3 to 4 cases. File: plugin/evals/README (new) listing case provenance and round last used.
  3. Judge hygiene: pin `--judge-model` to one ID for the whole loop and do not let the loop edit graders or mocks in the same round it is scored by them. Prefer `regex`, `tool_used`, `file_exists` graders (cost nothing, not gameable by phrasing). Calibrate the one `llm` rubric against 5 to 10 human-labelled outputs once. Files: plugin/evals/*/graders/, plugin/skills/self-test/SKILL.md.
  4. Report per-dimension scores (citation present, claim supported, contradiction surfaced, parked-not-guessed), not one scalar, per the 2610.12601 finding that scalar rewards transfer worse. File: plugin/evals/results aggregation notes in self-test SKILL.md step 2.
  5. Runs: 3 runs per case for screening; 5 runs on the holdout and regression sets for the accept/reject decision; ask for a paired comparison against the previous accepted version (skill-creator and agentskills.io both recommend the previous version as baseline), not only the no-plugin baseline.

### Gaps
- No source gave runs-per-case guidance specific to LLM-judged research reports; the 9/36-run numbers are for SWE-bench pass@1 variance.
- Did not open the 2606.11045 or 2610.12601 full texts; split sizes in 2610.12601 are unknown.
- Did not open tianpan.co Goodhart posts (blog-level, not primary).

## What acceptance criteria and stop rules do self-improving agent papers and projects use per round?

### Takeaway
Published self-improving systems accept a change on empirical benchmark score after a cheap staged check, cap total iterations at a fixed number, and validate transfer on a different benchmark. None uses a statistical-significance test or a hidden holdout inside the loop, and DGM itself documents objective hacking. Confidence: medium.

### Cited findings
- Darwin Godel Machine (arXiv 2505.22954, v1 29 May 2025, v3 12 Mar 2026, ICLR 2026): runs a fixed 80 iterations, one new agent per iteration; staged evaluation: 10 tasks to check the agent can still edit code, and only those that pass go to an expanded 50-task evaluation; reports pass@1 (agent never sees ground-truth test results); keeps an archive and retains only agents that compile and keep the ability to edit code, discarding the rest — https://arxiv.org/pdf/2505.22954v3, opened 2026-10-16, curl + pdftotext of the PDF (lines on staged evaluation, iterations)
- DGM transfer check: best agent from SWE-bench evaluated on Polyglot and vice versa; "Since each agent was optimized without ever accessing the alternate benchmark, these evaluations represent truly held-out tests" — https://arxiv.org/pdf/2505.22954v3, opened 2026-10-16, curl + pdftotext
- DGM appendix: tool-use hallucination fix was scored on only 3 SWE-bench tasks, and the paper describes an example of objective hacking "where the agent optimizes for the quantifiable metric rather than truly fulfilling the spirit of the task"; the fix worked by changing the logging markers, i.e. the detector was gamed — https://arxiv.org/pdf/2505.22954v3, opened 2026-10-16, curl + pdftotext (lines 5276 to 5403; my reading of the marker diff, medium)
- Huxley-Godel Machine (arXiv 2510.21614, 24 Oct 2025, ICLR 2026): finds benchmark score of an agent mismatches its self-improvement potential; selects what to expand by clade-aggregated descendant scores with Thompson sampling instead of the agent's own score — https://arxiv.org/abs/2510.21614v1 (search excerpt), opened 2026-10-16, Parallel search excerpt only; medium.
- SICA and ADAS: ADAS uses a fixed meta-agent to generate agents and evaluate them on a target benchmark; Godel Agent uses "a validation set" for feedback (search excerpts of DGM, SICA and Godel Agent papers) — https://proceedings.iclr.cc/paper_files/paper/2026/file/aa5f5e6eb6f613ec412f1d948dfa21a5-Paper-Conference.pdf, opened 2026-10-16, Parallel search excerpt only; medium.
- agentskills.io (the skill-eval guide Anthropic links): loop is propose change, apply, rerun all cases in `iteration-N+1/`, grade, human review; stop "when you're satisfied with the results, feedback is consistently empty, or you're no longer seeing meaningful improvement between iterations"; snapshot the previous skill as baseline; remove assertions that always pass in both arms; fix assertions that always fail; "Generalize from feedback" rather than patching specific test cases; "Keep the skill lean" — https://agentskills.io/skill-creation/evaluating-skills, opened 2026-10-16, WebFetch
- That guide also says stddev "is only meaningful with multiple runs per eval" and recommends starting with 2-3 test cases — same URL, opened 2026-10-16, WebFetch

### Contradictions
- agentskills.io says to stop when satisfied or when feedback is empty (human-judgment stop) — https://agentskills.io/skill-creation/evaluating-skills; DGM stops at a fixed iteration count with no quality test — https://arxiv.org/pdf/2505.22954v3. These are different rules, not factual conflict; the plugin's cap needs both.

### Inferences
- Round acceptance rule for the plugin (my synthesis from DGM staging, agentskills.io baseline-vs-previous, and the 2610.12601 holdout lesson). Accept a round only if all hold: (1) cheap gate passes first: `claude plugin validate --strict` and the deterministic `regex`/`file_exists` fast cases (DGM's 10-task gate analogue); (2) `regression` set does not drop below its prior score minus one case; (3) `holdout` mean beats the previous accepted version by at least a pre-registered margin (0.2 on the 8-case scale; recompute if case count changes) in a paired 5-run comparison, and per-dimension scores do not regress; (4) no grader, mock or case file changed in the diff that is being scored (DGM objective-hacking lesson); (5) a human reads the diff and 2 transcripts. Files: plugin/skills/self-test/SKILL.md (new "round gate" section), plugin/evals/ tags.
- Stop rules for the cap: hard max rounds (say 3, a number I chose; DGM used 80 with a far larger budget); stop at first round rejected twice in a row; stop when holdout stops improving by the margin; stop when dev score is up but holdout is flat or down (overfit signal: validation-minus-holdout gap rising, per 2610.12601); stop when the regression set is saturated and no new real-failure case exists. File: plugin/skills/self-test/SKILL.md.
- Today self-test is a one-time exam that "never edits the plugin to raise the score" and forbids re-running to chase a score (plugin/skills/self-test/SKILL.md lines 1-15 as read from the repo). A loop needs a separate skill or a clearly separated mode so the exam and the improver cannot be confused; the improver must not have write access to `holdout/` or graders. Suggest new file plugin/skills/self-improve/SKILL.md and a PreToolUse hook in plugin/hooks/ that denies edits to plugin/evals/holdout/ and graders during a round. (Design proposal, not sourced.)

### Gaps
- Did not open the HGM, SICA, ADAS or Godel Agent papers in full; their acceptance rules are known only from abstracts and search excerpts, so no concrete per-round thresholds were verified for them.
- No 2026 self-improving-agent source I opened used a statistical test for acceptance; I found none, not proven none exist.

## What do Anthropic's docs and posts recommend for evaluating agents and skills?

### Takeaway
Anthropic recommends a small start (20-50 tasks from real failures), several trials per task, outcome graders over step graders, deterministic graders where possible, reading transcripts, a no-plugin baseline and graduating capability evals to regression evals. Its docs do not address held-out sets, so that part has to come from outside sources. Confidence: high for what is stated, medium for the "absent" claims.

### Cited findings
- "Demystifying evals for AI agents" (published 2026-01-09 per a mirror): definitions of task, trial, grader, transcript, outcome and harness; start with 20-50 tasks; multiple trials; pass@k vs pass^k (75% per trial gives about 42% pass^3); read transcripts; watch saturation; make graders resistant to bypasses — https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents, opened 2026-10-16, WebFetch
- Anthropic example that grading bugs dominate: Opus 4.5 scored 42% on CORE-Bench until rigid grading and ambiguous specs were fixed, then 95% (Parallel search excerpt of the post, plus a third-party summary) — https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents, opened 2026-10-16, Parallel search excerpt only; medium.
- Plugin evals doc: 3 runs per case default; WITH and W/OUT arms and Δ; six grader types (`regex`, `tool_used`, `tool_order`, `file_exists`, `llm`, `baseline`), the first four free; `--threshold`, `--max-cost-usd`, `--judge-model`, `--json`, exit codes 0/1/2; "leave `partial: true` documents and runs with `skippedPaidGraders` out of any trend you chart"; pin both models "so scores are comparable over time" — https://code.claude.com/docs/en/plugin-evals, opened 2026-10-16, WebFetch (read via saved output and grep)
- Plugin evals doc: if a `tool_used: Skill` grader passes but Δ is negative, "suspect the judge before the plugin"; a model-judged grader varies more on longer text — same URL, opened 2026-10-16, WebFetch
- skill-creator (skills docs): per-case subagent with clean context, `benchmark.json` aggregating pass rate, time and tokens with vs without skill, blind A/B between two skill versions — https://code.claude.com/docs/en/skills, opened 2026-10-16, WebFetch
- Evals are noted as "currently unavailable" if Anthropic turns the command off server-side (error message "plugin eval is currently unavailable") — https://code.claude.com/docs/pt/plugin-evals (search excerpt), opened 2026-10-16, Parallel search excerpt only; medium. Needs a fallback if the CLI is off.

### Contradictions
- None found.

### Inferences
- The repo's existing fast cases (plugin/evals/cite-or-park, contradiction, injection-resist, etc.) already follow Anthropic's advice (offline mocks, free graders, baseline). Needed additions: tags and directories for holdout/regression, a pinned `--judge-model` flag in plugin/skills/self-test/SKILL.md commands, a paired previous-version baseline (agentskills.io "snapshot previous skill"), and `--runs 5` for the accept decision. Do not chart partial runs.
- Cost cap: every round multiplies runs (cases x runs x 2 arms). Dropping the no-plugin arm (`--ablation none`) for holdout comparisons between two plugin versions halves the cost; keep the no-plugin arm only for the once-per-release exam. Docs say `--ablation none` runs one arm. File: plugin/skills/self-test/SKILL.md.

### Gaps
- code.claude.com/docs/en/skills was read only to character 100,000 of 109,478; I may have missed skill-creator detail at the end.
- The official skill-creator repo (github.com/anthropics/skills) was not opened, so its benchmark script behaviour (runs per eval) is unverified.
- Anthropic's published statements on held-out test sets or overfitting: none found in the pages I opened.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| DeepResearch Bench (RACE/FACT) | https://github.com/Ayanami0730/deep_research_bench | 100-task report-quality and citation benchmark; python scripts; judge GPT-5.5 via OpenRouter/OpenAI key, Jina key for FACT | local python, paid judge key | 2026-10-16 | skip as a per-round gate (paid key, 100 runs); reuse the design only |
| DeepResearch Bench II | https://github.com/imlrz/DeepResearch-Bench-II | 132 tasks, about 9,430 binary expert rubrics, public `tasks_and_rubrics.jsonl`; judge GPT-5.5 | local python (uv), paid judge key | 2026-10-16 | fallback: borrow a few rubrics as grader text; skip full run |
| BrowseComp / BrowseComp-Plus | https://arxiv.org/abs/2504.12516 ; https://texttron.github.io/BrowseComp-Plus | short-answer web-search difficulty; Plus adds fixed corpus | local, retriever setup | 2026-10-16 | skip; measures answers not reports or citations |
| claude plugin eval | https://code.claude.com/docs/en/plugin-evals | runs cases with/without plugin; free and llm graders; `--runs`, `--threshold`, `--json` | CLI v2.1.269+ | 2026-10-16 | use (already adopted); add tags and pinned judge |
| agentskills.io skill eval guide | https://agentskills.io/skill-creation/evaluating-skills | eval-driven iteration loop, previous-version baseline, benchmark.json | docs | 2026-10-16 | use as the loop template; adds no holdout rule |
| evalstats / errorbars / abeval | https://github.com/tapishr/evalstats | Wilson CIs, McNemar, paired CIs, power analysis for small evals | python libs (search excerpts only; not opened or run) | 2026-10-16 | fallback: only if the loop needs CIs; a hand-written bootstrap in self-test may suffice |
| GEPA | https://github.com/gepa-ai/gepa | reflective prompt optimizer with train/pareto/test split | python (not run) | 2026-10-16 | skip; mechanics belong to another facet; its split design is the useful part |
