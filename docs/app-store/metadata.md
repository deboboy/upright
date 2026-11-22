# App Store Connect — text metadata

Paste-ready values for the Be Upright listing. Last reviewed 2026-11-21.

## App information

| Field | Value | Count / limit |
|---|---|---|
| **App Name** | `Be Upright` | 14 / 30 |
| **Subtitle** | `AirPods posture coach` | 22 / 30 |
| **Bundle ID** | `com.lastmyle.upright` | immutable |
| **Primary Category** | Health & Fitness | — |
| **Secondary Category** | Productivity | — |
| **Content Rights** | Does not contain, show, or access third-party content | — |

## Seller & copyright

| Field | Value |
|---|---|
| **Seller name** (displayed on listing) | `Last Myle, LLC` |
| **Copyright** | `© 2026 Last Myle, LLC` |

## Marketing & support URLs

All three live as subpaths on the main `lastmyle.co` site. **Submission is blocked until these are published**. Page content drafted in `docs/app-store/site/`; handoff brief for the `lastmyle.co` codebase at `docs/app-store/site/cursor-brief.md`.

| Field | URL | Required? | Status |
|---|---|---|---|
| **Marketing URL** | `https://lastmyle.co/upright` | optional | pending publish |
| **Support URL** | `https://lastmyle.co/upright/support` | required | pending publish |
| **Privacy Policy URL** | `https://lastmyle.co/upright/privacy` | required | pending publish |

## Promotional text — 170 char limit

Editable after submission without a new binary.

> Turn your AirPods into a real-time posture coach. Catches your slouch, rewards good posture, and keeps you focused through 25-minute sessions.

141 / 170 characters.

## Description — 4000 char limit

```
Catches your slouch before it catches you.

Upright turns your AirPods into a real-time posture coach. Put them in your ears, start a focus session, and get live feedback on how your head is carried over your shoulders — while you work, read, or write.

HOW IT WORKS

1. Put your AirPods in and connect to your iPhone.
2. Calibrate your neutral posture — sit the way you want to sit.
3. Start a 25-minute focus session. Upright scores your posture 25 times a second using the motion sensors built into your AirPods.

WHAT YOU GET

• Live posture score, color-coded from green (good) through amber (warning) to red (slouch)
• Real-time pitch and roll chart so you can see your head position change in real time
• 25-minute focus sessions with gentle in-app coaching copy
• Session history with average scores, good/warning/slouch percentages, and color bars across every session
• Zero gear — no wearable, no extra hardware, just your AirPods and your iPhone

HARDWARE

Requires AirPods with motion support:
• AirPods Pro (1st or 2nd generation)
• AirPods Max
• AirPods (3rd generation)

Not compatible with AirPods 1st or 2nd generation — they don't have the motion sensors Upright needs.

PRIVACY

Your posture data stays on your device. Upright doesn't collect, transmit, or share your motion data. No account to create, no cloud sync, no tracking.

Stay stacked. Stay focused.
```

~1500 / 4000 characters.

## Keywords — 100 char limit, comma-separated

```
focus,timer,pomodoro,ergonomics,slouch,neck pain,back pain,wfh,desk,sitting,wellness,motion
```

99 / 100 characters. Deliberately omits `airpods`, `posture`, `coach`, `be`, `upright` — Apple indexes App Name and Subtitle separately, so repeating them here wastes characters.

## App Review Information

| Field | Value |
|---|---|
| **Contact — First name** | Frank |
| **Contact — Last name** | Martinez |
| **Contact — Email** | `frank@lastmyle.co` |
| **Contact — Phone** | (fill in) |
| **Demo account** | N/A (no sign-in) |
| **Notes to reviewer** | See `docs/app-store/review-notes.md` for the paste-ready text and rationale. |

The Notes to Reviewer field must call out that Upright requires motion-capable AirPods (Pro / Max / 3rd gen) to demonstrate the posture-tracking path. Without them, the Sensor card shows `disconnected` and the Posture card stays on `Unknown`. This is the single most common cause of App Review rejections for headphone-motion apps.

## Order of operations for submission

1. Publish the three pages from `docs/app-store/site/` onto `lastmyle.co` at `/upright`, `/upright/support`, `/upright/privacy`. Handoff brief for the Cursor agent working the `lastmyle.co` codebase: `docs/app-store/site/cursor-brief.md`.
2. Verify each of the three URLs returns HTTP 200.
3. Fill in the fields above in App Store Connect.
4. Upload the four screenshots from `docs/app-store/screenshots/`.
5. Complete App Privacy (Nutrition Label) and Age Rating questionnaires.
6. Write Notes to Reviewer calling out the AirPods requirement.
7. Pick build 1.1 (7) (or newer) for submission.
8. Submit.
