---
name: self-improve
description: Capped self-improvement loop for the research-agent plugin, scored against a frozen exam. Use when the user says "improve yourself", "self-improve", "run a self-improvement round" or "start round 2". Researches the plugin itself first, checks that research with the verifier and a 20-citation hand check, plans a short change list, implements it with new tail cases, re-measures the frozen fast exam paired (3 runs per case, 5 when budget allows), keeps only changes that do not drop the exam and have a stated reason, writes a changelog in docs/self-improvement/ and opens a pull request. At most 2 rounds per approval. Never edits a frozen case, grader or mock.
---

# Self-improve

Improve the plugin's own skills, agents and hooks in short, measured rounds. The exam stays
fixed while you change what it tests. A round ends in a pull request; the user's merge is the
only sign-off.

## Loop rules

- **Frozen exam.** The cases listed in `tests/frozen-exam.sha256` are the exam. `bash
  tests/check.sh` fails when any of their files changes. Never edit a frozen case's prompt,
  graders or mocks, and never rewrite the manifest in a round. Changing the exam is its own
  pull request, outside this loop.
- **Tail cases.** New cases go in new directories under `plugin/evals/`, tagged `tail` only
  (never `fast` or `live`). The author of the fixes writes them, so they are development cases,
  not a holdout. Their score is reported separately and never added to the frozen score.
- **Keep rule.** A change is kept only if the frozen fast exam does not drop in the paired
  re-measure (same cases, same run count, same model, before and after) and the findings file
  or the hand check gives a specific reason for it. Otherwise revert it and list it as
  rejected in the changelog.
- **Cap.** At most 2 rounds per approval from the user. After round 2, stop and ask.
- **Sign-off.** Open a pull request with the before and after numbers. Never merge it and never
  push to the default branch.
- **Budget.** Every eval run uses the user's Claude plan usage. Confirm before each one, as the
  `self-test` skill does. Never re-run a suite to chase a better number: fix the run count
  before measuring.

## Steps

1. **Confirm.** Tell the user the round's cost (two paired fast runs, one tail run, a research
   run) and ask for a yes. Ask whether the budget allows 5 runs per case instead of 3. Work on
   a new branch `self-improve/round-<n>`.
2. **Baseline.** Run `bash tests/check.sh`; it must pass with the manifest intact. Run the
   paired "before" measure of the frozen fast exam (commands below) on the current default
   branch.
3. **Research the plugin itself.** Run the `research` skill on "what should change in the
   research-agent plugin first, and why", with one internal-audit facet that cites the
   plugin's own files as `path:line`, and outside-evidence facets as needed. Use the slug
   `research-agent-self-improvement-r<n>`. The verifier appends its Verification section.
4. **Hand check 20 citations.** Pick 12 numbers, percentages or quotes spread across sections,
   and 8 more at random with a fixed seed (print the command). A worker re-opens each source
   and returns SUPPORTED, PARTIAL, UNSUPPORTED or UNREACHABLE with a quote of at most 30
   words; you never hold the pages. Write `research/runs/<slug>/hand-check.md`: picks,
   results, totals, and each failure pattern with the stage that introduced it (researcher,
   synthesizer, verifier).
5. **Plan.** Write `docs/self-improvement/<YYYY-MM-DD>-round-<n>-plan.md`: the loop rules,
   then one line per change with its files and its reason (a findings rank or a hand-check
   pattern). Show it to the user and implement only on a yes.
6. **Implement.** For each change, add a structural rule in `tests/rules/` first and watch it
   fail, then make the change and watch it pass. Add a `tail` case for pipeline behaviour the
   frozen exam cannot see. Keep prompts tight and update the EARS lines where behaviour
   changes. Run `bash tests/check.sh` until it passes.
7. **Re-measure.** Run the paired "after" measure with the same flags, and the tail suite once.
8. **Keep or revert** each change by the keep rule.
9. **Changelog.** Write `docs/self-improvement/<YYYY-MM-DD>-round-<n>.md`: a before/after
   table per frozen case, the tail scores in their own table, kept and rejected changes with
   reasons, the model id and Claude Code version. Add an Unreleased entry to `CHANGELOG.md`.
10. **Pull request.** Open it with the numbers and the changelog link. Stop.

## Commands

Run every eval from the repo root with the Bash tool's `run_in_background: true` and a long
timeout, as in the `self-test` skill. Do not edit the plugin while one runs.

The frozen fast exam, single run (the `self-test` command):

```bash
claude plugin eval plugin --tag fast --max-cost-usd 5 --json evals/results/latest.json -j 3 --allow-tools Write Edit
```

Paired measure, before and after: the same command with `--runs 3` (or `--runs 5`) and a named
result file. Raise `--max-cost-usd` only with the user's yes; a `partial` result is not scored.

```bash
claude plugin eval plugin --tag fast --runs 3 --max-cost-usd 5 --json evals/results/round<n>-before.json -j 3 --allow-tools Write Edit
claude plugin eval plugin --tag fast --runs 3 --max-cost-usd 5 --json evals/results/round<n>-after.json -j 3 --allow-tools Write Edit
```

Tail cases, reported separately:

```bash
claude plugin eval plugin --tag tail --max-cost-usd 5 --json evals/results/round<n>-tail.json -j 3 --allow-tools Write Edit
```

Live cases, only when the user asks (the `self-test` live command):

```bash
claude plugin eval plugin --tag live --allow-real-servers --max-cost-usd 5 --json evals/results/live.json --allow-tools Write Edit WebFetch WebSearch "Bash(git clone *)" "Bash(grep *)" "mcp__plugin_research-agent_deepwiki__*" "mcp__plugin_research-agent_firecrawl__*"
```

Read each result with the `jq` lines in the `self-test` skill, step 2. "Does not drop" means
the after suite score is at least the before suite score. Name any single case that dropped in
the changelog even when the suite held.

## Requirements (EARS)

- When a round starts, the loop shall run the research skill on the plugin and a 20-citation
  hand check before it changes any plugin file.
- When a round's diff changes a file listed in `tests/frozen-exam.sha256`, `tests/check.sh`
  shall fail and the round shall not be opened as a pull request.
- When the paired after-score of the frozen fast exam is below the before-score, the loop shall
  revert the change and list it as rejected.
- When a change is kept, the changelog shall name the findings rank or hand-check pattern that
  justifies it.
- When tail cases are scored, the loop shall report them apart from the frozen exam.
- When 2 rounds have run since the user's approval, the loop shall stop and ask.
