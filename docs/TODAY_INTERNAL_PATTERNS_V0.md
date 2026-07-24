# TODAY_INTERNAL_PATTERNS_V0

**Статус:** `CALIBRATION_HYPOTHESIS` — не gate, не код.  
**Версия:** 3.1 (2026-06-23)  
**Родитель:** [TODAY_ANCHOR_TYPES_V0.md](./TODAY_ANCHOR_TYPES_V0.md) · AT-006 Internal Anchor  
**Dataset:** [datasets/TODAY_LANGUAGE_CALIBRATION_V0.json](./datasets/TODAY_LANGUAGE_CALIBRATION_V0.json) · поле `internal_pattern_ids[]`

**Связь:** [TODAY_LANGUAGE_CALIBRATION_V0.md](today-language/TODAY_LANGUAGE_CALIBRATION_V0.md) · [DECISION_RELEVANCE_V1.md](./DECISION_RELEVANCE_V1.md) (C17) · PIM: [INTENT_MODEL_V1.md](./INTENT_MODEL_V1.md)

**Не путать с PIM:** «Internal patterns» — **editorial taxonomy** повторяющихся объяснительных конструкций. **Не** доказанный platform layer «IPL». См. § «Что доказано vs что нет».

---

## Зачем (пауза на batch_5 и TL-1)

Dataset expansion **PAUSED**. Риск: построить вторую «красивую теорию» после refuted count-gate.

Данные говорят **не**:

> внутренний паттерн важнее всего.

Данные говорят **уже сейчас**:

> **некоторые** внутренние паттерны — мощные источники узнавания; **другие** AT-006 — generic и слабые.

Это разные утверждения.

---

## Что доказано vs что нет

### Факт *(editorial, corpus)*

Хорошие тексты **систематически группируются** вокруг повторяющихся **объяснительных конструкций** (Class R > Class G; clustering в calibration).

### Не доказано *(важнее)*

Из clustering **не следует**, что узнавание — **свойство одного слоя**. Варианты A–D предполагают «единицу»; это **ещё не доказано**.

**Возможен variant E:** узнавание через **пересечение** object + pattern + tension — bundle, не отдельный слой.

**Нет доказательств** IPL как platform layer. Не «IPL roadmap».

### Project focus *(не purge из docs — purge из мышления команды)*

| Есть | Нет |
|------|-----|
| наблюдение о кластерах | доказательство Pattern Layer |
| каталог IP-001…008 | IPL как слой системы |
| полезная **редакторская таксономия** | platform layer «IPL» |

**До dependency map:** в sprint/planning **не** «IPL», **не** Pattern Selection Engine — только **RAT + taxonomy**. Имена в docs — historical.

---

## Стоп-условие — наблюдаемое явление vs правдоподобная теория

Повторяющийся паттерн последних недель: выигрыш — не от нового слоя, а от **вовремя остановиться** и спросить:

> **У нас уже есть наблюдаемое явление — или пока только правдоподобная теория?**

| Тема | Ошибка, которую удалось избежать |
|------|----------------------------------|
| **AP/SP** | Scene Engine **до** проверки Anchor |
| **PIM** | traits **без** Evidence / Contradiction / Temporal |
| **PR2** | Goal UI **до** Intent Model |
| **IPL** | Pattern Engine **до** RAT |
| **Discovery** | Validation Layer **до** появления данных |

**Правило (data-first):** сначала **источник данных и наблюдаемая реальность**, потом модель над ней. См. [DATA_ORIGINATION_AND_LIFECYCLE.md](./DATA_ORIGINATION_AND_LIFECYCLE.md).

### Что уже наблюдаемо vs что ещё нет *(2026-06-23)*

| Объект | Статус | Инструмент |
|--------|--------|------------|
| **Recognition** | наблюдается | editorial corpus · RAT |
| **Dependency map** | исследуется | существующие тексты |
| **RRM** | калибруется editorially | RAT phase 2 |
| **Discovery** | **не наблюдается** | нет prod Intent Records · циклов · contradiction traces · temporal evolution |

**Discovery до PR2 = гипотеза.** **После PR2 = потенциально измеримый объект.** PR2 создаёт не только write-path — PR2 **впервые создаёт возможность наблюдать Discovery как явление**.

### Асимметрия стоимости ошибки

| Действие | Стоимость |
|----------|-----------|
| **Подождать** с Discovery-архитектурой | почти нулевая |
| **Ошибочно канонизировать** Discovery как отдельную ось KIP | месяцы лишней системы |

**Fork B upside:** если через 3–6 месяцев Discovery = delayed validation (C14→C15→C16), **не понадобится** Discovery Relevance Map · Discovery tiers · Discovery ranking · Discovery policy — всё останется частью жизненного цикла знания.

### Текущее состояние *(согласовано)*

| Track | Роль |
|-------|------|
| **PR2** | следующий **инженерный** шаг — создать явление |
| **RAT** | следующий **исследовательский** шаг — Recognition |
| **Discovery** | **наблюдение** (Watchlist), не проектирование |

**Порядок:** PR2 → RAT ∥ Watchlist → месяцы истории → fork review (≥50–100 IR).

### Phenomenon Before Analysis *(AR-011)*

Два **разных** риска — не один:

| Риск | Статус *(2026-06-23)* |
|------|------------------------|
| Построить **неправильный** слой | хорошо контролируется (PR1 · AR-004 · AR-010 · C18 freeze) |
| **Не получить** наблюдаемые данные | почти не контролируется |

**AR-010** спрашивает: «есть ли уже явление?» **AR-011** фиксирует **фазу**: до PR2 TodayFlow не в **knowledge extraction**, а в **phenomenon creation** — система ещё не извлекает закономерности; она создаёт объект наблюдения.

**HostFlow-аналог:** нет карточек кандидата → нет воронки найма. Нет завершённых Intent Records → нет Discovery / IPL / Pattern / KIP review.

**Канонический объект явления:** не PIM, не Trait — **завершённый lifecycle Intent Record** (Goal → guidance → outcome → при необходимости reflection → следующий цикл).

**Признаки, что явление появилось** *(не до, а после)*:

1. существует канонический объект;
2. объект **создаётся пользователями** в prod;
3. объект появляется **регулярно**;
4. накоплено **≥50–100** экземпляров *(fork review)*;
5. возможны **повторные** наблюдения одного паттерна (contradiction traces · longitudinal цепочки).

**Inverse trap:** архитектурная осторожность начинает **конкурировать** со скоростью появления фактов — откладываем не преждевременный слой, а **наблюдаемую реальность**.

**ROI знаний:** imperfect PR2 в prod (2–3 нед.) > ещё месяц архитектуры без write-path. **AR-009** — *что хранить*, когда сигнал уже есть; **AR-011** — *не откладывать* prod и write-path ради новых гипотез.

> **AR-011 не делает Intent Records целью продукта.** Явление = **ежедневная привычка**, ради которой человек возвращается. Intent Records — **побочный продукт** этого использования. См. **AR-012**.

---

## Platform Layer Gate — когда разрешён новый слой *(C18+)*

> За последние месяцы сформировался не только набор канонов, а **критерий**, когда вообще разрешено создавать новый **платформенный** слой. Сильнее, чем §Стоп-условие для одной фичи — **анти-паттерн архитектурного фантазирования**.

### История — что остановило преждевременную реализацию

| Слой | Gate |
|------|------|
| **Anchors** | калибровка AP/SP |
| **PIM** | Evidence → Contradiction → Temporal |
| **Intent Model** | PR2 pre-flight |
| **IPL** | RAT / RPT |
| **Discovery** | observable phenomenon gate |

**Итог во всех случаях:**

> **Новый слой — только после устойчивого наблюдаемого явления, которое невозможно объяснить существующими слоями.**

### Типичная ошибка сложных продуктов

```
1. Замечаем интересную гипотезу
2. Даём ей название
3. Создаём Engine
4. Создаём Registry
5. Создаём Policy
6. Через полгода — явление не существовало как отдельная сущность
```

**Удалось остановиться до шага 3** — AP/SP · PIM · PR2 · IPL · Discovery.

### Gate question для любого C18+

> **Какое наблюдаемое явление не может быть объяснено текущим стеком?**

Если ответа **нет** → новый слой **не нужен**.

### Порядок построения *(HostFlow → TodayFlow)*

| HostFlow | TodayFlow |
|----------|-----------|
| source of truth | **сигналы** |
| observable processes | **повторяемое явление** |
| contracts | **измерение** |
| consumers | **модель** → **только потом** платформенный слой |

См. [DATA_ORIGINATION_AND_LIFECYCLE.md](./DATA_ORIGINATION_AND_LIFECYCLE.md) · [PIM_PR_GATE_V1.md](pim/PIM_PR_GATE_V1.md) C18 freeze.

### Что сейчас — реальность vs гипотеза *(2026-06-23)*

| Явление | Статус | Работа |
|---------|--------|--------|
| **Intent cycle** | наблюдаемо *(post-PR2)* | PR2 — **реальность** |
| **Recognition** | наблюдаемо | RAT — **реальность** |
| **Discovery layer** | **не наблюдаемо** | Watchlist — **гипотеза**, не Engine |

**C18 freeze** — не просто ограничение, а **механизм защиты архитектуры** от преждевременного усложнения.

### Когда появится основание для нового слоя

Устойчивый класс событий, который **одновременно**:

- **не** объясняется C14–C16 (или текущим стеком между PIM и DRE);
- **регулярно** влияет на ценность PIM;
- **требует** отдельной политики — не сводится к lifecycle существующих контрактов.

До этого — Watchlist · fork review · **без** Engine / Registry / Policy.

---

## PR2 ∥ RAT — два типа знания *(параллельно, не взаимозаменяемо)*

| Track | Что доказывает | Вопрос |
|-------|----------------|--------|
| **PR2** | PIM **способен накапливать** качественные сигналы | write-path · causal chain · audit |
| **RAT** | **Какие** сигналы вообще имеют смысл **объяснять** пользователю | узнавание · generation · curation |

**Это не одно и то же.** PR2 без RAT → риск **склада фактов**. RAT без PR2 → нет write-path для проверенных знаний.

### Два артефакта RAT phase 2 *(оба важнее stack A–E)*

| Артефакт | Отвечает | Может оказаться ценнее variant B/C/D/E |
|----------|----------|----------------------------------------|
| **Dependency map** | какой **компонент текста** несёт узнавание | stack между PIM и DRE |
| **Recognition Relevance Map (RRM)** | компонент **KIP** — recognition tier | см. §KIP |
| **Discovery** *(hyp)* | второй компонент KIP · или lifecycle *(fork)* | см. §KIP · §Discovery fork |

**RRM → KIP:** не одна шкала, а **политика инвестирования** — несколько **независимых** измерений:

| Плоскость | Ось | Вопрос | Статус |
|-----------|-----|--------|--------|
| **Value** | **C17 Decision** | Помогает **решениям**? | ACCEPTED |
| **Value** | **Recognition** | Помогает **узнаванию** («это про меня»)? | RAT · hypothesis |
| **Value** | **Discovery** | Помогает **новому пониманию** / ↓ неопределённости? | **open fork** · AR-005/006 |
| **Cost** | **Acquisition Cost** | Сколько стоит **добыть и поддерживать**? | hypothesis · post-AR-004 |
| **Feasibility** | **Observability** | Можно ли **надёжно извлечь** из поведения? | hypothesis · **post-n=40 gate** |
| **Process fit** | **Reusability** | **Сколько процессов** смогут это использовать? | hypothesis · **post-n=40 gate** · AR-009 |

**Knowledge ROI *(hypothesis)*:** не «полезно ли знание?», а **стоит ли затрат** на получение и поддержание при учёте Value ÷ Cost.

**PIM investment policy *(hypothesis)*:** **C17 ∩ RRM ∩ Observability ∩ Reusability** — не «high ROI → store». Discovery добавляется после fork; Cost входит в **ROI ranking**, не заменяет Observability или Reusability.

**PIM ≠ vault ценных знаний.** PIM существует для **поддержки будущих процессов** — см. **AR-009** (Knowledge as Asset Illusion).

**Не побочный продукт RAT.** Два разных вопроса:

| Deliverable | Вопрос |
|-------------|--------|
| **Dependency map** | **Из чего состоит** узнавание в тексте? |
| **RRM** | **Какие знания накапливать**, чтобы узнавание вообще было возможно? |

**Гипотеза RRM:** ~80% сигналов, которые PIM *может* хранить, имеют **низкую recognition relevance** — часть **не стоит добывать**, не только «не показывать в DRE».

**RAT → knowledge value:** RAT перестаёт быть только про текст; phase 2 проверяет, **коррелируют ли** survivor-механизмы с типами знаний для RRM. **Не** связывать RRM с IPL / Pattern / Object Layer до этой корреляции.

---

## North star — источник узнавания *(вопрос уровня PIM)*

**Перелом (аналог PIM):** архитектура вытекла из «**что источник истины о человеке?**»  
**TodayFlow сейчас:** «**какой вклад в узнавание даёт каждый компонент?**» — **не** «Pattern vs Tension».

Это **сильнее бинарного выбора:** tension · pattern · object могут **все существовать** и **ни один** не быть главным источником.

**Цель phase 2:** **dependency map** + **Recognition Relevance Map** — не «найти stack» заранее.

### C17 vs KIP — хранение vs добыча *(candidate layer после C10–C17)*

| | **C10–C17** *(ACCEPTED)* | **KIP / RRM** *(hypothesis · C18 candidate · freeze)* |
|---|---------------------------|------------------------------------------------------|
| **Класс** | модель данных · жизненный цикл сущностей | **политика инвестирования** в знания |
| **Вопрос PIM** | **Что стоит хранить?** | **Что вообще стоит добывать?** · **зачем** (decision · recognition · discovery) |
| **Уровень** | atom · evidence · relevance tier | **тип знания** *(hyp)* → policy |
| **Freeze** | в коде / PR gate | **не канонизировать** до RAT sign-off + Discovery fork |

**Тонкая, но фундаментальная разница.** Без RRM: «может пригодиться» → через 2–3 года PIM = **шумный склад сигналов**.

**RRM влияет не на DRE/IPL**, а на **эволюцию PIM** · acquisition · training corpus · archive.

### Матрица curation *(Decision × Recognition)*

| Decision relevance | Recognition relevance | Вывод |
|--------------------|----------------------|-------|
| **High** | **High** | **Приоритет №1** — acquire · retain · slice |
| **High** | Low | Полезно для **guidance** · weak для «это про меня» |
| Low | **High** | Полезно для **узнавания** · weak для решений |
| **Low** | **Low** | **Q4:** archive · **или не собирать вообще** |

**Q4 особенно важен:** часть сигналов не должна становиться долгоживущим знанием **независимо от confidence**.

### Открытая гипотеза — RRM может быть **двумерной** *(Recognition vs Discovery)*

> **Риск AR-005:** оптимизировать KIP только под «**это про меня**» → отфильтровать знания с **низким recognition**, но **высоким discovery** — источник сильнейших инсайтов через месяцы.

| Тип | Вопрос | Пользователь | PIM |
|-----|--------|--------------|-----|
| **Recognition relevance** | Помогает **узнать себя**? | чувство попадания · доверие | atoms для copy / trust |
| **Discovery relevance** | Помогает **узнать о себе новое**? | новое понимание | новое знание · снижение неопределённости |

**North star TodayFlow:** цикл помогает человеку **и/или** уменьшает неопределённость модели — **две цели**, не одна.

#### Примеры *(editorial — проверить в RAT)*

| Формулировка | Recognition | Discovery |
|--------------|-------------|-----------|
| «Ты часто берёшь на себя больше, чем успеваешь» | **very high** | medium *(часто уже знает)* |
| «Ты откладываешь не сложные задачи, а задачи с **неопределённым результатом**» | medium | **very high** |

Второй — меньше «вау, это я», но **больше ценности** для модели и развития пользователя.

#### Матрица Recognition × Discovery *(hypothesis)*

| Recognition | Discovery | Ценность |
|-------------|-----------|----------|
| High | High | **Редкие золотые сигналы** |
| High | Low | **Узнавание** · trust copy |
| Low | High | **Обучение** · model insight · retain for LRE |
| Low | Low | **Шум** · Q4 drop |

#### Knowledge Investment Policy *(KIP — candidate C18 · не RRM-only)*

> **KIP** = политика: **какие знания добывать · хранить · показывать** — по **независимым причинам ценности**, не одному score.

RRM *(recognition map)* — **часть** KIP, не весь KIP. Discovery — **не** «третья колонка по тем же правилам», пока не закрыт fork ниже.

#### Временная асимметрия метрик *(AR-005/006)*

| Ось | Когда измеряется | Источник сигнала |
|-----|------------------|------------------|
| **Recognition** | **сразу** после текста | immediate response · RAT · editorial |
| **Decision** | по **результату** действия | outcome · goal · guidance |
| **Discovery** | **через время** (недели–месяцы) | longitudinal validation *(hyp)* |

**Discovery = отложенная валидация** *(hypothesis)* — нельзя надёжно мерить тем же RAT-scoring, что Recognition.

**Пример:**

> «Ты не избегаешь сложных задач. Ты избегаешь задач, где не понимаешь **критерий успеха**.»

| Момент | Recognition | Discovery |
|--------|-------------|-----------|
| При чтении | medium | **непонятно** |
| Через 3 месяца | — | «чёрт, это была моя проблема» |

#### Как мерить Discovery *(hypothesis — не RAT editorial)*

| Инструмент | Подходит для |
|------------|--------------|
| «это про меня» · RAT ablation | **Recognition only** |
| Повторное упоминание пользователем | Discovery |
| Инсайт в последующих **Intent Records** / решениях | Discovery |
| ↓ неопределённость в PIM · новые high-confidence atoms | Discovery |
| Outcome по цели | Decision |

**Не строить Discovery Relevance Map** по правилам Recognition до выбора инструмента.

#### Скрытый класс: low / low / high *(looks like noise)*

| Decision | Recognition | Discovery |
|----------|-------------|-----------|
| Low | Low | **High** |

На первый взгляд — **похоже на Q4** (low decision + low recognition). Может быть **источник сильнейших долгосрочных инсайтов**. KIP не должен drop без longitudinal check *(AR-005/006)*.

#### Discovery fork *(открыт — до prod Intent Records + longitudinal history)*

> **Решение (2026-06-23):** не строить **Discovery Validation Protocol** и **не** проектировать Discovery Engine до появления реальных Intent Records в проде. Аналог C10–C17: без write-path нельзя знать, какие сигналы возникают, как часто, что противоречит, что знание vs шум.

**Сейчас:** только **Discovery Watchlist** — наблюдение, не архитектура · без интерпретации. См. §Discovery Watchlist · [PR2_PREFLIGHT.md](./archive/PR2_PREFLIGHT.md) §14.

| Fork A | Fork B |
|--------|--------|
| Discovery = **отдельная relevance-ось** KIP (3D) | Discovery = **delayed validation** · lifecycle **C14–C16**, не RRM |
| **Признаки** *(post data)*: high-Discovery knowledge types **стабильно отличаются** от high-Recognition; separable tiers независимо от Recognition | **Признаки** *(post data)*: гипотеза ценна только после **2–5 циклов**; коррелирует с temporal evolution · contradiction resolution · confidence growth |
| Артефакт *(если подтвердится)*: Discovery tier в KIP | Артефакт *(если подтвердится)*: `discovery_validated_at` · evidence chain |

**Порог для fork review** *(не раньше)*: ≥50–100 **завершённых** Intent Records · несколько недель истории · первые **contradiction events**.

**Не канонизировать** fork A **и** не отбрасывать fork B — до review на реальных траекториях Goal → Behavior → Outcome → Reflection → Next Goal.

#### Discovery Watchlist *(observation only — не протокол · не engine)*

Для каждого **потенциального инсайта** — только сбор материала, **без scoring и без tier assignment**:

| Поле | Назначение |
|------|------------|
| `first_seen_at` | когда впервые зафиксирован |
| `source_intent_record_ids[]` | из каких Intent Records происходит |
| `source_discovery_answers[]` | ответы на discovery questions *(если есть)* |
| `reappeared_count` | сколько раз снова всплыл в цикле |
| `user_self_reference_count` | явные self-reference пользователя |
| `linked_future_goals_count` | связанные последующие цели |
| `linked_future_outcomes_count` | связанные outcomes |

**Не делать сейчас:** Discovery Validation Protocol · Discovery Engine · `discovery_relevance` prod field · editorial Discovery map.

**Главный дефицит — данные, не теория.** PR2 создаёт поток и **впервые делает Discovery наблюдаемым** — см. §Стоп-условие.

---

### C17 на atom · RRM на тип знания *(hypothesis)*

| Тип знания | Recognition *(hyp)* | Discovery *(hyp)* |
|------------|---------------------|-------------------|
| Поведенческие циклы (overcommitment) | **очень высокая** | medium |
| Ambiguity / неопределённый outcome | medium | **очень высокая** |
| Незавершённости | высокая | high |
| Повторяющиеся решения | высокая | medium–high |
| Бытовые предпочтения | низкая | low |
| Статические факты профиля | **очень низкая** | very low |

Atom наследует tier от **knowledge type** + editorial override post-RAT.

### Acquisition path *(hypothesis — не prod)*

```
Signal
  → Candidate Knowledge Type
  → Value tiers (C17 + recognition + discovery)
  → Feasibility (observability) + Process fit (reusability) + Cost (acquisition)
  → Knowledge ROI ranking
  → KIP write (or drop · or feature-scoped cache)
```

**Не:** `Signal → PIM` по confidence alone.  
**Не:** `RRM high → acquire` без observability check *(AR-008)*.  
**Не:** `high ROI → store` без reusability check *(AR-009)*.

### Training corpus gate *(future own model)*

Atom в training set только если одновременно:

1. **C14–C16** — достаточная доказательность  
2. **C17** — decision relevance  
3. **Recognition** *(hyp)* — попадание · trust  
4. **Discovery** *(hyp)* — новое знание · model learning  

Не «всё, что известно» — то, что влияет на **решения**, **узнавание** или **открытие нового**.

---

> **Что является источником узнавания?**

Pilot n=19 refuted одну universal unit (AR-003). Phase 2: dependency map · class matrix · **KIP/RRM** (recognition on texts) · **Discovery fork deferred** (longitudinal post-PR2).

Это **не** исследование tension · **не** «какой текст лучше» · **не** DRE tuning.

### Пример variant E *(intersection, не слой)*

| Формулировка | Узнавание |
|--------------|-----------|
| `overload_pressure` | ❌ не работает |
| `overcommitment` / `deferred_closure` | △ не идеально |
| «Ты продолжаешь держать открытым **разговор**, который давно можно было завершить» | ✅ работает |

Одновременно: **tension** = unresolved pressure · **pattern** = deferred closure · **object** = conversation.  
Убрать **любой** компонент — узнавание может резко упасть.

---

## Recognition Ablation Test *(RAT — единственный активный research track)*

> **Не тест H7 / tension.** **Процедура последовательного удаления** — как AP/SP нашли anchor: не доказывали напрямую, а **убирали уровни** и смотрели, где ломается качество.

**Pilot dataset:** [TODAY_RAT_VALIDATION_V0.md](./TODAY_RAT_VALIDATION_V0.md) · n=19 · cal-018 эталон · **no sign-off**

**Вопрос RAT:** **что остаётся последним**, когда strong text разбирают на части? *(не только «score упал» — фиксировать **почему**)*

### Ablation ladder *(на каждый strong case)*

```
Исходник (recognition_score baseline)
    ↓ убрать object
    ↓ убрать pattern
    ↓ убрать tension
    ↓ заменить соседним pattern (same tension_id)
    ↓ заменить соседним tension
```

На **каждом** шаге: score 1–5 · если упало — `recognition_loss_reason`.

| # | Step | Что делаем |
|---|------|------------|
| 0 | **Baseline** | исходный keep/exemplar |
| 1 | **Object strip** | abstract label вместо «тот разговор / отчёт» |
| 2 | **Pattern strip** | убрать форму проявления → tension-only или generic |
| 3 | **Tension strip** | убрать давление → нейтральное описание |
| 4 | **Neighbor pattern swap** | A→B, same tension, объяснение дня фиксировано |
| 5 | **Neighbor tension swap** | tension cluster B, pattern/object по возможности fixed |

### Aggregate output — dependency map *(n=30–40)*

**Не** «H7 supported/refuted» · **не** global winner · **вклад каждого компонента:**

| Компонент | Вклад в recognition *(example)* | Интерпретация |
|-----------|----------------------------------|---------------|
| Object | **45%** | доминирует, но не монополия |
| Pattern | 35% | существует · не главный |
| Tension | 15% | существует · не главный |
| Остальное | 5% | context · narrative · time |

Тогда **одновременно верны:** tension существует · pattern существует · **ни один** не единственный источник → variant **E** или multimodal retrieval *(см. AR-003 pilot)*.

Pilot n=19 уже refuted **одну** universal unit (AR-003). Phase 2: **% contribution map** + `text_class` → dominant mechanism.

**Stack A–E — только после map + RRM**, не до.

### Recognition Relevance Map *(RRM — candidate Knowledge Investment Policy)*

> **Candidate architectural layer** после C10–C17 · **не ACCEPTED** · **C18 freeze** до RAT sign-off + код столкнулся с C17.

**Цель:** не дать PIM стать складом фактов. **Не lens engine** — **политика добычи и retention**.

| RRM отвечает | Dependency map отвечает |
|--------------|-------------------------|
| какие **знания** накапливать | из чего **текст** создаёт узнавание |

Schema: [TODAY_LANGUAGE_CALIBRATION_V0.json](./datasets/TODAY_LANGUAGE_CALIBRATION_V0.json) · `recognition_relevance_map` · [DECISION_RELEVANCE_V1.md](./DECISION_RELEVANCE_V1.md) §0.1.

**Связь с C17:** Decision + Recognition + Discovery *(hyp)* · Q4 low/low/low = drop · **не** отсекать low-recognition / high-discovery без проверки (AR-005).

**Риск без RRM:** lens-engine или DRE поверх atoms, которые **не стоило добывать**.

### Knowledge Type Catalog *(phase 2 · class-level RRM)*

Проблема может быть не в конкретном atom, а в **классе знания** — см. **AR-004** (Knowledge Density Illusion).

| Class | id | Recognition *(hyp)* |
|-------|-----|---------------------|
| Behavioral Pattern | `behavioral_pattern` | **high** |
| Repeated Decision | `repeated_decision` | medium–high |
| Social Dynamic | `social_dynamic` | medium–high |
| Work Habit | `work_habit` | low |
| Preference | `preference` | **low** |
| Life Object | `life_object` | class-dependent *(text_class)* |
| Emotional Tendency | `emotional_tendency` | medium |
| Recurring Conflict | `recurring_conflict` | **high** |

**Survivor → class *(hypothesis · n=40):***

| Survivor | Knowledge type class |
|----------|----------------------|
| `pattern_form` | Behavioral Pattern |
| `context_bundle` | Social Dynamic + Recurring Conflict |
| `object_frame` | Life Object |
| `life_object` | Life Object |

**Главный вопрос n=40:** не «какой survivor победил», а **какие классы знаний чаще всего стоят за survivor**. Если связь устойчива — RRM = **карта того, что добывать в PIM**, не рейтинг отдельных atoms.

**C17 ∩ RRM:** пересечение двух карт value → приоритет №1 atoms · Q4 (low decision + low recognition) → **не добывать**.

**AR-004 → memory economics:** после density illusion следующий шаг — **Acquisition Cost** + **Knowledge Observability**. **Не** превращать RRM в acquisition policy сразу после n=40 — сначала observability map по классам знаний.

#### Knowledge ROI *(editorial examples · hypothesis)*

| Knowledge | Decision | Recognition | Acq. cost | Observability | ROI *(hyp)* |
|-----------|----------|-------------|-----------|---------------|-------------|
| Повторяющиеся перегрузы | high | high | **medium** | **high** | **high** |
| Любит работать в тишине | medium | low | low | high | **low** |
| Утренние встречи · Notion | low | low | **low** | high | **low** |
| Откладывает неприятные разговоры | medium | high | **high** | medium | **uncertain** |
| Ждёт ответа дольше нужного | medium | high | **high** | **low–medium** | **uncertain** |
| Берёт лишние обязательства | high | high | **high** | medium | **uncertain** |

**High recognition + high cost** — ловушка «собирать всё ценное для узнавания» без учёта месяцев наблюдения и длинной истории сигналов — см. **AR-008**.

#### Knowledge Observability *(post-n=40 gate)*

> Насколько данный **класс знаний** можно надёжно извлечь из поведения пользователя?

**Риск:** RRM вокруг знаний, которые **теоретически прекрасны**, но **практически почти недоступны** (social dynamics · latent avoidance · long-horizon patterns).

#### Knowledge Reusability *(post-n=40 gate · AR-009)*

> **Сколько разных процессов** способны использовать это знание?

**Не Value · не Cost · не Observability.** Ответ на вопрос: **где и когда** знание будет использоваться?

| Knowledge | Reusability *(hyp)* | Consumers *(hyp)* |
|-----------|---------------------|-------------------|
| Перегруз | **high** | guidance · DRE · reflection · planning · prioritization · retrieval |
| Любит работать под музыку | **low** | почти нигде |
| Ждёт ответа дольше нужного | **uncertain** | DRE only? · или planning · decision · reflection? |

**Platform knowledge vs feature knowledge:** high recognition + high observability + good ROI, но **один consumer** (например только DRE) → **feature knowledge**, не инфраструктура PIM.

**Порядок после n=40:**

1. RRM correlation (survivor → knowledge type class)  
2. **Observability map** по классам  
3. Knowledge ROI sketch (Value × Observability ÷ Cost)  
4. **Reusability map** — platform vs feature knowledge  
5. **Только потом** KIP / acquisition policy sign-off  

---

### `recognition_loss_reason` *(если score упал)*

| reason | Сигнал |
|--------|--------|
| `life_object_loss` | abstract label · «правда, но не про меня» |
| `pattern_form_loss` | tension-only · generic internal |
| `tension_loss` | нейтральное описание без давления |
| `bundle_loss` | упало только при удалении **второго** компонента → **variant E** |
| `specificity_loss` | стало универсально |
| `temporal_context_loss` | без «неделю/вчера» |
| `narrative_loss` | потеря мини-истории *(не только время)* |
| `emotional_hit_loss` | «правда, но не про меня» |
| `causality_loss` | без причинной связи |

**Vocab open** — pilot добавил `pattern_form_loss`, `narrative_loss`; новые id по мере RAT. См. [TODAY_RAT_VALIDATION_V0.json](./datasets/TODAY_RAT_VALIDATION_V0.json) `loss_reason_vocab`.

**Ключевой критерий (AR-001):** потеря **узнавания** при сохранении **объяснения**.

### Параллель AP/SP — Pattern как Scene *(RAT защищает)*

См. §Стоп-условие — общий паттерн «слой до явления».

| Ошибка AP/SP | Та же ошибка сейчас |
|--------------|---------------------|
| 1. Хорошие тексты **содержат сцены** | 1. Хорошие тексты **содержат pattern** |
| 2. Построить **Scene Engine** | 2. Построить **Pattern Selection Engine** |
| 3. Сцена — лишь **носитель Anchor** | 3. Pattern — лишь **носитель** object / bundle / context |

**RAT** = ablation как при поиске anchor: **убираем уровни**, смотрим где ломается — **до** engine investment.

---

## Конкурирующие stacks *(A–E — RAT выберет; все не доказаны)*

| | Stack | Утверждение |
|---|-------|-------------|
| **A** | `PIM → DRE` | Промежуточные слои лишни |
| **B** | `PIM → Pattern → DRE` | Pattern = единица узнавания |
| **C** | `PIM → Tension → Pattern → DRE` | Tension объясняет · pattern персонализирует |
| **D** | `PIM → Object → … → DRE` | Object первичен · pattern/tension производны |
| **E** | `PIM → (Object + Pattern + Tension bundle) → DRE` | **Узнавание = пересечение** · не один слой |

**Prod сейчас:** implicit **A**. **E** — наиболее правдоподобен для postponed-conversation кейсов, **не доказан**.

**Не строить** stack до **dependency map**. Engine names — outcomes phase 3+, не roadmap.

### Четыре сценария *(после map)*

| # | Map reads | Инвестиция | Stack |
|---|-----------|------------|-------|
| **1** | Object ≫ Pattern > Tension | Object Retrieval из PIM | **D** |
| **2** | Pattern ≫ Object > Tension | H6 · IPL **кандидат** platform layer | **B/C** |
| **3** | Pattern ≈ Object ≈ Tension | Bundle composer | **E** |
| **4** | Flat / no dominant | Context · anchor-like 2nd order *(pilot: cal-018)* | **A** / multimodal |

---

## HYPOTHESIS H3 — Psychological Recognition *(TENTATIVE, narrowed)*

**Было (слишком широко):** «главный источник узнавания — внутренние паттерны».

**Сейчас:** AT-006 **может** нести узнавание — но **не любой** AT-006. Внутри AT-006 уже два класса (см. ниже).

Архитектура `internal → scene → action` — **гипотеза генерации**, не доказанный канон. Проверять через H4, не расширять bulk dataset.

---

## HYPOTHESIS H4 — Observable Pattern *(SUPPORTED — editorial; limited as data model)*

> Class **R** patterns (наблюдаемые без интерпретации) стабильно сильнее Class **G** на validation set.

**Editorial sign-off (2026-06-23):** **SUPPORTED** — см. [TODAY_H4_VALIDATION_V0.md](./TODAY_H4_VALIDATION_V0.md).

**Ограничение:** H4 **не** объясняет delayed message, postponed conversation, expectation без observable action пользователя. Observable behavior — **один вид** сильных паттернов, не корневая причина.

**Редакционное правило:** «сначала наблюдаемое, потом вывод» — для правки G→R.  
**Не root model:** см. **H5 (Language)** [Self-Verification](./TODAY_SELF_VERIFICATION_V0.md).

| Observable (Class R) | Generic / interpretive (Class G) |
|----------------------|----------------------------------|
| ✅ перегруз — «это было вчера» | ❌ избегание — нужно принять вашу трактовку |
| ✅ усталость | ❌ проблемы с близостью |
| ✅ откладывание | ❌ «открыться миру» |
| ✅ «надо собраться» / чужие приоритеты | ❌ работа с доверием |

**Механизм:** overload / fatigue / procrastination / self_pressure — **наблюдаемы**.  
Avoidance / isolation / «открытость» — **психологические слова**, узнавания не создают.

**Риск (как с анкорами):** «есть internal pattern = хорошо» → refuted. **Важен тип паттерна.**

**Следующая проверка:** **H5 (Language)** Self-Verification — [TODAY_SELF_VERIFICATION_V0.md](./TODAY_SELF_VERIFICATION_V0.md). Не bulk api_live.

---

## HYPOTHESIS IPL-H5 — Lens independence *(deferred — post-RAT, variant B/C only)*

> **Не путать с H5 (Language) Self-Verification.**
>
> **Не запускать до RAT aggregate.** Без карты зависимости — ложный pass.

> Если RAT → **pattern-level:** один PIM slice может порождать **разные валидные** internal patterns в зависимости от контекста дня.

**Параллель с PIM:** goal text / outcome — не знание. Между signal и knowledge — ILR → Atom.  
**Гипотеза генерации (не канон):** между PIM и DRE может понадобиться слой выбора линзы — **если** IPL-H7 покажет pattern-level.

| Кандидат | Вопрос | Роль *(гипотеза)* |
|----------|--------|-------------------|
| **PIM** | Что **вероятно происходит**? | знание |
| **Tension** | Что создаёт **внутреннее давление**? | объяснение *(variant C)* |
| **Pattern** | **Через что** узнавание? | узнавание *(variant B/C)* |
| **Life object** | **Какая ситуация**? | узнавание *(variant D)* |
| **Context bundle** | **Комбинация** object · time · scene? | узнавание *(variant D+)* |
| **DRE** | Что **полезно показать**? | presentation |
| **TL-1** | Текст не сломан? | output gate |

**Примеры PIM (knowledge):** перегруз · избегание конфликта · переоценка сроков.  
**Примеры pattern (editorial taxonomy):** overcommitment · self-pressure · deferred closure.

**Reject:** проектировать pattern/tension/object layer до RAT · «IPL roadmap».

### Пример: один PIM, разные линзы *(H5 — day context меняется)*

PIM (stable): перегруз · высокая ответственность · привычка брать лишнее.

| День | Контекст | Selected pattern *(editorial)* |
|------|----------|------------------------|
| A | много входящих, карта «движение» | **overcommitment loop** (IP-002) |
| B | «надо собраться», усталость после недели | **self-pressure trap** (IP-004) |
| C | висящая начатая задача, низкий темп | **deferred closure** (IP-001) |

PIM **не изменился**. Меняется day context → другой **winner** среди кандидатов.

**Reject (H5):** selection = 1:1 map trait → pattern.

### Gate H5

Один PIM slice → ≥2 day contexts → **разные** selected patterns.

---

## HYPOTHESIS IPL-H6 — Pattern Selection layer *(deferred — post-RAT, variant B only)*

> **Вопрос уровнем ниже RAT.** H6: frozen day · ≥2 patterns правдивы · выбор главного.
>
> **Только если** RAT aggregate → pattern доминирует **и** bundle (E) не объясняет большинство кейсов.

**Параллель ILR:** не `Signal → chosen meaning`, а `Signal → competing interpretations → selection`.

```
PIM + day context (+ intent record if PR2+)
  → Pattern Candidates[]      multi-weight, все Class R
  → Pattern Selection         один primary для DRE
  → pattern_selection_audit
  → DRE → text
```

### Пример: один день, три кандидата

PIM: перегруз · ответственность · берёт лишнее.  
Day: обязательства · открытые задачи · цель «завершить проект».

| Candidate | Одновременно правдив? |
|-----------|----------------------|
| **overcommitment_loop** | «Удерживаешь слишком много одновременно» |
| **self_pressure_trap** | «Не объём — ощущение, что всё должно быть идеально» |
| **deferred_closure** | «Напряжение от незакрытых старых, не от новых» |

Все три **true at once**. Selection — **не** «самый правдивый автоматически побеждает».

### Truth vs usefulness — не один winner-score

На одном frozen day кандидаты могут расходиться по осям:

| Pattern | truth_score *(узнавание)* | day_relevance_score *(объясняет сегодня)* |
|---------|---------------------------|-------------------------------------------|
| overcommitment_loop | 0.82 | **0.91** |
| self_pressure_trap | **0.87** | 0.63 |
| deferred_closure | 0.76 | 0.58 |

Человек узнаёт себя **во всех трёх**. Но **overcommitment** лучше объясняет **этот** день (цель «завершить проект», много открытых задач).

**Вопрос ranking:** побеждает max truth или max day relevance? → **day relevance для primary lens**; truth без relevance — secondary hook или rejected, не DRE spine.

### Два этапа (не один «reasoning» blob)

| Этап | Вопрос | Вход |
|------|--------|------|
| **1. Candidate generation** | Какие patterns **поддерживаются** PIM + day context? | atoms, IM, ritual, focus, goal |
| **2. Candidate ranking** | Какой pattern **лучше всего объясняет сегодня**? | truth_score · day_relevance_score · `final_selection_score` |

Generation = retrieval (кто вообше в игре). Ranking = почему **этот** primary, не другой с большим evidence.

**Reject:** `PIM → chosen_pattern` без candidate set · single opaque score · LLM-only rank без audit axes.

### IPL ≠ Pattern Library *(если variant B/C — post-H7)*

| Артефакт | Роль |
|----------|------|
| **Pattern Reference** (IP catalog) | Editorial taxonomy · не platform layer |
| **Selection + audit** | *Только если RAT → pattern* · research sketch |

### Gate H6

Frozen `(user, day_id, intent_record_id, day_context)`:

- ≥2 valid Class R **candidates**;
- 1 **selected** + ≥1 **rejected** with `selection_reason`;
- DRE input = **selected** only.

Всегда ровно один candidate → lookup, не layer.

### Audit sketch *(hypothesis — post-H6 + H7 only)*

```json
{
  "selected_pattern": "overcommitment_loop",
  "candidates": [
    {
      "id": "overcommitment_loop",
      "truth_score": 0.82,
      "day_relevance_score": 0.91,
      "final_selection_score": 0.91,
      "selected": true
    },
    {
      "id": "self_pressure_trap",
      "truth_score": 0.87,
      "day_relevance_score": 0.63,
      "final_selection_score": 0.63,
      "selected": false
    },
    {
      "id": "deferred_closure",
      "truth_score": 0.76,
      "day_relevance_score": 0.58,
      "final_selection_score": 0.58,
      "selected": false
    }
  ],
  "supporting_evidence": ["atom_17", "atom_41", "intent_record_223"],
  "selection_reason": ["goal_completion_framing", "open_tasks_signal", "day_relevance_wins_over_truth"]
}
```

Ответы: **почему этот текст?** · **почему pattern A, хотя B had higher truth?**

Паритет audit stack: `pim_read_audit` · `pim_write_audit` · **`pattern_selection_audit`**.

---

## Platform shape — конкурирующие stacks *(не roadmap)*

**Prod сейчас:** variant **A** — `PIM → DRE → TL-1`.

| Variant | Stack | Когда проектировать |
|---------|-------|---------------------|
| **A** | `PIM → DRE` | RAT: узнавание не зависит от pattern/tension/object |
| **B** | `PIM → Pattern → DRE` | RAT → pattern dominates · **then** H6 |
| **C** | `PIM → Tension → Pattern → DRE` | RAT → tension explains · pattern personalizes |
| **D** | `PIM → Object → … → DRE` | RAT → object dominates |
| **E** | `PIM → (Object + Pattern + Tension bundle) → DRE` | RAT → **intersection** · collapse only when multi-component removed |

**Anti-pattern (AR-001, AR-002):** канонизировать любой variant · строить engine · говорить «IPL» как о решённом слое.

---

## HYPOTHESIS IPL-H7 — Recognition component map *(RAT — не «tension research»)*

> **Имя историческое (IPL-H7).** По сути: **какой компонент strong text несёт основную массу узнавания?**
>
> **Единственный активный track.** 30–40 cases · 2–3 нед · **∥ PR2** · **до** PR3 · **до** любого engine.

### Разметка + ablation ladder

Schema: [TODAY_LANGUAGE_CALIBRATION_V0.json](./datasets/TODAY_LANGUAGE_CALIBRATION_V0.json) · `recognition_research`.

| Поле | Зачем |
|------|--------|
| `recognition_score` | baseline (step 0) |
| `ablation_scores` | score после каждого step 1–5 |
| `tension_id` · `pattern_id` · `life_object` | компоненты bundle |
| `recognition_loss_reason` | почему упало на step N |
| `dominant_loss_component` | object \| pattern \| tension \| bundle |

### Outcomes → stack *(из aggregate map, не intuition)*

| RAT aggregate | Variant | Следующий шаг |
|---------------|---------|---------------|
| **Object** доминирует | **D** | object retrieval из PIM |
| **Pattern** доминирует | **B/C** | **тогда** H6 |
| **Tension** доминирует | **C** или **A** | pattern layer likely лишний |
| **Bundle** / multi-step collapse | **E** | bundle composer · не отдельный «IPL engine» |
| Равномерно мало | **A** | DRE-only |

### H7 vs H5/H6

| | RAT (H7) | H6 | H5 |
|---|----------|----|----|
| **Уровень** | **источник** узнавания | structure selection | editorial principle |
| **Когда** | **сейчас** | post-RAT · variant B | parallel |

**Do not:** называть H7 «tension test» · строить engine · bulk api_live.

---

## AR-001 — Premature collapse of recognition into explanation

| | |
|---|---|
| **ID** | AR-001 |
| **Risk** | Схлопнуть узнавание в объяснение (tension/DRE) до IPL-H7 |
| **Symptom** | `PIM → Tension → DRE` · tension как «единство узнавания» |
| **Failure mode** | **Потеря узнавания** при сохранении **объяснения** |
| **Parallel** | AP/SP: scene до anchor |
| **Mitigation** | RAT (H7) **до** stack decision · не `PIM → Tension → DRE` до aggregate map |

---

## AR-002 — Premature «IPL» / engine investment

| | |
|---|---|
| **ID** | AR-002 |
| **Risk** | Говорить про IPL как будущий engine · строить pattern/tension layer до IPL-H7 |
| **Symptom** | Pattern Selection Engine · Tension Engine · «IPL roadmap» |
| **Failure mode** | Месяцы на слое, который окажется лишним (variant A/D) или не на том уровне (variant C) |
| **Parallel** | AP/SP: ranking сцен до anchor |
| **Mitigation** | **Dependency map first** · не «IPL roadmap» · не engine до n=40 contribution map |

---

## AR-004 — Knowledge Density Illusion

| | |
|---|---|
| **ID** | AR-004 |
| **Risk** | «Чем больше фактов о человеке — тем лучше узнавание» |
| **Symptom** | PIM как **склад** high-confidence atoms · acquisition без RRM · density = quality |
| **Failure mode** | 100 фактов low recognition relevance **менее полезны**, чем 10 recognition atoms · память без отдачи |
| **RRM refutation *(hypothesis)*:** | «тишина» · «утренние встречи» · «использует Notion» — medium/low decision · **low recognition** |
| **Mitigation** | **Knowledge Type Catalog** + RRM · optimize **return per memory unit** · не volume |

**Platform economics:** RRM спрашивает не «что делает текст хорошим», а **какие знания имеют долгосрочную ценность для системы**.

**C17 ∩ RRM:** только **пересечение** двух карт → приоритет №1 atoms · Q4 (low/low) → **не добывать**.

**Следующий шаг AR-004:** **Acquisition Cost** + **Observability** → **Knowledge ROI** · **Reusability** → policy = **C17 ∩ RRM ∩ Observability ∩ Reusability** · не «high ROI → store» *(AR-009)*.

---

## AR-009 — Knowledge as Asset Illusion

| | |
|---|---|
| **ID** | AR-009 |
| **Risk** | «Высокий ROI → знание нужно **хранить** в PIM» |
| **Symptom** | PIM как **vault ценных фактов** · retention по ROI score |
| **Failure mode** | Память заполняется знаниями **ценными локально**, но **без платформенной отдачи** · один consumer = feature knowledge в PIM |
| **Parallel chain** | scene → good text · anchor → good text · pattern → recognition source · **high ROI → store** |
| **Example** | waiting_for_reply — high recognition · medium decision · uncertain ROI · **reusability unknown** (DRE only?) |
| **Mitigation** | **Reusability map** · platform vs feature knowledge · PIM для **процессов**, не активов |

**PIM существует не для хранения ценных знаний.** PIM существует для **поддержки будущих процессов** — это разные вещи.

---

## AR-008 — High Recognition / High Cost trap

| | |
|---|---|
| **ID** | AR-008 |
| **Risk** | «Собирать всё с высокой recognition relevance» без учёта стоимости добычи |
| **Symptom** | RRM → acquisition policy сразу после n=40 · prioritize high-rec atoms |
| **Failure mode** | Месяцы наблюдения · длинная история · много сигналов · PIM инвестирует в **теоретически идеальные**, **практически недоступные** знания |
| **Example** | waiting_for_reply · postpones_hard_conversations — high recognition · **high acquisition cost** · observability uncertain |
| **Mitigation** | **Knowledge Observability map** post-n=40 · **Knowledge ROI** · не KIP sign-off до трёх осей |

**Natural continuation AR-004:** память = ограниченный ресурс → учитывать не только **ценность**, но **стоимость получения**.

---

## AR-007 — Pattern as Scene *(carrier, not source)*

| | |
|---|---|
| **ID** | AR-007 |
| **Risk** | Pattern taxonomy mistaken for recognition **source** |
| **Symptom** | «58% pattern survivor → build IPL» без ablation |
| **Failure mode** | Pattern = carrier (как scene для anchor) · engine на носителе, не на источнике |
| **Parallel** | AP/SP Scene Engine до Anchor |
| **Mitigation** | RAT contribution map · AR-003 · не Pattern Selection до map |

---

## AR-005 — Recognition-only KIP trap

| | |
|---|---|
| **ID** | AR-005 |
| **Risk** | RRM как **одна** шкала recognition → drop low-recognition / high-**discovery** knowledge |
| **Symptom** | KIP оптимизирует только «это про меня» · слабые «вау», но сильные инсайты отфильтрованы |
| **Failure mode** | PIM теряет сигналы для **нового понимания** · модель не снижает неопределённость по скрытым паттернам |
| **Example** | overcommitment: high recognition · ambiguous-outcome avoidance: high **discovery** |
| **Mitigation** | Держать **discovery_relevance** открытой гипотезой · не RAT-only scoring · fork §Discovery |

---

## AR-006 — Discovery measured with Recognition instruments

| | |
|---|---|
| **ID** | AR-006 |
| **Risk** | Discovery Relevance Map по тем же правилам, что Recognition (editorial RAT) |
| **Symptom** | `discovery_relevance` на strong text at T0 · drop low-rec/low-dec «noise» |
| **Failure mode** | Отложенные инсайты отфильтрованы · KIP оптимизирован под instant hit |
| **Example** | success-criteria avoidance: rec=medium at read · discovery validated months later |
| **Mitigation** | Temporal instruments · PR2 longitudinal · Discovery fork open · AR-005 · §Стоп-условие · AR-010 |

---

## AR-010 — Layer before observable phenomenon *(meta)*

| | |
|---|---|
| **ID** | AR-010 |
| **Risk** | Построить validation layer / engine **до** наблюдаемого явления в prod |
| **Symptom** | Scene Engine до Anchor · traits без C14–C16 · Goal UI до IM · Pattern Engine до RAT · Discovery Protocol до Intent Records |
| **Gate question** | «У нас уже есть **наблюдаемое явление** — или только правдоподобная теория?» |
| **C18+ gate** | «**Какое наблюдаемое явление не может быть объяснено текущим стеком?**» — нет ответа → слой не нужен |
| **Failure mode** | Месяцы на Engine / Registry / Policy для сущности, которая не существовала отдельно |
| **Mitigation** | §Стоп-условие · §Platform Layer Gate · data-first · PR2 создаёт явление · Watchlist без выводов · [PIM_PR_GATE_V1.md](pim/PIM_PR_GATE_V1.md) C18 freeze |

**Asymmetric cost:** подождать ≈ бесплатно · ошибочная канонизация Discovery-оси = месяцы лишней работы. Fork B может снять need for Discovery policy entirely.

**См. также AR-011** — phenomenon creation vs analysis; inverse trap (осторожность vs факты).

---

## AR-011 — Phenomenon Before Analysis *(meta)*

| | |
|---|---|
| **ID** | AR-011 |
| **Risk** | Отложить **создание наблюдаемого явления**, пока совершенствуется архитектура гипотетических слоев |
| **Symptom** | Discovery / IPL / KIP / Pattern review **без** prod Intent Records · editor-only исследование без предмета |
| **Gate question** | «Мы уже **создаём** явление в prod — или только **обсуждаем** его модель?» |
| **Failure mode** | Команда научилась не строить преждевременные слои — и перестала создавать **факты** для следующих решений |
| **Mitigation** | PR2 write-path · prod launch · ≥50–100 IR · §Стоп-условие · AR-010 · AR-009 только post-signal |
| **Canonical object** | Завершённый Intent Record lifecycle — не PIM slice, не editorial corpus |

**Phase:** pre-PR2 = phenomenon creation · post-PR2 prod data = knowledge extraction *(Discovery fork · KIP · IPL)*.

**PR2 Success Criterion** *(не merge gate)*: retention **и** IR as byproduct — см. [PR2_PREFLIGHT.md](./archive/PR2_PREFLIGHT.md) §15 · AR-012. IR-only success без D7/D10 = **instrumentation trap**.

**Roadmap gate question:** создаём **поток фактов** быстрее, чем **новые гипотезы**? *(только если продукт уже даёт причину вернуться — иначе см. AR-012)*

### Launch priority freeze *(2026-06-23 · revised)*

**Главная проблема — продуктом почти никто не пользуется.** Пока нет **ощутимой ежедневной пользы**, архитектура · retention · data — шум.

**Цель не «собрать Intent Records».** Цель — **продукт, которым люди захотят пользоваться регулярно**. IR · longitudinal · Discovery — **следствие** использования, не мотивация пользователя.

**Главные вопросы продукта:**

> Что пользователь получает **вечером**, чего не было бы **без** TodayFlow?  
> Становится ли жизнь **ощутимо лучше** от завершённого дня?

| # | Приоритет *(usefulness first)* |
|---|--------------------------------|
| 1 | **Утренний ритуал** — ясность и фокус (S0–S5) |
| 2 | **Польза в течение дня** — важное сделано (S9) |
| 3 | **Вечернее завершение** — «день был лучше благодаря TodayFlow» (S10) |
| 4 | **Осознанный следующий день** — continuity без guilt |
| 5 | PR2 write-path · IR · Discovery — **после** доказанной пользы |

**Gate question для новой работы:** увеличивает ли это **вечернюю полезность**? Retention (D7) — **индикатор**, не цель sprint.

**Launch one-liner:** не data · не streak — **день, который вечером ощущается полезнее**.

---

## AR-012 — Usefulness Before Instrumentation *(meta)*

| | |
|---|---|
| **ID** | AR-012 |
| **Risk** | Оптимизировать **метрики** (IR, retention, audits) без **ощутимой пользы** завершённого дня |
| **Symptom** | Высокий D7 при слабом вечернем ответе · «PR2 success» · streak без результата |
| **Gate question** | «Становится ли жизнь пользователя **ощутимо лучше** от завершённого дня в TodayFlow?» |
| **Evening question** | «Что человек получил **вечером**, чего не было бы **без** TodayFlow?» |
| **Failure mode** | Липкий ритуал / data pipeline **без** ценности · или infra принята за продукт |
| **Mitigation** | §0.2 PIM North Star · evening screen test S0–S10 · usefulness → retention → data |
| **Relationship** | **AR-011** = не analysis layers рано · **AR-012** = usefulness **→** retention **→** data |

**Retention — не North Star.** Главный **внешний индикатор**, что ежедневная полезность **реальна**. Люди возвращаются ради **результата**, не ради ритуала.

**Продуктовая ценность** *(цель)* → **поведение** *(D1/D7/завершённые дни)* → **данные** *(IR · longitudinal)*.

**Sticky ritual trap:** D7 хороший · вечером «ничего не изменилось» — продуктовый провал (Duolingo без языка).

**Evening screen test:** каждый экран S0–S10 — повышает ли шанс *«день был лучше благодаря TodayFlow»*? Только «какие данные соберём» → infra.

**Infrastructure trap:** PIM · Intent Record · PR2 — не продукт. Продукт = **полезность** между утром и вечером.

---

## AR-003 — False Universal Survivor

| | |
|---|---|
| **ID** | AR-003 |
| **Risk** | Все strong texts сводятся к **одной** минимальной единице узнавания |
| **Symptom** | «IPL = source of recognition» · проектирование `PIM → IPL → DRE` |
| **Pilot refutation** | n=19: 58% / 16% / 16% / 11% — **четыре** mechanism classes; 42% ≠ шум |
| **Key case** | **cal-018** (top exemplar) → `context_bundle` — не reducible to pattern or object |
| **Mitigation** | North star → **class→survivor map** · candidate = multimodal Recognition Retrieval |

**Candidate outcome *(post n=40, not canon)*:**

```
PIM → Recognition Retrieval (Pattern · Object · Context Bundle) → DRE
```

---

### Gate-вопросы (калибровка)

0. **RAT phase 2:** contribution map · `text_class` → mechanism · n=30–40 · **not** global winner.
1. **H5 (Language):** self-verification · parallel editorial.
2. **H6** *(post-RAT, variant B):* frozen day · competing patterns.
3. **Causality** *(post-stack decision):* selected + slice + почему не другой.

### Скрытый словарь причинности

На 32 keep/exemplar ([calibration](../datasets/TODAY_LANGUAGE_CALIBRATION_V0.json)): top-2 pattern clusters ≈ **63%**, top-5 ≈ **91%**.  
Это не «что написать», а «**через какую человеческую закономерность** объяснить день».

**Симптом неверного pattern:** факты верны · совет логичен · грамматика ок · **узнавания нет** — pattern выбран неверно, не текст слаб.

---

## Pattern taxonomy vs PIM *(не platform layer)*

| | **PIM** | **Pattern taxonomy** *(editorial)* |
|---|---------|-------------------------------------|
| Объект | Знание о человеке | Повторяющиеся **объяснительные конструкции** в strong texts |
| Статус | platform layer (PR2 write) | **calibration artifact** · IP-001…008 |
| Доказано | atoms · IM · read audit | clustering · Class R > G |
| **Не доказано** | — | IPL как самостоятельный слой между PIM и DRE |

**Имена «IPL» / «Engine»** — historical. Сейчас: **taxonomy + RAT**. Platform layer — **только после** RAT aggregate + stack variant sign-off.

---

## Классы паттернов

### Class R — Recognition

Высокий keep. Узнавание **сразу**, без интерпретации.

| id | slug | n | Keep % | Observable test |
|----|------|--:|-------:|-----------------|
| IP-002 | overload | 9 | **100** | «Слишком много задач / перегруз» — да, вчера |
| IP-004 | self_pressure | 4 | **100** | «Надо собраться», чужие приоритеты |
| IP-007 | fatigue | 3 | **100** | «Устал» — телесно, вчера |
| IP-001 | procrastination | 4 | 75 | «Давно откладывал» — особенно + object |

### Class G — Generic

Психологично звучит. Узнавания нет или слабое.

| id | slug | n | Keep % | Rewrite % | Почему G |
|----|------|--:|-------:|----------:|----------|
| IP-003 | avoidance | 3 | **0** | **100** | «Избегайте догадок» — интерпретация поведения |
| IP-008 | isolation | 3 | 33 | 33 | «Изолирован / замыкается» — без конкретики |
| — | openness / trust / closeness | — | — | — | *Lexical traps в api_live, не отдельные IP yet* |

### Pending (мало данных)

| id | slug | n | Примечание |
|----|------|--:|------------|
| IP-005 | rumination | 0 | Кандидат; проверять **после** H4 |
| IP-006 | indecision | 1 | 100% keep, n=1 — не generalize |

---

## Каталог IP-001 … IP-008

`Keep %` = keep + exemplar · 22 записи с AT-006 в 60 api_live.

| id | Pattern | class | n | Keep % | Rewrite % |
|----|---------|-------|--:|-------:|----------:|
| IP-002 | overload | **R** | 9 | 100 | 0 |
| IP-004 | self_pressure | **R** | 4 | 100 | 0 |
| IP-007 | fatigue | **R** | 3 | 100 | 0 |
| IP-001 | procrastination | **R** | 4 | 75 | 25 |
| IP-003 | avoidance | **G** | 3 | 0 | 100 |
| IP-008 | isolation | **G** | 3 | 33 | 33 |
| IP-006 | indecision | pending | 1 | 100 | 0 |
| IP-005 | rumination | pending | 0 | — | — |

### Контрпример H3 (полная версия refuted)

Если бы «любой AT-006 = сильный», все 22 записи были бы keep-heavy.  
**Avoidance 0% keep**, **isolation 33%** — внутри AT-006 есть R и G.

### Сильная vs слабая формулировка (генерация)

| ❌ Слабая | Class | Почему |
|----------|-------|--------|
| «Поговорите с партнёром» | AT-005 + AT-004 | нет internal |
| «Избегайте догадок» | IP-003 (G) | интерпретация |

| ✅ Сильная | Class | Почему |
|----------|-------|--------|
| «Отчёт, который **давно откладывали**» | IP-001 (R) + object | observable |
| «Если уже неделю **откладываете** разговор…» | IP-001 (R) + relationship | observable delay, не «избегание» |

---

## Internal Pattern layer (pre-TL-1)

**Не gate.** Если H4 + H5 + **H6**:

```
PIM + day context (+ intent if PR2+)
  → Candidate generation (retrieval)
  → Candidate ranking (truth · day_relevance · final)
  → pattern_selection_audit
  → DRE (presentation under selected lens)
  → TL-1
```

**TL-1 BLOCKED.** Порядок работ *(не менять)*:

```
1. PR2 — Intent Record write-path
2. Longitudinal data — реальный цикл Goal → … → Next Goal
3. Discovery Watchlist — наблюдение *(∥ RAT recognition on texts)*
4. RAT / ablation — dependency map + KIP/RRM recognition tier (n→40)
5. Через несколько недель — первые траектории · fork review *(≥50–100 IR)*
6. Discovery fork decision — axis vs delayed validation vs hybrid
7. Stack candidate A–E · atom curation · platform layer
```

| # | Gate | Блокирует |
|---|------|-----------|
| 1 | **PR2** | write-path · causal merge |
| 2 | **RAT** | dependency map · RRM · class matrix |
| 3 | **Map + RRM sign-off** | stack canon · acquisition priority · platform layer |
| 4 | **H6** *(scenario 2 only)* | pattern selection layer |
| 5 | **TL-1** | prod gate |

**Pause (AR-001…009):** не строить retrieval/ranking между PIM и DRE до map. RAT = **recognition** on texts. **Discovery fork open** — Watchlist only, no protocol/engine until prod Intent Records.

---

## Changelog

| Дата | Изменение |
|------|-----------|
| 2026-06-23 | v2.5 — §Platform Layer Gate (C18+); anti-fantasy ladder; HostFlow→TodayFlow build order |
| 2026-06-23 | v3.1 — AR-012 usefulness not retention as North Star; usefulness→retention→data; evening screen test |
| 2026-06-23 | v3.0 — Experience North Star; Retention→Data; month-1 KPI; infrastructure trap; launch one-liner |
| 2026-06-23 | v2.9 — AR-012 Retention Before Instrumentation; Launch freeze revised; PR2 Success = retention + IR byproduct |
| 2026-06-23 | v2.8 — Launch priority freeze; users+data bottleneck; ship gate question |
| 2026-06-23 | v2.7 — PR2 Success Criterion (data metrics, merge ≠ success); roadmap gate question |
| 2026-06-23 | v2.6 — AR-011 Phenomenon Before Analysis; two-risk frame; phenomenon creation vs extraction; inverse trap |
| 2026-06-23 | v2.4 — Reusability axis; AR-009 Knowledge as Asset Illusion; platform vs feature knowledge; AR-010 (ex-009 meta) |
| 2026-06-23 | v2.3 — §Стоп-условие (observable vs theory); AR-010 meta; asymmetric cost; Fork B upside |
| 2026-06-23 | v2.2 — Discovery fork open until prod IR; Watchlist (not protocol); no Discovery Engine |
| 2026-06-23 | v2.1 — Knowledge ROI; Acquisition Cost; Observability; AR-008; post-n=40 gate before KIP |
| 2026-06-23 | v2.0 — KIP (not RRM-only); temporal asymmetry; Discovery fork; AR-006/007; longitudinal vs RAT; Knowledge Type Catalog |
| 2026-06-23 | v1.9 — Discovery hypothesis; AR-005; 3-axis KIP |
| 2026-06-23 | v1.8 — RRM candidate KIP/C18; store vs acquire; 2×2 matrix |
| 2026-06-23 | v1.7 — RAT = knowledge value; RRM not IPL-linked |
| 2026-06-23 | v1.6 — PR2∥RAT knowledge split; RRM vs C17 two axes |
| 2026-06-23 | v1.5 — contribution map; AR-004; 4 scenarios; project focus |
| 2026-06-23 | v1.4 — AR-003 False Universal Survivor; multimodal retrieval candidate |
| 2026-06-23 | v1.3 — variant E bundle; RAT ablation ladder; dependency map |
| 2026-06-23 | v1.2 — source of recognition; RAT; Object Layer |
| 2026-06-23 | v1.1 — stop «IPL engine»; RPT; variants A–D; recognition unit localization |
| 2026-06-23 | v1.0 — north star; H7 cheap editorial; AR-002 |
| 2026-06-23 | v0.9 — H7 collapse test; AR-001; tension=explanation / pattern=recognition |
| 2026-06-23 | v0.8 — IPL-H7 demoted: after H6 only; A/B/C counterexample; no Tension→DRE skip |
| 2026-06-23 | v0.6 — IPL-H7 tension-before-pattern; H6 pairs + tension_id |
| 2026-06-23 | v0.5 — truth vs day_relevance; retrieval not reasoning; IPL sibling of PIM |
| 2026-06-23 | v0.4 — H6 competing patterns; pattern_selection_audit |
| 2026-06-23 | H4 validation set: [TODAY_H4_VALIDATION_V0](./TODAY_H4_VALIDATION_V0.md) — 20 entries |
| 2026-06-23 | v0.3 — H5 lens independence; IPL vs PIM |
| 2026-06-23 | v0.2 — H3 narrowed; Class R/G; H4 Observable; rumination deprioritized |
| 2026-06-23 | v0.1 — IP-001…IP-008; pause batch_5 |
