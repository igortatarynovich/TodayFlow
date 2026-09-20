# Closed loop v0 — next agent

**Date:** 2026-09-19  
**Status:** **LOCKED** — product path is on live. Do not reopen. Continue fill via `docs/status/P1_LIBRARY_FILL_HANDOFF.md`.  
**Chat:** [Closed loop gratitude D+1](03572416-b86f-4314-b59a-bb0942ca9efe)  
**Goal of this train:** Personal Model daily loop that remembers yesterday — evening = gratitude (Product Flow §4), not 3-way outcome.  
**Ledger:** PR #21 merged → `main` `254ad0bf`. Live compose recreated from that SHA.

---

## 0. First 15 minutes

1. If you are here to continue product work: stop and open `docs/status/P1_LIBRARY_FILL_HANDOFF.md`.
2. Do **not** restore «Закрыть день» / Сделал·Частично·Не сделал. Launch cut 2026-08-30 stands.
3. Product loop is on `main` (`254ad0bf`). Live compose was recreated from that SHA after merge. Ledger ≠ server for later library-fill commits until the next recreate.
4. Time may be simulated (Playwright clock **before** first `/today` mount). Do not wait for 18:00.

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
- Playwright `frontend/e2e/evening-d1-continuity.spec.ts` against live: pass (API origin match, not port). Post-merge re-run: **1 passed (7.0s)** (`PLAYWRIGHT_BASE_URL=https://todayflow.today`).
- First Today daytime after ritual: no `today-story-next-anchor` promising «Вечер»; `Далее` disabled on last step. Evening still time-gated (`getTimeOfDayByHour` ≥ 18:00).
- Guest save is magic-link email (`/onboarding/save`), not password `/auth` first. Intent/reality = First Today chips on `?first=1`.
- **Run 3 gratitude 2026-09-18→19:** wall-clock evening 18.09 (quiet chip) + **same person morning 19.09** `T1.continuity` «Возвращение ясности» / «За спокойный момент» from GET yesterday. Facts in `BEHAVIOR_CHANGE_TEST_V0.md`.
- **Second person:** Елена Day 1 live + **simulated** evening/D+1 (clock hour=20 → 08:00). GET `/day-connection/2026-09-19` `kind=gratitude`; D+1 «за спокойный момент». Wall-clock 20.09 morning is extra, not a blocker.

---

## 4. G1 on merge SHA

`ci.yml` on `main` uses `grep -E` + `cancel-in-progress`. GitHub run for `254ad0bf`: **12/12 jobs success**. G0 stays deferred.

---

## 5. Next (ordered)

1. **Fill:** `docs/status/P1_LIBRARY_FILL_HANDOFF.md` — next type `meditation.silence`.
2. Behavior test cohort (5–10) stays owner-gated.
3. Do not restore Close Day. Do not invent practice from `/practices?limit=1`. G0 stays deferred.

---

## 6. Do not

- Reopen 3-way evening outcome or `TodayEveningProductClose` on production ScreenFlow.
- Invent practice from hub `/practices?limit=1`.
- Invent D+1 copy when GET fails.
- Push more product onto the closed PR #21.
- Claim CI green without GitHub checks on the SHA.
- Untrip `llm_spend.json` / billing latch.

Canon opened this train: `TODAY_PRODUCT_FLOW_V1` §4 · `TODAY_DISPLAY_INVENTORY_V1` v1.3 · `PRODUCT_EXECUTION_TRACKER` Architecture impact 2026-09-18.
