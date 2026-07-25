# Day Scenario UI Preference B4

**Status:** LANDED (FE prefers scenario nests; not a full Today redesign)  
**Date:** 2026-07-25  
**Canon:** [DAY_SCENARIO_V1.md](../DAY_SCENARIO_V1.md)  
**Prior:** [DAY_SCENARIO_WIRE_PROJECTION_B3.md](./DAY_SCENARIO_WIRE_PROJECTION_B3.md)

## What landed

Frontend composition prefers B3 wire nests without rewriting Today layout:

| Surface | Preference |
|---------|------------|
| Types | `day_story.interpretive_chorus`, `day_story.day_scenario`, talisman `avoid_*` |
| Color guide | Scenario talisman name/note/avoid over morning celestial catalog why |
| Spine color card | Same talisman preference |
| Narrative | Chorus chapter after why; when chorus present, skip independent tarot/number symbol dump |
| Sphere focus | Domain lenses first; else scenario scenes |

## Out of scope

- Full chapter/UI redesign of Today
- `runtime_sot=true` / formula-bank return
- Profile UI

## Architecture impact

```markdown
## Architecture impact
- **SoT before (FE):** morning catalog color why; tarot/number often parallel chapters; domains-only spheres
- **SoT after (FE):** prefers day_scenario/interpretive_chorus/talisman when present; public slots still primary text when filled by B3
- **Public contract changed?** no — consume additive nests from B3
- **Migration required?** no
- **Canon updated?** yes — DAY_SCENARIO_V1 + this note
- **Backward compatible?** yes — missing nests → prior FE behavior
```
