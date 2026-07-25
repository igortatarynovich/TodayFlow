# Day Scenario Personalization C3.3a

**Status:** LANDED (evidence pack · depth modes · gate · downgrade; lifecycle unchanged)  
**Date:** 2026-07-25  
**Code:** `day_scenario_personalization_c33.py` · wired in `call_day_scenario_native_llm_c1`  
**Prompt:** `day-scenario-native-c3.3a`  
**Canon:** [DAY_SCENARIO_V1.md](../DAY_SCENARIO_V1.md)

## Architecture impact

```markdown
## Architecture impact
- **SoT before:** personalization = optional why_personal / natal prose; no depth contract;
  bad personal claims could ship or force full unavailable with editorial natal checks only
- **SoT after:** bounded personalization_evidence pack → depth mode (general|light|deep) →
  personalization gate → retry → downgrade to honest general OR reject story (leak) →
  then C3.1/C3.2 editorial gate
- **Public contract changed?** no — personalization_depth / traces are scenario-internal;
  not new required Today UI fields
- **Migration required?** no
- **Canon updated?** yes — this note + DAY_SCENARIO_V1 + tracker + C1 prompt version
- **Backward compatible?** yes — GET path unchanged; refresh LLM only
- **Lifecycle / UI:** unchanged
```

## Evidence pack (not raw Profile)

Built before prompt from interpretation claims + day_personal source flags:

| Field | Role |
|-------|------|
| `evidence_depth` | general / light_personalized / deep_personalized |
| `available_sources` | personal_astrology, human_design, … |
| `behavioral_tendencies` | id + label + confidence + source_refs |
| `sensitive_domains` | sphere hints |
| `supportive_resources` | compensating baselines |
| `natal_activations` | capped claims with evidence_refs |
| `confidence` | pack confidence |
| `evidence_refs` | allow-list for personal cites |

LLM input gets `personalization_evidence`; raw `day_personal` is stripped from the payload copy.

## Depth modes

| Mode | Allowed | Forbidden |
|------|---------|-----------|
| `general` | day facts only | «вы обычно», natal voice, habitual claims |
| `light_personalized` | why_personal, tone, one sphere, likely reaction | precise houses / ASC / natal activations |
| `deep_personalized` | forces, spheres, trap, action, intensity, natal | decorative-only (why_personal + natal alone) |

Depth is recorded on scenario + capture (`personalization_depth`, `editorial_meta`).

## Provenance traces

On conflict and each scene:

- `personalization_level`
- `personalization_reason`
- `personalization_evidence_refs`
- `general_fallback_available`

Deep also uses `habitual_force` / `required_movement` / `compensating_for` / `trap_pattern`.

## Defect codes

| Code | After retries |
|------|----------------|
| `PERSONALIZATION_CLAIM_WITHOUT_EVIDENCE` | downgrade general |
| `PERSONALIZATION_DEPTH_OVERREACH` | downgrade general |
| `PERSONALIZATION_DECORATIVE_ONLY` | downgrade general |
| `PERSONALIZATION_SCENES_UNCHANGED` | downgrade general |
| `PERSONALIZATION_GENERIC_ACTION` | downgrade general |
| `PERSONALIZATION_SPHERE_UNJUSTIFIED` | downgrade general |
| `PERSONALIZATION_CONFLICT_UNCHANGED` | downgrade general |
| `PERSONALIZATION_NATAL_OVERCLAIM` | downgrade general |
| `PERSONALIZATION_EVIDENCE_ORPHAN` | downgrade general |
| `PERSONALIZATION_PROFILE_FACT_LEAK` | **reject story** → unavailable |

Downgrade strips natal / personal claims / traces; **keeps** day conflict + scenes. Not Formula Bank rewrite.

## Pairwise fixtures

`tests/test_day_scenario_personalization_c33a.py` — same day skeleton; control / light / deep A / deep B packs; structural difference + evidence isolation.

## Out of scope (C3.3b+)

- Automatic ranking of all life spheres  
- Profile generation changes  
- UI depth indicator  
- Language polish  
- New personality sources  
- Long-term memory / lifecycle
