# Intake (Area 1) - digest
Source: research/findings/engineer-intake.md; verification: 19 of 20, 1 unverified (corrected in text 2026-10-16)

## Decision
Extend the interview skill into a budgeted two-phase intake protocol, all prompt and file structure inside Claude Code, free, nothing to install (Recommendation section). Confidence medium; the numeric budgets are worker proposals that need a spike.
- Step 0 size gate: a diff describable in one sentence skips intake (A1).
- Restate any "do X with Y" as a question about the problem, then write goal, constraints and ruled-out options for John to confirm. Question framing beat a "don't be sycophantic" prompt (P5). Strong models answer the literal request 0.75-0.92 of the time (P9). XY-problem capture (P12).
- Open phase: one "tell me about the last time" question per turn along a JTBD timeline over a fixed coverage list (E6, E7, E14, E18). Free-form LLM interviewing finds "less than half" of implicit requirements (E11). A fixed slot structure reached IRE 0.69 (E12).
- Explore branch on "I don't know" or unnamed options: dispatch the research skill, verify every candidate URL and repo, and show a table of at most 5 options with explanation cards (U5, U7, U8, P15, P19). 3-13% of citation URLs across commercial LLMs and deep-research agents are hallucinated (U7; corrected after verification).
- Closed phase in the spec-kit `/clarify` shape via AskUserQuestion in the main session: one question per call, 2-5 options, the recommended option first, a "why it matters" line, a cap of 5 and a Deferred list (E23, E28, A29). AskUserQuestion is not available in subagents (A30).
- Push back once with the concrete cost, then respect John's call and record an "accepted over objection" ADR (P24, P20).
- Play back a batched glossary of dictated names, with explicit confirmation only where an error is costly (E42, E43). Stop when every coverage heading is Clear or Deferred, John says done, or the cap is hit (E28, E30, E25).
- Artifact: a Markdown spec (goal, EARS requirements each with a fit criterion, acceptance scenarios, constraints, deferred list, glossary, decision log; E1, E4, E34) plus a JSON task list with a `passes` field and a verification command per item (A36, A37). Approval goes in a file, not ExitPlanMode alone (A20, A21, A22).

## Alternatives and rejected
- spec-kit `/specify` + `/clarify` or OpenSpec adopted directly: kept as alternative. Free Markdown frameworks; OpenSpec licence not checked (A4, A6).
- Kiro-style flow: kept as alternative for its format only. Kiro is a separate IDE (A3, E3).
- OntoAgent-style slot ontology: kept as alternative. Best measured gains, but web-app domain only and it needs scenario data (E12).
- Claude Code plan mode alone: kept as alternative. Cheapest, but it has gate bugs (A21).
- Gemini Deep Research collaborative planning: kept as alternative. Paid, preview, separate engine (U1).
- Static checklist of dimensions: kept as alternative. Cheap but goes stale (worker judgement).
- Plain "don't be sycophantic" system line: kept as alternative. Weaker (P5).
- Fine-tuned interviewer: rejected. Prompted models beat fine-tuned ones (E10).
- Pure free-form LLM interviewing: rejected. Under half of implicit requirements, found late (E11).
- Asking John to write EARS himself: rejected (worker inference).
- Confirming every entity: rejected. It frustrates callers (E43).
- spec-kit installed wholesale: rejected. Verbose multi-file output (A12).
- Kiro, Cursor, Devin: rejected. Different engines; Devin is paid and hosted (A10, A11; ruling that Claude Code is the engine).
- BMAD: rejected. Heavy pipeline for one user, v7 alpha (A8).
- Aider: rejected. No intake artifact; page not opened, search excerpt only (Tools evaluated).
- Deep-research output without URL verification: rejected (U7).
- Sensecape and TrailLM as UI: rejected. Research prototypes (U3).
- Heavy reference architecture for John: rejected (worker judgement).

## Stack
| Tool | What it does here | Where it runs | Cost | Evidence |
|---|---|---|---|---|
| Claude Code AskUserQuestion | Closed gap-closing questions: 1-4 questions with 2-4 options per call | Main session only, not subagents | Free (Recommendation) | A29, A30 |
| Interview skill (this repo) | Hosts the protocol: phases, budget, stop rule | Plugin skill | Free | U14-U21 |
| Research skill (this repo) | Explore branch: verified option map, hard cap of 8 workers | Plugin skill and workers | Free; token cost not stated | U22, U24 |
| spec-kit `/clarify` and `/specify` patterns | Prompt shape copied, not installed | Prompt text | Free | E23, E28, A4 |
| EARS + Volere fit criterion | Format of the requirements in the spec | Notation | Free | E1, E2, E4 |
| JSON task list with `passes` | Machine-owned checklist edited only through its status field | Repo file | Free | A36, A37, A38 |
| ADR (Nygard) | "Accepted over objection" and constraint log | Repo file | Free | P20, P25 |
| Official MCP registry API | One candidate source for the explore branch; listings are unvetted | curl, keyless | Free | U9, U11 |
| urlhealth idea | URL check before John sees a candidate; idea copied, tool not installed | n/a | Free | U8 |

## Setup steps
| Step | Automated or John | How it is verified |
|---|---|---|
| 1. Rewrite the interview skill: size gate, restate step, open phase, explore branch, closed phase, budget, stop rule, approval checkpoint | Automated (build) | Spike 9: `claude plugin eval` regex and file_exists graders on 3 real John briefs |
| 2. Wire the explore branch to the research skill plus a URL/repo verify step | Automated | Spike 11: planted fake tool names are caught |
| 3. Seed the glossary from the repo and John's known tools | Automated | Spike 3: entity repair on a real dictated transcript |
| 4. Write the spec and JSON task list templates | Automated | Spikes 4 and 7 |
| 5. Approval record as a file plus a script-checked state | Automated | Spike 8: file flag versus ExitPlanMode |
| 6. Choose how questions reach John when he is not in the session | **John** (decision) | Spike 6: async answers over a message channel and timeout behaviour |
| 7. Supply 3 past briefs and one dictated transcript for spikes 1, 3 and 9 | **John** (by hand) | Files present |

## Repo composition
- Skill: `plugin/skills/interview/SKILL.md` gains the explore branch, an "I don't know" path that dispatches research instead of recording a gap (today SKILL.md:26-28, U20), a closed phase, a budget, a stop rule, a glossary playback, a size gate and a plan-approval checkpoint (Implications). The five-whys probe moves after the option map (worker inference). Keep the file short, because long instruction files get ignored (A18).
- Skill reuse: the research skill serves as the explore branch (U22).
- Files per project: a Markdown spec with goal, EARS requirements with fit criteria, acceptance scenarios, constraints, Deferred list, glossary and decision log. Also a JSON task list with `passes` and a verify command, an ADR-style objection and constraint log, and an approval file (Implications).
- Hooks: none named. Approval needs a "script-checked state" (Implications).
- MCP servers: none new. The official MCP registry API is called by curl (U9).
- Superpowers: the findings do not keep or drop it for intake. Superpowers brainstorming as a sycophancy mitigation is untested (Open questions). Beads and Ralph: not addressed. Fresh-session execution of one task at a time comes from Anthropic's harness post (A38), not from Ralph.

## Spikes
| Spike | Probe | Pass criterion |
|---|---|---|
| 1 | Run 3 past John briefs through two-phase intake and through a free-form interview | Count implicit requirements found and questions asked; no pass line given |
| 2 | Recommended-default questions versus neutral ones | Whether the default biases John's answers; no pass line given |
| 3 | Glossary entity repair on a real dictated transcript with his tool names | Names corrected; no pass line given |
| 4 | Build one small feature from artifacts with and without anti-goals and decision log | Score difference; no pass line given |
| 5 | AskUserQuestion under `claude -p` / Agent SDK, with and without canUseTool | Observe block, error or auto-skip |
| 6 | Hands-off operator answers questions asynchronously | What happens on timeout |
| 7 | Markdown versus JSON task list on plan-following, about 5 runs | Adherence comparison |
| 8 | ExitPlanMode versus a file-based approval flag (issues #50176, #30090) | Whether ExitPlanMode is needed at all |
| 9 | 3 real John briefs, e.g. "dockerize this website" | Agent surfaces a non-user option and the hidden constraint (`claude plugin eval` graders) |
| 10 | Explore branch on one real John topic | Count of verified candidates he had not known |
| 11 | Plant fake tool names | Verify step catches them |
| 12 | Time box with 3 versus 5 option-narrowing rounds | John can state the requirements afterwards |

## Requirements served
- R1: the restate step plus the goal, constraints and ruled-out record, the coverage list and the glossary playback come before any design (P5, P12, E42).
- R2: "do X with Y" becomes a question about the problem; the options table always includes a non-user option (P9; pushback Q&A).
- R3: one objection with the cost, an alternative and the cheapest test, then an ADR if John overrides (P24, P20).
- R4: the open phase asks one open question per turn (E14, E18). The closed phase is multiple choice, not yes/no chains (E23); see Tensions.
- R5: a table of at most 5 options with a marked recommendation and explanation cards (P15, P19).
- R8 (input): the spec and JSON task list are the hand-off to planning (A36).
- R19: the explore branch runs the bounded research skill (hard cap of 8 workers, U24) and verifies every candidate (U7, U8).
- Q2: the spec, task list and approval live in files (A20-A22).
- Q4: every task carries a verification command and a `passes` field (A37).
- Q5: the skill file and the spec stay short (A18, A12).

## GTM scenario
- Scan as-is: gap. The intake findings do not cover existing systems.
- Fix Attio tables and views: gap, apart from intake scoping. A brief like "fix the Attio tables" goes through restate-as-question and the goal and constraint record (P5, P12). Dictated tool names (Attio, Clay, n8n, Outreach) go through glossary playback; coined names are among the hardest entities in the voice benchmark (E43, E45).
- Set up Clay workflows: gap.
- Clean data: gap.
- Finish tooling: gap. The explore branch could surface tools John has not named (U22), but nothing in the findings is GTM-specific.

## Tensions
- AskUserQuestion works only in the main session (A30), and its behaviour under `claude -p` is unverified (Open questions; spike 5). That conflicts with R14 and R15 (batched approvals over SMS, unattended overnight runs). Who approves in a hands-off setup is unanswered (Open questions).
- R4 bans chains of yes/no questions. The closed phase is multiple choice with a recommended default (E23), and NN/g warns that closed questions can lead (E16). The findings read the two as a funnel, not a conflict, but bias is untested (spike 2).
- JSON versus Markdown for the task list was left unresolved here (Contradictions). Planning chose `tasks.json`; the A/B is still spike 7.
- The verify step's rationale originally said deep-research agents hallucinate 3-13% of URLs. The verifier marked that unverified, and it was corrected to "across commercial LLMs and deep-research agents" (Verification). The decision still holds on U7 and U8.
- The numeric budgets (cap of 5 questions, the 20-turn, 3-5-options and 3-round figures) are worker proposals with no source (Open questions). The requirements also set no time budget (requirements Gaps).
- No opened study tests any elicitation method with a non-expert dictating by voice (Open questions).
- The anti-goals section of the spec has no opened evidence; it is a worker addition (What does the intake artifact contain).
- The explore branch spends research-skill workers on every "I don't know", and no cost ceiling is set for that (requirements Gaps; U24).

## Open for John
- Which channel carries intake questions and approvals when he is away (SMS, Slack or another), and what the agent does on timeout (spike 6; requirements Gaps).
- Whether he accepts recommended-default multiple-choice questions in the closed phase (spike 2).
- Where constraint and objection records persist: CLAUDE.md, memory or a file (Open questions: a product decision).
- Supplying 3 past briefs and a dictated transcript for spikes 1, 3 and 9.
