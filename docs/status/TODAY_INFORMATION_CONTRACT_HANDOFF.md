# Today Information Contract — FROZEN

**Date:** 2026-09-21  
**Branch:** `cursor/today-information-contract`  
**Parked:** Profile train on `cursor/profile-knowledge-to-output` @ `744f73d5`. P1 library fill on `cursor/p1-self-compassion-loop-notes` @ `f48a438d`.  
**Pass bound:** **TODAY_INFORMATION_CONTRACT: CLOSED / PASS.** Independent close-out §12. Coverage ledger §11 remains 20 COMPLETE / 0 PARTIAL / 0 MISSING / 0 OMIT-BY-DESIGN and is **not** the close-out proof.

Not PIC. Not IL dump. Not P1 fill. Do not rebuild server until asked.

---

## 0. Decision (locked)

TIC is **closed**. Do **not** invent TIC-K21. Do **not** continue this train by inertia.

Glance leftover is **out of TIC locked-surface scope** (`TodayGlanceAct` unmounted; `glanceSection` unrendered). If a later audit finds it mounted on the 4-surface, the freeze is void and the gate fails — fix in a separate hop, not inside an audit.

---

## 1. First 15 minutes

1. This file + tracker NOW (`TIC CLOSE-OUT PASS`) + Information Contract §12.
2. Do not start a new TIC-K. Next product gate is chosen from canon.
3. Run (ledger only): `backend/.venv/bin/python -m pytest tests/test_today_information_contract_closeout_v1.py -q --tb=short --no-cov`
4. G0 stays deferred. Do not compose-rebuild.

---

## 2. Close-out (PASS)

Four blocks independently re-audited the assembled system:

1. 20/20 executable re-audit — PASS  
2. Inventory last-authority — PASS  
3. Forbidden-source scan (regression K01/K06/K07/K09/K10/K13–K17/K20) — PASS  
4. Omit integrity — PASS  

Gate: `evaluate_tic_closeout`. FE: `todayTicCloseout.test.ts`.

---

## 3. Queue

**Empty.** Next named product gate comes from canon (PIC §9 names Compatibility Information Contract as a separate table). Not this file. Not Glance unless a later audit puts it in locked-surface scope.

---

## 4. Do not

- Invent TIC-K21 or resume TIC hops.
- Treat §11 COMPLETE as a reason to keep working Today meaning.
- Resume PIC / carry CE prose / expand IL.
- Rebuild server. Untrip billing. Merge/deploy only if asked.
- Reopen Glance as a fifth act from this freeze.
