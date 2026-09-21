# Today Information Contract — next agent

**Date:** 2026-09-21  
**Branch:** `cursor/today-information-contract`  
**Parked:** Profile train on `cursor/profile-knowledge-to-output` @ `744f73d5`. P1 library fill on `cursor/p1-self-compassion-loop-notes` @ `f48a438d`.  
**Pass bound:** TIC N=20. Coverage: [TODAY_INFORMATION_CONTRACT_V1 §11](../today/TODAY_INFORMATION_CONTRACT_V1.md). **14 COMPLETE / 6 PARTIAL / 0 MISSING / 0 OMIT-BY-DESIGN.**

Not PIC. Not IL dump. Not P1 fill. Do not rebuild server until asked.

---

## 0. Decision (locked)

TIC управляет Today. Очередь **только** из §11. First remaining defect = **K13**.

`TIC-K10` = Personal Narrative avoid after bind. Global `do_not` stays on the scene and does not feed `T3.caution`. Missing personal avoid omit.

---

## 1. First 15 minutes

1. This file + tracker NOW (`TIC-K10 COMPLETE`) + Information Contract §11.
2. Stay on `cursor/today-information-contract`. Profile remains parked.
3. Run: `backend/.venv/bin/python -m pytest tests/test_today_information_contract_v1.py -q --tb=short --no-cov`
4. G0 stays deferred. Do not compose-rebuild.

---

## 2. Audit (closed)

Measured IN → F → K → derivation → field → Inventory → locked FE.

COMPLETE: K01, K02, K03, K04, K05, K06, K07, K08, K09, K10, K11, K12, K18, K19.  
PARTIAL: K13, K14, K15, K16, K17, K20.

---

## 3. Queue

1. **K13 only** — chorus bridge, not Personal×card.
2. Then the next §11 defect (K14), not a PIC leftover.

---

## 4. Do not

- Fix anything else inside a K13 hop unless it is the K13 chain.
- Resume PIC / carry CE prose / expand IL.
- Invent TIC-K21 or planned Day Sources into N.
- Treat scent/stone unused-on-path as a K15 license to add generators.
- Rebuild server. Untrip billing. Merge/deploy only if asked.
- Use K13 as a reason to clean remaining Today, moon sheet, or persisted cache.
- Reopen K01/K06/K07/K09/K10.
