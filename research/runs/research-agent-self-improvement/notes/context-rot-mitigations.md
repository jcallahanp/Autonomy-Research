# Context rot evidence and mitigations for multi-agent Claude Code setups

Brief: Find what current evidence says about context rot and which concrete mitigations a lead-plus-workers Claude Code plugin is still missing, beyond research/findings/context-management.md.
Run: research/runs/research-agent-self-improvement/PLAN.md

Background not re-cited: research/findings/context-management.md already cites Chroma's report (July 2025), Anthropic's context-engineering, multi-agent research and effective-harnesses posts, and the Claude Code docs pages on compaction, hooks, memory, skills and subagents. Only new or correcting items follow.

## What measured evidence exists, from 2025-2026, that quality degrades as context grows, and at what sizes?

### Takeaway
Independent measurements agree that degradation starts far below the advertised window (about 4K to 32K tokens in NoLiMa, an effective length of 4K for Claude 3.5 Sonnet) and persists even with perfect retrieval, so the context-management.md open question "shape for current models is unknown" is only partly answered: there is still no published measurement for Claude 4.5+/5.x. Confidence: medium (all hard numbers are from older or non-Claude models).

### Cited findings
- NoLiMa (ICML 2025, arXiv v3 dated 9 Jul 2025): at 32K, 11 of 13 models fall below 50% of their short-context baseline; Claude 3.5 Sonnet scored 87.5 base, 77.6 at 4K, 61.7 at 8K, 45.7 at 16K, 29.8 at 32K, effective length 4K against a claimed 200K. Reasoning models also fall under 50% of base on NoLiMa-Hard at 32K (o1 99.9 to 31.1). — https://arxiv.org/html/2502.05167v3, opened 2026-10-16, WebFetch
- "Context Length Alone Hurts LLM Performance Despite Perfect Retrieval" (Findings of EMNLP 2025, Nov 2025): across 5 LLMs on math, QA and coding, performance drops 13.9% to 85% as input grows, "well within their claimed context lengths", even when irrelevant tokens are whitespace or masked. Mitigation: have the model recite the retrieved evidence first, turning a long task into a short one; up to +4% for GPT-4o on RULER. — https://aclanthology.org/2025.findings-emnlp.1264/, opened 2026-10-16, WebFetch
- Context Rot Evaluation (arXiv 2605.23170, 22 May 2026): nine non-Claude models at 8K, 32K, 64K; accuracy drops when the task sits mid-context instead of at the end (up to 94pp for Qwen at 64K); of four newer vendor releases three stay within 6pp under one filler type, but middle-position drops of 16 to 56pp persist under another. — https://arxiv.org/html/2605.23170, opened 2026-10-16, WebFetch
- Anthropic, "Harness design for long-running application development" (24 Mar 2026): Sonnet 4.5 showed "context anxiety" (wrapping up prematurely near the believed limit) strongly enough that "compaction alone wasn't sufficient", so the harness used context resets with handoff artifacts; "Opus 4.5 largely removed that behavior", so resets were dropped and one session with automatic compaction was used. The post gives no token thresholds. — https://www.anthropic.com/engineering/harness-design-long-running-apps, opened 2026-10-16, WebFetch
- Anthropic prompting guide: Sonnet 5, Sonnet 4.6 and Haiku 4.5 have context awareness (they track remaining window); in a harness that compacts, tell the model so, or it "may sometimes naturally try to wrap up work as it approaches the context limit". — https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices, opened 2026-10-16, WebFetch (saved to tool-results file, read with grep and sed)

### Contradictions
- NoLiMa and the EMNLP paper show large drops at 4K to 32K; the Context Rot Evaluation finds three of four newer models within 6pp at 64K under one filler type but large drops under another. Different tasks and filler decide it, and none tests Claude 4.5+. A Claude-specific long-context run (needle plus reasoning at 32K, 128K, 500K) would settle it.

### Inferences
- My inference: for a research run the dominant risk is not the 200K-1M ceiling but mid-context facts (an early constraint in a long lead history) being used less reliably; this supports the existing "lead holds little" rule and puts constraints at the end of the context via re-injection rather than only at the start.
- My inference: since the plugin's workers are Sonnet at 40 maxTurns, and context awareness exists on Sonnet-class models, a one-line "your context may be compacted; do not wrap up early; write your note first" is cheap insurance.

### Gaps
- No 2026 measurement of Claude Opus 5.x / Sonnet 5.x quality versus context length was found; Chroma's report is already cited and predates these models. Parallel Search hit its free-tier rate limit on the third search, so coverage of Anthropic's 2026 posts is partial.

## Which Claude Code mechanisms help, and which does the plugin not yet use?

### Takeaway
The plugin already uses a Compact Instructions section, a SessionStart `compact` re-injection of INDEX.md, "re-read PLAN.md and INDEX.md after compaction", explicit worker models and maxTurns. Missing: re-injecting the active run's PLAN.md/status, subagent persistent `memory:`, tool-output trimming hooks, and a worker-side "you may be compacted" instruction. Confidence: medium-high (plugin state read from files; docs from one fetch each).

### Cited findings
- Plugin state (local files, opened 2026-10-16, Bash): plugin/hooks/hooks.json has only SessionStart with matcher `startup|resume|clear|compact`; plugin/hooks/session-start.sh injects the using-research-agent skill body plus `head -n 30 research/findings/INDEX.md`, but not research/runs/<slug>/PLAN.md. CLAUDE.md has a "# Compact instructions" section. Agents: researcher and spike-worker are `model: sonnet`, `effort: medium`, `maxTurns: 40`; synthesizer `inherit`/`high`; verifier `haiku`/`medium`; none set `memory:` or `autoCompactWindow`. — /home/user/Autonomy-Research/plugin/hooks/hooks.json, session-start.sh, plugin/agents/*.md, CLAUDE.md
- Subagent frontmatter `memory` (scopes `user`, `project`, `local`; directories `.claude/agent-memory/<name>/`): the system prompt includes the first 200 lines or 25KB of that agent's MEMORY.md and enables Read/Write/Edit; it has no effect if auto memory is off (`CLAUDE_CODE_DISABLE_AUTO_MEMORY`). — https://code.claude.com/docs/en/sub-agents, opened 2026-10-16, WebFetch
- Subagents support automatic compaction; `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` applies to them; a resumed subagent keeps its full history; a subagent stopped at `maxTurns` returns output marked partial and can be resumed via `SendMessage`. The page says nothing on whether SessionStart hooks fire in subagents or whether CLAUDE.md compact instructions apply there (it states hooks from plugins "all apply inside subagents", naming PreToolUse, PostToolUse, SubagentStart, SubagentStop). — https://code.claude.com/docs/en/sub-agents, opened 2026-10-16, WebFetch
- Claude Code scans each subagent's final report, but the scan "never removes or rewords anything" and does not judge intent; a background subagent result arrives as a completion notification. — same URL, same fetch
- Anthropic's guide recommends, for multi-window work: a different prompt for the first window, a structured `tests.json`, an `init.sh`, and "consider starting with a brand new context window rather than using compaction" because the latest models "are extremely effective at discovering state from the local filesystem", with a prescriptive start ("Review progress.txt, tests.json, and the git logs."). — https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices, opened 2026-10-16, WebFetch
- The same guide warns of subagent overuse and gives a prompt wrap: "Use subagents when tasks can run in parallel, require isolated context, or involve ..." (text truncated in my read of line 931). — same URL

### Contradictions
- context-management.md rec 4 lists the SessionStart `compact` hook as optional; the plugin already ships it. No disagreement, but the optional item is done. Separately, context-management.md says auto memory "isn't loaded into subagents"; the sub-agents page says a subagent with `memory:` loads its own MEMORY.md (200 lines/25KB). These differ in mechanism (parent auto memory versus per-agent memory), not in fact.

### Inferences
- Recommendation 1 (plugin/hooks/session-start.sh): after INDEX.md, also print the most recently modified `research/runs/*/PLAN.md` (first 40 lines) and, if present, a run status file. Reason: `compact`-matcher output is the only documented re-injection that survives compaction; right now a compaction mid-run restores the global index but not the facet list, which CLAUDE.md compact instructions and the skill rule ask the lead to "re-read" (a manual step the compacted model may skip).
- Recommendation 2 (plugin/skills/research/SKILL.md, "What the lead may hold"): add a run ledger line written after each worker returns (facet, status, note path, one-line verdict) so the post-compaction re-read is one small file. The skill's compaction requirement is an EARS line only; a ledger makes it checkable.
- Recommendation 3 (plugin/agents/researcher.md and spike-worker.md): add "Write the note skeleton first, then fill sections; if you notice compaction (a summary replaces your history), re-read the brief and the note file before continuing." Cheap, matches "ASSUME INTERRUPTION" style in the memory tool and Anthropic's wrap-up-early warning for Sonnet-class workers.
- Recommendation 4 (plugin/hooks/hooks.json, new script): PostToolUse `updatedToolOutput` or PreToolUse command rewriting to cap oversized tool results in workers. Already identified in context-management.md rec 15 but not implemented in hooks.json.
- Recommendation 5 (plugin/agents/researcher.md): consider `memory: project` only if cross-run learning is wanted (for example, which sources 403); it adds up to 25KB per worker start, so default off. Low priority.
- Not worth adding: PreCompact (stdout goes to debug log per background doc), the memory tool (API only), `initialPrompt` (main-session agents only).

### Gaps
- Whether the `compact` SessionStart hook fires inside a compacting subagent remains undocumented (page silent). Test in a long worker run.
- The skill-level progressive-disclosure check was not redone; background already covers it.

## How do long-running harnesses keep state across sessions, and does it apply to a research run spanning compactions?

### Takeaway
Yes: the pattern is files plus a prescriptive restart (progress file, structured checklist, git log, init script), and Anthropic's current guidance says a fresh window that rediscovers state from disk can beat compaction. For research this maps to PLAN.md, a status ledger, notes and findings, and git commits per worker note. Confidence: medium-high.

### Cited findings
- Harness-design post (24 Mar 2026): original harness used "structured artifacts to hand off context between sessions"; the later three-agent harness communicated "via files: one agent would write a file, another agent would read it and respond"; a reset "provides a clean slate, at the cost of the handoff artifact having enough state". — https://www.anthropic.com/engineering/harness-design-long-running-apps, opened 2026-10-16, WebFetch
- Prompting guide (see above): `progress.txt`, `tests.json`, `init.sh`, git logs as the restart set; tell the model compaction will occur and to save state before the window refreshes. — https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices, opened 2026-10-16, WebFetch

### Contradictions
- None found. (context-management.md cites the older effective-harnesses post, which agrees; the 2026 post adds that newer models may not need resets.)

### Inferences
- Mapping to the plugin: progress file = run ledger; feature list = PLAN.md facet table with status (JSON-like fixed fields so workers do not rewrite it; the effective-harnesses JSON rationale is in the background file); init script = the SessionStart hook; restart prompt = an explicit "after compaction or /clear: read PLAN.md, ledger, git log -5" line in plugin/skills/using-research-agent/SKILL.md (already injected at every start). Recommendation 6 (plugin/skills/research/SKILL.md): at phase boundaries offer `/clear` plus the restart line rather than waiting for auto-compaction, since a clean window avoids the compaction-summary loss that the next section documents; commit notes to git as they land so `git log` is a second recovery map.
- Recommendation 7 (plugin/skills/research/SKILL.md): for first-window versus later-window difference, the lead's first turn builds PLAN.md and the ledger schema; later turns only update status. Already largely true (PLAN.md before workers); just make the ledger explicit.

### Gaps
- No evidence found on how long a research lead stays reliable (turns or tokens) before a reset beats compaction; Anthropic's post is qualitative.

## What failure modes appear when a lead orchestrates many workers, and what fixes are documented?

### Takeaway
The 2025-2026 literature names the exact failures (lost constraints through compaction, orchestrator omitting context, subagent not reporting constraints, step repetition, not recognising completion), but gives frequencies only for older frameworks and few concrete fixes beyond structure and verification. Confidence: medium.

### Cited findings
- "Model or Harness?" taxonomy (arXiv 2607.28802, stamped 30 Jul 2026): Context Rationale Erosion "occurs when compaction removes information needed later, such as an important constraint"; subagent Delegation Failure "occurs when the orchestrator assigns work with incorrect scope or dependencies"; Communication Failure "occurs when the orchestrator omits necessary context or fails to use the subagent's output", or a subagent fails to report relevant results or constraints. The paper is "descriptive rather than quantitative" and gives no specific fixes. — https://arxiv.org/html/2607.28802v1, opened 2026-10-16, WebFetch (first 100,000 of 229,295 characters read)

### Contradictions
- None found.

### Inferences
- My inference: constraint loss has two entry points in this plugin: (a) the lead's compaction (mitigated by hook and compact instructions) and (b) the lead's dispatch prompt omitting a constraint (not mitigated). Recommendation 8 (plugin/skills/research/SKILL.md and plugin/agents/researcher.md): the dispatch template must carry a fixed "Constraints" block copied verbatim from PLAN.md (free tiers only, date, file paths, schema), and the worker's note must restate it in the first line ("Brief:" already does in note-schema.md) so the synthesizer can diff brief versus note.
- Recommendation 9 (plugin/agents/synthesizer.md and verifier.md): the verifier already re-opens URLs; add a cheap check that each note's "Brief:" line equals the PLAN.md facet brief. This catches orchestrator-side drift by string comparison, no model judgement.
- Recommendation 10 (plugin/skills/research/SKILL.md): workers return only a 10-line summary; the lead's summary-of-summaries is where drift enters. Have the lead copy TAKEAWAYS lines verbatim into the ledger rather than paraphrase them.
- Recommendation 11 (CLAUDE.md): keep the existing rule that the lead keeps one model and effort; add that a worker stopped at maxTurns (partial output) is resumed via SendMessage or re-dispatched with the note path, never silently accepted.

### Gaps
- MAST (arXiv 2503.13657, 14 failure modes, 1600+ traces) and its per-mode frequencies were seen only in search-result excerpts, never opened, so they are not cited. No source with measured fixes for orchestrator summary drift in Claude Code specifically.
- Sub-agents page last 10,964 characters unread.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Parallel Search `web_search` | https://docs.parallel.ai/search/search-mcp | Search with excerpts; returned publish dates for arXiv and Anthropic posts | connector | 2026-10-16 | Use for discovery; free tier rate-limited after two calls in this session |
| WebFetch | https://code.claude.com/docs/en/tools-reference | Pointed-prompt page reads; handled arXiv HTML and Anthropic posts | Claude Code | 2026-10-16 | Use; large pages need offset paging (229k-char paper read in part) |
