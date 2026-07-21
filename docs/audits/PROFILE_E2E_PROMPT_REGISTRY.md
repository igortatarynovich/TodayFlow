# Profile E2E — Prompt Registry (passports)

**Stage:** [PROFILE_E2E_RECONSTRUCTION.md](../PROFILE_E2E_RECONSTRUCTION.md)  
**Block passport:** [PROFILE_E2E_BLOCK_PASSPORT_TEMPLATE.md](./PROFILE_E2E_BLOCK_PASSPORT_TEMPLATE.md)  
**life_spheres:** [PROFILE_E2E_BLOCK_PASSPORT_LIFE_SPHERES.md](./PROFILE_E2E_BLOCK_PASSPORT_LIFE_SPHERES.md) · [PROFILE_E2E_BLOCK_PASSPORT_SPHERES_SYNTHESIS.md](./PROFILE_E2E_BLOCK_PASSPORT_SPHERES_SYNTHESIS.md) · [PROFILE_LIFE_SPHERES_DETERMINISTIC_PROJECTOR_V0.md](./PROFILE_LIFE_SPHERES_DETERMINISTIC_PROJECTOR_V0.md)  
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
| Trigger (**gate**) | else: skip LLM · `reason=patterns_skipped_ineligible` · `recurring_patterns=[]` |
| **Debt (spheres coupling)** | Current funnel still **stops** after patterns skip/fail → spheres never start. Confirmed `GENERATION_GATE` defect on spheres control-flow (patterns gate itself is correct and stays). Target: continue to spheres / projector independently |
| Input | shared + identity + styles |
| System | patterns from **living/signals only**; mission + helps; text asks honesty if sparse |
| Expected | recurring_patterns[], living_changes, life_mission, helps[≥2] |
| **Architectural defect** | Block purpose = confirmed repeats only. Asking the model «не выдумывай» while `RESPONSE_SCHEMA` / `_patterns_ok` **require** filled patterns is a **GENERATION_GATE + RESPONSE_SCHEMA** defect — not «модель выдумала». |
| Snapshot | patterns, living_changes, life_mission, helps |
| UI | patterns → Character; mission → Direction; helps → Character; living_changes rarely surfaced |
| **Unique knowledge?** | Only with longitudinal evidence; otherwise **do not generate** (omit step) |

Passport target: [PROFILE_E2E_BLOCK_PASSPORT_TEMPLATE.md](./PROFILE_E2E_BLOCK_PASSPORT_TEMPLATE.md) § recurring_patterns.

---

## P4 · `profile.spheres.v1` — **LEGACY (not target content authority)**

| Field | Content |
|-------|---------|
| prompt_id | `profile.spheres.v1` |
| version | `1.0.0` |
| **Status** | **Legacy debt.** Must not be treated as target content authority for `life_spheres` |
| Trigger (current code) | after patterns success only — **accidental coupling**; see Case A report |
| Expected (legacy) | 9 spheres × how/need/risk/turns_on/turns_off/helps |
| Eval gap | review runner **skips** this step |
| Snapshot | `life_spheres` (today only if LLM step runs) |
| UI | Direction sphere cards; FE chart/DEFAULTS can compete (**dual source debt**) |
| Quality gates | identity echo into how; duplicate hows |
| **Target content** | **Superseded** by P4b synthesis — projector kept as A/B baseline / cue kitchen |
| **Future LLM** | See P4b (not a thin wording layer on projector prose) |
| **Unique knowledge?** | Legacy LLM step is **not** the unique-knowledge path |

---

## P4b · `profile.spheres.synthesis.v1` — **TARGET content authority**

| Field | Content |
|-------|---------|
| prompt_id | `profile.spheres.synthesis.v1` |
| version | `1.0.0` |
| **Status** | **Production-wired** via `life_spheres_synthesis_run_v0` in profile funnel |
| Passport | [PROFILE_E2E_BLOCK_PASSPORT_SPHERES_SYNTHESIS.md](./PROFILE_E2E_BLOCK_PASSPORT_SPHERES_SYNTHESIS.md) |
| Trigger | after identity/styles; IFF `spheres_projection_allowed` **and** non-empty `sphere_cues`; **independent of patterns** |
| Input | identity slice · relevant_style · prepared `sphere_cues` · optional house_cues |
| Expected | one sphere × how/need/risk/turns_on/turns_off/helps |
| Deterministic owns | eligibility · cue selection · house gate · JSON/ban validation |
| Must not | raw planet=sign as sole homework; invent without cues; patterns dependence |
| Eval | `run_life_spheres_synthesis_eval_v0.py` |

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
| spheres (legacy LLM) | — | do not use as SoT |
| spheres (cues) | prepared semantic facts from natal/styles | raw planet=sign dumps |
| spheres (synthesis) | practical manifestation map per field question | identity/style paste; kitchen astrology; generic filler |

Next: wire synthesis into funnel after Case A/B + UI checklist; keep projector for A/B until then.
