# Character Engine Stage 0–1 — Live Review v0

**Date:** 2026-07-25  
**Status:** REVIEWED (prod packs) — **conditional GO → Stage 2 shadow**  
**CE baseline:** `5eb61c6`  
**Server flags at review:** `STAGE01_SHADOW=1` · Stage 2 off · `PUBLISH_READY=0`

## Sample

| Metric | Value |
|--------|-------|
| Users with settings | 7 |
| Usable packs | 6 |
| Build errors | 1 (user 19 — `ChartResponse.positions` dict vs list; **outside CE Stage 0**, blocks core-profile read) |
| Full-natal packs | 3 (u1 Gemini, u2 Aquarius, u26 Pisces) |
| Date-only packs | 3 (Taurus lp=3 clones) |

Anonymized labels only — no emails / DOB values in this doc.

## Blocker found & fixed during review

**Stage 0 ignored live natal cache shapes:**

| Cache shape | Field | Before | After |
|-------------|-------|--------|-------|
| Swiss list | `body` | OK | OK |
| natal_facts-shaped list | `name` | **dropped all planets** | accepted |
| houses `dict` (`Asc` / `house_N` / `1`) | — | ignored (`houses=[]`) | normalized → cusps + angles |

**Evidence:** user 1 full natal had only catalog sun + numerology (5 facts) before fix → **30 facts** after (moon/planets/ASC/MC/houses). Swiss correctly displaces catalog sun.

Fix: `character_engine_stage0_facts_v0.py` + unit test `test_stage0_accepts_name_keyed_positions_and_houses_dict`.

## Post-fix pack results

| Pack | Mode | Facts | Claims | Notes |
|------|------|------:|-------:|-------|
| u1 Gemini lp1 | full | 30 | 0 | ASC Pisces · Moon Aries — no registry match (expected thin) |
| u2 Aquarius lp7 | full | 27 | 1 | `autonomy_high` only · Moon Libra (air) → no `freedom_vs_stability` |
| u20–22 Taurus lp3 | date_only | 5 | 0 | Earth sun outside autonomy/analysis sets · ASC rule capability-gated |
| u26 Pisces | full | 26 | 1 | `presence_through_air_asc` only (Gemini ASC) |

**Thesis frequency (usable packs):** `autonomy_high` 1/6 · `presence_through_air_asc` 1/6 · empty 4/6.

## Gate checklist (live)

| Gate | Result |
|------|--------|
| Traceability (`all_supporting_facts_exist` / edges / no forbidden kinds) | PASS on all usable packs |
| Swiss displaces catalog/bridge | PASS (u1 after fix) |
| Full-natal claims absent without birth time | PASS (ASC rule → `capability_insufficient` on date_only) |
| No single thesis on >50% of packs | PASS |
| Diagnostics do not change Profile publish SoT | PASS (by design) |
| Registry not one claim-set for most profiles | PASS (but **empty dominates**) |

## Product review criteria

| Criterion | Verdict |
|-----------|---------|
| Coverage | **Thin by design** — 5 rules; Gemini / Taurus / many charts → 0 claims |
| Diversity | Low absolute claim variety on this small prod sample; not one-thesis dominance |
| Dominance | PASS — no thesis >50% |
| Insufficient / empty rate | **High (4/6)** — Stage 2 must treat empty graph as `insufficient_identity_core`, not invent |
| Logline / prose | N/A — Stage 1 emits IDs/thesis_keys only (no `surface_text`) |
| Repetition | Identical empty set on 3 Taurus date-only packs (same input family) |
| Traceability | PASS |

## Contrast with live Profile UI (owner-like u2)

Old Profile still shows day-rhythm “ловушка”, Вы-voice spheres, Мудрец from LP — **none of that is CE**.  
CE for Aquarius full natal emits only `autonomy_high` grounded in sun — correct Stage 0–1 behavior.

## Verdict

**Conditional GO to Stage 2 shadow** after Stage 0 cache-shape fix is on the server.

**Do not** broaden the evidence registry before Stage 2 just to fill empty packs — staging residual risk still applies (expand with AND patterns only).  
**Do not** enable `PUBLISH_READY` / Profile cutover.

## Next (order)

1. Deploy Stage 0 cache-shape fix to prod (this change).  
2. Enable `CHARACTER_ENGINE_STAGE2_SHADOW=1` (Stage 0–1 remains on).  
3. Live-review Identity Core: sparse packs → insufficient; Aquarius → one core grounded in Stage 1 claims.  
4. Stage 3+ only after canon §1.4 exit criterion.

## Residual

- user 19 `ChartResponse` ValidationError on core-profile read (positions dict) — separate bug; fix outside CE publish path.  
- Tiny prod N=6 — re-check when more full-natal packs exist.  
- Registry still sun-element thin — expected until deliberate Stage 1 expansion after Stage 2.
