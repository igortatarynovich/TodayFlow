# SCREEN_FLOW_V1

**Статус:** ACTIVE  
**Версия:** 1.0 (2026-07-30)  
**Контракт:** Discrete product steps via transform — **viewport lock** + **swipe** + **keyboard** + **a11y**

Канон для полноэкранного (one-act-at-a-time) продуктового потока шагов — **Today ScreenFlow** (Glance → Plot → Symbols → Reading → Move → Response) и будущих product flows.

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

### 1.5 A11y

При смене шага:
1. **Focus heading** первого текстового заголовка в новом step (`<h2>` или `aria-labelledby`)
2. **`aria-live="polite"` announcement:** "Step N of M — Step Title"
3. **Inert на inactive шагах** (только активный доступен для tab/screen reader)

### 1.6 Step status

Каждый шаг может быть:
- **pending:** загружается → skeleton UI, prev/next разрешены
- **ready:** данные готовы, рендерится полный контент
- **empty:** данные пришли, но пустые → заглушка «Нет данных для этого шага»
- **failed:** запрос упал → «Нет соединения.» — **не изобретать** fake content
- **degraded:** частичный fallback → «Не удалось загрузить.» + то, что есть

**Не изобретать:** Fake calm rows, фальшивая витрина, «нет сигнала» ≠ «Нет соединения.» — см. [AGENTS.md](../AGENTS.md) "Value gate placement".

### 1.7 Re-entry always 0 unless explicit deep-link

По умолчанию ScreenFlow открывается на **step 0**. Если URL имеет `?sf=1&step=N` (или другой роут-признак), можно открыть прямо на `N`.

Повторный возврат на `/today` без query → снова step 0, не сохранённый last index.

### 1.8 onIndexChange analytics

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

## 2. Axis (provisional)

**Default (provisional):** `axis="x"` (horizontal swipe).

**Реальные устройства:** требуют pilot на iOS / Android — edge gestures (iOS edge-back на left swipe) и pull-to-refresh (y axis вниз) могут конфликтовать.

**Risk Y:** Pull-to-refresh на мобильном браузере.  
**Risk X:** iOS edge-back gesture (left swipe) может перехватывать ScreenFlow swipe.

**Decision:** После pilot на real device финализировать. Пока — x, но готовность к переключению.

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

| Index | Job | Notes (Phase 2a LIVE) |
|-------|-----|------------------------|
| 0 Glance | 1с тема | title + thesis · VerdictStrip · **one** nearest Glance mark · teaser icons |
| 1 Plot | разворот | narrative hero / pulse / dialogue |
| 2 Symbols | ритуал | optional when gates/impacts present · full GlanceTimeline |
| 3 Personal | чтение+действие+отклик | **interim:** Reading/Move/Response bundled in one scrollable step (TapWidget inside). Split to 3 discrete steps = Phase 2b. |

Target end-state (Phase 2b): Reading / Move / Response as separate ScreenFlow steps (indices 3–5).

Re-entry: ordinary visit → **0**; deep-link only with `sf=1&step=N`.

**Contract:** [TODAY_WAVE2_CONTRACT_V1.md](../today/TODAY_WAVE2_CONTRACT_V1.md) — `day_facts_v1` + `day_story` → Today Contract Assembler.

**Композиция:** `TodayProductScreenFlow.tsx` — обёртка вокруг `ScreenFlow` + `TodayActNav` controlled.

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

### 2026-07-30 — v1.0 (init)

- **Added:** ScreenFlow V1 canon (transform-only · viewport lock · swipe · keyboard · a11y)
- **Mapping:** Today 6 steps (Glance → Plot → Symbols → Reading → Move → Response)
- **Primitive:** `ScreenFlow` + `ScreenFlowStep` + tests
- **Analytics:** `screen_flow_step_reached` meaning event
- **Axis:** provisional `x` (pending real-device pilot)
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
