# Day Story Generation Lifecycle v0

**Status:** audit note (no runtime change)  
**Date:** 2026-07-25  
**Related:** [DAY_PRODUCT_LOGIC_CAPTURE_PACK.md](./DAY_PRODUCT_LOGIC_CAPTURE_PACK.md)

## When LLM runs today

| Entry | `force_rebuild` | LLM? |
|-------|-----------------|------|
| `GET /today/contract` → `build_day_story_v1_wire` | `False` | **No** (cache or deterministic fallback / unavailable shell) |
| `POST /today/story/refresh` → `build_day_story_record_for_refresh` | `True` | **Yes**, if chat LLM configured |

Code: [`day_story_wire_v1.py`](../../backend/src/todayflow_backend/services/day_story_wire_v1.py) — comment: GET must not block on Nebius.

## Retry

`call_day_story_llm_v1`: up to **2** attempts. Rejects: empty content, JSON parse fail, phrase gate fail, empty expect+trap. On total failure → `build_day_story_fallback_v1` (facts-only / `interpretation_status: unavailable` — **not** formula-bank prose).

## Capture implication

Packs that need raw DeepSeek must use **refresh / force_rebuild=True**. Lifecycle section records `get_calls_llm: false`.

## Follow-up (not this note)

If packs show mass `unavailable` on first open → separate Architecture impact for warmup / first-open generate. Do not silently re-enable LLM on every GET.
