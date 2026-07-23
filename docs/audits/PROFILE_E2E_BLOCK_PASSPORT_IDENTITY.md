# Profile E2E — Block Passport: `identity`

**Status:** APPROVED for Profile v1 Freeze (2026-07-21)  
**Stage:** [PROFILE_E2E_RECONSTRUCTION.md](../PROFILE_E2E_RECONSTRUCTION.md)  
**Matrix:** [PROFILE_V1_BLOCK_FREEZE_MATRIX.md](./PROFILE_V1_BLOCK_FREEZE_MATRIX.md)  
**Template:** [PROFILE_E2E_BLOCK_PASSPORT_TEMPLATE.md](./PROFILE_E2E_BLOCK_PASSPORT_TEMPLATE.md)  
**Prompt:** `profile.identity.v1` · [PROFILE_E2E_PROMPT_REGISTRY.md](./PROFILE_E2E_PROMPT_REGISTRY.md) P1

> Generation unit for UI: `hero_quote` · `character_strengthens` · `character_drains`.  
> Stability = meaning / schema / facts — not verbatim text.

---

## 1. Passport table

| Field | Value |
|-------|--------|
| `block_id` | `identity` |
| `purpose` | Дать человеку устойчивое ядро «кто я» и опоры/зоны роста — без дневной повестки |
| `user_question` | Кто я в жизни? Что меня усиливает? Что меня истощает? |
| `allowed_sources` | person · astro (signs/elements as facts) · numerology numbers · baseline archetype_seed · living summary **только как мягкий фон, не как confirmed patterns** |
| `min_source_depth` | `birth_data_only` при наличии `birth_date` + usable sun/baseline |
| `forbidden_sources` | Today day chain · CUM day themes · raw check-in lists as «patterns» · taxonomy slots as substitute for LLM when contract exists |
| `insufficient_when` | нет `birth_date` / нет минимальных astro+baseline фактов для портрета → step **не** вызывается; UI forming / birth CTA |
| `generation_required` | `yes` for `recognition_line`, `identity_core`, `strengths[3]`, `growth_zones[3]` |
| `generation_gate` | `identity_generation_allowed(pack)` — birth_date + (sun_sign or baseline seed). **До** промпта |
| `allowed_claims` | Кто человек в жизни; 3 опоры; 3 зоны напряжения/роста. Языковая вариативность OK |
| `forbidden_claims` | Паспорт знака («вы Овен, поэтому…»); советы «сегодня»; подтверждённые recurring patterns; гарантии; мета про ИИ/систему; пустые формулы |
| `prompt_id` | `profile.identity.v1` |
| `expected_response` | `profile_funnel_identity_v0`: `recognition_line` ≤120 (no day/advice/archetype name); `identity_core` ≥20 chars; `strengths`≥3; `growth_zones`≥3 |
| `acceptance_criteria` | `_identity_ok` + Voice §0 (человек, не система) + не day agenda + не sun-sign cliché as sole content |
| `on_reject` | retry 1 → funnel fail → forming shell; **не** подставлять taxonomy как «готовый портрет» |
| `snapshot_fields` | `recognition_line`, `identity_core`, `strengths`, `growth_zones` (внутри `profile_contract_v1`) |
| `ui_surfaces` | Hero quote · Character strengthens · Character drains · (identitySummary feed) |
| `appear_when` | contract `ready`/`partial` with non-empty `identity_core`; иначе forming / omit quote |
| `access_tier` | trial / free (static who-you-are) |
| `kitchen` | prompt versions · raw · validation · fingerprint · capture attempts |

---

## 2. Eligibility (before prompt)

```text
identity_generation_allowed:
  birth_date present
  AND (sun_sign OR baseline.archetype_seed / equivalent)
→ may_generate=true → call profile.identity.v1
else → may_generate=false → ran=false → no LLM → forming + birth CTA
```

Capture: `block_eligibility.identity.may_generate` vs `ran`.

---

## 3. Prompt contract (stable meaning)

| Must | Must not |
|------|----------|
| Who in life (2–3 sentences) | Day expect/do/spheres-today chain |
| 3 distinct strengths | Verbatim identity paste into other steps (other passports) |
| 3 growth zones (honest tension) | Sign passport as the whole answer |
| Ground in allowed inputs | Invent longitudinal patterns |

Shared voice for Profile steps **must not** include Today day-meaning chain (defect class `PROMPT` if present).

---

## 4. Snapshot → API → UI

| Field | API | UI |
|-------|-----|-----|
| `identity_core` | GET core-profile contract | Hero quote body (`buildProfileHeroQuote` / identitySummary) |
| `strengths` | same | Character «Усиливает» — **contract-only** when present (no taxonomy mix-in) |
| `growth_zones` | same | Character «Истощает» — **contract-only** when present |

Dual-source FE mix (`allowBaseMix` taxonomy into strengthens/drains) = `PROJECTION` defect — forbidden for this block when contract lists exist.

---

## 5. Dual outcome

1. **Stable contract:** gate open → schema + meaning acceptance pass (wording may vary).  
2. **Do not generate:** gate closed → no LLM → no fake identity cards from taxonomy.

---

## 6. Freeze progress (`identity`)

| Check | Status |
|-------|--------|
| Passport approved | **PASS** |
| Eligibility before LLM | **PASS** (`identity_generation_allowed` + skip path) |
| Prompt without day chain | **PASS** (`profile_voice_block`) |
| Snap→API→UI contract-only | **PASS** (QuickMap + Case A visible_blocks) |
| Capture 4 proofs | **PASS** — [PROFILE_CAPTURE_IDENTITY_FREEZE_A.md](./PROFILE_CAPTURE_IDENTITY_FREEZE_A.md) |
| Overall block | **PASS** |
