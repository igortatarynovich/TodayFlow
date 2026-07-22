# character_helps Freeze — Case A/B/C capture proof

**Date:** 2026-07-21  
**Block passport:** [PROFILE_E2E_BLOCK_PASSPORT_CHARACTER_HELPS.md](./PROFILE_E2E_BLOCK_PASSPORT_CHARACTER_HELPS.md) **APPROVED**  
**Packs:** `backend/evals/profile_quality/runs/capture_20260721T181028Z/` (same scenarios as patterns Freeze)  
**Gate:** `patterns_generation_allowed` (shared step `profile.patterns.v1`)

| Alias | Scenario | Intent |
|-------|----------|--------|
| **A** | `patterns-freeze-A` | Birth-only — gate closed → helps omit |
| **B** | `patterns-freeze-B` | Longitudinal — gate open → helps show |
| **C** | `patterns-freeze-C` | Onboarding only — gate closed → helps omit |

---

## Eligibility

| Case | depth | patterns may/ran | Snapshot helps | UI `live.helps` |
|------|-------|------------------|----------------|-----------------|
| A | birth_data_only | false / false | `[]` | `[]` |
| B | profile_plus_checkins | true / true | 2 items | same 2 |
| C | onboarding_answers | false / false | `[]` | `[]` |

---

## Four proofs

| # | Check | A | B | C |
|---|-------|---|---|---|
| 1 | Eligibility before LLM | PASS skip | PASS run | PASS skip |
| 2 | Prompt / living grounding | n/a | helps from patterns step, living-themed | n/a |
| 3 | Contract | empty omit | 2 helps; snap = GET | empty omit |
| 4 | UI | no taxonomy invent | Character shows contract helps; no divergences | no invent |

---

## Defects fixed

| Class | Fix |
|-------|-----|
| `PROJECTION` | `buildStableHelps` / QuickMap `thriveAreas` = contract `helps` only |
| `UI_GATE` | Screen uses `live.helps` only — no `thriveAreas` fallback |
| `PROMPT` | helps must be living-grounded supports, not birth/taxonomy filler |
| capture | Character `visible_blocks` includes `live.helps`; invent divergence when `helps=[]` |

---

## Verdict

**`character_helps` Freeze Overall: PASS**
