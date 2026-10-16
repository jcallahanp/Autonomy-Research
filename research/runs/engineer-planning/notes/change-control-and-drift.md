# Change control, replanning and drift detection

Brief: Design how an autonomous engineer changes an approved plan mid-build without leaving documents stale, and which tools detect drift between plan, code and docs.
Run: research/runs/engineer-planning/PLAN.md

## Change-control practice and how spec-driven tools handle changes

### Takeaway
For a solo owner the fitting model is: approved plan is immutable once John signs it; every change is a small dated change record (proposal with old-to-new text, impact list, scope class), applied in a fixed order, with superseded decisions kept (ADR supersede). OpenSpec, BMAD correct-course and DevSquad all converge on this; Kiro and spec-kit docs I opened say little about mid-build amendment. Confidence: medium (tool docs read; no spike).

### Cited findings
- ADR practice: amend by adding information, or supersede with a new ADR; old text not rewritten — https://github.com/joelparkerhenderson/architecture-decision-record, opened 2026-10-16, WebFetch — Quote: "amend the ADR by adding new information, or supersede the ADR by creating a new ADR"
- OpenSpec lets the agent revise plan artifacts mid-build; the loop is Apply -> (plan changed) -> Update -> Apply — https://github.com/Fission-AI/OpenSpec/blob/main/docs/workflows.md, opened 2026-10-16, WebFetch — Quote: "you can update planning artifacts whenever implementation reveals something new"
- OpenSpec verify checks implementation against artifacts on completeness, correctness, coherence — same page — Quote: "validates implementation against your artifacts across three dimensions"
- OpenSpec archive merges ADDED/MODIFIED/REMOVED/RENAMED deltas into main specs and moves the change folder to a dated archive; MODIFIED must carry the full updated block; REMOVED needs Reason and Migration — https://openspec.dev/docs/schemas/spec-driven, opened 2026-10-16 via Exa highlights (not separately fetched) — Quote: "MODIFIED Requirements: Changed behavior - MUST include full updated content"
- BMAD correct-course: trigger, impact analysis over PRD/epics/architecture/UX, old-to-new edit proposals, scope class Minor/Moderate/Major, explicit approval — https://github.com/bmad-code-org/BMAD-METHOD skills/bmad-correct-course/SKILL.md:260 (commit cfba3ff), read 2026-10-16, git clone + grep — Quote: "**Major**: Needs fundamental replan with PM/Architect involvement"
- Same file: approval prompt — SKILL.md:244 — Quote: "Do you approve this Sprint Change Proposal for implementation? (yes/no/revise)"
- Same file: goal — SKILL.md:8 — Quote: "Manage significant changes during sprint execution by analyzing impact across all project artifacts and producing a structured Sprint Change Proposal."
- DevSquad spec amendment: implement worker raises a drift flag, coordinator pauses, amendments never silent, propagation flags downstream artifacts without editing them, resume blocked until updated or waived — https://microsoft.github.io/devsquad-copilot/concepts/spec-amendment/, opened 2026-10-16, WebFetch — Quote: "returns a `spec-drift` flag with a structured payload"
- Same page: propagation is flag-only — Quote: "The refine agent does not edit these artifacts in amendment mode. It flags them."
- spec-kit: changes mean re-planning from the spec, not patching code — https://github.com/github/spec-kit/blob/main/spec-driven.md, opened 2026-10-16, WebFetch — Quote: "means revisiting the specification and creating new implementation plans"
- spec-kit README names no amend step; it offers consistency checks and a converge loop — https://github.com/github/spec-kit, opened 2026-10-16, WebFetch — Quote: "Repeat implement → converge until convergence reports Converged."
- Kiro feature-specs page does not document post-task spec updates — https://kiro.dev/docs/specs/feature-specs/, opened 2026-10-16, WebFetch — Quote: "Implementation can adapt"

### Contradictions
- None found. (Kiro and spec-kit pages are silent rather than conflicting.)

### Inferences
- Triggers for a formal replan (mine, from BMAD "triggering issue" + DevSquad drift flag): a failed spike, a blocked dependency, an owner scope change, or a discovered contradiction between an approved acceptance criterion and reality. Anything else is a within-plan task edit.
- Semantic versioning of the plan is not documented by any tool I opened; use a simple `plan vN` counter plus dated change files (OpenSpec archive shape) rather than semver.

### Gaps
- Kiro mid-build spec update behaviour and Kiro task-regeneration: docs pages opened were silent; unverified.
- MADR docs and Nygard original not opened (adr.github.io was silent on supersession); only the joelparkerhenderson page.
- Whether "RFC amendments / engineering change request" forms add anything for a solo owner: no source opened.

## Docs-as-code sync checks

### Takeaway
Cheap deterministic path-mapping gates (Danger or a 20-line script) plus link checking are the base; they detect proxies for staleness, not falsehood. Start as warn, gate only on drift introduced by the current diff. Published noise data exists only for lychee (429 flakiness) and LLM checkers; none for Danger, Vale, markdownlint or mermaid lint. Confidence: medium.

### Cited findings
- Danger-style rule is a four-line path comparison; start with warn; hard fail invites junk edits — https://datadef.io/guides/en/docs-checks-in-ci, opened 2026-10-16, WebFetch — Quote: "Teams usually start with warn rather than fail"
- Same page: CI cannot check truth — Quote: "CI detects proxies for outdatedness rather than outdatedness itself"
- Same page gives no false-positive rates for lychee or Vale (WebFetch answer: advice only, e.g. exclude internal hosts so link job does not "cry wolf").
- lychee: rate limiting yields spurious broken links — https://lychee.cli.rs/troubleshooting/rate-limits/, opened 2026-10-16, WebFetch — Quote: "The result is that lychee will report a lot of broken links with `429` as a status code."
- Same page: mitigation of last resort — Quote: "As a last resort, you might want to accept `429` as a valid status code."
- Real user report of lychee noise leading to deactivation — https://github.com/lycheeverse/lychee/issues/1873, seen 2026-10-16 in Exa highlights only (not fetched; treat as unconfirmed) — Quote: "have deactivated it as we started getting too many false positives"
- Drift gate that ignores pre-existing drift (judges only the PR's own diff) — https://pantheon-org.github.io/skill-quality-auditor/ADR/adr-044-docs-drift-pr-gate/, seen 2026-10-16 in Exa highlights only — Quote: "Gate mode only fails on drift introduced by the current diff."
- Schemathesis: MIT, finds API responses that deviate from the OpenAPI/GraphQL schema; page makes no false-positive claim — https://github.com/schemathesis/schemathesis, opened 2026-10-16, WebFetch — Quote: "licensed under the terms of the MIT license"
- Dredd is archived, so skip — https://github.com/apiaryio/dredd, opened 2026-10-16, WebFetch — Quote: "This repository was archived by the owner on Nov 8, 2024. It is now read-only."
- Pact can-i-deploy needs published verification results and recorded deployments; exit 0 safe, 1 not — https://docs.pact.io/pact_broker/can_i_deploy, opened 2026-10-16, WebFetch — Quote: "All required verification results are published and successful."
- Atlas `migrate diff` needs a dev database; `migrate lint` runs in CI — https://atlasgo.io/versioned/diff, opened 2026-10-16, WebFetch — Quote: "a URL to a Dev Database that will be used to compute the diff"

### Contradictions
- None found.

### Inferences
- For a solo repo, Pact is overkill (needs a Broker and two parties); Schemathesis fits only if the project exposes an OpenAPI schema. Atlas/migra only if there is a database. (Mine.)
- The existing dependents manifest + Stop hook (engineer-context.md) is the same pattern as the path-mapping gate; add "diff-scoped" semantics from the ADR-044 pattern so old debt does not block.

### Gaps
- No published false-positive data for Danger, Vale, markdownlint, mermaid-lint, migra, Dredd (archived). Not searched beyond one query each; unverified.
- Mermaid validation tool (mermaid-cli / mermaid-lint) not opened; the registry already lists Mermaid Chart MCP.
- Vale and markdownlint docs not opened.

## LLM consistency audits

### Takeaway
Naive LLM doc-vs-code comparison is very noisy (80-98% flag rate); published fixes are (a) restrict to "incorrectness" and filter, precision ~0.63; (b) execution-backed cross-check, precision 0.88 at recall 0.21; (c) report only specific contradictions, anecdotally ~1 in 12 false at under a cent per PR. Use LLM audits as a diff-scoped, evidence-citing second layer after deterministic checks. Confidence: medium (academic data is function-level docstrings, not plan-vs-code).

### Cited findings
- DocPrism abstract: plain LLM flags over 90%; filtering brings it to 14%; precision 0.63 — https://arxiv.org/abs/2511.00215, opened 2026-10-16, WebFetch — Quote: "LCEF reduces DocPrism's inconsistency flag rate from 98% to 14%"
- Same: broad evaluation precision — Quote: "achieves a precision of 0.63 without performing any fine-tuning"
- DocPrism full text: main false-positive cause is flagging missing detail — https://arxiv.org/html/2511.00215v2, seen in Exa highlights only — Quote: "LLMs identify natural gaps between high-level documentation and code as incompleteness inconsistencies"
- Cascade (April 2026): reports only if existing code fails a doc-derived test and doc-generated code passes it — https://arxiv.org/abs/2604.19400, opened 2026-10-16, WebFetch — Quote: "13 previously unknown inconsistencies, of which 10 have subsequently been fixed" ; precision 0.88 / recall 0.21 are from the HTML version seen in Exa highlights only (https://arxiv.org/html/2604.19400).
- Doc-Drift GitHub Action (blog, 2026-01-26): flags only specific contradictions; self-reported noise and cost — https://newsletter.nerdnoir.com/p/documentation-needs-a-feedback-loop, opened 2026-10-16, WebFetch — Quote: "Maybe one in every dozen findings needs to be dismissed."
- Same: cost — Quote: "The total spend reported was a whopping $0.03."
- Same: limits — Quote: "The system catches specific contradictions, not conceptual drift."
- Verdict (intent-vs-diff gate, 1 star): scope mismatch causes false positives — https://github.com/verdict-ci/verdict, opened 2026-10-16, WebFetch — Quote: "false positives born of mismatched scope, not real defects."
- Blog on a docs-gate: free path-check first, LLM only when docs touched, about $0.01 per call — https://blog.sarvesh.pro/the-ci-check-that-forces-your-docs-to-keep-up-with-your-code/, seen in Exa highlights only — Quote: "The typical case — a developer forgets to update docs — costs literally nothing."
- CCI dataset labels are noisy (45.67% of "inconsistent" labels wrong in a 600-sample check) — https://arxiv.org/html/2506.20558, seen in Exa highlights only — Quote: "a staggering 45.67% of instances labeled as positive (i.e., inconsistent) are, in fact, incorrectly identified"

### Contradictions
- Doc-Drift's "rare false positives" (self-reported, one author, toy and one demo repo) vs DocPrism's measured precision 0.63 on 1,991 real pairs — https://newsletter.nerdnoir.com/p/documentation-needs-a-feedback-loop vs https://arxiv.org/abs/2511.00215. Different tasks (diff-scoped contradictions vs whole-function consistency); a spike on John's own repos would settle it.

### Inferences
- Design (mine): LLM auditor gets one plan section plus the specific diff or files that implement it, must cite plan line and file:line, stays silent otherwise, and runs at milestone boundaries, not on every edit. Findings are advisory (John-batched) never auto-edits of the approved plan.
- Cost should be small with Haiku-class model per check, but Haiku 5.5 is registered as unfit for complex reasoning; use Sonnet for the audit pass. Unmeasured.

### Gaps
- No published accuracy for plan-vs-code (as opposed to docstring-vs-code) auditing found.
- Exa-highlight-only items above should be re-opened before being relied on.

## Replan protocol

### Takeaway
Three tiers: Minor (inside an approved task's acceptance criteria): engineer edits and logs. Moderate (changes tasks/order/approach but not goals or acceptance criteria): engineer applies a change record and tells John in the digest. Major (changes goal, scope, acceptance criteria, cost/risk ceiling, or touches an irreversible/external action): engineer stops that branch, writes a change proposal, and waits for John's batched approval while continuing unaffected tasks. This adapts BMAD's Minor/Moderate/Major and DevSquad's block-until-propagated. Confidence: medium; the tier boundaries are my design, not tested.

### Cited findings
- BMAD routes by scope class and requires explicit approval before implementing — BMAD-METHOD skills/bmad-correct-course/SKILL.md:244,260 (commit cfba3ff), read 2026-10-16 — Quote: "Do you approve this Sprint Change Proposal for implementation? (yes/no/revise)"
- BMAD offers incremental or batch review of edit proposals (relevant to John's batched list) — fetched via Exa highlights of https://github.com/bmad-code-org/bmad-method/blob/main/src/bmm-skills/4-implementation/bmad-correct-course/SKILL.md (WebFetch of that URL returned 404; clone path differs) — Quote: "Batch**: Present all changes at once for review"
- DevSquad: work stops until downstream artifacts are updated or waived; changes are never silent — https://microsoft.github.io/devsquad-copilot/concepts/spec-amendment/, WebFetch — Quote: "blocks resume until each flagged artifact is either updated"
- OpenSpec update confirms each edit one artifact at a time and reconciles other artifacts (page 404 on direct fetch; seen in Exa highlights of https://openspec.dev/docs/reference/slash-commands) — Quote: "Confirms every edit with you before writing, one artifact at a time"
- Stop-hook doc-gate pitfalls: JSON block ineffective, exit 2 worked — already in research/tool-registry.md (doc-sentinel row, PR dgalarza/claude-code-workflows#36) — path:research/tool-registry.md:192 — Quote: "Stop hook auto-dispatching a drift resolver; found JSON block ineffective, exit 2 worked"

### Contradictions
- None found.

### Inferences
- Update order (mine, from DevSquad propagation and OpenSpec sync/archive): (1) write change record with trigger, evidence, old-to-new text; (2) append a superseding ADR if a decision changed (old ADR marked superseded, not edited); (3) edit the plan source of truth and bump `plan vN`; (4) edit tasks.json and dependents-manifest-listed docs; (5) run deterministic gates (links, path-mapping, schema diff) and the LLM audit on the touched sections; (6) mark change record applied. Only after step 6 does the task resume.
- Batched approval presentation: one entry per Major change: title, trigger, what breaks if not approved, old to new diff of plan lines, cost/time effect, recommendation, default if no answer (stay blocked on that branch). Minor and Moderate appear as an FYI list with links to change records.
- Frozen snapshot: keep `plan.approved.vN` read-only and a `CHANGELOG`; do not mutate an approved version in place.

### Gaps
- Whether John wants Moderate changes to need approval is an owner decision, not researchable.
- Hook-level enforcement that the engineer cannot edit an approved snapshot (permissions.deny on the path) not spiked.

## Recommendation, alternatives, rejections, spikes
- Recommendation: file-based change records (OpenSpec-shaped delta + BMAD scope tiers + DevSquad block-until-propagated), superseding ADRs, a diff-scoped Stop/TaskCompleted gate using the dependents manifest, lychee on changed docs with 429 handling, and a milestone-time LLM audit that must cite plan line and file:line. No new tool installed.
- Alternatives: adopt OpenSpec CLI for deltas/archive (npm; licence unchecked); Danger JS if the repo is on GitHub PRs; docs-gate style LLM verifier.
- Rejected: Dredd (archived 2024-11-08); Pact for a solo repo (needs Broker); whole-document LLM comparison (80-98% flag rate); spec-kit/Kiro as change engines (docs silent on amendment); semver for the plan.
- Spike before building: (1) run an LLM plan-vs-diff audit on 3 of John's past repos and hand-label precision; (2) exit-2 Stop-hook gate with diff-scoped semantics; (3) lychee on changed files with and without `--accept 429`; (4) confirm permissions.deny prevents edits to the approved snapshot.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| OpenSpec update/archive (delta specs) | https://github.com/Fission-AI/OpenSpec/blob/main/docs/workflows.md | Change folders, delta merge, verify, archive | npm CLI + slash commands | 2026-10-16 | Borrow shape; adopt only if wanted ready-made |
| BMAD correct-course | https://github.com/bmad-code-org/BMAD-METHOD (skills/bmad-correct-course/SKILL.md, commit cfba3ff) | Impact analysis, old-to-new edit proposals, Minor/Moderate/Major, approval | skill | 2026-10-16 | Borrow protocol; skip framework |
| Danger JS | https://datadef.io/guides/en/docs-checks-in-ci | PR rule: code path changed without docs path, warn/fail | CI | 2026-10-16 (via guide only) | Fallback; a shell script does the same |
| lychee | https://lychee.cli.rs/troubleshooting/rate-limits/ | Link checker; 429 noise needs config | CLI/CI | 2026-10-16 | Use on changed docs, tune retries/accept |
| Schemathesis | https://github.com/schemathesis/schemathesis | MIT; OpenAPI/GraphQL schema-conformance testing | CLI/CI | 2026-10-16 | Use only if an OpenAPI schema exists |
| Dredd | https://github.com/apiaryio/dredd | API description vs implementation | CLI | 2026-10-16 | Reject: archived 2024-11-08 |
| Pact can-i-deploy | https://docs.pact.io/pact_broker/can_i_deploy | Consumer-contract deploy gate via Broker | Broker + CI | 2026-10-16 | Skip for solo repo |
| Atlas migrate diff/lint | https://atlasgo.io/versioned/diff | Schema diff against dev DB, migration lint | CLI/CI | 2026-10-16 | Use if repo has a DB; migra not opened |
| DocPrism | https://arxiv.org/abs/2511.00215 | LLM code-doc inconsistency detector, LCEF filter | research code (not run) | 2026-10-16 | Reference: copy filter idea |
| Cascade | https://arxiv.org/abs/2604.19400 | Test-generation-based doc-code consistency, precision-first | research (not run) | 2026-10-16 | Reference only; Java-focused |
| Doc-Drift | https://newsletter.nerdnoir.com/p/documentation-needs-a-feedback-loop | PR Action flagging specific doc contradictions; GPT-4o-mini | GitHub Action (not run) | 2026-10-16 | Reference; self-reported numbers |
| Verdict | https://github.com/verdict-ci/verdict | Intent-vs-diff fidelity gate; 1 star | CLI/Action (not run) | 2026-10-16 | Reference only; unvetted |
| docs-gate | https://github.com/sarvesh-ghl/docs-gate | Regex path map plus LLM verification, free when docs untouched | GitHub Action (not run) | 2026-10-16 (Exa highlights) | Reference only |
