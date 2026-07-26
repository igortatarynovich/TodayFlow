# Character Engine Stage 5 — deterministic assembly (Compass + adapters)

**Date:** 2026-07-26  
**Canon:** [CHARACTER_ENGINE_ARCHITECTURE_IMPACT_V1.md](./CHARACTER_ENGINE_ARCHITECTURE_IMPACT_V1.md) Stage 5 · [CHARACTER_ENGINE_SCHEMA_CONTRACTS_V0.md](./CHARACTER_ENGINE_SCHEMA_CONTRACTS_V0.md) §6–§7  
**Depends on:** Stage 2–4 grounded  
**LLM:** **no**

## Architecture impact

- **SoT before:** Stage 2–4 diagnostics; Profile consumption projected ad-hoc from Stage 2–4 nests.
- **SoT after:** Stage 5 builds `compass` (`compass_v1`) + `legacy_map` (`character_engine_adapter_v1`) in `diagnostics.character_engine_stage5`. Pure functions of Stage 2–4 — no new claims, no LLM.
- **Profile consumption (v0.7):** when Stage 5 grounded, owned slots prefer `legacy_map` fields (decision / relationship / money / growth / helps / trap / strengths).
- **Public contract changed?** yes — optional diagnostics nest. **No** `character_engine_v1` ready publish.
- **Migration required?** no — flag-gated.
- **Canon updated?** this audit + tracker + schema §11.
- **Backward compatible?** yes when flags off.
- **Not:** `CHARACTER_ENGINE_PUBLISH_READY=1` cutover · kill legacy funnel · full cascade ready envelope.

## Modules

| Piece | Path |
|-------|------|
| Assembler | `character_engine_stage5_assembly_v0.py` |
| Shadow | `character_engine_stage5_shadow_v0.py` |
| Flags | `CHARACTER_ENGINE_STAGE5_SHADOW` / `ENABLED` |
| Tests | `test_character_engine_stage5_assembly_v0.py` |

## Live recipe

`STAGE01..4_SHADOW=1` · `STAGE5_SHADOW=1` · `PROFILE_CONSUMPTION=1` · `*_ENABLED=0` · `PUBLISH_READY=0`

## Exit / next

- Live smoke: Stage 5 nest grounded · consumption sources `stage5_legacy_map.*`
- Then owner decision on `PUBLISH_READY` cutover (separate PR with Architecture impact).
