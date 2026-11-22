# App Store screenshots

Four composited screenshots for the App Store Connect listing of **Be Upright**.

All files are **1320 × 2868 px** (iPhone 6.9" / iPhone 16 Pro Max class), 8-bit sRGB PNG. Apple uses this as the baseline for iPhone screenshots on new submissions; smaller device sizes are generated from these.

## Shot list

Upload in this order. The first two shots are what appears above the fold in the App Store listing.

| # | File | Headline | Rationale |
|---|------|----------|-----------|
| 1 | `01-posture-slouch.png` | *Catches your slouch.* | Hero shot — slouch state with score 51 and coaching copy. Demonstrates the core product value (real-time posture detection) at a glance. |
| 2 | `02-posture-good.png` | *Stay stacked. Stay focused.* | The positive flip side — good state with score 12 and encouragement copy. Reinforces the brand tagline. |
| 3 | `03-motion-chart.png` | *Live motion from your AirPods.* | Shows the unique tech — pitch and roll chart at 25 Hz driven by AirPods motion. Addresses "how does this even work?". |
| 4 | `04-history.png` | *Every session. Every score.* | Longitudinal value — two real sessions with contrasting color bars (98% good vs 83% good / 7% slouch). Shows the app is useful over time, not just in one session. |

Apple requires at least 3 iPhone screenshots; 4 is above the floor. A planned fifth shot showing the Sensor card ("Zero gear. Zero setup.") was dropped because the raw capture included a `Start failed: AirPods are not the active audio route…` event in the Events log that would read as a failure state in a marketing context.

## Composition

- Off-white background (`#f4f4f5`) matching the app and app icon
- Two-line bold headline centered at top (Arial Bold stand-in for SF Pro Display, 108 pt)
- Supporting subhead below (Helvetica Neue regular, 42 pt, muted `#52525b`)
- Full-width 3-stop posture-gradient accent (teal `#0d9488` → amber `#d97706` → red `#e11d48`, 16 px tall)
- Raw iPhone screenshot centered (scaled to fit 2180 px tall, preserving aspect)
- "Upright" wordmark anchored at bottom center

## Source

- Raw iPhone captures: `build/app-store-shots/raw/` (not tracked — iPhone 14 at 1170 × 2532 native)
- Composition pipeline: ImageMagick (`magick ... -composite`) — see the compose_shot bash function in the Nov 21 session commit for exact parameters
- Headlines and subheads: finalized in `SESSION_SUMMARY.md` under the Nov 21 session resume

## Uploading

App Store Connect → Apps → Be Upright → **Distribution** → App Store tab → iPhone 6.9" Display section → drag the four PNGs in listing order.

Screenshots can be swapped without a new binary submission.
