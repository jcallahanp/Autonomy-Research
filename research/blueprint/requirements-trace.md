# Requirements trace

Purpose: map each requirement in `research/requirements/autonomous-engineer.md` (R1-R23, Q1-Q8 and the constraints) to the decisions that satisfy it, or mark it partial or unmet with the reason.

Status: **met** (a decision covers it, pending its spikes), **partial** (covered with a named shortfall), **unmet**. "F" numbers are the requirements in flow.md; "area" refers to decisions.md.

## Functional requirements
| Req | Satisfied by | Status | Why not fully met |
| --- | --- | --- | --- |
| R1 Play back goal, constraints, anti-goals, conflicts | Area 1 restate step, coverage list, glossary playback (F2, F8) | met | Anti-goals section has no opened evidence (engineer-intake §Tensions) |
| R2 Record intent behind named tools, offer alternatives | Area 1 restate as a problem; options table always holds a non-user option (F2, F4) | met | |
| R3 Say when a request misfits | Area 1 one objection with cost, then ADR (F6) | met | |
| R4 One open question per turn, no yes/no chains | Area 1 open phase (F3); closed phase is multiple choice with a default | partial | Default-bias untested (SP38) |
| R5 Options for a non-technical reader | Area 1 at most 5 options with cards (F4); area 8 plain diagrams | met | |
| R6 As-is map before changes | Area 2 five-step protocol (F9-F11) | partial | Clay table contents and Attio view filters have no official read (gtm-scenario steps 5, 11) |
| R7 Map paths, bound, sandbox in parallel, record negatives | Area 4 trials (F12-F17); area 3 dead-ends | met | Path cap defaults to 3 (worker choice) |
| R8 Plan set as single source of truth | Area 7 plan set, `approval.json` (F18-F20) | met | |
| R9 Record change, update dependents, re-approval | Area 7 change tiers and `DEPENDENTS.md` gate (F30, F31) | met | Hook blocking mode unsettled (SP06) |
| R10 Data flows, privacy risks, per-project limits | `integrations.yaml`, `profile.yaml`, data classes, health Claude-only (ruling 9; area 10) | partial | Requirement says John's projects default to permissive; health is default-deny until he decides (engineer-models §Tensions) |
| R11 One ordered setup list, verified, no piecemeal asks | setup.md; area 4 hand-off (F21); area 5 sitting | met | Re-logins after session expiry return later (gtm-scenario step 23) |
| R12 Create keys and config itself where allowed; say why not | Area 5 parent-to-child minting; human-only rows with reasons | partial | Children only on Cloudflare, Vercel, Supabase, Slack (engineer-human-loop E1-E11); Clay and n8n key endpoints unknown (SP65, SP66) |
| R13 Browser for API-less config, confirm through API | Area 6 Playwright flows with API read-back; F25 audit | partial | API read-back confirms Attio view ID and title only (engineer-browser A1) |
| R14 Pause only the gated action, batch, continue | Ruling 3, T1 digest; T2 prompts separate (F26, F31, F38) | partial | T2 hard gates go as separate immediate messages, not in the one batch (deliberate, engineer-human-loop §Tensions) |
| R15 Run without human input overnight | Supervisor `claude -p` per task with `--permission-prompts none` (F22) | partial | Blocked until John picks Path A or B (ruling 1) |
| R16 Self-merge routine changes | Ruling 2; area 11 `gh pr merge --auto` (F28) | unmet by default | Off until John picks a GitHub route and shadow mode passes |
| R17 Separate audit agent checks claims, tests, docs, secrets, drift | Ruling 4; area 11 `audit.sh` and auditor; area 12 gitleaks (F24, F25) | met | |
| R18 Stop on no progress, record, notify | Area 9 bounds and breaker; area 11 FAIL handling; denial counter (F27, F29) | met | |
| R19 Bounded discovery pass, log every candidate | Area 3 ladder and vet card; `ROW:` to the registry | met | Envelope numbers untested (SP54) |
| R20 Security tests, patch, report with scope and limits | Area 12 (F32-F34) | met | Gate thresholds are worker numbers |
| R21 Deploy web without human steps beyond gates; Android second; no iOS | Area 13 CLI deploys, PWA and Capacitor, iOS deferred (F35-F38) | partial | Promote is a T1 digest line by default (ruling 9), a human step beyond the three gates |
| R22 Three-page dark brief before and after, plus agent plan | Area 8 brief and `architecture.yaml`; ruling 7 publishing | partial | Publishing needs an interactive session; dark polarity readability contested (engineer-briefing E45, E46) |
| R23 Repeatable setup with plain-language steps | Area 14 `bootstrap.sh`, `doctor.sh`, `/setup`; setup.md | met | |

## Quality requirements
| Req | Satisfied by | Status | Why not fully met |
| --- | --- | --- | --- |
| Q1 Cheaper tier kept only while quality holds | Model tiers move down only after SP32; routing re-checked per release (engineer-models §Implications 9) | met | |
| Q2 State in files; re-read after compaction | `tasks.json`, `PROGRESS.md`, plan; SessionStart compact hook (area 9) | met | Compaction fidelity unmeasured (SP24) |
| Q3 Overnight run ends in a known state | `RUN_STATUS.json` trap, `waiting_for_reset`, reconcile (F39, F40) | met | |
| Q4 Done carries evidence | Evidence command rerun at HEAD; implementer tests never count (F24, F25) | met | |
| Q5 Brief at most three pages; agent docs model-sized | Area 8 three pages; CLAUDE.md under 200 lines; reads under about 128K-256K | met | |
| Q6 Paid recommendations carry price and reason | stack.md cost column; no paid tool adopted without a spike | partial | Max price and Claude per-token prices not opened (engineer-runtime §open q 12; engineer-models §Open questions 5) |
| Q7 Broad permissions acceptable with disclosure, R20 not loosened | Auto mode inside a non-root VM with managed deny rules; trifecta disclosed (engineer-security §Q6) | met | Narrower than Q7 allows: bypass mode rejected (decisions.md tensions) |
| Q8 GTM acceptance with no clicks after one sitting | gtm-scenario.md | partial | 5 GAP steps, including re-logins and the Attio merge route |

## Constraints
| Constraint | Satisfied by | Status |
| --- | --- | --- |
| Claude Code is the engine | Area 10: no gateway, only writer | met |
| Hard gates money, delete, store | Ruling 9; T2 prompts (F38) | met |
| Approvals as one batched list over a light channel | Ruling 3, Telegram digest | met (Telegram, not SMS) |
| Free and self-hosted first | stack.md; paid items optional and priced | met |
| Web first, Android second, iOS deferred | Area 13 | met |
| Outreach company limits; Attio App SDK blocked; some Attio config UI-only | Areas 6 and 2; SP60, SP67 | met, pending spikes |
| John is on Max | Ruling 1 | open (Path A or B) |
