# Day Scenario Eval Baseline C3.5.1

**Eval version:** `c35.1`  
**Pack score:** `0.932` · mean cell `0.993`  
**Pass:** `True` (pack threshold `0.75`)  
**Cells:** `616` · days `28` · profiles `11` · locales `['en', 'ru']`

## Thresholds (PROVISIONAL)

- reject `< 0.6`
- review `0.6`–`0.79`
- pass `≥ 0.8`
- note: PROVISIONAL — calibrate after golden-set labeling (C3.5c)

## Aggregate axes

- `chorus_coherence`: `1.0`
- `conflict_recognizability`: `1.0`
- `day_closure_quality`: `1.0`
- `formulation_repeatability`: `0.508`
- `no_parallel_forecasts`: `1.0`
- `recommendation_provenance`: `0.973`
- `scene_concreteness`: `0.974`
- `user_differentiation`: `1.0`

## By locale

- `en`: `0.996`
- `ru`: `0.989`

## By profile

- `act_first`: `0.996`
- `analyze_first`: `0.996`
- `autonomy_oriented`: `0.996`
- `birth_date_only`: `0.996`
- `demand_clarity`: `0.996`
- `incomplete_evidence`: `0.996`
- `no_birth_time`: `0.996`
- `no_profile`: `0.996`
- `over_responsible`: `0.954`
- `rejection_sensitive`: `0.996`
- `smooth_conflict`: `0.996`

## By day_type

- `astro_loud`: `0.996`
- `boundary_pressure`: `0.996`
- `calm`: `0.996`
- `card_shift`: `0.996`
- `clarity_vs_smooth`: `0.996`
- `client_now`: `0.996`
- `competing_drivers`: `0.996`
- `draft_send`: `0.996`
- `evening_checkin`: `0.996`
- `family_minute`: `0.996`
- `high_evidence`: `0.996`
- `honest_general_better`: `0.996`
- `insufficient_data`: `0.996`
- `low_evidence`: `0.996`
- `mixed_signals`: `0.988`
- `moon_sign_change`: `0.988`
- `morning_email`: `0.988`
- `number_shift`: `0.988`
- `quiet_sky`: `0.988`
- `recovery_day`: `0.988`
- `relationship_ask`: `0.988`
- `single_driver`: `0.996`
- `standup_extra`: `0.988`
- `station_tension`: `0.996`
- `strong_natal`: `0.988`
- `tempo_overload`: `0.988`
- `weak_personal`: `0.988`
- `work_deadline`: `0.988`

## Band counts (cell score)

- `pass`: `616`

## Defect code frequency

- `SCENE_ABSTRACT`: `396`
- `PROVENANCE_PROP_NOT_DERIVED`: `168`
- `PERSONALIZATION_SCENES_UNCHANGED`: `112`
- `PERSONALIZATION_DEPTH_OVERREACH`: `56`

## Worst 20 cells

1. `2026-07-15` · `over_responsible` · `ru` · day_type=`moon_sign_change` · score=`0.94` · contract=`0.976` · editorial=`0.868` · defects: `PERSONALIZATION_SCENES_UNCHANGED`, `PROVENANCE_PROP_NOT_DERIVED`, `SCENE_ABSTRACT`
2. `2026-07-17` · `over_responsible` · `ru` · day_type=`strong_natal` · score=`0.94` · contract=`0.976` · editorial=`0.868` · defects: `PERSONALIZATION_SCENES_UNCHANGED`, `PROVENANCE_PROP_NOT_DERIVED`, `SCENE_ABSTRACT`
3. `2026-07-18` · `over_responsible` · `ru` · day_type=`weak_personal` · score=`0.94` · contract=`0.976` · editorial=`0.868` · defects: `PERSONALIZATION_SCENES_UNCHANGED`, `PROVENANCE_PROP_NOT_DERIVED`, `SCENE_ABSTRACT`
4. `2026-07-22` · `over_responsible` · `ru` · day_type=`tempo_overload` · score=`0.94` · contract=`0.976` · editorial=`0.868` · defects: `PERSONALIZATION_SCENES_UNCHANGED`, `PROVENANCE_PROP_NOT_DERIVED`, `SCENE_ABSTRACT`
5. `2026-07-24` · `over_responsible` · `ru` · day_type=`work_deadline` · score=`0.94` · contract=`0.976` · editorial=`0.868` · defects: `PERSONALIZATION_SCENES_UNCHANGED`, `PROVENANCE_PROP_NOT_DERIVED`, `SCENE_ABSTRACT`
6. `2026-07-25` · `over_responsible` · `ru` · day_type=`relationship_ask` · score=`0.94` · contract=`0.976` · editorial=`0.868` · defects: `PERSONALIZATION_SCENES_UNCHANGED`, `PROVENANCE_PROP_NOT_DERIVED`, `SCENE_ABSTRACT`
7. `2026-07-29` · `over_responsible` · `ru` · day_type=`standup_extra` · score=`0.94` · contract=`0.976` · editorial=`0.868` · defects: `PERSONALIZATION_SCENES_UNCHANGED`, `PROVENANCE_PROP_NOT_DERIVED`, `SCENE_ABSTRACT`
8. `2026-07-31` · `over_responsible` · `ru` · day_type=`morning_email` · score=`0.94` · contract=`0.976` · editorial=`0.868` · defects: `PERSONALIZATION_SCENES_UNCHANGED`, `PROVENANCE_PROP_NOT_DERIVED`, `SCENE_ABSTRACT`
9. `2026-08-01` · `over_responsible` · `ru` · day_type=`mixed_signals` · score=`0.94` · contract=`0.976` · editorial=`0.868` · defects: `PERSONALIZATION_SCENES_UNCHANGED`, `PROVENANCE_PROP_NOT_DERIVED`, `SCENE_ABSTRACT`
10. `2026-08-05` · `over_responsible` · `ru` · day_type=`number_shift` · score=`0.94` · contract=`0.976` · editorial=`0.868` · defects: `PERSONALIZATION_SCENES_UNCHANGED`, `PROVENANCE_PROP_NOT_DERIVED`, `SCENE_ABSTRACT`
11. `2026-08-07` · `over_responsible` · `ru` · day_type=`quiet_sky` · score=`0.94` · contract=`0.976` · editorial=`0.868` · defects: `PERSONALIZATION_SCENES_UNCHANGED`, `PROVENANCE_PROP_NOT_DERIVED`, `SCENE_ABSTRACT`
12. `2026-08-08` · `over_responsible` · `ru` · day_type=`recovery_day` · score=`0.94` · contract=`0.976` · editorial=`0.868` · defects: `PERSONALIZATION_SCENES_UNCHANGED`, `PROVENANCE_PROP_NOT_DERIVED`, `SCENE_ABSTRACT`
13. `2026-07-12` · `over_responsible` · `ru` · day_type=`calm` · score=`0.958` · contract=`1.0` · editorial=`0.892` · defects: `PERSONALIZATION_SCENES_UNCHANGED`, `PROVENANCE_PROP_NOT_DERIVED`
14. `2026-07-12` · `over_responsible` · `en` · day_type=`calm` · score=`0.958` · contract=`1.0` · editorial=`0.892` · defects: `PERSONALIZATION_SCENES_UNCHANGED`, `PROVENANCE_PROP_NOT_DERIVED`
15. `2026-07-13` · `over_responsible` · `ru` · day_type=`single_driver` · score=`0.958` · contract=`1.0` · editorial=`0.892` · defects: `PERSONALIZATION_SCENES_UNCHANGED`, `PROVENANCE_PROP_NOT_DERIVED`
16. `2026-07-13` · `over_responsible` · `en` · day_type=`single_driver` · score=`0.958` · contract=`1.0` · editorial=`0.892` · defects: `PERSONALIZATION_SCENES_UNCHANGED`, `PROVENANCE_PROP_NOT_DERIVED`
17. `2026-07-14` · `over_responsible` · `ru` · day_type=`competing_drivers` · score=`0.958` · contract=`1.0` · editorial=`0.892` · defects: `PERSONALIZATION_SCENES_UNCHANGED`, `PROVENANCE_PROP_NOT_DERIVED`
18. `2026-07-14` · `over_responsible` · `en` · day_type=`competing_drivers` · score=`0.958` · contract=`1.0` · editorial=`0.892` · defects: `PERSONALIZATION_SCENES_UNCHANGED`, `PROVENANCE_PROP_NOT_DERIVED`
19. `2026-07-15` · `over_responsible` · `en` · day_type=`moon_sign_change` · score=`0.958` · contract=`1.0` · editorial=`0.892` · defects: `PERSONALIZATION_SCENES_UNCHANGED`, `PROVENANCE_PROP_NOT_DERIVED`
20. `2026-07-16` · `over_responsible` · `ru` · day_type=`station_tension` · score=`0.958` · contract=`1.0` · editorial=`0.892` · defects: `PERSONALIZATION_SCENES_UNCHANGED`, `PROVENANCE_PROP_NOT_DERIVED`

## Notes

- Synthetic matrix baseline — not live Nebius.
- Runtime LLM / today.py / Nebius paths untouched in C3.5.1.
- Next: golden-set labeling (C3.5c) → live shadow.
