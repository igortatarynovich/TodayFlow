# Profile E2E — Sample Pack (first forensic artifact)

**Stage:** [PROFILE_E2E_RECONSTRUCTION.md](../profile/PROFILE_E2E_RECONSTRUCTION.md)  
**Date:** 2026-07-21  
**Source pack:** `backend/evals/profile_quality/runs/review_packs_20260721T085424Z/case_01_pq-001_base.json`  
**Scenario:** Birth only — Aries / life path 1 (`pq-001`), `source_depth=birth_data_only`, `living=null`

> This is **not** yet a production-faithful capture (spheres skipped; no Snapshot/API/UI columns).  
> It is the best existing artifact to start degradation analysis **without changing prompts**.

---

## 1. Allowed inputs (summary)

| Class | Present |
|-------|---------|
| Facts | first_name Аня, birth_date 1991-04-12 |
| Calculated | sun aries/fire/cardinal, life_path 1, expression 5, baseline initiator/fire/fast_start |
| Self-descriptions | none |
| Living / check-ins | **null** |
| Missing | birth_time, birth_place, onboarding, checkins, gender |

Honesty (expected): general portrait only; **no** recurring_patterns as fact; no real stress behaviour as fact.

---

## 2. Funnel artifacts present

| Step | Raw quality (human skim) | Parsed into final? |
|------|--------------------------|--------------------|
| identity | Strong, specific RU — «человек первого шага» | Yes |
| styles | Strong, new angles (relationship/money/decision) | Yes |
| patterns | Invents recurring_patterns + helps from **no living** | Partially (patterns present in raw; final_product in pack truncated before patterns fields in snippet — see JSON) |
| spheres | **Not run** by eval runner | Missing |

Identity raw (abbrev):

> Аня — человек первого шага. Она зажигается от новой идеи и действует раньше, чем успевает испугаться…

→ Evidence that **model can produce meaningful Profile text** on thin inputs.

---

## 3. Unique-knowledge check (this case)

| Step | Unique? | Note |
|------|---------|------|
| identity | Yes | Clear core thesis |
| styles | Mostly yes | Adds relationship/money/decision scenes; some tempo echo of identity |
| patterns | **No (invalid)** | Repeats identity/styles as «patterns» without living evidence — **canon violation** if shown as confirmed repeats |
| spheres | Unknown | Not captured |

---

## 4. Suspected degradation points

### Input
- Onboarding/living absent — correct for scenario.  
- Shared payload has no prior snapshot (OK for first publish).

### Prompt
1. **Patterns step** asked for recurring_patterns with `living: null` — model invents behavioural facts. Prompt says «только из living», but schema still requires pattern strings → forces invention.  
2. **Frame pollution:** system prompts include Today day-structure (чего ждать / что делать / сферы сегодня) via `common_v1.voice_block` — wrong genre for static Profile.  
3. Eval runner ≠ production (skips spheres, 1 attempt).

### Validation
- Pack `validation` section must be read in full JSON — if patterns accepted at birth_only, **gate failed to enforce Content Canon §3**.  
- Phrase gates may still pass high-quality identity (good).

### Projection
- Not captured for this pack (no FE render). Next harness must map contract → QuickMap → V2 visible strings.

---

## 5. Required next capture (definition)

One pack file must contain:

```text
allowed_inputs
calculated_facts (baseline, natal attach if any)
derived_claims / source_depth
exact prompts ×4 (system+user)
raw ×4
parsed ×4
validation decisions (+ rejected raw if any)
persisted snapshot payload
GET /account/core-profile body
FE visible strings per block (Hero, Character, Direction, Evidence, Sources)
```

**Harness (shipped):** [PROFILE_PRODUCTION_CAPTURE_PACK.md](./PROFILE_PRODUCTION_CAPTURE_PACK.md)  
CLI: `backend/evals/profile_quality/run_production_capture_v0.py --cases A,B`

Capture adapter wraps production path (funnel + portrait + optional CoreProfileService publish). Does **not** log personal prompts into `generation_logs`.

**Do not rewrite prompts until production capture packs exist for ≥1 birth-only and ≥1 longitudinal case.**

---

## 6. Working conclusion (provisional)

| Claim | Status |
|-------|--------|
| Model can write good Profile RU when chain is well-specified | **Supported** by case_01 identity/styles (capability evidence only) |
| Bad Profile text = «модель выдумала» | **Rejected as diagnosis** — use architectural classes |
| Four funnel steps each unique | **Not proven**; patterns on birth-only is **GENERATION_GATE + RESPONSE_SCHEMA** |
| Spheres needed as LLM | **Unknown** — never captured in this run |

Architecture principle: [PROFILE_E2E_RECONSTRUCTION.md](../profile/PROFILE_E2E_RECONSTRUCTION.md) · passport: [PROFILE_E2E_BLOCK_PASSPORT_TEMPLATE.md](./PROFILE_E2E_BLOCK_PASSPORT_TEMPLATE.md)

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-21 | v0 — forensic note on existing case_01; requirements for next harness |
