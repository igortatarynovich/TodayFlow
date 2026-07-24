# Decision Relevance v1 (C17)

**Статус:** `ACCEPTED` — канон **приоритизации знаний** для решений и контекста.  
**Версия:** 1.0.7 (2026-06-23)  
**Владелец:** Product + Intelligence

**Это не:** `confidence` (насколько уверены) · `interest score` (тема нравится) · сортировка по `last_updated`.

**Это:** **насколько знание полезно для принятия решений** — какие atoms попадают в DRE, LRE, Gate slice, training — а какие остаются в архиве.

**Связь:**

| Документ | Роль |
|----------|------|
| [PERSONAL_INTELLIGENCE_MODEL_V1.md](pim/PERSONAL_INTELLIGENCE_MODEL_V1.md) | PIM; DRE / LRE inputs |
| [USER_KNOWLEDGE_MODEL.md](pim/USER_KNOWLEDGE_MODEL.md) | `decision_relevance` на atoms; Context Selection §6 |
| [HUMAN_DECISION_MODEL_V1.md](./HUMAN_DECISION_MODEL_V1.md) | HDM claims — typically high relevance |
| [TEMPORAL_IDENTITY_V1.md](./TEMPORAL_IDENTITY_V1.md) | historical + low relevance → archive |
| [TODAY_INTERNAL_PATTERNS_V0.md](./TODAY_INTERNAL_PATTERNS_V0.md) | RAT → **Recognition Relevance Map** (hypothesis); параллельная ось curation |
| [API_MEMORY_AND_LEARNING_LAYER.md](./API_MEMORY_AND_LEARNING_LAYER.md) | top-K slice economics |

---

## 0. Два класса вопросов

| C10–C16 | C17 |
|---------|-----|
| **Что** мы знаем о человеке? | **Что из этого важно** для помощи человеку? |
| Почему · когда · почему перестало | **Насколько влияет** на решения сегодня |

Без C17 PIM рискует стать **точным, объяснимым, историческим архивом**, который не отделяет важное от второстепенного.

**Ограниченный контекст** (LLM сейчас, own model завтра) — PIM **не отдаёт всё**. Нужен **ranking по decision relevance**, не только по confidence.

### 0.1 Recognition Relevance *(RRM — candidate layer · C18 freeze)*

**C10–C17:** модель данных · **что стоит хранить** (после попадания в PIM).  
**RRM *(hypothesis)*:** политика инвестирования · **что стоит добывать** (до write).

| | C17 | RRM |
|---|-----|-----|
| Вопрос | Важно для **решений**? | Важно для **узнавания**? |
| Уровень | **atom** | **тип знания** *(hypothesis)* |
| Статус | ACCEPTED | hypothesis · не prod до sign-off |

#### Матрица curation

| Decision | Recognition | Действие |
|----------|-------------|----------|
| High | High | Priority #1 |
| High | Low | Guidance slice · weak recognition |
| Low | High | Recognition slice · weak guidance |
| **Low** | **Low** | **Q4:** archive · **не собирать** |

#### Acquisition *(hypothesis)*

```
Signal → Candidate Knowledge Type → RRM + C17 policy → PIM (or drop)
```

#### Training corpus *(future)*

Atom in training iff **C14–C16** evidence + **C17** + **RRM** — см. [TODAY_INTERNAL_PATTERNS_V0.md](./TODAY_INTERNAL_PATTERNS_V0.md) §RRM.

**Не** добавлять `recognition_relevance` / `discovery_relevance` в prod до RRM sign-off.

**AR-004 — Knowledge Density Illusion:** больше фактов ≠ лучше узнавание. RRM — **value axis**, не acquisition policy alone.

**Knowledge ROI *(hypothesis)*:** Value (C17 + Recognition [+ Discovery]) ÷ **Acquisition Cost**. Память = ограниченный ресурс — см. AR-004 · AR-008.

#### 0.4 Acquisition Cost · Knowledge Observability *(post-AR-004 · AR-008)*

| Плоскость | Ось | Вопрос |
|-----------|-----|--------|
| **Value** | C17 | Помогает **решениям**? |
| **Value** | RRM | Помогает **узнаванию**? |
| **Feasibility** | **Observability** | Можно ли **надёжно добыть** из поведения? |
| **Cost** | **Acquisition Cost** | Сколько стоит **получить и поддерживать**? |

**PIM investment policy *(hypothesis)*:** **C17 ∩ RRM ∩ Observability ∩ Reusability** — не превращать RRM в acquisition policy сразу после n=40 · не «high ROI → store» *(AR-009)*.

| Knowledge | Decision | Recognition | Cost | Observability | Reusability | ROI *(hyp)* |
|-----------|----------|-------------|------|---------------|-------------|-------------|
| Повторяющиеся перегрузы | high | high | medium | high | **high** | **high** |
| Тишина / утро / Notion | low–medium | low | low | high | **low** | **low** |
| Ждёт ответа · откладывает разговоры | medium | high | **high** | low–medium | **uncertain** | **uncertain** |

Schema: `recognition_relevance_map.knowledge_investment_economics` in [TODAY_LANGUAGE_CALIBRATION_V0.json](./datasets/TODAY_LANGUAGE_CALIBRATION_V0.json).

#### 0.5 Knowledge Reusability *(post-AR-008 · AR-009)*

| Ось | Вопрос |
|-----|--------|
| **Reusability** | **Будет использоваться повторно** — сколькими процессами? |

**PIM ≠ vault.** PIM для **поддержки процессов** (guidance · DRE · reflection · planning · prioritization · retrieval) — не для хранения «ценных активов».

**Platform knowledge vs feature knowledge:** high ROI + один consumer → **feature knowledge** · не обязательно долгоживущий atom в PIM.

**Post-n=40:** после Observability + ROI sketch — **Reusability map** до KIP sign-off.

#### 0.2 Discovery Relevance *(open hypothesis · AR-005)*

**Recognition:** «**это про меня**» · trust · copy hit.  
**Discovery:** «**я этого не замечал**» · новое знание · снижение неопределённости модели.

| | Recognition | Discovery |
|---|-------------|-----------|
| User | попадание | новое понимание |
| PIM | trust | новый atom · pattern hypothesis |

**Матрица Rec × Disc:** high/high = gold · high/low = узнавание · **low/high = обучение (не drop!)** · low/low = шум.

**KIP *(hypothesis)*:** Decision (C17) + Recognition + Discovery — **три причины ценности знания**. См. [TODAY_INTERNAL_PATTERNS_V0.md](./TODAY_INTERNAL_PATTERNS_V0.md) §KIP · AR-005.

#### 0.3 Temporal asymmetry · Discovery fork *(AR-006 · open until prod Intent Records)*

| Ось | Когда | Инструмент |
|-----|-------|------------|
| **Recognition** | сразу после текста | RAT · editorial · «это про меня» |
| **Decision** | по outcome действия | goal · guidance · Intent Records |
| **Discovery** | недели–месяцы | longitudinal PIM *(post-PR2)* |

**Discovery ≠ Recognition map по тем же правилам.**

**Не строить сейчас:** Discovery Validation Protocol · Discovery Engine · prod `discovery_relevance`.

**Сейчас (post-PR2):** **Discovery Watchlist** — наблюдение без интерпретации. Поля: `first_seen_at` · `source_intent_record_ids[]` · `source_discovery_answers[]` · `reappeared_count` · `user_self_reference_count` · `linked_future_goals_count` · `linked_future_outcomes_count`. См. [TODAY_INTERNAL_PATTERNS_V0.md](./TODAY_INTERNAL_PATTERNS_V0.md) §Discovery Watchlist · [PR2_PREFLIGHT.md](./archive/PR2_PREFLIGHT.md) §14.

**Fork review** *(не раньше ≥50–100 завершённых Intent Records + недели истории + contradiction events)*:

| Fork A | Fork B |
|--------|--------|
| Discovery = **третья ось KIP** | Discovery = **delayed validation** C14–C16 |
| high-Discovery types **отличаются** от high-Recognition | ценность после **2–5 циклов** · temporal evolution |

**RAT phase 2** = recognition on texts only. Fork — на реальных траекториях, не на editorial примерах. **Стоп-условие (AR-010):** Discovery до PR2 = гипотеза; после PR2 = потенциально измеримый объект. См. [TODAY_INTERNAL_PATTERNS_V0.md](./TODAY_INTERNAL_PATTERNS_V0.md) §Стоп-условие.

## 1. `decision_relevance` на Atom

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| `decision_relevance` | enum | ✓ | `very_low` \| `low` \| `medium` \| `high` \| `very_high` |
| `relevance_score` | float 0–1 | ○ | fine-grained; tier = derived thresholds |
| `surface_affinity` | enum[] | ○ | где знание **максимально** полезно — см. §2 |
| `dre_eligible` | bool | ✓ | может войти в Day Reasoning slice |
| `lre_eligible` | bool | ✓ | может войти в Learning Reasoning slice |
| `archive_only` | bool | ✓ | default false; true → не в live slices |

**Правило:** `confidence` и `decision_relevance` **независимы**.

- высокий confidence + very_low relevance → знаем точно, но **не влияет** на решения (кофе утром);
- средний confidence + very_high relevance → **в slice**, но с hedging в copy.

### 1.1 Примеры (канон)

| Claim (пример) | `decision_relevance` | Зачем |
|----------------|---------------------|-------|
| Любит кофе утром | `very_low` | flavor, не decisions |
| Предпочитает работать в тишине | `medium` | format / environment |
| Избегает конфликтов | `high` | goal guidance, risks |
| Склонен к перегрузке | `very_high` | daily focus, goal realism, slip risk |
| Часто переоценивает сроки | `very_high` | goal loop, Intent Model |

---

## 2. `surface_affinity` (куда попадает)

| Surface | Engine | Типичные atoms |
|---------|--------|----------------|
| `daily_focus` | DRE | overload, priorities, slip patterns |
| `goal_guidance` | DRE | intent patterns, overestimate, HDM traits |
| `discovery` | LRE | high-uncertainty + **high** relevance gaps |
| `weekly_review` | DRE+LRE | `person_evolution`, phase changes |
| `negative_guardrail` | DRE | suppress, «не говорить сегодня» |
| `training_export` | AMLL | very_high + resolved contradictions |

Один atom может иметь **несколько** affinities. Selection — по surface запроса + relevance tier.

---

## 3. Как назначается relevance

**v1 — три источника (детерминированные, не LLM invention):**

| Источник | Как |
|----------|-----|
| **Claim registry** | default tier per `domain` + `claim` ([USER_KNOWLEDGE_MODEL.md](pim/USER_KNOWLEDGE_MODEL.md) §3) |
| **Empirical lift** | atom correlated с goal outcomes / contradiction impact → tier ↑ |
| **User utility** | save / «это про меня» / dismiss на guidance с atom ref → tier adjust |

**Запрещено:** все atoms `medium` by default; relevance только из LLM narrative.

### 3.1 Registry defaults (illustrative)

| Domain / claim family | Default tier |
|-----------------------|--------------|
| `intent.overestimate_*`, `discipline.overload_*` | `very_high` |
| `trait.*`, `stress_*`, HDM dimensions | `high` |
| `timing.*`, `format.*` | `medium` |
| `interest.*` (без decision link) | `low`–`medium` |
| preference trivia, ritual flavor | `very_low` |

Новый claim — PR + default tier в registry.

---

## 4. Context Selection (C17 slice)

**CUM / Gate** — не «все `llm_eligible`», а **ranked top-K**:

```
1. validity_status = current
2. surface_affinity ∋ requested_surface
3. sort: decision_relevance (tier) DESC → relevance_score → confidence
4. cap: DRE 12–18 atoms · LRE 8–15 · Gate total 15–30
5. always include: negative/suppress if dre_eligible (small cap)
6. exclude: archive_only · historical · very_low (unless explicit review surface)
```

**Training export:** prefer `very_high` + `high` + Contradiction resolution rows; sample `low` for hard negatives.

---

## 5. DRE / LRE и C17

| Engine | Selection bias |
|--------|------------------|
| **DRE** | `dre_eligible` ∧ high/very_high relevance ∧ current validity · IM active record |
| **LRE** | `lre_eligible` ∧ (high relevance **или** high uncertainty on high-impact claim) |

LRE **не** тратит discovery budget на very_low relevance atoms — даже если curiosity высокая.

---

## 6. Gates (engineering)

| ID | Gate |
|----|------|
| **C17** | Каждый pattern/hypothesis/trait-like atom имеет `decision_relevance` + `dre_eligible` / `lre_eligible` |
| **C17a** | Context Selection сортирует по relevance, не только confidence |
| **C17b** | `archive_only` atoms never в live DRE/LRE/Gate |
| **C17c** | Claim registry entry включает default relevance tier |

**Reject:** PIM slice = all atoms where `confidence > 0.5`; новый claim без default relevance.

---

## 7. Changelog

| Дата | Изменение |
|------|-----------|
| 2026-06-23 | v1.0.8 — §0.5 Reusability; AR-009 Knowledge as Asset Illusion; 4-axis policy |
| 2026-06-23 | v1.0.7 — §0.3 stop condition AR-010; PR2 creates observable Discovery |
| 2026-06-23 | v1.0.6 — Discovery Watchlist; fork open until prod IR; no protocol/engine |
| 2026-06-23 | v1.0.5 — §0.3 temporal asymmetry; Discovery fork; AR-006; RAT vs longitudinal |
| 2026-06-23 | v1.0.5 — §0.4 Acquisition Cost · Observability · Knowledge ROI · AR-008 |
| 2026-06-23 | v1.0.4 — §0.2 Discovery relevance; 3-axis KIP; AR-005 |
| 2026-06-23 | v1.0.3 — RRM candidate KIP; store vs acquire |
| 2026-06-23 | v1.0.2 — RRM matrix; RAT knowledge value |
| 2026-06-23 | v1.0.1 — §0.1 Recognition Relevance (RAT/RRM hypothesis); link INTERNAL_PATTERNS |
| 2026-06-23 | v1.0 ACCEPTED — decision_relevance; surface_affinity; CUM ranking; C10–C16 vs C17 split |
