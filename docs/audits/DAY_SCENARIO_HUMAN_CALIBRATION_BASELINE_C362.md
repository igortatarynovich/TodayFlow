# Day Scenario Human Calibration Baseline C3.6.2

**Status:** LANDED (human consensus calibration · eval-only · one observe promotion)
**Date:** 2026-07-27
**Cases:** 40 sealed human (`label_source=human`)
**Locales:** {'ru': 20, 'en': 20}

## Architecture impact

```markdown
## Architecture impact
- **SoT before:** C3.6.1 synthetic_bootstrap calibration only; human pilot used for C3.6.3 promotions
- **SoT after:** human consensus calibration over 40 sealed cases; analyzer P/R vs human labels;
  shadow false-block KPI; CHORUS_SEMANTIC_DUPLICATION → candidate_blocking (observe);
  SCENE_UNIVERSAL_ADVICE stays candidate_blocking (low recall)
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this baseline + tracker + DAY_SCENARIO_V1 + HUMAN_CALIBRATION_C362
- **Backward compatible?** yes — candidate_blocking remains observe-only (no retry/reject)
```

## Shadow KPI

- `actual_runtime_blocked`: **12**
- `false_blocks_against_labels`: **0**
- `true_blocks_against_labels`: **12**
- `would_block_if_SCENE_UNIVERSAL_ADVICE_promoted`: **12**
- `false_blocks_if_SCENE_UNIVERSAL_ADVICE_promoted`: **0**
- `true_blocks_if_SCENE_UNIVERSAL_ADVICE_promoted`: **12**

### False-block cases (pass/acceptable hit by blocking analyzer)

_none_

## Measured codes

| Code | maturity | P | R | FPR | +sup | −sup |
|------|----------|---|---|-----|------|------|
| `ASTRO_JARGON_BARE` | blocking | 0.625 | 0.7142857142857143 | 0.09090909090909091 | 7 | 33 |
| `CHORUS_SEMANTIC_DUPLICATION` | candidate_blocking | 1.0 | 1.0 | 0.0 | 6 | 27 |
| `CHORUS_UNTRANSLATED_JARGON` | experimental | 0.6666666666666666 | 1.0 | 0.06896551724137931 | 4 | 29 |
| `SCENE_ABSTRACT` | blocking | 1.0 | 1.0 | 0.0 | 10 | 30 |
| `SCENE_CLONE` | blocking | 1.0 | 0.7 | 0.0 | 10 | 30 |
| `SCENE_MISSING_CHOICE` | advisory | None | 0.0 | 0.0 | 6 | 34 |
| `SCENE_MISSING_EVERYDAY` | blocking | 1.0 | 1.0 | 0.0 | 10 | 30 |
| `SCENE_UNIVERSAL_ADVICE` | candidate_blocking | 1.0 | 0.18181818181818182 | 0.0 | 11 | 29 |
| `THESIS_ECHO` | experimental | None | 0.0 | 0.0 | 7 | 33 |

Insufficient support codes: **33**

## Promotion candidates (decision table)

| Code | now | recommend blocking? | reason |
|------|-----|---------------------|--------|
| `CHORUS_SEMANTIC_DUPLICATION` | candidate_blocking | yes | perfect measured P/R on n≥4 → promote to candidate_blocking (observe) |
| `CHORUS_UNTRANSLATED_JARGON` | experimental | no | measured but not yet recommended |
| `SCENE_MISSING_CHOICE` | advisory | no | measured but not yet recommended |
| `SCENE_UNIVERSAL_ADVICE` | candidate_blocking | no | keep candidate_blocking (P=1.0, R=0.18181818181818182, shadow_false=0, shadow_true=12) |
| `THESIS_ECHO` | experimental | no | measured but not yet recommended |

## Explicit limits

- Dual agent blind labels (not full human panel).
- EN cases are curated matrix + mutations; RU are live_capture.
- Analyzer attached post-seal via editorial gates (projected→native field map).
- Decision table may recommend observe promotions (`candidate_blocking`); full `blocking` only with separate product acceptance.
- Accepted observe promotion from this baseline: `CHORUS_SEMANTIC_DUPLICATION` → candidate_blocking.
