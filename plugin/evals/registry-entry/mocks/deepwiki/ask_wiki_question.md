---
type: fixed
---

widget-mcp is a TypeScript MCP server (src/index.ts) using the official MCP TypeScript SDK
over stdio. It wraps three REST endpoints of the Acme Widgets API. On install, a postinstall
hook (scripts/fetch-schema.js) downloads an OpenAPI schema. It reads ACME_WIDGETS_TOKEN from
the environment and sends it as a bearer token.
