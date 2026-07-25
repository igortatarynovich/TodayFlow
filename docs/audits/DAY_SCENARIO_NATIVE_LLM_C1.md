# Day Scenario Native LLM C1

**Status:** LANDED (native LLM schema + wire; lifecycle GET/refresh unchanged)  
**Date:** 2026-07-25  
**Code:** `day_scenario_native_llm_c1.py` · hooked in `day_story_wire_v1` on `force_rebuild`  
**Canon:** [DAY_SCENARIO_V1.md](../DAY_SCENARIO_V1.md)  
**Prior:** [DAY_SCENARIO_RUNTIME_SOT_B5.md](./DAY_SCENARIO_RUNTIME_SOT_B5.md)

## Architecture impact

```markdown
## Architecture impact
- **SoT before:** LLM generated legacy day_story slots (expect/trap/do/…); B5 projector
  discarded them as meaning and rebuilt/overwrote from deterministic or hybrid scenario
- **SoT after:** on refresh/force_rebuild, LLM returns native day_scenario JSON
  (chorus · conflict · scenes · prop_material); deterministic props from scenes;
  B5 projector adapts to public contract only
- **Public contract changed?** no — legacy fields remain projections
- **Migration required?** cache semantics — records without `day_scenario.generation_source`
  (`native_llm_c1` | `deterministic_engine_b5`) → facts_only_unavailable on GET;
  refresh creates native scenario; **no** reconstruct from legacy expect/trap
- **Canon updated?** yes — DAY_SCENARIO_V1 + this note + lifecycle note + tracker
- **Backward compatible?** field shapes yes; old meaning caches without marker show unavailable
  until refresh
- **Lifecycle:** unchanged — GET `force_rebuild=False` (no Nebius); refresh may call LLM
```

## Pipeline

```text
facts → native LLM scenario → validate/normalize → deterministic props → B5 projector → public contract
```

GET (no LLM): facts → deterministic `build_day_scenario_v1` → projector.

LLM fail after retry: `facts_only_unavailable` — **no** legacy LLM schema fallback.

## Native schema (`day_scenario_native_llm_c1`)

- `interpretive_chorus` (astrology / day_card / day_number / natal)
- `conflict` (title, forces, why_today, why_personal, driver_refs)
- `scenes` (2–4; each linked to conflict)
- `prop_material` (candidates only — final color/goals/affirm from engine)
- `generation_notes` (diagnostics only)

Forbidden legacy keys: expect, trap, do, avoid, domains, talisman, story, theme, …

## Prompt version

`day-scenario-native-c3.3b` — personalization contract + justified sphere selection.  
Prior: `c3.3a` · `c3.2` · `c3.1` · `c1.0`.  
Legacy `day-story-v1.10-no-formula-runtime` remains eval/compare only — **not** runtime SoT.

See [DAY_SCENARIO_EVERYDAY_QUALITY_C31.md](./DAY_SCENARIO_EVERYDAY_QUALITY_C31.md) ·
[DAY_SCENARIO_CHORUS_QUALITY_C32.md](./DAY_SCENARIO_CHORUS_QUALITY_C32.md) ·
[DAY_SCENARIO_PERSONALIZATION_C33A.md](./DAY_SCENARIO_PERSONALIZATION_C33A.md) ·
[DAY_SCENARIO_SPHERE_SELECTION_C33B.md](./DAY_SCENARIO_SPHERE_SELECTION_C33B.md).

## Cache migration

| Cache payload | GET behavior |
|---------------|--------------|
| Has `generation_source` + ready scenes | Re-project stored scenario (deterministic) |
| Missing marker (pre-C1) | `facts_only_unavailable` — no invent from expect/trap |
| Refresh | Native LLM (if configured) or deterministic on GET miss |

## Out of scope (later)

- Changing LLM call count / GET Nebius
- Profile / Tarot product flows
- Formula-bank rewrite of failed editorial output

**Landed later:** C2 chapters UI · C3.1 everyday editorial gate · C3.2 chorus causal chain · C3.3a personalization contract · C3.3b sphere selection.
