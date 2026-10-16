---
type: llm
focus: { source: file, path: research/findings/fizz-timeout.md }
---

You are grading the citations in a research findings file. Two sources were available:
https://docs.fizzhttp.test/config says the default timeout is 30 seconds;
https://blog.fizzhttp.test/release-3 says that from 3.0 it is 60 seconds, up from 30.

PASS only if all of these hold:
- Accuracy: every value attributed to a URL is what that page says (30 seconds to the docs
  URL, 60 seconds from 3.0 to the blog URL). No claim is attributed to the wrong URL.
- Completeness: each factual claim about fizzhttp carries a URL, and the Evidence section
  lists both URLs with a date and the tool used to open them.
- Both claims appear together where the disagreement is discussed, and the file either says
  which it favours and why, or marks it unresolved.
- No URL appears that is not one of the two above.

FAIL if the file is missing or empty, if any claim is attributed to the wrong source, if a
claim has no URL, if either source is dropped, or if the file picks one value without saying
why.
