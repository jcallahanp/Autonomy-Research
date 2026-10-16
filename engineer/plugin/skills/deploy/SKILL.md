---
name: deploy
description: Choose where a project runs and ship it safely, preview first. Use when a task deploys, publishes or releases anything, picks a hosting platform, or adds a migration, domain or paid resource ("deploy this", "where should this run", "ship the preview", "promote to production", "roll back"). Gives the platform decision table, the preview-then-promote route with the promote as a T1 line whose default is hold, the 11-item pre-promote checklist, the rollback table and the watch window, and the T2 hard gates for spending money, deleting data and app-store submission.
---

# Deploy

Deploy previews yourself. Promote to production only after John says go. Never spend money,
delete data or submit to an app store without his typed confirmation.

## Rules (EARS)

- F35: When a deploy is due, deploy a preview with the platform CLI and one narrow token, then
  run the 11-item pre-promote checklist below.
- F36: When the checklist passes, add a T1 promote line with default `hold`, unless
  `docs/plan/profile.yaml` gates promotes as T2 (then write a `HARD GATE: promote` line instead).
- F37: If the watch window after a promote fails, then roll back at once and tell John.
- F38: When an action spends money, deletes data or submits to an app store, write a
  `HARD GATE:` line (below); the supervisor sends it as a separate T2 prompt that needs John's
  typed `CONFIRM`, and no default ever applies.
- Rolling back is allowed without approval. Rolling forward is not.
- Use the platform CLI with a token from the broker. Use vendor MCP servers read-only (logs,
  status), never to deploy.

## Choose the platform

Pick the first row that fits the project. Free tiers first. Record the choice as an ADR and the
service, token scope and price (with the date) in `docs/plan/integrations.yaml`.

| Project type | Platform | Deploy command (preview) |
| --- | --- | --- |
| Static site or single-page app | Cloudflare Workers static assets (or Pages) | `wrangler deploy` to a preview environment or `wrangler versions upload` |
| Edge API with a small database | Cloudflare Workers with D1 and R2 | as above |
| Next.js or SSR that needs Vercel features, personal use only | Vercel Hobby | `vercel deploy` (no `--prod`) |
| Postgres app with auth and storage | Supabase Free, or Neon Free plus own auth | `supabase db push` against a branch or staging project |
| Container API that can scale to zero | Google Cloud Run in John's project | `gcloud run deploy SERVICE --source . --no-traffic --tag preview` |
| Always-on bot, queue worker, n8n | The VM, Docker Compose, behind Cloudflare Tunnel and Access | compose up on a staging port, probe `/healthz` |
| Scheduled jobs and webhook receivers | systemd timers with `Persistent=true`; Worker cron and Worker receivers | as the row above it |
| Android app | PWA first; Capacitor when native APIs are needed | build and install on a test device with `adb` |

- iOS is deferred. Google Play needs a $25 account, identity checks and testers: John's steps.
- A paid plan, a new domain or any new paid resource is a `money` hard gate (T2).
- The deploy guard blocks production commands (`vercel ... --prod`, `wrangler deploy
  --env production`, `gcloud ... update-traffic`, `supabase db push` to production). Do not try
  other spellings; the guard is there so promotes go through John.

## Preview, then promote

1. Deploy the preview from the task branch with the platform CLI.
2. Run a smoke test against the preview URL: the health endpoint and one key page or call.
3. Run the pre-promote checklist. Every item gets `pass`, `fail` or `n/a` with its evidence.
4. If any item fails, fix it in a new task or record the blocker; do not ask for a promote.
5. When every item passes, add one T1 line (see the `digest` skill):
   `Promote <project> <sha7> to production? Preview <url>. Rollback: <command>` with
   default `hold`, `kind: promote`. If `profile.yaml` sets `promote` to `t2`, write
   `HARD GATE: promote Promote <project> <sha7> to production. Rollback: <command> CONFIRM: PROMOTE <sha7>`.
6. Stage 1 has no promote runner: after John replies `y`, the promote is run from the command in
   the line by an attended session or by John. Never run it from an unattended session.

## Pre-promote checklist

1. CI is green for the exact SHA being promoted, and the diff has no secrets.
2. The preview passes the smoke test.
3. Every migration is add-only (expand, never contract), and a backup was taken first.
4. The previous release and its rollback command are written down.
5. Every secret the target needs is present, checked by name only.
6. Tokens are the narrowest that work; any OIDC subject is pinned to this repo and branch.
7. DNS and TLS are valid for the target host.
8. An uptime check and error tracking exist for the target.
9. No new paid resource, unless John confirmed it with a T2 reply.
10. The approval line carries a diff summary, the preview URL and the rollback command.
11. A watch window with automatic rollback is ready, and John is notified at its end.

Out of scope without John, always: a destructive or contract migration, a new paid plan, a new
domain, a new OAuth scope.

## Rollback

| Platform | Roll back | Note |
| --- | --- | --- |
| Vercel | `vercel rollback` (Hobby: previous production only) | undo with `vercel promote <deployment>` |
| Cloudflare Workers | `wrangler rollback [version-id]` | bound resources (D1, R2) are not rolled back |
| Cloud Run | `gcloud run services update-traffic SERVICE --to-revisions <previous>=100` | the deploy guard blocks `update-traffic`, so add a T1 line with this command at once and tell John |
| VM with Compose | restart the previous image tag | migrations stay add-only so the old image still runs |

Rollback never fixes data. That is why migrations are add-only and a backup comes first.

## Watch window

After a promote, probe `/healthz` and one key page every minute for 15 minutes (or the window
the plan sets). On two failures in a row, roll back, confirm the rollback with the same probe,
and add a T1 line saying what failed, what you rolled back to, and the evidence.

## Hard gates (T2)

These need a separate T2 prompt and John's exact `CONFIRM <n> <PHRASE>` reply. No default ever
applies, and silence means no. Stop before the action, write one bullet under `## Asks for John`
in `PROGRESS.md`, and end the task `needs_john`:
`HARD GATE: <money|delete|appstore> <text> CONFIRM: <PHRASE>` (gate words: `money`, `delete` for
`delete_data`, `appstore` for `store_submission`). The supervisor sends it at once as
`HARD GATE N: <project>: <text>`; without `CONFIRM:` the phrase is `MONEY N`, `DELETE N` or `STORE N`.
- `money`: any purchase, paid plan, domain, paid add-on or spend above the plan's ceiling.
- `delete_data`: dropping or truncating a table, a contract migration, deleting records in a live
  system, deleting a bucket or a backup.
- `store_submission`: submitting to Google Play or any app store.

Write the T2 text so John can decide from his phone: what happens, the exact amount or the exact
data, whether it can be undone, and the phrase he must type.
