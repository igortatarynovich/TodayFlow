# Web Launch — Product Blueprint (Stage 0)

**Статус:** **LAUNCH SCOPE FROZEN** (2026-07-01) — execution only.  
**Дата:** 2026-07-01  

---

## Launch Scope Freeze *(ACTIVE)*

**Не до launch v1 — не обсуждаем и не расширяем:**

- Personal Model, Projection-first, PIM, Product Model, философия
- Новые категории, новые product-документы, фундаментальные концепции

**Правило новых идей:** нужна для **launch v1** или это **v2 backlog**?  
v2 → одна строка в трекер, **не обсуждаем**.

**Следующие шаги (только это):**

1. **Story brief + React** — экран за экраном (§Execution Plan · Launch Story Script)  
2. **Story gate** — продолжает историю или прерывает?  
3. **Story walkthrough** — весь path в React  
4. **Поле** — 10 пользователей × поведение  
5. **v2** — только после метрик

**Самая дорогая ошибка сейчас:** не запуститься, бесконечно улучшая модель.

---

**Stage 0 закрыт.** Отвечает на: *что пользователь видит, чувствует, делает на каждом экране launch path.*

**План работ (код, gaps):** [WEB_LAUNCH_EXECUTION_PLAN.md](./WEB_LAUNCH_EXECUTION_PLAN.md) — DoD · gaps · Decision Log.

**Что строить (product SoT):** [TODAYFLOW_PRODUCT_BUILD_MAP.md](../TODAYFLOW_PRODUCT_BUILD_MAP.md) — Axis A · Axis B · Design Tokens.

**UI-детали (reference):** этот Blueprint.

**Фундамент (frozen до v2):** [TODAYFLOW_PRODUCT_MODEL.md](../TODAYFLOW_PRODUCT_MODEL.md) §4.

> TodayFlow — персональный ежедневный ориентир, который **помнит, что было вчера**.

**Принцип (внутренний):**

> Не объяснять. Давать **исследовать себя**. Главное — сверху; игровые и исследовательские блоки — ниже.

**Порядок ценности:**

`Любопытство → быстрая награда → исследование → сохранение → возврат завтра → совместимость → история → глубина`

**Критерий успеха launch:**

> Пользователь **сам** открывает приложение на следующий день. Причина — Today, карта/число, или «вчера сохранилось».

**Процесс (frozen — docs complete):**

1. ~~Blueprint / Product Model / Execution Plan~~ — **done**  
2. **React** — story brief → build → story gate, экран за экраном  
3. **Story walkthrough** E2E → **Launch Freeze** уже ON  
4. **Launch DoD** (11 criteria)  
5. **User test** 10 users → метрики  
6. **Анализ** → v2

**Launch Story Script · DoD · Decision Log:** [WEB_LAUNCH_EXECUTION_PLAN.md](./WEB_LAUNCH_EXECUTION_PLAN.md)

**Supersedes для web launch** *(не удалять архивные каноны, но не строить launch по ним):*

| Документ | Что устарело для launch |
|----------|-------------------------|
| [FIRST_DAY_EXPERIENCE.md](../FIRST_DAY_EXPERIENCE.md) §1 | `/demo/today` как guest value; auth-first |
| [FIRST_DAY_EXPERIENCE.md](../FIRST_DAY_EXPERIENCE.md) §2 | маршрут `Landing → Demo → Signup` |
| [BEHAVIOR_CHANGE_TEST_V0.md](./BEHAVIOR_CHANGE_TEST_V0.md) ship gate row | «Demo» в минимальном пути |
| [PRODUCT_EXECUTION_TRACKER.md](../PRODUCT_EXECUTION_TRACKER.md) P0.1 | «DONE demo today» — **reverse для launch** |

**Сохраняет силу:** [EXPLAIN_MEANING_NOT_MECHANISM.md](../EXPLAIN_MEANING_NOT_MECHANISM.md), [MARKET_ATTENTION_AND_SCREEN_JOBS.md](../MARKET_ATTENTION_AND_SCREEN_JOBS.md) (совместимость = L1), evening/continuity intent в [BEHAVIOR_CHANGE_TEST_V0.md](./BEHAVIOR_CHANGE_TEST_V0.md).

---

## Retention hooks по дням

| День | Крючок | Job продукта |
|------|--------|--------------|
| **1** | «Интересно, что TodayFlow скажет **обо мне**?» | Быстрый личный результат |
| **2** | «**Вчера не исчезло.** Приложение помнит.» | Связь вчера → сегодня |
| **3–7** | «Можно копнуть: совместимость, профиль, слои» | Исследовательские механики |
| **10+** | «У меня уже история, люди, повторения» | Привычка + личный актив |

---

## 1. Landing

### Цель (5 секунд)

**Почувствовать:** curiosity — «интересно, что **сегодня для меня**».

**Не:** понять продукт, прочитать features, увидеть demo-ответ.

### Почему нажмёт CTA

Не потому что «бесплатно» или «регистрация».  
Потому что хочет **свой** Today — с картой, числом, настроением и **памятью о вчера** (обещание на будущее, не proof сейчас).

### Layout — блок за блоком

#### Block A · Hero (above fold, ~80vh mobile)

| Пиксель / зона | Содержание | Зачем | Если убрать |
|----------------|------------|-------|-------------|
| Top | Logo TodayFlow | Узнаваемость | − brand trust |
| H1 | **Интересно, что сегодня для тебя?** | Curiosity hook | − причина остаться |
| Sub | Персональный ориентир на день — с картой, числом, настроением, рекомендациями и **памятью о вчера** | Язык рынка (гороскоп/таро/GPT) + отличие | − непонятно чем не ChatGPT |
| Primary CTA | **Создать мой Today** | Действие, не «signup» | − conversion |
| Secondary | Уже есть аккаунт → Войти | Returning users | − friction для old users |
| **Нет** | Demo, «Как это работает», feature grid, «Начать бесплатно» | — | + шум, − curiosity |

**Feel:** спокойно, тепло, не «SaaS 2010», не «астро-шум».

#### Block B · Product vitrine (scroll 1)

Статичные **превью UI** (не live demo, не fake «сегодня»):

| # | Card | Preview copy | Зачем | Если убрать |
|---|------|--------------|-------|-------------|
| 1 | Today | «Сегодня стоит обратить внимание на…» | Главный продукт | − не видят payoff |
| 2 | Карта дня | «Твоя карта на сегодня…» | Рыночный спрос | − «ещё один гороскоп без таро» |
| 3 | Число дня | «Энергия дня…» | Нумерология audience | − теряем сегмент |
| 4 | Вечер | «Что получилось сегодня?» | Retention mechanic visible | − не понятно зачем вечер |
| 5 | Завтра | «Вчера главным было…» | **Moat в одной карточке** | − теряем отличие от GPT |
| 6 | Совместимость | «Добавь человека — посмотри динамику» | L1 hook, share | − теряем viral |

Подпись под витриной (1 строка): *Не общий гороскоп. Твой день — с памятью о вчера.*

#### Block C · Footer CTA

| | |
|---|---|
| H2 | Завтра утром ты увидишь, как прошёл сегодня |
| CTA | **Создать мой Today** (same as hero) |

### Landing — success metric

≥40% scroll to vitrine; CTA click rate — baseline after field test.

---

## 2. Первый запуск (value-first onboarding)

**Правило:** registration **после** первой награды. Разговор, не форма.

### 0–10 сек · Экран «Имя»

| | |
|---|---|
| **See** | «Как к тебе обращаться?» + поле Имя |
| **Feel** | Меня спрашивают, не регистрируют |
| **Do** | Ввести имя → **Продолжить** |
| **Reward** | Ещё нет — только тон «диалог» |

### 10–30 сек · Экран «Дата рождения»

| | |
|---|---|
| **See** | «Когда ты родился?» · день / месяц / год |
| **Feel** | Ожидание награды близко |
| **Do** | Выбрать дату → **Показать первый результат** |

### 30–60 сек · Экран «Первый результат» ★ первая награда

| | |
|---|---|
| **See** | «{Имя}, уже можно собрать первый Today.» · Знак · Число пути (1 строка) · Короткий личный текст (2–3 строки) · Mini preview Today · «Чтобы карта была точнее — место и время» |
| **Feel** | **«Это про меня»** — первый dopamine |
| **Do** | Primary: **Уточнить карту** · Secondary: **Пропустить и открыть Today** |
| **Reward** | Личный результат **до** email |

**Первый «хочу дальше»:** здесь.

### 60–120 сек · Место рождения (optional path)

| | |
|---|---|
| **See** | «Где ты родился?» · autocomplete · «Помогает точнее рассчитать карту» |
| **Do** | **Продолжить** |

### 120–150 сек · Время рождения (optional)

| | |
|---|---|
| **See** | «Во сколько ты родился?» · «Не знаю — добавить позже» |
| **Do** | **Завершить карту** |

### 150–180 сек · Сохранение ★ второй commit moment

| | |
|---|---|
| **See** | «Хочешь сохранить карту и возвращаться каждый день?» · Email only (no password v1 — magic link / follow-up) |
| **Feel** | Сохраняю **уже полученное**, не покупаю кота в мешке |
| **Do** | **Сохранить мой Today** |
| **After** | Account created → First Today |

**Intent / Reality chips:** перенести **после** first result preview или **внутрь** First Today — **story gate** на onboarding (не блокировать launch).

---

## 3. First Today

**Цель:** полноценный первый опыт за **< 2 мин** до понимания главного; исследование — opt-in scroll.

**Иерархия:** один главный блок доминирует визуально (60%+ attention). Остальное — «Исследовать день глубже».

### Block · Главный ориентир (TOP — hero card)

| | |
|---|---|
| **See** | Дата · «{Имя},» · Настрой дня (1 строка) · **На что обратить внимание** (2–3 строки max) · **Главный шаг / фокус** (1 actionable line) |
| **Feel** | Личное сообщение утром, не статья |
| **Why on top** | Единственный ответ на «что сегодня для меня» |
| **Without block** | Нет продукта |

### Block · Карта дня

| | |
|---|---|
| **See** | Визуал карты + название + 2 строки значения **для тебя сегодня** |
| **Feel** | Ритуал, красота, «моя карта» |
| **Emotion** | Curiosity + узнавание |
| **Why exists** | Рыночный спрос; shareable; отличие от plain text GPT |
| **Rule** | Collapsed или compact по default; expand «Подробнее» |
| **Without** | − сегмент tarot-audience; − visual hook |

### Block · Число дня

| | |
|---|---|
| **See** | Число + «энергия дня» (1–2 строки) |
| **Feel** | Быстрый numerology hit |
| **Why exists** | Второй привычный формат рынка; дополняет карту |
| **Rule** | Не конкурирует с главным — меньший visual weight |
| **Without** | − numerology segment |

### Block · Настроение дня

| | |
|---|---|
| **See** | «Как может ощущаться день» — 1 строка + optional emoji-free tone word |
| **Feel** | Validation |
| **Why exists** | Bridge между «астро» и «про меня сегодня» |
| **Without** | − emotional hook для sensitive users |

### Block · Что делать

| | |
|---|---|
| **See** | 1–3 коротких пункта «поддержит сегодня» |
| **Feel** | Практичность без todo-app |
| **Why exists** | Ответ на «что мне делать» (рыночный запрос) |
| **Rule** | Subordinate to главный фокус — не второй план на день |
| **Without** | − practical users bounce to ChatGPT |

### Block · Чего избегать

| | |
|---|---|
| **See** | 1–2 пункта «лучше не сегодня» |
| **Feel** | Забота, не запрет |
| **Why exists** | Рынок спрашивает «что не делать»; снижает impulsive mistakes |
| **Without** | − half of horoscope expectation |

### Block · Рекомендации / цели

| | |
|---|---|
| **See** | Связь с intent chip: «Если фокус — X, сегодня…» |
| **Feel** | Персонализация |
| **Why exists** | Intent onboarding payoff visible |
| **Rule** | **Day 1:** один блок max; не goal tracker |
| **Without** | − связь onboarding → Today |

### Block · Символ / астрологический слой

| | |
|---|---|
| **See** | Луна / транзит / «небо сегодня» — collapsed «Для любопытных» |
| **Feel** | Глубина для astro-native |
| **Why exists** | Credibility для astro audience |
| **Rule** | **Never above** главный ориентир |
| **Without** | − astro credibility (acceptable for launch test) |

### Block · Закрыть день (sticky / evening CTA)

| | |
|---|---|
| **See** | «Вечером вернись — завтра увидишь, как прошёл сегодня» + **Закрыть день** |
| **Feel** | Причина вернуться |
| **Why** | Seeds D2 hook |
| **Without** | **No retention — critical** |

### First Today — NOT on screen

- Profile CTA «Открыть карту личности»
- «Три сферы дня» как равные карточки
- Why / PIM / «алгоритм»
- Demo disclaimer

---

## 4. Вечер (Evening close)

**Недооценённый экран. Job:** не «завершить UI» — **создать причину открыть завтра**.

### Entry

| | |
|---|---|
| **When** | User taps «Закрыть день» или evening prompt |
| **Feel** | 30 сек, не homework |

### Screen · Close

| | |
|---|---|
| **See** | «Как прошёл сегодняшний **главный фокус**?» · repeat focus line · **Получилось / Частично / Не получилось** · optional «Что помогло или помешало?» |
| **Do** | Select outcome → **Сохранить день** |

### Screen · Confirmed ★ key copy

| | |
|---|---|
| **See** | «День сохранён. **Завтра утром TodayFlow начнёт с того, что было сегодня.**» |
| **Feel** | Завершённость + anticipation |
| **Do** | Leave app (no profile push) |

### Evening — success

User can articulate: «Завтра увижу сегодняшнее».

---

## 5. День 2+

### Что меняется

| | Day 1 | Day 2+ |
|---|-------|--------|
| Continuity | Promise only | **Delivered** |
| Blocks | Same hierarchy | Same + continuity on top |
| Ritual | Full exploration available | Continuity **before** new content |

### Первое, что видит (above everything)

> **Вчера главным было:** «…» · **Итог:** частично. · **Сегодня продолжим отсюда.**

| | |
|---|---|
| **Feel** | «Вчера не исчезло» — **product moat** |
| **Why first** | If buried — indistinguishable from horoscope app |
| **If yesterday not closed** | Soft: «Вчера не закрыт — хочешь отметить итог?» (not guilt) |

Then: новый Today → карта → число → … (same hierarchy as Day 1).

---

## 6. Profile

### Зачем человек сюда заходит (NOT «посмотреть натальную карту»)

| Мoment | Job |
|--------|-----|
| D3–7 | «Что накопилось? Кто я в системе? Есть ли люди?» |
| D10+ | «Моя история + карта + совместимости в одном месте» |

**Profile ≠ first payoff. Profile = accumulated value.**

### Structure

#### Top · Identity strip

Имя · знак · число пути · 1 строка характера.

#### «Мои дни» ★ launch differentiator

- N дней с TodayFlow  
- Last 3–7: дата · фокус · исход  
- Repeat hint when data exists: «Третий раз за неделю переносишь после обеда» *(later)*

**Why:** shows artifact growing; reason to keep opening.

#### «Моя карта» (teaser)

Солнце · Луна · Асцендент — 2 строки each → **Развернуть карту**

#### «Совместимости»

Saved people · quick add · last check preview

#### «Глубокие слои» (collapsed)

Full natal · numerology · patterns · history

### Profile — NOT

- 40-screen natal on first visit  
- Blocking onboarding  
- Primary nav highlight before D3

---

## 7. Compatibility

**Два уровня** (Product Model §5.4): **Public** — standalone; **Personal** — через Model внутри TF.

**Живёт по другим законам.** L1 market attention (~40–50%). See [MARKET_ATTENTION_AND_SCREEN_JOBS.md](../MARKET_ATTENTION_AND_SCREEN_JOBS.md).

### Public Compatibility *(standalone — не ломать)*

- Работает **без** аккаунта и **без** Today path  
- Acquisition: Google «Leo Scorpio compatibility», share, TikTok  
- Две даты → инсайты, %, рекомендации — **полная ценность снаружи**

### Personal Compatibility *(inside TodayFlow — E3 hook)*

- «Рассчитано через **твою** модель» — особенности, история, save person  
- Hook **после** Today payoff; не блокирует launch story

### Почему открывают

«Подходим ли?» · «Почему так между нами?» · «Стоит ли писать?»

### Когда показываем hook

| Trigger | Placement |
|---------|-----------|
| After First Today scroll | Card: «Хочешь проверить совместимость с кем-то?» |
| Day 2 | Nav or Today footer |
| After email save | Optional interstitial |

**Not:** first screen before Today payoff.

### Flow (minimal)

1. Имя человека  
2. Дата рождения  
3. (optional) место / время  
4. **Проверить совместимость**  
5. Result: emotional hook + 3 bullets + save to profile  
6. Share CTA (later)

### After compatibility

Return to Today OR save person in Profile — **never dead end**.

---

## Epic backlog *(FROZEN — единственный launch scope)*

| Epic | Scope | Stories |
|------|-------|---------|
| **E1 · Первый опыт** | Acquisition → first value | Landing · Onboarding · First Today |
| **E2 · Daily Loop** | Retention core | Evening · Day 2 · Continuity first |
| **E3 · Hook** | Viral / depth | Compatibility (minimal) |
| **E4 · Profile** | Launch-minimum | Identity + «Мои дни» teaser · не deep chart first |

**Порядок реализации:** E1 → E2 → E3 → E4.  
**PRs** — story brief → React → story gate ✅. **Никаких новых сущностей** в launch.

### Launch path *(story walkthrough в React)*

```
Landing → Onboarding → First Today → Evening → Day 2 → Compatibility → Profile
```

Критерий: **одна непрерывная история**, не «разные приложения».

### Field metrics *(10 users × 7 days — behavior, not opinions)*

| Metric | Question |
|--------|----------|
| Landing → Start | Конверсия CTA |
| Start → Today | Дошёл до первого Today |
| D1 → D2 | Voluntary return |
| D2 → D3 | Loop holds |
| Evening close rate | Закрывают ли день |
| Compatibility open | Открыли hook |
| Unprompted return | Вернулись сами (no push) |

**Gate для v2:** метрики поля reviewed → только тогда новый продуктовый цикл.

---

## Doc cleanup checklist (before implementation)

- [ ] [FIRST_DAY_EXPERIENCE.md](../FIRST_DAY_EXPERIENCE.md) — пометка §1–2 **superseded by Blueprint** для web launch; новый маршрут
- [ ] [BEHAVIOR_CHANGE_TEST_V0.md](./BEHAVIOR_CHANGE_TEST_V0.md) — убрать Demo из ship gate path
- [ ] [PRODUCT_EXECUTION_TRACKER.md](../PRODUCT_EXECUTION_TRACKER.md) — Stage 0 + Epic E1; P0.1 demo → **REVERSE for launch**
- [ ] [CORE_PRODUCT_CANON.md](../CORE_PRODUCT_CANON.md) §8 guest — align or footnote Blueprint
- [ ] [TODAY_CANON_VS_CODE_DIFF.md](./TODAY_CANON_VS_CODE_DIFF.md) — launch diff в Execution Plan

---

## Internal review gate (story walkthrough)

**Participants:** Product (story editor) + Eng.

**Walkthrough script — один вопрос на экран:**

> Этот экран **продолжает** историю или **прерывает**?

**Pass:** unanimous «я бы открыл завтра» + сквозная история из Execution Plan §Launch Story Script.

**Fail:** переделать в React. Не polish ради polish.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-01 | No Figma; story-first React process |
