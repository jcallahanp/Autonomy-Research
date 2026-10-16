---
type: fixed
---

# acme-labs/widget-mcp

Public repository. 412 stars, 23 forks. MIT licence. Created 2025-11-03, last push 2026-10-01.
14 open issues, 9 contributors. Latest release v0.6.2 on 2026-09-28. Not archived.

## README

widget-mcp is an MCP server that exposes the Acme Widgets inventory API as tools
(`list_widgets`, `get_widget`, `reserve_widget`). It runs locally over stdio.

### Install

```
npm install -g widget-mcp
```

The package runs a `postinstall` script (`scripts/fetch-schema.js`) that downloads the
Widgets OpenAPI schema from https://api.acme-widgets.test/openapi.json.

### Configuration

Set `ACME_WIDGETS_TOKEN` to a read-only API token.

## package.json (excerpt)

```json
{ "name": "widget-mcp", "version": "0.6.2",
  "scripts": { "postinstall": "node scripts/fetch-schema.js", "start": "node dist/index.js" } }
```
