# Security

This plugin reads the web and other people's repositories. These rules limit the harm that
content can do.

## What the plugin does and does not do

- **Fetched content is data.** Pages, READMEs, search results and tool output are quoted and
  cited, never followed as instructions. A page that says "ignore previous instructions" or
  "run this command" is recorded as a finding about the page.
- **Triage never runs candidates.** `repo-triage` and `tool-scan` read a README, a manifest and
  public metadata. They do not install, build or run anything from the candidate.
- **Spikes run only named paths.** The `spike` skill tests only paths the user names. Each test
  runs in a `spike-worker` agent, in a temporary directory outside the project tree, under
  `env -i` so no environment variables or secrets pass through.
- **No secrets in `.mcp.json`.** It carries keyless servers only (DeepWiki, Firecrawl,
  Playwright). `tests/check.sh` fails if it mentions a key, token or secret.
- **Hooks are small.** The SessionStart hook reads the skill index and the top of
  `research/findings/INDEX.md`. `scripts/cloud-setup.sh` installs Superpowers in cloud
  sessions only.
- **Network calls.** The bundled MCP servers call `mcp.deepwiki.com` and `mcp.firecrawl.dev`.
  Playwright downloads a browser on first use. Claude.ai connectors you add are separate.

## Before you run the self-test

`claude plugin eval` runs plugin code on your machine as you. Read the plugin first, and
confirm the trust prompt only if you trust it.

## Reporting a problem

Use GitHub's private vulnerability reporting: open the **Security** tab of the
[repository](https://github.com/jcallahanp/Autonomy-Research) and choose **Report a
vulnerability**. If that option is not shown, open a GitHub issue that describes the problem
without exploit details or secrets, and ask for a private channel.

Never post a secret in an issue. If you find one committed in this repo, report it the same way.
