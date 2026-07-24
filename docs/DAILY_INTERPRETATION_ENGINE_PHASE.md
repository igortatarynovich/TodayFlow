# Phase N — Daily Interpretation Engine

**Статус:** PLANNED — архитектурная фаза (не текущий execution slice)  
**Владелец:** Product + Architecture  
**Канон-база:** [EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md](explainability/EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md) · [PRODUCT_TRUTH_FIRST.md](./PRODUCT_TRUTH_FIRST.md) · [DAY_CONTEXT_V0.md](./DAY_CONTEXT_V0.md) · [DATA_OWNERSHIP_AND_CONSUMPTION_MAP.md](./DATA_OWNERSHIP_AND_CONSUMPTION_MAP.md) · [DAY_ENGINE_AND_COHERENCE.md](./DAY_ENGINE_AND_COHERENCE.md)  
**Следующий артефакт:** [rfc/RFC_DAILY_STATE_V0.md](./rfc/RFC_DAILY_STATE_V0.md) (DRAFT) — схема + правила конфликтов; **не** макет и **не** генератор символов  
**Канон текстов/советов:** [EXPLAINABLE_INTERPRETATION.md](explainability/EXPLAINABLE_INTERPRETATION.md)

---

## Зачем эта фаза

Это **не смена философии**, а продолжение Product Truth First и уже существующего Daily Engine.

Сегодня день собирается из нескольких рабочих слоёв (`DayContext`, `day_model`, `today_contract_v1`, `day_symbol_state_v1`, morning ritual symbols). Риск следующего шага — добавить «камень дня», «цвет дня», «талисман дня» как **отдельные вычисления**. Это нарушит канон:

> сначала модель → backend → контракт → UI  
> нет источника — нет блока

Правильный путь: **усилить единый движок интерпретации дня**, а производные (цвет, камень, аромат, практика, режим) получать из него.

---

## Принцип фазы

```
существующие сигналы
        ↓
   DailyState          ← единый SoT дня (эволюция DayContext / DayModel)
        ↓
 Recommendation Engine ← сопоставление, не независимые генераторы
        ↓
Today · Tarot · Numerology · Practices · Guidance
```

**Цвет, камень, аромат, талисман перестают быть вычислениями.**  
Они становятся **производными** от `DailyState`.

Главная защита: **не создавать второй центр правды о дне** рядом с DayContext — только эволюция в один контракт.

---

## Объект истины: DailyState

Рабочие имена (выбрать одно при kickoff фазы, не плодить параллельные):

| Кандидат | Роль |
|----------|------|
| **DailyState** | Публичный SoT дня для всех projections |
| DayContext (эволюция) | Уже есть как вход/снимок; может стать ядром DailyState |
| DayModel | Уже есть как смысловой слой; входит в `interpretation`, не заменяет SoT |

**Правило именования:** один объект — один контракт. Не вводить `DailyContext` рядом с `DayContext` без явной миграции.

### Из чего собирается (только существующие источники)

| Вход | Уже в продукте |
|------|----------------|
| Профиль / Personal Model | CoreProfile, CUM, profile_contract |
| Натал | natal / chart services |
| Транзиты / foundation | `daily_foundation`, spine |
| День (дата, ритуал, check-in) | DayConnection, ritual, fusion |
| Нумерология | personal day number / day_symbol |
| Выбранная карта | day_symbol_state / ritual card |
| История пользователя | history layer, meaning_events |
| Прочие сигналы | behavior_patterns, intent, rhythm |

Новые входные домены **не** открываются ради камня или цвета.

---

## Три обязательных решения kickoff (K1–K3)

Детали и черновик схемы: [RFC_DAILY_STATE_V0.md](./rfc/RFC_DAILY_STATE_V0.md).  
Без принятия K1–K3 фаза не переходит в implementation.

### K1. Разделить факты, синтез и рекомендации

| Слой | Смысл |
|------|--------|
| `evidence` | вычисленные / собранные входные факты |
| `interpretation` | вывод движка о дне |
| `recommendations` | пользовательские производные |

Не смешивать в одном плоском объекте «и факт, и вывод, и совет».

### K2. Provenance у каждой рекомендации

Не `stone: amethyst`, а полный объект: `id`, `reason`, `supports`, `based_on`, `confidence` (или null), `mapping_version`.

UI показывает готовый `reason` с backend — **без** повторной генерации объяснения на frontend.

### K3. Конфликт сигналов — не усреднение

Предусмотреть в контракте:

- `signal_tensions`
- `dominant_signal`
- `counter_signal`
- `resolution`

Чтобы выдавать полезные формулировки вроде: день поддерживает действие, но энергия ограничена → одно важное действие, не ускорение всего.

### K4. Объяснимые советы

Ни одно практическое утверждение без цепочки обоснования.  
Паттерны поведения важнее меню сфер.  
Промпт = structured DailyState; выход = основание → интерпретация → одно действие.  
Подробно: [EXPLAINABLE_INTERPRETATION.md](explainability/EXPLAINABLE_INTERPRETATION.md).

---

## Recommendation Engine (над interpretation)

Сопоставляет `interpretation` (+ evidence refs) → `recommendations` с provenance:

| Производное | Условие появления в production UI |
|-------------|-----------------------------------|
| цвет / камень / аромат / тотем | есть mapping + ProvenancedRec в контракте |
| практика | то же + practice catalog / current |
| режим дня / guidance | согласованы с `resolution` |

Каждое производное проходит Product Truth First и получает **паспорт UI-блока**. Пока маппинга нет — блока нет.

---

## Потребители

| Projection | Читает |
|------------|--------|
| Today | DailyState целиком |
| Tarot | interpretation + evidence (не hardcoded tags) |
| Numerology | evidence.personal_day |
| Practices | recommendations.practice |
| Profile (дневные якоря) | ссылка на Today / recommendations slice, не свой пересчёт |

---

## Явные запреты этой фазы

1. **Не добавлять** независимые генераторы «камень дня / цвет дня / талисман дня».  
2. **Не поднимать** morning `daily_symbols` в статус SoT (legacy / partial input).  
3. **Не рисовать** производные в production без контракта и provenance.  
4. **Не плодить** параллельный SoT рядом с DayContext.  
5. **Не усреднять** конфликтующие сигналы без `resolution`.  
6. **Не нарушать** порядок: модель → вычисление → API → контракт → состояния → UI.

Допустимо: RFC, docs, прототип вне production.  
Недопустимо: production-блок «как будто уже есть».

---

## Связь с тем, что уже в коде

| Уже есть | Роль в Phase N |
|----------|----------------|
| `build_day_context_v0` / DayContext | предшественник → преимущественно `evidence` + meta |
| `day_model` / `guide_decision` | → `interpretation` |
| `today_contract_v1` / `day_story` | projection Today (читает DailyState) |
| `day_symbol_state_v1` | evidence (карта/число), не замена DailyState |
| morning `daily_symbols` | legacy / partial input |
| Recommendation / practice current | → `recommendations` с provenance |

Phase N = **свести** куски в один движок, не добавить восьмой параллельный.

---

## Порядок реализации (после принятия RFC)

1. Принять RFC: имя контракта + **K1–K3**.  
2. JSON Schema + fixtures + validator.  
3. Сборщик: evidence / partial / fingerprint.  
4. Interpretation + conflict resolution (не average).  
5. Recommendation Engine: mapping → ProvenancedRec.  
6. Миграция потребителей: Today → Tarot → Practices → Profile day anchors.  
7. UI только после состояний loading/ready/empty/partial/error.  
8. Удаление обходных путей символов.

---

## Критерий готовности фазы

- Один backend-объект дня — SoT для всех projections.  
- Слои evidence / interpretation / recommendations разделены.  
- У каждой recommendation есть provenance.  
- Конфликты сигналов выражены через tensions + resolution.  
- Нет production UI символов без mapping.  
- Нет персональных «как будто».

---

**Сейчас:** Phase N = PLANNED.  
**Делать:** дорабатывать [RFC_DAILY_STATE_V0.md](./rfc/RFC_DAILY_STATE_V0.md).  
**Не делать:** макеты символов дня, генераторы камня/цвета, production UI.
