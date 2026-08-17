# IL-1 handoff — next agent

**Date:** 2026-08-17  
**Owner intent:** IL-1 catalog is **frozen for conceptual additions**. Catalog/priority transfer SHA: **`ecb4cbe4`**. Do not start another blind planet research pass. The ingest of the Sun–Jupiter research rows is closed; remaining work is **targeted** closed loci named below. Do not redesign TodayFlow. Do not polish the methodology document. Do not reopen sequence / ontology / evidence.

**Catalog state (correct, not a gap):** 24 draft / 0 active / 0 sign objects / CORE unscored. Planet `function` slots remain classical elemental. Watters 2003 is **not** traditional. Greene Luminaries Sun/Moon are psychological `school_specific`, not CORE.

**Research-first (operational):** search legally available loci before asking the owner. Order: Google Books preview → publisher previews (Calaméo / Weiser) → Open Library / controlled borrowing → library sources. Owner is asked only when a **specific** needed locus (edition + pages X–Y) is closed. Do not ask the owner to buy, photograph, or paraphrase a book as the default step.

Canon: [`INTERPRETATION_LIBRARY_V1.md`](./INTERPRETATION_LIBRARY_V1.md) (**1.3.14** Watters/Greene atomic refine + Inner Planets Mercury).  
Today Meaning SoT remains [`docs/today/TODAY_CONTENT_PIPELINE_V1.md`](../today/TODAY_CONTENT_PIPELINE_V1.md). IL is pipeline step 2 lookup only.

Prior chat: [IL-1 ingest and gates](0dd63406-cfcc-47b2-b184-780f5aada991)

---

## 0. First 15 minutes

1. Read this file + IL § Sequence + **Activation gates** + §6 ingest + Layer 1–4 fill-rules.
2. 1.3.8 activation gates are **committed** (`3c62a5c6`). Do not reopen them.
3. IL ingest lives on short-lived `il/il-1-ingest` (from that tip). Do **not** mix Profile v2 / Foundation UI / landing / Trust / motion into IL commits. Working tree on the host often has those dirty; leave them.
4. Search a legally available next locus yourself (research-first rule above). If found: ingest (`locus → claims → normalization → draft`). If a **specific** page is closed: ask the owner for pages X–Y of that edition. If nothing is needed: **stop**. Do not pad classical/traditional ingest. Do not invent work.

v1.3.8 is closed: `requires_action` and Layer 5 stay draft→active gates, not IL-1 re-ontology.  
`876e6f98` is closed as first traditional class: classical layer not rewritten.  
`ecb4cbe4` is the catalog/priority transfer: do not pad traditional.  
`9a0fe7c2` closed leftover busywork only; catalog unchanged. First psychological class = Greene Introduction (1.3.11). Houlding *Saturn: The Great Teacher* = 1.3.12. **1.3.13** = Watters Sun–Jupiter (professional/modern practical) + Greene *The Luminaries* Sun/Moon. **1.3.14** = atomic refine + Greene *Inner Planets* Mercury.

---

## 1. Locked (do not reopen)

Sequence: **IL-0 ✅ → IL-1 now → IL-2 composition rules → IL-3 engine → IL-4 expression**.

This sequence *is* the knowledge engine (atoms + provenance → composition rules → themes → expression). It is not a library of texts. Do not add a second vision document.

- IL-1 is **surface-neutral**: no `today_message` / `profile_blurb` / `compatibility_line`. `surface` exists only on expression packs (IL-4).
- Objects must map to entities the **current Swiss + Astro/calculation layer can emit**. No Uranus/Neptune/Pluto/ASC/MC until a real opened locus **and** calc emits them.
- Swiss = runtime ephemeris input. **Licensing** is a parallel legal gate, not a research blocker. Do not write “Swiss outside IL.”
- If sources do not fit the ontology: **log a concrete gap** from real material. Do **not** expand the schema “just in case.”
- Canonical objects must **not be richer than the evidence base**. Do not polish drafts into a modern average.
- Remaining psychological / professional lemmas wait for **opened** pages — no backfill from model memory or jacket copy.
- Ingest = paraphrase + locus, never paste translations/scrapes.
- Evidence: `core` | `supported` | `school_specific` | `editorial`. CORE ≈ intersection of ingested **school classes**, not two classical authors. Engine primary theme only from `core` ∪ `supported`.
- meaning ≠ relevance ≠ expression. Profile changes **priority**, not meaning. One object feeds Profile / Today / Compatibility.

### Activation gates (not methodology)

Stop **before `status: active`**, not before IL-1 draft.

1. **`requires_action: false`** on an unattested locus ≠ “this aspect does not require action.” Draft + unread by runtime is OK. **`active` with that ambiguity is forbidden** until representation is unambiguous **or** ingest/runtime contract forbids reading the boolean as a negative assertion. Schema stays boolean for IL-1.
2. IL-1 Layer 5 gold list (~50–60) = **curated candidates**, not proven `non_compositional` exceptions. IL-2 may demote curated → composed.

User-facing provenance later = school band (*Traditional* · *Modern psychological* · *Cross-tradition* · *TodayFlow synthesis*), not “Lilly p.57”. That is Trust Layer / Expression, not IL ingest.

Public brand copy SoT: [`docs/content/TODAYFLOW_TRUST_LAYER.md`](../content/TODAYFLOW_TRUST_LAYER.md). Do not turn IL into a marketing doc.

---

## 2. Done

### Git (IL catalog)

| SHA | What |
|-----|------|
| `c9fe3d05` | Schema, corpus, classical seven drafts (Sun–Saturn) |
| `805bbbdb` | 12 houses (Lilly I.7) + 5 aspects (Ptolemy) + sign classifications; signs withheld |
| `b9f2643e` | Lilly I.1 aspect **geometry** compared; I.16 sign QUALITY claims; commanding grouping compared |
| `3c62a5c6` | Activation gates 1.3.8 (requires_action / Layer 5 candidates) + handoff |
| `5dee20a5` | Trust Layer (brand) — **not** IL ingest |

IL ingest after 1.3.8: branch `il/il-1-ingest`. `edc37221` Valens/Lilly I.19. `876e6f98` Houlding traditional class. **`ecb4cbe4` = catalog/priority transfer** (do not pad traditional). `9a0fe7c2` leftover freeze only. **1.3.11** = first psychological class (Greene Introduction). **1.3.12** = Houlding Saturn article (living-traditional planet locus; not a T1–T4 import). **1.3.13** = Watters Sun–Jupiter (professional/modern practical, not traditional) + Greene *Luminaries* Sun/Moon. **1.3.14** = atomic refine + Inner Planets Mercury.

### Catalog (all `draft`, nothing `active`)

Runtime: `DATA/reference/astrology/interpretation_v1/`

- **24 objects** in `objects_v1.json`: 7 planets · 12 houses · 5 major aspects
- **0** `type=sign` objects
- **37** claim ledgers in `claims/`
- Schema example fixture `status: schema_example` is **not** meaning SoT (modern Saturn lemmas there are not product meaning)

| Layer | IDs | Provenance honesty |
|-------|-----|--------------------|
| 1 planets | `astro.object.{sun,moon,mercury,venus,mars,jupiter,saturn}` | Ptolemy I.4–I.7 + Lilly CA I.8–I.14 + Valens I.1. Saturn also Greene Introduction (psychic-process `school_specific`) and Houlding *Great Teacher* (boundary/constraint `school_specific`; cold/dry/malefic/slow compared). Sun–Jupiter also Watters 2003 (`professional` / `modern_general_practical`, `school_specific` — **not** traditional). Sun/Moon also Greene *Luminaries* preview; Mercury also Greene *Inner Planets* Hermes-spontaneity (`psychological`, `school_specific`). `function` still elemental (Ptolemy/Lilly), not a Valens, Watters, Greene, or Houlding average |
| 2 signs | **claims only** `astro.sign.{aries…pisces}` + `astro.sign.classifications` | Lilly QUALITY; Valens I.2 Aries fiery *and* watery. Psych slots unattested |
| 3 houses | `astro.house.01`–`12` | Object `domain` still Lilly CA I.7. Valens IX compared on thin lemmas. Houlding houses extract opened for 1/6/7/12 only — personality and known-enemies rule not copied into `domain` |
| 4 aspects | conjunction / sextile / square / trine / opposition | Geometry compared. Planetary orbs compared (Lilly I.19 + Houlding). Square-not-simply-bad is school_specific. `interaction` not rewritten |
| 5 combos | none materialized | gold list in IL §8 = candidates |

Saturn object slots stay classical: cooling quality / cold / dryness / slowness / solitude / austerity. Sun–Jupiter `function` stays elemental. Watters essential-self / night-world / mind / desire / drive / expansion stay `school_specific` in the ledger and in provenance pointers only. Greene Luminaries solar-consciousness / embodiment stay `school_specific`. Do not rewrite `function` into a modern identity average. **Not** CORE.

### Opened loci (citable; ingest only from these)

**Ptolemy, Tetrabiblos**, Ashmand 1822, Gutenberg 70850:

- I.4–I.7 planets
- I.13 four angles (temperament — not 12 houses)
- I.14–I.15 sign classes
- I.16 configurations
- I.17 commanding/obeying (summer/winter grouping **and** equinox pair-relation)
- I.18 beholding / equal power
- I.21 triplicities (winds/rulers, **not** fire/earth/air/water on signs)
- I.27 application / bodily conjunction

**Lilly, Christian Astrology** 1659, Wikisource djvu:

- I.1 aspects, printed p.25–26 (geometry + good/enmity/concord)
- I.7 houses, printed ~p.50–56, djvu 75–81
- I.8–I.14 planets Saturn→Moon
- I.16 divisions, djvu 111–114; nature/quality of 12 signs, printed ~p.93–98
- I.16 commanding list, printed p.91, djvu 117
- I.16 Antiscion / Contrantiscion, printed p.89–91 (cites “PTOL. APHO.” — attribution ≠ consensus)
- I.19 terms/aspects, printed ~p.105 (Archive.org 1647/1659 text): partile/platick, planetary moiety orbs (two tables), imperfect enmity vs perfect hatred

**Valens, Anthologies**, Riley unperfected English (paraphrase only; Greek PD):

- I.1 Nature of the Stars (seven planets)
- I.2 Nature of the Twelve Signs (Aries opened; fiery *and* watery weather)
- I.3 50 terms — **dignity**, not Layer 2; not copied (Foundation §2.5)
- IX The XII Places (Riley 2K;3P)

**Houlding / Skyscript** (copyrighted; paraphrase only):

- *The Classical Origin and Traditional Use of Aspects* (Traditional Astrologer Mag. 8, 1995; Skyscript 2004)
- *The Houses: Temples of the Sky* 1st ed. 1996 extracts: 1st, 6th, 7th, 12th (Skyscript 2003)
- *Saturn: The Great Teacher* (Skyscript, December 2003). Introduction + Psychological Astrology ingested atomically. Mundane Signification catalog **not** copied. Houlding quoting Greene's membrane lemma **not** ingested as Greene.

**Watters, Astrology For Today** (copyrighted; paraphrase only):

- 2003, Carroll & Brown, London. Skyscript republications: sun1 / moon1 / mercury1 / venus1 / mars1a / jupiter1.html. `primary_read` = access quality, not historical primacy. Classification gap: modern general practical. Parked `src.professional.watters_today` (`source_class=professional`, `school=modern_general_practical`). Atomic splits at ingest (father≠attraction, traits≠health, orbit-fact≠symbolism). Body/health/fertility rows stay in the ledger, **not** `object.domains`. Research `runtime_semantic_candidate` is not a schema field.

**Greene, Saturn: A New Look at an Old Devil** (copyrighted; paraphrase only):

- Weiser Classics 2021 (ISBN 978-1-57863-735-5; 288 pp.). Introduction starts p.1. Opened via Red Wheel/Weiser Calaméo two-chapter preview: Introduction p.1–8.
- Same preview includes ch.1 watery signs/houses (p.9–34) — **not ingested** (planet-in-house is Layer 5).
- 2011 Weiser and 1976 Open Library `saturnnewlookato00gree` exist; Introduction did not require borrow.

**Greene / Sasportas, The Inner Planets** (copyrighted; paraphrase only):

- 1993 Samuel Weiser, ISBN 0-87728-741-4. Publisher preview opened: Part One Mercury (young-Hermes spontaneity). Psychological `school_specific` only. Unread planet sections not backfilled.

**Greene / Sasportas, The Luminaries** (copyrighted; paraphrase only):

- 1992 Samuel Weiser / CPA, ISBN 978-0-87728-750-6. Publisher preview opened: Part One *Mothers and Matriarchy* (Moon); Part Two *The Hero with a Thousand Faces* (Sun). Psychological `school_specific` only. Intentional Sun/Moon polarity logged; do not average into CORE consciousness vs unconscious.

### Collisions already logged (do not “fix”)

1. Moon/Venus temperature: Ptolemy moisture + moderate heat vs Lilly cold+moist.
2. Mercury: Ptolemy alternates dry/moist vs Lilly native cold/dry melancholy; convertibility compared only as *takes colour from what it joins*.
3. Sun benefic: Ptolemy common vs Lilly fortune-if-dignified.
4. Element: Lilly fire/earth/air/water vs Ptolemy I.21 winds/rulers on the same triangles.
5. Mode: schema `cardinal\|fixed\|mutable` loses Ptolemy tropical vs equinoctial; Lilly glues four as moveable/cardinal (Lilly I.16 nature also calls Aries/Libra equinoctial).
6. Houses: Lilly “Ptolomeian Doctrine” ≠ opened Ptolemy topical houses.
7. `requires_action`: boolean; `false` = not established by opened locus.
8. Aspect quality: Ptolemy harmonious/discordant-by-sex ≠ Lilly good/enmity/concord. Do not copy Lilly labels into `interaction`.
9. Commanding: **grouping** Aries–Virgo vs Libra–Pisces compared. Ptolemy **pair-relation** (equal distance from equinox) stays school_specific.
10. Ptolemy I.18 beholding ≠ Lilly Antiscion + Contrantiscion.
11. Lilly Northern list in the same chapter says six signs but names five (Leo omitted in this scan). Commanding list on p.91 is the compared grouping.
12. Lilly long/short ascension is rising-time technique; opened list puts Aquarius in both — not normalized as Layer 2 meaning.
13. Layer 2 required psych slots (`motivation` / `strengths` / `excess` / `deficiency` / `behavioral_tendencies`) unattested classically — **do not materialize 12 sign objects**.
14. Valens I.1 is a topical/significator catalog, not Ptolemy/Lilly elemental qualities. Do not average into `function`.
15. Saturn dryness: Ptolemy/Lilly secondary dry vs Valens injuries from cold **and moisture**.
16. Valens malefics-in-sect can bestow good — not added to the compared “traditionally malefic” lemma.
17. Mercury convertibility now has Valens as a third compared row; native cold/dry vs alternate dry/moist still unresolved.
18. Moon/Venus temperature still unresolved: Valens I.1 does not attest heat or cold.
19. Aries element: Lilly fire vs Ptolemy winds vs Valens fiery *and* watery weather. Do not compare fire.
20. Houses: Valens IX vs Lilly I.7 — compared on thin topics (life, brothers, marriage…). Enemies: Lilly VII public + XII private vs Valens XII. Servants: Lilly VI vs Valens XII slaves. Derived-place rotation has no schema slot.
21. Lilly I.19: conjunction “very improperly” an aspect; orbs are planetary moieties, two tables from memory — not an IL aspect field.
22. Houlding: orbs belong to planets; modern aspect-orbs are a 20th-century simplification. Compared with Lilly I.19 as planetary-not-aspectual. Numbers not copied onto objects.
23. Houlding: square is not simply damaging (planet/dignity/reception). Lilly I.19 keeps imperfect enmity. Not averaged into `interaction`. Planet-dependent quality is IL-2.
24. Houlding 1st house adds personality/mind. Lilly I.7 is life/stature/complexion. Domain not rewritten. Provenance is product, not academic: layers coexist; do not silently ship a modern identity/personality object.
25. Servants/employees: Lilly I.7 + Houlding 6th compared. Valens IX still puts slaves in XII.
26. Known enemies: Houlding moves secret→7th once known. Lilly VII-public vs XII-private vs Valens XII-enemies remain distinct. These are different *category systems* for life, not a disagreement about one lemma — do not consensus-score them into one house.
27. Houlding 12th “unconscious / premature development” is later overlay on a traditional page — not Layer 3 meaning.
28. Greene Introduction: Saturn as a psychic process that can use pain/restriction toward self-discovery, greater consciousness, and eventual freedom. This is a different category from Ptolemy/Lilly cold/dry/malefic. Do not rewrite `function`. Do not import structure / limits / maturation / reality from this page or from jacket copy.
29. Houlding *Great Teacher*: personal boundary and mature-through-constraint are living-traditional `school_specific`. They do **not** make Ptolemy confirm structure-setting / individual identity. Do not average into `function`.
30. Houlding's astronomy-to-signification causal story is her explanatory model, not a TodayFlow fact. Slow tempo is compared as a quality only.
31. External Saturn research pilots may invent T1–T4, `schools_confirming`, or premature `canonical_fields`. Those are **not** IL evidence tiers. Keep `core|supported|school_specific|editorial`. T2 secondary excerpts stay out of object slots until a primary locus is opened.
32. Watters 2003 is modern general practical, not Lilly/Houlding traditional. `primary_read` ≠ stronger canonical evidence. Schema has no `modern_general_practical` source_class; parked in `professional`. Do not use Watters to manufacture classical → traditional → psychological consensus.
33. Sun function registers are different categories: Ptolemy/Lilly heat; Watters essential-self / becoming; Greene solar-consciousness / eternal. Do not average to “Sun = consciousness” or one core-self lemma.
34. Moon function registers are different categories: Ptolemy/Lilly moisture; Watters night-world / emotion / habit; Greene embodiment / involuntary / numinous. Same-book Sun/Moon polarity is intentional. Do not average to “Moon = unconscious” as CORE.
35. Watters body/medical and planet-in-sign fertility rows (heart/spine, gynecological flag, diabetes, infections, liver-from-excess, etc.) are source evidence in the ledger only. Not `object.domains`. Not runtime meaning. IL-2/IL-3 must not treat them as product copy.
36. Hand *Horoscope Symbols* Ch.4 / Ch.7 still closed (previews stop inside Ch.3). Greene *Relating* Venus/7th section still closed. Arroyo *Four Elements* planet-section text still closed. Mars/Jupiter psychological still empty. No placeholder meaning.
37. Mercury psychological is no longer empty: Greene *Inner Planets* young-Hermes spontaneity is `school_specific`. Do not average with Watters mind/curiosity or Ptolemy convertibility.

CORE cannot be scored yet. Do not teach “Saturn = structure” or “Sun = consciousness / Moon = unconscious” as CORE.

---

## 3. What to do next

**Do not run another blind planet literature pass.** Ingest of the opened Sun–Jupiter rows is closed. Next research is **one named gap** only, if the owner asks or a specific page actually opens:

1. Venus / Mars / Jupiter **psychological function** (Greene *Relating* Venus/7th if that chapter opens; otherwise Arroyo planet sections if preview text appears). Mercury psychological is no longer empty (Inner Planets Hermes). Corpus notes remaining closures.
2. Robert Hand *Horoscope Symbols* Ch.4 “The Planets: Core Meanings” (Sun→Saturn) **if** pages past Ch.3 are readable. Same book Ch.7 Aspects — same closed boundary; do not burn a second call to confirm it.

If those pages stay closed: ask the owner for **edition + pages X–Y**, not “find more astrology.”

Do not pad Greene watery houses. Do not copy Houlding Mundane Signification as a catalog. Do not ingest T2 secondary excerpts as object fields. Do not treat Watters as traditional. Do not rescore CORE because more rows exist.

Do **not**:

- pad classical/traditional loci to raise the object counter
- polish Saturn/houses/aspects to a modern average
- create Layer 2 sign objects from QUALITY lines
- create Layer 5 combo objects yet (candidates list exists; wait until atoms are denser **or** owner asks — still candidates, not proven exceptions)
- set any object `active`
- wire runtime / Today prompts
- expand schema for `unknown` / `not_evidenced`
- open a parallel “canonical v2”
- backfill Greene/Hand from model memory
- invent a second evidence scale (T1–T4) or `schools_confirming` on object slots
- let secondary (T2) excerpts strengthen `function` / `themes` / `shadow`

### Ingest recipe

```text
opened locus
  → claims/<id>.json  (paraphrase + locus + evidence_tier + gap_notes)
  → objects_v1.json   only if required object slots are attested
  → tests in backend/tests/test_astrology_interpretation_schema_v1.py
  → IL changelog patch (1.3.x, “no methodology change”)
```

Validate: host often has no pytest. Use `python3` + `jsonschema` and `exec` the test file with `__file__` set.

Author for commits (do not `git config`): `TodayFlow Agent <agent@todayflow.app>` via env.

### Tests to keep true

- nothing `active`
- no `type==sign` objects
- no surface keys
- no `evidence_tier: core` yet
- aspects: geometry compared; `requires_action is False` cannot be `active`
- houses: Lilly `domain` text remains; Valens compared on thin lemmas; Houlding 1/6/7/12 is traditional class without rewriting domain
- Aries fiery remains `school_specific`, not compared to Ptolemy fire **or** Valens fire (Valens also watery)
- Lilly I.19 / Houlding orbs not copied onto aspect objects; square-not-simply-bad stays school_specific
- Saturn `function` remains cooling/cold; Greene psychic-process stays `school_specific`; Houlding personal-boundary / mature-through-constraint stay `school_specific`; no `structure` in object themes
- Watters `source_class=professional` (not traditional); Greene Luminaries Sun/Moon `school_specific`; medical/body rows not in `object.domains`; no `evidence_tier: core`; functions unchanged

---

## 4. Parallel trains (not this job)

Leave these alone unless the owner’s query is explicitly about them:

- Profile v2 viewport / recognition scene
- Foundation UI visual language v0.5/v0.6
- Trust Layer landing `#trust` / ads copy
- Today scroll / day-number tap (original reason for branch `cursor/today-scroll-and-number-tap`)

Product authority: canon `docs/` → tracker → **server**. Git is a ledger. `main` is the only product base.

---

## 5. Paste into the next chat

```text
Continue Interpretation Library IL-1 ingest.

Handoff: docs/astrology/IL1_HANDOFF.md
Canon: docs/astrology/INTERPRETATION_LIBRARY_V1.md

LOCKED: sequence IL-0✅ → IL-1 now → IL-2 rules → IL-3 engine → IL-4 expression.
Do not polish the IL document. Do not reopen methodology/ontology/schema.
Do not materialize 12 sign objects. Do not set status=active.
Do not mix Profile/Trust/landing/motion into IL commits.

Transfer SHA: ecb4cbe4. Catalog 24 draft / 0 active / 0 signs / CORE unscored is correct.
Do not add conceptually. Do not pad classical/traditional ingest.
Watters 2003 is professional/modern practical, not traditional. Do not CORE-score it.
Do not start a blind planet research pass. Remaining NEED_OWNER:
  Hand Horoscope Symbols Ch.4/Ch.7 (preview stops in Ch.3);
  Greene Relating Venus/7th; Arroyo Four Elements planet sections;
  Mars/Jupiter psychological still empty.
Mercury psychological = Inner Planets Hermes spontaneity only; do not backfill unread chapters.
Research-first: Google Books → publisher preview → Open Library/CDL → libraries.
Ask the owner only for a specific closed locus (edition + pages).
Do not ingest Greene watery houses or Houlding Mundane Signification as a catalog.
Do not import T1-T4 / schools_confirming / T2 excerpts into object slots.
Do not rewrite planet function slots. Do not copy Watters medical rows into object.domains.
Do not redesign TodayFlow.
```
