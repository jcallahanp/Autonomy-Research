# Task tracking across sessions and keeping dependent documents updated

Brief: How should a long-running coding agent track tasks so no work is lost across sessions and compactions, and what makes it reliably update every dependent document when scope changes?
Run: research/runs/engineer-context/PLAN.md

## Task-tracking stores compared (Beads, Claude task list, repo files, GitHub Issues)
### Takeaway
Claude Code's built-in task list is session-scoped by default and optionally shared via a named directory; it is not a durable plan. Durable state must live in files committed to the repo (or Beads), and a SessionStart hook (startup/resume/compact) must re-inject a pointer to it. For one engineer, a JSON feature list plus a progress file plus git is enough; Beads is worth it only when dependency ordering and discovered-work capture matter. Confidence: medium (vendor-side claims for Beads are the vendor's own).

### Cited findings
- Task list is Claude's own checklist, restored on --resume/--continue, and shareable across sessions with a named dir — https://code.claude.com/docs/en/interactive-mode, opened 2026-10-16, WebFetch (saved output) — Quote: "To share a task list across sessions, set `CLAUDE_CODE_TASK_LIST_ID` to use a named directory in `~/.claude/tasks/`"
- Task tools exist (create/get/list/update with dependencies) but availability is model-gated — https://code.claude.com/docs/en/tools-reference, opened 2026-10-16, WebFetch — Quote: "`TaskUpdate` | Updates task status, dependencies, details, or deletes tasks."
- Task tools are default only on listed models; others must opt in — https://code.claude.com/docs/en/tools-reference, opened 2026-10-16, WebFetch — Quote: "available by default only on Opus 4.7, Sonnet 4.6, Haiku 4.5, and earlier models"
- Compaction summary keeps "pending tasks" only as prose; the exact conversation is gone — https://code.claude.com/docs/en/context-window, opened 2026-10-16, WebFetch (saved output) — Quote: "The summary keeps: your requests and intent, key technical concepts, files examined or modified with important code snippets, errors and how they were fixed, pending tasks, and current work."
- Anthropic's long-running harness: JSON feature list edited only via a passes field, progress file, git commits — https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents, opened 2026-10-16, WebFetch — Quote: "edit this file only by changing the status of a passes field" (page also says tests must not be removed or edited)
- Beads: dependency-aware graph, ready query, atomic claim, Dolt storage with JSONL as export only — https://github.com/steveyegge/beads, opened 2026-10-16, WebFetch — Quote: "It replaces messy markdown plans with a dependency-aware graph, allowing agents to handle long-horizon tasks without losing context."
- Beads README tells agents to avoid markdown TODOs and use claim — https://github.com/gastownhall/beads (clone commit d274841) README.md:57, read 2026-10-16, grep — Quote: "Do not use markdown TODO lists for task tracking."
- Beads Claude Code integration uses a SessionStart hook that also fires after compaction; no PreCompact hook needed — beads clone docs/integrations/claude-code.md:49 (commit d274841), read 2026-10-16, sed — Quote: "No `PreCompact` hook is needed - SessionStart fires again after compaction."
- Beads' own comparison with GitHub Issues (vendor claim): GH has no ready-work concept and is cloud-first — beads clone docs/reference/faq.md:20 (commit d274841), read 2026-10-16, sed — Quote: "No built-in \"ready\" concept; requires custom GraphQL plus a sync service"
- Beads concedes GitHub Issues suit human teams and can coexist — beads clone docs/reference/faq.md:25 (commit d274841), read 2026-10-16 — Quote: "GitHub Issues and Jira excel for human teams working in a web UI with cross-repo dashboards and integrations."

### Contradictions
- None found on mechanics. Beads' README says JSONL "is an export ... not the source of truth", while a Beads discussion (search excerpt only, not opened) described it as "JSONL files + SQLite cache"; the README is newer (Dolt), so older write-ups are stale on storage.

### Inferences
- (mine) Cost to the agent: TaskCreate/Update is near zero but non-durable; JSON feature file costs one edit per task and one git commit; Beads costs a CLI install, a SessionStart hook and discipline to write notes; GitHub Issues costs network, auth and `gh` calls per update. Rests on the findings above.
- (mine) Do not rely on the task list as the plan: it is model-gated, and compaction summarises pending tasks as prose.

### Gaps
- No measured comparison of Beads vs plain files on task loss; only vendor claims and anecdotes found.
- Whether Task tools are on by default for the engine's model (Sonnet 5.5 / later) is not stated on the page quoted; test with `CLAUDE_CODE_ENABLE_TASKS`.
- https://github.com/boshu2/agentops/blob/HEAD/skills/beads/references/WORKFLOWS.md — 404 on WebFetch; search excerpt not cited.
- https://github.com/gastownhall/beads/blob/main/docs/FAQ.md — 404.

## Mechanisms that force document updates (hooks, CI, definition of done, ADRs, audit pass)
### Takeaway
Instructions in CLAUDE.md are advisory; only a Stop hook (command type, exit 2) or CI gate guarantees a doc step. Evidence of effect is mostly anecdotal. Best design: a Stop hook that blocks when code or scope files changed without the manifest of dependent docs being touched or explicitly waived, plus a fresh-context reviewer subagent pass against the plan, plus a CI check as backstop. Confidence: medium.

### Cited findings
- CLAUDE.md is context, not enforcement; use hooks for must-happen rules — https://code.claude.com/docs/en/memory, opened 2026-10-16, WebFetch (saved output) — Quote: "Claude treats them as context, not enforced configuration."
- Hooks are deterministic — https://code.claude.com/docs/en/best-practices, opened 2026-10-16, WebFetch — Quote: "Unlike CLAUDE.md instructions which are advisory, hooks are deterministic and guarantee the action happens."
- Stop hook as gate for unattended runs — best-practices — Quote: "The `/goal` and Stop hook versions are what let an unattended run finish correctly without you."
- Stop hooks are capped: overridden after eight consecutive blocks; must check stop_hook_active — https://code.claude.com/docs/en/hooks-guide, opened 2026-10-16, WebFetch (saved output) — Quote: "Claude Code overrides a Stop hook after it blocks eight times in a row with no tool call from Claude in between."
- TaskCompleted hook can refuse completion; TaskCreated can roll back — https://code.claude.com/docs/en/hooks, opened 2026-10-16, WebFetch — Quote: "Prevents the task from being marked as completed."
- Agent-type hooks verify against real state — hooks-guide — Quote: "When verification requires inspecting files or running commands, use `type: \"agent\"` hooks." (agent hooks marked experimental)
- Adversarial fresh-context review against the plan — best-practices — Quote: "Use a subagent to review the rate limiter diff against PLAN.md. Check that every requirement is implemented"
- Docs gate example: Stop hook blocks a turn that changed code but not docs/, with loop guard; author's own claim, no baseline — https://github.com/viditparashar96/eng-skills, opened 2026-10-16, WebFetch — Quote: "you cannot end a turn that changed source code without documenting it" (page also: "Supersede — never delete — old decisions"; 0 stars, effect anecdotal)
- Real-world pitfall: Stop hook JSON decision:block did not block on one installed version; exit 2 did; session marker prevents loops — https://github.com/dgalarza/claude-code-workflows/pull/36, opened 2026-10-16, WebFetch — Quote: "the JSON payload is parsed without error but the Stop proceeds anyway"
- Anthropic maintainer endorsed the Stop hook as the supported evidence gate (issue closed) — https://github.com/anthropics/claude-code/issues/75720, opened 2026-10-16, WebFetch — Quote: "There is a supported way to do this today: a `Stop` hook."
- Spec amendment workflow: propagation checklist blocks resume until each flagged artifact is updated or waived; but design artifacts are not auto-propagated — https://microsoft.github.io/devsquad-copilot/concepts/spec-amendment/, opened 2026-10-16, WebFetch — Quote: "The coordinator blocks resume until each flagged artifact is either updated (via `devsquad.plan`) or explicitly waived."
- Same-PR rule plus reviewer, because agents skip update instructions — https://specstory.com/learning/ai-coding/spec-drift, opened 2026-10-16, WebFetch — Quote: "An agent can still skip an instruction to update the spec."
- Tests can hide drift when edited to match code — specstory page (search excerpt of same page; fetch returned only the three quotes above) — not quoted, see Gaps.
- ADR basics only: adr.github.io page does not cover supersession or tooling placement — https://adr.github.io/, opened 2026-10-16, WebFetch — Quote: "captures a single AD and its rationale" (supersession claim comes only from eng-skills above)
- OpenSpec per-change folder (proposal, specs, design, tasks), MIT — https://github.com/Fission-AI/OpenSpec, opened 2026-10-16, WebFetch — Quote: "tasks.md — implementation checklist" (merge mechanics of archive not explained on the page)

### Contradictions
- Hooks docs say Stop can block via JSON decision or exit 2 (https://code.claude.com/docs/en/hooks); the doc-sentinel PR reports only exit 2 blocked on its installed version (PR #36, 2026-04). Settle by a spike on the engine's current version.

### Inferences
- (mine) A doc manifest file (e.g. docs/DEPENDENTS.md mapping "scope change" to plan, architecture, diagrams, decisions) lets a command Stop hook check mtimes or git diff mechanically; the model then only writes content. This is my design, not found as a tested pattern.
- (mine) A Stop hook can check only that files were touched, not that content is right; hence the fresh-context reviewer subagent pass is needed as well.
- (mine) Safety valve required: the 8-block cap and stop_hook_active mean a hook can fail open silently; log when it fails open.

### Gaps
- No controlled evidence that any doc-staleness hook reduces drift; only author claims.
- Docs-as-code CI (link checkers, doc linters, OpenAPI diff, "docs or it didn't happen" rules) were not opened this session; no cited findings. The Exa-surfaced developertoolkit.ai plan.md CI snippet was seen only as a search excerpt.
- ADR supersession tooling (adr-tools, log4brains) not verified.
- Parallel Search returned "Too Many Requests" on both calls; Exa used instead.

## Anthropic docs on resume, memory files, SessionStart
### Takeaway
A resumed session restores conversation history, model and permission mode, but not all launch flags; compaction re-injects project-root CLAUDE.md and auto memory from disk and runs SessionStart hooks with the compact matcher. So the reliable resume contract is: state files in the repo, a short CLAUDE.md pointer, and a SessionStart hook that prints the current task and plan status. Confidence: high.

### Cited findings
- Fresh context each session; two carry-over mechanisms — https://code.claude.com/docs/en/memory, opened 2026-10-16 — Quote: "Each Claude Code session begins with a fresh context window."
- CLAUDE.md size guidance — memory — Quote: "target under 200 lines per CLAUDE.md file"
- Auto memory loads first 200 lines or 25KB — memory — Quote: "The first 200 lines of `MEMORY.md`, or the first 25KB, whichever comes first, are loaded at the start of every conversation."
- Compaction table: root CLAUDE.md and auto memory re-injected; context hooks added earlier are summarised; compact-matched SessionStart hooks re-run — https://code.claude.com/docs/en/context-window, opened 2026-10-16 — Quote: "SessionStart hooks that match the `compact` source | Claude Code runs them and adds their output to the compacted context"
- Context added by earlier hooks is lost — context-window — Quote: "Context that hooks added earlier | Summarized with the rest of the conversation"
- SessionStart matchers include resume and compact — https://code.claude.com/docs/en/hooks, opened 2026-10-16 — Quote: "`resume` is \"`--resume`, `--continue`, or `/resume`\"" (page lists `compact` as "Auto or manual compaction")
- Re-inject recipe, dynamic output allowed — hooks-guide — Quote: "Use a `SessionStart` hook with a `compact` matcher to re-inject critical context after every compaction."
- Resume restores history, model, permission mode, active goal, unexpired scheduled tasks; not some flags — https://code.claude.com/docs/en/sessions, opened 2026-10-16 — Quote: "Not every configuration flag from the original launch is restored."
- Bypass mode is not restored on terminal resume — sessions — Quote: "The permission mode a new session would start in." (row for sessions that ended in bypassPermissions)
- Retention and storage — sessions — Quote: "Change the 30-day retention" (cleanupPeriodDays); transcripts at ~/.claude/projects
- claude -p sessions are hidden from the picker and --continue — sessions — Quote: "Claude Code leaves sessions created with [`claude -p`](/docs/en/headless) or the [Agent SDK](/docs/en/agent-sdk/overview) out of the session picker and out of `claude --continue`."
- Interrupted tool calls are not re-run on resume — sessions — Quote: "A tool that was still running when the previous process ended, for example in a crash, doesn't finish or run again when you resume."
- Resuming an idle large session can trigger a summary dialog — sessions — Quote: "Resume from summary: runs [`/compact`](/docs/en/context-window#what-survives-compaction) immediately."
- Spec then fresh session — best-practices — Quote: "Once the spec is complete, start a fresh session to execute it."
- Anthropic's harness pattern: progress file for next session — effective-harnesses page — Quote: "claude-progress.txt file that keeps a log of what agents have done" (page text; verbatim fragment from fetch summary)

### Contradictions
- None found.

### Inferences
- (mine) Unattended loops should use `claude --resume <name>` with names, not --continue, because -p sessions are skipped by --continue.
- (mine) Do not rely on hook-injected context persisting; re-inject from files via the compact SessionStart hook each time.

### Gaps
- Behaviour of resume plus the Task list when CLAUDE_CODE_TASK_LIST_ID is unset in cloud sessions not tested.
- The Stop section of the hooks page was truncated in WebFetch (page 270k chars); stop_hook_active field confirmed via hooks-guide instead.

## Failure patterns and fixes
### Takeaway
Documented failures: false "done" claims without evidence (worse after compaction and with shared state files), agents skipping instructions to update specs, and tests edited to match drifted code. Fixes applied: Stop/TaskCompleted gates running real checks, evidence-in-report requirements, fresh-context review, spec-in-same-PR, and amendment flows with propagation checklists. Confidence: medium (issue reports are anecdotal).

### Cited findings
- User report: tasks marked done without testing despite CLAUDE.md and hooks saying not to — https://github.com/anthropics/claude-code/issues/60177, opened 2026-10-16, WebFetch — Quote: "Worse in long sessions (after compaction)" (also: closed as not planned by stale bot; reporter's observation, not measured)
- Earlier similar report: tasks marked complete without implementation — https://github.com/anthropics/claude-code/issues/14947 — seen only as search excerpt; not cited (see Gaps).
- Issue 75720 title describes the failure and the maintainer's fix is the Stop hook — see above — Quote: "an `agent`-type Stop hook spawns a subagent that can read files, run tests, and inspect the working tree before deciding"
- Maintainer's caveat: a model judging a model shares blind spots; passing tests is not proof of live — issue 75720 fetch (paraphrased in fetch result, not a verbatim page quote) — see Gaps.
- Anthropic harness names the failure modes — effective-harnesses page — Quote: "Claude marks features as done prematurely."
- Spec drift sequence ends with agent editing code without opening spec — specstory — Quote: "the agent edits the code without opening the spec"
- Fix: evidence over assertion — best-practices — Quote: "Have Claude show evidence rather than asserting success: the test output, the command it ran and what it returned, or a screenshot of the result."
- Reviewer over-reporting risk — best-practices — Quote: "A reviewer prompted to find gaps will usually report some, even when the work is sound"
- Duplicate tasks after compaction: Claude Code reminds the model of running background work to avoid duplicates (docs); no source found for duplicated task-list entries — context-window — Quote: "Claude Code reminds Claude which ones are still running so it doesn't start a duplicate"

### Contradictions
- None found.

### Inferences
- (mine) Task done must be defined as a command with an exit code (test, build, link check, doc manifest check) recorded in the task record, enforced by TaskCompleted or Stop hooks; an LLM judge is a supplement only.
- (mine) Having a second hook or session edit CLAUDE.md or hooks is a risk (issue 60177 claims the agent edited its own config); protect .claude/ with a PreToolUse deny or ConfigChange hook. Reporter claim only.

### Gaps
- No source found for duplicated tasks specifically after compaction with Beads or the Task list.
- Issues 14947 and 68154/72186 not opened.

## Recommendation, alternatives, rejected, spikes
(mine; rests on the findings above)
- Recommend: repo-resident state. `tasks.json` (id, status, evidence_command, evidence_result, depends_on), `PROGRESS.md`, `docs/DEPENDENTS.md` manifest, ADRs with supersession, committed every step. A SessionStart hook (startup, resume, compact matchers) prints open tasks and last progress. A TaskCompleted/Stop command hook runs the evidence command and the doc-manifest check, with a stop_hook_active guard and fail-open logging. A fresh-context reviewer subagent compares diff against plan before the final stop.
- Alternatives: Beads (graph, ready, discovered-from; use if tasks exceed ~50 or dependency ordering bites); Claude native task list with CLAUDE_CODE_TASK_LIST_ID as the in-session view only; GitHub Issues as a human mirror.
- Rejected: native task list as sole store (model-gated, session-scoped); CLAUDE.md instructions alone (advisory); LLM-only completion judge (shared blind spots); eng-skills as an installed dependency (unproven, 0 stars; copy the idea only).
- Spike before building: (1) Stop hook exit 2 vs JSON block on the engine's current version; (2) hook behaviour under claude -p and cloud/routines; (3) whether Task tools are on for the engine model; (4) beads vs tasks.json task-loss test over 3 forced compactions; (5) doc-manifest false-positive rate.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Beads (re-check) | https://github.com/steveyegge/beads | Dolt dependency-graph tracker; SessionStart prime hook; README says no markdown TODOs | local CLI | 2026-10-16 (clone d274841) | Alternative; adopt only if tasks.json proves too weak |
| Claude Code task list (TaskCreate etc.) | https://code.claude.com/docs/en/tools-reference | In-session checklist, named dir sharing, model-gated | Claude Code | 2026-10-16 | Use as in-session view only |
| TaskCompleted / Stop hooks | https://code.claude.com/docs/en/hooks | Block completion on exit 2 | Claude Code | 2026-10-16 | Use: core gate |
| SessionStart hook (compact/resume) | https://code.claude.com/docs/en/hooks-guide | Re-inject state after compaction/resume | Claude Code | 2026-10-16 | Use |
| eng-skills | https://github.com/viditparashar96/eng-skills | Stop-gate blocking code change without docs change; ADR commands | Claude Code hooks (npm) | 2026-10-16 (page only, not installed) | Reference only; unproven |
| doc-sentinel (dgalarza) | https://github.com/dgalarza/claude-code-workflows/pull/36 | Stop hook auto-dispatching drift-resolver | Claude Code plugin | 2026-10-16 (PR page only) | Reference only; useful pitfalls |
| DevSquad spec amendment | https://microsoft.github.io/devsquad-copilot/concepts/spec-amendment/ | Drift flag, propagation checklist, Spec Evolution Log | Copilot framework | 2026-10-16 | Borrow checklist idea; skip tool |
| OpenSpec | https://github.com/Fission-AI/OpenSpec | Per-change proposal/specs/design/tasks, MIT | npm CLI | 2026-10-16 | Fallback spec framework |
