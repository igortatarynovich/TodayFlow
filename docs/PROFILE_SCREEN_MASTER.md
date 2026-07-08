# Profile · Screen Master

**Статус:** **CANON** — единственная спецификация экрана Profile для дизайна, разработки и QA.  
**Версия:** 2.2 (2026-07-02).  
**Код:** `frontend/src/components/profile/v0/` · лимиты `frontend/src/lib/profilePage/profileScreenLimits.ts`

**Production route (2026-07-06):** default `/profile` → **`ProfileWebScreen`** shell + **`ProfileQuickMapScreen`** (`HeroLarge` + Foundation surfaces + `ProfileWebMyDays`). Legacy: `?view=v0` → `ProfileV0Screen`. Superseded thin shell: `ProfileWebQuickMap` (deprecated). QA: [status/PROFILE_FOUNDATION_QA.md](./status/PROFILE_FOUNDATION_QA.md).

**Цель:** две половины личности — **портрет** («Кто я») и **живая история** («Как меняется моя жизнь» · Maps). Не CRM, не лендинг, не Excel-трекеры.

**Onboarding (v2):** Profile **не** первый экран после signup и **не** host для core setup. Сбор birth data — `/onboarding/core` ([FIRST_DAY_EXPERIENCE.md](./FIRST_DAY_EXPERIENCE.md)). Profile показываем как «твой портрет» **после** First Today или по depth CTA.

**Две фазы работы:**

| Фаза | Фокус | Статус |
|------|--------|--------|
| **1 · Архитектура** | единая ширина · отступы · ось · expand без shift · **flat DOM** | **в коде** — см. §0.2 |
| **2 · Визуальные сущности** | убрать card-thinking · каждый слой — свой тип объекта | **следующий проход** (см. §0.3) |

Фаза 2 **не начинается**, пока Фаза 1 не принята в QA (§8).

---

## 0.2 DOM (Фаза 1 · flat)

```
.page
└─ .profileStack          ← только flex + gap 40px, без background
   ├─ section.heroScene       ← atmospheric field · 3-row layout
   ├─ section.statement
   ├─ section.numbersMonument      ← Core Pattern
   ├─ section.nameCodeBlock        ← Social Mirror (CSS reuse)
   ├─ section.lifeDualitySection
   ├─ section.compassAction
   └─ a.atlasCover
```

**Удалено:** `.profileSection` ×6 · `ProfileV0Zone` · `zoneHero` · `heroViewport` · `whoSceneInner` · `actionLayerInner` · gradient на `.profileStack`.

**Route v0:** `profile-v0-route` снимает тройной padding/max-width orbit-контейнеров; ширину задаёт только `.page`.

---

## 0.3 Visual entity model (Фаза 2)

**Не думать:** Hero Card · Numbers Card · Action Card.  
**Думать:** шесть **разных типов объектов** — один смысл = одна визуальная роль.

| Слой | Entity | Ощущение | Анти-паттерн |
|------|--------|----------|--------------|
| 1 Hero | **Scene** | сцена без границ: мягкий фон · эмблема · орбиты · текст | голубой прямоугольник · card shell · border-radius box |
| 2 Why | **Statement** | цитата / объяснение: accent-линия или выделенная фраза | белая карточка · shadow · padding-box |
| 3 Numbers | **Monument** | ядро профиля: большая цифра · орбиты · глубина · свечение · слои | таблица · card · flat rectangle |
| 4 Life | **Duality** | два разных мира: Love = мягкость/круги · Money = сетка/геометрия | две одинаковые карточки с разными иконками |
| 5 Action | **Compass** | навигация: символ пути · принцип · направление · меньше текста | карточка с советами · список в box |
| 6 Portal | **Portal** | переход в следующий уровень (уже ближе всего к канону) | рекламный banner · card CTA |

## 0.4 Typography · 6 sizes + 4 colors

**Sizes (canon — единственные допустимые на /profile v0):**

| Token | Role | Где |
|-------|------|-----|
| `--profile-type-xl` | **XL** | SAGE · digit 7 (`calc(xl * 1.45)`) |
| `--profile-type-l` | **L** | Love / Money / Compass / Portal titles |
| `--profile-type-m` | **M** | главный вывод слоя (Why phrase, Love/Money main, Compass main, Hero tagline) |
| `--profile-type-body` | **Body** | весь остальной текст · detail panels |
| `--profile-type-caption` | **Caption** | Важно, Спутник, Сегодня, Имя, signal labels |
| `--profile-type-micro` | **Micro** | Карта личности, Почему именно…, Мои числа |

**Colors:**

| Token | Role |
|-------|------|
| `--profile-color-primary` | почти чёрный · M + L + важное |
| `--profile-color-secondary` | тёплый серо-коричневый · Body |
| `--profile-color-secondary-muted` | приглушённый Body |
| `--profile-color-accent` | фиолетовый · **только Numbers** (7, орбиты, active) |
| `--profile-color-accent-green` | **только Compass** |

**Запрещено:** локальные `font-size` вне токенов · сине-серые UI-цвета · фиолетовый текст вне Numbers.

**Фаза 2:** Numbers ✓ → Hero ✓ → Life ✓ → Action ✓ → Why ✓ → typography + Numbers content model ✓ · **стоп → аудит** · Portal — после аудита.

---


## 0. Общая сетка

| | Desktop | Mobile |
|---|---------|--------|
| Колонка | **`--profile-content-width: 820px`** · `.profileSection` · `.profileStack` gap **40px** | одна колонка + gutter **16px** |
| Фон | `#f3efe8` off-white | то же |
| Navbar | fixed сверху | то же |
| Hero | **65–70vh** | **75vh**, контент по центру; Why/Numbers peek на первом экране |

**Порядок (7 слоёв Portrait + Living Maps + Portal):**

**A · Кто я** *(Portrait — почти не меняется)*

1. Hero — кто ты  
2. Why — почему сформировался профиль  
3. Core Pattern — что тобой движет  
4. Social Mirror — как тебя видят другие  
5. Life layer — Love + Money (desktop 2 col · mobile swipe)  
6. Action layer — Compass  

**B · Как меняется моя жизнь** *(Living Maps — §7)*

7. Living Maps — heatmaps · journeys · timelines · share *(не трекеры)*  

**C · Depth**

8. Portal — карта личности · collapsed natal / sources  

**Не на скролле:** Compatibility · Today · **Name entity (removed)**.

---

## 1. Hero · entity: **Scene**

**Роль:** обложка личности — **сцена**, не card.

**Layout (3 зоны):**

| Зона | Содержимое |
|------|------------|
| Top | «Карта личности» + «Данные рождения» |
| Center | **эмблема + орбиты + glow** (единый объект) · SAGE · caption · meta |
| Bottom | tagline · **3 качества** (точка + слово + подпись, без box) |

**Визуал v2.1:** `.heroScene` — radial field по элементу · **без** border-radius box · **без** heroFade · **без** ElementAtmosphere card shell.

---

## 2. Why · entity: **Statement**

**Роль:** интерпретация между Hero и Numbers — **редакционная цитата**, не карточка и не секция.

| | |
|---|---|
| Heading | «Почему именно {archetype}» · uppercase kicker |
| Phrase | **наблюдение** (`whyManifest`) · `--profile-type-l3-soft` · weight 400 · не конкурирует с Hero |
| Note | короткое объяснение (`layerHint`) · обычный prose, не UI-footer |
| Визуал | **левая вертикальная линия** · типографика справа · без box / card / shadow / фона |
| Expand | **нет** |

**Acceptance:** при скрытых Hero и Numbers — ощущение pull-quote из дорогого журнала, не UI-блок.

**Код:** `.statement` · `.statementBody` · `.statementHeading` · `.statementPhrase` · `.statementNote`

**Запрещено:** «Следующий слой» · card shell · декор уровня Hero · S/W списки · знак · элемент · модальность.

---

## 3. Core Pattern · entity: **Monument**

**Роль:** **что тобой движет** — паттерн решений, не «мои числа».

**Surface label:** «Что тобой движет» · **не** «Мои числа» / «Число личности».

**Collapsed:** label · орбиты · **главная цифра (LP)** · poetic caption · driver blurb · «Раскрыть паттерн».

**Expand — спутники (user roles, не numerology labels):**

| Спутник | Смысл | Data |
|---------|-------|------|
| В поведении | как паттерн виден в действиях | `manifestation[]` |
| Под напряжением | где ломается | `minus_side` / watchouts |
| Ежедневный режим | micro-pattern | `reading` / birth day |

**Запрещено:** спутники «Число личности» / «Число проявления» — они в Social Mirror (скрыто).

---

## 3.5 Social Mirror · entity: **Mirror** (Name killed)

**Роль:** **как тебя видят другие** — blended perception, без источников.

**Surface:** «Как тебя видят» · lead · 2–3 observations · expand (Первое впечатление / Что транслируешь / Слепая зона).

**Data (hidden):** expression · personality · soul_urge · sign portrait · communication · strengths · watchouts.

**Код:** `ProfileV0SocialMirrorBlock.tsx` · `buildSocialMirrorCard` · view model `socialMirror`.

**Запрещено:** glyph имени · «Имя» · numerology facet labels на surface.

---

## 4. Life layer · entity: **Duality**

**Роль:** один слой жизни — **два разных мира**, не две карточки.

**Сцена:** `.lifeDualityScene` — radial field без card shell · `.lifeDualityTrack` gap **28px**.

| | Love · мягкость | Money · структура |
|---|---|---|
| Фон | radial rose · орбиты-декор | grid · ось слева |
| Symbol | круг | квадрат 6px |
| Signals | Важно / Мешает · italic | Усиливает / Тормозит · border-left |
| Expand | facet-кнопки → клик → `.dualityDetailPanel` (глубина, не длина) | то же |

**Expand-модель (как Numbers):** «Подробнее» → chips (Потребность / Ошибка / …) → клик → одна секция L4. **Не** текстовый столбец.

**Layout:** desktop 2 col · mobile swipe **86vw**

---

## 5. Action · entity: **Compass**

**Роль:** кульминация — «Как двигаться дальше?» Маршрут, не card с советами.

**Layout:** `.compassAction` · min-height **380–460px** · desktop **40/60** · `overflow: visible` · «Сегодня» — **целое предложение**, без обрезки UI/data.

---

## 6. Portal · entity: **Portal**

**Роль:** **переход** в Deep Dive — порог, не баннер и не card.

- Kicker «Следующий уровень» · vertical **slit** · side vignette · flat edges (no radius)
- Title «Карта личности» · CTA «Войти»
- Min-height **~16–22rem / 34vh** · centered · `.atlasPortalSlit`

---

## 7. Living Maps · «Как меняется моя жизнь»

**Роль:** вторая половина Profile и TodayFlow — **живая история**, не трекеры и не статистика.  
**Канон:** [TODAYFLOW_PRODUCT_MODEL.md](./TODAYFLOW_PRODUCT_MODEL.md) §4.10 · §5.8 · [PERSONAL_INTELLIGENCE_LAYER.md](./PERSONAL_INTELLIGENCE_LAYER.md) §3.3.

**JTBD:** *Каким становится моя жизнь?* — узоры, которые **рисуются сами** из Today.

### 7.1 Связь Today · Profile · PIM

| Источник | Что даёт Maps |
|----------|----------------|
| **Today** | +1 точка за действие дня (карта · число · mood · energy · practice · promise · evening) |
| **Profile** | дом карт · drill-down · living observations · share |
| **PIM** | atoms · temporal patterns → **story render** (mechanism скрыт) |

**Запрещено:** отдельный nav «Трекеры» · экран «заполни статистику» · % completion в UI.

### 7.2 Visual entity model *(Maps)*

| Map | Entity feel | Анти-паттерн |
|-----|-------------|--------------|
| Mood · Energy | **Heatmap field** (GitHub-style) · tap → day story | таблица · average score |
| Habit | **Color weave** — каждая привычка свой цвет | чеклист · admin grid |
| Ascetic | **Journey** — башня · дерево · тропа | «Аскеза №4» |
| Promise · Goal | **Timeline arc** | task list · KPI |
| Wish | **Constellation** — желания как якоря | Pinterest board |
| Relationship | **Orbit network** | compat % list |
| Tarot · Theme · Symbol | **Arc journey** | spread statistics |

### 7.3 Drill-down (нажал день / период)

L3 **только** язык предметной области + **твоя история** — см. EXPLAIN_MEANING:

> «8 июля настроение резко изменилось. Сегодня был сложный лунный аспект. Ты отметил высокую усталость. Вечером не удалось выполнить обещание дня.»

Не: «алгоритм коррелировал mood с lunar_aspect_id…».

### 7.4 Launch vs north star

| Сейчас | North star |
|--------|------------|
| `ProfileMapsPreviewBlock` — seed strip (7 точек) | full heatmaps + drill-down |
| `/habits` heatmap + completion copy | color weave · story-only language |
| `core_profile.living` | cross-map observations · share cards |

**Код (seed):** `ProfileMapsPreviewBlock.tsx` · `profileMapsPreview.ts` · iOS Maps preview.  
**Backlog:** MP-* в [PRODUCT_EXECUTION_TRACKER.md](./PRODUCT_EXECUTION_TRACKER.md).

### 7.5 Cycle *(контекст, не hero)*

Женский цикл **не** отдельный блок Profile. Влияет на Today (рекомендации · практика · вечер). В Maps — только **наблюдения** через месяцы («в первой половине цикла чаще…»), не «день 16».

---

## 8. Implementation map

| Слой | Component |
|------|-----------|
| Screen | `ProfileV0Screen.tsx` |
| Hero | `ProfileV0Hero.tsx` |
| Why | `ProfileV0WhoScene.tsx` |
| Numbers | `ProfileV0NumbersMiniHero.tsx` |
| Social Mirror | `ProfileV0SocialMirrorBlock.tsx` |
| Life | `ProfileV0LifeLayer.tsx` → Love/Money objects |
| Action | `ProfileV0ActionLayer.tsx` |
| Living Maps | `ProfileMapsPreviewBlock.tsx` · `profileMapsPreview.ts` *(seed)* |
| Data | `buildProfileV0Data.ts` · `buildProfileV0SphereCards.ts` |

---

## 9. QA checklist

### Фаза 1 · архитектура (gate для Фазы 2)

- [ ] `--profile-content-width: 820px` · все слои в `.profileSection`
- [ ] Между слоями **40px** · без negative margin / translate overlap
- [ ] Expand Numbers / Love / Money: **только высота вниз**, ширина и ось не меняются
- [ ] Левая граница Hero = Why = Numbers = Life = Action = Portal

### Фаза 2 · visual entities (после gate)

- [ ] Hero — **Scene** (поле + emblem object · без fade/card)
- [x] Why — **Statement** (accent line · editorial phrase · no card)
- [ ] Numbers — **Monument** (поле + satellites + «Вместе» без card)
- [ ] Life — **Duality** (Love soft / Money grid · одна сцена)
- [ ] Action — **Compass** (маршрут · route markers · «Сегодня»)
- [ ] Portal — **Portal** (переход)
- [ ] Быстрый скролл без текста: **6 разных визуальных якорей**

---

## 10. Perception audit (ощущения, не блоки)

**Gate (2026-06-01):** taxonomy **ACTIVE** — см. [PROFILE_V0_CONTENT_INSIGHT_AUDIT.md](./status/PROFILE_V0_CONTENT_INSIGHT_AUDIT.md).  
Считать инсайты по **категории измерения**, не по количеству строк. Pipeline target: `{ categoryId, text }`.

**Не уходить в генерацию текста** до category contract в builders.

### Reference → Consumer

| | Reference (скрыто) | Consumer (экран) |
|---|-------------------|------------------|
| Модель | archetype · LP · name # · sign · LLM | вопрос пользователя → ответ |
| Пример | personality + expression + portrait | «Как тебя видят другие» |

### Spatial mix

| Weight | Слои | Доля (цель) |
|--------|------|-------------|
| **compact** | Hero · Why | origin **≤20%** |
| **standard** | Core Pattern · Compass | |
| **expanded** | Social Mirror · Love · Money | application **≥80%** |

### Слой → вопрос → обязательные категории

Полная таблица: `profileInsightTaxonomy.ts` · audit doc.

| Слой | Вопрос | Категории (кратко) |
|------|--------|-------------------|
| Hero | Кто ты | identity · strength · conflict · life_theme |
| Why | Почему профиль | formation → helps → breaks |
| Core Pattern | Что движет | driver · fear · trap · decisions · recovery |
| Social Mirror | Как видят | first · after · misread · trust |
| Love | Близость | seeks · fears · loves · destroys · strengthens |
| Money | Реализация | growth · earning · risk · blind_spot · catalyst |
| Compass | Что делать | amplify · avoid · energy · skill · check_soon |

**Dedup (done):** `ProfileContentLedger`. **Budget (necessary, not sufficient):** `profileInsightBudget.ts`. **Taxonomy (gate):** `profileInsightTaxonomy.ts`.

### Тест №1 · скролл без чтения

Ожидаемая цепочка: Личность → Объяснение → Ядро чисел → Love/Money → Направление → Следующий уровень.

**Риск:** Why + Numbers оба «спокойные светлые» — порог: `border-top` на `.numbersMonument` + фиолетовое поле vs flat Statement.

### Тест №2 · только формы

`NEXT_PUBLIC_PROFILE_SHAPE_AUDIT=1` или класс `.pageShapeAudit` на `.page` — текст прозрачный, формы остаются.

Pass: без текста различимы Scene · Statement · Monument · Duality · Compass · Portal.

### Тест №3 · 10 секунд памяти

Pass: Sage · 7 · love/money · compass. Fail: «красивые круги» без смысла.

### Главный оставшийся риск

Не UI — **одномерные инсайты** (5 строк = 1 категория) и **перекос origin/application** (~30% объяснение vs цель ≤20%). Taxonomy gate + spatial mix — [insight audit](./status/PROFILE_V0_CONTENT_INSIGHT_AUDIT.md).
