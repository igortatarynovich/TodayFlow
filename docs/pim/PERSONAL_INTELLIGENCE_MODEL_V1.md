# Personal Intelligence Model v1 (PIM)

**Статус:** `ACCEPTED` — **центральный объект** системы TodayFlow.  
**Версия:** 1.5 (2026-06-23)  
**Владелец:** Product + Intelligence + Engineering

**North star:**

> Мы строим **не** приложение с Таро и **не** приложение с прогнозами.  
> Мы строим систему, которая **постепенно строит всё более точную модель человека**.  
> Карта, число, цель, вопросы и рефлексия — **механизмы сигналов** и ежедневного контакта.

**Связь (не путать термины):**

| Термин | Что это |
|--------|---------|
| **PIM** (этот документ) | **Артефакт** — структурированная модель человека (главный актив) |
| **PIL** | **Слой-процесс** — pipeline обновления PIM, context selection, gate — [PERSONAL_INTELLIGENCE_LAYER.md](./PERSONAL_INTELLIGENCE_LAYER.md) |
| **Knowledge Atom** | **Единица знания** внутри PIM — [USER_KNOWLEDGE_MODEL.md](./USER_KNOWLEDGE_MODEL.md) §2 |
| **Intent Model (IM)** | **Подграф PIM** — история намерений — [INTENT_MODEL_V1.md](../INTENT_MODEL_V1.md) |
| **Contradiction** | **События смены мнения** — [CONTRADICTION_AND_REEVALUATION_V1.md](../CONTRADICTION_AND_REEVALUATION_V1.md) |
| **Temporal Identity** | **Время и природа изменений** — [TEMPORAL_IDENTITY_V1.md](../TEMPORAL_IDENTITY_V1.md) |
| **Decision Relevance** | **Приоритет для решений** — [DECISION_RELEVANCE_V1.md](../DECISION_RELEVANCE_V1.md) |
| **HDM** | **Подграф PIM** — модель принятия решений — [HUMAN_DECISION_MODEL_V1.md](../HUMAN_DECISION_MODEL_V1.md) |
| **CUM** | **Compact export** PIM для Gate/UI — [USER_MODEL_TARGET_STATE.md](./USER_MODEL_TARGET_STATE.md) |
| **AMLL** | Экономика LLM-вызовов, training records — [API_MEMORY_AND_LEARNING_LAYER.md](../API_MEMORY_AND_LEARNING_LAYER.md) |
| **Experiences** | Интерфейсы (Today, Profile, …) — **не** центр |

**Долгосрочная цель:** обучение **собственной модели** … — не отдельный проект, а следствие архитектуры.

**Критерий успеха продукта:** [PIM_PRODUCT_NORTH_STAR.md](../archive/PIM_PRODUCT_NORTH_STAR.md) — завершённый цикл → ценность PIM ↑.

---

## 0. Четыре слоя (канон)

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 4 — EXPERIENCES (интерфейсы)                          │
│  Today · Calendar · Tarot · Profile · Goals · Reflection …  │
└───────────────────────────┬─────────────────────────────────┘
                            │ produce / consume
┌───────────────────────────▼─────────────────────────────────┐
│  Layer 3 — REASONING (два двигателя — не смешивать)          │
│  Day Reasoning · Learning Reasoning                            │
└───────────────────────────┬─────────────────────────────────┘
                            │ reads / writes
┌───────────────────────────▼─────────────────────────────────┐
│  Layer 2 — PERSONAL INTELLIGENCE MODEL (PIM)  ★ ЦЕНТР ★      │
│  Traits · Motivations · Decision Style · Goals · Confidence  │
└───────────────────────────┬─────────────────────────────────┘
                            │ fed by
┌───────────────────────────▼─────────────────────────────────┐
│  Layer 1 — SIGNALS (источники, не владеют пользователем)     │
│  карта · число · астрология · цель · discovery · behavior …  │
└─────────────────────────────────────────────────────────────┘
```

**Today — не центр.** Today — **один experience**, который генерирует сигналы и показывает output Reasoning+PIM.

**Смена парадигмы (как Reference vs Runtime в HostFlow):**

| Было (ошибочная интерпретация) | Стало (канон) |
|--------------------------------|---------------|
| экран Today | **потребитель PIM** |
| экран Profile | **потребитель PIM** |
| экран Goals | **потребитель PIM** |
| Discovery / Reflection | **потребители PIM** |

Experiences **не владеют** знанием. Они **читают** PIM и **пишут** signals → (ILR) → atoms.

---

## 1. Layer 1 — Signals

Сигналы **не принадлежат** Today Screen. Они **питают PIM**.

| Источник | Signal types | Experience |
|----------|--------------|------------|
| Tarot pick / meaning | symbolic_choice, card_id | Today ritual |
| Numerology pick | number_choice, day_number | Today ritual |
| Astrology / calendar | transit_fact, sky_event | Today S0, Reference |
| Day goal set / outcome | goal_text, goal_result | Today Goal Loop |
| Discovery answer | discovery_answer, hypothesis_delta | Today S9/S10 |
| Evening reflection | reflection_text | Today S10 |
| Primary action | action_done / skip | Today S9 |
| Open/return times | session_timing | L2 behavioral |
| Calendar marks | rhythm, streaks | Calendar |
| Goal history (100+) | goal_patterns | Goals / HDM |
| Profile facts | identity_anchor | Profile onboarding |

**Правило:** каждый signal → **event** → (PIL) → **Interpretation Instance(s)** → (confirmation) → **atom candidate** — не signal → interpretation-atom напрямую для inferred claims.

**Запрещено:** signal → OpenAI без PIM path; signal → atom как вывод о человеке без ILR + `evidence_chain` (**C14**).

### 1.1 Signal vs Interpretation (HARD — C14)

**Главный риск PIM после C13 — загрязнение интерпретациями**, не нехватка данных.

| | **Signal** | **Interpretation** |
|---|------------|-------------------|
| **Что** | что **реально произошло** | что система **думает** |
| **Примеры** | поставил цель; не выполнил; открыл 08:13; пропустил вечер; ответил на Discovery | избегает конфликтов; переоценивает себя; много задач; лучше под дедлайном |
| **Где** | Events · Intent Record · behavioral log | **Interpretation Instance** → **Knowledge Atom** |
| **На один паттерн** | один факт | **много** конкурирующих гипотез |

```
Signal:  7× goal outcome = no
    → Interpretation candidates (weighted, ILR):
        · цели слишком амбициозные
        · цели вечером, не утром
        · цели вне приоритетов
        · ✗ shortcut «ленивый» (L4 — не atom без extra gate)
    → Confirmation / competing evidence
    → Atom: intent.overestimate_frequency
       evidence_chain → 7× intent_record_id
```

**Intent Record = signals.** **Atom = promoted interpretation** с доказуемостью. См. [INTERPRETATION_LAYER_AND_REFERENCE.md](../explainability/INTERPRETATION_LAYER_AND_REFERENCE.md).

**Gate C14:** ни один atom без **цепочки наблюдений** (`evidence_chain[]`). PIM отвечает «почему правда?» через конкретные events/records, не только `source`.

**Ценность для own model:** Variant B dataset — observations + interpretations + **contradiction resolution trace** ([CONTRADICTION_AND_REEVALUATION_V1.md](../CONTRADICTION_AND_REEVALUATION_V1.md)).

### 1.2 Contradiction & Re-evaluation (C15)

**Следующий риск после C14:** PIM копит **устаревшие** мнения — только reinforcement, без смены модели.

| Новый сигнал | Исход | Артефакт |
|--------------|-------|----------|
| Подтверждает atom | Reinforce | `last_confirmed_at` ↑ |
| Оспаривает atom | Contradict | **Contradiction Event** → Re-evaluation |
| Делает рамку неактуальной | Supersede | retire atom + spawn hypothesis |

**Запрещено:** contradicting signal → только `confidence -= Δ` без Contradiction Event и resolution trace.

См. [CONTRADICTION_AND_REEVALUATION_V1.md](../CONTRADICTION_AND_REEVALUATION_V1.md) — полный канон C15.

### 1.3 Temporal Identity (C16)

**Риск после C15:** путать **рост человека**, **ошибку модели** и **смену контекста**.

| `change_nature` | Смысл |
|-----------------|-------|
| `model_error` | гипотеза была неверна — не «человек изменился» |
| `person_evolution` | устойчивое изменение поведения во времени |
| `context_shift` | верно в одном контексте (work / family / ситуация), не глобально |

Каждый atom + каждый resolved Contradiction отвечает: **когда правда? · всё ещё правда? · что изменилось?**

См. [TEMPORAL_IDENTITY_V1.md](../TEMPORAL_IDENTITY_V1.md) — `valid_from` / `valid_until`, `temporal_scope`, historical PIM.

### 1.4 Decision Relevance (C17)

**C10–C16:** что знаем · почему · когда · почему перестало.  
**C17:** **что из знания важно для помощи** — ranking для DRE, LRE, Gate, training.

См. [DECISION_RELEVANCE_V1.md](../DECISION_RELEVANCE_V1.md).

---

## 2. Layer 2 — Personal Intelligence Model (PIM)

**Это то, что должна учить собственная модель** — не «LLM для красивого текста», а **модель человека**.

**PIM — не набор полей профиля.** Главный объект внутри PIM — **Knowledge Atom** ([USER_KNOWLEDGE_MODEL.md](./USER_KNOWLEDGE_MODEL.md) §2).

Через год главный вопрос — не «что мы знаем?», а **«почему мы считаем, что знаем?»**  
Ответ: у каждого atom — тип, значение, confidence, **provenance**, **decay**.

### 2.1 Knowledge Atom — единица PIM

Минимальный канон полей (полная схема — UKM):

| Поле | Роль |
|------|------|
| `knowledge_type` | `fact` \| `pattern` \| `hypothesis` |
| `value` | score, enum, struct |
| `confidence` | 0–1 |
| `provenance` | channel, signals, interpretation refs |
| `evidence_chain` | конкретные наблюдения → atom (**C14**) |
| `first_seen_at` | когда впервые появилось |
| `last_confirmed_at` | последнее подтверждение / reinforcement |
| `decay_strategy` | как устаревает без подкрепления |
| `valid_from` / `valid_until` | окно истинности (**C16**) |
| `temporal_scope` | enduring \| phase \| context_bound \| situational_episode |
| `change_nature` | при retire — model_error \| person_evolution \| context_shift |
| `decision_relevance` | насколько важно для решений (**C17**) |

**Запрещено:** trait/decision_style в UI или LLM как «факт» без atom + confidence + provenance.  
**Запрещено:** все atoms в slice по confidence alone — нужен **C17** rank.

### 2.2 Структура PIM (канон v1.1)

```
User / PIM
 ├─ knowledge_atoms[]       # ★ PRIMARY
 ├─ contradiction_events[]  # C15 — open/resolved re-evals
 ├─ intent_model            # подграф — [INTENT_MODEL_V1.md](../INTENT_MODEL_V1.md)
 ├─ hdm                     # подграф — [HUMAN_DECISION_MODEL_V1.md](../HUMAN_DECISION_MODEL_V1.md)
 ├─ materialized_views      # удобные проекции (не source of truth)
 │   ├─ traits[] · motivations[] · fears[]
 │   ├─ decision_style · communication_style
 │   ├─ stress_patterns[] · growth_areas[]
 │   ├─ life_priorities[] · current_state
 │   └─ behavioral_patterns[]
 └─ meta
      ├─ version
      ├─ last_signal_at
      └─ training_eligibility
```

**Views** — read models из atoms; **не** пишутся напрямую из Experience.

**CUM** — **top-K projection** by **decision_relevance** (C17) + surface, 15–30 atoms — не полный dump.

### 2.3 Intent Model — домен намерений

Не список целей. **История намерений:** declare → action → outcome.

См. [INTENT_MODEL_V1.md](../INTENT_MODEL_V1.md) — Intent Records, signal hierarchy (цели >> mood), derived patterns как atoms.

### 2.4 Обновление PIM (приоритет сигналов)

| Приоритет | Источник | Частота |
|-----------|----------|---------|
| **P0** | Post-goal behavior (что сделал после цели) | continuous |
| **P1** | Goal outcome (достиг / нет) | daily evening |
| **P2** | Goal text + themes (постановка) | daily morning |
| P3 | Ritual choices (card, number) | daily |
| P4 | Behavioral (timing, completions) | continuous |
| P5 | Discovery answers | targeted |
| P6 | Profile explicit facts | rare anchor |

**Own model training target:** предсказывать/обновлять **atoms** из signals — не генерировать гороскоп.

---

## 3. Layer 3 — Reasoning (два двигателя)

**Запрещено смешивать** Day Reasoning и Learning Reasoning в одном prompt / одной функции без явной границы.  
Иначе через месяцы «что важно сегодня» и «какую гипотезу проверить» начнут конфликтовать.

### 3.1 Day Reasoning Engine (DRE)

**Задача:** помочь **прожить день**.

| Вопрос | Output |
|--------|--------|
| Что сегодня важно **этому** человеку? | `daily_focus_id` |
| Какая цель реалистична? | goal suggestions S6 |
| Где вероятен срыв? | `primary_risk` |
| Что подсветить? | do/avoid |
| Что **лучше не говорить** сегодня? | negative guardrails |

**Inputs:** PIM slice — **relevance-ranked** current atoms + IM active record + day context.

### 3.2 Learning Reasoning Engine (LRE)

**Задача:** помочь **лучше понять человека**.

| Вопрос | Output |
|--------|--------|
| Какая гипотеза с макс. uncertainty reduction? | `hypothesis_id` |
| Какой discovery-вопрос задать? | `discovery_question` |
| Каких данных не хватает в PIM? | `data_gap[]` |
| Какой signal собрать следующим? | acquisition hint (internal) |

**Inputs:** PIM atoms — low confidence **на high-relevance** claims; IM patterns; HDM gaps.

### 3.3 Общие правила

**Outputs обоих:** structured decisions — **не** финальный пользовательский текст (текст = Layer 4 polish via gated LLM или template).

**Orchestration:** Experience запрашивает DRE и/или LRE **явно** (Today S5/S8 → DRE; S9/S10 discovery → LRE).

---

## 4. Layer 4 — Experiences

Интерфейсы взаимодействия с PIM. **Потребители** модели, **не** владельцы знания.

| Experience | PIM read | PIM write (signals → atoms) | Reasoning |
|------------|----------|----------------------------|-----------|
| **Today** | focus, HDM, IM | ritual, **goals**, outcomes, discovery | DRE + LRE |
| **Goals** | IM threads, patterns | long-horizon intents | LRE |
| **Discovery** | hypotheses | answers | LRE |
| **Reflection** | state snapshot | reflection text | LRE |
| **Profile** | identity atoms | explicit facts | — |
| Calendar | rhythm atoms | marks, streaks | DRE |
| Tarot (product) | — | symbolic choices | — |
| Future Coach, Reviews | full slice | outcomes | DRE + LRE |

Спека Today: [TODAY_SCREEN_V1_CANON.md](../TODAY_SCREEN_V1_CANON.md).

---

## 5. Архитектурные границы (HARD)

### 5.1 Запрещённые зависимости

| Запрещено | Почему |
|-----------|--------|
| `Today → OpenAI` (или любой external LLM) **напрямую** | LLM не знает пользователя; тупик без накопления PIM |
| `Experience → LLM` без PIM read | Нет learning asset |
| `Experience → LLM` с пересборкой личности из birth/sign при наличии Snapshot | Personal Model / PIL — модули читают Snapshot, не rediscovery |
| `Tarot / Astrology API → UI` как центр продукта | Это signal sources, не мозг |
| Prompt с full profile / full reference | Token waste; нет PIM slice |
| Ответ LLM → UI без Evaluation + Request Record | AMLL violation |
| Trait в UI как **fact** без confidence | R20 / UKM |

**Code gap vs this section:** [audits/PERSONAL_MODEL_CODE_COMPLIANCE_2026-07-21.md](../audits/PERSONAL_MODEL_CODE_COMPLIANCE_2026-07-21.md).

### 5.2 Обязательная цепочка

**Сейчас (внешний LLM как исполнитель):**

```
Experience (e.g. Today S7)
    ↓ emit signals (learning)
    ↓ request output
PIM read (+ optional PIM write from new signals)
    ↓
Reasoning (DRE and/or LRE — explicit)
    ↓
PIL: Context Selection + Prompt Refinement
    ↓
AMLL: LLM Call Gate (cache → reuse → template → classify → minimal LLM)
    ↓
External LLM  ← получает ТОЛЬКО prepared context, не «пользователя»
    ↓
Evaluation → Experience output → Feedback → PIM update → Training record
```

**Целевое состояние (фаза 5 — [ONTOLOGY_AND_FOUNDATION_PHASES.md](../ONTOLOGY_AND_FOUNDATION_PHASES.md)):**

```
Signals
    ↓
PIM (update + read)
    ↓
Reasoning
    ↓
Own Model  ← замена External LLM для классификации, ranking, copy, PIM update
```

### 5.3 Миграция (не big bang)

| Этап | External LLM | Own model |
|------|--------------|-----------|
| Now | polish copy, narrative | — |
| +dataset | gate, cache, ROI | classifiers on signals |
| +PIM stable | сужение scope | discovery selector, focus ranker |
| Target | fallback only | PIM update, reasoning, primary copy |

Каждый этап **увеличивает** PIM asset, **уменьшает** external token spend ([API_MEMORY_AND_LEARNING_LAYER.md](../API_MEMORY_AND_LEARNING_LAYER.md)).

---

## 6. Today в контексте PIM

| Today phase | PIM | Reasoning | LLM (if any) |
|-------------|-----|-----------|--------------|
| S0 fact | — | pick sky fact | template / reference |
| S5 synthesis | read slice | daily_focus + do/avoid | gated polish |
| S6 goal | **write** goal signals | goal suggestions | optional |
| S7–S8 | read + write | goal risks, HDM-aware copy | gated |
| S9 discovery | read hypotheses | pick question | template-first |
| S10 evening | **write** outcomes + answers | — | minimal |

**PR gate:** новый Today endpoint без строки «какой сигнал в PIM» и «какой slice PIM читает Reasoning» — **reject**.

**PR2 Goal Loop gate (C13):** merge **reject**, если нет Intent Record (A1) … atom path (A6). Guidance-only = UI feature, не PIM.

**Atom gate (C14):** merge **reject**, если atom о человеке без `evidence_chain` через signals + ILR path.

**Contradiction gate (C15):** merge **reject**, если stable atom ослаблен без `contradiction_id` + resolution trace.

**Temporal gate (C16):** retire/supersede без `valid_until` + `change_nature`; enduring без min window.

**Relevance gate (C17):** context slice ranked by `decision_relevance`; claim registry default tier required.

---

## 7. Mapping существующего stack

```
UMTS (зачем)     →  PIM уменьшает uncertainty по §USER_MODEL
KASP / ILR       →  Signal → Interpretation → Knowledge → PIM atoms
UKM              →  storage format для PIM knowledge atoms
PIL              →  процесс вокруг PIM (не дублирует PIM)
AMLL             →  LLM как временный worker
HDM              →  decision subgraph PIM
Today Canon      →  Experience spec Layer 4
```

---

## 8. Changelog

| Дата | Изменение |
|------|-----------|
| 2026-06-23 | v1.0 ACCEPTED — 4 layers; PIM center; deny Today→LLM; migration path to own model |
| 2026-06-23 | v1.1 — Knowledge Atom as PIM unit; Intent Model domain; DRE/LRE split; Experiences as consumers |
| 2026-06-23 | v1.2 — C14 Signal vs Interpretation; evidence_chain gate; ILR mandatory before inferred atoms |
| 2026-06-23 | v1.3 — C15 Contradiction Event; re-evaluation; living model vs archive |
| 2026-06-23 | v1.4 — C16 Temporal Identity; change_nature; historical atoms |
| 2026-06-23 | v1.5 — C17 Decision Relevance; CUM ranking by relevance |
| 2026-07-21 | v1.6 — link Personal Model code compliance audit (no new principle) |
