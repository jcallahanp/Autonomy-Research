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
| gitleaks | 8.30.1 | github-release | 2026-10-16 | tag v8.30.1 (2026-02-21), read from `proxy.golang.org/github.com/zricethezav/gitleaks/v8/@latest`; sha256 551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb (`gitleaks_8.30.1_linux_x64.tar.gz`), checksum copied from vendor checksum files, not re-verified by download |
| osv-scanner | 2.7.0 | github-release | 2026-10-16 | tag v2.7.0 (2026-10-12), read from `proxy.golang.org/github.com/google/osv-scanner/v2/@latest`; sha256 160c6253e2922e9e0a6a9771c5c4c40a4b3c6090b34a3cdd5e80c96cc2e4218b (`osv-scanner_linux_amd64`), checksum copied from vendor checksum files, not re-verified by download |
| sops | 3.13.3 | github-release | 2026-10-16 | tag v3.13.3, latest on `proxy.golang.org/github.com/getsops/sops/v3/@latest`; sha256 TO-PIN on setup day from `sops-v3.13.3.checksums.txt` on the release page |
| bun | 1.4.3 | github-release | 2026-10-16 | `npm view bun version`; needed by the Claude Code Channels plugins; sha256 TO-PIN on setup day from `SHASUMS256.txt` on the bun-v1.4.3 release page |
| semgrep | 1.181.0 | pipx | 2026-10-16 | `pip index versions semgrep` (PyPI) |

Release downloads and their sha256 live in `engineer/templates/release-pins.txt`; a TO-PIN row stops
`setup-root.sh --install` until the checksum is read on setup day.

## Apt repository keys

`engineer/templates/apt-repos.txt` holds these; `setup-root.sh` refuses a key file whose primary keys differ.

| Repo | Primary key fingerprint(s) | Read on | Source |
| --- | --- | --- | --- |
| google-chrome apt key | EB4C1BFD4F042F6DDDCCEC917721F63BD38B4796 | 2026-10-16 | matches https://www.google.com/linuxrepositories/ |
| nodesource apt key | 6F71F525282841EEDAF851B42F59B5F99B1BE0B4 | 2026-10-16 | read from the key file at its URL; no independent publication found: trust-on-first-use |
| github-cli apt key | 2C6106201985B60E6C7AC87323F3D4EA75716059, 7F38BBB59D064DBCB3D84D725612B36462313325 | 2026-10-16 | matches github.com/cli/cli `docs/install_linux.md` |
| cloudflare apt key | CC94B39C77AE7342A68B89628A682D308D4E5E73 | 2026-10-16 | read from the key file at its URL; no independent publication found: trust-on-first-use |

## GitHub Actions

Pinned by full commit SHA in `engineer/templates/project/.github/workflows/checks.yml`.

| Action | Tag | Commit | Read on |
| --- | --- | --- | --- |
| actions/checkout | v7.0.1 | 3d3c42e5aac5ba805825da76410c181273ba90b1 | 2026-10-16 |

## Managed settings

The managed-settings key names in `engineer/templates/` were checked against
code.claude.com/docs/en/settings and code.claude.com/docs/en/permissions on 2026-10-16.
Permission rules match the command string only: a `Bash(git push *)` deny rule does not stop
`/usr/bin/git push` or `sh -c "git push"`. The PreToolUse hooks (`engineer/plugin/hooks/`) are the
guard for those; the deny rules are a first, cheap layer.
