# Tarot Golden Dataset v1

**Статус:** ACTIVE (2026-07-25) — эталонные сценарии **без оценок**  
**Тип:** eval fixture / content QA  
**Связанные:** [TAROT_INTERPRETATION_ENGINE_V1.md](./TAROT_INTERPRETATION_ENGINE_V1.md) · [TAROT_QUESTION_ONTOLOGY_V1.md](./TAROT_QUESTION_ONTOLOGY_V1.md) · [TAROT_KNOWLEDGE_BASE_V1.md](./TAROT_KNOWLEDGE_BASE_V1.md)

---

## 0. Зачем

**Golden Dataset** ≠ **Golden Eval**.

| Artifact | Что это | Что не делает |
|----------|---------|----------------|
| **Dataset** | фиксированные сценарии: вопрос · профиль · карты · ожидаемый `question_type` | не ставит баллы |
| **Eval** | рубрикатор + прогон ответов по датасету | не определяет состав сценариев |

Датасет расширяется независимо от рубрикатора.

---

## 1. SoT

| Layer | Path |
|-------|------|
| Scenarios | `backend/tests/fixtures/tarot_golden_dataset_v1.json` |
| Schema | `docs/schemas/tarot_golden_dataset_v1.schema.json` |
| Runtime use | offline tests now · live LLM scoring later (Eval) |

Public `tarot_answer_v1` **не** меняется.

---

## 2. Scenario record

Обязательные поля:

- `id` · `label` · `question` · `concern_domain` · `spread_id`
- `cards[]` — фиксированный расклад (`card_id` · `orientation` · `position_id` · `title`)
- `profile` — короткий tint (experience-slice keys), не paste Profile
- `expect.question_type` — Ontology type, который должен классифицироваться

Опционально:

- `expect.domain` / `intent` / `decision_horizon`
- `expect.answer_shape` — структурные флаги для Eval (не 1–5)
- `tags` · `notes`

**Запрещено в датасете:** числовые scores · paid-worth · anti-sameness verdicts.

---

## 3. Coverage policy (v1 seed)

Минимум один сценарий на каждый `question_type` Ontology + отдельные кейсы:

- adjacent minors (Cups 8/9/10, Swords 8/9/10) — проверка Q1 uniqueness
- choice spread
- emotionally hard / vague open question

---

## 4. Acceptance

- [x] Schema + fixture landed
- [x] Offline tests: schema · ontology expect · pack builds · minors carry Q1 fields
- [ ] Golden Eval harness consumes this fixture (next)
- [ ] Live LLM scoring pass (Eval gate) — live r3 12/12 done; architecture stays Frozen / Editorial Phase
