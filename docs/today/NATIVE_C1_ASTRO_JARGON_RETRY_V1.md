# Native C1 Astro Jargon Retry V1

**Date:** 2026-08-24  
**Status:** **LOCKED** — stop Global retry trading `ASTRO_JARGON_BARE` for `verbatim_seed_leak` (why_today paste). **Not** detector weakening. **Not** I0 reopen. **Not** IL-4. **Not** `active`.  
**Canon:** [NATIVE_C1_SEED_LEAK_RETRY_V1](./NATIVE_C1_SEED_LEAK_RETRY_V1.md) · [NATIVE_C1_EDITORIAL_GATE_CALIBRATION_V1](./NATIVE_C1_EDITORIAL_GATE_CALIBRATION_V1.md) · [DAY_SCENARIO_EVERYDAY_QUALITY_C31](../audits/DAY_SCENARIO_EVERYDAY_QUALITY_C31.md)

---

## Architecture impact

- **SoT before:** Seed-kill and editorial jargon retries were separate essays. Prod gen **1117** (user 15): attempt 0 `ASTRO_JARGON_BARE` on `chorus.astrology[1]`; attempt 1 pasted `why_today` into that `human_meaning` → `verbatim_seed_leak` vs `conflict.why_arose`; attempt 2 reverted to jargon. `astrology_voice_lacks_human_translation` unchanged; coaching did not name the other gate.
- **SoT after:** **Native C1 Astro Jargon Retry V1** — prompt `day-scenario-native-c5.4`; jargon retry covers **every** `astrology[i]` and forbids why_today/title paste; seed-kill retry forbids jargon rollback. Shared `SEED_JARGON_CROSS_HINT_RU`. Detectors unchanged. Public JSON unchanged.
- **Public contract changed?** no
- **Migration required?** no — force rebuild / refresh picks up c5.4
- **Canon updated?** yes — this file · tracker 1.3.121
- **Backward compatible?** yes — same blocking codes; cross-gate retry only

---

## Problem (production gen 1117)

```
attempt 0: ASTRO_JARGON_BARE chorus.astrology[1]
attempt 1: verbatim_seed_leak human_meaning[1] + conflict.why_arose
attempt 2: ASTRO_JARGON_BARE chorus.astrology[1]
```

Not post-merge seed-kill (1.3.120). Not SCENE_* (1.3.119).

---

## Out of scope

- Weaken `astrology_voice_lacks_human_translation` / `_HUMAN_TRANSLATION_RE`
- Post-LLM overwrite of `human_meaning`
- Reopen I0 / IL-4 / evidence allowlist / everyday detectors

---

## Tests

`backend/tests/test_native_c1_astro_jargon_retry_v1.py`

## Live (2026-08-24, after backend recreate)

| gen | result |
|-----|--------|
| **1117** (c5.3) | FAIL — jargon[1] ↔ why_today paste ↔ jargon[1] |
| **1118** (c5.4) | **PASS** user 15 — 3 Global then personal/merged; `interpretation_status=ok` |
