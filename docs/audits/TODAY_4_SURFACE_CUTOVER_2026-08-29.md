# Today 4-surface cutover — Phase 2.1

**Date:** 2026-08-29  
**Status:** **done** — default `/today` uses the 4-surface `TodayProductScreenFlow` (Today → Ritual → My Day → Evening).  
**Sources:** `docs/status/RELEASE_PLAN_V1.md` task 2.1 · `docs/today/TODAY_PRODUCT_FLOW_V1.md` · `TODAY_SCREEN_V1_CANON.md` v4.1 §Default path.

## What changed

- Removed the `?core_loop=1` experiment. The G1 viability surface (`TodayCoreLoopViabilitySurface`) was a preview of Theme → Action → Progress rendered inside the legacy `?full=1` ritual flow. That experiment is no longer needed because the default path already renders the full 4-surface ScreenFlow through `TodayCompositionSurface`.
- Deleted `frontend/src/components/today/TodayCoreLoopViabilitySurface.tsx`.
- Removed `coreLoopViabilityMode` prop and all related rendering/tracking from `frontend/src/components/today/TodayRitualFlow.tsx`.
- Removed `coreLoopViability*` copy keys from `frontend/src/components/today/todayRitualCopy.ts`.
- Removed `coreLoopViabilityMode` variable and `core_loop` query-param cleanup from `frontend/src/app/today/page.tsx`.

## Current route map

| Route | Surface | Notes |
|-------|---------|-------|
| `/today` | `TodayCompositionSurface` (4-surface ScreenFlow) | **default / production path** |
| `/today?first=1` | `TodayCompositionSurface` variant `firstToday` | First Today payoff; no ritual gate |
| `/today?experience=1` | `TodayExperienceSurface` | legacy compressed Today; unchanged by this cutover |
| `/today?full=1` | `TodayRitualFlow` | legacy full-scroll ritual; `core_loop` preview removed |

## Acceptance criteria

- `?core_loop=1` becomes default: ✅ a plain `/today` already renders the same 4-surface `TodayProductScreenFlow` that the experiment was meant to preview.
- No regression in ship gate walkthrough: ✅ the default path (Landing → Signup → Onboarding → `/today` → Evening Close → D2+ Continuity) is unchanged and still uses `TodayCompositionSurface`.

## Architecture impact

- **SoT before:** default `/today` was documented as `TodayCompositionSurface` (Day Story + Ritual Gates), but a separate `?core_loop=1` experiment inside `?full=1` could still render a competing Theme → Action → Progress preview.
- **SoT after:** there is one default 4-surface ScreenFlow for `/today`; `?core_loop=1` is no longer a product route. The `?full=1` and `?experience=1` legacy paths remain as non-default overrides.
- **Public contract changed?** no — no API or JSON contract changes.
- **Migration required?** no — old `?core_loop=1` URLs are now served by the default composition path.
- **Canon updated?** yes — this audit doc plus updates in `docs/status/RELEASE_PLAN_V1.md` and `docs/PRODUCT_EXECUTION_TRACKER.md`.
- **Backward compatible?** yes — the removed component was only reachable through the `?core_loop=1` query param inside the legacy `?full=1` path; its behavior is replaced by the default surface.

## Remaining known legacy

- The `core_loop_viability_surface_visible` meaning event is still emitted by the default `/today` path (instrument names `first_today_v1` and `experience_v0`). The event name predates the cutover but still correctly marks the composition surface as visible. Renaming it would touch the backend `event_type` enum and is left for a separate analytics cleanup if desired.
- `?full=1` and `?experience=1` are still wired in `page.tsx` as legacy non-default paths. Removing them is out of scope for Phase 2.1 and is tracked separately.

## Tests

- `frontend/src/components/today/composition/__tests__/TodayProductScreenFlow.test.ts` — 4-surface flow index/step logic.
- `frontend/src/components/today/composition/__tests__/TodayCompositionSurface.test.tsx` — default surface rendering and time-gate behavior.
- `npm run test` in `frontend/` expected green after the cleanup.
