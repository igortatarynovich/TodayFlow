# Angle Canon V1

**Date:** 2026-08-22  
**Status:** LOCKED (two angle packs + provenance + five gates). **Not JSON.** **Not** schema. **Not** objects. **Not** CORE. **Not** a book. **Not** smoke.  
**Canon:** [INTERPRETATION_LIBRARY_V1.md](./INTERPRETATION_LIBRARY_V1.md) §6.56. Territory: [MAINSTREAM_ANGLE_SEMANTIC_MAP_V1.md](./MAINSTREAM_ANGLE_SEMANTIC_MAP_V1.md). Grammar: [ANGLE_CANON_GRAMMAR_V1.md](./ANGLE_CANON_GRAMMAR_V1.md). Model: [ANGLE_CANON_MODEL_V1.md](./ANGLE_CANON_MODEL_V1.md). House packs: [HOUSE_CANON_V1.md](./HOUSE_CANON_V1.md). Planet packs: [PLANET_CANON_V1.md](./PLANET_CANON_V1.md). Split: [KNOWLEDGE_CORE_V1_PRODUCT_CANON_AND_LENSES.md](./KNOWLEDGE_CORE_V1_PRODUCT_CANON_AND_LENSES.md).

This file is the product `orientation` of ASC and MC. 1.3.100 is territory. 1.3.101 is grammar. 1.3.102 is synthesis **with origin control**. Grammar dry-run lemmas are **not** inherited automatically.

```text
Mainstream include-territory → orientation synthesis → five gates → collision vs House 1/10 → lock
```

No new literature. No House 1 / House 10 vocabulary. No schema until storage. One slot only (`orientation`). Secondary collision-zone stays out. Unused include stays in territory.

---

## Architecture impact

- **SoT before:** grammar locked one slot; dry-run lemmas were illustrative. Risk: paste 1.3.101 wording as Canon; promote appearance / first-impression / mask or career / reputation / calling; treat personal-facing vs public-facing as the pack; write planet-on-angle essays.
- **SoT after:** each Canon atom is `direct` from that angle’s locked 1.3.100 **include** families. Five gates pass. Secondary unused. `personal-facing` / `public-facing` unused (include leftovers, not a second atom). Catalog untouched. Schema still later.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this file · IL §6.56 · grammar next-pointer · inventory execution · handoff
- **Backward compatible?** yes (`draft`). Deprecated: treating 1.3.101 dry-run wording as locked values; filling every territory family for symmetry; prettying lemmas for IL-4.

---

## 0. Origin rule (locked)

Same tags as Planet / Sign / House / Aspect Canon fill.

| Origin | Means | Does not mean |
|--------|-------|----------------|
| **direct** | Normalization of a 1.3.100 **include** family (same concept, shorter lemma) | Copied vendor sentence; copied 1.3.101 dry-run line |
| **direct-secondary** | Normalization of a 1.3.100 **secondary** family | Allowed in other fills; **forbidden here** (collision-zone) |
| **derived** | TodayFlow inference from **two or more** locked include families of **this** angle | A new astrology; a school package; Google |

This fill uses **direct** only. No `direct-secondary`. No `derived` atom was required.

**Reject** if: not in that angle’s 1.3.100 include even as a parent; is a 1.3.100 secondary (appearance / first-impression / mask / beginning-new-experiences / career / reputation / calling / profession); copies House 1 or House 10 `arena`; copies planet `core_function`; uses angular strength as proof; equates the angle with a house; is pair-specific (`Mars conjunct ASC`); or is user-facing copy.

Pipeline per atom:

```text
lemma → direct → parent include family → five gates → keep / rewrite / drop
```

---

## 1. Five gates (locked)

1. **Origin control** — every `orientation` atom is a 1.3.100 **include** on that angle. No secondary. No classification arithmetic. No fourth panel. No books. No 1.3.101 dry-run as a source.
2. **Orientation-fit** — the lemma must hang **several** planet functions, not only one convenient pair. The ASC pack must work on Mars and Venus **without planet-keyed angle lemmas**. Same for MC.
3. **Collision control** — the lemma is a chart-edge orientation, not a house arena ([grammar §1.2](./ANGLE_CANON_GRAMMAR_V1.md)). Locked negatives: House 1 `self-presentation · appearance · first-impression`; House 10 `career · public-role · reputation · calling`; also `mask`.
4. **Discrimination** — the same planet function on ASC vs MC must be distinguishable from the two packs alone, without House.arena.
5. **Orientation, not interpretation** — no stored “Mars rising means…”, no vocation-as-fate, no pretty sentence. Packs attach a known function to an edge. They do not interpret the placement.

Coverage is **not** “every 1.3.100 family placed.” Expected: **3** orientation atoms per angle. Leftover families stay recognizable as territory. A lemma that looks too technical for a Today line and still orients is **kept**.

---

## 2. Locked packs

Parents use 1.3.100 **include** family names. Grammar dry-run is listed once in §4 as a non-source.

Planet `core_function` atoms used in dry-runs are from [PLANET_CANON_V1.md](./PLANET_CANON_V1.md): Mars `act · pursue · assert` · Venus `attract · value · relate`. House `arena` used only as negative control: 1st `self-presentation · appearance · first-impression` · 10th `career · public-role · reputation · calling`.

### ASC

Territory used: doorway-meeting / entering-the-world · how-met / personal-first-contact · automatic-response / environmental-coping.  
Left in territory: personal-facing (include leftover; not a second atom) · appearance / first-impression / mask / beginning-new-experiences (secondary collision-zone).

```text
orientation:  doorway-meeting · how-met · automatic-response
```

| Atom | Slot | Origin | Parents |
|------|------|--------|---------|
| doorway-meeting | orientation | direct | doorway-meeting / entering-the-world |
| how-met | orientation | direct | how-met / personal-first-contact |
| automatic-response | orientation | direct | automatic-response / environmental-coping |

**Collision:** not House 1 `self-presentation` · `appearance` · `first-impression`. Not `mask`. Not Mars `act`. `entering-the-world` not chosen — too close to House 1 `starting-in-the-world`. `personal-first-contact` not chosen as the lemma — too close to `first-impression`. `personal-facing` unused — include leftover; would make public–private look like the payload.  
**Vs MC:** the function is **met** at the rising edge; it does not stand at height.  
**Orientation:** attachment at the horizon. Not a meeting-face *sphere*.

### MC

Territory used: culmination / height / most-visible-point · mark-in-the-outer-world · aiming / destination-at-height.  
Left in territory: public-facing (include leftover; not a second atom) · career / reputation / calling / profession / authority (secondary collision-zone).

```text
orientation:  culmination · outer-mark · aiming
```

| Atom | Slot | Origin | Parents |
|------|------|--------|---------|
| culmination | orientation | direct | culmination / height / most-visible-point |
| outer-mark | orientation | direct | mark-in-the-outer-world |
| aiming | orientation | direct | aiming / destination-at-height |

**Collision:** not House 10 `career` · `public-role` · `reputation` · `calling`. Not `profession`. Not Saturn `structure`. `destination-at-height` not chosen as the lemma — vocation-as-destination leak toward House 10. `public-facing` unused — include leftover; would make public–private look like the payload. Astrodienst “MC and the tenth house represent profession” remains a leak, not a parent.  
**Vs ASC:** the function **stands / aims** at culmination; it is not how-met at the door.  
**Orientation:** attachment at the meridian. Not a public-role *sphere*.

---

## 3. Collision test (locked)

Packs must fail this test if any House 1 / House 10 arena token appears in an `orientation:` line.

| Forbidden in ASC pack | Source |
|-----------------------|--------|
| self-presentation · appearance · first-impression | House 1 `arena` |
| mask | 1.3.100 secondary |
| career · public-role · reputation · calling | House 10 `arena` (wrong edge as well) |

| Forbidden in MC pack | Source |
|----------------------|--------|
| career · public-role · reputation · calling | House 10 `arena` |
| profession | 1.3.100 secondary / Astrodienst leak |
| self-presentation · appearance · first-impression | House 1 `arena` (wrong edge as well) |

Geometric guard (restated): a planet can occupy House 1 without conjuncting ASC. Occupancy of the 10th is not conjunction with MC. If a pack lemma erases that split, fill is broken.

---

## 4. Cross-planet dry-run (locked as a check, not as pair essays)

Locked packs, not grammar illustrations. 1.3.101 dry-run wording is **not** the source of these rows.

### Mars AT ASC

```text
planet:       act · pursue · assert
orientation:  doorway-meeting · how-met · automatic-response
frame:        acting/asserting hung on doorway-meeting / how-met / automatic-response
out:          house.1.arena · appearance · first-impression · mask · personal-facing as the stem
```

### Mars AT MC

Same planet function. Different pack.

```text
planet:       act · pursue · assert
orientation:  culmination · outer-mark · aiming
frame:        acting/asserting hung on culmination / outer-mark / aiming
out:          house.10.arena · career · reputation · calling · public-facing as the stem
```

Difference is **only** `orientation`.

### Venus AT ASC

Same ASC pack. Different planet function.

```text
planet:       attract · value · relate
orientation:  doorway-meeting · how-met · automatic-response
frame:        valuing/relating hung on doorway-meeting / how-met / automatic-response
out:          a Venus-keyed ASC lemma
```

Venus does not get a private ASC pack. Mars does not get a private MC pack.

### Negative control — Mars IN House 1

```text
planet:  act · pursue · assert
arena:   self-presentation · appearance · first-impression
frame:   acting/asserting routed into self-presentation / appearance / first-impression
```

Occupancy of the 1st is not conjunction with ASC. Frames must not match.

### Negative control — Mars IN House 10

```text
planet:  act · pursue · assert
arena:   career · public-role · reputation · calling
frame:   acting/asserting routed into career / public-role / reputation / calling
```

Occupancy of the 10th is not conjunction with MC. Frames must not match.

### 4.1 Gate check

| Test | Result |
|------|--------|
| Origin | all orientation atoms `direct` from that angle’s include |
| No 1.3.101 dry-run as source | parents are 1.3.100 include families |
| Orientation-fit | Mars AT ASC and Venus AT ASC share one ASC pack |
| Collision vs House 1 | ASC `orientation:` has no self-presentation / appearance / first-impression / mask |
| Collision vs House 10 | MC `orientation:` has no career / public-role / reputation / calling |
| Discrimination ASC ↔ MC | doorway-meeting / how-met / automatic-response vs culmination / outer-mark / aiming |
| Geometric guard | Mars in 1st ≠ Mars AT ASC; Mars in 10th ≠ Mars AT MC |
| Secondary unused | appearance · first-impression · mask · career · reputation · calling stay in territory |
| Include leftover | personal-facing · public-facing unused (not a second atom) |
| Orientation not interpretation | no planet-on-angle essay · no vocation-as-fate |
| Compression | leftover families remain in 1.3.100 territory |

If ASC and MC packs had used House 1 / House 10 vocabulary to become distinct, fill would fail. They do not.

---

## 5. This pass does not do

- JSON / schema / `object.canon` on angles / `astro.object.asc` / `astro.object.mc` / `active`
- Pretty lemmas after lock
- Promote secondary collision-zone
- Copy House 1 / House 10 packs
- Storage / materialization — **done 1.3.103**
- Stored Planet×Angle smoke — **done 1.3.104** · final atomic smoke — **done 1.3.105**
- DSC / IC objects
- Rising-sign portraits · MC-in-sign careers
- Sign / House / Aspect pack edits · books · CORE · Co–Star ingest
- Fill leftover include (`personal-facing` / `public-facing`) for symmetry
- A second angle slot

**Sequence (locked, not skipped):** fill (this file) → storage/materialization — **done 1.3.103** → stored Planet×Angle smoke — **done 1.3.104** → **STOP Angles** → final atomic smoke (Planet + Sign + House + Aspect + Angle, all stored) — **done 1.3.105** → Knowledge Core V1 FREEZE → IL-2.

**Next named:** stored Planet×Angle composition smoke — **done 1.3.104.** **STOP Angles.** Final atomic smoke — **done 1.3.105.** Next = Knowledge Core V1 FREEZE. Not lemma rewrite. **STOP Aspects.** **STOP Houses.** **STOP Signs.** Do not improve these packs without a named Composition Engine failure.

---

## Changelog

- **1.2 (2026-08-23)** — 1.3.104 stored Planet×Angle smoke PASS. Packs unchanged. STOP Angles. Final atomic smoke — **done 1.3.105.** Next = Knowledge Core V1 FREEZE.
- **1.1 (2026-08-22)** — 1.3.103 storage/materialization. Two drafts carry `canon.orientation`. Packs unchanged. Stored Planet×Angle smoke — **done 1.3.104.**
- **1.0 (2026-08-22)** — 1.3.102. Two packs. Origin `direct` from 1.3.100 include. Five gates. Collision vs House 1/10. Secondary unused. personal-facing / public-facing leftover. Dry-run 1.3.101 not inherited. Storage/materialization — **done 1.3.103.**
