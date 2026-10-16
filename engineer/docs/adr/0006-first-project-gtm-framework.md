# ADR 0006: First project is the GTM framework over Attio, Clay, n8n

Status: accepted 2026-10-16

## Context
- John's GTM acceptance scenario runs over Attio, Clay and n8n, which are web apps (blueprint gtm-scenario.md; engineer-host §Recommendation).
- The blueprint's setup sitting also listed Outreach, Google OAuth, WHOOP, Withings, Slack, GCP, Vercel and Supabase (blueprint setup.md, Phase D).
- Vendor API shapes for snapshot exports are unverified (blueprint spikes.md SP60, SP65, SP66).

## Decision
- The first project after setup is the GTM framework over Attio, Clay and n8n.
- The focus is the framework for automating such projects, not one-off vendor scripts.
- Stage 1 builds framework code only; vendor snapshot exporters wait for that project's as-is stage.

## Consequences
- Setup steps 15-17, 26, 28, 29 and 31 move to per-project rows (blueprint setup.md; Open decision 2).
- The setup sitting covers the engine's own accounts plus Attio, Clay, n8n and the Google sign-in.
- The browser allowlist starts with Attio, Clay and Google sign-in hosts; John's n8n host is added on setup day (Open decision 8).
