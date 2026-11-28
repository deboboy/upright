# Session Summary — 2026-06-21 / 2026-07-01 / 2026-11-07 / 2026-11-17 / 2026-11-21 / 2026-11-27

## Session Resume — 2026-11-27 — LIVE ON THE APP STORE

Be Upright is approved and live: **https://apps.apple.com/us/app/be-upright/id6785146509**

Review turnaround was ~6 days (submitted 2026-11-21 evening, approved 2026-11-27). First attempt, first approval — no rejection, no Resolution Center thread. The `docs/app-store/review-notes.md` playbook paid off: the AirPods hardware requirement explanation and the step-by-step reproduction flow likely saved a "unable to demonstrate feature" rejection.

### What changed today

- **CTA URL finalized** across `docs/app-store/site/marketing.md` and the inline copies in `docs/app-store/site/cursor-brief.md`. Swapped the placeholder `https://apps.apple.com/app/be-upright` for the real locale-agnostic form `https://apps.apple.com/app/be-upright/id6785146509`. Chose the locale-agnostic variant (no `/us/` prefix) over the region-locked one Frank first received, so international visitors to `www.lastmyle.co/upright` auto-redirect to their own storefront instead of hitting a "not available in your region" page on the US listing.
- **Cursor brief updated** to reflect the live URL. The CTA-handling section no longer talks about "does not exist yet" — now points at the real URL and notes it's the locale-agnostic form.

### Your next steps

1. [ ] **Push the same CTA URL update through the `lastmyle.co` repo.** The placeholder is still live on `www.lastmyle.co/upright` until Cursor + Amplify ships the swap. One-line Cursor prompt: *"On the Be Upright pages, replace the two `[Download on the App Store →]` link targets from `https://apps.apple.com/app/be-upright` to `https://apps.apple.com/app/be-upright/id6785146509`. See the updated `docs/app-store/site/marketing.md` in the upright repo for reference."*
2. [ ] (Optional, non-urgent) Flip the App Store CTA button to use Apple's **Smart App Banner** or **App Store badge** if the Last Myle site has a design system component for that. Current approach is a plain text link — functional but uses the generic site button styling.
3. [ ] Watch **App Store Connect → Analytics** for install and session counts in the first week. The first 50 installs are usually friends-and-family and bots.
4. [ ] **Tell Nam-ho** that he can uninstall the TestFlight version and grab the App Store release — avoids him being stuck on the TestFlight build if you push updates via the App Store release channel instead.

### Still parked (now post-launch; most become v1.1 candidates)

- [ ] Apex `lastmyle.co` → `www` 301 redirect. Latent bug that will bite any future page added at the apex.
- [ ] 5th screenshot (Zero gear Sensor card, re-capture with cleared Events log).
- [ ] 6th screenshot (Welcome Landing card, requires uninstall + fresh TestFlight install to trigger first-launch state).
- [ ] App Preview videos (15–30 s, muted-autoplay-safe captions). High leverage on conversion.
- [ ] Flip DSA trader status if we want to drop the EU "non-trader" warning on the listing.
- [ ] Nam-ho's feedback on the live build.
- [ ] Product work for 1.1 — see the "Later (product)" line from the original 2026-07-01 session notes: *"Clarify Haptic/Speak/Reset UI, tune posture thresholds, slouch alerts, history detail view."* Thresholds were already tuned in 2026-11-07 session; the other three remain.

### Timeline, end-to-end

For posterity — total elapsed project time from "repo exists" to "live on App Store":

| Date | Milestone |
|---|---|
| 2026-06-21 → 07-01 | First working iPhone build, TestFlight #1 blocked on macOS SDK; moved to GitHub Actions CI; build 1.0 (1) uploaded. |
| 2026-11-07 | TestFlight install flow proven, posture-thresholds tuned, app icon shipped. |
| 2026-11-17 | Untethered TestFlight install, audio-route guard, `WKScriptMessageHandlerWithReply` registration root-cause fix. |
| 2026-11-21 | App Store collateral completed; app submitted for review at `1.1 (7)`. |
| **2026-11-27** | **Approved. Live on the App Store.** First post-launch patch `1.1.1 (10)` submitted for review the same evening. |

---

## Session Resume — 2026-11-27 (evening) — first post-launch patch submitted

### What shipped

- **Posture gauge visual refresh** (`web/styles.css`). Frank flagged that the score number ("51") looked undersized in the main Posture card — ~32% of inner panel height. Shipped as a two-pass iteration:
  - First pass (1.1.1 (8)): bumped font 3.6rem → 6rem and card height 210px → 260px. On-device review: "doesn't look that much larger" — because the container grew with the font, the ratio only moved from 32% to 42%.
  - Second pass (1.1.1 (9)): reverted card to 210px, pushed font to 7rem, tightened letter-spacing to -0.09em. Ratio jumped to ~63% of inner height — visibly dominant.
  - Third pass (1.1.1 (10)): fixed the stacking bug where score sat at the top edge and label at the bottom. Swapped `display: grid; place-items: center` for `display: flex; flex-direction: column; justify-content: center; align-items: center; gap: 0.6rem`. Grid was centering each item within its cell but letting the rows drift to the container edges; flex centers the pair as a block.
- **Submitted 1.1.1 (10) for App Store Review** as the first post-launch update. "What's New in This Version" copy described the visual polish without inflating what changed.

### CI firefights

Three new failure modes surfaced during this round of iteration, all now fixed:

- **Train closed after public release (ITMS-90186 + ITMS-90062).** After `1.1 (7)` went live, Apple closed the `1.1` marketing version train — no more uploads allowed on that version string, not even to TestFlight. First `1.1 (8)` upload failed with "CFBundleShortVersionString [1.1] must contain a higher version than that of the previously approved version [1.1]" and "Invalid Pre-Release Train. The train version '1.1' is closed for new build submissions." Fix: bump `CFBundleShortVersionString` to `1.1.1`, not just `CFBundleVersion`. The train stays open for TestFlight iteration on the new version until the next approval closes it.
- **Max Distribution certificates hit on the Apple Developer account.** After bumping to `1.1.1`, next CI run failed at **archive** step with "Choose a certificate to revoke. Your account has reached the maximum number of certificates." Root cause: our GH Actions pipeline uses `-allowProvisioningUpdates` with automatic signing, and because each macOS runner starts with an empty keychain, Xcode creates a fresh Development certificate every build. After ~8 CI runs we hit Apple's cap (3 Distribution + 2 Development per user). All 7 of the accumulated certs were visible in the Apple Developer portal as "Created via API" Development certs. Fix: revoke the 6 older ones in developer.apple.com → Certificates. Keep the most recent (buffer) + the manually-created local Dev cert + all Distribution certs untouched. Longer-term fix is to export one cert as `.p12` and persist via GitHub Secret, or use `fastlane match` — not needed tonight.
- **ITMS-90725 iOS 27 SDK deadline warning** (non-blocking). Upload succeeded with: "This app was built with the iOS 26.5 SDK. Starting April 2027, iOS and iPadOS apps must be built with the iOS 27 SDK or later, included in Xcode 27 or later." The GH Actions workflow pins `latest-stable` via `setup-xcode@v1` which currently resolves to Xcode 26.6 / iOS 26.5 SDK. Will auto-resolve to Xcode 27 when Apple releases it, well before the April 2027 deadline.

### Build numbering — now on the 1.1.1 train

The 1.1 train is closed. The 1.1.1 train opened and all subsequent TestFlight iterations go there:

| Build | Purpose |
|---|---|
| `1.1.1 (8)` | First attempt at the gauge resize. Score only moderately bigger. |
| `1.1.1 (9)` | Pushed font-size to 7rem; much more dominant. |
| `1.1.1 (10)` | Fixed vertical centering of the score+label pair. **Submitted for App Store review.** |

CFBundleVersion continues from `(7)` — Apple only requires uniqueness within a train, not reset per train, and continuity is easier to reason about operationally.

### Your next steps

1. [ ] **Watch App Store Connect for the 1.1.1 review outcome.** Update reviews typically turn around faster than first reviews — often in under 24 hours. Same three possible outcomes as before (In Review / Ready for Sale / Rejected).
2. [ ] (Optional cleanup) The failed CI runs `46066100466` (1.1 (8) train-closed) and `46066492815` (first 1.1.1 (8) cert-cap) are harmless but visible in GitHub Actions history. If you want them deleted to keep the UI clean: `gh run delete 46066100466 && gh run delete 46066492815`.
3. [ ] Keep an eye on the Distribution cert count in developer.apple.com — if we ship 1.1.2 and 1.1.3 soon, we'll hit the cap again. Revoke the "Created via API" cert from today (2027/11/27 expiration) once a newer one appears.
4. [ ] Consider moving to a persisted `.p12` cert in CI (durable fix for the max-certs problem) — see "Longer-term" note in the commit message for `cf7846c`.

### Memory additions

Three new CI-failure patterns worth saving alongside the existing `testflight-ci-failure-patterns.md` entries:

- **Train closed after App Store release** → when a marketing version string goes live, Apple blocks all further uploads on it. Bump `CFBundleShortVersionString` to the next patch (e.g. `1.1` → `1.1.1`) before the next TestFlight upload.
- **Max certificates on auto-provisioning CI** → `-allowProvisioningUpdates` on a fresh runner creates one Dev cert per build. Revoke old `Created via API` Development certs periodically in developer.apple.com. Keep Distribution untouched. Durable fix is a persisted `.p12`.
- **ITMS-90725 iOS 27 SDK deadline** (reference) → by April 2027, uploads will require Xcode 27 / iOS 27 SDK. `latest-stable` setup-xcode action will pick this up automatically when Apple ships it; no action needed until then.

---

## Session Resume — 2026-11-21

### What shipped

Four commits, zero new TestFlight builds — this was an App Store collateral push, not a code push. All work scoped to `docs/app-store/`.

- **Commit `7c68b09`** — 4 App Store screenshots at 1320×2868 composited and committed to `docs/app-store/screenshots/`, with a per-shot rationale README. Raw iPhone captures at native 1170×2532 (iPhone 14 class) placed on an off-white brand canvas with Arial Bold two-line headline, muted subhead, full-width posture-gradient accent, and Upright wordmark. ImageMagick compose pipeline.
- **Commit `963c970`** — App Store Connect text metadata finalized at `docs/app-store/metadata.md` (App Name, Subtitle, Promotional text, Description, Keywords, Categories, Copyright, Seller, URL fields, App Review contact). Draft copy for the three required marketing pages at `docs/app-store/site/marketing.md`, `support.md`, `privacy.md`.
- **Commit `73182ba`** — Pivoted the marketing-site plan from a dedicated `apps.lastmyle.co` subdomain to subpaths on the main `lastmyle.co` site for velocity. All URL references rewritten; `/upright`, `/upright/support`, `/upright/privacy` stay the same, just hosted on the existing domain. Added `docs/app-store/site/cursor-brief.md` — a self-contained handoff document for the Cursor agent that will add the three pages to the `lastmyle.co` codebase (inline markdown source for all three pages, GitHub raw URLs for the app icon and screenshot assets, design guidance to match the existing site system, SEO/Open Graph per-page settings, testing checklist, non-goals).
- **Commit `5f89df9`** — Paste-ready **Notes to Reviewer** at `docs/app-store/review-notes.md`. Front-loads the AirPods hardware requirement (which is the #1 rejection risk for headphone-motion apps), gives a 7-step reproduction flow with the audio-route gotcha called out as IMPORTANT, enumerates what the app does *not* do to preempt reject categories, and includes a rejection-response playbook for the four most likely bounce reasons.

### Resolved open questions

Three of the five open questions in `docs/app-store-assets.md` are now closed:

- **Legal entity** → **Last Myle, LLC**. Applied consistently across copyright, seller name, and all site/metadata footers. (Bundle ID stays `com.lastmyle.upright` — bundle IDs can't have spaces and are immutable for published apps.)
- **Marketing site plan** → subpaths on `lastmyle.co` via Cursor brief in a separate repo. Three required pages drafted.
- **Telemetry decision** → zero-collection for v1. Privacy policy drafted to match ("no data collected", no analytics, no third parties).

### Things ready to paste / upload when you're ready

| Where | What | Source |
|---|---|---|
| App Store Connect → Distribution → App Information | App Name, Subtitle, Categories, Copyright, Seller | `docs/app-store/metadata.md` |
| App Store Connect → Distribution → Version info | Promotional text, Description, Keywords | `docs/app-store/metadata.md` |
| App Store Connect → Distribution → iPhone 6.9" Display | 4 screenshot PNGs | `docs/app-store/screenshots/` |
| App Store Connect → App Review Information | Notes to Reviewer | `docs/app-store/review-notes.md` |
| `lastmyle.co` repo (Cursor) | Three new pages at `/upright`, `/upright/support`, `/upright/privacy` | `docs/app-store/site/cursor-brief.md` + the three `.md` source files |

### Your next steps

Everything remaining is outside this repo:

1. [ ] **Hand the Cursor brief to the `lastmyle.co` codebase.** Open the file in Cursor inside that repo or paste its contents into the Cursor chat. Expect the agent to flag back on the four items noted at the end of the brief (contact email, last-updated date, CTA destination, nav placement).
2. [ ] **Verify the three URLs return HTTP 200** once published. Apple's submission validator checks these at submission time.
3. [ ] **App Store Connect setup** (~30 min total):
   - Paste all text fields from `metadata.md`.
   - Upload the four screenshots from `docs/app-store/screenshots/`.
   - Complete the **Age Rating** questionnaire (expected 4+ — no mature content).
   - Complete the **App Privacy** questionnaire — pick "Data Not Collected" per the drafted policy. If you later add any analytics or crash reporting, this must be updated before that version ships.
   - Paste the **Notes to Reviewer** text from `review-notes.md`.
   - Fill in the Contact phone number under App Review Information.
   - Pick build **1.1 (7)** (or newer) for submission.
4. [ ] **Hit Submit.** First-review turnaround is usually 24–48 hours.

### Later that evening — submitted to App Store Review

After the collateral work above, everything got pasted into App Store Connect and the app was submitted.

**What got pasted / uploaded in ASC:**

- **Media Manager** → "iPhone with Dynamic Island (large display)" slot → all 4 screenshots from `docs/app-store/screenshots/`, in listing order. ASC confirms the slot accepts `1320 × 2868px` (matched our export exactly). First attempt uploaded to the "Product Page Information → Header" slot by mistake, which expects landscape `5244 × 2950` / `3840 × 1646` for Custom Product Pages; wrong destination, not a file problem.
- **App Information** → Name, Subtitle, Categories, Copyright, Content Rights per `docs/app-store/metadata.md`.
- **Age Rating** → walked questionnaire, all None/No → **4+**.
- **App Privacy** → "No, we do not collect data from this app" → short-circuits the Nutrition Label questionnaire. Matches `docs/app-store/site/privacy.md`.
- **Pricing and Availability** → Free; **China and Vietnam removed** from the territory list.
- **App Compliance** → Digital Services Act set to **non-trader** for v1 (accepts the EU "non-trader" warning on the listing in exchange for not having to declare Last Myle, LLC's business address right now; easy to flip later). Leftover China mainland compliance rows (Security Assessment, AI Generated Content) show "Active" but will resolve as the availability change propagates — not a blocker.
- **1.0 Prepare for Submission** → Promotional Text, Description, Keywords, URLs, Build pick **1.1 (7)**, Notes to Reviewer from `docs/app-store/review-notes.md`, contact info (Frank Martinez / frank@lastmyle.co).
- **Submit.**

**Status:** `1.0 Waiting for Review`. Apple's SLA is 24–48 hours for first review.

### URL deploy + the apex-domain catch

In parallel, the Cursor agent published the three pages into the `lastmyle.co` codebase per the handoff brief. AWS Amplify auto-deployed on push. Pages went live at:

- `https://www.lastmyle.co/upright`
- `https://www.lastmyle.co/upright/support`
- `https://www.lastmyle.co/upright/privacy`

Caught a latent bug that would have auto-rejected the review: the **apex domain was not redirecting to `www.`**. `https://lastmyle.co/upright/*` returned 404 while `https://www.lastmyle.co/upright/*` returned 200. If ASC had the bare URLs, Apple's reviewer fetch would have hit the 404.

Verified with `curl -I` on all six variants (3 paths × 2 hostnames). Updated the ASC URL fields to include `www.` on all three. URL fields are editable while the app is Waiting for Review and the reviewer sees the latest values — no resubmission required.

**Follow-up (not urgent):** add a 301 redirect from the apex `lastmyle.co` to `www.lastmyle.co` so this doesn't bite future pages. That's a DNS / Amplify config change in a different repo.

### Open questions, resolved during submission

Two more from `docs/app-store-assets.md`:

- **Release pacing** → Going direct to App Store review (not staying TestFlight-only). Nam-ho's feedback loop was not a gate.
- **Contact email** → `frank@lastmyle.co` used in ASC App Review Information. Site pages still use `support@lastmyle.co` as the published contact — fine to leave as a different-purpose alias, or swap later if you want everything to go to one inbox.

### Your next steps

1. [ ] **Watch your email** for the App Review result. Three possible outcomes:
   - **In Review** — reviewer picked up the submission (status turns blue in ASC).
   - **Ready for Sale** — approved, app is live or scheduled for release.
   - **Rejected** — email + Resolution Center thread in ASC with reasons. Respond directly in the thread.
2. [ ] (Non-blocking) Apex-to-www 301 redirect on `lastmyle.co` so bare URLs stop 404ing.
3. [ ] If **approved**: celebrate. Then real App Store URL replaces the placeholder `https://apps.apple.com/app/be-upright` in `docs/app-store/site/marketing.md` and on the published page.
4. [ ] If **rejected**: most likely reasons per `docs/app-store/review-notes.md` playbook. Most common for apps like Be Upright is "unable to demonstrate feature" when the reviewer doesn't have motion-capable AirPods — Notes to Reviewer explicitly addresses this, so if it still happens we respond with a pointer back to those notes.

### Still parked (not blockers)

- [ ] Fifth screenshot — the "Zero gear. Zero setup." Sensor card shot. Dropped from this round because the raw capture contained a `Start failed` event in the Events log. Easy re-capture with a cleared Events log any time; screenshots can be swapped in ASC without a new binary.
- [ ] Sixth screenshot — the "Welcome to Upright." Landing card shot. Requires uninstalling and reinstalling Be Upright via TestFlight to trigger the first-launch state.
- [ ] App Preview videos (optional; deferred to v1.1 of the listing).
- [ ] Nam-ho's feedback on the latest build.
- [ ] Flip DSA trader status to **trader** and declare Last Myle, LLC's business details if we want to drop the EU "non-trader" warning.

### Last six commits on `master` (collateral + submission milestone)

```
<will be updated after this commit>
46ffba2 Document 2026-11-21 session: App Store collateral complete.
5f89df9 Draft paste-ready App Review notes.
73182ba Pivot site plan to lastmyle.co subpaths and add Cursor handoff brief.
963c970 Finalize App Store text metadata and draft apps.lastmyle.co site copy.
7c68b09 Ship 4 App Store screenshots at 1320x2868 and update asset plan.
d4590c0 Document 2026-11-17 session: TestFlight untethered, audio-route guard, Reply-handler root cause, branded icon.
```

The TestFlight workflow was not triggered by any commit tonight — the path filter excludes `docs/**`. Build **1.1 (7)** remains the current TestFlight build and is the one in App Store Review.

---

## Session Resume — 2026-11-17

### What shipped (three CI builds in one evening)

- **Build 1.1 (5)** — audio-route guard on Start Session + first-pass calibration defensive fix. Added `BridgeError.audioRouteMissing` with a user-facing message, guarded `HeadphoneMotionAdapter.startUpdates` behind `hasBluetoothHeadphonesInAudioRoute()`, and surfaced the error in the Posture card copy instead of silently leaving it on "Start a session to begin tracking." Hardened `web/app.js` calibration with optional chaining against `undefined` reply.
- **Build 1.1 (6)** — branded app icon. Replaced the Xcode-template placeholder (teal background, yellow ring, blank white face) with the stacked-dots mark: three circles vertically centered on the off-white brand background colored with the existing posture palette (`#0d9488` good, `#d97706` warn, `#e11d48` bad). Source SVG preserved at `build/icon-previews/option-a-stacked-dots.svg`; PNG rendered with ImageMagick at 1024×1024, 8-bit sRGB, no alpha (Apple requirement).
- **Build 1.1 (7)** — the actual root-cause fix. See issue #19 below. This is the build to expose to the internal group.

### You went untethered

- Added yourself as an internal tester to the **Upright Friends** group (Account Holder had to add themselves explicitly — not automatic).
- Installed via the TestFlight invite email on your iPhone; no cable, no Xcode, no `devicectl`.
- Confirmed the live posture pipeline on the TestFlight build: 597 samples / 24 s session, avg score **37**, posture distribution 72% good / 20% slouch.
- Workflow going forward: `git push` to `master` → ~3 min CI → TestFlight notification on iPhone → tap **Update**.

### Issues resolved

#### 17. Posture tracking showed Unknown / 0 samples with AirPods "connected"

**Symptom:** Session started, Focus Timer counted down, Motion stayed at 0 samples for 13+ s. Sensor card showed `Permission: granted`, `Connection: connected`, `Motion ready: yes`, **Device: AirPods** (generic — not "Frank's AirPods Pro"), **Rate: —**.

**Cause:** AirPods were paired to the iPhone but the active audio route had drifted to another device (Mac — happens automatically when there's audio activity on the Mac side). `CMHeadphoneMotionManager.isDeviceMotionAvailable` returned `true` because the pairing is still known, but `startDeviceMotionUpdates(...)` emits zero samples until the AirPods are the active audio sink. The generic "AirPods" label in the Sensor card was the smoking gun: `HeadphoneMotionAdapter.connectedDeviceName` falls back to that string only when the audio-route lookup finds nothing.

**Fix:** Play audio on the iPhone to force the route (any clip works). Shipped in build 1.1 (5): a guard in `HeadphoneMotionAdapter.startUpdates` that refuses to start when no Bluetooth headphone port is in the active route, surfacing the reason in both the Events log and the Posture card copy.

#### 18. Calibration JS error (long-running, finally diagnosed)

**Symptom:** Events log showed `Calibration fallback used: undefined is not an object (evaluating 'result.neutral')` every time Calibrate Neutral was tapped. The fallback (`engine.calibrate()`) masked the user-visible impact, but the error had been there for weeks.

**First diagnosis (wrong):** I assumed `WKScriptMessageHandlerWithReply` was returning an unexpected shape or an edge-case serialization of `["ok": true, "neutral": [...]]`. Added defensive optional chaining in `web/app.js` as a workaround. That reduced the symptom but didn't fix the cause.

**Actual cause:** See issue #19 — the Reply handler was never active. `result` was always `undefined` because `postMessage` wasn't returning a Promise; JS saw nothing from the native side at all.

**Fix:** Keep the defensive JS (belt-and-suspenders) but ship the real fix in 1.1 (7).

#### 19. "Session started" logged AFTER audio_route_missing error — and the real root cause

**Symptom:** After installing 1.1 (5), testing the new audio-route guard produced a confusing Events log:

```
9:24:07 PM — Session started.                          ← should not exist
9:24:07 PM — Error: native_error — AirPods are not...  ← duplicate
9:24:07 PM — Error: audio_route_missing — AirPods ...
9:24:07 PM — Starting session…
```

The audio-route guard fired correctly in Swift, but the JS ran its success path anyway, and a phantom `native_error` event appeared alongside the real `audio_route_missing` one.

**Cause:** `NativeBridge.install` called `configuration.userContentController.add(self, contentWorld:, name:)` — the fire-and-forget `WKScriptMessageHandler` variant. Because `NativeBridge` conforms to **both** `WKScriptMessageHandler` and `WKScriptMessageHandlerWithReply`, the compiler silently picked the plain one. Consequences:

- On the JS side, `postMessage` returned `undefined` instead of a Promise, so every `await bridge.call(...)` resolved to `undefined`. This is what made `result.neutral` throw (issue 18) and what let `await startUpdates(...)` never throw on error.
- The `WKScriptMessageHandler` extension's closure *was* being invoked on message delivery, and when `handle(...)` called `replyHandler(nil, error)`, that closure dispatched `error` events with `code: "native_error"` — the duplicate.

A separate secondary bug in `NativeBridge.startUpdates` called `reply(NSNull(), replyHandler)` unconditionally after `adapter.startUpdates(...)` returned, which would have been a protocol violation once the Reply handler actually worked.

**Fix (build 1.1 (7)):**

- `addScriptMessageHandler(self, contentWorld:, name:)` instead of `add(self, contentWorld:, name:)` — registers the Reply variant.
- Track a `replied` flag in `startUpdates` so the success path is skipped when the sync error path already replied, and the async error path skips the reply entirely.

Verified on-device: audio-route test now produces a clean log (`Starting session…` → `Error: audio_route_missing` → `Start failed: ...`), no phantom `Session started`, no duplicate `native_error`, Posture card copy updates to the route-missing message.

### What's in the current master binary

Build **1.1 (7)** at commit `edca6a2` on master:

- All three tonight's commits merged in (`d41ca0a` route guard + defensive calibration JS, `59bc08b` stacked-dots icon, `edca6a2` the real Reply-handler fix)
- All prior work from 2026-11-07 session (card reorder, lower thresholds, deployment target 15.0)

### Your next steps

1. [ ] In App Store Connect → TestFlight → **Upright Friends** internal group → **Builds** tab, enable **1.1 (7)** for the group. Builds 1.1 (5) and 1.1 (6) can stay or be hidden; 1.1 (7) is strictly newer.
2. [ ] Update to 1.1 (7) on your iPhone via TestFlight → run the expected-behavior test from the push summary (audio-route guard without music; happy-path with music).
3. [ ] Check back on Nam-ho's App Store Connect user-invite acceptance (sent 2026-11-07). If Pending, resend; if Accepted, add him to the Upright Friends internal group so he can install 1.1 (7).
4. [ ] When ready, draft TestFlight tester-facing copy — the current App Description ("Very rough first version of the Upright iOS app.") shows to anyone with TestFlight access to this build and could be sharper for friends.

### Debug playbook additions

For `memory/testflight-ci-failure-patterns.md` or a future runbook — tonight added two new patterns:

- **Paired AirPods but no motion samples**: check Sensor card Device label. "AirPods" (generic) means the audio route lookup found nothing; the AirPods aren't the active sink. Play audio on the iPhone or switch route via Control Center. Guarded in 1.1 (5)+.
- **`WKScriptMessageHandlerWithReply` registration**: in Swift, `WKUserContentController` has two overloads — `add(_:contentWorld:name:)` registers the plain handler, `addScriptMessageHandler(_:contentWorld:name:)` registers the Reply handler. If your Swift class conforms to **both** protocols, `add(...)` silently picks the plain variant regardless of the `name` string. Symptom on the JS side: `postMessage` returns `undefined` instead of a Promise; every `await bridge.call(...)` resolves to `undefined`.

### Still parked for later (public App Store release)

Per `docs/app-store-assets.md`:

- App Store screenshots (6 shots at iPhone 6.9" / 1320×2868)
- Marketing site for Support URL and Privacy Policy URL
- App Store text metadata (name is "Be Upright"; still need subtitle, description, keywords)
- App Preview video (optional, v1.1+)
- Privacy Nutrition Label questionnaire
- Age-rating questionnaire
- App Review notes (flag the AirPods-reviewer-can't-test problem)

---

## Session Resume — 2026-11-07

### What shipped

- **UI reorder** (`web/index.html`): Posture card first, then Focus Timer, Motion, History, Events; Sensor / Settings moved to the bottom. Posture is the primary value; the status card was reference info surfaced too high.
- **Posture thresholds lowered** (`web/posture-core.js`): `warningHigh 55 → 35`, `slouchHigh 72 → 55`, `warningLow 35 → 20`. Scoring is `|Δpitch| × 160 + |Δroll| × 80` (radians) against calibrated neutral — old `warningHigh = 55` required ~20° of head drop. Observed session averaged 10–12° head drop with avg score **52** (still "good"). New thresholds trigger warning at ~13° and slouch at ~20°, matching the Motion chart's existing ±12° Y-scale.
- **Version bump → 1.1 (3)** in `ios/Upright/Info.plist` and all four build configurations in `ios/Upright.xcodeproj/project.pbxproj`. Marketing bump reflects the product change; build bump avoids `ITMS-90189` against the existing build **2**.
- **TestFlight upload (CI)**: workflow run [`42447679340`](https://github.com/deboboy/upright/actions/runs/42447679340) succeeded in 2m19s after both agreements were re-accepted. Build **1.1 (3)** is **Processing** in App Store Connect.
- **Physical-device run** verified before upload: `xcodebuild` for `platform=iOS,id=…` + `xcrun devicectl device install app` + `xcrun devicectl device process launch com.lastmyle.upright` installs and relaunches without Xcode GUI. Signing already configured (team `7B4D6525KF`, bundle `com.lastmyle.upright`).

### Issues resolved

#### 15. TestFlight CI archive failed — Program License Agreement not accepted

**Symptom:** GitHub Actions run [`42447264456`](https://github.com/deboboy/upright/actions/runs/42447264456) failed in **Build archive** with:

```
error: Unable to process request - PLA Update available: You currently don't have access
to this membership resource. To resolve this issue, your team's Account Holder, Frank
Martinez, must agree to the latest Program License Agreement.
error: No profiles for 'com.lastmyle.upright' were found: Xcode couldn't find any iOS App
Development provisioning profiles matching 'com.lastmyle.upright'.
```

**Cause:** Apple published a new Program License Agreement; team cannot sign or fetch provisioning profiles until the Account Holder accepts it. The "no profiles" error is a downstream symptom.

**Fix:** Account Holder accepted the updated PLA at [developer.apple.com/account](https://developer.apple.com/account). Re-triggering the workflow then let archive + export succeed.

#### 16. TestFlight CI upload failed — Free Apps Agreement expired

**Symptom:** Archive and export succeeded, but the **Upload to TestFlight** step returned HTTP 403 `FORBIDDEN.REQUIRED_AGREEMENTS_MISSING_OR_EXPIRED` with `links.see = "/business"`.

**Cause:** Separate from the PLA — App Store Connect's own Business agreements (Free Apps / Paid Apps) also need to be in effect for the `iris` upload API to accept new builds. A PLA refresh invalidated the Free Apps Agreement.

**Fix:** Accepted the pending agreement at [appstoreconnect.apple.com/business](https://appstoreconnect.apple.com/business), then re-ran the failed job:

```bash
gh run rerun 42447679340 --failed
```

Re-run succeeded end-to-end in 2m19s. Build **1.1 (3)** is now queued in TestFlight.

### Your next steps

1. [ ] Wait 5–15 min for App Store Connect to finish processing build **1.1 (3)**.
2. [ ] Confirm build status reaches **Ready to Test** (should be automatic — `ITSAppUsesNonExemptEncryption = false` is already set in `Info.plist`).
3. [ ] TestFlight → **Internal Testing** → enable build **1.1 (3)** for your existing internal group.
4. [ ] Add friends' Apple ID emails to the same internal group.
5. [ ] Share `docs/testflight.md` as the tester brief.

### Debug playbook (for future PLA / agreement breaks)

When a CI build suddenly fails after months of working:

1. `gh run list --workflow=testflight.yml --limit 5` — find the failing run ID.
2. `gh run view <id> --log-failed | tail -60` — the actual Apple error is near the bottom.
3. If the message mentions **PLA** or **provisioning profile**, Account Holder opens [developer.apple.com/account](https://developer.apple.com/account) and accepts the updated PLA.
4. If the message mentions **REQUIRED_AGREEMENTS_MISSING_OR_EXPIRED** or **/business**, Account Holder opens [appstoreconnect.apple.com/business](https://appstoreconnect.apple.com/business) and accepts the pending Free Apps / Paid Apps agreement.
5. `gh run rerun <id> --failed` to re-trigger without a new commit (no version bump needed if the upload step is what failed — the build never landed).

---

## Goal

Get the Upright iOS app building and running on a physical iPhone with live AirPods posture tracking, improve onboarding and brand experience, polish the Motion card and session history, and **ship a TestFlight beta to friends**.

## Current Status

- **Simulator:** App loads and runs (browser mock).
- **Physical iPhone:** App installs, signs, and runs (development team + keychain configured).
- **Brand refresh:** **Verified** — light theme, first-launch landing, posture stripe.
- **AirPods session:** **Working** — connect, stream at 25 Hz, live posture score, focus timer, 240+ samples per session.
- **Motion card:** **Working** — pitch/roll Δ readouts, auto-scaled degree chart, RAF-throttled redraws.
- **Session history:** **Implemented** — saves summaries to `localStorage` on stop (`upright.sessions`).
- **Connection detection:** **Fixed** — delegate + `isDeviceMotionAvailable`; Sensor card shows **Motion ready**.
- **TestFlight (local upload):** **Blocked** — Mac on macOS 24 / Xcode 16; App Store Connect requires iOS 26 SDK (Xcode 26 / macOS 26.2+). User chose **not** to upgrade macOS.
- **TestFlight (GitHub Actions):** **Build 1 live** — workflow run [#4](https://github.com/deboboy/upright/actions/runs/28523810877) uploaded successfully. **Be Upright → TestFlight → build 1.0 (1)** is **Ready to Submit** (expires in 90 days).
- **App Store Connect app name:** **Be Upright** — bundle ID verified **`com.lastmyle.upright`**.
- **App target:** **iPhone only** (`TARGETED_DEVICE_FAMILY = 1`) — fixes iPad orientation validation error (error 1 on upload).
- **Next CI build:** **Build 2** — bumped `CFBundleVersion` + `ITSAppUsesNonExemptEncryption = false` in `Info.plist` (skips export compliance prompt on future uploads).

---

## Your Next Steps (Resume When Back)

### Done ✓
- [x] App Store Connect API key (Admin) + GitHub repository secrets
- [x] GitHub Actions **TestFlight #4** — archive, export, upload all green
- [x] Export signing fix — Admin API key (App Manager failed with cloud signing error)
- [x] Bundle ID verified on **Be Upright** (`com.lastmyle.upright`)
- [x] Export compliance completed — **None of the algorithms mentioned above**
- [x] Build **1.0 (1)** **Ready to Submit** in TestFlight

### Next — in order
1. [ ] **TestFlight → Internal Testing** → create group → add your Apple ID email
2. [ ] Enable **build 1** for the group → install via **TestFlight** app on iPhone
3. [ ] Add friends’ Apple ID emails to the same internal group
4. [ ] **Share friend brief** — `docs/testflight.md`
5. [ ] (Optional) Commit/push triggers build **2** via GitHub Actions when you want latest plist fixes in TestFlight

**Docs:** `docs/github-actions-testflight.md` · `docs/testflight.md`

**Later (product):** Clarify Haptic/Speak/Reset UI, tune posture thresholds, slouch alerts, history detail view.

---

## Issues Fixed (This Session)

### 7. Motion card showed flat / empty data

**Symptom:** Chart lines appeared flat; readouts empty despite samples flowing.

**Cause:** Chart plotted raw radians with a tiny multiplier; no delta-from-neutral scaling.

**Fix:** Plot degrees away from calibrated neutral, auto Y-scale, live pitch/roll/window readouts, zero reference line.

### 8. “Disconnected” status despite AirPods in ears

**Symptom:** Sensor card showed `disconnected` while permission was `granted`; user thought app was broken.

**Cause:** Connection logic misused `isConnectionStatusActive` (means “updates running”, not “buds connected”) and only checked active Bluetooth audio route.

**Fix:**
- `CMHeadphoneMotionManagerDelegate` + `startConnectionStatusUpdates()`
- Treat `isDeviceMotionAvailable` as motion-ready signal
- Expanded audio-route port detection
- Added **Motion ready** row to Sensor card
- Delayed status re-push after web load; poll until connected

### 9. Permission button returned `undefined` / `unknown`

**Cause:** WKWebView reply handler does not reliably return bare Swift strings to JS.

**Fix:** Native returns `{ permission: "granted" }`; bridge-sdk unwraps; button disables when already granted.

### 10. Boot fragility from chart errors

**Cause:** `drawChart()` inside boot `try/catch` could trigger mock-bridge fallback on UI errors.

**Fix:** `safeDrawChart()` / `scheduleDrawChart()`; boot only falls back on bridge failures; single boot promise.

### 11. SIGABRT crash when scrolling during session

**Symptom:** App froze/crashed on Thread 2 at `recentSamples.append(sample)` when scrolling to Motion card.

**Cause:** CoreMotion callback on background thread raced with main-thread reads of `recentSamples` (Swift `Array` is not thread-safe).

**Fix:**
- Serial `sampleQueue` for all `recentSamples` access
- Dispatch motion events to main thread before bridge/JS
- Stop existing motion updates before starting a new session
- Throttle chart redraws to one per animation frame

### 12. Swift build error in `HeadphoneMotionAdapter`

**Symptom:** `Cannot convert value of type '() -> Void?' to expected argument type 'DispatchWorkItem'`.

**Fix:** Inlined `DispatchQueue.main.async` closure instead of passing optional-returning closure to `execute:`.

### 13. TestFlight upload validation errors

**Symptom:** Upload failed — iPad orientation bundle error + iOS 26 SDK required.

**Fix:**
- Set app to **iPhone only** in `project.pbxproj` (orientation / multitasking error).
- Local upload still blocked without Xcode 26 / macOS 26.2+.
- Added **GitHub Actions** workflow (`.github/workflows/testflight.yml`) to build and upload from cloud Macs.

### 14. TestFlight showed “No Builds” despite green GitHub upload

**Symptom:** TestFlight tab empty; Activity showed no errors; bundle ID was correct.

**Cause:** Build **1.0 (1)** uploaded successfully but blocked on **Missing Compliance** (export encryption). A re-upload hit **ITMS-90189** (redundant binary — build 1 already registered).

**Fix:**
- App Store Connect → **Manage** → **None of the algorithms mentioned above** (app uses only Apple OS APIs, no custom crypto)
- Build status → **Ready to Submit**
- For future uploads: `ITSAppUsesNonExemptEncryption = false` in `Info.plist`; increment build number before each new upload

---

## Earlier Issues Fixed (Prior Sessions)

### 1. Xcode project would not open (`project.pbxproj` parse error)

**Fix:** Corrected `scripts/create_repo_files.py` generator and regenerated `project.pbxproj`.

### 2. Swift compile errors (11 issues)

**Fixes:** CoreMotion import, WebKit preconcurrency, bridge handler split, deprecated JS prefs, sample throttling, etc.

### 3. Build failed on “Copy Web” phase

**Fix:** Build script uses `${SRCROOT}/../web/`.

### 4. Runtime crash on launch (JSON write)

**Fix:** `JSONEncoder` for event type; validate payload before dispatch.

### 5. WKWebView JavaScript would not boot

**Fix:** Classic scripts instead of ES modules; file URL access prefs; bridge request `id`; event routing.

### 6. Native bridge connected but UI stalled

**Fix:** Sensor markup, main-thread replies, status cache, listener timing, timeouts.

---

## Brand Refresh (Verified on iPhone)

| Decision | Choice |
|----------|--------|
| Theme | Light only |
| Scope | First-launch landing + reskin existing app |
| Accent | Posture rainbow (good / warning / slouch) |
| Typography | System fonts (SF Pro) |
| Landing | First launch only via `localStorage` (`upright.landingSeen`) |
| CTA | Black primary buttons |
| Tagline | **Stay stacked. Stay focused.** |

---

## Motion & History Features

### Motion card
- Pitch Δ / Roll Δ / Window readouts
- Canvas chart: last ~90 samples, degrees from neutral, auto-scale, dashed 0° line
- Sample count in header

### Session history (`web/session-store.js`)
- Saves on **Stop** when ≥ 5 samples
- Stores: when, duration, avg score, good/slouch %, color bar
- Up to 40 sessions in `localStorage` (`upright.sessions`)
- **History** card with Clear button

---

## AirPods Test Results (Latest — Verified on iPhone)

1. **Motion ready:** yes with AirPods in ears
2. **Start Session** → 25 Hz, 240 samples, timer running
3. **Live chart** — pitch/roll Δ updating (e.g. +2.3° / +4.3°)
4. **Scroll to Motion card** — no crash after thread-safety fix
5. Posture score responds to head movement (good / warning / slouch)

---

## TestFlight Distribution Progress (updated 2026-07-01)

| Step | Status |
|------|--------|
| App Store Connect app record | **Be Upright** created |
| Local Archive + upload | Failed — SDK 26 required |
| iPhone-only target fix | **Done** |
| GitHub Actions workflow | **Done** |
| Admin API key + GitHub secrets | **Done** |
| First cloud build (run #4) | **Succeeded** — build **1.0 (1)** uploaded |
| Export compliance | **Done** — none of the algorithms above |
| Build visible in TestFlight | **Ready to Submit** (90-day expiry) |
| Internal testers invited | **Next** — create group + add emails |
| Build 2 (CI) | **Queued in repo** — bump + encryption plist flag |

---

## TestFlight Debug Notes (resolved)

### What happened

Workflow run **TestFlight #4** (`28523810877`, ~3 min, all steps green):

- **Archive:** succeeded — bundle ID `com.lastmyle.upright`
- **Export:** succeeded with **Admin** API key
- **Upload:** `No errors uploading archive at '.../Upright.ipa'`
- **Build Uploads:** first attempt **Failed** (7:13 AM); second **Complete** (7:36 AM)
- **TestFlight:** build **1** showed **Missing Compliance** until export form completed
- **Email ITMS-90189:** redundant re-upload of build **1** — increment build number before next CI run

### Export compliance (for reference)

For Upright (local WKWebView + AirPods motion, no custom crypto):

- App Store Connect → **Manage** → **None of the algorithms mentioned above**
- Or set in `Info.plist`: `ITSAppUsesNonExemptEncryption` = `false` (done for build 2+)

### Failed export before Admin key (for reference)

```
error: exportArchive Cloud signing permission error
error: exportArchive No profiles for 'com.lastmyle.upright' were found
```

**Fix:** App Store Connect API key with **Admin** role (not App Manager).

---

## Files Changed (Latest Commit)

| Area | Files |
|------|--------|
| iOS | `ios/Upright/Info.plist` — build **2**, `ITSAppUsesNonExemptEncryption` |
| iOS | `ios/Upright.xcodeproj/project.pbxproj` — `CURRENT_PROJECT_VERSION = 2` |
| Docs | `SESSION_SUMMARY.md` — TestFlight resolved, next steps |

---

## Reference

- Bundle ID: `com.lastmyle.upright`
- Motion usage: `NSMotionUsageDescription` in `ios/Upright/Info.plist`
- Export compliance: `ITSAppUsesNonExemptEncryption` in `ios/Upright/Info.plist`
- Bridge contract: `docs/bridge-contract.md`
- Test plan: `docs/iphone-test-plan.md`
- TestFlight (local): `docs/testflight.md`
- TestFlight (GitHub Actions): `docs/github-actions-testflight.md`
- Storage keys: `upright.landingSeen`, `upright.sessions`
- **Always Clean Build Folder** (⇧⌘K) after web changes before device run
