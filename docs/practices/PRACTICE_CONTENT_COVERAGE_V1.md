# Practice Content Coverage v1

**Статус:** `ACCEPTED` — SoT fill-pass библиотеки.  
**Версия:** 1.0 (2026-08-25).  
**Владелец:** Product.  
**Ledger:** [`DATA/reference/practice/content_coverage_matrix_v1.json`](../../DATA/reference/practice/content_coverage_matrix_v1.json).  
**Parent:** [PRACTICE_CONTENT_TAXONOMY_V1.md](./PRACTICE_CONTENT_TAXONOMY_V1.md) §0.1 · §10.

**Это:** какие ячейки продукт обязан уметь закрыть **до** массовой генерации текста.  
**Это не:** тексты практик · runtime retrieval · screen need-чипы · cartesian product всех enum.

---

## Architecture impact

- **SoT before:** taxonomy locked types/purpose/state; fill implied as «написать items против vocab». Риск — плотность в одной технике (40 grounding) и дыры в purpose/direction/class.
- **SoT after:** fill = coverage-first. P0 = 25 need cells (один канонический `purpose × direction` на каждый purpose) + listed forms. Item = identity / retrieval / payload. Matrix status `empty` until seed items exist. Meaning still does not emit `item_id`. Preferred type in a cell is a **fill target**, not a meaning output.
- **Public contract changed?** no
- **Migration required?** no runtime. No Content Items in this pass.
- **Canon updated?** yes — this file · matrix JSON · item contract · empty library · taxonomy v1.1 · `_INDEX` · README · tracker
- **Backward compatible?** yes. Legacy `CONTENT/practices/*.json` untouched (P2 remap after P0).

---

## 0. Закон fill-pass

1. **Сначала покрытие, потом плотность.** Не писать второй item в закрытую ячейку, пока есть `empty` в P0.
2. **Не декартово произведение.** 25 purpose × 10 direction × 86 type — не план. План = need cells ниже.
3. **Ячейка = потребность продукта**, не «ещё одна карточка». Закрыта, когда есть ≥1 `active`/`draft` item, чьи retrieval-поля попадают в cell (purpose + direction + class/type формы).
4. **Preferred type — fill target.** Meaning по-прежнему эмитит только state → direction → purpose. Retrieval может выбрать alt form (другой class/type), если constraints так говорят.
5. **Один purpose — два job'а допустимы**, если class разный: «сейчас» (`practice`/`meditation`/`affirmation`) vs «на период» (`discipline`). Это не дубль grounding.

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
| `need.focus.focus` | focus | focus | scattered | practice / box_breathing | meditation / focused_attention | now |
| `need.energy.activate` | energy | activate | low_energy | practice / energizing_breath | practice / mobility | now |
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

1. 26 need cells — primary form, одна ячейка за раз.
2. Оставшиеся P0 types, у которых ещё `item_ids = []` (обычно alt, не взятые как primary).
3. Только потом P1 density.

Канон кодов: `type_spine[].phase` в ledger (сейчас **44 P0 / 42 P1**). Сводка в markdown не дублирует список — при расхождении ведёт JSON.

Один item может закрыть несколько cells, если retrieval-массивы это честно отражают. Не клеить extra purpose в title, чтобы «закрыть» две ячейки ложью.

---

## 4. Как закрывать ячейку

На один seed item:

1. Выбрать **пустую** P0 cell (не самую привычную технику).
2. Заполнить три группы ([taxonomy §10](./PRACTICE_CONTENT_TAXONOMY_V1.md#10-content-item--три-группы)).
3. `purpose` / `direction` / `input_state` / `content_class` / `type` совпадают с cell (или с alt form).
4. Duration: Today now-job ≤ 5 min, если cell не sleep/evening; discipline — `duration_days`, не минуты сессии.
5. Payload: `ru` обязателен. Без medical claims. Ritual = последовательность, не магия.
6. Записать `item_id` в `item_ids[]` ячейки ledger. Status cell → `seed` пока draft, `covered` когда item `active`.

Запрещено: генерировать payload без пустой P0 cell; закрывать cell только title без retrieval-полей; ставить `item_id` в meaning/prompt.

---

## 5. P1 / P2 (не сейчас)

| Phase | Что |
|-------|-----|
| P1 density | второй duration, другой context (`work` vs `evening`), audio, EN, оставшиеся types семейства |
| P1 variants | тот же purpose, другой direction (`need.focus.stabilize` и т. п.) — только после P0 |
| P2 remap | `CONTENT/practices/*.json`, C1.4 ascetics → items; не новые types |

---

## 6. Чтение матрицы

Ledger JSON:

- `need_cells[].status`: `empty` · `seed` · `covered`
- `need_cells[].item_ids`: сейчас `[]`
- `type_spine[]`: `phase` = `P0` \| `P1` \| `deferred`
- `gaps`: считается из status; до fill все P0 need cells = `empty`

Следующий рабочий шаг после этого документа: **seed items в empty P0 cells**, по одной ячейке, не пакетом «все grounding».

---

## Changelog

| Дата | Изменение |
|------|-----------|
| 2026-08-25 | v1.0 ACCEPTED — 26 P0 need cells, type spine, coverage-first law, empty ledger |
