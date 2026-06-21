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

## iPhone test

1. Open `ios/Upright.xcodeproj` in Xcode on a Mac.
2. Select your iPhone as the run destination.
3. Sign with your Apple ID / development team.
4. Run the `Upright` scheme.
5. Connect compatible AirPods and grant motion permission when prompted.
6. In the app, tap **Start Session**. Motion samples stream from AirPods into the web UI.

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
