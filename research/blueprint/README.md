# Autonomous engineer blueprint

Purpose: the one-page entry to the build blueprint for John's autonomous Claude Code engineer; start here.

Built 2026-10-16 from the 14 area digests in `digests/` and the findings files in `research/findings/engineer-*.md`.
Citations read "(engineer-<area> E12)" or "(engineer-<area> §section)": the evidence ID or section in
`research/findings/engineer-<area>.md`. This folder is synthesis; nothing here was run or installed.

## What the engineer is
A packaged Claude Code setup that takes a project from a spoken brief to deployed, audited software
with John at design and approval level only. Claude Code is the only engine and the only writer
(engineer-models E57, E58). It runs on one Ubuntu VM John controls (engineer-runtime §Q7, S16, S28).

## Architecture in one paragraph
John talks to an interactive Claude Code session for intake, plan approval and anything that needs
a claude.ai login (publishing pages, Remote Control). After he approves a hash-bound plan
(engineer-planning E29, E30), a supervisor process under systemd (engineer-protocol E124) works the
`tasks.json` DAG: one fresh, bounded `claude -p` per task in its own worktree and branch
(engineer-context §Q7.4; engineer-protocol E37, E38), behind a root-owned managed-settings file, the
Bash sandbox and fail-closed hooks (engineer-human-loop E148, E168, E152). A Stop/TaskCompleted gate
and a script-first auditor decide "done" from evidence, never from the model's claim (engineer-protocol
E11, E15, E138). Secrets sit in SOPS+age files readable only by a `secretbroker` user that runs
allowlisted jobs (engineer-human-loop E58-E60). Browser-only work (Attio views, Clay tables, OAuth
consent) runs in Playwright on a persistent headed Chrome profile (engineer-browser T4, S1). The
supervisor's own Telegram bot sends one numbered daily digest plus immediate hard-gate prompts
(engineer-human-loop E118). Every night ends in a known state written to `RUN_STATUS.json` and
`MORNING.md` (engineer-context §Q7.5; engineer-protocol E103).

## Files in this folder
| File | What it holds |
| --- | --- |
| [decisions.md](decisions.md) | Per area: decision, alternatives, rejected with reason; the lead's 12 rulings applied |
| [stack.md](stack.md) | Every tool with where it runs and cost; where every secret lives and who can read it |
| [setup.md](setup.md) | Numbered setup order, John's one sitting as one block, the spike that must pass first |
| [repo-composition.md](repo-composition.md) | Plugin and template layout, state files, hooks, MCP, what comes from Superpowers, Beads, Ralph |
| [flow.md](flow.md) | One project end to end, with EARS requirements |
| [gtm-scenario.md](gtm-scenario.md) | John's GTM acceptance scenario traced step by step, GAPs flagged |
| [spikes.md](spikes.md) | Every spike, de-duplicated, ordered by what it blocks |
| [requirements-trace.md](requirements-trace.md) | R1-R23 and Q1-Q8 mapped to decisions |
| [open-questions.md](open-questions.md) | What stays open, with the default taken meanwhile |
| `digests/` | The 14 area digests this blueprint was built from |

Diagrams: `docs/diagrams/engineer-context.mmd`, `engineer-runtime.mmd`, `engineer-project-flow.mmd`,
`engineer-approvals.mmd` (linked from `docs/diagrams/index.md`).

## Decisions John still owes
| # | Decision | Default until he answers |
| --- | --- | --- |
| 1 | Auth for the supervisor's `claude -p` runs: Path A, Max `/login`, or Path B, a Console API key (decisions.md, ruling 1) | None. Unattended runs are not built until he chooses; everything else is built to work under either path |
| 2 | Secrets store: does he already have 1Password? (ruling 6) | SOPS+age behind the `secretbroker` user (free) |
| 3 | How R16 self-merge is enforced: GitHub Pro (price unverified), a public repo, or local-only enforcement (ruling 2) | Self-merge off; routine PRs reach him as one digest line each |
| 4 | Hard gates beyond his three, and per-project privacy (ruling 9) | Exactly money, deleting data, app-store submission; production promotes are digest items with default "hold"; health data Claude-only |
| 5 | VPS or home box for the VM, and whether it is the same VM as the health app (engineer-runtime §Open for John) | A dedicated VM separate from the health VM (blueprint inference: the engineer holds untrusted input, secrets and egress at once, engineer-security E114) |
