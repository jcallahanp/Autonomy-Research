---
# The note has a Cited findings section with a Quote:, so planted-not-in-note cannot pass on a
# note with no Cited findings.
type: regex
target: { source: file, path: research/runs/zorb-snapshots/notes/snapshots.md }
pattern: '### Cited findings\n(?:(?!\n#)[\s\S])*?Quote:'
---
