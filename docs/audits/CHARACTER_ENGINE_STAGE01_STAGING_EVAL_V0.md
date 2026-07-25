# Character Engine Stage 0–1 — Staging Evaluation v0

**Date:** 2026-07-25  
**Status:** GATE PASS (synthetic fixed profiles)  
**CE baseline commit:** `5eb61c665b04cf1ade8f15939a0bf2acfcf1adc5` (`feat(character-engine): add LLM-first identity core shadow`)  
**Note:** Cite this SHA as CE baseline — not the current tip of `design/profile-journey-premium` (branch may already contain later Day Scenario / Tarot commits).  

**Flags for live Stage 0–1 shadow review (only):**
```
CHARACTER_ENGINE_STAGE01_SHADOW=1
CHARACTER_ENGINE_STAGE01_ENABLED=0
CHARACTER_ENGINE_STAGE2_SHADOW=0
CHARACTER_ENGINE_STAGE2_ENABLED=0
CHARACTER_ENGINE_PUBLISH_READY=0
```
Enable Stage 2 shadow only after real-pack Stage 0–1 diagnostics review.  

**SoT:** unchanged — diagnostics only; funnel / `personality` remain publish path.

## Profiles (fixed fixture)

`backend/tests/fixtures/character_engine_stage01_staging_profiles_v0.json`

| id | Intent |
|----|--------|
| `full_natal_air_asc` | Full natal + ASC/houses |
| `date_only` | Date-only capability; Leo negative control |
| `no_name_no_numerology` | Capricorn without numerology |
| `conflicting_sources` | Autonomy sun + structure LP + earth moon |
| `bridge_diverges_swiss` | Swiss Virgo vs bridge Leo |
| `earth_analysis` | Distinct analysis chart |
| `water_emotional` | Distinct water chart |
| `fire_direct` | Distinct fire autonomy chart |

Runner: `python -m todayflow_backend.services.character_engine_stage01_staging_eval_v0`

## Findings (pre-tighten)

- `autonomy_high` fired on **5/8** when life_path alone could mint autonomy (LP 1/5/7 OR autonomy sun).
- `direction_through_ideas` duplicated autonomy for air suns.
- `analysis_before_action` fired on Aquarius via LP7 overlap — polluted autonomy charts.
- Leo date-only correctly produced **zero** claims (no generic Sun+LP portrait) — kept as negative control.

## Registry corrections applied

1. Autonomy / analysis require **sun pattern**; life_path only **strengthens**.
2. Removed standalone `air_sun_direction_v0` claim.
3. Rebalanced fixtures so autonomy suns are not the majority sample.
4. Gates: Swiss>bridge · no ASC without full natal · repeatability · negative controls · no thesis on >50% of set · distinct claim sets across archetypes.

## Post-tighten thesis frequency

| thesis_key | count / 8 |
|------------|-----------|
| autonomy_high | 3 |
| analysis_before_action | 3 |
| emotional_sensitivity_high | 2 |
| freedom_vs_stability | 2 |
| presence_through_air_asc | 1 |

## Gate checklist (before Stage 2)

| Gate | Result |
|------|--------|
| No unknown fact/claim/edge refs | PASS |
| Same input → stable IDs | PASS |
| Swiss displaces bridge | PASS |
| Full-natal claims absent without birth time | PASS |
| Registry not emitting one claim set to most profiles | PASS |
| Diagnostics do not change active Snapshot semantics | PASS (by design) |

## Residual semantic risk

- Registry is still sun-element thin (few mechanisms). Expand carefully with **AND** patterns, not broad OR.
- Live server profiles may still cluster; re-run this eval with anonymized staging packs before Stage 3.
- Empty evidence (Leo) → Stage 2 must return `insufficient_identity_core` (covered in Stage 2 tests).

## Next

Live review order:
1. Stage 0–1 shadow only (flags above) on real packs — inspect facts, authority dedupe, claim breadth, exclusions.
2. Separately enable `CHARACTER_ENGINE_STAGE2_SHADOW=1` after that review.
3. Stage 3+ only after Stage 2 **exit criterion** (canon [CHARACTER_ENGINE_SCHEMA_CONTRACTS_V0 §1.4](./CHARACTER_ENGINE_SCHEMA_CONTRACTS_V0.md)): Identity Core is sole SoT; Stage 3–5 expand, never reinterpret. Review question: *«This is a manifestation of the Identity Core because…»*.

Stage 2 Identity Core is **LLM-first**: prompt `profile.character_engine.stage2.v1` chooses one core; code validates structure/provenance only (not interpretation quality).  
Do not add quality-scoring gates that duplicate the prompt.
