# TL-0 — Language Calibration

**Статус:** `IN_PROGRESS`  
**Канон:** [TODAY_LANGUAGE_V1.md](./TODAY_LANGUAGE_V1.md) v1.1

| Фаза | Артефакт | Статус |
|------|----------|--------|
| **TL-0A** | Сырой корпус | ✅ fixtures · ✅ `api_live` (323 logs → 2080 phrases) |
| **TL-0B** | Авто-теги | ✅ |
| **TL-0C.1** | Анти-паттерны (повторяющиеся провалы) | ✅ [TODAY_LANGUAGE_ANTI_PATTERNS_V0.md](./TODAY_LANGUAGE_ANTI_PATTERNS_V0.md) |
| **TL-0C.2** | Сильные patterns + «почему работает» | ✅ [TODAY_LANGUAGE_STRONG_PATTERNS_V0.md](./TODAY_LANGUAGE_STRONG_PATTERNS_V0.md) |
| **TL-0C.3** | Ручная разметка 30+30 | ⬜ **IN_PROGRESS** (batch_1–3: 45 api_live) |
| **TL-0C.4** | Anchor hypothesis validation | ✅ 60 api_live — count gate **REFUTED**; role model H2 |
| **TL-0C.5** | RAT phase 2 | ⬜ **PR2 ∥ RAT** · dependency map + **RRM** · [TODAY_RAT_VALIDATION_V0](./TODAY_RAT_VALIDATION_V0.md) · **no platform layer** |
| **TL-1** | Code gate | **BLOCKED** |

**Ключевое число:** `323 generation logs → 2080 фраз` — достаточный объём для поиска **закономерностей**, не для немедленных score.

**Скрипты:** `export_today_generation_logs.py` · `today_language_corpus_v0.py` · `today_language_patterns_v0.py`

**Machine draft (TL-0C.1/0C.2):** [datasets/TODAY_LANGUAGE_PATTERNS_V0.json](./datasets/TODAY_LANGUAGE_PATTERNS_V0.json)

---

## Порядок TL-0C (обновлён)

**Не начинать с score 30+30.** Сначала паттерны, потом разметка.

```
TL-0A/0B  corpus + auto-tags
    ↓
TL-0C.1   10–20 анти-паттернов (типы провалов, не отдельные фразы)
    ↓
TL-0C.2   сильные паттерны + «почему работает» (не score)
    ↓
TL-0C.3   ручная разметка 30 плохих + 30 хороших/пограничных из api_live
    ↓
TL-0C.4   anchor validation (60 api_live) — count gate refuted; role model H2
    ↓
TL-0C.5   Internal Pattern Library (H3) — **dataset expansion PAUSED**
    ↓
TL-1      code gate (BLOCKED — после IP Library sign-off)
```

---

## TL-0C.1 — поиск повторяющихся провалов

**Цель:** не оценивать отдельные фразы. Искать **повторяющиеся типы** плохих фраз.

| Тип | Название | Суть |
|-----|----------|------|
| **A** | Псевдоконкретика | «Ситуация начнёт проясняться» — сцена вроде есть, человек ничего не видит |
| **B** | Универсальная мудрость | «Не всё требует немедленного ответа» — подходит любому |
| **C** | Подмена конкретики эмоцией | «Прилив уверенности» — эмоция есть, сцены нет |
| **D** | Фальшивая конкретика | «Неожиданный разговор изменит многое» — кажется конкретным, но универсально |

**Deliverable:** 10–20 именованных анти-паттернов с 3–5 примерами каждый — editorial, не авто-score.

**Machine draft:** `today_language_patterns_v0.py` → [TODAY_LANGUAGE_PATTERNS_V0.json](./datasets/TODAY_LANGUAGE_PATTERNS_V0.json)

**Editorial classifier:** [TODAY_LANGUAGE_ANTI_PATTERNS_V0.md](./TODAY_LANGUAGE_ANTI_PATTERNS_V0.md) — AP-001–008

**Strong pattern library:** [TODAY_LANGUAGE_STRONG_PATTERNS_V0.md](./TODAY_LANGUAGE_STRONG_PATTERNS_V0.md) — SP-001–008

Первый прогон (2026-06-23, ~2023 narrative phrases):

| type_id | count | share |
|---------|------:|------:|
| Z_untyped_weak | 811 | ~40% |
| C_emotion_without_scene | 179 | ~9% |
| A_pseudo_concreteness | 87 | ~4% |
| B_universal_wisdom | 49 | ~2.5% |
| D_fake_concreteness | 39 | ~2% |

**Важно:** TL-0B `likely_good` часто совпадает с типом **D** («В любви сделай шаг к разговору»). Это аргумент против раннего TL-1.

---

## TL-0C.2 — сильные паттерны («почему работает»)

**Цель:** не score. Вопрос: **почему эта фраза работает?**

Пример эталона:

> Кто-то может написать вам именно тогда, когда вы уже решили, что ответа не будет.

Работает не из-за «сообщения», а из-за: ожидание · эмоция · узнаваемая ситуация · интрига.

**Deliverable:** 10–20 сильных паттернов с полем `why_works` — см. [TODAY_LANGUAGE_STRONG_PATTERNS_V0.md](./TODAY_LANGUAGE_STRONG_PATTERNS_V0.md) SP-001–008.

---

## TL-0C.3 — ручная разметка (schema v0.3)

**Файл:** [datasets/TODAY_LANGUAGE_CALIBRATION_V0.json](./datasets/TODAY_LANGUAGE_CALIBRATION_V0.json) · `schema_version: 0.3`

### Зачем v0.2 → v0.3

`score` не отвечает на главный вопрос редактора.

| Фаза | Вывод |
|------|--------|
| **batch_1** | `core_scene` часто есть у слабых фраз — слабость часто в **отсутствии ставки** |
| **batch_3** | **Keep/exemplar без ставки** — фокус, перегруз, объект, дедлайн. Гипотеза «ставка обязательна» **не выдержала** → RULE_004 = анкоры ([TODAY_ANCHOR_TYPES_V0](./TODAY_ANCHOR_TYPES_V0.md)) |

| Поле | Смысл |
|------|--------|
| `corpus_id` | `corp-XXXX` из corpus — для `api_live` **обязателен** |
| `text` | Исходная фраза |
| `score` | 1–10 — сила формы, не решение |
| `reason` | Почему такой score |
| **`editorial_decision`** | `keep` · `rewrite` · `reject` · `exemplar` |
| `anti_pattern_id` | AP-001…008 |
| `strong_pattern_id` | SP-001…008 |
| **`core_scene`** | id из `core_scenes.catalog` |
| **`stake_type`** | id из `stake_types.catalog` — v0.3; **усилитель**, не единственный критерий |
| **`anchor_types`** | id[] из `anchor_types.catalog` — **v0.5**: `AT-001`…`AT-006` ([TODAY_ANCHOR_TYPES_V0](./TODAY_ANCHOR_TYPES_V0.md)) |
| **`hypothesis_bucket`** | v0.4 batch_4: `no_anchor` \| `scene_only` \| `object_no_stake` |
| `text_improved` | Обязателен для `rewrite` |

### editorial_decision

| Значение | Смысл | Пример |
|----------|--------|--------|
| **keep** | Оставить как есть | cal-002 |
| **rewrite** | Идея / scene ok, форма плохая | cal-016: score **4**, не reject |
| **reject** | Выкинуть | cal-017: rubric |
| **borderline** | Сцена есть, зацепки слабые — не keep, не reject | batch_4 hypothesis |
| **exemplar** | Образец библиотеки | cal-018 |

### stake_type (v0.3)

| id | Что означает |
|----|--------------|
| `none` | Ставки нет |
| `fear_of_answer` | Страх услышать ответ |
| `waiting_too_long` | Слишком долго ждали |
| `repeated_avoidance` | Снова избегаете / обходите тему |
| `emotional_cost` | Эмоциональная цена молчания |
| `missed_opportunity` | Можно упустить шанс |
| `relationship_tension` | Напряжение в отношениях |
| `overload_cost` | Цена перегруза |
| `self_betrayal` | Снова против себя |

Не обязательно идеально — после **60+** станет видно, какие ставки реально работают.

### anchor_types (v0.5)

Каталог **[TODAY_ANCHOR_TYPES_V0.md](./TODAY_ANCHOR_TYPES_V0.md)** — ids `AT-001`…`AT-006`.

| id | Тип |
|----|-----|
| AT-001 | Scene — конкретная ситуация |
| AT-002 | Stake — цена / напряжение |
| AT-003 | Object — отчёт, задача, встреча… |
| AT-004 | Decision — выбор, действие |
| AT-005 | Relationship — человек, связь |
| AT-006 | Internal — обещание себе, откладывание, перегруз |

**Правило (гипотеза):** достаточно **одного сильного** анкора; не нужны все типы. `stake_type=none` совместим с AT-003 + AT-006.

### core_scene

Короткий id сцены — **важнее отдельной фразы** для будущей генерации.

| Фраза (смысл) | `core_scene` |
|---------------|--------------|
| Человек напишет, когда перестали ждать | `delayed_message` |
| Разговор, который откладывали | `postponed_conversation` |
| Старое решение выглядит иначе | `reassessing_decision` |
| Возвращение к старой теме | `recurring_topic` |

Полный стартовый каталог (17 id) — в `core_scenes.catalog` в calibration JSON. После **60+** разметок ожидается **каталог сцен** как основа генерации Today — важнее SP и AP.

### Milestone TL-1

| Bucket | Min | Критерий |
|--------|-----|----------|
| Плохие | **30** | `api_live`, score 1–4, `editorial_decision` ∈ reject/rewrite/borderline |
| Хорошие / borderline | **30** | score 7–10 или 4–6 с `keep`/`exemplar` |
| **Все 60+** | | `editorial_decision` + `core_scene` + `anchor_types` (v0.4) |
| **Pre-TL-1** | | Anchor analysis по batch_4 — stake как правило или усилитель |

**Не идти в TL-1 сразу после 60.** Сначала TL-0C.4: таблица reject/keep/borderline × scene/stake/object/action.

Очередь: `review_slices` в corpus + anti/strong classifiers.

**Seed:** 18 editorial + **45 api_live** (batch_1–3). **batch_4:** +15 → 60 api_live.

### TL-0C.4 batch_4 — anchor hypothesis test

**15 × api_live** — контролируемый эксперимент, не «добивание числа».

| hypothesis_bucket | editorial_decision | count | Критерий |
|-------------------|-------------------|------:|----------|
| `no_anchor` | reject | 5 | без сцены, ставки, объекта |
| `scene_only` | borderline | 5 | сцена/relationship, без stake и без object |
| `object_no_stake` | keep | 5 | объект и/или action, `stake_type=none` |

Каждая запись: `anchor_types[]` + `hypothesis_bucket`.

**После batch_4 проверить:**

| Признак | reject | borderline | keep |
|---------|--------|------------|------|
| Scene | ? | ✓ | ? |
| Stake | ? | ✗ | ✗ |
| Object | ✗ | ✗ | ✓ |
| Action | ✗ | ? | ✓ |

→ Решение: `stake_anchor` как **RULE** или как **усилитель** в генераторе.

Каталог: [TODAY_ANCHOR_TYPES_V0.md](./TODAY_ANCHOR_TYPES_V0.md)

**Гипотеза gate (pre-TL-1):** проверена на **60 api_live** — см. [TL-0C.4 validation](#tl-0c4-validation--60-api_live) ниже.

### TL-0C.4 batch_4 summary (2026-06-23)

**15 × api_live** — anchor hypothesis test (cal-064–078). Milestone **60 api_live** достигнут; **TL-1 не открывается** до anchor analysis.

| hypothesis_bucket | editorial_decision | count |
|-------------------|-------------------|------:|
| `no_anchor` | reject | 5 |
| `scene_only` | borderline | 5 |
| `object_no_stake` | keep | 5 |

| anchor_types (batch_4) | count |
|--------------------------|------:|
| AT-001 | 5 |
| AT-003 | 5 |
| AT-005 | 3 |
| AT-004 | 4 |
| AT-006 | 3 |

**Проверка gate hypothesis (batch_4):**

| decision | avg `anchor_types` |
|----------|-------------------:|
| reject | 0.0 |
| borderline | 1.6 |
| keep | 2.4 |

→ На batch_4 alone паттерн совпадал; **полная проверка после ретро batch_1/2** — ниже.

---

### TL-0C.4 validation — 60 api_live

**2026-06-23:** ретро `anchor_types[]` на batch_1 (cal-019–033) + batch_2 (cal-034–048).

#### Матрица: anchor count × editorial_decision

| Anchors | Reject | Rewrite | Borderline | Keep | Exemplar |
|--------:|-------:|--------:|-----------:|-----:|---------:|
| **0** | 9 | 3 | 0 | 0 | 0 |
| **1** | 1 | 1 | 2 | 2 | 0 |
| **2** | 0 | 11 | 3 | 12 | 3 |
| **3+** | 0 | 5 | 0 | 5 | 3 |

**Строгая гипотеза** (0→reject, 1→borderline, 2+→keep/exemplar): **56.7%** (34/60) — **REFUTED**.

**Главный контрпример:** **16 rewrite с 2+ анкорами** — AT-004 + AT-005 (generic love) даёт count≥2, но AP-004 rewrite.

#### Anchor type: reject% vs keep% (keep + exemplar)

| Anchor | n | Reject % | Keep % | Rewrite % |
|--------|--:|---------:|-------:|----------:|
| AT-001 Scene | 16 | 0 | 19 | 50 |
| AT-002 Stake | 4 | 0 | 75 | 25 |
| AT-003 Object | 13 | **0** | **100** | 0 |
| AT-004 Decision | 30 | 0 | 63 | 37 |
| AT-005 Relationship | 19 | 0 | 16 | **68** |
| AT-006 Internal | 22 | 5 | **68** | 27 |

**AT-006 подтверждён** — почти AT-003 по силе (откладывание, перегруз, «надо собраться»).  
**AT-005** — rewrite trap (generic partner/родные).

#### Top combinations

| Combo | n | типично |
|-------|--:|---------|
| AT-003 + AT-004 | 7 | keep |
| AT-004 + AT-005 | 6 | **rewrite** |
| AT-003 + AT-004 + AT-006 | 5 | keep / exemplar |
| AT-001 + AT-005 | 5 | borderline / rewrite |
| AT-004 + AT-006 | 4 | keep |

**TL-1 BLOCKED.** Следующий шаг: **anchor role model** (S+P vs S+T), не count-only.

#### Anchor Utility Matrix

| Anchor | class | Exemplar % | Keep+Ex % | Rewrite trap % |
|--------|-------|----------:|----------:|---------------:|
| AT-003 | structural | **38.5** | **100** | **0** |
| AT-006 | psychological | 18.2 | 68.2 | 27.3 |
| AT-004 | transitional | 16.7 | 63.3 | 36.7 |
| AT-001 | structural | 0 | 18.8 | 50.0 |
| **AT-005** | structural | **0** | 15.8 | **68.4** |

#### HYPOTHESIS H2 — роль анкоров

**AT-006** — главный psychological carrier (откладывание, перегруз > «партнёр»).

| Combo class | n | Keep+Ex % | Rewrite % |
|-------------|--:|----------:|----------:|
| **AT-003 + AT-006** | 6 | **100** | 0 |
| S + P | 15 | 60 | 40 |
| S + T (no psych) | 16 | 50 | **50** |
| **AT-004 + AT-005** | 11 | 18 | **82** |

**AI-банальность:** AT-004 + AT-005 («сделай шаг к разговору с партнёром») — 2 анкора формально, **82% rewrite**.

**Классы:** Structural (AT-001,003,005) · Psychological (AT-002,006) · Transitional (AT-004).

JSON: `stats.tl_0c_4_hypothesis_validation` · `internal_patterns`

---

### TL-0C.5 — RAT phase 2 *(dependency map + RRM)*

**PR2 ∥ RAT:** PR2 = PIM **может накапливать** · RAT = **что стоит** объяснять / хранить для узнавания.

**North star *(platform v4):*** «**Что добывать в PIM?**» vs «**что хранить?**» (C17) · **RRM = candidate KIP layer** · C18 freeze.

**Два deliverable RAT:** dependency map (текст) · **RRM** (знания · **не** побочный продукт).

**Dataset:** [TODAY_RAT_VALIDATION_V0](./TODAY_RAT_VALIDATION_V0.md) · n=23 · `phase_2_class_matrix` in JSON

**Два артефакта phase 2:** (1) dependency map / stack A–E · (2) **RRM** — knowledge type → recognition relevance · **Knowledge Type Catalog** (8 classes) · survivor→class correlation.

**Главный вопрос n=40:** какие **классы знаний** стоят за survivor — не «кто победил в ablation». **AR-004:** density illusion · C17 ∩ RRM.

**C17 vs RRM:** [DECISION_RELEVANCE_V1](./DECISION_RELEVANCE_V1.md) = решения · RRM = «это про меня» — **независимые оси** curation.

**Порядок:** `PR2 ∥ RAT (→n=40) → RRM → Observability → ROI → Reusability → KIP sign-off`

**AR-001…010:** no platform layer · **KIP hypothesis** · AR-004 density · AR-008 high-rec/high-cost · **AR-009** high ROI ≠ store · AR-010 stop condition (observable vs theory)

### TL-0C.3 batch_1 summary (2026-06-23)

Только `source=api_live`, показательные (не идеальные).

**editorial_decision**

| decision | count |
|----------|------:|
| reject | 5 |
| rewrite | 5 |
| keep | 4 |
| exemplar | 1 |

**core_scene (batch_1)**

| core_scene | count |
|------------|------:|
| none | 3 |
| domain_rubric_leak | 2 |
| postponed_conversation | 4 |
| pseudo_clarity | 1 |
| self_promise_procrastination | 3 |
| inner_conflict_logic_vs_feeling | 1 |
| unresolved_conflict | 1 |

**Вывод batch_1:** reject — без сцены; rewrite/keep — scene есть, **stake часто none**.

### TL-0C.3 batch_2 (2026-06-23)

**15 × api_live, только `rewrite`** — золото для будущего генератора (идея ok, форма испорчена).

Приоритет отбора: likely_good+AP-004 · trigger без stake · love/conversation surfaces.

| stake_type (batch_2) | count |
|------------------------|------:|
| repeated_avoidance | 6 |
| relationship_tension | 4 |
| emotional_cost | 4 |
| missed_opportunity | 1 |

Все cal-034–048: `text_improved` + `core_scene` + `stake_type` + AP/SP.

**Seed:** 48 entries total (18 seed + 15 batch_1 + 15 batch_2).

### TL-0C.3 batch_3 (2026-06-23)

**15 × api_live, только `keep` / `exemplar`** — верхняя граница качества для gate (что нельзя случайно зарезать).

Критерии отбора: score ≥ 6 · `core_scene` ≠ none · разнообразие сцен (не только love/разговоры).

| editorial_decision | count |
|--------------------|------:|
| exemplar | 5 |
| keep | 10 |

| core_scene (batch_3) | count |
|----------------------|------:|
| self_promise_procrastination | 11 |
| agreeing_against_self | 2 |
| reassessing_decision | 1 |
| recurring_topic | 1 |

| stake_type (batch_3) | count |
|----------------------|------:|
| overload_cost | 5 |
| missed_opportunity | 4 |
| none | 4 |
| emotional_cost | 1 |
| self_betrayal | 1 |

**Фокус batch_3:** короткие фразы · work/focus/overload/money · без яркой эзотерики · 4× `stake_type=none` как допустимый keep без сильной ставки.

**Exemplar (cal-049–053):** corp-0939 (короткая, score 9) · corp-0053 (work/social) · corp-0844 · corp-0842 (презентация/дедлайн) · corp-1843 (money/reassessing).

**api_live после batch_3:** 45 total — rewrite 20 · reject 5 · keep 14 · exemplar 6 (keep+exemplar **20** cumulative).

**Вывод batch_3 для RULE_004:** keep/exemplar **без ставки** — достаточно **AT-003 + AT-006** (object + internal). Разметка cal-049–063: `anchor_types[]` добавлена.

**Seed:** 63 entries total (18 seed + 45 api_live).

### После 60+

- каталог **плохих форм** (AP + reject/rewrite);
- каталог **сильных форм** (SP + exemplar);
- каталог **сцен** (`core_scene`) + **ставок** (`stake_type`) — основа генерации.

---

## TL-0A — экспорт и corpus

### Подключение к БД

Если `localhost:5432` — локальный Postgres (не docker `todayflow`):

```bash
docker run --rm --network todayflow_default \
  -v "$PWD":/workspace -w /workspace \
  -e DATABASE_URL=postgresql+psycopg://postgres:postgres@postgres:5432/todayflow \
  python:3.12-slim bash -c \
  'pip install -q sqlalchemy "psycopg[binary]" && PYTHONPATH=backend/src python backend/scripts/export_today_generation_logs.py --dry-run --sample 100'
```

### Экспорт + corpus + patterns

```bash
# export (пример)
docker run --rm --network todayflow_default \
  -v "$PWD":/workspace -w /workspace \
  -e DATABASE_URL=postgresql+psycopg://postgres:postgres@postgres:5432/todayflow \
  python:3.12-slim bash -c \
  'pip install -q sqlalchemy "psycopg[binary]" && PYTHONPATH=backend/src python backend/scripts/export_today_generation_logs.py --out docs/datasets/raw/generation_logs_ru_v0.jsonl'

PYTHONPATH=backend/src backend/.venv/bin/python backend/scripts/today_language_corpus_v0.py --logs-dir docs/datasets/raw

PYTHONPATH=backend/src backend/.venv/bin/python backend/scripts/today_language_patterns_v0.py
```

Raw JSONL **не коммитятся** — `.gitignore`: `docs/datasets/raw/*.jsonl`.

---

## TL-0B — авто-теги

`no_scene` · `too_generic` · `abstract` · `has_scene` · `has_trigger` · `emotional_hook` · `likely_good`

Очередь: `review_slices` в [TODAY_LANGUAGE_CORPUS_V0.json](./datasets/TODAY_LANGUAGE_CORPUS_V0.json).

**Ограничение:** auto-tags — **не** замена TL-0C.1; тип D обходит `likely_good`.

---

## Changelog

| Дата | Изменение |
|------|-----------|
| 2026-06-23 | v2.0 — Reusability axis; AR-009 Knowledge as Asset Illusion; platform vs feature; AR-010 (ex-009 meta) |
| 2026-06-23 | v1.9 — Knowledge ROI; Acquisition Cost; Observability; AR-008; post-n=40 KIP gate |
| 2026-06-23 | v1.8 — Discovery relevance hypothesis; AR-005; 3-axis KIP |
| 2026-06-23 | v1.6 — RRM vs C17; PR2∥RAT |
| 2026-06-23 | Phase 2 RAT n=23; recognition_mechanism; class matrix |
| 2026-06-23 | v1.3 — variant E bundle; RAT ablation ladder; dependency map |
| 2026-06-23 | v1.1 — RPT; variants A–D; stop «IPL engine» |
| 2026-06-23 | H4 editorial SUPPORTED + limitation; H5 Self-Verification candidate |
| 2026-06-23 | H4 Observable; Class R/G; H3 narrowed |
| 2026-06-23 | batch_4: 15 anchor hypothesis (cal-064–078); 60 api_live; TL-1 blocked |
| 2026-06-23 | batch_3: 15 keep/exemplar api_live (cal-049–063); 45 api_live cumulative |
| 2026-06-23 | Schema v0.3: stake_type; batch_2: 15 rewrite-only (cal-034–048) |
| 2026-06-23 | TL-0C.3 batch_1: 15 api_live (cal-019–033) |
| 2026-06-23 | TL-0C.1 editorial classifier AP-001–008 → TODAY_LANGUAGE_ANTI_PATTERNS_V0.md |
| 2026-06-23 | api_live export: 323 logs; corpus 2919 unique (2080 generation_log) |
| 2026-06-23 | `--since`, `--sample`; docker network export note |
| 2026-06-23 | TL-0A/B scripts + corpus 841 (fixtures) |
