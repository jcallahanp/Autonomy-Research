# ADR 0003: SOPS and age secrets behind secretbroker, no 1Password

Status: accepted 2026-10-16

## Context
- Secret leaks pass every model-facing control and transcripts are plaintext (engineer-human-loop E69-E72, E81, E82).
- The blueprint's default was SOPS+age behind a `secretbroker` Unix user with an allowlisted `agent-run` runner; a 1Password `op` pipe would replace it if John had 1Password (blueprint decisions.md, ruling 6; engineer-human-loop E58-E60).
- John has no 1Password.

## Decision
- Secrets live only in SOPS files encrypted with age, readable only by `secretbroker`.
- The engineer uses a secret only through `sudo -u secretbroker agent-run <job>`; John seeds values with `seed` from his own SSH terminal.
- No `op` rows anywhere; TOTP, when a project needs it, comes through a pyotp wrapper run by the broker (a later stage).

## Consequences
- Stage 1 builds `agent-run`, `seed` and the broker jobs; `oauth-capture`, `mint-child` and the TOTP wrapper wait for the first project that needs them.
- No secret value appears in argv, logs or stdout (plan Review Focus 2).
- Cost: free (blueprint stack.md).
