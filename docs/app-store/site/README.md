# Be Upright — marketing site content

Source copy for the three pages that need to be live on `lastmyle.co` before Be Upright can be submitted to the App Store.

Publishing happens in the `lastmyle.co` codebase (a separate repo), not in this one. The handoff brief for the Cursor agent working that repo is at [`cursor-brief.md`](./cursor-brief.md).

## URL plan

| URL | Source file | Purpose |
|---|---|---|
| `https://lastmyle.co/upright` | `marketing.md` | Marketing / landing page. Referenced from App Store Connect as the optional Marketing URL. |
| `https://lastmyle.co/upright/support` | `support.md` | Support page. **Required by Apple** — Support URL in App Store Connect must resolve to HTTP 200. |
| `https://lastmyle.co/upright/privacy` | `privacy.md` | Privacy policy. **Required by Apple** — Privacy Policy URL in App Store Connect must resolve to HTTP 200. |

The `/upright` subpath leaves room for future Last Myle apps to live at `/<other-app>` under the same domain.

## Content status

All three files are **Markdown source only** — no HTML, CSS, or deploy tooling in this directory. The `lastmyle.co` codebase (whatever framework it uses) is where these get turned into real pages; `cursor-brief.md` tells that codebase's agent what to do.

## Things that still need a decision before publish

- **Contact email** — all three files use `support@lastmyle.co` as a placeholder. Swap to whatever address you actually want to receive mail at (common alternatives: `hello@lastmyle.co`, `frank@lastmyle.co`).
- **Last-updated date** on the privacy policy — currently set to 2026-11-21 (today). Bump when you actually publish.
- **Copy voice for marketing page** — current draft matches the App Store description tone (direct, brief). If you want it longer / more emotional / more technical, flag it.
