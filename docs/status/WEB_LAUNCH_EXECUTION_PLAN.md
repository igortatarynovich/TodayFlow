> ⚠️ STALE — не отражает Journey/Day Sources. См. [audits/FULL_USER_PATH_CANON_V1.md](../audits/FULL_USER_PATH_CANON_V1.md). Полная ревизия — отдельная задача.

# Web Launch v1 — Execution Plan

**Статус:** **PROCESS FROZEN** — режиссура истории в **React**; Figma **не используем**.  
**Дата:** 2026-07-01  

> **Builders:** порядок работ — [TODAYFLOW_PRODUCT_BUILD_MAP.md](../TODAYFLOW_PRODUCT_BUILD_MAP.md).  
> Этот файл — gaps vs code · DoD · Decision Log. Не дублирует Build Map.

**Scope freeze:** [WEB_LAUNCH_PRODUCT_BLUEPRINT.md](./WEB_LAUNCH_PRODUCT_BLUEPRINT.md) · Epic 1–4 only.

---

## Порядок работ

**Единый источник:** [TODAYFLOW_PRODUCT_BUILD_MAP.md](../TODAYFLOW_PRODUCT_BUILD_MAP.md) — **Axis A** (journey) · **Axis B** (Entity Catalog · Design Tokens).

1. **6-step law** — question → entity → sources → projections → React
2. **Axis A** — User Journey (Phase 1)
3. **Axis B** — Entity Catalog + Design Tokens *(параллельно, не «фаза 2.5»)*
4. **Phase 2** — Screen Compositions (screen **uses** entities)
5. **Phase 3–4** — Layout · Data flow per entity
6. **Phase 5** — Build order → React
7. **Phase 6** — Polish

**Wave 1 ship checklist** — Build Map §Phase 5 + DoD ниже.

---

## С чего начать (30 секунд)

| Вопрос | Документ |
|--------|----------|
| **Что строить дальше?** | [TODAYFLOW_PRODUCT_BUILD_MAP.md](../TODAYFLOW_PRODUCT_BUILD_MAP.md) |
| Gaps vs code · DoD · Decision Log | **этот файл** |
| Content model (reference) | [TODAYFLOW_PRODUCT_MODEL.md](../archive/TODAYFLOW_PRODUCT_MODEL.md) §4 |
| Changelog | [PRODUCT_EXECUTION_TRACKER.md](../PRODUCT_EXECUTION_TRACKER.md) |

**Сейчас:** Build Map screen gate — **4 экрана ✅ · 4 ❌ · 2 🟡**. Достраиваем launch scope, walkthrough **после** последнего ✅.

### Launch scope remaining *(Build Map P1)*

| Priority | Screen / block | Status |
|----------|----------------|--------|
| **P0.2** | Value-first onboarding (2–5) | ✅ (Landing → welcome → birth → preview → save → First Today) |
| **P1** | Intent/Reality placement | ✅ **CLOSED 2026-07-24** — placement **C** inside First Today (`FirstTodayReactionGate`) |
| **P1** | Auth at save decision | ✅ **CLOSED 2026-07-24** — magic only; plaintext temp password removed from welcome email |
| **P2** | Compat return path · returning-user routing | 🟡 |

**Done in React (closed):** Landing · First Today · Evening · D2 · Compat hook · Maps seeds · Composition stack · **Profile min (Blueprint §6)**.

---

## Фактический путь в коде (as-is, web · updated 2026-07-24)

> Ранее (01.07) здесь ошибочно стоял auth-first. Value-first уже в коде; этот блок приведён к факту.

```
Landing (/) — signupHref → /onboarding/welcome?fresh=1
  → /onboarding/welcome → birth → preview → (refine) → save (email + magic)
  → claim → /today?first=1
      → FirstTodayReactionGate (intent + reality chips)
      → ritual spine → personalized Today
  → evening close → D2 ContinuityRecall
  → /profile — Profile-min
```

| Route | Component | Launch gate |
|-------|-----------|-------------|
| `/` | curiosity landing + vitrine | ✅ |
| `/demo/today` | redirect → `/onboarding/welcome?fresh=1` | ✅ |
| `/auth` | returning users (login) | ✅ |
| `/onboarding/welcome`…`/save` | value-first funnel | ✅ |
| `/onboarding/intent` · `/reality` | legacy → redirect First Today | ✅ placement C |
| `/today?first=1` | `TodayCompositionSurface` · firstToday + reaction gate | ✅ |
| `/today` | `TodayCompositionSurface` · default | ✅ |
| `/today?experience=1` | legacy ritual | ✅ preserved |
| `/compatibility/*` | public flows | ✅ + hook from Today |
| `/profile` | launch-min | ✅ |

**Redirect wiring:** ✅ `FIRST_TODAY_PATH` after onboarding when `!hasCompletedFirstToday()`.

---

## Launch vs full content

| Product | Launch v1 (DoD) | North star (v2+) |
|---------|-----------------|------------------|
| **Today** | Overview · Guidance · Symbols · **1× Practice** · Evening · D2 continuity | Full 7 zones · Tracking · cycle · Goals |
| **Profile** | Identity + «Мои дни» + collapsed sources | Full interactive hub §4.4 |
| **Compatibility** | Public L1 preserved + Personal hook | Full types library §4.5 |
| **Tarot** | Card in Symbols zone; existing routes | Question-first flow §4.6 |
| **Growth** | Teaser from Today zone 4; existing routes | Full Growth · **Maps** feed |
| **Maps** *(system property)* | «Мои дни» + evening (+1 seed) | Mood/Habit/Year Wrapped · share |

Content model **определяет** React; launch **не ждёт** полной библиотеки compatibility types.

---

## Режиссура истории (правило на каждый экран)

**Не спрашиваем:** «что здесь показать?»  
**Спрашиваем:**

| # | Вопрос |
|---|--------|
| 1 | **Зачем** пользователь сюда попал? |
| 2 | **Что понять за 5 секунд?** |
| 3 | **Какое одно действие** сделать? |
| 4 | **Почему** захочет перейти дальше? |
| 5 | **Смена состояния:** до → после |

**Story gate (единственный критерий готовности):**  
> *Этот экран **продолжает** историю или **прерывает** её?*  
> Прерывает — переделываем, неважно насколько «красиво».

**Per-screen workflow:** Story brief ✅ → React → Story gate ✅ → next screen.

---

## Целевой путь (launch v1)

```
Landing → Имя → DOB → первый результат → место/время → email → Today → Evening → D2+ → Compatibility · Tarot · Profile
```

**Проектируем путь человека, не UI.** Детали: **§User Journey Path** ниже.

**Story walkthrough:** тот же порядок в React после story gate на каждом шаге.

---

## User Journey Path

> **Canonical:** [TODAYFLOW_PRODUCT_BUILD_MAP.md](../TODAYFLOW_PRODUCT_BUILD_MAP.md) **Phase 1**.  
> Редактировать journey только там. Здесь — story gate table для walkthrough.

---

## Launch Story Script *(gate table — journey in Build Map P1)*

Gate checklist для walkthrough. Journey — Build Map Phase 1. Layout/c copy уточняются в React, но **до/после** не меняем без строки в Decision Log.

**Сквозная история (ощущение пользователя):**  
*«Я познакомился с TodayFlow. Он рассказал что-то обо мне. Показал первый день. Вечером мы закрыли день. На следующий он вспомнил вчера. Потом посмотрел совместимость. Понял, что формируется моя история — не один день.»*

| Screen | Зачем сюда | За 5 сек | Одно действие | Почему дальше | **До → После** | Gate |
|--------|------------|----------|---------------|---------------|----------------|------|
| **Landing** | Curiosity с рынка | «Интересно, что **сегодня для меня**» | Создать мой Today | Хочу **свой** результат | Не знает TF → **Хочет узнать свой Today** | ⬜ |
| **Имя** | Начать разговор | Меня спрашивают, не регистрируют | Ввести имя → Продолжить | Жду персональный ответ | Незнакомое приложение → **Личный разговор** | ⬜ |
| **Дата рождения** | Дать сигнал для расчёта | «Сейчас что-то покажут» | Выбрать дату → Показать результат | Награда близко | Анкета → **Жду reveal** | ⬜ |
| **Первый результат** | Первая награда | «Это про **меня**» | Уточнить / → Today | Хочу полный день | Любопытство → **Это про меня** | ⬜ |
| **Место/время** | Хочу точнее | «Точность выросла» | Место · время · skip | Точнее Today | Ок → **доверяю** | ⬜ |
| **Email** | Сохранить | Есть что терять | Email → continue | С любого устройства | Value → **сохранить** | ⬜ |
| **First Today** | Payoff дня 1 | Один главный ориентир сверху | Прочитать фокус; вечером — закрыть | Вечером проверю, как пройдёт | Ожидания → **Хочу вечером проверить день** | ⬜ |
| **Evening** | Причина открыть завтра | День можно **закрыть** | Итог фокуса → Сохранить | **Завтра увижу сегодняшнее** | День закончился → **Интересно, что завтра** | ⬜ |
| **Day 2** | Deliver moat | **Вчера не исчезло** | Открыть Today | Приложение **помнит** | Новый день → **Действительно помнит вчера** | ⬜ |
| **Compatibility** | Следующий слой исследования | Можно проверить **с кем-то** | Добавить человека → проверить | Хочу исследовать **отношения** | Исследую себя → **Исследую отношения** | ⬜ |
| **Profile** | Накопленная ценность | Здесь **растёт** история | Посмотреть «Мои дни» / людей | Больше чем один день | Пользуюсь Today → **Растёт что-то большее** | ⬜ |

---

## Launch Definition of Done

**Launch v1 считается готовым**, когда выполнены **все** пункты. Не «почти» — иначе бесконечное «осталось ещё вот это».

| # | Критерий | Status |
|---|----------|--------|
| 1 | Landing — story gate ✅ + в launch path | ⬜ |
| 2 | Value-first onboarding — story gate ✅ на каждом шаге | ⬜ |
| 3 | First Today — story gate ✅ + Blueprint hierarchy | ⬜ |
| 4 | Вечернее закрытие работает (D1) | ⬜ |
| 5 | D2 continuity показывается **первым** | ⬜ |
| 6 | Compatibility hook — story gate ✅ | ⬜ |
| 7 | Минимальный Profile — story gate ✅ | ⬜ |
| 8 | Нет ссылок на `/demo/today` | ⬜ |
| 9 | Нет путей, обходящих launch flow | ⬜ |
| 10 | Пройден **story walkthrough** — путь feels like one story | ⬜ |
| 11 | Проведён тест минимум на **10 пользователях** | ⬜ |

**Ship gate:** все 11 ✅ → можно объявлять launch done и открывать v2 planning.

---

## Launch Freeze *(с первого экрана в React)*

**ACTIVE** с начала реализации launch path до окончания полевого теста (DoD #11).

**Разрешено:**

- правки, чтобы экран **продолжал историю** (copy, порядок, один CTA)
- баги
- поломанные сценарии launch path

**Запрещено:**

- новые функции / экраны / разделы / сущности
- «полировка дизайна» без story-gate провала
- новые product-docs

Любая идея «а давайте ещё добавим…» → v2 backlog (одна строка в трекер) **без обсуждения** до метрик поля.

---

## Decision Log

Маленькая таблица: **что решили и почему**. Новые строки — сюда, не в новые `.md`.

| Date | Decision | Why | Status |
|------|----------|-----|--------|
| 2026-07-01 | **Invisible Mechanism CLOSED** | 4 user knowledges · dual spec · auto G1–G5 | **CLOSED** |
| 2026-07-01 | **Build Map v0.3** — Axis A/B · Entity Catalog | Screens **use** entities | **ACTIVE** |
| 2026-07-01 | **Build Map v0.2** — Component Catalog | Superseded → Entity Catalog | **REVOKED** |
| 2026-07-01 | **Product Build Map v0.1** — Phases 0–6; 7-Q template | Builder entry point | **ACTIVE** |
| 2026-07-01 | **User Journey Path** § — question-first, not UI | Merged → Build Map P1 | **ACTIVE** |
| 2026-07-01 | **Monetization** — story threshold not day 8; price TBD | §4.11 HYPOTHESIS only | **HYPOTHESIS** |
| 2026-07-01 | **Dual value** — instant + +1 to Map | Every action; copy shift | **ACTIVE** |
| 2026-07-01 | ~~Artifacts / Journey~~ | Renamed **Maps** | **REVOKED** |
| 2026-07-01 | **Today = life dashboard** (7 zones) | Aggregator; practices IN Today | **ACTIVE** |
| 2026-07-01 | **Growth cluster** — 5-й standalone candidate | JTBD «изменить жизнь»; entry from Today/Profile/Tarot | **ACTIVE** |
| 2026-07-01 | **Product count not fixed** — Core/Standalone/Services map | JTBD exercise before final nav | **ACTIVE** |
| 2026-07-01 | ~~4 products only~~ | Superseded by §4.1 map + Growth | **REVOKED** |
| 2026-07-01 | **Standalone + Personal** projections (§5.4) | Ecosystem | **ACTIVE** |
| 2026-07-01 | **Story gate** — 4 вопроса + до/после | Эмоциональная последовательность | **ACTIVE** |
| 2026-07-01 | ~~Figma before code~~ | Superseded by story-first React | **REVOKED** |
| 2026-07-01 | **Launch Scope Freeze** — Epic 1–4 only | Дороже не запуститься | **ACTIVE** |
| 2026-07-01 | **Value-first onboarding**, email/account **после** первой награды | Curiosity → reward → save; не auth-first | **ACTIVE** |
| 2026-07-01 | **Убрать `/demo/today`** из launch path | Demo даёт fake payoff до curiosity | **ACTIVE** |
| 2026-07-01 | **Continuity = moat** — D2 line **above** ritual | Иначе неотличимо от гороскопа | **ACTIVE** |
| 2026-07-01 | **Evening close обязателен D1** | Seeds return; без него нет D2 hook | **ACTIVE** |
| 2026-07-01 | **Profile launch-min** — identity + «Мои дни», не natal wall | Profile = accumulated value, не first payoff | **ACTIVE** |
| 2026-07-01 | **Field test 10×7d**, measure **behavior** not opinions | Единственный источник truth для v2 | **ACTIVE** |
| 2026-07-01 | **Day continuity localStorage v0** OK for launch | Server persist → v2 | **ACTIVE** |
| 2026-07-01 | Intent/Reality chips placement | Defer to **story gate** | **CLOSED 2026-07-24** — placement **C** in First Today |
| 2026-07-01 | Auth at save | magic vs password | **CLOSED 2026-07-24** — magic only; no plaintext password in email |
| 2026-07-01 | **claimGuestProfile → First Today**, not Profile; no early `markFirstTodayCompleted` | Profile gate bypassed first Today after magic/save | **CLOSED** |
| 2026-07-01 | **`/meaning/events` batch dedup** (BE + FE outbox) | Duplicate idempotency_key in one POST → 500 on Today | **CLOSED** |
| 2026-07-01 | **Personal Model** naming (vs Profile UI) | Team review post-launch | **DEFERRED** |

---

## Фактический путь · Gap summary

**Superseded:** актуальная таблица экранов и routes — **§С чего начать** и [Build Map P1](../TODAYFLOW_PRODUCT_BUILD_MAP.md#axis-a--phase-1--user-journey-screen-gate--2026-07-01). Не дублировать здесь.

---

## Phases & gates

| Phase | Gate | Status |
|-------|------|--------|
| **0** Docs + Story Script | Process frozen | ✅ |
| **0.5** **Content model** §4 (4 products) | Today launch layers agreed | ⬜ **NEXT** |
| **1** React screen-by-screen | Story gate per screen | ⬜ |
| **2** Story walkthrough | DoD #10 | ⬜ |
| **3** Field test | DoD #11 | ⬜ |
| **4** v2 | Metrics | ⬜ |

**PR rule:** one screen/story = one PR after story brief; merge after story gate ✅.

---

## Epic 1 — Первый опыт

### E1-S1 · Landing

**Blueprint:** §1 Landing  
**Code:** `frontend/src/app/page.tsx`

| # | Task | Status |
|---|------|--------|
| 0 | Story brief + gate per §Launch Story — **Landing** row | ⬜ |
| 1 | React: curiosity hero + vitrine + CTA «Создать мой Today» | ⬜ |
| 2 | Remove `/demo/today` CTA; secondary = «Войти» | ⬜ |
| 3 | Remove feature grid / SaaS «Как начать» blocks | ⬜ |
| 4 | Static UI preview cards (6) — story, not polish | ⬜ |
| 5 | Delete or 410 `/demo/today` + `GuestTodaySurface` | ⬜ |
| 6 | Story gate review | ⬜ |

**Reuse:** `orbit-page` / orbit components; auth redirect for logged-in users (`resolvePostAuthTarget`).

---

### E1-S2 · Value-first onboarding

**Blueprint:** §2 Первый запуск  
**Code today:** auth-first chain `/auth` → `/onboarding/core` → intent → reality

| # | Task | Status |
|---|------|--------|
| 0 | Story brief per §Launch Story — Имя → Email rows | ⬜ |
| 1 | **Decision (story gate):** magic link vs password at save | ✅ magic only (2026-07-24) |
| 2 | Guest flow routes — **no new entities** | ✅ |
| 3 | First result **before** account | ✅ |
| 4 | Email/save **after** first reward | ✅ |
| 5 | Intent/Reality: story gate picks placement | ✅ **C** inside First Today |
| 6 | Wire post-save → `FIRST_TODAY_PATH` | ✅ |
| 7 | `/auth` only for returning users | ✅ |
| 8 | Story gate each step | 🟡 partial |

**Reuse:** `useCoreSetupFlow` · `ProfileSetupSection` (birth calc) · `onboardingContext` · `fetchCoreProfileCached` · backend core profile API.

**Not in launch:** full Profile-as-setup first screen.

---

### E1-S3 · First Today

**Blueprint:** §3 First Today  
**Code:** `FirstTodaySurface.tsx` · `firstTodayPackage.ts` · `today/page.tsx` (`?first=1`)

| # | Task | Status |
|---|------|--------|
| 0 | Story brief — **First Today** row | ⬜ |
| 1 | React: главный ориентир доминирует; game blocks ниже | ⬜ |
| 2 | Fix all onboarding exits → `/today?first=1` (see redirect bugs) | ⬜ |
| 3 | Collapse tarot/number/symbolic below fold | ⬜ |
| 4 | Remove equal-weight «статья» blocks | ⬜ |
| 5 | Hide Profile depth CTA on D1 | ⬜ |
| 6 | Sticky «Закрыть день» CTA (links to E2 evening) | ⬜ |
| 7 | `markFirstTodayCompleted` (exists in `page.tsx`) | ✅ partial |
| 8 | Story gate review | ⬜ |

**Reuse:** `buildFirstTodayPackage` · `FirstTodaySurface` · `firstTodayState.ts` · Today contract/narrative APIs.

---

## Epic 2 — Daily Loop

### E2-S1 · Evening close (Day 1)

**Blueprint:** §4 Вечер  
**Code:** `TodayDayContinuityEveningClose.tsx` · `TodayDayContinuityClosed.tsx` · `todayDayContinuity.ts`

| # | Task | Status |
|---|------|--------|
| 0 | Story brief — **Evening** row | ⬜ |
| 1 | React: close + confirmed copy | ⬜ |
| 2 | Mount evening flow on **First Today** path (not only `TodayExperienceSurface`) | ⬜ |
| 3 | Entry: sticky CTA from E1-S3 | ⬜ |
| 4 | Outcomes: done / partial / not_done + optional note | ✅ exists |
| 5 | Confirmed copy: «Завтра утром… начнёт с того, что было сегодня» | 🟡 verify copy |
| 6 | Persist via `saveDayContinuity` | ✅ localStorage v0 |

---

### E2-S2 · Day 2+ continuity first

**Blueprint:** §5 День 2+  
**Code:** `buildContinuityOpeningLine` · `TodayS0Greeting` (`continuityLine` prop)

| # | Task | Status |
|---|------|--------|
| 0 | Story brief — **Day 2** row | ⬜ |
| 1 | React: continuity **above** ritual | ⬜ |
| 2 | Show opening line **before** ritual entry / tarot pick | ⬜ |
| 3 | Unclosed yesterday: soft prompt (Blueprint copy) | ⬜ |
| 4 | Default `/today` for returning users uses same hierarchy as First Today post-D1 | ⬜ |
| 5 | Reduce ritual gate as **first** interaction on D2+ | ⬜ |

**Reuse:** entire `todayDayContinuity.ts` module; evening components.

---

## Epic 3 — Hook · Compatibility

**Blueprint:** §7 Compatibility  
**Code:** `frontend/src/app/compatibility/**` · `CompatibilityDesktopWireframe.tsx`

**Принцип (Product Model §5.4):** Public Compatibility **живёт сама**; Personal — глубже внутри TF. Launch **не** схлопывает `/compatibility/*` в Today-only.

| Level | Launch scope | Status |
|-------|--------------|--------|
| **L1 Public** | Standalone routes работают без account; SEO/share entry | 🟡 exists — **preserve** |
| **L2 Personal** | Hook в Today + «через твою модель» при account | ⬜ E3 |

| # | Task | Status |
|---|------|--------|
| 0 | Story brief — **Compatibility** row (inside-TF hook only) | ⬜ |
| 1 | React: hook card on Today scroll + D2 | ⬜ |
| 2 | Public flow unchanged: `/compatibility/*` standalone value | ✅ preserve |
| 3 | Personal layer copy when authenticated (Model-aware line) | ⬜ |
| 4 | Card CTA → existing flow; save person when logged in | ⬜ |
| 5 | Return: Today or Profile — no dead end | ⬜ |
| 6 | Story gate: hook continues story **without** breaking public entry | ⬜ |

**Reuse:** existing compatibility flows — **no new API entity**.

**Not in launch:** share CTA polish; full Personal dynamics v2.

---

## Epic 4 — Profile (launch-minimum)

**Blueprint:** §6 Profile  
**Code:** `frontend/src/app/profile/page.tsx` (full natal)

| # | Task | Status |
|---|------|--------|
| 0 | Story brief — **Profile** row | ⬜ |
| 1 | React: identity + «Мои дни»; deep layers collapsed | ⬜ |
| 2 | Top: name · sign · life path · 1-line character | 🟡 data exists |
| 3 | **«Мои дни»:** N days · last 3–7 focus + outcome from `day_continuity` records | ⬜ |
| 4 | «Моя карта» teaser → expand | 🟡 partial |
| 5 | «Совместимости» list + quick add | 🟡 partial |
| 6 | Collapse full natal / patterns / deep history | ⬜ |
| 7 | Nav: Profile not primary highlight before D3 | ⬜ |

**Reuse:** `coreProfile` · `natalPreview` · `profileCircleItems` · compatibility routes.

---

## Infrastructure already built (do not rebuild)

| Capability | Location | Launch use |
|------------|----------|------------|
| First Today package builder | `lib/firstTodayPackage.ts` | E1-S3 |
| First Today state | `lib/firstTodayState.ts` | guards, completion |
| Day continuity v0 | `lib/todayDayContinuity.ts` | E2 |
| Evening UI | `TodayDayContinuityEveningClose` / `Closed` | E2-S1 |
| Today experience surface | `TodayExperienceSurface.tsx` | E2-S2 base |
| Onboarding chips + events | `lib/onboardingContext.ts` | E1-S2 |
| Core profile / birth setup | `useCoreSetupFlow` · API | E1-S2 |
| Compatibility flows | `app/compatibility/**` | E3 |
| Meaning events | `useMeaningRuntime` | all epics |
| Auth redirect helpers | `lib/authRedirect.ts` | fix targets E1 |

---

## Launch debt (accepted for v1)

| Item | Notes |
|------|-------|
| Day continuity in **localStorage** only | Server persist → v2; document for field test |
| PIM / LLM architecture unchanged | Infrastructure invisible to user — OK for launch |
| iOS parity lags web | After web launch path story gates; [IOS_TODAYFLOW_STATUS.md](./IOS_TODAYFLOW_STATUS.md) |
| `TODAY_CANON_VS_CODE_DIFF.md` | Ritual-first analysis — superseded for **launch path** by this plan |
| Analytics `signup_source` etc. | Tracker P0 optional; wire when field test starts |

---

## Metrics (field test gate)

Measure **behavior**, not surveys.

| Metric | Definition |
|--------|------------|
| Landing → Start | CTA click / unique landing |
| Start → Today | Reached First Today with personal content |
| D1 → D2 | Return next calendar day (no push) |
| D2 → D3 | Loop retention |
| Evening close rate | `day_continuity` closed / D1 sessions |
| Compatibility open | Hook click → flow started |
| Unprompted return | Opens without notification |

**v2 gate:** review metrics → open next product cycle only then.

---

## iOS (after web E1–E4)

Native app: `ios/TodayFlow/`. Same REST contracts; native UI per [cross-platform rule](../.cursor/rules/cross-platform-mobile.mdc).

| Web story | iOS follow-up |
|-----------|---------------|
| E1 Landing | App Store / deep link TBD — not blocking web launch |
| E1 Onboarding | Native onboarding flow parity |
| E1–E2 Today | `Today` native screen — hierarchy + evening + continuity |
| E3 Compatibility | Native compatibility entry + hook |
| E4 Profile | Strip to launch-min + «Мои дни» |

Track in tracker; **web story path first**.

---

## Story walkthrough (DoD #10)

**Participants:** Product (story editor) + Eng.

**Единственный вопрос на каждом экране:** продолжает историю или прерывает?

**Pass:** сквозная фраза из §Launch Story Script — без ощущения «разных приложений».

**Fail:** переделать экран в React; не «подкрутить дизайн».

---

## v2 backlog rule

См. также **Launch Freeze** выше.

New idea → answer: **needed for launch v1 DoD?**

- **No** → one line in tracker; **do not discuss** until field results.
- **Yes** → must fit Epic 1–4 + Launch Freeze allowlist; no new entities.

---

## Doc cleanup (non-blocking)

- [ ] [FIRST_DAY_EXPERIENCE.md](../FIRST_DAY_EXPERIENCE.md) — banner OK; trim active links to this plan
- [ ] [BEHAVIOR_CHANGE_TEST_V0.md](./BEHAVIOR_CHANGE_TEST_V0.md) — remove Demo from ship path
- [ ] [TODAY_CANON_VS_CODE_DIFF.md](./TODAY_CANON_VS_CODE_DIFF.md) — add pointer to this file for launch
- [ ] Tracker P0.1 «demo done» — footnote **REVERSED for launch** (already in Blueprint)

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-01 | User Journey Path v1 — question → answer per step |
| 2026-07-01 | Product Model v0.4.2 — Maps not Journey |
| 2026-07-01 | Standalone value law §5.4; Compatibility L1/L2 in E3 |
| 2026-07-01 | **No Figma** — story-first React; Launch Story Script | Режиссура истории, не макеты |
| 2026-07-01 | Process freeze: Launch DoD, Launch Freeze, Decision Log |
| 2026-07-01 | Initial execution plan: as-is code map, Epic 1–4 stories, phases, reuse, launch debt |
| 2026-07-01 | Value-first wiring: claim → `/today?first=1`; save dev-token → immediate First Today; demo → welcome |
| 2026-07-01 | Meaning events: in-batch dedup (backend) + outbox chunk dedup (frontend) |
