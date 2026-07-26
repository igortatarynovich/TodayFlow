# Day Scenario Eval Hardening C3.5.1

**Status:** LANDED (eval-only)  
**Date:** 2026-07-26  
**Eval version:** `c35.1`  
**Parent:** [DAY_SCENARIO_EVAL_PACK_C35.md](./DAY_SCENARIO_EVAL_PACK_C35.md)

## Architecture impact

```markdown
## Architecture impact
- **SoT before:** C3.5.0 pack — 14×4×2 synthetic matrix; EN scene heuristic; soft provenance/closure
- **SoT after:** C3.5.1 eval harness — 28×≥10×2 matrix; EN editorial parity gate; provenance +
  day_closure dual scores; baseline report; fixtures/mutations for regression
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this note + pack note + DAY_SCENARIO_V1 + tracker
- **Backward compatible?** yes — `build_synthetic_eval_matrix_c35` legacy wrapper retained
- **Runtime LLM gates / today.py / Nebius:** untouched (explicit non-goal)
```

## What landed

| Module | Role |
|--------|------|
| `day_scenario_eval_fixtures_c351.py` | good RU/EN natives · `NEGATIVE_FIXTURES` · `apply_mutation` |
| `day_scenario_eval_editorial_en_c351.py` | EN editorial gate (eval-only parity with RU C3.1/C3.2) |
| `day_scenario_eval_provenance_c351.py` | provenance chain + day_closure contract/editorial scores |
| `day_scenario_eval_report_c351.py` | baseline report + markdown/JSON writers |
| `day_scenario_eval_pack_c35.py` | `EVAL_VERSION=c35.1` · expanded matrix · dual cell scores |

## Dual scoring

Every cell returns:

- `axes` — eight pack axes  
- `contract_score` / `editorial_score` — means across conflict, scenes, chorus, provenance, closure  
- `defect_codes` — union of axis defect codes  

**Closure rule:** scenes alone never satisfy `day_closure_quality` (`CLOSURE_MISSING`).

## Thresholds (PROVISIONAL)

Documented in report + pack:

- cell reject `< 0.60` · review `0.60–0.79` · pass `≥ 0.80`  
- pack pass threshold `0.75` (provisional; calibrate via golden set)

## Shape gates

| Mode | Requirement |
|------|-------------|
| Legacy C3.5.0 | ≥14 days · ≥4 profiles incl. `no_birth_time` · ru+en |
| C3.5.1 | ≥28 days · ≥8 profiles · ≥400 cells · ru+en |

Default synthetic C3.5.1: **28 × 11 × 2 = 616 cells**.

## Explicit non-goals (this change)

- No runtime gate disable or rewrite  
- No today.py API / public JSON contract changes  
- No Nebius calls in CI  
- No Character Engine / Tarot edits  

Runtime EN production gate expansion = **separate follow-up**.

## Next

1. Golden-set labeling — [DAY_SCENARIO_EVAL_GOLDEN_SET_C35C.md](./DAY_SCENARIO_EVAL_GOLDEN_SET_C35C.md)  
2. Live shadow on captured weeks  
3. Calibrate provisional thresholds from labeled cases
