# Character Engine → Profile consumption slice v0

**Date:** 2026-07-26  
**Baseline CE:** `5eb61c6`  
**Flag:** `CHARACTER_ENGINE_PROFILE_CONSUMPTION=1`  
**Not:** `CHARACTER_ENGINE_PUBLISH_READY` (full cascade cutover stays off)

## Architecture impact

- **SoT before:** Profile journey recognition / why / trap from `profile_contract_v1` (funnel/personality) + LP archetype why + living day-rhythm insight projection. CE Stage 2 lived in `diagnostics` only → **zero visible CE on Profile**.
- **SoT after (selected slots only):** When Stage 2 `status=grounded` and consumption flag on:
  - `identity_core` / `recognition_line` ← Identity Core `surface_text`
  - `portrait_why_v0` ← Stage 1 claims + Stage 0 fact labels
  - `insight_nodes_v0` trap ← Identity thesis trap bank (**forbids living day-rhythm as identity trap**)
  - recognition name label ← CE thesis label (FE prefers over Мудрец/LP seed)
- **Public contract changed?** yes — optional nest `character_engine_consumption_v0`; selected contract/why/insight fields overwritten on read when flag on. Residual slots (decisions / intimacy / money / houses essays) **unchanged**.
- **Migration required?** no version bump — flag-gated read overwrite; Snapshot personality prose may still differ until later adapters.
- **Canon updated?** this audit + tracker; full CE cutover still `CHARACTER_ENGINE_ARCHITECTURE_IMPACT_V1.md` D4.
- **Backward compatible?** yes when flag off; with flag on, old clients still see fields but values come from CE for owned slots.

## Why “simple natal→LLM→profile” kept failing

Dual SoT: Swiss/natal + CE diagnostics vs publish personality. Shadow never fed UI. More Stage 3 LLM without consumption = more invisible prose.

## Residual (explicit)

- decisions / relationship / money / houses person-lines still old
- Stage 2 LLM on Profile read when consumption on (memory cache skips re-run if diagnostics already present)
- Trap lines = editorial bank keyed by identity thesis (declared overwrite for this slice)
- Stage 3 Internal Engine **HOLD** until owner §1.4 skim + this slice verified on server

## Architecture impact (2026-07-26 v0.4 residual close)

- **SoT after:** `emotional_style` / `work_and_realization` / `home_and_security` on contract (matrix explore) + `character_engine_aspect_lines_v0` + rewritten `natal_summary.notable_aspects.gist`.
- **Keep Swiss:** aspect geometry / orb / strength; cusp/sign/degree.
- **FE:** AspectCard prefers CE line when key matches.
- **Consumption profile surface:** journey + character + spheres + houses + matrix styles + aspect person-voice — residual natal instrument facts only.
- **Still HOLD Stage 3** until owner §1.4 skim.
