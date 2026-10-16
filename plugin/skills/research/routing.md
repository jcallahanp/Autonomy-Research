# Tool routing

Which tool to reach for at each research step. Try the primary; use the fallback when the
primary is missing, errors, or returns nothing. When a connector is missing, say so in the
output (see `setup`). Evidence: `research/findings/tool-routing.md`.

| Step | Primary | Fallback |
| --- | --- | --- |
| Find tools or repos | Parallel web_search | Exa web_search_exa, then WebSearch |
| Find MCP servers | Official MCP registry API (curl) | Parallel search with `site:github.com mcp` |
| Find code across GitHub | Sourcegraph stream API (curl) | Exa with code phrasing |
| Read a page | Parallel web_fetch with objective | Exa fetch, Firecrawl keyless, Playwright in a subagent |
| Verify and cite | WebFetch with a pointed prompt | Firecrawl scrape, then Parallel or Exa fetch with an objective |
| Understand a repo | DeepWiki ask_wiki_question | `git clone --depth 1` + grep (also the confirmation step) |
| Library API syntax | Context7, at most 3 calls | WebFetch the official docs page |
| Test an edge case | Bash (curl, clone, run) | Playwright in a subagent |
| Draw architecture | Write `.mmd`, validate with local `mmdc` | Mermaid Chart MCP in a subagent; live editor link for humans |

Hand-off contract: a discovery result is cut to three URLs before any fetch; every fetch ends in
one Evidence bullet or is dropped; every DeepWiki claim is confirmed against the clone before
the repo is written up.

"Test an edge case" means a probe the user asked for, run by a worker. It never means running
a candidate tool found during discovery or triage (see `repo-triage`).
