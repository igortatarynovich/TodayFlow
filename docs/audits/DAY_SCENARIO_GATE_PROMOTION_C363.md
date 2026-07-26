# Day Scenario Gate Promotion C3.6.3

**Status:** LANDED (selective quality → blocking by sealed pilot evidence)  
**Date:** 2026-07-26  
**Code:** `day_scenario_gate_maturity_c36.py` · editorial retry wired in `call_day_scenario_native_llm_c1`  
**Evidence:** sealed batch [c362_blind_pilot_20260726](./day_scenario_human_golden/batches/c362_blind_pilot_20260726/) (7/7 · 4 pass / 1 acceptable / 2 reject)

## Architecture impact

```markdown
## Architecture impact
- **SoT before:** C3.6 — all quality codes observe-only; only hard contract/safety
  may retry/reject in native LLM loop
- **SoT after:** maturity registry still sole policy owner; four quality codes
  promoted to blocking (retry then unavailable); SCENE_UNIVERSAL_ADVICE →
  candidate_blocking (observe); other quality unchanged
- **Public contract changed?** no — gate_maturity/policy still capture-only;
  exhausted quality reject → None → facts_only_unavailable (pre-existing path)
- **Migration required?** no
- **Canon updated?** yes — this note + DAY_SCENARIO_GATE_MATURITY_C36 +
  DAY_SCENARIO_V1 + tracker
- **Backward compatible?** yes for clients; generation may unavailable more often
  on B5-style abstract/clone scenes
```

## Promotions (evidence-linked)

| Code | Mode | Runtime | Pilot rationale |
|------|------|---------|-----------------|
| `SCENE_CLONE` | blocking | retry → reject | Dual-agreed reject driver (B5 clones) |
| `SCENE_MISSING_EVERYDAY` | blocking | retry → reject | Dual-agreed reject driver |
| `SCENE_ABSTRACT` | blocking | retry → reject | Severe on both sealed rejects |
| `ASTRO_JARGON_BARE` | blocking | retry → reject | Material on sealed reject templates |
| `SCENE_UNIVERSAL_ADVICE` | candidate_blocking | observe | Co-driver on reject but minor on acceptable |

Family remains **`quality`** (not hard/safety). Analyzers unchanged; only maturity + native wiring.

## Not promoted

`THESIS_ECHO`, remaining editorial/personalization quality codes — still experimental/advisory.

## Limits

- Pilot n=7; dual agent blind (not full human panel).  
- Full EN/40 human golden still required before broader quality promotions.  
- No quality→general downgrade.

## Tests

- `tests/test_day_scenario_gate_maturity_c36.py`
- `tests/test_day_scenario_gate_maturity_runtime_c36.py`
