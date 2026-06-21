# Architecture

Upright uses a three-layer design:

1. **Native iOS shell**: Swift, `WKWebView`, `CMHeadphoneMotionManager`, permission handling, lifecycle hooks, haptics, speech, and settings actions.
2. **Bridge layer**: `web/bridge-sdk.js` plus `ios/Upright/NativeBridge.swift` define a narrow, versioned RPC/event contract.
3. **Web app layer**: static SPA owns onboarding, session state, posture scoring, timer logic, charts, history, and exports.

## Data flow

- JS calls native through `window.webkit.messageHandlers.nativeBridgeWithReply.postMessage(...)`.
- Native replies with promise results through `WKScriptMessageHandlerWithReply`.
- Native pushes streams back to JS with `window.__dispatchNativeEvent(type, payload)`.
- Motion samples use radians for raw values; the web app converts to degrees for display.

## Responsibility split

Native owns:

- AirPods/headphone motion permission and availability.
- Motion update start/stop.
- Sanitized motion samples and connection/interruption events.
- Haptics, speech, and app-settings actions.

Web owns:

- Neutral calibration UX and posture math.
- Slouch detection thresholds and hysteresis.
- Focus timer, alerts, charts, session summaries, and history.
- Mock/browser development mode.
