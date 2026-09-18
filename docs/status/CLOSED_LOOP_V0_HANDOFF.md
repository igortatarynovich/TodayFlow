# Closed loop v0 — next agent

**Date:** 2026-09-18  
**Chat:** [Closed loop gratitude D+1](03572416-b86f-4314-b59a-bb0942ca9efe)  
**Goal of this train:** Personal Model daily loop that remembers yesterday — evening = gratitude (Product Flow §4), not 3-way outcome.

---

## 0. First 15 minutes

1. Read this file + `docs/today/TODAY_PRODUCT_FLOW_V1.md` §4 D+1 + `docs/today/TODAY_DISPLAY_INVENTORY_V1.md` v1.3 `T1.continuity` + tracker NOW (CLOSED LOOP v0).
2. Do **not** restore «Закрыть день» / Сделал·Частично·Не сделал. Launch cut 2026-08-30 stands. `BEHAVIOR_CHANGE_TEST_V0.md` Run 3 still describes that dead path — walk the **live** path (gratitude), do not implement the old checklist.
3. Do **not** push more commits onto PR #21 until `ci.yml` can land (`workflow` scope). Each push starts a full 12-job suite with no cancel-in-progress.
4. Live frontend on this host already includes the loop + daytime ritual handoff cut. Ledger ≠ server.

---

## 1. Where it lives

| | |
|---|---|
| Branch | `loop/gratitude-d1-practice-select` |
| Tip | `8f9558de` |
| PR | https://github.com/igortatarynovich/TodayFlow/pull/21 |
| Base | `main` |
| Working tree | clean vs origin (this handoff file may be local-only) |
| Live | `docker-compose.prod.yml` frontend recreated after `8bd3424e` / `8f9558de` |

**Commits on the PR (oldest first):**

| SHA | What |
|-----|------|
| `78b37d68` | Close Today loop: gratitude D+1 + `GET /practices/select` |
| `76f66f80` | Register `T1.continuity` in Grammar catalog |
| `8bd3424e` | Hide ritual «Вечер» handoff when evening step is off |
| `8f9558de` | Emit `T1.continuity` on live Today grammar frame |

---

## 2. Locked (do not reopen)

- Evening job = gratitude (`TodayEveningGratitudeBlock`). Persist `POST /day-connection/{date}`: `evening_completed` + `evening_observations.kind=gratitude` + optional `morning_focus` (max 100 chars, already-shown thesis, not a rewrite).
- D+1 TODAY = one user line `T1.continuity` from `GET /day-connection/{yesterday}`. Empty omit. No invent on transport failure («Нет соединения.» / «Не удалось загрузить.»). localStorage = same-device fallback only.
- MY DAY practice = `GET /practices/select` from Global `primary_energy` → need cell (`frontend/src/lib/todayPracticeSelect.ts`). Miss omits. Never `/practices?limit=1`.
- `showEveningClose={false}` on production ScreenFlow. `TodayEveningProductClose` stays unmounted on the product path.
- Meaning value-gate stays backend. FE = null/empty/trivial-dupe defense.

**Architecture impact** is already in the PR body and tracker (2026-09-18). Public JSON: no new fields. Additive use of existing DayConnection observations.

---

## 3. Verified on live (`todayflow.today`)

- Authenticated `/today`: D+1 recall from yesterday DayConnection; no «Закрыть день»; MY DAY catalog practice (Дыхание 4-7-8 from select).
- Playwright `frontend/e2e/evening-d1-continuity.spec.ts` against live: pass (API origin match, not port). Re-run 2026-09-18: **1 passed (8.7s)** (`PLAYWRIGHT_BASE_URL=https://todayflow.today`).
- First Today daytime after ritual: no `today-story-next-anchor` promising «Вечер»; `Далее` disabled on last step. Evening still time-gated (`getTimeOfDayByHour` ≥ 18:00).
- Guest save is magic-link email (`/onboarding/save`), not password `/auth` first. Intent/reality = First Today chips on `?first=1`.
- **Run 3 gratitude 2026-09-18:** calendar D+1 without route-mock — POST gratitude on `2026-09-17`, open `/today` on `2026-09-18`, slot `today-entity-continuity-recall` shows yesterday focus + «Вечер сохранён благодарностью». Facts in `BEHAVIOR_CHANGE_TEST_V0.md`. Magic-link claim and second-person 2-day still open. Do not restore Close Day.

---

## 4. Blocker — PR not merge-ready until iOS Smoke green

**Was:** iOS XCTest Smoke red because `ci.yml` used `rg` (not on `macos-latest`). Same fail on `main`. No `cancel-in-progress` (four pushes = four full suites).

**Fix on this branch:** `ci.yml` now `grep -E` + `concurrency.cancel-in-progress` + timeouts 12/15/12/12. Pushed after `workflow` scope. Do not claim green until GitHub checks on the SHA.

Cloud autopilot [Autopilot PR 21](bc-19910920-872e-4e3d-a7f0-458f66d6630f) had confirmed the same blocker and did not change product code.

---

## 5. Next (ordered)

1. **`ci.yml` landed on this PR** (`grep -E` + `cancel-in-progress` + job timeouts). Re-run CI. Merge PR #21 only after iOS Smoke green (owner merges).
2. Run 3 leftovers remaining: wall-clock evening ≥ 18:00 MSK (Playwright clock already green); team 2 calendar days. Magic-link claim in UI done 2026-09-18 (SMTP unset on live → JWT fallback; refine skip → authenticated Today). Second account calendar D+1 OK.
3. G1 leftover was this same `rg` fail on `main`. After merge, `main` inherits the grep pick. G0 stays deferred.

---

## 6. Do not

- Reopen 3-way evening outcome or `TodayEveningProductClose` on production ScreenFlow.
- Invent practice from hub `/practices?limit=1`.
- Invent D+1 copy when GET fails.
- Push workflow-less product commits onto #21 (queues another full suite).
- Claim CI green without GitHub checks on the SHA.
- Untrip `llm_spend.json` / billing latch.

Canon opened this train: `TODAY_PRODUCT_FLOW_V1` §4 · `TODAY_DISPLAY_INVENTORY_V1` v1.3 · `PRODUCT_EXECUTION_TRACKER` Architecture impact 2026-09-18.
