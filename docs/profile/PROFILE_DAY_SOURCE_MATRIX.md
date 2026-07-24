# Profile × Day Source Matrix

**Статус:** принято (канон доступности Source Families по данным профиля).  
**Версия:** 1.0 (2026-07-24).  
**Канон источников:** [DAY_SOURCES_CANON.md](../DAY_SOURCES_CANON.md) · [DAY_SOURCE_REGISTRY.md](../DAY_SOURCE_REGISTRY.md).

## Назначение

Ответить: **какие поля профиля / контекста открывают какие Source Families**.  
Без времени рождения продукт не «ломается» — сужается набор семейств.

---

## 1. Входные атомы

| Atom | Описание | Где живёт |
|------|----------|-----------|
| `target_date` | Гражданская дата дня | Always (Today request) |
| `timezone` | TZ пользователя / места | Profile or device |
| `lat` / `lon` | Координаты для локального неба | Profile place / device geo |
| `birth_date` | Дата рождения | Profile |
| `birth_time` | Время рождения | Profile (optional) |
| `birth_place` → `birth_lat/lon` | Место рождения | Profile (optional) |
| `birth_name` | Имя для name-numbers | Profile (optional) |
| `celestial_events` | Precomputed sky bridge (v0) | Server day pipeline |
| `draw_event` | Таро / оракул | Ritual / L5 |
| `life_signals` | Mood, tasks, calendar | L4 user data |

---

## 2. Матрица: Source Family → требования

| Source Family | Capability (пример) | Требует | Foundation | Personal | Today |
|---------------|---------------------|---------|------------|----------|-------|
| `western_astrology` | positions, aspects, ingresses, retro | `target_date` + ephemeris/`celestial_events` | yes | soft | yes |
| `moon` | phase, sign, lunar aspects | same as sky | yes | no | yes |
| `moon` | rise/set, VOC local | + `lat/lon` + `timezone` | yes when geo | no | yes |
| `weekday_ruler` | ruler | `target_date` | yes | no | yes |
| `numerology` | universal_day | `target_date` | yes | no | yes |
| `numerology` | personal_year/month/day | + `birth_date` | no* | yes | yes |
| `numerology` | name_numbers | + `birth_name` + alphabet canon | no | yes | optional |
| `planetary_hours` | hour table | `target_date` + `lat/lon` + `timezone` | yes | elective | yes |
| `seasonal_calendar` | sun rise/set | `lat/lon` + `timezone` | yes | no | yes |
| `vedic_panchanga` | tithi…karana | datetime (+ geo for muhurta) | yes | no | later |
| `vedic_panchanga` / `vedic_personal` | gochara / dasha / lagna_gochara | + natal Moon; Lagna needs time+place | no | yes | yes |
| `chinese_metaphysics` | gan_zhi_day + lucky hours/directions | `target_date` (+ TZ preferred) | yes | soft | yes |
| `chinese_metaphysics` / `bazi` | bazi / clashes | + birth datetime (+ hour for full) | no | yes | yes |
| `mayan_calendars` | tzolkin_haab / dreamspell | `target_date` | soft | no | soft |
| `personal_astrology` | natal_transits (sign-level) | sky + `birth_date` (+ natal facts) | no | yes | yes |
| `personal_astrology` | houses, ASC/MC, progressions | + `birth_time` + `birth_place` | no | yes | yes |
| `human_design` | transit gates | datetime | soft* | yes (wire) | soft |
| `human_design` | bodygraph interaction | + birth datetime (+ place for depth) | no | yes | soft |

\* Soft Foundation transit sky deferred — v1 collected in Day Personal, not Foundation essence.
| `tarot_oracle` | card of day | `draw_event` | **no** | contextual | yes (L5) |
| `life_context` | tasks/mood | user permissions | no | — | yes (L4) |
| `biorhythms` | — | birth_date | **out_of_core** | — | no |
| `synchronicity_journal` | — | user observation | no | — | journal |

\* Personal day numbers могут **ехать в wire** рядом с Foundation для UI, но канонически относятся к Personal layer ([DAY_SOURCES_CANON](../DAY_SOURCES_CANON.md) §5.5).

---

## 3. Профили доступности (готовые наборы)

### A. Только дата дня (гость / минимум)

**Есть:** `target_date`  
**Доступно:**

- Foundation: `weekday_ruler`, `numerology.universal_day`
- Moon / Western: только если сервер уже построил shared sky без профиля (`celestial_events`)

**Недоступно:** personal numerology, houses, HD, BaZi, dashas

### B. Дата + shared sky (типичный Today без натала)

**Есть:** `target_date` + server `celestial_events`  
**Доступно:**

- Full shared Foundation: western_astrology + moon + weekday + universal_day

**Недоступно:** L3 personal

### C. + дата рождения

**Добавляется:**

- `numerology` personal year/month/day
- sign-level natal transits (если есть natal facts / positions by date)

**Всё ещё нет:** ASC, houses, progressions, HD, full BaZi hour pillar

### D. + время и место рождения

**Добавляется:**

- houses, angles, house transits, progressions, solar/lunar returns (when implemented)
- Human Design bodygraph
- BaZi hour pillar / full four pillars
- Vedic Lagna-based gochara

### E. + геолокация пользователя (не обязательно birth place)

**Добавляется:**

- moon rise/set, planetary hours, sun rise/set, local muhurta, visibility

### F. + ритуал / L5

**Добавляется:**

- `tarot_oracle` (не смешивать в Foundation)

---

## 4. UX-правило честности

| Ситуация | Сообщение продукту |
|----------|-------------------|
| Нет `birth_time` | Показывать Foundation; не обещать «дома» / ASC |
| Нет `birth_date` | Universal day ok; personal day скрыт / locked |
| Нет geo | Не показывать планетарные часы как точные |
| Tarot drawn | Подпись: оракул · не расчёт дня |

Registry возвращает `status=unavailable` + `unavailable_reason` — UI и Story опираются на это, а не на догадки.

---

## 5. Связь с кодом

| Артефакт | Роль |
|----------|------|
| `DaySourceInputs` | атомы §1 |
| `DaySourceRegistry.collect` | gate по `required_input_keys` |
| `build_day_foundation_from_sources` | только `ok` foundation families |
| Profile disclosure / availability matrix | продуктовые слоты — не дублировать школьную логику |

---

## 6. Changelog

| Дата | Версия | Изменение |
|------|--------|-----------|
| 2026-07-24 | 1.0 | Первая матрица: atoms → families → availability sets A–F |
