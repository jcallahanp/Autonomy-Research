---
# The verifier appended a ## Verification section to the findings file.
type: regex
target: { source: file, path: research/findings/quux-durability.md }
flags: m
pattern: '^## Verification\b'
---
