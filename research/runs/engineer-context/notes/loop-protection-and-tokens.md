# Loop protection and token economy

Brief: How should a long-running coding agent bound its loops (stop conditions, iteration caps, progress checks, circuit breakers, detecting "stuck overnight") and manage tokens (prompt caching, compaction, tool-output trimming, task batch size) without lowering outcome quality?
Run: research/runs/engineer-context/PLAN.md

Recommendation (one): run each overnight task as a `claude -p` call under an outer shell or Agent SDK supervisor that owns the bounds. Use `--max-turns`, `--max-budget-usd` and a wall-clock `timeout` per attempt. Run a file-change and same-error circuit breaker between attempts (copy the frankbria thresholds 3 and 5). Allow two attempts per task, then write a blocked note and move on. Write one terminal status file whatever happens. Do not use the Ralph plugin as the only bound. Alternatives: `/goal` with an in-condition turn clause (interactive or `-p`), Ralph plugin with `--max-iterations` plus `--completion-promise` (both set), frankbria/ralph-claude-code as a reference (not adopted). Rejected: unbounded `max_iterations: 0` loops; `/loop` for overnight; agent teams (about 7x tokens). Spike before building: (1) whether `--max-turns` and `--max-budget-usd` exit codes and `result` subtype are reliable under routines/cloud sessions; (2) a stub supervisor that detects "no git diff in 3 attempts" on a real repo; (3) cache hit rate across sequential `-p` runs in one directory.

## Stop conditions and caps in autonomous-loop systems and what users report

### Takeaway
Every mainstream mechanism has a cap, but several default to no limit: `--max-turns`, `--max-budget-usd`, SDK `maxTurns`/`maxBudgetUsd` and Ralph `max_iterations: 0` are all unbounded unless set. The documented failure reports (6,239 iterations in 11.7 h; 71% of a weekly allowance in one night; 67 empty branches) all trace to an unbounded default plus no progress check. Confidence: high.

### Cited findings
- `--max-turns` has no default limit and is print-mode only — https://code.claude.com/docs/en/cli-reference, opened 2026-10-16, WebFetch — Quote: "Limit the number of agentic turns (print mode only). Exits with an error when the limit is reached. No limit by default."
- `--max-budget-usd` stops on a client-side estimate, can be overshot, counts subagents — https://code.claude.com/docs/en/cli-reference, opened 2026-10-16, WebFetch — Quote: "Spend can pass the cap, so leave headroom."
- SDK: both limits default to none and produce distinct result subtypes — https://code.claude.com/docs/en/agent-sdk/agent-loop, opened 2026-10-16, WebFetch — Quote: "When either limit is hit, the SDK returns a `ResultMessage` with a corresponding error subtype (`error_max_turns` or `error_max_budget_usd`)."
- SDK docs call a budget the default for production agents — https://code.claude.com/docs/en/agent-sdk/agent-loop, opened 2026-10-16, WebFetch — Quote: "Setting a budget is a good default for production agents."
- Budget overshoot is bounded by one response plus running subagents — https://code.claude.com/docs/en/agent-sdk/agent-loop, opened 2026-10-16, WebFetch — Quote: "Spend can therefore pass the cap by up to the cost of that one response, plus anything that subagents still running at that moment spend"
- Ralph plugin zero means infinite, and there is no no-op detection — https://github.com/anthropics/claude-plugins-official/issues/1699 (opened 2026-10-16, WebFetch, issue filed 2026-05-03) — Quote: "One `/ralph-loop` ran **6,239 iterations over ~11.7 hours** before noticed."
- Same issue, on the missing check — https://github.com/anthropics/claude-plugins-official/issues/1699, opened 2026-10-16, WebFetch — Quote: "No-op detection — there is none. Iteration N+1's assistant output can be byte-identical to iteration N's; the loop continues regardless."
- Same issue proposes a non-zero default cap — https://github.com/anthropics/claude-plugins-official/issues/1699, opened 2026-10-16, WebFetch — Quote: "`/ralph-loop` without `--max-iterations` defaults to a non-infinite cap (suggested 1000), with explicit opt-in for unbounded"
- Claude Code Stop hooks have a built-in 8-block override — https://code.claude.com/docs/en/hooks-guide, opened 2026-10-16, WebFetch (saved output, line 1011) — Quote: "Claude Code overrides a Stop hook after it blocks eight times in a row with no tool call from Claude in between."
- `/goal` is a prompt-based Stop hook; the evaluator can judge "impossible"; no-tool-use stalls stop the loop — https://code.claude.com/docs/en/goal, opened 2026-10-16, WebFetch — Quote: "If Claude keeps answering the evaluator without making progress (no tool use for several turns in a row), Claude Code stops the loop, prints a warning"
- `/goal` bounds are written into the condition, not a flag — https://code.claude.com/docs/en/goal, opened 2026-10-16, WebFetch — Quote: "To bound how long a goal runs, include a turn or time clause in the condition, such as `or stop after 20 turns`."
- `/goal` evaluator only sees the transcript — https://code.claude.com/docs/en/goal, opened 2026-10-16, WebFetch — Quote: "It doesn't run commands or read files independently, so write the condition as something Claude's own output can demonstrate."
- Anthropic's own loop guidance: explicit turn caps and pilot first — https://claude.com/blog/getting-started-with-loops, opened 2026-10-16, WebFetch — Quote: "Setting a specific completion criteria and explicit turn caps, “stop after 5 tries.”"
- Headless runs wait on background work up to 10 minutes idle by default — https://code.claude.com/docs/en/headless, opened 2026-10-16, WebFetch — Quote: "stops whatever is still running after 10 minutes of continuous idle waiting by default and drops its partial result."
- Practitioner: unlimited default plus Docker restart-on-failure burned a weekly allowance; fixed by default of 5 — https://www.adrosenfeld.com/blog/2026-02-16-when-your-agent-burns-71-percent-of-your-tokens/, opened 2026-10-16, WebFetch — Quote: "Default `RALPH_MAX_ITERATIONS` from `0` (unlimited) to `5`."
- Same post, headline numbers — https://www.adrosenfeld.com/blog/2026-02-16-when-your-agent-burns-71-percent-of-your-tokens/, opened 2026-10-16, WebFetch — Quote: "67 workspace branches" ... "every single one was empty." (two quoted fragments from the fetch output; 71% of weekly Sonnet-only allowance)
- Practitioner: designed-up-front stop rule was two attempts per ticket — https://yoheinakamura.dev/night-loop-audit/, opened 2026-08 (dated 2026-08-17 on page), read 2026-10-16, WebFetch — Quote: "two attempts per ticket, then stop"
- Ralph origin: one item per loop, context is scarce — https://ghuntley.com/ralph/, opened 2026-10-16, WebFetch — Quote: "One item per loop. I need to repeat myself here—one item per loop."

### Contradictions
- ghuntley frames Ralph as `while :; do cat PROMPT.md | claude-code ; done` with no bound (https://ghuntley.com/ralph/); the Anthropic plugin page and Anthropic's loop blog recommend explicit caps (https://claude.com/blog/getting-started-with-loops). Not a factual conflict: the bound is the operator's job. Settled by treating the cap as mandatory in our supervisor.

### Inferences
- (Mine) The plugin's `max_iterations` guard only counts Stop-hook continuations inside one session, so it cannot cap spend if the session itself restarts (Docker restart in the 71% post). The outer supervisor must own a total-attempt counter in a file outside the container. Rests on: issue 1699, adrosenfeld post.
- (Mine) The three layers need different units: per-attempt (`--max-turns`, `--max-budget-usd`, `timeout`), per-task (2 attempts), per-night (total USD and wall clock). Anthropic's flags cover only the first.

### Gaps
- Issue anthropics/claude-code#18646 (`--max-iterations=3` equals-sign syntax silently ignored, iteration 462 reached) was seen only in a Parallel search excerpt and not opened; not cited.
- https://claude.com/plugins/ralph-loop text and anthropics/claude-code `plugins/ralph-wiggum/hooks/stop-hook.sh` were seen only in search excerpts; not cited. Not cloned.
- Yohei audit quotes "Ticket failures outnumber code failures 4.5 to 1" and "Records cannot be backfilled, only started" appear only in an Exa excerpt of https://yoheinakamura.dev/night-loop-audit/, not in my WebFetch output; not cited.
- Exit code values for `error_max_turns` and `error_max_budget_usd` under `-p`: docs say only "non-zero". Spike.

## Progress signals that detect a stuck run, and who implemented them

### Takeaway
Yes, implemented. frankbria/ralph-claude-code counts consecutive loops with zero changed files (open at 3), consecutive loops with errors (open at 5), and keeps the circuit open until manual reset or a 30-minute cooldown. Others proposed: hash identical outputs (issue 1699), PreToolUse depth counters, task-dedup. Test-count-not-moving and identical-tool-call detection were not found implemented in any opened source. Confidence: medium-high.

### Cited findings
- File-change progress rule and thresholds — https://raw.githubusercontent.com/frankbria/ralph-claude-code/main/lib/circuit_breaker.sh, opened 2026-10-16, WebFetch — Quote: "CB_NO_PROGRESS_THRESHOLD=${CB_NO_PROGRESS_THRESHOLD:-3}"
- Same-error threshold — https://raw.githubusercontent.com/frankbria/ralph-claude-code/main/lib/circuit_breaker.sh, opened 2026-10-16, WebFetch — Quote: "CB_SAME_ERROR_THRESHOLD=${CB_SAME_ERROR_THRESHOLD:-5}"
- The "same error" test is just "has errors this loop", not a hash of the message — https://raw.githubusercontent.com/frankbria/ralph-claude-code/main/lib/circuit_breaker.sh, opened 2026-10-16, WebFetch — Quote: "if [[ "$has_errors" == "true" ]]; then"
- Progress = uncommitted git changes — same file, opened 2026-10-16, WebFetch — Quote: "# Git shows uncommitted changes - clear progress"
- Open state needs cooldown or reset — same file, opened 2026-10-16, WebFetch — Quote: "CB_COOLDOWN_MINUTES=${CB_COOLDOWN_MINUTES:-30}"
- Proposed hash-based no-op detection (3 identical outputs) — https://github.com/anthropics/claude-plugins-official/issues/1699, opened 2026-10-16, WebFetch — Quote: "would have caught my incident at iteration 3 instead of iteration 6,239."
- Claude Code's built-in stall signal: no tool use across several evaluator turns — https://code.claude.com/docs/en/goal, opened 2026-10-16, WebFetch — Quote: "no tool use for several turns in a row"
- Claude Code's `/usage` surfaces per-loop token totals and cache misses — https://code.claude.com/docs/en/costs, opened 2026-10-16, WebFetch — Quote: "a row for each of the heaviest `/loop` or other scheduled tasks that ran recently, ordered by total tokens"
- Anthropic's `stop_hook_active` guard prevents hook-driven infinite continuation — https://code.claude.com/docs/en/hooks-guide, opened 2026-10-16, WebFetch (saved output line 1015) — Quote: "if [ "$(echo "$INPUT" | jq -r '.stop_hook_active')" = "true" ]; then"
- Adrosenfeld: empty branches (git artifacts) were the forensic signal — https://www.adrosenfeld.com/blog/2026-02-16-when-your-agent-burns-71-percent-of-your-tokens/, opened 2026-10-16, WebFetch — Quote: "Stateless restarts compound the problem."

### Contradictions
- None found.

### Inferences
- (Mine) Cheap, deterministic signals for a supervisor: `git diff --stat`/new commit count per attempt; `git rev-parse HEAD` unchanged; SHA-256 of final result text equal across attempts; hash of the last failing test names equal across attempts; `num_turns` and `total_cost_usd` from the `result` JSON. A change in the failing-test set is better "same error" evidence than frankbria's boolean, which can trip on unrelated errors (his own docs list false-positive risk as the reason for two-stage filtering, from search excerpt only, not cited).
- (Mine) Test-count progress is not built anywhere I opened; it is a spike item.

### Gaps
- anthropics/claude-code#54393 (12 overnight coordination bugs, PreCompact state file, hook depth counter) and #47049 (invented "BLOCKED on approval" gate, about 20% weekly quota and about 140 GBP) were seen only as Exa excerpts; not opened, not cited. Worth opening in a follow-up.
- DEV Community post (yurukusa, "108 Hours": "Fix, check, same error" repeated 20 times; CLAUDE.md rule "Retry errors up to 3 times") seen as Exa excerpt only; not cited.

## Anthropic cost control documentation (numbers)

### Takeaway
Cached reads cost 0.1x base input (0.05x on Opus 5.5 and Sonnet 5.5, 0.025x on Fable 5.1 and Mythos 5.1); 5-minute writes 1.25x, 1-hour writes 2x. Claude Code enables caching automatically; the 1-hour TTL is the default only on a subscription within plan usage, otherwise 5 minutes unless set. Enterprise average about 13 USD per developer per active day; no figure is given for unattended loops. Confidence: high.

### Cited findings
- Cache multipliers — https://platform.claude.com/docs/en/build-with-claude/prompt-caching, opened 2026-10-16, WebFetch — Quote: "1-hour cache write tokens are 2 times the base input tokens price"
- Cache read multiplier — same page — Quote: "Cache read tokens are 0.1 times the base input tokens price (see the table footnote for per-model exceptions)"
- Per-model exception for Opus 5.5 and Sonnet 5.5 — same page (as relayed by WebFetch from the table footnote) — Quote: "Cache hits and refreshes ... are priced at 0.05x the base input price."
- 5-minute write — same page — Quote: "5-minute cache write tokens are 1.25 times the base input tokens price"
- Cache refresh and lifetime measured from request start — same page — Quote: "The cache is refreshed for no additional cost each time the cached content is used."
- Minimum cacheable prompt is 512 tokens on the 5.x models — same page, WebFetch summary list (no single quotable line beyond) — Quote: "Shorter prompts cannot be cached, even if marked with `cache_control`."
- Claude Code TTL defaults by billing — https://code.claude.com/docs/en/prompt-caching, opened 2026-10-16, WebFetch — Quote: "Unless you choose a TTL yourself, Claude Code requests the one-hour TTL only on a Claude subscription within your plan's included usage."
- Overriding TTL — same page — Quote: "If you sign in with an API key or use a cloud provider, set `promptCacheTtl` to `1h` to give the main conversation a one-hour cache."
- Cache is per model, so a model switch rebuilds it — same page — Quote: "Each model has its own cache. Switching with `/model` means the next request reads the entire conversation history with no cache hits"
- Cache is scoped to machine and directory — same page — Quote: "In Claude Code, the cache is effectively scoped to one machine and directory."
- Sequential sessions share a prefix only if git status snapshot matches — same page — Quote: "Sequential sessions share the prefix only when the git status snapshot taken at startup matches"
- Compaction while warm is cheap; after a long gap it is a full uncached read — same page — Quote: "After a break longer than the cache lifetime, there is no cache left to read, so the summarization request reprocesses the full history as uncached input."
- Average cost — https://code.claude.com/docs/en/costs, opened 2026-10-16, WebFetch — Quote: "the average cost is around \$13 per developer per active day and \$150-250 per developer per month, with costs remaining below \$30 per active day for 90% of users."
- Agent teams token multiplier — https://code.claude.com/docs/en/costs, opened 2026-10-16, WebFetch — Quote: "Agent teams use approximately 7x more tokens than standard sessions when teammates run in plan mode"
- Thinking is billed as output — same page — Quote: "Thinking tokens are billed as output tokens, and the default budget can be tens of thousands of tokens per request depending on the model."
- Model choice guidance — same page — Quote: "Sonnet handles most coding tasks well and costs less than Opus. Reserve Opus for complex architectural decisions or multi-step reasoning."
- Cost in `-p` JSON output, estimate only — https://code.claude.com/docs/en/headless, opened 2026-10-16, WebFetch — Quote: "Both figures are client-side estimates and can differ from your actual bill."
- Cost fields are not billing data — https://code.claude.com/docs/en/agent-sdk/cost-tracking, opened 2026-10-16, WebFetch — Quote: "Do not bill end users or trigger financial decisions from these fields."
- Auto-compaction threshold on native 1M models — https://code.claude.com/docs/en/model-config, opened 2026-10-16, WebFetch — Quote: "compact before the window fills, at about 967K tokens by default."
- Compaction window settable 100K to 1M via `--autocompact` / `CLAUDE_CODE_AUTO_COMPACT_WINDOW` — same page — Quote: "The command and the flag accept a window size from 100K to 1M tokens"
- Bash output limits — https://code.claude.com/docs/en/tools-reference, opened 2026-10-16, WebFetch (saved output lines 165-176) — Quote: "Inline up to roughly 30,000 characters by default; past that, the path of a file saved to the session directory"
- Failing command output limit — same page — Quote: "Inline up to roughly 10,000 characters; past that, a head-and-tail excerpt of that size"
- Configurable inline ceiling — same page — Quote: "up to 128,000 characters"
- Default Bash timeout and ceiling — same page — Quote: "the default when Claude passes no timeout; two minutes out of the box"
- Idle background token cost — https://code.claude.com/docs/en/costs, opened 2026-10-16, WebFetch — Quote: "These background processes consume a small amount of tokens (typically under \$0.04 per session) even without active interaction."
- Subscription limits, not dollars, bound unattended runs: a usage limit pauses and may auto-continue — https://code.claude.com/docs/en/goal, opened 2026-10-16, WebFetch — Quote: "After three automatic retries, the goal pauses instead."

### Contradictions
- None found. Note one scope mismatch: the costs page says caching reduces cost "automatically", but cache lifetime is 5 minutes for API-key runs unless you set `promptCacheTtl` (same sources). Plan for it, do not assume 1 hour.

### Inferences
- (Mine) For an overnight `-p` supervisor on a Max subscription, the 1-hour TTL applies until plan usage is exhausted, then drops to 5 minutes (prompt-caching page, "drops the main conversation to the five-minute TTL"). If a task's tool calls leave gaps over 5 minutes (long test suites), set `promptCacheTtl=1h` to avoid repeated full-context re-reads.
- (Mine) Per-attempt `--max-budget-usd` is advisory on subscription plans (the Session cost "isn't relevant for billing purposes" for Max, costs page), so the real cap there is the plan window; wall-clock and turn caps matter more.

### Gaps
- No Anthropic figure for token cost of an unattended loop iteration; no published `--max-turns` recommendation number. Anthropic only gives "stop after 5 tries" and "20 turns" as examples.
- Opus 5.5 / Sonnet 5.5 absolute per-token prices not captured (pricing page not opened). Only multipliers.
- Exit code numbers for limits not documented beyond "non-zero".

## Token-reduction practices that hold quality

### Takeaway
Documented practices: clear between tasks, filter test output with a PreToolUse hook, keep CLAUDE.md under 200 lines, delegate verbose work to subagents, one item per loop, specific prompts, sonnet for routine work. I found no controlled measurement of quality effect in any opened source; the only numbers are "tens of thousands of tokens to hundreds" (Anthropic, illustrative) and the 7x agent-team figure. Confidence: medium (practices solid, effect sizes unmeasured).

### Cited findings
- Hook-filtered tool output — https://code.claude.com/docs/en/costs, opened 2026-10-16, WebFetch — Quote: "reducing context from tens of thousands of tokens to hundreds."
- Clear between unrelated tasks — same page — Quote: "Use `/clear` to start fresh when switching to unrelated work. Stale context wastes tokens on every subsequent message."
- CLAUDE.md size — same page — Quote: "Aim to keep CLAUDE.md under 200 lines by including only essentials."
- Subagents isolate verbose output — same page — Quote: "so the verbose output stays in the subagent's context while only a summary returns to your main conversation."
- Specific prompts reduce reads — same page — Quote: "Vague requests like \"improve this codebase\" trigger broad scanning."
- Give verification targets — same page — Quote: "When Claude can verify its own work, it catches issues before you need to request fixes."
- Long sessions cost because history is re-sent every request — same page — Quote: "Claude Code sends your full conversation with every request"
- Compactor can be told what to keep — https://code.claude.com/docs/en/agent-sdk/agent-loop, opened 2026-10-16, WebFetch — Quote: "Persistent rules belong in CLAUDE.md (loaded via `settingSources`) rather than in the initial prompt, because CLAUDE.md content is re-injected on every request."
- `--bare` skips CLAUDE.md, hooks, MCP, plugins for scripted runs (a context-size lever, API key required) — https://code.claude.com/docs/en/headless, opened 2026-10-16, WebFetch — Quote: "`--bare` is the recommended mode for scripted and SDK calls, and will become the default for `-p` in a future release."
- MCP tool definitions deferred by default; CLI tools are lighter — https://code.claude.com/docs/en/costs, opened 2026-10-16, WebFetch — Quote: "Tools like `gh`, `aws`, `gcloud`, and `sentry-cli` are still more context-efficient than MCP servers"
- Fresh context per task: Ralph "one item per loop", about 170k usable window — https://ghuntley.com/ralph/, opened 2026-10-16, WebFetch — Quote: "The name of the game is that you only have approximately 170k of context window to work with."
- Expensive preamble repeated per failed iteration is a measured waste case — https://www.adrosenfeld.com/blog/2026-02-16-when-your-agent-burns-71-percent-of-your-tokens/, opened 2026-10-16, WebFetch — Quote: "Expensive preambles multiply costs."
- Cache the repeated prefix across sequential `-p` calls by running in the same directory — https://code.claude.com/docs/en/prompt-caching, opened 2026-10-16, WebFetch — Quote: "Sessions you run in parallel in the same directory build matching prefixes and read each other's cache."
- `--exclude-dynamic-system-prompt-sections` improves cache reuse across machines for scripted runs — https://code.claude.com/docs/en/cli-reference, opened 2026-10-16, WebFetch — Quote: "Improves prompt-cache reuse across different users and machines running the same task."

### Contradictions
- None found.

### Inferences
- (Mine) Narrow tasks with a fresh `-p` session each (state on disk: git, a progress file, a task list) give both a small context and a restartable unit. The cost is a cold-start re-read each task; cache scoping to directory means sequential `-p` runs in the same repo can read the shared system-prompt and CLAUDE.md prefix if git status matches.
- (Mine) Quality-safe trims: filter passing-test noise, truncate logs, keep failing output whole (Claude Code already keeps failure excerpts to 10k chars). Unsafe trims: dropping the stack trace head, or lowering effort on planning/debug steps (Anthropic ties low effort to "file lookups, listing directories").
- (Mine) No source measured quality versus token cuts, so every trim should be A/B tested with `claude plugin eval`-style runs before being made default.

### Gaps
- No measured quality effect for any trimming practice in an opened source. Search for SWE-bench-style ablations of output truncation was not done.
- Tools like RTK-style output compressors, code-intelligence MCPs, and observation-masking papers were not surveyed (outside the call budget).

## How a run's end state is made known to an absent operator

### Takeaway
Claude Code gives machine-readable termination state (`result.subtype`, `stop_reason`, `num_turns`, `total_cost_usd`, `session_id`, exit code) but not a human-level "done, blocked, or stopped by bound" taxonomy; that has to be our own status file. The one real overnight audit I opened used per-ticket "inbox notes" (one note per human decision) plus a morning Slack digest. Confidence: medium.

### Cited findings
- Result subtype is the primary termination signal — https://code.claude.com/docs/en/agent-sdk/agent-loop, opened 2026-10-16, WebFetch — Quote: "The `subtype` field (available in both SDKs) is the primary way to check termination state."
- All subtypes carry cost, turns and session ID, so a partial run is resumable — same page — Quote: "All result subtypes carry `total_cost_usd`, `usage`, `num_turns`, and `session_id` so you can track cost and resume even after errors."
- The resume path after `error_max_turns` — same page, example comment — Quote: "Agent ran out of turns. Resume with a higher limit."
- Exit code semantics under `-p` — https://code.claude.com/docs/en/headless, opened 2026-10-16, WebFetch — Quote: "Claude Code exits with code 0 on success and a non-zero code when the run fails, so your scripts can branch on the exit status."
- SIGTERM exit code and no result recorded — same page — Quote: "Claude Code exits with code 143. Claude Code leaves the turn that was in progress unfinished and records no result for it."
- A crash yields a zeroed result — https://code.claude.com/docs/en/agent-sdk/cost-tracking, opened 2026-10-16, WebFetch — Quote: "That result may carry zeroed `usage`, `total_cost_usd`, and `modelUsage`, so recover the call's totals from what arrived before it."
- Text output of a long `/goal` looks stuck; use stream-json — https://code.claude.com/docs/en/goal, opened 2026-10-16, WebFetch — Quote: "a goal that runs many turns can look stuck. Add `--output-format stream-json --verbose` to emit each message as the loop runs."
- `/goal` status shows turns evaluated and token spend — same page — Quote: "How many turns have been evaluated"
- Unrecoverable errors clear the goal with a named cause — same page — Quote: "Goal cleared after an unrecoverable error"
- Stop-hook override produces a warning, not a clean stop — https://code.claude.com/docs/en/hooks-guide, opened 2026-10-16, WebFetch — Quote: "then ends the turn with a warning that the Stop hook blocked too many consecutive times."
- Notification hook for pushing to a human — https://code.claude.com/docs/en/hooks-guide, opened 2026-10-16, WebFetch (saved output line 90) — Quote: "This hook uses the `Notification` event, which Claude Code fires when Claude is waiting for input or permission."
- Inbox note = one decision request — https://yoheinakamura.dev/night-loop-audit/, read 2026-10-16, WebFetch — Quote: "1 note = 1 decision request"
- Morning digest by Slack, per-run summary preserved — same page — Quote: "preserves a per-run summary"
- Per-session token cost was not measured in that loop — same page — Quote: "per-run token cost was not measured."

### Contradictions
- None found.

### Inferences
- (Mine) Define exactly four terminal states and write one `RUN_STATUS.json` before exit via a `trap` handler in the supervisor, because SIGTERM and crashes produce no result: `done` (acceptance check script passed), `blocked` (reason + one decision request, mirroring "1 note = 1 decision request"), `stopped_by_bound` (which bound: turns, budget, attempts, wall clock, circuit open), `crashed` (no result seen). Include `session_id` for resume, git HEAD, per-task table, `total_cost_usd` (estimate), and the last circuit-breaker reason.
- (Mine) Pair with a push message (Notification hook, channel, or e-mail) at terminal state only, to avoid the "watchdog logging every 15 seconds forever" failure reported in the dev.to excerpt (not opened).
- (Mine) Done must be script-checked, not self-reported: `/goal`'s evaluator sees only what Claude surfaces (goal page), and Yohei's audit says "The claim outran its evidence" (page; Exa excerpt).

### Gaps
- No opened source documents a Routines or cloud-session way to read `result.subtype`; whether routines expose exit status is untested. Spike.
- Which push channel is least brittle for John (Channels, ntfy, e-mail, GitHub issue comment) is outside this facet.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Ralph Loop plugin (anthropics/claude-plugins-official) | https://claude.com/plugins/ralph-loop | Stop hook re-feeds one prompt until promise text or `--max-iterations`; `max_iterations: 0` is infinite; no no-op detection (issue #1699) | Claude Code plugin | 2026-10-16 (issue opened; plugin page seen in search excerpt) | Fallback only, with both `--max-iterations` and `--completion-promise` set; outer supervisor owns real bounds |
| frankbria/ralph-claude-code | https://github.com/frankbria/ralph-claude-code | Bash Ralph with circuit breaker (3 no-file-change loops, 5 error loops, 30 min cooldown), 100 calls/hour limit, dual-condition exit gate | local shell | 2026-10-16 (`lib/circuit_breaker.sh` opened; not cloned, not run) | Reference design for the breaker; copy thresholds, do not adopt wholesale |
| /goal | https://code.claude.com/docs/en/goal | Session-scoped Stop hook with a small-model evaluator; clears on met, impossible, or unrecoverable error | Claude Code, interactive or `-p` | 2026-10-16 | Use inside one task when the end state is verifiable, with a turn clause; not a bound on its own |
| claude -p --max-turns / --max-budget-usd | https://code.claude.com/docs/en/cli-reference | Per-run turn and estimated-spend caps; error result subtypes | Claude Code CLI | 2026-10-16 | Use on every unattended call; caps are per run and default to none |
| Agent SDK maxTurns / maxBudgetUsd | https://code.claude.com/docs/en/agent-sdk/agent-loop | Same caps plus typed result subtypes, hooks | local/VM | 2026-10-16 | Use if the supervisor is written in Python or TypeScript |
| PreToolUse output-filter hook | https://code.claude.com/docs/en/costs | Rewrites test commands to show failures only | Claude Code hooks | 2026-10-16 | Use, A/B test for quality |
| Prompt cache TTL controls (`promptCacheTtl`, `ENABLE_PROMPT_CACHING_1H`) | https://code.claude.com/docs/en/prompt-caching | 5m or 1h cache for main conversation | Claude Code | 2026-10-16 | Use `1h` when API-key runs have gaps over 5 min |
| Agent teams | https://code.claude.com/docs/en/costs | Parallel Claude instances | Claude Code | 2026-10-16 | Reject for overnight; about 7x tokens |
