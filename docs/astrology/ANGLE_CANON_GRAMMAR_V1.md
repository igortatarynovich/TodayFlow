# Angle Canon Grammar V1

**Date:** 2026-08-22  
**Status:** LOCKED (grammar + slot semantics). Dry-run lemmas are **not** locked values. **Not** fill. **Not JSON.** **Not** schema. **Not** objects. **Not** CORE. **Not** a book. **Not** IL-2.  
**Canon:** [INTERPRETATION_LIBRARY_V1.md](./INTERPRETATION_LIBRARY_V1.md) §6.55. Territory: [MAINSTREAM_ANGLE_SEMANTIC_MAP_V1.md](./MAINSTREAM_ANGLE_SEMANTIC_MAP_V1.md). Model: [ANGLE_CANON_MODEL_V1.md](./ANGLE_CANON_MODEL_V1.md). House grammar: [HOUSE_CANON_GRAMMAR_V1.md](./HOUSE_CANON_GRAMMAR_V1.md). House packs: [HOUSE_CANON_V1.md](./HOUSE_CANON_V1.md). Planet packs: [PLANET_CANON_V1.md](./PLANET_CANON_V1.md). Aspect grammar: [ASPECT_CANON_GRAMMAR_V1.md](./ASPECT_CANON_GRAMMAR_V1.md). Compose gate: [ASTROLOGY_COMPOSITION_MODEL.md](../ASTROLOGY_COMPOSITION_MODEL.md). Split: [KNOWLEDGE_CORE_V1_PRODUCT_CANON_AND_LENSES.md](./KNOWLEDGE_CORE_V1_PRODUCT_CANON_AND_LENSES.md).

This file answers **one** question:

> What **minimal payload** does an angle need so Composition can attach an already-known planet function to ASC vs MC **without House.arena and without a ready interpretation**?

It does not answer “what rising-sign person.” It is not a career essay. It is not a copy of House Canon. It does not decide Profile / Today / Compatibility separately. If the atomic frame is right, the consumer is downstream.

1.3.99 locked the type (orientation locus). 1.3.100 locked include / secondary / exclude. Do not reopen the type. Do not reopen the panel. Canon is allowed — and expected — to be **narrower** than that territory.

---

## Architecture impact

- **SoT before:** 1.3.100 locked territory. Slot count unnamed. Risk: copy `arena` / `manner` / `relation` by analogy; promote appearance / first-impression or career / reputation / calling from the collision-zone; treat personal-facing vs public-facing as a second public–private atom; write Mars-conjunct-ASC essays; skip grammar and fill from House 1 / House 10.
- **SoT after:** Angle generative role is **orientation** (which chart-edge a known function is attached to), not routing (where) and not interpretation (what it means). **One required slot:** `orientation`. Fill must start from **include-territory**. Secondary stays a **collision-zone**, not a default candidate. `facing` as its own slot is surplus. Dry-run lemmas wait for fill. Catalog untouched.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this file · IL §6.55 · inventory execution · handoff
- **Backward compatible?** yes (`draft`). Deprecated as grammar source: House 1 / House 10 packs; Foundation horizon/meridian copied as meaning; angular = louder; planet-on-angle cookbooks; 1.3.99 type labels used *instead of* a fillable slot.

---

## 0. Question this grammar is allowed to answer

```text
Planet  =  what the function is
Sign    =  how that function is done
House   =  where it is routed
Aspect  =  how two functions are linked
Angle   =  which chart-edge orientation the function is attached to
```

Only this:

> What minimal angle payload does the engine need to hang a known planet function on ASC vs MC **without borrowing House.arena and without interpreting the placement first**?

If a proposed slot does not change that hang, it is surplus. Houses got one slot because people/events did not survive deletion. Signs got two because `excess` did. Aspects got one because effort did not. Angles do not inherit any of those counts.

Target boundary (locked):

```text
Planet atoms (+ optional Sign manner)  AT  Angle.orientation  →  structured frame
House.arena                                                →  not an input
IL-2                                                       →  composition rules
IL-4                                                       →  formulates
```

Angle Canon orients the attachment. It does **not** decide what the placement means.

---

## 1. Generative role (locked)

| Layer | Job | Not the job |
|-------|-----|-------------|
| **Planet Canon** | Function semantics (`core_function` · `drive` · `domains` …) | Costume, sun-sign portrait |
| **Sign Canon** | Manner semantics — how that function is carried | A second planet; a person-type |
| **House Canon** | Arena / routing — where that function lands | An angle; a person |
| **Aspect Canon** | Topology of the link | Meaning of the link |
| **Angle Canon** | Orientation of the attachment — which chart edge the function is hung on | House arena; a rising-sign person; a career; an interpretation |

```text
Mars.core_function(act · pursue · assert)
  AT  ASC.orientation(doorway-meeting · how-met · automatic-response)
  →  acting/asserting attached at the rising edge (how the function is met)

Mars.core_function(act · pursue · assert)
  AT  MC.orientation(culmination · outer-mark · aiming)
  →  acting/asserting attached at the meridian (how the function stands at height)
```

The planet still acts. The angle does not become House 1, House 10, “mask,” or “career.” LLM (IL-4) formulates the frame. It does not choose whether ASC is a house.

### 1.1 Angle Canon is not a mini-Composition Engine (locked)

Need for a nicer sentence is **not** proof of a second Canon slot. Planet-conjunct-ASC / MC recipes already contain composition. That work belongs to IL-2 and IL-4. If 1.3.101 looks “thin” next to a finished Profile line, that is the point.

### 1.2 Angle.orientation ≠ House.arena (locked)

They both sound like “where this shows.” They do different work.

| Slot | Question | Example (Mars) |
|------|----------|----------------|
| **house.canon.arena** | Where in life is this function routed? | 1st: self-presentation · appearance · first-impression |
| **angle.canon.orientation** | Relative to which chart edge is this function attached? | ASC: doorway-meeting · how-met · automatic-response |

House arena is a span. Angle orientation is a point. A planet can occupy House 1 without conjuncting ASC. Do **not** name the angle slot `arena`. Do **not** copy House 1 / House 10 packs. Do **not** treat cusp identity as proof.

### 1.3 Include-first; secondary is a collision-zone (locked)

Grammar solves the deletion test on **include-territory** first.

| Bucket | Status in this grammar |
|--------|------------------------|
| **Include** | Candidate input to `orientation` |
| **Secondary** | Collision-zone. Present on the panel, **not** a default Canon candidate |
| **Exclude** | Out |

Secondary must not be promoted because it is frequent. Appearance / first-impression / mask are too close to House 1 `arena`. Career / reputation / calling are too close to House 10 `arena`. If include already discriminates ASC from MC, secondaries stay out of generative Canon.

---

## 2. Locked slots

One. Not two. Not copied.

| Slot | What it means | Why the engine needs it |
|------|----------------|-------------------------|
| **orientation** | Chart-edge facing a known planet function is attached to (orientation lemmas) | Distinguishes Planet-on-ASC from Planet-on-MC without House 1 / House 10 |

Each slot is a short list of **lemmas**, not a sentence, not a Today line, not a rising-sign blurb.

### 2.1 Literal deletion test (locked)

```text
same planet.core_function  AT  ASC  vs  AT  MC
without house.1.arena and without house.10.arena
If still distinct after removing the proposed payload → surplus
If not → candidate Angle Canon slot
```

Checked against locked 1.3.100 **include**, not secondary, not cookbooks.

| Angle | Include (1.3.100) | Orientation one slot must keep |
|-------|-------------------|--------------------------------|
| ASC | doorway-meeting · how-met / personal-first-contact · automatic-response · personal-facing | function is **met** at the rising edge |
| MC | culmination / height · public-facing · mark-in-the-outer-world · aiming / destination-at-height | function **stands / aims** at culmination |

**Include-first stem (locked as the discrimination to preserve, not as fill values):**

```text
ASC  →  doorway-meeting · how-met · automatic-response
MC   →  culmination / height · mark-in-the-outer-world · aiming / destination-at-height
```

That pair survives without House.arena. Fill may narrow further. It may not add House 1 / House 10 lemmas to make the pair “clearer.”

`personal-facing` / `public-facing` are include. They may support the same slot. They are **not** the stem and **not** a second atom. Using them as the only discriminator would reintroduce the rejected public–private payload (House 4 `private-base` / House 10 `public-role`).

### 2.2 Deletion test (locked)

> If this slot is removed, does the engine lose a real difference between Planet-on-ASC and Planet-on-MC **without House 1 / House 10**?

| Slot | Delete it? | Result |
|------|------------|--------|
| **orientation** | Remaining = object id + Foundation horizon/meridian. Object id is house-number logic. Geometry-as-meaning was already excluded. Type labels from 1.3.99 *are* this slot’s job, not a substitute. Same planet function on ASC vs MC becomes two names for a point. | **Required** |
| facing / public–private as own slot | Doorway-meeting vs culmination already discriminates. Personal/public as the payload was rejected in 1.3.99. | **Surplus** |
| arena copy | House job. ASC-as-destination = House 1. MC-as-destination = House 10. | **Forbidden**, not surplus |
| manner / excess | Sign job. Rising-sign / MC-in-sign is Sign **on** Angle. | **Surplus** |
| core_function / drive | Planet job. ASC does not `act`. | **Surplus** |
| relation | Aspect job. | **Surplus** |
| appearance / first-impression / mask | Secondary collision-zone (House 1). Include already works. | **Out of generative Canon** |
| career / reputation / calling / profession | Secondary collision-zone (House 10). Include already works. | **Out of generative Canon** |
| angular / stronger / louder | Foundation ranking. Does not discriminate ASC from MC. | **Surplus** |
| pair-specific lemmas | `Mars conjunct ASC` as stored meaning. Already composition. | **Surplus** |
| surface-specific rules | Today / Profile / Compatibility as three angle grammars. Consumer is downstream. | **Surplus** |

STOP at one slot. Do not add a second because Signs had `excess`, because Cafe names public vs personal face, or because a pretty sentence wants House 10 vocabulary.

### 2.3 Geometric guard (locked)

```text
planet.core_function  IN  house.1.arena
  ≠  planet.core_function  AT  ASC.orientation

planet.core_function  IN  house.10.arena
  ≠  planet.core_function  AT  MC.orientation
```

A planet can occupy House 1 without conjuncting ASC. If a slot, lemma, or later pack erases that split, the grammar is broken.

### 2.4 Guards (locked)

- **Angle ≠ house.** ASC is not House 1. MC is not House 10.
- **Angle ≠ sign.** Rising sign is Sign-on-Angle.
- **Angle ≠ planet.** ASC does not `act` / `feel` / `identify`.
- **Angle ≠ interpretation.** No stored “Mars rising means…”.
- **Angle ≠ angular strength.**
- **Secondary ≠ default candidate.** Collision-zone stays out until include fails — and include does not fail.
- **One pack per angle.** The same ASC pack must attach Mars and Venus. The same MC pack must attach Mars and Venus.
- **Angle ≠ mini-Composition Engine.** Orientation of the attachment, not what the placement means.
- **Angle ≠ surface grammar.** No separate Today / Profile / Compatibility rules.

---

## 3. Territory fitness (hypothesis, not Canon)

1.3.100 families are **input**. This cut is a grammar check. Fill (next) may drop more. It must not add families that are not on that map. It must not promote secondary to fill the stem.

| Bucket | Goes to | Test |
|--------|---------|------|
| **orientation-fit (include)** | Candidate `orientation` | Can it hang Mars.act on ASC vs MC without House.arena and without a ready interpretation? |
| **collision-zone (secondary)** | Stays in territory; **out of generative Canon** | appearance · first-impression · mask · beginning-new-experiences · career · reputation · calling |
| **personal-facing / public-facing** | Supporting include inside `orientation`, not a second slot, not the stem | Cafe face-discrimination; must not become House 4 / House 10 |
| **exclude** | **Out** | ASC = House 1 · MC = House 10 · angular=stronger · planet conjunct · rising portraits · MC-in-sign careers |

Canon **must not** try to place every locked family. Expected leftovers: House-collision secondaries, mask-as-cookbook, vocation-as-office, angular strength.

### 3.1 Cut (illustrative — not fill)

Include-first. Secondary not used.

| Angle | Orientation-fit (candidate) | Out of generative Canon |
|-------|-----------------------------|-------------------------|
| ASC | doorway-meeting · how-met · automatic-response | appearance · first-impression · mask · beginning-new-experiences · ASC = House 1 · rising-sign portraits · planet conjunct ASC |
| MC | culmination / height · mark-in-the-outer-world · aiming / destination-at-height | career · reputation · calling · profession · MC = House 10 · MC-in-sign career lists · planet conjunct MC |

`personal-facing` (ASC) and `public-facing` (MC) may ride in the same slot as support. Fill decides whether they stay. They must not become the only lemmas, and they must not be rewritten as `private-base` / `public-role`.

Astrodienst “MC and the tenth house represent profession” remains a **leak**, not a candidate.

---

## 4. How a pack is used (not implemented this pass)

```text
planet.core_function (+ optional sign.manner)
  AT  angle.orientation
  →  structured frame: this function attached at this chart edge
  →  IL-2 applies composition rules
  →  IL-4 formulates
```

Do not store `Mars conjunct ASC` essays.

House.arena is not an input to this transform. Angular ranking is not an input. Rising-sign portraits are not an input.

---

## 5. Dry-run (not locked)

Input = planet `core_function` from [PLANET_CANON_V1.md](./PLANET_CANON_V1.md) + House 1 / House 10 `arena` from [HOUSE_CANON_V1.md](./HOUSE_CANON_V1.md) + §3 orientation-fit. Output = grammar check. **Fill later.** Do not copy these rows into objects.

Planet lemmas below are locked packs, not new research. House lemmas are locked packs, used only as the **negative** control.

### Mars AT ASC — doorway / how-met

Mars.act/pursue/assert × ASC include-stem

```text
planet:       act · pursue · assert
orientation:  doorway-meeting · how-met · automatic-response
frame:        acting/asserting attached at the rising edge — how the function is met
not used:     house.1.arena · appearance · first-impression · mask
```

### Mars AT MC — height / aiming

Same planet function. Different edge.

```text
planet:       act · pursue · assert
orientation:  culmination · mark-in-the-outer-world · aiming
frame:        acting/asserting attached at the meridian — how the function stands / aims at height
not used:     house.10.arena · career · reputation · calling
```

### Negative control — Mars IN House 1

```text
planet:  act · pursue · assert
arena:   self-presentation · appearance · first-impression
frame:   acting/asserting routed into the meeting-face sphere
```

Occupancy of the 1st is not conjunction with ASC. The frames must not match.

### Negative control — Mars IN House 10

```text
planet:  act · pursue · assert
arena:   career · public-role · reputation · calling
frame:   acting/asserting routed into public-role / career
```

Occupancy of the 10th is not conjunction with MC. The frames must not match.

### Composability — Venus AT ASC

Same ASC pack. Different planet function.

```text
planet:       attract · value · relate
orientation:  doorway-meeting · how-met · automatic-response
frame:        valuing/relating attached at the rising edge — how the function is met
```

Venus does not get a private ASC pack. Mars does not get a private MC pack.

### Dry-run score

| Check | Result |
|-------|--------|
| Same planet function on ASC vs MC is distinct without House.arena | yes — doorway/how-met vs culmination/aiming |
| Mars in 1st ≠ Mars conjunct ASC | yes — arena vs orientation; occupancy ≠ conjunction |
| Mars in 10th ≠ Mars conjunct MC | yes |
| Secondary collision lemmas were not required | yes — appearance / career unused |
| personal/public was not the only discriminator | yes — not the stem |
| Venus and Mars share one ASC pack | yes |
| No construction copied `arena` / `manner` / `relation` as the angle slot | yes |
| No construction used angular=stronger as meaning | yes |
| No construction wrote a planet-on-angle cookbook | yes |
| One slot was enough | yes — facing / arena-copy / manner failed the deletion test |
| Extra fields for a pretty sentence | not taken as Canon; IL-2 / IL-4 |

If ASC and MC frames had used House 1 / House 10 vocabulary to become distinct, the grammar would fail.

---

## 6. This pass does not do

- Lock dry-run lemmas as Canon values
- Fill ASC / MC · schema · `astro.object.asc` / `astro.object.mc` · `active`
- Promote secondary collision-zone into the stem
- Copy House 1 / House 10 packs
- Planet×Angle smoke — **done 1.3.104** · final atomic smoke — **done 1.3.105**
- DSC / IC objects
- Rising-sign portraits · MC-in-sign careers
- Sign / House / Aspect pack edits · books · CORE · Co–Star ingest
- IL-2 composition rules · surface-specific angle grammars

**Sequence (locked, not skipped):** grammar (this file) → fill → storage/materialization → stored Planet×Angle smoke — **done 1.3.104** → **STOP Angles** → final atomic smoke (Planet + Sign + House + Aspect + Angle, all stored) — **done 1.3.105** → Knowledge Core V1 FREEZE → IL-2.

**Next named:** Angle Canon fill — **done 1.3.102.** Angle Canon storage/materialization — **done 1.3.103.** stored Planet×Angle smoke — **done 1.3.104.** **STOP Angles.** Final atomic smoke — **done 1.3.105.** Next = Knowledge Core V1 FREEZE → IL-2. **STOP Aspects.** **STOP Houses.** **STOP Signs.** Do not improve planet/sign/house/aspect packs without a named Composition Engine failure.

---

## Changelog

- **1.3 (2026-08-23)** — stored Planet×Angle smoke PASS 1.3.104. Grammar unchanged. STOP Angles. Final atomic smoke — **done 1.3.105.** Next = Knowledge Core V1 FREEZE.
- **1.2 (2026-08-22)** — Angle Canon storage/materialization locked 1.3.103. Two drafts. Grammar unchanged. stored Planet×Angle smoke — **done 1.3.104.**
- **1.1 (2026-08-22)** — Angle Canon fill locked 1.3.102. Two packs. Grammar unchanged. Storage/materialization — **done 1.3.103.**
- **1.0 (2026-08-22)** — 1.3.101. One slot (`orientation`). Include-first. Secondary = collision-zone, not default. Facing / public–private as own slot surplus. Arena copy forbidden. Dry-run: same planet function on ASC vs MC without House 1/10; planet in 1st ≠ planet conjunct ASC. Angle Canon fill — **done 1.3.102.**
