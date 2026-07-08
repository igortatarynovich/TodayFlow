# Today Screen v1 — сценарий экрана (канон)

**Статус:** `ACCEPTED` — источник истины для experience layer Today v1.  
**Версия:** 4.2 (2026-07-02) — **Day Story + Ritual Gates + continuous dialogue**  
**Владелец:** Product (sign-off) + Engineering (паритет web / iOS / Android)

**Это не:** Figma, wireframe, CSS.  
**Это:** пошаговый сценарий Today + ссылки на **продуктовую модель** ([HUMAN_DECISION_MODEL_V1.md](./HUMAN_DECISION_MODEL_V1.md)).

**Слои (стек TodayFlow):**

| Слой | Документ | Роль |
|------|----------|------|
| **Human Decision Model** | [HUMAN_DECISION_MODEL_V1.md](./HUMAN_DECISION_MODEL_V1.md) | **Срез PIM** — traits, confidence |
| **PIM (центр системы)** | [PERSONAL_INTELLIGENCE_MODEL_V1.md](./PERSONAL_INTELLIGENCE_MODEL_V1.md) | Atoms + Intent Model; Today = consumer |
| **Intent Model** | [INTENT_MODEL_V1.md](./INTENT_MODEL_V1.md) | Goal Loop → история намерений |
| **Experience spine** | этот doc §5–6 | Greeting → Ritual → Meaning |
| **Goal Loop** | §4 | Цель → **Intent Model + PIM** → DRE → Guidance |
| **Life Map → Daily Focus** | §1 | Один фокус дня, не сетка сфер |
| **State L1/L2/L3** | §2 | Explicit · Behavioral · Inferred |
| **Discovery Questions** | §3 | Targeted: **уменьшить uncertainty** по `hypothesis_id` |
| **Block registry** | §7 | UI-блоки |
| **Editorial language** | [TODAY_LANGUAGE_V1.md](./TODAY_LANGUAGE_V1.md) | Банальность / небанальность; правило кино; gate до показа |

**Experience North Star *(AR-012)*:** **ежедневная полезность** — не retention, не data. Вечерний вопрос: *«этот день был лучше благодаря TodayFlow»* · что получил **вечером**, чего не было бы без app? **Evening screen test (S0–S10):** каждый экран повышает ли этот ответ? Retention (D1/D7) — **индикатор** полезности, не North Star. PIM · IR · PR2 — infra.

**Вопрос экрана Today (не «прогноз по сферам»):**

> **Что сегодня для меня — и как мне прожить этот день лучше?**

За **15 секунд** пользователь получает: какой день · где сила · где риск · что сделать первым. Дальше — участие: карта · число · практика · цель · отметки · закрытие · продолжение завтра.

**Default path (v4.1):** **Day Story + Ritual Gates** — основа дня → открыть карту → открыть число → персональный день. `TodayCompositionSurface`.

**Legacy path:** S0–S10 phase FSM — `?experience=1` · PR2 Goal Loop gate · см. §5–6 ниже.

**North star:** [PIM_PRODUCT_NORTH_STAR.md](./PIM_PRODUCT_NORTH_STAR.md) — §0.2 **usefulness → retention → data** · §1 Platform (Learning Δ).

**Дневной цикл (experience spine):**

```
контекст дня → ритуал → смысл → намерение → поддержка → проверка вечером
```

**Связь:** [PERSONAL_INTELLIGENCE_MODEL_V1.md](./PERSONAL_INTELLIGENCE_MODEL_V1.md) (**центр системы**) · [HUMAN_DECISION_MODEL_V1.md](./HUMAN_DECISION_MODEL_V1.md) (срез PIM) · [USER_MODEL_TARGET_STATE.md](./USER_MODEL_TARGET_STATE.md) · [TODAY_PERSONALIZATION_CORE.md](./TODAY_PERSONALIZATION_CORE.md).

---

## A. Архитектурная граница (не экран — система)

**Центр:** **PIM** — не Today, не Tarot, не external API.

```
Signals → PIM (Knowledge Atoms + Intent Model) → DRE / LRE → (gated) LLM → Experience
```

| Запрещено | Обязательно |
|-----------|-------------|
| Today → OpenAI direct | Goal → **Intent Record + atoms** → DRE/LRE → AMLL Gate |
| Смешивать DRE и LRE в одном prompt | Today S5/S8 → **Day Reasoning**; discovery → **Learning Reasoning** |
| Trait без atom + provenance | Каждое знание = atom с `why we know` |

Долгосрочно: **Own Model** заменяет external LLM; PIM — главный актив. См. [PERSONAL_INTELLIGENCE_MODEL_V1.md](./PERSONAL_INTELLIGENCE_MODEL_V1.md) §5.3.

---

## 0. Фундаментальные UX-правила

| # | Правило | Следствие |
|---|---------|-----------|
| **R0** | **Greeting-first** — первый вход за день = S0, не карты | FSM gate |
| **R1** | Обязательный **выбор карты** (5 закрытых) | No name до flip |
| **R2** | Обязательный **выбор числа** | No number до reveal |
| **R3** | **Первый персональный смысл** — только после карта + число (S5) | No synthesis до S5 |
| **R3a** | **Факт дня ≠ смысл** — S0: астро-событие-факт, не совет | `day_sky_fact` |
| **R4** | Один stage на фазу | No long scroll spine |
| **R5** | Вечер **заменяет** часть дня, не append | Evening replace |
| **R6** | Данные ≠ показ | Reveal gates |
| **R7** | **No spoilers** | См. §0.1 |
| **R8** | Ритуал + goal loop **один раз за день**; restore last phase | Persistence |
| **R9** | **Участие в формировании** — видимая цепочка выбора | Phase order fixed |
| **R10** | **Цель — сигнал, не декор** — ввод цели **обязан** уйти в API и **изменить** подсказки после S8 | No local-only goal; no S9 без API response |
| **R11** | **До S5 нельзя просить цель** | Goal UI только после первого синтеза |
| **R12** | **После цели — обязателен API** перед S9 | S7 loading не skip |
| **R13** | **Всё после S8 учитывает цель** — вопрос дня, шаг, подсказки в S9 | Goal in context slice |
| **R14** | **Вечер: первый вопрос — результат по цели** | achieved / partial / no / changed |
| **R15** | **Сферы жизни — модель, не UI** — канонические Life Spheres для памяти, профиля, классификации; **запрещён** список «Работа / Отношения / Деньги / …» на Today | No sphere grid, no four-area triad, no DomainLens grid |
| **R16** | **Daily Focus — центр дня** — один главный фокус (Коммуникация, Решения, …); do/avoid — **производные фокуса**, не отдельный мини-гороскоп на сферу | UI = focus + 2–4 абзаца; weights сфер — internal |
| **R17** | **Выделить главное** — 1 focus + 1 риск + 1 шанс | Не equal-weight по сферам |
| **R18** | **Состояние выводится, а не спрашивается** — запрещены прямые шкалы настроения, тревоги, энергии, уверенности | No 😀😐😔; no «насколько тревожен» |
| **R19** | **Discovery Questions** — вопросы из **контекста** (цели, паттерны, фокус дня); помогают человеку **или** уточняют гипотезу модели | Не generic «как дела?» |
| **R20** | **Inferred ≠ fact** | `hypothesis` до confirm |
| **R21** | **Discovery = uncertainty reduction** — каждый вопрос привязан к `hypothesis_id` + `uncertainty_before`; не «красивый вопрос» | Scheduler в HDM |
| **R22** | **Goal → PIM** — цель дня **обязана** пополнять Intent Model + HDM (P0 source), не только дневной API | POST goal + Intent Record + atoms path |
| **R23** | **Goal Loop = PIM pipeline** — не считается реализованным, если только возвращает guidance | См. §4.1 — 6 обязательных шагов; PR2 gate |
| **R24** | **Signal ≠ Interpretation** — observation (Intent Record, event) ≠ atom claim без ILR + `evidence_chain` | C14; один failed goal ≠ trait |
| **R25** | **Contradiction explicit** — оспаривание atom → Contradiction Event + re-eval; не только `confidence -= Δ` | C15; retired atoms ∉ LLM slice |
| **R26** | **Temporal classify** — retire/supersede с `change_nature` + validity window; не путать evolution и model error | C16 |
| **R27** | **Decision relevance** — PIM slice по `decision_relevance`, не по confidence alone | C17; very_low ∉ DRE |
| **R24** | **Язык Today** — RULE_001–003; TL-0 до TL-1 | [TODAY_LANGUAGE_V1.md](./TODAY_LANGUAGE_V1.md) · [TODAY_LANGUAGE_CALIBRATION_V0.md](./TODAY_LANGUAGE_CALIBRATION_V0.md) |

### §0.1 R7 — no spoilers

| Запрещено до… | Примеры |
|---------------|---------|
| S1 tarot pick | Карты, число, синтез, цель |
| Flip карты | Название, смысл карты |
| Reveal числа | Число, смысл числа |
| S5 first synthesis | «Твой день», semantic blocks, **цель дня** |
| S8 goal guidance | Поддержка с учётом цели до API |
| S9 day active | Action / question без goal context |
| S10 evening | Вечер утром |
| S0 fact line | Интерпретация вместо факта |

### Product decisions

| ID | Решение | Статус |
|----|---------|--------|
| **C1** | **Greeting-first ritual** | **ACCEPTED** |
| **C2** | ~~Утренний mood check-in~~ → **SUPERSEDED v2.2** — состояние выводится; вечер = Discovery Questions (C7) | **SUPERSEDED** |
| **C3** | 5 карт | **ACCEPTED** |
| **C4** | Первый вход → S0; повторный → restore last phase | **ACCEPTED** |
| **C5** | **Goal Loop** | **ACCEPTED** |
| **C6** | **Life Map + Daily Focus** | **ACCEPTED** |
| **C7** | Inferred state + Discovery Questions | **ACCEPTED** |
| **C8** | Human Decision Model (срез PIM) | **ACCEPTED** |
| **C9** | **PIM — центр системы**; Experience→PIM→Reasoning→LLM; запрет Today→LLM direct | **ACCEPTED** — [PERSONAL_INTELLIGENCE_MODEL_V1.md](./PERSONAL_INTELLIGENCE_MODEL_V1.md) |
| **C10** | **Knowledge Atom** — единица PIM; provenance + decay; не поля профиля | **ACCEPTED** — [USER_KNOWLEDGE_MODEL.md](./USER_KNOWLEDGE_MODEL.md) §2 |
| **C11** | **Intent Model** — домен намерений; Goal Loop = P0 signal | **ACCEPTED** — [INTENT_MODEL_V1.md](./INTENT_MODEL_V1.md) |
| **C12** | **DRE / LRE** — Day vs Learning Reasoning раздельно | **ACCEPTED** — [PERSONAL_INTELLIGENCE_MODEL_V1.md](./PERSONAL_INTELLIGENCE_MODEL_V1.md) §3 |
| **C13** | **PR2 Goal Loop gate** — Intent Record + behavior + outcome + atoms; guidance-only = **reject** | **ACCEPTED** — §4.1, §9 PR2 |
| **C14** | **Signal ≠ Interpretation** — atoms только с `evidence_chain`; ILR до inferred claims | **ACCEPTED** — [PERSONAL_INTELLIGENCE_MODEL_V1.md](./PERSONAL_INTELLIGENCE_MODEL_V1.md) §1.1, [USER_KNOWLEDGE_MODEL.md](./USER_KNOWLEDGE_MODEL.md) §2.2 |
| **C15** | **Contradiction & Re-evaluation** — смена мнения через Contradiction Event, не silent confidence | **ACCEPTED** — [CONTRADICTION_AND_REEVALUATION_V1.md](./CONTRADICTION_AND_REEVALUATION_V1.md) |
| **C16** | **Temporal Identity** — `change_nature`; когда правда; evolution vs error vs context | **ACCEPTED** — [TEMPORAL_IDENTITY_V1.md](./TEMPORAL_IDENTITY_V1.md) |
| **C17** | **Decision Relevance** — приоритет знаний для DRE/LRE/Gate; не все atoms равны | **ACCEPTED** — [DECISION_RELEVANCE_V1.md](./DECISION_RELEVANCE_V1.md) |

**Утренний порядок (канон v2.x):**

1. Приветствие по времени суток  
2. Короткое астро-событие дня  
3. Выбор карты  
4. Выбор числа  
5. **Первый синтез дня** (без цели)  
6. **Цель дня** (запись или выбор из 3–5)  
7. **Отправка цели в API**  
8. **Второй синтез:** как прожить день с учётом цели  
9. Активный день  
10. **Вечером:** результат по цели + **Discovery Questions** + итог дня  

---

## 1. Life Map и Daily Focus — два уровня

### Уровень 1 — Life Map (модель, не экран)

**Канонические сферы жизни** — для Profile, памяти, learning, классификации событий, весов в движке. Пользователь **не** проходит по ним как по оглавлению Today.

| ID | Сфера (RU) |
|----|------------|
| `work_realization` | Работа и реализация |
| `money_resources` | Деньги и ресурсы |
| `relationships` | Отношения |
| `family_close` | Семья и близкие |
| `health_energy` | Здоровье и энергия |
| `personal_growth` | Личностный рост |
| `home_routine` | Дом и быт |
| `rest_recovery` | Отдых и восстановление |

**Источники весов (internal):** профиль · цель дня · карта · число · астро-события · история · `DomainLens` / contract *(как input, не как layout)*.

**На экране Today:** сферы **не рендерятся** списком. Допустимо в «Почему так?» (tap, PR2+): «скорее про работу и решения» — **без** процентов и без четырёх колонок по умолчанию.

---

### Уровень 2 — Daily Focus (экран Today)

**Объект дня:** `daily_focus_v1` — **один** главный фокус, выбранный движком.

**Канонический словарь фокусов** *(расширяемый, не смешивать со сферами 1:1)*:

| Focus ID | Человеческое имя |
|----------|------------------|
| `communication` | Коммуникация |
| `decisions` | Решения |
| `energy` | Энергия |
| `boundaries` | Границы |
| `patience` | Терпение |
| `completion` | Завершение |
| `relationships` | Отношения *(фокус дня, не секция UI)* |
| `money` | Деньги |
| `learning` | Обучение |
| `change` | Перемены |

**Selection inputs:** профиль · `day_goal` · tarot · numerology · `day_sky_fact` · day history · contract slots.

**Internal evidence** *(не обязательно в UI):*

```json
{
  "daily_focus_id": "communication",
  "sphere_weights": { "work_realization": 0.6, "relationships": 0.25, "money_resources": 0.15 },
  "primary_risk_id": "overload",
  "primary_opportunity_id": "direct_talk"
}
```

---

### Как это выглядит на экране (не гороскоп)

**Правильно** — фокус = Коммуникация:

> Сегодня стоит обратить внимание на разговоры и договорённости.  
> Люди могут дать больше информации, чем документы и планы.  
> Если вопрос давно откладывался — лучше обсудить напрямую.

**Правильно** — фокус = перегрузка (риск):

> Сегодня не пытайся успеть всё.  
> Соблазн взяться сразу за несколько задач может оказаться сильнее обычного.  
> Лучше закончить одно важное дело, чем начать пять новых.

**Запрещено (R15):**

```
Работа        …
Отношения     …
Деньги        …
Энергия       …
```

**Структура narrative на S5 / S8** *(не slot labels)*:

| Блок | Содержание | Привязка |
|------|------------|----------|
| **Daily Focus** | 1 заголовок + 1–2 строки «о чём день» | `daily_focus_id` |
| **Стоит** | 1–2 bullets «что делать» | focus + opportunity |
| **Лучше избегать** | 1–2 bullets | focus + primary_risk |
| **Главный шаг** | один CTA (S9) | focus + goal (после S8) |

Старые «semantic blocks» (внимание / помощь / сомнение) — **не три колонки по сферам**, а **три роли текста вокруг одного фокуса** *(или схлопнуты в focus + do/avoid в v2.1)*.

**Связь с data contract:** `DomainLens` → input в `daily_focus_v1`; UI **не** рендерит grid.

---

## 2. State model — три уровня данных

**North star:** не «как ты себя чувствуешь?», а «мы замечаем закономерности, которые ты сам можешь не видеть».

### Level 1 — Explicit (что человек говорит)

| Сигнал | Когда | Куда |
|--------|-------|------|
| Цель дня | S6 | API + L1 memory |
| Выбор карты / числа / варианта цели | S1–S6 | Learning events |
| Ответ на Discovery Question | S9, S10 | `meaning_events` → confirmation |
| Вечерняя рефлексия (текст) | S10 | Explicit, не mood chip |
| Заметки пользователя | по запросу | Profile / journal |

### Level 2 — Behavioral (что делает)

| Сигнал | Примеры |
|--------|---------|
| Время открытия Today | утро / поздно |
| Возвраты в течение дня | S9 restore |
| Выполнил главный шаг | mark done |
| Ответил на вопрос дня | skip / answer |
| Пропуск вечера | no S10 |

**Правило:** L2 **не показывается** пользователю как «мы видим, что ты…» без consent; идёт в inference pipeline.

### Level 3 — Inferred (что система предполагает)

**Строится из сотен малых сигналов L1+L2.** Примеры гипотез *(не спрашивать напрямую)*:

- склонность к перегрузке;
- избегание конфликтов;
- импульсивные решения;
- потребность в контроле;
- ориентация на результат;
- откладывание сложных разговоров.

**Канон PIL:** L3 = `knowledge_type: hypothesis` до user confirmation ([KNOWLEDGE_ACQUISITION_AND_SIGNAL_POLICY.md](./KNOWLEDGE_ACQUISITION_AND_SIGNAL_POLICY.md)). High-priority rec **не** из raw hypothesis.

### Карта состояния (Current State)

**Не** собирается из emoji-чекина. **Выводится** из:

```
L1 explicit + L2 behavioral → inference → state hypotheses → (optional) confirm via Discovery answer
```

**Запрещено как primary input:** mood chips · шкалы 1–10 · «насколько тревожен/уверен/энергичен».

---

## 3. Discovery Questions — targeted uncertainty reduction

**Роль:** не анкета — **инструмент HDM** ([HUMAN_DECISION_MODEL_V1.md](./HUMAN_DECISION_MODEL_V1.md) §3).

Каждый вопрос имеет **цель в модели:**

```
hypothesis (confidence 38%) → discovery question → answer → HDM atom update
```

| Где | Сколько | Правило |
|-----|---------|---------|
| **S9** | 1 | `targets_hypothesis` с наименьшей confidence × impact |
| **S10** | 1–2 | После goal outcome; уточнение дня **и** trait |

**Selection inputs:** HDM atoms · goal history · focus · L2 behavior · **не** generic pool.

**Пример (conflict_avoidance @ 38%):**

> Что ты обычно делаешь, когда понимаешь, что разговор будет неприятным?

**Learning:** `discovery_question_answered` + `hypothesis_id` + `confidence_delta` → UKM update.

**API *(PR4+)*:** `GET /today/discovery-question` returns `question_id`, `targets_hypothesis`, `uncertainty_before`.

---

## 4. Goal Loop — PIM + DRE (не «guidance API»)

**Цель дня — источник обучения PIM**, не input для красивого ответа.

**Goal Loop не считается реализованным**, если он только возвращает guidance. Иначе снова станет UI-фичей, а не частью PIM.

### 4.1 Обязательный pipeline (R23)

| # | Шаг | Фаза | Обязанность |
|---|-----|------|-------------|
| 1 | **Intent Record** | S6 `day_goal_set` | Создать запись в Intent Model |
| 2 | **Context link** | S6–S7 | Связать с `day_id`, `session_id`, ritual context (`daily_focus_id`, tarot, number) |
| 3 | **Goal capture** | S6 | Записать `goal_text` **или** выбранный `goal_option_id` + source |
| 4 | **Post-goal behavior** | S9 | Зафиксировать `post_set_actions` (opens, step done/skip, timing) — **P0 signal** |
| 5 | **Outcome** | S10 | Получить `outcome` (`achieved` \| `partial` \| `no` \| `changed`) + optional note |
| 6 | **Knowledge Atoms** | S10+ (async) | Породить или обновить atoms; derived patterns — **не** прямой fact |

```
S6 day_goal_set
    → Intent Record (create)
    → link day / session / focus / ritual
S7 goal API
    → DRE reads PIM slice (atoms + IM + HDM)
S8 goal_guidance
    → product output (gated LLM polish)
S9 day active
    → post_set_actions → events → IM record update
S10 evening
    → outcome → Intent Record (close cycle)
    → atom candidates (hypothesis | pattern) — PIL job
```

**Запрещено:**

- цель только в `localStorage` / только в day API response;
- outcome как **fact** о человеке без atom + `knowledge_type` + provenance;
- guidance без PIM read;
- PR merge с «только POST + красивый текст».

### 4.2 Два контура (оба обязательны, R22)

```
                    ┌─→ Intent Model + HDM (atoms)
Goal (S6) ─────────┤
                    └─→ POST day-context API (S7) — DRE input
                              ↓
                    PIM slice (IM record + atoms + HDM)
                              ↓
                    S8 Guidance (DRE output — personal navigator copy)
```

| Шаг | Фаза | PIM / IM | API day |
|-----|------|----------|---------|
| Set goal | S6 | **Intent Record create** + `goal_signal` | — |
| Loading | S7 | — | request; server reads **PIM slice** |
| Guidance | S8 | DRE: «обычно ты…» если atom confidence ≥ threshold | риски, помощь, подход **сегодня** |
| Day active | S9 | `post_set_actions` on IM record | goal in context slice |
| Evening | S10 | **outcome** on IM record → atom update job | — |

**Пример S8 с HDM (conflict_avoidance @ 72%):**

> Обычно ты откладываешь подобные разговоры до последнего.  
> Сегодня условия для прямого разговора выглядят лучше обычного.

**Gate:** confidence < 0.5 → **без** «обычно ты»; только контекст дня.

**Outcome → atoms (R20, R23):**

| Запись | Допустимо |
|--------|-----------|
| `outcome: achieved` на Intent Record | ✓ событие цикла |
| «Пользователь дисциплинирован» как fact | ✗ |
| `intent.overestimate_frequency` после N циклов | ✓ atom `hypothesis` → `pattern` после confirm |

Derived patterns: `knowledge_type: hypothesis` + `confidence` + `source` + `decay_strategy` ([USER_KNOWLEDGE_MODEL.md](./USER_KNOWLEDGE_MODEL.md) §2).

### 4.3 Два синтеза

| | S5 `day_synthesis` | S8 `goal_guidance` |
|---|-------------------|-------------------|
| Вход | карта + число + contract | + **цель пользователя** + API analysis |
| Вопрос | «Какой сегодня день?» | «Как прожить день с этой целью?» |
| Цель в тексте | нет | да |

---

## 5. Глоссарий фаз

```
S0 → S1 → S2 → S3 → S4 → S5 → S6 → S7 → S8 → S9 → S10
greeting → tarot pick → tarot reveal → number pick → number reveal
  → day synthesis → goal set → goal API loading → goal guidance → day active → evening
```

| Phase ID | Что происходит |
|----------|----------------|
| `S0_greeting` | Доброе утро/день/вечер + астро-событие + «Начать день» |
| `S1_tarot_pick` | 5 закрытых карт |
| `S2_tarot_reveal` | Карта + смысл + «Продолжить» |
| `S3_number_pick` | Скрытые числа |
| `S4_number_reveal` | Число + смысл + «Узнать свой день» |
| `S5_day_synthesis` | **Первый** смысл дня (без цели) |
| `S6_goal_set` | Запись цели или выбор из 3–5 вариантов |
| `S7_goal_analysis_loading` | Цель отправляется в API |
| `S8_goal_guidance` | Поддержка: риски, помощь, лучший подход *(второй синтез)* |
| `S9_day_active` | День идёт; **Discovery Question** · шаг · прогресс |
| `S10_evening` | Goal outcome → **1–2 Discovery Questions** → итог |

**Restore (C4):** повторный вход → last completed phase (S1…S9), не S0, не повтор pick/goal submit.

**Spine complete для S9:** `goalGuidanceReady` + API ack (не только карта/число).

---

## 6. Сценарий по фазам

### S0 — Greeting

**Видит:** приветствие по времени + имя · **одна строка факта** (астро/календарь) · «Начать день».

**Не видит:** карты · число · синтез · **цель** · вечер.

**Режиссура:** вход в день; no scroll; no peek ритуала (R7).

**Действие:** «Начать день» → `dayOpened` → S1.

---

### S1 — Tarot pick

**Видит:** 5 закрытых карт.

**Не видит:** название · число · синтез · цель.

**Режиссура:** карта = hero; no scroll; 4 карты исчезают сразу после pick; focus на выбранной.

**Действие:** pick → S2.

---

### S2 — Tarot reveal

**Видит:** карта + смысл · «Продолжить».

**Не видит:** число до ack.

**Действие:** continue → S3.

---

### S3 — Number pick · S4 — Number reveal

Как v1.1: скрытые тайлы → reveal → CTA «Узнать свой день» → S5.

---

### S5 — Day synthesis *(первый смысл + Daily Focus)*

**Видит:**

- **Daily Focus** — заголовок + короткий narrative *(первое появление персонального смысла, R3)*;
- **Стоит** / **Лучше избегать** — по 1–2 строки, **вокруг фокуса**, не по сферам;
- карта + число compact.

**Не видит:** список Life Spheres · DomainLens grid · цель · goal guidance · вечер.

**Режиссура:** «вот **главное** сегодня» — навигатор, не гороскоп (R16, R17).

**Действие:** CTA «Поставить цель на день» → S6 (R11).

---

### S6 — Goal set

**Видит:**

- краткая сводка S5 *(compact)*;
- **ввод цели** (текст) **или** выбор из **3–5** предложенных *(привязаны к контексту дня, не generic)*;
- CTA «Продолжить».

**Не видит:** goal guidance до submit; S9 blocks.

**Режиссура:** намерение — герой; ощущение «теперь я задаю направление дню».

**Действие:** submit goal → persistence + **POST API** → S7.

---

### S7 — Goal analysis loading

**Видит:** loader «Учитываем твою цель…» · цель пользователя на экране (якорь).

**Не видит:** S9; пустой skip в active day.

**Режиссура:** ожидание **осмысленной** поддержки, не спиннер ради спиннера.

**Действие:** API success → S8. **Ошибка:** retry + degraded template *(с флагом, не silent)* — всё равно не S9 без явного path.

---

### S8 — Goal guidance *(второй синтез + focus refinement)*

**Видит:**

- **обновлённый Daily Focus** с учётом цели;
- как прожить день **с этой целью** (стоит / избегать);
- риски на пути · что поможет · лучший подход.

**Не видит:** сетку сфер · вечер.

**Режиссура:** цель + фокус сходятся в один narrative.

**Действие:** «В свой день» → S9.

---

### S9 — Day active

**Видит:** compact focus + цель · **один Discovery Question** (не mood) · главный шаг · прогресс.

**Вопрос дня:** выбран под человека (R19) — помогает **или** уточняет гипотезу.

**Не видит:** шкалы состояния · emoji mood · «как себя чувствуешь».

**Restore:** сюда или S1–S8, не S0.

---

### S10 — Evening

**Триггер:** evening hour + spine complete.

**Порядок (жёстко):**

1. **Goal outcome** (R14): удалось / частично / нет / цель изменилась;
2. **1–2 Discovery Questions** — рефлексия через события дня, **не** mood poll (R18, R19);
   - примеры: «Что сложнее ожиданий?» · «Что забрало энергию?» · «Что откладывал?»;
3. Итог / что забираю (R5).

**Не видит утром:** S10 (R7). **Запрещено:** 😀😐😔 chips · «насколько устал».

**Learning:** ответы → L1 explicit + signal для L3 inference; не писать в CUM как fact без confirmation.

---

## 7. Block registry

### 7.1 Greeting · Day Sky Fact · «Начать день»

| Блок | Фаза | Примечание |
|------|------|------------|
| Time greeting | S0 | R0 |
| Day Sky Fact | S0 | R3a — факт, не совет |
| CTA Начать день | S0 | `dayOpened` |

### 7.2 Ritual · 7.3 Daily Focus · 7.4 Goal Loop

*(См. v2.1 — tarot S1–S4, focus S5/S8, goal S6–S8.)*

### 7.5 Discovery Question (day)

| Вопрос | Ответ |
|--------|-------|
| Когда? | S9 |
| Откуда? | Selector ← profile, focus, goal, hypotheses, history |
| Интерактив? | Текст или выбор из 2–4 *(не emoji mood)* |
| Запрещено | Generic mood; прямые шкалы L3 (R18) |
| Learning | `discovery_question_answered` + `question_id` + optional `hypothesis_id` |

### 7.6 Evening: goal outcome + Discovery Questions

| Вопрос | Ответ |
|--------|-------|
| Когда? | S10 |
| Порядок | Goal outcome → 1–2 discovery → итог |
| Learning | `day_goal_outcome`, `evening_discovery_answered` |

### 7.7 Day active · Progress · Action

| Блок | Фаза |
|------|------|
| Главный шаг | S9 — focus + goal |
| Прогресс | S9 — L2 signals |

**Удалено с Today UI (legacy):** mood chips · `selectedMoodId` gate · head_topic как обязательный check-in · `TodayLifeSpheresSection` · DomainLens grid · emoji state picker.

---

## 8. Анти-паттерны (reject PR)

- Цель **до S5** (R11).
- Переход в S9 **без** API после цели (R10, R12).
- Подсказки в S9 **без** goal context (R13).
- Вечер **без** первого вопроса по цели (R14).
- Цель только в `localStorage` — не learning, не API.
- **Список сфер жизни** на Today: Работа / Отношения / Деньги / Энергия × N (R15) — «4 мини-гороскопа».
- **DomainLens grid** / slot labels Статус·Возможность·Риск по доменам (R15, R16).
- **Equal recommendations** по всем сферам вместо одного Daily Focus (R17).
- **Mood emoji** / «как ты себя чувствуешь» (R18).
- Прямые шкалы: тревога, энергия, уверенность (R18).
- Прямой вопрос про **inferred** trait (R20): «ты тревожный?».
- Generic discovery **без** `hypothesis_id` (R21).
- Guidance «обычно ты…» при HDM confidence < 0.5.
- Goal **без** Intent Record + PIM path (R22, R23).
- Goal Loop merge **только** с guidance response — **reject PR2**.
- Outcome записан как **fact** о человеке без atom (R20).
- Derived pattern без `hypothesis` + confidence + **`evidence_chain`** + decay (C14).
- Guidance **без** PIM slice read (C9).
- Запись L3 hypothesis в UI как **факт**.

- Проценты сфер без «Почему?».
- Goal loop, spoilers, sphere grid, tarot ≠ 5.

---

## 9. PR scope

### PR1 — spine + Daily Focus

S0–S5 · gates · restore · 5 cards · `daily_focus_v1`.

**PIM gate:** [PIM_PR_GATE_V1.md](./PIM_PR_GATE_V1.md) §3 — пять вопросов PR; events + DRE read path обязательны; atoms optional.

### PR2 — Goal Loop (PIM gate — C13)

**Не в scope PR2:** только красивый guidance text.

**Обязательный end-to-end:**

| # | Acceptance | Проверка |
|---|------------|----------|
| A1 | `day_goal_set` (S6) **создаёт Intent Record** | `intent_record_id` persisted; linked `day_id` |
| A2 | `goal_guidance` (S7–S8) **читает PIM slice** | IM record + atoms + HDM in request/audit log; не full profile |
| A3 | S9 **использует goal context** | discovery, step, copy — `goal_text` / `intent_record_id` in slice |
| A4 | S10 **пишет outcome** в Intent Model | `outcome` + `outcome_at` on record; event `day_goal_outcome` |
| A5 | Outcome **не** fact о человеке напрямую | нет trait write из одного вечера; только IM record field |
| A6 | Derived patterns → **Knowledge Atoms** | `hypothesis` + confidence + **`evidence_chain`** + decay; promotion async OK |

**API/events (минимум):**

- `POST /today/day-goal` → create Intent Record + return `intent_record_id` + DRE payload for S8
- `day_goal_set`, `day_goal_outcome`, `post_goal_action` — learning events (web + iOS parity)
- Atom job: outcome batch → `intent.*` domain candidates

**UI scope:** S6–S8 · S10 goal outcome first · убрать sphere triad.

**Reject:** PR2 с passing UI tests, но без A1–A6.

**Merge gate** (A1–A6, causal chain, PIM Diff) доказывает write-path **в коде**. **PR2 Success** *(post-deploy)* — **ежедневная полезность**; D7 и IR — индикаторы. AR-012 · [PR2_PREFLIGHT.md](./status/PR2_PREFLIGHT.md) §15.

**Полная верификация по стеку C10–C17:** [PIM_PR_GATE_V1.md](./PIM_PR_GATE_V1.md) §4.  
**Merge:** обязательны **PIM test** + **PIM Diff** (§1.3–1.4) — не только UI smoke.

### PR3 — Discovery + HDM pipeline

Discovery scheduler · hypothesis linking · goal→HDM signals · убрать mood chips.

### PR4 — Guidance with HDM slice

S8 «обычно ты…» · confidence gates · `hdm_slice` in API.

### PR5+

`GET discovery-question` · iOS parity · Profile reflection of HDM (optional).

---

## 11. Day Story Experience *(default `/today` · v4.1 ACCEPTED)*

**Today не выдаёт день полностью готовым.** Сначала — **основа дня**. Потом пользователь **сам открывает карту и число** — и день становится **личным**.

> *«Я не просто прочитал прогноз. Я открыл свой день.»*

**Карта и число — не карточки в блоке «влияния».** Это **ритуальные двери** Today.

**Код (web):** `TodayCompositionSurface` · `todayDayStoryModel.ts` · `todayRitualGate.ts`

### 11.1 Stack order *(foundation → ritual → personalized)*

| # | Блок | Entity / slot | Вопрос / роль |
|---|------|---------------|---------------|
| 0 | **Вчера → сегодня** *(D2+)* | `ContinuityRecall` | «Вчера главным было…» · итог · мост в сегодня |
| 1 | **Живое приветствие** | composition | Доброе утро/день/вечер + имя · живая строка по фазе |
| 2 | **Пульс дня** | `DailyEnergy` | Главный ответ экрана — одна сводка; всё ниже раскрывает её |
| 3 | **Hero дня** | `DailyTheme` | Дата · главная тема · подзаголовок *(≠ Pulse, ≠ Focus)* |
| 4 | **День в одном взгляде** | `DailyGuidance` + `DailyWarnings` | **Обязательно:** «поддержано» \| «требует внимания» — две колонки |
| 5 | **Почему сегодня именно так** | `WhyExpand` | **Expandable** · только язык предметной области (луна · число · карта · символы · история) |
| 6 | **Что формирует день** | `DailyTarot` · `DailyNumber` · moon · astro · `DailySymbols` | Карточки влияний · **карта и число интерактивны** |
| 7 | **Выбор карты / числа** | ritual overlay | Рубашкой вверх → pick → влияет на pulse · рекомендации · практику · аффирмацию · вечер |
| 8 | **Что поможет прожить день** | `PracticeRecommendation` + | Практика · медитация · аффирмация · аскеза — **разные CTA**, не одинаковые кнопки |
| 9 | **Цель дня** | `DailyGoal` | 2–3 предложенных + «Своя цель» · вечером возвращается в закрытие |
| 10 | **Трекеры дня** | `DailyTracking` | «Что сегодня отметить» — привычки · настроение · энергия · аскеза · цикл · вода/сон/движение |
| 11 | **Сделай день своим** | composition | Быстрые действия: карта · цель · практика · аскеза · настроение · привычка |
| 12 | **Что изменится** | composition | Рост / Maps promise — зачем отмечать и закрывать |
| 13 | **Мосты** | `TodayExploreBridges` | 1–3 перехода **как продолжение дня**, не реклама разделов |
| — | **Вечер** | `EveningClose` | Заменяет Hero+ *(R5)* · не append внизу без акцента |
| — | **После закрытия** | `EveningClose` D | Подтверждение · «Сегодня добавлено» · «До завтра» |

> **v4.1 (код):** строки 6–7 таблицы — **ritual gates**, не passive influence cards. Практика · цель · вечер — **gate** до `personalizedReady`. См. `todayRitualGate.ts`.

### 11.6 Ritual Gates *(главный механизм Today)*

1. **Основа дня** — тема · glance · astro · pulse preliminary · экран незавершён.  
2. **Выбор карты** — ритуал pick → «Как эта карта влияет на твой день» → пересборка pulse · практики · аффirmации · вечера.  
3. **Выбор числа** — после карты → «Как влияет на день» → уточнение tempo · цели · pulse.  
4. **Персональный день** — только после обоих ритуалов.

### 11.7 Day Dialogue *(give + learn · PIM loop · continuous)*

**Главный принцип:** Today — **не вечерний опросник**. Это **непрерывный ненавязчивый диалог** с PIM: каждый блок **берёт** slice из Profile и **отдаёт** персональный смысл; каждое действие **учит** систему. См. [PERSONAL_INTELLIGENCE_LAYER.md](./PERSONAL_INTELLIGENCE_LAYER.md) §3.1–§3.2.

```
Profile → Today блок → человек → signal → Profile точнее завтра
         (повтор на каждом touchpoint, не только вечером)
```

**Анти-паттерн (запрещено):** собрать learning только в `EveningClose` · modal «расскажи о себе» без отдачи · daily gate «ответь на всё, чтобы увидеть день».

| Touchpoint | Когда | Product output *(из Profile)* | Learning output *(→ PIM)* |
|------------|-------|-------------------------------|---------------------------|
| Открытие | утро / первый заход | greeting · pulse · foundation | — *(behavioral: dwell)* |
| Mood chip | нет / устарело | lens «день под твоё состояние» | `mood_selected` |
| Focus chip | нет / устарело | приоритет рекомендаций | `head_topic_selected` |
| Ритуал карты | всегда | трактовка под focus · atoms | `tarot_selected` |
| Ритуал числа | после карты | tempo · pulse refine | `number_selected` |
| Практика / аффirm | после ритуалов | одна практика под mood+focus | `practice_*` · completion |
| Обещание | после ритуалов | формулировка под день | `action_option_selected` → Intent |
| Подтверждение смысла | post-ritual · optional | «это про тебя?» на pulse/guide | `sphere_feedback` / confirm backlog |
| **Вечер** | один лёгкий шаг | recap · «удалось?» без вины | `day_focus_outcome` · *optional* highlight chip |

**R18 (v4.2):** mood/focus — **staleness TTL**, не daily gate. Вечер — **≤1 explicit ask** (исход обещания); highlight / note — optional chips, не обязательный второй экран.

**C18 — Day Dialogue ACCEPTED:** Today = диалог по всему дню, не статья и не вечерний допрос.

### 11.2 Вечерний режим *(один touchpoint, не interrogation)*

**Триггер:** время суток + spine / user CTA «Завершить день».

| Элемент | Содержание |
|---------|------------|
| Заголовок | «{Имя}, день подходит к завершению» |
| Recap | Тема дня · обещание *(1 строка)* |
| **Один вопрос** | «Удалось?» — Да / Частично / Пока нет *(без вины)* |
| Optional | chip «что запомнилось» — можно пропустить |
| CTA | «Завершить день» → «День закрыт» + Tomorrow Hook |

*Не здесь:* серия микро-вопросов (surprise · harder · energy) — только если MS6 budget не исчерпан и как отдельные дни, не пачкой.

### 11.3 Состояния экрана *(не одна статичная страница)*

| Состояние | Что меняется |
|-----------|--------------|
| Утро / день / вечер | Приветствие · pulse line · evening gate |
| После выбора карты | Influence badge · pulse refresh |
| После выбора цели | Goal закреплена · evening recall |
| После практики | Progress signal · evening question |
| После закрытия | Closed surface · no forward blocks |
| Следующий день | `ContinuityRecall` slot 0 |

### 11.4 UX-правила Day Story *(дополнение к §0)*

| # | Правило |
|---|---------|
| **DS1** | **Pulse ≠ Theme ≠ Focus** — три разных ответа; запрещено дублировать текст между блоками |
| **DS2** | **Glance обязателен** — «поддержано / требует внимания» всегда на Day mode |
| **DS3** | **Why — expand only** — не простыня; язык §Invisible Mechanism |
| **DS4** | **Tarot + Number — ritual gates** — не passive cards; pick → reveal → impact block → rebuild day |
| **DS4a** | **Personalized blocks gated** — практика · цель · аффirmация · аскеза · медитация · вечер — **только после** карта + число |
| **DS5** | **Actions — иерархия CTA** — практика ≠ медитация ≠ аффирмация ≠ аскеза |
| **DS6** | **Tracking = отметить** — сигнал для Maps; не блокирует Theme/Action *(не gate)* |
| **DS7** | **Bridges — contextual** — copy привязан к теме дня |
| **DS8** | **Evening replaces** — не `<details>` в том же scroll утром *(R5)* |
| **DS9** | **Continuous dialogue** — learning по touchpoints дня; вечер ≤1 explicit ask; give-before-ask ([PIL](./PERSONAL_INTELLIGENCE_LAYER.md) MS1) |

### 11.5 Запрещено *(Day Story reject)*

- Повторять один текст в разных блоках (DS1)
- Theme и Focus одинаковыми
- Карточки без роли / orphan blocks
- Системный язык (PIM · API · алгоритм) в UI
- Today как длинная статья (article-scroll)
- Все действия — одинаковые кнопки
- Карта и число **пассивные** или **карточки в grid влияний**
- Показывать практику / цель **до** открытия карты и числа
- Вечернее закрытие спрятано внизу без акцента
- **Вечерний допрос** — серия обязательных вопросов без give в течение дня

**North star (после ритуала):** *«Я не просто прочитал прогноз. Я открыл свой день.»*

---

## 10. Changelog

| Дата | Изменение |
|------|-----------|
| 2026-07-02 | **v4.2** — §11.7 continuous dialogue (не вечерний допрос); §11.2 evening = 1 touchpoint; DS9; PIL §3.1 link |
| 2026-07-02 | **v4.1** — §11.7 Day Dialogue (give+learn); mood/focus; promise; evening learning; R18 refine |
| 2026-07-02 | **v4.0** — §11 Day Story Experience (default `/today`); stack + evening; DS1–DS8 |
| 2026-06-23 | v1.0–v2.2 — spine, goal, focus, discovery, state |
| 2026-06-23 | **v2.7** — R24 + editorial layer [TODAY_LANGUAGE_V1.md](./TODAY_LANGUAGE_V1.md) (банальность / правило кино) |
| 2026-06-23 | **v3.0** — C17/R27 Decision Relevance; platform PIM ranking |
| 2026-06-23 | **v2.9** — C16/R26 Temporal Identity; change_nature |
| 2026-06-23 | **v2.8** — C15/R25 Contradiction & Re-evaluation |
| 2026-06-23 | **v2.7** — C14/R24 Signal vs Interpretation; evidence_chain on atoms |
| 2026-06-23 | **v2.6** — R23/C13 PR2 PIM gate; §4.1 six-step Goal Loop; A1–A6 acceptance |
| 2026-06-23 | v2.5 — C10–C12 Atom, Intent Model, DRE/LRE |
