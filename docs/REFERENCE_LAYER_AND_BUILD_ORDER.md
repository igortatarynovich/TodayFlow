# Reference Layer и порядок построения TodayFlow

**Статус:** принято (фундаментальный канон).  
**Версия:** 1.0 (2026-05-31).  
**Владелец:** Product + Engineering.

**Связь:** [ONTOLOGY_AND_FOUNDATION_PHASES.md](./ONTOLOGY_AND_FOUNDATION_PHASES.md) (**фаза 1** — этот документ), [CORE_PRODUCT_CANON.md](archive/CORE_PRODUCT_CANON.md), [PERSONAL_INTELLIGENCE_LAYER.md](pim/PERSONAL_INTELLIGENCE_LAYER.md) (сквозной PIL — обязателен для всех генераций), [DAY_ENGINE_AND_COHERENCE.md](./DAY_ENGINE_AND_COHERENCE.md), [DAYMODEL_INPUT_CONTRACT.md](./DAYMODEL_INPUT_CONTRACT.md), [DATA_OWNERSHIP_AND_CONSUMPTION_MAP.md](./DATA_OWNERSHIP_AND_CONSUMPTION_MAP.md), [DATA_ORIGINATION_AND_LIFECYCLE.md](./DATA_ORIGINATION_AND_LIFECYCLE.md) (откуда данные, наполнение, lifecycle), [REFERENCE_LAYER_AND_BUILD_ORDER.md](./REFERENCE_LAYER_AND_BUILD_ORDER.md) (полная карта 180 + C/D/Co/R), [DAY_CONTEXT_V0.md](./DAY_CONTEXT_V0.md), [PERSONAL_INTELLIGENCE_LAYER.md](pim/PERSONAL_INTELLIGENCE_LAYER.md), [PRODUCT_EXECUTION_TRACKER.md](./PRODUCT_EXECUTION_TRACKER.md).

---

## Жёсткое правило (freeze)

**Пока этот документ не принят и таблица §6 не заполнена для доменов P0 — запрещено:**

- менять **Today UI** (новые блоки, перестройка layout, новые CTA-потоки);
- писать **новые промпты** и расширять generation pipeline;
- добавлять **новые LLM-вызовы** «на весь день» или «на весь экран»;
- **мигрировать JSON** справочников и наполнять Machine Contract без [DAYMODEL_INPUT_CONTRACT.md](./DAYMODEL_INPUT_CONTRACT.md) §5 и без прохождения [reference_machine_contract_v1.schema.json](./schemas/reference_machine_contract_v1.schema.json);
- начинать **P0.3 editorial scores** до зелёного CI job `reference-machine-contract-schema`;
- вводить **новые JSON/DB-схемы** справочников без строки в таблице §6 **и** без поля в Dependency Map §3 того контракта.

**Разрешено без снятия freeze:** багфиксы, i18n без смены смысла, тесты, CI, документация по этому канону, наполнение `draft`-записей **после** принятия DayModel Input Contract.

**Порядок артеfactов:** (1) таблица §6 здесь → (2) [DAYMODEL_INPUT_CONTRACT.md](./DAYMODEL_INPUT_CONTRACT.md) → (3) [reference_machine_contract_v1.schema.json](./schemas/reference_machine_contract_v1.schema.json) (P0.2) → (4) P0.3 editorial scores → (5) миграция legacy JSON / Reference API.

---

## 1. Назначение Reference Layer

### 1.1 Зачем нужен

Reference Layer — **единый слой смыслов и правил**, на который опираются все модули продукта. Он отвечает на четыре вопроса для каждой сущности:

1. **Что это?** (идентичность, категория)
2. **Какие у неё свойства?** (шкалы, связи, ограничения)
3. **Как использовать в продукте?** (use cases, consumers)
4. **Что отдавать другим модулям?** (Machine Contract + Content Contract)

ИИ **не должен** каждый раз заново «знать», что такое карта Таро, число 7 или Венера в Раке. Справочник хранит истину; LLM **адаптирует** уже зафиксированный смысл под пользователя и день.

**Цепочка продукта (канон):**

```
Reference Layer → Profile → Daily Context → Personal Intelligence Layer
  → LLM/API → Evaluation → Output → Feedback → Training Dataset
```

Справочники — **фундамент**. PIL — **обязательный посредник** перед любым LLM/API. Без PIL новые output surfaces не строятся ([PERSONAL_INTELLIGENCE_LAYER.md](pim/PERSONAL_INTELLIGENCE_LAYER.md) §4).

### 1.2 Что запрещено делать без Reference Layer

| Запрещено | Почему |
|-----------|--------|
| Генерировать «значение карты / числа / знака» с нуля в промпте | Разный смысл при каждом вызове, нет версионирования |
| Один LLM-запрос «сделай весь Today» | Усреднение, нет DayModel и причинности |
| Хранить смыслы только во фронте (`todayRitualCopy.ts`, разрозненные JSON) | Нет единого ownership и parity web/iOS/Android |
| Менять трактовку карты/числа без `version` / `valid_from` | Невозможно объяснить, почему 15 мая совет отличался от 15 июня |
| Пускать в `active` тексты только от LLM без review | Дрейф качества и канона |
| Строить Calendar Rhythm / фильтры дня без типов дней и статусов | Календарь станет вторым генератором смысла |

### 1.3 Какие модули читают Reference Layer

| Модуль | Что читает | Контракт |
|--------|------------|----------|
| **Profile Engine** | Astro, Numerology, Emotional baseline | Machine + частично Content (interpretation modules) |
| **Daily Context Builder** | Tarot, Numerology cycles, Astro transits, Calendar Rhythm | Machine |
| **DayModel / Decision Engine** | Нормализованные шкалы из Astro, Tarot, Numerology, Emotional State | Machine — поля строго по [DAYMODEL_INPUT_CONTRACT.md](./DAYMODEL_INPUT_CONTRACT.md) §5 |
| **Generation Pipeline (LLM)** | Content Contract срезов + Machine weights **через PIL** | Content (адаптация), не invention; см. [PERSONAL_INTELLIGENCE_LAYER.md](pim/PERSONAL_INTELLIGENCE_LAYER.md) |
| **Today / Morning Ritual** | Tarot card, Numerology day, UI Copy | Content + Machine |
| **Horoscope** | Astro (signs, transits, categories) | Content по категориям |
| **Tarot** | Tarot cards, spreads | Content + Machine (позиции расклада) |
| **Flow / Practices** | Practice, Habit, Ascetic, Goal | Machine (правила) + Content (инструкции) |
| **Calendar** | Calendar Rhythm, Emotional aggregates, tracker types | Machine |
| **UI (web / iOS / Android)** | UI Copy | Content only (никогда raw Machine rules в UX) |

**Personal Map** (layer 3 в `/profile?section=chart`) читает **Astrology Reference** как доказательную базу, не как генератор дневного текста ([PROFILE_SCREEN_MASTER.md](profile/PROFILE_SCREEN_MASTER.md)). Legacy URL `/natal-chart` редиректит на canonical deep link.

---

## 2. Reference Taxonomy

Десять доменов. Внутри домена — **entities** (строки таблицы §6).

**Связанный домен (PIL):** **Interpretation** — [INTERPRETATION_LAYER_AND_REFERENCE.md](explainability/INTERPRETATION_LAYER_AND_REFERENCE.md).

**Связанный домен (продукт / commerce):** **Symbolic Assets** — [REFERENCE_LAYER_AND_BUILD_ORDER.md](./REFERENCE_LAYER_AND_BUILD_ORDER.md); target `DATA/reference/symbolic/`. P3+ после P0 Today-critical reference.

### 2.1 Astrology

**Назначение:** объективный астрологический язык — знаки, планеты, дома, аспекты, циклы.

**Entities:** `ZodiacSign`, `Planet`, `House`, `Aspect`, `Element`, `Modality`, `MoonPhase`, `PlanetaryCycle`, `PlanetInSign`, `PlanetInHouse`, `AspectRelation`, `CrossDomainBridge`, `TransitTheme`.

**Machine:** коды, орбы, polarity, tension_level, life_domain, оси Internal Model.  
**Content:** keywords, themes, category lenses (love / money / work / energy / communication / health / decisions).

**Текущее хранение:** `DATA/astrology_reference/*.json`, loader `todayflow_backend.data.astrology`.

### 2.2 Tarot

**Назначение:** 78 карт, расклады, позиции, смысл в контексте дня и ситуации.

**Entities:** `TarotCard`, `TarotArcana`, `TarotSuit`, `TarotSpread`, `SpreadPosition`, `CardOrientation` (upright / reversed).

**Machine:** card_id, arcana, suit, correspondences (element, planet, axes), spread layout.  
**Content:** keywords, day_meaning, category meanings (love, work, money, energy, decision), advice, warning, reflection_question, ui_short_text; state variants (low energy, high stress) — expert expansion.

**Текущее хранение:** `tarot_major_arcana.json`, `tarot_spreads.json`; младшие арканы — **missing**.

### 2.3 Numerology

**Назначение:** числа 1–9, мастер- и кармические числа, персональные циклы.

**Entities:** `CoreNumber`, `MasterNumber`, `KarmicNumber`, `LifePathProfile`, `PersonalYear`, `PersonalMonth`, `PersonalDay`, `LetterMapping`.

**Machine:** value, reduction rules, master_number flags, cycle formulas.  
**Content:** energy label, behavior pattern, strength, risk, action type, day rhythm hint.

**Текущее хранение:** расчёт `todayflow_backend.data.numerology`, `DATA/numerology.json` (letters only); content-слой значений — **missing**.

### 2.4 Emotional State

**Назначение:** настроение, энергия, стресс, фокус — для тона рекомендаций и vetoes.

**Entities:** `MoodSlug`, `EnergyBand`, `StressBand`, `FocusState`, `OperatingMode`, `CheckInDimension`.

**Machine:** slug, intensity 1–5, recommended_tempo, blocked_recommendation_tags, compatible_practice_tags.  
**Content:** display label (i18n), tone hint, one-line system verdict («мягкий режим» / «день для действий»).

**Текущее хранение:** частично `check_ins.json`, `UserOperatingMode` в Profile Engine; unified reference — **partial**.

### 2.5 Practice

**Назначение:** дыхание, journaling, тело, медитация, фокус — подбор под состояние / карту / число / цель.

**Entities:** `PracticeCategory`, `PracticeTemplate`, `PracticeDuration`, `PracticeContraindication`.

**Machine:** duration_min, difficulty, target_states[], target_goals[], time_of_day.  
**Content:** title, steps, expected outcome, when_best.

**Текущее хранение:** `rituals.json`, `mantras.json`; unified model — **partial**.

### 2.6 Goal

**Назначение:** типы и категории целей, ритмы, типовые блоки, признаки прогресса.

**Entities:** `GoalCategory`, `GoalType`, `GoalDifficulty`, `ProgressSignal`, `TypicalBlocker`.

**Machine:** category code, suggested cadence, decomposition template id.  
**Content:** label, milestone hints, risk phrases.

**Текущее хранение:** логика в tracking / weekly goals; reference table — **missing**.

### 2.7 Habit

**Назначение:** типы привычек, частота, min/opt версия, streak, снижение нагрузки.

**Entities:** `HabitType`, `HabitFrequency`, `HabitMinimalVersion`, `StreakRule`, `RelapsePattern`.

**Machine:** frequency, min_version, optimal_version, streak_reset_policy, load_reduce_triggers.  
**Content:** display name, encouragement, relapse copy.

**Текущее хранение:** user habits in DB; type catalog — **missing**.

### 2.8 Ascetic

**Назначение:** аскезы / challenges — правила, длительность, критерии, кому не подходит.

**Entities:** `AsceticType`, `AsceticRule`, `AsceticDuration`, `AsceticRisk`.

**Machine:** rule set, completion criteria, max_duration, contraindication tags.  
**Content:** meaning, support on slip, warning.

**Текущее хранение:** user ascetics in tracking; type catalog — **missing**.

### 2.9 Calendar Rhythm

**Назначение:** типы дней, цветовые статусы, нагрузка / восстановление, ритм месяца.

**Entities:** `DayType`, `DayLoadLevel`, `DayColorStatus`, `MonthRhythmPattern`, `RecoveryDayRule`, `ActionDayRule`.

**Machine:** color token, load score, filters bitmask, aggregation weights.  
**Content:** short month-map labels («сильный день», «день восстановления»).

**Текущее хранение:** fusion scores, `DayConnection`; explicit rhythm reference — **missing**.

### 2.10 UI Copy

**Назначение:** CTA, microcopy, empty states, notifications, tone variants, **запретные формулировки**.

**Entities:** `UiCta`, `UiHeadline`, `UiEmptyState`, `UiNotification`, `UiToneVariant`, `UiBannedPhrase`.

**Machine:** key, max_length, surface[], locale fallback chain.  
**Content:** localized string (i18n bundle ref).

**Текущее хранение:** `CONTENT/i18n/app.*.json`, `todayRitualCopy.ts` / iOS mirrors; not unified as reference with status/version — **partial**.

---

## 3. Unified Reference Data Model

### 3.1 Общие поля (все справочники)

| Поле | Тип | Обяз. | Смысл |
|------|-----|-------|--------|
| `id` | string (stable UUID or semantic) | да | Не меняется при редактировании смысла |
| `code` | string | да | Машинное имя (`tarot.major.07`, `num.core.7`) |
| `domain` | enum | да | Один из 10 доменов §2 |
| `entity_type` | string | да | Подтип в домене (см. §6) |
| `title` | string | да | Человекочитаемое имя (default locale) |
| `category` | string | нет | Группировка в домене |
| `description` | string | нет | Базовое описание (editorial) |
| `keywords` | string[] | нет | Индексация и LLM-anchor |
| `positive_meaning` | string | нет | Сильная сторона / ресурс |
| `shadow_meaning` | string | нет | Риск / тень |
| `use_cases` | string[] | нет | `today_card`, `horoscope_love`, `practice_picker`, … |
| `machine_contract` | object | да | См. §4.1 |
| `content_contract` | object | да | См. §4.2 |
| `version` | string | да | Semver записи (`1.0.0`) |
| `valid_from` | date | да | С какой даты active |
| `valid_to` | date \| null | нет | null = бессрочно |
| `status` | enum | да | `draft` \| `review` \| `active` \| `deprecated` \| `archived` |
| `source_type` | enum | да | `system` \| `expert` \| `ai_assisted` |
| `created_at` | datetime | да | |
| `updated_at` | datetime | да | |
| `changed_by` | string | нет | author / service |
| `change_reason` | string | нет | для audit |

**Правило:** LLM, Daily Engine и Today UI используют только записи со `status = active` и `valid_from ≤ today < valid_to`.

### 3.2 Статусы

| Статус | Значение | Кто может читать |
|--------|----------|------------------|
| `draft` | Черновик, не в проде | editorial tools only |
| `review` | На проверке экспертом | staging / preview |
| `active` | Используется в продукте | все consumers |
| `deprecated` | Не для новых генераций; старые логи сохраняют `version` | engine fallback only |
| `archived` | История | audit |

### 3.3 Версии

- Любое изменение **смысла** (не опечатка) → новая `version`, опционально закрыть предыдущую (`valid_to`).
- `generation_logs` и `Daily Memory` должны сохранять **`reference_version`** (код + version) для explainability.
- Breaking change в `machine_contract` → major version; добавление optional полей → minor.

### 3.4 Локализация

- **Machine Contract** — locale-agnostic (коды, числа, enums).
- **Content Contract** — ключи i18n: `content.{domain}.{code}.{field}` в `CONTENT/i18n/` (EN source of truth → RU и др.).
- UI Copy domain может хранить только `i18n_key`, без inline текста в DB.
- Fallback: requested locale → `ru` / `en` (product rule) → EN.

### 3.5 Источник записи (`source_type`)

| source_type | Процесс |
|-------------|---------|
| `system` | Seed из расчётов / taxonomy (letters, orbs) |
| `expert` | Ручной editorial → `review` → `active` |
| `ai_assisted` | LLM draft → **обязательно** `draft` → human `review` → `active` |

### 3.6 Ownership

| Домен | Owner (editorial) | Owner (technical) | Repo path (interim) |
|-------|-------------------|-------------------|---------------------|
| Astrology | Astro editorial | Backend platform | `DATA/astrology_reference/` |
| Tarot | Tarot editorial | Backend platform | `DATA/astrology_reference/tarot_*.json` |
| Numerology | Numerology editorial | Backend platform | `DATA/numerology.json` + future content |
| Emotional State | Product + UX writing | Profile / Today squad | TBD `DATA/reference/emotional/` |
| Practice | Wellness editorial | Flow squad | `rituals.json` → migrate |
| Goal / Habit / Ascetic | Product | Tracking squad | TBD `DATA/reference/trackers/` |
| Calendar Rhythm | Product | Today + Calendar | TBD |
| UI Copy | UX writing | Frontend + iOS + Android | `CONTENT/i18n/`, migrate keys to catalog |

**Единая точка чтения (цель):** `GET /reference/v1/{domain}/{code}` — **not implemented**; до API — loaders in `todayflow_backend.data.*`.

---

## 4. Machine Contract + Content Contract

### 4.1 Machine Contract (движок)

**Кому:** Daily Context Builder, DayModel, Decision Engine, Calendar aggregations, Profile Selector weights, rule orchestrators.

**Содержит:**

- стабильные **коды** и **enum**-шкалы;
- **weights**, **polarity**, **tension_level**;
- **graphs**: links (`planet` → `house`, `card` → `element`);
- **rules**: if state X then block tag Y;
- **thresholds** для Calendar Rhythm;
- **no prose** для пользователя.

**Пример (TarotCard, machine):**

```json
{
  "card_id": "tarot.major.07",
  "arcana": "major",
  "suit": null,
  "orientation_default": "upright",
  "element": "water",
  "planet": "moon",
  "axes": ["A4", "A5"],
  "vector_bias": "transition",
  "energy_bias": "medium",
  "action_type_bias": "continue",
  "tempo_bias": "steady",
  "category_tags": ["work", "decision", "energy"]
}
```

### 4.2 Content Contract (LLM + UI)

**Кому:** Generation Pipeline (как **вход**, не как output), UI cards, Horoscope/Tarot screens.

**Содержит:**

- смысловые поля: meanings, advice, warning, reflection_question;
- **короткие** UI-строки с лимитами длины;
- **locale keys** или inline default locale;
- варианты по категории (love / work / …) и по состоянию (tired / anxious) — expert expansion.

**Пример (TarotCard, content):**

```json
{
  "locale": "ru",
  "keywords": ["движение", "воля", "контроль"],
  "day_meaning": "…",
  "love_meaning": "…",
  "work_meaning": "…",
  "advice": "…",
  "warning": "…",
  "reflection_question": "…",
  "ui_short_text": "Сегодня важен управляемый темп",
  "max_lengths": { "ui_short_text": 80, "advice": 280 }
}
```

### 4.3 Что отдаётся куда

| Consumer | Machine | Content | Примечание |
|----------|---------|---------|------------|
| DayModel builder | ✅ full slice | ❌ | только шкалы |
| DayModel builder | ✅ | ⚠️ labels optional | labels не влияют на Vector |
| LLM interpret_* steps | ✅ summary | ✅ bounded slice | LLM **адаптирует**, не invent |
| Today UI hero/cards | ❌ | ✅ ui_short + generated | |
| Horoscope categories | ⚠️ transit codes | ✅ category text | |
| Calendar cell color | ✅ | ❌ | |
| Calendar day detail | ⚠️ | ✅ cached daily output | не raw reference dump |
| Profile portrait | ⚠️ | ✅ interpretation modules | через Profile Engine |
| Personal Map | ✅ positions | ⚠️ one-line only | без дневного слоя |

### 4.4 Что нельзя отдавать напрямую

| Запрещено | Куда | Почему |
|-----------|------|--------|
| Полный `machine_contract` в UI | web / iOS / Android | Шум, ломает UX, риск утечки правил |
| Raw LLM draft content | `active` reference | Нет review |
| Deprecated entries в новые генерации | pipeline | Ломает explainability |
| Весь Personal Map / full profile | LLM prompt | Selector обязан резать контекст |
| `internal_profile` aggregates дословно | UI | Только мягкая формулировка в «Почему так» |
| Смена `active` meaning без version bump | prod | Audit trail |
| Content без `max_lengths` в UI Copy | mobile | Переполнение вёрстки |

---

## 5. Build Order

### 5.1 Порядок построения справочников (P0 → P2)

| Phase | Домены | Критерий готовности |
|-------|--------|---------------------|
| **P0** | Tarot (78 cards), Numerology (core + cycles), Astrology (signs, planets, houses, aspects, moon) | Manual core `active`; Machine Contract на всех entities; Content — min viable per card/number/sign |
| **P1** | Emotional State, UI Copy (Today-critical keys) | Check-in slugs + tone/veto rules; CTA/microcopy catalogued with status |
| **P2** | Practice, Goal, Habit, Ascetic | Flow может подбирать практики/трекеры по machine tags |
| **P3** | Calendar Rhythm | Month map, day colors, filters |

**Внутри P0 (строгая очередь исполнения):**

1. P0.1–P0.2 DayModel contract + Machine JSON Schema ✅  
2. P0.3 Tarot major machine drafts ✅  
3. P0.4 Tarot-only DayModel preview ✅  
4. **P0.5 Numerology machine drafts** ✅  
5. **P0.7** Astrology Machine Contract ✅ (canon)  
6. **P0.8** Astrology atomic machine drafts ✅  
7. **P0.9** Cross-domain validation ✅  
8. **P1.0** DayModel multi-source ✅  
9. **P1.1** DayModel Interpretation Rules  
10. **P1.2** Compact User Model (CUM)  
11. [EVOLUTION_CALCULATION_CONTRACT.md](./EVOLUTION_CALCULATION_CONTRACT.md) → UEM-2  
11. Numerology / Tarot **content layer** (editorial text, не machine)  
12. Reference API read-only + migrate loaders  

Старый порядок «taxonomy → content → API» дополняется **Foundation First**: второй столп DayModel (Numerology) до Evolution/UEM consumers.

### 5.2 Что блокирует Daily Engine

Daily Engine (`build_day_context_v0`, `build_day_model_v0`) **не может считаться завершённым**, пока:

| Блокер | Домен |
|--------|-------|
| Нет нормализованных шкал карты / числа / astro | Tarot, Numerology, Astrology |
| Карта дня выбирается без stable `card_id` + version | Tarot |
| Personal day number без content anchor | Numerology |
| Emotional check-in без veto/tempo rules | Emotional State |
| Нет `reference_version` в daily artifact | все P0 |

### 5.3 Что блокирует Today Screen

| Блокер | Зависимость |
|--------|-------------|
| Новые блоки / CTA / layout | P0 reference + DayModel gate §10 DAY_ENGINE |
| Новые промпты guide / day_layer / spheres | P0 content + DEC-13 pipeline split |
| «Открыть карту дня» без pre-selected card | Tarot P0 + nightly job |
| Hero / microcopy не из catalog | UI Copy P1 |
| Категории гороскопа из LLM invention | Astrology P0 category lenses |

### 5.4 Что блокирует Calendar

| Блокер | Домен |
|--------|-------|
| Цвета дней / фильтры | Calendar Rhythm P3 |
| «Карта месяца» (сильные/слабые дни) | Calendar Rhythm + Daily Memory |
| Day detail без cached daily output | Daily Engine + Today pipeline |
| Streak / habit types без catalog | Habit P2 |
| Behavior → profile loop без typed events | Goal/Habit/Ascetic machine tags P2 |

### 5.5 Порядок после справочников (Global Build Order)

Полная очередь — [PERSONAL_INTELLIGENCE_LAYER.md](pim/PERSONAL_INTELLIGENCE_LAYER.md) §2. Кратко:

```
P0 Reference → Data Ownership (done) → PIL Architecture (done)
  → Profile Layer → Memory Layer → Daily Context Builder
  → Prompt Refinement → Evaluation Engine
  → Output Surfaces → Feedback Loop → Training Dataset
  → (later) Fine-tuning / Own Model
```

Внутри generation path:

```
Daily Context → DayModel → PIL (retrieval + refinement) → split Generation (DE-13)
  → Evaluation → Today / Tarot / Calendar surfaces → Feedback → PIL update
```

---

## 6. Reference Catalog (первый артефакт)

**Легенда Status:** `active` = в проде в текущей форме; `partial` = есть данные, нет unified model; `missing` = нет каталога; `draft` = в работе editorial.

**Origination / Filling:** creation method, update cadence, replenishment — [DATA_ORIGINATION_AND_LIFECYCLE.md](./DATA_ORIGINATION_AND_LIFECYCLE.md) §7–§8 (дополняется точечно при работе по домену).

| Domain | Entity | Stores | Machine Contract | Content Contract | Consumers | Status |
|--------|--------|--------|------------------|------------------|-----------|--------|
| Astrology | ZodiacSign | `DATA/astrology_reference/zodiac_signs.json` → `DATA/reference/astrology/machine/sign_*.json` | id, element, modality + **machine vector** | name, themes | Profile, Horoscope, DayModel **P1.0** | partial → P0.8 drafts |
| Astrology | Planet | `planets.json` → `planet_*.json` machine | id, rulerships + machine | keywords, psychology | Profile, DayModel | partial → P0.8 |
| Astrology | House | `houses.json` → `house_*.json` machine | life_domain, axes + machine | description | Personal Map, DayModel | partial → P0.8 |
| Astrology | Aspect | `aspects.json` → `aspect_*.json` machine | angle, tension + machine | description | Aspect engine, DayModel | partial → P0.8 |
| Astrology | AspectRelation | `aspect_relations.json` | relation codes, weights | — | Narrative rules | partial |
| Astrology | MoonPhase | `moon_phases.json` | degree_range, cycle_day | themes, guidance | Today foundation, notifications | partial |
| Astrology | PlanetaryCycle | `planetary_cycles.json` | cycle ids, periods | — | Cycles module | partial |
| Astrology | PlanetInSign | `planet_in_sign_relationships.json` | planet, sign, relation_code | meaning snippets | Compatibility, Profile | partial |
| Astrology | PlanetInHouse | `planet_in_house_relationships.json` | planet, house, relation_code | meaning snippets | Personal Map, Profile | partial |
| Astrology | CrossDomainBridge | `cross_domain_bridges.json` | bridge_id, from_domain, to_domain | — | Narrative engine | partial |
| Astrology | TransitTheme | — (computed + future ref) | transit_code, house_activation, tension | category blurbs | Daily foundation, Horoscope | missing |
| Tarot | TarotCard (major) | `DATA/reference/tarot/machine/*.json` + legacy content in `tarot_major_arcana.json` | vector axes, tempo, risk, confidence | upright, reversed, keywords | Today ritual, DayModel v1 preview loader | partial (22 machine drafts + P0.4 loader) |
| Tarot | TarotCard (minor) | — | suit, rank, correspondences | meanings per category | Tarot spreads | missing |
| Tarot | TarotSpread | `tarot_spreads.json` | spread_id, positions[] | position labels | API Guidance, Tarot UI | partial |
| Tarot | SpreadPosition | `tarot_spreads.json` (nested) | position_index, role code | title, meaning template | Tarot reading pipeline | partial |
| Numerology | LetterMapping | `DATA/numerology.json` | letter → value, vowels | — | Name calculations | active |
| Numerology | CoreNumber | `DATA/reference/numerology/machine/core_*.json` | value 1–9, vector/tempo/risk | energy, pattern (content TBD) | DayModel, Profile | partial (machine drafts P0.5) |
| Numerology | MasterNumber | `DATA/reference/numerology/machine/master_*.json` + `numerology.json` flags | 11, 22, 33 | content | Profile, Today | partial (machine drafts P0.5) |
| Numerology | PersonalDay | computed + `personal_day_*.json` machine | formula + machine by reduced 1–9 | day meaning (content TBD) | Morning ritual, DayModel | partial (machine P0.5) |
| Numerology | PersonalMonth | computed + `personal_month_*.json` machine | formula | month theme (content TBD) | Horoscope, Commerce | partial (machine P0.5) |
| Numerology | PersonalYear | computed + `personal_year_*.json` machine | formula | year theme (content TBD) | Profile, Commerce | partial (machine P0.5) |
| Emotional State | MoodSlug | ritual + tracking slugs | slug, intensity, tempo_bias, veto_tags | display label, verdict line | Today check-in, DayModel, LLM | partial |
| Emotional State | OperatingMode | `profile_engine/models.py` | enum, selector weights | — | Profile Selector, prompts | partial |
| Emotional State | CheckInDimension | `check_ins.json` | dimension id, scale | prompts | Tracking, fusion | partial |
| Practice | PracticeTemplate | `rituals.json`, `mantras.json` | category, duration, difficulty, state_tags | title, steps, outcome | Flow, Today recommendations | partial |
| Practice | PracticeCategory | — | code, parent | label | Practice picker | missing |
| Goal | GoalCategory | — | code (money, relations, …) | label, typical blocks | Profile, Today actions | missing |
| Goal | GoalType | — | cadence, difficulty | decomposition hints | Weekly goals, Calendar | missing |
| Habit | HabitType | — | frequency, min/opt, streak rules | name, relapse copy | Today trackers, Calendar | missing |
| Ascetic | AsceticType | — | rules, duration, contraindications | meaning, slip support | Today, Calendar | missing |
| Calendar Rhythm | DayType | — | type_code, load_level, color_token | short label | Calendar month | missing |
| Calendar Rhythm | DayColorStatus | — | color, filter_bit | — | Calendar UI | missing |
| Calendar Rhythm | MonthRhythmPattern | — | pattern rules on aggregates | map copy | Calendar «карта месяца» | missing |
| UI Copy | UiCta | `CONTENT/i18n/app.*.json`, `todayRitualCopy.ts` | key, max_length, surfaces[] | localized string | Today, iOS, Android | partial |
| Symbolic | Product SKU | — | sku, asset_refs, stage_gate | title, price | Commerce | missing |

**Следующий шаг после таблицы §6:** [DAYMODEL_INPUT_CONTRACT.md](./DAYMODEL_INPUT_CONTRACT.md) (P0.1) — Dependency Map и Machine fields; **затем** editorial draft scores; **затем** JSON Schema per entity.

---

## 7. Пополнение справочников

1. **Manual Core** — P0 entities вручную (`active`).  
2. **Expert Expansion** — категории, state variants (`review` → `active`).  
3. **AI-Assisted Drafts** — только `draft`; promotion только после human review.  
4. **Usage Feedback** — метрики open/save/ignore → revision ticket, не silent overwrite.

---

## 8. Связь с существующими канонами

| Документ | Роль после Reference Layer |
|----------|------------------------------|
| [PERSONAL_INTELLIGENCE_LAYER.md](pim/PERSONAL_INTELLIGENCE_LAYER.md) | Сквозной PIL: learning-aware features, два выхода, events, training dataset |
| [INTERPRETATION_LAYER_AND_REFERENCE.md](explainability/INTERPRETATION_LAYER_AND_REFERENCE.md) | Behavior Interpretation Reference |
| [USER_MODEL_TARGET_STATE.md](pim/USER_MODEL_TARGET_STATE.md) | Personal Path, PEG, stage → engine |
| [USER_MODEL_TARGET_STATE.md](pim/USER_MODEL_TARGET_STATE.md) | Cycles, paths, achievements |
| [REFERENCE_LAYER_AND_BUILD_ORDER.md](./REFERENCE_LAYER_AND_BUILD_ORDER.md) | Symbolic Reference + commerce rules |
| [KNOWLEDGE_ACQUISITION_AND_SIGNAL_POLICY.md](./KNOWLEDGE_ACQUISITION_AND_SIGNAL_POLICY.md) | Каналы сбора A–I, trust, confirmation gates |
| [USER_KNOWLEDGE_MODEL.md](pim/USER_KNOWLEDGE_MODEL.md) | Knowledge Atoms; fact/pattern/hypothesis |
| [API_MEMORY_AND_LEARNING_LAYER.md](./API_MEMORY_AND_LEARNING_LAYER.md) | API как актив: Gate (after UKM), cache/reuse, token ROI |
| [ASTROLOGY_COMPOSITION_MODEL.md](./ASTROLOGY_COMPOSITION_MODEL.md) | P0.8 gate — atomic only; composites → Composition Engine |
| [ASTROLOGY_MACHINE_CONTRACT.md](./ASTROLOGY_MACHINE_CONTRACT.md) | P0.7 — astro Machine Layer (third SoT pillar) |
| [CROSS_DOMAIN_MACHINE_VALIDATION.md](./CROSS_DOMAIN_MACHINE_VALIDATION.md) | P0.9 — one coordinate system; gates P1.0 DayModel |
| [ONTOLOGY_AND_FOUNDATION_PHASES.md](./ONTOLOGY_AND_FOUNDATION_PHASES.md) | **5 фаз построения**; текущий этап = онтология мира |
| [DATA_ORIGINATION_AND_LIFECYCLE.md](./DATA_ORIGINATION_AND_LIFECYCLE.md) | **Откуда** CD появляются, confirm, retire, filling policy; data-first freeze |
| [DATA_OWNERSHIP_AND_CONSUMPTION_MAP.md](./DATA_OWNERSHIP_AND_CONSUMPTION_MAP.md) | Кто владеет SN/RT; PIL читает slices |
| [DAY_ENGINE_AND_COHERENCE.md](./DAY_ENGINE_AND_COHERENCE.md) | DayModel / DayContext — **consumers** Machine Contract; входные шкалы — [DAYMODEL_INPUT_CONTRACT.md](./DAYMODEL_INPUT_CONTRACT.md) |
| [DAY_CONTEXT_V0.md](./DAY_CONTEXT_V0.md) | Форма входа; layers ссылаются на reference codes |
| [PERSONAL_INTELLIGENCE_LAYER.md](pim/PERSONAL_INTELLIGENCE_LAYER.md) | Порядок слоёв; generation **после** reference P0 |
| [API_MEMORY_AND_LEARNING_LAYER.md](./API_MEMORY_AND_LEARNING_LAYER.md) | Validator/safety — **после** freeze снятия для новых prompts |
| [TODAY_LANGUAGE_V1.md](today-language/TODAY_LANGUAGE_V1.md) | Quality gates на уже существующий guide — не новые промпты |

---

*При изменении taxonomy или таблицы §6 — bump версию документа и запись в PRODUCT_EXECUTION_TRACKER.*
