# DAY_SCENARIO_V1 — драматургический каркас дня

**Status:** CANON DRAFT — **B1–B5 + C1 + C2 landed** (SoT + native LLM + **story chapters UI**); language polish open  
**Date:** 2026-07-25  
**Engine:** `day_scenario_v1.py` · `day_color_catalog_v1.py` · `day_scenario_project_v1.py` · `day_scenario_native_llm_c1.py`  
**Wire note:** [audits/DAY_SCENARIO_WIRE_PROJECTION_B3.md](./audits/DAY_SCENARIO_WIRE_PROJECTION_B3.md)  
**UI note:** [audits/DAY_SCENARIO_UI_PREFERENCE_B4.md](./audits/DAY_SCENARIO_UI_PREFERENCE_B4.md)  
**Runtime SoT:** [audits/DAY_SCENARIO_RUNTIME_SOT_B5.md](./audits/DAY_SCENARIO_RUNTIME_SOT_B5.md)  
**Native LLM:** [audits/DAY_SCENARIO_NATIVE_LLM_C1.md](./audits/DAY_SCENARIO_NATIVE_LLM_C1.md)  
**Chapters UI:** [audits/DAY_SCENARIO_CHAPTERS_C2.md](./audits/DAY_SCENARIO_CHAPTERS_C2.md)  
**Capture rubric:** [audits/DAY_PRODUCT_LOGIC_CAPTURE_PACK.md](./audits/DAY_PRODUCT_LOGIC_CAPTURE_PACK.md)  
**Related:** [DAY_ENGINE_AND_COHERENCE.md](./DAY_ENGINE_AND_COHERENCE.md) · [SCREEN_CONTRACTS_V1.md](./SCREEN_CONTRACTS_V1.md) · [today-language/TODAY_LANGUAGE_V1.md](./today-language/TODAY_LANGUAGE_V1.md)

---

## Два уровня (не смешивать)

| Уровень | Вопрос | Что это |
|---------|--------|---------|
| **1 — Что происходит** | Какая сегодня история? | **Сценарий** (`day_scenario`): конфликт → сцены → реквизит → UI |
| **2 — Почему это происходит** | Какие факторы к ней привели? | **Интерпретационный хор**: астрология · карта дня · число дня · натал |

Уровень 2 **усиливает** сценарий, а не конкурирует с ним.  
Астрология / таро / нумерология — **язык объяснения одной истории**, не четыре независимых прогноза.

```text
Факты (небо, циклы, натал, карта дня, число дня)
        ↓
Единый интерпретационный слой  ← «почему» (Уровень 2)
        ↓
Главный конфликт дня           ← «что» (Уровень 1)
        ↓
Сцены → Реквизит → UI
```

**Запрещено:** складывать рядом «гороскоп», «карту дня» и «число дня» как отдельные модули с разными сюжетами.  
**Нужно:** четыре взгляда на **один** день.

---

## Source of Truth rule

```text
Факты → Интерпретационный хор → Главный конфликт → Сцены → Реквизит → UI
```

**Сценарий дня (`day_scenario`) — SoT Уровня 1** для пользовательских поверхностей Today.

Ни один практический артефакт не генерируется отдельно от сцены:

- цвет / нежелательный цвет
- цель дня
- аффирмация
- настроение / вайб
- музыка / место / символ
- юмор / сюжетный намёк

Каждый элемент реквизита обязан иметь **происхождение** (`origin_scene_id` и/или `serves_conflict`).

`day_thesis` — **ярлык / проекция Акта III**, не параллельный сюжет.  
DomainLens / FE sphere cards — **проекции Акта V**.  
Date-preset color catalog **не** meaning SoT (может остаться seed).

Карта дня и число дня — **не** SoT сюжета и **не** отдельные продукты внутри Today.

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

### Акт VII. Развязка

Если прожить день осознанно — что к вечеру? (`evening_payoff`)

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

### Next — language / personalization quality

---

## Non-goals

- Обязательные humor/music/place каждый день  
- Compatibility modules как Today SoT  
- Скрытие имён планет/знаков «чтобы было проще»  
- Четыре независимых прогноза на одном экране  
- Диагноз «модель плохая»
