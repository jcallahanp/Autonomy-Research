---
name: as-is
description: Map an existing system before changing it. Use when a project touches a system that already runs (a code repo, Attio, Clay, n8n, Slack or another SaaS tool) and before you propose any change to it ("map what is there", "do the as-is scan", "what does the current setup do", "adopt this repo"). Runs the five-step brownfield protocol (access inventory, config snapshots, code map, credential inventory by name only, as-is pack) with read-only workers, marks every row observed, inferred or asserted, and writes everything under docs/map/. Never decrypts or prints a credential.
---

# As-is scan

Find out what an existing system really does before you change it. Write what you find to
`docs/map/` and load it by path. You hold only one status line per step; workers do the reading.

## Rules (EARS)

- F9: When a project involves an existing system, produce the as-is pack, every row marked
  `observed`, `inferred` or `asserted`, before you propose any change.
- F10: Inventory credentials by name and metadata only. Never run
  `n8n export:credentials --decrypted`, never run TruffleHog with verification, and never print,
  cat, echo or copy a secret value, an `.env` file or a key file.
- F11: When the map is written, keep it out of `CLAUDE.md`. Read files under `docs/map/` by path
  when a task needs them.
- When a source is only visible in a UI (Attio view filters and Workflows, Clay enrichment
  columns and functions), record it as a gap to ask John about, not as a finding.
- When a change would delete or merge records in a live system, stop: that is a `delete_data`
  hard gate (T2): write `HARD GATE: delete <what, how many rows> CONFIRM: <PHRASE>` under
  `## Asks for John` (see the `digest` skill). Reconciliation is a read-only diff with John's
  approval per cluster.

## Marks

Mark every row in every table with one of these words:
- `observed`: you read it in a file, an API response or a snapshot, and you cite where
  (`path:line`, or the snapshot file and its JSON path).
- `inferred`: you concluded it from observed facts; name the facts.
- `asserted`: someone told you (John, a README, a comment) and you have not checked it.

Never upgrade a mark without new evidence. An `asserted` row that matters goes on the gap list.

## Before you start

1. Read `docs/plan/profile.yaml` for `data_classes` and `adopted_rules`. If the repo has its own
   agent rules (`CLAUDE.md`, `AGENTS.md`, `docs/agent_rules.md`), they win inside that project.
   Record any rule that conflicts with unattended work as a gap for John.
2. Create `docs/map/` if it is missing. Keep one status line per step in your own context, for
   example `step 3: 7 modules mapped, 1 failed (billing), notes in docs/map/notes/`.

## Step 1: Access inventory

List every system the project touches and how you can read it. Write `docs/map/access.md`:

| System | What it holds | Read path (API, CLI, export, UI only) | Access granted by | Status | Mark |
| --- | --- | --- | --- | --- | --- |

- Use names only: the account, workspace or repo name, never a token or password.
- `Status` is `have read access`, `asked`, or `no access`. Missing access is a gap, not a
  reason to guess.
- Ask John for read-only access only; never ask for an admin or write scope at this stage.

## Step 2: Config snapshots

Take one JSON snapshot per SaaS tool through official read paths only, and save it as
`docs/map/snapshots/<tool>.json`. Call vendor APIs through the broker, which holds the key, so
you never see it: `sudo -n -u secretbroker /opt/engineer/bin/agent-run api-call <service> GET <path>`.
The broker allows only the services and methods in `/opt/engineer/etc/broker-services.json`
(GET only). For a tool with no service there, record a gap and ask John; never ask him to paste
a key into the session.

| Tool | Read path to use |
| --- | --- |
| Attio | `api-call attio GET ...`: objects, attributes, lists, list entries (counts, not every record) |
| n8n | `api-call n8n GET /workflows`, `GET /credentials` (metadata only), `GET /executions?status=error` |
| Clay | The Clay CLI's workflow and table listings, signed in as `secretbroker`; until a broker job runs it, a gap for John |
| Slack | `apps.manifest.export` for each app, once a broker service exists; until then, a gap |
| Code repo | The files themselves; `git log --stat` for recent change areas |

- Strip record contents that are personal or customer data; keep structure, names and counts.
- If no read path exists, write the gap and, only when John agrees, use the `browser` skill to
  take a screenshot of the screen. A screenshot is `observed` for what it shows and nothing else.

## Step 3: Code map

Map code from the outside in, then module by module.

1. Build the script graph first and save it under `docs/map/graph/`:
   - Python: `pydeps --show-deps --no-output` (JSON) or a ripgrep import inventory.
   - TypeScript or JavaScript: `npx --no-install depcruise --output-type json`.
   - Always: `rg -n` inventories of entry points, HTTP routes, external calls, env var names and
     scheduled jobs, one file per inventory.
2. Split the graph into modules of a size one worker can read (about 20 files).
3. Dispatch one `mapper` agent per module. Give it the module's file list and the graph file.
   It returns a note in this shape; save it verbatim as `docs/map/notes/<module>.md`:
   purpose, entry points, inputs, outputs, external calls, data stores, env var names, risks,
   open questions; every fact with `path:line` and a mark.
4. Dispatch one `merger` agent with the list of note paths. It returns `docs/map/modules.md`:
   one row per module, the edges between modules, and contradictions between notes.
5. Re-open a sample yourself: pick three facts at random from the notes and check each cited
   line. If one is wrong, send that module back to a fresh `mapper` and say why.

## Step 4: Credential inventory

Write `docs/map/credentials.md` with names and metadata only:

| Name | Kind (API key, OAuth app, webhook secret, password) | Used by (`path:line` or workflow) | Owner | Scopes, if visible | Rotation, if visible | Mark |
| --- | --- | --- | --- | --- | --- | --- |

- Find names in code with `rg` for env var reads and in n8n through `GET /credentials`.
- Scan for committed secrets with `gitleaks detect --redact --no-banner --report-format json`.
  Report a hit as `path:line kind`, never its value, and add a T1 line for John to rotate it
  (a bullet under `## Asks for John` in `PROGRESS.md`).
- Never run `n8n export:credentials --decrypted`, `trufflehog --verify` (or any TruffleHog mode
  that tests a secret against a live service), `env`, `printenv`, or `cat` on an `.env` file.

## Step 5: As-is pack

Write `docs/map/as-is.md`, at most three pages, in this order:

1. Context diagram: `docs/map/context.mmd`, a `flowchart LR` (never C4 syntax), one node per
   system from step 1, one edge per data flow. Link it; do not paste it.
2. System-of-record table: for each kind of data (company, person, deal, workflow run), which
   system holds the truth, which systems copy it, and how often. Mark every row.
3. Gaps: everything UI-only, every `asserted` row that matters, every missing access.
4. Risks: what could break or leak, with the evidence.
5. Keep, replace or remove: one row per component, with the reason. This is a proposal; John
   decides.

Then add a T1 line asking John to sign off the context diagram and the system-of-record table
(see the `digest` skill for the line format). Do not start planning changes until he answers.

## Handing on

- The gap list feeds intake's deferred questions and the plan's open questions.
- The glossary of real object, workflow and credential names goes into `docs/plan/brief.md`.
- When the system changes later, update `docs/map/` in the same change and list the map files
  in `docs/DEPENDENTS.md` against the source globs they describe.
