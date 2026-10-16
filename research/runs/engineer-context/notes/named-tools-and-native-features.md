# Superpowers, Beads, Ralph and Claude Code native: context and memory

Brief: What Superpowers, Beads, the Ralph Wiggum loop and Claude Code's native features each do for context management, memory across sessions and task tracking, and their documented failure modes.
Run: research/runs/engineer-context/PLAN.md

Repo commits read: superpowers bb92a77 (v7.0.0, 2026-10-09), beads d274841, anthropics/claude-code 03b5892 (plugins/ralph-wiggum). All read 2026-10-16 in a mktemp clone; nothing run.

## Superpowers: which skills touch context, planning and hand-off, what they need from the human, known limits
### Takeaway
Superpowers carries state in files (spec, plan, git-ignored ledger) and in fresh subagent contexts, not in conversation. It gates on human approval at brainstorming and plan-execution choice, then runs without check-ins except four stop cases. Its own text and open issues admit compaction and context-hand-off weaknesses. Confidence: high for the skills, medium for the issues (read from a list page).

### Cited findings
- Brainstorming has a hard gate: nothing is built until the human approves the written design; spec is committed to docs/superpowers/specs. — https://github.com/obra/superpowers skills/brainstorming/SKILL.md:180 (commit bb92a77), read 2026-10-16, git clone + sed — Quote: "Nothing gets built until your human partner approves the full"
- Writing-plans offers two executors (subagent-driven, or native inline) and states the cost of each. — skills/writing-plans/SKILL.md:191 (bb92a77), read 2026-10-16, clone — Quote: "A fresh subagent implements each task and a fresh reviewer checks it before the next one starts"
- Subagents are given crafted context, not the session history, to protect the controller's context. — skills/subagent-driven-development/SKILL.md:10 (bb92a77) — Quote: "They should never inherit your session's context or history"
- The maintainers document the compaction failure and answer it with a ledger file. — skills/subagent-driven-development/SKILL.md:131 (bb92a77) — Quote: "Conversation memory does not survive compaction."
- The ledger is per plan, git-ignored, resumable after compaction; trust it over recollection. — skills/executing-plans/SKILL.md:135 (bb92a77) — Quote: "after compaction, trust the ledger and `git log` over your own"
- Inline execution does not check in; only four stop cases. — skills/executing-plans/SKILL.md:39 (bb92a77) — Quote: "Four things stop you, and only these: an irreversible or destructive"
- Inline execution on a long plan degrades late tasks. — skills/executing-plans/SKILL.md:62 (bb92a77) — Quote: "its later tasks would run on a compacted context."
- A SessionStart hook re-injects the bootstrap on startup, clear and compact. — hooks/hooks.json:5 (bb92a77) — Quote: "\"matcher\": \"startup|clear|compact\","
- Worktree skill is isolation only (detects existing isolation, prefers native tools). — skills/using-git-worktrees/SKILL.md:8 (bb92a77) — Quote: "Ensure work happens in an isolated workspace."
- Open issues (list page, titles only, Oct 2026): #2481 fix rounds exceed the compaction re-attach cut; #2493 plan constraints do not reach the implementer; #2510 agent changed an approved plan despite CLAUDE.md saying wait; #2506 design approval used to skip worktree consent. — https://github.com/obra/superpowers/issues?q=is%3Aissue+compaction+OR+context+OR+skipped, opened 2026-10-16, WebFetch (summarised by fetch model; titles not re-verified individually) — Quote: "never reach the implementer"

### Contradictions
- None found.

### Inferences
- Superpowers is a process layer, not a memory store: its only durable cross-session artifacts are the spec, the plan and the ledger, all plain files. Rests on the lines at executing-plans:135 and brainstorming:180.
- Its human burden is front-loaded (approve design, pick executor, consent to merge/push); after that it is built for unattended runs. A forgotten-document-update guard does not exist in the skills I read; the ledger covers task progress only.

### Gaps
- Issue bodies not opened (only the list page); maintainer replies and fix status unknown.
- No source found for token-cost measurements of subagent-driven mode beyond the skill's own "costs a fresh context per task".

## Beads: what it stores, cross-session use, failure modes, unattended use
### Takeaway
Beads is a Dolt-backed issue graph (dependencies, hash IDs, ready-work query) that the agent reads through the bd CLI at session start (`bd prime`) and writes as it works, replacing markdown TODOs. The README documents no human-in-the-loop requirement; the failure modes are in the issue tracker and recovery docs (stale state, sync, data loss), not in agent behaviour. Confidence: medium-high.

### Cited findings
- Positioning: persistent graph memory for long-horizon work. — https://github.com/steveyegge/beads README.md:15 (commit d274841), read 2026-10-16, clone — Quote: "It replaces messy markdown plans with a dependency-aware graph, allowing agents to handle long-horizon tasks without losing context."
- Agent instruction block: prime, ready, claim, close, remember; forbids markdown TODOs. — README.md:57 (d274841) — Quote: "Do not use markdown TODO lists for task tracking."
- `bd remember` stores project facts that `bd prime` injects later. — README.md:79 (d274841) — Quote: "Store project memory that `bd prime` injects later."
- Atomic claim and hash IDs for multi-agent use. — README.md:62 (d274841) — Quote: "Hash-based IDs (`bd-a1b2`) prevent merge collisions in multi-agent/multi-branch workflows."
- Compaction of old closed issues to save context. — README.md:65 (d274841) — Quote: "Semantic \"memory decay\" summarizes old closed tasks to save context window."
- Documented data-loss incident and a refusal built in response. — docs/recovery/init-safety.md:344 (d274841) — Quote: "the 2026-08-11 fleet-wide data loss."
- Issue tracker, Oct 2026 (list page, 25 of 446 shown): stale derived state, autosync push failures, 503 on proxied server, agent changes recorded as repo owner. — https://github.com/steveyegge/beads/issues?q=is%3Aissue+agent+ignores+OR+forgets+OR+stale, opened 2026-10-16, WebFetch — Quote: "Default actor falls back to git user.name for non-interactive callers, so agent changes are recorded as the repo owner"
- The page found no issue about agents forgetting to use bd (fetch-model statement, not a quote from the page): see Gaps.

### Contradictions
- None found.

### Inferences
- Beads adds what native tasks lack: dependencies, a ready-queue, multi-agent claim and git-synced history. It overlaps with CLAUDE_CODE_TASK_LIST_ID (single-machine shared list) for a single researcher; the registry already says git files suffice for one researcher.
- Adoption relies on the agent obeying the AGENTS.md/CLAUDE.md block; per the memory docs that is "context, not enforced", so a SessionStart hook running `bd prime` is the stronger wiring. Inference from README.md:57 plus native docs below.
- Operating cost is real: a Dolt server, schema migrations and a 446-issue tracker with P1 server bugs suggest an immature ops surface.

### Gaps
- Whether agents skip bd in practice: no user report opened.
- Unattended-run guidance (no human) not found in README; docs/multi-agent not read in full.

## Ralph Wiggum loop: mechanism, stop conditions, documented failures, safeguards
### Takeaway
Ralph is a loop that re-feeds one prompt; state lives in files and git, not the conversation. The Claude Code plugin does it with a Stop hook, with no iteration cap and no promise by default, so runaway is the default. Documented failures: unlimited loops, false completion, spec drift, broken codebase, cost. Users add caps, one-task-per-iteration, BLOCKED/DECIDE exits, sandboxes and deterministic verification. Confidence: high.

### Cited findings
- Original technique: a bash loop, one task per loop, small context. — https://ghuntley.com/ralph/, opened 2026-10-16, WebFetch — Quote: "Ralph is a technique. In its purest form, Ralph is a Bash loop."
- Official plugin: Stop hook feeds the same prompt back. — https://github.com/anthropics/claude-code plugins/ralph-wiggum/README.md:23 (commit 03b5892), read 2026-10-16, clone — Quote: "Stop hook feeds the SAME prompt back"
- Default is unlimited. — README.md:60 (03b5892) — Quote: "`--max-iterations <n>` - Stop after N iterations (default: unlimited)"
- Completion is exact string match, one condition only; cap is the primary safety. — README.md:134 (03b5892) — Quote: "Always rely on `--max-iterations` as your primary safety mechanism."
- Hook removes state and exits at the cap. — hooks/stop-hook.sh:52 (03b5892) — Quote: "Ralph loop: Max iterations ($MAX_ITERATIONS) reached."
- Not for judgment work. — README.md:160 (03b5892) — Quote: "Tasks requiring human judgment or design decisions"
- Real incident: unlimited loop hijacked every reply. — https://dev.to/sean8/i-accidentally-made-claude-ask-itself-the-same-question-1966-times-1c5h, 2026-01-03, opened 2026-10-16, WebFetch — Quote: "Claude attempted this task 1,966 times"
- Stops only on Ctrl-C in the pure form; model drifts when work is done; "done" is unreliable. — https://gist.github.com/accelas/762f7e96e8310b43986581aed73e31be (podcast notes, secondary), opened 2026-10-16, WebFetch — Quote: "It stops when you hit Ctrl-C. That is it."
- Same source on drift and false completion. — same gist — Quote: "When it says it's done, it's not really done."
- Safeguards from a third-party Ralph script (secondary, 2026-04-04): iteration cap default 10, exit codes for COMPLETE/MAX/BLOCKED/DECIDE, one task per iteration, sandbox. — https://ralphloop.sh/blog/ralph-loop-failure-modes/ (seen via Exa search highlights only; page not opened separately, see Gaps)
- Native Claude Code overrides a Stop hook that blocks eight times in a row with no tool call between. — https://code.claude.com/docs/en/hooks-guide, opened 2026-10-16, WebFetch — Quote: "Claude Code overrides a Stop hook after it blocks eight times in a row with no tool call from Claude in between."

### Contradictions
- Plugin README cost claim "One $50k contract completed for $297 in API costs" (README.md:169, 03b5892) vs. the 1,966-iteration incident with zero output; they are different setups (scoped task vs vague prompt with cap 0), not a true conflict, but the cost headline is anecdotal.

### Inferences
- The plugin's in-session loop keeps one growing context (compaction applies), unlike Huntley's restart-per-iteration bash loop; the fresh-context benefit is lost. Rests on README.md:27 ("inside your current session") vs the gist's "restart, don't continue".
- Safe use for the engineer: external `claude -p` loop with a hard cap, one task per iteration from a task file, script-checked completion, branch isolation.

### Gaps
- ralphloop.sh page not opened (only Exa highlights); treat its numbers as unverified.
- No independent cost-per-iteration figures found.

## Claude Code native: CLAUDE.md, auto memory, compaction, hooks, tasks, subagents, plan mode
### Takeaway
Native features already cover: instruction memory (CLAUDE.md, rules), learned memory (auto memory), compaction with defined survivors, hook-based enforcement and re-injection, a session task list shareable by ID, isolated-context subagents with optional persistent memory, and plan mode with a plan file that survives compaction. They do not give a dependency graph, a durable cross-machine ledger, or an iteration loop with verification. Confidence: high (official docs, opened 2026-10-16).

### Cited findings
- Fresh context each session; two carriers. — https://code.claude.com/docs/en/memory, opened 2026-10-16, WebFetch — Quote: "Each Claude Code session begins with a fresh context window."
- Instructions are advisory; hooks enforce. — memory page — Quote: "Claude treats them as context, not enforced configuration. To block an action regardless of what Claude decides, use a PreToolUse hook instead."
- Size guidance. — memory page — Quote: "target under 200 lines per CLAUDE.md file."
- Auto memory loads first 200 lines or 25KB of MEMORY.md and is exempt from the transcript cleanup. — memory page — Quote: "The first 200 lines of `MEMORY.md`, or the first 25KB, whichever comes first, are loaded at the start of every conversation."
- Compaction survivors: root CLAUDE.md, auto memory and plan-mode plan re-injected; skills capped; hook-added context summarised. — https://code.claude.com/docs/en/context-window, opened 2026-10-16, WebFetch — Quote: "Context that hooks added earlier | Summarized with the rest of the conversation"
- Path-scoped rules and nested CLAUDE.md can be lost to compaction. — context-window page — Quote: "compaction summarizes them away with everything else."
- Files re-read after compaction: five, large ones as path only. — context-window page — Quote: "re-reads up to five of the files Claude has read or edited in the session"
- SessionStart with `compact` matcher re-injects critical context. — https://code.claude.com/docs/en/hooks-guide — Quote: "Use a `SessionStart` hook with a `compact` matcher to re-inject critical context after every compaction."
- Task list is per session unless an ID is set. — https://code.claude.com/docs/en/interactive-mode — Quote: "To share a task list across sessions, set `CLAUDE_CODE_TASK_LIST_ID` to use a named directory in `~/.claude/tasks/`"
- Subagents: own context, summary back; persistent memory directory per agent; nesting allowed up to three layers by default. — https://code.claude.com/docs/en/sub-agents, opened 2026-10-16, WebFetch — Quote: "Each subagent runs in its own context window with a custom system prompt, specific tool access, and independent permissions."
- Subagent memory field. — sub-agents page — Quote: "The `memory` field gives the subagent a persistent directory that survives across conversations."
- Plan mode: read-only research, edits blocked until approval. — https://code.claude.com/docs/en/permission-modes — Quote: "Plan mode tells Claude to research and propose changes without making them."
- Plan mode is not enforced under bypass permissions in interactive sessions. — permission-modes page — Quote: "Claude Code also doesn't enforce plan mode's blocks."

### Contradictions
- Task brief assumed subagents cannot spawn subagents; the sub-agents page says nesting is allowed by default (three layers). Registry/other facets that assume flat subagents need checking. Source: https://code.claude.com/docs/en/sub-agents (via fetch model summary, not a verbatim line; verify with a spike).

### Inferences
- Overlap map (mine): Superpowers' ledger = native task list + plan file + git; Superpowers' SessionStart bootstrap = native SessionStart hook; Beads' `bd remember`/`prime` = auto memory + CLAUDE.md; Beads' graph/claim = no native equivalent; Ralph = Stop hook plus loop; native only supplies the eight-block cap, which tool calls reset, so it does not bound Ralph.
- Forgotten document updates are not addressed by any of these as a guarantee; the only enforceable mechanism is a hook (Stop or PreToolUse) that checks for the update. Rests on the memory page's "not enforced" line.

### Gaps
- Fetch-model summaries were used for the interactive-mode and sub-agents pages; exact line wording beyond the quotes above not verified.
- Hooks reference page (Stop output schema) not read in full.

## Comparable systems: one idea each
### Takeaway
Cline contributes a human-readable file bank re-read each session; Aider a ranked, token-budgeted repo map instead of memory; Devin trigger-recalled Knowledge with suggested saves (now moving to Skills); OpenHands always-on repo context plus keyword-triggered skills. All are variations of files-on-disk plus selective loading, which Claude Code already does. Confidence: medium (one fetch each).

### Cited findings
- Cline Memory Bank: structured markdown re-read because memory resets. — https://docs.cline.bot/features/memory-bank, opened 2026-10-16, WebFetch — Quote: "my memory resets completely between sessions"
- Cline file roles. — same — Quote: "Current focus, recent changes, next steps (updates most frequently)"
- Aider repo map: graph-ranked, small budget. — https://aider.chat/docs/repomap.html, opened 2026-10-16, WebFetch — Quote: "The token budget is influenced by the `--map-tokens` switch, which defaults to 1k tokens."
- Devin Knowledge: trigger-based recall, auto-suggested saves. — https://docs.devin.ai/product-guides/knowledge, opened 2026-10-16, WebFetch — Quote: "Devin will retrieve a Knowledge item when its current work is related to the specified triggers."
- Devin deprecation note. — same (fetch-model statement that Knowledge is being migrated to Skills; no verbatim line captured).
- OpenHands: always-on context vs keyword-triggered skills. — https://docs.openhands.dev/openhands/usage/microagents/microagents-overview, opened 2026-10-16, WebFetch — Quote: "activate when a user message contains configured terms."

### Contradictions
- None found.

### Inferences
- Nothing here beats native CLAUDE.md + auto memory + skills for a Claude Code engine; the transferable ideas are Cline's activeContext/progress split (a hand-off file) and Devin's trigger-described entries (matches skill descriptions).

### Gaps
- Playbooks page for Devin not opened; Aider's chat-history summarisation not read.

## Recommendation, alternatives, rejects, spikes (facet-level)
- Recommend: native stack first (root CLAUDE.md under 200 lines, auto memory on, SessionStart `compact` hook, plan-mode plan files, `CLAUDE_CODE_TASK_LIST_ID`), plus Superpowers brainstorming/plan/ledger as the process layer (already pinned at 7.0.0).
- Alternatives: Beads when more than one agent or machine must share a dependency graph; external `claude -p` Ralph loop for verifiable, atomic tasks only.
- Reject: the in-session ralph-loop plugin with default settings (unlimited, same context); Cline/Aider/Devin/OpenHands as engines (Claude Code is fixed).
- Spike before building: (1) a Stop-hook check that blocks finish if a named doc was not updated; (2) Ralph via `claude -p` with cap and script-checked completion on a toy repo; (3) whether Superpowers ledger survives a real compaction on a long plan; (4) subagent nesting depth.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Superpowers | https://github.com/obra/superpowers | Spec/plan/ledger skills, fresh-subagent execution, SessionStart bootstrap; v7.0.0 | plugin | 2026-10-16 | Use as process layer; watch open issues #2481, #2493, #2510 |
| Beads | https://github.com/steveyegge/beads | Dolt issue graph with ready/claim, `bd prime`, `bd remember`; 446 issues open | local CLI + Dolt | 2026-10-16 | Defer; adopt only for multi-agent graph need |
| Ralph Wiggum plugin | https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum | Stop-hook loop, same prompt, default unlimited | Claude Code plugin | 2026-10-16 | Skip as shipped; use an external capped loop |
| Cline Memory Bank | https://docs.cline.bot/features/memory-bank | Markdown memory files re-read each session | Cline | 2026-10-16 | Idea only |
| Aider repo map | https://aider.chat/docs/repomap.html | Graph-ranked repo map, 1k tokens default | Aider | 2026-10-16 | Idea only |
| Devin Knowledge | https://docs.devin.ai/product-guides/knowledge | Trigger-recalled tips; moving to Skills | hosted, paid | 2026-10-16 | Idea only |
| OpenHands skills | https://docs.openhands.dev/openhands/usage/microagents/microagents-overview | Always-on repo context plus keyword skills | OpenHands | 2026-10-16 | Idea only |
