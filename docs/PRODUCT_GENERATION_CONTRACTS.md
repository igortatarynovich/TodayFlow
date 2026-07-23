# Product Generation Contracts

**Статус:** TARGET DRAFT — **контракты генерации** · Profile UI slots **APPROVED** в [PRODUCT_AVAILABILITY_MATRIX.md](./PRODUCT_AVAILABILITY_MATRIX.md) §3.1  
**Роль:** два связанных актива — **Contract** (продуктовая спецификация) и **Implementations** (промпты под модели = IP).  
**Связь:** [PRODUCT_AVAILABILITY_MATRIX.md](./PRODUCT_AVAILABILITY_MATRIX.md) (**gate экрана**) · [PRODUCT_CAPABILITY_CONTRACTS.md](./PRODUCT_CAPABILITY_CONTRACTS.md) · [PRODUCT_DATA_PROVIDERS.md](./PRODUCT_DATA_PROVIDERS.md) · Voice · Explainable Computation  
**Код:** `prompts/registry_v1.py` хранит implementations · [PRODUCT_PROMPT_LIBRARY.md](./PRODUCT_PROMPT_LIBRARY.md) = pointer сюда

---

## Два актива (не «промпт вторичен»)

| Актив | Что фиксирует | Меняется когда |
|-------|----------------|----------------|
| **Contract** | *Что* должно произойти: схемы, зависимости, execution/quality rules | Меняется продуктовая спецификация поля / правила |
| **Implementations** | *Как* конкретная модель этого добивается: тексты промптов, параметры | Новая модель, A/B промпта, тюнинг под DeepSeek / GPT / Claude / Gemini / local |

Промпты — **ключевой IP** TodayFlow, но не единственный источник логики.  
Логика продукта живёт в Contract; мастерство формулировок — в Implementations.

Через год: новый промпт или другая модель → тот же Contract.  
Несколько implementations одного контракта могут сосуществовать (выбор по модели / locale / experiment).

```text
Capability / facts on profile
        ↓
Contract (schemas · deps · execution rules · quality rules)
        ↓
Select Implementation (e.g. deepseek-v4-pro)
        ↓
Validate Output Schema + Quality Rules
        ↓
Persist → UI / Today / Compat / Tarot
```

---

## Два качественных промпта Profile (не смешивать)

Качество результата = **качество промпта под свою роль**. Две разные работы, два разных Implementation:

| Шаг | Contract | Промпт должен уметь | Вход | Выход | Запрет |
|-----|----------|---------------------|------|-------|--------|
| **1. Facts** | `natal_facts` | Точно собрать карту: Солнце, Луна, планеты, спутники/узлы (если в схеме), ASC, углы, дома, аспекты… | `available_input` (+ catalog keys где уместно) | validated JSON facts + `unavailable_facts` | Писать «кто ты» / советы / инсайты |
| **2. Interpretation** | `personality` (+ `natal_chart` / `name_numerology` / `growth`…) | Из **уже полученных** facts сделать описание, рекомендации, инсайты, слоты шапки и тела | `calculated_facts` + `unavailable_facts` (+ catalog) | поля слотов 3.1 | Пересчитывать ASC/дома/планеты; угадывать missing |

```text
правильный fact-prompt  →  надёжные natal_facts
        ↓
правильный interpretation-prompt  →  описание · инсайты · рекомендации
```

- Без сильного **fact**-промпта интерпретация стоит на песке.  
- Без сильного **interpretation**-промпта факты не становятся продуктом для человека.  
- Справочник (знак по дате, год в культурах) **не** заменяет fact-prompt для углов/домов и **не** входит в interpretation как «переспрос модели».  
- Один «напиши весь профиль» промпт — **антипаттерн**: смешивает роли и ломает explainability.

### Глубина доступа и промпты

Качественные fact + interpretation промпты строят **полный** пакет по данным. Глубина **показа** — отдельно:

| Момент | Access | Fact prompt | Interpretation prompt | UI |
|--------|--------|-------------|----------------------|-----|
| До регистрации | Guest | Можно для preview (rate-limited) | Preview-слоты / укороченный surface | Нет полного `/profile` |
| После регистрации | Free | Полный по `available_input` | Полный по facts (L3 **в результате**) | Reveal L1+L2; L3 gated |
| После подписки / trial | Trial / Paid | Тот же facts SoT (не пересчёт ради тарифа) | Тот же результат | Reveal L1+L2+L3 |

Не делать: отдельный «free prompt» и «paid prompt», которые по-разному **сочиняют** человека.  
Делать: один качественный interpretation → `revealed_slots` по access.

CODE: fact Implementation = `profile.natal_facts.v1`. Interpretation — целевые `personality` / related; legacy `profile.identity|styles|patterns` = temporary Δ до wiring по 3.1.

---

## Структура одной записи

```text
Personality
├── Contract
│   ├── Input Schema
│   ├── Output Schema
│   ├── Dependencies          # requires / optional
│   ├── Execution Rules       # что использовать / запреты / null / tools
│   └── Quality Rules         # факты, повтор, категоричность, Voice…
│
└── Implementations
    ├── deepseek-v4-pro       # текущий MVP
    ├── gpt-…
    ├── claude-…
    ├── gemini-…
    └── local-llm-…
```

### Contract

| Часть | Содержание |
|-------|------------|
| **Input Schema** | Ключи из `available_input` + `calculated_facts` (+ packs). Типы, обязательность. |
| **Output Schema** | Поля результата, типы, nullable. |
| **Dependencies** | `requires` / `optional` — граф, не порядковый номер. |
| **Execution Rules** | Какие факты можно использовать; чего не делать; когда `null` / skip / не вызывать контракт; какие tools допустимы (если появятся). Эволюция **независимо** от quality. |
| **Quality Rules** | Не противоречить фактам; не повторяться; не опираться на unavailable; не делать категоричных выводов без оснований; Voice; формат полей. Эволюция **независимо** от execution. |

### Implementations

| Часть | Содержание |
|-------|------------|
| **Prompt (+ params)** | System/user templates, temperature, max_tokens, model id — под конкретный executor. Версионируется (`implementation_id` + `version`). |
| **Binding** | `contract_id` + `model_family` (+ locale). Несколько bindings на один Contract. |

Дополнительно для ship:

| Поле | Смысл |
|------|--------|
| `contract_id` | стабильный id (напр. `personality`) |
| `capability_gate` | Availability / Capability Resolver |
| `default_implementation` | какой binding в production (сейчас DeepSeek V4 Pro) |

---

## Зависимости = граф, не порядок «01…12»

Номера семейств — только удобные ярлыки в документации.  
**Источник истины порядка запуска — `requires` / `optional`.**

Пример:

```yaml
contract_id: personality
requires:
  - base_astrology_facts   # или natal_facts, если объединён MVP fact-step
optional:
  - name_numerology
  - natal_chart_structure  # angles/houses facts, если capability full
```

Планировщик:

1. Берёт целевой контракт (или набор для экрана).  
2. Строит DAG по `requires`.  
3. Пропускает `optional`, если facts/capability нет.  
4. Не запускает контракт, если `requires` не удовлетворены (gate) — не «попроси модель не выдумывать».

---

## Каталог контрактов (ids, не жёсткая очередь)

| contract_id | Назначение | requires (типично) | optional |
|-------------|------------|--------------------|----------|
| `natal_facts` | MVP: LLM → JSON карты (Sun/Moon/planets/angles/houses…) | — (только `available_input`) | geocode fields |
| `base_astrology` | Смысл L1-фактов / symbolism | `natal_facts` (date-level keys) | catalog |
| `name_numerology` | Числа + смысл имени | name in input | — |
| `natal_chart` | Смысл структуры карты | `natal_facts` with full capability | — |
| `personality` | Кто ты / эмоции / strengths / blind spots | `natal_facts` (+ `base_astrology` если отделён) | `name_numerology`, `natal_chart` |
| `relationships` | Близость | `personality` | `natal_chart` |
| `career` | Работа / реализация | `personality` | `natal_chart` (MC/10th) |
| `money` | Деньги | `personality` | `natal_chart` |
| `compatibility` | A×B | facts **обоих** профилей | depth packs |
| `today` | День | profile packages + day facts | ritual card/number |
| `tarot` | Ответ на вопрос | draw facts | profile slice |
| `reflection` | Вечер | `today` package | living marks |
| `growth` | Что помогает / рост | `personality` | living evidence |

Имена можно уточнять; менять можно промпт и модель, не ломая `contract_id` и schemas.

---

## Пример: `personality`

**UI binding:** слоты [PRODUCT_AVAILABILITY_MATRIX](./PRODUCT_AVAILABILITY_MATRIX.md) §3.1 Profile.  
Поля Output Schema = то, что UI имеет право положить в слот; `null` / omit = Hide when.

### Input Schema

```json
{
  "available_input": {
    "display_name": "string|null",
    "birth_date": "date",
    "birth_time": "string|null",
    "birth_place": "string|null",
    "latitude": "number|null",
    "longitude": "number|null",
    "timezone_at_birth": "string|null"
  },
  "calculated_facts": {
    "sun_sign": "required",
    "sun_element": "optional",
    "moon_sign": "optional",
    "life_path": "optional",
    "ascendant": "optional",
    "houses": "optional",
    "aspects": "optional",
    "planets": "optional"
  },
  "unavailable_facts": "object"
}
```

Facts SoT: контракт **`natal_facts`** (LLM JSON). Интерпретация **не** пересчитывает ASC/дома.

### Output Schema (слоты матрицы 3.1)

```json
{
  "identity_summary": "string|null",
  "sun_sign_meaning": "string|null",
  "element_expression": "string|null",
  "numerology_core": "string|null",
  "emotional_style": "string|null",
  "decision_style": "string|null",
  "relationship_style": "string|null",
  "work_and_realization": "string|null",
  "money_patterns": "string|null",
  "home_and_security": "string|null",
  "strengths": ["string"],
  "core_strengths": ["string"],
  "internal_tensions": ["string"],
  "growth_zones": ["string"],
  "blind_spots": ["string"],
  "chart_dominants": ["string"],
  "important_aspects": ["string"],
  "limitations": "string|null",
  "claims": [
    {
      "field": "string",
      "claim": "string",
      "source_fact_ids": ["string"],
      "confidence": "high|medium|low",
      "availability": "available|partial|unavailable"
    }
  ]
}
```

| Output field | Слот матрицы 3.1 | Free | Trial/Paid |
|--------------|------------------|------|------------|
| `identity_summary` | Узнавание | ✅ | ✅ |
| `sun_sign_meaning` · `element_expression` · `numerology_core` | Солнце · стихия · numerology | ✅ | ✅ |
| `emotional_style` · `decision_style` · `relationship_style` | Стили | ✅ | ✅ |
| `work_and_realization` · `money_patterns` · `home_and_security` | Работа / деньги / дом | ✅ если facts; house-based только full natal | ✅ |
| `strengths` · `core_strengths` | Сильные стороны | ✅ | ✅ |
| `internal_tensions` · `growth_zones` · `blind_spots` | Напряжения / рост (список) | ✅ краткий | ✅ deep |
| `limitations` | Limitations + CTA | ✅ | ✅ |
| deep `helps` | → contract `growth`, не personality | ❌ | ✅ |

### Execution Rules

- Использовать только ключи из `calculated_facts`.  
- Не использовать `houses` / `ascendant` / MC, если их нет или они в `unavailable_facts`.  
- Недостаточно оснований для поля → `null` / пустой массив.  
- Не вызывать контракт без минимума (нет date-level facts / нет `sun_sign`).  
- House-based формулировки запрещены при `natal_facts.mode != full`.

### Quality Rules

- Не противоречить переданным фактам.  
- Не повторять одно и то же разными словами в соседних полях.  
- Не ссылаться на missing data как на известное.  
- Voice: о человеке, не о системе.  
- Каждый существенный claim желательно с `source_fact_ids` (в `claims[]` или inline).

### Dependencies

```yaml
requires: [natal_facts]
optional: [name_numerology, natal_chart, base_astrology]
```

Отдельные слоты имени / ASC-структуры:

| Слот 3.1 | contract_id |
|----------|-------------|
| Нумерология имени | `name_numerology` |
| Структура карты | `natal_chart` |
| Соответствия (catalog) | `base_astrology` + catalog (не LLM invent) |

---

## Пример: `today` (day pack)

**UI binding:** [PRODUCT_AVAILABILITY_MATRIX](./PRODUCT_AVAILABILITY_MATRIX.md) §3.2 Today day pack.  
Один Implementation = один стабильный голос практика. Не отдельный промпт на цвет, отдельный на карту, отдельный на сферы.

### Input (логический)

```text
profile_slice          # natal_facts + personality summary (без kitchen)
day_astro_events       # транзиты / события дня (facts)
ritual_tarot_card?     # карта, которую открыл человек
ritual_day_number?     # число, которое открыл человек
intent_goals_slice?    # цели / намерение если есть
```

### Output — каждый блок с «почему»

| Поле / слой | Обязательное «почему» |
|-------------|------------------------|
| `day_character` | какой это день и что несёт |
| `talisman` (color / scent / stone) | почему эти; что дадут сегодня |
| `tarot_in_day` | как карта отражается на дне |
| `number_in_day` | как число отражается на дне |
| `do` / `avoid` | из всей сборки |
| `active_spheres[]` | какие активны и почему |
| `practice` | какая усилит и почему |
| `goals_today[]` | какие цели уместны и почему |

### Quality Rules (Today)

- Нет символа / сферы / практики / цели без обоснования на входах дня.  
- Карта и число **вплетены в день**, не отдельные гороскопы.  
- Voice = стабильный практик (таро+астро+нумерология); не смена автора между полями одного ответа.  
- Не противоречить profile facts; house-claims только при full natal.  
- Не говорить о системе / модели / «расчёте».

### Dependencies

```yaml
requires: [profile_ready_base]   # ≥ birth date / ready profile slice
optional: [tarot_draw, day_number, intent, full_natal]
```

**CODE Δ Today:** `day_story` / morning symbols — приближение; довести Input/Output и always-why под эту таблицу; убрать preset-only символы.

---

## Implementations (IP) — personality / shared

| Слот 3.1 | contract_id |
|----------|-------------|
| Нумерология имени | `name_numerology` |
| Структура карты (ASC/дома/MC) | `natal_chart` |
| Что помогает (L3) | `growth` |

### Implementations (IP)

| binding | Содержит |
|---------|----------|
| `deepseek-v4-pro` (MVP default) | system/user templates; params; version |
| `gpt-…` / `claude-…` / `gemini-…` / `local-llm-…` | отдельные тексты под модель, тот же Contract |

Каноническая форма текста: факты → unavailable → allowed fields → null.  
Качество формулировок — актив; смена модели = новая Implementation, не новый Contract.

**CODE Δ:** production Snapshot ещё пишется legacy `profile.identity|styles|patterns` — adapter до wiring по 3.1; не наращивать как SoT.

---

## Связь с Capability Contracts

| Слой | Документ |
|------|----------|
| Какие факты запросить / что unavailable | PRODUCT_CAPABILITY_CONTRACTS · PRODUCT_DATA_PROVIDERS |
| Что должно произойти (спека) | **Contract** в этом документе |
| Как модель этого добивается (IP) | **Implementations** в этом документе |

---

## Definition of Done

**Contract**

1. `contract_id` + Input / Output Schema.  
2. Dependencies (`requires` / `optional`).  
3. Execution Rules и Quality Rules — **отдельными** списками.  
4. Gate: skip если requires не выполнены.  

**Implementations**

5. Хотя бы один production binding (сейчас DeepSeek V4 Pro) + version.  
6. Eval: Case A (full facts) / Case B (time missing → null на house/ASC-полях) на default implementation.

---

## Open decisions

1. Один `natal_facts` vs split base/structure fact contracts.  
2. Где живут schemas / rules в репо (`docs/schemas/generation/` vs код).  
3. Machine-readable registry Contract + Implementations в MVP.  
4. Политика выбора Implementation (model routing / locale / experiment).

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-22 | v0.1 — ядро = Generation Contracts; prompt = implementation; deps graph not order |
| 2026-07-22 | v0.2 — Contract ⊕ Implementations (промпты = IP); Execution Rules ⊥ Quality Rules |
| 2026-07-23 | Two quality prompts locked: fact (`natal_facts`) ⊥ interpretation (`personality`+) — never merge |
| 2026-07-23 | `today` day pack: always-why · tarot/number in day · stable practitioner voice |
