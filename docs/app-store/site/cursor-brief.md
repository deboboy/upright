# Cursor brief: publish Be Upright pages on lastmyle.co

**Mission:** Add three new pages — `/upright`, `/upright/support`, `/upright/privacy` — to the Last Myle marketing site. Markdown source for each page is inlined below. When this is done, all three URLs must return **HTTP 200** so the Be Upright iOS app can be submitted to the Apple App Store.

**Target repo:** the `lastmyle.co` codebase (separate from the `upright` repo this brief originated from).

**Not a goal:** rewriting the Last Myle site's design system or framework. These three pages should feel like native Last Myle pages, not a transplant.

---

## Context

Be Upright is Last Myle's first iOS app — a real-time posture coach that reads motion from AirPods. Apple requires every App Store submission to have a live Support URL and Privacy Policy URL. The original plan was a separate `apps.lastmyle.co` subdomain, but we pivoted on 2026-11-21 to publish the content as subpaths on the main site for velocity.

The `/upright` prefix leaves room for future Last Myle apps at `/<other-app>` under the same domain.

---

## Routes to add

| Route | Required by Apple? | Role |
|---|---|---|
| `/upright` | optional | Marketing / landing page for Be Upright. Will be used as the "Marketing URL" in App Store Connect. |
| `/upright/support` | **required** | Support page. Used as the "Support URL" in App Store Connect. |
| `/upright/privacy` | **required** | Privacy policy. Used as the "Privacy Policy URL" in App Store Connect. |

All three must return HTTP 200. Apple's submission validator does not care about the HTML content on these pages, only that they resolve.

---

## Source content (inline)

The three pages below are the source of truth. These are also mirrored on GitHub if you'd rather pull from there:

- https://raw.githubusercontent.com/deboboy/upright/master/docs/app-store/site/marketing.md
- https://raw.githubusercontent.com/deboboy/upright/master/docs/app-store/site/support.md
- https://raw.githubusercontent.com/deboboy/upright/master/docs/app-store/site/privacy.md

### Page 1 — `/upright` (marketing)

```markdown
# Be Upright

**Stay stacked. Stay focused.**

A real-time posture coach that runs on your AirPods.

[Download on the App Store →](https://apps.apple.com/app/be-upright)

---

## Catches your slouch before it catches you

Upright uses the motion sensors built into your AirPods to score your posture 25 times a second — live, while you work. No wearable. No camera. Nothing to set up beyond putting your AirPods in.

---

## How it works

1. **Put your AirPods in** and connect to your iPhone.
2. **Calibrate your neutral posture** — sit the way you want to sit.
3. **Start a 25-minute focus session.** Upright tracks every tilt of your head and shows you when you drift.

---

## What you get

- **Live posture score** color-coded from green through amber to red
- **Real-time pitch and roll chart** so you can see your head position change
- **25-minute focus sessions** with gentle in-app coaching copy
- **Session history** with averages, posture distribution, and color bars across every session
- **Zero gear** — just your AirPods and your iPhone

---

## Hardware

Requires AirPods with motion support:

- AirPods Pro (1st or 2nd generation)
- AirPods Max
- AirPods (3rd generation)

Not compatible with AirPods 1st or 2nd generation — they don't have the motion sensors Upright needs.

---

## Privacy

Your posture data stays on your device. Upright doesn't collect, transmit, or share your motion data. No account to create, no cloud sync, no tracking.

Read the full [Privacy Policy](/upright/privacy).

---

## Support

Questions? Email [support@lastmyle.co](mailto:support@lastmyle.co) or visit the [Support page](/upright/support).

---

[Download on the App Store →](https://apps.apple.com/app/be-upright)

© 2026 Last Myle, LLC. Be Upright is an app by Last Myle.
```

### Page 2 — `/upright/support`

```markdown
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

© 2026 Last Myle, LLC
```

### Page 3 — `/upright/privacy`

```markdown
# Be Upright — Privacy Policy

**Last updated: 2026-11-21**

Be Upright is designed to be private by default. This page explains what that means in practice.

## The short version

Be Upright does not collect, transmit, or share any personal information or motion data from your device. There is no account to create, no cloud service, and no third parties involved in your use of the app.

## What Be Upright stores on your device

Be Upright stores the following **on your iPhone only**:

- **Session history** — the start time, duration, average posture score, sample count, and good/warning/slouch percentages for each completed session. Stored in your device's local app storage (iOS `localStorage`) and visible only to you, inside Be Upright.
- **In-memory motion samples** during an active session — head pitch, roll, and yaw readings from your AirPods, used to compute the live posture score and chart. These samples are **not saved** when a session ends; only the summary statistics above are retained.
- **A first-launch flag** indicating that you've seen the welcome screen.

You can delete all local data at any time by tapping Clear in the History and Events cards, or by deleting Be Upright from your iPhone. Uninstalling removes all local data.

## What Be Upright does not do

- We do not collect your motion data
- We do not transmit your motion data or session history off your device
- We do not use any third-party analytics (no Firebase, Mixpanel, Google Analytics, Sentry, or similar)
- We do not use any advertising networks
- We do not track you across apps or websites
- We do not fingerprint your device
- We do not require you to create an account, sign in, or share any identifying information
- We do not share, sell, or otherwise disclose data about you to any third party, because we don't have any to share

## Permissions Be Upright requests

- **Motion & Fitness** — required so the app can read head motion data from your AirPods via Apple's `CMHeadphoneMotionManager`. All motion processing happens on your device; nothing is transmitted. You can revoke this permission at any time in Settings → Privacy & Security → Motion & Fitness. Revoking it will disable posture tracking but won't otherwise affect your use of the app.

Be Upright does not request access to your microphone, camera, contacts, location, photos, notifications, or any other sensitive permission.

## Children

Be Upright is not directed to children under 13 and we do not knowingly collect information from anyone, regardless of age, because we do not collect information at all.

## Changes to this policy

If we change this policy in a way that materially affects what we collect or how we use it, we'll update the "Last updated" date at the top of this page and, if the change is significant, post a notice in the app or on this site. Minor wording changes (clarifications, typo fixes) may be made without notice.

## Contact

Privacy questions: **[support@lastmyle.co](mailto:support@lastmyle.co)**

## Jurisdiction

Be Upright is published by Last Myle, LLC in the United States. Because Be Upright doesn't collect or process personal data, no additional jurisdiction-specific disclosures (GDPR, CCPA, etc.) apply. If this changes in a future version of the app, this page will be updated accordingly before the new version ships.

© 2026 Last Myle, LLC
```

---

## Design guidance

- **Match the existing Last Myle site.** Use the same typography, color tokens, spacing scale, header, and footer that other Last Myle pages use. These pages should read as native site pages, not transplants.
- **Be Upright brand elements you can optionally accent with** (don't override the Last Myle look; just use for small moments like a product thumbnail or a page-top divider):
  - App icon (stacked teal / amber / red dots on off-white): https://raw.githubusercontent.com/deboboy/upright/master/ios/Upright/Assets.xcassets/AppIcon.appiconset/AppIcon-1024.png
  - Posture palette: teal `#0d9488`, amber `#d97706`, red `#e11d48`
  - App background: off-white `#f4f4f5`
  - Tagline: *Stay stacked. Stay focused.*

## App Store screenshots available for the marketing page

Composited 1320 × 2868 PNGs with headline overlays — good as a hero image or gallery on `/upright`:

- Shot 1 (hero, slouch state): https://raw.githubusercontent.com/deboboy/upright/master/docs/app-store/screenshots/01-posture-slouch.png
- Shot 2 (good state): https://raw.githubusercontent.com/deboboy/upright/master/docs/app-store/screenshots/02-posture-good.png
- Shot 3 (motion chart): https://raw.githubusercontent.com/deboboy/upright/master/docs/app-store/screenshots/03-motion-chart.png
- Shot 4 (history): https://raw.githubusercontent.com/deboboy/upright/master/docs/app-store/screenshots/04-history.png

Use shot 1 or shot 2 as the hero. The other two work in a small gallery below the fold if the design calls for it.

---

## Navigation and discoverability

- **`/upright`** — may be surfaced in main nav or a Projects / Apps index page on `lastmyle.co`. This decision belongs to Frank — if he hasn't specified, default to adding a link from wherever Last Myle lists its work, and don't push it into primary nav yet.
- **`/upright/support`** and **`/upright/privacy`** — do **not** add to main nav. They're reachable from in-body and footer links on `/upright` (and from the App Store listing itself). This matches the convention for every App Store app's support and privacy pages.
- The `/upright` marketing copy already contains internal links to `/upright/support` and `/upright/privacy` in the body and the closing section — make sure those stay routable as relative paths.

---

## SEO and metadata

Set these on each page (adapt syntax to whatever meta-tag helper the Last Myle site uses):

| Page | `<title>` | Meta description (~155 char) |
|---|---|---|
| `/upright` | `Be Upright — Stay stacked. Stay focused.` | `Real-time posture coaching from your AirPods. Catches your slouch, rewards good posture, keeps you focused through 25-minute sessions.` |
| `/upright/support` | `Be Upright — Support | Last Myle` | `Help and troubleshooting for the Be Upright iOS app. Common fixes, hardware requirements, and how to contact support.` |
| `/upright/privacy` | `Be Upright — Privacy Policy | Last Myle` | `How Be Upright handles your data. Short version: it doesn't collect or transmit anything. Full policy explains what's stored locally and why.` |

Open Graph + Twitter card:

- `og:title` and `twitter:title` — match the `<title>` above
- `og:description` and `twitter:description` — match the meta description above
- `og:image` and `twitter:image` — use the app icon (1024×1024) for `/upright/support` and `/upright/privacy`; use shot 1 (hero screenshot) for `/upright`
- `og:url` — the canonical URL of each page
- `og:type` — `website` for all three
- `og:site_name` — `Last Myle`

---

## Call-to-action handling

The `/upright` marketing page body includes two `[Download on the App Store →]` calls pointing at `https://apps.apple.com/app/be-upright`. **This URL does not exist yet** — Be Upright has not been approved by Apple at the time of this brief.

Two acceptable approaches:

1. **Point the button at the TestFlight public link until approval.** Frank can provide that URL.
2. **Render the button as disabled / "Coming soon"** until Frank updates this brief with the real App Store URL.

Do not leave the button linking to a 404.

---

## Testing checklist

Before closing out the work:

- [ ] `GET https://lastmyle.co/upright` returns HTTP 200
- [ ] `GET https://lastmyle.co/upright/support` returns HTTP 200
- [ ] `GET https://lastmyle.co/upright/privacy` returns HTTP 200
- [ ] Internal link `/upright/support` on the marketing page resolves without redirect
- [ ] Internal link `/upright/privacy` on the marketing page resolves without redirect
- [ ] All `mailto:support@lastmyle.co` links open the system mail composer
- [ ] Pages render correctly on mobile Safari (viewport meta present, no horizontal scroll)
- [ ] Copyright footer on each page reads `© 2026 Last Myle, LLC`
- [ ] If the Last Myle site supports dark mode, text remains readable on both themes
- [ ] View source: `<title>` and `<meta name="description">` are present per the table above
- [ ] `og:image` is reachable (no broken image)
- [ ] Favicon is set (Last Myle site default is fine)
- [ ] No console errors on page load

---

## Items requiring Frank's input before publish

Pass these back to Frank rather than guessing:

1. **Contact email**: all three pages use `support@lastmyle.co`. Confirm or swap. Candidate alternatives: `hello@lastmyle.co`, `frank@lastmyle.co`.
2. **"Last updated" date** on the privacy policy: currently `2026-11-21` (the date this brief was written). Bump to actual publish date if different.
3. **CTA destination** on the marketing page: TestFlight public link vs. disabled button — see the Call-to-action section above.
4. **Main-nav placement** for `/upright`: should it appear in header nav, a "Projects / Apps" list page, or nowhere until public launch?

---

## Non-goals

- **Do not change the Be Upright markdown copy.** If the copy needs editing, flag it to Frank and he'll edit upstream in the `upright` repo (`docs/app-store/site/*.md`).
- **Do not add per-page analytics.** Be Upright's core pitch is zero tracking. If the Last Myle site already has analytics, leave existing behavior alone; don't add additional tracking just for these three pages.
- **Do not build a CMS or admin for these pages.** Three static pages, nothing more.
- **Do not add JavaScript to `/upright/privacy`** beyond whatever your site framework needs to render markdown. Keep it a plain document page.
- **Do not alter site-wide design tokens.** These pages adapt to the site; the site does not adapt to these pages.
