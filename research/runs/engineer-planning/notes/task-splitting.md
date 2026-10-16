# Task decomposition: size versus error rate and splitting rules

Brief: Find evidence for how narrow tasks must be for a Claude Code engineer to succeed reliably, and turn it into concrete splitting rules (John: Superpowers tasks were not narrow enough and the agent hallucinated).
Run: research/runs/engineer-planning/PLAN.md

## Evidence linking task size to success

### Takeaway
Success falls with task size on every source opened: METR's logistic fits, SWE-Bench Pro (lines and files), Anthropic's own harness posts, and spec-kit's maintainers. The 80%-reliability horizon for the best Claude models is roughly 1 hour of human work (METR, Opus 4.6, noise-adjusted), 4-10x below the headline 50% number, so "reliable" tasks should be sized at tens of minutes of human work, 1-4 files, about 100 lines, with a runnable check. Confidence: medium (METR numbers are revised often and secondary sources disagree on exact values).

### Cited findings
- METR defines the horizons by fitted success curve over human task duration; 50% and 80% are separate points on it — https://metr.org/time-horizons/, opened 2026-10-16, Exa search highlights (page text) — Quote: "To get the 50%-time horizon (or 80%-time horizon), we find the task duration where the fitted curve intersects with 50% (or 80%) success probability."
- METR page is frozen; last Claude entry Mythos Preview (early) May 2026; above 16 h unreliable — https://metr.org/time-horizons/, opened 2026-10-16, Exa — Quote: "September 8th, 2026: Clarified that this page is no longer actively updated."
- METR's noise-adjusted Opus 4.6 numbers: 50% about 7.6 h, 80% about 1 h 16 m (full dataset, regularization-fix logistic) — https://metr.org/notes/2026-03-20-impact-of-modelling-assumptions-on-time-horizon-results/, opened 2026-10-16, Exa — Quote: "Logistic (Reg. Fix) | 7h 38m (-36%) | 1h 16m (+9%)"
- METR says modelling choices move Opus 4.6 results ~1.5x (50%) and 2x (80%) — same URL — Quote: "The variation in the results from reasonable methods is ~1.5x in 50% TH and 2x in 80% TH for Opus 4.6."
- METR says the 80% horizon is not an independent estimate — https://metr.org/notes/2026-01-22-time-horizon-limitations/, opened 2026-10-16, Exa — Quote: "20% and 80% time horizons are not fully independent estimates from the 50% time horizon, because there aren't enough parameters to fit them separately."
- Claude Code scaffold did not beat METR's own scaffolds for Opus 4.5, so the numbers transfer to Claude Code roughly — https://metr.org/notes/2026-02-13-measuring-time-horizon-using-claude-code-and-codex/, opened 2026-10-16, Exa — Quote: "neither Claude Code nor Codex outperform the default scaffolds METR uses, at least when measuring the time horizon of Opus 4.5 and GPT-5."
- Opus 4.5 50% horizon 320 minutes on TH1.1 (CI 170-729); Sonnet 4.5 122 min on TH1 — https://metr.org/blog/2026-1-29-time-horizon-1-1/, opened 2026-10-16, Exa — Quote: "Claude Opus 4.5 | 289 [110,1268] | 320 [170,729] | +11%"
- SWE-Bench Pro tasks average 107 lines over 4.1 files; best models scored about 23% in Sept 2025 vs over 70% on Verified — https://scale.com/blog/swe-bench-pro, opened 2026-10-16, Exa — Quote: "These tasks require substantial changes, averaging 107.4 lines of code across 4.1 files."
- Scale reports performance degrades with lines and files — https://labs.scale.com/leaderboard/swe_bench_pro_public, opened 2026-10-16, Exa — Quote: "Model performance significantly degrades as solutions require more lines to be added and files to be edited."
- Scale's failure analysis: bigger models miss on logic on large edits; some hit context overflow — https://dataist.ai/research/top-coding-agents-solve-under-a-quarter-of-swe-bench-pro-tasks/, opened 2026-10-16, Exa (secondary) — Quote: "Some systems ran into context overflow and endless walking of the file tree, formatting errors and build incompatibilities."
- Anthropic: Claude's dominant failure was doing too much at once — https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents, opened 2026-10-16, Exa — Quote: "the agent tended to try to do too much at once—essentially to attempt to one-shot the app."
- Anthropic: one feature per session was critical — same URL — Quote: "the next iteration of the coding agent was then asked to work on only one feature at a time. This incremental approach turned out to be critical"
- Claude Code docs: context fills and performance degrades; Anthropic's first-listed fix is a runnable check — https://code.claude.com/docs/en/best-practices, opened 2026-10-16, WebFetch — Quote: "LLM performance degrades as context fills. When the context window is getting full, Claude may start \"forgetting\" earlier instructions or making more mistakes."
- Claude Code docs: size test for skipping a plan — same URL — Quote: "If you could describe the diff in one sentence, skip the plan."
- Claude Code docs: spec should name files, interfaces, out-of-scope and an end-to-end check — same URL — Quote: "they name the files and interfaces involved, state what is out of scope, and end with an end-to-end verification step that proves the feature works."
- Anthropic (Mar 2026): as models improved (Opus 4.6) the sprint decomposition was removed; decomposition need shrinks with model strength — https://www.anthropic.com/engineering/harness-design-long-running-apps, opened 2026-10-16, Exa — Quote: "I started by removing the sprint construct entirely."
- spec-kit maintainers document hallucination during long implement runs near compaction — https://github.github.com/spec-kit/concepts/complex-features.html, opened 2026-10-16, Exa — Quote: "agents can start to lose track of the plan, ignore tasks, or hallucinate — usually right before or after context compaction is triggered."

### Contradictions
- Opus 4.6 horizons differ by source. METR's note (2026-03-20) gives a pre-adjustment 50% of 12 h and noise-adjusted 7h38m / 1h16m — https://metr.org/notes/2026-03-20-impact-of-modelling-assumptions-on-time-horizon-results/ ; a third-party data-file reading gives 718.8 min / 69.9 min — https://www.clrtstudio.com/insights/half-the-time-not-every-time (seen in Exa highlights only); another gives 221.6 min (3.69 h) / 7.7 min — https://the-agent-report.com/2026/05/claude-mythos-shatters-metr-time-horizon/ (highlights only). Settle by reading METR's dashboard data file (page is dynamic; not opened).
- Anthropic says decomposition into sprints became unnecessary on Opus 4.6 (harness-design post) vs Anthropic's Claude Code docs and Huntley still recommending narrow tasks. Both can hold: it depends on whether a runnable check exists and how close the task is to the model edge.

### Inferences
- (Mine, from METR 80% about 1 h and SWE-Bench Pro) A routine engineer task should target well under the 80% horizon, say 15-45 min of human work, because John's tasks will be in private, unfamiliar code where Scale saw lower rates (22.7% to 17.8% for Opus 4.1) and because METR tasks are self-contained with scoring scripts, which real tasks lack.
- (Mine) Hallucination in long runs is a context-length failure, so a token/turn budget is a better operational cap than minutes. spec-kit's own docs and the Anthropic harness post both point at context exhaustion.

### Gaps
- No METR 80% value for Claude Opus 5.x / Sonnet 5.5 (current models) found; METR page frozen 2026-09-08 and dynamic, raw data not opened.
- No source linking success to "files touched" for Claude specifically beyond Scale's qualitative statement; the per-bucket numbers were not opened.
- OpenAI Codex and Cursor vendor guidance on task size not searched (budget).
- FeatBench not opened.

## How Superpowers, Beads, Ralph, spec-kit, Kiro, BMAD, Taskmaster split work

### Takeaway
Only Ralph and Anthropic's harness set a hard "one item per fresh context" rule. Superpowers 7.0.0 defines a task as a test-cycle-sized unit with 2-5-minute steps inside it, but leaves task count and size to the planner; spec-kit and Kiro produce large markdown plans and execute all tasks in one run unless the user scopes it. Failure reports exist for spec-kit (hallucination mid-run), Kiro (session too long, over-large specs for small bugs) and over-verbosity; I found none for Beads granularity. Confidence: medium.

### Cited findings
- Superpowers writing-plans defines a task as the smallest unit with its own test cycle, with steps as single actions — https://github.com/obra/superpowers skills/writing-plans/SKILL.md:36-41 (commit bb92a77), read 2026-10-16, clone — Quote: "A task is the smallest unit that carries its own test cycle and is worth a fresh reviewer's gate."
- Same file: steps are one action each — skills/writing-plans/SKILL.md:45 — Quote: "**Each step is one action with a checkable result:**"
- Superpowers tells the planner to fold setup and docs into the task and to split only where a reviewer could reject one without the other — skills/writing-plans/SKILL.md:37-40 — Quote: "split only where a reviewer could meaningfully reject one task while approving its neighbor."
- Superpowers has no numeric ceiling on files, lines or tokens per task in writing-plans; the only size rule is the scope check for independent subsystems — skills/writing-plans/SKILL.md:19-21 — Quote: "If the spec covers multiple independent subsystems, it should have been broken into sub-project specs during brainstorming."
- Superpowers executor: fresh implementer subagent per task, model chosen by task type ("isolated functions, clear specs, 1-2 files" as mechanical) — skills/subagent-driven-development/SKILL.md:188 — Quote: "**Mechanical implementation tasks** (isolated functions, clear specs, 1-2 files): use a fast, cheap model."
- Superpowers fix loop is capped at 5 rounds with escalation — skills/subagent-driven-development/SKILL.md:75 — Quote: "Fix round R of 5: R≤3 resume implementer; R≥4 fresh implementer, more capable model"
- Superpowers plan placeholders are banned — skills/writing-plans/SKILL.md:159 — Quote: "decide nothing (\"TBD\", \"handle edge cases\", \"add appropriate validation\","
- Ralph (Huntley, 2025-07-14): one item per loop, narrow when it goes wrong — https://ghuntley.com/ralph/, opened 2026-10-16, Exa — Quote: "One item per loop. I need to repeat myself here—one item per loop. You may relax this restriction as the project progresses, but if it starts going off the rails, then you need to narrow it down"
- Ralph's rationale is context size — same URL — Quote: "you only have approximately 170k of context window to work with. So it's essential to use as little of it as possible."
- Ralph variant repo: one iteration = one fresh context = one task = one commit; 40-60% context "smart zone" — https://github.com/ghuntley/how-to-ralph-wiggum, opened 2026-10-16, Exa — Quote: "Each iteration = one fresh context window = one task from IMPLEMENTATION_PLAN.md = one commit"
- Ralph's own prompt variant still allows "the most important 10 things" per loop, so Huntley's size rule is not uniform — https://ghuntley.com/ralph/ — Quote: "choose the most important 10 things."
- spec-kit tasks template: tasks grouped by user story, [P] marks parallel tasks (different files, no dependencies), each story has an "Independent Test" — https://github.com/github/spec-kit templates/tasks-template.md:16-19,81 (commit f6e72bc), read 2026-10-16, clone — Quote: "**[P]**: Can run in parallel (different files, no dependencies)"
- spec-kit's template warns against vague tasks and same-file conflicts — templates/tasks-template.md:252 — Quote: "Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence"
- spec-kit docs: scope each implement run with N tasks or a phase; sub-agent per task; spec-of-specs when one phase overwhelms — https://github.github.com/spec-kit/concepts/complex-features.html, opened 2026-10-16, Exa — Quote: "/implement only execute tasks 1-10, then stop and report progress" (from discussion #2914, https://github.com/github/spec-kit/discussions/2914)
- spec-kit user report (2025-09): too much generated spec, agent ignores parts — https://github.com/github/spec-kit/discussions/1784, opened 2026-10-16, Exa — Quote: "split task to atomic points by yourself (in the ticket for example) - ask LLM to implement one by one"
- Kiro: "Session Too Long" when spec is large, user wants single tasks without full docs — https://github.com/kirodotdev/Kiro/issues/2324, opened 2026-10-16, Exa — Quote: "A single task execution probably doesn't need the full requirements and design docs, but I couldn't see any way to exclude them."
- Kiro/spec-kit overkill for small work — https://www.martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html, opened 2026-10-16, Exa — Quote: "The requirements document turned this small bug into 4 \"user stories\" with a total of 16 acceptance criteria"
- Fowler article: agent ignored instructions and duplicated existing code — same URL — Quote: "the agent ultimately not follow all the instructions."
- Beads supports hierarchical epic/task/sub-task IDs and `bd ready` for tasks with no open blockers — https://github.com/steveyegge/beads README.md:73-86 (commit dff9492), read 2026-10-16, clone — Quote: "`bd-a3f8` (Epic) * `bd-a3f8.1` (Task) * `bd-a3f8.1.1` (Sub-task)"
- Anthropic harness: 200+ features all marked failing in a JSON list, one at a time; JSON used because the model edits it less — https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents, opened 2026-10-16, Exa — Quote: "the model is less likely to inappropriately change or overwrite JSON files compared to Markdown files."

### Contradictions
- Superpowers calls steps "2-5 minute" in older versions (brief's recollection); the 7.0.0 file I read (commit bb92a77) says "Each step is one action" and defines tasks by test cycle, with no minutes figure found (grep for "minute" returned only the word in unrelated places; none in right-sizing). Treat any "2-5 minutes" claim as unverified for this version.

### Inferences
- (Mine) John's failure matches Superpowers' design: the task is defined by "own test cycle", not by a context or file budget, so one task can span many files and the implementer subagent still runs a long session. Evidence: SKILL.md:36-41 has no numeric ceiling; spec-kit docs show the same mode (mid-run hallucination) with larger tasks.
- (Mine) Taskmaster: I cloned it but only confirmed it ships `analyze_project_complexity` and `expand_all` tools (README.md:356); I did not read how it thresholds subtasks, so no claim on its granularity.

### Gaps
- BMAD story sizing not opened (registry already marks it heavy; skipped).
- Taskmaster complexity thresholds and failure reports not read.
- No failure report on Beads granularity or on too-fine splitting in Superpowers found.
- Superpowers GitHub issues about hallucination or oversize tasks not searched.

## What "narrow enough" means operationally

### Takeaway
No source gives one universal unit; the converging operational definition is: one fresh context, one verifiable outcome (a check the agent can run), one commit, touching files that change together. Over-splitting also hurts (coordination overhead, interface mismatches, error accumulation), with a peak at intermediate granularity. Confidence: medium (the over-splitting evidence is mostly benchmarks on small programs and one preprint of doubtful provenance).

### Cited findings
- Terminal-Bench v2 success peaks at an intermediate number of workflow steps and falls when too fragmented — https://www.alphaxiv.org/abs/2605.21516, opened 2026-10-16, Exa (summary page) — Quote: "the agent's success rate peaks at a specific number of steps (six, in this case) and declines if the task is either too unified or too fragmented."
- Same work: partial harnesses can beat fully structured ones — same URL — Quote: "specifying only the initial steps and leaving the remaining execution to agent can achieve higher pass rate than fully structured workflows."
- Splitting one class across two agents loses 25-39 points even with full docstrings (Sonnet, Haiku) — https://arxiv.org/pdf/2603.24284, opened 2026-10-16, Exa — Quote: "a persistent coordination gap (25–39pp) separates multi-agent from single-agent performance—even when specifications are detailed."
- That paper: the spec is the coordination contract — same URL — Quote: "the specification functions as a coordination contract between agents"
- Over-fine nodes add interface overhead — https://arxiv.org/html/2607.29529v1 (AuditCoder), opened 2026-10-16, Exa — Quote: "overly fine nodes add interface overhead and may split a global invariant across locally plausible components."
- Decomposition granularity preprint reports an optimal window and a coordination-error rise with over-splitting (DGI) — https://clawrxiv.io/abs/2604.00690, opened 2026-10-16, Exa — Quote: "(III) an over-decomposition regime where coordination overhead dominates." Provenance weak (clawRxiv, AI-style authorship, unreviewed); use as hypothesis only.
- Claude Code docs say after two failed corrections, clear and restart; and that tight feedback beats long sessions — https://code.claude.com/docs/en/best-practices, opened 2026-10-16, WebFetch — Quote: "After two failed corrections, `/clear` and write a better initial prompt incorporating what you learned."
- Anthropic harness: end each session in a mergeable state with commit and progress file — https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents — Quote: "the kind of code that would be appropriate for merging to a main branch"
- cwc-long-running-agents scopes each session to one feature, with a default-FAIL contract and a fresh evaluator — https://github.com/anthropics/cwc-long-running-agents, opened 2026-10-16, Exa highlights — Quote: "it scopes each session to one feature, writes to a structured `PROGRESS.md` as it works and re-reads it first thing on every restart"
- Ralph repo: "smart zone" 40-60% of context — https://github.com/ghuntley/how-to-ralph-wiggum, Exa — Quote: "40-60% context utilization for \"smart zone\""

### Contradictions
- Ralph/Anthropic "one item per loop, narrow" vs Terminal-Bench finding that too-fine steps lose — https://github.com/ghuntley/how-to-ralph-wiggum vs https://www.alphaxiv.org/abs/2605.21516. Reconcile: a "task" is small in context, not in number of micro-steps; fold setup/docs into the task (Superpowers' own right-sizing rule).

### Inferences
- (Mine) Proposed splitting rules for John's engineer:
  1. One task = one fresh session, one commit, one acceptance check the agent can run (test, build, script, screenshot). No check, no task.
  2. Size cap by estimate of human work 15-45 min, 1-4 files, about 100 changed lines (SWE-Bench Pro average is 107 lines / 4 files, where best models were near 23%; a cap near the average is the edge, so go below it). Anything over: split.
  3. Split on seams where an interface can be written down (signature, schema, test) before either side is built; never split inside one module or one class (arXiv 2603.24284).
  4. Fold scaffolding, config and docs into the task that needs them (Superpowers rule); do not make 2-minute tasks.
  5. Context cap: planner records files-to-read per task and the implementer starts fresh; stop and re-split if the session passes about 50% of context or after 2 failed corrections.
  6. Put the global constraints in every task's context verbatim; keep task text self-contained (names files, interfaces, out-of-scope, check) per Claude Code docs.
  7. Re-split triggers: task fails its check twice, touches files not listed, or the agent asks to change the interface.
  8. Revisit sizes per model release: the Opus 4.6 harness dropped sprints.
- (Mine) Time box is a poor unit because METR shows estimates of human time are noisy (80% of estimates within 4x). Prefer files + lines + check + context share.

### Gaps
- No controlled study of "too fine" splitting on real repo-level Claude Code work; evidence is class-level or small-program benchmarks.
- Numbers in rules 2 and 5 are my inference, not measured; need a spike (see recommendation).

## Dependency ordering and parallelism

### Takeaway
Represent tasks as a DAG with explicit blocks edges and a "ready" query (Beads does this; spec-kit's [P] marker is the minimal form). Parallelism pays only when tasks touch different files and share no interfaces; naive parallel agents raised cost 44-60% for little gain. Confidence: medium.

### Cited findings
- Beads: `bd ready` lists tasks with no open blockers; `bd dep add <child> <parent>` links blocks/related/parent-child; `--claim` takes a task — https://github.com/steveyegge/beads README.md:73-76 (commit dff9492), read 2026-10-16, clone — Quote: "| `bd ready` | List tasks with no open blockers. |"
- Beads: dependency link types — README.md:76 — Quote: "| `bd dep add <child> <parent>` | Link tasks (blocks, related, parent-child). |"
- Superpowers parallel dispatch only for independent problems — https://github.com/obra/superpowers skills/dispatching-parallel-agents/SKILL.md:3 (commit bb92a77), read 2026-10-16, clone — Quote: "Use when facing 2+ independent tasks that can be worked on without shared state or sequential dependencies"
- Superpowers sends dependent work sequentially — skills/dispatching-parallel-agents/SKILL.md:32 — Quote: "\"Can they work in parallel?\" -> \"Sequential agents\" [label=\"no - shared state\"];"
- spec-kit: [P] means different files, no dependencies; foundational phase blocks all stories — templates/tasks-template.md:60-62 (commit f6e72bc) — Quote: "No user story work can begin until this phase is complete"
- Cohesion-aware partitioning (arXiv 2606.00953): file-parallel baseline cost +44% for +0.9pt pass; Agent Teams fastest but lowest pass rate — https://arxiv.org/html/2606.00953, opened 2026-10-16, Exa — Quote: "The poor task partitioning causes parallel agents to produce conflicting interfaces, requiring redundant re-generation that incurs extra costs without improving code quality."
- Same paper: execution through a shared ready-list without layer barriers — same URL — Quote: "each file is registered as a task whose state advances from pending to ready the moment all of its upstream files have completed"
- Same paper: coupling raises benefit of cohesion-aware partitions — same URL — Quote: "edge density (|E|/|V|; Table 4) correlates positively with absolute test-pass improvement over Sequential"
- Claude Code supports worktrees for isolated parallel sessions and warns agent teams are experimental — https://code.claude.com/docs/en/best-practices, WebFetch, opened 2026-10-16 — Quote: "Worktrees: run separate CLI sessions in isolated git checkouts so edits don't collide"
- Ralph/Huntley: parallel subagents for reads/search, one for build/test to avoid back-pressure — https://ghuntley.com/ralph/ — Quote: "only 1 subagent for build/tests of rust."
- Anthropic harness: JSON feature list with a pass field, choose "highest-priority feature that's not yet done" — Anthropic URL above — Quote: "Choose a single feature to start working on."

### Contradictions
- None found.

### Inferences
- (Mine) For one user and an unattended engineer, sequential by default with a DAG in `tasks.json` (id, deps, files, check, status) is enough; allow parallel worktrees only when two ready tasks have disjoint file sets and no shared interface, as declared in the plan. This matches the registry stance: Beads only when ordering or multi-agent claims bite.
- (Mine) Include a `files` list per task so the supervisor can detect overlap mechanically and serialize on conflict; this is the file-set version of Beads' blocks edge.

### Gaps
- Beads real-world failure reports at scale not read (registry notes 446 open issues and an Aug 2026 data-loss incident).
- Worktree merge-conflict rates for Claude Code not found.

## Recommendation, alternatives, rejects, spikes

Recommendation: keep Superpowers' subagent-per-task execution, but replace its size rule with a hard task contract in the plan (rules 1-8 above: one fresh session, one commit, one runnable check, 1-4 files, about 100 lines, files list, deps list, global constraints repeated), stored as a `tasks.json` DAG with passes field and `ready` computed by the supervisor script. Cap each unattended session by `--max-turns` and a context share.
Alternatives: Beads (use if multi-agent claims or cross-session dependency queries bite); spec-kit [P] and phase scoping (cheap pattern, lighter than adopting the tool); Ralph one-item-per-loop with the outer supervisor owning bounds.
Rejected: BMAD/Kiro-style large story documents for a single-user engineer (Fowler: overkill, Kiro "Session Too Long"); Taskmaster auto-expand as sizing authority (thresholds unread); fully parallel agent fan-out by default (cost up, quality not).
Spike before building: (1) run 10 John-style tasks at three sizes (about 50, 100, 300 lines) on Sonnet 5.5 and Opus 5.5 and record pass-on-first-check rate, turns and context use, to set the real caps; (2) test whether a planner can emit accurate `files` lists; (3) compare one-commit tasks vs Superpowers right-sizing on a repo where John saw hallucination; (4) read METR raw data for current Claude 80% horizons.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Superpowers writing-plans / subagent-driven-development (task sizing) | https://github.com/obra/superpowers | Task = smallest unit with its own test cycle; fresh subagent per task; no numeric size cap (commit bb92a77) | plugin | 2026-10-16 | Keep the executor, override sizing with an explicit task contract |
| Beads (dependency graph) | https://github.com/steveyegge/beads | `bd ready`, blocks/related/parent-child edges, hierarchical epic IDs (commit dff9492) | CLI (clone read only) | 2026-10-16 | Unchanged: defer until ordering or multi-agent claims bite; tasks.json DAG first |
| Ralph (Huntley) one-item-per-loop | https://github.com/ghuntley/how-to-ralph-wiggum | One task, fresh context, one commit per iteration; plan on disk | bash loop | 2026-10-16 | Use the pattern (not the unbounded loop); outer supervisor owns bounds |
| github/spec-kit tasks template, [P] markers | https://github.com/github/spec-kit | Tasks by user story with [P] parallel flag; docs admit mid-run hallucination on big features | agent slash commands | 2026-10-16 | Copy [P] and phase-scoping ideas only |
| Kiro tasks | https://github.com/kirodotdev/Kiro/issues/2324 | Per-task runs in IDE; "Session Too Long" on large specs | proprietary IDE | 2026-10-16 | Skip (issue evidence) |
| Taskmaster (claude-task-master) | https://github.com/eyaltoledano/claude-task-master | Task generator with complexity analysis and expand tools (commit c0c98d3); thresholds not read | CLI/MCP, clone read only | 2026-10-16 | Not evaluated beyond tool list; skip until thresholds read |
| anthropics/cwc-long-running-agents | https://github.com/anthropics/cwc-long-running-agents | One-feature-per-session scoping, default-FAIL contract, fresh evaluator | Claude Code hooks | 2026-10-16 (README highlights via Exa) | Template candidate, as registry row; README now seen via search highlights |
| METR time-horizon dashboard | https://metr.org/time-horizons/ | 50%/80% horizons per model; frozen 2026-09-08 | web | 2026-10-16 | Evidence source; read raw data in a spike |
