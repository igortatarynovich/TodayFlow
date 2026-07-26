# Gate Calibration Report (c36.1)

- Cases: **14** (RU=10, EN=4)
- Label sources: `synthetic_bootstrap`
- Positive / negative labeled cases: 12 / 2
- Human labels complete: **False**
- Maturity promotion performed: **False**
- Runtime unchanged: **True**
- Public contract unchanged: **True**

## Limitations

- Labels are synthetic_bootstrap, not human/editor consensus.
- Baseline does not authorize maturity promotion.
- Results verify harness wiring and surface obvious false positives only.
- Thresholds and maturity remain provisional.
- Many codes have insufficient_support on a 14-case bootstrap.
- RU/EN metrics are not comparable without adequate support on both locales.
- actual_runtime_blocked≈0 is expected under observe-only quality policy.

## Shadow (counterfactual vs policy)

- `actual_runtime_blocked`: **0** (expected ~0 while quality is observe-only)
- `would_block_if_quality_promoted`: **14**
- `would_retry_if_quality_promoted`: **0**
- `false_blocks_against_labels` (good/pass wrongly blocked): **2** ← primary shadow KPI
- `true_blocks_against_labels`: **12**

_actual_runtime_blocked==0 is expected under C3.6 quality=observe policy; it is not a quality score. Primary shadow KPI: false_blocks_against_labels (pass/good cases that would be wrongly blocked if quality codes became blocking)._

### Worst false-block codes (pass labels)

| Code | False blocks on pass | FP (all) | Metric status |
|------|---------------------:|---------:|---------------|
| `PERSONALIZATION_CONFLICT_UNCHANGED` | 2 | 6 | insufficient_support |
| `PERSONALIZATION_DECORATIVE_ONLY` | 2 | 6 | insufficient_support |
| `PERSONALIZATION_SCENES_UNCHANGED` | 2 | 6 | insufficient_support |
| `SCENE_ABSTRACT` | 1 | 10 | measured |
| `THESIS_ECHO` | 1 | 10 | insufficient_support |
| `SCENE_CLONE` | 1 | 8 | measured |
| `PERSONALIZATION_NATAL_OVERCLAIM` | 0 | 8 | insufficient_support |
| `CHORUS_ROLE_DRIFT` | 0 | 1 | insufficient_support |
| `CLOSURE_NO_CONFLICT_CALLBACK` | 0 | 1 | insufficient_support |
| `CHORUS_PARALLEL_FORECAST` | 0 | 0 | insufficient_support |
| `CLOSURE_MISSING` | 0 | 0 | measured |
| `CLOSURE_WELLNESS_MUSH` | 0 | 0 | insufficient_support |

## Per-code metrics

| Code | Status | +/− support | TP | FP | TN | FN | P | R | FPR | RU status | EN status | False blocks on pass |
|------|--------|------------:|---:|---:|---:|---:|---|---|-----|-----------|-----------|---------------------:|
| `CHORUS_PARALLEL_FORECAST` | insufficient_support | 1/13 | 1 | 0 | 13 | 0 | N/A | N/A | N/A | insufficient_support | insufficient_support | 0 |
| `CHORUS_ROLE_DRIFT` | insufficient_support | 0/14 | 0 | 1 | 13 | 0 | N/A | N/A | N/A | insufficient_support | insufficient_support | 0 |
| `CLOSURE_MISSING` | measured | 2/12 | 2 | 0 | 12 | 0 | 1.00 | 1.00 | 0.00 | insufficient_support | insufficient_support | 0 |
| `CLOSURE_NO_CONFLICT_CALLBACK` | insufficient_support | 0/14 | 0 | 1 | 13 | 0 | N/A | N/A | N/A | insufficient_support | insufficient_support | 0 |
| `CLOSURE_WELLNESS_MUSH` | insufficient_support | 1/13 | 1 | 0 | 13 | 0 | N/A | N/A | N/A | insufficient_support | insufficient_support | 0 |
| `CONFLICT_NO_OPPOSITION` | insufficient_support | 1/13 | 1 | 0 | 13 | 0 | N/A | N/A | N/A | insufficient_support | insufficient_support | 0 |
| `LOCALE_LANGUAGE_MISMATCH` | measured | 2/12 | 2 | 0 | 12 | 0 | 1.00 | 1.00 | 0.00 | insufficient_support | insufficient_support | 0 |
| `PERSONALIZATION_CONFLICT_UNCHANGED` | insufficient_support | 0/14 | 0 | 6 | 8 | 0 | N/A | N/A | N/A | insufficient_support | insufficient_support | 2 |
| `PERSONALIZATION_DECORATIVE_ONLY` | insufficient_support | 0/14 | 0 | 6 | 8 | 0 | N/A | N/A | N/A | insufficient_support | insufficient_support | 2 |
| `PERSONALIZATION_NATAL_OVERCLAIM` | insufficient_support | 0/14 | 0 | 8 | 6 | 0 | N/A | N/A | N/A | insufficient_support | insufficient_support | 0 |
| `PERSONALIZATION_SCENES_UNCHANGED` | insufficient_support | 0/14 | 0 | 6 | 8 | 0 | N/A | N/A | N/A | insufficient_support | insufficient_support | 2 |
| `PROVENANCE_REF_MISSING` | insufficient_support | 1/13 | 1 | 0 | 13 | 0 | N/A | N/A | N/A | insufficient_support | insufficient_support | 0 |
| `SCENE_ABSTRACT` | measured | 2/12 | 2 | 10 | 2 | 0 | 0.17 | 1.00 | 0.83 | insufficient_support | insufficient_support | 1 |
| `SCENE_CLONE` | measured | 2/12 | 2 | 8 | 4 | 0 | 0.20 | 1.00 | 0.67 | measured | insufficient_support | 1 |
| `SCENE_UNIVERSAL_ADVICE` | measured | 2/12 | 2 | 0 | 12 | 0 | 1.00 | 1.00 | 0.00 | insufficient_support | insufficient_support | 0 |
| `THESIS_ECHO` | insufficient_support | 0/14 | 0 | 10 | 4 | 0 | N/A | N/A | N/A | insufficient_support | insufficient_support | 1 |

### Insufficient support (11)

`CHORUS_PARALLEL_FORECAST`, `CHORUS_ROLE_DRIFT`, `CLOSURE_NO_CONFLICT_CALLBACK`, `CLOSURE_WELLNESS_MUSH`, `CONFLICT_NO_OPPOSITION`, `PERSONALIZATION_CONFLICT_UNCHANGED`, `PERSONALIZATION_DECORATIVE_ONLY`, `PERSONALIZATION_NATAL_OVERCLAIM`, `PERSONALIZATION_SCENES_UNCHANGED`, `PROVENANCE_REF_MISSING`, `THESIS_ECHO`

## Next

**C3.6.2 — Human Golden Set and Review Protocol** (manual labeling + disagreement resolution before any promotion).


_Generated from synthetic_bootstrap — harness check only; not human-labeled; not promotion evidence._
