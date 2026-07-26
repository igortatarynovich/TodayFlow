# Human golden blind batch `c362_blind_pilot_20260726`

Pilot export from **live** `day_scenario` generations (C3.6.2).

## For reviewers

1. Open only files under `blind/` (and the rubric).
2. Do **not** open `cases/` — it may contain operator meta.
3. Fill `reviewer_templates/<case_id>.reviewer_a.json` and `.reviewer_b.json`.
4. Set `overall_band` + each defect `presence` (`present`/`absent`/`uncertain`/`not_applicable`).
5. Return filled templates to the operator (no chat with the other reviewer).

Rubric: `docs/audits/DAY_SCENARIO_HUMAN_REVIEW_RUBRIC_C362.md`

## Inventory

- Cases: **7** (pilot — not the full 40 target)
- Locales: see `index.json`
- Source: `live_capture` only in this batch

## Operator

After dual reviews: `append_reviewer_submission` → adjudicate if needed → `build_consensus` → attach analyzer.
