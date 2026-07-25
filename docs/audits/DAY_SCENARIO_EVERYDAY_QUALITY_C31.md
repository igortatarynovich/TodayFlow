# Day Scenario Everyday Quality C3.1

**Status:** LANDED (editorial gate + everyday prompt rules; lifecycle unchanged)  
**Date:** 2026-07-25  
**Code:** `day_scenario_editorial_gate_c31.py` · wired in `call_day_scenario_native_llm_c1`  
**Prompt:** `day-scenario-native-c3.1`  
**Canon:** [DAY_SCENARIO_V1.md](../DAY_SCENARIO_V1.md) · [DAY_SCENARIO_NATIVE_LLM_C1.md](./DAY_SCENARIO_NATIVE_LLM_C1.md)

## Architecture impact

```markdown
## Architecture impact
- **SoT before:** native LLM accepted after schema validation only; abstract/universal
  scenes could ship as meaning
- **SoT after:** schema validate → editorial quality gate → retry with defect feedback
  (no formula rewrite) → on persistent critical fail: facts_only_unavailable
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this note + DAY_SCENARIO_V1 + tracker + C1 prompt version note
- **Backward compatible?** yes — deterministic GET path unchanged; gate applies on refresh LLM
- **Lifecycle:** unchanged (GET no Nebius)
```

## Scene quality bar

Each scene must include:

1. concrete domestic moment  
2. inner impulse  
3. outer situation  
4. choice between two strategies  
5. observable consequence  
6. action doable today  

Banned as sole content: «не торопитесь», «сохраняйте баланс», «слушайте себя», «избегайте конфликтов», «сделайте паузу».

## Defect codes (critical unless noted)

| Code | Meaning |
|------|---------|
| `SCENE_ABSTRACT` | no lived moment / sphere forecast |
| `SCENE_UNIVERSAL_ADVICE` | universal tip without concrete action |
| `SCENE_MISSING_EVERYDAY` | thin/missing everyday_example |
| `SCENE_CLONE` | near-duplicate scenes |
| `THESIS_ECHO` | thesis dumped across scenes |
| `ASTRO_JARGON_BARE` | astro term without human translation |
| `PSEUDO_DIAGNOSIS` | clinical / insulting psych labels |
| `CATEGORICAL_PROMISE` | inevitability claims |
| `NATAL_WITHOUT_EVIDENCE` | natal voice without evidence |
| `SCENE_MISSING_CHOICE` | soft — no opportunity/trap tension |
| `CHORUS_PARALLEL_ECHO` | soft — duplicate chorus voices |
| `AFFIRMATION_UNNATURAL` | fake-wellness affirmation |
| `BUREAUCRATIC` | soft — bureaucratic voice |

## Retry policy

1. Reject with `format_editorial_retry_feedback`  
2. Second attempt with defects listed  
3. Still failing → `None` → wire `facts_only_unavailable`  
**No** template overwrite of LLM prose.

## Capture / eval

- Attempt status `editorial_gate_reject` + defect codes  
- `editorial_score` / `editorial_defects` on accepted `editorial_meta`  
- Capture classes: `SCENE_QUALITY`, `CHORUS_QUALITY`, `LANGUAGE`

## Out of scope (later C3.x)

- C3.3b sphere selection / production pairwise eval  
- C3.5 multi-day eval harness pack  
- UI redesign

**Landed:** [DAY_SCENARIO_CHORUS_QUALITY_C32.md](./DAY_SCENARIO_CHORUS_QUALITY_C32.md) ·
[DAY_SCENARIO_PERSONALIZATION_C33A.md](./DAY_SCENARIO_PERSONALIZATION_C33A.md)
