# TodayFlow iOS Status

Updated: 2026-07-05

## Shared auth contract (2026-07-23)

iOS/Android must use the same Bearer session as web — see [AUTH_SESSION_CONTRACT_V1.md](../AUTH_SESSION_CONTRACT_V1.md):

- Store `access_token` + `refresh_token` (Keychain / EncryptedSharedPreferences).
- On 401: one `POST /auth/refresh`, then retry; only then clear session.
- Pre-account profiles: upsert `/guest/profiles` before email; claim binds server rows.
- Do not invent cookie-only or app-local auth that web cannot share.

Updated: 2026-07-23 (auth refresh + durable guest_profiles).

## Scope

This status tracks the native iOS product work for TodayFlow.

Important:
- The active Xcode app for the current working branch is in `/Users/victoria_tatarynovich/TodayFlow/ios/TodayFlow`.
- The monorepo at `/Users/victoria_tatarynovich/TodayFlow` remains the source of backend, frontend, product docs, and service contracts.
- The iOS app is not a separate product definition.
- iOS consumes the same service, the same contracts, and the same product canon as web.
- If web canon changes, iOS must follow the same direction instead of inventing parallel logic.

## Reality Check

As of 2026-03-30, the native app is no longer positioned as a web wrapper.

Current truth:
- Root navigation is native SwiftUI.
- The main shell no longer opens an embedded web view for tab-level flows.
- `Today`, `Calendar`, `Goals`, `Questions`, `Compatibility`, `Tarot`, `Explore`, `Profile`, `Auth`, and `Onboarding` exist as native screens in this repo.
- Some user-facing copy still reflects staged rollout, but the product direction is now explicit: native first, with web parity as the implementation target rather than the presentation layer.

## Native Parity Snapshot

### Strong / already native

- Auth and session persistence
- Onboarding and birth data capture
- Today opening flow and day-state interaction
- Calendar and tracker overview
- Goal creation and goal progress logging
- Questions flow
- Compatibility flow
- Tarot daily card and guided spreads
- Profile summary
- **Practices (2026-07-05):** таб «Практики» в `ContentView`; wizard goal → direction → catalog (`PracticesWizardHubView` + `PracticeCatalogContent`); history + detail через `PracticesRootView`; deep link `/practices`, `/practices/history`, `/practices/{id}`

### Partial / native shell exists but depth is still behind web

- Today ritual secondary actions: блок «Собрать день» и **сферы** выровнены с вебом по смыслу и общему копирайту (`TodayRitualCopy`); быстрые чипы «Собрать день» — `TodayRitualCopy.BuildDayQuickChips` (паритет веб `RITUAL_BUILD_DAY_QUICK_CHIPS`); карта → число → тон дня — **горизонтальный дек**. **Хребет ритуала** формализован в `TodayRitualStateMachine.swift` (снимок, фазы, запрет недопустимых шагов, `TodayRitualSpineReducer`); события `number_selected` / `mood_selected` для шагов числа и настроения уходят только через **`analyticsHint`** в `applySpineEffects` после успешного перехода (паритет с веб `todayRitualSpineMachine` + Android `TodayRitualSpineMachine`); если guide за день уже есть — **`generationLogId`** из `todayGuideNarrative` (как на вебе `narrativeGenerationIds.guide`). Юнит-тесты: `TodayFlowTests/TodayFlowSmokeTests.swift`. Секция **«Главный шаг на сегодня»** и блок **DE-7** по `fusion.activity_context.guide_meaning_completions_today`: eyebrow «Сегодня в Flow», чипы по ненулевым счётчикам и пустое состояние (паритет веб `TodayResultView`, `GuideMeaningCompletionsFocusStrip`). Чипы «дисциплина / деньги / близость / эмоции» переключают на **Flow** и открывают соответствующий сценарий: фокус на создании привычки, шит новой цели (`weekly-goals`), шит контракта аскезы (`ascetic-contracts` + каталог `/practices/asceticisms`).
- **Привычки в Flow:** шаблоны из того же набора, что `HABIT_TEMPLATE_GROUPS` на вебе (`TrackerHabitTemplates`), создание через `POST /habits` с `category` (label категории), `target_frequency` daily/weekly и `target_per_period`, как в `EntityCreateWizard`.
- **Fusion:** ответ `GET /tracking/fusion/{date}` содержит `rhythm_context` и **DE-9** `day_history` (`FusionIndex.dayHistory`: scores, week summary, meaning signals, **v1.5** `reflection_excerpt`); полоска в `TodayRitualFlowView` (ritual + spheres), паритет веб `TodayDayHistoryStrip`.
- **Learning (implicit):** раскрытие «Почему так?» в сводке дня ритуала шлёт **`today_guide_why_opened`** (`trackTodaySurfaceEvent`, при наличии — `generation_id` от `todayGuideNarrative`), паритет веб `trackMeaningEvent`. Полоска **DE-9** при первом появлении (`ritual_after_callout` / `your_day_spheres`) — **`today_day_history_first_visible`**; выбор карты / уточнителя / «применить к дню» — **`tarot_selected`** с опциональным `generationLogId`, как на вебе.
- **DE-8 narrative depth:** `AccountSettings.todayNarrativeDepthLevel` + picker в `ProfileSettingsView`; **на экране «Сегодня»** — сегмент «Глубина текстов дня» (`TodayNarrativeDepthInlineBar` в `TodayView`, канон `TodayRitualCopy.NarrativeDepthControl`) + `TodayFlowStore.updateTodayNarrativeDepthLevel` (частичный PUT); после успешной смены — `trackTodaySurfaceEvent` с типом **`today_narrative_depth_changed`** (паритет веб meaning). `GET /auth/me` → `AuthSession.insightDepthTier`; режим «Глубже» только при `pro`/`premium`; `POST /today/narrative` без override в теле — сервер + тарифный кламп. Оболочка экрана (строки загрузки, нижний бар «Фокус …») — `TodayRitualCopy.TodayPageShell` / `FocusTimerChrome` (паритет веб `RITUAL_COPY` §5.3). Тексты тостов и ошибок экрана Today и пресеты «удачного окна» числа — `TodayPageToasts`, `NarrativeDepthToasts`, `NumerologyLuckyDayPresets` (зеркало веб `RITUAL_COPY` / `NUMEROLOGY_LUCKY_DAY_PRESETS`).
- Tarot catalog and saved spreads
- Profile interpretation depth
- Tracker insights, diary, and progress views
- Weekly and cycle summaries
- Natal chart and richer astrological visualizations
- Subscription and account management detail

### Missing or materially behind web

- Catalog surfaces (non-practice)
- Reports surfaces
- Forecast archive and themed forecast screens
- Library and discover surfaces
- Dedicated growth/help education surfaces
- Admin surfaces

## Shared Product Rule

There is one TodayFlow product, not one web product and one iOS product.

The shared rule is:
- **Profile** — **Quick Map** (`ProfileQuickMapView`, PM-1 v0.8): слой 1 editorial hero + resume panels · слой 2 каркас · слой 3 натал в nested `DisclosureGroup` (натал · 4 дома · **полная карта** 12 домов/планеты/аспекты); CUM confirm внутри Quick Map; deep link раскрывает и скrolls. Ниже — сферы жизни, круг людей, pulse.
- Натальная карта — **source layer** внутри Profile, не отдельный экран; API `GET /natal-chart/` без изменений.
- `Today` is the daily decision engine.
- daily interactions are also signal collection for future personalization.
- weekly and monthly state maps are accumulated understanding layers, not separate product roots.

Important implementation rule:
- business logic and interpretation direction belong to the service;
- iOS may adapt pacing and presentation for native UX;
- iOS must not invent a different meaning model, JTBD model, or personalization model.
- iOS must consume the same evolving learning model: answers, journals, route choices, feedback, and psychotype synthesis all come from the shared service, not from app-local logic.

## What Is Already Done

### App foundation

- Full SwiftUI app shell is in place.
- Auth flow exists: sign in, sign up, password reset, password change, sign out.
- Session is persisted between launches.
- Onboarding exists with birth data capture and location suggestions.
- Birth profile and app snapshot are persisted locally.

### Product routing

- The app no longer uses a generic placeholder home.
- The native `Today` screen is aligned to the real core product direction around `/today`.
- The screen is structured as a mobile-native flow instead of a direct web clone.
- The app is expected to reflect the same `Today = decision engine + signal collection` direction as the service.

### Data integration

- Backend auth is wired.
- Geocode suggestions are wired.
- Astro chart bootstrap is wired with fallback behavior.
- `/today` is wired as the main day payload.
- `/morning-ritual/today` and `/today` are the canonical daily interpretation sources.
- `tracking/fusion/{date}` is wired and used for the state map.
- User answers are saved back to backend:
  - morning intention
  - pulse/state check
  - ritual feedback
  - mini-decision answer
  - question-of-day answer
  - journal entry
  - evening reflection

### Today interaction layer

- `Today` now contains real input surfaces, not only read-only cards.
- User input is stored and then used to refresh the day state.
- A first `state map` layer exists:
  - energy
  - emotional balance
  - focus
- Daily signals are also available as a separate accumulated layer for weekly/monthly state maps.
- Multi-day fusion history is loaded and persisted.
- The UI now derives:
  - trend direction
  - repeated risk pattern
  - lightweight correlation insight from user behavior
- The next day can now also adapt from recent `daily signals`, not only from static profile and transits.
- `Profile` can now expose a living personalization layer from the same service contract: recent signal summary, weekly state, and recent insights sit on top of the stable profile map.
- The shared service now also exposes an initial `user learning context`: response style, support style, dominant lanes/topics, and feedback-derived stats can be consumed by iOS from `core_profile.living.learning_context`.
- The service also keeps an internal quality-memory loop: generated answer -> user reaction -> downstream outcome. This loop improves future responses, but must stay invisible in user-facing app language.

### Performance and loading fixes already made

- Onboarding no longer blocks forever on slow service calls.
- Network requests now have explicit timeouts.
- `account/core-setup` no longer blocks onboarding completion.
- The app no longer waits for the full `/today` payload during onboarding bootstrap.
- `Today` loads its heavy product payload separately after entry into the app.

## Product Decisions Already Chosen

### Direction for `Today`

We are not building a decorative astrology page.

The chosen direction is:
- native mobile `Today`
- interactive
- stateful
- cumulative
- progressively revealing
- powered by the same service-side decision logic as web
- centered on one day screen, not separate morning/day/evening products

The purpose of the screen is:
- help the user enter the day quickly
- capture useful state signals
- improve personalization over time
- create desire for deeper interpretation
- return clearer and more personal answers on later days because the system learned the user better

### Free vs paid principle

The product should not dump everything in one request or one screen.

The chosen principle is:
- free layer gives fast entry and useful daily contact
- paid layer gives depth, continuity, interpretation, and adaptive intelligence

Free should be enough to create habit.
Paid should be what turns habit into personal guidance.

### Loading principle

We should not load the whole day in one blocking request.

The chosen UX principle is:
- show something useful immediately
- keep the user active while deeper layers are loading
- reveal the day in layers

This means the product should move toward:
- quick opening layer
- state check
- micro action
- teaser of deeper meaning
- premium deep interpretation

## Current Problems Still Open

### Heavy `/today`

The backend `/today` payload is still too heavy for first render.

Observed behavior:
- it may respond successfully
- but generation is slow because it pulls expensive downstream logic, including OpenAI-backed content generation

### Too much bundled into one endpoint

Right now `/today` still behaves too much like a monolithic page payload.

This is bad for:
- perceived speed
- mobile UX
- progressive reveal
- monetization structure

### Astro chart request issue

Some clients called `POST /chart` without `birth.location` while Pydantic required it, which produced `422`. The astro service now treats `location` as optional with a default, normalizes `HH:MM:SS` times, and the backend HTTP client fills `location` from coordinates when missing. Remaining 422s, if any, should be investigated per payload (e.g. non-numeric coordinates).

## What We Will Do Next

### 1. Keep one canonical `Today`, but allow layered delivery under the hood

Target direction:
- `/today/opening` — **live** (DayConnection + stage flags only; no morning payload)
- `/today/checkin-prompt` — **live** (next micro check-in from DayConnection; no LLM)
- `/today/core` — **live** (fast morning bundle without life-area `scenarios` list)
- `/today/scenarios` — **live** (life-area scenarios; usually warm cache after `/today/core`)
- `/today/state-map` — **live** (alias of `GET /tracking/fusion/{date}` under `/today`)
- `/today/evening` — **live** (evening connection fields + `DayRitual` when present)

Also live on the monorepo backend:
- `GET /today?light=1` — same contract as full `/today` but skips per-day trackers, journal slice, evening ritual object, and rewards aggregation (progressive load after opening).
- `GET /today/bundle` — **один** проход сборки утра: в ответе и `core`, и `scenarios` (внутри TTL-кеш 120s на пару user+date+locale, как у отдельных `/today/core` и `/today/scenarios`).

### Push reminders (shared contract)

Rhythm pushes (утро / день / вечер) и напоминания о **цели на день** завязаны на локальное время пользователя и флаг `push_opt_in` в настройках.

- `POST /notifications/devices` — регистрация FCM/APNs/Web token (`platform`: `ios` | `android` | `web`).
- `DELETE /notifications/devices/{id}` — отзыв токена.
- `GET/PUT /notifications/schedule` — таймзона (`IANA`), включение слотов и локальное время для: утреннего, дневного, вечернего напоминаний + двух **nudge** по цели дня (полдень / послеполуденное). Дополнительно: **`quiet_start` / `quiet_end`** (локальные `HH:MM`, типично 22:00–08:00) — в это окно крон не шлёт ритм и nudge по цели; **`max_auto_per_day`** (1–15, дефолт 5) — лимит записей в `push_dispatch_log` за локальный день для видов `morning_rhythm`, `day_rhythm`, `evening_rhythm`, `goal_midday`, `goal_afternoon`. Категории-тумблеры: `notify_rhythm_today`, `notify_goal_nudges`, `notify_goal_ack` (мгновенный «цель сохранена»; тоже уважает тихие часы), плюс резерв под будущие хуки: `notify_streak_care`, `notify_weekly_focus`, `notify_tarot_card`, `notify_habit_reminders`, `notify_comeback`.
- Сохранение **цели на день** через `POST /day-connection/{date}` с `morning_intention` обновляет снимок `daily_goal_snapshots` и при **изменении** текста шлёт мгновенный пуш «цель сохранена» (если есть устройство и `push_opt_in`).
- `POST /internal/push/run-due` + заголовок `X-Push-Dispatch-Secret` (env `PUSH_DISPATCH_SECRET`) — точка для крона/воркера: рассылка due-напоминаний по расписанию. В ответе счётчики включают **`blocked_quiet`** и **`blocked_cap`** (сколько раз в этом прогоне слот был бы отправлен, но остановлен тихими часами или дневным лимитом). Реальная доставка при наличии `FCM_SERVER_KEY` (legacy HTTP); иначе — логирование и учёт в `push_dispatch_log`.

### Push hooks roadmap (что ещё нужно и как не спамить)

**Принцип:** держать пользователя через **ритм и смысл**, а не через количество сообщений. Пуш = либо **согласованное расписание**, либо **редкое событие с высокой ценностью**, либо **транзакционный** (аккаунт/оплата).

**Уже заложено в сервисе (live):**
| Хук | Тип | Комментарий |
|-----|-----|-------------|
| `morning_rhythm` / `day_rhythm` / `evening_rhythm` | Расписание | Якоря дня; пользователь управляет временем и on/off в `user_push_schedules`. |
| `goal_midday` / `goal_afternoon` | Расписание | Только если есть текст цели в `daily_goal_snapshots` на сегодня. |
| `goal_saved` | Событие | Сразу после **изменения** `morning_intention`; не дублировать при повторном сохранении того же текста. |

**Рекомендуемые следующие хуки (нужна доработка бэкенда + тумблеры в настройках):**

| Хук | Когда срабатывать | Анти-спам |
|-----|-------------------|-----------|
| **Streak / день под угрозой** | Вечер (один слот, напр. после `evening_time`), только если сегодня ещё нет «активности дня» по правилам продукта (нет завершённого минимального чекина в Today). | Макс **1** в день; не слать, если пользователь уже открыл Today сегодня и сделал чекин; опциональный выключатель «забота о серии». |
| **Недельный фокус** | 1 раз: воскресенье вечер или понедельник утро (локально), если есть активная `WeeklyGoal` и нет прогресса за текущую неделю. | Макс **1** в неделю на этот тип; отдельный toggle. |
| **Мягкое «карта дня»** | Если в продукте есть явный «ритуал карты дня» и пользователь **ни разу** не заходил в него сегодня — один мягкий вечерний nudge. | Только при включённом **Tarot / daily card** preference (см. уже существующие reminder-настройки в модуле tarot); макс 1/день. |
| **Практика / привычка** | По выбранному пользователем времени или «после утреннего слота + 2ч», если есть активная привычка с напоминанием. | Строго по explicit opt-in на тип активности; не смешивать с ритмом Today без согласия. |
| **Re-engagement** | Нет сессий **N** дней (например 3–5). | Макс **1** раз в 7 дней; отдельный канал/toggle «редкие напоминания»; не в часы тишины. |
| **Транзакционные** | Сброс пароля, смена почты, успех/ошибка оплаты, истечение подписки. | Без лимита по продуктовой необходимости; не смешивать с маркетинговым текстом. |

**Глобальные правила (внедрять в `run-due` и событийные отправки):**
- **Лимит «продуктовых» пушей в сутки** (кроме transactional): например не более **4–5** автоматических на пользователя; приоритет: событие выше расписания или наоборот — зафиксировать в политике (разумно: transactional > goal_saved > rhythm > optional nudges).
- **Тихие часы** (настраиваемые, дефолт например 22:00–08:00 локально): в этот интервал не слать rhythm / goal / streak / re-engagement; transactional — по необходимости.
- **Не дублировать смысл в одно окно**: если за 30 минут уже ушёл пуш того же «семейства» (например утро), не слать второй с похожим CTA.
- **Уважать `push_opt_in` и отдельные категории** (следующий шаг API): `rhythm_today`, `goal_nudges`, `streak_care`, `weekly_focus`, `tarot_card`, `habits`, `comeback`, `account` — чтобы пользователь мог отключить «заботу о серии», но оставить «утро/вечер».

**Что сознательно не делать пушами (или только in-app):**
- Каждый новый инсайт / каждый сгенерированный абзац.
- Любая «лестница» из 3+ напоминаний подряд без действия пользователя.
- Промо и кросс-продукт без отдельного маркетингового согласия.

**Технические хуки для бэкенда (backlog):**
- Единый **`NotificationIntent`** в коде: `kind`, `priority`, `dedupe_key`, `respect_quiet_hours`.
- Таблица или расширение **`user_push_schedules`**: `quiet_hours_start/end`, `max_auto_per_day`, флаги категорий.
- Событийные вызовы из: завершения чекина дня, `WeeklyGoal` create/update, `TarotDraw`/card-of-day open (для условий «не открывал»), `last_active_at` для re-engagement.

Goal:
- fast first paint
- better mobile pacing
- independent retries
- better free vs paid separation

Important:
- this is a delivery/runtime split, not a product split;
- the user should still experience one `Today` surface;
- morning/day/evening are timing accents, not separate roots.

### 2. Design the free daily loop

Free layer should include:
- fast daily opening
- one state check
- one short action
- one teaser insight
- saved history that improves future relevance
- clear `energy / focus / risk` reading when the service provides it

Goal:
- make the user return daily
- make the system learn from behavior

### 3. Design the paid depth layer

Paid layer should include:
- deeper meaning of the day
- life-area scenarios
- stronger adaptive interpretation
- richer state history and patterns
- evening synthesis and longitudinal insights
- weekly/monthly state maps as better understanding of the same person

Goal:
- not just "more text"
- but clearly better personal guidance

### 4. Improve loading UX in the app

Need to replace passive waiting with active entry:
- immediate opening statement
- quick state capture
- micro progress
- locked or teaser deeper blocks

Goal:
- user feels the day already started
- not that the app is still thinking

### 5. Fix backend integration gaps

Immediate technical backend follow-ups:
- monitor `astro /chart` for any remaining validation failures after location/time fixes
- reduce cost and latency of `/today` (use `/today/opening` + `light=1` where appropriate; continue splitting heavy generation off the critical path)
- move heavy generation off the critical path

## Working Rule Going Forward

We will keep polishing the current direction, not restart it.

The current direction is considered correct:
- mobile-first
- interactive
- layered
- habit-forming
- personalization-driven
- monetization-aware
- service-first in logic, native-first in presentation
- one product canon across web and iOS

Next work should improve:
- pacing
- usefulness
- clarity
- reveal logic
- speed
- alignment with the shared service contracts and shared product canon

without losing the product direction already established.
