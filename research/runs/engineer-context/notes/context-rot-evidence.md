# Evidence on context rot and its mitigations

Brief: Evidence that LLM output quality degrades as context grows (context rot), especially for coding agents and current Claude models, and which mitigations are shown to work.
Run: research/runs/engineer-context/PLAN.md

All sources opened 2026-10-16 (today). Connectors: Parallel web_search worked once, then Parallel web_fetch returned "Too Many Requests"; Exa web_fetch_exa and WebFetch used instead.

## Q1 What do the main studies say about degradation with length, and do any cover agentic coding or 2026 models?

### Takeaway
Degradation with length is well established for single-call tasks (Lost in the Middle 2023, RULER 2024, NoLiMa 2025, Chroma July 2025) and by 2026 there are direct agentic and coding studies, including on Opus 4.6. The agentic evidence is more mixed than the synthetic evidence: it shows sparse, conditional failures (dropped obligations, premature "done"), no universal onset length, and one study blaming step count more than context length. Confidence: medium-high that rot exists, low on any threshold for current Claude models.

### Cited findings
- Lost in the Middle (2023): accuracy depends on where the relevant item sits; worst in the middle — https://arxiv.org/abs/2307.03172, opened 2026-10-16, Exa fetch — Quote: "performance is often highest when relevant information occurs at the beginning or end of the input context, and significantly degrades when models must access relevant information in the middle"
- RULER (2024): near-perfect vanilla NIAH hides large drops; only half of models claiming 32K hold up at 32K — https://arxiv.org/abs/2404.06654, opened 2026-10-16, Exa fetch — Quote: "While these models all claim context sizes of 32K tokens or greater, only half of them can maintain satisfactory performance at the length of 32K."
- NoLiMa (ICML 2025): without literal matches, 13 models drop sharply by 32K, reasoning/CoT does not fix it — https://arxiv.org/abs/2502.05167, opened 2026-10-16, Exa fetch — Quote: "At 32K, for instance, 11 models drop below 50% of their strong short-length baselines."
- Chroma context-rot report (July 2025): 18 LLMs, task complexity held constant, only length varied; includes Claude Sonnet 4 — https://research.trychroma.com/context-rot, opened 2026-10-16, Exa fetch — Quote: "even under these minimal conditions, model performance degrades as input length increases, often in surprising and non-uniform ways."
- Anthropic's Sept 2025 post states the same as a design premise and says it holds for all models, with a gradient not a cliff — https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents, opened 2026-10-16, Exa fetch — Quote: "These factors create a performance gradient rather than a hard cliff: models remain highly capable at longer contexts but may show reduced precision"
- Coding agent, Codex with gpt-5.4-mini (2026, CertiK, arXiv 2607.17937): 10,991-char clean context passes 8/10; 299,140-char contexts pass 3/10, relevant or irrelevant alike — https://arxiv.org/html/2607.17937v2, opened 2026-10-16, Exa fetch — Quote: "a 10,991-character clean context passes 8/10 runs, whereas two 299,140-character contexts—one relevant and one irrelevant—each pass 3/10."
- Same paper: failure is sparse, not global (coverage stays about 93-95% of clean while strict success falls to 37.5%) and agents claim success anyway — same URL — Quote: "In a broader mixed inventory, 38 of 44 failed runs nevertheless end with a success, safe, or completion claim."
- Same paper: no stable onset; effect is conditional on model, task, scaffold — same URL — Quote: "Scale pilots do not identify a stable onset: a failure appears at 90K once but disappears on replay, while 299K remains risky."
- Anthropic Fellows (May 2026, arXiv 2605.12366) tested Opus 4.6 (with thinking) as a transcript monitor: recall falls with prepended benign context — https://arxiv.org/pdf/2605.12366, opened 2026-10-16, Exa fetch — Quote: "Opus 4.6 (with thinking)'s recall drops from 99.7% when such an attack is inserted in a 100K transcript to 69% when the same attack is inserted in an 800K transcript."
- Same paper: position still matters in 2026 models; thinking helps — same URL — Quote: "We observe that in the middle is the hardest point for models to identify the attack and that this effect is stronger on the non-thinking model."
- "How Fast Do Agents Rot?" (Aug 2026, arXiv 2609.01660; nine models, open models plus three unnamed proprietary systems, so no Claude confirmed): step count, not context length, drives decay in an agentic loop — https://arxiv.org/pdf/2609.01660v1, opened 2026-10-16, Exa fetch — Quote: "Degradation is driven by step count rather than context length: bounding the context window steepens decay rather than easing it (logit slope -0.69 vs. -0.44)"
- Claude Code docs, best-practices: Anthropic's own coding-agent guidance rests on degradation — https://code.claude.com/docs/en/best-practices, opened 2026-10-16, Exa fetch — Quote: "Claude's context window fills up fast, and performance degrades as it fills."

### Contradictions
- Step count vs length: Mittal 2026 says decay "is driven by step count rather than context length" (https://arxiv.org/pdf/2609.01660v1); CertiK 2026 finds 299K-char contexts hurt even when the content is irrelevant, and Anthropic Fellows finds recall falls with prepended tokens (https://arxiv.org/html/2607.17937v2, https://arxiv.org/pdf/2605.12366). Different tasks (decision loops vs code audit vs monitoring) and none test a long Claude Code session; the dispute is open. Both agree the practical lever is fewer steps and less carried state, not a hard window cap, since Mittal reports bounding context made decay steeper.
- Vendor vs independent long-context numbers (secondary, aggregator): agenticoding.ai says "Anthropic reports 91.9% @256K where the arena measures 69.1%" (https://agenticoding.ai/effective-context, Exa search highlights; page not fetched). Treat as unverified.

### Inferences
- (mine) For an engineer running hours, the dominant risk is silent omission of earlier obligations plus an unwarranted "done", per CertiK's 38 of 44 failures ending in a completion claim, not obvious gibberish. That argues for external verification (tests, checklists) over trusting the agent's self-check.
- (mine) Because onset is not stable and Mittal ties decay to steps, a session-age or step-count rotation rule is better grounded than a token threshold alone.

### Gaps
- No study found that measures Claude Code itself, or Sonnet 5/Opus 5.x/Fable, on a multi-hour coding task as context grows. CertiK used Codex/gpt-5.4-mini; Anthropic Fellows used Opus 4.6 only as a classifier.
- ContextRotBench (OpenReview id DiZ67nkfay) — https://openreview.net/pdf?id=DiZ67nkfay returned a browser verification screen (WebFetch) and Parallel fetch returned 429; Exa search did not return an open copy. Only a search excerpt seen, so not cited. Spike: find an arXiv copy.
- 2606.29718 and 2602.05892 seen only as search highlights; fetch before citing numbers.

## Q2 What does Anthropic document about context engineering, compaction and windows, and does it give numbers?

### Takeaway
Anthropic documents the mechanism and gives sizes and defaults (windows, thresholds, trigger and keep values) plus two published performance numbers for context editing and memory (39% and 29% on an internal eval). It publishes no per-length quality-loss curve for Claude Code, and no measured loss rate for compaction summaries. Confidence: high on documented defaults, medium on completeness.

### Cited findings
- Context windows page: 1M window for many current models, standard pricing except Haiku 5.5; server-side compaction is the answer when conversations approach the limit — https://platform.claude.com/docs/en/build-with-claude/context-windows, opened 2026-10-16, Exa search highlights (page surfaced by search; content read in the result) — Quote: "If your conversations regularly approach context window limits, use server-side compaction."
- Context editing doc defaults: tool-result clearing triggers at 100,000 input tokens and keeps 3 tool uses — https://platform.claude.com/docs/en/build-with-claude/context-editing, opened 2026-10-16, Exa search result — Quote: "| `trigger` | 100,000 input tokens |"
- Same doc frames editing as quality work, not only cost — same URL — Quote: "context is a finite resource with diminishing returns, and irrelevant content degrades model focus."
- Context editing and memory tool, Sonnet 4.5, Sept 2025 (internal agentic-search eval): 39% combined, 29% editing alone, 84% fewer tokens in a 100-turn web search — https://claude.com/blog/context-management, opened 2026-10-16, Exa search result — Quote: "combining the memory tool with context editing improved performance by 39% over baseline. Context editing alone delivered a 29% improvement."
- Memory tool is file-based, outside the window — same URL — Quote: "store and consult information outside the context window through a file-based system."
- Claude Code compaction behavior, thresholds, re-injection rules (CLAUDE.md, plan, 5 files, 5,000-token skills) are documented in code.claude.com pages that the local findings file opened and quotes; see Q4 for path:line. I re-opened only best-practices myself (Q1).
- Best-practices: verification gates for unattended runs (`/goal`, Stop hook, fresh-subagent refutation) — https://code.claude.com/docs/en/best-practices, opened 2026-10-16, Exa fetch — Quote: "a verification subagent or a dynamic workflow that checks its own findings has a fresh model try to refute the result"
- Sonnet 5 launch (2026-06-30) says Anthropic's own BrowseComp number used a 10M token budget "with compaction and programmatic tool calling" — https://www.anthropic.com/news/claude-sonnet-5, opened 2026-10-16, Exa search result — Quote: "which used a 10M token budget with compaction and programmatic tool calling"

### Contradictions
- None found among Anthropic pages. Vendor-vs-independent MRCR gap noted in Q1.

### Inferences
- (mine) Anthropic's own eval for editing plus memory (39%) is the only published vendor measurement of "state in files plus clearing"; it is agentic search on Sonnet 4.5, not coding on current models.

### Gaps
- No Anthropic number for how much Claude Code compaction loses, or for quality vs tokens on Sonnet 5.5/Opus 5.5. Sonnet 5 system card not opened.
- Pages marked "Exa search result" were read from search highlights, which contained the quoted text; a direct page fetch was not done. Re-open before final publication.

## Q3 Which mitigations have measured effects?

### Takeaway
Measured: (a) a detailed external checklist beat self-check 10/10 vs 5/10 (small n, p=0.0325); (b) compaction plus trimming reduced rot in search agents, with more frequent triggers helping but costing more; (c) reminders in-context helped monitors cheaply but not for subtle cases; (d) context editing plus memory +39% (Anthropic internal). Subagent isolation is model-dependent and one study shows a fresh subagent can itself rot after compaction. No measurement found for "re-read the plan after compaction" as such, nor for files-vs-chat in Claude Code. Confidence: medium.

### Cited findings
- External checklist file restores obligations the agent's self-check forgot — https://arxiv.org/html/2607.17937v2, opened 2026-10-16, Exa fetch — Quote: "A detailed external checklist passes 10/10 runs, compared with 5/10 for a generic self-check (p=0.0325)"
- Same paper: delegation does not make a worker durable; fresh subagent lost an opaque contract after native compaction — same URL — Quote: "after a cleanly verified 2.4M-character load and native compaction, the worker reports losing an opaque contract and produces an exact artifact only by reading prohibited recovery material."
- Same paper, caveat on scope — same URL — Quote: "This single mechanism run is not a threshold estimate"
- Compaction + trimming, isolation, trigger frequency in long-horizon search (open models, June 2026) — https://arxiv.org/html/2606.29718v1, opened 2026-10-16, Exa search result text — Quote: "context isolation using sub-agent calls is highly model-dependent and can outperform other methods when paired with a strong LLM backbone"
- Same: compaction best at removing rot but costly — same URL — Quote: "While context compaction is the most effective at eliminating the rot phenomenon, it significantly increases tool calls and unfinished cases."
- Same: removing all context is not a fix — same URL — Quote: "entirely removing the accumulated context almost completely eliminates the rot phenomenon, but at the cost of a significant increase in unfinished trajectories"
- Reminders and incremental checks (Opus 4.6, GPT-5.4, Gemini 3.1 Pro as monitors) — https://arxiv.org/html/2605.12366, opened 2026-10-16, Exa search result text — Quote: "This is a promising mitigation as it can provide increased detection of some simple attacks almost for free (<3% input token overhead)."
- Same: reminders are not a general fix — same URL — Quote: "this reminder mitigation is effective across most models for the needle style attacks, but not against the more subtle attacks from MonitorBench."
- Thinking helps against rot — same URL — Quote: "Opus 4.6 with extended thinking enabled is much more resistant to this."
- Coding agents as long-context processors: letting an agent grep files instead of reading the text in-window raised results by 17.3% over prior best on five benchmarks (March 2026, arXiv 2603.20432) — https://www.alphaxiv.org/abs/2603.20432, opened 2026-10-16, Exa search result — Quote: "coding agents achieved an average performance improvement of 17.3% over the best previous results."
- Same CertiK paper: selecting a smaller evidence set helps conditionally — https://arxiv.org/html/2607.17937v2 — Quote: "Small scaffold probes suggest that coding agents can also help by selecting a smaller evidence set, but they neither eliminate rot"
- Informal practitioner test on Opus 4.6 1M in Claude Code (single session, not a study): 9 of 10 recall questions passed at 527K, but early exact strings less reliable — https://greghughes.net/claude-evaluating-one-million-token-context-in-the-real-world-2/, opened 2026-10-16, Exa search result — Quote: "Its recall of exact error messages and specific strings from the first quarter of a long session is less reliable."
- Limit tool output: Anthropic cost guidance on hook filtering is in the local findings file (see Q4); I did not measure it.

### Contradictions
- Subagent isolation helps (Anthropic, "only relevant summary returns", via local file line 25; and 2606.29718 for strong backbones) vs it "does not make a worker's own trajectory durable" (CertiK) and "highly model-dependent" (2606.29718). Open: no study of Claude subagents on coding.

### Inferences
- (mine) Files-not-chat is supported indirectly: CertiK's checklist (a file listing obligations) rescued 5 of 10 runs, and Anthropic's memory tool +39%. Direct A/B for Claude Code with a progress file vs none was not found.
- (mine) Re-reading the plan/checklist after compaction is the closest tested mechanism to CertiK's checklist and the Fellows' reminders. It is cheap and has directional support, but is unmeasured for Claude Code. A Stop-hook or verifier checking against the checklist is stronger than asking the agent to reread.
- (mine) Compaction should be treated as lossy: CertiK's worker lost a frozen contract over three compactions; 2606.29718 shows it reduces rot but not without cost. Decisions must live in files so a summary loss is recoverable.

### Gaps
- No measurement of whether Claude Code compaction summaries drop decisions (spike).
- No A/B of session rotation interval, or of tool-output caps, on coding quality.

## Q4 What does the local findings file establish for the research agent, and what transfers to an hours-long engineer?

### Takeaway
It establishes the architecture (thin lead, isolated subagents writing files, CLAUDE.md re-injection, size caps, compact instructions) from documentation, not from measurements of degradation on current models. Most of it transfers to an engineer; the parts that do not are about web-page fetching and per-question findings files. Confidence: high on what the file says.

### Cited findings
- Thesis: context rot precedes token cost; one architecture — /home/user/Autonomy-Research/research/findings/context-management.md:3 — Quote: "A 2-3 hour research run in Claude Code fails on context rot before it fails on tokens"
- Compaction loses early instructions; steering via CLAUDE.md Compact Instructions — context-management.md:11 — Quote: "detailed instructions from early in the conversation may be lost"
- Post-compaction survival rules: CLAUDE.md and plan re-injected, 5 files, skills capped — context-management.md:11 — Quote: "Invoked skill bodies: Re-injected, capped at 5,000 tokens per skill and 25,000 tokens total; oldest dropped first"
- Thrashing stop: auto-compaction stops if context refills repeatedly — context-management.md:11 — Quote: "a file or tool output immediately refilled the context window several times in a row"
- SessionStart hook with `compact` matcher re-injects state; PreCompact cannot add instructions — context-management.md:21 — Quote: "its stdout \"goes to the debug log\", so it cannot add instructions"
- Fresh subagent vs main-context rule and "after two failed corrections, /clear" — context-management.md:49 — Quote: "A clean session with a better prompt almost always outperforms a long session with accumulated corrections"
- Do not rely on Tasks tool or auto memory in all environments — context-management.md:19 — Quote: "On newer models, Claude keeps track of multi-step work without a written checklist"
- Ledger rule: after compaction trust the ledger and git log — context-management.md:102 — Quote: "After compaction, trust the ledger and git log over your own recollection"
- Plugin rule 4 (progress ledger + compact hook) — context-management.md:112 — Quote: "Progress ledger file written after every subagent returns, read first after any compaction"
- Its own stated limit: Chroma predates current models — context-management.md:145 — Quote: "the degradation shape for current models in the 200K-1M range is unknown, so the \"lead holds little\" rule rests on the general finding"
- No measured evidence for structured returns — context-management.md:61 — Quote: "No source quantifies merge quality with vs without a schema"

### Contradictions
- None found against the new sources. The file's line 145 gap ("rests on the general finding") is now partly narrowed by CertiK and Fellows 2026 papers but not closed for Claude coding sessions.

### Inferences
- (mine) Transfers directly: ledger-plus-git as recovery map; Compact Instructions section; SessionStart `compact` re-injection of plan; hooks that truncate verbose tool output; fresh subagent per task with a report-file contract; do not change model or effort mid-run (cache).
- (mine) Transfers with change: an engineer holds code, not fetched pages, so "lead holds only plan and index" becomes "orchestrator holds plan, task ledger and test status; each task (feature) runs in a fresh subagent or a fresh `claude -p` session". Add a deterministic verifier (tests, Stop hook, `/goal`) because CertiK shows self-checks forget obligations; the research file has no equivalent.
- (mine) Does not transfer: per-question findings files, WebFetch/Exa trimming rules (only partly: Bash output caps apply).
- (mine) Missing for a long-running engineer: session rotation rule (steps/age, per Mittal), explicit acceptance-criteria file re-read at each task start (per CertiK), and a check that a compaction did not lose a decision (diff ledger vs summary).

### Gaps
- The file's behavioral claims about compaction survival are documentation quotes from 2026-10-16, not tested in an unattended multi-hour cloud session.

## Q5 What is still unknown (spike list)?

### Takeaway
The central unknowns are Claude-specific and Claude Code-specific. Confidence: high that these are unmeasured in what I found.

### Cited findings
- The only 2026 studies on coding agents used non-Claude models for the agent role (Codex gpt-5.4-mini; open models) — https://arxiv.org/html/2607.17937v2, opened 2026-10-16, Exa fetch — Quote: "The main repeated experiment uses Codex with gpt-5.4-mini"
- CertiK sets the evaluation frame: the conditional distribution, not a threshold — https://arxiv.org/html/2607.17937v2 — Quote: "Context rot should therefore be treated as a conditional reliability distribution over model, task, scaffold, and context—not a single window threshold"

### Contradictions
- None found.

### Inferences
- (mine) Spike list, in priority order:
  1. Run the engineer on a fixed multi-requirement task set (acceptance checklist of 20-30 checks, as in CertiK) at clean vs 150K vs 400K context on the actual target model (Sonnet 5.5 / Opus 5.5), 10 runs each; measure strict pass and requirement coverage. Output: onset for this model and scaffold.
  2. Compaction fidelity: seed decisions in a session, force `/compact` (and auto-compact), then diff decisions in the summary and test recall; compare with and without Compact Instructions and a SessionStart `compact` hook re-injecting the ledger.
  3. Plan re-read A/B: after compaction, with vs without forced re-read of plan/acceptance file; score checklist coverage.
  4. Fresh subagent per task vs one long session, on the same backlog, 5 runs each; measure defects and tokens.
  5. Session rotation: step-count rotation (e.g., 40 vs 100 tool calls) vs token threshold (`CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` / auto-compact window) using Mittal's finding as hypothesis.
  6. Completion honesty: rate of "done" claims with failed checks, with and without a Stop-hook verifier.
  7. Tool-output cap effect (hook that truncates test/log output) on pass rate and tokens.

### Gaps
- ContextRotBench full results (blocked, see Q1). 2603.20432 and 2606.29718 numbers beyond the quoted lines. Sonnet 5 / Opus 5.5 system-card long-context numbers not opened.
- The CertiK quote about "two smaller scale series" appeared in a Parallel search excerpt, which is not a source; omitted from citation.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Parallel Search web_search / web_fetch | https://docs.parallel.ai/search/search-mcp | Search with excerpts; fetch with objective | claude.ai connector | 2026-10-16 | web_search worked; web_fetch returned "Too Many Requests" three times in a row; fall back to Exa |
| Exa web_fetch_exa / web_search_exa | https://exa.ai/docs/reference/exa-mcp | Search with highlights; page fetch to markdown | claude.ai connector | 2026-10-16 | Worked for arXiv, Chroma, Anthropic, code.claude.com; best here |
| WebFetch (built-in) | https://code.claude.com/docs/en/tools-reference | Fetch + summarize with a prompt | Claude Code | 2026-10-16 | Returns paraphrase, not verbatim quotes; OpenReview blocked by a verification screen |
| OpenReview PDF | https://openreview.net/pdf?id=DiZ67nkfay | ContextRotBench host | web | 2026-10-16 | Blocked (browser check); find arXiv copy |
