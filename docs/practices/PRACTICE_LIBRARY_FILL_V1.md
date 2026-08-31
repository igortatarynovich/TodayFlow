# Practice Library Fill v1

**Статус:** `ACCEPTED` — единственный **active** процесс наполнения библиотеки.  
**Версия:** 1.0 (2026-08-26).  
**Владелец:** Product.  
**Taxonomy:** [PRACTICE_CONTENT_TAXONOMY_V1.md](./PRACTICE_CONTENT_TAXONOMY_V1.md) — классы / types / атрибуты **не** меняются этим файлом.  
**Coverage:** [PRACTICE_CONTENT_COVERAGE_V1.md](./PRACTICE_CONTENT_COVERAGE_V1.md) — какие ячейки закрывать.  
**Item:** [`content_item_contract_v1.json`](../../DATA/reference/practice/content_item_contract_v1.json).  
**Registry:** [`technique_canon_v1.json`](../../DATA/reference/practice/technique_canon_v1.json).  
**Archive:** [PRACTICE_TECHNIQUE_RESEARCH_ARCHIVE_V1.md](./PRACTICE_TECHNIQUE_RESEARCH_ARCHIVE_V1.md).

**Это:** как принимать или пропускать технику и писать Content Item.  
**Это не:** landscape / shortlist / ingest / normalization / safety-review лестница. Та лестница **не** блокирует fill.

Meaning → Need → Retrieval → Item **без изменения**. Meaning не знает `item_id` / `technique_id`.

---

## Architecture impact

- **SoT before:** fill ждал Canonical Technique через Landscape → Shortlist → Ingest → Normalization → Targeted* → Safety Review. Один type (`box_breathing`) занял десять passes. Fill frozen.
- **SoT after:** fill = lightweight provenance на одну технику. Research ledgers — archive, non-blocking. `box_breathing` = `skipped_for_now`. Следующая работа = library fill с `need.calm.downregulate`, не Safety Review V1.1. 133 items остаются `llm_provisional`, пока не переписаны.
- **Public contract changed?** no
- **Migration required?** no runtime
- **Canon updated?** yes — этот файл · provenance pointer · technique contract · coverage next_pass · tracker
- **Backward compatible?** yes для клиентов. Несовместимо с продолжением research escalation как unlock fill.

---

## 0. Закон

1. **LLM не источник метода.** Несколько качественных источников подтверждают, что метод существует. Не диссертация о термине.
2. **Одна запись на технику.** Не отдельный landscape / ingest / normalization ledger на каждый type.
3. **Спор → skip.** Если начинается эскалация уровня box breathing — `skipped`, другой подходящий type для need.
4. **Safety только где материально нужно.** Задержки дыхания — да; journaling — обычно нет.
5. **Skip ≠ запрет продукта навсегда.** `skipped_for_now` можно открыть позже. Не продолжать ту же лестницу.
6. **Существование ≠ efficacy.** `allowed_claims[]` по умолчанию пуст.
7. **Источник подтверждает технику.** Техника не обязана оправдывать старый probe. LLM items — расходный материал; taxonomy / needs — каркас.

---

## 1. Запись техники

```text
technique_id
content_class / type
canonical_description     своими словами
source_refs[]             откуда взяли
safety_notes[]            если реально нужны
allowed_claims[]          обычно пусто
status                    accepted | skipped
```

`technique_id` на item — только если `status = accepted`. `skipped` в registry не аттестует probe.

---

## 2. Fill одной ячейки

Для каждой ячейки, которую fill ещё не закрыл sourced-техникой:

1. Взять preferred type ячейки.
2. Проверить, что нормальная техника этого type существует (несколько надёжных источников).
3. Если ясно — `accepted`: ядро своими словами + ссылки.
4. Если есть очевидный safety-вопрос — коротко проверить и записать `safety_notes[]`.
5. Если начинается спор — `skipped` / `skipped_for_now`. Вернуться к самой need и взять другой **уже существующий** taxonomy type. Не спасать skipped type похожей заменой того же семейства. Если подходящего type нет — ячейка остаётся uncovered; не изобретать технику ради покрытия.
6. Написать Content Item (expression принятой техники).
7. Validator → следующая ячейка.

Целевой масштаб: десятки техник за рабочий проход.

**Сейчас:** `extended_exhale`, `focused_attention`, `mobility`, `sensory_grounding`, `prompted_reflection`, `capability`, `body_release`, `relaxation`, `sleep`, `sleep_discipline`, `micro_action`, `self_check_in`, `journaling`, `connection_action`, `creative_prompt`, `priority_setting`, `transition_ritual`, `progressive_relaxation`, `routine_commitment`, `attention_discipline`, `acceptance`, `consistency_challenge`, `reduction`, `digital_pause`, `mindfulness`, `intention_setting`, `environment_reset`, `free_writing`, `morning_ritual`, `evening_ritual`, `breath_awareness`, `body_scan`, `open_awareness`, `grounding`, `letting_go`, `reflection_meditation`, `agency`, `relationship`, `digital_limit`, `consumption_limit`, `paced_breathing`, `physiological_sigh`, `practice_grounding`, `stretching`, `mindful_movement`, `walking`, `shaking_release` = `accepted`. Все 26 P0 need cells sourced. P0 type coverage: 40/44 P0 spine types sourced (оставшиеся 4 — skipped). P1 type coverage: 7/42 sourced; `practice.body_scan` skipped (`family_collapse` с `meditation.body_scan`). `box_breathing`, `energizing_breath`, `abstinence`, `self_trust` и `practice.body_scan` = `skipped_for_now`. Content Library: 118 активных content-library items + legacy catalog. Следующий P1 type: `practice.gratitude`. Не открывать Safety Review V1.1.

---

## 3. Запрещено

- Считать Landscape / Shortlist / Ingest / Normalization / Safety Review обязательной лестницей fill.
- Продолжать targeted safety / who_must_not_hold на `box_breathing`.
- Писать `technique_id` на item со `status = skipped`.
- Выдавать `item_id` / `technique_id` из Meaning.
- Заполнять `allowed_claims` из традиции или числа источников.

---

## Changelog

| Дата | Изменение |
|------|-----------|
| 2026-08-31 | P1 type `practice.shaking_release` sourced via `technique.shaking_release` (Cardiff and Vale UHB NHS Wales sedentary-worker micro-pause + West Suffolk NHS loosening + UMass Memorial workstation arm shake). Brief voluntary shake-out: drop arms, point hands to the floor, gently shake wrists/hands a few seconds, stop. Distinct from body_release (tense-hold-release), mobility, stretching, mindful_movement, and TRE. `practice.shaking_release.001` active. P1 coverage: 7/42 sourced, 1 P1 skipped. Next: `practice.gratitude`. |
| 2026-08-31 | P1 type `practice.walking` sourced via `technique.walking` (NHS sit less + Better Health get active + NHS England corridor/2-minute walk). Brief locomotion sit-break: stand, walk a short comfortable distance, stop. Distinct from mobility, mindful_movement, and walking_meditation. `practice.walking.001` active. P1 coverage: 6/42 sourced, 1 P1 skipped. Next: `practice.shaking_release`. |
| 2026-08-31 | P1 type `practice.mindful_movement` sourced via `technique.mindful_movement` (Sussex Mindfulness Centre NHS + UHDB NHS + RUH Bath PHY051). Brief movement-with-attention: sit or stand, make one slow comfortable movement (raise/lower arms or shift weight), keep attention on the moving body, return when it wanders. Distinct from mobility, stretching, sitting mindfulness, and walking. `practice.mindful_movement.001` active. P1 coverage: 5/42 sourced, 1 P1 skipped. Next: `practice.walking`. |
| 2026-08-31 | P1 type `practice.body_scan` skipped (`family_collapse`): sequential body observation is already `technique.body_scan` (meditation); no distinct practice-class kernel. Next P1 type `practice.stretching` sourced via `technique.stretching` (NHS Flexibility exercises + NHS Sitting exercises). Brief hold-stretch: sit upright, tilt ear toward shoulder (or open the chest), hold a few seconds without bouncing. Distinct from mobility (no hold) and PMR (tense-then-release). `practice.stretching.001` active. P1 coverage: 4/42 sourced, 1 P1 skipped. Next: `practice.mindful_movement`. |
| 2026-08-31 | P1 type `practice.grounding` sourced via `technique.practice_grounding` (Royal Berkshire NHS + Singh et al. 2003 Soles of the Feet). Brief somatic action: sit or stand, press both feet firmly into the floor, notice pressure/weight in the soles. Distinct from `sensory_grounding` and `meditation.grounding`. Not a treatment. `practice.grounding.001` active. P1 coverage: 3/42. Next P1 type: `practice.body_scan`. |
| 2026-08-31 | P1 type `practice.physiological_sigh` sourced via `technique.physiological_sigh` (Vlemincx et al. 2010 + KU Leuven resetter hypothesis + instructed-sigh relief). Brief breath practice: two consecutive nasal inhales (second smaller), then a long exhale through the mouth; repeat a few times comfortably. Not a treatment or anxiety/mood claim. `practice.physiological_sigh.001` active. P1 coverage: 2/42. Next P1 type: `practice.grounding`. |
| 2026-08-31 | P1 type coverage started. `practice.paced_breathing` sourced via `technique.paced_breathing` (NHS Bradford District Care Trust Ready to Relate + Harvard Health). Brief breath practice: slow steady pace (~5–6 breaths/min), inhale through nose, exhale slightly longer, no hold. Not a treatment or anxiety/blood-pressure claim. `practice.paced_breathing.001` active. P1 coverage: 1/42. Next P1 type: `practice.physiological_sigh`. |
| 2026-08-31 | Content Library wired to runtime hub. `content_library_selection_v1.py` implemented: active/accepted items mapped to `PracticeResponse` shape and merged into `GET /practices`; `GET /practices/{id}` resolves content-library `item_id`s; deterministic `GET /practices/select` selector is live. Hub catalog grows from 47 legacy free practices to 47 + 111 content-library items. No new technique sourcing; no P0 coverage change. Next: density pass or skipped-type reassessment. |
| 2026-08-30 | P0 spine type `consumption_limit` sourced via `technique.consumption_limit` (The Independent 48-hour rule + Shah et al. 2023 planning prompts). Brief discipline rule: for a set streak (7/14 days), defer any unplanned purchase not on today's plan; put it off and review later. Not a treatment or savings guarantee. `discipline.consumption_limit.001/002/003` activated. All non-skipped P0 spine types now sourced. Next: decide on P1 type coverage / density / skipped reassessment. |
| 2026-08-30 | P0 spine type `digital_limit` sourced via `technique.digital_limit` (NHS London Waiting Room + Google Android Digital Wellbeing). Brief discipline rule: set a bounded, recurring daily period (e.g., one hour) without opening feeds/social media, using a timer or device tool; follow for a short streak (7/14 days). Not a treatment or screen-time reduction guarantee. `discipline.digital_limit.001/002/003` activated. Next non-skipped P0 spine type: `discipline.consumption_limit`. |
| 2026-08-30 | P0 spine type `relationship` sourced via `technique.relationship` (Stinson et al. 2011 + Cohen & Sherman 2014). Brief affirmation: state a first-person statement that one can take one warm step toward another person (e.g., 'I can take one warm step toward a person'), spoken once or twice. Not a treatment or connection/acceptance guarantee. `affirmation.relationship.001/002/003` activated. Next non-skipped P0 spine type: `discipline.digital_limit`. |
| 2026-08-30 | P0 spine type `agency` sourced via `technique.agency` (Cohen & Sherman 2014 + Steele 1988). Brief affirmation: state a first-person statement that one chooses the next small step (e.g., 'I choose the next small step'), spoken once or twice, then optionally begin the step. Not a treatment or success/motivation guarantee. `affirmation.agency.001/002/003` activated. Next non-skipped P0 spine type: `affirmation.relationship`. |
| 2026-08-30 | P0 spine type `reflection_meditation` sourced via `technique.reflection_meditation` (NHS Scotland MBSR Three-Minute Breathing Space + Mindful.net). Brief practice: sit, ask one open question about present experience (e.g., 'What is my experience right now?'), do not answer immediately, stay with it for three breaths, then note one word. Not a treatment or clarity/insight guarantee. `meditation.reflection_meditation.001/002/003` activated. Next non-skipped P0 spine type: `affirmation.agency`. |
| 2026-08-30 | P0 spine type `letting_go` sourced via `technique.letting_go` (NHS inform + Allina Health). Brief practice: notice a small area of held tension (e.g., shoulders); on each out-breath, deliberately allow it to drop or soften a little. Not a treatment or relaxation guarantee. `meditation.letting_go.001/002/003` activated. Next non-skipped P0 spine type: `meditation.reflection_meditation`. |
| 2026-08-30 | P0 spine type `grounding` sourced via `technique.grounding` (NHS inform + Royal Berkshire NHS). Brief practice: sit and bring attention to physical contact points (weight on seat, feet on floor, back against chair), noticing contact and support for a few breaths without trying to change state. Not a treatment for anxiety, panic, trauma, or dissociation. `meditation.grounding.001/002/003` activated. Next non-skipped P0 spine type: `meditation.letting_go`. |
| 2026-08-30 | P0 spine type `open_awareness` sourced via `technique.open_awareness` (Lutz et al. 2008 + Mindful.net). Brief practice: sit, lightly notice or name whatever is present in one word (thought, sound, sensation, emotion) without explaining or judging, return to open awareness. Not a treatment or emotional-regulation guarantee. `meditation.open_awareness.001/002/003` activated. Next non-skipped P0 spine type: `meditation.grounding`. |
| 2026-08-30 | P0 spine type `body_scan` sourced via `technique.body_scan` (NHS Scotland Right Decisions + Guy's and St Thomas' NHS MBSR exercises). Brief practice: sit, move attention sequentially through a few body areas (feet/hands/face), notice sensations without moving or changing. Not a treatment or relaxation guarantee. `meditation.body_scan.001/002/003` activated. Next non-skipped P0 spine type: `meditation.open_awareness`. |
| 2026-08-30 | P0 spine type `breath_awareness` sourced via `technique.breath_awareness` (NHS Mindfulness + Guy's and St Thomas' NHS MBSR exercises). Brief practice: sit, bring attention to natural sensations of breathing without controlling it, return when mind wanders. Not a treatment or relaxation guarantee. `meditation.breath_awareness.001/002/003` activated. Next non-skipped P0 spine type: `meditation.body_scan`. |
| 2026-08-30 | P0 spine type `evening_ritual` sourced via `technique.evening_ritual` (NHS Every Mind Matters + Imperial NHS sleep hygiene). Brief practice: dim light, put device out of reach, sit, take a few slow out-breaths as a wind-down transition. Not a sleep-induction or treatment. `practice.evening_ritual.001/002/003` activated. Next non-skipped P0 spine type: `meditation.breath_awareness`. |
| 2026-08-30 | P0 spine type `morning_ritual` sourced via `technique.morning_ritual` (NHS Every Mind Matters sleep + activity guidance + Sonnentag & Kühnel 2016). Brief practice: after waking, do one or two simple physical actions (water/light/movement), name one task/day direction, and begin. No sleep/productivity/mental-health claims. `practice.morning_ritual.001/002/003` activated. Next non-skipped P0 spine type: `practice.evening_ritual`. |
| 2026-08-30 | P0 spine type `free_writing` sourced via `technique.free_writing` (Peter Elbow 1973 + MIT Writing Process). Brief practice: write continuously for a set time (2/5 minutes) without stopping, editing, or erasing. Not a therapeutic or clinical intervention. `practice.free_writing.001/002/003` activated. Next non-skipped P0 spine type: `practice.morning_ritual`. |
| 2026-08-30 | P0 spine type `environment_reset` sourced via `technique.environment_reset` (Mind.org.uk + Leicestershire Partnership NHS Trust). Brief practice: reset immediate physical environment by removing/relocating/tidying one object or clearing a surface before next task. No productivity/stress-treatment claims. `practice.environment_reset.001/002/003` activated. Next non-skipped P0 spine type: `practice.free_writing`. |
| 2026-08-30 | P0 spine type `intention_setting` sourced via `technique.intention_setting` (Gollwitzer 1999 + 1993). Brief practice: pre-formulate a single concrete aim for a specific upcoming period/action. No outcome/behavior-change guarantees. `practice.intention_setting.001/002/003` activated. Next non-skipped P0 spine type: `practice.environment_reset`. |
| 2026-08-30 | Habit_change-prepare cell sourced via `consistency_challenge` (already accepted). `discipline.consistency_challenge.002` activated: seven-day replacement rule — when the old pull comes, do one new short action in its place. All 26 P0 need cells sourced. Next: finalize skipped types or non-P0 cells. |
| 2026-08-30 | Presence-stabilize cell sourced via `mindfulness`. `technique.mindfulness` accepted from Oxford Mindfulness definition + NHS mindfulness + Bishop et al. (2004). Brief practice: direct attention to present-moment experience (sounds/sensations/breath), notice without judgment, return when mind wanders. No treatment claims or mind-emptying. Next = `need.habit_change.prepare`. |
| 2026-08-30 | Reset-release cell sourced via `digital_pause`. `technique.digital_pause` accepted from NHS Every Mind Matters screen breaks + NHS Employers DSE guidance. Brief action: move device out of reach or face down and do not interact for a short bounded period (e.g., 2/5 minutes). No nervous-system reset or wellness claims. Next = `need.presence.stabilize`. |
| 2026-08-30 | Simplicity-release cell sourced via `reduction`. `technique.reduction` accepted from Paas & van Merriënboer (2020) cognitive-load stimuli reduction + RACGP clutter/cognitive resources + Sweller et al. (2019) extraneous attention-capturing stimuli. Brief discipline rule: select one unnecessary or attention-competing thing and remove/defer it for a short period (e.g., 7/14 days). No decluttering philosophy or wellness claims. Next = `need.reset.release`. |
| 2026-08-30 | Consistency-prepare cell sourced via `consistency_challenge`. `technique.consistency_challenge` accepted from Lally et al. (2010) daily repetition in context + Lally & Gardner (2012) making health habitual + Scientific American streak motivation. Brief short streak challenge (seven/fourteen days; one small action; miss resets count; visible progress). Next = `need.simplicity.release`. |
| 2026-08-30 | Detachment-release cell sourced via `acceptance` (alt); primary `abstinence` skipped for now. `technique.acceptance` accepted from NICE NG193 ACT + NHS Scotland The Matrix ACT + Psychology Tools ACT overview. Brief notice-allow-don't-push-away practice (three breaths). `technique.abstinence` skipped (source gap: no general short-term abstinence method; evidence is substance-specific). Next = `need.consistency.prepare`. |
| 2026-08-30 | Self-control-stabilize cell sourced via `attention_discipline`. `technique.attention_discipline` accepted from APA multitasking switching costs + Harvard Health monotasking + Leeds Teaching Hospitals NHS Trust digital wellbeing. Brief one-open-feed rule (close extra feeds, one stream at a time). Next = `need.detachment.release`. |
| 2026-08-30 | Discipline-prepare cell sourced via `routine_commitment`. `technique.routine_commitment` accepted from NICE PH49 small routine changes + Lally & Gardner (2012) making health habitual + Keller et al. (2021) routine/time cue planning. Brief repeated action at same time/cue for a short streak (e.g. 7 days). Next = `need.self_control.stabilize`. |
| 2026-08-30 | Recovery-recover cell sourced via `progressive_relaxation`. `technique.progressive_relaxation` accepted from NHS inform progressive muscle relaxation + Mayo Clinic relaxation techniques + VA Whole Health Library PMR. Brief localized tense-and-release (fists on inhale, open on exhale, three times). Next = `need.discipline.prepare`. |
| 2026-08-30 | Transition-prepare cell sourced via `transition_ritual`. `technique.transition_ritual` accepted from Leroy (2009) attention residue + Leroy & Glomb (2018) ready-to-resume plan + NHS Every Mind Matters working-from-home breaks. Brief close-stand-switch practice (close what you were doing, stand, three steps, sit for next). Next = `need.recovery.recover`. |
| 2026-08-29 | Decision-making-focus cell sourced via `priority_setting`. `technique.priority_setting` accepted from NHS England line managers expectations + NHS Elect Time Management & Productivity Programme + Mayo Clinic Research mindful single-tasking. Brief one-task commitment (write one priority, set rest aside, close). Next = `need.transition.prepare`. |
| 2026-08-29 | Creativity-open cell sourced via `creative_prompt`. `technique.creative_prompt` accepted from Mayo Clinic Press art and health + Mayo Clinic stress relievers sketching + Greater Manchester Mental Health NHS Arts for Good Health. Brief one-line micro-creativity (draw one line, do not erase, stop). Next = `need.decision_making.focus`. |
| 2026-08-29 | Connection-connect cell sourced via `connection_action`. `technique.connection_action` accepted from NHS Essex ICB Looking after your mental health + Liu et al. (2025) systematic review on behavioral activation for social connection + Laidlaw et al. (2020) tele-delivered behavioral activation for connectedness. One short message / honest question / brief check-in to someone you have not reached. Next = `need.creativity.open`. |
| 2026-08-29 | Self-connection-reflect cell sourced via `journaling`. `technique.journaling` accepted from NHS Lanarkshire Writing for Wellbeing + CUH NHS Write Your Self + Greater Good Science Center Expressive Writing. Brief three-sentence unedited private writing. Next = `need.connection.connect`. |
| 2026-08-29 | Emotional-awareness-reflect cell sourced via `self_check_in`. `technique.self_check_in` accepted from Greater Good Science Center Naming Your Emotions + NHS Lothian Emotion Workbook + Torre & Lieberman (2018) affect labeling + Nook et al. (2022) timing/intensity caution. One-word feeling + body spot check-in. Next = `need.self_connection.reflect`. |
| 2026-08-29 | Motivation-activate cell sourced via `micro_action`. `technique.micro_action` accepted from NHS ELFT behavioural activation + Mayo Clinic Anxiety Coach depression behavioral activation + Psychology Tools behavioral activation. Brief two-minute immediate action. Next = `need.emotional_awareness.reflect`. |
| 2026-08-29 | Sleep-discipline cell sourced via `sleep_discipline`. `technique.sleep_discipline` accepted from Mayo Clinic sleep tips + Mayo Clinic insomnia CBT-I + NHS inform sleep hygiene. Fixed latest bedtime rule for 7 consecutive days. Next = `need.motivation.activate`. |
| 2026-08-29 | Sleep-prepare cell sourced via `sleep`. `technique.sleep` accepted from NHS inform sleep hygiene + Mayo Clinic Health System sleep tips + NHS inform insomnia page. Brief pre-sleep meditation (soften jaw on out-breath). Next = `need.sleep.discipline`. |
| 2026-08-29 | Rest cell sourced via `relaxation`. `technique.relaxation` accepted from CUH NHS systematic focusing + Mayo Clinic relaxation techniques + NHS inform progressive muscle relaxation. Brief body-focused relaxation (heavy hands). Next = `need.sleep.prepare`. |
| 2026-08-29 | Release cell sourced via `body_release`. `technique.body_release` accepted from NHS inform progressive muscle relaxation + Mayo Clinic + NCBI StatPearls. Abbreviated single-area tension-release (shoulders). Next = `need.rest.downregulate`. |
| 2026-08-29 | Confidence cell sourced via `capability`. `technique.capability` accepted from CBT/REBT rational coping-statement method + NHS inform anxiety guide. `affirmation.self_trust` skipped (source gap). Next = `need.release.release`. |
| 2026-08-26 | Source confirms the technique; the technique need not justify an old probe. LLM items are disposable. |
| 2026-08-26 | Skip preferred type → return to the need, pick another existing type, or leave uncovered. Do not invent a similar replacement. |
| 2026-08-26 | v1.0 ACCEPTED — research escalation retired; lightweight fill is the active process; box_breathing skipped_for_now |
