# P1 library fill — next agent

**Date:** 2026-09-20  
**Chat:** [P1 fill after closed loop](03572416-b86f-4314-b59a-bb0942ca9efe)  
**Goal of this train:** Keep Practice Library fill moving (lightweight provenance). Closed loop v0 is already on live; do not reopen it.  
**Loop reference:** `docs/status/CLOSED_LOOP_V0_HANDOFF.md` (LOCKED).

---

## 0. First 15 minutes

1. Read this file + `docs/practices/PRACTICE_LIBRARY_FILL_V1.md` §0–§2 + tracker NOW (`P1 MEDITATION SILENCE SKIP`).
2. Checkout `cursor/p1-self-compassion-loop-notes` (includes walking_meditation and the `meditation.silence` skip). Do **not** start a parallel fill branch unless this one is merged or abandoned.
3. Next type in ledger order: **`affirmation.self_identity`**. Taxonomy meaning: «I can remain myself». Distinct from `capability` (able to handle this), `agency` (I choose the next step), and skipped `self_trust`. Landscape family also lists self_worth / self_trust — skip if the kernel collapses into those or into a Steele values-affirmation writing protocol.
4. G0 stays deferred. Do **not** untrip `DATA/ops/llm_spend.json`.

---

## 1. Where it lives

| | |
|---|---|
| Branch | `cursor/p1-self-compassion-loop-notes` |
| Tip | this skip commit (`meditation.silence` `family_collapse`) |
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
| HEAD | P1 `meditation.silence` skipped (`family_collapse`) |

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
- Payload must not contain the type code string (e.g. `self_identity`).
- Public JSON unchanged by a type fill.

---

## 3. Coverage now

- Library items: **153** (unchanged — silence was a skip)
- P1 types sourced: **20/42**
- P1 skipped: `practice.body_scan` (`family_collapse`), `meditation.silence` (`family_collapse`)
- P0 need cells: 26/26 sourced
- Provenance: v1.70
- Active items this branch: `meditation.loving_kindness.001`, `meditation.self_compassion.001`, `meditation.gratitude.001`, `meditation.walking_meditation.001`

**This-train kernels (do not collapse the next type into these):**

| Type | Kernel | Not |
|------|--------|-----|
| `meditation.loving_kindness` | Sit; wish yourself well; then one cared-for person; stop | Four-circle MBSR, CFT, self_compassion |
| `meditation.self_compassion` | Sit; notice a hard moment / harsh self-talk; answer as to a friend; stop | Loving-kindness to another, acceptance-without-answer, slogan |
| `meditation.gratitude` | Sit; one ordinary thankful fact; a few breaths; stop | Written three-item list (`practice.gratitude`), well-wishing, open mindfulness |
| `practice.walking` *(already on main)* | Stand; walk a short comfortable distance; stop | Walking as meditation object |
| `meditation.walking_meditation` | Stand; slow short loop; attention on lift–move–land; return to the feet; stop | Sit-break locomotion, in-place mindful_movement, pressing soles while still |
| `meditation.silence` *(skipped)* | — | Choiceless awareness / just sitting (`open_awareness`); unguided sitting (delivery); silent-day / noble silence (`discipline.silence`) |
| `affirmation.capability` *(already sourced)* | Spoken «I can handle this» coping statement | Steele values writing, self_identity |
| `affirmation.agency` *(already sourced)* | Spoken «I choose the next small step» | Self_identity, capability |

---

## 4. Next fill — `affirmation.self_identity`

Taxonomy meaning: I can remain myself.

1. Confirm a normal technique exists (several official_health / educational sources). Kernel candidate: a brief first-person statement that one can remain oneself in this situation; speak once or twice; stop.
2. If sources collapse into `capability`, `agency`, skipped `self_trust`, Steele/Cohen values self-affirmation (write a value, not «remain myself»), or a slogan without a method — **skip**, do not stretch. Next P1 after this row is `affirmation.self_worth`.
3. If accepted: unique `technique.*` id + `affirmation.self_identity.001`. Retrieval must not copy `affirmation.capability.001` / `affirmation.agency.001`.
4. Update: canon JSON + library + coverage counts **154 / 21/42** (if accepted) + tests (`test_coverage_counts`, sourced test, mapping dict) + fill/provenance/coverage/_INDEX/tracker.
5. Tests: `backend/.venv/bin/pytest tests/test_content_library_v1.py::test_coverage_counts tests/test_content_library_v1.py::test_p1_affirmation_self_identity_sourced tests/test_content_library_selection_v1.py -q --tb=short --no-cov` (from `backend/`).
6. Do not commit / PR / deploy unless asked.

---

## 5. Tests already run (local, this machine)

- After `walking_meditation`: library validator + sourced + selection — passed
- After `meditation.silence` skip: `test_coverage_counts` + `test_p1_meditation_silence_skipped` + `test_fill_unfrozen_provisional_probes` + `test_library_valid_against_taxonomy_and_ledger` + `test_technique_canon_lightweight_skip_box` + `test_content_library_selection_v1.py` — **19 passed** (`--no-cov`)
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
- Invent a sitting «silence» method by stripping the object from `open_awareness` / `breath_awareness` / `mindfulness`.
- Stretch `self_identity` into capability, agency, or a values-writing protocol to save coverage.

Canon opened this train: `PRACTICE_LIBRARY_FILL_V1` · `PRACTICE_CONTENT_COVERAGE_V1` · `PRACTICE_TECHNIQUE_PROVENANCE_V1` v1.70 · tracker NOW.
