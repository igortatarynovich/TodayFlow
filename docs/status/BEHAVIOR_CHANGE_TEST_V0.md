# Minimum Day Cycle + Behavior Test (operational, not canon)

**Дата:** 2026-06-23  
**Статус:** **IN_PROGRESS** — ship gate **до** первых 5–10 людей · behavior test **BLOCKED** · Run 3 gratitude 2026-09-18: calendar D+1 OK, magic-link claim + 2nd person still open  
**Не канон:** продуктовый минимум и протокол поля; не новые AR · не PR2 scope.

---

## Главный вопрос *(после ship gate)*

> **Становится ли день человека лучше благодаря прохождению полного цикла** — а не благодаря отдельному экрану Today?

До этого цикла — разговоры про retention · PR2 · Discovery · behavior change **преждевременны**.

---

## Два крайних действия — **не делать**

| ❌ | Почему |
|----|--------|
| Ещё месяц архитектуры | Infra достаточна; продукта нет |
| Полевой тест на фрагменте (S0–S5 без вечера) | Ложный отрицательный сигнал |

---

## Два пробела *(predmetno)*

### Gap 1 — Evening Close как **событие**, не блок контента

**Сейчас:** пользователь получает Today, но продукт не отвечает: *«Что произошло с моим днём?»*

**Нужно:** закрытие цикла, не ещё один insight.

| Утро | Вечер |
|------|-------|
| «Что сегодня **главное**?» | «Что произошло с **этим главным**?» |

**Минимум v0:**

1. **Outcome** — 3 варианта: **Сделал** · **Частично** · **Не сделал**
2. **Один короткий вопрос:** «Что помешало или помогло?» *(free text или 2–3 chips — не Discovery scheduler)*

**Без:** анализа · Discovery engine · ILR · trait write · PR2 Intent Record *(можно localStorage + `meaning_event` day-0)*.

**Ощущение:** завершённость дня.

### Gap 2 — Обещание **завтра**

**Сейчас:** день заканчивается в пустоту.

**Нужно:** *«Завтра приложение продолжит этот разговор»* — **непрерывность**, не новый контент.

**Минимум v0:**

- показать связку: **вчерашний фокус → сегодняшний результат → завтрашняя отправная точка**
- пример формулировки: *«Завтра начнём с того, как сегодняшний результат повлиял на ваш следующий шаг.»*
- при следующем открытии `/today`: **1 строка** continuity *(не прогноз · не новый ритуал)*

**Без:** новых карточек · инсайтов · экранов · Discovery-вопросов · сущностей.

---

## Минимальный Ship Gate *(v0 — только это)*

```
Landing → Demo → Signup → Onboarding → Today → Evening Close → Tomorrow Return
```

| Фаза | Содержание | Код *(2026-06-23)* |
|------|------------|---------------------|
| **Утро** | Theme · Insight · **Main Focus** | `TodayExperienceSurface` S0–S5 · PR1 path — **есть** |
| **День** | Главное действие *(optional v0 — one CTA)* | legacy `/today` · partial; **не** в experience spine |
| **Вечер** | Сделал / Частично / Не сделал + что помогло/помешало | **нет** в experience surface; legacy evening = scroll + много полей |
| **Завтра** | Причина вернуться · continuity | **нет** явного hook |

**Onboarding path:** [FIRST_DAY_EXPERIENCE.md](../FIRST_DAY_EXPERIENCE.md) — core largely DONE; verify intent → reality → `/today`.

**Не в scope v0 ship:** PR2 write-path · IR · atoms · Discovery · новые AR.

---

## Что **НЕ** добавлять

- новые карточки · инсайты · ритуалы · экраны
- Discovery-вопросы · дополнительные сущности
- месяц PR2-архитектуры «ради данных»

**Проблема — не нехватка контента. Проблема — нет завершённого цикла.**

---

## Implementation *(web · код в репо, UI не верифицирован)*

**Файлы в репозитории** (проверено grep/read, не walkthrough):

- `frontend/src/lib/todayDayContinuity.ts`
- `frontend/src/components/today/experience/TodayDayContinuityEveningClose.tsx`
- `frontend/src/components/today/experience/TodayDayContinuityClosed.tsx`
- wiring в `TodayExperienceSurface.tsx` + `TodayS0Greeting.tsx`

**Unit-тесты** (`npm test -- --testPathPattern=todayDayContinuity`): 5/5 pass *(2026-06-23, локально)*.

**UI / ship gate:** не подтверждено. См. walkthrough ниже.

---

## Walkthrough — продуктовая приёмка

### Run 2 *(2026-06-23 · после фиксов)*

**Статус:** **ядро Day Continuity работает · ship gate не пройден** (DoD 3/6).

**Стек:** postgres (local) · backend `:8080` · astro `:8081` · frontend `:3000`.

**Фиксы перед прогоном:** CORS `:3001` в dev · onboarding → `/today` (не `?first=1`).

| # | Шаг | Результат |
|---|-----|-----------|
| 1 | Лендинг `:3000/` | **OK** |
| 2 | Демо `/demo/today` | **OK** · evening close **нет** |
| 3 | Регистрация | **API OK** · UI submit не проверен (automation fill ≠ React state) |
| 4 | Core onboarding | **API OK** · UI форма грузится |
| 5–6 | Intent / Reality | **Не в UI** · контекст задан вручную |
| 7 | Today | **OK** — `TodayExperienceSurface`, фокус после S5 |
| 8 | Закрыть день | **OK** — `evening_close` → **Сделал** → `day_closed` + tomorrow hook |
| 9 | Continuity | **OK** — S0 line при closed record на вчера *(симуляция D−1)* |

### Run 1 *(до фиксов)* — BLOCKED

CORS `:3001` · demo 404 на `:3000` · onboarding → `FirstTodaySurface`.

### Остаётся до ship gate *(не PR2 · не Discovery · не новые экраны)*

1. **Signup → onboarding → `/today` целиком через UI** — закрывает DoD «полный путь нового пользователя».
2. **Календарный день 2** — тот же аккаунт, утро после **настоящего** закрытия вчера; continuity line без подстановки в localStorage.
3. **2 дня подряд** — второй человек/участник команды повторяет тот же цикл.

→ после 1–3 можно сказать: **ship gate passed** для первого закрытого дневного цикла → behavior test.

### Run 3 — чеклист *(заполнять по факту)*

⚠️ **Dead path (не выполнять, не возвращать в код):** шаги 7–8 ниже — June Close Day (Сделал · Частично · Не сделал). Канон вечера: `TODAY_PRODUCT_FLOW_V1` §4 gratitude. Живой прогон 2026-09-18 — таблица **Run 3 gratitude** сразу под этой.

**Дата D (сегодня):** __________ · **аккаунт (email):** __________ · **кто проходил:** __________

| # | Шаг | OK / BROKEN | Заметка |
|---|-----|-------------|---------|
| 1 | `/` → «Начать бесплатно» | | |
| 2 | `/auth?mode=signup` — регистрация **в UI** | | |
| 3 | `/onboarding/core` — имя, дата, место, submit | | |
| 4 | `/onboarding/intent` — выбор chip | | |
| 5 | `/onboarding/reality` — выбор chip → **`/today`** (не `?first=1`) | | |
| 6 | Ritual → S5 → **main focus** зафиксирован | | |
| 7 | «Закрыть день» → outcome + note → **day_closed** | DEAD | Launch cut 2026-08-30. Не реализовывать. |
| 8 | Tomorrow hook на экране закрытия | DEAD | Заменено `T1.continuity` с GET вчерашней gratitude. |

**Дата D+1 (завтра, тот же аккаунт):**

| # | Шаг | OK / BROKEN | Заметка |
|---|-----|-------------|---------|
| 9 | `/today` → S0 **continuity line** *(без ручного localStorage)* | | Живой слот: `T1.continuity` |
| 10 | Фокус дня + закрытие второго дня | | Вечер = gratitude, не outcome |

**Run 3 — второй человек:** повторить D + D+1 · имя: __________

### Run 3 gratitude *(2026-09-18 · live `todayflow.today` · не June Close Day)*

**Дата D:** 2026-09-18 · **D−1 seed:** 2026-09-17 · **кто:** agent walkthrough · **аккаунт D+1:** `run3-gratitude-*@example.com` (API signup + core-setup; JWT в UI, не magic-link)

Живой путь, не таблица June:

| # | Шаг | OK / BROKEN | Заметка |
|---|-----|-------------|--------|
| 1 | `/` → CTA в продукт | **OK** | CTA = «Собрать мой Today» → `/onboarding/invite`. «Начать бесплатно» / `/auth?mode=signup` на лендинге нет. |
| 2 | Invite → welcome имя | **OK** | «Построить мой Profile» → `/onboarding/welcome?fresh=1`. Имя «Анна» в UI. |
| 3 | Birth → preview | **PARTIAL** | Preview открылся с Тельцом без свежего ввода даты в этом прогоне (guest draft уже был committed — `beginGuestOnboardingSession` не стирает). Intent/reality chips = First Today `?first=1`, не `/onboarding/intent`. |
| 4 | `/today?first=1` guest | **OK** | Composition + pitch. «Закрыть день» нет. До 18:00 MSK evening frame нет. На ритуале `Далее` disabled (последний шаг; next-anchor не обещает «Вечер»). |
| 5 | `/onboarding/save` | **OK (форма)** | Magic-link: «Куда прислать вашу карту?» / «Прислать ссылку». Письмо не открывали (нет inbox) — claim не закрыт в UI. |
| 6 | Authenticated `/today` (реальный календарь 18.09) | **OK** | После retry. `T1.continuity` с GET `/day-connection/2026-09-17` (без route-mock, без подстановки localStorage): «С чего продолжить» / «Вчера в фокусе было: «держать одно главное». Вечер сохранён благодарностью: тихий вечер у окна.» Нет «Закрыть день». MY DAY: «Дыхание 4-7-8» (`GET /practices/select`). На MY DAY `Далее` disabled — evening time-gated. |
| 7 | Evening gratitude persist | **OK (Playwright clock)** | `frontend/e2e/evening-d1-continuity.spec.ts` vs live: **1 passed (8.7s)**. Стена 18:00 MSK в этом прогоне не ждали (~15:40 MSK). `evening_observations.kind=gratitude`. |
| 8 | Второй человек 2 дня подряд | **не делали** | Остаётся до полного ship gate. |

Canon opened: `today/TODAY_PRODUCT_FLOW_V1.md` §4 · `today/TODAY_DISPLAY_INVENTORY_V1.md` v1.3 `T1.continuity`.

---

## Behavior test *(BLOCKED until ship gate DoD)*

| | |
|---|---|
| **Когорта** | 5–10 реальных людей |
| **Длительность** | 14 дней |
| **Day 14 question** | *«Что вы начали делать благодаря TodayFlow, чего раньше не делали?»* |

**Candidate behavior** *(hypothesis, not canon)*: один фокус → доведён до конца **чаще**.

**AR freeze:** [TODAYFLOW_PRODUCT_CANON_UNIFIED.md](../TODAYFLOW_PRODUCT_CANON_UNIFIED.md) §6.

---

## DoD — ship gate passed

- [ ] Новый пользователь: landing → demo → signup → onboarding → **полный** today *(2026-09-18: landing → invite → welcome → First Today → save form OK; magic-link claim не закрыт в UI)*
- [x] Утром зафиксирован **main focus** *(walkthrough run 2; live 2026-09-18 authenticated Today shows thesis)*
- [x] Вечером: **благодарность** persist (`evening_completed` + `kind=gratitude`) · не 3-way outcome *(run 2 был Close Day — dead; live 2026-09-18 = Playwright clock + API D−1 seed)*
- [x] После вечера: **tomorrow hook** / `T1.continuity` виден *(run 2 localStorage; **календарный D+1 2026-09-18 = GET yesterday, no route mock**)*
- [x] На следующее утро: **continuity line** *(календарный D+1 2026-09-18 на `todayflow.today`)*
- [ ] Команда прошла путь сама 2 дня подряд без legacy scroll-trap

→ разблокировать behavior test · **остановиться** на новых фичах до day-14 интервью.
