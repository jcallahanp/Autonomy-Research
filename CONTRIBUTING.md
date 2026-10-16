# Contributing

Thanks for helping. Keep changes small and keep each one to a single concern.

## Run the checks

```bash
bash tests/check.sh            # structure: manifests, skills, agents, template wiring, docs
bash tests/check-mermaid.sh    # every diagram is linked, allowed, and renders (uses npx; slow)
claude plugin validate plugin --strict
claude plugin validate . --strict
```

`tests/check.sh` prints `FAIL <rule>: <detail>` for each problem and exits 1 if there is any.
New rules go in `tests/rules/<topic>.sh`. Write the rule first, watch it fail, then fix the
repo until it passes. Set `MERMAID_SKIP_RENDER=1` to run only the static diagram checks.

The same checks run in CI on every push and pull request
(`.github/workflows/validate.yml`).

Do not edit the plugin while `claude plugin eval` (the `self-test` skill) is running.
Never change a skill, grader or mock just to raise an eval score.

## Diagrams: one concern each

- One small `.mmd` file per concern, in `docs/diagrams/`. Never one giant design diagram.
- Use `flowchart` or `sequenceDiagram` only. Draw C4 levels as flowcharts.
- Link every file from `docs/diagrams/index.md`.

## Requirements: EARS

Write requirements in EARS form: "When X, the system shall Y." One requirement per line, each
one testable. Interview output lives in `research/requirements/<slug>.md`.

## Research rules

- Every claim about a tool cites a page that was opened. Search snippets are not sources.
- Log every tool you evaluate in `research/tool-registry.md`: name, link, what it does,
  verified date, verdict.
- Put what you cannot answer in `research/open-questions.md`. Do not guess.

## Other limits

- `CLAUDE.md` stays under 60 lines, with no imports and no procedures.
- Each `SKILL.md` stays under 500 lines, with a description under 1,536 characters.
- `.mcp.json` holds only keyless servers. Never commit a secret.
- Bump the version in `plugin/.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`
  together, and add a `CHANGELOG.md` entry.
