# TestFlight via GitHub Actions

Build and upload Upright to TestFlight **without upgrading macOS** on your MacBook.

The workflow runs on **GitHub's cloud Macs** (with the latest Xcode). Your laptop only needs **git** and a browser — no local archive or upload.

---

## What runs where

| Task | Your MacBook | GitHub Actions |
|------|----------------|----------------|
| Edit code | Yes | — |
| `git push` | Yes | — |
| Add GitHub secrets | Browser only | — |
| Xcode archive + upload | Optional (local testing) | **Yes** |
| TestFlight processing | — | App Store Connect |

You can reinstall **Xcode 16** (last compatible with your macOS) for **USB testing on your own iPhone**. TestFlight builds for friends come from GitHub.

---

## One-time setup

### 1. App Store Connect app record

If not done already, create **Upright** in [App Store Connect](https://appstoreconnect.apple.com) with bundle ID `com.lastmyle.upright`.

### 2. App Store Connect API key

1. [App Store Connect](https://appstoreconnect.apple.com) → **Users and Access** → **Integrations** → **App Store Connect API**
2. **Generate API Key** with role **Admin** (required for cloud distribution signing in CI)
3. Name suggestion: `Upright GitHub Actions`
4. Download the `.p8` file (only once)
5. Note **Issuer ID** and **Key ID**

**Important:** **App Manager** is not enough for `xcodebuild -exportArchive` with automatic signing. You need **Admin** or you will see:

```text
error: exportArchive Cloud signing permission error
error: exportArchive No profiles for 'com.lastmyle.upright' were found
```

If you already created an App Manager key, generate a new **Admin** key and update the three `APPSTORE_*` GitHub secrets.

### 3. GitHub repository secrets

Repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| Secret | Value |
|--------|--------|
| `APPSTORE_ISSUER_ID` | Issuer ID from App Store Connect |
| `APPSTORE_API_KEY_ID` | Key ID (e.g. `ABC123XYZ`) |
| `APPSTORE_API_PRIVATE_KEY` | Full contents of the `.p8` file (including `BEGIN/END` lines) |
| `APPLE_TEAM_ID` | Your 10-character Team ID (Xcode → Settings → Accounts, or developer.apple.com) |

Example Team ID from this project: `7B4D6525KF` — use yours if different.

### 4. Push the workflow

Ensure `.github/workflows/testflight.yml` is on the `master` branch (merge or push).

---

## Run a build

1. GitHub repo → **Actions** tab
2. **TestFlight** workflow (left sidebar)
3. **Run workflow** → branch `master` → **Run workflow**
4. Wait ~10–20 minutes (green checkmark = upload succeeded)
5. [App Store Connect](https://appstoreconnect.apple.com) → **Upright** → **TestFlight** → wait for processing
6. Add internal/external testers (see `docs/testflight.md`)

Pushes to `master` that touch `ios/`, `web/`, or the workflow file also trigger a build automatically.

---

## Troubleshooting

### Workflow fails: missing secrets

Add all four secrets in step 3 above.

### SDK version error on GitHub runner

The workflow uses `macos-latest` and `latest-stable` Xcode. If Apple raises SDK requirements again, update `.github/workflows/testflight.yml`:

```yaml
runs-on: macos-latest   # or a newer label when available
```

and re-run.

### `Cloud signing permission error` / `No profiles were found`

The **archive** step succeeded but **export** failed. Common causes:

1. **API key role is App Manager** — create a new key with **Admin** access and update GitHub secrets (`APPSTORE_API_KEY_ID`, `APPSTORE_API_PRIVATE_KEY`). Issuer ID stays the same.
2. **Bundle ID not registered** — [developer.apple.com/account/resources/identifiers](https://developer.apple.com/account/resources/identifiers/list) → confirm `com.lastmyle.upright` exists (App IDs).
3. **App record missing** — App Store Connect → **Apps** → **Upright** with the same bundle ID.

After fixing, re-run **Actions → TestFlight → Run workflow**.

### Signing / provisioning errors (other)

### Upload succeeded but no build in TestFlight

Processing can take 10–30 minutes. Check email from Apple for processing errors.

### Local Xcode vs CI

| Goal | Tool |
|------|------|
| Test on **your** iPhone via USB | Xcode 16 on your Mac (compatible with your macOS) |
| Ship to **friends** via TestFlight | GitHub Actions workflow |

---

## Security notes

- Never commit the `.p8` file — secrets only
- Rotate API keys if exposed
- Restrict API key access to this repo's Actions

---

## Related docs

- Friend testing instructions: `docs/testflight.md`
- Local device testing: `README.md`
