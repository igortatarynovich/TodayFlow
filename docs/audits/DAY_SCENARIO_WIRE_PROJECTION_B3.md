# Day Scenario Wire Projection B3

**Status:** SUPERSEDED for meaning policy by [DAY_SCENARIO_RUNTIME_SOT_B5.md](./DAY_SCENARIO_RUNTIME_SOT_B5.md) (B3 fill-empty / keep-LLM retired)  
**Date:** 2026-07-25  
**Code:** `day_scenario_project_v1.py` · hooked in `day_story_wire_v1._build_day_story_record`  
**Canon:** [DAY_SCENARIO_V1.md](../DAY_SCENARIO_V1.md)

## Architecture impact

```markdown
## Architecture impact
- **SoT before:** day_story LLM/fallback slots; color = celestial date preset + catalog why
- **SoT after (projected fields):** day_scenario_v1 → day_story slots; color/affirm/domains-fill/thesis
  from scenario; LLM prose kept when present; unavailable recovered from scenes when possible
- **Public contract changed?** additive — optional `day_story.day_scenario`, `day_story.interpretive_chorus`,
  talisman.avoid_* ; existing required fields unchanged
- **Migration required?** no (additive nests)
- **Canon updated?** yes — this note + DAY_SCENARIO_V1
- **Backward compatible?** yes — old clients ignore new nests; FE color guide may still read morning
  until B4 prefers scenario talisman → [DAY_SCENARIO_UI_PREFERENCE_B4.md](./DAY_SCENARIO_UI_PREFERENCE_B4.md)
```

## Projection map

| Public field | Scenario source |
|--------------|-----------------|
| `expect` | conflict + primary scene (fill if empty / unavailable) |
| `trap` | primary scene.trap |
| `do` / `primary_action` / `today_move` | goals[0] or recommended_action |
| `avoid` | primary scene.do_not |
| `domains.*` | scenes → wire lenses (fill empty only) |
| `talisman.color` / note / avoid | props.color / avoid_color |
| `practice_recommendation` | props.affirmations[0] |
| `day_thesis` / `primary_conflict` | conflict |
| `events_lead` | foundation drivers |
| `interpretive_chorus` | chorus voices |
| `day_scenario` | full nest (`runtime_sot: true` for projected meaning) |

## Legacy paths that no longer set meaning (after projection)

- Celestial date-preset color **catalog why** as user recommendation (seed only; scenario color wins on `talisman`)
- Formula bank runtime prose (still QA-only)
- Independent tarot/numerology “second forecast” on Today (chorus explains one conflict)

## Missing scenes

Attach scenario meta; **do not invent** expect/trap/do. If story was `unavailable`, it stays unavailable (`runtime_source=scenario_meta_only`).

## `interpretation_unavailable`

1. Build fallback facts-only (`unavailable`).  
2. Project scenario.  
3. If scenes exist → fill editorial → status **`ok`**, `editorial.runtime_source=day_scenario_v1`, `recovered_from_unavailable=true`.  
4. If no scenes → remain **`unavailable`** with scenario meta.

## Lifecycle

Unchanged: GET still `force_rebuild=False` (no Nebius). Projection is deterministic — no LLM.
