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

## 4. Blocker — PR not merge-ready

**iOS XCTest Smoke** red on this PR **and on `main`**: `.github/workflows/ci.yml` uses `rg` to pick an iPhone simulator; `rg` is not on `macos-latest`. Job never reaches `xcodebuild`.

All other checks on `8f9558de`: green (Frontend Tests, Backend Tests, iOS Build, schemas, lint, smoke, i18n, iOS Copy Policy). `mergeable: MERGEABLE`, `mergeStateStatus: UNSTABLE`.

**CI delay cause:** no `concurrency.cancel-in-progress`. Four pushes = four full 12-job runs (~5.5 min `Backend Tests` each). Frontend Tests job is sequential Jest+coverage+`next build`+Playwright (~4 min).

**Fix is ready, cannot push from this host’s OAuth token** (`gist`, `read:org`, `repo` — no `workflow` scope). HTTPS origin. No SSH key.

Local artifacts (do not lose):

- Branch `ci/cancel-and-grep` (commit `1ab77486`)
- Patch: agent store `ci-cancel-and-grep.patch` and `/tmp/0001-fix-ci-cancel-stacked-runs-cap-job-time-pick-iOS-sim.patch`

Patch contents: `concurrency` group on `github.ref` + `cancel-in-progress`; `timeout-minutes` 12/15/12/12 on backend/frontend/ios-build/ios-test; `rg` → `grep -E`.

**Unblock:** GitHub UI edit of `ci.yml` on the PR branch, **or** `gh auth refresh -s workflow` then cherry-pick/push `ci/cancel-and-grep` onto `loop/gratitude-d1-practice-select`. Do not stack more product pushes until that lands.

Cloud autopilot [Autopilot PR 21](bc-19910920-872e-4e3d-a7f0-458f66d6630f) confirmed the same blocker and did not change product code (session rule: no workflow edits just to go green).

---

## 5. Next (ordered)

1. Land `ci.yml` (grep + cancel-in-progress) from an account that can push workflows. Re-run CI. Merge PR #21 only after iOS Smoke green (owner merges). Still blocked on this host (`gist`/`read:org`/`repo`, no `workflow`).
2. Run 3 gratitude leftovers: magic-link claim in UI; optional wall-clock evening ≥ 18:00 MSK (Playwright clock already green); second person D+D+1.
3. G1 leftover is this same `rg` fail on `main`. G0 (Token Factory / LLM latch ~$5) stays deferred.

---

## 6. Do not

- Reopen 3-way evening outcome or `TodayEveningProductClose` on production ScreenFlow.
- Invent practice from hub `/practices?limit=1`.
- Invent D+1 copy when GET fails.
- Push workflow-less product commits onto #21 (queues another full suite).
- Claim CI green without GitHub checks on the SHA.
- Untrip `llm_spend.json` / billing latch.

Canon opened this train: `TODAY_PRODUCT_FLOW_V1` §4 · `TODAY_DISPLAY_INVENTORY_V1` v1.3 · `PRODUCT_EXECUTION_TRACKER` Architecture impact 2026-09-18.
