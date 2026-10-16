# Mechanisms for proposing and accepting prompt/skill changes

Brief: Find the mechanisms that exist for an agent system to propose, test and accept changes to its own prompts and skills, and which could be adopted by a Claude Code plugin made of markdown skills and agents.
Run: research/runs/research-agent-self-improvement/PLAN.md

Note: the Parallel web_fetch tool is called "Parallel fetch" below. Dates are page dates where the page showed one; otherwise "undated". Recommended plugin paths are proposals (Inferences), not existing files.

## What do the optimizers (DSPy MIPROv2 and GEPA, TextGrad, promptfoo, 2025-26 reflective evolution) do: inputs, candidate generation, keep rule?

### Takeaway
All of them share one shape: a dataset or task set, a metric (scalar, sometimes with text feedback), an LLM that proposes rewritten text, and a rule that keeps a candidate only if it scores better, usually on data separate from the data that drove the edit. They differ in how the proposer is conditioned (summaries and tips in MIPROv2, rollout traces and feedback in GEPA, critique "gradients" in TextGrad, observed failures and prior scores in promptfoo) and in selection (Bayesian search, Pareto frontier, best-so-far). Confidence: high.

### Cited findings
- MIPROv2 optimizes instructions and few-shot demos jointly: (1) bootstrap demo candidates by keeping those the program gets right, (2) propose instructions from a dataset summary, a program summary, the demos and a random "tip", (3) Bayesian optimization over combinations across `num_trials`, scoring on a minibatch and fully evaluating the best set every `minibatch_full_eval_steps`; returns the program best on the full validation set — https://dspy.ai/api/optimizers/MIPROv2/, opened 2026-10-16, Parallel fetch (page undated)
- GEPA loop: sample a candidate from the Pareto frontier, sample a minibatch (default 3), collect traces and feedback, pick a module, have a reflection LM propose a new instruction, roll it out on the minibatch, "if improved, evaluate on Pareto validation set", update the pool, optional merge, stop when budget is exhausted, return best on validation — https://dspy.ai/api/optimizers/GEPA/overview/index.md, opened 2026-10-16, Parallel fetch (undated)
- GEPA requires `reflection_lm` (or a custom `instruction_proposer`) and exactly one budget setting among `auto` (light/medium/heavy), `max_full_evals`, `max_metric_calls` — same URL, opened 2026-10-16, Parallel fetch
- GEPA paper (ICLR 2026 oral, v2 dated 2026-02-14): beats GRPO by 6% on average using up to 35x fewer rollouts, and beats MIPROv2 by over 10%; acceptance is minibatch-first, then a full Pareto-set check; a "best candidate only" ablation (similar to TextGrad's strategy) is compared against Pareto selection; whole experiment suite costs under $500 with GPT-4.1 mini — https://arxiv.org/pdf/2507.19457, opened 2026-10-16, Parallel fetch
- GEPA's `optimize_anything` generalizes to any text artifact; a Feb 2026 GEPA blog (gskill) uses it to learn skills for coding agents from ~200 train / ~50 validation / ~60 test tasks, with a stronger LLM reflecting on evaluation results, repeated "until convergence"; learned skills were transferred to Claude Code (Haiku 4.5, Sonnet 4.5) — https://github.com/gepa-ai/gepa/blob/main/docs/docs/blog/posts/2026-02-18-automatically-learning-skills-for-coding-agents/index.md, opened 2026-10-16, Parallel fetch (post dated 2026-02-18)
- TextGrad: PyTorch-style API where an LLM critique ("textual gradient") of a `Variable` (answer or system prompt) is back-propagated and `TGD.step()` rewrites it; needs a backward-engine LLM; its tutorials say an OpenAI/Anthropic key is needed; published in Nature 2025 — https://github.com/zou-group/textgrad, opened 2026-10-16, Parallel fetch
- promptfoo (page last updated 2026-10-13): `promptfoo optimize` runs a baseline eval, asks an optimizer model for revised prompts "using observed failures and prior scores", evaluates them, and prints the strongest; one prompt/provider pair per run — https://www.promptfoo.dev/docs/usage/prompt-optimization/, opened 2026-10-16, Parallel fetch
- promptfoo's default judge for `llm-rubric` picks a provider from whichever credential exists (OpenAI, Anthropic, Google AI Studio, etc.), and `llm-rubric` supports a minimum `threshold` score — https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/llm-rubric/ (snippet only; page not opened, so not relied on; see Gaps)

### Contradictions
- None found.

### Inferences
- Inference: the transferable core is GEPA's loop reduced to markdown: pick a failing case, read the trace, write one targeted edit with a stated hypothesis, test on the failing case first (minibatch), then on all cases (validation), keep only if it does not regress. Rests on the GEPA overview and paper findings above.
- Inference: MIPROv2 (Bayesian search over many candidates) and TextGrad (per-step critique with no frontier) need many LLM calls and a metric function; they add little over a manual single-edit loop for a plugin with a handful of skills.

### Gaps
- Exact promptfoo `optimize` iteration cap and candidate count per round: the page opened does not state them; the CLI reference (https://www.promptfoo.dev/docs/usage/command-line/) was not opened.
- The GEPA paper's per-iteration reflection meta-prompt wording was visible only as a fragment; not quoted.

## Can any of them run on markdown skills or agent prompts without an API key beyond a free tier? What is the lightweight manual equivalent?

### Takeaway
DSPy GEPA/MIPROv2, TextGrad and promptfoo all call an external LLM that you must configure; I found no source showing a free tier suffices, and GEPA's docs recommend a strong reflection model. The one mechanism that runs on markdown skills with no extra key is Anthropic's skill-creator scripts, which shell out to `claude -p` with the session's own auth, plus the Claude Code `claude plugin eval` command. The manual equivalent is a failure-trace-driven edit with a recorded hypothesis. Confidence: medium (the free-tier question for external providers is unsettled).

### Cited findings
- skill-creator's `improve_description.py` calls `claude -p` as a subprocess, "same auth pattern as run_eval.py — uses the session's Claude Code auth, no separate ANTHROPIC_API_KEY needed" — cloned file /tmp/tmp.lGRKOZligk/skills/skills/skill-creator/scripts/improve_description.py from https://github.com/anthropics/skills (HEAD commit dated 2026-10-09), read 2026-10-16, git clone + sed/grep
- `claude plugin eval` runs a plugin's eval cases with and without the plugin; graders `regex`, `tool_used`, `tool_order`, `file_exists` are computed from transcript and files at no cost; `llm` and `baseline` graders call a judge model; `--max-cost-usd` caps spend; `--ablation none` halves cost; `--runs` defaults to 3; exit code 1 when a case scores below `--threshold` — https://code.claude.com/docs/en/plugin-evals, opened 2026-10-16, Parallel fetch (undated)
- GEPA's reflection needs a configured LM: the constructor asserts a reflection LM or custom proposer is given — https://dspy.ai/api/optimizers/GEPA/overview/index.md, opened 2026-10-16, Parallel fetch
- GEPA can be given a custom `instruction_proposer` — same URL (so in principle the proposer can be something other than a paid API model; I did not verify any free-tier model works)
- skill-creator's improve step is explicitly a human-in-the-loop edit cycle: apply improvements, rerun all cases in a new `iteration-<N+1>/` directory with baseline, launch reviewer, read feedback, repeat — /tmp/tmp.lGRKOZligk/skills/skills/skill-creator/SKILL.md lines 308-322, https://github.com/anthropics/skills, read 2026-10-16, git clone
- skill-creator guidance for edits: generalize from feedback rather than "fiddly overfitty changes"; keep the prompt lean; explain the why instead of ALWAYS/NEVER; look for repeated helper scripts across test transcripts and bundle them — SKILL.md lines 298-306, same clone

### Contradictions
- None found.

### Inferences
- Inference: the lightweight manual equivalent is a "failure-trace edit record": for each change write (a) the failing case and the trace excerpt, (b) a one-sentence hypothesis, (c) the single edit, (d) the before/after result on the failing case and on all other cases, (e) accept or reject. This is GEPA steps 3-9 done by Claude itself, and the skill-creator guidance above (generalize, explain why, read transcripts) is its proposer prompt.
- Inference (proposed files): a new `plugin/skills/skill-improve/SKILL.md` holding the loop above; the record kept as `research/self-improvement/changelog.md` (accepted) and `research/self-improvement/rejected.md` (rejected, with the hypothesis); `plugin/skills/self-test/SKILL.md` calls `claude plugin eval` for the with/without-plugin check. Rests on the plugin-evals and skill-creator findings.
- Inference: the skill-creator repo is a template, not a dependency: copy its patterns (iteration directories, grader/comparator agent prompts, `history` passed to the proposer) into plugin-owned markdown agents, e.g. `plugin/agents/skill-grader.md` and `plugin/agents/skill-comparator.md`.

### Gaps
- Whether any DSPy/GEPA run is feasible on a free-tier hosted LM (rate limits, quality) — no source opened; untested.
- Whether `claude plugin eval` consumes plan usage on a free Claude plan: docs opened give list-price cost estimates only.

## How does Anthropic's skill-creator iterate on a skill (benchmark loop, description optimization, blind A/B)?

### Takeaway
Three separate loops. (1) Content loop: draft, run each test prompt with the skill and a baseline, grade assertions, aggregate to `benchmark.json` (pass rate, time, tokens, mean +/- stddev, delta), human reviews outputs in a viewer, revise, rerun in a new iteration directory until the user is happy, feedback is empty, or progress stalls. (2) Description loop: automated, 60/40 train/held-out split, up to 5 iterations, best chosen by held-out score. (3) Blind comparison: optional, an independent agent scores two outputs without knowing which skill made which. Confidence: high (read from the repo source).

### Cited findings
- Benchmark loop: spawn a grader subagent per run reading `agents/grader.md`, write `grading.json` with fields `text`, `passed`, `evidence`; prefer scripts for programmatically checkable assertions; run `scripts.aggregate_benchmark` to produce `benchmark.json`/`benchmark.md` with pass_rate, time, tokens, mean +/- stddev and delta; do an "analyst pass" for non-discriminating assertions, high-variance evals and time/token tradeoffs; launch viewer with `--previous-workspace` on iteration 2+ — SKILL.md lines ~165-262 (grep'd lines 167-245), https://github.com/anthropics/skills, cloned 2026-10-16 (repo HEAD 2026-10-09)
- Stop rule for the content loop: "Keep going until: the user says they're happy; the feedback is all empty; you're not making meaningful progress" — SKILL.md lines 316-322, same clone
- Baseline: for a new skill the baseline is always `without_skill`; for an existing skill use the original or previous iteration — SKILL.md line 313, same clone
- Description optimization: `run_loop.py` splits the eval set 60% train / 40% held-out (stratified by should_trigger), runs each query 3 times, has Claude propose a new description from failures, re-evaluates on train and test, up to 5 iterations (`--max-iterations 5`); exits on `all_passed` or `max_iterations`; returns `best_description` chosen by test score, "rather than train score to avoid overfitting" — SKILL.md lines 386-394 and scripts/run_loop.py lines 79-234, same clone
- Description proposer safeguards: prompt includes "PREVIOUS ATTEMPTS (do NOT repeat these — try something structurally different)", forbids growing a list of specific queries, caps at about 100-200 words and a hard 1024-character limit with a rewrite-shorter retry — scripts/improve_description.py lines 103-170, same clone
- Blind A/B: comparator receives output_a/output_b paths, eval prompt and optional expectations, "do NOT try to infer which skill produced which output"; scores 1-5 on a content rubric and a structure rubric, winner by overall rubric score, TIE only if truly equal; analyzer then explains why the winner won — agents/comparator.md lines 1-85 and SKILL.md lines 325-330, same clone
- SKILL.md says blind comparison "is optional, requires subagents, and most users won't need it. The human review loop is usually sufficient." and, in the Cowork variant, "Blind comparison: Requires subagents. Skip it." — SKILL.md lines ~327-330 and 434, same clone
- Another SKILL.md variant (daymade fork) adds an explicit end-of-round menu: continue, accept, "Revert to previous iteration — this round made things worse", or run blind comparison — https://github.com/daymade/claude-code-skills/blob/main/skill-creator/SKILL.md (search excerpt only; page not opened; see Gaps)
- Official plugin page describes four modes (Create, Eval, Improve, Benchmark) and four agents (Executor, Grader, Comparator, Analyzer) — https://claude.com/plugins/skill-creator (search excerpt only; page not opened; the repo files above confirm grader, comparator, analyzer)

### Contradictions
- The claude.com plugin listing (excerpt) describes an "Executor" agent; the anthropics/skills clone has only `agents/analyzer.md`, `comparator.md`, `grader.md`. Not settled; probably a different packaging of the same skill (plugin vs skills repo). Opening the plugin repo `anthropics/claude-plugins-official` would settle it.

### Inferences
- Inference: for a markdown plugin, the adoptable parts are: iteration directories with a fixed baseline, a grader agent that writes evidence per assertion, a rule that the "best" version is chosen on held-out cases, and a proposer prompt that includes prior failed attempts. Proposed files: `plugin/agents/skill-grader.md`, `plugin/agents/skill-comparator.md`, and the loop in `plugin/skills/skill-improve/SKILL.md`.
- Inference: do not copy the human-review viewer step as mandatory in autonomous runs; use it as the acceptance gate instead (see next section).

### Gaps
- `claude-plugins-official` skill-creator and `claude.com/plugins/skill-creator` not opened (snippets only).
- Whether description-optimization held-out sets are large enough for meaningful scores: skill-creator says nothing about minimum size; `max(1, ...)` per class in the split code is the only floor seen.

## What safeguards do these systems use against degenerate edits?

### Takeaway
Seen in sources: a hard round or budget cap (skill-creator 5 iterations, GEPA budgets, promptfoo's held-out adoption), held-out validation for selection, minibatch-then-full-eval gating, Pareto frontier to avoid local optima, history of previous attempts shown to the proposer, length caps, and human review with revert. Not found in any source: a rollback automation beyond "choose best iteration", a minimum effect size, or a persisted rejected-changes log; those would be plugin-side additions. Confidence: medium-high.

### Cited findings
- Round cap: `--max-iterations 5` with exit reasons `all_passed` / `max_iterations` — scripts/run_loop.py and SKILL.md lines 386-394, https://github.com/anthropics/skills, cloned 2026-10-16
- Rollback by selection: final answer is `max(history, key=test_passed)`, i.e. the best iteration, not the last — scripts/run_loop.py lines 216-234, same clone
- Held-out selection: promptfoo `--validation-split` (0 < x <= 0.5) judges candidate adoption on held-out tests and warns that the default full-set search "can overfit to the configured tests" — https://www.promptfoo.dev/docs/usage/prompt-optimization/ (updated 2026-10-13), opened 2026-10-16, Parallel fetch
- GEPA gates: minibatch improvement required before the full validation evaluation; budget caps (`max_full_evals`, `max_metric_calls`); `skip_perfect_score` skips already-perfect examples; custom `instruction_proposer` can enforce `max_chars` and raises on oversize instead of truncating; `max_reflection_cost` is not supported in DSPy yet and raises rather than being silently ignored — https://dspy.ai/api/optimizers/GEPA/overview/index.md, opened 2026-10-16, Parallel fetch
- GEPA validation set guidance: "provide the smallest valset that is just large enough to match your downstream task distribution, while providing as large trainset as possible" — same URL
- GEPA keeps a Pareto frontier (candidates best on at least one instance) rather than only the global best, to avoid stagnation; ablation compares against best-only selection — https://dspy.ai/api/optimizers/GEPA/overview/index.md and https://arxiv.org/pdf/2507.19457, opened 2026-10-16, Parallel fetch
- Plugin-eval safeguards: `Δ` against a no-plugin baseline ("If a case scores 1.0 both with and without the plugin, the plugin isn't what made it pass"), `--max-cost-usd` ceiling, partial runs flagged `partial: true` and excluded from trends, pin model so a model rollout is not mistaken for a regression, CI exit code on `--threshold` — https://code.claude.com/docs/en/plugin-evals, opened 2026-10-16, Parallel fetch
- Analyzer flags non-discriminating assertions and high-variance (flaky) evals so noise is not treated as signal — agents/analyzer.md lines ~218-256 and SKILL.md "analyst pass", https://github.com/anthropics/skills, cloned 2026-10-16
- Proposer-side anti-overfit instructions: no ever-expanding list of the specific failing queries; "ALWAYS/NEVER in all caps is a yellow flag" — scripts/improve_description.py line 127, SKILL.md line 302, same clone
- Plugin-eval docs recommend pinning models and using `--runs` (default 3) per case per arm, which is the only variance control documented — https://code.claude.com/docs/en/plugin-evals, opened 2026-10-16, Parallel fetch

### Contradictions
- None found.

### Inferences
- Inference (proposed acceptance rule, to be written into `plugin/skills/skill-improve/SKILL.md`): cap at 3 edit rounds per session; one edit per round; accept only if the target case improves by a stated margin (e.g. 2 of 3 runs flip), no previously passing case regresses, and the edit does not grow the file past a stated size; otherwise revert and append to `research/self-improvement/rejected.md` with the hypothesis. The margin and caps are my choice; no source gives a standard minimum effect size.
- Inference: human-review gate: write each accepted change as a git commit (or a diff block in `research/self-improvement/changelog.md`) on a branch, never auto-merge to the main branch; mirrors skill-creator's "Revert to previous iteration" option and the GEPA-blog practice of testing on held-out tasks before trusting a learned skill.
- Inference: the held-out set for a plugin is a small fixed list of eval cases in `plugin/evals/` that the proposer is never shown the failure traces of; the description-trigger set should be split 60/40 as skill-creator does. Rests on run_loop.py and promptfoo findings.
- Inference: because `claude plugin eval` has `llm` graders that add cost and noise, prefer `regex`, `tool_used`, `file_exists` graders for acceptance gates in `plugin/skills/self-test/SKILL.md`.

### Gaps
- No source found giving a minimum effect size or significance test for prompt edits in these tools; promptfoo's CLI reference was not opened and may have thresholds.
- No source found for a persisted rejected-changes log in any of the tools; skill-creator keeps `history` for description attempts only (improve_description.py `--history`), which is the nearest analogue.
- No evidence gathered on reward hacking of LLM-judge graders by self-edited prompts.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| DSPy GEPA | https://dspy.ai/api/optimizers/GEPA/overview/index.md | Reflective, Pareto-based prompt evolution with minibatch-then-validation gating; needs a reflection LM | Python, local, needs LM key | 2026-10-16 | Reference design only; copy loop, do not install (key needed) |
| DSPy MIPROv2 | https://dspy.ai/api/optimizers/MIPROv2/ | Bootstrap demos + proposed instructions + Bayesian search | Python, local, needs LM key | 2026-10-16 | Skip; many calls, little value for markdown skills |
| TextGrad | https://github.com/zou-group/textgrad | Textual-gradient critique and rewrite, PyTorch-style API | Python, needs OpenAI/Anthropic key | 2026-10-16 | Skip; GEPA paper reports it as a weaker baseline |
| promptfoo optimize | https://www.promptfoo.dev/docs/usage/prompt-optimization/ | Baseline eval, LLM-proposed rewrites, optional held-out validation split | Node CLI, needs provider credential | 2026-10-16 | Fallback; not for markdown skills (prompt/provider pairs) |
| GEPA optimize_anything / gskill | https://github.com/gepa-ai/gepa/blob/main/docs/docs/blog/posts/2026-02-18-automatically-learning-skills-for-coding-agents/index.md | Evolves any text artifact, including coding-agent skills, from task feedback | Python, needs LM key and task generator | 2026-10-16 | Reference design; demonstrates skills as optimizable text |
| Anthropic skill-creator (anthropics/skills) | https://github.com/anthropics/skills/tree/main/skills/skill-creator | Content loop, grader/comparator/analyzer agents, description optimizer via `claude -p` | local, session auth, no extra key | 2026-10-16 | Use as template; copy patterns into plugin agents |
| claude plugin eval | https://code.claude.com/docs/en/plugin-evals | With/without-plugin eval cases, free deterministic graders, cost ceiling, CI exit codes | CLI, session auth | 2026-10-16 | Use in plugin/skills/self-test/SKILL.md |
