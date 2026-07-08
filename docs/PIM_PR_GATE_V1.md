# PIM PR Gate v1 — проверка PR через стек C10–C17

**Статус:** `ACCEPTED` — **обязательный gate** для PR1, PR2 и далее.  
**Версия:** 1.5 (2026-06-23)  
**Владелец:** Engineering + Product

**North star продукта:** [PIM_PRODUCT_NORTH_STAR.md](./PIM_PRODUCT_NORTH_STAR.md) — завершённый день → ценность PIM ↑.

**North star вопрос ревью:**

> Не только «экран открывается / кнопка работает / текст показывается».  
> **Чему научилась система?**

**Жёсткое правило:** PR, который проверяется **только** открытием Today → **reject** (для learning surfaces).

**Критерий качества (одна строка):**

> Каждый завершённый дневной цикл должен оставлять **больше знания в PIM**, чем было до его начала.  
> День закончился, PIM не стал богаче → Experience сработал, **платформа не развилась** → gate **fail**.

**Freeze:** **не** придумывать C18+, пока C10–C17 не прошли через код и не столкнулись с реальностью.

**Platform Layer Gate (C18+):** новый платформенный слой — только если **устойчивое наблюдаемое явление** нельзя объяснить текущим стеком. Gate question: *«Какое явление не объясняется существующими слоями?»* — нет ответа → слой не нужен. См. [TODAY_INTERNAL_PATTERNS_V0.md](./TODAY_INTERNAL_PATTERNS_V0.md) §Platform Layer Gate · AR-010. **C18 freeze = защита архитектуры**, не только пауза на документы.

**Риск сейчас:** не недостаток архитектуры, а **упрощённые реализации**, тихо обходящие C10–C17.

---

## 0. Замкнутый цикл (ядро платформы)

```
Signal → Intent → Evidence → Interpretation → Contradiction → Temporal Identity → Relevance → Reasoning → Experience → Signal
```

| Canon | Что решает |
|-------|------------|
| **C10** | Что такое знание (Atom) |
| **C11** | Что такое намерение (Intent Model) |
| **C12** | DRE vs LRE |
| **C13** | Goal Loop учит PIM |
| **C14** | Знание = доказательства |
| **C15** | Смена мнения |
| **C16** | Время и природа изменения |
| **C17** | Ценность для решений |

Это **не набор экранов** — это ядро. PR оценивается через этот стек, не только через UI.

### 0.1 Три контура acceptance (независимые)

Раньше существовал в основном **первый** — можно было месяцами улучшать экраны и не приближаться к собственной модели.

| Контур | Вопрос | Инструменты gate |
|--------|--------|------------------|
| **Experience** | Пользователю стало **понятнее и полезнее**? | UI smoke, copy, [TODAY_LANGUAGE_V1.md](./TODAY_LANGUAGE_V1.md) |
| **Architecture** | Соблюдены **C10–C17** и **ownership**? | §1.1, §1.2, anti-patterns §2 |
| **Learning** | Система стала **умнее** после взаимодействия? | **PIM test**, **PIM Diff**, **Learning Δ** §1.5 |

**Merge learning surface** (Today · Goal · Discovery · Reflection) требует **все три**. Чистый visual/CSS — Experience only, Learning Δ N/A (явно в PR).

---

## 1. Пять вопросов каждого PR (обязательно в описании)

Если нет ответа — фича **только на уровне интерфейса**, merge **reject**:

| # | Вопрос | Минимальный ответ |
|---|--------|-------------------|
| **Q1** | Какой **новый signal** появился? | `event_type`(ы) + payload |
| **Q2** | Куда попадает в **PIM**? | Intent Record / atom candidate / read slice |
| **Q3** | Какой **atom** может обновиться? | `knowledge_id` / claim / domain или «read-only PR» |
| **Q4** | Какой **evidence** появляется? | `evidence_chain` append / Intent field / event id |
| **Q5** | Какой **DRE или LRE** consumer? | surface + relevance tier |

**Шаблон в PR description:**

- `## PIM (C10–C17)` — Q1–Q5  
- `## PIM Ownership` — §1.1 на каждое новое поле  
- `## Today disappearance` — §1.2  
- `## PIM Diff` — §1.4  
- `## Learning Δ` — §1.5  
- `## PIM ROI` — §1.6 (новые сценарии / roadmap)

### 1.1 Порядок владения данными (на каждое новое поле)

Заполнение Q1–Q5 **недостаточно**, если данные физически живут в слое Experience.

| Вопрос | Правильный ответ (типично) |
|--------|---------------------------|
| **Кто владелец данных?** | **PIM** (Intent Model · UKM store) |
| **Кто создал signal?** | Experience (Today · Evening · Goals UI) |
| **Кто интерпретирует?** | **ILR** → atom; **LRE** для discovery gaps |
| **Кто потребляет?** | **DRE** · Discovery · Weekly Review |
| **Может ли Today удалить знание?** | **Нет** — только user / PIM policy |

**Правило HostFlow:** сначала **источник истины**, потом потребители — не наоборот.

См. [DATA_OWNERSHIP_AND_CONSUMPTION_MAP.md](./DATA_OWNERSHIP_AND_CONSUMPTION_MAP.md).

### 1.2 Тест «Today исчез»

> Если завтра **Today исчезнет**, сохранится ли смысл этого знания **внутри PIM**?

| Ответ | Вердикт |
|-------|---------|
| **Да** — Intent Records, atoms, evidence остаются | ✓ правильный слой |
| **Нет** — знание только в `day_goals` / local state / evening form | ✗ **reject** — данные у Experience |

**PR2 успешен** только если мысленно удалив экран Today, остаются:

- Intent Records  
- Evidence Chains  
- Atoms  
- Contradictions (когда появятся)  
- Relevance metadata  

Если вместе с экраном исчезает знание — оно было создано **не в том слое**.

### 1.3 Два типа проверки: Experience vs PIM

PR **обязан** быть проверяем **через PIM без UI**.

| | **Experience test** | **PIM test** |
|---|-------------------|--------------|
| **Вопрос** | Что увидел пользователь? | Какое **знание** появилось или изменилось? |
| **Как** | Открыть Today, UI, скриншот | API / DB / audit log / job queue |
| **Достаточно для merge?** | Нет (после C10–C17) | **Да** — вместе с Experience smoke |

Если для приёмки фичи нужно только «открыть экран и посмотреть, что нарисовалось» — это **Experience-level** тест. Merge без **PIM test** — **reject** (кроме чистого copy/CSS без learning surface).

### 1.4 PIM Diff (обязательная секция PR)

Зафиксировать **до** и **после** одного полного сценария (для PR2 — S6→S10):

```markdown
## PIM Diff

| Артефакт | До | После сценария | Δ |
|----------|-----|----------------|---|
| Intent Records | 0 | 1 | +1 |
| meaning_events (signals) | N | N+k | +k (перечислить types) |
| Interpretation Instances | … | … | … |
| Atom candidates (job queue) | … | … | +K |
| Atoms (committed) | X | X' | … |
| evidence_chain entries | … | … | +M |
| Contradiction Events | Y | Y' | … |

Как проверено без UI: `GET …` / SQL / pytest fixture / audit log path
```

**PR2 — минимум после полного дня:**

| Проверить | Не достаточно |
|-----------|----------------|
| Intent Record +1 | «цель сохранилась» в UI |
| signals `day_goal_set`, `post_goal_action`, `day_goal_outcome` | guidance показался |
| `guidance_shown_at` на record | outcome в форме вечера |
| atom job enqueued (candidates) | только narrative response |
| relevance defaults на candidates | — |

### 1.5 Learning Delta Test

**Формализация:** после прохождения сценария должен произойти **хотя бы один** из:

| # | Learning Δ (достаточно одного) | Canon |
|---|-------------------------------|-------|
| L1 | Новый **signal** | Events → PIM |
| L2 | Новая **interpretation** (instance / candidate) | ILR |
| L3 | Усилен существующий **atom** (reinforce, evidence append) | C14 |
| L4 | Возник **contradiction** | C15 |
| L5 | Обновилась **temporal identity** (`valid_*`, `change_nature`) | C16 |
| L6 | Изменился **relevance** score / tier | C17 |

```
Learning Δ = 0  →  PIM Δ = 0  →  PR подозрителен
```

| Тип PR | Learning Δ = 0 |
|--------|----------------|
| Today · Goal · Discovery · Reflection · новый learning path | **красный флаг** → reject по умолчанию |
| Чистый visual / CSS / copy без нового surface | допустимо — указать **N/A** в PR |
| PR1 ritual (S0–S5) | минимум **L1** (signals +Δ); atoms optional |

**PIM Diff** (§1.4) — **измерение** Learning Δ; не заменяет его логикой.

**Связь с §2.1:** guidance показан, Learning Δ = 0 — классический ложноположительный результат.

### 1.6 PIM ROI (новые сценарии и roadmap)

См. [PIM_PRODUCT_NORTH_STAR.md](./PIM_PRODUCT_NORTH_STAR.md) §5.

| Вопрос | Заполнить в PR |
|--------|----------------|
| Что получает **пользователь**? | focus / guidance / insight / … |
| Что получает **PIM**? | signal types · evidence · contradiction · atoms |
| **Стоит ли** стоимость реализации? | да/нет + кратко |

**Низкий PIM ROI** (анимации, новая колода, лишний гороскоп-блок) — не reject автоматически, но **не P0** без явного Experience-only обоснования.

**Высокий PIM ROI, скучный UI** — приоритет над «красивым» сценарием с Learning Δ ≈ 0.

---

## 2. Anti-patterns (ловить на review)

| Обход | Canon | Reject |
|-------|-------|--------|
| Guidance без PIM read | C9, C13 | ✓ |
| Goal только local / только narrative | C13, R23 | ✓ |
| Trait из одного outcome | C14, R24 | ✓ |
| Atom без `evidence_chain` | C14 | ✓ |
| `confidence` tweak без Contradiction | C15 | ✓ |
| Retire без `change_nature` | C16 | ✓ |
| Slice = all `confidence > 0.5` | C17 | ✓ |
| Experience → LLM direct | C9 | ✓ |
| `day_goals` / `day_goal_outcomes` **owned by Today** | §1.1, C11 | ✓ |
| Outcome на **Evening Reflection** entity, не IM | §4.8 | ✓ |
| Intent Record в ritual/local state only | C13, §1.2 | ✓ |
| **Guidance generated → PIM unchanged** | §1.3, §2.1 | ✓ |
| Merge с только Experience test | §1.3, §1.5 | ✓ |
| **Learning Δ = 0** на learning surface | §1.5 | ✓ (red flag) |
| «Сделаем atoms в PR3» без events сейчас | C10 | ⚠️ только если PR явно read-only + events |

### 2.1 «Guidance generated → ничего в PIM»

Самый опасный **ложноположительный** результат PR2.

| Пользователь видит | Платформа |
|--------------------|-----------|
| цель поставлена ✓ | PIM **не изменился** |
| совет получен ✓ | знание **не появилось** |
| день прожит ✓ | own model **не научилась** |

По сути — **direct LLM call** за красивым экраном. **Reject:** PIM Diff Δ=0; **Learning Δ = 0** (§1.5).

---

## 3. PR1 — spine + Daily Focus (верификация)

**Scope канона:** S0–S5 · gates · restore · 5 cards · `daily_focus_v1`.

### 3.1 Ожидание по стеку

| Phase | Q1 Signal | Q2 PIM | Q3 Atom | Q4 Evidence | Q5 Consumer |
|-------|-----------|--------|---------|-------------|-------------|
| **S0** greeting | `day_opened`, `day_sky_fact_viewed` | read: — | — | event ids | DRE: pick fact (template) |
| **S1–S2** tarot | `tarot_selected`, `tarot_revealed` | write: signal only | optional `interest.*` hypothesis **не в PR1** | `card_id` in events | DRE: synthesis input |
| **S3–S4** number | `number_selected` | write: signal only | — | `numerology_value`, `revealed` | DRE |
| **S5** synthesis | `first_synthesis_viewed` | **read** PIM slice (C17 rank) | — (DRE **output** `daily_focus_id`, не atom) | `pim_slice_*` audit + ritual context | **DRE** → **Daily Focus only** |

**S5 boundary (reject):** после S5 — **«о чём день»**, не **«как прожить с моей целью»**. Нет goal UI / `PrimaryAction` / goal-linked guidance (PR2).

**PR1 может быть read-heavy:** atoms не обязаны persist; **events обязаны** (§3.1.2); S5 **обязан** PIM read **с audit** (§3.1.1), не checkbox.

#### 3.1.1 PIM read audit (anti–fake integration)

| Audit | Когда |
|-------|-------|
| `pim_slice_requested` | до merge slice в DRE |
| `pim_slice_used` | после merge (`atom_ids[]` может быть `[]`) |
| `dre_fields_used` | поля, реально попавшие в DRE request |

Пустой slice day-1 — **OK**. Нет audit trio — **reject**.

#### 3.1.2 Meaning events minimum (L1)

Один проход S0–S5 → **все шесть:** `day_opened`, `day_sky_fact_viewed`, `tarot_selected`, `tarot_revealed`, `number_selected`, `first_synthesis_viewed`. Детали: [PR1_PREFLIGHT.md](./status/PR1_PREFLIGHT.md) §6.1.

**Главный вопрос PR1:** появился ли **наблюдаемый путь** Experience → signals → PIM read → DRE? Шаблон секций PR: [PR1_GATE_SECTIONS.md](./status/PR1_GATE_SECTIONS.md).

### 3.2 Код сегодня (2026-06-23)

| Канон | Код | PIM gate |
|-------|-----|----------|
| S0 greeting + sky fact | Ritual hero first | **gap** |
| S5 до check-in | check-in **before** synthesis | **reject** |
| 5 cards | не зафиксировано | **gap** |
| `daily_focus_v1` | sphere triad / four-area | **gap** |
| Phase FSM S0–S10 | `entry`…`checkin`…`day_ready` | **gap** |
| Learning events S0–S5 | partial `meaning_events` | **verify** |
| DRE read slice S5 | direct narrative LLM | **architectural debt** |

**PR1 DoD:** FSM S0–S5; §3.1.2 event chain; §3.1.1 audit trio; S5 Daily Focus only. **PIM Diff:** шесть `meaning_events` + audit rows (atoms optional).

**PR1 PIM test (без UI):** после сценария — (1) шесть `event_type` в `meaning_events`; (2) `pim_slice_requested` + `pim_slice_used` + `dre_fields_used` в generation trace.

**PR1 не делает:** Intent Record, goal loop, atom promotion jobs.

---

## 4. PR2 — Goal Loop (верификация по фазам)

**Scope:** S6–S10 (goal path) + A1–A6 ([TODAY_SCREEN_V1_CANON.md](./TODAY_SCREEN_V1_CANON.md) §9, [INTENT_MODEL_V1.md](./INTENT_MODEL_V1.md) §5).

### 4.1 Intent Record — поля при создании (S6)

| Поле | Источник UI | Canon |
|------|-------------|-------|
| `intent_record_id` | server | ✓ |
| `day_id` | calendar day | ✓ |
| `session_id` | today session | ✓ |
| `goal_text` | user type | ✓ |
| `goal_source` | `user_typed` \| `suggested_pick` | ✓ |
| `goal_option_id` | if pick from 3–5 | ○ |
| `set_at` | S6 timestamp | ✓ |
| `daily_focus_id` | from S5 DRE | ✓ |
| `life_sphere_hint` | classifier internal | ○ |
| tarot/number refs | ritual context link | ✓ |

### 4.2 По фазам — пять вопросов

| Phase | Q1 Signals | Q2 PIM | Q3 Atoms (candidates) | Q4 Evidence | Q5 Consumer |
|-------|------------|--------|----------------------|-------------|-------------|
| **S6** set goal | `day_goal_set` | **create Intent Record** | — yet | `goal_text`, `set_at` on record | LRE: optional goal theme classify |
| **S7** API load | `day_goal_submitted` | link record + day context | — | request audit | **DRE** input build |
| **S8** guidance | `goal_guidance_viewed` | **read** slice: IM + atoms (C17) | — | `guidance_shown_at` on record | **DRE** → copy; gated LLM polish |
| **S9** active | `post_goal_action`, `primary_action_done/skip` | **update** `post_set_actions` on IM | — | behavioral events → chain | **DRE** (goal in slice) |
| **S10** evening | `day_goal_outcome` | **outcome** on IM record | see §4.3 | outcome on record; **not** direct trait | **LRE** evening; ILR job async |

### 4.3 Atom types после S10 (async job — не блокер UI, блокер **merge**)

| Claim (candidate) | `knowledge_type` | `decision_relevance` default | `evidence_chain` from |
|-------------------|------------------|------------------------------|------------------------|
| `intent.overestimate_frequency` | `hypothesis` | `very_high` | N intent outcomes |
| `intent.off_priority_theme` | `hypothesis` | `high` | goals vs focus mismatch |
| `intent.action_within_2h_rate` | `pattern` | `very_high` | S9 post_set_actions |
| HDM trait inference | `hypothesis` | `high` | ILR from goal themes — **не fact** |

**A5:** S10 outcome = **signal** on Intent Record only; atom promotion **async** with C14 chain.

**A6:** job emits atom candidates; не synchronous trait write.

### 4.4 Relevance defaults (PR2 registry rows — минимум)

| Claim | Tier | `dre_eligible` | `surface_affinity` |
|-------|------|----------------|-------------------|
| `intent.overestimate_*` | `very_high` | true | `goal_guidance`, `daily_focus` |
| `intent.action_within_2h_*` | `very_high` | true | `goal_guidance` |
| `trait.conflict_avoidance` | `high` | true | `goal_guidance` |
| ritual flavor atoms | `very_low` | false | — |

### 4.5 Contradiction triggers (PR2 — возможные, не обязательны day-1)

| Trigger | Example | C15 path |
|---------|---------|----------|
| Outcome vs declared ambition | goal «запущу бизнес» + `no` × 5 | ILR → Contradiction → `intent.overestimate` |
| New outcome vs old `high` atom | prior avoid-conflict + achieved social goal | Contradiction → C16 `change_nature` TBD |
| User «не про меня» on guidance | dismiss | `user_corrected` |

PR2 **не обязан** resolve contradictions — **обязан** не писать conflicting atom без event.

### 4.6 DRE slice при S7–S8 (минимальный)

```
P0: active Intent Record (today)
P1: very_high/high atoms, surface_affinity ∋ goal_guidance
P2: HDM subgraph (confidence ≥ gate)
P3: daily_focus_id + ritual context
P4: negative/suppress (cap 2)
Exclude: historical, archive_only, very_low
```

### 4.8 Ownership (PR2 — обязательно)

| Сущность | Владелец | **Не** владелец | S10 / Evening |
|----------|----------|-----------------|---------------|
| **Intent Record** | **Intent Model** (PIM subgraph) | Today · Ritual FSM · Goals Screen | — |
| **Goal outcome** (`outcome`, `outcome_at`) | **Intent Model** (поля record) | Evening Reflection · `day_goal_outcomes` table | Evening = **signal source** only |
| **post_set_actions** | Intent Model (on record) | S9 UI state | events → update record |
| **Atoms** | UKM / PIM | day analytics · narrative cache | ILR job from IM + events |

**Reject PR2:** `CREATE TABLE day_goals` без `intent_records` в PIM store; outcome column только в evening_submissions; A1 формально «есть id», но delete Today = delete goals.

**API shape:** `POST /today/day-goal` — **Experience endpoint**, пишет в **Intent Model service/store**, не в today-local DB как SoT.

---

### 4.9 Код сегодня

| A1–A6 | Код | Status |
|-------|-----|--------|
| A1 Intent Record | нет `day-goal` API | **missing** |
| A2 PIM read | narrative direct | **debt** |
| A3 S9 goal context | — | **missing** |
| A4 S10 outcome → IM | — | **missing** |
| A5 no direct fact | — | **verify** |
| A6 atom job | — | **missing** |

### 4.10 PR2 Success Criterion *(post-deploy · AR-012)*

| Gate | Когда | Вопрос |
|------|-------|--------|
| **Merge** | PR merge | Write-path доказан |
| **Success** | 30d prod | **Daily usefulness** — retention/IR = indicators |

**Gate:** «Становится ли жизнь **ощутимо лучше** от завершённого дня?» · «Что получил **вечером** без TodayFlow?»

**Reject:** sticky ritual (D7 ok · evening weak) · IR-first KPI.

Full spec: [PIM_PRODUCT_NORTH_STAR.md](./PIM_PRODUCT_NORTH_STAR.md) §0.2 · [PR2_PREFLIGHT.md](./status/PR2_PREFLIGHT.md) §15.

---

## 5. Порядок работ — **Gate 1: PR1 в коде** (сейчас)

**Freeze:** новый канон (C18+, новые docs) — **пауза**. Достаточно архитектуры на месяцы; нужно **столкновение с кодом**.

**Главный результат сессии:** измеримый критерий успеха — [PIM_PRODUCT_NORTH_STAR.md](./PIM_PRODUCT_NORTH_STAR.md). Актив продукта = **PIM**. Не C10–C17 по отдельности.

### Gate 1 — открыть PR1: PIM-мышление, не Today-мышление

**Шаг 0 (обязателен до кода):** [status/PR1_PREFLIGHT.md](./status/PR1_PREFLIGHT.md) — короткий canon vs code diff (entry, spoilers, LLM, mood, events, keep/delete/debt). PR1 режется узко по §9 того документа.

**Цель Gate 1 — не доказать, что архитектура правильная.**  
**Цель — найти первое место, где канон ломается при столкновении с кодом.** Такие места дают самые ценные открытия.

Если PR1 **требует обходить** Ownership · Intent Model · Evidence · Learning Δ — проблема не в коде, а в каноне или в Today-центричной реализации.

| Секция PR | Контур |
|-----------|--------|
| Experience smoke | UI S0–S5 |
| Architecture | C10–C17, ownership §1.1 |
| Learning | PIM test без UI |
| `## PIM Ownership` | каждое новое поле |
| `## Today disappearance` | §1.2 |
| `## PIM Diff` | §1.4 |
| `## Learning Δ` | §1.5 — минимум L1 (signals) |

**Цель:** увидеть, **где канон ломается о код** — и зафиксировать в diff/tracker, не C18.

### После Gate 1

1. **PR2** — Goal Loop + A1–A6 + Learning Δ > 0 за полный день.  
2. **Prod deploy** — доказать **ежедневную привычку** (D7/D10); IR = byproduct · AR-012.  
3. Gaps → правки **только если блокируют retention или write-path**.  
4. **Не** новый канон / слой, если не проходит: «удержание в ближайшие недели?»

**Freeze до первых prod IR:** Discovery Engine · IPL · KIP review · новые C18+ docs.

**Tracker:** [PRODUCT_EXECUTION_TRACKER.md](./PRODUCT_EXECUTION_TRACKER.md) · Step A: [status/TODAY_CANON_VS_CODE_DIFF.md](./status/TODAY_CANON_VS_CODE_DIFF.md) · **PR1 pre-flight:** [status/PR1_PREFLIGHT.md](./status/PR1_PREFLIGHT.md).

---

## 6. Changelog

| Дата | Изменение |
|------|-----------|
| 2026-06-23 | v1.7 — §4.10 revised: retention primary, IR byproduct; AR-012 |
| 2026-06-23 | v1.6 — §4.10 PR2 Success Criterion (post-deploy, data metrics, AR-011); merge ≠ success |
| 2026-06-23 | v1.5 — Platform Layer Gate (C18+); gate question; C18 freeze as architecture protection |
| 2026-06-23 | v1.0 ACCEPTED — 5 PR questions; PR1/PR2 verification; C18 freeze; anti-patterns |
| 2026-06-23 | v1.1 — data ownership matrix; «Today исчез» test; PR2 Intent Record / outcome owners |
| 2026-06-23 | v1.2 — Experience vs PIM test; mandatory PIM Diff; «guidance → PIM unchanged»; daily cycle richness criterion |
| 2026-06-23 | v1.3 — три контура acceptance; **Learning Delta Test**; «чему научилась система?» |
| 2026-06-23 | v1.4 — PIM ROI §1.6; link [PIM_PRODUCT_NORTH_STAR.md](./PIM_PRODUCT_NORTH_STAR.md) |
| 2026-06-23 | §5 — **Gate 1: PR1 в коде**; freeze нового канона; критерий успеха = PIM ↑ |
| 2026-06-23 | §5 — **шаг 0:** [PR1_PREFLIGHT.md](./status/PR1_PREFLIGHT.md) до кода; узкий scope S0–S5 |
| 2026-06-23 | §3 — S5 boundary, PIM audit trio, `first_synthesis_viewed`; [PR1_GATE_SECTIONS.md](./status/PR1_GATE_SECTIONS.md) |
