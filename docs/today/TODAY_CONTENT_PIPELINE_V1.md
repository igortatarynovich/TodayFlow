# Today Content Pipeline v1

**Status:** CANON LOCKED · **2026-08-15**  
**Роль:** **единственный канон и единственный Meaning SoT Today** — что считается, что решает смысл дня, что пишет LLM, что можно показать.  
Любой другой документ про Today **подчинён** этому файлу или описывает другой слой (не смысл).

**Не:** Figma · ScreenFlow layout · Profile Character Engine · product north star.

### Один канон — не плодить параллели

| Вопрос | Ответ живёт здесь | Другие файлы |
|--------|-------------------|--------------|
| Почему пользователю показали *это*? | **этот файл** | — |
| Как считаются сырые факты неба/числа? | → [DAY_SOURCES_CANON](../DAY_SOURCES_CANON.md) | подчинён: только facts, не сюжет |
| Что означает астрологический факт системы (Saturn, square, 7th…)? | → [INTERPRETATION_LIBRARY_V1](../astrology/INTERPRETATION_LIBRARY_V1.md) | step 2 lookup; не канон дня |
| Как нарезан экран (какие шаги видит человек)? | → [TODAY_PRODUCT_FLOW_V1](./TODAY_PRODUCT_FLOW_V1.md) | product cycle; не смысл |
| Что именно написано в каждом блоке (лимит · источник слова)? | → [TODAY_DISPLAY_INVENTORY_V1](./TODAY_DISPLAY_INVENTORY_V1.md) · закон [DISPLAY_CONSTRUCTION_GRAMMAR_V1](../foundation/DISPLAY_CONSTRUCTION_GRAMMAR_V1.md) | presentation; не смысл; последний authority перед UI |
| Как выглядят токены/атмосфера? | → [TODAYFLOW_FOUNDATION_UI](../TODAYFLOW_FOUNDATION_UI.md) | visual only |
| Старый движок conflict/scenes (код сегодня) | → [DAY_SCENARIO_V1](../DAY_SCENARIO_V1.md) | **миграция / hygiene**, не Meaning SoT |
| B5 «scenario exclusive» | → [DAY_SCENARIO_RUNTIME_SOT_B5](../audits/DAY_SCENARIO_RUNTIME_SOT_B5.md) | **SUPERSEDED** как meaning; runtime note до cutover |
| Шесть блоков / 1a+1b | → [TODAY_SCREEN_SCENARIO_V3](./TODAY_SCREEN_SCENARIO_V3.md) | **SUPERSEDED**; historical map after FE cutover 2026-08-15 |

При конфликте формулировок: **побеждает этот файл**. Не заводить второй «канон дня», «Meaning SoT», «Day Story SoT».

**Связь (подчинённые):** DAY_SOURCES · [INTERPRETATION_LIBRARY_V1](../astrology/INTERPRETATION_LIBRARY_V1.md) (step 2 lookup) · DAY_ENGINE (указатель сюда) · DAY_SCENARIO_V1 (I0–I8 hygiene) · [TODAY_PRODUCT_FLOW_V1](./TODAY_PRODUCT_FLOW_V1.md) (экраны) · SCENARIO_V3 (historical six-block map) · AMC (machine tags).

---

## I0 — Interpretation Layers (LOCKED)

Два последовательных authority, не один гигантский Meaning SoT.

| Слой | Вопрос | Кто решает | Не имеет права |
|------|--------|------------|----------------|
| **Global Day** | Какой сегодня день? | Детерминированный Global Day Engine (+ LLM только формулирует) | Натал, карта, число, цели, история |
| **Personal Day** | Как этот день касается *меня*? | Global × Natal Overlay; LLM #2 формулирует | Менять Global; CE; карта; число; цели |

**I0.** Global interpretation completes **without** personal, tarot, numerology, or Character Engine evidence. Personal interpretation **consumes** Global Day × Natal Overlay and may contextualize it, **never redefine** it. Ritual symbols are interpretive overlays **after** Personal Day persist and **never** participate in Global or Personal Day determination.

Повторность (жёстко):

```text
одинаковые входы + одинаковые версии правил  →  одинаковый смысл дня
```

LLM не выбирает mood/energy, главных drivers, окна времени, valence окон.  
Текст можно генерировать **один раз** и сохранить. GET не вызывает LLM.

Два человека в одной **locale** + одна **local_date** (timezone уже сведена на крае) + одна **semantic_version** → **один и тот же Global Day**.

```text
GlobalDayKey   = local_date + locale + semantic_version
PersonalDayKey = user_identity + local_date + semantic_version
```

`behavior_version` в Personal identity **не** входит, пока overlay не станет реальным входом Today и не будет правила meaningful delta.

В Global identity **не** входят `user_id`, profile hash, expression/prompt конкретного пользователя. Force rebuild пересоздаёт **тот же** ключ (engineering ledger), не новую semantic version. Persist: [COMPUTE_LIFECYCLE_AND_ARTIFACT_ECONOMICS_V1.md](../COMPUTE_LIFECYCLE_AND_ARTIFACT_ECONOMICS_V1.md). This file remains Today **meaning** SoT.

**Persist / economics (subordinate):** Personal = `1 × user × local_date × semantic_version` (landed: `personal_day_v1`). Global = `GlobalDayKey`, not × user. Re-open after first accepted artifact = 0 LLM on that layer. GET miss does not enqueue regeneration.

### Who knows what (LOCKED)

IL / Canon — atomic astrology. Character Engine — the person. Neither layer owns the other.

```text
Interpretation Library  знает астрологию.  Не знает человека.
Character Engine        знает человека.    Не знает астрологию.
Personal Day            = Global Day × Natal Overlay.
```

Today **не** вызывает Character Engine как общий API личности. Никакой CE-output не входит в Personal Day, пока отдельная проекция не названа слотом + Architecture impact. Тогда же решить, меняет ли она `PersonalDayKey` (по умолчанию — нет: ключ без `profile_hash`).

**Запрещены в Personal Day (и в lens/enrichment как CE-prose):** `recognition_line` · `identity_core` · archetype name · insight nodes · `effort_vector` · `bridge_line` · `life_mission` · living notes как смысл дня · Natal Decode essay.

Natal Overlay = today sky × **natal chart** (дома, транзиты к наталу). Это астрология этого человека, не Character Engine.

Planet = what · Sign = how · House = where · Aspect = relation — это **только** астрологический atomic layer. Он **не** кодирует Global vs Personal. Персонализацию **не** заталкивать в Canon.

| Профиль дня | Цепочка | Не содержит |
|-------------|---------|-------------|
| **Global Day** | astronomical facts → IL atoms → composition → global semantic frame | натал, Character Engine, карта, число, цели |
| **Personal Day** | Global Day × Natal Overlay → personal relevance | Character Engine, карта, число, цели, переписывание Global energy/drivers/windows |

LLM формулирует каждый слой **после** этих решений, в пределах structured payload. Текущий Personal = wrapper over `day_story` — другой продукт, не этот канон.

Personal Model — единственный authority **о человеке**, не единственный владелец всей семантики продукта. Иначе астрология снова въедет в person-модель и получится монолит.

### Downstream non-mutation (LOCKED)

```text
Downstream layer may enrich or verbalize upstream meaning,
but may never mutate an upstream semantic decision.
```

| Слой | Может | Не может |
|------|--------|----------|
| Personal | объяснить global risk / strength | заменить `primary_energy`, drivers, windows |
| Card / number | дать lens / bridge | изменить Global Day |
| Narrative LLM | переформулировать окно / силу | поменять `supports[]` / `cautions[]` / scores |
| UI | скрыть / не показать значение | вычислить другое |

Проверка (ручная в ревью; цель — автоматом в CI): любое поле Today либо **owned** таблицей ниже, либо **derived view** без новой семантики. Если owner неоднозначен — архитектурная дыра, не «потом разберёмся».

---

## Ownership смысловых результатов (LOCKED)

Не компоненты и не экраны — **кто имеет право определить значение**.  
Правило ревью: **для каждого поля Today — ровно один decision owner.**

| Результат | Authority |
|-----------|-----------|
| Sky facts | Day Sources |
| Canonical meaning факта | [Interpretation Library](../astrology/INTERPRETATION_LIBRARY_V1.md) |
| Driver ranking | Global Day Engine |
| Primary energy | Global Day Engine |
| Strength / risk | Global Day Engine |
| Timeline windows (`supports[]` / `cautions[]`) | Global Day Engine |
| Global prose | Global Narrative LLM |
| Natal activations | Personal / Natal Engine |
| Card identity | Ritual Engine |
| Number identity | Numerology Engine |
| Card / number base meaning | Catalogs |
| Personal focus axis | Natal Overlay (closed-set domain already chosen) |
| Personal headline / focus body / priority / avoid | Personal Day |
| Card / number lens | Personal Day × symbol (**после** persist Personal Day; не bind) |
| Color / practice / affirmation | Downstream enrichment |
| Формулировка текста | Соответствующий Narrative LLM |
| Что и где показывать | [TODAY_DISPLAY_INVENTORY_V1](./TODAY_DISPLAY_INVENTORY_V1.md) |

**Не путать:**

- **Authority** = кто *решает* смысл.  
- **Narrative LLM** = кто *формулирует* уже решённое.  
- **Presentation contract** = кто *раскладывает* по UI, не invent.

Projector / ScreenFlow / FE **не** появляются в колонке Authority для смысловых полей.

---

## Цепочка (10 шагов)

Причинный порядок (**вычисление / persist**):

```text
Небо → Global Day
Небо × натал → Personal Day          (persist; не ждёт кадр MY DAY)
Personal Day × карта → Card Lens
Personal Day × число → Number Lens
```

**Показ (ScreenFlow):** TODAY → RITUAL → MY DAY → EVENING.  
Это другой порядок. RITUAL может показать линзу, потому что Personal Day уже в persist — не потому что пользователь открыл MY DAY.

Каждый следующий слой **использует** предыдущий и **не переписывает** его.

```text
1  Astronomy Facts          Swiss / day interval — только расчёт
2  Astrology Interpretation Canon   фиксированные значения (не в prompt целиком)
3  Global Day Engine        drivers · energy · strength · risk · windows
4  Global Day Narrative     LLM #1 — только человеческий язык Global Profile
5  Natal Overlay            today sky × natal — детерминированно
6  Personal Day bind        Global + overlay **только**. Persist. Нет CE, карты, числа, целей
7  Personal Narrative       LLM #2 — thesis · axis already chosen · how it shows · priority · avoid
8  Ritual identity          карта + число (hash). Параллельно. Не вход Personal Day
9  Ritual lenses            Personal Day × card / number. Guest: omit. Не mutate Personal Day
10 Contract → UI            цвет / практика / аффирмация после смысла. UI ничего не интерпретирует
```

Карта/число identity можно знать в любой момент по hash. Они **не** входят в bind. UX reveal: **GLOBAL → RITUAL → PERSONAL** (порядок показа). Backend: ночной prebake Global + Personal. Клик не запускает LLM. Lens формулируется после Personal persist (тот же процесс может писать lens в том же job — в Personal Day fields карта/число не пишутся).

---

## 1. Astronomy Facts

Вход: `local_date` · day timezone · lat/lon (для VOC/rise если есть).  
Выход: координаты, знаки, аспекты, exact times, ingress, stations, фаза Луны, VOC windows.

LLM **не** получает raw longitudes и **не** считает аспекты.

Хранить **day interval [00:00–23:59 local]**, не только noon snapshot. Noon = representative state для «что в небе сейчас днём», не единственный способ выбрать главное событие.

---

## 2. Astrology Interpretation Canon

Справочник системы (планета, знак, аспект, фаза, дом, тип транзита).  
Не Day Content. Не отправлять весь справочник в каждый prompt.

**SoT lookup:** [Interpretation Library v1](../astrology/INTERPRETATION_LIBRARY_V1.md) — семантические объекты (не гороскопы). AMC даёт веса/теги для scoring, не смысл.

Engine подставляет **уже выбранным** drivers короткие canonical lines из IL + сам факт (LLM не может заменить факт).

```text
ASTRONOMY → ASTRO FACT → CANONICAL MEANING (IL) → (позже) LLM STORY
```

Default: атомы (layers 1–4) + composition. **Не** каталог всех planet×sign. Curated Layer 5 — только non-compositional исключения; IL-1 gold list = candidates until IL-2.

Пока нет `active` объектов (IL-1 drafts не runtime SoT) — **не** отдавать значение на откуп Kimi; лучше бедный канон / omit, чем ежедневное «вспоминание». Наполнение = research (IL-1…IL-3), не генерация.

---

## 3. Global Day Engine (детерминированный смысл)

Только общее небо. **Без** натала / карты / числа / user goals.

### Какие факты меняют день

| Слой | Что | Зачем |
|------|-----|--------|
| Быстрый | Луна: знак, фаза, ingress, мажорные аспекты, VOC | отличает сегодня от завтра |
| Средний | 1–3 главных мажорных аспекта светил и личных + Юпитер/Сатурн (outers — только если сильные/событийные) | характер дня |
| Событийный | ingress, station/Rx, New/Full Moon, eclipse, exact major | повышает вес |

Не отдавать двадцать слабых аспектов.

### Что Engine **обязан** посчитать (без LLM)

- ranked drivers (1–3) + supporting
- semantic tags + scores по закрытому набору  
  `grounded | flow | radiance | momentum | clarity | tension | renewal | depth`
- **`primary_energy`** = argmax(score) по правилам весов, ничьей, min confidence, нейтральный день
- strength / risk (типы действий, не гороскоп сфер)
- timeline windows **до** любого narrative

`primary_energy` ≠ `visual_mode`.  
Energy = продуктовый смысл. `visual_mode` = UI mapping той же id (пока 1:1). LLM не выбирает ни то, ни другое.

Ничья / слабый день: зафиксировать правило (например stability/`clarity` или `grounded` при max score < threshold). Это часть scoring version в manifest.

### Timeline — часть Global Day, не Scenario

```text
day interval → exact events → classification → windows
```

Окно:

```text
Window { time, driver_id, intensity, supports[], cautions[] }
```

Не бинарное «хорошее/плохое». Mars может быть `supports: physical_action` и `cautions: sensitive_conversation`.

Часы и polarity окон — только geometry + canon. LLM #1 формулирует уже готовые окна.

---

## 4. Global Day Narrative — LLM #1

**Вход:** Global Day Profile (mode, drivers, canonical lines, windows, strength/risk).  
**Выход:** atmosphere, headline, strength copy, risk copy, direction, timeline labels.  
**Запрет:** user, natal, card, number, color, practice, goals.

Повторяемость смысла: Profile фиксирован. Текст — один раз, persist. Повторный GET не зовёт модель.

---

## 5. Natal Overlay

Natal overlay = today sky × natal (детерминированно). Не второй гороскоп.  
**Не** меняет Global Day Profile. Только activations для Personal Day.

---

## 6. Personal Day bind + Personal Narrative — LLM #2

**Personal Day = Global Day × Natal Overlay.**

**Вход bind / LLM #2:** готовый Global Day + natal overlay.  
**Не входят:** Character Engine, card, number, goals/history, Profile Snapshot prose.

**Выход:** personal thesis (headline) · overlay-chosen focus axis (не свободный title) · how it shows (focus body) · priority · avoid.

**Запрет:** менять `primary_energy`, global drivers, global strength/risk, window times/supports/cautions; подмешивать CE; писать card/number в поля Personal Day.

Strength + tension day → «силу сегодня лучше направить в самообладание», не «день на самом деле grounded».

Lens card/number — **шаг 9**, не этот bind.

---

## 7. Ritual identity (параллельно bind; не вход Personal Day)

Карта: `sha256(owner_key|local_date|"day_card") % 78` + orientation digest.  
Число: numerology **Personal Day Number** если есть `birth_date`, иначе Universal Day (masters 11/22/33). Это **не** продуктовый Personal Day.

Reveal открывает identity. **Не** пересобирает Global Day. **Не** создаёт и **не** мутирует Personal Day.  
Base meaning = catalog. Personal lens (шаг 9) только если Personal Day уже persisted. Guest: catalog only.

---

## 8–10. Ritual lenses, enrichments и UI

Цвет / практика / аффирмация — scoring каталога **после** Personal Day. Отдельный «шаг»-слот (`T3.action`) **нет** — это вопрос `T3.priority`. User-facing *why* только из установленного смысла + provenance.

UI читает Contract. Не ранжирует, не invent.

**Экран (product cycle):** [TODAY_PRODUCT_FLOW_V1](./TODAY_PRODUCT_FLOW_V1.md) — `today` · `ritual` · `my_day` · `evening`. Не 1a/1b и не шесть блоков.

| Когда | Что | Показ |
|-------|-----|-------|
| TODAY | Global Day: energy% · mood · Global day clock · timed transits · strength/risk | Global clock; **не** Personal Timeline |
| RITUAL | карта, затем число. Catalog всегда при identity. Lens только если Personal Day persisted | sequential reveal |
| MY DAY | Personal Day: headline · focus axis · focus body · priority · cautions · rhythm · optional color/practice/affirmation | natal timeline если есть; иначе Global `windows[]` как «Ритм дня» |
| EVENING | благодарность → Gratitude History | не trap-check / не «совпал ли прогноз» |

Timeline **authority** = Global Engine `windows[]` (`supports` / `cautions`). **Показ Global clock** = TODAY (окно + timed transits) и, если нет natal clocks, `my_day` («Ритм дня»). **Показ Personal Timeline** = `my_day` только при natal activations («Мой ритм дня»). UI hide ≠ mutate.

Guest: TODAY + ritual **catalog** (universal number + card base) + evening. MY DAY omit. Ritual **personal lens** omit.

Core answer = TODAY (погода дня) за 1–2 минуты. MY DAY = «для меня». Ritual = две линзы. Evening = благодарность.

---

## Day Package (immutable)

После успешной сборки GET только читает.

```text
identity: owner | local_date | day_tz | rule versions
astronomy_facts
global_day_profile     # energy, drivers, strength, risk, windows
global_narrative       # persist once
natal_overlay          # omit if no natal
ritual: card, number
personal_narrative     # persist once; omit if guest / no natal overlay
ritual_lenses          # omit if no personal_narrative; never written into personal_narrative fields
enrichments
manifest:
  ephemeris_version
  astro_rules_version
  scoring_version
  timeline_rules_version
  natal_overlay_version
  canon_lookup_version
  global_prompt_version
  personal_prompt_version
  card_catalog_version
  number_catalog_version
  color_catalog_version
  today_contract_version
```

Смена весов scoring **не** пересчитывает уже сохранённый день.

---

## Наложение на существующий код (оставить / упростить / удалить)

| Артефакт | Решение | Почему |
|----------|---------|--------|
| Swiss / `sky_geometry_v1` / `celestial_events` | **упростить** | Остаётся Astronomy Facts. Noon не единственный ranker; day interval + exact events — SoT окон |
| `day_events_ranker_v1` / Foundation | **упростить** → Global Day Engine | Ranking без натала / карты / числа. Natal activations — только overlay |
| `headline_sky` / `sky_today` | **оставить** как view Global Facts | Не Meaning SoT |
| AMC / reference machine JSON | **оставить** как scoring tags | Не user prose |
| Astrology Interpretation Canon (lookup) | **IL-0 schema** · IL-1 drafts, not `active` | [INTERPRETATION_LIBRARY_V1](../astrology/INTERPRETATION_LIBRARY_V1.md); не ежедневный LLM |
| `visual_mode` от native LLM | **удалить как decision** | `primary_energy` из scoring; visual_mode = map |
| `day_flow_windows_kimi_v1` | **удалить** | Окна считает Engine; LLM #1 только labels |
| `today_glance_timeline_v1` clocks | **оставить** как geometry | Расширить до Global windows (`supports[]`/`cautions[]`) |
| `day_scenario_native_llm_c1` (один вызов chorus+conflict+scenes+natal+card+number) | **split landed 1.3.116 · shared Global persist 2026-08-25** | Global stage + Personal overlay; Global LLM reused via `GlobalDayKey` ([NATIVE_C1_I0_GENERATION_SPLIT_V1](./NATIVE_C1_I0_GENERATION_SPLIT_V1.md)); prompt `day-scenario-native-c5.5` |
| Dramaturgy brief C4 | **упростить** | DTO **Global Profile** → LLM #1. Не planner сюжета, не personal |
| `day_scenario` / conflict / scenes | **упростить** | Не Meaning SoT. Максимум внутренний literary scaffold **над** уже зафиксированным Global/Personal Profile. Не выбирает energy/windows |
| Projector B5 | **упростить** | Structure-only mapping Profile+narratives → `today_contract`. Не primary-pick, не concat meaning |
| `interpretive_chorus` | **упростить** | Не 4 независимых прогноза. Bridges карты/числа — выход LLM #2 |
| Color catalog scorer | **оставить** | После Profile; why из смысла |
| Card/number prebake + catalogs | **оставить** | Overlay only |
| `NumerologyService.daily_number` на ritual | **исправить** | Personal Day если birth_date, иначе Universal |
| `POST /today/narrative` guide generation | **удалить** после parity | Read-only consume package |
| `deterministic_engine_b5` полный spine | **упростить** | Poorer fallback = Global Facts + omit narrative, не второй гороскоп |
| `day_story` theme aliases | **упростить** | `theme` ← Global headline; personal slots отдельно |
| `practice_recommendation` bucket | **упростить** | typed `daily_actions[]` |
| I2/I3 (`primary_scene_id`, projector) | **hygiene landed 2026-08-15** | Не цементируют Scenario-как-SoT. Projector structure-only; gate rejects missing/unknown id |
| I1 «один DayScenario SoT» | **заменён I0** | Два authority в одной причинной цепочке |
| DayModel §10 (Vector/Tension/…) | **не Today content SoT** | Не конкурирует с Global/Personal Profile |
| Capability / ScreenFlow matrix | **оставить, дописать** | Guest видит только Global |

---

## Порядок работ (после этого lock)

Не чинить `day_story` по частям поверх старой модели.

0. **Этот документ** — pipeline + I0. **landed**
1. I3 + I2 hygiene. **landed 2026-08-15**
2. **I0 contract** в коде: `global_day` ≠ `personal_day`; Scenario не пишет energy/windows. **landed 2026-08-15**
3. Удалить Kimi timeline как decision; windows ∈ Global Engine. **landed 2026-08-15**
4. Energy/mood = deterministic scoring (`primary_energy`). **landed 2026-08-15**
5. Personal vs Universal number. **landed 2026-08-15**
6. Manifest + immutable GET. **landed 2026-08-15** (`day_package_manifest`; GET `allow_rebuild_on_miss=False`)
7. Guide read-only. **landed 2026-08-15** (POST `/today/narrative` consumes persist)
8. typed `daily_actions[]`. **landed 2026-08-15**
9. poorer fallback. **landed 2026-08-15** (`omit_narrative` on B5 convenience path)
10. capability matrix в ScreenFlow. **landed 2026-08-15**
11. D−1 lifecycle. **landed 2026-08-15** (additive evening enqueue; clock details in DAY_LIFECYCLE_V1)
12. **Interpretation Library** — Sequence LOCKED IL-0…IL-4. **IL-0 done.** Next: IL-1 ~100 surface-neutral objects keyed to calc output. Swiss is the runtime ephemeris input; **license** is a parallel legal gate (not a research blocker). Scale library only after IL-4.

---

## Architecture impact — Personal Day formula + compute≠display (2026-08-29)

- **SoT before:** Personal Meaning = sky × natal/CE context. Bind = Global + overlay + card + number (+ goals). Pipeline listed Ritual lenses *before* Personal Day. LLM #2 also wrote card/number bridges and personal action.
- **SoT after:** Personal Day = **Global Day × Natal Overlay**. No CE, card, number, or goals in bind. Compute persist may complete before the MY DAY surface. Card/number are lenses *after* Personal persist. `T3.action` is not a meaning result. Guest has catalog, not personal lens.
- **Public contract changed?** semantics of what may feed `personal_day` — CE and ritual identity are not inputs. JSON field names unchanged in this lock.
- **Migration required?** no key bump. Runtime that still concatenates card/number/CE into Personal bind is drift; lens may share a job but must not mutate Personal Day fields.
- **Canon updated?** yes — this file · Grammar §5.1 · Product Flow · Today Inventory v1.2 · tracker.
- **Backward compatible?** yes for GET shape. Clients that treated CE prose or `T3.action` as Personal Day meaning are out of frame.

## Architecture impact (2026-08-15)

- **SoT before:** I1–I8 — один DayScenario как Meaning SoT; LLM `visual_mode`; timeline copy из Scenario или Kimi; personal/card/number могли участвовать в одном native call.
- **SoT after:** этот файл — content pipeline. I0: Global Day / Personal Day. Ownership-таблица смысловых результатов (один decision owner на поле). Downstream non-mutation. Energy и windows детерминированы до LLM. Карта/число — линзы Personal Day. Два LLM только формулируют. GET читает persist.
- **Public contract changed?** target yes (phased): `global_day` / `personal_day` nests; `primary_energy`; windows with supports/cautions. Нет wire bump в lock-only.
- **Migration required?** yes — native C1 monolith, Kimi windows, LLM visual_mode, ritual number, guide. Cached days keep old shape until regenerate/admin.
- **Canon updated?** yes — this file · DAY_SCENARIO_V1 I0/I1 · DAY_SOURCES §0 · DAY_ENGINE banner · [TODAY_PRODUCT_FLOW_V1](./TODAY_PRODUCT_FLOW_V1.md) (экраны) · SCENARIO_V3 superseded as product map · README · tracker.
- **2026-08-17:** step 2 lookup = Interpretation Library (schema only; not a second Meaning SoT). User-facing planet×sign catalog **rejected** (ACM + IL layers). IL-1 Layer 5 gold list = curated candidates until IL-2.
- **Backward compatible?** yes API until nests land; old clients ignore.
