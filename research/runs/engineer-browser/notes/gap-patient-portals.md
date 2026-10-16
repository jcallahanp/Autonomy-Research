# Blood-work and patient portals: API, aggregator or browser

Brief: Find how the engineer can fetch John's blood-work results into his FastAPI/Postgres health app with least manual work and acceptable privacy risk.
Run: research/runs/engineer-browser/PLAN.md

Dates: all pages opened 2026-10-16 with Exa web_fetch_exa unless noted. Connectors: Parallel was not used (Exa only); WebFetch not used.

## US lab and portal landscape (Quest, Labcorp, MyChart, Function Health)

### Takeaway
No lab or DTC service offers John a personal API key. Every one offers a logged-in, manual PDF download (Labcorp "Official Report", Function "My Documents" PDF) and Quest offers an Apple Health feed; none offers CSV. The practical machine-readable routes are the Apple Health export (FHIR JSON for clinical records) or an aggregator. Confidence: medium-high.

### Cited findings
- Labcorp lets a signed-in patient download the doctor-identical report, typically as PDF — https://patient.labcorp.com/help-center/q-and-a/3000/2, opened 2026-10-16, Exa fetch — Quote: "The Official Report is the same document shared with your doctor."
- Labcorp Official Report downloads as PDF from web or app — same URL — Quote: "The report will download to your computer (typically as a PDF)."
- Quest MyQuest is the patient channel; its results page lists no API or CSV export, only the app, doctor copies, and Apple Health — https://www.questdiagnostics.com/patients/test-results, opened 2026-10-16, Exa fetch — Quote: "We offer integrated results through Apple Health."
- Function Health (draws at Quest) exposes results as a member-initiated PDF download; no API is mentioned on its FAQ — https://www.functionhealth.com/faq, opened 2026-10-16, Exa fetch — Quote: "Once your results are ready, you can log in and download them as a PDF to share with your healthcare provider."
- Function Health labs are Quest sites — same URL — Quote: "We partner with Quest for easily accessible labs (2,000+ locations across the US)"
- Function lets members connect wearables but only as inbound apps — same URL — Quote: "You can log into Function and connect supported apps to sync your health data"
- Apple Health "Export All Health Data" produces export.zip whose export.xml has ClinicalRecord elements pointing at per-record FHIR JSON files — https://www.johngoldin.com/blog/apple-health-export/2020-02-apple-health-export1/index.en.html, opened via Exa search highlight only (2020 blog, not re-fetched) — Quote: "resourceFilePath that contains the path to a json dataset in the Apple Health Export/clinical records folder"
- An open-source parser already turns that export into lab CSV/JSON (tomhallmain/health_data_parser) and another loads lab DiagnosticReport files into Postgres (trumpetsherald/HealthKitGrafana) — search highlights only (repos not opened): see Gaps.

### Contradictions
- None found.

### Inferences
- Because Quest feeds Apple Health and Function draws at Quest, an Apple Health clinical-records export is the lowest-friction structured path for Quest and Labcorp results if John has an iPhone and has linked the lab (my inference; Labcorp-to-Apple link not verified).

### Gaps
- Whether Quest/MyQuest or Labcorp offer an official patient FHIR endpoint: no official page found. Fasten's source code appeared to carry a Quest FHIR client (DeepWiki excerpt), but git clone of fasten-sources failed (needs GitHub credentials), so not cited.
- MyQuest download/ToS text: only the Quest FAQ was opened; the MyQuest terms of use were not found.
- Whether John has an iPhone, which lab his blood work uses, and whether it was ordered by a doctor or DTC: unknown; ask John.
- Apple Health Records supported-institution list and iOS 2026 export format changes: not opened (the 2020 blog is the only export source and is old).

## Patient access APIs (Cures Act, Epic, Apple, Health Connect, Blue Button)

### Takeaway
The law gives John the right and Epic gives a self-service route, but registering one's own SMART app only reaches Epic-based health systems, each of which is a separate customer endpoint; it does not reach Quest or Labcorp. Android Health Connect medical records is real but still experimental and is a phone-side store, not a server API. Blue Button was not researched. Confidence: medium.

### Cited findings
- ONC certification rules say any individual can authorize apps of choice without extra steps — https://healthit.gov/certification-health-it/conditions-ccg/application-programming-interfaces/, opened via Exa search highlight (page not re-fetched) — Quote: "any individual can authorize apps of their choice to receive their health data without any additional or out-of-band steps, or any other preconditions."
- Same page: for patient-chosen apps no vetting or BAA is generally needed — Quote: "For third-party applications chosen by individuals to facilitate their access to their electronic health information (EHI) held by actors, there would not be a need for a business associate agreement"
- Epic: self-service registration, no Epic relationship required — https://open.epic.com/DeveloperResources, opened 2026-10-16, Exa fetch — Quote: "no special relationship is required to develop or deploy an app."
- Epic is federated: connection is per health system — same URL — Quote: "There is no central Epic endpoint. To exchange data with organizations using Epic, you'll need to establish connections directly with individual organizations."
- Epic patient-authorized apps have extra distribution options (TEFCA IAS, auto-distribution) — same URL — Quote: "If you are deploying an automatically-distributed patient-authorized app, you can connect directly to customer endpoints listed here."
- Epic says patient apps are common — https://open.epic.com/DesignOverview, via Exa search highlight — Quote: "over 500 patient-authorized health apps have connected to the Epic community in 2025."
- Epic registers an app by form and issues production and non-production client IDs; non-production data is sandbox-only — https://fhir.epic.com/Documentation?docId=patient_facing_apps, via Exa search highlight — Quote: "the website creates an app record in the Epic database and assigns the app production and non-production client IDs."
- Epic sandbox must not hold real data — https://fhir.epic.com/Documentation?docId=patientfacingfhirapps, opened 2026-10-16, Exa fetch — Quote: "You agree not to put individually identifiable information in any Epic-provided sandboxes."
- Health Connect Medical Records (FHIR, includes laboratory permission) is experimental, needs Android 16 SDK, Play policy not finished; page updated 2026-09-22 — https://developer.android.com/health-and-fitness/health-connect/medical-records, opened 2026-10-16, Exa fetch — Quote: "The Play Policy for Medical Records access is still being developed, and apps may need to meet additional requirements before they can be released on the Play Store."
- Health Connect read permission for labs exists — https://developer.android.com/health-and-fitness/health-connect/medical-records/read-data, search highlight — Quote: "android.permission.health.READ_MEDICAL_DATA_LABORATORY_RESULTS"

### Contradictions
- None found.

### Inferences
- A solo Epic SMART app is feasible only for Epic-hosted portals (MyChart at John's doctor or hospital). It needs an Epic developer account (human), a patient-facing OAuth redirect that John completes in a browser with his MyChart login and 2FA (human, once per health system, then refresh tokens), and a hosted redirect URI. It will not fetch Quest or Labcorp results unless the health system's Epic copies them in (often true for ordered labs, unverified).
- Health Connect needs an Android app on John's phone to read and forward; too heavy for one blood panel (my judgement).

### Gaps
- Epic auto-distribution criteria and whether a one-person, no-company developer is accepted for production: the criteria page text was not read in full; "Patient-Facing Consumer Health Apps playbook" not opened.
- Apple HealthKit clinical-records API requires an iOS app; Apple's current Health Records docs were not opened (only a 2018 WWDC excerpt).
- CMS Blue Button 2.0: not researched (claims for Medicare beneficiaries, not lab results; likely irrelevant for John unless on Medicare).
- TEFCA IAS requires identity proofing by CLEAR or ID.me (cited under Aggregators); no direct-to-individual developer route verified.

## Aggregators (1up, Health Gorilla, Particle, Flexpa, Metriport, Fasten)

### Takeaway
No aggregator is built for one person pulling his own record. Flexpa has no free live tier ($20,000/year minimum); Fasten Connect is commercial and its self-hosted Fasten OnPrem is archived and cannot import from providers; Health Gorilla, Particle and Metriport are sales-gated. Confidence: medium-high.

### Cited findings
- Fasten OnPrem is archived (GPL-3.0) and cannot sync with providers — https://github.com/fastenhealth/fasten-onprem/, opened 2026-10-16, Exa fetch — Quote: "Fasten Onprem is not able to import data from healthcare providers directly. You can only use this application to manually enter data, or upload FHIR Bundles"
- Same page shows status — Quote: "Status: ARCHIVED"
- Fasten Connect (commercial) issues test and live keys; live uses patient portal login or TEFCA — https://docs.connect.fastenhealth.com/quickstart, search highlight — Quote: "Free developer sandbox" (fastenhealth.com) and "Test mode only connects to sandbox environments and synthetic or vendor-provided test data."
- Fasten TEFCA IAS has extra live fees and needs CLEAR or ID.me identity proofing — https://docs.connect.fastenhealth.com/guides/tefca-ias, opened 2026-10-16, Exa fetch — Quote: "There are additional fees involved with TEFCA IAS in `live` mode."
- Flexpa live access: no free plan, demo intake first — https://www.flexpa.com/docs/guides/getting-started, opened 2026-10-16, Exa fetch — Quote: "Start at flexpa.com/demo."
- Flexpa pricing starts at $20,000/year; includes a hosted MCP server from the $50,000 tier (add-on $5,000 on Startup) — https://www.flexpa.com/pricing, via Exa search highlight — Quote: "Startup For teams validating their first integration.$20,000/year"
- Flexpa docs: "We do not have a free plan for live mode" — https://www.flexpa.com/docs/guides/getting-started, search highlight — Quote: "We do not have a free plan for live mode, but our pricing is publicly available."
- 1upHealth Patient Access is a payer-side product requiring app vetting; a third-party price listing shows pay-as-you-go FHIR queries — https://docs.1up.health/docs/get-started/third-party-apps, search highlight — Quote: "Developer requests production access."; price listing (saasworthy.com, third-party, unverified): "1,000 FREE API queries / month".
- Metriport open source (licence "Other"), customers are treatment-purpose organizations; cloud is quote-based — https://github.com/metriport/metriport/, search highlight — Quote: "Teams across care delivery, value-based programs, and health tech platforms build on Metriport"; 2023 Fierce piece: "Right now, Metriport customers are only those who are authorized to access patient data for treatment purposes."
- Health Gorilla sandbox needs a contact request; has an IAS service — https://developer.healthgorilla.com/docs/sandbox-environment, search highlight — Quote: "Submit a request via our contact page."
- Particle Health: free portal signup gets sandbox, "see if you qualify for production access" — https://portal.particlehealth.com/signup/, search highlight — Quote: "See if you qualify for production access that will allow you to pull live patient data."

### Contradictions
- Metriport blog says anyone can run its code; the same post says "a company could independently run our open source code, but would face non-code challenges like network agreements" — https://www.metriport.com/blog/open-source-healthcares-structural-data-advantage (search highlight). Self-hosting is therefore not a practical solo route.

### Inferences
- For a single user the aggregator route is ruled out on price and eligibility (Flexpa $20,000/year; others sales-gated), not on technology. The only plausibly cheap exception is Fasten Connect or 1up pay-as-you-go if they accept a one-person account; unverified, and Fasten live pricing is not published.
- Flexpa MCP and Fasten TEFCA flows show the target shape (consent in browser, then agent reads FHIR) but each requires a human identity-proofing step by John (CLEAR or ID.me).

### Gaps
- Fasten Connect live pricing and whether an individual can open a live account: no public price found; ask support (human).
- 1up pricing is from a third-party listing (saasworthy), not 1up's own page.
- Health Gorilla and Particle price: only a 2020 blog excerpt ("starts at $500/month for provider access ... free for patients") seen; no current pricing opened.
- Most aggregator claims rest on search highlights, not full-page fetches; re-open before relying on them.

## Browser fallback and privacy

### Takeaway
Logging into Labcorp, MyQuest or Function with an automated browser is a licensed-for-personal-use grey zone: Labcorp's agreement bans robots and scrapers without written permission, so the engineer should not log in unattended. A manual download by John, or an attended session where John does the login, is within terms; an agent that only parses the PDF after John saves it is not accessing the portal. Confidence: medium.

### Cited findings
- Labcorp User Agreement (updated 2026-07-22) bans automated collection — https://www.labcorp.com/compliance/privacy/privacy-notice/online-services-user-agreement, opened 2026-10-16, Exa fetch and search highlight — Quote: "use any automated means to collect information or Content from, index, crawl, or otherwise access the Online Services, including robots, spiders, or scrapers, without our prior written permission"
- Same agreement allows personal single downloads — Quote: "You may print or download a single copy of Content for your personal, non-commercial, informational use"
- Same agreement bans credential stuffing and bypassing authentication — Quote: "password mining, credential stuffing, or any other unauthorized means"
- A Labcorp document viewer separately prohibits automated trawling — https://www.labcorp.com/labcorp-spotlight-viewer-terms-conditions, search highlight — Quote: "use manual or automated means to trawl, mine, scrape, frame, or mirror the Services or Content"
- Earlier run note records the hand-over pattern (John logs in, profile chmod 700, excluded from git, in permissions.deny) — /home/user/Autonomy-Research/research/runs/engineer-browser/notes/sessions-and-hosting.md:179 — Quote: "(2) John logs in manually (including Google, with his own 2FA, so no script touches Google's login)"
- Same note says portal 2FA type is unknown — sessions-and-hosting.md:66 — Quote: "Whether Attio, Clay, n8n, Outreach and the blood-work portal offer TOTP, passkey-only or SMS 2FA for John's accounts: unknown; ask John."
- Epic forbids real PHI in its sandbox, so real-data tests must go through John's own live login — see Epic finding above.

### Contradictions
- None found. Quest and Function terms of use were not opened, so the Labcorp rule cannot be assumed to apply to them.

### Inferences
- Risk of a persistent logged-in medical browser profile on the engineer VM: the profile (cookies) is a standing credential for PHI that a prompt-injected page could drive. Recommended mitigation (mine, built on the earlier note): no persistent portal profile; John downloads the PDF himself; the engineer sees only a dropbox folder outside git.
- Best-effort parsing of lab PDFs (text-layer PDFs from Labcorp/Quest) is a local, no-login step; the engineer can build and test the parser on synthetic PDFs.

### Gaps
- Quest/MyQuest and Function terms of use not found/opened.
- 2FA types for MyQuest, Labcorp Patient, Function: unknown (ask John).
- HIPAA or other law on storing PHI on a personal VM: not researched.

## Recommendation (order: API/FHIR, aggregator, browser plus PDF, manual upload)

### Takeaway
Do not build the FHIR or aggregator path for one blood panel a few times a year. Recommended: (1) manual upload by John to a gitignored inbox with an engineer-built, tested local parser for Labcorp, Quest and Function PDFs; (2) if John has an iPhone, an Apple Health export (zip) dropped in the same inbox and parsed locally into Postgres; (3) an Epic SMART-on-FHIR patient app only if his results live in a MyChart-using system and he wants automation; (4) aggregators and unattended browser logins rejected. Confidence: medium.

### Cited findings
See the sections above; no new sources.

### Contradictions
- None found.

### Inferences
- Outcome quality: official PDFs and Apple clinical records both carry LOINC-coded values only in the FHIR path; PDFs need a parser with a verification step (reconcile counts and reference ranges against the PDF). John effort: one download per draw. Cost: zero.
- Human-only steps: (a) John signs in to the lab or portal and clicks download (2FA, ID); (b) for Epic: create the developer account, and complete MyChart OAuth consent per health system; (c) any TEFCA IAS or CLEAR/ID.me identity proofing; (d) any aggregator contract or BAA; (e) deciding where PHI may live (disk, backups, never git).
- Engineer can do alone: DB schema, ingest endpoint, PDF and FHIR-JSON parsers on synthetic fixtures, a CI check that no health file is tracked by git (permissions.deny and .gitignore).

### Gaps
- Spike before building: (1) get one real Labcorp and one Quest/Function PDF from John and verify the text layer parses; (2) confirm Apple Health clinical-records export includes Quest/Labcorp labs for John; (3) ask John which portal/lab he uses and whether it is MyChart; (4) if automation is wanted, ask Fasten/1up whether an individual account is allowed and the price.

## Alternatives and rejected
- Alternative: Epic SMART app for MyChart-hosted labs; Fasten Connect or 1up only if pricing/eligibility are confirmed for an individual.
- Rejected: Flexpa ($20,000/year, no free live tier); Metriport self-host (network agreements, treatment-purpose customers); Health Gorilla and Particle (sales-gated, provider-oriented); Fasten OnPrem as a puller (archived, cannot import); Health Connect (experimental, needs an Android app); unattended Playwright login to Labcorp (agreement bans robots; PHI session on VM).

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Fasten OnPrem | https://github.com/fastenhealth/fasten-onprem/ | Self-hosted GPL-3.0 FHIR record viewer; archived; no provider import, FHIR Bundle upload only | Docker, self-hosted | 2026-10-16 | Reject as puller; archived |
| Fasten Connect | https://docs.connect.fastenhealth.com/quickstart | Commercial patient-authorized records API (50,000+ systems, TEFCA add-on fees); free sandbox, live price unpublished | hosted | 2026-10-16 | Fallback; ask about individual live account |
| Flexpa | https://www.flexpa.com/pricing | Patient-consented FHIR API with hosted MCP; $20,000-$900,000+/year, no free live | hosted | 2026-10-16 | Reject: price |
| 1upHealth Patient Access / API | https://docs.1up.health/docs/get-started/third-party-apps | Payer patient-access FHIR with app vetting; third-party list shows pay-as-you-go | hosted | 2026-10-16 (search highlight) | Fallback only; price unverified |
| Metriport | https://github.com/metriport/metriport/ | Open-source clinician-facing record exchange; quote-based cloud | self-host / hosted | 2026-10-16 (search highlight) | Reject for solo use |
| Health Gorilla | https://developer.healthgorilla.com/docs/sandbox-environment | Sales-gated FHIR/IAS API | hosted | 2026-10-16 (search highlight) | Reject for solo use |
| Particle Health | https://portal.particlehealth.com/signup/ | Free sandbox; production by qualification | hosted | 2026-10-16 (search highlight) | Reject for solo use |
| Epic on FHIR (open.epic) patient-facing SMART app | https://open.epic.com/DeveloperResources | Self-service client IDs; per-health-system patient OAuth | hosted (Epic customers) | 2026-10-16 | Fallback for MyChart labs; John does consent |
| Android Health Connect Medical Records | https://developer.android.com/health-and-fitness/health-connect/medical-records | On-phone FHIR store incl. lab read permission; experimental | Android 16 | 2026-10-16 | Skip |
| Apple Health export (clinical records) | https://www.johngoldin.com/blog/apple-health-export/2020-02-apple-health-export1/index.en.html | export.zip with FHIR JSON clinical records | iPhone, then local parse | 2026-10-16 (2020 blog, search highlight) | Use if John has iPhone; spike |
| tomhallmain/health_data_parser | https://github.com/tomhallmain/health_data_parser | Parses Apple Health clinical lab records to CSV/JSON | local Python (not run) | 2026-10-16 (search highlight) | Reference only; do not run on real data unvetted |
| trumpetsherald/HealthKitGrafana | https://github.com/trumpetsherald/HealthKitGrafana | Loads Apple Health export and Labcorp lab files into Postgres | Docker (not run) | 2026-10-16 (search highlight) | Reference only |
