# Tarot Position Semantics v1

**Статус:** ACTIVE (2026-07-25) — content SoT for Context Pack  
**Тип:** reference / interpretation instructions (не user-facing prose)  
**Владелец:** Product + Backend  
**Связанные:** [TAROT_INTERPRETATION_ENGINE_V1.md](./TAROT_INTERPRETATION_ENGINE_V1.md) · [TAROT_KNOWLEDGE_BASE_V1.md](./TAROT_KNOWLEDGE_BASE_V1.md)

---

## 0. Зачем

KB отвечает: *что потенциально значит карта?*  
Position Semantics отвечает: *как именно читать эту карту в этой позиции?*

Одна и та же карта (напр. Шут) должна раскрываться по-разному:

| Роль | Фокус |
|------|--------|
| `risk` | импульсивность, недооценка последствий |
| `resource` / `gain` | открытость, свобода от старого сценария |
| `next_step` | небольшой эксперимент без требования полной гарантии |
| `outcome` | начало нового цикла, ещё не сформированный результат |

Без этого богатый KB используется слишком обобщённо.

---

## 1. SoT

| Слой | Путь |
|------|------|
| Role library | `DATA/reference/tarot/position_semantics_v1/roles.json` |
| Position → role map | same file `position_role_map` + heuristic fallback in loader |
| Pack projection | `tarot_interpretation_engine_v1` → per-card `position_semantics` |
| User prose | LLM only |

**Не:** готовые фразы позиции · отдельные ветки генерации по раскладу · новые поля `tarot_answer_v1` · UI.

---

## 2. Role record

| Field | Meaning |
|-------|---------|
| `role_id` | стабильный id (`risk`, `next_step`, …) |
| `purpose` | зачем позиция в раскладе |
| `answers_question` | на какой вопрос отвечает |
| `extract_from_card` | что извлечь из символики карты |
| `do_not` | запреты для LLM в этой роли |
| `result_type` | ожидаемый тип результата (код) |
| `short_instruction` | одна строка для компактного напоминания |

### Result types

`resource_gain` · `concrete_risk` · `hidden_cause` · `concrete_action` · `likely_outcome` · `time_context` · `advice_frame` · `warning_signal` · `consideration` · `focus_lens` · `relational_signal` · `support_factor` · `nuance` · `neutral_read`

---

## 3. Pack shape (per card)

```yaml
position_role: next_step          # role_id
position_role_instruction: "…"   # short_instruction (compat)
position_semantics:
  role_id: next_step
  purpose: …
  answers_question: …
  extract_from_card: …
  do_not: […]
  result_type: concrete_action
```

Public `tarot_answer_v1` unchanged.

---

## 4. Acceptance

- [x] Role library covers owner list (gain/resource, risk/blocks, hidden, next_step, outcome, past/present/future, advice, warning, …)
- [x] Live spread position_ids map to roles (choice / triad / guidance family)
- [x] Pack carries full `position_semantics` facts
- [x] Prompt reads `position_semantics` (v1.3)
- [ ] Owner live scoring after Position + Ontology
