# TodayFlow Frontend

Canonical Next.js app that serves:
- `todayflow.today` marketing + SEO pages
- `todayflow.app` product surfaces (form, dashboard, report viewer)

## Stack
- Next.js 14 (App Router, React Server Components)
- TypeScript + ESLint (Next config)
- next-seo for canonical meta tags/OG data

## Development
```bash
cd frontend
npm install    # or pnpm install
npm run dev
```

Environment variables (API base URLs, Stripe keys) will be pulled from `.env.local`.
Keep all content rendering dumb — the backend API owns logic per [docs/TODAYFLOW_PRODUCT_CANON_UNIFIED.md](../docs/TODAYFLOW_PRODUCT_CANON_UNIFIED.md).

## Routes to implement
- `/` Landing page with CTA → Birth Chart form
- `/birth-chart` ✅ initial form + Lite preview fetch wired to backend `/reports/lite`
- `/signup`, `/login` ✅ placeholder auth flow hitting backend
- `/dashboard` ✅ prototype checkout button calling backend `/payments/checkout-session`
- `/admin` ✅ paragraphs list + toggle + audit log
- `/reports/full` ✅ prototype page calling backend `/reports/full`

When ready, deploy to Vercel with domain split:
- Marketing: `todayflow.today`
- Product: `todayflow.app`
