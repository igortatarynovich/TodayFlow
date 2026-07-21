# Profile E2E — Block Passport Template

**Stage:** [PROFILE_E2E_RECONSTRUCTION.md](../PROFILE_E2E_RECONSTRUCTION.md)  
**Rule:** нет заполненного паспорта → блока ещё не существует (не проектировать UI/prompt).

> Качество результата — ответственность цепочки ниже. Категории «модель выдумала» **нет**.

---

## Passport fields (обязательные)

| Field | Question |
|-------|----------|
| `block_id` | Стабильный id блока |
| `purpose` | Зачем блок существует в продукте |
| `user_question` | На какой вопрос пользователя отвечает |
| `allowed_sources` | Какие данные разрешено использовать |
| `min_source_depth` | Минимальная глубина данных для генерации |
| `forbidden_sources` | Что нельзя подмешивать (Today, CUM day, taxonomy-as-fact, …) |
| `insufficient_when` | При каких пробелах данных блок **нельзя** строить |
| `generation_required` | `yes` / `no` / `conditional` — нужна ли LLM |
| `generation_gate` | Условие **запуска** генерации; если false — step не вызывается. **Обязателен до промпта:** «имеет ли блок право существовать для этого пользователя?» |
| `allowed_claims` | Какие утверждения допустимы |
| `forbidden_claims` | Что нельзя утверждать (даже «осторожно») |
| `prompt_id` | Промпт (или `—` если только calc) |
| `expected_response` | Структура / контракт ответа |
| `acceptance_criteria` | По каким правилам ответ принимается |
| `on_reject` | Поведение при ошибке (retry / omit block / forming / fail publish) |
| `snapshot_fields` | Поля Snapshot |
| `ui_surfaces` | Где показывается |
| `appear_when` | Условия показа пользователю |
| `access_tier` | trial / free / sub / calc |
| `kitchen` | Что остаётся только во внутренней трассе |

---

## Dual outcome (единственные допустимые выводы)

После capture / eval для блока допустим **ровно один** из двух:

1. **Stable contract:** данный prompt + gate + schema стабильно дают результат, соответствующий паспорту.  
2. **Do not generate:** при текущем объёме данных блок не строится → generation не запускается → UI не показывает блок как факт.

Запрещённый исход: «иногда хорошо, иногда выдумывает».

---

## Capture proof (4 checks)

Для каждого блока production-faithful pack должен показать:

| # | Check | Fail class (typical) |
|---|--------|----------------------|
| 1 | Блок имел право быть создан (`generation_gate` / eligibility) | `GENERATION_GATE` · `INSUFFICIENT_DATA` · `BLOCK_PURPOSE` |
| 2 | Промпт точно описывал требуемый результат | `PROMPT` |
| 3 | Ответ соответствует контракту / acceptance | `RESPONSE_SCHEMA` · `VALIDATION` · `INPUT` |
| 4 | Тот же ответ без искажений дошёл до UI | `SNAPSHOT` · `API` · `PROJECTION` · `UI_GATE` |

---

## Example — `recurring_patterns` (target passport)

| Field | Value |
|-------|--------|
| purpose | Показать **подтверждённые** повторяющиеся закономерности поведения |
| user_question | Что у меня повторяется в жизни / днях? |
| allowed_sources | living signals, check-ins, longitudinal summary, prior confirmed patterns |
| min_source_depth | `profile_plus_checkins` (или выше) |
| insufficient_when | `source_depth == birth_data_only` · living отсутствует · < N check-in days |
| generation_gate | `classify_allowed_claims(depth).recurring_patterns == True` |
| allowed_claims | Наблюдения, опирающиеся на накопленные дни |
| forbidden_claims | «Регулярно…» из одной даты рождения; stress/recovery as fact без evidence |
| prompt_id | `profile.patterns.v1` (только если gate открыт) |
| on_reject / omit | **Не вызывать** LLM step; Snapshot без confirmed patterns; UI не показывает блок |
| **Wrong design** | Промпт «не выдумывай patterns при пустом living» + schema, требующая заполнения |
| **Right design** | Gate закрыт → step не запускается |

Текущий production (до фикса): schema/`_patterns_ok` требуют `recurring_patterns` всегда → дефект `RESPONSE_SCHEMA` + `GENERATION_GATE`, не «модель выдумала».

---

## Draft passports

| Block | Path | Product lock |
|-------|------|--------------|
| `life_spheres` | [PROFILE_E2E_BLOCK_PASSPORT_LIFE_SPHERES.md](./PROFILE_E2E_BLOCK_PASSPORT_LIFE_SPHERES.md) · [PROFILE_LIFE_SPHERES_DETERMINISTIC_PROJECTOR_V0.md](./PROFILE_LIFE_SPHERES_DETERMINISTIC_PROJECTOR_V0.md) | natal-presence · deterministic-first · **not** patterns continuation |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-21 | Template opened with stage architecture principle |
| 2026-07-21 | generation_gate = eligibility before prompt (mandatory) |
| 2026-07-21 | Link draft passport `life_spheres` |
