# Day Source Registry

**Статус:** принято (контракт + код v0).  
**Версия:** 0.1 (2026-07-24).  
**Канон:** [DAY_SOURCES_CANON.md](./DAY_SOURCES_CANON.md).

## Назначение

Единая точка регистрации Source Families. Day Foundation **не** знает школы и формулы — только читает `SourceResult` из Registry.

```text
DaySourceInputs
    → Registry.resolve (по наличию входов + flags)
    → providers.run → SourceResult[]
    → Day Foundation (синтез L1/L2)
```

## Код

| Путь | Роль |
|------|------|
| `backend/.../services/day_sources/types.py` | `DaySourceInputs`, `SourceResult`, family specs |
| `backend/.../services/day_sources/registry.py` | register / resolve / collect |
| `backend/.../services/day_sources/adapters/` | concrete families (v1: western_astrology, moon, numerology, weekday_ruler) |

## SourceResult (нормализованный выход)

| Поле | Тип | Смысл |
|------|-----|--------|
| `family_id` | str | slug из канона |
| `capability_ids` | str[] | какие capabilities отданы |
| `layer` | `foundation` \| `personal` \| `life` \| `interactive` | уровень потребления |
| `status` | `ok` \| `unavailable` \| `skipped` | результат resolve/run |
| `unavailable_reason` | str \| null | например `missing_birth_time` |
| `payload` | object | детерминированные факты семейства |
| `evidence_refs` | str[] | ссылки на сырые источники / ids |
| `calculation_version` | str | версия расчёта адаптера |

## Правило добавления семьи

1. Строка в [DAY_SOURCES_CANON.md](./DAY_SOURCES_CANON.md).  
2. Адаптер `adapters/{family_id}.py` с `run(inputs) -> SourceResult`.  
3. `register()` в `registry.default_registry()`.  
4. Тест: available / unavailable по входам.  
5. Foundation **не** трогать, кроме whitelist семейств для синтеза (если новый источник идёт в shared plot).

## v1 зарегистрированные семьи

| family_id | layer | required for `ok` | Foundation |
|-----------|-------|-------------------|------------|
| `western_astrology` | foundation | `celestial_events` или ephemeris path | yes |
| `moon` | foundation | lunar fields in celestial / ephemeris | yes |
| `numerology` | foundation (+ personal caps) | `target_date`; personal needs `birth_date` | universal only in Foundation |
| `weekday_ruler` | foundation | `target_date` | yes |

Планируемые (канон есть, адаптер later): `vedic_panchanga`, `chinese_metaphysics`, `planetary_hours`, `human_design`, `personal_astrology`, …
