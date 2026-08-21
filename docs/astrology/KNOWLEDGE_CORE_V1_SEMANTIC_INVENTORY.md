# Knowledge Core V1 — Semantic Inventory

**Date:** 2026-08-21  
**Status:** **APPROVED** — V1 freeze map (owner 2026-08-21). Literature discovery is a tool against a named `KC-*` row, not a process.  
**Canon:** [INTERPRETATION_LIBRARY_V1.md](./INTERPRETATION_LIBRARY_V1.md) §6.25–§6.35. Parent order: [KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md](../KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md). Today Meaning SoT: [TODAY_CONTENT_PIPELINE_V1.md](../today/TODAY_CONTENT_PIPELINE_V1.md). Identity/mechanics: [foundation_v1.md](../foundation_v1.md). Compose: [ASTROLOGY_COMPOSITION_MODEL.md](../ASTROLOGY_COMPOSITION_MODEL.md). Outer representation: [IL1_OUTER_PLANET_DRAFT_REPRESENTATION.md](./IL1_OUTER_PLANET_DRAFT_REPRESENTATION.md). Product-meaning gate: [TODAYFLOW_CANON_V1.md](./TODAYFLOW_CANON_V1.md). Split: [KNOWLEDGE_CORE_V1_PRODUCT_CANON_AND_LENSES.md](./KNOWLEDGE_CORE_V1_PRODUCT_CANON_AND_LENSES.md). Planet map: [MAINSTREAM_PLANET_SEMANTIC_MAP_V1.md](./MAINSTREAM_PLANET_SEMANTIC_MAP_V1.md). Grammar: [PLANET_CANON_GRAMMAR_V1.md](./PLANET_CANON_GRAMMAR_V1.md). Planet Canon: [PLANET_CANON_V1.md](./PLANET_CANON_V1.md). Storage: [PLANET_CANON_STORAGE_V1.md](./PLANET_CANON_STORAGE_V1.md). Fill: [PLANET_CANON_SUN_SATURN_FILL_V1.md](./PLANET_CANON_SUN_SATURN_FILL_V1.md). Recognition check: [COSTAR_SEMANTIC_CONTENT_ENGINE_TEARDOWN_V1.md](../audits/COSTAR_SEMANTIC_CONTENT_ENGINE_TEARDOWN_V1.md).

This file is the **V1 limiter**. IL V1 is not “complete astrology.” It is the minimum set of controlled semantic primitives sufficient for Today / Profile / Compatibility without the LLM inventing meanings. That is the IL-1 done criterion — not book count, claim count, school count, or CORE lemmas.

---

## Architecture impact

- **SoT before:** parent order existed, but the next named IL pass was still a layer slice. Gap → author → closed book could run without a V1-wide constituent map.
- **SoT after:** this inventory is the **owner-approved V1 freeze map**. New **books** remain forbidden unless a named `KC-*` row has a V1-required constituent that is actually missing. **1.3.76:** product meaning comes from Mainstream convention. **1.3.77:** planet map locked. **1.3.78:** Planet Canon grammar locked. **1.3.79:** Planet Canon V1 locked. **1.3.80:** `canon` storage locked. **1.3.81:** Sun–Saturn `canon` filled. Next execution = **1.3.82 composition smoke-test**, then Signs. Co–Star is a recognition check. Do not rewrite `function` this inventory.
- **Public contract changed?** no (inventory). Outer schema delta is 1.3.72.
- **Migration required?** no
- **Canon updated?** yes — this file · IL §6.25 / §6.26 · parent · handoff · tracker
- **Backward compatible?** yes — catalog 36 draft / 0 `active` until a later materialize pass

---

## Freeze (literature)

**Stopped:** new books · Uranus/ASC/Mars/Layer 5 monographs · Cell C / Pulse Part Two / Hand Ch.10 as the next task · coverage hunts · scoring CORE as a product gate.

**Book test:** a **book** opens only if Mainstream panel + Canon structuring cannot supply a V1 runtime constituent (row X → consumer Y → missing Z). No chain → do not open the book. Modern reference pages (Astrodienst, Cafe Astrology, one more of that class) are the Mainstream panel, not “new books.”

**Allowed without a book:** named Architecture impact (schema/model); opportunistic extract of an already-named NEED_OWNER planet locus if that page becomes legally readable (1.3.59).

**Coverage symmetry between layers is not a goal.** Houses/aspects stay `DRAFT_CLASSICAL` until IL-2 hits a specific semantic hole.

---

## 1. What IL V1 must know (layers)

Product question first. A layer is a job, not a bookshelf.

| Layer | Job | Holds | Must not hold |
|-------|-----|-------|----------------|
| **Foundation** | astronomical/astrological **identities and mechanics** | names, rulers, dates, orbs, house system, geometry, Swiss emit | meaning of Saturn, character of Aries |
| **Planets** | what **function/process** the body is | **Canon grammar (1.3.78):** `core_function` · `drive` · `needs` · `constructive` · `distorted` · `domains`. Schema storage still `function` · `themes` · `positive_expression` · `shadow` · `domains` · `tempo` until a later named pass. `tempo` in schema ≠ Canon | planet-in-sign recipes, `today_message` |
| **Signs** | **how** a function is expressed | classification: `mode` · `element` · `orientation`. Later-interpretive: `motivation` · `expression` · `strengths` · `excess` · `deficiency` · `behavioral_tendencies` | ruler/dates (Foundation), planet×sign (Layer 5) |
| **Houses** | **where** in experience | `domain` · `internal_meaning` · `external_manifestations` · `people` · `activities` · `resources` · `risks` | ASC as a house; turned-house technique |
| **Aspects** | **how two functions interact** | `angle` · `interaction` · `requires_action` | pair cookbooks (Mars□Saturn is Layer 5 / IL-2) |
| **Angles** | role of **ASC / MC** | Layer 1 objects, constituents **not yet defined** | House 1 / House 10 substitution |
| **Compositions** | planet×sign · planet×house · planet×aspect×planet | IL-2 **rules** by default; IL-1 gold list = **candidates** only where atoms may lie | 10 000 JSON horoscopes |
| **Time** | natal vs transit (vs later techniques) | `temporal_class` clustering; Layer 5 types `natal_aspect` · `transit_to_natal` · `transit_through_house` | progressions / returns as IL V1 objects (see OUT_OF_V1) |

Atoms (IL-1 gold, IL §8): 12 Layer-1 objects (Sun–Pluto + ASC + MC) · 12 signs · 12 houses · 5 major aspects = **41**. Then ~50–60 Layer 5 candidates. Dignity/rulership stays Foundation §2.5.

Nodes · Chiron · Lilith: identity in Foundation §2.2; **not** IL-1 gold. Minors (quincunx): Foundation §2.4 OOS v1.

---

## 2. Status vocabulary (locked)

| Status | Meaning |
|--------|---------|
| `FOUNDATION` | Live outside IL. Do not research as an IL meaning slot. |
| `DRAFT_STRUCTURAL` | IL `draft` object exists; structural constituents filled; later-interpretive may be omitted on purpose. |
| `DRAFT_CLASSICAL` | IL `draft` from one school; not a landscape; not CORE. |
| `RESEARCH_STABLE` | Coverage hunt closed. Named-locus extract only. |
| `CLAIMS_WITHHELD` | Claims exist; object not materialized (schema would fake consensus). |
| `ACCESS_BLOCKED` | ≥3 dedicated loci, 0 readable bodies. Discovery stopped. Not a book hunt. |
| `DEFERRED_V1` | In the V1 *model*; not this execution slice. No literature until the row is reopened by owner. |
| `UNTYPED` | Product uses the **fact**; IL has no object type. Decide: Foundation / new type / OUT_OF_V1. |
| `CANDIDATE` | Layer 5 gold list. No objects. Compose-default until IL-2. |
| `OUT_OF_V1` | Explicitly excluded from Interpretation Library V1. |
| `NEED_MODEL` | Constituents not defined. Literature forbidden until parent steps 1–4. |

Nothing is `active`. Runtime today still invents meaning in prompts. «Runtime consumer» below is the **intended** authority after IL-3, not a live wire.

---

## 3. Inventory

One table, split by layer so it stays readable. Columns are the same everywhere.

**Evidence requirement (default, unless a row says otherwise):** IL-1 draft may be `school_specific`. CORE is a research characteristic, not a product gate (1.3.73). Product meaning waits on TodayFlow Canon. Do not fill a required slot to satisfy schema.

### 3.1 Foundation — identities and mechanics

| ID | Product need | Semantic layer | Object | Required constituents | Evidence requirement | Current coverage | Runtime consumer | Status |
|----|--------------|----------------|--------|----------------------|----------------------|------------------|------------------|--------|
| KC-F1 | Know which body/sign/house/aspect the calc emitted | Foundation | Swiss/calc identities | name · id · emit | astronomy / machine contract, not school-convergence | Live (Foundation §1, AMC 39) | Day Sources → pipeline step 1 | `FOUNDATION` |
| KC-F2 | Sign identity without IL meaning | Foundation | 12 signs | element · mode · polarity · `ruler` / `ruler_classical` · dates | L1–L3 locks | Foundation §2.1 tables | Profile chart, Today climate | `FOUNDATION` |
| KC-F3 | Planet identity / natural houses | Foundation | 10 bodies + nodes/Chiron/Lilith | speed · `natural_houses` · keywords as identity | L2–L3 locks; outers `calibrated: false` | Foundation §2.2 | scoring tags, not IL lookup | `FOUNDATION` |
| KC-F4 | Aspect geometry / orbs | Foundation | 5 majors | angle · orb policy | machine + Foundation §2.4; quincunx OOS | Live tables | calc layer | `FOUNDATION` |
| KC-F5 | Dignity / rulership formulas | Foundation | dignity tables | L1 ruler · classical chain | Foundation §2.5; not IL | Foundation | traditional chains in code | `FOUNDATION` |

IL must **not** copy these into knowledge objects. Research that only restates rulers/dates/orbs does not close any IL row.

### 3.2 Planets — function / process

Structural vs later-interpretive on **outers** is not the same job as on Sun–Saturn ([IL1_LAYER1_OUTERS_DEFINITION.md](./IL1_LAYER1_OUTERS_DEFINITION.md)).

| ID | Product need | Semantic layer | Object | Required constituents | Evidence requirement | Current coverage | Runtime consumer | Status |
|----|--------------|----------------|--------|----------------------|----------------------|------------------|------------------|--------|
| KC-P-SUN | What the Sun *does* as a process | Planets | `astro.object.sun` | Layer 1 schema slots | school_specific OK; CORE blocked; `function` stays classical elemental | Draft; psych COVERED; humanistic filled | Today drivers · Profile · Compat | `RESEARCH_STABLE` |
| KC-P-MOON | What the Moon *does* | Planets | `astro.object.moon` | same | same | Draft; psych **THIN** (Luminaries preview); Costello NEED_OWNER densify | Today fast climate (sign/phase/aspects) · Profile | `RESEARCH_STABLE` |
| KC-P-MER | What Mercury *does* | Planets | `astro.object.mercury` | same | same | Draft; psych **THIN** (Hermes crumb) | Today personal pace · Profile communication | `RESEARCH_STABLE` |
| KC-P-VEN | What Venus *does* | Planets | `astro.object.venus` | same | same | Draft; psych COVERED (Sullivan excerpt); p.69 NEED_OWNER densify | Today · Profile values/relating · Compat | `RESEARCH_STABLE` |
| KC-P-MAR | What Mars *does* | Planets | `astro.object.mars` | same | psych slot ACCESS_BLOCKED; no fourth book | Draft; psych **0 claims**; 3 unread loci | Today action/risk windows · Profile | `RESEARCH_STABLE` + `ACCESS_BLOCKED`(psych) |
| KC-P-JUP | What Jupiter *does* | Planets | `astro.object.jupiter` | same | psych paused (already dense) | Draft; psych COVERED | Today · Profile growth | `RESEARCH_STABLE` |
| KC-P-SAT | What Saturn *does* | Planets | `astro.object.saturn` | same | CORE candidates listed only, not scored | Draft; psych COVERED; `themes` still elemental | Today slow drivers · Overlay · Compat | `RESEARCH_STABLE` |
| KC-P-URA | What Uranus *does* | Planets | `astro.object.uranus` | identity+clustering vs later-interpretive (`function`/`domains` = school packages) | do not fill schema from Hand; `domains` natal set unattested | Claims 3 schools; object withheld; **schema optional-on-draft 1.3.72** | Today only if strong/eventful (pipeline §3) | `CLAIMS_WITHHELD` · schema ready |
| KC-P-NEP | What Neptune *does* | Planets | `astro.object.neptune` | same as Uranus | same | same | same | `CLAIMS_WITHHELD` · schema ready |
| KC-P-PLU | What Pluto *does* | Planets | `astro.object.pluto` | same; `domains` **0** attested natal keys | same | same | same | `CLAIMS_WITHHELD` · schema ready |

Planet fill is **not** a literature project. Outer representation is locked (1.3.72). **Do not fill outer `function` by CORE or by Hand.** Next named after Canon (1.3.73) = Sun–Pluto claim audit on the existing ledger.

### 3.3 Signs — how a function is expressed

| ID | Product need | Semantic layer | Object | Required constituents | Evidence requirement | Current coverage | Runtime consumer | Status |
|----|--------------|----------------|--------|----------------------|----------------------|------------------|------------------|--------|
| KC-S-CLASS | Classify the twelve spans | Signs | `astro.sign.aries`…`pisces` | `mode` · `element` · `orientation` | Lilly grid as school_specific draft; collisions stay claims | 12 drafts (1.3.68); close-out 1.3.69 | Today Moon-in-sign climate · natal placements | `DRAFT_STRUCTURAL` |
| KC-S-LINT | Character / motivation of a sign | Signs | same objects, later-interpretive keys | `motivation` · `expression` · `strengths` · `excess` · `deficiency` · `behavioral_tendencies` | independent psych structure textbook; Pulse/QUALITY forbidden | omitted; Cell C `ACCESS_BLOCKED` | Profile portraits, if ever | `DEFERRED_V1` + `ACCESS_BLOCKED`(Cell C) |

Do not reopen sign literature to look complete. Cell C is a future evidence dependency, not a V1 blocker.

### 3.4 Houses — area of experience

| ID | Product need | Semantic layer | Object | Required constituents | Evidence requirement | Current coverage | Runtime consumer | Status |
|----|--------------|----------------|--------|----------------------|----------------------|------------------|------------------|--------|
| KC-H-12 | Where a process lands | Houses | `astro.house.01`…`12` | `domain` · `internal_meaning` · `people` · `activities` · `resources` · `risks` · `external_manifestations` | IL-1 fill = Lilly CA I.7 school_specific; not averaged with Valens/Houlding | 12 drafts, **classical only**; no Layer-2-style landscape | Natal Overlay · Profile house lines · Decode | `DRAFT_CLASSICAL` |
| KC-H-ASC≠1 | Do not treat House 1 as ASC | Houses / Angles | — | distinction in model | already gated in IL Layer 1 vs 3 | documented, not a research task | all natal surfaces | `FOUNDATION` / model lock |

Houses have drafts. They do **not** automatically need a new book. Coverage symmetry with Planets/Signs is **not** a goal. Reopening houses means IL-2 hit a specific semantic hole, then parent steps 1–4 — not Houlding *Houses* as the next ingest.

### 3.5 Aspects — interaction of two functions

| ID | Product need | Semantic layer | Object | Required constituents | Evidence requirement | Current coverage | Runtime consumer | Status |
|----|--------------|----------------|--------|----------------------|----------------------|------------------|------------------|--------|
| KC-A-5 | How two functions interact | Aspects | conjunction · opposition · square · trine · sextile | `angle` · `interaction` · `requires_action` | geometry compared; qualitative systems (Ptolemy harmonious/discordant vs Lilly enmity) stay claims, not object defaults | 5 drafts; `interaction` is schema enum (sextile currently `flow`, not «opportunity requiring participation») | Today major aspects · Overlay · Compat | `DRAFT_CLASSICAL` |
| KC-A-REQ | Do not `active` an unevidenced boolean | Aspects | `requires_action` | unambiguous representation **or** runtime contract | activation gate 1.3.8 | `false` on draft ≠ «does not require action» | IL-3 when wired | `DEFERRED_V1` (gate, not a book) |
| KC-A-MIN | Minor aspects | Aspects | quincunx etc. | — | Foundation §2.4 | OOS v1 | — | `OUT_OF_V1` |

Pair meaning (Saturn□Venus) is **not** Layer 4. It is composition (KC-C-\*).

### 3.6 Angles — ASC / MC

| ID | Product need | Semantic layer | Object | Required constituents | Evidence requirement | Current coverage | Runtime consumer | Status |
|----|--------------|----------------|--------|----------------------|----------------------|------------------|------------------|--------|
| KC-ANG-ASC | What ASC *is* as a role | Angles | `astro.object.asc` (gold set) | **undefined** — parent steps 1–4 never run | calc already emits; locus + model before ingest | 0 objects, 0 dedicated claims | Profile chart · Overlay angularity · Compat axes | `NEED_MODEL` |
| KC-ANG-MC | What MC *is* as a role | Angles | `astro.object.mc` | **undefined** | same | 0 objects, 0 dedicated claims | Profile vocation axis · Overlay | `NEED_MODEL` |

No ASC/MC book until constituents are defined. House 1 / House 10 drafts are not a substitute.

### 3.7 Compositions

Default: IL-2 Composition Engine from atoms ([ACM](../ASTROLOGY_COMPOSITION_MODEL.md)). IL-1 gold list = **candidates**, not objects (IL §8).

| ID | Product need | Semantic layer | Object | Required constituents | Evidence requirement | Current coverage | Runtime consumer | Status |
|----|--------------|----------------|--------|----------------------|----------------------|------------------|------------------|--------|
| KC-C-P×S | How a function expresses in a sign | Compositions | `planet_in_sign` | IL-2 rules; curated only if `non_compositional` | IL-2 after atoms; IL-1 list is suspicion, not proof | 10 gold candidates, **0 objects** | natal placements · Moon-in-sign Today | `CANDIDATE` |
| KC-C-P×H | How a function lands in a house | Compositions | `planet_in_house` | same | same | 11 gold candidates, 0 objects | Overlay · Profile houses | `CANDIDATE` |
| KC-C-NASP | How two natal functions interact | Compositions | `natal_aspect` | same | same | 14 gold candidates, 0 objects | Profile tension · Compat | `CANDIDATE` |
| KC-C-TRN | How sky now meets natal | Compositions | `transit_to_natal` | same | same | 15 gold candidates, 0 objects | Natal Overlay (pipeline §5) · Personal Day | `CANDIDATE` |
| KC-C-TH | How a transiting body occupies a natal house | Compositions | `transit_through_house` | same | same | 5 gold candidates, 0 objects | Overlay slow background | `CANDIDATE` |
| KC-C-RULES | Compose without a catalog | Compositions | IL-2 rules | weights, conflict, merge | after IL-1 atoms; may demote candidates | not started | IL-3 | `DEFERRED_V1` (sequence lock) |

Gold lists stay in IL §8. Do not ingest Layer 5 to look busy. Do not start IL-2 rules before this inventory is approved **and** Layer 1–4 atoms are the declared SoT for compose inputs.

### 3.8 Time — natal vs transit vs later

| ID | Product need | Semantic layer | Object | Required constituents | Evidence requirement | Current coverage | Runtime consumer | Status |
|----|--------------|----------------|--------|----------------------|----------------------|------------------|------------------|--------|
| KC-T-CLASS | Cluster by pace | Time | root `temporal_class` | `fast` · `medium` · `slow` · `natal` | schema clustering, not a technique treatise | filled on drafts (often schematic) | engine ranking (future) | `DRAFT_STRUCTURAL` |
| KC-T-NATAL | Meaning of a natal placement | Time | natal objects + `natal_aspect` | natal temporal_class; not «today» | surface-neutral IL-1 | atoms draft; natal combos `CANDIDATE` | Profile · Compat · Overlay base | see KC-P / KC-C-NASP |
| KC-T-TRANSIT | Meaning of sky-now vs natal | Time | `transit_to_natal` · transiting planet atoms | transit ≠ natal rewrite of the planet | pipeline I0: Global Day has no natal; Overlay consumes Global | atoms draft; transit combos `CANDIDATE` | Today Global (sky) · Overlay (sky×natal) | see KC-C-TRN |
| KC-T-PHASE | Lunar phase / VOC as **fact** | Time | **no IL type** | Day Sources / Foundation-like factual layer; may rank/UI as calculated fact | not school-convergence | Live facts; no IL phase object | Today fast climate | `FOUNDATION` (fact-only). Separate lunar-meaning inventory only if product later needs «Full Moon means X for the user» |
| KC-T-PROG | Secondary progressions / solar arc / returns | Time | — | — | Day Sources may emit facts; IL V1 gold set has no type | facts partial in DAY_SOURCES; no IL objects | not Today V1 meaning SoT | `OUT_OF_V1` |

---

## 4. Book test (after approval only)

A source stays in the queue only if all of the following are true:

1. **Row ID** exists in §3 (or is added by a named Architecture impact).
2. **Constituent** on that row is required for V1 *and* currently missing (not `DEFERRED_V1`, not `ACCESS_BLOCKED`, not `RESEARCH_STABLE` densify-by-choice).
3. **Runtime consumer** is a V1 surface (Today Global / Overlay / Profile / Compatibility / future IL-3), not a nice-to-have monograph.
4. The source is the **best independent locus for that constituent**, not «the next readable PDF».

Otherwise:

> This book closes nothing necessary for V1 → **remove from queue**.

Examples against the current tree:

| Temptation | Verdict |
|------------|---------|
| Greene *Outer Planets* / Tarnas *Prometheus* / *Astrological Neptune* | Densify already-COVERED psych slots. Representation is schema (1.3.72), not empty ledger. **Out of queue.** |
| Pulse Part Two / Hand Ch.10 / Cell C fourth book | KC-S-LINT is `DEFERRED_V1` + `ACCESS_BLOCKED`. **Out of queue.** |
| Fourth Mars psych book | KC-P-MAR psych is `ACCESS_BLOCKED`. **Out of queue.** |
| Any ASC cookbook | KC-ANG-ASC is `NEED_MODEL`. **Out of queue** until steps 1–4. |
| Layer 5 transit cookbook | KC-C-\* is `CANDIDATE`; IL-2 not started. **Out of queue.** |
| Named NEED_OWNER page (p.138, Costello, Hand Ch.4 Sun) that **opens** | Access extract against an existing row. Not discovery. Allowed under 1.3.59 even during freeze. |

---

## 5. Owner decisions (LOCKED 2026-08-21)

1. **Inventory = V1 freeze map — APPROVED.** New literature discovery is forbidden until a named `KC-*` row has a V1-required constituent that is actually missing. Book test: row X → consumer Y → missing Z. No chain → do not open the book.
2. **OUT_OF_V1 — APPROVED as listed.** Minors · secondary progressions / solar arc / returns as IL objects · Nodes / Chiron / Lilith as IL-1 gold · sign later-interpretive as an execution blocker. Not “never” — not a blocker for the first working semantic engine.
3. **KC-T-PHASE — fact-only in V1.** Phase/VOC stay in Day Sources / Foundation-like factual layer and may participate in UI/ranking as a calculated fact. No Interpretation Library for phases now. If the product later needs «Full Moon means X for the user», open a separate lunar-phase meaning inventory. Until then: no phase literature.
4. **Houses and Aspects stay `DRAFT_CLASSICAL` — APPROVED.** Do not “catch up” school counts to Planets/Signs. Structural atoms are enough for the next stage. New research only if IL-2 hits a specific semantic insufficiency. **Coverage symmetry between layers is not a goal.**
5. **Next named pass after approval = outer schema (done 1.3.72), not ASC/MC and not literature.** **1.3.73** inserts TodayFlow Canon *before* filling meaning keys. Then: Sun–Pluto claim audit → materialize outer drafts under Canon (not CORE) → ASC/MC definition → ASC/MC decision → IL-1 V1 close-out → IL-2 Composition.

ASC/MC are second because they are `NEED_MODEL`: constituents are not defined. Do not start from a book.

---

## 6. Execution order (LOCKED, then redirected 1.3.81)

```text
1. Outer Planet Draft Representation V1        ✅ 1.3.72 schema/model
2. TodayFlow Canon — semantic selection        ✅ 1.3.73–1.3.74
3. Co–Star Semantic & Content Engine teardown  ✅ Phase 0 (1.3.75)  recognition check
4. Product Canon vs Lenses                     ✅ 1.3.76 split
5. Mainstream Planet Semantic Map              ✅ 1.3.77  (territory + families; not Canon)
6. Planet Canon grammar                        ✅ 1.3.78  (slots; dry-run; not fill)
7. Planet Canon V1 fill                        ✅ 1.3.79  (packs + provenance; not schema)
8. Schema pass                                 ✅ 1.3.80  (`canon` nest; not object fill)
9. Write `canon` onto planet drafts            ✅ 1.3.81  Sun–Saturn; `function` untouched
10. Composition smoke-test                     NEXT  1.3.82  four constructions; not IL-2
11. Signs → Houses → Aspects → ASC/MC Mainstream maps
12. IL-1 V1 close-out / IL-2 Composition
```

Historical literature does not appear in this order. Lenses stay in the existing corpus. Co–Star is a check on Mainstream rows, not a source.

---

## Changelog

- **1.10 (2026-08-21)** — Sun–Saturn canon fill (1.3.81). Next = 1.3.82 smoke-test, not Signs.
- **1.9 (2026-08-21)** — Planet Canon storage (1.3.80). Optional `canon` nest. Next = write packs onto drafts. **Done 1.3.81.**
- **1.8 (2026-08-21)** — Planet Canon V1 (1.3.79). Ten packs + provenance. Next = schema pass. **Done 1.3.80.**
- **1.7 (2026-08-21)** — Planet Canon grammar (1.3.78). Six slots. tempo = Foundation. Next = 1.3.79 fill. **Done 1.3.79.**
- **1.6 (2026-08-21)** — Mainstream Planet Semantic Map (1.3.77). Astrology.com = panel #3. Concept families locked. Next = Canon shape, not JSON. **Done 1.3.78.**
- **1.5 (2026-08-21)** — Product Canon vs Lenses (1.3.76). Mainstream map was next. **Done 1.3.77.**
- **1.4 (2026-08-21)** — IL architecture frozen (1.3.75). Co–Star teardown Phase 0. Next was Phase 1 in-app. **Superseded as “next” by 1.5 / 1.3.76.**
- **1.3 (2026-08-21)** — three layers locked (1.3.74): Evidence Corpus / Semantic Consensus / TodayFlow Canon. 491 claims stay. Next = short corpus pass, not Outer/ASC/books. **Superseded as “next” by 1.4 / 1.3.75.**
- **1.2 (2026-08-21)** — TodayFlow Canon (1.3.73) inserted before outer fill. CORE demoted from product gate.
- **1.1 (2026-08-21)** — owner-approved freeze map. Five decisions locked. IL-1 done criterion = minimum controlled primitives, not bibliography. KC-T-PHASE fact-only. Outer representation 1.3.72.
- **1.0 (2026-08-21)** — first V1-wide semantic inventory. IL 1.3.71 freeze. No ingest.

