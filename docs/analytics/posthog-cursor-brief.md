# Cursor brief: track Be Upright pages in PostHog

**Mission:** PostHog is already installed and initialized in the `lastmyle.co` codebase. Add explicit, named tracking for the Be Upright pages so we can analyze funnel behavior cleanly without wading through autocapture noise.

**Target repo:** `lastmyle.co` (separate from the `upright` repo this brief originated from).

**Pages in scope:**

- `/upright` — marketing landing
- `/upright/support` — support
- `/upright/privacy` — privacy policy

---

## Step 0 — verify what's already captured

Before adding anything, inspect the existing PostHog integration in the `lastmyle.co` codebase and confirm:

1. **Where is `posthog.init(...)` called?** (Usually root layout / entry point. Note whether it's wrapped in a provider/hook.)
2. **Is `autocapture` enabled?** (`autocapture: true` is the default and captures link clicks as `$autocapture` events.)
3. **Is pageview tracking enabled?** (`capture_pageview: true` default, or Next.js-style router-change hook.)
4. **Are there any existing event-naming conventions** in the codebase? Prefer those over the suggestions below if they're established.

If all three of (a) pageviews, (b) autocapture, (c) a working PostHog init are already in place, hitting `/upright`, `/upright/support`, and `/upright/privacy` will already produce raw event data without any changes. The additions in this brief are about **surfacing the right events as named, queryable primitives** — not about enabling tracking from scratch.

Report back if the integration is different from the assumed shape (e.g. PostHog is off, autocapture is disabled by design, events use a custom wrapper) before applying the changes below.

---

## Step 1 — custom events to add

Three events, in priority order. All use **snake_case** names and properties (PostHog convention and matches what the dashboards/insights expect).

### Event 1 — `app_store_cta_click` (conversion-critical)

Fire when a visitor clicks either "Download on the App Store →" link on `/upright`. This is the single most important conversion event for the Be Upright listing page.

**Properties:**

| Property | Type | Values | Why |
|---|---|---|---|
| `cta_position` | string | `"hero"` or `"footer"` | Distinguishes the two CTAs on the page so you can A/B the above-fold vs below-fold placement later. |
| `destination_url` | string | the full App Store URL | Captured for future-proofing in case the URL changes (e.g. when a per-locale link is used). |

**Where:** both CTA links in the `/upright` page component. The two links currently point at `https://apps.apple.com/app/be-upright/id6785146509`.

### Event 2 — `support_email_click`

Fire when a visitor clicks any `mailto:support@lastmyle.co` link. Tracks support-demand interest across both `/upright` (one link in the Support section) and `/upright/support` (two or three links).

**Properties:**

| Property | Type | Values | Why |
|---|---|---|---|
| `source_page` | string | `"marketing"`, `"support"`, or the current path | Lets you tell "support requests from users still reading marketing" from "support requests from users on the support page itself." |

### Event 3 — `upright_outbound_link_click`

Fire when a visitor clicks any external link from the Be Upright pages (e.g. the `CMHeadphoneMotionManager` reference on `/upright/support`, or future links to blog posts). Low priority — autocapture may already give you this via `$autocapture` with the right properties.

**Properties:**

| Property | Type | Values |
|---|---|---|
| `href` | string | the clicked URL |
| `link_text` | string | the visible text of the link |
| `source_page` | string | path of the page where the click happened |

Skip this one if autocapture already provides sufficient resolution for outbound clicks.

---

## Step 2 — implementation guidance

The exact code depends on the framework the `lastmyle.co` site uses. Here are the idioms for the common cases.

### React / Next.js

```jsx
import posthog from 'posthog-js';

// in the CTA component on /upright
<a
  href="https://apps.apple.com/app/be-upright/id6785146509"
  onClick={() =>
    posthog.capture('app_store_cta_click', {
      cta_position: 'hero', // or 'footer' for the lower CTA
      destination_url: 'https://apps.apple.com/app/be-upright/id6785146509',
    })
  }
>
  Download on the App Store →
</a>
```

### Astro / vanilla

```html
<a
  href="https://apps.apple.com/app/be-upright/id6785146509"
  data-ph-capture="app_store_cta_click"
  data-ph-props='{"cta_position":"hero","destination_url":"https://apps.apple.com/app/be-upright/id6785146509"}'
>
  Download on the App Store →
</a>

<script>
  // in a shared client script
  import posthog from 'posthog-js';
  document.querySelectorAll('[data-ph-capture]').forEach((el) => {
    el.addEventListener('click', () => {
      const name = el.dataset.phCapture;
      const props = el.dataset.phProps ? JSON.parse(el.dataset.phProps) : {};
      posthog.capture(name, props);
    });
  });
</script>
```

### Wrapper helper

If `lastmyle.co` already has a small helper for capturing events (e.g. a `trackEvent(name, props)` function), **use that instead of calling `posthog.capture` directly**. Consistency with the rest of the site matters more than the exact form here.

---

## Step 3 — do not break mailto clicks

The naive wiring on `mailto:` links can swallow the click if the handler delays navigation or if the link is intercepted by a router. Verify after wiring:

- Clicking the `mailto:support@lastmyle.co` link still opens the user's mail client
- Clicking the App Store CTA still navigates to the App Store (the capture call is fire-and-forget; PostHog's SDK queues events locally and does not block navigation)

If there are issues, PostHog ships a `beforeunload` queue flush — events dispatched right before page navigation are preserved via `sendBeacon`.

---

## Step 4 — define PostHog Insights after data lands

Not a code change — a PostHog-side setup. After events start flowing (usually within minutes), create:

1. **Funnel**: `/upright` pageview → `app_store_cta_click` → App Store (end — tracked externally via App Store Connect Analytics). The App Store Connect side isn't observable in PostHog, but `app_store_cta_click` as the "exit" event approximates it well.
2. **Trend**: `app_store_cta_click` count by week, broken down by `cta_position`. Reveals whether hero or footer CTA drives more clicks.
3. **Trend**: `support_email_click` count. If this starts rising, check in-app support UX.
4. **Session Recording filter**: `$pageview` where `$current_url` matches `/upright/*` — lets you watch real sessions on the Be Upright pages for qualitative insight.

These can be created from the PostHog dashboard or via the PostHog MCP server if that's installed in your editor.

---

## Step 5 — don't track anything privacy-sensitive

The site's existing PostHog setup governs what personal data is captured (typically IP, user agent, approximate geo, with configurable anonymization). This brief adds only **behavioral click events on public marketing pages**. No new personal identifiers are introduced.

Specifically, **do not**:

- Capture email addresses or contact form contents (none exist on these pages anyway)
- Pass `distinct_id` from the iOS app context — the app is zero-collection by design and must stay that way
- Add persistent user identification on the privacy or support pages beyond whatever the rest of the site already does

The Be Upright app's privacy policy at `/upright/privacy` explicitly rules out third-party analytics *in the app*. Site-level analytics on the marketing pages is outside the app's privacy scope and is not in conflict, but keep the two contexts separate.

---

## Testing checklist

Before marking done:

- [ ] Visit `/upright` in a browser with PostHog's Toolbar enabled (or check the PostHog Live Events panel). Clicking the hero CTA emits `app_store_cta_click` with `cta_position: "hero"`.
- [ ] Clicking the footer CTA emits `app_store_cta_click` with `cta_position: "footer"`.
- [ ] Clicking a `mailto:support@lastmyle.co` link emits `support_email_click` with the correct `source_page`.
- [ ] After each CTA click, the browser still navigates to the destination (App Store or mail client) — the capture does not block navigation.
- [ ] The three pageviews on `/upright`, `/upright/support`, `/upright/privacy` show up in PostHog Live Events with the correct `$current_url`.
- [ ] No errors in the browser console on any of the three pages.
- [ ] Events in PostHog show the expected properties (open one event, check the Properties panel).

---

## Not in scope

- Setting up the PostHog MCP server for Cursor / Claude Code — that's a separate `npx @posthog/wizard mcp add` step that affects your AI tooling, not site code. Instructions available from the PostHog dashboard; nothing for Cursor to do in the `lastmyle.co` repo.
- Changing PostHog project settings (autocapture, session recording, etc.) — those are dashboard-side decisions, not code changes.
- Adding analytics to the iOS app. The app is deliberately zero-collection and the shipped privacy policy enforces that stance. Do not add any app-side tracking.
- Server-side event capture, API routes, or feature flags. This brief covers the client-side, declarative-event layer only.
