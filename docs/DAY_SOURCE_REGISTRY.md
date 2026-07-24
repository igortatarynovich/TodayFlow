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
| `moon.void_of_course` | foundation | timed major Moon aspects + next ingress | yes when timeline resolves |
| `moon.timed_lunar_aspects` | foundation | `AstroService` sample+bisect majors | yes (feeds VOC + lunar timeline) |
| `numerology` | foundation (+ personal caps) | `target_date`; personal needs `birth_date` | universal only in Foundation |
| `weekday_ruler` | foundation | `target_date` | yes |
| `seasonal_calendar` | foundation | `target_date` + `lat/lon` | yes when geo |
| `planetary_hours` | foundation | `target_date` + `lat/lon` (+ TZ preferred) | yes when geo |
| `vedic_panchanga` | foundation | `target_date` (+ geo for muhurta) | yes |
| `chinese_metaphysics` | foundation | `target_date` (+ TZ preferred) | yes |
| `mayan_calendars` | foundation | `target_date` | soft |
| `personal_astrology` | **personal** | birth_date (profections); + `personal_transits` for natal transits | no (L3) |
| `human_design` | **personal** | `target_date` (+ birth for bodygraph) | no (L3; soft transit, Today later) |
| `bazi` | **personal** | `birth_date` (+ `birth_time` for hour pillar) | no (L3; clashes + pillars) |
| `vedic_personal` | **personal** | `birth_date`; Lagna gochara needs time+place | no (L3) |
| `kabbalah_letter` | **personal** | `target_date` | no (L3; Today claims deferred) |
| `electional_horary` | **personal** | explicit request + geo (+ time; question→horary) | no (situational) |

Планируемые (канон есть, адаптер later): solar/lunar returns, HD channels, …

### Pipeline wiring

`build_day_story_interpretation_v1` / `day_story_wire_v1` передают `target_date` и `birth_date` (из `core_profile.astro`) в Day Foundation. Foundation **всегда** собирается — даже без `celestial_events` (число дня + управитель недели).

`day_personal_v1` собирает L3 (`personal_astrology`, `human_design`, `bazi`, `vedic_personal`, `kabbalah_letter`, `electional_horary`) отдельно. `kabbalah_letter` без Today claims; `electional_horary` только при `electional_requested`.
