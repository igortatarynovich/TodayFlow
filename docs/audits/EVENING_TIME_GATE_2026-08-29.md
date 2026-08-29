# Evening time-gated surface audit (2026-08-29)

**Status:** implemented. Phase 2.3 closed.

**Goal:** ensure the evening close step does not appear in the morning scroll. The evening surface is still part of the product flow; it is simply hidden until the evening time window or until the user explicitly enters evening close mode.

## What changed

- `frontend/src/components/today/composition/TodayProductScreenFlow.tsx` now accepts a `showEvening?: boolean` prop (default `true`).
- When `showEvening` is `false`:
  - the evening `ScreenFlowStep` is not rendered;
  - step indices and dot counts are recomputed (evening step is removed);
  - next-button labels on the preceding step no longer mention evening;
  - helper index functions (`todayScreenFlowStepCount`, `todayHandoffIndices`, `todayScreenFlowReadingIndex`, `todayScreenFlowPracticeIndex`, `todayScreenFlowInsightIndex`, `todayScreenFlowCloseIndex`, `todayScreenFlowAttributesIndex`) accept an optional `showEvening` argument.
- `frontend/src/components/today/composition/TodayCompositionSurface.tsx` decides `showEvening`:
  - `true` if the user is in `eveningMode` (explicitly opened evening close), or
  - `true` if `getTimeOfDayByHour() === "evening"`.
  - otherwise `false` during morning/day scroll.
- Tests updated to mock `getTimeOfDayByHour` and verify that:
  - the evening frame is hidden when time is morning/day;
  - the today frame is still rendered;
  - index helpers correctly skip the evening step when `showEvening` is false.

## Architecture impact

- **SoT before:** the four-screen product flow (`today` → `ritual` → `my_day` → `evening`) always rendered the evening step, so a morning scroll could land on or preview the evening close block.
- **SoT after:** the evening step is a time-gated surface. The four-screen flow still exists as the canonical model; the gate is a presentation-layer decision driven by the user's local time and an explicit evening-mode override. No backend or API contract changes.
- **Public contract changed?** no — the same contract fields are returned; only the FE screen flow presentation changes.
- **Migration required?** no. Cached days keep the same nests.
- **Canon updated?** yes — this file + `docs/PRODUCT_EXECUTION_TRACKER.md` + `docs/status/RELEASE_PLAN_V1.md`.
- **Backward compatible?** yes for API and cached data. The UI scroll order changes only when the local time is not evening.

## Tests

```bash
cd /opt/TodayFlow/frontend
npx jest src/components/today/composition/__tests__/TodayProductScreenFlow.test.ts \
         src/components/today/composition/__tests__/TodayCompositionSurface.test.tsx --no-coverage
```

All green. Frontend production build also passes.

## Risks / follow-ups

- Users who want to close the day before the evening window (e.g., going to sleep early) currently have no UI affordance in the product-foundation screen flow. The legacy stacked path still has an explicit button, but the product-foundation path does not. Add an explicit "Закрыть день" entry point if the product wants early evening access.
- The time gate uses `getTimeOfDayByHour()` which treats hours before 05:00 as "evening". This matches the existing dashboard state machine, but may need refinement for late-night / early-morning usage.
