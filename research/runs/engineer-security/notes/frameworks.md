# Security frameworks and which items tooling can check

Brief: Pick the security frameworks that give an autonomous engineer checkable pass/fail tests for John's project types and split items into tool-checkable versus judgement.
Run: research/runs/engineer-security/PLAN.md

Legend used in lists: T = a tool gives pass/fail; L = LLM reviewer can check with file:line evidence; H = human judgement or real pentest.

## Framework versions and coverage
### Takeaway
Use ASVS 5.0.0 (May 2025) as the master checklist, Level 1 as the floor and a hand-picked Level 2 subset for auth, session, access control and health data; add API Top 10 2023 for integrations, MASVS plus MASTG for Android, LLM Top 10 2025 and Agentic Top 10 2026 for LLM features, CIS Ubuntu 24.04/26.04 and Docker 1.9.0 for the VM, and SSDF only as a process vocabulary. Confidence: high on versions, medium on the level recommendation (my judgement).

### Cited findings
- ASVS current stable is 5.0.0, May 2025, released at Global AppSec EU Barcelona — https://github.com/OWASP/ASVS 5.0 README.md (commit 2b47a9d), read 2026-10-16, git clone — Quote: "The latest stable version is version 5.0.0 (dated May 2025)"
- ASVS 5.0 has 345 requirements by CSV count: L1 70, L2 183, L3 92 (my count of `5.0/docs_en/*_en.csv`, commit 2b47a9d); the prose says L1 is about 20%, and L2 compliance needs L1+L2 — https://github.com/OWASP/ASVS 5.0/en/0x03-What-is-the-ASVS.md:99-101 (commit 2b47a9d), read 2026-10-16, git clone — Quote: "an application needs to implement around 70% of the requirements in the ASVS (all of the L1 and L2 requirements) in order to comply with L2."
- ASVS levels are risk-chosen, not prescribed, and you may fork and omit irrelevant chapters — same file :112-114 and :145 — Quote: "an early-stage startup that is only collecting limited sensitive data may decide to focus on Level 1 for its initial security goals"
- ASVS ships machine-readable exports (CSV, JSON, XML, CycloneDX) so a checklist can be generated, and v4.0.3-to-5.0.0 mapping YAML — https://github.com/OWASP/ASVS 5.0/mappings/README.md:12-13 (commit 2b47a9d), read 2026-10-16 — Quote: "`mapping_v4.0.3_to_v5.0.0.yml` - from v4.0.3 to v5.0.0"
- ASVS 5.0 has 17 chapters (V1 Encoding ... V16 Logging and Error Handling, V17 WebRTC); chapters can be dropped when unused — 5.0/en/0x03-What-is-the-ASVS.md:121 (commit 2b47a9d) — Quote: "around 350 requirements which are divided into 17 chapters"
- OWASP Top 10 2025 final list A01 Broken Access Control ... A03 Software Supply Chain Failures, A10 Mishandling of Exceptional Conditions — https://top10.owasp.org/2025, opened 2026-10-16, WebFetch — Quote: "A10:2025 - Mishandling of Exceptional Conditions"; also "A03:2025 - Software Supply Chain Failures"
- API Security Top 10 is still the 2023 edition (API1 BOLA ... API10 Unsafe Consumption of APIs) — https://api-security.owasp.org/editions/2023/en/0x00-header, opened 2026-10-16, WebFetch — Quote: "API10:2023 Unsafe Consumption of APIs"
- WSTG latest stable is v4.2 (3 Dec 2020); 5.0 still in development — https://owasp.org/www-project-web-security-testing-guide/ , opened 2026-10-16, WebFetch — Quote: "We are currently developing release version 5.0."
- LLM Top 10 is the 2025 edition, LLM01 Prompt Injection ... LLM06 Excessive Agency ... LLM10 Unbounded Consumption — https://genai.owasp.org/llm-top-10/ , opened 2026-10-16, WebFetch — Quote: "LLM10:2025 Unbounded Consumption"
- Agentic Top 10 for 2026 published 9-10 Dec 2025, ASI01 Agent Goal Hijack ... ASI10 Rogue Agents — https://genai.owasp.org/download/52117/ (Exa fetch of search highlights; table of contents) and https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/ (WebFetch), 2026-10-16 — Quote: "ASI02: Tool Misuse and Exploitation" ; page: "December 9, 2025"
- MASVS has eight control groups (STORAGE, CRYPTO, AUTH, NETWORK, PLATFORM, CODE, RESILIENCE, PRIVACY); the old L1/L2/R levels were reworked as "MAS Profiles" — https://github.com/OWASP/owasp-masvs Document/03-Using_the_MASVS.md:28 (commit bbe226f, repo date 2026-09-21), read 2026-10-16, git clone — Quote: "have been reworked as [\"MAS Profiles\"](https://mas.owasp.org/Profiles/)"
- CIS lists Ubuntu Linux 26.04 LTS (1.0.0), 24.04 LTS (2.0.0) and Docker (1.9.0); benchmark page gives no price statement — https://www.cisecurity.org/cis-benchmarks , opened 2026-10-16, WebFetch — Quote: "Ubuntu Linux 24.04 LTS (2.0.0)"; "Docker (1.9.0)"
- SSDF: v1.1 final Feb 2022; Rev 1 (v1.2) is still an initial public draft dated 17 Dec 2025, comments closed 30 Jan 2026 — https://csrc.nist.gov/pubs/sp/800/218/r1/ipd , opened 2026-10-16, WebFetch — Quote: "Comments Due: January 30, 2026 (public comment period is CLOSED)"

### Contradictions
- None found. (ZAP tags lag: see next section.)

### Inferences
- Level choice (mine, from the ASVS "which level" text and L1/L2 counts): single-user app holding John's own health data is low in user-count risk but high in data sensitivity. Take all 70 L1 items, plus L2 items in V6 (auth/MFA), V7 (session), V8 (authorization), V11/V14 (crypto, data protection), V13 (config, secrets) and V16 (logging). Skip V10 OAuth unless the app is an OAuth provider, V17 WebRTC, and L3.
- The agent should generate its checklist from the ASVS CSV filtered by chapter and level, not hand-copy it.
- CIS and SSDF give little checkable value for the app itself: CIS applies to the VM and containers; SSDF is a process catalogue with no pass/fail tests.

### Gaps
- WSTG 4.2 date and "5.0 still developing" come from the project page; not checked whether a 5.0 pre-release is tagged in the repo.
- CIS benchmark PDFs are SecureSuite-gated for tailoring; whether a plain PDF download is free was not confirmed (page does not say). Free Docker-side alternative (docker-bench-security) not opened.
- Agentic Top 10 full text of items not read; only the contents list and the blog summary came through search highlights.

## Tool-checkable vs judgement mapping
### Takeaway
Roughly: ASVS L1 is about half tool-checkable (headers, cookies, TLS, injection patterns, dependency age) and half LLM-with-evidence (authorization on every route, session handling); business-logic, threat-model and documentation items need human sign-off. Published mappings are partial: Semgrep rules carry OWASP Top 10 2025 tags and some carry old ASVS 4.0 tags; ZAP tags are Top 10 2021 and WSTG 4.2; MASTG ships Semgrep rules tagged with MASVS controls; no complete ASVS 5.0-to-tool mapping was found. Confidence: medium.

### Cited findings
- Semgrep rules repo carries OWASP 2025 tags: in a clone, 1,489 rule files contain `owasp:` and 628 `A..:2025` entries (my grep, commit 17e31e1, 2026-10-15) — https://github.com/semgrep/semgrep-rules javascript/express/security/cors-misconfiguration.yaml:10 — Quote: "- A07:2025 - Authentication Failures"
- Some Semgrep rules map to the old ASVS 4.0, not 5.0 (106 files mention asvs) — https://github.com/semgrep/semgrep-rules kotlin/lang/security/weak-rsa.yaml:14-16 (commit 17e31e1) — Quote: "control_id: 6.2.5 Insecure Algorithm"
- MASTG repo contains 51 rule files in `rules/`, Semgrep-style with MASVS control in the message — https://github.com/OWASP/owasp-mastg rules/mastg-android-backup-manifest.yml:10 (commit 02ffd85, 2026-09-30) — Quote: "message: \"[MASVS-STORAGE-2] allowBackup detected as $ARG.\""
- ZAP alert tags cover Top 10 2017 and 2021 only and WSTG v4.2; also a HIPAA tag — https://www.zaproxy.org/docs/desktop/addons/common-library/alerttags/ , opened 2026-10-16, WebFetch — Quote: "OWASP Top 10 (2021) - Tags representing the risks/vulnerabilities from the 2021 OWASP Top 10 list."
- ZAP Automation Framework runs from one YAML file and the active-scan job can select rules by alert tag — https://www.zaproxy.org/docs/automate/automation-framework/ (Exa highlights) and https://www.zaproxy.org/docs/desktop/addons/automation-framework/job-ascan/ , both search-highlight only; see Gaps. (No quote claimed.)
- ASVS L1 text itself marks which items are black-box testable: "Level 1 is not necessarily penetration testable by an external tester without internal access to documentation or code" — 5.0/en/0x03-What-is-the-ASVS.md:97 (commit 2b47a9d), read 2026-10-16 — Quote: "Level 1 is not necessarily penetration testable by an external tester without internal access to documentation or code"

### Contradictions
- Semgrep tags Top 10 2025 (cors-misconfiguration.yaml:10) while ZAP tags stop at 2021 (alerttags page). Not a conflict of fact: tooling lags by edition. The engineer should map by CWE or by ASVS chapter, not by Top 10 year.

### Inferences
Split of the 70 ASVS L1 items (my read of the 5.0 CSV, `req_id` list; counts approximate):
- T (tool): V1.2.4 parameterized queries, V1.2.5 OS command injection, V1.3.2 no eval, V1.5.1 XXE (Semgrep/CodeQL); V3.3.1 cookie Secure, V3.4.1 HSTS, V3.4.2 CORS fixed origin, V4.1.1 Content-Type, V12.1.1/V12.2.1/V12.2.2 TLS (ZAP baseline, header and TLS checkers, curl); V13.4.1 no .git served (curl); V11.3.1/V11.3.2/V11.4.1 crypto primitives (Semgrep); V15.2.1 dependencies within remediation window (osv-scanner, npm audit, pip-audit); V4.4.1 WSS; V6.2.6 password field type (Playwright DOM check). About 20 items.
- L (LLM reviewer with file:line evidence, or a written test): V8.2.1/V8.2.2/V8.3.1 authorization on every route and object (best done as per-route tests with a second user), V7.2.4/V7.4.1 session rotation and logout (Playwright tests), V6.2.x password policy, V6.3.1 brute-force controls, V9.1.x token validation, V15.3.1 response field minimization, V5.x uploads, V2.2.1/V2.2.2 server-side validation, V14.2.1 no secrets in URLs. About 35 items.
- H (human): V2.3.1 business-flow order, V2.1.1/V6.1.1/V8.1.1/V15.1.1 documentation items (the LLM can write them, John must accept), plus anything needing an external pentest. About 15 items.
- ASVS 5.0 chapter V15 and V16 carry the process-flavoured items (documentation, logging); these are mostly L (check that the artifact exists) not T.

### Gaps
- No published ASVS 5.0 to Semgrep or ZAP rule mapping found in this session (only the legacy `asvs:` metadata above); not searched beyond the repos opened.
- ZAP Automation Framework and alert-tag selection: only search highlights seen for the automation pages; the alerttags page was opened.
- OWASP's own tool mapping (e.g. ASVS "tool" column) not found in the CSV: columns are chapter, section, req_id, description, L only.

## Minimal checklists per project type
### Takeaway
Below: 20 web, 15 integrations/workflows, 15 mobile and 12 LLM items, each with a pass criterion and T/L/H. They are my synthesis from the cited frameworks; every item names its source control. Confidence: medium (judgement on selection).

### Cited findings
- Source controls are those listed above: ASVS 5.0 req_ids from `docs_en/..._en.csv` (commit 2b47a9d); API Top 10 2023 names; LLM Top 10 2025; Agentic Top 10 2026; MASVS groups. MASTG Android rules exist for allowBackup, exported content providers and biometrics (file list `rules/`, commit 02ffd85) — https://github.com/OWASP/owasp-mastg rules/mastg-android-content-provider-exported.yml (listing), read 2026-10-16 — Quote: "mastg-android-content-provider-exported.yml"

### Contradictions
- None found.

### Inferences
**A. Web app with auth and health data (ASVS 5.0)**
1. T. Gitleaks on repo and history finds 0 secrets (V13).
2. T. Dependency audit (osv-scanner/npm audit) shows 0 high or critical unfixed (V15.2.1, A03:2025).
3. T. Semgrep with the p/owasp-top-ten and language packs: 0 findings at ERROR (V1.2.4, V1.2.5, V1.3.2, V11.x).
4. T. Response headers: HSTS with max-age >= 1 year, CSP present, X-Content-Type-Options nosniff, Content-Type correct (V3.4.1, V4.1.1).
5. T. Cookies: Secure, HttpOnly, SameSite, __Host- prefix on the session cookie (V3.3.1).
6. T. TLS 1.2+ only, valid public cert, HTTP redirects to HTTPS (V12.1.1, V12.2.x).
7. T. `/.git/`, `.env`, source maps with secrets return 404 on the deployed URL (V13.4.1).
8. T. CORS: Allow-Origin is a fixed value, never `*` with credentials (V3.4.2).
9. T. ZAP baseline against staging: 0 medium or high alerts (passive; unauthenticated).
10. L/T. Every route and object access has a negative test: logged-out gets 401; second user gets 403/404 on first user's records (V8.2.1, V8.2.2, A01:2025).
11. T. Login rate limit test: Nth failed attempt is throttled (V6.3.1).
12. T. Session is new after login, dead after logout, rejected after server-side revoke (V7.2.4, V7.4.1).
13. L. Passwords: length >= 8 (15 recommended), no composition rules, breached-list check (V6.2.1-V6.2.5); or passkey/MFA only, which the engineer should prefer.
14. L. Health records encrypted at rest by the database or disk, key not in the repo; backups encrypted (V14, V11).
15. T. No health data in URLs, logs or analytics payloads: grep logs of a test run for seeded canary values (V14.2.1, V16).
16. T. Error responses contain no stack traces or SQL (A10:2025, V16).
17. L. Server-side validation exists for every input that reaches storage (V2.2.1, V2.2.2).
18. T. Playwright e2e: HTML-escaping canary `<script>` in every text field renders as text (V1.2.1, V3.2.2).
19. T. Backup restore test succeeds and is documented (not an ASVS item; engineer reliability).
20. H. Threat model and data-flow note reviewed by John; decision on retention and deletion (A06:2025).

**B. Integrations, webhooks, n8n workflows (API Top 10 2023, ASVS V4/V13)**
1. T. Every inbound webhook verifies a signature or shared secret: a request with a bad signature gets 401 (API2, API10).
2. T. Replay test: same signed payload with an old timestamp is rejected.
3. T. Gitleaks on workflow JSON exports: 0 credentials inline; secrets only as n8n credential references.
4. T. n8n instance not on a public port without auth; `curl` from outside shows auth wall (API8; n8n audit available via its public API per registry row).
5. L. Each outbound call's host comes from a fixed allowlist, not from user input (API7 SSRF).
6. T. Third-party API responses are schema-validated before use (API10): a malformed fixture fails safely.
7. T. Rate limits and payload size caps on public endpoints (API4): oversized request gets 413, burst gets 429.
8. L. Per-object authorization on every API route (API1, API5), tested with two principals.
9. T. OpenAPI spec exists and equals the routes mounted (API9 inventory): diff is empty.
10. L. API tokens are least-scope and listed with owner and expiry (API2).
11. T. Workflow error path alerts and does not leak payloads to the notification channel.
12. T. Idempotency: replay of the same event does not double-write.
13. L. Response bodies return only needed fields (API3, V15.3.1).
14. T. Pin or review third-party community nodes; list has 0 unreviewed (A03:2025, ASI04).
15. H. Decision on which workflows may act without human approval.

**C. Android app or PWA (MASVS, ASVS where web)**
1. T. MASTG Semgrep rules over the project: 0 ERROR; allowBackup false or backup rules exclude health data (MASVS-STORAGE-2).
2. T. No exported components without need (MASTG content-provider rule; MASVS-PLATFORM).
3. T. Network security config: cleartext traffic disabled (MASVS-NETWORK-1).
4. T. Gitleaks on APK sources; no API keys in resources (MASVS-STORAGE).
5. L. Health data stored only in app-private storage, encrypted with Keystore-backed key (MASVS-STORAGE-1, CRYPTO-1).
6. T. Logcat during a test run contains no seeded canary health values (MASVS-STORAGE-2).
7. L. Biometric gate uses a crypto-bound key, not a bare boolean callback (MASVS-AUTH; MASTG biometric rules exist).
8. T. Screenshot/recents protection (FLAG_SECURE) on health screens: grep plus emulator check (MASVS-PLATFORM-3).
9. T. Dependency audit as in A2.
10. T. PWA: service worker does not cache authenticated API responses; manifest scope correct; HTTPS only.
11. L. Permissions requested equal permissions used (MASVS-PRIVACY).
12. T. Release build is not debuggable, signed, with debug flags off (MASVS-CODE).
13. T. TLS config as A6 for the backend.
14. H. Resilience/anti-tamper (MASVS-RESILIENCE) is out of scope for a single-user personal app; John confirms the omission.
15. H. Physical-device, rooted-device behaviour needs a human test.

**D. LLM feature or agent (LLM Top 10 2025, Agentic 2026)**
1. L. Untrusted text (web pages, emails, documents) is never placed in the system prompt; it is delimited as data (LLM01, ASI01).
2. T. Injection fixture set: 10+ known injection strings in retrieved content; the test asserts no tool call outside the allowlist fires (LLM01, LLM06).
3. L. Tool list is minimal and each tool has least scope; destructive tools need human confirmation (LLM06, ASI02, ASI03).
4. T. Model output rendered as text or sanitized, never `innerHTML`/`eval`/shell (LLM05; Semgrep).
5. T. No secrets or health data in prompts, traces or the system prompt; canary grep (LLM02, LLM07).
6. T. Per-request and per-day token and spend caps enforced: a loop test stops at the cap (LLM10, ASI08).
7. L. Outbound network from the agent restricted to an allowlist (exfiltration path, ASI01).
8. L. Memory or RAG writes come from trusted sources only; stored content can be listed and purged (LLM04, LLM08, ASI06).
9. T. MCP servers and skills pinned to a version or commit, 0 unreviewed (LLM03, ASI04).
10. L. Health-related answers carry a source or a "not medical advice" boundary (LLM09).
11. T. Audit log of every tool call with arguments exists and has no PII beyond need (ASI10).
12. H. Which actions the agent may take unattended (ASI09, human-trust).

### Gaps
- Pass criteria are untested; thresholds (for example 15-character password) are ASVS wording or my choice and should be spiked.
- n8n has no OWASP-style catalogue; the n8n items come from API Top 10 and the n8n API row in the registry, not an n8n security benchmark (not searched).
- MASTG test-to-MASVS coverage count not computed; only the rule directory listing was read.

## Health data rules (US)
### Takeaway
HIPAA binds covered entities and business associates, which a personal app is not unless John builds it for a provider or insurer. The FTC Health Breach Notification Rule and Washington's My Health My Data Act cover apps that serve other consumers; for John's own single-user data they most plausibly do not apply, but the safe engineering stance is to build as if breach notice and consent logging were required. Not legal advice. Confidence: medium.

### Cited findings
- HIPAA applies only to defined entities — https://www.hhs.gov/hipaa/for-professionals/covered-entities/index.html , opened 2026-10-16, Exa fetch (WebFetch got 403) — Quote: "If an entity does not meet the definition of a covered entity or business associate, it does not have to comply with the HIPAA Rules."
- FTC finalized HBNR changes on 26 April 2024 to cover health apps not under HIPAA — https://www.ftc.gov/news-events/news/press-releases/2024/04/ftc-finalizes-changes-health-breach-notification-rule , opened via Exa search highlights only (see Gaps), 2026-10-16 — Quote: "Final rule underscores its application to health apps and similar technologies not covered by HIPAA"
- HBNR rule text: breach of security means acquisition without authorization of the individual — https://www.ecfr.gov/current/title-16/part-318 (via ecfr renderer API, WebFetch, 2026-10-16) — Quote: "acquisition of such information without the authorization of the individual"
- FTC rule page: coverage — https://www.ftc.gov/legal-library/browse/rules/health-breach-notification-rule , opened 2026-10-16, WebFetch — Quote: "vendors of personal health records and related entities"
- Washington My Health My Data Act: private right of action; in force 31 Mar 2024 for non-small businesses — https://www.atg.wa.gov/protecting-washingtonians-personal-health-data-and-privacy , opened 2026-10-16, WebFetch — Quote: "it is unlawful for anyone to sell or offer to sell consumer health data without first obtaining valid authorization."

### Contradictions
- None found.

### Inferences
- A user storing only their own data in software they run themselves is not a "vendor" serving consumers; none of the three regimes obviously attaches (my reading; not legal advice). If John ever lets another person (spouse, client) use the app, or sells it, HBNR (60-day notice, FTC notice at 500+ people) and MHMDA (consent, deletion, private suit) come into scope, and so would the engineer's tests.
- Engineering consequence: keep (a) a data inventory, (b) a deletion/export path, (c) an access log so a breach could be scoped, (d) no sharing of health data with analytics or ad SDKs. These are checkable: items A14-A16, C6, D5.
- Other state laws (e.g. Nevada, Connecticut health-data provisions) not researched.

### Gaps
- FTC press release read through Exa search highlights, not a full page open; the page itself was not opened with WebFetch. The business-guidance blog URL variant returned 404 for one guessed URL.
- Penalty amount per HBNR violation not confirmed from an opened page (only "subject to civil penalties" in a search highlight).
- HBNR effective date (60 days after Federal Register publication) from highlights only; exact date not confirmed.
- No state law other than Washington checked.

## Recommendation, alternatives, rejected, spikes
- Recommendation: adopt ASVS 5.0.0 (L1 + chosen L2 chapters) as the web master list, generated from the CSV, enforced by a pinned command set (Semgrep with OWASP tags, gitleaks, osv-scanner, ZAP baseline, curl header checks, Playwright negative tests), with the 12 to 20-item lists above as the first release gate. Use MASTG Semgrep rules for Android and the LLM/Agentic lists for LLM features.
- Alternatives: ASVS L2 whole (183 more items; mostly L-class, expensive); OWASP Top 10 2025 only (too coarse for pass/fail); WSTG 4.2 as a manual test script (old, 2020).
- Rejected: CIS full benchmark scoring for the app (VM only; PDFs gated); SSDF as test source (no pass/fail); MASVS-RESILIENCE for a single-user app; ZAP tags as a framework key (2021 only).
- Spike before building: (1) run Semgrep `p/owasp-top-ten` plus ASVS-tagged rules on a sample repo and count findings per ASVS chapter; (2) ZAP automation YAML in a container against a test app with a login; (3) two-user authorization test harness pattern in Playwright; (4) canary-in-logs grep for health data; (5) MASTG rules on a sample Android project.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| OWASP ASVS 5.0.0 | https://github.com/OWASP/ASVS | 345 requirements, L1 70 / L2 183 / L3 92, CSV/JSON exports | repo clone read-only | 2026-10-16 | Use as master checklist generator; L1 plus chosen L2 chapters |
| OWASP Top 10 2025 | https://top10.owasp.org/2025 | Ten risk categories A01-A10 | docs | 2026-10-16 | Use as vocabulary only, not pass/fail |
| OWASP API Security Top 10 2023 | https://api-security.owasp.org/editions/2023/en/0x00-header | Ten API risks | docs | 2026-10-16 | Use for integrations and webhooks |
| OWASP WSTG 4.2 | https://owasp.org/www-project-web-security-testing-guide/ | Manual web test guide, Dec 2020; 5.0 in development | docs | 2026-10-16 | Fallback reference for manual test scripts |
| OWASP LLM Top 10 2025 | https://genai.owasp.org/llm-top-10/ | LLM01-LLM10 | docs | 2026-10-16 | Use for LLM features |
| OWASP Agentic Top 10 2026 | https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/ | ASI01-ASI10, Dec 2025 | docs | 2026-10-16 | Use for the engineer's own agent design and any agent feature |
| OWASP MASVS / MASTG | https://github.com/OWASP/owasp-masvs ; https://github.com/OWASP/owasp-mastg | Mobile controls; MASTG has 51 Semgrep-style rules | repo, read only | 2026-10-16 | Use for Android; skip RESILIENCE |
| CIS Benchmarks (Ubuntu 24.04 v2.0.0, 26.04 v1.0.0, Docker 1.9.0) | https://www.cisecurity.org/cis-benchmarks | Hardening checklists | docs, PDF gated by form | 2026-10-16 | Use selectively for the VM; do not gate app work on it |
| NIST SSDF SP 800-218 (1.1; Rev 1 draft 2025-12-17) | https://csrc.nist.gov/pubs/sp/800/218/r1/ipd | Secure development practice catalogue | docs | 2026-10-16 | Skip as test source; vocabulary only |
| Semgrep rules registry (tags) | https://github.com/semgrep/semgrep-rules | Rules with OWASP 2025 and some ASVS 4.0 metadata | CLI, local (not run) | 2026-10-16 | Use; spike coverage |
| ZAP alert tags / Automation Framework | https://www.zaproxy.org/docs/desktop/addons/common-library/alerttags/ | Rule tags Top 10 2017/2021, WSTG 4.2, HIPAA; YAML automation | local/container (not run) | 2026-10-16 | Use for baseline DAST; tags dated |
| FTC HBNR, HIPAA, WA MHMDA | https://www.ftc.gov/legal-library/browse/rules/health-breach-notification-rule | Legal regimes for health data | n/a | 2026-10-16 | Reference; not legal advice |
