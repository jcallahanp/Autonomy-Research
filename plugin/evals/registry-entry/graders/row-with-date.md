---
# One table row names widget-mcp and carries a verified date.
type: regex
target: { source: file, path: research/tool-registry.md }
flags: m
pattern: '^\|[^\n]*widget-mcp[^\n]*\|[^\n]*\b20\d\d-\d\d-\d\d\b[^\n]*\|'
---
