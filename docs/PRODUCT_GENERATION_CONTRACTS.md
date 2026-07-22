# Product Generation Contracts

**Статус:** TARGET DRAFT — **ядро продукта**  
**Роль:** два связанных актива — **Contract** (продуктовая спецификация) и **Implementations** (промпты под модели = IP).  
**Связь:** [PRODUCT_CAPABILITY_CONTRACTS.md](./PRODUCT_CAPABILITY_CONTRACTS.md) · [PRODUCT_DATA_PROVIDERS.md](./PRODUCT_DATA_PROVIDERS.md) · [PRODUCT_AVAILABILITY_MATRIX.md](./PRODUCT_AVAILABILITY_MATRIX.md) · Voice · Explainable Computation  
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
| `today` | День | profile packages + day facts | — |
| `tarot` | Ответ на вопрос | draw facts | profile slice |
| `reflection` | Вечер | `today` package | living marks |
| `growth` | Что помогает / рост | `personality` | living evidence |

Имена можно уточнять; менять можно промпт и модель, не ломая `contract_id` и schemas.

---

## Пример: `personality`

### Input Schema (черновик)

```json
{
  "available_input": { "display_name": "string|null", "birth_date": "date", … },
  "calculated_facts": {
    "sun_sign": "required",
    "moon_sign": "optional",
    "life_path": "optional",
    "ascendant": "optional",
    "houses": "optional"
  },
  "unavailable_facts": "object"
}
```

### Output Schema (черновик)

```json
{
  "identity_summary": "string|null",
  "emotional_style": "string|null",
  "relationship_style": "string|null",
  "strengths": "string[]",
  "blind_spots": "string[]",
  "limitations": "string"
}
```

### Execution Rules

- Использовать только ключи из `calculated_facts`.  
- Не использовать `houses` / `ascendant`, если их нет или они в `unavailable_facts`.  
- Недостаточно оснований для поля → `null` / пустой массив по схеме.  
- Не вызывать контракт, если нет минимума Input Schema (напр. нет `sun_sign` и нет date facts).

### Quality Rules

- Не противоречить переданным фактам.  
- Не повторять одно и то же разными словами в соседних полях.  
- Не ссылаться на missing data как на известное.  
- Voice: о человеке, не о системе.

### Dependencies

```yaml
requires: [natal_facts]
optional: [name_numerology, natal_chart]
```

### Implementations (IP)

| binding | Содержит |
|---------|----------|
| `deepseek-v4-pro` (MVP default) | system/user templates; params; version |
| `gpt-…` / `claude-…` / `gemini-…` / `local-llm-…` | отдельные тексты под модель, тот же Contract |

Каноническая форма текста: факты → unavailable → allowed fields → null.  
Качество формулировок — актив; смена модели = новая Implementation, не новый Contract.

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
