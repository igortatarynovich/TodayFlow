# TodayFlow — Product Build Map

**Статус:** **ACTIVE** — **главный документ продукта**.  
**Версия:** 0.7.2  
**Дата:** 2026-07-03  
**Текущая работа:** **React Today** *(Composition v1 🟢 — продуктовых обсуждений больше нет)*

> **Правило:** проектируем **сущности продукта**. React · CSS · Figma — **после** entity spec 🟢.  
> Экран = вторичен. Today = набор entities. Profile = проекции тех же entities + накопление.

---

## Главный закон *(6 шагов — всегда в этом порядке)*

```
1. Пользовательский вопрос
        ↓
2. Продуктовый ответ
        ↓
3. Сущность (Entity)          ← единица продукта, не UI
        ↓
4. Источники данных
        ↓
5. Проекции (где ещё живёт)
        ↓
6. React-компонент            ← только после entity 🟢
```

*(Design Tokens · layout — после entity inventory.)*

**Пример · `DailyTheme`:**

| Шаг | Содержание |
|-----|------------|
| **Вопрос** | Что сегодня **главное**? |
| **Ответ** | Главная **тема дня** |
| **Сущность** | `DailyTheme` |
| **Источники** | Day Model · Profile |
| **Проекции** | Today · Weekly · Profile · Wrapped |
| **React** | `<DailyTheme />` — layout меняется, сущность нет |

Если начать с `ThemeCard.tsx` — мышление UI-first и через год сотни одноразовых компонентов.  
Если начать с **сущности** — десятки стабильных смыслов с множеством проекций.

**Код запрещён**, пока сущность sprint не **🟢** (шаги 1–5 + §Today Entity Pattern + **два базовых закона** §1–§2).

---

## §Два базовых закона *(CLOSED — не обсуждаем, применяем автоматически)*

| # | Закон | Применение |
|---|--------|------------|
| **§1** | **Невидимый механизм** | Experience · copy · L1–L4 |
| **§2** | **Позитивное определение** | Product Model · Build Map · Screen/Entity Specs · UX · onboarding · paywall · empty states · marketing |

Новая сущность · экран · функция · текст — **сразу** через оба закона. К законам **не возвращаемся**.

---

## §1 · Закон невидимого механизма *(CLOSED — не обсуждаем, применяем везде)*

**Статус:** **CLOSED** 2026-07-01. Граница **архитектура ↔ продукт**. Copy gate G1–G5 — обязателен автоматически.

> **TodayFlow не объясняет, *как* он думает.** Только **почему** вывод имеет смысл.

### Внутри может быть что угодно · снаружи — только четыре знания

**Internal (существует для команды):** PIM · Personal Model · DayModel · Knowledge Atoms · Reference · LLM · API · интерпретации · любые модели.

**External (существует для пользователя) — только:**

| # | Что пользователь «знает» |
|---|------------------------|
| 1 | **Астрология** |
| 2 | **Нумерология** |
| 3 | **Таро** |
| 4 | **Его собственная жизнь** (история · паттерны · привычки · дни) |

Весь Experience собирается **только** из этих четырёх. Движок **⛔**.

### Два описания каждой сущности *(обязательно)*

| | **Internal** *(spec / dev)* | **External** *(UI / copy)* |
|---|---------------------------|---------------------------|
| **Что** | reads · writes · dependencies · models · API | **только** вывод · смысл · L1–L4 |
| **Язык** | Day Model · PIM · events · schemas | астрология · нумерология · таро · **жизнь человека** |
| **Пример Tarot** | Tarot engine + Day Model + card ID | «Сегодня **Сила** хорошо сочетается с темой дня…» |
| **Пример Profile** | pattern detection · atoms | «**Последние недели** тема отдыха возвращалась чаще обычного» |
| **Пример Number** | numerology weight in assembler | «**Число дня** усиливает стремление завершать начатое» |
| **Пример life** | PIM correlation · signals | «**За последнее время** ты чаще чувствовал прилив энергии после прогулок» |

### ⛔ / ✅ *(закрытый список)*

| ⛔ | ✅ |
|----|-----|
| «Система сопоставила карту…» | «Сегодня карта **Сила** хорошо сочетается с темой дня…» |
| «Мы нашли повторяющийся паттерн…» | «Последние недели тема отдыха возвращалась чаще обычного» |
| «Алгоритм повысил вес…» | «Сегодняшнее **число дня** усиливает…» |
| «PIM обнаружил корреляцию…» | «**За последнее время** ты чаще чувствовал… после прогулок» |

### Copy gate G1–G5

Fail → переписать, не ship. Без исключений для экранов · entities · push · Profile · Compatibility.

---

## §2 · Закон позитивного определения *(CLOSED — не обсуждаем, применяем везде)*

**Статус:** **CLOSED** 2026-07-01. Фундаментальный · наравне с §1.

> **Любая сущность, экран, функция и текст описываются через свою ценность для пользователя.**  
> **Никогда — через свои ограничения или отличия от других сущностей.**

### Всегда отвечаем

- **Что это?**
- **Зачем это человеку?**
- **Что это ему даёт?**

### Никогда не отвечаем

- Чем это **не является**?
- Почему это **не похоже** на X?
- Почему это **лучше** Y?

### Примеры *(автоматический rewrite)*

| ❌ | ✅ |
|----|-----|
| «Это не гороскоп.» | «Today помогает быстрее понять **характер** сегодняшнего дня.» |
| «Это не натальная карта.» | «Профиль объединяет все знания о человеке в **одну персональную картину**.» |
| «Это не список практик.» | «Сегодня Today предлагает **одну** практику, которая лучше всего поддерживает тему дня.» |
| «У вас пока нет данных.» | «Начните **создавать свою историю**.» |

### Где действует *(везде)*

Product Model · Build Map · Screen Specs · Entity Specs · UX copy · onboarding · paywall · empty states · marketing.

### В entity spec

Только про **эту** entity: **Роль** · **Зачем** · **Суть** / **Ценность** · L1–L4.  
Границы entity ID — в **Internal** *(dev)*, без сравнительных формулировок в product spec.

**Copy gate:** определение сущности через «не / нет / отсутствует / unlike X» → **fail**, переписать.

---

## §Today Entity Pattern *(системный принцип)*

### Роли — каждая сущность свой вопрос *(не повторять одну мысль)*

| Entity | Вопрос | Роль |
|--------|--------|------|
| `DailyTheme` | **О чём** сегодняшний день? | Смысл / тема («День ясности») |
| `DailyFocus` | **Куда** смотреть? | Внимание (descriptive) |
| `DailyEnergy` | **В каком темпе** жить? | **Режим и темп** дня («меньше, но глубже») |
| `DailyGuidance` | **Как** действовать? | 2–3 do |
| `DailyWarnings` | **Чего** избегать? | 1–3 мягких don't |
| `PracticeRecommendation` | Что **лучше всего поможет прожить** день? | **Одна** практика |

`DailyEnergy` **кормит** Guidance · Warnings · Practice — задаёт **ритм**, не дублирует Theme.

**Theme vs Energy (пример):**

| | Theme | Energy |
|---|-------|--------|
| Вопрос | О чём день? | В каком темпе? |
| Пример | «Ясность» | «Не торопись — меньше, но глубже» |
| | | «Хороший день для быстрых решений» |

---

### Два уровня *(каждая сущность Today)*

**Уровень 1 — быстрый (30–60 сек)**  
Достаточно закрыть приложение и жить. Theme · Focus · Energy · Guidance · Warnings — короткие выводы.

**Уровень 2 — «Почему так?»**  
Глубина по желанию — **язык предметной области** (луна · число · карта · цикл · **твоя** история).  
⛔ PIM · DayModel · API · «алгоритм» · «ИИ» — см. §Invisible Mechanism.

---

### Четыре слоя *(единая структура каждой сущности — Experience)*

| # | Слой | Время | Содержание | Язык |
|---|------|-------|------------|------|
| **L1** | Короткий вывод | ~5 сек | Одна строка / режим / пункт | человек |
| **L2** | Лично для тебя | ~20 сек | Что значит **для меня** сегодня | человек |
| **L3** | Почему так | expand | **Почему имеет смысл** — луна · число · карта · цикл · паттерн из истории | **предметная область** |
| **L4** | Подробнее | deep link | Трактовка · Profile · библиотека | предметная область |

**L3** — факторы **как явления** («Луна в…», «число дня…»), не как pipeline («PIM slice»).

---

### Источники в entity spec — **Internal / External**

Каждая entity spec **две колонки** (см. §Invisible Mechanism):

| **Internal** | **External (L1–L4 copy)** |
|--------------|---------------------------|
| Input: Day Model · PIM · API · dependencies | Output: астрология · нумерология · таро · **жизнь человека** |
| Writes: events · schemas · learning path | Writes: как прожил · совпало · помогло — **продуктово** |

---

### Writes в entity spec

Пишем **продуктово**, не event names:

- как человек **прожил** день;
- **совпал** ли рекомендуемый темп/фокус с реальностью;
- что **помогло** / **мешало**;
- материал для **Maps** и будущего анализа.

---

## Две параллельные оси

Экран **не владеет** сущностью. Экран **использует** сущность с токенами проекции.

```
AXIS A · Пользовательская (вертикаль)          AXIS B · Сущностная (горизонталь)
────────────────────────────────────          ────────────────────────────────────
Landing                                       Hero · Insight · Summary · Timeline
  ↓                                           Chart · Heatmap · Practice · Goal
Onboarding                                    Tracker · Symbol · Match · Reading …
  ↓
Today              ←── composes ──→           DailyTheme · DailyFocus · DailyEnergy · DailyGuidance …
Evening
  ↓
Day 2
  ↓
Compatibility        ←── composes ──→          CompatibilityMatch · CompatibilityInsight
  ↓
Tarot                ←── composes ──→          TarotReading · CardOfDay
  ↓
Profile              ←── composes ──→          Portrait · DaysTimeline · MapsPreview
```

**Владелец смысла:** §Entity Catalog.  
**Экран:** composition map — какие entities + какие Design Tokens на этой проекции.

---

## Как пользоваться

| Что | Ось | Когда |
|-----|-----|-------|
| Foundation | — | Phase 0 ✅ |
| User Journey | **A** | Phase 1 |
| Entity Catalog | **B** | параллельно — **сейчас: Today inventory** |
| Design Tokens | **B** | *после* entity specs 🟢 |
| Screen Compositions | A×B | Phase 2 — экран = entity list + tokens |
| Layout | A | Phase 3 |
| Data Flow | B | Phase 4 — **на entity**, не на экран |
| Build Order | A+B | Phase 5 → React |
| Polish | — | Phase 6 |

---

## §Entity Rules *(обязательно)*

| # | Правило |
|---|---------|
| E1 | **Сущность** именуется по **смыслу**, не по UI (`DailyTheme`, не `ThemeCard`) |
| E2 | Экран **не владеет** — только **uses** entity + projection tokens |
| E3 | **Один Entity ID** — один смысл навсегда |
| E4 | Новая проекция = та же entity + другие tokens, не новый ID |
| E5 | React PR **только** если entity 🟢 в каталоге |
| E6 | UI на экране **только** из каталога — нет orphan blocks |
| E7 | Deprecate entity → пометка в каталоге; не `DailyThemeV2` |
| E8 | **§1 Invisible Mechanism (CLOSED)** — dual Internal/External; 4 user knowledges only |
| E9 | **§2 Positive Definition (CLOSED)** — ценность для пользователя; без ограничений и отличий от других |

---

## §Design Tokens *(продуктовые, не CSS)*

Токены описывают **как сущность проявляется** на конкретной проекции. Один entity — разные tokens на Today vs Profile.

### Size

`XS` · `S` · `M` · `L` · `XL`

### Priority

`Hero` · `Primary` · `Secondary` · `Supporting` · `Decorative`

### Reveal

`Always` · `Collapsed` · `Expandable` · `Premium` · `Unlocked`

### Behavior

`Interactive` · `Static` · `Selectable` · `Swipeable` · `Dismissible`

### Projection shorthand

`Today · DailyTheme · L · Hero · Always · Static`  
`Profile · DailyTheme · M · Secondary · Collapsed · Expandable`

---

## Phase 0 · Foundation *(Done)*

| | |
|---|---|
| **Продукт** | Персональный ежедневный ориентир — точнее со временем; **помнит вчера** |
| **4 продукта** | Today · Profile · Compatibility · Tarot |
| **Services** | practice · habit · ascetic · affirmation · cycle · symbols — **внутри Today** |
| **Maps** | накопительная ценность в Profile — **вторая половина продукта** ([TODAYFLOW_PRODUCT_MODEL.md](./TODAYFLOW_PRODUCT_MODEL.md) §4.10) |
| **UI-закон** | ответы, не дисциплины |

**Формула:** `today → value · each day → more · week → patterns · month → life map · year → share`

### Current ship wave *(wave 1)*

```
Landing → onboarding → First Today → Evening → D2 → Compatibility hook → Profile min
```

| In | Out |
|----|-----|
| value-first onboarding | auth-first |
| TodayOverview + core entities | full entity library |
| Compatibility Public L1 | all projection types |
| CardOfDay in Today | full Tarot flow |
| Profile min | natal wall |
| localStorage continuity | server persist |

---

## Axis A · Phase 1 · User Journey *(screen gate — 2026-07-01)*

```
Landing → Имя → DOB → reward → [место/время] → email → Today → Evening → D2+ → Compatibility · Tarot · Profile
```

**Правило:** один экран = один gate. ✅ только когда **история реализована в React**, не «spec 🟢» и не «частично спрятали».  
Walkthrough / field test — **после** последнего ✅ в таблице.

| # | Screen | Feeling / gate | React | Status |
|---|--------|----------------|-------|--------|
| 1 | **Landing** | Curiosity → «Создать мой Today» | Hero + vitrine 6 cards · demo off · CTA signup | ✅ |
| 2 | **Имя** | Диалог, не регистрация | `/onboarding/welcome` · guest draft | 🟡 |
| 3 | **Дата рождения** | Жду reveal | `/onboarding/birth` · sign + life path | 🟡 |
| 4 | **Первый результат** | «Это про меня» **до** email | `/onboarding/preview` | 🟡 |
| 5 | **Место · время · email** | Сохраняю полученное | refine optional · `/onboarding/save` · `POST /auth/email-signup` | 🟡 |
| 5b | **Intent · Reality chips** | Контекст дня | `/onboarding/intent` · `/reality` · **после** auth | 🟡 *(placement OPEN — story gate)* |
| 6 | **First Today** | «Понял фокус — вечером проверю» | `/today?first=1` · `TodayCompositionSurface` · `firstToday` | ✅ |
| 7 | **Evening** | «День закрыт — что завтра?» | `EveningClose` в Composition · D1 path | ✅ |
| 8 | **D2+ Today** | «Помнит вчера — история» | `/today` default · `ContinuityRecall` slot 0 | ✅ |
| 9 | **Compatibility hook** | Следующий слой исследования | Explore card · return/new CTA · `/compatibility` | ✅ |
| 9b | **Compatibility return** | Не dead end | Public flows exist · return path не проверен end-to-end | 🟡 |
| 10 | **Tarot in Today** | Symbol in day | `DailyTarot` в Symbols zone · `/tarot` explore bridge | ✅ *(launch = in Today, not full flow)* |
| 11 | **Profile min** | «Растёт история» | `ProfileLaunchMinScreen` · identity strip · Мои дни · MapsPreview · chart teaser · compat · deep collapsed | ✅ |

### §Conversation Structure *(launch path — structure before copy)*

**Принцип:** экран = **нить диалога** (практик → ответ пользователя), не форма и не каталог карточек.

| Turn ID | Screen | Role | React |
|---------|--------|------|-------|
| `welcome_name` | `/onboarding/welcome` | practitioner + reply | `ValueFirstOnboardingShell` · `ConversationTurn` |
| `birth_date` | `/onboarding/birth` | practitioner + reply | same |
| `preview_recognition` | `/onboarding/preview` | speech + deepen + CTAs | `FirstResultScreen` · `ConversationThread` |
| `refine_optional` | `/onboarding/refine` | deepen optional | shell |
| `today_opening` | `/today?first=1` | greeting | `TodayCompositionSurface` · `firstToday` |
| `today_checkin` | same | user mood/focus | `TodayDayDialogueMorning` in turn response |
| `today_focus` | same | theme + pulse | turn message |
| `today_ritual` | same | tarot/number invite | turn without «Шаги дня» chrome |
| `today_close` | same | evening | `EveningClose` |
| `save_invite` | `/onboarding/save` | practitioner + email | shell · guest close prompt |

**Script (IDs only):** `frontend/src/lib/conversationStructure.ts` · **UI:** `frontend/src/components/conversation/*`

**firstToday zones:** no `glance` · no `astroContext` · no continuity · no ritual step bar.

**Copy gate:** тексты launch path переписаны под тон «приём у специалиста» (2026-07-03) · `valueFirstOnboardingCopy.ts` · `buildFirstResultModel.ts` · `todayCompositionCopy.ts` · `todayDayDialogue.ts`

**Launch scope remaining (ordered):**

1. **Intent/Reality placement** — story gate (inside First Today vs after reward)
2. **Launch path hygiene** — returning-user routing · auth-first path for login only
3. **Field test prep** — walkthrough after polish

**Done — не reopen без story-gate fail:** Composition Today v1 · evening · D2 continuity · compat hook · landing · redirects → `?first=1`.

*(Screen feelings — Blueprint §Launch Story; не дублируем copy здесь.)*

---

## Today · Entity Inventory *(WORKING)*

**Экран Today** = composition этих сущностей. Ничего уникального «только для Today UI».

### Карта вопрос → ответ → сущность

| User question | Product answer | Entity ID |
|---------------|----------------|-----------|
| Что сегодня **главное**? | Главная **тема** дня | `DailyTheme` |
| На каком **темпе** жить? | **Режим** дня | `DailyEnergy` |
| На что **обратить внимание**? | Главный **фокус** | `DailyFocus` |
| Что **вероятно произойдёт**? | Возможные **события** | `DailyEvents` |
| Что **лучше делать**? | **Рекомендации** | `DailyGuidance` |
| Чего **избегать**? | **Предупреждения** | `DailyWarnings` |
| Какое **настроение** дня? | Mood дня | `DailyMood` |
| Какая **карта** дня? | Карта Таро | `DailyTarot` |
| Какое **число** дня? | Число дня | `DailyNumber` |
| Какие **символы**? | Камень · цвет · тотем · стихия… | `DailySymbols` |
| Что **лучше всего поможет прожить** день? | **Одна** практика | `PracticeRecommendation` |
| Какую **цель** поставить? | Цель дня | `DailyGoal` |
| Что **отметить**? | Привычки · аскезы · цикл | `DailyTracking` |

**Loop-сущности** *(не контент дня, но часть Today)*:

| User question | Entity ID |
|---------------|-----------|
| **С чего** продолжить сегодня? | `ContinuityRecall` |
| Как **завершить** день? | `EveningClose` |

---

### Проверка каждой сущности

| Entity | Ценность 🟢 | Источники (draft) | Проекции | В коде сейчас |
|--------|-------------|-------------------|----------|---------------|
| `DailyTheme` | характер дня за 3–5 сек | profile · natal · transits · numerology · history · reference | Today · Weekly · Monthly · Year · Profile | 🟡 `FirstToday` theme block; ritual surface — отдельно |
| `DailyFocus` | куда направить внимание | DailyTheme · intent/reality · yesterday · DayModel · Profile · history | Today · Evening · D2 · Profile · Maps | 🟢 spec · код: fix theme leak |
| `DailyEvents` | probabilistic layer | DayModel · transits | Today · Weekly | ❌ |
| `DailyGuidance` | 2–3 действия на день | Theme · Focus · DayModel · domains · Profile · history | Today · Weekly · Profile · Maps | 🟢 spec · 🟡 код |
| `DailyWarnings` | мягкая защита дня | tension · Profile risks · transits · yesterday · reality | Today · Evening · Profile · Week | 🟢 spec · 🟡 код |
| `DailyEnergy` | **темп и режим** дня | Day Model · `DailyTheme` | Today · Profile · Maps · feeds Guidance | ❌ score UI — вне scope |
| `DailyMood` | emotional tone | check-in · DayModel · history | Today · Profile · Maps | 🟡 spine mood disabled in code |
| `DailyTarot` | symbol + meaning | Tarot engine · reference | Today · Tarot · Profile | ✅ ritual pick |
| `DailyNumber` | число **этого** дня | Day Model · numerology · Profile context | Today · Profile · Week | 🟢 spec · ritual reveal |
| `DailySymbols` | якоря дня | Day Model · symbolic reference | Today · Profile · Wrapped | 🟢 spec · 🟡 teaser only |
| `PracticeRecommendation` | прожить день через действие | Day Model · Theme · Energy · Tarot · Number · Profile · history | Today · Weekly · Profile · Maps · Wrapped | 🟢 spec · ✅ Composition |
| `DailyGoal` | goal for today | goals system | Today · Profile | 🟡 teaser default |
| `DailyTracking` | habits · ascetic · cycle | habit · cycle engines | Today · Profile · Maps | 🟡 teaser default |
| `ContinuityRecall` | мост вчера → сегодня · память о прожитом дне | `day_continuity` · EveningClose write | Today D2+ · Profile · Weekly · Wrapped | 🟢 spec · ✅ Composition default |
| `EveningClose` | завершить день · **причина вернуться завтра** | `DailyFocus` · `day_continuity` write | Today · Profile · feeds `ContinuityRecall` | 🟢 spec · ✅ Composition D1+D2 |

**Wave 1 Today (entities):** Theme · Focus · Guidance · Warnings · Energy · Tarot · Number · Symbols (subset) · PracticeRecommendation · ContinuityRecall · EveningClose.

**Отложить wave 1:** Events · Mood (until check-in) · Goal · Tracking (teaser ok).

---

### `DailyTheme` *(entity spec 🟢)*

| | |
|---|---|
| **Роль** | **О чём** сегодняшний день |
| **User question** | Что сегодня **главное**? / О чём этот день? |
| **Product answer** | Одна фраза — **тема** («День ясности») |
| **Зачем** | За **3–5 сек** понять **характер** сегодняшнего дня |
| **L1** | «День ясности» |
| **L2** | 1–2 предложения — что это значит **лично** сегодня |
| **L3 · Почему?** | Факторы человеческим языком (луна · число · цикл · карта · история…) |
| **L4** | Profile · натал · библиотека |
| **Источники** | **Day Model** · Profile · history |
| **Writes** | прочитал тему · **узнал почему** · совпала ли тема с прожитым днём → Maps |
| **Проекции** | Today · Weekly · Monthly · Year · Profile |
| **React** | ⬜ |

---

### `DailyFocus` *(entity spec 🟢)*

| | |
|---|---|
| **Роль** | **Куда** смотреть |
| **User question** | На что **сегодня** обратить внимание? |
| **Product answer** | **Один** главный фокус |
| **Тон** | Описательный: «Обрати внимание на X» |
| **L1** | Одна строка фокуса |
| **L2** | Почему это важно **сегодня** для тебя |
| **L3 · Почему?** | Факторы предметной области + Theme + вчера + intent/reality |
| **L4** | Profile · «Мои дни» |
| **Источники** | **Day Model** · `DailyTheme` · Profile · **вчерашний outcome** · intent/reality · history |
| **Writes** | принял фокус · evening outcome · повторяющиеся фокусы → **Focus Map** |
| **Проекции** | Today · `EveningClose` · D2 · Profile · Week · Month Maps |
| **Код** | `TodayDailyFocusBlock` — отделить от Theme |
| **React** | ⬜ |

---

### `DailyGuidance` *(entity spec 🟢)*

| | |
|---|---|
| **Роль** | **Как** действовать |
| **User question** | Что сегодня **лучше делать**? |
| **Product answer** | **2–3** рекомендации · ≤3 пункта |
| **Тон** | Коротко · сегодня · 2–3 **коротких действия** на день |
| **L1** | Bullet list (2–3) |
| **L2** | Как это связано с Theme + Energy **сегодня** |
| **L3 · Почему?** | Транзиты · число · карта · domains — **человеческим языком** |
| **L4** | Profile insights |
| **Источники** | **Day Model** · `DailyTheme` · `DailyFocus` · `DailyEnergy` · Profile · history |
| **Writes** | прочитал · сохранил/отклонил · **выбрал пункт** · совпало с днём |
| **Проекции** | Today · Weekly · Profile · Maps |
| **Код** | `primary_action` · domain `action` → entity |
| **React** | ⬜ |

---

### `DailyWarnings` *(entity spec 🟢)*

| | |
|---|---|
| **Роль** | **Чего** избегать |
| **User question** | Чего сегодня **лучше избегать**? |
| **Product answer** | **1–3** мягких предупреждения |
| **Тон** | Защита, не страх · не запрет |
| **L1** | 1–3 коротких строки |
| **L2** | Что будет, если проигнорировать **мягко** |
| **L3 · Почему?** | Луна · напряжённые аспекты · вчерашний день · текущий ритм — **не** «risk pattern detected» |
| **L4** | Profile risks |
| **Источники** | **Day Model** · Profile · `DailyEnergy` · **вчерашний outcome** · reality chip |
| **Writes** | прочитал · полезно/игнор · **risk pattern** для Maps |
| **Проекции** | Today · Evening · Profile · Week · Month |
| **Код** | domain `risk` → entity |
| **React** | ⬜ |

---

### `DailyEnergy` *(entity spec 🟢)*

| | |
|---|---|
| **Роль** | **В каком темпе** жить — **режим дня**, не «батарейка» |
| **User question** | На каком **темпе** сегодня лучше жить? |
| **Product answer** | **Рекомендуемый ритм** — не 8/10 |
| **Зачем** | Практичнее «уровня энергии» — **как прожить** Theme |
| **Режимы** *(примеры label)* | День ускорения · Спокойный · Наблюдения · Общения · Концентрации · Восстановления · Перемен |
| **L1** | Режим + одна строка («Сегодня лучше не спешить») |
| **L2** | Как прожить Theme в этом темпе («меньше, но глубже» / «быстрые решения») |
| **L3 · Почему?** | «Сегодня сочетание личного числа дня и фазы Луны…» — **не** «Day Model показала» |
| **L4** | Profile · циклы · Maps |
| **Источники** | **Day Model** · `DailyTheme` · Profile · history |
| **Feeds** | `DailyGuidance` (тон) · `DailyWarnings` (от чего беречь) · `PracticeRecommendation` (какой тип) |
| **Writes** | рекомендуемый темп · **как прожил** · совпал/не совпал · помогло/мешало → **Energy Map** |
| **Проекции** | Today · EveningClose · Profile · Week · Month Maps |
| **React** | ⬜ — **запрещено** «Energy: 8/10» как продукт |

**Пример L1 (30 сек Today):**

```
Тема:     День ясности.
Фокус:    Решения, которые откладываешь.
Энергия:  Сегодня лучше не спешить.
Делать:   • закончить начатое • говорить прямо • время на размышления
```

---

### `DailyTarot` *(entity spec 🟢)*

| | |
|---|---|
| **Роль** | **Символ дня** — одна карта в контексте **сегодня** |
| **User question** | Какая **карта** сегодня? / Что она говорит **мне сейчас**? |
| **Product answer** | Карта + смысл **в связке с темой дня** — не полный расклад |
| **Зачем** | Символический слой; углубляет Theme без отдельного «продукта Таро» |
| **L1** | Название карты + одна строка («Отшельник — день тишины и ясности») |
| **L2** | Что это значит **лично для тебя сегодня** (с Theme · Energy) |
| **L3 · Почему?** | «Карта хорошо сочетается с темой дня… ответы проще в спокойствии, чем в спешке» — **таро + день**, не pipeline |
| **L4** | Полная трактовка карты · история раскладов · Tarot product |
| **Источники (internal)** | Day Model · `DailyTheme` · tarot reference · Profile |
| **Жест** | Пользователь **может** тянуть карту (ритуал) — но entity = **смысл после reveal** |
| **Writes** | прочитал · сохранил · «откликнулось» · связь с днём → Tarot Map seed |
| **Проекции** | Today · Profile «Мои карты» · Week review |
| **Код** | ritual pick в `TodayExperienceSurface` — entity boundary + L3 copy |
| **React** | ⬜ |

**L3 — ✅ пример:**  
«Сегодня Отшельник сочетается с темой ясности. Он напоминает, что ответы проще найти в спокойствии, чем в спешке.»

**L3 — ⛔ запрещено:**  
«Система выбрала карту на основании DayModel…» · «Алгоритм определил карту дня…»

---

### `DailyNumber` *(entity spec 🟢)*

| | |
|---|---|
| **Роль** | **Число дня** — нумерологический слой **сегодня** (не life path) |
| **User question** | Какое **число** сегодня? / Что оно значит **для меня сейчас**? |
| **Product answer** | Число дня + смысл в контексте **этого** дня — не «ваш life path» |
| **Зачем** | Второй символический якорь (рядом с Tarot); усиливает Theme · Guidance |
| **L1** | Число + одна строка («**7** — день завершения и ясности») |
| **L2** | Что это значит **лично для тебя сегодня** (с Theme · Energy · Focus) |
| **L3 · Почему?** | «**Число дня** усиливает стремление завершать начатое» · связь с личным циклом — **нумерология**, не engine |
| **L4** | Life path · expression · полная нумерология в Profile |
| **Internal** | Day Model · numerology engine · personal day calc · Profile life path *(context)* · events |
| **External** | **Нумерология** + **твоя жизнь** (если L2) — §Invisible Mechanism |
| **Жест** | Reveal в ritual — entity = **смысл после показа**, не процесс выбора |
| **Writes** *(product)* | прочитал · сохранил · «откликнулось» · как число **сложилось** с днём → Maps |
| **Проекции** | Today · Profile (numerology) · Week review |
| **Код** | `numerology_number` · `RitualNumberPickExperience` — entity boundary + L3 copy |
| **React** | ⬜ |

**L3 — ✅:**  
«Сегодняшнее **число дня** усиливает стремление завершать начатое — хороший момент закрыть то, что давно откладывал.»

**L3 — ⛔:**  
«Алгоритм повысил вес числа…» · «На основании numerology_explanation из API…»

**Theme + Number (пример L1 блока):**  
Тема: День ясности. · Число дня: **4** — структура и порядок.

---

### `DailySymbols` *(entity spec 🟢)*

| | |
|---|---|
| **Роль** | **Символы дня** — камень · цвет · тотем · стихия · талисман *(umbrella)* |
| **User question** | Какие **символы** поддерживают меня **сегодня**? |
| **Product answer** | 1–4 коротких символа + как **использовать** сегодня — **кратко и по делу** |
| **Зачем** | Мягкий «якорь» дня; **дополняет** Tarot · Number |
| **Wave 1 subset** | **цвет + камень** (остальное — teaser / expand) |
| **Facets** *(internal IDs, один entity)* | `color` · `stone` · `totem` · `element` · `talisman` · `moon` *(если в блоке)* |
| **L1** | Компактно: «**Лазурит** · **синий**» + по одной строке на символ |
| **L2** | Как это **лично** поддерживает Theme · Energy сегодня |
| **L3 · Почему?** | «Сегодня **цвет дня** — синий: он поддерживает спокойную концентрацию. **Камень** лазурит усиливает тему ясности» — астрология + символика, **кратко и по делу** |
| **L4** | Библиотека символов · Profile · «Мои символы» |
| **Internal** | Day Model · symbolic reference · `DailyTheme` · Profile |
| **External** | **Астрология** (луна · стихия) + **символическая традиция** (камень · цвет · тотем) |
| **Writes** *(product)* | просмотр · expand facet · «использовал сегодня» · избранное → Maps |
| **Проекции** | Today · Profile · Week · Wrapped (symbol palette) |
| **Код** | `FirstToday` symbolic teaser only — **нет** полного `DailySymbols` |
| **React** | ⬜ |

**L1 — ✅ (wave 1):**

```
Символы дня
Камень: лазурит — ясность и спокойствие
Цвет: синий — сосредоточенность
```

**L3 — ✅:**  
«Синий цвет сегодня поддерживает спокойную концентрацию. Лазурит усиливает тему ясности — можно носить или держать рядом как якорь.»

**L3 — ⛔:**  
«Reference Layer вернул stone_id…» · «Символы подобраны алгоритмом…»

---

### `PracticeRecommendation` *(entity spec 🟢)*

| | |
|---|---|
| **Роль** | Небольшое **действие**, которое помогает **прожить** сегодняшний день |
| **User question** | Что сегодня **лучше всего поможет прожить** этот день? |
| **Product answer** | **Одна** практика — наиболее созвучная сегодняшнему дню |
| **Зачем** | Связать понимание дня с **реальным действием**; понимание → **опыт** |
| **Суть** | Практика связывает **тему дня** с **конкретным проживанием** |
| **L1** | Название + очень короткое описание · **~30 сек** |
| **L2** | Почему **именно сегодня** она уместна (Theme · Energy · контекст дня) |
| **L3 · Почему?** | Тема · энергия · карта · число · астрология — язык предметной области |
| **L4** | Как выполнять · когда лучше · чего ожидать · связанные практики |
| **Intro-фразы** *(L1, вариативно)* | «Сегодня полезно:» · «Сегодня хорошо подойдёт:» · «Сегодня попробуй:» · «Сегодня удели:» |
| **Internal** | Day Model · `DailyTheme` · `DailyEnergy` · `DailyTarot` · `DailyNumber` · Profile · history · practice reference *(pick one)* |
| **External** | **Астрология** · **нумерология** · **таро** · **твоя жизнь** *(история выполнений)* |
| **Writes** *(product)* | просмотр · **начал** · **выполнил** · «помогло» / «позже» · связь с темой дня → **Practice Map** |
| **Learning** *(invisible)* | какие практики выбирает чаще · что помогает · какие темы → какие практики — **Maps / Profile** |
| **Проекции** | Today · Profile *(любимые · эффективные)* · Maps *(месяц · год)* · Weekly · Wrapped |
| **Код** | Today — одна рекомендация · `/practices` — library projection · entity block — ⬜ |
| **React** | ⬜ |

**L1 — ✅:**

```
Сегодня полезно
Дыхательная практика · 10 минут
Спокойное дыхание, чтобы замедлиться и услышать себя
```

**L2 — ✅:**  
«Сегодняшняя тема связана с восстановлением внутреннего равновесия. Эта практика помогает немного замедлиться и лучше услышать себя.»

**L3 — ✅:**  
«Сегодня энергия дня располагает к спокойному внутреннему наблюдению. Практики, связанные с дыханием и концентрацией, помогают прожить этот день более гармонично.»

**L3 — ✅ (tarot weave):**  
«Сегодня карта Умеренность усиливает тему баланса. Именно поэтому практики осознанности и постепенных действий особенно созвучны сегодняшнему дню.»

**L3 — ⛔:** *(copy gate — §1)*  
«Practice Engine выбрал practice_id…» · «На основе PIM slice…» · «Рекомендация из каталога…»

**Примеры одной практики:**

| Intro | Практика |
|-------|----------|
| Сегодня полезно | 10 минут дыхательной практики |
| Сегодня хорошо подойдёт | прогулка без телефона |
| Сегодня попробуй | записать три мысли, которые не дают покоя |
| Сегодня удели | пять минут практике благодарности |

---

### `ContinuityRecall` *(entity spec 🟢)*

| | |
|---|---|
| **Роль** | **Мост** между вчерашним и сегодняшним днём |
| **User question** | **С чего** продолжить сегодня? / Что **связывает** вчера и сегодня? |
| **Product answer** | **Одна** строка памяти: вчерашний фокус + итог + отправная точка на сегодня |
| **Зачем** | Today **помнит** прожитый день и даёт ощущение **непрерывной истории** |
| **Суть** | ContinuityRecall показывает, что вчера **имело значение** и **продолжается** сегодня |
| **Wave 1** | **D2+** · первый блок Today composition · First Today — skip *(вчера ещё нет)* |
| **L1** | Одна строка · **~5 сек** · «Вчера главным было… Итог… Сегодня продолжим…» |
| **L2** | Как вчерашний итог **лично** влияет на сегодняшний Theme · Focus |
| **L3 · Почему?** | **Твоя жизнь:** паттерны дней · повторяющиеся фокусы · что помогало раньше |
| **L4** | Profile · «Мои дни» · Focus Map · timeline последних 3–7 дней |
| **Internal** | `day_continuity` record · `EveningClose` write · `DailyFocus` *(вчера)* · outcome · note · localStorage v0 → server v2 |
| **External** | **Твоя жизнь** *(история дней)* · при L3 — мягкая связь с Theme дня |
| **Writes** *(product)* | просмотр · **принял мост** · tap «Мои дни» · закрыть вчера *(если открыт)* → Focus Map · Days timeline |
| **Learning** *(invisible)* | outcome patterns · focus recurrence · return-after-close → retention signals |
| **Проекции** | Today D2+ *(hero slot)* · Profile · Weekly · Wrapped *(«твои недели»)* |
| **Код** | `todayDayContinuity.ts` · `buildContinuityOpeningLine` · `TodayS0Greeting` — 🟡 wiring · hierarchy D2+ — ⬜ |
| **React** | ⬜ |

**L1 — ✅** *(из кода · copy gate OK):*

```
Вчера главным было: «Уделить время отдыху без экранов».
Итог: частично.
Сегодня продолжим с того, как это повлияло на ваш следующий шаг.
```

**L2 — ✅:**  
«Вчера ты хотел больше тишины — получилось частично. Сегодня можно мягче вернуться к этому же намерению.»

**L3 — ✅:**  
«За последние дни тема отдыха возвращалась несколько раз. Вчерашний итог — хорошая отправная точка, чтобы сегодня двигаться в том же ритме.»

**L3 — ⛔:** *(copy gate — §1)*  
«localStorage record loaded…» · «day_continuity.v1…» · «Система восстановила фокус…»

**Вечер → утро** *(связка с `EveningClose`):*

| Вечер *(write)* | Утро D2+ *(read · ContinuityRecall)* |
|-----------------|--------------------------------------|
| «Завтра начнём с того, как сегодняшний результат повлиял на ваш следующий шаг.» | Opening line с фокусом + итогом вчера |

**Unclosed yesterday** *(positive prompt):*

```
Вчера можно ещё закрыть — или начать сегодняшний день с новым фокусом.
```

---

### `EveningClose` *(entity spec 🟢)*

| | |
|---|---|
| **Роль** | **Завершить** день и **сохранить** его смысл для завтра |
| **User question** | Как **завершить** этот день? / Что **получилось** с главным фокусом? |
| **Product answer** | Короткий итог по фокусу + **обещание**, с чего начнётся завтра |
| **Зачем** | Завершённость сегодня · **причина открыть** приложение завтра |
| **Суть** | EveningClose превращает прожитый день в **запись**, которую утром подхватит `ContinuityRecall` |
| **Wave 1** | **D1+** · **~30 сек** · CTA «Завершить день» · после confirm — **выход**, без push в Profile |
| **L1 · Close** | Фокус дня + три итога: **Сделал** · **Частично** · **Не сделал** + опциональная заметка |
| **L1 · Confirmed** | «День закрыт» + фокус + итог + **hook на завтра** |
| **L2** | Что сегодня **значило лично** · как итог повлияет на завтрашний старт |
| **L3 · Почему?** | **Твоя жизнь:** закрытые дни складываются в **историю** · повторяющиеся фокусы · что помогало |
| **L4** | Profile · «Мои дни» · Focus Map · timeline |
| **Internal** | `DailyFocus` *(mainFocus)* · `day_continuity` · `saveDayContinuity` · outcome · note · `closedAt` · learning event `day_focus_outcome` |
| **External** | **Твоя жизнь** *(фокус · итог · заметка)* |
| **Writes** *(product)* | outcome · note · **closedAt** → `ContinuityRecall` D2+ · Focus Map · Days timeline · retention signal |
| **Learning** *(invisible)* | close rate · outcome distribution · note themes · focus recurrence |
| **Проекции** | Today *(evening slot)* · Profile · Weekly · Wrapped |
| **Код** | `TodayDayContinuityEveningClose` · `TodayDayContinuityClosed` · `todayDayContinuity.ts` — 🟡 ritual surface only · First Today path — ⬜ |
| **React** | ⬜ |

**L1 · Close — ✅** *(из кода):*

```
Закрытие дня
Что произошло с главным фокусом?
«Уделить время отдыху без экранов»

[ Сделал ]  [ Частично ]  [ Не сделал ]
Что помешало или помогло? · необязательно
[ Завершить день ]
```

**L1 · Confirmed — ✅:**

```
День закрыт
Уделить время отдыху без экранов
Итог: Частично — вечером удалось отложить телефон

Завтра начнём с того, как сегодняшний результат повлиял на ваш следующий шаг.
```

**L2 — ✅:**  
«Сегодня главным было время без экранов — получилось частично. Завтра утром Today продолжит с этого места.»

**L3 — ✅:**  
«Когда дни закрываются с итогом, проще замечать, какие фокусы возвращаются и что реально помогает.»

**L3 — ⛔:** *(copy gate — §1)*  
«Сохранено в localStorage…» · «day_focus_outcome event…» · «Запишите рефлексию в дневник…»

**Вечер → утро** *(write → read):*

| `EveningClose` *(вечер)* | `ContinuityRecall` *(утро D2+)* |
|--------------------------|----------------------------------|
| outcome + note + hook | opening line с фокусом + итогом |

**Entry · feeling:** **~30 секунд** · одно решение · ощущение **завершённого** дня.

---

### Entity queue *(wave 1 — порядок spec)*

| # | Entity | Spec |
|---|--------|------|
| ✅ | `DailyTheme` | 🟢 |
| ✅ | `DailyFocus` | 🟢 |
| ✅ | `DailyGuidance` | 🟢 |
| ✅ | `DailyWarnings` | 🟢 |
| 5 | `DailyEnergy` | 🟢 |
| 6 | `DailyTarot` | 🟢 |
| 7 | `DailyNumber` | 🟢 |
| 8 | `DailySymbols` | 🟢 |
| 9 | `PracticeRecommendation` | 🟢 |
| 10 | `ContinuityRecall` | 🟢 |
| 11 | `EveningClose` | 🟢 |
| — | **Composition Today** | 🟢 v1 CLOSED · React 🟡 v1 shipped web |

---

### Код vs сущности *(gap)*

| Сейчас в коде | Статус |
|---------------|--------|
| `TodayCompositionSurface` | ✅ default + `?first=1` · legacy ritual → `?experience=1` |
| `FirstTodaySurface` | retired · composition `firstToday` variant |
| `TodayExperienceSurface` | legacy · `?experience=1` only |

**Следующий порядок:** (1) manual QA `/today` (2) polish (3) teasers (4) Compatibility hook (5) Profile min.

---

## Composition Today v1 *(CLOSED 🟢 — entities compose the screen)*

**Статус:** **CLOSED** 2026-07-01. Экран = **композиция entity projections**. Не UI-first · не ritual spine.

> **Сущности собирают экран.** Порядок = психология пользователя, не исторический код.

**Narrative spec (copy · примеры · вечер · запреты):** [TODAY_SCREEN_V1_CANON.md](./TODAY_SCREEN_V1_CANON.md) **§11 Day Story Experience** (v4.0).  
**Code diff:** [status/TODAY_CANON_VS_CODE_DIFF.md](./status/TODAY_CANON_VS_CODE_DIFF.md) §Day Story v3.

### Психология порядка

| Этап | Вопрос пользователя |
|------|---------------------|
| 1 | **Что происходит?** — Theme · Focus |
| 2 | **Что с этим делать?** — Guidance · Warnings |
| 3 | **Почему?** — L3 expand |
| 4 | **Какой фон дня?** — Energy · Mood |
| 5 | **Символы · рост · исследование** |
| 6 | **Закрыть день** — Evening |

---

### Режимы экрана

| Режим | Когда | Что видно |
|-------|-------|-----------|
| **Day** *(утро–день)* | default | Zones 0–13 ниже |
| **Evening** | user · time · CTA «Завершить день» | Evening Zone — Hero исчезает |

---

### Zone 0 · Continuity *(D2+ only)*

| # | Entity | Wave 1 |
|---|--------|--------|
| 0 | `ContinuityRecall` | ✅ **перед Hero** · skip First Today |

---

### Hero Zone

| # | Entity | User question | Wave 1 |
|---|--------|---------------|--------|
| 1 | `DailyTheme` | **Какой** сегодня день? | ✅ |
| 2 | `DailyFocus` | **На что** особенно обратить внимание? | ✅ |

**Theme** = атмосфера дня · **Focus** = направление внимания. Два разных ответа.

---

### Guidance Zone

| # | Entity | Role | Wave 1 |
|---|--------|------|--------|
| 3 | `DailyGuidance` | Что **поддержит** этот день | ✅ |
| 4 | `DailyWarnings` | Где быть **внимательнее** | ✅ |
| 5 | **`WhyExpand`** | **Почему?** — L3 aggregate | ✅ |

**`WhyExpand`** *(composition slot — не entity)* — expandable **после** Guidance + Warnings.  
Язык **предметной области** (§1): астрология · число дня · карта · лунный цикл · календарь · **твоя история**.  
Источники L3: Theme · Focus · Guidance · Warnings · Energy · Tarot · Number.

---

### Energy Zone

| # | Entity | User question | Wave 1 |
|---|--------|---------------|--------|
| 6 | `DailyEnergy` | **Какой** сегодня ритм? | ✅ |
| — | `DailyMood` | **Каким** может ощущаться день? | teaser · после check-in |

---

### Symbols Zone

Мягкие якоря · **компактные карточки** · каждая entity **самостоятельна** · каждая **expandable** L2–L4.

| # | Entity | Wave 1 |
|---|--------|--------|
| 7 | `DailyTarot` | ✅ |
| 8 | `DailyNumber` | ✅ |
| 9 | `DailySymbols` | 🟡 subset *(color + stone)* |

---

### Growth Zone

Понимание → **опыт**. Сервисы **внутри Today** — рекомендации **сегодняшнего** дня.

| # | Entity | Wave 1 |
|---|--------|--------|
| 10 | `PracticeRecommendation` | ✅ |
| 11 | `DailyGoal` | teaser |
| 12 | `DailyTracking` | teaser *(что отметить вечером)* |

---

### Explore Zone

**После** того как человек получил день. **Мосты** — продолжение сегодня, не реклама разделов.

| # | Slot | Wave 1 |
|---|------|--------|
| 13 | **`TodayExploreBridges`** *(composition — не entity)* | ✅ 1–3 bridges |

**Примеры copy** *(§2 · positive)*:

- «Сегодня особенно интересно посмотреть **совместимость**.»
- «Сегодня хороший день **задать вопрос картам**.»
- «Сегодня стоит открыть **профиль**.»

**Projections:** `CompatibilityMatch` · `TarotReading` · Profile — contextual, day-linked.

---

### Evening Zone

| Step | Entity / state | Wave 1 |
|------|----------------|--------|
| A | Hero + day zones **скрыты** | ✅ |
| B | `EveningClose` · Close flow | ✅ |
| C | **Tomorrow Hook** *(confirmed · часть EveningClose)* | ✅ |
| D | День **завершён** · exit | ✅ |

---

### Stack order *(canonical · Day mode)*

```
0  ContinuityRecall     (D2+ only)
1  DailyTheme
2  DailyFocus
3  DailyGuidance
4  DailyWarnings
5  WhyExpand
6  DailyEnergy
7  DailyTarot
8  DailyNumber
9  DailySymbols
10 PracticeRecommendation
11 DailyGoal              (teaser wave 1)
12 DailyTracking          (teaser wave 1)
13 TodayExploreBridges
—  EveningClose            (Evening mode replaces Hero+)
```

### First Today path *(D1 · `?first=1`)*

**Тот же** `TodayCompositionSurface` · variant **`firstToday`**.

| Zone | D1 |
|------|-----|
| Hero | Theme · Focus ✅ |
| Guidance | Guidance ✅ |
| Symbols | Tarot · Number · Symbols ✅ |
| Growth | Practice ✅ |
| Evening | EveningClose ✅ |
| Skip | Continuity · Warnings · WhyExpand · Energy · Explore |

Legacy `FirstTodaySurface` — **retired** from `/today?first=1`.

---

### Wave 1 vs код *(gap — исправлять в React)*

| Composition v1 | Сейчас в коде *(2026-07-02)* |
|----------------|---------------|
| Theme → Focus **first** | ✅ greeting → pulse → hero → glance *(Day Story v3)* |
| Symbols **after** meaning | ✅ influences после why · pick overlay |
| `WhyExpand` **collapsed** | ⚠️ always open — fix DS3 |
| `ContinuityRecall` slot 0 D2+ | ✅ partial — outcome line |
| `DailyTracking` slot 12 | ❌ gap |
| `TodayExploreBridges` slot 13 | ❌ hook lib only, not mounted |
| Evening replaces Hero | ⚠️ separate surface OK · practice/mood gaps |

**DoD React:** один `<Today />` · stack = таблица выше · **без** orphan blocks · tokens per zone.

---

## Axis B · Entity Catalog *(остальные продукты — после Today)*

## Phase 2 · Screen Compositions *(A × B)*

**Цель:** экран = **список entity IDs + tokens**. Экран не создаёт новых сущностей.

**Today:** см. **[Composition Today v1](#composition-today-v1-closed--entities-compose-the-screen)** — **CLOSED 🟢**.

### §Screen Template

| # | Поле |
|---|------|
| 1 | Job |
| 2 | User Question |
| 3 | Product Answer |
| 4 | **Uses** — entities + projection tokens |
| 5 | Writes Back (aggregate) |
| 6 | Feeling on Close |

---

### Screen · Today

**Canonical stack:** [Composition Today v1](#composition-today-v1-closed--entities-compose-the-screen) — не дублировать здесь.

| Mode | Entities |
|------|----------|
| **Day D1** | slots 1–13 |
| **Day D2+** | slot 0 + 1–13 |
| **Evening** | `EveningClose` → Tomorrow Hook |

---

### Screen · Profile

| Uses | Notes |
|------|-------|
| `Portrait` | Hero |
| `DailyTheme` | Secondary projection |
| `TarotReading` | summary row |
| `HabitSummary` | |
| `CompatibilityMatch` | saved people |
| `MapsPreview` | |
| `DaysTimeline` | «Мои дни» |
| `MoodHeatmap` | wave 2 |

---

### Screen · Compatibility

| Uses | Notes |
|------|-------|
| `TodayOverview` or compact Hero | entry |
| `CompatibilityMatch` | Hero |
| `CompatibilityInsight` | per projection type |
| `CompatibilityRadar` | wave 2 |

---

## Phase 3 · Layout *(per screen — order & grouping)*

Не пиксели. **Stack order** и **grouping** = Composition v1 zones.

**Today:** `ContinuityRecall?` → Hero → Guidance → Energy → Symbols → Growth → Explore → *(Evening mode)* `EveningClose`

**Profile:** `Portrait` → sections as collapsible groups of **same entities**, different tokens.

---

## Phase 4 · Data Flow *(per Entity)*

Pipeline привязан к **Entity ID**, не к экрану.

### `DailyTheme`

```
Profile + date → DayModel → Reference → PIM slice → LLM Gate → DailyTheme payload → projections
```

### `PracticeRecommendation`

```
Today context + Profile → Practice Engine → PIM → PracticeRecommendation → completion → Maps
```

### `CardOfDay`

```
date + Profile → Tarot Engine → Reference → PIM → CardOfDay → Tarot Map signal
```

### `CompatibilityMatch`

```
Profile A + B → Compatibility Engine → Reference → CompatibilityMatch
```

**Learning invariant:** Experience → LLM напрямую запрещено.

---

## Phase 5 · Build Order

По **ценности** + **entity readiness** (Axis B 🟢).

| Sprint | Entities | Journey gate |
|--------|----------|--------------|
| **1** | LandingHero · ProductVitrine · MapsPromise · onboarding entities · `TodayOverview` · `DailyTheme` · `DailyEnergy` | curiosity → orientir |
| **2** | `DailyGuidance` · `DailyWarnings` · `CardOfDay` · `PracticeRecommendation` · `ServiceRecommendations` · `EveningClose` · `ContinuityRecall` | day closes · remembers |
| **3** | `CompatibilityMatch` · `CompatibilityInsight` | relationships |
| **4** | `CardOfDay` depth · `TarotReading` | ritual |
| **5** | `Portrait` · `DaysTimeline` · `MapsPreview` | history > one day |
| **6** | Heatmaps · Wrapped projections | share |
| **7** | Phase 6 Polish | post wave-1 |

**Wave 1 checklist:** Sprint 1–2 + Compat hook + Profile min + walkthrough + field test.  
Code gaps: [WEB_LAUNCH_EXECUTION_PLAN.md](./status/WEB_LAUNCH_EXECUTION_PLAN.md).

---

## Phase 6 · Polish

Анимации · transitions — **после** wave-1 checklist.

---

## Справочники

| Документ | Когда |
|----------|-------|
| [TODAYFLOW_PRODUCT_MODEL.md](./TODAYFLOW_PRODUCT_MODEL.md) §4 | Content model |
| [status/WEB_LAUNCH_EXECUTION_PLAN.md](./status/WEB_LAUNCH_EXECUTION_PLAN.md) | Code gaps · DoD |
| [PERSONAL_INTELLIGENCE_MODEL_V1.md](./PERSONAL_INTELLIGENCE_MODEL_V1.md) | Learning |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-01 | **v0.7.1** — Phase 1 screen gate table · launch remaining list |
| 2026-07-01 | **v0.7.0** — **Composition Today v1 CLOSED** · zones · stack · Evening mode |
| 2026-07-01 | **v0.6.0** — wave 1 entity queue complete · `EveningClose` 🟢 |
| 2026-07-01 | **v0.5.9** — `ContinuityRecall` spec 🟢 |
| 2026-07-01 | **v0.5.8** — §2 canonical form · **два базовых закона** |
| 2026-07-01 | **v0.5.7** — **Positive Definition CLOSED** · E9 |
| 2026-07-01 | **v0.5.6** — `PracticeRecommendation` spec 🟢 |
| 2026-07-01 | **v0.5.5** — `DailySymbols` spec 🟢 · wave 1: color + stone |
| 2026-07-01 | v0.5.4 — `DailyNumber` |
| 2026-07-01 | v0.3 — две оси A/B · Entity Catalog · 6-step law |
| 2026-07-01 | v0.1 — initial Build Map |
