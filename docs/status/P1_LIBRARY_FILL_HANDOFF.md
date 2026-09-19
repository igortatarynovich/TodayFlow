# P1 library fill — next agent

**Date:** 2026-09-19  
**Chat:** [P1 fill after closed loop](03572416-b86f-4314-b59a-bb0942ca9efe)  
**Goal of this train:** Keep Practice Library fill moving (lightweight provenance). Closed loop v0 is already on live; do not reopen it.  
**Loop reference:** `docs/status/CLOSED_LOOP_V0_HANDOFF.md` (LOCKED).

---

## 0. First 15 minutes

1. Read this file + `docs/practices/PRACTICE_LIBRARY_FILL_V1.md` §0–§2 + tracker NOW (`P1 MEDITATION GRATITUDE`).
2. Checkout `cursor/p1-self-compassion-loop-notes` (tip `46dba113`). Do **not** start a parallel fill branch unless this one is merged or abandoned.
3. Next type in ledger order: **`meditation.walking_meditation`**. Distinct from already-accepted `practice.walking` (locomotion sit-break; footsteps are **not** the object).
4. G0 stays deferred. Do **not** untrip `DATA/ops/llm_spend.json`.

---

## 1. Where it lives

| | |
|---|---|
| Branch | `cursor/p1-self-compassion-loop-notes` |
| Tip | `46dba113` |
| Remote | `origin/cursor/p1-self-compassion-loop-notes` (pushed; **no PR yet**) |
| Base | `main` `254ad0bf` |
| Live | compose still `254ad0bf` — this library fill is **not** on `todayflow.today` until merge + recreate |

**Commits on this branch (oldest first):**

| SHA | What |
|-----|------|
| `4a69a6a1` | P1 `loving_kindness` + `self_compassion`; Run 3 Elena clock-sim notes |
| `46dba113` | P1 `meditation.gratitude` (sit with one thankful fact) |

---

## 2. Locked (do not reopen)

**Closed loop (already on `main` / live):**

- Evening = gratitude only. No «Закрыть день». No 3-way outcome.
- D+1 = `GET /day-connection/{yesterday}` → `T1.continuity`. Empty omit. No invent on transport failure.
- MY DAY practice = `GET /practices/select`. Never `/practices?limit=1`.
- Time may be simulated (Playwright `clock.setFixedTime` **before** first `/today` mount; `isEveningTime` is `useMemo([])`).

**Fill law (`PRACTICE_LIBRARY_FILL_V1`):**

- LLM is not a method source. Several quality sources confirm the method exists.
- One technique record. Debate → `skipped` / `skipped_for_now`. Do not invent a type to save coverage.
- `allowed_claims[]` empty. Meaning does not emit `item_id` / `technique_id`.
- Payload must not contain the type code string (e.g. `walking_meditation`).
- Public JSON unchanged by a type fill.

---

## 3. Coverage now

- Library items: **152**
- P1 types sourced: **19/42** (`practice.body_scan` skipped, `family_collapse`)
- P0 need cells: 26/26 sourced
- Provenance: v1.68
- Active items this branch: `meditation.loving_kindness.001`, `meditation.self_compassion.001`, `meditation.gratitude.001`

**This-train kernels (do not collapse the next type into these):**

| Type | Kernel | Not |
|------|--------|-----|
| `meditation.loving_kindness` | Sit; wish yourself well; then one cared-for person; stop | Four-circle MBSR, CFT, self_compassion |
| `meditation.self_compassion` | Sit; notice a hard moment / harsh self-talk; answer as to a friend; stop | Loving-kindness to another, acceptance-without-answer, slogan |
| `meditation.gratitude` | Sit; one ordinary thankful fact; a few breaths; stop | Written three-item list (`practice.gratitude`), well-wishing, open mindfulness |
| `practice.walking` *(already on main)* | Stand; walk a short comfortable distance; stop | Walking as meditation object |

---

## 4. Next fill — `meditation.walking_meditation`

Taxonomy meaning: meditation in motion. Practice-class walking already says: *“walking_meditation (footsteps as the meditation object)”*.

1. Confirm a normal technique exists (several official_health / educational sources). Kernel in our words: slow walk, attention on the steps, return when the mind wanders, stop.
2. If sources collapse into `practice.walking` (just get up and move) or `mindful_movement` (in-place) — **skip**, do not stretch. Next P1 after this row is `meditation.silence`.
3. If accepted: `technique.walking_meditation` (or equivalent unique id) + `meditation.walking_meditation.001`. Retrieval must not copy `practice.walking.001` (that item is locomotion / sit-break).
4. Update: canon JSON + library + coverage counts **153 / 20/42** + tests (`test_coverage_counts`, sourced test, mapping dict) + fill/provenance/coverage/_INDEX/tracker.
5. Tests: `backend/.venv/bin/pytest tests/test_content_library_v1.py::test_coverage_counts tests/test_content_library_v1.py::test_p1_meditation_walking_meditation_sourced tests/test_content_library_selection_v1.py -q --tb=short`
6. Do not commit / PR / deploy unless asked.

---

## 5. Tests already run (local, this machine)

- After `self_compassion`: library + selection **18 passed**
- After `gratitude`: library + selection **19 passed** (`test_p1_meditation_gratitude_sourced` included)
- Do not claim CI green until GitHub checks on the SHA

---

## 6. Loop leftovers (not blockers)

- Мария 18→19.09 wall-clock D+1 closed. Елена evening/D+1 closed **with Playwright clock** (hour=20 → 08:00 next day, quiet chip, recall «за спокойный момент»). Facts: `BEHAVIOR_CHANGE_TEST_V0.md` rows 7–11.
- Optional extra: calendar morning 2026-09-20 for clock-Elena. Not required to continue fill.
- Behavior test cohort 5–10 stays owner-gated.
- Identities live in the agent store; **do not log JWTs**.

---

## 7. Do not

- Restore Close Day / 3-way evening outcome.
- Invent practice from hub `/practices?limit=1`.
- Invent D+1 copy when GET fails.
- Untrip `llm_spend.json`.
- Open Safety Review / box_breathing / energizing_breath / abstinence research.
- Merge or recreate compose unless asked.
- Claim the fill is live — ledger ≠ server.

Canon opened this train: `PRACTICE_LIBRARY_FILL_V1` · `PRACTICE_CONTENT_COVERAGE_V1` · `PRACTICE_TECHNIQUE_PROVENANCE_V1` v1.68 · tracker NOW.
