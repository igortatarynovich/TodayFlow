# Human golden blind batch `c362_blind_pilot_20260726`

Pilot export from **live** `day_scenario` generations (C3.6.2).

## Status

| Role | State |
|------|--------|
| Reviewer A | **filled** (`reviewer_templates/*.reviewer_a.json`) — blind agent pass |
| Reviewer B | **waiting** — see [REVIEWER_B_INSTRUCTIONS.md](./REVIEWER_B_INSTRUCTIONS.md) + `review_sheets/` |
| Seal | blocked until B completes (`import_human_reviews_seal_c362.py`) |

## For reviewer B

1. Open only `review_sheets/` (or `blind/`) + the rubric.
2. Do **not** open `cases/` or `*.reviewer_a.json`.
3. Fill `reviewer_templates/<case_id>.reviewer_b.json`.

Rubric: `docs/audits/DAY_SCENARIO_HUMAN_REVIEW_RUBRIC_C362.md`

## Operator seal

```bash
cd backend
PYTHONPATH=src .venv/bin/python evals/day_scenario_quality/import_human_reviews_seal_c362.py \
  --batch ../docs/audits/day_scenario_human_golden/batches/c362_blind_pilot_20260726
```

## Inventory

- Cases: **7** (pilot — not the full 40 target)
- Locales: RU
- Source: `live_capture`
