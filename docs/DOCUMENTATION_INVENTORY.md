# Documentation Inventory

**Status:** ACTIVE — inventory only (not a product SoT).
**Purpose:** before any archive/delete, list every `docs/**/*.md` with role and duplication risk.
**Rule:** do not delete a row with unique decisions until those decisions are merged into an entry-point interim doc (see [README.md](./README.md)).

Owned by docs governance. Update this table in the same PR when adding or retiring docs ([docs-single-canon](../.cursor/rules/docs-single-canon.mdc)).

## Legend

| Is SoT | Meaning |
|--------|---------|
| `yes (interim until PR-2)` | Current best authority; fold into consolidated Product Surface Map later |
| `partial / subordinate` | Detail under a parent; not a competing product SoT |
| `no` | Audit, tracker, calibration, RFC, passport, or index — keep until unique decisions transfer |

## By entry section

### 1. Product Map

| Document | Purpose | Is SoT | Duplicates | Status |
|----------|---------|--------|------------|--------|
| [`docs/CORE_PRODUCT_CANON.md`](./CORE_PRODUCT_CANON.md) | живой канон: Core Product Canon | no / review | Product Model + Build Map + screen canons | — |
| [`docs/CORE_USER_LOOP.md`](./CORE_USER_LOOP.md) | прочее: Core User Loop — Theme → Action → Progress | no / review | — | принято (гипотеза главного объекта продукта — проверяется, не wire). |
| [`docs/FIRST_DAY_EXPERIENCE.md`](./FIRST_DAY_EXPERIENCE.md) | прочее: First Day & Onboarding — продуктовый контракт | yes (interim until PR-2) | — | ACCEPTED — канон guest → signup → onboarding → First Today (маршруты, данные, PIM, DoD). |
| [`docs/MARKET_ATTENTION_AND_SCREEN_JOBS.md`](./MARKET_ATTENTION_AND_SCREEN_JOBS.md) | прочее: Market Attention & Screen Jobs | no / review | — | принято (рыночный канон + «почему открыть сегодня»). |
| [`docs/PRODUCT_LEXICON_AND_RETENTION.md`](./PRODUCT_LEXICON_AND_RETENTION.md) | прочее: Лексика и удержание внимания | no / review | — | канон продукта (2026-07-20) |
| [`docs/PRODUCT_TRUTH_FIRST.md`](./PRODUCT_TRUTH_FIRST.md) | прочее: Product Truth First | yes (interim until PR-2) | — | ACTIVE — обязательный продуктовый принцип TodayFlow |
| [`docs/TODAYFLOW_PRODUCT_BUILD_MAP.md`](./TODAYFLOW_PRODUCT_BUILD_MAP.md) | карта / pipeline: Product Build Map | yes (interim until PR-2) | — | ACTIVE — главный документ продукта. |
| [`docs/TODAYFLOW_PRODUCT_MODEL.md`](./TODAYFLOW_PRODUCT_MODEL.md) | продуктовая / доменная модель: Product Model | yes (interim until PR-2) | — | FROZEN for Launch v1 (execution) · §4 Content Models — ACTIVE (2026-07-01). |
| [`docs/UNDERSTANDING_PROGRESS_AND_DEPTH_CANON.md`](./UNDERSTANDING_PROGRESS_AND_DEPTH_CANON.md) | живой канон: Understanding Progress and Depth | yes (interim until PR-2) | — | ACTIVE — канон продуктовой модели TodayFlow |
| [`docs/audits/FULL_USER_PATH_CANON_V1.md`](./audits/FULL_USER_PATH_CANON_V1.md) | аудит (только deltas): полный пользовательский путь и целевой канон v1 | no | FIRST_DAY + CORE_USER_LOOP + screen canons (until accepted) | аудит + целевой канон (не молчаливая перепись старых SoT) |

### 2. Technical Architecture

| Document | Purpose | Is SoT | Duplicates | Status |
|----------|---------|--------|------------|--------|
| [`docs/API_MEMORY_AND_LEARNING_LAYER.md`](./API_MEMORY_AND_LEARNING_LAYER.md) | продуктовая / доменная модель: API Memory & Learning Layer (AMLL) | partial / subordinate | — | принято (канон экономики и обучения на API). |
| [`docs/ASTROLOGY_COMPOSITION_MODEL.md`](./ASTROLOGY_COMPOSITION_MODEL.md) | продуктовая / доменная модель: Astrology Composition Model (ACM-Compose) | partial / subordinate | — | принято (канон gate перед P0.8 — первичные vs производные сущности). |
| [`docs/ASTROLOGY_MACHINE_CONTRACT.md`](./ASTROLOGY_MACHINE_CONTRACT.md) | технический контракт: Astrology Machine Contract (AMC) | yes (interim until PR-2) | — | принято (канон P0.7 — структура Machine Layer для астрологии). |
| [`docs/CONTRADICTION_AND_REEVALUATION_V1.md`](./CONTRADICTION_AND_REEVALUATION_V1.md) | прочее: Contradiction & Re-evaluation v1 (C15) | no / review | — | `ACCEPTED` — канон как система меняет мнение о человеке. |
| [`docs/CROSS_DOMAIN_MACHINE_VALIDATION.md`](./CROSS_DOMAIN_MACHINE_VALIDATION.md) | технический контракт: Cross-Domain Machine Validation (CDMV) | partial / subordinate | — | принято (P0.9 DONE — общая система координат подтверждена). |
| [`docs/DAILY_INTERPRETATION_ENGINE_PHASE.md`](./DAILY_INTERPRETATION_ENGINE_PHASE.md) | прочее: Phase N — Daily Interpretation Engine | no / review | RFC_DAILY_STATE_V0 (DEFERRED) | PLANNED — архитектурная фаза (не текущий execution slice) |
| [`docs/DATA_ORIGINATION_AND_LIFECYCLE.md`](./DATA_ORIGINATION_AND_LIFECYCLE.md) | прочее: Происхождение данных и жизненный цикл (Data Origination & Lifecycle) | no / review | — | принято (канон откуда данные берутся, как подтверждаются и когда устаревают). |
| [`docs/DATA_OWNERSHIP_AND_CONSUMPTION_MAP.md`](./DATA_OWNERSHIP_AND_CONSUMPTION_MAP.md) | карта / pipeline: Карта владения данными и потребления (Data Ownership & Consumption) | yes (interim until PR-2) | — | принято (канон архитектуры данных). |
| [`docs/DAYMODEL_INPUT_CONTRACT.md`](./DAYMODEL_INPUT_CONTRACT.md) | технический контракт: DayModel Input Contract | partial / subordinate | — | принято (архитектурный шаг P0.1 — между Reference Layer и миграцией данных). |
| [`docs/DAY_CONTEXT_V0.md`](./DAY_CONTEXT_V0.md) | прочее: DayContext v0 — спецификация | no / review | — | черновик контракта (`day_context_v0`), согласован с [DAY_ENGINE_AND_COHERENCE.md](./DAY_EN |
| [`docs/DAY_ENGINE_AND_COHERENCE.md`](./DAY_ENGINE_AND_COHERENCE.md) | прочее: Day Engine и цельность продукта (аудит → направление) | no / review | — | канон продуктово-инженерного направления (не маркетинг). |
| [`docs/DECISION_RELEVANCE_V1.md`](./DECISION_RELEVANCE_V1.md) | прочее: Decision Relevance v1 (C17) | no / review | — | `ACCEPTED` — канон приоритизации знаний для решений и контекста. |
| [`docs/EVOLUTION_CALCULATION_CONTRACT.md`](./EVOLUTION_CALCULATION_CONTRACT.md) | технический контракт: Evolution Calculation Contract (ECC) | partial / subordinate | — | принято (канон формулы Evolution Score и переходов стадий). |
| [`docs/EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md`](./EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md) | прочее: Explainable Computation and Interpretation | yes (interim until PR-2) | — | ACTIVE — общий канон вычислений и интерпретаций всего TodayFlow |
| [`docs/EXPLAINABLE_INTERPRETATION.md`](./EXPLAINABLE_INTERPRETATION.md) | прочее: Explainable Interpretation | no / review | EXPLAINABLE_COMPUTATION_AND_INTERPRETATION | ACTIVE — канон текстов и советов (дочерний к umbrella) |
| [`docs/EXPLAIN_MEANING_NOT_MECHANISM.md`](./EXPLAIN_MEANING_NOT_MECHANISM.md) | прочее: Explain Meaning, Not Mechanism | no / review | — | принято — сквозное правило TodayFlow (Profile · Today · Guidance · Symbolic · Gamification |
| [`docs/HUMAN_DECISION_MODEL_V1.md`](./HUMAN_DECISION_MODEL_V1.md) | продуктовая / доменная модель: Human Decision Model v1 (HDM) | partial / subordinate | — | `ACCEPTED` — канон долгосрочной модели человека для TodayFlow. |
| [`docs/INTENT_MODEL_V1.md`](./INTENT_MODEL_V1.md) | продуктовая / доменная модель: Intent Model v1 (IM) | partial / subordinate | — | `ACCEPTED` — канон домена намерений внутри PIM. |
| [`docs/INTERPRETATION_LAYER_AND_REFERENCE.md`](./INTERPRETATION_LAYER_AND_REFERENCE.md) | продуктовая / доменная модель: Interpretation Layer & Reference (ILR) | partial / subordinate | — | принято (канон как события становятся смыслом — без LLM). |
| [`docs/KNOWLEDGE_ACQUISITION_AND_SIGNAL_POLICY.md`](./KNOWLEDGE_ACQUISITION_AND_SIGNAL_POLICY.md) | прочее: Knowledge Acquisition & Signal Policy (KASP) | no / review | — | принято (канон что, откуда и как система имеет право собирать данные). |
| [`docs/LLM_QUALITY_AND_PROMPT_EVOLUTION.md`](./LLM_QUALITY_AND_PROMPT_EVOLUTION.md) | прочее: LLM Quality & Prompt Evolution | yes (interim until PR-2) | — | active canon (2026-07) |
| [`docs/ONTOLOGY_AND_FOUNDATION_PHASES.md`](./ONTOLOGY_AND_FOUNDATION_PHASES.md) | прочее: Онтология мира и фазы построения TodayFlow | no / review | — | принято (канон вида сверху — где мы сейчас и в каком порядке строим систему). |
| [`docs/PERSONAL_INTELLIGENCE_LAYER.md`](./PERSONAL_INTELLIGENCE_LAYER.md) | продуктовая / доменная модель: Personal Intelligence Layer (PIL) | yes (interim until PR-2) | — | принято (сквозной архитектурный канон). |
| [`docs/PERSONAL_INTELLIGENCE_MODEL_V1.md`](./PERSONAL_INTELLIGENCE_MODEL_V1.md) | продуктовая / доменная модель: Personal Intelligence Model v1 (PIM) | partial / subordinate | PERSONAL_INTELLIGENCE_LAYER + USER_MODEL_TARGET_STATE | `ACCEPTED` — центральный объект системы TodayFlow. |
| [`docs/PIM_PRODUCT_NORTH_STAR.md`](./PIM_PRODUCT_NORTH_STAR.md) | прочее: PIM Product North Star | no / review | PERSONAL_INTELLIGENCE_LAYER / PRODUCT_MODEL | `ACCEPTED` — критерий успеха продукта (платформа, не экран). |
| [`docs/PIM_PR_GATE_V1.md`](./PIM_PR_GATE_V1.md) | прочее: PIM PR Gate v1 — проверка PR через стек C10–C17 | no / review | — | `ACCEPTED` — обязательный gate для PR1, PR2 и далее. |
| [`docs/REFERENCE_LAYER_AND_BUILD_ORDER.md`](./REFERENCE_LAYER_AND_BUILD_ORDER.md) | продуктовая / доменная модель: Reference Layer и порядок построения TodayFlow | yes (interim until PR-2) | — | принято (фундаментальный канон). |
| [`docs/TEMPORAL_IDENTITY_V1.md`](./TEMPORAL_IDENTITY_V1.md) | прочее: Temporal Identity v1 (C16) | no / review | — | `ACCEPTED` — канон времени и природы изменений в PIM. |
| [`docs/USER_KNOWLEDGE_MODEL.md`](./USER_KNOWLEDGE_MODEL.md) | продуктовая / доменная модель: User Knowledge Model (UKM) | partial / subordinate | — | принято (канон того, что система знает о пользователе). |
| [`docs/USER_MODEL_TARGET_STATE.md`](./USER_MODEL_TARGET_STATE.md) | продуктовая / доменная модель: User Model Target State (UMTS) | partial / subordinate | — | принято (канон конечного артефакта Intelligence Layer). |
| [`docs/i18n/Quality_Rules.md`](./i18n/Quality_Rules.md) | i18n: Правила качества i18n текстов | no / review | — | Активные правила |
| [`docs/i18n/RU_Translation_Guide.md`](./i18n/RU_Translation_Guide.md) | i18n: Руководство по заполнению русских переводов | no / review | — |  |
| [`docs/i18n/RU_Translations_Priority.md`](./i18n/RU_Translations_Priority.md) | i18n: План приоритизации RU переводов | no / review | — | ❌ Не заполнены |
| [`docs/i18n/Translation_Guide.md`](./i18n/Translation_Guide.md) | i18n: Инструкции по полному переводу RU ключей | no / review | — | — |
| [`docs/rfc/RFC_DAILY_STATE_V0.md`](./rfc/RFC_DAILY_STATE_V0.md) | RFC: RFC — DailyState v0 | no (RFC / deferred) | — | DRAFT — следующий артефакт Phase N (не implementation) |
| [`docs/schemas/REFERENCE_MACHINE_CONTRACT_V1.md`](./schemas/REFERENCE_MACHINE_CONTRACT_V1.md) | schema notes: Reference Machine Contract v1 — JSON Schema | no / review | — | принято (P0.2). |

### 3. Generation Registry

| Document | Purpose | Is SoT | Duplicates | Status |
|----------|---------|--------|------------|--------|
| [`docs/PROFILE_E2E_RECONSTRUCTION.md`](./PROFILE_E2E_RECONSTRUCTION.md) | прочее: Profile End-to-End Reconstruction | yes (interim until PR-2) | — | ACTIVE — сквозной этап (не UI redesign) |
| [`docs/audits/EXPLAINABLE_GENERATION_AUDIT_REGISTRY_V0.md`](./audits/EXPLAINABLE_GENERATION_AUDIT_REGISTRY_V0.md) | аудит (только deltas): Explainable Generation Audit Registry v0 | no | — | ACTIVE quality gate (сквозной аудит, не новый принцип) |
| [`docs/audits/PROFILE_E2E_BLOCK_MAP.md`](./audits/PROFILE_E2E_BLOCK_MAP.md) | аудит (только deltas): Profile E2E — Block Map (current V2 + target gaps) | no | PROFILE_E2E_RECONSTRUCTION + prompt registry | — |
| [`docs/audits/PROFILE_E2E_BLOCK_PASSPORT_LIFE_SPHERES.md`](./audits/PROFILE_E2E_BLOCK_PASSPORT_LIFE_SPHERES.md) | block/prompt passport: Profile E2E — Block Passport: `life_spheres` (draft) | no | prompt registry + reconstruction (keep unique eligibility/projector decisions until merged) | draft · product decision fixed · no funnel/code changes in this artifact |
| [`docs/audits/PROFILE_E2E_BLOCK_PASSPORT_TEMPLATE.md`](./audits/PROFILE_E2E_BLOCK_PASSPORT_TEMPLATE.md) | block/prompt passport: Profile E2E — Block Passport Template | no | PROFILE_E2E_RECONSTRUCTION + prompt registry | — |
| [`docs/audits/PROFILE_E2E_PIPELINE_MAP.md`](./audits/PROFILE_E2E_PIPELINE_MAP.md) | аудит (только deltas): Profile E2E — Pipeline Map (current reality) | no | PROFILE_E2E_RECONSTRUCTION | — |
| [`docs/audits/PROFILE_E2E_PROMPT_REGISTRY.md`](./audits/PROFILE_E2E_PROMPT_REGISTRY.md) | аудит (только deltas): Profile E2E — Prompt Registry (passports) | no | — | — |
| [`docs/audits/PROFILE_E2E_SAMPLE_PACK.md`](./audits/PROFILE_E2E_SAMPLE_PACK.md) | аудит (только deltas): Profile E2E — Sample Pack (first forensic artifact) | no | — | — |
| [`docs/audits/PROFILE_PRODUCTION_CAPTURE_PACK.md`](./audits/PROFILE_PRODUCTION_CAPTURE_PACK.md) | capture / freeze evidence: Profile Production-Faithful Capture Pack | no | — | IMPLEMENTATION — infra only |
| [`docs/content/TODAYFLOW_VOICE_CANON.md`](./content/TODAYFLOW_VOICE_CANON.md) | voice / content canon: Voice Canon | yes (interim until PR-2) | — | архитектурный канон контента (не copywriter guide). |

### 4. Implementation Status

| Document | Purpose | Is SoT | Duplicates | Status |
|----------|---------|--------|------------|--------|
| [`docs/DOCUMENTATION_INVENTORY.md`](./DOCUMENTATION_INVENTORY.md) | документационный индекс: Documentation Inventory | no (index) | — (index only) | ACTIVE — inventory only (not a product SoT). |
| [`docs/PRODUCT_EXECUTION_TRACKER.md`](./PRODUCT_EXECUTION_TRACKER.md) | статус / трекер: Product Execution Tracker | no | — | — |
| [`docs/audits/DAY_SYMBOL_REVEAL_CANON_V1.md`](./audits/DAY_SYMBOL_REVEAL_CANON_V1.md) | аудит (только deltas): Day Symbol Reveal Canon v1 | partial (accepted decisions) | — | accepted product decisions for P0 leak closure (2026-07-20) |
| [`docs/audits/INTERPRETATION_QUALITY_AUDIT_2026-07-20.md`](./audits/INTERPRETATION_QUALITY_AUDIT_2026-07-20.md) | аудит (только deltas): Interpretation Quality Audit — TodayFlow | no | — | Inventory + dual-influence fixes + eval harness shipped; full 100-scenario blind scoring i |
| [`docs/audits/PERSONAL_MODEL_CODE_COMPLIANCE_2026-07-21.md`](./audits/PERSONAL_MODEL_CODE_COMPLIANCE_2026-07-21.md) | аудит (только deltas): Personal Model — code compliance audit (2026-07-21) | no | — | audit (канон уже есть; новых принципов нет) |
| [`docs/audits/PERSONAL_MODEL_EXPERIENCE_WIRING_P1_2026-07-21.md`](./audits/PERSONAL_MODEL_EXPERIENCE_WIRING_P1_2026-07-21.md) | аудит (только deltas): Personal Model → Experiences wiring audit (P1) — 2026-07-21 | no | — | P1 implementation in progress — `experience_contract_assembler_v0` + Consistency Tests |
| [`docs/audits/PROFILE_AS_SOURCE_CONSUMPTION_AUDIT.md`](./audits/PROFILE_AS_SOURCE_CONSUMPTION_AUDIT.md) | аудит (только deltas): Profile as Canonical Identity — Downstream Consumption Audit | no | — | ACTIVE — next stage after PR-4.1 CLOSED |
| [`docs/audits/PROFILE_CAPTURE_CASE_AB_REPORT.md`](./audits/PROFILE_CAPTURE_CASE_AB_REPORT.md) | capture / freeze evidence: Profile Capture — Case A/B Comparative Report | no | — | — |
| [`docs/audits/USER_JOURNEY_AUDIT_2026-07-20.md`](./audits/USER_JOURNEY_AUDIT_2026-07-20.md) | аудит (только deltas): User Journey Audit — 2026-07-20 | no | — | — |
| [`docs/status/BEHAVIOR_CHANGE_TEST_V0.md`](./status/BEHAVIOR_CHANGE_TEST_V0.md) | статус / трекер: Minimum Day Cycle + Behavior Test (operational, not canon) | no | — | IN_PROGRESS — ship gate до первых 5–10 людей · behavior test BLOCKED |
| [`docs/status/IOS_TODAYFLOW_STATUS.md`](./status/IOS_TODAYFLOW_STATUS.md) | статус / трекер: iOS Status | no | — | — |
| [`docs/status/PR1_GATE_SECTIONS.md`](./status/PR1_GATE_SECTIONS.md) | статус / трекер: PR1 — шаблон секций PIM PR Gate (для описания PR) | no | — | draft для копирования в PR description при открытии PR1 |
| [`docs/status/PR1_MERGE_VERIFICATION.md`](./status/PR1_MERGE_VERIFICATION.md) | статус / трекер: PR1 — merge verification (evidence, not design) | no | — | READY FOR MERGE (оба binary gate пройдены 2026-06-23) |
| [`docs/status/PR1_PREFLIGHT.md`](./status/PR1_PREFLIGHT.md) | статус / трекер: PR1 Pre-flight — Canon vs Code (Today spine) | no | — | Pre-flight complete — достаточен для старта реализации; код PR1 не начат |
| [`docs/status/PR2_GATE_SECTIONS.md`](./status/PR2_GATE_SECTIONS.md) | статус / трекер: PR2 — шаблон секций PIM PR Gate (для описания PR) | no | — | draft — заполнять при открытии PR2 |
| [`docs/status/PR2_PREFLIGHT.md`](./status/PR2_PREFLIGHT.md) | статус / трекер: PR2 Pre-flight — Canon vs Code (PIM write-path) | no | — | Pre-flight complete — достаточен для планирования PR2; код Goal Loop не начат |
| [`docs/status/PROFILE_FOUNDATION_QA.md`](./status/PROFILE_FOUNDATION_QA.md) | статус / трекер: Profile · Foundation QA (production Quick Map) | no | — | code-side pass · manual shape scroll — optional |
| [`docs/status/PROFILE_V0_IGOR_TAXONOMY_AUDIT.md`](./status/PROFILE_V0_IGOR_TAXONOMY_AUDIT.md) | статус / трекер: Profile taxonomy audit · Igor / Sage / 7 / Aquarius | no | — | — |
| [`docs/status/TODAY_CANON_VS_CODE_DIFF.md`](./status/TODAY_CANON_VS_CODE_DIFF.md) | статус / трекер: Today · Step A — Canon vs Code Diff | no | — | Step A complete — diff + Day Story v3 block map |
| [`docs/status/WEB_LAUNCH_EXECUTION_PLAN.md`](./status/WEB_LAUNCH_EXECUTION_PLAN.md) | статус / трекер: Web Launch v1 — Execution Plan | no | — | PROCESS FROZEN — режиссура истории в React; Figma не используем. |
| [`docs/status/WEB_LAUNCH_PRODUCT_BLUEPRINT.md`](./status/WEB_LAUNCH_PRODUCT_BLUEPRINT.md) | статус / трекер: Web Launch — Product Blueprint (Stage 0) | no | WEB_LAUNCH_EXECUTION_PLAN + screen canons | LAUNCH SCOPE FROZEN (2026-07-01) — execution only. |

### 5. Screen Maps

| Document | Purpose | Is SoT | Duplicates | Status |
|----------|---------|--------|------------|--------|
| [`docs/COMPATIBILITY_CONTENT_CANON_V1.md`](./COMPATIBILITY_CONTENT_CANON_V1.md) | живой канон: Compatibility Content Canon v1 | yes (interim until PR-2) | — | C2 engineering-closed для guest + registered under flag (publish_gate в production). Premi |
| [`docs/COMPATIBILITY_REVIEW_PACK_V1.md`](./COMPATIBILITY_REVIEW_PACK_V1.md) | прочее: Compatibility Review Pack v1 | no / review | — | — |
| [`docs/DAILY_NAVIGATION_MODEL.md`](./DAILY_NAVIGATION_MODEL.md) | продуктовая / доменная модель: Daily Navigation Model | partial / subordinate | — | принято (продуктовое ядро). |
| [`docs/PR2_APP_SHELL.md`](./PR2_APP_SHELL.md) | прочее: PR-2: Production App Shell | no / review | — | ACCEPTED / CLOSED (2026-07-21) |
| [`docs/PR3_TODAY_BLOCKS_REGISTRY.md`](./PR3_TODAY_BLOCKS_REGISTRY.md) | реестр промптов / блоков: Today Production Blocks Registry (PR-3 entry) | yes for Profile prompts (interim) | — | ACTIVE — Composition Surface honesty pass |
| [`docs/PR3_TODAY_PRODUCTION_SURFACE.md`](./PR3_TODAY_PRODUCTION_SURFACE.md) | прочее: PR-3: Today Production Surface | no / review | — | IN PROGRESS — Composition honesty pass (soft why + strengthen) |
| [`docs/PR4_PROFILE_CANON.md`](./PR4_PROFILE_CANON.md) | живой канон: PR-4 Profile Canon (surface) | yes (interim until PR-2) | — | CLOSED — slice 4.1 accepted (2026-07-21) |
| [`docs/PROFILE_CONTENT_CANON_V1.md`](./PROFILE_CONTENT_CANON_V1.md) | живой канон: Profile Content Canon v1 (C3) | yes (interim until PR-2) | — | принято для аудита и контракта (до переключения production generation). |
| [`docs/PROFILE_SCREEN_MASTER.md`](./PROFILE_SCREEN_MASTER.md) | прочее: Profile · Screen Master | no / review | PR4_PROFILE_CANON + PROFILE_CONTENT_CANON_V1 | CANON для visual/layout legacy v0; production IA — [PR4_PROFILE_CANON.md](./PR4_PROFILE_CA |
| [`docs/SCREEN_CONTRACTS_V1.md`](./SCREEN_CONTRACTS_V1.md) | технический контракт: Screen Contracts v1 | yes (interim until PR-2) | — | принято (foundation-first — до Engine Projection Specs). |
| [`docs/TODAYFLOW_FOUNDATION_UI.md`](./TODAYFLOW_FOUNDATION_UI.md) | прочее: TODAYFLOW_FOUNDATION_UI | yes (interim until PR-2) | — | ACTIVE — канон визуала всего сервиса (web · iOS · Android). |
| [`docs/TODAY_ANCHOR_TYPES_V0.md`](./TODAY_ANCHOR_TYPES_V0.md) | калибровка языка: TODAY_ANCHOR_TYPES_V0 | no | TODAY_LANGUAGE_V1 / calibration | `CALIBRATION_HYPOTHESIS` — не gate, не код. |
| [`docs/TODAY_CONTRACT_ASSEMBLER_MAPPING.md`](./TODAY_CONTRACT_ASSEMBLER_MAPPING.md) | технический контракт: Today Contract Assembler Mapping | partial / subordinate | — | принято (bridge legacy → Model B). |
| [`docs/TODAY_H4_VALIDATION_V0.md`](./TODAY_H4_VALIDATION_V0.md) | калибровка языка: TODAY_H4_VALIDATION_V0 — Observable Pattern Hypothesis | no | TODAY language calibration pack | `SUPPORTED` — preliminary editorial sign-off (2026-06-23) |
| [`docs/TODAY_INTERNAL_PATTERNS_V0.md`](./TODAY_INTERNAL_PATTERNS_V0.md) | калибровка языка: TODAY_INTERNAL_PATTERNS_V0 | no | TODAY_LANGUAGE_V1 / calibration | `CALIBRATION_HYPOTHESIS` — не gate, не код. |
| [`docs/TODAY_LANGUAGE_ANTI_PATTERNS_V0.md`](./TODAY_LANGUAGE_ANTI_PATTERNS_V0.md) | калибровка языка: TODAY_LANGUAGE_ANTI_PATTERNS_V0 — редакционный классификатор плохого текста | no | TODAY_LANGUAGE_V1 | `ACCEPTED` (editorial v0) |
| [`docs/TODAY_LANGUAGE_CALIBRATION_V0.md`](./TODAY_LANGUAGE_CALIBRATION_V0.md) | калибровка языка: TL-0 — Language Calibration | no | TODAY_LANGUAGE_V1 | `IN_PROGRESS` |
| [`docs/TODAY_LANGUAGE_STRONG_PATTERNS_V0.md`](./TODAY_LANGUAGE_STRONG_PATTERNS_V0.md) | калибровка языка: TODAY_LANGUAGE_STRONG_PATTERNS_V0 — библиотека драматургии сильного текста | no | TODAY_LANGUAGE_V1 | `ACCEPTED` (editorial v0) |
| [`docs/TODAY_LANGUAGE_V1.md`](./TODAY_LANGUAGE_V1.md) | прочее: TODAY_LANGUAGE_V1 — редакционный канон текста Today | no / review | — | `ACCEPTED` — источник истины для языка и качества копирайта на экране Today и связанных na |
| [`docs/TODAY_PERSONALIZATION_CORE.md`](./TODAY_PERSONALIZATION_CORE.md) | прочее: Ядро персонализации: Today (контракт, события, prompt) | yes (interim until PR-2) | — | канон для реализации Today после утреннего ритуала. |
| [`docs/TODAY_PRODUCT_MODEL.md`](./TODAY_PRODUCT_MODEL.md) | продуктовая / доменная модель: Today — продуктовая модель | partial / subordinate | — | принято (канон что такое экран Today и воронка формирования дня). |
| [`docs/TODAY_RAT_VALIDATION_V0.md`](./TODAY_RAT_VALIDATION_V0.md) | калибровка языка: TODAY_RAT_VALIDATION_V0 — Recognition Ablation Test | no | TODAY language calibration pack | `IN_PROGRESS` — pilot n=19, no sign-off |
| [`docs/TODAY_SCREEN_V1_CANON.md`](./TODAY_SCREEN_V1_CANON.md) | живой канон: Today Screen v1 — сценарий экрана (канон) | yes (interim until PR-2) | — | `ACCEPTED` — источник истины для experience layer Today v1. |
| [`docs/TODAY_SELF_VERIFICATION_V0.md`](./TODAY_SELF_VERIFICATION_V0.md) | калибровка языка: TODAY_SELF_VERIFICATION_V0 — H5 (Language) | no | TODAY_LANGUAGE_V1 / calibration | `CALIBRATION_HYPOTHESIS` — candidate; не gate, не код. |

## Counts

- Total markdown files under `docs/` (excluding README): **101**
- 1. Product Map: **10**
- 2. Technical Architecture: **36**
- 3. Generation Registry: **10**
- 4. Implementation Status: **21**
- 5. Screen Maps: **24**

## Next (PR-5, after allowlist)

Archive candidates: `Is SoT = no` and `Duplicates ≠ —`, only after unique decisions are merged into the five README sections.

