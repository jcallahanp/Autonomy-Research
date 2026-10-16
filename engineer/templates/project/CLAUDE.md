# {{NAME}}

This project is built by the autonomous engineer. John ({{OWNER}} on GitHub) approves the plan,
reviews Tier 2 pull requests and answers the digest. This file is context; the hooks and the
audit enforce the rules.

## Start here, every session
1. The SessionStart context: open tasks, the last `PROGRESS.md` entry, approval status.
2. Your task in `docs/plan/tasks.json`, then only the files it names in `files_to_read`.
3. `dead-ends.md` before you try any tool or path.

## Where things live
| You need | Read |
| --- | --- |
| Goal, scope, non-goals, costs | `docs/plan/brief.md` |
| Acceptance criteria (EARS) | `docs/plan/requirements.md` |
| Services, auth, env var names, prices | `docs/plan/integrations.yaml` |
| Gates, privacy, data classes, adopted rules | `docs/plan/profile.yaml` |
| System model | `docs/plan/architecture.yaml` (view: `architecture.mmd`) |
| Interfaces | `docs/plan/contracts/` |
| Changes of course | `docs/plan/changes/` |
| Decisions | `docs/adr/` (MADR) |
| The existing system, if any | `docs/map/` |
| Which docs change with which code | `docs/DEPENDENTS.md` |
| The setup list for John | `docs/setup.md` |
| What happened so far | `PROGRESS.md` |

There is no generated overview here; read docs/map/ by path.

## Skills
- superpowers:<name> means the local skill <name> in the engineer plugin.
- test-driven-development and finishing-a-development-branch are not installed; every task ends in a PR.
- the plan skill's task contract wins over Superpowers task sizing: one session, one commit, one
  check, about 1-4 files and 100 lines.
- Engineer skills: `plan`, `as-is`, `browser`, `deploy`, `security-review`, `digest`.

## Rules
- Build only what an approved task names. The plan set in `docs/plan/` is the source of truth;
  change it only through a change record (`plan` skill).
- Never edit `tests/acceptance/`, `.github/`, `.claude/`, `audit/`, `CODEOWNERS` or this file.
  Never edit an existing test to make it pass, and never add a skip.
- No secret values anywhere: not in code, tests, logs, commits or messages. `.env.example` holds
  names only. Vendor APIs go through the broker.
- Never push to the default branch, merge, deploy to production, spend money, delete data or
  submit to an app store yourself. Those go through the supervisor and John (`digest` skill).
- APIs before the browser. On a login page, CAPTCHA or bot challenge, stop and write a blocked
  note; never try to get past it.
- Write requirements in EARS ("When X, the system shall Y").
- Diagrams are small `flowchart` or `sequenceDiagram` Mermaid files, one concern each.

# Compact instructions
When compacting, keep:
- The current task id, its check command and its last result.
- Paths of the plan files and of any notes you are writing.
- Decisions already made in this session, with the reason.

Drop:
- File contents you can read again, tool output and search results.
