# Profile knowledge-to-output — next agent

**Date:** 2026-09-20  
**Branch:** `cursor/profile-knowledge-to-output`  
**Parked:** P1 library fill on `cursor/p1-self-compassion-loop-notes` @ `f48a438d`  
**Pass bound:** PIC N=18 drives Profile. Occupancy F03/F06 → K01 qualifier closed. K13 COMPLETE. K02 COMPLETE. K12 COMPLETE. K05 COMPLETE. K04 COMPLETE. K09 COMPLETE. K07 COMPLETE. K10 COMPLETE. K06 OMIT-BY-DESIGN. K15 COMPLETE. **K16 COMPLETE.** Coverage: [PROFILE_INFORMATION_CONTRACT_V1 §11](../profile/PROFILE_INFORMATION_CONTRACT_V1.md).

Not remaining P1. Not IL-3→Stage 1. Not TODAY_INFORMATION_CONTRACT. Do not rebuild server until the PIC queue is worked.

---

## 0. Decision (locked)

PIC управляет разработкой. Сначала `PIC-K*` + исходные `PIC-F*`, потом вся цепочка до slot. Не «что ещё протащить из движка».

K01 thesis может остаться `builds_through_analysis`. Occupancy меняет конкретизацию, не двух разных людей.

**Profile train first-paint core is closed except K01 thesis mint (not in queue).** 15 COMPLETE / 2 PARTIAL / 0 MISSING / 1 OMIT-BY-DESIGN. Remaining queue is K03, then deferred K01. Then TODAY_INFORMATION_CONTRACT.

---

## 1. First 15 minutes

1. This file + tracker NOW (`PIC K16 COMPLETE`) + Information Contract §11 queue.
2. Stay on `cursor/profile-knowledge-to-output`. Next code: **K03** — ASC/MC `how` in `P2.anchor.asc/mc`; house how stays Explore.
3. Run: `backend/.venv/bin/python -m pytest tests/test_profile_knowledge_to_output_v1.py tests/test_profile_deep_themes_v0.py tests/test_character_engine_profile_consumption_v0.py -q --tb=short --no-cov`
4. G0 stays deferred. Do not untrip `DATA/ops/llm_spend.json`. Do not compose-rebuild.

---

## 2. Occupancy (closed)

Same Sun Virgo / Moon Taurus / ASC Gemini. Mars Cancer H4 vs Libra H7.

Thesis identical: `builds_through_analysis`. Surface/recognition differs by IL-2 lemmas. Occupancy = `qualifier`. Not IL-3. Not IL-4. Catalog `draft`.

---

## 2b–2k. Closed hops

K13 · K02 · K12 · K05 · K04 · K09 · K07 · K10 · K06 (OMIT-BY-DESIGN) · K15 as previously closed. See tracker Architecture impact blocks.

---

## 2l. K16 (closed — COMPLETE)

Practical tips are not new personality knowledge. Existing GET/PUT `/account/profile/deep-themes` already existed; this hop locked the derivation:

selected K07 theme → existing how/need/risk → chrome-wrapped 1–2 do-lines → K16 → Explore `P6.practical_tips`.

Source of the action is `derive_practical_tips_from_k07_sphere` in `profile_deep_themes_v0` (`k16_source=k07_how_need_risk`). Not identity-thesis `_TIPS`, not `_GENERIC_TIPS`, not Stage4/5 essay, not LLM. Trial+ only. Missing matching K07 row → empty omit. how/need/risk never rewritten. Chooser moved off the path into Explore. Grammar emit of `P6.practical_tips` is Explore-only. No merge onto P4 spheres. K03 and K01 were not this hop.

---

## 3. Queue (from §11, not architecture leftovers)

1. K03 — ASC/MC how on P2; house how Explore.

COMPLETE already: K02, K04, K05, K07, K08, K09, K10, K11 (bridge), K12, K13, K14, K15, K16, K17, K18.  
OMIT-BY-DESIGN: K06 (path M).  
Not in queue: 13-key K01 thesis mint.

---

## 4. Do not

- Resume P1 fill.
- Expand IL (transits, angles, occupancy dump).
- Mint K06 secondaries onto P3 or invent a slot because the id exists.
- Change 13-key K01 thesis because Mars differs.
- Invent PIC-K19.
- Drag K03 house how/do into leftover K16 work.
- Start TODAY_INFORMATION_CONTRACT.
- Rebuild/recreate compose services on this host for this queue.
- Untrip billing. Merge/deploy only if asked.
