# Day Story Generation Lifecycle v0

**Status:** audit note — updated for Phase C1 native scenario LLM  
**Date:** 2026-07-25  
**Related:** [DAY_PRODUCT_LOGIC_CAPTURE_PACK.md](./DAY_PRODUCT_LOGIC_CAPTURE_PACK.md) · [DAY_SCENARIO_NATIVE_LLM_C1.md](./DAY_SCENARIO_NATIVE_LLM_C1.md)

## When LLM runs today

| Entry | `force_rebuild` | LLM? |
|-------|-----------------|------|
| `GET /today/contract` → `build_day_story_v1_wire` | `False` | **No** (cache or deterministic scenario / unavailable shell) |
| `POST /today/story/refresh` → `build_day_story_record_for_refresh` | `True` | **Yes** — **native scenario** (`call_day_scenario_native_llm_c1`), if chat LLM configured |

Code: [`day_story_wire_v1.py`](../../backend/src/todayflow_backend/services/day_story_wire_v1.py) — GET must not block on Nebius.

## Native vs legacy

| Path | Runtime? |
|------|----------|
| `call_day_scenario_native_llm_c1` | **Yes** on refresh |
| `call_day_story_llm_v1` (legacy expect/trap JSON) | **No** — eval/compare only |

## Retry

Native C1/C3.1–C3.3b: up to **2** attempts. Rejects: empty, parse fail, legacy keys, schema validation, **personalization + sphere selection gates** (then downgrade to general or reject on profile leak), **editorial gate** (scenes/chorus). Retry includes defect feedback. On total failure → `facts_only_unavailable` (**not** legacy LLM schema, **not** formula-bank prose). Bad personalization with a salvageable day story → **honest general** (strip personal layer), not unavailable.

## Cache

- Valid `day_scenario.generation_source` ∈ {`native_llm_c1`, `deterministic_engine_b5`} → re-project.
- Missing marker (pre-C1) → unavailable; refresh creates native scenario. No reconstruct from expect/trap.

## Capture implication

Packs that need raw DeepSeek must use **refresh / force_rebuild=True**. Capture records native prompt + validation defects. Lifecycle: `get_calls_llm: false`.

## Follow-up

C2 Chapters UI. Do not re-enable LLM on every GET.
