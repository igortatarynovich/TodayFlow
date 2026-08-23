# Native C1 Editorial Gate Calibration V1

**Date:** 2026-08-23  
**Status:** **IN PROGRESS** — quality/calibration pass on existing native C1 + C3.1 gates. **Not** IL-4 rewrite. **Not** I0 split reopen. **Not** consume/polish reopen. **Not** `active`.  
**Canon:** [DAY_SCENARIO_EVERYDAY_QUALITY_C31](../audits/DAY_SCENARIO_EVERYDAY_QUALITY_C31.md) · [DAY_SCENARIO_GATE_MATURITY_C36](../audits/DAY_SCENARIO_GATE_MATURITY_C36.md) · [NATIVE_C1_I0_GENERATION_SPLIT_V1](./NATIVE_C1_I0_GENERATION_SPLIT_V1.md)

---

## Architecture impact

- **SoT before:** Native C1 I0 split (c5.0) + C3.6.3 blocking gates; gate retry on Global stage passed **codes only** (`SCENE_MISSING_EVERYDAY;…`), not actionable editorial feedback → model repeated the same formulation defects.
- **SoT after:** **Native C1 Editorial Gate Calibration V1** — prompt `day-scenario-native-c5.1`; Global gate retry injects `format_editorial_retry_feedback` (defect messages + targeted hints for everyday scenes and astro translation). Gates unchanged (no semantic weakening). Public JSON unchanged.
- **Public contract changed?** no — `interpretation_status` semantics unchanged; fewer `unavailable` when LLM passes gates
- **Migration required?** no — `force` rebuild / refresh picks up c5.1
- **Canon updated?** yes — this file · tracker 1.3.117
- **Backward compatible?** yes — same gate codes; stricter retry coaching only

---

## Problem (production 2026-08-23)

Generation reaches LLM; failure is **editorial gate** on Global stage:

| Code | Typical cause | Fix lane |
|------|----------------|----------|
| `SCENE_MISSING_EVERYDAY` | `everyday_example` missing / formula tip without lived moment | Prompt contract + retry feedback |
| `SCENE_ABSTRACT` | setup = sphere forecast; no concrete marker | Prompt contract + retry feedback |
| `ASTRO_JARGON_BARE` | `human_meaning` echoes sky label or template «подталкивает день к сюжету» | Prompt translation examples + retry feedback |

`interpretation_status: unavailable` = **honest product signal** (no invented prose), not transport failure.

---

## Scope (this pass)

1. Collect reject reasons from `generation_logs` (`native_llm_c1_meta`, `error_message`).
2. **Prompt c5.1** — sharper everyday + astro translation one-shots (no gate relaxation).
3. **Retry path** — Global stage retries receive full `format_editorial_retry_feedback`, not code-only strings.
4. **Regression matrix** (fixtures, no single-user smoke):
   - `evidence_depth`: general · light · deep
   - multiple conflict families (momentum / change / pressure)
   - forced Personal stage failure → `personal_degraded`, Global preserved

**Success criterion:** IL-2/3 meaning preserved → Global in everyday language → Personal overlay does not mutate Global → gates PASS → `interpretation_status: ok` + non-empty `story` in Today.

---

## Out of scope

- Reopen IL-4 attach/consume/polish
- Change I0 stage order or `GLOBAL_LOCKED` contract
- Post-LLM hard overwrite of meaning slots
- GET `/today/contract` auto-rebuild on `unavailable` (ops: `POST /today/story/refresh` `force=true`)

---

## Ops

```bash
# Reject reason rollup (production DB)
python backend/scripts/collect_native_gate_rejects_v1.py --days 7

# Regression matrix (force rebuild — slow, uses live LLM)
python backend/scripts/native_c1_regression_matrix_v1.py --date 2026-08-23
python backend/scripts/native_c1_regression_matrix_v1.py --user-id 26 --date 2026-08-23

# Unit regression
pytest backend/tests/test_native_c1_editorial_gate_calibration_v1.py -q
```
