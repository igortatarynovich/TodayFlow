# Practice Technique Ingest v1

**Статус:** `ACCEPTED` — provenance-preserving paraphrase selected loci. **Не** normalization. **Не** technique canon.  
**Версия:** 1.0 (2026-08-25).  
**Владелец:** Product + Research.  
**Parent order:** [KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md](../KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md) шаг 10.  
**Shortlist:** [PRACTICE_TECHNIQUE_SHORTLIST_V1.md](./PRACTICE_TECHNIQUE_SHORTLIST_V1.md).  
**Provenance:** [PRACTICE_TECHNIQUE_PROVENANCE_V1.md](./PRACTICE_TECHNIQUE_PROVENANCE_V1.md).  
**Machine:** [`technique_ingest_v1.json`](../../DATA/reference/practice/technique_ingest_v1.json) · contract [`technique_ingest_contract_v1.json`](../../DATA/reference/practice/technique_ingest_contract_v1.json).

**Это:** что утверждает каждый *selected locus*, своими словами, без copy.  
**Это не:** истинный kernel · optional hold · variant-склейка · Canonical Technique · `technique_id` · efficacy.

`technique_canon_v1.json` остаётся **пустым**.  
`practice.box_breathing.001` остаётся provisional, без `technique_id`.  
Другие семьи **не** открыты.

---

## Architecture impact

- **SoT before:** Shortlist V1 выбрал три loci для `equal_count_breath`. Следующий шаг мог открыть ещё семьи или сразу написать «общим ядром является…».
- **SoT after:** ingest = **selected loci → independent evidence records**. `observed_*` = observation источника, не canonical field. Три записи не склеены. Newcastle — конфликтующее описание, не variant. SFH sequence и stop/safety лежат в разных полях. Normalization — отдельный named pass. Canon и library attestation не меняются.
- **Public contract changed?** no
- **Migration required?** no runtime. Fill frozen.
- **Canon updated?** yes — этот файл · ingest JSON · provenance pipeline/§11 · shortlist next-pointer · coverage · `_INDEX` · README · tracker
- **Backward compatible?** yes для клиентов. Несовместимо с записью `technique_canon_v1.json`, `technique_id`, или kernel-синтезом из этого pass.

---

## 0. Закон этого pass

1. **Только selected loci.** Supporting и rejected не ingest.
2. **Один locus — одна evidence record.** Не сводить три описания к одному extracted technique.
3. **Paraphrase, не copy.** Своя формулировка. Не переносить benefit-заголовки в mechanism.
4. **Observation ≠ canon.** Поля `observed_mechanism` / `observed_steps` / `observed_bounds` / `observed_safety` / `observed_variants` фиксируют, *что написал этот источник*. Они не заполняют `canonical_mechanism`.
5. **Ingest ≠ normalization.** Запрещены формулы: «общим ядром является…», «вторая задержка optional», «три фазы — variant четырёх».
6. **Конфликт оставлять стоять.** Несовпадение фаз — `conflict_tags`, не среднее.

---

## 1. Граница

```text
Landscape candidate family
  → selected evidence loci
  → ingested evidence records
  ≠ Canonical Technique
  ≠ normalized kernel
```

Этот pass закрывает только средний переход.

---

## 2. Три записи

| `evidence_id` | Locus | Что фиксирует |
|---------------|-------|----------------|
| `ev.equal_count.bhf.heart_matters.box` | BHF Heart Matters, «Box breathing» | Четырёхфазная последовательность (пауза после вдоха и после выдоха). Safety в этой секции не заявлена. |
| `ev.equal_count.nhs_sfh.box_leaflet` | NHS Sherwood Forest leaflet | **Отдельно** sequence (BOX BREATHING) и **отдельно** stop/safety (другой заголовок). Не одно смешанное ядро. |
| `ev.equal_count.nhs_newcastle.square` | Newcastle NHS, «Square breathing» | Трёхфазное описание (вдох–задержка–выдох, повтор). `claim_scope = conflicting_method_sequence`. Не variant. |

`observed_variants[]` на BHF/SFH — опции, которые **сам locus** предлагает (поза, обвести телефон). Это не решение, что семья имеет такие variants.

---

## 3. Поля evidence record

`evidence_id` · `candidate_family` · `source_ref` · `locus` · `source_family` · `paraphrase` · `observed_mechanism` · `observed_steps[]` · `observed_bounds[]` · `observed_safety[]` · `observed_variants[]` · `claim_scope` · `conflict_tags[]` · `ingest_status`

`ingest_status` этого pass: `ingested`.  
Не `extracted`, не `canonical`.

`claim_scope`: `method_sequence_only` · `method_sequence_and_stop_rules` · `conflicting_method_sequence`.  
Не efficacy. Не treatment.

---

## 4. Запрещено

- Писать `technique_canon_v1.json`.
- Ставить `technique_id` на Content Item.
- Открывать следующую landscape-семью.
- Синтезировать общий kernel.
- Называть Newcastle variant четырёхфазных страниц.
- Кладсть SFH dizziness внутрь `observed_steps`.
- Копировать protocol text. Заявлять efficacy. Писать новые items.
- Считать ingest аттестацией `box_breathing`.

---

## 5. Что дальше

1. Ingest стоит. Normalization V1 = `insufficient_evidence`. V1.1 = `normalize_one` candidate. Safety Review = `insufficient_safety`. Targeted Safety Shortlist = stop A. Canon пуст. Type не attested.
2. Следующий named pass: **Targeted Safety Ingest**.
3. `technique_id` — только после `canonical`.

---

## Changelog

| Дата | Изменение |
|------|-----------|
| 2026-08-26 | pointer: Targeted Safety Shortlist V1 = stop A; next = Targeted Safety Ingest |
| 2026-08-26 | pointer: Safety Review V1 = insufficient_safety; next = owner decides |
| 2026-08-25 | pointer: Normalization V1.1 = normalize_one candidate; next = Safety Review |
| 2026-08-25 | pointer: Targeted Ingest V1 closed; next = Normalization V1.1 |
| 2026-08-25 | pointer: Targeted Shortlist V1 closed; next = targeted ingest → Normalization V1.1 |
| 2026-08-25 | pointer: Normalization V1 closed as insufficient_evidence; next = targeted shortlist |
| 2026-08-25 | v1.0 ACCEPTED — three independent evidence records for equal_count_breath selected loci; not kernel; not canon |
