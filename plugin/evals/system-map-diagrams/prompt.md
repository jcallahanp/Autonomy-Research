---
description: system-map writes two small flowchart .mmd files, one concern each, linked from an index.
tags: [fast]
runs: 1
max_turns: 14
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
disallowed_tools: [WebFetch, WebSearch, Bash]
---

Draw how our Ledgerly billing service fits together: a context diagram and a container diagram. Save them as docs/diagrams/ledgerly-context.mmd and docs/diagrams/ledgerly-containers.mmd.

What I know: customers and our support staff use the Ledgerly web app. The web app calls the Ledgerly API. The API stores invoices in Postgres, charges cards through Stripe, sends receipts through SendGrid, and puts jobs on a Redis queue. A worker takes jobs off the queue and generates PDF invoices into S3.
