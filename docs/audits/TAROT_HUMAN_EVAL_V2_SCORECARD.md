# Tarot Human Eval v2 — scorecard

Ответь на три вопроса по каждому кейсу: `yes` · `partial` · `no`.

| id | question | symbols? | answered? | would pay? | notes |
|----|----------|----------|-----------|------------|-------|
| `hv2_work_direction_three` | Какое направление в работе сейчас заслуживает внимания? | yes | yes | yes | Owner liked direction — person sees themselves. Flag antithesis («не кричит, а г |
| `hv2_ds_choice_work_leave_or_stay` | Стоит ли менять работу — или сначала что-то прояснить здесь? |  |  |  | ⬜ score |
| `hv2_ds_work_decision_burnout_minors` | Я выгораю на работе — что важно учесть перед сменой роли? |  |  |  | ⬜ score |
| `hv2_ds_money_decision_calm` | Какой взгляд поможет принять решение о деньгах спокойнее? |  |  |  | ⬜ score |
| `hv2_ds_conflict_colleague` | В чём корень конфликта с коллегой и как его не раздуть? |  |  |  | ⬜ score |
| `hv2_ds_direction_creative` | Куда мне двигаться дальше в творческом проекте? |  |  |  | ⬜ score |
| `hv2_ds_q1_cups_8_9_10_leave` | Стоит ли уходить из отношений, которые почти хороши, но внутри уже пусто |  |  |  | ⬜ score |
| `hv2_ds_relationship_state_three` | Что сейчас важно понять в отношениях с этим человеком? |  |  |  | ⬜ score |
| `hv2_ds_relationship_intent_other` | Что он думает обо мне после нашего разговора? |  |  |  | ⬜ score |
| `hv2_ds_open_reflection_one` | Что мне важно увидеть сейчас? |  |  |  | ⬜ score |
| `hv2_ds_q1_swords_8_9_10_anxiety` | Почему я чувствую себя в ловушке мыслей и что с этим делать? |  |  |  | ⬜ score |
| `hv2_ds_self_state_anxiety` | Почему мне так тревожно и тяжело внутри последние дни? |  |  |  | ⬜ score |
| `hv2_ds_timing_readiness_job` | Когда лучше менять работу — пора ли сейчас? |  |  |  | ⬜ score |

## How to score

1. Read `answer.symbols_overview` → `question_story` → `direct_answer` → `next_step` in the fixture.
2. Fill the three columns (or patch `human` on the case in JSON).
3. Optional voice flags: `antithesis_formula` · `sees_self` · `warmth_without_mush`.

