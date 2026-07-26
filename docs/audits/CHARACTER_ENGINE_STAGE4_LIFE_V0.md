# Character Engine Stage 4 — life_bundle (scenes · potential · blind spots)

**Date:** 2026-07-26  
**Canon:** [CHARACTER_ENGINE_ARCHITECTURE_IMPACT_V1.md](./CHARACTER_ENGINE_ARCHITECTURE_IMPACT_V1.md) Stage 4 · [CHARACTER_ENGINE_SCHEMA_CONTRACTS_V0.md](./CHARACTER_ENGINE_SCHEMA_CONTRACTS_V0.md) §2.1 · §9  
**Baseline CE:** `5eb61c6`  
**Depends on:** Stage 2 grounded + Stage 3 grounded

## Architecture impact

- **SoT before:** Stage 3 Internal Engine in diagnostics; Profile relationship/money/growth from editorial banks or Stage 3 slots.
- **SoT after:** Stage 4 `scenes` / `potential` / `blind_spots` in `diagnostics.character_engine_stage4`. Expand-only from Identity Core + engine + primary tension. `scene_kind` codes only (no career/love/money roots). Core rewrite / unknown claims / invalid scene_kind → `insufficient_life_bundle`.
- **Profile consumption (v0.6):** when Stage 4 grounded:
  - `relationship_style` ← scene `intimacy`
  - `money_style` ← scene `risk` | `responsibility` | `uncertainty` (resource proxy)
  - `growth_zones` / helps prefer `potential`
  - Stage 3 trap/decision remain preferred for those slots
- **Public contract changed?** yes — optional diagnostics nest; owned Profile slots may source Stage 4 when consumption on. No `character_engine_v1` ready publish.
- **Migration required?** no — flag-gated (`STAGE4_SHADOW` / `ENABLED` / consumption forces Stage 4 on Profile read).
- **Canon updated?** this audit + tracker + schema §11.
- **Backward compatible?** yes when flags off.
- **Not:** `CHARACTER_ENGINE_PUBLISH_READY` · Stage 5 Compass · adapters cutover.

## Modules

| Piece | Path |
|-------|------|
| Prompt | `profile.character_engine.stage4.v1` **1.0.0** |
| Builder | `character_engine_stage4_life_v0.py` |
| Shadow | `character_engine_stage4_shadow_v0.py` |
| Flags | `CHARACTER_ENGINE_STAGE4_SHADOW` / `ENABLED` |
| Tests | `test_character_engine_stage4_life_v0.py` |

## Live recipe

`STAGE01_SHADOW=1` · `STAGE2_SHADOW=1` · `STAGE3_SHADOW=1` · `STAGE4_SHADOW=1` · `PROFILE_CONSUMPTION=1` · `*_ENABLED=0` · `PUBLISH_READY=0`

## Exit / next

- Live voice skim: scenes feel like manifestations of the same Identity Core.
- Then Stage 5 deterministic Compass + adapters — not before Stage 4 live note.
