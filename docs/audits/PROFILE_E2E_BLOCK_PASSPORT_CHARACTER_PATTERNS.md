# Profile E2E — Block Passport: `character_patterns`

**Status:** APPROVED for Profile v1 Freeze (2026-07-21)  
**Stage:** [PROFILE_E2E_RECONSTRUCTION.md](../PROFILE_E2E_RECONSTRUCTION.md)  
**Matrix:** [PROFILE_V1_BLOCK_FREEZE_MATRIX.md](./PROFILE_V1_BLOCK_FREEZE_MATRIX.md)  
**Template:** [PROFILE_E2E_BLOCK_PASSPORT_TEMPLATE.md](./PROFILE_E2E_BLOCK_PASSPORT_TEMPLATE.md)  
**Prompt:** `profile.patterns.v1` · [PROFILE_E2E_PROMPT_REGISTRY.md](./PROFILE_E2E_PROMPT_REGISTRY.md) P3

> **Граница Freeze:** этот блок = только **подтверждённые** `recurring_patterns[]`.  
> `life_mission` · Character `helps[]` · `living_changes` — отдельные поверхности (не входят в PASS этого блока).  
> Стабильность = смысл/схема/факты, не verbatim.

---

## 1. Passport table

| Field | Value |
|-------|--------|
| `block_id` | `character_patterns` |
| `purpose` | Показать **подтверждённые** повторяющиеся закономерности поведения из накопленных дней |
| `user_question` | Что у меня повторяется в жизни / днях? |
| `allowed_sources` | living.summary · living.signals · signal_profile · insights · check-in notes (as evidence for patterns) |
| `min_source_depth` | `profile_plus_checkins` (или `longitudinal_profile`) |
| `forbidden_sources` | birth-only natal as sole evidence; Today day agenda; inventing repeats from sun-sign; taxonomy filler as confirmed patterns |
| `insufficient_when` | `source_depth` ∈ {`birth_data_only`, `onboarding_answers`} living empty / check-in days below depth gate |
| `generation_required` | **yes** — only when gate open |
| `generation_gate` | `patterns_generation_allowed(pack)` ≡ `classify_allowed_claims(depth).recurring_patterns` |
| `allowed_claims` | Recurring observations grounded in living evidence; language may vary |
| `forbidden_claims` | «Регулярно…» / «всегда…» from birth alone; day advice; kitchen/system meta; identity paraphrase as “pattern” |
| `prompt_id` | `profile.patterns.v1` |
| `expected_response` | `recurring_patterns[]` ≥1 meaningful item (≥8 chars). Other funnel fields may coexist but are **out of this block’s Freeze scope** |
| `acceptance_criteria` | Gate open → patterns grounded in living; gate closed → **no LLM**, Snapshot `recurring_patterns=[]`, UI omits block |
| `on_reject` | omit patterns (empty list); do not invent; do not block identity/styles/spheres |
| `snapshot_fields` | `profile_contract_v1.recurring_patterns` |
| `ui_surfaces` | Profile V2 Character · «Что повторяется» (`perceivedAs` ← contract patterns only) |
| `appear_when` | non-empty `recurring_patterns` after gate+accept |
| `access_tier` | trial growth / sub depth — presence only with evidence |
| `kitchen` | source_depth, eligibility, raw attempts, living fingerprint |

---

## 2. Eligibility (before prompt)

```text
patterns_generation_allowed:
  source_depth in (profile_plus_checkins, longitudinal_profile)
→ may_generate=true → call profile.patterns.v1
else → may_generate=false → ran=false → recurring_patterns=[] → UI omit
```

Capture: `block_eligibility.patterns.may_generate` vs `ran`.

---

## 3. Snapshot → API → UI

| Layer | Rule |
|-------|------|
| Snapshot / GET | `recurring_patterns` list or `[]` |
| UI | Character patterns list from contract only — **no taxonomy mix-in** when list empty or present |
| Forbidden | Show “confirmed repeats” from birth/taxonomy defaults |

---

## 4. Dual outcome

1. **Stable contract:** gate open → living-grounded patterns (wording may vary).  
2. **Do not generate:** gate closed → no LLM → empty list → UI omit.

---

## 5. Freeze progress

| Check | Status |
|-------|--------|
| Passport approved | **PASS** |
| Eligibility before LLM | **PASS** A/C skip · B run |
| Capture A omit / B show / C omit | **PASS** — [PROFILE_CAPTURE_CHARACTER_PATTERNS_FREEZE_ABC.md](./PROFILE_CAPTURE_CHARACTER_PATTERNS_FREEZE_ABC.md) |
| FE contract-only patterns | **PASS** (`perceivedAs` = contract only) |
| Quality must not invent when omitted | **PASS** A/C `perceivedAs=[]` |
| Overall | **PASS** |
