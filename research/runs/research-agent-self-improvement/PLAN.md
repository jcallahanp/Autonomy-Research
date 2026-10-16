# How should research-agent v0.1 improve itself, and how should a capped self-improvement loop be judged without overfitting?

Brief: John (2026-10-16) wants the plugin to test and improve itself by using itself. Find the changes that would most raise research quality and resistance to context rot, and how to evaluate a capped self-improvement loop without overfitting to the plugin's own exam. Scope is this repo's plugin (skills, agents, hooks, evals); free tiers only; no cost reporting.
Effort: Landscape or enumeration - 5 workers
Tools: Parallel Search and Exa connectors available (deferred; load with ToolSearch); WebFetch for citing; DeepWiki and git clone for repos.
Rulings: "Context rot" = answer quality degrading as context grows or ages, in the lead or a worker. "Self-improvement loop" = a round that proposes and applies changes to the plugin's own prompts/skills/evals, then re-measures. Prefer sources dated 2025-2026; name the date of every source. A recommendation must say which plugin file it changes. Free tiers only. Facets do not overlap: measurement (facet 1) is separate from change-proposal mechanics (facet 5). Synthesis ruling (lead, after the internal-audit return): a citation of a local repo file as `path:line, read YYYY-MM-DD, Read` counts as an opened source for claims about this repo; that note has no URLs by design.

## Facets
- [x] Evaluating research agents and self-improvement without overfitting - notes/eval-without-overfit.md - medium - several papers abstract-only; no runs-per-case for LLM-judged reports
- [x] Context rot evidence and mitigations for multi-agent Claude Code setups - notes/context-rot-mitigations.md - medium - no Claude 4.5+/5.x measurements; Parallel rate-limited
- [x] Citation faithfulness techniques and failure rates - notes/citation-faithfulness.md - medium - no effect sizes for quote-first alone; 5 papers unopened
- [x] Mechanisms for proposing and accepting prompt/skill changes - notes/prompt-optimization-loops.md - medium - GEPA/TextGrad free-tier untested; promptfoo cap page unopened
- [x] Internal audit of this plugin's own evidence - notes/internal-audit.md - high - eval HTML/traces unread

## Gap round
- not run: every facet answered its key questions; gaps are depth, not missing answers

## Outputs
- Findings: research/findings/research-agent-self-improvement.md - written (31 claims dropped: 20 excerpt-only or session observations, 11 resting only on the out-of-repo build report; lead ruling: they stay dropped, because the build report is the lead's own writing, not a source)
- Verification: verifier 19 of 20 verified (needs-review: unsupported-rate figures were derived as complements of reported accuracy); independent hand check 17 supported, 3 partial, 0 unsupported (hand-check.md): 2 partials introduced at the synthesizer merge (citation narrowed, claim strengthened), 1 wrong line range from the researcher
