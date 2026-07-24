# Human Decision Model v1 (HDM)

**Статус:** `ACCEPTED` — канон **долгосрочной модели человека** для TodayFlow.  
**Версия:** 1.0 (2026-06-23)  
**Владелец:** Product + Intelligence (PIL / UKM)

**Это не:** Profile screen · анкета onboarding · гороскоп · mood journal.

**Это:** **модель принятия решений** — что система **пытается узнать** о человеке за месяцы использования и как **уменьшает неопределённость** по каждому измерению.

**Связь:**

| Документ | Роль |
|----------|------|
| [PERSONAL_INTELLIGENCE_MODEL_V1.md](pim/PERSONAL_INTELLIGENCE_MODEL_V1.md) | **PIM — центральный артефакт** (4 слоя) |
| [USER_MODEL_TARGET_STATE.md](pim/USER_MODEL_TARGET_STATE.md) | CUM = compact export PIM |
| [INTENT_MODEL_V1.md](./INTENT_MODEL_V1.md) | **Подграф PIM** — история намерений |
| [USER_KNOWLEDGE_MODEL.md](pim/USER_KNOWLEDGE_MODEL.md) | Knowledge Atom — единица PIM |
| [KNOWLEDGE_ACQUISITION_AND_SIGNAL_POLICY.md](./KNOWLEDGE_ACQUISITION_AND_SIGNAL_POLICY.md) | Signal → PIM |
| [TODAY_SCREEN_V1_CANON.md](./TODAY_SCREEN_V1_CANON.md) | Today = Experience; Goal → PIM |

**HDM** — **подграф PIM** (`traits`, `decision_style`, `stress_patterns`, `motivations`), не отдельный центр.  
**Доказательная база HDM** в первую очередь из [Intent Model](./INTENT_MODEL_V1.md) (цели, outcomes, post-goal behavior), не из mood polls.

**North star (главный вопрос продукта):**

> **Что именно система пытается узнать о человеке за месяцы использования?**

Ответ: **не «всё о пользователе»**, а **конкретные измерения принятия решений** ниже — с измеримой **уверенностью** по каждому.

---

## 0. Принципы

| # | Принцип |
|---|---------|
| **H0** | HDM строится **медленно** — из целей, выборов, действий, discovery; не из одной анкеты |
| **H1** | Каждое знание = **значение + confidence + sources** — не boolean без контекста |
| **H2** | Discovery Questions **не красивые** — они **targeted**: уменьшают uncertainty по `hypothesis_id` |
| **H3** | **Цели дня** — самый ценный сигнал (частота >> разовых вопросов); 100 целей > 100 generic вопросов |
| **H4** | Inferred traits = `hypothesis` до confirmation; UI **не** показывает trait как факт без confidence gate |
| **H5** | Guidance использует HDM: не только «сегодня поговори», а «**обычно ты откладываешь** — сегодня условия лучше» |

---

## 1. Измерения модели (канон v1)

Каждое измерение — **enum или шкала** + **confidence** + **evidence**. Не все заполняются сразу.

### 1.1 Отношение к неопределённости (`uncertainty_tolerance`)

| Значение | Смысл |
|----------|--------|
| `avoids` | Избегает неопределённости |
| `tolerates` | Нормально переносит |
| `seeks` | Ищет неопределённость |

### 1.2 Способ принятия решений (`decision_style`)

| Значение | Смысл |
|----------|--------|
| `fast` | Быстро |
| `analytical` | После анализа |
| `social` | Через других людей |
| `intuitive` | Через интуицию |

### 1.3 Источник стресса (`stress_source`) — multi, top-K

| ID | Смысл |
|----|--------|
| `overload` | Перегрузка |
| `conflicts` | Конфликты |
| `loss_of_control` | Отсутствие контроля |
| `time_pressure` | Нехватка времени |
| `financial_risk` | Финансовые риски |

### 1.4 Мотивация (`motivation_driver`) — multi, ranked

| ID | Смысл |
|----|--------|
| `achievement` | Достижения |
| `safety` | Безопасность |
| `freedom` | Свобода |
| `recognition` | Признание |
| `relationships` | Отношения |

### 1.5 Поведение под нагрузкой (`under_load_behavior`)

| Значение | Смысл |
|----------|--------|
| `works_more` | Начинает больше работать |
| `postpones` | Откладывает |
| `withdraws` | Закрывается |
| `seeks_support` | Ищет поддержку |
| `controls_more` | Уходит в контроль |

### 1.6 Производные traits (примеры, расширяемый registry)

| Trait ID | Пример гипотезы |
|----------|-----------------|
| `conflict_avoidance` | Избегает сложных разговоров |
| `overload_pattern` | Берёт слишком много при стрессе |
| `deadline_procrastination` | Откладывает до последнего |
| `delegation_avoidance` | Не делегирует |

**Правило:** trait registry — versioned; новый trait только с **discovery template** + **signal mapping**.

---

## 2. Knowledge atom (confidence layer)

Каждая запись HDM — **Knowledge Atom** (UKM), не строка в UI.

```json
{
  "atom_id": "hdm_conflict_avoidance_v1",
  "dimension": "trait",
  "trait": "conflict_avoidance",
  "value": true,
  "confidence": 0.72,
  "knowledge_type": "hypothesis",
  "sources": [
    { "kind": "discovery_answers", "weight": 0.35 },
    { "kind": "goal_patterns", "weight": 0.40 },
    { "kind": "behavioral_signals", "weight": 0.25 }
  ],
  "last_updated": "2026-06-23",
  "confirmation_count": 2,
  "contradiction_count": 0
}
```

| Поле | Правило |
|------|---------|
| `confidence` | 0..1; < 0.5 — не в high-priority copy; 0.5–0.75 — мягкие формулировки; > 0.75 — «обычно ты…» |
| `knowledge_type` | `hypothesis` → `pattern` после N confirmations; `fact` только для explicit user statements |
| `sources` | Обязательны; audit для PIL |

**Пороги *(TBD wire)*:** confirm → +Δ confidence; contradict → −Δ; decay без reinforcement.

---

## 3. Discovery Questions → HDM (не журнал)

**Discovery Question** привязан к:

```json
{
  "question_id": "dq_conflict_avoidance_03",
  "targets_hypothesis": "conflict_avoidance",
  "uncertainty_before": 0.62,
  "purpose": "reduce_uncertainty"
}
```

**Пример:**

- Гипотеза: `conflict_avoidance = true`, confidence **38%**
- Через неделю (не каждый день):  
  *«Что ты обычно делаешь, когда понимаешь, что разговор будет неприятным?»*
- Ответ → signal → обновление atom → **не** «запись в дневник» как конечная цель

**Scheduler rules:**

| Правило | Смысл |
|---------|--------|
| Max 1 targeted discovery / day | Не допрос |
| Приоритет: lowest confidence × highest impact | Impact = влияние на guidance |
| Не спрашивать trait напрямую | R20 в Today canon |
| Cooldown на тот же `hypothesis_id` | ≥ 7 дней без новых сигналов |

---

## 4. Источники сигналов (приоритет)

| Приоритет | Источник | Примеры |
|-----------|----------|---------|
| **P0** | **Цели дня** (100+ за месяцы) | Темы, формулировки, outcomes, changed goals |
| **P1** | **Выборы ритуала** | Карта, число, вариант цели |
| **P2** | **Поведение (L2)** | Время открытия, returns, step done, skip evening |
| **P3** | **Discovery answers** | Targeted ответы |
| **P4** | **Explicit profile** | Onboarding facts — anchor, не единственный источник |

**Контур данных:**

```
Goals + Choices + Behavior + Discovery
        ↓
   Signal extraction
        ↓
   HDM update (confidence)
        ↓
   CUM slice for Gate / Today
```

---

## 5. Guidance: два входа, один выход

**Было (Today v2.0):**

```
Goal → API → Guidance (день)
```

**Добавлено (v2.3):**

```
Goal → Human Model update → Guidance (день + долгосрочный угол)
```

| Вход S8 | Использование |
|---------|----------------|
| Контекст дня | карта, число, focus, astro |
| Цель дня | немедленная поддержка |
| **HDM slice** | персонализация тона: «обычно ты…», «ты чаще…» |

**Пример copy (confidence > 0.7):**

> Обычно ты откладываешь подобные разговоры до последнего момента.  
> Сегодня условия для такого разговора выглядят лучше обычного.

**Запрещено при confidence < 0.5:** утверждения «ты всегда…» в product copy.

**API S7/S8 request** должен включать: `hdm_slice_top_k` (15–30 atoms max, UKM gate) — не full profile.

---

## 6. Что система узнаёт за 30 / 180 дней *(ориентиры, не обещания UI)*

| Горизонт | Реалистичный выход |
|----------|-------------------|
| **7 дней** | Первые гипотезы по goal themes; 1–2 traits confidence 0.3–0.5 |
| **30 дней** | Ranked stress_source, motivation hints; 2–3 traits 0.5–0.65 |
| **90 дней** | Стабильные decision_style / under_load; персонализированный discovery schedule |
| **180 дней** | Guidance с «обычно ты…» на ключевых traits; measurable recommendation lift |

**Метрика успеха HDM:** снижение **uncertainty** по измерениям §1 + рост **confirmed** patterns — [USER_MODEL_TARGET_STATE.md](pim/USER_MODEL_TARGET_STATE.md) §2 #4.

---

## 7. Mapping → CUM / Profile

| HDM | CUM / Profile |
|-----|----------------|
| Dimensions §1 | `behavioral_patterns[]` |
| Traits §1.6 | `behavioral_patterns` + UKM atoms |
| confidence | `confidence{}` per dimension |
| Не дублировать | Profile Identity facts (birth, name) |

Profile screen **может** показывать обобщённый портрет **позже** — Today **не** показывает HDM как таблицу traits.

---

## 8. Changelog

| Дата | Изменение |
|------|-----------|
| 2026-06-23 | v1.0 ACCEPTED — измерения, confidence atoms, discovery targeting, Goal→HDM→Guidance, source priority |
