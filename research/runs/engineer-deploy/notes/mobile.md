# Android path and the iOS deferral

Brief: Find the most autonomous way for a Claude Code engineer to ship John's apps to his own Android phone (and later the Play Store), and confirm what iOS would take.
Run: research/runs/engineer-deploy/PLAN.md

Method note: Parallel Search returned "Too Many Requests"; I used WebFetch on primary pages and one Exa search. WebFetch returns model-summarised text; quotes below are the page sentences it reproduced between quotation marks.

## Android build paths
### Takeaway
Recommendation: PWA first (zero store, zero fee), then a thin native wrapper only where the app needs Android-only APIs (Health Connect, widgets, background work). The headless wrapper route is Capacitor or Expo built with Gradle/`eas build --local` on a Linux VM; Gradle needs no Android Studio. Confidence: medium (build-tool claims partly inferred).

### Cited findings
- Android apps build and sign headless with the Gradle wrapper, no Android Studio — https://developer.android.com/build/building-cmdline, opened 2026-10-16, WebFetch — Quote: "You do not need Android Studio to sign your app. You can sign your app from the command line, using `apksigner` for APKs or `jarsigner` for app bundles"
- Expo local builds run on Linux; you supply the Android SDK/NDK — https://docs.expo.dev/build-reference/local-builds/, opened 2026-10-16, WebFetch — Quote: "macOS and Linux are supported."
- EAS cloud free plan is 15 Android + 15 iOS builds, low-priority queue; paid from $19/month — https://expo.dev/pricing, opened 2026-10-16, WebFetch — Quote: "At peak times, you may experience wait times of 90+ minutes with the low-priority queue depending on demand."
- Capacitor Android is Android-Studio-centred; docs also allow command line — https://capacitorjs.com/docs/android, opened 2026-10-16, WebFetch — Quote: "either run your app on the command-line or with Android Studio."
- TWA wraps a PWA; same-developer check via Digital Asset Links; Bubblewrap is a Node CLI to build TWA projects (page last updated 2020-02-04) — https://developer.chrome.com/docs/android/trusted-web-activity/overview, opened 2026-10-16, WebFetch — Quote: "the app and the site it opens are expected to come from the same developer."
- Health Connect is a native Android SDK (Gradle dependency, manifest permissions); the page shows no web API — https://developer.android.com/health-and-fitness/health-connect/get-started, opened 2026-10-16, WebFetch — Quote: "Add the Health Connect SDK dependency in your module-level `build.gradle` file"
- PWA capability gaps on iOS vs Android (Background Sync, Web Bluetooth, NFC; Android PWA has them) — https://toimi.pro/blog/pwa-vs-native-app/ (third-party, dated 2026-10-03), opened via Exa highlights 2026-10-16 — Quote: "Background Sync | Yes (MDN) | No | Yes"

### Contradictions
- None found.

### Inferences
- Health Connect, home-screen widgets and reliable background sync cannot come from a PWA, so a wrapper is justified only when an app needs them (rests on the Health Connect and capability-table findings). Widgets: no source opened; treated as native-only from general knowledge, unverified.
- A PWA can run notifications and mic via standard web APIs on Android Chrome; I opened no page that states mic/notification support, so this is general knowledge.
- Flutter, React Native CLI and native Kotlin were not researched from opened pages. They build headless with Gradle by the same Android toolchain, but rewrite cost against a web-stack app makes them poor fits (my judgement).
- Ranking by outcome then John effort: (1) PWA, (2) Capacitor wrapping the same web code, (3) Expo/React Native only if a UI rewrite is wanted, (4) native Kotlin only for Health Connect-centred apps.

### Gaps
- No page opened for Flutter docs, React Native CLI, Capacitor headless Gradle build, Capacitor plugin for Health Connect, widget support, Bubblewrap's current README.
- Android SDK install on a headless VM/cloud session not verified; no spike.

## Distribution and Play account rules
### Takeaway
Own-phone distribution needs no Play account: `adb install` is explicitly exempt from 2026 developer verification. Play needs $25, government ID, an Android device check, and for post-2023 personal accounts a closed test of 12 testers for 14 days before production. Confidence: high on fee/testing, medium on verification details.

### Cited findings
- One-time $25 fee and ID requirements — https://support.google.com/googleplay/android-developer/answer/6112435, opened 2026-10-16, WebFetch — Quote: "There is a US$25 one-time registration fee that you can pay with the following credit or debit cards:"
- Personal accounts after 13 Nov 2023 have testing requirements; new personal accounts must verify an Android device via the Play Console mobile app — same URL — Quote: "must meet specific testing requirements before they can make their app available on Google Play."
- Closed test: 12 testers, 14 days — https://support.google.com/googleplay/android-developer/answer/14151465, opened 2026-10-16, WebFetch — Quote: "a minimum of 12 testers who have been opted in continuously for at least 14 days."
- Developer verification dates: protections begin 30 Sep 2026 in Brazil, Indonesia, Singapore, Thailand, global in 2027; limited distribution account for hobbyists (20 devices) — https://developer.android.com/developer-verification, opened 2026-10-16, WebFetch — Quote: "Effective September 30, 2026: Protections begin for users installing apps from participating stores in select regions on certified Android devices."
- ADB installs exempt; limited distribution account free, up to 20 devices; $25 for Full Distribution — https://developer.android.com/developer-verification/guides/faq, opened 2026-10-16, WebFetch — Quote: "As a developer, you are free to install apps without verification with ADB."
- Same FAQ — Quote: "This lets you share apps with up to 20 specific devices for testing and personal use at no cost and without ID verification."
- Firebase App Distribution: CLI, Gradle, fastlane upload; CI integration; pricing not on page — https://firebase.google.com/docs/app-distribution, opened 2026-10-16, WebFetch — Quote: "Automate distribution by integrating the CLI into continuous integration (CI) jobs."

### Contradictions
- None found. Note the verification page (dates) says the limited account "launch[es] in August" (2026 per page); I did not confirm whether it is live on 2026-10-16.

### Inferences
- John's single-phone case is covered by three free routes: PWA install, `adb install` over wireless debugging, or a limited distribution account. A sideloaded APK on a non-certified-region phone is likely outside the Sept 2026 enforcement regions, but his country is unknown to me.
- The 12-tester/14-day rule is a calendar delay (at least 14 days) and needs 12 real people opted in: a human-recruited step the engineer cannot do. Skip the Play Store until an app is worth that.

### Gaps
- Whether the 2026 advanced-flow waiting period affects a user installing a downloaded (non-ADB) APK; FAQ line says it "does not apply to ADB installs" but the full rule was not read.
- Firebase App Distribution price: not on the opened page.
- Google's "Play Console closed testing" page 14151465 could have changed since; read as summarised.

## Automation after account setup and signing keys
### Takeaway
After John creates the account, pays, verifies ID and creates the app, the engineer can build, sign and upload through a service account via EAS Submit or fastlane supply. Human-only: account creation, ID/device verification, tester recruitment, store listing and declarations, production promotion decision. Confidence: medium; sources disagree on whether the first upload must be manual.

### Cited findings
- EAS Submit first release goes to internal testing; service account key required; listing is not managed — https://docs.expo.dev/submit/android/, opened 2026-10-16, WebFetch — Quote: "EAS requires a Google Service Account key to submit on your behalf."
- EAS Submit does not do listing, and moving past internal needs Console work — https://docs.expo.dev/submit/introduction/, opened 2026-10-16, WebFetch — Quote: "To distribute beyond internal testing, finish the setup tasks in Play Console and promote the release."
- fastlane supply requires a manual first upload; can push listing text, screenshots, changelogs, binaries and promote tracks — https://docs.fastlane.tools/actions/upload_to_play_store/, opened 2026-10-16, WebFetch — Quote: "you'll need to set up your app manually first by uploading at least one build"
- Service account is created in Cloud Console and invited in Play Console Users & permissions; must be kept secure — https://developers.google.com/android-publisher/getting_started, opened 2026-10-16, WebFetch — Quote: "The service account credentials need to be securely managed"
- Play App Signing: Google holds app signing key; upload key loss is recoverable by reset request — https://support.google.com/googleplay/android-developer/answer/9842756, opened 2026-10-16, WebFetch — Quote: "If you lose your upload key or suspect that it was compromised, you are not locked out of your app."
- Upload key is an RSA 2048+ keystore you hold — same URL — Quote: "You use this key to sign your app bundle before uploading it to the Play Console."

### Contradictions
- Expo says the first `eas submit` works out of the box ("the default `eas submit` command works out of the box", https://docs.expo.dev/submit/android/) vs fastlane says one build must be uploaded manually first (https://docs.fastlane.tools/actions/upload_to_play_store/). Settle with a spike on a throwaway app; plan for a one-time manual `.aab` upload by John.

### Inferences
- Keep the upload keystore and the service-account JSON in the engineer's secret store (network-secret/vault), never in the repo; since Play App Signing allows an upload key reset, loss is recoverable but needs John to file the request in the Console (human step). The Publishing API getting-started page notes the service account must be used in a secure environment.
- The Publisher API edits/upload reference page returned 404, so API-level limits (edits, draft app status) are unverified; the app stays in draft until the listing is complete (Expo page).
- Submission to the store is John's hard gate: engineer can stage to internal track autonomously, John approves promotion to closed/production.

### Gaps
- Android Publisher API edits.bundles reference: 404 at https://developers.google.com/android-publisher/api-ref/rest/v3/edits/bundles/upload. Not read.
- Vault choice and Play-key backup procedure: no source opened beyond Play doc above.

## iOS deferral
### Takeaway
Defer iOS. It costs $99/year, needs macOS build (cloud: EAS or Codemagic), and an iOS PWA works only for push after Home Screen install. Deferral is sound; unlock by paying Apple and choosing a cloud macOS builder. Confidence: medium-high.

### Cited findings
- Apple Developer Program price — https://developer.apple.com/programs/whats-included/, opened 2026-10-16, WebFetch — Quote: "The Apple Developer Program is 99 USD per membership year, or in local currency where available."
- iOS web push needs iOS 16.4 and an installed Home Screen web app, triggered by user action — https://webkit.org/blog/13878/web-push-for-web-apps-on-ios-and-ipados/, opened 2026-10-16, WebFetch — Quote: "A web app that has been added to the Home Screen can request permission to receive push notifications"
- iOS 26: every site added to Home Screen opens as a web app; push still needs Home Screen web app — https://progressivewebapps.com/blog/the-state-of-progressive-web-apps-in-2026/ (dated 2026-09-25), via Exa highlights 2026-10-16 — Quote: "Web Push on iOS still requires a Home Screen web app, but any site can now become one."
- EU: Apple announced removing Home Screen web apps in iOS 17.4 beta, then reversed; they stay on WebKit — https://openpwa.net/reference/platforms/ios-by-version/ (dated 2026-10-05), via Exa highlights — Quote: "will continue to offer the existing Home Screen web apps capability in the EU"
- Codemagic free tier 500 macOS M2 minutes/month, then $0.095/min — https://codemagic.io/pricing/, opened 2026-10-16, WebFetch — Quote: "first 500 / month - $0, then $0.095 / minute"
- EAS Free plan includes iOS builds (15/month) — https://expo.dev/pricing (see above) — Quote: "15 Android and 15 iOS builds"
- App Store review risk for wrapped websites — https://toimi.pro/blog/pwa-vs-native-app/ (third-party), via Exa — Quote: "A thin wrapper around your store will likely ... rejected."

### Contradictions
- None found. (Apple's own EU page, https://developer.apple.com/support/apps-in-the-eu/, appeared in Exa highlights but I did not open it, and its web-app content was not in the excerpt.)

### Inferences
- iOS unlock path: pay $99, have John accept Apple terms and create an App Store Connect API key (human), build with EAS or Codemagic (no Mac needed), distribute via TestFlight. TestFlight and App Store Connect API automation not read from opened pages; treat as unverified.
- Meanwhile an iOS PWA with push is available if John ever opens it on an iPhone, no fee, but no Background Sync.

### Gaps
- Apple web push developer docs page returned only a title stub; WebKit blog used instead.
- TestFlight rules, EAS iOS credential automation, GitHub macOS runner pricing: not opened.
- Apple's EU page not opened.

## Final recommendation block
- Recommend: build every app as a PWA first; install on John's Android via Chrome; add Capacitor (Gradle, headless on Linux VM) only for apps needing Health Connect/widgets/background; sideload via `adb install` or Firebase App Distribution; no Play account until an app needs wide distribution.
- Alternatives: Expo/EAS (free 15 builds/month, `eas build --local` on Linux), Bubblewrap TWA for Play-listing a PWA, Flutter/RN/Kotlin.
- Rejected: native Kotlin or Flutter as default (rewrite cost); EAS paid plans (not needed); iOS now (cost, Mac, review risk).
- Spike before building: (1) `./gradlew assembleRelease` on the engineer VM with Android SDK; (2) first `eas submit` vs fastlane first-upload contradiction on a test app; (3) `adb` wireless install and PWA install on John's phone; (4) whether Health Connect is reachable from a Capacitor plugin.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Gradle wrapper (Android CLI build) | https://developer.android.com/build/building-cmdline | Headless build and sign APK/AAB, no Android Studio | Linux VM | 2026-10-16 | Use; spike SDK setup |
| Bubblewrap / Trusted Web Activity | https://developer.chrome.com/docs/android/trusted-web-activity/overview | Node CLI wraps PWA as Android app (page dated 2020) | Linux VM | 2026-10-16 | Fallback for Play-listing a PWA; README not opened |
| Capacitor | https://capacitorjs.com/docs/android | Wraps web app in Android WebView app; Android Studio centred, CLI allowed | Linux VM | 2026-10-16 | Use when native plugins needed; spike headless |
| Expo EAS Build / local build | https://docs.expo.dev/build-reference/local-builds/ | Cloud 15 free Android builds/month; `--local` on Linux | Expo cloud or VM | 2026-10-16 | Fallback if RN chosen |
| EAS Submit | https://docs.expo.dev/submit/android/ | Uploads .aab to internal track via service account | Expo cloud/CLI | 2026-10-16 | Use if Expo; no listing management |
| fastlane supply | https://docs.fastlane.tools/actions/upload_to_play_store/ | Uploads binaries, listing, screenshots, promotes tracks | Linux VM | 2026-10-16 | Use for non-Expo; first upload manual |
| Firebase App Distribution | https://firebase.google.com/docs/app-distribution | Tester distribution via CLI/Gradle/fastlane; price not seen | Google cloud | 2026-10-16 | Fallback to adb |
| Codemagic | https://codemagic.io/pricing/ | Cloud macOS builds, 500 free M2 min/month, $0.095/min after | cloud | 2026-10-16 | Use for iOS later |
| Health Connect SDK | https://developer.android.com/health-and-fitness/health-connect/get-started | Native Android health data API | Android | 2026-10-16 | Needs native/wrapper app; not PWA |
