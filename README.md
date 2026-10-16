# Autonomy Research

A **project-development research agent** for Claude Code. It finds tools and GitHub repos,
works out how systems connect, tests whether an approach is feasible, and writes cited findings
and small Mermaid diagrams. It is a plugin (`research-agent`) and a template repo in one.

The parent goal is a fully autonomous Claude Code engineer. This agent does the research that
engineer will need first, and every answer it gives cites a page it actually opened.

Requires Claude Code 2.1.292 or later.

## Quick start

**Plugin: use the skills in your own projects.**

```bash
claude plugin install research-agent --marketplace jcallahanp/Autonomy-Research
```

Start `claude`, then run `/research-agent:setup` (or say "set up the research agent").
Marketplace name: `research-agent-marketplace`. Details: [docs/installation.md](docs/installation.md).

**Template: a research workspace, with cloud sessions.** Click **Use this template** on GitHub,
or clone the repo. Cloud sessions load `.claude/` and `.mcp.json` with no install. Steps:
[docs/cloud-sessions.md](docs/cloud-sessions.md). Not sure which to pick?
[docs/plugin-vs-template.md](docs/plugin-vs-template.md).

Four tools are claude.ai connectors you connect by hand (Parallel Search, Exa, Context7,
Mermaid Chart): [docs/connectors.md](docs/connectors.md). DeepWiki, Firecrawl and Playwright come
bundled and need no keys.

## Skills

| Skill | What it does |
| --- | --- |
| `research` | Splits a question into facets, runs workers, merges cited findings, and has a verifier check them. |
| `tool-scan` | Finds and judges candidate tools or repos for a need, and logs them in the tool registry. |
| `repo-triage` | Reads a repo's README, manifest and scorecard to say if it is safe to install. Never runs it. |
| `setup` | Checks which of the seven tools are connected and prints steps for the missing ones. |
| `interview` | Turns a vague idea into EARS requirements, one question at a time. |
| `system-map` | Draws a system as small Mermaid diagrams, one concern per file. |
| `spike` | Tests up to three named paths for feasibility, in isolated workers. |
| `self-test` | Scores the plugin once with `claude plugin eval` against a no-plugin baseline. |
| `self-improve` | Runs a capped round of changes to the plugin itself, re-measured against a frozen exam, ending in a pull request. |
| `using-research-agent` | The index of the skills above, injected at session start. |

## Where outputs land

| Output | Location |
| --- | --- |
| Cited findings and their index | `research/findings/` |
| Run ledger | `research/runs/` |
| Requirements | `research/requirements/` |
| Spike results | `research/spikes/` |
| Tools evaluated | `research/tool-registry.md` |
| Unanswered questions | `research/open-questions.md` |
| Diagrams | `docs/diagrams/` (index: [docs/diagrams/index.md](docs/diagrams/index.md)) |

## Checks and self-test

```bash
bash tests/check.sh                    # structure checks
bash tests/check-mermaid.sh            # diagram checks (slow, uses npx)
claude plugin validate plugin --strict # plugin manifest and frontmatter
```

CI runs the same checks: `.github/workflows/validate.yml`. For the eval suite, run
`/research-agent:self-test`. It asks you to confirm first, because it uses your plan usage.
More in [CONTRIBUTING.md](CONTRIBUTING.md).

## More

- [Proposal](docs/proposal/2026-10-16-research-agent-proposal.md) (approved)
- [Diagram index](docs/diagrams/index.md)
- [Changelog](CHANGELOG.md), [Security](SECURITY.md), [Contributing](CONTRIBUTING.md)

## Status

v0.1. The skills, agents, hooks, evals and docs are in place. Expect rough edges; open an issue.

## License

MIT. See [LICENSE](LICENSE).
