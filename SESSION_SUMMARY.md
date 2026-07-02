# Session Summary — 2026-06-21 / 2026-07-01

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
