# App Review — Notes to Reviewer

Paste this into the **Notes to Reviewer** field in App Store Connect → App Review Information. 4000-character limit; current draft is ~1900.

The goal: make the hardware requirement unmissable, then give the reviewer a numbered flow that works on the first try. Apps that depend on specialized Apple hardware (AirPods motion, Apple Watch, HomePod, etc.) get bounced regularly when the reviewer can't reproduce the core feature and concludes the app is broken.

---

## Final text to paste

```
HARDWARE REQUIREMENT

Be Upright requires motion-capable AirPods (AirPods Pro 1st or 2nd gen, AirPods Max, or AirPods 3rd gen) to demonstrate posture tracking. The AirPods must be in your ears AND connected as the active audio route on the review iPhone.

Without compatible AirPods present and routed, the Sensor card will show "Connection: disconnected" and "Motion ready: no", the Posture card stays on "Unknown" with score 0, and no motion samples will flow. This is correct behavior when the required hardware is unavailable — Apple's CMHeadphoneMotionManager API does not provide any way to simulate headphone motion without the physical hardware.

CMHeadphoneMotionManager reference: https://developer.apple.com/documentation/coremotion/cmheadphonemotionmanager

HOW TO REVIEW THE CORE FLOW

1. Launch Be Upright. The first-launch landing screen appears; tap "Get started" to enter the main view.
2. Put motion-capable AirPods in your ears, paired to the review iPhone.
3. IMPORTANT: Play a few seconds of any audio on the iPhone (Music, YouTube, anything) to force iOS to route audio to the AirPods. Without this step, iOS may hold the audio route elsewhere and Be Upright will show an audio-route warning in the Posture card instead of starting a session.
4. In Be Upright, scroll to the Sensor card (bottom of the dashboard). Tap "Request Permission" and grant Motion & Fitness access when prompted.
5. Tap "Calibrate Neutral" while sitting in your normal upright posture.
6. Tap "Start Session" in the Focus Timer card. The Posture card updates in real time at 25 Hz. Tilt your head forward (a slouch motion) and the score climbs; the pill transitions from "good" (green) to "warning" (amber) to "slouch" (red). Return to upright and the score falls.
7. Tap "Stop" to end the session. A summary row appears in the History card with the average score, posture distribution, and a color bar.

WHAT THE APP DOES NOT DO

- No account creation, sign-in, or user data collection
- No cloud service, telemetry, analytics, ads, or in-app purchases
- No data leaves the device (privacy policy: https://lastmyle.co/upright/privacy)
- Fully functional offline

CONTACT

If you cannot reproduce the posture-tracking flow or have any questions, please contact Frank Martinez at frank@lastmyle.co.

Thank you for reviewing.
```

---

## Why each section is there

- **Hardware requirement first, in caps.** Reviewers triage dozens of apps a day and skim. Burying the requirement would mean a predictable rejection ("app doesn't work — Posture card stays blank"). Putting it first and explaining *why* the blank-state is correct behavior preempts that rejection path.
- **Explicit API citation** to `CMHeadphoneMotionManager`. Reviewers can cross-reference Apple's own docs and confirm this really is the only way to read AirPods motion. Shows we're using a first-party Apple API, not a hack.
- **Step 3's "IMPORTANT" audio-route note.** This is the single most common first-time-user failure mode (every TestFlight tester so far has hit it). Calling it out upfront saves the reviewer from the same wasted debug cycle.
- **"What the app does not do" section.** Cuts off any lingering questions about whether there's a login, a subscription, a third-party service to inspect, or data flowing somewhere. Four short lines, four potential reject-reason categories preempted.
- **Contact with an actual name and email.** Apple reviewers do sometimes email when they're stuck. Having a real human to reach reduces the odds of a reject-and-email-later loop.

## Things I deliberately did not include

- **The "Haptic" / "Speak" / "Reset" buttons on the Focus Timer card** — they're marked as test actions in the UI and I didn't want to draw reviewer attention to a surface that isn't the core flow. If they ask, the honest answer is "manual triggers for the haptic feedback and speech feedback systems — placeholder UI pending a design pass."
- **The fact that the app is a WKWebView shell over native CoreMotion.** Apple's guideline 4.2 ("Minimum Functionality") sometimes trips up WebView-based apps, but Be Upright clearly has unique device-dependent functionality (AirPods motion) and is not a repackaged website. Volunteering the architecture detail invites scrutiny that wouldn't otherwise happen.
- **Explanations of the posture-scoring math.** Not relevant to a reviewer; they just need to see the score respond to head motion.

## If the reviewer rejects anyway

Most likely reasons and how to respond:

| Rejection reason | Response |
|---|---|
| "App did not demonstrate the posture-tracking feature." | Reply pointing to the hardware requirement and asking what AirPods model the reviewer had available. Offer to have Frank join a brief review call. |
| "App appears to be a web wrapper (4.2)." | Reply explaining the native CoreMotion integration, pointing to `NativeBridge.swift` and `HeadphoneMotionAdapter.swift` as the native modules, and listing the on-device-only motion processing. |
| "Missing export compliance." | Already set — `ITSAppUsesNonExemptEncryption = false` in `Info.plist`. Shouldn't happen but if it does, respond with that fact and a pointer to the Info.plist entry. |
| "Privacy policy URL does not resolve." | Means the `lastmyle.co/upright/privacy` page isn't live yet. Resolve the site publish before resubmitting. |
