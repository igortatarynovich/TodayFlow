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

## Retry (C3.6 maturity)

Native C1 + **Gate Maturity C3.6**: up to **2** attempts for **hard** failures only — empty, parse fail, legacy keys, schema validation, SoT assemble errors, broken evidence refs (`PERSONALIZATION_EVIDENCE_ORPHAN`). `PROFILE_FACT_LEAK` → immediate reject (unavailable); leaked text never shipped and never sent to a quality-rewrite prompt. **Editorial / soft personalization / sphere heuristics** always analyze and write scores/defects to **capture**; they **do not** retry, downgrade to general, or force unavailable. On hard total failure → `facts_only_unavailable`. See [DAY_SCENARIO_GATE_MATURITY_C36.md](./DAY_SCENARIO_GATE_MATURITY_C36.md).

## Cache

- Valid `day_scenario.generation_source` ∈ {`native_llm_c1`, `deterministic_engine_b5`} → re-project.
- Missing marker (pre-C1) → unavailable; refresh creates native scenario. No reconstruct from expect/trap.

## Capture implication

Packs that need raw DeepSeek must use **refresh / force_rebuild=True**. Capture records native prompt + validation defects. Lifecycle: `get_calls_llm: false`.

## Follow-up

C2 Chapters UI. Do not re-enable LLM on every GET.
