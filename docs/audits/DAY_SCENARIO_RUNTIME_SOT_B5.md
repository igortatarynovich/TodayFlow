# Day Scenario Runtime SoT B5

**Status:** LANDED (exclusive meaning SoT; lifecycle GET/refresh unchanged)  
**Date:** 2026-07-25  
**Code:** `day_scenario_v1.py` · `day_scenario_project_v1.py` · `day_story_wire_v1.py` · `day_story_v1.py` (unavailable wipe)  
**Canon:** [DAY_SCENARIO_V1.md](../DAY_SCENARIO_V1.md)  
**Prior:** [DAY_SCENARIO_WIRE_PROJECTION_B3.md](./DAY_SCENARIO_WIRE_PROJECTION_B3.md) · [DAY_SCENARIO_UI_PREFERENCE_B4.md](./DAY_SCENARIO_UI_PREFERENCE_B4.md)

## Architecture impact

```markdown
## Architecture impact
- **SoT before:** hybrid — scenario overlay + fill-empty; LLM expect/trap/do kept when present;
  domains LLM prose preserved; catalog/morning could still seed competing meaning on cache
- **SoT after:** day_scenario_v1 exclusive meaning SoT when scenes valid;
  legacy day_story slots = projections only; no llm_with_scenario_overlay;
  missing/invalid scenes → interpretation_status=unavailable + meaning slots stripped
  (facts_only_unavailable / scenario_meta_only)
- **Public contract changed?** semantics — expect/trap/do/avoid/domains/talisman always from
  scenario when ready; unavailable blanks talisman/practice on contract; additive nests unchanged
- **Migration required?** no version bump of today_contract_v1; old caches re-projected on serve
- **Canon updated?** yes — DAY_SCENARIO_V1 + this note
- **Backward compatible?** yes for field presence — old clients still get filled legacy slots via
  projector; they no longer see parallel LLM meaning when scenario is ready
```

## Runtime policy

Only two meaning modes:

| Mode | Condition | User surfaces |
|------|-----------|---------------|
| **scenario** | valid conflict + scenes | ok; all meaning = projections |
| **facts_only_unavailable** | no scenario / empty scenes | unavailable; sky/facts + honest message; no legacy editorial |

No hybrid «scenario + legacy editorial fallback».

## Overwrite map

Projector **always** overwrites (when ready): theme, primary_conflict, events_lead, expect, trap, do, avoid, story, domains, talisman, practice_recommendation, development_point, interpretive_chorus, day_scenario.

## Provenance (minimum)

`editorial.slot_provenance` + field `provenance` where present:

- `source_kind` = `day_scenario_v1`
- `origin_scene_id`
- `origin_conflict_id`
- `evidence_refs`
- `projection_version` = `day_scenario_project_v1.b5`

## Lifecycle

Unchanged: GET still `force_rebuild=False` (no Nebius). Exclusive projection is deterministic on build + cache hit + wire serve.

## Out of scope (next)

- Fuller scene UI composition
- LLM prompt rewrite to emit scenario-native JSON only (LLM output still discarded as SoT by projector)
- `runtime_sot=false` dual engine
