# Day story / day product capture

Offline and DB harness for production-faithful packs.

```bash
cd backend
PYTHONPATH=src python evals/day_story_quality/run_day_product_capture_v0.py \
  --offline --no-llm \
  --dates 2026-07-18,2026-07-19,2026-07-20,2026-07-21,2026-07-22,2026-07-23,2026-07-24

# With LLM (if configured):
PYTHONPATH=src python evals/day_story_quality/run_day_product_capture_v0.py \
  --offline --dates 2026-07-20,2026-07-21,2026-07-22
```

Canon: `docs/audits/DAY_PRODUCT_LOGIC_CAPTURE_PACK.md`  
Scenario SoT (target): `docs/DAY_SCENARIO_V1.md`
