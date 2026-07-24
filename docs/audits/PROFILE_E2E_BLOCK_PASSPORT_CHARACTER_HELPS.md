# Profile E2E — Block Passport: `character_helps`

**Status:** APPROVED for Profile v1 Freeze (2026-07-21)  
**Stage:** [PROFILE_E2E_RECONSTRUCTION.md](../profile/PROFILE_E2E_RECONSTRUCTION.md)  
**Matrix:** [PROFILE_V1_BLOCK_FREEZE_MATRIX.md](./PROFILE_V1_BLOCK_FREEZE_MATRIX.md)  
**Template:** [PROFILE_E2E_BLOCK_PASSPORT_TEMPLATE.md](./PROFILE_E2E_BLOCK_PASSPORT_TEMPLATE.md)  
**Prompt:** `profile.patterns.v1` (same step as patterns; field `helps`) · [PROFILE_E2E_PROMPT_REGISTRY.md](./PROFILE_E2E_PROMPT_REGISTRY.md) P3

> **Граница Freeze:** этот блок = только Character **`helps[]`** («Внутренние опоры»).  
> Sphere-row `helps` · `life_mission` · `recurring_patterns` — не входят в PASS этого блока.  
> Генерация **разделяет gate** с `character_patterns` (один LLM step). Не плодим отдельный engine.

---

## 1. Passport table

| Field | Value |
|-------|--------|
| `block_id` | `character_helps` |
| `purpose` | Показать **конкретные опоры**, которые уже работают у человека (из living) |
| `user_question` | На что мне реально опираться? |
| `allowed_sources` | living.summary · living.signals · signal_profile · insights · check-in notes |
| `min_source_depth` | `profile_plus_checkins` (или `longitudinal_profile`) |
| `forbidden_sources` | birth-only natal as sole evidence; taxonomy thriveAreas as “your supports”; Today agenda; kitchen meta |
| `insufficient_when` | same as patterns — depth ∈ {`birth_data_only`, `onboarding_answers`} living empty |
| `generation_required` | **yes** — only when patterns gate open (packaged in patterns step) |
| `generation_gate` | `patterns_generation_allowed(pack)` — **no separate LLM step** |
| `allowed_claims` | Concrete supports grounded in living evidence; wording may vary |
| `forbidden_claims` | Generic “rest / talk / trust the process”; birth-sign as support; inventing when gate closed |
| `prompt_id` | `profile.patterns.v1` |
| `expected_response` | `helps[]` ≥2 meaningful items (≥8 chars) when gate open |
| `acceptance_criteria` | Gate open → helps living-grounded; gate closed → no LLM → Snapshot `helps=[]` → UI omits |
| `on_reject` | omit helps; do not invent from taxonomy; do not block identity/spheres |
| `snapshot_fields` | `profile_contract_v1.helps` |
| `ui_surfaces` | Profile V2 Character · «Внутренние опоры» (`live.helps` ← contract only) |
| `appear_when` | non-empty contract `helps` after gate+accept |
| `access_tier` | trial growth / sub depth — presence only with evidence |
| `kitchen` | source_depth, eligibility.patterns, raw attempts |

---

## 2. Eligibility (before prompt)

```text
patterns_generation_allowed → may_generate
  true  → call profile.patterns.v1 → helps filled with living supports
  false → ran=false → helps=[] → UI omit
```

No independent helps gate: packaging is explicit, not accidental.

---

## 3. Snapshot → API → UI

| Layer | Rule |
|-------|------|
| Snapshot / GET | `helps` list or `[]` |
| UI | Character helps from **contract only** — no `thriveAreas` / taxonomy mix-in or Screen fallback |
| Forbidden | Show “Внутренние опоры” from birth taxonomy when `helps=[]` |

---

## 4. Dual outcome

1. **Stable contract:** gate open → ≥2 living-grounded helps.  
2. **Do not generate:** gate closed → empty → UI omit.

---

## 5. Freeze progress

| Check | Status |
|-------|--------|
| Passport approved | **PASS** |
| Eligibility = patterns gate | **PASS** A/C skip · B run |
| FE contract-only (no taxonomy) | **PASS** |
| Capture A omit / B show / C omit | **PASS** — [PROFILE_CAPTURE_CHARACTER_HELPS_FREEZE_ABC.md](./PROFILE_CAPTURE_CHARACTER_HELPS_FREEZE_ABC.md) |
| Overall | **PASS** |
