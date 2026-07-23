# Product Data Providers — факты карты и география

**Статус:** TARGET DRAFT (MVP)  
**Роль:** откуда берутся факты карты и места — **без лишних сервисов**.  
**Связь:** [PRODUCT_CAPABILITY_CONTRACTS.md](./PRODUCT_CAPABILITY_CONTRACTS.md) · [PRODUCT_GENERATION_CONTRACTS.md](./PRODUCT_GENERATION_CONTRACTS.md) · [LLM_QUALITY_AND_PROMPT_EVOLUTION.md](./LLM_QUALITY_AND_PROMPT_EVOLUTION.md)

---

## Принцип (MVP)

```text
Name · Date · Time · City
        ↓
Geography (минимально: resolve city → lat/lon/TZ; без нового сервиса)
        ↓
LLM structured call (DeepSeek V4 Pro)  →  NatalChartFacts JSON
        ↓
Generation Contracts (интерпретация только из этого JSON)
        ↓
Today / Compatibility / Tarot
```

| Часть | MVP | Не делать |
|-------|-----|-----------|
| **Факты карты** | Структурированный ответ **LLM** (сейчас DeepSeek V4 Pro) по контракту `natal_facts` | Отдельный astrology microservice «на вырост» |
| **География** | Существующий geocode / тонкий resolve; своя mega-БД — later | Не блокировать MVP новой ETL-платформой |
| **Справочная база знаний** | Накапливаемый **каталог / детерминированный lookup** (знак по дате, год животного, камень/цвет, ярлыки других гороскопов…) | Спрашивать LLM каждый раз «какой знак 13 февраля?» / «чей год 1990?» |

Продуктовый код **не** считает эфемериды сам. Он передаёт birth data в контракт **`natal_facts`** (executor = LLM) и сохраняет JSON.

**Swiss / local AstroEngine:** legacy read-path only. **Не SoT** продукта и не источник для Generation Contracts. Новый UI / новые промпты читают только validated `natal_facts` (+ catalog keys).

---

## 0. База знаний (каталог) — не LLM

**Правило:** всё, что однозначно следует из даты/ключа и уже известно справочнику, берём из **накопленной базы**, а не из промпта.

Примеры (не исчерпывающий список):

| Вопрос | Источник | Не так |
|--------|----------|--------|
| Какой тропический знак у 13 февраля? | `sign_for_date` / zodiac table | «LLM, какой знак?» |
| Чей китайский год 1990? | chinese horoscope / year table | переспрашивать модель |
| Тибетский / др. ярлык по дате | tibetan (и др.) lookup | выдумывать в personality |
| Камень · цвет · стихия **знака** (Profile шапка) | catalog keys | импровизация в UI |
| Цвет / запах / камень **дня** (Today) | **не** catalog-only: day + events + profile → today interpretation | `catalog[sun_sign]` или ротация пресетов как «цвет дня» |

Поток шапки Profile:

```text
birth_date (+ name?)
  → catalog / deterministic lookups  →  fixed keys для шапки
  → natal_facts (только то, чего нет в каталоге / углы-дома)
  → interpretation contracts читают keys + facts, не переизобретают справочник
```

**Накопление:** каждый подтверждённый ключ (традиция × значение × дата/знак) остаётся в репо/каталоге и переиспользуется. Нет ключа → omit блока, без выдумки.

CODE сегодня (зачатки, не единый SoT-файл): `data/astrology.sign_for_date`, `chinese_horoscope`, `tibetan_horoscope`, CONTENT/catalog*. **Δ:** собрать единый Profile header knowledge pack по ключам матрицы §3.1 «Соответствия».

---

## 1. Факты карты = LLM (не отдельный API)

**Единственный источник** Солнца, Луны, планет, углов (ASC/MC/IC/DSC), домов, аспектов, ретроградности, узлов (и опциональных точек) для MVP:

→ **structured LLM response** по контракту генерации `natal_facts` ([PRODUCT_GENERATION_CONTRACTS](./PRODUCT_GENERATION_CONTRACTS.md)), модель: DeepSeek V4 Pro.

Это **не** отдельный astrology microservice. Это executor контракта (LLM) с жёстким JSON Output Schema:

```text
available_input (date / time? / place? / lat/lon/TZ?)
→ LLM
→ NatalChartFacts (validated JSON)
→ persist on profile
→ следующие контракты (personality, …) только читают facts
```

### Оркестратор

```text
resolve natal facts (LLM)
  birth_date
  birth_time?          # нет → mode date_only; не просить ASC/houses
  place / lat / lon / timezone?
→ NatalChartFacts
```

### Контракт ответа `NatalChartFacts` (TARGET)

Минимум полей (имена стабильные; вендорные ключи не протекают наружу):

| Группа | Поля |
|--------|------|
| **Meta** | `provider`, `provider_version`, `calculation_id`, `house_system`, `zodiac` (tropical default), `mode` (`full` \| `date_only`), `confidence` |
| **Angles** | `ascendant`, `mc`, `ic`, `descendant` — каждый: sign, degree, absolute_longitude; **omit/null если mode≠full** |
| **Planets** | Sun…Pluto (+ Moon): sign, degree, absolute_longitude, house?, retrograde, speed? |
| **Points** | North/South Node; Chiron / Lilith / asteroids — **opt-in** в запросе |
| **Houses** | 12 cusps: sign, degree, absolute_longitude; planet_in_house assignments |
| **Aspects** | body1, body2, type, orb, applying? |
| **Unavailable** | `{ key, reason }` — зеркало Capability Contracts |

**Date-only:** запрос без time/place → API (или adapter) возвращает только то, что надёжно без углов; angles/houses в `unavailable`.

### Запрос к провайдеру (логически)

| Вход | Обязателен для `full` |
|------|------------------------|
| date | да |
| time (local) | да |
| lat / lon | да |
| timezone (IANA или offset на момент рождения) | да (из Geography) |
| house_system | default Placidus (продуктовый выбор) |

### Смена модели / провайдера LLM

Меняется `LLM_PROVIDER` / model id (сейчас DeepSeek V4 Pro).  
Контракт `NatalChartFacts` и downstream-промпты **не** меняются.

Позже, если понадобится детерминированный calc — подставить другой source за тем же JSON-shape. Для MVP это **не** строится.

### Code Δ

| TARGET MVP | CODE |
|------------|------|
| Natal facts из LLM JSON | Локальный `AstroEngine` + Swiss |
| Один fact-prompt → persist | Portrait funnel смешивает calc + LLM |
| Date-only: не просить ASC/houses | Частично: `time_unknown` strip |

---

## 2. География

### MVP

Не строить отдельный geo-сервис и ETL «на вырост».

- Использовать уже существующий resolve города (geocode / autocomplete), чтобы получить lat/lon и по возможности TZ.  
- Передать place (+ coords/TZ если есть) в fact-промпт LLM вместе с датой/временем.  
- Без места при известном времени — не просить ASC/houses (Availability / Capability).

### Later (не блокер MVP)

Своя локальная таблица НП (GeoNames-scale, TZ boundaries), чтобы мелкие населённые пункты не пропадали и runtime не зависел от Nominatim. См. историю решений ниже — **после** работающего LLM fact → profile loop.

### Code Δ

| TARGET MVP | CODE |
|------------|------|
| Тонкий geocode, без нового сервиса | `Geocoder` + Nominatim; TZ часто не пишется |

---

## Склейка в продукте

```text
1. User: Name · Date · Time? · City?
2. (optional) thin geocode → lat/lon/TZ
3. Capability Resolver → allowed fact fields
4. LLM fact prompt (DeepSeek) → NatalChartFacts → validate → persist
5. Generation Contracts interpretation (только из facts)
6. Today / Compatibility / Tarot
```

Place без time → не просить full natal / ASC / houses.

---

## Open decisions

1. Точный `prompt_id` fact-слоя (`profile.natal_facts.v1` vs `01`/`03` split).  
2. Валидация JSON карты (schema-only vs лёгкие sanity checks градусов).  
3. Когда (если) возвращать детерминированный calc — не блокер MVP.  
4. GeoNames local DB — post-MVP.  
5. Asteroids / Lilith / Chiron — default on или opt-in в fact prompt.

---

## Порядок работ (MVP)

1. JSON Schema `NatalChartFacts` (= Output Schema контракта `natal_facts`).  
2. Контракт `natal_facts` + Prompt-реализация + вызов DeepSeek.  
3. Persist на профиле; новый путь не зависит от inline Swiss.  
4. Контракты `personality` и далее — только на сохранённых facts.  
5. Legacy Swiss — не развивать; оставить до cutover.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-22 | v0.1 — split Astrology API vs Geography; swappable providers; local geo DB; code Δ |
| 2026-07-22 | v0.2 — Sun/Moon/planets/angles via Astrology API port |
| 2026-07-22 | v0.3 — **MVP pivot:** факты карты = LLM (DeepSeek V4 Pro), без отдельного астро-сервиса; geo ETL deferred |
| 2026-07-22 | v0.4 — ядро = Generation Contracts, не Prompt Library |
