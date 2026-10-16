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
- [ ] Rate limits for Parallel, Exa (keyless) and DeepWiki are undocumented; how many calls does one research run need?
- [ ] Who owns the Exa connector account and its $10/month free credit?

## Evidence gaps
- [ ] No context-rot measurement exists for Fable, Opus 5 or Sonnet 5; the "lead holds little" rule rests on Claude 4-era data.
- [ ] No published benchmark for depth-first "how do these two systems integrate" research; the 90.2% multi-agent gain is for breadth-first queries.
- [ ] No measurement of LLM comprehension of diagrams versus prose at equal token count.
- [ ] Whether Claude Code's bundled `/deep-research` workflow can be invoked from a plugin skill or only by the user.
- [ ] Does the Mermaid Chart connector render experimental `C4Context` syntax reliably? Stay on `flowchart` until checked.
- [ ] Do `TaskCreate`/`TaskList` entries persist across sessions on any surface? Docs call them session todos.
