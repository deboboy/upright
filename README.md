# Upright

Upright is a hybrid iOS posture-tracking app: a thin Swift/WKWebView shell owns AirPods motion access, while the product experience lives in a portable web codebase.

## What is included

- **iOS shell**: Swift app with `WKWebView`, Core Motion headphone-motion adapter, native bridge, haptics, speech, and settings actions.
- **Web app**: no-build static SPA for onboarding, session state, posture scoring, timer, charts, and history.
- **Bridge SDK**: versioned JS interface matching the Swift bridge contract.
- **Browser dev shim**: replays recorded AirPods motion traces so the web app can be tested without an iPhone.
- **Docs**: architecture, bridge contract, and iPhone/AirPods test plan.

## Repo layout

```text
ios/Upright/                         Swift iOS shell
ios/Upright.xcodeproj/               Xcode project
web/                                 Static web app + bridge SDK + mock traces
docs/                                Architecture and test docs
scripts/create_repo_files.py         Regenerates this repo layout
```

## Local web dev

```bash
npm run serve
```

Open `http://localhost:5173`. The app uses the mock AirPods trace by default in a normal browser.

## iPhone / AirPods testing

Use a **physical iPhone** for real AirPods motion. The simulator cannot access headphone sensors.

### Prerequisites

- Mac with current Xcode
- iPhone connected (USB or wireless debugging after first USB pair)
- **Developer Mode** enabled on the iPhone (Settings → Privacy & Security → Developer Mode) on iOS 16+
- Supported AirPods in your ears and connected to the **iPhone** (Pro, Max, 3rd gen, etc.)
- Apple ID added in Xcode → Settings → Accounts

### First-time Xcode setup

1. Open `ios/Upright.xcodeproj` in Xcode.
2. In the **left sidebar**, click the **blue Upright project icon at the top** of the file tree (not a `.swift` file).
3. In the **center panel**, use the **TARGETS** section on the left (not the menu bar) and select **Upright**.
4. Open the **Signing & Capabilities** tab at the top of the center panel.
5. Check **Automatically manage signing** and choose your **Team** (personal Apple ID is fine).
6. If the bundle ID conflicts, change it to something unique (e.g. `com.yourname.upright`).

On first run, macOS may prompt for your **Mac login password** (not your Apple ID) so `codesign` can access your development certificate. Click **Always Allow**.

If the app installs but will not open, trust the developer on the phone: **Settings → General → VPN & Device Management**.

### Build and run

1. Select the **Upright** scheme.
2. Choose your **iPhone** as the run destination (not a simulator).
3. If you changed web files or pulled new commits, do a clean build first:
   - **Product → Clean Build Folder** (⇧⌘K)
4. Press **Run** (▶).

After launch, the top-right badge should say **Native shell** (not “Browser mock” or “JS error”). The **Sensor** card should populate with mode, permission, connection, and device.

### Live session flow

1. Put on AirPods connected to the iPhone.
2. Tap **Request Permission** and allow the iOS motion prompt.
3. Confirm **Permission** shows `granted` and **Connection** shows `connected` or `active`.
4. Sit in your normal posture and tap **Calibrate Neutral** (optional but recommended).
5. Tap **Start Session** in the Focus Timer card.
6. Move your head slowly — **Posture** score and pill (good / warning / slouch) should update, **Motion** sample count should climb (~25 Hz), and the chart should draw pitch/roll lines.
7. Tap **Stop** when finished. Check the **Events** log for `Session started.` / `Session stopped.`

### Troubleshooting

| Symptom | What to try |
|--------|-------------|
| “Signing requires a development team” | Set Team under TARGETS → Signing & Capabilities |
| Keychain / `codesign` password prompt | Use your **Mac login password**; click Always Allow |
| Badge stuck on “Detecting…” or “JS error” | Clean Build Folder, rebuild, run on device again |
| Badge says “Browser mock” | You are not in the native shell; rebuild and run from Xcode on the phone |
| Sensor fields show dashes | Scroll to **Events** for errors; tap **Request Permission** again |
| Start Session does nothing | Check **Events** log; ensure permission is `granted` and AirPods are in ears |
| Permission stays `unknown` | Tap **Request Permission**; AirPods must be worn for the motion prompt |
| No motion / unsupported | Use supported AirPods on the phone, not the simulator |

More scenarios (disconnect mid-session, backgrounding, etc.) are in `docs/iphone-test-plan.md`.

For distributing builds to friends via TestFlight, see `docs/testflight.md`.

### App UI (quick reference)

| Card / control | Purpose |
|----------------|---------|
| **Sensor** | AirPods connection, motion permission, sample rate |
| **Posture** | Slouch score and good / warning / slouch state |
| **Focus Timer** | Start/stop a tracked session; **Haptic**, **Speak**, **Reset** are manual test actions for native feedback |
| **Motion** | Live pitch/roll chart and sample count |
| **Events** | Bridge and session log (useful when debugging) |

## Native bridge v1

Calls:

- `ready()`
- `headphones.getStatus()`
- `headphones.requestPermission()`
- `headphones.startUpdates({ sampleRateHz })`
- `headphones.stopUpdates()`
- `headphones.calibrateNeutral()`

Events:

- `motion`
- `status`
- `interruption`
- `error`

See `docs/bridge-contract.md` for schemas.
