# Today Display Inventory v1

**Status:** ACTIVE — **SoT конструкции экрана Сегодня**  
**Date:** 2026-08-29  
**Роль:** закрытый список того, что пользователь **видит** на четырёх поверхностях. Каждое написанное слово имеет класс, источник, лимит и причину. Слот вне этого файла **не существует** на Today.

**Не заменяет:** смысл дня ([TODAY_CONTENT_PIPELINE_V1](./TODAY_CONTENT_PIPELINE_V1.md)) · нарезку поверхностей ([TODAY_PRODUCT_FLOW_V1](./TODAY_PRODUCT_FLOW_V1.md)) · pager ([SCREEN_FLOW_V1](../foundation/SCREEN_FLOW_V1.md)) · visual ([TODAYFLOW_FOUNDATION_UI](../TODAYFLOW_FOUNDATION_UI.md)).

При конфликте «что на экране / сколько текста / откуда слово»: **побеждает этот файл**.  
Смысл поля — у Pipeline (authority). Какие шаги есть — у Product Flow. Этот файл — **как слот выглядит и сколько он весит**.

[TODAY_SCREEN_SCENARIO_V3](./TODAY_SCREEN_SCENARIO_V3.md) — **SUPERSEDED** как product map; не наращивать шесть блоков.

**Пара:** [PROFILE_DISPLAY_INVENTORY_V1](../profile/PROFILE_DISPLAY_INVENTORY_V1.md) — тот же закон конструкции для Profile.

---

## Architecture impact

- **SoT before:** Product Flow задавал 4 поверхности и грубые слоты («одно резюме», «≤2–3 пункта»), без закрытого каталога chrome vs calc vs generated и без единого бюджета предложений. SCENARIO_V3 и `todayCompositionCopy.storyNext` держали мёртвые лейблы (ориентир, обещание, ловушка как шаг).
- **SoT after:** этот файл — display contract. Новый слот = строка здесь + Architecture impact. FE не invent. Транспорт / unavailable — честный copy, пустой UI дозволен.
- **Public contract changed?** no JSON schema. Семантика показа уточнена (anti-dupe headline vs focus).
- **Migration required?** no. Cutover: не возвращать orientation/promise как шаги; evening остаётся time-gated ([EVENING_TIME_GATE_2026-08-29](../audits/EVENING_TIME_GATE_2026-08-29.md)).
- **Canon updated?** yes — этот файл · README · Product Flow pointer · Pipeline pointer · трекер.
- **Backward compatible?** да для API. UI, который рисует шестой блок или invent при `degraded`, **вне рамки**.

---

## 0. Закон конструкции (общий с Profile)

### 0.1 Классы текста

| Класс | Кто пишет | FE может придумать? |
|-------|-----------|---------------------|
| **chrome** | `todayCompositionCopy`, лейблы 8-set, категории благодарности | нет |
| **calc** | Global Day Engine / natal overlay / ritual identity | нет — факт или omit |
| **generated** | LLM формулирует **уже решённый** слот (Global prose · Personal prose · lens) | нет нового смысла |
| **projected** | FE/BE view без новой семантики (`clipCompassProse`, chip labels) | нет |
| **catalog** | значение карты / числа из каталога | нет «сегодня» внутри catalog |
| **user** | благодарность, обещание если живёт вне meaning | не переписывает день |

Authority смысла — таблица Pipeline § Ownership. Presentation **не** в колонке Authority.

### 0.2 Три вопроса

1. Откуда?  2. Почему показали?  3. Повторится при тех же входах и версии правил?

Одинаковые `GlobalDayKey` / `PersonalDayKey` + chrome version → одинаковый набор слотов. Текст generated стабилен после persist (GET = 0 LLM).

### 0.3 Рамка

- Слот не в инвентаре → не рисовать.
- Пусто → omit, не «ради заполнения».
- `interpretation_status=unavailable` на MY DAY → одна строка «Не удалось загрузить.» Смысловые слоты, цвет, natal timeline, практика, depth — omit. Global Day на шаге TODAY может остаться (Engine, не Personal LLM).
- Сеть / throw → «Нет соединения.» Не calm-заглушка.
- Карта и число **не** определяют Global/Personal. Lens не говорит, каким *является* день.
- Guest: TODAY + RITUAL (universal number + card base) + EVENING. MY DAY omit.

### 0.4 Бюджеты

| Метка | Практика |
|-------|----------|
| chip / label | 1–3 слова · ≤18–24 chars |
| 1 мысль | 1 предложение · 8–18 слов · ≤120 chars |
| 1–2 предложения | ≤180–220 chars после clip |
| list item | 1 предложение · ≤180–200 chars |

Clip (`clipCompassProse`) — защита, не генерация.

---

## 1. Четыре поверхности (LOCKED)

Совпадает с Product Flow. Не пятый шаг.

```text
1  today     Какой сегодня день?           Global Day
2  ritual    Карта и число как линзы       Catalog + Personal lens
3  my_day    Что это значит для меня?      Personal Day
4  evening   За что я благодарен?          User → Gratitude History
             (нет в скролле, если не eveningMode и не вечер по часам)
```

Цвет, практика, аффирмация, depth, трекеры — **карточки внутри `my_day`**, не шаги.

---

## 2. Каталог — TODAY (Global)

**Одинаков** для `local_date` + locale + semantic_version. Не влияют: натал, Таро, число, цели, поведение.

Код: `TodayDayBrief` pane `atmosphere` · `buildTodayDayBriefModel`.

---

### T1-date — Дата

| Слот | Класс | Источник | Лимит | Почему |
|------|-------|----------|-------|--------|
| Eyebrow | chrome | «Сегодня» | 1 слово | якорь экрана |
| Title | calc+chrome | локаль даты («15 августа») | 1 строка | |

---

### T1-hero — Главная энергия

| Слот | Класс | Источник | Лимит | Почему |
|------|-------|----------|-------|--------|
| Луна backdrop | calc | illumination / phase | визуал ~40% сферы за верхним краем; **не** дублировать мини-луной в ряду | один живой объект |
| Eyebrow | chrome | «Энергия дня» | 2 слова | |
| Title = энергия | chrome map of calc | `primary_energy` → 8-set RU: Заземление · Поток · Сияние · Импульс · Ясность · Напряжение · Обновление · Глубина | **1 слово** | Engine выбирает; LLM не выбирает mood |
| % | calc | `round(energy_scores[primary_energy]*100)` | 2–3 цифры + `%` · omit если scores нет | не invent |
| Настроение | calc (тот же 8-set, отдельная метрика если есть) | kit Data | 1 слово · omit если нет | не путать с energy word |
| Человеческая строка | generated (Global prose) | atmosphere / expect / essence — **одна** линия | **1 предложение · 12–22 слова · ≤160 chars** | формулирует уже выбранную энергию |
| Sheet по тапу | projected | line + expect + note + energyCause | 2–4 предложения суммарно · каждый кусок ≤160–320 | глубина **того же** слота, не новый шаг |

**Запрет:** натал · personal overlay · «ориентир» отдельным кадром · ярлык внутренней классификации (`напряжение|усиление|…`) на UI.

---

### T1-clock — Часы неба (Global day clock)

Не Personal Timeline.

| Слот | Класс | Источник | Лимит | Почему |
|------|-------|----------|-------|--------|
| Заголовок окна | chrome | «Окно дня» | 2 слова | |
| Range | calc | `windows[]` (пик intensity → следующий timed clock) | `HH:MM–HH:MM` · один clock → omit range, не +90 мин invent | Engine authority |
| Spectrum | calc | позиция start на 06:00–24:00 | визуал | chrome подписи 06:00 / 24:00 |
| Список влияний | calc + generated fact | Луна (знак · фаза) + ranked drivers **1–3** | строка: имя + опц. время + 1 короткая fact_ru **≤120 chars** | «почему день такой» |
| Leading glyph | catalog | `DsPlanet` | — | |
| Sheet строки | calc | событие · время · canonical meaning · почему в ranked · связь с energy | 4–8 rows · value 1 предложение | воспроизводимый ответ |

Untitled window (нет факта драйвера) — omit.

---

### T1-strength / T1-risk — Поддержка и риски Global

| Слот | Класс | Источник | Лимит | Почему |
|------|-------|----------|-------|--------|
| Label support | chrome | «Сегодня поддерживает» | 2 слова | |
| Label risk | chrome | «Риски» | 1 слово | |
| Chips | calc | `strength[]` / `risk[]` — **типы действий**, не сферы жизни | **≤4 support · ≤3 risk** · chip 1–3 слова (`GLOBAL_ACTION_TYPE_LABELS_RU`) | |
| Sheet | generated/calc | почему, какие drivers, как обычно проявляется | 2–4 предложения | Global ≠ personal cautions на MY DAY |

---

### T1 — здесь нет

Персональный прогноз · натал · Personal Day Number · карта · **персональный** timeline · гороскоп work/money/love/health · простыня аспектов · кадр «ориентир» · CTA «Посмотреть мой день» как смысл дня (навигация ScreenFlow — chrome next, не контент).

---

## 3. Каталог — RITUAL

Reveal **не** пересобирает день. Identity `(owner, local_date)` фиксируется.

| Состояние | Что видно |
|-----------|-----------|
| **A** | Закрытая карта. Число скрыто. |
| **B** | Карта открыта (id + orientation). CTA открыть число. |
| **C** | Карта и число постоянно. Повторный выбор запрещён. |

---

### T2-gate — Состояния A/B

| Слот | Класс | Источник | Лимит | Почему |
|------|-------|----------|-------|--------|
| Title card | chrome | «Открой свою карту дня» / pick copy | 1 строка · ≤12 слов | вход, не смысл дня |
| Body card | chrome | 1–2 предложения · ≤220 chars | зеркало, не ответ на все вопросы | |
| Title number | chrome | «Открой своё число дня» | 1 строка | |
| Body number | chrome | 1–2 предложения · ≤180 chars | ритм, не пересчёт дня | |
| Step chrome | chrome | «Шаг 1 из 2» / «Шаг 2 из 2» | — | |

---

### T2-result — Состояние C + sheet

| Слот | Класс | Источник | Лимит | Почему |
|------|-------|----------|-------|--------|
| Карта face | catalog | deck + id + orientation | визуал | |
| Число glyph | calc | numerology identity | 1–2 цифры / title | |
| Sheet: «Значение» | **catalog** | base meaning карты / числа | **2–4 предложения · 40–70 слов · ≤420 chars** | учебник символа, не «ты сегодня» |
| Sheet: «Для тебя сегодня» | generated lens | Personal Day × symbol (`bridge_to_day` / personal_angle) | **1–3 предложения · 20–45 слов · ≤280 chars** | линза поверх уже посчитанного дня; **не** «день такой потому что карта» |

**Запрет:** карта/число → назад в Global energy/drivers/windows · второй сюжет дня · invent lens при пустом persist.

Код: `TodayRitualLensPair` · hook_reveal.

---

## 4. Каталог — MY DAY (Personal)

```text
Global Day × Natal Overlay → Personal Day
```

Карта и число в расчёт **не** входят. Экран сам = «это про тебя» — отдельного блока «почему важно для тебя» нет.

**Anti-dupe (LOCKED):** `headline` и `focusBody` **не** могут быть одним и тем же `why_personal`. Если после clip строки совпадают или одна содержит другую (≥24 chars) — оставить **focus**, headline omit.

Код: `TodayMyDayPane`.

---

### T3-unavailable

| Слот | Класс | Источник | Лимит |
|------|-------|----------|-------|
| Одна честная строка | chrome | «Не удалось загрузить.» | 3 слова |

Omit: headline, focus, priority, caution, color, natal timeline, practice, depth. Extra user trackers (привычки, которые человек уже ведёт) можно оставить как жизнь, не meaning.

---

### T3-headline — Personal headline

| Слот | Класс | Источник | Лимит | Почему |
|------|-------|----------|-------|--------|
| Title card | generated | Personal: `day_personal.summary_ru` **или** conflict thesis personal, **не** сырой Global expect | **1 мысль · 12–20 слов · ≤180 chars** | одно резюме «для меня» |

Код сейчас часто берёт `why_personal` в `personalLine` — **drift**: это материал focus. Cutover: headline ≠ why_personal.

---

### T3-focus — Мой фокус

| Слот | Класс | Источник | Лимит | Почему |
|------|-------|----------|-------|--------|
| Label | chrome | Callout «main» / «Мой фокус» | 2 слова | |
| Title | generated | Daily Focus / Personal theme | **3–8 слов · ≤72 chars** | одна тема |
| Body | generated | `why_personal` → soft natal beat → `personal_astrology.summary_ru` → `development_point` (первый живой) | **1–2 предложения · 18–35 слов · ≤220 chars** | мост тренд × человек |

Guest / general capability: весь MY DAY omit (не пустые слоты «твоего дня»).

---

### T3-priority — В приоритете

| Слот | Класс | Источник | Лимит | Почему |
|------|-------|----------|-------|--------|
| Label | chrome | «В приоритете» | 2 слова | |
| Items | generated | Personal `do[]` (не копия Global strength chips) | **1–3 пункта** · каждый **1 предложение · 8–16 слов · ≤200 chars** | конкретное действие/объект/момент |

Пустой список → omit секции.

---

### T3-caution — Осторожнее

| Слот | Класс | Источник | Лимит | Почему |
|------|-------|----------|-------|--------|
| Label | chrome | «Осторожнее» | 1 слово | |
| Items | generated | Personal `avoid[]` | **1–2 пункта** · каждый **1 предложение · ≤180 chars** | **не** копия T1-risk chips; фильтр exact-dupe с priority |

---

### T3-rhythm — Ритм дня

Внутри `my_day`, не шаг.

| Случай | Подпись chrome | Содержимое | Лимит |
|--------|----------------|------------|-------|
| Есть natal activations | «Мой ритм дня» | часы натал × `windows[]` supports/cautions | ≤5 timed rows · label lived use, не жаргон аспекта · ≤72 chars label |
| Нет натальных часов, есть windows + fact_ru | «Ритм дня» (не «мой») | Global clock view | те же rows |
| Нет ни того ни другого | — | **omit** | |

Unavailable interpretation → rhythm omit (даже если Engine windows есть на TODAY).

---

### T3-color — Цвет (опционально)

| Слот | Класс | Источник | Лимит | Почему |
|------|-------|----------|-------|--------|
| Имя + swatch | catalog hex | scoring после energy + risk + personal focus; LLM **не** выбирает | 1–3 слова | |
| Зачем / как носить | generated/catalog fill-empty | BE `color_guide` | **3–6 коротких строк** · каждая ≤80 chars (benefit, clothing, accessory, amount, avoid) | omit если nest null / unavailable |
| Intensity | chrome map | мягко \| ярко | 1 слово | |

Catalog / morning `daily_symbols.color` **не** подмена при unavailable.

---

### T3-practice / affirmation / action

| Слот | Класс | Источник | Лимит | Почему |
|------|-------|----------|-------|--------|
| Практика | catalog item + chrome | максимум **одна**; из Personal Focus или компенсации Personal Risk | title ≤48 chars · 1 предложение зачем ≤160 | иначе omit |
| Аффирмация | generated from Personal | отдельный тип, не practice bucket | 1 предложение · ≤140 chars | |
| Действие | generated | один выполнимый шаг | 1 предложение · ≤140 chars | |
| Трекеры / streaks | user | уже ведущиеся привычки | строки факта, не meaning | **не** участвуют в Global/Personal/energy |

Блок заданий: **≤2** выдачи «на сегодня» + отдельно «каждый день». Не каталог «выбери из шести». Empty = честный omit / chrome «Сегодня без отдельного задания.»

---

### T3-depth — Depth layer (опционально)

Не второй сюжет дня. Только после того, как база MY DAY уже полезна. Явный выбор темы. Free → CTA, не серый замок на базе. Лимит пакета: observation → mechanism → 1 шаг; не раздувать экран. Canon: [TODAY_DEPTH_LAYER_V1](../TODAY_DEPTH_LAYER_V1.md).

---

## 5. Каталог — EVENING

Не: выполнил ли обещание, совпал ли прогноз, ловушка дня, настроение.

**Показ:** `eveningMode || local hour === evening`. Иначе шаг **вынут** из скролла (индексы пересчитываются).

| Слот | Класс | Источник | Лимит | Почему |
|------|-------|----------|-------|--------|
| Title | chrome | «За что ты благодарен сегодняшнему дню?» | 1 предложение | единственный вопрос |
| Lead | chrome | «Выбери, что откликается — или напиши своё.» | 1 предложение | |
| Категории | chrome | ровно 5: За человека рядом · За то, что получилось · За спокойный момент · За новый опыт · За себя | 2–5 слов каждая | можно учесть контекст дня в **будущем** ранжировании; сейчас — фиксированный набор |
| Своё | user | textarea | **≤500 chars на поле · persist body ≤2000** | всегда доступно |
| Save / saved | chrome | «Сохранить» / «Благодарность сохранена.» | — | |

Gratitude **никогда** не переписывает сохранённый день. Запись: дата · категории · текст · опц. ссылка Personal Day · `manifest` version.

**Запрет на evening как шаг:** trap-check, «Принимаю» манифест, «Идти в сон» как job прогноза, promise-as-meaning.

---

## 6. Chrome next-anchor (не контент)

Подписи ScreenFlow («Дальше», «Ритуал», «Мой день», «Вечер») — **chrome навигации**. Не несут смысла дня.

Разрешённый набор hint: какой сегодня день · карта затем число · что это значит для меня · за что благодарен.  
**Мёртвые** ключи (`orientation`, `promise`, `ловушка как шаг`, `Поток дня` отдельным шагом) — не возвращать.

---

## 7. First Today (вход, не пятая поверхность)

После signup: reaction gate → **те же** 4 поверхности с capability. Не отдельный conversation-цикл как SoT дня. Intent/reality chips — user input в Personal Model, не второй Global Day.

---

## 8. Вне рамки

| Что | Почему |
|-----|--------|
| Кадр orientation / «Ориентир» | свёрнут в T1 sheets + T3 |
| Шесть блоков SCENARIO_V3 как шаги | superseded |
| DomainLens гороскоп 4 сфер как обязательный dashboard | не Product Flow 2026-08 |
| Promise / trap evening | заменены gratitude |
| FE словарь цвета / calm rows при fail | invent запрещён |
| Personal Timeline на TODAY | только MY DAY |
| Карта как причина energy% | стрелка только вперёд |

---

## 9. Код сейчас vs замок

| В коде сейчас | Замок |
|---------------|-------|
| `TodayDayBrief` pane `orientation` ещё существует | не шаг ScreenFlow; не наращивать |
| MY DAY `headline` = `why_personal` clip | **drift** — headline ≠ focus body |
| `todayCompositionCopy.storyNext` полный deprecated словарь | не использовать в UI |
| Loop/promise chrome ещё в copy | evening = gratitude only |
| Guide LLM может подмешиваться в composition VM | не authority; не подменять Engine chips |

---

## 10. Проверка (воспроизводимость)

1. Два пользователя, одна locale+date+version → **одинаковый** T1 (энергия, drivers, windows, chips).
2. Тот же человек, повторный GET того же PersonalDayKey → 0 LLM, те же T3 слоты.
3. Guest: нет MY DAY; T1 без personal sheet layer.
4. Unavailable: T3 = одна честная строка; цвет/timeline/focus нет.
5. Вечер до вечернего часа: шага evening нет в dots.
6. Карта открыта: T1 energy не меняется.
7. Priority items не равны T1 strength chip labels (разный слой).
8. Headline и focusBody не дублируют одну фразу.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-08-29 | v1.0 — закрытый display contract Today; лимиты слотов; anti-dupe headline/focus; evening time gate учтён |
