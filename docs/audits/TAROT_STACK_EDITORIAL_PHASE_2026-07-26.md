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

### Analytical voice v1.8 (2026-07-27)

Owner: texts must feel rigorous, not faux-important.  
Prompt `tarot-interpretation-v1.8`: pattern → cost → answer → testable step; metaphor only if it unpacks into behavior; ban empty solemnity formulas in clean gate.

### Practitioner + friend persona v1.9 (2026-07-27)

Owner: LLM always speaks as one experienced wise practitioner and friend  
(tarot · numerology · astrology · psychology · sexology-when-intimacy · friend).  
SoT: [TODAYFLOW_VOICE_CANON.md](../content/TODAYFLOW_VOICE_CANON.md) §1 v1.7 · Tarot prompt `tarot-interpretation-v1.9`.  
Not clinical diagnosis; not naming the professions in user text.

Hard reject is **narrow**: short parallel **verbs/adjectives** («не кричит, а греет»).  
Prompt still bans broader «это не …, а …». Broad regex was rejecting most live answers (~1/12 then ~6/12).

### Paid deepen chooser (UI, Editorial Phase)

On Tarot result, **paid / trial** users get **Углубить тему** with 3–4 choices (money practical / intimacy & sex / work / boundaries).

- **Guest** → signup teaser  
- **Auth free** → pricing teaser (`/pricing`)  
- **Paid / trial** (`lite`|`pro`, `is_paid`, `active`|`trialing`) → unlock chooser  

Reuses question-first flow via `/tarot?concern=&refine=&question=&source=deepen` — **no** new LLM hop, contract, or ontology domain. Intimacy/sex is a **relationships** refine. Soft UI gate only (no hard Tarot paid BE gate yet).

### Human eval next

- real model answers (13 cases in fixture)  
- editor scores  

After each answer, three questions:

1. Понял ли ты, что карты хотят сказать?  
2. Получил ли ты ответ именно на свой вопрос?  
3. Заплатил бы ты за такой разбор?  

**Q3 voice (2026-07-26):** avoid rhetorical «не X, а Y» (owner example: «не кричит, а греет») — `tarot-interpretation-v1.7` + gate `antithesis_formula` (narrowed 2026-07-27).

Fallback LLM provider: **deferred** until owner purchases and connects one.
