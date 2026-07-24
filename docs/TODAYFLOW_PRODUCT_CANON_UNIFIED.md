# TodayFlow — Product Canon (Unified v1.8)

**Дата:** 2026-07-24
**Статус:** предлагаемая замена для четырёх документов, которые одновременно называли себя главными:
`CORE_PRODUCT_CANON.md` (21.07) · `TODAYFLOW_PRODUCT_MODEL.md` (02.07, v0.4.9) · `TODAYFLOW_PRODUCT_BUILD_MAP.md` (03.07, философская часть) · `PIM_PRODUCT_NORTH_STAR.md` (23.06).

**Что НЕ вошло сюда и почему:**

| Документ | Почему остаётся отдельно |
|---|---|
| `TODAY_PRODUCT_MODEL.md` | Уровень **экрана** Today (Today Package, воронка сборки), не всего продукта — верно ограничен по scope, менять не нужно |
| `PROFILE_SCREEN_MASTER.md` | Уровень **UI** Profile — так же верно ограничен |
| `TODAYFLOW_PRODUCT_BUILD_MAP.md` (Entity Catalog / build order) | Это **рабочий трекер** сущностей и порядка сборки — меняется еженедельно; философская часть (6-шаговый закон, Entity Rules, Design Tokens) перенесена сюда в §5, а сам файл остаётся **только** живым списком entity + build order, без претензии быть «главным документом продукта» |
| `audits/FULL_USER_PATH_CANON_V1.md` | Уже единственный SoT пути пользователя (22.07) — этот канон **ссылается** на него, не дублирует |

**Правило на будущее:** после принятия этого документа — четыре старых файла помечаются `SUPERSEDED → TODAYFLOW_PRODUCT_CANON_UNIFIED.md` первой строкой и переносятся в `docs/archive/` (см. Cleanup Report). Новый «принцип продукта» пишется **только** сюда.

---

## 0. Один абзац

TodayFlow — не набор эзотерических инструментов, а система, которая строит и непрерывно развивает **Personal Model** человека и через неё принимает все персональные решения в продукте. Внешнее обещание рынку: персональный ежедневный ориентир, который **помнит, что было вчера**. Ядро — Personal Core (имя, дата/время/место рождения) → **Profile** (личная карта: натал, нумерология, архетипы, сферы жизни) → каждый день собирается **Today** (что важно, чего избегать, один шаг) через объективный контекст дня + персональный слой, поданный LLM-нарративом.

---

## 1. Терминология (обязательно, не путать в разговорах)

| Термин | Что это | Не путать с |
|---|---|---|
| **Personal Model** | Главная продуктовая сущность — живое цифровое представление человека, единственный SoT персонализации. Рабочее имя, финальный термин — open review | «Profile» как SoT — Profile это лишь UI-проекция |
| **Profile** (экран) | UI-проекция Personal Model — вкладка «Профиль» | Personal Model целиком |
| **Projection** | Экран/flow, который читает Personal Model, пишет обратно, делает модель понятнее пользователю | «раздел приложения» |
| **PIM** | Инфраструктура обновления Personal Model (Knowledge Atoms, Learning Δ) — невидима пользователю | UI-функция |
| **Experience** | Конкретный UI/сессия на projection (First Today, evening close) | Projection целиком |
| **Maps** | Живая накопительная история жизни — вторая половина **продукта** (UI: `/maps/*`, не Profile scroll; §3.4.1) | «трекер» / «статистика» · «вторая половина Profile» |

**Запрет user-facing слов:** трекер, статистика, completion rate, «алгоритм нашёл» → карта, история, наблюдение.

---

## 2. Personal Model

> Цифровое представление человека внутри TodayFlow, которое непрерывно развивается вместе с ним — и через которое TodayFlow принимает все персональные решения.

Не анкета, не натальная карта, не экран. Модель **не вычисляется раз в день — она живёт**: растёт с каждым осмысленным взаимодействием, обогащается новыми днями/людьми/выборами, уточняется, иногда пересматривает старые выводы (contradiction, не догма).

**Инварианты:**
- никогда не «завершена» — нет «100% profile complete» как финала;
- единственный источник истины — Today, Compatibility и другие модули ничего не «знают» сами, знает только Personal Model.

---

## 3. Product map (карта продукта — единая версия)

### 3.1 Что пользователь хочет сделать (JTBD)

| JTBD | Куда ведёт |
|---|---|
| Узнать сегодняшний день | **Today** |
| Понять себя | **Profile** |
| Посмотреть совместимость | **Compatibility** |
| Получить ответ на вопрос | **Tarot** |
| Изменить жизнь регулярными действиями | **Growth** (и зоны Today: Practice · Goals · Tracking) |

4 обязательных top-level JTBD: понять себя · понять другого человека · принять решение · понять что делать сегодня. Каждая крупная поверхность/route/API должна отвечать хотя бы одному.

**Question-first без явного вопроса:** пользователь не обязан печатать вопрос — система выводит вероятный JTBD из точки входа, экрана, действия и контекста, собирает ответ через общий Personal Model, возвращает один цельный ответ + одно предложение углубиться. Явный ввод вопроса — опционален, implicit-распознавание — обязательно.

### 3.2 Карта экосистемы

| Слой | Что входит | Примечание |
|---|---|---|
| **Ядро** | Today · Profile | Ежедневный вход + «кто я» |
| **Standalone** | Compatibility · Tarot · Growth | Самостоятельная ценность + сильнее с Model |
| **Сервисы** | Journal · Saved people · Notifications · Calendar · Settings · History | Инфраструктура опыта, не «продукт» |

**Growth** = practices · asceticisms · habits · trackers · meditations · affirmations · quests · goals · streaks — один человеческий вопрос: *что я могу делать регулярно, чтобы изменить жизнь*. Не отдельный пункт top-level меню на launch — вход из Today/Profile/Tarot.

**Правило UI:** пользователь не видит дисциплин (астрология/нумерология/психология/PIM/DayModel как primary framing) — только ответы на человеческие вопросы. Natal + numerology = доказательная база, не витрина.

### 3.3 Today (daily dashboard)

Не «астро-экран» и не линейный сценарий — ежедневный дашборд (аналог Apple Health для дня): много виджетов, один вопрос. Hero за ~10 сек — дальше исследование по желанию.

| Zone | Содержание | Launch v1 |
|---|---|---|
| 1 · Overview | Hero · тема дня · energy · фокус | ✅ core |
| 2 · Guidance | что делать · чего избегать | ✅ do/don't |
| 3 · Daily Symbols | карта · число · символ… | ✅ card+number, остальное 🟡 |
| 4 · Practice | одна рекомендованная практика | 🟡 one rec |
| 5 · Goals | цель дня | 🟡 optional |
| 6 · Tracking | привычки · цикл · mood | v2+ |
| 7 · Evening | закрытие дня → завтра | ✅ core |

### 3.4 Profile (карта человека)

Экран Profile отвечает на один вопрос — **«кто я»** (почти не меняется):

| Слой | Содержание |
|---|---|
| **Кто я** | Portrait · natal · numerology · циклы · сильные/слабые · отношения · деньги · предназначение |

Maps на Profile **не** вторая половина скролла — вынесены (см. §3.4.1); на экране допустима только тонкая CTA / seed preview.

North star: устойчивый портрет человека, не CRM и не натальная стена. Launch v1: identity strip + тонкая CTA/MapsPreview seed + свёрнутые deep-слои. Живая история («как меняется моя жизнь») — на Maps surfaces.

### 3.4.1 IA-уточнение: где живёт UI Maps *(PR-4 supersede, 2026-07-21)*

Personal Model — общий SoT для Profile и Maps, но **UI-дом разный**:

| Проекция | Где | Роль |
|---|---|---|
| **Profile screen** | `/profile` | «Кто я» — портрет, натал, нумерология, сферы жизни. Maps — только тонкая CTA/seed preview (`ProfileMapsPreviewBlock`), не вторая половина скролла |
| **Maps surfaces** | `/maps/*`, `/tracking/*` | «Как меняется моя жизнь» — накопительная история из действий Today/Evening |

Формулировка «Maps как вторая половина Profile» — устаревшая версия до PR-4, не текущий IA. Источник истины по Maps IA — `docs/profile/PROFILE_SCREEN_MASTER.md` §7.

### 3.5 Compatibility, Tarot, Growth — коротко

- **Compatibility**: «Кто мы друг для друга» — библиотека, не один калькулятор. Public L1 (две даты → инсайты) standalone; Personal L2 через Model. Launch: Public L1 + Personal hook; полная библиотека типов — v2+.
- **Tarot**: живой ритуал (вопрос → расклад → карты → расшифровка → связь с тобой → действие), не «выберите карту». Launch: card-of-day в Today + существующие spreads; question-first flow — v2+.
- **Growth**: не mega-nav, а teaser/рекомендация из Today (zone 4) + существующие routes (`/practices`, `/habits`, `/asceticisms`, `/affirmations`).

### 3.6 Maps — вторая половина продукта *(не вторая половина Profile)*

Today отвечает «что сегодня», Maps отвечают «каким становится моя жизнь». UI-дом — `/maps/*` · `/tracking/*` (см. §3.4.1), не вложенный скролл Profile. Не Journey, не «раздел трекеров» — живая история (аналог Spotify Wrapped/GitHub graph/Strava year), которая рисуется сама. Язык — истории и наблюдения, не статистика и проценты (например: «май стал самым спокойным месяцем», а не «среднее настроение 7.4»). Каталог карт (Mood/Energy/Habit/Ascetic/Goal/Wish/Relationship/Tarot/Theme/Symbol) — живой список, ведётся в Build Map (Entity Catalog), не дублируется здесь.

---

## 4. Законы (обязательные контракты для любой projection)

1. **Read/write** — любая projection обязана явно ответить: что читает из Personal Model, что пишет обратно. Читает и пишет → core, строим. Только читает или только пишет → подозрительно, разобраться. Ни то ни другое → не core (SEO/catalog/admin).
2. **Standalone value** — каждая крупная projection: (а) может существовать как отдельный продукт без аккаунта/Today; (б) становится заметно ценнее внутри TodayFlow через Personal Model. Оба теста обязательны. Маршруты `/compatibility`, `/tarot`, `/numerology`, `/horoscope` — не удалять из-за этого закона; персональный слой добавляет, не заменяет публичный.
3. **Непрерывность** — Personal Model никогда не сбрасывается (новый телефон, переустановка, редизайн UI — модель продолжается, не «день ноль»).
4. **Ясность** — любой Experience обязан делать Personal Model понятнее пользователю. Тест: после сессии человек может сказать «я понял что-то о себе» / «это помнит меня», а не «мне выдали текст».
5. **Двойная ценность** — каждое значимое действие даёт ценность сейчас (Today/Tarot/Compatibility/Portrait) и +1 к будущей Map (накопительная ценность).

---

## 5. Как строится продукт (перенесено из Build Map, философская часть)

**Главный закон (6 шагов, всегда в этом порядке):** question → entity → sources → projections → tokens → React.

**Entity Rules:**

| # | Правило |
|---|---|
| E1 | Сущность именуется по смыслу, не по UI (`DailyTheme`, не `ThemeCard`) |
| E2 | Экран не владеет — только **uses** entity + tokens |
| E3 | Один Entity ID — один смысл навсегда |
| E4 | Новая проекция = та же entity + другие tokens, не новый ID |
| E5 | React PR только если entity 🟢 в каталоге |
| E6 | UI на экране только из каталога — нет orphan-блоков |
| E7 | Deprecate entity → пометка в каталоге, не `DailyThemeV2` |
| E10 | Projection читает Snapshot/CUM, не пересобирает личность заново |

**Design tokens (продуктовые, не CSS):** Size (XS–XL) · Priority (Hero/Primary/Secondary/Supporting/Decorative) · Reveal (Always/Collapsed/Expandable/Premium/Unlocked) · Behavior (Interactive/Static/Selectable/Swipeable/Dismissible).

**Живой список entity + порядок сборки** — ведётся в `TODAYFLOW_PRODUCT_BUILD_MAP.md` (теперь это чистый рабочий трекер, не документ «что такое продукт»).

---

## 6. Критерий успеха (North Star)

**Experience North Star (не путать с Learning North Star ниже):**

> Что пользователь получает вечером такого, чего не получил бы без TodayFlow?

Причинность строго в одну сторону: **daily usefulness → retention → data**. Обратное не работает — можно собрать данные без продукта, можно сделать липкий ритуал без ценности (streak без результата). Retention — индикатор, не цель.

**Learning / Platform North Star:**

> Завершённый день должен увеличивать ценность Personal Model (PIM). `Learning Δ > 0` за цикл → платформа выросла.

**Три контура, не путать:**

| Контур | Вопрос |
|---|---|
| Experience | Полезнее пользователю сегодня? |
| Поведение | Retention — индикатор (D1/D7/завершённые дни ≥5 за 14 дней) |
| Platform/Learning | Learning Δ > 0? |

**PIM ROI-тест для нового сценария:** что получает пользователь? что получает PIM (signal/evidence/contradiction)? стоит ли знание стоимости реализации? Красивая анимация карты = высокий Experience, низкий PIM ROI → низкий приоритет. Intent Record + outcome = может выглядеть скучно, но высокий PIM ROI → приоритет.

---

## 7. Монетизация — гипотеза цены; рынок и процессинг — FROZEN 2026-07-24

### 7.1 Рынок · язык · процессинг *(FROZEN)*

| Решение | Значение |
|---|---|
| **Целевой рынок** | США и Европа. РФ как рынок **не рассматривается**. |
| **Язык продукта (v1)** | **Русский** — рабочий и user-facing язык (команде так удобнее; аудитория русскоязычная в US/EU / диаспора). EN — отдельная волна i18n, не блокер soft launch. |
| **Платежи** | **Stripe** (карты US/EU). Российский эквайринг не нужен. |
| **Валюта тарифов в UI** | **$/€** (не ₽). Конкретные цифры — по-прежнему гипотеза до поля. |

Следствие: старые ₽ в `pricing/page.tsx` — ошибка позиционирования, не «локализация». Draft-экран должен показывать $/€ placeholders.

### 7.2 Цена и paywall — всё ещё гипотеза

**Важно:** цифры в UI — **пример**, не зафиксированное решение. Цену рано фиксировать до поля.

**Формула (проверить в поле):** сегодня → польза · каждый день → больше · неделя → закономерности · месяц → карта жизни · год → share. Продаём **непрерывность истории**, не «Premium/Pro».

**Paywall trigger** — не календарный триггер («8 дней»), а триггер по полноте истории после первого ощутимого результата (гипотеза, калибровать в поле): 5–6 закрытых дней, 5 заполненных Today, 3 карты таро, 4 совместимости, 3 практики.

**Week 1 Wrapped** — маленький красивый чеклист фактов + одна мысль («чаще завершал день спокойнее»), CTA «Продолжить» как достижение, не «trial ended».

**Anti-pattern** — не блюрить то, что уже показали; показать полностью → «следующая карта начнёт строиться завтра».

**Freemium (гипотеза):** Free — Today lite · Compatibility · 1 taro · Profile базовый. Paid — полный Today · Maps · история · practices · full Tarot · Wrapped.

**Pricing amounts:** не фиксировать до поля. Зависит от дизайна, Week 1 Report, D7 retention. A/B нескольких точек в **USD/EUR** после первых пользователей.

**Явное правило для launch:** монетизация — **не блокер** DoD запуска v1. Paywall + цена — отдельная волна. Checkout на Stripe можно подключать в wave 2; до этого `/pricing` остаётся draft в marketing shell.

---

## 8. Путь пользователя — не дублируется, только ссылка

Единственный источник истины — `audits/FULL_USER_PATH_CANON_V1.md` (22.07, самый свежий). Он же — единственное место, где живёт диаграмма Landing→Preview→Save→Claim→Profile→Today.

**Резолюция конфликта:** старая версия этого канона (в `CORE_PRODUCT_CANON.md` §8.2, со ссылкой на контракт от 23.06) описывала другой порядок — signup до birth-данных, Today до Profile («Today first, Profile second»). Это **устарело** после slices A–E и здесь не воспроизводится. `FULL_USER_PATH_CANON_V1.md` — единственная версия, которой нужно следовать.

---

## 9. Явные противоречия старых документов, снятые этим объединением

| Было | Где | Решение здесь |
|---|---|---|
| 5 файлов заявляли себя «главным документом продукта» с разными датами (01.06–21.07) | TODAY_PRODUCT_MODEL, PIM_NORTH_STAR, TODAYFLOW_PRODUCT_MODEL, BUILD_MAP, CORE_PRODUCT_CANON | Один документ (этот). Build Map — только entity-трекер. Today/Profile screen models — остаются, но explicitly не «весь продукт» |
| Порядок Today vs Profile после signup — расходится | CORE_PRODUCT_CANON §8.2 vs FULL_USER_PATH_CANON_V1 | §8 выше — FULL_USER_PATH_CANON_V1 побеждает |
| Тарифы в ₽ в коде vs рынок US/EU | `pricing/page.tsx` (старый draft) | §7.1 — рынок US/EU, Stripe, $/€; язык UI русский; цифры всё ещё placeholder |
| «Launch Scope Freeze» объявлен 02.07 («философия закрыта до user test»), но 21.07 в CORE_PRODUCT_CANON появился новый крупный блок (JTBD packs: Love OS/Money OS/Decision OS/Pattern OS/State OS) | TODAYFLOW_PRODUCT_MODEL freeze-notice vs CORE_PRODUCT_CANON §11 | **CLOSED 2026-07-24** — §10: packs ×6 → **backlog v2**, не launch (post-freeze scope; не core daily loop) |
| §3.4 unified называл Maps «второй половиной Profile»; PR-4 / PROFILE_SCREEN_MASTER §7 уже вынесли Maps на `/maps/*` | этот документ (до v1.4) vs PROFILE_SCREEN_MASTER §7 | §3.4.1 — Profile = «кто я»; Maps UI = отдельные surfaces; SoT IA = PROFILE_SCREEN_MASTER §7 |

### 9.1 Уточнение: L1/L2/L3 — три разные оси, не путать в одном абзаце

| Ось | Что значит L1 / L2 / L3 |
|---|---|
| **Day Sources** | objective sky / shared symbolic / personal-to-natal |
| **Profile Free vs Paid** | identity base / structural (ASC·дома·styles) / deep packs (helps, patterns) |
| **Поля пользователя (data gate)** | дата / +время / +место — это входной gate, не depth-tier |

Data gate и Day L3 связаны (без времени+места нет natal-транзитов), но Free-режим без reveal L3 на Profile — отдельное решение матрицы тарифов, не то же самое, что «нет birth_place у пользователя». Три оси используют одинаковые буквы случайно — не одна и та же лестница.

---

## 10. JTBD Packs — **CLOSED 2026-07-24: backlog v2, не launch**

Users не покупают астрологию/таро/нумерологию как изолированные системы — они покупают ясность, объяснение, контроль, decision support, дневную ориентацию. Содержание паков сохранено как справочник для v2; **в launch v1 не едут**.

- **Love OS** — что чувствует другой человек · почему отношения буксуют · продолжать или отпустить · почему повторяется romantic pattern
- **Money/Career OS** — почему не растёт доход · что монетизировать · менять работу или нет · действовать сейчас или ждать
- **Decision OS** — делать или нет · писать или нет · остаться или уйти · принять оффер · рисковать сейчас или ждать
- **Pattern OS** — почему повторяются ситуации/расставания/токсичные динамики · почему рвётся дисциплина
- **State OS** — что происходит эмоционально сейчас · временно ли это · как пережить следующие 24 часа
- **Daily OS** — на чём фокус сегодня · чего избегать · где действовать, где держать паузу

**Решение *(FROZEN 2026-07-24):*** JTBD packs ×6 → **backlog v2**, не launch-контур.

**Почему:**

1. **Post-freeze scope** — паки появились после объявленной заморозки философии (02.07), не до; второй раз мимо freeze (§9) — сигнал держать гейт строже, не расширять soft launch.
2. **Не core daily loop** — не встраиваются в замороженные v1-поверхности (Today / Profile / Compatibility / Tarot); по канону это explicit-question JTBD-слой, а он сам «опционален, не центр продукта».
3. **Не косметика** — фактически 6 новых generation-контрактов с полной планкой качества; content-спринт, конкурирующий с smoke web перед soft launch.
4. **North Star soft launch** — проверить, что дневной цикл (Today ritual + Profile + Growth Index) даёт «вечером лучше, чем без приложения». Шесть OS ничего не добавляют к этой проверке.

---

## 12. Launch MVP contour — FROZEN 2026-07-24

Зафиксировано по Cleanup Report §6.1. Правки — только явным решением + строка в changelog.

**Едет в launch v1 (поверхности / primary path):**

- Landing
- Onboarding (**value-first**: preview → email/claim, не auth-first)
- Profile-min
- Today + Evening + D2 continuity — First Today включает **Intent/Reality chips** (placement C) перед reveal
- Compatibility (hook / Public L1 + Personal hook)
- Tarot ×1 (card-of-day / один спред на старте)
- Pricing/Billing как **draft / wave 2** (не DoD launch; см. §7) — маршрут живёт в marketing shell, не в product nav

**Auth at save *(FROZEN):*** email + **magic link only** (без plaintext temp password в welcome-email).

**Intent/Reality *(FROZEN placement C):*** внутри First Today (`FirstTodayReactionGate`), не отдельные шаги funnel и не post-auth screens. Legacy `/onboarding/intent|reality` → redirect на First Today.

**Backlog v2 — убрать из primary nav / не продавать как launch-scope** (routes могут остаться как deep-link / redirect / legacy):

affirmations · asceticisms · challenges · rewards · growth (полный) · library · maps (кроме тонкой CTA / seed preview на Profile) · reports · weekly · discover · dashboard (уже redirect → `/today`)

Redirect-заглушки (`/dashboard`, `/horoscopes`, `/birth-chart`) **не удалять** — совместимость со старыми/deep-link URL.

**Платежи *(FROZEN 2026-07-24):*** рынок **US/EU** → **Stripe**, валюта **$/€**. РФ не в scope. Язык продукта v1 — **русский**. См. §7.1.

### 12.2 Platforms — **FROZEN 2026-07-24** (факт кода, не желаемое)

**Web-first:** soft launch DoD = web. iOS/Android не блокируют web.

| Платформа | v1 scope | Реальный статус (репо, 2026-07-24) |
|---|---|---|
| **Web** | Полный launch-контур §12 | ✅ |
| **iOS** | Today · Profile · Compatibility · Tarot | ✅ поверхности уже есть |
| **Android** | **Есть:** Today + Compatibility (2 таба в `MainActivity`). **Строить с нуля:** Profile UI + auth/onboarding вход (сейчас только prefs `auth_token` + `CompactUserModel` data, без экранов). **Отдельный спринт:** Tarot product (card-of-day внутри Today ritual ≠ Tarot surface) | Не «включить Profile» — новая работа |

Явно: Android v1 **не** обещает паритет с web/iOS по Profile/Tarot/auth. Молчаливое отставание запрещено — scope выше, не «догоним потом без записи».

### 12.1 Growth Index feed in v1 — **A FROZEN 2026-07-24**

**Решение A:** не возвращать `/habits`, `/asceticisms`, `/affirmations`, полный Growth в primary nav.  
Вместо этого — **микро-действия внутри Today** (zone 4 Practice + evening close): один тап → события `habit_completed` / `affirmation_done` / `ascetic_step_done` / `practice_completed` → кормление Growth Index (`meaning_progress` · Reward Rings).

Это не переоткрывает MVP scope: Growth остаётся teaser из Today (§3.5), teaser просто **реально пишет** в индекс с первого дня.

#### Zone 4 (Today) — teaser, не хаб

| Слот | Логика | Событие |
|---|---|---|
| Practice | как есть | `practice_completed` |
| Аффирмация дня | системная; короткий текст + кнопка «Сделал(а)» (не простое чтение) | `affirmation_done` на тап (не `affirmation_read` / `action_option_selected`) |
| Активная привычка / аскеза | если уже настроена через `/practices` — один тап «Отметил(а) сегодня», без отдельного экрана | `habit_completed` / `ascetic_step_done` |
| Настроить | маленькая deep-link на `/practices` (не primary nav) | не событие |

Zone 4 **не создаёт** привычки/аскезы — только закрывает уже существующие. Создание остаётся на `/practices` (роут жив, из nav убран).

#### Evening

Если есть активная привычка/аскеза — опциональный вопрос в **существующем** вечернем блоке рядом с целью дня (тот же UI-паттерн), не отдельный шаг S11.

#### Backend — `ring_tier_reached_at`

При пересчёте growth index: если peak впервые покрыл порог тира → insert `(user_id, tier_key, reached_at=now())`; повторное пересечение того же порога не перезаписывает. Идемпотентно.

**Не делать в v1:** отдельные экраны трекеров в nav, streak-ради-streak копирайт, checkout мерча.

**Мерч / кольца — заложить сейчас, производить потом:**

- Копирайт `futureMerchRu` остаётся обещанием «потом», не checkout.
- **Обязательно в v1 коде:** персистить факт «user достиг тира N в дату X» (`reward_ring_tier_reached` per user × tier) при пересечении порога. Дёшево сейчас; восстановить задним числом — нет. Пик индекса (`reward_evolution_index_peak`) уже есть — дополнить **датами по тирам**, не только списком earned ids.
- Waitlist / производство / кто имеет право заказать (Pro vs любой достигший) — отдельный операционный трек **после** soft launch, не блокер DoD.

---

## 11. Changelog

| Дата | Изменение |
|---|---|
| 2026-07-24 | v1.0 — объединение CORE_PRODUCT_CANON + TODAYFLOW_PRODUCT_MODEL + TODAYFLOW_PRODUCT_BUILD_MAP (философская часть) + PIM_PRODUCT_NORTH_STAR; явное снятие 4 противоречий (§9); JTBD packs вынесены в §10 (тогда — открытый приоритет) |
| 2026-07-24 | v1.1 — §12 Launch MVP contour FROZEN (§6.1 Cleanup Report) |
| 2026-07-24 | v1.2 — §7.1 рынок US/EU + Stripe +$/€ FROZEN; язык продукта v1 = русский; РФ out of scope |
| 2026-07-24 | v1.3 — Auth-at-save magic-only hygiene; Intent/Reality placement **C** in First Today |
| 2026-07-24 | v1.4 — §3.4 Profile = «кто я» only; §3.4.1 Maps UI home = `/maps/*` (PR-4); §9.1 L1/L2/L3 three-axis disambiguation |
| 2026-07-24 | v1.5 — §12.1 Growth feed **A**: Today micro-actions → Growth Index; ring_tier_reached_at required; no merch checkout in v1 |
| 2026-07-24 | v1.6 — §12.2 Platforms: Android = Today+Compatibility existing; Profile+auth = build; Tarot = later sprint |
| 2026-07-24 | v1.7 — §12.1 Zone 4/Evening slot design; `/practices` demoted from primary nav; `reward_ring_tier_reached` |
| 2026-07-24 | v1.8 — §10 JTBD packs ×6 → **backlog v2** (не launch); post-freeze scope, не core daily loop |
