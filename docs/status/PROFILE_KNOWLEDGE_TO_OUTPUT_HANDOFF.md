# Profile knowledge-to-output — next agent

**Date:** 2026-09-20  
**Branch:** `cursor/profile-knowledge-to-output`  
**Parked:** P1 library fill on `cursor/p1-self-compassion-loop-notes` @ `f48a438d`  
**Goal:** Carry one natal construction from calculated chart → IL → Character Engine → Profile slot without collapsing it into a sun-bucket template.

Not a new product canon. Not a new SoT. Not a 30-page audit. Not `affirmation.permission` / remaining P1 types.

---

## 0. Decision (locked)

P1 Library Fill **STOPPED**. Coverage stays **153 items, 20/42 P1 sourced, 5 P1 skipped**. P0 remains 26/26. Remaining P1 types wait on product demand (`PRACTICE_CONTENT_COVERAGE_V1`: type coverage *or skipped-type reassessment*). Do not delete items. Do not continue `affirmation.acceptance`.

Work sequence from here: **Profile knowledge-to-output → Today → Compatibility → Tarot → field cohort → launch ops.**

---

## 1. First 15 minutes

1. This file + tracker NOW (`PROFILE KNOWLEDGE-TO-OUTPUT`) + `PROFILE_EXPERIENCE_SCENARIO_V1` (CE is person SoT) + `ASTROLOGY_COMPOSITION_MODEL` / `CALC_IL_WIRE_V1` (IL is knowledge; not a pair catalog).
2. Stay on `cursor/profile-knowledge-to-output`. Do not resume P1 fill.
3. Run: `backend/.venv/bin/pytest tests/test_profile_knowledge_to_output_v1.py -q --tb=short --no-cov`
4. G0 stays deferred. Do not untrip `DATA/ops/llm_spend.json`.

**Pass bound:** invert the xfail — Mars × sign × house must appear in Character Engine Stage 1 claims, and two same-Sun charts must no longer share one Identity Core surface. Then project that distinction into `P1.recognition_line` / `P1.identity_core`. Stop when one construction survives to the visible Profile slot.

---

## 2. Four questions — answered from payloads (2026-09-20)

Two natal snapshots, **same Sun Virgo / Moon Taurus / ASC Gemini**. Only Mars differs: Cancer house 4 vs Libra house 7.

### 1. Is IL knowledge actually used in Profile generation?

**No.** `character_engine_*.py` does not import IL. IL wire runs at the library layer (`wire_calc_to_il`, catalog still `draft`). Live Profile consumption reads CE Identity Core + a 13-key editorial bank. Natal Decode Depth can attach IL-4; first-paint Profile does not.

### 2. Is specificity lost at each hop?

**Yes, at Stage 1.**

| Hop | Cancer H4 | Libra H7 |
|-----|-----------|----------|
| Calc | Mars Cancer / house 4 | Mars Libra / house 7 |
| IL-2/3 | `act · pursue · assert` × `close · indirect · holding` × `home · family · roots` | same *what* × `balancing · tactful · proportionate` × `partnership · one-to-one · contracts` |
| CE Stage 0 | `planet_sign:mars` value `{sign: cancer, house: 4}` | `{sign: libra, house: 7}` |
| CE Stage 1 | `analysis_before_action`, `anchor_through_earth_moon`, `presence_through_air_asc` | **identical** |
| Identity Core | `builds_through_analysis` | **identical** |
| Surface | «Ты строишь через анализ до шага — сначала понять устройство, потом выбрать.» | **identical** |

House occupancy is stored on the Stage 0 value blob and **never matched**. Stage 1 is a sun/moon/ASC element registry (~13 thesis keys).

### 3. Who writes meaning?

IL lemmas are composed deterministically (`meaning_source=il3_themes`, `llm_chose_meaning=None`). Character Engine Stage 2 is **LLM-first**; when LLM is down it fills from `_DETERMINISTIC_SURFACE_BY_IDENTITY` (13 Russian templates). Code does not score wording; it only checks claim_id provenance. LLM is asked to phrase a pre-chosen sun-bucket thesis, not to compose Mars × house.

### 4. Why would two people look different?

They look different **only if the sun-bucket (or moon/ASC element rule) differs**. Same Sun + different Mars/house → same Profile recognition line. That is the defect this train fixes.

---

## 3. Next code (do this, not a new doc)

1. Invert `test_il_mars_constructions_reach_stage1_claims` (currently `xfail`).
2. Stage 1 (or a thin adapter beside the v0 registry) must mint **IL-3 natal frames as evidence claims**. Do not add a planet_in_sign cookbook. Do not inject IL-4 English lemma glue as Russian identity prose. IL-2/3 = meaning; IL-4 = voice; omit if compose refuses.
3. Identity / consumption must not collapse those claims back to the 13-template bank before `P1.recognition_line`.
4. Architecture impact required when IL draft catalog is first read on first-paint Profile (today CALC_IL_WIRE says product surfaces ignore `draft`).
5. Tests: `tests/test_profile_knowledge_to_output_v1.py`. Do not reopen P1 fill tests unless coverage JSON is touched.

Canon already opened: `PROFILE_EXPERIENCE_SCENARIO_V1` · `CALC_IL_WIRE_V1` · `IL2_COMPOSITION_RULES_V1` · `IL3_INTERPRETATION_ENGINE_V1` · `CHARACTER_ENGINE_ARCHITECTURE_IMPACT_V1` D2.

---

## 4. Do not

- Continue P1 types (`affirmation.acceptance`, density, skipped reassessment) on this pass.
- Write a new Profile/CE/IL canon or a 30-page audit.
- Set catalog `active` as a side effect.
- Let the LLM choose Saturn □ Venus / Mars house.
- Invent Russian meaning when IL refuses — omit.
- Untrip billing. Merge/deploy only if asked.
- Start Today / Compatibility / Tarot until one natal construction reaches the Profile screen.
