# TestFlight Beta — Friend Testing Guide

How to distribute Upright to friends on their iPhones and AirPods.

## Overview

Plugging an iPhone into Xcode only works for **your** device (or a few devices registered on your dev team). For friends, use **TestFlight** — Apple's standard beta distribution channel.

---

## What You Need First

### 1. Apple Developer Program ($99/year)

Enroll at [developer.apple.com/programs](https://developer.apple.com/programs).

TestFlight for friends requires a **paid** Apple Developer account. A free Apple ID in Xcode is enough for personal device testing only.

### 2. App Store Connect

Sign in at [appstoreconnect.apple.com](https://appstoreconnect.apple.com) and create an app record:

| Field | Value |
|-------|-------|
| Name | Be Upright |
| Bundle ID | `com.lastmyle.upright` (must match Xcode) |
| SKU | e.g. `upright-ios` |

Fill in **App Privacy** details (motion/sensor usage; Upright does not collect account data today).

---

## Ship to TestFlight (One-Time Setup)

Allow about 30–60 minutes for the first upload and processing.

### Step 1 — Configure signing in Xcode

**TARGETS is not a menu-bar item.** It is a section in the project settings panel.

1. Open `ios/Upright.xcodeproj` in Xcode.
2. In the **left sidebar** (Project Navigator), click the **blue Upright icon at the very top** of the file tree — the one that looks like an app blueprint, **not** a `.swift` file or the `web/` folder.
3. The **center panel** opens the project editor. On the **left edge of that center panel**, you should see two labeled sections:
   - **PROJECT** → Upright
   - **TARGETS** → Upright
4. Under **TARGETS**, click **Upright** (the app target, not the project row above it).
5. At the **top of the center panel**, open the **Signing & Capabilities** tab.
6. Enable **Automatically manage signing**.
7. Choose your **paid Developer Program team** (not a personal/free team if you want TestFlight).

**If you do not see PROJECT / TARGETS:** you likely selected a source file instead of the project. Click the blue **Upright** root item again in the left sidebar. If the left sidebar is hidden, show it with **View → Navigators → Project** (⌘1).

Bundle ID in the project: **`com.lastmyle.upright`**. Change it in Xcode only if you need a unique ID for your Apple account.

### Step 2 — Archive the app

1. Scheme: **Upright**.
2. Run destination: **Any iOS Device (arm64)** — not a simulator.
3. **Product → Clean Build Folder** (⇧⌘K) if you recently changed web files.
4. **Product → Archive**.
5. In the Organizer window: **Distribute App** → **App Store Connect** → **Upload**.

**Use Product → Archive on your Mac** — not **Start Build** in Xcode Cloud. Cloud builds are optional CI; TestFlight upload works from a local archive.

**Can't upgrade macOS / Xcode?** Use **GitHub Actions** to build and upload from the cloud. Your MacBook only needs `git push` and GitHub secrets — see `docs/github-actions-testflight.md`.

### Step 3 — Enable TestFlight

1. In App Store Connect, open **Upright** → **TestFlight**.
2. Wait for the build to finish processing (often 10–30 minutes).
3. Add testers:
   - **Internal testers** — up to 100 people on your App Store Connect team; available immediately.
   - **External testers** — friends by email; the **first external build** requires **Beta App Review** (often 24–48 hours).

Friends install the **TestFlight** app from the App Store and accept your email invite.

### Step 4 — Future uploads

For each new build you send to testers:

1. Bump **Build** in Xcode (e.g. `1` → `2`). **Version** can stay `1.0` until you want a visible version change.
2. Archive and upload again.
3. TestFlight notifies testers when the new build is ready.

---

## Upload Validation Errors

### “SDK version issue … must be built with the iOS 26 SDK … Xcode 26 or later”

Apple requires the **latest Xcode** for App Store Connect uploads. Your archive was built with an older SDK (e.g. iOS 18.2 / Xcode 16).

**Fix:**

1. Install **Xcode 26** (or the latest Xcode from the Mac App Store / [developer.apple.com/xcode](https://developer.apple.com/xcode)).
2. Open the project in the new Xcode.
3. **Product → Clean Build Folder** (⇧⌘K).
4. **Product → Archive** again and re-upload.

Check your version: **Xcode → About Xcode**.

**Alternative:** If you cannot install Xcode 26 locally, use `docs/github-actions-testflight.md` — GitHub builds with the latest Xcode and uploads to TestFlight. Your MacBook does not need a macOS upgrade.

### “Invalid bundle … UIInterfaceOrientationPortrait … iPad multitasking”

The app was set to run on **iPad** with portrait-only orientations. iPad multitasking requires all orientations unless the app is iPhone-only.

**Fix (already applied in repo):** Upright is **iPhone only** (`TARGETED_DEVICE_FAMILY = 1`). Pull latest, clean, archive, and upload again.

If you still see this in Xcode: **TARGETS → Upright → General → Supported Destinations** — ensure only **iPhone** is listed (remove iPad if present).

---

## Instructions for Your Friends (Copy/Paste)

Share this with beta testers:

> **Upright beta — how to test**
>
> 1. Install **TestFlight** from the App Store and open the invite link or email from Frank.
> 2. Use a **real iPhone** (the simulator cannot access AirPods motion).
> 3. Wear **AirPods Pro, AirPods Max, AirPods (3rd generation)**, or another supported model with head tracking — buds must be **in your ears** and connected to the phone.
> 4. Open **Upright** → tap **Get started** on first launch.
> 5. On the **Sensor** card, confirm **Motion ready: yes**, then tap **Start Session**.
> 6. Optional: sit in your normal posture and tap **Calibrate Neutral**.
> 7. Move your head slowly — the **Posture** score and **Motion** chart should update.
> 8. Tap **Stop** when finished. Completed sessions may appear in **History**.
>
> **If something fails:** scroll to the **Events** card at the bottom and send a screenshot of the **Sensor** card and **Events** log.

---

## Device & Hardware Requirements

| Requirement | Details |
|-------------|---------|
| iPhone | Physical device required |
| iOS | 14.0 or later |
| AirPods | Models with head tracking (Pro, Max, 3rd gen, Beats Fit Pro, etc.) |
| AirPods placement | In ears (Automatic Ear Detection affects motion) |
| Motion permission | iOS prompts on first use — tap **Allow** |
| Not supported | Simulator; most non–head-tracking earbuds |

---

## In-App Test Flow (Quick Reference)

1. Put on AirPods connected to the iPhone.
2. Open Upright — badge should say **Native shell**.
3. Sensor card: **Permission** = `granted`, **Motion ready** = `yes`.
4. Tap **Calibrate Neutral** (optional, recommended).
5. Tap **Start Session** in the Focus Timer card.
6. Confirm **Motion** sample count climbs (~25 Hz) and the chart updates.
7. Tap **Stop** — check **History** for a saved session (needs a few seconds of samples).

---

## Pre-Launch Checklist (Before Inviting Friends)

- [ ] Apple Developer Program active.
- [ ] App created in App Store Connect with bundle ID `com.lastmyle.upright`.
- [ ] Archive uploaded and build shows **Ready to Test** in TestFlight.
- [ ] You installed the build on **your** iPhone via TestFlight and completed a full session.
- [ ] Feedback channel chosen (group chat, email, GitHub issues, etc.).
- [ ] Friends brief copied (see above).

---

## Troubleshooting (For Testers)

| Symptom | What to try |
|--------|-------------|
| TestFlight invite missing | Check spam; confirm email matches Apple ID |
| App won't install | Update iOS to 14+; free storage on iPhone |
| Badge says **Browser mock** or **JS error** | Report to developer — wrong build or corrupt install |
| **Motion ready: no** | Re-seat AirPods in ears; toggle Bluetooth; reopen app |
| **Connection: disconnected** | Wear AirPods in ears; wait a few seconds; tap **Start Session** anyway if Motion ready is yes |
| Permission stays unknown | AirPods must be worn when iOS shows the motion prompt |
| No chart / 0 samples | Tap **Start Session**; check **Events** for errors |
| App crashed while scrolling | Update to latest TestFlight build |

More scenarios: `docs/iphone-test-plan.md`.

---

## Distribution Alternatives (Usually Not for Friends)

| Method | Best for |
|--------|----------|
| USB + Xcode Run | Your device only |
| Ad Hoc IPA | Fixed device list; requires each device's UDID |
| Development team installs | Few people added to your Apple team |

**TestFlight** is the right default for friend beta testing.

---

## Project Reference

| Item | Value |
|------|-------|
| Bundle ID | `com.lastmyle.upright` |
| Display name | Upright |
| Marketing version | 1.0 |
| Minimum iOS | 14.0 |
| Motion usage string | `NSMotionUsageDescription` in `ios/Upright/Info.plist` |
| Local dev testing | `README.md` → iPhone / AirPods testing |
| Bridge / API | `docs/bridge-contract.md` |

---

## Feedback to Collect

Ask testers to note:

- iPhone model and iOS version
- AirPods model
- Whether **Motion ready** showed yes before starting
- Whether posture states (good / warning / slouch) felt accurate
- Any crashes, freezes, or confusing UI
- Screenshot of **Sensor** + **Events** if anything failed
