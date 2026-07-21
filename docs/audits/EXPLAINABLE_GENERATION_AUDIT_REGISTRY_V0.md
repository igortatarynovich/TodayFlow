# Explainable Generation Audit Registry v0

**Статус:** ACTIVE quality gate (сквозной аудит, не новый принцип)  
**Дата:** 2026-07-21  
**Канон:** [EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md](../EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md) · [PRODUCT_TRUTH_FIRST.md](../PRODUCT_TRUTH_FIRST.md) · [EXPLAINABLE_INTERPRETATION.md](../EXPLAINABLE_INTERPRETATION.md)  
**Метод:** inventory production generators / projections → check inputs · calc · prompt · schema · trace · violations → remediation  
**Эталон compliance:** `practice_selection_ranker_v1` · частичный — `compact_user_model_v0`

---

## Как читать реестр

| Поле | Смысл |
|------|--------|
| **Pri** | P0 блокирует честность hot-path · P1 подрывает доверие · P2 polish / reference |
| **Trace** | наличие `source_inputs` · `calculation_version` · `evidence` · `derived_claims` · `confidence` · `limitations` · `fingerprint` (+ prompt/model versions) |
| **LLM invents** | что модель добавляет сверх структурированного входа |
| **Violations** | разрыв канона (пустые формулы, сферы без контекста, нет evidence, общий=персональный) |
| **Remediation** | минимальный следующий шаг к gate |

**Gate rule:** новый generator / prompt / projection не мержится, пока нет строки в этом реестре со статусом `pass` или явным `waive` + owner + expiry.

---

## Сводка

| Pri | Count | Фокус |
|-----|-------|--------|
| P0 | 3 | day_story · profile_contract · compatibility_content |
| P1 | 7 | recommendations · explainers · tarot_answer · FE sphere/energy/strengthen · practices fallback |
| P2 | 3 | template tarot · CUM version · natal editorial |
| Pass / reference | 2 | practice_selection_ranker · (partial) CUM confidence |

Goals / promises / ascetics: **user-authored contracts** в tracking API — отдельной LLM-генерации «красивой аскезы» в hot-path не найдено; риск — UI copy и future generators. Держать в реестре как **watch**.

---

## Backend generators

### P0

| generator | endpoint / wire | inputs | calculation (code) | prompt / fn | output schema | trace | violations | remediation |
|-----------|-----------------|--------|--------------------|-------------|---------------|-------|------------|-------------|
| **day_story_v1** | `GET /today/contract` · morning ritual wire · `day_story_wire_v1.build_day_story_v1_wire` | day_engine_brief, ritual (card/number), user_core_slim, intent, behavior, rhythm, color/stone | почти нет до LLM; symbols/ritual отдельно | day_story prompt (`DAY_STORY_PROMPT_VER` internal) | theme, direction, story, do/avoid, domains{relationships,money_work,family}, talisman, practice_recommendation, … | generation_id partial; **нет** source_inputs / evidence / confidence / limitations / fingerprint | LLM invents почти весь день; domains всегда заполнены; пустые формулы банятся в prompt без runtime gate | (1) structured interpretation before prose (2) domains only with evidence (3) full trace + phrase validator |
| **profile_contract_v1** | CoreProfile publish path · `profile_contract_v1` | person, astro signs, numerology, baseline, living | enrich living patterns детерминированно; rich text — LLM | profile contract prompts + `generation_meta` | identity_core, strengths, growth_zones, styles, life_spheres×9, status forming/ready | generation_meta (prompt/model/validation); **нет** evidence per claim / confidence / limitations / fingerprint | claims без связи к natal/numerology atoms; forming не раскрывает gaps | (1) claim→evidence map (2) per-domain confidence (3) honest forming limitations |
| **compatibility_content_v1** | enrichment job · `compatibility_content_v1/generate_v1.generate_content_v1` | signs, dates, profiles, source_depth, score_hint | static template score / quick_reading; depth resolve | PROMPT_VERSION + publish_gate | Registered/Premium content surfaces | prompt_version, source_depth, publish_gate; **нет** source_inputs evidence map / confidence / fingerprint | LLM prose без claim→profile fact map; limitations только через gate | (1) evidence map (2) confidence by source_depth (3) expose limitations in product surface |

### P1

| generator | endpoint / wire | inputs | calculation | prompt / fn | output | trace | violations | remediation |
|-----------|-----------------|--------|-------------|-------------|--------|-------|------------|-------------|
| **daily_recommendations** | morning ritual · `_get_daily_recommendations` | natal slice, day_number, tarot card | none | learning_service log + prompt_version_id | what_to_do / avoid / key_focus | generation_log rich; **нет** evidence/confidence/limitations | LLM reinvented symbol meanings; empty formulas only prompt-banned | pass catalog meanings into prompt; cite catalog_version; runtime phrase gate |
| **tarot_card_explanation** | morning · `core/tarot_explainer.explain_tarot_card` | card_name, orientation, user_context | none | tarot-explainer-v3 | meaning, do/avoid, events, why | generation_log + cache; no catalog evidence | no catalog link; fallback ≈ LLM | bind Reference tarot machine/content; evidence; confidence |
| **numerology_explanation** | morning · numerology explainer | number, type, user_context | number itself elsewhere; text none | numerology-explainer-v3 | same shape as tarot explainer | generation_log; no formula version in output | no calc steps / catalog; fallback opaque | attach calculation_version + catalog meaning before LLM |
| **tarot_answer_v1** | tarot spread context | cards, question, concern_domain, profile slice | template compose (`compose_question_first_reading`) | mostly template; light stitching | tarot_answer_v1 fields | generation_id, synthesis_mode; weak evidence map | card→claim not explicit; no confidence | export card/catalog refs in evidence[]; confidence by spread depth |
| **daily_horoscope / spine** | morning · `_get_daily_horoscope` | profile, forecast, recommendations, consistency | `_build_deterministic_spine` | LLM **disabled P0** (latency) | spine + optional scenarios | generation_log when used; deterministic path cleaner | scenarios empty in prod; if LLM re-enabled needs full gate | keep spine deterministic; any LLM behind same trace gate as day_story |
| **natal_chart_editorial** | profile / reports · `natal_chart_editorial.generate_natal_chart_editorial` | chart positions | chart calc separate (astro engine) | editorial LLM | editorial blocks | varies | editorial may overclaim without ASC precision flags | require time_unknown / ascendant_precision in limitations before prose |
| **thematic / full reports** | `/api` thematic + full_reports | birth data | astro calc | report generators | long-form reports | generation logs partial | high invent risk; sphere-heavy | freeze or gate behind same canon before relaunch |

### P2 / reference

| generator | notes | status |
|-----------|-------|--------|
| **practice_selection_ranker_v1** | deterministic rank + `selection_decision_trace_v1`, versions, context hash, block reasons | **PASS — reference** |
| **compact_user_model_v0** | confidence by domain, knowledge atoms with evidence_count | **PASS-ish** — add top-level `calculation_version` |
| **tarot template synthesis** | catalog `_CARD_SPEAK` composition | good pattern — add catalog_version + fingerprint |

### Watch (no LLM invent in hot-path today)

| area | path | risk | gate |
|------|------|------|------|
| Ascetic contracts | `POST /tracking/ascetic-contracts` | user text; UI may suggest fuzzy copy | any generator must be behavioral contract schema |
| Goals / day promises | tracking / today UI | empty formulas in FE strengthen/goals | no personal goal without user task id or explicit pick list |
| Affirmations | `affirmation_generator` | motivational fluff | same phrase + evidence gate |

---

## Frontend projections (assemble / fallback)

| surface | file | issue | source | violation | remediation | Pri |
|---------|------|-------|--------|-----------|-------------|-----|
| Today spheres | `lib/todayDaySphereFocus.ts` | client advice when contract fields empty | local fallback | sphere menu / invented practice | hide cards without contract evidence | P1 |
| Today energy | `app/today/page.tsx` · utils | residual energy paths / decisions | server ?? 0 after PR-1; watch other call sites | placeholder as signal | never drive UI from invented score | P1 |
| Today strengthen | `lib/todayCompositionModel.ts` / day story model | invented strengthen tools | local | advice without DailyState | only link practices/goals from API ids | P1 |
| Practices hero | `app/practices/page.tsx` | catalog_fallback still shown (labeled) | catalog | general as day practice | prefer empty + CTA choose; keep label if shown | P1 |
| Profile live cards | `buildProfileV2LiveContext.ts` | fixed in PR-1 (stone/supports/awareness) | morning / CUM | was identity→stone | keep tests; no regress | mitigated |
| Tarot rail tags | `TarotRail.tsx` | fixed in PR-1 | was hardcoded | fake personal tags | keep null until DailyState | mitigated |

---

## Quality gate checklist (per new/changed generator)

Copy into PR description:

```text
[ ] Registry row added/updated
[ ] Inputs listed (no invent)
[ ] Deterministic calc named + calculation_version
[ ] Prompt receives structured DailyState/slice only
[ ] Output schema has evidence / derived_claims / confidence / limitations
[ ] Trace persisted (fingerprint + versions)
[ ] Runtime ban on empty formulas (not only prompt text)
[ ] Partial data → lower specificity, not higher certainty
[ ] Personal claims require user context or labeled general
[ ] FE projection: no client invent; empty/error distinct
```

---

## Remediation backlog (execution order)

1. **P0 day_story_v1** — interpretation+evidence before prose; domain partial; full trace; phrase validator.  
2. **P0 profile_contract_v1** — claim evidence map + limitations in forming.  
3. **P0 compatibility_content_v1** — evidence by source_depth + product-visible limitations.  
4. **P1 symbol explainers + daily_recommendations** — catalog meaning in → cite out.  
5. **P1 FE** — remove sphere/strengthen invent; practices empty honesty.  
6. **P1 tarot_answer evidence map**.  
7. **P2** — stamp versions on template/CUM; align reports or keep offline.

Phase N DailyState RFC remains PLANNED; this registry is the **gate while DailyState evolves** — do not wait for DailyState to start P0 trace on day_story/profile/compat.

---

## Update protocol

- Owner: Engineering + Product  
- Update this file when adding/changing a generator or finding a new violation  
- Status values per row: `fail` (default until fixed) · `mitigated` · `pass` · `waive`  
- Do **not** spawn new principle docs from audit findings — fix code or extend this registry
