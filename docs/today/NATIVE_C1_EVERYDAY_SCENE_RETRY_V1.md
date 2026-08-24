# Native C1 Everyday Scene Retry V1

**Date:** 2026-08-24  
**Status:** **LOCKED** — close Global `SCENE_MISSING_EVERYDAY` / `SCENE_ABSTRACT` retry whack-a-mole. **Not** C3.1 detector weakening. **Not** I0 reopen. **Not** IL-4. **Not** `active`.  
**Canon:** [NATIVE_C1_EDITORIAL_GATE_CALIBRATION_V1](./NATIVE_C1_EDITORIAL_GATE_CALIBRATION_V1.md) · [DAY_SCENARIO_EVERYDAY_QUALITY_C31](../audits/DAY_SCENARIO_EVERYDAY_QUALITY_C31.md)

---

## Architecture impact

- **SoT before:** c5.1 retry listed the failing `scenes[i]` everyday_example. Prod gen **1104** (user 13): attempt 0 `SCENE_MISSING_EVERYDAY` on `work_decisions`; attempt 1 same codes on `energy_body`. Two attempts, second scene traded in. Gate codes unchanged; model did not keep lived markers on **all** scenes.
- **SoT after:** **Native C1 Everyday Scene Retry V1** — prompt `day-scenario-native-c5.2` states the lived-marker bar on every scene (clock / quote≥12 / person+speech / channel) and forbids shortening passing scenes. Retry feedback repeats that contract. Global `max_attempts` default **3**. C3.1 detectors unchanged (`everyday_has_lived_specificity` / `_CONCRETE_MARKER_RE`). Public JSON unchanged.
- **Public contract changed?** no
- **Migration required?** no — force rebuild / refresh picks up c5.2
- **Canon updated?** yes — this file · tracker 1.3.119
- **Backward compatible?** yes — same blocking codes; stricter all-scene retry only

---

## Problem (production gen 1104)

```
attempt 0: SCENE_MISSING_EVERYDAY + SCENE_ABSTRACT scenes[0:scene.work_decisions]
attempt 1: SCENE_MISSING_EVERYDAY + SCENE_ABSTRACT scenes[1:scene.energy_body]
```

Not `unknown_evidence` (1.3.118). Not CHORUS_PARALLEL.

---

## Out of scope

- Weaken SCENE_* detectors so thin tips PASS
- Post-LLM overwrite of `everyday_example`
- Reopen I0 / IL-4 / evidence allowlist

---

## Tests

`backend/tests/test_native_c1_everyday_scene_retry_v1.py`

## Live (2026-08-24, after backend recreate)

| user | gen | result |
|------|-----|--------|
| **13** | 1106 | **PASS** — first Global accepted (c5.2) |
| **17** | 1107 | **PASS** — 3 Global (`ASTRO_JARGON_BARE` ×2 then accept); would have been unavailable at `max_attempts=2` |
| **8** | 1108 | **PASS** |
| **11** | 1109 | **PASS** |
| **15** | 1101 | still `verbatim_seed_leak` — out of this pass |
