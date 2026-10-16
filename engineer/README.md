# engineer

Stage-1 template code for the autonomous Claude Code engineer. Everything here lands in
`/opt/engineer/` on the droplet (root-owned, read-only to the `engineer` user). The design is in
`research/blueprint/`; the build plan is `docs/plans/2026-10-16-engineer-stage-1.md`.
Setup day (John's one sitting on the droplet): [setup-day.md](../docs/engineer/setup-day.md).

## Layout
| Path | What it holds |
| --- | --- |
| `plugin/` | The `engineer` Claude Code plugin: skills, agents, hooks, MCP config |
| `bin/` | Sudo-target wrappers (`run-task`, `agent-run`, ...) |
| `scripts/eng/` | Shared Python helpers: `conf`, `schema`, `approval`, `paths`, `hosts`, `brokerlib` |
| `scripts/<area>/` | Supervisor, broker jobs, approvals, checks, egress, browser, root setup |
| `etc/engineer.conf` | Paths, users and commands; droplet defaults |
| `templates/` | Schemas, run defaults, protected paths, bootstrap pins, units, project skeleton |
| `docs/` | ADRs and `versions.md` (every pinned version, with the date) |

## Conventions
- **Root.** A `bin/` script finds its root with `root=$(cd "$(dirname "$(readlink -f "$0")")/.." && pwd)`;
  a script in `scripts/<area>/` goes two levels up; Python uses `Path(__file__).resolve().parents[N]`.
- **Config.** `<root>/etc/engineer.conf` is `KEY=VALUE` or `KEY="VALUE"` with `#` comments and no
  expansion. Bash sources it; Python reads it with `eng.conf.load(root)`, which refuses any line bash
  would expand. Droplet-only config (projects, egress lists) lives under `ETC_DIR`, never in git.
- **Privilege.** A sudo-target or root-run script never takes a secret, a secret path or a command
  from its caller. Secrets are decrypted by `secretbroker` with SOPS+age through `eng.brokerlib`.
- **Code.** Bash files start `#!/bin/bash` and `set -euo pipefail`. Python is 3.12 with the stdlib
  and PyYAML only. Each code file is at most 200 lines.

## Tests
`bash tests/engineer/run.sh [area ...]` runs `tests/engineer/<area>/test_*.sh` and each
`test_*.py`. Tests copy this tree into a temp dir (`mk_root` in `tests/engineer/lib.sh`,
`make_root` in `tests/engineer/testlib.py`), rewrite `etc/engineer.conf` to point inside it, put
stub commands in `<root>/bin/`, and run offline with no root, systemd or VM.
`bash tests/check.sh` runs them too, through `tests/rules/engineer.sh`.
