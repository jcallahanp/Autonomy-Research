# Security testing and reports (Area 12) - digest
Source: research/findings/engineer-security.md; verification: 19 of 20 verified, 1 unverified (EASE 2024 per-tool attribution, E30; corrected in the findings, not load-bearing)

## Decision
- Layered, file-based protocol: deterministic tools decide the gate, an evidence-bound LLM review adds findings, a human decides the residue (Summary; Q11, confidence medium).
- Master checklist: OWASP ASVS 5.0.0 (May 2025) at L1 plus chosen L2 chapters, generated from its CSV/JSON exports (E1, E3, E4); add API Top 10 2023 for integrations (E7), MASVS/MASTG for Android (E11), LLM Top 10 2025 and Agentic Top 10 2026 for LLM features (E9, E10, E124). No ASVS 5.0-to-tool mapping exists (Open q 12).
- Free core stack: Semgrep CE, Bandit or Ruff `S`, OSV-Scanner plus pip-audit or `npm audit`, gitleaks `--redact`, Socket free on npm PRs, Dependabot alerts, ZAP baseline on John's own staging only, Checkov for IaC, Lynis on the VM (Q11; E25, E32, E34, E37, E39, E44, E49, E35, E54, E57, E61). SAST is a tripwire, not an audit: 55-96 % of flagged vulnerable files are flagged again after the fix (E29, Exa highlights).
- Pin every scanner, Action, MCP server, skill and n8n community node by version plus checksum or SHA, after the March 2026 Trivy compromise (E41, E42, Exa highlights; E119); never auto-enable a project `.mcp.json` in CI (E117).
- LLM review: `/security-review` per PR touching auth/data/config, Claude Security plugin per milestone, run blind to SAST output (E70, E92), accepted only with file:line, repro or failing test and scope, because benchmarks show low precision (E82, E84) and runs vary (E139). LLM-only findings warn and ticket; never the sole gate.
- Gates (worker inference, not sourced as a rule): block merge and deploy on new Critical/High deterministic findings, any secret, any failing auth test; exceptions carry owner, reason, expiry max 90 days (Q7; pattern from E145-E147). Enforced by the existing Stop/TaskCompleted done-gate hook (E154).
- Reports: WSTG reporting structure as `REPORT.md` (E127-E130) plus a one-page `BRIEF.md`; three states per area, never "secure"; footer "not a penetration test" and "absence of findings is not evidence of absence" (Q9, worker inference; E131).
- The engineer itself holds the lethal trifecta, so defences are architectural: read-only untrusted-input subagents, plan-then-execute for privileged work, sandbox egress allowlist, pinned MCP with `tools/list` hash (E114, E121, E123, E125); `-p` shows no trust or MCP prompt (E110).

## Alternatives and rejected
- Opengrep - alternative - LGPL fork at v1.100.0 with a clean licence, own rules (E21, E24).
- Grype or a pinned checksum-verified Trivy binary - alternative for container/filesystem SCA (E43, E41).
- TruffleHog verified-only - alternative - AGPL, local use (E46).
- GitHub Secret Protection - optional paid - $19 per active committer per month (E28, E36, Exa highlights).
- CodeQL - kept for public repos only (E26).
- ASVS L2 whole; WSTG 4.2 as manual script; DefectDojo self-hosted; GitHub code scanning merge protection; Nuclei on own hosts - alternatives (Q11; E8, E141, E146, E59).
- claude-code-security-review Action - alternative on trusted PRs only, warn never gate; not hardened against injection (E74, E137).
- OpenAI Codex Security - alternative second model family; paid OpenAI key, price unverified (E79, Exa only, not cloned).
- CodeQL on private repos - rejected - needs Code Security, $30 per active committer per month (E27, E28).
- trivy-action / setup-trivy by tag - rejected - compromised (E41).
- TruffleHog unverified default mode - rejected - low precision in SecretBench (E47; worker inference on the figure).
- ZAP active scans or Nuclei against third-party SaaS - rejected (Q11).
- Single "is this secure?" prompt; LLM review as sole gate; blocking on unreproduced LLM findings - rejected (E82).
- Aardvark/Codex Security or CodeMender as primary - rejected - not Claude, paid or enterprise, price unverified (E76, E81).
- CVSS 4.0 on LLM-found custom-code issues - rejected - severity not risk (E133, E134); single "secure" or percentage score - rejected.
- CIS full benchmark for the app (VM only); SSDF as test source; MASVS-RESILIENCE; ZAP tags as framework key (2021 only); OWASP Top 10 2025 alone as pass/fail - rejected (E12, E13, E6; Q11).

## Stack
| Tool | What it does here | Where it runs | Cost | Evidence |
|---|---|---|---|---|
| OWASP ASVS 5.0.0 CSV | Generated master checklist, L1 + chosen L2 | repo `security/` | free | E1-E5 |
| Semgrep CE + `p/owasp-top-ten` | Pattern SAST with `--baseline-commit` | local, CI | free; rules licence internal non-SaaS use | E20, E25 |
| Bandit or Ruff `S` | Python SAST | local, CI | free | E32, E34 |
| OSV-Scanner, pip-audit / `npm audit` | Dependency CVEs, SARIF, dated ignores | local, CI | free | E37-E39 |
| gitleaks `--redact` | Secret scan, pre-commit and CI, baseline | local, CI | free (MIT) | E44, E45 |
| Socket free | Malware/typosquat/install-script PR checks (npm) | GitHub app | $0, 1,000 scans/month | E49, E50 |
| Dependabot alerts | Vulnerable-dependency alerts | GitHub | free on private repos per features page | E35 |
| ZAP baseline | Passive DAST, IGNORE/WARN/FAIL config | Docker, CI, own staging only | free | E54, E62 |
| Checkov | IaC, Dockerfile, compose scan | local, CI | free | E57 |
| Lynis; Docker Bench if Docker | VM host audit | Ubuntu VM | free | E61, E60 |
| Playwright + curl tests | Two-user authz, sessions, XSS canary, headers, Access JWT | CI | free | Q11; E101, E102 |
| `/security-review`; Claude Security plugin | LLM diff review per PR; multi-agent scan per milestone | Claude Code session | counts against plan usage; no published price | E70, E71, E149, E150 |
| n8n hardening env vars | SSRF protection (off by default), block env access, exclude nodes | VM | free | E108, E109 |

## Setup steps
| Step | Automated or John | How it is verified |
|---|---|---|
| 1. Generate `security/` folder: ASVS CSV-filtered checklist, project-type list, `findings.json`, dated `allowlist.md`, `REPORT.md`/`BRIEF.md` skeletons | Automated | Files present; checklist row count per chapter |
| 2. Pin every scanner by version + checksum, every Action by full SHA | Automated | Checksum check in CI; no mutable tags (Q3) |
| 3. gitleaks pre-commit and CI with `--redact` | Automated | Spike 1 (report redaction) |
| 4. Semgrep, Bandit/Ruff, OSV-Scanner/pip-audit with baselines in CI | Automated | Spike 1-2 (offline rules, no login; open q 18) |
| 5. Install Socket free GitHub app; enable Dependabot alerts | Not stated in findings who does it; likely John if an app install needs UI consent (digest reading, unverified) | Alert/PR comment appears on a test PR |
| 6. Per-repo fine-grained tokens; `permissions.deny` on secret paths | Token creation: John (setup list per R11); deny rules: automated | Spike 8 (`claude -p` honours deny) |
| 7. Hooks: done-gate checks (red gate, no repro, no scope, expired exception); protect `.claude/settings*`, hooks, CI workflows | Automated | Spike 7 (exit 2 vs JSON block, open q 20) |
| 8. Pin MCP servers and hash `tools/list` | Automated | Hash mismatch fails session start (re-prompt behaviour unverified, open q 22) |
| 9. n8n hardening vars, version floor vs advisories; Lynis, Docker Bench on VM | Automated | Env vars set; version >= patched floor (ranges unresolved, open q 5, 29) |
| 10. Weekly rescan job (Routines or Actions cron) for new CVEs and expired exceptions | Automated | Job run log |
| 11. Threat model, retention/deletion decision (A20), which workflows act unattended (B15) | **John** | Recorded decision in repo |
| 12. Seeded-flaw fixture repo as the skill's regression eval | Automated | Recall drop fails the plugin eval (Implications 4) |

## Repo composition
- Skill: `security-review` whose output schema is the evidence contract (file:line, CWE/risk id, four-level severity, repro or failing test, observed vs expected, scope) (Implications 1).
- Template: `security/` per project repo with generated checklist, pinned versions, baselines, `findings.json`, `allowlist.md`, SARIF/JSON per tool, `REPORT.md`, `BRIEF.md` (Implications 2; Q11).
- Hooks: Stop/TaskCompleted done-gate gains three checks (E154); hooks blocking edits to `.claude/settings*`, hooks and CI workflows (Q6).
- Agents: read-only, no-secret, no-outbound subagents for research and inbound-text triage returning structured JSON; privileged work from a plan fixed before untrusted input (Q6, CaMeL as design reference only, E123).
- Scripts/CI: weekly rescan; checksum-verified tool install; `findings.json` replaces DefectDojo for one user (not spiked, Q7).
- Fixture: seeded-flaw repo (unsigned webhook, SSRF fetch, logged token) as eval (spike 6).
- MCP: pinned versions plus `tools/list` hash; no auto-enabled project `.mcp.json` in CI (E117, E119).
- Superpowers/Beads/Ralph: not discussed in this findings file.

## Spikes
| Spike | Probe (what to run) | Pass criterion |
|---|---|---|
| 1 | Each core tool once on one of John's repos | Findings and triage minutes recorded; gitleaks output redacted; Semgrep rules work offline without login in CI; Lynis report parses; Socket covers Python (yes/no) |
| 2 | Semgrep `p/owasp-top-ten` + ASVS-tagged rules on a sample repo | Findings counted per ASVS chapter |
| 3 | ZAP Automation Framework YAML in a container vs a test app with login | Authenticated baseline completes with JSON report |
| 4 | Playwright two-user authorization harness; canary-in-logs grep | Cross-user access test fails on a seeded bug; canary health value found or absent in logs as expected |
| 5 | MASTG rules on a sample Android project | Rules run and map to MASVS ids |
| 6 | Seeded repo through `/security-review` and the Claude Security plugin, tokens via OpenTelemetry | Catches and false positives counted; token cost of a diff review and a milestone audit measured |
| 7 | Hook or CI check on review reports and `findings.json` | Rejects report lacking file:line + repro; fails deploy on red gate or expired exception (exit 2 vs JSON block settled) |
| 8 | `claude -p` on the cloud VM reading a denied secret path | Read is refused |
| 9 | gitleaks vs TruffleHog (verified) on John's git history | Precision contradiction (E47 vs E48) settled for his repos |
| 10 | Webhook four-case tests vs real WHOOP and Withings test events (joins engineer-deploy spike 6) | All four cases behave as designed per provider |
| 11 | GitHub merge protection on John's private-repo plan | Required check blocks a red merge (or shown unavailable) |
| 12 | Fetch PTES and NIST SP 800-115 text; read n8n GHSA for CVE-2026-21858 ranges | Report checklist sourced; affected range settled |

## Requirements served
- R20: concrete pass/fail tests per project type, gates, remediation with regression test, retest status, WSTG-shaped report with scope, method, findings, severity, remediation and a "not assured" list (Q7, Q9, Q11).
- R17: done-gate hook rejects findings without repro and "clean" without scope; gitleaks covers "no secret committed" (Implications 1; E44, E154).
- R16: deterministic gates give the pass/fail that self-merge needs; LLM-only findings never block (Q7).
- R14: exceptions and the human residue (threat model, unattended workflows) route to John as decisions (Q11 Human lines).
- R10: health-data legal context and "build as if notice and consent applied" stance: data inventory, deletion/export path, access log, no analytics SDKs (Q10; not legal advice).
- R19: tool candidates logged with verdicts (Tools evaluated table).
- R22: one-page `BRIEF.md` per security report for John (Q9).
- Q4: every finding and "clean" verdict carries tool output, repro and commit (Q9).
- Q6: paid options priced: CodeQL/Code Security $30, Secret Protection $19 per active committer per month (E28, Exa highlights).
- Q7: keeps engineer permissions separate from R20; adds trifecta split as the risk disclosure (Q6).

## GTM scenario
- Scan as-is: gitleaks on n8n workflow exports and the repo; n8n version floor and hardening vars checked against advisories (Q11 type 2; E103-E109).
- Fix Attio tables and views: Attio writes are privileged work run from a plan fixed before untrusted input is read (Q6); Attio webhooks deduped on event id, since Attio signs the body only (E95).
- Set up Clay workflows: gap.
- Clean data: gap (beyond approval gates on irreversible actions, Q6; deleting data is a hard gate per requirements).
- Finish tooling: pinned n8n community nodes and MCP servers (Q3); Outreach: gap.

## Tensions
- Requirements Q7 allows broad permissions for the engineer; this area says never `bypassPermissions` unattended where untrusted input is read (E113) and requires a sandbox egress allowlist (E125). Any area that runs the engineer unattended in bypass mode conflicts with this.
- `-p` sessions show no trust or MCP approval prompt (E110), and a malicious repo setting once leaked API keys before trust (E111): unattended runs (R15) depend on the pinning and hooks, whose enforcement (exit 2 vs JSON block, `tools/list` re-prompt) is unverified (open q 20, 22).
- The done-gate builds on engineer-context.md:118 (E154) and the deploy matrix on engineer-deploy.md:425-431 (E155); gate enforcement before deploy is cross-facet and unspiked (spike 7).
- R16 self-merge vs GitHub merge protection: code scanning on private repos needs paid Code Security (E27); whether merge protection works on John's plan is spike 11.
- Gate thresholds, SLA days (Medium 30, Low 90) and the 90-day exception cap are worker numbers, not sourced (Q7).
- LLM-review and much tooling evidence is Exa page text or highlights (source-strength caveat); Trivy incident details (E41) and the $19/$30 prices (E28, E36) are Exa highlights; "$5 to $25" per scan is search-only and excluded (open q 7).
- Claude Security plugin cost: one run used 189 subagents over two hours (E149) and counts against plan usage (E71); no dollar figure published (E150); effect on John's Max plan unmeasured.
- Semgrep rules licence limits use to internal, non-competing, non-SaaS contexts (E20, Exa highlights); digest reading: this may matter if the engineer is later handed to other people (G8), which favours Opengrep.
- n8n CVE-2026-21858 affected range and Git-node fixed versions unresolved (open q 5, 29); "use the higher numbers until re-read".
- Unverified: Socket Python coverage, Dependabot free-on-private beyond the features page, GitHub secret scanning on personal private repos (open q 16); Lynis report path (open q 9).
- John's code and VM were not inspected, so which project tests apply is unconfirmed (Implications 5).

## Open for John
- Threat model and health-data retention/deletion decision (A20).
- Which n8n workflows and LLM-feature actions may run unattended (B15; type 4 Human).
- Whether to pay for GitHub Secret Protection ($19) or Code Security ($30) per active committer per month (E28), or stay free.
- Accepting each exception (owner is John; expiry, compensating control) (Q7).
- Whether the health app stays single-user; another user brings FTC HBNR and Washington MHMDA into scope (Q10, not legal advice).
