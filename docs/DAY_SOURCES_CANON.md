# Day Sources Canon

**Статус:** принято (канон — единый Source of Truth для расчётных источников дня).  
**Версия:** 1.0 (2026-07-24).  
**Владелец:** Product + Engineering.

**Роль:** ответить на вопрос «из чего формируется день» — один раз, для всего движка.  
Не список фич и не промпт. Это **реестр Source Families**: что считается, откуда, чем питается, куда идёт.

**Связь:** [DAY_ENGINE_AND_COHERENCE.md](./DAY_ENGINE_AND_COHERENCE.md) · [DAYMODEL_INPUT_CONTRACT.md](./DAYMODEL_INPUT_CONTRACT.md) · [DAY_CONTEXT_V0.md](./DAY_CONTEXT_V0.md) · [ASTROLOGY_MACHINE_CONTRACT.md](./ASTROLOGY_MACHINE_CONTRACT.md) · [PRODUCT_DATA_PROVIDERS.md](./PRODUCT_DATA_PROVIDERS.md) · [PRODUCT_AVAILABILITY_MATRIX.md](./PRODUCT_AVAILABILITY_MATRIX.md) · [ONTOLOGY_AND_FOUNDATION_PHASES.md](./ONTOLOGY_AND_FOUNDATION_PHASES.md).

**Следующие артефакты (порядок жёсткий):**

1. Этот документ — **DAY_SOURCES_CANON** ✅  
2. **Day Source Registry** (код + контракт регистрации семейств)  
3. **Day Foundation** как синтез поверх Registry (без знания о системах)  
4. **Profile × Source Matrix** (какие поля профиля открывают какие семейства)

---

## 0. Три независимых слоя (не путать)

```text
Day Sources          →  детерминированные расчёты по системам
        ↓
Day Foundation       →  единый объективный контекст дня (синтез Sources)
        ↓
Day Story            →  интерпретация Foundation → экран Today
```

| Слой | Что это | Чего это **не** |
|------|---------|-----------------|
| **Day Sources** | Отдельные Source Families (астрология, Луна, нумерология, Gan-Zhi, …) | Не текст для UI |
| **Day Foundation** | Синтез **общего** характера дня из зарегистрированных Sources | Не натал, не «ваш гороскоп», не LLM-проза |
| **Day Story** | Авторская / LLM интерпретация Foundation (+ Personal) для экрана | Не источник фактов |

**Правило:** Foundation **не** импортирует знания о Панчанге, HD или Ба-цзы напрямую.  
Он получает нормализованные payload'ы от Registry. Новая система = новый Source Family + регистрация, без переписывания Foundation.

`day_foundation_v1` в коде — **временный** адаптер поверх `celestial_events` (astro + lunar). После Registry он становится **потребителем** Sources, а не владельцем системной логики. Термин канона — **Day Foundation**, не «day_foundation_v1 как онтология».

---

## 1. Пять уровней потребления (куда идут Sources)

| Уровень | Имя | Вопрос | Типичные Sources |
|---------|-----|--------|------------------|
| **L1** | Objective time context | Что объективно происходит во времени/небе? | Planetary Positions, Moon Phase/Rise, Season, Sun rise/set |
| **L2** | Shared symbolic context | Каков общий характер дня? | Aspects, Ingresses, Retro/Stations, Universal Day Number, Weekday Ruler, Planetary Hours, Panchanga, Gan-Zhi |
| **L3** | Personal context | Как день касается этого человека? | Natal Transits, Houses, Progressions, Personal Day, Dashas, BaZi, Human Design |
| **L4** | Life context | Что реально происходит в жизни? | Calendar, tasks, mood, habits, weather, journal |
| **L5** | Interactive symbolic | Что пользователь выбирает / отражает? | Tarot draw, oracle, question, synchronicity journal |

**Foundation** собирает в основном **L1 + L2** (shared).  
**Personal** активирует **L3**.  
**Today Story** может использовать L1–L5, но факты всегда traceable к Source Family.

Цепочка смысла (обязательна для Story):

```text
факт (Source)
  → значение в выбранной системе (Reference / school canon)
  → персональная активация (L3, если доступна)
  → сфера жизни
  → практическое действие
  → место в более длинном цикле
```

Без этой цепочки получается общий гороскоп. С ней — модель дня.

---

## 2. Карточка Source Family (обязательный шаблон)

Каждое семейство и каждый **подтип** (capability) описывается полями ниже.

| Поле | Смысл |
|------|--------|
| `family_id` | Стабильный slug (`western_astrology`, `moon`, `numerology`, …) |
| `capability_id` | Подтип внутри семейства (`aspects`, `phase`, `universal_day`, …) |
| `purpose` | Зачем этот источник в продукте (1–2 предложения) |
| `data_sot` | Откуда берутся **числа/факты** (эфемериды, формула, каталог, user event) |
| `required_inputs` | Минимальные входы (дата, TZ, lat/lon, birth_*, …) |
| `deterministic_outputs` | Машиночитаемые результаты (не prose) |
| `depends_on` | Другие Source Families / capabilities |
| `school_canon` | Зафиксированная школа / правило (или `TBD` до freeze) |
| `version` | `v1` / `v2` / `planned` |
| `in_foundation` | Участвует ли в Day Foundation (L1/L2) |
| `in_personal` | Участвует ли в Personal layer (L3) |
| `in_today` | Видим / используется ли на Today (через Foundation или Story) |
| `availability_gate` | Условие доступности (см. Profile Matrix) |
| `notes` | Ограничения, non-goals, маркировка (например «историческая модель») |

**Жёсткие правила:**

1. Два Source Family **не** смешивают факты в одном поле без явного synthesis step.  
2. LLM **не** является `data_sot` для позиций планет, фаз Луны, титхи, Gan-Zhi, чисел дня.  
3. Оракул / Таро / синхроничности — L5: рядом с Foundation, **не вместо** него.  
4. Пока `school_canon = TBD`, capability можно прототипировать, но **не** считать product SoT.

---

## 3. Канон школ (freeze v1)

Где продукт обязан выбрать одну школу — здесь.

| Тема | Канон v1 | Альтернативы (не смешивать в v1) |
|------|----------|-----------------------------------|
| Зодиак (западный день / foundation) | **Тропический** | Сидерический — только Vedic family |
| Узлы Луны | **True Node** | Mean Node — later / toggle |
| Система домов (personal) | **Placidus** при наличии времени+места | Whole Sign — opt-in later |
| Мажорные аспекты | 0 / 60 / 90 / 120 / 180 | Миноры — capability `minor_aspects` later |
| Луна без курса | **Placidus-style major aspects only** (conjunction, sextile, square, trine, opposition) до следующего знака | Другие наборы — не в v1 |
| Нумерология: редукция | Сохранять **11, 22** (и **33** если вышло); иначе 1–9 | «Всегда одна цифра» — не канон |
| Нумерология: Personal Year/Month/Day | Вложенная формула: PY = BD+BM+year → PM = PY+month → PD = PM+day | Другие школы — later |
| Веда: аянамша | **Lahiri** (когда Panchanga/Gocharа включатся) | Raman / KP / Fagan — later |
| Китайский день | **Civil date + local TZ** → stem-branch | Solar-term edge cases документировать при имплементации |
| Human Design | Ephemeris-based gates (когда family включится); школа — **standard HD gates** | — |
| Биоритмы | **Не ядро**; маркировать как historical model | — |
| Ангельские числа | **Не расчётный Source**; journal / L5 only | — |

Изменение строки таблицы = bump `version` затронутых capabilities + запись в changelog этого документа.

---

## 4. Архитектурный поток

```text
┌─────────────────────────────────────────────────────────────┐
│ Inputs: target_date · timezone · lat/lon · profile slice    │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ Day Source Registry                                         │
│   resolve(available families by inputs + feature flags)     │
│   run each Source Family → normalized SourceResult          │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ Day Foundation                                              │
│   merge L1+L2 SourceResults → shared day plot + essence     │
│   NO school logic here                                      │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ Personal Activation (L3)   │  Life Context (L4)             │
│   only if inputs allow     │  calendar / mood / tasks …     │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ Day Story / Today surfaces                                  │
│   interpretation · UI · optional L5 (Tarot, journal)        │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Source Families

Ниже — полный каталог. Статусы `version`:

- `v1` — в каноне и уже/скоро в Registry  
- `planned` — в каноне, реализация после Registry + Profile Matrix  
- `out_of_core` — документировано, не ядро движка дня

### 5.1 `western_astrology` — Западная астрология

**Назначение семейства:** самый насыщенный источник ежедневных небесных данных (L1/L2) и персональной активации транзитами (L3).

**Семейный `data_sot` (target):** Swiss Ephemeris / deterministic ephemeris pipeline.  
**CODE сегодня:** `celestial_events_builder` (+ related) — partial; natal facts на Profile пока через `natal_facts` LLM ([PRODUCT_DATA_PROVIDERS.md](./PRODUCT_DATA_PROVIDERS.md)) — **не** путать с Day Sky SoT.

#### 5.1.1 `planetary_positions`

| Поле | Значение |
|------|----------|
| purpose | Положения точек на выбранный момент |
| data_sot | Ephemeris |
| required_inputs | `target_datetime` (+ `lat/lon` для horizon-relative) |
| deterministic_outputs | sign, longitude°, speed, direction (D/R), latitude, declination, altitude/azimuth (если geo) |
| depends_on | — |
| school_canon | Tropic zodiac; bodies v1: Sun…Pluto; optional later: Chiron, Ceres, nodes, Lilith, Selena, Arabic parts, fixed stars |
| version | v1 (core 10 bodies) |
| in_foundation | yes |
| in_personal | yes (as transit positions) |
| in_today | yes |

#### 5.1.2 `aspects`

| Поле | Значение |
|------|----------|
| purpose | Угловые связи между телами в течение дня |
| data_sot | Derived from planetary_positions |
| required_inputs | positions timeline for day |
| deterministic_outputs | pair, aspect_type, orb, exactness, applying/separating, exact_time, duration_hint, retrograde_repeat flag |
| depends_on | `planetary_positions` |
| school_canon | Majors v1; minors planned |
| version | v1 (majors) |
| in_foundation | yes |
| in_personal | yes (sky aspects as shared; natal aspects → personal family) |
| in_today | yes |

#### 5.1.3 `ingresses`

| Поле | Значение |
|------|----------|
| purpose | Переход планеты в новый знак |
| data_sot | Ephemeris sign-change search |
| required_inputs | date range + TZ |
| deterministic_outputs | planet, from_sign, to_sign, local_time |
| depends_on | `planetary_positions` |
| school_canon | Tropic |
| version | v1 |
| in_foundation | yes |
| in_personal | no (shared) |
| in_today | yes |

#### 5.1.4 `retrogrades_and_stations`

| Поле | Значение |
|------|----------|
| purpose | Ретроградность, станции, тень, повтор градуса |
| data_sot | Ephemeris speed / station detection |
| required_inputs | date (+ lookback/forward window) |
| deterministic_outputs | planet, state (retro/direct), station_type, station_time, shadow_window |
| depends_on | `planetary_positions` |
| school_canon | Station as distinct event when speed ≈ 0 |
| version | v1 |
| in_foundation | yes |
| in_personal | soft background |
| in_today | yes |

#### 5.1.5 `solar_proximity` (combustion / cazimi / under beams / heliacal)

| Поле | Значение |
|------|----------|
| purpose | Традиционные состояния близости к Солнцу и видимости |
| data_sot | Ephemeris + heliacal helpers |
| required_inputs | positions; geo for heliacal |
| deterministic_outputs | flags + orb; heliacal event times |
| depends_on | `planetary_positions` |
| school_canon | TBD traditional orbs (freeze before ship) |
| version | planned |
| in_foundation | optional later |
| in_personal | elective / traditional |
| in_today | later |

#### 5.1.6 `lunar_nodes_sky`

| Поле | Значение |
|------|----------|
| purpose | Положение узлов, аспекты к узлам, близость сезона затмений |
| data_sot | Ephemeris True Node (v1) |
| required_inputs | datetime |
| deterministic_outputs | node longitudes, signs, aspects_to_nodes, eclipse_season_proximity |
| depends_on | `planetary_positions`, `eclipses` |
| school_canon | True Node |
| version | planned (partial may exist in celestial) |
| in_foundation | yes when ready |
| in_personal | yes (to natal) |
| in_today | yes when ready |

#### 5.1.7 `eclipses`

| Поле | Значение |
|------|----------|
| purpose | Солнечные/лунные затмения как событийный контекст |
| data_sot | Ephemeris eclipse functions |
| required_inputs | date window; geo for visibility |
| deterministic_outputs | type, exact_time, sign/degree, visibility, pre/post window |
| depends_on | — |
| school_canon | Astronomical eclipse classification |
| version | planned |
| in_foundation | yes (when in window) |
| in_personal | yes (to natal points) |
| in_today | yes |

#### 5.1.8 `seasonal_solar_points`

| Поле | Значение |
|------|----------|
| purpose | Равноденствия, солнцестояния, смена знака Солнца |
| data_sot | Ephemeris / seasonal calculator |
| required_inputs | date + TZ |
| deterministic_outputs | season_point events, sun_sign ingress |
| depends_on | `ingresses` (sun) |
| school_canon | Tropic seasons |
| version | v1 (sun ingress already); equinox/solstice planned explicit |
| in_foundation | yes |
| in_personal | no |
| in_today | yes |

---

### 5.2 `moon` — Лунный контекст

**Назначение:** быстрый суточный ритм; часто отдельный слой даже при наличии western_astrology.

#### 5.2.1 `phase`

| Поле | Значение |
|------|----------|
| purpose | Фаза, освещённость, возраст Луны |
| data_sot | Sun–Moon elongation / ephemeris (NASA-compatible metrics) |
| required_inputs | datetime |
| deterministic_outputs | phase_id (8-fold), elongation°, illumination%, age_days, waxing/waning, days_to_quarter |
| depends_on | `western_astrology.planetary_positions` (Sun, Moon) |
| school_canon | 8 named phases |
| version | v1 |
| in_foundation | yes |
| in_personal | no |
| in_today | yes |

#### 5.2.2 `sign`

| Поле | Значение |
|------|----------|
| purpose | Знак Луны → эмоциональный/бытовой тон дня |
| data_sot | Moon longitude → tropic sign |
| required_inputs | datetime |
| deterministic_outputs | sign, degree, ingress_time if today |
| depends_on | positions |
| school_canon | Tropic |
| version | v1 |
| in_foundation | yes |
| in_personal | soft (vs natal moon later) |
| in_today | yes |

#### 5.2.3 `lunar_aspects`

| Поле | Значение |
|------|----------|
| purpose | Таймлайн дня по быстрым аспектам Луны |
| data_sot | Aspect search Moon→planets |
| required_inputs | day window + TZ |
| deterministic_outputs | timed aspect list (applying/exact/separating) |
| depends_on | `aspects` |
| school_canon | Majors v1 |
| version | v1 |
| in_foundation | yes |
| in_personal | no (shared timeline) |
| in_today | yes |

#### 5.2.4 `void_of_course`

| Поле | Значение |
|------|----------|
| purpose | Интервал после последнего мажорного аспекта Луны до смены знака |
| data_sot | Derived from lunar_aspects + moon ingress |
| required_inputs | day window |
| deterministic_outputs | voc_start, voc_end, rule_id |
| depends_on | `lunar_aspects`, `sign` |
| school_canon | Majors-only (see §3) |
| version | v1 (timeline via timed_lunar_aspects; unavailable without ingress+aspects) |
| in_foundation | yes when ready |
| in_personal | elective |
| in_today | yes when ready |

#### 5.2.5 `lunar_day`

| Поле | Значение |
|------|----------|
| purpose | 29/30 «лунных суток» (традиция ВЕ) |
| data_sot | School-specific (sunrise-of-moon **or** from new moon) |
| required_inputs | date + geo (если от восхода) |
| deterministic_outputs | lunar_day_number, method_id |
| depends_on | moon rise / phase |
| school_canon | TBD — **не универсальный стандарт**; freeze method before ship |
| version | planned |
| in_foundation | optional |
| in_personal | no |
| in_today | optional |

#### 5.2.6 `moon_rise_set_culmination`

| Поле | Значение |
|------|----------|
| purpose | Локальная видимость Луны |
| data_sot | Ephemeris rise/set |
| required_inputs | date + lat/lon + TZ |
| deterministic_outputs | rise, set, culmination, altitude, azimuth, visibility_duration |
| depends_on | — |
| school_canon | Astronomical |
| version | planned |
| in_foundation | yes (L1) when geo present |
| in_personal | no |
| in_today | yes when geo |

#### 5.2.7 `perigee_apogee`

| Поле | Значение |
|------|----------|
| purpose | Расстояние Луны; супер/микролуние около фаз |
| data_sot | Ephemeris distance extrema |
| required_inputs | date window |
| deterministic_outputs | distance_km, event flags near full/new |
| depends_on | `phase` |
| school_canon | Astronomical distances |
| version | planned |
| in_foundation | soft |
| in_personal | no |
| in_today | optional |

#### 5.2.8 `declination_oob`

| Поле | Значение |
|------|----------|
| purpose | Склонение, параллели, Moon out of bounds |
| data_sot | Ephemeris declination |
| required_inputs | datetime |
| deterministic_outputs | declination, OOB flag, parallels |
| depends_on | positions |
| school_canon | OOB = beyond max solar declination |
| version | planned (specialist) |
| in_foundation | no (v1) |
| in_personal | specialist |
| in_today | later |

---

### 5.3 `personal_astrology` — Персональная астрология дня

**Назначение:** сопоставление текущего неба с наталом (L3). Не часть shared Foundation.

#### Capabilities (сводка)

| capability_id | version | required_inputs | in_foundation | in_personal | in_today |
|---------------|---------|-----------------|---------------|-------------|----------|
| `natal_transits` | v1/partial | birth chart + sky | no | yes | yes |
| `transits_by_house` | planned | birth **time+place** | no | yes | yes |
| `house_rulers_chains` | planned | time+place | no | yes | later |
| `secondary_progressions` | planned | birth datetime+place | no | yes | soft background |
| `solar_arc` | planned | birth | no | yes | soft |
| `solar_return` / `lunar_return` | planned | birth | no | yes | period context |
| `profections` | planned | birth date (+time for day/month) | no | yes | soft |
| `time_lords` (firdaria, ZR, …) | planned | birth | no | yes | later |
| `planet_returns` | planned | birth | no | yes | event |

**school_canon:** Placidus houses when time+place; without birth time — **no houses/angles/progressed angles**.

---

### 5.4 `electional_horary` — Электив / хорар

| Поле | Значение |
|------|----------|
| purpose | Выбор времени / карта вопроса |
| data_sot | Ephemeris chart for elected or question moment |
| required_inputs | datetime + place; question for horary |
| deterministic_outputs | chart factors (ASC, Moon applications, dignities, VOC, …) |
| school_canon | Traditional elective checklist TBD |
| version | planned |
| in_foundation | **no** |
| in_personal | situational |
| in_today | only on explicit user request |

---

### 5.5 `numerology` — Нумерология дня

#### 5.5.1 `universal_day`

| Поле | Значение |
|------|----------|
| purpose | Коллективное число календарной даты |
| data_sot | Digit sum of YYYY-MM-DD (local civil date) |
| required_inputs | `target_date` |
| deterministic_outputs | `universal_day` ∈ {1–9, 11, 22, 33?} |
| depends_on | — |
| school_canon | Keep 11/22/(33); else reduce 1–9 (§3) |
| version | v1 |
| in_foundation | yes |
| in_personal | no |
| in_today | yes |

#### 5.5.2 `personal_year` / `personal_month` / `personal_day`

| Поле | Значение |
|------|----------|
| purpose | Вложенные персональные циклы |
| data_sot | PY = birth_day + birth_month + year digits; PM = PY + month; PD = PM + day |
| required_inputs | birth_date + target_date |
| deterministic_outputs | PY, PM, PD (+ master handling) |
| depends_on | — |
| school_canon | Nested formula (§3) |
| version | v1 |
| in_foundation | **no** (personal) |
| in_personal | yes |
| in_today | yes |

#### 5.5.3 `calendar_day_number`

| Поле | Значение |
|------|----------|
| purpose | Число дня месяца (1–31 → reduce) |
| data_sot | day-of-month reduction |
| required_inputs | target_date |
| deterministic_outputs | `dom_number` |
| version | planned |
| in_foundation | soft |
| in_personal | no |
| in_today | optional |

#### 5.5.4 `pinnacles_challenges_cycles`

| Поле | Значение |
|------|----------|
| purpose | Длинные персональные циклы как фон |
| required_inputs | birth_date |
| version | planned |
| in_foundation | no |
| in_personal | yes |
| in_today | soft background |

#### 5.5.5 `name_numbers`

| Поле | Значение |
|------|----------|
| purpose | Expression / soul / personality from name |
| required_inputs | name + alphabet canon |
| school_canon | TBD — multilingual transliteration must be frozen before ship |
| version | planned |
| in_foundation | no |
| in_personal | yes |
| in_today | optional |

**Правило продукта:** Universal и Personal day **хранить раздельно** — общий фон vs как человек входит в день.

---

### 5.6 `vedic_panchanga` — Ведическая астрология / Панчанга

| capability_id | purpose | required_inputs | version | in_foundation | in_personal | in_today |
|---------------|---------|-----------------|---------|---------------|-------------|----------|
| `tithi` | 30 lunar days from Sun–Moon angle | datetime | v1 | yes | no | yes |
| `nakshatra` | 27 lunar mansion of Moon | datetime | v1 | yes | soft | yes |
| `yoga` | 27 yogas from Sun+Moon | datetime | v1 | yes | no | yes |
| `karana` | half-tithi | datetime | v1 | yes | no | yes |
| `vara` | weekday planetary ruler | date + TZ | v1 | yes | no | yes |
| `muhurta_intervals` | Rahu Kala, Yamaganda, … | geo + sunrise | v1 | soft | elective | yes |
| `gochara` | Vedic transits vs natal Moon/Lagna | natal + sky | planned | no | yes | yes |
| `dasha` | Vimshottari periods | birth | planned | no | yes | soft |
| `ayanamsha` | Sidereal offset | — (config) | v1 Lahiri | config | config | — |

**school_canon:** Lahiri ayanamsha (§3). Sidereal only inside this family — не подменять tropic Foundation.

---

### 5.7 `chinese_metaphysics` — Китайская метафизика / альманах

| capability_id | purpose | required_inputs | version | in_foundation | in_personal | in_today |
|---------------|---------|-----------------|---------|---------------|-------------|----------|
| `gan_zhi_day` | Stem–branch day pillar | date + TZ | v1 | yes | no | yes |
| `five_elements_day` | Element + Yin/Yang of pillar | gan_zhi | v1 | yes | no | yes |
| `jianchu_officer` | 12 day officers | date cycle | v1 | yes | no | yes |
| `almanac_actions` | Auspicious / inauspicious lists | day factors | v1 soft via Jianchu | soft | elective | yes |
| `clashes` | Animal clash etc. | birth animal + day | planned | no | yes | yes |
| `lucky_hours_directions` | Hours / directions / Tai Sui | date + geo rules | planned | soft | yes | yes |
| `solar_terms` | 24 jieqi | sun longitude | v1 | yes | no | yes |
| `bazi` | Four pillars vs day pillar | birth datetime+place | planned | no | yes | yes |

---

### 5.8 `tarot_oracle` — Таро / оракул

| Поле | Значение |
|------|----------|
| purpose | Интерактивный символический слой (L5) |
| data_sot | Random / user draw + deck + orientation + spread |
| required_inputs | draw event (не календарь) |
| deterministic_outputs | card_ids, positions, orientation |
| school_canon | Deck + spread contracts (Reference Tarot) |
| version | v1 (card of day exists as product ritual) |
| in_foundation | **no** |
| in_personal | contextual |
| in_today | yes — **alongside**, never replacing calculated context |

---

### 5.9 `human_design` — Human Design

| Поле | Значение |
|------|----------|
| purpose | Транзиты по 64 воротам; соединение с бодиграфом |
| data_sot | Ephemeris → HD gates/lines |
| required_inputs | datetime; personal: birth datetime+place |
| deterministic_outputs | gate activations, channels, defined centers (transit) |
| school_canon | Standard HD gate mapping |
| version | planned |
| in_foundation | soft (transit sky only) |
| in_personal | yes |
| in_today | later |

---

### 5.10 `mayan_calendars`

| capability_id | notes | version | in_foundation |
|---------------|-------|---------|---------------|
| `tzolkin_haab` | Historical count — separate from Dreamspell | planned | soft |
| `dreamspell` | Argüelles system — **different family capability**, never merge ids | planned | soft |

---

### 5.11 `kabbalah_letter` — Каббалистические / буквенно-числовые

| Поле | Значение |
|------|----------|
| version | planned / school-dependent |
| in_foundation | no (v1) |
| notes | Strong school/religion variance — freeze before any Today wiring |

---

### 5.12 `planetary_hours`

| Поле | Значение |
|------|----------|
| purpose | 24 unequal planetary hours (Chaldean order) |
| data_sot | Local sunrise/sunset → 12 day + 12 night hours |
| required_inputs | date + lat/lon + TZ |
| deterministic_outputs | hour table: start/end, ruler |
| depends_on | `seasonal_calendar.sun_rise_set` |
| school_canon | Chaldean order from day ruler |
| version | v1 (NOAA-approx sunrise/sunset in backend; Swiss rise_trans later) |
| in_foundation | yes (L2) when geo |
| in_personal | elective |
| in_today | yes when geo |

---

### 5.13 `weekday_ruler`

| Поле | Значение |
|------|----------|
| purpose | Планетарный управитель дня недели |
| data_sot | Civil weekday → planet |
| required_inputs | `target_date` + TZ (civil) |
| deterministic_outputs | weekday, ruler_planet |
| school_canon | Mon Moon … Sun Sunday (shared traditional table) |
| version | v1 |
| in_foundation | yes |
| in_personal | no |
| in_today | yes |

---

### 5.14 `seasonal_calendar` — Сезонный / гражданский контекст

| capability_id | purpose | required_inputs | version | in_foundation | in_today |
|---------------|---------|-----------------|---------|---------------|----------|
| `season` | Season of year | date + hemisphere | v1/partial | yes | yes |
| `sun_rise_set` | Sunrise/sunset, day length | geo + date | v1 | yes | yes |
| `dst_calendar` | DST transitions | TZ | planned | soft | soft |
| `holidays` | Civil/religious holidays | locale + date | planned | soft | soft |

Не эзотерика сами по себе, но L1-ориентация во времени.

---

### 5.15 `biorhythms` — out_of_core

| Поле | Значение |
|------|----------|
| purpose | 23/28/33-day cycles from birth |
| version | out_of_core |
| in_foundation | **no** |
| notes | Historical popular model; **no scientific forecasting basis** — label if ever exposed |

---

### 5.16 `synchronicity_journal` — out_of_core / L5

| Поле | Значение |
|------|----------|
| purpose | Повторяющиеся числа/совпадения после наблюдения пользователя |
| data_sot | User observation events |
| in_foundation | **no** |
| in_today | journal only |

---

### 5.17 `life_context` — Реальные данные пользователя (L4)

| capability_id | examples | privacy |
|---------------|----------|---------|
| `calendar_tasks` | events, unfinished tasks | high |
| `checkins` | mood, energy, sleep | high |
| `habits_cycles` | habits, cycle | sensitive |
| `geo_weather` | location, weather | permissioned |
| `relationships_workload` | user notes | high |

Не эзотерическая система; делает день practically useful. Отдельные privacy/medical rules. Не подменяет Source Families 5.1–5.14.

---

## 6. Что меняется ежедневно vs фон

**Ежедневно / внутри суток:** Moon position/sign/aspects/phase, VOC, lunar day, moon rise/set, fast aspects, exactness of slow aspects, planetary hours, universal & personal day numbers, Panchanga, Gan-Zhi, Chinese hours, HD transits, user calendar events.

**Медленный фон:** retro cycles, slow planet transits, progressions, solar return, profections, personal year/month, dashas, BaZi luck pillars, season, long-term goals.

Foundation подчёркивает **дневное**; Story может ссылаться на фон, не подменяя дневной сюжет фоном.

---

## 7. Три продуктовых вопроса (закрывающий тест)

Любая фича Today должна явно отвечать, **какой** вопрос она закрывает:

1. **Каков общий характер этого дня?** → L1/L2 Sources → Foundation  
2. **Как день взаимодействует с человеком?** → L3 Personal (+ Profile Matrix gates)  
3. **Как использовать день на практике?** → L4 Life + actionable Story (+ elective L5)

Если фича не traceable к Source Family из этого документа — она не часть Day Engine.

---

## 8. Карта реализации (после этого канона)

| Шаг | Артефакт | DoD |
|-----|----------|-----|
| 1 | **DAY_SOURCES_CANON** (этот файл) | Семьи описаны; школы §3; слои §0 |
| 2 | **Day Source Registry** | `family_id` → provider; `SourceResult` schema; resolve-by-inputs |
| 3 | **Day Foundation refactor** | Читает только Registry; celestial_events → adapters |
| 4 | **Profile × Source Matrix** | birth date/time/place/geo → available families |
| 5 | Enable planned families | Panchanga, Gan-Zhi, Hours, VOC, … one family at a time |

---

## 9. Changelog

| Дата | Версия | Изменение |
|------|--------|-----------|
| 2026-07-24 | 1.0 | Первый канон: слои Sources → Foundation → Story; каталог семейств; freeze школ v1 |
