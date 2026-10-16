---
# The findings file cites both sources.
type: regex
target: { source: file, path: research/findings/fizz-timeout.md }
pattern: '^(?=[\s\S]*docs\.fizzhttp\.test)(?=[\s\S]*blog\.fizzhttp\.test)'
---
