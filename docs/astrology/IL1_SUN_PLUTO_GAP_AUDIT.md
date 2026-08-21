# IL-1 gap audit — Sun→Pluto live recount

**Date:** 2026-08-18  
**Status:** **1.3.58 live recount** from current ledgers after 1.3.57. Not product meaning. Not CORE scoring.  
**Supersedes:** 1.3.24 / 1.3.44 dashboard snapshots. Do **not** inherit counts or “next = Pluto psychological” from those pages. `IL1_CORPUS_QA.md` remains a **historical** 303-row QA (1.3.28), not this dashboard.  
**Canon:** [INTERPRETATION_LIBRARY_V1.md](./INTERPRETATION_LIBRARY_V1.md) §6.6 · §6.11 · §6.12 · §6.13 · §6.14 · §6.15 · §6.16. Parent: [KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md](../KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md).  
**Handoff:** [IL1_HANDOFF.md](./IL1_HANDOFF.md).

This file records what the ledger already contains. It does **not** rewrite `object.function`, set `active`, invent T1–T4, ingest claims, or open a new bibliography.

**NOW (1.3.81):** Sun–Saturn `canon` filled. Next ≠ this dashboard. Next = 1.3.82 composition smoke-test, not Signs. Do not score CORE from these KPIs. Do not rewrite `function` from this file.

---

## 0. KPI dashboard (order locked)

CORE=0 is a fact. It is **not** the top KPI and must not drive a hunt for artificial consensus.

| KPI | Live (recomputed 1.3.58) |
|-----|--------------------------|
| **Psychological coverage** | COVERED **7** · THIN **2** · DISCOVERED **0** · ACCESS_BLOCKED **1** · EMPTY **0** |
| **School-class coverage** | classical 7 (Sun–Saturn) · traditional 1 (Saturn only) · psychological 9 ingested + Mars ACCESS_BLOCKED · humanistic 10 · Watters `professional` 6 (Sun–Jupiter) · Hand `professional` 7 (Venus–Pluto; Sun/Moon/Mercury unread) |
| **Access-blocked slots** | **1** — Psychological Mars |
| **Unresolved collisions** | **19** function-register / temperature / malefic collisions (see §4). Do not “fix.” |
| **CORE candidates** | **5** Saturn lemmas spanning classical+traditional: `cold` · `dry` · `malefic` · `slow_course` · `well_dignified_austere`. **Not scored.** Psych and Hand do not state those lemmas. |
| **CORE** | **0** |

Catalog facts (ledger, not 1.3.44):

| | Count |
|---|---|
| Draft knowledge objects | 24 (classical seven · 12 houses · 5 aspects). Nothing `active`. |
| Sign objects | 0 |
| Outer-planet objects | 0 (Uranus / Neptune / Pluto = claims only) |
| Planet claim rows | **491** (Sun 55 · Moon 40 · Mercury 37 · Venus 60 · Mars 52 · Jupiter 74 · Saturn 65 · Uranus 33 · Neptune 38 · Pluto 37) |
| Psychological planet claims | **82** (Jupiter 19 · Sun 12 · Saturn 11 · Pluto 10 · Uranus 9 · Neptune 9 · Venus 9 · Moon 2 · Mercury 1 · Mars 0) |
| All claim files (planets+houses+aspects+signs) | 653 |
| Corpus sources | 67 / max 80, all `candidate` |
| `evidence_tier: core` | 0 |
| `evidence_tier: supported` | 64 (classical-internal, plus 5 Saturn traditional) |
| Object `function` (Sun–Saturn) | unchanged classical elemental |

Slot statuses (psych school class only):

| Status | Meaning |
|--------|---------|
| **COVERED** | Normal direct-read psychological ingest exists (principle text, not jacket). |
| **THIN** | 1–2 limited psych claims only (preview crumb). |
| **DISCOVERED** | A quality dedicated locus is identified; extraction not yet done; slot still empty of psych claims. |
| **ACCESS_BLOCKED** | ≥3 quality independent dedicated loci identified; none readable; 0 psych claims. **Not** a semantic gap. |
| **EMPTY** | No quality candidate field yet. |

`NEED_OWNER` remains a **locus** status. `ACCESS_BLOCKED` is a **slot** status ([IL §6.11](./INTERPRETATION_LIBRARY_V1.md)). Humanistic Rudhyar is **not** a psychological fill.

---

## 1. Psychological slots Sun→Pluto

Recomputed from `claims/astro.object.*.json`. One status per planet psych slot.

| Planet | Psych n | Status | Direct-read ingest | Remaining access (not this slot’s emptiness) |
|--------|---------|--------|--------------------|-----------------------------------------------|
| Sun | 12 | **COVERED** | Luminaries preview (2) + Greene Apollon Issue 1 / `in_sungod` (10) | Apollo's Chariot NEED_OWNER (densify COVERED). Hand Ch.4 Sun unread (**professional**, not psych). |
| Moon | 2 | **THIN** | Luminaries preview only | Costello *The Astrological Moon* NEED_OWNER (densify THIN). Independent field 1.3.51 found no other readable dedicated locus. |
| Mercury | 1 | **THIN** | Inner Planets Hermes spontaneity | Remaining Inner Planets Mercury chapters = same-author densify. Hand Ch.4 Mercury unread (**professional**). Independent field 1.3.52 found no other readable dedicated psych locus. |
| Venus | 9 | **COVERED** | Sullivan official-site *Venus and Jupiter* excerpt | Inner Planets p.69 NEED_OWNER (densify COVERED). Dual Goddess seminar body unread. |
| Mars | **0** | **ACCESS_BLOCKED** | none | 3 dedicated loci NEED_OWNER: Inner Planets p.138; Sasportas Dynamics Part 1; Huber *The Planets* p.59. Jacket/webinar/Mythic/Tarnas-thin do not count. **Not EMPTY.** Do not hunt a fourth book. |
| Jupiter | 19 | **COVERED** | CPA page (7) + *By Jove!* Psychology of Jupiter extract (12) | Relating p.39 / remaining book / transcript unread. **Psych paused** (already dense). |
| Saturn | 11 | **COVERED** | Greene Introduction (2) + Tarnas official intro senex (9) | Remaining *Saturn: A New Look* chapters = same-author densify. `themes` still cold/dryness/slowness/solitude/austerity (no `structure`). |
| Uranus | 9 | **COVERED** | Tarnas official intro Prometheus section | Outer Planets / *Art of Stealing Fire* / *Prometheus the Awakener* NEED_OWNER (densify COVERED). Object withheld. |
| Neptune | 9 | **COVERED** | Tarnas official intro Neptune section | *The Astrological Neptune* / Outer Planets NEED_OWNER (densify COVERED). Object withheld. |
| Pluto | 10 | **COVERED** | Greene/Campion *Living with Pluto* interview Parts 1–2 | Outer Planets NEED_OWNER (densify COVERED). Object withheld. **Not empty.** |

**1.3.44 is wrong here:** Pluto is COVERED, not empty. Mars is ACCESS_BLOCKED, not a hunt-for-Pluto-style semantic gap. EMPTY psych slots: **0**. DISCOVERED psych slots: **0** (Mars moved DISCOVERED → ACCESS_BLOCKED at 1.3.57).

---

## 2. School-class matrix (recomputed)

`U` = used in claims. `p` = pending unread. `.` = not on this ledger.

| Planet | Classical | Traditional | Psychological | Humanistic | Watters (prof.) | Hand Ch.4 (prof.) | Object |
|--------|-----------|-------------|---------------|------------|-----------------|-------------------|--------|
| Sun | U 14 | p Skyscript | **COVERED** 12 | U 12 | U 17 | **p — Ch.4 not extracted** | draft, classical `function` |
| Moon | U 13 | p | **THIN** 2 | U 12 | U 13 | **p — Ch.4 not extracted** | draft, classical `function` |
| Mercury | U 11 | p | **THIN** 1 | U 12 | U 13 | **p — Ch.4 not extracted** | draft, classical `function` |
| Venus | U 14 | p | **COVERED** 9 | U 12 | U 13 | U 12 | draft, classical `function` |
| Mars | U 16 | p | **ACCESS_BLOCKED** 0 | U 12 | U 11 | U 13 | draft, classical `function` |
| Jupiter | U 13 | p | **COVERED** 19 (paused) | U 12 | U 14 | U 16 | draft, classical `function` |
| Saturn | U | U 8 Houlding | **COVERED** 11 | U 12 | **.** | U 16 | draft, classical `function` / classical `themes` |
| Uranus | . | . | **COVERED** 9 | U 12 | . | U 12 | **no object** |
| Neptune | . | . | **COVERED** 9 | U 12 | . | U 17 | **no object** |
| Pluto | . | . | **COVERED** 10 | U 12 | . | U 15 | **no object** |

Hand Ch.4 Sun / Moon / Mercury is a **coverage gap inside an already-opened book**, not a missing title. Do not backfill from research-dump atoms. Watters+Hand are both `professional` — not two school classes.

Do **not** pad traditional (`ecb4cbe4`).

---

## 3. Semantic gaps vs access gaps

Do not mix these. ACCESS_BLOCKED is not “we do not know where to look.”

### Semantic (NEED_EVIDENCE-style)

| Gap | What it is | What it is not |
|-----|------------|----------------|
| Moon psych **THIN** | Only Luminaries preview (2). Independent readable densify failed 1.3.51. | Not EMPTY. Costello is access, not missing bibliography. |
| Mercury psych **THIN** | Only Hermes (1). Independent readable densify failed 1.3.52. | Not EMPTY. Remaining Inner Planets chapters are same-author densify. |
| Traditional except Saturn | Living-traditional planet loci not opened for Sun–Jupiter / outers | Not a hunt; freeze `ecb4cbe4` |
| Hand Ch.4 Sun/Moon/Mercury | Professional class unread in an opened book | Not psychological EMPTY |
| Outer objects withheld | Celestial_object slots would force a single-school fake | Not “Pluto psych empty” |
| EMPTY psych slots | **None** | — |
| DISCOVERED psych slots | **None** | Mars was DISCOVERED until 1.3.57 |

### Access (`NEED_OWNER` loci / `ACCESS_BLOCKED` slot)

| Item | Kind | Action when readable |
|------|------|----------------------|
| Psychological Mars (p.138 · Dynamics Part 1 · Huber p.59) | **ACCESS_BLOCKED slot** | Extract that named chapter only. No new discovery. |
| Costello *The Astrological Moon* | NEED_OWNER densify of THIN | Extract; do not hunt a substitute |
| Hand *Horoscope Symbols* Ch.4 Sun → Moon → Mercury | NEED_OWNER professional | Extract; do not backfill |
| Inner Planets Venus p.69 | NEED_OWNER densify of COVERED | Extract; Sullivan already covers the slot |
| Apollo's Chariot | NEED_OWNER densify of COVERED | Extract; Apollon Issue 1 already covers the slot |
| *The Astrological Neptune* / Outer Planets / *Prometheus the Awakener* / *Art of Stealing Fire* | NEED_OWNER densify of COVERED outers | Extract; objects still withheld |

Pirate dumps, jacket, TOC, forum quotes, Mythic extracts, CPA webinar pages, and Tarnas thin survey paragraphs remain **not** loci.

---

## 4. Unresolved collisions (do not “fix”)

19 live collisions. CORE cannot paper over them.

1. **Moon / Venus temperature** — Ptolemy vs Lilly. Valens I.1 does not adjudicate.
2. **Mercury native quality vs convertibility** — Ptolemy alternate dry/moist vs Lilly native cold/dry; convertibility compared only as *takes colour from what it joins*.
3. **Sun benefic** — Ptolemy common vs Lilly fortune-if-dignified.
4. **Saturn dryness vs Valens cold+moisture injury** — not collapsed.
5. **Saturn malefic** — Valens in-sect can bestow good; not added to the compared malefic lemma.
6. **Venus function registers** — moisture ≠ Watters love/desire ≠ Hand non-coercive bonding ≠ Rudhyar inward way / quintessence ≠ Sullivan channel-for-Eros.
7. **Mars function registers** — heat/dryness ≠ Watters assertive-drive ≠ Hand survival ≠ Rudhyar first-gesture / energy-release. Psych still 0 (ACCESS_BLOCKED).
8. **Jupiter function registers** — temperate ≠ Watters enlargement ≠ Hand expansion ≠ Hand integration ≠ CPA contingent-benefic ≠ Greene *By Jove!* individuation-teleology / gluttony-as-unconscious-quest ≠ Rudhyar organizer-of-functions.
9. **Mercury breadth-over-depth (Watters) vs Jupiter overview (Hand)** — future reconciliation; Mercury not rewritten.
10. **Jupiter expansion vs Uranus alien-frame expansion** — Hand distinction; do not merge.
11. **Saturn = structure** — Houlding personal-boundary / Hand structure-limits are school_specific. Ptolemy is not a confirming source. Rudhyar I-am-I / Ring-Pass-Not is another category. Tarnas senex/limit is another category.
12. **Outers** — Uranus, Neptune and Pluto each have Hand **and** Rudhyar **and** a psych ingest; lemmas differ, not CORE.
13. **Uranus function registers** — Hand disruption/mutation ≠ Rudhyar transform/through ≠ Tarnas Prometheus-freedom/own-path.
14. **Neptune function registers** — Hand dissolution ≠ Rudhyar ecstasy/prenatal ≠ Tarnas ocean-of-consciousness / Nirvana-and-Maya. Tarnas Maya is Neptune-alone, not Hand Neptune+Saturn.
15. **Pluto function registers** — Hand reconstruction ≠ Rudhyar celestial-seed ≠ Greene life-force-in-substance.
16. **Sun function registers** — Ptolemy/Lilly heat ≠ Watters essential-self ≠ Greene Luminaries solar-consciousness ≠ Greene Apollon inner-light/carrier ≠ Rudhyar light-as-integration.
17. **Moon function registers** — Ptolemy/Lilly moisture ≠ Watters night-world ≠ Greene embodiment ≠ Rudhyar song-of-life.
18. **Mercury function registers** — convertibility ≠ Watters mind ≠ Greene Hermes ≠ Rudhyar weaver.
19. **Saturn function registers** — cold/dry ≠ Houlding boundary ≠ Greene psychic-process ≠ Hand resistance/structure ≠ Rudhyar I-am-I ≠ Tarnas senex/Chronos/threshold-guardian.

Independent convergence that is **not CORE:** classical compared lemmas (two classical authors). Saturn cold/dry/malefic/slow/austere = classical **+** traditional = CORE *candidates* only.

---

## 5. School-specific additions worth keeping (not CORE)

Keep as tint / later engine distinctions. Do not average into `function`.

| Register | Keep as |
|----------|---------|
| Hand Venus | voluntary non-coercive bonding; complementary union; Venus–Mars polarity |
| Rudhyar Venus | inward way / response-evaluation; quintessence from experience; not necessarily benefic |
| Sullivan Venus | channel-for-Eros / Urania-Pandemos / same-impulse-for-relating-and-creating |
| Rudhyar Mars | first gesture of being; surplus-energy release; desire as life-movement |
| Hand Mars | survival energy; individuality; conflict as mechanism, not essence |
| Hand Jupiter | expansion **and** integration as separate functions |
| Greene *By Jove!* | gluttony-as-unconscious-quest; individuation/teleology; leap toward a bigger pattern |
| Rudhyar Jupiter | Organizer of Functions; purpose→form→function; Soul-compensator |
| Hand Saturn | resistance ≠ punishment; consensus reality ≠ truth; consequences ≠ karma |
| Rudhyar Saturn | I-am-I / Ring-Pass-Not; systolic contraction; fate-tester |
| Tarnas Saturn | senex / Chronos / threshold-guardian / limit-necessity |
| Greene Saturn Introduction | psychic process / pain toward self-discovery |
| Houlding Saturn | personal boundary; mature-through-constraint |
| Hand Uranus | disruption of over-stabilized Saturnine structure; mutation ≠ rebellion |
| Rudhyar Uranus | Saturn forms / Uranus transforms; keyword *through* |
| Tarnas Uranus | Prometheus-figure; freedom-rebellion; own-path; unintegrated as forced change from without |
| Hand Neptune | dissolution of distinction; Maya = Neptune+Saturn (combination, not Neptune-alone) |
| Rudhyar Neptune | Master of Ecstasy; prenatal Great Mother; compassion/at-one-ment |
| Tarnas Neptune | transcendent-ideal; ocean-of-consciousness; Nirvana-and-Maya |
| Hand Pluto | reconstruction after total crisis; death/rebirth symbolic |
| Rudhyar Pluto | Sower of Celestial Seed; hierophant of actual birth |
| Greene/Campion Pluto | life-force-in-substance; grind-or-victim; survival instinct when overwhelmed |
| Rudhyar Sun | Heart vs photosphere; light as integration |
| Greene Apollon Sun | carrier-not-physical-Sun; inner-light; cosmocrator; vocation-as-inner-call |
| Rudhyar Moon | Song of Life; resurrected past |
| Greene Luminaries | solar consciousness / Moon embodiment — polarity in the same book is intentional |
| Greene Inner Planets Mercury | young-Hermes spontaneity |
| Watters 2003 | modern general practical parked in `professional`; body/medical/orbit-fact ledger-only |

Hand outer runtime divider (Uranus = what must change; Neptune = where boundaries blur; Pluto = what can no longer be kept) is logged and **not activated**.

---

## 6. Next research queue (from this recount)

**Retired instructions (do not execute):** “Next research move: Pluto psychological.” “Mars psych is empty, hunt another book.” “CORE=0, go produce consensus.” “Generate another planet source to raise coverage.”

There is **no EMPTY psych slot** left to discover. Independent densify of THIN Moon/Mercury already ran (1.3.51 / 1.3.52). §6.10 empty-slot + densify budget is closed. **1.3.59:** planet fill is research-stable. Coverage counts are not a reason to reopen discovery.

### Next large step (not planet research)

**Layer 2 Signs** — **classification-complete / interpretation-deferred** (1.3.69). Do not reopen sign literature.

**Layer 1 Outers** — **1.3.70** definition/readiness (parent steps 1–4). Claims exist; objects withheld. Do not assemble from Hand.

**1.3.71:** V1 Semantic Inventory **APPROVED**. Literature only against a named `KC-*` row.

**1.3.72:** Outer Planet Draft Representation. Meaning keys optional on draft outers. Objects still withheld.

**1.3.73:** TodayFlow Canon. Product meaning is owner-locked Canon, not CORE. Next = Sun–Pluto claim audit on existing claims. Do not fill outers by intersection.

### Access queue (opportunistic extract only)

**1.3.71:** this is **not** a research backlog. Do not hunt these titles. Extract **only** if a named page becomes legally readable.

When a **named** page becomes legally readable: extract only. `school_specific`. No `function` rewrite. No CORE. No `active`. Do **not** hunt a fourth analog if it stays closed.

0. **Layer 2 Cell C** (`ACCESS_BLOCKED`, 1.3.65) — Arroyo Part II ch.9–12 **or** Martin Vol. 1 structure lessons **or** Hamaker *Elements and Crosses*. Extraction-only; then L2-C7+C8. Do not hunt a fourth. Do not fill from Pulse.
1. **Psychological Mars** (`ACCESS_BLOCKED`) — Inner Planets p.138 **or** Dynamics Part 1 **or** Huber p.59. Highest access priority among planets: only ACCESS_BLOCKED psych slot. Do not hunt a fourth book.
2. **Costello *The Astrological Moon*** — densify THIN Moon. NEED_OWNER.
3. **Hand Ch.4 Sun → Moon → Mercury** — professional coverage inside an opened book. NEED_OWNER. ISBN 9780914918165.
4. **Inner Planets Venus p.69** — densify COVERED Venus. NEED_OWNER.
5. **Apollo's Chariot** — densify COVERED Sun. NEED_OWNER.
6. **Outer densify** (*The Astrological Neptune* · Outer Planets · *Prometheus the Awakener* · *Art of Stealing Fire*) — COVERED slots; objects still withheld; lower product urgency.

### Do not

- Hunt Mars discovery or a fourth Mars book
- Unpause Jupiter psych
- Pad traditional
- Treat remaining Inner Planets Mercury chapters as filling EMPTY
- Auto-pick Tarnas thin Sun/Moon/Mercury/Mars survey paragraphs
- Surrogate-fill NEED_OWNER with summaries of those authors
- Score CORE or promote the five Saturn candidates
- Materialize Uranus/Neptune/Pluto objects
- Materialize 12 sign objects from the first modern cookbook
- Mix Profile v2 / Foundation UI / landing into IL commits

### If no named planet locus is newly readable

Stop. Do not continue Layer 2 literature. Do not invent a 20th Mars source. Do not start CORE scoring. Next named work is owner approval of [KNOWLEDGE_CORE_V1_SEMANTIC_INVENTORY.md](./KNOWLEDGE_CORE_V1_SEMANTIC_INVENTORY.md).

---

## 7. What this recount did not do

- No claims added or removed.
- No `evidence_tier` changed to `core` or `supported`.
- No `object.function` / `themes` rewrite.
- No Uranus/Neptune/Pluto objects materialized.
- No Layer 5 combo objects.
- No pirate-dump fill.
- CORE still unscored.

---

## 8. Historical ingest log (not live SoT)

1.3.24 opened this audit. 1.3.44 was a Neptune-discovery checkpoint whose “next = Pluto psychological” **must not** be reused. 1.3.45–1.3.57 filled or blocked the empty psych slots. Details live in [INTERPRETATION_LIBRARY_V1.md](./INTERPRETATION_LIBRARY_V1.md) changelog and [IL1_HANDOFF.md](./IL1_HANDOFF.md).

- **1.3.45** Pluto psych ingest (Greene/Campion). Object withheld.
- **1.3.46** Uranus psych ingest (Tarnas intro). Object withheld.
- **1.3.47** Neptune psych ingest (Tarnas intro Neptune section). Object withheld.
- **1.3.48** Venus psych ingest (Sullivan excerpt).
- **1.3.50** Sun psych densify (Apollon Issue 1).
- **1.3.51** Moon densify skip (still THIN).
- **1.3.52** Mercury densify skip (still THIN).
- **1.3.53** Saturn psych densify (Tarnas senex).
- **1.3.54–1.3.56** Mars discovery, no ingest (p.138 · Dynamics · Huber cataloged unread).
- **1.3.57** Psychological Mars `ACCESS_BLOCKED`.
- **1.3.58** this live recount. Dashboard numbers above replace 1.3.44.
- **1.3.59** planet fill research-stable; Layer 2 Signs definition is the next large step. Access queue stays opportunistic.
- **1.3.60** Layer 2 schools + source types. Next = literature map from §6.14, not Arroyo/Rudhyar pending IDs.
- **1.3.61** Layer 2 literature map. Landscape, not shortlist.
- **1.3.62** Layer 2 selection criteria locked. Next = 1.3.63 shortlist. Cell C unscored.
- **1.3.63** Layer 2 shortlist locked. Next = 1.3.64 Houlding ontology extract. Cell C remains a cell.
- **1.3.64** Houlding triplicity ontology extracted. No sign objects.
- **1.3.65** Layer 2 Cell C `ACCESS_BLOCKED`.
- **1.3.66** Pulse Part One extracted (humanistic). Schema requiredness demoted in 1.3.67.
- **1.3.67** Later-interpretive optional on IL-1 draft `type=sign`.
- **1.3.68** Twelve Lilly classification-only sign drafts. Later-interpretive omitted.
- **1.3.69** Layer 2 classification-complete / interpretation-deferred. Next = do not reopen sign literature.
- **1.3.70** Layer 1 Outers definition/readiness. Next = scoped optional-on-draft or keep withheld; not Hand ingest.
