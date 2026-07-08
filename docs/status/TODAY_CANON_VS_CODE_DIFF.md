# Today · Step A — Canon vs Code Diff

**Дата:** 2026-07-02  
**Статус:** **Step A complete** — diff + **Day Story v3** block map  
**Источники:** [TODAY_SCREEN_V1_CANON.md](../TODAY_SCREEN_V1_CANON.md) v4.0 §11 · [TODAYFLOW_PRODUCT_BUILD_MAP.md](../TODAYFLOW_PRODUCT_BUILD_MAP.md) · `TodayCompositionSurface.tsx`

**Prod route (2026-07-02):** `/today` default → **`TodayCompositionSurface`** (Day Story v3). Legacy: `?experience=1` → `TodayExperienceSurface` · `?full=1` → `TodayRitualFlow`.

**Web launch v1 (2026-07-01):** diff для launch path — [WEB_LAUNCH_EXECUTION_PLAN.md](./WEB_LAUNCH_EXECUTION_PLAN.md).

**Stack:** [PERSONAL_INTELLIGENCE_MODEL_V1.md](../PERSONAL_INTELLIGENCE_MODEL_V1.md) · Today canon **v4.0** §11 · Composition Today v1.

---

## Day Story v3 — блоки §11 vs код

| # | Блок (канон §11) | Код `TodayCompositionSurface` | Статус | Следующий шаг |
|---|------------------|----------------------------------|--------|---------------|
| 0 | ContinuityRecall D2+ | `today-zone-continuity` · `buildContinuityOpeningLine` | **partial** | Итог вчера (done/partial/not) в pill |
| 1 | Живое приветствие | `today-zone-greeting` · `todayDayGreeting.ts` | **done** | Copy polish по фазе |
| 2 | Пульс дня | `today-zone-pulse` · `story.pulse` | **done** | Dedup vs hero tagline (DS1) |
| 3 | Hero дня | `today-zone-hero` · `DailyTheme` | **done** | Date в greeting, не в hero — OK |
| 4 | День в одном взгляде | `today-zone-glance` supported/caution | **done** | Обязательность при пустых hints |
| 5 | Почему так | `today-zone-why-story` | **partial** | **Expandable** (сейчас always open) |
| 6 | **Ритуал: карта** | `today-zone-ritual-tarot` · overlay pick | **done** | Reveal in overlay; impact block on surface |
| 7 | **Ритуал: число** | `today-zone-ritual-number` | **done** | Variant B (3 tiles) — optional |
| 8 | Пульс пересборка | pulse phases in story model | **partial** | Dedup · goal suggestions after number |
| — | Персональные блоки gated | zones by `personalizedReady` | **done** | Tracking · bridges still gap |
| 8 | Поможет прожить | `today-zone-strengthen` | **partial** | `/practices/current` overlay + start/complete; meditation/asceticism CTA отдельно |
| 9 | Цель дня | `today-entity-daily-goal` | **partial** | 3 chips from contract+focus; `promise_text` → CUM; Intent API still gap |
| 10 | Трекеры | — | **gap** | `DailyTracking` slot 12 · mood/energy chips |
| 11 | Сделай день своим | `today-zone-actions` | **partial** | mood · habit actions · scroll targets |
| 12 | Что изменится | `today-zone-growth` | **done** | — |
| 13 | Мосты Explore | — | **gap** | Wire `todayCompatibilityHook` + Tarot + Profile |
| — | Вечер replace | `TodayDayContinuityEveningClose` | **partial** | Practice outcome · evening mood · greeting |
| — | После закрытия | `TodayDayContinuityClosed` | **partial** | «Сегодня добавлено» list |
| — | Screen states | `todayCompositionZones` · engagement | **partial** | Pulse refresh after tarot pick |

**iOS / Android:** паритет не начат для Day Story stack — [IOS_TODAYFLOW_STATUS.md](./IOS_TODAYFLOW_STATUS.md).

---

## Experience canon vs код (v1.0 ACCEPTED)

| Канон | Код сегодня | Решение |
|-------|-------------|---------|
| Goal Loop (C5/C13) | S6–S10: Intent Record + behavior + outcome + atoms | Нет `day-goal` path; goal local-only | **PR2 — PIM gate** |
| PIM center (C9): Experience→PIM→Reasoning→Gate→LLM | Много `Today → narrative LLM` direct paths | **architectural debt** |
| Inferred state L3 | Direct mood/energy scales | **reject** |
| Карта → Число → **Синтез → Чек-ин** (C2=B) | Карта → Число → **Чек-ин → Синтез** | **change** — FSM reorder |
| 5 закрытых карт (C3) | N не зафиксировано в каноне кода | **change** |
| Restore last phase (C4/R8) | Persistence есть; повтор pick не всегда предотвращён | **change** |
| R7 — no spoilers | Частично `todayRevealGate.ts` (только tarot/number/synthesis) | **extend** gate на все фазы |
| Режиссура: no scroll на S2, карта = hero | Scroll + длинный ritual flow | **change** |

---

## Главный вывод

Текущий web-Today — **ritual-first funnel**, не **Theme → Action → Progress spine**.

| Ожидание канона | Факт в коде |
|-----------------|-------------|
| Открытие = «какой день» | Открытие = **Ritual Entry Hero** (72dvh) + CTA «Открыть день» |
| Symbolic = preview-слой | **Tarot pick + number pick** — главный интерактив до контента |
| Action = виден после темы | Action в `TodayResultView` **после** tarot + number + mood check-in |
| Progress = обязательный блок | **Нет** dedicated Progress strip в prod UI |
| Evening = скрыт утром | Evening hook + `<details>` в том же scroll **сразу после ритуала** |
| Depth = CTA-блок | Copy есть в `todayRitualCopy.ts`, **не рендерится** в `TodayRitualFlow` |

Единственное место, где loop близок к канону — **`TodayCoreLoopViabilitySurface`** (query-flag, не default).

---

## Таблица блоков

| Блок | Канон (§2) | Product role | В коде | Статус | Решение |
|------|------------|--------------|--------|--------|---------|
| **2.1 Тема дня** | Заголовок + смысл; коротко: фокус · темп · риск · окно; «Почему так?» по tap | **Theme** — «что происходит»; hero утра; питает loop | **После** ritual spine: hero `ritualDayUnlocked` — headline/body, risk, best_move, practical brief (tempo/lucky). **До** ритуала — generic entry, не тема. Why — toggle в hero (`dayWhyOpen`), не отдельный блок ✓ | **partial** | **change** — тема должна быть первым кадром, не post-ritual |
| **2.2 Фокус / избегать** | «Где действовать» · «Где не спешить» | **Insight** — после symbolic; не прогноз | В unlocked hero: `displayDoLine` / `dayDontLine` (+ spine signals). Нет отдельной секции в `TodayResultView`. Доступно только после tarot+number+mood | **partial** | **change** — вынести из hero-dump; не gate за полным ритуалом |
| **2.3 Символ дня** | Карта + число (краткий слой); CTA → Tarot | **Symbolic Context** — ритуал-сигнал, не hub | `#today-ritual-card` + `#today-ritual-number` + depth tarot — **полный** pick UX до темы/action. Tarot link to product — частично (meaning popover, не `/tarot` CTA block) | **wrong-level** | **change** — preview-слой, не главный экран |
| **2.4 Действие дня** | Один главный шаг; expand: альтернативы / практика | **Action** — замыкание «что делать» | `TodayResultView`: «Главный шаг на сегодня» + option chips + 20 min + Flow link. Показ **только** если `ritualSpineComplete && ritualDayUnlocked`. Fallback через narrative ✓ | **partial** | **change** — visible без полного ritual gate; один primary |
| **2.5 Прогресс дня** | Сделано · streak · «день начался» (день 1) | **Progress** — обязательный loop closure | `page.tsx` считает `dailySteps`/`progressPercent` — **не передаёт в UI**. Нет progress strip. `essentialsProgress` — чеклист «база дня», не loop. `guideMeaningCompletions` chips — фрагмент. `core_loop=1` — static day-one copy only | **gap** | **change** — обязательный Progress projection |
| **2.6 Вечер** | Утром скрыто; вечером — закрыть день + рефлексия | **Reflection** — evening-only | `TodayResultView`: hook + `<details>` + `TodayEveningSection` **в том же потоке** после check-in. `eveningHourCompact` только укорачивает текст до 19:00, блок на странице | **wrong-level** | **change** — time-gate / отдельная evening surface |
| **2.7 Углубление** | CTA: Profile · Calendar · Tarot | **Depth routes** — не отдельный экран | `deeperRoutes*` в `todayRitualCopy.ts` — **0 usages** в `TodayRitualFlow`. Разрозненные Link: `/tracking/calendar` (Flow), habit wizard. `TodayGuideSection` (depth cards) — **не смонтирован** | **gap** | **change** — вернуть depth block или удалить dead copy |

---

## Cross-cutting (не отдельные строки §2)

| Наблюдение | Статус | Решение |
|------------|--------|---------|
| **Check-in** (mood + head_topic) | Есть `#today-ritual-checkin`; блокирует `TodayResultView` | **partial** — learning input OK, но не должен блокировать Theme/Action/Progress |
| **Essentials** («база дня», 4 чекбокса) | `TodayResultView` post-ritual | **partial** — Product Model = Action.support; не путать с Progress |
| **Сферы внимания** (×3) | `TodayResultView` «Куда смотреть» + отдельный `POST …/narrative surface=spheres` | **partial** — Insight есть, но после ritual + split API ≠ Today Package |
| **Calendar / fusion context** | `TodayDayHistoryStrip` в hero и spheres | **partial** — Calendar Context optional OK, но рано на day 1 |
| **Build day / goals / support** | goal wizard, weekly goals, support hooks в `TodayResultView` | **wrong-level** — Calendar entities на Today |
| **Narrative depth control** | `TodayNarrativeDepthControl` atop page | **dead** для §2 inventory (settings-adjacent) |
| **Split narrative API** | `guide` · `day_layer` · `spheres` · `evening` — 4 POST из `page.tsx` | **wrong-level** vs Product Model «один Today Package» |
| **TodayGuideSection** | Legacy tab UI, не импортируется в `page.tsx` | **dead** |

---

## Порядок экрана (факт)

```
Default /today
├─ TodayNarrativeDepthControl          [dead для §2]
├─ Ritual Entry Hero (72dvh)           [не канон-блок — gate]
├─ [user taps Open]
├─ Tarot pick → Number pick → Check-in
├─ Hero «Твой день» (theme+brief+focus)  [2.1–2.2 partial]
└─ TodayResultView
   ├─ Spheres                           [Insight — early]
   ├─ Main step                         [2.4 partial]
   ├─ Support / Build day               [Calendar — wrong-level]
   ├─ Essentials                        [Action.support]
   └─ Evening hook + form                 [2.6 wrong-level]

?core_loop=1
└─ TodayCoreLoopViabilitySurface       [Theme → Action → Progress — ближе к канону]
```

---

## Риски (подтверждены)

| Риск | Вердикт |
|------|---------|
| Ritual стал главным экраном вместо Theme → Action → Progress | **Да** (default path) |
| Symbolic / Calendar слишком рано | **Да** (tarot+number до темы; history/goals до Progress) |
| Action спрятан за ритуалом | **Да** |
| Morning / evening смешаны | **Да** |
| Why отдельным блоком | **Нет** — tap-level в hero ✓ |

---

## Следующий шаг

**PR gate:** [PIM_PR_GATE_V1.md](../PIM_PR_GATE_V1.md) — PR1 §3, PR2 §4. **Freeze C18** до прохождения стека в коде.

**Канон Today:** [TODAY_SCREEN_V1_CANON.md](../TODAY_SCREEN_V1_CANON.md) v3.0 `ACCEPTED`. P0.2 — PR1 → PR2 по PIM gate.

---

*Bump при изменении `/today` route или §2 inventory.*
