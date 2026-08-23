# Angle Canon Model V1

**Date:** 2026-08-22  
**Status:** LOCKED (parent steps 1–4). **Not** grammar. **Not** fill. **Not** JSON. **Not** schema. **Not** objects. **Not** CORE. **Not** a book. **Not** slots copied from House or Sign.  
**Canon:** [INTERPRETATION_LIBRARY_V1.md](./INTERPRETATION_LIBRARY_V1.md) §6.53. Parent: [KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md](../KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md). Inventory: [KNOWLEDGE_CORE_V1_SEMANTIC_INVENTORY.md](./KNOWLEDGE_CORE_V1_SEMANTIC_INVENTORY.md) KC-ANG-ASC · KC-ANG-MC. House guard: [HOUSE_CANON_GRAMMAR_V1.md](./HOUSE_CANON_GRAMMAR_V1.md) §2.3 · [MAINSTREAM_HOUSE_SEMANTIC_MAP_V1.md](./MAINSTREAM_HOUSE_SEMANTIC_MAP_V1.md). House 1 / 10 packs: [HOUSE_CANON_V1.md](./HOUSE_CANON_V1.md). Compose gate: [ASTROLOGY_COMPOSITION_MODEL.md](../ASTROLOGY_COMPOSITION_MODEL.md). Split: [KNOWLEDGE_CORE_V1_PRODUCT_CANON_AND_LENSES.md](./KNOWLEDGE_CORE_V1_PRODUCT_CANON_AND_LENSES.md). Geometry: [foundation_v1.md](../foundation_v1.md). Precedent: [IL1_LAYER1_OUTERS_DEFINITION.md](./IL1_LAYER1_OUTERS_DEFINITION.md).

This file answers parent steps 1–4 for ASC and MC:

> What **compositional type** do chart angles have, such that Composition can use them without collapsing ASC to 1st House and MC to 10th House?

It does not name Canon slots. It does not lock lemmas. It does not open the Mainstream panel.

1.3.98 closed Aspects. Planet / Sign / House / Aspect atoms are stored + smoke PASS. Angles were the remaining gold-set family whose **job** was undefined. Do not skip this lock and start a map or a fill.

---

## Architecture impact

- **SoT before:** KC-ANG-ASC / KC-ANG-MC were `NEED_MODEL` — constituents undefined; parent 1–4 never run. House Canon already forbids `1st = ASC` and `10th = MC`. Risk: copy `arena` onto angles, copy `manner`, treat angles as routing anchors, or paste mask / career cookbooks because Profile already prints ASC/MC.
- **SoT after:** ASC and MC are **orientation loci** (horizon vs meridian). Routing stays House. Projection-strength stays Foundation. Named Canon slots wait for grammar. Catalog untouched. Literature still forbidden. Cookbooks still out of queue.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this file · IL §6.53 · inventory KC-ANG · handoff
- **Backward compatible?** yes (`draft`). Deprecated as the angle job: House 1 / House 10 substitution; `arena` / `manner` / `relation` by analogy; angular = stronger as meaning.

---

## 0. Question this model is allowed to answer

Closed stack:

```text
Planet  =  what the function is
Sign    =  how that function is done
House   =  where it is routed
Aspect  =  how two functions are linked
Angle   =  ?   ← this pass
```

Only this:

> What does an already-known planet function (and optionally its sign manner) **attach to** when the chart point is ASC or MC, if that attachment must not be a house arena?

If a proposed type does not change Planet-on-ASC vs Planet-in-House-1, it is surplus. If it makes them the same construction, it is forbidden.

---

## 1. Subject

A Layer 1 *angle* is an IL knowledge object for a calc-emitted chart-edge point: **ASC** (eastern horizon) or **MC** (upper meridian).

It is a semantic primitive of the lookup. It is not Foundation identity by itself, not a house span, not a sign, not a planet function, not a Layer 5 combination.

V1 gold set is **ASC + MC only**. DSC and IC exist geometrically as opposites. They are not IL V1 objects this pass.

Calc already emits ASC/MC when birth time and place are known. Identity emit does not, by itself, justify an IL meaning pack.

---

## 2. Bounds

- **ASC ≠ House 1.** The 1st is a span with locked `arena`: `self-presentation · appearance · first-impression`. The ASC is a point on the horizon. A planet can occupy House 1 without conjuncting ASC (Placidus). That geometry is the proof they are different objects.
- **MC ≠ House 10.** The 10th is a span with locked `arena`: `career · public-role · reputation · calling`. The MC is a point on the meridian. Same occupancy/conjunction split.
- **Angle ≠ Sign.** Rising sign / MC-in-sign is Sign manner **on** an angle, not the angle’s own payload and not House 1 / House 10.
- **Angle ≠ Planet function.** ASC does not `act` / `feel` / `identify`. A planet on the angle still carries `core_function`.
- **Angle ≠ angularity-as-meaning.** “On an angle ⇒ stronger / louder” is Foundation magnitude / overlay ranking. It does not discriminate ASC from MC. It is not an IL lemma family.
- **No automatic transfer** of traditional (mask, appearance-as-fate) or modern (career MC, vocation-as-soul) cookbooks into Canon. Consumer job first. Territory later. Lemmas last.
- **No books.** Mainstream panel pages are the later map, not this pass.
- **DSC / IC** are not gold objects. Compat may use ASC as a relating orientation; it does not mint a DSC IL object here.
- **Time unknown:** angles are omitted as facts (Foundation). Do not invent meaning to fill the hole.

Profile journey copy that glosses MC as “house 10 / mc” is a **consumer leak**, not a license for Canon.

---

## 3. Candidate types (deletion against the closed stack)

Four candidates. One survives.

| Candidate | What it would do in composition | Delete it? |
|-----------|----------------------------------|------------|
| **Routing anchors** | Send a planet function *into* ASC/MC as if they were destinations | **Rejected.** House.arena already answers where. Routing-to-ASC is House 1 by another name. |
| **Projection points** | Mark planets that cast onto the angle as louder / more available | **Rejected as the meaning type.** Useful as Foundation/ranking. Does not discriminate ASC from MC. No semantic payload beyond “this is angular.” |
| **Public–private axis (as payload)** | Load ASC with private/self and MC with public/career | **Rejected as the payload type.** Those lemmas already live on House 4 (`private-base`) and House 10 (`public-role`). Copying them collapses the guard. Horizon vs meridian may *discriminate* the two orientations; they must not steal house arenas. |
| **Orientation loci** | Attach a known function to a chart-edge facing: how it is met (horizon) vs how it stands at height (meridian) | **Required.** Survives House 1 / House 10 occupancy. Discriminates ASC from MC without copying `arena`. |

STOP. Do not invent a fifth type because Signs had two slots or Aspects had `relation`.

### 3.1 Why routing cannot be the job

```text
Mars.core_function(act · pursue · assert)
  ×  house.1.arena(self-presentation · appearance · first-impression)
  →  acting routed into the meeting-face sphere

Mars.core_function(act · pursue · assert)
  AT  ASC as routing-anchor
  →  the same construction with a different name
```

If ASC is a routing anchor, KC-H-ASC≠1 is dead. House Canon already dropped `angle identity` as surplus. This model must not reintroduce it.

### 3.2 Why projection cannot be the job

Conjunction to ASC and conjunction to MC would share one payload: `angular` / `stronger`. Composition would still need a second source to say *which* edge. That second source is the orientation type. Projection is then ranking, not Canon.

### 3.3 Why public–private cannot be the payload

House 1 is not “private.” House 1 arena is meeting-face / appearance. House 10 arena is public-role / career. If MC Canon is `public-role`, Planet-on-MC and Planet-in-10 become interchangeable. The geometric split (point vs span) would have no semantic consequence.

---

## 4. Locked compositional type

**Orientation locus.**

An angle orients how an already-known function (and optionally its sign manner) **meets a chart edge**. It does not say what the function is, how it is done, where in life it lives, or how two functions are linked.

```text
Planet  =  what
Sign    =  how
House   =  where (arena)
Aspect  =  relation
Angle   =  which chart-edge orientation the function is attached to
```

Discrimination (locked as a requirement, not as lemmas):

| Angle | Geometric edge | Orientation job (type label, not a pack) |
|-------|----------------|------------------------------------------|
| **ASC** | eastern horizon | how the function is **met / meets** at the rising edge |
| **MC** | upper meridian | how the function **stands / is seen** at culmination |

Those type labels are **not** Canon values. Grammar must not paste House 1 `self-presentation` or House 10 `career` to fill them.

Constructions this type must keep distinct (dry, not fill):

```text
planet.core_function  AT  ASC.orientation(horizon)
  ≠  planet.core_function  IN  house.1.arena

planet.core_function  AT  MC.orientation(meridian)
  ≠  planet.core_function  IN  house.10.arena

sign.manner  ON  ASC.orientation
  ≠  house.1.arena
  ≠  a person-type
```

LLM (IL-4) formulates the frame. It does not choose whether ASC is a house.

---

## 5. Constituents (model, not slots)

Parent step 3 is the **set**, not a grammar. Named lemma slots are not copied from House (`arena`) or Sign (`manner` · `excess`) or Aspect (`relation`).

| Band | What | Status in this pass |
|------|------|---------------------|
| Identity (not IL meaning) | calc emit · longitude · occupying sign as **fact** | Already true. Does not justify an IL pack |
| Compositional type | orientation locus (horizon vs meridian) | **Locked** |
| Discrimination requirement | ASC pack ≠ MC pack in any later fill | **Locked as a gate.** Lemmas wait |
| Named Canon slots | one required: `orientation` (1.3.101) | **Unspecified** at 1.3.99; **locked in grammar.** Do not copy `arena` / `manner` / `relation` |
| Exclude | house `arena` copy · sign `manner` copy · planet `core_function` copy · mask cookbook · career cookbook · angular=stronger · DSC/IC objects · pair essays | Locked out |

The full set of *model* constituents is therefore: type + discrimination + “slots named later without analogy.” That is enough to end `NEED_MODEL`. It is not enough to fill.

---

## 6. Definitions

- **Chart angle:** a calc-emitted horizon or meridian point used as an orientation locus in composition.
- **Orientation locus:** the chart-edge job that tells Composition **which way** a known function is faced or seen, without saying where in life it lives (house), how it is done (sign), what it is (planet), or how two functions link (aspect).
- **Not a constituent:** Foundation identity; Swiss coordinates; house arena; sign manner; planet function; Layer 5 combinations; product voice; DSC/IC as V1 objects.
- **Rising sign / MC-in-sign:** composition (Sign **on** Angle). Not an angle slot. Not House 1 / House 10.
- **Planet on angle:** composition (Planet **at** orientation locus). Not PlanetInHouse.

---

## 7. Consumer jobs (the test of the type)

Inventory already named the surfaces. They do not get extra slots here. They must be servable **from orientation**, not from house substitution.

| Consumer | What it may ask the angle | What it must not ask |
|----------|---------------------------|----------------------|
| **Profile** | How this person is met (ASC) / how they stand at height (MC) | Textbook “ASC = mask”; “MC = career house” |
| **Overlay angularity** | Ranking may use Foundation geometry; meaning is Planet **at** the orientation | Rewrite a transit as House 1 / House 10 because the cusp is nearby |
| **Compatibility axes** | ASC as relating-orientation | A DSC IL object; House 7 as a substitute for ASC |

If a later grammar slot does not change one of these constructions, it is surplus.

---

## 8. Sufficiency bar for later passes

A Mainstream map (next) may list concept families. It must tag leakage: house-arena copies, sign-manner copies, planet-function copies, cookbooks.

Grammar may name slots **only if**:

1. Deleting the slot collapses Planet-on-ASC vs Planet-on-MC, or Sign-on-ASC vs Sign-on-MC.
2. The slot is not House 1 / House 10 `arena`.
3. The slot is not Sign `manner` / `excess`.
4. The slot is not Planet `core_function`.
5. The slot is not `stronger` / luck / vocation-as-fate.

Fill is forbidden until that grammar exists. Objects are forbidden until storage is named. Stored Planet×Angle smoke is forbidden until packs are on drafts. Final atomic smoke is forbidden until Angles are closed the same way Planet / Sign / House / Aspect were: stored-source gate, then STOP Angles.

---

## 9. This pass does not do

- Mainstream Angle Semantic Map (territory)
- Angle Canon grammar (slots)
- Fill · schema · `astro.object.asc` / `astro.object.mc`
- Copy House 1 or House 10 packs onto angles
- DSC / IC objects
- Books · CORE · Co–Star ingest · `active`
- Reopen Planet / Sign / House / Aspect packs
- Final atomic smoke · Knowledge Core V1 FREEZE · IL-2

**Stopped before parent step 5** (schools / source types for angle drafts). 1.3.76 already forbids books; the next family pass is a Mainstream panel map, not a school shortlist.

---

**Next named:** Mainstream Angle Semantic Map — **done 1.3.100.** Angle Canon grammar — **done 1.3.101** (one slot: `orientation`). Angle Canon fill — **done 1.3.102.** Angle Canon storage/materialization — **done 1.3.103.** stored Planet×Angle smoke — **done 1.3.104.** **STOP Angles.** Final atomic smoke — **done 1.3.105.** Knowledge Core V1 FREEZE — **done 1.3.106.** Next = IL-2. **STOP Aspects.** **STOP Houses.** **STOP Signs.** Do not start CORE scoring. Do not start ASC cookbooks.

---

## Changelog

- **1.2 (2026-08-22)** — Angle Canon grammar locked 1.3.101. One slot (`orientation`). Include-first. Secondary = collision-zone. Next = Angle Canon fill.
- **1.1 (2026-08-22)** — Mainstream Angle map locked 1.3.100. Sequence corrected: stored Planet×Angle smoke and STOP Angles before final atomic smoke.
- **1.0 (2026-08-22)** — 1.3.99. Parent steps 1–4. Angles = orientation loci (horizon vs meridian). Routing / projection / public–private-as-payload rejected. Named slots unspecified. Catalog unchanged.
