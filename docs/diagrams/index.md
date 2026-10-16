# Diagrams

Small Mermaid files, one concern each. Render any of them at https://mermaid.live or with the
Mermaid Chart connector.

| File | Level | What it shows |
| --- | --- | --- |
| [c1-context.mmd](c1-context.mmd) | C4 context | Who uses the researcher and what it talks to |
| [c2-containers.mmd](c2-containers.mmd) | C4 containers | The plugin's parts and the research workspace they write |
| [c3-research-run.mmd](c3-research-run.mmd) | Component / sequence | One research run: lead, workers, synthesizer, verifier, files |
| [tool-routing.mmd](tool-routing.mmd) | Decision flow | Which tool each research step uses, and the fallbacks |
| [context-flow.mmd](context-flow.mmd) | Data flow | What lives in the lead's context, the workers' contexts, and on disk |
| [setup-flow.mmd](setup-flow.mmd) | Flow | How a new user or cloud session gets to a working state |
