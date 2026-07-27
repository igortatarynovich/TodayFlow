# Day Scenario Human Calibration C3.6.2 (baseline)

**Status:** LANDED (40 sealed human cases · eval-only)  
**Date:** 2026-07-27  
**Code:** `day_scenario_human_calibration_c362.py` · `evals/.../run_human_calibration_c362.py`  
**Baseline:** [DAY_SCENARIO_HUMAN_CALIBRATION_BASELINE_C362.md](./DAY_SCENARIO_HUMAN_CALIBRATION_BASELINE_C362.md) · [`.json`](./DAY_SCENARIO_HUMAN_CALIBRATION_BASELINE_C362.json)

## Architecture impact

```markdown
## Architecture impact
- **SoT before:** MISSING_EVERYDAY = empty/short only; bare «» counted as concrete; thin tips often ABSTRACT-only or escaped
- **SoT after:** lived-specificity (time/quote/person+act/channel/long+marker); thin tip → MISSING (+ ABSTRACT co-label);
  bare guillemets no longer count as concrete
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — DAY_SCENARIO_EVERYDAY_QUALITY_C31 + calib baseline refresh
- **Backward compatible?** yes — stronger quality block on thin everyday (already blocking maturity)
```

## Findings (short)

| Finding | Action |
|---------|--------|
| `SCENE_CLONE` / `SCENE_ABSTRACT` blocking | P≈1.0, FPR=0 — keep |
| `ASTRO_JARGON_BARE` blocking | P=0.5, FPR≈0.15 — **watch**; both false blocks are this code (`hg-f61a374bc5aa`, `hg-95113b431251`) |
| `SCENE_MISSING_EVERYDAY` blocking | lived-specificity fix · calib **P=R=1.0**, FPR=0 |
| `SCENE_ABSTRACT` blocking | co-fires on thin everyday · calib **P=R=1.0** |
| `SCENE_UNIVERSAL_ADVICE` candidate | P=1.0 but R≈0.18 — stay candidate |
| `CHORUS_SEMANTIC_DUPLICATION` | P=R=1.0 → **candidate_blocking** |

## Next

- Tighten everyday detector on projected `domestic_example` fields — **DONE** (lived-specificity; thin→MISSING)
- Revisit `ASTRO_JARGON_BARE` FP before broader blocking confidence
- Do **not** promote `SCENE_UNIVERSAL_ADVICE` until recall improves
