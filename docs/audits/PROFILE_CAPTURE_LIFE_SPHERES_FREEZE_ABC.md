# life_spheres Freeze — Case A/B/C capture proof

**Date:** 2026-07-21  
**Block passport:** [PROFILE_E2E_BLOCK_PASSPORT_LIFE_SPHERES.md](./PROFILE_E2E_BLOCK_PASSPORT_LIFE_SPHERES.md) **APPROVED**  
**Prompt passport:** [PROFILE_E2E_BLOCK_PASSPORT_SPHERES_SYNTHESIS.md](./PROFILE_E2E_BLOCK_PASSPORT_SPHERES_SYNTHESIS.md)  
**Packs:** `backend/evals/profile_quality/runs/capture_20260721T161519Z/`  
**Harness:** `run_production_capture_v0.py --cases spheres-A,spheres-B,spheres-C`

| Alias | Scenario | Intent |
|-------|----------|--------|
| **A** | `spheres-freeze-A` | Full allowable natal (sun+personal planets), unknown time, no living |
| **B** | `spheres-freeze-B` | Limited natal (sun only), unknown time, no living |
| **C** | `spheres-freeze-C` | Gate closed — no `sun_sign` (identity may still run via life_path) |

---

## Eligibility

| Case | patterns may/ran | spheres may/ran | Result |
|------|------------------|-----------------|--------|
| A | false / false | **true / true** | PASS — spheres without patterns |
| B | false / false | **true / true** | PASS — sun-only foundations enough for slice |
| C | false / false | **false / false** | PASS — closed gate, 0 sphere LLM attempts |

Missing-data (C): identity still published; `life_spheres={}`; UI `life_spheres` lines = 0.  
Patterns/history are **not** a hidden dependency (A/B: patterns skipped, spheres ran).

---

## Four proofs (per open-gate case)

| # | Check | A | B | C |
|---|-------|---|---|---|
| 1 | Eligibility before LLM | PASS | PASS | PASS (closed) |
| 2 | Prompt / cues path | synthesis ×3 ok | 3 ok (1 retry) | n/a skipped |
| 3 | Contract acceptance | love/money/decisions; distinct how (Jaccard ≤0.04); no day/kitchen/astro/longitudinal leaks | same | empty omit |
| 4 | Snapshot payload → GET → UI | equal spheres; `visible_blocks.life_spheres` 21 lines; needs present; no divergences | same | empty consistent |

Snapshot path in pack: `snapshot_written.payload.profile_contract_v1` (= GET).

---

## Contract quality (A/B published copy)

- love / money / decisions `how` pairwise Jaccard ≪ 0.55  
- no unsupported astro kitchen in user text  
- no day-language / kitchen terms / longitudinal markers  
- text about the person  
- wording variance OK (semantic stability)

---

## Defects fixed in this slice (proven)

| Class | Fix |
|-------|-----|
| `PROJECTION` / capture | FE harness omitted Direction spheres → include `buildProfileLifeSpheresFromProfileData` in `visible_blocks.life_spheres` |
| `VALIDATION` | ban day-language + kitchen terms in `validate_sphere_synthesis_v0`; map system leak class to `VALIDATION` |
| `INPUT` | capture scenarios pass `natal` into portrait pack |
| docs | one APPROVED block passport; synthesis = subordinate prompt passport |

No Context Engine / FactAtoms / new registries.

---

## Verdict

**`life_spheres` Freeze Overall: PASS**
