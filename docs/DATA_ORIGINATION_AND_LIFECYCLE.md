# Происхождение данных и жизненный цикл (Data Origination & Lifecycle)

**Статус:** принято (канон **откуда данные берутся, как подтверждаются и когда устаревают**).  
**Версия:** 1.0 (2026-05-31).  
**Владелец:** Product + Engineering.

**Роль:** дополняет [DATA_OWNERSHIP_AND_CONSUMPTION_MAP.md](./DATA_OWNERSHIP_AND_CONSUMPTION_MAP.md) (кто владеет и **когда читает**) ответами на:

- **откуда** сущность появляется;
- **кто** её подтверждает;
- **как** и **как часто** обновляется;
- **когда** устаревает, архивируется или удаляется;
- **когда** становится **Knowledge** (обучаемым активом).

**Связь:** [ONTOLOGY_AND_FOUNDATION_PHASES.md](./ONTOLOGY_AND_FOUNDATION_PHASES.md) (фаза 1 — контекст), [REFERENCE_LAYER_AND_BUILD_ORDER.md](./REFERENCE_LAYER_AND_BUILD_ORDER.md) (§6 catalog), [KNOWLEDGE_ACQUISITION_AND_SIGNAL_POLICY.md](./KNOWLEDGE_ACQUISITION_AND_SIGNAL_POLICY.md) (каналы сбора), [USER_KNOWLEDGE_MODEL.md](./USER_KNOWLEDGE_MODEL.md) (Knowledge Atoms), [INTERPRETATION_LAYER_AND_REFERENCE.md](./INTERPRETATION_LAYER_AND_REFERENCE.md) (Event ≠ meaning), [EVOLUTION_CALCULATION_CONTRACT.md](./EVOLUTION_CALCULATION_CONTRACT.md), [PERSONAL_INTELLIGENCE_LAYER.md](./PERSONAL_INTELLIGENCE_LAYER.md), [PERSONAL_INTELLIGENCE_LAYER.md](./PERSONAL_INTELLIGENCE_LAYER.md).

---

## 0. Жёсткое правило разработки

**Запрещено** планировать следующий шаг как:

- «Какой **экран** сделать следующим?»
- «Какой **API** сделать следующим?»

**Обязательно** планировать как:

> **«Какие данные существуют в системе и как они появляются?»**

Порядок исполнения TodayFlow:

```
Определить данные → Структура → Способ появления → Обновление → Жизненный цикл → Наполнение
  → только потом: Derived snapshots → Engines → API → UI
```

**Freeze:** новый экран, endpoint или LLM surface **без строки** в §7 (Entity Registry) или явной пометки «consumer of existing SN» — **не принимается** в Phase 0–1 без записи в PRODUCT_EXECUTION_TRACKER.

**Consumers последними:** API и UI — **проекции** уже существующих CD/DD/SN; не источники истины.

---

## 1. Шесть уровней (канонический порядок)

| Уровень | Вопрос | Артефакт |
|---------|--------|----------|
| **1. Определить данные** | Что это? Зачем? Кто владелец? Где хранится? Кто использует? SoT? | §7 Entity Registry; REFERENCE §6 |
| **2. Структура данных** | Поля, связи, версии, статусы, Machine + Content Contract | `reference_machine_contract_v1`, taxonomy C/D/Co/R |
| **3. Способ появления** | Manual / Generated / Imported / User Created / Learned / Derived | §3 Creation Methods |
| **4. Способ обновления** | Никогда / редко / по событию / по расписанию / continuous | §4 Update Cadence |
| **5. Жизненный цикл** | Создание → Подтверждение → Использование → Обновление → Архив | §5 Lifecycle States |
| **6. Наполнение и пополнение** | Кто заполняет, как пополняется справочник | §8 Filling Policy |

Уровни **1–6** выполняются **до** consumer-слоя (DayModel aggregation, narrative API, экраны).

---

## 2. Девять обязательных полей (шаблон сущности)

Для **каждой** сущности в Entity Registry (§7) фиксируются:

| Поле | Смысл |
|------|--------|
| **Owner** | Команда/движок, ответственный за корректность |
| **Source of Truth** | Где каноническая запись (path, table, formula id) |
| **Creation Method** | §3 — как появляется **первый раз** |
| **Update Method** | §4 — как меняется после создания |
| **Validation Method** | schema CI, expert review, confirmation gate, eval |
| **Versioning Policy** | semver record, `valid_from`, `reference_version` in SN |
| **Consumer List** | engines/API/UI **без** обратного ownership |
| **Retention Policy** | сколько хранить, когда delete vs archive |
| **Learning Policy** | можно ли в training; `knowledge_type`; trust tier |

**Правило:** если поле «—» / TBD — сущность **не** `active` в проде.

---

## 3. Creation Methods (способ появления)

| Метод | Код | Определение | Пример |
|-------|-----|-------------|--------|
| **Manual Reference** | `manual` | эксперт/platform заполнил CD/Co | Tarot major machine draft, ZodiacSign |
| **Generated** | `generated` | движок вычислил по формуле + ref | personal day number, transit list |
| **Imported** | `imported` | bulk ingest из внешнего каталога | ephemeris tables, SKU catalog (future) |
| **User Created** | `user_created` | явный ввод пользователя | birth_date, goal text, journal entry |
| **Learned** | `learned` | из behavior после KASP gate | behavioral pattern, preference hypothesis |
| **Derived** | `derived` | из других SN/CD без нового смысла | Ascendant, DayContext, Evolution Score |

**Комбинации допустимы:** Personal Day = `generated` (value) + `manual` (machine meaning by reduced 1–9).

**Запрет:** `learned` → `fact` без Confirmation (KASP §5, UKM).

---

## 4. Update Cadence (способ обновления)

| Cadence | Когда | Примеры |
|---------|-------|---------|
| **Immutable** | практически никогда | Tarot Card identity, LetterMapping |
| **Rare** | при смене user input или migration | CoreProfile, natal snapshot |
| **Daily batch** | cron / first-open-of-day | card-of-day, personal cycles, DayContext |
| **Event-driven** | на действие пользователя | check-in, practice_completed, goal update |
| **Continuous** | stream / rolling window | Behavior aggregates, fusion scores |
| **Scheduled recompute** | weekly/monthly job | Evolution Score, theme history |

---

## 5. Lifecycle States

### 5.1 Reference records (CD/Co)

```
draft → review → active → deprecated → archived
```

| Переход | Кто | Условие |
|---------|-----|---------|
| `draft` → `review` | Editorial / Eng | schema valid + peer review |
| `review` → `active` | Product owner | Dependency Map satisfied; consumers listed |
| `active` → `deprecated` | Product | replacement entity exists; SN carry `reference_version` |
| `deprecated` → `archived` | Eng | no SN in retention window references version |

### 5.2 User knowledge (UKM)

```
draft → candidate → confirmed → active → deprecated
```

| Статус | `knowledge_type` | В LLM / high-priority rec |
|--------|------------------|---------------------------|
| `draft` | — | нет |
| `candidate` | `hypothesis` | нет |
| `confirmed` | `pattern` / `fact` | да (по tier) |
| `active` | as confirmed | да |
| `deprecated` | — | read-only history |

**Гипотеза «пользователь предпочитает короткие ответы»:** `learned` → `candidate` → user confirm или stable pattern → `confirmed`.

### 5.3 Snapshots (SN)

```
computed → persisted → consumed → superseded → (optional) archived
```

Пересчёт SN **не** меняет CD. Новый SN ссылается на `reference_version` + input hash.

---

## 6. Validation Methods

| Метод | Применение |
|-------|------------|
| **JSON Schema CI** | all `reference_machine_contract_v1` records |
| **Expert editorial review** | content contract, symbolic meaning |
| **Formula unit tests** | numerology reduction, astro calc |
| **Confirmation gate** | behavioral → knowledge (KASP §5) |
| **Quality / eval gate** | generation output before show (PIL §10) |
| **Cross-source coherence** | DayModel conflict detector (P1.0+) |

---

## 7. Entity Registry (v1 — ключевые сущности)

Легенда Creation: M=manual, G=generated, I=imported, U=user_created, L=learned, D=derived.

### 7.1 Reference (CD)

| Entity | Owner | Source of Truth | Create | Update | Validation | Versioning | Consumers | Retention | Learning |
|--------|-------|-----------------|--------|--------|------------|------------|-----------|-----------|----------|
| **TarotCard (major)** | Platform / Editorial | `DATA/reference/tarot/machine/*.json` + content JSON | M | Immutable (identity); machine semver rare | Schema CI + review | `version`, `status` per file | Daily Engine, DayModel, Generation | Permanent CD | Co → dataset **after** review; not raw LLM |
| **Numerology CoreNumber** | Platform / Editorial | `DATA/reference/numerology/machine/core_*.json` | M | Immutable core; machine semver rare | Schema CI + review | per record | Profile Engine, DayModel, Commerce | Permanent CD | same as Tarot |
| **Numerology PersonalDay/Month/Year (machine)** | Platform / Editorial | `personal_*_*.json` | M | Rare editorial | Schema CI | per record | DayModel, Commerce, Horoscope | Permanent CD | — |
| **LetterMapping** | Platform | `DATA/numerology.json` | M | Rare | Unit tests | file version | NumerologyService | Permanent | — |
| **ZodiacSign** | Platform / Editorial | `DATA/astrology_reference/zodiac_signs.json` | M | Rare | Schema + review | TBD unified | Profile, Horoscope, DayModel | Permanent CD | — |
| **Planet / House / Aspect** | Platform / Editorial | `DATA/astrology_reference/*.json` | M / I (ephemeris) | Rare | Schema + astro tests | TBD | Profile, Daily Engine | Permanent CD | — |
| **PracticeTemplate** | Platform / Editorial | `rituals.json`, `mantras.json` | M; later AI **draft** | Review → active | Editorial | per template | Flow, Today rec | deprecated → archive | usage signals → **not** auto-edit template |
| **HabitType** | Platform | catalog TBD | M | Rare | review | semver | Calendar, Today | permanent | — |
| **Symbolic Product SKU** | Commerce / Editorial | catalog TBD | M / I | catalog sync | commerce review | sku version | Commerce layer | while listed | purchase events → behavioral only |
| **UI Copy (UiCta)** | Product / i18n | `CONTENT/i18n/*` | M | frequent copy | max_length + lint | key semver | UI all platforms | replace in place | — |
| **Interpretation Reference** | Platform / Editorial | ILR catalog TBD | M; later L-assisted draft | review | ILR L1–L4 rules | meaning_id version | Interpretation Engine | permanent | confirmed meanings → dataset |

### 7.2 Derived & runtime (DD / SN / RT)

| Entity | Owner | Source of Truth | Create | Update | Validation | Versioning | Consumers | Retention | Learning |
|--------|-------|-----------------|--------|--------|------------|------------|-----------|-----------|----------|
| **Ascendant / houses** | Profile Engine | natal calc SN | D ← birth_date, time, location | Rare (birth fix) | astro tests | `profile_hash` | CoreProfile, Map | user account life | — |
| **Personal Day Number** | Daily Engine | formula + `numerology.personal_day.{n}` machine | G daily | Daily batch | formula tests | date key in DayContext | DayModel, ritual | SN 90d+ (TBD) | — |
| **Personal Month / Year** | Profile / Daily | formula + machine ref | G | monthly / yearly roll | formula tests | cycle id in SN | Commerce, Horoscope | SN policy | — |
| **Card of Day** | Daily Engine | pick algo + tarot ref | G daily | Daily batch | stable `entity_code` | day + card in SN | Today, DayModel | SN retention | open/save events → behavioral |
| **DayContext** | Daily Engine | `build_day_context_v0` output | D | Daily / check-in | contract tests | `day_context_sha256` | Generation, PIL | logs + optional persist | full context **not** training raw |
| **DayModel v1** | Daily Engine | aggregator | D ← tarot + numerology + astro | Daily | P1.0 contract tests | in DayContext | Decision, narrative depth | with DayContext | — |
| **CoreProfile Snapshot** | Profile Engine | DB / SN store | D | Rare | integration tests | `profile_hash`, ref versions | Today path, API | account life | — |
| **Check-in snapshot** | Tracking | RT → SN | U + G (map slug) | Event | slug catalog | per day | DayModel risk/tempo | 365d TBD | → signal, not fact |
| **Behavioral Pattern** | Learning / UKM | `internal_profile`, knowledge store | L ← events | Continuous | confirmation gate | atom id + version | CUM, DayModel (future) | while active | **yes** after `confirmed` |
| **Knowledge Atom** | UKM | knowledge store | L / U after confirm | Event / decay | UKM schema | atom version | PIL, LLM Gate | deprecate, not silent delete | **primary** training asset |
| **Evolution Score** | UEM (future) | PEG internal | D | Scheduled weekly | ECC tests | ES snapshot | stage engine — **not API until UEM-2** | history snapshots | aggregates only |
| **Today Narrative Output** | Generation | `generation_logs` | G (LLM/template) | per request | quality gate | `generation_id` | UI | AMLL retention | pairs + reactions → dataset |

### 7.3 Примеры (уровень 3 — появление)

| Сущность | Появляется | Из чего |
|----------|------------|---------|
| Zodiac Sign | Manual Reference | editorial JSON |
| Ascendant | Derived | birth_date, birth_time, birth_location |
| Personal Day | Generated + Manual machine | date formula → lookup `numerology.personal_day.{n}` |
| Behavioral pattern | Learned | events → signals → confirmation |
| Hypothesis «короткие ответы» | Learned → candidate | behavioral + optional explicit confirm |

---

## 8. Filling & Replenishment Policy (уровень 6)

**Принцип:** у каждого справочника есть **владелец наполнения** и **способ пополнения** — не ad-hoc правки в коде/UI.

| Domain | Primary source | Replenishment | Review | Tooling (target) |
|--------|----------------|---------------|--------|------------------|
| **Tarot** | Expert editorial | Manual PR to `DATA/reference/tarot/` | Product + astro/tarot reviewer | schema validator, 78-card checklist |
| **Numerology** | Expert editorial | Manual PR to `DATA/reference/numerology/` | Product reviewer | schema validator, 39-record gate |
| **Astrology** | Expert + imported ephemeris | Manual JSON + calc tables | Astro reviewer | unified schema, calc regression |
| **Practices** | Expert; later AI drafts | Manual; AI → `draft` only | Editorial | template schema |
| **Symbolic Assets** | Commerce catalog + editorial | Manual SKU; import feed | Commerce + Product | SKU ↔ stage/month gates |
| **Behavior Interpretation** | Expert ILR | Manual; later Learning-assisted **candidates** | L4 never auto-promote | ILR instance log |
| **UI Copy** | Product / i18n | Manual locale PR | copy lint | max_length CI |
| **User Knowledge** | System (KASP) | Automatic **signals**; knowledge only after confirm | user + eval | UKM atom API internal |

**AI-assisted replenishment (future):** только `draft` / `candidate`; promotion → `review` → `active` человеком. LLM **не** пишет напрямую в `active` CD.

**Детальные playbooks** по доменам дополняются **точечно** в REFERENCE §6 (колонка Filling) — без отдельного «mega-audit».

---

## 9. Связь с другими канонами

| Документ | Разделение ответственности |
|----------|----------------------------|
| **DATA_OWNERSHIP** | CD/DD/SN/RT; **кто читает когда**; API read model |
| **Этот документ (DOL)** | **откуда берётся**, confirm, update, retire, learning eligibility |
| **KASP** | какие каналы сбора **разрешены** |
| **UKM** | форма Knowledge Atom после confirm |
| **REFERENCE §6** | inventory + storage path |
| **EVOLUTION_CALCULATION_CONTRACT** | Derived ES; API gate |

**Цепочка для обучаемых данных:**

```
Creation (§3) → Validation (§6) → Use in SN → Events → Signals (KASP)
  → Interpretation (ILR) → Confirmation → Knowledge (UKM) → Dataset (AMLL)
```

---

## 10. Чеклист для новой сущности (DoD data-first)

- [ ] Строка в §7 Entity Registry (или REFERENCE §6)
- [ ] Creation Method + Update Cadence named
- [ ] Source of Truth path / formula id
- [ ] Machine and/or Content contract (или явно «runtime only»)
- [ ] Validation method in CI or review checklist
- [ ] Versioning + retention documented
- [ ] Consumer list — engines only; API/UI marked as projection
- [ ] Learning Policy: trainable? `knowledge_type`? trust tier?
- [ ] PRODUCT_EXECUTION_TRACKER row

---

## 11. Build order (вставка в Global)

```
Reference taxonomy (§6)
  → DATA_ORIGINATION_AND_LIFECYCLE (этот документ) — per-entity origination
  → DayModel / Machine contracts
  → Snapshots & engines
  → API / UI consumers
```

См. [PERSONAL_INTELLIGENCE_LAYER.md](./PERSONAL_INTELLIGENCE_LAYER.md) §2 — слой **1a** после Reference taxonomy.

---

## 12. Changelog

- **1.0 (2026-05-31)** — шесть уровней, nine-field template, creation methods, entity registry v1, filling policy, data-first freeze rule.

---

*При добавлении сущности или смене creation/update policy — bump версию и строка в PRODUCT_EXECUTION_TRACKER.*
