---
name: interview
description: Front-loaded requirements interview that turns a vague idea into testable requirements. Use when the user wants to define, scope or specify something before building or researching it ("help me work out what I need", "interview me", "write requirements for X", "what should this do"), or when a research brief is too thin to split into facets. Asks one open question per turn, plays back what it heard, asks for anti-goals, probes goals with five whys, writes EARS requirements under Volere-style headings to research/requirements/<slug>.md, and ends with a missing/inconsistent audit.
---

# Interview

Turn what the user wants into requirements that research and building can be checked against.
The interview is conversation with the user; it needs no workers and fetches no pages. When the
user says "skip" or answers stay thin, write down what is known and record the gaps. Never
guess to fill them.

## Requirements

- When the interview starts, the skill shall pick a short kebab-case `<slug>` for the topic and
  tell the user the output path `research/requirements/<slug>.md`.
- When it asks, the skill shall ask exactly one open question per turn, and shall not stack a
  second question onto the same message.
- When the user answers, the skill shall play back what it heard in one or two sentences
  before the next question, and shall correct the playback if the user says it is wrong.
- When a goal is stated, the skill shall probe it with five-whys questions ("why does that
  matter?", up to five times) until the answer names the underlying need, so that a
  solution is not recorded as a requirement.
- When the goals are known, the skill shall ask for anti-goals: what the system must never do,
  and what is out of scope.
- If the user says "skip", or an answer is too thin to write as a requirement, then the skill
  shall stop asking about that heading, write what is known, and list the gap in
  `research/open-questions.md`. It shall not invent an answer.
- When it writes a requirement, the skill shall use EARS form ("When X, the system shall Y";
  "While X, ..."; "If X, then ..."; "Where X, ..."), one testable statement per line.
- Before it finishes, the skill shall run the audit below and report the result.

## Question order

Ask in this order, skipping what the user already answered. One question per turn.

1. Purpose: what is this for, and who is it for?
2. Why now, and what does success look like?
3. Goals, each probed with five whys.
4. Anti-goals and non-goals.
5. Constraints: platform, budget, time, tools already in use, things that cannot change.
6. Prior art: what exists, what was tried, what failed.
7. Quality needs: speed, safety, cost, privacy, reliability, how it is checked.
8. Open risks or unknowns the user already worries about.

If a question can be answered by reading the repo (for example the current tools or
`research/tool-registry.md`), read the file and offer the finding in the playback instead of
asking. Offer repo or web reconnaissance as an option; do not start it unasked.

## Output file

Write `research/requirements/<slug>.md` with these headings, in this order:

1. `# <Topic> requirements` and a two-line purpose.
2. `## Stakeholders and users`
3. `## Goals`, each with the need found by the five whys.
4. `## Anti-goals and out of scope`
5. `## Constraints`
6. `## Functional requirements`, EARS statements, numbered `R1`, `R2`, ...
7. `## Quality requirements`, EARS statements, numbered `Q1`, `Q2`, ...
8. `## Assumptions and risks`
9. `## Audit`, the result of the audit below.
10. `## Gaps`, each unanswered item, also copied to `research/open-questions.md`.

A requirement states behaviour or a limit, not a design. If a line names a library or file
layout and the user did not require it, move it to Assumptions.

## Audit

At the end, read the file back and answer for each heading:

- Missing: is anything the user said not written, or any heading empty with no gap listed?
- Inconsistent: do two statements conflict, or does a requirement contradict an anti-goal or
  constraint?
- Redundant or untestable: is any statement a duplicate, or impossible to check?

List each finding under `## Audit` with the requirement ids. Ask the user to settle conflicts;
do not choose silently. Then print the path, the count of requirements, and the open gaps.
