# Day Scenario Sphere Selection + Pairwise Eval C3.3b

**Status:** LANDED (justified sphere candidates · pairwise harness; lifecycle unchanged)  
**Date:** 2026-07-25  
**Code:** `day_scenario_sphere_selection_c33b.py` · `day_scenario_pairwise_eval_c33b.py`  
**Prompt:** `day-scenario-native-c3.3b`  
**Depends on:** [DAY_SCENARIO_PERSONALIZATION_C33A.md](./DAY_SCENARIO_PERSONALIZATION_C33A.md)

## Architecture impact

```markdown
## Architecture impact
- **SoT before:** sphere choice left to LLM with only soft SPHERE_UNJUSTIFIED checks
- **SoT after:** pack carries sphere_selection (ranked candidates + reasons + refs);
  gate rejects outside-pack spheres without justification; pairwise eval scores
  same-day A/B/control structural divergence without Nebius
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this note + DAY_SCENARIO_V1 + tracker
- **Backward compatible?** yes
- **Lifecycle / UI:** unchanged
```

## Sphere selection

Built after personalization pack, before prompt:

| Input | Effect |
|-------|--------|
| day domains / ritual head | shared day spheres |
| sensitive_domains (light/deep) | personal boost (light: capped) |
| behavioral_tendencies (deep) | tendency→sphere map |
| thesis family | fallback |

Output nest `personalization_evidence.sphere_selection`:

- `ranked_spheres` (≤4) with `reason`, `evidence_refs`, `source`, `weight`
- `primary_candidates`, `allowed_spheres`
- `must_justify_outside`

**Not** a full ranking of all life spheres every day.

## Extra defect codes

| Code | Semantics |
|------|-----------|
| `PERSONALIZATION_SPHERE_OUTSIDE_PACK` | sphere not in selection without reason/refs → retry → downgrade |
| `PERSONALIZATION_SPHERE_SELECTION_EMPTY` | depth set but empty selection |

## Pairwise production eval

`run_pairwise_eval_c33b` — fixture/captured scenarios only (no Nebius):

- same date / card / number / domains
- control (general) · profile A · profile B
- checks: control honesty, ≥2 structural diffs A↔B, no cross-profile evidence, gate clean
- `pass` when pairwise_score ≥ 0.8 and control score ≥ 0.8

## Out of scope

- C3.5 multi-day × multi-locale eval pack — **landed:** [DAY_SCENARIO_EVAL_PACK_C35.md](./DAY_SCENARIO_EVAL_PACK_C35.md)  
- UI depth / sphere badges  
- Profile generation changes  
- Live Nebius pairwise in CI
