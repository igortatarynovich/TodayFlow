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

**Сейчас:** `extended_exhale`, `focused_attention`, `mobility`, `sensory_grounding`, `prompted_reflection`, `capability`, `body_release`, `relaxation`, `sleep`, `sleep_discipline` = `accepted`. Sourced 10/26. `box_breathing`, `energizing_breath` и `self_trust` = `skipped_for_now`. Следующая ячейка: `need.motivation.activate`. Не открывать Safety Review V1.1.

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
| 2026-08-29 | Sleep-discipline cell sourced via `sleep_discipline`. `technique.sleep_discipline` accepted from Mayo Clinic sleep tips + Mayo Clinic insomnia CBT-I + NHS inform sleep hygiene. Fixed latest bedtime rule for 7 consecutive days. Next = `need.motivation.activate`. |
| 2026-08-29 | Sleep-prepare cell sourced via `sleep`. `technique.sleep` accepted from NHS inform sleep hygiene + Mayo Clinic Health System sleep tips + NHS inform insomnia page. Brief pre-sleep meditation (soften jaw on out-breath). Next = `need.sleep.discipline`. |
| 2026-08-29 | Rest cell sourced via `relaxation`. `technique.relaxation` accepted from CUH NHS systematic focusing + Mayo Clinic relaxation techniques + NHS inform progressive muscle relaxation. Brief body-focused relaxation (heavy hands). Next = `need.sleep.prepare`. |
| 2026-08-29 | Release cell sourced via `body_release`. `technique.body_release` accepted from NHS inform progressive muscle relaxation + Mayo Clinic + NCBI StatPearls. Abbreviated single-area tension-release (shoulders). Next = `need.rest.downregulate`. |
| 2026-08-29 | Confidence cell sourced via `capability`. `technique.capability` accepted from CBT/REBT rational coping-statement method + NHS inform anxiety guide. `affirmation.self_trust` skipped (source gap). Next = `need.release.release`. |
| 2026-08-26 | Source confirms the technique; the technique need not justify an old probe. LLM items are disposable. |
| 2026-08-26 | Skip preferred type → return to the need, pick another existing type, or leave uncovered. Do not invent a similar replacement. |
| 2026-08-26 | v1.0 ACCEPTED — research escalation retired; lightweight fill is the active process; box_breathing skipped_for_now |
