# Research-agent self-improvement: what to change first, and how to judge a capped loop

The v0.1 self-test score of 0.97 measures whether the lead follows the routing and output-shape rules on mocked pages. It does not measure the part of the pipeline where outside evidence says citation errors arise: the merge step, then verification. The one plugin agent meant to catch those errors, the verifier, cannot reopen pages fetched through Firecrawl, Playwright or a clone. It has never run on real content, and all five existing findings files are `unverified`. Published audits find 12% to 97% unsupported statements in deep-research systems (DeepTRACE, Sep 2025) and 23% to 76% factually unsupported citations across 14 models (May 2026). Dead links account for only 0% to 6%. In one three-system study the orchestrator or merge stage caused 53% to 100% of final-report errors. So the changes that most raise research quality are, in order: (1) make the verifier able to re-fetch and check claims against a verbatim quote, then run it on the existing findings; (2) carry a verbatim `Quote:` with every claim from note to findings, and add a "no information not backed by a cited line" rule to the synthesizer, which in one measured case raised citation precision from 87.6 to 91.0-94.1; (3) make clone and repo `path:line` citations legal, because the synthesizer's URL-only rule currently drops them. For context rot, the cheapest gains come from four changes. Re-inject the active run's PLAN.md and a run ledger from the existing `compact` SessionStart hook. Stop that hook truncating INDEX.md to its first 30 lines. Tell Sonnet workers that they may be compacted and must not wrap up early. Copy constraints verbatim into every dispatch. A self-improvement loop should be a separate skill from the self-test exam. It should use a split the proposer never reads (dev, holdout, frozen regression), pin the judge, freeze graders and mocks during a round, compare paired against the previous accepted version over several runs, and report per-dimension scores rather than one scalar. It should be capped at a fixed number of rounds with stated stop rules. With 8 cases at 3 runs, only changes of roughly 0.2 to 0.3 can be told apart from noise (worker inference). The self-test must first gain graders for the pipeline tail, or a loop would be optimising an exam that cannot see the verifier.

## Questions and answers

### Q1. What does the plugin's own evidence show about v0.1's weak and untested areas?

Confidence: high on the facts (each is a file and line in this repo), medium on the ranking.

The self-test record gives 0.97 against a 0.8 bar and a delta of 0.76 against a bar of 0.3. 7 of 8 cases scored 1.0, from one run per case per arm (docs/self-test/2026-10-16-v0.1.md:7-8). The single failing grader (`injection-resist` `no-beacon`) was itself broken. It was fixed afterwards and "has not been re-run" (docs/self-test/2026-10-16-v0.1.md:23-29). The record states its own limits: one run per case, the two live cases not run, and mocked pages only, so it "measures the workflow and output rules, not live search quality" (docs/self-test/2026-10-16-v0.1.md:31-38).

The graders are weak in several places. The no-plugin baseline scored 1.0 on `one-fact-inline` and passed some graders in `injection-resist`, `system-map-diagrams` and `cite-or-park` (plugin/evals/results/2026-10-16T02-20-47-488Z/aggregate-result.json, read with Bash `jq`). `cite-or-park`'s `reply-says-gap` regex accepts `403|blocked|unreachable` anywhere in the reply (plugin/evals/cite-or-park/graders/reply-says-gap.md:5-7). `one-fact-inline`'s `cites-url` only needs `https?://\S+` and never checks that the URL was opened. The only open-page check is `with-only` and was reported as `scored: false` (plugin/evals/one-fact-inline/graders/cites-url.md:3-5, content-calls.md:5-9). No grader in any case checks a `## Verification` section, an INDEX line, PLAN.md, the worker cap, the return-line limit, or that the lead did not open notes. The case list has no spike, tool-scan, gap-round or compaction case (plugin/skills/self-test/SKILL.md:127-138, plus a Grep over plugin/evals/*/graders). The prompts for `cite-or-park` and `contradiction` are single-facet (plugin/evals/cite-or-park/prompt.md:10, plugin/evals/contradiction/prompt.md:10). The internal-audit worker infers that most of the 0.76 delta comes from file-existence and mock-availability checks, so it shows that procedures are followed, not that the research is better (inference).

Reading the prompts together turns up conflicts that the mocked suite cannot catch:
- **Verifier tool gap.** Researchers fall back from Parallel to Exa, then Firecrawl, then Playwright (plugin/agents/researcher.md:64-65). The verifier has no Bash, Firecrawl or Playwright (plugin/agents/verifier.md:6), so a page opened by those routes is marked "page did not open" (verifier.md:23-24). It also cannot reopen clone citations.
- **Verifier sample.** The verifier is told to pick "up to 20" pairs, but must also include every summary claim, every number and every high-confidence claim (verifier.md:17-18). It runs on `model: haiku` (verifier.md:4).
- **Clone citations are dropped.** The researcher is told to "Cite the file path in the clone and the repo URL" (researcher.md:67-68). The synthesizer excludes any claim "with no URL" (synthesizer.md:24-26), and the note schema requires a URL on every Cited findings line (plugin/skills/research/note-schema.md:10-11). This run needed a lead ruling to keep its own repo-file citations (PLAN.md Rulings).
- **Three registry writers.** The lead writes rows in tool-scan and repo-triage (tool-scan/SKILL.md:18-20, repo-triage/SKILL.md:24-26). The synthesizer writes them in normal mode (synthesizer.md:65-66). In a spike the synthesizer writes them and "nobody else writes those rows" (spike/SKILL.md:67-68), yet spike step 2 runs repo-triage, where the lead writes a row (repo-triage/SKILL.md:46-47).
- **Budget conflict.** Tool-scan allows up to three candidates per cluster, each needing five or more steps (tool-scan/SKILL.md:34-47). The researcher stops at "about 10 to 15 tool calls" (researcher.md:47-48).
- **Rules with no actor.** One EARS rule says output over 25,000 characters must run "in a subagent" (research/SKILL.md:208-209), but researchers have `disallowedTools: Agent` (researcher.md:9). The same holds for routing.md's Playwright and Mermaid "in a subagent" (routing.md:12, 16-17). For Mermaid, system-map says "No plugin agent has this tool" (system-map/SKILL.md:50-51).
- **Connector probing unspecified.** The research skill says "Check which search tools exist" but gives no method (research/SKILL.md:77-80, 120).
- **Hook truncation.** The hook injects `head -n 30` of INDEX.md (plugin/hooks/session-start.sh:14). INDEX.md allows up to 200 lines with a 9-line header (research/findings/INDEX.md:1-9), so after about 20 findings the newest stop being injected (inference).
- **Worker caps.** "Never more than 8 workers per run" includes the gap round (research/SKILL.md:17, 38). Spike's per-path triage researchers are not counted against it (spike/SKILL.md:55).

Nothing in the evidence base itself has been verified. All five INDEX lines end `unverified` (research/findings/INDEX.md:11-15). `grep -c "## Verification"` returns 0 for all five findings files. methodology.md and packaging.md run to 533 and 543 lines (`wc -l`, Bash). The routing table's evidence is one of those unverified files (routing.md:5).

**Contradictions** (inside the repo, all from the internal-audit note):
- plugin/skills/research/routing.md:13 gives "Parallel fetch with full content, in a subagent" as the verify-and-cite fallback. plugin/agents/researcher.md:46 says "never use Parallel `full_content`". The evidence favours the researcher rule. The researcher, which is the agent that fetches, cannot spawn subagents (researcher.md:9), so no agent can carry out routing.md's "in a subagent" part. Resolve by deleting the routing.md fallback.
- plugin/skills/spike/SKILL.md:67-68 ("nobody else writes those rows") disagrees with plugin/skills/repo-triage/SKILL.md:46-47 (the lead writes the row). This is unresolved as a design choice: one owner per verdict must be named.
- plugin/agents/synthesizer.md:24-26 sends excluded claims to `## Open questions`. synthesizer.md:79-80 and plugin/skills/research/SKILL.md:210-211 send them to "Gaps". findings-format.md has no Gaps section, only Open questions (findings-format.md:18), so the evidence favours Open questions.

### Q2. Which changes would most raise research quality?

Confidence: medium. The failure rates are measured. The effect sizes come from one study (AI-Q) and are vendor-qualitative elsewhere. Quote-first alone has no measured effect.

**How often citations fail without checks.** DeepTRACE (303 queries, 9 systems, Sep 2025) measured unsupported statements from 12.5% (GPT-5 DR) to 97.5% (Perplexity DR), and citation accuracy of "40-80% across systems" (https://arxiv.org/html/2509.04499). Its judge correlated with human labels at only r=0.62. "Cited but Not Verified" (130 queries, 14 models, May 2026) found factually unsupported citations at 23.2% for Claude Opus 4.5, 31.1% for Haiku 4.5, 41.3% for Sonnet 4.6, 45.8% for Opus 4.6 and up to 75.6% for OSS-120B. Dead links were only 0% to 6% for frontier models, and the paper says surface metrics "mask factual failures" (https://arxiv.org/html/2605.06635v1). The same paper found that more search made things worse: GPT-5.4's unsupported rate rose from 21.4% to 83.3% going from 2 to 150 tool calls, and Opus 4.6's from 20.0% to 42.1%. The worker infers that a verifier which only checks links resolve catches under 6% of failures (inference).

**Where errors arise.** In the AI-Q, MS-Agent and TrajectoryKit pipelines, the orchestrator caused 84.7%, 52.6% and 100% of final-report errors respectively, mostly citation-related. Researchers and multi-document searchers erred in 46% to 71% of sampled sentences, against 0.9% to 6.4% for single-document snippet searchers (https://arxiv.org/html/2608.24306v1). In this plugin, the synthesizer is the merge stage.

**What measurably helps.** In the AI-Q study (50 DeepResearch Bench examples), giving the orchestrator raw single-document snippets instead of synthesised notes raised citation recall from 64.5 to 69.7 and precision from 87.6 to 94.1, with RACE quality unchanged (52.6 to 52.4). Adding "do NOT use information which is not backed by citations" gave recall 69.6 and precision 91.0. Judge agreement with arbitrated humans was 76% (kappa 0.62), and the agent-level results rest on 20 examples (https://arxiv.org/html/2608.24306v1). In L-MARS, a multi-turn judge loop with a cross-provider verifier lifted strict citation F1 from 0.131 to 0.254 and cut no-citation answers from 34% to 13%. Even so, unsupported claims stayed at 36% to 54% (https://arxiv.org/html/2509.00761v4). Anthropic's hallucination guide recommends extracting word-for-word quotes first, then finding a supporting quote for each claim and retracting the claim if none exists. It gives no effect size (https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations). The Citations API guarantees "valid pointers to the provided documents", but needs documents passed as API blocks (https://platform.claude.com/docs/en/build-with-claude/citations). The worker infers that Claude Code subagents do not pass pages that way, so the plugin cannot rely on the API (inference, unverified).

**Checker reliability limits any single verdict.** In L-MARS, human-versus-Gemini kappa was 0.458 (strict binary) and 0.219 (3-class), and two LLM families agreed at 0.683. Human and model also disagreed on whether 15 of 20 URLs were reachable, because of fetch environment and link drift (https://arxiv.org/html/2509.00761v4). Cited-but-Not-Verified recommends ensemble or hybrid rule-plus-LLM checks (https://arxiv.org/html/2605.06635v1).

The resulting changes are ranks 1 to 3 in the Implications table: a working verifier with a risk-weighted sample, quote-first citations through note, synthesis and verification, and legal repo citations. The worker's sampling rule is an inference with thresholds of its own choosing: check every number, date, name, quote and single-source claim, plus a random 20% (minimum 5) of the rest, and re-check the whole note on any failure. Its reasoning: at a 20% to 50% per-claim error rate, a random 5 pairs finds at least one failure with probability 67% to 97%.

**Contradictions.** DeepTRACE gives Gemini DR citation accuracy as 50.3% in Table 1 and 40.3% in the Section 4 text, both at https://arxiv.org/html/2509.04499. This is unresolved; the PDF was unreadable in the session. Neither value changes the recommendation.

### Q3. Which changes would most raise resistance to context rot?

Confidence: medium. The degradation evidence covers older or non-Claude models. The mitigations are documented mechanisms plus worker inference, with no measured effect for this plugin.

**Degradation sets in well below the window.** NoLiMa (v3, 9 Jul 2025): at 32K tokens, 11 of 13 models fall below 50% of their short-context baseline. Claude 3.5 Sonnet went from 87.5 at base to 29.8 at 32K, an effective length of 4K against a claimed 200K (https://arxiv.org/html/2502.05167v3). Context length alone cut performance by 13.9% to 85% even with perfect retrieval and whitespace filler. Reciting the evidence first helped by up to 4% (https://aclanthology.org/2025.findings-emnlp.1264/, Nov 2025). The Context Rot Evaluation (22 May 2026) found drops of up to 94 percentage points when the task sits mid-context rather than at the end (https://arxiv.org/html/2605.23170). Anthropic's harness post (24 Mar 2026) reports "context anxiety" in Sonnet 4.5, strong enough that "compaction alone wasn't sufficient", and says Opus 4.5 "largely removed that behavior" (https://www.anthropic.com/engineering/harness-design-long-running-apps). Anthropic's prompting guide says Sonnet 5, Sonnet 4.6 and Haiku 4.5 track their remaining window and "may sometimes naturally try to wrap up work as it approaches the context limit" unless told that compaction will happen. It also recommends a fresh window that rediscovers state from files (progress file, structured test list, git log) over compaction (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices). A July 2026 taxonomy names the plugin-relevant failures without measuring them. "Context Rationale Erosion" is compaction removing "an important constraint". "Communication Failure" is the orchestrator omitting "necessary context", or a subagent not reporting constraints (https://arxiv.org/html/2607.28802v1).

**What the plugin already does and lacks.** hooks.json has only SessionStart, with matcher `startup|resume|clear|compact`. session-start.sh injects the using-research-agent skill and `head -n 30` of INDEX.md, but no run's PLAN.md. CLAUDE.md has a Compact instructions section. Researcher and spike-worker run on `sonnet`/`medium` with `maxTurns: 40`, and no agent sets `memory:` (plugin/hooks/hooks.json, session-start.sh, plugin/agents/*.md, CLAUDE.md; read with Bash). Per the sub-agents page, subagents auto-compact, a subagent stopped at `maxTurns` returns partial output that can be resumed via `SendMessage`, and per-agent `memory:` loads the first 200 lines or 25KB of that agent's MEMORY.md (https://code.claude.com/docs/en/sub-agents). The page does not say whether `compact` SessionStart hooks fire inside subagents.

The changes, all worker inferences built on the sources above, are ranks 4 to 6 in the Implications table:
- Re-inject the newest run's PLAN.md and a run ledger, and the newest INDEX lines, on `compact`.
- Keep a ledger line per returned worker, with the TAKEAWAY copied verbatim rather than paraphrased.
- After compaction or `/clear`, read PLAN.md, the ledger and `git log -5`, and offer `/clear` at phase boundaries.
- Tell workers to write the note skeleton first and that they may be compacted.
- Carry a verbatim Constraints block from PLAN.md in every dispatch, and have the verifier string-compare each note's Brief line against the plan.

The worker rates per-agent `memory: project` as low priority and default-off, because it adds up to 25KB at every worker start. It rates PreCompact, the API memory tool and `initialPrompt` as not worth adding (inference).

**Contradictions.**
- NoLiMa (https://arxiv.org/html/2502.05167v3) and the EMNLP paper (https://aclanthology.org/2025.findings-emnlp.1264/) show large drops at 4K to 32K. The Context Rot Evaluation (https://arxiv.org/html/2605.23170) finds three of four newer vendor releases within 6 percentage points at 64K under one filler type, but drops of 16 to 56 points under another. Task and filler decide the outcome, and none of the three tests Claude 4.5 or later. This is unresolved and listed under Open questions. The recommendations do not depend on it, because they target mid-context constraint loss, which all three show.
- The earlier file research/findings/context-management.md says auto memory "isn't loaded into subagents". The sub-agents page (https://code.claude.com/docs/en/sub-agents) says a subagent with `memory:` loads its own MEMORY.md. These describe different mechanisms (the parent's auto memory versus per-agent memory), so both hold. The earlier file also lists the SessionStart `compact` hook as optional; the plugin already ships it (hooks.json).

### Q4. How should the plugin propose and accept changes to its own prompts and skills?

Confidence: medium-high for what the tools do (read from docs and from source), medium for the adapted rule.

Every optimiser opened shares one shape: a task set, a metric, an LLM that proposes rewritten text, and a rule that keeps a candidate only if it scores better, usually on data separate from the data that drove the edit.
- **MIPROv2** proposes instructions from data and program summaries, then runs Bayesian search (https://dspy.ai/api/optimizers/MIPROv2/).
- **GEPA** samples from a Pareto frontier, reflects on traces from a minibatch (default 3), keeps an edit only "if improved" on the minibatch and then on the Pareto validation set, and stops at a budget (https://dspy.ai/api/optimizers/GEPA/overview/index.md). The GEPA paper (v2, 14 Feb 2026) reports beating GRPO by 6% on average with up to 35x fewer rollouts, and MIPROv2 by over 10% (https://arxiv.org/pdf/2507.19457). A GEPA blog post (18 Feb 2026) evolved coding-agent skills on about 200 train, 50 validation and 60 test tasks, then transferred them to Claude Code (https://github.com/gepa-ai/gepa/blob/main/docs/docs/blog/posts/2026-02-18-automatically-learning-skills-for-coding-agents/index.md).
- **TextGrad** back-propagates LLM critiques as "textual gradients" (https://github.com/zou-group/textgrad).
- **promptfoo `optimize`** (page updated 13 Oct 2026) proposes rewrites "using observed failures and prior scores". Its `--validation-split` judges adoption on held-out tests, and the page warns that the default full-set search "can overfit to the configured tests" (https://www.promptfoo.dev/docs/usage/prompt-optimization/).

All of these need a configured external LLM: GEPA asserts that a reflection LM or a custom proposer is given, and TextGrad needs an OpenAI or Anthropic key. No source showed that a free tier suffices.

Anthropic's skill-creator (https://github.com/anthropics/skills, cloned 2026-10-16, HEAD 2026-10-09) is the one mechanism that runs on markdown skills with no extra key. `improve_description.py` shells out to `claude -p` and "uses the session's Claude Code auth, no separate ANTHROPIC_API_KEY needed". Its parts:
- **Content loop.** Run with the skill and against a baseline, grade into `grading.json`, aggregate `benchmark.json` (pass rate, time, tokens, mean ± stddev, delta), run an analyst pass for non-discriminating and high-variance assertions, have a human review, then rerun in `iteration-N+1/`.
- **Baseline.** The baseline is `without_skill` for a new skill and the previous iteration for an existing one (SKILL.md:313).
- **Stop rule.** Stop when "the user says they're happy; the feedback is all empty; you're not making meaningful progress" (SKILL.md:316-322).
- **Description optimiser.** It splits the eval set 60/40 train/held-out, runs each query 3 times, caps at `--max-iterations 5`, and returns `best_description` chosen by test score "rather than train score to avoid overfitting" (run_loop.py:79-234).
- **Proposer guards.** The proposer sees "PREVIOUS ATTEMPTS (do NOT repeat these…)", may not grow a list of specific failing queries, and works to a 1024-character cap (improve_description.py:103-170).
- **Edit guidance.** Generalise rather than make "fiddly overfitty changes", keep the skill lean, and treat ALWAYS/NEVER in caps as "a yellow flag" (SKILL.md:298-306).
- **Blind A/B.** A comparator scores two outputs without knowing which skill made which; this step is "optional… most users won't need it" (agents/comparator.md:1-85, SKILL.md:325-330).

agentskills.io gives the same loop: snapshot the previous skill as the baseline, remove assertions that always pass in both arms, "Generalize from feedback", keep the skill lean, and note that stddev "is only meaningful with multiple runs per eval" (https://agentskills.io/skill-creation/evaluating-skills).

Adapted for this plugin (worker inference): a GEPA-style loop reduced to markdown, with one edit per round. Each edit gets a written record:
1. the failing case and a trace excerpt;
2. a one-sentence hypothesis;
3. the single edit;
4. the before and after scores on the failing case, then on all dev cases;
5. accept or reject.

Accepted changes become git commits on a branch, never auto-merged, and are listed in `research/self-improvement/changelog.md`. Rejected changes go to `research/self-improvement/rejected.md` with their hypothesis, and the proposer is shown that file as its "previous attempts". Skill-creator's grader, comparator and analyzer prompts can be copied into plugin agents. Do not install GEPA, MIPROv2, TextGrad or promptfoo: each needs a key, and the markdown loop captures their transferable part. No source gave a minimum effect size or a persisted rejected-changes log; both are plugin-side additions.

### Q5. How should a capped self-improvement loop be evaluated without overfitting to its own exam?

Confidence: medium. The split, variance and judge evidence is opened and recent. The thresholds and cap values are worker choices.

**Evidence that tuning against an eval overfits it.**
- A study of reflective prompt optimisation on a multi-agent deep-research agent (8 Oct 2026; abstract only) used a topic-disjoint train/validation/test split. Held-out citation reward rose from 0.702 to 0.781 (+0.079, bootstrap 95% CI [0.051, 0.107]), with a three-seed mean of +0.107. The validation-minus-held-out gap was "small-sample selection under a noisy judge, not memorization". Collapsing per-dimension feedback into one scalar made held-out transfer negative. The authors conclude: "Credible evaluation of prompt optimizers therefore requires held-out topics, multiple seeds, and verifier ablations" (https://arxiv.org/abs/2610.12601).
- The Darwin Gödel Machine (v3, 12 Mar 2026) checked transfer on a benchmark each agent "was optimized without ever accessing" (https://arxiv.org/pdf/2505.22954v3). Its appendix describes "objective hacking", where the agent "optimizes for the quantifiable metric rather than truly fulfilling the spirit of the task". In the worker's reading of the diff, the fix changed the logging markers that the detector looked for (inference, medium).
- Anthropic's evals post says to make graders "resistant to bypasses or hacks", but in the opened copy it does not discuss held-out sets (https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents).

**Evidence on noise.**
- Single-run pass@1 on SWE-Bench-Verified varied by 2.2 to 6.0 points depending on which run was picked, with SD above 1.5 even at temperature 0, so "reported gains of 2 to 3 points may be evaluation noise" (https://arxiv.org/abs/2602.07150, Feb 2026, v3 25 Mar 2026).
- `claude plugin eval` defaults to 3 runs per case per arm ("One run of a non-deterministic agent tells you little"). Its guidance: confirm any change at three runs; pin the judge and agent models "so scores are comparable over time"; grade long text with `regex` and keep `llm` graders for short outputs; a small judge can mark correct answers wrong; if `tool_used: Skill` passes but Δ is negative, "suspect the judge before the plugin"; keep `partial: true` runs out of trends; use `--ablation none` to run one arm (https://code.claude.com/docs/en/plugin-evals).
- v0.1 was scored on one run per case (docs/self-test/2026-10-16-v0.1.md:7-8).
- The worker's arithmetic (inference): with 8 cases × 3 runs and pass rates near 0.5, the standard error of a suite mean is about 0.10, so only changes of about 0.2 to 0.3 are separable from noise. The existing delta bar of 0.3 sits at that resolution. A claimed +0.05 is not distinguishable.

**Anthropic's eval guidance** (Jan 2026; https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents):
- Start with "20-50 simple tasks drawn from real failures" and run multiple trials.
- Use pass@k and pass^k; at 75% per trial, pass^3 is about 42%.
- "Eval saturation occurs when an agent passes all of the solvable tasks".
- LLM judges "should be closely calibrated with human experts".
- Research-agent evals should combine groundedness checks that "verify that claims are supported by retrieved sources" with coverage checks.
- Capability evals start at a low pass rate and graduate to regression evals, which should pass at "nearly 100%". The worker read this point in the WebFetch summary and a search excerpt; medium.

**Benchmarks to borrow from, not run.** DeepResearch Bench scores reports with RACE (an LLM judge against a reference report, task-specific criteria) and citations with FACT. FACT extracts statement-URL pairs, scrapes the cited pages and has a judge check support. Its judge moved to GPT-5.5 and GPT-5.4-mini on 11 May 2026, and old and new scores are not comparable. Running it needs an OpenRouter or OpenAI key, a Jina key and 100 full reports (https://github.com/Ayanami0730/deep_research_bench). DeepResearch Bench II (paper Jan 2026, evaluator updated Aug 2026) uses 132 tasks and about 9,430 binary rubrics scored 1/0/-1, with a GPT-5.5 judge and public `tasks_and_rubrics.jsonl` (https://github.com/imlrz/DeepResearch-Bench-II). BrowseComp (16 Apr 2025, 1,266 questions) scores short answers only (https://arxiv.org/abs/2504.12516). The worker infers that the plugin should borrow two designs: binary rubrics as grader text, and a deterministic FACT-style check that every cited line carries a URL listed in the note's opened log. The latter needs a sampled `llm` support check only (inference).

**The evaluation design** (worker synthesis; files named in Implications rank 9):
1. **Separate the exam from the improver.** Today self-test "never edits the plugin to raise the score" (plugin/skills/self-test/SKILL.md:1-15). Keep it as the per-release exam with the no-plugin baseline, and put the loop in a new `plugin/skills/self-improve/SKILL.md`. The two notes name this file differently (`self-improve` and `skill-improve`); this file uses `self-improve`.
2. **Use three tagged splits under `plugin/evals/`.** `dev`: the proposer reads transcripts and failures. `holdout`: the proposer sees only aggregate pass/fail, never prompts, graders or transcripts, and the split is scored once per round. `regression`: graduated cases, which must stay near 1.0. Keep a reserve of 3 to 4 cases that are never used. After each accepted round, rotate holdout cases whose failures were reported to the proposer into dev, and add new cases built from real run failures. Record provenance and the round each case was last used in `plugin/evals/README.md`.
3. **Freeze what scores the round.** Pin `--judge-model`. Reject any round whose diff touches a grader, mock or case file. Add a PreToolUse hook in `plugin/hooks/hooks.json` that denies edits to `plugin/evals/holdout/` and to graders while a round runs. Prefer `regex`, `tool_used`, `tool_order` and `file_exists` graders, and calibrate the single `llm` rubric once against 5 to 10 human-labelled outputs.
4. **Report per dimension.** Score citation present, claim supported, contradiction surfaced and parked-not-guessed separately, never as one scalar (2610.12601).
5. **Set runs and baseline.** Screen at 3 runs. Decide at 5 runs on holdout and regression, in a paired comparison against the previous accepted version with `--ablation none` to halve cost. Keep the no-plugin arm for the release exam.
6. **Accept a round only if all of the following hold:**
   - `claude plugin validate --strict` and the deterministic fast cases pass first. This mirrors DGM's staged 10-task gate before its 50-task evaluation (https://arxiv.org/pdf/2505.22954v3).
   - Regression drops by no more than one case.
   - Holdout beats the previous accepted version by a pre-registered margin: 0.2 on the 8-case scale, recomputed if the case count changes.
   - No per-dimension score regresses.
   - No grader, mock or case file changed.
   - A human reads the diff and two transcripts.
7. **Stop at the first of:**
   - a hard cap of 3 rounds (a worker choice; skill-creator caps description optimisation at 5, DGM ran a fixed 80);
   - two rejected rounds in a row;
   - holdout improving by less than the margin;
   - dev rising while holdout is flat or falling, which signals overfit;
   - regression saturated with no new real-failure case available.

**Contradictions.** agentskills.io stops on human judgment ("when you're satisfied… feedback is consistently empty, or you're no longer seeing meaningful improvement"; https://agentskills.io/skill-creation/evaluating-skills). DGM stops at a fixed iteration count with no quality test (https://arxiv.org/pdf/2505.22954v3). These are different rules rather than conflicting facts. The evidence favours using both: a hard cap so the loop ends, and quality-based early stops so it does not run its full budget against a noisy judge. A smaller issue: the DeepResearch Bench repo shows Apache-2.0 in its sidebar and MIT in its README badge (https://github.com/Ayanami0730/deep_research_bench). This is unresolved but not material, since the plugin reuses only the design.

No self-improving-agent source the workers opened uses a significance test inside its loop. The worker notes that the absence is not proven.

## Evidence

Web sources (all opened 2026-10-16):
- https://github.com/Ayanami0730/deep_research_bench — WebFetch. RACE and FACT method; judge moved to GPT-5.5/GPT-5.4-mini on 11 May 2026 with non-comparable scores; OpenRouter/OpenAI and Jina keys needed; 100 public queries; license shown as Apache-2.0 (sidebar) and MIT (badge).
- https://github.com/imlrz/DeepResearch-Bench-II — WebFetch. 132 tasks, about 9,430 binary rubrics (1/0/-1), GPT-5.5 judge, Apache-2.0 code, mostly CC BY 4.0 data; paper Jan 2026, evaluator updated Aug 2026.
- https://arxiv.org/abs/2504.12516 — WebFetch. BrowseComp, 16 Apr 2025: 1,266 short-answer questions measuring persistent browsing.
- https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents — WebFetch. Jan 2026: 20-50 tasks from real failures; multiple trials; pass@k/pass^k; saturation; judge calibration; bypass-resistant graders; groundedness and coverage checks; capability evals graduating to regression (summary plus excerpt, medium); no held-out-set discussion.
- https://arxiv.org/abs/2610.12601 — WebFetch (abstract). 8 Oct 2026: topic-disjoint split; held-out +0.079 [0.051, 0.107]; validation-minus-held-out gap from small-sample selection under a noisy judge; scalar feedback transferred negatively.
- https://arxiv.org/abs/2602.07150 — WebFetch. Feb 2026 (v3 25 Mar 2026): single-run variance of 2.2 to 6.0 points; SD above 1.5 at temperature 0; 2-3 point gains may be noise.
- https://code.claude.com/docs/en/plugin-evals — WebFetch and Parallel fetch, undated. 3 runs default; `--threshold`, `--judge-model`, `--max-cost-usd`, `--ablation none`; free and paid grader types; regex for long text; suspect the judge; exclude partial runs; pin models.
- https://code.claude.com/docs/en/skills — WebFetch, undated (last 9,478 characters unread). skill-creator with/without benchmark and blind A/B; nothing on runs per eval, variance or a held-out split.
- https://arxiv.org/pdf/2505.22954v3 — curl + pdftotext. DGM, v3 12 Mar 2026: 80 iterations; staged 10-task then 50-task evaluation; cross-benchmark held-out transfer; objective-hacking example.
- https://agentskills.io/skill-creation/evaluating-skills — WebFetch, undated. Iteration loop; previous-version baseline; human-judgment stop; remove always-pass assertions; generalise; stddev needs multiple runs; start with 2-3 cases.
- https://arxiv.org/html/2502.05167v3 — WebFetch. NoLiMa, v3 9 Jul 2025: 11 of 13 models under 50% of baseline at 32K; Claude 3.5 Sonnet effective length 4K.
- https://aclanthology.org/2025.findings-emnlp.1264/ — WebFetch. Nov 2025: 13.9% to 85% drops with perfect retrieval; reciting evidence first gives up to +4%.
- https://arxiv.org/html/2605.23170 — WebFetch. 22 May 2026: mid-context drops up to 94 points; three of four newer releases within 6 points under one filler, 16 to 56 point drops under another.
- https://www.anthropic.com/engineering/harness-design-long-running-apps — WebFetch. 24 Mar 2026: Sonnet 4.5 context anxiety; "compaction alone wasn't sufficient"; Opus 4.5 removed it; file-based handoff between agents.
- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices — WebFetch, undated. Context awareness on Sonnet 5, Sonnet 4.6 and Haiku 4.5; tell the model it will be compacted; a fresh window that rediscovers state from progress files, a structured test list and git log.
- https://code.claude.com/docs/en/sub-agents — WebFetch, undated (last 10,964 characters unread). Per-agent `memory:` (200 lines/25KB); subagents auto-compact; `maxTurns` partial output resumable via SendMessage; the report scan "never removes or rewords anything"; silent on SessionStart in subagents.
- https://arxiv.org/html/2607.28802v1 — WebFetch (first 100,000 of 229,295 characters). 30 Jul 2026: definitions of Context Rationale Erosion, Delegation Failure and Communication Failure; descriptive, no fixes.
- https://arxiv.org/html/2509.04499 (and /abs/2509.04499) — WebFetch. DeepTRACE, 2 Sep 2025: per-system unsupported and citation-accuracy rates; judge r=0.62; Gemini DR 50.3% vs 40.3% discrepancy.
- https://arxiv.org/html/2605.06635v1 — WebFetch. May 2026: unsupported-citation rates for 14 models; dead links 0-6%; more tool calls raise unsupported rates; recommends ensemble or hybrid judges.
- https://arxiv.org/html/2509.00761v4 — WebFetch. L-MARS (arXiv 2509): unsupported 36-54%; judge loop citation F1 0.131 to 0.254; human-verifier kappa 0.458/0.219; reachability disagreement; stratified audit samples.
- https://arxiv.org/html/2608.24306v1 — WebFetch (first 100,000 of 156,000 characters). AI-Q study (arXiv id 2608): raw snippets raise precision 87.6 to 94.1 and recall 64.5 to 69.7; citation-only instruction gives 91.0/69.6; orchestrator causes 52.6-100% of final-report errors; stage error rates.
- https://platform.claude.com/docs/en/build-with-claude/citations — WebFetch, undated. Valid-pointer guarantee; `cited_text` not billed as output; qualitative "significantly more likely to cite the most relevant quotes"; cannot be combined with structured outputs.
- https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations — WebFetch, undated. Quote-first for documents over 20k tokens; retract any claim without a supporting quote; no effect sizes.
- https://dspy.ai/api/optimizers/MIPROv2/ — Parallel fetch, undated. Bootstrap demos, proposed instructions, Bayesian search, minibatch and full evaluation.
- https://dspy.ai/api/optimizers/GEPA/overview/index.md — Parallel fetch, undated. Pareto sampling, minibatch then validation gate, budget settings, reflection LM required, custom proposer, smallest-sufficient valset guidance, `skip_perfect_score`.
- https://arxiv.org/pdf/2507.19457 — Parallel fetch. GEPA paper, v2 14 Feb 2026: +6% over GRPO with up to 35x fewer rollouts; over 10% better than MIPROv2; minibatch-first acceptance; Pareto versus best-only ablation; under $500 for the suite.
- https://github.com/gepa-ai/gepa/blob/main/docs/docs/blog/posts/2026-02-18-automatically-learning-skills-for-coding-agents/index.md — Parallel fetch. 18 Feb 2026: `optimize_anything` learning coding-agent skills on 200/50/60 train/validation/test tasks; transferred to Claude Code.
- https://github.com/zou-group/textgrad — Parallel fetch. Textual-gradient API; needs an OpenAI or Anthropic key; Nature 2025.
- https://www.promptfoo.dev/docs/usage/prompt-optimization/ — Parallel fetch. Updated 13 Oct 2026: `optimize` uses observed failures and prior scores; `--validation-split`; warns that full-set search "can overfit".
- https://github.com/anthropics/skills (skills/skill-creator, HEAD 2026-10-09) — git clone, read with sed and grep. `improve_description.py` uses session auth via `claude -p` (lines 103-170: previous attempts, no query lists, length cap); SKILL.md:165-262 benchmark loop, :298-306 edit guidance, :308-322 iteration and stop rule, :313 baseline, :325-330 and :434 blind A/B optional, :386-394 description loop; `scripts/run_loop.py`:79-234 60/40 split, 5 iterations, best by test score; `agents/comparator.md`:1-85; `agents/analyzer.md`:~218-256 flaky and non-discriminating assertions.

Local repo files (per the PLAN.md Synthesis ruling; all read 2026-10-16):
- docs/self-test/2026-10-16-v0.1.md:7-8, 23-29, 31-38 — Read. Score 0.97, delta 0.76, one run per case; fixed grader not re-run; stated limits.
- plugin/evals/results/2026-10-16T02-20-47-488Z/aggregate-result.json — Bash `jq`. Baseline passes on one-fact-inline, injection-resist `no-pwned-file`, system-map-diagrams `two-mmd-files` and cite-or-park `reply-says-gap`; `content-calls` unscored; a `costUsd` key whose value was not read.
- plugin/evals/cite-or-park/graders/reply-says-gap.md:5-7; plugin/evals/one-fact-inline/graders/cites-url.md:3-5, content-calls.md:5-9; plugin/evals/cite-or-park/prompt.md:10; plugin/evals/contradiction/prompt.md:10; plugin/evals/scorecard-lookup/graders/score.md:5-6; plugin/evals/interview-ears/prompt.md:10-14 — Read. Weak or vacuous graders; single-facet prompts; the interview prompt answers every question up front.
- plugin/skills/self-test/SKILL.md:1-15, 127-138 — Read. The exam never edits the plugin; case list; no grader for Verification, INDEX or PLAN (with a Grep over plugin/evals/*/graders).
- plugin/agents/researcher.md:6, 8, 9, 46, 47-48, 64-65, 67-68, 87 — Read. maxTurns 40; tools; no Agent tool; never `full_content`; 10-15 call stop; fetch fallback chain; clone-path citation; 10-line return.
- plugin/agents/synthesizer.md:24-26, 42-45, 65-66, 68, 79-80 — Read. URL-only drop rule; spike exemption; registry writes; 12-line return; Gaps-versus-Open-questions wording.
- plugin/agents/verifier.md:4, 6, 17-18, 23-24, 38-40, 42 — Read. Haiku; tool list; sample rule; "page did not open"; does not write INDEX status; 5-line return.
- plugin/agents/spike-worker.md:42-45 — Read. One Bash call for create, install, probe and cleanup.
- plugin/skills/research/note-schema.md:10-11; plugin/skills/research/routing.md:5, 12-13, 16-17; plugin/skills/research/SKILL.md:13-24, 17, 19-20, 37-38, 73, 77-80, 120, 181, 200-202, 208-209, 210-211 — Read. URL on every finding; routing fallbacks; worker cap; never open a note; connector probe; 25,000-character rule; Gaps wording.
- plugin/skills/tool-scan/SKILL.md:13-14, 18-20, 34-47; plugin/skills/repo-triage/SKILL.md:24-26, 46-47; plugin/skills/spike/SKILL.md:55, 67-68; plugin/skills/system-map/SKILL.md:50-51 — Read. Registry writers; candidate budget; triage workers; no Mermaid tool.
- plugin/hooks/session-start.sh:14 and plugin/hooks/hooks.json; plugin/agents/*.md frontmatter; CLAUDE.md — Read and Bash. `head -n 30` of INDEX.md; only a SessionStart hook; agent models, efforts and maxTurns; Compact instructions section.
- research/findings/INDEX.md:1-15; research/findings/*.md (`grep -c "## Verification"`, `wc -l`); research/open-questions.md:10-22; .claude/skills/research/findings-format.md:18; `git log --oneline` — Read and Bash. All findings unverified; file lengths; open design questions; no Gaps section; 19 commits in one day.

## Implications for the researcher plugin

Changes ranked by expected effect on research quality and context rot. Ranks 1 to 3 act on every research run's citations. Ranks 4 to 6 act on every long run's state. Rank 7 removes misrouting. Rank 8 must land before rank 9, because a loop scored by an exam that cannot see the pipeline tail would optimise the wrong thing.

| Rank | Change | Plugin file(s) | Evidence | Confidence |
| --- | --- | --- | --- | --- |
| 1 | **Make the verifier able to verify, then run it.** Add Firecrawl and a read-only clone-and-grep path. Fix the cap at 20 pairs with a priority order: numbers, dates, names, quotes, single-source and summary claims, then random. Re-fetch every page itself. Judge each claim against the verbatim quote and the page; unreachable or uncertain counts as fail. On any failure, re-check every claim from that note. Pass the verifier only claim, URL and quote, never the surrounding prose. First targets: tool-routing.md and context-management.md, which back the routing and context rules. | plugin/agents/verifier.md; plugin/skills/research/findings-format.md (section 7 wording) | verifier.md:4, 6, 17-18, 23-24; INDEX.md:11-15; routing.md:5; unsupported rates 12-97% (2509.04499) and 23-76% with dead links 0-6% (2605.06635v1); reachability disagreement and kappa 0.458 (2509.00761v4); errors cluster by stage (2608.24306v1) | high that it is needed; medium on the sample rule (worker thresholds) |
| 2 | **Quote-first citations end to end.** Add a `Quote:` field (one verbatim sentence) to every Cited findings line. The researcher copies the sentence before writing the claim. The synthesizer carries claim, URL and quote verbatim, adds "do not use information not backed by a cited line", adds no number absent from a note, and marks sentences that merge two notes as synthesis citing both. | plugin/skills/research/note-schema.md; plugin/agents/researcher.md; plugin/agents/synthesizer.md | Raw snippets raise precision 87.6 to 94.1; citation-only instruction gives 91.0 (2608.24306v1); orchestrator causes 53-100% of errors (same); Anthropic quote-first and retract guidance (reduce-hallucinations) | medium (quote-first alone unmeasured) |
| 3 | **Make repo and clone citations legal.** Accept `<repo URL> + path:line (commit)` and local `path:line, read <date>, <tool>` as opened sources wherever the URL rule applies. | plugin/agents/synthesizer.md:24-26; plugin/skills/research/note-schema.md:10-11; plugin/agents/researcher.md:67-68 | Internal-audit line pairs; this run needed a lead ruling (PLAN.md) | high |
| 4 | **Re-inject the live run on compaction and keep a run ledger.** On `compact`, print the newest `research/runs/*/PLAN.md` (about 40 lines) and its ledger, and the newest INDEX lines instead of `head -n 30`. After each worker returns, write a ledger line (facet, status, note path, TAKEAWAY copied verbatim). After compaction or `/clear`, read PLAN.md, the ledger and `git log -5`. Offer `/clear` at phase boundaries. | plugin/hooks/session-start.sh; plugin/skills/research/SKILL.md; plugin/skills/using-research-agent/SKILL.md | session-start.sh:14 against INDEX.md:4; mid-context drops (2605.23170, 2502.05167v3); Context Rationale Erosion (2607.28802v1); file handoff (harness-design post); fresh window plus progress files (prompting best practices) | medium |
| 5 | **Worker compaction guard.** Write the note skeleton first. Say "your context may be compacted; do not wrap up early". If a summary replaces your history, re-read the brief and the note before continuing. A worker stopped at maxTurns is resumed or re-dispatched, never silently accepted. | plugin/agents/researcher.md; plugin/agents/spike-worker.md; plugin/skills/research/SKILL.md | Context awareness and wrap-up warning on Sonnet-class models (prompting best practices); Sonnet 4.5 context anxiety (harness-design post); maxTurns partial output resumable (sub-agents page) | medium (cheap, no measured effect) |
| 6 | **Carry constraints verbatim and check for drift.** Every dispatch gets a fixed Constraints block copied from PLAN.md. The verifier string-compares each note's `Brief:` line with the PLAN.md facet brief. | plugin/skills/research/SKILL.md (dispatch template); plugin/agents/researcher.md; plugin/agents/verifier.md | Communication and Delegation Failure definitions (2607.28802v1); researcher.md:87 and note-schema Brief line | low-medium (no measured fix) |
| 7 | **Remove conflicting rules.** Delete routing.md's `full_content` and "in a subagent" fallbacks. Give the 25,000-character rule an actor. Name one registry writer. Limit a tool-scan cluster to one candidate per worker, since more tool calls raised unsupported rates. Count triage workers against the cap of 8. Specify a ToolSearch probe per connector. Use "Open questions" wording everywhere. | plugin/skills/research/routing.md; plugin/skills/research/SKILL.md; plugin/agents/synthesizer.md; plugin/skills/tool-scan/SKILL.md; plugin/skills/repo-triage/SKILL.md; plugin/skills/spike/SKILL.md | Internal-audit line pairs (Q1); 2 to 150 calls raised GPT-5.4 unsupported claims from 21.4% to 83.3% (2605.06635v1) | medium-high |
| 8 | **Give the self-test eyes on the pipeline tail.** Add a multi-facet mock case that grades the Verification section, INDEX line, PLAN.md, worker cap and "lead never Read a note" (`file_exists`, `regex`, `tool_used`, `tool_order`). Add a deterministic FACT-style grader: every cited line's URL appears in the note's opened log. Tighten `reply-says-gap` and `cites-url` so the baseline cannot pass them. Re-run injection-resist. Use 3 runs. | new plugin/evals/<multi-facet-case>/; plugin/evals/cite-or-park/graders/reply-says-gap.md; plugin/evals/one-fact-inline/graders/cites-url.md; plugin/skills/self-test/SKILL.md:127-138 | Q1 audit; groundedness checks and real-failure tasks (Anthropic evals post); FACT design (deep_research_bench); 3-run default (plugin-evals) | high that it is needed |
| 9 | **Capped self-improvement loop**, separate from the exam. Tagged dev, holdout and regression splits with rotation and a reserve. A PreToolUse hook denies edits to holdout and graders during a round. Pinned judge. One edit per round with a hypothesis record. Paired 5-run comparison against the previous accepted version. Per-dimension scores. Acceptance gate and stop rules as in Q5; cap of 3 rounds. | new plugin/skills/self-improve/SKILL.md; plugin/evals/ (tags, README.md provenance); plugin/hooks/hooks.json (PreToolUse); research/self-improvement/changelog.md and rejected.md; optionally plugin/agents/skill-grader.md and skill-comparator.md copied from skill-creator | Q4 and Q5 sources: 2610.12601, 2505.22954v3, 2602.07150, plugin-evals, skill-creator clone, agentskills.io, promptfoo, GEPA | medium (thresholds are worker choices) |

Lower priority: per-agent `memory: project` for researchers (default off; up to 25KB per start; sub-agents page), and a PostToolUse trimming hook (already recommended in context-management.md).

Do not do:
- Add retrieval depth to fix citations, because depth raised unsupported rates (2605.06635v1).
- Rely on the Citations API from subagents (worker inference, unverified).
- Run DeepResearch Bench per round (paid judge key, 100 runs).
- Install GEPA, MIPROv2, TextGrad or promptfoo (each needs a provider key).

Candidate EARS requirements:
- When the verifier cannot reopen a cited page with any fetch tool the researcher used, the verifier shall mark the claim unverified with the reason "page did not open" and shall re-check every other claim from the same note.
- When a self-improvement round's diff changes any file under `plugin/evals/holdout/` or any grader, the round shall be rejected.
- When the holdout score of a round fails to beat the previous accepted version by the pre-registered margin in a paired 5-run comparison, the loop shall reject the round and append it to `research/self-improvement/rejected.md`.
- When the conversation is compacted during a research run, the SessionStart hook shall inject the active run's PLAN.md and ledger.

## Tools evaluated

| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| DeepResearch Bench (RACE/FACT) | https://github.com/Ayanami0730/deep_research_bench | 100-task report-quality (RACE) and citation (FACT) benchmark; judge GPT-5.5 / GPT-5.4-mini since 11 May 2026 | local Python; OpenRouter/OpenAI key plus Jina key | 2026-10-16 | Skip as a per-round gate; reuse the FACT claim-to-URL design as a deterministic grader |
| DeepResearch Bench II | https://github.com/imlrz/DeepResearch-Bench-II | 132 tasks, about 9,430 binary expert rubrics, public `tasks_and_rubrics.jsonl`; judge GPT-5.5 | local Python (uv); paid judge key | 2026-10-16 | Fallback: borrow a few rubrics as grader text; skip the full run |
| BrowseComp | https://arxiv.org/abs/2504.12516 | 1,266 short-answer questions testing persistent browsing | dataset | 2026-10-16 | Skip; measures answers, not reports or citations |
| `claude plugin eval` | https://code.claude.com/docs/en/plugin-evals | Runs cases with/without plugin; free regex/tool_used/tool_order/file_exists graders, paid llm/baseline; `--runs` (default 3), `--threshold`, `--judge-model`, `--ablation none`, `--max-cost-usd` | CLI v2.1.269+, session auth | 2026-10-16 | Adopt for `/self-test`; for improvement rounds add dev/holdout/regression tags, a pinned `--judge-model`, 5 runs for accept decisions, `--ablation none` for version-vs-version |
| agentskills.io skill-eval guide | https://agentskills.io/skill-creation/evaluating-skills | Eval-driven iteration loop; previous-version baseline; assertion pruning; stop rule | docs | 2026-10-16 | Use as the loop template; it has no holdout rule |
| Anthropic skill-creator | https://github.com/anthropics/skills/tree/main/skills/skill-creator | Content loop, grader/comparator/analyzer agents, description optimiser with 60/40 split and 5-iteration cap via `claude -p` | local, session auth, no extra key | 2026-10-16 | Use as template; copy patterns into plugin agents |
| GEPA (DSPy optimizer, optimize_anything) | https://dspy.ai/api/optimizers/GEPA/overview/index.md | Reflective, Pareto-based prompt and text evolution with minibatch-then-validation gating; learned coding-agent skills in a Feb 2026 post | Python; needs a reflection LM | 2026-10-16 | Reference design only; copy the loop, do not install |
| DSPy MIPROv2 | https://dspy.ai/api/optimizers/MIPROv2/ | Bootstrapped demos, proposed instructions, Bayesian search | Python; needs LM key | 2026-10-16 | Skip; many calls, little value for markdown skills |
| TextGrad | https://github.com/zou-group/textgrad | Textual-gradient critique and rewrite, PyTorch-style API | Python; needs OpenAI/Anthropic key | 2026-10-16 | Skip |
| promptfoo optimize | https://www.promptfoo.dev/docs/usage/prompt-optimization/ | Baseline eval, LLM-proposed rewrites from failures, optional `--validation-split` | Node CLI; needs provider credential | 2026-10-16 | Fallback; built for prompt/provider pairs, not markdown skills |

## Open questions

- **Current-model context rot.** No measurement of quality against context length exists for Claude 4.5+/5.x. NoLiMa and the EMNLP paper conflict with the Context Rot Evaluation on newer models (Q3). A Claude-specific needle-plus-reasoning run at 32K, 128K and 500K would settle it.
- **Hook behaviour.** Whether a `compact` SessionStart hook fires inside a subagent that auto-compacts is undocumented.
- **Runs per case.** No opened source gives a number for LLM-judged research reports. The SWE-bench power figures (about 9 runs for a 2% effect) came from a search excerpt only and are excluded.
- **Effect sizes.** None was found for quote-first extraction alone, or for the Citations API against prompting beyond the vendor's qualitative statement.
- **Verifier model.** Whether Haiku is an adequate claim-support judge is untested. DRB II judge-human agreement is unverified because its paper was not opened.
- **Unresolved discrepancies.** DeepTRACE gives Gemini DR citation accuracy as 50.3% (Table 1) and 40.3% (text). The DeepResearch Bench license shows as Apache-2.0 and MIT.
- **Acceptance thresholds.** No source gives a minimum effect size or significance test for prompt edits. The 0.2 margin, 3-round cap and 20%/minimum-5 sample are worker choices. Skill-creator's only floor on held-out size is `max(1, …)` per class.
- **Grader gaming.** Whether self-edited prompts game LLM-judge graders was not studied; DGM's gamed detector is the only example.
- **Never observed.** The verifier has not run on real content. Per-run eval traces and HTML reports were not read, so how the lead behaved inside passing cases is unknown. The `costUsd` value in aggregate-result.json was not read, so the self-test's real cost (research/open-questions.md:16) stays open.
- **Free tiers.** Whether `claude plugin eval` consumes a free plan's usage, and whether GEPA or DSPy can run on any free hosted LM, is untested.
- **Unchecked in practice.** Whether agent `tools` allow-lists with `mcp__plugin_research-agent_*` names work live, whether `maxTurns` maps to tool calls, and how often the lead misroutes a one-fact question into a multi-facet run.
- **Excluded: seen only as search excerpts, never opened.**
  - DeepResearch Bench paper details (22 fields, 50/50 language split) and the RACE judge's 68.78% human agreement.
  - BrowseComp-Plus.
  - The GEPA paper's "test split… inaccessible" quote (html/2507.19457).
  - arXiv 2606.11045 (38 of 102 checkpoints overfit).
  - arXiv 2602.07150's 9-run and 36-run power figures.
  - arXiv 2411.00640 (paired differences, power analysis).
  - Anthropic's CORE-Bench 42% to 95% example.
  - The plugin-eval "currently unavailable" message.
  - Huxley-Gödel Machine; SICA, ADAS and Gödel Agent acceptance rules.
  - evalstats, errorbars and abeval.
  - MARCH's verifier confirmation bias.
  - arXiv 2606.07937 (hallucination attenuating across a 3-agent chain). This would contradict the finding that later stages introduce errors, if opened.
  - promptfoo `llm-rubric` judge defaults and the `optimize` iteration cap.
  - The daymade skill-creator fork's revert menu.
  - The claude.com skill-creator listing (four modes, an "Executor" agent absent from the repo clone).
  - MAST failure-mode frequencies.
- **Excluded: build report.** These claims rest only on the build report at /mnt/project-files/research-agent/2026-10-16-build-report.md, which is outside the repo, so the Synthesis ruling for repo files does not cover it. The lead may rule to admit them.
  - Decision 2: the researcher keeps Bash, with only prompt rules against injection.
  - Decision 9: terse registry rows.
  - Decision 22: double counting.
  - "Haiku may ignore the effort setting".
  - Vaguer tool-scan clone wording.
  - Text-presence checks and the frontmatter parser test not in CI.
  - Setup status not injected at session start.
  - The cosmetic deferred items.
  - "What you decide next".
  - The scorecard "/10" grader being a known fragility.
  - The spike isolated environment wrapping only one command.
- **Excluded: session observations with no opened page.** Parallel Search hitting its free-tier rate limit after two or three calls, and WebFetch needing offset paging on large pages.
- **Also unsettled.** No minimum size is known for a meaningful holdout. No source measures "citation laundering" through aggregator pages. Setup's seven-tool probe was not compared line by line with the research skill's two-tool probe.

## Verification
Checked 2026-10-16 by the verifier. Sample: 20 statement-URL pairs.
Verified: 19. Unverified: 1.
- Unverified: "Dead links account for only 0% to 6%" and the per-model "23.2% to 75.6%" unsupported-citation rates (the Opus 4.5 to OSS-120B list in Q2) — https://arxiv.org/html/2605.06635v1 — The page reports Fact Check accuracy (76.8% for Opus 4.5, 24.4% for OSS-120B), so the unsupported percentages are complements the page never states. The page never states a 0% to 6% dead-link figure; its Link Works metric (94.1% to 100% for frontier models) also counts blocked access and timeouts, not only dead links.

Notes (not counted as failures): the summary's "53% to 100%" for orchestrator or merge-stage errors is a rounding of 52.6% in https://arxiv.org/html/2608.24306v1 (Section 6.2). The GPT-5.4 21.4% to 83.3% pair is a complement of Table 2's Fact Check scores (78.6% to 16.7%) and was counted as verified. DeepTRACE Table 1 vs. text (50.3% vs 40.3% for Gemini) is already flagged in the body.
