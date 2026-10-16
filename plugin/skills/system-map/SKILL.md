---
name: system-map
description: Draw a system as small Mermaid diagrams. Use when the user asks to map, diagram or draw how a system, tool or integration fits together ("draw the architecture", "show how X talks to Y", "make a context diagram", "map the containers"). Produces C4 context and container levels as flowcharts, and sequenceDiagram for flows, one concern per small .mmd file in docs/diagrams/ (or a path the user names), linked from the index and validated with tests/check-mermaid.sh when it exists.
---

# System map

Make the structure of a system visible in diagrams small enough to read at a glance and review
as plain text. Never produce one giant diagram or design document.

## Requirements

- The skill shall draw C4 context and container levels as `flowchart`, and flows over time as
  `sequenceDiagram`. It shall never use C4 syntax (`C4Context`, `C4Container`, `Person(...)`).
- When a diagram would show more than one concern, the skill shall split it into separate
  `.mmd` files, one concern each, and keep each under about 25 lines.
- When it writes a diagram, the skill shall save it to `docs/diagrams/<name>.mmd`, or to the
  directory the user names, with a lowercase kebab-case name.
- When it adds a diagram, the skill shall add a row to `index.md` in the same directory with
  the link, the level (context, containers, flow) and one line on what it shows.
- When `tests/check-mermaid.sh` exists, the skill shall run it on the directory and fix any
  failure before reporting. If it does not exist, the skill shall say the diagram is unchecked.
- The skill shall draw only what it has read or been told. If a part or link is not confirmed,
  it shall omit it and list the question in `research/open-questions.md`.

## Steps

1. Ask or infer the concern for each diagram: who uses the system and what it talks to
   (context), the parts inside it and how they connect (containers), or one flow in order
   (sequence). Read the sources the user points at; use `researcher` workers for anything
   external so fetched pages stay out of the lead.
2. Draw the context level first: the system as one box, its users and external systems around
   it, one labelled edge per interaction.
3. Draw the container level: the parts inside the system boundary (a `subgraph`), what each
   one does in a few words, and the stores and external systems at the edge.
4. Draw one `sequenceDiagram` per flow that matters (a request, a run, a set-up path).
5. Save, update `index.md`, validate, and reply with the file paths.

## Mermaid rules that avoid parse errors

- Start the file with `flowchart LR`, `flowchart TB` or `sequenceDiagram`, and nothing before it.
- Quote node and edge labels that contain brackets, colons or slashes: `a["x (y)"]`, `a -- "label" --> b`.
- In a `sequenceDiagram`, never put a semicolon in a message. Mermaid reads it as a statement end.
- Use `<br/>` for line breaks in labels. Give every node a short id and a readable label.

## Optional shareable link

The Mermaid Chart connector (`mcp__Mermaid_Chart__validate_and_render_mermaid_diagram`) can
render a diagram and return a link a person can open. Use it only when the user wants a
shareable link, and run it in a worker. It is never required: the `.mmd` file in the repo is
the deliverable, and tests/check-mermaid.sh is the check.
