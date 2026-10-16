---
name: plan
description: Write and keep the project's plan set under docs/plan/ and turn it into small tasks. Use after intake (and the as-is scan, when an existing system is involved) and before any code ("write the plan", "break this into tasks", "update the plan", "this needs a change of course", "what does John sign"). Covers the plan files, the four files John signs and how approval.json binds them by hash, the task contract (one session, one commit, one check, about 1-4 files and 100 lines), the tasks.json fields, change records tiered Minor, Moderate or Major, docs/DEPENDENTS.md and the project setup list. The task contract here wins over Superpowers task sizing.
---

# Plan

The plan set is the single source of truth for a project. Write it before building, keep it
small, and change it only through a change record.

## Rules (EARS)

- F18: Before building, write the plan set and the before-brief and treat them as the single
  source of truth.
- F19: When John approves by an allowlisted Telegram reply or by approving the plan PR from his
  own GitHub account, the supervisor writes the approval: `approval.json` with the sha256 of each
  signed file, and the tag `plan-approved-N`. You never write `approval.json` or the tag.
- F20: If a signed file's hash no longer matches the approval, then the hooks refuse code edits
  until John approves again. Do not try to work around this; write a change record.
- F21: When the plan is approved, write one ordered setup list in `docs/setup.md`: long waits
  first, a verification for every row, and the reason for every row only John can do.
- F30: When a change of course is needed, write a change record tiered Minor, Moderate or Major,
  update every dependent document named in `docs/DEPENDENTS.md` in the same change, and block
  dependent tasks until the record is `applied`.
- F31: When a change is Major, park that branch, send one T1 line, and keep working on tasks the
  change does not touch.

## Before you write

1. Run the Superpowers `brainstorming` skill with John (its hard gate applies: no design before
   he agrees the goal). Intake is interactive; unattended runs start only after approval.
2. Read `docs/map/as-is.md` if it exists, `docs/plan/profile.yaml`, `dead-ends.md` and
   `docs/adr/`. Do not plan a path that `dead-ends.md` lists unless its `retry-when` is met.

## The plan set

| File | What it holds | John signs it |
| --- | --- | --- |
| `docs/plan/brief.md` | Goal, scope, non-goals, risks, costs summary; at most three pages, page 1 a context flowchart | yes |
| `docs/plan/requirements.md` | EARS requirements with ids (`R1`, `R2`) and a fit criterion each: the acceptance criteria | yes |
| `docs/plan/integrations.yaml` | Every service: purpose, auth, env var names, price with date, owner action, fallback, the 12 checklist fields; edges; monthly total | yes |
| `docs/plan/profile.yaml` | Hard gates, extra Tier 2 globs, promote default, self-merge, data classes, allowed processors, adopted rules, unattended | yes |
| `docs/plan/architecture.yaml` | The system model: `nodes` (id, kind, label) and `edges` | no |
| `docs/plan/architecture.mmd` | The `flowchart LR` view of `architecture.yaml`, same node ids | no |
| `docs/plan/contracts/` | One file per interface: request, response, errors, example | no |
| `docs/plan/tasks.json` | The task DAG (below) | no |
| `tests/acceptance/` | Frozen acceptance checks, one per fit criterion | no |
| `docs/adr/NNNN-<slug>.md` | One MADR per decision, copied from `docs/adr/0000-template.md` | no |

- John signs exactly four files: `brief.md`, `requirements.md`, `integrations.yaml` and
  `profile.yaml`. The approval record hashes those four.
- The `plan-reviewer` agent, in a fresh context, checks everything John does not sign against
  the four signed files. Run it before you ask John for approval and fix what it finds.
- Keep `architecture.yaml` and `architecture.mmd` in step: the parity check fails when their node
  ids differ. Keep `integrations.yaml` `env_vars` and `.env.example` in step: that check fails on a
  missing or extra name.
- Write names of secrets, never values. A price always carries the date you read it.
- The guards never let you write under `tests/acceptance/`. Write each acceptance check as a
  runnable draft in `docs/plan/contracts/acceptance/<requirement-id>.<ext>` and list it in the
  plan PR; John moves it into `tests/acceptance/` in his review, where CODEOWNERS covers it.

## Asking for approval

1. Open the plan as one PR. Its description lists the four signed files and links each draft.
2. Add one T1 line: `Approve plan v<N> for <project>? PR <url>` with default `n` (see the
   `digest` skill). Plan approval never takes a default on timeout.
3. When John approves, the supervisor runs `approve-plan`, which writes the approval and tags
   `plan-approved-N`. Read the approval status from the SessionStart context; do not edit code
   until it says `approved`.

## The task contract

Every task fits one session, one commit and one check:
- about 1-4 files and about 100 changed lines;
- one evidence command in `check` that exits 0 only when the task works and prints a test count
  (`TESTS_RUN=<n>`, pytest `N passed`, `Ran N tests`, or the runner's own summary);
- one Conventional Commit, and one PR per task (never a local merge to the default branch).

This contract wins over Superpowers task sizing. When a task does not fit, split it. A task that
needs a Tier 2 path (CI, auth, migrations, lockfiles, `docs/plan/`, `security/`) is still one
task; its PR simply waits for John's review.

## tasks.json

`docs/plan/tasks.json` is `{"version": 1, "tasks": [...]}`, checked against
`/opt/engineer/templates/schemas/tasks.schema.json`. Each task has:

| Field | Rule |
| --- | --- |
| `id` | Letters, digits, `_` or `-`, at most 64 characters, unique |
| `title` | At most 120 characters; becomes the PR title after `<type>: ` |
| `type` | `feat`, `fix`, `docs`, `test`, `chore`, `refactor`, `style` or `perf` |
| `status` | `todo` when written; later `ready`, `running`, `done`, `blocked`, `needs_john` |
| `depends_on` | Ids of tasks that must be `done` first; no cycles, no unknown ids |
| `requirement_ids` | The `R` ids this task serves |
| `files` | The files the task may create or change |
| `files_to_read` | Optional: files the implementer reads first (contracts, map notes) |
| `check` | The evidence command, run from the project root |
| `evidence_result` | `null` until the check has run |
| `passes` | `false` when written |
| `attempts` | `0` when written |
| `blocked_note` | `null`; the supervisor fills it when a task is blocked |

- Only the planner writes tasks. The implementer changes only `status` and `passes` of its own
  task.
- Order tasks so the earliest ones prove the riskiest assumption.
- Every requirement id appears in at least one task; every task names at least one.
- Write each task so the implementer decides nothing: name the files, the interface and the
  check (the Superpowers `writing-plans` "no placeholders" rule).

## Change records

Write a change record whenever the plan must change after approval, as
`docs/plan/changes/NNNN-<slug>.md` with: date, tier, reason, what changes, the dependent
documents updated, the tasks affected, and `status: proposed` or `status: applied`.

| Tier | When | What you do |
| --- | --- | --- |
| Minor | No signed file changes and no task is added or removed (a typo, a clearer contract example) | Apply it in the same PR as the fix |
| Moderate | Tasks, contracts or architecture change, but no signed file does | Update the dependents, mark the affected tasks `blocked` until the record is `applied`, rerun `plan-reviewer`, then apply |
| Major | Goal, scope, acceptance, a cost or risk ceiling, or an irreversible or external action changes, or any signed file must change | Park the branch, add one T1 line, keep working on unaffected tasks; John's approval of the new plan version re-signs the files |

- A signed file changed by a Major change breaks the approval hash on purpose: code edits stop
  until John approves the new version.
- If a change also creates or reverses a decision, write a new ADR that supersedes the old one.

## docs/DEPENDENTS.md

Each row maps a source glob to a document that must change with it:
`| src/api/** | docs/plan/contracts/api.md |`. The stop gate fails a task that changes a matching
file without changing the document. Add a row whenever you write a document that describes code.

## The project setup list

After approval, write `docs/setup.md` (F21) as one ordered list for one sitting with John:
- long waits first (account approvals, domain verification, store reviews);
- for every row: what John does, why only he can do it (payment, identity, consent, legal terms,
  CAPTCHA), and the command or check that proves it worked;
- secrets are seeded by John with `sudo -u secretbroker /opt/engineer/bin/seed <NAME>`; list the
  names only.
Never ask for setup steps piecemeal during the night; add a missing one to the next digest.
