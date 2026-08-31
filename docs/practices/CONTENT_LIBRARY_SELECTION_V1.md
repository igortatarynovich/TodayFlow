# Content Library Selection v1

**Статус:** `ACCEPTED` — runtime bridge между Meaning (need) и Content Library (item).  
**Версия:** 1.0 (2026-08-29).  
**Владелец:** Product + Engineering.  
**Код:** `backend/src/todayflow_backend/services/content_library_selection_v1.py`.  
**Тесты:** `backend/tests/test_content_library_selection_v1.py`.  
**Parent:** [PRACTICE_CONTENT_TAXONOMY_V1.md](./PRACTICE_CONTENT_TAXONOMY_V1.md) · [PRACTICE_CONTENT_COVERAGE_V1.md](./PRACTICE_CONTENT_COVERAGE_V1.md) · [PRACTICE_LIBRARY_FILL_V1.md](./PRACTICE_LIBRARY_FILL_V1.md) · [PRACTICE_TECHNIQUE_PROVENANCE_V1.md](./PRACTICE_TECHNIQUE_PROVENANCE_V1.md).

**Это:** детерминированный выбор `active` Content Item по продуктовой потребности (purpose / direction / state / context).  
**Это не:** генерация текста, рекомендательная модель, LLM-ранжирование, копирование meaning в item.

---

## Architecture impact

- **SoT before:** Content Library имела валидатор и coverage ledger, но не было runtime-сервиса, который по need выбирал item. Практики в `day_scenario_project_v1.py` брались из старых `props.affirmations[0]`; `api/practices.py` использует legacy catalog.
- **SoT after:** `content_library_selection_v1.py` — canonical, deterministic selector. Meaning по-прежнему не знает `item_id`/`technique_id`. Item выбирается из `active` строк с `accepted` техникой по retrieval-полям. Сортировка стабильная, воспроизводимая, не-random.
- **Public contract changed?** no — добавлен internal service; API endpoints пока не меняются.
- **Migration required?** no runtime.
- **Canon updated?** yes — этот файл · `PRODUCT_EXECUTION_TRACKER.md` · `RELEASE_PLAN_V1.md`.
- **Backward compatible?** yes. Legacy endpoints остаются; новый сервис может постепенно заменять fallback-выборки.

---

## 0. Закон

1. **No LLM.** Выбор идёт по retrieval-полям JSON, не по embedding / model score.
2. **No randomness.** Одинаковый query + одинаковая библиотека всегда дают один и тот же `item_id`.
3. **Meaning не знает item_id.** Вход — `NeedQuery` (purpose, direction, state, context, ...). Выход — `ContentSelection` с `item_id`.
4. **Только active + accepted.** `status` item = `active`. Если `technique_id` указан, техника должна быть `accepted` в `technique_canon_v1.json`. Draft / skipped / техника без provenance — не выбираются.
5. **Hard tags first.** Purpose и direction обязательны совпадать. `content_class` / `type` — опциональные фильтры (например, чтобы взять именно discipline или meditation).
6. **Soft tags second.** `input_state`, `context`, `energy_effect`, `duration` — ранжируют, но не исключают.
7. **Honest miss.** Если нет совпадения — возвращается `matched=False` с причиной, не «успокаивающий» placeholder.

---

## 1. Query shape

```python
@dataclass
class NeedQuery:
    purpose: str          # обязательно
    direction: str        # обязательно
    input_state: list[str] = []   # soft
    context: list[str] = []       # soft
    duration: int | None = None     # soft
    duration_unit: str = "minutes"
    energy_effect: str | None = None  # soft
    content_class: str | None = None  # hard filter
    item_type: str | None = None      # hard filter
    locale: str = "ru"
```

---

## 2. Ranking

Кандидаты — активные items, чьи retrieval-поля совпадают по hard tags. Сортировочный ключ (меньше = лучше):

1. `-state_overlap` — больше совпадений `input_state`.
2. `-context_overlap` — больше совпадений `context`.
3. `-energy_match` — точное совпадение `energy_effect`, если задан.
4. `duration_penalty` — если задан `duration`, минимизируем разницу; иначе минимизируем саму длительность.
5. `item_id` — лексикографический tie-break для детерминизма.

---

## 3. Output shape

```python
@dataclass
class ContentSelection:
    item_id: str | None
    content_class: str | None
    item_type: str | None
    title: str
    body: str
    outcome_label: str
    duration: int | None
    duration_unit: str | None
    context: list[str]
    delivery: list[str]
    technique_id: str | None
    reason: str
    matched: bool
```

`reason` — краткая аргументация выбора (какие hard/soft tags совпали). Не пишется, если `matched=False`.

---

## 4. Usage

### Service

```python
from todayflow_backend.services.content_library_selection_v1 import (
    NeedQuery, select_content_item
)

q = NeedQuery(purpose="sleep", direction="prepare", input_state=["restless"])
selection = select_content_item(q)
assert selection.item_id == "meditation.sleep.001"
```

### Endpoint

`GET /practices/select?purpose=sleep&direction=prepare&input_state=restless`

Parameters:
- `purpose` (required)
- `direction` (required)
- `input_state` — comma-separated
- `context` — comma-separated
- `duration` — preferred session length
- `energy_effect` — `up` | `down` | `neutral`
- `content_class` — `practice` | `meditation` | `affirmation` | `discipline`
- `type` — item type code
- `locale` — `ru` (default) | `en`

Response: `ContentItemSelectResponse` (item_id, title, body, outcome_label, reason, matched).

---

## 5. Boundaries

- **Not a screen formatter.** `title`/`body` берутся из payload; как показывать — задача UI/Display Inventory.
- **Not a personalization engine.** State/context — soft filters, не заменяют Character Engine или Personal Model.
- **Not a content author.** Сервис не пишет новые items; только выбирает из существующих active.

---

## Changelog

| Дата | Изменение |
|------|-----------|
| 2026-08-31 | v1.0 IMPLEMENTED — service deployed, wired to `GET /practices` and `GET /practices/{id}`; catalog adapter maps 111 active Content Library items to the hub. |
| 2026-08-29 | v1.0 ACCEPTED — deterministic selection service, tests, canon. |
