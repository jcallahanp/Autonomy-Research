# Spikes, tracer bullets, set-based design, bounding rules and negative results

Brief: Find how mature teams and agent systems bound feasibility trials (candidates, duration, kill rules) and record failures so they are never retried, to design the engineer's trial protocol.
Run: research/runs/engineer-feasibility/PLAN.md

Existing spike skill read in full (/home/user/Autonomy-Research/plugin/skills/spike/SKILL.md): max 3 parallel spike-workers, user-named paths only, EARS requirement plus one fixed probe, repo-triage first, negative results kept, no time box or kill rule stated. methodology.md has no heading containing "recommend" (grep found none), so it was not used.

## 1. Definitions and practice (spike, tracer bullet, walking skeleton, set-based design)

### Takeaway
The four ideas are different tools: a spike or prototype is disposable and answers one question; tracer code and a walking skeleton are kept and prove end-to-end wiring; set-based design carries several alternatives and eliminates them with recorded reasons. For the engineer, the feasibility trial is a spike (throwaway, one question), and the first build step after it should be a walking skeleton. Confidence: high.

### Cited findings
- Modern spike guidance sets short boxes: spikes "should be time-boxed in short increments (1-3 days)" and "used sparingly" — https://dojoconsortium.org/docs/work-decomposition/spikes/, opened 2026-10-16, WebFetch — Quote: "They should be time-boxed in short increments (1-3 days)."
- Success is a decision, not a document: a spike is judged by whether it ends in proceed, pivot, reduce scope or drop — https://agilesm.net/spike-enabler-story.html, opened 2026-10-16, WebFetch — Quote: "A spike is successful when it leads to a clear choice (proceed, pivot, reduce scope, or drop the approach)"
- Spike write-up must record what was ruled out — same page — Quote: "Record what was tried, what was learned, what constraints were discovered, and what options were ruled in or out."
- Anti-pattern of no box — same page — Quote: "It runs until someone feels finished, so uncertainty expands and decisions drift;"
- Walking skeleton (Cockburn) vs prototype — https://codeclimate.com/legacy/kickstart-your-next-project-with-a-walking-skeleton, opened 2026-10-16, WebFetch — Quote: "tiny implementation of the system that performs a small end-to-end function. It need not use the final architecture, but it should link together the main architectural components."
- Same page: skeleton is kept code — Quote: "it's not a prototype and not a proof of concept — it's production code"
- Tracer bullets (Pragmatic Programmer) — https://flylib.com/books/en/1.315.1.25/1/, opened 2026-10-16, WebFetch — Quote: "Tracer code is not disposable: you write it for keeps." and "Prototyping generates disposable code."
- Set-based design principles (Sobek, Ward, Liker 1999, as summarised in a peer-reviewed review) — the Sloan page itself returned only footnotes to WebFetch. Cambridge review text appeared in Exa results; not opened separately. See Gaps. The Sloan page does confirm the contrast with point-based design — https://sloanreview.mit.edu/article/toyotas-principles-of-setbased-concurrent-engineering/, opened 2026-10-16, WebFetch — Quote: "Toyota considers a broader range of possible designs and delays certain decisions longer than other automotive companies do."
- Riskiest assumption first, one per test, pass line fixed beforehand, feasibility maps to a spike — https://builderscamp.com/guides/other/riskiest-assumption-test, opened 2026-10-16, WebFetch — Quote: "One per test." / "feasibility needs an engineering spike." / "The pass line is set before the test runs."

### Contradictions
- XP original says a week or two per spike (seen in Exa snippet only) vs Dojo 1-3 days vs Baaz 1-2 weeks for third-party integrations (below). Differences are domain, not error; for an agent the box should be set in turns/tokens/wall-clock, not days. Nothing published settles agent-scale boxes.

### Inferences
- (Mine) Spike = disposable, tracer/skeleton = kept; the spike skill's "nothing left in the repo" matches the throwaway rule, so a passing spike should hand the next step a skeleton task, not the spike code.
- (Mine) Set-based design's useful transferable rule is "eliminate infeasible or dominated options and write down why", not "carry many options long".

### Gaps
- Full text of Sobek/Ward/Liker 1999 not read (Sloan page truncated to footnotes; paywall copies). The three principles (map the design space; integrate by intersection; establish feasibility before commitment) were seen only in Exa results from the Cambridge review (https://www.cambridge.org/core/journals/design-science/article/setbased-design-a-review-and-new-directions/DD708BAB57193C6635CA85C7508FE82E) and Doerry/Koenig (PDF unreadable to WebFetch); I did not open them as pages, so they are uncited.
- SAFe enablers page: https://framework.scaledagile.com/enablers returned only a short definition ("supports research, prototyping, and other actions needed to understand customer needs"), no timebox. Spikes page not opened.
- XP spike page (http://www.extremeprogramming.org/rules/spike.html) returned 503 to WebFetch; its "week or two" box is seen only in an Exa result, uncited.
- No source found with a Toyota-reported count of alternatives carried per subsystem.

## 2. Bounding rules (time boxes, candidate counts, kill criteria)

### Takeaway
Practice converges on: one question per spike, box fixed before starting (hours to 3 days for ordinary spikes; 1-2 weeks only for real third-party integrations with access ready), pass line written first, one assumption per test, and an explicit decision at box end even if the answer is "inconclusive". No published data gives an ideal parallel candidate count for feasibility trials; the closest evidence is Anthropic's 3-5 parallel subagents and a paper finding sampling returns diminish below 10. Confidence: medium.

### Cited findings
- Time box and decision — Dojo page above — Quote: "They should be time-boxed in short increments (1-3 days)."
- Batch learning is worse than batching work (supports trial early, not research everything first) — https://dojoconsortium.org/docs/work-decomposition/spikes/, opened 2026-10-16, WebFetch — Quote: "Batching learning is worse than batching other kinds of work"
- Integration spikes run longer but only once access exists — https://baaz.pro/blog/how-to-estimate-api-integration-work, opened 2026-10-16, WebFetch — Quote: "One to two weeks for a team that already has access, environments, and a clear vertical slice."
- Same page: spike is evidence, not scrap code — Quote: "A spike is not a scrappy prototype you throw away by default."
- One assumption per test, pass line first — builderscamp page above — Quote: "One per test." and "The pass line is set before the test runs."
- Anthropic scales effort to complexity and had an overspend failure mode — https://www.anthropic.com/engineering/multi-agent-research-system, opened 2026-10-16, WebFetch — Quote: "Simple fact-finding requires just 1 agent with 3-10 tool calls"
- Anthropic's lead spins up 3-5 parallel workers (seen in Exa result text of the same post; WebFetch excerpt did not return that sentence, so uncited). Same-post cost: "multi-agent systems use about 15× more tokens than chats." (WebFetch quote.)
- Resampling returns diminish fast when the verifier is imperfect — https://arxiv.org/abs/2411.17501, opened 2026-10-16, WebFetch — Quote: "Empirical results show that optimal sampling attempts are often fewer than 10"
- Claude Code docs: after two failed corrections, restart with a better prompt, and test fan-out on 2-3 items first — https://code.claude.com/docs/en/best-practices, opened 2026-10-16, WebFetch — Quote: "After two failed corrections, `/clear` and write a better initial prompt incorporating what you learned."
- Same docs: fan-out gate — Quote: "Refine your prompt based on what goes wrong with the first 2-3 files, then run on the full set."
- Same docs name the unbounded-exploration failure — Quote: "The infinite exploration."

### Contradictions
- Anthropic: most coding tasks are poorly parallelisable (WebFetch quote: "most coding tasks involve fewer truly parallelizable tasks than research") vs Claude Code docs promoting `/batch` across "5 to 30 subagents" in worktrees. Reconciled by task type: batch is for independent, same-shaped edits; a feasibility trial of competing paths is a different shape (independent candidates, one probe), which fits parallel.

### Inferences
- (Mine) Candidate cap of 3 in the current spike skill is consistent with 3-5 parallel workers in Anthropic's design and with sub-10 diminishing returns; no source supports a number above 5 for feasibility trials.
- (Mine) Add to the skill, from the sources above: box in turns and wall-clock per worker (suggest 1 working session or about 60 turns; this number is mine, unvalidated), kill rule "stop at box end and report inconclusive", and "two failed fix attempts on the same blocker = record and stop".
- (Mine) Test the riskiest assumption first, not the most attractive path: order probes so the cheapest probe that could kill a path runs first.

### Gaps
- No published data on candidate counts for human feasibility trials (set-based design literature gives qualitative advice only in what I could open).
- Best-of-N SWE results (Satori-SWE Best@50 vs Best@500) appeared only in Exa results, not opened; uncited.

## 3. Desk research vs real trial

### Takeaway
No formal published heuristic found. Practitioner consensus: documentation is not evidence of behaviour. Trial is required when the claim concerns auth flows, rate limits, webhooks, pagination, error shapes, sandbox-vs-production differences, or anything undocumented; desk research suffices for stable, documented, low-impact facts the team has used before. Confidence: medium (practitioner blogs, not a standard).

### Cited findings
- "Real APIs diverge from documentation" — https://qapractices.com/checklists/third-party-integration-testing-checklist/, opened 2026-10-16, WebFetch — Quote: "Real APIs diverge from documentation. Validate every behavior empirically,"
- Sandbox is not production — https://baaz.pro/blog/how-to-estimate-api-integration-work, opened 2026-10-16, WebFetch — Quote: "Sandboxes that diverge from production teach you the wrong lessons."
- Spike is warranted by uncertainty, with listed triggers — https://agilesm.net/spike-enabler-story.html, opened 2026-10-16, WebFetch — Quote: "A spike is successful when it leads to a clear choice (proceed, pivot, reduce scope, or drop the approach)" (trigger list itself was not captured in a quote; see Gaps).
- Do not trial when the change is cheap to undo: builderscamp page (Exa text only for that passage; WebFetch confirmed "feasibility needs an engineering spike"), so the cheap-and-reversible exception is uncited.

### Contradictions
- None found.

### Inferences
- (Mine) A decision table for the engineer, built from the above: trial required if the claim is (a) behavioural not documented, (b) about auth, rate limit, quota, webhook or pagination, (c) UI-only, with no API, (d) from a sandbox or docs older than the last vendor release, or (e) a go/no-go dependency for the plan. Desk research is enough if documented, versioned, reversible, and cited from the vendor page with a date. Mark each claim in the plan as "documented" or "observed" and only "observed" counts for dependency decisions.
- (Mine) UI-only features cannot be desk-checked at all; the probe is a real browser run and the result is "works on date X with version Y".

### Gaps
- No standard (ISO, NIST, SAFe) heuristic on desk vs trial found.
- Rate-limit and auth probes may need real accounts; the spike skill already stops as "blocked" without credentials, which will make many auth trials end blocked. Needs a decision with John on test accounts.

## 4. Agent-era parallel trials (2025-2026)

### Takeaway
Claude Code supports parallel trials natively via worktrees, `isolation: worktree` subagents and `/batch`; Cursor ships `/best-of-n` (same task, several models, one worktree each, picker not merger). Cost scales roughly linearly with N (about 3x for 3 models; about 15x for multi-agent research). Gains are real for hard or high-stakes work and diminish quickly with N when selection is by weak tests. Confidence: medium-high on mechanics, low on gain magnitudes.

### Cited findings
- Claude Code parallel options — https://code.claude.com/docs/en/best-practices, opened 2026-10-16, WebFetch — Quote: "Run multiple Claude sessions in parallel to speed up development, run isolated experiments, or start complex workflows."
- Fan-out size — same page — Quote: "Run `/batch <instruction>` to have Claude split the change across 5 to 30 subagents."
- Cheap rollback for risky tries — same page — Quote: "Instead of carefully planning every move, you can tell Claude to try something risky. If it doesn't work, rewind and try a different approach."
- Fresh-context reviewer — same page — Quote: "A fresh context improves code review since Claude won't be biased toward code it just wrote."
- Cursor best-of-N — https://cursor.com/docs/configuration/worktrees, opened 2026-10-16, WebFetch — Quote: "`/best-of-n` runs the same task across multiple models at once." and "Try multiple approaches for a hard change"
- Cost of best-of-N (third-party doc mirror, not Cursor) — https://docs.arantic.com/cursor/parallel-agents, opened 2026-10-16, WebFetch — Quote: "Best-of-N multiplies cost by the number of models. Three models on one task is roughly three times the tokens of one run."
- Multi-agent token cost and fit — Anthropic post above — Quote: "multi-agent systems use about 15× more tokens than chats."
- Diminishing returns — arXiv 2411.17501 above — Quote: "Empirical results show that optimal sampling attempts are often fewer than 10"
- Cursor 3 best-of-N reliability complaints (forum, Exa text only; not opened) — uncited; see Gaps.

### Contradictions
- Cursor docs frame best-of-N as comparing models on one task; the spike skill compares different paths with one probe. Not a conflict; different axis. Spike = vary the approach, fix the probe. Best-of-N = vary the model, fix the task.

### Inferences
- (Mine) For the engineer, "N parallel workers" should vary the approach (path) and fix the probe, with a deterministic pass condition, because LLM-judged selection is the weak link (the resampling paper's false-positive point).
- (Mine) Cost control: cap workers at 3, cap turns per worker, and run a cheap desk check first so a path that is dead on paper never costs a worker.
- (Mine) Worktrees isolate files only; they do not isolate network, credentials or installs. The spike skill's `env -i` temp dir covers that and is the right place; sandboxing is another facet.

### Gaps
- Devin, Factory, OpenHands practice on parallel attempts not researched (time). No cost-per-trial data from Claude Code worktree users found.
- Gain magnitude for coding agents (best-of-N on SWE-bench with agents) not verified from an opened source.

## 5. Recording negative results

### Takeaway
Three working formats exist: ADR "Considered Options / Bad, because" (rationale, human-readable), a dated negative-results registry with expectation / what happened / evidence / decision (lab-notebook style), and a machine-checkable ledger (epitaph tombstones with `retry_when`; dsh-negative-ledger with expiring facts). The pattern that stops retries is: record with evidence and a retry condition, and make a pre-flight lookup mandatory in the agent instructions. Confidence: medium (all agent-era tools are young and unvetted).

### Cited findings
- ADR rejected options template — https://adr.github.io/madr/decisions/adr-template.html, opened 2026-10-16, WebFetch — Quote: "Considered Options" and "Bad, because {argument d}"
- Dated registry with four fields, evidence must be a location, "check before re-running" — https://github.com/notque/vexjoy-agent/blob/main/docs/what-didnt-work.md, opened 2026-10-16, Exa web_fetch_exa — Quote: "Negative-results registry. A list of experiments that lost, so the next session skips a known-dead path."
- Same file: field list — Quote: "- **Decision**: rejected | deferred | revisit-if <condition>."
- Same file: evidence discipline — Quote: "Evidence must be a location (`file:line`, eval path, PR #, or `learning.db topic/key`), not a claim."
- Same file also shows a retired auto-capture loop: 74 percent of rows were one-off and injected hints were truncated (author's own measurement; page contains no instructions to agents). Lesson: auto-captured negative memory without recurrence check wasted tokens — Quote: "74% of the corpus (1,849 of 2,490 rows) was one-off."
- Tombstone ledger with refutation condition and pre-flight rule — https://pypi.org/project/epitaph/, opened 2026-10-16, Exa web_fetch_exa (v0.2.0, uploaded 2026-09-05) — Quote: "epitaph is the **repo-scoped attempt ledger**: one JSON file per rejected attempt, committed to the repo, queryable by machine before the retry happens."
- Same page: example record flag — Quote: "--retry-when \"once a fencing token sits in front of the lock\""
- Scratchpad dead-ends section and read-first rule — https://gist.github.com/corpulent/f7fbad0a4d9cdb6a5d4f31d249a2341c, opened 2026-10-16, WebFetch — Quote: "record only approaches that were actually attempted and explain concretely why they failed" and "Before performing any task, read .ai_scratchpad.md."
- Claude Code docs on failed approaches polluting context — best-practices page above — Quote: "the context is cluttered with failed approaches."
- Spike write-ups must say what was ruled out — agilesm page above — Quote: "Record what was tried, what was learned, what constraints were discovered, and what options were ruled in or out."

### Contradictions
- None found. (Two designs differ: epitaph requires human approval to reach "approved"; the scratchpad gist expires on task end. Choose by lifetime: spike negatives about an external tool are long-lived and need a re-test date.)

### Inferences
- (Mine) The current spike skill keeps negatives in `research/spikes/<slug>.md` but has no lookup rule. Add a flat `research/dead-ends.md` (or per-path section) with fields: path, date, version/commit tested, probe, result, evidence (command and output location), `retry-when` condition, and an expiry hint for fast-moving tools. Add a first step to spike, intake and engineer planning: grep that file and the tool registry for the path before dispatching any worker; on a match, state the prior result and require the `retry-when` condition to hold. Do not adopt epitaph or dsh; copy the record shape (both unvetted, v0.x).
- (Mine) Record only attempted failures with evidence, as the gist says; a "rejected on paper" entry should be labelled desk-rejected so it is not treated as observed.
- (Mine) Expiry matters: a tool-version-specific negative result goes stale. Store version tested.

### Gaps
- epitaph and dsh-negative-ledger code not cloned or read; behaviour claims are the READMEs' own. dsh-negative-ledger README seen only in Exa search text; uncited.
- No data on how reliably agents obey a "check first" rule; the vexjoy measurements suggest a hook beats prose.

## Recommendation, alternatives, rejected, spike-first (facet summary)

- Recommendation: keep the spike skill's 3-worker cap and add (1) desk check and dead-end lookup before dispatch, (2) per-worker box in turns and wall-clock with a written kill rule, (3) riskiest-assumption-first probe ordering, (4) a `retry-when` and version field on every negative result, kept in a greppable `research/dead-ends.md`, (5) a rule that dependency decisions need "observed" evidence, not "documented".
- Alternatives: ADR-style Considered Options per decision (heavier); epitaph-like JSON ledger with a hook (more automation, unvetted); best-of-N across models (answers a different question).
- Rejected: carrying many sets of alternatives long-term (set-based design cost without a Toyota-scale team); auto-captured negative memory without recurrence checks (vexjoy retired theirs); LLM-judged winner selection without a deterministic probe.
- Spike before building: whether a `PreToolUse` or `SessionStart` hook that greps dead-ends.md actually changes agent behaviour; what turn box fits one spike-worker; whether test accounts for auth and rate-limit probes can be provided.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| epitaph 0.2.0 | https://pypi.org/project/epitaph/ | Repo-scoped JSON ledger of rejected agent attempts with `retry_when`, `check_nogo` MCP/CLI lookup; pip/pipx install | local, Python >=3.10 | 2026-10-16 (PyPI page only, not installed) | Reference only; copy record shape; v0.x, unvetted |
| dsh-negative-ledger | https://github.com/akslcw/dsh-negative-ledger | Negative-fact ledger for tool-call failures with fingerprint, TTL and block/warn modes | local plugin | not opened (Exa excerpt only) | Reference only; unverified |
| vexjoy-agent what-didnt-work.md | https://github.com/notque/vexjoy-agent/blob/main/docs/what-didnt-work.md | Markdown negative-results registry format | repo file | 2026-10-16 | Copy the four-field format |
| Cursor /best-of-n | https://cursor.com/docs/configuration/worktrees | Same task across several models in separate worktrees | Cursor IDE | 2026-10-16 | Skip (different engine); idea only |
| Claude Code worktrees, /batch | https://code.claude.com/docs/en/best-practices | Parallel isolated sessions and subagents | Claude Code | 2026-10-16 | Use for parallel candidate runs |
| MADR template | https://adr.github.io/madr/decisions/adr-template.html | ADR with Considered Options and pros/cons | markdown | 2026-10-16 | Use for decisions; not for trial logs |
