# User Model Target State (UMTS)

**Статус:** принято (канон **конечного артефакта** Intelligence Layer).  
**Версия:** 1.0 (2026-05-31).  
**Владелец:** Product + Engineering.

**Роль:** **северная звезда** артефакта Intelligence — всё остальное средства, не цели.

**Критерий успеха продукта (операционно):** [PIM_PRODUCT_NORTH_STAR.md](./PIM_PRODUCT_NORTH_STAR.md) — завершённый цикл → **ценность PIM** ↑ (Learning Δ > 0).

**Связь:** [CORE_PRODUCT_CANON.md](./CORE_PRODUCT_CANON.md), [USER_MODEL_TARGET_STATE.md](./USER_MODEL_TARGET_STATE.md) (кем становится пользователь), [USER_MODEL_TARGET_STATE.md](./USER_MODEL_TARGET_STATE.md), [REFERENCE_LAYER_AND_BUILD_ORDER.md](./REFERENCE_LAYER_AND_BUILD_ORDER.md), [PERSONAL_INTELLIGENCE_LAYER.md](./PERSONAL_INTELLIGENCE_LAYER.md), [USER_KNOWLEDGE_MODEL.md](./USER_KNOWLEDGE_MODEL.md), [KNOWLEDGE_ACQUISITION_AND_SIGNAL_POLICY.md](./KNOWLEDGE_ACQUISITION_AND_SIGNAL_POLICY.md), [INTERPRETATION_LAYER_AND_REFERENCE.md](./INTERPRETATION_LAYER_AND_REFERENCE.md), [DATA_OWNERSHIP_AND_CONSUMPTION_MAP.md](./DATA_OWNERSHIP_AND_CONSUMPTION_MAP.md), [DAY_CONTEXT_V0.md](./DAY_CONTEXT_V0.md).

---

## 0. Главный вопрос

**Какой конечный артефакт производит TodayFlow?**

Без ответа система начнёт **собирать знания ради знаний** — бесконечные слои, справочники, интерпретации, память.

**Формула:**

> TodayFlow **не** стремится хранить всё.  
> TodayFlow стремится **уменьшать неопределённость** о пользователе и его следующем шаге.

---

## 1. Что НЕ является целью

| Не цель | Почему |
|---------|--------|
| Максимум данных о пользователе | шум, privacy risk, token waste |
| «Идеальный» профиль в вакууме | нет критерия done |
| Обучить собственную модель | средство, не продукт |
| Огромная память / миллионы events | свалка без UMTS |
| Все интерпретации / все справочники | без фильтра «что двигает UMTS» |

**Правило freeze для новых слоёв:** если артефакт **не уменьшает неопределённость** в одном из §2 — **не строим**.

---

## 2. Выходы продукта

Intelligence + Product Layer производят **пять** результатов (4 = CUM, 5 = путь):

| # | Выход | Вопрос | Артефакт |
|---|-------|--------|----------|
| **1** | Понимание пользователя | Кто он? | CUM **Identity** + Patterns |
| **2** | Понимание периода | Что сейчас? | **Current State** + Themes |
| **3** | Лучшее действие | Что делать? | **Recommendations** |
| **4** | Улучшение точности | Стало лучше? | **Confidence** + learning |
| **5** | **Эволюция** | Во что превращается? | **Personal Path** — [EVOLUTION_CALCULATION_CONTRACT.md](./EVOLUTION_CALCULATION_CONTRACT.md) (до UEM-2 без API stage) |

**#1–#4** — Compact User Model §3. **#5** — прогресс и commerce.

---

## 3. Compact User Model (конечный артефакт Intelligence)

Intelligence Layer **не отдаёт** events, raw memory, interpretation dump.

Он отдаёт **Compact User Model (CUM)** — сжатая модель для Context Selection, UI, Gate:

```json
{
  "contract_version": "compact_user_model_v1",
  "as_of": "2026-05-31",
  "identity": {},
  "current_state": {},
  "active_themes": [],
  "behavioral_patterns": [],
  "recommendations": [],
  "confidence": {},
  "evolution": { "stage": "practitioner", "evolution_score": 340 }
}
```

### 3.1 Identity — кто человек (stable)

| Поле | Содержание | Источник |
|------|------------|----------|
| `facts` | birth, goals stated, habits declared | onboarding, KASP A/B, `fact` |
| `strengths` | что работает устойчиво | `pattern`, confirmed |
| `constraints` | ограничения, avoid, negative memory | UKM negative domain |
| `motivation_style` | direct / gentle, short / deep | format/style patterns |
| `life_rhythm` | peak hours, weekly cycle | timing patterns |

**Не включать:** сырые events, 300 interpretations, bulk reference.

### 3.2 Current State — что происходит сейчас (daily)

| Поле | Содержание | Источник |
|------|------------|----------|
| `mood_energy` | today check-in | KASP C, DayContext RT |
| `dominant_tension` | conflict / risk today | DayModel, DayContext |
| `stage` | micro-life phase (если есть signal) | L3 interpretation, weak |
| `risks` | что может пойти не так сегодня | DayModel risk |
| `opportunities` | окна для действия | rhythm + patterns |

**Код сегодня:** `DayContext` layers, `fusion`, `day_model` — частично покрывают **#2**.

### 3.3 Active Themes — какие темы доминируют

| Поле | Пример |
|------|--------|
| `themes[]` | `{ id: "discipline", weight: 0.82, stability: "stable" }` |
| `window_days` | 30 / 60 |
| `linked_areas` | work, body, relationships |

Top **3–5** themes, не 50 tags.

### 3.4 Behavioral Patterns — что реально работает

| Поле | Пример |
|------|--------|
| `works[]` | evening body practice, 2-min format |
| `does_not_work[]` | morning-heavy routines |
| `evidence_strength` | confirmed count / window |

### 3.5 Recommendations — что делать дальше

| Правило | |
|---------|---|
| Count | **1 primary** + до **2 alternates** |
| Form | concrete, timed, measurable |
| Source | DayContext + patterns + **не** hypothesis-only |
| Anti | philosophy essay, 50 bullet list |

**Код сегодня:** Today `action_options`, `support` — прототип **#3**.

### 3.6 Confidence — насколько система уверена

| Поле | Описание |
|------|----------|
| `overall` | 0–1 composite |
| `by_domain` | identity, themes, timing, rec |
| `uncertainty_flags` | unknown birth time, low data, L4 only |
| `delta_30d` | изменение vs 30 days ago (**#4**) |

**UX:** явная осторожность при low confidence ([PERSONAL_INTELLIGENCE_LAYER.md](./PERSONAL_INTELLIGENCE_LAYER.md) §10.18).

---

## 4. Уменьшение неопределённости (метрика успеха)

Улучшение = **confidence растёт** или **hypothesis → confirmed pattern**.

| Сегодня | Через месяц | Улучшение? |
|---------|-------------|------------|
| interest discipline: 0.55 (hypothesis) | 0.91 (pattern, 17 confirms) | ✅ |
| «возможно вечер» (hypothesis) | 84 evening completions | ✅ |
| 10 000 events, CUM пустой | — | ❌ **провал** |

**Learning Layer (#4)** измеряет:

- `confidence_delta` по domain  
- `hypothesis_promotion_rate`  
- `recommendation_completion_rate`  
- `user_correction_rate` (down = better)  

---

## 5. Критерий провала через год

Если через 12 месяцев система имеет 10 000+ events, но **не может** ответить:

1. **Кто он?** (Identity с facts + stable patterns)  
2. **Что с ним происходит?** (Current State + Active Themes)  
3. **Что делать дальше?** (Recommendations с evidence)  

→ **архитектура провалилась**, независимо от числа слоёв и справочников.

---

## 6. Целевое состояние через 1 год (пример)

Не схема БД — **итог**, который пользователь (и система) «чувствуют»:

### Identity (stable)

- Life path 7, Scorpio Sun, evening person (confirmed)  
- Prefers short, direct copy (stable)  
- Body practices work; morning routines don't (confirmed)  
- Sensitive topics: control, money (user-visible opt-in)  

### Current State (today)

- Mood: tired · Energy: low  
- Tension: workload vs need for rest  
- Risk: overcommitting today  

### Active Themes

1. discipline (0.88)  
2. work focus (0.71)  
3. financial clarity (0.65, still hypothesis-heavy)  

### Behavioral Patterns

- Best window: 18:00–22:00  
- Completes 2-min actions 3× more than 20-min  
- Returns after skip within 48h when evening nudge  

### Recommendations (today)

1. **Primary:** 2-min breath before one work task (20 min block)  
2. **Alternate:** defer non-urgent message until tomorrow 10:00  

### Confidence

- overall: 0.78 (↑ from 0.52 at day 30)  
- timing patterns: 0.85 (high)  
- money theme: 0.58 (medium — needs more confirm)  

---

## 7. Фильтр: что собирать / что выбрасывать

Каждый канал, event, справочник, interpretation rule проходит **UMTS filter**:

| Вопрос | Да → keep | Нет → drop / defer |
|--------|-----------|---------------------|
| Уменьшает неопределённость в Identity? | collect | ignore |
| Влияет на Current State / Themes? | collect | ignore |
| Может изменить Recommendations? | collect | ignore |
| Двигает Confidence / learning metrics? | collect | ignore |
| Только «интересно аналитикам»? | — | **never collect** |

### Примеры

| Элемент | Verdict |
|---------|---------|
| Birth date | ✅ Identity fact |
| Every page scroll pixel | ❌ defer |
| mood_selected daily | ✅ Current State |
| 1× save money post | ⚠️ signal only, not knowledge (KASP) |
| Tarot machine scores P0 | ✅ DayContext / Current State |
| 180 reference rows inactive | ❌ defer until consumer in CUM |
| L4 «хочет переехать» | ❌ never as fact; theme interest only |

---

## 8. Как слои служат UMTS (не наоборот)

| Слой | Служит выходу |
|------|----------------|
| Reference Layer | расчёт Identity facts, DayModel inputs |
| KASP | только разрешённые данные для CUM |
| Events | сырьё → фильтр §7 |
| Signals | нормализация для Interpretation |
| Interpretation Reference | смысл без LLM → Themes / Patterns |
| UKM | atoms → CUM fields |
| Memory | materialize CUM between sessions |
| DayContext | **Current State** + inputs to Recommendations |
| CoreProfile SN | **Identity** stable slice |
| AMLL / Gate | экономия на пути к Recommendations |
| Feedback | **Confidence** delta |

**Stop rule:** новый документ/слой без строки «какой выход §2» — не принимается в канон.

---

## 9. Mapping к коду (gap)

| CUM block | Сегодня | Gap |
|-----------|---------|-----|
| Identity | `CoreProfileSnapshot`, living layer | unified CUM contract |
| Current State | `DayContext`, fusion, day_model | explicit `current_state` object |
| Active Themes | learning_context topics | top-K stable themes |
| Behavioral Patterns | `behavior_patterns`, meaning_surface | confirmed vs hypothesis split |
| Recommendations | Today narrative actions | rank + evidence link |
| Confidence | partial in selector | `delta_30d`, by_domain |

**Target contract:** [compact_user_model_v1.schema.json](./schemas/compact_user_model_v1.schema.json) — **UMTS-1 ✅ (2026-07-03)**. Read slice: [compact_user_model_v0.schema.json](./schemas/compact_user_model_v0.schema.json) · CI `compact-user-model-schema`.

---

## 10. Build order (пересмотр приоритетов)

| Priority | Work | Serves |
|----------|------|--------|
| **UMTS-1** | Этот канон + CUM schema | north star ✅ · [compact_user_model_v1.schema.json](./schemas/compact_user_model_v1.schema.json) **2026-07-03** |
| **P0 Reference** | tarot/numerology/astro for **day** | Current State |
| **UKM + ILR** | только поля, нужные CUM §3 | Identity, Themes, Patterns |
| **UMTS-2** | `build_compact_user_model_v0` | single output for selector/LLM |
| Gate / AMLL | after CUM slice stable | cost |
| Own model | after CUM + dataset | #4 |

**Не параллельно без лимита:** новые interpretation rules без §7 filter.

---

## 11. Feature DoD (UMTS-aware)

- [ ] Какой выход §2 затронут (1–4)?  
- [ ] Какое поле CUM §3 обновляется?  
- [ ] Как измеряется ↓ uncertainty / ↑ confidence?  
- [ ] Что **не** собираем (explicit non-goals)?  

---

## 12. Changelog

- **1.2 (2026-07-03)** — UMTS-1: `compact_user_model_v1.schema.json` + CI; v0 read slice cross-linked.
- **1.1 (2026-05-31)** — 5-й выход «Эволюция»; CUM.evolution; связь UEM/GPS/SACL.
- **1.0 (2026-05-31)** — первый канон UMTS.
