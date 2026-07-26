# Character Engine Stage 3 — Internal Engine (shadow + Profile consumption)

**Date:** 2026-07-26  
**Canon:** [CHARACTER_ENGINE_ARCHITECTURE_IMPACT_V1.md](./CHARACTER_ENGINE_ARCHITECTURE_IMPACT_V1.md) Stage 3 · [CHARACTER_ENGINE_SCHEMA_CONTRACTS_V0.md](./CHARACTER_ENGINE_SCHEMA_CONTRACTS_V0.md) §1.4  
**Baseline CE:** `5eb61c6`  
**Owner override:** proceed Stage 3 despite prior HOLD / §1.4 OPEN skim (explicit product request).

## Architecture impact

- **SoT before:** Stage 2 Identity Core in diagnostics (+ Profile consumption v0.4 editorial banks for trap/decision). No Internal Engine artifact.
- **SoT after:** Stage 3 `internal_engine` + `primary_tension` (+ 0..3 secondary) in `diagnostics.character_engine_stage3`. Expand-only: `identity_thesis_echo` must match Stage 2 thesis; unknown claim_ids rejected; core rewrite → `insufficient_internal_engine`.
- **Profile consumption (v0.5):** when Stage 3 grounded:
  - trap / `recurring_patterns` ← `primary_tension.surface_text`
  - `decision_style` ← `internal_engine.decision.surface_text`
  - helps prefer growth/recovery surfaces
  - else editorial banks (v0.4) remain fallback
- **Public contract changed?** yes — optional diagnostics nest; owned Profile slots may source Stage 3 when consumption on. No `character_engine_v1` ready publish.
- **Migration required?** no — flag-gated (`STAGE3_SHADOW` / `STAGE3_ENABLED` / consumption forces Stage 3 on Profile read).
- **Canon updated?** this audit + tracker + schema §11 flag table.
- **Backward compatible?** yes when flags off; with consumption on, trap/decision text authority moves to Stage 3 when grounded.
- **Not:** `CHARACTER_ENGINE_PUBLISH_READY` · Stage 4–5 · Compass.

## Modules

| Piece | Path |
|-------|------|
| Prompt | `profile.character_engine.stage3.v1` **1.0.0** |
| Builder | `character_engine_stage3_internal_v0.py` |
| Shadow | `character_engine_stage3_shadow_v0.py` |
| Flags | `CHARACTER_ENGINE_STAGE3_SHADOW` / `ENABLED` |
| Tests | `test_character_engine_stage3_internal_v0.py` |

## Live recipe

`STAGE01_SHADOW=1` · `STAGE2_SHADOW=1` · `STAGE3_SHADOW=1` · `PROFILE_CONSUMPTION=1` · `*_ENABLED=0` · `PUBLISH_READY=0`

## Exit / next

- Live voice skim: «This is a manifestation of the Identity Core because…» on production-like packs.
- Then Stage 4 scenes — not before Stage 3 live review note.
