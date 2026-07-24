# Product Block — Six Questions (quality SoT)

**Status:** ACTIVE — главный критерий качества блока / экрана / генерации  
**Date:** 2026-07-22  
**Parents:** [PRODUCT_TRUTH_FIRST.md](./PRODUCT_TRUTH_FIRST.md) · [EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md](explainability/EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md) · [content/TODAYFLOW_VOICE_CANON.md](./content/TODAYFLOW_VOICE_CANON.md)  
**Profile application:** [PROFILE_PRODUCT_SURFACE_CANON.md](profile/PROFILE_PRODUCT_SURFACE_CANON.md) · [PROFILE_PRODUCT_JOURNEY_FORMS_V1.md](profile/PROFILE_PRODUCT_JOURNEY_FORMS_V1.md)  
**Engineering passport (ниже):** [audits/PROFILE_E2E_BLOCK_PASSPORT_TEMPLATE.md](./audits/PROFILE_E2E_BLOCK_PASSPORT_TEMPLATE.md)

> TodayFlow — не набор отдельных AI-генераций.  
> Каждый блок обязан быть объяснимым как шаг пользовательского пути.  
> **Нет убедительного ответа хотя бы на один из шести вопросов → убрать или переработать.**

Это **продуктовый** паспорт. Технический Freeze-паспорт (gate · prompt · schema) не заменяет его — дополняет вопросы 3–4.

---

## Шесть вопросов (обязательны)

| # | Вопрос | Подвопросы |
|---|--------|------------|
| **1** | **Зачем существует?** | Какую проблему пользователя решает? Если удалить блок — что человек потеряет? |
| **2** | **Почему именно эта информация?** | Почему эти данные, а не любые другие? Как они помогают сделать *следующий* шаг? |
| **3** | **Откуда взялось?** | Исходные данные · вычисления · промпты · правила · SoT. Полная трассировка. |
| **4** | **Почему можно доверять?** | Детерминизм · living evidence · независимые источники · явное разделение факт / интерпретация / adjacent context. |
| **5** | **Почему именно здесь?** | Почему этот экран и этот порядок? Какую когнитивную задачу решает *в этот момент* пути? |
| **6** | **К чему ведёт?** | Что человек делает после? Если никуда — блок лишний или не на своём месте. |

### Правило удаления

Перефраз предыдущего блока · красивый текст без потери при удалении · CTA без ценности · «ещё одна генерация» без нового этапа пути → **не полировать, удалить или слить**.

---

## Поля паспорта блока (карта продукта)

Один блок = одна строка / карточка паспорта. Не новый engine — документ + заполнение по мере экранов.

| Поле | Шесть вопросов |
|------|----------------|
| `purpose` / назначение | 1 |
| `user_job` / пользовательская задача | 1 · 5 |
| `why_this_info` | 2 |
| `inputs` / входные данные | 3 |
| `sot` | 3 |
| `formation` / механизм | 3 |
| `trust` / доказательство устойчивости | 4 |
| `why_here` / место в пути | 5 |
| `leads_to` / следующий шаг пути | 6 |
| `omit_when` | 1 · 4 (когда блока не должно быть) |

Карта продукта растёт **экран за экраном** (Product Truth First). Не заводить пустой реестр «на все модули». Первый заполненный срез — Profile journey (§ ниже).

---

## Profile journey — ответы на шесть вопросов

| Блок | 1 Зачем | 2 Почему эта info | 3 Откуда | 4 Доверие | 5 Почему здесь | 6 Куда ведёт |
|------|---------|-------------------|----------|-----------|----------------|--------------|
| **recognition_line** (+ name · visual) | Узнавание за ≤5 с — «это про меня» | Одна фраза поведения, отличающая ядро; не биография | calc archetype + identity `recognition_line` | calc label; line accepted by contract rules (≤120, no day/archetype echo) | Первый момент пути: shareable узнавание | → почему (trust) |
| **portrait_why_v0** | Снять «случайный AI» | selected_by ≠ influenced_by — честное происхождение имени vs расширение | life_path→archetype helper · sun/element/rhythm · natal angles when time | детерминизм; omit ASC/MC без времени | Сразу после узнавания: «откуда вывод» | → инсайт (новое) |
| **insight_nodes_v0** | От узнавания к закономерности | Один узел (trap/tension), не три списка | Snapshot strings + living notes; grounded_on = факты | living quotes = *adjacent context*, не proof-link v0; patterns gate | После «почему»: новое «не замечал» | → усилие |
| **effort_vector_v0** | Нужен следующий шаг после осознания | Только направление из выбранного node.help | `nodes[0].help` only | null если нет safe help / help≈insight; no LLM | После узла: действие, не ещё описание | → практика (bridge) |
| **bridge_line** | Объяснить, **зачем открыть Today сейчас** | Только логика продолжения пути — не совет и не day-forecast | kind выбранного node (+ living context flag) | детерминизм; не дублирует effort_vector; без императива | Конец Profile-пути | → Today |

Цепочка (линейная, проверяемая):

```text
recognition_line → portrait_why → insight_node → effort_vector → bridge_line → Today
```

Если `effort_vector` не добавляет нового действия относительно узла — блока нет (`null`).  
Если `bridge_line` отвечает на «что делать» или пустой CTA — блока нет / переписать.

---

## Связь с уже существующими канонами

| Канон | Что закрывает |
|-------|----------------|
| Explainable Computation | вопрос 3–4 (цепочка происхождения) |
| Product Truth First | нет источника → нет блока; экран за экраном |
| E2E Block Passport | вопрос 3–4 в инженерной форме (gate · prompt · schema) |
| Voice §0.05–0.06 | вопрос 6 (ценность шага; не kitchen) |
| Profile Journey Forms | вопросы 1–2 · 5–6 на поверхности Profile |

Six Questions **не отменяют** Freeze-паспорт — требуют, чтобы у блока был смысл в путешествии *до* и *после* технической стабильности.

---

## Порядок внедрения (без платформенного каркаса)

```text
1. Зафиксировать этот критерий (этот документ)
2. Держать заполненной карту Profile journey (§ выше) при каждом delta
3. Следующий экран после Profile Freeze (Today) — те же 6 вопросов на каждый блок
4. Не создавать registry/engine «Product Map Platform» без доказанной пользы
```

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-22 | v1.0 — Six Questions as product quality SoT; Profile journey first filled slice |
