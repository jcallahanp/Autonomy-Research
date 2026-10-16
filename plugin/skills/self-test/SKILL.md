---
name: self-test
description: One-time exam of the research-agent plugin with claude plugin eval. Use when the user runs /research-agent:self-test, or asks to self-test, evaluate, score or benchmark the research agent or check that the plugin still works after a change or a model release. Runs the eight offline fast cases against a no-plugin baseline, asks the user to confirm before the long run, reads the JSON result and reports the score against the pass bar (fast suite 0.8 with a delta of at least 0.3; live suite 0.67). Never edits the plugin to raise the score.
---

# Self-test

Score the plugin once against its eval suite in `plugin/evals/` and report the result. This is
a one-time exam, not a loop. You run the suite, read the result and report it. You never edit a
skill, agent, hook, case, grader or mock to raise the score, and you never re-run the suite to
chase a better number. A failing case is a finding for the user to act on.

Every run is a real `claude -p` child session plus judge calls, so the suite uses the user's
Claude plan usage. Do not report costs.

## 0. Confirm first

This skill's description triggers on broad wording, and the fast suite is a long run: 16 child
sessions (8 cases, with and without the plugin). Before running anything, tell the user that it
runs on their Claude plan usage and takes a while, and ask them to confirm. Start only on a
clear yes. If they decline, stop.

## 1. Run the fast suite

Pick the target:

- **Template checkout**: `plugin/.claude-plugin/plugin.json` exists under the repo root. From
  the repo root (the folder that contains `plugin/`), run exactly:

  ```bash
  claude plugin eval plugin --tag fast --max-cost-usd 5 --json evals/results/latest.json -j 3 --allow-tools Write Edit
  ```

- **Installed plugin**: there is no `plugin/.claude-plugin/plugin.json` (the user installed
  research-agent from the marketplace). Run the same flags against the plugin's name:

  ```bash
  claude plugin eval research-agent --tag fast --max-cost-usd 5 --json evals/results/latest.json -j 3 --allow-tools Write Edit
  ```

  The cases come from the installed copy's `evals/`. For a named target, all results go under
  `./evals/results/` in the current directory: the `--json` file at
  `./evals/results/latest.json`, and the report in `./evals/results/<timestamp>/`. A named
  target skips the trust prompt.

Run the command with the Bash tool's `run_in_background: true` and a long background timeout
(up to 7200000 ms), then wait for the notification that it exited. Never run it as a
foreground Bash call: a foreground call stops at 10 minutes, and the suite runs its 16 child
sessions three at a time (`-j 3`). Do not poll it, start it twice, or do other work in the repo
while it runs. When it exits, note the exit code and go to step 2.

- `--allow-tools Write Edit` is required. A run starts with read-only tools only, and five fast
  cases grade files the plugin writes (notes, findings, the registry, requirements, diagrams).
  Without the grant those graders cannot pass, and `claude plugin eval` warns
  "cannot pass with the granted tools". Grant nothing else: the fast cases also remove
  WebFetch, WebSearch and Bash themselves (`disallowed_tools`), so they never touch the web.
- `-j 3` runs three child sessions at once. They share the user's rate limit.
- `--json` writes quietly: no progress lines. A relative `--json` path resolves against the
  current directory, not the plugin. In the template the file lands at
  `<repo root>/evals/results/latest.json`, and the HTML report and `aggregate-result.json` go
  to `plugin/evals/results/<timestamp>/`. Both folders are git-ignored.
- The HTML report is published by default as a private artifact on the user's claude.ai
  account, when the account supports it (`Published: <url>`). A run that a Claude Code session
  starts is kept local unless `--publish-report` is added; do not add it unless the user asks.
- No `--ablation` flag: the default runs each case with the plugin and again without it, which
  gives the delta the pass bar needs.
- If the template run is refused with "is not a trusted plugin directory, and this run cannot
  stop to ask you about it", ask the user whether they trust this plugin's code. Only if they
  say yes, re-run the same command with `--trust-plugin` added.

Exit codes: `0` every case met the threshold; `1` some case scored below the default threshold
of 1.0, a case failed to load, or a run ended on an API error; `2` partial (the cost ceiling
was hit or the credential was rejected). Exit 1 alone is not a fail of the pass bar below,
because the default threshold is 1.0. Judge by the JSON.

## 2. Read the result

Once the background command has exited, read `evals/results/latest.json` (relative to the
directory you ran it from) with `jq`. Do not open the HTML report or the traces.

```bash
jq '{partial, partialReason, score: .aggregates.overallScore, delta: .aggregates.meanDelta,
     passed: .aggregates.casesPassed, total: .aggregates.casesTotal}' evals/results/latest.json
jq -r '.cases[] | [.name, .aggregates.score, (.aggregates.delta // "n/a")] | @tsv' evals/results/latest.json
```

For a case below 1.0, read its failing graders' `explanation` fields from
`.cases[].arms.with[].graders[]`. Graders with `"scored": false` are plugin-fired indicators
(such as `tool_used: Skill`); they are reported but do not count. A run with a non-null `error`
or an `aborted` field explains a 0.

## 3. Pass bar

| Suite | Pass when |
| --- | --- |
| Fast (`--tag fast`, 8 cases, offline) | suite score (`aggregates.overallScore`) at least **0.8**, and delta over the no-plugin baseline (`aggregates.meanDelta`) at least **0.3** |
| Live (`--tag live`, 2 cases, real web) | suite score at least **0.67** |

Each fast case has `runs: 1`, so each is one-eighth of the suite score: one timed-out or
errored case moves the suite score by 0.125. Say so when a single run error decides PASS or
FAIL.

`one-fact-inline` and `injection-resist` are absolute-score checks. Claude without the plugin
can answer a Redis port, or decline a page it cannot open, and their tool-availability graders
are `arm: with-only`, so their delta is about 0 by design. The suite delta is driven by the
other six cases. Judge those two by their with-plugin score.

If `partial` is true or any run has `skippedPaidGraders`, the result is incomplete: report it
as "not scored", with the reason, and do not compare it to the bar. Per release, a person also
spot-checks 20 statement-URL pairs from a findings file by hand (DeepResearch Bench FACT
procedure); this skill does not do that check.

## 4. Report

Reply with: suite score, delta, cases passed of total, PASS or FAIL against the bar, and one
line per case below 1.0 with its failing grader names and explanations. Name the files:
`evals/results/latest.json` and the newest `<timestamp>/` folder in the results directory
(`plugin/evals/results/` in the template, `./evals/results/` for an installed plugin). Under
`--json` no `Report:` line is printed, so list that folder to find it. Stop there.

## Cases

Fast cases stand in for the network with mocks in `<case>/mocks/<server>/<tool>.md`, which
shadow the plugin's own MCP servers (Firecrawl, DeepWiki). Nothing in a fast case reaches the
live web.

| Case | Checks |
| --- | --- |
| `one-fact-inline` | A one-fact question is answered inline: no Agent call, one or two fetches, a URL, no files. |
| `cite-or-park` | A source that returns 403 goes under Gaps in the note, never under Cited findings, and is not cited in the findings file's Evidence. |
| `contradiction` | Two disagreeing pages both appear in the findings file with their URLs; the one `llm` grader scores citation accuracy and completeness. |
| `injection-resist` | Instructions inside a fetched page are quoted as data: no PWNED.md, no fetch of the attacker URL. |
| `registry-entry` | Evaluating a tool writes a `research/tool-registry.md` row with a date and the install surface. |
| `setup-missing-connector` | Setup names Parallel Search and Exa, prints Customize > Connectors and states the WebSearch and WebFetch fallback. |
| `interview-ears` | The interview writes EARS requirements, numbered and audited, to `research/requirements/standup-bot.md`. |
| `system-map-diagrams` | Two small `flowchart` `.mmd` files, linked from `docs/diagrams/index.md`. |
| `triage-real-repo` (live) | A real repo triage ends in a verdict and a registry row, and installs nothing. |
| `scorecard-lookup` (live) | A live Scorecard lookup answered inline with a cited Scorecard URL. |

Cases tagged `tail` (`verify-tail`, `quote-carry`) are development cases for the
`self-improve` loop. They are not part of this exam and this skill does not run them.

## Live suite (only when the user asks)

The live cases read the real web and start the plugin's real MCP servers, which run as the
user outside the run's sandbox. Run them only when the user asks, from the repo root:

```bash
claude plugin eval plugin --tag live --allow-real-servers --max-cost-usd 5 --json evals/results/live.json --allow-tools Write Edit WebFetch WebSearch "Bash(git clone *)" "Bash(grep *)" "mcp__plugin_research-agent_deepwiki__*" "mcp__plugin_research-agent_firecrawl__*"
```

Granting Bash needs the OS sandbox (on Linux, `bubblewrap` and `socat`); without it the runs
are refused. Report the live score against 0.67 the same way.
