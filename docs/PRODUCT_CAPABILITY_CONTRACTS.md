# Product Capability Contracts

**Статус:** TARGET DRAFT — **контракты ответа API по уровню данных**  
**Роль:** сначала уровни доступных данных и контракт ответа; Profile / Today / Compatibility **потребляют** один структурированный результат.  
**Связь:** [PRODUCT_GENERATION_CONTRACTS.md](./PRODUCT_GENERATION_CONTRACTS.md) (**ядро: контракты генерации**) · [PRODUCT_DATA_PROVIDERS.md](./PRODUCT_DATA_PROVIDERS.md) · [PRODUCT_AVAILABILITY_MATRIX.md](./PRODUCT_AVAILABILITY_MATRIX.md) · [PRODUCT_DATA_INTAKE.md](./PRODUCT_DATA_INTAKE.md) · Explainable Computation  



**Отличие от** [ASTROLOGY_MACHINE_CONTRACT.md](./ASTROLOGY_MACHINE_CONTRACT.md): AMC описывает внутренний Machine Layer / reference. Этот документ — **продуктовый оркестратор**: что запрашиваем, при каких данных, что LLM имеет право писать.

---

## Главный сдвиг (MVP)

```text
❌ «Как написать промпт профиля?»
❌ «Мы считаем астрологию внутри TodayFlow»

✅ «Какой уровень данных → какой контракт ответа?»
✅ TodayFlow = оркестратор: ввод → capabilities → внешний API / каталог → сохранение → интерпретация
```

| Роль | Кто | Что делает |
|------|-----|------------|
| **Солнце / Луна / планеты / углы / дома / аспекты** | **LLM structured facts** (DeepSeek V4 Pro) — [PRODUCT_DATA_PROVIDERS](./PRODUCT_DATA_PROVIDERS.md) | JSON `NatalChartFacts`; **без** отдельного астро-сервиса |
| **География** | Тонкий geocode (MVP); mega-БД later | City → lat/lon/TZ если есть |
| **Справочные соответствия** | Каталог (опционально) | По ключам из facts |
| **Описание и инсайты** | LLM (следующие промпты) | Только из уже сохранённых facts |

**Разделение ролей LLM:**

1. **Fact prompt** — единственный шаг, который **имеет право** вернуть положения планет / ASC / дома (по контракту, в JSON).  
2. **Interpretation prompts** — **запрещено** пересчитывать или угадывать карту; только `calculated_facts`; missing → `null`.

Не строить лишние calc-сервисы для MVP.

---

## Пайплайн

```text
Пользователь
  → ввод данных (PRODUCT_DATA_INTAKE)
  → Capability Resolver: что есть / чего нет
  → запрос L1 / L2 к внешнему API + каталогу
  → structured facts → сохранение в профиле
  → Generation Contracts (интерпретация только по Allowed output / Output Schema)
  → Profile / Today / Compatibility / Tarot читают готовый пакет
```

---

## Capability Resolver

| Есть | Запросить | Не запрашивать |
|------|-----------|----------------|
| дата | L1 базовый профиль | ASC, дома, MC/IC, планеты в домах |
| дата + имя | L1 + name numerology fields | — |
| дата + время + место | L1 + L2 полная натальная структура | — |
| дата + время, **без** места | L1; время **не** использовать для домов | L2 angles/houses |
| дата + место, без времени | L1; место сохранить | L2; не имитировать точность |
| нет даты | ничего персонального | весь L1–L3 |

Resolver формирует **четыре блока** каждого запроса (ниже). Неполный ввод → исключаем поля из запроса, а не угадываем.

---

## Четыре блока каждого API-запроса

Каждый вызов (L1 / L2 / L3) несёт:

### 1. `available_input`

Что пользователь реально указал:

```json
{
  "display_name": "string|null",
  "name_language": "string|null",
  "name_variant": "full|short|birth|current|null",
  "birth_date": "YYYY-MM-DD",
  "birth_time": "HH:MM|null",
  "birth_time_known": true,
  "birth_place": "string|null",
  "latitude": "number|null",
  "longitude": "number|null",
  "timezone_at_birth": "IANA|null"
}
```

### 2. `calculated_facts`

Только надёжно полученные факты (от внешнего API / каталога / уже сохранённого L1).  
Каждый факт: `{ "id", "key", "value", "source", "confidence" }`.

### 3. `unavailable_facts`

```json
{
  "ascendant": { "status": "unavailable", "reason": "birth_time_missing" },
  "houses": { "status": "unavailable", "reason": "birth_place_missing" },
  "name_numerology": { "status": "unavailable", "reason": "name_missing" }
}
```

### 4. `allowed_output`

Явный список полей, которые **разрешено** заполнить на этом шаге.  
Всё остальное — omit / null. Инструкция оркестратора:

> Используй только `calculated_facts`. Не восстанавливай отсутствующие значения. Не выводи ASC/дома/связанное, если их нет в `calculated_facts`.

---

## Слой 1 — Базовый профиль (`capability: base_profile`)

### Вход

| Поле | Роль |
|------|------|
| `birth_date` | **минимум** |
| `display_name` + язык/вариант имени | расширяет; не обязательно |

### Что должно быть в `calculated_facts` до LLM (источник: внешний API + каталог)

**По дате:**

- `sun_sign`, `sun_element`, `sun_modality`, `sun_ruling_planet`, `sun_polarity`
- `life_path_number`, `birthday_number` (+ другие date numbers, если в каноне)
- `personal_year` / `personal_month` / `personal_day` — если известна `as_of` дата
- каталог по ключу знака/числа: `stones`, `colors`, `plants`, `cultural_images`, `mythic_correspondences`, `tradition_notes`

**По имени (только если имя есть):**

- `expression_number`, `soul_urge_number`, `personality_number` (+ другие — только из утверждённого нумерологического канона)

### `allowed_output` (L1 interpretation / presentation)

| Поле | Условие |
|------|---------|
| `identity_summary` | всегда при L1 |
| `sun_sign_meaning` | sun_sign in facts |
| `element_expression` | element in facts |
| `numerology_core` | life_path (и др. date numbers) in facts |
| `name_expression` | name numbers in facts |
| `cultural_associations` | catalog keys present |
| `strengths_from_available_facts` | только из facts |
| `possible_tensions_from_available_facts` | только из facts |
| `limitations` | всегда — что недоступно и почему |
| `confidence` | всегда |
| `missing_capabilities` | всегда |

**Запрещено в L1:** ASC, дома, MC/IC, планеты в домах, house-based сферы, выводы «как будто» имя было.

### Пользователь

> Этот базовый разбор построен по дате рождения. Добавьте полное имя, чтобы открыть нумерологию имени…

---

## Слой 2 — Полная натальная структура (`capability: full_natal`)

### Вход (все три)

- `birth_date`
- `birth_time` + `birth_time_known=true`
- `birth_place` + координаты / TZ

Без места при известном времени → **не** запрашивать L2 angles/houses; показать CTA места.

### `calculated_facts` (внешний астро-API)

- точные положения планет; Луна; ретроградность  
- Ascendant; MC; IC; Descendant  
- дома; планеты в домах; управители домов  
- аспекты + орбисы; конфигурации  
- преобладание стихий/модальностей  
- `confidence` / reliability per fact  

Плюс пакет L1 (можно дополнить запрос фактами из ответа L1).

### `allowed_output` (структурная интерпретация)

| Поле | Основание (примеры) |
|------|---------------------|
| `outer_expression` | ASC, 1st house |
| `emotional_structure` | Moon sign/house, water emphasis |
| `decision_style` | Mars, Mercury, modalities |
| `relationship_style` | Venus, 7th, DSC |
| `work_and_realization` | MC, 10th, Saturn |
| `money_patterns` | 2nd/8th, Venus |
| `home_and_security` | IC, 4th, Moon |
| `communication_style` | Mercury, 3rd |
| `core_strengths` | dominants, harmonious aspects |
| `internal_tensions` | hard aspects, element clash |
| `growth_zones` | Saturn, squares, 12th… |
| `chart_dominants` | calculated |
| `important_aspects` | calculated list |
| `limitations` | всегда |

Каждый вывод **обязан** ссылаться на `source_fact_ids` (например `moon_in_cancer`, `mars_square_saturn`).

### Если нет времени

В `unavailable_facts`: `ascendant`, `houses`, `mc`, `ic`, `dsc`, `planets_in_houses`, `house_rulers`, `house_transits` — reason `birth_time_missing`.  
В `allowed_output` этих полей **нет**. Надёжные noon/date-only факты — только если внешний API явно пометил их как reliable без времени.

### Если есть время, нет места

Не использовать время для полного расчёта.  
`unavailable_facts.houses/ascendant.reason = birth_place_missing`.  
CTA: место нужно для координат и TZ.

---

## Слой 3 — Персональный разбор и польза (`capability: personal_insight`)

**Вход:** не сырые birth fields, а готовый пакет:

- L1 facts + L1 allowed fields (если есть)  
- L2 facts + structural fields (если capability есть)  
- confirmed user answers (если есть)  
- `unavailable_facts`  
- provenance  

### `allowed_output` (конкретные разделы)

| Раздел | Поля (минимум) |
|--------|----------------|
| Восприятие мира | `attention_focus`, `information_processing`, `situation_clarity_helps` |
| Решения | `decision_normal_mode`, `decision_confidence`, `decision_delay_or_error` |
| Эмоции | `safety_need`, `emotion_expression`, `emotion_protection` |
| Отношения | `closeness_need`, `attachment_style`, `repeating_friction` |
| Работа | `work_conditions`, `strength_expression`, `career_risks` |
| Напряжения | `conflicting_needs`, `behavior_manifestation`, `basis_fact_ids` |
| Что помогает | `helps[]` — только следствие уже сформированных выводов |

### Жёсткий след каждого текстового вывода

```json
{
  "claim": "string",
  "source_fact_ids": ["fact_id", "..."],
  "confidence": "high|medium|low",
  "availability": "available|partial|unavailable",
  "missing_data_effect": "string|null",
  "generation_method": "llm|template|omit"
}
```

Недостаточно оснований → поле пустое · раздел не показывается · CTA какие данные откроют.

---

## Пользовательский принцип (UI)

Профиль всегда показывает три вещи:

1. **Что определили**  
2. **На каких данных**  
3. **Что откроется** после дополнения  

Пример:

> Сейчас профиль построен по имени и дате рождения.  
> Доступны базовая астрология и нумерология.  
> Добавьте время и место рождения, чтобы открыть Асцендент, дома, карьерную ось, сферу отношений и более точное описание эмоциональных реакций.

---

## Сохранение

После каждого успешного слоя:

| Сохранить | Куда |
|-----------|------|
| `available_input` | профиль (введённые данные) |
| `calculated_facts` + `unavailable_facts` | профиль (рассчитанный слой) |
| L1/L2/L3 response packages | артефакты разбора (versioned) |

Today / Compatibility / Tarot **не** пересчитывают астрологию — читают сохранённый пакет профиля (+ day overlay отдельно, когда будет).

---

## Open decisions (блокируют wiring)

1. **Провайдер natal / L2:** см. [PRODUCT_DATA_PROVIDERS.md](./PRODUCT_DATA_PROVIDERS.md) — выбор вендора + adapter.  
2. **География:** ETL GeoNames-scale local DB (не список в git).  
3. **Нумерология:** внешний сервис vs наш канон (Pythagorean) — только один SoT.  
4. **Каталог соответствий:** ключи знак/число → камень/цвет/…  
5. **Legacy Swiss:** fallback при outage или cutover-only.  
6. **L3 доступ:** Free preview vs Trial (Availability Matrix).

---

## Code Δ (срез 2026-07-22)

| TARGET | CODE |
|--------|------|
| Оркестратор → внешний API | Локальный `AstroEngine` (Swiss) + свой numerology |
| Capability Resolver → allowed_output | Частично: `time_unknown` strip houses; нет единого resolver-контракта |
| L1/L2/L3 раздельные пакеты | Profile funnel LLM шаги + read-path projections; смешение ролей |
| LLM только из facts | Промпты получают контекст; нет жёсткого `allowed_output` / `unavailable_facts` пакета |
| Единый пакет для Today/Compat | Параллельные пути и ephemeral compat birth data |

---

## Порядок после APPROVED

1. Выбрать провайдера (Open decision 1–2).  
2. Зафиксировать JSON Schema для L1 / L2 / L3 response (+ четыре блока запроса).  
3. Реализовать Capability Resolver (pure function: input → capabilities + request bodies).  
4. Persist facts на профиле.  
5. Перевести Profile UI на чтение пакетов (без новых «промптов ради промптов»).  
6. Compat / Today — consumers того же пакета.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-22 | v0.1 DRAFT — оркестратор; resolver; L1/L2/L3 contracts; four request blocks; claim provenance |
