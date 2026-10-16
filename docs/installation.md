# Installation

research-agent needs Claude Code 2.1.292 or later (`claude --version`). It has two install
paths. If you are not sure which one you want, read [plugin-vs-template.md](plugin-vs-template.md).

## Path A: the plugin (your own projects, on your machine)

1. Install it in one step:

   ```bash
   claude plugin install research-agent --marketplace jcallahanp/Autonomy-Research
   ```

   Or in two steps. The marketplace name is `research-agent-marketplace`:

   ```bash
   claude plugin marketplace add jcallahanp/Autonomy-Research
   claude plugin install research-agent@research-agent-marketplace
   ```

   The default scope is `user`. Add `--scope project` or `--scope local` to narrow it.
2. Start `claude` in any project. Run `/research-agent:setup`, or say "set up the research agent".
3. Connect the claude.ai connectors that setup reports as missing. See [connectors.md](connectors.md).
4. To update later: `claude plugin update research-agent@research-agent-marketplace`, then restart.

### Verify path A
- `claude plugin list` shows `research-agent`.
- At session start, Claude's context holds the skill index (`using-research-agent`) and the first
  30 lines of `research/findings/INDEX.md`, when that file exists in your project.
- Type `/` and look for `/research-agent:setup`.
- `/research-agent:setup` ends with "All seven tools present." or one line per missing tool,
  `<tool>: missing, fallback <fallback>`.
- `/mcp` lists the bundled servers as `plugin:research-agent:<server>`.

## Path B: the template (a research workspace, also cloud sessions)

1. On GitHub, open the repository and choose **Use this template**. Or run
   `git clone https://github.com/jcallahanp/Autonomy-Research`.
2. Open the new repo in `claude` locally, or start a cloud session. See [cloud-sessions.md](cloud-sessions.md).
3. Locally, accept the one-time approval prompt for each server in `.mcp.json`. Cloud sessions
   load `.claude/` and `.mcp.json` with no install and no prompt.
4. Say "set up the research agent". Nothing is installed on this path, so the skills load from
   `.claude/skills/` without the `research-agent:` prefix (for example `/setup`).

### Verify path B
- The SessionStart hook in `.claude/settings.json` injects the skill index. In a cloud session
  the hook runs only when `CLAUDE_CODE_REMOTE=true`. Locally the index is not injected;
  ask "which research skills do you have?" to see the skills in `.claude/skills/`.
- Setup reports "All seven tools present." or the missing tools with their fallbacks.
- `/mcp` lists `deepwiki`, `firecrawl` and `playwright`.

## Troubleshooting

- **A connector is missing.** Setup names it and its fallback. Connect it as described in
  [connectors.md](connectors.md), then start a new session so the tools load. Research still
  runs on the fallbacks and says so in its output.
- **A site returns 403 or 429.** Research does not guess. The claim goes under Gaps in the
  findings file. It may retry with Firecrawl or, as a last resort, Playwright. Cloud sessions
  can also block hosts that the environment's network setting does not allow.
- **Playwright does not start.** It needs Node and a browser download on first use. Run `/mcp`
  for its status. If it fails, research continues without it; pages that need a browser are
  listed under Gaps. Cloud sessions use the pre-installed Chromium through
  `plugin/scripts/playwright-mcp.sh`.
- **A bundled server is absent.** Run `/mcp`. For the plugin, run `claude plugin list` to
  confirm `research-agent` is enabled.
- **The self-test asks you to trust the plugin.** `claude plugin eval` runs plugin code as you,
  so the first run in an untrusted directory asks for confirmation. Read the plugin, then say
  yes. Do not add `--trust-plugin` on code you have not read.
- **Skills not found.** Restart Claude Code after install or update.

## Uninstall

- Plugin: `claude plugin uninstall research-agent`, then
  `claude plugin marketplace remove research-agent-marketplace`. Add `--keep-data` to the
  first command if you want to keep the plugin's data directory.
- Template: delete the folder or the GitHub repository. Connectors live on your claude.ai
  account, so remove them under Customize > Connectors if you no longer want them.
