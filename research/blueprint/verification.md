# Blueprint check against the findings

Purpose: record whether the blueprint says what the findings say. Date: 2026-10-16.

Method: a fresh verifier picked 20 load-bearing blueprint statements by risk (prices, numbers, flags, "X cannot do Y" claims, the tension rulings, setup steps) and opened the cited evidence item in each findings file. No web lookups; the findings' own Verification sections cover the sources.

Result: 17 supported, 3 distorted, 0 uncited. One more distortion was found outside the sample. All four were fixed in place:
- decisions.md, ruling 6: the 1Password `op` pipe is a worker's inference; engineer-human-loop E112 is the same-user caveat, not support for the pipe.
- decisions.md, process shape: permission prompts stay open until answered; other forwarded dialogs expire after five minutes (was "prompts never time out", E109).
- decisions.md, area 1: the 3-13% hallucination range spans commercial LLMs and deep-research agents.
- decisions.md, area 14: no documented logged-in browser, and SSO cannot run in a cloud session (was "cloud cannot do logged-in browsing", C17).

Unverified items now labelled in the text:
- Superpowers is pinned at commit bb92a77; the "7.0.0" version label is unverified (stack.md, repo-composition.md).
- The browser area's 41-point over-report figure comes from search-page content and is unverified (decisions.md).
- Withings+ on the free API plan was already flagged unverified (setup.md).

The per-claim table was not saved: the verifier could edit files but not create one.
