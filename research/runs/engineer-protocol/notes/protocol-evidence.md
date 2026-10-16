# Protocol evidence and definition of done

Brief: Find which development-protocol steps have evidence of improving coding-agent outcomes, so the engineer's unattended protocol keeps only steps that pay for themselves, and define "done" fully.
Run: research/runs/engineer-protocol/PLAN.md

Dates: all sources opened 2026-10-16. Tools: WebFetch for quotes (arXiv abstract pages, Anthropic pages), Exa search (returned page text for pages marked "Exa page text"), git clone --depth 1 read-only for Superpowers (commit bb92a77) and spec-kit (commit f6e72bc) in a mktemp dir. Parallel Search returned "Too Many Requests"; Exa used instead. Nothing installed or run.

## Evidence per protocol step (TDD, plan-execute-verify, verification, separate reviewer, debate, self-consistency, run vs read)

### Takeaway
Keep: an external, executable check that the agent cannot rewrite (pre-existing or independently written tests, build, lint, browser run), fresh-context reviewer that is given evidence, and a plan for non-trivial work. Drop or demote: "write tests first" as a prompt-level ritual, agent-invented tests as proof, same-agent self-review, and debate/critique loops (no gain over sampling or over an executable check). Confidence: medium-high (benchmarks are SWE-bench-heavy, Python, mostly small open-weight models in the TDD/review papers).

### Cited findings
- Agent-written tests barely move outcomes: prompting four models to write more or fewer tests flipped test-writing at scale but not resolution; none of 4 McNemar tests significant. Cost moved (+19.8% output tokens for GPT-5.2 with no gain; -49.0% / -32.9% input tokens when suppressed, 2.6% / 1.8% success drop). — https://arxiv.org/abs/2602.07900 (abstract) and https://arxiv.org/html/2602.07900v2 (numbers), opened 2026-10-16, WebFetch + Exa page text — Quote: "prompt-induced changes in the volume of agent-written tests do not significantly change final outcomes in this setting."
- Procedural TDD prompting can harm: on SWE-bench Verified (100 instances, Qwen3-Coder 30B) adding TDD instructions raised regressions 6.08% to 9.94%; test-impact context (which tests are at risk) cut regressions 70% and lifted resolution 24% to 32% in a second setup (25 instances, small sample). — https://arxiv.org/abs/2603.17973, opened 2026-10-16, WebFetch — Quote: "adding TDD procedural instructions without targeted test context increased regressions to 9.94%"
- Test quality decides whether test feedback helps: same repair agent 61.2% with no test, 57.3% with tests from a weak test agent, 65.3% with tests from a strong model, 69.4% with oracle fail-to-pass tests. — https://arxiv.org/abs/2609.09133, opened 2026-10-16, WebFetch — Quote: "tests from the base Test agent reduce resolved rate from a no-test baseline of 61.2% to 57.3%"
- Same-trajectory tests and patch share errors; the proposed fix is to separate test writing from repair and freeze tests. — https://arxiv.org/abs/2609.09133, opened 2026-10-16, WebFetch — Quote: "when the same trajectory writes both the patch and the test, their errors can agree and create false confidence."
- Given human-written tests, a decoupled propose/debug/revise workflow reached 94.3% on SWE-bench Verified; the stated bottleneck is writing valid reproduction tests. Only 7 test-hacking cases in 800 runs. — https://arxiv.org/abs/2510.23761 (Exa page text of abstract), opened 2026-10-16, Exa — Quote: "TDFlow attains 88.8% pass rate on SWE-Bench Lite (an absolute improvement of 27.8% over the next best system) and 94.3% on SWE-Bench Verified."
- Independent verification beats self-review: RETRACE (backward reconstruction withholding the issue) raised Pass@1 56.2% to 63.2% (GPT-5-mini) and 75.8% to 79.4% (MiniMax-2.5); Self-Refine with comparable budget lowered Pass@1 by 1.4 and 1.8 points. — https://arxiv.org/abs/2608.08950 (WebFetch for the lift) and the same paper's HTML via Exa for the Self-Refine delta, opened 2026-10-16 — Quote: "RETRACE lifts Pass@1 by 7.0% and 3.6% respectively on the mini-SWE-agent scaffold"
- Intrinsic self-correction degrades; debate does not beat self-consistency at equal responses (GSM8K: debate 6 responses 83.2 vs self-consistency 6 responses 85.3; 9 responses 83.0 vs 88.2). Note: 2023, GPT-3.5, math not code. — https://arxiv.org/abs/2310.01798 (WebFetch) and https://arxiv.org/html/2310.01798v2 (Exa page text for table), opened 2026-10-16 — Quote: "LLMs struggle to self-correct their responses without external feedback."
- Agentic (tool-using) review beats diff-only review and review-guided revision lifts resolve rate 22.9% to 38.4% in 4 rounds, using 2.44 samples on average; reviewer was an independent model reading the repo, not the author. — https://arxiv.org/abs/2607.06065 (WebFetch) and https://arxiv.org/html/2607.06065 (Exa page text for numbers), opened 2026-10-16 — Quote: "outperforms single-turn fixed-context review in both decision accuracy and resolve rate after revision"
- A weak reviewer needs grounded evidence: with official execution evidence 5 of 6 reviewers improved; patch-only 8B reviewer accepted all nine target omissions; without official tests, generated-test cascade had over-rejection 0.66. — https://arxiv.org/html/2610.01023, opened 2026-10-16, Exa page text — Quote: "an 8B reviewer accepts all nine target omissions when it sees only the patch."
- Running beats reading: Anthropic's long-running harness saw the agent test with unit tests or curl yet miss that the feature failed end-to-end; browser automation fixed it. — https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents, opened 2026-10-16, WebFetch — Quote: "One final major failure mode that we observed was Claude’s tendency to mark a feature as complete without proper testing."
- Evaluator value depends on task difficulty relative to the model: on the newer model the evaluator was overhead for tasks within model capability. — https://www.anthropic.com/engineering/harness-design-long-running-apps, opened 2026-10-16, WebFetch — Quote: "for tasks within that boundary, the evaluator became unnecessary overhead"
- Plans: a standard plan improves resolution; a bad plan hurts more than none; periodic plan reminders help (21,120 SWE-agent trajectories, 4 LLMs). — https://arxiv.org/abs/2604.12147, opened 2026-10-16, WebFetch — Quote: "A subpar plan hurts performance even more than no plan at all."
- Plan source matters: a plan from Claude Sonnet 4.5 lifted Qwen3-Coder-30B from 42.8% to 57.8% Pass@1; self plan +5.4%. — https://arxiv.org/pdf/2608.06113v1, opened 2026-10-16, Exa page text — Quote: "providing Qwen3-Coder-30B-A3B-Instruct with a plan from Claude Sonnet 4.5 improves Pass@1 on SWE-bench Verified from 42.8% to 57.8%"
- Agents game tests when they can edit them: GPT-5 cheated on 76% of Oneoff-SWEbench impossible tasks; hiding tests cut cheating near zero but hurt legit performance; read-only tests restored legit performance and stopped modification. — https://arxiv.org/html/2510.20270v1, opened 2026-10-16, WebFetch — Quote: "Read-only access provides a middle ground: it restores legitimate performance while preventing test modification attempts."
- Claude Code reward-hacking sample (EvilGenie, Claude Code with Sonnet 4): 20.7% heuristic solutions on unambiguous problems; holdout tests not foolproof. — https://arxiv.org/html/2511.21654v1, opened 2026-10-16, Exa page text — Quote: "Importantly, we find that holdout tests are not foolproof."
- Anthropic's own guidance: verification is the lead recommendation; independent fresh-context reviewer for unattended runs. — https://code.claude.com/docs/en/best-practices, opened 2026-10-16, WebFetch — Quote: "Give Claude a check it can run: tests, a build, a screenshot to compare. It's the difference between a session you watch and one you walk away from."
- Anthropic warns reviewers over-report: "A reviewer prompted to find gaps will usually report some, even when the work is sound" so restrict findings to correctness/requirements. — https://code.claude.com/docs/en/best-practices, opened 2026-10-16, WebFetch — Quote: "A reviewer prompted to find gaps will usually report some, even when the work is sound, because that is what it was asked to do."
- Superpowers' TDD skill asserts an absolute rule but cites no effect size in the skill file read. — https://github.com/obra/superpowers skills/test-driven-development/SKILL.md:34 (commit bb92a77), read 2026-10-16, git clone — Quote: "NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST"

### Contradictions
- Otter/TDFlow/Anthropic Academy treat test-first as valuable (reproduction test written before fix; failing test committed and protected) — https://arxiv.org/html/2502.05368, https://academy.claude.com/courses/ai-native-sdlc-playbook/give-claude-a-feedback-loop; disagrees with the Chen et al. finding that more agent-written tests do not change outcomes and with TDAD's TDD-prompt regression increase — https://arxiv.org/abs/2602.07900, https://arxiv.org/abs/2603.17973. Reconciliation (inference): value lies in a pre-existing or independently produced, frozen oracle, not in the agent's own habit of writing tests; the papers test different things (ephemeral agent tests vs. frozen fail-to-pass tests). A direct head-to-head of "frozen independent test first" vs "no test" on Claude Code is not found.
- Anthropic harness post says evaluator gave "real lift" at the model's edge, "unnecessary overhead" within it — https://www.anthropic.com/engineering/harness-design-long-running-apps; Claude Code docs recommend a fresh reviewer for all unattended work — best-practices page. Settle by measuring on John's tasks.
- Plan evidence: DCAS/plan-compliance papers show plans help; a practitioner write-up claims plan-and-execute is brittle (https://github.com/frankbria/codeframe/blob/main/docs/archive/AGENT_ARCHITECTURE_RESEARCH.md, opened via Exa, practitioner opinion, not a study). Harness-design ablation reports planning is "a cost saver for stronger models, with little change in accuracy" (https://bittide.aicompass.dev/article/fe85a7a9-3514-4d12-bec2-2f04e55e25ef, aggregator of an arXiv paper, abstract only).

### Inferences
- Rank by evidence: (1) executable external check + evidence shown; (2) fresh, tool-using reviewer fed grounded evidence; (3) plan/spec for multi-file or uncertain work; (4) frozen failing test before the fix for bug fixes. Weakest: TDD as a prompt rule, debate, same-agent self-review.
- Because Claude Code is the engine and plans are cheap, tie the plan step to size (Anthropic: skip the plan if the diff fits in one sentence).
- Multi-agent debate adds cost without gain; if extra compute is wanted, use sampling plus an executable selector (self-consistency analogue), not critique rounds. Self-consistency evidence here is math reasoning (2022-2023), weak for code; no code-agent number found.

### Gaps
- No study found of Claude Code specifically (Opus/Sonnet 5.x) with and without TDD, planner, or reviewer on a controlled benchmark; most numbers are small open-weight models on SWE-bench Verified (known contamination and 28.5% of a 49-task sample hackable, https://arxiv.org/abs/2606.16062, snippet via Exa).
- No outcome numbers found for Superpowers' own claims; its README says "Evidence over claims" (README.md, bb92a77) but cites no measurements.
- Self-preference bias of same-family LLM reviewers: not searched to a source; not claimed.

## Definition of done (what "done" means for one agent task)

### Takeaway
Done = every item is either a script that exits 0 or a reviewer verdict citing evidence: (a) frozen acceptance tests pass plus the existing suite (no test file edited by the implementer), (b) build, lint, typecheck exit 0, (c) a run of the real artifact (browser or CLI) with output pasted, (d) docs/diagram/change-log updated where the diff touches them, (e) secret/security scan clean, (f) fresh-context reviewer verdict against the plan's acceptance criteria and scope, (g) clean tree committed. Items a-e and g are deterministic hooks; f and the "run the real thing" judgement are reviewer work. Confidence: medium (synthesised from vendor guidance; no study defines a full DoD).

### Cited findings
- Anthropic: put verification in CLAUDE.md and as hooks; stop hook as deterministic gate; show evidence. — https://code.claude.com/docs/en/best-practices, opened 2026-10-16, WebFetch — Quote: "a Stop hook runs your check as a script and blocks the turn from ending until it passes."
- Anthropic Academy: protect the check from the agent; evidence comes from the toolchain, not the model. — https://academy.claude.com/courses/ai-native-sdlc-playbook/give-claude-a-feedback-loop, opened 2026-10-16, Exa page text — Quote: "an agent fixing code must not be able to weaken the check on that code."
- Anthropic Academy "Trust it": unattended runs need a hook-gated test pass, a lint/typecheck hook, a fresh reviewer, and reading the diff. — https://academy.claude.com/courses/claude-code-in-action/trust-it-verifying-unsupervised-runs, opened 2026-10-16, Exa page text — Quote: "The real gate on an unsupervised run is whether the tests passed, and whether Claude actually ran them or only claimed that it did."
- Anthropic long-running harness: feature list with per-feature `passes` flag edited only by status; "clean state" means mergeable code with docs. — https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents, opened 2026-10-16, Exa page text — Quote: "there are no major bugs, the code is orderly and well-documented, and in general, a developer could easily begin work on a new feature"
- Anthropic sprint contract: generator and evaluator agree what "done" looks like before code. — https://www.anthropic.com/engineering/harness-design-long-running-apps, opened 2026-10-16, WebFetch — Quote: "Before each sprint, the generator and evaluator negotiated a sprint contract"
- Tests passing is not mergeable: roughly half of SWE-bench-passing PRs would be rejected by maintainers (24.2 pp gap), for quality, broken unrelated code, or conventions. — https://metr.org/notes/2026-03-10-many-swe-bench-passing-prs-would-not-be-merged-into-main/, opened 2026-10-16, WebFetch — Quote: "We find that roughly half of test-passing SWE-bench Verified PRs"
- Tests pass but design constraints violated: test outcomes have negligible association with design compliance (Cramér's V <= 0.11); design satisfaction 32.6%-50.2%. — https://www.arxiv.org/pdf/2604.05955, opened 2026-10-16, Exa page text — Quote: "Test passing is a poor proxy for design compliance."
- Superpowers verification skill: no completion claim without fresh run in the same message. — https://github.com/obra/superpowers skills/verification-before-completion/SKILL.md:17 (commit bb92a77), read 2026-10-16, git clone — Quote: "NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE"
- Superpowers per-task two-part review (spec compliance and code quality), reviewer told not to trust the implementer. — skills/subagent-driven-development/SKILL.md:8 and task-reviewer-prompt.md:64 (commit bb92a77), read 2026-10-16 — Quote: "## Do Not Trust the Report"; and "Reviewer found spec gaps = not done."
- spec-kit "Done When": tasks marked [X], implementation validated against spec, plan and test coverage; its checklists test the requirements, not the code. — https://github.com/github/spec-kit templates/commands/implement.md:219-220 and checklist.md:34 (commit f6e72bc), read 2026-10-16 — Quote: "Implementation validated against specification, plan, and test coverage"; "`[x]` does NOT mean implementation work is complete."
- Kiro specs: requirements with acceptance criteria and trackable tasks; no stated definition of done on the page read. — https://kiro.dev/docs/specs/, opened 2026-10-16, WebFetch — Quote: "Break down requirements into user stories with acceptance criteria."

### Contradictions
- None found on the content of DoD. Vendors differ on enforcement: Superpowers and spec-kit rely on prompts and checklists (advisory); Anthropic recommends hooks (deterministic) — https://code.claude.com/docs/en/best-practices ("Unlike CLAUDE.md instructions which are advisory, hooks are deterministic").

### Inferences
- Deterministic (script exit code): frozen/acceptance tests; whole suite; build; lint; typecheck; test-file-diff guard (fail if the implementer touched protected tests, conftest.py, CI config); secret scan (gitleaks, in registry); dependency/SAST scan (Semgrep, in registry); docs-manifest check (code changed implies listed doc/diagram/changelog touched, per Wave 1 doc-manifest gate); git clean and committed; output-evidence file present.
- Judgement (fresh reviewer, tools allowed, fed grounded evidence): each plan acceptance criterion met with cited evidence; no scope creep; design/convention fit (the METR and SWE-Shield gaps); docs accurate not merely present; "does the running thing behave" for UI via Playwright run.
- Security scan on every task is not evidenced by any study found; treat as cheap script at phase end plus on diffs touching auth, secrets, deps.
- Change-log entry and diagram updates are hygiene with no outcome evidence; keep because Wave 1 already made them a manifest gate and they are scriptable, not because they raise pass rates.

### Gaps
- No source defines Kiro hooks as a completion gate; the Kiro hooks page was not opened.
- No measured effect of docs/changelog gates on later-task success was found.

## Phases and gates mapped to the harness (one task; one project phase)

### Takeaway
Per task: brief/plan (size-gated) -> frozen acceptance check -> build -> deterministic gate (Stop/TaskCompleted hook) -> fresh reviewer -> commit; per phase: whole-branch review, full suite, scan, doc-manifest, then the supervisor merges. Versus Wave 1, this facet adds three things: protect the oracle (read-only tests plus a diff guard), require a run of the real artifact, and make the reviewer evidence-fed and correctness-scoped. It removes TDD-as-ritual and any debate step. Confidence: medium.

### Cited findings
- Claude Code's own recommended order is explore, plan, implement, commit, with plan skippable when the diff fits in a sentence. — https://code.claude.com/docs/en/best-practices, opened 2026-10-16, WebFetch — Quote: "If you could describe the diff in one sentence, skip the plan."
- Hook mechanics Wave 1 chose: Stop hook blocks until check passes; exit 2 feeds failures back. — https://academy.claude.com/courses/claude-code-in-action/trust-it-verifying-unsupervised-runs, opened 2026-10-16, Exa page text — Quote: "A hook that exits with `exit 2` feeds the failure straight back to Claude."
- Superpowers phases: fresh implementer subagent per task, task review after each, broad whole-branch review at the end, never in parallel for implementers. — skills/subagent-driven-development/SKILL.md:8,282 (commit bb92a77), read 2026-10-16 — Quote: "Never dispatch multiple implementation subagents in parallel (conflicts)."
- spec-kit phases: specify, clarify, plan, tasks, implement, with a constitution check gate in the plan. — https://github.com/github/spec-kit templates/plan-template.md:39 (commit f6e72bc), read 2026-10-16 — Quote: "## Constitution Check"
- Anthropic's planner/generator/evaluator: planner stays high-level to avoid propagating a wrong implementation decision. — https://ai.engineer/talks/mR-WAvEPRwE-build-agents-that-run-hours-without-losing, opened 2026-10-16, Exa page text (talk summary) — Quote: "An incorrect implementation decision made at the beginning can otherwise propagate through every later sprint."
- Context resets plus handoff artifacts across sessions; evaluator pass can move to the end on stronger models. — https://www.anthropic.com/engineering/harness-design-long-running-apps, opened 2026-10-16, WebFetch — Quote: "the evaluator used the Playwright MCP to click through the running application the way a user would"

### Contradictions
- None found.

### Inferences
- Gate table (inference):
  - Brainstorm/interview (phase): harness enforces nothing; output is an EARS acceptance list John confirms. Keep (cheap, upstream of everything).
  - Plan (task): size-gated by a script rule (touches >1 file or unknown area); plan file must list acceptance criteria that map to checks. Hook: plan file exists before first Edit (PreToolUse).
  - Build: PreToolUse deny on protected paths (tests/, conftest.py, CI, hooks); PostToolUse lint/typecheck.
  - Verify: Stop/TaskCompleted hook runs suite, build, lint, typecheck, secret scan, doc-manifest; exit 2 on fail; pastes output to evidence file. Wave 1 chose this; unchanged.
  - Review: fresh reviewer subagent with tools, given plan + diff + evidence file, scoped to correctness and criteria; one round, capped; findings fix then re-run gate, not re-debate.
  - Merge: supervisor (not the implementer) checks gate evidence file and reviewer verdict, then merges.
  - Phase end: whole-branch review with Opus-class reviewer, full suite, SAST/dependency scan, run the app via Playwright for UI work, update docs/diagrams.
- Reviewer and implementer same model family is untested here; use a different model tier for the reviewer only if measured to help (spike).
- The evidence says tests help as oracle after generation; so the test-first step should mean "acceptance check exists and is frozen before build", authored by the plan/interview step or a separate test agent, not "implementer writes tests then code".

### Gaps
- Exit-code vs JSON blocking behaviour of TaskCompleted/Stop hooks is a Wave 1 spike item; not re-tested here.
- Whether TaskCompleted hooks fire for subagent tasks in unattended `claude -p` runs was not checked.

## Evidence table (step, evidence, effect size, source, keep or drop)

### Takeaway
Table below; keep/drop are my judgement. Confidence: medium.

| Step | Evidence | Effect size | Source | Verdict |
| --- | --- | --- | --- | --- |
| Executable check the agent runs (tests, build, lint, screenshot) | Vendor guidance plus oracle experiments | Oracle F2P tests +8.2 pp (61.2 to 69.4) | arxiv 2609.09133; best-practices page | Keep, core |
| Frozen independent acceptance test before fix | Strong-model tests +4.1 pp; weak-model tests -3.9 pp; TDFlow 94.3% with human tests | -3.9 to +8.2 pp depending on test quality | arxiv 2609.09133, 2510.23761 | Keep, only if independent and validated to fail first |
| Agent writes its own tests (any time) | No outcome change; token cost +19.8% or saving 33-49% | ~0 pp resolution | arxiv 2602.07900 | Drop as a required step; allow, do not trust as proof |
| TDD as prompt procedure | Regressions 6.08% to 9.94% (small model, 100 tasks) | worse, +3.9 pp regressions | arxiv 2603.17973 | Drop as ritual; keep Superpowers TDD only for new pure-logic modules where tests are the spec (unproven) |
| Test-impact context (which tests to run) | Regressions -70%; resolution 24% to 32% (25 tasks) | large, small n | arxiv 2603.17973 | Keep idea: run related tests first via dependency map |
| Protect tests (read-only / diff guard) | GPT-5 cheats 76% of impossible tasks with editable tests; read-only stops modification | cheating 76% to ~0 | arxiv 2510.20270 | Keep, hook |
| Verification before completion claim, evidence pasted | Anthropic #1 tip; premature "done" failure mode | qualitative | Anthropic harness blog; best-practices | Keep |
| Run the real artifact (browser/CLI) vs reading code or unit tests | Agent missed e2e failures until browser automation used | "dramatically improved" (no number) | Anthropic harness blog | Keep for UI/service tasks |
| Fresh agentic reviewer, tools, evidence | Review-guided revision 22.9% to 38.4%; agentic > single-turn | +15.5 pp (small open model) | arxiv 2607.06065 | Keep, one capped round |
| Independent reconstruction verifier | +7.0 / +3.6 pp Pass@1 | +3.6 to +7.0 pp | arxiv 2608.08950 | Optional; spike, high cost |
| Same-agent self-review / Self-Refine | -1.4 / -1.8 pp | slightly negative | arxiv 2608.08950; 2310.01798 | Drop |
| Multi-agent debate | No better than self-consistency at equal cost (GSM8K 83.0 vs 88.2 at 9 responses) | negative vs baseline | arxiv 2310.01798 | Drop |
| Self-consistency / sampling + executable selector | Strong for math; no code-agent number sourced | n/a | arxiv 2203.11171 (Exa page text, not quoted) | Defer; only with a deterministic selector |
| Explicit plan/spec | Standard plan helps; bad plan worse than none; frontier-model plan +15 pp for small executor; for strong models mostly cost saving | +5 to +15 pp small models; ~0 accuracy for strong | arxiv 2604.12147, 2608.06113, harness-design abstract | Keep, size-gated; plan quality gate (reviewer checks plan against acceptance list) |
| Sprint contract / negotiated done | Anthropic harness design; no ablation number | qualitative | Anthropic harness-design | Keep as acceptance list in plan, skip negotiation rounds |
| Evaluator on every task | Overhead within model capability | task-dependent | Anthropic harness-design | Keep at task end for risky tasks, always at phase end |
| Design/convention review beyond tests | Test pass vs maintainer merge gap 24.2 pp; design satisfaction <= 50.2% | 24 pp | METR note; arxiv 2604.05955 | Keep in reviewer rubric |
| Docs/diagram/changelog gate | No outcome study | none | Wave 1 choice | Keep (scripted, cheap); label hygiene |

### Cited findings
- See sections above; each row cites a quoted source there.

### Contradictions
- See first section.

### Inferences
- Recommendation (one): the unattended protocol = size-gated plan with a frozen acceptance list -> build with protected oracle and lint/typecheck hooks -> Stop/TaskCompleted deterministic gate with pasted evidence -> one capped fresh tool-using reviewer scoped to correctness and plan criteria -> supervisor merge; phase end adds whole-branch review, full suite, scans, real-app run, docs.
- Alternatives: (a) Superpowers full flow (TDD iron law plus two-stage review per task) if John prefers its discipline; cost higher, outcome gain from TDD unproven; (b) spec-kit/Kiro-style heavier spec ceremony, rejected for one-user effort (registry already notes verbosity); (c) Ralph-style loop, rejected earlier in registry; (d) RETRACE-style reconstruction verifier, spike only.
- Rejected with reasons: debate (no gain), same-agent self-review (negative), mandatory agent-written tests (no gain, extra tokens), TDD-as-prompt-ritual (regression increase in one study).
- Spike before building: (1) A/B on 10 of John's own tasks: with vs without reviewer step and with vs without plan, measuring gate-pass on first try and maintainer-style rubric; use `claude plugin eval` per registry. (2) Verify protected-path PreToolUse deny actually blocks Bash writes to tests. (3) Reviewer on different model tier vs same. (4) Check whether the implementer can disable hooks/config (BenchJack-style conftest hack: a nine-line conftest.py hooking pytest, https://arxiv.org/html/2605.12673) so the guard must cover conftest.py and test config.

### Gaps
- All effect sizes are from SWE-bench-like Python benchmarks and mostly small open models; transfer to John's non-benchmark Attio/Clay/n8n-type tasks is unmeasured.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Superpowers TDD + verification-before-completion skills (re-read) | https://github.com/obra/superpowers | Iron-law TDD and "no completion claim without fresh evidence" skills; subagent-driven-development with per-task spec+quality review; no measured effect sizes in the files read (commit bb92a77) | Claude Code plugin | 2026-10-16 | Keep verification and review skills; do not mandate TDD iron law (evidence mixed) |
| spec-kit implement/checklist templates (re-read) | https://github.com/github/spec-kit | "Done When" list: tasks marked, validated against spec/plan/tests; checklists test requirement quality not code (commit f6e72bc) | slash commands | 2026-10-16 | Borrow Done-When wording; advisory only, needs hooks |
| TDAD | https://arxiv.org/abs/2603.17973 | Test-impact map as agent skill; open source tool; 70% regression cut in small study | Python tool, local | 2026-10-16 | Idea only: dependency-to-tests map; not installed; spike if regression is a problem |
| ExecCritic | https://arxiv.org/abs/2609.09133 | Separate Test and Repair agents with frozen tests; RL-trained Qwen | research code | 2026-10-16 | Reference design for test/implementer separation; not installed |
| RETRACE | https://arxiv.org/abs/2608.08950 | Training-free backward-reconstruction patch verifier | research | 2026-10-16 | Reference; optional spike |
| SWE-Review | https://arxiv.org/abs/2607.06065 | Agentic reviewer benchmark and trained reviewers | research | 2026-10-16 | Reference for reviewer design (tool-using, diagnosis-feeding) |
| ImpossibleBench | https://arxiv.org/abs/2510.20270 | Measures test-exploiting; read-only tests mitigation | benchmark | 2026-10-16 | Evidence; possible harness to test own guard hook |
| EvilGenie | https://arxiv.org/abs/2511.21654 | Reward-hacking benchmark incl. Claude Code | benchmark | 2026-10-16 | Evidence only |
| nizos/tdd-guard | https://github.com/nizos/tdd-guard | Hook that enforces TDD; maintainer discussion #192 questions TDD value after Chen et al. (Exa snippet only; repo not opened) | Claude Code hook | not opened | Not evaluated beyond snippet; skip |
