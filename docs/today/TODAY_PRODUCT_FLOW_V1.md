# Today Product Flow v1

**Status:** CANON LOCKED · **2026-08-15**  
**Роль:** **единственный канон продуктового цикла Today** — какие экраны видит пользователь, какой вопрос у каждого, что открывается тапом, что вечером сохраняется.  
**Meaning SoT:** только [TODAY_CONTENT_PIPELINE_V1](./TODAY_CONTENT_PIPELINE_V1.md). Этот файл **не** считает energy, drivers, windows, Personal Day.

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

---

## Четыре поверхности (LOCKED)

Обязательные шаги ScreenFlow — ровно эти. Цвет, практика, аффирмация, timeline, энциклопедия драйвера **не** становятся новыми шагами: только тап / sheet внутри экрана.

| # | id | Вопрос | Слой смысла |
|---|----|--------|-------------|
| 1 | `today` | Какой сегодня день? | **Global Day** |
| 2 | `ritual` | Посмотри на день ещё с двух сторон | Card + Number **lenses** |
| 3 | `my_day` | Что это значит *для меня*? | **Personal Day** |
| 4 | `evening` | За что я благодарен этому дню? | User response → Gratitude History |

Guest: `today` + `ritual` (universal number + card base) + `evening`. `my_day` — honest omit.

### Code now vs target

| | Сейчас | Target |
|--|--------|--------|
| Шаги | **4** (`today` · `ritual` · `my_day` · `evening`) | 4 |
| Timeline | только `my_day`: natal clocks как интервал до следующего часа; `supports`/`cautions` из Engine; omit если нет активаций | **только** на `my_day`, персональный |
| Вечер | благодарность (persist); 5 категорий + «Написать своё» | **благодарность** |
| Color / practice / action | карточки **внутри** `my_day`, omit если пусто | внутри `my_day` |
| Ritual A/B | **A:** закрытая карта (`DsRitualGate`); pick в overlay. **B:** открытая карта + number gate | закрытая карта → открытая + число |
| Ritual C | compact card + number; tap → catalog then lens | оба остаются на экране |
| First Today | reaction gate → те же 4 поверхности (capability) | не отдельный conversation-цикл |

---

## 1. TODAY — общий день

Один экран. Один dashboard.

```text
ENERGY → MOON → MAIN DRIVER → STRENGTHS → RISKS
```

Одинаков для одной `local_date` / day-TZ / версии правил.  
**Не влияют:** натал, Таро, число, цели, история поведения.

### Верх

- Дата: «Сегодня · 15 августа» (локаль).  
- **Главная энергия** = `primary_energy` (закрытый 8-set). Считает Day Engine. LLM только формулирует.  
- Одна короткая человеческая строка про уже установленную энергию.

### Луна

Компактный факт (не энциклопедия): знак · фаза · день цикла.  
Тап → sheet: фаза, знак, смена знака если сегодня, значение **в контексте сегодняшнего Global Day**.

### Главный драйвер

Один (на экране). Engine ранжирует 1–3; UI показывает главного.  
Подпись — canonical meaning, не десять аспектов.  
Тап → событие, время, canonical meaning, почему в ranked drivers, связь с `primary_energy`.

Пользователь всегда может ответить: *почему TodayFlow считает день именно таким?*

### Сильные стороны / риски

Chips / иконки из Global `strength[]` / `risk[]` (типы действий, не сферы).  
Тап по chip → почему, какие drivers, как обычно проявляется.  
Риски Global ≠ персональные cautions на `my_day`.

### Здесь нет

Персональный прогноз · натал · Personal Day Number · карта · персональный timeline · гороскоп work/money/relationships/health · простыня аспектов · отдельный кадр «ориентир».

**Timeline на этом экране запрещён.** Окна считает Engine (authority); **показ** — только Personal Timeline на `my_day`. UI hide ≠ mutate.

---

## 2. RITUAL — карта и число

Один ScreenFlow-шаг, три состояния. Reveal не пересобирает день.

Карта и число **ничего не определяют** в Global Day и Personal Day. Это линзы поверх уже посчитанного Personal Day.

```text
PERSONAL DAY × CARD  → Card Lens
PERSONAL DAY × NUMBER → Number Lens
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

Карта и число в расчёт **не входят**.

Нет отдельного блока «почему день важен для тебя»: сам экран = «это про тебя».

| Слот | Правило |
|------|---------|
| Personal headline | одно резюме |
| Мой фокус | одна тема + 1–2 предложения |
| В приоритете | ≤2–3 конкретных пункта |
| Осторожнее | 1–2 персональных риска — **не** копия Global Risks |
| Personal Timeline | см. ниже |
| Color / practice / affirmation / action | опциональные карточки; не источники смысла |
| Trackers / streaks | показать релевантное; **не** участвуют в Global / Personal / energy / drivers / timeline |

### Personal Timeline

Единственный timeline продукта. Внутри `my_day`, не отдельный шаг.

Основа: точные события общего неба × natal activations.  
Не бинарное хорошо/плохо: окно несёт `supports[]` / `cautions[]` (уже решённые Engine; Personal только отбирает и формулирует).

Нет значимых персональных активаций → **omit**, не invent.

### Дополнительные карточки (не шаги)

- **Цвет** — один, scoring после energy + risk + personal focus. LLM не выбирает.  
- **Практика** — максимум одна, из Personal Focus или компенсации Personal Risk. Иначе omit.  
- **Аффирмация** — отдельный тип, не `practice_recommendation` bucket. Из Personal Day.  
- **Действие** — один выполнимый шаг (application Personal Day).  
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

| Depth | Evidence | `today` | `ritual` | `my_day` | `evening` | Personal Timeline |
|-------|----------|---------|----------|----------|-----------|-------------------|
| guest | shared sky | да | card + universal number | omit | да | omit |
| general | account, thin natal | да | да | omit | да | omit |
| light | DOB | да | да | да (без домов/ASC) | да | omit |
| deep | DOB + time + place | да | да | да | да | если есть активации |

Пустые персональные слоты, притворяющиеся «твоим днём», запрещены.

---

## Порядок работ (после lock)

Не чинить шестиблочный ScreenFlow поверх этой модели.

0. **Этот документ** — product flow.  
1. Схлопнуть ScreenFlow ids → `today` · `ritual` · `my_day` · `evening`.  
2. TODAY dashboard: energy · moon · driver · strength/risk chips; sheets on tap; **убрать timeline с Global**.  
3. Ritual A→B→C (карта, затем число; оба остаются).  
4. MY DAY: headline · focus · priority · cautions · personal timeline · optional cards.  
5. Evening gratitude persist (замена evening-job «обещание/ловушка»).  
6. Gratitude History → Month → Map (отдельный поезд).

---

## Architecture impact (2026-08-15)

- **SoT before:** presentation = SCENARIO_V3.4 шесть блоков (day+orientation, color, tasks, loop=promise). Timeline мог жить на Global. Evening = close/trap/promise.
- **SoT after:** этот файл — product cycle. 4 поверхности. Timeline **показ** только Personal. Evening = gratitude. Meaning без изменений (pipeline I0).
- **Public contract changed?** target yes, phased: gratitude payload; ScreenFlow step ids; Global screen без `windows` в UI (поля Engine остаются в `global_day`).
- **Migration required?** yes — FE ScreenFlow cutover; evening job; cached UI that expects 1b/orientation/color steps.
- **Canon updated?** yes — this file · pipeline § экран · SCENARIO_V3 superseded banner · SCREEN_FLOW_V1 §4 · README · tracker · capability TS.
- **Backward compatible?** yes API; old cached days keep nests. FE ScreenFlow ids are `today` · `ritual` · `my_day` · `evening`.
