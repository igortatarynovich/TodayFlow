# Tarot Interpretation Stack v1 — Architecture Frozen / Editorial Phase

**Date:** 2026-07-26  
**Owner verdict:** full architecture freeze lift **declined**; status changed to **Editorial Phase**  
**Canon:** [TAROT_INTERPRETATION_ENGINE_V1.md](../tarot/TAROT_INTERPRETATION_ENGINE_V1.md) · [TAROT_GOLDEN_EVAL_V1.md](../tarot/TAROT_GOLDEN_EVAL_V1.md)

---

## Why not full lift

Harness green (live r3 **12/12**) means the **foundation stage is complete**, not that the architecture should reopen for new layers. Freeze stays to **protect** the stack from premature change.

## Accepted now

| Item | Status |
|------|--------|
| Timeout fix + background LLM budget | accepted · deployed |
| No JSON→plain retry on ReadTimeout | accepted |
| Q3 wording (`tarot-interpretation-v1.6`) | accepted |
| Live Golden Eval r3 (12/12) | accepted |
| Production deployment | accepted |
| Tarot-only reliability commit `da03d22` | accepted |

## Status label

**Tarot Interpretation Stack v1 — Architecture Frozen / Editorial Phase**

Not `freeze lifted`. Not a return to open architecture work.

## Allowed without RFC

- Knowledge Base editorial data  
- Prompt wording  
- Editorial data / fixtures  
- Evaluation (auto + human)  
- Timeout / reliability hardening  

## Requires RFC

- New engine layers  
- New public contracts / `tarot_answer_v1` fields  
- New pipeline stages or extra LLM hops  
- New spread types / Tarot UI as primary track  

## Next (product eyes — not new engine)

Human **Golden Eval v2** — protocol: [TAROT_GOLDEN_EVAL_HUMAN_V2.md](../tarot/TAROT_GOLDEN_EVAL_HUMAN_V2.md) · seed fixture `tarot_golden_eval_human_v2.json` (1 owner case).

- **20–30** real questions  
- varied spreads  
- real model answers  
- editor scores  

After each answer, three questions:

1. Понял ли ты, что карты хотят сказать?  
2. Получил ли ты ответ именно на свой вопрос?  
3. Заплатил бы ты за такой разбор?  

**Q3 voice (2026-07-26):** avoid rhetorical «не X, а Y» (owner example: «не кричит, а греет») — `tarot-interpretation-v1.7` + gate `antithesis_formula`.

Fallback LLM provider: **deferred** until owner purchases and connects one.
