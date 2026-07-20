# LLM Quality & Prompt Evolution

**Status:** active canon (2026-07)  
**Related:** [DAY_ENGINE_AND_COHERENCE.md](./DAY_ENGINE_AND_COHERENCE.md) §2.1 · [API_MEMORY_AND_LEARNING_LAYER.md](./API_MEMORY_AND_LEARNING_LAYER.md)

## Shift

Platform default is no longer token scarcity. Generation quality and multi-step meaning chains win over AMLL economize.

| Mode | Env | Behavior |
|------|-----|----------|
| **rich** (default) | `LLM_QUALITY_MODE=rich` | Generous `max_tokens`, full context packs, standard model tier for all Today surfaces, multi-step disclosure funnels |
| **economize** | `LLM_QUALITY_MODE=economize` | Legacy tight caps, cheap tiers for spheres/evening, clipped slices |

Code: `todayflow_backend.services.llm_quality_policy_v1`.

## Nebius Token Factory

OpenAI-compatible client:

```bash
LLM_PROVIDER=nebius
NEBIUS_API_KEY=...
NEBIUS_BASE_URL=https://api.tokenfactory.nebius.com/v1/
NEBIUS_MODEL=deepseek-ai/DeepSeek-V4-Pro
```

Equivalent manual wiring:

```bash
OPENAI_BASE_URL=https://api.tokenfactory.nebius.com/v1/
OPENAI_API_KEY=$NEBIUS_API_KEY
LLM_DEFAULT_MODEL=<model_id>
```

## Disclosure chain (API requests)

### Today — guide (existing DE-13)

1. Interpretation  
2. Core text  
3. Satellites  

### Today — child surfaces (new)

Each of `day_layer` / `spheres` / `evening` / `deepen` runs **2 API calls** when `rich`:

1. Personalize / map / reflect / expand  
2. Render UI JSON  

Fallback: monolith system prompt in `today_narrative.py` if a funnel step fails.

### Profile (profile-contract-v3)

Four LLM steps, one shared normalized input pack:

1. Identity (`identity_core` + strengths + growth_zones)  
2. Styles (relationship / money / decision)  
3. Patterns (recurring + living_changes + life_mission + helps)  
4. Spheres (9 × how/need/risk/turns_on/turns_off/helps)  

**DoD gates (automated):** strict required fields + quality (no duplicate sentences / identity echo / generic phrases) + light consistency; fallback is neutral `forming` (never chart/template scaffold); per-prompt versions + model/temp/max_tokens in `generation_meta`; hash lock + snapshot cache so parallel page opens coalesce.

**Still open (manual):** sample 20–30 real DeepSeek-V4-Pro portraits for live voice vs structure-fill.

## Prompt registry

Versioned prompts live under `todayflow_backend/prompts/`:

- `common_v1.py` — product voice + Day Engine chain  
- `day_disclosure_v1.py` — per-step day prompts  
- `profile_disclosure_v1.py` — profile layers  
- `registry_v1.py` — `prompt_id` → version + builder  

**Evolution rule:** change prompt text → bump that prompt’s `version` in the registry → learning/`generation_logs` stay attributable.

## Logging

`POST /today/narrative` `input_payload` includes:

- `llm_quality_policy` — mode snapshot  
- `disclosure_funnel` — per-surface step timings / prompt versions (child surfaces)  
- existing `guide_funnel_*` fields for guide  

## Rollback

```bash
LLM_QUALITY_MODE=economize
```

Restores legacy token tables and disables child/profile multi-step funnels (guide funnel still available).
