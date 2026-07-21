# Profile · `life_spheres` Quality Review V0

**Status:** SoT after PR-2 · **do not expand to 6 more spheres until RULESET defects below are addressed**  
**Date:** 2026-07-21  
**Passport:** [PROFILE_E2E_BLOCK_PASSPORT_LIFE_SPHERES.md](./PROFILE_E2E_BLOCK_PASSPORT_LIFE_SPHERES.md)  
**Projector:** [PROFILE_LIFE_SPHERES_DETERMINISTIC_PROJECTOR_V0.md](./PROFILE_LIFE_SPHERES_DETERMINISTIC_PROJECTOR_V0.md) · `life_spheres_projector_v0.1`  
**Harness:** `backend/evals/profile_quality/run_life_spheres_quality_pack_v0.py`  
**Cases:** `backend/evals/profile_quality/life_spheres_quality_cases_v0.json`  
**Latest run:** `backend/evals/profile_quality/runs/life_spheres_quality_20260721T145313Z/`

> Goal: prove love / money / decisions produce **grounded, distinct, useful** user meaning — not only a valid JSON object.  
> No class `MODEL`. Weak text ⇒ architectural defect class.

---

## 0. Verdict

| Question | Result |
|----------|--------|
| Funnel decoupling / gate / partial Snapshot (PR-2 engineering) | **Hold** — out of scope to re-litigate here |
| Contrast sensitivity (styles & Venus/Moon change outputs) | **Supported** — pair comparisons pass |
| Honesty without birth time | **Supported** — no house/ASC leaks on sign-only cases |
| Partial styles omit correctly | **Supported** — lsq-07 money/decisions omitted |
| User-facing quality of `how` without houses | **Fail (RULESET)** — planet-in-sign **boilerplate** (“задаёт тон проявления”); only sign label changes |
| Style-lens fields (need/risk/on/off/helps) | **Mostly useful** when class matches; class misfires under keyword collisions |
| Ready to expand to 6 more spheres | **No** — fix `how` trait rules + bucket priority first |
| Ready for life_mission / character_helps | **No** — separate passports after spheres quality holds |

**Automated pack summary (run `20260721T145313Z`):** cases_pass **1/8** (only houses-enriched lsq-05 fully passes specificity) · comparisons_pass **2/2** · defects **23** (dominated by `how` boilerplate RULESET).

---

## 1. Block purpose (per sphere)

| Sphere | User must understand | Differs from identity | Differs from styles | Forbidden at birth-only / no houses |
|--------|----------------------|----------------------|---------------------|-------------------------------------|
| **love** | How closeness shows; what is needed; where it breaks; one support move | Identity = who overall; love = manifestation **in intimacy** | Style = lens; love fields = situation map | House-precise partnership claims; “регулярно…” from living |
| **money** | How value/resource shows; risk; one focus | Not a second biography | Not a copy of `money_style` alone | House 2/8 claims without houses; longitudinal money habits as fact |
| **decisions** | How choosing works; hygiene; one next move | Not life mission | Not a paste of `decision_style` | Confirmed decision “patterns” without history |

**Field roles (evaluate separately, never as one blob):**

| Field | User value |
|-------|------------|
| `how` | Concrete manifestation cue (natal color + locus) |
| `need` | What support looks like here |
| `risk` | Where it breaks here |
| `turns_on` / `turns_off` | Engage / shut-down triggers |
| `helps` | One doable move in this sphere |

---

## 2. Quality criteria

| Criterion | Pass condition |
|-----------|----------------|
| **Grounding** | Field tied to evidence (`rule:` / `planet:` / `house:` / `style:`) |
| **Specificity** | Not interchangeable across users; `how` must not be pure boilerplate |
| **Distinctness** | Spheres ≠ each other; ≠ `identity_core` |
| **Usefulness** | `helps` actionable; `need` concrete support (not cosmic filler) |
| **Internal coherence** | need≠risk; on≠off; style class not fighting its own risk blindly without note |
| **Voice** | About the person — not system/funnel/LLM |
| **Honesty** | No houses/ASC without `houses_available`; no longitudinal claims |

Defect classes allowed: `BLOCK_PURPOSE` · `INPUT` · `RULESET` · `RESPONSE_SCHEMA` · `VALIDATION` · `PROJECTION` · `UI_GATE` · `VOICE`.

---

## 3. Contrast matrix (8 cases)

| ID | Contrast | Intent |
|----|----------|--------|
| lsq-01 / lsq-02 | Same Sun Leo; different Venus/Moon + styles | Love (and others) must diverge |
| lsq-03 / lsq-04 | Same natal Capricorn stack; different styles only | Style lens must move need/risk/on/off/helps |
| lsq-05 | Houses available | `how` enriched; evidence lists houses |
| lsq-06 | No birth time | Sign-only honesty |
| lsq-07 | Incomplete styles | Emit love only; omit money/decisions |
| lsq-08 | Identity slow vs styles fast | Must not fake harmony; expose ruleset bias |

---

## 4. Case reviews

### lsq-01 — soft closeness (Leo · Venus/Moon Cancer)

| Sphere | Foundations that mattered | Rule IDs (sample) | Output (compressed) | Quality | Defects |
|--------|---------------------------|-------------------|---------------------|---------|---------|
| love | Venus Cancer · relationship_style (тёплые/темп) | `love.how.planet`, `love.*.from_style` | how: boilerplate Venus Cancer; need: pace class; helps: граница темпа | **FAIL** | `RULESET` how boilerplate; style_class=`pace` overweights «темп» vs care/warmth (`RULESET` bucket priority) |
| money | Jupiter Cancer · security style | `money.how.planet`, `money.*.from_style` | security need/helps useful | **FAIL** | `RULESET` how boilerplate |
| decisions | Saturn Capricorn · consensus-ish style | `decisions.*` | analysis class (keyword) | **FAIL** | `RULESET` how boilerplate; class may misread «согласование» |

**Snapshot / API:** partial `life_spheres` with 3 keys · fingerprint stable.  
**UI:** FE may prefix love how with «В отношениях» (`PROJECTION` chrome — not inventing claims). Money chrome «В реализации» is a **naming mismatch** for money sphere (`PROJECTION` / copy debt).

---

### lsq-02 — autonomy pace (Leo · Venus Aries · Moon Aquarius)

| Sphere | Influencing inputs | Quality | Defects |
|--------|--------------------|---------|---------|
| love | Venus Aries · clarity/autonomy style | FAIL | `RULESET` how boilerplate |
| money | Jupiter Sag · growth style | FAIL | how boilerplate; helps wording borderline |
| decisions | Saturn Cap · speed style | FAIL | how boilerplate; how **identical** to lsq-01 decisions (same Saturn Capricorn) |

**Compare lsq-01 vs lsq-02:** **PASS** for sensitivity — love/money need/risk/on/off/helps all differ.  
**Residual RULESET:** `decisions.how` unchanged (same Saturn sign) and love/money `how` jaccard ≈ 0.8 (template skeleton dominates).

---

### lsq-03 / lsq-04 — same natal, different styles

| Check | Result |
|-------|--------|
| need/risk/on/off/helps move with styles | **PASS** (comparison) |
| `how` moves with styles | **FAIL expected** — `how` natal-led; identical across pair when planets unchanged |
| decisions on lsq-04 | need shifts; risk/on/off/helps **stuck** on analysis templates despite speed-ish wording in lsq-03 vs analysis in lsq-04 — lsq-03 decisions class=`analysis` because style contains «критерий» (`RULESET` keyword collision) |

---

### lsq-05 — houses available — **PASS**

| Sphere | claim_depth | Evidence houses | Notes |
|--------|-------------|-----------------|-------|
| love | houses_plus_styles | `house:7` | how includes partnership description — specificity OK |
| money | houses_plus_styles | `house:2`, `house:8` | how carries exchange locus |
| decisions | houses_plus_styles | `house:9` | how carries choice locus |

**Proof:** enriching `how` with real house text clears the boilerplate specificity gate. Confirms defect is **missing trait content for sign-only path**, not “spheres impossible without houses”.

---

### lsq-06 — no birth time — honesty OK, specificity FAIL

- No house/ASC markers in fields → **Honesty PASS**.  
- All three `how` still boilerplate → **RULESET FAIL** (same as other sign-only cases).  
- Style fields remain usable.

---

### lsq-07 — incomplete styles

| Sphere | Result |
|--------|--------|
| love | Emitted (relationship_style present) — how still boilerplate FAIL |
| money / decisions | **omit** `style_missing` — **correct architecture** (no invent from identity) |

Gate still opens (one style enough). Partial map is valid product state.

---

### lsq-08 — contradictory foundations

| Observation | Class |
|-------------|-------|
| Projector follows **styles** (pace/growth/…) and ignores identity “slow/silence” tension | `RULESET` / `BLOCK_PURPOSE` — no contradiction policy in v0.1 |
| Style «скорость важнее долгого **анализа**» → class `analysis` not `speed` | `RULESET` — keyword priority / substring collision |
| User gets a fast-style sphere map that fights identity without acknowledgment | Product honesty gap — not longitudinal; still a coherence debt |

---

## 5. Cross-cutting proofs

### 5.1 What works

1. **Independence from patterns** — quality pack uses foundations only (no patterns step).  
2. **Style sensitivity** — need/risk/on/off/helps change when styles change (lsq-03/04).  
3. **Natal sensitivity on planet labels** — Venus/Jupiter signs appear in `how`.  
4. **Honesty** — sign-only cases do not claim houses.  
5. **Omit discipline** — missing styles → omit sphere.  
6. **Houses path** — full quality pass when house descriptions exist (lsq-05).  
7. **Grounding meta** — evidence/rule_ids present per sphere.  
8. **Distinctness vs identity** — no identity_echo failures in this pack.  
9. **Sphere-to-sphere field collapse** — need/helps differ across love/money/decisions when styles differ.

### 5.2 Confirmed defects (must fix before expanding spheres)

| ID | Class | Why architecture produced weak text | Fix direction |
|----|-------|-------------------------------------|---------------|
| D1 | `RULESET` | `_planet_line` emits fixed sentence «задаёт тон проявления»; only `{Planet, sign}` vary → `how` interchangeable | Planet×sign trait table (or require `planet_bullets`) before emit; forbid boilerplate-only `how` |
| D2 | `RULESET` | Style buckets are first-match keyword lists; «темп», «анализ», «критер» steal class from stronger cues | Priority / scoring buckets; multi-label with primary; tests on lsq-01 & lsq-08 |
| D3 | `RULESET` | `how` ignores styles entirely → same natal ⇒ identical how across users with different styles | Optional short style clause in `how` **after** natal trait (still sphere-specific) |
| D4 | `RULESET` | No identity↔styles contradiction policy | Either hedge `how`/`risk` or kitchen flag; do not silently pick styles only |
| D5 | `PROJECTION` | FE frames money `how` as «В реализации» | Align chrome with money sphere (copy), not claim rewrite |
| D6 | `RULESET` | Without houses, pack almost never “passes” specificity — product over-promises natal-presence richness | Either ship traits for sign-only or mark `how` claim_depth visibly thinner in UI later |

**Not defects:** comparisons proving outputs move with foundations; patterns gate; partial omit.

---

## 6. Field-level synthesis

| Field | Grounding | Specificity | Usefulness | Notes |
|-------|-----------|-------------|------------|-------|
| how | planet/house evidence OK | **Weak** sign-only | descriptive | Primary blocker |
| need | style rules OK | OK via style quote | OK as support need | Class misfire affects content |
| risk | style rules OK | OK | OK | |
| turns_on/off | style rules OK | mostly OK | OK | occasional weak binding |
| helps | style rules OK | OK | mostly OK | keep verb-led templates |

---

## 7. Snapshot → API → UI

| Layer | Status |
|-------|--------|
| Projector output | Partial map + `life_spheres_meta` (fingerprint, evidence) |
| Snapshot normalize | Keeps non-empty sphere keys only — OK |
| API | Same contract fields on partial portrait shell — OK for PR-2 |
| UI | Partial spheres render when present (PR-2 FE); forming banner may still show (global ready not split) — `UI_GATE` debt, not sphere invent |
| QuickMap | Must not invent longitudinal patterns — unchanged |

---

## 8. Decision gate (what next)

```text
IF D1 (how traits) + D2 (bucket priority) fixed
  AND quality pack cases_pass ≥ 6/8 without houses requirement
  AND comparisons still pass
THEN expand projector to next spheres (work/family/…)
ELSE do not expand; do not start life_mission / character_helps passports for presence coupling
```

**Immediate next engineering slice (after this review):** ruleset patch for D1+D2 only — re-run this pack — update this document changelog.  
**Still out of scope:** remaining six spheres, mission, helps[], Screen Master redesign.

---

## 9. How to re-run

```bash
cd backend
.venv/bin/python evals/profile_quality/run_life_spheres_quality_pack_v0.py
# writes evals/profile_quality/runs/life_spheres_quality_<ts>/pack.{json,md}
```

Author updates this SoT from the newest run when ruleset changes.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-21 | Initial quality review from pack run `20260721T145313Z`; verdict = do not expand spheres until how traits + buckets fixed |
