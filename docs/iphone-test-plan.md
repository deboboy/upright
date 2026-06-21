# iPhone / AirPods Test Plan

## Prerequisites

- Mac with current Xcode.
- iPhone paired with the Mac.
- AirPods model supported by `CMHeadphoneMotionManager`.
- Apple ID / development team for signing.

## Build and run

1. Open `ios/Upright.xcodeproj`.
2. Select the `Upright` scheme.
3. Select your physical iPhone as the destination.
4. Choose a signing team in the target settings if Xcode prompts.
5. Run.

## Permission flow

1. Put on supported AirPods.
2. Launch Upright.
3. Tap **Request Permission**.
4. Grant the iOS motion prompt.
5. Tap **Start Session**.

Expected: `connection` becomes `connected` or `active`, `permission` becomes `granted`, and motion samples begin streaming.

## Failure states to verify

- Permission denied.
- Unsupported or missing AirPods.
- AirPods disconnected mid-session.
- Motion temporarily unavailable.
- App backgrounded while a session is active.
- Web app opened in Safari instead of native shell.

The web app should still boot and fall back to mock mode when native support is unavailable.
