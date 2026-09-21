# Profile knowledge-to-output — next agent

**Date:** 2026-09-20  
**Branch:** `cursor/profile-knowledge-to-output`  
**Parked:** P1 library fill on `cursor/p1-self-compassion-loop-notes` @ `f48a438d`  
**Pass bound:** PIC N=18 drives Profile. Occupancy F03/F06 → K01 qualifier closed. K13–K16 COMPLETE. K06 OMIT-BY-DESIGN. **K03 COMPLETE.** Coverage: [PROFILE_INFORMATION_CONTRACT_V1 §11](../profile/PROFILE_INFORMATION_CONTRACT_V1.md).

Not remaining P1. Not IL-3→Stage 1. Not TODAY_INFORMATION_CONTRACT until K01 thesis is closed or consciously deferred. Do not rebuild server until the PIC queue is worked.

---

## 0. Decision (locked)

PIC управляет разработкой. Сначала `PIC-K*` + исходные `PIC-F*`, потом вся цепочка до slot. Не «что ещё протащить из движка».

K01 thesis может остаться `builds_through_analysis`. Occupancy меняет конкретизацию, не двух разных людей.

**Profile train first-paint core is closed except K01 thesis mint.** 16 COMPLETE / 1 PARTIAL / 0 MISSING / 1 OMIT-BY-DESIGN. Remaining: deferred K01 thesis mint as a **separate decision**. Then TODAY_INFORMATION_CONTRACT.

---

## 1. First 15 minutes

1. This file + tracker NOW (`PIC K03 COMPLETE`) + Information Contract §11 queue.
2. Stay on `cursor/profile-knowledge-to-output`. Next is **not Today**. Next is an explicit K01 thesis decision (close mint or defer).
3. Run: `backend/.venv/bin/python -m pytest tests/test_profile_knowledge_to_output_v1.py tests/test_character_engine_profile_consumption_v0.py tests/test_natal_decode_depth_v0.py -q --tb=short --no-cov`
4. G0 stays deferred. Do not untrip `DATA/ops/llm_spend.json`. Do not compose-rebuild.

---

## 2. Occupancy (closed)

Same Sun Virgo / Moon Taurus / ASC Gemini. Mars Cancer H4 vs Libra H7.

Thesis identical: `builds_through_analysis`. Surface/recognition differs by IL-2 lemmas. Occupancy = `qualifier`. Not IL-3. Not IL-4. Catalog `draft`.

---

## 2b–2l. Closed hops

K13 · K02 · K12 · K05 · K04 · K09 · K07 · K10 · K06 (OMIT-BY-DESIGN) · K15 · K16 as previously closed. See tracker Architecture impact blocks.

---

## 2m. K03 (closed — COMPLETE)

Applied angles/houses are not a second personality root and not K07 spheres.

F05/F06 → angle orientation × sign manner (ASC/MC) and IL-2 `compose_planet_in_house` (occupied Sun–Saturn) → how/do → Explore `P6.applied.asc` / `P6.applied.mc` / `P6.applied.house`.

Full natal only. Unoccupied houses omit. Identity-thesis 12-house bank is not the source. K15 Decode and K16 tips are not fallback. DSC/IC stay out of V1. Not added to P1–P5. House 1 occupancy is not ASC.

---

## 3. Queue (from §11, not architecture leftovers)

1. **K01 thesis mint** — close the 13-key mint or consciously defer. Do not start TODAY_INFORMATION_CONTRACT before that decision.

COMPLETE already: K02, K03, K04, K05, K07, K08, K09, K10, K11 (bridge), K12, K13, K14, K15, K16, K17, K18.  
OMIT-BY-DESIGN: K06 (path M).

---

## 4. Do not

- Resume P1 fill.
- Expand IL (transits, angles, occupancy dump).
- Mint K06 secondaries onto P3 or invent a slot because the id exists.
- Change 13-key K01 thesis because Mars differs — that is the remaining decision, not a silent hop.
- Invent PIC-K19.
- Start TODAY_INFORMATION_CONTRACT.
- Rebuild/recreate compose services on this host for this queue.
- Untrip billing. Merge/deploy only if asked.
