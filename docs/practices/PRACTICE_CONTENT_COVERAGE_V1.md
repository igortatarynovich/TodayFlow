# Practice Content Coverage v1

**Статус:** `ACCEPTED` — SoT fill-pass библиотеки. **Fill unfrozen** 2026-08-26.  
**Версия:** 1.12 (2026-08-29); pointer 2026-08-29 — decision-making-focus cell sourced via priority_setting, not research ladder.  
**Владелец:** Product.  
**Ledger:** [`DATA/reference/practice/content_coverage_matrix_v1.json`](../../DATA/reference/practice/content_coverage_matrix_v1.json).  
**Parent:** [PRACTICE_CONTENT_TAXONOMY_V1.md](./PRACTICE_CONTENT_TAXONOMY_V1.md) §0.1 · §10.  
**Active fill:** [PRACTICE_LIBRARY_FILL_V1.md](./PRACTICE_LIBRARY_FILL_V1.md).  
**Provenance:** [PRACTICE_TECHNIQUE_PROVENANCE_V1.md](./PRACTICE_TECHNIQUE_PROVENANCE_V1.md).

**Это:** какие ячейки продукт обязан уметь закрыть **до** массовой генерации текста.  
**Это не:** тексты практик как SoT · runtime retrieval · screen need-чипы · cartesian product · разрешение писать payload из LLM.

---

## Architecture impact

- **SoT before:** taxonomy locked types/purpose/state; fill implied as «написать items против vocab». Риск — плотность в одной технике (40 grounding) и дыры в purpose/direction/class. После P0/P1 density: 133 LLM-draft items закрывали cells, но техника не имела provenance.
- **SoT after:** fill = coverage-first **архитектура** (26 need cells, type spine, item shape) остаётся. **Содержание 133 LLM drafts не SoT.** Research ladder archived, non-blocking. Active fill = lightweight provenance. `box_breathing` = skipped_for_now. Next sourced cell = `need.transition.prepare`. Первые 16 items = architecture probes.
- **Public contract changed?** no
- **Migration required?** no runtime. 133 drafts stay provisional without `technique_id`.
- **Canon updated?** yes — this file · matrix JSON · [PRACTICE_LIBRARY_FILL_V1](./PRACTICE_LIBRARY_FILL_V1.md) · [PRACTICE_TECHNIQUE_PROVENANCE_V1](./PRACTICE_TECHNIQUE_PROVENANCE_V1.md) · taxonomy pointer · tracker
- **Backward compatible?** yes for clients. Not compatible with continuing LLM-seed as content SoT.

---

## 0. Закон fill-pass

0. **Fill unfrozen.** Не продолжать research ladder. Не продолжать `box_breathing` / `energizing_breath`. 133 draft = `llm_provisional` until a cell is rewritten against an `accepted` technique. Первые 16 = architecture probes. Next sourced cell = `need.transition.prepare`.
1. **Сначала покрытие, потом плотность.** Не писать второй item в закрытую ячейку, пока есть `empty` в P0. (Архитектурный закон; плотность не возобновляется до provenance.)
2. **Не декартово произведение.** 25 purpose × 10 direction × 86 type — не план. План = need cells ниже.
3. **Ячейка = потребность продукта**, не «ещё одна карточка». Закрыта, когда есть ≥1 `active`/`draft` item, чьи retrieval-поля попадают в cell (purpose + direction + class/type формы).
4. **Preferred type — fill target.** Meaning по-прежнему эмитит только state → direction → purpose. Retrieval может выбрать alt form (другой class/type), если constraints так говорят.
5. **Один purpose — два job'а допустимы**, если class разный: «сейчас» (`practice`/`meditation`/`affirmation`) vs «на период» (`discipline`). Это не дубль grounding.
6. **Порядок seed детерминированный.** Следующий pass = первая `empty` P0 cell в порядке `need_cells[]` ledger. Не выбирать ячейку по удобству темы.
7. **Один seed item закрывает одну need cell.** Несколько retrieval tags (states, context) допустимы. Ledger `item_ids` пишется только в `seed_cell`. Совпадение tags с другой ячейкой **не** закрывает её.

---

## 1. Три слоя покрытия

| Слой | Вопрос | P0 criterion |
|------|--------|----------------|
| **Need cells** | Можем ли ответить на потребность? | 25 cells §2, каждая ≥1 item |
| **Type spine** | Есть ли seed у обязательных техник? | каждый P0 type §3 ≥1 item; остальные types = P1/deferred |
| **State/direction** | Нет ли дыр в персонализации? | каждый `input_state` и каждый `direction` встречается ≥1 P0 cell |

Density (P1): второй duration, другой context, audio vs text, EN locale.  
Remap (P2): legacy catalog → эти cells, не новый type-список.

---

## 2. P0 need cells

Один канонический direction на purpose. Typical `input_state` — подсказка retrieval, не отдельный enum в id.

`id` = `need.{purpose}.{direction}`.

| id | purpose | direction | typical input_state | primary form | alt form | job |
|----|---------|-----------|---------------------|--------------|----------|-----|
| `need.calm.downregulate` | calm | downregulate | overstimulated, tense | practice / extended_exhale | meditation / relaxation | now |
| `need.focus.focus` | focus | focus | scattered | meditation / focused_attention | practice / box_breathing (skipped) | now |
| `need.energy.activate` | energy | activate | low_energy | practice / mobility | practice / energizing_breath (skipped) | now |
| `need.grounding.stabilize` | grounding | stabilize | scattered, disconnected, tense | practice / sensory_grounding | meditation / grounding | now |
| `need.clarity.reflect` | clarity | reflect | uncertain | practice / prompted_reflection | meditation / reflection_meditation | now |
| `need.confidence.open` | confidence | open | uncertain | affirmation / capability | affirmation / self_trust | now |
| `need.release.release` | release | release | emotionally_heavy, stuck | practice / body_release | meditation / letting_go | now |
| `need.rest.downregulate` | rest | downregulate | overstimulated | meditation / relaxation | practice / progressive_relaxation | now |
| `need.sleep.prepare` | sleep | prepare | restless, overstimulated | meditation / sleep | practice / evening_ritual | now |
| `need.sleep.discipline` | sleep | prepare | restless | discipline / sleep_discipline | — | period |
| `need.motivation.activate` | motivation | activate | stuck, low_energy | practice / micro_action | affirmation / agency | now |
| `need.emotional_awareness.reflect` | emotional_awareness | reflect | emotionally_heavy | practice / self_check_in | meditation / open_awareness | now |
| `need.self_connection.reflect` | self_connection | reflect | disconnected | practice / journaling | meditation / body_scan | now |
| `need.connection.connect` | connection | connect | disconnected | practice / connection_action | affirmation / relationship | now |
| `need.creativity.open` | creativity | open | stuck | practice / creative_prompt | practice / free_writing | now |
| `need.decision_making.focus` | decision_making | focus | uncertain | practice / priority_setting | practice / intention_setting | now |
| `need.transition.prepare` | transition | prepare | scattered | practice / transition_ritual | practice / morning_ritual | now |
| `need.recovery.recover` | recovery | recover | tense, low_energy | practice / progressive_relaxation | meditation / body_scan | now |
| `need.discipline.prepare` | discipline | prepare | restless | discipline / routine_commitment | discipline / consistency_challenge | period |
| `need.self_control.stabilize` | self_control | stabilize | restless | discipline / attention_discipline | discipline / digital_limit | period |
| `need.detachment.release` | detachment | release | overstimulated | discipline / abstinence | meditation / acceptance | mixed |
| `need.consistency.prepare` | consistency | prepare | scattered | discipline / consistency_challenge | discipline / routine_commitment | period |
| `need.simplicity.release` | simplicity | release | overstimulated | discipline / reduction | discipline / consumption_limit | period |
| `need.reset.release` | reset | release | stuck | practice / digital_pause | practice / environment_reset | now |
| `need.presence.stabilize` | presence | stabilize | scattered, balanced | meditation / mindfulness | meditation / breath_awareness | now |
| `need.habit_change.prepare` | habit_change | prepare | stuck | discipline / consistency_challenge | discipline / routine_commitment | period |

26 cells: 25 purpose + extra `need.sleep.discipline` (тот же purpose, другой job). Не 26-й purpose.

Screen needs (`PRACTICES_SCREEN_V1` §1) закрываются этими cells, не отдельной матрицей:

| Screen need | P0 cell |
|-------------|---------|
| calm | `need.calm.downregulate` |
| focus | `need.focus.focus` |
| recover | `need.recovery.recover` |
| body | `need.grounding.stabilize` |
| understand | `need.clarity.reflect` |
| sleep | `need.sleep.prepare` |

---

## 3. P0 types (spine)

Тип в P0, если он primary или alt хотя бы одной P0 cell. Остальные types = **P1** (density после зелёных need cells). В ledger v1.0 `deferred` нет: не-P0 = P1, не «выбросить из продукта».

P0 **не** требует item на каждый из 86 types.

Порядок seed:

1. Первая `empty` P0 cell в порядке ledger — primary form, одна ячейка за раз.
2. Оставшиеся P0 types, у которых ещё `item_ids = []` (обычно alt, не взятые как primary).
3. Только потом P1 density.

Канон кодов: `type_spine[].phase` в ledger (сейчас **44 P0 / 42 P1**). Сводка в markdown не дублирует список — при расхождении ведёт JSON.

Seed-pass не закрывает несколько cells одним item, даже если retrieval tags пересекаются. Плотность/reuse — не этот pass.

---

## 4. Как закрывать ячейку

На один seed item:

1. Взять **первую empty** P0 cell в порядке ledger (не выбирать вручную).
2. Заполнить три группы ([taxonomy §10](./PRACTICE_CONTENT_TAXONOMY_V1.md#10-content-item--три-группы)). `identity.seed_cell` = id этой ячейки.
3. `purpose` / `direction` / `input_state` / `content_class` / `type` совпадают с cell (primary form).
4. Duration: Today now-job ≤ 5 min, если cell не sleep/evening; discipline — `duration_days`, не минуты сессии.
5. Payload: `ru` обязателен. Без medical claims. Ritual = последовательность, не магия.
6. Записать `item_id` **только** в `item_ids[]` этой ячейки (+ type_spine этого type). Status cell → `seed` пока draft, `covered` когда item `active`.

**Шаг 2 — оставшиеся P0 types** (после того как нет empty need cells):

1. Взять **первый** P0 `type_spine[]` с `item_ids = []`.
2. `seed_cell` = первая `need_cells[]` cell, чей primary **или** alt совпадает с этим class/type.
3. Форма item = alt (или primary, если type ещё не сеяли). Retrieval = purpose/direction/typical states **этой** cell.
4. Append `item_id` в `item_ids[]` этой cell (primary остаётся первым). Не писать тот же item во вторую cell, даже если type там тоже alt (`meditation.body_scan` → только `need.self_connection.reflect`, не recovery).
5. Discipline extras / session duration — по class, как в шаге 1.

**Шаг 3 — P1 density** (после закрытых P0 cells и P0 types). Одна ось на type, порядок `type_spine[]` P0:

1. Взять первый P0 type без same-cell sibling с другим `duration` / `duration_days` / `context` / `delivery`.
2. Тот же `seed_cell`, class, type, purpose, direction, что у первого item этого type.
3. Ось: session `duration < 5` → `5`; session уже `5` (sleep/evening) → `delivery = audio + guided` (без `media_ref`); discipline → `duration_days = 14`. Не EN и не вторая ось на том же item.
4. Append в cell `item_ids` и `type_spine` этого type. Не писать во вторую cell.
5. **P1 types (42)** не вешать на P0 cells: validator `form_ok` = только primary/alt ячейки. Это не density и не этот pass.

**Шаг 4 — EN locale** (после шага 3). Не новые items:

1. На каждом существующем item: `payload.locales.en.title` + `body`; `presentation.outcome_label.en`.
2. `ru` остаётся обязательным. Discipline extras (`commitment_rule` и др.) остаются в исходной строке — не плодить второй контракт.
3. Те же запреты payload: без `purpose` / `direction` / type code / `item_id`. Для `meditation.sleep` английский текст не содержит `sleep`.

**Шаг 5 — context `work` vs `evening`** (после шага 4). Одна ось, порядок P0 `type_spine[]`:

1. Клонировать первый item type (`.001` / первый в `item_ids`). Duration/delivery/`duration_days` не менять.
2. Context: `work` (без evening) → `evening + anytime`; already evening/`before_sleep` → `work + anytime`; `morning` → `evening + anytime`; только `anytime` → `evening`.
3. Тот же `seed_cell`. Payload ru+en копируются (техника та же, меняется когда предлагать).
4. Не вешать P1 types на P0 cells.

**DoD одной ячейки** (не «текст хороший»):

- ячейка больше не `empty`
- item валиден против taxonomy + item contract
- retrieval-полей достаточно, чтобы попасть в cell
- payload без semantic/retrieval logic (коды, purpose, item_id, «почему сегодня»)
- coverage ledger ссылается на `item_id` (ровно эта cell + type_spine)
- другие empty cells не получили этот `item_id`
- Meaning / public Today JSON **не** менялись

Семена: `need.grounding.stabilize` → `practice.sensory_grounding.001`; `need.calm.downregulate` → `practice.extended_exhale.001`; `need.focus.focus` → `practice.box_breathing.001`; `need.energy.activate` → `practice.energizing_breath.001`; `need.clarity.reflect` → `practice.prompted_reflection.001`; `need.confidence.open` → `affirmation.capability.001`; `need.release.release` → `practice.body_release.001`; `need.rest.downregulate` → `meditation.relaxation.001`; `need.sleep.prepare` → `meditation.sleep.001`; `need.sleep.discipline` → `discipline.sleep_discipline.001`; `need.motivation.activate` → `practice.micro_action.001`; `need.emotional_awareness.reflect` → `practice.self_check_in.001`; `need.self_connection.reflect` → `practice.journaling.001`; `need.connection.connect` → `practice.connection_action.001`; `need.creativity.open` → `practice.creative_prompt.001`; `need.decision_making.focus` → `practice.priority_setting.001`; `need.transition.prepare` → `practice.transition_ritual.001`; `need.recovery.recover` → `practice.progressive_relaxation.001`; `need.discipline.prepare` → `discipline.routine_commitment.001`; `need.self_control.stabilize` → `discipline.attention_discipline.001`; `need.detachment.release` → `discipline.abstinence.001`; `need.consistency.prepare` → `discipline.consistency_challenge.001`; `need.simplicity.release` → `discipline.reduction.001`; `need.reset.release` → `practice.digital_pause.001`; `need.presence.stabilize` → `meditation.mindfulness.001`; `need.habit_change.prepare` → `discipline.consistency_challenge.002`.

Запрещено: генерировать payload без пустой P0 cell (шаг 1) или без пустого P0 type_spine (шаг 2) или без P0 type, которому ещё нет density sibling (шаг 3); вешать P1 type на P0 cell; закрывать cell только title без retrieval-полей; ставить `item_id` в meaning/prompt; автозакрывать соседние cells по пересечению tags. EN без `locales.ru` не считается закрытым item.

---

## 5. P1 / P2

| Phase | Что | Статус |
|-------|-----|--------|
| P1 density (ось duration/delivery) | второй duration (5 min / 14 days) или audio+guided если now-job уже 5 | **done** — 44 siblings, тот же `seed_cell` |
| P1 density (EN locale) | `locales.en` + `outcome_label.en` на всех 89 items | **done** |
| P1 density (другой context) | `work` vs `evening` как отдельная ось retrieval | **done** — 44 siblings |
| P1 density (audio vs text) | `delivery` audio+guided на seed, который ещё text+unguided | **cancelled** — fill frozen; LLM is not technique source |
| P1 types семейства | 42 types не primary/alt ни одной P0 cell | **blocked**: `form_ok` не пускает на текущие cells. Нужны P1 variant cells или смена SoT |
| P1 variants | тот же purpose, другой direction (`need.focus.stabilize` и т. п.) | не этот pass — расширение ledger |
| **Technique landscape** | семейства методов + типы источников по class | **archive** — [PRACTICE_TECHNIQUE_LANDSCAPE_V1](./PRACTICE_TECHNIQUE_LANDSCAPE_V1.md); non-blocking |
| **Shortlist criteria** | допуск семьи к shortlist (C1–C9); не корпус | **archive** — [PRACTICE_TECHNIQUE_SHORTLIST_CRITERIA_V1](./PRACTICE_TECHNIQUE_SHORTLIST_CRITERIA_V1.md) |
| **Shortlist by family** | loci под критерии; type = expression hypothesis | **archive** — one slice: [PRACTICE_TECHNIQUE_SHORTLIST_V1](./PRACTICE_TECHNIQUE_SHORTLIST_V1.md) |
| **Ingest** | paraphrase selected loci → evidence records | **archive** — [PRACTICE_TECHNIQUE_INGEST_V1](./PRACTICE_TECHNIQUE_INGEST_V1.md) |
| **Normalization** | один kernel / split / insufficient_evidence | **archive** — [PRACTICE_TECHNIQUE_NORMALIZATION_V1](./PRACTICE_TECHNIQUE_NORMALIZATION_V1.md) (`insufficient_evidence`) |
| **Targeted shortlist** | identity post-exhale hold | **archive** — [PRACTICE_TECHNIQUE_TARGETED_SHORTLIST_V1](./PRACTICE_TECHNIQUE_TARGETED_SHORTLIST_V1.md) |
| **Targeted ingest** | paraphrase selected resolution loci | **archive** — [PRACTICE_TECHNIQUE_TARGETED_INGEST_V1](./PRACTICE_TECHNIQUE_TARGETED_INGEST_V1.md) |
| **Normalization V1.1** | retry: post_exhale_hold + equal_count axes, then overall verdict | **archive** — [PRACTICE_TECHNIQUE_NORMALIZATION_V1_1](./PRACTICE_TECHNIQUE_NORMALIZATION_V1_1.md) (`normalize_one` candidate) |
| **Safety Review** | bounds / claims of the normalized candidate | **archive** — [PRACTICE_TECHNIQUE_SAFETY_REVIEW_V1](./PRACTICE_TECHNIQUE_SAFETY_REVIEW_V1.md) (`insufficient_safety`) |
| **Targeted Safety Shortlist** | who_must_not_hold for required holds | **archive** — [PRACTICE_TECHNIQUE_TARGETED_SAFETY_SHORTLIST_V1](./PRACTICE_TECHNIQUE_TARGETED_SAFETY_SHORTLIST_V1.md) (stop A) |
| **Targeted Safety Ingest** | paraphrase selected hold-safety loci | **archive** — [PRACTICE_TECHNIQUE_TARGETED_SAFETY_INGEST_V1](./PRACTICE_TECHNIQUE_TARGETED_SAFETY_INGEST_V1.md) (not continued) |
| **Safety Review V1.1** | may_release vs model of who_must_not_hold | **not opened** — research escalation closed |
| **Library fill / lightweight provenance** | source check → description → safety if needed → accepted/skipped → Content Item | **next** — [PRACTICE_LIBRARY_FILL_V1](./PRACTICE_LIBRARY_FILL_V1.md); next cell `need.transition.prepare`; sourced 16/26; `box_breathing`, `energizing_breath` and `self_trust` skipped_for_now |
| P2 remap | `CONTENT/practices/*.json`, C1.4 ascetics → items; не новые types | после sourced fill, не вместо |

---

## 6. Чтение матрицы

Ledger JSON:

- `need_cells[].status`: `empty` · `seed` · `covered`
- `need_cells[].item_ids`: `need.calm.downregulate` → `practice.extended_exhale.001`; `need.focus.focus` → `practice.box_breathing.001`; `need.energy.activate` → `practice.energizing_breath.001`; `need.grounding.stabilize` → `practice.sensory_grounding.001`; `need.clarity.reflect` → `practice.prompted_reflection.001`; `need.confidence.open` → `affirmation.capability.001`; `need.release.release` → `practice.body_release.001`; `need.rest.downregulate` → `meditation.relaxation.001`; `need.sleep.prepare` → `meditation.sleep.001`; `need.sleep.discipline` → `discipline.sleep_discipline.001`; `need.motivation.activate` → `practice.micro_action.001`; `need.emotional_awareness.reflect` → `practice.self_check_in.001`; `need.self_connection.reflect` → `practice.journaling.001`; `need.connection.connect` → `practice.connection_action.001`; `need.creativity.open` → `practice.creative_prompt.001`; `need.decision_making.focus` → `practice.priority_setting.001`; `need.transition.prepare` → `practice.transition_ritual.001`; `need.recovery.recover` → `practice.progressive_relaxation.001`; `need.discipline.prepare` → `discipline.routine_commitment.001`; `need.self_control.stabilize` → `discipline.attention_discipline.001`; `need.detachment.release` → `discipline.abstinence.001`; `need.consistency.prepare` → `discipline.consistency_challenge.001`; `need.simplicity.release` → `discipline.reduction.001`; `need.reset.release` → `practice.digital_pause.001`; `need.presence.stabilize` → `meditation.mindfulness.001`; `need.habit_change.prepare` → `discipline.consistency_challenge.002`
- `type_spine[]`: `phase` = `P0` \| `P1` \| `deferred`
- `gaps`: 0 P0 cells still `empty`; duration/delivery + EN + work/evening context density present. Content origin = `llm_provisional`.

Следующий рабочий шаг: **library fill** следующей ячейки. Sourced 16/26. Latest: `need.decision_making.focus` (`priority_setting`; write one priority, set rest aside, close). Next = `need.transition.prepare`. Не Safety Review. Не box / energizing-breath research.

---

## Changelog

| Дата | Изменение |
|------|-----------|
| 2026-08-29 | **Decision-making-focus cell sourced via priority_setting.** `technique.priority_setting` accepted (NHS England line managers expectations + NHS Elect Time Management & Productivity Programme + Mayo Clinic Research mindful single-tasking). Brief one-task commitment (write one priority, set rest aside, close). Next = `need.transition.prepare`. |
| 2026-08-29 | **Creativity-open cell sourced via creative_prompt.** `technique.creative_prompt` accepted (Mayo Clinic Press art and health + Mayo Clinic stress relievers sketching + Greater Manchester Mental Health NHS Arts for Good Health). Brief one-line micro-creativity (draw one line, do not erase, stop). Next = `need.decision_making.focus`. |
| 2026-08-29 | **Connection-connect cell sourced via connection_action.** `technique.connection_action` accepted (NHS Essex ICB Looking after your mental health + Liu et al. 2025 systematic review on behavioral activation for social connection + Laidlaw et al. 2020 tele-delivered behavioral activation for connectedness). One short message / honest question / brief check-in to someone you have not reached. Next = `need.creativity.open`. |
| 2026-08-29 | **Self-connection-reflect cell sourced via journaling.** `technique.journaling` accepted (NHS Lanarkshire Writing for Wellbeing + CUH NHS Write Your Self + Greater Good Science Center Expressive Writing). Brief three-sentence unedited private writing. Next = `need.connection.connect`. |
| 2026-08-29 | **Emotional-awareness-reflect cell sourced via self_check_in.** `technique.self_check_in` accepted (Greater Good Science Center Naming Your Emotions + NHS Lothian Emotion Workbook + Torre & Lieberman 2018 affect labeling + Nook et al. 2022 timing/intensity caution). One-word feeling + body-spot check-in. Next = `need.self_connection.reflect`. |
| 2026-08-29 | **Motivation-activate cell sourced via micro_action.** `technique.micro_action` accepted (NHS ELFT behavioural activation + Mayo Clinic Anxiety Coach depression behavioral activation + Psychology Tools behavioral activation). Brief two-minute immediate action. Next = `need.emotional_awareness.reflect`. |
| 2026-08-29 | **Sleep-discipline cell sourced via sleep_discipline.** `technique.sleep_discipline` accepted (Mayo Clinic sleep tips + Mayo Clinic insomnia CBT-I + NHS inform sleep hygiene). Fixed latest bedtime rule for 7 consecutive days. Next = `need.motivation.activate`. |
| 2026-08-29 | **Sleep-prepare cell sourced via sleep.** `technique.sleep` accepted (NHS inform sleep hygiene + Mayo Clinic Health System sleep tips + NHS inform insomnia page). Brief pre-sleep meditation (soften jaw on out-breath). Next = `need.sleep.discipline`. |
| 2026-08-29 | **Rest cell sourced via relaxation.** `technique.relaxation` accepted (CUH NHS systematic focusing + Mayo Clinic relaxation techniques + NHS inform progressive muscle relaxation). Brief body-focused relaxation (heavy hands). Next = `need.sleep.prepare`. |
| 2026-08-29 | **Release cell sourced via body_release.** `technique.body_release` accepted (NHS inform + Mayo Clinic + NCBI StatPearls). Abbreviated single-area tension-release for shoulders. Next = `need.rest.downregulate`. |
| 2026-08-29 | **Confidence cell sourced via capability.** `technique.capability` accepted. `affirmation.self_trust` skipped (source gap). Next = `need.release.release`. |
| 2026-08-26 | **Clarity cell sourced via prompted_reflection.** Kernel = one question → own-words answer; no required conclusion. Not a journaling protocol. Probe rewritten. Next = `need.confidence.open`. |
| 2026-08-26 | **Grounding cell sourced via sensory_grounding.** Kernel = notice present sense data. 3-2-1 / 5-4-3-2-1 not the kernel. Probe rewritten. Next = `need.clarity.reflect`. |
| 2026-08-26 | **Energy cell sourced via mobility.** Preferred `energizing_breath` skipped. Probe not saved. No pranayama remap. `technique.mobility` accepted. Next = `need.grounding.stabilize`. |
| 2026-08-26 | **Focus cell sourced via focused_attention.** Preferred `box_breathing` stayed skipped. No breath substitute. `technique.focused_attention` accepted. Next = `need.energy.activate`. |
| 2026-08-26 | **First sourced cell.** `technique.extended_exhale` accepted. `need.calm.downregulate` covered. Next = `need.focus.focus`. |
| 2026-08-26 | **Research escalation closed.** Ladder = archive / non-blocking. Fill unfrozen. Lightweight provenance is the fill process. `box_breathing` skipped_for_now. [PRACTICE_LIBRARY_FILL_V1](./PRACTICE_LIBRARY_FILL_V1.md). |
| 2026-08-26 | **Targeted Safety Shortlist V1.** who_must_not_hold. Stop A. Joshi 2024 + Nivethitha 2017 selected. Wellness rejected. Next = Targeted Safety Ingest. [PRACTICE_TECHNIQUE_TARGETED_SAFETY_SHORTLIST_V1](./PRACTICE_TECHNIQUE_TARGETED_SAFETY_SHORTLIST_V1.md). |
| 2026-08-26 | **Safety Review V1.** S-B2 locked. Overall `insufficient_safety`. Not canon. Next = owner decides. [PRACTICE_TECHNIQUE_SAFETY_REVIEW_V1](./PRACTICE_TECHNIQUE_SAFETY_REVIEW_V1.md). |
| 2026-08-25 | **Normalization V1.1.** Axes: hold required, equal_count common_parameter. Overall `normalize_one` candidate. Landscape remapped. Next = Safety Review. [PRACTICE_TECHNIQUE_NORMALIZATION_V1_1](./PRACTICE_TECHNIQUE_NORMALIZATION_V1_1.md). |
| 2026-08-25 | **Targeted Ingest V1.** Two resolution loci. Square vs 5:5 unmerged. 4-4-6-2 is label observation, not variant. Next = Normalization V1.1. [PRACTICE_TECHNIQUE_TARGETED_INGEST_V1](./PRACTICE_TECHNIQUE_TARGETED_INGEST_V1.md). |
| 2026-08-25 | **Targeted Shortlist V1.** Post-exhale hold identity. Definition + contrast selected; variant not found in preferred class. Next = targeted ingest → Normalization V1.1. [PRACTICE_TECHNIQUE_TARGETED_SHORTLIST_V1](./PRACTICE_TECHNIQUE_TARGETED_SHORTLIST_V1.md). |
| 2026-08-25 | **Normalization V1.** Decision `insufficient_evidence`. Research question: post-exhale hold identity. [PRACTICE_TECHNIQUE_NORMALIZATION_V1](./PRACTICE_TECHNIQUE_NORMALIZATION_V1.md). |
| 2026-08-25 | **Ingest V1.** Three evidence records for equal_count selected loci. Not kernel, not canon. [PRACTICE_TECHNIQUE_INGEST_V1](./PRACTICE_TECHNIQUE_INGEST_V1.md). |
| 2026-08-25 | **Shortlist V1.** Vertical slice `equal_count_breath`. Selected = ingest permission, not canon. [PRACTICE_TECHNIQUE_SHORTLIST_V1](./PRACTICE_TECHNIQUE_SHORTLIST_V1.md). |
| 2026-08-25 | **Shortlist Criteria V1.** Gates C1–C9. Shortlist still closed. technique_id only at canonical. [PRACTICE_TECHNIQUE_SHORTLIST_CRITERIA_V1](./PRACTICE_TECHNIQUE_SHORTLIST_CRITERIA_V1.md). |
| 2026-08-25 | **Landscape V1.** Four class maps; shortlist closed; technique canon still empty. Next = selection criteria, not ingest. [PRACTICE_TECHNIQUE_LANDSCAPE_V1](./PRACTICE_TECHNIQUE_LANDSCAPE_V1.md). |
| 2026-08-25 | **Fill frozen.** Audio vs text cancelled. 133 items = llm_provisional. First 11 = architecture probes. Next = [PRACTICE_TECHNIQUE_PROVENANCE_V1](./PRACTICE_TECHNIQUE_PROVENANCE_V1.md). |
| 2026-08-25 | P1 density context: 44 siblings, `work` ↔ `evening`. First = `practice.extended_exhale.003`. Sleep/evening seeds flip to `work`. Next = audio vs text. |
| 2026-08-25 | P1 density EN locale: `locales.en` + `outcome_label.en` on all 89 items. `ru` kept. `meditation.sleep` EN has no `sleep`. Next = other context (`work` vs `evening`). |
| 2026-08-25 | P1 density (ledger P0 type order): 44 siblings. First = `practice.extended_exhale.002` (duration 5) on `need.calm.downregulate`. Sleep/evening now-jobs → audio+guided. Discipline → 14 days. P1 types (42) not attached — contract `form_ok`. Next = EN locale. |
| 2026-08-25 | P0 type-spine fill (ledger order): 19 remaining P0 types. First empty type was `practice.mobility` → `need.energy.activate`. `meditation.body_scan.001` listed only on `need.self_connection.reflect`, not recovery. P0 type spine complete (44/44). Next = P1 density. |
| 2026-08-25 | P0 seed #26 (ledger order): `need.habit_change.prepare` → `discipline.consistency_challenge.002`. Same type as #22 does not share coverage. P0 need cells complete (26/26). Next = remaining empty P0 type_spine types (19). |
| 2026-08-25 | P0 seed #25 (ledger order): `need.presence.stabilize` → `meditation.mindfulness.001`. Overlapping `scattered` / `stabilize` do not close focus/grounding/transition/self_control. Next empty = `need.habit_change.prepare`. |
| 2026-08-25 | P0 seed #24 (ledger order): `need.reset.release` → `practice.digital_pause.001`. Overlapping `stuck` / `release` do not close release/motivation/creativity/habit_change/detachment. Next empty = `need.presence.stabilize`. |
| 2026-08-25 | P0 seed #23 (ledger order): `need.simplicity.release` → `discipline.reduction.001`. Overlapping `overstimulated` / `release` do not close detachment/rest/calm/reset. Next empty = `need.reset.release`. |
| 2026-08-25 | P0 seed #22 (ledger order): `need.consistency.prepare` → `discipline.consistency_challenge.001`. Overlapping `scattered` / `prepare` do not close transition/focus/habit_change. Next empty = `need.simplicity.release`. |
| 2026-08-25 | P0 seed #21 (ledger order): `need.detachment.release` → `discipline.abstinence.001`. Overlapping `overstimulated` / `release` do not close calm/rest/simplicity/reset. Next empty = `need.consistency.prepare`. |
| 2026-08-25 | P0 seed #20 (ledger order): `need.self_control.stabilize` → `discipline.attention_discipline.001`. Overlapping `restless` / `stabilize` do not close sleep/discipline/grounding/presence. Next empty = `need.detachment.release`. |
| 2026-08-25 | P0 seed #19 (ledger order): `need.discipline.prepare` → `discipline.routine_commitment.001`. Overlapping `restless` / `prepare` do not close sleep/self_control/transition/consistency. Next empty = `need.self_control.stabilize`. |
| 2026-08-25 | P0 seed #18 (ledger order): `need.recovery.recover` → `practice.progressive_relaxation.001`. Overlapping `tense` / `low_energy` do not close grounding/calm/energy/motivation. Next empty = `need.discipline.prepare`. |
| 2026-08-25 | P0 seed #17 (ledger order): `need.transition.prepare` → `practice.transition_ritual.001`. Overlapping `scattered` / `prepare` do not close focus/grounding/consistency. Next empty = `need.recovery.recover`. |
| 2026-08-25 | P0 seed #16 (ledger order): `need.decision_making.focus` → `practice.priority_setting.001`. Overlapping `uncertain` / `focus` do not close clarity/confidence/box_breathing. Next empty = `need.transition.prepare`. |
| 2026-08-25 | P0 seed #15 (ledger order): `need.creativity.open` → `practice.creative_prompt.001`. Overlapping `stuck` does not close release/motivation/reset. Next empty = `need.decision_making.focus`. |
| 2026-08-25 | P0 seed #14 (ledger order): `need.connection.connect` → `practice.connection_action.001`. Overlapping `disconnected` does not close grounding/self_connection. Next empty = `need.creativity.open`. |
| 2026-08-25 | P0 seed #13 (ledger order): `need.self_connection.reflect` → `practice.journaling.001`. Overlapping `disconnected` does not close grounding/connection. Next empty = `need.connection.connect`. |
| 2026-08-25 | P0 seed #12 (ledger order): `need.emotional_awareness.reflect` → `practice.self_check_in.001`. Overlapping `emotionally_heavy` does not close release. Next empty = `need.self_connection.reflect`. |
| 2026-08-25 | P0 seed #11 (ledger order): `need.motivation.activate` → `practice.micro_action.001`. Overlapping `stuck` / `low_energy` do not close release/energy/recovery. Next empty = `need.emotional_awareness.reflect`. |
| 2026-08-25 | P0 seed #10 (ledger order): `need.sleep.discipline` → `discipline.sleep_discipline.001`. Same `purpose=sleep` as `meditation.sleep.001` does not share coverage. Period `duration_days`, not session minutes. Next empty = `need.motivation.activate`. |
| 2026-08-25 | P0 seed #9 (ledger order): `need.sleep.prepare` → `meditation.sleep.001`. Same `purpose=sleep` does not close `need.sleep.discipline`. Next empty = `need.sleep.discipline`. |
| 2026-08-25 | P0 seed #8 (ledger order): `need.rest.downregulate` → `meditation.relaxation.001`. Overlapping `overstimulated` does not close sleep/detachment/simplicity or calm. Next empty = `need.sleep.prepare`. |
| 2026-08-25 | P0 seed #7 (ledger order): `need.release.release` → `practice.body_release.001`. Overlapping `stuck` / `emotionally_heavy` do not close motivation/reset/emotional_awareness. Next empty = `need.rest.downregulate`. |
| 2026-08-25 | P0 seed #6 (ledger order): `need.confidence.open` → `affirmation.capability.001`. Overlapping `uncertain` does not close decision_making. Next empty = `need.release.release`. |
| 2026-08-25 | P0 seed #5 (ledger order): `need.clarity.reflect` → `practice.prompted_reflection.001`. Overlapping `uncertain` does not close confidence/decision_making. Next empty = `need.confidence.open`. |
| 2026-08-25 | P0 seed #4 (ledger order): `need.energy.activate` → `practice.energizing_breath.001`. Overlapping `low_energy` does not close motivation/recovery. Next empty = `need.clarity.reflect`. |
| 2026-08-25 | P0 seed #3 (ledger order): `need.focus.focus` → `practice.box_breathing.001`. Overlapping `scattered` does not close grounding. Next empty = `need.energy.activate`. |
| 2026-08-25 | P0 seed #2 (ledger order): `need.calm.downregulate` → `practice.extended_exhale.001`. Seed closes exactly one cell; retrieval tags do not auto-close others. |
| 2026-08-25 | First P0 seed: `need.grounding.stabilize` → `practice.sensory_grounding.001` (draft). 25 cells remain empty. No batch-fill. |
| 2026-08-25 | v1.0 ACCEPTED — 26 P0 need cells, type spine, coverage-first law, empty ledger |
