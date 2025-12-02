# SecureKit (Frontend) — Quick Friendly Guide


SecureKit is a Next.js App Router frontend that acts as a small security toolkit UI. It includes:

- Dashboard (home)
- QR Shield — upload/scan QR images and analyze detected URLs
- PixelVault — hide/extract messages in images (steganography)
- PhishyWishy — phishing analysis playground

## Main files / structure

- `app/page.js` — root dashboard (cards link to tools)
- `app/dashboard/page.js` — dashboard page
- `app/qr_shield/page.js` — QR Shield tool page
- `app/pixel_vault/page.js` — PixelVault tool page
- `components/Sidebar.js` — responsive sidebar with mobile drawer
- `components/ui/` — small UI primitives (card, button)
- `lib/cn.js` — helper to join classnames
- `public/` — static assets

## Routes

The front-end links to these routes:

- `/` — root dashboard
- `/qr_shield` — QR Shield
- `/pixel_vault` — PixelVault
- `/phishy_wishy` — PhishyWishy


## Setup & deps

Make sure Node.js is installed. Then run:

```powershell
npm install
# or
# pnpm install
```

Install a few optional helpers if you don't already have them:

```powershell
npm install lucide-react clsx tailwind-merge
# or pnpm add lucide-react clsx tailwind-merge
```

- `lucide-react` — icon components used in the UI
- `clsx`, `tailwind-merge` — utilities sometimes used by `cn()` helpers

## Run the app

```powershell
npm run dev
```

Open `http://localhost:3000` and click the dashboard cards or use the sidebar.

## Notes I noticed

- Some pages use `"use client"` (hooks/browser APIs). That's intentional for the interactive parts.
- Lint advises using `next/image` for `<img>` tags — that helps optimization. Not necessary now, but useful for production.
- The sidebar uses `usePathname()` to highlight the active route. If active highlighting doesn't update, check that `usePathname()` is used correctly.
