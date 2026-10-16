# Open questions

Things the evidence could not settle. Each findings file keeps its own detailed list; this is
the cross-cutting set.

## For John
- [ ] Monthly budget for paid API keys? Default until answered: free tiers only.
- [ ] Which deployment targets matter first for the later engineer project: Docker, Vercel, Cloudflare, Android?

## To measure in a cloud session
- [ ] Claude Code's compaction trigger percentage and buffer are unpublished; measure with `/context` before and after auto-compaction.
- [ ] Do plugin-shaped folders under `.claude/skills/` and symlinked `.claude/skills -> ../skills` load in cloud sessions? Fallback is a sync script.
- [ ] Can a hook or skill reliably detect that a claude.ai connector (Exa, Parallel, Context7, Mermaid Chart) is missing? Tool-name probing is an inferred pattern.
- [ ] Does `maxTurns` count tool calls one-to-one (needed to map a 10-15 call budget onto a turn cap)?
- [ ] Do structured return schemas measurably improve merge quality? Run an A/B on two questions with and without `_FORMAT.md`.
- [ ] Real cost of the proposed `/self-test` fast suite (8 cases x 3 runs x 2 arms plus judge calls).
- [ ] Does `claude plugin eval --runs 3` override a case's `runs: 1` frontmatter, or the reverse? The `self-improve` paired re-measure assumes the flag wins; check the run counts in the JSON.
- [ ] Rate limits for Parallel, Exa (keyless) and DeepWiki are undocumented; how many calls does one research run need?
- [ ] Who owns the Exa connector account and its $10/month free credit?

## Evidence gaps
- [ ] No context-rot measurement exists for Fable, Opus 5 or Sonnet 5; the "lead holds little" rule rests on Claude 4-era data.
- [ ] No published benchmark for depth-first "how do these two systems integrate" research; the 90.2% multi-agent gain is for breadth-first queries.
- [ ] No measurement of LLM comprehension of diagrams versus prose at equal token count.
- [ ] Whether Claude Code's bundled `/deep-research` workflow can be invoked from a plugin skill or only by the user.
- [ ] Does the Mermaid Chart connector render experimental `C4Context` syntax reliably? Stay on `flowchart` until checked.
- [ ] Do `TaskCreate`/`TaskList` entries persist across sessions on any surface? Docs call them session todos.

## From research-agent-self-improvement
- [ ] Does a `compact` SessionStart hook fire inside a subagent that auto-compacts? Undocumented. (source: research-agent-self-improvement, 2026-10-16)
- [ ] How many runs per case does an LLM-judged research report need? No opened source gives a number. (source: research-agent-self-improvement, 2026-10-16)
- [ ] What effect sizes do quote-first extraction alone, and the Citations API against prompting, produce? Only the vendor's qualitative statement exists. (source: research-agent-self-improvement, 2026-10-16)
- [ ] Is Haiku an adequate claim-support judge for the verifier? Untested; DRB II judge-human agreement is unverified because its paper was not opened. (source: research-agent-self-improvement, 2026-10-16)
- [ ] Which figure is right for Gemini Deep Research citation accuracy: 50.3% (DeepTRACE Table 1) or 40.3% (its text)? (source: research-agent-self-improvement, 2026-10-16)
- [ ] Is the DeepResearch Bench license Apache-2.0 or MIT? The page shows both. (source: research-agent-self-improvement, 2026-10-16)
- [ ] What minimum effect size or significance test should a prompt edit need before it is accepted? The 0.2 margin, 3-round cap and 20%/minimum-5 sample are unsourced worker choices. (source: research-agent-self-improvement, 2026-10-16)
- [ ] Do self-edited prompts game LLM-judge graders? Not studied; DGM's gamed detector is the only example seen. (source: research-agent-self-improvement, 2026-10-16)
- [ ] Has the verifier ever run on real content? It has not. (source: research-agent-self-improvement, 2026-10-16)
- [ ] How did the lead behave inside passing eval cases? Per-run eval traces and HTML reports have not been read. (source: research-agent-self-improvement, 2026-10-16)
- [ ] Does `claude plugin eval` consume a free plan's usage? (source: research-agent-self-improvement, 2026-10-16)
- [ ] Can GEPA or DSPy run on any free hosted LM? (source: research-agent-self-improvement, 2026-10-16)
- [ ] Do agent `tools` allow-lists with `mcp__plugin_research-agent_*` names work in a live session? (source: research-agent-self-improvement, 2026-10-16)
- [ ] How often does the lead misroute a one-fact question into a multi-facet run? (source: research-agent-self-improvement, 2026-10-16)
- [ ] What is the smallest holdout size that is meaningful for prompt evaluation? No minimum is known. (source: research-agent-self-improvement, 2026-10-16)
- [ ] How much citation laundering happens through aggregator pages? No source measures it. (source: research-agent-self-improvement, 2026-10-16)
- [ ] Does Setup's seven-tool probe agree with the research skill's two-tool probe? The two were not compared line by line. (source: research-agent-self-improvement, 2026-10-16)
- [ ] Can the live eval cases be made to grade research quality rather than workflow shape? Both live graders check wording or files, and one live case (scorecard) depends on a client-rendered page. Observed by the lead during round 1 measurement. (source: research-agent-self-improvement, 2026-10-16)
- [ ] What noise floor does the frozen fast exam have on this model? At 8 cases x 3 runs it separates only changes of about 0.2-0.3; a 5-run paired comparison needs a budget call from John. Observed by the lead during round 1 measurement. (source: research-agent-self-improvement, 2026-10-16)

## From the autonomous-engineer interview (2026-10-16)
- [ ] Time budget or deadline for the engineer project. None stated.
- [ ] The approval channel for batched gates: SMS, Slack, Telegram or another. John said "SMS or similar".
- [ ] How many candidate paths the engineer may keep when testing feasibility (R7 in research/requirements/autonomous-engineer.md).
- [ ] A template for per-project gates and privacy limits (R10, R14).
- [ ] Whether the engineer's self-merge of routine changes (R16) has limits, for example production deploys.

## From the existing-systems run (2026-10-16)
- [Settled 2026-10-16 by the browser run: yes, the OpenAPI spec has only GET routes for views and no workflow routes; views and Workflows need the browser. See research/findings/engineer-browser.md.] Does the Attio REST API offer only GET for views (no create or update)? The verifier could not confirm it from the OpenAPI spec (too large to read whole). Spike against an Attio sandbox before relying on UI automation for views.
- Does listing Attio webhooks need a "webhook:read" scope? The views page names only object_configuration:read.
- Can any Clay client (official or unofficial) export table contents and enrichment column settings? The unofficial client page says "building and updating", not export.
- Where does John's GTM system configuration live (Attio-Project repo holds none)? Asked of John; first engineer task is account access and exports.
