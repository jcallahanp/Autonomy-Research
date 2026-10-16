# Reports, gates, remediation and cadence

Brief: Define how an autonomous engineer turns security results into deploy gates, tracked remediation and a professional report that is honest about what it assures.
Run: research/runs/engineer-security/PLAN.md

Connectors note: Parallel Search returned "Too Many Requests" on both search calls; used Exa search and WebFetch. DeepWiki, Firecrawl and Playwright were not connected.

## What a professional report contains and what goes to John

### Takeaway
Use the WSTG structure (introduction with scope, limitations, timeline and disclaimer; executive summary; findings summary and details; reproducible test artifacts; appendices for methodology and rating explanations), trimmed for a single owner: a one-page brief for John, with the full report as an appendix file beside it. Confidence: medium (WSTG opened; PTES 503, NIST PDF unreadable).

### Cited findings
- WSTG lists Introduction (scope, limitations, timeline, disclaimer), Executive Summary, Findings (summary plus details), Human Factors, Reproducible Test Artifacts, and Appendices (methodology, severity explanations) — https://wstg.owasp.org/latest/5-Reporting/01-Reporting_Structure, opened 2026-10-16, WebFetch — Quote: "A list of the findings with their risk level."
- WSTG defines limitations as what was not tested — same URL — Quote: "Out-of-bounds areas in relation to testing."
- WSTG wants artifacts that let developers retest — same URL — Quote: "These artifacts can help developers quickly validate and retest vulnerabilities."
- WSTG puts methodology and rating explanations in an appendix — same URL — Quote: "Severity and risk rating explanations."
- Public reviews carry a point-in-time disclaimer (OpenSSF security-reviews repo) — https://github.com/ossf/security-reviews/blob/main/reviews/linux-kernel/linux-kernel-vuln-remediation.md, opened 2026-10-16, WebFetch — Quote: "All security reviews are conducted on a "best-effort" basis against a software component at a point in time."
- An LLM scanner's own report can disclose the runs it did not do — https://dev.to/shimo4228/claude-security-beta-cost-output-accuracy-189-agents-2-hours-measured-1eji, opened 2026-10-16, WebFetch — Quote: "No tests run, no exploit fires, no proof of concept is validated."

### Contradictions
- None found.

### Inferences
- Proposed layout (mine, from the WSTG list): `security/REPORT.md` (full: scope, tool names and versions, per-framework-item coverage table, findings with evidence, retest status, limitations) and `security/BRIEF.md` (one page for John: verdict line, open High items with due date, what was and was not checked, one decision needed). Findings machine-readable as SARIF or JSON beside them so a later run can diff.
- Include a "Not checked" list as prominently as findings; this follows from the WSTG limitations field and the OpenSSF point-in-time disclaimer.

### Gaps
- PTES reporting page: HTTP 503 at http://www.pentest-standard.org/index.php/Reporting; not cited.
- NIST SP 800-115 section 7: PDF at nvlpubs.nist.gov returned undecodable binary via WebFetch; not cited.
- No Trail of Bits or OSTIF full report opened (only an OpenSSF disclaimer); severity/difficulty definitions of a named firm not confirmed.
- SARIF-to-report converters (DefectDojo import, Faraday): not opened; no claim made.

## Severity: CVSS 4.0 or High/Medium/Low

### Takeaway
For a solo owner use a four-level rubric (Critical, High, Medium, Low) assigned from exploitability plus impact in John's own terms, and record a CVSS 4.0 base vector only for dependency/CVE findings that already carry one. CVSS itself says it ranks severity, not risk. Confidence: medium.

### Cited findings
- CVSS 4.0 scores rank vulnerabilities relative to each other — https://www.first.org/cvss/v4.0/specification-document, opened 2026-10-16, WebFetch — Quote: "Its outputs include numerical scores indicating the severity of a vulnerability relative to other vulnerabilities."
- Risk factors beyond the score are out of CVSS scope — same URL — Quote: "These factors are outside the scope of CVSS."
- CVSS 4.0 wants a nomenclature label on any displayed score (CVSS-B for Base only, CVSS-BTE with Threat and Environmental) — same URL — Quote: "This nomenclature should be used wherever a numerical CVSS value is displayed or communicated."
- GitHub code scanning thresholds are expressed as Critical, High or higher, Medium or higher, All — https://docs.github.com/en/code-security/code-scanning/managing-your-code-scanning-configuration/set-code-scanning-merge-protection, opened 2026-10-16, WebFetch — Quote: "Required tools and alert thresholds"

### Contradictions
- None found.

### Inferences
- A CVSS vector for a custom-code finding found by an LLM is a guess dressed as precision; the FIRST text says the score is about severity, not risk. A solo owner needs "fix before deploy / fix this week / fix when touched / note". Mine, from the CVSS quotes.
- Because gates in GitHub and GitLab consume severity levels, a 4-level rubric maps straight onto them.

### Gaps
- No source opened on EPSS or CISA KEV for exploitability weighting (EPSS page 404 at first.org/epss/model); recommended only as an optional field.
- Not confirmed how LLM-assigned CVSS compares with human scoring.

## Honest claims: what scan plus LLM review may say

### Takeaway
It may claim: "automated static scan and LLM code review of named paths, with named tool versions, on a stated commit; N findings; these framework items checked, these not". It may not claim: penetration test, absence of vulnerabilities, compliance, or assurance beyond the commit. Confidence: medium (PCI wording only seen in a search snippet, so gap).

### Cited findings
- Anthropic's own security-review Action warns it should be used on trusted PRs only — https://github.com/anthropics/claude-code-security-review, opened 2026-10-16, WebFetch — Quote: "This action is not hardened against prompt injection attacks and should only be used to review trusted PRs."
- That Action filters out categories by design, so silence on them is not a clean result — same URL — Quote: "The tool automatically excludes a variety of low-impact and false positive prone findings to focus on high-impact vulnerabilities:"
- LLM scans vary between runs — dev.to measurement above — Quote: "Scans are nondeterministic. Two scans of the same code can surface different findings."
- A static read does not prove exploitability — dev.to — Quote: "No tests run, no exploit fires, no proof of concept is validated."
- Public reviews are scoped by time — OpenSSF disclaimer above — Quote: "All security reviews are conducted on a "best-effort" basis against a software component at a point in time."
- Claude Code docs: no system is immune — https://code.claude.com/docs/en/security, opened 2026-10-16, WebFetch — Quote: "no system is completely immune to all attacks."

### Contradictions
- None found.

### Inferences
- Mandatory report footer (mine): scope and commit hash; tools with versions; "not a penetration test: nothing was exploited"; "absence of findings is not evidence of absence"; list of unchecked framework items; nondeterminism (re-running may change results).
- For John in plain words: three states per area, "checked and clean at this commit", "checked, issues open", "not checked". Never a single "secure" verdict.

### Gaps
- PCI SSC Penetration Testing Guidance (scan vs pentest difference; "simply running an automated tool does not satisfy the penetration testing requirement") seen only in an Exa result; PDF at listings.pcisecuritystandards.org returned binary via WebFetch; not cited.
- No NCSC or ISO wording opened.
- Third-party claim that Claude Security costs "$5 to $25" per scan appears in a Startup Fortune search result only; page not opened; not used as a figure.

## Gates, exceptions, remediation and retest

### Takeaway
Block merge/deploy on: any new Critical or High from the deterministic scanners, any secret, any failing auth/authorisation test. Everything else becomes a ticket with a due date by severity. Exceptions are recorded with reason, owner and expiry, and an expired exception re-opens the finding. LLM-only findings should warn and ticket, not block, until reproduced. Confidence: medium.

### Cited findings
- GitHub: per-tool merge-protection thresholds are configurable — https://docs.github.com/en/code-security/code-scanning/managing-your-code-scanning-configuration/set-code-scanning-merge-protection, opened 2026-10-16, WebFetch — Quote: "Optionally, to change the default enforcement status, click Disabled."
- GitHub dismissal comments are optional, so John's process must make the reason mandatory — https://docs.github.com/en/code-security/code-scanning/managing-code-scanning-alerts/resolving-code-scanning-alerts, opened 2026-10-16, WebFetch — Quote: "Optionally, you can comment on a dismissal to record the context of an alert dismissal."
- GitLab policies take severity levels and a count threshold per rule — https://docs.gitlab.com/user/application_security/policies/merge_request_approval_policies/, opened 2026-10-16, WebFetch — Quote: "Number of vulnerabilities allowed before this rule is considered."
- GitLab also has a warn mode — same URL — Quote: "allows merge requests to proceed but shows warnings and bot comments."
- GitLab bypass is a recorded exception — same URL — Quote: "When a bypass condition is met, the policy is not enforced for the matching merge request or branch."
- DefectDojo counts SLA days from finding creation and flags breaches; per-severity days are configurable — https://docs.defectdojo.com/asset_modelling/os_hierarchy/os__sla_configuration/, opened 2026-10-16, WebFetch — Quote: "Newly created Assets in DefectDojo will always apply the Default SLA Configuration."
- DefectDojo ties risk-acceptance expiry to SLA restart — same URL — Quote: "Risk Acceptance expiry or reactivation of a Closed Finding are the only ways to reset or recalculate an SLA"
- DefectDojo can restart the SLA on reopen — same URL — Quote: "Restart SLA on Finding Reactivation"

### Contradictions
- None found.

### Inferences
- Proposed SLA table (mine, not from a source): Critical/High block merge; Medium due 30 days; Low due 90 days or when the file is next touched. DefectDojo page gave no default day values, so these are my numbers to tune.
- Exception record (mine): finding id, reason, who accepted (John), expiry date (max 90 days), compensating control; engine refuses to treat an expired exception as valid. Mirrors DefectDojo expiry plus GitLab bypass reason.
- Retest on fix: the fixing change must carry a regression test (or a re-run scanner rule) and the next report shows "retested at commit X: closed".
- DefectDojo itself is heavy for one user; a `security/findings.json` with ids, status, due, exception-expiry achieves the same with a hook or CI check. Not spiked.

### Gaps
- DefectDojo default SLA values not stated on the opened page.
- GitHub alert dismissal expiry: page does not say; not verified in settings.
- Whether Claude Code hooks can enforce "no deploy while gate file red" is another facet; not covered here.

## Cadence and cost

### Takeaway
Three tiers: per-change fast deterministic checks (secrets, SAST on diff, dependency audit, auth tests) on every change; an LLM diff review on PRs touching auth, data access or config; a full audit per milestone; a scheduled weekly or monthly rescan for new CVEs in dependencies. Token costs for LLM audits are only partly sourced. Confidence: low-medium.

### Cited findings
- One LLM full scan of a small config tree used 189 subagents over two hours — https://dev.to/shimo4228/claude-security-beta-cost-output-accuracy-189-agents-2-hours-measured-1eji, opened 2026-10-16, WebFetch — Quote: "189 subagents ran for two hours and returned 20 findings."
- Same source: no dollar total published; routine use is a diff scan (small diffs use a lighter shape) — Quote: "This scan may take a while and may use a significant number of tokens."
- Claude Code docs give general spend context — https://code.claude.com/docs/en/costs, opened 2026-10-16, WebFetch — Quote: "Agent teams use approximately 7x more tokens than standard sessions when teammates run in plan mode"
- Same doc on model choice — Quote: "Sonnet handles most coding tasks well and costs less than Opus."
- The Action only scans changed files on PRs — https://github.com/anthropics/claude-code-security-review, opened 2026-10-16, WebFetch — Quote: "**Diff-Aware Scanning**: For PRs, only analyzes changed files"

### Contradictions
- None found.

### Inferences
- Tiering (mine): the fast tier costs near zero tokens if deterministic; LLM spend should be bounded with `--max-budget-usd` (already in registry) per audit; the milestone audit is the only tier near the two-hour scale shown.
- Weekly scheduled runs fit Routines or GitHub Actions cron rows in the registry; dependency rescans matter even with no code change because new CVEs appear.

### Gaps
- No sourced dollar cost per LLM security scan; the $5-25 figure is unverified (snippet only).
- Runtimes of Semgrep/gitleaks/CodeQL not measured here (tooling is another facet).

## Recommendation, alternatives, rejected, spikes

### Takeaway
Recommend: a file-based pipeline. Deterministic gates block (new High/Critical, any secret, failing auth tests); LLM review warns and tickets; `security/findings.json` is the source of truth with due dates and expiring exceptions; each milestone produces `REPORT.md` (WSTG-shaped) plus a one-page `BRIEF.md` for John in dark-theme brief style, with coverage stated as checked / open / not checked and a standing "not a penetration test" footer.
Alternatives: DefectDojo self-hosted for tracking (adds a service for one user); GitHub code scanning merge protection if the repo is on GitHub (thresholds native, CodeQL only). Rejected: CVSS 4.0 scoring of LLM-found custom-code issues (false precision); a single "secure" or percentage score; blocking on unreproduced LLM findings.
Spike before building: (1) whether a hook/CI check can read findings.json and fail deploy on expired exceptions; (2) measure real token cost of an LLM diff review and a milestone audit on John's repo; (3) fetch PTES/NIST text for the report checklist; (4) test GitHub merge-protection on a private repo plan.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| GitHub code scanning merge protection | https://docs.github.com/en/code-security/code-scanning/managing-your-code-scanning-configuration/set-code-scanning-merge-protection | Per-tool alert thresholds (Critical, High or higher, Medium or higher, All) as a required check | GitHub | 2026-10-16 | Use if repo is on GitHub; dismissal comments optional, so add own exception record |
| GitLab merge request approval policies | https://docs.gitlab.com/user/application_security/policies/merge_request_approval_policies/ | Block or warn on new findings by severity count; bypass settings with reason | GitLab | 2026-10-16 | Reference design for gate and exception semantics; not adopted (GitHub assumed) |
| DefectDojo (SLA and risk acceptance) | https://docs.defectdojo.com/asset_modelling/os_hierarchy/os__sla_configuration/ | Per-severity SLA days, breach flag, risk-acceptance expiry restarts SLA; risk-based SLA is Pro | self-hosted / hosted | 2026-10-16 | Reference design; skip as a service for one user unless findings volume grows |
| anthropics/claude-code-security-review | https://github.com/anthropics/claude-code-security-review | GitHub Action: diff-aware LLM review, PR comments, results JSON; not hardened against prompt injection | GitHub runner | 2026-10-16 | Fallback for PR review on trusted PRs only; warn, never sole gate |
| OWASP WSTG reporting structure | https://wstg.owasp.org/latest/5-Reporting/01-Reporting_Structure | Report section list | docs | 2026-10-16 | Use as the REPORT.md skeleton |
| FIRST CVSS 4.0 | https://www.first.org/cvss/v4.0/specification-document | Severity scoring with B/BTE labels | spec | 2026-10-16 | Use only for CVE-bearing dependency findings, with label |
| claude-security plugin (beta, per dev.to measurement) | https://dev.to/shimo4228/claude-security-beta-cost-output-accuracy-189-agents-2-hours-measured-1eji | Multi-agent LLM scan with panel verification; one third-party run: 189 agents, 2 h, 20 findings | Claude Code plugin | 2026-10-16 (article only, not installed) | Candidate for milestone audit; spike cost first |
