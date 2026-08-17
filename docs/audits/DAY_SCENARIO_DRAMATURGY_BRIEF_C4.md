# Day Scenario Dramaturgy Brief C4

**Status:** LANDED (pre-LLM skeleton + protected user message + scenario-first UI)  
**Date:** 2026-07-26  
**Code:** `day_scenario_dramaturgy_brief_c4.py` · wired in `day_scenario_native_llm_c1` · FE `todayDaySpine` / `todayDayMap`  
**Canon:** [DAY_SCENARIO_V1.md](../DAY_SCENARIO_V1.md)  
**Prior:** [DAY_SCENARIO_NATIVE_LLM_C1.md](./DAY_SCENARIO_NATIVE_LLM_C1.md) · C3.3b sphere selection

## Architecture impact

```markdown
## Architecture impact
- **SoT before:** Native LLM received a large flat user JSON (interpretation + full
  day_events_pack + day_thesis slogan). Truncation at 14k often cut ranked drivers;
  model latched onto registry day_thesis.label_ru as the plot. UI hero preferred
  day_thesis slogan; ritual unlock copy competed with scenario props.
- **SoT after:** Deterministic dramaturgy_brief (ranked must_dramatize + scene_slots +
  act_iii_registry_label demoted) is built *before* LLM and placed first in the user
  message (protected from truncation). Prompt version day-scenario-native-c4.0.
  conflict.title must come from facts, not slogan paraphrase. UI prefers ready
  day_scenario.conflict.short_name; ritual unlock hint suppressed when scenario ready.
- **Public contract changed?** no — same day_scenario / day_story projection fields
- **Migration required?** no — refresh/force_rebuild picks up new prompt; old caches
  keep prior generation_source until refresh
- **Canon updated?** yes — DAY_SCENARIO_V1 + this note + tracker
- **Backward compatible?** yes — GET without rebuild unchanged; FE falls back to
  day_thesis when scenario nest not ready
```

## Pipeline (enforced)

```text
Facts (event pack) → Dramaturgy brief (C4) → Native LLM conflict/scenes
  → Deterministic props → B5 projector → UI
```

`day_thesis` / `act_iii_registry_label` = Act III registry seed **only**, not the story.

**Entity status (LOCKED 2026-08-15):** Brief **не** Meaning SoT и не planner. Serialization adapter (protected prefix) для legacy native call.  
**Meaning SoT:** только [TODAY_CONTENT_PIPELINE_V1](../today/TODAY_CONTENT_PIPELINE_V1.md). Target: Brief сериализует **Global Day Profile** → LLM #1, не «scenario after the call».

## Brief contract (`day_dramaturgy_brief_c4`)

| Field | Role |
|-------|------|
| `must_dramatize` | Top ranked driver facts the story must use |
| `scene_slots` | Preferred spheres + driver hooks |
| `sphere_candidates` | From C3.3b selection |
| `chorus_seeds` | Card / number / head_topic |
| `act_iii_registry_label` | Slogan demoted; `role=registry_seed_only_not_plot` |

## Out of scope (later)

- Auto-promoting quality gates (still C3.6 observe)
- Human golden batch C3.6.2 labeling
- Changing GET Nebius policy
- Formula-bank overwrite of scenes
