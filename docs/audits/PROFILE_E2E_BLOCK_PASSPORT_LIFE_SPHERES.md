# Profile E2E — Block Passport: `life_spheres`

**Status:** APPROVED for Profile v1 Freeze (2026-07-21)  
**Stage:** [PROFILE_E2E_RECONSTRUCTION.md](../profile/PROFILE_E2E_RECONSTRUCTION.md)  
**Matrix:** [PROFILE_V1_BLOCK_FREEZE_MATRIX.md](./PROFILE_V1_BLOCK_FREEZE_MATRIX.md)  
**Template:** [PROFILE_E2E_BLOCK_PASSPORT_TEMPLATE.md](./PROFILE_E2E_BLOCK_PASSPORT_TEMPLATE.md)  
**Prompt passport (subordinate):** [PROFILE_E2E_BLOCK_PASSPORT_SPHERES_SYNTHESIS.md](./PROFILE_E2E_BLOCK_PASSPORT_SPHERES_SYNTHESIS.md)  
**Cue / kitchen ruleset (not user-copy SoT):** [PROFILE_LIFE_SPHERES_DETERMINISTIC_PROJECTOR_V0.md](./PROFILE_LIFE_SPHERES_DETERMINISTIC_PROJECTOR_V0.md)

> **Один канон блока.** Этот файл = block passport.  
> Synthesis passport = только prompt/field contract для LLM.  
> Production Freeze scope = **`love` · `money` · `decisions`** (не все 9).  
> Patterns / living **не** открывают и не закрывают блок.

---

## 1. Passport table

| Field | Value |
|-------|--------|
| `block_id` | `life_spheres` |
| `purpose` | Показать, как базовые особенности человека **проявляются** в ключевых сферах — прикладная карта без требования личной истории |
| `user_question` | Как базовые особенности проявляются в близости / деньгах / решениях? |
| `allowed_sources` | birth foundations (signs/planets available); optional houses **only if** birth time+place allow; `identity_core` · strengths · growth_zones; `relationship_style` · `money_style` · `decision_style`; prepared `sphere_cues` / optional `house_cues` |
| `min_source_depth` | `birth_data_only` when §2 gate holds. Longitudinal **не** повышает eligibility |
| `forbidden_sources` | patterns success as precondition; living as eligibility; Today / CUM day; FE DEFAULTS/catalog filler; raw planet=sign as sole LLM homework; projector phrase tables as published copy |
| `insufficient_when` | нет birth foundation + sun_sign; нет identity_core (≥20); нет ни одного usable style (≥12) для slice; пустые `sphere_cues` для сферы → omit **этой** сферы |
| `generation_required` | **yes** — `profile.spheres.synthesis.v1` per eligible sphere |
| `generation_gate` | `spheres_projection_allowed(foundations)` **and** non-empty cues per sphere. **Does not read** `patterns_generation_allowed` |
| `allowed_claims` | Sphere-specific how/need/risk/turns_on/turns_off/helps grounded in cues+style+identity; language may vary |
| `forbidden_claims` | longitudinal «всегда/регулярно» without living; planet/sign/house names in user text; day agenda; kitchen terms; identity/style paste; same meaning across love/money/decisions `how` |
| `prompt_id` | `profile.spheres.synthesis.v1` (legacy `profile.spheres.v1` = not authority) |
| `expected_response` | Partial `life_spheres`: up to 3 spheres × 6 string fields (synthesis passport §2) |
| `acceptance_criteria` | §4 + synthesis validator + distinctness across spheres |
| `on_reject` | omit failing sphere; never projector boilerplate; do not block identity/styles/patterns |
| `snapshot_fields` | `profile_contract_v1.life_spheres.{love,money,decisions}` (+ kitchen meta in generation/capture) |
| `ui_surfaces` | Profile V2 Direction · sphere cards (`buildProfileLifeSpheresFromProfileData` — contract-only) |
| `appear_when` | ≥1 valid sphere in Snapshot; **patterns not required** |
| `access_tier` | trial/free presence when gate holds |
| `kitchen` | cue ids, trait/planet/sign used to build cues, fingerprints, synthesis_version, omit reasons |

---

## 2. Eligibility (before any sphere LLM call)

```text
spheres_projection_allowed(foundations):
  (birth_date OR sun_sign) AND sun_sign
  AND identity_core length ≥ 20
  AND ≥1 of relationship_style / money_style / decision_style length ≥ 12

Per sphere:
  gate open AND non-empty sphere_cues → may call synthesis
  else → omit sphere (ran=false for that sphere / no fill)
```

| Case | Patterns / living | Expected gate |
|------|-------------------|---------------|
| Birth-only + identity/styles | absent | **open** if sun+identity+styles |
| Unknown birth time | absent | **open** (sign/planet cues); no house claims |
| No sun / no identity / no styles | any | **closed** — no LLM |
| Patterns skipped | n/a | **irrelevant** — must not close spheres |

Capture: `block_eligibility.spheres.may_generate` vs `ran`.

---

## 3. Pipeline (production)

```text
identity + styles ready
  → build_sphere_foundations_v0
  → spheres_projection_allowed?
       no  → life_spheres={} · ran=false
       yes → per sphere (love/money/decisions):
              cues → profile.spheres.synthesis.v1 → validate
              fail → omit sphere (no projector copy)
  → Snapshot.life_spheres (partial OK)
  → GET same fields
  → UI Direction cards from contract only
```

Deterministic owns: eligibility · cue selection · house gate · validation.  
LLM owns: user-facing six fields.  
Projector tables: A/B / cue kitchen only — **not** published copy.

---

## 4. Acceptance (Freeze)

1. Schema: 6 fields per published sphere; length bounds (synthesis validator).  
2. Distinctness: love/money/decisions `how` not near-duplicates; fields not identity/style paste.  
3. No unsupported claims (astro labels, longitudinal markers, day-language, kitchen terms).  
4. Voice: about the person; no system status.  
5. Stability = meaning/structure/facts — not verbatim text.  
6. Dual outcome only: stable sphere **or** omit.

---

## 5. Snapshot → API → UI

| Layer | Field |
|-------|--------|
| Snapshot / GET | `profile_contract_v1.life_spheres[id].{how,need,risk,turns_on,turns_off,helps}` |
| UI | Direction `<details>` cards — title + need line + expanded how/need/risk/turnsOn/turnsOff/helps |
| Forbidden UI path | FE chart/DEFAULTS fill when contract empty |

UI may add chrome frame on `how` («В отношениях …») — meaning must still match Snapshot field.

---

## 6. Dual outcome

1. **Stable contract** for each published sphere.  
2. **Do not generate / omit** when gate closed or cues/validation fail.

Forbidden: invent 9×6; require patterns; silent projector as personal fact.

---

## 7. Freeze progress

| Check | Status |
|-------|--------|
| Passport approved (this file) | **PASS** |
| Prompt passport aligned | synthesis doc = subordinate |
| Eligibility independent of patterns | **PASS** (A/B patterns skipped, spheres ran) |
| Capture A/B/C 4 proofs | **PASS** — [PROFILE_CAPTURE_LIFE_SPHERES_FREEZE_ABC.md](./PROFILE_CAPTURE_LIFE_SPHERES_FREEZE_ABC.md) |
| Overall | **PASS** |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-21 | Draft: natal-presence · independent of patterns |
| 2026-07-21 | **APPROVED Freeze canon** — synthesis = content authority; scope love/money/decisions; contradictions with deterministic-final-copy removed |
