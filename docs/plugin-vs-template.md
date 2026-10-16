# Plugin or template?

This repo is both. Pick the one that fits what you are doing.

## In plain English

A **plugin** is like an app you install once on your computer. After one install command, its
skills appear as `/research-agent:<skill>` in every project you open on that machine. It
updates from the author's repo.

A **template** is a folder of starter files you copy once with GitHub's "Use this template"
button. The copy becomes your own project. It already holds the `.claude/` setup, the
`research/` folder and a `CLAUDE.md` with the research rules.

## What loads where

| | Plugin (installed) | Template (your copy of the repo) |
| --- | --- | --- |
| Local terminal | Yes | Yes, after you trust the folder |
| Cloud session (claude.ai/code) | No. Cloud sessions do not install plugins. | Yes. Cloud sessions load the committed `.claude/` and `.mcp.json`. |
| The repo's `CLAUDE.md` rules | No | Yes |
| Skill names | `/research-agent:research` | `/research` |
| Updates | `claude plugin update` | You pull changes yourself |

Why the plugin carries no `CLAUDE.md`: a `CLAUDE.md` at the plugin root is not loaded, and
`claude plugin validate` warns about it. Plugin instructions live in skills. For that reason
the plugin sits in the `plugin/` folder of this repo, and the repo-root `CLAUDE.md` belongs to
the template side only. Behaviour for users is the same.

Sources: the load table in `research/findings/packaging.md` (Q1 and Q2), which cites the
[plugins reference](https://code.claude.com/docs/en/plugins-reference) and the
[cloud environments page](https://code.claude.com/docs/en/cloud-environments).

## Which one should I pick?

- **Use the plugin for your own projects.** You keep your repos as they are and bring the
  research skills along. See [installation.md](installation.md), path A.
- **Use the template for a research workspace.** You get the folders, the rules in
  `CLAUDE.md` and cloud-session support. It is the better choice if you will run research from
  claude.ai/code. See [installation.md](installation.md), path B, and
  [cloud-sessions.md](cloud-sessions.md).

You can use both: a template workspace for research, and the plugin on your other projects.

If you install the plugin and also open a copy of the template locally, no hook runs twice.
The template's session hook runs only in cloud sessions, and the template never turns the
plugin on by itself. You will see both `/research` and `/research-agent:research`; they are the
same skill.
