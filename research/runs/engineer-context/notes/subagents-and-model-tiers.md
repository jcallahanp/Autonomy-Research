# Subagent architecture and model tiers

Brief: Which subagent architectures work for a long-running coding agent, which tasks can go to Haiku/Sonnet/Opus-class models without losing outcome quality, and how to measure that on John's own tasks.
Run: research/runs/engineer-context/PLAN.md

Recommendation (one line): see end of Q5. Connectors note: Parallel fetch returned 429 (Too Many Requests) in this session; I used WebFetch and Exa instead.

## Q1 What Anthropic docs and engineering posts say about subagents and orchestrator-worker

### Takeaway
Claude Code subagents give fresh isolated context, per-agent tool allowlists and a per-agent model; the documented cost levers are Haiku for simple subagents, Sonnet for teammates, and delegating verbose work. For long-running coding, Anthropic's own harness posts (Nov 2025, Mar 2026) use initializer/coder, then planner/generator/evaluator, with file handoffs and fresh-context evaluators, and say the evaluator pays off only when the task is beyond what the model does solo. Confidence: high.

### Cited findings
- Subagent = fresh context, own tools and permissions — https://code.claude.com/docs/en/sub-agents, opened 2026-10-16, WebFetch — Quote: "Each subagent starts with a fresh, isolated context window. It doesn't see your conversation history, the skills you've already invoked, or the files Claude has already read."
- Model per subagent is a frontmatter field — https://code.claude.com/docs/en/sub-agents, opened 2026-10-16, WebFetch — Quote: "Model to use: `sonnet`, `opus`, `haiku`, `fable`, a full model ID such as `claude-opus-5-5`, or `inherit`."
- Tool scoping by allowlist or denylist — same page — Quote: "To restrict tools, use the `tools` field as an allowlist or the `disallowedTools` field as a denylist."
- Subagents cost tokens of their own — same page — Quote: "each subagent spends tokens of its own while it runs."
- Cost guidance: Opus only for hard reasoning, Haiku for simple subagents — https://code.claude.com/docs/en/costs, opened 2026-10-16, WebFetch — Quote: "Reserve Opus for complex architectural decisions or multi-step reasoning." and "For simple subagent tasks, specify `model: haiku`"
- Agent teams cost about 7x — same page — Quote: "Agent teams use approximately 7x more tokens than standard sessions when teammates run in plan mode"
- Delegate tests/docs/logs to subagents so output stays out of main context — same page — Quote: "Delegate these to subagents so the verbose output stays in the subagent's context while only a summary returns to your main conversation."
- Initializer + coder harness with file/git handoff — https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents, opened 2026-10-16 (via Exa search content, page text returned by Exa; not re-fetched) — Quote: "an initializer agent that sets up the environment on the first run, and a coding agent that is tasked with making incremental progress in every session"
- Same post leaves multi-agent open — same source — Quote: "it's still unclear whether a single, general-purpose coding agent performs best across contexts, or if better performance can be achieved through a multi-agent architecture."
- Planner/generator/evaluator harness cost and when the evaluator earns its keep — https://www.anthropic.com/engineering/harness-design-long-running-apps, opened 2026-10-16, WebFetch — Quote: "It is worth the cost when the task sits beyond what the current model does reliably solo."
- Same post: solo $9/20 min vs harness $200/6 h — Quote: "The harness was over 20x more expensive, but the difference in output quality was immediately apparent."
- Same post: a separate evaluator is not automatically strict — Quote: "the evaluator is still an LLM that is inclined to be generous towards LLM-generated outputs."
- Anthropic ships a fresh-context, no-write evaluator pattern and /goal — https://github.com/anthropics/cwc-long-running-agents, opened 2026-10-16 (Exa returned README text; not cloned) — Quote: "A separate agent with no Write/Edit tools grades the work from a context window that never saw the build."
- /goal uses a small fast model as judge that cannot run tools — https://code.claude.com/docs/en/goal, opened 2026-10-16, WebFetch — Quote: "The evaluator runs on whichever provider your session is configured for. It does not call tools, so it can only judge what Claude has already surfaced in the conversation."
- Orchestrator-worker evidence already collected (Opus lead + Sonnet workers beat single Opus by 90.2%, breadth-first research, ~15x chat tokens) — /home/user/Autonomy-Research/research/findings/architecture.md:3 (read 2026-10-16) — Quote: "Anthropic's Research system (Opus lead + Sonnet workers) beat single-agent Opus by 90.2% on an internal breadth-first eval, but at roughly 15x chat token cost"

### Contradictions
- None found. (Note: Anthropic's own multi-agent post says coding has fewer parallelizable tasks than research, per architecture.md:13; the harness posts use sequential roles, not parallel fan-out. Consistent.)

### Inferences
- For a long-running coding engineer the right shape is sequential roles with file handoff (plan file, progress file, git), not parallel peers; parallel fan-out is for read-only work (search, test runs, review). Rests on the harness posts and architecture.md:13.
- Because evaluator value depends on the distance between task and model ability, the evaluator should be switchable per task class and re-measured at each model release.

### Gaps
- I did not re-fetch the multi-agent-research-system post; its claims are cited only via the local findings file.
- Exa returned the harness and cwc README text in search content; I did not clone cwc-long-running-agents to read evaluator.md.

## Q2 What small or cheap models do well and badly in coding workflows

### Takeaway
Vendor and paper evidence agree: Haiku-class is good for narrow, well-specified, checkable work (search/localization, summaries, compaction, classification, simple edits, test running with a deterministic check) and clearly worse on long agentic coding and iterative reasoning. A cheap scout/handoff to a stronger fixer matched the best single model at about one-fifth the cost in one paper. Confidence: medium-high (vendor claims plus one preprint; no measurement on John's tasks).

### Cited findings
- Haiku 5.5 vendor positioning (7 Oct 2026) — https://www.anthropic.com/claude-haiku-5-5, opened 2026-10-16, WebFetch — Quote: "It pairs well with Opus 5.5 and Sonnet 5.5 as a subagent on coding work."
- Same page: not for complex agentic coding — Quote: "Sonnet 5.5 and Opus 5.5 remain better choices for complex agentic coding tasks like those measured by Terminal-Bench 4.0."
- Terminal-Bench 4.0 gap: Haiku 5.5 39.2% vs Sonnet 5.5 70.6% — same page (as returned by WebFetch summary; numbers not a verbatim sentence) — Quote: "Haiku 5.5 scored 39.2%, and Sonnet 5.5 scored 70.6%." (WebFetch's paraphrase of the table; treat the numbers as medium confidence)
- Haiku product page: use cases and price — https://www.anthropic.com/claude/haiku, opened 2026-10-16, WebFetch — Quote: "Haiku 5.5 is a fast, cost-efficient subagent for coding and well-defined tasks." Price per same fetch: $0.10 / $0.50 per million input/output tokens up to 100K prompt tokens.
- Haiku 4.5 as a published baseline: 73.3% SWE-bench Verified, "matching Sonnet 4" (Oct 2025) — https://www.anthropic.com/claude/haiku, opened 2026-10-16, WebFetch — Quote: "The only SWE-bench figure is for Haiku 4.5: 73.3% on SWE-bench Verified." (WebFetch summary text)
- Cheap scout then frontier fixer — https://arxiv.org/html/2608.04804v1 (Scrouting), opened 2026-10-16, WebFetch — Quote: "SuperScout matches the best single model's solve rate (159 of 266 for SuperScout, 158 for the best model)." Cost per solve $0.230 vs $1.274 for Opus 4.6 alone (SWE-bench Pro Python, 266 tasks; same fetch).
- Same paper: the scout handoff, not routing, did the work — Quote: "A no-router ablation, always the cheapest fixer with the handoff, ties the routed system on this benchmark." (WebFetch's quoted line)
- Verbose retrieval and test re-execution are the waste in coding agents — https://arxiv.org/pdf/2609.30725, search excerpt only; the PDF would not parse in WebFetch. Moved to Gaps.

### Contradictions
- None found on tier direction. Note vendor-published numbers for Haiku 5.5 come from Anthropic itself; no independent reproduction found.

### Inferences
- Delegable to Haiku-class (hypothesis to test): file/symbol search and localization, summarizing test or log output, compaction, formatting, running a fixed test command and reporting, link/quote checking against an opened page. Rests on Haiku 5.5 vendor text and the Scrouting result.
- Keep on Sonnet-class: implementation of well-scoped tickets, research workers, code review. Keep on Opus/Fable-class: architecture, planning of the long run, debugging with unclear root cause, final integration. Rests on Terminal-Bench gap, Anthropic cost guidance (costs page) and the harness-design "beyond what the model does solo" rule. This is my inference, not a measured result.

### Gaps
- https://arxiv.org/pdf/2609.30725 (cost-inefficient behaviours; Haiku 4.5 subagent under Claude Code): WebFetch returned binary PDF, Parallel fetch returned 429. Not cited.
- No independent per-task-type measurement (debugging vs search vs formatting) of Haiku 5.5 found. Haiku 5.5 system card seen only as search excerpt (not opened).
- Opus 5.5 Terminal-Bench figure: the Haiku page gave none, so no Opus number is cited.

## Q3 Published architectures with a separate verifier or reviewer, and their effect

### Takeaway
Separate reviewers help when anchored to a decisive check (tests, running the app) and mostly fail when they just re-read the output. Single LLM review catches about half of defects; a second independent reviewer adds the most; lightweight reviewers without evidence add little or reject too much. Confidence: medium (several preprints, small samples, some single-author).

### Cited findings
- Weak reviewers become reliable when execution evidence is supplied — https://arxiv.org/html/2610.01023, opened 2026-10-16, WebFetch — Quote: "Official execution evidence shows the potential of weak review when decisive checks are available."
- Same paper: reviewer size does not predict quality; generated-test cascade still over-rejects — Quote: "Reviewer size is not a consistent predictor of quality." Cascade numbers (catch 0.76/0.80, over-rejection 0.66/0.67) from the same abstract.
- Lightweight cross-model reviewer no better than same-model fresh review — https://arxiv.org/html/2610.01471v1, opened 2026-10-16, WebFetch — Quote: "A lightweight cross-model reviewer scores no higher than same-model review."
- Same paper: one same-model plus one cross-model review beats two same-model — Quote: "one CCR plus one XMR review covers more ground-truth errors than two CCR reviews (56.7% vs. 42.7%)."
- Single-model review is incomplete (single-org case study, 294 issues) — https://doi.org/10.5281/zenodo.20519584, content returned by Exa search, not separately fetched — Quote: "coverage of an artifact's confirmed defects rises from about 47% with one reviewer to about 72% with a second"
- Anthropic evaluator catches issues only at the edge of model ability — https://www.anthropic.com/engineering/harness-design-long-running-apps, opened 2026-10-16, WebFetch — Quote: "It is worth the cost when the task sits beyond what the current model does reliably solo."
- Claude marks features done without end-to-end testing; mitigations are a pass/fail feature list and e2e test — https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents (Exa-returned text) — Quote: "Claude's tendency to mark a feature as complete without proper testing."
- MAST: weak or missing verification is a leading failure class and objective-level verification added +15.6% on ChatDev — /home/user/Autonomy-Research/research/findings/architecture.md:15 (read 2026-10-16) — Quote: "Adding a high-level task-objective verification step to ChatDev gave +15.6% task success [MAST]."

### Contradictions
- Anthropic's harness post (evaluator "continued to give real lift" at the model's edge) vs the cross-model paper (lightweight reviewer no better than same-model): not a direct conflict, different setups. A multi-agent judge paper (https://arxiv.org/abs/2609.30328, Exa excerpt only, Qwen3-8B) reports a claim-checking pipeline at 4.4% accuracy vs 43.7% for the same model asked directly; this warns that elaborate verifier pipelines without independent evidence can be worse than one direct call. Would be settled by running John's own paired test.

### Inferences
- A cheap verifier should check things that can be tested mechanically (command exit codes, file exists, quote present in a page, test passes), not judge quality. The Haiku verifier in this repo fits that shape for citations; a code-review verifier on Haiku does not have support in the evidence.
- For code correctness, put the money into the check (tests, e2e run), then a Sonnet/Opus-class reviewer with fresh context and no write tools.

### Gaps
- No published cost-per-defect-caught number for a Haiku-class reviewer in a coding agent.
- arxiv 2609.30328, the Zenodo paper and 2610.10961 (cross-provider review, 8 of 20 turns had material findings) are cited from search content only; not independently opened beyond that.

## Q4 Measuring quality against cost for model-tier choices

### Takeaway
Cheap loop: 20 to 50 real tasks from John's own past failures, deterministic graders first, paired runs of the same tasks per tier, a few repeats because agents are nondeterministic, compare pass rate and token cost, read transcripts. Claude Code already has the measurement primitives (plugin eval, /usage attribution, OpenTelemetry). Confidence: medium-high.

### Cited findings
- Start small and from real failures — https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents, opened 2026-10-16, WebFetch — Quote: "In reality, 20-50 simple tasks drawn from real failures is a great start."
- Grade outcomes — same page — Quote: "it's often better to grade what the agent produced, not the path it took."
- Prefer deterministic graders — same page — Quote: "We recommend choosing deterministic graders where possible"
- Consistency metric — same page — Quote: "pass^k measures the probability that all k trials succeed."
- Isolation per trial — https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents (Exa-returned text) — Quote: "Each trial should be \"isolated\" by starting from a clean environment."
- Read transcripts — demystifying-evals page, WebFetch — Quote: "You won't know if your graders are working well unless you read the transcripts and grades from many trials."
- Per-subagent and per-skill cost attribution exists — https://code.claude.com/docs/en/costs, opened 2026-10-16, WebFetch — Quote: "recent usage attributed to skills, subagents, plugins, and individual MCP servers, each shown as a percentage of the total."
- Model-per-subagent override for A/B runs — https://code.claude.com/docs/en/sub-agents, WebFetch — Quote (from the earlier findings file, line 53): see architecture.md:53 `CLAUDE_CODE_SUBAGENT_MODEL` runs every subagent on one model. Local read: /home/user/Autonomy-Research/research/findings/architecture.md:53 — Quote: "`CLAUDE_CODE_SUBAGENT_MODEL` (+ `_FORCE`) runs every subagent on one model"
- Existing eval command: `claude plugin eval` with `--runs`, `--judge-model`, `--max-cost-usd` — /home/user/Autonomy-Research/research/tool-registry.md:41 (read 2026-10-16) — Quote: "`--runs` (default 3), `--threshold`, `--judge-model`, `--ablation none`, `--max-cost-usd`"
- Published routing/benchmark tooling exists but targets general tasks: Agent-as-a-Router with CodeRouterBench (~10K tasks, 8 LLMs) — https://www.alphaxiv.org/abs/2606.22902 (Parallel search excerpt only). Not cited as a source; moved to Gaps.
- Practitioner caution on harness vs model: a harness change moved cost with flat correctness — https://www.alphaxiv.org/abs/2607.03691 search excerpt only ("Flat correctness, rising cost"); moved to Gaps.

### Contradictions
- None found.

### Inferences
- Cheap loop for John (my design): (1) collect 20 to 30 tasks from his repos with a runnable check (tests pass, lint clean, file diff matches); (2) tag by role: search/localize, summarize, implement, review, debug, plan; (3) run each task per tier with `CLAUDE_CODE_SUBAGENT_MODEL` or per-agent `model:` swapped, 3 repeats, fresh worktree each; (4) record pass rate, pass^3, tokens and dollars from /usage or OpenTelemetry, wall time; (5) adopt the cheaper tier for a role only if pass^3 is not lower than the stronger tier on that role and a human spot-check of 5 transcripts agrees; (6) re-run on every model release, since Anthropic notes harness assumptions go stale as models improve (managed-agents post, Apr 2026, search excerpt).
- Under a Max subscription, dollars are not billed per token, so use tokens and plan-usage share as the cost proxy; list-price dollar figures from /usage are estimates.

### Gaps
- The 20-task count and 3 repeats are standard-practice inferences, not a measured sample-size analysis. 3 repeats on 20 tasks gives wide intervals; I did not compute them.
- No source found that gives a validated statistical threshold for accepting a cheaper tier.

## Q5 What the local rules settle, and what the engineer needs beyond them

### Takeaway
The repo's rules settle research-agent roles: lead holds plan and index only, Sonnet researchers, Haiku citation verifier, inherit-model synthesizer, Sonnet spike worker. They rest on Anthropic's Opus-lead/Sonnet-worker data and are sound for research. They do not settle coding: no implementer, no code reviewer, no test-runner role, no tier measurement, and the Haiku verifier is justified for citation checks only. Confidence: high on what exists, medium on what the engineer needs.

### Cited findings
- Researcher on Sonnet, 40 turns, no CLAUDE.md — /home/user/Autonomy-Research/plugin/agents/researcher.md:4-7 (read 2026-10-16) — Quote: "model: sonnet" / "maxTurns: 40" / "omitClaudeMd: true"
- Verifier on Haiku, medium effort, read-and-fetch tools only, 20-claim cap — /home/user/Autonomy-Research/plugin/agents/verifier.md:4-6 (read 2026-10-16) — Quote: "model: haiku" and "never more than 20 claims"
- Verifier marks uncertain as unverified — /home/user/Autonomy-Research/plugin/agents/verifier.md:34 (read 2026-10-16) — Quote: "An uncertain judgment counts as unverified."
- Synthesizer inherits lead's model at high effort, no research tools — /home/user/Autonomy-Research/plugin/agents/synthesizer.md:4-6 — Quote: "model: inherit"
- Spike worker on Sonnet, only agent allowed to run a candidate — /home/user/Autonomy-Research/plugin/agents/spike-worker.md:4 and :18 — Quote: "You are the one agent allowed to install or run a candidate."
- Prior decision: Haiku not default for workers — /home/user/Autonomy-Research/research/findings/architecture.md:128 — Quote: "*Haiku workers by default*: not adopted; Anthropic's data says worker model quality beats token budget, and Haiku is reserved for the verifier and for trivially bounded tasks."
- Prior decision: agent teams rejected — architecture.md:125 — Quote: "*Agent teams with peer messaging*: rejected for now; docs say roughly 7x tokens, experimental and disabled by default"
- Prior open question that this facet inherits: architecture.md:148 — Quote: "the degradation slope for the models this plugin will actually run is unmeasured."
- Lead may hold only plan, INDEX, status lines — /home/user/Autonomy-Research/CLAUDE.md (supplied in session context, "What the lead may hold in context"; not re-read as a file in this session).

### Contradictions
- Prior finding architecture.md:118 says the verifier could be "Haiku or Sonnet"; verifier.md:4 fixes Haiku. Not a conflict, but the Haiku choice has no measurement behind it (see Gaps).

### Inferences
- Already settled and reusable by the engineer: lead holds plan and index only; one worker per mutually exclusive facet; workers write file notes and return short summaries; a single synthesizer; fresh-context verifier with read-only tools; homogeneous worker models for cache sharing (architecture.md:80); no peer agent teams.
- Needed beyond them for a coding engineer:
  1. Roles: planner (Opus/Fable-class), implementer (Sonnet-class, one ticket at a time, fresh context, progress file plus git), tester/runner (Haiku-class only if the check is a fixed command), reviewer (fresh context, no Write/Edit, Sonnet-class or higher, given test evidence), debugger (escalate to the lead's model).
  2. A deterministic done-gate (tests, e2e) before any LLM verdict; `/goal` or a Stop hook as the loop engine, with a turn cap. /goal's evaluator cannot run tools (goal docs), so the builder must surface evidence.
  3. Escalation rule: cheap tier first only for checkable roles; on failed check, rerun on the next tier rather than retrying the same tier more than once (inference).
  4. Tier measurement on John's tasks (Q4) before any role is moved to Haiku; the research agent's own Haiku verifier should be checked the same way with seeded wrong citations.
  5. Cost telemetry: /usage attribution per subagent, an OpenTelemetry export if unattended runs matter.
- Recommendation: adopt Claude Code subagents with the existing lead/worker/synthesizer/verifier pattern, extend it with planner, implementer, fresh-context reviewer and a deterministic done-gate, run Opus/Fable for plan and debug, Sonnet for implement/review/research, Haiku 5.5 only for search, summarization, compaction and fixed-command test running until a 20 to 30 task paired test shows no loss. Alternatives: single Sonnet agent with /goal (cheapest, spike first); Anthropic's cwc-long-running-agents primitives as a template; agent teams (rejected, 7x). Rejected: Haiku as default implementer (Terminal-Bench 39.2% vs 70.6%); a Haiku code reviewer without execution evidence (cross-model paper); parallel implementers on one repo (Cognition and architecture.md:13). Spike before building: paired tier test on 20 to 30 real tasks; the done-gate plus fresh-context reviewer loop on one real ticket; whether a Haiku verifier catches seeded errors at the Sonnet rate.

### Gaps
- Whether plugin `agents/` can set per-run model overrides from a skill (per-invocation `model` parameter per the sub-agents docs summary in architecture.md:53) was not tested.
- The Haiku verifier's recall on seeded bad citations is unmeasured.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Claude Code subagents (model/tools per agent) | https://code.claude.com/docs/en/sub-agents | Fresh-context workers, per-agent model and tool allowlist | Claude Code | 2026-10-16 | Use; core primitive |
| /goal | https://code.claude.com/docs/en/goal | Fast-model evaluator checks a completion condition after every turn; cannot run tools | Claude Code (interactive, -p, Remote Control) | 2026-10-16 | Use as loop engine with a turn cap and tool-surfaced evidence |
| anthropics/cwc-long-running-agents | https://github.com/anthropics/cwc-long-running-agents | Hooks plus fresh-context evaluator subagent, default-FAIL contract, progress handoff | Claude Code / Agent SDK | 2026-10-16 (README via Exa; not cloned) | Template to copy; spike first |
| Claude Haiku 5.5 | https://www.anthropic.com/claude-haiku-5-5 | Cheap subagent model; $0.10/$0.50 per M tokens up to 100K prompt | Claude API / Claude Code alias haiku | 2026-10-16 | Use for narrow checkable roles only; not implementer |
| Scrouting / SuperScout | https://arxiv.org/html/2608.04804v1 | 7B scout hands off to frontier fixer; research prototype | research (not run) | 2026-10-16 | Reference; idea (cheap scout, strong fixer) |
| Agent-as-a-Router / CodeRouterBench | https://www.alphaxiv.org/abs/2606.22902 | Routing benchmark for coding tasks | research (not opened) | 2026-10-16 (search excerpt only) | Reference only; unverified |
