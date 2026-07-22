# Документация TodayFlow

Только **живой канон**. Ветки A–E (Evolution/Calendar/Symbolic/Practice registries), screen-pipeline, старые `spec/` и дублирующие спеки удалены **2026-06-23** — история в `PRODUCT_EXECUTION_TRACKER` changelog.

## С чего начать

| Слой | Документ |
|------|----------|
| **Полный пользовательский путь (SoT маршрута)** | [audits/FULL_USER_PATH_CANON_V1.md](./audits/FULL_USER_PATH_CANON_V1.md) — Landing→Preview→Save→Claim→Profile · A–E |
| **User Journey (pointer)** | [USER_JOURNEY_CANON.md](./USER_JOURNEY_CANON.md) → FULL_USER_PATH |
| **Product Availability Matrix** | [PRODUCT_AVAILABILITY_MATRIX.md](./PRODUCT_AVAILABILITY_MATRIX.md) — данные × экраны × блоки |
| **Data Intake (ровно 2 способа ввода)** | [PRODUCT_DATA_INTAKE.md](./PRODUCT_DATA_INTAKE.md) — публичный preview→email · добавить профиль · единая модель профиля |
| **Capability Contracts (уровни данных → API)** | [PRODUCT_CAPABILITY_CONTRACTS.md](./PRODUCT_CAPABILITY_CONTRACTS.md) — оркестратор · L1/L2/L3 · allowed_output |
| **Generation Contracts (ядро генерации)** | [PRODUCT_GENERATION_CONTRACTS.md](./PRODUCT_GENERATION_CONTRACTS.md) — Contract ⊕ Implementations (промпты = IP) |
| **Data Providers (астро + гео)** | [PRODUCT_DATA_PROVIDERS.md](./PRODUCT_DATA_PROVIDERS.md) — MVP: LLM natal_facts · geo thin |
| **Product Build Map** | [TODAYFLOW_PRODUCT_BUILD_MAP.md](./TODAYFLOW_PRODUCT_BUILD_MAP.md) — entities · Personal Model pointer |
| **Personal Model ↔ code** | [audits/PERSONAL_MODEL_CODE_COMPLIANCE_2026-07-21.md](./audits/PERSONAL_MODEL_CODE_COMPLIANCE_2026-07-21.md) — P0 read-path · [P1 Experience wiring](./audits/PERSONAL_MODEL_EXPERIENCE_WIRING_P1_2026-07-21.md) |
| Product Model (reference) | [TODAYFLOW_PRODUCT_MODEL.md](./TODAYFLOW_PRODUCT_MODEL.md) — §4 content model |
| Launch gaps / DoD / code | [status/WEB_LAUNCH_EXECUTION_PLAN.md](./status/WEB_LAUNCH_EXECUTION_PLAN.md) |
| Launch UX feel (reference) | [status/WEB_LAUNCH_PRODUCT_BLUEPRINT.md](./status/WEB_LAUNCH_PRODUCT_BLUEPRINT.md) |
| Трекер работ | [PRODUCT_EXECUTION_TRACKER.md](./PRODUCT_EXECUTION_TRACKER.md) |

## PIM · Intelligence

- [PERSONAL_INTELLIGENCE_LAYER.md](./PERSONAL_INTELLIGENCE_LAYER.md) — сквозной канон: learning-aware, PIL pipeline
- [USER_KNOWLEDGE_MODEL.md](./USER_KNOWLEDGE_MODEL.md) — Knowledge Atoms
- [INTENT_MODEL_V1.md](./INTENT_MODEL_V1.md) · [HUMAN_DECISION_MODEL_V1.md](./HUMAN_DECISION_MODEL_V1.md)
- [INTERPRETATION_LAYER_AND_REFERENCE.md](./INTERPRETATION_LAYER_AND_REFERENCE.md) — event ≠ meaning
- [KNOWLEDGE_ACQUISITION_AND_SIGNAL_POLICY.md](./KNOWLEDGE_ACQUISITION_AND_SIGNAL_POLICY.md)
- [API_MEMORY_AND_LEARNING_LAYER.md](./API_MEMORY_AND_LEARNING_LAYER.md) — LLM Call Gate, cache, ROI
- [CONTRADICTION_AND_REEVALUATION_V1.md](./CONTRADICTION_AND_REEVALUATION_V1.md)

## Data · Reference (фаза 1)

- [DATA_ORIGINATION_AND_LIFECYCLE.md](./DATA_ORIGINATION_AND_LIFECYCLE.md)
- [DATA_OWNERSHIP_AND_CONSUMPTION_MAP.md](./DATA_OWNERSHIP_AND_CONSUMPTION_MAP.md)
- [REFERENCE_LAYER_AND_BUILD_ORDER.md](./REFERENCE_LAYER_AND_BUILD_ORDER.md)
- [DAYMODEL_INPUT_CONTRACT.md](./DAYMODEL_INPUT_CONTRACT.md)
- [ASTROLOGY_MACHINE_CONTRACT.md](./ASTROLOGY_MACHINE_CONTRACT.md) · [ASTROLOGY_COMPOSITION_MODEL.md](./ASTROLOGY_COMPOSITION_MODEL.md) · [CROSS_DOMAIN_MACHINE_VALIDATION.md](./CROSS_DOMAIN_MACHINE_VALIDATION.md)
- [EVOLUTION_CALCULATION_CONTRACT.md](./EVOLUTION_CALCULATION_CONTRACT.md) — **запрет `evolution_stage` в API** до UEM-2

## Today · Profile (experience)

- [TODAY_SCREEN_V1_CANON.md](./TODAY_SCREEN_V1_CANON.md) — **ACCEPTED** experience layer Today
- [TODAY_LANGUAGE_V1.md](./TODAY_LANGUAGE_V1.md) — язык и quality gate копирайта
- [TODAY_PRODUCT_MODEL.md](./TODAY_PRODUCT_MODEL.md) · [FIRST_DAY_EXPERIENCE.md](./FIRST_DAY_EXPERIENCE.md) — **guest → onboarding → First Today** (route contract v2)
- [TODAY_PERSONALIZATION_CORE.md](./TODAY_PERSONALIZATION_CORE.md) — контракт, events, prompts (web + iOS)
- [TODAY_CONTRACT_ASSEMBLER_MAPPING.md](./TODAY_CONTRACT_ASSEMBLER_MAPPING.md) · [SCREEN_CONTRACTS_V1.md](./SCREEN_CONTRACTS_V1.md)
- [DAY_ENGINE_AND_COHERENCE.md](./DAY_ENGINE_AND_COHERENCE.md) · [DAY_CONTEXT_V0.md](./DAY_CONTEXT_V0.md)
- [PROFILE_SCREEN_MASTER.md](./PROFILE_SCREEN_MASTER.md) · [TODAYFLOW_FOUNDATION_UI.md](./TODAYFLOW_FOUNDATION_UI.md)
- [DAILY_NAVIGATION_MODEL.md](./DAILY_NAVIGATION_MODEL.md) · [CORE_USER_LOOP.md](./CORE_USER_LOOP.md) · [MARKET_ATTENTION_AND_SCREEN_JOBS.md](./MARKET_ATTENTION_AND_SCREEN_JOBS.md)
- [EXPLAIN_MEANING_NOT_MECHANISM.md](./EXPLAIN_MEANING_NOT_MECHANISM.md)

## Статусы · схемы · i18n

- [TODAYFLOW_PRODUCT_BUILD_MAP.md](./TODAYFLOW_PRODUCT_BUILD_MAP.md) — **product SoT** · Entity Catalog · Design Tokens
- [status/WEB_LAUNCH_EXECUTION_PLAN.md](./status/WEB_LAUNCH_EXECUTION_PLAN.md) — gaps · DoD · Decision Log
- [status/WEB_LAUNCH_PRODUCT_BLUEPRINT.md](./status/WEB_LAUNCH_PRODUCT_BLUEPRINT.md) — screen feel/do (reference)
- [status/BEHAVIOR_CHANGE_TEST_V0.md](./status/BEHAVIOR_CHANGE_TEST_V0.md) — **Minimum Day Cycle** ship gate (Evening Close + Tomorrow) · behavior test BLOCKED
- [status/IOS_TODAYFLOW_STATUS.md](./status/IOS_TODAYFLOW_STATUS.md) — web + iOS направление
- [status/TODAY_CANON_VS_CODE_DIFF.md](./status/TODAY_CANON_VS_CODE_DIFF.md) — diff канон ↔ код
- [status/PROFILE_FOUNDATION_QA.md](./status/PROFILE_FOUNDATION_QA.md) — Profile Quick Map vs Foundation §9 (code-side)
- `docs/schemas/` — JSON Schema (CI: `today-contract-schema`, `day-context-schema`, `compact-user-model-schema`)
- `docs/i18n/` — правила перевода

## Правило чтения

При расхождении приоритет (сверху вниз):

0. [audits/FULL_USER_PATH_CANON_V1.md](./audits/FULL_USER_PATH_CANON_V1.md) — **путь пользователя** (после A–E)
1. [TODAYFLOW_PRODUCT_MODEL.md](./TODAYFLOW_PRODUCT_MODEL.md) — модель продукта (Personal Model, projections)
2. [PERSONAL_INTELLIGENCE_MODEL_V1.md](./PERSONAL_INTELLIGENCE_MODEL_V1.md) · [PERSONAL_INTELLIGENCE_LAYER.md](./PERSONAL_INTELLIGENCE_LAYER.md)
3. [USER_MODEL_TARGET_STATE.md](./USER_MODEL_TARGET_STATE.md)
4. [TODAY_SCREEN_V1_CANON.md](./TODAY_SCREEN_V1_CANON.md) (для Today UX)
5. [CORE_PRODUCT_CANON.md](./CORE_PRODUCT_CANON.md)
6. [PRODUCT_EXECUTION_TRACKER.md](./PRODUCT_EXECUTION_TRACKER.md)

## Правило записи (обязательно)

**Сначала найти — потом писать.** Cursor rule: [`.cursor/rules/docs-single-canon.mdc`](../.cursor/rules/docs-single-canon.mdc).

Перед созданием **любого** нового файла в `docs/`:

1. Пройти индекс **этого README** — тема уже покрыта?
2. Поиск по `docs/**/*.md` (и при необходимости `PRODUCT_EXECUTION_TRACKER`) по ключевым словам.
3. Если документ есть → **дополнить существующий**, не плодить `_V2`, `*_MAP`, `*_REGISTRY`, `branch_*`.
4. Новый файл — только при явном пробеле в каноне + строка здесь + запись в `PRODUCT_EXECUTION_TRACKER`.

**Не создавать:** параллельные карты/реестры, `spec/`, snapshot на каждый PR, второй SoT на ту же фичу.

**Куда писать по умолчанию:** трекер (статус работ) · канон экрана (`TODAY_SCREEN_V1_CANON`, `PROFILE_SCREEN_MASTER`) · PIM-слой · OpenAPI/schemas.
