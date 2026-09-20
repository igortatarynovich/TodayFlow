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
| `K01` | Один наблюдаемый механизм личности (логлайн) | `F01`–`F04`, `F09`, full: `F05`; occupancy `F03`/`F06` | Planet `core_function` · Sign `manner` · (full) Angle `orientation` · IL-2 `planet_in_sign` / `planet_in_house` | CE Акт I: одна мысль из Evidence Graph. Occupancy — qualifier, **не** замена 13-key thesis. **Не** список черт, **не** sun-bucket сам по себе | IL 7 планет draft; CE Stage 1 = 13 sun/moon/ASC ключей **плюс** IL-2 occupancy claims | CE каскад есть; Stage 1 читает IL-2 compose (не IL-3 rank, не IL-4 voice) | **да:** два одинаковых Солнца + разный Mars×дом → разный K01 surface | **да** | `P1.recognition_line` · `P1.identity_core` · Matrix `identity_summary` | 1 предложение механизма + occupancy lemmas |
| `K02` | Роль каждого факта в **этом** ядре | subset `F01`–`F10`, `F12`; occupancy `F03`/`F06` | те же атомы; каталог не энциклопедия | CE Акт II: «какую часть этой личности я сформировал». Occupancy = `source_roles.qualifier`. Тест: без имени планеты фраза про человека | атомы есть | правило есть | partial anchors + occupancy qualifier | **да** | `P2.anchor.sun/moon/asc/mc/element/rhythm` · `P2.selected_life_path` | 1 тезис на опору; пустое omit |
| `K03` | Прикладной смысл углов и домов **этого** человека | `F05` `F06` (+ занятые `F03`) | Angle `orientation` · House `arena` · Planet×House compose | CE Act II applied: `how` + `do` на зону. Не «7-й дом = партнёрство» | 12 house packs + 2 angle packs stored; catalog `draft` | `character_engine_house_lines_v0` / `asc_v0` | есть how/do; IL occupancy в Stage 1 **не** входит | **да, full only** | P2 ASC/MC · Explore natal · Matrix «Структура карты» | `how` + `do`; незначимое omit |
| `K04` | Internal Engine: как решает / воспринимает / держит стресс / риск / восстановление / рост / выгорание | `F03` `F04` `F07` `F08` + ядро | Planet function · Aspect `relation` · IL-2 frames | CE Акт III: правила работы, не качества. Capability L2 `decision_style` / L3 perception — **алиасы**, не отдельные корни | IL-2 compose 616 cells; CE Stage 3 prompts существуют | правило канона есть | first-paint **не** держит оси отдельно от K01-шаблона | **да, свёрнуто** | `P3.insight` / node (не 7 виджетов) · Matrix «Решения» | механизм; пустая ось omit |
| `K05` | Одно главное напряжение A↔B | hard `F07`, clash `F08`, конфликт ролей K02 | Aspect `relation` · IL-2 `aspect_pair` | CE Акт IV: ровно одно главное. Content `inner_tension` = alias | аспекты stored; Stage 1 имеет 1 tension-правило (`freedom_vs_stability`) | канон есть | **узко:** только одна ось из реестра, не IL-пара | **да** | внутри `P3.insight` | одна ось, не список |
| `K06` | Вторичные напряжения (1–3), не конкурируют с K05 | то же | то же | CE Акт IV secondary | то же | канон есть | не отдельный слот Inventory | **да как материал узла** | `P3.*` / Explore | короткие оси |
| `K07` | Как K01+K04+K05 проявляются в ситуациях | full усиливает домами `F06` | House `arena` для «где»; сцена ≠ корень | CE Акт V. Matrix «Эмоции / отношения / работа / деньги / дом» = **ярлыки сцен**, запрещены как generative roots | house packs есть | CE + life_spheres projector | сферы рисуются; корни `relationships/career/money` в TARGET запрещены | **да ≤2 сферы на пути** | `P4.sphere.*` · Matrix L2 styles | teaser + expand how/need/risk |
| `K08` | Направление роста (не профессия) | K01+K04+K05 | — (derived) | CE Акт VI | нет отдельного KB | канон: из системы, не новый LLM-корень | `P4.effort_vector` проецируется из `help`, не из потенциала как поля | **да проекцией** | `P4.effort_vector` | 1 вектор поведения |
| `K09` | Слепая зона / честная цена оси | K05 + K04 | — | CE Акт VII | нет отдельного KB | канон есть | нет отдельного слота; должно звучать в P3/P4 | **да внутри узла** | `P3.insight` · `P3.help` | 1 неудобная правда |
| `K10` | Компас: strengths · helps · energy · red flags · practical takeaway | только уже построенные K01–K09 | — | CE Акт VIII **derived only**. Capability `core_strengths` / Matrix `helps[]` = проекции | — | запрет собственного промпта | L3 `helps` gated Trial+; strengths в Inventory не как акт пути | **да derived** | `P3.help` · `P4.effort_vector` · Matrix helps (Trial+) | список следствий; empty omit |
| `K11` | Дуга пути личности (вообще, не сегодня) | K01+K05+K08 | `F09` как evidence, не заголовок | CE Финал | number_base для цифры; дуга — композиция | канон есть | `P5.bridge_line` = мост в Today из `node.kind`, **не** финальная дуга жизни | **частично** | `P5.bridge_line` | 1 предложение «почему открыть Today» |
| `K12` | Что life path / birthday вносят в **этого** человека | `F09` | `number_base_v1` 1–9, 11/22/33 | вклад в K01/K02, не статья «число 7 означает» | **есть** JSON bank | lookup + CE evidence | `P2.selected_life_path` calc; смысл часто банк/LLM | **да** | P2 life_path · P1 visual seed | имя/число + вклад, не энциклопедия |
| `K13` | Что имя-числа вносят в самопрезентацию | `F10` | тот же bank | Capability L1 `name_expression`; omit без имени | bank есть | канон: не влиять на натал | `P2.name_numerology` compact Why | **да** | Why header fact, не акт пути | omit + CTA без имени |
| `K14` | Культурные соответствия знака/даты | `F12` | header pack · chinese/tibetan services · sign stones/colors | **lookup**, не LLM. Нет ключа → omit | цвета hardcoded; камни из sign catalog; год — сервисы | Matrix closed decision #10 | `P2.correspondence` compact Why | **да** | Why header fact, не акт пути | ключ+ярлык; без выдумки |
| `K15` | Как карта объясняет уже известное ядро | весь natal pack + K01 (+ K05) | IL-4 phrase pack на decode | opt-in POST; не personality root; не Today/Compat SoT | IL-4 bind 1.3.123; catalog draft | [PROFILE_NATAL_DECODE_DEPTH_V1](./PROFILE_NATAL_DECODE_DEPTH_V1.md) | CTA + cache; GET не генерит | **да opt-in** | `P6.natal_decode` | история карты поверх fixed core |
| `K16` | Практические tips выбранной deep-темы | K07 база неизменна | — | L3 Paid/Trial: 1–2 темы, не переписывать how/need/risk | — | CE deep themes | endpoint есть | **да Trial+** | expand сферы / deep-themes | `practical_tips[]` |
| `K17` | Чего нет и что откроется | `unavailable` из Capability | — | всегда честность; не invent | — | Matrix §1.1 copy | `P-data.*` | **да** | `P-data.cta_text` · `P-forming.message` | CTA ввода / forming chrome |
| `K18` | Как это уже проявлялось в отметках | `F13` | — | Content `source_depth`; запрет паттернов на `birth_data_only` | — | Content §3 | слот есть; пусто omit | **да если есть** | `P3.living_evidence` | «вы отметили», не диагноз |

**N = 18. Конец списка.**

Слоты chrome (`P*.step_title`, `TF.no_connection`, CTA Today) — не знания. Они остаются в Display Inventory.

---

## 4. Что покрыто / чего нет

Сводка по базе, не по желаемому экрану.

| Есть | Нет / дырка |
|------|-------------|
| Считать `F01`–`F11` (Swiss + numerology) | IL catalog **38 draft / 0 active**; product surfaces ignore `draft` |
| Planet Canon Sun–Saturn · Sign manner ×12 · House arena ×12 · Aspect relation ×5 · Angle ASC/MC | Uranus/Neptune/Pluto objects withheld · DSC/IC out of V1 · Mars psych `ACCESS_BLOCKED` · sign later-interpretive `DEFERRED_V1` |
| IL-2/3 compose 616 cells на library layer | **CE не импортирует IL.** Occupancy дома на Stage 0 хранится и не матчится |
| Number base 1–9 / 11/22/33 | Отдельный смысл personal_year vs life_path — только bridge, не вторая таблица (канон чисел) |
| Header catalog цвет/камень/CN/TB | Растения / ведический ярлык как накопленный ключ — заявлено Matrix, единого pack нет |
| Display Inventory путь из 5 актов | Имя-нумерология и соответствия шапки есть в Matrix 3.1 и **нет** как `slot_id` |
| Natal Decode opt-in + IL-4 polish | First-paint `K01` = 13 шаблонов по солнцу/луне/ASC |

Главный дефект покрытия (уже измерен, 2026-09-20): два натала с одним Солнцем Девы и разным Марс×дом дают разные IL-2/3 кадры и **один** Identity Core. Это не недостаток «ещё одного слоя» — это `K01`/`K02` без правила, которое потребляет planet×sign×house.

---

## 5. Product selection (M) — что Profile показывает

Не новое решение. Восстановлено из Display Inventory (путь) + Matrix 3.1 (approved blocks).

**На пути (Recognition → Why → Insight → Effort → Bridge):**

| Знание | Показ |
|--------|--------|
| `K01` | да — герой |
| `K02` + calc `F01 F04 F05 F09` | да — Why anchors |
| `K04` `K05` `K09` | да — один узел Insight, не склад |
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
| IL-2/3/4 + wire + attach + consume + polish | library → editorial voice | атомы для `K01`–`K03`/`K15`; first-paint CE их не читает |
| CE Stage 1 13-key registry | mint thesis_key по солнцу/луне/ASC | **уже**, чем N; режет `K01` до ведра |
| Disclosure funnel identity→styles→patterns→spheres | legacy LLM корни | TARGET запрещает как SoT; CODE Δ |
| Life spheres projector | сцена → карточка | presentation `K07`, не новый тип |
| Profile meaning polish 1.3.123 | IL-4 на decode | только `K15` |
| Knowledge-to-output harness | фиксирует схлопывание | диагностика, не контракт |
| Day Sources / vedic / bazi в Profile×Day matrix | факты дня | **не** Profile N; Today/overlay |

Документы, которые описывают **слоты, доступ или каскад**, но не заменяют эту таблицу: Display Inventory · Matrix 3.1 · Capability allowed_output · Content Canon §4 · CE Scenario.

Где они расходятся — побеждает: **N = этот файл** · композиция = CE · UI слот = Inventory. Capability/Content поля = aliases строк §3.

---

## 8. Незакрытые конфликты документов (не резались молча)

| Конфликт | Стороны | Что делает этот файл |
|----------|---------|----------------------|
| Состав экрана | Matrix: шапка → структура → стили сфер. Inventory: 5 актов пути + Explore | N не выбирает IA. M пути = Inventory; Matrix 3.1 остаётся approved access/reveal |
| Имя / камень в шапке | Matrix слоты есть; Inventory `slot_id` нет | знание `K13`/`K14` допустимо; **показ на пути не закрыт слотом** — дыра display, не новое знание |
| `sun_sign_meaning` как L1 поле | Capability vs CE «одна мысль» | схлопнуто в `K01`/`K02`. Отдельной статьи знака нет |
| Chinese/Tibetan как evidence личности | CE Пролог vs Stage 1 rules | как **факт** `F12` и lookup `K14` — да. Как mint `K01` — в live реестре **нет** |

Owner может сузить M (убрать показ), не расширяя N.

---

## 9. Другие разделы

Тот же закон, другие таблицы. **Этим файлом не заполняются.**

| Раздел | Контракт (ещё не этот жанр) | Сейчас вместо N |
|--------|-----------------------------|-----------------|
| Today | нужен `TODAY_INFORMATION_CONTRACT` | pipeline + Display Inventory слоты — механизмы и показ без закрытого N «что можно знать из неба×натала» |
| Compatibility | то же | два Profile N + pair derivation (не написано как конечное множество) |
| Tarot | то же | card_base + question/spread; не закрытый N ответа |
| Практики | taxonomy + coverage ledger | метод/item, не «знание о человеке» |

Пока Profile N не является gate в коде, не начинать Today N «заодно».

---

## 10. Следующий шаг (не код смысла)

1. Считать этот файл SoT информационного пространства Profile.  
2. Любая генерация / слот / IL-wire в first-paint обязана указать `PIC-K*` + `PIC-F*`. Нет строки — нет работы.  
3. Закрыть display-дыры `K13`/`K14` (Inventory row) **или** вычеркнуть их из M — отдельное продуктовое решение, не новое знание.  
4. Чинить `K01` wire (IL planet×sign×house → CE claim) **только** как покрытие уже названного `K01`/`K02`, не как новый слой.  
5. Today Information Contract — следующий раздел, той же формой таблицы, после того как Profile N принят как gate.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-09-20 | v1 reconstruction: 6 inputs · 13 facts · **18 allowed knowledge**. Ничего не добавлено сверх существующих канонов. |
