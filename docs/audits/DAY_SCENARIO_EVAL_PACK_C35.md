# Day Scenario Eval Pack C3.5

**Status:** LANDED (comparative harness · synthetic CI matrix; no Nebius)  
**Date:** 2026-07-25  
**Code:** `day_scenario_eval_pack_c35.py` · `tests/test_day_scenario_eval_pack_c35.py`  
**Depends on:** C3.1–C3.3b gates / pairwise scoring  

## Architecture impact

```markdown
## Architecture impact
- **SoT before:** pairwise same-day eval only (C3.3b); no multi-day / multi-locale pack
- **SoT after:** eval pack scores 14d × ≥3 natal profiles + no-birth-time × ru/en
  on fixture/captured scenarios; axes cover conflict/scenes/chorus/diff/repeat/
  provenance/parallel/closure
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this note + DAY_SCENARIO_V1 + tracker
- **Backward compatible?** yes
- **Lifecycle / UI:** unchanged — eval-only, not runtime SoT
```

## Matrix

| Axis | Requirement |
|------|-------------|
| Days | 14 consecutive |
| Profiles | `smooth_conflict`, `demand_clarity`, `analyze_first`, `no_birth_time` |
| Locales | `ru`, `en` |
| Compare | same dates across profiles |

CI uses `build_synthetic_eval_matrix_c35` (112 cells). Live Nebius captures can be fed into `run_eval_pack_c35` the same way — **not** required in CI.

## Score axes

| Axis | Source |
|------|--------|
| `conflict_recognizability` | title + opposing forces + thesis |
| `scene_concreteness` | RU: C3.1 editorial gate · EN: eval-side concrete heuristic |
| `chorus_coherence` | C3.2 chorus defects |
| `user_differentiation` | structural diffs A↔B↔C same day; control honesty |
| `formulation_repeatability` | token Jaccard across consecutive days (lower = better) |
| `recommendation_provenance` | actions/props anchored to scene / evidence |
| `no_parallel_forecasts` | chorus parallel / semantic-dupe codes |
| `day_closure_quality` | affirmation / prop closure present, not mush |

`pass` when `shape_ok` and `pack_score ≥ 0.75`.

## EN note

Production editorial gate remains **RU-primary**. EN cells use an eval-only concrete heuristic so the pack can compare locales without expanding the runtime gate in this phase.

## Out of scope

- Visual polish / UI redesign — **after** capture review with this harness  
- Live Nebius in CI (optional offline captures via `run_eval_pack_c35`)  
- Changing GET lifecycle  
- Formula rewrite of failed LLM output  
- Expanding production language gate to EN (later)

## Recommended next (capture review)

1. Run several weeks of real scenarios through the pack (or feed captures into `run_eval_pack_c35`).  
2. Rank editorial / personalization defect codes by frequency.  
3. Spot repeated phrasing and weak everyday scenes.  
4. Only then do visual/language polish against those findings.
