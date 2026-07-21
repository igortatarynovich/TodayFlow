# TodayFlow Product Execution Tracker

Last updated: 2026-07-21
Owner: Product + Engineering
Status: Active working document

## 1) Purpose

This file is the single source of truth for:
- product problems, needs, and goals,
- target architecture,
- implementation roadmap,
- progress tracking (done / in progress / next),
- change log.

Rule: every meaningful implementation change must be reflected here.

Important:
- Product canon: [CORE_PRODUCT_CANON.md](./CORE_PRODUCT_CANON.md).
- **PIM center:** [PERSONAL_INTELLIGENCE_MODEL_V1.md](./PERSONAL_INTELLIGENCE_MODEL_V1.md) · [USER_KNOWLEDGE_MODEL.md](./USER_KNOWLEDGE_MODEL.md) · [INTENT_MODEL_V1.md](./INTENT_MODEL_V1.md).
- **Today experience (ACCEPTED):** [TODAY_SCREEN_V1_CANON.md](./TODAY_SCREEN_V1_CANON.md) · [TODAY_LANGUAGE_V1.md](./TODAY_LANGUAGE_V1.md).
- **Profile UI:** [PR4_PROFILE_CANON.md](./PR4_PROFILE_CANON.md) (production IA; applies umbrella) · [PROFILE_SCREEN_MASTER.md](./PROFILE_SCREEN_MASTER.md) (v0 visual) · [TODAYFLOW_FOUNDATION_UI.md](./TODAYFLOW_FOUNDATION_UI.md).
- **Explainable Computation (platform gate):** [EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md](./EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md) — выше модулей; конфликт → umbrella.
- **Understanding progress (depth · missing · trial · sub):** [UNDERSTANDING_PROGRESS_AND_DEPTH_CANON.md](./UNDERSTANDING_PROGRESS_AND_DEPTH_CANON.md).
- **Core loop:** [CORE_USER_LOOP.md](./CORE_USER_LOOP.md) · [DAILY_NAVIGATION_MODEL.md](./DAILY_NAVIGATION_MODEL.md).
- **Product model (whole product):** [TODAYFLOW_PRODUCT_MODEL.md](./TODAYFLOW_PRODUCT_MODEL.md) — Personal Model, projections (doc №1).  
**Today + First Day:** [TODAY_PRODUCT_MODEL.md](./TODAY_PRODUCT_MODEL.md), [FIRST_DAY_EXPERIENCE.md](./FIRST_DAY_EXPERIENCE.md).
- **Reference Layer (P0 freeze):** [REFERENCE_LAYER_AND_BUILD_ORDER.md](./REFERENCE_LAYER_AND_BUILD_ORDER.md).
- **Platform parity:** [status/IOS_TODAYFLOW_STATUS.md](./status/IOS_TODAYFLOW_STATUS.md).

---

## 2) Extracted From User Discovery (Fixed Context)

### Problems
- Product has strong features, but no strict system architecture.
- The `Today` page is not yet a clear daily magnet in all scenarios.
- UX/visual language is inconsistent across modules.
- Risk of contradictory interpretations between sections.
- Reward mechanics are not yet implemented as a domain system.
- The product still exposes too many parallel surfaces instead of one clear user story. **Mitigation (2026-07-05):** `day_story_v1` — one LLM artifact for Today contract + derived narrative surfaces; profile/tarot single-answer contracts — next.
- The product still thinks in internal modules more than in user jobs to be done.
- The profile page is not yet the user's clear personal map.
- Text generation quality: default **`TODAY_NARRATIVE_QUALITY_MODE=trust_llm`** (2026-07-05) — post-hoc copy gates off; strict mode via env for legacy QA.
- **Acquisition UX (2026-07-05):** no «попадает?» / «это про вас?» / «откликнулось?» validation under content blocks. Product gives orientations; learning via **behavior** (mood, actions, questions text, ritual choices, navigation) per KASP channels B–I. Ritual post-reveal: optional **proximity** chips («Что сейчас ближе?») only — not accuracy checks. No per-block compatibility echo, profile atom confirm spam, or guidance resonance forms.
- **Behavioral questions map (2026-07-05, accepted):** implicit questions → signals (not validation UI). **P1:** `day_promise` + `honest_step` (ritual). **P1:** `guidance_ask` text → CUM `active_themes` semantic top-K. Pattern promotion threshold: **KASP default ≥3/14d** until product review; `behavioral_patterns.works` uses softer ≥2/14d. Full map: mood/head_topic/proximity/spheres/guidance/evening/compat navigation — see chat 2026-07-05 + DE-5 tags.

### Needs
- Core center: `Natal Chart + Numerology Core Profile`.
- Brand and system definition:
  - `TodayFlow` is the brand,
  - `Profile` is the personal map,
  - `Today` is the daily guide.
- Mobile-first product thinking:
  - primary use case is phone,
  - core screens must open fast and read in stacked sections,
  - long information should be hidden behind reveals/expanders instead of shown at once.
- Product IA with implicit JTBD routing plus core interpretation surfaces:
  - `Today`
  - `Profile`
  - `Compatibility`
  - `Tarot`
  - `Growth`
- Unified interpretation pipeline (no contradictions).
- Multi-profile support:
  - self
  - spouse / partner
  - child
- Compatibility in two modes:
  - static sign-to-sign base content (free/paid depth),
  - personalized compatibility using birth data.
- Retention system (streaks, archetypes, seals, evolution index) tied to core profile.
- API-generated high-quality texts for profile/today/tarot/compatibility.

### Goals
- Increase retention to 2-3 sessions/day.
- Make the daily flow clear on one `Today` surface, with light time-of-day emphasis and reminders instead of three separate product modes.
- Keep content coherent across all modules.
- Be monetization-ready with clear gated value.
- Remove excess complexity from screens and make profile + today immediately understandable.
- Move the product from module-first to JTBD-first.
- Reach full coverage of the 4 core JTBD: self, other, decision, today.
- Use `Today` as both a daily decision engine and a learning surface that gathers better personalization signals over time.
- Build weekly and monthly state maps as accumulated user-understanding layers, not as separate product roots.

---

## 3) Architecture Gap Analysis

### Already in place
- Broad feature coverage in backend and frontend (astro, tarot, cycles, habits, practices).
- `Today` already improved and partially merged with morning ritual behavior.
- Menstrual/cycle-related functionality exists in architecture.
- Compatibility backend routes exist.

### Missing / weak points
- **Reference Layer not unified:** astrology/tarot/numerology JSON exists but lacks unified data model, Machine/Content Contract, versioning, and Reference API — blocks clean Daily Engine and new generation work ([REFERENCE_LAYER_AND_BUILD_ORDER.md](./REFERENCE_LAYER_AND_BUILD_ORDER.md)).
- IA/navigation still reflects the older service-first model in places and is not yet fully normalized to the JTBD-first model.
- Main surfaces do not yet infer and answer user intent strongly enough by their structure and CTAs (исключение: **Today narrative** — явный слой **`intent`** в промптах после DE-6).
- No explicit universal `Core Profile Engine` contract used by all modules.
- No formal contradiction-resolution layer for interpretations.
- No durable learning layer for prompt/version/result/feedback analysis across modules.
- **DayContext → narrative** for Today is wired end-to-end including **intent** (DE-6, §4.7); **UI/explainability** по всем слоям канона и «почему вместе» с ритуалом — ещё не полностью выровнены с одним публичным пакетом DayContext.
- Compatibility productization (static library + personalization + gate logic) is incomplete.
- Decision support is present only indirectly through forecasts/tarot, not as a first-class product lane.
- Money/career and state/stabilization JTBD are partially covered in services but weakly packaged in UI.
- Reward domain model is not fully implemented end-to-end.
- Design system is not fully unified (tokens/components/layout consistency).
- Profile page is still not the canonical “my life map” surface.
- Today still contains too much secondary material in the default view.
- Legacy `quality_gate` logic is too influential in shaping generated text.

---

## 4) Target Product Architecture (Canonical)

## Layer 0: Reference Layer (foundation — build first)

Canon: [REFERENCE_LAYER_AND_BUILD_ORDER.md](./REFERENCE_LAYER_AND_BUILD_ORDER.md).

- Unified taxonomy (10 domains) + catalog table §6
- Machine Contract (engine) + Content Contract (LLM/UI)
- Status/version lifecycle (`draft` → `active` only in prod)
- Read API: `GET /reference/v1/{domain}/{code}` (target)

**Blocks until P0 active:** new Today UI, new prompts, split generation pipeline (DE-13), Calendar rhythm filters.

## Layer A: Core Intelligence
- `Core Profile Engine`
  - natal chart summary
  - numerology summary
  - stable archetype baselines
  - profile version/hash
- `Interpretation Orchestrator`
  - combines core profile + transits + cycles + context
  - conflict resolution rules
  - deterministic output envelope for frontend

## Layer B: Domain Modules
- `Today Engine`
- `Forecast Engine`
- `Tarot & Guidance Engine`
- `Compatibility Engine` (static + personalized)
- `Growth Engine` (habits, diary, practices, askesis)
- `Rewards Engine`

## Layer B.1: Canonical User Surfaces
- `Profile`
  - stable personal map
  - natal chart
  - numerology identity
  - signs / houses / strong and weak sides
  - additional profiles
- `Today`
  - only current-day interpretation
  - tarot day card
  - actionable “do / avoid / notice”

## Layer C: Experience/UI
- Unified navigation with implicit JTBD routing and clear core surfaces
- Shared component library + design tokens
- Consistent cards/actions/feedback patterns

## Layer D: Learning Loop
- `Prompt Registry`
  - module
  - version
  - prompt kind
- `Generation Logs`
  - input payload
  - profile snapshot
  - model
  - output
  - fallback/error state
- `Feedback Signals`
  - explicit user feedback
  - future implicit quality signals

Purpose:
- compare prompt versions,
- identify dead or weak outputs,
- prepare curated dataset for future tuning,
- improve prompts without online self-training in production.

---

## 4.6) Daily ritual UX canon (web + iOS parity)

This section locks **packaging** decisions for the daily engine: what the product promises on screen, how dense Today may be, and what must stay aligned across web and native clients.

**Today experience canon (web + iOS + Android):** [TODAY_SCREEN_V1_CANON.md](./TODAY_SCREEN_V1_CANON.md) · [TODAY_LANGUAGE_V1.md](./TODAY_LANGUAGE_V1.md).

### Fixed product decisions

- **Unified engine inputs (north star)**  
  The day layer is assembled from the same family of signals the backend already knows: profile + natal + numerology + tarot-of-day + astro/transit context + **behavioral state** (check-ins, diary, habits, ascetics, answered questions). Delivery can be incremental; **contracts stay stable** so iOS/Android can consume the same envelopes as web.

- **Layered IA (frequency of use)**  
  `Today` = operational 24h surface (what changes today). Stable natal depth and “library” reading live under **Profile / knowledge surfaces**. Compatibility and active tarot/question flows remain **separate hubs**, not collapsed into one Today scroll.

- **Information diet**  
  Show **outcomes and one clear “why” affordance** on Today; rotate which natal/astro facet grounds the copy across days instead of exposing full chart vocabulary by default.

- **Progressive disclosure**  
  Headlines read as guidance (“сегодня уместно…”), not as raw chart rows. Technical astro backing opens in sheet / secondary reveal for users who want proof.

- **Visual direction: tactile esotericism**  
  Sand–pale rose-gold spectrum, **raised cards**, generous whitespace between blocks; separation via depth/shadow rather than heavy divider lines. Fight low-contrast “soap” by anchoring text in graphite/brown ink on matte surfaces.

- **Invisible technology**  
  Do **not** surface LLM/“ИИ” as the source of copy in user-facing UI. The product voice stays interpretive and personal; model plumbing is internal.

- **Today ritual flow parity (web ⇄ iOS)**  
  The block **«Собрать день» / «С чего начнём»** (body + calendar hint + quick chips), **life spheres (сферы)** always visible after the daily ritual spine, with a **pre–check-in hint** when mood is unset — **required on both web and iOS** (`TodayRitualFlow` / `TodayRitualFlowView` + shared copy sources).

- **Ritual spine contract (code parity web ⇄ iOS ⇄ Android scaffold)**  
  One reducer model for the main path (open day → tarot continue → number → mood → check-in): `frontend/src/lib/todayRitualSpineMachine.ts`, `ios/.../TodayRitualStateMachine.swift`, `android/.../TodayRitualSpineMachine.kt`. Illegal transitions return `null` / no-op. Meaning analytics for **number** and **mood** steps are emitted only from **`analyticsHint`** after a valid reducer transition (`executeRitualSpineAnalytics` on web/Android, `applySpineEffects` on iOS). Tests: Jest (`todayRitualSpineMachine.test.ts`), XCTest (`TodayFlowSmokeTests`), Android `ExecuteRitualSpineAnalyticsTest`.

- **iOS Today deck**  
  Card of day → numerology layer → tone/summary presented as a **horizontal page deck** (swipe / pager), reducing vertical wall-of-cards overload while keeping the same narrative order as web.

### Near-term development plan

| Priority | Item | Notes |
|----------|------|--------|
| P1 | **iOS chip deep links** | Done: chips switch to Flow + `pendingTrackerQuickCreate` → привычка (scroll + focus), цель (sheet), аскеза (sheet + `POST /tracking/ascetic-contracts`). |
| P1 | **Narrative fusion contract** | Done: `GET /tracking/fusion/{date}` и `/today/state-map` отдают **`rhythm_context`**; в `POST /today/narrative` полный `fusion` — для **guide** и **day_layer**; компактный `_fusion_slim_for_prompt` (scores + encouragement + recommendations + rhythm_context) — для **spheres**, **evening**, **deepen**. Версия промпта модуля narrative — **`today-narrative-v9`** (DE-5: `behavior_patterns`; DE-6: `intent`; DE-12: `visible_profile` / `internal_profile` в DayContext и user JSON; жёстче анти-абстракция + RU quality gate на guide/spheres). |
| P2 | **Today widget layout (bento)** | Optional user-tunable card grid on Today once baseline ritual + spheres + build-day parity is stable on both platforms. |
| P2 | **Retention loop polish** | Push → open deck → micro-task → check-in → evening close; keep triggers aligned with `DayConnection` and documented in push matrix. |

---

## 4.7) Day Engine & DayContext (coherence + learning)

**Canon:** [DAY_ENGINE_AND_COHERENCE.md](./DAY_ENGINE_AND_COHERENCE.md)

**Goal:** one logical **DayContext** drives narrative generation and explainable UI; chain **cause → interpretation → recommendation**; close the loop **recommended → did → outcome** (evening, tracking).

**Already related in codebase:** `fusion` / `rhythm_context`, `ritual_context` on `POST /today/narrative`, `core_profile`, learning layer, §4.6 ritual UX, [TODAY_PERSONALIZATION_CORE.md](./TODAY_PERSONALIZATION_CORE.md) (events + future JSON contract).

### Execution checklist

| ID | Task | Status | Notes |
|----|------|--------|--------|
| DE-1 | DayContext **v0 spec** (doc fields + optional JSON Schema draft under `docs/schemas/`) | DONE | [DAY_CONTEXT_V0.md](./DAY_CONTEXT_V0.md), `day_context_v0.schema.json`, CI `day-context-schema`, `build_day_context_v0` |
| DE-2 | Backend **DayContext assembler**; single injection point before LLM in `today_narrative` (and same pack for downstream surfaces) | DONE | `build_today_narrative` вызывает `build_day_context_v0` до LLM; guide user JSON из `layers`; `generation_logs.input_payload`: `day_context_sha256`, `day_context_contract_version` |
| DE-3 | Surface **`generation_id`** (+ context version) wherever users give step/outcome feedback | DONE | Web: state для guide/day_layer/spheres/evening; `generation_id` в meaning payload; `POST /learning/feedback` при day_connection (ритуал/вопрос/решение) и вечере; iOS: `generationLogId` в `trackTodaySurfaceEvent` + feedback после `saveEveningReflection` |
| DE-4 | **Feedback loop** on ritual steps: picked / 20m focus / evening ↔ tracking events + learning | DONE | `VALID_EVENT_TYPES` + `RING_EVENT_WEIGHTS` для канонических типов; веб/iOS шлют `sphere_opened`, `tarot_selected`, `mood_selected`, `focus_started`, `evening_reflection_submitted` и др.; `tests/test_meaning_events.py` |
| DE-5 | **Pattern aggregates** from events into learning / profile-facing summaries | DONE | `build_meaning_surface_patterns_v0` → `DayContext.layers.behavior_patterns`, `learning_context.meaning_surface_patterns`, промпты narrative; `stats.meaning_events_28d`; pytest `test_meaning_surface_patterns.py` |
| DE-6 | **Intent**: wire `morning_intention`, head topic, and “what matters” into priority in prompts and UI | DONE | `intent_slice_v0` (`build_intent_layer_v0`) → `DayContext.layers.intent`; `DayConnection` + `head_topic` из `ritual_context` в `build_today_narrative`; промпт `today-narrative-v9` + `intent` в user JSON (guide…deepen); кэш: `intent_context_fp`; API: `RitualContextRequest.head_topic`, `ritual_context` на всех surface; web: `lastRitualNarrativeContextRef` + `head_topic` в ритуале; iOS: `TodayNarrativeRitualContextPayload.head_topic`, last-context для child surfaces; схема `ritual_layer.head_topic`; pytest `test_intent_slice_v0`, `test_day_context_v0` |
| DE-7 | **Flow completion** signals into fusion / DayContext | DONE | v0–v2: флаги `DayConnection` + `guide_action_options_selected_today` + **`guide_meaning_completions_today`** в `GET /tracking/fusion` → DayContext; slim fusion с клампом 0–50; различие с `day_completed` в [DAY_CONTEXT_V0.md](./DAY_CONTEXT_V0.md). **v3 (UI):** под «Главный шаг» на вебе и iOS — eyebrow «Сегодня в Flow», чипы по ненулевым типам и текст пустого состояния, если объект счётчиков есть, но суммы нулевые (`TodayResultView`, `GuideMeaningCompletionsFocusStrip`). Backlog: жёсткая связка текста вариантов шага с событиями. |
| DE-8 | **`depth_level`** quick / normal / deep — contract, settings, prompt branches | DONE | **v0–v2:** как ранее (narrative contract, `user_settings`, тарифный кламп `deep`). **v3 (2026-05-04):** выбор на Today (веб/iOS) + частичный PUT. **v4 (2026-05-04):** meaning-событие `today_narrative_depth_changed` → `/meaning/events` (web `trackMeaningEvent`, iOS `trackTodaySurfaceEvent`), `VALID_EVENT_TYPES` + вес Mind в `RING_EVENT_WEIGHTS`; см. [TODAY_PERSONALIZATION_CORE.md](./TODAY_PERSONALIZATION_CORE.md). |
| DE-9 | **Temporal context** (yesterday, 7-day trend) inside DayContext | **DONE** | **v0–v1.4:** как ранее (fusion scores, UI strip, week summary, meaning signals, `day_model.temporal`). **v1.5 (2026-07-03):** `reflection_excerpt` из `DayConnection` (вечер/дневник/утро, caps); UI-строка `formatFusionDayHistoryReflectionLine*` (web+iOS); промпт-гайды. Эпик закрыт — temporal slice в DayContext, fusion API, UI и LLM. |
| DE-10 | **Health** (sleep, activity) with consent — HealthKit first, Android later | BACKLOG | Privacy review |
| DE-11 | **Journal excerpts** in DayContext under explicit policy (extends diary slice beyond counts) | BACKLOG | With user consent + caps |
| DE-12 | **Visible vs internal profile slices** for prompts (no new tables v0) | DONE | `profile_prompt_slices_v0` → `DayContext.layers.visible_profile` / `internal_profile`; схема `day_context_v0`; `_attach_profile_slices` во все user JSON narrative; системные параграфы RU/EN + `PROMPT_VER` v9; pytest `test_profile_prompt_slices_v0` |
| DE-13 | **Narrative multi-call pipeline** (узкие шаги вместо одного guide на всё) | **DONE** | **v0–v4:** funnel interpretation → core → satellites; per-step cache; child chain; step3 core. **v5 (2026-07-03):** `guide_contract_v2` + `guide_pipeline_v0` в HTTP guide; `guide_funnel_core_source`; preserve LLM core vs `guide_decision`; web/iOS/Android parsers. **v6 (2026-07-20):** quality-first `LLM_QUALITY_MODE=rich` + Nebius/DeepSeek-V4-Pro; child surfaces 2-step funnels; **profile 4-step** portrait funnel (`profile-contract-v3`) + strict/quality gates + forming fallback + lock/cache DoD tests. Canon: [LLM_QUALITY_AND_PROMPT_EVOLUTION.md](./LLM_QUALITY_AND_PROMPT_EVOLUTION.md). **Open:** manual QA 20–30 live profiles. Монолит только fallback. |
| **GE-1** | **Generation Orchestrator** — единый управляющий слой генераций; мета-воронка в логах; связка с [PERSONAL_INTELLIGENCE_LAYER.md](./PERSONAL_INTELLIGENCE_LAYER.md) §10.1 / §11 | IN_PROGRESS | **v0.1:** `orchestration` в `generation_logs`. **v0.2 (2026-05-04):** `orchestration.reasoning_trace` (полный `selector_debug` + `selector_resolution` + урезанные `generation_rules`); `POST /today/narrative` → **`run_today_narrative_pipeline`** (`api/today.py`). **v0.3 (2026-07-03):** `ORCHESTRATOR_VERSION` 0.4.0; `reasoning_trace.day_model` (vector/tension/risk/gate); `narrative_outcome` после генерации (funnel/monolith, child chain); guide `merge_pass_steps` ↔ DE-13 funnel + `guide_contract_v2`. **Дальше:** Guidance/Compatibility через тот же фасад; payload между шагами funnel в orchestration; смысловой quality gate. |
| **PS-1** | **Profile Selector v1** — topic life-area excerpts · day_history signals · eval harness | **DONE** | `profile-selector-v1` · `topic_sphere_excerpt` · `selector_eval.py` · DayContext wiring |
| **PM-1** | **Profile vs Personal Map** — убрать дублирование IA и копирайта: натал как **source layer** без Today и без повторяющегося портрета; Profile = портрет + сферы; CTA по смыслу блока; сферы ≠ копия домов | **DONE** | Quick Map dedup · sphere frames (`profileSphereCopy`) · `/profile?view=v0` · life sphere/house audit · iOS builder parity · Portal-only «Карта личности» |
| **DS-2** | **Foundation HeroLarge** — единый hero §1.1 (`88dvh`, symbol 120px, geometry, fade); web `HeroLarge.tsx` + iOS `HeroLargeView` | **DONE** | Quick Map · Editorial · FirstDayTeaser (web+iOS); test `HeroLarge.test.tsx`. |
| **DS-3** | **Profile orbit-card purge** — production `/profile` на Foundation surfaces | **DONE** | `SurfaceInsight` + `ProfileSurface` · route chrome · setup · legacy sections (Synthesis, Pulse, Overview, Circle, …) — **0× `orbit-card` в `components/profile/`** |
| **DS-4** | **Profile motion kit** — CSS-only reveal/stagger/expand; `prefers-reduced-motion` | **DONE** | `--tf-motion-*` tokens · `ProfileMotion.tsx` · HeroLarge · expandable/portal · Quick Map stagger · iOS `ProfileMotion.swift` |
| **DS-1 lite** | **Archetype SVG assets** — `public/images/icons/archetypes/` + `VISUAL_ASSET_MODE=asset` | **DONE** | 12 named + unknown · mask tint · iOS `ArchetypeSymbolView.swift` · `ARCHETYPE_SLUGS` |
| **PM-QA** | **Profile Foundation QA** — Quick Map vs Foundation §9 + shape audit hook | **DONE** | [PROFILE_FOUNDATION_QA.md](./status/PROFILE_FOUNDATION_QA.md) · `NEXT_PUBLIC_PROFILE_SHAPE_AUDIT` · tests pass |
| **DS-FIGMA** | **Foundation Figma file** — `TODAYFLOW_FOUNDATION_UI` (Cover + §8 pages) | **IN DESIGN** | [Cover v1](https://www.figma.com/design/pWdevqQqOi6wvoVc6hFWHa) · living portal composition · **не sign-off** |
| **DS-12** | **Archetype expansion** — 8→12 seeds (seeker · mentor · guardian · visionary · catalyst) | **DONE** | registry aliases (evolution levels) · inline + SVG · iOS paths |
| **DS-5** | **Foundation HeroMedium** — §1.2 Today theme hero (52dvh, 80px symbol) | **DONE** | `HeroMedium.tsx` · Today day-anchor · `todayHeroMedium` · iOS `HeroMediumView.swift` |
| **DS-6** | **Foundation HeroSmall** — §1.3 Compatibility section header (200px, 48px symbol) | **DONE** | `HeroSmall.tsx` · hub · exploration · dynamics · `CompatibilityOrbitSymbol` · iOS `HeroSmallView.swift` |
| **DS-7** | **Planet SVG assets** — 10× `public/images/icons/planets/` + `PlanetIcon` | **DONE** | mask tint · Profile chart table · `InlinePlanetIcons` · iOS `PlanetSymbolView.swift` |
| **DS-8** | **Geometry System** — G1–G5 primitives + Profile / Today / Portal compositions | **DONE** | `FoundationGeometryLayers` · `SacredGeometryBackdrop` preset/tone · portal deep section · iOS `FoundationGeometryView.swift` |
| **DS-9** | **Zodiac SVG assets** — 12× `public/images/icons/zodiac/` + mask tint `ZodiacIcon` | **DONE** | Today pillars · Compatibility orbit · Profile V0 · iOS `ZodiacSymbolView.swift` |
| **DS-10** | **Typography bridge** — `--orbit-text-*` → `--tf-type-*` aliases · `profileV0` tokens | **DONE** | `globals.css` legacy aliases · `profileV0.module.css` on Foundation §5/§6 |
| **DS-11** | **Element SVG assets** — 4× `public/images/icons/elements/` + `ElementIcon` | **DONE** | mask tint · `ElementAtmosphere` pattern tile · iOS `ElementSymbolView.swift` |
| **MP-1** | **Maps canon + Profile IA** — вторая половина продукта: split «Кто я» / «Как меняется жизнь»; §4.10 Product Model · §7 Profile Master · §3.3 PIL | **DONE** | Living Maps band · heatmap/habit weave preview · explore card grid + hub · local cross-map observation (web+iOS) |
| **MP-2** | **Map language migration** — tracker/statistics → карта/история (§5.8); routes/copy web + iOS | DONE | Hub «Мои карты» · heatmap без % · weekly integration story · habits/ascetic/calendar/help/rings · iOS chrome parity · **исключения:** legacy URL `/affirmations/tracker`, `/asceticisms/tracker`; internal `day_trackers` / `planet_tracker` catalog |
| **MP-3** | **Map entities P0** — Mood · Energy · Habit · Promise: heatmap + day drill-down + story copy | DONE | **Web v0** · **iOS v0:** local stores · 4 map screens · Profile preview · mood sync · fusion persist · evening continuity writer · `/maps/*` deep links · Maps hub · batch fusion history |
| **MP-4** | **Map entities P1** — Ascetic journey · Wish · Relationship network · Tarot arc | **DONE** | web `/maps/{ascetic,wish,relationship,tarot}` + share line v0; iOS P1 views + deep links; relationship writer on compat result |
| **MP-5** | **Cycle as context** — Today recommendations only; cycle patterns in Maps observations, never hero | DONE | `cycleMapModel` + Profile Living Maps (web/iOS) · без «день N» · cross-map after 4+ cycles |

**Порядок работ (зафиксировано, см. PIL):** 1) Profile Engine → 2) Profile Selector (расширение + eval) **PS-1 DONE** → 3) Today DayModel + цепочка → 4) Today UI только как проекция → 5) Guidance → 6) Compatibility → 7) Flow. **Maps (MP-*)** — параллельно после MP-1, не блокируя Today spine. Параллельно GE-1 разворачивает **операционный контур** (§10 PIL).

---

## 5) Implementation Roadmap

## Phase 0: Reference Layer (P0 catalog)

**Фаза канона:** [ONTOLOGY_AND_FOUNDATION_PHASES.md](./ONTOLOGY_AND_FOUNDATION_PHASES.md) **Фаза 1** (Canonical Knowledge) + начало **Фазы 2** (DayModel rules). Не путать с PIL output surfaces (фазы 3–5).

Status: `IN_PROGRESS`

Canon: [REFERENCE_LAYER_AND_BUILD_ORDER.md](./REFERENCE_LAYER_AND_BUILD_ORDER.md).

### Tasks
- [x] Fix Reference Layer canon doc + domain catalog table §6.
- [x] DayModel Input Contract + Dependency Map ([DAYMODEL_INPUT_CONTRACT.md](./DAYMODEL_INPUT_CONTRACT.md)).
- [x] Reference Machine Contract JSON Schema v1 + CI ([REFERENCE_MACHINE_CONTRACT_V1.md](./schemas/REFERENCE_MACHINE_CONTRACT_V1.md)).
- [x] P0.3 — editorial draft scores (22 major arcana), each file passes validator (`DATA/reference/tarot/machine/`).
- [x] P0.4 — DayModel v1 aggregation test (loader + tarot-only preview aggregator + pytest).
- [x] Reference system taxonomy + C/D/Co/R classification ([REFERENCE_LAYER_AND_BUILD_ORDER.md](./REFERENCE_LAYER_AND_BUILD_ORDER.md)).
- [x] Data ownership & consumption map ([DATA_OWNERSHIP_AND_CONSUMPTION_MAP.md](./DATA_OWNERSHIP_AND_CONSUMPTION_MAP.md)).
- [x] Ontology & foundation phases canon ([ONTOLOGY_AND_FOUNDATION_PHASES.md](./ONTOLOGY_AND_FOUNDATION_PHASES.md)).
- [x] Data origination & lifecycle canon ([DATA_ORIGINATION_AND_LIFECYCLE.md](./DATA_ORIGINATION_AND_LIFECYCLE.md)).
- [x] Personal Intelligence Layer canon v2 — сквозной learning-aware слой ([PERSONAL_INTELLIGENCE_LAYER.md](./PERSONAL_INTELLIGENCE_LAYER.md)).
- [x] User Evolution Model ([USER_MODEL_TARGET_STATE.md](./USER_MODEL_TARGET_STATE.md)).
- [x] Gamification & Progress System ([USER_MODEL_TARGET_STATE.md](./USER_MODEL_TARGET_STATE.md)).
- [x] Symbolic Asset & Commerce Layer ([REFERENCE_LAYER_AND_BUILD_ORDER.md](./REFERENCE_LAYER_AND_BUILD_ORDER.md)).
- [x] User Model Target State / north star ([USER_MODEL_TARGET_STATE.md](./USER_MODEL_TARGET_STATE.md)).
- [x] Interpretation Layer & Reference canon ([INTERPRETATION_LAYER_AND_REFERENCE.md](./INTERPRETATION_LAYER_AND_REFERENCE.md)).
- [x] Knowledge Acquisition & Signal Policy ([KNOWLEDGE_ACQUISITION_AND_SIGNAL_POLICY.md](./KNOWLEDGE_ACQUISITION_AND_SIGNAL_POLICY.md)).
- [x] User Knowledge Model canon ([USER_KNOWLEDGE_MODEL.md](./USER_KNOWLEDGE_MODEL.md)).
- [x] API Memory & Learning Layer canon ([API_MEMORY_AND_LEARNING_LAYER.md](./API_MEMORY_AND_LEARNING_LAYER.md)).
- [x] P0.5 — Numerology machine drafts (`DATA/reference/numerology/machine/`, loader, validator, numerology-only preview).
- [x] P0.7 — Astrology Machine Contract canon ([ASTROLOGY_MACHINE_CONTRACT.md](./ASTROLOGY_MACHINE_CONTRACT.md)).
- [x] Astrology Composition Model gate ([ASTROLOGY_COMPOSITION_MODEL.md](./ASTROLOGY_COMPOSITION_MODEL.md)).
- [x] P0.8 — Astrology atomic machine drafts (39: 12 signs, 10 planets, 12 houses, 5 aspects; loader + validator).
- [x] P0.9 — Cross-domain machine validation — PASS → P1.0 unlocked.
- [x] **P1.0** — DayModel v1 multi-source aggregation (`aggregate_day_model_v1`, 15 tests).
- [x] **P1.1** — DayModel Interpretation Rules (`interpret_day_model_v1`, 12 tests).
- [x] **P1.2** — DayModel Content Mapping (`map_day_model_interpretation_to_content_keys`, 13 tests).
- [x] **P1.3** — Content Contract Seed Texts (37 keys, validator, resolver, 13 tests).
- [x] **P1.4** — Deterministic Day Content Assembly (`assemble_day_content_package_v1`, 10 tests).
- [x] **P1.5** — DayModel Package Evaluation (`evaluate_day_content_package_v1`, 10 tests).
- [x] **P1.6** — Deterministic Renderer Contract (`render_day_content_package_v1`, 10 tests).
- [x] **P1.7** — LLM Call Gate for DayModel Content (`decide_day_content_llm_call_v1`, 10 tests).
- [x] **P1.8** — LLM Request Record Contract (pre/post-call builders, 10 tests).
- [x] **P1.9** — Prompt Context Slice Contract (`build_llm_context_slice_v1`, 10 tests).
- [x] **P1.10** — Prompt Template Contract (`build_day_llm_prompt_v1`, 10 tests).
- [x] **P1.11** — LLM Response Contract & Validator (`validate_day_llm_refinement_response_v1`, 12 tests).
- [x] **P1.12** — LLM Response Evaluation & Post-call Integration (`evaluate_day_llm_response_v1`, 10 tests).
- [x] **P1.13** — Final Surface Candidate Selection (`select_day_surface_candidate_v1`, 10 tests).
- [x] **P1.14** — Surface Candidate Audit Record (`build_day_surface_candidate_audit_v1`).
- [x] **P1.15** — User Exposure & Reaction Contract (`build_day_surface_exposure_v1`, `build_day_surface_reaction_v1`, 10 tests).
- [x] **P1.16** — Reaction → Learning Signal Mapping (`build_day_surface_learning_signal_v1`, 12 tests).
- [x] **P1.17** — Pattern Candidate Aggregation (`try_aggregate_pattern_candidate_v1`, 10 tests); [USER_KNOWLEDGE_MODEL.md](./USER_KNOWLEDGE_MODEL.md).
- [x] **P1.18** — Pattern Confirmation Gate (`try_confirm_pattern_from_candidate_v1`, 11 tests).
- [x] **P1.19** — Knowledge Candidate (`try_build_knowledge_candidate_from_pattern_v1`, 10 tests).
- [x] **P1.20** — Active Knowledge Confirmation Gate (`try_activate_knowledge_from_candidate_v1`, 12 tests).
- [x] **P1.21** — Active Knowledge Usage Policy (`try_build_active_knowledge_usage_policy_v1`, 12 tests).
- [x] **P1.22** — Active Knowledge Runtime Gate (`try_decide_active_knowledge_runtime_v1`, 11 tests).
- [x] **P1.23** — Active Knowledge Hint Package (`try_build_active_knowledge_hint_package_v1`, 11 tests).
- [x] **P1.24** — Hint Package Application Contract (`try_apply_hint_package_v1`, 11 tests).
- [x] **P1.25** — Hint Application Dataset Policy (`try_build_hint_application_dataset_policy_v1`, 10 tests).
- [x] **P1.26** — Dataset Candidate Promotion Gate (`try_promote_dataset_candidate_v1`, 10 tests).
- [x] **P1.27** — Training Dataset Registry (`try_register_training_example_v1`, 14 tests). **→ STOP:** [API_MEMORY_AND_LEARNING_LAYER.md](./API_MEMORY_AND_LEARNING_LAYER.md)
- [ ] ~~P1.28+ Learning pipeline (Export Gate, training batch, …)~~ — **DEFERRED** until users + own-model roadmap.
- [x] **Branch A** — Knowledge Usage Layer → **architecture closed** (A1.1–A1.8); ops: promotion→DB, log criteria — [status/branch_a_knowledge_usage_layer.md](./status/branch_a_knowledge_usage_layer.md).
- [x] **Branch B** — Evolution Engine → **B1.0–B1.14** ✅ — [status/branch_b_evolution_engine.md](./status/branch_b_evolution_engine.md).
- [x] **Branch C** — Practice System → **C1.0–C1.6** ✅ CD · **C2.0–C2.4** ✅ runtime stack — [status/branch_c_practice_system.md](./status/branch_c_practice_system.md).
- [x] **Branch D** — Symbolic Asset System → **D1.0–D1.5** ✅ — [status/branch_d_symbolic_assets.md](./status/branch_d_symbolic_assets.md). Symbolic foundation complete; Commerce Runtime deferred.
- [x] **Branch E** — Calendar Intelligence → **E1.0–E1.7** ✅ — [status/branch_e_calendar_intelligence.md](./status/branch_e_calendar_intelligence.md).
- [x] **Reference Intelligence Layer** — C1.7 ✅ · C1.8 ✅ · **Next:** FIRST_DAY_DOD_GAP_ANALYSIS.
- [ ] **Surface Layer** — **System map** ✅ · **Reference inventory** ✅ · **S1.1** ✅. **⏸ Today wire-plan paused** until RIL P0 edges (causal map §12).
- [ ] Compact User Model (CUM) implementation.
- [ ] Evolution Calculation Contract → UEM-2 (`evolution_stage` in API only after ECC active + P1.1).
- [ ] Tarot: full 78 cards + Machine Contract scales for DayModel.
- [ ] Numerology: content layer for core numbers + personal day/month/year.
- [ ] Emotional State + Today-critical UI Copy rows → `active`.
- [ ] Reference read API v1 + `reference_version` in generation logs.

**Freeze until Phase 0 P0 rows active:** Today UI redesign, new prompts, DE-13 pipeline split.

---

## Phase 1: Core Architecture Foundation
Status: `IN_PROGRESS`

### Tasks
- [x] Define `Core Profile` schema (backend + frontend DTO).
- [x] Build shared endpoint/service for core profile context.
- [x] Add orchestrator rules for interpretation consistency.
- [x] Refactor key personalized endpoints to consume core context.
- [x] Add integration tests for consistency between modules.
- [x] Split stable profile interpretation from daily interpretation at service contract level.
- [x] Add multi-profile contract to core profile domain.

### Done in this phase
- [x] Product-level architecture and scope documented in this tracker.
- [x] Implemented backend `CoreProfileService` with stable response envelope and `profile_hash`.
- [x] Added `GET /account/core-profile` endpoint for authenticated users.
- [x] Added frontend `CoreProfile` DTO and connected `/today` to consume it.
- [x] Implemented baseline `Interpretation Orchestrator` and wired it into `day-flow`.
- [x] Refactored `today`, `morning-ritual`, and `numerology/daily/explain` to expose `core_profile` + `consistency`.
- [x] Added integration tests for core profile consistency flow (auth + seeded context).
- [x] Added learning layer foundation: prompt versions, generation logs, feedback API, and generator-side best-effort logging.
- [x] Split `core_profile` contract into stable `interpretation` and separate `daily_interpretation`, with snapshot migration for older cached payloads.
- [x] Added explicit multi-profile contract to `core_profile`: `astro.relation`, `profiles.primary/selected/items`, and relation-aware account profile payloads.

---

## Phase 2: IA + Today As Daily Magnet
Status: `IN_PROGRESS`

### Tasks
- [x] Stabilize legacy top-level IA before JTBD pivot.
- [ ] Make `Today` the operational daily center as one surface with light time-of-day framing and reminders.
- [x] Ensure fast loading and remove route flicker across critical pages.
- [x] Remove/redirect duplicate or legacy entry routes.
- [x] Add clear CTA flow for 2-3 daily returns.
- [ ] Make `/profile` the canonical “my map / my face / my orientation” screen.
- [ ] Reduce `/today` default payload to daily-guide essentials only; secondary analytics stay behind reveal.
- [ ] Ensure daily answers and micro-interactions persist across refresh and repeated returns.
- [ ] Make progress tracking and weekly-goal entry visible and natural inside `/today`, including soft empty-state guidance when no goal exists.

### Done in this phase
- [x] `Today` and morning ritual direction aligned conceptually.
- [x] Dedicated weekly dashboard route made accessible via interface (previous request).
- [x] Header IA normalized for the pre-JTBD product model and clear hub aliases.
- [x] Local routing stability improved (SW disabled on localhost + legacy `/app` flow normalized).
- [x] Added explicit return cadence block on `/today` for 2-3 daily sessions.
- [x] Today cleanup pass completed (legacy blocks/anchor flows removed or replaced with slot navigation).
- [x] Today visual polish pass completed (single visual language for stage panels and summary rail).
- [x] `/profile` turned into a single mobile-first entry flow: core setup -> build -> ready profile.
- [x] `/onboarding/core` now redirects into `/profile?setup=core` instead of duplicating a second build flow.
- [x] Ready-state profile is now stacked and expandable for mobile instead of exposing all sections at once.
- [x] `/today` first screen reduced to daily guide essentials: day message, card-of-day entry, next action, progress.
- [x] Secondary analytics remain below and/or behind explicit reveal instead of occupying the first mobile viewport.
- [x] `Today` core-profile CTA now points to `/profile?setup=core`, matching the new single-entry profile flow.
- [x] `Утро / День / Вечер` in `Today` no longer behave as separate gated products; they now work only as optional timing modes inside one daily surface.
- [x] Time-of-day states in `Today` now share one visual system: common headers, common content cards, and soft empty states instead of mixed panel styles.
- [x] Forecast text prompts upgraded to API-first v2: shorter editorial prompts, less mystic-template language, stronger human-readable fallback text.
- [x] Tarot and numerology explanation prompts upgraded to API-first v2: more personal, less dictionary-like, no dead spiritual cliches.
- [x] Core profile now includes API-generated interpretation blocks: identity, strengths, watchouts, and four life areas for Profile surface.
- [x] Profile life areas now route directly into system services: love -> compatibility, career -> horoscopes, money -> forecasts, family -> additional profiles.
- [x] Today now exposes direct guided routes to card of the day, compatibility, profile, and deeper helper layers without forcing users into menu discovery.
- [x] Header and auth nav now point to canonical live routes instead of legacy aliases, with reduced duplication in mobile and profile menus.
- [x] Legacy dashboard reduced to alias behavior: `/dashboard` now redirects to `/today`, and key return CTAs no longer send users into the old dashboard hub.
- [x] Sign-to-sign compatibility flow rebuilt into the same guided system: clean pair selection, concise result, personal next step, and heavy text moved behind a secondary reveal.
- [x] Birthdate compatibility flow rebuilt into the same guided system: clearer pair setup, RU/EN city input, lighter result structure, and a clean bridge into deep profile-based compatibility.
- [x] Dead legacy dashboard archive removed from the frontend codebase: unused old page, old dashboard CSS, and unused dashboard component set deleted so the new IA no longer competes with hidden legacy code.
- [x] Profile interpretation prompt and fallback upgraded to a more human “life map” tone, and `Today` / `Profile` frontend text shaping was rewritten to remove templated phrasing and make actions/readouts clearer.
- [x] Server-side daily guidance upgraded: `day meaning` prompt tightened, morning recommendation generation rewritten in a clearer human tone, and morning forecast summary now returns more readable, action-oriented daily language.
- [x] Forecast generation pipeline tightened further: the daily AI forecast now preserves the main theme as a top insight, weekly AI generation now uses actual user context, and weekly fallback copy was rewritten to be more supportive and usable.
- [x] `Today` now persists lightweight daily answers across refresh (`ritual feedback`, `mini-decision`, `question of the day`) and exposes a visible progress tracker instead of hiding day progress in a minor card.
- [x] `/today` now includes a soft weekly-goal empty state: suggested goals, inline goal creation, and a clear bridge into the weekly focus screen when the user has no active goal.

---

## Phase 3: Forecast + Tarot + Compatibility Productization
Status: `COMPLETED`

### Tasks
- [x] Build single Forecast surface with filters (life domains).
- [x] Implement static compatibility content matrix (free/paid depth).
- [x] Implement personalized compatibility overlay from birth profile.
- [x] Ensure tarot thematic spreads reuse shared interpretation context.
- [x] Add consistency checks between Today/Forecast/Tarot outputs.
- [ ] Reframe these modules in UI as separate services around the user profile, not competing roots.

---

## Phase 4: Growth + Rewards Domain
Status: `COMPLETED`

### Tasks
- [x] Implement streak model (day/week milestones).
- [x] Implement archetype progression model.
- [x] Implement natal-linked seals/energetic rewards.
- [x] Implement weekly `Personal Evolution Index`.
- [x] Integrate rewards feedback into Today/Profile/Practice completion.

---

## Phase 5: Design System Hardening
Status: `IN_PROGRESS`

### Tasks
- [x] Lock color tokens, typography scale, spacing grid.
- [x] Standardize button/card/input variants.
- [x] Unify icon style and tarot cover style.
- [ ] Audit all key screens for visual/system consistency.
- [ ] Mobile + desktop QA pass for primary flows.
- [ ] Normalize Profile and Today into the canonical 2-surface mental model.

---

## Phase 6: JTBD + Question-First Productization
Status: `PLANNED`

### Outcome
- TodayFlow becomes a JTBD-first system instead of a module-first collection.
- The user arrives with a real-life question in mind, and the product answers it through the correct screen structure, CTA, and next route.
- The 4 core JTBD become explicit product lanes, not implicit backend capabilities.

### Tasks
- [x] **Daily Navigation Model** — ICA kernel, Profile→Context→Guidance→Action, daily 4 ([DAILY_NAVIGATION_MODEL.md](./DAILY_NAVIGATION_MODEL.md)).
- [x] **Market attention + screen jobs** — L1–L5 tiers, 5 Today domains, retention loop ([MARKET_ATTENTION_AND_SCREEN_JOBS.md](./MARKET_ATTENTION_AND_SCREEN_JOBS.md)).
- [x] **Need Registry v1** — 28 base needs, surface defaults, inference sources ([INTENT_MODEL_V1.md](./INTENT_MODEL_V1.md)).
- [x] **Intent Registry v1** — intent catalog + need mapping + envelope map ([INTENT_REGISTRY_V1.md](./INTENT_REGISTRY_V1.md)).
- [x] **Answer Contract v1** — need-indexed mandatory answer elements + Assembler role ([SCREEN_CONTRACTS_V1.md](./SCREEN_CONTRACTS_V1.md)).
- [x] **Screen Contracts v1** — mandatory user output per screen ([SCREEN_CONTRACTS_V1.md](./SCREEN_CONTRACTS_V1.md)).
- [x] Screen Contracts gap analysis — [status/TODAY_CANON_VS_CODE_DIFF.md](./status/TODAY_CANON_VS_CODE_DIFF.md).
- [x] **P0.1 (sprint):** iOS read `GET /today/contract` — **DONE (2026-07-05):** `TodayCompositionSurfaceView` default in `TodayView` (foundation from `day_story` + ritual via `TodayRitualFlowView`).
- [ ] **P0.2:** Compatibility `potential_tier` + `potential_conditions` — **UI hero = score ring + tagline** (2026-07); tier — metadata/learning layer.
- [ ] **P1:** Living Profile (`recurring_patterns`, `living_changes`; Calendar → Profile/Today).
- [ ] **P1:** Maps P0 (MP-2…MP-3) — Mood · Energy · Habit · Promise heatmaps + story language; см. [TODAYFLOW_PRODUCT_MODEL.md](./TODAYFLOW_PRODUCT_MODEL.md) §4.10.
- [ ] **Engine Projection Specs v1** — **after** P0.1 wire accepted.
- [ ] **Question Registry v1** — Hub / AI only (`explicit_question` → `need_id`).
- [ ] Define need inference contract (surface_open, block, lane, learning_context).
- [ ] Implement shared answer envelope per **need** (not generic lane templates only).
- [ ] Build `Decision OS` as a first-class lane.
- [ ] Repackage `Love OS` around direct relationship questions instead of only compatibility mechanics.
- [ ] Repackage `Money / Career OS` around income, role, and project-decision questions.
- [ ] Build `State OS` for energy, anxiety, and temporary difficult periods.
- [ ] Build `Pattern OS` for recurring scenarios and self-sabotage loops.
- [ ] Expose one best deeper route from each answer into tarot, compatibility, forecasts, or profile.
- [ ] Add learning signals for question intent, chosen route, and completion quality.

### Deliverables
- backend JTBD inference + answer assembler.
- JTBD prompt packs for `love`, `money_career`, `decision`, `state`, `pattern`, `daily`.
- UI structures and CTA patterns that answer latent user questions without requiring free-form input.
- analytics events for inferred JTBD, chosen route, and deeper route opened.

### Definition of Done
- A new user can arrive with a question in mind, not a tool choice.
- The system answers in a single coherent structure.
- The user does not need to understand internal modules to get value.
- The strongest monetization lanes are explicit in the entry flow: relationships, money, decisions.

---

## Phase 6.1: Expanded Product Completion Backlog
Status: `IN_PROGRESS`

This section converts the full current-state audit into one canonical working backlog.

### Critical Product
- [ ] Finalize `Today` as the primary daily engine on one surface, not as separate morning/day/evening products.
- [ ] Ensure `Today` continuously enriches the personalization layer, not only answers the current day.
- [ ] Finalize `Profile` as a true life map, not a form plus utility cards.
- [ ] Build the shared learning LLM layer (canon: [PERSONAL_INTELLIGENCE_LAYER.md](./PERSONAL_INTELLIGENCE_LAYER.md)) that turns answers, journals, questions, routes, and feedback into a more accurate psychotype and response model.
- [ ] Enforce one canonical journey for **web launch v1**: [WEB_LAUNCH_EXECUTION_PLAN.md](./status/WEB_LAUNCH_EXECUTION_PLAN.md) (story-first React). Legacy demo path — **reverse**; see Blueprint §Doc cleanup.
- [ ] Remove remaining legacy meanings, routes, and UI logic that contradict the current product canon.

### Web Launch v1 — **PROCESS FROZEN** (2026-07-01)

**Work plan:** [status/WEB_LAUNCH_EXECUTION_PLAN.md](./status/WEB_LAUNCH_EXECUTION_PLAN.md) — DoD · Launch Freeze · Decision Log · stories  
**UX spec:** [WEB_LAUNCH_PRODUCT_BLUEPRINT.md](./status/WEB_LAUNCH_PRODUCT_BLUEPRINT.md)

**Docs complete.** Дальше: story brief → React → story gate → walkthrough → 10 users → v2.

| Phase | Status |
|-------|--------|
| Product docs + **§4 content model** | 🟡 **ACTIVE** |
| React launch path | ⬜ after Today layers agreed |
| Story walkthrough | ⬜ |
| Launch DoD (11) | ⬜ |
| Field test 10 users | ⬜ |
| v2 planning | ⬜ after data |

### Onboarding & Guest (P0 — contract locked 2026-06-23; **web launch supersedes demo**)

Source of truth: [FIRST_DAY_EXPERIENCE.md](./FIRST_DAY_EXPERIENCE.md) §1–§13.

- [x] **P0.1** `/demo/today` — guest Today (Theme/Action/Progress, no auth, no LLM); fix landing CTA off `/today`.
- [x] **P0.2** `/onboarding/core` — core setup screen (not `/profile?setup=core`).
- [x] **P0.3** `/onboarding/intent` + `/onboarding/reality` — 1 chip each; persist + events.
- [x] **P0.4** Post-signup redirect → `/onboarding/core` when `!core_profile.is_ready`.
- [x] **P0.5** First Today `?first=1` — Theme-first, deterministic, Progress empty.
- [x] **P0.6** Profile as portrait **after** First Today (not first post-signup screen).
- [ ] Signup payload: `locale`, `signup_source`, `initial_referrer` (wire when analytics ready).
- [ ] iOS: same route parity (native onboarding, not Profile-as-setup).

### Profile and Core
- [ ] Connect daily signal collection, weekly state map, and monthly state map into one shared personalization model.
- [ ] Turn the personalization model into an evolving psychotype layer, not just a state log:
  - [ ] daily signals
  - [ ] diary entries
  - [ ] explicit user questions / JTBD entries
  - [ ] route choices
  - [ ] feedback on generated answers
  - [ ] learned response preferences and repeated tensions
- [ ] Finalize full core onboarding (see [FIRST_DAY_EXPERIENCE.md](./FIRST_DAY_EXPERIENCE.md) §4):
  - [x] dedicated `/onboarding/core` route (not Profile hub)
  - [ ] RU/EN name input; optional last name
  - [ ] birth date, optional birth time, city search
  - [ ] gender for RU grammar; locale
  - [ ] explanation of why the data matters (one screen, low friction)
- [x] Finalize stable core build flow:
  - [x] loading screen
  - [x] clear build status
  - [x] ready-state without UI jumps
- [x] Expand profile content:
  - [x] strengths
  - [x] weak spots
  - [x] what to strengthen
  - [x] what to avoid
  - [x] love
  - [x] family
  - [x] money
  - [x] career
  - [x] houses and house meaning
- [x] Finalize multi-profile management:
  - [x] primary profile
  - [x] spouse / partner
  - [x] child
  - [x] close people
- [x] Keep numerology inside the core, not as a competing separate service.

### Today
- [x] Reduce the first screen to:
  - [x] one main meaning of the day
  - [x] card of the day
  - [x] one next step
  - [x] one supporting block
  - [x] fast exits to deeper services
- [x] Remove overload from the middle and lower parts of `/today`.
- [x] Audit all Today CTAs:
  - [x] card of day
  - [x] day number
  - [x] forecast
  - [x] practices
  - [x] quick actions
- [x] Finalize daily texts so they:
  - [x] support
  - [x] warn
  - [x] help the user move through the day
  - [x] do not sound generic
- [x] Strengthen `Today <-> Profile` so the day always reads through the user's core.

### Forecasts
- [ ] Remove remaining canon drift around `Forecasts` and `Horoscopes` as separate roots.
- [ ] Keep any surviving forecast-like functionality only as a secondary helper layer around `Profile`, `Compatibility`, or decision support, not as a period-centered product.

### Compatibility
- [x] Review how the new backend compatibility text lands in the UI.
- [x] Strengthen compatibility result surface:
  - [x] core dynamic
  - [x] where it flows easily
  - [x] where conflict appears
  - [x] what helps
  - [x] how to act
- [x] Strengthen fast compatibility entry from:
  - [x] profile
  - [x] today
  - [x] people circle
- [x] Bring sign compatibility and birthdate compatibility to one meaning and text-quality standard.
- [x] **Compatibility Exploration v1 (web):** hub hero + 10 scenario cards (skins/hover FX); `CompatibilityExplorationResult` — ring %, 4 dimensions, narrative, deep journal, return loop; analyze + profile pair surfaces wired.
- [x] **Compatibility scenario tone (API):** `format_id` + `tone_mode` in encyclopedia selection; LLM system prompt + payload `scenario`; 4 playful series (`after_wine`, `home_renovation`, `best_friends`, `rule_breaker`).
- [x] **Compatibility playful format split (web + API + iOS):** `tone_mode=playful` → short stat-card surface; no encyclopedia intro prepend, no funnel; frontend `presentation=playful`.
- [x] **Compatibility scenario metrics (API):** `compatibility_scenario_metrics.py` — theme-scoped subscores + hero %; funnel filtered to 4 domains per `format_id`; per-domain ↑/↓ drivers.
- [x] **Compatibility pair profiles + scenario (web + API + iOS contract):** `POST /compare` + `/synastry` accept `format_id`; `scenario_context` in response; hub cards → `/compatibility?series=` for logged-in pairs; pair result uses theme-scoped metrics + continuation switch.
- [x] **Compatibility pair iOS (native):** hub series → pair compare with `format_id`; `CompatibilityExplorationResultView` for profile result; scenario score labels + carousel switch.
- [x] **Compatibility deep sections by scenario (web):** `compatibilityScenarioDeepSections.ts` — 4 journal blocks with skin labels (dynamics + pair), not generic 5-pack.
- [x] **Compatibility echo → hypothesis (PIM):** `compatibility_echo_knowledge_v0.py` — per-event echo/switch → inferred hypothesis; aggregate patterns in `meaning_derived_knowledge_v0` (3+ echoes / format interest).
- [x] **Compatibility ILR rules v0:** `interpretation_reference_v0` — echo yes/no/partial, conflicts+yes, scenario switch, deep open; secondary payload filter for compound triggers.
- [x] **ILR-2 reference catalog:** `DATA/reference/interpretation/interpretation_rule_registry_v1.json` + loader/validator; engine reads active rules from JSON.
- [x] **Compat-ref-1 scenario metrics:** `DATA/reference/compatibility/compatibility_scenario_metrics_registry_v1.json` — blends/hero/funnel domains; `compatibility_scenario_metrics.py` loads from registry.
- [x] **Import pilot (attachment):** `DATA/reference/psychology/attachment_style_registry_v1.json` (`active`) — 4 styles, deep_block_bias, source license; loader reads `active` only.
- [x] **Attachment → deep blocks:** `compatibility_attachment_reference_v0.py` — echo on communication/conflicts → block reorder + style hints; dynamics `attachment_reference`; pair `scenario_context.deep_block_order`; web pair UI order.
- [x] **Attachment lens confirm chip (web + iOS + BE):** `compatibility_attachment_knowledge_v0.py` — upsert `behavior_hypothesis:attachment_lens_*`; `compatibility_attachment_confirm` + `profile_atom_correction`; chip under hero on exploration result.
- [x] **ILR spawn → attachment lens:** `spawn_hypothesis_ids: ["attachment_lens:v0"]` on compat echo rules; `spawn_attachment_lens_from_ilr_v0` in ILR sync; rule `beh.compat_echo_communication_yes.v1`.
- [x] **Attachment registry review:** `attachment_style_registry_v1.json` — registry **`active`**, 4 styles `active`; engine reads `active` only.
- [x] **Profile CUM — confirmed attachment lens:** `relationship_insights_top_k` in CUM + `ProfileRelationshipInsightsBlock` (web/iOS).
- [x] **Android attachment lens chip:** dynamics result + `compatibility_attachment_confirm` events.
- [x] **Android compatibility ILR chip:** CUM fetch + `IlrInstanceChip` + `interpretation_instance_confirm`.
- [x] **Compatibility ILR instance chip:** `interpretation_instance_confirm` + `CompatibilityIlrInstanceChip` (web/iOS).
- [x] **Profile ILR instance confirm:** non-`beh.compat_*` instances in `ProfileInterpretationInstanceBlock` (web/iOS); event `interpretation_instance_confirm` / `event_source: profile`.
- [x] **ILR spawn `beh.compat_echo_yes.v1` → attachment lens:** `spawn_hypothesis_ids` on echo-yes rule.
- [x] **OpenAPI learning contracts:** `CompatibilityAttachmentReferenceV0`, `CompactUserModelInterpretationInstance`, meaning payload schemas + `GET /meaning/events/learning-payloads`; JSON Schema in `docs/schemas/`.

### Tarot
- [x] Audit the entire tarot flow:
  - [x] Tarot Hub
  - [x] One Card
  - [x] Three Cards
  - [x] Tarot Result
- [x] Make every spread read as:
  - [x] meaning
  - [x] manifestation
  - [x] caution
  - [x] next step
- [x] Verify card of the day works and feels like the central ritual of the day.
- [ ] **Tarot Question-First v1** (canon `SCREEN_CONTRACTS_V1` §6.4–§6.8):
  - [x] Canon + event dictionary
  - [x] Phase A web: Hero → concern → refine → spread → ritual (`TarotQuestionFlow`, `/tarot/spread/[spreadId]`)
  - [x] Phase B web: synthesis blocks + 3 today actions + self-question + resonance + next routes (`TarotSpreadReading` v2, `TarotReadingStorySurface`)
  - [x] Phase C web: journey history + Today deepen bridge (`tarotJourneyStore`, anchor spread, `tarot_deepen_started`)
  - [x] iOS Phase C: `TarotJourneyStore`, journey panel на hub, Today «Исследовать глубже» → anchor spread + `tarot_deepen_started`
  - [x] iOS question-first funnel: `TarotQuestionFlowView`, generic `TarotSpreadRitualView`, hub `/tarot`, reading v2 + resonance events
  - [x] Nav cleanup: `/guidance` и `/questions` → `/tarot` (редиректы + удалены legacy pages)
  - [ ] Android паритет воронки
- [ ] **Tarot Immersive Dark Shell v1 (код)** — после Figma ниже; полный web-флоу; удалить dual-theme UI в коде.

- [ ] **Figma: Tarot Immersive Dark Shell — полный web-флоу** (см. spec ниже). **Исполнитель: дизайн в Figma**, не код. Код — отдельный пункт после DoD Figma.

#### Figma: Tarot Immersive Dark Shell — полный web-флоу (2026-07-06)

**File:** `WxwGUutaPRKpLKEvAICEEC` (TodayFlow Product UI)

**Источник визуала:** `archive · draft-tarot-dark-shell` (`65:2`) — **только** main + rail + tokens (фон, glass, gold, типографика блоков). **Не** копировать кастомный sidebar «ORACLE OS» / «TodayFlow ORACLE OS» из draft.

**Shell (фиксировано, как у остального product web):**

| Колонка | Ширина | Содержание |
|---------|--------|------------|
| Sidebar | 240px | **Стандартный** `DsAppSidebar`: Сегодня · Моя карта · Совместимость · **Таро (active)** · Практики + Настройки внизу — **тот же компонент/стиль**, что `web-compatibility-hub` `40:4`, `web-practices` `55:111` |
| Main | fluid (~880px) | Контент шага воронки |
| Rail | 320px | Общий для всего флоу (см. ниже) |

**Grid:** `240 | minmax(0,1fr) | 320` — как registry product web, **не** sidebar draft `65:4`.

---

**Создать фреймы (именование → route):**

| # | `frame_name` | Route | Stepper rail |
|---|--------------|-------|--------------|
| 1 | `web-tarot-hub` | `/tarot` | neutral (до шага 1) |
| 2 | `web-tarot-question` | `/tarot/question` | **1 · Вопрос** active |
| 3 | `web-tarot-spread-ritual` | `/tarot/spread/[spreadId]` | **2 · Карты** active |
| 4 | `web-tarot-result` | `/tarot/result` | **3 · История** active (+ **4 · Мост** в CTA-блоке) |

**Опционально (отдельные фреймы или variants):** guest limit gate · loading · error · refine-only sub-state на question.

---

**Main — что перенести из `65:2` (hub):**

- Header: eyebrow `TAROT / IMMERSIVE HUB` + status pills (карта дня, счётчик раскладов — placeholder copy)
- Row 1: hero «Задайте вопрос дню» + primary CTA «Начать расклад» + secondary «Продолжить прошлый вопрос»
- Row 1: recommended ritual card (visual + preset spread)
- Row 2: «Расклады для решения» — 3 карточки (**3** / **5** / **1** — copy из draft; product IDs: `three_cards`, `guidance_choice_two`, `one_card`)
- Row 2: «Карта дня» + «Вопрос для старта»

**Main — question (`§6.4` steps 2–3):**

- Домены concern (chips) + textarea своего вопроса
- Refine: варианты по домену + skip
- Spread select (если не на hub) — карточки **по вопросам**, не «1/3/5 карт»
- Те же dark tokens, **не** cream `55:449`

**Main — ritual (`§6.4` step 5):**

- Вопрос пользователя (quote)
- Pick + flip deck / slots; CTA «Получить толкование» disabled → enabled
- Карты **portrait**, не landscape crop

**Main — result (`§6.5`, структура колонок как `29:692`, tokens как hub):**

- Колонка карт (portrait, labels позиций)
- Колонка narrative: вопрос → verdict (Instrument Serif) → «Почему сейчас» → 3 insight rows → action box → follow-up chips → bridge (Today / practice / compat)
- **Запрещено в UI:** wall of card keywords, light theme, второй sidebar

---

**Rail — единый на все 4 экрана (из `65:2` right column):**

1. **Ritual gate** — copy про контекст дня (без LLM UI)
2. **Путь расклада** — stepper 1–4: Вопрос · Карты · История · Мост (highlight по экрану)
3. **Связи дня** — Фокус / Риск / Практика (placeholder chips)

---

**Удалить / архивировать в Figma (чтобы не было двух истин):**

| Frame | node | Действие |
|-------|------|----------|
| `web-tarot-hub` (светлый) | `55:449` | → `archive · web-tarot-hub-light` или удалить после промоции нового hub |
| `archive · draft-tarot-dark-shell` | `65:2` | После промоции: переименовать в `web-tarot-hub` **или** оставить в archive, canonical — новый ряд фреймов |
| Старый `web-tarot-result` | `29:692` | → `archive · web-tarot-result-light-sidebar` если sidebar не product-standard; заменить unified dark result |
| Registry card `11 web-tarot-hub` (0%) | `69:1221` | Обновить статус / удалить дубль |

**Не трогать:** iOS tarot frames (`ios-tarot-*`) — отдельный parity; android-tarot-*.

---

**DoD Figma:**

- [ ] 4 web-фрейма в product grid (240/ fluid /320) со **стандартным** sidebar
- [ ] Один token set (dark immersive) на hub → result
- [ ] Rail + stepper на всех экранах
- [ ] SCREEN REGISTRY обновлён (frame_name \| node_id \| route)
- [ ] `figmaMap.ts` layouts: `web-tarot-hub`, `web-tarot-question`, `web-tarot-spread-ritual`, `web-tarot-result` → node_ids
- [ ] Светлый `55:449` в archive / удалён
- [ ] Link frames в flow diagram (hub → question → ritual → result)

**После DoD Figma → код:** пункт «Tarot Immersive Dark Shell v1 (код)».

#### Tarot Immersive Dark Shell v1 — spec код (2026-07-06)

**Цель:** один связный тёмный Tarot-флоу (hub → question → ritual → result → bridge) по макету Figma **`archive · draft-tarot-dark-shell`** (`node_id` **`65:2`**, file `WxwGUutaPRKpLKEvAICEEC`). Старый светлый hub (`web-tarot-hub` `55:449`) и patchwork `theme="light"|"dark"` **удалить**, чтобы не было двух параллельных «истин».

**Жёсткие ограничения (от заказчика):**
- **Shell и сетка не меняем:** `ProductWebAppShell` → sidebar · main · rail (`DsAppShell`, ~240 / fluid / ~320). Стандартное product-меню (`DsAppSidebar`, те же пункты и routes) — **не** копировать кастомный sidebar «ORACLE OS» из draft.
- **Из draft берём:** визуальный язык (фон `#1a1714`, glass-панели, золото `#c9a96e` / `#d4af37`), типографику блоков, composition **внутри** main + rail.
- **Контракты и data не ломаем:** `SCREEN_CONTRACTS_V1` §6.4–§6.8, `tarot_answer_v1`, `tarotQuestionFlowCanon`, events (`tarot_session_started` … `tarot_reading_follow_up`), guest limits, journey/deepen bridge.

**Figma → продукт (hub `65:2`, main column):**
| Блок draft | Route / step | Примечание |
|---|---|---|
| Hero «Задайте вопрос дню» + CTA | `/tarot` | Primary → question flow; secondary → last session |
| Status pills (расклады / карта дня) | `/tarot` header | Data-driven, не декор |
| Recommended ritual card | `/tarot` | Deeplink в preset spread |
| «Расклады для решения» (3 / 5 / 1 cards) | hub + spread select | **ID раскладов** — существующие API; только UI/copy из draft |
| «Карта дня» + «Вопрос для старта» | hub + `/tarot/card-of-the-day` | Card portrait, `object-fit: contain` |

**Figma → продукт (rail, slot `rail`):**
| Блок draft | Содержание |
|---|---|
| Ritual gate | Контекст дня перед раскладом (Today contract slice) |
| Путь расклада (1–4) | Stepper: Вопрос → Карты → История → Мост; active step по route |
| Связи дня | Focus / Risk / Practice chips из day context |

**Шаги воронки (все экраны — dark shell, один token set):**
1. **Hub** `/tarot` — immersive hub по `65:2`
2. **Question** — domain + refine (inline или step; стиль dark, не cream hub)
3. **Ritual** `/tarot/spread/[spreadId]` — pick/flip; dark panels как в draft
4. **Result** `/tarot/result` — narrative по §6.5; layout можно унаследовать структуру `web-tarot-result` `29:692`, но **только** в tokens dark shell (не второй theme switch)
5. **Bridge** — CTA в Today / practice / compat (§6.6)

**Удалить / заменить (web, после parity нового UI):**
- `TarotWebHub` light layout + light-only CSS в `productWebScreens.module.css` (cream input, spread rows `55:449`)
- Переключатель `TarotWebScreen` `theme="light"` для tarot; единый `TarotDarkShell` или `theme="dark"` by default без light path
- Orphan / legacy UI: `TarotSpreadRitual.module.css`, `TarotHero`, `SpreadSelection` на hub, дубли `/tarot/spread/one-card` · `three-cards` если funnel полностью через `[spreadId]`
- Figma registry: **`web-tarot-hub` → `65:2`** в `figmaMap.ts`; пометить `55:449` archived (не implementation source)

**Не трогать без отдельной задачи:** backend spread API, `tarot_reading_synthesis`, iOS/Android (отдельный parity item после web DoD).

**DoD (web):**
- [ ] `/tarot` визуально соответствует `65:2` в main+rail; sidebar = стандартный product nav
- [ ] Полный путь hub → result без смены «другой темы» посередине
- [ ] Нет импортов удалённых light-tarot компонентов; `npm run build` green
- [ ] Карты не обрезаются (portrait + contain)
- [ ] Events + guest gates сохранены
- [ ] `figmaMap.ts` + строка changelog в этом файле

**Learning Δ (PIM):** те же events; rail Ritual gate может emit `sphere_opened` / context preview — без новых LLM calls.

### Texts and AI Pipeline
- [ ] Fully remove dependency on old meaning-shaping behavior inside `quality_gate`.
- [ ] Finalize generation quality for:
  - [ ] today
  - [ ] forecasts
  - [ ] profile interpretations
  - [ ] tarot
  - [ ] compatibility
- [ ] Lock one text standard:
  - [ ] clear
  - [ ] human
  - [ ] low-noise
  - [ ] no dead cliches
  - [ ] no esoteric filler
- [ ] Continue building the learning layer:
  - [ ] generation logging
  - [ ] feedback
  - [ ] prompt versioning
  - [ ] curated examples
  - [ ] user-level psychotype synthesis from daily answers, journals, questions, routes, and feedback
  - [ ] reusable learned interpretation context for future generations
  - [ ] internal quality memory: answer -> user reaction -> downstream outcome
  - [ ] use this quality memory to separate stronger and weaker response patterns
  - [ ] keep this loop invisible in user-facing language
- [ ] Add offline evaluation later to compare prompt quality with evidence.

### UX and Navigation
- [ ] Fully audit mobile navigation.
- [ ] Remove duplicate or conflicting routes.
- [ ] Audit all buttons and links across the product.
- [ ] Ensure the user always understands:
  - [ ] where they are
  - [ ] what this screen is
  - [ ] what to do next
  - [ ] why the next module matters

### Mobile
- [ ] Audit all key screens on mobile width:
  - [ ] profile
  - [ ] today
  - [ ] forecasts
  - [ ] horoscopes
  - [ ] tarot
  - [ ] compatibility
  - [ ] calendar
  - [ ] habits
  - [ ] cycle
- [ ] Check spacing, heights, scroll, sticky layers, and overlays.
- [ ] Ensure menus, modals, and disclosure sections do not break the flow.

### Design
- [ ] Finalize one visual language for:
  - [ ] cards
  - [ ] typography
  - [ ] accents
  - [ ] atmospheric background layers
  - [ ] motion
- [ ] Ensure heavy blocks reveal progressively instead of dumping everything at once.
- [ ] Remove random visual leftovers from older screen generations.

### Data and Input
- [ ] Finalize RU/EN city input.
- [ ] Allow normal name input beyond Latin-only assumptions.
- [ ] Verify geocoding returns stable coordinates.
- [ ] Verify save and rebuild flow when core data changes.

### Performance
- [x] Continue removing duplicate heavy requests (incremental: `/today` supports `light=1` and `/today/opening` for fast first paint; full payload unchanged by default).
- [ ] Audit caching for:
  - [ ] core profile
  - [ ] daily forecast
  - [ ] monthly/yearly forecast
  - [ ] tarot explanation
  - [ ] compatibility
- [ ] Remove unnecessary rerenders and page jitter.
- [ ] Audit speed of `/today`, `/profile`, `/horoscopes`.

### QA and Cleanup
- [ ] Walk all legacy routes and decide which stay as aliases and which get deleted.
- [ ] Check console for `404`, `500`, and runtime warnings.
- [ ] Verify auth redirects and return-to-origin flow.
- [ ] Verify full Docker run scenario.
- [ ] Keep `PRODUCT_EXECUTION_TRACKER.md` as the single working execution point.

---

## 5.1 Text Generation Policy Shift

New rule:
- meaningful user-facing texts should be generated through API-backed interpretation;
- the old `quality_gate` is not the source of meaning anymore.

Operational consequence:
- we now store prompt/version/output traces for `forecast`, `tarot`, and `numerology` generation flows;
- quality improvements must come from prompt/context iteration and reviewed datasets, not from over-aggressive gating.

## 5.2 Learning Layer Status

Status: `IN_PROGRESS`

### Implemented
- [x] Added DB tables for `prompt_versions`, `generation_logs`, `generation_feedback`.
- [x] Added backend `LearningService`.
- [x] Added `POST /learning/feedback`.
- [x] Added admin prompt registry listing.
- [x] Connected forecast/tarot/numerology generators to best-effort logging.

### Next
- [ ] Add implicit feedback signals from UI interactions.
- [ ] Surface generation IDs to frontend where user feedback is collected.
- [ ] Add offline evaluation scripts and curated dataset export.
- [ ] Route `Profile` and `Today` generation through the same logged pipeline.

`quality_gate` may remain only as:
- output sanitation,
- broken payload detection,
- anti-garbage safety layer.

It must not:
- flatten rich text,
- over-template copy,
- replace specific interpretation with dead generic phrases.

## 5.3 Day Engine — execution backlog

Linked canon: [DAY_ENGINE_AND_COHERENCE.md](./DAY_ENGINE_AND_COHERENCE.md). Tracker checklist: **§4.7**.

Ordered work (aligns with canon §7):

1. **UI garbage pass** — duplicates, abstract CTAs, blocks without action (keep §4.6 information diet).
2. **DE-1** — done: [DAY_CONTEXT_V0.md](./DAY_CONTEXT_V0.md) + schema + `build_day_context_v0`; при появлении публичного DTO — сверка типов с iOS.
3. **DE-2** — done: `build_day_context_v0` в `build_today_narrative` до LLM; guide из `DayContext.layers`; hash и версия контракта в `generation_logs.input_payload` (`day_context_sha256`, `day_context_contract_version`).
4. **DE-4** — done: расширены `POST /meaning/events` и веса колец; клиенты (Today web + iOS) переведены на канонические `event_type` где однозначно; см. `TODAY_PERSONALIZATION_CORE`; DE-3 закрыт для Today narrative + learning.
5. **DE-5** — done: агрегаты по `meaning_events` (окно 7–60 дней) в DayContext и learning; подсказки `pattern_hints` в psychotype summary и в user-prompt всех surface Today narrative.
6. **DE-6** — done: intent + head_topic в DayContext и narrative (см. §4.7 DE-6). **DE-7** — done: flow closure в fusion + UI главного шага (см. §4.7 DE-7).
7. **DE-7** — v0–v2: flow closure в fusion / slim (в т.ч. `guide_meaning_completions_today`). **DE-9** — v0: `day_history_v0` в DayContext и `day_history` в user JSON narrative (вчера + 7 дней fusion scores + дельта). **DE-13** — backlog: цепочка узких LLM/артефактов вместо монолитного `surface=guide` (см. [DAY_ENGINE_AND_COHERENCE.md](./DAY_ENGINE_AND_COHERENCE.md) §2.1).
8. **Обязательное продолжение контура (не «опционально»):** **DE-8** (глубина: контракт + управляемая ветвь промпта + UI настройки, когда API v0 готов) и **DE-9** (время: уже в DayContext/промпте — довести **наблюдаемость** для пользователя и при необходимости обогащение смысловыми сигналами по дням). **DE-10 / DE-11** — по согласованию и приватности, после измеримого ядра. **DE-13** — целевая декомпозиция монолитного guide (см. [DAY_ENGINE_AND_COHERENCE.md](./DAY_ENGINE_AND_COHERENCE.md) §2.1); вести как отдельный эпик, не смешивать с косметикой UI.

**Rule:** any merge that touches Today narrative, ritual payload, or learning ingestion should update §4.7 table status or this subsection.

### 5.3.1 Канон пользовательского копирайта Today (web ⇄ iOS)

**Источник формулировок (SoT для текста на экране Today):** `frontend/src/components/today/todayRitualCopy.ts` — объект `RITUAL_COPY` и экспортируемые рядом `format*`; **дословное зеркало:** `ios/TodayFlow/TodayFlow/Design/TodayRitualCopy.swift` (в т.ч. блоки `TodayWeb*`). Experience canon: [TODAY_SCREEN_V1_CANON.md](./TODAY_SCREEN_V1_CANON.md). Логика Day Engine: [DAY_ENGINE_AND_COHERENCE.md](./DAY_ENGINE_AND_COHERENCE.md), [DAY_CONTEXT_V0.md](./DAY_CONTEXT_V0.md).

**Связь с п.1 (UI garbage):** пользовательский русский в `frontend/src/components/today` вне `todayRitualCopy.ts` / каталогов i18n — долг §5.3; правки копирайта сценария Today делаются в каноне и зеркале, а не «в месте вызова».

**Вопрос дня (рабочий слой):** промпты и опции — в `todayRitualCopy.ts` (`RITUAL_QUESTION_OF_DAY_*`, `buildRitualQuestionOfDayDefaultCards`); `buildQuestionOfDay` в `todayPageUtils.ts` только выбирает пул и индекс по дате; зеркало — `TodayWebQuestionOfDayCopy` в `TodayRitualCopy.swift`.

**iOS, компактный «быстрый ответ» в `TodayView`:** шапка, подписи шагов, варианты «да/нет/неясно», контекст «отношения/работа», кнопка сохранения, префиксы баннеров, тост успеха — в `RITUAL_COPY` (`workingLayerCompactQuickAnswer*`, `workingLayerQuickDecision*`, `workingLayerQuestionOfDaySavedContextPrefix`) и `TodayWebWorkingLayerCopy`.

**iOS, нативные композеры на `TodayView` (утро / чек-ин / дневник / вечер):** весь видимый RU — в `RITUAL_COPY` (`todayView*`, общее `todayViewComposerSaving`, промпты типов дневника `dayJournalPrompt*`) и зеркале `TodayWebTodayViewComposerCopy` + `TodayWebDaySectionCopy` / `TodayWebEveningSectionCopy` (подписи шкал чек-ина); форматтеры `formatTodayViewMorningComposerSavedBanner`, `formatTodayViewJournalSavedCountBanner`.

**iOS, основной экран `TodayView` (герой, guide/день/вечер, таро, fusion, фолбэки):** строки в `TODAY_SHELL_COPY` (`shell*` в `todayRitualCopy.ts`) и зеркале `TodayShellCopy` в `TodayRitualCopy.swift`; переиспользуются `TodayWebGuideSectionCopy.guidePanelEyebrowToday`, `TodayRitualCopy.dayEngineBriefEyebrow`, `TodayWebFlowTabsCopy`, `TodayWebWorkingLayerCopy` (да/нет в отклике таро), `TodayWebDaySectionCopy` (типы дневника в ленте); форматтеры `formatShell*` рядом с `TODAY_SHELL_COPY`.

**Четыре сферы + ритуальный поток iOS:** пользовательские фолбэки сфер и энергетического риска — `RITUAL_COPY.fourArea*` в `todayRitualCopy.ts`, логика в `todayFourAreas.ts` (паритет `RitualFourAreaBuilder`); строки экрана `TodayRitualFlowView` (дисклеймер метрик героя, a11y ритма, защита дня, вечерний лоадер, число дня, треугольник сфер, подсказки целей) — `ritualFlow*` и форматтеры `formatFourAreaEnergyRiskChunk`, `formatRitualFlow*` в TS и зеркальные `TodayRitualCopy` / `TodayShellCopy` (подписи орбов героя).

**Продуктовый лейаут `TodayExperienceLayout` (RU/EN):** канон `TODAY_EXPERIENCE_CHROME_RU` / `TODAY_EXPERIENCE_CHROME_EN` и `formatExperience*` / `experienceChromeBundle` в `todayRitualCopy.ts`; зеркало — `TodayExperienceChromeCopy.swift` (включая пресеты «удачного окна» для блока числа дня).

**iOS главный TabView + вкладки Flow и Практики (RU/EN):** канон `TODAY_MAIN_TAB_COPY_*`, `FLOW_TRACKER_CHROME_*`, `PRACTICES_EXPERIENCE_CHROME_*` и хелперы (`flowStreakTitle`, `practicesDaysStreak`, …) в `frontend/src/components/today/flowPracticesMainTabChrome.ts` (реэкспорт из `todayRitualCopy.ts`); зеркало — `FlowPracticesMainTabChromeCopy.swift`; точка входа вида — `FlowTrackerChrome.swift` (`typealias` на `*Copy`).

---

## 6) Current Priorities (Execution Order)

### 🔴 Phase 3 — Screen Block Definition (единственный приоритет)

**Канон:** [TODAY_SCREEN_V1_CANON.md](./TODAY_SCREEN_V1_CANON.md) + [PROFILE_SCREEN_MASTER.md](./PROFILE_SCREEN_MASTER.md) — build (full internal) vs reveal (L1–L4 UI).

**Порядок P0:** Onboarding (5) → Profile **Identity · Intent · Reality · Direction** → **затем** Today Theme · Action · Progress. Today = проекция Profile, не раньше source.

| Step | Status |
|------|--------|
| Onboarding (5 секций) | 🟡 defined v1.1 — **review** |
| Profile Identity (Facts · Markers · Narrative) | 🟡 v1.3 — **review** |
| Profile I · R · D (non-Identity) | 🟡 v1.2 draft |
| Profile Behavior · Knowledge · Rhythm · Map | ⬜ |
| Today T · A · P | ⏸ blocked |
| Test B / viability | ⏸ blocked |

---

### ⏸ Phase 4 — Core Loop Viability Test (paused)

**Статус:** PAUSED — blocked on Screen Block Definition (Today T→A→P). Instrument `?core_loop=1` = черновик, не канон UI.

| Step | Status |
|------|--------|
| Test A backend | ✅ conditional |
| Instrument (G1-surface web) | ⚠️ draft (needs §2 alignment) |
| Test B pulse 1 | ⏸ |
| Verdict A or B | ⏸ OPEN |

---

### Цель: зацикленный умный сервис (Day Engine) — **после First Day P0**

**Канон:** один логический **DayContext** → генерация narrative → экраны Today → **действия и ответы пользователя** (meaning events, Flow, вечер, feedback с `generation_id`) → агрегаты и следующий DayContext. Это не набор разрозненных экранов, а **сервис с обратной связью**; см. [DAY_ENGINE_AND_COHERENCE.md](./DAY_ENGINE_AND_COHERENCE.md) (вход/выход, §2.1 уровни 5–6, §5 критично добавить).

**Уже в контуре (§4.7):** DE-1…DE-7, DE-12; обучение: события, паттерны, intent, fusion closure в UI.

**Следующие обязательные инкременты (порядок работ):**

0. **DE-8** — **DONE** (§4.7): глубина в профиле + на Today, тарифный кламп, meaning-событие `today_narrative_depth_changed`.
1. **DE-9** — сделать **temporal context** не только в промпте: явный UX/API слой «вчера / неделя» там, где усиливает доверие и решение (веб + iOS, те же контракты).
2. **Learning pipeline (§5.2 Next)** — неявные сигналы из UI, полнота `generation_id` там, где собирается исход, **единый logged pipeline** для Profile и Today narrative (как в чеклисте §5.2).
3. **UI garbage pass (§5.3 п.1)** — убрать дубли и пустые CTA без действия; не опережать смысловую цепочку.
4. Затем — канонический путь продукта: `core build → profile → today → deeper services`; **Profile** как живая карта; **Today** как ежедневный двигатель; JTBD-лейны без разрыва с Day Engine.

5. Качество навигации, копирайт, мобильный QA — непрерывно, но **после** фиксации измеримого ядра контура (п. 0–2).

### 6.2 Branch goal — «Today» 100% (Definition of Done for this branch)

**Смысл «100%» здесь:** экран **Today** (веб + нативный iOS) соответствует канону **§4.6 Daily ritual UX** и **[TODAY_SCREEN_V1_CANON.md](./TODAY_SCREEN_V1_CANON.md)**; цепочка **Day Engine** для дня замкнута на уровне **обязательного minimum** ниже.

**Не входят в эту метрику:** Phase 6 JTBD, DE-10/11/13, полный редизайн Forecast как отдельного сервиса вокруг профиля.

#### Обязательно (DoD ветки)

1. **Контракты и загрузка:** `GET /today`, `GET /tracking/fusion/{date}`, `POST /today/narrative` (guide → day_layer → spheres → evening) корректно обрабатывают ошибки и пустые состояния; после ритуала guide пересобирается с `ritual_context` (веб + iOS).
2. **Ритуал:** карта → число → настроение (+ `head_topic` где задано); пользовательский копирайт ритуала только из `todayRitualCopy` / `TodayRitualCopy` (паритет строк web ⇄ iOS).
3. **Секции канона:** ориентиры, сферы, главный шаг, база дня (четыре опоры), глубина (CTA), вечерняя фиксация — присутствуют и не противоречат TODAY_WEB §3–4.
4. **Сигналы:** канонические `event_type` и payload для meaning-событий **паритет web ⇄ iOS** для чипов карты, числа, главного шага и essentials (см. TODAY_WEB §4.1, §5).
5. **Персонализация narrative:** вход в LLM через сжатый `user_core` / slices без дублирования сырого `profile` в guide JSON (см. `today_narrative` и связанные тесты контракта).
6. **Документация:** при закрытии ветки обновить статус в **§4.7** и **[IOS_TODAYFLOW_STATUS.md](./status/IOS_TODAYFLOW_STATUS.md)** под фактическое состояние.

#### Желательно (не блокер «100%» этой ветки)

- **DE-7** закрыт в §4.7 (v3 UI); дальнейшая **жёсткая связка** текста вариантов шага с событиями — см. backlog в строке DE-7.
- **DE-8:** пользовательская настройка `depth_level` в UI — перенесено в **обязательный** дорожник §6 (п. 0), не «когда-нибудь».
- Динамический набор сфер и отдельные API под фокус дня/вечер (TODAY_WEB §5 — следующие итерации).

#### Явно вне скоупа ветки

- DE-10 Health, DE-11 journal excerpts, DE-13 multi-call narrative pipeline.

---

## 7) Progress Log

Use format:
- `YYYY-MM-DD` | `Area` | `Change` | `Status` | `Notes`

Historical note:
- older entries may mention the legacy `5-section` IA model;
- these entries describe what was implemented at that time and do not override the current question-first product canon.

- 2026-07-08 | Web Today narrative | client-side same-day dedup (sessionStorage) | DONE | `fetchTodayNarrativeCached` в `todayNarrativeCache.ts`: ключ date/surface/parent/topic/depth/ritual_fp; hit → без POST; in-flight coalesce; `force` после ритуала. Паритет iOS `cachedNarrative` + переживает remount вкладки. Today page + LifeSpheres deepen.
- 2026-07-08 | Today narrative cache | fix «Сегодня собирается бесконечно» — same-day reuse | DONE | `_load_narrative_cache` / `_load_funnel_step_cache`: `day_context_sha256` = предпочтение свежести, не жёсткий гейт. Причина: `get_daily_fusion_index` дрейфует от внутридневной активности пользователя → каждый заход был cache-miss + повтор LLM-воронки. Теперь переиспользуется свежий лог со стабильным ключом (date/surface/ritual_fp/intent_fp/tier/depth/snapshot), как `day_story_v1`. AMLL: `reason=GATE:cache_hit:same_day_reuse`. Backend-only, паритет web/iOS/Android через тот же REST. См. `DAY_CONTEXT_V0.md` §Промпты narrative.
- 2026-07-08 | Web product UI | CSS convergence: domain layouts → productPageLayout | IN PROGRESS | `todayWebV2` / `tarotWebV2` / `compatibilityWebV2` удалены; Today·Tarot·Compat hub импортируют `productPageLayout.module.css`.
- 2026-07-08 | Web product UI | habits / asceticisms / maps / horoscope → ProductPageScreen | IN PROGRESS | `/habits`, `/asceticisms`, `/asceticisms/tracker`, `/maps/*` (7), `/horoscope/today` + `[sign]` — orbit-page / todayflow-serene убраны; v2 header + pl.panel + toolbar.
- 2026-07-08 | Web product UI | cycle / journal / affirmations / discover / library / lunar → ProductPageScreen | IN PROGRESS | `/cycle`, `/journal`, `/affirmations`, `/affirmations/tracker`, `/discover`, `/library`, `/lunar/today` — orbit-page убран; loading/guest через ProductPageScreen; inner content частично legacyHost.
- 2026-07-08 | Web product UI | questions / numerology / compatibility sub-routes → ProductPageScreen | IN PROGRESS | `/questions/*` (6), `/numerology/*` (7), `/compatibility/analyze`, `/compatibility/signs`, `/compatibility/birthdates` + result pages — orbit-page убран; QuestionEntryCard / compat-desktop / calc forms в legacyHost.
- 2026-07-08 | Web product UI | calendar / profile-summary / subscriptions / discover pattern → ProductPageScreen | IN PROGRESS | `/calendar`, `/profile-summary`, `/subscriptions`, `/discover/pattern/[axis_id]` — orbit-page и hero images убраны; v2 header + pl.panel + legacyHost.
- 2026-07-08 | Web product UI | challenges / reports / help / tarot cards → ProductPageScreen | IN PROGRESS | `/challenges`, `/challenges/[id]`, `/reports/full`, `/reports/thematic`, `/reports/thematic/[theme]`, `/help`, `/help/*`, `/tarot/cards/[slug]` — orbit-page и hero images убраны; metadata help → layout.tsx; inner forms/viewer в legacyHost.
- 2026-07-07 | Web product UI | Today dashboard v2 aligned to Profile reference | IN PROGRESS | Today dashboard на `productPageLayout` + `productV2Surface` tokens; wide canvas `mainWide`; cards/type/spacing match profile v2.
- 2026-07-21 | Today / Story | PR-3 day_story_v1 explainable slice | **IN PROGRESS** | Backend trace+gates; FE domain honesty; soft why from claims; strengthen from practice_recommendation only. [PR3_TODAY_PRODUCTION_SURFACE.md](./PR3_TODAY_PRODUCTION_SURFACE.md)
- 2026-07-21 | Web product UI | PR-3 Today Production Surface | **IN PROGRESS** | Composition = single reading line + optional soft why + optional one strengthen tool. Block gate: why / 10–20s / action.
- 2026-07-21 | Profile | PR-4 Profile Canon (slice 4.1) | **ACCEPTED / CLOSED** | Who-you-are surface; umbrella applied; day/maps out; natal stays on Profile as source (person first). Next: [audits/PROFILE_AS_SOURCE_CONSUMPTION_AUDIT.md](./audits/PROFILE_AS_SOURCE_CONSUMPTION_AUDIT.md). [PR4_PROFILE_CANON.md](./PR4_PROFILE_CANON.md)
- 2026-07-21 | Product | Voice: person not system | **ACTIVE** | UI never describes system state; missing CTA = absence · unlock · valued action. [TODAYFLOW_VOICE_CANON.md](./content/TODAYFLOW_VOICE_CANON.md) §0.05–§0.06 · [UNDERSTANDING_PROGRESS_AND_DEPTH_CANON.md](./UNDERSTANDING_PROGRESS_AND_DEPTH_CANON.md)
- 2026-07-21 | Profile | Profile E2E architecture principle | **ACTIVE** | Model = contract executor; block_eligibility before prompt; architectural defects only. [PROFILE_E2E_RECONSTRUCTION.md](./PROFILE_E2E_RECONSTRUCTION.md) · [PROFILE_E2E_BLOCK_PASSPORT_TEMPLATE.md](./audits/PROFILE_E2E_BLOCK_PASSPORT_TEMPLATE.md)
- 2026-07-21 | Profile | Profile Production-Faithful Capture Pack | **ACTIVE** | Infra only: capture + eligibility vs ran + Case A/B. No prompt/UI/contract product fixes until packs. [PROFILE_PRODUCTION_CAPTURE_PACK.md](./audits/PROFILE_PRODUCTION_CAPTURE_PACK.md)
- 2026-07-21 | Profile | Profile End-to-End Reconstruction | **ACTIVE** | Architecture-first: passport → gate → prompt → accept → publish. Next: run capture packs, classify defects without MODEL. [PROFILE_E2E_RECONSTRUCTION.md](./PROFILE_E2E_RECONSTRUCTION.md)
- 2026-07-21 | Profile | Profile as source (post–PR-4) | **NEXT** | Wire Experiences to Snapshot after E2E map; kill parallel SoI. [audits/PROFILE_AS_SOURCE_CONSUMPTION_AUDIT.md](./audits/PROFILE_AS_SOURCE_CONSUMPTION_AUDIT.md)
- 2026-07-21 | Product | Understanding Progress & Depth canon | **ACCEPTED** | Progress = quality of understanding. Never empty Profile; missing field → what opens + why; subscription = depth not chopped blocks; trial = full experience. [UNDERSTANDING_PROGRESS_AND_DEPTH_CANON.md](./UNDERSTANDING_PROGRESS_AND_DEPTH_CANON.md)
- 2026-07-21 | Content | Voice: TodayFlow не говорит о себе | **ACCEPTED** | Ban «мы/система/ИИ/алгоритм» как субъект; факт в центре. [TODAYFLOW_VOICE_CANON.md](./content/TODAYFLOW_VOICE_CANON.md) §0
- 2026-07-21 | Web product UI | PR-2 App Shell (rail honesty) | **ACCEPTED / CLOSED** | Канон: [PR2_APP_SHELL.md](./PR2_APP_SHELL.md). Один `ProductWebAppShell`; rail = данные; без reserved empty track; Profile структурный эталон. К shell — только багфиксы. Today content → PR-3.
- 2026-07-08 | Web product UI | Product Page Standard v1 (единый продукт) | **ACCEPTED** | Один shell (`ProductWebShellLayout`), один page wrapper (`ProductPageScreen`), tokens (`productV2Surface`) + grids (`productPageLayout`). Запрет: orbit-page / custom hero / локальные карточки на in-app routes. Миграция: Today·Profile·Practices·Tarot·Compat hub — partial; Tracking·Weekly·Account — partial; ~40+ orbit routes — backlog. См. PR-2.
- 2026-07-08 | Web product UI | Account profiles/subscriptions/reports → ProductPageScreen | IN PROGRESS | `/account/profiles`, `/account/subscriptions`, `/account/reports` — orbit hero removed; v2 header + legacyHost panels.
- 2026-07-07 | Web product UI | Today composition embed + full=1 product shell | IN PROGRESS | `rootWebEmbed`/`sectionWebEmbed` v2 panels; `/today?full=1` → `TodayWebDashboard layout=ritual` (unified nav, no orbit main).
- 2026-07-07 | Web product UI | Tarot + Compatibility v2 aligned to Profile reference | IN PROGRESS | `productPageLayout` domain blocks (tarot spreads, compat mode/pair); `mainWide` + `productWebContentV2`; Compatibility hub on v2 tokens.
- 2026-07-07 | Web product UI | Profile v2 as visual reference + productV2Surface tokens | IN PROGRESS | `productV2Surface.module.css` (cards, type, gaps); Practices v2 + history aligned; user chip removed from practices top bar (identity in sidebar only). Next: tracking/account shells, Today composition slot.
- 2026-07-05 | Web Today single voice | legacy TodayRitualFlow deduped | DONE | `?full=1` path uses `usesDayStorySingleVoice`: no guide overlay, no ritual POST, contract do/avoid/why/evening; shared helpers in `todayContractMapper.ts`.
- 2026-07-05 | Web Today single voice | day_story only on composition surface | DONE | Skip POST `/today/narrative` when `contract.day_story`; no guide/spheres/evening overlay; dashboard chrome from day_story; `usesDayStorySingleVoice` policy + tests.
- 2026-07-05 | Phase 2 client parity | Web Profile/Tarot + iOS composition + Android ritual | DONE | Web: Quick Map reads `profile_contract_v1`; Tarot result reads `tarot_answer_v1`; Today story/spine from `contract.day_story` (`todayContractMapper.ts`). iOS: `TodayCompositionSurfaceView` default. Android: `TodayCompositionScreen` + `DayEngagementStore` + spine FSM ritual flow.
- 2026-07-05 | Phase 2 contracts | profile_contract_v1 + tarot_answer_v1 + mobile contract parity | DONE | Profile: `profile_contract_v1.py` replaces monolith interpreter path in `CoreProfileService` (legacy `interpretation` shim); Tarot: `tarot_answer_v1` in `POST /tarot/spread/context`; Today: `day_story` on `GET /today/contract`; iOS: `TodayContractV1` fetch + ritual hero from contract; Android: `GET today/contract` + `TodayContractScreen` tab; pytest `test_phase2_contracts_v1.py`.
- 2026-07-05 | Backend / PIM | DE-5 behavioral signals v0.1 (post-validation) | DONE | `meaning_surface_patterns_v0`: proximity (`sphere_feedback`), guidance_ask, practices, tarot_deepen → `DayContext.behavior_patterns`, CUM `behavioral_patterns` + `current_state.ritual_proximity_*`, derived knowledge hypotheses; pytest extended.
- 2026-07-05 | Backend / AMLL | Today narrative AMLL Gate v1 wired | DONE | `today_narrative_llm_gate_v1`: cache_hit/reuse/template/call_llm/blocked; `build_today_narrative` logs `amll_gate` + `gate_decision`; skip LLM on template; orchestration trace; pytest `test_today_narrative_llm_gate_v1.py`.
- 2026-07-05 | Backend / PIM | DE-5 v0.2 P1: honest_step + day_promise + guidance themes | DONE | `top_honest_step_ids`, `day_promise_sets`, `top_guidance_lanes`/`top_guidance_themes` (keyword semantic, no LLM); CUM `active_themes` merges head_topic + guidance; `current_state.honest_step_id`; `behavioral_patterns.works` day_promise≥2 / honest_step≥2; derived hypotheses; `learning_slim.today_surface_patterns` expanded; pattern gate threshold → KASP default ≥3/14d (product TBD).
- 2026-07-03 | Backend | GE-1 v0.4: Guidance + Compatibility facades | DONE | `run_guidance_answer_pipeline`, `run_compatibility_dynamics_pipeline`; orchestration в guidance/compatibility logs; `funnel_step_handoffs`, `semantic_quality` trace; `api/questions.py`, `api/compatibility.py`; pytest `test_generation_orchestrator.py`.
- 2026-07-03 | Backend Today | GE-1 v0.3: orchestration ↔ DE-13 funnel | DONE | `ORCHESTRATOR_VERSION` 0.4.0; `reasoning_trace.day_model`; `attach_narrative_outcome_to_orchestration` (funnel/monolith, child chain); guide merge_pass plan funnel + `guide_contract_v2`; pytest `test_generation_orchestrator.py`.
- 2026-07-03 | Web + Backend | Tarot result: question-first reading (не энциклопедия) | DONE | `tarot_reading_synthesis.py`; result surface: главный ответ → история → 3 инсайта → 1 шаг сегодня → follow-up chips; RU-only copy; event `tarot_reading_follow_up`; убраны spread line / card list / resonance ○○○ на `/tarot/result`.
- 2026-07-03 | Backend | Tarot synthesis: insight bundles (не биты карт) | DONE | Ответ на вопрос; единая история; конкретные инсайты; мудрый собеседник; chips «Что сейчас кажется самым важным?».
- 2026-07-02 | iOS | Tarot Question-First funnel + ritual v2 | DONE | `TarotQuestionFlowCanon`, `TarotQuestionFlowView`, `TarotSpreadRitualView`; events `tarot_session_started`…`tarot_reading_resonance`; `/tarot` fullScreenCover.
- 2026-07-02 | Web + iOS | Tarot Phase C: journey + Today deepen bridge | DONE | `tarotJourneyStore`, `/tarot/journey`, anchor в ritual, CTA «Исследовать глубже» (Today + card-of-day), `tarot_deepen_started`; iOS: `TarotHubView` по `/tarot`, reading v2 DTO.
- 2026-07-02 | Web + Backend | Tarot Phase B: synthesis contract + resonance + routes | DONE | `TarotSpreadReading` + `generation_log_id`; result surface: why / 3 today / self-Q / ○○○ / Today·goal·practice; events `tarot_reading_resonance`, `tarot_spread_done`, `first_synthesis_viewed`.
- 2026-07-02 | Product + Web | Tarot Question-First canon §6.4–§6.8 + Phase A funnel | DONE | `SCREEN_CONTRACTS_V1`; `tarotQuestionFlowCanon.ts`, `TarotQuestionFlow`, `/tarot/spread/[spreadId]`; events `tarot_session_started`, `tarot_question_domain_selected`, `tarot_question_refined`, `tarot_spread_selected`, `tarot_question_submitted`.
- 2026-02-15 | Product | Created unified execution tracker | DONE | This file initialized as canonical plan.
- 2026-02-15 | Backend | Added Core Profile Engine service | DONE | New service assembles natal + numerology + baseline context.
- 2026-02-15 | Backend API | Added `/account/core-profile` endpoint | DONE | Unified profile contract now available for UI and other modules.
- 2026-02-15 | Frontend Today | Connected core profile contract to `/today` | DONE | Added "Ядро профиля" card and missing-fields visibility.
- 2026-02-15 | Backend Day Flow | Added interpretation orchestrator baseline | DONE | `day-flow` now returns consistency block built from core profile + day context.
- 2026-02-15 | Backend APIs | Refactored key personalization endpoints to core context | DONE | `today`, `morning-ritual`, `numerology/daily/explain` now include unified profile/consistency payload.
- 2026-02-15 | Backend Tests | Added integration consistency suite | DONE | New tests in `backend/tests/integration/test_core_profile_consistency.py` (execution pending env with pytest).
- 2026-02-15 | Frontend IA | Normalized top navigation to 5 sections | DONE | Primary nav now: Today, Profile, Forecast, Tarot&Guidance, Growth.
- 2026-02-15 | Frontend Routing | Added IA hub aliases | DONE | Added `/profile`, `/forecast`, `/guidance`, `/growth` redirects to existing module roots.
- 2026-02-15 | Frontend IA | Synced footer navigation with 5-section model | DONE | Footer now reinforces same top-level IA instead of old fragmented links.
- 2026-02-15 | Frontend PWA | Disabled SW registration for localhost | DONE | Prevents local RSC route conflicts/flicker during testing in production-mode localhost.
- 2026-02-15 | Frontend Routing | Updated legacy `/app` redirect | DONE | `/app` now routes directly to `/today` instead of heavy dashboard hop.
- 2026-02-15 | Frontend Today | Added return-cadence CTA block | DONE | New "Ритм возврата" section guides morning/day/evening return behavior.
- 2026-02-15 | Frontend Today | Removed legacy duplicate sections and stale anchors | DONE | Removed "Маршрут дня", refreshed stale labels/copies, replaced hash anchors with `?slot=` routing.
- 2026-02-15 | Frontend Routing | Migrated old Today anchor links across modules | DONE | Updated key links in numerology/natal flows and ritual redirects to slot-based navigation.
- 2026-02-15 | Frontend Today | Applied visual cohesion pass | DONE | Added atmospheric canvas background, unified chip style, and standardized Morning/Day/Evening panel design.
- 2026-02-15 | Frontend Forecast | Built unified forecast workspace with filters | DONE | Added domain/date filters + personalized overlay from `core_profile` and `day-flow` consistency.
- 2026-02-15 | Backend Compatibility | Added deterministic sign-to-sign endpoint | DONE | New `/compatibility/signs` returns static report, score, free/paid text depth, and optional personalized overlay.
- 2026-02-15 | Frontend Compatibility | Connected signs result to backend API | DONE | Removed placeholder result and now render static matrix + personalized layer + paywall depth logic.
- 2026-02-15 | Backend Tarot | Added spread context endpoint | DONE | New `/tarot/spread/context` returns spread + `core_profile` + `consistency`.
- 2026-02-15 | Frontend Tarot | Connected one-card spread to shared context | DONE | `one-card` now consumes `/tarot/spread/context` and shows aligned focus/do/avoid guidance.
- 2026-02-15 | Backend Today | Added rewards snapshot to `/today` | DONE | Added rewards domain payload: streaks (daily/weekly/habit/ascetic/tarot), archetype level, seals, scores, evolution index, milestones.
- 2026-02-15 | Frontend Today | Switched rewards card to backend domain model | DONE | `/today` now renders archetype/evolution/seals/milestones from backend rewards payload instead of local-only reward mock.
- 2026-02-15 | Frontend Profile | Replaced `/profile` redirect with profile hub | DONE | New profile page now shows core profile summary + rewards contour (archetype, evolution index, streaks, seals, milestones).
- 2026-02-15 | Frontend Practices | Added rewards feedback on completion | DONE | Practice completion screen now loads `/today` rewards snapshot and shows post-completion archetype/evolution/streak/milestone reinforcement.
- 2026-02-15 | Frontend Design System | Added shared rewards DTO + reusable contour component | DONE | Introduced `src/lib/rewards.ts` and `src/components/rewards/RewardsContourCard.tsx` to remove duplicated reward UI logic.
- 2026-02-15 | Frontend Design System | Locked reward visual tokens in global theme | DONE | Added reward-specific tokens in `globals.css` (`--orbit-reward-*`) and shared card surface class for consistent rendering.
- 2026-02-15 | Frontend Today/Profile/Practices | Unified rewards presentation layer | DONE | `/today`, `/profile`, and `/practices/[id]` now render a common rewards component for consistent look and behavior.
- 2026-02-15 | Frontend Design System | Added unified glyph + tarot cover primitives | DONE | Added `SectionGlyph` and `TarotCover` components and applied them to `/today`, `/tarot`, and `/tarot/spread/one-card`.
- 2026-02-15 | Performance Today | Removed duplicated heavy API calls from `/today` | DONE | Frontend no longer performs extra `/morning-ritual/today` and `/account/core-profile` calls after loading `/today`; consumes payload from `/today` response directly.
- 2026-02-15 | Backend Morning Flow | Added fast path for morning ritual in daily cycle | DONE | `/today` now requests `get_morning_ritual(..., fast_mode=True)` to avoid expensive AI generation on page-open while preserving core guidance.
- 2026-02-15 | Backend Day Flow | Enabled lightweight mode by default | DONE | `GET /day-flow` now defaults to `fast=true`, using editorial affirmations instead of per-request AI generation for UI overlays.
- 2026-02-15 | Backend Core Profile | Added in-process TTL cache for stable core payload | DONE | `CoreProfileService` now caches built profile payload by user/profile fingerprint to reduce repeated recomputation and stabilize response latency.
- 2026-02-15 | Backend Quality Gate | Strengthened semantic checks for daily forecasts | DONE | `quality_gate` now rejects template/dead phrasing, duplicate lines, low-information blocks, and micro-actions without explicit action verbs.
- 2026-02-15 | Backend AI Generation | Added semantic validation + grounded fallback blocks | DONE | `ai_client` now validates LLM output for meaning/actionability and replaces weak output with context-aware fallback text.
- 2026-02-15 | Backend Personal Texts | Hardened affirmations/tarot/numerology content quality | DONE | Added anti-template prompt constraints, output sanitization, and meaningful deterministic fallbacks in explainers/generator.
- 2026-02-15 | Backend Morning Ritual | Added quality validation for daily recommendations payload | DONE | LLM recommendations now pass semantic checks before response; invalid payloads use practical fallback.
- 2026-02-15 | Backend Tests | Added text quality regression tests | DONE | New tests in `backend/tests/test_text_quality.py` cover dead-pattern rejection, action checks, and duplicate-line blocking in forecast gate.
- 2026-02-15 | Backend Core Profile | Added persistent core profile snapshots in DB | DONE | New `core_profile_snapshots` storage (migration + model) and `CoreProfileService` now reuses frozen payload by `user_id + profile_hash`, rebuilding only on input changes.
- 2026-02-15 | Backend Core Setup | Added atomic core setup endpoint | DONE | New `POST /account/core-setup` updates name + primary astro profile, invalidates natal cache for changed profile, computes/saves numerology, and returns refreshed `core_profile`.
- 2026-02-15 | Frontend Dashboard | Fixed numerology name source | DONE | `useDashboardData` now uses real user name from `/account/profile` for `/numerology/name` instead of `AstroProfile.label`, preventing wrong core numerology.
- 2026-02-15 | Frontend Profile | Added unified core setup form | DONE | `/profile` now includes a single "Настройка ядра" form bound to `POST /account/core-setup` and redirects to `/today` after successful save without extra hydration calls.
- 2026-02-15 | Frontend Calendar | Fixed broken JSX in month layout | DONE | Restored valid `div/aside` structure in `/calendar` month view; resolved lint/build failures and return route to green build state.
- 2026-02-15 | Frontend Calendar | Added interactive selected-day side panel | DONE | `/calendar` month view now supports date selection with actionable side panel (events, notes, cycle, tracker) instead of passive cells only.
- 2026-02-15 | Frontend Tracking Calendar | Replaced static streak visuals with progress mechanics | DONE | Added per-activity progress rings (completion %), streak milestone progress (7/21/40/90/180/365), and “days to next milestone” indicators.
- 2026-02-15 | Frontend Calendar UX | Closed dead controls on `/calendar` | DONE | Added real content for `day` and `week` modes so mode buttons no longer switch to empty states.
- 2026-02-15 | Frontend Calendar Routing | Connected day deep-link between calendar pages | DONE | `/tracking/calendar` now reads `?date=YYYY-MM-DD` and focuses selected/current date from organizer deeplink.
- 2026-02-15 | Frontend Routing Audit | Closed unresolved route links across app | DONE | Added alias pages for `/login`, `/signup`, `/account/subscription`, `/journal/all`; added legal pages `/terms`, `/privacy`; fixed subscription links in billing success.
- 2026-02-15 | Frontend Today UX | Fixed no-op CTA behavior in daily engine | DONE | `Today` slot actions now open sections directly (morning/day/evening), next-action CTA handles slot navigation interactively, morning refresh has visible loading state, and card-of-day has explicit open actions.
- 2026-02-15 | Frontend Auth Redirects | Preserved query context through auth aliases | DONE | `/login` and `/signup` aliases now forward all query params to `/auth` (including `redirect`) instead of dropping user context.
- 2026-02-15 | Frontend Billing Flow | Fixed malformed unauth redirect URL | DONE | `/billing/success` now encodes `redirect` + optional `session_id` correctly when sending user to login flow.
- 2026-02-15 | Frontend Checkout Flow | Fixed redirect parameter encoding | DONE | `/checkout` now encodes redirect target when routing unauth users to signup/login path.
- 2026-02-15 | Frontend Auth Flow | Enabled return-to-origin after login/signup | DONE | `/auth` now reads and validates `redirect` query and navigates users back to the originating route after successful auth instead of always forcing `/today`.
- 2026-02-15 | Frontend Checkout UX | Removed blocking stub alert flow | DONE | Replaced checkout `alert` no-op with explicit redirect to `/pricing?notice=checkout_unavailable` and added visible explanatory banner on pricing page.
- 2026-02-15 | Frontend Tarot | Removed mock draw logic from three-card spread | DONE | `/tarot/spread/three-cards` now uses real `/tarot/spread/context` response, including aligned focus/do/avoid consistency block.
- 2026-02-15 | Frontend Tarot | Removed mock result generator | DONE | `/tarot/result` now builds result from live `/tarot/spread/context` using `spread` param instead of synthetic card placeholders.
- 2026-02-15 | Frontend Stability | Hardened array handling on critical pages | DONE | Added normalization guards for API arrays in `/today`, `/reports/thematic/[theme]`, and `/account/compatibility` to prevent `.find is not a function` runtime crashes on malformed payloads.
- 2026-02-15 | Frontend Compatibility | Removed mock delay and connected birthdate result to live sign matrix | DONE | `/compatibility/birthdates/result` now derives zodiac signs from dates and calls `/compatibility/signs`; removed synthetic timeout payload.
- 2026-02-15 | Frontend Lunar | Connected lunar page to real celestial endpoint | DONE | `/lunar/today` now reads live `/celestial/moon-phase` data (current phase, themes, guidance, next phase) instead of placeholder response.
- 2026-02-15 | Frontend Horoscope | Removed synthetic network delay on sign page | DONE | `/horoscope/today/[sign]` now renders deterministic sign-specific guidance immediately without artificial `setTimeout` loading.
- 2026-02-15 | Frontend Assets | Patched missing local image placeholders | DONE | Added `/images/Diary.png`, `/images/journal.png`, `/images/self-discovery.png` to prevent Next Image 400 errors from broken local sources.
- 2026-02-15 | Frontend Numerology | Replaced generic result mock with endpoint-backed logic | DONE | `/numerology/result` now resolves by `type` via real numerology endpoints (`/life-path`, `/name`, `/daily`, `/personal-year`) and removed timeout mock.
- 2026-02-15 | Frontend UX Consistency | Replaced blocking alerts with toast feedback across modules | DONE | Removed `alert(...)` from `today`, `dashboard`, `calendar`, `tracking/*`, `journal`, `cycle`, `habits`, `challenges`, `generate/forecast`, and tarot share flows; unified error/info/success feedback via `ToastProvider`.
- 2026-03-25 | Product Canon | Fixed core product model | DONE | Added `CORE_PRODUCT_CANON.md`: TodayFlow is the brand, `Profile` is the personal map, `Today` is the daily guide, separate services exist around the core profile.
- 2026-03-25 | Product Direction | Deprecated legacy gate-first text philosophy | DONE | Tracker now records that API interpretation is the primary text source; `quality_gate` remains safety-only, not meaning-shaping.
- 2026-03-25 | Frontend Profile | Rebuilt `/profile` as the single core-profile flow | DONE | `/profile` now handles guided setup, build state, and stable ready-state in one mobile-first screen; `/onboarding/core` reduced to redirect.
- 2026-03-25 | Frontend Today | Reduced first-screen overload and removed phase locks | DONE | `Today` now opens with essential daily guidance, keeps `Утро / День / Вечер` as optional sections, and no longer blocks later phases behind completion gates.
- 2026-03-25 | Frontend Today | Promoted card of day to a central daily object | DONE | `Today` now treats the tarot card as a primary interactive entry point instead of a secondary info tile.
- 2026-03-25 | Frontend Tarot | Rebuilt `/dashboard/card-of-day` into a mobile-first daily reading screen | DONE | New flow centers on the card, today meaning, 3 concrete actions, expandable interpretation, support practice/affirmation, and clean return routes to `/today` and `/tarot`.
- 2026-03-25 | Frontend Profiles | Rebuilt `/account/profiles` into profile-circle management | DONE | Page now supports fast creation of additional people profiles, clear primary-profile logic, and direct compatibility entry without routing users through legacy account flows.
- 2026-03-25 | Frontend Compatibility | Rebuilt `/compatibility` into a guided pair-selection flow | DONE | Compatibility now reads ready-made profiles, supports deep-linked pair preselection, gives a cleaner result surface, and aligns with mobile-first product flow.
- 2026-03-25 | Frontend Natal Chart | Rebuilt `/natal-chart` as a permanent profile-core screen | DONE | Removed daily-noise blocks, connected core-profile metrics, centered the page around personal map, life areas, personal planets, and aspects in a cleaner layered structure.
- 2026-03-25 | Frontend Profile | Turned `/profile` into the central system hub | DONE | Added explicit service navigation from profile to Today, full natal chart, compatibility, and related profiles while preserving core setup and stable personal summary.
- 2026-03-25 | Frontend Routing | Continued legacy route cleanup across secondary surfaces | DONE | Replaced stale `/app`, `/birth-chart`, `/dashboard/daily`, `/dashboard/explore`, and `/dashboard/birth-chart` links in account, weekly, horoscope, lunar, catalog, billing, compatibility, tarot-detail, dashboard helpers, discover helpers, and home preview components with canonical routes like `/today`, `/profile`, `/profile?setup=core`, `/natal-chart`, `/catalog`, and `/compatibility`.
- 2026-03-25 | Backend Geocode | Added bilingual city suggestions | DONE | Added `/astro/geocode/suggest` and extended geocoder dataset with RU/EN city labels for guided place entry and autofill.
- 2026-03-25 | Frontend Profile | Added city autocomplete and stronger life-map framing | DONE | `/profile` now supports RU/EN city search with coordinates capture and includes clearer “who you are” and life-area sections so the screen feels like a personal map rather than a bare form.
- 2026-03-25 | Frontend Header | Reworked mobile navigation into sheet menu | DONE | Replaced brittle disappearing mobile nav with a stable grouped sheet that keeps main sections, quick access, and tracking routes reachable on phone.
- 2026-03-25 | Frontend Forecasts | Reframed `/forecasts` as guided daily interpretation | DONE | Removed the unclear old “period tape” feeling and rebuilt the page around steps: choose date, choose sphere, understand meaning, take the next action, then branch into Today, horoscopes, profile, tarot, and compatibility.
- 2026-03-25 | Frontend Profile | Added stronger interpretation and next-step guidance | DONE | `/profile` now explains strengths, cautions, life areas, and gives direct next moves into Today, horoscopes, and compatibility so it feels like a life map rather than a static data sheet.
- 2026-03-25 | Frontend Today | Added guided exits from daily engine | DONE | `Today` now gives clearer “where to go next” routes into forecasts, horoscopes, and compatibility, reducing the feeling of isolated blocks and helping the system lead the user through the product.
- 2026-03-25 | Frontend Discover | Removed duplicate “second center” behavior from `/discover` | DONE | Root `/discover` is now a lightweight orientation hub with direct exits into profile, natal chart, forecasts, compatibility, and dominant pattern pages instead of duplicating the profile/natal-map center.
- 2026-03-25 | Frontend Forecasts | Rebuilt `/forecasts` as a guided decision screen | DONE | Forecasts now follow a single mobile-first flow: choose date, choose life layer, read the meaning, then move into the one relevant next service instead of scanning a heavy ribbon of cards.
- 2026-03-25 | Frontend Profile | Strengthened `/profile` as a life-map surface | DONE | Profile now includes a practical “my life map” layer around houses 1/4/7/10 plus a clearer “how to use this map” section so the page feels like a personal guide, not a data container.
- 2026-03-25 | Frontend Today | Reduced CTA noise and rewrote key daily microcopy | DONE | `Today` now prioritizes one main daily route, cleaner action wording, and more human guidance in the hero and morning blocks instead of equal-weight buttons and template-like phrases.
- 2026-03-25 | Frontend Forecast Detail | Rebuilt `/forecasts/[date]` into a clear read-and-act screen | DONE | The detailed forecast page now follows the same guided structure as the list screen: meaning of the day, personal lens, one next step, and secondary materials hidden below instead of a long technical wall of content.
- 2026-03-25 | Frontend Compatibility | Rebuilt `/compatibility` into a quick pair-selection flow | DONE | Compatibility now starts from a simple “me + someone from my circle” guided setup, offers quick person shortcuts, reduces form weight, and frames the result as one clear relationship reading instead of a heavy setup screen.
- 2026-03-26 | Backend Forecasts | Fixed and strengthened monthly AI forecast assembly | DONE | `/reports/monthly-forecast` now uses the same humanized AI merge logic as other daily forecast surfaces, inserts theme/notice into psychological insights, deduplicates actions, and no longer relies on the broken `day_offset` branch inside the AI loop.
- 2026-03-26 | Frontend Tarot | Turned `/tarot/result` into a guided interpretation screen | DONE | Tarot result now uses live `core_profile` and `consistency` context from `/tarot/spread/context` to show the main meaning, how it manifests, caution, personal lens, and one clear next step instead of a plain list of card values.
- 2026-03-26 | Frontend Tarot Flow | Unified tarot spread entry with the canonical result journey | DONE | `/tarot/spread/one-card` and `/tarot/spread/three-cards` now act as clean question-entry screens that route into one shared guided result experience, preserve the asked question in `/tarot/result`, and use the canonical `/tarot/card-of-the-day` path instead of sending users back into legacy dashboard routing.
- 2026-03-26 | Frontend Tarot Routing | Made `/tarot/card-of-the-day` the real primary screen | DONE | The card-of-day UI now lives behind the canonical tarot route, the old `/dashboard/card-of-day` path only redirects there as a legacy alias, and the screen itself was extracted into a shared tarot component so product routing matches the current IA.
- 2026-03-26 | Frontend CTA Cleanup | Removed remaining live `/dashboard` root CTA drift from key screens | DONE | Full report upsell now routes to pricing, report history opens `lite` into profile and general “back/home/day connection” CTAs now lead to `Today` or `Profile` instead of the old dashboard root on reports, thematic reports, pattern pages, pricing, and tarot day-connection entry points.
- 2026-03-26 | Frontend Weekly Routing | Introduced `/weekly` as the new live weekly entry route | DONE | Main weekly navigation from `Today`, auth nav, and service discovery now points to `/weekly` instead of `/dashboard/weekly`, reducing legacy IA language in the active user flow while keeping the existing weekly screen behavior intact.
- 2026-03-26 | Frontend Weekly Alias | Made `/weekly` the real primary weekly screen route | DONE | The weekly screen now renders through a shared component at the canonical `/weekly` path, while `/dashboard/weekly` has been reduced to a legacy redirect alias in the same pattern as other cleaned routes.
- 2026-03-26 | Frontend Weekly UX | Rewrote weekly screen labels into the current product language | DONE | The weekly surface now presents itself as `Недельный фокус` instead of an old dashboard subpage, with cleaner auth/loading/empty copy, renamed transit and planetary sections, clearer next-route navigation, and less legacy dashboard vocabulary in the visible UI.
- 2026-03-26 | Frontend Weekly Integration | Moved weekly integration into the same canonical weekly axis | DONE | The weekly integration screen now lives at `/weekly/integration`, is reachable from the main weekly focus surface, and the old `/tracking/weekly` route has been reduced to a legacy redirect alias so weekly meaning no longer competes across separate roots.
- 2026-03-26 | Frontend Copy Cleanup | Removed another small batch of live dashboard wording from canonical UI | DONE | `Systems` now routes current cycles into `Today`, the catalog hero no longer invites users into an old dashboard concept, the weekly feature copy was renamed to `Weekly Focus`, and cross-section helper semantics were updated from an internal `dashboard` bucket to a `today` bucket.
- 2026-03-26 | Frontend Catalog Copy | Reframed product-detail catalog copy around the current IA | DONE | Catalog product pages no longer describe the system through `Lite / Dashboard / Full`; they now explain services through the real product flow of `Profile`, `Today`, weekly focus, and deeper services, while keeping the same structure and CTAs.
- 2026-03-26 | Frontend Catalog Language | Removed remaining internal orbit vocabulary from product detail screens | DONE | Catalog product pages now present themselves in direct product language instead of internal `Orbit` / `Orientation Rail` terminology, with Russian-first headings, clearer route labels, and simpler explanations of how services fit into the main TodayFlow flow.
- 2026-03-26 | Frontend Catalog Hero | Removed the remaining imported/foreign framing from catalog entry screens | DONE | Catalog index and product metadata no longer describe the experience through `Astro.com matrix`, `best-in-orbit`, or English intake/meta phrasing; they now present the catalog as a direct TodayFlow service map with Russian-first entry language.
- 2026-03-26 | Frontend Catalog Categories | Rewrote category-page fallback copy into product language | DONE | Catalog category screens for free, forecasts, personality, relationships, authors, education, shop, subscriptions, and tools no longer fall back to English placeholders; they now keep readable Russian-first hero, recommendation, and aside copy even when translation keys are missing.
- 2026-03-26 | Frontend Catalog I18n | Rewrote active catalog localization keys into canonical product language | DONE | The live `catalog.*` translations in `app.en.json` and `app.ru.json` no longer override screens with `Orbit / Dashboard / Lite+ / Astro.com matrix` framing on the main catalog, category pages, or shared product-detail sections; they now speak through `TodayFlow`, `Profile`, `Today`, weekly focus, and clear service-task language.
- 2026-03-26 | Frontend Catalog Product I18n | Continued removing legacy framing from deeper product-detail translations | DONE | Additional hidden `catalog.products.*` translation keys for forecasts, psychology, star stories, and numerology no longer describe services through `Orbit`, `Dashboard`, `Loop`, or `Lite+` framing where those products now belong to the canonical TodayFlow IA.
- 2026-03-26 | Frontend Catalog Tail I18n | Removed the remaining legacy catalog language from deep product and category translations | DONE | The remaining hidden `catalog.products.*`, category hero, and catalog CTA keys in `app.en.json` and `app.ru.json` no longer leak `Orbit`, `Lite+`, `Dashboard`, `portal`, or imported product framing into live catalog surfaces; they now describe services through direct TodayFlow product language.
- 2026-03-26 | Frontend Horoscopes | Filled month/year screens with readable period guidance | DONE | `/horoscopes` now renders monthly/yearly payloads as real interpretation surfaces with lead meaning, main themes, focus areas, and supporting recommendations instead of sparse generic blocks.
- 2026-03-26 | Backend Period Texts | Humanized yearly and period descriptions at source | DONE | `personal_transits` now returns readable period descriptions, humanized focus areas, stronger yearly recommendations, richer monthly overview summaries, and cleaner lunar window text instead of generic service-level English placeholders.
- 2026-03-26 | Backend Compatibility Texts | Rewrote relationship summaries and recommendations in human tone | DONE | `synastry` and `psych_compatibility` now produce readable Russian-first strengths, triggers, communication techniques, closeness/boundary advice, and practical relationship rules instead of generic English template phrases.
- 2026-03-26 | Backend Today Texts | Strengthened fast and cached daily meaning assembly | DONE | `morning_ritual` now builds daily summary and focus from actual forecast meaning instead of raw tension fields, and its fast/fallback daily guidance texts are more concrete, supportive, and readable.
- 2026-03-26 | Product Direction | Switched canonical product framing to JTBD-first | DONE | `CORE_PRODUCT_CANON.md` and this tracker now define the main product truth as 5 core user jobs, implicit JTBD routing across the main product surfaces, and dedicated JTBD packs for love, money/career, decisions, patterns, state, and daily guidance.
- 2026-03-26 | Product Backlog | Expanded canonical execution backlog from current-state audit | DONE | Added grouped backlog for critical product, core/profile, today, forecasts, compatibility, tarot, text pipeline, UX, mobile, design, data, performance, and QA so all remaining work now lives in one working tracker.
- 2026-03-26 | Frontend JTBD Entry | Moved question-first routing into the main product surfaces | DONE | Added a shared question-entry layer and embedded it into `/today`, `/profile`, and `/questions`, so JTBD routing now lives inside the core product journey instead of existing only as an isolated separate page.
- 2026-03-26 | Frontend Decision OS | Moved decision routing into the main product surfaces | DONE | Extracted a shared `Decision OS` entry layer and embedded it into `/today`, `/profile`, and `/questions/decision`, so concrete choice-making now lives inside the main product journey instead of only as a separate isolated screen.
- 2026-03-26 | Frontend Love and Career OS | Added explicit relationship and money-career lane entries | DONE | Added dedicated `Love OS` and `Money / Career OS` entry surfaces plus lane-pinned question routing, and embedded both lanes into `/today` and `/profile` so the strongest JTBD paths are now explicit inside the core journey instead of hidden behind generic questions.
- 2026-03-26 | Frontend State and Pattern OS | Added explicit stabilization and recurring-pattern lane entries | DONE | Added dedicated `State OS` and `Pattern OS` entry surfaces and embedded both lanes into `/today` and `/profile`, so overload/stabilization and repeating-scenario questions now have explicit routes inside the main product journey instead of living only in generic question routing.
- 2026-03-26 | JTBD Learning Signals | Started logging real downstream route openings from question flows | DONE | `Question` and `Decision OS` result CTAs now send `route_opened` feedback with lane, source surface, and chosen route metadata before navigation, so the learning layer can see not just the inferred JTBD answer but which deeper route the user actually opened next.
- 2026-03-26 | JTBD Answer Feedback | Added direct helpfulness signals to question and decision answers | DONE | `Question` and `Decision OS` results now let the user mark the answer as helpful or still unclear, and those explicit quality signals are logged into the learning layer with lane and surface metadata instead of only tracking route openings.
- 2026-03-26 | JTBD Route Completion | Started logging actual arrival on destination surfaces after JTBD CTA | DONE | JTBD result CTAs now append a lightweight arrival marker, and a shared app-level route logger records `route_completed` plus cleans the URL on arrival, so the learning layer can distinguish between a clicked CTA and a completed transition into the deeper surface.
- 2026-03-26 | JTBD Downstream Completion | Started logging first real actions on destination surfaces | DONE | After JTBD arrival, the active JTBD context now persists in session storage and real downstream actions like compatibility calculation, practice direction selection, morning intention save, and profile core setup completion are logged back into the learning layer instead of stopping at route arrival.
- 2026-03-26 | JTBD Destination Adaptation | Started adapting destination surfaces from active JTBD context | DONE | `compatibility` and `practices` now read the active JTBD context and preselect the first meaningful state for the destination surface, so the user arrives not just on the right route but closer to the right mode, goal, and direction for the original lane.
- 2026-03-26 | Daily Horoscope Prism | Rebuilt `Today` around profile-based horoscope scenarios | DONE | `morning_ritual` now returns a structured `daily_horoscope` block with a headline, a profile-prism narrative, and separate life scenarios for general, love, family, career, and money; `/today` renders those scenarios as a visible daily-horoscope layer so the day is read through the user profile instead of only through one generic summary.
- 2026-03-26 | Profile Daily Lenses | Turned core profile into the permanent source of daily scenario lenses | DONE | `core_profile.interpretation` now includes stable `daily_lenses` for general, love, family, career, and money, `Profile` renders them as an explicit “how your day usually unfolds” layer, and the daily-horoscope prompt now uses those lenses so `Today` is generated from the profile’s lasting logic instead of only from one-day context.
- 2026-03-26 | Daily Scenario Routing | Connected daily horoscope scenarios to the right next product action | DONE | The scenario cards in `/today` now route love and family into `compatibility`, career and money into the dedicated money-career lane, and the general scenario back into the profile foundation; those scenario CTA clicks are also logged as `daily_horoscope_scenario_opened` so the system can learn which daily line actually turns into the next user move.
- 2026-03-26 | Daily Foundation Framing | Reframed the daily layer from horoscope language to day-foundation language | DONE | The generation prompt for the daily scenario block now explicitly asks for a personal “day spine” built on top of the profile base rather than a horoscope, and `/today` presents that block as `Daily Foundation` / `Стержень дня через базу профиля`, making the product read as a daily support system built from life-profile foundations instead of a horoscope feature.
- 2026-03-26 | Daily Spine Structure | Added an explicit backbone schema for the day foundation | DONE | The daily foundation contract now includes a structured `spine` with `day_axis`, `main_risk`, `best_mode`, `first_move`, and `do_not_enter`, and `/today` surfaces those fields as the first visible layer before scenario cards so the day is built from an explicit support model rather than only from narrative text.
- 2026-03-26 | Semi-Deterministic Day Spine | Anchored the daily backbone to system signals before AI phrasing | DONE | The `spine` layer in `morning_ritual` is now first composed from deterministic product signals like `consistency.focus`, `consistency.do_focus`, `consistency.avoid_focus`, daily summary, recommendation focus, and profile baseline, then passed into the model as a fixed system backbone and merged back on response so the day support layer depends less on free-form generation and more on the actual product state.
- 2026-03-26 | Daily Spine Next Action | Turned the day backbone into an executable next move | DONE | The daily `spine` now includes a structured `next_action` with route, label, and kind derived from deterministic day focus and tone, and `/today` renders that action as a primary CTA with click logging so the top-level day support block can drive the next user move directly instead of only describing it.
- 2026-03-26 | Daily Foundation Feedback Context | Added generation logging and completion context for the day foundation layer | DONE | `morning_ritual` now logs each generated daily foundation and returns `daily_horoscope_generation_log_id`, the top-level day spine CTA now carries that id through arrival params, and the shared frontend feedback context now persists daily-foundation metadata alongside JTBD so downstream completion signals can be attributed back to the actual generated day-support layer instead of existing only as unbound navigation.
- 2026-03-26 | Day Spine Route Completion | Added explicit arrival tracking for executable day-spine actions | DONE | The shared route-arrival logger now emits `day_spine_route_completed` when a top-level daily foundation action lands on its destination, carrying `day_spine_action_kind`, label, target href, and arrived path so the product can compare which generated day-backbone routes actually complete and then correlate that with the existing downstream completion signals on `compatibility`, `practices`, `profile`, and other destinations.
- 2026-03-26 | Today and Profile Stability | Removed avoidable waiting on `/today` and stabilized `/profile` state resolution | DONE | `/today` no longer enforces an artificial initial loading delay and now guards against duplicate in-flight initial loads, while `/profile` now checks real stored astro profiles in addition to `core_profile.is_ready`, so existing users are no longer incorrectly pushed into “create profile” state; the profile hero also now includes simple in-page navigation chips to make the screen’s internal route clearer.
- 2026-03-26 | Questions Surface Separation | Removed explicit question widgets from core profile and day screens | DONE | `/today` and `/profile` no longer embed `QuestionEntryCard` / `DecisionEntryCard` blocks or lane-specific question funnels; both screens now answer implicitly through their own content and only point to `/questions` as a separate explicit question tool, matching the product rule that user questions live in the person’s head while core surfaces respond through structured guidance rather than questionnaires.
- 2026-03-26 | Stored Day Layer | Started reusing saved daily texts and removed internal loading narration | DONE | `core_profile` already reads from a saved snapshot by profile hash, and now `morning_ritual` also reuses saved `daily_recommendation` and `daily_foundation` generations per user/date/profile snapshot instead of regenerating them on every open; `/today` loading states were also rewritten to neutral user-facing copy with no internal system narration.
- 2026-03-26 | Stored Compatibility Layer | Added persisted reuse for compatibility calculations with TTL | DONE | Quick `/compatibility/compare` and deep `/compatibility/synastry` results are now stored in `cached_compatibility` and reused for the same user, pair, relation mode, locale, and unchanged profiles for 7 days, so compatibility does not recompute identical pairs on every open while still invalidating naturally when profile data changes.
- 2026-03-26 | Today Screen Simplification | Removed route-hub behavior from `/today` | DONE | `/today` no longer tries to branch the user through multiple “next layer”, people-question, weekly, and question-surface hubs. The screen now stays focused on the day itself: core meaning, daily foundation, state/progress, and one real next move instead of a cluster of competing navigation exits.
- 2026-03-26 | Today Page Decomposition | Split the `/today` monolith into reusable modules | DONE | `frontend/src/app/today/page.tsx` no longer keeps section primitives, quick-action forms, and pure today-specific helper/type logic inline. These pieces now live in dedicated modules under `frontend/src/components/today`, so the route file is closer to an orchestrator and future section-level extraction can continue without editing one 3000-line file for every change.
- 2026-03-26 | Today Screen Section Extraction | Pulled the first large screen blocks out of `/today/page.tsx` | DONE | The top overview stack and the `Рабочий слой дня` are now rendered through dedicated screen-section components in `frontend/src/components/today/TodayOverviewSection.tsx` and `frontend/src/components/today/TodayWorkingLayerSection.tsx`, so the route file no longer owns all top-level presentation directly and can continue shrinking section by section.
- 2026-03-26 | Today Phase Extraction | Moved the morning, day, and evening flows out of `/today/page.tsx` | DONE | The three main phase surfaces of `/today` now live in `frontend/src/components/today/TodayMorningSection.tsx`, `frontend/src/components/today/TodayDaySection.tsx`, and `frontend/src/components/today/TodayEveningSection.tsx`, leaving the route file responsible mainly for data loading, state orchestration, and cross-section callbacks instead of owning the full UI of every day phase.
- 2026-03-26 | Profile Hero and Setup Extraction | Moved the top profile shell and core-setup flow out of `/profile/page.tsx` | DONE | The main hero entry block and the whole profile core-setup/build surface now live in `frontend/src/components/profile/ProfileHeroSection.tsx` and `frontend/src/components/profile/ProfileSetupSection.tsx`, so the route file no longer directly owns the first large product surfaces of `Profile` and can continue shrinking toward a screen-composition role.
- 2026-03-27 | Core Profile Multi-Profile Contract | Added explicit role-aware profile circle contract to account and core-profile payloads | DONE | `astro_profiles` now store `relation`, account profile APIs return normalized roles, `core_profile` now exposes `astro.relation` plus `profiles.primary/selected/items`, and account/profile-management UI lets users mark a profile as self, partner, child, or close person instead of inferring everything from labels.
- 2026-03-27 | Core Profile Contract Split | Separated stable profile map from daily profile lenses in the core payload | DONE | `core_profile.interpretation` now contains only the lasting profile map (`identity`, `strengths`, `watchouts`, `life_areas`), `daily_lenses` moved into `core_profile.daily_interpretation`, `morning_ritual` now reads daily lenses from the dedicated block, and old core-profile snapshots are migrated on read so saved payloads still work after the contract change.
- 2026-05-03 | Backend / Day Engine | DE-5: агрегаты поверхности Today из `meaning_events` | DONE | `meaning_surface_patterns.py`; `build_day_context_v0(..., behavior_patterns=…)`; `build_today_narrative` подмешивает слой в LLM (guide…deepen); `LearningService` + кэш-маркер `core_profile`; сжатый `today_surface_patterns` в `user_core.learning` для промпта.
- 2026-05-03 | Full-stack | DE-4: канонические `meaning` events + веса колец + клиенты | DONE | Backend: `VALID_EVENT_TYPES`, `RING_EVENT_WEIGHTS`; `TodayResultView` / `TodayRitualFlow` / `today/page` и iOS (`TodayRitualFlowView`, `saveEveningReflection` → `evening_reflection_submitted`); типы в `frontend/src/lib/types.ts`; pytest `test_meaning_events.py`.
- 2026-05-03 | Full-stack | DE-3: `generation_id` в событиях Today + learning feedback | DONE | Web: state для всех narrative surface, `generation_id` в meaning payload (`TodayResultView`), `POST /learning/feedback` при сигналах day_connection и сохранении вечера; iOS: `generationLogId` в `trackTodaySurfaceEvent`, `submitLearningFeedback` после `saveEveningReflection`.
- 2026-05-03 | Backend / Contracts | DE-2: DayContext перед narrative LLM | DONE | `build_today_narrative` → `build_day_context_v0` для всех surface; guide user prompt из `layers`; ленивый импорт в `day_context.py` против цикла с `today_narrative`; лог `input_payload.day_context_sha256` + `day_context_contract_version`.
- 2026-05-03 | Backend / Contracts | DayContext v0: спека, JSON Schema, CI, `build_day_context_v0` | DONE | [DAY_CONTEXT_V0.md](./DAY_CONTEXT_V0.md), `docs/schemas/day_context_v0.schema.json`, `scripts/validate_day_context_contract.py`, job `day-context-schema`; черновик сборки `backend/.../day_context.py` + pytest.
- 2026-05-03 | Product / Architecture | Day Engine зафиксирован в трекере выполнения | DONE | Канон [DAY_ENGINE_AND_COHERENCE.md](./DAY_ENGINE_AND_COHERENCE.md); в трекере добавлены §4.7 (чеклист DE-1…DE-11), §5.3 (порядок работ), приоритет §6 п.0; gap в §3 про отсутствие единого DayContext end-to-end.
- 2026-05-03 | Backend / Narrative | DayModel v0 во все LLM-pack’и narrative + лог | DONE | `day_model` и `day_engine_brief` в user JSON для **day_layer**, **spheres**, **evening**, **deepen** (`_attach_day_logic_slices`); `input_payload.day_model_contract` для всех surface при наличии слоя; промпт **today-narrative-v11** (слайсы RU/EN: day_model в п.1); pytest на day_layer user JSON и `day_model_contract` в логе.
- 2026-05-03 | Frontend | Today: общий блок опоры + логика дня; copy policy | DONE | `TodayDayLogicCallout` (ритуал + `TodayGuideSection`); лоадер ритуала — новый текст без «без воды»; `COMPATIBILITY_GENERATION_LIVE` в `lib/compatibilityDynamicsMode.ts` — убраны вхождения `llm` из сканируемых `app/components`, `userFacingCopyPolicy` зелёный.
- 2026-05-03 | Backend / API + tests | Narrative: контракт ответа guide vs LLM | DONE | `TodayNarrativeResponse` и docstring `post_today_narrative`: в HTTP-ответе `day_model`/`day_engine_brief` только у guide; pytest parametrize `day_layer`/`spheres`/`evening`/`deepen` — user JSON содержит оба слоя.
- 2026-05-03 | Full-stack | DE-6: intent в DayContext и Today narrative | DONE | `intent_slice_v0.py`, `build_day_context_v0(..., intent_slice=…)`, `DayConnection` + `head_topic` в `build_today_narrative`, `intent_context_fp` в кэше narrative, `PROMPT_VER` v7→v8; `RitualContextRequest.head_topic`, `ritual_context` для всех surface; web `lastRitualNarrativeContextRef` + `head_topic` в эффекте ритуала; iOS last-context + `head_topic` + повторный refresh при выборе темы после check-in; [DAY_CONTEXT_V0.md](./DAY_CONTEXT_V0.md) + `day_context_v0.schema.json` (`ritual.head_topic`); pytest `test_intent_slice_v0`, расширен `test_day_context_v0`.
- 2026-05-03 | Backend / Day Engine | DE-7 v0: этапы дня в fusion и slim fusion | DONE | `GET /tracking/fusion/{date}` → `activity_context.morning_completed` / `day_completed` / `evening_completed` из `DayConnection`; `_fusion_slim_for_prompt` переносит только эти три ключа для spheres/evening/deepen; [DAY_CONTEXT_V0.md](./DAY_CONTEXT_V0.md); pytest `test_tracking.py`, `test_today_narrative_contract.py`; docstring `profile_prompt_slices_v0`: DE-7 → DE-12.
- 2026-05-03 | Backend / Day Engine | DE-7 v1: выборы guide action_options в fusion | DONE | `activity_context.guide_action_options_selected_today` = count `meaning_events` (`action_option_selected`, `local_date`); slim fusion кламп 0–50; pytest `test_tracking.py::test_fusion_counts_action_option_selected_meaning_events`, расширен slim-тест в `test_today_narrative_contract.py`.
- 2026-05-03 | Backend / Day Engine | DE-7 v2: «сделано» из meaning_events в fusion | DONE | `guide_flow_signals.guide_meaning_completions_today_counts` → `activity_context.guide_meaning_completions_today` (5 типов); slim `_fusion_slim_for_prompt`; различие с `day_completed` в [DAY_CONTEXT_V0.md](./DAY_CONTEXT_V0.md); pytest `test_tracking.py` (в т.ч. `test_fusion_guide_meaning_completions_today_from_meaning_events`), `test_today_narrative_contract.py::test_fusion_slim_clamps_guide_meaning_completions_today`; iOS `FusionActivityContext.guideMeaningCompletionsToday`.
- 2026-05-03 | Backend / Day Engine | DE-8 v0: `depth_level` в narrative API и DayContext | DONE | `POST /today/narrative.depth_level` (quick/normal/deep); `DayContext.meta.depth_level`; кэш `_load_narrative_cache`; `policy.depth_level` + guide top-level; `_openai_json` max_tokens/temp; `PROMPT_VER` v12; web `todayNarrativeApi` + iOS `TodayNarrativeRequest.depth_level`; pytest кэш по depth; [DAY_CONTEXT_V0.md](./DAY_CONTEXT_V0.md), schema fixture. |
- 2026-05-03 | Backend / Day Engine | DE-9 v0: temporal slice в DayContext + LLM | DONE | `fusion_scores.py` (`build_fusion_scores_for_inputs`, `compute_fusion_scores_map_for_dates`); `history_layer_v0.build_history_layer_v0`; `build_day_context_v0(..., history_slice=…)`; `build_today_narrative` + `_attach_day_history_to_llm_pack` → `day_history`; рефактор `GET /tracking/fusion` на общую формулу scores; pytest `test_fusion_scores.py`, `test_history_layer_v0.py`, [DAY_CONTEXT_V0.md](./DAY_CONTEXT_V0.md). |
- 2026-05-04 | Full-stack | DE-8 v1: глубина narrative из профиля + клиенты без override | DONE | Миграция `today_narrative_depth_level`; `PUT account/profile` + GET; `POST /today/narrative` без `depth_level` → настройка пользователя; веб settings + iOS `AccountSettings` / `ProfileSettingsView`; iOS `fetchTodayNarrative(depthLevel: nil)` и JSON без ключа; web `todayNarrativeApi` уже без поля по умолчанию. |
- 2026-05-04 | Backend + clients | DE-8 v2: тарифный гейт для `deep` | DONE | `_clamp_narrative_depth_for_insight_tier` в `today_narrative` (free → `deep`→`normal`); `PUT account/profile` 400 для free + `deep`; веб settings: `/auth/me` + `insightDepthFromProfile`, скрытие опции; iOS `AuthSession.insightDepthTier`, `resumeSessionIfNeeded` в load настроек, picker без «Глубже» на free; pytest `test_account`, `test_today_narrative_contract`. |
- 2026-05-04 | Full-stack | DE-9 v1: `day_history` в fusion + полоска в ритуале | DONE | `FusionIndexResponse.day_history` + `build_history_layer_v0` в `get_daily_fusion_index`; типы и UI на вебе (`FusionResponse.day_history`, `TodayRitualFlow`); iOS `FusionIndex.dayHistory` + `TodayRitualFlowView`; dev preview mock; pytest `test_tracking.py::test_daily_fusion_index` проверяет контракт `day_history`. |
- 2026-05-03 | Backend / Narrative | Кэш guide по `day_context_sha256` | DONE | `build_day_context_v0` до `_load_narrative_cache`; в кэше требуется совпадение `input_payload.day_context_sha256`; при смене fusion — промах кэша и новый `generation_log`; pytest `test_guide_narrative_cache_hit_when_day_context_unchanged`, `test_guide_narrative_cache_miss_when_fusion_changes_day_context`; [DAY_CONTEXT_V0.md](./DAY_CONTEXT_V0.md).
- 2026-05-03 | Backend / Copy | Narrative: анти-абстракция + RU quality gate | DONE | `today_narrative.py`: усилены `_GUIDE_SYS` / `_SPHERES_SYS` / `_DAY_SYS`; `_guide_payload_concrete`, `_spheres_payload_concrete`, `_ru_narrative_quality_reject`; кэш guide не отдаётся при провале гейта; `temperature` 0.52; web+iOS: подписи сфер без «мы смотрим на записи», `dayMarkerMoon` переименован; pytest расширен `test_today_narrative_contract.py`.
- 2026-04-26 | Product Today UX | Зафиксирован канон ритуала и упаковки Today (web + iOS) | DONE | Добавлен §4.6: north-star входов движка, слоистая IA, information diet, progressive disclosure, тактильная палитра (песок / розовое золото), отсутствие ИИ в пользовательском тексте, паритет «Собрать день» + сферы + подсказка до чекина; iOS — горизонтальный дек карта→число→тон; бэклог: контракт narrative fusion для привычек/дневника/аскез, опциональный bento-виджет Today.
- 2026-04-26 | iOS Today | Deep link чипов «Собрать день» в Flow | DONE | `TrackerQuickCreateKind` + `pendingTrackerQuickCreate`: привычка — скролл к блоку и фокус поля; цель и аскеза — шиты; `TodayFlowStore.createAsceticContract` → `POST /tracking/ascetic-contracts`; каталог через `PracticesClient.fetchAsceticisms`; обработка intent в `onAppear`/`onChange` у `CalendarView`, чтобы сработало при переключении таба с Today.
- 2026-04-26 | iOS Goals | Паритет якорей и лимитов с веб `EntityCreateWizard` | DONE | `week_start`: понедельник недели выбранного дня (`weekStartMonday`), месяц — `monthAnchorIso`; лимит 3 цели на недельный пул и 3 на месячный (`goalSlotCounts` / `canCreateGoal`); формы быстрой цели и `GoalsView`; `createGoal` возвращает `Bool`.

---

## 8) Working Rules

- Any new feature starts as a task update in this file.
- Any completed implementation must update:
  - phase checkbox,
  - progress log,
  - current priorities (if changed).
- If priorities conflict, follow section `6) Current Priorities`.
- 2026-03-25: Пересобран прогнозный слой `/horoscopes` в формате спокойного персонального workspace вокруг ядра профиля. Убраны прямые упоминания ИИ из пользовательского текста, упрощена структура периодов `день / неделя / месяц / год`, добавлены понятные CTA между `/profile`, `/today`, `/forecasts`, `/natal-chart`. Детальный экран `/forecasts/[date]` приведен к той же продуктовой формулировке.
- 2026-03-25: Полностью пересобран `/forecasts` как единый прогнозный календарь: сильный главный блок периода, дата-чипы, доменные переключатели, спокойный персональный слой справа и более чистая лента карточек без ощущения таблицы и техфильтратора.
- 2026-03-25: Пересобран входной экран `/tarot` как единый сервис-хаб: карта дня, быстрый вопрос, глубокий расклад и связь с ядром профиля. Убран разрозненный вход в модуль, добавлены понятные сценарии использования и прямые переходы в `Today`, `Profile` и `Card of the Day`.
- 2026-03-25: Унифицированы экраны `one-card`, `three-cards` и `tarot/result` под один продуктовый сценарий. Теперь это один визуальный язык, единые CTA, более спокойные итоговые экраны и понятный переход между быстрым вопросом, глубоким раскладом и картой дня.
- 2026-03-25: Полностью упрощен `/calendar`. Убраны перегруженные режимы и модальные сценарии, оставлен один month-hub: сетка месяца, выбранный день, быстрые события, запись дня, слой цикла и слой трекеров. Экран теперь читает период сверху вниз и не ощущается как технический органайзер.
- 2026-03-25: Пересобран `/habits` в формате спокойной habit map. Убрана утилитарная “админская” подача, добавлены единый hero, мягкая heatmap-лента по каждой привычке, простой сценарий создания и ясная сводка по стрикам и completion rate.
- 2026-03-25: Пересобран `/cycle` в формат личного слоя ритма. Убраны перегруженные аналитические панели, добавлены hero, дневная фиксация, сценарий дня, короткая сводка и практики под текущее состояние. Экран теперь читается как часть `TodayFlow`, а не отдельный аналитический сервис.
- 2026-03-25: Начата зачистка legacy-навигации. Обновлены живые переходы в `NavAuthLinks`, `Footer`, account-карточках и пересобран `/tracking/progress` как новый хаб трекеров. Старые ссылки на `dashboard/daily`, `dashboard/explore`, `forecast`, `guidance`, `growth` заменяются на канонические маршруты нового продукта.
- 2026-03-27: `Profile` теперь показывает role-aware круг людей как часть канонической личной карты. На экране появился отдельный блок связей с `self / partner / child / close person`, пояснениями зачем нужен каждый профиль и прямыми переходами в `Today`, `compatibility` и `/account/profiles`, поэтому multi-profile больше не живет только в аккаунт-настройках.
- 2026-03-27: Домовой слой `Profile` доведен до практической карты жизни. Блок `Сферы жизни и дома` теперь объясняет не только значение дома, но и где тема проявляется, что усиливать, чего избегать и куда идти дальше по каждому дому, а вместе с уже собранными strengths, cautions и life areas это закрывает расширение контента профиля до канонической “life map” поверхности.
- 2026-03-27: Стабилизирован build flow на `/profile`. Вместо голого спиннера появился отдельный loading-screen, hero и setup-flow теперь живут в одной staged-логике, а после успешной сборки экран не прыгает сразу в ready-state: пользователь сначала видит явное completion-состояние с подтвержденными данными и кнопкой `Перейти к карте`, а уже потом сам переводит экран в постоянный режим профиля.
- 2026-03-27: Убран основной перегруз из средней и нижней части `/today`. `Опора дня` сокращена до одного поддерживающего решения с компактной практикой и недельным вектором вместо конкурирующих карточек и CTA, а `Ход дня` теперь просит всего одну быструю фиксацию, показывает только первые записи за день и уводит в глубину через один спокойный выход вместо набора параллельных сервисных кнопок.
- 2026-03-27: Верхний слой `/today` доведен до одной линии движения и сильнее привязан к `Profile`. На первом экране остались один главный смысл дня, карта дня, один следующий ход и одна supporting card, дублирующие CTA убраны, сценарные и практические переходы стали спокойнее, а блоки `Опора из профиля` и `Как день читается через тебя` теперь читают день через `core_profile`, а не как набор отдельных сервисов.
- 2026-03-27: Дневной язык `Today` доведен до одного product tone. В backend обновлены prompt-версии и fallback-тексты утреннего daily layer, чтобы тексты устойчивее выполняли три функции: поддержать, предупредить и сдвинуть в действие; на фронте переименованы и выровнены пользовательские формулировки вроде `Что поддержит день` / `Что не усиливать` и убраны остатки смешанного англо-сервисного словаря.
- 2026-03-27: Numerology перестала конкурировать с `Profile` как отдельный вход. `Profile` теперь поддерживает фокус `?focus=numerology` и адресует пользователя прямо в numerology-слой общей карты, numerology result/entry screens ведут обратно в этот канонический маршрут, а сохраненные numerology calculations в `/library` тоже открывают numerology уже внутри профиля, а не через отдельные result pages.
- 2026-03-27: Compatibility result surface приведен к канонической структуре смысла. Основной экран `/compatibility` теперь сначала показывает главную динамику связи, затем явно отвечает на пять продуктовых вопросов: где течет легче всего, где возникает трение, что помогает и как действовать дальше; backend `deep_dive` больше не падает в UI россыпью дублирующих карточек, а читается как один собранный relationship lens.
- 2026-03-27: `Sign compatibility` и `birthdate compatibility` приведены к одному смысловому стандарту. Их result pages теперь обе читаются через одну и ту же структуру: главная динамика связи, где течет легче, где возникает трение, что помогает и как действовать дальше; тексты и CTA больше не живут в разных product tones и естественно ведут в глубокую совместимость.
- 2026-03-28: Быстрые входы в `Compatibility` доведены до role-aware маршрутов. `Profile`, `Today` и `Круг людей` теперь не ведут в пустой общий compatibility-flow по generic ссылке, а стараются открыть уже готовую пару `me + someone from my circle`; если нужного второго профиля еще нет, продукт уводит в `/account/profiles`, чтобы сначала собрать реальный круг людей, а уже потом читать связь.
- 2026-03-28: Живой tarot-поток очищен от сервисной подачи и приведен к одной продуктовой логике. `/tarot`, `one-card`, `three-cards`, `tarot/result` и `card-of-the-day` теперь читают карты как слой смысла вокруг `Today` и `Profile`, а не как отдельный “tarot service”; хаб стал вести через центральный ежедневный ритуал, spread-entry screens заранее обещают структуру `meaning / manifestation / caution / next step`, а `card of the day` закреплена как главный tarot-вход дня.
- 2026-03-28: Tarot spreads доведены до явного смыслового контракта. `/tarot/spread/context` теперь возвращает отдельный `reading` блок с `meaning`, `manifestation`, `caution` и `next_step`, а `tarot/result` опирается уже на этот backend-ready слой вместо чисто фронтовой склейки; в итоге и одна карта, и три карты читаются в одном продуктовой формате, а не только выглядят так визуально.
- 2026-03-28: Канон уточнен: TodayFlow не делится на три самостоятельных продукта `утро / день / вечер` и не строится вокруг отдельного `future / period` сервиса. Есть один экран `Today` с мягкой временной логикой и напоминаниями, а будущее как смысловой слой допустимо только внутри `Profile`, `Compatibility`, decision-support и других вторичных интерпретаций, но не как отдельный продуктовый центр.
- 2026-03-28: `Today` дополнительно дочищен под новый канон одного дневного экрана. На живом UI убраны остатки старой фазовой модели вроде `Открываем утро`, `Закрытие дня` и `ритуал`-формулировок там, где они продолжали дробить экран на самостоятельные этапы; weekly-ориентир закреплен как внешний helper, а вечерний смысловой блок свернут в reveal, чтобы экран оставался про один текущий ход, а не про три параллельных режима дня.
- 2026-03-28: В `Today` добавлен явный reminder-layer вместо фазовой навигации. Верх экрана теперь показывает `Ритм возврата` с мягкой подсказкой, когда и за чем лучше вернуться в течение дня, а выбор раскрытого блока больше опирается на незавершенный следующий шаг пользователя, чем на жесткое деление дня по времени суток.
- 2026-03-28: Собран более цельный auth contour. `/auth` теперь держит явный `mode=login|signup`, безопасно сохраняет `redirect`, после успешного входа или регистрации определяет следующий шаг через `redirect` или готовность core-profile, алиасы `/login` и `/signup` больше не теряют намерение пользователя, recovery flow ведет обратно в единый auth entry, а в `/account/settings` добавлена отдельная смена пароля для авторизованного пользователя вместо смешивания signed-in security и recovery-сценариев.
- 2026-03-28: `Today` signals выведены в общий personalization layer. Ответы `ritual feedback`, `mini decision` и `question of day` теперь сохраняются в `DayConnection`, учитываются в `tracking/fusion/{date}` как часть живого состояния дня, а weekly/monthly state map в `/tracking/calendar` и `/calendar/unified` показывает их отдельной строкой `Сигналы дня`, чтобы накопленное понимание пользователя строилось из реальных daily inputs, а не только из трекеров и дневника.
- 2026-03-28: `Today` начал учиться на вчерашнем отклике пользователя. Decision engine в `/morning-ritual/today` теперь читает последние `daily signals` из `DayConnection` и мягко адаптирует энергию, фокус, риск, действия и ограничения на следующий день: если вчера день не собрался, усиливается режим бережности и сужения фронта; если осталась неясность, следующий день сильнее предупреждает об ошибках и поспешных решениях.
- 2026-03-28: `Daily signals` подключены и к auto-insights. Инсайты теперь умеют замечать не только completion/mood-паттерны, но и повторяющуюся собранность дня, неясность решений и доминирующий фокус из `question of day`, поэтому слой `меня видят` начинает строиться из реального daily dialogue с пользователем, а не только из сервисных трекеров.
- 2026-03-28: `Profile` получил живой evolving layer поверх стабильной карты. В `core_profile` добавлен блок `living` с summary, signal profile, weekly state и recent insights, а на `/profile` появился отдельный слой накопленного понимания пользователя: как сейчас собирается день, растет ли ясность решений, какая тема всплывает чаще всего и что уже заметила система. Профиль теперь развивается не только через натал и числа, но и через проживаемый ритм пользователя.
- 2026-03-28: Начат user-level learning context поверх learning layer. `LearningService` теперь синтезирует общий контекст из feedback, JTBD route choices, diary topics и daily signals, а `core_profile.living` включает этот слой как `learning_context`. На `/profile` появился отдельный блок о том, как системе лучше говорить с пользователем, что ему сейчас помогает и какие темы у него повторяются чаще всего. Это ещё не финальный learning LLM, но уже общий psychotype foundation для web и iOS.
- 2026-03-28: Зафиксировано обязательное правило internal quality memory. Сервис должен помнить цепочку `сгенерированный ответ -> реакция пользователя -> downstream route/outcome` и на её основе различать сильные и слабые паттерны ответа. Этот learning contour остаётся внутренним: пользователь не должен видеть язык про “обучение машины” или “тренировку модели”, только более точные и уместные ответы.
- 2026-03-28: JTBD answer assembler начал учитывать живой learning context и quality memory. В `QuestionService` ответы и suggested-route теперь читают `core_profile.living.learning_context`: при необходимости усиливают ясность, сужение фронта и concrete-next-step tone, а money/future lanes больше не ведут пользователя в старые forecast-first корни, а синхронизированы с новым каноном `Today + Profile + Compatibility`.
- 2026-03-29: Learning context встроен и в `Today` decision engine. `/morning-ritual/today` теперь читает `core_profile.living.learning_context` как дополнительный deterministic-layer поверх транзитов, numerology, state, goals и yesterday signals: повторяющиеся темы пользователя, signal bias и preferred response style влияют на дневной focus, риск, действия и ограничения, а debug-сигналы decision engine уже несут этот learning slice как общий контракт для web и iOS.
- 2026-03-29 | Backend Astro | Снят частый 422 на `POST /chart` | DONE | В astro-сервисе `BirthData.location` по умолчанию пустая строка; парсер времени принимает `HH:MM:SS`; `AstroService.compute_chart` подставляет `lat,lon` в `location`, если город не передан; `user_context` всегда шлёт `location` в JSON.
- 2026-03-29 | Backend Today | Слой быстрой доставки для мобильного first paint | DONE | Добавлен `GET /today/opening` (DayConnection + флаги этапов); на `GET /today` — query `light=1` без трекеров дня, среза дневника, вечернего ritual payload и тяжёлого rewards snapshot (утро, core_profile и consistency сохраняются).
- 2026-03-29 | Backend Today | Полный набор progressive-слоёв под один экран Today | DONE | Добавлены `GET /today/checkin-prompt` (следующий чекин по DayConnection, RU/EN), `GET /today/core` (утро без списка сценариев), `GET /today/scenarios` (сценарии по сферам), `GET /today/state-map` (алиас fusion), `GET /today/evening` (вечерняя связка + ritual); общий хелпер `_fetch_morning_ritual_fast` + закрытие `AstroService`; полный `GET /today` использует тот же хелпер для утра.
- 2026-03-29 | Backend Today | Один проход core+scenarios + кеш утра | DONE | Добавлен `GET /today/bundle` и in-memory TTL-кеш (120s) на `(user_id, date, locale)` для `/today/core`, `/today/scenarios`, `bundle` и утренней части полного `GET /today`; при смене `morning_intention` в day-connection кеш сбрасывается.
- 2026-03-29 | Backend Push | Ритм дня и цель на день | DONE | Таблицы `push_devices`, `user_push_schedules`, `daily_goal_snapshots`, `push_dispatch_log` + миграция SQL; API `POST/DELETE /notifications/devices`, `GET/PUT /notifications/schedule`; крон-хук `POST /internal/push/run-due` с `X-Push-Dispatch-Secret`; сервис `push_delivery`: слоты morning/day/evening + goal midday/afternoon по локальному времени, мгновенный пуш при сохранении новой формулировки цели (`morning_intention`); опционально `FCM_SERVER_KEY` для legacy FCM HTTP.
- 2026-03-30 | Product Push | Матрица хуков и анти-спам | DONE | В `docs/status/IOS_TODAYFLOW_STATUS.md` зафиксированы: уже live-хуки, рекомендуемые следующие (streak, weekly focus, карта дня, привычки, re-engagement, transactional), глобальные лимиты/тихие часы/дедуп, категории для будущих тумблеров и технический backlog (`NotificationIntent`, расширение расписания, событийные точки в чекинах и активности).
- 2026-03-31 | Backend Push | Тихие часы, дневной лимит, категории | DONE | В `user_push_schedules`: `quiet_start`/`quiet_end`, `max_auto_per_day` (1–15), флаги `notify_rhythm_today`, `notify_goal_nudges`, `notify_goal_ack`, резервные `notify_streak_care` … `notify_comeback`; миграция `add_push_schedule_antispam.sql`; `run_due` учитывает тихие часы и лимит по `push_dispatch_log`; мгновенный `goal_saved` уважает `notify_goal_ack` и тихие часы; ответ крона расширен `blocked_quiet` / `blocked_cap`.
- 2026-04-26: Зафиксирован канон daily ritual UX и план развития — см. **§4.6** в этом трекере (паритет web/iOS, упаковка Today, очередь по narrative fusion и deep links).
- 2026-04-26: iOS — реализованы deep links чипов «Собрать день» в таб Flow (`pendingTrackerQuickCreate`, шиты цели/аскезы, скролл к новой привычке).
- 2026-04-26: iOS — цели: `week_start` как понедельник недели выбранного дня и якорь месяца `yyyy-MM-01`, лимит 3+3 как на вебе.
- 2026-05-03 | Product | Зафиксирована цель ветки «Today 100%» | IN_PROGRESS | Добавлен §6.2 DoD: ритуал, narrative, meaning parity web/iOS, обновление §4.7 и iOS status при закрытии; вне скоупа DE-10/11/13 и Phase 6 JTBD.
- 2026-05-03 | Frontend/Backend Today | Ритуал, копирайт, narrative cache, slim profile в guide | DONE | Герой без числа до шага числа; «Луна и фон дня» без profile_prism в первой строке; `day_narrative_brief_v0` с RU якорем mood/topic; кэш narrative по `prompt_label` + версия; `user_core` локализован, сырой `profile` убран из guide JSON для LLM.
- 2026-05-03 | Backend Today narrative | Семантическая дедупликация полей guide | DONE | `_dedupe_guide_payload_cross_fields` в `today_narrative` (паритет с веб-дедупом); на кэш-hit та же цепочка + `_normalize_guide_payload_for_tier`; pytest в `test_today_narrative_contract.py`.
- 2026-05-03 | Web + iOS Today | DE-7 UI: главный шаг ↔ fusion completions | DONE | Заголовок секции «Главный шаг на сегодня» (TODAY_WEB §4); строка «Сегодня в Flow уже отмечено: …» из `guide_meaning_completions_today`; тип `FusionResponse.activity_context` на вебе; `TodayRitualCopy.formatGuideMeaningCompletionsLine` на iOS.
- 2026-05-04 | Web + iOS Today | DE-7 UI v3: чипы и пустое состояние | DONE | `guideMeaningCompletionsEyebrow` / `guideMeaningCompletionsEmpty`; `guideMeaningCompletionChipItems` (TS) и `TodayRitualCopy.guideMeaningCompletionChipItems` + `GuideMeaningCompletionsFocusStrip` (Swift); dev `today-ritual-preview` с примером `activity_context`.
- 2026-05-04 | Product | Зафиксирован обязательный контур «умного сервиса» | DONE | §6 переписан: DayContext → narrative → UI → события/вечер → снова контекст; DE-8/DE-9 и §5.2 Learning Next — следующие обязательные инкременты; §5.3 п.8 уточнён (DE-10/11 отдельно, DE-13 эпик); §6.2: DE-7 в желательном заменён на backlog связки шага с событиями.
- 2026-05-04 | Web + iOS + Android scaffold | Ритуал: общий spine-reducer + аналитика из эффектов | DONE | Паритет фаз/переходов и `isSpineComplete`/`tarotContinueAck`; `analyticsHint` + единые исполнители событий; веб: `source: today_ritual` в payload `mood_selected`; Android: `ExecuteRitualSpineAnalytics.kt` + JUnit; см. §4.6 bullet «Ritual spine contract» и [TODAY_PERSONALIZATION_CORE.md](./TODAY_PERSONALIZATION_CORE.md) (payload ритуала).
- 2026-05-04 | Web + iOS Today | DE-9 v1.1: day_history у сфер | DONE | Компонент `TodayDayHistoryStrip`; повтор полоски в `#today-ritual-your-day`; iOS — `fusionDayHistoryStrip` в `spheresTriadBlock` (паритет).
- 2026-05-04 | Web + iOS Today | DE-9 v1.2: недельная сводка в полоске | DONE | `trailing_7d_summary` → вторая строка в `TodayDayHistoryStrip` / `fusionDayHistoryStrip`; Jest `formatFusionDayHistory.test.ts`; mock в `today-ritual-preview`.
- 2026-05-04 | Full-stack Today | DE-9 v1.3 + мета-срез guide | DONE | Нулевая дельта: `RITUAL_COPY.dayHistoryDeltaAllZeroTail` / EN + `formatFusionDayHistoryEn`; iOS `TodayRitualCopy` (RU/EN); `strip_llm_meta_commentary` + `strip_meta_from_guide_payload` в `ritual_cue_sanitize.py` → `_guide_apply_final_processing_pass`; pytest `test_ritual_cue_sanitize.py`; дорожная карта «Оркестратор O1–O12» в [TODAY_LANGUAGE_V1.md](./TODAY_LANGUAGE_V1.md).
- 2026-05-04 | Backend + Web + iOS | §5.2 implicit: «Почему так?» в ритуале | DONE | `today_guide_why_opened` в `VALID_EVENT_TYPES`, вес Mind `0.03`; веб `TodayRitualFlow`, iOS `TodayRitualFlowView`; pytest `test_post_meaning_events_accepts_today_guide_why_opened`; [TODAY_PERSONALIZATION_CORE.md](./TODAY_PERSONALIZATION_CORE.md).
- 2026-05-04 | Web + iOS + Android scaffold | §5.2: generation_id на шагах хребта | DONE | При наличии guide — `number_selected` / `mood_selected` с `generation_id`: веб `executeRitualSpineAnalytics` + `narrativeGenerationIds.guide`, iOS `applySpineEffects` + `todayGuideNarrative.generationID`, Android параметр `guideGenerationId`; Jest `todayRitualSpineMachine.test.ts`; см. [TODAY_PERSONALIZATION_CORE.md](./TODAY_PERSONALIZATION_CORE.md) (ритуальная цепочка).
- 2026-05-04 | Web + iOS + Backend | §5.2: tarot + DE-9 visibility | DONE | `tarot_selected` с опциональным `generation_id` (веб/iOS); `today_day_history_first_visible` (`VALID_EVENT_TYPES`, Mind `0.025`), веб `TodayDayHistoryStrip` + IntersectionObserver, iOS `fusionDayHistoryStrip(placement:)` + `onAppear`; pytest `test_post_meaning_events_accepts_today_day_history_first_visible`.
- 2026-05-04 | Web + iOS | §5.3 UI garbage (канон копирайта) | DONE | `TodayResultView`: интро сфер из `RITUAL_COPY.areasIntroToday` (убран дубль захардкоженного текста); чипы «Собрать день» — `RITUAL_BUILD_DAY_QUICK_CHIPS` / `TodayRitualCopy.BuildDayQuickChips` (паритет [TODAY_SCREEN_V1_CANON.md](./TODAY_SCREEN_V1_CANON.md) §3–4).
- 2026-05-04 | Web + iOS Today | §5.3 UI garbage (оболочка `/today`) | DONE | `RITUAL_COPY`: загрузка/ошибки/фон, подписи шагов дня, тост и хром фокус-таймера, строки `TodayNarrativeDepthControl`; iOS — `TodayRitualCopy.TodayPageShell`, `NarrativeDepthControl`, `FocusTimerChrome` (в т.ч. «Собираю твой день…» / «Обновляю твой день…» вместо «Today»).
- 2026-05-04 | Web + iOS Today | §5.3 UI garbage (тосты и фолбэки `/today`) | DONE | `RITUAL_COPY`: тосты Guidance / DE-8 / сохранения дня и вечера / практики; фолбэки заголовка дня, числа, колец плана; `NUMEROLOGY_LUCKY_DAY_PRESETS`; iOS — `TodayPageToasts`, `NarrativeDepthToasts`, `NumerologyLuckyDayPresets`, `numerologyMeaningFallbackShort`, резерв заголовка дня в `dayTypeHeadline`.
- 2026-05-04 | Web + iOS Today | §5.3 UI garbage (`TodayRitualFlow` + связка карта/число) | DONE | `RITUAL_COPY` + хелперы: мост карта+число, кольцо «таро», риск/лучший ход, подсказка героя, таро без анимации, чек-ин, шит детали, закрытие/«Поняла»; iOS — те же формулы в `TodayRitualCopy`, `bridgeLine` = веб-фолбэк, `TodayGuideActionable` использует `heroRiskLabel` / `heroBestMoveLabel`.
- 2026-05-04 | Web + iOS Today | §5.3 UI garbage (`TodayResultView`) | DONE | `RITUAL_COPY`: `eveningHookBodyCompact`, `areasTriadModalDetailHint`, `sphereSheetNavTitle` (aria), `formatActionOptionEstimatedMinutesSuffix`; кнопка модалки сферы — `sheetCloseCta`; iOS — `eveningHookBodyCompact`, `areasTriadModalDetailHint` в каноне (UI треугольника без «окна» — строка не дублируется в разметке).
- 2026-05-04 | Web + iOS Today | §5.3 канон копирайта (Guide / Working / Quick actions) | DONE | Веб: `RITUAL_COPY` + хелперы в `todayRitualCopy.ts`; `TodayQuickActions`, `TodayGuideSection`, `TodayWorkingLayerSection` без захардкоженного русского; iOS — `TodayWebQuickActionsCopy`, `TodayWebGuideSectionCopy`, `TodayWebWorkingLayerCopy` в `TodayRitualCopy.swift` (дословный паритет для нативных экранов позже).
- 2026-05-04 | Web + iOS Today | §5.3 канон копирайта (сферы `/today` + хром секций) | DONE | `RITUAL_COPY`: блок сфер (`TodayLifeSpheresSection`), общие CTA «Свернуть»/«Развернуть»/«Открыть», подсказки `DaySectionHeader` (`TodaySectionPrimitives`); iOS — `TodayWebLifeSpheresCopy`, `TodayWebSectionChromeCopy`.
- 2026-05-04 | Web + iOS Today | §5.3 канон копирайта (этапы дня `/today`) | DONE | `RITUAL_COPY` + хелперы: `TodayDaySection`, `TodayMorningSection`, `TodayEveningSection`, `TodayFlowTabs`; вечерний outlook и связь с утром; iOS — `TodayWebDaySectionCopy`, `TodayWebMorningSectionCopy`, `TodayWebEveningSectionCopy`, `TodayWebFlowTabsCopy` (число/чек-ин — `TodayRitualCopy`).
- 2026-05-04 | Web + iOS Today | §5.3 канон: табы `/today` + уровни DE-8 | DONE | `TODAY_FLOW_TABS` из `RITUAL_COPY`; подписи «Короче/Обычно/Глубже» в `todayNarrativeDepthUi` + `TodayRitualCopy.NarrativeDepthControl.option*`; iOS `TodayView` / `ProfileView` без захардкоженных строк селекта; `TodayWebFlowTabsCopy` — подписи вкладок для паритета.
- 2026-05-04 | Web + iOS Today | §5.3 канон: прогрев `/today` + маршруты сфер | DONE | `thinkingMessages` и `getHoroscopeScenarioRoute` из `RITUAL_COPY`; iOS — `TodayWebPageShellCopy` (дословный паритет).
- 2026-05-04 | Web + iOS Today | §5.3 канон: данные дня в `todayPageUtils` | DONE | События для нарратива, подзаголовок входа в ритуал, тултипы ритма, награды/карточка rewards, персональный инсайт, следующее действие, дневной нудж, сводка энергии — в `RITUAL_COPY` + форматтеры в `todayRitualCopy.ts`; iOS — `TodayWebTodayPageDataCopy`.
- 2026-05-04 | Product | §5.3.1 SoT копирайта Today в трекере | DONE | Подпункт **5.3.1**: канон `todayRitualCopy.ts` ⇄ `TodayRitualCopy.swift`, связь с п.1 UI garbage; перенос «вопроса дня» — см. строку лога «§5.3.1: вопрос дня в каноне».
- 2026-05-04 | Web + iOS Today | §5.3 канон: фокус/риск/план/неделя/«сейчас»/ритм возврата | DONE | `buildDayFocusSummary`, `buildDayRiskSummary`, `buildTodayActionPlan`, `buildTodayCriticalLimits`, `buildWeeklyPatternMap`, `buildLifeNowSummary`, `buildDailyReturnCadence` → `RITUAL_COPY` + форматтеры; расширение `TodayWebTodayPageDataCopy`; без карточки «вопрос дня» (след. инкремент).
- 2026-05-04 | Web + iOS Today | DE-8 v3: глубина narrative на Today | DONE | Веб: `TodayNarrativeDepthControl`, `narrativeDepthSeq` → повторный `postTodayNarrative(guide)`; iOS: `TodayNarrativeDepthInlineBar`, `patchTodayNarrativeDepthLevel`, `preloadAllNarratives(force:)`; якорь настроек `#today-narrative-depth-settings`.
- 2026-05-04 | Backend + Web + iOS | DE-8 v4: learning-сигнал смены глубины | DONE | `today_narrative_depth_changed` в `VALID_EVENT_TYPES`, вес в Mind; клиенты шлют событие после успешного сохранения; pytest `test_post_meaning_events_accepts_narrative_depth_changed`; §4.7 DE-8 → **DONE**.
- 2026-05-04 | Web + iOS | DE-8 v4.1: событие и из формы настроек | DONE | Веб `/account/settings`: `trackMeaningEvent` при фактической смене `today_narrative_depth_level`; iOS `ProfileSettingsView`: `trackTodaySurfaceEvent` + `serverSyncedNarrativeDepth`; `payload.source` `account_settings` / `profile_settings` в [TODAY_PERSONALIZATION_CORE.md](./TODAY_PERSONALIZATION_CORE.md).
- 2026-05-04 | Web + Backend + i18n | OAuth redirect callbacks | DONE | `POST /oauth/google/code`, `GET /oauth/providers.code_exchange_enabled`, колбэки Next `/auth/google/callback`, POST Apple `/auth/apple/callback`; `OAuthButtons` через `getJson`, `state` + i18n `auth.oauth.callback.*`; `.env.example`; pytest в `test_auth.py`; дорожная карта #26.
- 2026-05-04 | Web + iOS | §5.3.1: «вопрос дня» в каноне | DONE | `RITUAL_QUESTION_OF_DAY_*` + `buildRitualQuestionOfDayDefaultCards` в `todayRitualCopy.ts`; `buildQuestionOfDay` — только выбор по дате/энергии/фокусу; `TodayWebQuestionOfDayCopy` в `TodayRitualCopy.swift`; §5.3.1 трекера без остатка по этому пункту.
- 2026-05-04 | iOS | RU/EN аудит (инкремент) | IN_PROGRESS → частично | `AuthView` + `PasswordRecoveryView`: `AuthScreenChrome` по той же схеме, что `CompatibilityScreenChrome`; `ProfileSettingsScreenChrome` — подпись пикера «ты»; `ExploreHubView` — ru/en заголовки и подзаголовки карточек; см. дорожную карту #30. Остаток аудита: онбординг, демо-лейауты, отдельные экраны.
- 2026-05-04 | Web + iOS Today | §5.3 канон: баннеры быстрого ответа / вопроса дня (iOS) | DONE | `RITUAL_COPY` + `TodayWebWorkingLayerCopy`: префиксы баннеров и подпись кнопки сохранения в компактном блоке `TodayView`; паритет формулировок с веб-каноном на будущее.
- 2026-05-04 | Web + iOS Today | §5.3 канон: компактный «быстрый ответ» iOS (полный блок) | DONE | `workingLayerCompactQuickAnswer*` в `todayRitualCopy.ts` и `TodayWebWorkingLayerCopy`; `TodayQuickAnswerSection` без захардкоженного русского.
- 2026-05-04 | Web + iOS Today | §5.3.1: нативные композеры `TodayView` (утро/чек-ин/дневник/вечер) | DONE | `todayView*` + `dayJournalPrompt*` + форматтеры в `todayRitualCopy.ts`; `TodayWebTodayViewComposerCopy` и промпты в `TodayWebDaySectionCopy`; чек-ин — шкалы из `TodayWebEveningSectionCopy`; правка синтаксиса `ringHint*` в `TodayExperienceLayout.swift` (`static var`).
- 2026-05-04 | Web + iOS Today | §5.3.1: `TodayView` герой + панели + таро/fusion | DONE | `TODAY_SHELL_COPY.shell*` + `formatShell*` в `todayRitualCopy.ts`; расширение `TodayShellCopy` и замена литералов в `TodayView.swift`; RU-фолбэки цикла действий вместо EN; подсказки цели (`shellGoalHint*`).
- 2026-05-04 | Web + iOS Today | §5.3.1: четыре сферы + `TodayRitualFlowView` | DONE | `fourArea*` + `ritualFlow*` + `formatFourArea*` / `formatRitualFlow*` в `todayRitualCopy.ts`; `todayFourAreas.ts` на каноне; зеркало в `TodayRitualCopy.swift`; `TodayRitualFlowView` + `RitualFourAreaBuilder` без захардкоженного RU в перечисленных блоках; риск энергии унифицирован с вебом («Напряжение редко…»); настроение `driven` — тот же суффикс, что у мотивации.
- 2026-05-04 | Web + iOS Today | §5.3.1: `TodayExperienceLayout` chrome RU/EN | DONE | `TODAY_EXPERIENCE_CHROME_RU` / `EN` + хелперы в `todayRitualCopy.ts`; `TodayExperienceChromeCopy.swift` + файл в таргете Xcode; `TodayExperienceLayout` без локального `TodayExpChrome`.
- 2026-05-04 | Web + iOS | §5.3.1: Flow / Практики / главный TabView chrome | DONE | TS `flowPracticesMainTabChrome.ts` (+ реэкспорт из `todayRitualCopy.ts`); iOS `FlowPracticesMainTabChromeCopy.swift`, `FlowTrackerChrome.swift` как `typealias`; подписи табов в `ContentView` через `TodayMainTabCopy`.
- 2026-05-04 | Web + iOS | §5.3.1: веб `/tracking/calendar` hero → канон Flow | DONE | `trackingCalendarPage*` в `flowPracticesMainTabChrome.ts` / `FlowTrackerChromeCopy`; страница через `flowTrackerChromeBundle(getLocale())`.
- 2026-05-04 | Web + iOS | §5.3.1: веб `/tracking/progress` хаб → канон Flow | DONE | `trackingProgress*` карточки/футер/логин в `flowPracticesMainTabChrome.ts` + `FlowTrackerChromeCopy`; `progress/page.tsx` на `flowTrackerChromeBundle`.
- 2026-05-04 | Web + iOS | §5.3.1: веб heatmap календаря → канон Flow | DONE | `heatmap*` в `FlowTrackerChromeCopy` / TS; вкладка «Практики» — `practicesExperienceChromeBundle().navPractices`; `CalendarHeatmap.tsx` + `weekdayFallback`; легенда — `heatmapLegend*` (см. также удаление `HEATMAP_LABEL` в трекере 2026-05-04).
- 2026-05-04 | Web + iOS | §5.3.1: heatmap drill + инсайт под картой + сводка категорий | DONE | `heatmapDrillDayCaption*`, `heatmapUnderMapInsight*`, `trackingCatSummary*` в `flowPracticesMainTabChrome.ts` / `FlowTrackerChromeCopy`; `calendarHeatmapModel.ts` + `entityTrackerCompute.categorySummaryLines` принимают `fc`; placeholder сущности в `CalendarHeatmap` из канона.
- 2026-05-04 | Web | `trackingRhythm` — только используемое API | DONE | Оставлены `lineDone` + `computeMarks` + типы; удалены неимпортируемые `buildWhatsHappening`, `computeRhythmBand`, `habitStabilityLabel`, `asceticHoldPhrase`, `practiceAttentionPhrase`.
- 2026-05-04 | Web + iOS | Веб `/habits` — карта привычек → канон Flow | DONE | `habitsMap*` в `flowPracticesMainTabChrome.ts` / `FlowTrackerChromeCopy`; страница на `flowTrackerChromeBundle` + `getLocale()`; тултипы heatmap — `ru-RU`/`en-US`; CTA логина — `trackingProgressHubLoginCta`.
- 2026-05-04 | Web | Мастер сущностей: шаблоны из канона RU/EN | DONE | `trackerEntityCatalog.ts` — типы + `filterAsceticismsByCategory`; данные в `components/today/trackerEntityTemplateCatalog.ts` (`getGoalTemplateGroups` / `getHabitTemplateGroups` / `getAsceticCategoryFilters`); фильтры аскез — объединённые RU+EN `keywords`; `EntityCreateWizard` по `getLocale()`. iOS/Android: при нативном мастере — паритет с этим TS-файлом.
- 2026-05-04 | Web + iOS | §5.3.1: `buildAttentionItems` / `buildBestItems` + heatmap tokens | DONE | `trackingAttention*` / `trackingBest*` в каноне; `entityTrackerCompute` принимает `fc`; удалён неиспользуемый `HEATMAP_LABEL` из `heatmapTokens.ts` (легенда только `heatmapLegend*`).
- 2026-05-04 | Web + iOS | §5.3.1: веб `/tracking/insights` + `/tracking/diary` → канон Flow | DONE | `trackingInsights*`, `trackingInsight*`, `trackingDiary*`, `trackingFormDateLabel`, `diary*Placeholder`, `insightsGeneratingShort`, `saveDiarySaving`, `insightsGenerateErrorFallback`; страницы на `flowTrackerChromeBundle(getLocale())`; даты — `ru-RU`/`en-US`; iOS — `trackingAutoInsightTypeLabel(for:)` + зеркальные строки в `FlowTrackerChromeCopy` (`insightsEmpty`/`insightsIntro` для `RitualsView` без изменения смысла).
- 2026-05-04 | Web + iOS | §5.3.1: веб `/tracking/calendar` page toasts + empty/login | DONE | `trackingCalendarEmptyState`, `trackingCalendarLoginPrompt`, `trackingToast*` в `flowPracticesMainTabChrome.ts` + `FlowTrackerChromeCopy`; `calendar/page.tsx` на `flowTrackerChromeBundle`.
- 2026-05-04 | Web + iOS | §5.3.1: веб `TrackerView` + `EntityCreateWizard` → канон Flow | DONE | `actionSave`/`actionCancel`, `habitSheetTitle`, `trackingEntityWizard*`, `trackingView*`; `practicesExperienceChromeBundle` для `navPractices`; даты полосы дней — `ru-RU`/`en-US`; зеркало в `FlowTrackerChromeCopy`.
- 2026-05-04 | Web + iOS | §5.3.1: веб `/affirmations` → канон Flow | DONE | `affirmations*` в `flowPracticesMainTabChrome.ts` / `FlowTrackerChromeCopy` (герой, фильтры, фокусы, каталог, CTA, `detectFocus` + EN-регэкспы); страница на `flowTrackerChromeBundle(getLocale())`.
- 2026-05-04 | Web + iOS | §5.3.1: веб `/affirmations/tracker` → канон Flow | DONE | `affirmationsTracker*` + реюз `trackingFormDateLabel`, `trackingDiaryEntriesHeading`, `actionSave`, `saveDiarySaving`, `trackingDiarySaveError`, `trackingProgressHubLoginCta`, `affirmationsLibraryLinkTracker`; даты `ru-RU`/`en-US`; зеркало в `FlowTrackerChromeCopy`.
- 2026-05-04 | Web + iOS | §5.3.1: веб `/practices` каталог (мастер) | DONE | `practicesCatalog*` в `PRACTICES_EXPERIENCE_CHROME_*` / `PracticesExperienceChromeCopy`; цели и направления + ключевые слова фильтра в `practicesCatalogContent.ts` (RU-ключи направлений для матчинга API); страница на `practicesExperienceChromeBundle(getLocale())`; `inferPracticeDefaultsFromJTBD` типизирует `PracticeCatalogDirectionKey`.
- 2026-05-04 | Web + iOS | §5.3.1: веб `/practices/[id]` карточка практики | DONE | `practiceDetail*` + `practicePatternAxisA1`–`A7` в `PRACTICES_EXPERIENCE_CHROME_*` / `PracticesExperienceChromeCopy`; реюз `stepsDoneLabel`, `practicesCatalogDifficulty*`; убран неиспользуемый `useRouter`/`PatternLink`/`currentStepNumber`.
- 2026-05-04 | Web + iOS | §5.3.1: веб `/practices/history` | DONE | `practicesHistory*` + реюз `historyProgressTitle`, `statistics`, `stat*`, `completedPractices`, `navHistory`, `repeatCta`, `practiceDetailBackLink`; даты `ru-RU`/`en-US`; зеркало в `PracticesExperienceChromeCopy`.
- 2026-05-04 | Web + iOS | Веб `/guidance/history` | DONE | Канон `guidanceHistoryChrome.ts` ⇄ `GuidanceHistoryChromeCopy` + `typealias GuidanceHistoryChrome`; страница без `t()`; `guidance.history.filtersAria` в `app.ru.json`/`app.en.json` (паритет с каноном).
- 2026-05-04 | Web | Guidance history: один вход по локали | DONE | `guidanceHistoryPageBundle.ts` — `guidanceHistoryPageBundle(locale)` = `chrome` + `catalogLocale` + `formatHistoryDate` (`ru-RU`/`en-US`); `/guidance/history/page.tsx` собирает хром и каталог из одного бандла (паритет с `guidanceHubPageBundle`).
- 2026-05-04 | Web + iOS | Веб `/guidance` (хаб расклада) | DONE | Канон `guidanceHubChrome.ts` ⇄ `GuidanceHubChromeCopy` + `typealias GuidanceHubChrome`; `guidanceHubInterpolate` для `{startOver}` / `{question}` / `{spreadTitle}`; страница на `guidanceHubChromeBundle`; `auth.login.title` остаётся в `t()`; строки = `nav.guidance.hub` + `guidance.page.*` в JSON.
- 2026-05-04 | Web + iOS | Веб `/tarot/result` — канон строк | DONE | `tarotSpreadResultChrome.ts` ⇄ `TarotSpreadResultChromeCopy.swift` + `typealias TarotSpreadResultChrome`; ключи `tarot.spreadResult.*` в `app.ru.json`/`app.en.json`; страница на `tarotSpreadResultChromeBundle` + `tarotSpreadResultResolvePositionLabel` (позиции past…outcome).
- 2026-05-04 | Web + iOS | Guidance: результат разбора + полоса карт + `GuidanceResultCard` | DONE | `guidanceResultChrome.ts` ⇄ `GuidanceResultChromeCopy.swift` + `typealias GuidanceResultChrome`; ключи `guidance.result.*`, `guidance.strip.*`, `guidance.resultCard.*` в `app.ru.json`/`app.en.json`; `stripTarotAppendFromExplanation` (RU+EN); подсказка совместимости по EN-регэкспу для `relationships`.
- 2026-05-04 | Web + iOS | Guidance: безопасность вопроса + подпись селекта расклада | DONE | `guidanceSafetyKeywords` — RU + EN (фразы + `\brape\b`); зеркало `GuidanceSafetyKeywords.swift`; `guidanceHubSpreadField` в `guidanceHubChrome.ts` ⇄ `GuidanceHubChromeCopy` (паритет `guidance.catalog.spreadField`).
- 2026-05-04 | Web + iOS + Android | Guidance: эвристики вынесены из UI | DONE | `guidanceResultLoveQuestionHeuristic` / `guidanceResultShowCompatHint` в `guidanceResultChrome.ts`; зеркало `GuidanceResultChromeCopy`; Android `GuidanceQuestionHeuristics.kt` (`GuidanceSafetyKeywords`, `GuidanceCompatHint`) — паритет с вебом/iOS (в репо нет `gradlew`; проверка `:app:compileDebugKotlin` — при настроенном Gradle).
- 2026-05-04 | Web + iOS | Guidance hub: группы раскладов в каноне хаба | DONE | `guidanceHubCatalogSectionQuick|Medium|Deep` + `guidanceHubSpreadSectionLabelsFromBundle` в `guidanceHubChrome.ts`; `/guidance` на этом каноне; удалён неиспользуемый `localizedGuidanceSectionLabels` из `catalog.ts`; iOS `GuidanceHubChromeCopy` + реюз в `GuidanceViewChrome.spreadSection*`.
- 2026-05-04 | Web | Guidance hub: единый бандл каталога мастера | DONE | `guidanceHubWizardCatalog.ts` — `guidanceHubWizardCatalogBundle(locale)` (расклады, темы, исходы, уточнение, роли, intimacy); `/guidance/page.tsx` один `useMemo` вместо шести; строки по-прежнему из `catalog.ts` / `guidance.catalog.*`.
- 2026-05-04 | Web | Guidance hub: один вход по локали | DONE | `guidanceHubPageBundle.ts` — `guidanceHubPageBundle(locale)` = `chrome` + `wizardCatalog` + `spreadSectionLabels`; `/guidance/page.tsx` один `useMemo` на страницу для хаба.
- 2026-05-04 | Web + iOS | §5.3.1: сводка трекера (`entityTrackerSpec` / `MARK_TODAY`) → канон | DONE | `trackingCategory*`, `trackingScreenHero*`, `trackingStatus*`, `trackingMarkToday*`, `trackingViewLimitsHint`, `trackingViewTodayLinkHint`; `entityTrackerSpec.ts` — только типы + `FREE_LIMITS`/`PRO_LIMITS`; `MARK_TODAY` убран из `trackerSpec.ts`.
- 2026-05-04 | Web | `trackerSpec` / `trackerCompute` — вырезан мёртвый слой | DONE | `trackerSpec.ts` — только `TrackerTier` + `DEFAULT_TRACKER_TIER`; из `trackerCompute.ts` оставлен `sliceLastNDaysSorted` (остальные вычисления и RU-строки нигде не импортировались). Новый UI-инсайт — через канон Flow, не через старые таблицы.
- 2026-05-04 | Tooling | iOS Xcode открытие проекта | DONE | Восстановлен `TodayFlow.xcodeproj/project.xcworkspace/contents.xcworkspacedata` (обязательный файл пакета).
- 2026-05-04 | Full-stack Today | O6: низкий ресурс настроения (tired/heavy/quiet_wish) | DONE | Промпт `LOW_RESOURCE` / `РЕЖИМ_НИЗКИЙ_РЕСУРС` + metadata `low_energy_ritual_mood`; веб/iOS — один шаг фокуса, меньше CTA, без недели в day history / без чипов build-day; Jest `isLowEnergyRitualMood`; pytest system prompt; [TODAY_LANGUAGE_V1.md](./TODAY_LANGUAGE_V1.md) O6.
- 2026-05-04 | Backend Today narrative | O8: day_layer без «простыни» и дубля anchor | DONE | `_finalize_day_layer_payload_o8` после LLM и на cache hit; лимиты `nudge` / `personal_insight_*` / chips; снятие дословного префикса `anchor_summary`; доп. строки в `_DAY_SYS`; pytest `test_o8_finalize_day_layer_*`; [TODAY_LANGUAGE_V1.md](./TODAY_LANGUAGE_V1.md) #35.
- 2026-05-04 | Web + iOS Today | O9: один канонический главный шаг + CTA «К шагу дня» | DONE | `guideCanonicalPrimaryStepLine` в `todayGuideActionable.ts` / Jest; `TodayGuideSection` + `RITUAL_COPY.guidePrimaryNavigateCta`; iOS `TodayGuideActionable.guideCanonicalPrimaryStepLine`, `TodayGuidePanel.guideExecutionDoItems`, `TodayWebGuideSectionCopy.guidePrimaryNavigateCta`; [TODAY_LANGUAGE_V1.md](./TODAY_LANGUAGE_V1.md) #36 / O9.
- 2026-05-04 | Full-stack Today | O10: мета-комментарий LLM — расширение паттернов + day_layer | DONE | `ritual_cue_sanitize._LLM_META_NEEDLES`, `strip_meta_from_guide_payload` (доп. поля `core_message`); `_finalize_day_layer_payload_o8` + `strip_llm_meta_commentary`; паритет `ritualCueSanitizer.ts`, `TodayRitualCueSanitizer`, `RitualCueSanitizer.kt` + тесты; pytest / Jest / JUnit; дорожная карта #37 / O10.
- 2026-05-04 | Backend Today narrative | O1 (guide): дедуп hero vs тезис | DONE | `_dedupe_guide_payload_cross_fields`: очистка `headline`/`subline` при `_texts_semantically_redundant` с `core_message.body` и `anchor_summary`; subline при дубле headline; pytest `test_o1_top_level_hero_cleared_when_redundant_with_core_body_and_brief_anchor`, `test_o1_subline_cleared_when_redundant_with_headline_only`; дорожная карта #38 / O1.
- 2026-05-04 | Full-stack Today | O3: RU gate заголовка `day_layer` | DONE | `is_ru_abstract_topic_headline`, расширение `_TOPIC_LABELS_NOT_ACTIONS`; `_day_layer_payload_concrete` (мин. 12 символов для `personal_insight_title`); pytest `test_text_quality`, `test_ritual_cue_sanitize`; паритет `isRuAbstractTopicHeadline` / `TodayRitualCueSanitizer` / `RitualCueSanitizer.kt`; Jest `ritualCueSanitizer.test.ts`; дорожная карта #39 / O3.
- 2026-05-04 | Backend Today narrative | O4 + кэш guide / dedupe hero | DONE | При непустом `ritual_norm` RU — `_guide_payload_links_ritual_context` (иглы tarot/число/mood/head_topic/day_events); `_dedupe_guide_payload_cross_fields`: не снимать `headline` только из‑за `anchor_summary` (совместимо с `_guide_payload_concrete` и повторной валидацией кэша); EN — не обнулять `headline` при overlap с `core_message.body`; pytest `test_o4_*`, `test_guide_narrative_cache_hit_when_day_context_unchanged`, EN fallback; дорожная карта #40 / O4.
- 2026-05-04 | Full-stack Today | O5: кавычечные EN slug → RU подпись | DONE | `replace_quoted_en_slugs_for_ru_display` в `ritual_cue_sanitize` (spine + recommendations); паритет TS / Swift / Kotlin + `repairRitualDoNotEnterLine`; веб — `todayRitualSignals`, `todayPageUtils`; pytest / Jest / JUnit; дорожная карта O5.
- 2026-05-04 | Backend + Web + iOS Today | O7: «Ритм и вчера» без ложных баллов | DONE | `history_layer_v0`: `trailing_7d_summary_trustworthy`, `trailing_7d_flow_days`; при `fusion_score_delta_trustworthy=false` — одна строка без «Вчера: …», скрытие `trailing_7d` при нуле дней с Flow; веб `formatFusionDayHistory*`, `TodayDayHistoryStrip.footerHint`, `isFusionDayHistoryDeltaUntrustworthy`; iOS `FusionDayHistoryV0` + `fusionDayHistoryStrip`; pytest `test_history_layer_v0`, Jest `formatFusionDayHistory`; дорожная карта O7.
- 2026-05-04 | Backend + Web + iOS Today | O11: сферы и rhythm_context | DONE | `_rhythm_context_signal_categories`, `_spheres_payload_grounded_in_rhythm`, расширение `_SPHERES_SYS`; `_spheres_payload_concrete(..., rhythm_context)`; веб `computeSphereScoresProvisional`, `areasScoresProvisionalHint`, префикс `≈` у %; iOS `sphereScoresProvisional` + тот же копирайт; pytest `test_o11_spheres_rhythm_grounding.py`, Jest `todayFourAreas.test.ts`; дорожная карта O11.
- 2026-05-04 | Backend Today | O12: merge-pass в метаданных оркестратора | DONE | `ORCHESTRATOR_VERSION` 0.3.0, `MERGE_PASS_CONTRACT`, `narrative_merge_pass_plan`, поля `merge_pass_steps` / `primary_narrative_anchor` / стадия `merge_pass_documented` в `build_today_narrative_orchestration_meta`; pytest `test_generation_orchestrator.py`, расширение `test_today_narrative_contract`; дорожная карта O12.
- 2026-05-04 | Full-stack Today | O2: явный primary в payload guide | DONE | `narrative_hierarchy` (`narrative_hierarchy_v0`, `primary_anchor` = `day_engine_brief`) на cache hit и свежей генерации; `todayNarrativeApi` / `parseNarrativeHierarchyFromGuide` + Jest; iOS `TodayGuideActionable.narrativeHierarchyDisplay`; Android каркас `GuideNarrativeHierarchy.kt` + `GuideNarrativeHierarchyTest`; `DAY_CONTEXT_V0.md`; pytest `test_today_narrative_contract`, `test_today_narrative_day_layer_logs_day_context_hash`; дорожная карта O2 / #41.
- 2026-05-04 | Web + iOS | P1 RU: Guidance → «Разбор» в пользовательском тексте | DONE | `TODAY_MAIN_TAB_COPY_RU.guidance` = «Разбор» (`flowPracticesMainTabChrome.ts`); `GuidanceViewChrome` — заголовок «Центр разборов», фильтры/история/режимы без латиницы; `TodayExperienceChromeCopy` + `todayRitualCopy` (`TODAY_EXPERIENCE_CHROME_RU`, тост `todayToastGuidanceFollowup`); `ExploreHubView` секция; `CompatibilityView` CTA; кнопки ритуала → `TodayMainTabCopy.flow`; паритет TS ⇄ Swift.
- 2026-05-04 | Web | P1: `/guidance` и `/guidance/history` через `t()` + каталоги | DONE | Ключи `guidance.page.*`, `guidance.history.*` в `CONTENT/i18n/app.ru.json` / `app.en.json`; eyebrow = `nav.guidance.hub`; RU без латинского «Guidance» в UI; EN — полные строки; даты истории `ru-RU` / `en-US` по `getLocale()`.
- 2026-05-31 | Product / Economy | User Evolution + Gamification + Symbolic Commerce canons | DONE | [USER_MODEL_TARGET_STATE.md](./USER_MODEL_TARGET_STATE.md), [USER_MODEL_TARGET_STATE.md](./USER_MODEL_TARGET_STATE.md), [REFERENCE_LAYER_AND_BUILD_ORDER.md](./REFERENCE_LAYER_AND_BUILD_ORDER.md): Personal Path, PEG, cycles, stage→API, symbolic reference.
- 2026-05-31 | Product / Architecture | User Model Target State (north star) | DONE | [USER_MODEL_TARGET_STATE.md](./USER_MODEL_TARGET_STATE.md): 4 outputs, Compact User Model, uncertainty metric, UMTS filter, stop infinite layering.
- 2026-05-31 | Product / Architecture | Interpretation Layer & Reference canon | DONE | [INTERPRETATION_LAYER_AND_REFERENCE.md](./INTERPRETATION_LAYER_AND_REFERENCE.md): Interpretation Reference, Engine, Instance, taxonomy×10, L1–L4, Signal→Interpretation→Knowledge.
- 2026-05-31 | Product / Architecture | Knowledge Acquisition & Signal Policy | DONE | [KNOWLEDGE_ACQUISITION_AND_SIGNAL_POLICY.md](./KNOWLEDGE_ACQUISITION_AND_SIGNAL_POLICY.md): channels A–I, trust T1–T5, fact/pattern/hypothesis, Event→Signal→Confirmation→Knowledge; UKM v1.1 fields.
- 2026-05-31 | Product / Architecture | User Knowledge Model canon | DONE | [USER_KNOWLEDGE_MODEL.md](./USER_KNOWLEDGE_MODEL.md): Knowledge Atoms, Events→Signals→Knowledge→Memory→Context; UKM before Gate; proto-code `meaning_surface_patterns_v0`.
- 2026-05-31 | Product / Architecture | API Memory & Learning Layer canon | DONE | [API_MEMORY_AND_LEARNING_LAYER.md](./API_MEMORY_AND_LEARNING_LAYER.md): LLM Call Gate, Request/Response/Reaction records, cache/reuse, Learning Signals, dataset status, token ROI; links PIL + generation_logs baseline.
- 2026-05-31 | Product / Architecture | PIL v2 — сквозной learning-aware канон | DONE | [PERSONAL_INTELLIGENCE_LAYER.md](./PERSONAL_INTELLIGENCE_LAYER.md) v2: Every feature must be learning-aware; два выхода; Global Build Order 1–12; Training Dataset; freeze без PIL; cursor rule `personal-intelligence-layer.mdc`.
- 2026-05-31 | Product / Architecture | Personal Intelligence Layer canon | DONE | [PERSONAL_INTELLIGENCE_LAYER.md](./PERSONAL_INTELLIGENCE_LAYER.md): events→memory→retrieval→prompt refinement→orchestrator→evaluation→feedback; maturity path to fine-tuning; LLM denylist; code baseline map.
- 2026-05-31 | Product / Architecture | Data ownership & consumption map | DONE | [DATA_OWNERSHIP_AND_CONSUMPTION_MAP.md](./DATA_OWNERSHIP_AND_CONSUMPTION_MAP.md): CD/DD/SN/RT, chain Reference→Behavior, CoreProfile/DayContext boundaries, API read model, LLM/UI policies.
- 2026-05-31 | Product / Architecture | Ontology & foundation phases canon | DONE | [ONTOLOGY_AND_FOUNDATION_PHASES.md](./ONTOLOGY_AND_FOUNDATION_PHASES.md): 5 phases (Knowledge→Rules→Intelligence→LLM→Own Model); current stage = world ontology; consumer/API/UI freeze; maps P0 + PIL to phases.
- 2026-05-31 | Product / Architecture | Data origination & lifecycle canon | DONE | [DATA_ORIGINATION_AND_LIFECYCLE.md](./DATA_ORIGINATION_AND_LIFECYCLE.md): six-level build order, creation methods, nine-field entity template, registry v1, filling policy, data-first freeze (no screen/API-first planning).
- 2026-06-01 | Product / Architecture | Branch B Evolution Engine — architecture closed at B1.5 | DONE | contracts CD only; B1.6 deferred; primary signal supplier = Branch C; [status/branch_b_evolution_engine.md](./status/branch_b_evolution_engine.md).
- 2026-06-01 | Product / Architecture | Branch D1.0 Symbolic Asset Ontology | DONE | Symbolic Asset ≠ Product; entities only; deps A/B/C/E ready; [SYMBOLIC_ASSET_ONTOLOGY.md](./SYMBOLIC_ASSET_ONTOLOGY.md); next D1.1.
- 2026-06-01 | Backend / Contract | Branch D1.1 Symbolic Asset Definition Registry | DONE | 40 canonical objects; no associations/commerce; validator+loader+11 tests; [SYMBOLIC_ASSET_REGISTRY.md](./SYMBOLIC_ASSET_REGISTRY.md); next D1.2.
- 2026-06-01 | Backend / Contract | Branch D1.2 Symbolic Asset Association Registry | DONE | 88 contextual links; cross-ref D1.1+B1.1+C1.1+C1.6+E1.5; no recommendations; [SYMBOLIC_ASSET_ASSOCIATION_REGISTRY.md](./SYMBOLIC_ASSET_ASSOCIATION_REGISTRY.md); next D1.3.
- 2026-06-01 | Backend / Contract | Branch D1.3 Symbolic Collection Registry | DONE | 16 curated collections; cross-ref D1.1+D1.2; no shop/commerce; [SYMBOLIC_ASSET_COLLECTION_REGISTRY.md](./SYMBOLIC_ASSET_COLLECTION_REGISTRY.md); next D1.4.
- 2026-06-01 | Backend / Contract | Branch D1.4 Symbolic Visibility Policy | DONE | B1.13+E1.7→D1.1/D1.3 caps; no recommendation/commerce activation; [SYMBOLIC_VISIBILITY_POLICY.md](./SYMBOLIC_VISIBILITY_POLICY.md); next D1.5.
- 2026-06-01 | Backend / Reference | Branch C1.8 Practice Selection Ranker | DONE | deterministic rank+trace; C1.7+B1.11; 12 tests; [PRACTICE_SELECTION_RANKER.md](./PRACTICE_SELECTION_RANKER.md); next FIRST_DAY_DOD_GAP_ANALYSIS.
- 2026-06-01 | Backend / Reference | Branch C1.7 Practice Context Association Registry | DONE | 120 context→practice edges; 5 negative; validator+loader+16 tests; [PRACTICE_CONTEXT_ASSOCIATION_REGISTRY.md](./PRACTICE_CONTEXT_ASSOCIATION_REGISTRY.md).
- 2026-06-01 | Product / Architecture | Generation order & budget canon | DONE | 7-step foundation path; 0–2 LLM/day Today; evening separate; cache horoscope/tarot/month; [API_MEMORY_AND_LEARNING_LAYER.md](./API_MEMORY_AND_LEARNING_LAYER.md).
- 2026-06-01 | Product / Architecture | Reference Inventory & Consumption Map | DONE | Per-domain CD counts, prod vs tests readers, Today wire constraints; [REFERENCE_INVENTORY_AND_CONSUMPTION_MAP.md](./REFERENCE_INVENTORY_AND_CONSUMPTION_MAP.md); wire paused → enrichment first.
- 2026-06-01 | Product / Architecture | System Map & Data Flow | DONE | Unified A–E+P map; runtime + LLM chains; Today slice; stop rules; freeze new branches; [DATA_OWNERSHIP_AND_CONSUMPTION_MAP.md](./DATA_OWNERSHIP_AND_CONSUMPTION_MAP.md); next Today vertical slice.
- 2026-06-01 | Product / Architecture | Surface Layer S1.1 Today Intelligence Read Model | DONE | Projection spec; builder + validator; no prod consumer yet; [SCREEN_CONTRACTS_V1.md](./SCREEN_CONTRACTS_V1.md).
- 2026-06-01 | Product / Architecture | Surface Layer S1.0 Read Model Ontology | DONE | Five read-only surfaces over A–E; policy stack; no commerce/LLM/mutations; [PRODUCT_SURFACE_READ_MODEL_ONTOLOGY.md](./PRODUCT_SURFACE_READ_MODEL_ONTOLOGY.md); next S1.1 Today.
- 2026-06-01 | Backend / Contract | Branch D1.5 Symbolic Commerce Separation | DONE | SKU→asset refs only; separation policy; Branch D complete; [SYMBOLIC_COMMERCE_SEPARATION_LAYER.md](./SYMBOLIC_COMMERCE_SEPARATION_LAYER.md).
- 2026-06-01 | Backend / Contract | Branch E1.7 Calendar Consumer Policies | DONE | B1.12→E visibility caps; redact/block artifacts; [CALENDAR_INTELLIGENCE_CONSUMER_POLICIES.md](./CALENDAR_INTELLIGENCE_CONSUMER_POLICIES.md); Branch E complete.
- 2026-06-01 | Backend / Contract | Branch E1.6 Calendar Knowledge/Evolution Bridge | DONE | pattern→knowledge candidate + progression context; no stage/profile/memory; [CALENDAR_KNOWLEDGE_EVOLUTION_BRIDGE.md](./CALENDAR_KNOWLEDGE_EVOLUTION_BRIDGE.md); next E1.7.
- 2026-06-01 | Backend / Contract | Branch E1.5 Rhythm Pattern Confirmation Gate | DONE | candidate→pattern gate; no insight/recommendation; [CALENDAR_RHYTHM_PATTERN_CONFIRMATION.md](./CALENDAR_RHYTHM_PATTERN_CONFIRMATION.md); next E1.6.
- 2026-06-01 | Backend / Contract | Branch E1.4 Rhythm Pattern Candidate | DONE | detect repetition signals; threshold gate; no confirmation/recommendation; [CALENDAR_RHYTHM_PATTERN_CANDIDATE_CONTRACT.md](./CALENDAR_RHYTHM_PATTERN_CANDIDATE_CONTRACT.md); next E1.5.
- 2026-06-01 | Backend / Contract | Branch E1.3 Calendar Month Map Contract | DONE | aggregate day records; no inference; [CALENDAR_MONTH_MAP_CONTRACT.md](./CALENDAR_MONTH_MAP_CONTRACT.md); next E1.4.
- 2026-06-01 | Backend / Contract | Branch E1.2 Calendar Signal Ingestion | DONE | verified artifacts → day record marks; idempotent; [CALENDAR_SIGNAL_INGESTION.md](./CALENDAR_SIGNAL_INGESTION.md); next E1.3.
- 2026-06-01 | Backend / Contract | Branch E1.1 Calendar Day Record Contract | DONE | user×date atom; refs/facts only; [CALENDAR_DAY_RECORD_CONTRACT.md](./CALENDAR_DAY_RECORD_CONTRACT.md); next E1.2.
- 2026-06-01 | Product / Architecture | Branch E1.0 Calendar Intelligence Ontology | DONE | archive + rhythm engine; entities only; [CALENDAR_INTELLIGENCE_ONTOLOGY.md](./CALENDAR_INTELLIGENCE_ONTOLOGY.md); next E1.1.
- 2026-06-01 | Backend / Contract | Branch B1.14 Evolution Consumer Metrics | DONE | read-only observability; all 6 consumers; [EVOLUTION_CONSUMER_METRICS.md](./EVOLUTION_CONSUMER_METRICS.md); Branch B wiring complete.
- 2026-06-01 | Backend / Contract | Branch B1.13 Evolution → Commerce Visibility Policy | DONE | visibility only; no targeting/recommendation; [EVOLUTION_COMMERCE_VISIBILITY_POLICY.md](./EVOLUTION_COMMERCE_VISIBILITY_POLICY.md); next B1.14.
- 2026-06-01 | Backend / Contract | Branch B1.12 Evolution → Calendar Runtime Policy | DONE | depth/visibility cap only; no insights; [EVOLUTION_CALENDAR_RUNTIME_POLICY.md](./EVOLUTION_CALENDAR_RUNTIME_POLICY.md); next B1.13.
- 2026-06-01 | Backend / Contract | Branch B1.11 Evolution → Practice Selector Filter | DONE | cap/filter only; no final selection; [EVOLUTION_PRACTICE_SELECTOR_FILTER.md](./EVOLUTION_PRACTICE_SELECTOR_FILTER.md); next B1.12.
- 2026-06-01 | Backend / Contract | Branch B1.10 Evolution Day Presentation Envelope | DONE | presentation envelope only; DayModel unchanged; [EVOLUTION_DAY_PRESENTATION_ENVELOPE.md](./EVOLUTION_DAY_PRESENTATION_ENVELOPE.md); next B1.11.
- 2026-06-01 | Backend / Contract | Branch B1.9 Evolution → Context Selector Wiring | DONE | cap-only AK/memory/context limits; no force-expand; [EVOLUTION_CONTEXT_SELECTOR_WIRING.md](./EVOLUTION_CONTEXT_SELECTOR_WIRING.md); next B1.10.
- 2026-06-01 | Backend / Contract | Branch B1.8 Evolution → LLM Gate Wiring | DONE | cap-only slice wire-in; no force-call; [EVOLUTION_LLM_GATE_WIRING.md](./EVOLUTION_LLM_GATE_WIRING.md); next B1.9.
- 2026-06-01 | Backend / Contract | Branch B1.7 Evolution Effect Consumer Map | DONE | six consumers; slice-only read; no full policy; [EVOLUTION_EFFECT_CONSUMER_MAP.md](./EVOLUTION_EFFECT_CONSUMER_MAP.md).
- 2026-06-01 | Backend / Contract | Branch B1.6 Evolution Effect Runtime Policy | DONE | B1.5→allowed/blocked effects; gate-gated unlocks; no promotion/commerce activation; [EVOLUTION_EFFECT_RUNTIME_POLICY.md](./EVOLUTION_EFFECT_RUNTIME_POLICY.md); next B1.7.
- 2026-06-01 | Backend / Contract | Branch C2.4 Runtime Signal Metrics | DONE | read-only counts/distributions; window-scoped; [PRACTICE_RUNTIME_SIGNAL_METRICS.md](./PRACTICE_RUNTIME_SIGNAL_METRICS.md); unblocks B1.6.
- 2026-06-01 | Backend / Contract | Branch C2.3 Practice Runtime Trace Map | DONE | audit layer event→ES; read-only; snapshot ref helpers; [PRACTICE_RUNTIME_TRACE_MAP.md](./PRACTICE_RUNTIME_TRACE_MAP.md); next C2.4.
- 2026-06-01 | Backend / Contract | Branch C2.2 Runtime Event→Emission Bridge | DONE | event→emission→B1.3; ascetic blocked; trace IDs; [PRACTICE_RUNTIME_EVENT_EMISSION_BRIDGE.md](./PRACTICE_RUNTIME_EVENT_EMISSION_BRIDGE.md); next C2.3.
- 2026-06-01 | Backend / Contract | Branch C2.1 Practice Runtime Event Contracts | DONE | six event kinds; validators; C2.0 path check; ascetic pending-only; [PRACTICE_RUNTIME_EVENT_CONTRACT.md](./PRACTICE_RUNTIME_EVENT_CONTRACT.md); next C2.2.
- 2026-06-01 | Backend / Contract | Branch C2.0 Practice Runtime Signal Emitter | DONE | CD→B1.3 bridge; no promotion/state/score; ascetic blocked; [PRACTICE_RUNTIME_SIGNAL_EMITTER_CONTRACT.md](./PRACTICE_RUNTIME_SIGNAL_EMITTER_CONTRACT.md); next C2.1.
- 2026-06-01 | Product / Architecture | Branch C Practice System — CD complete C1.0–C1.6 | DONE | all six entity registries; [status/branch_c_practice_system.md](./status/branch_c_practice_system.md); runtime emitters next.
- 2026-06-01 | Backend / Reference | Branch C1.6 Cycle Definition Registry | DONE | 8 temporal programs; components C1.1–C1.5; [CYCLE_REGISTRY.md](./CYCLE_REGISTRY.md).
- 2026-06-01 | Backend / Reference | Branch C1.5 Ritual Definition Registry | DONE | 8 containers; components → C1.1/C1.2/C1.4; [RITUAL_REGISTRY.md](./RITUAL_REGISTRY.md); next C1.6 Cycle.
- 2026-06-01 | Backend / Reference | Branch C1.4 Ascetic Definition Registry | DONE | 10 restrictions; produces_signals empty; safety rules; [ASCETIC_REGISTRY.md](./ASCETIC_REGISTRY.md); next C1.5 Ritual.
- 2026-06-01 | Backend / Reference | Branch C1.3 Goal Definition Registry | DONE | 10 outcomes; weekly/milestone/long_horizon; produces_signals → B1.3; [GOAL_REGISTRY.md](./GOAL_REGISTRY.md); next C1.4 Ascetic.
- 2026-06-01 | Backend / Reference | Branch C1.2 Habit Definition Registry | DONE | 10 habits → C1.1; produces_signals → B1.3; [HABIT_REGISTRY.md](./HABIT_REGISTRY.md); next C1.3 Goal.
- 2026-06-01 | Backend / Reference | Branch C1.1 Practice Definition Registry | DONE | 10 action types; produces_signals → B1.3; not content/variants; [PRACTICE_REGISTRY.md](./PRACTICE_REGISTRY.md); next C1.2 Habit.
- 2026-06-01 | Product / Architecture | Branch C1.0 Practice Ontology | DONE | Practice, Habit, Goal, Ascetic, Ritual, Cycle; signal map to B1.3; [PRACTICE_ONTOLOGY.md](./PRACTICE_ONTOLOGY.md); next C1.1.
- 2026-06-01 | Backend / Reference | Branch B1.5 Evolution Product Effects Registry | DONE | per-stage intelligence/engine/unlock/commerce effects; [EVOLUTION_PRODUCT_EFFECTS_REGISTRY.md](./EVOLUTION_PRODUCT_EFFECTS_REGISTRY.md); next Branch C.
- 2026-06-01 | Product | Phase 3 Core Loop Viability Test | ACTIVE | [CORE_LOOP_VIABILITY_TEST.md](./CORE_LOOP_VIABILITY_TEST.md): experiment not UI; Variant A/B; instrument=G1-surface; freeze enrichment until verdict.
- 2026-06-01 | Product / Web | G1-surface instrument | DONE | `/today?core_loop=1` / `?first=1`: Theme+Action+Progress без ritual gate; Test B rubric §6.3 + anti-cheat §4.
- 2026-06-01 | Product | Test B pulse 1 procedure | DONE | [CORE_LOOP_VIABILITY_TEST.md](./CORE_LOOP_VIABILITY_TEST.md) v1.2: 2–3 users; Q4 commit; S1–S4; F1–F4 breakpoints; no iOS/checklist before pulse 1.
- 2026-06-01 | Product | Profile serves Today canon | DONE | PROFILE_SCREEN_ARCHITECTURE §0.1; Identity=Operating Manual; exploration ≠ core.
- 2026-06-01 | Product | Phase 1 partial accept v0.2 | ACTIVE | Traits-first; 28 canon ✅; archetypes/formula ⬜; validation backlog.
- 2026-06-01 | Product | Profile cards 1–6 accept v1.11 | DONE | Card 6 portrait; all cards closed.
- 2026-06-01 | Product | Card 6 three axes v1.10 | DONE | superseded by v1.11 portrait UX.
- 2026-06-01 | Product | L1 Profile Cards spec v1.8 | DONE | review gate; engineering paused.
- 2026-06-01 | Product | Profile Data Inventory v1.0 | DONE | PROFILE_DATA_INVENTORY.md: 5 source layers; per-element table; before screen wire.
- 2026-06-01 | Product | Profile user cards v1.7 | DONE | 8 cards §3.1; screen canon parked until data inventory accepted.
- 2026-06-01 | Product | Explain Meaning v1.1 voice ban | DONE | EXPLAIN_MEANING_NOT_MECHANISM: four copy types; system/algorithm ban; Profile unveiling; gamification metaphors.
- 2026-06-01 | Product | Profile three-entity split | DONE | PROFILE_SCREEN_ARCHITECTURE §0.3; interest nav §4.1; GPS §0.1 two scales.
- 2026-06-01 | Product | SCREEN_BLOCK_DEFINITION v1.5 | ACTIVE | Interest tiles Day 1; I/R/D chips; system blocks ≠ layout.
- 2026-06-01 | Product | Profile Identity v1.4 | ACTIVE | Operating Manual question; Today-serving trait filter.
- 2026-06-01 | Product | Profile block definition v1.2 | DONE | Foundation→I/I/R/D Day 1; pipeline §2.1.
- 2026-06-01 | Product / Architecture | Profile Build Pipeline v1.1 | DONE | Predictability; canon matrix §6; LLM allow/deny.
- 2026-06-01 | Product | Minimal Cycle Viability gate | DONE | [MINIMAL_CYCLE_VIABILITY.md](./MINIMAL_CYCLE_VIABILITY.md) → pointer to Core Loop test.
- 2026-06-01 | Product / Architecture | Decision Source of Truth Map | DONE | [DECISION_PIL_MAP.md](./DECISION_PIL_MAP.md).
- 2026-06-01 | Product | Block Data Requirements | DONE | [BLOCK_DATA_REQUIREMENTS.md](./BLOCK_DATA_REQUIREMENTS.md): by user decision D1–D28; min/enrich/forbidden; Day1/7/30 maturity matrix.
- 2026-06-01 | Product | Screen Block Purposes | DONE | [SCREEN_BLOCK_PURPOSES.md](./SCREEN_BLOCK_PURPOSES.md): 52 sections → user decision; existence audit.
- 2026-06-01 | Product | Screen Content Map pass 1 | DONE | [SCREEN_CONTENT_MAP.md](./SCREEN_CONTENT_MAP.md): sections for all 9 screens; cross-screen index §10.
- 2026-06-01 | Product | TC-D Core Trait Definition | DONE | Admission criterion + Card 1 phrasing test; before TC0 catalog; [PROFILE_TODAY_DOMAIN_INVENTORY.md](./PROFILE_TODAY_DOMAIN_INVENTORY.md) v2.4.
- 2026-06-01 | Product | T0 Hybrid C accepted | DONE | Core/Love/Money/Operating as separate domains; not compromise; [PROFILE_TODAY_DOMAIN_INVENTORY.md](./PROFILE_TODAY_DOMAIN_INVENTORY.md) v2.3.
- 2026-06-01 | Product | TC0 Foundation Catalog №1 | DONE | 10S+5W Core; control→Love; 28-label routing locked; [DOMAIN_PHASE1](./DOMAIN_PHASE1_ARCHETYPES_AND_TRAITS.md) §4.
- 2026-06-01 | Product | TC2-A Output Model Variant B | DONE | CoreTraitProfile 15 scores; top-3 projection; [DOMAIN_PHASE1](./DOMAIN_PHASE1_ARCHETYPES_AND_TRAITS.md) §5.1.
- 2026-06-01 | Product | TC2-B scoring model v0.1 | ACTIVE | Rule-based additive; 5 rules; batches B1–B5; [DOMAIN_PHASE1](./DOMAIN_PHASE1_ARCHETYPES_AND_TRAITS.md) §5.2.
- 2026-06-01 | Product | TC2-B1 sign layer | DONE | Element+modality; Water empathy/depth +2; SIGN_LAYER_CAP=3; [DOMAIN_PHASE1](./DOMAIN_PHASE1_ARCHETYPES_AND_TRAITS.md) §5.2.1.
- 2026-06-01 | Product | Product Data Inventory v1.0 | SIGNED | Registry 87 rows; task closed; [PRODUCT_DATA_INVENTORY.md](./PRODUCT_DATA_INVENTORY.md).
- 2026-06-01 | Product | Profile Pass C Data Binding v0.2 | SIGNED | Seven CDs; gaps G1–G6 resolved; [PROFILE_DATA_BINDING.md](./PROFILE_DATA_BINDING.md).
- 2026-06-01 | Product | Profile Coherence Rule v0.1 | SIGNED | Card 1 identity source; 3/4/6 projections; Foundation→Projection→Narrative; [PROFILE_COHERENCE.md](./PROFILE_COHERENCE.md).
- 2026-06-01 | Design | TodayFlow Foundation UI | ACTIVE | [TODAYFLOW_FOUNDATION_UI.md](./TODAYFLOW_FOUNDATION_UI.md): Figma TODAYFLOW_FOUNDATION_UI — Hero L/M/S, Symbols, Geometry, Surfaces A-D, Typography, Colors; textless premium test; draft `todayflow-foundation.css` |
- 2026-06-01 | Product | Profile Screen Master | **ACTIVE** | Foundation code sign-off done; v0 Phase 2 entities + taxonomy audit remain · prod = Quick Map |
- 2026-06-01 | Product | Meta doc chain | PAUSED | No new product docs; Figma is deliverable |
- 2026-06-01 | Web | Profile sprint: Who scene + sphere objects | DONE | Who=L1 archetype+chips, expand=why only; Love/Money visual objects; desktop 2-col; scroll rhythm widths |
- 2026-06-01 | Product | Foundation Domain Registry | FROZEN | After data inventory; TC2-B/Love/domain priority paused.
- 2026-06-01 | Product | Foundation Domain Registry v2.0 | SUPERSEDED | by v2.1 DoD.
- 2026-06-01 | Product | Love Domain Card 3 scope | ACTIVE | LD-D→LD-2 before scoring; [LOVE_DOMAIN_CARD.md](./LOVE_DOMAIN_CARD.md).
- 2026-06-01 | Product | TC2-B scoring | PAUSED | Resume after Foundation map; B1 sign layer done.
- 2026-06-01 | Product | TC2-B2 Life path LP 1-3 | CANCELLED | Superseded by Foundation map pause.
- 2026-06-01 | Product | TC1.75 Trait Coverage PASS | DONE | 0 Unsupported; Weak confidence ceiling; [DOMAIN_PHASE1](./DOMAIN_PHASE1_ARCHETYPES_AND_TRAITS.md) §5.075.
- 2026-06-01 | Product | TC0 revision pass 2 | DONE | Core 10S+5W; superseded by TC0 sign-off.
- 2026-06-01 | Product | T0 hybrid domain model stop | DONE | Core vs Love/Money/Operating; before TC0; [PROFILE_TODAY_DOMAIN_INVENTORY.md](./PROFILE_TODAY_DOMAIN_INVENTORY.md) v2.2.
- 2026-06-01 | Product / Architecture | Profile Source of Truth Map | DONE | [PROFILE_PIL_MAP.md](./PROFILE_PIL_MAP.md): preserved; step 5 of screen-first canon.
- 2026-06-01 | Product / Architecture | Profile Readiness Audit | DONE | [PROFILE_READINESS_AUDIT.md](./PROFILE_READINESS_AUDIT.md): 7-block existence audit; Identity+Intent+Reality sufficient; empty blocks policy.
- 2026-06-02 | Product | Today Step B — ownership map | DONE | [TODAY_OWNERSHIP_MAP.md](./status/TODAY_OWNERSHIP_MAP.md) · DayModel vs User State vs Action Foundation; compass gaps → Today.
- 2026-06-02 | Product / Frontend | Today Step A — canon vs code diff | DONE | [TODAY_CANON_VS_CODE_DIFF.md](./status/TODAY_CANON_VS_CODE_DIFF.md) · ritual-first ≠ Theme→Action→Progress.
- 2026-06-02 | Product / Frontend | Profile v0 content-stable + visual QA | DONE | 29/31 unique · 2 compass gaps deferred · [PROFILE_V0_VISUAL_QA.md](./status/PROFILE_V0_VISUAL_QA.md) · UI audit tests.
- 2026-06-02 | Product / Frontend | Profile v0 taxonomy slots + Igor audit table | DONE | `buildProfileV0TaxonomySlots` · [PROFILE_V0_IGOR_TAXONOMY_AUDIT.md](./status/PROFILE_V0_IGOR_TAXONOMY_AUDIT.md).
- 2026-06-01 | Product / Frontend | Profile v0 taxonomy gate (category ≠ count) | DONE | `profileInsightTaxonomy.ts` · superseded by slot pipeline.
- 2026-06-01 | Product / Frontend | Profile v0: Name killed, Social Mirror + insight budget 31 | DONE | Structural pass in web; taxonomy gate supersedes count-only QA.
- 2026-06-01 | Product / Architecture | Core User Loop canon | DONE | [CORE_USER_LOOP.md](./CORE_USER_LOOP.md): Theme→Action→Progress as main product object; domain matrix; branches A–E as loop feeders; pause enrichment until loop proof.
- 2026-06-01 | Product / Architecture | First Today Success Criteria v2 | DONE | [FIRST_DAY_EXPERIENCE.md](./FIRST_DAY_EXPERIENCE.md): action not feeling; one-sentence test; Test A/B; backend conditional pass / UX fail.
- 2026-06-01 | Product / Architecture | First Day execution lock P0.1–P0.3 | ACTIVE | Gap analysis v1.1; G5 Why deferred; freeze C1.7/registries.
- 2026-06-01 | Product / Architecture | First Day DoD gap analysis | DONE | [FIRST_DAY_EXPERIENCE.md](./FIRST_DAY_EXPERIENCE.md): model vs web/iOS/backend audit; P0 gaps G1–G5 mapped; three data kinds Foundation/Causal/Product.
- 2026-06-01 | Product / Architecture | First Day Experience + Today model v1.1 | DONE | [FIRST_DAY_EXPERIENCE.md](./FIRST_DAY_EXPERIENCE.md): 30s path Profile(1–3)→First Today→Daily Loop, MVP blocks without Knowledge/Evolution/Calendar/ME; [TODAY_PRODUCT_MODEL.md](./TODAY_PRODUCT_MODEL.md) v1.1: Progress mandatory in package, Why layer (selected/filtered/blocked); freeze C1.7/new registries/API until First Day DoD.
- 2026-06-01 | Product / Architecture | Profile + Today product models (воронки) | DONE | [PROFILE_PRODUCT_MODEL.md](./PROFILE_PRODUCT_MODEL.md): 4-layer profile funnel (Identity→Intent→Reality→Behavior), блоки экрана, обязательность; [TODAY_PRODUCT_MODEL.md](./TODAY_PRODUCT_MODEL.md): 6-stage day funnel, Today Package (Theme/Insight/Action/Reflection/Symbolic), UI↔data map, logical request sequence; no new API contracts.
- 2026-06-01 | Backend / Reference | Branch B1.4 Evolution Score / ECC Integration | DONE | read-only ES; B1.3→B1.2 path; no API/promotion; [EVOLUTION_SCORE_INTEGRATION.md](./EVOLUTION_SCORE_INTEGRATION.md); next B1.5.
- 2026-06-01 | Backend / Reference | Branch B1.3 Progression Signal Contract | DONE | registry + `progression_signal_v1`; eligibility aggregation; [PROGRESSION_SIGNAL_CONTRACT.md](./PROGRESSION_SIGNAL_CONTRACT.md); next B1.4 ECC.
- 2026-06-01 | Backend / Reference | Branch B1.2 Evolution User State Contract | DONE | `evolution_user_state_v1`; eligibility snapshot; no promotion; [EVOLUTION_USER_STATE_CONTRACT.md](./EVOLUTION_USER_STATE_CONTRACT.md); next B1.3 signals.
- 2026-06-01 | Backend / Reference | Branch B1.1 Evolution CD Reference Tables | DONE | 7 stages, 10 path themes, 6 stage gates; loader + validator; [EVOLUTION_CD_REFERENCE.md](./EVOLUTION_CD_REFERENCE.md); next B1.2 user state.
- 2026-06-01 | Product / Architecture | Branch B1.0.1 Evolution Hierarchy & Ownership | DONE | Stage primary axis; parallel paths; stage gates ≠ achievements; engine ownership; [EVOLUTION_HIERARCHY_AND_OWNERSHIP.md](./EVOLUTION_HIERARCHY_AND_OWNERSHIP.md); prerequisite for B1.1.
- 2026-06-01 | Product / Architecture | Branch B1.0 Evolution Entity Registry | DONE | stages, paths, cycles, milestones, gates, signals, unlocks; no UI/API; [EVOLUTION_ENTITY_REGISTRY.md](./EVOLUTION_ENTITY_REGISTRY.md); next B1.0.1 hierarchy.
- 2026-06-01 | Product / Architecture | Branch A Knowledge Usage Layer — architecture closed | ACTIVE | A1.1–A1.8; A1.8 partial until AK pool from promotion; log criteria — [status/branch_a_knowledge_usage_layer.md](./status/branch_a_knowledge_usage_layer.md); next Branch B.
- 2026-06-01 | Backend / Reference | Branch A1.8 Hot Path Wiring | DONE | `user_active_knowledge` DB; loader; `build_today_narrative` + metrics log; [KNOWLEDGE_HOT_PATH_WIRING.md](./KNOWLEDGE_HOT_PATH_WIRING.md); ops: promotion persist.
- 2026-05-31 | Backend / Reference | Branch A1.7 Knowledge Usage Metrics & Trace | DONE | `knowledge_usage_metrics_trace_v1`; DayContext + P1.9 enrich; 7 tests; [KNOWLEDGE_USAGE_METRICS.md](./KNOWLEDGE_USAGE_METRICS.md); next hot path.
- 2026-05-31 | Backend / Reference | Branch A1.5–A1.6 Personalization Usage Gate + P1.9 wire | DONE | `try_decide_personalization_usage_v1()`; `maybe_build_llm_context_slice_v1(..., day_context_layers=...)`; 12+4 tests; [PERSONALIZATION_USAGE_GATE.md](./PERSONALIZATION_USAGE_GATE.md); next A1.7 metrics.
- 2026-05-31 | Backend / Reference | Branch A1.4 Profile Knowledge Personalization | DONE | Context Slice → safe_personalization_summary; Profile Selector enrichment; DayContext hook; 12 tests; [PROFILE_KNOWLEDGE_PERSONALIZATION.md](./PROFILE_KNOWLEDGE_PERSONALIZATION.md); next A1.5 usage gate.
- 2026-05-31 | Backend / Reference | Branch A1.3 Day Engine Knowledge Wiring | DONE | `try_apply_day_engine_knowledge_v1()`; guide_decision knowledge_hints layer; DayContext opt-in; 13 tests; [status/knowledge_context_selection_a1_3.md](./status/knowledge_context_selection_a1_3.md); next A1.4 Profile Selector.
- 2026-05-31 | Backend / Reference | Branch A1.2 Day Engine Knowledge Integration | DONE | `try_build_day_engine_knowledge_input_v1()`; hint channels; advisory-only; 14 tests; [DAYENGINE_KNOWLEDGE_INTEGRATION.md](./DAYENGINE_KNOWLEDGE_INTEGRATION.md); next A1.3 Day Engine wiring.
- 2026-05-31 | Backend / Reference | Branch A1.1 Knowledge Context Selection | DONE | `select_knowledge_context_v1()`; freshness layer (`last_confirmed_at`); soft cap 3 / hard cap 5; conflict resolution; 10 tests; [status/knowledge_context_selection_a1_1.md](./status/knowledge_context_selection_a1_1.md); next A1.2 Profile Selector wire.
- 2026-05-31 | Product / Architecture | Branch A1.0 Knowledge Context Selection canon | DONE | [KNOWLEDGE_CONTEXT_SELECTION_SYSTEM.md](./KNOWLEDGE_CONTEXT_SELECTION_SYSTEM.md): Knowledge Selector → Context Selector → Slice; before Day Engine/LLM budget; next A1.1 builder.
- 2026-05-31 | Product / Architecture | Learning infrastructure scope freeze at P1.27 | ACTIVE | P1.28+ deferred; priority → Knowledge Usage, Evolution, Practice, Symbolic Assets, Calendar Intelligence; [API_MEMORY_AND_LEARNING_LAYER.md](./API_MEMORY_AND_LEARNING_LAYER.md).
- 2026-05-31 | Backend / Reference | P1.27 training dataset registry | DONE | `try_register_training_example_v1()`; scaffold frozen; next product branches A–E per freeze doc.
- 2026-05-31 | Backend / Reference | P1.26 dataset candidate promotion gate | DONE | `try_promote_dataset_candidate_v1()`; day_training_example_approval_v1; evidence/review gates; training_use_allowed=true only when approved; `test_day_model_v1_training_example_approval.py` (10); [DAYMODEL_TRAINING_EXAMPLE_APPROVAL.md](./DAYMODEL_TRAINING_EXAMPLE_APPROVAL.md); next P1.27 dataset registry.
- 2026-05-31 | Backend / Reference | P1.25 hint application dataset policy | DONE | `try_build_hint_application_dataset_policy_v1()`; candidate/runtime_trace_only/rejected; training_use_allowed=false; `test_day_model_v1_hint_application_dataset_policy.py` (10); [DAYMODEL_HINT_APPLICATION_DATASET_POLICY.md](./DAYMODEL_HINT_APPLICATION_DATASET_POLICY.md); next P1.26 promotion gate.
- 2026-05-31 | Backend / Reference | P1.24 hint package application contract | DONE | `try_apply_hint_package_v1()`; consumer compatibility; before/after trace; no mutation; `test_day_model_v1_hint_application.py` (11); [DAYMODEL_HINT_APPLICATION.md](./DAYMODEL_HINT_APPLICATION.md); next P1.25 application audit.
- 2026-05-31 | Backend / Reference | P1.23 active knowledge hint package | DONE | `try_build_active_knowledge_hint_package_v1()`; usage→hint_type mapping; applied=false; no application; `test_day_model_v1_active_knowledge_hint_package.py` (11); [DAYMODEL_ACTIVE_KNOWLEDGE_HINT_PACKAGE.md](./DAYMODEL_ACTIVE_KNOWLEDGE_HINT_PACKAGE.md); next P1.24 hint application.
- 2026-05-31 | Backend / Reference | P1.22 active knowledge runtime gate | DONE | `try_decide_active_knowledge_runtime_v1()`; surface compatibility; allow/deny only; `test_day_model_v1_active_knowledge_runtime_gate.py` (11); [DAYMODEL_ACTIVE_KNOWLEDGE_RUNTIME_GATE.md](./DAYMODEL_ACTIVE_KNOWLEDGE_RUNTIME_GATE.md); next P1.23 hint package.
- 2026-05-31 | Backend / Reference | P1.21 active knowledge usage policy | DONE | `try_build_active_knowledge_usage_policy_v1()`; allowed/forbidden usages; max influence low/medium; `test_day_model_v1_active_knowledge_usage_policy.py` (12); [DAYMODEL_ACTIVE_KNOWLEDGE_USAGE_POLICY.md](./DAYMODEL_ACTIVE_KNOWLEDGE_USAGE_POLICY.md); next P1.22 runtime gate.
- 2026-05-31 | Backend / Reference | P1.20 active knowledge confirmation gate | DONE | `try_activate_knowledge_from_candidate_v1()`; strict gate; Active Knowledge≠Profile; `test_day_model_v1_active_knowledge.py` (12); [DAYMODEL_ACTIVE_KNOWLEDGE.md](./DAYMODEL_ACTIVE_KNOWLEDGE.md); next P1.21 usage policy.
- 2026-05-31 | Backend / Reference | P1.19 knowledge candidate from pattern | DONE | `try_build_knowledge_candidate_from_pattern_v1()`; machine-readable claims; no active knowledge; `test_day_model_v1_knowledge_candidate.py` (10); [DAYMODEL_KNOWLEDGE_CANDIDATE.md](./DAYMODEL_KNOWLEDGE_CANDIDATE.md); next P1.20 confirmation gate.
- 2026-05-31 | Backend / Reference | P1.18 pattern confirmation gate | DONE | `try_confirm_pattern_from_candidate_v1()`; gate re-checks promotion_eligible; confirmed/not_ready/conflicted/rejected; `test_day_model_v1_confirmed_pattern.py` (11); [DAYMODEL_PATTERN_CONFIRMATION_GATE.md](./DAYMODEL_PATTERN_CONFIRMATION_GATE.md); next P1.19 knowledge candidate.
- 2026-05-31 | Product / Architecture | Knowledge Promotion Ladder canon | DONE | [USER_KNOWLEDGE_MODEL.md](./USER_KNOWLEDGE_MODEL.md): Signal→Candidate→Pattern→Knowledge→Profile; Pattern Candidate≠Pattern; no skip steps.
- 2026-05-31 | Backend / Reference | P1.17 pattern candidate aggregation | DONE | `try_aggregate_pattern_candidate_v1()`; promotion_eligible gate; no Pattern/memory/profile; `test_day_model_v1_pattern_candidate.py` (10); [DAYMODEL_PATTERN_CANDIDATE_AGGREGATION.md](./DAYMODEL_PATTERN_CANDIDATE_AGGREGATION.md).
- 2026-05-31 | Backend / Reference | P1.16 reaction → learning signal mapping | DONE | `build_day_surface_learning_signal_v1()`; all reaction types mapped; memory/ranking flags false; `test_day_model_v1_surface_learning_signal.py` (12); [DAYMODEL_LEARNING_SIGNAL_MAPPING.md](./DAYMODEL_LEARNING_SIGNAL_MAPPING.md); next P1.17 aggregation policy.
- 2026-05-31 | Backend / Reference | P1.15 user exposure & reaction contract | DONE | `build_day_surface_exposure_v1()` + `build_day_surface_reaction_v1()`; raw weights; audit→exposure→reaction; `test_day_model_v1_surface_exposure_reaction.py` (10); [DAYMODEL_USER_EXPOSURE_REACTION.md](./DAYMODEL_USER_EXPOSURE_REACTION.md); next P1.16 learning signal mapping.
- 2026-05-31 | Backend / Reference | P1.14 surface candidate audit record | DONE | `build_day_surface_candidate_audit_v1()`; hash/id derivation; [DAYMODEL_SURFACE_CANDIDATE_AUDIT.md](./DAYMODEL_SURFACE_CANDIDATE_AUDIT.md); next P1.15 exposure/reaction.
- 2026-05-31 | Backend / Reference | P1.13 surface candidate selection | DONE | `select_day_surface_candidate_v1()`; deterministic/llm/blocked; threshold 0.75; `test_day_model_v1_surface_candidate.py` (10); [DAYMODEL_SURFACE_CANDIDATE_SELECTION.md](./DAYMODEL_SURFACE_CANDIDATE_SELECTION.md); next P1.14 audit record.
- 2026-05-31 | Backend / Reference | P1.12 LLM response evaluation + post-call | DONE | `evaluate_day_llm_response_v1()`; post-call enrichment; used_in_ui=false; `test_day_model_v1_llm_response_evaluation.py` (10); [DAYMODEL_LLM_RESPONSE_EVALUATION.md](./DAYMODEL_LLM_RESPONSE_EVALUATION.md); next P1.13 surface selection.
- 2026-05-31 | Backend / Reference | P1.11 LLM response validator contract | DONE | `validate_day_llm_refinement_response_v1()`; valid/invalid + issues; `test_day_model_v1_llm_refinement_response.py` (12); [DAYMODEL_LLM_RESPONSE_CONTRACT.md](./DAYMODEL_LLM_RESPONSE_CONTRACT.md); next P1.12 post-call integration.
- 2026-05-31 | Backend / Reference | P1.10 LLM prompt template contract | DONE | registry + `build_day_llm_prompt_v1()`; refinement-only; `test_day_model_v1_llm_prompt.py` (10); [DAYMODEL_PROMPT_TEMPLATE_CONTRACT.md](./DAYMODEL_PROMPT_TEMPLATE_CONTRACT.md); next P1.11 Response Validator.
- 2026-05-31 | Backend / Reference | P1.9 LLM context slice contract | DONE | `build_llm_context_slice_v1()`; depth none/minimal/standard; no profile; `test_day_model_v1_llm_context_slice.py` (10); [DAYMODEL_CONTEXT_SLICE_CONTRACT.md](./DAYMODEL_CONTEXT_SLICE_CONTRACT.md); next P1.10 Prompt Template.
- 2026-05-31 | Backend / Reference | P1.8 LLM request record contract | DONE | pre/post-call builders; only on call_llm; evaluation hook fields; `test_day_model_v1_llm_request_record.py` (10); [DAYMODEL_LLM_REQUEST_RECORD.md](./DAYMODEL_LLM_REQUEST_RECORD.md); next P1.9 Context Slice.
- 2026-05-31 | Backend / Reference | P1.7 Day content LLM call gate | DONE | `decide_day_content_llm_call_v1()`; no_call/call_llm/blocked; policy meta only; `test_day_model_v1_llm_call_gate.py` (10); [DAYMODEL_LLM_CALL_GATE.md](./DAYMODEL_LLM_CALL_GATE.md); next P1.8 Request Record.
- 2026-05-31 | Backend / Reference | P1.6 Day content renderer contract | DONE | `render_day_content_package_v1()`; surfaces today_hero/guidance/risk/action/tempo/reflection; block→not renderable; `test_day_model_v1_content_renderer.py` (10); [DAYMODEL_RENDERER_CONTRACT.md](./DAYMODEL_RENDERER_CONTRACT.md); next P1.7 LLM Gate.
- 2026-05-31 | Backend / Reference | P1.5 Day content package evaluation | DONE | `evaluate_day_content_package_v1()`; completeness/confidence/conflict/repetition scores; recommendation use/caution/block; `test_day_model_v1_content_evaluation.py` (10); [DAYMODEL_PACKAGE_EVALUATION.md](./DAYMODEL_PACKAGE_EVALUATION.md); next P1.6 Renderer Contract.
- 2026-05-31 | Backend / Reference | P1.4 Day content assembly | DONE | `assemble_day_content_package_v1()`; slots headline/guidance/risk/action/tempo/reflection + metadata; `test_day_model_v1_content_assembly.py` (10); [DAYMODEL_INPUT_CONTRACT.md](./DAYMODEL_INPUT_CONTRACT.md); next P1.5 Evaluation.
- 2026-05-31 | Backend / Reference | P1.3 Day content seed texts | DONE | 37 keys `text_short`/`text_medium` locale en; validator + `resolve_content_entries_from_mapping()`; `test_day_model_v1_content_seed_texts.py` (13); [DAYMODEL_CONTENT_SEED_TEXTS.md](./DAYMODEL_CONTENT_SEED_TEXTS.md); next P1.4 Assembly.
- 2026-05-31 | Backend / Reference | P1.1 DayModel v1 interpretation rules | DONE | `interpret_day_model_v1()`; enums strategy/opportunity/risk/tempo/action/reflection/pressure; rule hits in `reasons`; `test_day_model_v1_interpretation.py` (12); [DAYMODEL_INTERPRETATION_RULES.md](./DAYMODEL_INTERPRETATION_RULES.md); next P1.2 Content Mapping.
- 2026-05-31 | Backend / Reference | P1.0 DayModel v1 multi-source aggregation | DONE | `aggregate_day_model_v1()`; vector 0.4/0.3/0.3; tempo 0.2/0.4/0.4; enum score maps; `test_day_model_v1_multisource.py` (15); [status](./status/day_model_v1_aggregation_p1_0.md); next P1.1 Interpretation Rules.
- 2026-05-31 | Backend / Reference | P0.8 Astrology atomic machine drafts | DONE | [ASTROLOGY_COMPOSITION_MODEL.md](./ASTROLOGY_COMPOSITION_MODEL.md) gate; 39 files; loader + validator; next P0.9.
- 2026-05-31 | Product / Architecture | Astrology Composition Model gate | DONE | [ASTROLOGY_COMPOSITION_MODEL.md](./ASTROLOGY_COMPOSITION_MODEL.md): primary vs derived; atomic-only P0.8; Composition Engine = phase 2.
- 2026-05-31 | Backend / Reference | P0.5 Numerology machine drafts | DONE | 39 files `DATA/reference/numerology/machine/`; loader + validator; next P0.7 AMC (not partial DayModel).
- 2026-05-31 | Backend / Reference | P0.4 DayModel v1 aggregation test (tarot-only) | DONE | `reference_machine_loader.py`, `day_model_v1_aggregator.py`, `test_day_model_v1_aggregation.py`; preview contract `day_model_v1_preview`; no UI/LLM/legacy migration; next P0.5 numerology machine drafts.
- 2026-05-31 | Reference / Tarot | P0.3 Tarot Major machine drafts (22 files) | DONE | `DATA/reference/tarot/machine/00_fool.json` … `21_world.json`; `status: draft`, `version: 0.1.0`; legacy `tarot_major_arcana.json` untouched; validator extended for 22-file gate; next P0.4 DayModel v1 aggregation test.
- 2026-05-31 | Product / Architecture | Reference Machine Contract JSON Schema v1 (P0.2) | DONE | `docs/schemas/reference_machine_contract_v1.schema.json`, fixtures, `scripts/validate_reference_machine_contract.py`, CI job `reference-machine-contract-schema`.
- 2026-05-31 | Product / Architecture | DayModel Input Contract (P0.1) | DONE | [DAYMODEL_INPUT_CONTRACT.md](./DAYMODEL_INPUT_CONTRACT.md): шкалы, Dependency Map, Machine fields per domain, gap vs `day_model_v0`; обновлены REFERENCE_LAYER freeze, README, tracker Phase 0.
- 2026-06-22 | Product / Architecture | Answer Contract v1 (Intent → Assembler) | DONE | [SCREEN_CONTRACTS_V1.md](./SCREEN_CONTRACTS_V1.md): Intent Registry, Answer Assembler role, Tier 1–2 mandatory answer elements; chain Reference → Profile → Question → Intent → Engines → Assembler → Surface; Phase 6 tracker + `CORE_PRODUCT_CANON` §6.1 cross-ref; next Question Registry v1.
- 2026-06-22 | Product / Architecture | Need-first stack (Need · Intent · Answer) | DONE | [INTENT_MODEL_V1.md](./INTENT_MODEL_V1.md) (28 needs, surface defaults, inference); [INTENT_REGISTRY_V1.md](./INTENT_REGISTRY_V1.md); [SCREEN_CONTRACTS_V1.md](./SCREEN_CONTRACTS_V1.md) v1.1 need-indexed; Question Registry demoted to Hub/AI; next Engine Projection Specs v1.
- 2026-06-22 | Product / Architecture | Daily Navigation Model (ICA kernel) | DONE | [DAILY_NAVIGATION_MODEL.md](./DAILY_NAVIGATION_MODEL.md): clarity+direction+reflection; Identity·Context·Guidance·Action; daily 4 opоры; screen map; Question Registry = chat periphery; `CORE_PRODUCT_CANON` §1 + JTBD Entry reframed.
- 2026-06-22 | Product / Architecture | Market attention + screen jobs | DONE | [MARKET_ATTENTION_AND_SCREEN_JOBS.md](./MARKET_ATTENTION_AND_SCREEN_JOBS.md): L1–L5 market tiers; 5 Today life domains; Today vs Tarot; Profile living KB; Calendar facts loop; retention Today→Calendar→Profile; `SCREEN_INVENTORY` §1 updated.
- 2026-06-22 | Product / Architecture | Screen Contracts v1 | DONE | [SCREEN_CONTRACTS_V1.md](./SCREEN_CONTRACTS_V1.md): mandatory slots per screen; Today domain status/opportunity/risk/action; Profile 8 elements; Compatibility 5; Tarot 4; Calendar 5; foundation-before Engine Projection Specs.
- 2026-06-22 | Product / Architecture | Today contract Model B ADR | DONE | [SCREEN_CONTRACTS_V1.md](./SCREEN_CONTRACTS_V1.md) v1.2: 3 DomainLens + global_context.period + personal_growth; unified status/opportunity/risk/action; отвергнуты 5-equal-domains и смешанная v1.1; до OpenAPI.
- 2026-06-22 | Product / Architecture | Today assembler mapping (legacy bridge) | DONE | [TODAY_CONTRACT_ASSEMBLER_MAPPING.md](./TODAY_CONTRACT_ASSEMBLER_MAPPING.md): source priority, slot rules, strict no-legacy-UI-bind, P0.1 acceptance; before OpenAPI.
- 2026-06-22 | Engineering | `assemble_today_contract_v1()` + fixtures | DONE | `services/today_contract_assembler_v1.py`; 3 fixture scenarios + `test_today_contract_assembler_v1.py` green; OpenAPI after wire.
- 2026-06-22 | Engineering | GET /today/contract wire | DONE | `today_contract_wire_v1.py` + `test_today_contract_endpoint.py`; legacy inputs server-side only.
- 2026-06-22 | Engineering | Web Today P0.1 contract render | DONE | `GET /today/contract` + `TodayContractSurface` / domain components; default Today path; ritual uses contract for domains.
- 2026-06-22 | Engineering | P0.1.1 Today text quality gate | DONE | `today_contract_text_quality_v1.py`; profile reject, imperative actions, family dedupe, short copy; tests green.
- 2026-06-22 | Engineering | P0.1.2 Today Text Quality v2 | DONE | Family profile leak blocked; Growth≠Period; cross-domain dedupe; domain-themed fallbacks; `family_profile_leak.json`; 22 contract tests green; web re-check before iOS.
- 2026-06-23 | Frontend / Onboarding P0.1 | Guest demo Today `/demo/today` | **DONE** | `GuestTodaySurface` + `buildGuestTodayPackage`; landing CTA → `/demo/today`; signup → `/onboarding/core`; tests `demoTodayPackage.test.ts`.
- 2026-06-23 | Frontend / Onboarding P0.2 + P0.4 | Core setup `/onboarding/core` | **DONE** | `CoreOnboardingFlow`, `useCoreSetupFlow`, `coreSetup.ts`; Profile ≠ onboarding host; `resolvePostAuthTarget`; legacy links migrated.
- 2026-06-23 | Frontend / Onboarding P0.3 | Intent + Reality chips | **DONE** | `IntentOnboardingFlow`, `RealityOnboardingFlow`, `onboardingContext.ts`; events `onboarding_intent_selected` / `onboarding_reality_selected`; backend + tests.
- 2026-06-23 | Frontend / Onboarding P0.5 | First Today `?first=1` | **DONE** | `FirstTodaySurface`, `buildFirstTodayPackage`; Theme→Progress→Insight→Action; deterministic, no LLM; tests.
- 2026-06-23 | Frontend / Onboarding P0.6 | Profile after First Today | **DONE** | `ProfileFirstDayTeaser`, `firstTodayState.ts`; journey redirects; `resolvePostCoreAuthTarget`.
- 2026-06-23 | Product / Onboarding | First Day & onboarding route contract v2 | **ACCEPTED** | [FIRST_DAY_EXPERIENCE.md](./FIRST_DAY_EXPERIENCE.md) v2: guest `/demo/today`, signup vs core split, `/onboarding/*`, Intent/Reality chips, Profile ≠ onboarding, PIM events, P0 backlog; [CORE_PRODUCT_CANON.md](./CORE_PRODUCT_CANON.md) §8.2; KASP channel A updated.
- 2026-06-23 | Product / Architecture | PIM v1.1 — Atom · Intent · DRE/LRE | **ACCEPTED** | PIM v1.1: Knowledge Atom unit; [INTENT_MODEL_V1.md](./INTENT_MODEL_V1.md); DRE/LRE split; UKM v1.3 provenance/decay; Today v2.5 C10–C12.
- 2026-06-23 | Product / Editorial | generation_logs export script | **DONE** | `export_today_generation_logs.py` → JSONL raw; corpus `--logs-dir`; PII mask; column introspection.
- 2026-06-23 | Product / Editorial | TL-0A/B language corpus | **DONE** | `today_language_corpus_v0.py` → 841 RU phrases + auto-tags; [TODAY_LANGUAGE_CORPUS_V0.json](./datasets/TODAY_LANGUAGE_CORPUS_V0.json).
- 2026-06-23 | Product / Editorial | TODAY_LANGUAGE + TL-0 | **IN_PROGRESS** | H4 SUPPORTED; H5 Self-Verification candidate; TL-1 blocked |
- 2026-06-23 | Product / Editorial | TODAY_LANGUAGE_V1 + RULE_001 (правило кино) | **ACCEPTED** | [TODAY_LANGUAGE_V1.md](./TODAY_LANGUAGE_V1.md): ось банальность/небанальность; Today v2.7 R24.
- 2026-06-23 | Product / Architecture | PR2 Goal Loop PIM gate (C13) | **ACCEPTED** | Today v2.6 R23; A1–A6 acceptance; guidance-only = reject; [INTENT_MODEL_V1.md](./INTENT_MODEL_V1.md) §6.
- 2026-06-23 | Product / Architecture | Signal vs Interpretation (C14) | **ACCEPTED** | PIM v1.2; UKM `evidence_chain`; ILR §8.1; Today v2.7 R24.
- 2026-06-23 | Product / Architecture | Contradiction & Re-evaluation (C15) | **ACCEPTED** | [CONTRADICTION_AND_REEVALUATION_V1.md](./CONTRADICTION_AND_REEVALUATION_V1.md); PIM v1.3; Today v2.8 R25.
- 2026-06-23 | Product / Architecture | Temporal Identity (C16) | **ACCEPTED** | [TEMPORAL_IDENTITY_V1.md](./TEMPORAL_IDENTITY_V1.md); change_nature; UKM temporal fields; PIM v1.4; Today v2.9 R26.
- 2026-06-23 | Product / Architecture | Decision Relevance (C17) | **ACCEPTED** | [DECISION_RELEVANCE_V1.md](./DECISION_RELEVANCE_V1.md); PIM slice ranking; UKM v1.7; Today v3.0 R27.
- 2026-06-23 | Product / Architecture | PIM PR Gate v1 | **ACCEPTED** | [PIM_PR_GATE_V1.md](./PIM_PR_GATE_V1.md): 5 PR questions; PR1/PR2 stack verification; C18 freeze.
- 2026-06-23 | Product / Architecture | PIM PR Gate v1.1 ownership | **ACCEPTED** | «Today исчез» test; Intent Record / outcome owners; reject `day_goals` as SoT.
- 2026-06-23 | Product / Architecture | PIM PR Gate v1.2 PIM Diff | **ACCEPTED** | Experience vs PIM test; mandatory PIM Diff; «guidance → PIM unchanged» anti-pattern.
- 2026-06-23 | Product / Architecture | PIM PR Gate v1.3 Learning Δ | **ACCEPTED** | три acceptance-контура; Learning Delta Test; reject UI-only verification.
- 2026-06-23 | Product / Architecture | PIM Product North Star | **ACCEPTED** | [PIM_PRODUCT_NORTH_STAR.md](./PIM_PRODUCT_NORTH_STAR.md): актив = PIM; Learning Δ; PIM ROI.
- 2026-06-23 | Engineering | **PR1 pre-flight** | **DONE** | [PR1_PREFLIGHT.md](./status/PR1_PREFLIGHT.md) §6–§10: S5 boundary, PIM audit, events chain, gate question. Шаблон PR: [PR1_GATE_SECTIONS.md](./status/PR1_GATE_SECTIONS.md).
- 2026-06-23 | Engineering | **Gate 1 — PR1 в коде** | **READY FOR MERGE** | S0–S5, S5 sentence-filter, pim_read_audit. Evidence: [PR1_MERGE_VERIFICATION.md](./status/PR1_MERGE_VERIFICATION.md) — live S5 (688/671/657) + gen log **692** + 6 events. → **PR2** (PIM write-path).
- 2026-06-23 | Product / Architecture | **Platform Layer Gate (C18+)** | **ACCEPTED** | Новый слой только при необходимости · gate question · [INTERNAL_PATTERNS](./TODAY_INTERNAL_PATTERNS_V0.md) v2.5 · [PIM_PR_GATE](./PIM_PR_GATE_V1.md) v1.5 · AR-010.
- 2026-06-23 | Product / Architecture | **Стоп-условие observable vs theory** | **ACCEPTED** | AP/SP · PIM · PR2 · IPL · Discovery — [INTERNAL_PATTERNS](./TODAY_INTERNAL_PATTERNS_V0.md) v2.3 §Стоп-условие · AR-010.
- 2026-06-23 | Product / Architecture | **AR-011 Phenomenon Before Analysis** | **ACCEPTED** | Два риска (wrong layer vs no data); pre-PR2 = phenomenon creation; IR lifecycle = canonical object — [INTERNAL_PATTERNS](./TODAY_INTERNAL_PATTERNS_V0.md) v2.6 §Стоп-условие · AR-011.
- 2026-06-23 | Engineering | **Day Continuity v0 (web)** | **PARTIAL UI VERIFIED** | Walkthrough run 2: close day + continuity line OK · onboarding→`/today` fix · [BEHAVIOR_CHANGE_TEST_V0.md](./status/BEHAVIOR_CHANGE_TEST_V0.md) § Walkthrough run 2.
- 2026-06-23 | Product | **Behavior Change Test (14d)** | **BLOCKED** | До ship gate; не тестировать S0–S5 фрагмент — [BEHAVIOR_CHANGE_TEST_V0.md](./status/BEHAVIOR_CHANGE_TEST_V0.md).
- 2026-06-23 | Product | **AR-012 freeze** | **ACTIVE** | No AR-013+; no field test on incomplete cycle.
- 2026-06-23 | Product / Architecture | **AR-012 Retention Before Instrumentation** | **ACCEPTED** | Продукт удержания первичен; IR = byproduct; instrumentation trap — [INTERNAL_PATTERNS](./TODAY_INTERNAL_PATTERNS_V0.md) v2.9 · PR2 §15 revised.
- 2026-06-23 | Product / Architecture | **Launch priority freeze** | **ACTIVE** | Retention-first order; gate «удержание в недели?» — AR-011/012 · [PR2_PREFLIGHT](./status/PR2_PREFLIGHT.md) · [PIM_PR_GATE](./PIM_PR_GATE_V1.md) §5.
- 2026-06-23 | Product / Architecture | **PR2 Success Criterion (post-deploy)** | **REVISED** | Retention primary · IR secondary · reject IR-only success — [PR2_PREFLIGHT](./status/PR2_PREFLIGHT.md) §15 · AR-012.
- 2026-06-23 | Product / Architecture | **Discovery fork** | **OPEN** | No Validation Protocol until prod Intent Records; post-PR2 **Watchlist** only — [INTERNAL_PATTERNS](./TODAY_INTERNAL_PATTERNS_V0.md) v2.2 · [PR2_PREFLIGHT](./status/PR2_PREFLIGHT.md) §14.
- 2026-06-23 | Engineering | **PR2 pre-flight** | **DONE** | [PR2_PREFLIGHT.md](./status/PR2_PREFLIGHT.md) — entity map; §2.1 birth moment; causal chain > atom; separate read/write audit; §14 Watchlist.
- 2026-06-23 | Docs | Legacy spec cleanup | DONE | Removed `spec/`, `REIMAGINING_PLAN.md`, PAUSED screen/visual docs, branch status snapshots, superseded Today web decisions; canon pointers → `TODAY_SCREEN_V1_CANON`, `PROFILE_SCREEN_MASTER`.
- 2026-06-23 | Docs | Aggressive canon prune | DONE | Removed 133 branch/registry/screen-pipeline docs; **37** canon files + schemas/i18n remain; `docs/README.md` rewritten as single index.
- 2026-06-23 | Docs | Single-canon rule | DONE | `.cursor/rules/docs-single-canon.mdc` + `docs/README.md` §Правило записи: search-before-create, no parallel specs; cross-ref in `workflow-incremental-docs.mdc`.
- 2026-07-01 | Docs | **Build Map v0.7.1 — Phase 1 screen gate table** | **ACTIVE** | launch remaining list · walkthrough after last ✅
- 2026-07-01 | Engineering | **Launch path wiring (web)** | **DONE** | Landing vitrine · demo redirect · FIRST_TODAY redirects · profile chart portal off
- 2026-07-01 | Engineering | **Landing v2 — outcome-first (web)** | **DONE** | Hero (map + copy) · 4 today cards · insight heatmap · final CTA · no feature menu
- 2026-07-01 | Engineering | **Maps seeds — Focus Map preview (Profile web)** | **DONE** | evening → dot seed · Profile preview · no Maps nav
- 2026-07-01 | Engineering | **Value-first onboarding P0.2 (web)** | **PARTIAL** | welcome → birth → preview → guest First Today → save · email-signup · claim → `/today?first=1` (not Profile skip)
- 2026-07-02 | Product / Architecture | **Maps — вторая половина TodayFlow (canon)** | **ACCEPTED** | §4.10 + §5.8 [TODAYFLOW_PRODUCT_MODEL.md](./TODAYFLOW_PRODUCT_MODEL.md) · §7 [PROFILE_SCREEN_MASTER.md](./PROFILE_SCREEN_MASTER.md) · §3.3 [PERSONAL_INTELLIGENCE_LAYER.md](./PERSONAL_INTELLIGENCE_LAYER.md) · backlog MP-1…MP-5
- 2026-07-02 | Engineering | **MP-2 Map language (web + iOS)** | **PARTIAL** | heatmap legend · calendar/ascetic/habits · nav · iOS sync notes
- 2026-07-03 | Engineering | **MP-2 Map language (web + iOS)** | **DONE** | weekly integration + WeeklyScreen story · ascetic/calendar/help/rings · `formatWeeklyRhythmStoryLine` · iOS chrome parity · legacy URL paths kept
- 2026-07-03 | Engineering | **Public launch path (web)** | **DONE** | docker stack · preview→First Today · guest claim on auth · nav cleanup · `/health` · `docker-compose.prod.yml`
- 2026-07-02 | Engineering | **MP-3 Mood Map v0 (web)** | **PARTIAL** | `/maps/mood` · heatmap · drill-down story · observation · Profile link
- 2026-07-02 | Engineering | **MP-3 Energy Map v0 (web)** | **PARTIAL** | `/maps/energy` · fusion API sync · mood fallback · Today persist · drill-down story · Profile link
- 2026-07-02 | Engineering | **MP-3 Habit Map v0 (web)** | **PARTIAL** | `/habits` · `habitMapModel` · 35-day 7×5 grid · day story · observation · mood/energy cross-links
- 2026-07-02 | Engineering | **MP-3 Promise Map v0 (web)** | **PARTIAL** | `/maps/promise` · `promiseMapModel` · evening close + open promises · drill-down · observation · Profile link
- 2026-07-03 | Engineering | **MP-3 Maps iOS parity v0** | **PARTIAL** | `TodayDayLocalStores` · Mood/Energy/Promise/Habit map views · Profile preview · mood→engagement sync · fusion persist
- 2026-07-03 | Engineering | **MP-3 Maps iOS gaps closed** | **DONE** | evening continuity writer · `/maps/*` + `/tracking/progress` deep links · `MapsHubView` · batch fusion sync for Energy Map
- 2026-07-03 | Engineering | **MP-1 Living Maps block v0** | **DONE** | section band · explore card grid + hub · local cross-map observation · heatmap/habit weave preview (web+iOS)
- 2026-07-03 | Engineering | **PS-1 Profile Selector v1** | **DONE** | `topic_sphere_excerpt` · day_history signals · `selector_eval.py` · DayContext wiring · slim LLM pack includes knowledge summary
- 2026-07-03 | Engineering | **DE-9 temporal context** | **DONE** | v1.5 `reflection_excerpt` · UI reflection line web+iOS · meaning signals · `day_model.temporal` |
- 2026-07-03 | Engineering | **DE-13 narrative funnel v1** | **IN_PROGRESS** | `day_history` in funnel step1/2 · step2 arg fix · temporal in funnel prompts |
- 2026-07-03 | Engineering | **DE-13 narrative funnel v2** | **IN_PROGRESS** | per-step cache reuse · `guide_funnel_step{1,2}_cache_hit` · `funnel_prompt_ver` in logs · pytest cache + cached_interpretation |
- 2026-07-03 | Engineering | **DE-13 narrative funnel v3** | **IN_PROGRESS** | child surfaces funnel chain · `funnel_interpretation` in user JSON · `guide_funnel_chain_used` · prompt v17 |
- 2026-07-03 | Engineering | **DE-13 narrative funnel v4** | **IN_PROGRESS** | step3 core_text_v0 LLM · guide_decision fallback · step3 cache/logs · step2 prompt v2 |
- 2026-07-03 | Engineering | **DE-13 guide_contract_v2** | **DONE** | HTTP envelope · guide_pipeline lineage · preserve funnel core · web/iOS/Android parsers · DE-13 epic closed |
- 2026-07-02 | Engineering | **Meaning-derived knowledge v0** | **PARTIAL** | `meaning_derived_knowledge_v0.py` · 3–6 → inferred hypothesis · 7+ → `day_active_knowledge_v1` · CUM sync · Today/Profile confirm
- 2026-07-02 | Engineering | **ILR engine v0 (BE)** | **PARTIAL** | JSON catalog `DATA/reference/interpretation/` + loader · compatibility rules · **gap:** migrate remaining triggers; editorial review queue
- 2026-07-02 | Engineering | **ILR confirm v0 (web + iOS + BE)** | **PARTIAL** | Today post-ritual chips · Profile atom confirm · inferred strip · iOS `PimInterpretationConfirmView` + CUM client · **gap:** Android
- 2026-07-02 | Engineering | **UKM explicit L1 promotion v0** | **PARTIAL** | mood/focus/promise/outcome/confirm/correction → `user_active_knowledge` · inferred verdict on `profile_atom_correction` · **gap:** full ILR ref expansion
- 2026-07-03 | Engineering | **UMTS-1 CUM schema v1** | **DONE** | [compact_user_model_v1.schema.json](./schemas/compact_user_model_v1.schema.json) · fixtures · CI `compact-user-model-schema` · v0 read slice unchanged
- 2026-07-06 | Product / Engineering | **Production pass · Landing #1 + guest limits** | **IN_PROGRESS** | Guest IA · `guestAccessStore` enforcement · **Tarot Figma pass (web):** hub 55:449 light shell · ritual+result 29:692 dark `ProductWebAppShell` · card images `contain` + portrait aspect · **gap:** iOS/Android parity
- 2026-07-03 | Design | **DS-FIGMA Foundation file v0** | **IN REVIEW** | [TODAYFLOW_FOUNDATION_UI](https://www.figma.com/design/pWdevqQqOi6wvoVc6hFWHa) · Cover premium textless · 8 pages · TF variables/styles · gate: «дорого/нет»
- 2026-07-03 | Design / Engineering | **Foundation sign-off — code-side (§9)** | **DONE** | Symbol grid + surfaces complete · Figma v0 built · formal Cover review open
- 2026-07-03 | Engineering | **DS-12 Archetype expansion 12/12 (web + iOS)** | **DONE** | seeker · mentor · guardian · visionary · catalyst · evolution aliases
- 2026-07-03 | Engineering | **DS-11 Element SVG assets (web + iOS)** | **DONE** | 4× elements SVG · `ElementIcon` · atmosphere pattern · `ElementSymbolView.swift`
- 2026-07-03 | Engineering | **DS-10 Typography bridge (`--tf-type-*`)** | **DONE** | `globals.css` orbit-text aliases · `profileV0.module.css` Foundation tokens
- 2026-07-03 | Engineering | **DS-9 Zodiac SVG assets (web + iOS)** | **DONE** | 12× zodiac SVG · mask tint `ZodiacIcon` · `ZodiacSymbolView.swift`
- 2026-07-03 | Engineering | **DS-8 Geometry System (web + iOS)** | **DONE** | G1–G5 · profile/today/portal presets · `SacredGeometryBackdrop` · portal deep · `FoundationGeometryView.swift`
- 2026-07-03 | Engineering | **DS-7 Planet SVG assets (web + iOS)** | **DONE** | 10× planets SVG · `PlanetIcon` · chart table · `PlanetSymbolView.swift`
- 2026-07-03 | Engineering | **DS-6 Foundation HeroSmall (web + iOS)** | **DONE** | Compatibility hub/exploration/dynamics headers · orbit symbol · compact score ring aside
- 2026-07-03 | Engineering | **DS-5 Foundation HeroMedium (web + iOS)** | **DONE** | `HeroMedium.tsx` · Today composition day-anchor · archetype/sun pillars · iOS `HeroMediumView.swift`
- 2026-07-03 | Design / Engineering | **Foundation sign-off — code-side QA (§9)** | **SUPERSEDED** | → **DONE** (2026-07-03 PM-QA) · Figma frames remain open
- 2026-07-03 | Engineering | **Phase 2 cleanup: ProfileLifeSection + legacy /natal-chart audit** | **DONE** | Quick Map `ProfileLifeSection` · `buildProfileLifeSpheresFromProfileData` · `?section=spheres` scroll · `/natal-chart` redirect only · href audit test
- 2026-07-03 | Engineering | **PM-1 backlog: sphere copy audit + ProfileV0 route** | **DONE** | `profileSphereCopy` canon · life sphere framing · `findLifeSphereHouseCopyOverlaps` · `/profile?view=v0` + `profileV0Route` chrome
- 2026-07-03 | Engineering | **DS-1 lite Archetype SVG assets (web + iOS)** | **DONE** | 8× `public/images/icons/archetypes/` · `VISUAL_ASSET_MODE=asset` · `ArchetypeSymbolView.swift`
- 2026-07-03 | Engineering | **DS-4 Profile motion kit (web + iOS)** | **DONE** | `--tf-motion-*` · `ProfileMotion.tsx` · HeroLarge/expand/portal/Quick Map · iOS `ProfileMotion.swift`
- 2026-07-03 | Engineering | **DS-3 Profile orbit-card purge (web)** | **DONE** | `ProfileSurface` tiles · legacy sections migrated · 0× `orbit-card` in `components/profile/`
- 2026-07-03 | Engineering | **DS-3 Profile route chrome (web)** | **DONE** | `SurfaceInsight` Surface B · `/profile` loading + notices без `orbit-card`
- 2026-07-03 | Engineering | **DS-2 Foundation HeroLarge (web + iOS)** | **DONE** | `HeroLarge.tsx` · Profile Quick Map / Editorial / FirstDayTeaser · iOS `HeroLargeView.swift` · symbol 120px · 88dvh canvas
- 2026-07-03 | Engineering | **UMTS-2 CUM v0.19** | **DONE** | Profile Quick Map UI: confidence %, delta_30d, 90d sparkline, primary + alternates · web+iOS
- 2026-07-02 | Engineering | **Today Day Dialogue v0 (web + iOS)** | **PARTIAL** | mood+focus + CUM merge · **inline ritual pick** (tarot grid + number flower, not modal gate) · post-ritual confirm · inferred strip · Tarot/Compat/Profile CUM · **gap:** Android · iOS pick parity audit
- 2026-07-02 | Engineering | **Compatibility PIM loop v0 (web + BE)** | **PARTIAL** | micro-echo · block_feedback → LLM · hub «Не сейчас» · **iOS:** `CompatibilityExplorationResultView` (ring hero, dimension cards, continuation) + analyze PIM · **gap:** pair profiles exploration · atom promotion
- 2026-07-02 | Product | **Today Screen v4.0 — Day Story Experience (canon §11)** | **ACCEPTED** | 17-block product spec → [TODAY_SCREEN_V1_CANON.md](./TODAY_SCREEN_V1_CANON.md) §11 · diff [TODAY_CANON_VS_CODE_DIFF.md](./status/TODAY_CANON_VS_CODE_DIFF.md) §Day Story v3
- 2026-07-02 | Engineering | **Meaning events batch dedup (web + BE)** | **DONE** | in-batch idempotency dedup · frontend outbox chunk dedup · fixes Today 500 spam
- 2026-07-02 | Engineering | **Value-first post-auth → First Today (web)** | **DONE** | `claimGuestProfile` no early `markFirstTodayCompleted` · save dev-token immediate redirect · demo → welcome
- 2026-07-01 | Engineering | **Onboarding preview · interpretation engine v1 (web)** | **DONE** | `frontend/src/lib/interpretation/*` — weighted candidates (sun + sign + life path + personal year/day) · mixed lenses · evidence gate · audit in guest draft · event `onboarding_recognition_shown`
- 2026-07-01 | Engineering | **First Result screen (web onboarding preview)** | **DONE** | Hero + key influences + dominant trait + mini-portrait + 6 dimension cards + surprise + «Почему?» · `FirstResultScreen` · engine-backed copy
- 2026-07-01 | Engineering | **First Result v2 — dedup + session (web)** | **DONE** | 4 visible cards + «ещё наблюдения» · dimension-specific «Почему?» · metadata sources (modality/ruler/season/weekday/chinese/personal year) · card types · RU polish · guest draft in `sessionStorage` · landing `?fresh=1`
- 2026-07-02 | Engineering | **Backend down / geocode+login fix** | **DONE** | `meaning.py` SyntaxError (frozenset `}`) crashed uvicorn · migration duplicate column tolerant · CityAutocomplete error surface
- 2026-07-02 | Engineering | **Onboarding chart path (web)** | **DONE** | name numerology on preview · single CTA → refine → email · welcome email + magic link · `/auth/magic` · profile prep on claim
- 2026-07-01 | Engineering | **Profile min — «Мои дни» (web)** | **DONE** | last 3 closed · focus + outcome · link Today · editorial + D1 teaser
- 2026-07-01 | Engineering | **Compatibility hook (Composition Explore)** | **DONE** | Card in Explore · CTA by saved person · `/compatibility` · D1 skip
- 2026-07-01 | Engineering | **Goal / Tracking teasers (Composition web)** | **DONE** | Growth zone slots 11–12 · default only · D1 skip
- 2026-07-01 | Engineering | **Composition polish (web)** | **DONE** | CSS module · loading skeletons · copy · evening hint · D2 continuity visual first · tests
- 2026-07-01 | Engineering | **First Today → Composition path (web)** | **DONE** | `?first=1` · `TodayCompositionSurface` variant `firstToday` · D1 zones
- 2026-07-01 | Engineering | **TodayCompositionSurface v1 (web)** | **PARTIAL** | Default `/today` · legacy `?experience=1`
- 2026-07-01 | Product | **Build Map v0.6.0 — wave 1 entities complete** | **ACTIVE** | `EveningClose` 🟢 · [TODAYFLOW_PRODUCT_BUILD_MAP.md](./TODAYFLOW_PRODUCT_BUILD_MAP.md)
- 2026-07-01 | Product | **Build Map v0.5.9 — `ContinuityRecall` spec 🟢** | **ACTIVE** | D2+ bridge
- 2026-07-01 | Product | **Positive Definition §2 CLOSED (canonical)** | **CLOSED** | Два базовых закона с §1
- 2026-07-01 | Product | **Positive Definition CLOSED** | **CLOSED** | §5.7 · Build Map E9 · spec · UX · empty states
- 2026-07-01 | Product | **Build Map v0.5.6 — `PracticeRecommendation` spec 🟢** | **ACTIVE** | One practice · [TODAYFLOW_PRODUCT_BUILD_MAP.md](./TODAYFLOW_PRODUCT_BUILD_MAP.md)
- 2026-07-01 | Product | **Build Map v0.5.5 — `DailySymbols` spec 🟢** | **ACTIVE** | Wave 1: color + stone · umbrella entity · [TODAYFLOW_PRODUCT_BUILD_MAP.md](./TODAYFLOW_PRODUCT_BUILD_MAP.md)
- 2026-07-01 | Product | **Invisible Mechanism CLOSED** | **CLOSED** | §5.6 · Build Map · dual Internal/External · 4 user knowledges — не revisiting
- 2026-07-01 | Product | **Build Map v0.2** | **REVOKED** | Component Catalog → Entity Catalog
- 2026-07-20 | Backend / LLM | **Quality-first Nebius + disclosure funnels** | **DONE** | `LLM_PROVIDER=nebius` · `LLM_QUALITY_MODE=rich` default · prompt registry · child surface 2-step funnels · profile 3-step portrait · [LLM_QUALITY_AND_PROMPT_EVOLUTION.md](./LLM_QUALITY_AND_PROMPT_EVOLUTION.md)
- 2026-07-20 | Profile / LLM | **profile-contract-v3 DoD hardening** | **IN_PROGRESS** | 4-step funnel · strict+quality validation · forming (no scaffold) · per-prompt versions in meta · hash lock/cache · pytest DoD green · FE no template spheres while forming · **next:** 20–30 live DeepSeek samples
- 2026-07-20 | Product / Audit | **User journey audit (guest→Today)** | **IN_PROGRESS** | Doc [USER_JOURNEY_AUDIT_2026-07-20.md](./audits/USER_JOURNEY_AUDIT_2026-07-20.md) · Tarot/Numerology module GET gated `not_selected` + reveal POSTs · hub no COD spoil · **open:** morning/Today redact pre-ritual · guest transfer · product decisions on pick vs reveal
- 2026-07-20 | Today / Reveal | **P0 day symbol SoT** | **IN_PROGRESS** | `day_symbol_states` · `/today/symbols/*` · morning redact · ritual FE reveal · guest claim · matrix pytest · canon [DAY_SYMBOL_REVEAL_CANON_V1.md](./audits/DAY_SYMBOL_REVEAL_CANON_V1.md) · **next:** rebuild day_story on reveal fingerprint · E2E Playwright · mood/goals claim fields
- 2026-07-20 | Today / Story | **day_story fingerprint rebuild** | **DONE** | `day_story_states` · fingerprint v1 · reveal → `story_refresh_required` (no LLM) · `POST /today/story/refresh` + lock · FE updating state · tests `test_day_story_rebuild_v1.py` · **next:** deploy · full guest claim · HTTP/e2e matrix
- 2026-07-20 | Auth / Guest | **full guest claim** | **DONE** | `guest_sessions` + `guest_day_snapshots` + claim token · `POST /today/guest/*` · atomic claim · conflict canon · FE sync/claim · tests `test_guest_claim_full_v1.py` · **next:** interpretation quality audit
- 2026-07-20 | Today / Quality | **interpretation quality audit** | **IN_PROGRESS** | Doc [INTERPRETATION_QUALITY_AUDIT_2026-07-20.md](./audits/INTERPRETATION_QUALITY_AUDIT_2026-07-20.md) · generation map · IQ-001/002 dual-influence fixes · `day-story-v1.1` · eval 100 + blind harness · pilot n=4 both schema OK (DeepSeek ~41s / Kimi ~22s, Kimi needs ≥4k tokens) · backend redeployed · **next:** human blind score 20→100 · EN/PL prompts · FE hardcode gates · consistency evaluator
- 2026-07-21 | Product / Canon | **Full user path canon v1** | **IN_PROGRESS** | Doc [FULL_USER_PATH_CANON_V1.md](./audits/FULL_USER_PATH_CANON_V1.md) · audit docs↔BE↔FE↔iOS · target journey landing→D30 · contradictions X1–X15 · generation registry · **no UI/code edits yet** · **next:** product accept X* → update FIRST_DAY / TODAY_SCREEN / blueprint → then implementation
- 2026-07-21 | Product / Canon | **§3 Canonical Personal Knowledge Principle** | **REVERTED** | Ошибочно поднят как новый закон; идея уже в Personal Model / PIL / DATA_OWNERSHIP · откат церемонии §3 · **вместо этого:** [PERSONAL_MODEL_CODE_COMPLIANCE_2026-07-21.md](./audits/PERSONAL_MODEL_CODE_COMPLIANCE_2026-07-21.md)
- 2026-07-21 | Eng / Audit | **Personal Model code compliance** | **IN_PROGRESS** | Doc [PERSONAL_MODEL_CODE_COMPLIANCE_2026-07-21.md](./audits/PERSONAL_MODEL_CODE_COMPLIANCE_2026-07-21.md) · **P0 DONE:** `build(publish_portrait=)` gate · GET no portrait LLM · `POST /account/core-profile/refresh` · Compat life_path from Snapshot/store · GenerationLog provenance · tests `test_core_profile_read_path_no_llm_v1.py` · **next P1:** Experiences consume CUM/contract slice · Compat profile_a/b = snapshot · **then C3** profile quality
- 2026-07-21 | Eng / Audit | **P1 Experience wiring** | **IN_PROGRESS** | Doc [PERSONAL_MODEL_EXPERIENCE_WIRING_P1_2026-07-21.md](./audits/PERSONAL_MODEL_EXPERIENCE_WIRING_P1_2026-07-21.md) · **SoI:** Formal single source without shared contract assembler → divergent understanding · target: Snapshot → **Experience Contract** → allowlist ExperienceSlice · Experience Consistency Tests (decision/conflict/communication/motivation/energy) · Tarot dead wiring · order P0→P1→C3→Telemetry · **next:** implement assembler_v0 + Consistency Tests · then C3
- 2026-07-21 | Content / C2 | **Compatibility content v1.1 production** | **DONE (guest+registered under flag)** | publish_gate in enrichment · Voice Canon architectural · prompt freeze until user data · **next:** telemetry; premium ≥5 real Q
- 2026-07-21 | Product / Metric | **Reference Rate (hardened)** | **RESERVED** | Prior knowledge impossible from current input alone · **in use** when comparable across modules (Today vs Tarot) and drives decisions · [PROFILE §7.2](./PROFILE_CONTENT_CANON_V1.md)
- 2026-07-21 | Product / Roadmap | **Longitudinal Validation** | **RESERVED (after C3, not C4)** | **Hypothesis:** model changes only with enough confirmed facts — not regen/prompt drift · [PROFILE §7.3](./PROFILE_CONTENT_CANON_V1.md) · exit criteria for C3/Telemetry in §7
- 2026-07-21 | Product / Roadmap | **Stage exit criteria (C3→Telemetry→RR→LV)** | **CANON** | Order frozen · C3: 4-step / unique knowledge / no section echo / prior as knowledge source · Telemetry: reads·confirm·regen·fallback·RR trend · [PROFILE §7](./PROFILE_CONTENT_CANON_V1.md)
- 2026-07-21 | Product / Roadmap | **Hypothesis falsifiers** | **RESERVED (after first real-user weeks)** | When to reject RR / Longitudinal / Consistency hypotheses · not engineering DoD · [PROFILE §7.4](./PROFILE_CONTENT_CANON_V1.md) · do not formalize yet
- 2026-07-01 | Product | **Launch Scope Freeze** | **ACTIVE** | Epic 1–4 only; Figma → code → 10×7d field; [WEB_LAUNCH_PRODUCT_BLUEPRINT.md](./status/WEB_LAUNCH_PRODUCT_BLUEPRINT.md)
- 2026-07-01 | Product | **TodayFlow Product Model v0.2** | **FROZEN** | Living model, Lifecycle, laws; doc №1 — no launch-scope edits until user test.
- 2026-06-22 | Engineering | P0.2 Today Experience (web) | PAUSED | Gate до ACCEPTED канона — снят 2026-06-23.
- 2026-06-22 | Engineering | P0.2.1 Unified day synthesis (web) | DONE | `todayUnifiedSynthesis.ts` + `todaySynthesisTextPolicy.ts`; one headline + paragraphs; RU tarot weave (Tower↔stability bridge); EN filter; thematic evening prompt; semantic cards deduped vs synthesis; tests green; iOS after web gate.
- 2026-06-22 | Engineering | P0.2.2 Ritual reveal gate (web) | DONE | `todayRevealGate.ts`; no card name / day number in UI before pick+reveal; experience starts at closed-card grid + symbol tiles; spine ribbon removed; synthesis gated until both ack; `TodayExperienceSurface` auto-opens day.
- 2026-06-22 | Product / Architecture | Today Experience Scenario v1 | ACTIVE | [TODAY_EXPERIENCE_SCENARIO_V1.md](./TODAY_EXPERIENCE_SCENARIO_V1.md): data vs narrative vs experience; phase machine; block registry; anti article-scroll; next after P0.1.3.
- 2026-06-22 | Engineering | P0.1.3 Today Narrative Layer + Growth skill | DONE | `todayNarrativeFromContract.ts` + `TodayNarrativeView`; growth observation reject; ritual/default Today unified story UI; before experience phases.
