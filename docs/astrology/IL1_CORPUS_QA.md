# IL-1 corpus QA — planet claims (not CORE)

**Date:** 2026-08-17  
**Status:** ledger quality audit. Not product meaning. Not CORE scoring. Not a new research pass.  
**Canon:** [INTERPRETATION_LIBRARY_V1.md](./INTERPRETATION_LIBRARY_V1.md)  
**Handoff:** [IL1_HANDOFF.md](./IL1_HANDOFF.md)  
**Gap audit (coverage, not QA):** [IL1_SUN_PLUTO_GAP_AUDIT.md](./IL1_SUN_PLUTO_GAP_AUDIT.md)

This pass inspects the then-existing **303** planet claim rows (snapshot at 1.3.28). It does **not** rewrite `object.function`, add sources, promote `core`, or start a CORE-candidate audit. **1.3.29** reopened discovery afterward; planet claims are now 315. Do not treat this file as the live ingest queue.

| Locus | Status |
|--------|--------|
| Greene *Inner Planets* Venus p.69 | NEED_OWNER |
| Greene *Inner Planets* Mars p.138 | NEED_OWNER |
| Greene *Outer Planets* Uranus / Neptune / Pluto | NEED_OWNER (one volume) |
| Hand Ch.4 Sun / Moon / Mercury | NEED_OWNER (this host; owner direct_read) |
| CORE scoring | **blocked** |
| CORE-candidate audit | **premature** |
| Existing claims / `object.function` | **unchanged** in this pass |

Historical NEED_OWNER list at the time of this QA (still pending as loci; 1.3.29 allows other independent authors to fill the *semantic* gap):

---

## 0. Snapshot

| | Count |
|---|---|
| Planet claim rows | 303 |
| `core` | **0** |
| `supported` / `compared` | 64 (classical-internal, plus Saturn classical+traditional on a few lemmas) |
| `school_specific` / `extracted` | 239 |
| Forbidden row keys (`runtime_semantic_candidate`, `do_not_compare_with`, `classification_gap`) | **0** |
| Exact duplicate `(concept_id, source_id)` | **0** |
| Exact duplicate `normalized_claim` across different `concept_id` on the same planet | **0** |
| Object `function` Sun–Saturn | still classical elemental |
| Uranus / Neptune / Pluto objects | none (claims only) |

`source_class`: professional 182 · classical 99 · psychological 14 · traditional 8.

---

## 1. What is already clean

- **1.3.14 splits held:** Sun father ≠ attraction; traits ≠ health; orbit-fact ≠ solar-return symbolism. Moon cycle-fact ≠ phase-symbolism.
- **Watters vs Hand not merged:** Venus love/desire vs non-coercive bonding; Mars assertive-drive vs survival/individuality. Same `source_class=professional`, different `school` strings — not two school classes, not CORE.
- **Medical / body / iron / healing** live on `field: domains` (or health-named concept_ids) in the **ledger**. They are not copied into `object.domains` (Lilly “large heart” is manners, not cardiology).
- **Combo claims stay combo:** `claim.neptune.maya_with_saturn`, `claim.neptune.artistic_creativity_with_venus`. No Layer 5 objects.
- **Schema freeze held:** no T1–T4, no `runtime_semantic_candidate` field. Ledger-only + gap_notes is the operational substitute.

---

## 2. False equivalence (do not CORE-collapse)

`compared` rows share one `concept_id` and one `normalized_claim` while `original_claim` diverges. That is the intended compared-lemma pattern **inside classical**. Risks for a later CORE pass:

| Lemma | Shared normalized | Originals actually differ |
|--------|-------------------|---------------------------|
| `claim.venus.moist` / `claim.moon.moist` | “primary quality is moisture” | Ptolemy moisture±heat vs Lilly **cold** and moist. Heat/cold is **not** compared; moisture is. Do not later treat temperature as settled. |
| `claim.jupiter.benefic` / `claim.venus.benefic` / `claim.mars.malefic` / `claim.saturn.malefic` | “traditionally benefic/malefic” | Ptolemy elemental-mix vs Lilly fortune/infortune **manners**. Category mix under one ID. |
| `claim.mercury.convertible` (+ Valens) | “takes colour from what it joins” | Valens is capricious **outcomes** / topical catalog, not the same convertibility lemma. Slight over-compare. |
| `claim.saturn.slow_course` (Lilly + Houlding) | “tempo is very slow” | Lilly daily motion vs Houlding “careful, disciplined approach” mixed into tempo. |
| Saturn cold/dry/malefic (classical + **traditional**) | same norms | Two **school classes**, same lemma — closest CORE candidate in the gap audit. Still **not** CORE: no psych/Hand confirmation *of that lemma*; human review not past `compared`. |

Do **not** treat Watters + Hand as two school classes. Do **not** treat Ptolemy + Lilly as CORE.

---

## 3. Remaining compound / wide `normalized_claim`

Not all “and” is a bug (e.g. “solitude and withdrawal” as one Lilly lemma). These are the ones a later school-compare should not treat as a single atom without a split:

**Watters function packages still slash-joined**

- `claim.sun.essential_self` — essential self / day-conscious identity  
- `claim.moon.night_world_function` — night-world / unconscious + solar counterpart  
- `claim.moon.emotion_habit_function` — emotion + need + habit  
- `claim.venus.love_desire_function` — love / desire / attraction (one Watters package; do not merge with Hand)

**Hand function still wide**

- `claim.pluto.radical_transformation` — consciousness / being  
- `claim.pluto.evolutionary_power` — development, decay, dissolution, reformation (sequence, not one verb)  
- `claim.saturn.hand_structure_limits` — limits + rules + structure  
- `claim.uranus.insight_enlightenment` — sudden insight / lightning-flash (close; keep dated 1981)

**Orbit facts still two facts in one row**

- `claim.mercury.orbit_fact` — ~1 year **and** always in/near the Sun’s sign  
- `claim.venus.orbit_fact` — 46° **and** always in/near the Sun’s sign  
- `claim.jupiter.orbit_fact` — ~12 years **and** ~1 year per sign  

Recommended later: split only these, still `school_specific`, still ledger-only for astronomy-in-an-astrology-page. **Not this freeze pass.**

---

## 4. Fact / symbolic inference / medical / runtime

Operational classes already in the ledger (no new schema field):

| Class | How it sits now | QA note |
|--------|------------------|---------|
| **Astronomy fact** | `field: tempo`, concept_id `*_orbit_fact` / `*_cycle_fact` | Keep out of `object.function`. Not Day Sources. |
| **Symbolic inference from fact** | e.g. `claim.sun.solar_return_symbolism`, `claim.moon.phase_symbolism`; Uranus peripheral-awareness from telescopic invisibility | Already gap-noted as symbolic, not astronomy. Do not CORE. |
| **Medical / body** | `field: domains`, `body_*` / health concept_ids | Ledger only. Not `object.domains`. Not runtime copy. |
| **Runtime semantic candidate** | **not a schema field** | Do not add it. Hand bonding / survival / disruption stay `school_specific` until a real CORE pass. |

**Mis-filed `field` (log only):**

- Lilly `claim.saturn.melancholic` and `claim.saturn.studious_of_goods` are `field: domains` — temperament/manners, not a life-domain slot.  
- CPA `claim.jupiter.transit_contradictory` and `claim.jupiter.return_life_development_doorways` are `field: tempo` — transit/theme, not tempo.

Do not retag in this freeze. Retag later would be QA hygiene, not ingest.

---

## 5. Provenance vs ledger

Hand Ch.4 function extras (Venus complementary-union, Mars individuality, Jupiter becoming, Saturn structure/consensus/actualization, etc.) exist in claims and are **not** all copied onto `object.provenance`. That is the locked pointer-only pattern: one Hand function pointer on Venus–Saturn objects; outers have no object. Not a sync bug.

---

## 6. Explicitly not done

- No `evidence_tier` change.  
- No `object.function` / `themes` rewrite.  
- No claim split/merge in JSON.  
- No CORE-candidate scoring.  
- No new bibliography.  
- No pirate-dump fill of NEED_OWNER loci.

**Next (when pages exist):** locked fetch order, independent Greene extraction, then a **new** gap audit + first CORE-candidate audit without automatic promotion — against this QA list, not against a silently averaged modern Sun.
