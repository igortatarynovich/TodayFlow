# Case A/B — spheres synthesis wire proof

**Date:** 2026-07-21  
**Commit stage:** production funnel uses `profile.spheres.synthesis.v1`  
**Harness:** `backend/evals/profile_quality/run_production_capture_v0.py --cases A,B`  
**Packs:** `backend/evals/profile_quality/runs/capture_synthesis_ab_20260721T153457Z/`

## Chain proven

```text
ready facts (sun + styles + identity)
  → sphere_cues (sun.aries / sun.taurus trait cues when full natal not in scenario)
  → profile.spheres.synthesis.v1
  → validate_sphere_synthesis_v0
  → Snapshot.profile_contract_v1.life_spheres (partial)
  → GET body retains same spheres
  → FE contract-only projection would emit 3 spheres (all 6 fields)
```

| Case | patterns | spheres ran | source | spheres in Snapshot | projector fallback |
|------|----------|-------------|--------|---------------------|--------------------|
| A `pq-001` birth-only | `ran=false` | `ran=true` | `spheres_synthesis_v1` | love · money · decisions | **none** |
| B `pq-007` longitudinal | `ran=true` | `ran=true` | `spheres_synthesis_v1` | love · money · decisions | **none** |

## Notes

1. Scenario packs still ship **sun_sign only** → cues fall back to sun traits (not Venus/Jupiter full set). Production can lift fuller natal via `natal` / `natal_summary.personal_planets` into foundations (already wired).  
2. FE harness in this environment failed on `node_not_found` for QuickMap script; contract-level partial map is complete (3×6). Manual FE check: `buildSpheresFromContractOnly` keeps partial.  
3. Fail path unit-tested: synthesis validation fail ⇒ omit sphere, never `deterministic_projector` copy.

## SoT

User-facing sphere copy authority: **synthesis**.  
Projector: A/B baseline / trait-cue kitchen only.  
Legacy `profile.spheres.v1`: not called.
