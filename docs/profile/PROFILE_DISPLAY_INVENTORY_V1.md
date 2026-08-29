# Profile Display Inventory v1

**Status:** ACTIVE — **SoT конструкции экрана `/profile`**  
**Date:** 2026-08-29  
**Роль:** закрытый список того, что пользователь **видит**. Каждое написанное слово имеет класс, источник, лимит и причину. Слот вне этого файла **не существует** на Profile.

**Не заменяет:** Character Engine ([PROFILE_EXPERIENCE_SCENARIO_V1](./PROFILE_EXPERIENCE_SCENARIO_V1.md)) · путешествие чувств ([PROFILE_PRODUCT_SURFACE_CANON](./PROFILE_PRODUCT_SURFACE_CANON.md)) · образцы форм ([PROFILE_PRODUCT_JOURNEY_FORMS_V1](./PROFILE_PRODUCT_JOURNEY_FORMS_V1.md)) · pipeline Snapshot ([PROFILE_CONTENT_CANON_V1](./PROFILE_CONTENT_CANON_V1.md)).

При конфликте «что на экране / сколько текста / откуда слово»: **побеждает этот файл**.  
Путешествие (зачем шаг) остаётся у Surface Canon. Образцы — у Forms. Смысл личности — у Character Engine.

**Пара:** [TODAY_DISPLAY_INVENTORY_V1](../today/TODAY_DISPLAY_INVENTORY_V1.md) — тот же закон конструкции для Сегодня.

---

## Architecture impact

- **SoT before:** конструкция Profile была размазана: Surface Canon (чувства) · Forms (образцы) · Screen Master (v0 layout) · Content Canon (pipeline) · живой UI с лишним актом «Портрет подробнее». Нельзя было ответить «какие именно слова на экране и почему» одним документом.
- **SoT after:** этот файл — закрытый display contract. Новый слот = строка здесь + Architecture impact. Код, которого нет в инвентаре, — drift, не продукт.
- **Public contract changed?** no JSON. Меняется правило **показа**, не поля Snapshot.
- **Migration required?** no runtime. Cutover UI: убрать акт Character warehouse со скролла (см. §4).
- **Canon updated?** yes — этот файл · `_INDEX` · README · Surface Canon pointer · Forms pointer · трекер.
- **Backward compatible?** да для API. UI, который рисует склад strengths/drains как отдельный шаг пути, **вне рамки**.

---

## 0. Закон конструкции (общий с Сегодня)

Один экран = предсказуемая конструкция. Не «ещё абзац, потому что поле есть в JSON».

### 0.1 Классы текста

| Класс | Кто пишет | FE может придумать? |
|-------|-----------|---------------------|
| **chrome** | константа UI (`profileV2SystemCopy`, лейблы архетипа) | нет — только этот список |
| **calc** | детерминированный расчёт (life_path, знак, стихия, ритм, ASC если время) | нет — показать факт |
| **generated** | LLM в **именованный** слот Snapshot / funnel | нет — только этот слот, после gate |
| **projected** | детерминированная проекция из generated (effort, bridge, why rows) | нет LLM |
| **user** | человек (имя, время рождения, living notes) | нет переписывания смысла |
| **catalog** | справочник (архетип SVG, numerology caption) | нет новой прозы |

FE **не** authority смысла. Clip на клиенте — защита длины, не авторство.

### 0.2 Три вопроса на каждый слот

Как Today Product Flow. Нет ответа → слота нет:

1. Откуда это взялось? (класс + поле + версия правил)
2. Почему система это показала? (job шага + appear_when)
3. Получим ли то же при тех же входах и той же версии? (reproducible)

### 0.3 Рамка

- Слот не в инвентаре → **не рисовать**.
- Пусто / gate закрыт → **omit**, не шаблон «для любого».
- Транспорт / `degraded` → «Нет соединения.» / «Не удалось загрузить.» — [AGENTS.md](../../AGENTS.md). Не выдумывать портрет.
- День, цели, камни, трекеры на Profile **запрещены** (PR-4).
- Голос: [TODAYFLOW_VOICE_CANON](../content/TODAYFLOW_VOICE_CANON.md) — человек, не система.

### 0.4 Как читать лимиты

Русский экран ~390px. Оценка: **1 короткая строка ≈ 8–14 слов ≈ 50–90 символов**.  
В коде гейт часто в **символах**. Оба числа обязательны: человеческий бюджет (предложения / строки) и машинный (chars).

| Метка | Смысл |
|-------|--------|
| **1 мысль** | 1 предложение, без «и… и… и…» списка черт |
| **1–2 строки** | перенос на мобиле, не абзац |
| **omit** | блока нет; дырки не заполнять |

---

## 1. Что содержится в профиле (модель → экран)

Профиль на экране — **первая проекция Character Engine**, не энциклопедия карты и не склад JSON.

```text
Факты рождения + расчёты     →  calc (Шаг 2)
Evidence Graph               →  kitchen / honesty, не простыня
Акт I одна мысль             →  recognition_name + recognition_line
Акт III–IV напряжение        →  один insight node
Компас derived               →  effort_vector (из help узла, без нового LLM)
Мост в день                  →  bridge_line (детерминированный)
Натал / числа                →  Explore, по запросу; не шаг узнавания
```

**Повтор тех же входов** (тот же fingerprint Snapshot + та же chrome-версия) → тот же набор блоков и те же базовые черты. LLM формулирует слот, не меняет каскад.

Другие модули (Today · Compat · Tarot) **читают Snapshot**, не пересобирают героя. См. Content Canon §2.

---

## 2. Скролл (LOCKED)

Ровно этот порядок. Нет шестого «акта портрета» на главном пути.

```text
[forming]     ← только пока портрет не ready
[data CTA]    ← только если не хватает времени/места (честный next step)
  1 Recognition     Шаг 1  меня поняли
  2 Why             Шаг 2  понятно почему
  3 Insight         Шаг 3  нашёл то, чего не замечал     ← один узел
  4 Effort          Шаг 4  куда усилие  (+ 0–2 сферы)
  5 Bridge          Шаг 5  зачем Today
  6 Explore         не шаг пути — склад карты / деталей по раскрытию
```

**New-value:** каждый следующий шаг даёт информацию, которой не было выше. Перефраз = дефект → слить или удалить.

---

## 3. Каталог блоков

Условные обозначения источника: `CE` = Character Engine consumption · `contract` = `profile_contract_v1` · `proj` = read-path projection · `live` = capability / userMessages.

---

### P-forming — Портрет ещё читается

| | |
|---|---|
| **Job** | Честно сказать, что ядро ещё не ready — без кухни пайплайна |
| **appear_when** | `portraitForming` / status forming |
| **omit_when** | Snapshot ready |

| Слот | Класс | Источник | Лимит | Почему |
|------|-------|----------|-------|--------|
| Сообщение | chrome (safe rewrite) | `FORMING_MESSAGE_RU` · `_safe_forming_message` | 2 предложения · ≤240 chars | Voice §0: не «генерация / тексты / формируется» |

**Запрет:** статус пайплайна, «ИИ считает», пустой экран без строки.

---

### P-data — Что откроет следующий шаг

| | |
|---|---|
| **Job** | Человек понимает, *чего не хватает ему*, не «системе мало данных» |
| **appear_when** | `live.userMessages` без `l3_gated` |
| **omit_when** | birth time+place достаточны / сообщений нет |

| Слот | Класс | Источник | Лимит | Почему |
|------|-------|----------|-------|--------|
| Текст CTA | chrome / capability copy | `userMessages[].text` | 1–2 предложения · ≤220 chars | ценность: ASC, дома, внешнее проявление |
| Кнопка | chrome | «Данные рождения» | 2 слова | ведёт в редактор фактов, не в генерацию |

**Запрет:** «Недостаточно данных», «Нам не хватает», day-лексика.

---

### P1 — Recognition (Шаг 1)

**Вопрос человека:** «Это про меня?»  
**Метрика:** узнавание ≤5 с без скролла. Share test: имя + линия + образ.

| Слот | Класс | Источник | Лимит | Почему |
|------|-------|----------|-------|--------|
| Visual | catalog | `baseline.archetype_seed` → `ArchetypeHeroVisual` | 1 объект, ≥ половины первого взгляда | образ первичен; pills запрещены |
| `recognition_name` | calc | `character_engine_consumption_v0.recognition_label` или RU label seed (`Architect`/`Harmonizer`/`Explorer`/`Sage`/`Observer` ← **только** life_path) | 1 слово / название | имя ядра; не «Личный профиль» |
| `recognition_line` | generated | `profile_contract_v1.recognition_line` | **1 мысль, 1–2 строки, 12–18 слов, 16–120 chars** | узнаваемое поведение; отличает архетип от соседних |
| Сигнал chrome | chrome | «Почему именно ты» / «Свернуть» | 2–3 слова | раскрытие, не второй логлайн |
| `identity_core` | generated | `profile_contract_v1.identity_core` | **только по тапу сигнала**; 2–4 предложения · ≤720 chars | кухня Шага 1; не первая строка |

**Fallback line:** если нет валидной `recognition_line` — первая фраза `identity_core`, если она проходит тот же gate; иначе omit line (не invent).

**Запрет на первом кадре:** Солнце/Луна/ASC/путь chips · список сил · совет «сегодня» · имя архетипа внутри line · второй абзац «кто ты» · eyebrow «Профиль».

**Анти-дубль → P2:** факт карты и его смысл живут в Why, не пересказом в герое.

Код: `ProfileRecognitionScene` · gate `validate_recognition_line`.

---

### P2 — Why (Шаг 2)

**Вопрос:** «Почему портрет звучит так — и что выбрало имя?»  
**Честность:** `selected_by` ≠ `portrait_influenced_by`. Солнце **не** выбирает имя Архитектора.

| Слот | Класс | Источник | Лимит | Почему |
|------|-------|----------|-------|--------|
| Заголовок шага | chrome | «Главное, что формирует тебя» / Forms: «Почему портрет звучит именно так» | 1 строка | job шага, не имя архетипа в заголовке |
| Секция selected | chrome | «Выбрало имя» | 2 слова | отделяет причину label |
| Строка архетип ← LP | calc + chrome glue | `numerology.life_path` + seed | 1 строка · факт + короткий смысл ≤120 chars | единственный selected_by |
| Секция influenced | chrome | «Расширяет портрет» | 2 слова | не причинность имени |
| Якорь Солнце | calc + meaning | `astro.sun_sign` + role-prose (framework / element bank / CE) | title 1–3 слова · detail факт · meaning **1 предложение, 12–22 слова, ≤160 chars** | как *у него* работает, не «Овен = лидер» из учебника |
| Стихия | calc + meaning | `astro.sun_element` | то же | расширение, не selected_by |
| Ритм | calc | `baseline.rhythm_style` **дословно** или укороченный факт | 1 строка · без UI-дописки | |
| Луна | calc + meaning | natal moon | omit если нет позиции | |
| ASC / MC | calc + meaning | rising / MC | **omit без reliable time** | |
| Honesty без времени | chrome | Forms sample | 2 предложения | что откроется *о нём*, не определение домов |
| Tap expand | presentation | sun / moon / asc / mc: свёрнутый meaning | hint chrome «Нажми — смысл за фактом» | плотность; смысл тот же слот |

**Роль-проза якоря:** существующий bank / CE / life_path helper. Нет текста → честный fallback «расширяет портрет», не LLM на read path.

**Запрет:** «вы Овен, поэтому Архитектор» · декоративные chips без meaning · дамп 12 домов · энциклопедия «7-й дом = партнёрство» · повтор `recognition_line` другими словами.

Код: `portrait_why_v0` · `ProfileWhyScene` · `buildWhyFormationCards`.

---

### P3 — Insight node (Шаг 3)

**Вопрос:** «Чего я раньше не замечал?»  
**Форма:** **один** узел-история. Не три зоны Strengths · Limits · Patterns.

First release: **макс. 1 узел** (`insight_nodes_v0.nodes[0]`).

| Слот | Класс | Источник | Лимит | Почему |
|------|-------|----------|-------|--------|
| Заголовок шага | chrome | «Что важно понять о себе» | 1 строка | |
| Eyebrow kind | chrome | «Твой дар» только для `kind=strength`; tension/repeat — **без** eyebrow | 2–3 слова | Forms: заголовок узла = единственный heading для ловушки |
| `title` | generated / projected | node.title из strengths / growth_zones / patterns | 1 строка · 4–10 слов · ≤80 chars | имя узла, не список |
| `insight` | generated | node.insight | **2–3 предложения · 30–55 слов · ≤360 chars на экране** (склад контракта ≤900 — kitchen) | новая ценность vs Шаг 1 |
| Опоры label | chrome | «Опоры» | 1 слово | |
| `grounded_on[]` | calc | подмножество фактов Шага 2 | **2–4 строки** · каждая = факт, не интерпретация · ≤80 chars | не утверждать точную причинность без trace |
| Что помогает label | chrome | «Что помогает» | 2 слова | |
| `help` | generated | node.help · иначе одна строка strengths/practical | **1 предложение · 12–22 слова · ≤140 chars** (склад ≤360) | опора, не day tip; kitchen-фразы («механизм проявляется», zone ids) — **скрыть** |
| Living label | chrome | «Как это уже проявлялось» + note «Контекст из отметок — не доказательство» | 1 строка + 1 note | |
| `living_evidence[]` | user | check-in / notes | **0–2 цитаты** · каждая ≤240 chars · 1 строка | **omit** без living; не выдумывать повтор |

**appear_when:** есть `title` + `insight`.  
**omit_when:** нечего сказать нового относительно P1.  
**patterns/helps LLM:** только если `patterns_generation_allowed`; иначе узел из strengths/growth + calc.

**Запрет:** три равных документа · living без сигналов · «подтверждённый паттерн» при закрытом gate · пересказ recognition_line.

Код: `profile_insight_nodes_projection_v0` · `ProfileInsightScene`.

---

### P4 — Effort (Шаг 4)

**Вопрос:** «Куда прикладывать усилия?» — одно предложение, не «кто я».

| Слот | Класс | Источник | Лимит | Почему |
|------|-------|----------|-------|--------|
| Заголовок | chrome | «Куда прикладывать усилия» | 1 строка | |
| Lead | chrome | «Одно направление — не ещё одно описание «кто ты».» | 1 предложение | анти-дубль Шага 1 |
| `effort_vector` | **projected** | **только** `nodes[0].help`, если проходит gate (глагол в начале · ≠ insight · ≠ recognition_line · нет «сегодня/завтра») | **1 предложение · 12–22 слова · 8–140 chars** | нет отдельного LLM; null → **omit всего блока** |
| Сферы | generated derived | `life_spheres` | **0–2 карточки на скролле** если дают *где*, не пересказ вектора. Заголовок 1–2 слова. Teaser 1 предложение · ≤88 chars. Expand: how/need/risk — по **1 предложению**, ≤220 chars | новая ценность после узла |

**Запрет:** `life_mission` как замена вектора · day agenda · императив «сделай сегодня» · swipe-лента из 8 сфер на главном пути (это склад → Explore).

Код: `profile_effort_vector_projection_v0` · `ProfileEffortScene`.

---

### P5 — Bridge (Шаг 5)

**Вопрос:** «Почему теперь открыть Today?» — не второе «что делать».

| Слот | Класс | Источник | Лимит | Почему |
|------|-------|----------|-------|--------|
| Заголовок | chrome | «Мост в день» | 1 строка | |
| `bridge_line` | **projected** chrome-pack | `profile_bridge_line_projection_v0`: tension-pack **или** repeat-pack по `kind` узла | **2 предложения · 20–40 слов · ≤220 chars** | детерминизм; не LLM; не дубль effort |
| CTA | chrome | «Открыть Today →» | 3 слова | навигация, не совет |

Packs (смысл, не invent):

- tension: особенность ясна на портрете → Today показывает проявление в конкретном дне.
- repeat: повтор назван → Today — экран, где видно проявление и сдвиг.

**Запрет:** императив · прогноз дня · камень дня · пересказ effort_vector.

Код: `ProfileBridgeScene`.

---

### P6 — Explore / Натальная карта (не шаг пути)

**Вопрос:** «Как устроена карта, которая уже объяснила ядро?»  
**Триггер:** человек раскрыл склад. Не авто-портрет.

| Слот | Класс | Источник | Лимит | Почему |
|------|-------|----------|-------|--------|
| Заголовок | chrome | «Натальная карта» | 1 строка | |
| Колесо / preview | calc | natal preview | визуал, не простыня аспектов на collapsed | |
| Числа | calc | numerology facets | факты; без «имя»-glyph | |
| Детали контракта | generated | `progressiveDetails` — слоты, **не** занятые узлом (anti-dupe) | каждая деталь: title chrome + 1–2 предложения · ≤240 chars | склад, не новый акт пути |
| Сферы остаток | generated | сферы сверх 0–2 на P4 | same limits as P4 expand | |
| Стили (решения / близость / деньги) | generated | `decision_style` · `relationship_style` · `money_style` | **по 2–4 предложения · ≤520 chars склад · на экране 2 предложения, ≤280 chars** | **только здесь**, не отдельный акт «Портрет» |
| Natal Decode | generated opt-in | `POST` explicit · [PROFILE_NATAL_DECODE_DEPTH_V1](./PROFILE_NATAL_DECODE_DEPTH_V1.md) | длинная проза только после CTA; дома на базе = тезисы `how`/`do` 1–2 предложения | не второй логлайн |

**Запрет:** маркетинговый список «Потенциалы и таланты / Уроки жизни / Периоды силы» без данных · авто-decode на GET · энциклопедия домов.

---

## 4. Вне рамки (не рисовать на `/profile`)

| Что | Почему |
|-----|--------|
| Акт **«Портрет подробнее»** (склад strengths / drains / helps / patterns как равный шаг 04) | ломает new-value; материалы → P3 узел или P6 |
| `life_mission` отдельной карточкой на скролле | дубль P4 или кухня; omit если есть effort_vector |
| Living Maps / My Days / week heatmaps | `/maps/*`, `/tracking/*` |
| Today: энергия, ловушка дня, обещание, цвет | PR-4 |
| Compatibility hub | другой продукт |
| Сырой dump 12 домов / аспектов на первом экране | P2 = якоря; P6 = карта |
| Имя как numerology-glyph | Social Mirror v0 killed |
| FE-invented calm / «нет сигнала» при ошибке сети | честный failure copy |

---

## 5. Код сейчас vs замок

Честно, чтобы не путать ledger с рамкой.

| В коде сейчас | Замок инвентаря |
|---------------|-----------------|
| `ProfileCharacterScene` на главном скролле (шаг 04 «Портрет») | **drift** — убрать с пути; стили → P6 |
| Сферы Act 4 до 8 в swipe | на пути **0–2**; остальное Explore |
| `why.honesty` в projection часто `null` | без времени — **обязателен** chrome honesty |
| `identity_core` за сигналом | **разрешено** как disclosure, не как line |
| Explore `benefits[]` три обещания | **запрещены** — не слот данных |
| `PROFILE_LIMITS` (heroTagline 110, sphereMain 88…) | наследие v0; для V2 journey действуют лимиты **этого файла** |

Cutover UI не требует нового JSON: скрыть Character act, если узел уже забрал материалы (`omitMaterialLists` уже есть — довести до «сцены нет»).

---

## 6. Проверка (воспроизводимость)

Для одного и того же Snapshot fingerprint + chrome version:

1. Набор блоков совпадает (forming / data / P1–P6).
2. P1: name из life_path mapping; line проходит `validate_recognition_line`.
3. P2: первая содержательная строка selected_by = LP→архетип; Солнце не в selected.
4. P3: ровно один узел или omit; living пуст → слота нет.
5. P4: отсутствует, если help не action-line; текст не содержит «сегодня».
6. P5: не начинается с императива; не равен effort_vector.
7. Нет слов из `PROFILE_V2_FORBIDDEN_LEXICON` (день, «Мы рассчитали», «Профиль готов»).

Ручной проход: Forms samples Case A (birth-only) и Case C (living) — [PROFILE_PRODUCT_JOURNEY_FORMS_V1](./PROFILE_PRODUCT_JOURNEY_FORMS_V1.md).

---

## Changelog

| Date | Change |
|------|--------|
| 2026-08-29 | v1.0 — закрытый display contract Profile; Character warehouse вне рамки; лимиты слотов |
