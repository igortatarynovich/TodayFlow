# Day Scenario Eval Golden Set C3.5c

**Status:** SCAFFOLD ONLY — **0 labeled cases**  
**Date:** 2026-07-26  
**Depends on:** C3.5.1 hardening ([DAY_SCENARIO_EVAL_HARDENING_C351.md](./DAY_SCENARIO_EVAL_HARDENING_C351.md))

## Purpose

Human-labeled cases to calibrate provisional thresholds and validate defect codes against real (or curated) natives — **after** synthetic C3.5.1 matrix.

## Schema (per case)

```yaml
case_id: string          # stable id, e.g. gs-c35c-001
locale: ru | en
profile_id: string       # one of PROFILE_IDS or free-form capture tag
day_type: string | null  # optional DAY_TYPES label
source: synthetic | capture | curated
native_ref: string       # path or capture id (do not inline PII)
expected:
  band: reject | review | pass
  primary_defects: [string]   # defect codes expected present (may be empty for pass)
  axes_notes: string | null   # free-form rater note
raters:
  - id: string
    band: reject | review | pass
    notes: string | null
consensus_band: reject | review | pass | unresolved
labeled_at: YYYY-MM-DD | null
```

## Cases

_None yet._

| case_id | locale | profile_id | source | consensus_band | labeled_at |
|---------|--------|------------|--------|----------------|------------|
| — | — | — | — | — | — |

## Threshold calibration target

After ≥N labeled cases (product decides N):

1. Compare pack cell bands vs consensus.  
2. Adjust `THRESHOLDS_PROVISIONAL` / `PACK_PASS_THRESHOLD` only with Architecture impact.  
3. Feed defect frequency into live-shadow review.

## Non-goals

- Not a runtime SoT  
- Not a substitute for Nebius live shadow  
- No unlabeled bulk dumps in this file
