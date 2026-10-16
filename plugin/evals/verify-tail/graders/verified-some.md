---
# The verifier could re-open the mocked pages: at least one sampled claim counts as verified.
# "Unverified: 1" does not match (no word boundary inside "Unverified").
type: regex
target: { source: file, path: research/findings/quux-durability.md }
flags: mi
pattern: '^## Verification\b[\s\S]*?\bVerified\b\W{0,4}[1-9]'
---
