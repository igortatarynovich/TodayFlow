# Character Engine — Runtime Inventory v0

**Status:** ACTIVE — inventory before Architecture Impact / schema  
**Date:** 2026-07-25  
**Canon:** [PROFILE_EXPERIENCE_SCENARIO_V1.md](../profile/PROFILE_EXPERIENCE_SCENARIO_V1.md) §8  
**Rule:** Не проектировать CE Snapshot schema поверх неизвестных jobs. Этот документ = вход в Architecture Impact.

---

## 0. Verdict (одной страницей)

| | |
|---|---|
| **Целевой publish path** | `ensure_natal_facts` → `generate_personality` (`profile.personality.v1`) → `profile_contract_v1` → `core_profile_snapshots` |
| **Живой параллельный builder** | Disclosure funnel (`profile.identity|styles|patterns` + spheres synthesis + chart_reading) + oneshot `_PROFILE_SYS_RU` |
| **Хранилище личности сегодня** | DB `core_profile_snapshots.payload` (+ ephemeral matrix/why/nodes на GET) |
| **Главный риск** | Два способа собрать «кто ты» в одном Snapshot + template/editorial/thematic roots вне Snapshot |
| **Миграционное правило** | Не держать новый CE cascade параллельно со старыми roots дольше переходного окна |

**Правильный порядок (подтверждён):**  
Inventory → Architecture Impact → schema → pipeline → adapters → Shadow comparison → reader migration → kill old roots → cleanup.

---

## 1. Publish graph (факт)

```text
POST /account/core-profile/refresh | core-setup | astro save
  → CoreProfileService._publish_portrait  (services/core_profile.py)
      → ensure_natal_facts_for_profile     (ensure_natal_facts_v0.py)
      → build_profile_portrait_v1          (profile_contract_v1.py)
           ├─ preferred: generate_personality  (personality_contract_v1.py)
           │             → personality_to_profile_contract
           └─ fallback:  disclosure funnel OR oneshot OR forming shell
      → INSERT/UPDATE core_profile_snapshots
      → generation_logs (module=profile_contract_v1)

GET /account/core-profile
  → snapshot | baseline shell
  → ephemeral: natal_summary, profile_matrix_v0, portrait_why_v0,
               insight_nodes_v0, effort_vector_v0, bridge_line_v0
  → NEVER portrait LLM on read
```

---

## 2. Roots inventory (минимальный результат)

Легенда fate: **D** delete · **A** temporary adapter · **P** projection assembler · **F** facts-only keep · **CE** evolve into Character Engine root.

### 2.1 Generation / meaning roots

| Root | Contract / module | Prompt ID | Launcher | Storage | API | FE / other deps | Fate | Migration risk |
|------|-------------------|-----------|----------|---------|-----|-----------------|------|----------------|
| **natal_facts** | `natal_facts_contract_v1.py` | `profile.natal_facts.v1` | `ensure_natal_facts` on publish; `POST /profile/natal-facts` | `cached_natal_charts.chart_metadata.natal_facts` | natal-facts + feed portrait | Matrix / guest claim | **F** (позже calc-first) | Dual authority vs Swiss ephemeris |
| **personality** | `personality_contract_v1.py` | `profile.personality.v1` | `build_profile_portrait_v1` if natal_facts | Nested → `payload.profile_contract_v1` | via core-profile after publish | Profile V2 journey; ExperienceSlice | **CE** | Schema ≠ CE cascade yet; house nulls; strict_relaxed |
| **disclosure funnel** | `profile_disclosure_funnel_v0.py` | `profile.identity.v1` · `styles.v1` · `patterns.v1` · `spheres.synthesis.v1` · `chart_reading.v1` | Fallback when personality unavailable | Same Snapshot | core-profile | Capture / journey tests | **D** (flag quarantine first) | Invents full portrait **without** natal_facts |
| **oneshot portrait** | `profile_contract_v1.call_profile_contract_llm_v1` | none (`_PROFILE_SYS_RU`) | When funnels off + no personality | Same Snapshot | core-profile | — | **D** | Unversioned prompt |
| **forming shell** | `build_profile_contract_forming_v1` | none | On LLM/validation fail | Snapshot `status=forming/partial` | core-profile | FE forming gates | **A** (UX only) | Hash lock + 300s retry; identity keep |
| **life_spheres synthesis** | `life_spheres_synthesis_run_v0.py` | `profile.spheres.synthesis.v1` | Funnel spheres step | `profile_contract_v1.life_spheres` | core-profile | `profileLifeSpheres.ts`, Effort scene | **P** ← CE scenes | love/money/work essays as roots today |
| **natal interpreter templates** | `natal_chart_interpreter.py` | none | On-read `/natal-chart/?include_interpretations` | Response only | `/natal-chart/` | Personal Map | **A→D** as character SoT | Parallel «who you are» |
| **natal editorial LLM** | `natal_chart_editorial.py` | learning `natal-chart-editorial-v2` (not registry) | `include_editorial` | generation_logs (+ reuse) | `/natal-chart/` editorial | Personal Map | **D** as meaning root | gifts/tensions invent character |
| **thematic reports** | `thematic_reports.py` | service-internal | `POST /reports/thematic/*` | report response | thematic APIs | reports UI | **D** as character root | career/love/family from birth alone |
| **numerology explainer** | `core/numerology_explainer.py` | unregistered | numerology / ritual paths | generation_logs | numerology APIs | name pages | **A** → name_numerology + CE | Parallel identity voice |
| **compat editorial/LLM** | `compatibility_*` | mostly unregistered | compat endpoints | `cached_compatibility` | `/compatibility/*` | Compat FE | **A** pair Experience | Pair meaning outside CE scenes |
| **day/guide funnels** | `surface_disclosure_funnel_v0` · `guide_narrative_funnel_v0` | `day.*` prompt family | Today pipeline | day payloads | today APIs | Today FE | keep **day** roots; **forbid** stable person invent | Thin Snapshot → day becomes de-facto personality |
| **career_analysis** | `career_analysis.py` | none | **unwired** | — | — | — | **D** | Dead deterministic career meaning |
| **legacy profile_interpreter** | `core/profile_interpreter.py` | unregistered | **no callers** | would log | — | — | **D** | Orphan |

### 2.2 Snapshot / projection / facts (not generative roots)

| Unit | Module | Prompt | Storage | API | Consumers | Fate |
|------|--------|--------|---------|-----|-----------|------|
| **CoreProfile Snapshot** | `core_profile.py` | — | `core_profile_snapshots` · cache TTL 900s | `GET/POST /account/core-profile*` | all Profile + Experience | **F+store**; stop inventing meaning |
| **Swiss natal calc** | `natal_chart_cache.py` | — | `cached_natal_charts.positions/houses` | `/natal-chart/`, reports | chart UI | **F** preferred calc SoT |
| **header knowledge** | `profile_header_knowledge_v0.py` | — | ephemeral on GET/publish | core-profile | header | **F** |
| **baseline archetype** | `profile_baseline_archetype_v0.py` | — | Snapshot `baseline` | core-profile | portrait_why | **F** (seed ≠ prose) |
| **matrix adapter** | `profile_matrix_adapter_v0.py` | — | ephemeral `profile_matrix_v0` | core-profile | `profileMatrixAccess.ts` | **P** |
| **portrait_why / insight_nodes / effort / bridge** | `profile_*_projection_v0.py` | — | ephemeral `*_v0` | core-profile | V2 journey | **P** |
| **ExperienceSlice** | `experience_contract_assembler_v0.py` | — | derived | Today/Compat/Tarot/day | surfaces | **P** |
| **CUM** | `compact_user_model_v0.py` | — | assembled | `/account/compact-user-model` | learning UI | **P** (not portrait gen) |
| **profile_content_v1 gates** | `profile_content_v1/*` | — | eligibility only | — | funnel depth | **F**/evolve schemas |

### 2.3 Canon-only IDs (no BE generative root — do not add)

`relationships` · `career` · `money` · `growth` · `base_astrology` · `name_numerology` (as interpretation roots) — **projection assembler only**.  
**Δ:** semantic dual roots still live as **fields inside** `personality` / funnel / `life_spheres` / `interpretation.life_areas`.

---

## 3. Registry prompt IDs (profile)

| prompt_id | Live caller | CE action |
|-----------|-------------|-----------|
| `profile.natal_facts.v1` | natal_facts / ensure | keep facts |
| `profile.personality.v1` | personality_contract | **evolve → CE cascade** |
| `profile.identity.v1` | disclosure funnel | kill after CE |
| `profile.styles.v1` | disclosure funnel | kill after CE |
| `profile.patterns.v1` | disclosure funnel (gated) | kill / fold into CE tensions |
| `profile.spheres.synthesis.v1` | life_spheres + funnel | fold into CE scenes assembler |
| `profile.spheres.v1` | **registered, not called** | remove from registry |
| `profile.chart_reading.v1` | disclosure funnel optional | kill / Evidence Graph |

---

## 4. Frontend consumers (clusters)

| Cluster | Key paths | Reads | Fate |
|---------|-----------|-------|------|
| **V2 journey (primary)** | `ProfileV2SystemScreen` · Recognition/Why/Character/Insight/Effort scenes · `buildProfileJourneyProjection` · `buildProfileFirstScreenProjection` · `buildProfileQuickMapData` | `profile_contract_v1` + `*_v0` projections | **CE reader** |
| **Matrix explore** | `buildProfileProgressiveDetailsProjection` | `profile_matrix_v0.revealed_slots` | **A** → CE scenes |
| **Sphere framing** | `profileSphereCopy.ts` · `profileLifeSpheres.ts` | life_spheres / life_areas | **A** — stop rewriting meaning |
| **V0 taxonomy (parallel)** | `buildProfileV0TaxonomyLayers` · V0Screen · editorial · PatternsSection | `interpretation.life_areas.*` + zodiac/LP | **D/block** |
| **Today** | `TodayCompositionSurface` · `todayDayStoryModel` | `decision_style`, `helps[0]` | **CE reader**; drop `life_areas` keys as meaning (`todayPageUtils`) |
| **Tarot** | `tarot/result` · `buildTarotReadingStoryModel` | often `interpretation.identity` | **A** → `identity_core` |
| **Personal Lens / Discover** | `personal-lens.ts` · `PersonalityPatterns.tsx` | axes engine | **D/block** vs CE |
| **Cache** | `coreProfileCache.ts` | whole CoreProfile blob | **A** — version for CE Snapshot |

### iOS Δ (high risk)

| Path | Behavior | Fate |
|------|----------|------|
| `ios/.../Views/ProfileView.swift` · `ProfileQuickMapView.swift` | Prefer `interpretation.lifeAreas` (love/career/money essays) | **A/rewrite** — opposite of web V2 |
| `Models/InteractiveSurfaces.swift` | Decodes `ProfileContractV1` | DTO ready; UI not wired |

Android: DTO-shaped fields; no Profile essay consumers found in scan.

---

## 5. Parallel personality builders (kill list priority)

1. Disclosure funnel (+ spheres synthesis) — **P0**  
2. Oneshot `_PROFILE_SYS_RU` — **P0**  
3. FE V0 taxonomy / `profileSphereCopy` rewrite — **P0** (reader-side invent)  
4. iOS Profile from `interpretation.life_areas` — **P0** platform parity  
5. Natal interpreter templates + editorial — **P1**  
6. Thematic reports career/love — **P1**  
7. Numerology explainer as identity — **P1**  
8. Personal Lens / Discover PersonalityPatterns — **P1**  
9. Compat editorial inventing person (not pair) — **P2**  
10. Day/guide minting stable person when Snapshot thin — **P2**  
11. Dead: `career_analysis`, `profile_interpreter`, `profile.spheres.v1` — **cleanup**

---

## 6. Architecture Impact — D1–D4 (**ACCEPTED**)

SoT решений: [CHARACTER_ENGINE_ARCHITECTURE_IMPACT_V1.md](./CHARACTER_ENGINE_ARCHITECTURE_IMPACT_V1.md).

| # | Decision | Verdict |
|---|----------|---------|
| **D1** | Snapshot home | `core_profile_snapshots.payload.character_engine_v1` · no new table · one write authority `_publish_portrait` |
| **D2** | Evidence Graph | `raw_fact → typed edge → claim → cascade section` · Swiss/deterministic = calc authority · LLM natal_facts = bridge only |
| **D3** | Pipeline | Managed stages 0–6 · atomic publish · not monolith · not disclosure funnel · prompt family `profile.character_engine.v1` |
| **D4** | Legacy fields | Deterministic adapters only · Shadow = diagnostics · no dual portrait publish · kill roots at cutover by milestone |

### Migration hard rule

> Не запускать новый Character Engine **параллельно** со старыми personality roots дольше переходного окна (milestones, не календарь).  
> Shadow comparison ≠ dual SoT publish.

---

## 7. Next actions (execution)

1. ~~Inventory · Architecture Impact D1–D4 · Schema draft v0.1~~ → [CHARACTER_ENGINE_SCHEMA_CONTRACTS_V0](./CHARACTER_ENGINE_SCHEMA_CONTRACTS_V0.md).  
2. Machine-readable JSON Schema + ID stability tests.  
3. Recipe + stage prompts · pipeline behind flag · Shadow.  
4. Cutover readers · kill roots · cleanup.  

**UI Profile:** только изменения, не закрепляющие старые смысловые зависимости.

---

## 8. Changelog

| Date | Change |
|------|--------|
| 2026-07-25 | v0 — full runtime inventory (BE roots · registry · FE/iOS clusters · kill list · D1–D4 open) |
| 2026-07-25 | v0.1 — D1–D4 closed → [CHARACTER_ENGINE_ARCHITECTURE_IMPACT_V1](./CHARACTER_ENGINE_ARCHITECTURE_IMPACT_V1.md) |
| 2026-07-25 | v0.2 — schema draft pointer [CHARACTER_ENGINE_SCHEMA_CONTRACTS_V0](./CHARACTER_ENGINE_SCHEMA_CONTRACTS_V0.md) |
