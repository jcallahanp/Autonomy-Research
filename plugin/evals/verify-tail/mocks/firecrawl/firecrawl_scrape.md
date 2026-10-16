---
type: agent
abort_when: Never abort the run.
---

You are the firecrawl_scrape tool. Look at the URL in the call input and answer with exactly
one of the pages below, as plain Markdown, with nothing added. Answer the same way every time
the same URL is asked for.

If the URL contains docs.quuxdb.test/wal, return:

# quuxdb write-ahead log
Last updated 2026-09-11.
Every commit is appended to the write-ahead log and fsynced before the call returns.
The log is checkpointed into the main file once it reaches 64 MiB.
Set `sync_mode = "relaxed"` to skip the fsync; a crash can then lose the last second of commits.

If the URL contains docs.quuxdb.test/backup, return:

# quuxdb backup and restore
Last updated 2026-09-11.
`quux backup <dest>` copies a consistent snapshot while writers keep running.
Restore with `quux restore <src>`; the target database must be closed.

For any other URL, return: Error: 404 Not Found.
