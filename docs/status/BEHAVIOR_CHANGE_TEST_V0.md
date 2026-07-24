# Minimum Day Cycle + Behavior Test (operational, not canon)

**Дата:** 2026-06-23  
**Статус:** **IN_PROGRESS** — ship gate **до** первых 5–10 людей · behavior test **BLOCKED**  
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

**Дата D (сегодня):** __________ · **аккаунт (email):** __________ · **кто проходил:** __________

| # | Шаг | OK / BROKEN | Заметка |
|---|-----|-------------|---------|
| 1 | `/` → «Начать бесплатно» | | |
| 2 | `/auth?mode=signup` — регистрация **в UI** | | |
| 3 | `/onboarding/core` — имя, дата, место, submit | | |
| 4 | `/onboarding/intent` — выбор chip | | |
| 5 | `/onboarding/reality` — выбор chip → **`/today`** (не `?first=1`) | | |
| 6 | Ritual → S5 → **main focus** зафиксирован | | |
| 7 | «Закрыть день» → outcome + note → **day_closed** | | |
| 8 | Tomorrow hook на экране закрытия | | |

**Дата D+1 (завтра, тот же аккаунт):**

| # | Шаг | OK / BROKEN | Заметка |
|---|-----|-------------|---------|
| 9 | `/today` → S0 **continuity line** *(без ручного localStorage)* | | |
| 10 | Фокус дня + закрытие второго дня | | |

**Run 3 — второй человек:** повторить D + D+1 · имя: __________

---

## Behavior test *(BLOCKED until ship gate DoD)*

| | |
|---|---|
| **Когорта** | 5–10 реальных людей |
| **Длительность** | 14 дней |
| **Day 14 question** | *«Что вы начали делать благодаря TodayFlow, чего раньше не делали?»* |

**Candidate behavior** *(hypothesis, not canon)*: один фокус → доведён до конца **чаще**.

**AR freeze:** [PIM_PRODUCT_NORTH_STAR.md](../archive/PIM_PRODUCT_NORTH_STAR.md) §0.2.

---

## DoD — ship gate passed

- [ ] Новый пользователь: landing → demo → signup → onboarding → **полный** today *(UI signup/onboarding не пройдены целиком)*
- [x] Утром зафиксирован **main focus** *(walkthrough run 2)*
- [x] Вечером: outcome 3-way + один ответ «помогло/помешало» · **ощущение закрытия** *(run 2)*
- [x] После вечера: **tomorrow hook** виден *(run 2)*
- [ ] На следующее утро: **continuity line** *(механизм OK run 2 · **календарный D+1 после close — pending**)*
- [ ] Команда прошла путь сама 2 дня подряд без legacy scroll-trap

→ разблокировать behavior test · **остановиться** на новых фичах до day-14 интервью.
