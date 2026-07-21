# Profile E2E — Prompt Registry (passports)

**Stage:** [PROFILE_E2E_RECONSTRUCTION.md](../PROFILE_E2E_RECONSTRUCTION.md)  
**Block passport:** [PROFILE_E2E_BLOCK_PASSPORT_TEMPLATE.md](./PROFILE_E2E_BLOCK_PASSPORT_TEMPLATE.md)  
**Date:** 2026-07-21 · **Source:** code + eval packs

> Unique-knowledge verdicts are **hypotheses** until production-faithful packs prove them.
>
> Mismatches are **architectural** (`PROMPT` / `RESPONSE_SCHEMA` / `GENERATION_GATE` / …). There is no «модель выдумала» diagnosis.

---

## Shared frame (all funnel steps)

| Field | Value |
|-------|--------|
| Frame builders | `prompts/common_v1.py` → `voice_block`, `profile_layers_block` |
| Concat | `profile_disclosure_v1._frame` |
| **Risk** | Voice block includes **Today day chain** («чего ждать → что делать → сферы сегодня») — wrong for static portrait |
| Voice bans | AI/LLM/algorithm meta-language (good); product-as-subject still needs Voice Canon §0 audit |

---

## P1 · `profile.identity.v1`

| Field | Content |
|-------|---------|
| prompt_id | `profile.identity.v1` |
| version | `1.0.0` (`registry_v1.py`) |
| Call site | `profile_disclosure_funnel_v0` step identity |
| Trigger | `publish_portrait=True` + rich quality mode |
| Input schema | shared: person, astro, numerology, baseline, living, locale, profile_hash |
| System | `identity_system(locale)` + frame |
| User | `{ shared, step: "identity" }` |
| Model params | policy-driven (eval: DeepSeek-V4-Pro, temp ~0.48, max_tokens 3200) |
| Expected JSON | `profile_funnel_identity_v0`: identity_core, strengths[3], growth_zones[3] |
| Parser | JSON extract + step validator (≥20 char identity, 3+3) |
| Retry | 1 on parse/schema fail |
| Fallback | step fail → funnel fail → forming shell |
| Forbidden claims | sun-sign passport only; Voice bans |
| Snapshot fields | `identity_core`, `strengths`, `growth_zones` |
| UI projections | Hero quote, Character strengthens/drains (via QuickMap), Evidence |
| **Unique knowledge?** | Yes if real synthesis; else sign cliché |

---

## P2 · `profile.styles.v1`

| Field | Content |
|-------|---------|
| prompt_id | `profile.styles.v1` |
| version | `1.0.0` |
| Trigger | after identity success |
| Input | shared + identity result |
| System | styles: relationship / money / decision; «не повторяй identity» |
| Expected | `relationship_style`, `money_style`, `decision_style` (≥12 chars) |
| Snapshot | same three fields |
| UI | decision_style → Character; relationship/money often **unused** on V2 surface / thin ExperienceSlice |
| **Unique knowledge?** | **Open** — must not rewrite identity with new adjectives |

---

## P3 · `profile.patterns.v1`

| Field | Content |
|-------|---------|
| prompt_id | `profile.patterns.v1` |
| version | `1.1.0` |
| Trigger (current) | after styles — **only if** `patterns_generation_allowed(pack)` (`source_depth` ≥ `profile_plus_checkins`) |
| Trigger (**gate**) | else: skip LLM · `reason=patterns_skipped_ineligible` · `recurring_patterns=[]` · spheres not started |
| Input | shared + identity + styles |
| System | patterns from **living/signals only**; mission + helps; text asks honesty if sparse |
| Expected | recurring_patterns[], living_changes, life_mission, helps[≥2] |
| **Architectural defect** | Block purpose = confirmed repeats only. Asking the model «не выдумывай» while `RESPONSE_SCHEMA` / `_patterns_ok` **require** filled patterns is a **GENERATION_GATE + RESPONSE_SCHEMA** defect — not «модель выдумала». |
| Snapshot | patterns, living_changes, life_mission, helps |
| UI | patterns → Character; mission → Direction; helps → Character; living_changes rarely surfaced |
| **Unique knowledge?** | Only with longitudinal evidence; otherwise **do not generate** (omit step) |

Passport target: [PROFILE_E2E_BLOCK_PASSPORT_TEMPLATE.md](./PROFILE_E2E_BLOCK_PASSPORT_TEMPLATE.md) § recurring_patterns.

---

## P4 · `profile.spheres.v1`

| Field | Content |
|-------|---------|
| prompt_id | `profile.spheres.v1` |
| version | `1.0.0` |
| Trigger | after patterns |
| Expected | 9 spheres × how/need/risk/turns_on/turns_off/helps |
| Eval gap | review runner **skips** this step |
| Snapshot | `life_spheres` |
| UI | Direction sphere cards (also natal house taxonomy can compete) |
| Quality gates | identity echo into how; duplicate hows |
| **Unique knowledge?** | **Suspect** — candidate for deterministic projection from natal+contract |

---

## P5 · Oneshot `_PROFILE_SYS_RU`

| Field | Content |
|-------|---------|
| prompt_id | *(unregistered string in `profile_contract_v1.py`)* |
| Trigger | `prefer_multi_step_funnels() == False` (economize) |
| System | single portrait JSON (full contract shape) |
| Snapshot | same `profile_contract_v1` |
| **Unique knowledge?** | Alternate path — must not diverge from funnel meaning |

---

## Logging gap (forensic)

Production `generation_logs` for Profile store:

- `prompt_text` ≈ `"profile_disclosure_funnel_v0"`  
- normalized final contract / meta  

**Missing:** per-step system, user, raw.  
Required for E2E: extend capture (eval or publisher) before blaming the model.

---

## Prompt unique-knowledge matrix (to prove)

| Step | Must add | Must not |
|------|----------|----------|
| identity | who in life | sign passport |
| styles | decision/relationship/money angles | paraphrase identity |
| patterns | evidence-backed repeats | invent from birth-only |
| spheres | sphere-specific how/need | copy identity into every how |

Next: run production-faithful pack and score this matrix per case.
