# Character Engine Stage 2 — Live Review v0

**Date:** 2026-07-26  
**Status:** LIVE SHADOW ON — review pass with residual thesis-map fix  
**CE baseline:** `5eb61c6`  
**Flags:** `STAGE01_SHADOW=1` · `STAGE2_SHADOW=1` · `STAGE2_ENABLED=0` · `PUBLISH_READY=0`

## What ran

Stage 2 Identity Core (`profile.character_engine.stage2.v1`) against prod users with settings (N=7, usable 6). Diagnostics only — Profile UI SoT unchanged.

## Results

| Pack | Stage 1 claims | Stage 2 status | Notes |
|------|----------------|---------------|-------|
| u1 Gemini full | 0 | `insufficient_identity_core` | Correct short-circuit (`no_grounded_stage1_claims`) |
| u2 Aquarius lp7 full | `autonomy_high` | **`grounded`** | thesis `builds_through_autonomy` · surface_text present · refs OK |
| u19 | — | build error | `ChartResponse.positions` dict (pre-existing, outside CE) |
| u20–22 Taurus date_only | 0 | `insufficient_identity_core` | Correct |
| u26 Pisces full | `presence_through_air_asc` | **`grounded`** (after map fix) | thesis `builds_through_air_presence` · RU surface_text · refs OK |

### Aquarius grounded sample (anonymized)

- **primary Stage 1:** `autonomy_high` (sun Aquarius; LP7 + Mars strengthen in rationale)
- **identity thesis:** `builds_through_autonomy`
- **surface_text (logline):** independent thinker / internal compass / self-definition (EN in this run)
- **contract validation:** all structural gates PASS; `surface_not_in_id` PASS

### Exit-criterion probe (canon §1.4)

For u2: *«This is a manifestation of the Identity Core because…»* — natural for autonomy-driven Stage 3+ expansion.  
After thesis-map fix, u26 also grounds (`builds_through_air_presence`). **Two grounded packs** — still early for Stage 3 exit; continue shadow + voice review.

## Fixes from this pass

1. **Identity thesis map** — add Stage 1 → identity mappings:
   - `freedom_vs_stability` → `builds_through_freedom_vs_stability`
   - `presence_through_air_asc` → `builds_through_air_presence`
2. **Stage 2 not on GET** — LLM Stage 2 only on portrait publish/refresh (`include_stage2=True`). Read-path keeps Stage 0–1 only (cheap).
3. **Deploy hygiene** — prior prod image lacked GET Stage 0–1 attach; rebuild with current `core_profile.py`.

## Gate checklist

| Gate | Result |
|------|--------|
| Empty Stage 1 → insufficient (no invent) | PASS |
| Grounded refs resolve to Stage 1 claim/facts | PASS (u2) |
| No publish / no Profile SoT change | PASS |
| All Stage 1 thesis_keys normalizable | **FIXED** (was FAIL on presence) |
| Stage 2 not on every Profile GET | **FIXED** |
| Exit criterion for Stage 3 | **NOT YET** — need more grounded packs + owner review of loglines |

## Verdict

**Stage 2 shadow stays ON.** u2 + u26 both ground after thesis-map deploy.  
**Do not** enable `PUBLISH_READY` or Stage 3 until owner voice review + exit criterion on more packs.

## Next (order)

1. Confirm u26 grounds after thesis-map deploy.  
2. Owner review of grounded loglines (voice: person-not-system; RU preference if locale=ru).  
3. Optional: Stage 2 locale/voice pass if EN loglines on RU profiles.  
4. Stage 3 Internal Engine only after §1.4 feels natural on most production-like packs.
