# Character Engine Stage 0–1 — Staging Evaluation v0 / v1

**Date:** 2026-07-26 (v1 expansion) · prior GATE PASS 2026-07-25  
**Status:** **GATE PASS (v1)** — expanded registry + 16 fixtures  
**CE baseline commit:** `5eb61c665b04cf1ade8f15939a0bf2acfcf1adc5`  
**Eval version:** `character_engine_stage01_staging_eval_v1`

**SoT:** unchanged — diagnostics only; funnel / `personality` remain publish path.

## Expansion intent (v1)

Live gap was thin registry → high empty rate (Gemini/Taurus/etc.). Expand with **AND** sun/moon/ASC patterns — not LP-alone OR mints.

New Stage 1 theses:

| thesis_key | Pattern (AND) |
|------------|----------------|
| `direction_through_air_mind` | Sun Gemini/Libra (Aquarius stays autonomy) |
| `stability_through_earth` | Sun Taurus (Virgo/Cap stay analysis) |
| `care_through_water_sun` | Sun Cancer/Pisces |
| `anchor_through_earth_moon` | Earth moon AND sun not autonomy |
| `drive_through_fire_mars` | Mars in fire + sun present |
| `presence_through_{fire,earth,water}_asc` | Full natal ASC element |

Identity thesis map updated for all emitted keys (Stage 2 normalize).

## Profiles (fixed fixture)

`backend/tests/fixtures/character_engine_stage01_staging_profiles_v0.json` (fixture_version **v1**)

| id | Intent |
|----|--------|
| `full_natal_air_asc` | Full natal + air ASC |
| `full_natal_earth_asc` | Gemini + Taurus ASC |
| `full_natal_fire_asc` | Capricorn + Aries ASC |
| `full_natal_water_asc` | Taurus + Cancer ASC |
| `date_only` | Leo negative control (empty) |
| `no_name_no_numerology` | Capricorn analysis sans LP |
| `conflicting_sources` | Autonomy + structure LP + earth moon |
| `bridge_diverges_swiss` | Swiss Virgo > bridge Leo |
| `earth_analysis` | Virgo + earth moon anchor |
| `water_emotional` | Cancer care + Scorpio moon |
| `fire_direct` | Sagittarius + fire mars |
| `gemini_air_mind` | Live gap — Gemini |
| `taurus_earth_stable` | Live gap — Taurus |
| `libra_air_mind` | Libra + earth moon |
| `pisces_water_care` | Pisces care |
| `scorpio_analysis_water_moon` | Scorpio + water moon |

Runner: `python -m todayflow_backend.services.character_engine_stage01_staging_eval_v0`

## Post-expansion thesis frequency (16 packs)

| thesis_key | count / 16 | share |
|------------|------------|-------|
| analysis_before_action | 5 | 0.31 |
| autonomy_high | 3 | 0.19 |
| emotional_sensitivity_high | 3 | 0.19 |
| direction_through_air_mind | 3 | 0.19 |
| freedom_vs_stability | 2 | 0.12 |
| drive_through_fire_mars | 2 | 0.12 |
| stability_through_earth | 2 | 0.12 |
| anchor_through_earth_moon | 2 | 0.12 |
| care_through_water_sun | 2 | 0.12 |
| presence_through_*_asc | 1 each | 0.06 |

**Empty claim packs:** 1/16 (0.062) — Leo negative control only.

## Gate checklist

| Gate | Result |
|------|--------|
| all_cases_ok / repeatable IDs | PASS |
| Swiss displaces bridge | PASS |
| Full-natal ASC gated | PASS |
| No thesis on >50% of set | PASS |
| Distinct claim sets (≥5 among archetype subset) | PASS |
| Live-gap charts nonempty (Gemini/Taurus/Pisces) | PASS |
| Stage1→identity thesis map complete | PASS |
| Leo negative control empty | PASS |
| Diagnostics do not change Snapshot SoT | PASS (by design) |

## Residual risk

- `analysis_before_action` is the densest thesis (still ≤50%). Prefer AND-tightening over new broad OR if it climbs.
- Leo still has no fire-sun expression rule by design (preserves empty control). Add Leo expression only with a separate negative control.
- Next: Stage 2 staging/eval over the same 16 packs (logline/voice) before more live prod testing.

## Prior v0 note (2026-07-25)

Tightened autonomy/analysis to require sun pattern; removed redundant air-sun direction; 8-fixture GATE PASS. Superseded by v1 expansion above for coverage.
