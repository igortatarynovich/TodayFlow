# Interpretation Library v1 — ontology / schema

**Статус:** ACCEPTED (канон схемы и порядка работ) — **IL-1 in progress** (24 draft objects: classical seven · 12 houses · 5 major aspects; no sign objects yet; nothing `active`).  
**Версия:** 1.3 (2026-08-17).  
**Методология:** **LOCKED** до закрытия IL-1 (~100 объектов). Не переоткрывать схему слоёв / evidence / provenance / ingest, пока модель не столкнётся с источниками.  
**Владелец:** Product + Research.  
**Данные:** `DATA/reference/astrology/interpretation_v1/` — corpus · `claims/` · `objects_v1.json` (draft).  
**Схема:** [astrology_interpretation_v1.schema.json](../schemas/astrology_interpretation_v1.schema.json) · claims ledger [astrology_claims_v1.schema.json](../schemas/astrology_claims_v1.schema.json).  
**Пример формы (не SoT смысла):** [astrology_interpretation_v1.example.json](../schemas/fixtures/astrology_interpretation_v1.example.json).

**Роль:** семантическая база астрологических примитивов (данные, не пользовательский текст). Для **Today** это шаг 2 pipeline ([TODAY_CONTENT_PIPELINE_V1](../today/TODAY_CONTENT_PIPELINE_V1.md) — **единственный Meaning SoT дня**): «Astrology Interpretation Canon (lookup)». Не второй канон дня. Тот же lookup читают Profile · Compatibility · Tarot-context.

---

## Architecture impact

- **SoT before:** pipeline step 2 («Astrology Interpretation Canon») named as **дыра**; смысл примитивов размазан (Foundation keywords · legacy JSON · AMC vectors · LLM invention).
- **SoT after:** Interpretation Library = that lookup (atoms first, curated Layer 5). Runtime: Swiss/JPL → calculation → IL → engine → expression. Licensing Swiss = parallel gate. Engine clusters + ranks; LLM выражает pack. **Today Meaning SoT остаётся** TODAY_CONTENT_PIPELINE_V1.
- **Public contract changed?** no (пока нет runtime wiring).
- **Migration required?** no until IL-4 (Expression). Legacy content JSON не удалять до `active` атомов.
- **Canon updated?** this doc · pipeline §2 · AMC §2.2 · ACM · Foundation §2 compose rule · DAY_SOURCES цепочка · tracker freeze.
- **Backward compatible?** yes — generators continue until Engine consumes packs.

---

## 0. Зачем останавливать Today-контент

Сейчас продукт пытается получить качественный **персональный** результат раньше, чем есть система знаний, из которой результат собирается.

Pipeline уже назвал дыру: **Astrology Interpretation Canon (lookup) — нужен**. Пока lookup пуст, Global/Personal Narrative продолжают «вспоминать» значения в промпте.

Это не библиотека гороскопов и не тысячи абзацев.  
Один knowledge object → десятки корректных пользовательских выражений.

**Freeze (Today content):** не расширять narrative prompts / formula banks / slot-polish, пока нет IL-3 Engine (темы выбираются до LLM). I0 и product cycle **не** переоткрываются.

**Freeze (методология IL):** не менять corpus method / evidence tiers / provenance / ingest rules до первых ~100 объектов (IL-1). Дальше — только баги модели, которые вскроет столкновение с источниками.

**Разрешено параллельно:** транспортная честность, routing, visual foundation, DS, баги, геометрия, ScreenFlow без новой семантики, **Swiss licensing gate** (не блокирует research IL-1).

Сиблинги (уже есть, не дублировать):

| Домен | Meaning SoT | Machine SoT |
|-------|-------------|-------------|
| Tarot | [TAROT_CARD_BASE_V1](../tarot/TAROT_CARD_BASE_V1.md) + [KB](../tarot/TAROT_KNOWLEDGE_BASE_V1.md) | `DATA/reference/tarot/machine/` |
| Numerology | [NUMBER_BASE_V1](../numerology/NUMBER_BASE_V1.md) | `DATA/reference/numerology/machine/` |
| Astrology | **этот документ** (IL-1 draft) | AMC 39 атомов |

**Не путать с ILR** ([INTERPRETATION_LAYER_AND_REFERENCE](../explainability/INTERPRETATION_LAYER_AND_REFERENCE.md)): там signals поведения пользователя. Здесь — символические примитивы.

---

## Sequence (LOCKED)

```text
IL-0 Foundation
  corpus registry · evidence levels · provenance schema · legal/licensing gates (declared)
       ↓
IL-1 Canon primitives   ~100 surface-neutral objects · corpus only · review
       ↓
IL-2 Composition        planet×sign · planet×house · aspect · natal aspect
                        transit→natal · merge of several signals
       ↓
IL-3 Interpretation Engine
  Swiss/JPL → calc facts → knowledge objects → clustering
  → relevance → primary / supporting themes
       ↓
IL-4 Expression         generative layer only here
                        meaning already chosen; voice for Profile / Today / Compatibility
       ↓
scale the library
```

| ID | Что это | Не это |
|----|---------|--------|
| **IL-0** | Foundation: корпус, методика, schema, declared gates | наполнение объектов |
| **IL-1** | ~100 канонических объектов из корпуса | `today_message` / проза экрана |
| **IL-2** | **правила** композиции (не каталог всех пар) | 10 000 JSON-гороскопов |
| **IL-3** | детерминированный engine тем | LLM |
| **IL-4** | выражение уже выбранного смысла | решение «что значит Saturn □ Venus» |

**IL-0 закрыт** (2026-08-17) как foundation. Следующий execution slice = **IL-1**.  
Масштаб библиотеки — только после IL-4.

### Runtime stack (Swiss *в* IL-системе)

Лицензию Swiss выносим из content/research track. **Эфемериды из IL-системы не выносим.**

Без Swiss (или другого ephemeris source) динамическая часть IL не знает, какие knowledge objects активны сейчас.

```text
Swiss Ephemeris / JPL     что физически где и когда
        ↓
Calculation layer         знаки, дома, аспекты, транзиты, орбисы
        ↓
Interpretation Library    что эти конструкции означают
        ↓
Interpretation Engine     какие значения важны этому человеку сейчас
        ↓
Expression                как показать (Profile / Today / Compatibility)
```

Пример:

```text
Swiss: Saturn = 14° Aries, natal Venus = 14° Cancer
  → calc: transiting Saturn square natal Venus
  → IL: knowledge object astro.combo.transit.saturn.square.natal.venus
  → engine: relevance / aggregation
  → Today (IL-4 pack, surface=today)
```

Ответственность не смешивать:

| Слой | Решает | Не решает |
|------|--------|-----------|
| Swiss / JPL | долгота, время, координаты | смысл Saturn □ Venus |
| Calculation | аспект, дом, орбис, «это square» | трактовку |
| Interpretation Library | каноническое значение конструкции | что показать *этому* человеку *сегодня* |
| Interpretation Engine | активность, кластер, relevance | прозу экрана |
| Expression | формулировку под surface | астрологическое значение |

**IL-1 constraint:** первые ~100 объектов проектировать под сущности, которые реально выдаёт Swiss + наш Astro/calculation layer (`transiting_planet`, `aspect`, `natal_point`, sign, house, major aspect ids). Не вводить в канон конструкции, которых calc не эмитит (квинконс OOS v1 — Foundation §2.4). Иначе получится ontology, которая плохо маппится на вход IL-3.

### Surface-neutral (жёстко, IL-1)

Первые ~100 объектов **не пишутся под Today**.

Запрещены поля и смыслы вида `today_message`, `today_copy`, `profile_blurb`, `compatibility_line`, «сообщение на сегодня», CTA экрана. Saturn = function / themes / domains / polarity — не заготовка строки Today.

Тест объекта шире, чем sky → Today:

> Один knowledge object, если релевантен, должен корректно обслужить **Profile**, **Today** и **Compatibility**. Разница поверхностей — IL-4 Expression pack (tone, length, focus), не разные значения в каноне.

### Swiss licensing — параллельный gate, не отдельный технический мир

Эфемериды = вход runtime IL (см. Runtime stack).  
**Лицензия** Swiss = бинарный legal gate (Foundation §1.4): коммерческое использование текущей `pyswisseph` конфигурации либо покрыто выбранной лицензией, либо до публичного сервиса меняется лицензирование/реализация.

Лицензионный вопрос **не блокирует** research Greene/Hand/Valens и создание первых 100 knowledge objects.  
До проверки полного pipeline `raw sky → knowledge objects → Today` Swiss уже является входом этого pipeline.

Не писать «Swiss вне IL». Писать: **Swiss licensing вне content track IL**.

---

## 1. Слои (строить строго снизу)

Комбинаторный взрыв `planet × planet × aspect × house × sign` **запрещён** как каталог. Согласовано с [ACM-Compose](../ASTROLOGY_COMPOSITION_MODEL.md): атомы в Reference; композиты — runtime. Исключение: **узкий curated Layer 5** только там, где сложение атомов врёт.

```
Layer 1 Objects  →  Layer 2 Signs  →  Layer 3 Houses  →  Layer 4 Aspects
        ↓
Layer 5 Combinations (compose default; curated if non-compositional)
        ↓
Meaning normalization (theme clusters)
        ↓
Profile relevance (priority, not meaning)
        ↓
Expression pack → LLM (IL-4; voice only; `surface` lives here)
```

### Layer 1 — Objects

Sun · Moon · Mercury · Venus · Mars · Jupiter · Saturn · Uranus · Neptune · Pluto · ASC · MC.

v1.1: North Node · South Node · Chiron · Lilith (Mean Apogee) — identity уже в Foundation §2.2.

Поля: `function` · `themes[]` · `positive_expression` · `shadow` · `domains` · `tempo`.

Не статья «Что такое Сатурн».

### Layer 2 — Signs

Aries → Pisces.

Поля: `mode` · `element` · `orientation` · `motivation` · `expression` · `strengths[]` · `excess[]` · `deficiency[]` · `behavioral_tendencies[]`.

Identity (ruler, dates) остаётся в Foundation §2.1 — **не копировать** в IL.

**IL-1 fill:** `motivation` / `strengths` / `excess` / `deficiency` / `behavioral_tendencies` не «ошибка схемы». Это слоты более позднего интерпретационного слоя — ждать локусы (Arroyo, Rudhyar, …). Классические деления знака (Ptolemy I.14–I.15, I.21; Lilly CA I.16) их не подтверждают. 12 sign objects не материализовать искусственно.

`element` и `mode` **не унифицировать** задним числом: Lilly fiery/earthly/airy/watry и Ptolemy winds/rulers — разные системы; Ptolemy tropical/equinoctial ≠ Lilly moveable/cardinal. Mismatch со schema (`cardinal|fixed|mutable`, четыре стихии) — gap_note, не silent collapse.

### Layer 3 — Houses

1–12.

Поля: `domain` · `internal_meaning` · `external_manifestations[]` · `people[]` · `activities[]` · `resources[]` · `risks[]`.

**IL-1 fill:** topical houses в draft-объектах = Lilly CA I.7. То, что Lilly ссылается на «Ptolomeian Doctrine», не есть Ptolemy+Lilly consensus. Compared — только после открытого topical locus у Ptolemy.

### Layer 4 — Aspects (major only, v1)

Conjunction · Opposition · Square · Trine · Sextile.

Не готовые трактовки пар, а **характер взаимодействия**:

| Аспект | `interaction` |
|--------|----------------|
| conjunction | merging / amplification |
| square | friction requiring action |
| opposition | polarization / projection |
| trine | easy flow / access |
| sextile | opportunity requiring participation |

Таблица — **смысл слота**, когда локус его подтвердит. Не default для копирования в объект.

**IL-1 fill:** Ptolemy I.16 даёт только harmonious / discordant. `requires_action` в схеме — boolean (нет `unknown` / `not_evidenced`). `false` = свойство **не установлено данным локусом**, не утверждение «square не требует действия». Схему из-за этого не расширять.

Миноры (Foundation §2.4) — не Layer 4 v1.

### Layer 5 — Combinations

Только после атомов.

Типы: `planet_in_sign` · `planet_in_house` · `natal_aspect` · `transit_to_natal` · `transit_through_house`.

**Default (IL-2):** Composition Engine собирает объект из атомов (не JSON на каждую пару).  
**Curated (часть IL-1 gold):** только `curation_reason: non_compositional` — значение нельзя надёжно сложить; всё равно **surface-neutral**.

Хранить в `DATA/reference/astrology/interpretation_v1/` — **не** в `machine/`. ACM freeze на composite **machine** JSON остаётся.

---

## 2. Knowledge object (данные, не copy)

Пример формы — транзит, не пользовательское предложение:

| Поле | Содержание |
|------|------------|
| phenomenon | Saturn square natal Venus |
| type | `transit_to_natal` |
| base_meaning | ограничения / проверка ценностей, отношений, удовольствия |
| psychological | переоценка привязанностей и собственной ценности |
| domains.relationships | дистанция, серьёзность, проверка отношений |
| domains.money | ограничения, осторожность, пересмотр расходов |
| domains.work | ценность собственного труда, компенсация |
| opportunity | установить более зрелые границы |
| risk | изоляция, холодность, чрезмерный пессимизм |
| action | пересматривать, устанавливать границы, упрощать |
| avoid | окончательные выводы из временного эмоционального состояния |
| intensity | runtime (орбис) — в объекте только `intensity_rule` |
| temporal_class | `medium` |
| polarity | `challenging` + `constructive` |
| theme_clusters | `relationships` · `boundaries` · `values` |
| confidence | после review |
| provenance | source → passage/concept → normalized claim → reviewer → version |

Engine уже может сказать (это **не** хранится в объекте):

- *Relationships may feel more serious than usual today. Don’t mistake temporary distance for a final answer.*
- *Money decisions deserve more scrutiny right now. What feels restrictive may actually be forcing you to clarify what is worth paying for.*

### Запрещено в объекте

- обращение на «ты» / «you»;
- «сегодня», даты, имена;
- поля экрана (`today_message`, `profile_blurb`, `compatibility_line`, …);
- абзацы-гороскопы;
- коммерческие дампы (Co-Star и аналоги);
- текст, единственный источник которого — LLM.

---

## 3. Meaning normalization

Несколько независимых сигналов часто описывают **один** кластер.

Нельзя печатать четыре интерпретации:

- relationships difficult
- relationships serious
- relationships challenged
- emotions intense

Engine поднимает кластер:

`RELATIONSHIPS` / `BOUNDARIES` / `EMOTIONAL_PRESSURE`

Три независимых сигнала об одном → выше `confidence` / relevance темы.  
На экране: **Today’s relationship theme**, не перечень транзитов.

Закрытый набор `theme_clusters` (v1):

`identity` · `emotions` · `relationships` · `boundaries` · `values` · `money` · `work` · `communication` · `body` · `home` · `growth` · `meaning` · `power` · `change` · `timing`

Новый кластер = bump контракта, не свободная строка.

---

## 4. Profile relevance ≠ астрологическое значение

```
Sky × Natal × Profile × Current goals/context  →  Relevance
```

Тот же транзит не занимает одно место у всех. Если сигнал про `work`, а у человека активна карьерная цель — **растёт приоритет показа**. Астрологическое значение **не** переписывается.

Это не персонализация смысла («у тебя Сатурн значит другое»). Это ранжирование.

---

## 5. LLM — только IL-4 Expression

LLM **не** решает, что означает Saturn square Venus.

Вход (expression pack):

```yaml
primary_theme: boundaries in relationships
theme_clusters: [relationships, boundaries]
supporting_signals:
  - astro.combo.transit.saturn.square.natal.venus
  - astro.combo.planet_in_house.moon.07
opportunity: clarify expectations
risk: interpreting distance as rejection
profile_relevance:
  note: relationship goal active
  boost: 0.4
tone: direct_grounded
length_words: [22, 35]
locale: en
surface: today
```

Задача модели: выразить это хорошо.  
Запрет: новые темы, астрожаргон как содержание, прогноз-дата, противоречие pack.

Это тот же паттерн, что Tarot pack: факты в KB, LLM — автор ответа.

---

## 6. Research corpus — как собираем, не «какую базу скачать»

Готовой Interpretation Library не существует. Её нужно **собрать**: традиционная основа + современная интерпретация + собственная нормализация.

Реестр кандидатов: [`DATA/reference/astrology/interpretation_v1/source_corpus_v1.json`](../../DATA/reference/astrology/interpretation_v1/source_corpus_v1.json) (~35 источников, все `status: candidate`).  
Схема: [astrology_source_corpus_v1.schema.json](../schemas/astrology_source_corpus_v1.schema.json).

Ни один источник не `approved` как закрытый product-SoT, пока строка не прошла legal review. **IL-1 не ждёт этого для всех 36 строк:** при `ingest_rule: research_paraphrase` можно извлекать claims из `candidate`. Копирование текста запрещено. Swiss dual-license **не** условие старта IL-1.

### 6.1 Четыре уровня источников (смысл)

| Уровень | `source_class` | Зачем | Примеры в корпусе |
|---------|----------------|-------|-------------------|
| Первоисточники | `classical` | исторический фундамент западной традиции | Ptolemy *Tetrabiblos* · Valens *Anthologies* · Dorotheus *Carmen* · Firmicus *Matheseos* · Lilly *Christian Astrology* |
| Живая традиционная школа | `traditional` | нормализация ontology (аспект ≠ «плохо») | Skyscript · Deborah Houlding (houses, aspects/orbs) |
| Психологическая | `psychological` | человеческая динамика | Greene · Sasportas · Arroyo · Rudhyar · Demetra George |
| Практические транзиты | `professional` | язык Today (transit-to-natal) | Robert Hand *Planets in Transit* · Tierney · Sullivan |

**Project Hindsight** (с 1993) — доступ к эллинистическим текстам. Это **программа переводов**, не один том. Древний оригинал может быть public domain; **современный перевод защищён**. Hindsight = research, не копипаст в JSON.

Skyscript: структурированная библиотека (planets, houses, aspects, natal, predictive, stars, rulerships, orbs, history). Houlding по аспектам/орбам нужна именно ontology: planetary orbs vs modern aspect orbs. **Статьи не копировать** — концепт → сверка → своя запись.

Несколько независимых школ обязательны. Не выбираем одного «правильного» автора.

### 6.2 Астрономия — вход IL, не источник смысла

Положения тел **не** берутся с astrology websites. Они питают calculation layer, который активирует объекты IL.

| Источник | Роль у нас |
|----------|------------|
| **Swiss Ephemeris** | LIVE runtime вход: `todayflow-astro` · `pyswisseph` · `FLG_SWIEPH` · `astro/ephe` |
| NASA/JPL Horizons | кандидат на независимую сверку позиций; не wired |

Swiss Ephemeris — **dual license** (Astrodienst): GNU AGPL **или** Swiss Ephemeris Professional License. Выбор должен быть сделан **до** публичного сервиса. В репозитории **нет** артефакта Professional License. `todayflow.today` уже публичен.

Это **legal gate** (Foundation §1.4), параллельный content/research track. Не стоп для IL-1. Не отдельный от IL технический мир: без эфемерид IL-3 не знает активных объектов.

`ingest_rule: facts_only` — Swiss/JPL не дают трактовок в knowledge object.

### 6.3 Запрещено как фундамент

Не строить IL на: Astro-Seek interpretations · random blogs · Reddit · TikTok/Instagram astrology · Co-Star · The Pattern · Sanctuary · **ChatGPT/LLM-generated interpretation dumps**.

«Создай 5000 трактовок» даёт объём без происхождения. Это противоположность IP, который нам нужен.

### 6.4 Юридическое правило ingest

```text
оригинал / издание  →  исследователь читает
                    →  записывает УТВЕРЖДЕНИЕ (paraphrase)
                    →  указывает locus (глава/стр.), не цитату перевода
                    →  в библиотеку попадает normalized_claim
```

**Запрещено** класть в объект / claim ledger: абзац современного перевода, скрап Skyscript, текст Co-Star, вывод LLM как `source`.

IL-1 research artifacts (pipeline, not a new ontology): `DATA/reference/astrology/interpretation_v1/claims/<object_id>.json` → `objects_v1.json`. Ledger schema: [astrology_claims_v1.schema.json](../schemas/astrology_claims_v1.schema.json). Knowledge-object schema не расширяется «на всякий случай»; дыры фиксируются в `gap_notes` на реальном материале.

`original_claim` в provenance = **наша** короткая формулировка утверждения автора, не его copyrighted prose.

### 6.5 Методика одного объекта (пример: Saturn square natal Venus)

Берём Hand · Greene · traditional (Lilly/Houlding/Skyscript) · ещё 1–2 professional.

Из каждого — не текст, а **утверждения**:

`constraint` · `relationship testing` · `value reassessment` · `financial restraint` · `self-worth` · `distance` · `commitment` · `maturation`

Смотрим пересечение.

Если 4 независимых источника: restriction + relationships + values + maturation → кандидат в **CORE**.

Если один автор: «обязательно произойдёт расставание» → **не** входит в базу автоматически. Максимум `school_specific` после review, чаще `rejected`.

### 6.6 Уровни доказательности

| `evidence_tier` | Смысл | Что можно в продукте |
|-----------------|-------|----------------------|
| **core** | почти все выбранные школы | primary theme Today / Profile |
| **supported** | несколько авторитетных источников | supporting signals |
| **school_specific** | одна школа | tint; не выдавать как «астрология говорит» |
| **editorial** | нормализация TodayFlow | только с reviewer; не маскировать под традицию |

Разница обязательна:

- Пока CORE по Saturn **не scored**: открыты только classical loci (холод / сухость / malefic). *Structure / limits / maturity* — не CORE до Greene/Hand (или иного открытого психологического/профессионального локуса).
- не CORE: *Saturn square Venus значит, что партнёр отдалится*

Канон — не усреднённая «одна астрология». Provenance держит слои различимыми. Когда придут Greene, Hand, Sasportas, Arroyo, George: смотреть, что с классическим claim произошло (продолжено / переосмыслено / психологизировано / заменено). Классические lemmas **не затирать** современным пакетом.

Engine: primary theme только из `core` ∪ `supported`. `editorial` не может быть единственным основанием пользовательского утверждения.

### 6.7 Пайплайн (не 50 книг вручную в таблицу)

```text
corpus (classical + traditional + psychological + transit)
        ↓
извлечение утверждений
        ↓
нормализация (свои lemmas)
        ↓
сопоставление авторов
        ↓
consensus scoring → evidence_tier
        ↓
human review
        ↓
Interpretation Library object
```

LLM в этом пайплайне **может** помогать извлекать кандидаты-утверждения из текста, который исследователь уже легально читает. Не может быть источником. Каждая строка проходит human review.

### 6.8 Provenance (IP)

Через год «почему Saturn □ Venus = проверка отношений?» → конкретные `concept_id`, авторы, издания, locus, normalized_claim, tier, reviewer — не «так написал GPT».

Поля claim / provenance row:

`concept_id` · `source` · `author` · `edition` · `locus` · `original_claim` (paraphrase) · `normalized_claim` · `school` · `evidence_tier` · `review_status` · `field`

`review_status`: `extracted` → `compared` → `reviewed` | `rejected`.

---

## 7. Масштаб

Фундамент конечен:

12 signs · 12 houses · 12 Layer-1 objects · 5 major aspects · углы уже в Layer 1 · dignity/rulership — Foundation §2.5 (не дублировать в IL).

Дальше комбинации **композиционно**. Вручную curated — где сложение атомов врёт.

Не начинать с 10 000 комбинаций. Не менять методологию до конца IL-1. Порядок = **Sequence (LOCKED)** выше.

| ID | Работа | Выход |
|----|--------|--------|
| **IL-0** | Foundation: корпус, evidence, provenance, declared gates | ✅ 2026-08-17 |
| **IL-1** | ~100 surface-neutral objects из корпуса + review | in progress (24 drafts: planets 7 · houses 12 · aspects 5; signs withheld) |
| **IL-2** | Composition rules (не полный каталог пар) | after IL-1 |
| **IL-3** | Interpretation Engine (sky → themes) | after IL-2 |
| **IL-4** | Expression (LLM / voice per surface) | after IL-3 |

Масштаб библиотеки — после IL-4. Если на IL-1 модель не выдерживает источники — чинить ontology, не плодить объекты и не трогать Today-прозу.

---

## 8. IL-1 gold set — первые ~100 (surface-neutral)

Не «контент Today». Слои 1–4 целиком, затем non-compositional combinations, которые нельзя надёжно сложить из атомов. Остальное — IL-2 rules.

### Атомы (41)

- Objects (12): sun, moon, mercury, venus, mars, jupiter, saturn, uranus, neptune, pluto, asc, mc
- Signs (12): aries…pisces
- Houses (12): 01…12
- Aspects (5): conjunction, opposition, square, trine, sextile

### Non-compositional combinations (~50–60)

Не полный декартов продукт. Критерий: значение нельзя надёжно сложить из атомов, объект годен Profile / Today / Compatibility, **и** конструкция есть в output calculation layer (Swiss + Astro).

**transit_to_natal:** Saturn□natal Venus, Saturn□Moon, Saturn□Sun, Saturn□Mars, Saturn☍Venus, Saturn☍Moon, Saturn☌Sun, Saturn☌Moon, Jupiter△Sun, Jupiter□Saturn, Uranus□Moon, Uranus☍Venus, Neptune□Venus, Pluto□Sun, Pluto□Venus.

**transit_through_house:** Saturn→7, Saturn→10, Jupiter→10, Uranus→7, Pluto→1.

**natal_aspect:** Moon□Saturn, Moon☍Saturn, Moon☌Saturn, Venus□Saturn, Venus☍Saturn, Mars□Saturn, Sun□Saturn, Moon□Pluto, Venus□Pluto, Mars□Pluto, Sun☌Saturn, Venus☌Mars, Mercury□Neptune, Mars□Uranus.

**planet_in_sign:** Moon Scorpio, Moon Capricorn, Saturn Aries, Saturn Cancer, Venus Capricorn, Venus Aries, Mars Cancer, Mars Libra, Sun Pisces, Mercury Pisces.

**planet_in_house:** Saturn 7/10/4, Moon 7/10/12, Venus 7/2, Mars 1/10, Sun 10.

Итого порядка **90–100** объектов. Gate IL-1: corpus → claims → normalized object → human review. Настоящие дыры ontology вскроются здесь — не в теории.

---

## 9. Связь с уже принятым каноном

| Канон | Что остаётся | Что меняет IL |
|-------|--------------|----------------|
| TODAY_CONTENT_PIPELINE | I0, Global/Personal authority, LLM формулирует | Step 2 lookup = этот файл; IL не Meaning SoT дня |
| Foundation §2 | identity, орбисы, dignity L1–L3 | семантика глубже keywords; **комбинации не синтезирует LLM** |
| AMC | 39 machine vectors | Content Contract = IL, не legacy psychology one-liners |
| ACM | атомы в machine/; compose runtime | Layer 5 curated **interpretation** files allowed |
| DAY_SOURCES | факт (эфемериды) | «значение в системе» = IL |
| EXPLAINABLE_INTERPRETATION | pack → LLM | pack наполняется из IL, не из свободного промпта |
| Daily Interpretation Engine | DailyState / recommendations | IL — вход смысла, не второй день-SoT |

---

## 10. Changelog

- **1.3.4 (2026-08-17)** — Fill-rules from corpus collisions (no schema change): Layer 2 psych slots wait later loci; element/mode are distinct descriptive systems; houses = Lilly I.7 only; `requires_action: false` = not evidenced. Do not polish existing objects to a modern average.
- **1.3.3 (2026-08-17)** — Houses 1–12 from Lilly CA I.7 (not compared to Ptolemy I.13). Major aspects from Ptolemy I.16/I.27; `requires_action` left false. Sign *objects* withheld: Layer 2 required psych slots unattested; element/mode conflicts logged. No ASC/MC/outers. No methodology change.
- **1.3.2 (2026-08-17)** — IL-1 classical seven drafts (Sun–Saturn) from Ptolemy I.4–I.7 + Lilly CA I.8–I.14. Concrete gaps: Moon/Venus temperature mismatch; Mercury native quality vs convertibility; CORE still blocked. No methodology change.
- **1.3.1 (2026-08-17)** — IL-1 started. First draft `astro.object.saturn` from Ptolemy I.4–I.5 + Lilly CA I.8 (claims ledger → normalized object). CORE not scored. No methodology change.
- **1.3 (2026-08-17)** — Swiss stays in IL runtime stack; only *licensing* is a parallel gate. IL-1 objects must map to calc-layer entities.
- **1.2 (2026-08-17)** — Sequence LOCKED IL-0…IL-4; surface-neutral IL-1; Swiss licensing out of content track; methodology freeze until first ~100 objects.
- **1.1 (2026-08-17)** — research corpus methodology; evidence_tier CORE/SUPPORTED/SCHOOL-SPECIFIC/EDITORIAL; source registry (~35 candidates); ingest = paraphrase not copy; Swiss dual-license gate; forbidden list.
- **1.0 (2026-08-17)** — ontology + schema + freeze Today content until IL-3; gold set listed; no production objects.
