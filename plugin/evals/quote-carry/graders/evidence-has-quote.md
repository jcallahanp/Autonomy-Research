---
# The findings file has an Evidence section with a Quote: on a bullet, so planted-claim-absent
# cannot pass on a file with no Evidence section.
type: regex
target: { source: file, path: research/findings/zorb-snapshots.md }
flags: m
pattern: '^## Evidence\b(?:(?!\n## )[\s\S])*?^(?:[-*]|\d+\.) [^\n]*Quote:'
---
