# Life Path co-voice rubric v0

**Status:** ACTIVE · 2026-07-24  
**Code SoT:** `backend/src/todayflow_backend/services/life_path_visibility_v0.py`  
**Prompts:** `profile.identity.v1` ≥1.2.0 · `profile.styles.v1` ≥1.1.0  
**Eval:** `evals/profile_quality/run_life_path_co_voice_eval_v0.py` (matrix A/B/C/D × 2)

## Rule

Life path is a **co-voice equal to astro**, not background. «Visible» = at least one identity/styles field carries a theme from the claimed LP dictionary that is **distinguishable** from other LPs.

## Fail conditions (release)

| Id | Meaning |
|----|---------|
| F1 | Claimed LP not detectable in any scored field |
| F3 | Same natal A vs C (LP9 vs LP1) shows no theme shift |
| F4 | Both B and D fail F1 — strong natal silences any LP |

## Production repair

If identity draft fails visibility, one repair LLM call (`_repair_identity_life_path_co_voice`) rewrites with explicit `themes_ru` before accepting the step.
