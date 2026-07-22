# Profile E2E — Block Passport: `direction_mission`

**Status:** APPROVED for Profile v1 Freeze (2026-07-21)  
**Stage:** [PROFILE_E2E_RECONSTRUCTION.md](../PROFILE_E2E_RECONSTRUCTION.md)  
**Matrix:** [PROFILE_V1_BLOCK_FREEZE_MATRIX.md](./PROFILE_V1_BLOCK_FREEZE_MATRIX.md)  
**Template:** [PROFILE_E2E_BLOCK_PASSPORT_TEMPLATE.md](./PROFILE_E2E_BLOCK_PASSPORT_TEMPLATE.md)  
**Prompt:** `profile.patterns.v1` (field `life_mission`) · [PROFILE_E2E_PROMPT_REGISTRY.md](./PROFILE_E2E_PROMPT_REGISTRY.md) P3

> **Граница Freeze:** этот блок = только Direction **`life_mission`** (одна приземлённая строка).  
> Character helps/patterns · spheres · living_changes — не входят в PASS.  
> Генерация **разделяет gate** с `character_patterns` (один LLM step).

---

## 1. Passport table

| Field | Value |
|-------|--------|
| `block_id` | `direction_mission` |
| `purpose` | Дать одно **живое направление** — к чему человек тянется в практике, из накопленных дней |
| `user_question` | Куда мне двигаться / во что вкладываться? |
| `allowed_sources` | living.summary · living.signals · signal_profile · insights |
| `min_source_depth` | `profile_plus_checkins` (или `longitudinal_profile`) |
| `forbidden_sources` | birth-only sun-sign mission; taxonomy lifeTheme as fact; Today agenda; kitchen meta |
| `insufficient_when` | same as patterns — depth ∈ {`birth_data_only`, `onboarding_answers`}; living empty |
| `generation_required` | **yes** — only when patterns gate open |
| `generation_gate` | `patterns_generation_allowed(pack)` — no separate LLM step |
| `allowed_claims` | One grounded direction line from living evidence; wording may vary |
| `forbidden_claims` | Generic destiny slogans; inventing when gate closed; kitchen/system voice |
| `prompt_id` | `profile.patterns.v1` |
| `expected_response` | `life_mission` string ≥12 chars when gate open |
| `acceptance_criteria` | Gate open → living-grounded mission; gate closed → no LLM → null/empty → UI omits |
| `on_reject` | omit mission; do not invent from taxonomy; do not block identity/spheres |
| `snapshot_fields` | `profile_contract_v1.life_mission` |
| `ui_surfaces` | Profile V2 Direction · mission text (`model.lifeMission` ← contract only) |
| `appear_when` | non-empty contract `life_mission` after gate+accept |
| `access_tier` | trial growth / sub depth — presence only with evidence |
| `kitchen` | source_depth, eligibility.patterns, raw attempts |

---

## 2. Eligibility

```text
patterns_generation_allowed → may_generate
  true  → profile.patterns.v1 → life_mission filled
  false → ran=false → life_mission empty → UI omit
```

---

## 3. Snapshot → API → UI

| Layer | Rule |
|-------|------|
| Snapshot / GET | `life_mission` string or empty/null |
| UI | Direction mission from **contract only** — no taxonomy `lifeTheme` mix-in |
| Forbidden | Show mission from birth taxonomy when contract empty |

---

## 4. Dual outcome

1. **Stable contract:** gate open → one living-grounded mission line.  
2. **Do not generate:** gate closed → empty → UI omit.

---

## 5. Freeze progress

| Check | Status |
|-------|--------|
| Passport approved | **PASS** |
| Eligibility = patterns gate | **PASS** A/C skip · B run |
| FE contract-only | **PASS** |
| Capture A omit / B show / C omit | **PASS** — [PROFILE_CAPTURE_DIRECTION_MISSION_FREEZE_ABC.md](./PROFILE_CAPTURE_DIRECTION_MISSION_FREEZE_ABC.md) |
| Overall | **PASS** |
