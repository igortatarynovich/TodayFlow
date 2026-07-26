# Tarot Golden Eval — live report #3 · 2026-07-26

**Mode:** live · **Dataset:** `tarot_golden_dataset_v1` (12)  
**Machine report:** [TAROT_GOLDEN_EVAL_LIVE_2026-07-26_r3.json](./TAROT_GOLDEN_EVAL_LIVE_2026-07-26_r3.json)  
**Prior:** [#1](./TAROT_GOLDEN_EVAL_LIVE_2026-07-25.md) 7/12 · [#2](./TAROT_GOLDEN_EVAL_LIVE_2026-07-26.md) 11/12  
**Canon:** [TAROT_GOLDEN_EVAL_V1.md](../tarot/TAROT_GOLDEN_EVAL_V1.md)

## Verdict

**Freeze lift gate: YES** (`freeze_lift_ready=true`) — **LLM 12/12**.

| Gate | Result |
|------|--------|
| pack_pass | 12/12 |
| llm_pass | **12/12** (100%) |
| critical shape | pass |
| anti-sameness | pass (~0.031) |
| rubric_mean | 4.0 |

## Ops context

- Prod backend redeployed with Tarot `background` timeout (45s) + no JSON→plain retry on ReadTimeout.
- Live eval CLI: `LLM_HTTP_TIMEOUT_SECONDS=120` / background 180.
- One scenario retried past `clean_failed:question_story` then passed (attempts still limited).
- Fallback provider: **not** wired (owner deferred).

## Prod smoke (same deploy)

- `POST /tarot/spread/context/public` choice 6-card: HTTP 200 · ~10.5s · `synthesis_mode=tarot_llm_v1` · `synthesis_status=ok`.

## Next

1. **Owner:** accept freeze lift (yes/no).
2. Continue Q3 editorial polish only if owner wants further wording work.
3. Fallback provider — later, when purchased.
