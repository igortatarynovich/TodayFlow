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

**Сейчас:** `extended_exhale`, `focused_attention`, `mobility`, `sensory_grounding`, `prompted_reflection`, `capability`, `body_release`, `relaxation`, `sleep`, `sleep_discipline`, `micro_action`, `self_check_in`, `journaling`, `connection_action`, `creative_prompt`, `priority_setting`, `transition_ritual`, `progressive_relaxation`, `routine_commitment` = `accepted`. Sourced 19/26. `box_breathing`, `energizing_breath` и `self_trust` = `skipped_for_now`. Следующая ячейка: `need.self_control.stabilize`. Не открывать Safety Review V1.1.

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
