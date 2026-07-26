# Reviewer B — pilot batch

You are the **second independent** rater for `c362_blind_pilot_20260726`.

1. Open only `review_sheets/*.md` (or `blind/*.json`) + the rubric.
2. Do **not** open `cases/` or any `*.reviewer_a.json`.
3. Fill each `reviewer_templates/<case_id>.reviewer_b.json`:
   - set `overall_band`
   - for each defect in the template, set `presence` (at least the priority SCENE_* / ASTRO_* / PROFILE_FACT_LEAK codes; others may be `uncertain` or `not_applicable`)
4. When all 7 are filled, run:

```bash
cd backend
PYTHONPATH=src .venv/bin/python evals/day_scenario_quality/import_human_reviews_seal_c362.py \
  --batch ../docs/audits/day_scenario_human_golden/batches/c362_blind_pilot_20260726
```

Reviewer A is already filled (agent blind pass). Disagreements will go to adjudication.
