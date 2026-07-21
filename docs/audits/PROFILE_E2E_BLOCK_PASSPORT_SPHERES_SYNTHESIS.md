# Profile E2E — Prompt Passport: `profile.spheres.synthesis.v1`

**Status:** active passport · eval harness green · **wired in production funnel** (`synthesize_life_spheres_v0`)  
**Date:** 2026-07-21  
**Block:** `life_spheres` · [PROFILE_E2E_BLOCK_PASSPORT_LIFE_SPHERES.md](./PROFILE_E2E_BLOCK_PASSPORT_LIFE_SPHERES.md)  
**Stage:** [PROFILE_E2E_RECONSTRUCTION.md](../PROFILE_E2E_RECONSTRUCTION.md)  
**Code:** `prompts/profile_spheres_synthesis_v1.py` · `services/life_spheres_cues_v0.py` · `services/life_spheres_synthesis_validate_v0.py`  
**Eval:** `evals/profile_quality/run_life_spheres_synthesis_eval_v0.py` · run `life_spheres_synthesis_20260721T151429Z`

> **Pivot:** проблема качества — не «модели нельзя доверять», а **плохо определённая задача**.  
> Deterministic слой выбирает evidence и `sphere_cues`.  
> **Пользовательский текст** создаёт synthesis prompt.  
> Legacy `profile.spheres.v1` (funnel step 4) и projector `v0.2` as final copy — **not** target content authority.

---

## 0A. Product formula (north star — no extra magic)

```text
calculated facts (planets, houses, ASC, aspects, numerology, profile facts)
  → one user fact base, laid out by meaning domains
  → select relevant context for the current question
  → clear prompt with a concrete job
  → personal answer
```

Later: birth foundations + accumulated living data + current question → sharper answer.

| Layer | Does | Does not |
|-------|------|----------|
| Calc / foundations | Already computed natal & profile facts | Re-interpret astrology in the LLM |
| Fact base | Map ready facts into domains (love, money, decisions, …) | Hand-authored phrase tables per field |
| Context select | Pick relevant slice for this block/question | Dump the whole chart |
| Prompt | State the user question + required transformation | Ask the model to “read the chart” |
| Model | Synthesize practical personal copy | Guess planets/signs or invent living history |

`life_spheres` in this slice is the first concrete instance: Venus/Moon/Mars/7H cues + identity + relationship_style → love synthesis (etc.).  
**Next artifact (not this commit):** canonical question→facts map reusable across Profile, Today, compatibility, free-form questions.

Lexical repeat stability (Jaccard ~0.12–0.30) with stable facts/structure is **acceptable** — semantic stability, not verbatim clone.

---

## 0. Pipeline (target)

```text
spheres_projection_allowed(foundations)
  → build_sphere_synthesis_input (cues, style, identity slice, house cues?)
  → profile.spheres.synthesis.v1  (per sphere)
  → validate JSON + forbidden claims + distinctness
  → Snapshot.life_spheres[sphere]
```

| Layer | Owns |
|-------|------|
| Deterministic | eligibility · source selection · `sphere_cues` · house gate · JSON/schema · ban checks |
| LLM synthesis | user-facing how/need/risk/turns_on/turns_off/helps |
| Does **not** own | raw planet/sign interpretation from scratch; patterns; mission; Character helps[] |

---

## 1. Prompt passport table

| Field | Value |
|-------|--------|
| `prompt_id` | `profile.spheres.synthesis.v1` |
| `version` | `1.0.0` |
| `block_id` | `life_spheres` (one sphere per call) |
| `purpose` | Преобразовать **уже подготовленные** смысловые признаки + style/identity в практическую карту проявления **в одной сфере** |
| `user_question` | Per sphere — §2 |
| `generation_required` | **yes** (synthesis) |
| `generation_gate` | `spheres_projection_allowed` **and** non-empty `sphere_cues` for that sphere |
| `allowed_inputs` | identity_core, strengths, growth_zones, relevant_style, sphere_cues[], optional house_cues[] — all precomputed |
| `forbidden_inputs_in_prompt` | raw planet=sign pairs as the only cue; living/patterns; Today; system meta |
| `forbidden_output` | planet/sign/house names; system/LLM talk; «всегда/регулярно»; identity/style paraphrase; event forecasts |
| `expected_response` | JSON object with exactly 6 string fields (one sphere) |
| `on_reject` | retry once · else omit sphere · do not fill from projector as silent personal fact |
| `kitchen` | cue ids, trait/planet/sign used to build cues, prompt version, model, attempts |

---

## 2. Sphere contracts (love · money · decisions)

| sphere_id | Name (RU) | user_question | user_value | relevant_style |
|-----------|-----------|---------------|------------|----------------|
| `love` | Любовь | Как базовые особенности проявляются в близости? | Понять, как входит в близость, что нужно, где напряжение, один шаг | `relationship_style` |
| `money` | Деньги | Как базовые особенности проявляются в деньгах и ценности? | Понять отношение к ресурсу, риск, один практический фокус | `money_style` |
| `decisions` | Решения | Как базовые особенности проявляются в решениях? | Понять способ выбирать и один hygiene-шаг | `decision_style` |

### Field contract (same for all three)

| Field | Question the model must answer | Not |
|-------|-------------------------------|-----|
| `how` | Что человек **наблюдаемо** делает/показывает в этой сфере? (2 sentences) | Source labels; style paste |
| `need` | Какое **условие** помогает оставаться собой здесь? (1) | Abstract «гармония» |
| `risk` | Как сила/потребность **ломается** здесь? (1) | Longitudinal «всегда» |
| `turns_on` | Какая **конкретная ситуация** включает участие? (1) | Generic praise |
| `turns_off` | Какая ситуация **выключает**? (1) | Bare avoid-list |
| `helps` | **Один** выполнимый шаг для типичного напряжения (1, verb) | Global Character helps |

---

## 3. Input pack (`SphereSynthesisInputV0`)

```text
{
  sphere_id, sphere_name,
  user_question, user_value,
  identity_core, strengths[], growth_zones[],
  relevant_style,
  sphere_cues: [{id, text}],      # prepared semantic facts — no "Venus = Cancer"
  house_cues: [{id, text}] | [],  # only if houses_available
  locale
}
```

**Cue rules:** behavioral / situational; grounded in natal calc or styles; never only a glyph.  
Kitchen may store `planet`, `sign`, `trait_rule_id` used to **build** cues — not shown to the model as astrology homework.

---

## 4. Acceptance (synthesis)

1. All 6 fields present; length bounds (how ≥40; others ≥20; caps as projector).  
2. No planet/sign/house/ASC/system markers in output.  
3. No longitudinal markers without living.  
4. Not near-duplicate of identity_core or relevant_style (Jaccard / containment).  
5. Fields pairwise distinct (how≠need≠helps…).  
6. `helps` contains an action cue.  
7. Trace: prompt_id, version, cue ids, model, fingerprint of input pack.

---

## 5. Dual outcome

1. **Stable synthesis** matching this passport.  
2. **Omit sphere** if gate closed, cues empty, or validation fails after retry.

Forbidden: free fill to satisfy schema; silent projector overwrite presented as synthesis.

---

## 6. Relation to projector v0.2

| Artifact | Role after pivot |
|----------|------------------|
| `life_spheres_traits_v0` / cues builder | **Evidence → sphere_cues** (not final UI copy) |
| `life_spheres_style_buckets_v0` | Optional kitchen / cue sharpening — not user text |
| `life_spheres_projector_v0` | Baseline for A/B eval vs synthesis; not production SoT for copy |
| `profile.spheres.v1` | **Legacy** funnel prompt — replace with synthesis |

---

## 7. Eval slice (this stage)

| Check | Result (run `20260721T151429Z`, validator FP fix) |
|-------|-----------------------------------------------------|
| Cues for love/money/decisions on 8 cases | **8/8** (lsq-07 money/decisions = omit) |
| Synthesis validation | **8/8** after word-boundary bans |
| Contrast lsq-01 vs lsq-02 love | **PASS** (Jaccard 0.07) |
| Contrast lsq-03 vs lsq-04 love (same natal, styles) | **PASS** (Jaccard 0.21) |
| vs projector near-clone | **none** (mean Jaccard ≈ 0.02) |
| Repeat lexical stability (2 runs) | Low Jaccard (~0.12–0.30) — paraphrase variance; meaning holds in spot checks; not a reason to return to projector tables |
| Funnel wiring | **shipped** in `profile_disclosure_funnel_v0` — fail/omit, no projector copy fallback |
| Case A/B production capture | required proof after this wire |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-21 | Passport opened; pivot from deterministic-final-copy to synthesis-on-cues |
| 2026-07-21 | Prompt + cues + validator + eval harness; 8-case LLM run; registry id registered |
