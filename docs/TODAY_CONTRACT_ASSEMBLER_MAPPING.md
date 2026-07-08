# Today Contract Assembler Mapping

**Статус:** принято (bridge legacy → Model B).  
**Версия:** 1.0 (2026-06-22).  
**Владелец:** Product + Engineering.

**Роль:** как **Assembler** заполняет `today_contract_v1` из legacy Today inputs. **До OpenAPI** — фиксирует правила, чтобы внутренние поля не стали UI-контрактом.

**Контракт:** [SCREEN_CONTRACTS_V1.md](./SCREEN_CONTRACTS_V1.md) §2.2 Model B · §3.3  
**Gap:** [status/TODAY_CANON_VS_CODE_DIFF.md](./status/TODAY_CANON_VS_CODE_DIFF.md)

**Целевой owner Assembler:** backend (один DTO на wire). Сегодня spheres частично собираются на **клиенте** (`buildTodayFourAreas`) — P0.1 = **перенос сборки на сервер**, клиент только рендерит контракт.

---

## 1. Target payload (`today_contract_v1`)

```yaml
DomainLens:
  status: string
  opportunity: string
  risk: string
  action: string

today_contract_v1:
  global_context:
    period: string
  personal_growth:
    development_point: string
  domains:
    relationships: DomainLens
    money_work: DomainLens
    family: DomainLens
  primary_action: string
  progress: object
  generation_id: string
```

**Не домены:** `global_context` · `personal_growth` — отдельные блоки UI.

---

## 2. Strict rule — legacy = input only

| Legacy (запрещено bind в UI после P0.1) | Роль в Assembler |
|----------------------------------------|------------------|
| `energy` sphere / score | input → meta или deprecated display |
| `theme` / `summaryTitle` | input → `global_context.period` |
| `insight` / `watch` / `reason` (four areas) | input → `DomainLens` slots |
| `spheres.love` / `spheres.money` / `spheres.work` | input → domain lenses |
| `buildTodayFourAreas()` output | **заменяется** контрактом |
| Разрозненные client fetches | **заменяется** одним DTO |

**Клиент P0.1:** рендер только из `today_contract_v1` + optional enrich (Progress counters, Symbolic tarot card **не** substitute domain lenses).

---

## 3. Legacy source inventory

| Priority | Source | API / artifact | Ключевые поля |
|----------|--------|----------------|---------------|
| 1 | **Spheres (computed)** | Client: `buildTodayFourAreas()` ← rings, scenarios, spine, spheres narrative | `love/work/money/energy` → headline, detail, insight, watch, reason |
| 2 | **Narrative** | `POST /today/narrative` surfaces `guide`, `spheres`, `day_layer` | `payload` text blocks; spheres keys `*_insight`, `*_reason` |
| 3 | **Morning ritual** | `GET /morning-ritual/today` · today bundle `morning` | `daily_horoscope.scenarios[]`, `spine`, `daily_recommendations`, `decision_engine` |
| 4 | **Fusion** | `GET /tracking/fusion/{date}` | `scores`, `recommendations`, `encouragement`, `rhythm_context` |
| 5 | **Fallback templates** | `todayRitualCopy.ts` / `TodayRitualCopy.swift` | `fourArea*Fallback`, spine fallbacks |

**Assembler input bundle (server target):** morning + fusion + narrative payloads + core_profile slice + day_model preview — **один assemble call**, не 4 client round-trips.

---

## 4. Source priority (per slot)

При конфликте: **выше в таблице §3 побеждает**, если текст non-empty и проходит sanitizer.  
Ниже — дополняет пустые слоты. **Никогда** два разных текста в один слот без merge rule.

| Slot | Priority order (first wins for primary text) |
|------|---------------------------------------------|
| Any `DomainLens.*` | 1 spheres narrative keys → 2 narrative `spheres` surface → 3 morning `scenarios` → 4 fusion-derived hint → 5 template |
| `global_context.period` | 1 narrative `guide` primary / theme → 2 `spine.best_mode` + scenario lead → 3 `decision_engine.hero` label → 4 fusion `encouragement` → 5 template |
| `personal_growth.development_point` | 1 narrative growth/body keys → 2 spine + insight synthesis → 3 `decision_engine.actions[0]` hint → 4 template |
| `primary_action` | 1 strongest domain `action` (priority: relationships > money_work > family if tie by score) → 2 `spine.first_move` → 3 `decision_engine.actions[0]` → 4 `daily_recommendations.what_to_do` → 5 template |

---

## 5. Mapping rules — domains

### 5.1 `domains.relationships` ← legacy `love` sphere

| Target slot | Primary legacy | Fallback chain |
|-------------|----------------|----------------|
| `status` | `concat(spheres.love.todayHeadline, spheres.love.todayDetail)` trimmed | `scenario slug=love` → `focus` + `summary` |
| `opportunity` | `spheres.love.insight` | `narrativePick(spheresNarrative, love_insight, relationships_insight)` |
| `risk` | `spheres.love.watch` | `RITUAL_COPY.fourAreaLoveWatch` only if no narrative risk |
| `action` | **synthesize** (§6) from `spheres.love.reason`, domain-specific narrative, `spine.first_move` if head_topic=relations | template action for love |

**Не использовать:** `energy` sphere as relationships substitute.

### 5.2 `domains.money_work` ← merge `work` + `money` spheres

| Target slot | Primary legacy | Merge rule |
|-------------|----------------|------------|
| `status` | Merge `work.todayHeadline/detail` + `money.todayHeadline/detail` | One sentence: work context + money context; dedupe via `dedupeRitualCoreTexts` |
| `opportunity` | Prefer higher-score sphere `insight`; or combine if both distinct | `money_insight` / `work_insight` narrative keys |
| `risk` | Prefer `money.watch`; else `work.watch` | `daily_recommendations.what_to_avoid` slice if money-related |
| `action` | **synthesize** (§6); bias `money` scenario `focus` if money score ≥ work | `first_move` if head_topic=money |

**Wire id:** `money_work` (single domain). Legacy **не** exposes separate UI ids `work` / `money` after P0.1.

### 5.3 `domains.family` ← dedicated lens (not love alias)

| Target slot | Primary legacy | Fallback chain |
|-------------|----------------|----------------|
| `status` | `scenario slug=family` → `focus` + `summary` | **не** reuse love scenario alone; if only love scenario, mark `status` with honest empty_reason + family template |
| `opportunity` | `narrativePick(family_support, family_insight, family_reason)` | derive support tone from family scenario `summary` |
| `risk` | family scenario tension phrase OR narrative family risk key | template family tension |
| `action` | **synthesize** (§6) from family scenario `focus` | small family-specific action template |

**Gap today:** client maps `family` head_topic → `love` area ([todayFourAreas.ts](frontend/src/components/today/todayFourAreas.ts) `HEAD_TOPIC_TO_AREA`). Assembler **must** populate `domains.family` independently.

---

## 6. Mapping rules — meta blocks

### 6.1 `global_context.period`

| Step | Source |
|------|--------|
| 1 | Narrative `guide` payload: primary theme / day thesis (если есть structured field) |
| 2 | `morning.daily_horoscope.spine.best_mode` |
| 3 | Lead scenario summary (highest-weight scenario of day) |
| 4 | `decision_engine.hero.energy_label` + focus chips (compressed) |
| 5 | `fusion.encouragement` |
| 6 | `RITUAL_COPY` day type headline |

**Anti-pattern:** raw transit list as `period`.

### 6.2 `personal_growth.development_point`

| Step | Source |
|------|--------|
| 1 | Narrative: `body_insight`, `energy_reason`, `state_reason`, growth keys in spheres payload |
| 2 | Synthesis: one line from `spine.best_mode` + `spheres.energy.insight` (if not duplicate of period) |
| 3 | `decision_engine.actions[0]` if personal-growth tone |
| 4 | Template `fourAreaEnergyInsight*` only as last resort |

**Не использовать:** full `energy` sphere card as growth block.

### 6.3 `primary_action`

| Step | Source |
|------|--------|
| 1 | Pick **one** `domains.*.action` with highest domain score (love > money_work > family tie-break) |
| 2 | `spine.first_move` if no domain action |
| 3 | `decision_engine.actions[0]` |
| 4 | `daily_recommendations.what_to_do` |
| 5 | Template |

### 6.4 `action` synthesis (per domain)

When legacy has `reason` but no explicit action:

```
action = first imperative clause from (reason OR insight OR scenario.focus)
         capped at 1 short sentence
         if none → domain-specific pause/hold template (not empty)
```

Use existing copy sanitizer: `repairRitualDoNotEnterLine`, `dedupeRitualCoreTexts` — same rules as ritual flow.

---

## 7. Mapping table (quick reference)

| Target | Primary legacy |
|--------|----------------|
| `relationships.status` | `spheres.love` headline/detail |
| `relationships.opportunity` | `spheres.love.insight` |
| `relationships.risk` | `spheres.love.watch` |
| `relationships.action` | §6 synthesize |
| `money_work.status` | merge `spheres.work` + `spheres.money` headline/detail |
| `money_work.opportunity` | best of work/money `insight` |
| `money_work.risk` | money `watch` → work `watch` |
| `money_work.action` | §6 + money/work scenario |
| `family.status` | `scenario family` focus/summary — **never** `family_insight` profile narrative |
| `family.opportunity` | narrative family support / scenario |
| `family.risk` | family tension narrative / scenario |
| `family.action` | §6 + family scenario focus |
| `global_context.period` | guide theme / `spine.best_mode` / scenarios |
| `personal_growth.development_point` | energy/body narrative + spine hint |
| `primary_action` | strongest domain action → `first_move` |

---

## 8. UI composition (client)

```
TodayScreen
├── GlobalContextBlock(period)              # not DomainLens
├── PersonalGrowthBlock(development_point)  # not DomainLens
├── TodayDomainLens(domain=relationships)   # one component × 3
├── TodayDomainLens(domain=money_work)
├── TodayDomainLens(domain=family)
├── PrimaryActionBlock
├── ProgressBlock                           # CORE_USER_LOOP
└── SymbolicBrief                           # tarot/number — not domain substitute
```

**iOS parity:** same component boundaries as `TodayRitualFlowView` refactor — bind `TodayDomainLensView(model: contract.domains.*)`.

---

## 9. P0.1 acceptance checklist

| # | Criterion | Verify |
|---|-----------|--------|
| 1 | Web + iOS receive **one** `today_contract_v1` DTO | API integration test |
| 2 | Today renders unified **narrative story** (not 3× slot grid) | UI review — `TodayNarrativeView` |
| 3 | `period` + `development_point` **separate** blocks, not in `domains` | contract lint |
| 4 | `domains.family` populated **independently** of love | family scenario path |
| 5 | Every domain has non-empty **`action`** (or explicit hold template) | assembler validation |
| 6 | Client **does not** call assemble pipeline: morning + fusion + narrative + client `buildTodayFourAreas` | network trace |
| 7 | No UI bind to `insight`/`watch`/`reason`/`energy` as primary contract | code grep / lint rule |
| 8 | UI renders **narrative story**, not raw DomainLens slot grid | `TodayNarrativeView` |

### P0.1.2 — Today Text Quality v2 (gate before iOS)

**Запрещено в Today output:**

- описания личности; «Игорь такой человек»; profile summaries
- одинаковые тексты в разных слотах или доменах

**Обязательно:**

- каждый слот про **сегодняшний день** (`сегодня → ситуация → навигация`)
- каждый домен — собственная тема: отношения = контакт; деньги/работа = решения; семья = атмосфера дома
- `personal_growth.development_point` ≠ `global_context.period`
- Family **не** использует Profile fallback / `family_insight` personality напрямую

**Реализация:** `today_contract_text_quality_v1.py` + fixture `family_profile_leak.json`; assembler `accept_narrative_source` / `dedupe_cross_domain_lenses`.

### P0.1.3 — Today Narrative Layer (UI)

**Data contract** (`today_contract_v1`) — для assembler/API: `status`, `opportunity`, `risk`, `action` per domain.

**Narrative contract** (`today_narrative_v1`, client-side) — для человека:

- Главная мысль дня (period headline + subline + growth skill)
- Где это проявится (одна строка per domain, связанный spine)
- Что сделать (primary action)

UI **не** рендерит DomainLens slots напрямую. `buildTodayNarrativeV1()` в `frontend/src/lib/todayNarrativeFromContract.ts`.

**Реализация:** `buildTodayNarrativeV1()` в `frontend/src/lib/todayNarrativeFromContract.ts`.

**Следующий шаг (не этот PR):** [TODAY_SCREEN_V1_CANON.md](./TODAY_SCREEN_V1_CANON.md) — phase machine + block registry; убрать article-scroll.

---

## 10. Implementation sequence (no OpenAPI first)

| Step | Deliverable |
|------|-------------|
| 1 | **This doc** accepted |
| 2 | Backend `assemble_today_contract_v1()` — pure function + fixtures from legacy JSON samples | **DONE** — `today_contract_assembler_v1.py` |
| 3 | Attach to Today package endpoint (extend morning ritual or `GET /today/contract`) | **DONE** — `GET /today/contract` |
| 4 | Web/iOS: read contract; deprecate `buildTodayFourAreas` in render path |
| 5 | OpenAPI schema from §1 (after fixtures green) |
| 6 | Engine Projection Specs — map projections → DomainLens slots |

---

## 11. Changelog

| Дата | Изменение |
|------|-----------|
| 2026-06-22 | v1.3 — P0.1.3 Narrative Layer + Growth skill: UI story from contract; growth rejects observations |
| 2026-06-22 | v1.2 — P0.1.2 Today Text Quality v2: family profile reject, Growth≠Period, cross-domain dedupe, domain themes |
| 2026-06-22 | v1.1 — P0.1.1 text quality gate: profile reject, imperative actions, family dedupe, length limits |
