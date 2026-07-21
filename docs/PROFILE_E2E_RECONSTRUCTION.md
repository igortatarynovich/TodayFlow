# Profile End-to-End Reconstruction

**Status:** ACTIVE — сквозной этап (не UI redesign)  
**Started:** 2026-07-21  
**Parent canons:** [EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md](./EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md) · [PROFILE_CONTENT_CANON_V1.md](./PROFILE_CONTENT_CANON_V1.md) · [PR4_PROFILE_CANON.md](./PR4_PROFILE_CANON.md) · [UNDERSTANDING_PROGRESS_AND_DEPTH_CANON.md](./UNDERSTANDING_PROGRESS_AND_DEPTH_CANON.md) · [TODAYFLOW_VOICE_CANON.md](./content/TODAYFLOW_VOICE_CANON.md)

> **Запрет на этом этапе:** рисовать новый экран · переписывать промпты «на глаз» · чинить тексты без доказанной точки в цепочке · объяснять брак фразой «модель выдумала».

---

## Архитектурный принцип (жёстко)

> **Profile E2E рассматривает модель как ограниченный исполнитель проверяемого контракта.**  
> Вариативность формулировок допустима; вариативность смысла, структуры и фактических утверждений — нет.  
> **Любое несоответствие контракту считается дефектом архитектуры блока до тех пор, пока не доказано обратное.**

Категории «ошибка модели» / «модель выдумала» **не используются** как диагноз.

**Стабильность контракта означает:**

| Да | Нет |
|----|-----|
| Одинаковый набор допустимых смыслов | Буквально одинаковый текст при каждом запуске |
| Соответствие схеме ответа | Бесконечная подгонка prompt под verbatim identity |
| Отсутствие неподтверждённых утверждений | |
| Сохранение назначения блока | |
| Допустимая языковая вариативность | |

Если результат не соответствует ожиданиям, дефект находится в **архитектуре генерации**:

| Возможная причина | Класс дефекта |
|-------------------|---------------|
| Неверно определено назначение блока | `BLOCK_PURPOSE` |
| Для блока недостаточно данных | `INSUFFICIENT_DATA` |
| Неправильно собраны входные данные | `INPUT` |
| Неточно сформулирован промпт | `PROMPT` |
| Неправильно определена схема ответа | `RESPONSE_SCHEMA` |
| Некорректно работает валидация | `VALIDATION` |
| Генерация запущена при закрытом gate | `GENERATION_GATE` |
| Искажение при записи Snapshot | `SNAPSHOT` |
| Искажение при формировании API | `API` |
| Искажение при проекции во Frontend | `PROJECTION` |
| Блок показан, когда не должен | `UI_GATE` |

Единственные допустимые выводы по блоку:

1. **«Данный промпт стабильно генерирует результат, соответствующий контракту блока»** (смысл/схема/факты; не verbatim).  
2. **«Этот блок невозможно построить при текущем объёме данных — генерация не должна запускаться.»**

Запрещённый вывод: «иногда пишет хорошо, а иногда выдумывает».

### `block_eligibility` — обязательно до промпта

До запуска любого LLM-шага должен существовать ответ:

> **Имеет ли этот блок право существовать для данного пользователя?**

Проверка eligibility **раньше** генерации. Нет права → step не вызывается.  
Capture фиксирует `may_generate` vs `ran`.

### Продуктовый голос (рядом с архитектурой)

> Ни один пользовательский текст не описывает состояние системы.  
> Любой текст описывает человека, смысл данных или ценность следующего шага.

Канон: [TODAYFLOW_VOICE_CANON.md](./content/TODAYFLOW_VOICE_CANON.md) §0.05–§0.06 · весь TodayFlow.

### Порядок проектирования блока

```text
1. Назначение + вопрос пользователя
2. Разрешённые / запрещённые данные + min depth
3. block_eligibility / generation_gate
4. Точная задача для модели (только если gate открыт)
5. Схема ответа + критерии приёмки
6. Snapshot → API → UI (без искажений)
7. Публикация пользователю (голос: человек, не pipeline)
```

Нет паспорта → блока нет.  
Недостаточно данных → генерация **не запускается** (не «попроси не выдумывать»).  
Ответ ≠ паспорт → не публиковать; дорабатывать prompt/contract до стабильности.

**Passport template:** [audits/PROFILE_E2E_BLOCK_PASSPORT_TEMPLATE.md](./audits/PROFILE_E2E_BLOCK_PASSPORT_TEMPLATE.md)

### Пример: Patterns

Неправильно: ждать, что модель «не будет выдумывать recurring patterns при отсутствии living».

Правильно: блок recurring patterns = только **подтверждённые** повторы поведения → строится только при наличии данных → иначе step **не вызывается**.

Production-faithful pack должен это **доказать** (eligibility + raw + accept + UI), а не списывать на модель.

---

## Цель

Построить **один осмысленный Profile**, для которого по каждому пользовательскому элементу известны ответы паспорта (зачем → вопрос → данные → gate → calc/ruleset → prompt → expected → acceptance → Snapshot → API → UI → kitchen → missing/depth/tier).

Сначала — **полная карта текущей реальности**, без предположений.

---

## Артефакты этапа

| # | Artifact | Path | Status |
|---|----------|------|--------|
| 0 | Architecture principle + defect classes | this doc | **canon** |
| 0b | Block passport template | [audits/PROFILE_E2E_BLOCK_PASSPORT_TEMPLATE.md](./audits/PROFILE_E2E_BLOCK_PASSPORT_TEMPLATE.md) | **v0** |
| 0c | Block passport · `life_spheres` | [audits/PROFILE_E2E_BLOCK_PASSPORT_LIFE_SPHERES.md](./audits/PROFILE_E2E_BLOCK_PASSPORT_LIFE_SPHERES.md) | **PASS** Freeze — [PROFILE_CAPTURE_LIFE_SPHERES_FREEZE_ABC.md](./audits/PROFILE_CAPTURE_LIFE_SPHERES_FREEZE_ABC.md) |
| 0d | Deterministic projector · cues kitchen | [audits/PROFILE_LIFE_SPHERES_DETERMINISTIC_PROJECTOR_V0.md](./audits/PROFILE_LIFE_SPHERES_DETERMINISTIC_PROJECTOR_V0.md) | A/B + cue/trait kitchen — **not** user-copy SoT |
| 0e | Quality review · love/money/decisions | [audits/PROFILE_LIFE_SPHERES_QUALITY_REVIEW_V0.md](./audits/PROFILE_LIFE_SPHERES_QUALITY_REVIEW_V0.md) | projector baseline + synthesis wire Case A/B |
| 0f | Spheres synthesis passport | [audits/PROFILE_E2E_BLOCK_PASSPORT_SPHERES_SYNTHESIS.md](./audits/PROFILE_E2E_BLOCK_PASSPORT_SPHERES_SYNTHESIS.md) | **wired** — cues → prompt → validate → Snapshot |
| 0g | P5 Canonical Context Engine | [rfc/RFC_CANONICAL_CONTEXT_ENGINE_V0.md](./rfc/RFC_CANONICAL_CONTEXT_ENGINE_V0.md) · [audits/CONTEXT_ENGINE_P5_FIRST_SLICE.md](./audits/CONTEXT_ENGINE_P5_FIRST_SLICE.md) | **STOPPED** — keep thin in-use mapping only; no further slices |
| 1 | Pipeline map (registration → UI + alt paths) | [audits/PROFILE_E2E_PIPELINE_MAP.md](./audits/PROFILE_E2E_PIPELINE_MAP.md) | **v0** |
| 2 | Prompt registry (passports) | [audits/PROFILE_E2E_PROMPT_REGISTRY.md](./audits/PROFILE_E2E_PROMPT_REGISTRY.md) | **v0 — align to block passport** |
| 3 | Block map (every surface block) | [audits/PROFILE_E2E_BLOCK_MAP.md](./audits/PROFILE_E2E_BLOCK_MAP.md) | **v0 — current reality** |
| 3b | Block Freeze Matrix (ship-gate) | [audits/PROFILE_V1_BLOCK_FREEZE_MATRIX.md](./audits/PROFILE_V1_BLOCK_FREEZE_MATRIX.md) | **ACTIVE** — close one block at a time |
| 3c | Block passport · `identity` | [audits/PROFILE_E2E_BLOCK_PASSPORT_IDENTITY.md](./audits/PROFILE_E2E_BLOCK_PASSPORT_IDENTITY.md) | **PASS** — [PROFILE_CAPTURE_IDENTITY_FREEZE_A.md](./audits/PROFILE_CAPTURE_IDENTITY_FREEZE_A.md) |
| 4 | Sample pack through full pipeline | [audits/PROFILE_E2E_SAMPLE_PACK.md](./audits/PROFILE_E2E_SAMPLE_PACK.md) | **v0 — existing eval + gaps** |
| 4b | Production-faithful capture harness | [audits/PROFILE_PRODUCTION_CAPTURE_PACK.md](./audits/PROFILE_PRODUCTION_CAPTURE_PACK.md) | **IMPLEMENTATION** |
| 4c | Case A/B capture report | [audits/PROFILE_CAPTURE_CASE_AB_REPORT.md](./audits/PROFILE_CAPTURE_CASE_AB_REPORT.md) | **v0 — packs run** |
| 5 | Degradation points (architectural classes only) | capture packs + maps | **v0** |
| 6 | Missing-data matrix · trial/free/sub content plan | Understanding Progress canon + block map | partial |
| 7 | Target architecture + Screen Master rewrite | *later* | not started |
| 8 | Contract tests per layer | *later* | not started |
| 9 | Downstream Snapshot consumption proof | [PROFILE_AS_SOURCE_CONSUMPTION_AUDIT.md](./audits/PROFILE_AS_SOURCE_CONSUMPTION_AUDIT.md) | exists |

---

## Порядок работ (жёстко) — Profile v1 Freeze

```text
1. Block Freeze Matrix from production Profile V2   ← done
2. Pick one FAIL block (max Freeze impact)         ← identity
3. Close ONLY that block: passport → eligibility → capture →
   defects → prompt/contract/FE → Snap→API→UI → tests
4. Next block only after PASS or omit from production
```

**Запрет в этом slice:** новые engines · registries · RFC · общие слои · redesign всего экрана · target-блоки · старт Today / DailyState.

**Закрыто:** `identity` · `life_spheres` = **PASS**.  
**Следующий (рекомендован):** `character_patterns` — граница birth vs longitudinal. Только из [PROFILE_V1_BLOCK_FREEZE_MATRIX.md](./audits/PROFILE_V1_BLOCK_FREEZE_MATRIX.md), один за раз.

SoT capture: `run_production_capture_v0.py`.

---

## Definition of done (этап E2E — до Freeze)

Критерии **реконструкции** (карта + доказательства). Без них Freeze Checklist не открывается.

1. Каждый **production**-блок имеет **полный паспорт** (нет паспорта → нет блока).  
2. Каждый prompt привязан к паспорту блока и `block_eligibility` / generation gate.  
3. Есть ≥1 production-faithful pack на birth-only и longitudinal: eligibility → prompts → raw → validation → snapshot → API → UI.  
4. Для каждого расхождения выставлен **архитектурный** класс дефекта (не `MODEL`).  
5. Список устаревших путей с планом удаления.  
6. Доказано, что Experiences читают Snapshot, а не invent personality (или зафиксирован gap).  
7. Промпты / UI доведены до **стабильного контракта** или блок снят с production.

---

## Profile v1 Freeze Checklist

**Статус Freeze:** OPEN — не объявлять Profile v1 Canon, пока все пункты не `PASS`.  
**Смысл:** не «хорошо выглядит», а **можно выпускать**.  
**Объём v1:** только блоки, уже в production на Profile. Target-блоки из block map **не** входят в Freeze; они — отдельные будущие паспорта после Canon.

> **Принцип канона (Profile и весь TodayFlow):**  
> Канон — это не максимальное количество функций.  
> Канон — это состояние, в котором **существующие** функции **закончены**.

Любая работа по пунктам ниже допускается только если ответ «да» хотя бы на один вопрос: текст полезнее · блок понятнее · UI лучше.  
«Ещё один слой инфраструктуры» → **не делать** ([PRODUCT_TRUTH_FIRST.md](./PRODUCT_TRUTH_FIRST.md) · architecture-must-prove-value).

### 1. Product completeness

| # | Критерий | Доказательство | Status |
|---|----------|----------------|--------|
| 1.1 | Каждый production-блок имеет **утверждённый** паспорт | 1:1 с [audits/PROFILE_E2E_BLOCK_MAP.md](./audits/PROFILE_E2E_BLOCK_MAP.md) + отдельный passport file / секция | OPEN |
| 1.2 | Нет production-блоков без паспорта | audit block map × UI × Snapshot fields | OPEN |
| 1.3 | Нет паспортов без существующего production-блока | orphan passport = удалить или пометить `not shipped` | OPEN |

### 2. Data integrity

| # | Критерий | Доказательство | Status |
|---|----------|----------------|--------|
| 2.1 | Блок использует только **необходимые** данные (passport allow-list) | passport § inputs + capture `source_inputs` | OPEN |
| 2.2 | Источник каждого user-facing поля известен | field → Snapshot/API path в passport | OPEN |
| 2.3 | Нет дублирования расчётов одного смысла | один SoT на claim; FE/taxonomy merge без второго «источника правды» | OPEN |
| 2.4 | Нет временных / искусственных данных в production UI | нет filler, fake %, `?? catalog[0]` как персональное, mock timestamps | OPEN |

### 3. Prompt quality

| # | Критерий | Доказательство | Status |
|---|----------|----------------|--------|
| 3.1 | Каждый LLM-prompt блока проходит evaluation | production-faithful pack / Case A/B ([PROFILE_PRODUCTION_CAPTURE_PACK.md](./audits/PROFILE_PRODUCTION_CAPTURE_PACK.md)) | OPEN |
| 3.2 | Контракт стабилен | raw → validate → Snapshot соответствует passport; иначе не publish | OPEN |
| 3.3 | Известные дефекты закрыты **или** явное limitation в passport/kitchen (не тихий брак) | defect log с классом; UI не врёт | OPEN |

### 4. Snapshot / API

| # | Критерий | Доказательство | Status |
|---|----------|----------------|--------|
| 4.1 | Snapshot соответствует UI (4th capture proof) | pack: Snapshot field → API → UI string без искажения | OPEN |
| 4.2 | API Profile не отдаёт временные поля как контракт | inventory deprecated / `tmp_*` / unused | OPEN |
| 4.3 | Нет legacy-полей «ради совместимости», если никто не читает | consumers audit; unused → remove or internal-only | OPEN |

### 5. UX quality (ship-gate, не вкус)

| # | Критерий | Доказательство | Status |
|---|----------|----------------|--------|
| 5.1 | Ценность блока ясна без знания кухни | passport «user question» ↔ видимый смысл блока; Voice §0.05–§0.06 | OPEN |
| 5.2 | В UI нет внутренних терминов | запрет user-facing: eligibility, synthesis, engine, funnel, snapshot, projector, gate, fingerprint, pipeline, … | OPEN |
| 5.3 | Тексты не повторяют один смысл в соседних блоках | sample/capture contrast; dedup Character / Direction | OPEN |

### 6. Production readiness

| # | Критерий | Доказательство | Status |
|---|----------|----------------|--------|
| 6.1 | Нет TODO/FIXME, влияющих на Profile production path | grep Profile BE/FE path; leftover → ticket вне Freeze или fix | OPEN |
| 6.2 | Нет заглушек как «готового» контента | Product Truth First antipatterns | OPEN |
| 6.3 | Нет boilerplate / временных веток «потом уберём» | code review Freeze pass | OPEN |
| 6.4 | Нет экранов / секций «в разработке» на production Profile | UI audit | OPEN |

### 7. Freeze (после PASS по §1–§6)

| # | Действие |
|---|----------|
| 7.1 | Объявить **Profile v1 Canon** (статус в этом doc + [PR4_PROFILE_CANON.md](./PR4_PROFILE_CANON.md) / Content Canon ссылка на Freeze). |
| 7.2 | Дальнейшие изменения Profile **только** при одном из оснований: (a) подтверждённый UX-дефект; (b) bugfix; (c) новый production-блок с полным паспортом. |
| 7.3 | Экран Today и остальные — копируют **способ мышления** (паспорт → eligibility → контракт → capture → UI), не наращивают отдельную архитектуру «как у Profile». |

**Не входит в Profile v1 Canon:** новые target-блоки из block map, расширение Context Engine, «улучшение ради слоя».

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-21 | Stage opened; pipeline / prompt / block / sample-pack v0 from code audit |
| 2026-07-21 | Capture harness shipped — [PROFILE_PRODUCTION_CAPTURE_PACK.md](./audits/PROFILE_PRODUCTION_CAPTURE_PACK.md) |
| 2026-07-21 | Architecture principle: no MODEL blame; block passport template; defect classes |
| 2026-07-21 | Hardened: model = contract executor; block_eligibility before prompt; Voice §0.05 person-not-system |
| 2026-07-21 | Profile v1 Freeze Checklist (ship-gate) + canon principle: finished existing functions, not max features |
| 2026-07-21 | Model = limited contract executor (meaning/schema stable; not verbatim). DailyState/RFC DEFERRED in Product Truth First |
| 2026-07-21 | Block Freeze Matrix + first block `identity` (passport · gate · profile voice · FE contract-only) |
| 2026-07-21 | `life_spheres` Freeze PASS — canonical passport · captures A/B/C · FE visible_blocks.life_spheres |
