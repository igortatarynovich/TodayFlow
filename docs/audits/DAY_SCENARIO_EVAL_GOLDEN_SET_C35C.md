# Day Scenario Eval Golden Set C3.5c

**Status:** BOOTSTRAP SEEDED — synthetic provisional labels; **0 human-labeled cases**  
**Date:** 2026-07-26  
**Depends on:** C3.5.1 hardening · C3.6.1 calibration ([DAY_SCENARIO_GATE_CALIBRATION_C361.md](./DAY_SCENARIO_GATE_CALIBRATION_C361.md))

## Purpose

Human-labeled cases to calibrate provisional thresholds and validate defect codes —
**after** synthetic C3.5.1 matrix and C3.6.1 bootstrap metrics.

## Schema (per case)

```yaml
case_id: string          # stable id, e.g. gs-c35c-001 or gs-c361-*
locale: ru | en
profile_id: string       # one of PROFILE_IDS or free-form capture tag
day_type: string | null  # optional DAY_TYPES label
source: synthetic | capture | curated
label_source: synthetic_bootstrap | human
native_ref: string       # path, factory id, or capture id (do not inline PII)
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

### A. Synthetic bootstrap (C3.6.1) — provisional, not human consensus

Loaded by `bootstrap_golden_cases_c361()` — fixtures live in code, not PII.

| case_id | locale | profile_id | source | label_source | consensus_band | primary_defects (provisional) |
|---------|--------|------------|--------|--------------|----------------|-------------------------------|
| gs-c361-good-ru | ru | smooth_conflict | synthetic | synthetic_bootstrap | pass | — |
| gs-c361-good-en | en | smooth_conflict | synthetic | synthetic_bootstrap | pass | — |
| gs-c361-neg-abstract-ru | ru | smooth_conflict | synthetic | synthetic_bootstrap | reject | SCENE_ABSTRACT, SCENE_UNIVERSAL_ADVICE |
| gs-c361-neg-clone-ru | ru | smooth_conflict | synthetic | synthetic_bootstrap | reject | SCENE_CLONE |
| gs-c361-neg-parallel-ru | ru | smooth_conflict | synthetic | synthetic_bootstrap | reject | CHORUS_PARALLEL_FORECAST |
| gs-c361-neg-closure-missing-ru | ru | smooth_conflict | synthetic | synthetic_bootstrap | reject | CLOSURE_MISSING |
| gs-c361-neg-closure-mush-ru | ru | smooth_conflict | synthetic | synthetic_bootstrap | reject | CLOSURE_WELLNESS_MUSH |
| gs-c361-neg-conflict-ru | ru | smooth_conflict | synthetic | synthetic_bootstrap | reject | CONFLICT_NO_OPPOSITION |
| gs-c361-neg-provenance-ru | ru | smooth_conflict | synthetic | synthetic_bootstrap | reject | PROVENANCE_REF_MISSING |
| gs-c361-neg-locale-en | en | smooth_conflict | synthetic | synthetic_bootstrap | reject | LOCALE_LANGUAGE_MISMATCH |
| gs-c361-neg-locale-ru | ru | smooth_conflict | synthetic | synthetic_bootstrap | reject | LOCALE_LANGUAGE_MISMATCH |
| gs-c361-mut-universal-en | en | smooth_conflict | synthetic | synthetic_bootstrap | reject | SCENE_UNIVERSAL_ADVICE, SCENE_ABSTRACT |
| gs-c361-mut-clone-ru | ru | smooth_conflict | synthetic | synthetic_bootstrap | reject | SCENE_CLONE |
| gs-c361-mut-drop-closure-en | en | smooth_conflict | synthetic | synthetic_bootstrap | reject | CLOSURE_MISSING |

Metrics snapshot: [DAY_SCENARIO_GATE_CALIBRATION_BASELINE_C361.md](./DAY_SCENARIO_GATE_CALIBRATION_BASELINE_C361.md)

### B. Human-labeled (C3.6.2 protocol)

**Protocol + tooling landed** — [DAY_SCENARIO_HUMAN_GOLDEN_C362.md](./DAY_SCENARIO_HUMAN_GOLDEN_C362.md) · [rubric](./DAY_SCENARIO_HUMAN_REVIEW_RUBRIC_C362.md).  
**Production human labels:** none yet (do not invent 40 fake consensus rows in code).

| case_id | locale | profile_id | source | consensus_band | labeled_at |
|---------|--------|------------|--------|----------------|------------|
| — | — | — | — | — | — |

Example tooling cycle: [DAY_SCENARIO_HUMAN_GOLDEN_EXAMPLE_CYCLE_C362.json](./DAY_SCENARIO_HUMAN_GOLDEN_EXAMPLE_CYCLE_C362.json)

## Next

**Human labeling batch** under C3.6.2 protocol (blind dual review + adjudication) → consensus calibration → promotions only with evidence.

## Non-goals

- Not a runtime SoT  
- Not a substitute for Nebius live shadow  
- No unlabeled bulk dumps in this file  
- No automatic maturity promotion from synthetic labels
