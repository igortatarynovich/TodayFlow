# Day Scenario Gate Calibration C3.6.1

**Status:** LANDED (eval/calibration harness · synthetic bootstrap only)  
**Date:** 2026-07-26  
**Code:** `day_scenario_gate_calibration_c361.py`  
**Depends on:** C3.5.1 fixtures · C3.6 maturity registry (read-only)  
**Baseline:** [DAY_SCENARIO_GATE_CALIBRATION_BASELINE_C361.md](./DAY_SCENARIO_GATE_CALIBRATION_BASELINE_C361.md) · [`.json`](./DAY_SCENARIO_GATE_CALIBRATION_BASELINE_C361.json)

## Architecture impact

```markdown
## Architecture impact
- **SoT before:** C3.6 maturity observe-only for quality; no per-code calibration metrics
- **SoT after:** c36.1 harness + 14 synthetic golden cases; TP/FP/TN/FN; P/R/FPR with
  measured|insufficient_support; shadow false-block KPI; baseline artifacts
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this note + golden scaffold + tracker + DAY_SCENARIO_V1
- **Backward compatible?** yes — eval-only
- **Runtime / maturity modes / Nebius / UI / retry:** untouched (no promotions)
```

## Explicit limitations (baseline)

- Labels are **`synthetic_bootstrap`**, not human/editor consensus.  
- Baseline **does not authorize** maturity promotion.  
- Results are for **harness verification** and spotting **obvious false positives**.  
- Thresholds and maturity remain **provisional**.  
- Many codes have **`insufficient_support`** on 14 cases.  
- RU/EN results are **not comparable** without adequate support on both locales.  
- `actual_runtime_blocked ≈ 0` is the **expected** C3.6 observe-only policy outcome — not a quality win.

## Metrics per defect code

For each code the report includes:

| Field | Meaning |
|-------|---------|
| support_positive / support_negative | labeled with / without the code |
| true_positives / false_positives / true_negatives / false_negatives | confusion counts |
| precision / recall / false_positive_rate | `null` when status ≠ measured or denom=0 |
| by_locale.ru / by_locale.en | separate confusion + status |
| metric_status | `measured` \| `insufficient_support` |

`insufficient_support` when positive or negative support &lt; 2 (bootstrap floor). Metrics then are **N/A**, never fake 0/1.

## Shadow semantics

| Field | Meaning |
|-------|---------|
| actual_runtime_blocked | cases with blocking-maturity fires (policy today) |
| would_block_if_quality_promoted | counterfactual if any quality fire blocked |
| would_retry_if_quality_promoted | counterfactual retry (0 while quality has no retry) |
| false_blocks_against_labels | **primary KPI** — pass/good cases wrongly blocked if promoted |
| true_blocks_against_labels | reject+expected cases that would correctly block |

## Next

**C3.6.2 — Human Golden Set and Review Protocol**  
Manual labeling + disagreement resolution among raters before any promotion decision. Do not treat a single editor’s labels as consensus.
