# Identity Freeze — Case A capture proof

**Date:** 2026-07-21  
**Passport:** [PROFILE_E2E_BLOCK_PASSPORT_IDENTITY.md](./PROFILE_E2E_BLOCK_PASSPORT_IDENTITY.md)  
**Pack:** `backend/evals/profile_quality/runs/capture_20260721T160949Z/capture_pq-001_20260721T161052Z.json`  
**Harness:** `run_production_capture_v0.py --cases A`

## Four proofs

| # | Check | Result |
|---|-------|--------|
| 1 | Eligibility before LLM | `may_generate=true` · `ran=true` · reason birth+astro/baseline |
| 2 | Prompt matches passport | `profile.identity.v1` · **no** Today day-chain («чего ждать») · profile voice present |
| 3 | Response = contract | `_identity_ok` · `identity_core` + 3 strengths + 3 growth_zones |
| 4 | Same answer → UI | Snapshot identity fields = GET · `visible_blocks.identity` contains `identity_core` · all strengths/growth in `visible_blocks.character` · no dual-source taxonomy mix into those lists |

## Notes

- Case A is birth-only: patterns correctly `may_generate=false` · `ran=false` (out of scope for this passport).
- Capture pack may still list stale patterns schema invariants — patterns block debt, not identity.
- Node resolution in capture harness fixed (bare `node` no longer short-circuits before Cursor node path).

## Verdict

**`identity` Freeze Overall: PASS** (Case A production-faithful).  
Case B not required for birth-floor identity gate; optional regression later.
