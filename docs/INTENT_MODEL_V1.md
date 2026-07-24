# Intent Model v1 (IM)

**Статус:** `ACCEPTED` — канон **домена намерений** внутри PIM.  
**Версия:** 1.1 (2026-06-23)  
**Владелец:** Product + Intelligence

**Это не:** список целей в UI · Goals screen как центр · onboarding «зачем я здесь» (Profile Intent layer — отдельный артефакт сбора).

**Это:** **история намерений человека** — что он **декларирует**, **делает**, **достигает** и **не достигает** — и производные **Knowledge Atoms** с доказуемостью.

**Связь:**

| Документ | Роль |
|----------|------|
| [PERSONAL_INTELLIGENCE_MODEL_V1.md](pim/PERSONAL_INTELLIGENCE_MODEL_V1.md) | PIM — контейнер; IM — **подграф** |
| [HUMAN_DECISION_MODEL_V1.md](./HUMAN_DECISION_MODEL_V1.md) | HDM читает паттерны из IM (decision style, stress) |
| [USER_KNOWLEDGE_MODEL.md](pim/USER_KNOWLEDGE_MODEL.md) | Паттерны IM → Knowledge Atoms (`domain: intent`) |
| [TODAY_SCREEN_V1_CANON.md](./TODAY_SCREEN_V1_CANON.md) | Goal Loop S6–S10 — **главный поставщик** IM records |

**North star:**

> Через 200 целей можно узнать **больше**, чем через 200 generic вопросов.  
> Intent Model — вероятно **сильнейший сигнал** во всей системе.

---

## 0. Иерархия информативности сигналов

| Ранг | Сигнал | Информативность | Куда |
|------|--------|-----------------|------|
| P4 | «Как ты себя чувствуешь?» | почти бесполезно | не собирать напрямую (C7) |
| P3 | «Что оказалось сложнее?» | средняя | Discovery (targeted) |
| P2 | «Какую цель поставил сегодня?» | высокая | **Intent Record** |
| P1 | «Удалось ли достичь?» | очень высокая | **Intent outcome** |
| **P0** | «Что сделал **после** постановки цели?» | **максимальная** | behavioral + IM linkage |

**Правило:** приоритет PIL-обновления PIM: **P0 > P1 > P2 > P3 > P4**.

---

## 1. Структура Intent Model

```
Intent Model (per user)
 ├─ records[]              # append-only история намерений
 ├─ active_threads[]       # week/month goal threads (optional)
 ├─ derived_patterns[]     # Knowledge Atoms (domain: intent)
 └─ meta
      ├─ record_count
      ├─ first_record_at
      └─ last_outcome_at
```

### 1.1 Intent Record (единица истории)

Каждый цикл «постановка → день → исход» — **одна запись**, не строка в goals table.

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| `intent_record_id` | string | ✓ | stable id |
| `day_id` | string | ✓ | календарный день |
| `goal_text` | string | ✓ | как сформулировал пользователь |
| `goal_source` | enum | ✓ | `user_typed` \| `suggested_pick` \| `carry_forward` |
| `life_sphere_hint` | string | ○ | internal classifier (не UI grid) |
| `themes[]` | string[] | ○ | extracted themes |
| `set_at` | datetime | ✓ | момент S6 |
| `guidance_shown_at` | datetime | ○ | S8 |
| `post_set_actions` | object | ○ | **P0** — opens, completions, skips после цели |
| `outcome` | enum | ○ | `achieved` \| `partial` \| `no` \| `changed` \| `skipped` |
| `outcome_note` | string | ○ | вечерний текст |
| `outcome_at` | datetime | ○ | S10 |
| `daily_focus_id` | string | ○ | контекст дня |
| `linked_atom_ids` | string[] | ○ | atoms, обновлённые этим циклом |

### 1.2 Что извлекается из 100+ records (derived patterns → atoms)

| Паттерн | Пример claim | Зачем |
|---------|--------------|-------|
| Реальные приоритеты | `intent.priority_themes_ranked` | что **делает**, не что говорит |
| Declare vs do gap | `intent.declared_not_executed_rate` | декларирует, но не делает |
| Overestimate | `intent.overestimate_frequency` | систематически завышает |
| Underestimate | `intent.underestimate_frequency` | систематически занижает |
| Success correlates | `intent.success_when_focus_is_*` | что ведёт к успеху |
| Slip correlates | `intent.slip_when_*` | что ведёт к срыву |
| Post-goal behavior | `intent.action_within_2h_rate` | дисциплина после намерения |

Все derived patterns — **Knowledge Atoms** ([USER_KNOWLEDGE_MODEL.md](pim/USER_KNOWLEDGE_MODEL.md) §2), не поля без provenance.

---

## 2. Потоки (Today Goal Loop)

```
S6 goal set     → Intent Record created (goal_text, set_at)
S7 API          → day context + PIM write candidate
S8 guidance     → guidance_shown_at; reads HDM + IM patterns
S9 behavior     → post_set_actions (P0 signals)
S10 outcome     → outcome + outcome_note (**signal** on record)
                  → ILR: competing interpretations
                  → atom candidates with evidence_chain → intent_record ids
```

**Запрещено:** цель только в local state / только в day API response без Intent Record + PIM path (R10, R22, R23).

**Владелец:** Intent Model (PIM) — не Today, не Evening Reflection. Evening = signal; outcome = поле **Intent Record**. Тест: [PIM_PR_GATE_V1.md](pim/PIM_PR_GATE_V1.md) §1.2, §4.8.

---

## 3. Потребители IM

| Consumer | Читает | Не делает |
|----------|--------|-----------|
| **Day Reasoning** | active goal, slip risk from patterns | не выбирает discovery |
| **Learning Reasoning** | uncertainty on intent-derived hypotheses | не выбирает daily focus |
| **HDM** | decision style evidence from outcomes | не хранит raw goals |
| **Own Model (future)** | records + atoms as training rows | — |

---

## 4. Отличие от Profile «Intent»

| | Profile Intent (onboarding) | Intent Model (PIM) |
|---|----------------------------|-------------------|
| **Когда** | день 0–1 | каждый день, накопительно |
| **Что** | «зачем я здесь» — themes/route | что человек **реально** ставит и делает |
| **Форма** | user chips, anchor | append-only records + derived atoms |
| **Ценность** | стартовый prior | **основной learning signal** |

Profile Intent **seed**-ит priors; Intent Model **переопределяет** их evidence over time.

---

## 5. PR2 acceptance gate (engineering)

Goal Loop **reject**, если нет **всех** пунктов:

| ID | Критерий |
|----|----------|
| **A1** | `day_goal_set` → Intent Record created + `day_id` / `session_id` link |
| **A2** | `goal_guidance` → reads PIM slice (IM + atoms + HDM), not full profile |
| **A3** | S9 → goal context in DRE inputs (`goal_text`, `intent_record_id`) |
| **A4** | S10 → `outcome` + `outcome_at` on Intent Record; event `day_goal_outcome` |
| **A5** | outcome **не** записывается как fact о человеке (только поле цикла) |
| **A6** | derived patterns → atoms (`hypothesis` + confidence + **`evidence_chain`** + decay) |

**Guidance-only PR = reject.** См. [TODAY_SCREEN_V1_CANON.md](./TODAY_SCREEN_V1_CANON.md) §4.1, §9 PR2 (C13).

---

## 6. Changelog

| Дата | Изменение |
|------|-----------|
| 2026-06-23 | v1.0 ACCEPTED — IM as PIM domain; signal hierarchy; Intent Record schema; Goal Loop binding |
| 2026-06-23 | v1.1 — PR2 acceptance gate A1–A6 |
