---
# The triage adds the repo's row to the tool registry.
type: regex
target: { source: file, path: research/tool-registry.md }
flags: mi
pattern: '^\|[^\n]*modelcontextprotocol/servers[^\n]*\|'
---
