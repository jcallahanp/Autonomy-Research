---
# PLAN.md's Outputs section records the verification count, so plan-outputs-done cannot pass
# on a stub or empty PLAN.md.
type: regex
target: { source: file, path: research/runs/quux-durability/PLAN.md }
flags: m
pattern: '^## Outputs\b(?:(?!\n## )[\s\S])*?^- Verification: [^\n]*\d+ of \d+'
---
