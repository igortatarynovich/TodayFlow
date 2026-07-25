# Tarot Question Ontology v1

**Статус:** ACTIVE (2026-07-25) — content SoT for Context Pack · **Interpretation Stack v1 frozen** ([engine](./TAROT_INTERPRETATION_ENGINE_V1.md))  
**Тип:** reference / interpretation instructions (не user-facing prose)  
**Владелец:** Product + Backend  
**Связанные:** [TAROT_INTERPRETATION_ENGINE_V1.md](./TAROT_INTERPRETATION_ENGINE_V1.md) · [TAROT_POSITION_SEMANTICS_V1.md](./TAROT_POSITION_SEMANTICS_V1.md) · [TAROT_KNOWLEDGE_BASE_V1.md](./TAROT_KNOWLEDGE_BASE_V1.md)

---

## 0. Зачем

Ontology отвечает не «какие слова в запросе», а:

> **Какого типа решение пользователь пытается получить от расклада?**

KB = что значит карта.  
Position Semantics = как читать карту в позиции.  
**Question Ontology = какую логику ответа требует вопрос.**

Один универсальный LLM prompt получает:

```
question ontology + position semantics + card knowledge + profile tint
```

**Не** отдельный финальный prompt на каждый тип вопроса.

---

## 1. Axes

| Axis | Values |
|------|--------|
| `question_type` | `choice` · `relationship_state` · `relationship_intent` · `work_decision` · `money_decision` · `conflict` · `self_state` · `direction` · `timing_readiness` · `open_reflection` |
| `domain` | `work` · `relationship` · `money` · `self` · `family` · `creative` · `general` |
| `intent` | `understand` · `choose` · `act` · `clarify` · `prepare` |
| `decision_horizon` | `near_term` · `mid_term` · `open` |

Пример (смена работы):

```yaml
question_type: choice
domain: work
intent: choose
decision_horizon: near_term
```

---

## 2. SoT

| Слой | Путь |
|------|------|
| Type library | `DATA/reference/tarot/question_ontology_v1/types.json` |
| Classifier | `backend/.../data/tarot_question_ontology_v1.py` |
| Pack projection | pack root `question_ontology` |
| Integration set | `backend/tests/fixtures/tarot_question_ontology_integration_v1.json` |

Public `tarot_answer_v1` unchanged.

---

## 3. Pack shape (`question_ontology`)

```yaml
question_ontology:
  question_type: choice
  domain: work
  intent: choose
  decision_horizon: near_term
  central_task: …
  direct_answer_means: …
  must_show: […]          # различия / сравнения, которые нужны
  allowed_specificity: …
  must_not_claim: […]
  next_step_kind: …
```

Это **инструкция интерпретации**, не готовый вывод.

---

## 4. Type highlights

| Type | Прямой ответ | Жёсткий запрет |
|------|--------------|----------------|
| `choice` | сравнение вариантов + ключевое различие | выдуманная гарантия победителя |
| `relationship_intent` | динамика / сигналы / возможная мотивация | мысли другого как факт |
| `timing_readiness` | готовность / неготовность момента | точная дата / «через N дней» |
| `open_reflection` | фокус внимания + один честный угол | псевдо-точный прогноз из тумана |

---

## 5. Acceptance

- [x] Types + pack instructions landed
- [x] Single prompt v1.4 reads `question_ontology` (no per-type prompt branch)
- [x] Integration set 10–12 offline classification checks
- [ ] Owner live text pass after Ontology (before heavy minors deepen)
- [ ] Minors deepen after Ontology checks hold
