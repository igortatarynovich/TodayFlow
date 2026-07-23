# Profile Capture — Case A/B Comparative Report

**Date:** 2026-07-21  
**Parent:** [PROFILE_PRODUCTION_CAPTURE_PACK.md](./PROFILE_PRODUCTION_CAPTURE_PACK.md) · [PROFILE_E2E_RECONSTRUCTION.md](../PROFILE_E2E_RECONSTRUCTION.md)  
**life_spheres:** [PROFILE_E2E_BLOCK_PASSPORT_LIFE_SPHERES.md](./PROFILE_E2E_BLOCK_PASSPORT_LIFE_SPHERES.md) · [PROFILE_LIFE_SPHERES_DETERMINISTIC_PROJECTOR_V0.md](./PROFILE_LIFE_SPHERES_DETERMINISTIC_PROJECTOR_V0.md)  
**Env fix:** `ffa50b5` (repo-root `.env` / Nebius) — closed separately  
**Patterns GENERATION_GATE:** shipped (`72224ae`). **Spheres control-flow / projector:** not yet implemented.

---

## Packs

| Case | Scenario | Pack (local) |
|------|----------|--------------|
| **A** birth-only | `pq-001` Аня | `backend/evals/profile_quality/runs/capture_case_a_retry/capture_pq-001_20260721T141036Z.json` |
| **B** longitudinal | `pq-007` Катя | `backend/evals/profile_quality/runs/capture_case_b/capture_pq-007_20260721T141631Z.json` |

**Eval-only timeout:** capture CLI sets `LLM_HTTP_TIMEOUT_SECONDS=120` (default) — does not alter production Settings defaults (still 12s sync).

---

## Case A — birth_data_only

| Layer | Result |
|-------|--------|
| `source_depth` | `birth_data_only` |
| `allowed_claims.recurring_patterns` | **false** |
| `block_eligibility.patterns` | **may_generate=false**, **ran=true** |
| identity | 1 attempt · ok |
| styles | 1 attempt · ok |
| patterns | 2 attempts · **both fail** (`living_changes: null` while `_patterns_ok` requires ≥12 chars; patterns list still filled from birth/identity) |
| spheres | **not started** (funnel stops after patterns fail/skip → partial) |
| quality / publish | `forming_fallback=true`, status **partial**, Snapshot/GET identity+styles only, `recurring_patterns=[]`, **no `life_spheres`** |
| FE QuickMap / visible_blocks | attached (identity/styles surface; no confirmed patterns; no Direction spheres) |

### Confirmed defects (A)

| Class | Code / evidence |
|-------|-----------------|
| `GENERATION_GATE` (patterns) | **Was:** eligibility forbade patterns but production still called the step. **Shipped fix:** skip LLM when ineligible (`patterns_skipped_ineligible`, attempts=0) |
| `GENERATION_GATE` (spheres) | **Confirmed open defect:** after patterns skip/fail, spheres never start. Passport requires **independent** `spheres_projection_allowed` (natal-presence). Absence of spheres in Case A is **not** an acceptable product outcome |
| `RESPONSE_SCHEMA` | (historical pack) `_patterns_ok` required `living_changes` while forcing the step — addressed for ineligible path by skip; schema still couples mission/helps to patterns step |
| `PROMPT` (secondary) | (historical) honesty-under-sparse-living while schema required fill |

**Case A expectation (locked by passport — no longer a hypothesis):**

```text
patterns: may_generate=false · ran=false
spheres:  may_generate=true when natal+identity+styles foundations hold
spheres:  projected (deterministic; PR-2: love/money/decisions)
Snapshot/API/UI: keep projected spheres even with empty recurring_patterns
```

Current production after patterns gate: patterns correctly skipped; **spheres still absent** → spheres coupling defect remains until projector PR.

---

## Case B — profile_plus_checkins

| Layer | Result |
|-------|--------|
| `source_depth` | `profile_plus_checkins` |
| `allowed_claims.recurring_patterns` | **true** |
| `block_eligibility.patterns` | **may_generate=true**, **ran=true** |
| identity / styles / patterns | 1 attempt each · ok |
| spheres | attempt1 parse fail (raw ~15k, not dict) · attempt2 **ok** (9 spheres) |
| quality | `ok=true`, status **ready**, `forming_fallback=false` |
| Snapshot / GET | same contract (`snap == get` for identity + patterns) |
| FE QuickMap / visible_blocks | attached; all three patterns appear under **direction** |

### Longitudinal facts — not merely eligibility

Living input (prompt):

- summary: «перегруз к вечеру; сложные разговоры откладываются»
- notes: «не стала писать коллеге», «разговор с партнёром перенесла», «сделала дела по списку», …
- insights: «откладывание сложных разговоров», «восстановление через порядок»

**All of the above are present in the patterns `user_prompt`.**

Contract `recurring_patterns` (accepted):

1. Вечернее опустошение после дня в режиме «надо»
2. Откладывание сложных разговоров до «лучшего момента»
3. Восстановление через порядок и список дел

`living_changes` describes the productivity ↔ withdrawal cycle from the check-in window.

Literal notes are not copied into raw (good), but **semantic content matches living**, not a rehash of identity alone. Identity is about holding the world via order; patterns add evening empty-out / postponed talks / recovery-via-list — grounded in signals.

**UI:** all three patterns + `living_changes` appear in `visible_blocks.direction` (and related character drains/strengthens echo the same themes). Snapshot → GET → FE without drop of those claims.

### Spheres (B)

- **Current code:** reachable only after patterns success (LLM `profile.spheres.v1`).
- First attempt: large raw, **JSON parse fail** → retry.
- Second attempt: accepted 9×6 fields.
- **Target:** spheres must **not** depend on patterns result. Case B proves patterns+living path; it does **not** justify coupling. After projector: Case B patterns remain; spheres come from deterministic ruleset (legacy LLM retired as content authority).
- Uniqueness vs identity/styles: still must be proven by projector validation gates (`identity_echo`, `spheres_not_distinct`).

---

## Side finding (B Evidence depth)

FE `visible_blocks.evidence` shows `onboarding_answers` while pack `source_depth` is `profile_plus_checkins`.

Cause: assembled capture GET body has `living.signals[]` but **no** `living.signal_profile.signals_days`, so client `resolveProfileSourceDepth` under-counts check-ins.

| Class | Note |
|-------|------|
| `PROJECTION` / capture assemble | Eval Snapshot shape incomplete vs production living marker — Evidence honesty can drift. Not a Nebius defect. |

---

## Hypotheses — status after packs

| Hypothesis | Status |
|------------|--------|
| «Плохой Profile = модель выдумывает» | **Rejected** as diagnosis — use architectural classes |
| Patterns on birth-only should not run | **Confirmed** → **gate shipped** (skip when ineligible) |
| Asking «не выдумывай» is enough | **Rejected** — schema + forced step dominate |
| Patterns with living use longitudinal input | **Supported** (prompt contains living; raw/Snapshot/UI reflect it) |
| All four steps always complete | **Current:** only when patterns ok — A stops; B may reach LLM spheres. **Target:** spheres independent of patterns |
| Spheres require patterns success | **Rejected as product** — accidental coupling; confirmed `GENERATION_GATE` defect on spheres |
| Spheres = natal-presence deterministic | **Locked** (passport + projector spec); implementation pending |
| FE always mirrors Snapshot depth | **Partial fail** on Evidence depth without `signals_days` |

---

## Comparative one-liner

```text
A (after patterns gate): patterns SKIPPED correctly → partial without patterns
   → DEBT: spheres still not started (coupling) → UI without Direction spheres
A (target): patterns skipped · spheres projected from foundations · UI keeps spheres

B (current): patterns OK → legacy LLM spheres after patterns → ready
B (target): patterns OK · spheres from projector independent of patterns result
```

---

## Implementation slices

### Slice 1 — patterns GENERATION_GATE

**Status: IMPLEMENTED** — `patterns_generation_allowed` in `profile_disclosure_funnel_v0`.

```text
if not patterns_generation_allowed(user_json):
    skip profile.patterns.v1 (no LLM call)
    Snapshot / merge: recurring_patterns=[], living_changes=null
    reason=patterns_skipped_ineligible · partial=true
    # DEBT (still true after slice 1): spheres not started
```

Regression: Case A → patterns attempts=0, may_generate=false, ran=false.

### Slice 2 — life_spheres foundation (PR-2)

**Status: IMPLEMENTED** — `life_spheres_projector_v0` + funnel continues after patterns skip/fail.  
Spec: [PROFILE_LIFE_SPHERES_DETERMINISTIC_PROJECTOR_V0.md](./PROFILE_LIFE_SPHERES_DETERMINISTIC_PROJECTOR_V0.md).

```text
identity → styles
  → patterns IFF patterns_generation_allowed   # unchanged
  → spheres IFF spheres_projection_allowed     # independent of patterns outcome
content = deterministic projector v0.1 (love, money, decisions)
partial Snapshot.life_spheres allowed
legacy profile.spheres.v1 = not target authority
```

**Case A success criteria after Slice 2:** patterns ran=false; spheres eligibility true; spheres projected; Snapshot/API/UI retain them.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-21 | Case A/B packs analyzed; comparative report; slice = patterns generation gate |
| 2026-07-21 | **IMPLEMENTED** production GENERATION_GATE: skip patterns when ineligible |
| 2026-07-21 | Locked Case A spheres expectation; patterns↔spheres coupling = confirmed defect; Slice 2 = projector spec |
| 2026-07-21 | **IMPLEMENTED** Slice 2: deterministic spheres (love/money/decisions) + funnel decoupling |
