# Feasibility (Area 4) - digest
Source: research/findings/engineer-feasibility.md; verification: 19 of 20, 1 unverified (SEI H/M/L quote)

## Decision
Before committing to a stack, run a fixed five-part feasibility protocol made of files: map, bound, sandbox, decide, record and hand off. Everything is free: Markdown, Mermaid, mermaid-lint, Docker or Podman, and Claude Code features (Q10). Confidence medium; the rubric, bounding numbers, checklist and setup-list format are worker syntheses, untested on John's systems.
- Map: `docs/map/integration-map.md` holds a plain Mermaid flowchart plus one sequence diagram per critical flow, parse-gated by mermaid-lint. LLM Mermaid is about 70% valid unchecked and 95% with a render loop (A4, A6). `integration-matrix.md` has one row per edge. One integration card per service follows a 12-point checklist built on Stripe's and Google's rules (D1, D12, D14). Mermaid's C4 type is experimental, so it is not the default (A3).
- Bound: first grep `dead-ends.md`, the ADRs and the tool registry (B29, A23). Trial only behavioural claims (auth, rate limits, webhooks, pagination, UI-only behaviour, go/no-go), because "Real APIs diverge from documentation" (B20). Run at most 3 paths, one question each, with the pass line written before the run and the riskiest assumption first (B9). Each trial is boxed in turns, wall-clock time and USD; it ends "inconclusive" at box end, and after two failed fixes on one blocker the agent records and stops (B4, B17, C59).
- Sandbox: one worktree and one `claude -p --output-format json --json-schema` process per trial (C1, C53). Each runs non-root in a `--network none` container that reaches a host proxy; the proxy allowlists hosts and injects that trial's scoped test credential (C23, C24, C17). The Bash sandbox stays on as an inner layer only, because on its own it "is not sufficient for fully unattended runs" (C16).
- The supervisor, not the agent, writes `result.json`, tears the trial down and sweeps orphans at start, because `-p` worktrees are not cleaned up (C3, C19, C22).
- Decide: pass/fail gates first, then H/M/L ratings against a datum, each with an evidence tag, under criteria John ranks and freezes. Near-ties are ties, settled by reversibility (A15, A16, A17, A18, A21). The SEI three-level quote (A19) is unverified. The decision is a MADR ADR whose status John edits (A27, A28).
- Record negatives in `dead-ends.md` with the version tested, an evidence location and `retry-when` (B29, B30, B31, B33).
- Hand-off: one setup list in dependency order, long waits first, which John works through in one local sitting with Claude in Chrome. Chrome pauses at login and CAPTCHA (D44, D47). The build starts with a walking skeleton, not the spike code (B5, B6).
- The spike skill blocks build-time needs (three user-named paths, no credentials, an advisory isolation recipe, worker self-cleanup, prose-only results; C65-C79). It needs a separate "trial" mode, not looser rules (Implications 1).

## Alternatives and rejected
- Docker Sandboxes `sbx`: kept as alternative if `/dev/kvm` exists. MicroVM with host-side credential injection; Ubuntu 24.04+ (C32, C33).
- Claude Code sandbox runtime (beta): kept as alternative for low-risk trials (C18).
- Hosted Vercel Sandbox or E2B: kept as alternative for one-off probes of public code. E2B has a $100 one-time credit and 1 h sessions; Vercel charges $0.1104 for a 30-minute 4-vCPU build; both prices seen 2026-10-16 (C42, C46).
- Structurizr DSL: kept as alternative when several views must come from one model (A2).
- Weighted scoring: kept as alternative with frozen weights and a sensitivity check, if John wants one number (A16).
- Mini-ATAM scenarios: kept as alternative for the one or two riskiest choices (A19, unverified quote).
- epitaph-style JSON ledger plus a hook: kept as alternative (B33).
- `setup.sh` with prompts: kept as alternative for the final verification step only (worker inference).
- Full ATAM: rejected. Too heavy for one user (worker inference, no quoted source).
- EventStorming as agent output: rejected. It is a human workshop (A10).
- Mermaid C4 as default: rejected. Experimental (A3).
- Summed unfrozen weights: rejected. False precision (A16).
- Kiro, BMAD or Spec Kit for this: rejected. None compares paths on evidence (worker inference).
- Carrying many alternatives long-term: rejected (worker inference).
- Auto-captured negative memory without a recurrence check: rejected. 74% of rows were one-off (B32).
- An LLM picking the winner without a deterministic probe: rejected (B16).
- Agent teams as trial runners: rejected. No worktree isolation (C6).
- Agent view as trial runner: rejected. Research preview (C7).
- The Bash sandbox alone: rejected (C16).
- gVisor and self-hosted Firecracker for v1: rejected. I/O cost and a KVM requirement (C27, C28).
- Hobby hosted tiers as the main path: rejected. 1 h on E2B, 45 min on Vercel, creation paused at quota (C42, C44, C45).
- Modal: rejected. No advantage seen (C49).
- Cloudflare Sandbox SDK: rejected unless already on Workers Paid (C50, C51).
- Cursor `/best-of-n`: rejected. Different engine, and it varies the model, not the path (B26).
- Fully browser-driven account creation: rejected. Chrome pauses at login and CAPTCHA, and some terms ban bot accounts (D44, D48).
- The model solving CAPTCHA or 2FA, or secrets in chat: rejected (worker inference).
- Supabase `anon`/`service_role` keys for new work: rejected. Deprecated by end of 2026 (D41).
- Piecemeal per-service setup asks: rejected. R11 requires one list (D52).

## Stack
| Tool | What it does here | Where it runs | Cost | Evidence |
|---|---|---|---|---|
| Mermaid (plain flowchart + sequenceDiagram) | Integration map | Repo `docs/map/` | Free | A1, A3 |
| mermaid-lint | Parse gate in a hook or CI. MIT, npx, Node 22+ per the worker, not in the quote | Local hook | Free | A6 |
| Integration matrix + cards (12-point checklist) | Per-edge and per-service facts with evidence tags | Repo | Free | D1-D15; Q7 |
| Claude Code worktrees | One isolated checkout per trial | VM | Free | C1, C3 |
| `claude -p --output-format json --json-schema` | One headless process per trial with a structured result, cost and exit code | Inside the trial container | Subscription or capped trial key (unresolved) | C19, C53, C56 |
| Docker or rootless Podman container (`--network none`, `--rm`, pids and memory limits) | Trial boundary | John's VM | Free | C23, C38 |
| Host proxy (Envoy, mitmproxy or Squid) | Host allowlist and credential injection, outside the boundary | John's VM | Free (Q10) | C23, C24; Implications 6 |
| Claude Code Bash sandbox (bubblewrap) | Inner layer only | Inside the trial | Free | C10, C12, C16 |
| MADR | Path-decision record that John confirms | Repo `docs/adr/` | Free | A27, A28 |
| `dead-ends.md` (vexjoy field format) | Negative-results registry | Repo | Free | B29, B30 |
| Claude in Chrome | One local setup sitting; John does consent, 2FA and secrets | John's machine | Not stated; off under API-key auth | D44, D45, D46 |
| Slack `apps.manifest.create` | Agent creates the Slack app; John clicks Install | Slack | Free | D34 |

## Setup steps
| Step | Automated or John | How it is verified |
|---|---|---|
| 1. `ls /dev/kvm` on the VM; try sbx if present | Automated | Spike 1 |
| 2. Install Docker or rootless Podman (subuid/subgid) | Automated if the agent has sudo, else **John** | Spike 2 container runs `claude -p` |
| 3. Add the bubblewrap AppArmor profile on Ubuntu 24.04, "a one-off sudo step" | **John** (one-off sudo) unless the agent holds sudo | Spike 4 |
| 4. Host proxy with per-trial allowlist, TLS termination and token injection | Automated | Spike 3: a tool that ignores `HTTP_PROXY` fails closed |
| 5. Decide trial auth: `--bare` plus a trial-only API key, or non-bare with clean settings | Automated probe, John decides on the key | Spike 2: exit codes 0 and 143, budget-stop exits |
| 6. Supply test accounts for auth and rate-limit probes | **John** (by hand) | Spike 8 |
| 7. Add the mermaid-lint hook and the dead-ends/ADR read-first rule and hook | Automated | Spikes 10 and 7 |
| 8. Rank 3 or 4 criteria once (rank order, not percentages); the ranking is frozen in the ADR | **John** | Recorded in the ADR with a date |
| 9. Review the integration map and matrix | **John** | Spike 9: correctness against a hand-made version |
| 10. Flip each ADR's status to accepted | **John** | Spike 12: he can state the decision and its undo path |
| 11. Start long waits first: Outreach production review, Google consent screen to "In production" | **John** (by hand) | Spikes 15 and 16 |
| 12. One local sitting with Claude in Chrome: first accounts, billing and plan upgrades, OAuth consent, 2FA, copy-once secrets into the vault (names only reach the agent) | **John** (by hand), agent prefills | The agent's "verifies all" table names the first failing row; time per step fed back (spike 20). About 45-90 minutes across 11 services is the worker's unsourced estimate |

## Repo composition
- Files: `docs/map/integration-map.md`, `docs/map/integration-matrix.md`, one integration card per service, `docs/adr/` MADR records, `dead-ends.md`, a `result.json` per trial, and the ordered setup-list page (Q10).
- Spike skill: add a "trial" mode beside the current feasibility mode. It takes a pre-authorised path list from intake with a configurable cap that defaults to 3, a per-trial credential manifest (test accounts only), a per-trial domain allowlist, and `--max-turns`, `--max-budget-usd` and a timeout. It allows at most two fix attempts per blocker, sets per-trial CPU, memory and pids limits, leaves `result.json` and teardown to the supervisor, and uses a written authorisation record for unattended runs (Implications 1).
- Both modes gain a step 0 dead-end lookup and the bounding fields in the brief (Implications 2-3).
- Hooks: a mermaid-lint gate on Markdown writes; a CLAUDE.md rule plus a hook to read `docs/adr/` and `dead-ends.md` before tool or integration choices (Implications 5; whether the hook beats prose is spike 7).
- Scripts: the trial supervisor (launch, box, `result.json`, teardown, startup sweep of worktrees, labelled containers and temp dirs; Q6). The VM bootstrap adds Docker or Podman, the host proxy and the AppArmor profile (Implications 6).
- Engineer gates after intake: "map", then "decide", then "R11 setup list", each a file because plan mode does not persist (A11; Implications 4).
- Five EARS requirements to add, covering dead-end retries, the box-end verdict, proxy-only credentials, teardown and the setup list (Implications 7).
- Superpowers, Beads, Ralph: not addressed. The two-attempt bound comes from the context protocol (E3).

## Spikes
| Spike | Probe | Pass criterion |
|---|---|---|
| 1 | `ls /dev/kvm` on John's VM; sbx if present | KVM present or absent decides sbx |
| 2 | Hardened container running `claude -p` under subscription login and under a trial-only key | `--bare` works; exit codes 0 and 143 and budget-stop exits observed |
| 3 | Host proxy injects a test token with TLS termination | A tool that ignores `HTTP_PROXY` fails closed |
| 4 | AppArmor bubblewrap profile on Ubuntu 24.04 | Sandbox runs |
| 5 | Three trials in parallel, then a forced kill | No leaked secret, no orphan worktree |
| 6 | Box sizing for one trial worker | Turn and wall-clock box that fits (about 60 turns is unvalidated) |
| 7 | PreToolUse or SessionStart hook greps `dead-ends.md` | Agent behaviour changes |
| 8 | John provides test accounts | Accounts available for auth and rate-limit probes |
| 9 | Generate the GTM integration map and matrix from config snapshots | Validity rate; correct against a hand-made version |
| 10 | mermaid-lint hook on 20 generated diagrams | Failures and repair rounds counted |
| 11 | Score 3 candidate paths 5 times each | Ratings are stable |
| 12 | Show John 3 ADRs | He can state the decision and its undo path |
| 13 | Change one design input | The stale-diagram check flags the map |
| 14 | Render a Mermaid C4 block where John views docs | It renders |
| 15 | Google OAuth publishing status with John's real scopes | Avoids the 7-day Testing refresh token |
| 16 | Outreach development versus production credentials | Behaviour confirmed |
| 17 | Clay API surface on John's plan | Surface known |
| 18 | n8n API on John's plan or self-host | API reachable |
| 19 | WHOOP and Withings refresh-token rotation store | New refresh token stored on every refresh |
| 20 | Actual minutes per setup step in the first sitting | Times fed back into the list |

## Requirements served
- R6: the map extends the as-is pack (C4 context plus container, system-of-record table, credential inventory) with a per-edge matrix and service cards built from config snapshots (A12; Q1).
- R7: the map, matrix and cards record dependencies, keys and integration points. At most 3 paths, parallel trials in `--network none` containers with proxy-injected test credentials, and negatives in `dead-ends.md` with `retry-when` (Q3-Q5).
- R10 (in part): rubric gates include "health data goes to no unapproved processor" and a privacy-risk rating (Q2).
- R11: one ordered setup list, long waits first, with an agent verification check per row and a final "verifies all" table (Q8).
- R12: the agent prefills forms and creates apps from manifests (D34). Rows state why a step is human-only: login and CAPTCHA (D44), admin roles (D19, D49), bot-account terms (D48, secondary source).
- R18: box end gives "inconclusive", and two failed fixes on one blocker stop the trial (Q3).
- R19 (in part): step 0 greps the tool registry and `dead-ends.md` before dispatch (Implications 2).
- Q3: every trial ends in a recorded verdict, including `inconclusive` and teardown status (Q6).
- Q4: `result.json` carries the exit code, cost, denied hosts and artifacts (Q6; C19, C53).
- Q6: hosted sandbox prices are stated where they are alternatives (C42, C44, C46, C49).

## GTM scenario
- Scan as-is: the integration map and matrix are generated from config snapshots; for GTM, edges come from configs, not a code graph (Q1; spike 9).
- Fix Attio tables and views: gap for UI-only configuration. The Attio card notes that rate-limit responses are 429 (D16); the 100 reads/s and 25 writes/s figures are worker inference, not in the quote. Webhooks retry up to 10 times with a 5 s timeout (D17). Only workspace admins grant workspace-level tokens, which makes that a John setup row (D19).
- Set up Clay workflows: the Clay card says tables are Enterprise only (D21) and webhook sources cap at 50,000 submissions even after rows are deleted (D20). Clay API auth and rate limit are unconfirmed (spike 17).
- Clean data: idempotency for every write and retrying only transient errors (D10, D14), plus Attio 429 handling (D16).
- Finish tooling: the n8n API is not on the free trial, and non-Enterprise keys have full access (D22, D23; spike 18). Outreach allows 10,000 requests per hour (D24); its dev-versus-production review and `expires_in` 7200 are a paraphrase, not a quote (D25; spike 16). Slack app from a manifest (D34). Setup order: Outreach review starts first (Q8).

## Tensions
- Docker on the VM: engineer-runtime says "no Docker is required" (E1), while trials need a container because the Bash sandbox alone is insufficient (C16). The findings reconcile this by scope, which adds Docker or Podman to the VM bootstrap (Q5 Contradictions).
- `--bare` versus subscription login: `--bare` never reads OAuth credentials (C20), and the runtime keeps the API key only as a capped fallback (E2). Without `--bare`, `-p` runs a directory's hooks and MCP servers (C21). Unresolved (spike 2).
- The setup sitting needs a local session with Claude in Chrome, which cloud sessions cannot do, and Chrome is off under API-key auth (Q8; D46). R13 wants browser control for UI-only configuration such as Attio, but the findings use Chrome only for the setup sitting.
- Path cap: one worker keeps a fixed 3, another wants a configurable cap tied to quota (Q3 Contradictions). The requirements leave the R7 cap unset (requirements Gaps).
- Retries: spike-worker forbids them (C74), while trial mode allows two per blocker. The findings reconcile this by mode (Q9 Contradictions).
- The H/M/L rating rests partly on the SEI quote, which the verifier could not confirm (A19; Verification).
- Whether GitHub renders Mermaid C4 is self-contradictory on one page (A7; spike 14). The agent-scale box (about 60 turns) is unvalidated (spike 6).
- R12 depends on terms of service, but no page establishes bot-account bans for John's specific services (Open questions; D48 is secondary). Several per-service values are worker inference, not quotes: Attio limits, Outreach dev/prod and 7200, Withings token lifetimes, Slack 12 h (Q7).
- Unattended trials clash with the current step-1 chat confirmation (C76) and with R15. Trial mode needs a written authorisation record, whose form is undecided (Q9 gap 10).
- Planning's `integrations.yaml` overlaps the matrix and cards here, and ADRs live in `docs/adr/` here but `docs/plan/decisions/` in planning (engineer-planning.md Q1).

## Open for John
- Rank 3 or 4 decision criteria once, and accept that near-ties are settled by reversibility (Q2).
- Provide test accounts for auth and rate-limit probes (spike 8).
- Paid tiers the human-only rows depend on: n8n paid cloud or self-host for the API (D22), Vercel Pro for webhooks (D38), Clay Enterprise for tables (D21).
- Move the Google consent screen to "In production" (D12).
- Allow Docker or rootless Podman, the proxy and the AppArmor profile on the VM (Implications 6). Choose `--bare` with a trial-only API key or subscription login for trials (spike 2).
- Whether hosted sandboxes may be used for public-code probes, which puts the repo and any token on a third party (Q5).
