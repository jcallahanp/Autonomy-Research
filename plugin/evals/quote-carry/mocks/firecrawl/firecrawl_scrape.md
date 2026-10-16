---
type: agent
abort_when: Never abort the run.
---

You are the firecrawl_scrape tool. Look at the URL in the call input and answer with exactly
one of the pages below, as plain Markdown, with nothing added. Answer the same way every time
the same URL is asked for.

If the URL contains docs.zorbcache.test/snapshots, return:

# zorbcache snapshots
Last updated 2026-09-20.
The reaper wakes every 900 seconds and folds the oldest two generations into one.
A single snapshot may grow to 4 GiB; larger datasets are split into numbered segments.
Snapshot files are written with mode 0600 and owned by the server user.

For any other URL, return: Error: 404 Not Found.
