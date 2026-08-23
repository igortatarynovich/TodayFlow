# Knowledge Core V1 — Semantic Inventory

**Date:** 2026-08-21  
**Status:** **APPROVED** — V1 freeze map (owner 2026-08-21). **1.3.106:** V1 **FROZEN** on stored primitives. Literature discovery is a tool against a named `KC-*` row, not a process.  
**Canon:** [INTERPRETATION_LIBRARY_V1.md](./INTERPRETATION_LIBRARY_V1.md) §6.25–§6.60. Freeze close-out: [KNOWLEDGE_CORE_V1_FREEZE.md](./KNOWLEDGE_CORE_V1_FREEZE.md). Parent order: [KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md](../KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md). Today Meaning SoT: [TODAY_CONTENT_PIPELINE_V1.md](../today/TODAY_CONTENT_PIPELINE_V1.md). Identity/mechanics: [foundation_v1.md](../foundation_v1.md). Compose: [ASTROLOGY_COMPOSITION_MODEL.md](../ASTROLOGY_COMPOSITION_MODEL.md). Outer representation: [IL1_OUTER_PLANET_DRAFT_REPRESENTATION.md](./IL1_OUTER_PLANET_DRAFT_REPRESENTATION.md). Product-meaning gate: [TODAYFLOW_CANON_V1.md](./TODAYFLOW_CANON_V1.md). Split: [KNOWLEDGE_CORE_V1_PRODUCT_CANON_AND_LENSES.md](./KNOWLEDGE_CORE_V1_PRODUCT_CANON_AND_LENSES.md). Planet map: [MAINSTREAM_PLANET_SEMANTIC_MAP_V1.md](./MAINSTREAM_PLANET_SEMANTIC_MAP_V1.md). Sign map: [MAINSTREAM_SIGN_SEMANTIC_MAP_V1.md](./MAINSTREAM_SIGN_SEMANTIC_MAP_V1.md). House map: [MAINSTREAM_HOUSE_SEMANTIC_MAP_V1.md](./MAINSTREAM_HOUSE_SEMANTIC_MAP_V1.md). House grammar: [HOUSE_CANON_GRAMMAR_V1.md](./HOUSE_CANON_GRAMMAR_V1.md). House Canon: [HOUSE_CANON_V1.md](./HOUSE_CANON_V1.md). House storage: [HOUSE_CANON_STORAGE_MATERIALIZATION_V1.md](./HOUSE_CANON_STORAGE_MATERIALIZATION_V1.md). House smoke: [HOUSE_CANON_COMPOSITION_SMOKE_V1.md](./HOUSE_CANON_COMPOSITION_SMOKE_V1.md). Aspect map: [MAINSTREAM_ASPECT_SEMANTIC_MAP_V1.md](./MAINSTREAM_ASPECT_SEMANTIC_MAP_V1.md). Aspect grammar: [ASPECT_CANON_GRAMMAR_V1.md](./ASPECT_CANON_GRAMMAR_V1.md). Aspect Canon: [ASPECT_CANON_V1.md](./ASPECT_CANON_V1.md). Sign grammar: [SIGN_CANON_GRAMMAR_V1.md](./SIGN_CANON_GRAMMAR_V1.md). Sign Canon: [SIGN_CANON_V1.md](./SIGN_CANON_V1.md). Sign storage: [SIGN_CANON_STORAGE_V1.md](./SIGN_CANON_STORAGE_V1.md). Sign materialization: [SIGN_CANON_MATERIALIZATION_V1.md](./SIGN_CANON_MATERIALIZATION_V1.md). Sign smoke: [SIGN_CANON_COMPOSITION_SMOKE_V1.md](./SIGN_CANON_COMPOSITION_SMOKE_V1.md). Grammar: [PLANET_CANON_GRAMMAR_V1.md](./PLANET_CANON_GRAMMAR_V1.md). Planet Canon: [PLANET_CANON_V1.md](./PLANET_CANON_V1.md). Storage: [PLANET_CANON_STORAGE_V1.md](./PLANET_CANON_STORAGE_V1.md). Fill: [PLANET_CANON_SUN_SATURN_FILL_V1.md](./PLANET_CANON_SUN_SATURN_FILL_V1.md). Smoke: [PLANET_CANON_COMPOSITION_SMOKE_V1.md](./PLANET_CANON_COMPOSITION_SMOKE_V1.md). Aspect smoke: [ASPECT_CANON_COMPOSITION_SMOKE_V1.md](./ASPECT_CANON_COMPOSITION_SMOKE_V1.md). Angle Canon: [ANGLE_CANON_V1.md](./ANGLE_CANON_V1.md). Angle grammar: [ANGLE_CANON_GRAMMAR_V1.md](./ANGLE_CANON_GRAMMAR_V1.md). Angle model: [ANGLE_CANON_MODEL_V1.md](./ANGLE_CANON_MODEL_V1.md). Angle map: [MAINSTREAM_ANGLE_SEMANTIC_MAP_V1.md](./MAINSTREAM_ANGLE_SEMANTIC_MAP_V1.md). Angle smoke: [ANGLE_CANON_COMPOSITION_SMOKE_V1.md](./ANGLE_CANON_COMPOSITION_SMOKE_V1.md). Atomic smoke: [ATOMIC_CANON_COMPOSITION_SMOKE_V1.md](./ATOMIC_CANON_COMPOSITION_SMOKE_V1.md). Recognition check: [COSTAR_SEMANTIC_CONTENT_ENGINE_TEARDOWN_V1.md](../audits/COSTAR_SEMANTIC_CONTENT_ENGINE_TEARDOWN_V1.md).

This file is the **V1 limiter**. IL V1 is not “complete astrology.” It is the minimum set of controlled semantic primitives sufficient for Today / Profile / Compatibility without the LLM inventing meanings. That is the IL-1 done criterion — not book count, claim count, school count, or CORE lemmas.

---

## Architecture impact

- **SoT before:** parent order existed, but the next named IL pass was still a layer slice. Gap → author → closed book could run without a V1-wide constituent map.
- **SoT after:** this inventory is the **owner-approved V1 freeze map**. **1.3.106:** V1 is **frozen on stored primitives** — five families are the compose atoms. New **books** remain forbidden unless a named `KC-*` row has a V1-required constituent that is actually missing. **1.3.76:** product meaning comes from Mainstream convention. **1.3.77:** planet map locked. **1.3.78:** Planet Canon grammar locked. **1.3.79:** Planet Canon V1 locked. **1.3.80:** `canon` storage locked. **1.3.81:** Sun–Saturn `canon` filled. **1.3.82:** smoke-test — aspect PASS, sign/house PARTIAL (house PARTIAL is now a snapshot). **1.3.83:** Signs Mainstream map locked. **1.3.84:** Sign Canon grammar locked. **1.3.85:** Sign Canon fill locked. **1.3.86:** Sign Canon storage locked. **1.3.87:** Sign Canon materialization locked. **1.3.88:** Planet × Sign smoke-test PASS. **1.3.89:** Houses Mainstream map locked. **1.3.90:** House Canon grammar locked. **1.3.91:** House Canon fill locked. **1.3.92:** House Canon storage/materialization locked. **1.3.93:** Planet × House smoke PASS. **STOP Houses.** **1.3.94:** Aspects Mainstream map locked. **1.3.95:** Aspect Canon grammar locked. **1.3.96:** Aspect Canon fill locked. **1.3.97:** Aspect Canon storage/materialization locked. 1.3.98 stored Planet × Aspect smoke locked. **1.3.99:** Angle Canon model locked (orientation loci). **1.3.100:** Mainstream Angle map locked. **1.3.101:** Angle Canon grammar locked (`orientation`). **1.3.102:** Angle Canon fill locked. **1.3.103:** Angle Canon storage/materialization locked. **1.3.104:** stored Planet×Angle smoke PASS. **1.3.105:** final atomic smoke PASS. **1.3.106:** Knowledge Core V1 FREEZE. **STOP Angles.** Next execution = IL-2 composition rules (not pair catalog). STOP Signs. Co–Star is a recognition check. Do not rewrite `function` this inventory.
- **Public contract changed?** no (inventory). Outer schema delta is 1.3.72.
- **Migration required?** no
- **Canon updated?** yes — this file · IL §6.25 / §6.26 · parent · handoff · tracker
- **Backward compatible?** yes — catalog 38 draft / 0 `active`

---

## Freeze (literature)

**Stopped:** new books · Uranus/ASC/Mars/Layer 5 monographs · Cell C / Pulse Part Two / Hand Ch.10 as the next task · coverage hunts · scoring CORE as a product gate.

**Book test:** a **book** opens only if Mainstream panel + Canon structuring cannot supply a V1 runtime constituent (row X → consumer Y → missing Z). No chain → do not open the book. Modern reference pages (Astrodienst, Cafe Astrology, one more of that class) are the Mainstream panel, not “new books.”

**Allowed without a book:** named Architecture impact (schema/model); opportunistic extract of an already-named NEED_OWNER planet locus if that page becomes legally readable (1.3.59).

**Coverage symmetry between layers is not a goal.** Houses/aspects stay `DRAFT_CLASSICAL` until IL-2 hits a specific semantic hole.

---

## Freeze (primitives)

**Declared 1.3.106.** Knowledge Core V1 is frozen on stored primitives. Full lock: [KNOWLEDGE_CORE_V1_FREEZE.md](./KNOWLEDGE_CORE_V1_FREEZE.md).

Five stored families = V1 atoms: Planet `core_function` · Sign `manner` · House `arena` · Aspect `relation` · Angle `orientation`. Catalog **38 draft / 0 `active`**. Unchanged this pass.

**Explicitly OUT:** Uranus/Neptune/Pluto = claims, no objects · DSC/IC out of V1 · CORE unscored (not a gate) · Layer 5 = candidates · later-interpretive signs deferred · Co–Star = recognition check, not source.

**STOP Angles.** **STOP Aspects.** **STOP Houses.** **STOP Signs.** Do **not** start CORE scoring. Do **not** start ASC cookbooks. Layer 2 Signs = classification-complete / interpretation-deferred.

**Next named:** IL-2 composition rules — **done 1.3.107.** IL-3 Interpretation Engine — **done 1.3.108.** IL-4 Expression — **done 1.3.109.** Library scale — **done 1.3.110.** Wire calc → IL — **done 1.3.111.** Next = attach IL-4 packs to product surfaces. Not a new “canonical v2.”

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
| **Angles** | which **chart-edge orientation** a function attaches to | compositional type locked 1.3.99 (orientation locus); named slots unspecified | House 1 / House 10 substitution; `arena` / `manner` by analogy |
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
| `CANDIDATE` | Layer 5 gold remaining after IL-2: missing-atom rows only (outers). No objects. |
| `COMPOSED` | IL-2 produces the frame from stored atoms. No catalog object. |
| `LOCKED` | Named pass closed. Do not reopen without a Composition Engine failure. |
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
| KC-H-12 | Where a process lands | Houses | `astro.house.01`…`12` | `domain` · `internal_meaning` · `people` · `activities` · `resources` · `risks` · `external_manifestations` · product `canon.arena` | IL-1 fill = Lilly CA I.7 school_specific; not averaged with Valens/Houlding. Mainstream territory locked 1.3.89; Canon arena stored 1.3.92; PlanetInHouse PASS 1.3.93 | 12 drafts, Lilly classical + `canon.arena`; **STOP Houses** | Natal Overlay · Profile house lines · Decode | `DRAFT_CLASSICAL` + stored Canon |
| KC-H-ASC≠1 | Do not treat House 1 as ASC | Houses / Angles | — | distinction in model | already gated in IL Layer 1 vs 3 | documented, not a research task | all natal surfaces | `FOUNDATION` / model lock |

Houses have drafts **and** stored Canon arena. PlanetInHouse PASS (1.3.93). **STOP Houses.** They do **not** automatically need a new book. Coverage symmetry with Planets/Signs is **not** a goal. Reopening houses means a named Composition Engine failure or IL-2 hit a specific semantic hole — not Houlding *Houses* as the next ingest.

### 3.5 Aspects — interaction of two functions

| ID | Product need | Semantic layer | Object | Required constituents | Evidence requirement | Current coverage | Runtime consumer | Status |
|----|--------------|----------------|--------|----------------------|----------------------|------------------|------------------|--------|
| KC-A-5 | How two functions interact | Aspects | conjunction · opposition · square · trine · sextile | `angle` · `interaction` · `requires_action` · product `canon.relation` | geometry compared; qualitative systems stay claims. Mainstream territory locked 1.3.94; grammar 1.3.95; fill 1.3.96; storage 1.3.97; Planet×Aspect smoke PASS 1.3.98 | 5 drafts; `interaction` enum (trine and sextile both `flow`); live operator is stored `canon.relation`. **STOP Aspects.** | Today major aspects · Overlay · Compat | `DRAFT_CLASSICAL` + stored Canon |
| KC-A-REQ | Do not `active` an unevidenced boolean | Aspects | `requires_action` | unambiguous representation **or** runtime contract | activation gate 1.3.8 | `false` on draft ≠ «does not require action» | IL-3 when wired | `DEFERRED_V1` (gate, not a book) |
| KC-A-MIN | Minor aspects | Aspects | quincunx etc. | — | Foundation §2.4 | OOS v1 | — | `OUT_OF_V1` |

Pair meaning (Saturn□Venus) is **not** Layer 4. It is composition (KC-C-\*).

### 3.6 Angles — ASC / MC

| ID | Product need | Semantic layer | Object | Required constituents | Evidence requirement | Current coverage | Runtime consumer | Status |
|----|--------------|----------------|--------|----------------------|----------------------|------------------|------------------|--------|
| KC-ANG-ASC | What ASC *is* as a role | Angles | `astro.object.asc` (gold set) | orientation-locus type locked 1.3.99; Mainstream territory locked 1.3.100; one Canon slot `orientation` locked 1.3.101; pack locked 1.3.102; stored 1.3.103; Planet×Angle smoke PASS 1.3.104; atomic smoke PASS 1.3.105; V1 freeze 1.3.106 | same panel; House 1 vocabulary not proof; secondary collision-zone not default | 1 draft object, 0 dedicated claims | Profile chart · Overlay angularity · Compat axes | STOP Angles; V1 frozen |
| KC-ANG-MC | What MC *is* as a role | Angles | `astro.object.mc` | same | same; House 10 vocabulary not proof | 1 draft object, 0 dedicated claims | Profile vocation/height axis · Overlay | STOP Angles; V1 frozen |

No ASC/MC book. House 1 / House 10 drafts are not a substitute. Parent 1–4 closed 1.3.99 (orientation loci). Cookbooks stay out of queue.

### 3.7 Compositions

Default: IL-2 Composition Engine from atoms ([ACM](../ASTROLOGY_COMPOSITION_MODEL.md)). IL-1 gold list = **candidates**, not objects (IL §8).

| ID | Product need | Semantic layer | Object | Required constituents | Evidence requirement | Current coverage | Runtime consumer | Status |
|----|--------------|----------------|--------|----------------------|----------------------|------------------|------------------|--------|
| KC-C-P×S | How a function expresses in a sign | Compositions | `planet_in_sign` | IL-2 rules; curated only if `non_compositional` | IL-2 1.3.107; IL-1 list was suspicion | 10 gold, **0 objects**, all composed | natal placements · Moon-in-sign Today | `COMPOSED` |
| KC-C-P×H | How a function lands in a house | Compositions | `planet_in_house` | same | same | 11 gold, 0 objects, all composed | Overlay · Profile houses | `COMPOSED` |
| KC-C-NASP | How two natal functions interact | Compositions | `natal_aspect` | same | same | Sun–Saturn composed; Pluto/Neptune/Uranus pairs remain candidates (missing atom); 0 objects | Profile tension · Compat | `COMPOSED` + `CANDIDATE` remainder |
| KC-C-TRN | How sky now meets natal | Compositions | `transit_to_natal` | same | same | Sun–Saturn transits composed; outer transits remain candidates; 0 objects | Natal Overlay (pipeline §5) · Personal Day | `COMPOSED` + `CANDIDATE` remainder |
| KC-C-TH | How a transiting body occupies a natal house | Compositions | `transit_through_house` | same | same | Saturn/Jupiter composed; Uranus/Pluto remain candidates; 0 objects | Overlay slow background | `COMPOSED` + `CANDIDATE` remainder |
| KC-C-RULES | Compose without a catalog | Compositions | IL-2 rules | weights, conflict, merge | after IL-1 atoms (declared 1.3.106) | **locked 1.3.107** — [IL2_COMPOSITION_RULES_V1.md](./IL2_COMPOSITION_RULES_V1.md) | IL-3 | `LOCKED` |
| KC-C-ENGINE | Rank sky themes without a person | Compositions | IL-3 engine | IL-2 frames; transit band before natal; no user fields | after IL-2 rules (1.3.107) | **locked 1.3.108** — [IL3_INTERPRETATION_ENGINE_V1.md](./IL3_INTERPRETATION_ENGINE_V1.md) | IL-4 | `LOCKED` |
| KC-C-EXPR | Voice already chosen themes | Expression | IL-4 packs | IL-3 themes; surface tone/length/focus; lemmas verbatim; no user fields | after IL-3 engine (1.3.108) | **locked 1.3.109** — [IL4_EXPRESSION_V1.md](./IL4_EXPRESSION_V1.md) | named wire | `LOCKED` |
| KC-C-SCALE | Which constructions locked engines cover | Scale | 6 types × stored atoms; not a catalog | cartesian counts; gold composed vs candidate; wire named not live | after IL-4 expression (1.3.109) | **locked 1.3.110** — [LIBRARY_SCALE_V1.md](./LIBRARY_SCALE_V1.md) | wire calc → IL — done 1.3.111 | `LOCKED` |
| KC-C-WIRE | Calc snapshot → IL-4 pack | Wire | duck-typed chart → SkyFact → IL-2/3/4 | library layer live; product surfaces not attached | after library scale (1.3.110) | **locked 1.3.111** — [CALC_IL_WIRE_V1.md](./CALC_IL_WIRE_V1.md) | attach IL-4 to product surfaces | `LOCKED` |

Gold lists stay in IL §8. Do not ingest Layer 5. Atoms remain compose inputs. **Next named = attach IL-4 packs to product surfaces.**

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
| Any ASC cookbook | KC-ANG-ASC type is locked. **Out of queue** — Mainstream panel is not a cookbook; grammar/fill not started. |
| Layer 5 transit cookbook | KC-C-* remainder is `CANDIDATE` (missing outer atoms). Compose-default locked 1.3.107. **Out of queue.** |
| Named NEED_OWNER page (p.138, Costello, Hand Ch.4 Sun) that **opens** | Access extract against an existing row. Not discovery. Allowed under 1.3.59 even during freeze. |

---

## 5. Owner decisions (LOCKED 2026-08-21)

1. **Inventory = V1 freeze map — APPROVED.** New literature discovery is forbidden until a named `KC-*` row has a V1-required constituent that is actually missing. Book test: row X → consumer Y → missing Z. No chain → do not open the book.
2. **OUT_OF_V1 — APPROVED as listed.** Minors · secondary progressions / solar arc / returns as IL objects · Nodes / Chiron / Lilith as IL-1 gold · sign later-interpretive as an execution blocker. Not “never” — not a blocker for the first working semantic engine.
3. **KC-T-PHASE — fact-only in V1.** Phase/VOC stay in Day Sources / Foundation-like factual layer and may participate in UI/ranking as a calculated fact. No Interpretation Library for phases now. If the product later needs «Full Moon means X for the user», open a separate lunar-phase meaning inventory. Until then: no phase literature.
4. **Houses and Aspects stay `DRAFT_CLASSICAL` — APPROVED.** Do not “catch up” school counts to Planets/Signs. Structural atoms are enough for the next stage. New research only if IL-2 hits a specific semantic insufficiency. **Coverage symmetry between layers is not a goal.**
5. **Next named pass after approval = outer schema (done 1.3.72), not ASC/MC and not literature.** **1.3.73** inserts TodayFlow Canon *before* filling meaning keys. Then: Sun–Pluto claim audit → materialize outer drafts under Canon (not CORE) → ASC/MC definition → ASC/MC decision → IL-1 V1 close-out → IL-2 Composition.

ASC/MC parent 1–4 closed 1.3.99: they are orientation loci. Mainstream Angle map locked 1.3.100. Angle Canon grammar locked 1.3.101 (`orientation`). Angle Canon fill locked 1.3.102. Angle Canon storage/materialization locked 1.3.103. Stored Planet×Angle smoke PASS 1.3.104. Final atomic smoke PASS 1.3.105. Knowledge Core V1 FREEZE **done 1.3.106.** IL-2 composition rules **done 1.3.107.** IL-3 Interpretation Engine **done 1.3.108.** IL-4 Expression **done 1.3.109.** Library scale **done 1.3.110.** Wire calc → IL **done 1.3.111.** **STOP Angles.** Do not start from a book. Next named = attach IL-4 packs to product surfaces.

---

## 6. Execution order (LOCKED, then redirected 1.3.106)

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
10. Composition smoke-test                     ✅ 1.3.82  aspect PASS; sign/house PARTIAL
11. Signs Mainstream map                       ✅ 1.3.83  territory + families; not manner
12. Sign Canon grammar                         ✅ 1.3.84  manner · excess; not fill
13. Sign Canon fill                            ✅ 1.3.85  12 packs + origin; not schema
14. Sign Canon storage                         ✅ 1.3.86  sign_canon_pack; not object fill
15. Sign Canon materialization                 ✅ 1.3.87  12 drafts; later-interpretive omitted
16. Planet × Sign composition smoke            ✅ 1.3.88  PlanetInSign PASS; house PARTIAL
17. Houses Mainstream map                      ✅ 1.3.89  territory + families; not Canon
18. House Canon grammar                        ✅ 1.3.90  arena; not fill
19. House Canon fill                           ✅ 1.3.91  12 packs + origin; not schema
20. House Canon storage / materialization      ✅ 1.3.92  house_canon_pack; 12 drafts; Lilly unchanged
21. Planet × House smoke → STOP Houses         ✅ 1.3.93  PlanetInHouse PASS; 1.3.82/1.3.88 house PARTIAL = snapshot
22. Aspects Mainstream map                     ✅ 1.3.94  territory + families; not grammar
23. Aspect Canon grammar                       ✅ 1.3.95  one slot (`relation`); dry-run ≠ fill
24. Aspect Canon fill                          ✅ 1.3.96  five packs; origin direct; not schema
25. Aspect Canon storage / materialization     ✅ 1.3.97  aspect_canon_pack; five drafts; interaction unchanged
26. Stored Planet × Aspect smoke → STOP Aspects ✅ 1.3.98  stored source; Square≠Opposition; Trine≠Sextile
27. ASC/MC parent 1–4                          ✅ 1.3.99  orientation loci; slots unspecified
28. Mainstream Angle Semantic Map              ✅ 1.3.100 same panel; House 1/10 not proof; not grammar
29. Angle Canon grammar                        ✅ 1.3.101 one slot (`orientation`); include-first; secondary = collision-zone
30. Angle Canon fill                           ✅ 1.3.102 include-direct; House 1/10 collision; not objects
31. Angle Canon storage / materialization      ✅ 1.3.103 angle_canon_pack; two drafts; not smoke
32. Stored Planet × Angle smoke → STOP Angles  ✅ 1.3.104 stored source; Mars AT ASC ≠ Mars AT MC ≠ House 1/10
33. Final atomic smoke                         ✅ 1.3.105 five stored families; operators discriminate
34. Knowledge Core V1 FREEZE                   ✅ 1.3.106 five stored families = V1 atoms; catalog unchanged
35. IL-2 composition rules                     ✅ 1.3.107 role weights, conflict, merge; Layer 5 demoted where atoms exist
36. IL-3 Interpretation Engine                 ✅ 1.3.108 sky-internal theme rank; not user relevance; not expression
37. IL-4 Expression                            ✅ 1.3.109 voice for already chosen themes; not meaning; not `active`
38. Library scale                              ✅ 1.3.110 616 composed cells; gold 43/12; wire named, not live
39. Wire calc → IL                             ✅ 1.3.111 library layer; product surfaces not attached
```

Historical literature does not appear in this order. Lenses stay in the existing corpus. Co–Star is a check on Mainstream rows, not a source.

---

## Changelog

- **1.41 (2026-08-23)** — Calc → IL wire (1.3.111). Library layer live. KC-C-WIRE locked. Next named = attach IL-4 packs to product surfaces.
- **1.40 (2026-08-23)** — Library scale (1.3.110). Coverage contract. KC-C-SCALE locked. Next named = wire calc → IL. **Done 1.3.111.**
- **1.39 (2026-08-23)** — IL-4 Expression (1.3.109). Voice packs. KC-C-EXPR locked. Next named = library scale. **Done 1.3.110.**
- **1.38 (2026-08-23)** — IL-3 Interpretation Engine (1.3.108). Sky-internal theme rank. KC-C-ENGINE locked. Next named = IL-4. **Done 1.3.109.**
- **1.37 (2026-08-23)** — IL-3 boundary: sky → astrological themes; not user relevance. Not a new SoT file. Handoff §3. **Done 1.3.108.**
- **1.36 (2026-08-23)** — IL-2 composition rules (1.3.107). Role weights, conflict, merge. KC-C-RULES locked. Layer 5 gold composed where atoms exist. Next named = IL-3. **Done 1.3.108.**
- **1.35 (2026-08-23)** — Knowledge Core V1 FREEZE (1.3.106). Five stored families = V1 atoms. Catalog unchanged. Next named = IL-2. **Done 1.3.107.**
- **1.34 (2026-08-23)** — Final atomic smoke (1.3.105). Five stored families. Operators discriminate. Occupancy ≠ conjunction. Next = Knowledge Core V1 FREEZE. **Done 1.3.106.**
- **1.33 (2026-08-23)** — Stored Planet × Angle smoke (1.3.104). Four gates PASS. Occupancy ≠ conjunction. STOP Angles. Final atomic smoke — **done 1.3.105.**
- **1.32 (2026-08-22)** — Angle Canon storage/materialization (1.3.103). Two drafts carry `canon.orientation`. Stored Planet×Angle smoke — **done 1.3.104.**
- **1.31 (2026-08-22)** — Angle Canon fill (1.3.102). Two packs. Origin direct from include. House 1/10 collision. Storage/materialization — **done 1.3.103.**
- **1.30 (2026-08-22)** — Angle Canon grammar (1.3.101). One slot (`orientation`). Include-first. Secondary = collision-zone. Angle Canon fill — **done 1.3.102.**
- **1.29 (2026-08-22)** — Mainstream Angle Semantic Map (1.3.100). Same panel. House 1/10 not proof. Angle Canon grammar — **done 1.3.101.**
- **1.28 (2026-08-22)** — Angle Canon model (1.3.99). Parent 1–4. Orientation loci. Named slots unspecified. Mainstream Angle map — **done 1.3.100.**
- **1.27 (2026-08-22)** — Stored Planet × Aspect smoke (1.3.98). Four gates PASS. Trine vs Sextile on one pair. STOP Aspects. Angle model — **done 1.3.99.**
- **1.26 (2026-08-22)** — Aspect Canon storage/materialization (1.3.97). Five drafts carry `canon.relation`. `interaction` unchanged. Next = 1.3.98 stored Planet × Aspect smoke. **Done 1.3.98.**
- **1.25 (2026-08-22)** — Aspect Canon fill (1.3.96). Five packs. Origin direct. Mixed-valence guard. Next = storage/materialization. **Done 1.3.97.**
- **1.24 (2026-08-22)** — Aspect Canon grammar (1.3.95). One slot (`relation`). Effort / `requires_action` surplus. Next = Aspect Canon fill. **Done 1.3.96.**
- **1.23 (2026-08-22)** — Mainstream Aspect Semantic Map (1.3.94). Same panel. Relation ≠ theme. Next = Aspect Canon grammar. **Done 1.3.95.**
- **1.22 (2026-08-22)** — Planet × House composition smoke (1.3.93). PASS. STOP Houses. Historical PARTIAL = snapshot. Next = Aspects Mainstream. **Done 1.3.94.**
- **1.21 (2026-08-22)** — House Canon storage/materialization (1.3.92). Twelve drafts carry `canon.arena`. Next = Planet × House smoke. **Done 1.3.93.**
- **1.20 (2026-08-22)** — House Canon fill (1.3.91). Twelve packs. Next = storage/materialization. **Done 1.3.92.**
- **1.19 (2026-08-22)** — House Canon grammar (1.3.90). One slot (`arena`). Next = House Canon fill. **Done 1.3.91.**
- **1.18 (2026-08-22)** — Mainstream House Semantic Map (1.3.89). Same panel. House ≠ angle. Next = House Canon grammar. **Done 1.3.90.**
- **1.17 (2026-08-22)** — Planet × Sign composition smoke (1.3.88). PASS. STOP Signs. Next = Houses Mainstream. **Done 1.3.89.**
- **1.16 (2026-08-21)** — Sign Canon materialization (1.3.87). Twelve drafts. Next = 1.3.88 smoke-test. **Done 1.3.88.**
- **1.15 (2026-08-21)** — Sign Canon storage (1.3.86). Optional `canon` on signs. Next = write packs onto drafts. **Done 1.3.87.**
- **1.14 (2026-08-21)** — Sign Canon fill (1.3.85). Twelve packs. Four gates. Next = Sign Canon storage. **Done 1.3.86.**
- **1.13 (2026-08-21)** — Sign Canon grammar (1.3.84). Two slots. Sign = how. Next = Sign Canon fill. **Done 1.3.85.**
- **1.12 (2026-08-21)** — Mainstream Sign Semantic Map (1.3.83). Same panel as planets. Classification is not proof. Trait ≠ manner named, not split. Next = Sign Canon grammar. **Done 1.3.84.**
- **1.11 (2026-08-21)** — Composition smoke-test (1.3.82). Aspect PASS. Sign/house PARTIAL. Next = Signs Mainstream for Sign Canon grammar. **Done 1.3.83.**
- **1.10 (2026-08-21)** — Sun–Saturn canon fill (1.3.81). Next = 1.3.82 smoke-test, not Signs. **Done 1.3.82.**
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

