# Native C1 Seed Leak Retry V1

**Date:** 2026-08-24  
**Status:** **LOCKED** — catch `verbatim_seed_leak` on Global native validate so I0 can retry. **Not** detector weakening. **Not** I0 reopen. **Not** IL-4. **Not** `active`.  
**Canon:** [NATIVE_C1_EDITORIAL_GATE_CALIBRATION_V1](./NATIVE_C1_EDITORIAL_GATE_CALIBRATION_V1.md) · [DAY_SCENARIO_GATE_MATURITY_C36](../audits/DAY_SCENARIO_GATE_MATURITY_C36.md) · [TODAY_SCREEN_SCENARIO_V3](./TODAY_SCREEN_SCENARIO_V3.md) (no seed leakage)

---

## Architecture impact

- **SoT before:** Seed-kill / sky-fact Plot labels ran only after I0 Global+Personal accepted, on mapped `day_scenario_v1` (`what_happens` ← `setup`, `short_name` ← `title`). Prod gen **1101** (user 15): cloned sky sentence in two setups → `verbatim_seed_leak` with **no retry**. After Global catch (c5.3), gen **1116**: `conflict.title` was a sky-fact label → mapped `conflict_short_name_is_sky_fact`, still after I0. Detectors unchanged; the miss was stage order.
- **SoT after:** **Native C1 Seed Leak Retry V1** — same detectors on native Global (`setup` ngrams + `_looks_like_sky_fact_label(title)`). Hard native markers: `verbatim_seed_leak:` · `conflict_short_name_is_sky_fact`. Retry uses `format_seed_leak_retry_feedback`. Prompt `day-scenario-native-c5.3`. Public JSON unchanged.
- **Public contract changed?** no
- **Migration required?** no — force rebuild / refresh picks up c5.3
- **Canon updated?** yes — this file · tracker 1.3.120
- **Backward compatible?** yes — same leak codes; earlier Global reject only

---

## Problem (production gen 1101)

```
gen 1101: accepted_global + accepted_personal → verbatim_seed_leak (mapped what_happens)
gen 1116: accepted_global + accepted_personal → conflict_short_name_is_sky_fact (mapped short_name ← title)
```

Not SCENE_* (1.3.119). Not `unknown_evidence` (1.3.118).

---

## Out of scope

- Weaken `_word_ngrams(min_words=6)` or `_looks_like_sky_fact_label`
- Drop `verbatim_seed_leak` / `conflict_short_name_is_sky_fact` from hard scenario validate
- Post-LLM rewrite of cloned setups
- Reopen I0 / IL-4 / evidence allowlist / everyday detectors

---

## Tests

`backend/tests/test_native_c1_seed_leak_retry_v1.py`

## Live (2026-08-24, after backend recreate)

| gen | result |
|-----|--------|
| **1101** (c5.1) | FAIL `verbatim_seed_leak` after I0 accept — the hole |
| **1116** (c5.3, leak-only) | FAIL `conflict_short_name_is_sky_fact` after I0 accept — same hole, title |
| **1117** (c5.3, leak+title) | Global retries seed-kill (attempt 1); terminal FAIL `ASTRO_JARGON_BARE` after 3 Global — editorial, not post-merge seed-kill |
