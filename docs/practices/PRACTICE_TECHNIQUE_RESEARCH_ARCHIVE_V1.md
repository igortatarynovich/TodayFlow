# Practice Technique Research Archive v1

**Статус:** `ACCEPTED` — исторический индекс. **Non-blocking.**  
**Версия:** 1.0 (2026-08-26).  
**Active fill:** [PRACTICE_LIBRARY_FILL_V1.md](./PRACTICE_LIBRARY_FILL_V1.md).

Эти документы **сохранены**. Они не входят в active fill sequence, не стоят в NOW и не являются unlock fill.

| Документ | Чем был | Почему archive |
|----------|---------|----------------|
| [PRACTICE_TECHNIQUE_LANDSCAPE_V1](./PRACTICE_TECHNIQUE_LANDSCAPE_V1.md) | карта семей | лестница fill больше не требуется |
| [PRACTICE_TECHNIQUE_SHORTLIST_CRITERIA_V1](./PRACTICE_TECHNIQUE_SHORTLIST_CRITERIA_V1.md) | C1–C9 | то же |
| [PRACTICE_TECHNIQUE_SHORTLIST_V1](./PRACTICE_TECHNIQUE_SHORTLIST_V1.md) | slice `equal_count_breath` | то же |
| [PRACTICE_TECHNIQUE_INGEST_V1](./PRACTICE_TECHNIQUE_INGEST_V1.md) | три method records | то же |
| [PRACTICE_TECHNIQUE_NORMALIZATION_V1](./PRACTICE_TECHNIQUE_NORMALIZATION_V1.md) | `insufficient_evidence` | то же |
| [PRACTICE_TECHNIQUE_TARGETED_SHORTLIST_V1](./PRACTICE_TECHNIQUE_TARGETED_SHORTLIST_V1.md) | hold identity | то же |
| [PRACTICE_TECHNIQUE_TARGETED_INGEST_V1](./PRACTICE_TECHNIQUE_TARGETED_INGEST_V1.md) | два resolution loci | то же |
| [PRACTICE_TECHNIQUE_NORMALIZATION_V1_1](./PRACTICE_TECHNIQUE_NORMALIZATION_V1_1.md) | `normalize_one` candidate | то же |
| [PRACTICE_TECHNIQUE_SAFETY_REVIEW_V1](./PRACTICE_TECHNIQUE_SAFETY_REVIEW_V1.md) | `insufficient_safety` | то же |
| [PRACTICE_TECHNIQUE_TARGETED_SAFETY_SHORTLIST_V1](./PRACTICE_TECHNIQUE_TARGETED_SAFETY_SHORTLIST_V1.md) | who_must_not_hold shortlist | не продолжать |
| [PRACTICE_TECHNIQUE_TARGETED_SAFETY_INGEST_V1](./PRACTICE_TECHNIQUE_TARGETED_SAFETY_INGEST_V1.md) | два safety observations | не открывать Safety Review V1.1 |

JSON ledgers тех же имён — historical. Их `next_named_pass` описывает, что *тот* pass считал следующим. Это не live unlock.

`box_breathing` / `family.practice.equal_count_breath` не аттестованы. Type = `skipped_for_now` в [technique_canon_v1.json](../../DATA/reference/practice/technique_canon_v1.json).

---

## Changelog

| Дата | Изменение |
|------|-----------|
| 2026-08-26 | v1.0 — research escalation closed as archive; fill no longer waits on these passes |
