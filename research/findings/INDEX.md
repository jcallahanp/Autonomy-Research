# Findings index

One line per findings file. The lead reads this file instead of the findings themselves.
Keep it under 200 lines. The verifier appends one line when a run finishes, in this form:
`- [<title>](<slug>.md) — <one-line answer> (<date>, <status>)`

Status is one of: `complete` (Verification section, every sampled claim verified),
`needs-review` (Verification section with at least one unverified claim), `unverified`
(no Verification section yet).

- [Research-agent architecture](architecture.md) — Bounded fan-out of 3-5 workers on mutually exclusive facets, cited notes on disk, one synthesizer, then a verifier pass. (2026-10-16, complete)
- [Context management and token economy](context-management.md) — A thin lead that holds only plan, index and status lines; workers read pages in isolated contexts and return short summaries. (2026-10-16, needs-review)
- [Research methodology](methodology.md) — Beads waits for Phase 2, Ralph loops only with a script-checked stop and a cap, and only supply-chain checks from security tooling apply. (2026-10-16, complete)
- [Packaging as plugin and template](packaging.md) — One repo can be plugin, marketplace and template; cloud sessions load only committed `.claude/` files and never install plugins. (2026-10-16, needs-review)
- [Tool routing](tool-routing.md) — Parallel Search for discovery and reading, Exa as second opinion, DeepWiki for repos confirmed by clone, Playwright last. (2026-10-16, needs-review)
- [Research-agent self-improvement](research-agent-self-improvement.md) — The 0.97 self-test covers mocked workflow rules, not the merge and verification tail, where the verifier cannot reopen Firecrawl or clone pages. (2026-10-16, needs-review)
- [Engineer intake](engineer-intake.md) — Run intake as a budgeted two-phase protocol in Claude Code: open "last time" questions over a coverage list, then a capped closed phase with recommended defaults, research on "I don't know", one push-back, and a short spec plus JSON task list with file-recorded approval. (2026-10-16, needs-review)
- [Engineer runtime and packaging](engineer-runtime.md) — Run the unmodified Claude Code binary on one plain Ubuntu VM John controls, non-root, signed in with his Max subscription via /login, with Channels and Remote Control for approvals and a persistent Chromium profile for logins; cloud Routines only for GitHub-only overnight jobs; package it as the template-plus-plugin repo with a pinned bootstrap script, doctor script and setup skill; no harness such as OpenClaw as the host. (2026-10-16, complete)
- [Engineer context](engineer-context.md) — Keep state in repo files re-injected by a SessionStart compact hook, enforce done with Stop/TaskCompleted hooks, run each overnight task as a bounded fresh `claude -p` session under a supervisor, Opus for planning and debugging, Sonnet for implementation and review, Haiku only for mechanical work after a paired test; Beads deferred. (2026-10-16, needs-review)
- [How an autonomous engineer understands an existing system before changing it](engineer-existing-systems.md) — Map existing systems by deterministic extraction first and LLM labelling second, record credentials by name only, reconcile read-only with per-merge approval, and deliver a C4 map plus source-of-truth, credential, data-quality and keep/replace/remove tables; John's GTM system is in no repo, so account access and exports come first. (2026-10-16, needs-review)
