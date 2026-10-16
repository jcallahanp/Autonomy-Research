# How agentic coding tools do intake

Brief: How do current agentic coding tools structure the step from a user request to an approved plan, and what do maintainers and users report works and fails?
Run: research/runs/engineer-intake/PLAN.md

Reading note: all pages below were opened 2026-10-16 with Parallel web_fetch (objective excerpts) unless stated. Search-only results are not cited.

## 1. How each tool structures intake and what artifact it produces

### Takeaway
Three families. (a) Read-only plan then approve: Claude Code, Cursor, Devin, Aider ask mode; artifact is one plan file or chat plan. (b) Phase-gated spec files: Kiro (requirements, design, tasks), spec-kit (spec, plan, tasks), OpenSpec (proposal, delta specs, design, tasks). (c) Role/skill pipelines: BMAD (brief, PRD, spec, architecture, tickets). Medium-high confidence; Aider and BMAD intake details are thinner.

### Cited findings
- Claude Code plan mode is read-only exploration then a plan; docs recommend it only when scope is uncertain, multi-file or unfamiliar — https://code.claude.com/docs/en/best-practices (page dated 2026-10-06), opened 2026-10-16, Parallel fetch — Quote: "If you could describe the diff in one sentence, skip the plan."
- Claude Code docs describe an interview pattern that writes SPEC.md, then executes in a fresh session — same URL — Quote: "Interview me in detail using the AskUserQuestion tool. Ask about technical implementation, UI/UX, edge cases, concerns, and tradeoffs."
- Kiro specs are three files per feature — https://kiro.dev/docs/web/specs/ (via search result page, fetched content seen in search; re-confirmed at https://kiro.dev/docs/specs/quick-spec.md), opened 2026-10-16 — Quote: "requirements.md - user stories and acceptance criteria in EARS notation"
- Kiro Quick Spec (docs page dated by search to Jun 2026) asks questions first, then writes all three files without approval gates — https://kiro.dev/docs/specs/quick-spec.md — Quote: "you answer clarifying questions up front and land directly on an actionable task list."
- spec-kit /specify writes a spec, caps open questions, and prefers defaults — https://github.com/github/spec-kit/blob/main/templates/commands/specify.md — Quote: "Make informed guesses based on context and industry standards"; "LIMIT: Maximum 3 [NEEDS CLARIFICATION] markers total"
- spec-kit /specify gates the spec with a quality checklist (max 3 fix iterations) and requires technology-agnostic measurable success criteria — same URL — Quote: "Success criteria are technology-agnostic (no implementation details)"
- OpenSpec: `/opsx:propose` creates a change folder with four artifacts that the human reviews before code — https://github.com/Fission-AI/OpenSpec/blob/main/README.md — Quote: "Your AI writes these; you review the plan before any code is written."
- OpenSpec specs are plain Markdown WHEN/THEN scenarios, delta-based, archived after apply — same URL and https://github.com/Fission-AI/OpenSpec/blob/main/docs/team-workflow.md — Quote: "Archiving folds a change's deltas into your main openspec/specs/ and moves the change folder to openspec/changes/archive/YYYY-MM-DD-<name>/."
- BMAD v6.12 stable / v7 alpha: right-sized path; a well-defined intent goes to bmad-spec then bmad-build, epics go through bmad-ticket (tickets.toml) — https://docs.bmad-method.org/plan/choose-a-planning-path/ (dated 2026-10-12) — Quote: "The spec skill writes the contract; it does not help you figure out what you want."
- BMAD has an unattended build skill — same URL — Quote: "To run stories unattended instead, give `bmad-build-auto` the story as its intent, one run per story"
- Aider has no plan artifact; ask mode discusses read-only, then "go ahead" in code mode executes; architect mode splits proposal from edit — https://aider.chat/docs/usage/modes.html (seen in search result; the page itself was not separately fetched, see Gaps) — Quote: "Saying something as simple as “go ahead” in code mode will have aider execute on the plan you've been discussing."
- Devin interactive planning: initial assessment (relevant files, findings, implementation questions) then a detailed plan with code citations — https://docs.devin.ai/work-with-devin/interactive-planning — Quote: "Devin will wait thirty seconds for feedback from you before automatically proceeding with its plan."
- Cursor plan mode: researches, asks clarifying questions, writes a Markdown plan with file paths and to-dos — https://cursor.com/blog/plan-mode (2025-10-07) — Quote: "it creates a Markdown file with file paths and code references. You can edit the plan directly, including adding or removing to-dos."

### Contradictions
- None found on structure. (BMAD's pre-v6 agent-persona pipeline versus the 2026 skill-based v6/v7 flow differs; only the current README/docs were read.)

### Inferences
- Only Devin's default (auto-proceed after 30 s) and BMAD's build-auto are designed for no human in the loop; everything else assumes a human approves the plan. (Devin page, BMAD path page.)
- The spec-kit /specify cap of 3 unresolved questions with informed defaults is the closest published model to "ask little, assume and record".

### Gaps
- Aider's own failure modes and the architect-mode blog (https://aider.chat/2024/09/26/architect.html) were not opened; Aider modes page seen only through search result excerpt.
- BMAD's elicitation/interview style (how many questions, format) not opened; only planning-path and README.
- Kiro docs/specs pages: content was seen through search result excerpts for the main specs page; only quick-spec and requirements-first were treated as quoted source here.

## 2. Reported failure modes

### Takeaway
Consistent reports: specs too long and repetitive, one workflow applied to every task size, agent ignores or over-follows spec text, wrong-problem specs (spec amplifies bad understanding), unreviewed assumptions silently expand, and in Claude Code itself plan-approval state bugs. Confidence: high for verbosity and size-mismatch (multiple independent sources); medium for anchoring on user wording (no direct source found).

### Cited findings
- Fowler/Thoughtworks (2025-10-15): spec-kit and Kiro too verbose for small tasks — https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html — Quote: "To be honest, I’d rather review code than all these markdown files."
- Same source: agent ignores or over-follows — Quote: "I frequently saw the agent ultimately not follow all the instructions."
- Same source: spec-kit research notes on existing classes were treated as new specs — Quote: "the agent ignored the notes that these were descriptions of existing classes, it just took them as a new specification and generated them all over again, creating duplicates."
- Same source: skepticism of big upfront specs — Quote: "I’m very skeptical that lots of up-front spec design is a good idea, especially when it’s overly verbose."
- Nearform (2026-06-24): model fills unstated gaps with defaults that compound — https://nearform.com/insights/lessons-from-real-world-failures-using-spec-driven-development — Quote: "AI systems don’t leave gaps. If you don’t specify a detail, the model assumes it for you."
- Nearform: SDD does not fix a wrong understanding — Quote: "SDD is an execution tool, not a discovery tool, so use it only after you have a firm grasp of what you’re building."
- Kiro issue #3526 (2025-10-27, closed not_planned): design docs 500 to 1,000+ lines — https://github.com/kirodotdev/Kiro/issues/3526 (via search excerpt of the issue page, fetched in same search call; treat as excerpt) — Quote: "kiro is almost always overly complicating design and creating document that is 500+ lines to read and approve."
- Claude Code best practices names over-long instruction files as a failure — https://code.claude.com/docs/en/best-practices — Quote: "If your CLAUDE.md is too long, Claude ignores half of it because important rules get lost in the noise."
- Claude Code best practices names unverified plausible output — same URL — Quote: "Claude produces a plausible-looking implementation that doesn’t handle edge cases."
- Claude Code plan-mode state bugs: ExitPlanMode returned "not in plan mode" and the agent treated that as approval (issue #50176, 2026-04-17) — https://github.com/anthropics/claude-code/issues/50176 — Quote: "The agent interpreted that error as implicit approval and started writing files."
- ExitPlanMode auto-approved under acceptEdits (issue #30090, 2026-03-02) — https://github.com/anthropics/claude-code/issues/30090 — Quote: "ExitPlanMode tool is auto-approved without showing any approval dialog to the user."
- Approved plan read as green light beyond the user's request (issue #24454, 2026-02-09, closed duplicate) — https://github.com/anthropics/claude-code/issues/24454 — Quote: "Claude treats ExitPlanMode approval as a green light to implement the full plan"
- Anthropic harness post: models mark features done without end-to-end testing — https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents — Quote: "Claude tended to make code changes, and even do testing with unit tests or `curl` commands against a development server, but would fail recognize that the feature didn't work end-to-end."
- Anthropic harness post (2026-03-24): evaluators approve weak work — https://www.anthropic.com/engineering/harness-design-long-running-apps — Quote: "Out of the box, Claude is a poor QA agent."  (seen via search excerpt; page not separately fetched)

### Contradictions
- Cursor says plans "significantly improve the code generated" (https://cursor.com/blog/plan-mode) while Fowler reports plain AI-assisted coding would have been faster and more controllable than spec-kit (https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html). They test different things (single lightweight plan versus multi-file spec workflow); no controlled comparison found.

### Inferences
- "Anchoring on the user's words" has no direct primary source here; the closest are Nearform's gap-filling and spec-kit's own rule to mark only high-impact ambiguities. I infer the risk is real for a hands-off operator because gaps get filled by defaults (Nearform) and nobody corrects them.
- Plan-approval gates are fragile in Claude Code itself (three issues). A hands-off engineer should not rely on ExitPlanMode as the approval record; use a file plus a script-checked state.

### Gaps
- No published measurement of plan-ignoring rates per tool; only anecdotes and issues.
- No source found on Devin or Cursor plan failure modes.

## 3. Which tools ask questions back, how many, in what style

### Takeaway
Claude Code (AskUserQuestion), Cursor, Devin, Kiro Quick Spec and spec-kit all ask. Only spec-kit /clarify specifies one question at a time with a recommended option, a table of options, a hard cap of 5, and "yes/recommended" acceptance. Claude Code natively supports 1-4 questions of 2-4 options per call but is unavailable in subagents. Confidence high.

### Cited findings
- spec-kit /clarify: max 5, one at a time, multiple choice 2-5 options or <=5 word answer — https://github.com/github/spec-kit/blob/main/templates/commands/clarify.md — Quote: "Present EXACTLY ONE question at a time."
- spec-kit /clarify cap and ranking — same URL — Quote: "Maximum of 5 total questions across the whole session."; "select the top 5 by (Impact * Uncertainty) heuristic."
- spec-kit recommended option and accept-by-word — same URL — Quote: "Format as: `**Recommended:** Option [X] - <reasoning>`"; "accept the recommendation by saying \"yes\" or \"recommended\""
- spec-kit /clarify stops early and flags what it defers — same URL — Quote: "If quota reached with unresolved high-impact categories remaining, explicitly flag them under Deferred with rationale."
- spec-kit /clarify skips trivia — same URL — Quote: "Exclude questions already answered, trivial stylistic preferences, or plan-level execution details (unless blocking correctness)."
- spec-kit /specify batch style (up to 3 questions in a table with Custom option) differs from /clarify — https://github.com/github/spec-kit/blob/main/templates/commands/specify.md — Quote: "Wait for user to respond with their choices for all questions (e.g., \"Q1: A, Q2: Custom - [details], Q3: B\")"
- Claude Code AskUserQuestion: Claude writes questions and options; limits — https://code.claude.com/docs/en/agent-sdk/user-input — Quote: "each `AskUserQuestion` call supports 1-4 questions with 2-4 options each"
- AskUserQuestion not in subagents — same URL — Quote: "`AskUserQuestion` is not currently available in subagents spawned via the Agent tool"
- AskUserQuestion is routed through the host's callback, so an operator layer can answer it — same URL — Quote: "Claude requests user input in two situations: when it needs permission to use a tool (like deleting files or running commands), and when it has clarifying questions"
- Cursor: questions are part of plan mode — https://cursor.com/blog/plan-mode — Quote: "Answer clarifying questions on your requirements for the best output quality."
- Windsurf/Devin desktop Plan mode (Cascade): multiple options, forced questions with a keyword — https://docs.devin.ai/desktop/cascade/modes (seen only in search excerpt) — Quote: "asking at least one clarifying question before it writes the plan"
- Claude Code docs: prompt the interview to skip the obvious — https://code.claude.com/docs/en/best-practices — Quote: "Don't ask obvious questions, dig into the hard parts I might not have considered."

### Contradictions
- Kiro Quick Spec asks "a set of clarifying questions up front" with no stated cap, while spec-kit caps at 3 and 5. No count is published for Kiro; not a true conflict.

### Inferences
- spec-kit /clarify is the best template to copy: one question, why-it-matters line, a marked recommendation, accept-by-"yes", hard cap, defer list. It maps directly onto AskUserQuestion with the recommended option listed first.
- Because AskUserQuestion is unavailable to subagents, intake must run in the main engineer session.

### Gaps
- Exact AskUserQuestion behaviour in `claude -p` with no callback (does it block, error, or auto-skip?) was not verified; needs a spike.
- Question counts/style for Cursor, Devin, BMAD not published in pages read.

## 4. Handoff to execution and evidence the format matters

### Takeaway
Handoffs: Claude Code plan file under ~/.claude/plans, optionally edited with Ctrl+G, then a fresh-session SPEC.md; Kiro tasks.md run per task or in dependency waves; OpenSpec tasks.md checkboxes plus archive; BMAD tickets.toml and one Build session per story; Cursor Markdown to-dos; Anthropic harness uses a JSON feature list with a passes flag. The only direct evidence on format is Anthropic's statement that JSON resisted model tampering better than Markdown; it is an observation, not a benchmark. Confidence medium.

### Cited findings
- Claude Code: fresh session for execution; self-contained specs with verification — https://code.claude.com/docs/en/best-practices — Quote: "The most useful specs are self-contained: they name the files and interfaces involved, state what is out of scope, and end with an end-to-end verification step"
- Claude Code: unattended finishing relies on goal/Stop-hook checks — same URL — Quote: "The `/goal` and Stop hook versions are what let an unattended run finish correctly without you."
- Anthropic JSON feature list — https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents — Quote: "we landed on using JSON for this, as the model is less likely to inappropriately change or overwrite JSON files compared to Markdown files."
- Same source: edit only the status field — Quote: "We prompt coding agents to edit this file only by changing the status of a passes field"
- Same source: one feature at a time — Quote: "the next iteration of the coding agent was then asked to work on only one feature at a time."
- Kiro runs tasks.md as a dependency graph — https://kiro.dev/docs/web/specs/ — Quote: "Kiro builds a dependency graph of the tasks in your tasks.md and groups independent tasks into waves"
- Kiro requirements use EARS so they translate into tests — https://kiro.dev/docs/specs/feature-specs/requirements-first.md — Quote: "Easy to translate into test cases"
- OpenSpec task conventions — https://github.com/Fission-AI/OpenSpec/blob/f917b8be5e1100189ef62320ba9322763053640e/docs/concepts.md — Quote: "Keep tasks small enough to complete in one session"
- BMAD plan joins tickets and judges the combined result — https://docs.bmad-method.org/plan/choose-a-planning-path/ — Quote: "The breakdown is an execution plan, not a promise that nothing will change."
- Cursor: build directly from the plan, optionally commit it — https://cursor.com/blog/plan-mode — Quote: "Optionally, save the plan as a Markdown file in your repository for future reference."
- Plans drift; regenerate — https://gist.github.com/celesteanders/21edad2367c8ede2ff092bd87e56a26f (secondary summary, seen in search excerpt only; not cited as primary) — see Gaps.

### Contradictions
- Anthropic says JSON beats Markdown for tamper-resistance (feature list). Kiro, spec-kit, OpenSpec and BMAD (mostly) use Markdown, and BMAD uses TOML for tickets. Different goals: Anthropic's is about resisting edits across sessions, the others about human review. A Hacker News commenter (https://news.ycombinator.com/item?id=45610996, search excerpt only) argues for structured, code-transformable specs; unverified.

### Inferences
- Two artifacts, not one: a short human-readable intent/spec (Markdown, reviewed once) and a machine-owned checklist (JSON with a `passes` field plus verification command per item). I rest this on the Anthropic JSON finding, Claude Code's "end with verification step", and OpenSpec/Kiro task conventions.
- Acceptance criteria written as WHEN/THEN or EARS (Kiro, OpenSpec, our own EARS rule) double as test names, supporting script-checked completion.

### Gaps
- No controlled evidence that Markdown vs JSON vs EARS changes plan-following rate; only Anthropic's anecdotal choice. Needs a spike.

## 5. What transfers to a Claude Code engineer run by a hands-off operator

### Takeaway
Transfers: spec-kit /clarify style (one question, recommendation, cap, defer), spec-kit /specify "informed defaults plus recorded assumptions", size-gated depth (skip plan when diff fits one sentence), EARS/WHEN-THEN acceptance criteria, task checklist with a status field, fresh-session execution, OpenSpec delta-per-change folder. Conflicts: approval gates that assume a human present (ExitPlanMode, Kiro phase gates, OpenSpec review step, Devin "Wait for my approval"), multi-file ceremonies, BMAD multi-persona planning for one user. Confidence medium.

### Cited findings
- Claude Code best practices: skip planning for tiny diffs — https://code.claude.com/docs/en/best-practices — Quote: "Sometimes you should skip planning and let Claude figure it out because the task is exploratory."
- Nearform: size-gate the process — https://nearform.com/insights/lessons-from-real-world-failures-using-spec-driven-development — Quote: "building an exhaustive prompt that contains a small spec of the change required, and/or using plan mode is usually faster here."
- Nearform: review early, not only at the end — Quote: "If you only review the output at the very end, you can lose hours or days unwinding the mess to find the root cause."
- Devin default auto-proceed gives a no-human path — https://docs.devin.ai/work-with-devin/interactive-planning — Quote: "By default, Devin will wait thirty seconds for feedback from you before automatically proceeding with its plan."
- Anthropic: planner expands 1-4 sentences into a spec for an autonomous harness — https://www.anthropic.com/engineering/harness-design-long-running-apps (search excerpt) — Quote: "a planner agent that took a simple 1-4 sentence prompt and expanded it into a full product spec."
- BMAD: autonomous loop add-on exists but is its own module — https://github.com/bmad-code-org/BMAD-METHOD/blob/main/README.md — Quote: "Builds, verifies, and retros a whole epic unattended"

### Contradictions
- None found.

### Inferences (recommendation, mine)
- Recommendation: build a small Claude Code skill modelled on spec-kit /specify + /clarify, without installing spec-kit. Steps: (1) size triage; one-sentence diffs skip planning. (2) Draft intent from the request, write assumptions explicitly. (3) Ask at most 3 to 5 questions via AskUserQuestion in the main session, one per call, recommended option first, only for items that change scope; everything else becomes a recorded assumption John can veto. (4) Write one SPEC.md (WHEN/THEN criteria, out of scope, a verification command) plus a JSON task list with a `passes` field. (5) Execute in a fresh session, one task at a time, completion checked by script/Stop hook.
- Alternatives: OpenSpec (lightest of the framework options, change-folder + delta specs, npm CLI, MIT status not checked); Kiro (paid IDE, rejected, not Claude Code); BMAD v6/v7 (heavy, persona/skill pipeline; v7 is alpha); Claude Code native plan mode alone (cheapest, but gate bugs).
- Rejected: spec-kit installed wholesale (verbose multi-file output per Fowler); Kiro, Cursor, Devin (different engines, Devin paid); Aider (no intake artifact).
- Spike before building: (a) behaviour of AskUserQuestion under `claude -p`/Agent SDK with and without canUseTool; (b) whether a hands-off operator can answer questions asynchronously (for example through a message channel) and what happens on timeout; (c) A/B of Markdown vs JSON task list on plan-following over, say, 5 runs; (d) whether ExitPlanMode is needed at all versus a file-based approval flag, given issues #50176 and #30090.

### Gaps
- Licences and install surface of OpenSpec and BMAD not checked (not installed or run, per rules).
- Who "approves" in a hands-off setup is a product decision for John; no source answers it.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Claude Code plan mode + AskUserQuestion | https://code.claude.com/docs/en/best-practices | Read-only plan, 1-4 questions with 2-4 options, plan file, ExitPlanMode gate | local CLI / SDK | 2026-10-16 | Use as engine; do not rely on ExitPlanMode as sole approval record (issues #50176, #30090) |
| GitHub spec-kit | https://github.com/github/spec-kit | /specify, /clarify (one question at a time, max 5, recommended option), /plan, /tasks templates | agent slash commands, Python CLI install | 2026-10-16 | Copy the clarify/specify prompt patterns; do not adopt wholesale (verbosity) |
| AWS Kiro specs | https://kiro.dev/docs/specs/ | requirements.md (EARS), design.md, tasks.md; Quick Spec mode | proprietary IDE/CLI | 2026-10-16 | Skip as tool; borrow EARS criteria and size-gating |
| OpenSpec | https://github.com/Fission-AI/OpenSpec | proposal/specs/design/tasks per change, delta specs, archive | npm CLI + slash commands | 2026-10-16 | Fallback if a ready-made framework is wanted; lighter than spec-kit |
| BMAD Method | https://github.com/bmad-code-org/BMAD-METHOD | Skill pipeline brief, PRD, spec, architecture, tickets, build, build-auto | skills in coding tool; needs uv | 2026-10-16 | Skip for one user; v7 alpha, heavy; reference for right-sizing |
| Aider modes | https://aider.chat/docs/usage/modes.html | ask / architect / code modes, no plan file | local CLI | 2026-10-16 | Skip; different engine, no artifact |
| Devin interactive planning | https://docs.devin.ai/work-with-devin/interactive-planning | Initial assessment, cited plan, 30 s auto-proceed | hosted, paid | 2026-10-16 | Skip; paid, hosted; borrow code-cited plan idea |
| Cursor plan mode | https://cursor.com/blog/plan-mode | Clarifying questions then editable Markdown plan with to-dos | proprietary IDE | 2026-10-16 | Skip; different engine |
