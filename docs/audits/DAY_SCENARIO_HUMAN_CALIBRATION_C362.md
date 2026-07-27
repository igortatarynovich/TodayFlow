# Day Scenario Human Calibration C3.6.2 (baseline)

**Status:** LANDED (40 sealed human cases · eval-only)  
**Date:** 2026-07-27  
**Code:** `day_scenario_human_calibration_c362.py` · `evals/.../run_human_calibration_c362.py`  
**Baseline:** [DAY_SCENARIO_HUMAN_CALIBRATION_BASELINE_C362.md](./DAY_SCENARIO_HUMAN_CALIBRATION_BASELINE_C362.md) · [`.json`](./DAY_SCENARIO_HUMAN_CALIBRATION_BASELINE_C362.json)

## Architecture impact

```markdown
## Architecture impact
- **SoT before:** C3.6.1 synthetic_bootstrap only; C3.6.3 promotions from pilot evidence
- **SoT after:** human consensus calibration over 40 sealed cases; analyzer P/R;
  shadow false-block KPI; CHORUS_SEMANTIC_DUPLICATION → candidate_blocking (observe);
  SCENE_UNIVERSAL_ADVICE stays candidate_blocking (low recall)
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this note + baseline + tracker + DAY_SCENARIO_V1
- **Backward compatible?** yes — candidate_blocking remains observe-only
```

## Findings (short)

| Finding | Action |
|---------|--------|
| `SCENE_CLONE` / `SCENE_ABSTRACT` blocking | P≈1.0, FPR=0 — keep |
| `ASTRO_JARGON_BARE` blocking | P=0.5, FPR≈0.15 — **watch**; both false blocks are this code (`hg-f61a374bc5aa`, `hg-95113b431251`) |
| `SCENE_MISSING_EVERYDAY` blocking | human+ but analyzer R=0 on projected map — **analyzer gap** |
| `SCENE_UNIVERSAL_ADVICE` candidate | P=1.0 but R≈0.18 — stay candidate |
| `CHORUS_SEMANTIC_DUPLICATION` | P=R=1.0 → **candidate_blocking** |

## Next

- Tighten everyday detector on projected `domestic_example` fields
- Revisit `ASTRO_JARGON_BARE` FP before broader blocking confidence
- Do **not** promote `SCENE_UNIVERSAL_ADVICE` until recall improves
