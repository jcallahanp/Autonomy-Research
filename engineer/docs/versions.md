# Pinned versions

Every version the engineer installs is pinned here with the date and where it was read.
User-level pins live in `engineer/templates/bootstrap-packages.txt`; this file is the record.
Re-pin by reading the source again on the day and updating both files in one commit.

| Package | Pin | Method | Read on | Source |
| --- | --- | --- | --- | --- |
| `@anthropic-ai/claude-code` | 2.1.301 | npm | 2026-10-16 | `npm view @anthropic-ai/claude-code version`; same as the CI pin in `.github/workflows/validate.yml` (at least 2.1.234) |
| `@playwright/mcp` | 0.0.83 | npm | 2026-10-16 | `npm view @playwright/mcp version` |
| `@playwright/cli` | 0.1.22 | npm | 2026-10-16 | `npm view @playwright/cli version` |
| `@mermaid-js/mermaid-cli` | 11.12.0 | npm | 2026-10-16 | Kept at the pin in `tests/check-mermaid.sh` and `research/blueprint/stack.md`; `npm view` shows 12.0.0 is out, not adopted in stage 1 |
| `@mermaid-lint/cli` (mermaid-lint) | 0.53.1 | npm | 2026-10-16 | `npm view @mermaid-lint/cli version`; the unscoped name `mermaid-lint` is not on npm; this package's maintainer is the author of github.com/jasonworden/mermaid-lint (engineer-briefing E59) and it ships the `mermaid-lint` binary |
| gitleaks | 8.30.1 | github-release | 2026-10-16 | tag v8.30.1 (2026-02-21), read from `proxy.golang.org/github.com/zricethezav/gitleaks/v8/@latest` |
| osv-scanner | 2.7.0 | github-release | 2026-10-16 | tag v2.7.0 (2026-10-12), read from `proxy.golang.org/github.com/google/osv-scanner/v2/@latest` |
| semgrep | 1.181.0 | pipx | 2026-10-16 | `pip index versions semgrep` (PyPI) |

Release checksums for downloaded binaries are recorded on setup day (Task 3, `templates/release-pins.txt`).
