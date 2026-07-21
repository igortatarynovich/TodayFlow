# P5 First Slice — STOPPED / frozen

**Status:** FROZEN — do not extend  
**Stopped:** 2026-07-21  
**RFC:** [RFC_CANONICAL_CONTEXT_ENGINE_V0.md](../rfc/RFC_CANONICAL_CONTEXT_ENGINE_V0.md) (**STOPPED**)  
**Canon:** [PRODUCT_TRUTH_FIRST.md](../PRODUCT_TRUTH_FIRST.md) § «Архитектура только с доказанной пользой»

## Decision

P5 as a product-wide Context Engine is **stopped**. It was not proven to improve answer quality or reduce delivery cost for MVP.

## What stays in code (in use)

Thin path already wired into spheres synthesis:

- `question_id` ↔ `sphere_id` mapping (`q.relationships.v1` / `q.money.v1` / `q.decisions.v1`)
- `build_context_pack_for_sphere` → synthesis user pack + kitchen (`fact_ids`, fingerprint)

Package: `backend/src/todayflow_backend/context_engine_v0/`  
Consumer: `life_spheres_synthesis_run_v0.py` · `life_spheres_cues_v0` (QUESTION_SPECS)

Do **not** rename/expand into a platform engine. Treat as synthesis helpers.

## Cancelled (do not schedule)

- ❌ P5.2 FactAtoms  
- ❌ P5.3 Living/Patterns migration  
- ❌ P5.4 Today migration  
- ❌ New Context Engine / registries / abstractions  

## Next priority

Product screens (purpose → data → prompt → quality → wire → UI), not infrastructure.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-21 | First slice opened |
| 2026-07-21 | **STOPPED** — freeze; keep only in-use mapping |
