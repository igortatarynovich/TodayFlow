# TODAY_SELF_VERIFICATION_V0 — H5 (Language)

**Статус:** `CALIBRATION_HYPOTHESIS` — candidate; не gate, не код.  
**Версия:** 0.1 (2026-06-23)  
**Родитель:** [TODAY_LANGUAGE_V1.md](today-language/TODAY_LANGUAGE_V1.md) · editorial quality stack  

**Связь:** [TODAY_H4_VALIDATION_V0.md](./TODAY_H4_VALIDATION_V0.md) · [TODAY_INTERNAL_PATTERNS_V0.md](./TODAY_INTERNAL_PATTERNS_V0.md) · [TODAY_ANCHOR_TYPES_V0.md](./TODAY_ANCHOR_TYPES_V0.md)

**Нумерация:** **H5 (Language)** = Self-Verification. В [TODAY_INTERNAL_PATTERNS_V0.md](./TODAY_INTERNAL_PATTERNS_V0.md) **IPL-H5…H7** — отдельный трек (pattern selection engine), не путать.

---

## Зачем (после H4 sign-off)

H4 **поддержана** как редакционное правило, но **не** как полная модель данных.

**H4 (редакция):** «Сначала наблюдаемое поведение, потом вывод» — хорошо для правки Class G.

**H4 (модель):** не объясняет все сильные примеры — delayed message, postponed conversation, open expectation **без** observable action пользователя.

---

## HYPOTHESIS H5 — Self-Verification

> **Хороший текст содержит элемент, который человек может быстро проверить на собственном опыте** — без необходимости принимать интерпретацию автора.

Не обязательно **наблюдаемое действие**. Обязательно **проверяемость**.

### Принцип генерации (candidate)

> **Не заставляй пользователя соглашаться с твоей интерпретацией. Покажи ему что-то, что он может узнать сам.**

Объединяет (если подтвердится):

- Internal Patterns (Class R)
- Core Scenes (`delayed_message`, `postponed_conversation`, …)
- Anchors (AT-003 object + AT-006 internal, AT-001 scene с проверяемым состоянием)

**H4** = частный случай H5, где проверка идёт через **observable behavior**.

---

## Типы self-verification *(candidate taxonomy)*

| type | Пример | Проверка |
|------|--------|----------|
| `observable_behavior` | «Вы уже неделю откладываете отчёт» | да / нет |
| `observable_behavior` | «Перечитываете сообщение несколько раз» | да / нет |
| `temporal_state` | «Пытаетесь успеть всё сразу» | да / нет |
| `open_loop` | «Разговор, который давно откладываете» | есть / нет |
| `expectation` | «Когда вы уже решили, что ответа не будет» | да / нет |
| `interpretive_label` | «Вам сложно доверять людям» | **нет** — нужна трактовка автора |

---

## Контрпримеры H4-only (сильные без observable action)

| Текст | Что работает | H4 | H5 |
|-------|--------------|----|----|
| «Кто-то может написать, когда вы уже решили, что ответа не будет» | **expectation** / отпускание | ❌ нет action | ✅ проверяемо |
| «Разговор, который откладывали, может снова напомнить о себе» | **open_loop** / незавершённость | ❌ | ✅ |
| «Вы избегаете близости» | интерпретация | ❌ | ❌ |

---

## Editorial sign-off stack (2026-06-23)

### H4 — Observable Pattern

| | |
|---|---|
| **Status** | **SUPPORTED** (preliminary editorial) |
| **Claim** | Observable (Class R) patterns стабильно сильнее interpretive (Class G) |
| **Limitation** | H4 **не** объясняет все strong examples; observable behavior — **один вид** сильных паттернов |
| **Role** | **Editorial rule** + Class R/G taxonomy — не root data model |
| **Evidence** | [TODAY_H4_VALIDATION_V0.json](./datasets/TODAY_H4_VALIDATION_V0.json) — 10/10 R keep+exemplar, 10/10 G rewrite/reject |

### H5 — Self-Verification

| | |
|---|---|
| **Status** | **CANDIDATE** — priority validation after H4 sign-off |
| **Claim** | Работают элементы, которые пользователь **самостоятельно подтверждает** без интерпретации автора |
| **Relation to H4** | H4 ⊆ H5 (observable = один тип self-verification) |
| **Next** | Разметить strong calibration examples (`cal-018`, delayed_message, postponed_conversation) полем `verification_type` — не bulk dataset |

---

## Поля для следующей validation (H5 set)

| Поле | Зачем |
|------|--------|
| `self_verifiable` | да / нет |
| `verification_type` | observable_behavior · temporal_state · open_loop · expectation · interpretive_label |
| `interpretation_required` | legacy H4 field; true ⟹ usually not self_verifiable |
| `editorial_decision` | keep / rewrite / reject / exemplar |

**TL-1 BLOCKED.** H5 validation → затем generation principle в канон; IPL engine (IPL-H5…) — параллельный трек.

---

## Changelog

| Дата | Изменение |
|------|-----------|
| 2026-06-23 | v0.1 — H5 candidate; H4 SUPPORTED + limitation; unifies anchors/scenes/IP |
