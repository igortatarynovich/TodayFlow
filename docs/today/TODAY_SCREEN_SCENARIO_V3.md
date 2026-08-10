# Today — сценарий страницы (v3.4 · шесть блоков)

**Status:** ACTIVE · **Updated 2026-08-10**  
**Prior:** v3.3 handoff 12-step (2026-08-08) · v3.2 story-deck · v3.1 content jobs  

## Presentation SoT — шесть блоков (LOCKED)

Продуктовая нарезка Today. **Не расширять** без явного решения owner.  
12-step handoff v3.3 = **deprecated** как presentation SoT (слишком много кадров = suite, не день).

```text
1. День          — общий тренд: вайб · энергия · сферы/акценты · почему так · ждать · ловушка · делать/не делать
2. Ритуалы       — число · карта (персональный вход)
3. Инструкция    — персональная инструкция на день (мне)
4. Цвет          — цвет дня
5. Задания       — 1–2 на сегодня (+ ежедневные, если уже ведутся); не каталог «выбери из шести»
6. Петля         — обещание дня → закрытие дня
```

**Правила рамки:**

1. Общие тренды **не избегать** — блок 1 = амбассадор тренда дня (не стыдливый soft glass).  
2. Персонализация наращивается блоками 2–3–5–6, **не вместо** блока 1.  
3. Любой новый кадр/раздел обязан ответить: в какой из 6 блоков входит. Если ни в какой — **out of scope**.  
4. Content houses v3.1 (Plot / Symbols / Move / …) остаются **источниками смысла**; меняется только склейка в 6 блоков.  
5. Research explanatory systems (`docs/audits/HUMAN_EXPLANATORY_SYSTEMS_ANALYSIS.md`) — справочник; **не** спека экрана.

### Job формулы полезного Today (v3.4+)

> **Минимум трения → Максимум ясности → Быстрое действие.**  
> Today = персональный компас состояния на 1–2 минуты утром — **не** энциклопедия астрологии и **не** магазин привычек.

| # | Польза (зачем открыл) | Scan / layout |
|---|----------------------|---------------|
| 1 | Снять тревогу «со мной всё ок / сегодня такой день» | **3 сек:** вайб → короткий why → **контраст Ловушка ‖ Инструкция**; expect/энергия — вторичны |
| 2 | Внешнее → внутреннее; момент «здесь» | Число + карта на **одном** кадре |
| 3 | Мост тренд × личная карта | 2–3 предложения Prioritize / Avoid |
| 4 | Визуальный якорь дня | Цвет + одна строка «зачем» |
| 5 | Убрать паралич выбора | **≤2** чеклиста (daily streak + 1 точечное); не каталог |
| 6 | Фиксация намерения → вечерний чекаут | Promise accept · evening close |

**Запрет на блок 1:** простыни эфемерид, kitchen dumps, «прочитай всё чтобы понять день».  
Смысл слотов — из live `day_story` / nests; внешние LLM-черновики **не** SoT и не hardcode.

### Presentation map (v3.4)

| # | Блок | ScreenFlow id | Что показывает | Откуда смысл (houses / nests) |
|---|------|---------------|----------------|-------------------------------|
| 1 | День | `day` | дата · вайб/headline · why · энергия · expect · trap · do/avoid · (опц.) timeline/сферы-акценты | day_story · welcome_glass · glance energy/timeline · morning celestial |
| 2 | Ритуалы | `rituals` | число + карта (если symbols) | Symbols·A |
| 3 | Инструкция | `instruction` | персональный prioritize / avoid (+ deepen опц.) | Glance Daily Focus · depth_layer |
| 4 | Цвет | `color` | color guide | color_guide / Move color |
| 5 | Задания | `tasks` | **≤2** выдачи «на сегодня» + блок «каждый день» (streaks); empty = честный omit; не catalog shop | practice gift · affirmation · `practice_recommendation` · `today_progress` |
| 6 | Петля | `loop` | обещание → close / evening | Move promise · Response · evening |

Без symbols: блок 2 omit → **5** шагов.  
Шаг 0 (`day`) может быть без chrome dots; дальше — ScreenFlow dots + swipe.

### Deprecated (не возвращать без решения)

| Было (v3.3) | Почему вне рамки |
|-------------|------------------|
| Priority отдельным кадром | Не блок 1 и не 3 |
| Make yours как каталог 6 категорий | Блок 5 = выдача, не магазин |
| Поток дня отдельным кадром | Входит в блок 1 |
| Focus отдельно от «инструкции» | = блок 3 |
| Recap | Лишний; петля = promise+close |
| 12 swipe-шагов | Распыляет день |

### Architecture impact (2026-08-10 — six blocks)

- **SoT before:** presentation = handoff 12-step ScreenFlow (v3.3).  
- **SoT after:** presentation = **6 блоков** выше; content jobs v3.1 unchanged as meaning houses.  
- **Public contract changed?** no required JSON — FE composition; optional richer day-brief copy may use existing `day_story` fields.  
- **Migration required?** yes FE — step indices / `?sf=1&step=N` remap.  
- **Canon updated?** yes — this file · SCREEN_FLOW_V1 Today mapping · tracker.  
- **Backward compatible?** yes for API; old deep-links remap best-effort.

Связанные: [SCREEN_FLOW_V1.md](../foundation/SCREEN_FLOW_V1.md) · [TODAY_WAVE2_CONTRACT_V1.md](./TODAY_WAVE2_CONTRACT_V1.md) · [TODAYFLOW_FOUNDATION_UI.md](../TODAYFLOW_FOUNDATION_UI.md) §16

---

## 0. Сквозные правила

1. **Экран = одна задача (или одна осознанная склейка из макета).** Свайп = продолжение.
2. **Один дом на сущность (данные).** Карта/число — Symbols. Цвет — **Attributes** (presentation; данные те же, что раньше жили в Move). Практика — Practice. Ловушка-тап — Close. Сюжет why — Insight. Reading-сферы остаются в данных, отдельного swipe-шага нет.
3. **No seed leakage.** Каждый акт формулирует текст из **своих** сырых данных. Ни один акт не является источником текста для другого. Дословный или перефразированный повтор чужой формулировки = **баг генерации**, не «сквозная персонализация».
4. **Внутренняя классификация динамики** (`напряжение | усиление | доминанта | ровный день`) управляет тоном формулировок и выбором визуала. **Не** рендерится ярлыком на UI.
5. **Честный omit.** Нет сигнала → не выдумывать конфликт / сферу / ловушку / связку «ради заполнения».
6. **Домены Reading/Response:** четыре — `work` · `money` · `relationships` · `energy`. Wire DomainLens = тот же словарь (legacy `money_work`/`family` — только read-compat).
7. **Конкретность.** User-facing строка называет действие, объект или момент («три вдоха до „отправить“», «одна фраза вместо трёх») — иначе **omit**. Абстрактные пары существительных («ясность в трении») и дампы тегов через тире («темп — …, способ — …») = баг генерации.
8. **No generation-meta leakage.** Внутренние правила пайплайна («не второй сюжет», «не отдельный прогноз», «без параллельного сюжета», «связывает фактор с тоном») **никогда** не попадают в user-facing текст — симметрично seed-leak, другой класс утечки.

---

## Content jobs (v3.1 — источники смысла)

Ниже — **что** должно быть сказано (дома данных). **Как** это нарезано в swipe — таблица Presentation map выше.

## Экран 0 — Сводка (Glance) *(content; presentation → Greeting / Energy / Attributes)*

**Job:** за 2 секунды ориентация и вход дальше — сжатая проекция уже определённых актов, не отдельный сюжет.

**Каркас показа (Day Atmosphere surface — FOUNDATION_UI §11.9 / §16 Story Frame):** full-bleed фон/декор по `day_atmosphere.visual_mode` · typography-first кадр · glass только на interactive clusters (§16) · sparse chrome. **Прогресс актов = ScreenFlow chrome** (точки + свайп/клавиатура; без ряда названий актов) — не отдельный виджет в hero. Jobs смысла ниже **не** меняются — только композиция.

**На экране:**

1. **Текстура** — 1–2 предложения: фраза-синтез **тона** (внутренняя классификация). Не факты, не ярлык категории, не `short_name` «A или B».
2. **Энергия дня** (опц.) — pulse facet; honest omit если пусто. Не invent на transport failure.
3. **Nearest / timeline** — glance timeline.
4. **Фокус дня** — один Daily Focus (`buildGlanceDailyFocus`): заголовок + направление (в приоритете / избегать) из `day_story`.

**Нет:** фактов Plot, why, карты/числа как identity на этом кадре в presentation Greeting; if/then практики на Greeting.

**Граница:** Glance не seed — сжимает согласованную модель, не генерирует заново.

---

## Экран 1 — Сюжет (Plot)

**Job:** откуда берётся тон дня — из реальных факторов, без обязательной драмы.

**На экране:**

1. **Визуал** (опц.) — привязан к внутренней классификации; ровный день → спокойный кадр, не драматический дефолт.
2. **Спина фактов — 0…2 строки.** Именованные факторы. Квоту не добиваем. Третий запрещён.
3. **`why_arose`** — только при сильной смысловой связи факт→тон; иначе omit (даже при ≥1 факте).
4. **`why_personal`** — только `profile_depth=deep`, не kitchen-natal; иначе omit.

**Нет:** явного тега типа динамики; обязательной пары `opposing_forces` как каркаса; карты/числа/цвета; сфер; if/then; цели; практик.

**`opposing_forces`:** один из возможных **исходов** данных, не обязательное поле. Пустой/omit, если нет двух разнонаправленных факторов. Не заполнять банком «ради драмы». Generation SoT: см. gap-план (`_opposing_forces` / `conflict_missing_opposing_forces`).

**Граница:** фраза Plot не вход для `link_to_conflict` / `serves_conflict` других модулей.

---

## Экран 2 — Символы (Symbols)

**Job:** ритуал раскрытия карты и числа, затем синтез символического поля.  
**Правило поверхности:** одна непрерывная лента — **раскрытое не пропадает**; B добавляется **ниже** A.

### A — ритуал (порядок фиксирован: карта → число)

На каждый хук после клика:

1. Identity (карта: имя · ориентация; число: значение · титул).
2. `base.meaning` (+ keywords) — статический lookup.
3. Сегодняшний слой = `bridge_to_day` (+ `personal_angle` только deep): трактовка + как может сказаться **сегодня**; не директива действия (Move). Отдельный `instruction` у карты/числа **не нужен**.
4. **Fail:** отдельный баннер/плашка. Никогда не склеивать с base/bridge.

**Нет в A:** цвет, apply, сферы, if/then.

### B — синтез (после раскрытия обоих хуков, под A)

1. Астрособытия (фаза Луны, ключевые транзиты) — сырые данные, не фраза Plot.
2. Glance timeline — **полный** вид (`label_short` + valence).

**Нет в B:** цвет; инструкции; повтор identity/base/bridge из A; сферы; if/then.

**Цвет:** не живёт в Symbols. Единственный дом — Move.  
Reveal API / prebake: [DAY_SYMBOL_REVEAL_CANON_V1](../audits/DAY_SYMBOL_REVEAL_CANON_V1.md) (карта/число; цвет-бандл с картой на API — presentation home = Move).

---

## Экран 3 — Чтение (Reading)

**Job:** подсветить, какая сфера сегодня реально значима — путеводитель, не гороскоп на все домены.

**Компакт:** до **2** доменов из 4 с реальным сигналом. Не добиваем «для полноты».

**Ровный день (0 сигналов):** короткий honest-текст «почему без острого фокуса» — тот же смысл, что на Glance; не пустой экран; не выдуманная сфера.

**Раскрытие по клику (поэтапно):**

1. Почему именно эта сфера сегодня (сырые данные домена).
2. Возможность → ловушка.

**Нет:** действие/рекомендация внутри сферы (**только Move**); цвет; карта/число; астро; timeline.

**Граница:** «почему сфера» не из фразы Plot и не копия другой сферы.

---

## Экран 4 — Действие (Move)

**Job:** ответ дня на действие целиком + цвет как практический якорь + одна ротируемая опора.

**Порядок сверху вниз:**

1. **Цвет дня (всегда):**
   - identity + base (имя, смысл каталога);
   - **интенсивность в UI:** «мягко» | «ярко» — видна пользователю и ведёт «как использовать»;
   - как использовать (с учётом интенсивности);
   - чего избегать (+ почему);
   - почему сегодня — сырые needs/факты, **не** seed Plot / `force_a|b`.
2. **If / then** на весь день: «сегодня сработает» / «сегодня лучше не» — один слой, не по сфере.
3. **Цель** — одно обещание.
4. **Опора** — один слот: практика **или** аффирмация (ротация по дню + пользователю); отметка сделал/прочитал.

**Нет:** действий внутри Reading; карты/числа/астро/timeline; сферных карточек; обязательной бинарности A/B как каркаса do/avoid.

**Граница:** Move не seed для Response.

---

## Экран 5 — Отклик (Response)

**Job:** быстрый чек-ин по ловушке сильнейшей сферы Reading.

**Два взаимоисключающих состояния:**

| Состояние | UI |
|-----------|-----|
| Есть ловушка | Вопрос с текстом ловушки сферы с **наибольшей магнитудой** ([DOMAIN_MAGNITUDE_V1](../foundation/DOMAIN_MAGNITUDE_V1.md)); три кнопки всегда: Обошёл / Попал / Не про это; короткое подтверждение записи |
| Нет ловушки | Только «Сегодня без острой ловушки» — **без тапа**; не подменять TodaySoftDayCheckIn |

**Нет:** кросс-сейл; повтор if/then/цвета/карты/числа/сфер; выдуманная ловушка.

**Граница:** ответ → accuracy/tap; домены = те же 4. Не переписывает Plot/Move.

---

## 1. Таймлайн

`favorable` / `caution`; различимый `label_short`.  
Компакт (nearest) — Glance. Полный вид — **Symbols·B** (не Move).

---

## 2. Условия приёмки

- [ ] Нет дословного/парафраз-повтора seed между актами.
- [ ] Plot без обязательного «A или B»; ровный день валиден.
- [ ] Symbols: карта→число; цвет отсутствует; fail = отдельный блок; B под A; раскрытое не пропадает.
- [ ] Reading: ≤2 сферы; без действия; поэтапное раскрытие.
- [ ] Move: цвет первым + интенсивность мягко/ярко; if/then глобально; одна опора (практика\|аффирмация).
- [ ] Response: магнитуда → одна ловушка; ровный = без тапа.
- [ ] Glance: текстура = тон; shared honest с Reading; без цвета.
- [ ] Свайп 390×844 + desktop.

---

## Architecture impact (v3.1 · 2026-08-03)

- **SoT before:** v3 (2026-07-31) — ScreenFlow jobs; conflict/`opposing_forces` as narrative spine; color bundled on Symbols; Reading = all scenes with action; Glance texture ≈ conflict label/why.
- **SoT after:** this document — per-act jobs above; no seed leakage; opposing_forces optional outcome; color house = Move only; Reading ≤2 + no action; Glance = tone synthesis.
- **Public contract changed?** yes (phased) — opposing_forces may omit; Reading domain ids → 4-way dictionary; color intensity field; presentation homes move. See tracker gap plan.
- **Migration required?** yes for generation gates + FE composition; no forced client version bump if additive/omit-tolerant.
- **Canon updated?** yes — this file · SCREEN_FLOW §4 · DAY_SYMBOL_REVEAL (color house) · tracker.
- **Backward compatible?** partial — old cached scenarios with forced A/B still render until regenerate; FE must tolerate omit.

---

## Changelog

### 2026-08-05 — v3.2 story deck presentation

- ScreenFlow cuts: Greeting → Energy+Flow → Symbols → Attributes → Practice → Insight → Close.
- Color presentation home → Attributes (data house unchanged).
- Reading not a separate swipe step; Close hosts trap tap + evening entry.
- Card face kept visible after pick on Symbols.
- **Photo vs theme frames:** Greeting / Energy+Flow / Practice = immersive photos (distinct pools); other steps = Day Atmosphere theme bg.
- **StoryBlockCue** vs **StoryNextAnchor:** within-step scroll vs next ScreenFlow step; never one component with modes.
- Multi-block orders: Energy (energy→flow); Symbols (card hero→number moment); Attributes (color→theme→focus→avoid); Insight (hero вывод→story→dialogue); Close (question→response→CTA, no foreshadow).

### 2026-08-04 — Glance: Daily Focus replaces sphere chips

- Экран 0: вместо ≤2 domain chips — один **Фокус дня** (title + prioritize/avoid) из `day_story` / Daily Focus model. Aligns V1 R15–R17; removes live «Сферы дня» chip pattern on product Glance. Dead `TodayLifeSpheresSection` deleted.
- Legacy `?experience=1` (`TodayExperienceSurface` day_synthesis): тот же `buildGlanceDailyFocus` + prioritize/avoid UI; tarot trap только заполняет пустой avoid.

### 2026-08-03 — Glance: drop ScreenFlow gauge (chrome owns progress)

- **Каркас Экран 0:** убран обязательный gauge «шаг N/6» в hero; прогресс = ScreenFlow chrome (точки + свайп; без ряда названий актов) — см. [SCREEN_FLOW_V1 §1.5](../foundation/SCREEN_FLOW_V1.md).
- Jobs смысла: texture / nearest / teaser / Daily Focus (supersedes ≤2 sphere chips).

### 2026-08-03 — v3.1b (concreteness)

§0.7–0.8: concreteness gate intent + ban on generation-meta leakage. Chorus bridges / number tempo / color note mash rewritten to lived tips; serve-heal markers extended.

### 2026-08-03 — v3.1

Semantic lock: Plot facts 0–2 · optional why · Symbols A/B surface · color→Move+intensity · Reading max-2 no action · Response magnitude trap · Glance tone · no seed leakage.

### 2026-07-31 — v3.0

Initial ScreenFlow content jobs after live audit.
