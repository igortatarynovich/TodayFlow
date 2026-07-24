# PR1 Pre-flight — Canon vs Code (Today spine)

**Дата:** 2026-06-23  
**Статус:** **Pre-flight complete** — достаточен для старта реализации; **код PR1 не начат**  
**Следующий шаг:** PR с секциями [PR1_GATE_SECTIONS.md](./PR1_GATE_SECTIONS.md) (не ещё один doc)  
**Канон:** [TODAY_SCREEN_V1_CANON.md](../TODAY_SCREEN_V1_CANON.md) §8–9 · [PIM_PR_GATE_V1.md](../pim/PIM_PR_GATE_V1.md) §3  
**Связанный diff:** [TODAY_CANON_VS_CODE_DIFF.md](../status/TODAY_CANON_VS_CODE_DIFF.md) (Step A, legacy `TodayRitualFlow`)

---

## 1. Где сейчас начинается Today

| Путь | Компонент | Когда |
|------|-----------|--------|
| **`/today` (default)** | `TodayExperienceSurface` | `todayExperienceMode = searchParams.get("full") !== "1"` → **true по умолчанию** (`page.tsx`) |
| `/today?full=1` | `TodayRitualFlow` | Legacy article-scroll ritual (~2400 строк) |
| `/today?core_loop=1` | `TodayCoreLoopViabilitySurface` | Эксперимент Theme→Action; не prod spine |
| **iOS** | `TodayRitualFlowView` | Паритет с **legacy** web (`full=1`), не с `TodayExperienceSurface` |

**Факт vs канон (S0):**

- FSM умеет фазу `entry` (`todayExperiencePhase.ts`: `!dayOpened → entry`).
- **`TodayExperienceSurface` инициализирует `dayOpened = true`** и при restore из `localStorage` всегда ставит `setDayOpened(true)` — **S0 greeting пропускается**.
- Нет экрана «Доброе утро» + day sky fact + CTA «Начать день».
- В legacy `TodayRitualFlow` — **Ritual Entry Hero** (~72dvh) + CTA, не S0 greeting-first (R0).

**Вывод:** prod web = director-layer (`TodayExperienceSurface`), но **не canon spine S0–S5**; iOS отстаёт от default web.

---

## 2. Где показываются карта и число

| Слой | Файл | Поведение |
|------|------|-----------|
| Фаза карты | `TodayExperienceSurface` → `RitualTarotPickExperience` | `phase === "tarot_reveal"`; `startAtGrid`, без skip |
| Фаза числа | `RitualNumberPickExperience` | `phase === "number_reveal"`; `tileMode="symbol"` |
| Legacy | `TodayRitualFlow` | `#today-ritual-card` / `#today-ritual-number` в длинном scroll |

**Количество карт:** `RitualTarotPickExperience` рендерит **`Array.from({ length: 6 })`** — канон **5** (C3 / PR1).

**Reveal gate:** `todayRevealGate.ts` — только `canShowTarotCardName`, `canShowDayNumber`, `canShowTodaySynthesis`. Частично соблюдается в experience mode (имя/теги карты после pick). **Не** покрывает S0, head_topic, semantic blocks, evening.

**Спойлеры до reveal (нарушения R7):**

| Место | Проблема |
|-------|----------|
| Header experience | `entryEyebrow` / дата видны до ритуала — ок для контекста, но не S0 fact line |
| `drawnTarot.leadRu` | Показывается после reveal карты **до** ack continue — допустимо post-pick |
| `onRitualSpineComplete` | Требует **`mood`** до вызова guide — синтез LLM **после** check-in, не после S4 |
| Legacy flow | Hero headline, sphere triad, day history — **до** или **вне** phase gate |

---

## 3. Порядок фаз (главный разрыв с каноном)

**Канон:** S0 → S1–S4 (карта + число) → **S5 synthesis** → (PR2+) goal…

**Код (`todayExperiencePhase.ts`):**

```
entry → tarot_reveal → number_reveal → checkin → day_ready → evening
```

**`isRitualSpineComplete`** (`todayRitualPersisted.ts`): карта + ack + число + **mood** + **checkInSubmitted** — synthesis и `postTodayNarrative` **заблокированы** до чек-ина.

| Канон | Код | Вердикт |
|-------|-----|---------|
| S5 после карта+число (R3) | S5 (`day_ready`) после check-in | **change** |
| Нет mood в PR1 (R18 / PR3) | `RITUAL_MOOD_GRID`, `head_topic`, essentials debt | **remove from PR1 spine** |
| Evening отдельно | `evening` phase в том же surface + textarea | **out of PR1** |

---

## 4. Прямые вызовы LLM (обход PIM → DRE → Gate)

| Вызов | Где | Когда (default experience) |
|-------|-----|------------------------------|
| `POST /today/narrative` `surface=guide` | `page.tsx` → `onRitualSpineComplete` | После spine complete **с mood** в `ritual_context` |
| `surface=day_layer` | `page.tsx` useEffect | Только **`!todayExperienceMode`** (legacy) |
| `surface=spheres` | `page.tsx` useEffect | Legacy only |
| `surface=evening` | `page.tsx` useEffect | Legacy only |

**Архитектурный долг:** клиент → `postTodayNarrative` напрямую; нет documented **PIM read path** в запросе S5 (см. §7).

**Backend:** `run_today_narrative_pipeline` в `api/today.py` — profile + fusion + ritual_context; **`today_intelligence_read_model_v1`** с `knowledge_context_slice` **существует**, но **не подключён** к `POST /today/narrative` в prod path.

---

## 5. Check-in / mood сейчас

| Элемент | Расположение |
|---------|----------------|
| Mood grid | `TodayExperienceSurface` `phase === "checkin"` — `RITUAL_MOOD_GRID` |
| Head topic | Те же chips после выбора mood |
| CTA | `RITUAL_COPY.ritualMoodDoneCta` → `checkInSubmitted` |
| Persist | `todayRitualPersisted.ts` — `mood`, `headTopic`, `checkInSubmitted` |
| Spine gate | `isRitualSpineComplete` требует mood |
| Narrative input | `TodayRitualNarrativePayload.mood` обязателен в `onRitualSpineComplete` |
| Synthesis model | `buildTodaySynthesisModel({ mood })` |
| Events | `mood_selected`, `head_topic_selected` через reducer / `executeRitualSpineAnalytics` (legacy); experience — частично через `trackMeaningEvent` |

**Вердикт для PR1:** check-in **не входит** в scope; блокирует spine и учит L3 mood — **убрать из morning spine**, оставить код за feature flag / debt label до PR3.

---

## 6. Meaning events — PR1 minimum (не формальный Δ)

**`meaning_events` Δ** для PR1 = **конкретный набор типов** после одного полного прохода S0–S5, не «любое +1».

### 6.1 Обязательная цепочка (L1)

| # | `event_type` | Когда | Payload minimum |
|---|--------------|-------|-----------------|
| 1 | `day_opened` | CTA «Начать день» (S0) | `day_key`, `source: today_experience` |
| 2 | `day_sky_fact_viewed` | S0 fact line visible | `sky_fact_id` или `fact_key` |
| 3 | `tarot_selected` | pick в сетке (до flip) | `card_id` (deck index) |
| 4 | `tarot_revealed` | face + name shown | `card_id`, `revealed: true` |
| 5 | `number_selected` | число раскрыто | `numerology_value`, `revealed: true` |
| 6 | `first_synthesis_viewed` | S5 Daily Focus **first paint** | `daily_focus_id` if known, `generation_id` |

**Reject PR1** если после сценария в audit отсутствует **любой** из шести типов.

**Не считать за PR1 spine:** `mood_selected`, `head_topic_selected`, `action_option_selected`, sphere/evening events.

### Уже в продукте (legacy / partial)

| `event_type` | Experience | Legacy | PR1 |
|--------------|------------|--------|-----|
| `tarot_selected` | ✓ | ✓ | keep; **добавить** отдельный `tarot_revealed` |
| `number_selected` | ✓ | ✓ | keep |
| `mood_selected` | ✓ | ✓ | **debt** — не PR1 |
| `head_topic_selected` | ✓ | ✓ | **debt** |
| sphere / action / evening_* | legacy | partial | **out of PR1** |

### Missing до PR1

| Event | Статус |
|-------|--------|
| `day_opened` | local `dayOpened` only |
| `day_sky_fact_viewed` | **missing** |
| `tarot_revealed` | смешано с `tarot_selected` |
| `first_synthesis_viewed` | **missing** (было обобщённо `day_synthesis_viewed` в gate) |

**Learning Δ PR1** = **L1** доказан этой цепочкой + **L6** (PIM read audit, §7). Atoms / intent — **0**, и это OK.

---

## 7. PIM read path — anti–fake integration

**Reject:** вызвали read model → пустой slice → галочка в PR без следа в Experience/DRE.

PR1 требует **наблюдаемый** read, даже при `atom_count: 0`.

### 7.1 Обязательные audit events (server)

| Event / log row | Когда | Payload minimum |
|-----------------|-------|-----------------|
| `pim_slice_requested` | до DRE S5 | `read_model_id`, `day_key`, `user_id`, `slice_policy_version` |
| `pim_slice_used` | после merge slice в DRE input | `read_model_id`, `atom_count`, `atom_ids[]` (может быть `[]`), `knowledge_fact_count` |
| `dre_fields_used` | в том же audit trace | **список полей**, реально попавших в DRE request (не «весь read model») |

Пример `dre_fields_used` (day-1 пустой slice OK):

```json
{
  "ritual_context": ["tarot_main_id", "numerology_value"],
  "knowledge_context_slice": [],
  "fusion_summary": ["energy_score"],
  "daily_focus_engine": ["domain_lens_input"]
}
```

**Merge criterion:** по generation log / orchestrator trace видно `requested → used → fields[]`. Пустой `atom_ids` — **не fail**.

### 7.2 Слой кода

| Слой | Статус |
|------|--------|
| `today_intelligence_read_model_v1` + `knowledge_context_slice` | **exists** (service + tests) |
| Wire в S5 DRE / `POST /today/narrative` | **missing** |
| Audit trio выше | **missing** |

**Не substitute:** прямой `core_profile` dump в LLM без slice audit.

---

## 8. S5 boundary — Daily Focus, не Goal Guidance (ломается чаще всего)

**Канон:** S5 = первый смысл дня. S6–S8 = Goal Loop. S9 = активный день.

### Вопрос после S5 (PR1)

| Допустимо | Запрещено в PR1 |
|-----------|-----------------|
| **«О чём этот день?»** — `daily_focus_id` + 1 заголовок + 1–2 строки | **«Как прожить его с моей целью?»** — любая goal-linked guidance |
| Компактный ritual context (карта/число) без prescription | Goal input, 3–5 suggestions, `day_goal_set` |
| Конец утреннего spine / neutral CTA | `PrimaryAction`, do/avoid как closure loop |
| Template + DRE focus selection | Половина S8 guidance «для красоты» |

**Reject PR1** если S5 рендерит goal UI, action chips как главный шаг, или copy в духе «с твоей целью сегодня…».

**PR2** подключает Intent Record и читает PIM slice **с** `intent_record_id`.

---

## 9. Keep / Delete / Debt

### Keep (переиспользовать в PR1)

| Asset | Почему |
|-------|--------|
| `TodayExperienceSurface` | Director shell — рефакторить FSM, не переписывать page |
| `todayExperiencePhase.ts` | Расширить фазы под S0–S5 naming |
| `RitualTarotPickExperience` / `RitualNumberPickExperience` | Pick UX; **6→5** cards |
| `todayRevealGate.ts` | Расширить на все pre-S5 surfaces |
| `todayRitualPersisted.ts` | Restore last phase (C4); убрать mood из spine slice |
| `todayRitualSpineMachine.ts` + reducer | Единый spine state; вычистить mood из complete |
| `useMeaningRuntime` / `/meaning/events` | Event transport |
| `today_intelligence_read_model_v1` | PIM read stub |
| `GET /today` + `today_day_v1` contract | Data layer под S5 |

### Delete or hide from default path (PR1)

| Item | Действие |
|------|----------|
| `checkin` phase в morning spine | Убрать из `todayExperiencePhase` order |
| `mood` / `head_topic` gating synthesis | Убрать из `isRitualSpineComplete` |
| `TodaySemanticCards` + long scroll в `day_ready` | Заменить на **Daily Focus** block (S5) |
| `PrimaryAction` / goal cues до PR2 | Скрыть или stub без goal loop |
| Evening block в `TodayExperienceSurface` | Не рендерить в PR1 |
| `postTodayNarrative` с обязательным `mood` | Изменить trigger: после S4, mood optional/absent |
| Default `dayOpened=true` | **false** на first visit → S0 |

### Debt (не PR1 — пометить, не чинить в том же PR)

| Item | PR |
|------|-----|
| `TodayRitualFlow` (`?full=1`) | maintain until removed |
| iOS `TodayRitualFlowView` parity | follow web after PR1 merge |
| `surface=spheres` / `day_layer` / `evening` split API | PR4+ |
| `TodayLifeSpheresSection`, four-area triad | PR2+ |
| Mood chips / inferred state | PR3 |
| `today_narrative_depth` UI on Today | settings-adjacent |
| `TodayCoreLoopViabilitySurface` | experiment |
| Atom promotion, contradiction | PR2+ |
| Intent Record / `POST /today/day-goal` | PR2 |

---

## 9. PR1 scope (узкий — только это)

**В scope:**

- **S0** greeting + day sky fact + `dayOpened`
- **S1–S4** ritual: **5** карт + число, **no spoilers** (R7 extended)
- **S5** first **Daily Focus only** (§8 — не goal guidance)
- **Restore** last completed phase (C4)
- **Meaning events** — цепочка §6.1 (6 типов)
- **PIM read path** — §7 audit trio + `dre_fields_used`

**Не трогать в PR1:**

- Goal Loop, Intent Record, Discovery
- Evening surface
- Atoms, contradiction, temporal, relevance jobs
- Sphere grid / triad / split narrative surfaces

---

## 10. Главный вопрос PR1 (gate)

> После прохождения S0–S5 появился ли **новый наблюдаемый путь** от Experience к PIM?

Не atom. Не intent. Не contradiction. **Доказуемый поток сигналов** + auditable read.

| Ответ | Вердикт |
|-------|---------|
| **Да** — §6.1 events + §7 audit в логах | PR1 выполнил задачу → PR2 |
| **Нет** — красивый ритуал, PIM не в цепочке | Reject |

Дополнительно: Today ≠ article-scroll; spine S0–S5 управляемый.

**Конкретные сигналы «готово»:**

1. First visit: **S0**, не карта.
2. Repeat visit: **restore** к last phase (S1–S5), без повторного pick.
3. Карта + число: **5** закрытых карт; имя/число/смысл не до reveal.
4. **S5** без mood; **только Daily Focus** (§8), не semantic wall / goal / primary action.
5. **Шесть** `meaning_events` из §6.1 — не абстрактный «Δ».
6. **`pim_slice_requested` + `pim_slice_used` + `dre_fields_used`** — даже при пустом slice.
7. PR description: [PR1_GATE_SECTIONS.md](./PR1_GATE_SECTIONS.md) — Ownership, Today disappearance, PIM Diff, Learning Δ.

---

## 11. Предлагаемый порядок файлов в PR1

1. `todayExperiencePhase.ts` — фазы S0–S5; drop checkin from morning
2. `TodayExperienceSurface.tsx` — S0 UI, S5 Daily Focus only, remove evening/mood/PrimaryAction
3. `todayRitualPersisted.ts` + spine machine — restore без mood gate
4. `RitualTarotPickExperience.tsx` — 5 cards; split `tarot_selected` / `tarot_revealed` events
5. `page.tsx` — narrative trigger после S4; no required mood
6. Backend — S5 DRE + `pim_slice_*` audit + `dre_fields_used`
7. Events — §6.1 chain + `first_synthesis_viewed`
8. Tests — FSM + reveal gate + PIM test (event list + audit trace)

**Не открывать в PR1:** `TodayRitualFlow.tsx` массовый рефактор, iOS full parity (отдельный follow-up PR).

**Следующий артефакт:** не документ — **PR** с заполненными секциями из [PR1_GATE_SECTIONS.md](./PR1_GATE_SECTIONS.md).

---

## Changelog

| Дата | Изменение |
|------|-----------|
| 2026-06-23 | Pre-flight diff зафиксирован; код PR1 не начат |
| 2026-06-23 | §6–§8: S5 boundary, PIM audit trio, meaning events chain; gate question §10 |
