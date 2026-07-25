# Day Scenario Chapters UI C2

**Status:** LANDED (FE story chapters from day_scenario; no lifecycle / GET change)  
**Date:** 2026-07-25  
**Code:** `todayScenarioChapters.ts` · hooked in `buildTodayDayNarrative` · `TodayPersonalizedProductSection`  
**Canon:** [DAY_SCENARIO_V1.md](../DAY_SCENARIO_V1.md)  
**Prior:** [DAY_SCENARIO_UI_PREFERENCE_B4.md](./DAY_SCENARIO_UI_PREFERENCE_B4.md) · [DAY_SCENARIO_NATIVE_LLM_C1.md](./DAY_SCENARIO_NATIVE_LLM_C1.md)

## Architecture impact

```markdown
## Architecture impact
- **SoT before (FE reading zone):** Day Map chapters from projected expect/trap/do slots
  (+ B4 chorus preference)
- **SoT after:** when day_scenario ready (conflict + scenes, not unavailable), reading zone
  composes five story chapters from scenario + interpretive_chorus + props;
  Day Map / legacy paths remain fallback
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — DAY_SCENARIO_V1 + this note + tracker
- **Backward compatible?** yes — missing/unavailable scenario → prior Day Map / legacy narrative
- **Lifecycle:** unchanged
```

## Chapter map

| # | Chapter id | Kicker | Source |
|---|------------|--------|--------|
| 1 | `opening` | Что изменилось сегодня | conflict (+ events_lead soft) |
| 2 | `chorus` | Почему именно так | interpretive_chorus |
| 3 | `scenes` | Где это проявится | scenes (+ opportunity/trap dual) |
| 4 | `supports` | Что поможет пройти день | scene actions + props/talisman |
| 5 | `vibe` | Чем закончится день | evening_closure / vibe_* |

Gate: `isDayScenarioReadyForChapters` — `interpretation_status !== unavailable`, conflict present, `scenes.length ≥ 1`.

## Out of scope

- Backend / LLM / GET-refresh lifecycle
- Profile / Tarot product flows
- Language polish pass
- Removing Day Map for non-scenario payloads
