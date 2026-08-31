# Profile Display Inventory v1

**Status:** ACTIVE — **последний authority перед UI** на `/profile`  
**Version:** 1.2 (2026-08-29)  
**Грамматика (закон):** [DISPLAY_CONSTRUCTION_GRAMMAR_V1](../foundation/DISPLAY_CONSTRUCTION_GRAMMAR_V1.md)  
**Пара:** [TODAY_DISPLAY_INVENTORY_V1](../today/TODAY_DISPLAY_INVENTORY_V1.md)

**Не заменяет:** Character Engine · Surface Canon (чувства шагов) · Journey Forms (образцы) · Content Canon (pipeline).

Слот вне этого файла **не существует**. FE не выбирает смысл и не заполняет пустое.

---

## Architecture impact

- **SoT before:** v1.1 records existed, but `P3.help` and `P3.node_title` sat in `path_new_value`, so Jaccard would treat the designed Effort projection as a dupe. Bridge empty_behavior was unresolved prose.
- **SoT after:** v1.2 — path_new_value is only the four path propositions (recognition · insight · effort · bridge). Help is node-internal; Effort may project from it. Explore stays off-path. Audit vs Grammar §5 in §7.
- **Public contract changed?** no JSON.
- **Migration required?** no. UI cutover: Character warehouse off the path; P4 spheres 0–2; leftover styles in Explore.
- **Canon updated?** yes — this file · Grammar §5 · tracker.
- **Backward compatible?** yes for API.

---

## 0. Поверхность

```text
Recognition → Why → Insight → Effort → Bridge
```

Explore — склад и глубина **рядом**, не шестой акт пути. Нет акта «Портрет» на скролле.

Путь (закрыт, Grammar §5): Кто я? → Почему это про меня? → Что я раньше не замечал? → Куда направить усилие? → Почему имеет смысл посмотреть сегодняшний контекст?

Journey acceptance: [DISPLAY_CONSTRUCTION_GRAMMAR_V1](../foundation/DISPLAY_CONSTRUCTION_GRAMMAR_V1.md) §5.2.

Conditional: `P-forming` · `P-data`.

**Persist meaning:** `(user_id, profile_hash)` + prompt/projection version.  
**Chrome persist:** copy keys + Inventory version.

---

## 1. Anti-dupe (роли, не длины)

| Group | Слоты | Правило |
|-------|-------|---------|
| `identity_axis` | `P1.recognition_line` · `P1.identity_core` | core = раскрытие той же оси; не новый тезис |
| `path_new_value` | `P1.recognition_line` · `P3.insight` · `P4.effort_vector` · `P5.bridge_line` | **четыре разных вопроса**; перефраз = дефект. **Не** title узла, **не** help |
| `why_not_hero` | `P1.*` · `P2.anchor.*` | факты карты не живут в герое |
| `node_heading` | `P3.node_title` · `P3.insight` | title называет узел; insight = новая закономерность, не второй заголовок |
| `node_help` | `P3.help` · `P3.insight` | help ≠ пересказ insight; Effort **может** проецироваться из help (тот же source, другой вопрос) |
| `node_not_warehouse` | `P3.*` · (запрещённый Character act) · `P6.detail` | материалы узла не дублируются списком сил на скролле |
| `effort_not_mission` | `P4.effort_vector` · `life_mission` | mission не заменяет вектор |
| `bridge_not_effort` | `P4.effort_vector` · `P5.bridge_line` | мост ≠ императив «что делать» |
| `effort_where` | `P4.effort_vector` · `P4.sphere.*` | сфера = где, не второй вектор |

Проверка proposition: нормализовать строки; Jaccard ≥ 0.72 или substring ≥24 = дубль роли.

---

## 2. Индекс слотов

| slot_id | one_question / role | class | authority |
|---------|---------------------|-------|-----------|
| `P-forming.message` | Что уже читается, пока ядро не ready? | chrome | product chrome |
| `P-data.cta_text` | Чего не хватает *мне*, чтобы открылась точность? | chrome | capability |
| `P-data.button` | Куда идти править факты? | chrome | product chrome |
| `P1.visual` | Какой образ ядра? | catalog | life_path → seed → asset |
| `P1.recognition_name` | Как называется ядро? | calc | life_path → archetype |
| `P1.recognition_line` | Кто я как наблюдаемый механизм? | generated | Character Engine / identity funnel |
| `P1.signal` | Есть ли раскрытие той же оси? | chrome | product chrome |
| `P1.identity_core` | Та же ось чуть шире (disclosure)? | generated | CE identity |
| `P2.step_title` | chrome шага | chrome | product chrome |
| `P2.selected_section` | chrome | chrome | product chrome |
| `P2.selected_life_path` | Что **выбрало имя**? | calc | numerology life_path |
| `P2.influenced_section` | chrome | chrome | product chrome |
| `P2.anchor.sun` | Как Солнце расширяет *этот* портрет? | calc+bank | natal sun |
| `P2.anchor.element` | Как стихия расширяет портрет? | calc+bank | sun element |
| `P2.anchor.rhythm` | Какой ритм baseline? | calc | baseline.rhythm_style |
| `P2.anchor.moon` | Как Луна расширяет портрет? | calc+bank | natal moon |
| `P2.anchor.asc` | Как ASC расширяет внешнее проявление? | calc+bank | rising |
| `P2.anchor.mc` | Как MC расширяет направление? | calc+bank | MC |
| `P2.honesty_no_time` | Чего ещё нет без времени? | chrome | product chrome |
| `P2.expand_hint` | chrome tap | chrome | product chrome |
| `P3.step_title` | chrome | chrome | product chrome |
| `P3.eyebrow` | chrome kind | chrome | product chrome |
| `P3.node_title` | Как назвать эту закономерность? | generated | CE / contract materials |
| `P3.insight` | Какую ловушку/дар я раньше не называл? | generated | CE cascade → node |
| `P3.grounded_label` | chrome | chrome | product chrome |
| `P3.grounded_on` | На каких **фактах** держится узел? | calc | subset of P2 facts |
| `P3.help_label` | chrome | chrome | product chrome |
| `P3.help` | Что помогает внутри этой оси (не день)? | generated | node.help / strengths |
| `P3.living_label` | chrome | chrome | product chrome |
| `P3.living_note` | chrome честности | chrome | product chrome |
| `P3.living_evidence` | Как это уже проявлялось в отметках? | user | living notes |
| `P4.step_title` | chrome | chrome | product chrome |
| `P4.lead` | chrome | chrome | product chrome |
| `P4.effort_vector` | Куда прикладывать усилие в поведении? | projected | nodes[0].help only |
| `P4.sphere.title` | Где (ярлык сферы)? | chrome/catalog | sphere id |
| `P4.sphere.teaser` | Где это сильнее (одна грань)? | generated | life_spheres |
| `P4.sphere.expand` | Как / нужно / риск в этой сфере? | generated | life_spheres fields |
| `P5.step_title` | chrome | chrome | product chrome |
| `P5.bridge_line` | Почему сейчас открыть Today? | projected | node.kind pack |
| `P5.cta` | chrome navigate | chrome | product chrome |
| `P6.title` | chrome | chrome | product chrome |
| `P6.wheel` | Как выглядит карта? | calc | natal preview |
| `P6.numbers` | Какие числа? | calc | numerology |
| `P6.detail` | Склад, не занятый узлом? | generated | progressiveDetails |
| `P6.style.*` | Как решаю / близость / деньги? | generated | contract styles |
| `P6.natal_decode` | Как карта объясняет уже известное ядро? | generated | opt-in decode |
| `TF.no_connection` | сеть | chrome | shared |
| `TF.unavailable` | сервер flagged | chrome | shared |

---

## 3. Записи слотов

Поля по Grammar §3. Chrome-семейства сжаты, если закон один.

### 3.1 Shared failure

#### `TF.no_connection`

| | |
|---|---|
| surface | chrome-shared |
| one_question | Связь оборвалась? |
| text_class | chrome |
| authority / semantic_source | product · AGENTS.md |
| display_source | `«Нет соединения.»` |
| output / budget | 1 предложение · 3 слова |
| required | conditional (throw / network) |
| empty_behavior | показать этот слот; **не** invent портрет |
| may_fe_transform | none |
| may_llm_add_meaning | нет |
| interaction | none |
| forbidden | calm rows, «нет сигнала», offline story |
| persist_key | n/a |
| anti_dupe_group | `failure` |

#### `TF.unavailable`

Как выше; copy `«Не удалось загрузить.»`; appear when server flagged unavailable / forming-safe absence of meaning.

---

### 3.2 Conditional

#### `P-forming.message`

| | |
|---|---|
| surface | profile |
| role | честно, пока Snapshot не ready |
| one_question | Что уже читается, пока повторы ещё не собраны? |
| text_class | chrome |
| authority | product chrome (Voice §0 rewrite) |
| semantic_source | `FORMING_MESSAGE_RU` · `_safe_forming_message` |
| display_source | то же |
| allowed_inputs | status=forming only |
| forbidden_inference | pipeline («генерация», «тексты», «ИИ считает») |
| output | 2 предложения |
| budget | ≤240 chars |
| required | да, если forming |
| empty_behavior | omit если ready |
| may_fe_transform | none (rewrite only via `_safe_forming_message`) |
| may_llm_add_meaning | нет |
| interaction | none |
| forbidden | day lexicon, «Профиль готов» |
| why_here | до Шага 1 |
| persist_key | chrome |
| anti_dupe_group | `meta` |

#### `P-data.cta_text` / `P-data.button`

| | `cta_text` | `button` |
|---|---|---|
| one_question | Чего не хватает *мне*? | Куда править факты? |
| text_class | chrome | chrome |
| authority | capability messages | product |
| display_source | `userMessages[].text` (не `l3_gated`) | «Данные рождения» |
| budget | 1–2 предл. · ≤220 chars | 2 слова |
| required | нет | вместе с текстом |
| empty_behavior | omit | omit |
| may_fe_transform | none | none |
| forbidden | «Недостаточно данных», «Нам не хватает», today |
| why_here | честный next step, не кухня | navigate editor |
| persist_key | chrome / capability | chrome |

---

### 3.3 P1 Recognition

#### `P1.visual`

| | |
|---|---|
| one_question | Какой один образ ядра? |
| text_class | catalog |
| authority | calc seed |
| semantic_source | `baseline.archetype_seed` ← **только** life_path mapping |
| display_source | `ArchetypeHeroVisual` |
| allowed_inputs | seed slug |
| forbidden_inference | pills, второй символ, факты карты |
| output | 1 visual object ≥ половины первого взгляда |
| budget | 1 объект |
| required | да, если seed есть; иначе пустой arch, не invent |
| empty_behavior | omit illustration, keep layout |
| may_fe_transform | none |
| interaction | none |
| why_here | Шаг 1 share test |
| persist_key | profile_hash (seed) |
| anti_dupe_group | `identity_axis` |

#### `P1.recognition_name`

| | |
|---|---|
| one_question | Как называется ядро? |
| text_class | calc |
| authority | numerology life_path → closed 5-set |
| semantic_source | `CE.recognition_label` или `archetypeDisplayLabel(seed)` |
| display_source | hero h1 |
| allowed_inputs | life_path, seed, locale |
| forbidden_inference | «Личный профиль»; Солнце выбрало имя |
| output | 1 название |
| budget | 1 слово / label |
| required | да, если seed |
| empty_behavior | fallback chrome «Твоя суть» (**не** смысл; не CE-строка) |
| may_fe_transform | map_label |
| persist_key | profile_hash |
| anti_dupe_group | `identity_axis` |

#### `P1.recognition_line`

| | |
|---|---|
| one_question | **Кто я как наблюдаемый механизм?** |
| text_class | generated |
| authority | Character Engine / identity funnel |
| semantic_source | `profile_contract_v1.recognition_line` |
| display_source | projection `journey.recognition.line` |
| allowed_inputs | CE Act I (одна мысль) from allowed snapshot depth; birth+baseline; **не** day, **не** living-as-pattern unless depth allows |
| forbidden_inference | совет на сегодня; имя архетипа в строке; список черт; day agenda; «всегда»; диагноз |
| output | 1 мысль |
| budget | 1–2 строки · 12–18 слов · **16–120 chars** |
| required | да на ready |
| empty_behavior | fallback: first sentence of identity_core **если** проходит тот же gate; иначе omit line |
| may_fe_transform | clip 120 |
| may_llm_add_meaning | нет — только формулировка механизма |
| interaction | none |
| forbidden | chips знака/пути; второй абзац «кто ты» |
| why_here | узнавание ≤5 с |
| persist_key | Snapshot + prompt version |
| anti_dupe_group | `path_new_value` · `identity_axis` |

Gate: `validate_recognition_line`.

#### `P1.signal`

Chrome «Почему именно ты» / «Свернуть». Budget 2–3 слова. Required если есть `P1.identity_core` отличающийся от line **или** есть P2. Interaction: disclose core **или** scroll to Why. `may_fe_transform`: none.

#### `P1.identity_core`

| | |
|---|---|
| one_question | Та же ось, чуть шире? (disclosure, не новый акт) |
| text_class | generated |
| authority | CE identity |
| semantic_source | `profile_contract_v1.identity_core` |
| display_source | behind signal |
| allowed_inputs | тот же Act I; не P3 materials |
| forbidden_inference | новый логлайн; day; encyclopedia natal |
| output | 2–4 предложения |
| budget | ≤720 chars склад; на экране не конкурирует с line |
| required | нет |
| empty_behavior | omit; signal may still scroll to Why |
| may_fe_transform | none (не compress в line, кроме documented fallback) |
| may_llm_add_meaning | нет |
| interaction | disclose |
| why_here | кухня Шага 1 |
| persist_key | Snapshot |
| anti_dupe_group | `identity_axis` (не `path_new_value` vs insight) |

---

### 3.4 P2 Why

#### `P2.step_title` · `P2.selected_section` · `P2.influenced_section` · `P2.expand_hint`

Chrome. Titles: «Главное, что формирует тебя» · «Выбрало имя» · «Расширяет портрет» · «Нажми — смысл за фактом».  
`one_question`: n/a (labels). `may_fe_transform`: none. Appear with P2.

#### `P2.selected_life_path`

| | |
|---|---|
| one_question | **Что выбрало имя архетипа?** |
| text_class | calc + chrome glue |
| authority | numerology + baseline mapping |
| semantic_source | `numerology.life_path` + seed |
| display_source | why selected_by row |
| allowed_inputs | life_path, seed, RU glue «Архетип X — из числа пути N» |
| forbidden_inference | Солнце/стихия/ритм участвовали в выборе имени |
| output | 1 строка факт + короткий смысл |
| budget | ≤120 chars |
| required | да, если LP+seed |
| empty_behavior | omit row (нет имени без LP) |
| may_fe_transform | map_label |
| may_llm_add_meaning | нет |
| interaction | none |
| why_here | Шаг 2 trust |
| persist_key | profile_hash |
| anti_dupe_group | `why_not_hero` |

#### `P2.anchor.sun` / `.element` / `.rhythm` / `.moon` / `.asc` / `.mc`

Общий закон якоря:

| | |
|---|---|
| one_question | Как **этот** факт расширяет уже названное ядро у *этого* человека? |
| text_class | calc (+ role-prose **bank / CE helper**, не read-path LLM) |
| authority | natal/astro calc; meaning = existing bank |
| allowed_inputs | that fact + CE core as *context to phrase*, not to retell P1 |
| forbidden_inference | «поэтому ты Архитектор»; энциклопедия дома; dump 12 houses; повтор recognition_line |
| output | title 1–3 слова · detail факт · meaning 1 предложение |
| budget | meaning 12–22 слов · ≤160 chars |
| required | нет |
| empty_behavior | omit якорь |
| appear | sun/element/rhythm: дата известна; moon: position; asc/mc: **reliable time** |
| may_fe_transform | none; tap-expand collapse meaning for sun/moon/asc/mc |
| may_llm_add_meaning | нет на read path |
| interaction | tap expand = тот же слот |
| persist_key | profile_hash + natal |
| anti_dupe_group | `why_not_hero` |

No bank text → meaning fallback chrome «расширяет портрет» (`empty` meaning, not invent).

#### `P2.honesty_no_time`

| | |
|---|---|
| one_question | Чего ещё нет без времени рождения? |
| text_class | chrome |
| display_source | Forms honesty (ASC/дома → внешнее проявление и сферы) |
| budget | 2 предложения |
| required | да, если нет reliable time |
| empty_behavior | omit если время есть |
| forbidden | «система не может», «недостаточно данных» |
| why_here | честность selected vs influenced |
| anti_dupe_group | `meta` |

---

### 3.5 P3 Insight

#### `P3.step_title` · `P3.eyebrow` · `P3.grounded_label` · `P3.help_label` · `P3.living_label` · `P3.living_note`

Chrome. Eyebrow: только `kind=strength` → «Твой дар»; tension/repeat → **omit eyebrow** (title узла = heading). Living note: «Контекст из отметок — не доказательство».

#### `P3.node_title`

| | |
|---|---|
| one_question | Как назвать эту одну закономерность? |
| text_class | generated / projected from materials |
| authority | CE → insight_nodes_v0 |
| semantic_source | `nodes[0].title` |
| allowed_inputs | strengths / growth_zones / patterns **materials**, не три списка на UI |
| forbidden_inference | три заголовка зон; day tip |
| output | 1 строка |
| budget | 4–10 слов · ≤80 chars |
| required | да вместе с insight |
| empty_behavior | omit **всего P3** |
| persist_key | Snapshot + projection version |
| anti_dupe_group | `node_heading` |

Max nodes first release: **1**.

#### `P3.insight`

| | |
|---|---|
| one_question | **Какую закономерность / ловушку я раньше не называл?** |
| text_class | generated |
| authority | CE Acts III–IV |
| semantic_source | `nodes[0].insight` |
| allowed_inputs | ядро + contradiction + materials; living только как adjacent, не proof |
| forbidden_inference | пересказ recognition_line; «регулярно» на birth_data_only; kitchen («механизм проявляется», zone ids) |
| output | 2–3 предложения |
| budget | 30–55 слов · **≤360 chars на экране** (склад ≤900 kitchen) |
| required | да для P3 |
| empty_behavior | omit P3 |
| may_fe_transform | clip + scrub kitchen |
| may_llm_add_meaning | нет сверх cascade |
| persist_key | Snapshot |
| anti_dupe_group | `path_new_value` |

#### `P3.grounded_on`

| | |
|---|---|
| one_question | На каких **фактах** (не интерпретациях) держится узел? |
| text_class | calc |
| authority | same facts as P2 subset |
| semantic_source | `grounded_on[].label` |
| allowed_inputs | LP, sun, element, rhythm, moon, ASC/MC if known |
| forbidden_inference | «потому что» как причинность без trace; prose interpretation in fact slot |
| output | 2–4 list rows |
| budget | каждая ≤80 chars |
| required | нет |
| empty_behavior | omit block опор |
| may_fe_transform | localize fact line |
| anti_dupe_group | `why_not_hero` (факты могут повторяться как опоры, не как смысл P1) |

#### `P3.help`

| | |
|---|---|
| one_question | Что помогает **внутри этой оси** (не совет дня)? |
| text_class | generated |
| authority | CE; patterns/helps LLM только если gate |
| semantic_source | `nodes[0].help` else one strengths/practical line |
| allowed_inputs | help/strengths; **не** Today, **не** invented living |
| forbidden_inference | day agenda; kitchen insight-help |
| output | 1 предложение |
| budget | 12–22 слов · ≤140 chars экрана (склад ≤360) |
| required | нет |
| empty_behavior | omit help step |
| may_fe_transform | clip; hide kitchen |
| persist_key | Snapshot |
| anti_dupe_group | `node_help` |

#### `P3.living_evidence`

| | |
|---|---|
| one_question | Как это уже проявлялось в **моих** отметках? |
| text_class | user |
| authority | user living |
| semantic_source | check-in / notes quotes |
| allowed_inputs | real signals only |
| forbidden_inference | выдуманный повтор; «подтверждённый паттерн» без gate |
| output | 0–2 цитаты |
| budget | каждая ≤240 chars · 1 строка |
| required | нет |
| empty_behavior | **omit** (слота нет) |
| may_fe_transform | scrub |
| anti_dupe_group | `living` |

---

### 3.6 P4 Effort

#### `P4.step_title` · `P4.lead`

Chrome: «Куда прикладывать усилия» · «Одно направление — не ещё одно описание «кто ты».»

#### `P4.effort_vector`

| | |
|---|---|
| one_question | **Куда прикладывать усилие в поведении?** |
| text_class | projected |
| authority | same as P3.help (no new LLM) |
| semantic_source | `effort_vector_v0` from `nodes[0].help` only |
| display_source | `journey.effortVector` |
| allowed_inputs | **только** that help, if action-start · ≠ insight · ≠ recognition_line · no сегодня/завтра |
| forbidden_inference | life_mission; new rec list; astrology; Today; second LLM |
| output | 1 предложение-действие |
| budget | 12–22 слов · **8–140 chars** |
| required | нет |
| empty_behavior | **omit всего P4** (включая сферы на пути) |
| may_fe_transform | clip |
| may_llm_add_meaning | нет |
| interaction | none |
| why_here | Шаг 4 |
| persist_key | projection version (read-path, not Snapshot field) |
| anti_dupe_group | `path_new_value` · `effort_not_mission` · `bridge_not_effort` |

#### `P4.sphere.title` / `.teaser` / `.expand`

| | title | teaser | expand |
|---|---|---|---|
| one_question | Где ярлык? | Где это сильнее (новая грань vs вектор)? | Как/нужно/риск здесь? |
| text_class | chrome/catalog | generated | generated |
| authority | life_spheres projector | CE derived | CE derived |
| allowed_inputs | sphere id + fields that **add where** | same | how/need/risk/helps |
| forbidden_inference | пересказ effort_vector; day agenda; 8 сфер на пути | same | same |
| budget | 1–2 слова | 1 предл. · ≤88 chars | 1 предл. на поле · ≤220 |
| required | нет | нет | нет |
| empty_behavior | omit card | omit teaser | omit expand |
| count | **0–2 на скролле** | | |
| persist_key | Snapshot | | |
| anti_dupe_group | `effort_where` | | |

Остальные сферы → `P6.detail` only.

---

### 3.7 P5 Bridge

#### `P5.step_title` · `P5.cta`

Chrome: «Мост в день» · «Открыть Today →». CTA interaction: navigate `/today`.

#### `P5.bridge_line`

| | |
|---|---|
| one_question | **Почему сейчас открыть Today?** |
| text_class | projected |
| authority | product packs keyed by `node.kind` |
| semantic_source | `bridge_line_v0` tension-pack **или** repeat-pack |
| allowed_inputs | kind of selected node (+ living flag for pack choice); **не** effort text |
| forbidden_inference | императив; дубль effort; прогноз дня; камень дня |
| output | 2 предложения |
| budget | 20–40 слов · ≤220 chars |
| required | нет |
| empty_behavior | omit line; CTA остаётся chrome-навигацией. Нет pack → нет строки, не invent мост |
| may_fe_transform | none |
| may_llm_add_meaning | нет |
| persist_key | projection version |
| anti_dupe_group | `path_new_value` · `bridge_not_effort` |

---

### 3.8 P6 Explore (не шаг пути)

#### `P6.title`

Chrome «Натальная карта». Appear if natal **or** leftover details.

#### `P6.wheel` / `P6.numbers`

Calc visuals/facts. one_question: как устроена карта / какие числа. No encyclopedia dump on collapsed. omit if no natal.

#### `P6.detail`

| | |
|---|---|
| one_question | Какие детали контракта ещё не сказаны на пути? |
| text_class | generated |
| authority | Snapshot leftover |
| allowed_inputs | progressiveDetails **minus** slots owned by P3/P4 |
| forbidden_inference | повтор insight/help/strengths уже в узле |
| output | title chrome + 1–2 предл. |
| budget | ≤240 chars body |
| required | нет |
| empty_behavior | omit |
| anti_dupe_group | `node_not_warehouse` |

#### `P6.style.decision` / `.relationship` / `.money`

| | |
|---|---|
| one_question | Как я решаю / строю близость / отношусь к деньгам **как проявление ядра**? |
| text_class | generated |
| authority | CE derived styles (не независимый generator) |
| semantic_source | contract `decision_style` / `relationship_style` / `money_style` |
| allowed_inputs | cascade; не новый personality root |
| forbidden_inference | отдельный акт на главном скролле |
| output | 2 предложения на экране |
| budget | ≤280 chars UI · склад ≤520 |
| required | нет |
| empty_behavior | omit |
| why_here | склад, не Шаг 3–4 |
| anti_dupe_group | `node_not_warehouse` |

#### `P6.natal_decode`

| | |
|---|---|
| one_question | Как **структура карты** объясняет уже известное ядро? |
| text_class | generated |
| authority | Natal Decode (not CE overwrite) |
| semantic_source | `natal_decode_depth_v0` after explicit POST |
| allowed_inputs | fixed identity_core + tension + natal + numerology packs |
| forbidden_inference | второй логлайн; write CE; feed Today as character root; auto GET generate |
| output | long-form only after CTA |
| budget | base houses = 1–2 предл. how/do; essay only in decode |
| required | нет |
| empty_behavior | CTA until generated; then persist by fingerprint |
| persist_key | decode fingerprint |
| anti_dupe_group | `decode` |

**Forbidden chrome:** marketing `benefits[]` («Потенциалы и таланты»…) — нет `slot_id` → нет UI.

---

## 4. Вне рамки

Character warehouse act · `life_mission` как замена P4 · Maps/Tracking · Today content · Compat hub · 12-house dump on P1/P2 · name glyph · FE invent on failure.

---

## 5. Код vs замок

| Код | Замок |
|-----|-------|
| `why.honesty` null | `P2.honesty_no_time` обязателен без времени |
| Explore benefits[] | нет слота |
| v0 `PROFILE_LIMITS` | бюджеты этого файла |

Cut 2026-08-29: `ProfileCharacterScene` removed from path; P4 spheres cap 0–2; leftover styles/mission in Explore.

---

## 6. Трасса (пример)

```text
«Ты первым видишь структуру…»
  → P1.recognition_line
  → generated
  → profile_contract_v1.recognition_line
  → Character Engine Act I
  → allowed: identity funnel; forbidden: day / archetype name
  → Snapshot (user, profile_hash) + prompt version
  → FE clip ≤120
```

---

## 7. Audit vs Grammar §5 (2026-08-29)

Построчно против замка: authority · inputs · one_question · anti-dupe · стрелка. Не UI cutover.

| Слот | Verdict | Заметка |
|------|---------|---------|
| `P-forming` / `P-data` | PASS | до пути; omit when ready / capable |
| `P1.visual` / `recognition_name` | PASS | имя только life_path; chrome «Твоя суть» не смысл |
| `P1.recognition_line` | PASS | механизм; journey: «Я человек, который…» |
| `P1.identity_core` | PASS | disclosure той же оси, не path_new_value |
| `P2.selected_life_path` + anchors | PASS | факты не в герое; CE только phrase context |
| `P2.honesty_no_time` | PASS | required без времени |
| `P3.node_title` | **FIXED** | был в `path_new_value` → `node_heading` |
| `P3.insight` | PASS | единственный new-value узла; journey: «Я раньше не замечал…» |
| `P3.help` | **FIXED** | был в `path_new_value` (ломал проекцию Effort) → `node_help` |
| `P3.grounded_on` / living | PASS | факты / user; living не proof |
| `P4.effort_vector` | PASS | projected from help only; omit whole P4 if unsafe |
| `P4.sphere.*` | **FIXED** | 0–2 on path; leftovers Explore |
| `P5.bridge_line` | **FIXED** | empty = omit line, keep CTA chrome |
| `P5.cta` | PASS | navigate; не смысл дня |
| `P6.*` | PASS | склад, не акт пути; `benefits[]` нет слота |
| Character warehouse | **FIXED** | нет slot_id на пути; стили в Explore |

**Остаток (не слот-дефект каталога):** `P2.honesty` if time-unknown still empty; Explore `benefits[]` copy unused as UI list. Character warehouse and P4>2 cut.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-08-30 | Grammar §9 scanner covers Profile path slots; catalog sync-tested against §2 |
| 2026-08-29 | FE cutover — Character warehouse off path; P4 spheres 0–2 |
| 2026-08-29 | v1.0 — первый закрытый список |
| 2026-08-29 | v1.1 — Grammar §3 records; one_question; allowed_inputs; forbidden_inference; anti_dupe groups; persist keys |
