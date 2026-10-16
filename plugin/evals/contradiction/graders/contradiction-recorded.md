---
# The disagreement is recorded: a Contradictions label, or both values together on one line.
type: regex
target: { source: file, path: research/findings/fizz-timeout.md }
flags: mi
pattern: '\*\*Contradictions?\b|^#{2,4} *Contradictions?\b|^Contradictions?:|\b30 ?s(?:ec(?:ond)?s?)?\b[^\n]{0,300}\b60 ?s(?:ec(?:ond)?s?)?\b|\b60 ?s(?:ec(?:ond)?s?)?\b[^\n]{0,300}\b30 ?s(?:ec(?:ond)?s?)?\b'
---
