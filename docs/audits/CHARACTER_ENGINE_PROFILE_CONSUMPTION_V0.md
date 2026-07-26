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

## Architecture impact (2026-07-26 v0.5 — Stage 3 consumption)

- **SoT after:** when `diagnostics.character_engine_stage3.stage3.status=grounded`:
  - trap ← `primary_tension.surface_text`
  - `decision_style` ← `internal_engine.decision`
  - helps prefer growth/recovery surfaces
- **Fallback:** v0.4 editorial banks if Stage 3 missing/insufficient.
- **Flag:** consumption still forces Stage 2+3 on Profile read; `PUBLISH_READY=0`.
- **Canon:** [CHARACTER_ENGINE_STAGE3_INTERNAL_V0.md](./CHARACTER_ENGINE_STAGE3_INTERNAL_V0.md).

## Architecture impact (2026-07-26 v0.6 — Stage 4 consumption)

- **SoT after:** when Stage 4 grounded:
  - `relationship_style` ← scene `intimacy`
  - `money_style` ← scene risk/responsibility/uncertainty (resource proxy, not money root)
  - `growth_zones` / helps ← `potential`
- **Keep:** Stage 3 trap/decision preferred for those slots.
- **Canon:** [CHARACTER_ENGINE_STAGE4_LIFE_V0.md](./CHARACTER_ENGINE_STAGE4_LIFE_V0.md).
- **Not:** PUBLISH_READY / Stage 5 Compass.
