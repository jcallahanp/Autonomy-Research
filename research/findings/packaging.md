# Packaging: plugin + template repo for a Claude Code research agent

**Summary.** A Claude Code plugin is a directory with an optional `.claude-plugin/plugin.json`
manifest and component folders (`skills/`, `agents/`, `hooks/hooks.json`, `.mcp.json`) at the
plugin root; a marketplace is any repo with `.claude-plugin/marketplace.json` whose plugin entry may
point at `"./"` (the repo root itself), so one GitHub repo can be the plugin, its own marketplace,
and a clone-and-go template at the same time. The two distribution paths load in different places:
plugins installed from a marketplace load in local terminal/desktop/VS Code sessions (and in GitHub
Actions via the `plugins` input) but **never** in Claude Code cloud sessions, which load only what is
committed in the repo (`CLAUDE.md`, `.claude/settings.json` hooks, `.claude/skills|agents|commands`,
`.claude/rules/`, `.mcp.json`). So the research/ workspace repo must carry its own `.claude/`
copies for cloud use, and the plugin is the way to reuse the same skills in any other repo locally.
The main pitfalls are duplicate hooks (hooks have no namespace, so a hook present in both
`.claude/settings.json` and a plugin's `hooks/hooks.json` runs twice) and secrets (never in
`.mcp.json`; use `${VAR}` expansion locally and claude.ai "network secrets" in the cloud).
CLAUDE.md should stay under ~200 lines of always-true facts, with procedures in skills and
path-scoped guidance in `.claude/rules/`. Setup can be mostly automated with a SessionStart hook
(context injection, dependency install) and a `/setup` skill that checks for tools and connectors,
but three things stay manual: installing the plugin, connecting claude.ai connectors, and creating
secrets. All claims below were verified against pages opened on 2026-10-16.

## Questions and answers

### Q1. Plugin anatomy: manifest, layout, marketplace, install, scopes, versioning, validation

**Confidence: high** (official reference pages opened directly).

- **Manifest.** `.claude-plugin/plugin.json` is optional; without it Claude Code loads the standard
  layout and names the plugin after its marketplace entry or directory. `name` is the only required
  key (kebab-case; names starting `claude-`, `anthropic-`, `cc-plugin-` are refused). Other keys:
  `displayName`, `version`, `description`, `author{name,email,url}`, `homepage`, `repository`,
  `license`, `keywords`, `metadata`, `defaultEnabled`, `dependencies`, `settings`, `userConfig`,
  `skills`, `commands`, `agents`, `hooks`, `mcpServers`, `lspServers`, `outputStyles`, `workflows`,
  `experimental.{themes,monitors,evals}`. Every component path must start with `./` and resolve inside
  the plugin root. `skills` *adds to* the default `skills/` scan; `commands`/`agents` *replace* theirs;
  `hooks`/`mcpServers` *merge* with `hooks/hooks.json` / `.mcp.json`. [plugins-reference]
- **Standard layout** (all at plugin root, not inside `.claude-plugin/`): `skills/<name>/SKILL.md`,
  `commands/*.md` (legacy; "Prefer `skills/` for new plugins"), `agents/*.md`, `hooks/hooks.json`
  (wrapped in a top-level `"hooks"` key), `.mcp.json`, `.lsp.json`, `bin/` (on PATH while enabled,
  but "claude.ai and Cowork don't install a plugin that has this directory"), `settings.json`,
  `scripts/` (convention only). **"A `CLAUDE.md` at the plugin root isn't loaded as context, and
  `claude plugin validate` warns when it finds one. To include instructions that load into Claude's
  context, put them in a skill."** [plugins-reference], [plugins/components]
- **Variables.** `${CLAUDE_PLUGIN_ROOT}` (installed version dir; changes on update), `${CLAUDE_PLUGIN_DATA}`
  (`~/.claude/plugins/data/<id>/`, survives updates), `${CLAUDE_PROJECT_DIR}`. Not exported to Bash-tool
  commands; write them in skill/agent Markdown and Claude Code substitutes inline. [plugins-reference]
- **userConfig.** Declares values Claude Code prompts for when the plugin is enabled; `sensitive: true`
  masks input and stores in the OS credential store. Referenced as `${user_config.KEY}` in MCP config /
  exec-form hook `args`, or as `CLAUDE_PLUGIN_OPTION_<KEY>` env in hook processes. The dialog appears
  only on `/plugin` install, not with `--plugin-dir` or shell install (use `/plugin configure <name>`).
  [plugins-reference], [plugins/create]
- **Marketplace.** `.claude-plugin/marketplace.json` requires `name`, `owner{name}`, `plugins[]`; each
  entry requires `name` and `source`. A relative source is resolved from the marketplace root and
  `"."` / `"./"` "means the root itself", so a single repo can be both marketplace and plugin
  (sokolmarek/researcher and anthropics/skills do exactly this). Keep entry `name` == manifest `name`
  or installs by manifest name fail. Reserved marketplace names include `claude-plugins-official`,
  `claude-community`, `inline`, `skills-dir`, `synced`, `npm`, `github`, `gh`. [marketplace-reference],
  [plugin-marketplaces], [researcher marketplace.json], [skills marketplace.json]
- **Install (terminal).** `/plugin marketplace add owner/repo` (or git URL, local path, hosted JSON), then
  `/plugin install <plugin>@<marketplace>` which opens the details pane to pick a scope. Shell:
  `claude plugin marketplace add owner/repo` + `claude plugin install <plugin>@<marketplace> [--scope project|local]`,
  or one step `claude plugin install <plugin> --marketplace owner/repo` (v2.1.292+). Verify with
  `claude plugin list`, `claude plugin details <name>`, and `/<plugin>:<skill>` in the `/` menu.
  Desktop app: **+ > Plugins > Add plugin**. VS Code: `/plugins`. Cloud sessions: no plugin browser.
  [plugins/install]
- **Scopes.** user → `enabledPlugins` in `~/.claude/settings.json`; project → committed
  `.claude/settings.json` ("doesn't download it to their machines, so each collaborator also runs
  `claude plugin install <name>@<marketplace> --scope project` once"); local → `.claude/settings.local.json`.
  Local > project > user. `extraKnownMarketplaces` in a committed file applies only after the teammate
  trusts the folder. [plugins/install], [settings]
- **Versioning.** Manifest `version` pins users to the cached copy until the string changes; omit it in
  both manifest and entry to let users track commits (version becomes the 12-char commit SHA). Auto-update
  is **off by default** for third-party marketplaces; users enable it under `/plugin` → Marketplaces, or run
  `claude plugin update <plugin>@<marketplace>`. Use `renames` in marketplace.json when renaming. [plugins/loading],
  [plugins/host-marketplace]
- **Validation.** `claude plugin validate <dir>` checks manifest, marketplace.json, skill/agent frontmatter
  and `.mcp.json` entries (v2.1.281+); `--strict` fails on warnings for CI. `claude plugin eval init`
  scaffolds `evals/<case>/{prompt.md,graders/*.md}`; `claude plugin eval .` runs each case 3× with and 3×
  without the plugin and reports `WITH`, `W/OUT`, `Δ` and cost; grader types `regex`, `tool_used`,
  `tool_order`, `file_exists`, `llm`, `baseline`. `/skill-doctor` (v2.1.252+) reports each skill's context
  cost and invocation frequency (Stats tab of `/plugin`; text in `-p`; unavailable over Remote Control).
  `/doctor` is the setup checkup and `/doctor prompt-audit [path]` audits CLAUDE.md/skills for conflicts.
  [plugins-reference], [plugin-evals], [skills], [slash-commands]

### Q2. Plugin vs template vs project `.claude/`: what loads where, and can one repo be both?

**Confidence: high** for the load matrix (quoted from the cloud-environments table); **medium** for
the "both" recommendation (derived from several pages, no single page describes it).

What each surface loads (✓ = loads, ✗ = does not):

| Source | Local terminal / desktop / VS Code | Cloud session (claude.ai/code, `--cloud`, routines) | GitHub Actions (`claude-code-action`) |
|---|---|---|---|
| Repo `CLAUDE.md`, `.claude/rules/` | ✓ | ✓ ("Part of the clone") | ✓ (`CLAUDE.md` read on every run) |
| Repo `.claude/skills|agents|commands` | ✓ | ✓ | ✓ for skills via `actions/checkout` then `/skill-name` prompt |
| Repo `.claude/settings.json` hooks + permissions | ✓ after folder trust | ✓ "in a session with one repository" | `settings` input (JSON or path) |
| Repo `.mcp.json` | ✓ with per-server approval prompt | ✓ loads "without asking" (no prompt possible) | `--mcp-config` in `claude_args` |
| Plugins in repo `.claude/settings.json` `enabledPlugins` | ✓ if each collaborator installs | ✗ "A cloud session doesn't install the plugins a repository turns on" | via `plugin_marketplaces` + `plugins` inputs |
| Plugins in `~/.claude/settings.json` | ✓ | ✗ | n/a |
| `~/.claude/CLAUDE.md`, `~/.claude/skills` | ✓ | ✗ (write `~/.claude/CLAUDE.md` from a setup script instead) | ✗ |
| claude.ai connectors / claude.ai-enabled skills | ✓ when signed in with claude.ai | ✓ (connector traffic via Anthropic's servers) | ✗ (API key auth) |
| Secrets | shell env → `${VAR}` | environment variables (readable) or **network secrets** (never enter VM) | GitHub Secrets |

Sources: [cloud-environments] "What carries over", [settings] "Settings in cloud sessions",
[plugins/install] Cloud tab, [claude-code-on-the-web] ("Subagents defined in your repo's
`.claude/agents/` are picked up automatically"), [github-actions], [mcp].

- **Plain-English version for a non-expert.** A *plugin* is like an app you install once on your
  computer: after `claude plugin install`, its skills show up as `/research:<skill>` in every project you
  open on that machine, and it updates from the author's repo. A *template repo* is a folder of starter
  files you copy once (GitHub "Use this template") to become *your* project; it already contains the
  `.claude/` setup, a `research/` folder for findings, and a `CLAUDE.md`. The template works in the cloud
  (claude.ai/code) because everything is inside the repo; the plugin does **not** work in the cloud, but it
  lets you use the same research skills on any other repo locally. You want both: the template so a
  stranger can clone and start a cloud or local session with zero install, and the plugin so the same
  person can bring the skills to projects that aren't copies of the template.
- **Can one repo be both?** Yes. The plugin lives at the repo root (`.claude-plugin/plugin.json`,
  `skills/`, `agents/`, `hooks/`), marketplace.json points its single entry at `"./"`, and the template
  behaviour comes from a committed `.claude/` directory plus `research/`. GitHub's template setting
  ("Settings → Template repository") copies "the same directory structure and files as your default
  branch" into a new repo with unrelated history; LFS files are not allowed. [github-template-repo]
- **Pitfalls when a repo is installed as a plugin *and* opened as a project.**
  1. *Hooks run twice.* "hooks have no prefix, so a hook that is in both your settings file and
     `hooks/hooks.json` runs twice each time its event fires." Skills and agents do not collide because
     plugin ones are namespaced (`/deploy` and `/my-plugin:deploy` both work). [plugins/create]
  2. *Skills-dir plugin shadowing.* A plugin folder placed under `.claude/skills/<name>/` with its own
     `.claude-plugin/plugin.json` loads as `<name>@skills-dir`, but if a marketplace plugin with the same
     manifest name is installed, the skills-dir copy is "Not loaded" and the installed one wins. Only the
     primary working directory's `.claude/skills/` is scanned for plugins (no parent walk), and a
     project-scope plugin's MCP servers go through the same per-server approval as `.mcp.json`. [plugins/loading]
  3. *Context cost.* Every model-invocable skill's description sits in context on every turn in every
     project where the plugin is enabled; `claude plugin details <name>` shows the "Always-on" tokens.
     [plugins], [plugins/install]
  4. *Project-scope install is not automatic.* Committing `enabledPlugins` only turns the plugin on; each
     clone shows `Plugin "<name>" is enabled in project settings but isn't installed here` until the user
     installs it. A marketplace entry with a *relative-path* source is the exception ("needs no install
     record because it loads from the marketplace itself"). [plugins/loading]
  5. *Cloud ignores `extraKnownMarketplaces`* "because that requires the workspace trust dialog, which a
     cloud session never shows." [plugins/loading]
- **Recommendation.** Keep *one source of truth* for skill text at the plugin root and make the
  template's `.claude/` thin: `.claude/settings.json` (hooks, permissions), `.claude/rules/`, and either
  symlinks or a sync script that copies `skills/` → `.claude/skills/` for cloud use. Do **not** also set
  `enabledPlugins` for this plugin in the template's `.claude/settings.json`, or local users who installed
  the plugin get duplicate hooks. See layout under Implications.

### Q3. MCP servers, approval, secrets, and detecting a missing connector

**Confidence: high** for approval/expansion/connector facts; **medium** for the detection pattern
(no doc describes a built-in "connector missing" check; the pattern is assembled from hook and tool facts).

- **Approval.** "Claude Code prompts for approval in interactive sessions before using project-scoped
  servers from `.mcp.json`"; reset with `claude mcp reset-project-choices`. In `claude -p`, SDK and cloud
  sessions "it loads project-scoped servers without asking". `enableAllProjectMcpServers` /
  `enabledMcpjsonServers` committed to `.claude/settings.json` are **ignored in an untrusted folder**
  ("A cloned repository can't approve its own servers"); `disabledMcpjsonServers` always rejects. [mcp]
- **Plugins can ship MCP servers** in `.mcp.json` at the plugin root or inline under `mcpServers`;
  servers start when the plugin is enabled, appear in `/mcp` as `plugin:<plugin>:<server>`, and tools are
  named `mcp__plugin_<plugin-name>_<server-name>__<tool-name>`. Precedence: local > project > user >
  plugin-provided > claude.ai connectors; "A server you've added in Claude Code takes precedence over a
  claude.ai connector that points at the same URL." [mcp], [plugins/components]
- **Env vars / secrets.** `.mcp.json` supports `${VAR}` and `${VAR:-default}` in `command`, `args`,
  `env`, `url`, `headers`. Unset without default leaves the literal `${VAR}` and `claude mcp list` warns.
  `ANTHROPIC_API_KEY`-style credential names are read as empty in remote `url`/`headers`. For a plugin,
  prefer `userConfig` with `sensitive: true` (credential store) over asking users to export variables. In
  cloud, environment variables are readable by anyone using the environment; use **network secrets**
  (Edit cloud environment → Network secrets → Add secret → host + Bearer value) so "the key itself stays
  outside the VM"; GitHub is proxied separately and never needs a secret. [mcp], [plugins-reference],
  [cloud-environments]
- **Connectors vs repo MCP.** Connectors are MCP servers you add on claude.ai; they "are automatically
  available in Claude Code" when "your active authentication method is a claude.ai subscription login"
  (not API key). In cloud sessions, connector traffic "travels through Anthropic's servers rather than the
  session's network", bypasses the domain allowlist, and re-auth happens at claude.ai/customize/connectors,
  not in-session. `disableClaudeAiConnectors: true` or `deniedMcpServers` blocks them. A repo `.mcp.json`
  server runs from the session VM (local stdio or HTTP) and *does* need the host on the allowlist. [mcp],
  [cloud-environments]
- **Detecting a missing connector.** Nothing in the docs lets a hook enumerate connected servers, but
  three facts combine into a workable pattern: (1) `SessionStart` supports `type: "mcp_tool"` hooks, and a
  hook that targets an absent server fails rather than runs, so a cheap probe can turn absence into a
  visible error; (2) a skill body can tell Claude to check for the tool names a connector provides (Exa
  tools appear as `mcp__Exa__web_search_exa`, Context7 as `mcp__Context7__*`) and, if absent, print the
  connect steps; (3) `/mcp` lists every server with `✔ Connected`, `! Needs authentication`, or
  `✘ Failed to connect`. The recommended design is a `/research:setup` skill whose instructions say
  "if `mcp__Exa__*` is not available, tell the user: open claude.ai → Customize → Connectors → + → search
  Exa → Connect; on Team/Enterprise an Owner must first add it under Organization settings → Connectors".
  [hooks], [mcp], [support: use-connectors], [support: custom-connectors]
- **Exact connector UI steps (for the manual-steps section):** "Navigate to Customize > Connectors. Click
  the '+' button next to Connectors. Browse available connectors… Click 'Connect' or 'Install'… Follow the
  authentication prompts." Per-conversation enable: "'+' button on the lower left of your chat interface,
  then 'Connectors'… toggles". Team/Enterprise: Owners add under "Organization settings > Connectors",
  then members "Navigate to Customize > Connectors… Click 'Connect'". [support: use-connectors],
  [support: custom-connectors]

### Q4. CLAUDE.md best practices and what goes where

**Confidence: high** (official memory page, official best-practices page, HumanLayer post all opened).

- **Size and content.** Official: "target under 200 lines per CLAUDE.md file. Longer files consume more
  context and reduce adherence." "Keep it to facts Claude should hold in every session: build commands,
  conventions, project layout, 'always do X' rules. If an entry is a multi-step procedure or only matters
  for one part of the codebase, move it to a skill or a path-scoped rule." Imports "don't reduce its context
  cost, because imported files also load at launch." [memory] Best-practices test: "For each line, ask:
  'Would removing this cause Claude to make mistakes?' If not, cut it." Include: commands Claude can't
  guess, style rules that differ from defaults, test runners, repo etiquette, architectural decisions,
  env quirks, gotchas. Exclude: anything derivable from code, standard conventions, API docs (link
  instead), frequently changing info, tutorials, file-by-file descriptions. Add "IMPORTANT" to at most one
  or two skipped lines; run `/context` to confirm it loaded; `/doctor` proposes cuts. [best-practices]
- **HumanLayer.** "your `CLAUDE.md` file should contain as few instructions as possible" (models follow
  ~150–200 instructions; Claude Code's own system prompt already uses ~50); author's root file is under
  sixty lines; use *progressive disclosure*: list topic docs (e.g. `agent_docs/running_tests.md`) with
  one-line descriptions and tell Claude when to read them; "Never send an LLM to do a linter's job"; avoid
  code snippets (go stale) and avoid relying on `/init` auto-generation. [humanlayer]
- **Hierarchy and mechanics.** Load order: managed → `~/.claude/CLAUDE.md` → every `CLAUDE.md` from
  filesystem root down to cwd (concatenated, closer files last) → `CLAUDE.local.md` appended per directory
  (gitignored; personal). Subdirectory `CLAUDE.md` files load on demand when Claude touches a file there.
  `@path` imports anywhere in the file; backticks keep a path literal. `.claude/rules/*.md` are discovered
  recursively; a `paths:` frontmatter glob makes a rule load only when matching files are touched;
  symlinked rules need one approval per project. `AGENTS.md` is read when no CLAUDE.md exists, or via
  `@AGENTS.md` import. [memory]
- **Decision table (official).** CLAUDE.md = every session, whole project, "core conventions and build
  commands". `.claude/rules/` = every session or when matching files open, "language-specific or
  directory-specific guidelines". Skill = on demand, "reference material, repeatable workflows". Hooks
  for anything that must happen every time ("An instruction like 'never edit `.env`' in CLAUDE.md … is a
  request, not a guarantee"). Trigger-based growth: wrong twice → CLAUDE.md; same prompt repeated →
  user-invocable skill; same playbook pasted thrice → skill; second repo needs it → plugin.
  [features-overview]
- **README vs CLAUDE.md.** README is for humans (install, what it is); CLAUDE.md is for Claude and is
  "treated as context, not enforced configuration." Several studied plugins keep a root `CLAUDE.md` as
  contributor notes and label it "not loaded at plugin runtime" (sokolmarek/researcher), which is correct
  because plugin-root CLAUDE.md never loads. [memory], [plugins-reference], [researcher README]

### Q5. Well-regarded plugin repos: layout, docs, onboarding, hooks, setup tricks

**Confidence: high** where raw files were opened (superpowers hooks/plugin.json/session-start,
anthropics/skills marketplace.json, researcher README/marketplace/hooks, research-superpowers
README/hooks/installation.md); **medium** where only the DeepWiki AI summary was available
(anthropics/claude-code plugins dir, ECC, mattpocock/skills).

| Repo | Layout | Docs & onboarding | Hooks | Clever setup |
|---|---|---|---|---|
| **obra/superpowers** | `.claude-plugin/plugin.json` (v7.0.0, no component keys; standard dirs), `skills/` as single source of truth, `hooks/`, `docs/`, `RELEASE-NOTES.md` | README with per-harness install (`claude plugin marketplace add obra/superpowers-marketplace`, `claude plugin install superpowers@superpowers-marketplace`), separate marketplace repo | `SessionStart` matcher `startup\|clear\|compact` runs `hooks/run-hook.cmd session-start` (polyglot .cmd/bash dispatcher) | `hooks/session-start` reads `skills/using-superpowers/SKILL.md` and emits `hookSpecificOutput.additionalContext` wrapped in `<EXTREMELY_IMPORTANT>`; emits different JSON shapes per harness; avoids `dirname`/`cat` because PATH may be empty at startup; `scripts/bump-version.sh` syncs versions |
| **anthropics/claude-code** `plugins/` | Each plugin: `.claude-plugin/plugin.json`, `commands/`, `agents/`, `skills/`, `hooks/`, `.mcp.json`, `README.md`; repo-root `.claude-plugin/marketplace.json` | Per-plugin README (usage, commands, agents); `plugin-dev` offers `/plugin-dev:create-plugin` 8-phase guided build | `explanatory-output-style` uses SessionStart script emitting `additionalContext` | Official layout examples the docs point to (`feature-dev`, `code-review`) |
| **anthropics/skills** | `skills/<name>/{SKILL.md,scripts/,references/,assets/}`, `template/SKILL.md`, root `.claude-plugin/marketplace.json` | README: `/plugin marketplace add anthropics/skills`, then install `document-skills` etc. | none | Marketplace entries use `"source": "./"`, `"strict": false` and a `skills: [...]` list, so one repo exposes several plugins without separate manifests |
| **affaan-m/ECC** (via DeepWiki) | `.claude-plugin/{plugin.json,marketplace.json}` in same repo, `agents/`, `skills/`, `commands/`, `rules/`, `hooks/hooks.json`, `contexts/` | README: `/plugin marketplace add https://github.com/affaan-m/ECC` then `/plugin install ecc@ecc`; manual `install.sh` alternative copies `rules/` to `~/.claude/rules/ecc/` | PreToolUse, PostToolUse, Stop, SessionStart, SessionEnd, PreCompact | `node scripts/ecc.js doctor` / `repair`; `/setup-pm` command; `PLUGIN_SCHEMA_NOTES.md` documents manifest rules |
| **mattpocock/skills** (via DeepWiki) | `skills/{engineering,productivity,misc,in-progress,deprecated}/`, `.claude-plugin/plugin.json` listing promoted skill paths, `.claude-plugin/marketplace.json` as fallback single-plugin marketplace, `docs/`, `CLAUDE.md` for contributors | README install block generated from `.agents/install-block.md`; primary install `claude plugin install mattpocock-skills@claude-plugins-official`; `npx skills@latest add` for other agents (mutually exclusive to avoid duplicates) | none | `claude plugin validate . --strict` required after manifest edits; `scripts/sync-plugin-version.mjs` ties plugin version to `package.json`; post-install `/setup-matt-pocock-skills` skill asks about trackers/labels/docs layout |
| **sokolmarek/researcher** | `.claude-plugin/` (plugin + marketplace, entry `"source": "./"`), `skills/` (35), `agents/` (9), `commands/` (15), `core/` Python kernel, `connectors/` docs, `hooks/`, `references/`, `templates/`, `evals/`, `docs/` site, `CLAUDE.md` "(not loaded at plugin runtime)", `CONTRIBUTING.md`, `SECURITY.md` | README capability table with "Works today / not implemented" honesty; `/plugin install researcher@researcher-marketplace`; licensed sources (Scite, Zotero) "attach as MCP servers you connect yourself" | `PreToolUse` Bash → `python "${CLAUDE_PLUGIN_ROOT}/scripts/citation-check-hook.py"` (timeout 20); `PostToolUse` Write\|Edit → draft-integrity hook | Optional deterministic kernel degrades gracefully if `uv` missing; `evals/BENCHMARKS.md`; signed releases |
| **leiverkus/research-superpowers** | `.claude-plugin/plugin.json`, `skills/` (17), `agents/` (7), `hooks/`, `schema/`, **`templates/research-project-template/`** (with `CLAUDE.md` frontmatter `methodology/discipline/languages`, `schema/`, `scripts/lint-wiki.py`, `.vscode/settings.json`), `examples/`, `docs/`, `CHANGELOG.md`, `CONTRIBUTING.md` | `docs/installation.md` (5–10 min, prerequisites, three install paths, verify, troubleshoot, uninstall, "what landed on disk"); `docs/installation-cowork.md` click-only path; `docs/recommended-mcps.md` (optional MCPs, "plugin works without them") | `SessionStart` `startup\|clear\|compact` → `run-hook.cmd session-start` (injects skill index); `startup` → `drift-check` (state-triggered, silent when nothing changed) | Plugin-installed-once + per-project template copied from `~/.claude/plugins/cache/<marketplace>/<plugin>/templates/…`; README says "you'll see a 'Research Superpowers' notice at session start" as the install verification signal |

Common patterns worth copying: a SessionStart hook that injects a short index of skills (not the
full text) and tells the user how to verify install; `"source": "./"` single-repo marketplace; a
root `CLAUDE.md` labelled as contributor notes; `docs/installation.md` written for a stranger with a
verification step and an uninstall step; honest capability tables; optional MCPs documented separately;
a version-sync script and `claude plugin validate --strict` in CI.

### Q6. Setup automation: what a plugin can do on first run, and what stays manual

**Confidence: high** for hook capabilities (hooks reference); **medium** for the overall flow design.

What can be automated:
- **SessionStart hook** (`startup|resume|clear|compact` matchers; only `command` and `mcp_tool`
  types). Plain stdout or `hookSpecificOutput.additionalContext` is injected "at the start of the
  conversation, before the first prompt"; `reloadSkills: true` re-scans skill dirs so skills a hook
  installs are usable in the same session; `CLAUDE_ENV_FILE` persists env vars for later Bash calls;
  exit 2 at SessionStart only shows stderr to the user (cannot block). Hooks run in cloud too; gate
  cloud-only work on `CLAUDE_CODE_REMOTE == "true"`; default timeout 600 s. Use the documented
  hash-check pattern (`sha256sum --check`) so installs are idempotent and fast. [hooks], [hooks-guide],
  [cloud-environments]
- **UserPromptSubmit hook** can inject `hookSpecificOutput.additionalContext` on every prompt (e.g. a
  one-line "setup incomplete: run /research:setup" banner until a marker file exists); default timeout 30 s.
  [hooks-guide]
- **A `/research:setup` (or `/doctor`-style) skill** with `disable-model-invocation: true` and
  `` !`command` `` dynamic context (e.g. `` !`claude mcp list 2>/dev/null || true` ``, `` !`gh auth status || true` ``,
  `` !`test -f .mcp.json && echo present` ``) can check tools, report connector availability via tool
  names, and walk the user through missing pieces; `allowed-tools` pre-approves the probes. Failed
  dynamic commands abort the skill, so append `|| true`. [skills]
- **Cloud setup script** (environment dialog) provisions toolchains and is cached for ~7 days if it
  finishes in ~5 minutes; it can write `~/.claude/CLAUDE.md` for personal preferences. [cloud-environments]
- **Plugin `userConfig`** prompts for API keys at install (`sensitive: true`) so users never edit JSON.
  [plugins-reference]
- **GitHub Actions** installs the plugin unattended via `plugin_marketplaces` + `plugins` inputs. [github-actions]

What the user must do by hand (exact current UI steps):
1. **Install the plugin (local).** In a terminal: `claude`, then `/plugin marketplace add <owner>/<repo>`,
   then `/plugin install <plugin>@<marketplace-name>` → choose "Install for you (user scope)" → read the
   summary line ("Plugin is now active." or "Run /reload-plugins to apply."). Shell equivalent:
   `claude plugin install <plugin> --marketplace <owner>/<repo>`. Verify: type `/` and look for
   `/<plugin>:<skill>`; or `claude plugin list`. Optional: `/plugin` → Marketplaces → select → "Enable
   auto-update". [plugins/install]
2. **Create the project from the template.** On GitHub: open the template repo → **Use this template**
   (available because the owner ticked Settings → "Template repository") → name the new repo. Or `git clone`.
   [github-template-repo]
3. **Start a cloud session.** claude.ai/code → sign in → "Sign in with GitHub" → install the Claude GitHub
   App on the account/org for private repos → create the **Default** environment (Pro/Max auto-created) →
   pick repository and permission mode → type the task. [web-quickstart]
4. **Connect connectors (Exa, Context7, Parallel, Mermaid Chart).** claude.ai → **Customize → Connectors →
   "+"** → find the connector → **Connect/Install** → complete auth. Per conversation: "+" button → Connectors
   → toggle. Team/Enterprise: an Owner first adds it under **Organization settings → Connectors**. If a cloud
   session reports a connector needs authorizing again, reconnect at claude.ai/customize/connectors.
   [support: use-connectors], [support: custom-connectors], [mcp]
5. **Create secrets.** Local: export the variable in your shell (or answer the plugin's `userConfig`
   prompt). Cloud: claude.ai/code → environment selector → settings icon → **Edit cloud environment →
   Network secrets → Add secret** → Secret type Bearer, Name, hosts, value → **Add** (cannot be edited later;
   delete and re-add). GitHub Actions: repo **Settings → Secrets** → `ANTHROPIC_API_KEY` or
   `CLAUDE_CODE_OAUTH_TOKEN` (`claude setup-token`). [cloud-environments], [github-actions]
6. **Approve `.mcp.json` servers (local only).** Accept the per-server prompt on first run in a trusted
   folder; cloud and `-p` load them without asking. [mcp]

## Evidence

All opened 2026-10-16.

- [plugins-reference] https://code.claude.com/docs/en/plugins-reference — WebFetch — manifest fields,
  path rules, `userConfig`, `${CLAUDE_PLUGIN_ROOT}`/`DATA`, standard layout, `bin/` not installed on
  claude.ai/Cowork, "CLAUDE.md at the plugin root isn't loaded", `claude plugin validate` results and
  `.mcp.json` checks (v2.1.281+), marketplace entry/manifest precedence.
- [plugins] https://code.claude.com/docs/en/plugins — WebFetch — what a plugin is, context cost of
  always-on descriptions, scopes, "A cloud session… doesn't load the plugins in your local settings",
  official vs community vs third-party marketplaces.
- [plugin-marketplaces] https://code.claude.com/docs/en/plugin-marketplaces — WebFetch — create
  marketplace walkthrough, `claude plugin marketplace add ./my-marketplace`, install id `name@marketplace`,
  entry-name == manifest-name rule, source types.
- [marketplace-reference] https://code.claude.com/docs/en/plugins/marketplace-reference — WebFetch —
  required fields, `"."` means root, reserved names, `strict`, `renames`, `metadata.pluginRoot`,
  validation messages.
- [plugins/install] https://code.claude.com/docs/en/plugins/install — WebFetch — terminal/desktop/VS
  Code/cloud install steps, scopes and files, "each collaborator also runs `claude plugin install … --scope project`",
  `--marketplace` one-step install, auto-update defaults, claude.ai synced plugins.
- [plugins/create] https://code.claude.com/docs/en/plugins/create — WebFetch — first plugin, `--plugin-dir`,
  `claude plugin init`, `.claude/skills/<name>/.claude-plugin/plugin.json` repo-shared plugins, convert
  `.claude/` → plugin, "a hook that is in both… runs twice", `userConfig` dialog only via `/plugin`.
- [plugins/loading] https://code.claude.com/docs/en/plugins/loading — WebFetch — `enabledPlugins` stages,
  `@skills-dir`/`@inline`/`@synced` ids, "Enabled in project settings but not installed", cloud ignores
  `extraKnownMarketplaces`, versions from manifest > entry > SHA, name-conflict order, on-disk layout
  `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/`.
- [plugins/components] https://code.claude.com/docs/en/plugins/components — WebFetch — skills namespacing
  `/<plugin>:<dir>`, single root SKILL.md, hooks.json shape, `.mcp.json` in plugin appearing as
  `plugin:my-plugin:db`, `bin/`, `${user_config}` in env.
- [plugins/host-marketplace] https://code.claude.com/docs/en/plugins/host-marketplace — WebFetch —
  hosting table, "Register the marketplace for everyone in a repository" (`--scope project`), release a new
  version (bump or omit `version`), auto-update off by default, `renames`, `forceRemoveDeletedPlugins`.
- [plugin-evals] https://code.claude.com/docs/en/plugin-evals — WebFetch — `claude plugin eval init`,
  `evals/<case>/prompt.md` + `graders/`, 3 runs, WITH/W/OUT/Δ, grader types, `--threshold`, difference
  from `claude plugin validate`.
- [skills] https://code.claude.com/docs/en/skills — WebFetch — frontmatter fields, locations table,
  commands merged into skills, `$ARGUMENTS`, `` !`command` `` rules (`|| true`), "Keep SKILL.md under 500
  lines", 1,536-char description budget, `/skill-doctor`, cloud sessions don't read `~/.claude/skills/`.
- [sub-agents] https://code.claude.com/docs/en/sub-agents — WebFetch — locations and priority, frontmatter
  (`skills`, `memory`, `isolation`, `omitClaudeMd`), plugin agents ignore `hooks`/`mcpServers`/`permissionMode`.
- [hooks] https://code.claude.com/docs/en/hooks — WebFetch — events and matchers, hook types, config
  locations incl. plugin `hooks/hooks.json` and skill frontmatter, SessionStart input/output (`additionalContext`,
  `reloadSkills`, `CLAUDE_ENV_FILE`), exit codes, `CLAUDE_CODE_REMOTE`.
- [hooks-guide] https://code.claude.com/docs/en/hooks-guide — WebFetch — SessionStart compact re-injection,
  `direnv export bash > "$CLAUDE_ENV_FILE"`, UserPromptSubmit `hookSpecificOutput.additionalContext`,
  timeouts (30 s for UserPromptSubmit).
- [mcp] https://code.claude.com/docs/en/mcp — WebFetch (two reads, offset 0 and 100000) — `.mcp.json`
  approval, non-interactive loads without asking, `enableAllProjectMcpServers` ignored in untrusted folder,
  `${VAR}`/`${VAR:-default}` expansion fields, credential vars read as empty, scopes/precedence incl.
  plugin and connectors, `claude mcp add` forms, plugin server tool naming, connectors auto-available with
  claude.ai login, `disableClaudeAiConnectors`, cloud connector re-auth at claude.ai/customize/connectors,
  tool search and `alwaysLoad`.
- [memory] https://code.claude.com/docs/en/memory — WebFetch — "target under 200 lines", when to add,
  locations table, `/init` and `CLAUDE_CODE_NEW_INIT`, `@path` imports, `CLAUDE.local.md`, load order,
  `.claude/rules/` with `paths:`, symlinked rules approval, `/doctor prompt-audit`, AGENTS.md rules, auto memory.
- [settings] https://code.claude.com/docs/en/settings — WebFetch — precedence (managed > CLI > local >
  project > user), what each file reaches, "Settings in cloud sessions" (one-repo reads `.claude/settings.json`;
  multi-repo reads only `enabledPlugins`/`extraKnownMarketplaces`), keys that wait for trust.
- [cloud-environments] https://code.claude.com/docs/en/cloud-environments — WebFetch — "What carries over
  from your setup" table, network secrets steps, setup scripts vs SessionStart hooks, `install_pkgs.sh`
  example with `CLAUDE_CODE_REMOTE`, 600 s hook timeout, connector traffic bypasses allowlist, writing
  `~/.claude/CLAUDE.md` from a setup script.
- [claude-code-on-the-web] https://code.claude.com/docs/en/claude-code-on-the-web — WebFetch — GitHub
  auth options, `/plugin` not available in cloud, `.claude/agents/` picked up automatically, security
  and isolation.
- [web-quickstart] https://code.claude.com/docs/en/web-quickstart — WebFetch — connect GitHub steps,
  Default environment, start a task, `/web-setup`, Owner must enable GitHub connector on Team/Enterprise.
- [slash-commands] https://code.claude.com/docs/en/slash-commands — WebFetch — `/doctor`, `/doctor prompt-audit`,
  `/skill-doctor` (v2.1.252+), `/reload-plugins`, `/reload-skills`, commands merged into skills.
- [github-actions] https://code.claude.com/docs/en/github-actions — WebFetch — `plugin_marketplaces` and
  `plugins` inputs, `/skill-name` prompt after `actions/checkout`, `settings` input, secrets, CLAUDE.md.
- [features-overview] https://code.claude.com/docs/en/features-overview — WebFetch — "Match features to
  your goal" table, "Build your setup over time" triggers, CLAUDE.md vs Rules vs Skills tab, "Keep
  CLAUDE.md under 200 lines", hooks as enforcement.
- [best-practices] https://code.claude.com/docs/en/best-practices (redirect target of
  anthropic.com/engineering/claude-code-best-practices) — WebFetch — CLAUDE.md include/exclude table,
  "Would removing this cause Claude to make mistakes?", emphasis guidance, `/context`, `/doctor`, skills
  and subagents examples, "The over-specified CLAUDE.md" failure pattern.
- [humanlayer] https://www.humanlayer.dev/blog/writing-a-good-claude-md — WebFetch — "as few instructions
  as possible", 150–200 instruction budget, <60-line root file, progressive disclosure via `agent_docs/`,
  "Never send an LLM to do a linter's job", avoid `/init` auto-generation.
- [github-template-repo] https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-template-repository
  — WebFetch — Settings → "Template repository"; new repo gets default-branch files; unrelated histories;
  optional include all branches; no Git LFS.
- [support: use-connectors] https://support.claude.com/en/articles/11176164-use-connectors-to-extend-claude-s-capabilities
  — mcp__Exa__web_search_exa (full-text highlights) — "Navigate to Customize > Connectors. Click the '+'
  button…", Connect/Install flow, custom connector steps.
- [support: custom-connectors] https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp
  — mcp__Exa__web_search_exa — Owners add under "Organization settings > Connectors"; members Connect;
  per-conversation "+" → Connectors toggles.
- [superpowers hooks.json / plugin.json / session-start] https://raw.githubusercontent.com/obra/superpowers/main/hooks/hooks.json ,
  …/.claude-plugin/plugin.json , …/hooks/session-start — mcp__Exa__web_fetch_exa — SessionStart matcher
  and `run-hook.cmd`, version 7.0.0 manifest, context-injection script details.
- [superpowers wiki] https://deepwiki.com (obra/superpowers) — mcp__deepwiki__read_wiki_structure +
  ask_wiki_question — layout, marketplace install commands, RELEASE-NOTES.md, bump-version.sh, multi-harness.
- [claude-code wiki] https://deepwiki.com (anthropics/claude-code) — mcp__deepwiki__ask_wiki_question —
  plugins/ layout, README per plugin, plugin-dev, output-style SessionStart hooks.
- [skills marketplace.json] https://raw.githubusercontent.com/anthropics/skills/main/.claude-plugin/marketplace.json
  — mcp__Exa__web_fetch_exa — `"source": "./"`, `"strict": false`, `skills` arrays; plus DeepWiki
  ask_wiki_question for skill folder conventions and README install commands.
- [ECC wiki] https://deepwiki.com (affaan-m/ECC) — mcp__deepwiki__ask_wiki_question — layout, install
  commands, `rules/`, hooks, `ecc.js doctor/repair`, `PLUGIN_SCHEMA_NOTES.md`.
- [mattpocock wiki] https://deepwiki.com (mattpocock/skills) — mcp__deepwiki__ask_wiki_question —
  bucketed skills, plugin.json + fallback marketplace.json, `claude plugin validate . --strict`,
  version-sync script, `/setup-matt-pocock-skills`.
- [researcher README / marketplace.json / hooks.json] https://raw.githubusercontent.com/sokolmarek/researcher/main/README.md ,
  …/.claude-plugin/marketplace.json , …/hooks/hooks.json — mcp__Exa__web_fetch_exa — project structure
  with `CLAUDE.md # Contributor notes (not loaded at plugin runtime)`, `"source": "./"`, PreToolUse/PostToolUse
  python hooks with `${CLAUDE_PLUGIN_ROOT}`, capability table, user-connected MCPs.
- [research-superpowers README / hooks.json / docs/installation.md]
  https://raw.githubusercontent.com/leiverkus/research-superpowers/main/README.md , …/hooks/hooks.json ,
  …/docs/installation.md — mcp__Exa__web_fetch_exa — plugin + `templates/research-project-template`,
  SessionStart `session-start` and `drift-check`, installation guide structure, Cowork path, recommended MCPs.
- [exa search: research plugins] mcp__Exa__web_search_exa and mcp__github__search_repositories — used only
  to discover candidate repos (Defiect/deep-research-plugin, tomkd555/research-skill, zdenekmach/deep-research,
  TheMizeGuy/deep-research-public, jasonm4130/claude-skills); their highlights confirm the common
  `.claude-plugin/` + `skills/` + `agents/` layout but were not opened in full, so they are not cited above.

## Implications for the researcher plugin

**Recommended repo layout** (one repo = plugin root = its own marketplace = GitHub template):

```
research-agent/                      # GitHub "Template repository" ON
├── .claude-plugin/
│   ├── plugin.json                  # name "research-agent", version, author, userConfig (sensitive keys)
│   └── marketplace.json             # name "research-agent-marketplace", plugins[0].source "./"
├── skills/                          # single source of truth for all skill text
│   ├── using-research-agent/SKILL.md   # short index injected by SessionStart (superpowers pattern)
│   ├── setup/SKILL.md               # /research-agent:setup — disable-model-invocation, probes tools/connectors
│   ├── research-topic/SKILL.md      # the research workflow; cites research/_FORMAT.md
│   ├── log-tool/SKILL.md            # appends to research/tool-registry.md
│   └── diagram/SKILL.md             # one-concern Mermaid files + index
├── agents/                          # researcher.md, verifier.md (plugin agents: no hooks/mcpServers keys)
├── hooks/
│   ├── hooks.json                   # SessionStart startup|clear|compact → scripts/session-start.sh
│   └── scripts/session-start.sh     # emits additionalContext: skill index + setup status (idempotent, no cat/dirname)
├── .mcp.json                        # deepwiki (http), playwright (stdio) — no secrets; ${VAR} only
├── evals/                           # claude plugin eval cases
├── .claude/                         # TEMPLATE side (what cloud sessions load)
│   ├── settings.json                # permissions.allow, SessionStart hook for cloud deps (CLAUDE_CODE_REMOTE guard); NO enabledPlugins for this plugin
│   ├── rules/                       # research-format.md (paths: research/**), diagrams.md (paths: **/*.mmd)
│   ├── skills/ -> ../skills         # symlink or sync script so cloud sessions get the skills
│   └── agents/ -> ../agents
├── research/
│   ├── findings/_FORMAT.md
│   ├── tool-registry.md
│   ├── open-questions.md
│   └── diagrams/index.md
├── scripts/
│   ├── cloud-setup.sh               # SessionStart target; sha256-gated installs
│   ├── sync-skills.sh               # copies skills/ → .claude/skills/ for Windows clones (no symlinks)
│   └── bump-version.sh              # keeps plugin.json + marketplace.json versions equal
├── docs/
│   ├── installation.md              # stranger-proof: prerequisites, 3 paths, verify, troubleshoot, uninstall
│   ├── connectors.md                # exact claude.ai steps for Exa/Context7/Parallel/Mermaid Chart
│   └── plugin-vs-template.md        # the plain-English explanation
├── CLAUDE.md                        # ≤ 60 lines: what/why/how, pointers; loads only when repo is opened as a project
├── CLAUDE.local.md.example          # personal overrides pattern (gitignored real file)
├── README.md, CHANGELOG.md, CONTRIBUTING.md, SECURITY.md, LICENSE
└── .github/workflows/validate.yml   # claude plugin validate . --strict (+ optional plugin eval)
```

Design consequences:
1. Skill text lives once under `skills/`; the template's `.claude/skills` is a symlink (Git stores it;
   Windows clones need `scripts/sync-skills.sh`). Cloud sessions load `.claude/skills` from the clone;
   local users who installed the plugin get the namespaced `/research-agent:*` copies. Both present
   locally is harmless for skills/agents (namespaced) but **hooks must live in exactly one place per
   surface**: plugin `hooks/hooks.json` for installed users, `.claude/settings.json` for cloud. Guard the
   template hook with `CLAUDE_CODE_REMOTE == "true"` so local users with the plugin don't double-fire.
2. Never set `enabledPlugins["research-agent@…"]` in the template's `.claude/settings.json`: cloud ignores
   it and local clones would show "enabled in project settings but isn't installed".
3. `.mcp.json` carries only keyless servers (DeepWiki, Playwright). Exa/Context7/Parallel/Mermaid Chart
   stay claude.ai connectors; `/research-agent:setup` detects their tool names and prints the connect steps.
   Any paid API key goes in `userConfig` (`sensitive: true`) locally and a network secret in the cloud.
4. CLAUDE.md: ≤ 60 lines; sections WHAT (repo map), WHY (research the researcher), HOW (how to cite, where
   findings go, EARS requirements), and a pointer list to `research/findings/_FORMAT.md`, `docs/`. Put the
   citation/format rules in `.claude/rules/research-format.md` with `paths: ["research/**"]`.
5. Ship `evals/` from `claude plugin eval init` with at least one `tool_used: Skill` grader per skill and a
   `file_exists` grader for `research/findings/*.md`; run `claude plugin validate . --strict` in CI.
6. Pin `version` in `plugin.json` and bump it per release (users on third-party marketplaces don't
   auto-update; the README must tell them `/plugin update research-agent@research-agent-marketplace`).
7. Documents the repo should contain (one line each):
   - `README.md` — what it is, 3-line install, link to docs/installation.md, capability table (works / not yet).
   - `docs/installation.md` — prerequisites, marketplace / `--plugin-dir` / template paths, verify, troubleshoot, uninstall.
   - `docs/connectors.md` — per-connector claude.ai steps, Team/Enterprise owner step, how `setup` detects them.
   - `docs/plugin-vs-template.md` — the plain-English explanation and which to use when.
   - `docs/cloud-sessions.md` — what loads in cloud, network secrets, setup script vs SessionStart.
   - `CLAUDE.md` — Claude-facing project facts and pointers (template side only).
   - `.claude/rules/*.md` — path-scoped research/diagram conventions.
   - `research/findings/_FORMAT.md`, `research/tool-registry.md`, `research/open-questions.md`, `research/diagrams/index.md` — the research workspace contract.
   - `CHANGELOG.md` — per-version notes (superpowers uses RELEASE-NOTES.md; either works).
   - `CONTRIBUTING.md` — how to add a skill, run validate/eval, bump version.
   - `SECURITY.md` — what hooks run, what network calls are made, how secrets are handled.
   - `LICENSE` — MIT like all studied plugins.
   - `.github/workflows/validate.yml` — CI gate.

## Tools evaluated

| Tool | Link | What it does | Where it runs | Verified | Verdict |
|---|---|---|---|---|---|
| `claude plugin validate [--strict]` | https://code.claude.com/docs/en/plugins-reference | Checks manifest, marketplace.json, skill/agent frontmatter, `.mcp.json` entries | Local shell, CI | 2026-10-16 | Use in CI and pre-commit |
| `claude plugin eval` | https://code.claude.com/docs/en/plugin-evals | Runs prompt cases with/without plugin, scores graders, HTML report | Local shell, CI (costs model calls) | 2026-10-16 | Use; start with `eval init` |
| `/skill-doctor` | https://code.claude.com/docs/en/skills | Per-skill context cost and usage frequency | Interactive terminal (v2.1.252+), `-p` text; not Remote Control | 2026-10-16 | Use to prune skill descriptions |
| `/doctor`, `/doctor prompt-audit` | https://code.claude.com/docs/en/slash-commands | Setup checkup; audit CLAUDE.md/skills for conflicts | Interactive terminal | 2026-10-16 | Recommend to users post-install |
| `claude plugin init` | https://code.claude.com/docs/en/plugins/create | Scaffolds a plugin under `~/.claude/skills/` that auto-loads | Local shell | 2026-10-16 | Dev convenience only |
| `plugin-dev` plugin (`/plugin-dev:create-plugin`) | https://github.com/anthropics/claude-code/tree/main/plugins | Guided 8-phase plugin creation | Local terminal | 2026-10-16 (via DeepWiki) | Optional accelerator |
| GitHub template repository | https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-template-repository | "Use this template" copies default-branch files into a new repo | GitHub web | 2026-10-16 | Use for clone-and-go |
| claude.ai connectors | https://support.claude.com/en/articles/11176164-use-connectors-to-extend-claude-s-capabilities | Remote MCP servers available in Claude Code when signed in with claude.ai | Local (claude.ai login) and cloud | 2026-10-16 | Use for Exa/Context7/Parallel/Mermaid Chart; document connect steps |
| Cloud network secrets | https://code.claude.com/docs/en/cloud-environments | Proxy attaches API key to listed hosts; key never enters VM | Anthropic-hosted cloud only | 2026-10-16 | Use for any paid API in cloud |
| `claude-code-action` `plugins` input | https://code.claude.com/docs/en/github-actions | Installs plugins unattended in CI | GitHub Actions | 2026-10-16 | Use if a CI research job is wanted |
| DeepWiki MCP (`ask_wiki_question`) | https://mcp.deepwiki.com/mcp | AI summary of indexed GitHub repos | Any (http MCP, keyless) | 2026-10-16 | Useful for indexed repos; two research repos were not indexed → fell back to raw files |
| Exa `web_fetch_exa` | claude.ai connector | Fetches raw GitHub files / pages as markdown | Cloud session via connector | 2026-10-16 | Reliable for raw.githubusercontent.com |

## Open questions

1. **Do `.claude/skills/<name>/.claude-plugin/plugin.json` "skills-dir plugins" load in cloud sessions?**
   The loading page says they need the workspace trust dialog "which a cloud session never shows", while
   the cloud page says `.claude/skills/` loads. Plain skills definitely load; whether a *plugin-shaped*
   folder there loads (with its hooks and `.mcp.json`) is unverified. Test in a cloud session.
2. **Can a hook enumerate connected MCP servers/connectors?** No documented hook input lists them. The
   `mcp_tool` SessionStart probe and skill-level tool-name check are inferred patterns; verify that a
   failed `mcp_tool` hook surfaces a readable message and that connector tool names (`mcp__Exa__*`) are
   stable across cloud and local.
3. **Symlinked `.claude/skills -> ../skills` in a template:** does Claude Code follow a symlinked skills
   directory in cloud sessions (Cowork explicitly skips symlinks pointing outside the working dir; cloud is
   not stated)? Fallback is the sync script.
4. **Project-scope `.mcp.json` approval in a fresh template clone (local):** committed
   `enableAllProjectMcpServers` is ignored until the user trusts the folder; confirm whether the trust
   dialog plus the per-server prompt is acceptable UX or whether docs should tell users to answer "Yes".
5. **ECC and mattpocock details** come from DeepWiki summaries, not opened files; confirm
   `/plugin install ecc@ecc` and `/setup-matt-pocock-skills` against the repos before citing them in
   user-facing docs.
6. **Does the claude.ai per-conversation connector toggle apply to Claude Code cloud sessions**, or are
   all connected connectors available by default there? The cloud page says "MCP connectors you enable on
   a session or routine"; the exact in-session control was not located in docs.
