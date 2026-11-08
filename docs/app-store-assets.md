# App Store Assets Plan

Everything the App Store Connect listing for **Be Upright** will need before public launch. TestFlight does not require most of this — it starts to matter when you're ready to submit the app to the public App Store (i.e. move beyond invited testers).

> **Source of truth:** Apple changes sizes and requirements periodically. Before any final export, verify against:
> - [App Store Connect Help → Screenshot specifications](https://developer.apple.com/help/app-store-connect/reference/screenshot-specifications)
> - [Human Interface Guidelines → App icons](https://developer.apple.com/design/human-interface-guidelines/app-icons)
> - [App Store Connect Help → Overview of app information](https://developer.apple.com/help/app-store-connect/reference/overview-of-app-information)

## App context

| | |
|---|---|
| App Store name | **Be Upright** |
| Bundle ID | `com.lastmyle.upright` |
| Tagline (current) | *Stay stacked. Stay focused.* |
| Target device family | iPhone only (`TARGETED_DEVICE_FAMILY = 1`) |
| Minimum iOS | 15.0 |
| Supported orientation | Portrait only |
| Core experience | WKWebView shell over AirPods headphone-motion posture tracking |

This context shapes several decisions below (e.g. we don't need iPad screenshots, landscape renders, or iMessage artwork).

---

## 1. App icon

The app icon ships inside the binary (`ios/Upright/Assets.xcassets/AppIcon.appiconset/`), so the next version-bump upload would include whatever we provide here. App Store Connect pulls the marketing icon from the uploaded binary — no separate upload field.

| Asset | Size | Format | Notes |
|---|---|---|---|
| App Store marketing icon | **1024 × 1024 px** | PNG, RGB, **no alpha** | Flat corners — Apple applies the rounded mask. No transparency; white or opaque background. |
| Home screen / Settings / Spotlight sizes | Generated from a **Single Size** entry in Xcode 14+ | PNG | If we use Xcode's Single Size icon well, the 1024 px asset is the only source we maintain. |

### What we need to produce

- [ ] Final **1024 × 1024** PNG master in a vector-editable source (Figma, Sketch, or Illustrator) so we can regenerate.
- [ ] Decide: wordmark, symbol (ear / spine motif), or hybrid? Current web app uses an AirPods silhouette on the landing — worth considering as a starting point.
- [ ] Keep legible at 60 × 60 px (Settings tile) — avoid thin strokes and small text.
- [ ] Dark-background check: Apple displays the icon on light and dark iOS backgrounds; make sure the icon isn't white-on-white when it lands on light mode.

---

## 2. Screenshots (App Store listing)

Apple requires at least one iPhone screenshot set. For new submissions today, the baseline is the **6.9" display** (iPhone 16/17 Pro Max class); Apple scales these down for the smaller devices. You can supply **up to 10** per device size.

| Device class | Resolution (portrait) | Required? |
|---|---|---|
| iPhone **6.9"** (iPhone 16/17 Pro Max) | **1320 × 2868** | **Yes — baseline for new apps** |
| iPhone **6.5"** (iPhone 11 Pro Max class) | 1242 × 2688 | Optional; still accepted for backward coverage |
| iPhone 6.7" (iPhone 14 Pro Max class) | 1290 × 2796 | Optional |
| iPad | — | **Skip** — Upright is iPhone-only |

### Plan — 6 screenshots for Upright

Treat the 6.9" set as canonical. Order matters: the first two are what shows above the fold in the App Store listing.

1. **Hero** — Posture card full-bleed showing a green "good" state, score 0, pill badge. Add a headline overlay: *"Stay stacked. Stay focused."*
2. **Live tracking** — Posture card with Motion chart visible, score in the warning band. Overlay: *"Real-time posture from your AirPods."*
3. **Focus Timer** — Timer card with active session. Overlay: *"25-minute focus sessions."*
4. **History** — History card with 3–4 completed sessions (avg scores, color bars). Overlay: *"Track trends across sessions."*
5. **Sensor transparency** — Sensor card showing Mode / Permission / Connection / Device. Overlay: *"Zero setup. Just your AirPods."*
6. **Landing** — First-launch landing card with AirPods silhouette. Overlay: *"Welcome to Upright."*

### What we need to produce

- [ ] Capture reference screens on a real iPhone 16/17 Pro Max simulator (Simulator → File → New Screen Shot).
- [ ] Decide on overlay typography and color (likely SF Pro + posture accent gradient).
- [ ] Composite in Figma / Sketch at 1320 × 2868 with device bezel optional.
- [ ] Export six **PNG or JPEG** files, sRGB, no alpha.
- [ ] Localization: only **en-US** at first. Add other locales later if we localize the app.

---

## 3. App Preview videos (optional, high leverage)

Up to **3 videos per device size**, 15–30 seconds, H.264 MP4 / M4V / MOV. Apple autoplays them in listings, so they're more visible than screenshots. Not required for launch but worth considering after v1 is live.

### What one would contain (sketch)

- 0–3 s: Hero shot of Posture card, tagline.
- 3–10 s: User puts in AirPods, taps Calibrate Neutral, sits upright, score at 0 / good.
- 10–20 s: User slouches, pitch chart drops, posture pill turns amber then red.
- 20–28 s: User straightens, pill returns to green, Focus Timer running in background.
- 28–30 s: Logo + tagline.

### What we need to produce

- [ ] Script + storyboard.
- [ ] Capture on-device using QuickTime screen recording from a connected iPhone (simulator doesn't show the posture updates driven by AirPods).
- [ ] Edit, color-grade, add captions (App Store autoplay is **muted by default** — captions are essential).
- [ ] Export at 1080 × 1920 @ 30 fps minimum (Apple scales to each device class).

**Defer to v1.1 of the listing** — launch with screenshots only.

---

## 4. Text metadata (App Store Connect form)

These live in App Store Connect and can be edited without a new build, except **App Name** which is tied to a submission.

| Field | Limit | Current / draft |
|---|---|---|
| **App Name** | 30 chars | *Be Upright* (14) |
| **Subtitle** | 30 chars | TBD — e.g. *"AirPods posture coach"* (22) |
| **Promotional text** | 170 chars | TBD — can change without resubmission |
| **Description** | 4000 chars | TBD — long-form; see outline below |
| **Keywords** | 100 chars, comma-separated | TBD — e.g. `posture,airpods,focus,timer,ergonomics,health,back pain,sitting,neck,slouch` |
| **Support URL** | — | TBD — need a landing page (lastmyle.co/upright?) |
| **Marketing URL** | optional | — |
| **Privacy Policy URL** | required | TBD — must be live before submission |
| **Copyright** | — | *© 2026 LastMyle* (adjust to legal entity name) |
| **Primary category** | — | **Health & Fitness** (recommended) |
| **Secondary category** | — | **Productivity** (focus timer angle) |

### Description outline (for drafting the 4000-char field)

1. One-sentence hook — what it does and why.
2. "How it works" — three-step list (put on AirPods, calibrate, go).
3. Feature bullets — real-time posture score, focus timer, history, haptic nudges.
4. Privacy posture — motion data stays on-device.
5. Hardware requirements — AirPods Pro / AirPods Max / AirPods (3rd gen) with motion support; iPhone running iOS 15+.
6. Call to action.

### What we need to produce

- [ ] Draft subtitle and promotional text in a doc for review.
- [ ] Draft the description (keep it under 4000 chars including line breaks).
- [ ] Finalize keyword list; avoid duplicating words from App Name / Subtitle (Apple indexes those separately).
- [ ] Stand up Support URL (even a one-page site with an email contact clears the requirement).
- [ ] Publish Privacy Policy URL (see §6).

---

## 5. Age rating

Set via a questionnaire in App Store Connect. Upright has no mature content, so this is quick.

- [ ] Walk the questionnaire: no violence, no sexual content, no gambling, no user-generated content, no unrestricted web access (WKWebView loads only bundled files), no third-party ads.
- Expected rating: **4+**.

---

## 6. Privacy

Two artifacts, both required.

### Privacy Nutrition Label

Declared in App Store Connect → App Privacy. For Upright today:

- **Data linked to you:** none.
- **Data not linked to you:** none *if* we don't send telemetry.
- **Data used to track you:** none.

If we later add analytics (e.g. Mixpanel, Sentry) we must update this. Motion data is processed on-device and not transmitted — declare accordingly.

- [ ] Fill App Privacy section — pick "Data Not Collected" for v1 if telemetry stays off.

### Privacy Policy URL

Apple requires a live URL even if we collect nothing.

- [ ] Draft a short privacy policy (what we collect, what we don't, contact).
- [ ] Host at a stable URL (e.g. `lastmyle.co/upright/privacy`).
- [ ] Paste the URL into the App Store Connect field.

---

## 7. Review notes & demo access

Supplied in App Store Connect → App Review Information. These aren't published; they help the reviewer.

- [ ] **Review notes**: explain that the app requires AirPods with motion support to demonstrate posture tracking; without them, the Sensor card will show `disconnected` and the Posture card won't update. Suggest reviewer uses the in-app mock mode if accessible (or we add a review-only mock toggle).
- [ ] **Demo account**: N/A — no login.
- [ ] **Contact info**: full name, phone, email for the reviewer to reach if they're blocked.

---

## 8. Promotional / optional artwork

Apple-featured placements can request bespoke art (1800 × 1200, etc.), but this is pulled from supplied screenshots unless we're invited. Skip for v1.

---

## Launch asset checklist (one-page view)

### Must-haves to submit

- [ ] 1024 × 1024 app icon in the binary
- [ ] At least 3 screenshots at 1320 × 2868 (iPhone 6.9")
- [ ] App Name, Subtitle, Description, Keywords finalized
- [ ] Support URL live
- [ ] Privacy Policy URL live
- [ ] Privacy Nutrition Label completed
- [ ] Age rating questionnaire completed
- [ ] Review notes written

### Nice-to-haves before submission

- [ ] Full 6-screenshot set
- [ ] Promotional text
- [ ] App Preview video (can wait for v1.1)

### Nice-to-haves after submission

- [ ] Additional locale screenshots + metadata
- [ ] Press kit page at marketing URL
- [ ] Social share graphics

---

## Open questions

1. **Brand identity**: do we have a logo/wordmark locked, or is this a parallel workstream with an outside designer?
2. **Marketing site**: where will Support URL and Privacy Policy live? Does `lastmyle.co` already host content, or do we need to stand that up?
3. **Legal entity on the App Store listing**: `LastMyle` as a DBA, LLC, or individual developer account? Shown publicly under the app name.
4. **Telemetry decision**: will v1 be truly zero-collection, or do we want crash/usage reporting? Changes the Privacy Nutrition Label.
5. **Release pacing**: TestFlight-only for a while, or submit to public App Store once Nam-ho and other friends give feedback?

---

## Related files

- `SESSION_SUMMARY.md` — current build state (1.1 (4)) and TestFlight status
- `docs/testflight.md` — tester brief (adapt text for App Store description)
- `docs/github-actions-testflight.md` — CI build process (same pipeline will produce the final release binary)
- `ios/Upright/Info.plist` — version strings, bundle ID, usage descriptions
- `ios/Upright/Assets.xcassets/AppIcon.appiconset/` — where the app icon lives in the binary
