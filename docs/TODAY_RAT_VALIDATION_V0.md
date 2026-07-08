# TODAY_RAT_VALIDATION_V0 — Recognition Ablation Test

**Статус:** `IN_PROGRESS` — pilot n=19, **no sign-off**  
**Версия:** 1.0 (2026-06-23)
**Phase:** 2 active · n=23 · class matrix + **KIP/RRM** (recognition on texts) · **Discovery fork deferred**  
**Pilot:** n=19 · **refuted:** single universal survivor (AR-003)
**Dataset:** [datasets/TODAY_RAT_VALIDATION_V0.json](./datasets/TODAY_RAT_VALIDATION_V0.json)  
**Parent:** [TODAY_INTERNAL_PATTERNS_V0.md](./TODAY_INTERNAL_PATTERNS_V0.md) · [DECISION_RELEVANCE_V1.md](./DECISION_RELEVANCE_V1.md) (C17) · IPL-H7 (RAT)

---

## Platform axis — какие знания заслуживают PIM? *(editorial sign-off 2026-06-23)*

До RAT все вопросы были про **генерацию**: pattern · IPL · Tension Layer · survivor.

**RAT открывает ось выше generation:**

> **Какие знания заслуживают места в PIM?** · **Какие стоит добывать?**

| Слой | Класс | Вопрос |
|------|-------|--------|
| **C10–C17** | модель · lifecycle | **Что хранить?** |
| **KIP / RRM** *(hypothesis · C18 candidate)* | политика инвестирования | **Что добывать?** · **зачем** |

| Канон | Вопрос | Ось |
|-------|--------|-----|
| **[C17](./DECISION_RELEVANCE_V1.md)** | Помогает ли знание **принимать решения**? | Decision Relevance |
| **RAT → RRM** *(hypothesis)* | Помогает ли знание создавать **узнавание** («это про меня»)? | Recognition Relevance |

**Множества не совпадают.** PIM без RRM рискует стать **складом фактов** с высокой decision relevance и нулевой recognition relevance. DRE компенсирует copy'ем — но не может «оживить» atoms, которые **не несут узнавания**.

### Recognition Relevance Map *(RRM — candidate platform artifact)*

**Не для:** генерации текста · выбора pattern · IPL / Object Layer.

**Для:** **отбора знаний** — что собирать, хранить, обновлять в PIM · **ещё до DRE**.

Любой кандидат в PIM — минимум **две независимые оси**:

1. **Decision Relevance** — рекомендации · действия · guidance (C17).
2. **Recognition Relevance** — узнаваемость · персональное попадание · ощущение точности (RRM).

| Knowledge item *(example)* | Decision | Recognition |
|------------------------------|----------|-------------|
| Переоценивает сроки | высокая | высокая |
| Часто перегружается | высокая | высокая |
| Ждёт ответа дольше, чем нужно | средняя | **высокая** |
| Любит работать в тишине | средняя | **низкая** |
| Предпочитает утро вечеру | низкая | низкая |
| Часто откладывает неприятные разговоры | средняя | **высокая** |

**Расхождения осей — самые ценные.** Q4 (low/low): **не собирать** · не только archive.

#### Матрица Decision × Recognition

| Decision | Recognition | Вывод |
|----------|-------------|-------|
| High | High | Приоритет №1 |
| High | Low | Guidance |
| Low | High | Узнавание |
| Low | Low | **Q4** — drop / archive |

#### RRM на типе знания *(не atom)*

| Тип | RRM |
|-----|-----|
| Поведенческие циклы | очень высокая |
| Незавершённости | высокая |
| Повторяющиеся решения | высокая |
| Бытовые предпочтения | низкая |
| Статические факты профиля | очень низкая |

**Acquisition:** `Signal → Knowledge Type → RRM policy → PIM` — см. C17 §0.1 · INTERNAL_PATTERNS §RRM.

**RRM ≠ побочный продукт RAT.** Dependency map = текст · RRM = знания · влияет на **PIM**.

**Открытая гипотеза (AR-005):** RRM может быть **2D** — Recognition vs **Discovery**. Не оптимизировать KIP только под «это про меня» · low-rec / high-disc = retain for LRE.

| | Recognition | Discovery |
|---|-------------|-----------|
| «берёшь больше, чем успеваешь» | very high | medium |
| «откладываешь задачи с неопределённым результатом» | medium | **very high** |

**KIP *(hypothesis)*:** C17 + Recognition + Discovery — три **причины** ценности. RRM = recognition tier only.

#### Temporal asymmetry *(AR-005/006 — не мерить Discovery как Recognition)*

| Ось | Когда | RAT phase 2 |
|-----|-------|-------------|
| Recognition | **T0** · сразу после текста | **in scope** — ablation · editorial |
| Decision | по outcome | PR2+ · Intent Records |
| Discovery | **weeks–months** | **out of scope** RAT-only · fork open |

**Пример:** «избегаешь задач, где не понимаешь критерий успеха» — recognition=medium at read · discovery validated months later.

**Discovery fork deferred** — Watchlist only after PR2; no protocol until ≥50–100 prod Intent Records. См. INTERNAL_PATTERNS §Discovery Watchlist.

### Не связывать RRM с IPL *(пока)*

**Сначала:** коррелируют ли `text_class` · `survivor` · `recognition_mechanism` с **типами знаний**?

**Потом:** dependency map (stack A–E) **и** RRM — два deliverable phase 2:

| Deliverable | Отвечает |
|-------------|----------|
| Class matrix + dependency map | как **текст** создаёт узнавание |
| **RRM** | какие **знания** стоит иметь в PIM для узнавания |

Schema hypothesis: [TODAY_LANGUAGE_CALIBRATION_V0.json](./datasets/TODAY_LANGUAGE_CALIBRATION_V0.json) · `recognition_relevance_map` · [TODAY_RAT_VALIDATION_V0.json](./datasets/TODAY_RAT_VALIDATION_V0.json) · `rrm_hypothesis`.

**Prod:** не добавлять `recognition_relevance` на atom до RRM sign-off (см. C17 §0.1).

### AR-004 — Knowledge Density Illusion

> **Риск:** чем больше фактов о человеке — тем лучше узнавание.

RRM может показать **обратное:** 100 atoms low recognition relevance < 10 high recognition atoms. Это **экономика памяти платформы**, не качество генератора.

| Knowledge item | Decision | Recognition |
|----------------|----------|-------------|
| Любит работать в тишине | medium | **low** |
| Предпочитает утренние встречи | medium | **low** |
| Использует Notion | low | **low** |
| Часто откладывает неприятные разговоры | medium | **high** |
| Склонен брать на себя слишком много | high | **high** |
| Ждёт ответа дольше, чем нужно | medium | **high** |

**C17** оптимизирует качество **решений**. **RRM** — качество **узнавания**. **Пересечение** — necessary, **не sufficient** для acquisition policy.

### Platform memory economics *(post-AR-004 · AR-008)*

| Плоскость | Ось | Вопрос |
|-----------|-----|--------|
| **Value** | C17 | Помогает **решениям**? |
| **Value** | RRM | Помогает **узнаванию**? |
| **Cost** | Acquisition Cost | Сколько стоит **добыть и поддерживать**? |
| **Feasibility** | **Observability** | Можно ли **надёжно извлечь** из поведения? |
| **Process fit** | **Reusability** | **Будет использоваться повторно** — сколькими процессами? |

**Knowledge ROI:** не «полезно ли?», а **стоит ли затрат** при Value ÷ Cost.

| Knowledge | Decision | Recognition | Cost | Observability |
|-----------|----------|-------------|------|---------------|
| Утренние встречи · Notion | low | low | **low** | high |
| Повторяющиеся перегрузы | high | high | medium | **high** → **high ROI** |
| Ждёт ответа · откладывает разговоры | medium | high | **high** | low–medium → **uncertain ROI** |

**Post-n=40 gate *(не спешить с KIP)*:** см. extended sequence в §AR-009 ниже.

**PIM investment policy *(hypothesis)*:** **C17 ∩ RRM ∩ Observability ∩ Reusability** — см. §AR-009.

### AR-009 — Knowledge as Asset Illusion

Повторяющийся паттерн исследования:

scene → good text · anchor → good text · pattern → recognition source · **high ROI → store**

**PIM существует не для хранения ценных знаний.** PIM — для **поддержки будущих процессов**.

| Knowledge | Recognition | ROI | Reusability *(hyp)* | Вывод |
|-----------|-------------|-----|---------------------|-------|
| Перегруз | high | high | **high** (guidance · DRE · planning · …) | **platform knowledge** |
| Работает под музыку | medium | low | **low** | не PIM priority |
| Ждёт ответа дольше нужного | very high | uncertain | **uncertain** (DRE only?) | **не store-by-default** |

**Platform knowledge vs feature knowledge:** один consumer · high ROI · всё равно может быть **feature knowledge**, не инфраструктура PIM.

**Post-n=40 gate *(extended)*:**

1. RRM correlation  
2. Observability map  
3. Knowledge ROI sketch  
4. **Reusability map** — platform vs feature  
5. KIP sign-off  

### Knowledge Type Catalog *(phase 2 · class-level)*

На каждый RRM-кандидат — не только `linked_knowledge_types[]`, но и **`knowledge_type_class[]`**:

| Class | id |
|-------|-----|
| Behavioral Pattern | `behavioral_pattern` |
| Repeated Decision | `repeated_decision` |
| Social Dynamic | `social_dynamic` |
| Work Habit | `work_habit` |
| Preference | `preference` |
| Life Object | `life_object` |
| Emotional Tendency | `emotional_tendency` |
| Recurring Conflict | `recurring_conflict` |

**Гипотеза классов *(не atom-level):***

- Preferences почти никогда не дают узнавание.
- Behavioral Patterns почти всегда дают узнавание.
- Recurring Conflict часто даёт узнавание.
- Life Objects работают только в определённых `text_class`.

**Survivor → class *(hypothesis):***

| Survivor | Knowledge type class |
|----------|----------------------|
| `pattern_form` | Behavioral Pattern |
| `context_bundle` | Social Dynamic + Recurring Conflict |
| `object_frame` | Life Object |
| `life_object` | Life Object |

**Главный вопрос n=40:** какие **классы знаний** чаще всего стоят за survivor — не «кто победил в ablation».

Schema: `knowledge_type_class_catalog` · `survivor_to_knowledge_type_class_hypothesis` · per-case `linked_knowledge_types[]` · `knowledge_type_class[]` in [TODAY_RAT_VALIDATION_V0.json](./datasets/TODAY_RAT_VALIDATION_V0.json).

---

## North star *(переформулирован после pilot)*

**Pilot refuted:** «существует **одна** минимальная единица узнавания» — см. **AR-003**.

**Было (слишком узко):**

> Что является единицей узнавания?

**Стало:**

> **Для каких классов текстов какая единица узнавания доминирует?**

Параллель с anchor count: сначала «больше анкоров → лучше», потом «**тип** анкора, не количество». RAT pilot: не один universal signal — **минимум четыре класса survivor** (~42% — не шум).

---

## Pilot reading *(editorial sign-off 2026-06-23)*

### Четыре конкурирующих механизма *(n=19)*

| `ablation_survivor` | share | Роль |
|---------------------|------:|------|
| `pattern_form` | 58% | узнаваемая закономерность |
| `object_frame` | 16% | рамка выбора («один приоритет») |
| `context_bundle` | 16% | связка time + narrative + pattern |
| `life_object` | 11% | конкретная ситуация / объект |

**58% — не победа IPL.** Если бы 85% pattern — было бы «слишком удобно». Сейчас: **конкурирующие механизмы**.

### cal-018 — критический сигнал

Один из **сильнейших** exemplar проекта → survivor **`context_bundle`**, не pattern · не object.

> Если лучший текст не сводится к pattern/object, **нельзя честно** утверждать: IPL = источник узнавания.

### Candidate outcome *(не roadmap — только если n=40 подтвердит)*

**Узнавание мультимодально.** Stack candidate:

```
PIM
  → Recognition Retrieval
       → Pattern
       → Object
       → Context Bundle
  → DRE
```

**Не** `PIM → IPL → DRE` до RAT aggregate. **Продолжать RAT**, не строить IPL.

### Ожидание на n=40 *(directional bet)*

| Mechanism | expected share |
|-----------|---------------:|
| Pattern-form | 45–60% |
| Context-bundle | 20–30% |
| Object-frame | 10–20% |
| Pure life-object | 5–15% |

---

## Phase 2 — clustering *(active; n=23)*

**Не новая гипотеза.** Кластеризовать три поля, которые впервые есть одновременно:

| Поле | Зачем |
|------|--------|
| `text_class` | класс текста (editorial; может ≠ `core_scene`) |
| `ablation_survivor` | что пережило ablation последним |
| `recognition_mechanism` | **почему** «это про меня» — не score, не pattern id |

### Recognition Mechanism *(на каждый exemplar после RAT)*

> Почему человек говорит «это про меня»?

| Mechanism | Пример |
|-----------|--------|
| `pattern_recognition` | «снова откладываешь отчёт» |
| `object_recognition` | «отчёт» · «один приоритет» · «слот 20 минут» |
| `narrative_recognition` | «перестал ждать → получил ответ» |
| `state_recognition` | «перегруз» · «усталость» · «надо собраться» |

**Mechanism может быть важнее survivor** — survivor = structural outcome; mechanism = psychological why.

**Не добавлять новые архитектурные сущности** — живы только Pattern · Object · Context Bundle · Life Object.

### Deliverable — class matrix *(engineering, not philosophy)*

| Text Class | Dominant Survivor | Dominant Mechanism | Confidence | n |
|------------|-------------------|--------------------|------------|--:|
| `delayed_message` | `context_bundle` | `narrative_recognition` | **high** | 2 |
| `focus` | `object_frame` | `object_recognition` | **high** | 5 |
| `procrastination` | `pattern_form` | `pattern_recognition` | **high** | 2 |
| `overload` | `pattern_form` | `pattern_recognition` | **high** | 3 |
| `postponed_conversation` | mixed | mixed | **low** | 2 |
| `work_execution` | mixed | `object_recognition` | **low** | 2 |

Полная таблица + `cal_ids`: [TODAY_RAT_VALIDATION_V0.json](./datasets/TODAY_RAT_VALIDATION_V0.json) · `phase_2_class_matrix`.

**Приоритет phase 2:**

1. **`delayed_message`** — только 2 в corpus (`core_scene`); нужно 3–5 из api_live · пока 2/2 → `context_bundle` (**high**).
2. **`focus` / work execution** — 5/5 `object_frame` на cal-055–057, 031, 061, 076 → **первый class-specific winner** (**high**).

**North star (engineering):**

> Для какого класса текстов **какой механизм узнавания** работает лучше всего?

**North star (platform · n=40):**

> Какие **классы знаний** дают максимальную отдачу на единицу памяти? *(C17 ∩ RRM)*

**Phase 2 поля на каждый RAT-кейс:** `linked_knowledge_types[]` · `knowledge_type_class[]` · см. JSON `phase_2_entry_fields`.

---

## Процедура

1. **Baseline** `recognition_score` 1–5 на исходнике.
2. **Ablation steps** — убрать один слой, сохраняя объяснение дня где возможно.
3. Если score падает ≥2 пункта — фиксировать `recognition_loss_reason` *(open vocab)*.
4. **`ablation_survivor`** — что пережило удаления **последним** на этом кейсе.

### Loss reason vocabulary *(open — дополнять по мере RAT)*

| id | Когда |
|----|--------|
| `specificity_loss` | стало универсально |
| `emotional_hit_loss` | «правда, но не про меня» |
| `life_object_loss` | abstract label вместо ситуации |
| `temporal_context_loss` | потеря «неделю / вчера / когда уже…» |
| `narrative_loss` | потеря мини-истории (не только время) |
| `causality_loss` | потеря причинной связки |
| `pattern_form_loss` | потеря узнаваемой закономерности *(«отпустил → получил»)* |
| `tension_loss` | остался совет без внутреннего давления |
| `bundle_loss` | распалась связка object+time+pattern |

---

## Pilot case — cal-018 *(эталон RAT)*

**Исходник:** «Кто-то может написать вам именно тогда, когда вы уже решили, что ответа не будет.»

| Step | Ablation | Text | Score | Loss reason |
|------|----------|------|------:|-------------|
| 0 | baseline | *(original)* | **5** | — |
| 1 | temporal / narrative strip | «Кто-то может написать вам сегодня.» | **2** | `temporal_context_loss`, `narrative_loss` |
| 2 | expectation object strip | «Вы можете неожиданно получить то, чего давно ждали.» | **3** | `life_object_loss`, `specificity_loss` |
| 3 | release-decision strip | «Кто-то может написать вам после долгого ожидания.» | **3** | `pattern_form_loss` |

**Survivor:** `context_bundle` — мини-история **«отпустил ожидание → контакт»** (pattern_form внутри bundle, не abstract tension).

**Note:** cal-018 короткий — мало слоёв, поэтому ideal first RAT probe.

---

## Pilot aggregate *(n=19, directional — не gate)*

| `ablation_survivor` | count | share |
|---------------------|------:|------:|
| `pattern_form` | 11 | 58% |
| `object_frame` | 3 | 16% |
| `context_bundle` | 3 | 16% |
| `life_object` / scene | 2 | 11% |

**Loss reasons observed (non-exclusive):** `pattern_form_loss` (8) · `specificity_loss` (7) · `temporal_context_loss` (5) · `life_object_loss` (4) · `narrative_loss` (3) · `emotional_hit_loss` (2) · `causality_loss` (2) · `tension_loss` (1)

### Чтение *(preliminary — superseded by §Pilot reading)*

- **42% non-pattern** — слишком много для шума; конкурирующие механизмы.
- **IPL не подтверждён** pilot'ом (58% ≠ 70–80%).
- **cal-018** → `context_bundle` блокирует «IPL = source of recognition».
- **Stack decision:** BLOCKED · phase 2 = **text-class clustering**.

### Следующий шаг

- RAT **n=30–40** с полем `text_class` · aggregate **per class**, не global winner.
- **Не** IPL Engine · **не** Object Layer · **не** multimodal stack canon до n=40 sign-off.
- PR2 / H5 / H6 — deferred per [TODAY_INTERNAL_PATTERNS_V0](./TODAY_INTERNAL_PATTERNS_V0.md).

---

## AR-003 — False Universal Survivor

| | |
|---|---|
| **ID** | AR-003 |
| **Risk** | Предположить, что все strong texts имеют **одну** минимальную единицу узнавания |
| **Symptom** | «IPL = source of recognition» · single survivor type in architecture |
| **Pilot refutation** | n=19: 58 / 16 / 16 / 11 — four mechanism classes |
| **Mitigation** | Phase 2: class→survivor map · multimodal retrieval **only** if n=40 confirms |

---

## Changelog

| Дата | Изменение |
|------|-----------|
| 2026-06-23 | v1.0 — Reusability axis; AR-009 Knowledge as Asset Illusion; platform vs feature knowledge; 4-axis policy |
| 2026-06-23 | v0.9 — Knowledge ROI; Acquisition Cost; Observability; AR-008; post-n=40 gate before KIP |
| 2026-06-23 | v0.9 — Discovery Watchlist; fork open until prod IR; no protocol |
| 2026-06-23 | v0.8 — KIP framing; temporal asymmetry; Discovery fork; AR-006; RAT scope = recognition only |
| 2026-06-23 | v0.6 — Discovery relevance hypothesis; AR-005; 3-axis KIP; Rec×Disc matrix |
| 2026-06-23 | v0.4 — platform axis; RRM vs C17; knowledge curation |
| 2026-06-23 | v0.3 — phase 2 active; recognition_mechanism; class matrix n=23 |
