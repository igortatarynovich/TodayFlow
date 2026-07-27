# Day Scenario Human Golden Set C3.6.2

**Status:** LANDED (protocol + tooling · **0 production human labels**)  
**Date:** 2026-07-26  
**Code:** `day_scenario_human_golden_c362.py` · `day_scenario_review_agreement_c362.py` · `day_scenario_human_calibration_c362.py`  
**Schema:** [DAY_SCENARIO_HUMAN_GOLDEN_SCHEMA_C362.json](./DAY_SCENARIO_HUMAN_GOLDEN_SCHEMA_C362.json)  
**Rubric:** [DAY_SCENARIO_HUMAN_REVIEW_RUBRIC_C362.md](./DAY_SCENARIO_HUMAN_REVIEW_RUBRIC_C362.md)  
**Extends:** [DAY_SCENARIO_EVAL_GOLDEN_SET_C35C.md](./DAY_SCENARIO_EVAL_GOLDEN_SET_C35C.md) (no parallel golden model)

## Architecture impact

```markdown
## Architecture impact
- **SoT before:** C3.5c scaffold + C3.6.1 synthetic_bootstrap only
- **SoT after:** human case contract, blind export, dual review, adjudication,
  immutable consensus, agreement metrics, consensus→calibration adapter
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this note + rubric + schema + golden scaffold
- **Backward compatible?** yes — eval-only
- **Runtime / maturity / Nebius / UI / retry:** untouched; no promotions
```

## What this phase builds

| Piece | Role |
|-------|------|
| Human case contract | machine-readable case + versions + hash |
| Blind export | scenario for reviewers without analyzer/synthetic leakage |
| Review import | validate submissions + append-only history |
| Agreement | exact/weighted overall, per-code, kappa (with caveats) |
| Adjudication | required on disagreement; overrides recorded |
| Consensus | sealed immutable label (`label_source=human`) |
| Calibration adapter | reads **consensus only**; skips synthetic & cannot_assess |

## Inventory target (next batch — not auto-filled)

Minimum **40** human cases after process check:

- 20 RU · 20 EN  
- ≥10 pass · ≥10 acceptable_with_issues · ≥10 reject · remainder borderline  
- profile mix: deep · general · no profile · birth date only · no birth time  
- sources: curated + live_capture + some synthetic **without** leaking mutation names  
- include FP hotspots from C3.6.1: `SCENE_ABSTRACT`, `SCENE_CLONE`, personalization decorative/unchanged codes  

**Do not** generate 40 fake human labels in code. Run a real blind batch after protocol accept.

## Mixing ban

| Label source | May enter human calibration? |
|--------------|------------------------------|
| `human` consensus | yes |
| `synthetic_bootstrap` | **no** |

## Example cycle

`example_review_cycle_fixture()` — blind packet → two agreeing reviewers → sealed consensus → analyzer attach post-seal.

## Next

1. ~~**Pilot blind batch**~~ — [c362_blind_pilot_20260726](./day_scenario_human_golden/batches/c362_blind_pilot_20260726/) sealed (7 RU)
2. ~~**EN curated expansion**~~ — [c362_en_expansion_20260726](./day_scenario_human_golden/batches/c362_en_expansion_20260726/) sealed (20 EN)
3. ~~**RU live expansion**~~ — [c362_ru_live_expansion_20260727](./day_scenario_human_golden/batches/c362_ru_live_expansion_20260727/) sealed (13 RU) — **40/40 inventory**
4. ~~Feed consensus into calibration~~ — [DAY_SCENARIO_HUMAN_CALIBRATION_C362.md](./DAY_SCENARIO_HUMAN_CALIBRATION_C362.md) · baseline 40 cases
5. ~~Analyzer gaps (`SCENE_MISSING_EVERYDAY` R=0)~~ — lived-specificity fix · calib P=R=1.0
6. ~~watch `ASTRO_JARGON_BARE` FP~~ — shadow false blocks = 0
7. Next: improve `SCENE_UNIVERSAL_ADVICE` recall · keep candidate until then

