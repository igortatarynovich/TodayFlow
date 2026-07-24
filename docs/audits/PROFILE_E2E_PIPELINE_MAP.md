# Profile E2E — Pipeline Map (current reality)

**Stage:** [PROFILE_E2E_RECONSTRUCTION.md](../profile/PROFILE_E2E_RECONSTRUCTION.md)  
**Date:** 2026-07-21 · **Mode:** code truth, no assumptions

---

## 1. Happy path (registration → Profile UI)

```text
Registration / auth
    → POST /account/core-setup  OR  POST|PUT /account/astro-data*
        → save user_settings + astro_profiles + numerology facts
        → warm natal cache (optional)
        → CoreProfileService.build(publish_portrait=True)
            → compute person/astro/numerology/baseline (code)
            → profile_hash (SHA-1 of facts + prompt versions)
            → build_profile_portrait_v1()
                → rich: run_profile_disclosure_funnel_v0
                    identity → styles → patterns → spheres  (≤4 sync LLM)
                → economize: oneshot _PROFILE_SYS_RU
                → fail: forming shell (no invented portrait)
            → quality validate + living enrich
            → upsert core_profile_snapshots (user_id, profile_hash)
            → generation_logs (meta only — NOT full prompts/raw)
    → GET /account/core-profile
        → build() → build_cached_or_baseline()  **no LLM**
        → overlay living, profiles, attach natal_summary (read-time)
    → FE /profile
        → fetchCoreProfileCached + CUM + natal preview
        → buildProfileQuickMapViewModel(contract + taxonomy + natal)
        → ProfileV2SystemScreen (Identity / Character / Direction / Evidence / Sources)
```

### Publisher entry points

| Endpoint | File | Publishes portrait? |
|----------|------|---------------------|
| `POST /account/core-setup` | `api/account.py` | Yes |
| `POST/PUT /account/astro-data*` | `api/account.py` → `_astro_profile_save_response` | Yes (even label-only edits) |
| `POST /account/core-profile/refresh` | `api/account.py` | Yes explicit |
| `GET /account/core-profile` | `api/account.py` | **No** — cached/baseline |

Proof read path has no LLM: `tests/test_core_profile_read_path_no_llm_v1.py`.

---

## 2. Dual-mode CoreProfileService

| Mode | Trigger | LLM? | Code |
|------|---------|------|------|
| Publish | `publish_portrait=True` | Yes (funnel or oneshot) | `core_profile.py` `_publish_portrait` → `build_profile_portrait_v1` |
| Read | default `build()` / GET | No | `build_cached_or_baseline` |

---

## 3. Deterministic calculations (code, not model)

| Output | Source | Notes |
|--------|--------|-------|
| Sun sign / element / modality | birth date (+ ephemeris if full chart) | baseline seed inputs |
| Life path, expression, … | numerology from name/date | model must not invent numbers |
| `baseline.archetype_seed`, `element_focus`, `rhythm_style` | element × modality × life_path mapping | calc seed — not portrait claims |
| `profile_hash` | facts + `PROFILE_CONTRACT_PROMPT_VER` + funnel prompt versions | prompt bump → new hash row |
| `living` (summary / signal_profile) | deterministic templates + overlays | **not** in profile_hash; overlaid on read |
| `natal_summary` | attach-on-read from natal service | **not** persisted in snapshot payload |
| Natal chart positions/houses/aspects | natal preview API | separate from portrait LLM |

---

## 4. Portrait funnel (LLM)

| Step | prompt_id | Writes | Unique knowledge? (audit open) |
|------|-----------|--------|--------------------------------|
| 1 identity | `profile.identity.v1` | `identity_core`, `strengths[3]`, `growth_zones[3]` | Core thesis |
| 2 styles | `profile.styles.v1` | `relationship_style`, `money_style`, `decision_style` | Should add angles; risk of rewrite |
| 3 patterns | `profile.patterns.v1` | `recurring_patterns`, `living_changes`, `life_mission`, `helps` | **Canon:** no real patterns on birth_only — but prod still asks LLM |
| 4 spheres | `profile.spheres.v1` | `life_spheres` ×9 ×6 fields | Candidate for deterministic projection |

Shared user JSON each step: `person, astro, numerology, baseline, living, locale, profile_hash` (+ prior step outputs).

Frame contamination risk: every system prompt prepends `voice_block` + `profile_layers_block` from `prompts/common_v1.py`, including **Today day-structure** language («чего ждать → что делать → сферы сегодня») — wrong domain for static Profile.

---

## 5. Validation / gates (degradation point #3)

File: `profile_contract_quality_v1.py` + step validators in `profile_disclosure_funnel_v0.py`

Rejects / weakens:

- short fields / missing required counts  
- duplicate sentences  
- identity echoed into ≥3 sphere `how`  
- banned phrases («вселенная», «поток энергии», …)  
- fast/slow lexical contradiction identity vs decision  
- locale mismatch  
- JSON/schema fail → retry once per step; step1 fail → whole funnel fail → forming shell  

On failure: **forming/partial shell**, not a soft rewrite of good prose — can look like «empty/generic» if FE expects ready contract.

---

## 6. Snapshot payload (persisted)

```text
profile_version, generated_at, is_ready, missing_fields, profile_hash
person, astro, numerology, baseline, profiles
profile_contract_v1 { status, identity_core, strengths, growth_zones,
  relationship_style, money_style, decision_style,
  recurring_patterns, living_changes, life_mission, helps, life_spheres,
  generation_meta, … }
interpretation          ← legacy shim from contract
daily_interpretation    ← legacy shim (lenses)
living                  ← stored then overlaid on read
```

**Not in generation_logs today:** rendered system/user prompts, per-step raw responses. Only meta + normalized contract.  
→ Full forensic packs must come from eval runner or a new capture harness.

---

## 7. Alternate / legacy paths (inventory)

| Path | Risk |
|------|------|
| `LLM_QUALITY_MODE=economize` → `_PROFILE_SYS_RU` oneshot | Different quality/shape than funnel |
| Forming shell when LLM fails | Honest empty rich fields — UI must handle |
| FE `buildProfileQuickMapViewModel` merges contract + **taxonomy/zodiac knowledge** + CUM | Projection degradation if taxonomy overrides contract |
| FE hardcoded signature roles (removed in PR-4) | Was inventing meaning |
| Guest onboarding in localStorage not in Snapshot | Input degradation |
| `natal_summary` / natal editorial separate personality | Competing SoI |
| Morning / Guidance / orchestrator use baseline+legacy interpretation | Parallel personality ([consumption audit](./PROFILE_AS_SOURCE_CONSUMPTION_AUDIT.md)) |
| Latest-snapshot queries ignoring hash selection | Possible stale/wrong portrait |

---

## 8. Fingerprint gaps

`profile_hash` **excludes:** lat/lon, timezone, `time_unknown`, astro profile id, living signals.  
Includes: names, gender, birth date/time, location_name, sun_sign, life_path, expression, prompt versions.

Living changes do **not** auto-regen portrait until explicit publish/refresh.

Forming retry comment (300s) exists; **no autonomous retry job** — needs explicit publisher.

---

## 9. Degradation checklist (four points)

| # | Point | What to verify on a real pack |
|---|-------|-------------------------------|
| 1 | **Input** | onboarding, living, prior snapshot, natal facts actually in user JSON? |
| 2 | **Prompt** | day-voice frame on Profile; schema forcing short clichés; patterns allowed without living? |
| 3 | **Validation** | good raw rejected → forming fallback? |
| 4 | **Projection** | FE QuickMap / taxonomy / copy safety cutting specificity? |

---

## Next capture requirement

Production-faithful harness must:

1. Run **all 4** funnel steps (including spheres).  
2. Persist each: system, user, raw, parsed, validation errors.  
3. Persist final Snapshot + GET `/account/core-profile` + FE-visible strings.  
4. Record `source_depth` and missing fields.

Until then: use `evals/profile_quality` with documented incompleteness (see Sample Pack).
