# Human golden blind batch `c362_blind_pilot_20260726`

Pilot export from **live** `day_scenario` generations (C3.6.2).

## Status

| Role | State |
|------|--------|
| Reviewer A | **filled** — agent blind pass |
| Reviewer B | **filled** — independent agent blind pass (`review_sheets/` only) |
| Seal | **7/7 sealed** (`sealed/*.json`) — overall bands agreed; no adjudication needed |

## Sealed bands (consensus)

| Case | Band |
|------|------|
| hg-1482ed91292c | pass |
| hg-21d5bfaf98ab | reject |
| hg-369b42ad90c1 | pass |
| hg-660b14d4bbb4 | pass |
| hg-df42bbdb781d | reject |
| hg-f3c8ab09e03f | acceptable_with_issues |
| hg-f61a374bc5aa | pass |

Reject drivers (both reviewers): `SCENE_CLONE`, `SCENE_ABSTRACT`, `SCENE_MISSING_EVERYDAY`, `SCENE_UNIVERSAL_ADVICE`; plus `ASTRO_JARGON_BARE` / `THESIS_ECHO` on the B5-template cases.

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
- **Next:** promote quality gates by evidence (`SCENE_CLONE` / everyday / bare astro jargon) → grow EN/40
