# Profile as Canonical Identity — Downstream Consumption Audit

**Date:** 2026-07-21  
**Status:** ACTIVE — next stage after PR-4.1 CLOSED  
**Parent:** [PR4_PROFILE_CANON.md](../archive/PR4_PROFILE_CANON.md) · Umbrella [EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md](../explainability/EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md)  
**Related:** [PERSONAL_MODEL_CODE_COMPLIANCE_2026-07-21.md](./PERSONAL_MODEL_CODE_COMPLIANCE_2026-07-21.md) · [PROFILE_CONTENT_CANON_V1.md](../profile/PROFILE_CONTENT_CANON_V1.md)

> Goal: Profile / Snapshot is the **only** identity SoT. Downstream modules may add domain context («сегодня», «эта пара», «эта карта») but must **not** invent a new character arc without their own evidence chain.

---

## Architecture (current)

```text
facts (astro + numerology)
        ↓ publish
CoreProfile Snapshot  ← SoT
  person · astro · numerology · baseline
  profile_contract_v1 (portrait)
  interpretation (legacy shim)
  living (read-path)
        ↓
build_cached_or_baseline()
        ↓ (partial)
ExperienceSlice(today | compatibility | tarot)
```

---

## Consumer table

| Module | Entry points | Fields from Profile/Snapshot | Own personality meaning? | Risk |
|--------|--------------|------------------------------|--------------------------|------|
| **Profile UI** | `app/profile/page.tsx`, `profilePage/*` | Full `profile_contract_v1`, living, natal preview | No | Canonical portrait consumer |
| **Experience Contract** | `experience_contract_assembler_v0.py` | Thin: decision_style, identity_core, helps, strengths, life_mission, relationship_style proxies; life_path, sun_sign, living.summary | No (projects) | Omits money_style, growth_zones, life_spheres, patterns, moon/ASC |
| **Today narrative / day_story** | `today_narrative.py`, `day_story_wire_v1.py` | ExperienceSlice as user_core; natal_summary / sun_sign in why-astro fallbacks | Partial | Fallbacks re-explain via sign + natal_summary |
| **Morning ritual** | `morning_ritual.py` | Full core incl. legacy interpretation, baseline, daily_lenses | Partial | Horoscope fallback rebuilds scenarios from baseline+sign — bypasses Slice |
| **Interpretation orchestrator** | `interpretation_orchestrator.py` | baseline element/rhythm, life_path | Yes (deterministic) | Consistency ≠ portrait voice |
| **Compatibility** | `compatibility_engine.py`, content_v1 | Slice for personalized; DOB→life_path fallback; guest zodiac paths | Partial / Yes (guest) | Guest invents meaning without Snapshot (expected for guests if honesty depth marked) |
| **Tarot** | `tarot_reading_synthesis.py` | Slice styles/identity/motivation | No (synthesis) | Orchestrator consistency still baseline |
| **Guidance / Questions** | `guidance_profile_modules.py`, `questions.py` | Ad-hoc interpretation / baseline / learning_context — **not** Slice | Partial | Parallel SoI vs Profile screen |
| **Natal personalization** | `natal_chart_personalization.py` | interpretation, baseline lenses | Partial | Fallbacks from archetype when empty; ignores contract life_spheres |
| **Practices** | `api/practices.py`, FE practices | Display meta mostly | No | Low risk |
| **CUM** | `compact_user_model_v0.py` | person, astro, numerology, baseline, interpretation, natal_summary | Partial | Experiences rarely consume CUM; prefers legacy interpretation over contract |
| **Legacy explainers** | `core/user_context.py`, `*_explainer.py`, affirmations | Signs/DOB → personality context | Yes | Bypass Snapshot portrait if still on hot paths |

---

## Portrait fields unused by Experiences

`money_style` · `growth_zones` · `recurring_patterns` · `living_changes` · `life_spheres` · forming status/meta · most numerology beyond life_path · moon/ASC on Experience Contract · most `living.signal_profile` structure.

Either **project them via ExperienceSlice** (when a module needs them) or **stop treating unused fields as product promises** on other surfaces.

---

## Re-interpretation hotspots (severity)

| Hotspot | Severity |
|---------|----------|
| Morning / Guidance prefer baseline + legacy interpretation over contract | **High** |
| Legacy UserContext / explainers rebuild natal personality | **High** if on prod paths |
| Today FE prism from `interpretation` / sun_sign | Medium |
| Compat DOB→life_path when preferred missing | Medium (fallback) |
| Natal personalization archetype fallbacks | Medium |
| Baseline seed element×modality×life_path | Acceptable as **calc seed**, must not replace portrait claims |

---

## Next actions (ordered)

1. Route **Guidance + morning fallbacks** through `ExperienceSlice` (or expand allowlists) — kill parallel SoI.
2. Expand Experience Contract **only** for fields modules actually need; otherwise drop unused portrait promises from downstream prompts.
3. Gate / deprecate legacy UserContext personality assembly on hot paths.
4. Today FE: prefer contract / slice over legacy `interpretation` blocks.
5. Then — and only then — deepen natal **UI** organization on Profile (person first → sources → structured natal; max understanding, not max data). See [PR4_PROFILE_CANON.md](../archive/PR4_PROFILE_CANON.md) §3.1.

**Do not start C3 portrait quality work** until Experiences stop assembling competing personalities from signs/baseline.

---

## Verdict

- **Storage SoT:** healthy (Snapshot publish; read-path no portrait LLM).  
- **Interpretation SoT:** incomplete — Profile UI is rich; Experiences get a thin slice or ad-hoc baseline/legacy.  
- **Highest leverage:** unify Experience identity path on Snapshot/`profile_contract_v1`, then organize natal disclosure on Profile.
