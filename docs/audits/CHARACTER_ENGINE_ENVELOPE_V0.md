# Character Engine — Envelope `character_engine_v1` v0 (forming)

**Date:** 2026-07-26  
**Status:** LIVE SHADOW — nest written as `forming`; **PUBLISH_READY=0**  
**Canon:** [CHARACTER_ENGINE_ARCHITECTURE_IMPACT_V1.md](./CHARACTER_ENGINE_ARCHITECTURE_IMPACT_V1.md) D1 · [CHARACTER_ENGINE_SCHEMA_CONTRACTS_V0.md](./CHARACTER_ENGINE_SCHEMA_CONTRACTS_V0.md) §2  
**Depends on:** Stage 0–5 diagnostics nests

## Architecture impact

- **SoT before:** CE lived only under `diagnostics.character_engine_stage*` (+ Profile consumption overlay).
- **SoT after:** Snapshot may also hold `payload.character_engine_v1` composed from Stage 0–5. Status stays **`forming`** until owner enables `CHARACTER_ENGINE_PUBLISH_READY`.
- **Public contract changed?** yes — optional root `character_engine_v1` on `GET /account/core-profile`. Not yet Profile SoT (`PUBLISH_READY=0`; consumption still projects from Stage nests / legacy_map).
- **Migration required?** no — fill-once on read when Stage 5 present and envelope missing; assemble-once thereafter.
- **Canon updated?** this audit + tracker + schema §11 item.
- **Backward compatible?** yes when readers ignore the nest.
- **Not:** ready cutover · kill funnel/oneshot · dual-SoT.

## Modules

| Piece | Path |
|-------|------|
| Envelope builder | `character_engine_envelope_v0.py` |
| Attach | after Stage 5 in `core_profile._maybe_attach_character_engine_shadow` |
| API | `CoreProfileResponse.character_engine_v1` |
| Tests | `test_character_engine_envelope_v0.py` |

## Assemble-once

Same `profile_fingerprint` + existing envelope → no rebuild on GET.  
Rebuild on portrait publish (`force=True`) or new hash.

## Exit / next

1. Live smoke: nest present · `status=forming` · schema validate · GET stays fast.  
2. Owner decision on `PUBLISH_READY` (separate Architecture impact PR).  
3. After cutover: kill list (funnel / oneshot) per Architecture Impact.
