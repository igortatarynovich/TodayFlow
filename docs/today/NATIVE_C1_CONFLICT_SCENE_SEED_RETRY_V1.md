# Native C1 Conflict→Scene Seed Retry V1

**Date:** 2026-08-24  
**Status:** **LOCKED** — name `conflict.why_arose` / `why_today` paste into `scenes[].why` so Global retry does not trade that leak for `ASTRO_JARGON_BARE`. **Not** detector weakening. **Not** I0 reopen. **Not** IL-4. **Not** `active`.  
**Canon:** [NATIVE_C1_ASTRO_JARGON_RETRY_V1](./NATIVE_C1_ASTRO_JARGON_RETRY_V1.md) · [NATIVE_C1_SEED_LEAK_RETRY_V1](./NATIVE_C1_SEED_LEAK_RETRY_V1.md) · [NATIVE_C1_EDITORIAL_GATE_CALIBRATION_V1](./NATIVE_C1_EDITORIAL_GATE_CALIBRATION_V1.md)

---

## Architecture impact

- **SoT before:** Seed-kill retry named setup-to-setup clones and why_today→`human_meaning`. Prod gen **1119** (user 2, c5.4): attempt 0–1 `verbatim_seed_leak` `conflict.why_arose`+`scenes[0].why` / `what_happens`; attempt 2 `ASTRO_JARGON_BARE` on `astrology[2]`. Exact-match mapper blanking of `scene.why == why_today` did not catch 6-word ngrams. Rebuild kept prior native (`kept_prior_native`). Detectors unchanged.
- **SoT after:** **Native C1 Conflict→Scene Seed Retry V1** — prompt `day-scenario-native-c5.5`; seed-kill retry names `why_today`/`why_arose` → `scenes[].why` / `why_sphere` / `setup`; `SEED_JARGON_CROSS_HINT_RU` forbids fixing that leak by jargon rollback. Detectors unchanged. Public JSON unchanged.
- **Public contract changed?** no
- **Migration required?** no — force rebuild / refresh picks up c5.5
- **Canon updated?** yes — this file · tracker 1.3.122
- **Backward compatible?** yes — same blocking codes; retry coaching only

---

## Problem (production gen 1119)

```
attempt 0: verbatim_seed_leak conflict.why_arose+scenes[0].why
attempt 1: verbatim_seed_leak conflict.why_arose+scenes[0].what_happens / why
attempt 2: ASTRO_JARGON_BARE chorus.astrology[2]
source: kept_prior_native
```

Not why_today→`human_meaning` (1.3.121). Not setup-to-setup clone (1.3.120).

---

## Out of scope

- Weaken `_word_ngrams(min_words=6)` / `find_verbatim_seed_leaks_v1`
- Post-LLM ngram strip of `why_sphere`
- Reopen I0 / IL-4 / evidence allowlist / everyday / jargon detectors

---

## Tests

`backend/tests/test_native_c1_conflict_scene_seed_retry_v1.py`

## Live (2026-08-24, after backend recreate)

| gen | result |
|-----|--------|
| **1119** (c5.4) | FAIL — `why_arose`→`scenes[0].why` ×2 then `ASTRO_JARGON_BARE` astrology[2]; `kept_prior_native` |
| **1121** (c5.5) | FAIL — leak → parse → jargon[2]; kept **1120** |
| **1122** (c5.5) | **PASS** user 2 — Global first try, then personal/merged; `interpretation_status=ok` |
