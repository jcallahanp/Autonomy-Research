# Findings index

One line per findings file. The lead reads this file instead of the findings themselves.
Keep it under 200 lines. The verifier appends one line when a run finishes, in this form:
`- [<title>](<slug>.md) — <one-line answer> (<date>, <status>)`

- [Research-agent architecture](architecture.md) — Bounded fan-out of 3-5 workers on mutually exclusive facets, cited notes on disk, one synthesizer, then a verifier pass. (2026-10-16, complete)
- [Context management and token economy](context-management.md) — A thin lead that holds only plan, index and status lines; workers read pages in isolated contexts and return short summaries. (2026-10-16, complete)
- [Research methodology](methodology.md) — Beads waits for Phase 2, Ralph loops only with a script-checked stop and a cap, and only supply-chain checks from security tooling apply. (2026-10-16, complete)
- [Packaging as plugin and template](packaging.md) — One repo can be plugin, marketplace and template; cloud sessions load only committed `.claude/` files and never install plugins. (2026-10-16, complete)
- [Tool routing](tool-routing.md) — Parallel Search for discovery and reading, Exa as second opinion, DeepWiki for repos confirmed by clone, Playwright last. (2026-10-16, complete)
