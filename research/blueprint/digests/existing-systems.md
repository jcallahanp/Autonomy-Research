# Existing systems (Area 2) - digest
Source: research/findings/engineer-existing-systems.md; verification: 16 of 20 verified, 4 unverified (S15 and S26 corrected in the text; S4 and S5 uncertain)

## Decision
Confidence medium (Recommendation section). A five-step brownfield protocol, free and self-hosted, run entirely in Claude Code. Deterministic extraction comes first and LLM labelling second, and the lead never holds a file:
1. Access inventory first: account and token names only, with John's scoped read access. For GTM this is the whole system, because the repo holds no GTM content (J1, J5).
2. A config snapshot per SaaS tool through the cheapest official read path, written as JSON into the repo:
   - Attio REST: objects, attributes, lists, view titles and webhooks, plus read-only SQL (S1-S8). S4 and S5 are uncertain.
   - Clay: the CLI for Workflows (S20-S24). Table queries are Enterprise-only (S17, S19).
   - n8n: `export:workflow` plus credential metadata and `status=error` executions (S31, S33, S34, S38, S39).
   - Outreach REST over OAuth (S42-S50). Slack `apps.manifest.export` (S58-S60). Claude Code files plus `claude mcp get` (S65-S70).
3. Code map by orchestrator and workers. A script graph comes first: pydeps or dependency-cruiser plus ripgrep (M11, M12). Then one read-only Explore subagent per module writes a note and returns a path plus a status line (M22, M25, M26, M36, M37). An integration subagent merges the notes, done in topological order (M44), and a verifier re-opens cited lines. The map stays out of CLAUDE.md, because auto-generated overviews lower success and raise cost by over 20% (M29-M31).
4. Credential inventory by metadata only, behind deny rules plus the sandbox (B13, B14). Enforcement was once reported broken (B15). Scans use gitleaks `--redact` (B16) or `trufflehog --no-verification` (B18, B19), plus n8n's credential list, which never returns secrets (S31, B23).
5. The as-is pack: a C4 context-plus-container Mermaid diagram (B1, B2, B33), a system-of-record table, the credential inventory, data-quality counts, a gap list, a risk list and a keep/replace/remove table (B3, B4). Every row is cited and marked observed, inferred or asserted by John. It feeds the intake explore branch (I1).
- Sources of truth: the CRM stays authoritative (B24), Clay writes lookup-first (B25), and Attio deletes are unrecoverable (B28). So reconciliation is a read-only diff with approval per cluster.

## Alternatives and rejected
- SCIP indexes (scip-python, scip-typescript) - kept as alternative - exact references, needs a working install (M4, M6)
- CodeQL - kept as alternative for call and data-flow questions; licence unchecked (M7, M8)
- Semgrep pattern scans - kept for credential and external-call tables (M9)
- Aider repo map - kept as reference design only (M1, M2)
- Browser screenshots of Attio views and workflows and Clay columns - kept as last resort (Alternatives; no run)
- Unofficial Clay session-cookie API (claycast) - kept as spike-only; unofficial, cookie expires every few weeks (S26-S28)
- Attio Dedupe app - kept as alternative for gated, reversible merges; price not checked (B29, B30)
- DeepWiki-style wiki - kept as navigation aid only (M13-M15)
- Claude Code OpenTelemetry - kept to measure mapping cost (M49-M52)
- DeepWiki for private code - rejected - public tier, MCP not connected, wiki accuracy mid-60s% (M15, B8)
- Auto-generated CLAUDE.md overview - rejected - lowers success, raises cost (M29, M30)
- Vector or embedding index - rejected - dense retrieval near random (M18)
- Agent teams - rejected - about 7x tokens (registry row; no evidence ID)
- Generated wiki as the as-is truth - rejected (B8, B9)
- TruffleHog with verification on - rejected - sends found secrets to providers (B19)
- `n8n export:credentials --decrypted` as default - rejected - "All sensitive information is visible in the files." (S40, S41)
- Agent-driven bulk merge without approval - rejected - Attio deletes unrecoverable (B28)
- Third-party Attio and Clay MCP wrappers as primary - rejected - unofficial, not opened
- universal-ctags - rejected - Aider dropped it for tree-sitter (M3)

## Stack
| Tool | What it does here | Where it runs | Cost | Evidence |
| --- | --- | --- | --- | --- |
| Claude Code Explore subagents (Haiku override possible) | Read-only per-module mapping workers | Claude Code | Model tokens | M26, M27, M40 |
| pydeps / dependency-cruiser (madge alt.) | Script-made import graph seeding the map | Local | Free (dependency-cruiser MIT) | M10-M12 |
| Semgrep / ripgrep patterns | Credential-name and external-call inventory | Local | Free (licence not stated) | M9 |
| gitleaks `--redact` / trufflehog `--no-verification` | Secret scan by metadata | Local | Free | B16-B19 |
| Claude Code `permissions.deny` + sandbox | Hard gate on secret files | Claude Code | Free | B13, B14 |
| Attio REST + official MCP | Objects, attributes, lists, view titles, webhooks, SQL | Hosted | SQL tool plan-gated (S14) | S1-S14 |
| Clay CLI / plugin | Workflows read, table query | Hosted + CLI | Table query Enterprise-only | S17-S25 |
| n8n public API + CLI | Workflow JSON, credential metadata, error executions | Self-hosted or cloud | API on free trial unverified (snippet only) | S31-S41, B20-B23 |
| Outreach REST | Sequences, steps, templates, mailboxes | Hosted | Not stated | S42-S54 |
| Slack `apps.manifest.export` | Scopes and events per app | Hosted, config token | Free | S58-S64 |
| Claude Code CLI inspectors | `claude mcp get`, `claude doctor` | Local | Free | S65-S70 |
| C4 model in Mermaid | As-is diagram notation | Repo | Free | B1, B2 |

## Setup steps
| Step | Automated or John | How it is verified |
| --- | --- | --- |
| 1. List the accounts and tokens needed, names only (Recommendation step 1) | Automated | List reviewed by John |
| 2. **Grant scoped read access:** Attio API key (whether personal keys are issued on his plan is a gap); Clay CLI sign-in; n8n API key with owner or admin role for credentials (S31); Outreach OAuth app, which may need an admin (S45, S54); a Slack config token plus app ids, since no method lists all apps (S61) | John | A read call per tool succeeds; Outreach and Slack in spikes 9 and 13 |
| 3. Deny rules plus sandbox block `.env` and credential data | Automated | Spike 5 on the pinned Claude Code version |
| 4. Config snapshot scripts write JSON per tool into the repo | Automated | JSON files present. UI-only items listed as gaps, not findings |
| 5. Script graph, then per-module notes, merge and verifier | Automated | Verifier re-checks cited lines (spike 2 measures accuracy) |
| 6. **Review the context diagram and the system-of-record table** | John | His sign-off; spike 12 compares agent vs John |
| 7. **Health only: run the identity-bound `deploy/SETUP.md` steps (22 numbered manual steps)** | John | Live-state check (J9, J21, J48) |

## Repo composition
- Skill: a brownfield or "as-is" phase whose lead holds only status lines (Implications 1).
- Scripts: an import-graph and ripgrep inventory step writing to a map directory, and config-snapshot scripts per SaaS tool (Implications 1-2).
- Agents: an Explore worker per module (fixed-schema note, every fact with `path:line` and a confidence tag), an integration merger and a verifier (Q1 inferences).
- Files: per-module notes and a system-level file loaded by path, never in CLAUDE.md (M29-M31, M57); the config JSON snapshots; `.env.example` with names only (B-section inference); the as-is pack (C4 Mermaid, system-of-record table, credential inventory, data-quality counts, gap list, risk list, keep/replace/remove table); a reconciliation table per entity (person, company, deal).
- Hooks: extend John's existing checker subagent and hooks (protected files, privacy, lint, Stop test gate) rather than replace them (J43, J44, Implications 6).
- The health repo's names-only `secrets.tf` convention is the model (J17, J28).
- Superpowers: John's GTM repo vendors it and mandates its brainstorming-then-OK loop (J3, J32). This file decides no keep or drop; it flags the loop as a tension. Beads and Ralph are not discussed.

## Spikes
| Spike | Probe (what to run) | Pass criterion |
| --- | --- | --- |
| 1 | Mapping pipeline on Health-Management | Tokens per module, wall time, lead context growth recorded |
| 2 | Verifier re-checks 30 random cited facts vs a single long-context pass | Accuracy compared |
| 3 | pydeps and dependency-cruiser on dynamic imports and TS path aliases | Edges correct |
| 4 | CodeQL licence for private repos | Terms read |
| 5 | Deny rules plus sandbox keep `.env` and n8n credential data out (issue #24846) | No secret read on the pinned version |
| 6 | gitleaks `--redact` JSON report | Secret and Match fields masked in the file |
| 7 | n8n credentials list fields, workflow-JSON credential refs, CLI reachability | Fields and mapping confirmed |
| 8 | Clay plan; `clay workflows` dumps a definition as JSON | Plan known; dump works or not |
| 9 | Outreach profile can create an API app; company policy | Known |
| 10 | Attio UI-only features (Workflows, view filters and columns); merge undo in sandbox | List confirmed |
| 11 | Compliance API artifact list route; key on John's plan | Route answers |
| 12 | Agent-extracted context diagram vs John's knowledge | Differences listed |
| 13 | `apps.manifest.export` on Slack apps John did not create | Works or not |

## Requirements served
- R6: this area is the as-is map itself: code, SaaS configuration, data flows, credentials by name, and breakages (Recommendation 1-5).
- R1, R3, R5: the as-is gap list becomes intake's Deferred and "ask John" questions, and real object names seed the playback (I1).
- R10: the system-of-record table and C4 diagram show where data flows (B-section). Privacy limits are not covered here.
- R11: the access inventory is one list of names and scopes before any mapping (step 1).
- R17: a verifier re-opens a sample of cited lines (Q1 inferences).
- Q2, Q5: the map lives on disk in per-module notes loaded by path, sized for a model (M25, M57).
- Q4: every row is cited and marked observed, inferred or asserted.
- Q8: GTM must start with account exports, because the repo is empty (J1-J5).
- Hard gate "deleting data": merges and deletes happen only after John approves a cluster, with a snapshot first (B28).

## GTM scenario
- Scan as-is: access list, then exports. These are an Attio schema dump, Clay Workflows, n8n workflow JSON, Outreach sequences and Slack manifests, then the as-is pack. Where John's GTM configuration lives is unsettled; `jcallahanp/Varonis` was not cloned (J45).
- Fix Attio tables and views: read side only. Views come back as id, title and created_at (S2), and filters, columns and Kanban grouping are UI-only (inference). Creation is Area 6.
- Clay workflows: read via CLI; "turn this Clay table into a Workflow" (S22). Enrichment column settings have no official read (inference).
- Clean data: a reconciliation table per entity, with a read-only diff and report, approval per cluster and an Attio snapshot before bulk changes. Clay writes lookup-first (B24-B28). It starts with a free scripted match against a Postgres export (inference).
- Finish tooling: n8n credential-to-workflow join and error executions (S31, S33, S34), plus the keep/replace/remove table.

## Tensions
- Unverified claims the decision rests on:
  - S4: views GET-only. Only the first 100k characters of the spec were read. Area 6 calls it settled from a full download (browser A1).
  - S5: webhooks listable.
  - S15 and S26 were corrected in the text.
- The Verification note says Evidence ends at S55, but S56-S76 are present now. The verification note is stale, or they were added after the check. The Design questions also flag S55-S76 as search-highlight-backed.
- Deny-rule docs (B13, B14) conflict with issue #24846 (B15). The credential gate rests on spike 5.
- Unresolved contradictions:
  - grep/glob just-in-time vs precomputed maps (M16 vs M1, M4).
  - Context-file guidance vs the study in 2602.11988 (M29).
  - n8n credential GET-by-id.
  - Compliance API path family (S73 vs S74).
  - Attio merge reversibility, native (B28) vs add-on (B30).
  - Outreach self-provisioning (S45) vs legacy lock (S56).
- Against R15, R16 and G1:
  - John's health rules, "approval before every action" and "no standing pre-approvals" (J39, J40).
  - The GTM CLAUDE.md brainstorm-then-OK loop (J32).
  - The worker proposes per-task scoped approval, untested.
- Against Q8 "no manual clicks": the GTM map needs John's access grants and an interview. UI-only Attio and Clay settings cannot be read as data.
- Mapping token cost is an estimate to measure, not evidence (Q1 inferences).

## Open for John
- Where his GTM configuration lives, and whether `jcallahanp/Varonis` holds sales tooling.
- Scoped read access to Attio, Clay, n8n, Outreach and Slack, and company policy on Outreach tokens in an agent environment.
- His Clay plan (Enterprise or not), and his n8n hosting (cloud or self-hosted).
- How to reconcile "no standing pre-approvals" with autonomous runs, for example per-task scoped approval.
- Whether the health VM and tunnel exist today (status.md last log 2026-10-11).
- Sign-off on the context diagram and the system-of-record table.
