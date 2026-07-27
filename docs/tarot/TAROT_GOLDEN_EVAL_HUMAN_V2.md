# Tarot Golden Eval — Human v2

**Status:** ACTIVE DRAFT (2026-07-26) — protocol + seed · **not** a full 20–30 labeled set yet  
**Phase:** Architecture Frozen / Editorial Phase  
**Extends:** [TAROT_GOLDEN_EVAL_V1.md](./TAROT_GOLDEN_EVAL_V1.md) (auto harness stays) · [TAROT_STACK_EDITORIAL_PHASE_2026-07-26.md](../audits/TAROT_STACK_EDITORIAL_PHASE_2026-07-26.md)  
**Schema:** [tarot_golden_eval_human_v2.schema.json](../schemas/tarot_golden_eval_human_v2.schema.json)  
**Seed fixture:** `backend/tests/fixtures/tarot_golden_eval_human_v2.json`

---

## Why v2

Auto Golden Eval v1 proves the **stack works** (shape · pass rate · anti-sameness).  
Human v2 asks whether the product **lets a person see themselves**.

Not a new engine. Not a new contract. Eval + editorial only.

## Target inventory

- **20–30** real questions (RU first; EN later)  
- Varied spreads (1 / 3 / choice / guidance)  
- Real model answers (capture from prod or live CLI)  
- Editor scores + optional second rater  

**Do not** invent 30 fake human labels in code.

## Three post-answer questions (required)

After reading the full answer, the reviewer (or user) answers:

| id | Question (RU) | Values |
|----|---------------|--------|
| `understood_symbols` | Понял ли ты, что карты хотят сказать? | `yes` · `partial` · `no` |
| `answered_my_question` | Получил ли ты ответ именно на свой вопрос? | `yes` · `partial` · `no` |
| `would_pay` | Заплатил бы ты за такой разбор? | `yes` · `partial` · `no` |

These three may outweigh another 100 automatic checks.

## Editor rubric (optional 1–5)

Reuse v1 ids when useful: `answered_question`, `clarity`, `story_not_card_list`, `symbolism_natural`, `practical_use`, `no_repetition`, `no_false_confidence`, `want_to_finish`.

Plus Editorial Phase voice flags (boolean notes, not architecture):

- `antithesis_formula` — saw «не X, а Y»  
- `sees_self` — person recognizes themselves  
- `warmth_without_mush` — warm without empty wellness  

## Case contract (minimal)

Each case stores:

- question · spread · cards (id + orientation + position)  
- answer blocks (symbols / story / answer / step — or captured `tarot_answer_v1` snapshot)  
- `prompt_version` · `model` · `captured_at`  
- `human` scores (three questions + optional rubric)  
- `editor_notes`  

## Seed

Case `hv2_work_direction_three` — owner live reading (work direction · Justice rev / 9 Wands / Queen Wands).  
Meaning **liked**; voice note: antithesis «не кричит, а греет» → fixed in prompt v1.7.

## Next

1. Capture 20–30 real Q+A into the fixture (append-only).  
2. Score with the three questions (+ optional rubric).  
3. Summarize yes/partial/no rates — drive Q3 wording, not new pipeline layers.

### Capture tooling (2026-07-27)

```bash
set -a && source .env && set +a
PYTHONPATH=backend/src backend/.venv/bin/python scripts/tarot_human_eval_capture_v2.py --write-fixture
```

- Writes live answers into `backend/tests/fixtures/tarot_golden_eval_human_v2.json` (**without** inventing `human` scores).  
- Scorecard: `docs/audits/TAROT_HUMAN_EVAL_V2_SCORECARD.md`  
- Capture dump: `docs/audits/TAROT_HUMAN_EVAL_V2_CAPTURE_*.json`
