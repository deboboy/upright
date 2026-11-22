# Be Upright — support page

Source copy for `https://lastmyle.co/upright/support`. Must resolve to HTTP 200 before App Store submission.

---

# Be Upright — Support

Need help with Be Upright? Most issues fall into one of a few categories below. If you can't find your answer here, email **[support@lastmyle.co](mailto:support@lastmyle.co)** and we'll get back to you.

## Quick fixes

### Posture tracking isn't working — the score stays on 0

The most common cause: your AirPods are paired to your iPhone but your iPhone isn't currently routing audio to them. This happens a lot when you've been using the AirPods with your Mac or iPad — iOS keeps the audio route elsewhere until something plays on the iPhone.

**Fix:** Play a few seconds of any audio on your iPhone (a YouTube clip, a Music track, anything). Then open Be Upright and tap Start Session. The Posture card should start updating within a second or two.

Starting with build 1.1 (5), Be Upright will tell you directly in the Posture card when the audio route is wrong instead of showing an empty session.

### "AirPods are not the active audio route" message

Same cause as above — just caught earlier by the app. Play a short audio clip on your iPhone, then tap Start Session again.

### The Sensor card shows "connected" but posture stays on Unknown

Three things to check in order:

1. Are your AirPods actually in your ears? Headphone motion only emits samples when the AirPods detect your ears.
2. Are your AirPods a motion-capable model? See the Hardware section below.
3. Did you tap Start Session? Posture only updates during an active session.

### My posture score is always "good" even when I'm slouching

Two possibilities:

1. **You calibrated while slouching.** Sit as upright as you can, then tap Calibrate Neutral. The app learns your "neutral" from your position when you tap, so calibrating in a slouch bakes the slouch into neutral.
2. **Your torso is slouching but your head is still level.** Be Upright measures head position (that's what the AirPods motion sensors can see). If your shoulders round forward but you keep your eyes on the screen, your head barely moves. Try letting your head drop with your shoulders — you'll see the score climb.

### The permission dialog never appeared

Check Settings → Privacy & Security → Motion & Fitness. Make sure Be Upright is toggled on. If it's not listed there, tap Request Permission in the Sensor card inside Be Upright.

## Hardware

Be Upright requires AirPods with motion sensors:

- **AirPods Pro** (1st generation or 2nd generation)
- **AirPods Max**
- **AirPods** (3rd generation)

The following AirPods models **do not have motion sensors** and cannot be used with Be Upright:

- AirPods (1st generation)
- AirPods (2nd generation)

iPhone: iOS 15.0 or later. iPhone only (not iPad).

## How Be Upright works (technical)

Be Upright uses Apple's `CMHeadphoneMotionManager` to read pitch, roll, and yaw from your AirPods 25 times a second. The app computes a "slouch score" from the difference between your current head position and the neutral position you calibrated to. Everything happens on your device — no data leaves your iPhone.

See the full [Privacy Policy](/upright/privacy) for what Be Upright does and doesn't collect.

## Still stuck?

Email **[support@lastmyle.co](mailto:support@lastmyle.co)** with:

- The iPhone model you're using (Settings → General → About → Model Name)
- The AirPods model you're using
- The iOS version (Settings → General → About → iOS Version)
- The Be Upright version (bottom of the Sensor card, or TestFlight / App Store page)
- A short description of what's happening and what you've already tried

We usually reply within 24 hours.

---

<small>© 2026 Last Myle, LLC</small>
