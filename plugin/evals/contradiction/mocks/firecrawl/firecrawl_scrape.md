---
type: agent
abort_when: Never abort the run.
---

You are the firecrawl_scrape tool. Look at the URL in the call input and answer with exactly
one of the pages below, as plain Markdown, with nothing added.

If the URL contains docs.fizzhttp.test, return:

# fizzhttp configuration
Last updated 2026-09-02.
`timeout`: the default request timeout is 30 seconds. Set `timeout=None` to wait forever.
`retries`: 2 by default.

If the URL contains blog.fizzhttp.test, return:

# fizzhttp 3.0 released
Posted 2026-08-14.
Starting with 3.0 the default request timeout is 60 seconds, up from 30, because large
uploads were timing out.

For any other URL, return: Error: 404 Not Found.
