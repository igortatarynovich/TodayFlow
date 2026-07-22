# character_patterns Freeze — Case A/B/C capture proof

**Date:** 2026-07-21  
**Block passport:** [PROFILE_E2E_BLOCK_PASSPORT_CHARACTER_PATTERNS.md](./PROFILE_E2E_BLOCK_PASSPORT_CHARACTER_PATTERNS.md) **APPROVED**  
**Packs:** `backend/evals/profile_quality/runs/capture_20260721T181028Z/`  
**Harness:** `run_production_capture_v0.py --cases patterns-A,patterns-B,patterns-C`

| Alias | Scenario | Intent |
|-------|----------|--------|
| **A** | `patterns-freeze-A` | Birth-only — gate closed |
| **B** | `patterns-freeze-B` | Longitudinal living — gate open |
| **C** | `patterns-freeze-C` | Onboarding only — gate closed |

---

## Eligibility (birth vs longitudinal boundary)

| Case | depth | may_generate | ran | Snapshot patterns | UI perceivedAs |
|------|-------|--------------|-----|-------------------|----------------|
| A | birth_data_only | false | false | `[]` | `[]` |
| B | profile_plus_checkins | true | true | 2 living-grounded items | same 2 |
| C | onboarding_answers | false | false | `[]` | `[]` |

---

## Four proofs

| # | Check | A | B | C |
|---|-------|---|---|---|
| 1 | Eligibility before LLM | PASS skip | PASS run | PASS skip |
| 2 | Prompt / living grounding | n/a | 1 attempt ok; patterns match living themes (postpone talks / restore via order) | n/a |
| 3 | Contract | empty omit | 2 patterns; snap payload = GET | empty omit |
| 4 | UI | no invent from taxonomy | Character list shows contract patterns; no divergences | no invent |

---

## Defects fixed in this slice

| Class | Fix |
|-------|-----|
| `PROJECTION` | FE `perceivedAs` = contract `recurring_patterns` only (no taxonomy mix-in) |
| `PROMPT` | patterns system requires living-grounded confirmed repeats |
| `GENERATION_GATE` | capture marks `ran` on success; stop seeding stale birth-only schema defects when skip is correct |
| capture | Character `visible_blocks` includes `perceivedAs` |

---

## Verdict

**`character_patterns` Freeze Overall: PASS**
