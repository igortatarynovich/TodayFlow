# Practice Content Taxonomy v1

**Статус:** `ACCEPTED` — SoT библиотеки практик / медитаций / аффирмаций / дисциплин.  
**Версия:** 1.2 (2026-08-25) — Canonical Technique слой; item = expression. Fill pointer 2026-08-26: lightweight, not research ladder.  
**Владелец:** Product.  
**Machine vocab:** [`DATA/reference/practice/content_taxonomy_v1.json`](../../DATA/reference/practice/content_taxonomy_v1.json).  
**Item contract:** [`DATA/reference/practice/content_item_contract_v1.json`](../../DATA/reference/practice/content_item_contract_v1.json).  
**Technique canon:** [PRACTICE_TECHNIQUE_PROVENANCE_V1.md](./PRACTICE_TECHNIQUE_PROVENANCE_V1.md) · [`technique_canon_v1.json`](../../DATA/reference/practice/technique_canon_v1.json).  
**Active fill:** [PRACTICE_LIBRARY_FILL_V1.md](./PRACTICE_LIBRARY_FILL_V1.md).  
**Coverage:** [PRACTICE_CONTENT_COVERAGE_V1.md](./PRACTICE_CONTENT_COVERAGE_V1.md) · [`content_coverage_matrix_v1.json`](../../DATA/reference/practice/content_coverage_matrix_v1.json).

**Это:** классы, типы и атрибуты контентных объектов. Смысловой движок говорит *какая потребность*, библиотека отвечает *каким объектом*.  
**Это не:** экран `/practices` · C1 evolution registries · массовое LLM-наполнение items · медицинские claims. Provenance техник — отдельный канон, не этот файл.

**Связанные (не заменяют этот файл):**

| Документ | Роль |
|----------|------|
| [PRACTICE_LIBRARY_FILL_V1.md](./PRACTICE_LIBRARY_FILL_V1.md) | **Active fill.** Lightweight provenance. Research ladder не блокирует. |
| [PRACTICE_TECHNIQUE_PROVENANCE_V1.md](./PRACTICE_TECHNIQUE_PROVENANCE_V1.md) | **SoT происхождения техники.** Одна запись на технику. LLM не источник метода. |
| [PRACTICE_TECHNIQUE_RESEARCH_ARCHIVE_V1.md](./PRACTICE_TECHNIQUE_RESEARCH_ARCHIVE_V1.md) | **Research archive.** Landscape → … → Targeted Safety — historical, non-blocking. |
| [PRACTICE_CONTENT_COVERAGE_V1.md](./PRACTICE_CONTENT_COVERAGE_V1.md) | Coverage-first cells. Meaning не знает item_id / technique_id. Fill unfrozen. |
| [PRACTICES_SCREEN_V1.md](./PRACTICES_SCREEN_V1.md) | Need/format чипы и цикл сессии. Need ≠ type. Format ≠ type. |
| [REFERENCE_LAYER_AND_BUILD_ORDER.md](../REFERENCE_LAYER_AND_BUILD_ORDER.md) §2.5 · §2.8 | Куда кладётся Machine + Content. P2 fill ещё впереди. |
| [TODAYFLOW_PRODUCT_BUILD_MAP.md](../TODAYFLOW_PRODUCT_BUILD_MAP.md) `PracticeRecommendation` | Одна рекомендация на день. Meaning не знает `item_id`. |
| [TODAYFLOW_VOICE_CANON.md](../content/TODAYFLOW_VOICE_CANON.md) | Человек, не система. Ритуал = последовательность действий, не магия. |
| [KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md](../KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md) | Parent порядка исследования. Practice fill **не** требует steps 5–10. Не IL CORE. |

---

## Architecture impact

- **SoT before:** экран locked на 6 needs × 9 formats; C1.1 `practice_definition_registry` = 10 evolution action types; C1.4 ascetic definitions = конкретные ограничения; `CONTENT/practices/*.json` = плоский каталог без class/purpose/state. Type, цель и форма подачи смешивались (`meditation_for_sleep`-паттерн, сферы жизни как типы аффирмаций).
- **SoT after:** библиотека = `content_class` → (`family`) → `type` → Content Item. Purpose, domain, input_state, direction, duration, context, delivery — атрибуты, не типы. Четыре класса: `practice` · `meditation` · `affirmation` · `discipline` (user label «аскеза» где нужен этот язык).
- **Public contract changed?** no — Today/Profile JSON, `practice_recommendation`, screen need/format IDs не меняются этим документом.
- **Migration required?** no runtime. Legacy catalog и C1 registries остаются; remap Content Items — отдельный fill-pass.
- **Canon updated?** yes — этот файл · vocab JSON · `docs/practices/_INDEX.md` · README · Reference Layer §2.5/§2.8/§6 · tracker.
- **Backward compatible?** yes. Screen chips и C1 codes не deprecated. Новые объекты базы обязаны нести поля этой taxonomy.

**v1.1:** pipeline Meaning → Need → Retrieval → Library → Item locked. Content Item = identity / retrieval / payload. Fill = coverage-first ([PRACTICE_CONTENT_COVERAGE_V1](./PRACTICE_CONTENT_COVERAGE_V1.md)); library file empty. Public JSON still unchanged.

**v1.2:** Canonical Technique is the source of the *method*. Content Item is a product expression (`identity.technique_id` only if the technique row is `accepted`). LLM may formulate payload after a technique is accepted; it is not the technique source. Fill process — [PRACTICE_LIBRARY_FILL_V1](./PRACTICE_LIBRARY_FILL_V1.md). Public JSON still unchanged.

---

## 0. Закон

1. **Не смешивать технику, цель и форму подачи.** Запрещены типы вида `meditation_for_anxiety`, `affirmation_career`, `breathwork_morning`.
2. **Meaning не знает контентный объект.** Астрология, Character Engine, Today, Profile, Tarot выдают потребность (`input_state` → `direction` → `purpose[]`). Retrieval выбирает класс, тип и item.
3. **Один type — одна техника.** Цель живёт в `purpose[]`. Сфера — в `domain[]` (nullable). Состояние — в `input_state[]` / `direction[]`.
4. **Четыре разных job'а, четыре класса.** Разовое действие ≠ направленное внимание ≠ когнитивная формулировка ≠ правило на период.
5. **Не лечить.** Нет медицинских обещаний, протоколов расстройств, гарантий сна/питания. Contraindications — ограничения продукта, не диагноз.
6. **Обратной зависимости нет.** Ни Meaning, ни астрологическая семантика не знают `item_id`, `technique_id`, текст медитации или конкретную практику.
7. **Техника не выдумывается под ячейку.** Need cell говорит, *какую потребность* закрыть. Canonical Technique говорит, *какой метод* существует. Item — наша реализация. См. [PRACTICE_TECHNIQUE_PROVENANCE_V1](./PRACTICE_TECHNIQUE_PROVENANCE_V1.md).

Исключение product-layer: meditation type `sleep` (пользователь ищет «Sleep Meditation»). Семантически это цель; в retrieval всё равно ставить `purpose: sleep`. Других purpose-as-type не добавлять.

---

## 0.1 Pipeline (граница ответственности)

Две цепочки. Не смешивать.

**Происхождение метода** — [PRACTICE_LIBRARY_FILL_V1](./PRACTICE_LIBRARY_FILL_V1.md) · [PRACTICE_TECHNIQUE_PROVENANCE_V1](./PRACTICE_TECHNIQUE_PROVENANCE_V1.md):

```text
preferred type
  → reliable source check
  → canonical_description (своими словами)
  → safety_notes if materially required
  → accepted | skipped
  → Content Item (technique_id only if accepted)
```

Лестница Landscape → Shortlist → Ingest → Normalization → Targeted* → Safety Review — [archive](./PRACTICE_TECHNIQUE_RESEARCH_ARCHIVE_V1.md). Не unlock fill. `box_breathing` = `skipped_for_now`.

**Продуктовая выдача:**

```text
Meaning → Need → Retrieval constraints → Content Library → Content Item
```

| Слой | Выдаёт | Не выдаёт |
|------|--------|-----------|
| **Meaning** (астрология, Character Engine, Today, Profile, Tarot) | `input_state` → `direction` → `purpose[]`; при необходимости `domain[]` / `context[]` | `item_id`, `technique_id`, title, script, type как «эта медитация» |
| **Canonical Technique** | устойчивое ядро метода, provenance, safety, allowed/prohibited claims | пользовательский UI copy; смысл дня |
| **Retrieval** | `content_class` → `family?` → `type` + duration / intensity / energy_effect / delivery и прочие ограничения | пользовательский текст |
| **Library** | конкретный `item_id` (expression канона) | смысл дня |

Need в этой цепочке — семантическая потребность (state/direction/purpose), не chip экрана `/practices`. Screen need — UX-проекция, см. §12.1.

Fill-pass **разморожен**. Active process = lightweight provenance. 133 items остаются `llm_provisional`, пока ячейка не переписана против `accepted` technique. `box_breathing` skipped — [PRACTICE_CONTENT_COVERAGE_V1.md](./PRACTICE_CONTENT_COVERAGE_V1.md).

---

## 1. Слои

```text
canonical technique    verified method kernel (provenance)
  └─ content_class     product object
       └─ family       только practice (breathwork, somatic, …)
            └─ type    код техники в taxonomy
                 └─ item    продуктовая реализация (2 min / audio / evening)
```

Атрибуты висят на **item** (и могут быть дефолтом на type, но не вместо type):

`purpose[]` · `domain[]` · `input_state[]` · `direction[]` · `duration` · `intensity` · `energy_effect` · `context[]` · `delivery` · `contraindications[]` · `semantic_version`

`family` в схеме = колонка «Class» внутри Practice. Не путать с `content_class`.

Уникальность type: пара `(content_class, type)`. Одинаковые коды в разных классах допустимы (`grounding`, `body_scan`, `visualization`, `gratitude`, `silence`) — это разные объекты.

---

## 2. content_class

| code | Внутреннее имя | User-facing | Job |
|------|----------------|-------------|-----|
| `practice` | practice | Практика | Сделать действие сейчас |
| `meditation` | meditation | Медитация | Направить внимание / состояние |
| `affirmation` | affirmation | Аффирмация | Когнитивная формулировка / установка |
| `discipline` | discipline | Аскеза *или* дисциплина | Соблюдать правило во времени |

`discipline` — внутренний код. «Аскеза» — label там, где продукту нужен этот язык. Не плодить второй class `ascetic`.

Почему meditation отдельный class: пользователь ищет Медитацию как самостоятельный объект, не «практику типа meditation».

Почему discipline не subtype practice: это не 5 минут дыхания сегодня, а ограничение/обязательство на период (`duration_days`, `commitment_rule`, `failure_policy`). Recommendation engine обязан различать эти job'ы.

---

## 3. Practice — family → type

Ritual здесь — структурированная последовательность действий, не обязательные магические акты.

### 3.1 breathwork

| type | Смысл |
|------|--------|
| `paced_breathing` | дыхание по заданному ритму |
| `extended_exhale` | удлинённый выдох |
| `box_breathing` | равные фазы дыхания |
| `physiological_sigh` | двойной вдох + длинный выдох |
| `energizing_breath` | активирующее дыхание |

### 3.2 somatic

| type | Смысл |
|------|--------|
| `body_release` | сброс телесного напряжения |
| `grounding` | возвращение внимания в тело / окружение |
| `body_scan` | последовательное наблюдение тела |
| `progressive_relaxation` | напряжение → расслабление |
| `sensory_grounding` | работа через органы чувств |

### 3.3 movement

| type | Смысл |
|------|--------|
| `mobility` | мягкая мобилизация |
| `stretching` | растяжка |
| `mindful_movement` | движение с вниманием |
| `walking` | осознанная прогулка |
| `shaking_release` | встряхивание / сброс напряжения |

Йога / asana **не type**. Screen format `yoga` — UI-фильтр; tradition-tag (`yoga`) можно повесить на item позже. Не плодить `yoga_for_sleep`.

### 3.4 reflection

| type | Смысл |
|------|--------|
| `journaling` | свободная письменная рефлексия |
| `prompted_reflection` | ответ на конкретный вопрос |
| `gratitude` | благодарность |
| `self_check_in` | проверка текущего состояния |
| `review` | анализ дня / события |

### 3.5 intention

| type | Смысл |
|------|--------|
| `intention_setting` | установка намерения |
| `priority_setting` | определение главного |
| `visualization` | мысленная репетиция |
| `future_self` | образ будущего себя |

### 3.6 behavioral

| type | Смысл |
|------|--------|
| `micro_action` | одно небольшое действие |
| `environment_reset` | изменение пространства |
| `digital_pause` | пауза от устройств |
| `boundary_action` | конкретное действие по границам |
| `connection_action` | действие для контакта с человеком |

### 3.7 creative

| type | Смысл |
|------|--------|
| `free_writing` | свободное письмо |
| `drawing` | рисунок |
| `music` | музыка / слушание как практика |
| `creative_prompt` | небольшое творческое задание |

Screen format `music` ≠ music layer сессии. Type `music` = самостоятельная практика звука. Фон медитации — delivery/session, не type.

### 3.8 ritual

| type | Смысл |
|------|--------|
| `morning_ritual` | начало дня |
| `evening_ritual` | завершение дня |
| `transition_ritual` | переход между состояниями / задачами |
| `release_ritual` | символическое завершение / отпускание |

---

## 4. Meditation — types

| type | Смысл |
|------|--------|
| `breath_awareness` | наблюдение дыхания |
| `body_scan` | внимание по телу |
| `open_awareness` | наблюдение всего возникающего |
| `focused_attention` | концентрация на одном объекте |
| `mindfulness` | наблюдение настоящего момента |
| `grounding` | стабилизация внимания здесь и сейчас |
| `relaxation` | снижение возбуждения |
| `visualization` | направляемые образы |
| `loving_kindness` | доброжелательность к себе / другим |
| `self_compassion` | поддерживающее отношение к себе |
| `acceptance` | наблюдение без борьбы с состоянием |
| `letting_go` | работа с отпусканием |
| `gratitude` | направленное внимание на благодарность |
| `sleep` | переход ко сну *(product exception, см. §0)* |
| `walking_meditation` | медитация в движении |
| `reflection_meditation` | направляемое размышление |
| `silence` | минимально направляемая практика |

`practice.body_scan` ≠ `meditation.body_scan`: первое — телесная последовательность «сделать»; второе — сидячее направленное внимание.

---

## 5. Affirmation — types

Типы = **механизм утверждения**, не жизненная сфера. `career` · `love` · `confidence` · `money` · `family` — не types, а `domain[]` (и то не всегда; `confidence` как цель = `purpose`).

| type | Логика |
|------|--------|
| `self_identity` | «Я могу оставаться собой…» |
| `self_trust` | доверие собственным решениям |
| `self_worth` | ценность не зависит от результата |
| `capability` | способность справляться |
| `permission` | «Мне можно…» |
| `acceptance` | принятие текущего состояния |
| `boundary` | право устанавливать границы |
| `agency` | акцент на собственном выборе |
| `resilience` | способность проходить сложности |
| `growth` | изменение и развитие |
| `release` | разрешение отпустить |
| `grounding` | возвращение к настоящему |
| `compassion` | мягкое отношение к себе |
| `intention` | выбранное направление действия |
| `relationship` | здоровое отношение к другим |

---

## 6. Discipline — types

Добровольное ограничение или обязательство **на период** ради выбранной цели. Цель не хранится в type: `digital_limit` может служить `focus`, `sleep`, `self_control`, `clarity` или `presence`.

| type | Смысл |
|------|--------|
| `abstinence` | временный отказ от чего-либо |
| `reduction` | осознанное сокращение потребления / поведения |
| `digital_limit` | ограничение соцсетей, телефона, контента |
| `consumption_limit` | ограничение покупок, развлечений, импульсивного потребления |
| `food_discipline` | режим или отказ от пищевой привычки **без медицинских обещаний** |
| `speech_discipline` | период без жалоб, сплетен, резких реакций |
| `attention_discipline` | ограничение отвлекающих стимулов |
| `routine_commitment` | обязательство регулярно выполнять выбранное действие |
| `movement_commitment` | ежедневная ходьба, растяжка, тренировка и т. п. |
| `mindfulness_commitment` | регулярная медитация / рефлексия |
| `sleep_discipline` | соблюдение выбранного режима сна |
| `financial_discipline` | временный лимит на необязательные траты |
| `social_discipline` | ограничение / структурирование социальных взаимодействий |
| `comfort_reduction` | добровольный отказ от части удобств |
| `silence` | период молчания или снижения коммуникации |
| `service` | обязательство регулярно делать что-то полезное для других |
| `consistency_challenge` | выполнение действия N дней подряд |

`meditation.silence` = сидячая минимальная практика. `discipline.silence` = правило коммуникации на период.

---

## 7. Purpose

Зачем объект. Массив. Не путать с type и с screen need (need — UX-чип; purpose — retrieval).

| code | Ориентир |
|------|----------|
| `calm` | снизить возбуждение / шум |
| `focus` | собрать внимание |
| `energy` | поднять ресурс |
| `grounding` | здесь и сейчас, опора |
| `clarity` | ясность, различить |
| `confidence` | опора на себя |
| `release` | отпустить |
| `rest` | отдых без обязательного сна |
| `sleep` | переход ко сну |
| `motivation` | сдвинуться |
| `emotional_awareness` | заметить чувство |
| `self_connection` | контакт с собой |
| `connection` | контакт с другим |
| `creativity` | творческий ход |
| `decision_making` | выбор |
| `transition` | смена фазы / задачи |
| `recovery` | восстановиться |
| `discipline` | держать правило |
| `self_control` | удержать импульс |
| `detachment` | не сливаться с содержанием |
| `consistency` | повтор во времени |
| `simplicity` | меньше лишнего |
| `reset` | обнулить паттерн |
| `presence` | присутствие |
| `habit_change` | смена привычки |

Новый purpose = bump этой taxonomy. Не кодировать purpose в имени type.

---

## 8. Domain

Где в жизни. Массив, **nullable / empty allowed**. Не каждая практика привязана к сфере.

`self` · `work` · `relationships` · `love` · `family` · `social` · `body` · `home` · `creativity` · `money` · `growth`

`affirmation.relationship` (механизм) ≠ `domain.relationships` (сфера).

---

## 9. State / Direction

Персонализация Today. Смысловой слой говорит «из какого состояния — куда», библиотека подбирает форму.

### 9.1 input_state

`overstimulated` · `tense` · `restless` · `low_energy` · `scattered` · `stuck` · `emotionally_heavy` · `uncertain` · `disconnected` · `balanced`

### 9.2 direction

`downregulate` · `activate` · `stabilize` · `focus` · `open` · `release` · `reflect` · `connect` · `prepare` · `recover`

Пример:

```text
semantic recommendation
  input_state = scattered
  direction   = stabilize
  purpose     = [grounding, clarity]

retrieval
  content_class = practice
  type          = sensory_grounding
  duration      ≤ 5 min
  context       = work
  → item из базы
```

---

## 10. Content Item — три группы

Machine: [`content_item_contract_v1.json`](../../DATA/reference/practice/content_item_contract_v1.json).  
Library (provisional; sourced fill unfrozen): [`content_library_v1.json`](../../DATA/reference/practice/content_library_v1.json).  
Technique registry (lightweight; `box_breathing` skipped): [`technique_canon_v1.json`](../../DATA/reference/practice/technique_canon_v1.json).

Три группы. Не смешивать identity с retrieval и retrieval с текстом.

### 10.1 identity

`item_id` · `content_class` · `family` (только practice, иначе null) · `type` · `status` (`draft` \| `active` \| `retired`) · `semantic_version` · `seed_cell` (P0 seed-pass: ровно одна need cell; не Meaning, не payload) · `technique_id` (optional, пока registry пуст; обязан существовать в technique canon, если задан)

`item_id` и `technique_id` стабильны. Meaning их не эмитит. Publish (`active`) — только с каноном `review_status = canonical`.

### 10.2 retrieval

То, по чему ищет retrieval. Не пользовательский текст.

`purpose[]` · `domain[]` (may be empty) · `input_state[]` · `direction[]` · `duration` + `duration_unit` · `intensity` · `energy_effect` · `context[]` · `delivery[]` · `contraindications[]`

Discipline additionally (constraints, not prose): `duration_days` · `frequency` · `difficulty` · `failure_policy` · `check_in_frequency`.

`guided` / `unguided` — delivery, не type.

### 10.3 payload

То, что видит человек. Не участвует в matching, кроме отсутствия (пустой payload = item не publishable).

`locales.{lang}.title` · `locales.{lang}.body` · `body_kind` (`instruction` \| `script` \| `affirmation_text` \| `commitment_rule`) · `media_ref?` · `presentation?` (surface labels; не второй retrieval)

Discipline payload extras: `commitment_rule` · `restriction` · `allowed_exceptions[]` · `start_condition` · `completion_condition`.

P0 locale = `ru`. EN — density-pass, не блокер покрытия.

---

## 11. Discipline — дополнительные поля

Обязательны для `content_class = discipline`. У разовой практики их нет.

| field | Смысл |
|-------|--------|
| `duration_days` | длина обязательства |
| `frequency` | `daily` · `weekdays` · `weekly` · `custom` |
| `commitment_rule` | что именно соблюдать (текст правила) |
| `restriction` | чего не делать / какой предел |
| `allowed_exceptions[]` | явные исключения |
| `start_condition` | когда начинается |
| `completion_condition` | что считается выполненным |
| `difficulty` | `low` · `medium` · `high` (жёсткость обязательства, не intensity сессии) |
| `failure_policy` | `restart` · `continue` · `pause` · `flexible` · `strict` |
| `check_in_frequency` | `daily` · `weekly` · `none` |

C1.4 `failure_tolerance` flexible/strict отображается в `failure_policy`. Не хранить цель внутри type.

---

## 12. Карта на существующие слои

Эти слои **не удаляются**. Taxonomy не подменяет их IDs.

### 12.1 Screen needs → purpose / direction (ориентир)

| Screen need ([PRACTICES_SCREEN_V1](./PRACTICES_SCREEN_V1.md) §1) | Ближайшие purpose |
|---|---|
| `calm` | `calm`, иногда `rest` |
| `focus` | `focus`, `clarity` |
| `recover` | `recovery`, `rest` |
| `body` | `grounding`, `self_connection` |
| `understand` | `clarity`, `emotional_awareness` |
| `sleep` | `sleep` |

Need-чип остаётся UX. Retrieval идёт по purpose/state, не по подмене type чипом.

### 12.2 Screen formats → class / family (ориентир)

| Screen format | Куда смотреть |
|---------------|---------------|
| `meditation` | `content_class = meditation` |
| `breath` | `practice` / `breathwork` |
| `yoga` | `practice` / `movement` (+ future `tradition=yoga`) |
| `stretch` | `practice` / `stretching` |
| `visualization` | `meditation.visualization` или `practice.intention.visualization` |
| `affirmation` | `content_class = affirmation` |
| `reflection` | `practice` / `reflection` |
| `music` | `practice.creative.music` |
| `sleep` | items с `purpose=sleep` и/или `meditation.sleep`; format ≠ type |

### 12.3 C1.1 practice definitions

Evolution action types (`breathing`, `journaling`, `meditation`, …) — сигналы прогрессии, не библиотека. При fill можно навесить `compatible_c1_category` на item. Не расширять C1.1 десятками техник.

### 12.4 C1.4 / CONTENT asceticisms

Существующие записи (`no_social_media_evening`, `asceticism.001`, …) — кандидаты в Content Items class `discipline`. Type выводится из механизма (`digital_limit`, `food_discipline`, …), не из цели.

### 12.5 Legacy `CONTENT/practices/practices.json`

Плоские `type: micro | body | observation` — не SoT. Remap при fill. Не добавлять новые legacy types.

---

## 13. Запрещено

- Кодировать цель или сферу в type (`meditation_for_focus`, `affirmation_money`).
- Второй purpose-as-type после `meditation.sleep`.
- Дублировать списки purpose/type на фронте как вторую SoT (FE = отображение и null-защита).
- Выдавать item_id или technique_id из астрологии / CE / day_story. Meaning → state/direction/purpose.
- Писать Content Item из головы LLM как источник техники. Formulation — после Canonical Technique.
- Медицинские, диагностические, «вылечит тревогу/бессонницу» формулировки.
- Обязательные эзотерические акты как условие ritual type.
- Параллельный «канон практик» в корне `docs/` или в screen-файле.

Расширение vocab = bump `semantic_version` этого канона + vocab JSON + tracker. Fill items bump не требует, пока коды те же.

---

## 14. Что дальше

1. **Library fill** — [PRACTICE_LIBRARY_FILL_V1.md](./PRACTICE_LIBRARY_FILL_V1.md). Sourced 15/26. Следующая ячейка: `need.decision_making.focus`. `box_breathing`, `energizing_breath` и `self_trust` = `skipped_for_now`. Не Safety Review V1.1.
2. Coverage-first архитектура (26 cells, type spine) стоит. 133 items остаются `llm_provisional`, пока fill не перепишет ячейку.
3. Retrieval runtime **после** accepted techniques + sourced P0 coverage. Meaning по-прежнему без `item_id` / `technique_id`.
4. Density (P1) и remap legacy `CONTENT/practices/*.json` — только как expressions принятых техник, не вместо provenance.

---

## Changelog

| Дата | Изменение |
|------|-----------|
| 2026-08-26 | pointer: research ladder archived; active fill = [PRACTICE_LIBRARY_FILL_V1](./PRACTICE_LIBRARY_FILL_V1.md); `box_breathing` skipped_for_now |
| 2026-08-26 | pointer: Targeted Safety Shortlist V1 = stop A; next = Targeted Safety Ingest |
| 2026-08-26 | pointer: Safety Review V1 = insufficient_safety; next = owner decides |
| 2026-08-25 | pointer: Normalization V1.1 = normalize_one candidate; next = Safety Review |
| 2026-08-25 | pointer: Targeted Ingest V1 closed; next = Normalization V1.1 |
| 2026-08-25 | pointer: Targeted Shortlist V1 closed; next = targeted ingest → Normalization V1.1 |
| 2026-08-25 | **v1.2** — Canonical Technique слой; item = expression; `technique_id` optional; fill frozen ([PRACTICE_TECHNIQUE_PROVENANCE_V1](./PRACTICE_TECHNIQUE_PROVENANCE_V1.md)) |
| 2026-08-25 | **v1.1** — pipeline Meaning→Need→Retrieval→Library→Item; item = identity/retrieval/payload; fill = coverage-first ([PRACTICE_CONTENT_COVERAGE_V1](./PRACTICE_CONTENT_COVERAGE_V1.md)) |
| 2026-08-25 | v1.0 ACCEPTED — четыре class, locked types, purpose/domain/state/direction, item shape, discipline extras |
