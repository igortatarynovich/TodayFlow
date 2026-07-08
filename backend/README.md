# TodayFlow Backend

Core API that powers Today, Profile, and product surfaces. Canon: [docs/CORE_PRODUCT_CANON.md](../docs/CORE_PRODUCT_CANON.md).

## Responsibilities
- Accept birth data, orchestrate the astrology microservice, and map results to the internal model (see `SPEC/Internal_Model_v1.md`, `SPEC/Model_Mapping_v1.md`).
- Run the Narrative Engine rules in `SPEC/Narrative_Engine_Rules_v1.md` to assemble Lite and Full reports using the canonical content pool in `CONTENT/`.
- Persist user profiles, generated reports, and purchase status in PostgreSQL.
- Expose REST endpoints consumed by the Next.js frontend (`todayflow.app`) and internal admin tools.

## Tech Stack
- Python 3.11
- FastAPI + Uvicorn
- SQLAlchemy / PostgreSQL
- HTTPX client for astro service + Stripe

## Local Development
1. Install dependencies:
   ```bash
   cd backend
   uv venv && source .venv/bin/activate  # or use your tool
   pip install -e .[dev]
   ```
2. Run the API:
   ```bash
   uvicorn todayflow_backend.main:app --reload --port 8080
   ```
3. Hit `http://localhost:8080/docs` to inspect the OpenAPI spec.

### Key Endpoints
- `POST /auth/signup` / `POST /auth/login` — placeholder email+password flow (replace with secure auth before launch).
- `POST /reports/lite` — orchestrates astro + narrative engine, persists lite report snapshots.
- `POST /payments/checkout-session` — creates a Stripe Checkout session (requires `STRIPE_SECRET_KEY` / `STRIPE_PRICE_ID`).
- `POST /payments/webhook` — Stripe webhook endpoint that marks users as paid after `checkout.session.completed`.
- `GET /admin/paragraphs`, `POST /admin/paragraphs/{id}/toggle` — internal content controls per MVP admin requirements.

Environment values (DB URL, astro URL, content/i18n versions) live in `todayflow_backend/core/config.py`
and should be overridden via `.env`. `docker-compose.yml` wires this service up with the astro worker,
frontend, and Postgres for a full local stack.
