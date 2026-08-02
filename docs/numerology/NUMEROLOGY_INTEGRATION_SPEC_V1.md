# Numerology base — integration spec v1

Closes the gap: `numerology_explainer` had no digit bank; FE had a bogus `"20"` rhythm key.

## Checklist

- [x] Source of `"20"` identified — FE/test only; not BE reduce. Documented in [NUMBER_BASE_V1.md](./NUMBER_BASE_V1.md) §2.
- [x] `number_base_v1` enriched (archetype, masters, karmic); loader exposes prompt block + alignment helper.
- [x] `numerology_explainer` v4: injects base block; forces `meaning` from bank; fallback from bank; honest empty if missing row.
- [x] FE `NUMBER_RHYTHM_BY_VALUE` mirrors bank (1–9, 11/22/33, karmic 13/14/16/19); no 20; no 44 (not in use).
- [x] Auto check: `_is_valid_numerology_explanation` requires meaning aligned with base anchors; `validate_number_base_v1` rejects value 20 in bank.
