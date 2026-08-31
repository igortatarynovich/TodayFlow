# Practice Technique Targeted Ingest v1

> **Research archive / non-blocking (2026-08-26).** Historical evidence only. Not in NOW. Does not unlock fill. Active process: [PRACTICE_LIBRARY_FILL_V1.md](./PRACTICE_LIBRARY_FILL_V1.md). Index: [PRACTICE_TECHNIQUE_RESEARCH_ARCHIVE_V1.md](./PRACTICE_TECHNIQUE_RESEARCH_ARCHIVE_V1.md).

**Статус:** `ACCEPTED` — paraphrase двух selected resolution loci. **Не** Normalization V1.1. **Не** technique canon.  
**Версия:** 1.0 (2026-08-25).  
**Владелец:** Product + Research.  
**Targeted shortlist:** [PRACTICE_TECHNIQUE_TARGETED_SHORTLIST_V1.md](./PRACTICE_TECHNIQUE_TARGETED_SHORTLIST_V1.md).  
**Family ingest (остаётся):** [PRACTICE_TECHNIQUE_INGEST_V1.md](./PRACTICE_TECHNIQUE_INGEST_V1.md).  
**Normalization V1:** [PRACTICE_TECHNIQUE_NORMALIZATION_V1.md](./PRACTICE_TECHNIQUE_NORMALIZATION_V1.md) (`insufficient_evidence`).  
**Provenance:** [PRACTICE_TECHNIQUE_PROVENANCE_V1.md](./PRACTICE_TECHNIQUE_PROVENANCE_V1.md).  
**Machine:** [`technique_targeted_ingest_v1.json`](../../DATA/reference/practice/technique_targeted_ingest_v1.json) · contract [`technique_targeted_ingest_contract_v1.json`](../../DATA/reference/practice/technique_targeted_ingest_contract_v1.json).

**Это:** что утверждают *два* selected resolution loci, своими словами, без copy.  
**Это не:** universal definition семьи · allowed variant · склейка phase-structure с equal-count · Canonical Technique · `technique_id` · Safety Review.

`technique_canon_v1.json` остаётся **пустым**.  
`practice.box_breathing.001` остаётся provisional, без `technique_id`.  
Landscape `mechanism_shape` **не** переписан. Family ingest V1 **не** заменяется.

---

## Architecture impact

- **SoT before:** Targeted Shortlist V1 выбрал Marchant 2025 и NHS Wales CAVUHB. Следующий шаг мог обобщить авторский contrast 5:5 на всю семью или объявить 4-4-6-2 допустимым variant будущего канона.
- **SoT after:** targeted ingest = **ровно два selected loci → independent evidence records**. Marchant: square и 5:5 хранятся **раздельно**; contrast условий эксперимента **не** становится определением семьи. CAVUHB: наблюдаемая последовательность 4-4-6-2 и ярлык *square*; из этого следует только, что *square* не обязательно equal-count. Две оси (`shape_phase_structure` · `timing_ratio`) записаны как **сигнал**, не решение. Normalization V1.1 ответит на два identity-вопроса, затем тем же overall verdict: `normalize_one` | `split_family` | `insufficient_evidence`. Safety Review — только если V1.1 даст достаточно определённый kernel.
- **Public contract changed?** no
- **Migration required?** no runtime. Fill frozen.
- **Canon updated?** yes — этот файл · targeted ingest JSON · provenance §11 · coverage/landscape next pointer · `_INDEX` · README · tracker
- **Backward compatible?** yes для клиентов. Несовместимо с `technique_id`, записью canon, склейкой осей, или Safety Review из этого pass.

---

## 0. Закон этого pass

1. **Только два selected loci.** Supporting / rejected / already-ingested family records не ingest заново.
2. **Один locus — одна evidence record.** Внутри Marchant square и 5:5 — два *named conditions*, не два канона.
3. **Paraphrase, не copy.** Не переносить HRV/mood/anxiety claims в mechanism.
4. **Observation ≠ canon.** `observed_*` = что написал этот источник.
5. **Авторский contrast ≠ family definition.** Marchant различает экспериментальные условия. Это не universal definition `equal_count_breath`.
6. **Unequal counts ≠ allowed variant.** CAVUHB 4-4-6-2 не становится variant будущего метода.
7. **Две оси не склеивать.** Phase structure и timing ratio расходятся как сигнал. Решение — Normalization V1.1.
8. **Ingest ≠ V1.1.** Запрещены формулы: «общим ядром является…», «hold optional», «4-4-6-2 — variant square», «5:5 доказывает, что hold не identity-bearing для семьи».

---

## 1. Граница

```text
Targeted shortlist selected loci
  → targeted ingested evidence records
  ≠ Canonical Technique
  ≠ Normalization V1.1 decision
  ≠ rewrite of landscape kernel
```

Family ingest V1 (BHF / SFH / Newcastle) остаётся отдельным корпусом. V1.1 читает **оба**.

---

## 2. Две записи

| `evidence_id` | Locus | Что фиксирует | Чего не делает |
|---------------|-------|----------------|----------------|
| `ev.equal_count.byu.marchant.2025.square` | Marchant 2025, Methods | **Отдельно** square (in 4 / hold 4 / out 4 / hold 4) и **отдельно** 5:5 (in 5 / out 5, без holds). Contrast — именованные условия *этого* эксперимента. | Не объявляет 5:5 определением семьи. Не ingest HRV/PETCO2/mood. 4:6 и 4-7-8 — другие named conditions, не family variants. |
| `ev.equal_count.nhs_wales.cavuhb.square` | CAVUHB workbook, «Square breathing» | Последовательность 4-4-6-2 под ярлыком *square*. Ярлык не фиксирует equal-count. | Не объявляет unequal counts допустимым variant. `observed_variants[]` пуст. |

---

## 3. Две оси (сигнал, не решение)

Имя landscape family `equal_count_breath` может нести слишком раннюю гипотезу. После CAVUHB потенциально расходятся:

| Ось | Вопрос | Этот pass |
|-----|--------|-----------|
| `shape_phase_structure` | Есть ли четыре timed фазы? | Наблюдение. Не kernel. |
| `timing_ratio` | Равны ли длительности этих фаз? | Наблюдение. Не kernel. |

Их **нельзя** склеить до Normalization V1.1. Landscape `mechanism_shape` не переписывается.

Сигнал shortlist/ingest, что box/square и equal-count могут оказаться не одной семантической осью, **не** есть решение V1.1.

---

## 4. Что V1.1 должен ответить

Не новые overall-статусы. Сначала структурированное решение по осям, затем прежний verdict.

| Identity question | Допустимые ответы оси |
|-------------------|------------------------|
| `post_exhale_hold` | `required` · `optional` · `unresolved` |
| `equal_count` | `identity_bearing` · `common_parameter` · `unresolved` |

Overall: `normalize_one` · `split_family` · `insufficient_evidence`.

Safety Review открывается **только** если V1.1 даст достаточно определённый kernel (`normalize_one` с resolved осями). Probe без `technique_id` до canonical.

Повторный `insufficient_evidence` допустим.

---

## 5. Поля

Как Ingest V1, плюс:

- Marchant: `observed_named_conditions[]` (square и 5:5) · `does_not_generalize_author_contrast = true`
- CAVUHB: `does_not_treat_unequal_counts_as_variant = true`
- Ledger: `axes_observed_not_decided[]` · `does_not_glue_axes` · `v1_1_identity_questions[]`

`claim_scope` этого pass: `experimental_named_conditions` · `method_sequence_and_label`.

`ingest_status`: `ingested`. Не `extracted`, не `canonical`.

---

## 6. Запрещено

- Писать `technique_canon_v1.json`.
- Ставить `technique_id` на probe.
- Открывать Safety Review / Canonical.
- Открывать следующую landscape-семью.
- Переписывать landscape kernel.
- Обобщать Marchant contrast на всю семью.
- Объявлять 4-4-6-2 variant.
- Склеивать phase structure и equal-count.
- Копировать protocol text. Заявлять efficacy. Писать новые items.

---

## 7. Что дальше

1. Targeted ingest стоит. Family ingest V1 стоит. Normalization V1.1 = `normalize_one` candidate. Safety Review = `insufficient_safety`. Targeted Safety Shortlist = stop A. Targeted Safety Ingest = two observations. Canon пуст. Type не attested.
2. Исторический next этого pass: Safety Review V1.1 (**не открывать**). `technique_id` — только после `canonical`.

**Live (2026-08-26):** research escalation archived, non-blocking. Safety Review V1.1 is **not** the next Product and is not opened. Next = [PRACTICE_LIBRARY_FILL_V1](./PRACTICE_LIBRARY_FILL_V1.md). `box_breathing` = skipped_for_now.

---

## Changelog

| Дата | Изменение |
|------|-----------|
| 2026-08-26 | research archive / non-blocking; live next = library fill, not Safety Review V1.1 |
| 2026-08-26 | pointer: Targeted Safety Ingest V1 closed; next = Safety Review V1.1 |
| 2026-08-26 | pointer: Targeted Safety Shortlist V1 = stop A; next = Targeted Safety Ingest |
| 2026-08-26 | pointer: Safety Review V1 = insufficient_safety; next = owner decides |
| 2026-08-25 | pointer: Normalization V1.1 = normalize_one candidate; next = Safety Review |
| 2026-08-25 | v1.0 ACCEPTED — two resolution loci; square vs 5:5 unmerged; 4-4-6-2 is label observation not variant; two axes signal-only; next = Normalization V1.1 |
