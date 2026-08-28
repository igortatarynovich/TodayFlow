# Caller audit: LLM-on-read in Today/Compat/Tarot/Account GETs

**Date:** 2026-08-28  
**Scope:** `GET` endpoints under `api/today.py`, `api/compatibility.py`, `api/tarot.py`, `api/account.py` that touch the Personal Model / Core Profile or any LLM.  
**Goal (Release Plan v1, Task 2.4):** no `build()` LLM-on-read; no LLM call inside a read-path `GET`.

## Method

1. Grep all four routers for `core_profile_service.build(`, `service.build(`, and any direct `chat_completion_plain` / `llm_operation` calls inside `GET` handlers.
2. Verify the single remaining `build()` calls in `account.py` are portrait publishers behind `POST` with `publish_portrait=True`.
3. Trace every `GET` that calls into a service that could invoke an LLM.

## Findings

### 1. `CoreProfileService.build()` is not used on read paths

All `GET` handlers in scope use `build_cached_or_baseline(...)`:

- `api/today.py` — `/contract`, `/core`, `/bundle`, `/scenarios`, `/evening`, `/` (today cycle) all call `core_profile_service.build_cached_or_baseline(db, user)`.
- `api/compatibility.py` — `/signs` calls `core_profile_service.build_cached_or_baseline(db, user)`.
- `api/tarot.py` — `POST /spread/context` (not a GET, but already audited) uses `build_cached_or_baseline(db, user)`.
- `api/account.py` — `/core-profile`, `/compact-user-model`, `/profile-summary`, `/profile-build-status`, `/profile/natal-decode`, `/profile-selector-preview` all use `build_cached_or_baseline(...)`.

The only remaining `service.build(...)` calls in `account.py` are portrait publishers behind explicit `POST` endpoints and pass `publish_portrait=True`:

- `POST /account/core-profile/publish-portrait`
- `POST /account/astro-profiles/{id}/save-and-publish`
- `POST /account/astro-profiles/primary/setup`

### 2. `GET /tarot/daily/explain` was the only LLM-on-read violation

`todayflow_backend/core/tarot_explainer.py::explain_tarot_card()` called `chat_completion_plain()` directly on every request. The endpoint `GET /tarot/daily/explain` is a read surface, so this violated the release gate.

### 3. Latent bug in the same endpoint

`explain_daily_tarot_card` called `tarot_service = get_tarot_service()` without `await` (the dependency factory is async). This produced a coroutine and then failed with `AttributeError: 'coroutine' object has no attribute 'get_daily_draw'`. This was hidden because the LLM path was the first thing users hit after a successful card reveal.

## Changes

1. `backend/src/todayflow_backend/core/tarot_explainer.py`
   - Added `allow_llm: bool = False` to `explain_tarot_card()`.
   - Added `_load_cached_explanation()` to read the newest valid `GenerationLog` row for `module="tarot"`, `surface="daily_card_explainer"`, matching `target_date`, `card_id`, and `orientation`.
   - On read path (`allow_llm=False`): cache hit → return cached explanation; cache miss → build deterministic fallback and log it as `fallback` with `skip_llm: read_path`.
   - The LLM path is preserved behind `allow_llm=True` for explicit write/POST or background enrichment surfaces.

2. `backend/src/todayflow_backend/api/tarot.py`
   - `GET /tarot/daily/explain` now injects `tarot_service: TarotService = Depends(get_tarot_service)` instead of calling the async factory inline.
   - Calls `explain_tarot_card(..., allow_llm=False)` explicitly.

3. `backend/tests/test_tarot_daily_explain_no_llm_v1.py`
   - Unit test: `explain_tarot_card()` mocked `chat_completion_plain` to raise if called; verifies fallback fields and that the second call hits cache.
   - Endpoint test: authenticates, reveals a card via `POST /tarot/daily/reveal`, then calls `GET /tarot/daily/explain` with `chat_completion_plain` mocked; verifies 200 and deterministic explanation fields.

## Verification

```bash
cd /opt/TodayFlow/backend
.venv/bin/python -m pytest tests/test_tarot_daily_explain_no_llm_v1.py -q
```

Result: 2 passed.

Also run:

```bash
.venv/bin/python -m pytest tests/test_core_profile_read_path_no_llm_v1.py -q
```

Result: 7 passed.

## Risks / follow-ups

- `GET /compatibility/business-partnership` performs deterministic composite/synastry/psych calculations and no LLM calls, but it is heavy and depends on the astro service being available. It is not in the release gate read-path list and was left unchanged.
- `test_tarot.py` has two pre-existing failures unrelated to this audit (`test_get_tarot_reminder_default`, `test_update_tarot_reminder`). They fail on `main` and are outside the caller-audit scope.
- `GET /today/contract` and related `GET`s already use `allow_rebuild_on_miss=False` and deterministic/fallback content; no additional code change was needed.
