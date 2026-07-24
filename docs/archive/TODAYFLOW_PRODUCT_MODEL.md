> SUPERSEDED 2026-07-24 → см. docs/TODAYFLOW_PRODUCT_CANON_UNIFIED.md

# TodayFlow — Product Model

**Статус:** **FROZEN for Launch v1** (execution) · **§4 Content Models — ACTIVE** (2026-07-01).  
**Версия:** 0.4.9 (2026-07-02)  
**Владелец:** Product

> **Launch Scope Freeze:** Personal Model, Projection-first, PIM, философия, новые категории и новые product-docs — **закрыты** до user test. Работа только по [WEB_LAUNCH_PRODUCT_BLUEPRINT.md](../status/WEB_LAUNCH_PRODUCT_BLUEPRINT.md) Epic 1–4.

**Роль:** описание **самой модели продукта** — не UX-спека, не PIM-канон, не OpenAPI.  
**Для кого:** product, design, engineering — единый язык решений на годы.

**Философия проектирования (одно предложение):**

> **Мы не строим экраны. Мы развиваем Personal Model пользователя; экраны — лишь временные проекции этой модели.**

Если через год появятся ещё 20 разделов — этот принцип остаётся истинным.

**Explainable Computation** *(общий канон вычислений и интерпретаций — см. [EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md](../explainability/EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md)):*

> Источник → расчёт → интерпретация → практический смысл → текст.  
> Нельзя объяснить происхождение вывода — нельзя в production. Касается целей, аскез, рекомендаций, натала, совместимости и всех разделов.

**Product Truth First** *(обязательный принцип отображения — см. [PRODUCT_TRUTH_FIRST.md](../PRODUCT_TRUTH_FIRST.md)):*

> **Сначала рабочая логика, данные и API. Потом интерфейс.**  
> Дизайн отображает построенный продукт, а не изображает будущий. Нет источника / нет данных — нет заполненного блока в production UI.

**Understanding Progress** *(см. [UNDERSTANDING_PROGRESS_AND_DEPTH_CANON.md](../UNDERSTANDING_PROGRESS_AND_DEPTH_CANON.md)):*

> Прогресс = качество понимания пользователя. Missing data → «знаем X, для Y нужно Z». Подписка = глубина, не обрезанные блоки. Trial = целостный опыт.

**Не путать с:**

| Документ | Уровень |
|----------|---------|
| [TODAYFLOW_PRODUCT_MODEL.md](./TODAYFLOW_PRODUCT_MODEL.md) | **Весь продукт** — Personal Model, projections, законы |
| [TODAY_PRODUCT_MODEL.md](../TODAY_PRODUCT_MODEL.md) | **Projection Today** — блоки экрана дня, Today Package |
| [PROFILE_SCREEN_MASTER.md](../profile/PROFILE_SCREEN_MASTER.md) | **UI Profile** — layout, editorial, depth routes |
| [PERSONAL_INTELLIGENCE_MODEL_V1.md](../pim/PERSONAL_INTELLIGENCE_MODEL_V1.md) | **PIM** — инфраструктура atoms, signals, gate |
| [USER_MODEL_TARGET_STATE.md](../pim/USER_MODEL_TARGET_STATE.md) | **CUM** — compact export для reasoning / LLM |
| [status/WEB_LAUNCH_PRODUCT_BLUEPRINT.md](../status/WEB_LAUNCH_PRODUCT_BLUEPRINT.md) | **Launch v1** — feel/do по экранам (временный execution slice) |

**Launch Blueprint** не дублирует этот документ. Blueprint = *как войти в продукт*. Product Model = *что продукт есть*.

---

## 0. Терминология (обязательно)

Внутри команды слово **Profile** перегружено. Фиксируем разделение:

| Термин | Что это | Примеры |
|--------|---------|---------|
| **Personal Model** *(рабочее имя — см. §0.1)* | Главная **продуктовая сущность** — живое цифровое представление человека; единственный SoT персонализации | identity, journey, patterns, saved people |
| **Profile** (экран) | **UI-проекция** Personal Model — вкладка «Профиль» / Life Intelligence hub | `/profile`, iOS Profile tab |
| **Projection** | Экран/flow, который **читает** Personal Model, **пишет** обратно и **делает модель понятнее** | Today, Compatibility, Tarot pick |
| **PIM** | **Инфраструктура** обновления Personal Model — не то, что видит пользователь | Knowledge Atoms, ILR, Learning Δ |
| **Reference Layer** | Справочники смыслов — **кормят** Personal Model, не UI | ~180 entities, machine contract |
| **Experience** | Конкретный UI/session на projection | First Today, evening close |
| **CUM** | Compact export для reasoning/LLM ([UMTS](../pim/USER_MODEL_TARGET_STATE.md)) | top-K atoms, current_state |
| **Maps** | Живая **накопительная история** жизни — вторая половина продукта (§4.10) | Mood Map · Habit Map · My 2026 |
| **Map** *(единственное)* | Одна временная проекция Personal Model — heatmap, journey, network, timeline | Карта настроения · карта обещаний |

**Правило речи:** в продуктовых и архитектурных обсуждениях — **Personal Model** (или утверждённый термин из §0.1); в пользовательском UI — **Profile**.

**Запрет user-facing слов:** **трекер** · **статистика** · **completion rate** · **алгоритм нашёл** → **карта** · **история** · **наблюдение** ([EXPLAIN_MEANING_NOT_MECHANISM.md](../explainability/EXPLAIN_MEANING_NOT_MECHANISM.md) · §4.10 · §5.8).

### 0.1 Имя сущности — **OPEN на review**

**Personal Model** — рабочее имя v0.2. Не срочно переименовывать; **на review зафиксировать термин на годы**.

| Кандидат | Плюс | Минус |
|----------|------|-------|
| **Personal Model** | точно, neutral | звучит инженерно |
| **Life Model** | ближе к пользователю | может путаться с «life path» numerology |
| **Life Graph** | накопление, связи | технично, graph ≠ продукт для всех |
| **Human Model** | человеко-центрично | generic |
| **Personal Intelligence** | близко к «пониманию себя» | конфликт с PIM / PIL |
| **Identity Model** | коротко | узко — не только identity |

**Решение review:** один термин для docs + code comments; **Profile** остаётся только для UI-вкладки.

---

## 1. Что такое TodayFlow

TodayFlow — **не**:

- приложение с гороскопами;
- AI-ассистент;
- трекер привычек;
- набор esoteric tools.

TodayFlow — **система, которая строит и развивает Personal Model человека** и через неё принимает все персональные решения в продукте.

**Внешнее обещание (рынок):** персональный ежедневный ориентир, который **помнит, что было вчера**.  
**Внутреннее ядро:** Personal Model + projections.

---

## 2. Personal Model

Personal Model — **не** анкета, **не** натальная карта, **не** экран, **не** архитектурный dump.

> **Personal Model** — цифровое представление человека **внутри TodayFlow**, которое **непрерывно развивается вместе с ним** — и через которое TodayFlow принимает **все персональные решения**.

### Продуктовая природа (не «вычисляется раз в день»)

Модель **не вычисляется** — она **живёт**:

- **растёт** — каждое осмысленное взаимодействие может обогатить;
- **обогащается** — новые дни, люди, выборы, совместимости;
- **уточняется** — предпочтения и контекст становятся точнее;
- **иногда пересматривает** старые выводы — contradiction, эволюция, смена контекста (не dogma).

Так пользователь **воспринимает** продукт: не «сервис посчитал гороскоп», а **«что-то обо мне копится и становится точнее»**.

### Инварианты

- **никогда не «завершена»** — нет «100% profile complete» как финала;
- **единственный SoT** — Today, Compatibility и др. **ничего не «знают» сами**; знает только Personal Model;
- **не архив** — знание, не влияющее на сегодняшнюю проекцию, мёртвый вес;
- **двигатель решений** — то, что человек увидит **сегодня утром**, зависит от того, что модель накопила **вчера**.

**Центр продукта:** Personal Model.  
**Центр ежедневного использования:** projection **Today** (главная дверь — не противоречие).

---

## 3. Personal Model Lifecycle *(продуктовый)*

Не технический pipeline PIM — **что растёт в глазах пользователя** и команды.

| Stage | Имя | Что есть | Типичный момент | Что чувствует пользователь |
|-------|-----|----------|-----------------|----------------------------|
| **0** | **Empty** | Нет identity | До имени | «Пока ничего моего» |
| **1** | **Identity** | Имя, дата рождения, первые вычисления (знак, число пути) | Первый результат onboarding | «Это уже про меня» |
| **2** | **Initial** | Первый Today, карта/число дня, первая совместимость | День 1 | «Интересно, что скажет завтра» |
| **3** | **Growing** | Закрытые дни, история, предпочтения, saved people | День 3–7 | «Вчера не исчезло» |
| **4** | **Learning** | Повторения, уточнение рекомендаций, связь дней | День 10–30 | «Оно замечает то, что я сам не вижу» |
| **5** | **Mature** | Большая собственная история, высокое доверие, глубокие projections | Месяцы+ | «Это моя история, не generic совет» |

**Важно:** растёт **не набор функций** — растёт **модель человека** внутри TodayFlow.  
Launch Blueprint целит **Stage 1 → 3** (Identity through Growing). Stage 4–5 — product north star, не launch gate.

---

## 4. Product map *(content model — не фиксируем число навсегда)*

**Смотрим по поведению (JTBD), не по технологиям и не по текущим routes.**

Natal · numerology · transits · Reference — **источники данных**, не продукты и не вкладки верхнего уровня.

### 4.0 Что пользователь хочет сделать

| JTBD | Куда ведёт |
|------|------------|
| Узнать **сегодняшний день** | **Today** |
| **Понять себя** | **Profile** |
| Посмотреть **совместимость** | **Compatibility** |
| Получить **ответ** на вопрос | **Tarot** |
| **Изменить жизнь** регулярными действиями | **Growth** *(и зоны Today: Practice · Goals · Tracking)* |

Практики · аскезы · привычки · трекеры · аффirmations · journaling · челленджи — **один человеческий вопрос:**

> *Что я могу делать регулярно, чтобы изменить свою жизнь?*

Это **не** отдельные продукты первого уровня («модуль аффirmаций»). Пользователь не выбирает технологию — он хочет **начать менять одну привычку**, а TodayFlow ведёт в нужный инструмент.

### 4.1 Карта экосистемы *(рабочая, не финальная)*

| Слой | Что входит | Примечание |
|------|------------|------------|
| **Ядро** | **Today** · **Profile** | Ежедневный вход + «кто я» |
| **Standalone** | **Compatibility** · **Tarot** · **Growth** | Самостоятельная ценность + сильнее с Model |
| **Сервисы** | Journal · Saved people · Notifications · Calendar · Settings · History | Инфраструктура опыта, не «продукт» |

**Growth** *(рабочее имя)* — practices · asceticisms · habits · trackers · meditations · affirmations · quests · goals · streaks.  
**Вход:** из Today («хорошее время для практики») · Profile («тебе подойдёт…») · Tarot («попробуй после расклада») — **не обязательно** пункт главного меню на launch.

**Число кластеров не зафиксировано** — ожидаем 5–7 после JTBD-упражнения; карта выше — v0.4.

### 4.2 Правило UI: пользователь не видит дисциплины

В интерфейсе **запрещены** как primary framing:

- астрология, нумерология, психология, PIM, DayModel, Reference

Пользователь видит **ответы на человеческие вопросы**. Движки — под капотом.

| Плохо (дисциплина) | Хорошо (ответ) |
|--------------------|----------------|
| «Натальная карта» как продукт | **Кто ты** → при желании «Почему система так считает?» |
| «Раздел нумерология» | Число / путь / цикл **внутри** Today или Profile |
| «Сейчас открою астрологию» | «Хочу посмотреть **себя**» → Profile |

**Natal + numerology = доказательная база**, не витрина. Profile = исследование себя; карта и числа — **источники** внизу иерархии.

### 4.3 Product — Today *(daily life dashboard)*

**JTBD:** *Что происходит с моим **днём** сегодня?*

Today — **не** «астро-экран» и **не** линейный сценарий. Это **ежедневный дашборд** (аналог Apple Health для **дня**): много виджетов — один вопрос.

> **Today = агрегатор всего, что помогает прожить сегодня** — из natal, transits, numerology, tarot, moon, habits, cycle, goals, yesterday, practices, affirmations. Источник не важен; важна **иерархия**.

**Правило без которого развалится:** Hero за **~10 сек** — главное; дальше **исследование по желанию**. Нет обязанности пройти 20 блоков. Кто-то только карту; кто-то сразу practice; кто-то habits; кто-то evening.

#### Смысловые зоны Today

| Zone | Содержание | Launch v1 |
|------|------------|-----------|
| **1 · Overview** | Hero · тема дня · energy · главный фокус | ✅ core |
| **2 · Guidance** | что делать · чего избегать · внимание · вероятные события | ✅ do/don't; events v2 |
| **3 · Daily Symbols** | карта · число · символ · цвет · тотем · камень · луна · планета · стихия… | ✅ card+number; rest 🟡 — **не** как отдельные генераторы; см. [DAILY_INTERPRETATION_ENGINE_PHASE.md](../DAILY_INTERPRETATION_ENGINE_PHASE.md) |
| **4 · Practice** | **одна** рекомендованная: дыхание · медитация · практика · аскеза · благодарность · визуализация · affirmation | 🟡 one rec |
| **5 · Goals** | цель дня (системная или своя) | 🟡 optional |
| **6 · Tracking** | привычки · аскеза · **месячный цикл** + прогноз/рекомендации · mood · energy · вода · сон… | v2+ *(code exists)* |
| **7 · Evening** | закрытие дня → завтра | ✅ core |

**First Today (launch):** зоны 1–3 compact + 7; 4–6 по одному блоку max или teaser → Growth/deep.

**Замкнутый цикл экосистемы:**

```
Profile: «Ты быстро выгораешь»
    → Today: «Сегодня восстановиться»
    → Tarot: «На что обратить внимание»
    → Growth/Practice: «Практика на 7 дней»
```

**Retention test:** богатство **ритуала** без перегруза Hero — *исследовать с удовольствием*, не «пройти воронку».

### 4.4 Product — Profile *(content hierarchy)*

**Два JTBD — две половины экрана:**

| Половина | Вопрос | Что меняется | Слой |
|----------|--------|--------------|------|
| **Кто я** | Кто я? | Почти не меняется — **знания** | Portrait · natal · numerology · cycles · spheres · strengths · risks · relationships · money · purpose |
| **Как меняется моя жизнь** | Каким становится моя жизнь? | Каждый день — **история** | **Maps** · living layer · «Мои дни» · shareable arcs |

**North star Profile:** не CRM и не натальная стена — **портрет + живая история**.

```
Profile (ты)
├── Кто я                    ← знания · портрет · collapsed sources
│   личность · натал · циклы · особенности · сильные/слабые · отношения · деньги · предназначение
│
├── Как меняется моя жизнь   ← Maps (§4.10) · не чеклисты и не «трекеры»
│   mood · energy · habits · ascetics · goals · wishes · relationships · tarot · themes · symbols · promises
│
├── Мои люди — compatibilities · saved · relationship map
├── Мои дни — последние закрытые дни · мост Today ↔ Maps
└── Небо / интерактив (depth) · natal wall только по желанию
```

**Launch v1 (Execution E4):** identity strip + «Мои дни» + MapsPreview seed + collapsed deep layers.  
**North star scroll:** *Хочется исследовать 20 минут* — узоры жизни, не справочник.

### 4.5 Product — Compatibility *(content model)*

**JTBD:** «Кто мы друг для друга?» — **библиотека совместимостей**, не один калькулятор.

**Public L1** (standalone): две даты → инсайты, %, рекомендации.

**Types library** *(north star — не всё в launch)*:

| Серьёзные | Шуточные / viral |
|-----------|------------------|
| Romantic · Marriage · Friendship · Work · Conflict | Apocalypse · Partner in Crime · Office |
| Parenting · Business · Living Together | Vacation · Movie Night · Zombie Survival |
| Communication · Emotional · Sexual · Travel | … |

**Personal L2:** «Зная **тебя**, в этих отношениях обрати внимание на…»

**Retention test:** *Почему вернуться?* — новый type / новый человек / saved library.

### 4.6 Product — Tarot *(content flow)*

**JTBD:** «Что происходит вокруг моего вопроса?» — **живой** ритуал, не «выберите карту».

```
1. Что вас волнует? (chips + свой вопрос)
2. Выбор расклада (1 · 3 · крест · да/нет · путь · неделя · месяц · …)
3. Анимация вытягивания
4. Карты
5. Расшифровка
6. Как связано с тобой (Personal Model)
7. Что можно сделать
8. Сохранить · история · избранное
```

**Launch:** card-of-day в Today + существующие spreads; full question-first flow — **v2+**.

### 4.7 Product — Growth *(change over time)*

**JTBD:** *Что я делаю с этой информацией, чтобы изменить жизнь?*

**Внутри (не отдельные nav-items):** practices · asceticisms · habits · trackers · meditations · breath · affirmations · journaling · challenges · daily quests · goals · streaks · **cycle tracking** (месячный цикл + рекомендации).

**Standalone (§5.4):** можно зайти «начать 7-дневную практику» без Today.  
**Synergy:** рекомендации из Profile/Today/Tarot → конкретная practice в Growth или **zone 4 Today**.

**Launch:** teaser/recommendation в Today (zone 4) + существующие routes (`/practices`, `/habits`, `/asceticisms`, `/affirmations`) — **не** новый mega-nav.

### 4.8 Visual north star *(не Material, не Settings)*

Между Apple Health · Flighty · Gentler Streak · Arc · Headspace · Cosmic:

- минимум шума, крупная типографика, воздух, иллюстрации;
- глубина **постепенно**; ничего как таблица/справочник;
- каждый продукт проходит: **§5.4 standalone** + **§5.1 read/write** + retention 15 sec test.

### 4.9 Projection Model *(technical view)*

Для engineering/PIM — projections **читают/пишут** Personal Model. Продуктово — **карта §4.1**.

```
                    Personal Model
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
     Today            Compatibility         Tarot
   (dashboard)              │                  │
        │                  │                  │
        └──────── Growth ──┴──────────────────┘
                           │
                      Profile (hub)
```

**Сервисы** (Journal, Calendar, Settings…) — cross-cutting, не projections верхнего уровня.

### 4.10 Maps *(вторая половина TodayFlow)*

> **Today** отвечает: *Что происходит сегодня?*  
> **Maps** отвечают: *Каким становится моя жизнь?*

Maps — **не Journey**, не Artifacts, **не nav-item**, не «раздел трекеров». Это **живая история человека** — награда за жизнь в TodayFlow (Spotify Wrapped · GitHub graph · Strava year). **Не PIM в UI** — личные карты, которые **рисуются сами**.

**D30 / viral north star:** шерят **Maps** («30 дней тишины» · «Моя карта желаний 2026»), не прогноз и не «отчёт».

#### Треугольник Today · Profile · PIM

```
                    Personal Model
                          │
         ┌────────────────┼────────────────┐
         │                │                │
      Today           Profile            PIM
   «что сегодня»   «кто я + история»   atoms · patterns
         │                │                │
         └──── writes ────┴─── reads ──────┘
                          │
                    Map aggregation
                          │
              Product Output: карты + истории
              Learning Output: signals → atoms → CUM
```

| Угол | Роль для Maps |
|------|----------------|
| **Today** | **Источник точек** — каждое действие дня (+1 в Map): карта · число · mood · energy · practice · promise · evening close |
| **Profile** | **Дом Maps** — «Как меняется моя жизнь»; drill-down · living observations · share |
| **PIM** | **Движок смысла** — signals → interpretation → knowledge atoms → temporal patterns → **story render** (не mechanism в UI) |

**Запрещено:** отдельный «конструктор карт» или экран «заполни трекер». Человек **ничего специально не строит** — закрыл день → точка; неделя → узор; месяц → карта; год → история.

#### Два типа ценности

| Тип | Примеры | Зачем |
|-----|---------|-------|
| **Мгновенная** | Today · Tarot · Compatibility · Portrait | **Открыть сегодня** |
| **Накопительная (Maps)** | Mood · Energy · Habit · Ascetic · Goal · Wish · Relationship · Tarot · Theme · Symbol · Promise · Year | **Не бросить** · share |

Maps **не в nav**. Появляются в Profile · «Мои дни» · month-end · Wrapped — **My 2026**, не отчёт.

#### Два вопросы на каждое действие (§5.5)

1. **Что сейчас?** · 2. **+1 в какую Map?**  
Copy: «узор привычек растёт сам», не «отметьте привычку» / «откройте трекер».

#### Язык: истории, не статистика

В продукте **нет статистики** — только **истории** и **наблюдения** ([EXPLAIN_MEANING_NOT_MECHANISM.md](../explainability/EXPLAIN_MEANING_NOT_MECHANISM.md) · §5.8).

| ❌ | ✅ |
|----|---|
| Среднее настроение — 7,4 | Май стал самым спокойным месяцем этого года |
| Выполнено 26 целей | 26 раз ты сдержал обещание, которое дал самому себе |
| Алгоритм нашёл паттерн | Самые сильные дни чаще приходятся после полноценного сна |
| Completion rate 83% | Этим летом — самая длинная серия утренних практик |

#### Каталог карт *(north star · entity specs в Build Map)*

Каждая Map — **projection** Personal Model: data source · render · drill-down · story template · PIM `event_type`(ы).

| Map | Render | Drill-down (день / период) | Растёт из |
|-----|--------|----------------------------|-----------|
| **Mood** | heatmap (GitHub-style) | лунный аспект · усталость · невыполненное обещание | evening · mood chip |
| **Energy** | heatmap | сон · закрытие вчера · DayModel | energy mark · fusion |
| **Habit** | цветной календарь-узор (не чеклист) | streak как узор, не % | daily marks в Today |
| **Ascetic** | journey (башня · дерево · тропа) | shareable arc «30 дней тишины» | ascetic day close |
| **Goal / Promise** | timeline обещаний | дал · выполнил · перенёс · повтор | promise of the day |
| **Wish** | карта желаний | «ещё хочешь?» · маленький шаг | wish add · periodic check-in |
| **Relationship** | сеть кругов | внимание · темы · не % compat | compat · journal · people |
| **Tarot** | архетипическое путешествие | «чаще сопровождали Отшельник · Звезда» | card-of-day history |
| **Day theme** | темы года | спокойствие · перемены · решения · деньги | DailyTheme accumulation |
| **Symbol** | повторяющиеся якоря | цвет · стихия · камень · тотем | symbolic picks |
| **Cycle** *(контекст)* | **не** «день 16» — паттерны в других Maps | «в первой половине цикла чаще продуктивность» | cycle data → Today recommendations only |

**Женский цикл:** **никогда** главная тема экрана. Влияет на рекомендации дня (практика · медитация · аффirm · цель · вечерний разбор). Через месяцы — **наблюдение** в Maps/PIM, не календарь месячных.

#### Pipeline *(learning-aware · обязателен)*

```
Today action (signal)
  → event_type + payload (web ⇄ iOS ⇄ Android паритет)
  → Interpretation → Confirmation → Knowledge Atom
  → Map aggregation (temporal · cross-domain)
  → Story render (L1 heatmap · L3 drill-down · observation copy)
  → User correction («не про меня») → PIM update
```

**Launch seed:** evening + «Мои дни» + MapsPreview → первые точки. Full heatmaps + drill-down — **MP-*** в трекере. Wrapped **v2+**.

### 4.11 Monetization *(HYPOTHESIS — не решение; только поле)*

**Формула (проверить):** сегодня → польза · каждый день → большее · **неделя** → закономерности · **месяц** → карта жизни · **год** → share.

**Продаём непрерывность.** Не Premium / Pro → **«Продолжить свою историю»**.

#### Paywall trigger *(измерять)*

**Не «8 дней».** Paywall после **первого ощутимого результата** — день 5, 9 или 6 закрытых дней; **измерять на поле**.

**Триггер по полноте истории** *(пороги — гипотеза, калибровать)*:

| Сигнал | Пример минимума |
|--------|-----------------|
| Закрытые дни | 5–6 |
| Заполненные Today | 5 |
| Карты таро | 3 |
| Совместимости | 4 |
| Практики | 3 |

→ *«Вот что уже начинает складываться»* — честнее календаря.

#### Week 1 Wrapped *(маленький, красивый)*

Checklist фактов + **одна** мысль (*«чаще завершал день спокойнее»*). CTA **«Продолжить»** — достижение, не «trial ended». Не SaaS-copy.

#### Paywall anti-pattern

Не blur того, что только показали. Показать **полностью** → *«Следующая карта начнёт строиться завтра»*.

#### Freemium *(гипотеза)*

Free: Today lite · Compatibility · 1 tarot · Profile базовый.  
Paid: полный Today · **Maps** · история · practices · full Tarot · Wrapped. App не «умирает».

#### Pricing *(не фиксировать до поля)*

Зависит от: дизайн · Week 1 Report · **D7 retention**.  
**A/B monthly (EU):** €7.99 · €9.99 · €12.99 — max **выручка**, не только CR. Yearly/lifetime — после тестов.

**Launch:** monetization не блокер DoD #11; paywall + price — **волна 2**.


## 5. Законы (обязательные контракты)

### 5.1 Закон read/write

Любая projection **обязана** ответить:

1. **Что читает из Personal Model?**
2. **Что возвращает обратно в Personal Model?**

| Ситуация | Действие |
|----------|----------|
| Читает **и** пишет | Core projection — строим |
| Только читает | Подозрительно — guest или нужен write-path |
| Только пишет | Подозрительно — нужен read для персонализации |
| Ни то, ни другое | **Не core** — SEO, catalog, admin |

**Примеры read/write:** см. §5.1.1 в v0.1 — Today, Compatibility, Journal, Tarot, guest horoscope.

<details>
<summary>§5.1.1 Примеры read/write (развернуть)</summary>

**Today** — read: identity, карта, intent, patterns, вчера (journey), preferences · write: outcome, mood, picks, evening close, signals.

**Compatibility** — read: Model A + Model B · write: saved person, relationship lens, history.

**Journal** — read: current state, themes · write: thoughts, events, signals.

**Tarot (in Today)** — read: day context + identity · write: card choice, engagement.

**Guest horoscope by sign** — read: sign only · write: — → acquisition, not core.

**Compatibility (public entry)** — read: two birth inputs only · write: optional save after account → **standalone L1**; with account → read Personal Model → **Personal L2**.

</details>

### 5.4 Закон standalone value *(экосистема, не «разделы»)*

> **Every projection must provide standalone value.**

Каждая крупная projection проходит **два теста**:

1. **Может ли существовать как отдельный продукт?** (без аккаунта, без Today — полная ценность)
2. **Становится ли заметно ценнее внутри TodayFlow?** (через Personal Model)

| Уровень | Compatibility (пример) | Tarot · Numerology · Natal (аналог) |
|---------|------------------------|-------------------------------------|
| **Standalone** | Две даты → инсайты, %, рекомендации; SEO / share / TikTok | Карта дня, число, карта — сами по себе |
| **Personal** | «Зная **тебя**, в отношениях с этим человеком…» — через Model | Интерпретация через модель + история дней |

**Не «раздел приложения»** — **самостоятельный продукт** + **единая модель** = экосистема (как AirPods + Watch + Mac).

**Launch implication:** маршруты `/compatibility`, `/tarot`, `/numerology`, `/horoscope` — **не удалять**; E3 hook **добавляет** Personal-слой, не заменяет Public.

**Read/write (§5.1) + standalone (§5.4)** — оба обязательны для core projection.

### 5.2 Закон непрерывности *(сильнее UX-деталей)*

> **Personal Model никогда не сбрасывается.**

- Новый телефон → та же модель (account).
- Переустановка → восстановление через email/account.
- Новый Today / новая совместимость / новый projection → **продолжение**, не «день ноль».
- Смена UI или redesign → модель **не** обнуляется.

**Personal Model — единственная непрерывная сущность продукта.**  
Projections и экраны сменяются; модель **переносит** историю.

*(Implementation note: требует server-side persistence journey/atoms; localStorage-only paths — временный debt, не принцип.)*

### 5.3 Закон ясности *(важнее read/write для продукта)*

> **Любой Experience обязан делать Personal Model понятнее пользователю.**

Projection не только **использует** модель и **пишет** в неё — она помогает человеку **лучше понимать себя** через накопленное.

| Плохо | Хорошо |
|-------|--------|
| Today прочитал/записал — пользователь не почувствовал | «Вчера главным было…» — человек **видит** свою модель |
| Скрытый ML без отражения в UI | «Третий раз за неделю…» — модель **проявлена** |
| Profile = простыня справочника | Profile = «вот что накопилось **обо мне**» |

**Тест Experience:** после сессии пользователь может сказать *«я понял что-то о себе»* или *«это помнит меня»* — не *«мне выдали текст»*.

Read/write без clarity → **инфраструктура без продукта**.

### 5.5 Закон двойной ценности *(instant + Maps)*

> **Каждое значимое действие даёт ценность сейчас и +1 к будущей Map.**

| Вопрос | Пример |
|--------|--------|
| **Что сейчас?** | Карта дня · результат compatibility · insight Profile |
| **+1 в Map?** | Tarot Map · Mood Map · Habit Map · Relationship Map |

Maps — **не продукт для заполнения**; **награда** за использование (§4.10). Сильнее badges/achievements.

### 5.6 Закон невидимого механизма *(§1 · CLOSED)*

**Статус:** **CLOSED** 2026-07-01. Базовый закон TodayFlow **№1**. Не обсуждаем — применяем ко всем экранам · entities · текстам.

> **Граница архитектура ↔ продукт.** Внутри — PIM · DayModel · LLM · API · …  
> Снаружи для пользователя — **только:** астрология · нумерология · таро · **его жизнь**.

Каждая сущность: **Internal** (reads/writes/models) + **External** (вывод · смысл · L1–L4).  
Copy gate: [TODAYFLOW_PRODUCT_BUILD_MAP.md](../TODAYFLOW_PRODUCT_BUILD_MAP.md) §1.

### 5.7 Закон позитивного определения *(§2 · CLOSED)*

**Статус:** **CLOSED** 2026-07-01. Базовый закон TodayFlow **№2**. Не обсуждаем — применяем везде.

> **Любая сущность, экран, функция и текст описываются через свою ценность для пользователя.**  
> **Никогда — через свои ограничения или отличия от других сущностей.**

**Всегда:** что это · зачем человеку · что даёт. **Никогда:** чем не является · почему не похоже на X · почему лучше Y.

Spec gate: [TODAYFLOW_PRODUCT_BUILD_MAP.md](../TODAYFLOW_PRODUCT_BUILD_MAP.md) §2.  
**Два закона** (§5.6 + §5.7) — автоматически для каждой новой сущности и экрана. К законам **не возвращаемся**.

Personal Model как единственный источник персонализации — § выше в этом документе + [PERSONAL_INTELLIGENCE_LAYER.md](../pim/PERSONAL_INTELLIGENCE_LAYER.md).  
Разрыв с кодом: [audits/PERSONAL_MODEL_CODE_COMPLIANCE_2026-07-21.md](../audits/PERSONAL_MODEL_CODE_COMPLIANCE_2026-07-21.md).

### 5.8 Закон историй *(Maps language · ACTIVE)*

**Статус:** **ACTIVE** 2026-07-02. Связан с §4.10 · [EXPLAIN_MEANING_NOT_MECHANISM.md](../explainability/EXPLAIN_MEANING_NOT_MECHANISM.md).

> **В продукте нет статистики и трекеров — только карты и истории.**

| Запрет (user-facing) | Замена |
|---------------------|--------|
| трекер · tracking hub | карта · история · «Мои дни» |
| статистика · % · completion rate · average | наблюдение · история · «самый … месяц» |
| алгоритм нашёл · система определила | «за последние месяцы…» · «ты чаще…» |

Copy type для Map insights — **«Наблюдение»** (EXPLAIN_MEANING §1), не audit language. Map drill-down L3 — язык предметной области: луна · число · карта · **твоя история**.

---

## 6. Reference Layer

> Reference существует **только** чтобы делать Personal Model умнее. **Никогда наоборот.**

- Пользователь взаимодействует с **Personal Model** (через projections), **не** со справочником.
- ~180 сущностей Reference — **двигатель**, не контент для ленты.
- Запрещено: «раздел Reference», простыня планет/домов вместо модели.
- Разрешено: 1–3 строки смысла из модели («опора дня — …»).

См. [REFERENCE_LAYER_AND_BUILD_ORDER.md](../REFERENCE_LAYER_AND_BUILD_ORDER.md).

---

## 7. PIM vs Personal Model

| | **PIM** | **Personal Model** |
|---|---------|-------------------|
| **Природа** | Инфраструктура | **Продуктовая сущность** |
| **Роль** | atoms, signals, gate, learning | то, что **растёт** и **ощущается** |
| **В UI** | Никогда напрямую | Через projections + clarity law |

PIM **обновляет** Personal Model.  
«PIM вырос (Learning Δ)» ≠ успех продукта, пока projection не сделала модель **понятнее** и **полезнее завтра**.

См. [PIM_PRODUCT_NORTH_STAR.md](./PIM_PRODUCT_NORTH_STAR.md).

---

## 8. Цепочка системы

```
Reference Layer
      ↓  (смыслы, rules)
    PIM / PIL
      ↓  (signals → atoms → model update)
 Personal Model          ← ★ продуктовый центр ★
      ↓  (read / write / clarify)
  Projection
      ↓  (package, copy, UI)
  Experience
      ↓
     User
```

**Не:** `PIM → Today`.  
**Да:** `PIM → Personal Model → Today`.

---

## 9. Profile (экран) — роль в модели

**Profile** — не «натальная карта на 40 экранов».

Внутренняя роль: **Life Intelligence hub** — обзор Personal Model и вход в глубину (**clarity** + **lifecycle stage** visible).

| Блок (conceptual) | Projection of |
|-------------------|---------------|
| Identity strip | stable facts · Stage 1+ |
| **Мои дни / Maps** | temporal accumulation · Stage 3+ · shareable |
| Моя карта | astrology/numerology depth |
| Совместимости | saved people · Stage 2+ |
| Глубокие слои | natal, patterns · Stage 4–5 |

Profile **не** first payoff. Today **открывает дверь**; Profile **показывает, что модель растёт**.

---

## 10. Критерий новой функции

Перед любой feature / Epic:

1. Какую **projection** создаёт или усиливает?
2. Что **читает** из Personal Model?
3. Что **пишет** обратно?
4. **Делает ли модель понятнее** пользователю? (закон ясности)
5. На каком **lifecycle stage** это работает?
6. Если 2–4 = «ничего» — **не core**.

Launch filter:

> Влияет ли это на то, что пользователь увидит **завтра утром** и **поймёт ли, что это про него**?

---

## 11. Связь с launch (Blueprint)

**Builder SoT:** [TODAYFLOW_PRODUCT_BUILD_MAP.md](../TODAYFLOW_PRODUCT_BUILD_MAP.md) — Entity Catalog · Design Tokens · 6-step law.  
**Launch feel/do (reference):** [status/WEB_LAUNCH_PRODUCT_BLUEPRINT.md](../status/WEB_LAUNCH_PRODUCT_BLUEPRINT.md).  
**Gaps / DoD:** [status/WEB_LAUNCH_EXECUTION_PLAN.md](../status/WEB_LAUNCH_EXECUTION_PLAN.md).

[WEB_LAUNCH_PRODUCT_BLUEPRINT.md](../status/WEB_LAUNCH_PRODUCT_BLUEPRINT.md) — execution slice:

`Landing → bootstrap Identity (Stage 1) → Today projection → evening write → D2 continuity (Stage 3 Growing)`

Реализует минимальный loop: **read / write / clarify** через Today.

---

## 12. Changelog

| Date | Version | Change |
|------|---------|--------|
| 2026-07-01 | 0.4.8 | §5.7 canonical · **два базовых закона** §5.6+§5.7 |
| 2026-07-21 | 0.4.9 | Убран ошибочный «третий закон»; Stories остаётся §5.8; link code compliance |
| 2026-07-01 | 0.4.7 | §5.7 **CLOSED** — Positive Definition |
| 2026-07-01 | 0.4.6 | §5.6 **CLOSED** — 4 user knowledges · dual Internal/External per entity |
| 2026-07-01 | 0.4.5 | §5.6 Закон невидимого механизма |
| 2026-07-01 | 0.4.4 | §4.11 refined: story-threshold paywall; no fixed day/price; Week-1 mini-Wrapped |
| 2026-07-01 | 0.4.3 | §4.11 Monetization HYPOTHESIS (superseded thresholds) |
| 2026-07-01 | 0.1 | DRAFT: projection-first, Personal Model vs Profile screen, read/write law |
