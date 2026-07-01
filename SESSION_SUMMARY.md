# Session Summary — 2026-06-21 / 2026-06-27

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
- **TestFlight (GitHub Actions):** **Upload succeeded** — workflow run [#4](https://github.com/deboboy/upright/actions/runs/28523810877) green (~3 min). **TestFlight tab shows “No Builds”** — investigating bundle ID mismatch (see Debug).
- **App Store Connect app name:** **Be Upright** (verify bundle ID matches `com.lastmyle.upright`).
- **App target:** **iPhone only** (`TARGETED_DEVICE_FAMILY = 1`) — fixes iPad orientation validation error (error 1 on upload).

---

## Your Next Steps (Resume When Back)

### Done ✓
- [x] App Store Connect API key (Admin) + GitHub repository secrets
- [x] GitHub Actions **TestFlight #4** — archive, export, upload all green
- [x] Export signing fix — Admin API key (App Manager failed with cloud signing error)

### Next — in order
1. [ ] **Verify bundle ID** on **Be Upright** → App Information (must be `com.lastmyle.upright`) — see **Debug** below
2. [ ] Fix mismatch (new ASC app or change Xcode bundle ID) if needed
3. [ ] Re-run **Actions → TestFlight → Run workflow** if bundle ID was wrong
4. [ ] **TestFlight** → confirm build **Processing** or **Ready to Test** → add testers
5. [ ] **Share friend brief** — `docs/testflight.md`

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
| First cloud build (run #4) | **Succeeded** — upload reported no errors |
| Build visible in TestFlight | **No** — see Debug section |
| TestFlight testers invited | **Pending** |

---

## Debug: GitHub green but TestFlight shows “No Builds”

Upload likely succeeded, but **“No Builds”** almost always means the build isn’t tied to **Be Upright** — usually a **bundle ID mismatch**.

### What GitHub uploaded

Workflow run **TestFlight #4** (`28523810877`, ~3 min, all steps green):

- **Archive:** succeeded — bundle ID `com.lastmyle.upright` (confirmed in logs)
- **Export:** succeeded after switching API key to **Admin** (App Manager → `Cloud signing permission error` / `No profiles were found`)
- **Upload:** `No errors uploading archive at '.../Upright.ipa'`

Xcode project bundle ID: **`com.lastmyle.upright`** (`ios/Upright.xcodeproj`).

### What to check in App Store Connect

1. **Be Upright → Bundle ID**  
   - Open **Be Upright** → **Distribution** or **App Information**  
   - **Bundle ID** must be exactly **`com.lastmyle.upright`**  
   - If it’s different (e.g. `com.lastmyle.beupright`), the build is attached to another app (or not visible under Be Upright).

2. **Activity**  
   - App Store Connect home → **Activity** (bell)  
   - Look for upload/processing messages or errors for `com.lastmyle.upright`.

3. **Email**  
   - Inbox for Apple / App Store Connect processing failure notices.

4. **Timing**  
   - Builds can take 30–60 min to appear as **Processing**  
   - **No Builds** (empty list) usually means mismatch, not slow processing (slow processing typically shows **Processing**).

### If bundle IDs don’t match — pick one

| Option | Action |
|--------|--------|
| **A (easiest)** | Create a new App Store Connect app with bundle ID **`com.lastmyle.upright`**, then re-run GitHub Actions **TestFlight** workflow |
| **B** | Change Xcode `PRODUCT_BUNDLE_IDENTIFIER` to match **Be Upright**’s bundle ID, commit, re-run workflow |

### Failed export before Admin key (for reference)

```
error: exportArchive Cloud signing permission error
error: exportArchive No profiles for 'com.lastmyle.upright' were found
```

**Fix:** App Store Connect API key with **Admin** role (not App Manager). Update `APPSTORE_API_KEY_ID` and `APPSTORE_API_PRIVATE_KEY` in GitHub secrets.

### Resume checklist

1. Note **Be Upright** bundle ID from App Information  
2. If ≠ `com.lastmyle.upright` → option A or B above  
3. Re-run workflow if needed  
4. TestFlight tab → **Processing** / **Ready to Test**  
5. Internal testers → install via TestFlight app  

---

## Files Changed (Latest Commit — `9ee1131`)

| Area | Files |
|------|--------|
| CI | `.github/workflows/testflight.yml` (new) |
| iOS project | `ios/Upright.xcodeproj/project.pbxproj` (iPhone only) |
| Docs | `docs/testflight.md`, `docs/github-actions-testflight.md` (new), `SESSION_SUMMARY.md` |
| Docs | `README.md` (Xcode signing steps, TestFlight link) |

---

## Reference

- Bundle ID: `com.lastmyle.upright` (change in Xcode if signing conflicts)
- Motion usage: `NSMotionUsageDescription` in `ios/Upright/Info.plist`
- Bridge contract: `docs/bridge-contract.md`
- Test plan: `docs/iphone-test-plan.md`
- TestFlight (local): `docs/testflight.md`
- TestFlight (GitHub Actions): `docs/github-actions-testflight.md`
- Storage keys: `upright.landingSeen`, `upright.sessions`
- **Always Clean Build Folder** (⇧⌘K) after web changes before device run
