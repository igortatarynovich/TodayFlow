# Day Scenario Human Calibration C3.6.2 (baseline)

**Status:** LANDED (40 sealed human cases · eval-only)  
**Date:** 2026-07-27  
**Code:** `day_scenario_human_calibration_c362.py` · `evals/.../run_human_calibration_c362.py`  
**Baseline:** [DAY_SCENARIO_HUMAN_CALIBRATION_BASELINE_C362.md](./DAY_SCENARIO_HUMAN_CALIBRATION_BASELINE_C362.md) · [`.json`](./DAY_SCENARIO_HUMAN_CALIBRATION_BASELINE_C362.json)

## Architecture impact

```markdown
## Architecture impact
- **SoT before:** thin everyday escaped; ASTRO_JARGON_BARE blocked lived metaphors (shadow FP=2)
- **SoT after:** lived-specificity for everyday; ASTRO jargon requires missing human framing
  or echo-template+jargon (lived metaphor OK) — shadow FP=0
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — C31/C32 notes + calib baseline refresh
- **Backward compatible?** yes — fewer false runtime blocks; echo jargon still blocked
```

## Findings (short)

| Finding | Action |
|---------|--------|
| `ASTRO_JARGON_BARE` blocking | lived-metaphor + echo-template guard · shadow FP **0** (was 2) · P 0.5→0.625 |
| `SCENE_CLONE` / `SCENE_ABSTRACT` blocking | P≈1.0, FPR=0 — keep |
| `SCENE_MISSING_EVERYDAY` blocking | lived-specificity fix · calib **P=R=1.0**, FPR=0 |
| `SCENE_ABSTRACT` blocking | co-fires on thin everyday · calib **P=R=1.0** |
| `SCENE_UNIVERSAL_ADVICE` candidate | P=1.0 but R≈0.18 — stay candidate |
| `CHORUS_SEMANTIC_DUPLICATION` | P=R=1.0 → **candidate_blocking** |

## Next

- ~~Tighten everyday detector~~ — DONE
- ~~Revisit `ASTRO_JARGON_BARE` FP~~ — DONE (shadow false blocks = 0)
- Do **not** promote `SCENE_UNIVERSAL_ADVICE` until recall improves
