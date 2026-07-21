# Compatibility quality eval (C2)

Product contracts: `docs/COMPATIBILITY_CONTENT_CANON_V1.md`  
Code: `services/compatibility_content_v1/`

## Artifacts

| File | Role |
|------|------|
| `scenarios_v1.json` | 80 cases: 20 zodiac / 20 dates / 20 one profile / 20 two profiles |
| `run_guest_baseline_checks.py` | Offline structural pass on deterministic guest baseline (no LLM) |

## Rubric

specificity · natural_ru · no_repetition · usefulness · source_depth_match · block_coherence · practical_advice_quality · shippable_without_regen

Structural: stable sense · no template collapse · guest ≠ registered · premium ≠ registered · do⊥avoid · verdict support · no fabricated partner facts · missing data not masked.

## Workflow

1. Guest baseline checks (always):  
   `python evals/compatibility_quality/run_guest_baseline_checks.py`
2. LLM offline run (registered + premium) against scenarios — inject `generate_content_v1` with live provider.
3. Manual score ≥30 answers.
4. Only then set `COMPATIBILITY_CONTENT_V1=1` and switch enrichment.

Production default: flag **off**.
