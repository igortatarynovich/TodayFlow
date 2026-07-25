# Day Scenario Chorus Quality C3.2

**Status:** LANDED (chorus causal-chain gate + prompt; lifecycle unchanged)  
**Date:** 2026-07-25  
**Code:** `day_scenario_editorial_gate_c31.py` (C3.2 chorus section) · `day_scenario_native_llm_c1.py`  
**Prompt:** `day-scenario-native-c3.2`  
**Canon:** [DAY_SCENARIO_V1.md](../DAY_SCENARIO_V1.md) · [DAY_SCENARIO_EVERYDAY_QUALITY_C31.md](./DAY_SCENARIO_EVERYDAY_QUALITY_C31.md)

## Architecture impact

```markdown
## Architecture impact
- **SoT before:** chorus voices could pass as four near-parallel mini-forecasts after C3.1 scene gate
- **SoT after:** same editorial gate enforces one causal line — astrology→env, card→archetype,
  number→tempo, natal→personal — with conflict_id binding; critical fail → retry → unavailable
- **Public contract changed?** no (optional conflict_id on chorus rows; not a public JSON required field)
- **Migration required?** no
- **Canon updated?** yes — this note + DAY_SCENARIO_V1 + tracker + C1 prompt version
- **Backward compatible?** yes — normalize fills conflict_id from conflict.title when missing
- **Lifecycle / UI:** unchanged
```

## Causal chorus roles

| Voice | Job |
|-------|-----|
| astrology | external environment / sky factor |
| day_card (tarot) | archetype of reaction |
| day_number | tempo / way through the conflict |
| natal | personal vulnerability or resource (evidence only) |

Every voice must carry `conflict_id` (slug of conflict title) + `link_to_conflict`.

## Defect codes (critical)

| Code | Meaning |
|------|---------|
| `CHORUS_PARALLEL_FORECAST` | unbound voice or parallel mini-forecast |
| `CHORUS_SEMANTIC_DUPLICATION` | near-duplicate paragraphs / term-swap |
| `CHORUS_ROLE_DRIFT` | voice doing another voice's job |
| `CHORUS_UNTRANSLATED_JARGON` | astro term without human translation |
| `CHORUS_NATAL_WITHOUT_EVIDENCE` | natal voice without natal evidence |

Retry uses existing `format_editorial_retry_feedback` — **no** formula rewrite.

## Out of scope

- C3.3b sphere selection / production pairwise eval  
- C3.5 eval pack  
- UI / lifecycle / public contract changes
