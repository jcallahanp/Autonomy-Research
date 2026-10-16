# Open questions

Purpose: what the blueprint leaves open, stated as open, with the default the build takes until it is answered.

Each row names who or what settles it: John, a spike (spikes.md) or a later research run. Items carried from `research/open-questions.md` ("From the existing-systems run" and "From wave 3") are marked (carried).

## Decisions for John
| # | Open question | Default meanwhile | Settled by |
| --- | --- | --- | --- |
| 1 | Path A (Max `/login`) or Path B (Console API key) for the supervisor's `claude -p`? Does a supervisor running the `claude -p` CLI under his own login fall under "Developers building products or services ... should use API key authentication" (engineer-human-loop E42)? (carried) | No unattended runs; everything else built path-independent | John, after SP01, SP02 |
| 2 | Does he already have 1Password? | SOPS+age behind `secretbroker` (ruling 6) | John |
| 3 | R16 route: GitHub Pro (price unverified), a public repo, or local-only enforcement (carried) | Self-merge off; one T1 "merge PR?" line per PR | John, then SP18, SP19 |
| 4 | Gates beyond money, deleting data, store submission; is external mail or secrets handling a T2 anywhere? | T1 digest lines; per-project `profile.yaml` may raise them | John at intake |
| 5 | Should production promotes ever be automatic after the pre-promote checklist? (engineer-deploy §Open for John) | T1 line with default "hold" | John |
| 6 | May any non-Anthropic endpoint ever see health data? (engineer-models Q7) | No; health is Claude-only | John |
| 7 | VPS or home box, and may the engineer share the health app's VM? | Dedicated VM (blueprint inference from engineer-security E114) | John |
| 8 | Which Moderate changes need his approval? (engineer-planning open q 32) | Moderate is FYI; Major waits for him | John |
| 9 | May lockfile bumps self-merge once R16 is on? (engineer-protocol §Q5) | John-gated | John |
| 10 | Threat model, health-data retention and deletion, and which n8n workflows may act unattended (engineer-security A20, B15) | Nothing that sends externally runs unattended | John |
| 11 | Pay for an OpenAI key for the Tier 2 cross-family reviewer, or fund the Argon spike? | Off; Claude-only | John, after SP34 |
| 12 | Dark or light after the phone test (engineer-briefing E45, E46) | Dark artifact page; committed Mermaid has no theme directive | John, after SP49 |
| 13 | Two Telegram bots if one cannot be shared? | Two bots: supervisor and Channels | SP16, John |

## Facts to establish about John's systems
| # | Open question | Default meanwhile | Settled by |
| --- | --- | --- | --- |
| 14 | Where does the GTM configuration live; does `jcallahanp/Varonis` hold sales tooling? (carried) | First engineer task is the access list and exports | John |
| 15 | Clay plan: Enterprise or not? Can any client export table contents and enrichment column settings? (carried) | Not Enterprise; tables and columns are browser-only and unread | SP65 |
| 16 | n8n hosting: cloud or self-hosted; API on his plan? | Treat the API as unavailable until SP66 shows it | SP66 |
| 17 | Does his employer allow Outreach app creation and UI automation? | No Outreach writes | John, SP67 |
| 18 | Does Attio issue personal API keys on his plan; does listing webhooks need a `webhook:read` scope? (carried) | Workspace token made by an admin; webhooks not listed | SP60 |
| 19 | Attio merge route: native merge (unrecoverable deletes, B28) or the Dedupe app (price not checked, B30)? | Report duplicates only; no merges executed | SP60, John |
| 20 | Do the health VM and tunnel exist today (status.md last log 2026-10-11)? | Live-state check before any health work | as-is scan |

## Design points the findings left open
| # | Open question | Default meanwhile | Settled by |
| --- | --- | --- | --- |
| 21 | Under Path B the key sits in the environment of the process the model controls; can the model's shell read it? | Treat the key as exposed; cap every run with `--max-budget-usd` | SP11 run under Path B |
| 22 | Where Claude Code keeps the `/login` credentials and whether the model can read them (not in the findings) | Treat as readable by the `engineer` user | SP11 |
| 23 | Which OS user runs the supervisor? The findings name only `engineer` and `secretbroker` | A third `supervisor` user owning the state dir (blueprint inference) | Build review |
| 24 | How often browser sessions expire per site, so how often John must re-log in | Daily logged-in check; re-login is a T1 digest line | SP63 |
| 25 | How to import an adopted repo's own backlog (status, TODO files) into `tasks.json` | John confirms a hand-converted `tasks.json` at intake | Later research run |
| 26 | Routines: worth adding for GitHub-only nightly jobs? (engineer-runtime C19) | Off in v1, so the digest stays on one channel | SP77 |
| 27 | Does a single-user private repo allow John to approve the bot's PR? (engineer-planning open q 31) | Approval by Telegram reply recorded in `approvals.jsonl` | SP18 |
| 28 | May a Max session spawn `codex` or `agy` with their own credentials? (engineer-models open q 19) | Not used in v1 | Later research run |
| 29 | Smithery: usable last rung (engineer-tool-discovery E16) vs "Skip" in `research/tool-registry.md` and `tool-routing` | Last rung; registry rows not rewritten in this pass | Registry update |
| 30 | Semgrep rules licence if the engineer is later handed to others (G8) | Semgrep CE now; Opengrep if shared | John at hand-over |
| 31 | All numeric budgets (intake cap of 5, envelope 3 workers/15 calls/10 min, task caps 1-4 files/100 lines, 24 h T1 timeout, about 60-turn trial box) are worker inference | Use them; recalibrate from SP30, SP35, SP36, SP37, SP54 | Spikes |
| 32 | Stop-hook blocking: exit 2 vs JSON decision | Use exit 2 | SP06 |
| 33 | Time budget for building the engineer (requirements Gaps) | None stated | John |
