# Today Information Contract v1

**Status:** CLOSED / PASS — close-out 2026-09-21. N=20 frozen.  
**Date:** 2026-09-21  
**Kind:** reconstruction. **Новых типов знаний нет.**  
**Не заменяет:** [TODAY_CONTENT_PIPELINE_V1](./TODAY_CONTENT_PIPELINE_V1.md) (I0 · owner · порядок вычисления) · [DAY_SOURCES_CANON](../DAY_SOURCES_CANON.md) (расчёт фактов неба/чисел) · Display Inventory (слоты UI) · Availability Matrix (доступ / reveal)

Цепочка (закон):

```text
source input
  → calculated fact
  → allowed knowledge          ← этот файл: конечное N
  → derivation / composition   ← Pipeline I0 / Engine / Overlay / catalog
  → product field (M ⊆ N)      ← что Today имеет право показывать
  → display slot               ← TODAY_DISPLAY_INVENTORY_V1
  → visible text
```

Если у текста нет этой цепочки — в продукте его нет. LLM не заполняет пробел.

**TIC-K\* ≠ PIC-K\*.** Identity Core, 13-key registry и Character Engine prose **не** входят в Today N. Profile train закрыт и не является источником Today-работы.

---

## Architecture impact

- **SoT before:** «что система имеет право знать про день» было размазано между Pipeline ownership, Day Sources families, Display Inventory слотами, Matrix 3.2 (каркас), Screen Contracts `today_contract_v1` и native C1 leftover. Механизмы (Engine, overlay, ritual, polish, depth) строились без конечного N.
- **SoT after:** этот файл — **закрытый перечень** фактов и допустимых знаний Today **и обязательный code gate**. Pipeline остаётся SoT I0 / non-mutation / кто решает. Display Inventory остаётся последним authority перед UI. Day Sources остаётся SoT расчёта. Строка вне таблиц §1–§3 **не существует** как содержание Today. Нет `TIC-K*` + зависимых `TIC-F*` — meaning-работа не начинается (chrome/ошибки исключены).
- **Public contract changed?** no JSON
- **Migration required?** no
- **Canon updated?** yes — этот файл · `today/_INDEX.md` · `docs/README.md` · Grammar §1 · Display Inventory pointer · Pipeline pointer · PIC §9 · tracker · handoff
- **Backward compatible?** yes for API. Gate живёт в `today_information_contract_v1.py`. Census существующих продюсеров — следующий hop, не этот start.

## Architecture impact — TIC close-out (2026-09-21)

- **SoT before:** §11 coverage table recorded 20 COMPLETE. That table is a hop ledger, not an independent close-out.
- **SoT after:** this file is **CLOSED / PASS**. Close-out re-executed the assembled chain (four acceptance blocks) without inventing K21 and without product fixes inside the gate. Inventory remains last UI authority. Glance leftover is **out of TIC locked-surface scope**. Next product gate is chosen from canon, not from TIC inertia.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this file §10/§12 · tracker · frozen handoff
- **Backward compatible?** yes. Gate: `evaluate_tic_closeout` in `today_information_contract_v1.py`. Coverage-table COMPLETE is not accepted as proof.

## Architecture impact — TIC-K01 human_line (2026-09-21)

- **SoT before:** Engine `pick_primary_energy` already chose the 8-set kind; `T1-hero.energy_word` painted it; `T1-hero.human_line` painted warm greeting / theme / period / expect.
- **SoT after:** same Engine energy. `human_line` is a closed 8-set formulation of that `primary_energy`. Greeting stays chrome. Missing/unknown omit. Not a second selector. Overlay does not change the shared-day kind.
- **Public contract changed?** no JSON fields
- **Migration required?** no
- **Canon updated?** yes — this file §3/§11 · Display Inventory `T1-hero.human_line` · this tracker · handoff
- **Backward compatible?** yes for API. Hero body wording changes from greeting to the chosen energy's sentence.

## Architecture impact — TIC-K06 overlay thesis (2026-09-21)

- **SoT before:** `day_personal.summary_ru` concatenated personal_astrology + HD + BaZi + Vedic + electional + name_numbers. T3.headline painted that mash.
- **SoT after:** same slot/field. `summary_ru` copies the already-derived F09 natal_transit thesis from `personal_astrology.summary_ru`. OUT families remain in the pack and do not feed K06. No overlay transit → omit. Not why_personal, not T1 human_line, not a new K.
- **Public contract changed?** no new JSON fields. `summary_ru` semantics = overlay thesis, not kitchen mash.
- **Migration required?** no. Cached packages may keep old mash until rebuild.
- **Canon updated?** yes — this file §3/§11 · Display Inventory `T3.headline` · tracker · handoff
- **Backward compatible?** yes for API. MY DAY headline omits when overlay transit is missing instead of filling HD/BaZi.

## Architecture impact — TIC-K07 overlay axis (2026-09-21)

- **SoT before:** F10 was named; `personal_day.natal_overlay.focus_axis` was not written. FE `pickPersonalFocusAxisLabel` filled `T3.focus_title` from Global `scenes[primary].sphere` (and kitchen overlay aliases).
- **SoT after:** same slot. F10 = closed 4-set domain of the already-chosen F09 natal_transit natal_point via existing `DOMAIN_NATAL_POINTS` order. Nest writer sets `natal_overlay.focus_axis`. FE map_label that id only; omit without it. Not a second ranker. Not kitchen / PIC / CE / chrome. Not T1-hero.human_line or T3.headline.
- **Public contract changed?** yes — `personal_day.natal_overlay.focus_axis` is now produced as F10 (`work|money|relationships|energy`). Leftover kitchen keys are not the slot source.
- **Migration required?** no. Cached packs without the writer omit the title until rebuild. Not a cache-migration hop.
- **Canon updated?** yes — this file §3/§10/§11 · Display Inventory `T3.focus_title` · tracker · handoff
- **Backward compatible?** yes for API. MY DAY focus title omits when overlay transit has no mapped natal point instead of filling a Global scene sphere.

## Architecture impact — TIC-K09 personal do (2026-09-21)

- **SoT before:** `day_story.do[]` / `today_move` copied Global scene `recommended_action` / `props.goals`. FE `pickMyDayPriorityLines` painted that list as `T3.priority`.
- **SoT after:** same slot. `do[]` is Personal Narrative after bind only. I0-locked Global action is not personal do. No Personal-owned do field on the locked overlay schema → omit. Not a second ranker. Not kitchen / PIC / CE / chrome. Not K01/K06/K07. Glance leftover unchanged except it cannot treat Global scene action as personal `today_move`.
- **Public contract changed?** yes — `day_story.do[]` / `today_move` may be empty on an ok interpretation (omit). No new JSON fields. Semantics = Personal Narrative do or empty.
- **Migration required?** no. Cached packs whose `do[]` equals scene `recommended_action` omit the slot until rebuild.
- **Canon updated?** yes — this file §3/§10/§11 · Display Inventory `T3.priority` · tracker · handoff
- **Backward compatible?** yes for API. MY DAY priority omits when Personal Narrative did not write do, instead of filling Global action.

## Architecture impact — TIC-K14 number lens (2026-09-21)

- **SoT before:** `T2.lens_number` painted `number.hook_reveal.bridge_to_day` from Global `interpretive_chorus.day_number` (link / tempo mash). Persist / `profile_depth==deep` existed; provenance was chorus, not Personal×number.
- **SoT after:** same slot. `personal_angle` is Personal Day × F11/F12 after persist only. I0-locked Global chorus stays on `interpretive_chorus.day_number` / `bridge_to_day` (including tempo/style) and does not feed K14. Locked Personal overlay has natal / why_personal / scene personalization — no number-lens field → omit. Not a second ranker. Not a copy of K06–K10. Not a copy of K13 card path. Not kitchen / PIC / CE / chrome. Not K15+.
- **Public contract changed?** no new JSON fields. `personal_angle` remains `omit` without Personal×number. Semantics of `T2.lens_number` = Personal lens or empty.
- **Migration required?** no. Cached packs whose lens equals chorus `bridge_to_day` omit the slot until a Personal×number line exists.
- **Canon updated?** yes — this file §3/§10/§11 · Display Inventory `T2.lens_number` · tracker · handoff
- **Backward compatible?** yes for API. Ritual number «Для тебя сегодня» omits when Personal×number did not write the lens, instead of filling Global chorus.

## Architecture impact — TIC-K15 color (2026-09-21)

- **SoT before:** `T3.color.*` / `color_guide` scored catalog rows from scene trap/sphere/mode tags via `_needed_color_tags` → existing `score_color_for_needs`. F05 `primary_energy` and F09 overlay activations sat nearby and did not choose the color. Catalog/talisman leftover could still fill the nest.
- **SoT after:** same slot and the same scorer. Needed tags are a closed F05 8-set lookup plus F09 domain via existing `DOMAIN_NATAL_POINTS` / `overlay_focus_axis_from_natal_point`, plus existing `day_favorable` celebration tags. Scene trap/sphere/mode are not K15 input. No second scorer. Scent/stone stay aliases without a slot. Missing grounded F05+F09 → omit. Catalog presence without that pick does not paint.
- **Public contract changed?** no new JSON fields. `color_guide` / `props.color` may be null on an ok interpretation (omit). Semantics = F14 pick after Personal persist, or empty.
- **Migration required?** no. Cached packs whose color came from scene tags omit or rescore until rebuild. Not a cache-migration hop.
- **Canon updated?** yes — this file §3/§10/§11 · Display Inventory `T3.color.*` · tracker · handoff
- **Backward compatible?** yes for API. MY DAY color omits when F05+F09 did not ground a pick, instead of filling scene tags or morning catalog.

## Architecture impact — TIC-K20 honesty (2026-09-21)

- **SoT before:** `T3.unavailable` painted honesty copy, but MY DAY still mounted `extraCards` (practice/affirmation/tasks) on the unavailable pane.
- **SoT after:** same slot. Unavailable MY DAY is only `T3.unavailable`. extraCards omit. Global scene/kitchen/chorus and empty K16/K17 do not fill the pane. Not a new meaning root. Glance leftover is not this hop.
- **Public contract changed?** no JSON fields. Semantics of unavailable MY DAY = honesty chrome only.
- **Migration required?** no
- **Canon updated?** yes — this file §3/§10/§11 · Display Inventory `T3.unavailable` · tracker · handoff
- **Backward compatible?** yes for API. Unavailable MY DAY no longer shows leftover practice/affirmation cards.

## Architecture impact — TIC-K17 XOR (2026-09-21)

- **SoT before:** `T3.affirmation` painted scene `props.affirmations[0]` / trap / `recommended_action` via `practice_recommendation`. Date-hash rotation picked practice vs affirmation when both existed. Catalog miss could leave the scene affirmation as fill.
- **SoT after:** K17 is XOR, not a new selector. Content mode is the existing K16 F10 need-cell class (`content_class=practice`). Exactly one Inventory slot: practice XOR affirmation. Scene affirmation is not Personal verbal support. Empty selected branch omits; it does not switch type for fill. Date-hash / availability / leftover catalog item do not choose the branch. K16 select query unchanged. Not K20 extraCards. Glance leftover is not this hop.
- **Public contract changed?** no JSON fields. `practice_recommendation` may be empty on an ok interpretation (omit). Semantics of `T3.affirmation` = Personal verbal support on the affirmation branch, or empty.
- **Migration required?** no. Cached scene-affirmation rec omits on the locked surface until rebuild.
- **Canon updated?** yes — this file §3/§10/§11 · Display Inventory `T3.affirmation` · tracker · handoff
- **Backward compatible?** yes for API. MY DAY never shows affirmation and practice together; affirmation omits without a grounded Personal branch.

## Architecture impact — TIC-K16 practice (2026-09-21)

- **SoT before:** `T3.practice` retrieved one catalog item via existing `GET /practices/select`, but the need cell came from Global `primary_energy` (K01 8-set) through `GLOBAL_ENERGY_NEED`. Personal `focus_axis` sat nearby and did not choose the technique.
- **SoT after:** same slot and the same selector. Need is the closed F10 4-set `personal_day.natal_overlay.focus_axis` mapped to an existing purpose/direction/context cell with `content_class=practice`. Global `primary_energy` does not feed K16. Compensating Personal Risk is not a today_contract field — do not invent it from K10 prose or Global F06. No second selector. Guest / missing F10 / unavailable interpretation → omit. XOR with affirmation is K17.
- **Public contract changed?** no JSON fields. Meaning still does not emit `item_id`. Semantics of `T3.practice` = catalog item from F10, or empty.
- **Migration required?** no. Cached Global-energy picks omit until F10 is present on the contract.
- **Canon updated?** yes — this file §3/§10/§11 · Display Inventory `T3.practice` · tracker · handoff
- **Backward compatible?** yes for API. MY DAY practice omits when F10 did not ground a select, instead of filling Global energy.

## Architecture impact — TIC-K13 card lens (2026-09-21)

- **SoT before:** `T2.lens_card` painted `card.hook_reveal.bridge_to_day` from Global `interpretive_chorus.day_card`. Persist gate existed; provenance was chorus, not Personal×card. `personal_angle` unused on attach.
- **SoT after:** same slot. `personal_angle` is Personal Day × F13 after persist only. I0-locked Global chorus stays on `interpretive_chorus.day_card` / `bridge_to_day` and does not feed K13. No Personal-owned card-lens field on the locked overlay schema → omit. Not a second ranker. Not a copy or inversion of K06–K10. Not kitchen / PIC / CE / chrome. Not K14+.
- **Public contract changed?** no new JSON fields. `personal_angle` remains `omit` without Personal×card. Semantics of `T2.lens_card` = Personal lens or empty.
- **Migration required?** no. Cached packs whose lens equals chorus `bridge_to_day` omit the slot until a Personal×card line exists.
- **Canon updated?** yes — this file §3/§10/§11 · Display Inventory `T2.lens_card` · tracker · handoff
- **Backward compatible?** yes for API. Ritual «Для тебя сегодня» omits when Personal×card did not write the lens, instead of filling Global chorus.

## Architecture impact — TIC-K10 personal avoid (2026-09-21)

- **SoT before:** `day_story.avoid[]` copied Global scene `do_not`. FE painted that list as `T3.caution`.
- **SoT after:** same slot. `avoid[]` is Personal Narrative after bind only. I0-locked Global `do_not` / `avoid_action` stay on the Global scene contract and do not feed K10. No Personal-owned avoid field on the locked overlay schema → omit. Not a second ranker. Not an inversion of K09 `do[]`. Not kitchen / PIC / CE / chrome. Glance leftover is not this hop.
- **Public contract changed?** yes — `day_story.avoid[]` may be empty on an ok interpretation (omit). No new JSON fields. Semantics = Personal Narrative avoid or empty.
- **Migration required?** no. Cached packs whose `avoid[]` equals scene `do_not` omit the slot until rebuild.
- **Canon updated?** yes — this file §3/§10/§11 · Display Inventory `T3.caution` · tracker · handoff
- **Backward compatible?** yes for API. MY DAY caution omits when Personal Narrative did not write avoid, instead of filling Global do_not.

---

## 0. Откуда таблица (ничего не придумано)

| Слой | Документ | Что взято |
|------|----------|-----------|
| Ввод | [PRODUCT_DATA_INTAKE](../PRODUCT_DATA_INTAKE.md) · [TODAY_CONTENT_PIPELINE_V1](./TODAY_CONTENT_PIPELINE_V1.md) I0 keys | дата дня · TZ · locale · birth · owner · stated |
| Факты неба | [DAY_SOURCES_CANON](../DAY_SOURCES_CANON.md) v1 in_today | Луна · тела · аспекты · ingress/stations · universal/personal number |
| Смысл дня | Pipeline ownership + I0 | Global Day · Natal Overlay · Personal Day · ritual lenses · enrichments |
| Показ | [TODAY_DISPLAY_INVENTORY_V1](./TODAY_DISPLAY_INVENTORY_V1.md) | M: какие слоты рисуем |
| Цикл | [TODAY_PRODUCT_FLOW_V1](./TODAY_PRODUCT_FLOW_V1.md) | TODAY → RITUAL → MY DAY → EVENING |
| Доступ | [PRODUCT_AVAILABILITY_MATRIX](../PRODUCT_AVAILABILITY_MATRIX.md) §1 · §3.2 | guest catalog; Personal omit; depth Trial+ |
| Карта / число | [TAROT_CARD_BASE_V1](../tarot/TAROT_CARD_BASE_V1.md) · [NUMBER_BASE_V1](../numerology/NUMBER_BASE_V1.md) | catalog, не причина дня |
| Depth | [TODAY_DEPTH_LAYER_V1](../TODAY_DEPTH_LAYER_V1.md) | опциональный слой поверх полного дня |
| Атомы | [INTERPRETATION_LIBRARY_V1](../astrology/INTERPRETATION_LIBRARY_V1.md) | lookup шага 2; не второй канон дня |

Алиасы (одно знание, много имён) схлопнуты в один `TIC-*`. Это не новое знание.

**Запрещено этим файлом:** добавить строку «потому что Day Sources / native C1 умеет». Новый `TIC-*` — только Architecture impact + строка в changelog.

---

## 1. Source input (закрыто)

Ровно то, без чего Today не из чего считать. Birth-поля — **вход дня**, не Personality N.

| ID | Ввод | Без него |
|----|------|----------|
| `IN.local_date` | гражданская дата дня | нет Today |
| `IN.locale` | locale | язык формулировки, не смысл |
| `IN.tz` | timezone дня | нет day interval / окон |
| `IN.place` | lat/lon | omit horizon/VOC/rise; Global Day без geo остаётся |
| `IN.birth_date` | дата рождения | нет Personal Day · нет Personal Day Number · Ritual number = Universal |
| `IN.birth_full` | время + место рождения | нет house/angle overlay claims |
| `IN.owner` | identity ключа | нет стабильного Ritual hash / PersonalDayKey |
| `IN.stated` | evening gratitude · habits · First Today chips | нет continuity / tracker / living day-record |

Других входов для Today нет. Карта дня, IL-лемма, цвет, практика — не ввод пользователя, а расчёт / lookup / scoring **после** фактов.

Character Engine snapshot, `recognition_line`, insight nodes, Natal Decode essay — **не входы**.

---

## 2. Calculated facts (закрыто)

Считается детерминированно. Это ещё не «знание о дне». Нет факта → нет зависимого `TIC-K`.

| ID | Что считаем | Из ввода | Где считается | Gate |
|----|-------------|----------|---------------|------|
| `F01` | Луна: фаза · illumination · знак · ingress | `IN.local_date`+`IN.tz` | Day Sources `moon` | дата |
| `F02` | Тела Sun–Pluto: знак · скорость · Rx на day interval | дата+TZ | Swiss / western_astrology | дата |
| `F03` | События неба: majors exact · ingress · stations/Rx edge · seasonal solar | `F02` | Day Sources v1 | дата |
| `F04` | Ranked drivers 1–3 (+ supporting) | `F01`–`F03` | Global Day Engine | дата |
| `F05` | `primary_energy` · scores · mood (тот же 8-set) | `F04` | Engine scoring | дата |
| `F06` | Global `strength[]` / `risk[]` (типы действий) | `F04`/`F05` | Engine | дата |
| `F07` | `windows[]` {time, driver, supports, cautions} | `F03`+`F04` | Engine | дата |
| `F08` | Natal snapshot (birth facts; **не** реминтится ради Today) | `IN.birth_*` | Profile calc, consume | дата / full |
| `F09` | Natal overlay activations (небо × натал) | `F02`/`F03` × `F08` | Natal Overlay | birth; house-claims — full |
| `F10` | Overlay closed-set axis (уже выбранный domain) | `F09` | Overlay select | overlay |
| `F11` | Universal Day Number | `IN.local_date` | numerology | дата |
| `F12` | Personal Day Number | `IN.birth_date` + дата | numerology | birth_date |
| `F13` | Card id + orientation | `IN.owner` + дата hash | Ritual Engine | owner |
| `F14` | Color identity (scored catalog pick) | `F05`+`F09` + color catalog | color scoring **после** Personal | Personal persist |
| `F15` | Yesterday gratitude record | `IN.stated` | DayConnection `evening_completed` | D2+ closed evening |
| `F16` | Today user records: gratitude write · habits · First Today chips | `IN.stated` | user persist | stated |

**Явно OUT как факты Today (уже в каноне, не в N):** прогрессии / соляр / returns · минорные аспекты · Nodes/Chiron/Lilith как IL-gold · Vedic / BaZi / HD · electional/horary без явного слота · planetary hours / weekday ruler как отдельный смысл · `calendar_day_number` planned · scent/stone как **отдельный** расчёт (алиас `F14`/`K15`, без слота → не показываем).

Code Δ: Capability TARGET vs CODE для natal facts не меняет **набор полей** этой таблицы.

---

## 3. Allowed knowledge (N = 20)

Что система **имеет право знать** из §2. Не «что ещё интересно вывести из неба».

Колонки покрытия:

- **KB** — есть ли knowledge atom / каталог / closed set
- **Rule** — есть ли правило derivation (не промпт «напиши красиво»)
- **Wire** — доходит ли до package / слота, не схлопываясь

| ID | Что знаем | Факты | Atoms / KB | Derivation | KB | Rule | Wire | Show? | Где | Формат |
|----|-----------|-------|------------|------------|----|------|------|-------|-----|--------|
| `K01` | Какой это **общий** день (вид энергии) | `F05` (`F04`) | closed 8-set `grounded\|flow\|radiance\|momentum\|clarity\|tension\|renewal\|depth` | Engine argmax; LLM **не** выбирает; human_line = формулировка уже выбранного, не отдельный корень | 8-set + label map + closed sentence map | Pipeline §3 | energy_word live; human_line = formulation of `primary_energy` | **да** (guest+) | `T1-hero.energy_word` · `energy_pct` · `mood` · `human_line` · `sheet` | слово + % + 1 предложение; пустое omit |
| `K02` | Какие влияния неба **ранжированы** для этого дня | `F01`–`F04` | IL canonical line того факта | Engine rank 1–3 + moon row; 4-й драйвер запрещён | IL draft; ranking v1 | Engine | transit rows | **да** | `T1-clock.transit` · `sheet` | ≤1 moon + 3 drivers; untitled omit |
| `K03` | Какие **типы действий** общий день поддерживает | `F06` strength | closed action-type set | Engine; не сферы жизни | type labels | Engine | chips | **да** | `T1-strength.chip` · `sheet` | ≤4 chips; пусто omit |
| `K04` | Какие **типы действий** в глобальном риске | `F06` risk | тот же set | Engine; ≠ personal avoid | type labels | Engine | chips | **да** | `T1-risk.chip` · `sheet` | ≤3 chips; пусто omit |
| `K05` | Когда support/caution по часам (authority = Engine windows) | `F07` (+ `F09` для natal clocks) | windows schema | Engine считает; Personal Timeline = **показ** тех же окон × natal, не второй timeline SoT | windows v1 | Pipeline timeline | T1 clock; T3 rhythm | **да** | `T1-clock.range` · `spectrum` · `T3.rhythm_row` | HH:MM; «мой» только при natal; иначе «Ритм дня» |
| `K06` | Главный **персональный тезис** дня | Global + `F09` | — | Personal Day = Global × Overlay; **не** CE; **не** `why_personal`; **не** T1 human_line | overlay natal_transit | Pipeline §6 | `day_personal.summary_ru` = overlay thesis (omit if no F09 transit) | **да, persist Personal** | `T3.headline` | 1 мысль; guest omit |
| `K07` | Ось / область, где тезис проявляется | `F10` (`F09`) | closed 4-set `work\|money\|relationships\|energy` | first natal_transit natal_point → existing `DOMAIN_NATAL_POINTS` (DOMAINS order); LLM free title = drift; не scene sphere; не K01/K06 prose | domain ids | Overlay | `personal_day.natal_overlay.focus_axis` | **да, если ось выбрана** | `T3.focus_title` | 1 слово map_label; нет оси → omit |
| `K08` | Как тезис проявляется на этой оси | overlay fields | — | `why_personal` first; не `development_point`; не CE | Personal nest | Pipeline | focus_body | **да, persist Personal** | `T3.focus_body` | 1–2 предл.; overlap headline drop |
| `K09` | Что конкретно сделать в сегодняшней ситуации | Personal Narrative after bind (`F09` persist) | — | Personal-owned do after bind; не Global `recommended_action` / goals; glance leftover только personal `today_move` ≠ scene action; нет основания → omit | Personal Narrative | Pipeline §6–7 | `day_story.do[]` empty unless Personal Narrative wrote it | **да, persist Personal** | `T3.priority` | 1–3 пункта; пусто omit |
| `K10` | Где персональный риск | Personal Narrative after bind (`F09` persist) | — | Personal-owned avoid after bind; не Global `do_not` / `avoid_action`; не инверсия K09 `do[]`; нет основания → omit | Personal Narrative | Pipeline §6–7 | `day_story.avoid[]` empty unless Personal Narrative wrote it | **да, persist Personal** | `T3.caution` | 1–2 пункта; пусто omit |
| `K11` | Что карта значит **в каталоге** | `F13` | tarot card_base | lookup; не «день такой из-за карты» | catalog | Ritual | catalog_card | **да** (guest catalog) | `T2.catalog_card` · `T2.card_face` | 2–4 предл. или omit |
| `K12` | Что число значит **в каталоге** | `F11` или `F12` | number_base | Personal Day Number если birth, иначе Universal; не продуктовый Personal Day | bank | Ritual / numerology | catalog_number | **да** (guest catalog) | `T2.catalog_number` · `T2.number_glyph` | catalog или omit |
| `K13` | Как карта окрашивает **уже persisted** Personal Day | K06–K10 × `F13` persist | catalog as color, not cause | шаг 9 Pipeline; Personal-owned lens after persist; не Global chorus `day_card` / `bridge_to_day`; не копия K06–K10; нет основания → omit; CE forbidden | lens | Pipeline §8–9 | `card.hook_reveal.personal_angle` empty unless Personal×card wrote it | **да только persist Personal** | `T2.lens_card` | 1–3 предл.; guest/general omit |
| `K14` | Как число окрашивает **уже persisted** Personal Day | K06–K10 × `F11`/`F12` persist | catalog as color, not cause | шаг 9 Pipeline; Personal-owned lens after persist; не Global chorus `day_number` / `bridge_to_day` / tempo; не копия K06–K10; не копия K13; persist-gate ≠ coverage; нет основания → omit; CE forbidden | lens | Pipeline §8–9 | `number.hook_reveal.personal_angle` empty unless Personal×number wrote it | **да только persist Personal** | `T2.lens_number` | 1–3 предл.; guest/general omit |
| `K15` | Какой один цвет как опора **этого** дня | `F14` (`F05`+`F09`) | color catalog | existing `score_color_for_needs` after energy + natal overlay; scene trap/sphere/mode **не** вход; LLM не выбирает цвет; scent/stone = **алиас**, не отдельный корень, слота нет → не показываем; нет F05+F09 → omit | color nest | Inventory `T3.color` | `color_guide` from `props.color` F14 pick only | **да, persist Personal** | `T3.color.*` | name+hex+lines; пустые lines не fill-empty |
| `K16` | Какая одна готовая техника поддержки | `F10` (Personal focus) | practice technique canon | existing `GET /practices/select` from F10 4-set need cell; `content_class=practice`; не Global `primary_energy`; не LLM pick; ≠ `T3.priority`; compensating risk не invent из K10/F06; нет F10 → omit; XOR с K17 | library | Content Library | FE select after persist Personal | **да, persist Personal** | `T3.practice` | 1 item; пусто omit |
| `K17` | XOR: вербальная опора **или** техника, не оба | F10 content class (existing K16 need cell) · Personal affirmation field | — | existing content mode = K16 `content_class` of the F10 cell; ровно одна ветка; scene `affirmations` / trap / `recommended_action` **не** вход; date-hash / availability / leftover catalog **не** выбирают ветку; пустая выбранная ветка → omit, не switch; ≠ CE identity; ≠ rewrite priority | field | Pipeline · K16 class | XOR slot | **да, persist Personal** | `T3.affirmation` xor `T3.practice` | 1 предл. или 1 item; пусто omit |
| `K18` | Опциональное углубление **выбранной** темы | полный base day + topic | depth topic menu | Trial+ generate; Free = CTA; не второй сюжет дня | [TODAY_DEPTH_LAYER_V1](../TODAY_DEPTH_LAYER_V1.md) | Matrix 3.2 | `T3.depth` | **да поверх дня** | `T3.depth` | CTA или pack; omit если нет offer |
| `K19` | Что вчерашний вечер оставил сегодняшнему утру | `F15` | — | user record; не invent смысла дня; не «получилось/нет» | gratitude | Inventory continuity | `T1.continuity` | **да D2+** | `T1.continuity` | 1–2 предл.; пусто omit |
| `K20` | Чего нет и что откроется | capability / persist gaps | Matrix copy | честность: guest MY DAY omit; unavailable = только `T3.unavailable`; extraCards/practice/affirmation **не** surrogate; no natal → no K06–K10/K13–K17; transport ≠ fake calm | — | Matrix · Grammar §2 | `T3.unavailable` · guest omit · extraCards omit | **да** | `T3.unavailable` · `TF.*` | «Не удалось загрузить.» / omit meaning |

**N = 20. Конец списка.**

Слоты chrome (`T1-date.eyebrow`, `T2-gate.*`, `T4.title`, `SF.next.*`, `T3.tasks_empty`) и user-write Evening (`T4.text` / categories) — не знания о дне. Tracker / First Today chips — user records (`F16`), не mint смысла. Они остаются в Display Inventory.

---

## 4. Что покрыто / чего нет

Сводка по базе, не по желаемому экрану.

| Есть | Нет / дырка |
|------|-------------|
| Считать `F01`–`F07`, `F11`–`F13` (Swiss + Engine + ritual hash + numbers) | IL catalog **38 draft / 0 active**; Today polish биндит chorus к IL-4, не выбирает смысл |
| Pipeline I0: Global без натала; Personal = Global × Overlay | Character Engine как вход Personal Day |
| Inventory путь TODAY → RITUAL → MY DAY → EVENING | DomainLens / 4 сферы SCREEN_CONTRACTS как generative Today N |
| Card/number catalog + lens-after-persist | Карта/число как причина energy/drivers/windows |
| Depth offer поверх полного дня | Второй «premium day plot» |
| Continuity из yesterday gratitude | Evening trap-check / promise-as-meaning |

Исполняемый статус каждой строки — **§11**. JSON/presence ≠ покрытие.

---

## 5. Product selection (M) — что Today показывает

Не новое решение. Восстановлено из Display Inventory + Product Flow + Matrix 3.2 guest/depth.

**Guest:** TODAY Global (`K01`–`K05`) + Ritual **catalog** (`K11` `K12`) + Evening user-write + honesty (`K20`). Lens / MY DAY meaning / color / practice / affirmation — omit.

**С birth_date, Personal persist:** + `K06`–`K10`, `K13`–`K17`. `K05` на MY DAY может показать natal clocks.

**Trial/Paid only generate:** `K18` depth. Base day тот же, что Free.

**D2+:** `K19` если yesterday evening closed.

**Не показываем, хотя движок где-то умеет:**

- энциклопедия аспектов / 20 слабых драйверов
- гороскоп work/money/relationships/health как корни дня
- CE identity / insight / effort / bridge / Natal Decode
- 13-key personality mint
- прогрессии, соляр, Vedic, BaZi, HD, electional как Today N
- независимые генераторы камня/запаха дня
- `T3.action` (снят; Priority владеет «что сделать»)
- Glance Daily Focus как пятый акт
- Personal Timeline на TODAY
- карта/число как причина Global/Personal bind
- fake calm при `is_fallback` / throw

---

## 6. Трассировка до предложения

Каждый видимый meaning-атом обязан уметь заполнить:

```text
этот текст
  ← slot_id                    Display Inventory
  ← TIC-K*                     этот файл (M)
  ← derived conclusion         Engine / Overlay / catalog / Personal Narrative
  ← composition rule           I0 non-mutation · rank · lookup · scoring
  ← knowledge atoms            8-set / IL line / card_base / number_base / color / technique
  ← TIC-F*                     calculated facts
  ← IN.*                       source input
```

Нет любого звена → omit. Не «сформулируй правдоподобно».

Chrome и failure (`«Нет соединения.»` / `«Не удалось загрузить.»`) в эту цепочку не входят: они не знания о дне.

---

## 7. Лишняя обвязка вокруг N

Построено до фиксации конечного множества. Не удаляется этим файлом; не является SoT знания.

| Механизм | Что делает | Отношение к N |
|----------|------------|----------------|
| Day Sources planned families (Vedic, BaZi, HD, nodes, eclipses, electional) | registry / later | **не** Today N V1 |
| native C1 leftover (chorus+conflict+scenes monolith hygiene) | literary scaffold | не выбирает energy/windows; не расширяет N |
| Today meaning polish 1.3.114 | IL-4 на astrology chorus | формулировка `K01`/`K02`, не новый корень |
| `day_scenario` / DayModel §10 / Projector B5 | mapping / hygiene | structure-only; не Meaning SoT |
| SCREEN_CONTRACTS 4 domains | historical payload | не generative N; DomainLens out of Inventory |
| Glance Daily Focus | leftover composition | не пятый акт; не `T3.priority` кроме personal `today_move` |
| Character Engine | личность | **запрещён** как вход Personal Day |
| Profile Information Contract | закрытое N Profile | **не** источник Today-работы; не копировать PIC-K* |

Документы, которые описывают **слоты, доступ или порядок**, но не заменяют эту таблицу: Display Inventory · Product Flow · Pipeline I0 · Matrix 3.2 · Capability.

Где они расходятся — побеждает: **N = этот файл** · I0/owner = Pipeline · UI слот = Inventory.

---

## 8. Незакрытые конфликты документов (не резались молча)

| Конфликт | Стороны | Что делает этот файл |
|----------|---------|----------------------|
| Matrix 3.2 «цвет/запах/камень/талисман дня» vs Inventory только `T3.color` | Matrix каркас vs Inventory M | **K15** = одна рекомендация-опора дня (color). Scent/stone не отдельные K и не показываются без слота |
| SCREEN_CONTRACTS 4 life domains vs «Today не гороскоп сфер» | P0.1 vs Pipeline/Inventory | domains **не** в N. Сферы дня не generative root |
| Pipeline «единственный Meaning SoT» vs этот файл | два файла одного экрана | Pipeline = **как** решается и кто owner. Этот файл = **какое** конечное множество можно знать. Не второй канон I0 |
| Day Sources `in_today: yes` на planned eclipse/nodes | registry vs V1 freeze | пока `version=planned` — **не** F и **не** K |
| `personal_year` / month в Sources vs Ritual number = Personal Day Number | numerology family vs Product Flow | PY/PM не слот Today V1; Ritual показывает PD или Universal (`K12`) |

Owner может сузить M (убрать показ), не расширяя N.

---

## 9. Другие разделы

Тот же закон, другие таблицы. **Этим файлом не заполняются.**

| Раздел | Контракт | Сейчас |
|--------|----------|--------|
| Profile | [PROFILE_INFORMATION_CONTRACT_V1](../profile/PROFILE_INFORMATION_CONTRACT_V1.md) | **исполнен** (17 COMPLETE / 0 PARTIAL / 0 MISSING / 1 OMIT-BY-DESIGN). Не очередь Today |
| Compatibility | нужен свой Information Contract | два Profile N + pair derivation. **Не выбран** (2026-09-21). Следующий Today gate = X11; X14 после него |
| Tarot (вопрос, не карта дня) | нужен свой | card_base + question/spread; не этот N |
| Практики (хаб, не `T3.practice`) | taxonomy + coverage | метод/item, не знание о дне |

Today N **CLOSED / PASS**. Compatibility / Tarot Information Contract — отдельные таблицы, не автоматическое продолжение этого файла.

---

## 10. Locked decisions (2026-09-21)

1. **N = 20.** Reconstruction из Pipeline ownership + Inventory M + Matrix depth/honesty. `human_line` — формулировка `K01`, не отдельный корень. `T3.rhythm` — показ `K05`, не второй timeline SoT. Scent/stone — алиас `K15`, без слота не показываем.
2. **N = 20 — обязательный code gate.** Любая **новая** meaning-producing работа в Today обязана назвать минимум `TIC-K*` и зависимые `TIC-F*`. Не может указать — работа не начинается. Chrome и transport failure исключены. Модуль: `today_information_contract_v1.py`. Executable coverage = §11.
3. **TIC-K\* не PIC-K\*.** Не переносить Identity Core / 13-key / CE prose в Today. `TIC-K01` = вид общего дня, не логлайн личности.
4. **Personal Day = Global × Natal Overlay.** Нет CE, карты, числа, целей в bind. Lens только после persist. Guest = catalog, не lens.
5. **LLM формулирует после решения Engine/Overlay/catalog.** Не выбирает energy/drivers/windows/axis. Не заполняет пустое generic prose. Downstream не мутирует upstream.
6. **Критерий закрытия Today train:** для каждого из 20 `TIC-K` определено facts → KB → derivation → wire → M/omit → slot; отображаемый M исполняется кодом. Тогда — не автоматически Compatibility N. Не «IL подключён», не «xfail стал pass», не «Today выглядит лучше».
7. **PIC закрыт.** Не использовать Profile Information Contract как источник автоматически возникающей Today-работы. Не invent `TIC-K21`. Не включать planned Day Sources в N.
8. **Не rebuild сервера** на coverage hops. Статусы §11 — hop ledger, не close-out. Close-out = §12 (четыре acceptance-блока). Не K21.
9. **K01 presentation (2026-09-21).** `T1-hero.human_line` = closed formulation of Engine `primary_energy`. Greeting is chrome, not K01. Missing/unknown omit. Overlay does not rewrite the shared-day kind. Not a second energy selector.
10. **K06 overlay thesis (2026-09-21).** `T3.headline` / `day_personal.summary_ru` = already-derived F09 natal_transit thesis (`personal_astrology.summary_ru`). HD / BaZi / Vedic / electional / name_numbers stay in the pack and do not feed K06. Missing overlay transit → omit. Not `why_personal`. Not T1 human_line. Not a new knowledge type.
11. **K07 overlay axis (2026-09-21).** `T3.focus_title` / `personal_day.natal_overlay.focus_axis` = F10 closed domain of the already-chosen F09 natal_transit natal_point. Kitchen aliases / Global scene sphere / PIC / CE / chrome do not feed K07. Missing or unmapped → omit. Not a second ranker. Not a duplicate of K01 `human_line` or K06 headline.
12. **K09 personal do (2026-09-21).** `T3.priority` / `day_story.do[]` = Personal Narrative after bind. Global `recommended_action` / `props.goals` do not feed the slot. I0 personal stage must not mutate scene action. Missing Personal-owned do → omit. Not a second selector. Not K10 avoid. Glance leftover is not this hop except rejecting Global scene action as `today_move`.
13. **K10 personal avoid (2026-09-21).** `T3.caution` / `day_story.avoid[]` = Personal Narrative after bind. Global `do_not` / `avoid_action` stay on the scene and do not feed the slot. Missing Personal-owned avoid → omit. Not a second ranker. Not an inversion of K09 `do[]`. Not K13+.
14. **K13 card lens (2026-09-21).** `T2.lens_card` / `card.hook_reveal.personal_angle` = Personal Day × F13 after persist. Global chorus `day_card` / `bridge_to_day` stay on the Global contract and do not feed the slot. Missing Personal-owned card lens → omit. Not a second ranker. Not a copy of K06–K10. Not K14.
15. **K14 number lens (2026-09-21).** `T2.lens_number` / `number.hook_reveal.personal_angle` = Personal Day × F11/F12 after persist. Global chorus `day_number` / `bridge_to_day` / tempo stay on the Global contract and do not feed the slot. Missing Personal-owned number lens → omit. Persist-gate is not coverage. Not a second ranker. Not a copy of K06–K10 or K13. Not K15+.
16. **K15 color (2026-09-21).** `T3.color.*` / `color_guide` = existing `score_color_for_needs` on F05 8-set + F09 overlay domain (`DOMAIN_NATAL_POINTS`) after persist. Scene trap/sphere/mode do not feed the slot. No second scorer. Scent/stone aliases unused without a slot. Missing grounded F05+F09 → omit. Catalog/talisman leftover does not paint. Not K16+.
17. **K16 practice (2026-09-21).** `T3.practice` = existing `GET /practices/select` from already-chosen F10 `focus_axis` (closed 4-set) after persist. Global `primary_energy` / K01 8-set do not feed the slot. No second selector. Compensating Personal Risk is not invented from K10 prose or Global F06. Guest / missing F10 / unavailable interpretation → omit. XOR with affirmation is K17.
18. **K17 XOR (2026-09-21).** Affirmation vs practice is one existing content mode, not a second selector. Mode = K16 `content_class` of the already-chosen F10 need cell (`practice`). Exactly one Inventory slot. Scene `props.affirmations` / trap / `recommended_action` do not feed `T3.affirmation`. Date-hash / availability / leftover catalog item do not choose the branch. Empty selected branch → omit, not switch. No Personal-owned affirmation field on the locked overlay → affirmation omit. K16 select query unchanged. Not K20 extraCards. Glance leftover is not this hop.
19. **K20 honesty (2026-09-21).** `T3.unavailable` is the already-known capability / persist / transport gap. Unavailable MY DAY paints that chrome only. extraCards (practice/affirmation/tasks) omit. Global scene/kitchen/chorus and empty K16/K17 are not surrogate meaning. Not a new selector. Glance leftover is out of locked-surface scope.
20. **Close-out (2026-09-21).** Four acceptance blocks PASS. Train frozen. Next product gate is chosen from canon, not TIC inertia.

---

## 11. Executable coverage audit (2026-09-21)

Статусы — факт кода на ветке `cursor/today-information-contract`, не желание канона. Измерена цепочка:

```text
IN → TIC-F → TIC-K → derivation → product field → Inventory slot → locked FE surface
  (TodayCompositionSurface → TodayProductScreenFlow)
```

Четыре независимые проверки на каждый K: producer/SoT · разрешённые F · wire до product field · Inventory slot + paint **или** OMIT-BY-DESIGN. Presence JSON ≠ покрытие. `human_line` / `T3.rhythm` / scent-stone судятся по семантике §3, не по совпадению имени поля. PIC / CE / 13-key не участвуют.

| Статус | Значит |
|--------|--------|
| `COMPLETE` | отображаемый M: facts → KB → derivation → wire → slot исполняется; пустое omit |
| `PARTIAL` | hops есть, но схлопывание / не те F / слот мапится мимо / семантика не TIC |
| `MISSING` | знание в N, до слота hop нет |
| `OMIT-BY-DESIGN` | TIC M это знание не показывает; не дефект. Guest omit personal K = Matrix M, не этот статус |

| ID | Status | F consumed | KB | Derivation | Wire | Slot | Defect |
|----|--------|------------|----|------------|------|------|--------|
| `K01` | **COMPLETE** | Engine `score_energy` / `pick_primary_energy` (F04→F05). `human_line` consumes F05 only | 8-set + `DAY_MODE_LABELS_RU` + `SHARED_DAY_HUMAN_LINES` | Engine argmax live; FE `atmosphereLine` = `formulateSharedDayHumanLine(primary_energy)` | `today_contract.global_day.primary_energy` · `energy_scores` | `T1-hero.energy_word` / `%` paint; `mood` 1:1 visual_mode; **`human_line` formulates the chosen energy**; greeting stays chrome | нет на измеренном hop |
| `K02` | **COMPLETE** | F01–F03 pack → ranker → `global_ranked_drivers` (natal/card filter `is_global_event`) | ranked event + `fact_ru` (IL catalog 0 active; не отдельный mint) | 1–3 global drivers + moon row; FE cap 3 | `global_day.drivers[]` | `T1-clock.transit` paint (`buildTransitRows`) | нет на измеренном hop |
| `K03` | **COMPLETE** | F04/F05/F07 → `_strength_risk` | closed `ACTION_TYPES` | Engine; не сферы жизни | `global_day.strength[]` | `T1-strength.chip` paint | нет |
| `K04` | **COMPLETE** | то же → `risk` (exclude strength) | тот же set | Engine; ≠ personal avoid | `global_day.risk[]` | `T1-risk.chip` paint | нет |
| `K05` | **COMPLETE** | F03/F04 → `build_global_windows`; T3 × F09 glance clocks если natal | windows schema | Engine authority; natal clocks = display source `natal`, не второй windows SoT | `global_day.windows[]` | `T1-clock.range`/`spectrum` paint; `T3.rhythm_row` paint (`«Мой ритм»` iff `row.source==="natal"`) | нет на paint path; `emitTodayDisplayFrame` не проецирует rhythm (scan gap, не meaning) |
| `K06` | **COMPLETE** | F09 natal_transit via `personal_astrology.summary_ru`. HD/BaZi/Vedic/electional/name_numbers **не** в thesis | overlay natal_transit | existing adapter thesis copied into K06 field; kitchen join removed | `day_story.day_personal.summary_ru` | `T3.headline` paint (`personalLine`) | нет на измеренном hop |
| `K07` | **COMPLETE** | F09 first `natal_transit` natal_point → existing `DOMAIN_NATAL_POINTS` (DOMAINS order) as F10. Kitchen beats / leftover overlay keys / scene sphere **не** вход | 4-set domain ids + `TODAY_CONTRACT_DOMAIN_LABEL_RU` | nest writer `build_personal_day_nest_v1`; FE `pickPersonalFocusAxisLabel` map_label only, omit without id | `personal_day.natal_overlay.focus_axis` | `T3.focus_title` paint; omit without axis | нет на измеренном hop |
| `K08` | **COMPLETE** | `conflict.why_personal` → natal_transit beat → `personal_astrology.summary_ru` | overlay fields | `pickInstructionPersonalBridge`; не `development_point`; overlap headline drop | `day_story.day_scenario.conflict.why_personal` | `T3.focus_body` paint | нет на измеренном hop (guest omit = M) |
| `K09` | **COMPLETE** | Personal Narrative after bind only. Global scene `recommended_action` / `props.goals` **не** вход (`_GLOBAL_SCENE_KEYS`; personal stage must not mutate) | — | projector leaves `do[]` / `today_move` empty without Personal-owned do; FE `pickMyDayPriorityLines` omit Global scene action and omit without persist | `day_story.do[]` | `T3.priority` paint; omit without personal do | нет на измеренном hop |
| `K10` | **COMPLETE** | Personal Narrative after bind only. Global scene `do_not` / `avoid_action` **не** вход (`_GLOBAL_SCENE_KEYS`; personal stage must not mutate) | — | projector leaves `avoid[]` empty without Personal-owned avoid; FE `pickMyDayCautionLines` omit Global scene caution, T1-risk chips, and K09 do inversion; omit without persist | `day_story.avoid[]` | `T3.caution` paint; omit without personal avoid | нет на измеренном hop |
| `K11` | **COMPLETE** | F13 `DaySymbolState` card id+orientation | `card_base_v1.get_base_meaning` | catalog lookup; не причина дня | `card.hook_reveal.base.meaning` | `T2.catalog_card` / `card_face` paint | нет |
| `K12` | **COMPLETE** | F12 if birth else F11 (`ritual_day_number`) | `number_base_v1.get_number_base` | catalog lookup | `number.hook_reveal.base.meaning` | `T2.catalog_number` / `number_glyph` paint | нет |
| `K13` | **COMPLETE** | F13 identity + already persisted Personal Day. Global `interpretive_chorus.day_card` / `bridge_to_day` **не** вход. K06–K10 not copied into the lens | catalog as color, not cause | attach leaves `personal_angle` omit without Personal-owned card lens; FE `pickRitualCardLens` omit chorus bridge, catalog, and omit-token; omit without persist | `card.hook_reveal.personal_angle` | `T2.lens_card` paint; omit without personal lens | нет на измеренном hop |
| `K14` | **COMPLETE** | F11 or F12 identity + already persisted Personal Day. Global `interpretive_chorus.day_number` / `bridge_to_day` / tempo **не** вход. K06–K10/K13 not copied into the lens | catalog as color, not cause | attach leaves `personal_angle` omit without Personal-owned number lens; FE `pickRitualNumberLens` omit chorus bridge, tempo mash, catalog, and omit-token; omit without persist | `number.hook_reveal.personal_angle` | `T2.lens_number` paint; omit without personal lens | нет на измеренном hop |
| `K15` | **COMPLETE** | Engine `primary_energy` (F05) + overlay natal_point via existing `DOMAIN_NATAL_POINTS` (F09) → existing `score_color_for_needs`. Scene trap/sphere/mode **не** вход. Scent/stone unused aliases | color catalog | `build_scenario_props_v1` needed-tags lookup; no second scorer; omit without grounded F05+F09; catalog/talisman leftover does not fill | `today_contract.color_guide` from `props.color` | `T3.color.*` paint on MY DAY from nest; omit without nest; morning catalog does not paint | нет на измеренном hop |
| `K16` | **COMPLETE** | F10 `personal_day.natal_overlay.focus_axis` (closed 4-set) → existing `GET /practices/select` (`content_class=practice`). Global `primary_energy` **не** вход. Compensating risk не invent | technique library | FE `fetchCatalogPracticeForFocusAxis`; no second selector; omit without F10 / guest / unavailable | catalog selection as tool | `T3.practice` paint when present; XOR with affirmation is K17 | нет на измеренном hop |
| `K17` | **COMPLETE** | existing K16 F10 need-cell `content_class` (practice). Scene `props.affirmations` / trap / `recommended_action` **не** вход. No Personal-owned affirmation field on locked overlay | existing content mode; not a second ranker | FE `pickLockedSupportSlot`; projector omits scene rec; empty selected branch does not switch; date-hash gone | XOR one of `T3.practice` / `T3.affirmation` | paint selected Inventory slot; omit both when the branch is empty | нет на измеренном hop |
| `K18` | **COMPLETE** | base day + topic id + billing | depth menu | `today_depth_layer_v1`; Free CTA; Trial+ generate | `today_contract.depth_layer` | `T3.depth` paint (`TodayDepthLayerSection`) | нет (не второй TODAY plot) |
| `K19` | **COMPLETE** | F15 yesterday `evening_completed` + gratitude | user record | `loadYesterdayEveningClose` → `buildGratitudeMemorySlot`; empty omit; no invent on GET fail | client memory slot / day-connection | `T1.continuity` paint D2+ | нет |
| `K20` | **COMPLETE** | capability + `interpretation_status` / transport | Matrix copy | guest `myDay:false`; unavailable `TODAY_UNAVAILABLE_COPY`; network `TODAY_NO_CONNECTION_COPY`; extraCards omit on unavailable pane | guest omit MY DAY; `TodayMyDayPane` unavailable card only | `T3.unavailable` / `TF.*` paint; extraCards/practice/affirmation not mounted | нет на измеренном hop |

Сводка: **COMPLETE 20** (`K01`–`K20`) · **PARTIAL 0** · **MISSING 0** · **OMIT-BY-DESIGN 0**. Hop ledger only. Close-out = §12.

### Очередь Today (только дефекты матрицы, порядок K)

Нет. Матрица закрыта. Close-out **PASS**. Не K21. Не IL. Не PIC. Не Compatibility N автоматически.

---

## 12. Close-out (2026-09-21)

**TODAY_INFORMATION_CONTRACT: CLOSED / PASS**

Не принимает `TIC_COVERAGE == 20 COMPLETE` как доказательство. Независимый re-audit уже собранной системы. Новых K нет. Продуктовых исправлений внутри gate нет.

Locked surfaces = production 4-surface path: `TodayProductScreenFlow` ← `TodayDayBrief` · `TodayRitualLensPair` · `TodayMyDayPane` · evening. Не `?full=1` / `?experience=1` / legacy stacked.

| Block | Verdict | Что измерено |
|-------|---------|--------------|
| **1. 20/20 executable re-audit** | **PASS** | Для каждого `TIC-K` снова исполнена цепочка input → fact → K → derivation → product field → Inventory slot → display/omit. Итог **20 COMPLETE / 0 PARTIAL / 0 MISSING**. Не чтение таблицы §11. |
| **2. Inventory last-authority** | **PASS** | Locked paint идёт через Inventory `slot_id`. Текст в payload / scene / nest / chorus / catalog сам по себе не рисуется. |
| **3. Forbidden-source scan** | **PASS** | Kitchen families, PIC/CE prose, Global→Personal подмена, scene leftovers, generic fallback и chrome-as-root не кормят locked meaning. Regression set K01/K06/K07/K09/K10/K13–K17/K20 PASS. |
| **4. Omit integrity** | **PASS** | Нет overlay → personal slots omit. Нет Personal×card/number → lenses omit. Нет personal do/avoid → priority/caution omit. Пустая K17-ветка не подставляет другую. Unavailable → только `T3.unavailable`. |

**Glance leftover:** **out of TIC locked-surface scope.** `TodayGlanceAct` не смонтирован. `glanceSection` не рендерится. Wave2 Daily Focus не пятый акт. Именованные helpers на locked path не являются Glance-as-act SoT: `T1-hero.sheet` `energyCause` = Inventory-authorized Global; `T3.priority` `glancePrioritize` = identity-check vs personal `today_move`. Если будущий re-audit найдёт `TodayGlanceAct` на 4-surface — этот freeze void, gate FAIL; чинить отдельным hop, не внутри аудита.

Gate: `evaluate_tic_closeout` · `backend/tests/test_today_information_contract_closeout_v1.py` · `frontend/src/lib/__tests__/todayTicCloseout.test.ts`.

**Следующий продуктовый gate (selection 2026-09-21, after X4/X5 CLOSED / PASS):** Full User Path **X11** leftover narrative. **X14 after X11.** SoT выбора: [TODAY_PRODUCT_FLOW_V1](./TODAY_PRODUCT_FLOW_V1.md) product-gate selection · [FULL_USER_PATH_CANON_V1](../audits/FULL_USER_PATH_CANON_V1.md) §13/§16. Не Compatibility Information Contract. Не invent `TIC-K21`. Не IL dump. Не PIC. Не rebuild.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-09-21 | X11 gate selection (after X4/X5 CLOSED / PASS): next = leftover narrative cleanup. X14 after X11. Not Compatibility N. Not K21. TIC remains CLOSED / PASS. |
| 2026-09-21 | X4/X5 CLOSED / PASS (joint honest reveal copy). TIC remains CLOSED / PASS. Next Today remainder = X11 then X14. Not Compatibility N. Not K21. |
| 2026-09-21 | X4/X5 gate selection (after X3 CLOSED / PASS): next = one joint X4/X5 honest reveal copy. Not Compatibility N. Not K21. TIC remains CLOSED / PASS. |
| 2026-09-21 | Product-gate selection: next = Full User Path X3 (Theme/Focus/Step spine). Not Compatibility N. Not K21. |
| 2026-09-21 | **§12 CLOSE-OUT PASS.** Independent four-block re-audit. TODAY_INFORMATION_CONTRACT: CLOSED / PASS. Glance leftover out of locked-surface scope. Frozen. Next product gate from canon, not TIC inertia. Not K21. |
| 2026-09-21 | §11 K20 COMPLETE: unavailable MY DAY = `T3.unavailable` only; extraCards/practice/affirmation omit; not surrogate meaning. **20 COMPLETE · 0 PARTIAL**. Next = TIC close-out, not K21. |
| 2026-09-21 | §11 K17 COMPLETE: XOR affirmation vs practice from existing F10 content class; scene rec/trap do not feed T3.affirmation; empty branch omits. 19 COMPLETE · 1 PARTIAL. Next remaining = K20. |
| 2026-09-21 | §11 K16 COMPLETE: `T3.practice` = existing `GET /practices/select` from F10 `focus_axis`; Global `primary_energy` does not feed the slot; omit without F10. 18 COMPLETE · 2 PARTIAL. Next remaining = K17. |
| 2026-09-21 | §11 K15 COMPLETE: `T3.color.*` / `color_guide` = existing `score_color_for_needs` on F05+F09 after persist; scene tags / catalog leftover do not feed the slot; omit without ground. 17 COMPLETE · 3 PARTIAL. Next remaining = K16. |
| 2026-09-21 | §11 K14 COMPLETE: `T2.lens_number` = Personal Day × F11/F12 after persist; Global chorus `day_number` / tempo stays on hook and does not feed the slot; omit without personal lens. 16 COMPLETE · 4 PARTIAL. Next remaining = K15. |
| 2026-09-21 | §11 K13 COMPLETE: `T2.lens_card` = Personal Day × F13 after persist; Global chorus `bridge_to_day` stays on scene and does not feed the slot; omit without personal lens. 15 COMPLETE · 5 PARTIAL. Next remaining = K14. |
| 2026-09-21 | §11 K10 COMPLETE: `avoid[]` = Personal Narrative after bind; Global `do_not` stays on scene and does not feed T3.caution; omit without personal avoid. 14 COMPLETE · 6 PARTIAL. Next remaining = K13. |
| 2026-09-21 | §11 K09 COMPLETE: `do[]` = Personal Narrative after bind; Global `recommended_action` / goals out of T3.priority; omit without personal do. 13 COMPLETE · 7 PARTIAL. Next remaining = K10. |
| 2026-09-21 | §11 K07 COMPLETE: F10 = first natal_transit natal_point → existing 4-domain membership; FE omit without `focus_axis`; no scene/kitchen fill. 12 COMPLETE · 8 PARTIAL. Next remaining = K09. |
| 2026-09-21 | §11 K06 COMPLETE: `summary_ru` = F09 natal_transit overlay thesis; kitchen families out of K06. 11 COMPLETE · 9 PARTIAL. Next remaining = K07. |
| 2026-09-21 | §11 K01 COMPLETE: `human_line` formulates `primary_energy`; greeting is chrome. 10 COMPLETE · 10 PARTIAL. Next remaining = K06. |
| 2026-09-21 | §11 executable coverage: 9 COMPLETE · 11 PARTIAL · 0 MISSING · 0 OMIT-BY-DESIGN. Queue from defects only; first = K01. No product fix in this hop. |
| 2026-09-21 | v1 reconstruction: 8 inputs · 16 facts · **20 allowed knowledge**. Ничего не добавлено сверх существующих канонов. PIC не источник очереди. |
