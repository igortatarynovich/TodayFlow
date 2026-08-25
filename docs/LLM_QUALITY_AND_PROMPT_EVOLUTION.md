# LLM Quality & Prompt Evolution

**Status:** active canon (2026-07)  
**Related:** [DAY_ENGINE_AND_COHERENCE.md](./DAY_ENGINE_AND_COHERENCE.md) §2.1 · [API_MEMORY_AND_LEARNING_LAYER.md](./API_MEMORY_AND_LEARNING_LAYER.md)  
**Product core (TARGET):** [PRODUCT_GENERATION_CONTRACTS.md](./PRODUCT_GENERATION_CONTRACTS.md) — Input/Output Schema · Rules · deps; промпт лишь реализация.

## Shift

Platform default is no longer token scarcity. Generation quality and multi-step meaning chains win over AMLL economize.

**Product shift (2026-07-22):** главный актив — библиотека **контрактов генерации**; `registry_v1.py` / тексты промптов — сменяемый executor.

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
# K2.6 lives on us-central1; K3 on eu-west2 (separate NEBIUS_COMPLEX_BASE_URL).
NEBIUS_BASE_URL=https://api.tokenfactory.us-central1.nebius.com/v1/
NEBIUS_COMPLEX_BASE_URL=https://api.tokenfactory.eu-west2.nebius.com/v1/
NEBIUS_MODEL=moonshotai/Kimi-K2.6
NEBIUS_COMPLEX_MODEL=moonshotai/Kimi-K3
NEBIUS_FALLBACK_MODEL=
LLM_STREAM_COMPLETIONS=1
LLM_STREAM_READ_TIMEOUT_SECONDS=120
```

**Model routing (2026-08-14):** Primary / day / prewarm / routine = **Kimi-K2.6** on `us-central1` (`NEBIUS_MODEL`, `resolve_default_chat_model`). **Kimi-K3** on `eu-west2` (`NEBIUS_COMPLEX_MODEL` + `NEBIUS_COMPLEX_BASE_URL`, `resolve_complex_chat_model`) only for multi-step portrait / natal ops where quality delta is product-visible and the call is user-justified:

| Uses K2.6 (`us-central1`) | Uses K3 (`eu-west2`) |
|-----------|-------------------|
| native day_story C1, day_flow windows, today narrative, guide/spheres funnels | CE Stage 2–4 LLM, profile disclosure funnel, natal decode depth |

Empty `NEBIUS_COMPLEX_MODEL` → complex path falls back to primary. Streaming required for Moonshot thinking models. Empty `NEBIUS_FALLBACK_MODEL` = no silent DeepSeek hop. Global `api.tokenfactory.nebius.com` hosts both models but K3 TTFT there was ~160s — keep regional split.

Equivalent manual wiring:

```bash
OPENAI_BASE_URL=https://api.tokenfactory.eu-west2.nebius.com/v1/
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

## AI COGS (per-request usage)

Every provider call in `llm_openai_compatible` emits one `llm_usage_v1` line:

`feature → model → input_tokens → output_tokens → reasoning_tokens → cached_tokens → latency_ms → estimated_cost_usd → user_id / request_id / operation_id`

- **Billed output:** `output_tokens` = provider `completion_tokens` (reasoning already inside). `reasoning_tokens` / `content_tokens` are breakdown only — never added twice to cost.
- **`operation_id`:** one UUID per product operation (`today.generate`, `today.narrative`, profile/natal/CE/tarot…). Nested retries and child calls inherit it. HTTP `request_id` is fallback grouping only.
- **Retry metadata:** `attempt`, `retry_reason` (`empty_content` | `parse_failed` | `gate_retry` | `json_mode_fallback` | `model_fallback` | …), plus booleans `parse_failed` / `empty_content` / `gate_retry`.
- **`trigger`:** `user` | `prewarm` | `eval` | `script` | `background`. HTTP middleware sets `user`; prewarm/enrichment set their own; evals/scripts inferred from argv or `LLM_TRIGGER`.
- Streaming Kimi requests `stream_options.include_usage`.
- Optional JSONL: `LLM_USAGE_LOG_PATH=/tmp/todayflow_llm_usage.jsonl`
- Report (feature × trigger × model × retry_reason + top-20 `operation_id`):

```bash
docker compose -f docker-compose.prod.yml logs backend --since 24h \
  | PYTHONPATH=backend/src backend/.venv/bin/python backend/scripts/report_llm_cogs.py --stdin
```

This is ops instrumentation, not a generation SoT.

## Cost Containment (router SoT, 2026-08-25)

Every provider call is: **request → policy → budget check → provider/model → usage accounting**.

A feature cannot grant itself 16k K3 output. Caps live in `llm_cost_guard_v1`, applied in `llm_openai_compatible._create_chat_collect`. Call-site `max_tokens=` is a request, not authority.

| Gate | Rule |
|------|------|
| K3 allowlist | Only `natal.decode`, `ce.stage2`, `ce.stage3`, `ce.stage4`. Recurring daily (`today.*`, prewarm) is never K3. |
| Today output | First attempt ≤ 1400 completion tokens; **retry** ≤ 600 (not a second full budget). |
| Natal/CE output | ≤ 2500 first / 900 retry. |
| Tarot | ≤ 1200 / 500. User-triggered, own cap. |
| Tenant USD | `LLM_DAILY_USD_CEILING` (default **$5** UTC day, whole environment). |
| Over budget | **Downgrade** to `LLM_DOWNGRADE_MODEL` (Qwen) if the cheap worst-case still fits; else **deny** (no provider call). Never retry the expensive model. |
| 402 / billing | `billing_suspended` trips the daily ceiling. No Token Factory fallback. |
| Prewarm | RFC 2606 `@example.com` excluded from production prewarm candidates. |
| Usage | Every provider call emits `llm_usage_v1` (ok, empty, timeout, deny, retry, thinking). JSONL: `LLM_USAGE_LOG_PATH`. Ledger: `LLM_SPEND_LEDGER_PATH`. |

```bash
LLM_COST_GUARD=1
LLM_DAILY_USD_CEILING=5
LLM_DOWNGRADE_MODEL=Qwen/Qwen3-30B-A3B-Instruct-2507
LLM_USAGE_LOG_PATH=/DATA/ops/llm_usage.jsonl
LLM_SPEND_LEDGER_PATH=/DATA/ops/llm_spend.json
```

`LLM_COST_GUARD=0` restores legacy thinking floors (K3 16k / K2.6 4k). Do not use in production.

### Unit economics (targets — measure before scaling)

Previous **$5 / 100 users / month** is **retired**. It assumed a cheap non-thinking model and one short completion/day. It is not a forecast of the current stack.

`$0.50–0.90 / MAU / month` is a **product goal after measurement**, not a router guarantee.

**Do not degrade Kimi** on natal / CE / paid synthesis until [COMPUTE_LIFECYCLE_AND_ARTIFACT_ECONOMICS_V1.md](./COMPUTE_LIFECYCLE_AND_ARTIFACT_ECONOMICS_V1.md) is implemented. First delete meaningless calls (GET/login/prompt-hash/Global×user/prewarm-as-MAU). Then measure one real lifecycle. Router caps stay as a floor, not as a quality cut.

Principle: calculate once → IL compose → persist → reuse → LLM only where personalization adds value. Core subscription compute vs premium (Tarot/deep compat) vs engineering (force rebuild — not MAU).

| Operation | Frequency (cost model) | Target cost | Notes |
|-----------|------------------------|-------------|--------|
| Natal / Character initial | 1× per user | $0.05–0.20 | K3 allowlisted; still capped |
| Natal refresh | rare / ops | $0.05–0.20 | Ops `ops_force` only; GET never rebuilds |
| Global Day | **1× per calendar day**, shared | amortized over DAU | Cost model. **Current I0 still generates Global per user** — that is implementation debt, not this pass. Do not treat 100 DAU as 100 Global LLM calls in the scaled model. |
| Personal Day | ≤1× / user / day | < $0.005–0.01 | Today class cap 1400 |
| Tarot | user-triggered | own budget | |
| Retries | exception | ≈ 0 in healthy runtime | Retry cap, not a full budget |

**24–48h measurement (next):** 1 real profile. Record `llm_usage_v1` for initialization + 30 Today opens + real retries + Tarot/on-demand. That series is 1 MAU COGS. Scale 100 / 1 000 / 10 000 from **that**, not from the retired $5 figure.

Report:

```bash
docker compose -f docker-compose.prod.yml logs backend --since 24h \
  | PYTHONPATH=backend/src backend/.venv/bin/python backend/scripts/report_llm_cogs.py --stdin
# JSONL (survives recreate):
PYTHONPATH=backend/src backend/.venv/bin/python backend/scripts/report_llm_cogs.py \
  --jsonl DATA/ops/llm_usage.jsonl
```

Code: `todayflow_backend.core.llm_cost_guard_v1`.

## Rollback

```bash
LLM_QUALITY_MODE=economize
```

Tight token tables + no child/profile multi-step funnels. **Does not** disable the cost guard. To disable the router (not recommended):

```bash
LLM_COST_GUARD=0
```
