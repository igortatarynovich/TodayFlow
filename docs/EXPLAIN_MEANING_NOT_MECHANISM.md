# Explain Meaning, Not Mechanism

**Статус:** принято — **сквозное правило** TodayFlow (Profile · Today · Guidance · Symbolic · Gamification · все surfaces).  
**Версия:** 1.1 (2026-06-01).  
**Владелец:** Product + Engineering.

**North star:**

> **Explain meaning, never explain internal decisioning.**  
> *(RU: Объясняй смысл для человека — никогда механизм принятия решения.)*

**Жёсткое правило:**

> **System reasoning never becomes product content.**  
> *(RU: Механизм принятия решения **никогда** не показывается пользователю.)*

**Продуктовый запрет (voice):**

> Пользователь **никогда** не должен чувствовать, что его **анализирует алгоритм**.  
> Режим продукта — **«я изучаю себя»**, не **«меня оценивает система»**.

**Umbrella:** [EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md](./EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md) — кухня обязана существовать; этот документ задаёт, что из неё **не** становится user-facing механизмом.

**Связь:** [PROFILE_SCREEN_MASTER.md](./PROFILE_SCREEN_MASTER.md) · [USER_MODEL_TARGET_STATE.md](./USER_MODEL_TARGET_STATE.md) §0.1 · [INTERPRETATION_LAYER_AND_REFERENCE.md](./INTERPRETATION_LAYER_AND_REFERENCE.md) · [TODAY_SCREEN_V1_CANON.md](./TODAY_SCREEN_V1_CANON.md) §3 · [EXPLAINABLE_INTERPRETATION.md](./EXPLAINABLE_INTERPRETATION.md).

---

## 0. Две разные вещи (не путать)

| | **Внутренняя объяснимость** | **Пользовательский слой** |
|--|----------------------------|---------------------------|
| **Для кого** | Инженерия · QA · analytics · audit | Пользователь |
| **Вопрос** | Почему **алгоритм** выбрал X? | **Что это значит для меня?** |
| **Где живёт** | Logs · trace · datasets · admin | Product UI · Narrative · Insight |
| **В UI** | ❌ **никогда** | ✅ |

### Системе нужно знать (internal only)

selection trace · rank · score · confidence · signal · pattern candidate · progression signal · eligibility · registry · completeness metrics · causal decision tree · blocked/filtered candidates.

### Пользователю нужно знать (product)

**только смысловой слой** — см. §1.

---

## 1. Четыре допустимых типа copy (единственные)

В продукте существуют **только** эти категории. Любой новый текст классифицируется в одну из них или **не публикуется**.

| Тип | Роль | Примеры |
|-----|------|---------|
| **Факт** | Нельзя оспорить · узнаваемый якорь | «Твой знак — Лев.» · «Число жизненного пути — 7.» · «Сегодня карта дня — Отшельник.» |
| **Интерпретация** | Смысл для человека · без mechanism | «Тебе важно понимать смысл своих действий.» · «Ты быстрее восстанавливаешься через уединение.» · «В отношениях для тебя важна эмоциональная безопасность.» |
| **Наблюдение** | Паттерн времени · без «мы обнаружили» | «Последние дни были более активными.» · «Этот месяц выглядит насыщеннее предыдущего.» · «Ты чаще завершаешь начатое в первой половине недели.» |
| **Приглашение к размышлению** | Мягкий CTA · не директива системы | «Возможно, сегодня стоит уделить внимание…» · «Интересно понаблюдать…» · «Обрати внимание…» |

**Marker** (archetype · strength · watchout) — **факт или интерпретация**, не «результат rule set».

**Рекомендация / предупреждение Today** — интерпретация или приглашение; **не** «система рекомендует».

---

## 2. Запрещённые формулировки (продуктовый ban list)

### 2.1 «Система / алгоритм / мы определили»

| ❌ Запрещено | Почему |
|-------------|--------|
| «Система знает тебя на 60%.» | CRM-ощущение · mechanism |
| «Система считает, что…» | Алгоритм вместо self-discovery |
| «Мы определили, что…» | Платформа как судья |
| «Алгоритм обнаружил…» | Разрушает магию |
| «На основе твоих данных система решила…» | Audit language |
| «Система рекомендует…» | → интерпретация или приглашение |
| «Потому что AI так решил» | No meaning |

**Замена:** второе лицо · факт · интерпретация · наблюдение · приглашение — **без субъекта «система»**.

### 2.2 Технический прогресс (Profile · Gamification · Evolution)

| ❌ Запрещено | ✅ Продуктовая метафора *(не эзотерика)* |
|-------------|------------------------------------------|
| «Профиль заполнен на 43%.» | «Глубина профиля» · «Уровень раскрытия» |
| «Собрано 17% данных.» | «Карта становится яснее» |
| «Получено 12 сигналов.» | «Новые грани открыты» |
| «Profile completeness» | «Путь становится понятнее» |
| «+50 XP» · «Level 5 unlocked» | Milestone **смыслом**, не валютой |

**Граница:** метафора **конкретная и спокойная** — не «космическая энергия пробудилась». См. [USER_MODEL_TARGET_STATE.md](./USER_MODEL_TARGET_STATE.md) §0.1.

### 2.3 Internal vocabulary — **никогда** в product UI

`confidence` · `score` · `rank` · `signal` · `pattern candidate` · `progression signal` · `eligibility` · `trace` · `registry` · `completeness` · `weight` · `rule id` · `candidate` · `hypothesis` *(as label)* · `debug_trace`.

---

## 3. Profile — живая история, не CRM

**Ощущение экрана:**

> Пользователь **постепенно открывает новые слои** своего профиля — **не** заполняет CRM-карточку самого себя.

| ❌ CRM / engine | ✅ Unveiling layers |
|-----------------|---------------------|
| «Заполни поля профиля» | Interest entries: «Кто я», «Мои числа»… |
| «Добавь данные для точности» | «Новая грань открыта» |
| Completeness bar | «Глубина профиля» / discrete milestones |
| Derived traits registry | Markers как **интерпретации** |

Layout — [PROFILE_SCREEN_MASTER.md](./PROFILE_SCREEN_MASTER.md) §4.1 (interest navigation).

---

## 4. Примеры по surface

### Today · Theme — ✅

> Сегодня хороший день для завершения начатого. Число дня усиливает концентрацию, а карта указывает на важность завершения циклов.

### Today — ❌

> Мы выбрали эту тему, потому что score дисциплины = 0.73, association rule 14 победило 22.

### Profile · Identity — ✅

| Слой | Пример |
|------|--------|
| Facts | Овен · Life path 7 |
| Markers | Архетип «Исследователь» · Сильные: focus, depth |
| Narrative | «Ты склонен искать глубину; опора — в ясных границах» |

### Profile — ❌

> Архетип из rule set #17; confidence 0.82; typology aggregated from 8 factors.

### Progress / Gamification — ✅

> «Карта становится яснее» · «Открыта новая грань — отношения» · «Путь становится понятнее после месяца практик»

### Progress — ❌

> «Система знает тебя на 68%» · «17 signals collected» · «Pattern candidate promoted»

---

## 5. Граница с соседними канонами

| Канон | Роль |
|-------|------|
| [PROFILE_SCREEN_MASTER.md](./PROFILE_SCREEN_MASTER.md) | Foundation vs Narrative — оба **без** mechanism |
| [INTERPRETATION_LAYER_AND_REFERENCE.md](./INTERPRETATION_LAYER_AND_REFERENCE.md) | Reference → meaning; не trace в UI |
| [DAY_CONTEXT_V0.md](./DAY_CONTEXT_V0.md) | `debug_trace` — internal only |
| L4 Interpretation | Never strategic conclusions **as facts** |

**Insight (Today):** «почему так» = **смысл** (луна · число · контекст) — не «почему selector проголосовал».

---

## 6. Куда писать internal reasoning

| Арtefact | Аудитория |
|----------|-----------|
| `profile_selector.debug_trace` | engineering |
| Request/Response Records (AMLL) | learning pipeline |
| Evaluation datasets | QA |
| Admin / debug | staff only |

**Acceptance test:** «Можно ли процитировать copy **без** system/score/signal/%/algorithm/registry?» Если нет — **FAIL**.

---

## 7. Checklist для фичи / copy / API field

- [ ] Copy — только §1 (факт · интерпретация · наблюдение · приглашение)  
- [ ] Нет субъекта «система» / «алгоритм» / «мы определили»  
- [ ] Нет §2.3 internal vocabulary в user-visible strings  
- [ ] Progress — метафора §2.2, не проценты данных  
- [ ] Profile ощущается как **раскрытие слоёв**, не CRM  
- [ ] web + iOS + Android **паритет**  

---

## 8. Anti-patterns

| Anti-pattern | Почему |
|--------------|--------|
| «Explainability UI» для пользователя | Алгоритм вместо self-discovery |
| Confidence % в product | Mechanism · rarely calibrated |
| «Система знает тебя на X%» | Мгновенный CRM-mode |
| Debug toggle in user settings | Leak path |
| Copy from `debug_trace` | Immediate FAIL |
| Gamification as data collection meter | Wrong motivation frame |

---

## 9. Changelog

- **1.1 (2026-06-01)** — §1 four copy types; §2 ban list + gamification voice; §3 Profile unveiling; progress metaphor.
- **1.0 (2026-06-01)** — Foundation vs mechanism; trace/score ban.

---

*Bump version on scope change. Any new surface must pass §1–§7 before ship.*
