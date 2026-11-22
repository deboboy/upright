# Be Upright — marketing site content

Source copy for the three pages that need to be live at `apps.lastmyle.co` before Be Upright can be submitted to the App Store.

## URL plan

| URL | Source file | Purpose |
|---|---|---|
| `https://apps.lastmyle.co/upright` | `marketing.md` | Marketing / landing page. Referenced from App Store Connect as the optional Marketing URL. |
| `https://apps.lastmyle.co/upright/support` | `support.md` | Support page. **Required by Apple** — Support URL in App Store Connect must resolve to HTTP 200. |
| `https://apps.lastmyle.co/upright/privacy` | `privacy.md` | Privacy policy. **Required by Apple** — Privacy Policy URL in App Store Connect must resolve to HTTP 200. |

The `/upright` subpath leaves room for future apps at `/<other-app>` under the same `apps.lastmyle.co` subdomain.

## Content status

All three files are **Markdown source only** — no HTML, CSS, or deploy tooling in this directory. When you stand up `apps.lastmyle.co`, you choose the static site generator / framework / deploy path separately and drop this copy in.

If you want the pages prototyped as styled static HTML (matching the app palette and the stacked-dots icon), say so and I'll build a `site/` directory with real HTML + CSS ready to deploy to Vercel / Netlify / Cloudflare Pages.

## Things that still need a decision before publish

- **Contact email** — all three files use `support@lastmyle.co` as a placeholder. Swap to whatever address you actually want to receive mail at (common alternatives: `hello@lastmyle.co`, `frank@lastmyle.co`).
- **Last-updated date** on the privacy policy — currently set to 2026-11-21 (today). Bump when you actually publish.
- **Copy voice for marketing page** — current draft matches the App Store description tone (direct, brief). If you want it longer / more emotional / more technical, flag it.
