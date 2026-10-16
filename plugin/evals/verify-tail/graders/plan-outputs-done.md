---
# PLAN.md's Outputs section no longer says pending or running once the run has finished.
type: regex
target: { source: file, path: research/runs/quux-durability/PLAN.md }
flags: mi
match: not_contains
pattern: '^## Outputs\b(?:(?!\n## )[\s\S])*?\b(?:pending|running)\b'
---
