# Atomic Canon Composition Smoke V1

**Date:** 2026-08-23  
**Status:** LOCKED (diagnostic). **Not** IL-2. **Not** LLM. **Not** pair essays. **Not** lemma rewrite. **Not** CORE. **Not** a grammar patch. **Not** `active`. **Not** Knowledge Core V1 FREEZE.  
**Canon:** [INTERPRETATION_LIBRARY_V1.md](./INTERPRETATION_LIBRARY_V1.md) §6.59. Prior stored smokes: [PLANET_CANON_COMPOSITION_SMOKE_V1.md](./PLANET_CANON_COMPOSITION_SMOKE_V1.md) · [SIGN_CANON_COMPOSITION_SMOKE_V1.md](./SIGN_CANON_COMPOSITION_SMOKE_V1.md) · [HOUSE_CANON_COMPOSITION_SMOKE_V1.md](./HOUSE_CANON_COMPOSITION_SMOKE_V1.md) · [ASPECT_CANON_COMPOSITION_SMOKE_V1.md](./ASPECT_CANON_COMPOSITION_SMOKE_V1.md) · [ANGLE_CANON_COMPOSITION_SMOKE_V1.md](./ANGLE_CANON_COMPOSITION_SMOKE_V1.md). Compose gate: [ASTROLOGY_COMPOSITION_MODEL.md](../ASTROLOGY_COMPOSITION_MODEL.md).

This pass answers: **are Planet, Sign, House, Aspect, and Angle all stored, and do their operators stay five different jobs?** Catalog unchanged. Do not reopen any family to “improve” packs. Do not freeze Knowledge Core here.

```text
planet.canon.core_function     what
sign.canon.manner              how
house.canon.arena              where
aspect.canon.relation          relation
angle.canon.orientation        orientation locus
```

No user-facing sentence. No Layer 5 pair object. Planet + Sign + House + Aspect + Angle, all stored.

---

## Architecture impact

- **SoT before:** five family smokes PASS in isolation (1.3.82 snapshot · 1.3.88 · 1.3.93 · 1.3.98 · 1.3.104). Next risk: treat the five operators as one essay; collapse House 1 into ASC; read `interaction` as `relation`; treat `mode`/`element` as `manner`; skip freeze and open IL-2 cookbooks.
- **SoT after:** one diagnostic reads all five stored operators from the catalog. Four gates PASS. Prior family smokes stand as snapshots of their own operators. Catalog unchanged. **STOP Angles.** **STOP Aspects.** **STOP Houses.** **STOP Signs.** Next named = Knowledge Core V1 FREEZE.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — this file · IL §6.59
- **Backward compatible?** yes (`draft`). Deprecated as next step: pack enrichment; occupancy = conjunction; House 1 = ASC; `interaction` as topology; Layer 5 essays; IL-2 before freeze.

---

## 0. Four gates (locked)

| Gate | Check |
|------|--------|
| **Stored source** | Each operator is on the object `canon` nest. Not markdown. Not Lilly `domain`. Not `interaction`. Not `mode`/`element`. |
| **Five families present** | 7 planets with `core_function` · 12 signs with `manner` · 12 houses with `arena` · 5 aspects with `relation` · 2 angles with `orientation`. Catalog 38 draft / 0 `active`. |
| **Operator discrimination** | Mars IN Aries ≠ Mars IN 1st ≠ Mars AT ASC ≠ Mars □ Saturn. Occupancy ≠ conjunction. House 1 ≠ ASC. |
| **No cookbook** | Frames carry lemmas only. No pair essay. No appearance-as-rising. No career-as-MC. No earth→practical. |

### 0.1 Verdict rules

Same three values as 1.3.82 / 1.3.88 / 1.3.93 / 1.3.98 / 1.3.104.

| Verdict | Means |
|---------|--------|
| **PASS** | The frame is produced from allowed atoms. Payload is on the objects. |
| **PARTIAL** | The construction type is identified, but a named atom type is missing. |
| **FAIL** | Apparent meaning appears only from hidden astrology or a stored pair essay. |

PARTIAL is not used here. Historical 1.3.82 sign/house PARTIAL rows stay snapshots.

### 0.2 Allowed inputs

| Kind | Allowed | Forbidden |
|------|---------|-----------|
| Planet | `object.canon.core_function` | `function` · `themes` · provenance sentences as the operator |
| Sign | `object.canon.manner` | `mode` / `element` / `orientation` as manner; “Capricorn = ambition” |
| House | `object.canon.arena` | Lilly `domain` as arena; `1st = ASC`; `10th = MC` |
| Aspect | `object.canon.relation` | `interaction` as operator; pair slogans |
| Angle | `object.canon.orientation` | House 1/10 `arena`; occupancy of 1st/10th as the edge |

---

## 1. Stored source — five families — **PASS**

| Family | Stored slot | Count | Smoke that locked it |
|--------|-------------|-------|----------------------|
| Planet | `canon.core_function` | 7 (Sun–Saturn) | 1.3.82 |
| Sign | `canon.manner` | 12 | 1.3.88 |
| House | `canon.arena` | 12 | 1.3.93 |
| Aspect | `canon.relation` | 5 | 1.3.98 |
| Angle | `canon.orientation` | 2 | 1.3.104 |

Uranus / Neptune / Pluto remain claims without objects. That is not a missing operator on a stored atom. DSC / IC are out of V1.

**Missing atom:** none for the five stored families.

**Forbidden recovery:** invent outer-planet `function` or DSC packs to “complete 41.” Gold-set count is not this gate.

**Verdict:** PASS

---

## 2. Prior smokes stand — **PASS**

Live re-read of the same stored objects. Do not edit 1.3.82 / 1.3.88 / 1.3.93 / 1.3.98 / 1.3.104 verdicts.

| Row | Operator | Verdict |
|-----|----------|---------|
| Venus × Capricorn — **PASS** | `manner`: reserved · disciplined · structured | 1.3.88 live |
| Moon × 4th house — **PASS** | `arena`: home · family · roots · private-base | 1.3.93 live |
| Mars □ Saturn — **PASS** | `relation`: friction · blockage · cross-purposes | 1.3.98 live |
| Mars AT ASC — **PASS** | `orientation`: doorway-meeting · how-met · automatic-response | 1.3.104 live |

1.3.82 Venus × Capricorn PARTIAL and house PARTIAL remain snapshots of a catalog without `manner` / `arena`.

**Verdict:** PASS

---

## 3. Operator discrimination — **PASS**

Same planet. Four constructions. Five jobs if Saturn is the other function on the square.

### Mars IN Aries — **PASS**

```text
type:     planet_in_sign
planet:   mars     core_function={act, pursue, assert}
sign:     aries    manner={initiating, direct, headlong}
```

`manner` is how. It is not House 1 appearance. It is not ASC doorway.

### Mars IN 1st ≠ Mars AT ASC

| Construction | Stored modifier | Type |
|--------------|-----------------|------|
| Mars IN 1st | `arena`: self-presentation · appearance · first-impression | `planet_in_house` |
| Mars AT ASC | `orientation`: doorway-meeting · how-met · automatic-response | `planet_at_angle` |

Occupancy ≠ conjunction. A planet can occupy House 1 without conjuncting ASC.

### Mars IN Aries ≠ Mars IN 1st

Manner is not arena. Aries `initiating` is absent from House 1 `arena`. House 1 `appearance` is absent from Aries `manner`.

### Mars □ Saturn ≠ Mars AT ASC

Relation is not orientation. Square `friction` is absent from ASC `orientation`.

**Missing atom:** none

**Verdict:** PASS

---

## 4. No cookbook — **PASS**

Inspected payload = the five `canon` slots named in §0. No generated sentence. No pair-specific prose field.

**Forbidden recovery:** “Mars in Aries means you look aggressive.” “Planet in 1st = planet on ASC.” “MC = career.” “Trine = Sextile because both `interaction=flow`.” “Capricorn = earth = practical.”

**Verdict:** PASS

---

## 4.1 Locked rows

| Row | Verdict |
|-----|---------|
| five stored families | Planet + Sign + House + Aspect + Angle, all stored |
| Venus × Capricorn — **PASS** | stored `manner` |
| Moon × 4th house — **PASS** | stored `arena` |
| Mars □ Saturn — **PASS** | stored `relation` |
| Mars AT ASC — **PASS** | stored `orientation` |
| Mars IN Aries — **PASS** | stored `manner` |
| Mars IN Aries ≠ Mars IN 1st | operator discrimination |
| Mars IN 1st ≠ Mars AT ASC | Occupancy ≠ conjunction |

**Forbidden recovery:** “Mars in Aries means you look aggressive.” “MC = career.” “Planet in 1st = planet on ASC.” Those recoveries are not on the objects.

---

## 5. Snapshot — family smokes stay family smokes

Do not edit 1.3.82 / 1.3.88 / 1.3.93 / 1.3.98 / 1.3.104 files to absorb this pass. This file is the joint diagnostic. Their PASS rows stay the authority for that operator.

---

## 6. This pass does not do

- Knowledge Core V1 FREEZE — **done 1.3.106**
- IL-2 engine · runtime wiring · LLM copy
- New lemmas · pack revision · `function` rewrite · `active`
- Outer planet objects · DSC / IC
- Layer 5 pair catalog
- Sign / House / Aspect / Planet / Angle pack edits

**Next named:** IL-2 (composition rules, not pair catalog) — **done 1.3.107.** Next = IL-3 engine. **STOP Angles.** **STOP Aspects.** **STOP Houses.** **STOP Signs.** Do not enrich packs without a named Composition Engine failure.

---

## Changelog

- **1.2 (2026-08-23)** — IL-2 composition rules 1.3.107. This diagnostic stands. Next = IL-3.
- **1.1 (2026-08-23)** — 1.3.106 Knowledge Core V1 FREEZE. This diagnostic stands. Next = IL-2. **Done 1.3.107.**
- **1.0 (2026-08-23)** — 1.3.105. Final atomic smoke PASS. Five stored families. Operators discriminate. Occupancy ≠ conjunction. Catalog unchanged. Next = Knowledge Core V1 FREEZE. **Done 1.3.106.**
