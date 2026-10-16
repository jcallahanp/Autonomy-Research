# Cloud sessions

Cloud sessions run at [claude.ai/code](https://claude.ai/code). They use the template path.
Everything below comes from `research/findings/packaging.md` (Q2, Q3, Q6), which cites the
[web quickstart](https://code.claude.com/docs/en/web-quickstart) and the
[cloud environments page](https://code.claude.com/docs/en/cloud-environments).

## Set up

1. **Create your project from the template.** Open the repo on GitHub and choose **Use this
   template**. Name the new repo.
2. **Connect GitHub.** At claude.ai/code, sign in and choose "Sign in with GitHub". Install the
   Claude GitHub App on your account or organization if the repo is private.
3. **Create the default environment, with network access.** Pro and Max accounts get a Default
   environment automatically. Check that its network setting allows the hosts research needs
   (DeepWiki, Firecrawl and the sites you ask about).
4. **Connect the claude.ai connectors.** See [connectors.md](connectors.md). They are
   per account, so one connection covers local and cloud.
5. **Start a session.** Pick the repo, then ask for research or say "set up the research agent".

## What loads in the cloud

- Loaded: the repo's `CLAUDE.md`, `.claude/skills`, `.claude/agents`, `.claude/settings.json`
  hooks, and `.mcp.json` (loaded without a prompt).
- Not loaded: plugins. "A cloud session doesn't install the plugins a repository turns on."
  This is why the template carries the skills through `.claude/skills` and `.claude/agents`,
  which are symlinks to `plugin/skills` and `plugin/agents`.
- Not loaded: your `~/.claude` files.

## What the hooks do

- `scripts/cloud-setup.sh` installs Superpowers (`superpowers@superpowers-marketplace`). It
  exits at once when `CLAUDE_CODE_REMOTE` is not `true`, and when Superpowers is already
  installed.
- The second SessionStart hook in `.claude/settings.json` runs `plugin/hooks/session-start.sh`
  only when `CLAUDE_CODE_REMOTE` is `true`. It injects the skill index and the top of
  `research/findings/INDEX.md`.

## Limits

- **Cloud Playwright has no user logins.** It runs a fresh headless Chromium inside the
  session. Pages behind your sign-in cannot be read. Such claims go under Gaps.
- **Local `claude mcp add` does not reach cloud sessions.** A server you add on your machine
  stays on your machine. Put the server in the repo's `.mcp.json` instead (keyless servers
  only), or use a claude.ai connector.
- **Secrets.** Nothing here needs one. If you add a paid key, use a cloud environment network
  secret (Edit cloud environment > Network secrets > Add secret) so the key does not enter the
  VM. Do not commit it to `.mcp.json`.
- **Re-authorizing a connector** happens at claude.ai/customize/connectors, not in the session.
