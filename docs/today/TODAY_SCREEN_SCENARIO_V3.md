# Today — сценарий страницы (v3.1)

**Status:** ACTIVE · **Locked 2026-08-03** (semantic design pass on `design/profile-journey-premium`)

Контекст: ScreenFlow (Glance → Plot → Symbols → Reading → Move → Response).  
Навигация: Glance = шаг 0 (читают первым). Проектирование спеки шло от содержания к сводке.

Связанные каноны: [SCREEN_FLOW_V1.md](../foundation/SCREEN_FLOW_V1.md) · [TODAY_WAVE2_CONTRACT_V1.md](./TODAY_WAVE2_CONTRACT_V1.md) · [DAY_SYMBOL_REVEAL_CANON_V1.md](../audits/DAY_SYMBOL_REVEAL_CANON_V1.md) · [DOMAIN_MAGNITUDE_V1.md](../foundation/DOMAIN_MAGNITUDE_V1.md)

---

## 0. Сквозные правила

1. **Экран = одна задача.** Свайп = продолжение.
2. **Один дом на сущность.** Цвет — только Move. Карта/число/астро — Symbols. Действие дня — только Move. Ловушка-тап — только Response.
3. **No seed leakage.** Каждый акт формулирует текст из **своих** сырых данных. Ни один акт не является источником текста для другого. Дословный или перефразированный повтор чужой формулировки = **баг генерации**, не «сквозная персонализация».
4. **Внутренняя классификация динамики** (`напряжение | усиление | доминанта | ровный день`) управляет тоном формулировок и выбором визуала. **Не** рендерится ярлыком на UI.
5. **Честный omit.** Нет сигнала → не выдумывать конфликт / сферу / ловушку / связку «ради заполнения».
6. **Домены Reading/Response/Glance chips:** четыре — `work` · `money` · `relationships` · `energy`. Wire DomainLens = тот же словарь (legacy `money_work`/`family` — только read-compat).
7. **Конкретность.** User-facing строка называет действие, объект или момент («три вдоха до „отправить“», «одна фраза вместо трёх») — иначе **omit**. Абстрактные пары существительных («ясность в трении») и дампы тегов через тире («темп — …, способ — …») = баг генерации.
8. **No generation-meta leakage.** Внутренние правила пайплайна («не второй сюжет», «не отдельный прогноз», «без параллельного сюжета», «связывает фактор с тоном») **никогда** не попадают в user-facing текст — симметрично seed-leak, другой класс утечки.

---

## Экран 0 — Сводка (Glance)

**Job:** за 2 секунды ориентация и вход дальше — сжатая проекция уже определённых актов, не отдельный сюжет.

**Каркас показа (Day Atmosphere surface — FOUNDATION_UI §11.9):** full-bleed фон/декор по `day_atmosphere.visual_mode` · стеклянная hero-карточка · gauge прогресса ScreenFlow (текущий акт / 6, не «score дня») · sparse chrome. Jobs смысла ниже **не** меняются — только композиция.

**На экране:**

1. **Текстура** — 1–2 предложения в glass hero: фраза-синтез **тона** (внутренняя классификация). Не факты, не ярлык категории, не `short_name` «A или B».
2. **ScreenFlow gauge** — прогресс актов (шаг 0…5 из 6). Не выдуманный балл дня.
3. **Nearest** — одно событие glance timeline (`label_short` + valence).
4. **Тизер ритуала** — один CTA в Symbols·A без identity/base/bridge на Glance.
5. **Индикатор сфер** (опц., secondary) — до 2 чипов из Reading; если без сигнала — shared honest-текст с Reading. Не конкурирует с texture в hero.

**Нет:** фактов Plot, why, карты/числа/астро/полного timeline, **цвета дня как контент-блока** (атмосфера = shell, не «цвет дня» слот), if/then, цели, практики, ловушки Response.

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

### 2026-08-03 — v3.1b (concreteness)

§0.7–0.8: concreteness gate intent + ban on generation-meta leakage. Chorus bridges / number tempo / color note mash rewritten to lived tips; serve-heal markers extended.

### 2026-08-03 — v3.1

Semantic lock: Plot facts 0–2 · optional why · Symbols A/B surface · color→Move+intensity · Reading max-2 no action · Response magnitude trap · Glance tone · no seed leakage.

### 2026-07-31 — v3.0

Initial ScreenFlow content jobs after live audit.
