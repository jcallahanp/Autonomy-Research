# Engineer planning: the plan set, its approval, change control, drift audits and task splitting

The engineer should write a small, committed plan set before code, not a framework's full template stack. The spec-driven tools all split the work into the same layers: what and why, how, and tasks. Kiro writes three files (https://kiro.dev/docs/specs/); OpenSpec writes a "1-2 pages" proposal plus behaviour specs (https://github.com/Fission-AI/OpenSpec schemas/spec-driven/schema.yaml:44 and :57 (commit f80d860)); spec-kit has spec, plan and tasks templates (https://github.com/github/spec-kit templates/spec-template.md:98 (commit f6e72bc)). Reviewers find the large sets verbose: Fowler's site (https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html) and the Thoughtworks Radar (https://www.thoughtworks.com/radar/techniques/spec-driven-development) both say so. The controlled evidence on spec volume is mixed. One study found a 9.2-point gain at roughly 28 times the tokens (https://iscap.us/proceedings/2026/pdf/6729.pdf). A thesis found no consistent coverage gain (https://mskre.no/thesis.pdf). A third study found context files add more than 20% cost (https://arxiv.org/abs/2602.11988).

John signs only the owner-facing parts. Approval is recorded as a file holding the hashes of the approved files, which goes stale on any edit (the Spec Guard pattern, https://github.com/jpstone/spec-guard), plus a record that carries his identity, because an in-session "Approve" records none (https://docs.plannotator.ai/learn/code-context/approve-ai-coding-plan-before-execution).

Mid-course changes go through dated change records:
- scope tiers taken from BMAD correct-course (https://github.com/bmad-code-org/BMAD-METHOD skills/bmad-correct-course/SKILL.md:260 (commit cfba3ff))
- changed decisions get a new superseding ADR rather than an edit (https://github.com/joelparkerhenderson/architecture-decision-record)
- DevSquad's rule that work stays blocked until every flagged document is updated or waived (https://microsoft.github.io/devsquad-copilot/concepts/spec-amendment/)
- enforcement by the dependents manifest and exit-2 Stop hook already chosen in wave 1 (/home/user/Autonomy-Research/research/findings/engineer-context.md:117-118)

Drift checks should be deterministic first. CI checks detect "proxies for outdatedness" (https://datadef.io/guides/en/docs-checks-in-ci). lychee produces false broken links under rate limiting (https://lychee.cli.rs/troubleshooting/rate-limits/). LLM audits are noisy: an unfiltered LLM flags 98% of items, and filtering brings that to 14% at a precision of 0.63 (https://arxiv.org/abs/2511.00215). They are therefore advisory only, limited to the current diff, and must cite the plan line and the code line.

Task success falls as tasks grow. METR's noise-adjusted 80% horizon for Opus 4.6 is about 1h16m of human work (https://metr.org/notes/2026-03-20-impact-of-modelling-assumptions-on-time-horizon-results/). SWE-Bench Pro tasks average 107 lines over 4.1 files, and the best models scored about 23% on them (https://scale.com/blog/swe-bench-pro). Anthropic's own harness failed by trying "to do too much at once" (https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents). Splitting too finely also loses: one benchmark peaks at about six steps (https://www.alphaxiv.org/abs/2605.21516), and in a 51-class-task study with Sonnet and Haiku, splitting one class across two agents opened a 25-39 point coordination gap, measured as specification detail was stripped across levels L0 to L3 (https://arxiv.org/pdf/2603.24284) (corrected after verification, 2026-10-16).

The proposed rule is one fresh session, one commit and one runnable check per task, at about 1-4 files and about 100 lines. Those caps are worker inference and must be spiked. Overall confidence: medium.

## Questions and answers

### Q1. What plan set should the engineer produce before code: files, formats, sizes, what is machine-readable?

**Confidence: medium.** The formats are documented. The sizes and the exact file list are worker inference. No source compares plan-set variants on agent adherence.

**What the tools converge on.**
- **Kiro:** "Every spec generates three key files that form the foundation of your specification:" (https://kiro.dev/docs/specs/). Its design file carries "Build design docs with sequence diagrams and architecture plans" (same page).
- **OpenSpec:** the proposal is "Keep it concise (1-2 pages). Focus on the \"why\" not the \"how\" -", and "A spec is a behavior contract, not an implementation plan." (https://github.com/Fission-AI/OpenSpec schemas/spec-driven/schema.yaml:44 and :57 (commit f80d860)).
- **spec-kit:** uses numbered "System MUST" requirements with a NEEDS CLARIFICATION marker (https://github.com/github/spec-kit templates/spec-template.md:98 (commit f6e72bc)). Its templates are spec 131, plan 113, tasks 252, constitution 50 and checklist 45 lines (same citation). Tasks carry "Include exact file paths in descriptions" (templates/tasks-template.md:20). Checklists act as "a read-only gate" (templates/commands/implement.md:57).
- **Superpowers:** "A plan is the set of decisions the implementer cannot make alone." (https://github.com/obra/superpowers skills/writing-plans/SKILL.md:157 (commit bb92a77)). It bans lines that "decide nothing" (skills/writing-plans/SKILL.md:159). It splits multi-subsystem specs so "Each plan should produce working, testable software on its own." (skills/writing-plans/SKILL.md). Brainstorming writes a committed design doc (skills/brainstorming/SKILL.md:157).
- **Agent OS:** keeps a product layer (mission, roadmap, tech stack) above per-feature specs (https://buildermethods.com/agent-os/v2/workflow; the "run only once" wording is a fetch-tool paraphrase).

**Evidence on size versus benefit.**
- **More scaffolding:** a Spec-Kit-style spec, plan and task list raised the weighted pass rate from 78.2% to 87.4%, at "roughly 28 times the tokens and 15 times as much wall-clock time" (https://iscap.us/proceedings/2026/pdf/6729.pdf). Against that, "adding more automated scaffolding before implementation did not consistently improve FR coverage." (https://mskre.no/thesis.pdf).
- **Granularity:** structured specs work best, and "organizing specifications at the module level provides the best overall balance" (https://conf.researchr.org/details/ase-2026/ase-2026-research-track/219/From-Vibe-to-Spec-An-Empirical-Study-to-Demystify-Specifications-in-Code-Generation).
- **Context files:** they raise cost "by over 20% on average" with no reliable gain (https://arxiv.org/abs/2602.11988).
- **Reviewers:** they call the large sets "very verbose and tedious to review" and report that "I frequently saw the agent ultimately not follow all the instructions." (https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html). The Radar says some tools produce "lengthy spec files" that are "hard to review" (https://www.thoughtworks.com/radar/techniques/spec-driven-development).

**Wave 1 already decided** a Markdown spec plus a JSON task list with `passes`, with approval recorded in a file (/home/user/Autonomy-Research/research/findings/engineer-intake.md:77). It also decided on `tasks.json`, `PROGRESS.md`, `docs/DEPENDENTS.md` and superseding ADRs (/home/user/Autonomy-Research/research/findings/engineer-context.md:117).

**Recommended plan set** (worker inference, plan-set note; all files under `docs/plan/`, committed):

| # | File | Format and size | What it holds |
|---|---|---|---|
| 1 | `brief.md` | Prose, 1-2 pages; the owner-facing file | Goal, non-goals, users, success measures, costs and risks |
| 2 | `requirements.md` | EARS, 15-40 lines | One "When X, the system shall Y" per line, each with an ID and a Given/When/Then acceptance line |
| 3 | `architecture.md` | One diagram plus 10-20 lines | Diagram source; see Contradictions for C4 versus flowchart |
| 4 | `integrations.yaml` | YAML; a script can check it against `.env.example` | Per service: purpose, auth type, env var name only, free or paid and price, owner action, fallback |
| 5 | `contracts/` | OpenAPI, JSON Schema or SQL DDL; no prose copy | Only where two parts talk to each other |
| 6 | Task list | One entry per task | id, title, requirement IDs, files, depends_on, acceptance test path, status |
| 7 | `tests/acceptance/` | Executable tests | One test per requirement ID |
| 8 | `decisions/NNNN-*.md` | MADR, 10-25 lines each | Only choices with real alternatives |

The worker estimates the human-reviewed text at about 150-250 lines, excluding contracts. Prose holds the "why"; YAML or JSON holds anything a script checks. The worker drops spec-kit's research.md, quickstart.md, per-story checklists and constitution, since CLAUDE.md holds the rules. The worker's reading of the evidence is that a spec helps most when it supplies what the task lacks (intent, constraints, success criteria), and that size should scale with the number of decisions, not with a template.

**Contradictions.**
- *Spec benefit.* The ISCAP study's gain (https://iscap.us/proceedings/2026/pdf/6729.pdf) disagrees with the thesis's "did not consistently improve" (https://mskre.no/thesis.pdf). The worker attributes the gap to set-up: ISCAP used single-function tasks with no SRS, while the thesis started from an SRS plus a fixed API contract. Both used LLM-generated specs, and neither tests intent a human confirmed. The two are consistent with "the contract is the essential file". Whether a human-confirmed brief adds more is unresolved (spike S1, S3).
- *Task file format.* The plan-set note proposes `tasks.yaml`. The task-splitting note and wave 1 use `tasks.json` (/home/user/Autonomy-Research/research/findings/engineer-context.md:117). The evidence favours JSON: Anthropic found "the model is less likely to inappropriately change or overwrite JSON files compared to Markdown files." (https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents). No source compares YAML with JSON, and wave 1 left JSON versus Markdown open (/home/user/Autonomy-Research/research/findings/engineer-intake.md:63). Use `tasks.json`.
- *Architecture diagram.* The plan-set note proposes a Mermaid C4 container diagram, with a "plain flowchart if no C4 skill". The feasibility findings rejected "**Mermaid C4 as default.** Experimental (https://mermaid.js.org/syntax/c4.html)." (/home/user/Autonomy-Research/research/findings/engineer-feasibility.md:319). The registry keeps "Use context + container levels for the as-is map" (/home/user/Autonomy-Research/research/tool-registry.md:132). The evidence favours a plain Mermaid flowchart drawn at C4 container level, not Mermaid's experimental C4 syntax.

### Q2. How does John approve the plan, and how is approval recorded?

**Confidence: medium.** The pattern is assembled from tools that were read, not tested. The hash-mismatch hook and single-user PR approval are unverified.

**What approval must cover.**
- Superpowers makes approval a hard gate, "Nothing gets built until your human partner approves the full", and limits it: "Approval covers what you showed them. A description you haven't written isn't approved." (https://github.com/obra/superpowers skills/brainstorming/SKILL.md:180 and :202 (commit bb92a77)).
- Plannotator says a plan should state "the intended outcome, boundaries, important implementation choices, risks, and validation". Its in-session Approve "does not record reviewer identity or authorization." (https://docs.plannotator.ai/learn/code-context/approve-ai-coding-plan-before-execution).
- Kiro gates each phase except Quick Spec, "Generate requirements, design, and tasks in one pass without approval gates.", and has a "select the floating **Review** button" comment flow (https://kiro.dev/docs/specs/).

**How the record can be made.**
- Spec Guard: "Approval binds a hash of exactly what was reviewed; edit a Spec afterward and the approval goes stale", and "The agent literally cannot stamp its own approval." (https://github.com/jpstone/spec-guard).
- GitHub protected branches can "dismiss stale pull request approvals when commits are pushed that affect the diff in the pull request." They also require that "any pull request that affects code with a code owner must be approved by that code owner" (https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches).

**Recommended procedure** (worker inference, plan-set note):

1. **What John signs.** Goals and non-goals, the scope list, acceptance criteria written as observable outcomes, the gates for later actions (spend, publish, delete, login), costs (the monthly total and each paid service with its price), and the risks with what the agent does if blocked.
2. **What John does not sign.** Architecture, schema, contracts and the task list. A fresh-context reviewer checks those against the signed brief.
3. **The record.** `docs/plan/approval.json` = {approved_by, date, files:{path: sha256}, scope_version, gates}. It is written only when John's own message, or a PR approval from his account, says yes.
4. **Enforcement.** A start-up or PreToolUse hook recomputes the hashes of brief.md, requirements.md and integrations.yaml and stops code edits on a mismatch.
5. **The version marker.** An annotated or signed tag, `plan-approved-N`, marks the approved version.
6. **Later changes.** Any edit to a hashed file needs re-approval of the diff only, shown as a plain-language summary.
7. **Effort split.** An Express path covers low-risk defaults, which the agent states aloud. The full path covers anything touching money, data deletion or outbound messages.

This extends the wave 1 decision of "approval recorded in a file, not via ExitPlanMode alone" (/home/user/Autonomy-Research/research/findings/engineer-intake.md:77).

**Contradictions.** None found among the opened sources. The single-user GitHub route is unverified, because GitHub may not let John approve his own PR (see Open questions). A hash file plus message-based approval may be the practical single-user route (worker inference).

### Q3. How are mid-course changes controlled so every dependent document is updated?

**Confidence: medium.** The tool docs were read; the tier boundaries are the worker's design and untested.

**What the sources do.**
- **ADRs:** practice is to "amend the ADR by adding new information, or supersede the ADR by creating a new ADR" (https://github.com/joelparkerhenderson/architecture-decision-record).
- **OpenSpec:** you can "update planning artifacts whenever implementation reveals something new". Its verify step "validates implementation against your artifacts across three dimensions" (https://github.com/Fission-AI/OpenSpec/blob/main/docs/workflows.md).
- **BMAD correct-course:** it exists to "Manage significant changes during sprint execution by analyzing impact across all project artifacts and producing a structured Sprint Change Proposal." It classes scope, as in "**Major**: Needs fundamental replan with PM/Architect involvement", and asks "Do you approve this Sprint Change Proposal for implementation? (yes/no/revise)" (https://github.com/bmad-code-org/BMAD-METHOD skills/bmad-correct-course/SKILL.md:8, :244, :260 (commit cfba3ff)).
- **DevSquad:** the implementer "returns a `spec-drift` flag with a structured payload". The refine agent "does not edit these artifacts in amendment mode. It flags them." The coordinator "blocks resume until each flagged artifact is either updated" (https://microsoft.github.io/devsquad-copilot/concepts/spec-amendment/).
- **spec-kit:** a change "means revisiting the specification and creating new implementation plans" (https://github.com/github/spec-kit/blob/main/spec-driven.md). Its README offers a converge loop rather than an amend step: "Repeat implement → converge until convergence reports Converged." (https://github.com/github/spec-kit).
- **Kiro:** its feature-specs page says only "Implementation can adapt" (https://kiro.dev/docs/specs/feature-specs/).

**Wave 1 enforcement.** `docs/DEPENDENTS.md` is "the manifest of documents each kind of scope change must touch". A Stop/TaskCompleted hook "blocks with exit 2 on failure, honours `stop_hook_active`, and logs when it fails open after the eight-block override" (/home/user/Autonomy-Research/research/findings/engineer-context.md:117-118). A doc-sentinel PR found a "Stop hook auto-dispatching a drift resolver; found JSON block ineffective, exit 2 worked" (/home/user/Autonomy-Research/research/tool-registry.md:192).

**Replan procedure** (worker inference, change-control note). It adapts BMAD's scope classes and DevSquad's rule that work stays blocked until documents are updated.

*Tiers:*
- **Minor:** the change stays inside an approved task's acceptance criteria. The engineer edits and logs it.
- **Moderate:** tasks, order or approach change, but goals and acceptance criteria do not. The engineer applies a change record and tells John in the digest.
- **Major:** the goal, scope, acceptance criteria or a cost or risk ceiling changes, or the change touches an irreversible or external action. The engineer stops that branch, writes a change proposal and waits for John's batched approval, while continuing unaffected tasks.

*Triggers for a formal replan:* a failed spike, a blocked dependency, a scope change from John, or a contradiction between an approved acceptance criterion and reality.

*Update order:*
1. Write the change record: trigger, evidence, old-to-new text.
2. Add a superseding ADR if a decision changed. The old ADR is marked superseded, not edited.
3. Edit the plan's source of truth and bump `plan vN`.
4. Edit `tasks.json` and every document listed in the dependents manifest.
5. Run the deterministic gates and the LLM audit on the touched sections.
6. Mark the change record applied. The task resumes only after step 6.

*Record keeping:* keep `plan.approved.vN` read-only, plus a CHANGELOG. Use a `plan vN` counter, not semver; no opened tool documents semver for plans.

*Batched presentation to John:* one entry per Major change, giving the title, trigger, what breaks if it is not approved, the old-to-new diff of plan lines, the cost and time effect, a recommendation, and the default if he does not answer (that branch stays blocked). Minor and Moderate changes appear as an FYI list.

**Contradictions.** Stop-hook blocking: the hooks docs say a JSON decision or exit 2 both block, while the doc-sentinel PR saw only exit 2 work. This is carried from wave 1 and is still "Unresolved; settle by a spike on the engine's current version." (/home/user/Autonomy-Research/research/findings/engineer-context.md:108). Use exit 2 until spiked. Kiro and spec-kit are silent on mid-build amendment rather than in conflict.

### Q4. Which drift-detection tools are worth running, and how noisy are they?

**Confidence: medium.** The published noise data covers only lychee and LLM checkers. The LLM data is for docstring-versus-code, not plan-versus-code.

**Deterministic layer.**
- **Path-mapping rule (Danger-style).** The guide says "Teams usually start with warn rather than fail" and "CI detects proxies for outdatedness rather than outdatedness itself" (https://datadef.io/guides/en/docs-checks-in-ci). The same guide gives no false-positive rates for lychee or Vale. Its only advice is to exclude internal hosts so the link job does not "cry wolf" (same URL; worker's reading of the page).
- **lychee.** It "will report a lot of broken links with `429` as a status code." Its last-resort fix is "you might want to accept `429` as a valid status code." (https://lychee.cli.rs/troubleshooting/rate-limits/).
- **Schemathesis.** "licensed under the terms of the MIT license". It tests responses against the OpenAPI or GraphQL schema and makes no false-positive claim (https://github.com/schemathesis/schemathesis).
- **Atlas.** `migrate diff` needs "a URL to a Dev Database that will be used to compute the diff" (https://atlasgo.io/versioned/diff).
- **Pact.** can-i-deploy needs "All required verification results are published and successful." and a Broker (https://docs.pact.io/pact_broker/can_i_deploy).
- **Dredd.** "This repository was archived by the owner on Nov 8, 2024. It is now read-only." (https://github.com/apiaryio/dredd).

**LLM layer.**
- **DocPrism.** "LCEF reduces DocPrism's inconsistency flag rate from 98% to 14%", and it "achieves a precision of 0.63 without performing any fine-tuning" (https://arxiv.org/abs/2511.00215).
- **Cascade.** It reports an inconsistency only when it is backed by a test, and it found "13 previously unknown inconsistencies, of which 10 have subsequently been fixed" (https://arxiv.org/abs/2604.19400).
- **Doc-Drift.** It flags only specific contradictions. Its author reports "Maybe one in every dozen findings needs to be dismissed." and "The total spend reported was a whopping $0.03." It warns that "The system catches specific contradictions, not conceptual drift." (https://newsletter.nerdnoir.com/p/documentation-needs-a-feedback-loop).
- **Verdict.** It warns of "false positives born of mismatched scope, not real defects." (https://github.com/verdict-ci/verdict).

**Worth running** (worker inference, change-control note):
1. The wave 1 dependents-manifest gate, limited to the drift the current diff introduces.
2. lychee on changed docs, with 429 handling.
3. Schemathesis, only if the project has an OpenAPI schema.
4. Atlas, only if it has a database.
5. A milestone-time LLM audit. It gets one plan section plus the diff that implements it, must cite the plan line and file:line, stays silent otherwise, and is advisory only: it never edits the approved plan.

The audit should run on a Sonnet-class model; the cost is unmeasured. Skip Pact for a solo repo, since it needs a Broker and two parties.

**Contradictions.** Doc-Drift's self-reported "one in every dozen" (https://newsletter.nerdnoir.com/p/documentation-needs-a-feedback-loop) sits against DocPrism's measured precision of 0.63 (https://arxiv.org/abs/2511.00215). The tasks differ: Doc-Drift checks diff-scoped contradictions in a toy repo and one demo repo, while DocPrism checks whole-function consistency on 1,991 real pairs. Unresolved; a hand-labelled spike on John's repos would settle it (S6).

### Q5. How narrow must tasks be, and what are the splitting rules?

**Confidence: medium.** That success falls with size is consistent across sources. The numeric caps are inference. The evidence on over-splitting comes mostly from small programs, plus one preprint of weak provenance.

**Size versus success.**
- METR's noise-adjusted figures for Opus 4.6 are "Logistic (Reg. Fix) | 7h 38m (-36%) | 1h 16m (+9%)" for the 50% and 80% horizons. METR adds: "The variation in the results from reasonable methods is ~1.5x in 50% TH and 2x in 80% TH for Opus 4.6." (https://metr.org/notes/2026-03-20-impact-of-modelling-assumptions-on-time-horizon-results/). The 80% figure is "not fully independent" of the 50% one (https://metr.org/notes/2026-01-22-time-horizon-limitations/).
- On Claude Code, METR found "neither Claude Code nor Codex outperform the default scaffolds METR uses, at least when measuring the time horizon of Opus 4.5 and GPT-5." (https://metr.org/notes/2026-02-13-measuring-time-horizon-using-claude-code-and-codex/). Opus 4.5's 50% horizon is 320 minutes on TH1.1 (https://metr.org/blog/2026-1-29-time-horizon-1-1/).
- SWE-Bench Pro tasks average "107.4 lines of code across 4.1 files", where the best models scored about 23% (https://scale.com/blog/swe-bench-pro). "Model performance significantly degrades as solutions require more lines to be added and files to be edited." (https://labs.scale.com/leaderboard/swe_bench_pro_public). A secondary source reports "context overflow and endless walking of the file tree" (https://dataist.ai/research/top-coding-agents-solve-under-a-quarter-of-swe-bench-pro-tasks/).
- Anthropic: "the agent tended to try to do too much at once". Working "on only one feature at a time ... turned out to be critical" (https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents).
- Claude Code docs: performance "degrades as context fills". "If you could describe the diff in one sentence, skip the plan." Good specs "name the files and interfaces involved, state what is out of scope, and end with an end-to-end verification step". "After two failed corrections, `/clear`" (https://code.claude.com/docs/en/best-practices).
- spec-kit's maintainers: "agents can start to lose track of the plan, ignore tasks, or hallucinate — usually right before or after context compaction is triggered." (https://github.github.com/spec-kit/concepts/complex-features.html).

**Why John's Superpowers tasks were too wide.**
- Superpowers 7.0.0 defines "A task is the smallest unit that carries its own test cycle". Each step is "one action with a checkable result", and it says to "split only where a reviewer could meaningfully reject one task while approving its neighbor." (https://github.com/obra/superpowers skills/writing-plans/SKILL.md:36-41, :45, :37-40 (commit bb92a77)). Its only size rule is the independent-subsystem check (SKILL.md:19-21).
- Its executor treats "isolated functions, clear specs, 1-2 files" as mechanical (skills/subagent-driven-development/SKILL.md:188). It caps fix rounds at 5 (:75).
- Worker inference: nothing caps a task's files or context, so one "task" can span many files in one long implementer session. That matches the hallucination mode spec-kit documents.

**How other tools scope tasks.**
- Ralph: "One item per loop ... if it starts going off the rails, then you need to narrow it down", because "you only have approximately 170k of context window" (https://ghuntley.com/ralph/). One Ralph prompt variant still says "choose the most important 10 things." (same URL). The how-to-ralph-wiggum repo: "Each iteration = one fresh context window = one task from IMPLEMENTATION_PLAN.md = one commit", with a "40-60% context utilization for \"smart zone\"" (https://github.com/ghuntley/how-to-ralph-wiggum).
- spec-kit: scopes runs with "/implement only execute tasks 1-10, then stop and report progress" (https://github.github.com/spec-kit/concepts/complex-features.html, from https://github.com/github/spec-kit/discussions/2914). One user advises "split task to atomic points by yourself" (https://github.com/github/spec-kit/discussions/1784).
- Kiro: a user reports "A single task execution probably doesn't need the full requirements and design docs" (https://github.com/kirodotdev/Kiro/issues/2324).
- Fowler's site: "The requirements document turned this small bug into 4 \"user stories\" with a total of 16 acceptance criteria" (https://www.martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html).

**Over-splitting also hurts.**
- Terminal-Bench v2: success "peaks at a specific number of steps (six, in this case) and declines if the task is either too unified or too fragmented". Also, "specifying only the initial steps ... can achieve higher pass rate than fully structured workflows." (https://www.alphaxiv.org/abs/2605.21516).
- Splitting one class across two agents: a 25–39pp coordination gap (stated in the abstract), measured as specification detail was stripped (levels L0 to L3, 51 class tasks, Sonnet and Haiku); the paper's wording is "persistent specification gap" (https://arxiv.org/pdf/2603.24284) (corrected after verification, 2026-10-16).
- "overly fine nodes add interface overhead" (https://arxiv.org/html/2607.29529v1).
- An unreviewed preprint names "an over-decomposition regime where coordination overhead dominates" (https://clawrxiv.io/abs/2604.00690; a hypothesis only).

**Ordering and parallelism.**
- Beads offers "`bd ready` | List tasks with no open blockers." and dependency links of types blocks, related and parent-child (https://github.com/steveyegge/beads README.md:73-76 (commit dff9492)).
- spec-kit's [P] marker means "different files, no dependencies" (templates/tasks-template.md:16-19,81).
- Superpowers dispatches in parallel only for tasks "without shared state or sequential dependencies" (skills/dispatching-parallel-agents/SKILL.md:3).
- Naive file-parallel agents "produce conflicting interfaces, requiring redundant re-generation that incurs extra costs" (https://arxiv.org/html/2606.00953).
- Claude Code worktrees "run separate CLI sessions in isolated git checkouts" (https://code.claude.com/docs/en/best-practices).

**Splitting rules** (worker inference, task-splitting note; the numbers must be spiked):
1. One task = one fresh session, one commit and one acceptance check the agent can run. No check, no task.
2. Cap each task at about 1-4 files and about 100 changed lines, roughly 15-45 minutes of human work. The SWE-Bench Pro average sits at the models' edge, so stay below it.
3. Split on seams where an interface can be written down first (a signature, schema or test). Never split inside one module or class.
4. Fold scaffolding, config and docs into the task that needs them. Do not make 2-minute tasks.
5. The planner records the files to read for each task. Stop and re-split past about 50% of the context window or after 2 failed corrections.
6. Repeat the global constraints verbatim in every task. Task text is self-contained: files, interfaces, out-of-scope, check.
7. Re-split when a task fails its check twice, touches files that are not listed, or needs an interface change.
8. Revisit the caps at each model release.

Tasks live in a `tasks.json` DAG with `files`, `depends_on`, the check and `passes`, and the supervisor computes `ready`. Run sequentially by default. Use parallel worktrees only for ready tasks with disjoint `files` and no shared interface. The worker prefers files, lines, check and context share over a time box, because METR's human-time estimates are noisy.

**Contradictions.**
- *Is decomposition still needed?* Anthropic's harness-design post says "I started by removing the sprint construct entirely." as models improved to Opus 4.6 (https://www.anthropic.com/engineering/harness-design-long-running-apps). The Claude Code docs (https://code.claude.com/docs/en/best-practices) and Ralph (https://ghuntley.com/ralph/) still recommend narrow tasks. The worker reconciles them: both hold, depending on whether a runnable check exists and how close the task is to the model's limit. Rule 8 covers the drift over time.
- *Narrow versus too fragmented.* "One item per loop" (https://github.com/ghuntley/how-to-ralph-wiggum) sits against Terminal-Bench's finding that too-fine steps lose (https://www.alphaxiv.org/abs/2605.21516). The reconciliation: a task is small in context, not in its number of micro-steps (Superpowers' own fold-in rule).
- *Ralph is not uniform.* The same page says both "One item per loop" and "choose the most important 10 things." (https://ghuntley.com/ralph/). The evidence favours one item when runs go wrong, as the page itself says.
- *Superpowers "2-5 minute" steps.* That figure came from the brief's memory. It is not in the 7.0.0 file read (skills/writing-plans/SKILL.md:45, commit bb92a77), so it is unverified for this version.
- *Opus 4.6 horizons.* Third-party readings of METR's data differ from METR's own note. Those readings were seen only in search highlights, so this is listed under Open questions.

### Q6. Recommendation, alternatives, rejected candidates and spike list

**Confidence: medium.** The three facet recommendations are consistent with each other and with wave 1. The specific caps, tiers and file list are worker inference.

**Recommended plan set and approval.** Use the lean set in Q1, all free with nothing to install:
- `brief.md`
- `requirements.md` in EARS
- `architecture.md` as a plain Mermaid flowchart at container level
- `integrations.yaml`
- `contracts/`
- `tasks.json`
- `tests/acceptance/`
- MADR decisions, only for real choices

The engineer writes it after a Superpowers-style brainstorm with the hard gate (https://github.com/obra/superpowers skills/brainstorming/SKILL.md:180). John signs the brief, the acceptance criteria, the integrations and costs, and the gates. Approval is recorded as a hash-bound `docs/plan/approval.json` (Spec Guard pattern, https://github.com/jpstone/spec-guard) plus an annotated tag `plan-approved-N`. GitHub protected-branch review is used where John can do it from his own account (https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches). A hook refuses code edits on a hash mismatch (worker inference; spike S2).

**Recommended change-control procedure.** File-based change records in OpenSpec's change-folder shape (https://github.com/Fission-AI/OpenSpec/blob/main/docs/workflows.md), the BMAD Minor/Moderate/Major tiers with explicit approval for Major changes (https://github.com/bmad-code-org/BMAD-METHOD skills/bmad-correct-course/SKILL.md:244,260 (commit cfba3ff)), superseding ADRs (https://github.com/joelparkerhenderson/architecture-decision-record), DevSquad's rule that work stays blocked until documents are updated (https://microsoft.github.io/devsquad-copilot/concepts/spec-amendment/), and the six-step update order in Q3. These are enforced by the wave 1 exit-2 Stop/TaskCompleted gate over `docs/DEPENDENTS.md` (/home/user/Autonomy-Research/research/findings/engineer-context.md:117-118), limited to the current diff. For drift, use lychee with 429 handling (https://lychee.cli.rs/troubleshooting/rate-limits/), Schemathesis or Atlas only where they apply, and a milestone LLM audit that cites plan lines and code lines and is advisory.

**Recommended task splitting.** Keep Superpowers' fresh-subagent-per-task executor (skills/subagent-driven-development/SKILL.md:188). Replace its sizing with the task contract in Q5, rules 1-8. Store tasks as a `tasks.json` DAG with `ready` computed by the supervisor. Bound each session with `--max-turns` and a context share. Wave 1 already set "two attempts per task, then a blocked note" (/home/user/Autonomy-Research/research/findings/engineer-context.md:119).

**Alternatives.**
- OpenSpec CLI for proposals, deltas and archive. It is lighter, and Thoughtworks put it in Assess in April 2026 (https://www.thoughtworks.com/radar/tools/openspec). npm; licence unchecked.
- Kiro's three files written by hand (https://kiro.dev/docs/specs/).
- spec-kit used only as prompt patterns: the NEEDS CLARIFICATION marker, the read-only checklist gate, [P] markers and phase scoping (https://github.com/github/spec-kit templates/commands/implement.md:57).
- Danger JS if the repo works through GitHub PRs (https://datadef.io/guides/en/docs-checks-in-ci).
- A docs-gate-style LLM verifier, which is search-highlight evidence only (see Open questions).
- Beads, if multi-agent claims or cross-session dependency queries become necessary (https://github.com/steveyegge/beads README.md:73-76 (commit dff9492)).
- Ralph's one-item-per-loop with the outer supervisor owning the bounds (https://github.com/ghuntley/how-to-ralph-wiggum).
- Plannotator as an optional plan viewer, not as the record (https://docs.plannotator.ai/learn/code-context/approve-ai-coding-plan-before-execution).

**Rejected, with reasons.**

| Candidate | Reason |
|---|---|
| spec-kit wholesale | Verbose (https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html, https://www.thoughtworks.com/radar/techniques/spec-driven-development) |
| BMAD as a framework | Heavy; borrow correct-course only |
| Kiro IDE | Not Claude Code; "Session Too Long" (https://github.com/kirodotdev/Kiro/issues/2324) |
| Tessl | Spec-as-source, beta, described only through the Fowler article |
| Spec Guard, Plannotator, Verdict or Doc-Drift as dependencies | Small or unvetted projects; copy the ideas (https://github.com/jpstone/spec-guard, https://github.com/verdict-ci/verdict) |
| ExitPlanMode approval alone | No identity recorded (https://docs.plannotator.ai/learn/code-context/approve-ai-coding-plan-before-execution; /home/user/Autonomy-Research/research/findings/engineer-intake.md:77) |
| Dredd | Archived 2024-11-08 (https://github.com/apiaryio/dredd) |
| Pact for a solo repo | Needs a Broker (https://docs.pact.io/pact_broker/can_i_deploy) |
| Whole-document LLM comparison | 98% flag rate unfiltered (https://arxiv.org/abs/2511.00215) |
| spec-kit or Kiro as change engines | Their docs are silent on amendment (https://github.com/github/spec-kit, https://kiro.dev/docs/specs/feature-specs/) |
| Semver for the plan | No tool documents it (worker inference) |
| Taskmaster auto-expand as the sizing authority | Thresholds not read |
| Parallel fan-out by default | Cost rises, quality does not (https://arxiv.org/html/2606.00953) |
| Mermaid C4 syntax as default | Experimental (/home/user/Autonomy-Research/research/findings/engineer-feasibility.md:319) |

Traycer was not researched.

**Spike list (must be tried for real before building).**

*Plan set and approval:*
- S1. Write the plan set for one real John project and time his review.
- S2. A hook that blocks code edits on an approval-hash mismatch, in the cloud runtime. Check that permissions.deny stops edits to `plan.approved.vN`.
- S3. Agent adherence with a 1-page brief versus the full set, on one task.
- S4. Whether John can approve a PR on a single-user repo with branch rules on, from the GitHub mobile app.

*Change control and drift:*
- S5. The exit-2 Stop-hook gate, limited to the current diff, on the current engine version.
- S6. An LLM plan-versus-diff audit on 3 of John's past repos, with precision labelled by hand.
- S7. lychee on changed files, with and without `--accept 429`.

*Task splitting:*
- S8. 10 John-style tasks at about 50, 100 and 300 lines on Sonnet 5.5 and Opus 5.5. Record pass on first check, turns and context use, to set the real caps.
- S9. Whether the planner emits accurate `files` lists.
- S10. One-commit tasks versus Superpowers right-sizing, on a repo where John saw hallucination.
- S11. Read METR's raw data for current Claude 80% horizons.
- S12. YAML versus JSON task lists, and Markdown versus JSON (wave 1 spike 7), on plan-following.

## Evidence

All sources were opened on 2026-10-16. "clone" means a read-only git clone in a mktemp dir; the commit is given.

**Plan set and approval (notes/plan-set.md)**

- E1. https://kiro.dev/docs/specs/, 2026-10-16, WebFetch. Claim: Kiro writes three files per spec: requirements.md (or bugfix.md), design.md, tasks.md. Quote: "Every spec generates three key files that form the foundation of your specification:"
- E2. https://kiro.dev/docs/specs/, 2026-10-16, WebFetch. Claim: Kiro's Quick Spec skips approval gates; the normal flow has a Review button for comments on exact passages. Quote: "Generate requirements, design, and tasks in one pass without approval gates."
- E3. https://github.com/github/spec-kit templates/spec-template.md:98 (commit f6e72bc), 2026-10-16, git clone. Claim: spec-kit's spec template uses numbered "System MUST" functional requirements, Given/When/Then scenarios and a marker for unresolved items; the templates are spec 131, plan 113, tasks 252, constitution 50 and checklist 45 lines. Quote: "- **FR-006**: System MUST authenticate users via [NEEDS CLARIFICATION: auth method not specified - email/password, SSO, OAuth?]"
- E4. https://github.com/github/spec-kit templates/tasks-template.md:20 (commit f6e72bc), 2026-10-16, git clone. Claim: spec-kit's tasks template groups tasks by user story, with exact file paths and parallel markers. Quote: "- Include exact file paths in descriptions"
- E5. https://github.com/github/spec-kit templates/commands/implement.md:57 (commit f6e72bc), 2026-10-16, git clone. Claim: spec-kit treats checklist boxes as a read-only gate in /implement. Quote: "Treat checklist markers as a read-only gate: scan checkbox state, report status, and ask before proceeding when needed"
- E6. https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html, 2026-10-16, WebFetch. Claim: Fowler site (Birgitta Boeckeler, 2025-10-15): spec-kit made too many repetitive files; Kiro's three files were easier but still too verbose for a small bug. Quote: "Overall they were just very verbose and tedious to review."
- E7. https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html (plan-set note, WebFetch) and https://www.martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html (task-splitting note, Exa), 2026-10-16. Claim: agents do not reliably follow all spec instructions (task-splitting note: the agent ignored instructions and duplicated existing code). Quote (plan-set note): "I frequently saw the agent ultimately not follow all the instructions." Quote (task-splitting note): "the agent ultimately not follow all the instructions."
- E8. https://www.thoughtworks.com/radar/techniques/spec-driven-development, 2026-10-16, WebFetch. Claim: Thoughtworks Radar, SDD in Assess, 2025-11-05: lengthy spec files are hard to review. Quote: "lengthy spec files"; "hard to review" (page text: some tools "generate lengthy spec files that are hard to review"; the fetch tool paraphrased around these phrases)
- E9. https://www.thoughtworks.com/radar/tools/openspec, 2026-10-16, WebFetch. Claim: Thoughtworks Radar April 2026 puts OpenSpec in Assess (propose, apply, archive; spec deltas) and says Spec Kit and Superpowers suit greenfield better than brownfield. Quote: "better suited to greenfield projects than brownfield ones" (as quoted by the fetch tool from the page)
- E10. https://github.com/Fission-AI/OpenSpec schemas/spec-driven/schema.yaml:44 and :57 (commit f80d860), 2026-10-16, git clone. Claim: OpenSpec's default schema makes proposal.md "1-2 pages", followed by per-capability specs/<capability>/spec.md behaviour contracts, design.md and tasks.md. Quote: "Keep it concise (1-2 pages). Focus on the \"why\" not the \"how\" -"; ":57 A spec is a behavior contract, not an implementation plan."
- E11. https://github.com/obra/superpowers skills/writing-plans/SKILL.md:157 (commit bb92a77), 2026-10-16, git clone. Claim: in Superpowers writing-plans, a plan holds only the decisions the implementer cannot make alone, has no placeholders, and is bounded in length by the code; plans are saved to docs/superpowers/plans/YYYY-MM-DD-<feature>.md. Quote: "A plan is the set of decisions the implementer cannot make alone."
- E12. https://github.com/obra/superpowers skills/brainstorming/SKILL.md:157 (commit bb92a77), 2026-10-16, git clone. Claim: Superpowers brainstorming saves a committed design doc at docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md, with goals, non-goals, constraints and decided parts. Quote: "`docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`, committed."
- E13. https://buildermethods.com/agent-os/v2/workflow, 2026-10-16, WebFetch. Claim: Agent OS (Builder Methods) phases are plan-product (mission, roadmap, tech stack), shape-spec, write-spec, create-tasks, implement/orchestrate. Quote: "define the strategic product mission, its projected feature development roadmap, and its technology stack"
- E14. https://iscap.us/proceedings/2026/pdf/6729.pdf, 2026-10-16, PDF text via pdftotext. Claim: in a controlled study (ISCAP 2026), a Spec-Kit-style generated spec, plan and task list raised the weighted test pass rate from 78.2% to 87.4% on 296 matched BigCodeBench comparisons, at roughly 28x tokens and 15x wall-clock. Quote: "The method used roughly 28 times the tokens and 15 times as much wall-clock time of the free-prompting baseline."
- E15. https://mskre.no/thesis.pdf, 2026-10-16, pdftotext. Claim: a master's thesis (automated Spec Kit versus vibe coding, 240 backends) found that more scaffolding did not consistently raise requirement coverage; code organisation in the best runs was clearer with more scaffolding. Quote: "adding more automated scaffolding before implementation did not consistently improve FR coverage."
- E16. https://conf.researchr.org/details/ase-2026/ase-2026-research-track/219/From-Vibe-to-Spec-An-Empirical-Study-to-Demystify-Specifications-in-Code-Generation, 2026-10-16, WebFetch. Claim: ASE 2026 study: fine-grained structured pseudocode specs beat natural language, and module-level granularity is the best balance. Quote: "organizing specifications at the module level provides the best overall balance"
- E17. https://arxiv.org/abs/2602.11988, 2026-10-16, WebFetch. Claim: AGENTS.md study (ETH SRI Lab, Feb 2026): context files raise cost by over 20% with no reliable success gain; instructions are followed, so unnecessary requirements make tasks harder. Quote: "increasing inference cost by over 20% on average" (fetch tool's quote of the abstract)
- E18. https://kiro.dev/docs/specs/, 2026-10-16, WebFetch. Claim: Kiro's design file carries architecture, sequence diagrams and data models; requirements carry EARS and acceptance criteria. Quote: "Build design docs with sequence diagrams and architecture plans" (page bullet list; requirements bullet: "Break down requirements into user stories with acceptance criteria")
- E19. https://github.com/Fission-AI/OpenSpec schemas/spec-driven/schema.yaml:57 (commit f80d860), 2026-10-16, git clone. Claim: in OpenSpec, a spec is externally observable behaviour; internals go in design.md. Quote: "A spec is a behavior contract, not an implementation plan."
- E20. https://github.com/obra/superpowers skills/writing-plans/SKILL.md, 2026-10-16, git clone. Claim: Superpowers splits a multi-subsystem spec into per-subsystem plans, each producing working, testable software, with steps that have checkable results. Quote: "Each plan should produce working, testable software on its own."
- E21. https://github.com/obra/superpowers skills/writing-plans/SKILL.md:159 (commit bb92a77), 2026-10-16, git clone. Claim: Superpowers plan hygiene bans vague lines (task-splitting note: plan placeholders are banned). Quote (plan-set note): "Lines that decide nothing (\"TBD\", \"handle edge cases\", \"add appropriate validation\"," Quote (task-splitting note): "decide nothing (\"TBD\", \"handle edge cases\", \"add appropriate validation\","
- E22. https://buildermethods.com/agent-os/v2/workflow, 2026-10-16, WebFetch. Claim: Agent OS keeps a product-level layer (mission, roadmap, tech stack) once per project, separate from per-feature specs. Quote: "It is typically run only once at the beginning a new project" (fetch-tool paraphrase of the page; treat as paraphrase)
- E23. https://conf.researchr.org/details/ase-2026/ase-2026-research-track/219/From-Vibe-to-Spec-An-Empirical-Study-to-Demystify-Specifications-in-Code-Generation, 2026-10-16, WebFetch. Claim: structured, module-level specs gave the best balance of quality, stability and tokens. Quote: "using fine-grained, structured pseudocode specifications significantly enhances generation stability and quality."
- E24. /home/user/Autonomy-Research/research/tool-registry.md:132, 2026-10-16, local read. Claim: C4 context and container levels, MADR for decisions, EARS and the Volere fit criterion were already adopted in earlier runs. Quote: "Use context + container levels for the as-is map"
- E25. https://github.com/obra/superpowers skills/brainstorming/SKILL.md:180 and :202 (commit bb92a77), 2026-10-16, git clone. Claim: Superpowers makes approval a hard gate and limits approval to what was shown. Quote: "Approval covers what you showed them. A description you haven't written isn't approved."
- E26. https://github.com/obra/superpowers skills/brainstorming/SKILL.md:180 (commit bb92a77), 2026-10-16, git clone. Claim: the gate's wording. Quote: "Nothing gets built until your human partner approves the full"
- E27. https://docs.plannotator.ai/learn/code-context/approve-ai-coding-plan-before-execution, 2026-10-16, WebFetch. Claim: Plannotator (local plan reviewer, page last reviewed 2026-07-18): its in-session Approve records no identity, so keep an authorising record in Git, an issue or a PR. Quote: "does not record reviewer identity or authorization."
- E28. https://docs.plannotator.ai/learn/code-context/approve-ai-coding-plan-before-execution, 2026-10-16, WebFetch. Claim: what a plan must state before approval. Quote: "the intended outcome, boundaries, important implementation choices, risks, and validation" (fetch-tool quote)
- E29. https://github.com/jpstone/spec-guard, 2026-10-16, WebFetch. Claim: Spec Guard (jpstone, an MCP server in a small repo) has three human gates (approve plan, authorize, complete); approval is hash-bound to exactly what was reviewed and goes stale on edit; the packet is stored as JSON in git. Quote: "Approval binds a hash of exactly what was reviewed; edit a Spec afterward and the approval goes stale"
- E30. https://github.com/jpstone/spec-guard, 2026-10-16, WebFetch. Claim: in Spec Guard the agent cannot approve itself. Quote: "The agent literally cannot stamp its own approval."
- E31. https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches, 2026-10-16, WebFetch. Claim: GitHub protected branches support required approving reviews, dismissal of stale approvals when the diff changes, and CODEOWNERS review. Quote: "dismiss stale pull request approvals when commits are pushed that affect the diff in the pull request."
- E32. Same GitHub URL, 2026-10-16, WebFetch. Claim: code-owner approval. Quote: "any pull request that affects code with a code owner must be approved by that code owner"
- E33. https://kiro.dev/docs/specs/, 2026-10-16, WebFetch. Claim: Kiro has approval gates for each phase except Quick Spec, and a Markdown Review flow for comments. Quote: "select the floating **Review** button"

**Change control and drift (notes/change-control-and-drift.md)**

- E34. https://github.com/joelparkerhenderson/architecture-decision-record, 2026-10-16, WebFetch. Claim: ADR practice is to amend by adding information, or to supersede with a new ADR; old text is not rewritten. Quote: "amend the ADR by adding new information, or supersede the ADR by creating a new ADR"
- E35. https://github.com/Fission-AI/OpenSpec/blob/main/docs/workflows.md, 2026-10-16, WebFetch. Claim: OpenSpec lets the agent revise plan artifacts mid-build; the loop is Apply -> (plan changed) -> Update -> Apply. Quote: "you can update planning artifacts whenever implementation reveals something new"
- E36. Same OpenSpec workflows URL, 2026-10-16, WebFetch. Claim: OpenSpec verify checks the implementation against the artifacts for completeness, correctness and coherence. Quote: "validates implementation against your artifacts across three dimensions"
- E37. https://github.com/bmad-code-org/BMAD-METHOD skills/bmad-correct-course/SKILL.md:260 (commit cfba3ff), 2026-10-16, git clone + grep. Claim: BMAD correct-course covers a trigger, impact analysis over the PRD, epics, architecture and UX, old-to-new edit proposals, a Minor/Moderate/Major scope class, and explicit approval. Quote: "**Major**: Needs fundamental replan with PM/Architect involvement"
- E38. BMAD-METHOD skills/bmad-correct-course/SKILL.md:244 (commit cfba3ff), 2026-10-16, git clone. Claim: the approval prompt; BMAD routes by scope class and requires explicit approval before implementing (the change-control note cites SKILL.md:244,260 for this). Quote: "Do you approve this Sprint Change Proposal for implementation? (yes/no/revise)"
- E39. BMAD-METHOD skills/bmad-correct-course/SKILL.md:8 (commit cfba3ff), 2026-10-16, git clone. Claim: the skill's goal. Quote: "Manage significant changes during sprint execution by analyzing impact across all project artifacts and producing a structured Sprint Change Proposal."
- E40. https://microsoft.github.io/devsquad-copilot/concepts/spec-amendment/, 2026-10-16, WebFetch. Claim: in DevSquad spec amendment, the implement worker raises a drift flag and the coordinator pauses; amendments are never silent; propagation flags downstream artifacts without editing them; resume is blocked until they are updated or waived. Quote: "returns a `spec-drift` flag with a structured payload"
- E41. Same DevSquad URL, 2026-10-16, WebFetch. Claim: propagation is flag-only. Quote: "The refine agent does not edit these artifacts in amendment mode. It flags them."
- E42. Same DevSquad URL, 2026-10-16, WebFetch. Claim: work stops until downstream artifacts are updated or waived; changes are never silent. Quote: "blocks resume until each flagged artifact is either updated"
- E43. https://github.com/github/spec-kit/blob/main/spec-driven.md, 2026-10-16, WebFetch. Claim: in spec-kit, changes mean re-planning from the spec, not patching code. Quote: "means revisiting the specification and creating new implementation plans"
- E44. https://github.com/github/spec-kit, 2026-10-16, WebFetch. Claim: the spec-kit README names no amend step; it offers consistency checks and a converge loop. Quote: "Repeat implement → converge until convergence reports Converged."
- E45. https://kiro.dev/docs/specs/feature-specs/, 2026-10-16, WebFetch. Claim: Kiro's feature-specs page does not document post-task spec updates. Quote: "Implementation can adapt"
- E46. https://datadef.io/guides/en/docs-checks-in-ci, 2026-10-16, WebFetch. Claim: a Danger-style rule is a four-line path comparison; start with warn, because a hard fail invites junk edits. Quote: "Teams usually start with warn rather than fail"
- E47. Same datadef URL, 2026-10-16, WebFetch. Claim: CI cannot check truth. Quote: "CI detects proxies for outdatedness rather than outdatedness itself"
- E48. Same datadef URL, 2026-10-16, WebFetch. Claim: the page gives no false-positive rates for lychee or Vale (WebFetch answer: advice only, e.g. exclude internal hosts so the link job does not "cry wolf"). Quote: "cry wolf"
- E49. https://lychee.cli.rs/troubleshooting/rate-limits/, 2026-10-16, WebFetch. Claim: lychee: rate limiting yields spurious broken links. Quote: "The result is that lychee will report a lot of broken links with `429` as a status code."
- E50. Same lychee URL, 2026-10-16, WebFetch. Claim: the mitigation of last resort. Quote: "As a last resort, you might want to accept `429` as a valid status code."
- E51. https://github.com/schemathesis/schemathesis, 2026-10-16, WebFetch. Claim: Schemathesis is MIT-licensed and finds API responses that deviate from the OpenAPI or GraphQL schema; the page makes no false-positive claim. Quote: "licensed under the terms of the MIT license"
- E52. https://github.com/apiaryio/dredd, 2026-10-16, WebFetch. Claim: Dredd is archived, so skip it. Quote: "This repository was archived by the owner on Nov 8, 2024. It is now read-only."
- E53. https://docs.pact.io/pact_broker/can_i_deploy, 2026-10-16, WebFetch. Claim: Pact can-i-deploy needs published verification results and recorded deployments; exit 0 means safe, 1 means not. Quote: "All required verification results are published and successful."
- E54. https://atlasgo.io/versioned/diff, 2026-10-16, WebFetch. Claim: Atlas `migrate diff` needs a dev database; `migrate lint` runs in CI. Quote: "a URL to a Dev Database that will be used to compute the diff"
- E55. https://arxiv.org/abs/2511.00215, 2026-10-16, WebFetch. Claim: DocPrism abstract: a plain LLM flags over 90%; filtering brings this to 14%; precision 0.63. Quote: "LCEF reduces DocPrism's inconsistency flag rate from 98% to 14%"
- E56. Same DocPrism URL, 2026-10-16, WebFetch. Claim: precision across the broad evaluation. Quote: "achieves a precision of 0.63 without performing any fine-tuning"
- E57. https://arxiv.org/abs/2604.19400, 2026-10-16, WebFetch. Claim: Cascade (April 2026) reports an inconsistency only if existing code fails a doc-derived test and doc-generated code passes it. Quote: "13 previously unknown inconsistencies, of which 10 have subsequently been fixed"
- E58. https://newsletter.nerdnoir.com/p/documentation-needs-a-feedback-loop, 2026-10-16, WebFetch. Claim: the Doc-Drift GitHub Action (blog, 2026-01-26) flags only specific contradictions; its noise and cost are self-reported. Quote: "Maybe one in every dozen findings needs to be dismissed."
- E59. Same Doc-Drift URL, 2026-10-16, WebFetch. Claim: cost. Quote: "The total spend reported was a whopping $0.03."
- E60. Same Doc-Drift URL, 2026-10-16, WebFetch. Claim: limits. Quote: "The system catches specific contradictions, not conceptual drift."
- E61. https://github.com/verdict-ci/verdict, 2026-10-16, WebFetch. Claim: Verdict (an intent-versus-diff gate, 1 star): scope mismatch causes false positives. Quote: "false positives born of mismatched scope, not real defects."
- E62. /home/user/Autonomy-Research/research/tool-registry.md:192, 2026-10-16, local read. Claim: Stop-hook doc-gate pitfalls: a JSON block was ineffective and exit 2 worked (doc-sentinel row, PR dgalarza/claude-code-workflows#36). Quote: "Stop hook auto-dispatching a drift resolver; found JSON block ineffective, exit 2 worked"

**Task splitting (notes/task-splitting.md)**

- E63. https://metr.org/notes/2026-03-20-impact-of-modelling-assumptions-on-time-horizon-results/, 2026-10-16, Exa. Claim: METR's noise-adjusted Opus 4.6 numbers are about 7.6 h at 50% and about 1 h 16 m at 80% (full dataset, regularization-fix logistic). Quote: "Logistic (Reg. Fix) | 7h 38m (-36%) | 1h 16m (+9%)"
- E64. Same METR note URL, 2026-10-16, Exa. Claim: METR says modelling choices move Opus 4.6 results by about 1.5x (50%) and 2x (80%). Quote: "The variation in the results from reasonable methods is ~1.5x in 50% TH and 2x in 80% TH for Opus 4.6."
- E65. https://metr.org/notes/2026-01-22-time-horizon-limitations/, 2026-10-16, Exa. Claim: METR says the 80% horizon is not an independent estimate. Quote: "20% and 80% time horizons are not fully independent estimates from the 50% time horizon, because there aren't enough parameters to fit them separately."
- E66. https://metr.org/notes/2026-02-13-measuring-time-horizon-using-claude-code-and-codex/, 2026-10-16, Exa. Claim: the Claude Code scaffold did not beat METR's own scaffolds for Opus 4.5, so the numbers transfer roughly to Claude Code. Quote: "neither Claude Code nor Codex outperform the default scaffolds METR uses, at least when measuring the time horizon of Opus 4.5 and GPT-5."
- E67. https://metr.org/blog/2026-1-29-time-horizon-1-1/, 2026-10-16, Exa. Claim: Opus 4.5's 50% horizon is 320 minutes on TH1.1 (CI 170-729); Sonnet 4.5's is 122 min on TH1. Quote: "Claude Opus 4.5 | 289 [110,1268] | 320 [170,729] | +11%"
- E68. https://scale.com/blog/swe-bench-pro, 2026-10-16, Exa. Claim: SWE-Bench Pro tasks average 107 lines over 4.1 files; the best models scored about 23% in Sept 2025, versus over 70% on Verified. Quote: "These tasks require substantial changes, averaging 107.4 lines of code across 4.1 files."
- E69. https://labs.scale.com/leaderboard/swe_bench_pro_public, 2026-10-16, Exa. Claim: Scale reports that performance degrades with lines and files. Quote: "Model performance significantly degrades as solutions require more lines to be added and files to be edited."
- E70. https://dataist.ai/research/top-coding-agents-solve-under-a-quarter-of-swe-bench-pro-tasks/, 2026-10-16, Exa (secondary). Claim: Scale's failure analysis: bigger models miss on logic in large edits; some hit context overflow. Quote: "Some systems ran into context overflow and endless walking of the file tree, formatting errors and build incompatibilities."
- E71. https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents, 2026-10-16, Exa. Claim: Anthropic: Claude's dominant failure was doing too much at once. Quote: "the agent tended to try to do too much at once—essentially to attempt to one-shot the app."
- E72. Same Anthropic URL, 2026-10-16, Exa. Claim: Anthropic: one feature per session was critical. Quote: "the next iteration of the coding agent was then asked to work on only one feature at a time. This incremental approach turned out to be critical"
- E73. https://code.claude.com/docs/en/best-practices, 2026-10-16, WebFetch. Claim: Claude Code docs: context fills and performance degrades; Anthropic's first-listed fix is a runnable check. Quote: "LLM performance degrades as context fills. When the context window is getting full, Claude may start \"forgetting\" earlier instructions or making more mistakes."
- E74. Same Claude Code docs URL, 2026-10-16, WebFetch. Claim: Claude Code docs: the size test for skipping a plan. Quote: "If you could describe the diff in one sentence, skip the plan."
- E75. Same Claude Code docs URL, 2026-10-16, WebFetch. Claim: Claude Code docs: a spec should name files, interfaces, what is out of scope and an end-to-end check. Quote: "they name the files and interfaces involved, state what is out of scope, and end with an end-to-end verification step that proves the feature works."
- E76. https://www.anthropic.com/engineering/harness-design-long-running-apps, 2026-10-16, Exa. Claim: Anthropic (Mar 2026): as models improved (Opus 4.6), the sprint decomposition was removed; the need for decomposition shrinks with model strength. Quote: "I started by removing the sprint construct entirely."
- E77. https://github.github.com/spec-kit/concepts/complex-features.html, 2026-10-16, Exa. Claim: spec-kit's maintainers document hallucination during long implement runs near compaction. Quote: "agents can start to lose track of the plan, ignore tasks, or hallucinate — usually right before or after context compaction is triggered."
- E78. https://github.com/obra/superpowers skills/writing-plans/SKILL.md:36-41 (commit bb92a77), 2026-10-16, clone. Claim: Superpowers writing-plans defines a task as the smallest unit with its own test cycle, with steps as single actions. Quote: "A task is the smallest unit that carries its own test cycle and is worth a fresh reviewer's gate."
- E79. skills/writing-plans/SKILL.md:45 (commit bb92a77), 2026-10-16, clone. Claim: steps are one action each. Quote: "**Each step is one action with a checkable result:**"
- E80. skills/writing-plans/SKILL.md:37-40 (commit bb92a77), 2026-10-16, clone. Claim: Superpowers tells the planner to fold setup and docs into the task and to split only where a reviewer could reject one task without the other. Quote: "split only where a reviewer could meaningfully reject one task while approving its neighbor."
- E81. skills/writing-plans/SKILL.md:19-21 (commit bb92a77), 2026-10-16, clone. Claim: Superpowers' writing-plans has no numeric ceiling on files, lines or tokens per task; its only size rule is the scope check for independent subsystems. Quote: "If the spec covers multiple independent subsystems, it should have been broken into sub-project specs during brainstorming."
- E82. https://github.com/obra/superpowers skills/subagent-driven-development/SKILL.md:188 (commit bb92a77), 2026-10-16, clone. Claim: the Superpowers executor uses a fresh implementer subagent per task, with the model chosen by task type ("isolated functions, clear specs, 1-2 files" count as mechanical). Quote: "**Mechanical implementation tasks** (isolated functions, clear specs, 1-2 files): use a fast, cheap model."
- E83. skills/subagent-driven-development/SKILL.md:75 (commit bb92a77), 2026-10-16, clone. Claim: the Superpowers fix loop is capped at 5 rounds, with escalation. Quote: "Fix round R of 5: R≤3 resume implementer; R≥4 fresh implementer, more capable model"
- E84. https://ghuntley.com/ralph/, 2026-10-16, Exa. Claim: Ralph (Huntley, 2025-07-14): one item per loop; narrow it when it goes wrong. Quote: "One item per loop. I need to repeat myself here—one item per loop. You may relax this restriction as the project progresses, but if it starts going off the rails, then you need to narrow it down"
- E85. Same Ralph URL, 2026-10-16, Exa. Claim: Ralph's rationale is context size. Quote: "you only have approximately 170k of context window to work with. So it's essential to use as little of it as possible."
- E86. https://github.com/ghuntley/how-to-ralph-wiggum, 2026-10-16, Exa. Claim: in the Ralph variant repo, one iteration = one fresh context = one task = one commit; the "smart zone" is 40-60% of context. Quote: "Each iteration = one fresh context window = one task from IMPLEMENTATION_PLAN.md = one commit"
- E87. https://ghuntley.com/ralph/, 2026-10-16, Exa. Claim: Ralph's own prompt variant still allows "the most important 10 things" per loop, so Huntley's size rule is not uniform. Quote: "choose the most important 10 things."
- E88. https://github.com/github/spec-kit templates/tasks-template.md:16-19,81 (commit f6e72bc), 2026-10-16, clone. Claim: in spec-kit's tasks template, tasks are grouped by user story, [P] marks parallel tasks (different files, no dependencies), and each story has an "Independent Test". Quote: "**[P]**: Can run in parallel (different files, no dependencies)"
- E89. templates/tasks-template.md:252 (commit f6e72bc), 2026-10-16, clone. Claim: spec-kit's template warns against vague tasks and same-file conflicts. Quote: "Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence"
- E90. https://github.github.com/spec-kit/concepts/complex-features.html, 2026-10-16, Exa. Claim: spec-kit docs: scope each implement run to N tasks or a phase; one sub-agent per task; a spec-of-specs when one phase overwhelms. Quote: "/implement only execute tasks 1-10, then stop and report progress" (from discussion #2914, https://github.com/github/spec-kit/discussions/2914)
- E91. https://github.com/github/spec-kit/discussions/1784, 2026-10-16, Exa. Claim: a spec-kit user report (2025-09): too much generated spec, and the agent ignores parts. Quote: "split task to atomic points by yourself (in the ticket for example) - ask LLM to implement one by one"
- E92. https://github.com/kirodotdev/Kiro/issues/2324, 2026-10-16, Exa. Claim: Kiro gives "Session Too Long" when the spec is large; the user wants to run single tasks without the full docs. Quote: "A single task execution probably doesn't need the full requirements and design docs, but I couldn't see any way to exclude them."
- E93. https://www.martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html, 2026-10-16, Exa. Claim: Kiro and spec-kit are overkill for small work. Quote: "The requirements document turned this small bug into 4 \"user stories\" with a total of 16 acceptance criteria"
- E94. https://github.com/steveyegge/beads README.md:73-86 (commit dff9492), 2026-10-16, clone. Claim: Beads supports hierarchical epic/task/sub-task IDs and `bd ready` for tasks with no open blockers. Quote: "`bd-a3f8` (Epic) * `bd-a3f8.1` (Task) * `bd-a3f8.1.1` (Sub-task)"
- E95. https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents, 2026-10-16, Exa. Claim: Anthropic's harness kept 200+ features, all marked failing, in a JSON list worked one at a time; JSON was used because the model edits it less. Quote: "the model is less likely to inappropriately change or overwrite JSON files compared to Markdown files."
- E96. https://www.alphaxiv.org/abs/2605.21516, 2026-10-16, Exa (summary page). Claim: Terminal-Bench v2 success peaks at an intermediate number of workflow steps and falls when the work is too fragmented. Quote: "the agent's success rate peaks at a specific number of steps (six, in this case) and declines if the task is either too unified or too fragmented."
- E97. Same alphaxiv URL, 2026-10-16, Exa. Claim: in the same work, partial harnesses can beat fully structured ones. Quote: "specifying only the initial steps and leaving the remaining execution to agent can achieve higher pass rate than fully structured workflows."
- E98. https://arxiv.org/pdf/2603.24284, 2026-10-16, Exa. Claim: splitting one class across two agents shows a 25-39 point coordination gap (abstract), measured as specification detail was stripped (levels L0 to L3, 51 class tasks, Sonnet, Haiku). Quote: none verbatim; the paper says "persistent specification gap" (corrected after verification, 2026-10-16).
- E99. Same arXiv 2603.24284 URL, 2026-10-16, Exa. Claim: the spec is the coordination contract. Quote: "the specification functions as a coordination contract between agents"
- E100. https://arxiv.org/html/2607.29529v1 (AuditCoder), 2026-10-16, Exa. Claim: over-fine nodes add interface overhead. Quote: "overly fine nodes add interface overhead and may split a global invariant across locally plausible components."
- E101. https://clawrxiv.io/abs/2604.00690, 2026-10-16, Exa. Claim: a decomposition-granularity preprint reports an optimal window and rising coordination errors with over-splitting (DGI). Provenance is weak (clawRxiv, AI-style authorship, unreviewed); use as a hypothesis only. Quote: "(III) an over-decomposition regime where coordination overhead dominates."
- E102. https://code.claude.com/docs/en/best-practices, 2026-10-16, WebFetch. Claim: Claude Code docs say to clear and restart after two failed corrections, and that tight feedback beats long sessions. Quote: "After two failed corrections, `/clear` and write a better initial prompt incorporating what you learned."
- E103. https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents, 2026-10-16, Exa. Claim: Anthropic's harness ends each session in a mergeable state, with a commit and a progress file. Quote: "the kind of code that would be appropriate for merging to a main branch"
- E104. https://github.com/ghuntley/how-to-ralph-wiggum, 2026-10-16, Exa. Claim: the Ralph repo's "smart zone" is 40-60% of context. Quote: "40-60% context utilization for \"smart zone\""
- E105. https://github.com/steveyegge/beads README.md:73-76 (commit dff9492), 2026-10-16, clone. Claim: Beads' `bd ready` lists tasks with no open blockers; `bd dep add <child> <parent>` links blocks/related/parent-child; `--claim` takes a task. Quote: "| `bd ready` | List tasks with no open blockers. |"
- E106. Beads README.md:76 (commit dff9492), 2026-10-16, clone. Claim: Beads' dependency link types. Quote: "| `bd dep add <child> <parent>` | Link tasks (blocks, related, parent-child). |"
- E107. https://github.com/obra/superpowers skills/dispatching-parallel-agents/SKILL.md:3 (commit bb92a77), 2026-10-16, clone. Claim: Superpowers dispatches in parallel only for independent problems. Quote: "Use when facing 2+ independent tasks that can be worked on without shared state or sequential dependencies"
- E108. skills/dispatching-parallel-agents/SKILL.md:32 (commit bb92a77), 2026-10-16, clone. Claim: Superpowers sends dependent work sequentially. Quote: "\"Can they work in parallel?\" -> \"Sequential agents\" [label=\"no - shared state\"];"
- E109. https://github.com/github/spec-kit templates/tasks-template.md:60-62 (commit f6e72bc), 2026-10-16, clone. Claim: in spec-kit, [P] means different files and no dependencies, and the foundational phase blocks all stories. Quote: "No user story work can begin until this phase is complete"
- E110. https://arxiv.org/html/2606.00953, 2026-10-16, Exa. Claim: cohesion-aware partitioning paper: the file-parallel baseline cost +44% for a +0.9pt pass gain; Agent Teams was fastest but had the lowest pass rate. Quote: "The poor task partitioning causes parallel agents to produce conflicting interfaces, requiring redundant re-generation that incurs extra costs without improving code quality."
- E111. Same arXiv 2606.00953 URL, 2026-10-16, Exa. Claim: in the same paper, execution runs through a shared ready-list without layer barriers. Quote: "each file is registered as a task whose state advances from pending to ready the moment all of its upstream files have completed"
- E112. Same arXiv 2606.00953 URL, 2026-10-16, Exa. Claim: in the same paper, coupling raises the benefit of cohesion-aware partitions. Quote: "edge density (|E|/|V|; Table 4) correlates positively with absolute test-pass improvement over Sequential"
- E113. https://code.claude.com/docs/en/best-practices, 2026-10-16, WebFetch. Claim: Claude Code supports worktrees for isolated parallel sessions and warns that agent teams are experimental. Quote: "Worktrees: run separate CLI sessions in isolated git checkouts so edits don't collide"
- E114. https://ghuntley.com/ralph/, 2026-10-16, Exa. Claim: Ralph/Huntley: parallel subagents for reads and search, but only one for build and test, to avoid back-pressure. Quote: "only 1 subagent for build/tests of rust."
- E115. https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents, 2026-10-16, Exa. Claim: Anthropic's harness uses a JSON feature list with a pass field and chooses the "highest-priority feature that's not yet done". Quote: "Choose a single feature to start working on."

**Earlier findings built on (local files named by the lead, read 2026-10-16)**

- E116. /home/user/Autonomy-Research/research/findings/engineer-intake.md:77, Read. Claim: intake ends in a Markdown spec plus a JSON task list with `passes` and a verification command per item, with approval recorded in a file. Quote: "approval recorded in a file, not via ExitPlanMode alone"
- E117. /home/user/Autonomy-Research/research/findings/engineer-intake.md:63, Read. Claim: JSON versus Markdown for the task list was left unresolved in intake. Quote: "**Contradictions.** JSON vs Markdown, see the agentic-tools answer; unresolved."
- E118. /home/user/Autonomy-Research/research/findings/engineer-context.md:117, Read. Claim: repo-resident task state: `tasks.json`, `PROGRESS.md`, a dependents manifest, and ADRs that supersede. Quote: "`docs/DEPENDENTS.md` (the manifest of documents each kind of scope change must touch)"
- E119. /home/user/Autonomy-Research/research/findings/engineer-context.md:118, Read. Claim: a command-type Stop and TaskCompleted hook enforces the evidence command and the doc-manifest check. Quote: "blocks with exit 2 on failure, honours `stop_hook_active`, and logs when it fails open after the eight-block override"
- E120. /home/user/Autonomy-Research/research/findings/engineer-context.md:108, Read. Claim: whether a JSON decision or exit 2 blocks a Stop hook is unresolved. Quote: "Unresolved; settle by a spike on the engine's current version."
- E121. /home/user/Autonomy-Research/research/findings/engineer-context.md:119, Read. Claim: the supervisor bounds each task. Quote: "two attempts per task, then a blocked note"
- E122. /home/user/Autonomy-Research/research/findings/engineer-feasibility.md:319, Read. Claim: Mermaid C4 was rejected as the default diagram syntax. Quote: "**Mermaid C4 as default.** Experimental (https://mermaid.js.org/syntax/c4.html)."
- E123. /home/user/Autonomy-Research/research/findings/engineer-feasibility.md:299, Read. Claim: decisions are recorded as MADR ADRs that John confirms. Quote: "Record a MADR ADR with a plain-language summary and a confirmation line; John flips the status"

## Implications for the autonomous engineer (and the researcher plugin)

**Plan set and approval**
- Add a `docs/plan/` template to the engineer with the eight files from Q1. `brief.md` is the only file John reads in full. The template carries the Superpowers "decide nothing" ban (E21) and spec-kit's NEEDS CLARIFICATION marker (E3), so open items are greppable.
- Make `tasks.json` the only task store the agent edits, and only through its `passes`/status field (E95, E118). Add fields for `files`, `depends_on`, `requirement_ids`, `check` and `files_to_read`, so the supervisor can compute `ready` and detect file overlap mechanically.
- Add `approval.json` plus a start-up and PreToolUse hash check. The engineer may write `approval.json` only after a message from John or an approval on his account (E29, E30, E27). Until spike S2 passes, treat the hook as unproven and keep the human message as the authority.

**Change control and drift**
- Add a `docs/plan/changes/NNNN-<slug>.md` change-record template: trigger, tier, evidence, old-to-new lines, affected documents from `docs/DEPENDENTS.md`, cost and time effect, recommendation, default if unanswered, status. Extend the wave 1 Stop hook so a task cannot resume while a change record it depends on is not `applied` (E42, E119).
- Add drift tooling in this order: the manifest gate, limited to the current diff; lychee on changed docs; Schemathesis or Atlas only when the project has an OpenAPI schema or a database; a milestone LLM audit with a cite-or-silent prompt, whose output goes to John's digest and never into automatic edits (E47, E49, E55, E58).

**Task splitting**
- Replace the Superpowers sizing step with a task-contract check run by the planner: one check, a files list, a line estimate, and interface seams named (E78-E81, E98).

**Research plugin**
- Its own plans (`PLAN.md`) already follow "one facet = one worker = one notes file". The same splitting evidence (E71, E72, E77) supports keeping worker briefs narrow and context-bounded.

## Tools evaluated

| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| GitHub spec-kit (templates, re-look) | https://github.com/github/spec-kit | Templates spec 131 / plan 113 / tasks 252 lines, NEEDS CLARIFICATION marker, read-only checklist gate, [P] parallel marker; docs admit mid-run hallucination on big features | agent commands, Python CLI | 2026-10-16 (commit f6e72bc) | Copy marker, gate, [P] and phase scoping; reject wholesale (verbose) |
| OpenSpec (re-look, incl. update/verify) | https://github.com/Fission-AI/OpenSpec | Proposal (1-2 pages), per-capability behaviour specs, design, tasks; update artifacts mid-build; verify on three dimensions; Thoughtworks Assess Apr 2026 | npm CLI + slash commands; licence not checked | 2026-10-16 (commit f80d860) | Borrow the change-record shape and behaviour-contract rule; fallback framework |
| Superpowers brainstorming, writing-plans, subagent-driven-development (re-look) | https://github.com/obra/superpowers | Hard-gate brainstorm, committed design doc, decisions-only plans; task = smallest unit with own test cycle, no numeric cap; fresh subagent per task; fix loop capped at 5 | plugin | 2026-10-16 (commit bb92a77) | Keep as process layer and executor; override task sizing with an explicit task contract |
| BMAD correct-course | https://github.com/bmad-code-org/BMAD-METHOD | Impact analysis, old-to-new proposals, Minor/Moderate/Major, explicit approval (skills/bmad-correct-course/SKILL.md) | skill | 2026-10-16 (commit cfba3ff) | Borrow the replan protocol; skip the framework |
| DevSquad spec amendment | https://microsoft.github.io/devsquad-copilot/concepts/spec-amendment/ | spec-drift flag, flag-only propagation, resume blocked until updated or waived | Copilot agents (docs only) | 2026-10-16 | Borrow block-until-propagated rule |
| Agent OS (Builder Methods) | https://buildermethods.com/agent-os/v2/workflow | Six phases: plan-product, shape-spec, write-spec, create-tasks, implement, orchestrate | agent commands | 2026-10-16 (workflow page; file names unconfirmed) | Reference only |
| Spec Guard | https://github.com/jpstone/spec-guard | MCP governance: three human gates, hash-bound approval stale on edit, JSON packet in git | MCP server | 2026-10-16 (README only, not run) | Copy hash-bound approval; do not install |
| Plannotator | https://docs.plannotator.ai/learn/code-context/approve-ai-coding-plan-before-execution | Local browser plan reviewer; Approve records no identity | local | 2026-10-16 (docs page only) | Optional viewer; not an approval record |
| GitHub protected-branch rules | https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches | Required reviews, stale-approval dismissal, code-owner review | GitHub | 2026-10-16 | Use as identity-bearing approval route; single-user self-approval unverified |
| Kiro specs (re-look) | https://kiro.dev/docs/specs/ | Three files, Review comments, Quick Spec without gates; feature-specs page silent on mid-build amendment | IDE | 2026-10-16 | Borrow format only |
| Danger JS / path-mapping rule | https://datadef.io/guides/en/docs-checks-in-ci | Warn when watched code changes without docs; detects proxies, not truth | CI | 2026-10-16 (guide only) | Fallback; a shell diff script does the same; start as warn |
| lychee | https://lychee.cli.rs/troubleshooting/rate-limits/ | Link checker; 429 rate limits produce false broken links | CLI/CI | 2026-10-16 | Use on changed docs; tune retries and accept |
| Schemathesis | https://github.com/schemathesis/schemathesis | MIT; OpenAPI/GraphQL schema-conformance testing | CLI/CI | 2026-10-16 | Use only if an OpenAPI schema exists |
| Dredd | https://github.com/apiaryio/dredd | API description vs implementation | CLI | 2026-10-16 | Reject: archived 2024-11-08 |
| Pact can-i-deploy | https://docs.pact.io/pact_broker/can_i_deploy | Consumer-contract deploy gate via Broker | Broker + CI | 2026-10-16 | Skip for solo repo |
| Atlas migrate diff/lint | https://atlasgo.io/versioned/diff | Schema diff against dev DB; migration lint | CLI/CI | 2026-10-16 | Use if the repo has a database; migra not opened |
| DocPrism / Cascade (LLM doc-code consistency) | https://arxiv.org/abs/2511.00215 ; https://arxiv.org/abs/2604.19400 | DocPrism: flag rate 98% to 14% with LCEF filter, precision 0.63; Cascade: test-backed reports, 13 new inconsistencies, 10 fixed (precision/recall figures seen only in search highlights) | research (not run) | 2026-10-16 (abstract pages) | Reference: diff-scoped, evidence-citing LLM audit only |
| Doc-Drift / Verdict | https://newsletter.nerdnoir.com/p/documentation-needs-a-feedback-loop ; https://github.com/verdict-ci/verdict | PR-time LLM doc-contradiction gate (self-reported ~1 in 12 dismissed, $0.03) and intent-vs-diff gate (1 star, scope-mismatch false positives) | GitHub Action / CLI (not run) | 2026-10-16 | Reference only; unvetted; docs-gate seen only in search highlights |
| Beads (dependency graph) | https://github.com/steveyegge/beads | `bd ready`, blocks/related/parent-child edges, hierarchical epic IDs | CLI (clone read only) | 2026-10-16 (commit dff9492) | Unchanged: defer until ordering or multi-agent claims bite; tasks.json DAG first |
| Ralph one-item-per-loop | https://github.com/ghuntley/how-to-ralph-wiggum | One task, fresh context, one commit per iteration; 40-60% context smart zone | bash loop | 2026-10-16 | Use the pattern, not the unbounded loop |
| Kiro tasks | https://github.com/kirodotdev/Kiro/issues/2324 | "Session Too Long" on large specs | proprietary IDE | 2026-10-16 | Skip |
| Taskmaster (claude-task-master) | https://github.com/eyaltoledano/claude-task-master | Task generator with complexity analysis and expand tools (commit c0c98d3); thresholds not read | CLI/MCP, clone read only | 2026-10-16 | Not evaluated beyond tool list; skip until thresholds read |
| METR time-horizon notes | https://metr.org/notes/2026-03-20-impact-of-modelling-assumptions-on-time-horizon-results/ | Opus 4.6 noise-adjusted 50%/80% horizons (7h38m / 1h16m), ~2x method variation at 80% | web | 2026-10-16 | Evidence source; read raw data for current models in a spike |
| Evaluating AGENTS.md / ISCAP SDD-vs-vibe / SDD thesis | https://arxiv.org/abs/2602.11988 ; https://iscap.us/proceedings/2026/pdf/6729.pdf ; https://mskre.no/thesis.pdf | Context files +20% cost; Spec-Kit-style spec +9.2 pts at ~28x tokens; more automated scaffolding not consistently better | papers | 2026-10-16 | Evidence for lean plan set |
| Thoughtworks Radar SDD / OpenSpec blips | https://www.thoughtworks.com/radar/techniques/spec-driven-development | Assess ring; lengthy specs hard to review; OpenSpec Assess Apr 2026 | web | 2026-10-16 | Evidence |

## Open questions

**Excluded claims (no opened source, or search snippet only)**
1. Kiro requirements use EARS ("WHEN ... THE SYSTEM SHALL ..."). The worker saw only a search excerpt of kiro.dev/docs/specs/feature-specs/requirements-first and did not open it this run. An earlier run did open it (/home/user/Autonomy-Research/research/findings/engineer-intake.md:59).
2. Thoughtworks Radar vol. 33 PDF warning on heavy up-front specification: search excerpt only.
3. Enact blog (2026-10-14, vendor) on named approvers and stale approvals: search excerpt only.
4. Lodestar (builder-seoro), in which a non-coder approves decision cards and spec amendments: search excerpt only.
5. OpenSpec archive delta rules (MODIFIED must carry the full block; REMOVED needs a Reason and a Migration), https://openspec.dev/docs/schemas/spec-driven: Exa highlights only, not fetched.
6. OpenSpec update "Confirms every edit with you before writing, one artifact at a time", https://openspec.dev/docs/reference/slash-commands: the page returned 404 on direct fetch; highlights only.
7. BMAD batch review of edit proposals: the WebFetch of the GitHub URL returned 404; highlights only.
8. lychee issue #1873, a user deactivating lychee over false positives: highlights only.
9. The ADR-044 pattern "Gate mode only fails on drift introduced by the current diff." (pantheon-org): highlights only. The recommendation to limit gates to the current diff therefore rests on worker inference, not on this source.
10. DocPrism full text: the main false-positive cause is flagging missing detail as incompleteness (https://arxiv.org/html/2511.00215v2): highlights only.
11. Cascade precision 0.88 at recall 0.21 (https://arxiv.org/html/2604.19400): highlights only. Only the abstract claim (13 inconsistencies, 10 fixed) is cited.
12. sarvesh docs-gate blog, a free path check first and the LLM only when docs are touched at about $0.01 per call; the docs-gate tool row rests on it: highlights only.
13. CCI dataset label noise (45.67% of "inconsistent" labels wrong): highlights only.
14. METR time-horizons page: the 50%/80% definition and the "no longer actively updated" note of 2026-09-08. The note marks this page as read through Exa search highlights, so both claims are excluded.
15. anthropics/cwc-long-running-agents: one feature per session, PROGRESS.md, default-FAIL contract. Exa highlights only in this run. The registry row from the audit-agent run says it was cloned (commit ad107a9); its claims are not cited here.
16-17. Third-party readings of METR's Opus 4.6 horizons: 718.8 min / 69.9 min (https://www.clrtstudio.com/insights/half-the-time-not-every-time) and 221.6 min / 7.7 min (https://the-agent-report.com/2026/05/claude-mythos-shatters-metr-time-horizon/), both highlights only. They disagree with METR's own note (E63). This is unresolved until METR's dashboard data file is read (spike S11).
18. Agent OS file names (mission.md, roadmap.md, tech-stack.md under agent-os/product/): search excerpt only.

**Gaps (pages not opened or not researched)**
19. Hill's large PR study, cited by the thesis, found no support for SDD reducing defects. It was not opened.
20. No maintainer data from spec-kit or Kiro on adherence rates. No source compares YAML with Markdown task lists, or YAML with JSON, on agent adherence.
21. Tessl, Traycer and BMAD file sizes were not opened. BMAD story sizing, Taskmaster complexity thresholds, FeatBench, and Codex and Cursor task-size guidance were not read.
22. Kiro's mid-build spec update and task regeneration: the pages opened were silent.
23. MADR docs and Nygard's original were not opened for supersession rules. RFC and engineering-change-request forms were not researched.
24. Vale, markdownlint, mermaid-cli/mermaid-lint and migra docs were not opened. No published false-positive data exists for Danger, Vale, markdownlint, mermaid-lint or migra.
25. No published accuracy for plan-versus-code LLM auditing; the data covers docstring-versus-code only.
26. No METR 80% horizon for Claude Opus 5.x or Sonnet 5.5. No Claude-specific success-by-files data beyond Scale's qualitative statement; Scale's per-bucket numbers were not opened.
27. No controlled study of over-fine splitting on repo-level Claude Code work. No failure reports were found on Beads granularity or on over-fine Superpowers splitting, and Superpowers issues about hallucination were not searched.
28. Beads failure reports at scale and worktree merge-conflict rates for Claude Code were not read.
29. Parallel Search returned "Too Many Requests" in the plan-set worker; Exa was used instead.

**Untested design points**
30. Whether a hook can reliably block edits on an approval-hash mismatch in a cloud session (S2), and whether permissions.deny protects `plan.approved.vN`.
31. Whether John can approve his own PR on a single-user repo with branch rules on. GitHub may not allow self-approval without a second account or a bypass (S4).
32. Whether Moderate changes should need John's approval. This is an owner decision, not researchable.
33. The numeric caps (15-45 minutes, 1-4 files, about 100 lines, 50% context) and the Minor/Moderate/Major boundaries are worker inference, unmeasured (S8, S10).
34. The Stop hook's JSON decision versus exit 2, carried from wave 1 (E120): unresolved (S5).

## Verification
Checked 2026-10-16 by the verifier. Sample: 20 cited claims.
Verified: 19. Unverified: 1.
- Unverified: "splitting one class across two agents costs 25-39 points", quoted as "a persistent coordination gap (25–39pp) separates multi-agent from single-agent performance—even when specifications are detailed." — https://arxiv.org/pdf/2603.24284 — quote not found verbatim (the paper says "persistent specification gap"; the 25–39pp coordination gap is in the abstract); the figure is conditional on stripping spec detail (levels L0 to L3, 51 class tasks, Sonnet and Haiku), which the claim omits, so the judgment is uncertain.

Not re-checked in the sampled reads: the ISCAP 78.2% and 87.4% pass rates and the 296 comparisons (the excerpt read showed the 9.2-point gain and the 28x and 15x multipliers only); the BMAD line numbers :8, :244 and :260 (the quoted lines were found, not the numbers); the Superpowers "7.0.0" version label (the page at commit bb92a77 carries no version).
