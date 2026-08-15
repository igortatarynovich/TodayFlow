# SCREEN_FLOW_V1

**Статус:** ACTIVE  
**Версия:** 1.0 (2026-07-30)  
**Контракт:** Discrete product steps via transform — **viewport lock** + **swipe** + **keyboard** + **a11y**

Канон для полноэкранного (one-act-at-a-time) продуктового потока шагов — **Today ScreenFlow** handoff composition (**Welcome → Priority → Promise → Make yours → Поток дня → [Число → Карта] → Цвет → Фокус → Практика → Recap → Close**; content jobs: [TODAY_SCREEN_SCENARIO_V3](../today/TODAY_SCREEN_SCENARIO_V3.md)) и будущих product flows.

**Визуальный родитель:** [TODAYFLOW_FOUNDATION_UI.md](../TODAYFLOW_FOUNDATION_UI.md) — surface/motion/radius/gap.

**Landing EXCLUDED:** Landing — marketing + CTA, не дискретные продуктовые шаги.

---

## 0. Purpose

**One active viewport at a time**, controlled by **transform** (не scroll). Каждый шаг — **full-height product surface** с собственным title, data status, и возможностью прямого доступа + навигации.

**Not:** 
- Document scroll (scrollIntoView / window.scrollTo)
- Anchor nav (`#hash`)
- Карусель медиа-контента (галереи, stories)

**Is:**
- Дискретные product steps (сегодня: Today Acts)
- Swipeable · keyboard accessible · transform-based
- Loading skeleton · failed/degraded state · empty state
- Entry index routing (`?sf=1&step=N`)

---

## 1. Hard rules

### 1.1 One activeIndex

У ScreenFlow ровно **один `activeIndex`** — видимый полный viewport.

- Prev / Next — только ±1 (не скачки через два шага)
- Scroll — **запрещён** на уровне flow; внутри одного step разрешён (Today ActShell overflow)

### 1.2 Transform-only transitions

**Никаких:**
- `element.scrollIntoView()`
- `window.scrollTo()`
- CSS `scroll-behavior: smooth`
- CSS `scroll-snap-type`

**Только:**
- `transform: translateX(...)` или `translateY(...)`
- `transition: transform 320ms ease-out`

**Причина:** Viewport lock + universal control (keyboard, swipe, direct programmatic). Scroll-based flows мешают edge gestures (iOS back swipe, pull-to-refresh) и разбивают a11y focus.

### 1.3 Viewport lock

ScreenFlow высотой **100dvh** (или другой полный viewport), без прокрутки вне одного шага.

### 1.4 Swipe + Next/Prev + Keyboard

Обязательные навигации:
- **Swipe (touch):** `touchstart` → `touchmove` → `touchend` с условием distance > threshold
- **Next/Prev UI (optional):** кнопки или nav bar
- **Keyboard:** `ArrowLeft` / `ArrowRight` (или `ArrowUp` / `ArrowDown` для `axis="y"`)

### 1.5 Chrome — swipe is primary, visible nav is a fallback

Per §1.4, nav bar/buttons are **optional** — swipe + keyboard are the mandatory contract. Chrome should read that way:

- **Today product:** no labeled act strip (`TodayActNav`) and no «Назад»/«Далее» text controls. Progress chrome = `ScreenFlow` dots · swipe · keyboard. Step titles stay in `aria-live` / `srOnly` on dots — not a visible name row. Primitive keeps `showStepControls` for fixtures only (default `false`).
- **No raw step numbers as the primary visual.** Ordinals `0–5` stay out of chrome (same as pre-2026-08-03 §1.5).
- **Flat act surface:** every ScreenFlow act uses Glance Block grammar (`TodayScreenBlock` / glass stack). No ActShell motif plate on the product path (`ProductJourneyScene chrome={false}`); Plot hero is a Block, not a dark wash plate.
- **Swipe remains untouched.** `ScreenFlow.tsx` touch handling, `SWIPE_THRESHOLD_PX`, and `reason: "swipe"` are not affected.
- **Legacy:** `TodayActNav` component may remain in tree for fixtures; product path does not render it.

### 1.6 A11y

При смене шага:
1. **Focus heading** первого текстового заголовка в новом step (`<h2>` или `aria-labelledby`)
2. **`aria-live="polite"` announcement:** "Step N of M — Step Title"
3. **Inert на inactive шагах** (только активный доступен для tab/screen reader)

### 1.7 Step status

Каждый шаг может быть:
- **pending:** загружается → skeleton UI, prev/next разрешены
- **ready:** данные готовы, рендерится полный контент
- **empty:** данные пришли, но пустые → заглушка «Нет данных для этого шага»
- **failed:** запрос упал → «Нет соединения.» — **не изобретать** fake content
- **degraded:** частичный fallback → «Не удалось загрузить.» + то, что есть

**Не изобретать:** Fake calm rows, фальшивая витрина, «нет сигнала» ≠ «Нет соединения.» — см. [AGENTS.md](../AGENTS.md) "Value gate placement".

### 1.8 Re-entry always 0 unless explicit deep-link

По умолчанию ScreenFlow открывается на **step 0**. Если URL имеет `?sf=1&step=N` (или другой роут-признак), можно открыть прямо на `N`.

Повторный возврат на `/today` без query → снова step 0, не сохранённый last index.

### 1.9 onIndexChange analytics

При каждом изменении activeIndex → analytics event:

```ts
{
  event_type: "screen_flow_step_reached",
  payload: {
    flow_id: "today-wave2", // или другой flow ID
    step_index: 2,
    step_label: "Symbols",
    via: "swipe" | "nav_button" | "keyboard" | "deep_link" | "programmatic"
  }
}
```

Meaning events: см. [TODAY_PERSONALIZATION_CORE.md](../TODAY_PERSONALIZATION_CORE.md) §Events.

---

## 2. Axis (locked)

**Default (locked for Today):** `axis="x"` (`TODAY_SCREEN_FLOW_AXIS`).

| Axis | Fits Today? | Why |
|------|-------------|-----|
| **x** | **Yes — locked** | Steps are `scrollable` (in-step vertical pan). `touch-action: pan-y` keeps content scroll. Transform pager on horizontal. |
| **y** | No for Today | Conflicts with in-step overflow scroll **and** mobile pull-to-refresh. Primitive still accepts `axis="y"` for non-scrollable pilots / fixtures. |

**iOS edge-back (risk X):** mitigated by `SCREEN_FLOW_EDGE_DEADZONE_PX` (24) — touches starting in the left band do not change step. Nav buttons / dots / keyboard remain primary alternatives.

**Evidence (2026-07-30):**
- Playwright harness `e2e/screen-flow-harness.spec.ts` — axis x **and** y: transform pager, no document overflow, @390×844; swipe + left-edge deadzone on x.
- Product choice for Today: **x** (scrollable steps). Physical Safari/Chrome residual smoke welcome; not a gate to keep provisional.

**Constants:** `TODAY_SCREEN_FLOW_AXIS`, `SCREEN_FLOW_EDGE_DEADZONE_PX` in `ScreenFlow.tsx`.

---

## 3. Loading matrix

| Step status | Skeleton | Navigation | Empty slot | Fail message |
|-------------|----------|------------|------------|--------------|
| **pending** | ✓ | ✓ (prev/next) | — | — |
| **ready** | — | ✓ | content | — |
| **empty** | — | ✓ | «Нет данных для этого шага» | — |
| **failed** | — | ✓ | — | «Нет соединения.» |
| **degraded** | — | ✓ | partial + «Не удалось загрузить.» | — |

**Главное:** никогда не **инвентить** calm rows / fake sphere dictionary / офлайн-выдумку. Честно: «Нет соединения.» / «Не удалось загрузить.»

---

## 4. Today mapping

Content jobs SoT: [TODAY_SCREEN_SCENARIO_V3.md](../today/TODAY_SCREEN_SCENARIO_V3.md) **v3.1 houses**.  
**Presentation SoT (LOCKED 2026-08-10):** **six blocks** — День → Ритуалы → Инструкция → Цвет → Задания → Петля.

| Index | Block | Notes |
|-------|-------|--------|
| 0 | День | тренд-амбассадор: вайб · why · энергия · expect/trap/do·don't · (опц. timeline) |
| 1 | Ритуалы | число + карта (omit if no symbols) |
| 2 | Инструкция | персональный prioritize/avoid |
| 3 | Цвет | color guide |
| 4 | Задания | 1–2 выдачи + ежедневные; не catalog shop |
| 5 | Петля | обещание → close |

Without symbols: indices shift (5 steps). Re-entry: ordinary visit → **0**; deep-link `sf=1&step=N`.

**v3.3 12-step handoff — deprecated** (see SCENARIO_V3.4).

### 4.1 Capability matrix (who may see which house)

Canon meaning: [TODAY_CONTENT_PIPELINE_V1](../today/TODAY_CONTENT_PIPELINE_V1.md) I0 · [DAY_SCENARIO_V1 I7](../DAY_SCENARIO_V1.md).  
Code: `frontend/src/lib/todayScreenFlowCapability.ts`.

ScreenFlow **hides** houses. It does **not** invent Personal Day.

| Depth | Evidence | Houses on | Honest omit |
|-------|----------|-----------|-------------|
| **guest** | shared sky only | Global Day (day + orientation) · ritual card/universal number | Personal Day, natal timeline, why_personal, personalized instruction |
| **general** | account, thin/no natal | same as guest + account ritual | why_personal, deep natal |
| **light** | DOB, no time/place | + Personal Day (light) | natal house/angle overlay |
| **deep** | DOB + time + place | + natal timeline / why_personal | — |

Guest must never see empty personal slots pretending to be “your day”.

**Contract:** [TODAY_WAVE2_CONTRACT_V1.md](../today/TODAY_WAVE2_CONTRACT_V1.md) — `day_facts_v1` + `day_story` → Today Contract Assembler.

**Композиция:** `TodayProductScreenFlow.tsx` — ScreenFlow dots + swipe.

---

## 5. Architecture impact

### SoT before

Не было канона ScreenFlow — Today Acts отрисовывались как document scroll (Wave 1 ActShell + `ProductJourneyScene`).

### SoT after

**ScreenFlow V1** — viewport lock + transform-only + swipe + keyboard + a11y + step status + analytics.

### Public contract changed?

**Да** — новый meaning event type: `screen_flow_step_reached`.

### Migration required?

**Нет** (пока) — Today Wave 2 пилот. Если ScreenFlow заменяет старый Today scroll, то — **да**, с fallback для старых версий iOS/Android.

### Canon updated?

**Да** — этот документ + [docs/foundation/_INDEX.md](../foundation/_INDEX.md) + [docs/README.md](../README.md).

### Backward compatible?

**Да** — сервер не меняется, только FE UI pattern. Старая `/today` page остаётся до полного rollout.

### Glance Screen 0 compression (2026-07-31)

- **SoT before:** Glance = title + thesis + fixed 4 VerdictStrip cards + nearest + teasers (four equal cards competed with thesis).
- **SoT after:** thesis hero · `domain_verdicts` compressed (majority collapse / unanimous line / outlier cards) · promoted nearest · teasers. Data remains Wave2 fixed-4 ([TODAY_WAVE2_CONTRACT_V1 §3.4](../today/TODAY_WAVE2_CONTRACT_V1.md)).
- **Public contract changed?** no — presentation only.
- **Migration required?** no.
- **Canon updated?** yes — this §4 row + Wave2 §3.4 + tracker.
- **Backward compatible?** yes.

---

## 6. Implementation reference

**Primitive:** `frontend/src/design-system/primitives/ScreenFlow/`

- `ScreenFlow.tsx` — компонент + `ScreenFlowStep` + `resolveScreenFlowEntryIndex`
- `ScreenFlow.module.css` — transform track + swipe capture
- `index.ts` — exports

**Tests:**
- Unit: `frontend/src/design-system/primitives/__tests__/ScreenFlow.test.tsx`
- Visual: `frontend/public/visual-fixtures/screen-flow.html`
- E2E: `frontend/e2e/screen-flow-harness.spec.ts`

**Today integration:**
- `TodayProductScreenFlow.tsx` — обёртка вокруг ScreenFlow для Today Acts
- `TodayGlanceAct.tsx` — Glance step (0)
- `todayGlanceNearest.ts` — logic `pickNearestGlanceItem` для Glance teasers

---

## 7. Changelog

### 2026-08-15 — Capability matrix (§4.1)

- **Added §4.1** — guest / general / light / deep: Global Day always; Personal Day omitted without natal evidence.
- **Code:** `todayScreenFlowCapability.ts`

### 2026-08-03 — Chrome: drop visible step numbers (§1.5)

- **Added §1.5** — nav bar is optional per §1.4; `TodayActNav` visible ordinal (`{item.step}`) replaced with non-numeric indicator, swipe stays the primary path.
- **Day accent (same day):** `TodayActNav` + ScreenFlow dots/controls consume `--day-*` for tint (FOUNDATION_UI §11.4); shape/labels/no-ordinals unchanged.
- **No mechanics change** — `ScreenFlow.tsx` swipe/keyboard untouched; this is `TodayActNav` chrome only.

### 2026-08-03 — Chrome: unmount labeled ActNav strip

- **Product Today** no longer mounts `TodayActNav` name row. Progress = ScreenFlow dots + swipe/keyboard (§1.5).

### 2026-08-03 — Chrome: hide Назад/Далее by default

- `showStepControls` default `false`; Today product chrome = dots only. Prev/next remain optional on the primitive for fixtures.
- **Related:** [TODAYFLOW_FOUNDATION_UI.md §16](../TODAYFLOW_FOUNDATION_UI.md) — Today block/panel visual grammar (new).

### 2026-08-03 — Today mapping → SCENARIO v3.1

- **§4 rows** replaced to match locked content jobs (no seed leakage · color house = Move · Reading ≤2 no action).
- Meaning SoT = [TODAY_CONTENT_PIPELINE_V1](../today/TODAY_CONTENT_PIPELINE_V1.md); presentation map = [TODAY_SCREEN_SCENARIO_V3](../today/TODAY_SCREEN_SCENARIO_V3.md); this file = pager mechanics + index map.

### 2026-07-30 — v1.2 (axis lock)

- **Axis:** Today locks `x` (`TODAY_SCREEN_FLOW_AXIS`); edge deadzone 24px; `overscroll-behavior` on root / scrollable steps
- **y:** remains on primitive for fixtures; not used by Today product flow

### 2026-07-30 — v1.1 (Phase 2b)

- **Today mapping:** Personal interim bundle → discrete Reading / Move / Response steps
- **Nav:** ActNav chips for Чтение · Действие · Отклик when personalized ready
- **Impl:** `actFilter` on `TodayPersonalizedProductSection` inside direct `ScreenFlowStep` children

### 2026-08-10 — Today six blocks (v3.4)

- **Presentation SoT:** День → Ритуалы → Инструкция → Цвет → Задания → Петля
- **Deprecated:** v3.3 12-step handoff as product frame
- **Detail:** [TODAY_SCREEN_SCENARIO_V3.md](../today/TODAY_SCREEN_SCENARIO_V3.md)

### 2026-07-30 — v1.0 (init)

- **Added:** ScreenFlow V1 canon (transform-only · viewport lock · swipe · keyboard · a11y)
- **Mapping:** Today 6 steps (Glance → Plot → Symbols → Reading → Move → Response)
- **Primitive:** `ScreenFlow` + `ScreenFlowStep` + tests
- **Analytics:** `screen_flow_step_reached` meaning event
- **Axis:** provisional `x` → **superseded by v1.2 lock**
- **Loading matrix:** pending/ready/empty/failed/degraded — no fake content rule
- **Re-entry:** default index 0, deep-link via `?sf=1&step=N` optional
- **Landing excluded:** Landing — marketing, не product steps
- **Canon link:** [TODAYFLOW_FOUNDATION_UI.md](../TODAYFLOW_FOUNDATION_UI.md) — surface parent

---

**Связанные каноны:**

- [TODAYFLOW_FOUNDATION_UI.md](../TODAYFLOW_FOUNDATION_UI.md) — visual SoT (surfaces/motion/mood/day-phase)
- [TODAY_WAVE2_CONTRACT_V1.md](../today/TODAY_WAVE2_CONTRACT_V1.md) — contract lock (day_facts_v1 + day_story)
- [TODAY_WAVE2_EXECUTION_PLAN.md](../today/TODAY_WAVE2_EXECUTION_PLAN.md) — Today Wave 2 execution plan
- [AGENTS.md](../AGENTS.md) — Architecture impact + Value gate placement
