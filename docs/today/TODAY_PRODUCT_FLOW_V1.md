# Today Product Flow v1

**Status:** CANON LOCKED · **2026-08-15**  
**Роль:** **единственный канон продуктового цикла Today** — какие экраны видит пользователь, какой вопрос у каждого, что открывается тапом, что вечером сохраняется.  
**Meaning SoT:** только [TODAY_CONTENT_PIPELINE_V1](./TODAY_CONTENT_PIPELINE_V1.md). Этот файл **не** считает energy, drivers, windows, Personal Day.  
**Display contract (последний authority перед UI):** [TODAY_DISPLAY_INVENTORY_V1](./TODAY_DISPLAY_INVENTORY_V1.md) · закон: [DISPLAY_CONSTRUCTION_GRAMMAR_V1](../foundation/DISPLAY_CONSTRUCTION_GRAMMAR_V1.md).

**Не:** Figma · Character Engine · north star · энциклопедия аспектов.

При конфликте нарезки экрана: **побеждает этот файл**.  
[TODAY_SCREEN_SCENARIO_V3](./TODAY_SCREEN_SCENARIO_V3.md) (1a/1b · шесть блоков) — **SUPERSEDED** как product map; остаётся картой *текущего кода* до cutover.

---

## Job

За 1–2 минуты понять: **какой сегодня день**, **что поддерживает**, **где риск**, **что это значит лично для меня**.

Today — не гороскоп по сферам. Пользователь не изучает систему. Ощущение как у приложения погоды: сначала сводка, по желанию — детали.

Любой элемент UI обязан ответить на три вопроса. Если хотя бы на один ответ «непонятно» — элемента нет в Today:

1. Откуда это взялось?  
2. Почему система это показала?  
3. Получим ли тот же результат при тех же входах и той же версии правил?

**Вычисление ≠ показ.** Стрелки смысла (Pipeline) и ScreenFlow — разные порядки. Personal Day persist **до** кадра MY DAY — норма. См. [DISPLAY_CONSTRUCTION_GRAMMAR_V1](../foundation/DISPLAY_CONSTRUCTION_GRAMMAR_V1.md) §5.1.

---

## Четыре поверхности (LOCKED)

Обязательные шаги ScreenFlow — ровно эти. Цвет, практика, аффирмация, timeline, энциклопедия драйвера **не** становятся новыми шагами: только тап / sheet внутри экрана.

| # | id | Вопрос | Слой смысла |
|---|----|--------|-------------|
| 1 | `today` | Какой сегодня день? | **Global Day** |
| 2 | `ritual` | Посмотри на день ещё с двух сторон | Card + Number **lenses** |
| 3 | `my_day` | Что это значит *для меня*? | **Personal Day** |
| 4 | `evening` | За что я благодарен этому дню? | User response → Gratitude History |

Guest: `today` + `ritual` **catalog** (universal number + card base) + `evening`. `my_day` — honest omit. Ritual **personal lens** — omit (нет Personal Day).

### Code now vs target

| | Сейчас | Target |
|--|--------|--------|
| Шаги | **4** (`today` · `ritual` · `my_day` · `evening`) | 4 |
| Timeline | **TODAY:** Global clock. **MY DAY:** natal clocks если есть, иначе `windows[]` × `fact_ru` как «Ритм дня» | Global clock ≠ «мой» natal timeline |
| Вечер | благодарность (persist); 5 категорий + «Написать своё» | **благодарность** |
| Color / practice / affirmation | карточки **внутри** `my_day`, omit если пусто | внутри `my_day` |
| Ritual A/B | **A:** закрытая карта (`DsRitualGate`); pick в overlay. **B:** открытая карта + number gate | закрытая карта → открытая + число |
| Ritual C | compact card + number; tap → catalog then lens | оба остаются на экране |
| First Today | reaction gate → те же 4 поверхности (capability) | не отдельный conversation-цикл |

---

## 1. TODAY — общий день

Один экран. Один dashboard.

```text
ENERGY% + mood → Global day clock → timed transits → STRENGTHS → RISKS
```

Одинаков для одной `local_date` / day-TZ / версии правил.  
**Не влияют:** натал, Таро, число, цели, история поведения.

### Верх

- Дата: «Сегодня · 15 августа» (локаль).  
- Луна — один backdrop, **~40% сферы за верхним краем** экрана (kit bleed). Не дублировать мини-луной в ряду.  
- **Главная энергия (слово)** = `primary_energy` (закрытый 8-set). Считает Day Engine. LLM только формулирует.  
- **Энергия %** = `round(energy_scores[primary_energy] * 100)` когда score есть. Honest omit, если scores нет. Не invent.  
- **Настроение** = тот же 8-set, отдельная метрика (kit Data).  
- Одна короткая человеческая строка про уже установленную энергию.

### Часы неба (Global day clock)

Не Personal Timeline.

- **Окно дня** (`DsWindowCard`): start–end из Engine `windows[]` (пик intensity → следующий timed clock; один clock → omit range, не invent +90 мин). Spectrum = позиция start на шкале 06:00–24:00.  
- **Влияния дня** (list rows): Луна (знак · фаза) + ranked drivers 1–3. Leading = `DsPlanet`. **Время на строке**, если Engine дал `windows[].time` для `driver_id`. Тап по планете/строке → sheet: событие, время, canonical meaning, почему в ranked, связь с `primary_energy`.  
Пользователь всегда может ответить: *почему TodayFlow считает день именно таким?*

### Сильные стороны / риски

Chips / иконки из Global `strength[]` / `risk[]` (типы действий, не сферы).  
Тап по chip → почему, какие drivers, как обычно проявляется.  
Риски Global ≠ персональные cautions на `my_day`.

### Здесь нет

Персональный прогноз · натал · Personal Day Number · карта · **персональный** timeline · гороскоп work/money/relationships/health · простыня аспектов · отдельный кадр «ориентир».

**Personal Timeline на этом экране запрещён.** Окна считает Engine (authority). **Показ Global clock** (окно + timed transits) — здесь. **Показ Personal Timeline** — только на `my_day` (небо × natal). UI hide ≠ mutate.

---

## 2. RITUAL — карта и число

Один ScreenFlow-шаг, три состояния. Reveal не пересобирает день.

Карта и число **ничего не определяют** в Global Day и Personal Day. Это линзы поверх **уже persisted** Personal Day.

Personal Day считается и сохраняется **независимо** от того, открыл ли пользователь кадр MY DAY. RITUAL читает этот persist только для Card Lens / Number Lens. Затем MY DAY показывает сам Personal Day.

```text
PERSONAL DAY × CARD  → Card Lens     (omit, если Personal Day нет — guest)
PERSONAL DAY × NUMBER → Number Lens  (omit, если Personal Day нет)
```

Стрелка только вперёд. Карта/число не идут назад в Personal / Global.

| Состояние | Что видно |
|-----------|-----------|
| **A** | «Открой свою карту дня» + закрытая карта. Число скрыто. |
| **B** | Карта открыта (id + orientation). CTA «Открыть число дня». |
| **C** | Карта и число постоянно на одном экране. Повторный выбор запрещён: identity фиксирована на `(owner, local_date)`. |

Тап по карте / числу → sheet: сперва catalog base, затем *что это может значить для тебя сегодня* (lens).  
Lens не говорит, каким является день.

---

## 3. MY DAY — персональный день

```text
Global Day × Natal Overlay → Personal Day
```

Character Engine **не** вход. Карта и число в расчёт **не входят**.

Нет отдельного блока «почему день важен для тебя»: сам экран = «это про тебя».

| Слот | Правило |
|------|---------|
| Personal headline | главный персональный **тезис** дня |
| Мой фокус — title | **ось / область**, где тезис проявляется сильнее (projected / map_label; не второй тезис) |
| Мой фокус — body | как именно проявляется и куда внимание |
| В приоритете | ≤2–3 конкретных пункта относительно сегодняшней ситуации |
| Осторожнее | 1–2 персональных риска — **не** копия Global Risks |
| Personal Timeline | см. ниже |
| Color / practice / affirmation | опциональные карточки; не источники смысла; **отдельного step нет** |
| Trackers / streaks | показать релевантное; **не** участвуют в Global / Personal / energy / drivers / timeline |

### Personal Timeline / ритм дня

Внутри `my_day`, не отдельный шаг.

**Если есть natal activations** — Personal Timeline: точные часы натала × Engine `windows[]` (`supports` / `cautions`). Подпись «Мой ритм дня».

**Если натальных часов нет** — показать **Global day clock**: те же timed `windows[]` × ranked `drivers.fact_ru`. Подпись «Ритм дня», не «мой». Это часы неба, не персональная геометрия. Untitled window (нет факта драйвера) — omit, не invent.

Нет ни natal clocks, ни timed windows с фактами → **omit**.

**Если `interpretation_status=unavailable`:** слоты смысла MY DAY (headline · фокус · приоритет · осторожнее) = одно честное «Не удалось загрузить.». **Цвет, natal timeline, практика, depth** — omit. Не мешать leftover `conflict.short_name`, catalog/morning color и независимый `day_facts` clock с этим статусом. Global Day на шаге `today` (окна, drivers, energy) может остаться — это Engine, не Personal interpretation.

### Дополнительные карточки (не шаги)

- **Цвет** — один, scoring после energy + risk + personal focus. LLM не выбирает. **Omit**, если Personal Day interpretation unavailable. Catalog / morning `daily_symbols.color` **не** подмена.
- **Практика** — максимум одна, из Personal Focus или компенсации Personal Risk. Иначе omit.  
- **Аффирмация** — отдельный тип, не `practice_recommendation` bucket. Из Personal Day.  
- **Отдельного «шага» нет** — конкретное действие = `T3.priority`.  
- Привычки/цели — жизнь пользователя рядом, не meaning.

---

## 4. EVENING — благодарность

Не спрашиваем: выполнил ли обещание, совпал ли прогноз, настроение, удалось ли избежать ловушки.

Один вопрос: **За что ты благодарен сегодняшнему дню?**

Несколько предложенных категорий + «Написать своё». Предложения могут учитывать контекст дня; свой текст всегда доступен.

### Данные (Gratitude History)

Каждый ответ — структурированная запись, не одноразовый check-in:

- дата  
- выбранные категории  
- свой текст  
- опционально контекст Personal Day (ссылка, не пересчёт)  
- версия Today Package (`manifest`)

**Gratitude никогда не переписывает уже рассчитанный день.**

**D+1 (не новый смысл дня):** на шаге `today` можно показать **одну** строку из вчерашней Gratitude History (`evening_completed` + категории/текст; опционально уже показанный тезис дня как `morning_focus` snapshot). Пусто → omit. Не прогноз, не outcome «сделал/не сделал», не второй канон вечера. Persist — `POST /day-connection/{date}`; чтение — `GET` вчерашней записи. localStorage — same-device fallback, не SoT.

### Позже (не блокер дневного цикла)

| Горизонт | Артефакт |
|----------|----------|
| Месяц | «Твой месяц» — темы благодарности, не голая статистика |
| 6 месяцев / год | **My Gratitude Map** — data-art (форма ← категория, плотность ← частота, положение ← период). Сохранить / поделиться / печать |

---

## Причинность (направление стрелок)

```text
НЕБО                    →  GLOBAL DAY
НЕБО × НАТАЛ            →  PERSONAL DAY
PERSONAL DAY × CARD     →  CARD LENS
PERSONAL DAY × NUMBER   →  NUMBER LENS
PERSONAL DAY            →  COLOR / PRACTICE / ACTION
USER RESPONSE           →  GRATITUDE HISTORY
```

Запрет назад:

- карта ↛ Personal Day / Global Day  
- число ↛ Personal Day / Global Day  
- Personal Day ↛ Global Day (`primary_energy`, drivers, strength, risk, window facts)  
- gratitude ↛ любой уже сохранённый день  

---

## Capability (кто какой экран видит)

| Depth | Evidence | `today` | ritual catalog | ritual lens | `my_day` | `evening` | Personal Timeline |
|-------|----------|---------|----------------|-------------|----------|-----------|-------------------|
| guest | shared sky | да | card + universal number | **omit** | omit | да | omit |
| general | account, thin natal | да | да | **omit** (нет Personal Day) | omit | да | omit |
| light | DOB | да | да | да (если Personal persisted) | да (без домов/ASC) | да | natal omit; **Global «Ритм дня»** если есть windows |
| deep | DOB + time + place | да | да | да | да | да | natal если есть активации; иначе Global clock |

Пустые персональные слоты, притворяющиеся «твоим днём», запрещены. Global `windows[]` на `my_day` — часы неба, не «мой натал».

---

## Порядок работ (после lock)

Не чинить шестиблочный ScreenFlow поверх этой модели.

0. **Этот документ** — product flow.  
1. Схлопнуть ScreenFlow ids → `today` · `ritual` · `my_day` · `evening`.  
2. TODAY dashboard: energy% · mood · Global day clock · timed transits · strength/risk chips; sheets on tap; Personal Timeline только на `my_day`.  
3. Ritual A→B→C (карта, затем число; оба остаются).  
4. MY DAY: headline · focus · priority · cautions · personal timeline · optional cards.  
5. Evening gratitude persist (замена evening-job «обещание/ловушка»).  
6. Gratitude History → Month → Map (отдельный поезд).

---

## Product-gate selection (2026-09-21)

После **TODAY_INFORMATION_CONTRACT: CLOSED / PASS** следующий шаг — не новое информационное N и не Compatibility Information Contract.

Сверка: этот файл (cycle) · [TODAY_DISPLAY_INVENTORY_V1](./TODAY_DISPLAY_INVENTORY_V1.md) (last UI authority) · [FULL_USER_PATH_CANON_V1](../audits/FULL_USER_PATH_CANON_V1.md) §13/§16.

| Gate | Статус после сверки | Класс |
|------|---------------------|--------|
| 4-surface cutover / ritual-first funnel | **CLOSED** (Phase 2.2). `/today` opens on `today`, then `ritual` · `my_day` · `evening` | cycle already locked |
| **X3 Theme / Focus / Step** | **CLOSED / PASS.** T1 Theme · T3 Focus · T3.priority Step. Live T2-gate copy is a lens over an already-counted day; card/number do not define Theme/Focus/Step or action timing | experience on closed N |
| **X4/X5 honest reveal copy** | **CLOSED / PASS (joint).** Two §13 IDs, one PASS. Locked `T2-gate.card_*` is a reveal, not a pick. Locked `T2-gate.number_*` is the calendar day number, not «своё». Gesture stays theater; formula stays calendar | experience copy |
| X4 (clause) | **PASS.** Card copy does not claim a real pick. Reveal verbs OK. Prebake + deck gesture unchanged | clause of X4/X5 |
| X5 (clause) | **PASS.** Number copy does not claim a personal number. Live CTA = «Открыть число дня». YYYYMMDD + ring gesture unchanged | clause of X4/X5 |
| **X11 legacy narrative** | **CLOSED / PASS.** Product `/today` mounts only the locked 4-surface. `?full=1` / `?experience=1` are no-ops. Glance-as-act not constructed. Evening is gratitude, not promise-trap. Leftover files stay | cleanup |
| **X14 progress + D2 continuity** | **CLOSED / PASS.** `T1.continuity` inside TODAY step; GET fail is TF chrome. `T3.tracker` = habit rows on MY DAY, not extraCards, survives unavailable. Не новые слоты. Не X11 leftover | experience |
| Compatibility Information Contract | **не выбран.** Отдельная таблица (PIC §9). Не автоматическое продолжение TIC | other section N |
| TIC-K21 / IL dump / PIC resume | **запрещены** этой сверкой | not a product gate |

**Следующий executable gate:** none on this Today remainder. **X14 CLOSED / PASS** on `cursor/x14-progress-d2-continuity`. Не расширять TIC. Не rebuild сервера. Не landing.

**Acceptance (X14 PASS):**

| In | Out |
|----|-----|
| Locked TODAY paints `T1.continuity` when yesterday gratitude exists; omit empty; no invent on transport failure | New Inventory slot · promise-outcome evening · second day meaning |
| Locked MY DAY paints `T3.tracker` from existing habit rows when present; omit empty; not a Priority surrogate | TIC-K21 · PIC · IL · Compatibility IC · leftover file delete · landing §16.3 · iOS parity |

Both clauses required. Order of paint = TODAY continuity, then MY DAY tracker (existing 4-surface). **CLOSED / PASS 2026-09-22.**

### Architecture impact — X14 close (2026-09-22)

- **SoT before:** X14 OPEN — AUDIT. Continuity outside TODAY step. Tracker in extraCards; mixed kinds; no emit; dropped on unavailable.
- **SoT after:** **X14 CLOSED / PASS.** Continuity in `today-frame-day`. Tracker = habit rows on MY DAY, survives unavailable. Empty omit unchanged.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this file · Inventory `T3.tracker` · FULL_USER_PATH · tracker · X14 handoff
- **Backward compatible?** yes

### Architecture impact — X14 audit (2026-09-22)

- **SoT before:** X14 selected; live placement/completeness unnamed.
- **SoT after:** X14 OPEN — AUDIT. `T1.continuity` PARTIAL. `T3.tracker` PARTIAL. No product paint.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this file · FULL_USER_PATH · tracker · X14 handoff
- **Backward compatible?** yes. Audit only.

### Architecture impact — X14 gate selection (2026-09-21)

- **SoT before:** X11 CLOSED / PASS; next remainder named «X14» without hop shape. §13 one OPEN progress row; §16.1 п.8 already one P1 item covering progress + D2.
- **SoT after:** next executable Today gate = **X14** only. PASS = both existing slots complete and placed on the locked 4-surface. Not two trains.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this file · FULL_USER_PATH §0/§13/§16 · tracker · X11 handoff pointer
- **Backward compatible?** yes. Selection only; no product paint in this hop.

**X11 close record (2026-09-21):**

**Acceptance (PASS):**

| In | Out |
|----|-----|
| Production `/today` does not mount Glance-as-act, `TodayExperienceSurface`, or `TodayRitualFlow` as product Today | Physical delete of leftover files |
| Locked 4-surface does not paint a second day story (stacked leftover, promise-trap evening drama, triple `day_story`) beside Inventory slots | X14 progress / D2 completeness · landing §16.3 · iOS parity |
| Leftover copy banks deferred from X4/X5 (`todayRitualCopy` pick / «своё число») are unreachable on locked path or cleaned here | TIC-K21 · PIC · IL · Compatibility IC · new meaning K |

**Live after this hop:** product `/today` always mounts `TodayCompositionSurface`. `?full=1` / `?experience=1` cannot switch leftover surfaces. `glanceSection` is not constructed. Evening remains gratitude. Leftover files remain in the repo.

### Architecture impact — X11 leftover narrative (2026-09-21)

- **SoT before:** X11 OPEN. Production already no-op'd leftover query params via `NODE_ENV`; the same `/today` route still imported leftover surfaces for development. Dead `glanceSection` still constructed on the locked surface.
- **SoT after:** **X11 CLOSED / PASS.** Product `/today` has one Inventory narrative. Query params are no-ops in the route. Glance leftover is not constructed there. **X14 stays after.** Not two trains.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this file · FULL_USER_PATH §0/§13/§16 · tracker · X11 handoff
- **Backward compatible?** yes. Production query params were already no-ops; the route no longer keeps a parallel mount.

### Architecture impact — X11 gate selection (2026-09-21)

- **SoT before:** X4/X5 CLOSED / PASS; next remainder named «X11 then X14» without hop shape. §13 one OPEN row; §16.1 P1 items 7–8 adjacent.
- **SoT after:** next executable Today gate = **X11** only. PASS = locked production Today has one Inventory narrative; leftover parallel surfaces/copy do not speak as Today. **X14 stays after X11.** Not two trains.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this file · FULL_USER_PATH §0/§13/§16 · tracker · X4/X5 handoff pointer
- **Backward compatible?** yes. Selection only; no product paint in this hop.

**X4/X5 close record (2026-09-21):**

**Acceptance (joint PASS):**

| Clause | In | Out |
|--------|----|-----|
| **X4** | Locked `T2-gate.card_*` chrome must not claim the user chose the card («выбери ту, к которой тянет», «Выбрать карту» as a real pick). Reveal verbs OK («открой / вытяни / сними»). | Prebake / POST reveal / deck gesture / ScreenFlow A / Inventory / K13 lens |
| **X5** | Locked `T2-gate.number_*` chrome must not claim a personal number («твоё/своё число»). Target wording: «число сегодняшнего дня» / «Открыть число дня» (already §2 state B). | YYYYMMDD formula / POST reveal / ring gesture / ScreenFlow B→C / Inventory / K14 lens |

Both clauses required. Order of paint = card then number (existing A→B). **Live after this hop:** locked card gate body is a reveal («Открой карту»), not «выбери ту, к которой тянет»; number gate title is «Открыть число дня», not «своё число». Overlay was already honest and stays theater. Unused pick CTAs in the same chrome bank neutralized. Legacy `todayRitualCopy` / `?full=1` / `?experience=1` were X11 (now **CLOSED / PASS**). Landing number promise = §16.3 backlog, not this gate. «Открой свою карту дня» remains §2 state A reveal chrome (day-card, not a pick).

### Architecture impact — X4/X5 honest reveal copy (2026-09-21)

- **SoT before:** joint gate OPEN. Live locked `T2-gate.card_body` still said «выбери ту, к которой тянет»; live `T2-gate.number_title` still said «Открой своё число дня». Overlay already honest. Mechanic already locked.
- **SoT after:** **X4/X5 CLOSED / PASS.** Same slots and A→B order. Card chrome is a reveal of a prebaked card. Number chrome is the calendar day number. Gesture stays theater. Formula stays YYYYMMDD.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this file · Display Inventory T2-gate · FULL_USER_PATH §0/§13/§16 · tracker · X4/X5 handoff
- **Backward compatible?** yes. Copy-only on existing `T2-gate.*` chrome.

### Architecture impact — X4/X5 gate selection (2026-09-21)

- **SoT before:** X3 CLOSED / PASS; next = «X4/X5» without hop shape. §13 two rows; §16.1 п.4 one item.
- **SoT after:** one joint executable gate. PASS = both honesty clauses on locked `T2-gate.*` chrome. Order = existing ritual A→B (card then number). Mechanic SoT remains [DAY_SYMBOL_REVEAL_CANON_V1](../audits/DAY_SYMBOL_REVEAL_CANON_V1.md) (prebake; client pick is theater; number = local-date reduce).
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this file · FULL_USER_PATH §0/§13/§16 · tracker · X3 handoff pointer
- **Backward compatible?** yes. Selection only; no product paint in this hop.

### Architecture impact — X3 Theme / Focus / Step (2026-09-21)

- **SoT before:** 4-surface locked; T1 Theme · T3 Focus · T3.priority present. Live T2-gate bodies still claimed the card «говорит о сегодня» and the number «задаёт ритм» / when to act.
- **SoT after:** same slots and order. T2-gate copy is a symbolic lens over an already-counted day. Card/number do not own Theme, Focus, Step, or action timing. Theatrical pick (X4) and «своё число» (X5) unchanged.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this file · FULL_USER_PATH §0/§13/§16 · tracker · X3 handoff
- **Backward compatible?** yes. Copy-only on existing `T2-gate.*` chrome.

### Architecture impact — product-gate selection (2026-09-21)

- **SoT before:** TIC CLOSED / PASS; next gate «from canon», unnamed. PIC §9 named Compatibility as a separate table, not a queue item.
- **SoT after:** next Today product gate is Full User Path **X3** (Theme/Focus/Step experience). X4–X5 then X11/X14. Not a new Information Contract. Not Compatibility N.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this file · FULL_USER_PATH §0/§13/§16 · tracker · TIC §12/handoff
- **Backward compatible?** yes. Selection only; no product paint in this hop.

---

## Architecture impact — compute≠display · no CE · no action card (2026-08-29)

- **SoT before:** four surfaces listed without stating that Personal Day persist can precede the MY DAY visit. Guest ritual did not split catalog vs personal lens. Optional MY DAY cards included a duplicate «действие».
- **SoT after:** display order remains TODAY → RITUAL → MY DAY → EVENING. Compute: Personal Day = Global × Natal Overlay, persist before MY DAY UI; RITUAL lens consumes that persist. Guest/general: catalog yes, lens no. Support cards = color · practice · affirmation. Priority owns «что сделать».
- **Public contract changed?** no JSON.
- **Migration required?** no. FE that still shows a separate action card or a personal lens for guest is drift.
- **Canon updated?** yes — this file · Grammar §5 · Pipeline · Today Inventory v1.2 · tracker.
- **Backward compatible?** yes API.

## Architecture impact (2026-08-15)

- **SoT before:** presentation = SCENARIO_V3.4 шесть блоков (day+orientation, color, tasks, loop=promise). Timeline мог жить на Global. Evening = close/trap/promise.
- **SoT after:** этот файл — product cycle. 4 поверхности. Personal Timeline **показ** только на `my_day`. Evening = gratitude. Meaning без изменений (pipeline I0).
- **Public contract changed?** target yes, phased: gratitude payload; ScreenFlow step ids. (Global `windows[]` UI: see 2026-08-15 day-clock note below.)
- **Migration required?** yes — FE ScreenFlow cutover; evening job; cached UI that expects 1b/orientation/color steps.
- **Canon updated?** yes — this file · pipeline § экран · SCENARIO_V3 superseded banner · SCREEN_FLOW_V1 §4 · README · tracker · capability TS.
- **Backward compatible?** yes API; old cached days keep nests. FE ScreenFlow ids are `today` · `ritual` · `my_day` · `evening`.

## Architecture impact (2026-08-15 · Global day clock on TODAY)

- **SoT before:** TODAY sequence ENERGY → MOON → MAIN DRIVER → STRENGTHS → RISKS. UI показывал одного драйвера; energy = 8-set label; `windows[]` скрыты на TODAY (Personal Timeline only on `my_day`).
- **SoT after:** TODAY sequence ENERGY% + mood → Global day clock (`DsWindowCard` from `windows[]`) → timed transits (moon + ranked drivers, tap → sheet) → STRENGTHS → RISKS. Луна = один backdrop, ~40% за верхним краем. **Personal Timeline** = natal × windows на `my_day`. Если natal clocks нет — `my_day` показывает Global `windows[]` × `fact_ru` как «Ритм дня».
- **Public contract changed?** no JSON fields; UI reads existing `global_day.energy_scores`, `windows[]`, `drivers[]`.
- **Migration required?** no — omit metric/window/time when Engine left them empty.
- **Canon updated?** yes — this file §1 · §3 · pipeline § экран · tracker.
- **Backward compatible?** yes; days without scores/windows honest-omit those blocks.

## Architecture impact (2026-08-15 · MY DAY Global rhythm fallback)

- **SoT before:** MY DAY timeline omit unless deep natal `glance_timeline`. Light `my_day` had no clock. Empty natal → empty block.
- **SoT after:** MY DAY mounts the rhythm whenever the screen is shown. Natal clocks win. Else Engine `windows[]` × driver `fact_ru`, label «Ритм дня» (not «Мой»). Untitled windows omit.
- **Public contract changed?** no.
- **Migration required?** no.
- **Canon updated?** yes — this file §3 · capability table · pipeline § экран.
- **Backward compatible?** yes; no windows/facts → still omit.

## Architecture impact (2026-08-18 · unavailable MY DAY does not leak color/timeline)

- **SoT before:** `interpretation_status=unavailable` filled navigational slots with «Не удалось загрузить.» but still forwarded leftover `day_scenario.props.color` / morning catalog into `color_guide`, and MY DAY independently fetched `day_facts.glance_timeline`. FE treated leftover `theme` as authoritative focus.
- **SoT after:** Color nest is **null** when interpretation is unavailable (PERSONAL DAY → COLOR). MY DAY paints one honest status and omits color, natal timeline, leftover focus title. Global Day Engine profile stays on the contract (I0 — not LLM meaning).
- **Public contract changed?** yes — semantics: `color_guide` is null on unavailable; `global_day` is present even when interpretation is unavailable.
- **Migration required?** no version bump. Next GET.
- **Canon updated?** yes — this file §3.
- **Backward compatible?** old clients that rendered catalog color next to failure copy stop doing so after FE deploy. Clients that assumed `global_day` absent on unavailable now see Engine facts on TODAY.
