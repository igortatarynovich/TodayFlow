# DAY_SCENARIO_V1 — legacy engine notes (не Meaning SoT)

**Status:** **SUBORDINATE / MIGRATION** — код B1–C5 ещё живёт здесь; **Meaning SoT Today = только** [TODAY_CONTENT_PIPELINE_V1](./today/TODAY_CONTENT_PIPELINE_V1.md).  
**Date:** 2026-08-15  
**Не использовать этот файл как канон «почему показали это».** При конфликте с pipeline — побеждает pipeline.

**Engine (current code):** `day_scenario_v1.py` · `day_color_catalog_v1.py` · `day_scenario_project_v1.py` · `day_scenario_native_llm_c1.py` · …  
**Wire / UI / eval notes:** audits `DAY_SCENARIO_*` (исторические landed phases).  
**Lifecycle:** [audits/DAY_LIFECYCLE_V1.md](./audits/DAY_LIFECYCLE_V1.md)  
**Related:** [DAY_ENGINE_AND_COHERENCE.md](./DAY_ENGINE_AND_COHERENCE.md) · [SCREEN_CONTRACTS_V1.md](./SCREEN_CONTRACTS_V1.md)

---

## Историческая модель (superseded as Meaning SoT)

Ниже — описание **текущего** native/B5 движка (conflict → scenes → chorus).  
Целевая модель смысла: **Небо → Global Day → Natal Overlay → Ritual → Personal → Presentation** — только в [TODAY_CONTENT_PIPELINE_V1](./today/TODAY_CONTENT_PIPELINE_V1.md).  
Product cycle: [TODAY_PRODUCT_FLOW_V1](./today/TODAY_PRODUCT_FLOW_V1.md) — TODAY → RITUAL → MY DAY → EVENING. UX reveal ≠ порядок authority. Natal Overlay — backend, не кадр.

| Было (B5 / C1) | Стало (pipeline I0) |
|----------------|---------------------|
| `day_scenario` = Meaning SoT | Global Day Profile + Personal Day Profile |
| Хор astro+card+number+natal в одном вызове | Card/number только Personal; Global без них |
| LLM `visual_mode` | Deterministic `primary_energy` |

**Запрещено по-прежнему:** четыре независимых прогноза (гороскоп / карта / число / натал) как разные сюжеты.

---

## Source of Truth rule (актуально)

```text
TODAY_CONTENT_PIPELINE_V1  ← единственный Meaning SoT
        ↑
этот файл = hygiene I0–I8 + описание legacy code до cutover
```

**`day_scenario` больше не Meaning SoT.** До cutover — literary/runtime scaffold; props/сцены не имеют права определять energy/windows в обход Global Day Engine.

### Legacy runtime (код до cutover)

Пока native/B5 ещё в проде: практические артефакты (цвет, цель, аффирмация…) не invent вне сцены; provenance `origin_scene_id`.  
**После cutover** provenance → Global/Personal Profile + enrichments (см. pipeline), не conflict/scenes.

`day_thesis` — **ярлык / проекция Акта III**, не параллельный сюжет.  
DomainLens / FE sphere cards — **проекции Акта V**.  
Date-preset color catalog **не** meaning SoT (может остаться seed).

Карта дня и число дня — **не** SoT сюжета и **не** отдельные продукты внутри Today.

---

## Meaning authority invariants (LOCKED 2026-08-15 · I0 refined same day)

**Content pipeline SoT:** [TODAY_CONTENT_PIPELINE_V1](./today/TODAY_CONTENT_PIPELINE_V1.md) — Небо → Global Day → Natal Overlay → Ritual → Personal → Presentation.  
`day_scenario` **не** универсальный Meaning SoT. Максимум literary scaffold над уже зафиксированными Global/Personal Profile.

Повторность: одинаковые входы + одинаковые версии правил → одинаковый смысл. LLM не выбирает energy, drivers, окна.

### I0. Interpretation Layers

Global interpretation completes **without** personal, tarot, or numerology evidence.  
Personal interpretation **consumes** Global Day and may contextualize it, **never redefine** it.  
Ritual symbols are overlays and **never** participate in Global Day determination.

Два человека в одной day-location/TZ + одна версия правил → один Global Day.

Natal Overlay — детерминированный шаг цепочки (небо × натал) **между** Global и Personal. **Не** третья interpretation authority и **не** экран.

### I1. Две последовательные authority (не один контейнер)

| Authority | Решает | Не решает |
|-----------|--------|-----------|
| **Global Day** | какой день, energy, strength, risk, windows, drivers | натал, карта, число, цели |
| **Personal Day** | как день касается человека; focus; bridges | global mood/drivers/windows |

Любой user-facing claim трассируется к Global Profile, Personal Overlay, ritual catalog, **или** persist narrative этих слоёв.  
Запрещено: параллельный LLM-сюжет; fill-empty, вводящий новую тему; FE-астрология; карта/число, переписывающие Global energy.

**Code now:** native C1 всё ещё один вызов (chorus+conflict+natal+card+number) — **нарушение I0**. Kimi timeline — нарушение. Guide generation — нарушение. B5 exclusive overwrite не спасает смешение слоёв.

### I2. Projector MAY transform structure, NEVER meaning

`project_day_scenario_onto_day_story_v1` — lossless mapping Scenario → public slots.  
Разрешено: переименовать, сложить в legacy aliases, slim chorus для wire.  
Запрещено: решать, какая сцена primary; склеивать новый prose; выбирать practice vs affirmation; invent evening_closure.

**Code now:** projector maps `primary_scene_id` (fill-empty from unique `role_in_story==primary` on cached packages). Нет first-scene guess. `expect` = `what_happens` (fill-empty `opportunity`), без concat. `do` только из primary scene + её goals. `practice_recommendation.kind` с пропа, без выбора practice vs affirmation.

Canonical public theme field: **`day_story.theme`**. `headline_anchor`, `primary_conflict`, `day_thesis.label_ru`, `global_period` — **deprecated aliases** того же `conflict.title` / `conflict.short_name`. Не три разных semantic concept.

### I3. Scenario несёт `primary_scene_id`

LLM (или deterministic engine) **обязан** выставить `primary_scene_id`, существующий среди `scenes[].scene_id`. Quality gate rejects missing/unknown id.  
Downstream (expect / trap / do / avoid / color / morning goal / evening trap-check) читает **только** эту сцену + её props. Projector не выбирает primary.

**Code now:** native schema несёт `primary_scene_id`; gate rejects missing/unknown. Fill-empty из unique `role_in_story==primary` на cached/normalize. Projector не выбирает primary.

### I4. Timeline ∈ Global Day Engine (до любого narrative)

Часы / intensity / `supports[]` / `cautions[]` = geometry + Astrology Canon. Существуют **до** LLM.  
LLM #1 только формулирует уже готовые окна. Scenario не классифицирует окна.  
**Запрещён** `day_flow_windows_kimi_v1`.

### I5. Immutable DayPackage identity + version manifest

После успешной native generation пакет дня неизменяем в пределах `(owner, local_date)`:

```text
identity = owner_key + local_date + scenario_version + evidence_version
```

Refresh / GET = retrieve + re-project + fill missing **deterministic** surfaces. Не regenerate narrative.  
Regeneration — только admin / version-migration / explicit owner tool.

Manifest (сохранять на записи, не только в логах): `sources_version` · ephemeris · `scenario_prompt_version` · `scenario_schema_version` · `persona_version` · `projector_version` · `card_catalog_version` · `number_catalog_version` · `color_catalog_version` · `practice_catalog_version` · `today_contract_version`.

**Code now:** `day_story_fingerprint_v1` есть, но включает mood/goals/profile_snapshot/sky_digest/color — смена входа **может** инвалидировать тот же день. `kept_prior_native` при LLM fail. `REGENERATE_ON_MODEL_CHANGE = False`. Полного version manifest на пакете нет. Fingerprint **намеренно** исключает card/number (overlay).

### I6. Timezone / rollover / precompute / invalidation — явные правила

| Вопрос | Правило |
|--------|---------|
| Birth TZ / place | Только natal chart (L3). Не «сегодняшний день». |
| Day TZ / location | Гражданский день Today = **day timezone** (push schedule TZ, иначе explicit request, иначе default). Device TZ не подменяет birth. |
| Travel same calendar day | Не пересобирает Scenario. Часы timeline/VOC могут пересчитаться как deterministic overlay, если day TZ сменился **до** assemble; после ready — immutable narrative. |
| Rollover | `local_date` меняется в **local midnight** day TZ. |
| Precompute | TARGET: пакет **D** готов до midnight D−1. Текущий clock (assemble 03:00–05:00, `ready_at` 05:00, 00:00–ready = `day_not_ready`) — **не** менять без отдельного Architecture impact на [DAY_LIFECYCLE_V1](./audits/DAY_LIFECYCLE_V1.md). |
| Profile facts mid-day (DOB/time/place added) | Narrative immutable today. Новые L3 overlays (why_personal / natal timeline) — **со следующего** local_date. Исключение: deterministic facts-only surfaces, которые не меняют conflict/scenes. |

### I7. Capability matrix (Today)

Sources → allowed fields → allowed screens. Не один ScreenFlow с пустыми слотами, притворяющимися персональными.

| Depth | Sources | Allowed meaning | Honest omit |
|-------|---------|-----------------|-------------|
| **guest** | L1/L2 shared sky, universal day, prebaked card | atmosphere, sky strip, universal number, card base | why_personal, natal timeline, Personal Day, personalized instruction/promise |
| **general** | + account, no/thin natal | shared story; chorus natal empty | why_personal, deep natal |
| **light** | DOB (no time/place) | Personal Day; light why_personal; no houses/ASC claims | natal house/angle overlay |
| **deep** | DOB + time + place | natal activations, why_personal, natal timeline | none of the above if evidence present |

Sphere selection ranks **evidence relevance**, not UI diversity. Нельзя добивать work/people/self ради сетки.

**Number (locked school):** masters **11, 22, 33** ([NUMBER_BASE_V1](./numerology/NUMBER_BASE_V1.md) · DAY_SOURCES_CANON §3). Nested PY→PM→PD. **UI identity:** Personal Day if `birth_date`; else Universal Day. Ritual prebake uses `ritual_day_number` (DAY_SOURCES numerology adapter) — **landed 2026-08-15**.

**Card identity (already executable):** `sha256(owner_key \| local_date \| "day_card") % 78` + orientation digest. Deck version must enter I5 manifest.

### I8. Provenance на каждом interpretive output

Каждый meaning slot: `source_refs[]` (`origin_scene_id` · `origin_conflict_id` · `evidence_refs` · `source_kind`).  
Gate: *Every user-facing interpretive claim traces to Scenario or deterministic evidence.* Orphan / untraced → reject or omit, не fallback-гороскоп.

**Code now:** `editorial.slot_provenance` на B5 projection — минимум. Не покрывает timeline Kimi copy, color catalog why beyond `link_to_conflict`, guide payload.

### Enrichment vs meaning (правило)

Deterministic enrichment **может** конкретизировать уже существующий смысл (время окна, имя цвета из каталога, base meaning карты). **Не может** ввести тему, которой нет в Scenario (пример запрета: timeline «лучше обсудить деньги», если денег нет в scenes/conflict).

Color engine / practice engine / number / card: selection + catalog lookup — OK; user-facing *why* — только chorus/props с provenance.

`primary_energy` (тот же закрытый 8-set) считает Global Day Engine. `visual_mode` = UI map от energy (пока 1:1). **LLM не выбирает energy.** Code now: native LLM `visual_mode` — **удалить как decision** (pipeline § overlay).

Fallback без LLM: **structurally poorer** (факты неба + omit сюжета), не второй template Narrative Engine. B5 `deterministic_engine_b5` обязан подчиняться этому (сейчас строит полный scenario spine из ranked facts — **риск** I1/I8).

`practice_recommendation` как generic bucket — **legacy**. Target: typed `daily_actions[]` (`practice` \| `affirmation` \| `reflection` \| `goal`) с `origin_scene_id`. Не смешивать практику и аффирмацию в одном kind.

### Core vs depth (метрика экрана)

**Core answer (1–2 минуты):** экран **TODAY** = Global Day (ENERGY% + mood → Global clock → timed transits → STRENGTHS → RISKS). MY DAY = персональный слой. Ritual = линзы. Evening = благодарность. [TODAY_PRODUCT_FLOW_V1](./today/TODAY_PRODUCT_FLOW_V1.md).  
**Ritual:** карта/число — линзы, не пересчёт.  
**Depth:** Personal Day (instruction / bridges) + color / tasks / loop.  
Нельзя считать полезность как прохождение всех 6–7 шагов.

---

## Architecture impact (2026-08-15 — I0 + pipeline)

- **SoT before:** I1 = один DayScenario Meaning SoT.
- **SoT after:** I0 + [TODAY_CONTENT_PIPELINE_V1](./today/TODAY_CONTENT_PIPELINE_V1.md). Global Day / Personal Day — две authority. Scenario demoted. Energy и windows детерминированы до LLM.
- **Public contract changed?** target yes — phased nests; no wire bump in this lock.
- **Migration required?** yes — see pipeline overlay table.
- **Canon updated?** yes — this section · pipeline doc · DAY_SOURCES §0 · DAY_ENGINE banner · SCENARIO_V3 · tracker.
- **Backward compatible?** yes cached payloads.

---

## Уровень 2 — интерпретационный хор

Четыре голоса, один конфликт:

| Голос | Вопрос | Роль |
|-------|--------|------|
| **Астрология / астрономия** | Что происходит во внешней среде? | Называет факторы прямо: «Луна вошла в Рыбы», «соединение Венеры с Юпитером», «квадрат Марса» — и связывает их с конфликтом |
| **Карта дня** | Какой архетип уместен? | Не новая история. «Этот архетип лучше всего описывает сегодняшний конфликт» / «вот какой ролью лучше прожить день» |
| **Число дня** | Как проживается день? | Темп, стиль, урок, способ прохождения **уже** определённого конфликта — окрашивает, не создаёт второй сюжет |
| **Натал / личные транзиты** | Почему именно для этого человека? | Активации, усиление/ослабление — персональный «почему» |

### Норма языка (важно)

**Не избегать** узнаваемых формулировок вроде «Луна в Рыбах».  
Люди любят их: они просто объясняют происходящее и делают день убедительным.

Плохо: только «сегодня осторожнее» без опоры.  
Хорошо: «Сегодня Луна вошла в Рыбы. Поэтому эмоции становятся сильнее логики…» — и это **ведёт** к уже названному конфликту.

Порядок для пользователя:

1. Сначала — главный конфликт / история дня.  
2. Затем — факторы, которые к нему привели (Луна в Рыбах · Карта — Отшельник · Число — 7 · ваш натальный Нептун).

### Карта дня — интерпретационный слой, не модуль

- Не источник истории дня.  
- Не должна противоречить астрологическому рассказу.  
- Говорит: какой архетип / роль описывает **этот** конфликт.

### Число дня — способ прохождения, не вторая история

- Не рассказывает новый сюжет.  
- Отвечает: темп, стиль поведения, урок, как пройти конфликт.  
- «Окрашивает» историю.

### Диалог систем

Системы **разговаривают** между собой вокруг одного конфликта:

- астрология — что происходит;  
- карта — какой архетип уместен;  
- число — какой способ действия естественен;  
- натал — почему именно вам.

Это авторский язык Today: не набор функций рядом, а единый хор.

### Chorus = sole bridge for day hooks (2026-08-01)

Для крючков «карта / число / цвет» поле **`bridge_to_day`** в `hook_reveal` берётся **только** из хора / props assemble-once:

| Крючок | Sole SoT моста |
|--------|----------------|
| Карта | `interpretive_chorus.day_card.link_to_conflict` (+ роль из того же voice) |
| Число | `interpretive_chorus.day_number.link_to_conflict` (+ tempo/style) |
| Цвет | `props.color.link_to_conflict` |

`tarot_explainer` / `numerology_explainer` **не** пишут параллельный мост и **не** переписывают канонический `base` (см. [DAY_SYMBOL_REVEAL_CANON_V1](./audits/DAY_SYMBOL_REVEAL_CANON_V1.md)). Пустой chorus → `bridge_status=unavailable`, не «догенерировать другим путём».

Базовые значения карт — единый `card_base_v1` (78×upright/reversed); числа — `number_base_v1`; цвет — `COLOR_CATALOG_V1`.

---

## Структура сценария (Уровень 1)

### Пролог — главный сдвиг дня

**Цель:** что изменилось по сравнению со вчера.

**Вход:** астрономия · астрология · циклы · натал · карта дня · число дня · user context · history.

**Выход:** `day_shift` — один главный сдвиг (не список событий).

### Акт I. Экспозиция — какой сегодня мир?

Не про пользователя. Про среду.

**Выход:** главная энергия · доминирующий конфликт среды · темп · предсказуемость.  
Факторы хора (Луна/аспекты) могут уже звучать как объяснение среды.

### Акт II. Персонализация

Почему для **этого** человека день отличается от среднего?

**Выход:** активируемые натальные факторы · что усиливается / ослабляется · почему.  
Карта/число здесь ещё не «второй прогноз» — они могут наметить архетип/темп, если уже известны.

### Акт III. Драматический конфликт

Ровно **одна** центральная линия. Примеры осей: безопасность↔рост · скорость↔качество · отношения↔независимость · логика↔эмоции.

Все дальнейшие рекомендации **и** все голоса хора **обязаны** обслуживать этот конфликт.

### Акт IV. Развитие — последствия, не советы

Какие сферы в центре · какие решения возникнут · соблазны · возможности.

### Акт V. Сцены

Конфликт проявляется в релевантных областях. Для каждой сцены:

- почему сфера важна сегодня  
- как проявится конфликт  
- возможность  
- ловушка  

Кандидаты: работа · отношения · деньги · общение · здоровье · отдых · творчество.  
Только участвующие в истории.

### Акт VI. Реквизит

Прикладные рекомендации **только** из истории; каждый элемент → ссылка на сцену.

Включая: цвет · avoid-цвет · цель · аффирмация · настроение · музыка · место · символ · юмор.

Необязательные типы — только если сцена естественно допускает.

**Цвет:** не «синий успокаивает», а связь с ловушкой/конфликтом; где применить; какой avoid усиливает риск **этого** дня.

**Реквизит решает trap** (не украшает день): аффирмация / практика / юмор обязаны `compensates_trap` или `serves_conflict`. Orphan «планета=цвет» и wellness-клише — reject.  
Стиль-калибровка: [DAY_SCENARIO_STYLE_HOOK_MECHANICS_V1.md](./audits/DAY_SCENARIO_STYLE_HOOK_MECHANICS_V1.md).

### Акт VII. Развязка

Если прожить день осознанно — что к вечеру? (`evening_payoff`)

`evening_payoff` — отложенная проверка («завтра окажется…»), не мораль. Даёт причину открыть вечер/завтра; крючок = любопытство + маленькое полезное действие, не тревожный чекин.

---

## Generation order (Phase B)

1. Facts: небо, циклы, натал, **карта дня**, **число дня**, history  
2. Interpretive chorus (Уровень 2) — факторы с ролями, без второго сюжета  
3. Scenario spine (prolog → **conflict** → consequences → scenes)  
4. Props derived from scenes (**B2**)  
5. Project to contract / UI (**B3–B5**): exclusive SoT; хор = объяснение, не вкладки-конкуренты  
6. Value gate: reject orphan props; second conflict; card/number that invent a rival story; scene without conflict link  

### B1–B5 shipped

- `build_day_scenario_v1` → foundation · chorus · conflict · scenes · props (`runtime_sot=true`)
- Wire: `project_day_scenario_onto_day_story_v1` **overwrites** meaning slots (not fill-empty hybrid)
- Public additive nests: `day_story.day_scenario`, `day_story.interpretive_chorus`
- Color / avoid / goals / affirm / domains only from scenario props/scenes
- Missing scenes → `unavailable` + stripped editorial (no legacy story leak)
- **B4 FE:** prefer talisman/chorus/scenes in Today model (not full UI rewrite)
- **B5:** exclusive runtime SoT; GET/refresh lifecycle unchanged

Fallback: facts-only / unavailable — **не** formula-bank / catalog why / LLM parallel prose.

---

## Architecture impact (Phase B — progressive)

### B1–B3 (landed) — engine + props + wire projection (historical)

```markdown
## Architecture impact
- **SoT before:** day_story LLM/fallback; color = celestial preset + catalog why
- **SoT after (projected fields):** day_scenario → day_story; color/affirm/domains-fill/thesis from scenario;
  LLM prose kept when present; unavailable may recover via scenes
- **Public contract changed?** additive nests only
- **Migration required?** no
- **Canon updated?** yes — DAY_SCENARIO_V1 + DAY_SCENARIO_WIRE_PROJECTION_B3
- **Backward compatible?** yes — old clients ignore new nests; FE color guide may still prefer morning until B4
```

### B4 (landed) — FE preference for scenario nests

```markdown
## Architecture impact
- **SoT before (FE):** morning catalog color why; tarot/number parallel dumps; domains-only spheres
- **SoT after (FE):** talisman/chorus/scenes preferred when present; no layout redesign
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — DAY_SCENARIO_V1 + DAY_SCENARIO_UI_PREFERENCE_B4
- **Backward compatible?** yes — missing nests keep prior FE paths
```

### B5 (landed) — exclusive runtime meaning SoT

```markdown
## Architecture impact
- **SoT before:** hybrid overlay — LLM expect/trap/do kept; domains LLM preserved; fill-empty only
- **SoT after:** day_scenario_v1 sole meaning SoT when ready; legacy slots = projections;
  missing scenario/scenes → unavailable + stripped meaning (facts_only / meta_only)
- **Public contract changed?** semantics of meaning fields (always scenario when ok);
  unavailable blanks talisman/practice on contract
- **Migration required?** no today_contract version bump; caches re-projected on serve
- **Canon updated?** yes — DAY_SCENARIO_V1 + DAY_SCENARIO_RUNTIME_SOT_B5
- **Backward compatible?** field shapes yes; parallel LLM meaning no longer visible when scenario ready
```

### Next — fuller scene UI (after B5)

Compose Today around prolog → conflict → chorus → scenes → props-in-scene → evening vector.  
**Does not** reintroduce hybrid meaning; SoT remains B5.

### C1 (landed) — Native Scenario Generation

```markdown
## Architecture impact
- **SoT before:** LLM wrote legacy expect/trap/do; B5 discarded as meaning
- **SoT after:** refresh LLM writes day_scenario_native_llm_c1; props deterministic; projector adapts
- **Public contract changed?** no
- **Migration required?** pre-C1 cache without generation_source → unavailable until refresh
- **Canon updated?** yes — DAY_SCENARIO_NATIVE_LLM_C1
- **Backward compatible?** field shapes yes
```

### Next — C2 Chapters UI

Compose Today as story chapters from conflict + scenes (not independent widgets).  
Legacy projections remain for old clients only.

### C2 (landed) — Story chapters UI

```markdown
## Architecture impact
- **SoT before (FE):** Day Map from projected expect/trap/do
- **SoT after:** scenario-ready → five chapters from conflict/chorus/scenes/props;
  fallback Day Map / legacy when scenario missing or unavailable
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — DAY_SCENARIO_CHAPTERS_C2
- **Backward compatible?** yes
```

### C3.1 (landed) — Everyday scenes + editorial gate

```markdown
## Architecture impact
- **SoT before:** schema-valid native scenario could ship abstract/universal scenes
- **SoT after:** editorial gate + retry feedback; critical fail → unavailable (no formula rewrite)
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — DAY_SCENARIO_EVERYDAY_QUALITY_C31
- **Backward compatible?** yes
```

### C3.2 (landed) — Chorus causal chain

```markdown
## Architecture impact
- **SoT before:** chorus could pass as four parallel mini-forecasts
- **SoT after:** editorial gate enforces astrology→env · card→archetype · number→tempo · natal→personal;
  conflict_id binding; critical fail → retry → unavailable
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — DAY_SCENARIO_CHORUS_QUALITY_C32
- **Backward compatible?** yes
```

### C3.3a (landed) — Personalization evidence contract

```markdown
## Architecture impact
- **SoT before:** personalization decorative (why_personal / natal only)
- **SoT after:** evidence pack + depth modes + gate; bad personalization → downgrade general
  (or unavailable on profile leak); structural traces required for deep
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — DAY_SCENARIO_PERSONALIZATION_C33A
- **Backward compatible?** yes
```

### C3.3b (landed) — Sphere selection + pairwise eval

```markdown
## Architecture impact
- **SoT before:** sphere choice unconstrained beyond soft unjustified checks
- **SoT after:** sphere_selection candidates on pack; outside-pack needs justification;
  pairwise A/B/control eval harness (no Nebius)
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — DAY_SCENARIO_SPHERE_SELECTION_C33B
- **Backward compatible?** yes
```

### C3.5 (landed) — Eval pack (14 days × profiles × locales)

```markdown
## Architecture impact
- **SoT before:** pairwise same-day only
- **SoT after:** 14d × 4 profiles (incl. no birth time) × ru/en eval pack;
  fixture CI matrix; live captures optional
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — DAY_SCENARIO_EVAL_PACK_C35
- **Backward compatible?** yes — eval-only
```

### C3.5.1 (landed) — Eval hardening (28d × 11 profiles · dual scores · EN parity gate)

```markdown
## Architecture impact
- **SoT before:** C3.5.0 14×4×2 pack; EN heuristic; soft provenance/closure
- **SoT after:** c35.1 harness — 28×11×2 = 616 cells; dual contract/editorial; EN editorial
  eval gate; provenance + day_closure c351; baseline report; fixtures/mutations
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — DAY_SCENARIO_EVAL_HARDENING_C351
- **Backward compatible?** yes — legacy matrix wrapper retained
- **Runtime gates / today.py / Nebius / UI / lifecycle:** untouched
```

### C3.6 (landed) — Gate Maturity & Runtime Safety

```markdown
## Architecture impact
- **SoT before:** editorial CRITICAL + soft personalization could retry / downgrade /
  unavailable in native LLM user loop
- **SoT after:** maturity registry is sole runtime-policy owner; quality analyzers
  score/defects → capture; hard contract/safety blocks; PROFILE_FACT_LEAK
  immediate reject (no quality rewrite); no quality→general downgrade
- **Public contract changed?** no — gate_maturity/policy not added to user API;
  capture-only for maturity annotations
- **Migration required?** no
- **Canon updated?** yes — DAY_SCENARIO_GATE_MATURITY_C36
- **Backward compatible?** yes — hard still unavailable
```

### C3.6.3 (landed) — Selective quality promotion (sealed C3.6.2 pilot)

```markdown
## Architecture impact
- **SoT before:** all quality codes observe-only under C3.6
- **SoT after:** SCENE_CLONE / SCENE_MISSING_EVERYDAY / SCENE_ABSTRACT /
  ASTRO_JARGON_BARE → blocking (retry then unavailable); SCENE_UNIVERSAL_ADVICE →
  candidate_blocking; maturity remains sole policy owner
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — DAY_SCENARIO_GATE_PROMOTION_C363
- **Backward compatible?** yes for clients; more unavailable on B5-style defects
```

### C3.6.1 (landed) — Calibration harness (synthetic bootstrap · P/R/FPR · RU/EN)

```markdown
## Architecture impact
- **SoT before:** C3.6 observe-only quality; no per-code calibration metrics
- **SoT after:** c36.1 harness + 14 synthetic golden cases; TP/FP/TN/FN;
  measured|insufficient_support; shadow false-block KPI; baseline artifacts —
  **no maturity promotions**
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — DAY_SCENARIO_GATE_CALIBRATION_C361
- **Backward compatible?** yes — eval-only
- **Runtime / Nebius / UI / retry:** untouched
```

### Next — C3.6.2 Human Golden Set and Review Protocol

> Manual labeling + disagreement resolution before any maturity promotion.
> Synthetic bootstrap alone is not promotion evidence.
> C3.6 maturity remains sole runtime-policy owner
> ([DAY_SCENARIO_GATE_MATURITY_C36.md](./audits/DAY_SCENARIO_GATE_MATURITY_C36.md)).

### C3.6.2 (landed) — Human golden protocol + tooling (0 production labels)

```markdown
## Architecture impact
- **SoT before:** C3.5c scaffold + synthetic_bootstrap only
- **SoT after:** human case contract, blind export, dual review, adjudication,
  consensus, agreement metrics, consensus-only calibration adapter
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — DAY_SCENARIO_HUMAN_GOLDEN_C362 + rubric + schema
- **Backward compatible?** yes — eval-only
- **Runtime / maturity / Nebius / UI:** untouched; no promotions; no fake 40 labels
```

### Next — analyzer gaps from human calibration

**Progress:** **40/40** sealed · human calibration baseline landed
([DAY_SCENARIO_HUMAN_CALIBRATION_C362.md](./audits/DAY_SCENARIO_HUMAN_CALIBRATION_C362.md)).
`CHORUS_SEMANTIC_DUPLICATION` → candidate_blocking; `SCENE_UNIVERSAL_ADVICE` stays candidate.
`SCENE_MISSING_EVERYDAY` lived-specificity fix landed (calib P=R=1.0).
`ASTRO_JARGON_BARE` FP fix landed (shadow false blocks **0**).
Next: improve `SCENE_UNIVERSAL_ADVICE` recall before any blocking promotion.

---

## Non-goals

- Обязательные humor/music/place каждый день  
- Compatibility modules как Today SoT  
- Скрытие имён планет/знаков «чтобы было проще»  
- Четыре независимых прогноза на одном экране  
- Диагноз «модель плохая»
- **Paywall / серые замки на base day_scenario** — подписка только добавляет optional depth layer ([TODAY_DEPTH_LAYER_V1.md](./TODAY_DEPTH_LAYER_V1.md))
