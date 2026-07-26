# Character Engine — Post-cutover kill + reader migration v0

**Date:** 2026-07-26  
**Status:** LIVE (partial reader migration)  
**Depends on:** [CHARACTER_ENGINE_PUBLISH_READY_CUTOVER_V0.md](./CHARACTER_ENGINE_PUBLISH_READY_CUTOVER_V0.md)

## Architecture impact

- **SoT before:** After PUBLISH_READY, CE was SoT on publish, but legacy generators could still be invoked; CUM/iOS/FE V0 spheres still preferred `interpretation.life_areas` / interpretation identity.
- **SoT after:** Defense-in-depth kill of `generate_personality` + disclosure funnel when flag on. CUM identity prefers `profile_contract_v1` → CE envelope → interpretation. Web V0 love/money cards and iOS Profile spheres/QuickMap prefer contract slots.
- **Public contract changed?** CUM `identity.sot` optional field. No breaking required fields.
- **Migration required?** no.
- **Canon updated?** this audit + tracker + prompt registry `deprecated` markers.
- **Backward compatible?** yes — legacy fields remain as fallback.
- **Not done yet:** full iOS life_areas removal · Tarot/Compat native CE readers · delete funnel/personality source files.

## Kill (live path)

| Path | Gate |
|------|------|
| `generate_personality` | returns `None` if `PUBLISH_READY` |
| `run_profile_disclosure_funnel_v0` | returns `(None, reason=publish_ready_cutover)` |
| `build_profile_portrait_v1` | already gated (prior cutover) |
| Prompt registry identity/styles/patterns/spheres/personality | marked `deprecated: character_engine_v1` |

## Readers

| Reader | Change |
|--------|--------|
| Profile Web V2 | already contract/CE consumption |
| Profile Web V0 spheres | love/money prefer contract styles / life_spheres |
| Profile iOS | spheres + QuickMap prefer `profileContractV1` |
| Compact User Model | identity from contract/CE |
| Today | already via experience_slice → profile_contract identity_line |
| Tarot / Compat | still snapshot readers; no new personality invent — follow-up |

## Next

1. Remove dead FE/iOS `life_areas` primary paths after QA.  
2. Compat pair-semantics CE pass.  
3. Optional file cleanup of funnel modules (keep until evals migrated).
