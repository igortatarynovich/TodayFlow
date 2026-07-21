# Profile End-to-End Reconstruction

**Status:** ACTIVE — сквозной этап (не UI redesign)  
**Started:** 2026-07-21  
**Parent canons:** [EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md](./EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md) · [PROFILE_CONTENT_CANON_V1.md](./PROFILE_CONTENT_CANON_V1.md) · [PR4_PROFILE_CANON.md](./PR4_PROFILE_CANON.md) · [UNDERSTANDING_PROGRESS_AND_DEPTH_CANON.md](./UNDERSTANDING_PROGRESS_AND_DEPTH_CANON.md) · [TODAYFLOW_VOICE_CANON.md](./content/TODAYFLOW_VOICE_CANON.md)

> **Запрет на этом этапе:** рисовать новый экран · переписывать промпты «на глаз» · чинить тексты без доказанной точки в цепочке · объяснять брак фразой «модель выдумала».

---

## Архитектурный принцип (жёстко)

**Категории «ошибка модели» / «модель выдумала» на этом этапе не существует.**

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

1. **«Данный промпт стабильно генерирует результат, соответствующий контракту блока.»**  
2. **«Этот блок невозможно построить при текущем объёме данных — генерация не должна запускаться.»**

Запрещённый вывод: «иногда пишет хорошо, а иногда выдумывает».

### Порядок проектирования блока

```text
1. Назначение + вопрос пользователя
2. Разрешённые / запрещённые данные + min depth
3. Gate: генерировать или нет
4. Точная задача для модели (только если gate открыт)
5. Схема ответа + критерии приёмки
6. Snapshot → API → UI (без искажений)
7. Публикация пользователю
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
| 1 | Pipeline map (registration → UI + alt paths) | [audits/PROFILE_E2E_PIPELINE_MAP.md](./audits/PROFILE_E2E_PIPELINE_MAP.md) | **v0** |
| 2 | Prompt registry (passports) | [audits/PROFILE_E2E_PROMPT_REGISTRY.md](./audits/PROFILE_E2E_PROMPT_REGISTRY.md) | **v0 — align to block passport** |
| 3 | Block map (every surface block) | [audits/PROFILE_E2E_BLOCK_MAP.md](./audits/PROFILE_E2E_BLOCK_MAP.md) | **v0 — current reality** |
| 4 | Sample pack through full pipeline | [audits/PROFILE_E2E_SAMPLE_PACK.md](./audits/PROFILE_E2E_SAMPLE_PACK.md) | **v0 — existing eval + gaps** |
| 4b | Production-faithful capture harness | [audits/PROFILE_PRODUCTION_CAPTURE_PACK.md](./audits/PROFILE_PRODUCTION_CAPTURE_PACK.md) | **IMPLEMENTATION** |
| 5 | Degradation points (architectural classes only) | capture packs + maps | **v0** |
| 6 | Missing-data matrix · trial/free/sub content plan | Understanding Progress canon + block map | partial |
| 7 | Target architecture + Screen Master rewrite | *later* | not started |
| 8 | Contract tests per layer | *later* | not started |
| 9 | Downstream Snapshot consumption proof | [PROFILE_AS_SOURCE_CONSUMPTION_AUDIT.md](./audits/PROFILE_AS_SOURCE_CONSUMPTION_AUDIT.md) | exists |

---

## Порядок работ (жёстко)

```text
1. Audit current pipeline          ← done (maps v0)
2. Capture production-faithful packs (eligibility + 4 proofs per block)  ← NOW
3. Classify defects with architectural classes only (no MODEL)
4. Decide which funnel steps create unique knowledge / which must gate off
5. Target architecture + content contracts (trial/free/sub)
6. Then prompts / UI / Screen Master — until stable contract or omit
```

**Текущий шаг реализации:** [PROFILE_PRODUCTION_CAPTURE_PACK.md](./audits/PROFILE_PRODUCTION_CAPTURE_PACK.md) — infra only; product gates/prompt fixes **после** packs.

Существующие review packs (`run_review_packs_v1.py`) **недостаточны** и **не** SoT. SoT = `run_production_capture_v0.py`.

---

## Definition of done (этап)

1. Каждый блок будущего экрана имеет **полный паспорт** (нет паспорта → нет блока).  
2. Каждый prompt привязан к паспорту блока и generation gate.  
3. Есть ≥1 production-faithful pack на birth-only и longitudinal: eligibility → prompts → raw → validation → snapshot → API → UI.  
4. Для каждого расхождения выставлен **архитектурный** класс дефекта (не `MODEL`).  
5. Список устаревших путей с планом удаления.  
6. Доказано, что Experiences читают Snapshot, а не invent personality (или зафиксирован gap).  
7. Только после этого — целевой Profile Screen Master и правки промптов **до стабильного контракта**.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-21 | Stage opened; pipeline / prompt / block / sample-pack v0 from code audit |
| 2026-07-21 | Capture harness shipped — [PROFILE_PRODUCTION_CAPTURE_PACK.md](./audits/PROFILE_PRODUCTION_CAPTURE_PACK.md) |
| 2026-07-21 | Architecture principle: no MODEL blame; block passport template; defect classes |
