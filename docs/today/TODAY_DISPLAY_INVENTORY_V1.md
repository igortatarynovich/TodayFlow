# Today Display Inventory v1

**Status:** ACTIVE — **последний authority перед UI** на Сегодня  
**Version:** 1.1 (2026-08-29)  
**Грамматика (закон):** [DISPLAY_CONSTRUCTION_GRAMMAR_V1](../foundation/DISPLAY_CONSTRUCTION_GRAMMAR_V1.md)  
**Meaning SoT:** [TODAY_CONTENT_PIPELINE_V1](./TODAY_CONTENT_PIPELINE_V1.md)  
**Cycle SoT:** [TODAY_PRODUCT_FLOW_V1](./TODAY_PRODUCT_FLOW_V1.md)  
**Пара:** [PROFILE_DISPLAY_INVENTORY_V1](../profile/PROFILE_DISPLAY_INVENTORY_V1.md)

[TODAY_SCREEN_SCENARIO_V3](./TODAY_SCREEN_SCENARIO_V3.md) — **SUPERSEDED** как product map.

Слот вне этого файла **не существует**. FE не выбирает смысл и не заполняет пустое.

---

## Architecture impact

- **SoT before:** v1.0 named surfaces and budgets; headline vs focus anti-dupe was a note, not a role lock with allowed_inputs. Grammar duplicated here.
- **SoT after:** v1.1 — Grammar §3 records for every visible atom. `T3.headline` and `T3.focus_body` have different `one_question`; `why_personal` may feed **one** of them, not both. LLM cannot infer do/avoid inside `T1-hero.human_line`.
- **Public contract changed?** no JSON.
- **Migration required?** no. UI cutover waits.
- **Canon updated?** yes — this file · Grammar · Product Flow pointer · tracker.
- **Backward compatible?** yes for API.

---

## 0. Поверхности

```text
TODAY → RITUAL → MY DAY → EVENING
```

Evening в скролле только если `eveningMode || local hour is evening`.  
Guest: TODAY + RITUAL (catalog) + EVENING. **Все `T3.*` meaning omit.**

| Слой | persist_key |
|------|-------------|
| T1 Global | `GlobalDayKey` |
| T2 identity | `(owner, local_date)` |
| T2 catalog | catalog version |
| T2 lens / T3 meaning | `PersonalDayKey` |
| T4 | user gratitude record + manifest; **не** мутирует день |
| Chrome | copy + Inventory version |

---

## 1. Anti-dupe (роли)

| Group | Слоты | Правило |
|-------|-------|---------|
| `global_vs_personal` | все `T1-*` meaning · все `T3-*` meaning | natal/CE/card/number **не** во входах T1; T3 не переписывает energy/drivers/windows |
| `day_kind` | `T1-hero.human_line` · `T1-hero.energy_word` | line формулирует **уже выбранную** энергию, не новую |
| `personal_split` | `T3.headline` · `T3.focus_title` · `T3.focus_body` | три вопроса; **один** source не кормит headline и focus_body |
| `do_layers` | `T1-strength.chip` · `T3.priority` | Global типы действий ≠ персональные пункты |
| `risk_layers` | `T1-risk.chip` · `T3.caution` | Global risk ≠ personal caution |
| `symbol_layers` | `T2.catalog_*` · `T2.lens_*` | учебник ≠ «день такой из-за карты» |
| `focus_vs_priority` | `T3.focus_body` · `T3.priority` | внимание/где ≠ конкретный do-список |

Proposition test: тот же, что Profile (Jaccard / substring).

**Source exclusivity:** `why_personal` → максимум одна роль из `{T3.headline, T3.focus_body}`. Замок: `why_personal` = вход **только** `T3.focus_body`. Headline = `day_personal.summary_ru` или personal conflict thesis — **не** `why_personal`.

---

## 2. Индекс слотов

| slot_id | one_question / role | class | authority |
|---------|---------------------|-------|-----------|
| `T1-date.eyebrow` | chrome | chrome | product |
| `T1-date.title` | Какая календарная дата? | calc | local_date |
| `T1-hero.moon` | Фаза как объект неба | calc | moon illumination |
| `T1-hero.eyebrow` | chrome | chrome | product |
| `T1-hero.energy_word` | Какая главная энергия дня (8-set)? | calc | Global Day Engine |
| `T1-hero.energy_pct` | Какая интенсивность этой энергии? | calc | energy_scores |
| `T1-hero.mood` | Какое настроение (тот же 8-set, другая метрика)? | calc | Engine mood / visual_mode |
| `T1-hero.human_line` | Каков уже выбранный общий день по-человечески? | generated | Global narrative |
| `T1-hero.sheet` | Тот же смысл глубже | projected | same as human_line + expect |
| `T1-clock.label` | chrome | chrome | product |
| `T1-clock.range` | Какое окно дня по часам? | calc | windows[] |
| `T1-clock.spectrum` | Где окно на шкале 06–24? | calc | window start |
| `T1-clock.transit` | Какие 1–3 влияния + Луна? | calc+fact | ranked drivers |
| `T1-clock.sheet` | Почему этот драйвер в ранге? | calc | driver + energy link |
| `T1-strength.label` | chrome | chrome | product |
| `T1-strength.chip` | Какие типы действий день поддерживает? | calc | Global strength[] |
| `T1-strength.sheet` | Почему этот тип? | calc/generated | drivers of that type |
| `T1-risk.label` | chrome | chrome | product |
| `T1-risk.chip` | Какие типы действий в риске? | calc | Global risk[] |
| `T1-risk.sheet` | Почему этот риск? | calc/generated | drivers |
| `SF.next.*` | Куда листаем? | chrome | ScreenFlow |
| `T2-gate.card_*` | chrome входа | chrome | product |
| `T2-gate.number_*` | chrome входа | chrome | product |
| `T2.card_face` | Какая карта (id+orientation)? | calc | Ritual Engine |
| `T2.number_glyph` | Какое число? | calc | Numerology Engine |
| `T2.catalog_card` | Что карта значит в каталоге? | catalog | tarot catalog |
| `T2.catalog_number` | Что число значит в каталоге? | catalog | number catalog |
| `T2.lens_card` | Как карта окрашивает уже посчитанный Personal Day? | generated | Personal × card |
| `T2.lens_number` | Как число окрашивает уже посчитанный Personal Day? | generated | Personal × number |
| `T3.unavailable` | Meaning не загрузился? | chrome | product |
| `T3.headline` | Что главное **лично для меня** сегодня? | generated | Personal Day |
| `T3.focus_label` | chrome | chrome | product |
| `T3.focus_title` | Какая одна тема внимания? | generated | Personal focus |
| `T3.focus_body` | Где это проявится и на что направить внимание? | generated | Personal (why_personal first) |
| `T3.priority_label` | chrome | chrome | product |
| `T3.priority` | Что конкретно сделать? | generated | Personal do[] |
| `T3.caution_label` | chrome | chrome | product |
| `T3.caution` | Где персональный риск? | generated | Personal avoid[] |
| `T3.rhythm_label` | chrome | chrome | product |
| `T3.rhythm_row` | Когда по часам support/caution? | calc | natal×windows or Global windows |
| `T3.color.*` | Какой цвет как опора дня? | catalog+fill | color scoring |
| `T3.practice` | Какая одна практика? | catalog | Personal focus/risk |
| `T3.affirmation` | Какая аффирмация дня? | generated | Personal |
| `T3.action` | Какой один выполнимый шаг? | generated | Personal |
| `T3.tracker` | Что я уже веду? | user | habits |
| `T3.tasks_empty` | chrome empty | chrome | product |
| `T3.depth` | Углубить выбранную тему? | generated | depth layer |
| `T4.title` | chrome вопроса | chrome | product |
| `T4.lead` | chrome | chrome | product |
| `T4.category` | chrome 5 категорий | chrome | product |
| `T4.text` | Свои слова благодарности | user | user |
| `T4.save_*` | chrome | chrome | product |
| `TF.no_connection` | сеть | chrome | shared |
| `TF.unavailable` | flagged | chrome | shared |

---

## 3. Записи слотов

### 3.1 Shared failure

`TF.no_connection` · `TF.unavailable` — те же записи, что в Profile Inventory. На MY DAY unavailable meaning → **только** `T3.unavailable`, не смесь leftover color/timeline.

#### `T3.unavailable`

| | |
|---|---|
| surface | my_day |
| one_question | Персональный смысл дня недоступен? |
| text_class | chrome |
| display_source | «Не удалось загрузить.» |
| budget | 3 слова |
| required | да, если `interpretation_status=unavailable` |
| empty_behavior | этот слот **вместо** T3 meaning |
| may_fe_transform | none |
| forbidden | leftover conflict.short_name, catalog color, independent day_facts clock |
| omit_also | T3.headline…depth, T3.color, natal rhythm |
| persist_key | n/a |
| anti_dupe_group | `failure` |

T1 Global Engine profile **может** остаться на TODAY.

---

### 3.2 T1 TODAY — Global

Capability: все глубины, включая guest.

#### `T1-date.eyebrow` / `T1-date.title`

Chrome «Сегодня» · calc formatted local date. one_question title: какая дата. budget 1 строка. `may_fe_transform`: locale format only.

#### `T1-hero.moon`

| | |
|---|---|
| one_question | Как выглядит Луна сегодня (объект, не мини-иконка в списке)? |
| text_class | calc |
| authority | Day Sources / lunar |
| semantic_source | illumination / phase |
| display_source | `DsCelestialMoon` ~40% bleed |
| allowed_inputs | moon phase geometry |
| forbidden_inference | вторая мини-луна в transit row **как дубль объекта** (row Луны как влияние — отдельный `T1-clock.transit` id=moon, не второй backdrop) |
| output | visual |
| required | нет (omit если нет phase) |
| empty_behavior | omit backdrop |
| may_fe_transform | none |
| persist_key | GlobalDayKey |
| anti_dupe_group | `global_sky` |

#### `T1-hero.eyebrow`

Chrome «Энергия дня».

#### `T1-hero.energy_word`

| | |
|---|---|
| one_question | **Какая главная энергия общего дня?** |
| text_class | calc |
| authority | Global Day Engine |
| semantic_source | `primary_energy` closed 8-set |
| display_source | `DAY_MODE_LABELS_RU` map |
| allowed_inputs | Engine primary_energy only |
| forbidden_inference | LLM chooses mood; natal; card; number |
| output | 1 слово: Заземление · Поток · Сияние · Импульс · Ясность · Напряжение · Обновление · Глубина |
| budget | 1 слово |
| required | да, если Engine дал set member |
| empty_behavior | omit word; не invent |
| may_fe_transform | map_label |
| may_llm_add_meaning | нет |
| persist_key | GlobalDayKey |
| anti_dupe_group | `day_kind` |

#### `T1-hero.energy_pct`

| | |
|---|---|
| one_question | Насколько сильна **эта** энергия? |
| text_class | calc |
| authority | Global Day Engine |
| semantic_source | `energy_scores[primary_energy]` |
| display_source | `round(*100)%` |
| allowed_inputs | that score |
| forbidden_inference | invent % |
| output | 2–3 digits + % |
| required | нет |
| empty_behavior | omit metric |
| may_fe_transform | none |
| persist_key | GlobalDayKey |
| anti_dupe_group | `day_kind` |

#### `T1-hero.mood`

| | |
|---|---|
| one_question | Какое настроение дня (отдельная метрика 8-set)? |
| text_class | calc |
| authority | Engine |
| allowed_inputs | mood / visual_mode if distinct |
| forbidden_inference | подмена energy_word |
| output | 1 слово map_label |
| required | нет |
| empty_behavior | omit |
| persist_key | GlobalDayKey |

#### `T1-hero.human_line`

| | |
|---|---|
| one_question | **Каков уже выбранный общий день на человеческом языке?** |
| text_class | generated |
| authority | Global Day (Engine decided energy/drivers; LLM формулирует) |
| semantic_source | persisted Global prose (atmosphere / essence / expect — **одна** линия после composition) |
| display_source | `atmosphereLine` / hero body |
| allowed_inputs | `primary_energy`, ranked driver **facts** (not natal), moon phase/sign as climate, windows as **time facts** |
| forbidden_inference | natal · CE · card · number · goals · **do/avoid advice** («избегай разговоров») · personal overlay · sphere horoscope · новая энергия |
| output | 1 предложение |
| budget | 12–22 слов · **≤160 chars** |
| required | нет |
| empty_behavior | omit line (energy_word может остаться) |
| may_fe_transform | clip |
| may_llm_add_meaning | **нет** |
| interaction | tap → `T1-hero.sheet` (тот же вопрос) |
| forbidden | см. inference |
| why_here | Recognition общего дня |
| persist_key | GlobalDayKey + global narrative version |
| anti_dupe_group | `day_kind` · `global_vs_personal` |

#### `T1-hero.sheet`

Projected same slot family. Inputs: line + expect + atmosphereNote + energyCause **уже из Global**. Budget 2–4 предложения, каждый кусок ≤160–320. `forbidden_inference`: new meaning. Interaction: overlay close. `anti_dupe_group`: `day_kind`.

#### `T1-clock.label` · spectrum chrome `06:00` / `24:00`

Chrome.

#### `T1-clock.range`

| | |
|---|---|
| one_question | Когда главное окно общего дня? |
| text_class | calc |
| authority | Global Day Engine windows[] |
| allowed_inputs | window start–end (peak intensity → next timed clock) |
| forbidden_inference | invent +90 мин; personal natal clocks |
| output | `HH:MM–HH:MM` |
| required | нет |
| empty_behavior | one clock → omit range, not invent; no windows → omit card |
| persist_key | GlobalDayKey |
| anti_dupe_group | `global_sky` |

#### `T1-clock.spectrum`

Calc visual of start on 06:00–24:00. omit without range/start.

#### `T1-clock.transit`

| | |
|---|---|
| one_question | Какие влияния неба ранжированы для этого дня? |
| text_class | calc + generated `fact_ru` (формулировка факта драйвера, не новая rank) |
| authority | Engine ranking |
| semantic_source | moon row + ranked drivers **1–3** |
| allowed_inputs | driver_id, fact_ru, optional window time |
| forbidden_inference | 4th driver; natal activation; card |
| output | list row: name + optional time + fact |
| budget | fact ≤120 chars · **count ≤1 moon + 3 drivers** |
| required | нет |
| empty_behavior | omit row / omit list |
| may_fe_transform | clip fact |
| may_llm_add_meaning | нет (не меняет rank) |
| interaction | tap → `T1-clock.sheet` |
| persist_key | GlobalDayKey |
| anti_dupe_group | `global_sky` |

Untitled window without driver fact → omit.

#### `T1-clock.sheet`

| | |
|---|---|
| one_question | Почему этот драйвер в ранге и как связан с энергией? |
| text_class | calc |
| allowed_inputs | event, time, canonical IL meaning of **that** fact, rank reason, energy link |
| forbidden_inference | personal «для тебя»; ephemeris dump |
| output | 4–8 rows · value 1 предложение |
| empty_behavior | omit extra rows |
| anti_dupe_group | `global_sky` |

#### `T1-strength.label` / `T1-risk.label`

Chrome: «Сегодня поддерживает» · «Риски».

#### `T1-strength.chip`

| | |
|---|---|
| one_question | Какие **типы действий** общий день поддерживает? |
| text_class | calc |
| authority | Global Day Engine `strength[]` |
| display_source | `GLOBAL_ACTION_TYPE_LABELS_RU` |
| allowed_inputs | Engine strength types |
| forbidden_inference | life spheres; personal do; LLM new type |
| output | chips |
| budget | **≤4** · 1–3 слова · ≤24 chars |
| required | нет |
| empty_behavior | omit cluster |
| may_fe_transform | map_label |
| interaction | tap → `T1-strength.sheet` |
| persist_key | GlobalDayKey |
| anti_dupe_group | `do_layers` |

#### `T1-risk.chip`

Как strength; `risk[]`; **≤3** chips; `anti_dupe_group`: `risk_layers`.

#### `T1-strength.sheet` / `T1-risk.sheet`

Why this type, which drivers, typical manifestation **global**. 2–4 предложения. No personal caution copy. `may_llm_add_meaning`: нет сверх Engine type.

#### `SF.next.*`

Chrome ScreenFlow: Дальше / Ритуал / Мой день / Вечер + hints из Inventory (`dayHint`, `ritualsHint`, `myDayHint`, `eveningHint`).  
**Нет слотов** для orientation / promise / trap-as-step / «Поток дня» как шаг.  
`may_fe_transform`: hide_by_gate (no evening → no evening label).

---

### 3.3 T2 RITUAL

Does not recompute Global/Personal.

#### `T2-gate.card_title` / `.card_body` / `.number_title` / `.number_body` / `.step`

Chrome. Card open CTA · 1–2 предл. ≤220 / ≤180. States A/B only. `one_question`: как войти в символ, не какой день.

#### `T2.card_face`

| | |
|---|---|
| one_question | Какая карта зафиксирована на сегодня? |
| text_class | calc |
| authority | Ritual Engine |
| allowed_inputs | card id + orientation · identity (owner, date) |
| forbidden_inference | change Global energy; second pick after lock |
| output | face visual |
| persist_key | (owner, local_date) |
| anti_dupe_group | `symbol_layers` |

#### `T2.number_glyph`

Numerology Engine identity. 1–2 digits / title. Same persist. Appear state B→C after card open (product flow).

#### `T2.catalog_card` / `T2.catalog_number`

| | |
|---|---|
| one_question | **Что символ значит в каталоге?** |
| text_class | catalog |
| authority | catalogs |
| allowed_inputs | catalog base meaning for that id |
| forbidden_inference | «ты сегодня»; rewrite Personal/Global |
| output | 2–4 предложения |
| budget | 40–70 слов · ≤420 chars |
| required | нет |
| empty_behavior | omit catalog block in sheet |
| may_fe_transform | none |
| persist_key | catalog version + id |
| anti_dupe_group | `symbol_layers` |
| interaction | sheet section «Значение» |

#### `T2.lens_card` / `T2.lens_number`

| | |
|---|---|
| one_question | **Как символ окрашивает уже посчитанный Personal Day?** |
| text_class | generated |
| authority | Personal Day × symbol (lens); **не** Ritual как day engine |
| semantic_source | hook_reveal `bridge_to_day` / `personal_angle` |
| allowed_inputs | persisted Personal Day meaning + this symbol identity + catalog as *color*, not cause |
| forbidden_inference | «день такой потому что карта/число»; mutate energy/drivers/windows; invent lens on empty persist |
| output | 1–3 предложения |
| budget | 20–45 слов · ≤280 chars |
| required | нет |
| empty_behavior | omit «Для тебя сегодня» |
| may_fe_transform | clip |
| may_llm_add_meaning | нет |
| persist_key | PersonalDayKey + ritual identity |
| anti_dupe_group | `symbol_layers` · `global_vs_personal` |
| interaction | sheet section after catalog |
| appear | guest: omit personal lens (catalog only) |

---

### 3.4 T3 MY DAY — Personal

Capability: light/deep. Guest/general: **no T3 meaning slots**.

#### `T3.headline`

| | |
|---|---|
| one_question | **Что главное лично для меня сегодня?** |
| text_class | generated |
| authority | Personal Day |
| semantic_source | `day_personal.summary_ru` **или** personal conflict thesis |
| display_source | `TodayMyDayPane` headline |
| allowed_inputs | Personal overlay over **locked** Global; CE as context not rewrite of Global |
| forbidden_inference | `why_personal` (это `T3.focus_body`); Global expect as «моё»; card/number as cause; copy of `T1-hero.human_line` |
| output | 1 мысль |
| budget | 12–20 слов · ≤180 chars |
| required | нет |
| empty_behavior | omit card |
| may_fe_transform | clip; **drop if overlaps focus_body** (substring ≥24 / Jaccard) |
| may_llm_add_meaning | нет |
| persist_key | PersonalDayKey |
| anti_dupe_group | `personal_split` · `global_vs_personal` |

Code that sets headline = `why_personal` = **drift**.

#### `T3.focus_label`

Chrome callout.

#### `T3.focus_title`

| | |
|---|---|
| one_question | Какая **одна тема** внимания? |
| text_class | generated |
| authority | Personal Day / Daily Focus title |
| allowed_inputs | personal theme slot |
| forbidden_inference | Global energy word as title; kitchen `short_name` |
| output | 3–8 слов |
| budget | ≤72 chars |
| required | нет |
| empty_behavior | omit title (body may stand with chrome label) |
| persist_key | PersonalDayKey |
| anti_dupe_group | `personal_split` |

#### `T3.focus_body`

| | |
|---|---|
| one_question | **Где это проявится и на что направить внимание?** |
| text_class | generated |
| authority | Personal Day |
| semantic_source | first live: `why_personal` → natal transit story → `personal_astrology.summary_ru` → `development_point` |
| display_source | instruction bridge |
| allowed_inputs | those fields only, already personal |
| forbidden_inference | rewrite `primary_energy`; copy T1 human_line; card/number cause; fill from Global strength chips |
| output | 1–2 предложения |
| budget | 18–35 слов · ≤220 chars |
| required | нет |
| empty_behavior | omit body |
| may_fe_transform | clip |
| may_llm_add_meaning | нет |
| persist_key | PersonalDayKey |
| anti_dupe_group | `personal_split` · `focus_vs_priority` |

#### `T3.priority_label` / `T3.caution_label`

Chrome: «В приоритете» · «Осторожнее».

#### `T3.priority`

| | |
|---|---|
| one_question | **Что конкретно сделать?** |
| text_class | generated |
| authority | Personal Day `do[]` |
| allowed_inputs | Personal do (action/object/moment) |
| forbidden_inference | copy T1-strength chip labels; abstract noun-pairs; Global do |
| output | list items |
| budget | **1–3** · each 8–16 слов · ≤200 chars |
| required | нет |
| empty_behavior | omit section |
| may_fe_transform | clip; count cap |
| persist_key | PersonalDayKey |
| anti_dupe_group | `do_layers` · `focus_vs_priority` |

Fallback to glance `prioritize` only if `do[]` empty **and** that string is personal, not Global chip.

#### `T3.caution`

| | |
|---|---|
| one_question | **Где персональный риск?** |
| text_class | generated |
| authority | Personal Day `avoid[]` |
| allowed_inputs | Personal avoid |
| forbidden_inference | copy T1-risk chips; exact duplicate of a priority item |
| output | list items |
| budget | **1–2** · each 1 предл. · ≤180 chars |
| required | нет |
| empty_behavior | omit section |
| may_fe_transform | clip; filter dupe vs priority |
| persist_key | PersonalDayKey |
| anti_dupe_group | `risk_layers` |

#### `T3.rhythm_label`

Chrome: «Мой ритм дня» если natal clocks; иначе «Ритм дня».

#### `T3.rhythm_row`

| | |
|---|---|
| one_question | Когда сегодня support/caution по часам? |
| text_class | calc |
| authority | natal activations × Engine windows **или** Global windows × fact_ru |
| allowed_inputs | timed rows from that rule |
| forbidden_inference | invent clocks; aspect jargon; show on T1; show if T3.unavailable |
| output | ≤5 timed rows · label lived use ≤72 chars |
| required | нет |
| empty_behavior | omit whole rhythm |
| persist_key | PersonalDayKey / GlobalDayKey for fallback clock |
| anti_dupe_group | `global_vs_personal` (label must not claim «мой» on Global fallback) |

#### `T3.color.name` / `.hex` / `.lines`

| | |
|---|---|
| one_question | Какой один цвет как опора **после** energy+risk+personal focus? |
| text_class | catalog hex + generated/catalog prose fill-empty |
| authority | color scoring (LLM **не** выбирает цвет) |
| allowed_inputs | BE `color_guide` nest |
| forbidden_inference | FE color dictionary; catalog morning color when unavailable |
| output | name 1–3 слова · 3–6 short lines ≤80 chars |
| required | нет |
| empty_behavior | omit card if nest null |
| persist_key | PersonalDayKey / color nest |
| anti_dupe_group | `enrichment` |

#### `T3.practice`

Max **one**. Catalog item from Personal Focus or compensating Personal Risk. Title ≤48 · why 1 предл. ≤160. omit otherwise. LLM does not pick. `anti_dupe_group`: `enrichment`.

#### `T3.affirmation`

Generated from Personal. 1 предл. ≤140. Not practice bucket. omit if empty.

#### `T3.action`

One doable step from Personal. 1 предл. ≤140. omit if empty.

#### `T3.tracker`

User habits already in progress. Facts, not meaning. Not inputs to energy/drivers. appear if user has rows.

#### `T3.tasks_empty`

Chrome «Сегодня без отдельного задания.» when today-tasks count 0. Not invent a task.

Today-tasks cap: **≤2** one-off + daily streak block separately.

#### `T3.depth`

| | |
|---|---|
| one_question | Хочу ли я глубже **выбранную** тему поверх уже полезного дня? |
| text_class | generated (Trial/Paid) / chrome CTA (Free) |
| authority | depth layer; user picks topic |
| allowed_inputs | base day unchanged + topic pack |
| forbidden_inference | second competing day plot; lock base chapters |
| required | нет |
| empty_behavior | omit / CTA |
| persist_key | depth generation key |
| anti_dupe_group | `depth` |

---

### 3.5 T4 EVENING

#### `T4.title` / `T4.lead`

Chrome: «За что ты благодарен сегодняшнему дню?» · «Выбери, что откликается — или напиши своё.»  
one_question title: единственный evening question.  
`may_fe_transform`: hide_by_gate (time).

#### `T4.category`

| | |
|---|---|
| one_question | Какая предложенная опора благодарности? |
| text_class | chrome |
| semantic_source | 5 ids: people · work · quiet · fresh · self |
| output | 2–5 слов each |
| required | нет (user may text-only) |
| empty_behavior | n/a |
| forbidden | trap-check, promise, mood as evening job |
| persist_key | chrome |
| anti_dupe_group | `gratitude` |

#### `T4.text`

| | |
|---|---|
| one_question | Что я хочу сказать своими словами? |
| text_class | user |
| allowed_inputs | user |
| forbidden_inference | rewrite Global/Personal day from this text |
| budget | field ≤500 · persist body ≤2000 |
| required | нет (categories suffice) |
| empty_behavior | omit persist if both empty |
| persist_key | gratitude record + date + manifest |
| anti_dupe_group | `gratitude` |

#### `T4.save` / `T4.saved`

Chrome. Save allowed if ≥1 category **or** text.

**Forbidden evening slots:** trap-check, «Принимаю» manifesto, «Идти в сон» as forecast job, promise-as-meaning.

---

### 3.6 First Today

Not a fifth surface. Reaction chips = `user` into Personal Model. Then same T1–T4 with capability. No second Global Day.

---

## 4. Вне рамки

Orientation step · SCENARIO_V3 six blocks · DomainLens as required dashboard · promise/trap evening · FE color/calm invent · Personal Timeline on T1 · card as cause of energy% · `storyNext` dead keys.

---

## 5. Код vs замок

| Код | Замок |
|-----|-------|
| `TodayDayBrief` orientation pane | нет шага; не наращивать |
| headline = `why_personal` | `T3.headline` ≠ that source |
| `storyNext` deprecated keys | нет slot_id |
| loop/promise copy | нет T4 meaning |
| guide LLM overlay VM | не authority T1 chips |

---

## 6. Трасса (пример)

```text
«День просит не спешить с резкими жестами.»
  → T1-hero.human_line
  → generated
  → persisted Global prose
  → Global Day Engine (primary_energy already grounded)
  → allowed: energy + ranked sky facts; forbidden: natal / do-advice / card
  → GlobalDayKey + narrative version
  → FE clip ≤160; tap sheet = same slot
```

```text
«Сложный разговор лучше назвать до вечера.»
  → T3.focus_body  (NOT T3.headline)
  → generated
  → why_personal
  → Personal Day overlay
  → PersonalDayKey
  → clip ≤220; must not equal headline
```

---

## Changelog

| Date | Change |
|------|--------|
| 2026-08-29 | v1.0 — первый закрытый список |
| 2026-08-29 | v1.1 — Grammar records; why_personal exclusivity; human_line forbidden_inference; persist keys; anti_dupe groups |
