# Day Scenario Eval Pack C3.5

**Status:** LANDED C3.5.0 · **HARDENED C3.5.1** (eval-only; no Nebius; runtime untouched)  
**Date:** 2026-07-25 · updated 2026-07-26  
**Code:** `day_scenario_eval_pack_c35.py` · `day_scenario_eval_fixtures_c351.py` · `day_scenario_eval_report_c351.py` · `day_scenario_eval_editorial_en_c351.py` · `day_scenario_eval_provenance_c351.py`  
**Tests:** `tests/test_day_scenario_eval_pack_c35.py` · `tests/test_day_scenario_eval_pack_c351.py`  
**Depends on:** C3.1–C3.3b gates / pairwise scoring  

## Architecture impact

```markdown
## Architecture impact
- **SoT before:** pairwise same-day eval only (C3.3b); no multi-day / multi-locale pack
- **SoT after (C3.5.0):** eval pack scores 14d × ≥3 natal profiles + no-birth-time × ru/en
- **SoT after (C3.5.1):** expanded synthetic matrix 28d × ≥10 profiles × ru/en (≥400 cells);
  dual contract/editorial scores; EN editorial parity gate (eval-only);
  provenance + day_closure c351 modules; baseline report artifacts
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this note + DAY_SCENARIO_EVAL_HARDENING_C351 + DAY_SCENARIO_V1 + tracker
- **Backward compatible?** yes
- **Lifecycle / UI:** unchanged — eval-only, not runtime SoT
- **Runtime gates / today.py / Nebius:** **untouched** (EN production gate expansion = separate follow-up)
```

## Matrix

| Axis | C3.5.0 (legacy wrapper) | C3.5.1 |
|------|-------------------------|--------|
| Days | 14 consecutive | 28 (`DAY_TYPES` rotation) |
| Profiles | `smooth_conflict`, `demand_clarity`, `analyze_first`, `no_birth_time` | 11 ids (≥8 required): 7 behavioral + controls |
| Locales | `ru`, `en` | `ru`, `en` |
| Cells | 112 | **616** (28×11×2) default |
| Compare | same dates across profiles | same |

- Legacy: `build_synthetic_eval_matrix_c35` (14 × `PROFILE_IDS_C35_LEGACY` × 2).  
- Hardened: `build_synthetic_eval_matrix_c351` (28 × `PROFILE_IDS` × 2).  
- Live Nebius captures can be fed into `run_eval_pack_c35` — **not** required in CI.

### Profile ids (C3.5.1)

Behavioral: `smooth_conflict`, `demand_clarity`, `analyze_first`, `act_first`, `over_responsible`, `rejection_sensitive`, `autonomy_oriented`  
Controls: `no_birth_time`, `no_profile`, `birth_date_only`, `incomplete_evidence`

## Score axes

| Axis | Source (C3.5.1) |
|------|-----------------|
| `conflict_recognizability` | title + opposing forces + thesis · **contract/editorial split** |
| `scene_concreteness` | RU: C3.1 gate · EN: `score_editorial_en_c351` (parity) |
| `chorus_coherence` | RU: C3.1/C3.2 · EN: EN gate chorus defects |
| `user_differentiation` | structural diffs across deep profiles; control honesty |
| `formulation_repeatability` | token Jaccard across consecutive days (lower = better) |
| `recommendation_provenance` | `score_provenance_c351` (dual) |
| `no_parallel_forecasts` | chorus parallel / semantic-dupe codes |
| `day_closure_quality` | `score_day_closure_c351` — **scenes alone cannot pass** |

Each cell also exposes `contract_score`, `editorial_score`, `defect_codes`.

### Thresholds (PROVISIONAL)

| Band | Cell score |
|------|------------|
| reject | `< 0.60` |
| review | `0.60`–`0.79` |
| pass | `≥ 0.80` |

Pack `pass` when `shape_ok` and `pack_score ≥ 0.75` (**provisional** pack gate).  
`shape_ok` accepts legacy 14×4×ru+en **or** C3.5.1 (≥28 days, ≥8 profiles, ≥400 cells, ru+en).

## EN note

Production editorial gate remains **RU-primary**. EN cells use **eval-only** `day_scenario_eval_editorial_en_c351` so the pack can compare locales without expanding the runtime gate in this phase. Runtime EN gate = separate follow-up.

## Related audits

- [DAY_SCENARIO_EVAL_HARDENING_C351.md](./DAY_SCENARIO_EVAL_HARDENING_C351.md) — hardening details  
- [DAY_SCENARIO_EVAL_BASELINE_C35.md](./DAY_SCENARIO_EVAL_BASELINE_C35.md) — synthetic baseline  
- [DAY_SCENARIO_EVAL_GOLDEN_SET_C35C.md](./DAY_SCENARIO_EVAL_GOLDEN_SET_C35C.md) — golden-set scaffold (0 labeled cases)

## Out of scope

- Visual polish / UI redesign — **after** golden set + live shadow  
- Live Nebius in CI  
- Changing GET lifecycle / today.py API contracts  
- Formula rewrite of failed LLM output  
- Expanding production language gate to EN (later)  
- Disabling / rewriting runtime LLM gates

## Recommended next

1. **C3.5.1 hardening** — landed (this note).  
2. **Golden-set labeling (C3.5c)** — fill schema in `DAY_SCENARIO_EVAL_GOLDEN_SET_C35C.md`.  
3. Live shadow / capture review → defect hotspots → polish.
