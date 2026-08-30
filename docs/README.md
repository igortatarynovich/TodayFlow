# Документация TodayFlow

Только **живой канон**. Ветки A–E (Evolution/Calendar/Symbolic/Practice registries), screen-pipeline, старые `spec/` и дублирующие спеки удалены **2026-06-23** — история в `PRODUCT_EXECUTION_TRACKER` changelog.

## С чего начать

| Слой | Документ |
|------|----------|
| **Product Canon (Unified)** | [TODAYFLOW_PRODUCT_CANON_UNIFIED.md](./TODAYFLOW_PRODUCT_CANON_UNIFIED.md) — Personal Model · карта продукта · законы · north star · монетизация |
| **Полный пользовательский путь (SoT маршрута)** | [audits/FULL_USER_PATH_CANON_V1.md](./audits/FULL_USER_PATH_CANON_V1.md) — Landing→Preview→Save→Claim→Profile · A–E |
| **User Journey (pointer)** | [USER_JOURNEY_CANON.md](./USER_JOURNEY_CANON.md) → FULL_USER_PATH |
| **Product Availability Matrix** | [PRODUCT_AVAILABILITY_MATRIX.md](./PRODUCT_AVAILABILITY_MATRIX.md) — **APPROVED (Profile)** · данные × экраны × слоты 3.1 · gate UI |
| **Data Intake (ровно 2 способа ввода)** | [PRODUCT_DATA_INTAKE.md](./PRODUCT_DATA_INTAKE.md) — публичный preview→email · добавить профиль · единая модель профиля |
| **Capability Contracts (уровни данных → API)** | [PRODUCT_CAPABILITY_CONTRACTS.md](./PRODUCT_CAPABILITY_CONTRACTS.md) — оркестратор · L1/L2/L3 · allowed_output |
| **Generation Contracts (ядро генерации)** | [PRODUCT_GENERATION_CONTRACTS.md](./PRODUCT_GENERATION_CONTRACTS.md) — Contract ⊕ Implementations (промпты = IP) |
| **Data Providers (астро + гео)** | [PRODUCT_DATA_PROVIDERS.md](./PRODUCT_DATA_PROVIDERS.md) — MVP: LLM natal_facts · geo thin |
| **Product Build Map** | [TODAYFLOW_PRODUCT_BUILD_MAP.md](./TODAYFLOW_PRODUCT_BUILD_MAP.md) — entity catalog · build order (не философия продукта) |
| **Personal Model ↔ code** | [audits/PERSONAL_MODEL_CODE_COMPLIANCE_2026-07-21.md](./audits/PERSONAL_MODEL_CODE_COMPLIANCE_2026-07-21.md) — P0 read-path · [P1 Experience wiring](./audits/PERSONAL_MODEL_EXPERIENCE_WIRING_P1_2026-07-21.md) |
| Launch gaps / DoD / code | [status/WEB_LAUNCH_EXECUTION_PLAN.md](./status/WEB_LAUNCH_EXECUTION_PLAN.md) — ⚠️ STALE |
| Launch UX feel (reference) | [status/WEB_LAUNCH_PRODUCT_BLUEPRINT.md](./status/WEB_LAUNCH_PRODUCT_BLUEPRINT.md) — ⚠️ STALE |
| Трекер работ | [PRODUCT_EXECUTION_TRACKER.md](./PRODUCT_EXECUTION_TRACKER.md) |
| **Human Explanatory Systems (research)** | [audits/HUMAN_EXPLANATORY_SYSTEMS_ANALYSIS.md](./audits/HUMAN_EXPLANATORY_SYSTEMS_ANALYSIS.md) — разбор объяснительных систем (не product SoT); intersection / retention; **запрет** прыжка в фичи TodayFlow до закрытия research |

## PIM · Intelligence

- [PERSONAL_INTELLIGENCE_LAYER.md](./pim/PERSONAL_INTELLIGENCE_LAYER.md) — сквозной канон: learning-aware, PIL pipeline
- [USER_KNOWLEDGE_MODEL.md](./pim/USER_KNOWLEDGE_MODEL.md) — Knowledge Atoms
- [INTENT_MODEL_V1.md](./INTENT_MODEL_V1.md) · [HUMAN_DECISION_MODEL_V1.md](./HUMAN_DECISION_MODEL_V1.md)
- [INTERPRETATION_LAYER_AND_REFERENCE.md](./explainability/INTERPRETATION_LAYER_AND_REFERENCE.md) — event ≠ meaning
- [KNOWLEDGE_ACQUISITION_AND_SIGNAL_POLICY.md](./KNOWLEDGE_ACQUISITION_AND_SIGNAL_POLICY.md)
- [API_MEMORY_AND_LEARNING_LAYER.md](./API_MEMORY_AND_LEARNING_LAYER.md) — LLM Call Gate, cache, ROI · **Cost Containment:** [LLM_QUALITY_AND_PROMPT_EVOLUTION.md](./LLM_QUALITY_AND_PROMPT_EVOLUTION.md)
- [COMPUTE_LIFECYCLE_AND_ARTIFACT_ECONOMICS_V1.md](./COMPUTE_LIFECYCLE_AND_ARTIFACT_ECONOMICS_V1.md) — **when to calculate / persist / LLM** (Profile layers · Shared Global Day · Personal Day · three ledgers). Payload: [audits/IL3_TO_SURFACE_PAYLOAD_AUDIT_2026-08-25.md](./audits/IL3_TO_SURFACE_PAYLOAD_AUDIT_2026-08-25.md)
- [CONTRADICTION_AND_REEVALUATION_V1.md](./CONTRADICTION_AND_REEVALUATION_V1.md)

## Data · Reference (фаза 1)

- [foundation_v1.md](./foundation_v1.md) — **Foundation v1 (единый SoT)** — геометрия ✅ · константы · маршрутизация · gate перед hooks/семантикой
- Domain magnitude: [foundation/DOMAIN_MAGNITUDE_V1.md](./foundation/DOMAIN_MAGNITUDE_V1.md) — calibrated valence weights (frozen extract)
- Color layer B: [color/COLOR_LAYER_B_V1.md](./color/COLOR_LAYER_B_V1.md) — 5 live + Champagne pending
- [DATA_ORIGINATION_AND_LIFECYCLE.md](./DATA_ORIGINATION_AND_LIFECYCLE.md)
- [DATA_OWNERSHIP_AND_CONSUMPTION_MAP.md](./DATA_OWNERSHIP_AND_CONSUMPTION_MAP.md)
- [REFERENCE_LAYER_AND_BUILD_ORDER.md](./REFERENCE_LAYER_AND_BUILD_ORDER.md) — JSON / Machine Contract build order (не порядок исследования смысла)
- [KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md](./KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md) — **порядок семантического ядра.** **Астрология IL (1.3.111):** calc → IL wire at library layer. Scale 1.3.110, IL-4 1.3.109, IL-3 1.3.108, IL-2 1.3.107 and freeze 1.3.106 stand. Five stored families = V1 atoms. STOP Angles. Next = attach IL-4 packs to product surfaces. Исторический корпус = lenses
- [KNOWLEDGE_CORE_V1_SEMANTIC_INVENTORY.md](./astrology/KNOWLEDGE_CORE_V1_SEMANTIC_INVENTORY.md) — **IL V1 freeze map (APPROVED):** что библиотека должна знать. **1.3.106 FROZEN** on stored primitives. Books только против named `KC-*` row. IL-1 done = минимальные primitives
- [KNOWLEDGE_CORE_V1_PRODUCT_CANON_AND_LENSES.md](./astrology/KNOWLEDGE_CORE_V1_PRODUCT_CANON_AND_LENSES.md) — **Product Canon vs Lenses (1.3.76):** Mainstream → Canon → runtime. Corpus → education / SEO / deep dives
- [astrology/MAINSTREAM_PLANET_SEMANTIC_MAP_V1.md](./astrology/MAINSTREAM_PLANET_SEMANTIC_MAP_V1.md) — **Mainstream planet map (1.3.77):** concept families. Not Canon, not JSON
- [astrology/MAINSTREAM_SIGN_SEMANTIC_MAP_V1.md](./astrology/MAINSTREAM_SIGN_SEMANTIC_MAP_V1.md) — **Mainstream sign map (1.3.83):** concept families. Not manner, not JSON
- [astrology/MAINSTREAM_HOUSE_SEMANTIC_MAP_V1.md](./astrology/MAINSTREAM_HOUSE_SEMANTIC_MAP_V1.md) — **Mainstream house map (1.3.89):** concept families. Not Canon, not JSON. House ≠ ASC
- [astrology/HOUSE_CANON_GRAMMAR_V1.md](./astrology/HOUSE_CANON_GRAMMAR_V1.md) — **House Canon grammar (1.3.90):** one slot (`arena`). Dry-run ≠ fill
- [astrology/HOUSE_CANON_V1.md](./astrology/HOUSE_CANON_V1.md) — **House Canon V1 (1.3.91):** twelve packs + provenance. Storage = 1.3.92 **done**
- [astrology/HOUSE_CANON_STORAGE_MATERIALIZATION_V1.md](./astrology/HOUSE_CANON_STORAGE_MATERIALIZATION_V1.md) — **House Canon storage + materialization (1.3.92):** `house_canon_pack` (`arena`); twelve drafts carry locked packs
- [astrology/HOUSE_CANON_COMPOSITION_SMOKE_V1.md](./astrology/HOUSE_CANON_COMPOSITION_SMOKE_V1.md) — **composition smoke (1.3.93):** PlanetInHouse PASS. STOP Houses
- [astrology/MAINSTREAM_ASPECT_SEMANTIC_MAP_V1.md](./astrology/MAINSTREAM_ASPECT_SEMANTIC_MAP_V1.md) — **Mainstream aspect map (1.3.94):** concept families. Relation ≠ theme. Not grammar, not JSON
- [astrology/ASPECT_CANON_GRAMMAR_V1.md](./astrology/ASPECT_CANON_GRAMMAR_V1.md) — **Aspect Canon grammar (1.3.95):** one slot (`relation`). Dry-run ≠ fill
- [astrology/ASPECT_CANON_V1.md](./astrology/ASPECT_CANON_V1.md) — **Aspect Canon V1 (1.3.96):** five packs + provenance. Storage = 1.3.97 **done**
- [astrology/ASPECT_CANON_STORAGE_MATERIALIZATION_V1.md](./astrology/ASPECT_CANON_STORAGE_MATERIALIZATION_V1.md) — **Aspect Canon storage + materialization (1.3.97):** `aspect_canon_pack` (`relation`); five drafts carry locked packs; `interaction` unchanged
- [astrology/ASPECT_CANON_COMPOSITION_SMOKE_V1.md](./astrology/ASPECT_CANON_COMPOSITION_SMOKE_V1.md) — **composition smoke (1.3.98):** stored Planet × Aspect PASS. STOP Aspects
- [astrology/ANGLE_CANON_MODEL_V1.md](./astrology/ANGLE_CANON_MODEL_V1.md) — **Angle Canon model (1.3.99):** parent 1–4. Orientation loci. Not fill
- [astrology/MAINSTREAM_ANGLE_SEMANTIC_MAP_V1.md](./astrology/MAINSTREAM_ANGLE_SEMANTIC_MAP_V1.md) — **Mainstream angle map (1.3.100):** concept families. House 1/10 not proof. Not grammar
- [astrology/ANGLE_CANON_GRAMMAR_V1.md](./astrology/ANGLE_CANON_GRAMMAR_V1.md) — **Angle Canon grammar (1.3.101):** one slot (`orientation`). Include-first. Secondary = collision-zone. Not fill
- [astrology/ANGLE_CANON_STORAGE_MATERIALIZATION_V1.md](./astrology/ANGLE_CANON_STORAGE_MATERIALIZATION_V1.md) — **Angle Canon storage (1.3.103):** `angle_canon_pack`; two drafts. Smoke **done 1.3.104**
- [astrology/ANGLE_CANON_COMPOSITION_SMOKE_V1.md](./astrology/ANGLE_CANON_COMPOSITION_SMOKE_V1.md) — **composition smoke (1.3.104):** stored Planet × Angle PASS. Occupancy ≠ conjunction. STOP Angles
- [astrology/ATOMIC_CANON_COMPOSITION_SMOKE_V1.md](./astrology/ATOMIC_CANON_COMPOSITION_SMOKE_V1.md) — **final atomic smoke (1.3.105):** five stored families. Operators discriminate. FREEZE **done 1.3.106**
- [astrology/KNOWLEDGE_CORE_V1_FREEZE.md](./astrology/KNOWLEDGE_CORE_V1_FREEZE.md) — **Knowledge Core V1 FREEZE (1.3.106):** five stored families = V1 atoms. Catalog 38 draft / 0 active. IL-2 **done 1.3.107**. IL-3 **done 1.3.108**. IL-4 **done 1.3.109**. Library scale **done 1.3.110**. Wire **done 1.3.111**. Attach **done 1.3.112**. Consume **done 1.3.113**.
- [astrology/IL2_COMPOSITION_RULES_V1.md](./astrology/IL2_COMPOSITION_RULES_V1.md) — **IL-2 composition rules (1.3.107):** role weights, conflict, merge. Not a pair catalog. IL-3 **done 1.3.108**. IL-4 **done 1.3.109**. Library scale **done 1.3.110**. Wire **done 1.3.111**. Attach **done 1.3.112**. Consume **done 1.3.113**.
- [astrology/IL3_INTERPRETATION_ENGINE_V1.md](./astrology/IL3_INTERPRETATION_ENGINE_V1.md) — **IL-3 Interpretation Engine (1.3.108):** sky-internal theme rank. Not user relevance. IL-4 **done 1.3.109**. Library scale **done 1.3.110**. Wire **done 1.3.111**. Attach **done 1.3.112**. Consume **done 1.3.113**.
- [astrology/IL4_EXPRESSION_V1.md](./astrology/IL4_EXPRESSION_V1.md) — **IL-4 Expression (1.3.109):** voice for already chosen themes. Not meaning. Library scale **done 1.3.110**. Wire **done 1.3.111**. Attach **done 1.3.112**. Consume **done 1.3.113**.
- [astrology/LIBRARY_SCALE_V1.md](./astrology/LIBRARY_SCALE_V1.md) — **Library scale (1.3.110):** V1 coverage contract. 616 composed cells. Wire live at library layer 1.3.111. Attach **done 1.3.112**. Consume **done 1.3.113**.
- [astrology/CALC_IL_WIRE_V1.md](./astrology/CALC_IL_WIRE_V1.md) — **Calc → IL wire (1.3.111):** library layer. Attach **done 1.3.112**. Consume **done 1.3.113**.
- [astrology/IL4_SURFACE_ATTACH_V1.md](./astrology/IL4_SURFACE_ATTACH_V1.md) — **IL-4 surface attach (1.3.112):** LLM input `il4_expression_pack`. Public JSON unchanged. Consume **done 1.3.113**.
- [astrology/IL4_EDITORIAL_CONSUME_V1.md](./astrology/IL4_EDITORIAL_CONSUME_V1.md) — **IL-4 editorial consume (1.3.113):** generation phrases packs. Fill-empty / reject-invalid. Public JSON unchanged. Polish **done 1.3.114**. Compat editorial **done 1.3.115**.
- [today/TODAY_MEANING_POLISH_V1.md](./today/TODAY_MEANING_POLISH_V1.md) — **Today meaning polish (1.3.114):** native astrology chorus binds to IL-4. Prompt c4.2. Public JSON unchanged. Compat editorial **done 1.3.115**. Profile polish **done 1.3.123**.
- [profile/PROFILE_MEANING_POLISH_V1.md](./profile/PROFILE_MEANING_POLISH_V1.md) — **Profile meaning polish (1.3.123):** Natal Decode sky theses bind to IL-4. Identity Core stays CE. Prompt 1.1.0. Public JSON unchanged.
- [profile/PROFILE_NATAL_DECODE_CACHE_REFRESH_V1.md](./profile/PROFILE_NATAL_DECODE_CACHE_REFRESH_V1.md) — **Natal Decode cache refresh (1.3.124):** ops one-shot onto v0.3 fingerprint. GET never rebuilds.
- [astrology/COMPAT_SYNASTRY_EDITORIAL_IL4_V1.md](./astrology/COMPAT_SYNASTRY_EDITORIAL_IL4_V1.md) — **Compatibility synastry editorial IL-4 (1.3.115):** editorial phrases packs when charts supplied. Prompt v1.1. Public JSON unchanged.
- [astrology/ANGLE_CANON_V1.md](./astrology/ANGLE_CANON_V1.md) — **Angle Canon V1 (1.3.102):** two packs + origin. Collision vs House 1/10. Stored 1.3.103
- [astrology/SIGN_CANON_GRAMMAR_V1.md](./astrology/SIGN_CANON_GRAMMAR_V1.md) — **Sign Canon grammar (1.3.84):** manner · excess. Dry-run ≠ fill
- [astrology/SIGN_CANON_V1.md](./astrology/SIGN_CANON_V1.md) — **Sign Canon V1 (1.3.85):** twelve packs + provenance. Storage = 1.3.86
- [astrology/SIGN_CANON_STORAGE_V1.md](./astrology/SIGN_CANON_STORAGE_V1.md) — **Sign Canon storage (1.3.86):** optional `canon` nest on signs (`manner` · `excess`)
- [astrology/SIGN_CANON_MATERIALIZATION_V1.md](./astrology/SIGN_CANON_MATERIALIZATION_V1.md) — **Sign Canon materialization (1.3.87):** twelve drafts carry locked packs
- [astrology/PLANET_CANON_GRAMMAR_V1.md](./astrology/PLANET_CANON_GRAMMAR_V1.md) — **Planet Canon grammar (1.3.78):** engine slots. tempo not Canon. Dry-run ≠ fill
- [astrology/PLANET_CANON_V1.md](./astrology/PLANET_CANON_V1.md) — **Planet Canon V1 (1.3.79):** ten packs + provenance. Storage = 1.3.80
- [astrology/PLANET_CANON_STORAGE_V1.md](./astrology/PLANET_CANON_STORAGE_V1.md) — **Planet Canon storage (1.3.80):** optional `canon` nest
- [astrology/PLANET_CANON_SUN_SATURN_FILL_V1.md](./astrology/PLANET_CANON_SUN_SATURN_FILL_V1.md) — **Sun–Saturn fill (1.3.81):** product `canon` on seven drafts
- [astrology/PLANET_CANON_COMPOSITION_SMOKE_V1.md](./astrology/PLANET_CANON_COMPOSITION_SMOKE_V1.md) — **composition smoke (1.3.82):** aspect PASS; sign/house PARTIAL *(house PARTIAL = snapshot after 1.3.93)*
- [audits/COSTAR_SEMANTIC_CONTENT_ENGINE_TEARDOWN_V1.md](./audits/COSTAR_SEMANTIC_CONTENT_ENGINE_TEARDOWN_V1.md) — Co–Star teardown Phase 0: **recognition check**, не источник смысла
- [TODAYFLOW_CANON_V1.md](./astrology/TODAYFLOW_CANON_V1.md) — **структуризация Mainstream** в Canon-атомы. Runtime: атомы → композиция → LLM формулирует. CORE не gate
- [DAYMODEL_INPUT_CONTRACT.md](./DAYMODEL_INPUT_CONTRACT.md)
- [ASTROLOGY_MACHINE_CONTRACT.md](./ASTROLOGY_MACHINE_CONTRACT.md) · [ASTROLOGY_COMPOSITION_MODEL.md](./ASTROLOGY_COMPOSITION_MODEL.md) · [CROSS_DOMAIN_MACHINE_VALIDATION.md](./CROSS_DOMAIN_MACHINE_VALIDATION.md)
- Astrology meaning: [astrology/INTERPRETATION_LIBRARY_V1.md](./astrology/INTERPRETATION_LIBRARY_V1.md) — **Interpretation Library** (semantic objects; IL-1 drafts, nothing `active`). Corpus: `DATA/reference/astrology/interpretation_v1/source_corpus_v1.json`. Index: [astrology/_INDEX.md](./astrology/_INDEX.md). Публичный язык Canon ≠ IL: [content/TODAYFLOW_TRUST_LAYER.md](./content/TODAYFLOW_TRUST_LAYER.md)
- [EVOLUTION_CALCULATION_CONTRACT.md](./EVOLUTION_CALCULATION_CONTRACT.md) — **запрет `evolution_stage` в API** до UEM-2
- Tarot: [tarot/TAROT_INTERPRETATION_ENGINE_V1.md](./tarot/TAROT_INTERPRETATION_ENGINE_V1.md) · [tarot/TAROT_CARD_BASE_V1.md](./tarot/TAROT_CARD_BASE_V1.md) (base meanings SoT) · [tarot/TAROT_DESIGN_LANGUAGE_V1.md](./tarot/TAROT_DESIGN_LANGUAGE_V1.md)
- Numerology: [numerology/NUMBER_BASE_V1.md](./numerology/NUMBER_BASE_V1.md) (digit SoT) · [numerology/NUMEROLOGY_INTEGRATION_SPEC_V1.md](./numerology/NUMEROLOGY_INTEGRATION_SPEC_V1.md)
- Day hooks reveal: [audits/DAY_SYMBOL_REVEAL_CANON_V1.md](./audits/DAY_SYMBOL_REVEAL_CANON_V1.md) — `hook_reveal` · chorus = sole bridge

## Today · Profile (experience)

**Today Meaning SoT (один):** [today/TODAY_CONTENT_PIPELINE_V1.md](./today/TODAY_CONTENT_PIPELINE_V1.md) — Небо → Global Day → Natal Overlay → Ritual → Personal → Presentation. Step 2 lookup = [astrology/INTERPRETATION_LIBRARY_V1.md](./astrology/INTERPRETATION_LIBRARY_V1.md) (не второй канон дня).  
**Today product cycle (экраны):** [today/TODAY_PRODUCT_FLOW_V1.md](./today/TODAY_PRODUCT_FLOW_V1.md) — TODAY → RITUAL → MY DAY → EVENING. Не плодить второй канон смысла.  
**Display contracts (последний authority перед UI):** [foundation/DISPLAY_CONSTRUCTION_GRAMMAR_V1.md](./foundation/DISPLAY_CONSTRUCTION_GRAMMAR_V1.md) (закон) · [profile/PROFILE_DISPLAY_INVENTORY_V1.md](./profile/PROFILE_DISPLAY_INVENTORY_V1.md) · [today/TODAY_DISPLAY_INVENTORY_V1.md](./today/TODAY_DISPLAY_INVENTORY_V1.md). Слот вне Inventory = нет в продукте. Новый слот только через запись + Architecture impact.

- [today/TODAY_CONTENT_PIPELINE_V1.md](./today/TODAY_CONTENT_PIPELINE_V1.md) — **единственный канон смысла / content pipeline Today**
- [today/TODAY_PRODUCT_FLOW_V1.md](./today/TODAY_PRODUCT_FLOW_V1.md) — **единственный канон продуктового цикла / ScreenFlow Today**
- [today/TODAY_DISPLAY_INVENTORY_V1.md](./today/TODAY_DISPLAY_INVENTORY_V1.md) — **слоты Сегодня** (последний authority перед UI)
- [foundation/DISPLAY_CONSTRUCTION_GRAMMAR_V1.md](./foundation/DISPLAY_CONSTRUCTION_GRAMMAR_V1.md) — **закон конструкции** (цепочка · 5 ограничений · FE не invent)
- [DAY_SOURCES_CANON.md](./DAY_SOURCES_CANON.md) — SoT **расчёта фактов** (не сюжет); питает Global Day
- [today/TODAY_SCREEN_SCENARIO_V3.md](./today/TODAY_SCREEN_SCENARIO_V3.md) — **SUPERSEDED** как product map; current-code until cutover
- [TODAYFLOW_FOUNDATION_UI.md](./TODAYFLOW_FOUNDATION_UI.md) — **visual** SoT (§2 ten-layer language · natal as composition · §11 Day Atmosphere)
- [DAY_SCENARIO_V1.md](./DAY_SCENARIO_V1.md) — legacy engine notes / I0–I8 hygiene (**не** Meaning SoT)
- [TODAY_SCREEN_V1_CANON.md](./TODAY_SCREEN_V1_CANON.md) — experience layer (ритуал/goal loop); meaning → pipeline
- [today/TODAY_WAVE2_EXECUTION_PLAN.md](./today/TODAY_WAVE2_EXECUTION_PLAN.md) — Wave 2 action plan (Tap → Verdict → Glance)
- [today/TODAY_WAVE2_CONTRACT_V1.md](./today/TODAY_WAVE2_CONTRACT_V1.md) — `day_facts_v1` + slots (**CONTRACT LOCKED**)
- [today/TODAY_MOTION_PILOT_V1.md](./today/TODAY_MOTION_PILOT_V1.md) — Today attention motion pilot (TapWidget)
- [TODAY_LANGUAGE_V1.md](./today-language/TODAY_LANGUAGE_V1.md) — язык и quality gate копирайта
- [TODAY_PRODUCT_MODEL.md](./TODAY_PRODUCT_MODEL.md) · [FIRST_DAY_EXPERIENCE.md](./FIRST_DAY_EXPERIENCE.md) — **guest → onboarding → First Today** (route contract v2)
- [TODAY_PERSONALIZATION_CORE.md](./TODAY_PERSONALIZATION_CORE.md) — контракт, events, prompts (web + iOS)
- [TODAY_CONTRACT_ASSEMBLER_MAPPING.md](./TODAY_CONTRACT_ASSEMBLER_MAPPING.md) · [SCREEN_CONTRACTS_V1.md](./SCREEN_CONTRACTS_V1.md)
- [DAY_ENGINE_AND_COHERENCE.md](./DAY_ENGINE_AND_COHERENCE.md) · [DAY_CONTEXT_V0.md](./DAY_CONTEXT_V0.md) — указатели → pipeline
- [DAY_SOURCE_REGISTRY.md](./DAY_SOURCE_REGISTRY.md) · [PROFILE_DAY_SOURCE_MATRIX.md](./profile/PROFILE_DAY_SOURCE_MATRIX.md)
- [PROFILE_SCREEN_MASTER.md](./profile/PROFILE_SCREEN_MASTER.md) · [profile/PROFILE_EXPERIENCE_SCENARIO_V1.md](./profile/PROFILE_EXPERIENCE_SCENARIO_V1.md) — **Character Engine** (единая модель личности) · [profile/PROFILE_DISPLAY_INVENTORY_V1.md](./profile/PROFILE_DISPLAY_INVENTORY_V1.md) — **конструкция экрана Profile** (блоки · provenance · лимиты) · [profile/PROFILE_NATAL_DECODE_DEPTH_V1.md](./profile/PROFILE_NATAL_DECODE_DEPTH_V1.md) — Natal Decode (opt-in depth)
- [foundation/SCREEN_FLOW_V1.md](./foundation/SCREEN_FLOW_V1.md) — **ScreenFlow** pager (transform · landing excluded)
- [foundation/DISPLAY_CONSTRUCTION_GRAMMAR_V1.md](./foundation/DISPLAY_CONSTRUCTION_GRAMMAR_V1.md) — **закон конструкции** экранов Profile / Today
- [practices/PRACTICE_CONTENT_TAXONOMY_V1.md](./practices/PRACTICE_CONTENT_TAXONOMY_V1.md) — **библиотека практик** SoT: class → type → purpose/state/domain; Canonical Technique → Item
- [practices/PRACTICE_LIBRARY_FILL_V1.md](./practices/PRACTICE_LIBRARY_FILL_V1.md) — **наполнение библиотеки**: lightweight provenance; accepted/skipped → Content Item
- [practices/PRACTICE_TECHNIQUE_PROVENANCE_V1.md](./practices/PRACTICE_TECHNIQUE_PROVENANCE_V1.md) — **происхождение техники**: одна запись на технику; LLM не источник метода
- [practices/PRACTICE_TECHNIQUE_RESEARCH_ARCHIVE_V1.md](./practices/PRACTICE_TECHNIQUE_RESEARCH_ARCHIVE_V1.md) — **архив research-лестницы** (Landscape → … → Targeted Safety): historical, non-blocking
- [practices/PRACTICE_CONTENT_COVERAGE_V1.md](./practices/PRACTICE_CONTENT_COVERAGE_V1.md) — **coverage-first fill**: 26 P0 need cells; sourced 18/26; next = `need.discipline.prepare`
- [practices/PRACTICES_SCREEN_V1.md](./practices/PRACTICES_SCREEN_V1.md) — **Практики** SoT экрана: цикл состояния · locked need/format · сессия · music layer ([index](./practices/_INDEX.md))
- [DAILY_NAVIGATION_MODEL.md](./DAILY_NAVIGATION_MODEL.md) · [CORE_USER_LOOP.md](./CORE_USER_LOOP.md) · [MARKET_ATTENTION_AND_SCREEN_JOBS.md](./MARKET_ATTENTION_AND_SCREEN_JOBS.md)
- [EXPLAIN_MEANING_NOT_MECHANISM.md](./explainability/EXPLAIN_MEANING_NOT_MECHANISM.md)
- **Brand / Trust (копирайт лендинга и рекламы):** [content/TODAYFLOW_TRUST_LAYER.md](./content/TODAYFLOW_TRUST_LAYER.md) — лендинг = бренд-поверхность (H1 = locked line); точность NASA/JPL + многослойный Canon; in-product голос остаётся [TODAYFLOW_VOICE_CANON.md](./content/TODAYFLOW_VOICE_CANON.md) ([index](./content/_INDEX.md))

## Статусы · схемы · i18n

- [TODAYFLOW_PRODUCT_BUILD_MAP.md](./TODAYFLOW_PRODUCT_BUILD_MAP.md) — entity catalog · build order
- [status/RELEASE_PLAN_V1.md](./status/RELEASE_PLAN_V1.md) — path to soft launch · gates · success criteria · **ACTIVE**
- [status/WEB_LAUNCH_EXECUTION_PLAN.md](./status/WEB_LAUNCH_EXECUTION_PLAN.md) — historical gaps · DoD · Decision Log — SUPERSEDED by `RELEASE_PLAN_V1.md`
- [status/WEB_LAUNCH_PRODUCT_BLUEPRINT.md](./status/WEB_LAUNCH_PRODUCT_BLUEPRINT.md) — screen feel/do (reference) — ⚠️ STALE
- [status/BEHAVIOR_CHANGE_TEST_V0.md](./status/BEHAVIOR_CHANGE_TEST_V0.md) — **Minimum Day Cycle** ship gate (Evening Close + Tomorrow) · behavior test BLOCKED
- [status/IOS_TODAYFLOW_STATUS.md](./status/IOS_TODAYFLOW_STATUS.md) — web + iOS направление
- [status/TODAY_CANON_VS_CODE_DIFF.md](./status/TODAY_CANON_VS_CODE_DIFF.md) — diff канон ↔ код
- [status/PROFILE_FOUNDATION_QA.md](./status/PROFILE_FOUNDATION_QA.md) — Profile Quick Map vs Foundation §9 (code-side)
- `docs/schemas/` — JSON Schema (CI: `today-contract-schema`, `day-context-schema`, `compact-user-model-schema`; Character Engine: `scripts/validate_character_engine_contract.py`, CI job pending workflow scope)
- `docs/i18n/` — правила перевода

## Правило чтения

При расхождении приоритет (сверху вниз):

0. [audits/FULL_USER_PATH_CANON_V1.md](./audits/FULL_USER_PATH_CANON_V1.md) — **путь пользователя** (после A–E)
1. [TODAYFLOW_PRODUCT_CANON_UNIFIED.md](./TODAYFLOW_PRODUCT_CANON_UNIFIED.md) — **канон продукта** (Personal Model, карта, законы, north star)
2. **Today смысл / content:** [today/TODAY_CONTENT_PIPELINE_V1.md](./today/TODAY_CONTENT_PIPELINE_V1.md) — **единственный**; не DAY_SCENARIO_V1, не B5, не DayModel §10
3. [TODAY_SCREEN_V1_CANON.md](./TODAY_SCREEN_V1_CANON.md) · [today/TODAY_PRODUCT_FLOW_V1.md](./today/TODAY_PRODUCT_FLOW_V1.md) — experience / product cycle (подчинены п.2 для смысла; нарезка экрана — PRODUCT_FLOW)
3a. [today/TODAY_DISPLAY_INVENTORY_V1.md](./today/TODAY_DISPLAY_INVENTORY_V1.md) — слоты Сегодня (**последний authority перед UI**; грамматика — [DISPLAY_CONSTRUCTION_GRAMMAR_V1](./foundation/DISPLAY_CONSTRUCTION_GRAMMAR_V1.md))
4. [profile/PROFILE_SCREEN_MASTER.md](./profile/PROFILE_SCREEN_MASTER.md) — уровень UI Profile
4a. [profile/PROFILE_DISPLAY_INVENTORY_V1.md](./profile/PROFILE_DISPLAY_INVENTORY_V1.md) — слоты Profile (последний authority перед UI)
5. [TODAYFLOW_PRODUCT_BUILD_MAP.md](./TODAYFLOW_PRODUCT_BUILD_MAP.md) — entity catalog / build order
6. [PRODUCT_EXECUTION_TRACKER.md](./PRODUCT_EXECUTION_TRACKER.md) — статус работ

Screen-level и PIM-слой (`pim/`, `today-language/`, `explainability/`) — уточняют unified, не заменяют его.  
**Не плодить** второй «канон дня» / «Meaning SoT» рядом с `TODAY_CONTENT_PIPELINE_V1`.

**Visual SoT:** [TODAYFLOW_FOUNDATION_UI.md](./TODAYFLOW_FOUNDATION_UI.md) — статика + §2 ten-layer language + **§2.7 Moon = live object (no stars)** + **§18 motion budget** (landing 7/10 · app 2–3/10 · share 5/10) + §11–§15 (Day Atmosphere · DS). Параллельный premium/design-канон не заводить. Figma вне рабочего контура.

## Правило записи (обязательно)

**Сначала найти — потом писать.** Cursor rule (local): `.cursor/rules/docs-single-canon.mdc`.

Перед созданием **любого** нового файла в `docs/`:

1. Пройти индекс **этого README** — тема уже покрыта?
2. Поиск по `docs/**/*.md` (и при необходимости `PRODUCT_EXECUTION_TRACKER`) по ключевым словам.
3. Если документ есть → **дополнить существующий**, не плодить `_V2`, `*_MAP`, `*_REGISTRY`, `branch_*`.
4. Новый файл — только при явном пробеле в каноне + строка здесь + запись в `PRODUCT_EXECUTION_TRACKER`.
5. **Потолок корня `docs/`:** ~15 `.md` файлов. Новый файл в корне — только с явным обоснованием, почему он не влезает в существующую подпапку (`profile/`, `pim/`, `today-language/`, `explainability/`, `status/`, `audits/`, `archive/`, …). Иначе — сразу в тематическую папку с `_INDEX.md`.

**Не создавать:** параллельные карты/реестры, `spec/`, snapshot на каждый PR, второй SoT на ту же фичу.

**Куда писать по умолчанию:** трекер (статус работ) · канон экрана (`TODAY_SCREEN_V1_CANON`, `profile/PROFILE_SCREEN_MASTER`) · `pim/` · OpenAPI/schemas.

**Архив:** закрытые PR-снимки и superseded-каноны — в [`archive/`](./archive/). Launch-доки со `⚠️ STALE` в `status/` — не читать как текущий SoT; путь пользователя — [FULL_USER_PATH_CANON_V1](./audits/FULL_USER_PATH_CANON_V1.md).
