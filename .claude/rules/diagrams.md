---
paths:
  - "docs/diagrams/**"
---

# Diagram files

Template-side rule for anything under `docs/diagrams/`. The list of diagrams is
`docs/diagrams/index.md`; read it before adding one.

- One concern per file, small `.mmd` files. Never one giant design document.
- Use `flowchart` for C4 context and container levels and for decisions, and `sequenceDiagram`
  for flows over time. Never C4 syntax (`C4Context`, `Person(...)`).
- Link every new diagram from `docs/diagrams/index.md` in the same change, with its level and
  one line on what it shows.
- In a `sequenceDiagram` message, no semicolons. Quote labels that hold brackets or colons.
- Check with `bash tests/check-mermaid.sh` (renders each file, checks the index link, rejects
  C4 syntax). `tests/check.sh` does not render diagrams.
