# Human golden curated EN batch `c362_en_expansion_20260726`

Curated EN natives from C3.5.1 eval matrix (+ selective mutations) for C3.6.2 blind review.

## Status

| Role | State |
|------|--------|
| Reviewer A | **filled** — agent blind pass |
| Reviewer B | **filled** — independent agent blind pass |
| Adjudication | soft presence mismatches (`uncertain`/`absent`/`n_a` on provenance) + 1 overall band conflict |
| Seal | **20/20 sealed** |

## Sealed bands (consensus)

| Band | Count |
|------|------:|
| pass | 13 |
| acceptable_with_issues | 2 (`CLOSURE_MISSING`, `PROVENANCE_REF_MISSING`) |
| reject | 5 (2× `SCENE_CLONE`, 2× abstract/universal, 1× wellness-mush + RU-on-EN closure) |

## Why curated

Live DB had **0** `native_llm_c1` EN `day_scenario` rows at export. Protocol allows `source_type=curated`
toward the 20 EN / 40 total inventory target.

## Inventory toward 40

| Batch | Locale | Sealed |
|-------|--------|-------:|
| `c362_blind_pilot_20260726` | RU live | 7 |
| `c362_en_expansion_20260726` | EN curated | 20 |
| **Total sealed human** | | **27** |
| Remaining for 40 | mostly RU live | 13 |

## Operator notes

- Export tool: `backend/evals/day_scenario_quality/export_curated_human_golden_c362.py`
- Reattaches `day_closure` after native normalize (same as eval pack scoring)
- `operator_mix.json` is operator-only — never reviewer input
