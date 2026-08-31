# Provenance: `core_profile_snapshot_id` in Tarot/Compat generation logs

**Date:** 2026-08-28  
**Scope:** Generation logs written by Tarot and Compatibility LLM/fallback surfaces.  
**Goal (Release Plan v1, Task 2.5):** every generation log that consumes the Personal Model carries the originating `core_profile_snapshot_id`.

## Method

1. Grep all `learning_service.log_generation(...)` calls under `api/tarot.py`, `services/compatibility*.py`, and `services/compatibility_content_v1/` for `module` in `tarot` / `compatibility`.
2. Check whether `core_profile_snapshot_id` is passed.
3. Trace pluming where the snapshot id was dropped on the way to the log.

## Findings

### Tarot

- `POST /tarot/spread/context` already extracted `snapshot_id` from `core_profile_service.build_cached_or_baseline()` and passed it to `log_generation()`.
- `GET /tarot/daily/explain` fallback path (after Caller Audit Phase 2.4) logs via `explain_tarot_card()` and passes `latest_snapshot.id`.

### Compatibility

- `services/compatibility_editorial.py` already passed `latest_snapshot.id` in its `log_generation()` calls.
- `services/compatibility_llm.py::generate_llm_product_surface()` did **not** accept or pass `core_profile_snapshot_id`, even though the caller in `services/generation_orchestrator.py` had access to the core profile snapshot. The LLM and fallback/error log rows were missing provenance.
- `services/compatibility_enrichment_v0.py` now fetches the latest snapshot for `job.user_id` and threads it through both the content-v1 result payload and the LLM dynamics pipeline.

## Changes

1. `backend/src/todayflow_backend/services/compatibility_llm.py`
   - Added `core_profile_snapshot_id: int | None = None` to `generate_llm_product_surface(...)`.
   - Passed it to both the success and error `log_generation()` calls for `surface="dynamics_llm"`.

2. `backend/src/todayflow_backend/services/generation_orchestrator.py`
   - Added `core_profile_snapshot_id: int | None = None` to `run_compatibility_dynamics_pipeline(...)`.
   - Forwarded it to `generate_llm_product_surface()`.

3. `backend/src/todayflow_backend/services/compatibility_enrichment_v0.py`
   - Added `_latest_core_profile_snapshot_id(db, user_id)` helper.
   - In `run_compatibility_enrichment_job()` the snapshot id is fetched after the user is loaded and passed to both `_enrich_with_content_v1()` and `run_compatibility_dynamics_pipeline()`.
   - `_enrich_with_content_v1()` now accepts `core_profile_snapshot_id` and stores it in the job `result_payload`.
   - The legacy dynamics pipeline `result` also includes `core_profile_snapshot_id`.

## Tests

- `backend/tests/test_compat_generation_provenance_v1.py` — 2 tests mocking the LLM failure path and asserting that `log_generation()` receives `core_profile_snapshot_id=42` (and `None` when not provided).
- `backend/tests/test_tarot_spread_context_provenance_v1.py` — 1 test overriding the core profile service to return `snapshot_id=123` and verifying that `POST /tarot/spread/context` writes a `GenerationLog` with `core_profile_snapshot_id=123`.

## Verification

```bash
cd /opt/TodayFlow/backend
.venv/bin/python -m pytest tests/test_compat_generation_provenance_v1.py tests/test_tarot_spread_context_provenance_v1.py -q
# 3 passed
```

## Risks / follow-ups

- `services/compatibility_content_v1/` does not currently write a `GenerationLog` row; the content-v1 path stores the snapshot id only in the job `result_payload`. If a separate content-v1 generation log is introduced later, it should also carry `core_profile_snapshot_id`.
- Compatibility `GET /signs` returns a baseline/template surface synchronously; the enrichment happens in a background job, which is where the provenance is now recorded. No GET log row is expected.
