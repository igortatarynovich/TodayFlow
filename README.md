# TodayFlow Monorepo

Product and architecture canon live in **`docs/`** — start with [docs/README.md](./docs/README.md) and [docs/CORE_PRODUCT_CANON.md](./docs/CORE_PRODUCT_CANON.md).

This repo holds:

- **Product canon & trackers** (`docs/`)
- **Reference content** (`CONTENT/`, `DATA/reference/`)
- **Backend API** (`backend/`)
- **Astrology microservice** (`astro/`)
- **Next.js frontend** (`frontend/`)
- **Native clients** (`ios/`, `android/`)
- **DevOps glue** (`docker-compose.yml`, per-service Dockerfiles)
- **Production data versions** (`CONTENT/version.json`)

## Architecture Snapshot

| Layer          | Tech / Location                     | Responsibility                                                                                                                                      |
|----------------|--------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|
| Frontend       | Next.js 14 (`frontend/`)             | Today, Profile, and product surfaces. No generation logic on client.                                                         |
| Backend API    | FastAPI (`backend/`)                 | Birth data intake, astro service orchestration, Internal Model mapping, Narrative Engine, persistence, Stripe.                                       |
| Astro Service  | FastAPI + Swiss Ephemeris (`astro/`) | Accurate Sun/Moon/Rising + houses. Returns normalized chart JSON used by backend rules.                                                              |
| Data Layer     | PostgreSQL                           | Users, UserProfiles, GeneratedReports, purchases. Wired via docker-compose.                                                                          |
| Content        | `CONTENT/paragraph_templates_v1*.jsonl` | Canonical paragraph templates + i18n snapshot, versioned via `CONTENT/version.json`.                                                                  |

Domains remain split per product routing:
- `todayflow.today` → marketing/fun content (served by frontend)
- `todayflow.app` → product, auth, payments (same Next.js deployment with domain routing)

## Local Stack

```bash
docker compose up --build
```

Services:
- `frontend` on http://localhost:3000 (Next.js)
- `backend` on http://localhost:8080 (FastAPI) — health: http://localhost:8080/health
- `astro` on http://localhost:8081 (placeholder chart service)
- `postgres` on localhost:5432

### Public deployment

1. Copy `.env.production.example` → `.env` on the server and set `PUBLIC_WEB_URL`, `PUBLIC_API_URL`, `AUTH_JWT_SECRET`, `POSTGRES_PASSWORD`, SMTP.
2. Build and run:

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

3. Put **nginx/Caddy** in front:
   - `PUBLIC_WEB_URL` → `frontend:3000`
   - `PUBLIC_API_URL` → `backend:8080` (must match `NEXT_PUBLIC_API_BASE_URL` baked at frontend build time)
4. **Launch walkthrough** (smoke test): `/` → onboarding → First Today → evening → save email → magic link → D2 `/today`.

Adjust `.env` / environment variables per service before adding real credentials (Stripe, Supabase, etc.). Payments default to a mock mode (`PAYMENTS_MODE=mock`) so local testing auto-upgrades accounts; set `PAYMENTS_MODE=stripe` + Stripe secrets when you are ready for live checkout.

## Development Guidelines

1. Update content via `CONTENT/paragraph_templates_v1.jsonl` + `scripts/sync_i18n.py`, bump versions in `CONTENT/version.json`.
2. Keep backend logic authoritative: frontend only renders responses, no astrology math or template selection on the client.
3. Extend the astro service for precise charts; backend consumes it via HTTP.
4. Capture product and architecture changes in `docs/PRODUCT_EXECUTION_TRACKER.md` and the relevant canon doc.
5. Run `scripts/parity_check.py` before locking content/i18n versions to ensure meta ↔ i18n parity.
6. Use the `/admin` interface (log in via `/auth/signup` with `is_admin=true`) to toggle Lite/Full usage and override variant text; all changes are logged for auditability.

### Security / Dependency Notes

- `npm audit` (frontend) currently reports 4 dev-only vulnerabilities coming from `glob@7.x`, which is pulled in by `eslint-config-next@14.2.35`. They do **not** affect production bundles (lint-only tooling). Fixing them requires upgrading to Next 16 / ESLint 9, so we track the follow-up instead of forcing `npm audit fix --force`.
- Running `npm audit` without WAN access may fail with `getaddrinfo ENOTFOUND registry.npmjs.org`; rerun once network access is available if you need an updated report.
