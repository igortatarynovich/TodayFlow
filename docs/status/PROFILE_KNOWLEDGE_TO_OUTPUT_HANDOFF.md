# Profile knowledge-to-output — next agent

**Date:** 2026-09-21  
**Branch:** `cursor/profile-knowledge-to-output`  
**Parked:** P1 library fill on `cursor/p1-self-compassion-loop-notes` @ `f48a438d`  
**Pass bound:** PIC N=18 drives Profile. **K01 COMPLETE.** Occupancy F03/F06 qualifier stands. K02–K18 closed or OMIT-BY-DESIGN (K06). Coverage: [PROFILE_INFORMATION_CONTRACT_V1 §11](../profile/PROFILE_INFORMATION_CONTRACT_V1.md).

Not remaining P1. Not IL-3→Stage 1. Profile Information Contract is executed in code. `TODAY_INFORMATION_CONTRACT` is the next named start — do not begin it inside a Profile hop. Do not rebuild server until asked.

---

## 0. Decision (locked)

PIC управляет разработкой. Сначала `PIC-K*` + исходные `PIC-F*`, потом вся цепочка до slot.

K01 определяется из разрешённых фактов, не из 13-key bucket. Occupancy конкретизирует механизм, не заменяет его. Virgo/Taurus/Gemini + Mars Cancer H4 vs Libra H7: механизм близкий, recognition line разная и **не** 13-key фраза.

**Profile train is closed.** 17 COMPLETE / 0 PARTIAL / 0 MISSING / 1 OMIT-BY-DESIGN.

---

## 1. First 15 minutes

1. This file + tracker NOW (`PIC K01 COMPLETE`) + Information Contract §11.
2. Stay on `cursor/profile-knowledge-to-output` until asked to open Today.
3. Run: `backend/.venv/bin/python -m pytest tests/test_profile_knowledge_to_output_v1.py tests/test_character_engine_stage2_identity_v0.py tests/test_character_engine_profile_consumption_v0.py -q --tb=short --no-cov`
4. G0 stays deferred. Do not untrip `DATA/ops/llm_spend.json`. Do not compose-rebuild.

---

## 2. Occupancy (closed)

Same Sun Virgo / Moon Taurus / ASC Gemini. Mars Cancer H4 vs Libra H7.

Mechanism stays close (`planet_in_sign:sun:virgo`). Surface/recognition differs by IL-2 qualifier lemmas. Occupancy = `qualifier`. Not IL-3. Not IL-4. Catalog `draft`.

---

## 2b–2n. Closed hops

K13 · K02 · K12 · K05 · K04 · K09 · K07 · K10 · K06 (OMIT-BY-DESIGN) · K15 · K16 · K03 · **K01** as previously closed. See tracker Architecture impact blocks.

---

## 2n. K01 (closed — COMPLETE)

Identity Core is not a 13-key Sun/Moon/ASC mint.

F01–F04 (+ F05 full, F09 contribution) → IL-2 roles (`compose_k01_identity_v0`) → one observable mechanism → `P1.recognition_line` / `P1.identity_core`.

Each piece traces to grounded evidence. Missing moon/ASC/house/F09 drops that piece. 13-key registry is fallback only if sun cannot compose. LLM does not overwrite composed meaning. Not a traits list. Not K03 applied how/do. Not Decode/tips.

---

## 3. Queue

1. **TODAY_INFORMATION_CONTRACT** — separate start. Do not carry a 13-key personality mint into Today.

COMPLETE: K01, K02, K03, K04, K05, K07, K08, K09, K10, K11 (bridge), K12, K13, K14, K15, K16, K17, K18.  
OMIT-BY-DESIGN: K06 (path M).

---

## 4. Do not

- Resume P1 fill.
- Expand IL (transits, angles, occupancy dump).
- Mint K06 secondaries onto P3 or invent a slot because the id exists.
- Expand the 13-key registry to “fix” K01.
- Invent PIC-K19.
- Start TODAY_INFORMATION_CONTRACT inside this Profile hop.
- Rebuild/recreate compose services on this host unless asked.
- Untrip billing. Merge/deploy only if asked.
