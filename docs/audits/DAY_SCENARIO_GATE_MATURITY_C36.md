# Day Scenario Gate Maturity C3.6

**Status:** LANDED (maturity registry · quality observe · hard-only blocking)  
**Date:** 2026-07-26  
**Code:** `day_scenario_gate_maturity_c36.py` · wired in `call_day_scenario_native_llm_c1`  
**Depends on:** C3.1–C3.5.1 analyzers (unchanged as detectors)

## Architecture impact

```markdown
## Architecture impact
- **SoT before:** editorial CRITICAL + soft personalization could retry / downgrade /
  unavailable in native LLM user loop (parallel policy in analyzers)
- **SoT after:** single runtime-policy owner = maturity registry. Analyzers emit
  defect code + score + details only. Quality = observe (capture/eval). Hard =
  schema/SoT/broken refs/PROFILE_FACT_LEAK may retry or reject.
- **Public contract changed?** no — no new user-facing fields. `gate_maturity`,
  policy decisions, and maturity annotations live in **capture** only.
  Pre-existing `editorial_meta` scores/defects keep analyzer shape without
  maturity/runtime_action keys.
- **Migration required?** no
- **Canon updated?** yes — this note + DAY_SCENARIO_V1 + tracker + lifecycle
- **Backward compatible?** yes for clients; generation may accept more
  quality-imperfect scenarios that previously became unavailable
- **Lifecycle:** GET still no Nebius; refresh LLM path policy changed (safer)
```

## Maturity modes (runtime effect)

| Mode | Runtime |
|------|---------|
| `experimental` | observe only |
| `advisory` | observe only |
| `candidate_blocking` | observe only until explicit promotion decision |
| `blocking` | may retry / reject_story |

Only `blocking` may change the user answer. `candidate_blocking` does **not** block.

## Hard (blocking) today

| Rule | Retry | Reject | Notes |
|------|-------|--------|-------|
| Native schema / SoT markers | yes | after attempts | broken contract assemble |
| Broken `origin_scene_id` / orphan props | yes | after attempts | hard validate |
| `PERSONALIZATION_EVIDENCE_ORPHAN` | yes | after attempts | evidence pack only in feedback |
| `PERSONALIZATION_PROFILE_FACT_LEAK` | **no** | immediate | leaked text never shipped; never quality-rewrite |

After hard retries exhausted → `None` → wire `facts_only_unavailable`.

## Quality (observe only)

Scene concreteness, chorus coherence, repetition, formulation, closure, personalization depth, generic wording, role drift, semantic duplication — and all other registered quality codes.

Must **not**: retry, downgrade to general, unavailable, replace first valid answer.

## Where scores / defects live

| Surface | Contents |
|---------|----------|
| Capture `attempts[].after_normalize` | scores, annotated defects, `gate_maturity` summary |
| Capture `defects[]` | observed codes |
| Eval pack (C3.5.1) | independent scoring |
| Public `editorial_meta` | pre-C3.6 analyzer scores/defects only (**no** `gate_maturity`) |
| User today_contract slots | unchanged |

## Single policy owner

- Analyzers must not call retry / downgrade / unavailable / replace.
- Legacy helpers (`editorial_has_critical`, `personalization_requires_retry`,
  `personalization_decision_after_retries`) remain for eval/tests labeling only —
  **not** used by `call_day_scenario_native_llm_c1`.
- Integration proof: `tests/test_day_scenario_gate_maturity_runtime_c36.py`.

## Out of scope

- Promoting quality codes to blocking (needs calibration metrics)
- Visual polish / UI / Nebius / today.py Optional talisman / CE / Tarot
