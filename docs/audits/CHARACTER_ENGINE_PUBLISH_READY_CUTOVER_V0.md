# Character Engine — PUBLISH_READY cutover v0

**Date:** 2026-07-26  
**Status:** LIVE — owner-approved cutover  
**Flag:** `CHARACTER_ENGINE_PUBLISH_READY=1`  
**Canon:** [CHARACTER_ENGINE_ARCHITECTURE_IMPACT_V1.md](./CHARACTER_ENGINE_ARCHITECTURE_IMPACT_V1.md) · [CHARACTER_ENGINE_SCHEMA_CONTRACTS_V0.md](./CHARACTER_ENGINE_SCHEMA_CONTRACTS_V0.md)

## Architecture impact

- **SoT before:** `profile_contract_v1` from personality / disclosure funnel / oneshot; CE nests + consumption overlay as de-facto Profile text; `character_engine_v1` stayed `forming`.
- **SoT after:** `payload.character_engine_v1` with `status=ready` is the portrait SoT for a profile hash. `profile_contract_v1` is a **projection** from CE adapters (`character_engine_contract_projection_v0` + consumption).
- **Public contract changed?** yes — `character_engine_v1.status` may be `ready`; `generation_meta.path/sot=character_engine_v1`. Legacy personality fields remain as DTO projections for readers.
- **Migration required?** soft — existing forming envelopes promote to `ready` on next GET when cascade complete; new publishes skip personality/funnel.
- **Canon updated?** this audit + tracker + schema §11 + `.env.production.example`.
- **Backward compatible?** readers that only use `profile_contract_v1` keep working via projection. Downstream modules not yet CE-native still read projected slots.
- **Kill on this cutover (live path gated):** `generate_personality` · disclosure funnel · oneshot via `build_profile_portrait_v1` hard gate when flag on.
- **Not yet:** file deletion of funnel modules · iOS/Today/Tarot/Compat reader migration · FE taxonomy kill.

## Publish path (flag on)

1. Natal facts ensure (unchanged).  
2. CE Stage 0–5 assemble (`include_stage2=True`, LLM allowed on 2–4).  
3. Envelope `character_engine_v1` → `ready` when complete.  
4. Project `profile_contract_v1` from CE adapters.  
5. Apply consumption into snapshot.  
6. Persist. **No** personality / funnel / oneshot.

## Read path

Unchanged assemble-once. Forming→ready promote once if flag on and nest complete.

## Rollback

Set `CHARACTER_ENGINE_PUBLISH_READY=0`, recreate backend. Envelopes demote `ready`→`forming` on read; next publish can use legacy portrait path again. Snapshots remain.

## Server check

`GET /account/core-profile` → `character_engine_v1.status=ready` · `profile_contract_v1.generation_meta.sot=character_engine_v1` (after promote or publish) · GET stays ~tens of ms.
