# Profile Capture — Case A/B Comparative Report

**Date:** 2026-07-21  
**Parent:** [PROFILE_PRODUCTION_CAPTURE_PACK.md](./PROFILE_PRODUCTION_CAPTURE_PACK.md) · [PROFILE_E2E_RECONSTRUCTION.md](../PROFILE_E2E_RECONSTRUCTION.md)  
**Env fix:** `ffa50b5` (repo-root `.env` / Nebius) — closed separately  
**Gates / prompts / UI / production timeout:** **not changed**

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
| spheres | **not started** (funnel stops after patterns fail → partial) |
| quality / publish | `forming_fallback=true`, status **partial**, Snapshot/GET identity+styles only, `recurring_patterns=[]` |
| FE QuickMap / visible_blocks | attached (identity/styles surface; no confirmed patterns) |

### Confirmed defects (A)

| Class | Code / evidence |
|-------|-----------------|
| `GENERATION_GATE` | eligibility forbids patterns; production still calls the step (`generation_ran_while_ineligible`) |
| `RESPONSE_SCHEMA` | `_patterns_ok` requires `recurring_patterns` + `living_changes` without longitudinal evidence |
| `PROMPT` (secondary) | step still asks for patterns / honesty under sparse living — wrong design vs gate |

Raw (both attempts) invents birth-style “recurring” lines (`Загорается новой идеей…`) with `living_changes: null` → validator rejects → no Snapshot patterns. **This is not «model invented» as a product diagnosis** — architecture forced the call and then rejected incomplete schema fill.

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

- Required by funnel after patterns.
- First attempt: large raw, **JSON parse fail** → retry.
- Second attempt: accepted 9×6 fields.
- **Open hypothesis:** spheres still may duplicate styles/identity (not fully audited here); uniqueness not proven, but step is reachable when patterns succeed.

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
| Patterns on birth-only should not run | **Confirmed** (eligibility false, production still runs) |
| Asking «не выдумывай» is enough | **Rejected** — schema + forced step dominate |
| Patterns with living use longitudinal input | **Supported** (prompt contains living; raw/Snapshot/UI reflect it) |
| All four steps always complete | **Only when prior steps ok** — A stops at patterns; B completes spheres on retry |
| Spheres always unique knowledge | **Still open** |
| FE always mirrors Snapshot depth | **Partial fail** on Evidence depth without `signals_days` |

---

## Comparative one-liner

```text
A: eligibility FORBIDS patterns → production STILL runs → schema rejects null living_changes
   → partial Snapshot without patterns → UI without confirmed patterns

B: eligibility ALLOWS patterns → living facts IN prompt → patterns IN raw/Snapshot/GET/UI
   → spheres retry then ok → ready contract
```

---

## First narrow implementation slice (from evidence)

**Status: IMPLEMENTED** — `patterns_generation_allowed` gate in `profile_disclosure_funnel_v0`.

```text
if not patterns_generation_allowed(user_json):  # classify_allowed_claims(depth).recurring_patterns
    skip profile.patterns.v1 (no LLM call)
    Snapshot / merge: recurring_patterns=[], living_changes=null
    reason=patterns_skipped_ineligible · partial=true
    spheres not started (same as prior patterns_failed stop — spheres code unchanged)
```

Regression: Case A path → patterns attempts=0, may_generate=false, ran=false.  
Case B path unchanged when living/check-ins make depth ≥ profile_plus_checkins.


---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-21 | Case A/B packs analyzed; comparative report; slice = patterns generation gate |
| 2026-07-21 | **IMPLEMENTED** production GENERATION_GATE: skip patterns when ineligible |
