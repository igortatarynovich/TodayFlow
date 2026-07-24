# Core User Loop — Theme → Action → Progress

**Статус:** принято (гипотеза **главного объекта продукта** — проверяется, не wire).  
**Версия:** 1.0 (2026-06-01).  
**Владелец:** Product + Engineering.

**Роль:** один объект, вокруг которого собираются ветки A/B/C/D/E, справочники, DayModel и экраны. **Не** описание экрана Today и **не** замена UMTS — **продуктовая проекция** цикла, который пользователь проходит каждый день.

**Пауза:** до проверки этой гипотезы — **не** расширять архитектуру (C1.7 enrichment, causal graph, новые registries). **Не** блокирует P0.1a, но задаёт **зачем** P0.1a.

**Связь:** [FIRST_DAY_EXPERIENCE.md](./FIRST_DAY_EXPERIENCE.md), [TODAY_PRODUCT_MODEL.md](./TODAY_PRODUCT_MODEL.md), [USER_MODEL_TARGET_STATE.md](pim/USER_MODEL_TARGET_STATE.md), [API_MEMORY_AND_LEARNING_LAYER.md](./API_MEMORY_AND_LEARNING_LAYER.md), [PERSONAL_INTELLIGENCE_LAYER.md](pim/PERSONAL_INTELLIGENCE_LAYER.md).

---

## 0. Главный вопрос

Не «из чего состоит Today?» и не «какие ветки существуют?»

> **Не является ли Theme → Action → Progress главным объектом всей системы?**

Если да — справочники **не существуют сами по себе**. Они **питают один цикл**.

**Источник цикла — Profile** *(в service of Today)*:

```
Profile  →  Theme  →  Action  →  Progress
```

Today — **главный продукт**. Profile — **Personal Operating Manual**, улучшающий качество Today. См. [PROFILE_SCREEN_MASTER.md](profile/PROFILE_SCREEN_MASTER.md) §0.1.

---

## 1. Три блока цикла

| Блок | Вопрос пользователя | Продуктовая функция |
|------|---------------------|---------------------|
| **Theme** | **Что сейчас важно?** | Направление дня / периода |
| **Action** | **Что делать?** | Одно (или мало) конкретных движений **сейчас** |
| **Progress** | **Что изменилось?** | След от выполненного Action; топливо для следующего Theme |

```
Theme     →  задаёт направление
Action    →  создаёт движение
Progress  →  показывает результат движения
```

**Поведение:** пользователь **делает** Action → Progress обновляется → следующий Theme точнее.

Это **не только First Day**. Один и тот же цикл:

| Сценарий | Theme | Action | Progress |
|----------|-------|--------|----------|
| First Day | фокус дня 1 | первый шаг | «день начался» |
| Day 20 | strategy дня | habit / goal step | streak, completions |
| Recovery Day | щадящий tempo | rest / micro-win | «берёшь паузу — это тоже шаг» |
| Discipline Cycle | path theme | practice block | cycle day N/M |
| Weekly Review | недельный vector | одна коррекция | delta vs прошлая неделя |

**Insight, Symbolic, Why** — усилители или layer 2. **Не** ядро цикла.

---

## 2. Связь с UMTS (Intelligence ≠ Product loop)

| UMTS / CUM (средства) | Куда в цикле |
|------------------------|--------------|
| Identity, Current State, Themes | **Theme** (inputs) |
| Recommendations | **Action** (inputs) |
| Confidence, behavioral patterns | **Progress** + обратная связь в Theme |
| Evolution (PEG) | **модификатор** всех трёх (caps, depth) |

UMTS отвечает: «что система **знает**».  
Core User Loop отвечает: «что пользователь **делает и видит**».

**Freeze rule (новый):** слой или registry row, который **не влияет** на Theme, Action или Progress в user-visible form — **backlog**, не приоритет enrichment.

---

## 3. Матрица доменов → цикл

Легенда:

| | |
|---|---|
| **✅** | **Primary** — главная роль домена в этот блок (prod или target явно) |
| **⚠️** | **Modifier** — влияет, но не главный поставщик; или wired partial / tests only |
| **❌** | **Not primary** — не должен быть оправданием enrichment «ради домена» |

### 3.1 Engine & branches

| Домен | Theme | Action | Progress | Комментарий |
|-------|:-----:|:------:|:--------:|-------------|
| **DayModel** (P1) | ✅ | ⚠️ | ❌ | strategy, tempo, risk, vector → Theme; `action_mode` → Action hint; не хранит Progress |
| **Practice** (C) | ❌ | ✅ | ⚠️ | C1 defs + selection → Action; tracker completions → Progress (partial prod) |
| **Calendar** (E) | ❌ | ❌ | ✅ | day marks, rhythm, month map → Progress / «что изменилось» |
| **Evolution** (B) | ⚠️ | ⚠️ | ✅ | caps tone/depth/practice; stage visible in Progress; B1.10 envelope |
| **Knowledge** (A) | ✅ | ⚠️ | ⚠️ | top-K atoms → Theme weight; hints → Action (advisory); confirmation → Progress narrative |
| **Symbolic** (D) | ⚠️ | ❌ | ❌ | tarot/number → Theme **angle**; не Action; не Progress ledger |

### 3.2 Profile & inputs

| Домен | Theme | Action | Progress | Комментарий |
|-------|:-----:|:------:|:--------:|-------------|
| **Birth Profile / Identity** | ✅ | ⚠️ | ❌ | natal + numerology base → Theme; domain bias → Action |
| **Intent** | ✅ | ⚠️ | ❌ | path theme, JTBD → Theme priority |
| **Reality / Current State** | ✅ | ⚠️ | ❌ | mood, mode → Theme tone + Action format |
| **Reference machine** (astro/transit/number) | ✅ | ❌ | ❌ | machine facts → DayModel → Theme |

### 3.3 Learning & signals

| Домен | Theme | Action | Progress | Комментарий |
|-------|:-----:|:------:|:--------:|-------------|
| **Meaning events / Signals** | ⚠️ | ⚠️ | ✅ | **primary** Progress fuel; feedback → future Theme |
| **Fusion / tracking** | ❌ | ⚠️ | ✅ | completions, streaks, guide_meaning_completions |
| **PIL / LLM** | ⚠️ | ⚠️ | ❌ | polish language **всех** блоков; не создаёт Progress facts |
| **Causal graph / associations** | ⚠️ | ⚠️ | ⚠️ | **selection explainability**; питает все три через rankers; не user object |

---

## 4. Ветки A–E как питатели цикла (не как карта мира)

| Branch | Было (мышление) | Стало (мышление) |
|--------|-----------------|------------------|
| **P1 + Day Engine** | «DayModel pipeline» | **Theme engine** (+ Action hints) |
| **C Practice** | «Practice system» | **Action engine** |
| **E Calendar** | «Calendar intelligence» | **Progress engine** |
| **A Knowledge** | «Knowledge usage» | **Theme refinement** (+ Action caution) |
| **B Evolution** | «Evolution engine» | **Loop governor** (what depth allowed) |
| **D Symbolic** | «Symbolic assets» | **Theme flavor** (optional layer) |

Пользователь **не видит** ветки. Видит **один цикл**.

---

## 5. Что даёт таблица (восстановление нити)

| Вопрос | Ответ через матрицу |
|--------|---------------------|
| Какие справочники **уже достаточны** для цикла? | DayModel seeds (P1.3), Practice defs (C1.1), базовый Profile — **достаточно для First Day Theme+Action** |
| Какие **не участвуют** в user loop? | Commerce SKUs (D1.5), bulk association rows **без** consumer в T/A/P |
| Какие дают **контекст**, но не Action? | Symbolic, much of Reference prose |
| Какие влияют на Action, **не** отражаясь в Progress? | Narrative `do_items` без tracker hook → **product gap** |
| Куда invest enrichment **после** P0? | Progress wiring (E1→UI, meaning→strip), Action selection (C1.7+ranker **when loop proven**) |

---

## 6. Prod vs target (честный срез 2026-06-01)

| Leg | Prod today | Target |
|-----|------------|--------|
| **Theme** | ✅ data (guide POST); ❌ UX (ritual gate) | Layer 1 visible ≤60s |
| **Action** | ✅ after ritual; ⚠️ copy quality | One primary CTA + tracker link |
| **Progress** | ⚠️ fragments (essentials %, DE-7); ❌ strip | Always visible; Calendar/E fusion merged |

**Foundation path** (P1.4 package) уже **структурирован** как Theme/Action slots — но **не** wired to UI. Legacy monolithic narrative **смешивает** три ноги в один JSON.

---

## 7. Implications (freeze-friendly)

### 7.1 Для First Day (P0.1a)

Реализуем **минимальный Core User Loop**, не «экран Today»:

- Theme + Action + Progress  
- **Без** Symbolic gate  
- Domains: Profile + Intent + Reality + DayModel only (Test A)

### 7.2 Для enrichment / registries

**Pause** до loop proof:

- C1.7 bulk seeding **не** приоритет, пока Action leg не visible  
- Causal graph **не** приоритет, пока Progress leg не visible  
- Calendar E **ценен** когда Action → event → Progress closed  

### 7.3 Для новых слоёв

Каждый proposal: **какую ногу T/A/P двигает?** Если «ни одну» — reject.

---

## 8. Связь с другими product models

| Документ | Роль |
|----------|------|
| [PROFILE_SCREEN_MASTER.md](profile/PROFILE_SCREEN_MASTER.md) | **Центральный объект** — источник контекста |
| [CORE_USER_LOOP.md](./CORE_USER_LOOP.md) | **Главный цикл** — Profile → Theme → Action → Progress |
| [FIRST_DAY_EXPERIENCE.md](./FIRST_DAY_EXPERIENCE.md) | Day 1 instance of loop |
| [TODAY_PRODUCT_MODEL.md](./TODAY_PRODUCT_MODEL.md) | Today = **projection** of loop на экран |
| [PROFILE_SCREEN_MASTER.md](profile/PROFILE_SCREEN_MASTER.md) | **UI + контент** Profile |
| [USER_MODEL_TARGET_STATE.md](pim/USER_MODEL_TARGET_STATE.md) | Intelligence artifact **behind** loop |

---

## 9. Open validation (после doc)

| # | Проверка |
|---|----------|
| V1 | Weekly Review / Recovery — описать как T→A→P (1 pager each) |
| V2 | Test B + matrix: после P0.1a Progress leg ✅ в prod UX? |
| V3 | Enrichment backlog **пересортировать** по колонкам матрицы |

---

*Bump версию при смене primary/modifier роли домена или статуса «главный объект продукта».*
