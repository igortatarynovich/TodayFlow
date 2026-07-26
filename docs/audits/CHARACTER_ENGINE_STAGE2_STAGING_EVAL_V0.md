# Character Engine Stage 2 — Staging Evaluation v0

**Date:** 2026-07-26  
**Status:** **GATE PASS** (after prompt v1.1.0 calibration)  
**CE baseline:** `5eb61c6`  
**Prompt:** `profile.character_engine.stage2.v1` **v1.1.0**  
**Fixtures:** same 16 packs as Stage 0–1 staging (`character_engine_stage01_staging_profiles_v0.json`)  
**Runner:** `python -m todayflow_backend.services.character_engine_stage2_staging_eval_v0`

**SoT:** unchanged — diagnostics only; no Profile publish / no `PUBLISH_READY`.

## Intent

Calibrate Identity Core **before** more live/prod testing: structure/provenance gates + RU voice + exit-criterion notes for humans.

## Calibration applied (v1.1.0)

1. **Voice:** `surface_text` — «ты» или 3-е лицо; запрет «вы/Вы».  
2. **Selection preference (prompt-only):** autonomy/tension/sun-mechanism/emotional → presence → mars-drive.  
3. **Retry once** on empty LLM text (timeouts were collapsing packs to insufficient).  
4. Staging gate `no_formal_vy_surface`.

## Results (locale=ru, post-calibration)

| Metric | Value |
|--------|-------|
| Packs | 16 |
| Grounded | **15** |
| Insufficient | **1** (Leo `date_only` negative — correct) |
| Grounded share | 0.938 |
| Contract errors on grounded | 0 |
| Formal «Вы» | 0 |
| Cyrillic surfaces | 15/15 |

### Identity thesis frequency (grounded)

| thesis | count |
|--------|------:|
| builds_through_analysis | 5 |
| builds_through_air_mind | 2 |
| builds_through_earth_stability | 2 |
| builds_through_freedom_vs_stability | 2 |
| builds_through_water_care | 2 |
| builds_through_autonomy | 1 |
| builds_through_earth_anchor | 1 |

No identity thesis >50% of grounded.

### Sample loglines (truncated)

- Aquarius full: «Ты — человек, который строит свой мир, удерживая живое напряжение между жаждой свободы…» (`freedom_vs_stability`)
- Gemini: «Ты — человек, который прокладывает путь через ментальную карту мира…» (`air_mind`)
- Taurus: «Ты — человек, который строит мир через ощутимую, надёжную основу…» (`earth_stability`)
- Fire Sag: «Человек, который прокладывает свой путь с огнём в сердце…» (`autonomy`)

## Gate checklist

| Gate | Result |
|------|--------|
| Known statuses only | PASS |
| Empty Stage 1 → insufficient | PASS |
| Leo negative insufficient | PASS |
| No contract errors on grounded | PASS |
| Surface present + refs resolve | PASS |
| Thesis map complete | PASS |
| No systemish / no «Вы» | PASS |
| RU cyrillic | PASS |
| Identity thesis not majority | PASS |
| ≥50% of nonempty Stage1 grounded | PASS |

## Exit criterion (canon §1.4) — human probe

Ask on grounded packs: *«This is a manifestation of the Identity Core because…»*  
Staging notes store `surface_text` + `selection_rationale` for review.  
**Not a code quality scorer.** Owner still reviews feel before Stage 3.

## Residual

- `builds_through_analysis` densest (5/15) — watch if Stage 1 analysis share climbs further.  
- Third-person «Человек…» mixed with «Ты — человек…» — both allowed; optional later unify.  
- LLM latency/timeouts still possible; one retry mitigates staging flakiness.

## Next (order)

1. Owner voice/exit skim of grounded loglines (optional).  
2. Live retest on prod shadow with Stage 0–1 v1 + Stage 2 prompt 1.1.0.  
3. Stage 3 only after exit criterion feels natural on most packs.  
4. No `PUBLISH_READY`.
