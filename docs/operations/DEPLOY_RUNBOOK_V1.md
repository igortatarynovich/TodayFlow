# Production Deploy Runbook v1 — TodayFlow

**Status:** ACTIVE  
**Date:** 2026-08-29  
**Owner:** Engineering + Ops  
**Scope:** manual deployment to the live Docker Compose host (`todayflow.today`) and the CI pipeline that validates every push before deploy.

**Canonical anchors:**
- Release plan: `docs/status/RELEASE_PLAN_V1.md` §Phase 4.2
- Agent rules: `AGENTS.md` §Production deploy
- Compose file: `docker-compose.prod.yml`
- Env template: `.env.production.example`

---

## 1. Architecture

Live site is **not** auto-deployed from GitHub. Git is the ledger; the server is the source of truth for what is running. The workflow is:

```
GitHub push/PR merge to main
        ↓
GitHub Actions: build + test + compose validate
        ↓
Manual ops step on the host
        ↓
docker compose -f docker-compose.prod.yml up -d --build
        ↓
Server check: /health, /today, LLM spend latch
```

Services: `postgres` (data), `astro` (Swiss Ephemeris), `backend` (FastAPI `:8080`), `frontend` (Next.js `:3000`). Nginx/Caddy terminates TLS and routes to `frontend:3000` / `backend:8080`.

---

## 2. Pre-deploy checklist

- [ ] PR is merged to `main` and GitHub Actions run is green.
- [ ] `.env` on the server exists and is sourced from `.env.production.example`.
- [ ] Required secrets are set: `AUTH_JWT_SECRET`, `POSTGRES_PASSWORD`, `PUSH_DISPATCH_SECRET`.
- [ ] Public URLs match DNS: `PUBLIC_WEB_URL`, `PUBLIC_API_URL`.
- [ ] SMTP host set for magic links (non-dev).
- [ ] LLM provider / Token Factory keys present if any LLM surface is enabled.
- [ ] `CONTENT/` and `DATA/` directories exist on the host (mounted into backend).
- [ ] No uncommitted local edits on the host workspace (or they are intentionally staged).
- [ ] Database backups are in place before schema-bearing deploys.

---

## 3. Deploy steps (manual)

Run on the host as the user that owns the workspace (`/opt/TodayFlow`):

```bash
cd /opt/TodayFlow

# 1. Pull ledger (main only)
git checkout main
git pull origin main

# 2. Validate env and compose
cp -n .env.production.example .env   # only if .env does not exist
# edit .env to set secrets and public URLs if needed

# 3. Build and recreate
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d --build

# 4. Wait for healthy state
sleep 20
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs --tail=50 backend
```

Use `--force-recreate <service>` instead of full `down` for targeted hotfixes:

```bash
docker compose -f docker-compose.prod.yml up -d --build --force-recreate backend
docker compose -f docker-compose.prod.yml up -d --build --force-recreate frontend
```

---

## 4. Post-deploy verification

- [ ] `curl -fsS https://api.todayflow.today/health` (or local `http://localhost:8080/health`) returns 200.
- [ ] Frontend JS is baked with `PUBLIC_API_URL`, not localhost: `docker exec todayflow-frontend-1 grep -oE 'https?://[^" ]+' /app/frontend/.next/static/chunks/common-*.js | sort -u` must include `https://api.todayflow.today` and must not include `http://localhost:8080`.
- [ ] Backend CORS matches the public site: `docker exec todayflow-backend-1 printenv ALLOWED_ORIGINS` includes `https://todayflow.today`.
- [ ] Frontend serves the landing page without 5xx.
- [ ] `/today` contract endpoint returns a valid contract (may be `degraded` if LLM is tripped, but must not 500).
- [ ] LLM spend latch path is writable and not falsely tripped: check `/DATA/ops/llm_spend.json`.
- [ ] Astro service responds: `curl http://localhost:8081/health` (if astro exposes health) or backend logs show astro calls succeeding.
- [ ] Push cron secret works: `POST /internal/push/run-due` with `PUSH_DISPATCH_SECRET` returns 200.
- [ ] No unexpected errors in `docker compose logs` for 2 minutes after deploy.

---

## 5. Rollback

Last known good state is the previous Docker image tag + previous git commit. Fast rollback:

```bash
cd /opt/TodayFlow
git log --oneline -5
# choose the good SHA
git checkout <good-sha>
docker compose -f docker-compose.prod.yml up -d --build --force-recreate backend frontend
```

For database rollback, restore from a backup taken before the deploy.

---

## 6. CI pipeline (GitHub Actions)

`.github/workflows/deploy.yml` runs on every push to `main` and on `workflow_dispatch`:

1. **Backend tests** — installs Python deps and runs `pytest`.
2. **Frontend build** — installs Node deps and runs `npm run build`.
3. **Compose validation** — checks `docker-compose.prod.yml` with `docker compose config` (no secrets required for validation).
4. **Image build smoke test** — builds backend and frontend images to catch Dockerfile regressions (does not push to a registry).

The pipeline does **not** auto-deploy to the live host because the host is not exposed to GitHub Actions. The pipeline is a required gate; do not deploy manually if the pipeline is red.

---

## 7. Monitoring & alerts

Minimal alerts until a real monitoring stack is added:

- `/health` endpoint availability (every 60s).
- Backend error rate in `docker compose logs`.
- LLM daily spend: `LLM_DAILY_USD_CEILING` and `llm_spend.json` tripped flag.
- Disk space on `DATA/` and `pgdata` volume.

Escalation: if `/health` is down for >5 minutes, rollback to last green SHA.

---

## 8. What is not in this runbook

- Kubernetes migration.
- Automated canary / blue-green deploy.
- Registry push and pull-based deploy.
- Secret rotation procedure (do it manually, then restart services).
- Database migration procedure (apply via backend CLI or manual SQL; back up first).

These are wave-2 launch-readiness items if needed.

---

## Changelog

- **1.0 (2026-08-29)** — Initial runbook. Manual host deploy, CI validation gate, rollback, monitoring checklist. Phase 4.2 launch readiness.
