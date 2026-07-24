# PR2 Pre-flight — Canon vs Code (PIM write-path)

**Дата:** 2026-06-23  
**Статус:** **Pre-flight complete** — достаточен для **планирования** PR2; **код Goal Loop не начат**  
**Следующий шаг:** PR с секциями [PR2_GATE_SECTIONS.md](./PR2_GATE_SECTIONS.md) (когда откроем PR)  
**Канон (уже принят — не дублировать):** [PIM_PR_GATE_V1.md](../pim/PIM_PR_GATE_V1.md) §4 · [INTENT_MODEL_V1.md](../INTENT_MODEL_V1.md) · [TODAY_SCREEN_V1_CANON.md](../TODAY_SCREEN_V1_CANON.md) §4, §9 PR2  
**PR1 baseline:** [PR1_MERGE_VERIFICATION.md](./PR1_MERGE_VERIFICATION.md) — read-path доказан (gen **692**, S0–S5)

---

## Главный вопрос PR2 (не «что увидит пользователь»)

> **Может ли система доказать происхождение любого intent-related знания — от конкретной цели пользователя до конкретного atom candidate — через audit и SQL, без localStorage?**

Если **да** → C10–C17 начинают жить в коде. Если **нет** → сначала storage + audit; UI Goal Loop откладывается.

PR1 доказал **read**. PR2 обязан доказать **write** и **causal chain** (факт цикла), не «красивый Goal Loop» и не наличие atom day-1.

**Intent Record = факт.** Atom candidate = **интерпретация.** Для merge PR2 факт важнее интерпретации — atom job может быть **полностью выключен** и не блокировать merge, если цепочка фактов восстановима.

### Merge gate ≠ PR2 Success *(AR-011)*

| Этап | Вопрос | Критерий |
|------|--------|----------|
| **Merge gate** | Доказан ли **write-path** в коде? | Один live день: causal chain + dual audits · A1–A4 · birth moment · §8 PIM Diff |
| **PR2 Success** | Есть ли **ежедневная полезность** + retention as indicator? | Evening value **then** D7 **then** IR — §15 · AR-012 |

**North Star prod — не retention и не IR.** Полезность завершённого дня; D7 и IR — **индикаторы**. **Sticky ritual trap:** D7 без вечернего «день был лучше» = провал.

**Operating priority *(2026-06-23)*:** **usefulness first** — вечерний ответ сильнее D7. AR-012 · [PIM_PRODUCT_NORTH_STAR](PIM_PRODUCT_NORTH_STAR.md) §0.2.

---

## 0. Сводка: canon vs code

| Область | Канон | Код сегодня | Вердикт |
|---------|-------|-------------|---------|
| FSM S6–S10 | `goal_set` → … → `evening` | `TodayExperiencePhase` заканчивается на `day_synthesis` | **missing** |
| Intent Record | PIM subgraph, append-only | нет таблицы / сервиса | **missing** |
| Goal API | `POST /today/day-goal` → IM + DRE | нет эндпоинта | **missing** |
| Goal events | `day_goal_set`, `day_goal_outcome`, … | только `goal_created` (generic) | **gap / rename** |
| Goal SoT | Intent Model | `DailyGoalSnapshot` (push text) | **reject as SoT** |
| PIM read S8 | slice: IM + atoms + HDM | `pim_read_audit` на guide (PR1) | **extend** |
| PIM write audit | write path traceable | нет `pim_write_audit` | **missing** |
| ILR / atoms | outcome → hypothesis + `evidence_chain` | `UserActiveKnowledge` (day hot path); day_model candidates | **partial / wrong domain** |
| S5 vs S8 boundary | понимание vs guidance с целью | PR1 sentence-filter на S5 | **keep**; S8 — новая surface |

---

## 1. Какие таблицы / модели появляются

### 1.1 Канон требует (PR2 minimum)

| Сущность | Назначение | Owner |
|----------|------------|-------|
| **`intent_records`** (или эквивалент в PIM store) | append-only цикл goal → outcome | **Intent Model** |
| **`meaning_events`** (existing) | +6 PR2 event types | Experience → ingestion |
| **`generation_logs`** (existing) | +guide pass **with goal** + audit | DRE pipeline |
| **Atom candidates / job queue** | async после S10 | UKM / PIL job (не UI) |

Поля Intent Record — [INTENT_MODEL_V1.md](../INTENT_MODEL_V1.md) §1.1 + link `daily_focus_id`, ritual refs ([PIM_PR_GATE_V1.md](../pim/PIM_PR_GATE_V1.md) §4.1).

### 1.2 Что уже есть в коде (не путать с IM)

| Таблица / модель | Файл | Роль сегодня | PR2 |
|------------------|------|--------------|-----|
| `DailyGoalSnapshot` | `db/models.py` | текст цели для **push reminder** | **не SoT**; migrate или read-only mirror |
| `WeeklyGoal` / steps | `tracking.py` | недельные цели трекинга | **out of PR2 spine** |
| `UserActiveKnowledge` | `db/models.py` | day_model hot path atoms | **не** intent domain |
| `MeaningEvent` | `db/models.py` | event stream | **extend** types |
| `day_connection.morning_intention` | tracking / today data | legacy текст | **не** Intent Record |

**Reject PR2:** `CREATE TABLE day_goals` owned by Today API без `intent_records` в PIM store ([PIM_PR_GATE_V1.md](../pim/PIM_PR_GATE_V1.md) §4.8).

**Решение до первого коммита PR2:** где физически живёт IM — отдельная таблица `intent_records` + JSON `post_set_actions`, или версионированный blob `user_intent_model`. Канон не требует UI-table; требует **Today disappearance test** и A1–A6.

---

## 2. Кто владелец Intent Record

| | |
|--|--|
| **Owner** | **Intent Model** (PIM subgraph) — [INTENT_MODEL_V1.md](../INTENT_MODEL_V1.md) §2 |
| **Не owner** | Today FSM · React state · `DailyGoalSnapshot` · Evening UI · Goals screen |
| **Evening (S10)** | **signal source only** — пишет event + передаёт outcome в IM service; **не** владеет `outcome` полем |
| **Experience API** | `POST /today/day-goal` — **transport**; persistence через IM service |

**Today disappearance test (PR2):** удалить экран Today → остаются `intent_records`, `day_goal_*` events, generation log с goal in DRE input, atom job rows.

**Код сегодня:** ownership **не реализован** — цель может жить в `localStorage` / `day_connection` / push snapshot без IM.

---

## 2.1 Момент рождения Intent Record *(design spike — критично)*

**Риск PR2:** не ownership и не atoms, а **когда** создаётся record. Слишком рано → мусор в PIM (drafts, previews). Слишком поздно → потеря guidance / post-goal / outcome linkage.

На record ссылаются: guidance, `post_set_actions`, outcome, `evidence_chain`, contradiction, temporal identity. **Неверное «рождение» загрязняет весь downstream.**

### Четыре разных сигнала (не один)

| # | Ситуация | Сигнал | Intent Record? |
|---|----------|--------|----------------|
| 1 | Выбрал **готовую** цель (chip) | UI selection | **Нет** — до submit |
| 2 | **Написал** свою цель | keystrokes in textarea | **Нет** — до submit |
| 3 | **Отредактировал** текст **до** submit | draft edits | **Нет** — draft = UI/local only |
| 4 | Нажал submit, **сразу вышел** | `day_goal_set` fired | **Да** — цикл **открыт**, может остаться без S8/S10 |

Различие 3 vs 4: submit = **commitment signal**; edit-before-submit = **не** commitment.

### Таблица решений (pre-flight default)

| Событие / действие | Создаём Intent Record? | Примечание |
|--------------------|------------------------|------------|
| Открыл экран цели (S6) | **Нет** | optional signal `goal_screen_opened` — **не** IM write |
| Начал печатать | **Нет** | draft в UI state only |
| Выбрал вариант из 3–5 | **Нет** | prefill textarea; не commit |
| Редактировал draft до submit | **Нет** | |
| Нажал «Продолжить» / **submit** | **Да** | `POST /today/day-goal` + `day_goal_set`; `set_at` = moment of submit |
| Submit + ушёл до S8 | **Да** (record exists) | `cycle_status: open`; нет `guidance_shown_at` — **не** откатывать record |
| Вернулся и **изменил цель после submit** | **Amendment или новая версия** — **решить в spike** | см. ниже |

### После submit: amendment vs supersede *(spike, до кода)*

| Стратегия | Когда | Downstream |
|-----------|-------|------------|
| **Amendment** (same `intent_record_id`, new `goal_text`, `amended_at`) | до первого S8 guidance | один id; guidance/actions/outcome на amended text |
| **Supersede** (close old + **new** record) | после S8 или material change | старый record `superseded_by`; новый цикл |
| **Reject** silent overwrite | — | без audit trail |

**Default для spike:** amendment **только до** `guidance_shown_at`; после S8 — supersede (новый record, link `supersedes`).

### Draft vs fact (жёстко)

- **Draft** — React state / optional `localStorage` restore S6; **никогда** в `intent_records`.
- **Fact** — только server ack от `POST /today/day-goal` после submit.
- **`goal_source`:** `user_typed` | `suggested_pick` — фиксируется **на submit**, не на chip click.

**Reject PR2:** create-on-first-keystroke, create-on-S6-mount, create-on-chip-select без submit.

---

Канон ([TODAY_SCREEN_V1_CANON.md](../TODAY_SCREEN_V1_CANON.md) §9, [PIM_PR_GATE_V1.md](../pim/PIM_PR_GATE_V1.md) §4.2):

| Phase | UI | `event_type` (target) | Payload minimum | В `meaning.py`? |
|-------|-----|----------------------|-----------------|-----------------|
| **S6** | **submit** goal (not open/type/pick) | `day_goal_set` | `intent_record_id`, `goal_text`, `goal_source`, `daily_focus_id` | **no** — есть только `goal_created` |
| **S7** | loader | `day_goal_submitted` *(optional)* | `intent_record_id`, request id | **no** |
| **S8** | guidance first paint | `goal_guidance_viewed` | `intent_record_id`, `generation_id` | **no** |
| **S9** | step done/skip | `post_goal_action` / `primary_action_done` / `primary_action_skip` | `intent_record_id`, action id, timing | **partial** — нет intent link |
| **S10** | outcome chips | `day_goal_outcome` | `intent_record_id`, `outcome`, optional note | **no** |
| **S10** | discovery answers | `evening_discovery_answered` | `question_id`, `hypothesis_id` | **no** (PR3+) |

**PR2 minimum chain (merge blocker):** submit S6 → S8 → S10: **`day_goal_set` → `goal_guidance_viewed` → `day_goal_outcome`**, все с одним `intent_record_id`; S8 `generation_id` = guide log **with goal context**.

**Causal chain (primary merge proof):** SQL/audit must reconstruct, **without atom job:**

```
day_goal_set → intent_record row
  → goal_guidance_viewed → generation_log_id (+ pim_read_audit)
  → [post_goal_action*] → post_set_actions on record
  → day_goal_outcome → outcome on record (+ pim_write_audit)
```

Atom candidate — **optional layer on top**, not substitute for this chain.

**Parity:** web + iOS + OpenAPI event dictionary ([TODAY_PERSONALIZATION_CORE.md](../TODAY_PERSONALIZATION_CORE.md) — точечное дополнение при merge, не новый канон).

---

## 4. Где возникает Interpretation Layer

**Канон:** Event ≠ meaning. Outcome на Intent Record — **signal**; trait/pattern — только через ILR → confirmation → atom ([INTERPRETATION_LAYER_AND_REFERENCE.md](../explainability/INTERPRETATION_LAYER_AND_REFERENCE.md), C14).

| Момент | Что происходит | Код сегодня |
|--------|----------------|-------------|
| S6 `goal_text` | explicit signal → optional theme classify (LRE) | нет |
| S8 guidance | DRE **read** atoms — не ILR write | narrative + `knowledge_context_slice` read |
| S10 `outcome` | signal on IM record | evening saves to `day_connection`, не IM |
| **Post-S10 async** | ILR: competing interpretations → atom **candidates** | **нет** ILR engine для intent |
| Day domain (parallel) | `day_model_v1_*_candidate` | есть — **не** подменяет intent ILR |

**`interpretation_orchestrator.py`:** legacy do/avoid builder — **не** ILR. Не использовать как write-path для PR2.

**PR2 boundary:** UI merge **не блокируется** отсутствием ILR job (A6 can be **off** for live pass). Merge **блокируется**, если outcome пишется как **fact** в profile/CUM без atom + `knowledge_type` (A5), или если **causal chain** не восстанавливается.

**Первое появление ILR в PR2:** async job после `day_goal_outcome` — optional for merge; required for **full** A6 before PR3, not PR2 binary gate.

---

## 5. Когда появляется первый Atom Candidate

| When | What | `knowledge_type` | PR2 merge blocker? |
|------|------|------------------|-------------------|
| S6–S9 | **none** (signals only) | — | — |
| S10 submit | outcome on IM only | — | — |
| **S10+ async job** | first **`intent.*` candidate** | `hypothesis` | **No** — A6 scaffold OK; job may be disabled for live pass |

**PR2 success ≠ atom exists.** PR2 success = **causal chain** (§3) + separate audits (§10).

Примеры claims ([PIM_PR_GATE_V1.md](../pim/PIM_PR_GATE_V1.md) §4.3): `intent.overestimate_frequency`, `intent.action_within_2h_rate` — **post-PR2** interpretation layer.

---

## 6. Где строится `evidence_chain`

**Канон ([USER_KNOWLEDGE_MODEL.md](../pim/USER_KNOWLEDGE_MODEL.md) §2):** каждый promoted atom — `evidence_chain[]` с refs на signals / intent records / events.

**PR2 minimum chain for one hypothesis atom** *(when A6 job enabled)*:

```
day_goal_set (event_id)
  → intent_record (intent_record_id)
  → pim_write_audit (create)
  → day_goal_outcome (event_id)
  → pim_write_audit (outcome)
  → [optional] post_goal_action events
  → interpretation_instance_id (ILR job)
  → knowledge_atom candidate (claim, knowledge_type=hypothesis)
```

**Explainability path (6 months later):** «Почему этот atom?» → `evidence_chain` must walk **Signal → Intent Record → Write Audit → ILR → Candidate → Atom**. Without **separate** write audit, chain breaks before C14–C16.

---

## 7. Какие contradiction triggers возникают автоматически

PR2 **не обязан resolve** day-1 ([PIM_PR_GATE_V1.md](../pim/PIM_PR_GATE_V1.md) §4.5). **Обязан** не писать conflicting atom без event.

| Trigger | Example | Expected path |
|---------|---------|---------------|
| Outcome vs ambition | «запущу бизнес» + `no` × N | ILR → `intent.overestimate_*` hypothesis |
| New outcome vs old atom | prior avoid-conflict + achieved social goal | Contradiction registry → re-eval (C15) |
| User dismiss guidance | «не про меня» | `user_corrected` signal |

**Код:** `anti_contradiction_guard` в `interpretation_orchestrator` — text overlap only; **не** C15 stack.

**PR2 pre-flight rule:** contradiction handling = **async / logged**; blocking merge only if sync write creates **fact** from single evening.

---

## 8. PIM Diff после одного полного дня (S0 → S10)

### Before (post-PR1 baseline)

| Artifact | Count |
|----------|-------|
| PR1 `meaning_events` | 6 types |
| `intent_records` | 0 |
| `pim_read_audit` on guide | ✓ |
| `pim_write_audit` | 0 |
| Atoms created (intent domain) | 0 |
| Guide gens without goal | 1+ |

### After (one full PR2 day — expected)

| Artifact | Δ | Proof | Merge? |
|----------|---|-------|--------|
| `intent_records` | +1 | row at **submit** only; `goal_text`, `set_at`, `daily_focus_id` | **yes** |
| `day_goal_set` | +1 | `intent_record_id`; fires **on submit**, not S6 open | **yes** |
| `goal_guidance_viewed` | +1 | `generation_id` linked | **yes** |
| `day_goal_outcome` | +1 | same `intent_record_id`; `outcome` on record | **yes** |
| `post_goal_action` | +0..n | S9 if in scope | no |
| Guide generation (with goal) | +1 | intent in DRE input; **`pim_read_audit`** on gen log | **yes** |
| **`pim_write_audit`** rows | +≥2 | **separate** from read: create + outcome | **yes** |
| Atom candidates | +0..n | async; **job may be off** | **no** |
| CUM / profile trait fields | 0 | A5 | **yes** |

**PR2 merge blockers (binary):**

1. **Causal chain live** — submit → guidance gen → (optional actions) → outcome; one `intent_record_id`; recoverable by SQL + audits **with atom job disabled**.
2. **Live S8** — guidance учитывает committed goal; не дублирует S5 без goal context.
3. **Birth moment** — no record before submit; submit-then-exit leaves valid open record (not draft garbage).

---

## 9. Фазы vs код — что строить / не строить

### PR2 in scope (канон)

| Phase | Product | PIM |
|-------|---------|-----|
| S6 | goal input / 3–5 picks | **create** Intent Record **on submit only** |
| S7 | loader | DRE request audit |
| S8 | goal guidance (second synthesis) | **read** slice IM+atoms+HDM |
| S9 | compact active day + primary step | update `post_set_actions` |
| S10 | outcome first, then discovery | **write** outcome on IM |

### Explicitly out / later

| Item | PR |
|------|-----|
| Discovery scheduler / HDM «обычно ты» | PR3–PR4 |
| Mood / head_topic spine | PR3 |
| iOS `TodayRitualFlowView` parity | track with web; not blocker if events+API stable |
| Full contradiction resolution UI | post-PR2 |
| New canon C18+ | **freeze** |

### Legacy debt (do not extend)

| Code | Action |
|------|--------|
| `TodayRitualFlow` article-scroll | no new goal logic here |
| `DailyGoalSnapshot` | do not make SoT |
| `PrimaryAction` in contract surface | wire to S9 **after** IM exists |
| `interpretation_orchestrator` do/avoid | not ILR write path |
| Evening → `day_connection` only | **change** to IM outcome + keep event |

---

## 10. DRE / audit — read и write **раздельно**

PR1 ввёл **`pim_read_audit`** в `generation_logs.input_payload.orchestration`. PR2 **не** сливает read/write в один blob.

### `pim_read_audit` (unchanged contract, extended fields)

- Lives on **generation** path (S5 guide, S8 goal-guidance gen).
- Proves: какой slice DRE **прочитал** (`pim_slice_used`, `dre_fields_used`, `intent_record_id` when S8).

### `pim_write_audit_v1` (new — IM mutations only)

- Lives on **Intent Model write** path, **not** inside generation log (or linked by `intent_record_id` + `trigger_event_id`).
- Proves: что система **записала** в PIM и **почему** (triggering event).

| Field | Purpose |
|-------|---------|
| `contract_version` | `today_pim_write_audit_v1` |
| `write_target` | `intent_record` |
| `operation` | `create` \| `amend` \| `supersede` \| `update_outcome` \| `update_post_set_actions` |
| `record_id` | `intent_record_id` |
| `fields_written[]` | e.g. `goal_text`, `outcome` |
| `trigger_event_id` | `meaning_events.event_id` for `day_goal_set`, `day_goal_outcome`, … |
| `supersedes` / `amended_from` | version lineage |

**Reject:** single `pim_audit` object mixing read slices and write ops — breaks «why this atom?» forensics.

**Second generation (S8):** guide call with goal in context; **`pim_read_audit`** on that log must reference `intent_record_id`; prior **`pim_write_audit`** row exists for create.

**Full explainability stack:**

```
Signal (meaning_event)
  → Intent Record (fact)
  → pim_write_audit (create / outcome)
  → DRE + pim_read_audit (guidance gen)
  → [ILR job]
  → Atom candidate
  → Atom (post-confirmation)
```

---

## 11. Acceptance map (A1–A6 → code gap)

| ID | Criterion | Code | Status |
|----|-----------|------|--------|
| **A1** | `day_goal_set` → Intent Record | no API, no table | **missing** |
| **A2** | S8 reads PIM slice (IM+atoms+HDM) | read model exists; not wired to goal path | **debt** |
| **A3** | S9 DRE/context includes goal | — | **missing** |
| **A4** | S10 outcome on IM + event | evening → day_connection | **wrong owner** |
| **A5** | no direct trait fact | verify in tests | **verify at implement** |
| **A6** | async atoms + evidence_chain | no intent job | **scaffold** — not PR2 binary gate |

**Guidance-only PR = reject** ([INTENT_MODEL_V1.md](../INTENT_MODEL_V1.md) §5).

**PR2 binary gate:** A1 + A2 + A4 + causal chain + §2.1 birth moment + separate audits. A6 = follow-up, not blocker for first merge.

---

## 12. Gate question (PR2)

> **Может ли система доказать происхождение любого intent-related знания — от конкретной цели пользователя (submit) до конкретного atom candidate — через Signal → Intent Record → Write Audit → Read Audit → ILR → Candidate, без localStorage?**

| Layer | PR1 | PR2 today | PR2 target |
|-------|-----|-----------|------------|
| Read audit | ✓ gen 692 | ✓ | + `intent_record_id` on S8 gen |
| Write audit | — | ✗ | ✓ separate `pim_write_audit` |
| Intent Record (fact) | — | ✗ | ✓ on submit only |
| Causal chain SQL | partial (events only) | ✗ | ✓ goal → guidance → outcome |
| Atom candidate | — | ✗ | optional for merge |

**Если causal chain + write audit нет** → **рано** открывать UI Goal Loop; добить storage + audit first.

---

## 13. Рекомендуемый порядок работ (не кодинг Goal Loop первым)

1. **Design spike (PR section):** §2.1 birth moment + amendment/supersede + IM storage schema.  
2. **Backend:** IM service + **`pim_write_audit_v1`** (separate from read) + `POST /today/day-goal` on **submit only**.  
3. **Live pass script:** causal chain proof with **atom job disabled**.  
4. **Extend** `pim_read_audit` for S8 goal context.  
5. **Frontend FSM** S6–S10 — **after** storage/audit green.  
6. **Async A6** — scaffold + tests; not merge blocker.  
7. **Merge verification:** SQL chain + dual audits filled.  
8. **Discovery Watchlist scaffold** *(non-blocking)* — §14; logging only, no scoring.

---

## 14. Discovery Watchlist *(PR2 learning output — не gate · не протокол)*

**Решение:** fork Discovery **открыт** до prod Intent Records. **Не** проектировать Discovery Validation Protocol или Discovery Engine сейчас — риск проектировать без явления (§Стоп-условие · §Platform Layer Gate · AR-010 · аналог C10–C17 до write-path).

> **До PR2 Discovery = гипотеза. После PR2 = потенциально измеримый объект.** PR2 создаёт не только write-path — PR2 **впервые создаёт возможность наблюдать Discovery**.

**После PR2 merge** — начать **сбор** longitudinal материала для потенциальных инсайтов. **Без интерпретации** · без tier assignment · без влияния на DRE/LRE ranking.

| Поле | Тип | Описание |
|------|-----|----------|
| `first_seen_at` | timestamp | первое появление |
| `source_intent_record_ids` | uuid[] | Intent Records-источники |
| `source_discovery_answers` | ref[] | discovery question answers *(если есть)* |
| `reappeared_count` | int | повторные появления в цикле |
| `user_self_reference_count` | int | явные self-reference |
| `linked_future_goals_count` | int | последующие цели |
| `linked_future_outcomes_count` | int | связанные outcomes |

**Хранение:** observability table / JSON append log / PIL event stream — **implementation choice at PR2**; канон не требует отдельного engine.

**Fork review trigger** *(не PR2 gate)*: ≥50–100 **завершённых** Intent Records · несколько недель · первые contradiction events. Критерии fork A/B — [TODAY_INTERNAL_PATTERNS_V0.md](../TODAY_INTERNAL_PATTERNS_V0.md) §Discovery fork.

**PR2 binary gate:** Watchlist **не блокирует** merge (как A6). Causal chain + write audit важнее.

---

## 15. PR2 Success Criterion *(post-deploy · AR-012)*

**Merge gate (§8)** = write-path в коде. **Success** = **ежедневная полезность**; retention и IR — **индикаторы / byproducts**.

### Главный вопрос

> Что пользователь получает **вечером**, чего не было бы **без** TodayFlow?

Слабый ответ → D7 не спасёт. Сильный → retention и IR **следствие**.

### Primary — usefulness *(qual + quant proxies)*

| Сигнал | Для чего |
|--------|----------|
| **Evening value statement** | «День был лучше благодаря TodayFlow» *(interviews / in-app)* |
| **Ясность · фокус · сделанное важное** | Продуктовая ценность §0.2 PIM North Star |
| **S10 closure без guilt** | Завершение с ощущением пользы |

### Behavioral indicators *(not North Star)*

| Метрика | Роль |
|---------|------|
| **D1 / D7 / D10** | Индикатор, что польза **реальна** |
| **≥5 return / 14d** | Привычка как **следствие** результата |
| **Sticky ritual trap reject** | D7 хороший · вечер слабый → **fail** |

### Tertiary — IR *(only if usefulness + retention met)*

Completed lifecycles · recoverable chains · repeat IR — для fork review, не для sprint goal.

### Не требуется

Discovery / IPL / KIP · IR count as primary KPI

### Требуется

Evening screen test пройден для S0–S10 · write-path не ломает вечернюю пользу

См. [PIM_PRODUCT_NORTH_STAR.md](PIM_PRODUCT_NORTH_STAR.md) §0.2 · AR-012.

---

## Changelog

| Дата | Изменение |
|------|-----------|
| 2026-06-23 | §15 revised — retention primary, IR byproduct; AR-012 |
| 2026-06-23 | §15 PR2 Success Criterion — data metrics, 30-day targets, merge ≠ success; AR-011 |
| 2026-06-23 | §Platform Layer Gate link; AR-010 |
| 2026-06-23 | §14 + §Стоп-условие link; PR2 creates observable Discovery; AR-010 |
| 2026-06-23 | §14 Discovery Watchlist — observation scaffold; fork open; not PR2 gate |
| 2026-06-23 | Pre-flight: entity map S6–S10 vs code; A1–A6 gaps; PIM Diff template; PR1 baseline linked |
| 2026-06-23 | §2.1 Intent Record birth moment; causal chain > atom for merge; separate read/write audit; harder gate Q |
