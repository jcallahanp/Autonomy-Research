# Security tooling an agent can run, and its noise

Brief: Choose the free or cheap security tools an autonomous Claude Code engineer runs on John's repos and deployments, with licence, setup, CI fit and false-positive evidence.
Run: research/runs/engineer-security/PLAN.md

Clone note: repos were cloned read-only with `git clone --depth 1` into /tmp/tmp.B1XCntP8tm on 2026-10-16; no code was run. Commit shas and dates below are HEAD of each clone. Where a source is "Exa highlights" the text came from the Exa search tool's page highlights for that URL, not a separate full fetch.

## Static analysis

### Takeaway
Use Semgrep CE (LGPL-2.1 engine; Semgrep-maintained rules under a non-open-source "internal use, no competing SaaS" licence, fine for John's own repos) for custom and framework rules, Bandit and Ruff `S` for Python, and CodeQL only on public repos (private repos need a paid GitHub Code Security licence at $30 per active committer per month). Opengrep is an LGPL-2.1 fork (cloned 2026-10-15, active) and the licence-clean fallback. Independent studies show SAST finds only a small share of real vulnerabilities (about 5-27 percent per tool) and that most alerts survive the fix, so treat SAST as a cheap tripwire, not an audit. Confidence: medium-high.

### Cited findings
- Semgrep-maintained rules moved to Semgrep Rules License v1.0 in Dec 2024; limits use to internal, non-competing, non-SaaS contexts; individuals and companies using rules internally are unaffected — https://semgrep.dev/blog/2024/important-updates-to-semgrep-oss, opened 2026-10-16, Exa highlights — Quote: "Semgrep-maintained rules are now licensed under Semgrep Rules License v.1.0, so that they're available only for internal, non-competing, and non-SaaS contexts."
- Engine is LGPL 2.1; rules licence "is not an open source license"; Opengrep forked at v1.100.0 under LGPL 2.1; Semgrep platform free for 10 contributors and 10 private repos — https://docs.semgrep.dev/faq/comparisons/opengrep, opened 2026-10-16, WebFetch — Quote: "forked from Semgrep Community Edition (CE) at v1.100.0 and licensed under LGPL 2.1."
- Same page on the free platform tier — https://docs.semgrep.dev/faq/comparisons/opengrep, opened 2026-10-16, WebFetch — Quote: "covers Semgrep Code and Supply Chain for up to 10 contributors and 10 private repositories"
- Opengrep was launched by a vendor consortium in response to the rules licence change; claim that features moved to paid is community commentary — https://www.infoq.com/news/2025/02/semgrep-forked-opengrep/, opened 2026-10-16, Exa highlights — Quote: "TL;DR: If you're using Semgrep without bundling and reselling it, you should be unaffected by our recent changes."
- Semgrep CE engine repo is LGPL; HEAD 51602ad dated 2026-10-14; Opengrep HEAD 6f7c930 dated 2026-10-15, LGPL 2.1; Opengrep emits SARIF — https://github.com/opengrep/opengrep README.md:178 (commit 6f7c930), read 2026-10-16, grep — Quote: "opengrep scan --sarif-output=sarif.json -f rules code"
- Semgrep CLI has a baseline option so only new findings report — https://github.com/semgrep/semgrep cli/src/semgrep/commands/scan.py:130 (commit 51602ad), read 2026-10-16, grep — Quote: "--baseline-commit",
- CodeQL CLI licence: free only on open-source codebases (and research) unless under a paid GitHub Advanced Security licence — https://github.com/github/codeql-cli-binaries/blob/main/LICENSE.md, opened 2026-10-16, WebFetch — Quote: "if your use of the Software is under a paid customer license for GitHub Advanced Security."
- Code scanning on private repos needs Code Security — https://docs.github.com/en/code-security/code-scanning/introduction-to-code-scanning/about-code-scanning, opened 2026-10-16, WebFetch — Quote: "If you want to use code scanning on private repositories, you need a GitHub Code Security license."
- GitHub Code Security $30 and Secret Protection $19 per active committer per month from 1 April 2025, now also for Team plan — https://github.blog/changelog/2025-03-04-introducing-github-secret-protection-and-github-code-security/, opened 2026-10-16, Exa highlights — Quote: "Code Security will be available for $30 per month per active committer"
- Real-vulnerability benchmark of Semgrep CE, CodeQL, Bandit, gosec: per-file recall 4.6-19.2 percent; 55-96 percent of flagged vulnerable files are flagged again after the fix; Bandit medium+ filter lowers recall from 13.9 to 9.3 percent — https://www.maxor-global.com/papers/flagged-on-both-sides.en.pdf (undated preprint), opened 2026-10-16, Exa highlights — Quote: "a majority of the flagged vulnerable files (55–96 %) are flagged again after the fix, so paired detection is only 0.9–3.3 %."
- Production Java study (EASE 2024): CodeQL 15.3, Semgrep 15.9, FindSecBugs 26.5, Snyk Code 11.2 percent detection; custom Semgrep rules reached 44.7 percent — https://dl.acm.org/doi/fullHtml/10.1145/3661167.3661262, opened 2026-10-16, Exa highlights — Quote: "By editing the configuration of Semgrep, we were able to increase its detection rate from 15.3% (26/170) to 44.7% (76/170)"
- CodeQL on 258 embedded C/C++ projects: 34 percent false-positive rate per report, concentrated in outlier rules; 20 percent of rules gave over 60 percent of false positives — https://dl.acm.org/doi/full/10.1145/3728923 (2025), opened 2026-10-16, Exa highlights — Quote: "20% of rules contribute to more than 60% of false positives."
- Bandit supports baseline JSON comparison and Apache-2.0 licence; HEAD 68ebe11 2026-09-21 — https://github.com/PyCQA/bandit doc/source/man/bandit.rst:74 (commit 68ebe11), read 2026-10-16, grep — Quote: "-b BASELINE, --baseline BASELINE"
- ESLint security plugin (Apache-2.0, HEAD d1ba1cd 2026-10-01) states its own noise — https://github.com/eslint-community/eslint-plugin-security README.md:7 (commit d1ba1cd), read 2026-10-16, grep — Quote: "finds a lot of false positives which need triage by a human."
- Ruff (MIT, HEAD 7610cd2 2026-10-16) ports flake8-bandit as its `S` rules — https://github.com/astral-sh/ruff README.md:335 (commit 7610cd2), read 2026-10-16, grep — Quote: "[flake8-bandit](https://pypi.org/project/flake8-bandit/)"

### Contradictions
- Opengrep fork rationale: community says features moved behind paid licence (InfoQ, https://www.infoq.com/news/2025/02/semgrep-forked-opengrep/) while Semgrep says only the rules licence changed and end users are unaffected. For John (internal use only) it does not matter.
- CodeQL false-positive picture: 34 percent per-report FP on C/C++ (ACM 3728923) versus 96 percent sampled precision on the same dataset in the same paper's Table 2 (per-repo sample); both come from one paper and differ by sampling unit.

### Inferences
- Because John's repos are private and personal, CodeQL costs $30 per month per committer (the repo owner, plus any bot committer counted as an active committer) and is not justified against Semgrep CE + Bandit/Ruff at zero cost; use CodeQL only on public repos (my inference from the licence and pricing findings).
- Low recall in every benchmark means a clean SAST run must never be reported as "secure"; the auditor should say "no findings from rule set X" (my inference).

### Gaps
- Ruff S-rule count and per-rule noise reports: no page opened beyond the README line.
- Semgrep-specific false-positive rate for p/default on typical Next.js or Python apps: no independent figure found.
- GitHub Pro personal-account code scanning for private repos: docs say Code Security licence needed; whether any personal-plan exception exists was not confirmed.

## Dependency and secret scanning

### Takeaway
Use OSV-Scanner (Apache-2.0, SARIF, `ignoreUntil` expiry) plus `pip-audit` and `npm audit` as lockfile checks, Dependabot alerts (free on private repos per GitHub's feature list) and Socket's free plan for new-package install-script/malware checks on pull requests. Use gitleaks (MIT; SARIF/JSON; baseline) as the default secret scanner; trufflehog (AGPL-3.0) only with verification off. GitHub secret scanning and push protection on a private personal repo require the paid $19 Secret Protection. Trivy and its CI action were compromised in March 2026: if used, pin by SHA and to the safe versions. Confidence: medium-high.

### Cited findings
- Dependabot alerts and other basics are available for private repos; secret scanning, push protection and code scanning need paid products for private repos — https://docs.github.com/en/code-security/getting-started/github-security-features, opened 2026-10-16, WebFetch — Quote: "Most of these features are available for public and private repositories."
- Secret Protection $19 and Code Security $30 per active committer per month; bots ignored — https://docs.github.com/en/billing/concepts/product-billing/github-advanced-security, opened 2026-10-16, Exa highlights — Quote: "GitHub App bots are ignored."
- OSV-Scanner emits SARIF v2.1.0 (Apache-2.0, HEAD f455353 2026-10-13) — https://github.com/google/osv-scanner docs/output.md:280 (commit f455353), read 2026-10-16, grep — Quote: "Outputs the result in the [SARIF](https://sarifweb.azurewebsites.net/) v2.1.0 format."
- OSV-Scanner config supports ignore entries with an expiry date — https://github.com/google/osv-scanner docs/configuration.md:34 (commit f455353), read 2026-10-16, grep — Quote: "# ignoreUntil = 2022-11-09 # Optional exception expiry date"
- pip-audit (Apache-2.0, HEAD 828e77a 2026-09-25) has JSON and other formats — https://github.com/pypa/pip-audit README.md:566 (commit 828e77a), read 2026-10-16, grep — Quote: "pip-audit -r requirements.txt --format=json"
- Trivy supports dated ignores in `.trivyignore` — https://github.com/aquasecurity/trivy docs/guide/configuration/filtering.md:291 (commit 9dd3e28), read 2026-10-16, grep — Quote: "CVE-2019-14697 exp:2023-01-01"
- Trivy compromise: malicious v0.69.4, 76 of 77 trivy-action tags force-pushed, 7 setup-trivy tags replaced, 2026-03-19; safe versions listed — https://github.com/aquasecurity/trivy/security/advisories/GHSA-69fq-xp46-6x23, opened 2026-10-16, Exa highlights — Quote: "Known safe versions include versions 0.69.2 and 0.69.3 of the Trivy binary, version 0.35.0 of trivy-action, and version 0.2.6 of setup-trivy."
- Hardening guidance after Trivy — https://www.wiz.io/blog/trivy-compromised-teampcp-supply-chain-attack, opened 2026-10-16, Exa highlights — Quote: "Pin GitHub Actions to full SHA hashes, not version tags."
- Grype (Apache-2.0, HEAD a402503 2026-10-15) and Trivy (Apache-2.0, HEAD 9dd3e28 2026-10-16) are both actively maintained — https://github.com/anchore/grype LICENSE (commit a402503), read 2026-10-16, git log — Quote: "Apache License Version 2.0, January 2004"
- Gitleaks (MIT, HEAD b58d3f1 2026-07-22) report formats include SARIF — https://github.com/gitleaks/gitleaks README.md:571 (commit b58d3f1), read 2026-10-16, grep — Quote: "[`json`](https://github.com/gitleaks/gitleaks/blob/master/testdata/expected/report/json_simple.json)"
- Gitleaks baseline: old findings in any prior report are ignored — https://github.com/gitleaks/gitleaks README.md:193 (commit b58d3f1), read 2026-10-16, grep — Quote: "gitleaks will ignore any old findings that are present in the baseline."
- TruffleHog licence is AGPL-3.0 since v3.0 — https://github.com/trufflesecurity/trufflehog README.md:900 (commit 31d7303), read 2026-10-16, grep — Quote: "Since v3.0, TruffleHog is released under a AGPL 3 license"
- Secret scanner benchmark SecretBench (818 repos): precision GitHub scanner 75, Gitleaks 46, TruffleHog 6 percent; recall Gitleaks 88, TruffleHog 52 percent; GitHub scanner recall 6 percent — https://arxiv.org/html/2307.00714 (2023), opened 2026-10-16, Exa highlights — Quote: "The top three tools based on precision are: GitHub Secret Scanner (75%), Gitleaks (46%), and Commercial X (25%)"
- ProwlBench (vendor-authored, 2026): gitleaks precision 0.931 recall 0.413; TruffleHog precision 0.940 recall 0.303 — https://github.com/Lercas/prowlbench, opened 2026-10-16, Exa highlights — Quote: "| gitleaks | 0.931 | 0.413 | 0.573 | 0.585 |"
- Socket Free plan: $0, 1 dev seat, 1,000 scans per month, unlimited private repos, block malicious packages, PR block/warn; GitHub Actions scanning not included — https://socket.dev/pricing, opened 2026-10-16, Exa highlights — Quote: "Free Stay secure as you build, solo or small team$0dev seat / monthscans / mo1,000"
- Socket detects install scripts, typosquats, known malware in PR comments (npm manifests) — https://docs.socket.dev/docs/socket-for-github, opened 2026-10-16, Exa highlights — Quote: "Detect potential typo squats ✅ Detect install scripts ✅ Detect telemetry ✅ Detect native code ✅ Detect known malware"
- Socket CLI is MIT, HEAD 766b1e6 2026-10-15 — https://github.com/SocketDev/socket-cli LICENSE (commit 766b1e6), read 2026-10-16, grep — Quote: "MIT License Copyright (c) 2022 Socket Inc"

### Contradictions
- SecretBench (2023, academic) puts TruffleHog precision at 6 percent, ProwlBench (2026, vendor-run, verified-results not scored) at 0.94. Different datasets and TruffleHog's verification step is what lowers noise in practice; settle with a spike on John's own history.

### Inferences
- A free GitHub account cannot run secret scanning or push protection on a private repo; gitleaks as a pre-commit hook plus CI step replaces it at zero cost (inference from the features page and gitleaks formats).
- Do not use trivy-action; run a pinned, checksum-verified Trivy binary at v0.69.3 or a later release checked against the advisory, or prefer OSV-Scanner + Grype for SCA (my inference after the March 2026 incident).

### Gaps
- Dependabot alerts page itself did not state pricing (about-dependabot-alerts fetch returned none); the free-on-private claim rests on the features page only.
- GitHub secret scanning on personal private repos: Free/Pro plan behaviour not separately confirmed beyond the features page.
- Socket install-script blocking for pip/uv not confirmed (docs show npm manifests only).
- osv-scanner, grype and pip-audit noise/false-positive rates: no independent study opened.
- Date of Trivy's current release after the incident not checked.

## Dynamic and infrastructure scanning

### Takeaway
ZAP (Apache-2.0, still open source; "ZAP by Checkmarx" since Sept 2024; left OWASP in 2023) baseline scan is passive-only and safe for headless CI against a staging URL; the API scan and full scan are active and must only hit John's own staging. Checkov (Apache-2.0, SARIF, baseline) or Trivy config for Terraform/Dockerfiles; Lynis (GPL) for the Ubuntu VM; Docker Bench for hosts. Nuclei (MIT) is useful for known-CVE and misconfiguration checks on John's own hosts, with severity filters. Confidence: medium.

### Cited findings
- ZAP joined Checkmarx in Sept 2024, stays open source under Apache v2 — https://www.zaproxy.org/blog/2024-09-24-zap-has-joined-forces-with-checkmarx/, opened 2026-10-16, WebFetch — Quote: "ZAP will stay under the control of the ZAP Core Team, remain open source, and stay licensed under Apache v2."
- ZAP is no longer an OWASP project (since Aug 2023) — https://www.zaproxy.org/docs/nowaspzap/, opened 2026-10-16, Exa highlights — Quote: "ZAP is no longer an OWASP project, and has not been one since August 2023."
- ZAP baseline: spider about 1 minute then passive scan only, config file to IGNORE/WARN/FAIL rules, JSON/XML/MD/HTML reports — https://www.zaproxy.org/docs/docker/baseline-scan/, opened 2026-10-16, Exa highlights — Quote: "-J report_json    file to write the full ZAP JSON document"
- ZAP packaged scans: baseline, full (active), API (OpenAPI/GraphQL active scan); Automation Framework YAML is the recommended route — https://www.zaproxy.org/docs/docker/about/, opened 2026-10-16, Exa highlights — Quote: "API Scan which performs an active scan against APIs defined by OpenAPI, or GraphQL (post 2.9.0)"
- ZAP repo HEAD e06ba5e dated 2026-10-15, Apache-2.0 — https://github.com/zaproxy/zaproxy LICENSE (commit e06ba5e), read 2026-10-16, git log — Quote: "Apache License Version 2.0, January 2004"
- Checkov (Apache-2.0, HEAD 7a6782e 2026-10-13) outputs SARIF/JSON/JUnit and has baseline files — https://github.com/bridgecrewio/checkov docs/2.Basics/CLI Command Reference.md:53 (commit 7a6782e), read 2026-10-16, grep — Quote: "Alongside outputting the findings, save all results to .checkov.baseline file so future runs will not re-flag the same noise."
- Trivy config scanning supports inline dated ignores in IaC files — https://github.com/aquasecurity/trivy docs/guide/scanner/misconfiguration/config/config.md:229 (commit 9dd3e28), read 2026-10-16, grep — Quote: "#trivy:ignore:aws-s3-enable-logging:exp:2024-03-10"
- Nuclei (MIT, HEAD a151a1d 2026-10-14) JSONL output and severity exclusion — https://github.com/projectdiscovery/nuclei README.md:198 (commit a151a1d), read 2026-10-16, grep — Quote: "-es, -exclude-severity value[]     templates to exclude based on severity."
- Docker Bench for Security (Apache-2.0, HEAD 154869d 2026-06-04) writes a JSON log — https://github.com/docker/docker-bench-security README.md:133 (commit 154869d), read 2026-10-16, grep — Quote: "docker-bench-security.log.json"
- Lynis is GPL, HEAD 9319416 2026-09-16; logs to /var/log/lynis.log — https://github.com/CISOfy/lynis README.md:111 (commit 9319416), read 2026-10-16, grep — Quote: "debugging information (/var/log/lynis.log)"

### Contradictions
- None found.

### Inferences
- Lynis writes a machine-readable report file (`/var/log/lynis-report.dat`) in my recollection; not verified from the clone, so the auditor parser for Lynis is a spike item.
- Docker Bench targets Docker host hardening; relevant only if John runs Docker on the VM (my inference).
- Active ZAP/Nuclei scans against third-party SaaS (Attio, Clay, Vercel-hosted domains owned by others) are out of bounds; run only against John's own staging (my inference).

### Gaps
- Nuclei false-positive rates and template-licence status: not opened.
- Lynis report format and noise: not verified beyond the log line.
- ZAP API-scan false-positive reports: no independent study opened.
- No Checkov or Trivy-config comparison study opened.
- Checkmarx KICS action compromise (Wiz update) mentioned in the same Wiz page: not examined; relevant if KICS is considered.

## Minimal stack and noise control

### Takeaway
Per project type: (1) Python: Ruff `S` + Bandit, Semgrep CE (`p/python` plus a few custom rules), pip-audit or OSV-Scanner, gitleaks. (2) TS/Next.js on Vercel/Supabase: Semgrep CE (`p/typescript`, `p/nextjs`), ESLint security plugin only if already linting, `npm audit` + OSV-Scanner, Socket free on PRs, gitleaks, ZAP baseline on the preview URL. (3) n8n/infra on the Ubuntu VM: Checkov or Trivy config on Dockerfile/Terraform, Lynis, Docker Bench if Docker, gitleaks on workflow exports. All emit SARIF or JSON. Confidence: medium.

### Cited findings
- Baselines available as flags in gitleaks, Bandit, Checkov, Semgrep (--baseline-commit); dated expiries in OSV-Scanner `ignoreUntil` and Trivy `exp:` — sources cited above (gitleaks README.md:193; bandit.rst:74; checkov CLI Command Reference.md:53; scan.py:130; osv-scanner configuration.md:34; trivy filtering.md:291).
- ZAP baseline config files can set rules to IGNORE/WARN/FAIL — https://www.zaproxy.org/docs/docker/baseline-scan/, opened 2026-10-16, Exa highlights — Quote: "Edit the file and ... WARN to IGNORE ... ignore rule or FAIL to fail"
- Filtering Bandit to medium+ lowers recall (13.9 to 9.3 percent) but barely changes paired detection — Maxor preprint above — Quote: "restricting Bandit to medium-or-higher findings lowers its recall from 13.9 % to 9.3 %"

### Contradictions
- None found.

### Inferences
- Noise policy (mine): (a) first run on a repo creates a baseline file committed to the repo; only new findings fail the gate; (b) fail on high/critical SCA with a fix available and on any verified/high-confidence secret; report medium and below without failing; (c) every allowlist entry carries an owner reason and an expiry (`ignoreUntil`, Trivy `exp:`), and a weekly job lists expired entries; gitleaks and Semgrep have no native expiry so keep a dated `allowlist.md` the auditor checks; (d) one aggregate SARIF/JSON per tool stored under `security/reports/` for the auditor; (e) the agent never auto-dismisses a finding, it proposes the allowlist diff for John.
- Secret reports must be written redacted (`gitleaks --redact`), already a registry spike.
- Pin every scanner by version and checksum or SHA, never `latest` or a mutable tag, given the March 2026 Trivy incident.

### Gaps
- Typical alert volume per tool on John's actual repos: unknown until a spike.
- Whether Semgrep `p/default` registry rules fetched at runtime need a Semgrep login or telemetry off in CI: not checked.

## Recommendation, alternatives, rejections, spikes

- Recommend: Semgrep CE + Bandit/Ruff S (Python) + OSV-Scanner + gitleaks as the always-on core; add Socket Free on npm PRs, Dependabot alerts, ZAP baseline on staging, Checkov for IaC/Dockerfiles, Lynis for the VM.
- Alternatives: Opengrep instead of Semgrep CE (clean licence, same syntax, supply your own rules); Grype/Trivy for container and filesystem SCA (pin; avoid trivy-action); trufflehog with `--results=verified` (AGPL; read-only local use); GitHub Secret Protection $19/committer/month if John wants push protection and accepts cost; CodeQL for public repos only.
- Rejected: CodeQL on private repos ($30/committer/month, licence-restricted otherwise); trivy-action and setup-trivy by tag (compromised March 2026); unverified TruffleHog default mode (6 percent precision in SecretBench); running ZAP active scans or Nuclei against third-party SaaS.
- Spike before building: run each core tool once on one of John's repos and record findings per tool and triage minutes; check redaction of gitleaks reports; confirm Semgrep registry rules run offline/no-login in CI; confirm Lynis report parseable; confirm Socket free covers Python.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Semgrep CE | https://github.com/semgrep/semgrep | LGPL-2.1 pattern SAST, SARIF/JSON; rules under Semgrep Rules License v1.0 (internal use only) | local, CI | 2026-10-16 | Use; internal use only is fine for John |
| Opengrep | https://github.com/opengrep/opengrep | LGPL-2.1 fork of Semgrep CE at v1.100.0, SARIF | local, CI | 2026-10-16 | Fallback; clean licence |
| CodeQL | https://docs.github.com/en/code-security/code-scanning/introduction-to-code-scanning/about-code-scanning | Dataflow SAST; CLI licence open-source only unless paid GHAS; private repos need $30/committer/month | GitHub Actions, CLI | 2026-10-16 | Public repos only; reject for private |
| Bandit | https://github.com/PyCQA/bandit | Python SAST, Apache-2.0, baseline | local, CI | 2026-10-16 | Use for Python |
| Ruff S rules | https://github.com/astral-sh/ruff | MIT linter with flake8-bandit port | local, CI | 2026-10-16 | Use if Ruff already used |
| eslint-plugin-security | https://github.com/eslint-community/eslint-plugin-security | Apache-2.0 JS security lint, self-declared noisy | local, CI | 2026-10-16 | Optional; noisy |
| OSV-Scanner | https://github.com/google/osv-scanner | Apache-2.0 lockfile SCA, SARIF, ignoreUntil | local, CI | 2026-10-16 | Use |
| pip-audit | https://github.com/pypa/pip-audit | Apache-2.0 Python SCA, JSON | local, CI | 2026-10-16 | Use for Python |
| Trivy | https://github.com/aquasecurity/trivy | Apache-2.0 SCA, image, IaC; compromised March 2026 (CVE-2026-33634) | local, CI | 2026-10-16 | Fallback; pin version/SHA, no trivy-action |
| Grype | https://github.com/anchore/grype | Apache-2.0 SCA/image scanner | local, CI | 2026-10-16 | Alternative to Trivy |
| Dependabot alerts | https://docs.github.com/en/code-security/getting-started/github-security-features | Free alerts on private repos | GitHub | 2026-10-16 | Use |
| Socket (free) | https://socket.dev/pricing | Malicious package and install-script PR checks; 1,000 scans/month free | GitHub app, CLI (MIT) | 2026-10-16 | Use for npm; verify Python |
| gitleaks | https://github.com/gitleaks/gitleaks | MIT secret scanner, SARIF/JSON, baseline | local, CI | 2026-10-16 | Use (default) |
| TruffleHog | https://github.com/trufflesecurity/trufflehog | AGPL-3.0 secret scanner with verification | local, CI | 2026-10-16 | Fallback; verified-only |
| GitHub Secret Protection | https://github.com/security/plans | Secret scanning + push protection; $19/active committer/month | GitHub | 2026-10-16 | Optional paid; not needed |
| ZAP | https://github.com/zaproxy/zaproxy | Apache-2.0 DAST; baseline passive, API/full active; Checkmarx-backed | Docker, CI | 2026-10-16 | Use baseline on own staging |
| Nuclei | https://github.com/projectdiscovery/nuclei | MIT template scanner, JSONL | local, CI | 2026-10-16 | Fallback; own hosts only |
| Checkov | https://github.com/bridgecrewio/checkov | Apache-2.0 IaC/Dockerfile scanner, SARIF, baseline | local, CI | 2026-10-16 | Use for IaC |
| Lynis | https://github.com/CISOfy/lynis | GPL host audit | Ubuntu VM | 2026-10-16 | Use; spike report parsing |
| Docker Bench for Security | https://github.com/docker/docker-bench-security | Apache-2.0 Docker host checks, JSON log | Docker host | 2026-10-16 | Use if Docker on VM |
