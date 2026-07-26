# Character Engine — Readers pass 2 (life_areas demotion + Compat/Tarot soft SoT)

**Date:** 2026-07-26  
**Status:** LIVE  
**Depends on:** [CHARACTER_ENGINE_POST_CUTOVER_READERS_V0.md](./CHARACTER_ENGINE_POST_CUTOVER_READERS_V0.md)

## Architecture impact

- **SoT before:** Profile V0 taxonomy + remaining iOS spheres still preferred `interpretation.life_areas`; Compat/selector/natal personalization could read life_areas as primary person meaning; Tarot logs had no person SoT stamp.
- **SoT after:** Shared helper `person_meaning_from_core_v0` prefers `profile_contract_v1` / CE → interpretation. FE V0 taxonomy hero/love/money/decisions prefer contract. iOS Profile + QuickMap prefer contract styles + `life_spheres.*.how`. Compat personalized adds `person_sot` + `identity_line`. Tarot generation log stamps `person_sot`.
- **Public contract changed?** Compat personalized: optional `person_sot`, `identity_line`. Tarot log input: `person_sot`. No required-field breaks.
- **Migration required?** no.
- **Canon updated?** this audit + tracker.
- **Backward compatible?** yes — life_areas remain fallback only.

## Shared helper

`backend/src/todayflow_backend/services/person_meaning_from_core_v0.py`

| Function | Prefer |
|----------|--------|
| `person_sot_label` | CE ready → contract (CE stamp / identity) → interpretation |
| `identity_excerpt_from_core` | contract → CE projections → interpretation.identity |
| `sphere_excerpt_from_core` | contract `life_spheres` / style slots → life_areas |
| `strengths_from_core` / `watchouts_from_core` | contract → interpretation |

Wired into: Profile Selector, natal chart personalization, Compat personalized.

## Readers

| Surface | Change |
|---------|--------|
| FE V0 taxonomy | identity / strengths / love / money / decisions from contract first |
| FE V0 sphere cards | already contract-first (pass 1) |
| FE V2 life spheres | already contract-only |
| iOS Profile spheres | all cards: `life_spheres` / style → life_areas |
| iOS QuickMap | work/money/thrive/mission prefer contract |
| Compat personalized | `person_sot` + `identity_line` from experience slice / helper |
| Tarot | still experience_slice for meaning; soft `person_sot` in generation log |

## Not done

- Delete funnel/personality source files (evals still reference).
- Dual-SoT enablement (explicitly out of scope).
- Removing `life_areas` from API payload (legacy fallback remains).

## Tests

- `pytest backend/tests/test_person_meaning_from_core_v0.py`
- `pytest backend/tests/test_profile_selector_v1.py` (contract preference case)
