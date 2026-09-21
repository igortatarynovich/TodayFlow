# Profile Information Contract v1

**Status:** ACTIVE — закрытое информационное пространство Profile  
**Date:** 2026-09-20  
**Kind:** reconstruction. **Новых типов знаний нет.**  
**Не заменяет:** Character Engine (композиция личности) · Interpretation Library (атомы астрологии) · Display Inventory (слоты UI) · Availability Matrix (доступ / reveal)

Цепочка (закон):

```text
source input
  → calculated fact
  → allowed knowledge          ← этот файл: конечное N
  → derivation / composition
  → product field (M ⊆ N)      ← что Profile имеет право показывать
  → display slot               ← PROFILE_DISPLAY_INVENTORY_V1
  → visible text
```

Если у текста нет этой цепочки — в продукте его нет. LLM не заполняет пробел.

---

## Architecture impact

- **SoT before:** «что система имеет право знать» было размазано между Capability `allowed_output`, Availability Matrix §3.1, Character Engine актами, Content Canon §4, Display Inventory слотами и Knowledge Core `KC-*`. Механизмы (IL-2/3/4, CE stages, polish, funnels) строились без конечного N.
- **SoT after:** этот файл — **закрытый перечень** фактов и допустимых знаний Profile **и обязательный code gate**. Display Inventory остаётся последним authority перед UI. Character Engine остаётся SoT композиции личности. IL-2 compose остаётся SoT occupancy-атомов для `K01`/`K02`. Строка вне таблиц §1–§3 **не существует** как содержание Profile. Нет `PIC-K*` + зависимых `PIC-F*` — meaning-работа не начинается (chrome/ошибки исключены).
- **Public contract changed?** no JSON
- **Migration required?** no
- **Canon updated?** yes — этот файл · `profile/_INDEX.md` · `docs/README.md` · Display Inventory · tracker · handoff
- **Backward compatible?** yes for API. Gate живёт в `profile_information_contract_v1.py` + `PIC_K`/`PIC_F` на meaning-модулях.

---

## 0. Откуда таблица (ничего не придумано)

| Слой | Документ | Что взято |
|------|----------|-----------|
| Ввод | [PRODUCT_DATA_INTAKE](../PRODUCT_DATA_INTAKE.md) | имя · дата · время · место |
| Факты карты | [PRODUCT_DATA_PROVIDERS](../PRODUCT_DATA_PROVIDERS.md) `NatalChartFacts` · [PRODUCT_CAPABILITY_CONTRACTS](../PRODUCT_CAPABILITY_CONTRACTS.md) L1/L2 | что можно посчитать |
| Доступ | [PRODUCT_AVAILABILITY_MATRIX](../PRODUCT_AVAILABILITY_MATRIX.md) §1 · §3.1 | без поля → нет зависимого вывода |
| Знания личности | [PROFILE_EXPERIENCE_SCENARIO_V1](./PROFILE_EXPERIENCE_SCENARIO_V1.md) акты I–VIII + финал | каскад, не энциклопедия |
| Поля Snapshot | [PROFILE_CONTENT_CANON_V1](./PROFILE_CONTENT_CANON_V1.md) §4 | alias полей |
| Атомы | [KNOWLEDGE_CORE_V1_SEMANTIC_INVENTORY](../astrology/KNOWLEDGE_CORE_V1_SEMANTIC_INVENTORY.md) · [LIBRARY_SCALE_V1](../astrology/LIBRARY_SCALE_V1.md) | planet/sign/house/aspect/angle |
| Числа | [NUMBER_BASE_V1](../numerology/NUMBER_BASE_V1.md) | 1–9 · 11/22/33 |
| Показ | [PROFILE_DISPLAY_INVENTORY_V1](./PROFILE_DISPLAY_INVENTORY_V1.md) · Matrix §3.1 | M: что рисуем |
| Decode | [PROFILE_NATAL_DECODE_DEPTH_V1](./PROFILE_NATAL_DECODE_DEPTH_V1.md) | opt-in, не personality root |

Алиасы (одно знание, много имён) схлопнуты в один `PIC-*`. Это не новое знание.

**Запрещено этим файлом:** добавить строку «потому что движок умеет». Новый `PIC-*` — только Architecture impact + строка в changelog.

---

## 1. Source input (закрыто)

Ровно то, что Intake разрешает хранить на профиле.

| ID | Ввод | Без него |
|----|------|----------|
| `IN.date` | дата рождения | нет персонального Profile |
| `IN.time` | время + `birth_time_known` | нет углов / домов / точной Луны |
| `IN.place` | место → lat/lon/TZ | время без места **не** даёт ASC/дома |
| `IN.name` | имя | нет именной нумерологии; натал не страдает |
| `IN.locale` | locale | язык формулировки, не смысл |
| `IN.stated` | онбординг / check-in / evening notes | нет living-утверждений о поведении |

Других входов для Profile нет. Китайский год, камень, IL-лемма — не ввод пользователя, а расчёт / lookup.

---

## 2. Calculated facts (закрыто)

Считается детерминированно. Это ещё не «знание о человеке». Нет факта → нет зависимого `PIC-K`.

| ID | Что считаем | Из ввода | Где считается | Gate |
|----|-------------|----------|---------------|------|
| `F01` | Солнце: знак | `IN.date` | Swiss / `sun_sign_from_date` | дата |
| `F02` | Солнце: стихия · модальность · полярность · управитель | `F01` | Foundation tables | дата |
| `F03` | Планеты Sun–Pluto: знак · градус · ретро | дата; точность без времени ниже | Swiss | дата |
| `F04` | Луна: знак · градус | дата; **точная** только full | Swiss | дата / full |
| `F05` | ASC · MC · IC · DSC: знак · градус | `IN.time`+`IN.place` | Swiss | **full only** |
| `F06` | 12 куспидов · планета-в-доме · управители домов | full | Swiss | **full only** |
| `F07` | Аспекты 5 majors: тип · орб | положения | Swiss + Foundation orbs | дата (грубее) / full |
| `F08` | Перевес стихий / модальностей | `F03`+`F04` | calc | дата |
| `F09` | Life path · birthday number | `IN.date` | numerology | дата |
| `F10` | Expression · Soul Urge · Personality | `IN.name` | numerology | имя |
| `F11` | Personal year / month / day | `IN.date` + as_of | numerology | дата |
| `F12` | Каталог: цвет · камень · китайский год · тибетский ключ | `F01` / `IN.date` | `profile_header_knowledge_v0` + horoscope services | ключ в каталоге, иначе omit |
| `F13` | User-stated / living | `IN.stated` | DayConnection / notes | только как «вы отметили» |

**Явно OUT как факты Profile (уже в каноне):** прогрессии / соляр / returns как IL-объекты (`KC-T-PROG`) · минорные аспекты · Nodes/Chiron/Lilith как IL-gold · DSC/IC как angle-атомы V1 · дома без full natal.

Code Δ: Capability TARGET = LLM `natal_facts`; CODE = Swiss. Для этой таблицы важен **набор полей**, не вендор.

---

## 3. Allowed knowledge (N = 18)

Что система **имеет право знать** из §2. Не «что ещё интересно вывести».

Колонки покрытия:

- **KB** — есть ли knowledge atom / каталог
- **Rule** — есть ли правило derivation (не промпт «напиши красиво»)
- **Wire** — доходит ли до Snapshot / слота, не схлопываясь

| ID | Что знаем | Факты | Atoms / KB | Derivation | KB | Rule | Wire | Show? | Где | Формат |
|----|-----------|-------|------------|------------|----|------|------|-------|-----|--------|
| `K01` | Один наблюдаемый механизм личности (логлайн) | `F01`–`F04`, `F09`, full: `F05`; occupancy `F03`/`F06` | Planet `core_function` · Sign `manner` · (full) Angle `orientation` · IL-2 `planet_in_sign` / `planet_in_house` | CE Акт I: одна мысль из разрешённых фактов. Occupancy — qualifier, **не** замена механизма. **Не** список черт, **не** 13-key bucket | IL 7 планет draft; Stage 1 occupancy claims + F05/F09 facts | `compose_k01_identity_v0`; 13-key bank только fallback если sun IL-2 не собирается | **закрыт:** F01–F04 → roles; нет atom → omit/меньше конкретности, не essay; occupancy конкретизирует | **да** | `P1.recognition_line` · `P1.identity_core` · Matrix `identity_summary` | 1 предложение механизма + grounded pieces |
| `K02` | Роль каждого факта в **этом** ядре | subset `F01`–`F10`, `F12`; occupancy `F03`/`F06` | те же атомы; каталог не энциклопедия | CE Акт II: «какую часть этой личности я сформировал». Occupancy = `source_roles.qualifier`. Тест: без имени планеты фраза про человека | атомы есть | правило есть | partial anchors + occupancy qualifier | **да** | `P2.anchor.sun/moon/asc/mc/element/rhythm` · `P2.selected_life_path` | 1 тезис на опору; пустое omit |
| `K03` | Прикладной смысл углов и домов **этого** человека | `F05` `F06` (+ занятые `F03`) | Angle `orientation` · House `arena` · IL-2 Planet×House | CE Act II applied: `how` + `do` на ASC/MC и занятые дома. Не энциклопедия 12 домов, не K07 sphere | 12 house + 2 angle packs stored; catalog `draft` | `derive_k03_*` в `character_engine_profile_consumption_spheres_houses_v0` | **закрыт:** full natal; нет occupancy/atom → omit; DSC/IC вне V1 | **да, full only, Explore/Map** | `P6.applied.asc/mc/house` | `how` + `do`; незначимое omit |
| `K04` | Internal Engine: как решает / воспринимает / держит стресс / риск / восстановление / рост / выгорание | `F03` `F04` `F07` `F08` + ядро | Planet function · Aspect `relation` · IL-2 frames | CE Акт III: **одна** ось в `P3.help` из F08 / harmonic F07, не семь виджетов. Capability L2 `decision_style` — **алиас**, не отдельный корень | IL-2 `planet_in_sign` `how` · harmonic `relation` | Stage 0 F08 + `select_internal_engine_path_axis_v0` | **да:** уникальный перевес / одна гармоника → `P3.help`; пустое omit | **да, свёрнуто** | `P3.help` (не 7 виджетов) · K05 держит `P3.insight` | механизм; пустая ось omit |
| `K05` | Одно главное напряжение A↔B | hard `F07`, clash `F08`, конфликт ролей K02 | Aspect `relation` · IL-2 `aspect_pair` | CE Акт IV: ровно одно главное. Content `inner_tension` = alias | Stage 0 mint 5 majors; Stage 1 ровно одна hard `aspect_pair` tension | канон есть | **закрыт:** grounded F07 → IL-2 → `P3.insight`; trap-bank не обгоняет; пустое omit | **да** | `P3.insight` | одна ось, не список |
| `K06` | Вторичные напряжения (1–3), не конкурируют с K05 | то же | то же | CE Акт IV secondary | то же | канон есть | **OMIT-BY-DESIGN на пути:** P3 не имеет слота без перегрузки K05 insight / второго узла. N остаётся для Explore | **нет на пути** | Explore / Stage3 schema | короткие оси, если когда-нибудь покажем вне first-paint |
| `K07` | Как K01+K04+K05 проявляются в ситуациях | full усиливает домами `F06` | House `arena` для «где»; сцена ≠ корень | CE Акт V. Matrix «Эмоции / отношения / работа / деньги / дом» = **ярлыки сцен**, запрещены как generative roots | house packs есть | CE consumption: occupied F06 of K01/K04/K05 bodies → IL-2 `planet_in_house` | **закрыт:** ≤2 сферы из grounded F06+arena; нет F06/связи → omit; identity-thesis / trap-bank / LLM не заполняют | **да ≤2 сферы на пути** | `P4.sphere.*` · Matrix L2 styles | teaser + expand how/need/risk |
| `K08` | Направление роста (не профессия) | K01+K04+K05 | — (derived) | CE Акт VI | нет отдельного KB | канон: из системы, не новый LLM-корень | `P4.effort_vector` проецируется из `help`, не из потенциала как поля | **да проекцией** | `P4.effort_vector` | 1 вектор поведения |
| `K09` | Слепая зона / честная цена оси | K05 + K04 | Sign `excess` того же тела, что дало K04 `how` | CE Акт VII: одна цена оси, **derived** из grounded K04+K05. Не отдельный LLM-корень | excess в IL-1 sign canon | правило: оба hop grounded, иначе omit | **да внутри узла:** fill-empty в `P3.insight` после A↔B; не вытесняет K04/K05 | **да внутри узла** | `P3.insight` · `P3.help` | 1 неудобная правда; пустое omit |
| `K10` | Компас: strengths · helps · energy · red flags · practical takeaway | только уже построенные K01–K09 | — | CE Акт VIII **derived only**. Capability `core_strengths` / Matrix `helps[]` = проекции | — | запрет собственного промпта | **закрыт:** `helps` = grounded K04 или omit; Stage3/4/5 / essay не заполняют; strengths/energy/red flags без самостоятельного корня | **да derived** | `P3.help` · `P4.effort_vector` · Matrix helps (Trial+) | список следствий; empty omit |
| `K11` | Дуга пути личности (вообще, не сегодня) | K01+K05+K08 | `F09` как evidence, не заголовок | CE Финал | number_base для цифры; дуга — композиция | канон есть | `P5.bridge_line` = мост в Today из `node.kind`, **не** финальная дуга жизни | **частично** | `P5.bridge_line` | 1 предложение «почему открыть Today» |
| `K12` | Что life path вносит в **этого** человека | `F09` life_path (birthday — не этот слот) | `number_base_v1` 1–9, 11/22/33 | вклад в Why, не статья «число 7 означает» | **есть** JSON bank | lookup | `P2.selected_life_path` calc; CE primary не слот | **да** | P2 life_path · P1 visual seed отдельно | число + grounded contribution; omit без bank |
| `K13` | Что имя-числа вносят в самопрезентацию | `F10` | тот же bank | Capability L1 `name_expression`; omit без имени | bank есть | канон: не влиять на натал | `P2.name_numerology` compact Why | **да** | Why header fact, не акт пути | omit + CTA без имени |
| `K14` | Культурные соответствия знака/даты | `F12` | header pack · chinese/tibetan services · sign stones/colors | **lookup**, не LLM. Нет ключа → omit | цвета hardcoded; камни из sign catalog; год — сервисы | Matrix closed decision #10 | `P2.correspondence` compact Why | **да** | Why header fact, не акт пути | ключ+ярлык; без выдумки |
| `K15` | Как карта объясняет уже известное ядро | весь natal pack + K01 (+ K05) | IL-4 phrase pack на decode | opt-in POST; не personality root; не Today/Compat SoT | IL-4 bind 1.3.123; catalog draft | [PROFILE_NATAL_DECODE_DEPTH_V1](./PROFILE_NATAL_DECODE_DEPTH_V1.md) | POST `natal_decode_depth_v0`; GET не генерит; `insight_nodes[0]` = optional K05 | **да opt-in Explore** | `P6.natal_decode` | история карты поверх fixed core |
| `K16` | Практические tips выбранной deep-темы | выбранная K07 сфера (`how`/`need`/`risk`) | chrome wrap 1–2 do-lines | L3 Trial+: только уже выбранная тема; не переписывать how/need/risk; нет grounded сферы → omit | — | CE deep themes | `derive_practical_tips_from_k07_sphere` (не LLM, не thesis bank) | **да Trial+ Explore** | `P6.practical_tips` | 1–2 шага или omit |
| `K17` | Чего нет и что откроется | `unavailable` из Capability | — | всегда честность; не invent | — | Matrix §1.1 copy | `P-data.*` | **да** | `P-data.cta_text` · `P-forming.message` | CTA ввода / forming chrome |
| `K18` | Как это уже проявлялось в отметках | `F13` | — | Content `source_depth`; запрет паттернов на `birth_data_only` | — | Content §3 | слот есть; пусто omit | **да если есть** | `P3.living_evidence` | «вы отметили», не диагноз |

**N = 18. Конец списка.**

Слоты chrome (`P*.step_title`, `TF.no_connection`, CTA Today) — не знания. Они остаются в Display Inventory.

---

## 4. Что покрыто / чего нет

Сводка по базе, не по желаемому экрану.

| Есть | Нет / дырка |
|------|-------------|
| Считать `F01`–`F11` (Swiss + numerology) | IL catalog **38 draft / 0 active**; product surfaces ignore `draft` besides PIC occupancy consume |
| Planet Canon Sun–Saturn · Sign manner ×12 · House arena ×12 · Aspect relation ×5 · Angle ASC/MC | Uranus/Neptune/Pluto objects withheld · DSC/IC out of V1 · Mars psych `ACCESS_BLOCKED` · sign later-interpretive `DEFERRED_V1` |
| IL-2 compose 616 cells на library layer; CE Stage 1 читает occupancy compose **и** одну hard `aspect_pair` (K05) | IL-3 rank / IL-4 voice / calc_il_wire **не** являются проводкой first-paint. Transits / angles не в Stage 1 |
| Number base 1–9 / 11/22/33 | Отдельный смысл personal_year vs life_path — только bridge, не вторая таблица (канон чисел) |
| Header catalog цвет/камень/CN/TB · слоты `P2.correspondence` / `P2.name_numerology` | Растения / ведический ярлык как накопленный ключ — заявлено Matrix, единого pack нет |
| Display Inventory путь из 5 актов + compact Why facts | Исполняемый статус каждой строки — **§11**, не эта сводка |
| Natal Decode opt-in + IL-4 polish | First-paint `K01` — IL-2 roles; occupancy qualifier; 13-key не SoT |

Покрытие `K01`/`K02` из `F03`/`F06` (2026-09-20): два натала с одним Солнцем Девы и разным Марс×дом дают разные IL-2 occupancy atoms, разные Stage 1 claims и разный Identity Core surface. Механизм (sun×sign + moon + ASC) остаётся близким; recognition line **не** 13-key фраза. Это не IL-3→Stage 1 слой.

---

## 5. Product selection (M) — что Profile показывает

Не новое решение. Восстановлено из Display Inventory (путь) + Matrix 3.1 (approved blocks).

**На пути (Recognition → Why → Insight → Effort → Bridge):**

| Знание | Показ |
|--------|--------|
| `K01` | да — герой |
| `K02` + calc `F01 F04 F05 F09` | да — Why anchors |
| `K13` `K14` | да — compact Why header facts, **не** акты пути и **не** Identity Core |
| `K04` `K05` `K09` | да — один узел Insight, не склад |
| `K06` | **нет** — OMIT-BY-DESIGN на пути; N / Explore |
| `K10` help | да — help узла → Effort vector |
| `K07` | да — 0–2 сферы, «где», не второй вектор |
| `K11` | только как мост в Today, не «миссия жизни» |
| `K17` | да, если данных не хватает |
| `K18` | да, если living есть |

**Рядом, не шестой акт:** Explore / Map — `K03` how/do, numbers, leftover styles, `K15` по запросу.

**Trial/Paid only:** `K10` deep helps · `K16` tips.

**Не показываем, хотя движок где-то умеет:**

- энциклопедия планет/домов
- независимые эссе Relationships / Career / Money / Strengths / Energy
- транзиты и «что значит сегодня» (это Today, не Profile)
- прогрессии, соляр, миноры, outers как объекты
- 616 IL-клеток списком
- Compass отдельным промптом
- второй логлайн в Natal Decode
- `K06` secondary tensions на first-paint (нет слота P3 без перегрузки одного insight)

---

## 6. Трассировка до предложения

Каждый видимый meaning-атом обязан уметь заполнить:

```text
этот текст
  ← slot_id                    Display Inventory
  ← PIC-K*                     этот файл (M)
  ← derived conclusion         CE акт / derived Compass / lookup
  ← composition rule           IL-2 frame или CE evidence rule или catalog key
  ← knowledge atoms            IL pack / number_base / header catalog
  ← PIC-F*                     calculated facts
  ← IN.*                       source input
```

Нет любого звена → omit. Не «сформулируй правдоподобно».

Chrome и failure (`«Нет соединения.»` / `«Не удалось загрузить.»`) в эту цепочку не входят: они не знания о человеке.

---

## 7. Лишняя обвязка вокруг N

Построено до фиксации конечного множества. Не удаляется этим файлом; не является SoT знания.

| Механизм | Что делает | Отношение к N |
|----------|------------|----------------|
| IL-2/3/4 + wire + attach + consume + polish | library → editorial voice | атомы для `K01`–`K03`/`K15`. First-paint CE читает **только** IL-2 occupancy compose |
| CE Stage 1 13-key registry | mint thesis_key по солнцу/луне/ASC | **не** meaning SoT K01; fallback только если sun IL-2 не собирается |
| Disclosure funnel identity→styles→patterns→spheres | legacy LLM корни | TARGET запрещает как SoT; CODE Δ |
| Life spheres projector | сцена → карточка | presentation `K07`, не новый тип |
| Profile meaning polish 1.3.123 | IL-4 на decode | только `K15` |
| Knowledge-to-output harness | Mars Cancer H4 vs Libra H7 | acceptance `K01`/`K02`, не контракт N |
| Day Sources / vedic / bazi в Profile×Day matrix | факты дня | **не** Profile N; Today/overlay |

Документы, которые описывают **слоты, доступ или каскад**, но не заменяют эту таблицу: Display Inventory · Matrix 3.1 · Capability allowed_output · Content Canon §4 · CE Scenario.

Где они расходятся — побеждает: **N = этот файл** · композиция = CE · UI слот = Inventory. Capability/Content поля = aliases строк §3.

---

## 8. Незакрытые конфликты документов (не резались молча)

| Конфликт | Стороны | Что делает этот файл |
|----------|---------|----------------------|
| Состав экрана | Matrix: шапка → структура → стили сфер. Inventory: 5 актов пути + Explore | N не выбирает IA. M пути = Inventory; Matrix 3.1 остаётся approved access/reveal |
| Имя / камень в шапке | Matrix слоты есть; Inventory не имел `slot_id` | **закрыто:** `K13`/`K14` остаются в M; слоты `P2.name_numerology` / `P2.correspondence` — compact Why facts |
| `sun_sign_meaning` как L1 поле | Capability vs CE «одна мысль» | схлопнуто в `K01`/`K02`. Отдельной статьи знака нет |
| Chinese/Tibetan как evidence личности | CE Пролог vs Stage 1 rules | как **факт** `F12` и lookup `K14` — да. Как mint `K01` — в live реестре **нет** |

Owner может сузить M (убрать показ), не расширяя N.

---

## 9. Другие разделы

Тот же закон, другие таблицы. **Этим файлом не заполняются.**

| Раздел | Контракт | Сейчас |
|--------|----------|--------|
| Today | [TODAY_INFORMATION_CONTRACT_V1](../today/TODAY_INFORMATION_CONTRACT_V1.md) | **стартован отдельно** (N=20). PIC не источник очереди |
| Compatibility | нужен свой Information Contract | два Profile N + pair derivation (не написано как конечное множество) |
| Tarot | то же | card_base + question/spread; не закрытый N ответа |
| Практики | taxonomy + coverage ledger | метод/item, не «знание о человеке» |

Profile train закрыт. Today N живёт в своём контракте. Этот файл больше **не** порождает Today-работу.

---

## 10. Locked decisions (2026-09-20)

1. **N = 18.** `K13`/`K14` остаются в M. Это compact secondary/header facts, не акты journey и не Identity Core. Вычёркивать их из-за дыры Inventory было бы подгонкой продукта под неполный каталог слотов.
2. **N = 18 — обязательный code gate.** Любая meaning-producing работа в Profile обязана назвать минимум `PIC-K*` и зависимые `PIC-F*`. Не может указать — работа не начинается. Chrome и transport failure (`«Нет соединения.»` / `«Не удалось загрузить.»`) исключены. Модуль: `profile_information_contract_v1.py`.
3. **Ближайший патч** — coverage defect `PIC-K01`/`PIC-K02` для фактов `PIC-F03`/`PIC-F06`, не «подключить IL к Character Engine». PIC говорит *что* обязано дойти; внутреннюю проводку выбирает минимальный путь в существующем коде.
4. **Выбранный путь:** Stage 0 `planet_sign` (sign + house) → IL-2 `compose_planet_in_sign` / `compose_planet_in_house` → Stage 1 occupancy claims → Stage 2 qualifier на Identity Core surface. Не IL-3 frames → Stage 1. Не IL-4 voice. Не новый слой.
5. **Acceptance:** Cancer Mars/4 vs Libra Mars/7 при одном Sun/Moon/ASC. Различие есть в F03/F06 → atoms существуют → IL-2 его сохраняет → CE использует при derivation K01/K02 → конечный K01 **не** схлопывается.
6. **Критерий закрытия Profile train** (исполнен 2026-09-21): для каждого из 18 `PIC-K` определено facts → KB → derivation → wire → M/omit → slot; отображаемый M исполняется кодом. `K06` = OMIT-BY-DESIGN. Тогда — `TODAY_INFORMATION_CONTRACT` отдельным стартом. Не «IL подключён», не «xfail стал pass», не «Profile выглядит лучше».
7. **K01 thesis** не определяется bucket-key. Occupancy конкретизирует механизм, не создаёт двух разных людей: Mars Cancer/H4 и Mars Libra/H7 при одном Sun/Moon/ASC дают близкий механизм и **разную** recognition line, не 13-key фразу.

---

## 11. Executable coverage audit (2026-09-20)

Статусы — факт кода на ветке `cursor/profile-knowledge-to-output`, не желание канона.

| Статус | Значит |
|--------|--------|
| `COMPLETE` | отображаемый M: facts → KB → derivation → wire → slot исполняется; пустое omit |
| `PARTIAL` | hops есть, но схлопывание / не те F / слот мапится мимо / UI не рисует |
| `MISSING` | знание в N, до слота hop нет |
| `OMIT-BY-DESIGN` | PIC M это знание не показывает (или показывает другую проекцию); не дефект |

Occupancy hop `F03`/`F06` → IL-2 → Stage 1 claim → Stage 2 qualifier **закрыт**. K01 meaning = `compose_k01_identity_v0` из разрешённых фактов; 13-key не SoT.

| ID | Status | F consumed | KB | Derivation | Wire | Slot | Defect |
|----|--------|------------|----|------------|------|------|--------|
| `K01` | **COMPLETE** | Stage0 `planet_sign:sun/moon` (F01/F03/F04), full `angle_sign:ascendant` (F05), `life_path_number` (F09); occupancy F03/F06 qualifier | Planet `core_function` · Sign `manner` · Angle `orientation` · IL-2 `planet_in_sign` / `planet_in_house` · number_base keyword | `compose_k01_identity_v0`; 13-key bank / LLM / Decode / tips не заполняют; нет atom → omit piece | Stage2 identity_core `k01_source=il2_composed_roles`; consumption `P1.recognition_line` / `P1.identity_core` | Inventory Recognition + disclosure | нет на измеренном hop; без sun IL-2 → 13-key fallback only; DSC/IC не V1 |
| `K02` | **COMPLETE** | natal F01/F04/F05/F09 + occupancy F03/F06 as qualifier | `_CLAIM_WHY_LABEL` + FE zodiac banks | fill-empty natal Why rows from projector/Stage0; occupancy claims not Why | consumption merges natal `sun/moon/asc/life_path`; skips `planet_in_*` | live `P2.anchor.sun/moon/asc`; unknown/occupancy omit (not `P2.anchor.rhythm`) | нет на измеренном hop; `P2.selected_life_path` = K12 |
| `K03` | **COMPLETE** | Stage0 `angle_sign:asc/mc` (F05) + occupied `planet_sign:*`.house (F06, Sun–Saturn) | IL-2 `compose_planet_in_house` (`what` × house `arena`); angle `orientation` × sign `manner` | `build_k03_applied_v0`; identity-thesis house bank / 12-house encyclopedia / K15 / K16 не заполняют | `character_engine_asc_v0` / `house_lines_v0`; emit `P6.applied.*` surface=explore | Inventory Explore/Map; not P1–P5; occupied houses only | нет на измеренном hop; без full natal / compose omit; DSC/IC не V1; K01 thesis не этим патчем |
| `K04` | **COMPLETE** | Stage0 `element_balance` (F08 from F03/F04 Sun–Saturn) + harmonic F07 (conjunction/trine/sextile). Hard square/opposition stay K05 | IL-2 `planet_in_sign` `how` · harmonic `relation` | `select_internal_engine_path_axis_v0`; identity thesis 7-slot engine cannot occupy the path axis | consumption `nodes[0].help`; omit without unique F08 tilt or harmonic | `P3.help` (Insight node, не 7 виджетов); K05 держит `P3.insight` | нет на измеренном hop; пустая ось omit; K06 не этим патчем |
| `K05` | **COMPLETE** | Stage0 `aspect_pair:*` (F07 5 majors, Foundation orbs); hard square/opposition only | IL-2 `compose_aspect_pair` (`what_a`/`what_b`/`relation`) | Stage1 ровно один tension claim; harmonics / empty compose → omit | consumption `nodes[0].insight`; trap-bank и Stage3 identity tension не обгоняют | `P3.insight` (emit + Insight; empty omit) | нет на измеренном hop; leftover F07 не становятся path M (K06 OMIT-BY-DESIGN) |
| `K06` | **OMIT-BY-DESIGN** | leftover grounded F07 after K05 (N only) | IL-2 aspect `relation` | Stage1 не минтит secondaries; Stage3 schema 0–3; LLM/Stage4 не заполняют путь | consumption **не копирует** в insight/help/effort/spheres; `k06_source=omit_by_design` | нет Inventory slot; не второй node | не дефект: P3 = один insight (K05+K09) + help (K04); Explore может читать N позже |
| `K07` | **COMPLETE** | Stage0 occupied `planet_sign:*`.house (F06 full natal) of K01 occupancy / K04 axis / K05 pair bodies | IL-2 `compose_planet_in_house` (`what` × house `arena`) | `build_k07_path_spheres_v0`; identity-thesis packs / Stage4 scenes / trap-bank не заполняют | consumption `life_spheres` ≤2; K08 effort не из сферы | `P4.sphere.*` emit + Effort 0–2; empty omit | нет на измеренном hop; без full F06/связи omit; K03 house how и K16 tips не этим патчем |
| `K08` | **COMPLETE** | derived from `nodes[0].help` | — | `project_effort_vector_v0` | `effort_vector_v0` | `P4.effort_vector` emit + Effort; omit empty | нет (качество help = K04/K10) |
| `K09` | **COMPLETE** | grounded K04 path_axis (F08 sign) + grounded K05 A↔B; не F* напрямую | sign `canon.excess` | `honest_cost_from_axis_v0`; trap-bank / Stage4 LLM `blind_spots` не заполняют | consumption append в `nodes[0].insight`; K04 `help` не меняет | `P3.insight` (дополнение) · `P3.help` остаётся K04 | нет на измеренном hop; без пары K04+K05 omit |
| `K10` | **COMPLETE** | derived from grounded K01–K09 (`P3.help` = K04); не F13 | — (no essay / compass prompt) | consumption `helps` = `[k04]` else omit; Stage3 widgets / Stage4 potential / Stage5 adapters / `_essays_for` cannot fill | `P3.help` · Matrix `helps` Trial+; K08 effort stays projection of that help | empty omit; Inventory still omits whole P4 without safe help — display dependency, not a K10 license to mint help | нет на измеренном hop; strengths/energy/red flags omit without derivative; K07 spheres не источник help |
| `K11` | **COMPLETE** (показанный M) | `nodes[0].kind` | `_BRIDGE_*_RU` | `project_bridge_line_v0` | `bridge_line_v0` | `P5.bridge_line` emit + Bridge; omit empty | дуга жизни **OMIT-BY-DESIGN**; M = мост в Today |
| `K12` | **COMPLETE** | F09 `life_path` only (birthday не в этом слоте) | `number_base_v1` `base_meaning` | lookup; нет meaning → omit | projector + consumption `selected_by` = `life_path` row | `P2.selected_life_path` emit/Why; CE primary не слот | нет |
| `K13` | **COMPLETE** | F10 `expression`/`soul_urge`/`personality` | numerology calc (unchanged) | compact format only | Matrix `name_numerology` bag `expression`/`soul_urge`/`personality` | `P2.name_numerology` emit + Why; omit without IN.name; CTA via K17 `need_name` | нет; не пишет в natal/Identity Core |
| `K14` | **COMPLETE** | F12 header pack | `profile_header_knowledge_v0` | lookup `header_pack_to_matrix_catalog` | Matrix `cultural_catalog` | `P2.correspondence` emit + Why; omit empty | нет |
| `K15` | **COMPLETE** | natal pack + fixed K01 (+ grounded K05 `insight_nodes[0]`) | IL-4 draft + decode prompt 1.1.0 | POST `generate_natal_decode_depth_v0`; GET `resolve_natal_decode_get` never LLM; Stage3 trap-bank не вход | `natal_decode_depth_v0` PIC_K15; emit `P6.natal_decode` surface=explore | Inventory Explore; panel in Explore after chart, not path | нет на измеренном hop; без K01/natal omit; K03 house how / K16 tips не этим патчем |
| `K16` | **COMPLETE** | selected K07 `life_spheres[theme]` how/need/risk (F06 already in K07) | chrome prefixes only (`Сделай это так` / шаг / `Не пускай сюда`) | `derive_practical_tips_from_k07_sphere`; Trial+; identity-thesis / `_GENERIC` / Stage4/5 / LLM не источник | `character_engine_deep_themes_v0` `tips_by_theme`; emit `P6.practical_tips` surface=explore | Inventory Explore; chooser in Explore, not path; how/need/risk immutable | нет на измеренном hop; нет matching K07 row → empty omit; catalog∩K07 often misses sex/friends/family/decisions; K03/K01 не этим патчем |
| `K17` | **COMPLETE** | capability gaps / forming | Matrix §1.1 copy | `resolve_capability` · forming helpers | `user_messages` / `forming_message` | `P-data.cta_text` · `P-forming.message` live; chrome-exempt emit | нет |
| `K18` | **COMPLETE** | F13 `living.signals[].note` | — (quotes) | `_living_quotes`; omit if empty | `nodes[0].living_evidence` | `P3.living_evidence` emit + Insight | нет |

Сводка: **COMPLETE 17** (`K01` `K02` `K03` `K04` `K05` `K07` `K08` `K09` `K10` `K11` `K12` `K13` `K14` `K15` `K16` `K17` `K18`) · **PARTIAL 0** · **MISSING 0** · **OMIT-BY-DESIGN** `K06` (path M) + внутри `K11` (дуга жизни). Occupancy-подhop `K01` закрыт внутри COMPLETE.

### Очередь Profile (из аудита, не из архитектурного бэклога)

PIC N=18 исполнен кодом. Не IL-3. **Today N стартован отдельно** — [TODAY_INFORMATION_CONTRACT_V1](../today/TODAY_INFORMATION_CONTRACT_V1.md). Этот файл не очередь.

Profile queue: **пуста.** Не invent PIC-K19.

Не в очереди: IL aspects/transits/angles dump.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-09-21 | Today Information Contract стартован отдельно (N=20). PIC queue пуста; этот файл не источник Today-работы. |
| 2026-09-21 | K01 COMPLETE: Identity Core from F01–F04 + F05/F09 IL-2 roles → `P1.recognition_line` / `P1.identity_core`; occupancy qualifies; 13-key registry not meaning SoT. PIC N=18 executed (17 COMPLETE / 0 PARTIAL / 0 MISSING / 1 OMIT-BY-DESIGN). |
| 2026-09-20 | K03 COMPLETE: ASC/MC + occupied-house how/do from F05/F06 IL-2 → Explore `P6.applied.*`; not 12-house encyclopedia; not P1–P5; K01 thesis deferred as separate decision. |
| 2026-09-20 | K16 COMPLETE: practical action = chrome wrap of selected K07 how/need/risk → Explore `P6.practical_tips`; Trial+; omit without grounded sphere; identity-thesis/Stage4/5/LLM not source; how/need/risk immutable. Next = K03. |
| 2026-09-20 | K15 COMPLETE: Decode explains fixed K01 (+ grounded K05) via natal facts → Explore `P6.natal_decode`; GET never LLM; Stage3 trap-bank is not input; not a sixth path act. Next = K16. |
| 2026-09-20 | K06 OMIT-BY-DESIGN from path M: leftover F07 / Stage3 secondaries stay N for Explore; no new P3 slot; do not overload K05 insight. Next = K15. |
| 2026-09-20 | K10 COMPLETE: Compass derived-only from grounded K01–K09 (`helps` = K04 or omit); essay/Stage3/Stage4/Stage5 cannot fill; no fake help for K07 spheres. Next = K06. |
| 2026-09-20 | K07 COMPLETE: ≤2 path spheres from grounded F06 occupied houses of K01/K04/K05 via house `arena`; identity-thesis / LLM / trap-bank cannot fill; K08 not from sphere. Next = K10. |
| 2026-09-20 | K09 COMPLETE: one honest cost from grounded K04 sign `excess` + K05 A↔B fill-empty into `P3.insight`; does not displace K04 help or K05 A↔B; trap-bank / Stage4 LLM omit. Next = K07. |
| 2026-09-20 | K04 COMPLETE: one Internal Engine axis from Stage 0 F08 `element_balance` (or harmonic F07) → `P3.help`; not seven widgets; K05 keeps `P3.insight`. Identity-thesis engine cannot occupy the path axis. Next = K09. |
| 2026-09-20 | K05 COMPLETE: F07 5-major facts in Stage 0 → IL-2 `aspect_pair` → one hard A↔B → `P3.insight`; trap-bank cannot beat; omit without grounded evidence. Next = K04. |
| 2026-09-20 | K12 COMPLETE: `P2.selected_life_path` = F09 life_path + number_base contribution; CE primary не слот; birthday не примешивается. Next = K05. |
| 2026-09-20 | K02 COMPLETE: natal F01/F04/F05/F09 survive CE Why; occupancy not `P2.anchor.rhythm`. Next = K12. |
| 2026-09-20 | K13 COMPLETE: Matrix/producer/consumer share `expression`/`soul_urge`/`personality`; omit without IN.name; no Identity Core leak. Next = K02. |
| 2026-09-20 | §11 executable coverage: 5 COMPLETE · 12 PARTIAL · 1 MISSING. Finite Profile queue from PIC, not engine leftovers. |
| 2026-09-20 | Owner lock: K13/K14 stay in M + slots; N=18 code gate; K01/K02 from F03/F06 via IL-2 compose (not IL-3). Completion = 18 executable chains. |
| 2026-09-20 | v1 reconstruction: 6 inputs · 13 facts · **18 allowed knowledge**. Ничего не добавлено сверх существующих канонов. |
