# Profile · `life_spheres` Quality Review V0

**Status:** Projector D1+D2 quality **PASS** as baseline · **architectural pivot** to synthesis-on-cues (see below)  
**Date:** 2026-07-21  
**Passport:** [PROFILE_E2E_BLOCK_PASSPORT_LIFE_SPHERES.md](./PROFILE_E2E_BLOCK_PASSPORT_LIFE_SPHERES.md)  
**Synthesis:** [PROFILE_E2E_BLOCK_PASSPORT_SPHERES_SYNTHESIS.md](./PROFILE_E2E_BLOCK_PASSPORT_SPHERES_SYNTHESIS.md)  
**Projector:** [PROFILE_LIFE_SPHERES_DETERMINISTIC_PROJECTOR_V0.md](./PROFILE_LIFE_SPHERES_DETERMINISTIC_PROJECTOR_V0.md) · `life_spheres_projector_v0.2` (A/B, not final copy SoT)  
**Harness (projector):** `backend/evals/profile_quality/run_life_spheres_quality_pack_v0.py`  
**Harness (synthesis):** `backend/evals/profile_quality/run_life_spheres_synthesis_eval_v0.py`  
**Cases:** `backend/evals/profile_quality/life_spheres_quality_cases_v0.json`  
**Latest projector run:** `…/life_spheres_quality_20260721T151047Z/`  
**Latest synthesis run:** `…/life_spheres_synthesis_20260721T151429Z/` (8/8 after validator FP fix)

> Goal: prove love / money / decisions produce **grounded, distinct, useful** user meaning — not only a valid JSON object.  
> No class `MODEL`. Weak text ⇒ architectural defect class (prompt / cues / validation).  
> **Do not** grow more projector field rules as the main fix path — fix **what we ask** the model.

---

## 0. Verdict (current)

### 0A · Projector baseline (kept)

| Question | Result |
|----------|--------|
| D1 planet×sign traits (no boilerplate `how`) | **PASS** |
| D2 scored style buckets (lsq-01 care, lsq-08 speed) | **PASS** |
| Contrast sensitivity | **PASS** — comparisons 2/2 |
| Honesty without birth time | **PASS** |
| Partial styles omit | **PASS** (lsq-07) |
| Sign-only `how` specificity | **PASS** |
| cases_pass ≥ 6/8 | **PASS — 8/8** |

**Projector pack (`20260721T151047Z`):** cases_pass **8/8** · comparisons_pass **2/2**.

### 0B · Synthesis pivot (target content)

| Question | Result |
|----------|--------|
| Prompt asks for 6 distinct field jobs | **Locked** in `profile.spheres.synthesis.v1` |
| Prepared `sphere_cues` (not raw planet=sign) | **PASS** dry-run 8/8 |
| LLM synthesis validation | **PASS 8/8** (`20260721T151429Z` + revalidate) |
| Contrast profiles diverge | **PASS** 2/2 |
| Not a projector clone | **PASS** (mean Jaccard ≈ 0.02) |
| Lexical repeat stability | Weak (~0.12–0.30) — paraphrase OK; do not “fix” with more gates |
| Funnel / UI wire | **Not yet** |
| Expand to 6 more spheres / life_mission / Character helps | Still **frozen** |

---

## 1. What changed since first review (v0.1 → v0.2)

| Defect | Class | Fix |
|--------|-------|-----|
| D1 `how` boilerplate «задаёт тон проявления» | `RULESET` | `life_spheres_traits_v0` — sphere×planet×sign manifestation traits; unsupported → omit |
| D2 first-match keyword buckets | `RULESET` | `life_spheres_style_buckets_v0` — weighted cues + conflict negatives + primary/secondary + score trace |

**Regression tests:** `backend/tests/test_life_spheres_d1_d2_v0.py` (lsq-01 care, lsq-08 speed, traits, omit, fingerprint bump, comparisons).

---

## 2. Block purpose (unchanged)

| Sphere | User must understand | Differs from identity / styles |
|--------|----------------------|--------------------------------|
| love | How closeness shows; need; break; one support | Manifestation in intimacy ≠ who / ≠ style paste |
| money | Value/resource manifestation; risk; one focus | Not biography; not raw money_style |
| decisions | How choosing works; hygiene step | Not life mission; not raw decision_style |

---

## 3. Quality criteria (unchanged)

Grounding · Specificity · Distinctness · Usefulness · Internal coherence · Voice · Honesty  

Defect classes: `BLOCK_PURPOSE` · `INPUT` · `RULESET` · `RESPONSE_SCHEMA` · `VALIDATION` · `PROJECTION` · `UI_GATE` · `VOICE`.

---

## 4. Case results (`20260721T151047Z`)

| ID | Contrast | Result | Notes |
|----|----------|--------|-------|
| lsq-01 | soft closeness | **PASS** | love `style_class=care` (not pace); Venus Cancer trait how |
| lsq-02 | autonomy pace | **PASS** | Venus Aries trait ≠ lsq-01 how; decisions `speed` |
| lsq-03 / lsq-04 | same natal, different styles | **PASS** | need/helps diverge; comparison green |
| lsq-05 | houses | **PASS** | traits + house weave; claim_depth houses_plus_styles |
| lsq-06 | no birth time | **PASS** | no house markers; traits still specific |
| lsq-07 | incomplete styles | **PASS** | love emit; money/decisions omit |
| lsq-08 | contradiction | **PASS** | decisions `speed` (not analysis); styles win without inventing longitudinal claims |

### Sample claim traces

**lsq-01 love.how**  
Foundations: Venus Cancer · relationship_style (тёплые/предсказуемость/мягкий темп)  
Rules: `trait:love.venus.cancer` · `bucket:care` · `rule:love.*.from_style`  
Output: эмоциональная безопасность / знакомый ритм / забота в мелочах — not boilerplate.

**lsq-08 decisions**  
Style: «скорость важнее долгого анализа»  
Bucket scores: speed↑ analysis↓ (conflict cues) → primary=`speed`  
Evidence includes `bucket:speed` and negative analysis hits in meta.

---

## 5. Cross-cutting proofs

### Works

1. No boilerplate `how` on sign-only path.  
2. Style scoring resists keyword traps.  
3. Trait + bucket traces in `per_sphere` / evidence.  
4. Fingerprint includes projection_version + trait_rule_ids.  
5. Omit on unsupported trait (no fake personal promise).  
6. Comparisons remain green.  
7. Honesty / identity-echo clean on this pack.

### Remaining non-blocking debts

| ID | Class | Note |
|----|-------|------|
| R1 | `PROJECTION` | FE money chrome «В реализации» — copy mismatch, not claim invent |
| R2 | `UI_GATE` | Global ready / forming banner not block-level yet |
| R3 | `RULESET` | Identity↔styles contradiction still unresolved as product policy (lsq-08 follows styles; acceptable for v0.2 presence) |
| R4 | Capture | Production-faithful Case A/B + UI checklist on PR #2 still to close before merge |

---

## 6. Merge gate for PR #2

| Criterion | Status |
|-----------|--------|
| cases_pass ≥ 6/8 | **8/8** |
| comparisons_pass = 2/2 | **2/2** |
| sign-only how specificity | **PASS** |
| no new honesty / identity-echo | **PASS** |
| lsq-01 / lsq-08 classification | **care / speed** |
| SoT updated to new run | **this doc** |
| Production-faithful Case A/B + UI test plan on PR | **still open** — required before merge |

**Frozen until after merge + separate decisions:** remaining six spheres · life_mission · character_helps · LLM wording · spheres prompt.

---

## 7. Re-run

```bash
cd backend
.venv/bin/python evals/profile_quality/run_life_spheres_quality_pack_v0.py
```

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-21 | Initial review from `20260721T145313Z` — fail (how boilerplate); do not expand |
| 2026-07-21 | D1+D2 → `v0.2`; run `20260721T151047Z` — **8/8 PASS**; merge blocked only on remaining PR test-plan Case A/B/UI |
