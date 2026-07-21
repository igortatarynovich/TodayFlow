# Personal Model → Experiences wiring audit (P1) — 2026-07-21

**Статус:** P1 implementation in progress — `experience_contract_assembler_v0` + Consistency Tests  
**Цель:** закрыть **Source of Interpretation** — единый способ читать личность в Experiences.  
**Не цель:** новый Product Principle, C3 quality, rename API (P2 hygiene).

**Связь:** [PERSONAL_MODEL_CODE_COMPLIANCE_2026-07-21.md](./PERSONAL_MODEL_CODE_COMPLIANCE_2026-07-21.md) (P0) · Product Model · PIL

Формат: **канон → факт → нарушение → минимальный fix**.

---

## 0. Главный вывод

> **Formal single source without a shared contract assembler still produces divergent understanding.**

| Этап | Проблема |
|------|----------|
| **До P0** | Модули могли **пересобрать** человека (LLM-on-read) |
| **После P0** | Все **читают** один Snapshot |
| **P1 (сейчас)** | Каждый **по-своему выбирает**, какие части Snapshot важны |

Это не баг хранения. Это **Source of Interpretation**.

Классическая ловушка: единая БД · единый Snapshot · единый hash — и четыре клиента собирают четыре представления объекта. Через полгода они живут собственной жизнью. Именно поэтому Today, Tarot и Compatibility начинают «говорить разными голосами», даже когда SoT формально один.

**C3 не начинать**, пока Experiences не сидят на одном Experience Contract → allowlist-проекциях. Иначе качество портрета смешивается с маршрутизацией данных.

---

## 0.1 Матрица доказательств (факт после P0)

| Вопрос | Должно быть | Факт |
|--------|-------------|------|
| Вход Experience | проекция **одного** Experience Contract | каждый модуль режет CoreProfile сам |
| Кто собирает контракт | один assembler (не знает Today/Tarot/Compat) | ≥4 независимых сборщика |
| Кто режет поля | allowlist на Experience | ad-hoc / широкий dump / dead wiring |
| Provenance | snapshot_id / hash / version | Today/Tarot OK-ish; Compat partial |
| Без snapshot | baseline/shell, без rebuild | **OK** (P0) |
| Лог | slice fingerprint + source_depth | частично / нет |

---

## 1. Карта сборщиков (факт)

| Assembler | Файл | Кто вызывает | Что отдаёт |
|-----------|------|--------------|------------|
| `build_cached_or_baseline` / Snapshot payload | `core_profile.py` | API read-path | Полный CoreProfile dict |
| `_core_context_for_narrative` | `today_narrative.py` | `day_story_wire_v1` | Slim `user_core` для day_story |
| `build_visible/internal_profile_slice_v0` | `profile_prompt_slices_v0.py` | legacy narrative | visible/internal slices |
| `select_profile_context` | `profile_engine/selector.py` | почти только debug preview | ProfileSelectorOutput |
| `build_compact_user_model_v0` | `compact_user_model_v0.py` | account GET | CUM — **Experiences не читают** |
| Compat ad-hoc | `compatibility.py` | signs/dynamics | sun, hash, life_path |
| Orchestrator baseline | `interpretation_orchestrator.py` | Tarot context | consistency (часто мёртвый для answer) |

---

## 2. Today

| | Факт |
|--|------|
| Вход | Snapshot/shell → `_core_context_for_narrative` → day_story |
| Assembler | локальный, знает про narrative |
| Поля | широкий prune interpretation/living — не allowlist |
| Contract styles | `decision_style` / `conflict_style` из `profile_contract_v1` **не** канонический вход |
| Provenance | snapshot_id в day fingerprint + GenerationLog |
| Без snapshot | shell OK (P0) |

**Fix:** day_story читает только `ExperienceSlice(today)` из общего контракта.

---

## 3. Compatibility

| | Факт |
|--|------|
| Вход | engine + ad-hoc sun/hash; life_path из Personal Model (P0); `profile_a/b` ≠ гарантия Snapshot payload |
| Поля личности | нет стабильного conflict/communication/decision из одного контракта |
| Provenance | partial |

**Fix:** `profile_*_ready` только при Snapshot; enrichment получает `ExperienceSlice(compatibility)`.

---

## 4. Tarot — индикатор Source of Interpretation

| | Факт |
|--|------|
| Вход | полный CoreProfile в `POST /tarot/spread/context` |
| Synthesis | `compose_question_first_reading` **принимает** `core_profile` / `consistency` и **почти не использует** |
| Цена | сложность и payload за данные, которые не влияют на ответ |

Это не только dead wiring. Это сигнал, что Tarot **вырос отдельно** от Product Model: система платит за «персонализацию», которой нет. Такие места чаще всего дают ощущение «разные голоса» между разделами.

**Fix:** Tarot synthesis **обязан** принимать и использовать `ExperienceSlice(tarot)`; мёртвые аргументы убрать или подключить. Тест: без slice / с изменённым decision_style меняется вход синтеза (не обязательно LLM-текст).

---

## 5. Целевая архитектура P1

Разница с «assembler сразу режет под Today» принципиальна: **assembler не знает Experiences**.

```
CoreProfileSnapshot          ← Source of Truth (P0)
        ↓
Experience Contract          ← канонический контракт личности для всех Experiences
   (experience_contract_assembler_v0)
        ↓
ExperienceSlice              ← проекция allowlist'ом конкретного Experience
   today | compatibility | tarot | (practices…)
        ↓
Today · Compatibility · Tarot
```

| Слой | Отвечает на | Знает ли про Today? |
|------|-------------|---------------------|
| **Snapshot** | Что сохранено о человеке? | нет |
| **Experience Contract** | Какой **единый** набор полей личности доступен Experiences? | **нет** |
| **ExperienceSlice** | Какие поля **нужны этому** Experience? | да (allowlist only) |
| **Experience LLM/engine** | Что означает ситуация области для known person? | да |

### Experience Contract (черновик полей — код, не новый канон-файл)

Стабильные входные поля (не тексты LLM-ответа Experience):

| Поле | Назначение |
|------|------------|
| `decision_style` | как выбирает |
| `conflict_style` | как держит напряжение |
| `communication_style` | как говорит |
| `motivation` / motivation_pattern | что двигает |
| `energy_source` / energy_pattern | откуда ресурс |
| `helps` | опоры |
| `life_path`, `sun_sign`, `rhythm` | calc identity |
| `identity_line` | одна короткая линия (не полный портрет) |
| provenance | `snapshot_id`, `profile_hash`, `profile_version`, `source_depth`, `generated_from_snapshot` |

Assembler заполняет контракт из Snapshot/shell **один раз**.  
Allowlist Today / Compat / Tarot только **выбирает подмножество** + добавляет `experience_id` + `experience_slice_fingerprint`.

Запрещено в Experiences: полный `interpretation` dump, произвольный living JSON, локальный пересчёт life_path, локальная «интерпретация базового профиля».

### Лог (обязательные ключи)

`core_profile_snapshot_id` · `profile_hash` · `profile_version` · `generated_from_snapshot` · `source_depth` · `experience_id` · `experience_slice_fingerprint`

---

## 6. Experience Consistency Tests (новый класс)

Не snapshot-тесты UI. Не LLM-текст. **Входной контракт** во всех Experiences.

На одном и том же Snapshot (или fixture shell) собрать slices для `today`, `compatibility`, `tarot` и проверить равенство полей контракта:

| Поле | Правило |
|------|---------|
| `decision_style` | identical across Experiences |
| `conflict_style` | identical |
| `communication_style` | identical |
| `motivation` (или motivation_pattern) | identical |
| `energy_source` (или energy_pattern) | identical |
| provenance `profile_hash` / `snapshot_id` | identical |

**Fail**, если хоть одно поле расходится между Today и Compatibility (и т.д.).

Дополнительно:

- без Snapshot → только shell-поля; нет скрытого portrait rebuild;  
- Tarot: synthesis pipeline получает непустой slice и падает/флагится, если slice отброшен;  
- allowlist: Today slice не содержит полей вне today-allowlist.

Это ценнее большинства snapshot/UI тестов для удержания Source of Interpretation.

---

## 7. Rename debt (P2 hygiene, не blocker)

`CoreProfileService.build()` по умолчанию **читает**. Имя провоцирует LLM-on-read.

Позже: `get_or_baseline()` / `publish_snapshot()`; `build` → deprecated alias.

---

## 8. План работ (порядок не менять)

### Серия аудитов → реализация

| # | Этап | Смысл |
|---|------|--------|
| 1 | **P0** | убрать генерацию с read-path — **DONE** |
| 2 | **P1** | единый Source of Interpretation (Contract → Slice) — **этот документ** |
| 3 | **C3** | качество модели личности (лишние LLM, память, разделы ≠ один текст) |
| 4 | **Telemetry** | подтверждение поведением реальных пользователей |

### P1 implementation steps

1. `experience_contract_assembler_v0` → **Experience Contract** (без knowledge о Today). — **DONE**  
2. Allowlist projectors → `ExperienceSlice(today|compatibility|tarot)`. — **DONE**  
3. Wire day_story → slice(today); удалить `_core_context_for_narrative`. — **DONE**  
4. Wire Compat → slice(compatibility); Snapshot-gated `profile_*_ready`. — **DONE**  
5. Wire Tarot synthesis → slice(tarot); `profile_lens` из slice. — **DONE**  
6. Лог: slice fingerprint + source_depth. — **DONE** (day_story / tarot / compat personalized)  
7. **Experience Consistency Tests** (§6). — **DONE** (`test_experience_consistency_v0.py`)  
8. **Только потом C3.**

### Что C3 сможет спросить только после P1

| Тема | Вопрос |
|------|--------|
| **A. Число LLM** | Почему 4 шага портрета — может 2 или 1? |
| **B. Память** | Profile использует предыдущие знания, или каждый раз «красивый с нуля»? |
| **C. Свой вопрос раздела** | Не один и тот же «ты долго думаешь» в decision / conflict / relationships |

Пока Experiences режут Snapshot по-разному, ответы A–C смешаны с wiring.

---

## 9. Что сознательно не делать

- Не плодить новый Core Principle / параллельный канон.  
- Не начинать C3 как главный трек до Consistency Tests green.  
- Не второй Snapshot schema.  
- Не «улучшать голос» Profile, пока Source of Interpretation не один.

---

## Changelog

| Дата | |
|------|--|
| 2026-07-21 | P1 wiring audit: multiple assemblers; Tarot ignores profile |
| 2026-07-21 | Усиление: главный вывод Source of Interpretation; слой Experience Contract; Experience Consistency Tests; порядок P0→P1→C3→Telemetry |
| 2026-07-21 | Implemented `experience_contract_assembler_v0`; Today/Compat/Tarot on slices; Consistency Tests green; removed `_core_context_for_narrative` |
