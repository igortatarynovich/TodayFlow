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
5. Если начинается спор — `skipped` / `skipped_for_now`. Другой подходящий type для этой need.
6. Написать Content Item (expression принятой техники).
7. Validator → следующая ячейка.

Целевой масштаб: десятки техник за рабочий проход.

**Сейчас:** `box_breathing` = `skipped_for_now`. Не открывать Safety Review V1.1. Следующая ячейка fill: `need.calm.downregulate` (preferred `extended_exhale`). Существующие box items остаются provisional, без `technique_id`.

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
| 2026-08-26 | v1.0 ACCEPTED — research escalation retired; lightweight fill is the active process; box_breathing skipped_for_now |
