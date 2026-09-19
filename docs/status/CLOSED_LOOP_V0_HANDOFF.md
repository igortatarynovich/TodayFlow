# Closed loop v0 — next agent

**Date:** 2026-09-18 (updated post-merge)  
**Chat:** [Closed loop gratitude D+1](03572416-b86f-4314-b59a-bb0942ca9efe)  
**Goal of this train:** Personal Model daily loop that remembers yesterday — evening = gratitude (Product Flow §4), not 3-way outcome.  
**Ledger:** PR #21 merged → `main` `254ad0bf`. Live compose recreated from that SHA.

---

## 0. First 15 minutes

1. Read this file + `docs/today/TODAY_PRODUCT_FLOW_V1.md` §4 D+1 + `docs/today/TODAY_DISPLAY_INVENTORY_V1.md` v1.3 `T1.continuity` + tracker NOW (CLOSED LOOP v0).
2. Do **not** restore «Закрыть день» / Сделал·Частично·Не сделал. Launch cut 2026-08-30 stands. `BEHAVIOR_CHANGE_TEST_V0.md` Run 3 June rows 7–8 are a dead path — walk gratitude.
3. Product is on `main` (`254ad0bf`). Live compose was recreated from that SHA after merge. Ledger ≠ server until the next recreate.
4. Docs in this working tree (tracker / this file / Run 3 notes) may be local-only until someone commits.

---

## 1. Where it lives

| | |
|---|---|
| Branch | `main` |
| Tip | `254ad0bf` (merge of PR #21) |
| PR | https://github.com/igortatarynovich/TodayFlow/pull/21 **MERGED** |
| Live | `docker-compose.prod.yml` frontend+backend recreated 2026-09-18 post-merge |

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
- Playwright `frontend/e2e/evening-d1-continuity.spec.ts` against live: pass (API origin match, not port). Post-merge re-run: **1 passed (9.4s)** (`PLAYWRIGHT_BASE_URL=https://todayflow.today`).
- First Today daytime after ritual: no `today-story-next-anchor` promising «Вечер»; `Далее` disabled on last step. Evening still time-gated (`getTimeOfDayByHour` ≥ 18:00).
- Guest save is magic-link email (`/onboarding/save`), not password `/auth` first. Intent/reality = First Today chips on `?first=1`.
- **Run 3 gratitude 2026-09-18→19:** wall-clock evening 18.09 (quiet chip) + **same person morning 19.09** `T1.continuity` «Возвращение ясности» / «За спокойный момент» from GET yesterday. Facts in `BEHAVIOR_CHANGE_TEST_V0.md`. Do not restore Close Day.

---

## 4. G1 on merge SHA

`ci.yml` on `main` uses `grep -E` + `cancel-in-progress`. GitHub run for `254ad0bf`: **12/12 jobs success** (Frontend Tests, Backend Tests, iOS XCTest Smoke, iOS Build, smoke, schemas, i18n, copy policy, lint). G0 stays deferred.

---

## 5. Next (ordered)

1. **G2 2.4:** second person × 2 days is closed **with simulated time** (Елена clock hour=20 persist + D+1 recall). Wall-clock 20.09 morning still available as extra confirmation, not a blocker. Behavior test cohort (5–10) stays owner-gated.
2. **P1 fill next:** `meditation.gratitude`. G0 stays deferred (do not untrip `llm_spend.json`).
3. Do not restore Close Day. Do not invent practice from `/practices?limit=1`.

---

## 6. Do not

- Reopen 3-way evening outcome or `TodayEveningProductClose` on production ScreenFlow.
- Invent practice from hub `/practices?limit=1`.
- Invent D+1 copy when GET fails.
- Push more product onto a closed PR. Next work is a new branch from `main`.
- Claim CI green without GitHub checks on the SHA.
- Untrip `llm_spend.json` / billing latch.

Canon opened this train: `TODAY_PRODUCT_FLOW_V1` §4 · `TODAY_DISPLAY_INVENTORY_V1` v1.3 · `PRODUCT_EXECUTION_TRACKER` Architecture impact 2026-09-18.
