# DayContext v0 — спецификация

**Статус:** черновик контракта (`day_context_v0`), согласован с [DAY_ENGINE_AND_COHERENCE.md](./DAY_ENGINE_AND_COHERENCE.md) и текущим бэкендом `POST /today/narrative`.  
**Машиночитаемая схема:** [docs/schemas/day_context_v0.schema.json](./schemas/day_context_v0.schema.json).  
**CI:** job `day-context-schema` → `scripts/validate_day_context_contract.py`.

## Назначение

`DayContext` — один логический пакет фактов и сжатых интерпретаций для **дня** (`target_date`), из которого собираются промпты narrative, объяснимость UI и (далее) события обучения. Целевой **смысловой** слой дня — **DayModel** (см. [DAY_ENGINE_AND_COHERENCE.md §10](./DAY_ENGINE_AND_COHERENCE.md#10-daymodel-и-decision-engine-закрытый-канон)); DayContext — вход в его расчёт, а не замена. v0 **не меняет** форму ответа `today_day_v1` и payload surfaces; это входной/промежуточный контракт для сборщика (**DE-2** — встроен в `build_today_narrative`, см. ниже).

## Корень объекта

| Поле | Тип | Обяз. | Смысл |
|------|-----|--------|--------|
| `contract_version` | строка | да | Константа `day_context_v0`. |
| `meta` | объект | да | Идентификация дня и режима генерации. |
| `layers` | объект | да | Слои канона §2; часть полей опциональна внутри `layers`. |

## meta

| Поле | Тип | Обяз. | Смысл |
|------|-----|--------|--------|
| `target_date` | `YYYY-MM-DD` | да | День контекста. |
| `locale` | строка | да | Нормализованная локаль (как в narrative). |
| `insight_depth_tier` | `free` \| `pro` \| `premium` | да | Тариф глубины инсайтов. |
| `depth_level` | `quick` \| `normal` \| `deep` | да | **DE-8:** запрошенная глубина текста за один вызов narrative (`POST /today/narrative`); влияет на промпт, `max_tokens`/temperature и `day_context_sha256`; не смешивать с `insight_depth_tier`. |
| `policy_version` | строка | нет | Контент-политика (напр. `clean-info-v1`). |
| `voice_profile` | строка | нет | Голос генерации. |
| `profile_snapshot_id` | int \| null | нет | Последний снапшот профиля, если известен. |
| `ritual_context_fingerprint` | строка | нет | SHA256-префикс нормализованного ritual (кэш narrative). |

## layers — соответствие канону

| Канон §2 | Ключ в `layers` | Источник в коде сегодня |
|----------|-----------------|-------------------------|
| tarot (+ ритуал) | `ritual` | `RitualContextRequest` после `_normalize_ritual_context` (может быть `{}`). |
| numerology / mood / тема «в голове» | ↑ внутри `ritual` | `numerology_value`, `mood`, опционально `head_topic` (id чипа, до 120 символов), `day_events`. |
| astrology + стержень дня | `daily_foundation` | Логи модуля `daily_foundation` (`spine`, сценарии, prism). |
| user_profile | `user_core` / `experience_slice` | `assemble_experience_slice(..., experience_id="today")` — не полный raw `core_profile`. |
| profile selector (промпт-гейт) | `profile_selector` | `select_profile_context` в `profile_engine/selector.py`; см. [DAY_CONTEXT_V0.md](./DAY_CONTEXT_V0.md). |
| rhythm (+ дневник-факты) | `fusion.rhythm_context` | `_build_rhythm_context` в `tracking.py`; также scores / encouragement / recommendations. |
| behavior_patterns | `behavior_patterns` | Агрегаты `meaning_events` за скользящее окно (`meaning_surface_patterns_v0`), см. `build_meaning_surface_patterns_v0` + DE-5. |
| history | `history` | **DE-9 v0–v1.5 (DONE):** `build_history_layer_v0` → `day_history_v0`: fusion scores вчера/7d, `day_flow`, `meaning_day_signals`, `reflection_excerpt` (`day_connection_excerpt_v0` из `DayConnection`, caps), дельты и trustworthy-флаги; в LLM как **`day_history`**; UI strip web+iOS. |
| intent | `intent` | **DE-6:** `build_intent_layer_v0` → `intent_slice_v0`: `morning_intention`, `morning_focus` из `DayConnection` на `target_date`; `head_topic` из нормализованного `ritual`; ответы мини-вопросов (`question_of_day_answer`, `quick_decision_answer`); поле `what_matters_line` — сжатая строка для LLM. Если нечего передать — `null` или слой отсутствует. |
| health_signals | `health_signals` | Зарезервировано (DE-10). |
| visible_profile | `visible_profile` | **DE-12:** срез «что пользователь осознанно задал / видит» (`profile_prompt_slices_v0.build_visible_profile_slice_v0`): имя, знак/дата, намерение из `intent`, настроение/тема из `ritual`, заголовки целей из `fusion.rhythm_context.goals`. В промпт LLM; не путать с наталом в `user_core`. |
| internal_profile | `internal_profile` | **DE-12:** срез для системы (`build_internal_profile_slice_v0`): `meaning_surface_patterns_v0`, выдержка `learning`, числовые `scores` — только факты из JSON; не показывать дословно как диагноз; допустимо мягко в «Почему так». |
| DayModel (§10) | `day_model` | **`day_model_v0`:** `build_day_model_v0` после сборки остальных слоёв; детерминированный объект для UI/объяснимости и срезов LLM (см. [DAY_ENGINE_AND_COHERENCE.md §10](./DAY_ENGINE_AND_COHERENCE.md#10-daymodel-и-decision-engine-закрытый-канон)). **DE-9 v1.4:** при `history_slice` — поле `temporal` (дельта, недельный тренд, summary для промпта). |
| Решение дня для guide | `guide_decision` | **`guide_decision_v0`:** `build_guide_decision_v0` сразу после `day_model`; сводит ритуал (карта, число, настроение, head_topic), луну из foundation, `day_model` и короткий контур `user_core` в готовые поля headline/subline/core/do/avoid/сигналы. В `today_narrative` они **подменяют** ядро ответа guide после LLM (решение → текст вторичных блоков остаётся за моделью). |

Полный **`fusion`** в v0 совпадает по смыслу с `FusionIndexResponse.model_dump()`: `date`, `scores`, `cycle_context`, `activity_context`, `rhythm_context`, `recommendations`, `encouragement`. В **`activity_context`** также **`morning_completed`**, **`day_completed`**, **`evening_completed`** из `DayConnection`; **`guide_action_options_selected_today`** — число событий `action_option_selected` в `meaning_events` за этот `local_date`; **`guide_meaning_completions_today`** — фиксированный словарь счётчиков по типам «сделано» из `meaning_events` за тот же день: `habit_completed`, `practice_completed`, `focus_completed`, `affirmation_done`, `ascetic_step_done` (DE-7 v2, `guide_flow_signals.py`). Сервер считает всё это в `GET /tracking/fusion/{date}` и далее в `POST /today/narrative` без доверия клиенту к числам. Флаг **`day_completed`** — отдельно: явная отметка этапа «Шаг дня» в `DayConnection`; он **не** выводится из счётчиков и может расходиться с ними (например, пользователь отметил этап без события или наоборот). В **`_fusion_slim_for_prompt`** для spheres/evening/deepen в компактный `fusion` попадают только эти поля из `activity_context` (не весь блок); по каждому счётчику — кламп 0–50.

## Промпты narrative (реализация)

`build_today_narrative` всегда строит `DayContext` до веток по `surface`. В **`generation_logs.input_payload`** для всех surface: `day_context_sha256`, `day_context_contract_version`. При наличии слоя **`day_model`** в `DayContext` также пишется **`day_model_contract`** (сжатый снимок для логов/кэша).

- **guide:** JSON в LLM с теми же ключами (`user_core`, полный `profile`, `fusion`, `daily_foundation`, опционально `ritual_context`, опционально `behavior_patterns`, опционально **`intent`**); при наличии в слоях — **`visible_profile`** и **`internal_profile`** (те же объекты, что в `DayContext.layers`). **`user_core`**, **`fusion`**, **`daily_foundation`**, ритуал — из `DayContext.layers` (нормализованный `fusion`). В user JSON для LLM при наличии — **`day_engine_brief`**, **`day_model`**, **`guide_decision`** (`guide_decision_v0`); в HTTP **`payload`** ответа те же ключи в основном для **`surface=guide`** (см. docstring эндпоинта), плюс **`narrative_hierarchy`** (`narrative_hierarchy_v0`, `primary_anchor` = `day_engine_brief`, O2) и **`guide_contract_v2`** + **`guide_pipeline`** (`guide_pipeline_v0`: funnel/monolith, log ids шагов DE-13). Ядро guide: funnel step3 (`guide_funnel_core_text_v0`) или fallback **`guide_decision_v0`**; при LLM-core **`guide_decision`** не перезаписывает headline/subline/core.
- **day_layer:** `user_core` и полный **`fusion`** из `DayContext.layers`; опционально `behavior_patterns`, **`intent`**, **`visible_profile`**, **`internal_profile`**; при наличии слоя — **`day_engine_brief`**, **`day_model`** в user JSON LLM.
- **spheres / evening / deepen:** `user_core` из `DayContext.layers`, компактный **`fusion`** через `_fusion_slim_for_prompt` от того же нормализованного `layers.fusion`; опционально `behavior_patterns`, **`intent`**, **`visible_profile`**, **`internal_profile`**; при наличии слоя — **`day_engine_brief`**, **`day_model`** в user JSON LLM.

Кэш narrative построен на **стабильном ключе дня** (date, surface, parent, `deepen_topic`, `insight_depth_tier`, `locale`, `ritual_context_fp`, `intent_context_fp`, `depth_level`, `prompt_label`) и на **переиспользовании за день**: `day_context_sha256` пишется в `generation_logs.input_payload`, но с [fix «Сегодня собирается бесконечно»] трактуется как **предпочтение свежести**, а не жёсткий гейт. `_load_narrative_cache` (и per-step `_load_funnel_step_cache`) при точном совпадении хэша отдают именно этот лог, иначе переиспользуют самый свежий лог с совпавшим стабильным ключом. Причина: `get_daily_fusion_index` пересчитывает `fusion` (и `recommendations`) из **собственной внутридневной активности пользователя** (mood, `action_option_selected`, практики, флаги `DayConnection`), поэтому хэш дрейфует от захода к заходу — жёсткая проверка `day_context_sha256` делала каждый заход cache-miss и повторно гоняла LLM-воронку. Осмысленные изменения (ритуал / намерение / тариф / глубина / снапшот профиля) уже покрыты стабильным ключом → корректно триггерят регенерацию. Детерминированные слои (`day_model`, `guide_decision`) на cache-hit пути пересобираются от текущего `fusion`, поэтому структурные поля guide остаются актуальными — переиспользуется только LLM-проза. Политика повторяет `day_story_v1` (стабильный ключ date + `ritual_fp` + snapshot). **Learning Δ:** AMLL-гейт помечает такой возврат как `cache_hit` с `reason=GATE:cache_hit:same_day_reuse` и `cache_policy=allow_similarity` (аудит переиспользования, «API = актив»).

`POST /today/narrative`: **`ritual_context`** допускается для любого `surface` (например slim `{ head_topic }` для child surfaces после ритуала); паритет web (`lastRitualNarrativeContextRef` + `postTodayNarrative`) и iOS (`lastRitualNarrativeContext` в `TodayFlowStore`).

## Версионирование

При несовместимых изменениях — новый `contract_version` (`day_context_v1`, …). Клиенты (web, iOS) для v0 могут не получать объект по API до появления отдельного эндпоинта; достаточно держать DTO в доке/схеме для паритета типов.
