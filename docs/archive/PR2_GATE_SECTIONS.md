# PR2 — шаблон секций PIM PR Gate (для описания PR)

**Статус:** draft — заполнять при открытии PR2  
**Pre-flight:** [PR2_PREFLIGHT.md](./PR2_PREFLIGHT.md)  
**Gate:** [PIM_PR_GATE_V1.md](../pim/PIM_PR_GATE_V1.md) §1, §4 · **Success:** §4.10, §Success below

---

## Summary

PR2: Goal Loop S6–S10 — **first PIM write-path**. Intent Record on **submit only** → DRE guidance → outcome → (optional) async atoms. **Fact before interpretation.** Prod success = **retention**; IR = byproduct (AR-012).

---

## Intent Record birth (§2.1)

| Action | Creates record? |
|--------|-----------------|
| Open S6 / type / pick chip | No |
| Submit «Продолжить» | **Yes** + `day_goal_set` |
| Submit then exit | Yes (open cycle) |
| Edit after submit | Amendment or supersede (spike) |

## PIM (C10–C17) — Q1–Q5 by phase

| Phase | Q1 Signal | Q2 PIM write/read | Q3 Atom | Q4 Evidence | Q5 Consumer |
|-------|-----------|-------------------|---------|-------------|-------------|
| S6 | `day_goal_set` | **write** on **submit** | none | `goal_text`, `set_at`, links | IM service |
| S7 | `day_goal_submitted` (opt) | — | none | request audit | DRE build |
| S8 | `goal_guidance_viewed` | **read** IM+atoms+HDM | none | `generation_id`, `guidance_shown_at` | DRE → S8 copy |
| S9 | `post_goal_action`, … | **update** `post_set_actions` | none | behavioral events | DRE slice |
| S10 | `day_goal_outcome` | **write** outcome on record | **async** candidates | outcome + event ids → chain | ILR job |

---

## PIM Ownership

| Entity | Owner | PR2 |
|--------|-------|-----|
| Intent Record | Intent Model | create / update |
| Goal outcome field | Intent Model | S10 write |
| `DailyGoalSnapshot` | Push service | not SoT |
| Atoms (`intent.*`) | UKM / PIL job | async only |
| S8 copy | DRE | render |

---

## Today disappearance

After one S0–S10 day, without UI:

| Artifact | Expected |
|----------|----------|
| `intent_records` row | ✓ |
| `day_goal_set`, `goal_guidance_viewed`, `day_goal_outcome` | ✓ linked |
| Generation log with goal + audits | ✓ |
| **`pim_read_audit`** on S8 gen | ✓ separate |
| **`pim_write_audit`** on IM writes | ✓ separate |
| Atom candidate row (A6) | optional — not required for merge |

**Fail:** goal only in localStorage; record before submit; mixed read/write audit blob.

---

## PIM Diff (fill at merge)

**Before:** PR1 baseline (6 events, 0 intent records, 0 intent atoms).

**After one full day:**

| Artifact | Δ |
|----------|---|
| `intent_records` | +1 (on submit) |
| PR2 meaning events | +3 minimum (set → guidance viewed → outcome) |
| `pim_write_audit` | +≥2 (create + outcome) — **not** inside read audit |
| `pim_read_audit` | on S8 generation log |
| Intent-domain atom candidates | +0 (job may be off) |

---

## Learning Δ

PR2 minimum: **causal chain of facts** — Intent Record + outcome + dual audits. Atom = interpretation layer (A6 scaffold, not merge gate).

---

## Merge blockers (binary)

1. **Causal chain** — submit → guidance gen → outcome; one `intent_record_id`; SQL + audits; **atom job off OK**.
2. Live S8 — guidance reflects committed goal; distinct from S5.
3. Birth moment — no record before submit.

---

## A1–A6 checklist

- [ ] A1 Intent Record on S6 **submit** (not open/type/pick)
- [ ] A2 PIM slice on S8 (`pim_read_audit`)
- [ ] A3 goal in S9 context
- [ ] A4 outcome on IM + event + `pim_write_audit`
- [ ] A5 no trait fact from one evening
- [ ] A6 async atom + evidence_chain *(scaffold; not merge blocker)*

---

## Success Criterion *(post-deploy · AR-012)*

**Merge** = write-path. **Success** = **daily usefulness**; D7 and IR = indicators.

**Primary:** evening value · «day was better thanks to TodayFlow» · clarity/focus/done.

**Indicators:** D1/D7/≥5 return — **not** North Star. Reject: good D7 · weak evening.

**Tertiary:** IR only after usefulness + retention signal.

Детали: [PIM_PRODUCT_NORTH_STAR.md](PIM_PRODUCT_NORTH_STAR.md) §0.2 · [PR2_PREFLIGHT.md](./PR2_PREFLIGHT.md) §15.
