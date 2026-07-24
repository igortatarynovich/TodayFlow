# RFC — DailyState v0

**Статус:** DRAFT — следующий артефакт Phase N (не implementation)  
**Фаза:** [DAILY_INTERPRETATION_ENGINE_PHASE.md](../DAILY_INTERPRETATION_ENGINE_PHASE.md)  
**Канон:** [EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md](../explainability/EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md) · [PRODUCT_TRUTH_FIRST.md](../PRODUCT_TRUTH_FIRST.md) · [DAY_CONTEXT_V0.md](../DAY_CONTEXT_V0.md) · [EXPLAINABLE_INTERPRETATION.md](../explainability/EXPLAINABLE_INTERPRETATION.md)  
**Запрещено до принятия RFC:** production UI, независимые генераторы символов дня, советы «по сферам» без цепочки обоснования

---

## Цель

Зафиксировать единый контракт дня как эволюцию `DayContext` / `DayModel` → **DailyState**, без второго центра правды.

Клиенты (Today, Tarot, Numerology, Practices, Profile day anchors) читают один объект.  
Цвет / камень / аромат / практика — только из `recommendations` с provenance.

---

## Обязательные решения kickoff

Без принятия пунктов ниже RFC не считается ready-for-implementation.

### K1. Разделить факты, синтез и рекомендации

Внутри контракта **нельзя смешивать** три слоя:

| Слой | Смысл | Примеры полей |
|------|--------|----------------|
| **evidence** | Вычисленные / собранные входные факты | natal_transits, personal_day, selected_card, check_in |
| **interpretation** | Вывод движка | day_axis, tempo, pressure, opportunity, risk, best_mode |
| **recommendations** | Пользовательские производные | color, stone, practice, guidance |

```text
evidence        → что было измерено / раскрыто / введено
interpretation  → что система вывела о дне
recommendations → что предложено пользователю (с provenance)
```

UI и LLM **не** пересобирают interpretation из recommendations.  
Если поля нет в своём слое — блока нет (Product Truth First).

### K2. У каждой рекомендации — provenance

Запрещена форма:

```yaml
stone: amethyst   # недостаточно
```

Обязательная форма элемента `recommendations.*`:

```yaml
stone:
  id: amethyst
  reason: "Сегодня усилены эмоциональная нагрузка и потребность в ясности."
  supports: ["emotional_load", "clarity_need"]
  based_on:
    - interpretation.pressure
    - interpretation.opportunity
    - evidence.check_in.energy
  confidence: 0.72          # только если есть измеримый источник; иначе null + omit UI %
  mapping_version: "rec_map_v0.1"
```

| Поле | Обязательность | Смысл |
|------|----------------|--------|
| `id` | да | стабильный код Reference / catalog |
| `reason` | да | готовое объяснение для UI (без повторной генерации на frontend) |
| `supports` | да | короткие machine tags тем, которые рекомендация поддерживает |
| `based_on` | да | пути к полям evidence/interpretation |
| `confidence` | нет | число только при реальном источнике; иначе `null` |
| `mapping_version` | да | версия таблицы сопоставления Recommendation Engine |

Нет `mapping_version` / нет `based_on` → рекомендация **не публикуется** в production UI.

### K3. Конфликт сигналов — не усреднение

Сигналы могут расходиться. DailyState **не** усредняет их в один «серый» день.

Обязательный блок в `interpretation` (или соседний top-level `conflicts`):

```yaml
signal_tensions:
  - a: evidence.natal_transits.caution
    b: evidence.personal_day.activation
    kind: tempo_vs_caution
  - a: evidence.selected_card.closure
    b: evidence.check_in.low_energy
    kind: closure_vs_capacity

dominant_signal:
  ref: evidence.check_in.low_energy
  weight_reason: "user-reported capacity bounds action"

counter_signal:
  ref: evidence.personal_day.activation
  weight_reason: "day number supports movement, not overload"

resolution:
  mode: "one_important_action"
  summary: "День поддерживает активные действия, но текущий уровень энергии ограничен. Лучше выбрать одно важное действие, а не пытаться ускорить всё сразу."
```

| Поле | Смысл |
|------|--------|
| `signal_tensions` | пары/группы противоречащих evidence-рефов |
| `dominant_signal` | что ограничивает или ведёт день |
| `counter_signal` | что тянет в другую сторону (не игнорировать) |
| `resolution` | продуктовое разрешение + `summary` для UI/guidance |

Правило: `interpretation.best_mode` и `recommendations.guidance` должны быть **согласованы** с `resolution`, а не обходить его.

### K4. Объяснимые советы (канон текста)

См. [EXPLAINABLE_INTERPRETATION.md](../explainability/EXPLAINABLE_INTERPRETATION.md). Кратко для контракта:

- Практическое утверждение без цепочки `evidence → pattern → risk/opportunity → action` **невалидно**.
- `recommendations.*.reason` — человеческий слой 1–3 (основание · интерпретация · действие), не ярлык сферы.
- Запрещены поля/тексты вида «избегать: семья» / «можно: работа» как самостоятельный продукт.
- Промпт получает slice DailyState; задача модели — обычная жизнь + один совет + почему сегодня; не «прогноз по отношениям».
- Паттерны поведения (`decisions`, `boundaries`, `completion`…) первичны; привязка к Life Map sphere — internal/optional, не меню UI.

---

## Черновик корня контракта

```yaml
contract_version: daily_state_v0
meta:
  target_date: YYYY-MM-DD
  locale: ru
  fingerprint: "…"          # стабильный ключ кэша / rebuild
  partial: true|false
  sources_present: [...]    # какие evidence-ключи реально заполнены

evidence:
  natal_transits: {...} | null
  personal_day: {...} | null
  selected_card: {...} | null
  check_in: {...} | null
  # только факты из существующих backend-источников

interpretation:
  day_axis: string | null
  tempo: string | null
  pressure: string | null
  opportunity: string | null
  risk: string | null
  best_mode: string | null
  signal_tensions: [...]
  dominant_signal: {...} | null
  counter_signal: {...} | null
  resolution: {...} | null

recommendations:
  color: ProvenancedRec | null
  stone: ProvenancedRec | null
  scent: ProvenancedRec | null
  totem: ProvenancedRec | null
  practice: ProvenancedRec | null
  guidance: ProvenancedRec | null
```

Точные типы и JSON Schema — отдельный шаг после принятия K1–K3 (файл вроде `docs/schemas/daily_state_v0.schema.json`).

---

## Миграция от текущего кода

| Сейчас | В DailyState |
|--------|----------------|
| DayContext `layers.*` | преимущественно → `evidence` (+ часть meta) |
| `day_model` / spine / `guide_decision` | → `interpretation` |
| practice current / future symbol maps | → `recommendations` с provenance |
| morning `daily_symbols` | legacy input → только через evidence + mapping, не SoT |

Один публичный read-path. Параллельный «второй день» запрещён.

---

## Критерии принятия RFC

- [ ] K1: три слоя разделены в схеме и в правилах сборщика  
- [ ] K2: тип `ProvenancedRec` обязателен для всех recommendations  
- [ ] K3: конфликт сигналов описан; запрет silent average зафиксирован  
- [ ] K4: советы только с цепочкой обоснования; запрет sphere-menu copy; промпт = structured DailyState ([EXPLAINABLE_INTERPRETATION.md](../explainability/EXPLAINABLE_INTERPRETATION.md))  
- [ ] Имя контракта и отношение к `day_context_v*` выбраны без дубля SoT  
- [ ] JSON Schema + минимум один valid / один invalid fixture  
- [ ] Список потребителей и порядок миграции согласованы  

**Не входит в принятие RFC:** макеты UI, генераторы камня/цвета, свободные LLM-промпты «прогноз по сфере».

---

## Следующий шаг после принятия

1. Schema + fixtures + validator script  
2. Сборщик (эволюция `build_day_context_v0` / day_model)  
3. Recommendation Engine с `mapping_version`  
4. Миграция потребителей  
5. UI по Product Truth First  
6. Удаление обходных путей
