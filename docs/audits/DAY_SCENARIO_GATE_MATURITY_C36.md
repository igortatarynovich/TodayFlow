# Day Scenario Gate Maturity C3.6

**Status:** LANDED (maturity registry · hard + selective quality blocking C3.6.3)  
**Date:** 2026-07-26  
**Code:** `day_scenario_gate_maturity_c36.py` · wired in `call_day_scenario_native_llm_c1`  
**Depends on:** C3.1–C3.5.1 analyzers (unchanged as detectors)  
**Promotion note:** [DAY_SCENARIO_GATE_PROMOTION_C363.md](./DAY_SCENARIO_GATE_PROMOTION_C363.md)

## Architecture impact

```markdown
## Architecture impact
- **SoT before:** editorial CRITICAL + soft personalization could retry / downgrade /
  unavailable in native LLM user loop (parallel policy in analyzers)
- **SoT after (C3.6):** single runtime-policy owner = maturity registry. Analyzers
  emit defect code + score + details only. Hard = schema/SoT/broken refs/
  PROFILE_FACT_LEAK may retry or reject.
- **SoT after (C3.6.3):** four quality codes promoted to blocking (retry→unavailable)
  from sealed C3.6.2 pilot evidence; remaining quality still observe.
- **Public contract changed?** no — no new user-facing fields. `gate_maturity`,
  policy decisions, and maturity annotations live in **capture** only.
  Pre-existing `editorial_meta` scores/defects keep analyzer shape without
  maturity/runtime_action keys.
- **Migration required?** no
- **Canon updated?** yes — this note + C363 promotion + DAY_SCENARIO_V1 + tracker
- **Backward compatible?** yes for clients; more unavailable on promoted defects
- **Lifecycle:** GET still no Nebius; refresh LLM path uses maturity policy
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
| Seed-kill validate codes (`invented_bank_binary`, `chorus:seed_paste_bridge`, `verbatim_seed_leak:*`, sky-fact short_name) | yes | after attempts | v3.1 — was soft accept gap |
| `SEED_BANK_BINARY_SHORT_NAME` / `SEED_CHORUS_PASTE` (editorial) | yes | after attempts | same seed-kill; earlier feedback on native JSON |
| `PERSONALIZATION_EVIDENCE_ORPHAN` | yes | after attempts | evidence pack only in feedback |
| `PERSONALIZATION_PROFILE_FACT_LEAK` | **no** | immediate | leaked text never shipped; never quality-rewrite |

After hard retries exhausted → `None` → wire `facts_only_unavailable`.

## Architecture impact (seed-kill hard-gate, 2026-08-03)

```markdown
## Architecture impact
- **SoT before:** find_verbatim_seed_leaks_v1 / bank-binary / chorus paste markers
  appeared in validate_day_scenario_v1 but were **not** in HARD_SCENARIO_VALIDATE_ERRORS —
  native LLM could accept seed-paste after map (serve heal cleaned cache only).
- **SoT after:** those validate strings are hard (retry→unavailable); editorial emits
  SEED_BANK_BINARY_SHORT_NAME / SEED_CHORUS_PASTE as family=hard blocking with retry.
- **Public contract changed?** no
- **Migration required?** no — serve heal still covers old caches
- **Canon updated?** yes — this note
- **Backward compatible?** yes for clients; more native LLM retries/unavailable on seed paste
```

## Quality — default observe; selective blocking (C3.6.3)

| Mode | Codes (examples) |
|------|------------------|
| **blocking** (retry → unavailable) | `SCENE_CLONE`, `SCENE_MISSING_EVERYDAY`, `SCENE_ABSTRACT`, `ASTRO_JARGON_BARE` |
| **candidate_blocking** (observe) | `SCENE_UNIVERSAL_ADVICE` |
| **observe** (experimental/advisory) | remaining scene/chorus/closure/personalization depth codes |

Unpromoted quality must **not**: retry, downgrade to general, unavailable, replace first valid answer.  
Promoted quality may retry then unavailable — **never** quality→general downgrade.

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

## Out of scope / next

- Broader quality promotions without EN/40 human golden consensus
- Visual polish / UI / Nebius / today.py Optional talisman / CE / Tarot
