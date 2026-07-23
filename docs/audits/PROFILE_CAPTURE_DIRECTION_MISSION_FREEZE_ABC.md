# direction_mission Freeze — Case A/B/C capture proof

**Date:** 2026-07-21  
**Block passport:** [PROFILE_E2E_BLOCK_PASSPORT_DIRECTION_MISSION.md](./PROFILE_E2E_BLOCK_PASSPORT_DIRECTION_MISSION.md) **APPROVED**  
**Packs:** `backend/evals/profile_quality/runs/capture_20260721T181028Z/` (shared with patterns/helps)  
**Gate:** `patterns_generation_allowed` (shared step `profile.patterns.v1`)

| Alias | Scenario | Intent |
|-------|----------|--------|
| **A** | `patterns-freeze-A` | Birth-only — omit |
| **B** | `patterns-freeze-B` | Longitudinal — show |
| **C** | `patterns-freeze-C` | Onboarding only — omit |

---

## Eligibility

| Case | depth | patterns may/ran | Snapshot `life_mission` | UI `lifeMission` |
|------|-------|------------------|-------------------------|------------------|
| A | birth_data_only | false / false | empty | omit |
| B | profile_plus_checkins | true / true | 100 chars, living-grounded | same |
| C | onboarding_answers | false / false | empty | omit |

---

## Four proofs

| # | Check | A | B | C |
|---|-------|---|---|---|
| 1 | Eligibility before LLM | PASS skip | PASS run | PASS skip |
| 2 | Prompt / living grounding | n/a | mission from patterns step | n/a |
| 3 | Contract | empty omit | snap = GET | empty omit |
| 4 | UI | no taxonomy invent | Direction shows contract mission; no divergences | no invent |

---

## Defects fixed

| Class | Fix |
|-------|-----|
| `PROJECTION` | QuickMap `lifeMission` = contract `life_mission` only |
| `PROMPT` | mission must be living-grounded, not sun-sign destiny |
| capture | invent / rewrite divergences for mission |

---

## Verdict

**`direction_mission` Freeze Overall: PASS**
