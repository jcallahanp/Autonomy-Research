# GTM scenario trace

Purpose: trace John's acceptance scenario (requirements Q8) step by step, naming the mechanism and evidence for each step, or flagging it GAP.

Q8: take the GTM system as it stands, map it, fix the Attio tables and views, set up the Clay workflows, clean the data and finish the tooling with no manual clicks from John after one setup session; plus picking up an old project where it left off. Status: **covered** (mechanism named with evidence), **partial** (mechanism exists, a named piece is missing or unconfirmed), **GAP** (no mechanism in the findings).

## Scan the GTM system as-is
| # | Step | Mechanism | Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | List accounts and tokens needed, names only | as-is skill step 1; the Attio-Project repo holds no GTM content, so the system is the accounts | engineer-existing-systems J1, J5 | covered |
| 2 | Get scoped read access | John's setup sitting: Attio key (workspace token needs an admin), Clay CLI sign-in, n8n key with expiry, Outreach OAuth app (may need an admin), Slack config token plus app ids | engineer-existing-systems S31, S45, S54, S61; engineer-human-loop E21, E22 | partial: whether Attio issues personal keys on his plan is unknown |
| 3 | Find where the GTM configuration lives | None; `jcallahanp/Varonis` was not cloned | engineer-existing-systems J45; research/open-questions.md | **GAP** |
| 4 | Snapshot Attio | REST: objects, attributes, lists, view titles, webhooks, read-only SQL (plan-gated) to JSON; view filters and columns read in the browser | engineer-existing-systems S1-S14; engineer-browser §Q11 | covered (S4, S5 uncertain; SP60) |
| 5 | Snapshot Clay | CLI for Workflows; table queries Enterprise only; no official read of table contents or enrichment column settings | engineer-existing-systems S17-S24; research/open-questions.md | **GAP** for table contents and column settings |
| 6 | Snapshot n8n | `export:workflow`, credential list (never secrets), `status=error` executions | engineer-existing-systems S31-S39 | covered if his edition exposes the API (engineer-feasibility D22; SP66) |
| 7 | Snapshot Outreach and Slack | Outreach REST over OAuth; Slack `apps.manifest.export` per app id | engineer-existing-systems S42-S50, S58-S61 | covered once the Outreach app exists (SP67) |
| 8 | Build the as-is pack and integration map | Script graph where code exists, edges from config snapshots, n8nmermaid for workflows, system-of-record table, gaps, risks, keep/replace/remove; John signs the context diagram | engineer-existing-systems B1-B4; engineer-feasibility §Q1; engineer-briefing E68 | covered (SP43) |

## Fix the Attio tables and views
| # | Step | Mechanism | Evidence | Status |
| --- | --- | --- | --- | --- |
| 9 | Intake for the fix | Interactive intake; "fix the Attio tables" restated as a problem; coined tool names repaired by glossary playback | engineer-intake P5, P12, E43, E45 | covered |
| 10 | Change objects, attributes and lists | REST scripts (Attio MCP writes ask for confirmation); 429 handling; idempotent writes; privileged writes from a plan fixed before untrusted input | engineer-browser A4-A7, A11; engineer-feasibility D10, D14, D16; engineer-security §Q6 | covered |
| 11 | Create views, Kanban and Workflows | Playwright `.spec.ts` flows with check-before-create by title; API read-back confirms ID and title only; filters and columns checked by a fresh UI read | engineer-browser A1-A3, §Implications 3; SP60, SP61 | partial: view filters cannot be confirmed by API |

## Set up the Clay workflows
| # | Step | Mechanism | Evidence | Status |
| --- | --- | --- | --- | --- |
| 12 | Clay Workflows | Clay plugin or CLI ("turn this Clay table into a Workflow"); Workflows are Alpha | engineer-browser A16; engineer-existing-systems S22 | covered (SP65) |
| 13 | Clay tables, columns, custom functions and signals | Browser flows; tables cannot be created by API; webhook sources cap at 50,000 submissions | engineer-browser A17, A18, A20, A25; engineer-feasibility D20, D21 | partial: which clicks consume credits is unknown (SP65) |

## Clean the data
| # | Step | Mechanism | Evidence | Status |
| --- | --- | --- | --- | --- |
| 14 | Find duplicates and conflicts | Reconciliation table per entity (person, company, deal), read-only diff and report; CRM authoritative; free scripted match against an export (inference) | engineer-existing-systems B24-B28 | covered |
| 15 | Data class | GTM and customer PII is the `customer` class: Claude or a paid API only; Attio terms limit automated decisions about people to supporting human decisions | engineer-models §Q6; engineer-human-loop E47 | covered |
| 16 | Apply merges and deletes | Snapshot first, then a T2 prompt per cluster (deleting data); the merge execution route is not chosen: native merge reversibility (B28) vs the Dedupe app (B30, price not checked) is unresolved | engineer-existing-systems B28-B30; engineer-protocol §Q5 | **GAP** |
| 17 | Write enrichment back | Clay writes lookup-first into Attio | engineer-existing-systems B25 | covered |

## Finish the tooling
| # | Step | Mechanism | Evidence | Status |
| --- | --- | --- | --- | --- |
| 18 | n8n | Credential-to-workflow join and error executions; nightly JSON export to git before edits; edits by API or instance MCP (n8n 2.13+, workflows flagged "Available in MCP"); hardening vars and version floor; pinned community nodes | engineer-existing-systems S31-S34; engineer-deploy E45-E51; engineer-security E103-E109 | covered if n8n is self-hosted or on a plan with the API (open question) |
| 19 | Outreach | MCP or REST once the app exists; 10,000 requests per hour; employer approval for app and UI automation | engineer-browser A41-A43; engineer-feasibility D24 | partial: company account limits are outside John's control |
| 20 | New flows with custom auth, retries or backfill | Code in a repo on a systemd timer or Cloudflare cron with a Worker receiver; Attio webhooks HMAC-signed, 5 s timeout, 10 retries over about 3 days, dedupe on event id | engineer-deploy E54-E64; engineer-security E95 | covered (routing rule is worker inference) |
| 21 | Slack app | Created from a manifest; John clicks Install in the sitting | engineer-feasibility D34; engineer-human-loop E10, E11 | covered (SP68) |
| 22 | Prove it | Auditor per task; Playwright postcondition read per UI write; after-brief and morning report | engineer-protocol E27, E138; engineer-browser T34, T35 | covered |
| 23 | No manual clicks after the sitting | Browser sessions expire on unknown schedules and need John's re-login through noVNC; Google login and CAPTCHA stay human | engineer-browser S11, S22, §Open questions; SP63 | **GAP**: re-logins are clicks, frequency unknown |

## Pick up an old project where it left off
| # | Step | Mechanism | Evidence | Status |
| --- | --- | --- | --- | --- |
| 24 | Resume a project the engineer ran | SessionStart hook re-injects `tasks.json`, `PROGRESS.md`, plan and approval status; supervisor reconciles from `events.jsonl`; `--resume <session_id>`; stale `approval.json` blocks edits; `dead-ends.md` stops retries | engineer-context §Q7.1; engineer-protocol E108, E124, E125; engineer-planning E29 | covered |
| 25 | Adopt a project someone else half-built | As-is protocol; live-state check before trusting docs (health: status.md last log 2026-10-11); the repo's own rules recorded in `profile.yaml` (ruling 8) | engineer-existing-systems J9, J21, J39, J40, J48 | covered |
| 26 | Turn the adopted repo's own backlog into `tasks.json` | No finding designs importing an existing status or TODO file into the DAG with evidence commands | none | **GAP** |

Count: 26 steps: 5 GAP (3, 5, 16, 23, 26), 4 partial (2, 11, 13, 19), and step 18 conditional on how n8n is hosted.
