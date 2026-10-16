---
name: security-review
description: Review a change or a milestone for security with evidence, deterministic tools first. Use when a PR touches auth, data handling, secrets, config, CI, dependencies or an external call, when a milestone ends, or when asked to "security review this", "check for vulnerabilities" or "write the security report". Runs the pinned scanners, then a model review blind to their output, and accepts a finding only with file:line, CWE, severity, a repro and its scope. Writes security/findings.json, and at a milestone security/REPORT.md and security/BRIEF.md. Never calls anything "secure".
---

# Security review

Deterministic tools decide the gate. Your own review adds findings only when you can prove them.
John decides what is left.

## Rules (EARS)

- F32: When a PR touches auth, data or config, run the deterministic scanners and this review,
  and accept a model finding only with `file:line`, a repro and its scope.
- F33: If a new Critical or High deterministic finding, any secret, or a failing auth test
  appears, then block merge and deploy: set the task to `needs_john` with the finding ids (the
  supervisor sends John an `Unblock <task>` T1 line with your reason; his `y` sets it ready again).
- F34: When a milestone ends, write `security/REPORT.md` and `security/BRIEF.md` stating scope,
  method, findings, severity, remediation, retest and what the review does not assure.
- Never write that a system is "secure". Say what was checked, at which commit, and how.
- Never run active scans (ZAP active, Nuclei, fuzzers) against a third-party service. Scan only
  hosts the project owns, and only its staging.
- Never put a secret value in a finding, a log or a report. Name the file, line and kind only.

## Step 1: Scope

Write down, before you look at any output:
- the commit SHA and the diff range (`git merge-base` with the default branch to `HEAD`);
- the areas in scope: auth, input handling, data storage, secrets, external calls, config, CI,
  dependencies; and the ones out of scope, with the reason;
- the standard: OWASP ASVS 5.0.0 Level 1, plus any Level 2 items `profile.yaml` or the plan names;
  the OWASP API Top 10 for an API; the LLM and agentic Top 10 when the project calls a model.

## Step 2: Deterministic tools first

Run each tool that applies, at the version pinned in `/opt/engineer/docs/versions.md`. Save raw
output outside the repo, in `"${TMPDIR:-/tmp}/security-raw/<tool>.json"`, and read it from there;
only the merged `security/findings.json` is committed. Changes under `security/` are Tier 2, so
the PR waits for John's review.

| Tool | For | Command shape |
| --- | --- | --- |
| gitleaks | secrets in the diff and history | `gitleaks detect --redact --no-banner --report-format json --report-path "${TMPDIR:-/tmp}/security-raw/gitleaks.json"` |
| Semgrep CE | code patterns | `semgrep scan --config p/default --json --metrics=off` |
| OSV-Scanner | known-vulnerable dependencies | `osv-scanner scan source -r . --format json` |
| `npm audit` / `pip-audit` | dependency advisories per ecosystem | `npm audit --json`; `pip-audit -f json` |
| Bandit or Ruff `S` rules | Python security lint | `ruff check --select S --output-format json` |
| Checkov | Terraform, Docker, CI config | `checkov -d . -o json` |

A tool that is not installed is a `not checked` line in the report, never a silent pass.

## Step 3: Model review, blind

Read the diff and the code it touches without opening the tool output. Look for: missing auth or
authorisation checks, unsigned or unchecked webhooks, injection (SQL, shell, template, path),
server-side request forgery on any fetch of a user-supplied URL, secrets or personal data in
logs, unsafe deserialisation, missing rate limits on login or costly calls, and trust in text
that came from outside (emails, web pages, tickets) when deciding what a tool does.

For each suspicion, try to prove it: write a failing test or a command that shows the bad
behaviour on a local or staging copy. No repro, no finding: keep it in the report as an open
question instead.

## Step 4: Merge and write findings

Merge tool findings and proven model findings into `security/findings.json`, a list of objects:

```json
{"id": "SEC-0001", "file": "src/hooks/webhook.py", "line": 42, "cwe": "CWE-345",
 "severity": "high", "title": "Webhook signature not checked",
 "repro": "pytest tests/security/test_webhook_unsigned.py", "observed": "200 OK",
 "expected": "401", "scope": "POST /hooks/whoop on staging", "source": "model",
 "status": "open", "found_at": "<sha>"}
```

- `severity` is `critical`, `high`, `medium` or `low`: critical means remote compromise or bulk
  data exposure with no precondition; high needs one easy precondition; medium needs several or
  exposes little; low is hardening.
- `source` is the tool name or `model`. Do not give a model finding a CVSS score.
- Deduplicate by `file`, `line` and `cwe`. Keep a tool finding you judge false as
  `status: "dismissed"` with the reason; a dismissal of a Critical or High needs John (T1 line).
- Dated exceptions John accepts go in `security/allowlist.md` with an expiry date.

## Step 5: Gate

Block the merge and any deploy (F33) when any of these is true, and say which one:
- a new Critical or High from a deterministic tool, not in `security/allowlist.md`;
- any secret found by gitleaks in the diff (add a T1 line for John to rotate it);
- a failing auth test;
- a model finding without `file:line`, a repro or a scope (it cannot pass, so fix the finding).

A Medium or Low finding does not block; it goes in the report and, if it needs a fix, a task.

## Step 6: Milestone report

At a milestone, write `security/REPORT.md` (for the record) and `security/BRIEF.md` (one page
for John) with:
1. Scope: commit, areas in and out, standard and level.
2. Method: each tool and version, what the model review covered.
3. Findings: a table of id, `file:line`, CWE, severity, status.
4. Remediation and retest: what was fixed, in which PR, and the retest that now passes.
5. Coverage, one line per area: `checked and clean at <sha>`, `checked, issues open`, or
   `not checked`.
6. Footer, word for word: "This is not a penetration test. Absence of findings is not evidence
   of absence."
