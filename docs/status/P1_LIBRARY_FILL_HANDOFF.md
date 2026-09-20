# P1 library fill — next agent

**Date:** 2026-09-20  
**Chat:** [P1 fill after closed loop](03572416-b86f-4314-b59a-bb0942ca9efe)  
**Goal of this train:** Keep Practice Library fill moving (lightweight provenance). Closed loop v0 is already on live; do not reopen it.  
**Loop reference:** `docs/status/CLOSED_LOOP_V0_HANDOFF.md` (LOCKED).

---

## 0. First 15 minutes

1. Read this file + `docs/practices/PRACTICE_LIBRARY_FILL_V1.md` §0–§2 + tracker NOW (`P1 PERMISSION SKIP`).
2. Checkout `cursor/p1-self-compassion-loop-notes`. Do **not** start a parallel fill branch unless this one is merged or abandoned.
3. Next type in ledger order: **`affirmation.acceptance`**. Taxonomy meaning: принятие текущего состояния. Distinct from sourced `meditation.acceptance` (allow a feeling for a few breaths without pushing it away). Skip if the kernel is that sitting method, skipped permission/worth slogans, or «I accept myself» without a method.
4. G0 stays deferred. Do **not** untrip `DATA/ops/llm_spend.json`.

**Pass bound:** finish the remaining P1 types once, in ledger order (rest of affirmation, then discipline). Do not chase 42/42. Do not open P2, P0 skip research, billing, or RELEASE_PLAN rewrite on this pass.

---

## 1. Where it lives

| | |
|---|---|
| Branch | `cursor/p1-self-compassion-loop-notes` |
| Tip | last push `ecad2792`; working tree has self_worth + permission skips (uncommitted) |
| Remote | `origin/cursor/p1-self-compassion-loop-notes` (**no PR yet**) |
| Base | `main` `254ad0bf` |
| Live | compose still `254ad0bf` — this library fill is **not** on `todayflow.today` until merge + recreate |

**Commits on this branch (oldest first, last pushed):**

| SHA | What |
|-----|------|
| `4a69a6a1` | P1 `loving_kindness` + `self_compassion`; Run 3 Elena clock-sim notes |
| `46dba113` | P1 `meditation.gratitude` (sit with one thankful fact) |
| `eb0ca483` | Point next work at the P1 fill handoff |
| `d570b0ab` | P1 `meditation.walking_meditation` (steps as the object; not `practice.walking`) |
| `c7453c76` | P1 `meditation.silence` skipped (`family_collapse`) |
| `ecad2792` | P1 `affirmation.self_identity` skipped (`source_gap`) |
| uncommitted | P1 `affirmation.self_worth` skipped; P1 `affirmation.permission` skipped — commit only if asked |

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
- Payload must not contain the type code string (e.g. `acceptance`).
- Public JSON unchanged by a type fill.

---

## 3. Coverage now

- Library items: **153** (unchanged — permission was a skip)
- P1 types sourced: **20/42**
- P1 skipped: `practice.body_scan` (`family_collapse`), `meditation.silence` (`family_collapse`), `affirmation.self_identity` (`source_gap`), `affirmation.self_worth` (`source_gap`), `affirmation.permission` (`source_gap`)
- P0 need cells: 26/26 sourced
- Provenance: v1.73
- Active items this branch: `meditation.loving_kindness.001`, `meditation.self_compassion.001`, `meditation.gratitude.001`, `meditation.walking_meditation.001`

**This-train kernels (do not collapse the next type into these):**

| Type | Kernel | Not |
|------|--------|-----|
| `meditation.self_compassion` | Sit; notice a hard moment / harsh self-talk; answer as to a friend; stop | Loving-kindness to another, acceptance-without-answer, slogan |
| `meditation.acceptance` *(already sourced, P0)* | Notice a difficult inner experience; allow it for a few breaths; do not push it away | Spoken «I accept this» without the sitting allow |
| `affirmation.capability` *(already sourced)* | Spoken «I can handle this» coping statement | Steele values writing, self_identity, self_worth |
| `affirmation.agency` *(already sourced)* | Spoken «I choose the next small step» | Self_identity, capability |
| `practice.boundary_action` *(already sourced)* | One decline of a request you do not have room for | Spoken «I am allowed to…» without the decline act |
| `affirmation.self_identity` *(skipped)* | — | Steele/Cohen values-writing; CCI/NHS self-esteem / worth; slogan («I'm lovable») |
| `affirmation.self_worth` *(skipped)* | — | CCI pie / self-esteem workbook; NHS five-item list; slogan («I am enough»); self_compassion |
| `affirmation.permission` *(skipped)* | — | Saying no (`boundary_action`); rest action; «deserve a break» (self_compassion); assertiveness rights-list; slogan («I am allowed to rest») |

---

## 4. Next fill — `affirmation.acceptance`

Taxonomy meaning: принятие текущего состояния.

1. Confirm a normal technique exists (several official_health / educational sources). Kernel candidate: a brief first-person statement that this present state or fact can be allowed; speak once or twice; stop.
2. If sources collapse into `meditation.acceptance`, `self_compassion`, skipped permission/worth, ACT protocol, or a slogan without a method («I accept myself») — **skip**, do not stretch. Next P1 after this row is `affirmation.boundary`.
3. If accepted: unique `technique.*` id + `affirmation.acceptance.001`. Retrieval must not copy `meditation.acceptance` items / `affirmation.agency.001`.
4. Update: canon JSON + library + coverage counts **154 / 21/42** (if accepted) + tests (`test_coverage_counts`, sourced test, mapping dict) + fill/provenance/coverage/_INDEX/tracker.
5. Tests: `backend/.venv/bin/pytest tests/test_content_library_v1.py::test_coverage_counts tests/test_content_library_v1.py::test_p1_affirmation_acceptance_sourced tests/test_content_library_selection_v1.py -q --tb=short --no-cov` (from `backend/`).
6. Do not commit / PR / deploy unless asked.

---

## 5. Tests already run (local, this machine)

- After `affirmation.self_worth` skip: **20 passed** (`--no-cov`)
- After `affirmation.permission` skip: `test_coverage_counts` + `test_p1_affirmation_permission_skipped` + `test_p1_affirmation_self_worth_skipped` + `test_fill_unfrozen_provisional_probes` + `test_library_valid_against_taxonomy_and_ledger` + `test_technique_canon_lightweight_skip_box` + `test_content_library_selection_v1.py` — **20 passed** (`--no-cov`)

---

## 6. Loop leftovers (not blockers)

- Мария 18→19.09 wall-clock D+1 closed. Елена evening/D+1 closed **with Playwright clock**. Facts: `BEHAVIOR_CHANGE_TEST_V0.md` rows 7–11.
- Behavior test cohort 5–10 stays owner-gated.
- Identities live in the agent store; **do not log JWTs**.

---

## 7. Do not

- Restore Close Day / 3-way evening outcome.
- Invent practice from hub `/practices?limit=1`.
- Invent D+1 copy when GET fails.
- Untrip `llm_spend.json`.
- Open Safety Review / box_breathing / energizing_breath / abstinence research.
- Open P2 library, dual natal SoT, or RELEASE_PLAN rewrite on this pass.
- Merge or recreate compose unless asked.
- Claim the fill is live — ledger ≠ server.
- Stretch permission/acceptance into slogans, workbooks, sitting ACT, or already-sourced families to save coverage.

Canon opened this train: `PRACTICE_LIBRARY_FILL_V1` · `PRACTICE_CONTENT_COVERAGE_V1` · `PRACTICE_TECHNIQUE_PROVENANCE_V1` v1.73 · tracker NOW.
